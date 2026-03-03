import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    snapshot = root / "data" / "qa_policy_snapshot.json"
    history = root / "data" / "qa_policy_snapshot_history.jsonl"

    if not snapshot.exists():
        print(f"skip: not found {snapshot}")
        return

    row = json.loads(snapshot.read_text(encoding="utf-8"))
    history.parent.mkdir(parents=True, exist_ok=True)
    with history.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"appended -> {history}")


if __name__ == "__main__":
    main()
