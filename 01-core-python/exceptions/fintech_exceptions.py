# fintech_exceptions.py | Chandrakant Pande | ck-builds
#
# Custom exception hierarchy and Oracle DB access layer for handling
# fintech transactions (validations, state errors, and routing).

import contextlib
import logging
import os
from logging.handlers import RotatingFileHandler

import oracledb
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOGS_DIR, exist_ok=True)

_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, "fintech_exceptions.log"),
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
)
_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

log = logging.getLogger("fintech_exceptions")
log.setLevel(logging.INFO)
if not log.handlers:
    log.addHandler(_handler)
    log.addHandler(logging.StreamHandler())

SUPPORTED_TXN_TYPES: frozenset[str] = frozenset({"DEBIT", "LOAN"})


# Exception hierarchy
class FintechError(Exception):
    pass


class ValidationError(FintechError):
    # raised for bad input — caller's fault, not the system's
    pass


class MissingFieldError(ValidationError):
    def __init__(self, field_name: str):
        self.field_name = field_name
        super().__init__(f"Required field missing or empty: {field_name}")


class AccountNotFoundError(ValidationError):
    def __init__(self, account_id: str):
        self.account_id = account_id
        super().__init__(f"Account '{account_id}' not found.")


class InvalidAmountError(ValidationError):
    def __init__(self, amount: object):
        self.amount = amount
        super().__init__(f"Invalid amount: {amount!r}. Amount must be a positive number.")


class UnknownTxnTypeError(ValidationError):
    def __init__(self, txn_type: str):
        self.txn_type = txn_type
        super().__init__(
            f"Unknown transaction type: {txn_type!r}. "
            f"Supported: {sorted(SUPPORTED_TXN_TYPES)}."
        )


class TransactionError(FintechError):
    # raised for failures during processing — system state issue
    pass


class InsufficientFundsError(TransactionError):
    def __init__(self, account_id: str, balance: float, requested: float):
        self.account_id = account_id
        self.balance = balance
        self.requested = requested
        super().__init__(
            f"Account '{account_id}': insufficient funds. "
            f"Balance: {balance:,.2f}, Requested: {requested:,.2f}."
        )


class LoanLimitExceededError(TransactionError):
    def __init__(self, account_id: str, requested_amt: float, loan_limit: float):
        self.account_id = account_id
        self.requested_amt = requested_amt
        self.loan_limit = loan_limit
        super().__init__(
            f"Account '{account_id}': loan limit exceeded. "
            f"Requested: {requested_amt:,.2f}, Limit: {loan_limit:,.2f}."
        )


@contextlib.contextmanager
def _get_connection():
    # validates .env keys before attempting a network call — fail fast with clear message
    needed = ["DB_USER", "DB_PASS", "DB_DSN"]
    missing = [k for k in needed if not os.getenv(k)]
    if missing:
        raise ValueError(f"Missing required .env keys: {', '.join(missing)}")

    conn = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN"),
    )
    log.info("Oracle connection opened.")
    try:
        yield conn
    finally:
        conn.close()
        log.info("Oracle connection closed.")


def get_account(account_id: str) -> dict[str, object]:
    sql = (
        "SELECT account_id, customer_name, balance, loan_limit "
        "FROM loan_accounts WHERE account_id = :account_id"
    )
    try:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"account_id": account_id})
                columns = [col[0].lower() for col in cur.description]
                row = cur.fetchone()
                if row is None:
                    raise AccountNotFoundError(account_id)
                return dict(zip(columns, row))
    except oracledb.Error as e:
        log.error("Oracle error in get_account | account=%s | %s", account_id, e)
        raise


def update_balance(account_id: str, new_balance: float) -> None:
    sql = (
        "UPDATE loan_accounts SET balance = :balance "
        "WHERE account_id = :account_id"
    )
    try:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"balance": new_balance, "account_id": account_id})
                conn.commit()
                log.info(
                    "Balance updated | account=%s | new_balance=%.2f | rows=%d",
                    account_id, new_balance, cur.rowcount,
                )
    except oracledb.Error as e:
        log.error("Oracle error in update_balance | account=%s | %s", account_id, e)
        raise


def validate_transaction(txn: dict) -> bool:
    act_id = txn.get("account_id")
    amt = txn.get("amount")
    txn_type = txn.get("txn_type")

    if not act_id:
        raise MissingFieldError("account_id")

    try:
        amt = float(amt)
    except (TypeError, ValueError) as e:
        raise InvalidAmountError(amt) from e

    if amt <= 0:
        raise InvalidAmountError(amt)

    if txn_type not in SUPPORTED_TXN_TYPES:
        raise UnknownTxnTypeError(txn_type)

    return True


def process_debit(act_id: str, amt: float) -> dict:
    act = get_account(act_id)
    bal = float(act["balance"])

    if bal < amt:
        raise InsufficientFundsError(act_id, bal, amt)

    new_bal = round(bal - amt, 2)
    update_balance(act_id, new_bal)

    log.info("Debit OK | account=%s | amount=%.2f | new_balance=%.2f", act_id, amt, new_bal)
    return {"new_balance": new_bal}


def process_loan(act_id: str, requested_amt: float) -> dict:
    act = get_account(act_id)
    loan_lmt = float(act["loan_limit"])

    if requested_amt > loan_lmt:
        raise LoanLimitExceededError(act_id, requested_amt, loan_lmt)

    log.info("Loan approved | account=%s | amount=%.2f", act_id, requested_amt)
    return {"loan_approved": requested_amt}


def run_pipeline(tran: list[dict]) -> list[dict]:
    results = []

    for txn in tran:
        txn_id = txn.get("txn_id", "unknown")
        try:
            validate_transaction(txn)
            if txn["txn_type"] == "DEBIT":
                detail = process_debit(txn["account_id"], float(txn["amount"]))
            elif txn["txn_type"] == "LOAN":
                detail = process_loan(txn["account_id"], float(txn["amount"]))
            results.append({"txn_id": txn_id, "status": "SUCCESS", "detail": detail})

        # ValidationError subtypes
        except MissingFieldError as e:
            log.warning("Missing field | txn=%s | field=%s", txn_id, e.field_name)
            results.append({"txn_id": txn_id, "status": "VALIDATION_ERROR", "detail": str(e)})

        except UnknownTxnTypeError as e:
            log.warning("Unknown txn_type | txn=%s | type=%s", txn_id, e.txn_type)
            results.append({"txn_id": txn_id, "status": "VALIDATION_ERROR", "detail": str(e)})

        except InvalidAmountError as e:
            log.warning("Invalid amount | txn=%s | amount=%s", txn_id, e.amount)
            results.append({"txn_id": txn_id, "status": "VALIDATION_ERROR", "detail": str(e)})

        except AccountNotFoundError as e:
            log.warning("Account not found | txn=%s | account=%s", txn_id, e.account_id)
            results.append({"txn_id": txn_id, "status": "VALIDATION_ERROR", "detail": str(e)})

        # TransactionError subtypes
        except InsufficientFundsError as e:
            log.warning(
                "Insufficient funds | txn=%s | account=%s | balance=%.2f | requested=%.2f",
                txn_id, e.account_id, e.balance, e.requested,
            )
            results.append({"txn_id": txn_id, "status": "FAILED", "detail": str(e)})

        except LoanLimitExceededError as e:
            log.warning(
                "Loan limit exceeded | txn=%s | account=%s | requested=%.2f | limit=%.2f",
                txn_id, e.account_id, e.requested_amt, e.loan_limit,
            )
            results.append({"txn_id": txn_id, "status": "REJECTED", "detail": str(e)})

        except FintechError as e:
            log.error("Unexpected fintech error | txn=%s | %s: %s", txn_id, type(e).__name__, e)
            results.append({"txn_id": txn_id, "status": "ERROR", "detail": str(e)})

        finally:
            log.info("Processed txn: %s", txn_id)

    return results


if __name__ == "__main__":
    trans = [
        {"txn_id": "T001", "account_id": "ACC001", "amount": 50000.00, "txn_type": "DEBIT"},  # SUCCESS
        {"txn_id": "T002", "account_id": "ACC003", "amount": 100000.00, "txn_type": "DEBIT"},  # InsufficientFunds
        {"txn_id": "T003", "account_id": "ACC999", "amount": 25000.00, "txn_type": "DEBIT"},  # AccountNotFound
        {"txn_id": "T004", "account_id": "ACC002", "amount": -500.00, "txn_type": "DEBIT"},  # InvalidAmount
        {"txn_id": "T005", "account_id": "ACC001", "amount": 5000000.00, "txn_type": "LOAN"},  # LoanLimitExceeded
        {"txn_id": "T006", "account_id": "ACC002", "amount": 300000.00, "txn_type": "LOAN"},  # SUCCESS
        {"txn_id": "T007", "account_id": "ACC001", "amount": 0, "txn_type": "DEBIT"},  # InvalidAmount
        {"txn_id": "T008", "account_id": "", "amount": 10000.00, "txn_type": "DEBIT"},  # MissingField
        {"txn_id": "T009", "account_id": "ACC001", "amount": 10000.00, "txn_type": "TRANSFER"},  # UnknownTxnType
    ]

    results = run_pipeline(trans)

    print("\n[ Transaction Results ]")
    print(f"  {'TXN':<6}  {'STATUS':<18}  DETAIL")
    print(f"  {'-' * 6}  {'-' * 18}  {'-' * 50}")
    for r in results:
        detail = r["detail"]
        if isinstance(detail, dict):
            detail_str = ", ".join(
                f"{k}: {v:,.2f}" if isinstance(v, float) else f"{k}: {v}"
                for k, v in detail.items()
            )
        else:
            detail_str = detail
        print(f"  {r['txn_id']:<6}  {r['status']:<18}  {detail_str}")

    log.info("Pipeline complete — %d transactions processed.", len(results))
