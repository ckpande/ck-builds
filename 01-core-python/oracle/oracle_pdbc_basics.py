# oracle_pdbc_basics.py
# Chandrakant Pande - ck-builds
#
# Oracle PDBC with oracledb thin mode: connect, DDL, DML, DQL, bind variables, stored procedure

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
    os.path.join(LOGS_DIR, "oracle_pdbc_basics.log"),
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
)
_handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s"))
log = logging.getLogger("oracle_pdbc")
log.setLevel(logging.INFO)
if not log.handlers:
    log.addHandler(_handler)
    log.addHandler(logging.StreamHandler())

_REQUIRED_KEYS = ["DB_USER", "DB_PASS", "DB_DSN"]


def get_connection():
    missing = [k for k in _REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        raise ValueError(f"Missing .env keys: {', '.join(missing)}")
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN"),
    )


def create_table():
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE employees (
                emp_id  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name    VARCHAR2(100) NOT NULL,
                dept    VARCHAR2(50),
                salary  NUMBER(10, 2)
            )
        """)
        con.commit()
        print("Table 'employees' created.")
    except oracledb.DatabaseError as e:
        error, = e.args
        if error.code == 955:
            print("Table 'employees' already exists.")
        else:
            log.error("create_table failed: %s", e)
            raise
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def insert_employee(name: str, dept: str, salary: float) -> int | None:
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        emp_id_var = cur.var(oracledb.NUMBER)
        sql = """
            INSERT INTO employees (name, dept, salary)
            VALUES (:name, :dept, :salary)
            RETURNING emp_id INTO :emp_id
        """
        data = {"name": name, "dept": dept, "salary": salary, "emp_id": emp_id_var}
        cur.execute(sql, data)
        con.commit()
        inserted_id = int(emp_id_var.getvalue()[0])
        print(f"Inserted emp_id={inserted_id} |  {name}")
        return inserted_id
    except oracledb.DatabaseError as e:
        log.error("insert_employee failed: %s", e)
        if con:
            con.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def insert_many_employees(records: list[dict]) -> None:
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        sql = "INSERT INTO employees (name, dept, salary) VALUES (:name, :dept, :salary)"
        cur.executemany(sql, records)
        con.commit()
        print(f"Bulk insert complete - {cur.rowcount} rows inserted.")
    except oracledb.DatabaseError as e:
        log.error("insert_many failed: %s", e)
        if con:
            con.rollback()
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def fetch_all_employees() -> None:
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT emp_id, name, dept, salary FROM employees ORDER BY emp_id")
        rows = cur.fetchall()
        print(f"\n{'ID':<8} {'Name':<20} {'Dept':<15} {'Salary':>10}")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<8} {row[1]:<20} {row[2]:<15} {row[3]:>10.2f}")
    except oracledb.DatabaseError as e:
        log.error("fetch_all failed: %s", e)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def fetch_one_employee(emp_id: int) -> None:
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT emp_id, name, dept, salary FROM employees WHERE emp_id = :emp_id",
            {"emp_id": emp_id},
        )
        row = cur.fetchone()
        if row:
            print(f"Found: ID={row[0]}, Name={row[1]}, Dept={row[2]}, Salary={row[3]}")
        else:
            print(f"No employee found with emp_id={emp_id}")
    except oracledb.DatabaseError as e:
        log.error("fetch_one failed: %s", e)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def fetch_many_employees(batch_size: int) -> None:
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        cur.arraysize = batch_size
        cur.execute("SELECT emp_id, name, dept, salary FROM employees ORDER BY emp_id")
        print(f"\nFetching in batches of {batch_size}")
        while True:
            rows = cur.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                print(f"  {row[0]}: {row[1]} | {row[2]} | {row[3]}")
    except oracledb.DatabaseError as e:
        log.error("fetch_many failed: %s", e)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def update_salary(emp_id: int, new_sal: float) -> None:
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "UPDATE employees SET salary = :salary WHERE emp_id = :emp_id",
            {"salary": new_sal, "emp_id": emp_id},
        )
        con.commit()
        if cur.rowcount > 0:
            print(f"Updated emp_id={emp_id} salary to {new_sal}")
        else:
            print(f"No row updated  - emp_id={emp_id} not found")
    except oracledb.DatabaseError as e:
        log.error("update_salary failed: %s", e)
        if con:
            con.rollback()
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def delete_employee(emp_id: int) -> None:
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "DELETE FROM employees WHERE emp_id = :emp_id",
            {"emp_id": emp_id},
        )
        con.commit()
        if cur.rowcount > 0:
            print(f"Deleted emp_id={emp_id}")
        else:
            print(f"No row deleted - emp_id={emp_id} not found")
    except oracledb.DatabaseError as e:
        log.error("delete_employee failed: %s", e)
        if con:
            con.rollback()
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def get_dept_count(dept: str) -> int | None:
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        count_var = cur.var(oracledb.NUMBER)
        cur.callproc("p_get_emp_count", [dept, count_var])
        result = int(count_var.getvalue())
        print(f"Dept '{dept}' has {result} employees(s) - via Stored procedure")
        log.info("get_dept_count | dept=%s | count=%d", dept, result)
        return result
    except oracledb.DatabaseError as e:
        log.error("get_dept_count failed: %s", e)
        return None
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def demo_rollback() -> None:
    con = None
    cur = None
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO employees (name, dept, salary) VALUES (:name, :dept, :salary)",
            {"name": "Rollback Test A", "dept": "Test", "salary": 10000},
        )
        cur.execute(
            "INSERT INTO employees (name, dept, salary) VALUES (:name, :dept, :salary)",
            {"name": "Rollback Test B", "dept": "Test", "salary": "NOT_A_NUMBER"},  # intentional
        )
        con.commit()
    except oracledb.DatabaseError as e:
        print(f"[ROLLBACK DEMO] error caught: {e}")
        if con:
            con.rollback()
            print("[ROLLBACK DEMO] Transaction rolled back - database unchanged")
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


if __name__ == "__main__":
    print("1: ----<< Create Table >>----")
    create_table()

    print("\n2: ---<< Insert single employees >>---")
    insert_employee("Chandrakant", "Engineering", 95000)
    insert_employee("Warun", "Finance", 82000)
    insert_employee("Jayant", "Operations", 74000)

    print("\n3: ---<< Bulk insert >>---")
    bulk_data = [
        {"name": "Harshad", "dept": "HR", "salary": 68000},
        {"name": "Ram", "dept": "Engineering", "salary": 99000},
        {"name": "Amir", "dept": "Finance", "salary": 77000},
    ]
    insert_many_employees(bulk_data)

    print("\n4a: ---<< fetchall >>---")
    fetch_all_employees()

    print("\n4b: ---<< fetchone (emp_id=1) >>---")
    fetch_one_employee(1)

    print("\n4c: ---<< fetchmany batch=2 >>---")
    fetch_many_employees(2)

    print("\n5: ---<< Update salary for emp_id=1 >>---")
    update_salary(1, 105000)

    print("\n6: ---<< Delete emp_id=3 >>---")
    delete_employee(3)

    print("\n7: ---<< Fetch after update/delete >>---")
    fetch_all_employees()

    print("\n8: ---<< SP - get_employee_count >>---")
    get_dept_count("Engineering")

    print("\n9: ---<< Rollback demo >>---")
    demo_rollback()

    print("\n10: ---<< Final check - rollback changed nothing >>---")
    fetch_all_employees()
