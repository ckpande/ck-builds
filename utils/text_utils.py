# text_utils.py
# Chandrakant Pande - ckpande

import re


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def truncate(text, limit=100, suffix="..."):
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)
    return (cut[0] if len(cut) > 1 else text[:limit]) + suffix


def is_blank(text):
    return not text or not text.strip()


if __name__ == "__main__":
    print("---< slugify >---")
    print(slugify("  Hello World!  "))
    print(slugify("Loan Application -- HDFC Tech 2026"))
    print(slugify("  ₹ Special @@ Chars ##  "))

    print("\n---< truncate >---")
    print(truncate("This is a long sentence that should be cut off after a few words.", 20))
    print(truncate("Short text", 100))
    print(truncate("Nospacesinhere", 5))

    print("\n---< is_blank >---")
    print(is_blank("   "))
    print(is_blank(""))
    print(is_blank(None))
    print(is_blank("not blank"))
