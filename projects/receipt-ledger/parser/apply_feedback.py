import argparse
import json
from pathlib import Path

from normalize import normalize_merchant
from user_rules import load_rules, save_rules


def parse_args():
    ap = argparse.ArgumentParser(description="Apply user category feedback and auto-learn rules.json")
    ap.add_argument("normalized_json", help="Path to *.normalized.json")
    ap.add_argument("feedback_json", help="Path to feedback json")
    ap.add_argument("--rules", default=None, help="Custom rules.json path")
    ap.add_argument("--out", default=None, help="Output normalized json path")
    return ap.parse_args()


# feedback schema
# {
#   "items": [
#     {"merchant_name": "씨유인덕원점", "category": "편의점"},
#     {"normalized_merchant_name": "쿠팡(쿠페이)_kicc", "category": "쇼핑"}
#   ]
# }


def main():
    args = parse_args()
    normalized_path = Path(args.normalized_json)
    feedback_path = Path(args.feedback_json)

    if not normalized_path.exists():
        raise SystemExit(f"normalized 파일이 없습니다: {normalized_path}")
    if not feedback_path.exists():
        raise SystemExit(f"feedback 파일이 없습니다: {feedback_path}")

    try:
        txs = json.loads(normalized_path.read_text(encoding="utf-8"))
        feedback = json.loads(feedback_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as e:
        raise SystemExit(f"입력 파일 인코딩 오류(UTF-8 필요): {e}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"손상된 JSON 형식입니다: {e}")

    if not isinstance(txs, list):
        raise SystemExit("normalized JSON은 transaction 배열(list)이어야 합니다.")

    items = feedback.get("items", []) if isinstance(feedback, dict) else feedback
    if not isinstance(items, list):
        raise SystemExit("feedback JSON은 items 배열(list)을 포함해야 합니다.")

    rules = load_rules(Path(args.rules) if args.rules else None)

    updates = 0
    for it in items:
        cat = (it.get("category") or "").strip()
        if not cat:
            continue

        norm = (it.get("normalized_merchant_name") or "").strip()
        if not norm:
            m = (it.get("merchant_name") or "").strip()
            if not m:
                continue
            norm = normalize_merchant(m)

        if not norm:
            continue

        rules[norm] = cat
        updates += 1

    save_rules(rules, Path(args.rules) if args.rules else None)

    # recategorize all transactions based on latest rules
    recategorized = 0
    for tx in txs:
        nm = (tx.get("normalized_merchant_name") or "").strip()
        if not nm:
            nm = normalize_merchant(tx.get("merchant_name", ""))
            tx["normalized_merchant_name"] = nm
        new_cat = rules.get(nm)
        if new_cat and tx.get("category") != new_cat:
            tx["category"] = new_cat
            recategorized += 1

    out_path = Path(args.out) if args.out else normalized_path
    out_path.write_text(json.dumps(txs, ensure_ascii=False, indent=2))

    print(f"rules_updated={updates}")
    print(f"recategorized={recategorized}")
    print(f"rules_total={len(rules)}")
    print(f"normalized_out -> {out_path}")


if __name__ == "__main__":
    main()
