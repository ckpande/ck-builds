# Library Management System

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Oracle](https://img.shields.io/badge/Oracle-19c%2F21c-red)
![License](https://img.shields.io/badge/license-MIT-green)

A console-based application for managing library records backed by Oracle Database.
Built with a layered architecture — routes, services, and data access are fully separated.

---

## Prerequisites

- Python 3.10+
- Oracle Database 19c or 21c (with PDB configured)
- pip

---

## Installation

```bash
git clone <repo-url>
cd library-management
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file at the project root:

```env
DB_USER=your_username
DB_PASS=your_password
DB_DSN=<host>:<port>/<service_name>
LOG_LEVEL=INFO
```

> `.env` is gitignored. Never commit credentials.

---

## Database

Run `create_table_library.sql` in SQL Developer or SQL*Plus before first use.

```sql
CREATE TABLE LIBRARY (
    BNO   NUMBER        PRIMARY KEY,
    BNAME VARCHAR2(100) NOT NULL,
    PRICE NUMBER(8,2),
    PUB   VARCHAR2(100)
);
```

---

## Usage

```bash
python main.py
```

---

## Project Structure

```
library-management/
├── config.py                   # credentials + logging setup
├── db_pool.py                  # Oracle connection pool
├── main.py                     # entry point
├── books/
│   ├── __init__.py
│   ├── models.py               # Book dataclass
│   ├── dao.py                  # all SQL queries
│   ├── services.py             # business logic + validation
│   └── routes.py               # user input/output
├── members/
│   └── __init__.py             # scaffolded
├── loans/
│   └── __init__.py             # scaffolded
├── logs/                       # auto-created on first run (gitignored)
├── create_table_library.sql    # run before first use
├── requirements.txt
├── env.example
└── README.md
```

---

## Architecture

| Layer | Responsibility | Avoids |
|---|---|---|
| `routes.py` | User input / output | Business logic or SQL |
| `services.py` | Validate + business rules | Writing SQL directly |
| `dao.py` | Execute SQL, manage transactions | Validating input |
| `db_pool.py` | Provide connections | Being called from routes or services |

---

## Logging

All log messages go to `logs/library.log`. The file rotates at 5 MB, keeping the last 3 backups automatically.

Control verbosity via `LOG_LEVEL` in `.env` — DEBUG / INFO / WARNING / ERROR / CRITICAL.

---

## Notes

- Uses `oracledb` in thin mode — no Oracle Client required
- Connection pooling via `oracledb.create_pool` (min=2, max=10)
- Deadlock retry with exponential backoff in `run_with_retry`

---

## Roadmap

- [x] Books Management — add, delete, update, search, view
- [ ] Members Management — register, update, deactivate members
- [ ] Loans Management — issue, return, track overdue loans

---

## Author

**Chandrakant Pande**
GitHub: [ckpande](https://github.com/ckpande)

---

## License

MIT. See [LICENSE](LICENSE) file for details.
