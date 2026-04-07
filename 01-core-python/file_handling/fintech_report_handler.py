# fintech_report_handler.py | Chandrakant Pande | ck-builds

# ETL pipeline: fetch loan data from MySQL → JSON snapshot, CSV report, audit log, pickle backup.
import csv
import json
import logging
import os
import pickle
import sys
from datetime import datetime
from decimal import Decimal
from logging.handlers import RotatingFileHandler

from mysql.connector import Error

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "mysql"))
from db_helper import get_connection

REPORTS_DIR = os.path.join(BASE_DIR, "reports")
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, 'fintech_report_handler.log'),
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
)
_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))

log = logging.getLogger("report_handler")
log.setLevel(logging.INFO)
if not log.handlers:
    log.addHandler(_handler)
    log.addHandler(logging.StreamHandler())


def fetch_trans_from_db(status: str | None = None) -> list:
    conn = None
    cur = None
    try:
        conn = get_connection("MYSQL_FINTECH_DB")
        cur = conn.cursor()

        if status:
            sql = "SELECT acc_id, cust_name, loan_type, loan_amt, bal_amt, int_rate, status, disb_date FROM loan_accounts WHERE status = %s ORDER BY acc_id"
            params = (status,)
        else:
            sql = "SELECT acc_id, cust_name, loan_type, loan_amt, bal_amt, int_rate, status, disb_date FROM loan_accounts ORDER BY acc_id"
            params = ()

        cur.execute(sql, params)
        columns = [col[0] for col in cur.description]
        rows = cur.fetchall()
        results = [dict(zip(columns, row)) for row in rows]

        label = f"status = {status}" if status else "all records"
        log.info("Fetched %s records from fintech_demo.loan_accounts (%s)", len(results), label)
        return results
    except Error as e:
        log.error("DB fetch failed: %s", e)
        return []
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()


def write_json_snapshot(trans: list, filepath: str) -> bool:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trans, f, indent=4, default=str)
        log.info("JSON snapshot written: %s | %d records", filepath, len(trans))
        return True
    except OSError as e:
        log.error("Failed to write JSON snapshot: %s | %s", filepath, e)
        return False


def read_json_snapshot(filepath: str) -> list | None:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        log.info("JSON snapshot read: %s | %d records", filepath, len(data))
        return data
    except FileNotFoundError as e:
        log.error("JSON file not found: %s", filepath)
        return None
    except json.JSONDecodeError as e:
        log.error("Malformed JSON: %s | %s", filepath, e)
        return None


def write_csv_report(trans: list, filepath: str) -> bool:
    try:
        if not trans:
            log.warning("write_csv_report called with empty list - nothing written: %s", filepath)
            return False

        fieldnames = list(trans[0].keys())
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(trans)
        log.info("CSV report written: %s | %d rows", filepath, len(trans))
        return True
    except OSError as e:
        log.error("Failed to write CSV report: %s | %s", filepath, e)
        return False


def read_csv_report(filepath: str) -> list:
    try:
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        log.info("CSV report read: %s | %d rows", filepath, len(rows))
        return rows
    except FileNotFoundError:
        log.error("CSV file not found: %s", filepath)
        return []


def append_audit_log(msg: str, filepath: str) -> None:
    try:
        with open(filepath, "a+", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} | {msg}\n")
    except OSError as e:
        log.error("Failed to write audit log: %s | %s", filepath, e)


def save_pickle_bkp(data: object, filepath: str) -> bool:
    try:
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
        log.info("Pickle bkp saved: %s", filepath)
        return True
    except OSError as e:
        log.error("Failed to save pickle: %s | %s", filepath, e)
        return False


def load_pickle_bkp(filepath: str) -> object:
    try:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        log.info("Pickle bkp loaded: %s", filepath)
        return data
    except FileNotFoundError:
        log.error("Pickle file not found: %s", filepath)
        return None
    except pickle.UnpicklingError as e:
        log.error("Corrupt pickle file: %s | %s", filepath, e)
        return None


def scan_rpt_dir(dir: str) -> list:
    results = []
    try:
        for name in sorted(os.listdir(dir)):
            fpath = os.path.join(dir, name)
            if not os.path.isfile(fpath):
                continue
            size_kb = round(os.path.getsize(fpath) / 1024, 2)
            last_modify = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d %H:%M:%S')
            results.append({"name": name, "size": size_kb, "last_modified": last_modify})
    except OSError as e:
        log.error("Failed to scan directory: %s | %s", dir, e)
    return results


if __name__ == "__main__":
    json_path = os.path.join(REPORTS_DIR, "loan_snapshot.json")
    csv_path = os.path.join(REPORTS_DIR, "loan_report.csv")
    audit_path = os.path.join(REPORTS_DIR, "pipeline_audit.log")
    pickle_path = os.path.join(REPORTS_DIR, "loan_backup.pkl")

    # Step 1 — fetch live data from MySQL
    trans = fetch_trans_from_db(status="ACTIVE")
    if not trans:
        print("[ERROR] No data fetched - check DB connection & .env (MYSQL_FINTECH_DB)")
        log.error("Pipeline aborted - no records returned from DB")
        sys.exit(1)
    print(f"Fetched       : {len(trans)} ACTIVE records from fintech_demo.loan_accounts")

    # Step 2 — JSON snapshot
    write_json_snapshot(trans, json_path)
    recovered = read_json_snapshot(json_path)
    print(f"JSON snapshot : {len(recovered)} records | amounts as strings: {type(recovered[0]['bal_amt']).__name__}")

    # Step 3 — CSV report
    write_csv_report(trans, csv_path)
    csv_rows = read_csv_report(csv_path)
    print(f"CSV report    : {len(csv_rows)} rows | fields as strings: {type(csv_rows[0]['bal_amt']).__name__}")

    # Step 4 — Audit log entries
    append_audit_log(f"DB fetch: {len(trans)} ACTIVE records from fintech_demo.loan_accounts", audit_path)
    append_audit_log(f"JSON snapshot written: {len(trans)} records -> {json_path}", audit_path)
    append_audit_log(f"CSV report written: {len(trans)} rows -> {csv_path}", audit_path)
    append_audit_log(f"Pickle backup saved -> {pickle_path}", audit_path)
    with open(audit_path, "r", encoding="utf-8") as f:
        entries = f.readlines()
    print(f"Audit log     : {len(entries)} entries (cumulative)")

    # Step 5 — Pickle backup
    save_pickle_bkp(trans, pickle_path)
    loaded = load_pickle_bkp(pickle_path)

    print(f"Pickle backup : {len(loaded)} items | Decimal preserved: {isinstance(loaded[0]['bal_amt'], Decimal)}")

    # Step 6 — OS directory scan
    print(f"\n[ Reports directory: {REPORTS_DIR} ]")
    print(f"  {'File':<28} {'Size (KB)':>10}  Last Modified")
    print(f"  {'-' * 28}  {'-' * 10}  {'-' * 19}")
    for entry in scan_rpt_dir(REPORTS_DIR):
        print(f"  {entry['name']:<28} {entry['size']:>10.2f}  {entry['last_modified']}")

    log.info("fintech_report_handler - run complete.")
