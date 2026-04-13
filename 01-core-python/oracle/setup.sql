-- setup.sql
-- Oracle DDL and stored procedure for oracle_pdbc_basics.py
-- Run once in SQL Developer, SQL*Plus, or DBeaver before executing the Python script


-- Employees table
-- GENERATED ALWAYS AS IDENTITY replaces the SEQUENCE + TRIGGER pattern from Oracle 11g
-- Requires Oracle 12c or later
CREATE TABLE employees (
    emp_id  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name    VARCHAR2(100) NOT NULL,
    dept    VARCHAR2(50),
    salary  NUMBER(10, 2)
);


-- SP: returns employee count for a given dept.
CREATE OR REPLACE PROCEDURE p_get_emp_count(
    lv_dept  IN  VARCHAR2,
    lv_count OUT NUMBER
) AS
BEGIN
    SELECT COUNT(*) INTO lv_count
    FROM   employees
    WHERE  dept = lv_dept;
END;
/


-- Verify table created
SELECT table_name FROM user_tables WHERE table_name = 'EMPLOYEES';

-- Verify SP created
SELECT object_name, object_type, status
FROM   user_objects
WHERE  object_name = 'P_GET_EMP_COUNT';
