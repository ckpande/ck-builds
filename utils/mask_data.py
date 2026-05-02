# mask_data.py
# Chandrakant Pande - ckpande

def mask_pan(pan):
    if not pan:
        return ""
    pan = str(pan).strip()
    if len(pan) != 10:
        return pan
    return pan[:5] + "****" + pan[-1]


def mask_ifsc(ifsc):
    if not ifsc:
        return ""
    ifsc = str(ifsc).strip()
    if len(ifsc) != 11:
        return ifsc
    return ifsc[:4] + "****" + ifsc[-3:]


def mask_phone(phone):
    if not phone:
        return ""
    phone = str(phone).strip()
    if len(phone) < 10:
        return phone
    return phone[:2] + "*" * (len(phone) - 4) + phone[-2:]


def mask_email(email):
    if not email or "@" not in str(email):
        return str(email) if email else ""
    local, domain = str(email).strip().split("@", 1)
    if len(local) <= 2:
        masked = local[0] + "*" * (len(local) - 1) if local else ""
    else:
        masked = local[0] + "***" + local[-1]
    return masked + "@" + domain


if __name__ == "__main__":
    print(mask_pan("ABCDE1234F"))
    print(mask_ifsc("HDFC0001234"))
    print(mask_phone(9876543210))
    print(mask_email("chandrakant@example.com"))
    print(mask_email("ab@example.com"))
