import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    bench = root / "data" / "benchmark_pipeline_result.json"
    smoke = root / "data" / "qa_smoke_report.json"
    actions = root / "data" / "qa_action_items.json"
    out = root / "data" / "qa_policy_snapshot.json"
    bench_summary = root / "data" / "benchmark_summary.md"

    b = json.loads(bench.read_text(encoding="utf-8")) if bench.exists() else {}
    s = json.loads(smoke.read_text(encoding="utf-8")) if smoke.exists() else {}
    a = json.loads(actions.read_text(encoding="utf-8")) if actions.exists() else {}

    stddev_threshold_sec = None
    if bench_summary.exists():
        for line in bench_summary.read_text(encoding="utf-8").splitlines():
            if line.startswith("- stddev threshold:"):
                stddev_threshold_sec = line.split(":", 1)[1].strip().rstrip("s")
                break

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark": {
            "all_pass": b.get("verdict", {}).get("all_pass"),
            "targets_sec": b.get("targets_sec", {}),
            "pipeline_total_avg_sec": b.get("pipeline_total_avg_sec"),
            "stddev_threshold_sec": stddev_threshold_sec,
            "fixed_cost_options": b.get("fixed_cost_options", {}),
        },
        "smoke": {
            "suite": s.get("suite"),
            "failed_count": s.get("failed_count"),
            "max_failures": s.get("max_failures"),
        },
        "action_policy": {
            "smoke_escalate_threshold": a.get("smoke_escalate_threshold"),
            "escalated_high_count": len(a.get("escalated_high", [])),
        },
    }

    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
