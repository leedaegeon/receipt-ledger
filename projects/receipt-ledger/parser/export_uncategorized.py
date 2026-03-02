import argparse
import json
from collections import Counter
from pathlib import Path


def parse_args():
    ap = argparse.ArgumentParser(description="Export uncategorized merchant list as feedback template")
    ap.add_argument("normalized_json", help="Path to *.normalized.json")
    ap.add_argument("--out", default=None, help="Output path (default: *.feedback.template.json)")
    return ap.parse_args()


def main():
    args = parse_args()
    p = Path(args.normalized_json)
    txs = json.loads(p.read_text())

    unc = [x for x in txs if x.get("direction") == "expense" and x.get("category") == "미분류"]
    cnt = Counter(x.get("normalized_merchant_name") or x.get("merchant_name") for x in unc)

    items = []
    for merchant, n in cnt.most_common():
        sample = next((x for x in unc if (x.get("normalized_merchant_name") or x.get("merchant_name")) == merchant), None)
        items.append(
            {
                "merchant_name": sample.get("merchant_name") if sample else merchant,
                "normalized_merchant_name": merchant,
                "count": n,
                "category": ""
            }
        )

    payload = {
        "meta": {
            "source": str(p),
            "uncategorized_expense_count": len(unc),
            "unique_merchants": len(items)
        },
        "items": items
    }

    out = Path(args.out) if args.out else p.with_name(p.stem + ".feedback.template.json")
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"template -> {out}")


if __name__ == "__main__":
    main()
