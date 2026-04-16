# validators.py
# Chandrakant Pande - ckpande

import re


def valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.fullmatch(pattern, email))


def valid_phone(phone):
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.fullmatch(pattern, phone))


def not_empty(text):
    return bool(text and text.strip())


def len_between(text, min_len=1, max_len=100):
    return min_len <= len(text) <= max_len


def matches(pattern, text):
    return bool(re.fullmatch(pattern, text))


def valid_url(url):
    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    return bool(re.fullmatch(pattern, url))


if __name__ == "__main__":
    print(valid_email("test@example.com"))
    print(valid_phone("+919876543210"))
    print(not_empty(" hello "))
    print(len_between("abc", 2, 5))
    print(matches(r'[A-Z]{3}\d{3}', "ABC123"))
    print(valid_url("https://example.com"))
