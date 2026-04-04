# ck-builds

Code. Build. Deploy. — Python · Django · DRF · REST API · JWT · React · Bootstrap · HTML · CSS · JS · Oracle · PL/SQL · MySQL

---

## What's here

### 01-core-python
Core Python scripts and patterns.

| Folder | File | What it does                                                                                                                                                                                             |
|---|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `mysql/` | `mysql_bulk_insert.py` | Bulk upserts employee records using `ON DUPLICATE KEY UPDATE` - tracks insert, update, and unchanged per record with rotating log and full rollback on failure                                           |
| `mysql/` | `db_helper.py` | Shared connection factory - loads credentials from `.env`, validates required keys, supports multiple databases via `db_env_key` parameter                                                  |
| `mysql/` | `mysql_pdbc_basics.py` | Full PDBC foundation - DDL, INSERT single and bulk, SELECT with fetchone/fetchall/fetchmany, UPDATE, DELETE, rollback demo                                                      |
| `mysql/` | `mysql_query_runner.py` | Generic SELECT executor - returns results as list of dicts via `cur.description`, `RotatingFileHandler` logging, fintech domain with `loan_accounts`                                                     |
| `mysql/` | `setup.sql` | MySQL DDL and seed data for `fintech_demo.loan_accounts` - run once before executing `mysql_query_runner.py`                                                                                             |
| `generators/` | `transaction_processor.py` | Streams a transaction CSV through a generator pipeline — filters by type and status, aggregates totals, and writes summaries to JSON                                                                     |
| `decorators/` | `file_logger_decorator.py` | Reusable `@log_execution` decorator - wraps any function with execution timing, structured log entries, and error capture using `functools.wraps` and `perf_counter`                                     |
| `exceptions/` | `fintech_exceptions.py` | Custom exception hierarchy for fintech - 6 domain exception classes with context attributes, Oracle-backed transaction pipeline, exception chaining, and try/except/finally isolation across 9 test cases |
| `exceptions/` | `setup.sql` | Oracle DDL and seed data for `loan_accounts` - run once before executing `fintech_exceptions.py`                                                                                                         |
| `iterators/` | `transaction_iterator.py` | Demonstrates the iterator protocol (`__iter__`, `__next__`, `StopIteration`, and `peek()`) with transaction filtering and running totals over large datasets using O(1) memory                           |

---

### projects
→ See detailed project documentation inside each project folder.

| Project | Stack | Status |
|---|---|---|
| [Library Management System](projects/library-management/README.md) | Python · Oracle · oracledb · 4-layer architecture | 🔄 In Progress |
| Employee Management System | Django · DRF · MySQL · React · JWT | 🔄 Upcoming |
| BiltyBook Fleet & Finance | Django · DRF · Oracle · PL/SQL · React | 🔄 Upcoming |

---

## Author
**Chandrakant Pande** · [ckpande](https://github.com/ckpande)
