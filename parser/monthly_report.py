import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text())


def is_fixed_cost(name: str) -> bool:
    keys = ["월세", "통신요금", "구독", "현대캐피탈", "보험", "자동이체"]
    return any(k in (name or "") for k in keys)


def build_report(items):
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

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_cashflow": net,
        "category_breakdown": by_cat.most_common(),
        "top_expense_transactions": top_tx,
        "fixed_cost_candidates": fixed[:20],
        "uncategorized_count": sum(1 for x in expense if x.get("category") == "미분류"),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python monthly_report.py <normalized.json>")
        sys.exit(1)
    p = Path(sys.argv[1])
    data = load(p)
    report = build_report(data)
    out = p.with_name(p.stem + ".report.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"report -> {out}")


if __name__ == "__main__":
    main()
