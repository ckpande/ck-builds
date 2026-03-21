# 📚 Library Management System v2.0

A production-grade console application for managing a library — books, members, and loans — built with Python and Oracle Database.
Designed with clean architecture principles: **models** (data), **DAO** (data access), **services** (business logic), and **routes** (CLI interaction).
Includes connection pooling, rotating logging, deadlock retry, and complete separation of concerns.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Oracle](https://img.shields.io/badge/Oracle-19c%2B-red)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 Features

- **Books Management** — add, delete, update price, search, list all books
- **Members Management** — add, update, delete, search, list members *(coming soon)*
- **Loans Management** — issue books, return books, view active loans *(coming soon)*
- **Production-Ready Infrastructure**
  - Connection pooling via `oracledb.create_pool` (min=2, max=10)
  - Rotating file logging — `logs/library.log` (5 MB cap, 3 backups)
  - Automatic deadlock retry — ORA-00060 with exponential backoff (1s → 2s → 4s)
  - Validation at the service layer — price > 0, blank field checks
  - Bind variables throughout — SQL injection safe

---

## 📦 Prerequisites

- Python 3.10 or higher
- Oracle Database 19c or 21c (with a PDB configured)
- `pip` (Python package manager)

---

## 🏛️ Architecture

```
main.py
  │
  ├── config.py       # credentials + logging — shared by all modules
  ├── db_pool.py      # Oracle connection pool — shared by all modules
  │
  ├── books/
  │     models.py     ← dataclass — one row = one object
  │     dao.py        ← all SQL lives here only
  │     services.py   ← validation + business rules
  │     routes.py     ← input/output only
  │
  ├── members/        # coming soon
  └── loans/          # coming soon
```

**Layer rules:**

| Layer | Responsibility | Must NOT |
|---|---|---|
| `routes.py` | User input / output | Contain business logic or SQL |
| `services.py` | Validate, decide, orchestrate | Write SQL directly |
| `dao.py` | Execute SQL, manage transactions | Validate input or raise to UI |
| `db_pool.py` | Provide connections | Be called from routes or services |

---

## 📁 Project Structure

```
library-management/
├── config.py                   # credentials + rotating log setup
├── db_pool.py                  # Oracle connection pool
├── main.py                     # entry point — run this file
├── books/
│   ├── __init__.py
│   ├── models.py               # Book dataclass
│   ├── dao.py                  # SQL: INSERT, UPDATE, DELETE, SELECT
│   ├── services.py             # business logic + validation
│   └── routes.py               # user interface
├── members/
│   └── __init__.py
├── loans/
│   └── __init__.py
├── logs/                       # auto-created on first run (gitignored)
├── create_table_library.sql    # Oracle DDL — run once before first use
├── env.example                 # credential template — copy to .env
├── requirements.txt
└── .gitignore
```

---

## 🔧 Installation

**1. Clone the repository**
```bash
git clone <repo-url>
cd library-management
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure credentials**

Copy `env.example` to `.env` and fill in your Oracle details:
```bash
cp env.example .env
```

```env
DB_USER=your_oracle_username
DB_PASS=your_oracle_password
DB_DSN=localhost:1521/orcl
LOG_LEVEL=INFO
```

> `.env` is gitignored — never commit credentials to version control.

**5. Create database tables**

Run `create_table_library.sql` in SQL Developer or SQL*Plus.
Re-run this file when Members and Loans modules are added.

**6. Run the application**
```bash
python main.py
```

---

## 📋 Modules

### ✅ Books
| Operation | Details |
|---|---|
| Add Book | Insert with duplicate BNO detection (ORA-00001) |
| Delete Book | Confirm prompt before permanent delete |
| Update Price | Validates price > 0 before hitting DB |
| Search Book | Find by Book Number — returns single record |
| View All | Formatted table display with total count |

### 🔲 Members *(coming soon)*
- Register, update, and deactivate library members
- Member ID, name, contact details, membership validity

### 🔲 Loans *(coming soon)*
- Issue and return books
- Track due dates and overdue loans
- Link members to books via loan records

---

## 📝 Logging

All log messages go to both the console and `logs/library.log`.

The log file rotates automatically at 5 MB, keeping the last 3 backups:
```
logs/library.log      ← current
logs/library.log.1    ← previous
logs/library.log.2    ← before that
logs/library.log.3    ← oldest (deleted on next rotation)
```

Control verbosity via `LOG_LEVEL` in `.env`:

| `LOG_LEVEL` | What is logged |
|---|---|
| `DEBUG` | All messages including pool acquire/release |
| `INFO` | Normal operations — inserts, updates, deletes, startup |
| `WARNING` | Deadlock retries and unexpected conditions |
| `ERROR` | Failed operations with full Python stack trace |
| `CRITICAL` | Startup failures — missing credentials, pool init error |

---

## 🎯 Key Design Decisions

| Component | Description |
|---|---|
| Connection Pool | `oracledb.create_pool(min=2, max=10)` — reuses connections, avoids overhead of opening a new connection per operation |
| Logging | `RotatingFileHandler` with file + console handlers, configurable level. Logs include timestamp and full traceback for errors |
| Retry on Deadlock | `run_with_retry` catches ORA-00060 and retries up to 3 times with exponential backoff (1s → 2s → 4s) |
| Layered Architecture | `routes` → `services` → `dao` → `models`. Business logic stays in services. DAO only executes SQL |
| Bind Variables | All SQL uses `:1` / `:name` placeholders — prevents SQL injection and improves Oracle query plan caching |

---

## 🤝 Contributing

When adding a new domain (Members, Loans, etc.), follow this pattern:

1. Create a sub-folder with `__init__.py`, `models.py`, `dao.py`, `services.py`, `routes.py`
2. Implement DAO methods — `insert`, `update`, `delete`, `find_by_id`, `find_all`
3. Add business rules in `services.py`
4. Build the CLI menu in `routes.py`
5. Import and wire into `main.py` — no other files need to change

---

## 🗺️ Roadmap

- [x] Books Management — add, delete, update, search, view
- [ ] Members Management — register, update, deactivate members
- [ ] Loans Management — issue, return, track overdue loans

---

## 🧑‍💻 Author

**Chandrakant Pande**
GitHub: [ckpande](https://github.com/ckpande)

---

## 🙏 Acknowledgements

- [python-oracledb](https://python-oracledb.readthedocs.io/) — Oracle Database driver
- [python-dotenv](https://github.com/theskumar/python-dotenv) — environment variable management

---

## 📄 License

MIT License. See [LICENSE](LICENSE) file for details.
