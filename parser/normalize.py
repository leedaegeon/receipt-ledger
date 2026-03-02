import re
from datetime import datetime

DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y.%m.%d %H:%M",
    "%Y-%m-%d",
    "%Y/%m/%d %H:%M",
    "%Y/%m/%d",
    "%Y.%m.%d",
]


def parse_datetime(date_text: str) -> datetime:
    raw = (date_text or "").strip()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            if "H" not in fmt:
                return dt.replace(hour=0, minute=0, second=0)
            return dt
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {date_text}")


def parse_amount(amount_text: str) -> int:
    s = (amount_text or "").strip()
    s = s.replace("원", "").replace(",", "").replace(" ", "")
    sign = -1 if s.startswith("-") else 1
    digits = re.sub(r"[^0-9]", "", s)
    if not digits:
        raise ValueError(f"Invalid amount: {amount_text}")
    return sign * int(digits)


def normalize_merchant(name: str) -> str:
    v = re.sub(r"\s+", " ", (name or "").strip())
    v = re.sub(r"(주식회사|\(주\)|주\.)", "", v)
    return v.lower().strip()


def resolve_direction(amount: int, direction_text: str = "", merchant_text: str = "") -> str:
    d = (direction_text or "").lower()
    m = (merchant_text or "")

    if any(k in d for k in ["출금", "결제", "debit"]):
        if "이체" in d or "송금" in d:
            return "transfer"
        return "expense"
    if any(k in d for k in ["입금", "credit"]):
        if "이체" in d or "송금" in d:
            return "transfer"
        return "income"

    if any(k in m for k in ["이체", "송금", "토스"]):
        return "transfer"

    if amount < 0:
        return "expense"
    if amount > 0:
        return "income"
    return "unknown"
