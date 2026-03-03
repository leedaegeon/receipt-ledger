import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    items_path = root / "data" / "qa_action_items.json"
    history_path = root / "data" / "qa_action_history.jsonl"

    if not items_path.exists():
        print(f"skip: not found {items_path}")
        return

    data = json.loads(items_path.read_text(encoding="utf-8"))
    ts = datetime.now(timezone.utc).isoformat()

    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as f:
        for item in data.get("items", []):
            row = {
                "ts": ts,
                "id": item.get("id"),
                "status": item.get("status"),
                "priority": item.get("priority"),
                "source_suite": item.get("source_suite"),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"appended -> {history_path}")


if __name__ == "__main__":
    main()
