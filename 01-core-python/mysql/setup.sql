-- setup.sql |
-- Run once in MySQL Workbench or CLI before executing mysql_query_runner.py

-- Create fintech_demo database if it does not exist for mysql_query_runner.py
CREATE DATABASE IF NOT EXISTS fintech_demo;

USE fintech_demo;

-- Creates loan_accounts table and seeds test data for mysql_query_runner.py
CREATE TABLE IF NOT EXISTS loan_accounts (
    acc_id VARCHAR(10) PRIMARY KEY,
    cust_name VARCHAR(60) NOT NULL,
    loan_type ENUM('HOME', 'PERSONAL', 'AUTO', 'EDUCATION') NOT NULL,
    loan_amt DECIMAL(12 , 2 ) NOT NULL,
    bal_amt DECIMAL(12 , 2 ) NOT NULL,
    int_rate DECIMAL(5 , 2 ) NOT NULL,
    status ENUM('ACTIVE', 'CLOSED', 'NPA') NOT NULL DEFAULT 'ACTIVE',
    disb_date DATE NOT NULL
);

INSERT INTO loan_accounts VALUES
('ACC001', 'Chandrakant Pande',    'HOME',      1500000.00, 1380000.00,  8.50, 'ACTIVE', '2023-04-01'),
('ACC002', 'Pawan Pande',    'PERSONAL',   350000.00,  210000.00, 12.75, 'ACTIVE', '2023-07-15'),
('ACC003', 'Nisha Ingole', 'AUTO',        800000.00,  560000.00,  9.20, 'ACTIVE', '2022-11-10'),
('ACC004', 'Jayant Raut',   'EDUCATION',  600000.00,       0.00,  7.00, 'CLOSED', '2020-06-01'),
('ACC005', 'Vishakha Raut',   'HOME',      2500000.00, 2490000.00,  8.75, 'NPA',    '2024-01-20'),
('ACC006', 'Warun Bhoyar',   'PERSONAL',   200000.00,  195000.00, 13.00, 'ACTIVE', '2025-02-28'),
('ACC007', 'Rupali Raut',    'AUTO',        950000.00,  430000.00,  9.50, 'ACTIVE', '2021-09-05'),
('ACC008', 'Abhijeet Helonde',    'HOME',      1800000.00, 1750000.00,  8.25, 'NPA',    '2023-12-01'),
('ACC009', 'Jyoti Helonde',   'EDUCATION',  450000.00,  225000.00,  7.50, 'ACTIVE', '2022-08-18'),
('ACC010', 'Anusaya Pande',  'PERSONAL',   500000.00,  500000.00, 12.50, 'ACTIVE', '2026-01-10');

-- Verify
SELECT COUNT(*)
FROM fintech_demo.loan_accounts;

