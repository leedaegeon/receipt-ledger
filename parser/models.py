from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RawRow:
    date_text: str
    amount_text: str
    merchant_text: str
    direction_text: Optional[str] = None
    account_label: Optional[str] = None


@dataclass
class Transaction:
    occurred_at: datetime
    amount: int
    direction: str  # expense|income|transfer|unknown
    merchant_name: str
    normalized_merchant_name: str
    category: str
    memo: Optional[str]
    account_label: Optional[str]
    source_row_hash: str
