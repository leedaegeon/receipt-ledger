import json
from collections import Counter, defaultdict
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    hist = root / "data" / "qa_action_history.jsonl"
    out = root / "data" / "qa_action_recurrence.md"

    if not hist.exists():
        out.write_text("# QA Action Recurrence\n\n- history not found\n", encoding="utf-8")
        print(f"saved -> {out}")
        return

    ids = []
    suites_by_id = defaultdict(Counter)
    for line in hist.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = row.get("id")
        if rid:
            ids.append(rid)
            suites_by_id[rid][row.get("source_suite") or "unknown"] += 1

    cnt = Counter(ids)
    lines = [
        "# QA Action Recurrence",
        "",
        "| id | occurrences | source_suites(top) |",
        "|---|---:|---|",
    ]
    for k, v in cnt.most_common(20):
        top_suites = ", ".join([f"{s}:{n}" for s, n in suites_by_id[k].most_common(3)])
        lines.append(f"| {k} | {v} | {top_suites} |")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
