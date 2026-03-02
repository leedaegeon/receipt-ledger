import argparse
import json
from pathlib import Path


def parse_args():
    ap = argparse.ArgumentParser(description="Check HIGH action items owner/due assignment")
    ap.add_argument("--path", default="../data/qa_action_items.json")
    ap.add_argument("--fail-on-unassigned-high", action="store_true")
    return ap.parse_args()


def main():
    args = parse_args()
    p = Path(args.path)
    if not p.exists():
        print(f"skip: not found {p}")
        return

    data = json.loads(p.read_text(encoding="utf-8"))
    items = data.get("items", [])
    warn = [
        x for x in items
        if x.get("priority") == "HIGH" and (x.get("owner") == "TBD" or x.get("due") == "TBD")
    ]

    if warn:
        print("## ⚠️ HIGH Action Items need owner/due")
        for w in warn:
            print(f"- {w.get('task')} (owner={w.get('owner')}, due={w.get('due')})")

    if args.fail_on_unassigned_high and warn:
        raise SystemExit(f"unassigned HIGH action items: {len(warn)}")


if __name__ == "__main__":
    main()
