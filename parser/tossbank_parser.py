import csv
from pathlib import Path
from typing import List

from models import RawRow, Transaction
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


def parse_pdf(path: Path, account_label: str = "토스뱅크") -> List[Transaction]:
    """
    현재 런타임에는 PDF 텍스트 추출 라이브러리가 없어 placeholder로 유지.
    우선순위:
    1) pypdf / pdfplumber 도입
    2) 페이지별 텍스트 추출
    3) 라인 파서(날짜/금액/적요) 적용
    """
    raise NotImplementedError(
        "PDF 파서는 환경 의존 라이브러리 설치 후 활성화됩니다. "
        "임시로 PDF를 CSV로 변환해 parse_csv를 사용하세요."
    )
