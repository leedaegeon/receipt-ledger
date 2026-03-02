import csv
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

from models import Transaction
from normalize import parse_datetime, parse_amount, normalize_merchant, resolve_direction
from classifier import classify
from dedup import make_hash, deduplicate
from user_rules import apply_user_rule
from fixed_cost import detect_fixed_cost_candidates, annotate_fixed_cost_candidates

DATE_HEADERS = ["거래일시", "거래일", "일시", "승인일시"]
AMOUNT_HEADERS = ["거래금액", "출금금액", "입금금액", "금액", "결제금액"]
MERCHANT_HEADERS = ["적요", "거래내용", "거래처", "상대계좌명", "메모"]
DIRECTION_HEADERS = ["거래구분", "입출금구분", "구분"]


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


def _pick(row: dict, keys: list[str]) -> str:
    for k in keys:
        if k in row and str(row[k]).strip():
            return str(row[k]).strip()
    return ""


def _build_tx(date_text: str, direction_text: str, amount_text: str, merchant_text: str, account_label: str) -> Transaction:
    occurred_at = parse_datetime(date_text)
    amount_signed = parse_amount(amount_text)
    direction = resolve_direction(amount_signed, direction_text, merchant_text)
    merchant = (merchant_text or "미상").strip()
    n_merchant = normalize_merchant(merchant)
    base_category = classify(n_merchant)
    category = apply_user_rule(n_merchant, base_category)
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


def parse_csv_with_invalid(path: Path, account_label: str = "토스뱅크") -> Tuple[List[Transaction], list[dict]]:
    rows: List[Transaction] = []
    invalid: list[dict] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for idx, r in enumerate(reader, start=2):
            date_text = _pick(r, DATE_HEADERS)
            amount_text = _pick(r, AMOUNT_HEADERS)
            merchant_text = _pick(r, MERCHANT_HEADERS)
            direction_text = _pick(r, DIRECTION_HEADERS)

            if not sum(bool(x) for x in [date_text, amount_text, merchant_text]) >= 2:
                invalid.append({"row": idx, "reason": "insufficient_fields", "raw": r})
                continue
            try:
                rows.append(_build_tx(date_text, direction_text, amount_text, merchant_text, account_label))
            except Exception as e:
                invalid.append({"row": idx, "reason": f"parse_error:{type(e).__name__}", "raw": r})
                continue
    deduped = deduplicate(rows)
    fixed_candidates = detect_fixed_cost_candidates(deduped)
    annotate_fixed_cost_candidates(deduped, fixed_candidates)
    return deduped, invalid


def parse_csv(path: Path, account_label: str = "토스뱅크") -> List[Transaction]:
    rows, _ = parse_csv_with_invalid(path, account_label)
    return rows


def parse_pdf_with_invalid(path: Path, account_label: str = "토스뱅크") -> Tuple[List[Transaction], list[dict]]:
    parser_js = Path(__file__).with_name("pdf_extract.js")
    proc = subprocess.run(
        ["node", str(parser_js), str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    text = proc.stdout

    owner_match = re.search(r"예금주\s+([가-힣A-Za-z0-9_]+)", text)
    owner_name = owner_match.group(1) if owner_match else ""

    rows: List[Transaction] = []
    invalid: list[dict] = []
    last_idx = -1

    for ln, raw in enumerate(text.splitlines(), start=1):
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
            except Exception as e:
                invalid.append({"line": ln, "reason": f"parse_error:{type(e).__name__}", "raw": line})
            continue

        # 줄바꿈으로 merchant가 이어진 경우 (예: 올리브영 + 관악)
        if last_idx >= 0:
            tail = re.sub(r"\s+", " ", line).strip()
            if tail and len(tail) <= 30 and not re.search(r"\d{4}-\d{2}-\d{2}", tail):
                tx = rows[last_idx]
                tx.merchant_name = f"{tx.merchant_name} {tail}".strip()
                tx.normalized_merchant_name = normalize_merchant(tx.merchant_name)
                base_category = classify(tx.normalized_merchant_name)
                tx.category = apply_user_rule(tx.normalized_merchant_name, base_category)
                continue

        if re.search(r"\d{4}-\d{2}-\d{2}", line):
            invalid.append({"line": ln, "reason": "unmatched_transaction_line", "raw": line})

    if owner_name:
        for tx in rows:
            if owner_name in tx.merchant_name and tx.direction in ("expense", "income"):
                tx.direction = "transfer"
                tx.category = "금융이체"

    deduped = deduplicate(rows)
    fixed_candidates = detect_fixed_cost_candidates(deduped)
    annotate_fixed_cost_candidates(deduped, fixed_candidates)
    return deduped, invalid


def parse_pdf(path: Path, account_label: str = "토스뱅크") -> List[Transaction]:
    rows, _ = parse_pdf_with_invalid(path, account_label)
    return rows
