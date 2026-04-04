# mysql_pdbc_basics.py | Chandrakant Pande | ck-builds

# Basic MySQL operations: connect, DDL, DML (insert/update/delete), DQL (fetch variants), rollback.

from mysql.connector import Error

from db_helper import get_connection


def create_table():
    con = None
    cur = None
    try:
        con = get_connection("MYSQL_DB")
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
            emp_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            dept VARCHAR(50),
            salary DECIMAL(10,2)
            )
        """)
        print("Table 'employees' created (or already exists)")
    except Error as e:
        print(f"[ERROR] create_table: {e}")
    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()


def insert_employee(name, dept, salary):
    con = None
    cur = None
    try:
        con = get_connection("MYSQL_DB")
        cur = con.cursor()
        sql = "INSERT INTO employees (name, dept, salary) VALUES (%s, %s, %s)"
        data = (name, dept, salary)
        cur.execute(sql, data)
        con.commit()
        print(f"Inserted emp_id={cur.lastrowid} | {name}")
    except Error as e:
        print(f"[ERROR] insert_employee: {e}")
        if con:
            con.rollback()
    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()


def insert_many_employees(records):
    con = None
    cur = None
    try:
        con = get_connection("MYSQL_DB")
        cur = con.cursor()
        sql = "INSERT INTO employees (name, dept, salary) VALUES (%s, %s, %s)"
        cur.executemany(sql, records)
        con.commit()
        print(f"Bulk insert complete - {cur.rowcount} rows inserted.")
    except Error as e:
        print(f"[ERROR] insert_many: {e}")
        if con:
            con.rollback()
    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()


def fetch_all_employees():
    con = None
    cur = None
    try:
        con = get_connection("MYSQL_DB")
        cur = con.cursor()
        cur.execute("SELECT emp_id, name, dept, salary FROM employees")
        rows = cur.fetchall()
        print(f"\n{'ID':<6} {'Name':<20} {'Dept':<15} {'Salary':>10}")
        print("-" * 55)
        for row in rows:
            print(f"{row[0]:<6} {row[1]:<20} {row[2]:<15} {row[3]:>10.2f}")
    except Error as e:
        print(f"[ERROR] fetch_all: {e}")
    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()


def fetch_one_employee(emp_id):
    con = None
    cur = None
    try:
        con = get_connection("MYSQL_DB")
        cur = con.cursor()
        cur.execute(
            "SELECT emp_id, name, dept, salary FROM employees WHERE emp_id = %s",
            (emp_id,)
        )
        row = cur.fetchone()
        if row:
            print(f"Found: ID= {row[0]}, Name= {row[1]}, Dept= {row[2]}, Salary= {row[3]}")
        else:
            print(f"No employee found with emp_id={emp_id}")
    except Error as e:
        print(f"[ERROR] fetch_one_employee: {e}")
    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()


def fetch_many_employees(batch_size):
    con = None
    cur = None
    try:
        con = get_connection("MYSQL_DB")
        cur = con.cursor()
        cur.execute("SELECT emp_id, name, dept, salary FROM employees")
        print(f"\nFetching in batches of {batch_size}:")
        while True:
            rows = cur.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                print(f"  {row[0]}: {row[1]} | {row[2]} | {row[3]}")
    except Error as e:
        print(f"[ERROR] fetch_many: {e}")
    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()


def update_salary(emp_id, new_sal):
    con = None
    cur = None
    try:
        con = get_connection("MYSQL_DB")
        cur = con.cursor()
        cur.execute(
            "UPDATE employees SET salary = %s WHERE emp_id = %s",
            (new_sal, emp_id)
        )
        con.commit()
        if cur.rowcount > 0:
            print(f"Updated emp_id={emp_id} salary to {new_sal}")
        else:
            print(f"No row updated - emp_id={emp_id} not found.")
    except Error as e:
        print(f"[ERROR] update_salary: {e}")
        if con:
            con.rollback()
    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()


def delete_employee(emp_id):
    con = None
    cur = None
    try:
        con = get_connection("MYSQL_DB")
        cur = con.cursor()
        cur.execute("DELETE FROM employees WHERE emp_id = %s", (emp_id,))
        con.commit()
        if cur.rowcount > 0:
            print(f"Deleted emp_id={emp_id}")
        else:
            print(f"No row deleted - emp_id={emp_id} not found.")
    except Error as e:
        print(f"[ERROR] delete_employee: {e}")
        if con:
            con.rollback()
    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()


def demo_rollback():
    con = None
    cur = None
    try:
        con = get_connection("MYSQL_DB")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO employees (name, dept, salary) VALUES (%s, %s, %s)",
            ("Temp User", "Test", 10000)
        )
        cur.execute(
            "INSERT INTO employees (name, dept, salary) VALUES (%s, %s, %s)",
            ("Bad User", "Test", "NOT_A_NUMBER")
        )
        con.commit()
    except Error as e:
        print(f"[Rollback_demo] Error: {e}")
        if con:
            con.rollback()
            print("[ROLLBACK DEMO] Transaction rolled back - database unchanged.")
    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()


if __name__ == "__main__":
    print("Step 1: Create Table")
    create_table()

    print("\nStep 2: Insert Single Employees")
    insert_employee("Chandrakant", "Engineering", 95000)
    insert_employee("Pawan", "Finance", 82000)
    insert_employee("Nisha", "Operations", 74000)

    print("\nStep 3: Bulk insert")
    bulk_data = [
        ("Jayant", "HR", 68000),
        ("Vishakha", "Engineering", 99000),
        ("Warun", "Finance", 77000),
    ]
    insert_many_employees(bulk_data)

    print("\nStep 4a: fetchall")
    fetch_all_employees()

    print("\nStep 4b: fetchone (emp_id=1)")
    fetch_one_employee(1)

    print("\nStep 4c: fetchmany batch=2")
    fetch_many_employees(2)

    print("\nStep 5: Update salary for emp_id=1")
    update_salary(1, 105000)

    print("\nStep 6: Delete emp_id=3")
    delete_employee(3)

    print("\nStep 7: Fetch after update/delete")
    fetch_all_employees()

    print("\nStep 8: Rollback demo")
    demo_rollback()

    print("\nStep 9: Final state - rollback changed nothing")
    fetch_all_employees()
