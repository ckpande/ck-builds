# transaction_iterator.py | Chandrakant Pande | ck-builds
#
# Iterator protocol: __iter__, __next__, StopIteration, peek(), generator comparison

import logging
import os
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, "transaction_iterator.log"),
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
)
_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

log = logging.getLogger("transaction_iterator")
log.setLevel(logging.INFO)
if not log.handlers:
    log.addHandler(_handler)
    log.addHandler(logging.StreamHandler())


class TransactionBatch:
    def __init__(self, trans: list) -> None:
        if not isinstance(trans, list) or not trans:
            raise ValueError("transactions must be a non-empty list")
        self._trans = trans

    def __iter__(self):
        return TransactionIterator(self._trans)

    def __len__(self) -> int:
        return len(self._trans)

    def __str__(self) -> str:
        return f"TransactionBatch({len(self._trans)} transactions)"

    def __repr__(self) -> str:
        return f"TransactionBatch(count={len(self._trans)})"


class TransactionIterator:
    def __init__(
            self,
            trans: list,
            txn_type: str | None = None,
            status: str | None = None,
    ) -> None:
        self._trans = trans
        self._index = 0
        self._txn_type = txn_type
        self._status = status

    def __iter__(self):
        return self

    def __next__(self) -> dict:
        while self._index < len(self._trans):
            txn = self._trans[self._index]
            self._index += 1

            if self._txn_type and txn.get("txn_type") != self._txn_type:
                continue
            if self._status and txn.get("status") != self._status:
                continue
            return txn

        raise StopIteration

    def peek(self) -> dict | None:
        scan_index = self._index
        while scan_index < len(self._trans):
            txn = self._trans[scan_index]
            scan_index += 1
            if self._txn_type and txn.get("txn_type") != self._txn_type:
                continue
            if self._status and txn.get("status") != self._status:
                continue
            return txn
        return None

    def __repr__(self) -> str:
        return (
            f"TransactionIterator("
            f"index={self._index}/{len(self._trans)}, "
            f"txn_type={self._txn_type!r}, "
            f"status={self._status!r})"
        )


# Generator version — same output, less code
def filtered_trans(trans, txn_type: str | None = None, status: str | None = None):
    for txn in trans:
        if txn_type and txn.get("txn_type") != txn_type:
            continue
        if status and txn.get("status") != status:
            continue
        yield txn


def running_total(iterator):
    total = 0.0
    for txn in iterator:
        total += float(txn["amount"])
        yield round(total, 2)


def batch_summary(batch: TransactionBatch) -> dict:
    total_amt = sum(float(t["amount"]) for t in batch)
    cr_total = sum(float(t["amount"]) for t in filtered_trans(batch._trans, txn_type="CREDIT", status="SUCCESS"))
    db_total = sum(float(t["amount"]) for t in filtered_trans(batch._trans, txn_type="DEBIT", status="SUCCESS"))
    success_cnt = sum(1 for t in batch if t.get("status") == "SUCCESS")
    failed_cnt = sum(1 for t in batch if t.get("status") == "FAILED")

    return {
        "total_txn": len(batch),
        "total_amount": round(total_amt, 2),
        "credit_total": round(cr_total, 2),
        "debit_total": round(db_total, 2),
        "success_count": success_cnt,
        "failed_count": failed_cnt,
    }


if __name__ == "__main__":

    transactions = [
        {"txn_id": "T001", "account_id": "ACC001", "txn_type": "CREDIT", "amount": 150000.00, "status": "SUCCESS"},
        {"txn_id": "T002", "account_id": "ACC002", "txn_type": "DEBIT", "amount": 45000.00, "status": "SUCCESS"},
        {"txn_id": "T003", "account_id": "ACC001", "txn_type": "CREDIT", "amount": 82000.00, "status": "SUCCESS"},
        {"txn_id": "T004", "account_id": "ACC003", "txn_type": "DEBIT", "amount": 12500.00, "status": "FAILED"},
        {"txn_id": "T005", "account_id": "ACC002", "txn_type": "CREDIT", "amount": 23000.00, "status": "SUCCESS"},
        {"txn_id": "T006", "account_id": "ACC004", "txn_type": "DEBIT", "amount": 8500.00, "status": "SUCCESS"},
        {"txn_id": "T007", "account_id": "ACC003", "txn_type": "CREDIT", "amount": 67000.00, "status": "PENDING"},
        {"txn_id": "T008", "account_id": "ACC001", "txn_type": "DEBIT", "amount": 31000.00, "status": "SUCCESS"},
    ]

    batch = TransactionBatch(transactions)
    print(f"batch: {repr(batch)} | len: {len(batch)}")

    # for loop — what PVM does internally
    print("\n--- for loop — what PVM does internally ---")
    _iter = iter(batch)
    print(f"iter(batch)  -> {repr(_iter)}")
    first = next(_iter)
    print(f"next(_iter)  -> {first['txn_id']} | {first['txn_type']} | {first['amount']:,.2f}")
    second = next(_iter)
    print(f"next(_iter)  -> {second['txn_id']} | {second['txn_type']} | {second['amount']:,.2f}")

    # TransactionBatch is iterable — multiple passes
    print("\n--- batch: pass 1 ---")
    for txn in batch:
        print(f"  {txn['txn_id']} | {txn['txn_type']:<6} | {txn['amount']:>12,.2f} | {txn['status']}")

    print("\n--- batch: pass 2 (same result) ---")
    print(f"  rows: {sum(1 for _ in batch)}")

    # TransactionIterator — single use
    print("\n--- TransactionIterator: CREDIT + SUCCESS ---")
    credit_it = TransactionIterator(transactions, txn_type="CREDIT", status="SUCCESS")
    print(f"  before: {repr(credit_it)}")
    for txn in credit_it:
        print(f"  {txn['txn_id']} | {txn['amount']:>12,.2f}")
    print(f"  after:  {repr(credit_it)}")
    print(f"  pass 2: {sum(1 for _ in credit_it)} rows")  # 0 — exhausted

    # peek() — look ahead without consuming
    print("\n--- peek() ---")
    it = TransactionIterator(transactions, txn_type="CREDIT", status="SUCCESS")
    print(f"  peek()  -> {it.peek()['txn_id']}  (cursor not moved)")
    print(f"  next()  -> {next(it)['txn_id']}  (same row, now consumed)")
    print(f"  peek()  -> {it.peek()['txn_id']}  (next row, not consumed)")

    # generator version — identical output
    print("\n--- filtered_trans (generator): CREDIT + SUCCESS ---")
    for txn in filtered_trans(transactions, txn_type="CREDIT", status="SUCCESS"):
        print(f"  {txn['txn_id']} | {txn['amount']:>12,.2f}")

    # running total
    print("\n--- running_total: CREDIT + SUCCESS ---")
    for total in running_total(TransactionIterator(transactions, txn_type="CREDIT", status="SUCCESS")):
        print(f"  {total:>12,.2f}")

    # batch summary — uses multiple passes on the same batch
    print("\n--- batch_summary ---")
    for k, v in batch_summary(batch).items():
        print(
            f"  {k:<15}: {v:>12,.2f}" if isinstance(v, float)
            else f"  {k:<15}: {v}"
        )

    log.info("transaction_iterator — run complete.")
