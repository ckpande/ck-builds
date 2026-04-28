# date_utils.py
# Chandrakant Pande - ckpande

from datetime import date, timedelta


def business_days_between(start, end):
    if start > end:
        return 0
    total_days = (end - start).days
    weeks = total_days // 7
    business_days = weeks * 5
    start_weekday = start.weekday()
    for i in range(total_days % 7 + 1):
        if (start_weekday + i) % 7 < 5:
            business_days += 1
    return business_days


def add_business_days(start_date, days_to_add):
    if days_to_add < 0:
        raise ValueError("days_to_add must be positive")
    weeks = days_to_add // 5
    remaining = days_to_add % 5
    result = start_date + timedelta(weeks=weeks)
    while remaining > 0:
        result += timedelta(days=1)
        if result.weekday() < 5:
            remaining -= 1
    return result


def format_date(dt, fmt="%Y-%m-%d"):
    return dt.strftime(fmt)


if __name__ == "__main__":
    d1 = date(2026, 4, 1)
    d2 = date(2026, 4, 30)
    print(f"Business days: {business_days_between(d1, d2)}")
    print(f"Add 5 business days to {d1}: {add_business_days(d1, 5)}")
    future = date(2076, 4, 1)
    print(f"50-year count: {business_days_between(d1, future)}")
