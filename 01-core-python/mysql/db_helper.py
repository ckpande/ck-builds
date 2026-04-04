# db_helper.py | Chandrakant Pande | ck-builds

# Reusable MySQL database connection helper - supports multiple databases via db_env_key.

import os

import mysql.connector as mysql
from dotenv import load_dotenv

load_dotenv()

REQUIRED_KEYS = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASS"]


def get_connection(db_env_key="MYSQL_DB"):
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if not os.getenv(db_env_key):
        missing.append(db_env_key)
    if missing:
        raise ValueError(f"Missing .env keys: {', '.join(missing)}")

    return mysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASS"),
        database=os.getenv(db_env_key),
        connection_timeout=10,
    )


if __name__ == "__main__":
    conn = get_connection()
    print("Connected:", conn.is_connected())
    if conn and conn.is_connected():
        conn.close()
