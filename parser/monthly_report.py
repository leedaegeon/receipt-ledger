import argparse
import json
from collections import Counter
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text())


def is_fixed_cost(name: str) -> bool:
    keys = ["월세", "통신요금", "구독", "현대캐피탈", "보험", "자동이체"]
    return any(k in (name or "") for k in keys)


def build_report(items, month: str | None = None, account: str | None = None):
    expense = [x for x in items if x.get("direction") == "expense"]
    income = [x for x in items if x.get("direction") == "income"]

    total_expense = sum(x["amount"] for x in expense)
    total_income = sum(x["amount"] for x in income)
    net = total_income - total_expense

    by_cat = Counter()
    for x in expense:
        by_cat[x.get("category") or "미분류"] += x["amount"]

    top_tx = sorted(expense, key=lambda x: x["amount"], reverse=True)[:10]

    fixed = []
    for x in expense:
        if is_fixed_cost(x.get("merchant_name", "")) or x.get("category") == "주거/고정비":
            fixed.append(x)

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
        "fixed_candidates": fixed[:20],
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
    return ap.parse_args()


def main():
    args = parse_args()
    p = Path(args.normalized_json)
    data = load(p)
    report = build_report(data, month=args.month, account=args.account)
    out = Path(args.out) if args.out else p.with_name(p.stem + ".report.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"report -> {out}")


if __name__ == "__main__":
    main()
