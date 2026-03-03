import json
from collections import Counter
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
    for line in hist.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("id"):
            ids.append(row["id"])

    cnt = Counter(ids)
    lines = [
        "# QA Action Recurrence",
        "",
        "| id | occurrences |",
        "|---|---:|",
    ]
    for k, v in cnt.most_common(20):
        lines.append(f"| {k} | {v} |")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
