import hashlib
from datetime import datetime


def make_hash(occurred_at: datetime, amount: int, normalized_merchant: str, account_label: str = "") -> str:
    minute_key = occurred_at.strftime("%Y-%m-%d %H:%M")
    key = f"{minute_key}|{amount}|{normalized_merchant}|{account_label or ''}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def deduplicate(items):
    seen = set()
    result = []
    for item in items:
        if item.source_row_hash in seen:
            continue
        seen.add(item.source_row_hash)
        result.append(item)
    return result
