# loan_data_processor.py
# Chandrakant Pande - ck-builds

# Comprehensions: list, dict, set, generator expressions applied to fintech loan data

import sys

LOANS: list[dict] = [
    {"acc_id": "ACC001", "cust_name": "Chandrakant Pande", "loan_type": "HOME", "loan_amt": 1500000.00,
     "bal_amt": 1380000.00, "int_rate": 8.50, "status": "ACTIVE"},
    {"acc_id": "ACC002", "cust_name": "Pawan Pande", "loan_type": "PERSONAL", "loan_amt": 350000.00,
     "bal_amt": 210000.00, "int_rate": 12.75, "status": "ACTIVE"},
    {"acc_id": "ACC003", "cust_name": "Harshad Ingole", "loan_type": "AUTO", "loan_amt": 800000.00,
     "bal_amt": 560000.00, "int_rate": 9.20, "status": "ACTIVE"},
    {"acc_id": "ACC004", "cust_name": "Jayant Raut", "loan_type": "EDUCATION", "loan_amt": 600000.00, "bal_amt": 0.00,
     "int_rate": 7.00, "status": "CLOSED"},
    {"acc_id": "ACC005", "cust_name": "Ram Kubde", "loan_type": "HOME", "loan_amt": 2500000.00, "bal_amt": 2490000.00,
     "int_rate": 8.75, "status": "NPA"},
    {"acc_id": "ACC006", "cust_name": "Warun Bhoyar", "loan_type": "PERSONAL", "loan_amt": 200000.00,
     "bal_amt": 195000.00, "int_rate": 13.00, "status": "ACTIVE"},
    {"acc_id": "ACC007", "cust_name": "Prajwal Raut", "loan_type": "AUTO", "loan_amt": 950000.00, "bal_amt": 430000.00,
     "int_rate": 9.50, "status": "ACTIVE"},
    {"acc_id": "ACC008", "cust_name": "Abhijeet Helonde", "loan_type": "HOME", "loan_amt": 1800000.00,
     "bal_amt": 1750000.00, "int_rate": 8.25, "status": "NPA"},
    {"acc_id": "ACC009", "cust_name": "Sagar Rane", "loan_type": "EDUCATION", "loan_amt": 450000.00,
     "bal_amt": 225000.00, "int_rate": 7.50, "status": "ACTIVE"},
    {"acc_id": "ACC010", "cust_name": "Abhishek Kshirsagar", "loan_type": "PERSONAL", "loan_amt": 500000.00,
     "bal_amt": 500000.00, "int_rate": 12.50, "status": "ACTIVE"},
]


# LIST COMPREHENSIONS
def active_acct_ids(loans: list[dict]) -> list[str]:
    return [loan["acc_id"] for loan in loans if loan["status"] == "ACTIVE"]


def npa_summaries(loans: list[dict]) -> list[str]:
    return [
        f"{loan['acc_id']} | {loan['cust_name']} | {loan['loan_type']} | {loan['bal_amt']:,.2f}"
        for loan in loans if loan["status"] == "NPA"
    ]


def high_bal_loans(loans: list[dict], min_bal: float) -> list[dict]:
    return [loan for loan in loans if loan['bal_amt'] >= min_bal]


def repayment_percentages(loans: list[dict]) -> list[dict]:
    return [
        {"acc_id": loan["acc_id"], "repaid_pct": round((1 - loan["bal_amt"] / loan["loan_amt"]) * 100, 2)}
        for loan in loans if loan["loan_amt"] > 0
    ]


def normalise_names(loans: list[dict]) -> list[dict]:
    return [{**loan, "cust_name": loan["cust_name"].upper()} for loan in loans]


# DICT COMPREHENSIONS
def bal_by_account(loans: list[dict]) -> dict[str, float]:
    return {loan["acc_id"]: loan["bal_amt"] for loan in loans}


def status_map(loans: list[dict]) -> dict[str, str]:
    return {loan["acc_id"]: loan["status"] for loan in loans}


def rate_by_type(loans: list[dict]) -> dict[str, float]:
    type_rates: dict[str, list] = {}
    for loan in loans:
        type_rates.setdefault(loan["loan_type"], []).append(loan["int_rate"])
    return {lt: round(sum(rates) / len(rates), 2) for lt, rates in type_rates.items()}


# SET COMPREHENSIONS
def unique_loan_types(loans: list[dict]) -> set[str]:
    return {loan["loan_type"] for loan in loans}


def active_cust_names(loans: list[dict]) -> set[str]:
    return {loan["cust_name"] for loan in loans if loan["status"] == "ACTIVE"}


# GENERATOR EXPRESSIONS
def total_active_balance(loans: list[dict]) -> float:
    return round(sum(loan["bal_amt"] for loan in loans if loan["status"] == "ACTIVE"), 2)


def high_risk_loan(loans: list[dict], min_bal_rate: float) -> bool:
    return any(
        loan["int_rate"] > min_bal_rate
        for loan in loans if loan["status"] == "ACTIVE"
    )


def npa_count(loans: list[dict]) -> int:
    return sum(1 for loan in loans if loan["status"] == "NPA")


# NESTED COMPREHENSION
def all_loan_fields(loans: list[dict]) -> list[tuple]:
    return [
        (loan["acc_id"], k, v)
        for loan in loans
        for k, v in loan.items()
    ]


if __name__ == "__main__":
    print("-------------------------------------------")
    print("------<< List Comprehension >>------")
    print("-------------------------------------------")
    ids = active_acct_ids(LOANS)
    print(f"  active_account_ids      : {ids}")

    npas = npa_summaries(LOANS)
    print(f"  npa_summaries           :  {len(npas)} NPA accounts")
    for s in npas:
        print(f"    {s}")

    high_bal = high_bal_loans(LOANS, 1_000_000.00)
    print(f"  high_balance_loans >10 lakhs  : {[l['acc_id'] for l in high_bal]}")

    pcts = repayment_percentages(LOANS)
    print(f"  repayment_percentages   : {pcts[:3]} ... (ACC004 fully repaid, bal_amt=0)")

    names = normalise_names(LOANS)
    print(f"  normalise_names         : {names[0]['cust_name']} | original: {LOANS[0]['cust_name']}")

    print("\n-------------------------------------------")
    print("------<< Dict Comprehensions >>------")
    print("-------------------------------------------")
    bal = bal_by_account(LOANS)
    print(f"  bal_by_account           : ACC001={bal['ACC001']:,.2f}, ACC005={bal['ACC005']:,.2f}")

    smap = status_map(LOANS)
    print(f"  status_map               : ACC004={smap['ACC004']}, ACC005={smap['ACC005']}")

    rates = rate_by_type(LOANS)
    print(f"  rates_by_type            : {rates}")

    print("\n-------------------------------------------")
    print('------<< Set Comprehensions >>------')
    print("-------------------------------------------")

    types = unique_loan_types(LOANS)
    print(f"  unique_loan_types         : {types}")

    act_names = active_cust_names(LOANS)
    print(
        f"  active_customer_names     : {len(act_names)} names | membership check: {'Chandrakant Pande' in act_names}")
    print("\n-------------------------------------------")
    print("------<< Generator Expressions >>------")
    print("-------------------------------------------")

    total = total_active_balance(LOANS)
    print(f"  total_active_balance       : {total:,.2f}")

    high_risk = high_risk_loan(LOANS, 12.0)
    print(f"  has_high_risk_loan > 12% : {high_risk}")

    npac = npa_count(LOANS)
    print(f"  npa_count                : {npac}")

    print("\n-------------------------------------------")
    print("------<< Nested Comprehension >>------")
    print("-------------------------------------------")

    fields = all_loan_fields(LOANS)
    print(f"  all_loan_fields          : {len(fields)} tuples (10 loans * 8 fields)")
    print(f"  first tuple              : {fields[0]}")

    print("\n-------------------------------------------")
    print("------<< Memory: List vs Generator >>------")
    print("-------------------------------------------")
    list_result = [loan["bal_amt"] for loan in LOANS if loan["status"] == "ACTIVE"]
    gen_result = (loan["bal_amt"] for loan in LOANS if loan["status"] == "ACTIVE")
    print(f"  list comprehension size : {sys.getsizeof(list_result)} bytes (stores all values)")
    print(f"  generator expression    : {sys.getsizeof(gen_result)} bytes (stores only the frame)")
    print(f"  difference grows with data size - at 1 crore rows: list=gigabytes, gen=~200 bytes")
