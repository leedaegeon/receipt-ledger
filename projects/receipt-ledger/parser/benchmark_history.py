import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    result_path = root / "data" / "benchmark_pipeline_result.json"
    history_path = root / "data" / "benchmark_history.jsonl"

    data = json.loads(result_path.read_text(encoding="utf-8"))
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "rows": data.get("rows"),
        "repeats": data.get("repeats"),
        "all_pass": data.get("verdict", {}).get("all_pass"),
        "steps": {
            k: {
                "avg_sec": v.get("avg_sec"),
                "target_sec": data.get("targets_sec", {}).get(k),
            }
            for k, v in data.get("steps", {}).items()
        },
    }

    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"appended -> {history_path}")


if __name__ == "__main__":
    main()
