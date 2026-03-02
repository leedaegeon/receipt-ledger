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
    if not p.exists():
        raise SystemExit(f"입력 파일이 없습니다: {p}")

    try:
        raw = p.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise SystemExit(f"입력 파일 인코딩 오류(UTF-8 필요): {e}")

    if not raw.strip():
        raise SystemExit("입력 JSON 파일이 비어 있습니다.")

    try:
        txs = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"손상된 JSON 형식입니다: {e}")

    if not isinstance(txs, list):
        raise SystemExit("normalized JSON은 transaction 배열(list)이어야 합니다.")

    unc = [x for x in txs if isinstance(x, dict) and x.get("direction") == "expense" and x.get("category") == "미분류"]
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
