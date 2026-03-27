# Transaction Processor - Generator Pipeline for Fintech CSV
# Chandrakant Pande - ck-builds

import os
from logging.handlers import RotatingFileHandler
import logging
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, "transaction_processor.log"),
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
)
_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

log = logging.getLogger("txn_processor")
log.setLevel(logging.INFO)
log.addHandler(_handler)
log.addHandler(logging.StreamHandler())


def create_sample_csv(filepath):
    header = "txn_id,account_id,txn_type,amount,status"
    rows = [
        "T001,ACC001,CREDIT,150000.00,SUCCESS",
        "T002,ACC002,DEBIT,45000.00,SUCCESS",
        "T003,ACC001,CREDIT,82000.00,SUCCESS",
        "T004,ACC003,DEBIT,12500.00,FAILED",
        "T005,ACC002,CREDIT,23000.00,SUCCESS",
        "T006,ACC004,DEBIT,8500.00,SUCCESS",
        "T007,ACC003,CREDIT,67000.00,PENDING",
        "T008,ACC001,DEBIT,31000.00,SUCCESS",
        "T009,ACC005,CREDIT,12000.00,SUCCESS",
        "T010,ACC002,DEBIT,19000.00,FAILED",
        "T011,ACC004,CREDIT,95000.00,SUCCESS",
        "T012,ACC005,DEBIT,27500.00,SUCCESS",
        "T013,ACC003,CREDIT,41000.00,SUCCESS",
        "T014,ACC001,DEBIT,13500.00,PENDING",
        "T015,ACC005,CREDIT,55000.00,SUCCESS",
    ]
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        f.write(header + "\n")
        for row in rows:
            f.write(row + "\n")
    log.info("Sample CSV created: %s | %d rows", filepath, len(rows))


def read_transactions(filepath):
    if not os.path.exists(filepath):
        log.error("Input file not found: %s", filepath)
        return

    with open(filepath, "r", encoding="utf-8") as f:
        next(f)
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.split(",")
            try:
                yield {
                    "txn_id": parts[0],
                    "account_id": parts[1],
                    "txn_type": parts[2],
                    "amount": float(parts[3]),
                    "status": parts[4]
                }
            except (ValueError, IndexError) as e:
                log.warning("Skipped invalid row: %s (%s)", ln, e)


def filter_transactions(src, txn_type, status):
    for txn in src:
        if txn["txn_type"] == txn_type and txn["status"] == status:
            yield txn


def calculate_summary(src):
    count = 0
    total = 0.0
    maxamt = float("-inf")
    minamt = float("inf")
    for txn in src:
        count += 1
        total += txn["amount"]
        if txn["amount"] > maxamt:
            maxamt = txn["amount"]
        if txn["amount"] < minamt:
            minamt = txn["amount"]
    return {
        "total_records": count,
        "total_amount": round(total, 2),
        "max_amount": round(maxamt, 2) if count > 0 else 0.0,
        "min_amount": round(minamt, 2) if count > 0 else 0.0,
    }


def write_summary(summary, filepath):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
        log.info("Summary written to: %s", filepath)
        return True
    except OSError as e:
        log.error("Failed to write summary: %s | %s", filepath, e)
        return False


def _print_summary(label, summary):
    print(f"\n[ {label} ]")
    for k, v in summary.items():
        print(f"  {k:<16}: {v}")


if __name__ == "__main__":
    src_csv = os.path.join(DATA_DIR, "transactions.csv")
    credits_js = os.path.join(DATA_DIR, "credit_summary.json")
    debits_js = os.path.join(DATA_DIR, "debit_summary.json")

    # Mock data generation
    create_sample_csv(src_csv)

    # Pipeline 1: CREDIT + SUCCESS  (nothing runs until iteration)
    raw_reader = read_transactions(src_csv)
    filtered = filter_transactions(raw_reader, "CREDIT", "SUCCESS")
    credits = calculate_summary(filtered)
    if credits["total_records"] == 0:
        log.warning("Pipeline 1 (CREDIT+SUCCESS): zero records matched.")

    _print_summary("CREDIT + SUCCESS Summary", credits)
    write_summary(credits, credits_js)

    # Pipeline 2: DEBIT + SUCCESS
    # New reader is required — the previous generator is exhausted after Pipeline 1
    raw_reader = read_transactions(src_csv)
    filtered = filter_transactions(raw_reader, "DEBIT", "SUCCESS")
    debits = calculate_summary(filtered)
    if debits["total_records"] == 0:
        log.warning("Pipeline 2 (DEBIT+SUCCESS): zero records matched.")

    _print_summary("DEBIT + SUCCESS Summary", debits)
    write_summary(debits, debits_js)

    log.info("Transaction processor completed successfully.")
