import csv
import re
import subprocess
from pathlib import Path
from typing import List

from models import Transaction
from normalize import parse_datetime, parse_amount, normalize_merchant, resolve_direction
from classifier import classify
from dedup import make_hash, deduplicate

DATE_HEADERS = ["거래일시", "거래일", "일시", "승인일시"]
AMOUNT_HEADERS = ["거래금액", "출금금액", "입금금액", "금액", "결제금액"]
MERCHANT_HEADERS = ["적요", "거래내용", "거래처", "상대계좌명", "메모"]
DIRECTION_HEADERS = ["거래구분", "입출금구분", "구분"]


def _pick(row: dict, keys: list[str]) -> str:
    for k in keys:
        if k in row and str(row[k]).strip():
            return str(row[k]).strip()
    return ""


def parse_csv(path: Path, account_label: str = "토스뱅크") -> List[Transaction]:
    rows: List[Transaction] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            date_text = _pick(r, DATE_HEADERS)
            amount_text = _pick(r, AMOUNT_HEADERS)
            merchant_text = _pick(r, MERCHANT_HEADERS)
            direction_text = _pick(r, DIRECTION_HEADERS)

            if not sum(bool(x) for x in [date_text, amount_text, merchant_text]) >= 2:
                continue
            try:
                occurred_at = parse_datetime(date_text)
                amount = parse_amount(amount_text)
                direction = resolve_direction(amount, direction_text, merchant_text)
                merchant = (merchant_text or "미상").strip()
                n_merchant = normalize_merchant(merchant)
                category = classify(n_merchant)
                h = make_hash(occurred_at, abs(amount), n_merchant, account_label)
                rows.append(
                    Transaction(
                        occurred_at=occurred_at,
                        amount=abs(amount),
                        direction=direction,
                        merchant_name=merchant,
                        normalized_merchant_name=n_merchant,
                        category=category,
                        memo=None,
                        account_label=account_label,
                        source_row_hash=h,
                    )
                )
            except Exception:
                continue
    return deduplicate(rows)


ROW_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(.+?)\s+([\-0-9,]+)\s+([\-0-9,]+)\s+(.+)$"
)


SKIP_PREFIXES = (
    "거래내역서",
    "예금주",
    "계좌번호",
    "예금종류",
    "조회기간",
    "본 확인서는",
    "단위:",
    "거래일자",
    "-- ",
)


def _build_tx(date_text: str, direction_text: str, amount_text: str, merchant_text: str, account_label: str) -> Transaction:
    occurred_at = parse_datetime(date_text)
    amount_signed = parse_amount(amount_text)
    direction = resolve_direction(amount_signed, direction_text, merchant_text)
    merchant = (merchant_text or "미상").strip()
    n_merchant = normalize_merchant(merchant)
    category = classify(n_merchant)
    h = make_hash(occurred_at, abs(amount_signed), n_merchant, account_label)
    return Transaction(
        occurred_at=occurred_at,
        amount=abs(amount_signed),
        direction=direction,
        merchant_name=merchant,
        normalized_merchant_name=n_merchant,
        category=category,
        memo=None,
        account_label=account_label,
        source_row_hash=h,
    )


def parse_pdf(path: Path, account_label: str = "토스뱅크") -> List[Transaction]:
    parser_js = Path(__file__).with_name("pdf_extract.js")
    proc = subprocess.run(
        ["node", str(parser_js), str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    text = proc.stdout

    rows: List[Transaction] = []
    last_idx = -1

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(tuple(SKIP_PREFIXES)):
            continue
        if re.match(r"^\d+\s*/\s*\d+", line):
            continue

        m = ROW_RE.match(line)
        if m:
            dt, gubun, amount, _balance, merchant = m.groups()
            try:
                rows.append(_build_tx(dt, gubun, amount, merchant, account_label))
                last_idx = len(rows) - 1
            except Exception:
                continue
            continue

        # 줄바꿈으로 merchant가 이어진 경우 (예: 올리브영 + 관악)
        if last_idx >= 0:
            tail = re.sub(r"\s+", " ", line).strip()
            if tail and len(tail) <= 30 and not re.search(r"\d{4}-\d{2}-\d{2}", tail):
                tx = rows[last_idx]
                tx.merchant_name = f"{tx.merchant_name} {tail}".strip()
                tx.normalized_merchant_name = normalize_merchant(tx.merchant_name)
                tx.category = classify(tx.normalized_merchant_name)

    return deduplicate(rows)
