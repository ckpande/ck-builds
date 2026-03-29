-- setup.sql
-- Oracle table and insert data for fintech_exceptions.py
-- Run once before executing the script.

CREATE TABLE loan_accounts (
    account_id    VARCHAR2(10)   PRIMARY KEY,
    customer_name VARCHAR2(60)   NOT NULL,
    balance       NUMBER(12, 2)  NOT NULL,
    loan_limit    NUMBER(12, 2)  NOT NULL
);

-- ACC003 has low balance to trigger InsufficientFundsError on T002
-- ACC999 is intentionally absent to trigger AccountNotFoundError on T003
INSERT INTO loan_accounts VALUES ('ACC001', 'Chandrakant Pande',  1380000.00, 2000000.00);
INSERT INTO loan_accounts VALUES ('ACC002', 'Pawan Pande',   210000.00,  500000.00);
INSERT INTO loan_accounts VALUES ('ACC003', 'Jayant Raut',    5000.00,  100000.00);

COMMIT;

-- Verify
SELECT account_id, customer_name, balance, loan_limit
  FROM loan_accounts
 ORDER BY account_id;
