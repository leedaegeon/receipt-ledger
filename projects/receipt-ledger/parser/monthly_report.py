import argparse
import json
from collections import Counter
from pathlib import Path

from fixed_cost import detect_fixed_cost_candidates

REQUIRED_FIELDS = ["occurred_at", "amount", "direction", "merchant_name"]


def load(path: Path):
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"파일 인코딩 오류(UTF-8 필요): {e}") from e

    if not raw.strip():
        raise ValueError("입력 JSON 파일이 비어 있습니다.")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"손상된 JSON 형식입니다: {e}") from e

    if not isinstance(data, list):
        raise ValueError("normalized JSON은 transaction 배열(list)이어야 합니다.")
    if not data:
        raise ValueError("거래 데이터가 비어 있어 리포트를 생성할 수 없습니다.")

    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{idx}번째 항목이 객체(dict)가 아닙니다.")
        missing = [f for f in REQUIRED_FIELDS if f not in item or item.get(f) in (None, "")]
        if missing:
            raise ValueError(f"{idx}번째 항목 필수필드 누락: {', '.join(missing)}")

    return data


def build_report(items, month: str | None = None, account: str | None = None, fixed_cost_options: dict | None = None):
    expense = [x for x in items if x.get("direction") == "expense"]
    income = [x for x in items if x.get("direction") == "income"]

    total_expense = sum(x["amount"] for x in expense)
    total_income = sum(x["amount"] for x in income)
    net = total_income - total_expense

    by_cat = Counter()
    for x in expense:
        by_cat[x.get("category") or "미분류"] += x["amount"]

    top_tx = sorted(expense, key=lambda x: x["amount"], reverse=True)[:10]

    fixed_candidates = detect_fixed_cost_candidates(items, **(fixed_cost_options or {}))

    uncategorized = [x for x in expense if x.get("category") == "미분류"]

    return {
        "meta": {
            "schema_version": "v1",
            "month": month,
            "account": account,
            "currency": "KRW",
        },
        "summary": {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_cashflow": net,
            "expense_count": len(expense),
            "income_count": len(income),
        },
        "category_breakdown": [
            {"category": c, "amount": a, "ratio": round((a / total_expense) * 100, 2) if total_expense else 0}
            for c, a in by_cat.most_common()
        ],
        "top_expenses": top_tx,
        "fixed_candidates": fixed_candidates[:20],
        "uncategorized": {
            "count": len(uncategorized),
            "items": uncategorized[:100],
        },
    }


def parse_args():
    ap = argparse.ArgumentParser(description="Build monthly report from normalized transactions")
    ap.add_argument("normalized_json", help="Path to *.normalized.json")
    ap.add_argument("--month", default=None)
    ap.add_argument("--account", default=None)
    ap.add_argument("--out", default=None, help="Output path for report json")
    ap.add_argument("--fixed-cost-amount-tolerance-ratio", type=float, default=0.15)
    ap.add_argument("--fixed-cost-amount-tolerance-abs", type=int, default=10000)
    ap.add_argument("--fixed-cost-min-months", type=int, default=2)
    ap.add_argument("--fixed-cost-min-average-amount", type=int, default=30000)
    return ap.parse_args()


def main():
    args = parse_args()
    p = Path(args.normalized_json)
    fixed_cost_options = {
        "amount_tolerance_ratio": args.fixed_cost_amount_tolerance_ratio,
        "amount_tolerance_abs": args.fixed_cost_amount_tolerance_abs,
        "min_months": args.fixed_cost_min_months,
        "min_average_amount": args.fixed_cost_min_average_amount,
    }

    try:
        data = load(p)
        report = build_report(data, month=args.month, account=args.account, fixed_cost_options=fixed_cost_options)
    except ValueError as e:
        raise SystemExit(f"리포트 생성 실패: {e}")

    out = Path(args.out) if args.out else p.with_name(p.stem + ".report.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"report -> {out}")


if __name__ == "__main__":
    main()
