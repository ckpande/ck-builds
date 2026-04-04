# mysql_query_runner.py | Chandrakant Pande | ck-builds

# Generic SELECT executor — returns results as list of dicts for any table

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import mysql.connector as mysql

from db_helper import get_connection

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOGS_DIR, exist_ok=True)

_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, "mysql_query_runner.log"),
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
)
_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
if not log.handlers:
    log.addHandler(_handler)
    log.addHandler(logging.StreamHandler(sys.stdout))


def run_query(sql, params=None, db_env_key="MYSQL_FINTECH_DB"):
    conn = None
    try:
        conn = get_connection(db_env_key)
        log.info("DB connected | query: %s | params: %s", sql.strip(), params)

        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            columns = [col[0] for col in cur.description]
            rows = cur.fetchall()

        results = [dict(zip(columns, row)) for row in rows]
        log.info("Rows returned: %d", len(results))
        return results
    except mysql.Error as e:
        log.error("MySQL error: %s", e)
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()
            log.info("DB connection closed.")


def _print_table(rows):
    if not rows:
        print(" No records found.")
        return
    headers = list(rows[0].keys())
    print("-" * 80)
    print(" | ".join(headers))
    print("-" * 80)
    for row in rows:
        print(" | ".join(str(row[h]) for h in headers))
    print()


# Run setup.sql before executing this file.
if __name__ == "__main__":
    print("\n[ ACTIVE loan accounts ]")
    _print_table(
        run_query(
            "SELECT acc_id, cust_name, loan_type, bal_amt, status "
            "FROM loan_accounts WHERE status = %s",
            ("ACTIVE",),
        )
    )

    print("[ NPA accounts - require immediate attention ]")
    _print_table(
        run_query(
            "SELECT acc_id, cust_name, loan_type, loan_amt, bal_amt "
            "FROM loan_accounts WHERE status = %s",
            ("NPA",),
        )
    )

    min_bal = 1_000_000.00
    print(f"[ High-value loans - bal_amt above {min_bal:,.2f} ]")
    _print_table(
        run_query(
            "SELECT acc_id, cust_name, loan_type, bal_amt, int_rate "
            "FROM loan_accounts WHERE bal_amt > %s ORDER BY bal_amt DESC",
            (min_bal,),
        )
    )
