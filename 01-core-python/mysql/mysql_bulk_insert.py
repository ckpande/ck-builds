# mysql_bulk_insert.py
# Insert multiple records into a table at once, updates if record already exists.

import os
import logging
import mysql.connector as mysql
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

os.makedirs("logs", exist_ok=True)

handler = RotatingFileHandler("logs/mysql_bulk_insert.log", maxBytes=5 * 1024 * 1024, backupCount=3)
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(handler)
log.addHandler(logging.StreamHandler())

emp_data = [
    (112, 'Arjun Mehta', 7200.00, 'FinEdge'),
    (113, 'Pooja Desai', 8500.50, 'ByteForce'),
    (114, 'Rahul Kulkarni', 6100.75, 'FinEdge'),
    (115, 'Divya Pillai', 9300.00, 'NexaCore'),
    (116, 'Suresh Patil', 5800.25, 'ByteForce'),
    (117, 'Kavita Joshi', 7600.00, 'NexaCore'),
    (118, 'Nikhil Bane', 8900.50, 'FinEdge'),
    (119, 'Shreya Wagh', 6400.00, 'ByteForce'),
    (120, 'Tushar Pawar', 9800.00, 'NexaCore'),
    (121, 'Madhuri Sathe', 7100.75, 'FinEdge'),
    (122, 'Ravi Londhe', 8100.00, 'FinEdge')
]


def insert_emp():
    db_config = {
        'host': os.getenv("MYSQL_HOST"),
        'user': os.getenv("MYSQL_USER"),
        'password': os.getenv("MYSQL_PASS"),
        'database': os.getenv("MYSQL_DB"),
        'port': int(os.getenv("MYSQL_PORT"))
    }

    if not all([db_config['user'], db_config['password'], db_config['database']]):
        raise ValueError("DB credentials missing — check your .env file")

    conn = None
    inserted = 0
    updated = 0
    unchanged = 0

    try:
        conn = mysql.connect(**db_config)
        log.info("Database connected.")

        with conn.cursor() as cur:
            sql = """
                INSERT INTO EMPLOYEE (EMPNO, EMPNAME, SAL, COMPNAME)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    EMPNAME  = VALUES(EMPNAME),
                    SAL      = VALUES(SAL),
                    COMPNAME = VALUES(COMPNAME)
            """

            for record in emp_data:
                cur.execute(sql, record)
                if cur.rowcount == 1:
                    inserted += 1
                    log.info(f"EMPNO {record[0]} — inserted.")
                elif cur.rowcount == 2:
                    updated += 1
                    log.info(f"EMPNO {record[0]} — updated.")
                else:
                    unchanged += 1
                    log.info(f"EMPNO {record[0]} — unchanged.")

            conn.commit()
            log.info(f"Summary — {inserted} inserted, {updated} updated, {unchanged} unchanged.")

    except mysql.Error as e:
        if conn and conn.is_connected():
            conn.rollback()
        log.error(f"MySQL Error: {e}")

    finally:
        if conn and conn.is_connected():
            conn.close()
            log.info("DB connection closed.")


if __name__ == "__main__":
    insert_emp()
