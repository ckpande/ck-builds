# transaction_context.py
# Chandrakant Pande - ck-builds

# Context managers: class-based __enter__/__exit__, @contextmanager, exception suppression

import logging
import os
import sys
from contextlib import contextmanager, suppress
from logging.handlers import RotatingFileHandler

from mysql.connector import Error

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "mysql"))
from db_helper import get_connection

LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, "transaction_context.log"),
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
)
_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

log = logging.getLogger("transaction_context")
log.setLevel(logging.INFO)
if not log.handlers:
    log.addHandler(_handler)
    log.addHandler(logging.StreamHandler())


class ManagedTransaction:
    def __init__(self, db_env_key: str = "MYSQL_DB"):
        self.db_env_key = db_env_key
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.conn = get_connection(self.db_env_key)
        self.cur = self.conn.cursor()
        log.info("Transaction opened | db=%s", self.db_env_key)
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
                log.info("Transaction committed.")
            else:
                self.conn.rollback()
                log.warning("Transaction rolled back | reason: %s: %s", exc_type.__name__, exc_val)
        finally:
            if self.cur:
                self.cur.close()
            if self.conn and self.conn.is_connected():
                self.conn.close()
            log.info("DB connection closed.")
        return False


@contextmanager
def managed_query(db_env_key: str = "MYSQL_DB"):
    conn = None
    cur = None
    try:
        conn = get_connection(db_env_key)
        cur = conn.cursor()
        log.info("Query context opened | db=%s", db_env_key)
        yield cur
        conn.commit()
        log.info("Query committed.")
    except Error as e:
        if conn:
            conn.rollback()
            log.warning("Query rolled back | %s", e)
        raise
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()
        log.info("DB connection closed.")


class SuppressingContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            log.warning("Exception suppressed: %s: %s", exc_type.__name__, exc_val)
        return True


if __name__ == "__main__":
    # 1. Class-based: TWO INSERTs commit atomically
    print("--< ManagedTransaction — successful commit >--")
    with ManagedTransaction("MYSQL_DB") as cur:
        cur.execute(
            "INSERT INTO employees (name,dept,salary) VALUES (%s, %s, %s)",
            ("Context Test A", "Engineering", 72000),
        )
        cur.execute(
            "INSERT INTO employees (name,dept,salary) VALUES (%s, %s, %s)",
            ("Context Test B", "Engineering", 74000),
        )
    print(f"  Both inserted | last emp_id={cur.lastrowid} | commit happened inside __exit__")

    # 2. Class-based: exception after first INSERT rolls back BOTH
    print("\n--< ManagedTransaction - exception rolls back both INSERTs >--")
    try:
        with ManagedTransaction("MYSQL_DB") as cur:
            cur.execute(
                "INSERT INTO employees (name, dept, salary) VALUES (%s, %s, %s)",
                ("Rollback Test A", "QA", 65000),
            )
            cur.execute(
                "INSERT INTO employees (name, dept, salary) VALUES (%s, %s, %s)",
                ("Rollback Test B", "QA", 67000),
            )
            raise ValueError("Intentional mid-transaction failure")
        # rollback happens inside __exit__ — BOTH rows never committed
    except ValueError:
        print("  ValueError caught - rollback confirmed in log")
        print("  Neither 'Rollback Test A' nor 'Rollback Test B' was committed")
        print("  Verify in MySQL Workbench: SELECT * FROM employees WHERE name LIKE 'Rollback%';")

    # 3. @contextmanager: read back employees
    print("\n--< managed_query - SELECT after context manager inserts >--")
    with managed_query("MYSQL_DB") as cur:
        cur.execute("SELECT emp_id, name, dept, salary FROM employees ORDER BY emp_id DESC LIMIT 3")
        rows = cur.fetchall()
    print("  Last 3 employees:")
    for row in rows:
        print(f"    {row[0]} | {row[1]} | {row[2]} | {row[3]:.2f}")

    # 4. SuppressingContext: return True swallows the exception
    print("\n--< SuppressingContext — return True swallows exceptions >--")
    with SuppressingContext():
        raise ValueError("This exception is swallowed - execution continues")
    print("  Execution continued after ValueError - exception was suppressed")
    print("  DO NOT use this pattern in production - exceptions carry information")

    # 5. contextlib.suppress: stdlib suppression for specific exception types
    print("\n--< contextlib.suppress — intentional, specific suppression >--")
    with suppress(FileNotFoundError):
        open("this_file_does_not_exist.txt")
    print("  suppress(FileNotFoundError) - no crash, file simply was not there")

    # 6. Multiple context managers in one with block
    print("\n[ Multiple context managers — single with statement ]")
    with managed_query("MYSQL_DB") as cur, suppress(Exception):
        cur.execute("SELECT COUNT(*) FROM employees")
        row = cur.fetchone()
        print(f"  Employee count: {row[0]} - two context managers in one with block")

    log.info("transaction_context - run complete.")
