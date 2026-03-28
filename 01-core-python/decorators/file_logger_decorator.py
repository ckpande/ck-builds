# file_logger_decorator.py
# Decorator that logs function name, arguments, execution time, and errors to a rotating log file.
# Chandrakant Pande - ck-builds

import functools
import json
import logging
import os
import time
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, "execution.log"),
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
)

_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

log = logging.getLogger("execution")
log.setLevel(logging.INFO)
if not log.handlers:
    log.addHandler(_handler)
    log.addHandler(logging.StreamHandler())


def log_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            took_ms = (time.perf_counter() - start) * 1000
            log.info("OK | %s | %.2fms", func.__name__, took_ms)
            return result
        except Exception as e:
            took_ms = (time.perf_counter() - start) * 1000
            log.error(
                "FAIL | %s | %.2fms | %s: %s",
                func.__name__, took_ms, type(e).__name__, e,
            )
            raise  # re-raise - decorator observes, never suppresses

    return wrapper


@log_execution
def write_json(filepath: str, data: list | dict) -> bool:
    # "w" mode - intentional, each run produces a clean snapshot
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Written: {filepath}")
    return True


@log_execution
def read_json(filepath: str) -> list | dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@log_execution
def write_csv(filepath: str, headers: list, rows: list) -> bool:
    # newline="" - prevents double blank lines on Windows
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        f.write(",".join(headers) + "\n")
        for r in rows:
            f.write(",".join(str(v) for v in r) + "\n")
    print(f"Written: {filepath}")
    return True


@log_execution
def read_csv(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        ln = f.read().splitlines()
    if not ln:
        return []
    headers = ln[0].split(",")
    return [dict(zip(headers, line.split(","))) for line in ln[1:]]


@log_execution
def process_loan_summary(records: list[dict]) -> dict:
    count = 0
    total = 0.0
    active_cnt = 0
    npa_cnt = 0
    for r in records:
        count += 1
        total += float(r["balance"])
        status = r["status"].strip()
        if status == "ACTIVE":
            active_cnt += 1
        elif status == "NPA":
            npa_cnt += 1
    return {
        "total_records": count,
        "active_count": active_cnt,
        "npa_count": npa_cnt,
        "total_balance": round(total, 2),
    }


if __name__ == "__main__":
    loan_data = [
        {"account_id": 1001, "customer": "Arjun Mehta", "balance": 1380000.00, "status": "ACTIVE"},
        {"account_id": 1002, "customer": "Pooja Desai", "balance": 210000.00, "status": "ACTIVE"},
        {"account_id": 1005, "customer": "Suresh Patil", "balance": 2490000.00, "status": "NPA"},
        {"account_id": 1008, "customer": "Shreya Wagh", "balance": 1750000.00, "status": "NPA"},
        {"account_id": 1009, "customer": "Tushar Pawar", "balance": 225000.00, "status": "ACTIVE"},
    ]

    # JSON
    json_path = os.path.join(DATA_DIR, "loan_snapshot.json")
    write_json(json_path, loan_data)
    recovered = read_json(json_path)
    print(f"JSON: {len(recovered)} records loaded")

    # CSV
    csv_path = os.path.join(DATA_DIR, "loan_snapshot.csv")
    csv_headers = ["account_id", "customer", "balance", "status"]
    csv_rows = [[r["account_id"], r["customer"], r["balance"], r["status"]] for r in loan_data]
    write_csv(csv_path, csv_headers, csv_rows)
    csv_records = read_csv(csv_path)
    print(f"CSV: {len(csv_records)} records loaded")

    # summary
    summary = process_loan_summary(csv_records)
    print("\nLoan Portfolio Summary:-")
    for k, v in summary.items():
        print(f"{k:<20}: {v}")

    # missing file — decorator should log FAIL
    print("\n[ testing error logging ]")
    try:
        read_json(os.path.join(DATA_DIR, "does_not_exist.json"))
    except FileNotFoundError:
        print("FileNotFoundError caught — check execution.log")

    log.info("file_logger_decorator — run complete")