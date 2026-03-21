# Library Management System

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
cd 04-projects/library-management
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
├── config.py               # credentials + logging setup
├── db_pool.py              # Oracle connection pool
├── main.py                 # entry point
├── books/
│   ├── __init__.py
│   ├── models.py           # Book dataclass
│   ├── dao.py              # all SQL queries
│   ├── services.py         # business logic + validation
│   └── routes.py           # user input/output
├── requirements.txt
├── env.example
└── README.md
```

---

## Notes

- Uses `oracledb` in thin mode — no Oracle Client required
- Connection pooling via `orc.create_pool` (min=2, max=10)
- Deadlock retry with exponential backoff in `run_with_retry`
- Rotating file logging — `logs/library.log` (max 5MB, 3 backups)
- `LOG_LEVEL` configurable via `.env` (DEBUG / INFO / WARNING)
- `members/` and `loans/` modules scaffolded — ready for implementation

---

## License

MIT
