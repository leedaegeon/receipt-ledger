import json
from pathlib import Path


def _load_recent_history(history_path: Path, max_items: int = 5):
    if not history_path.exists():
        return []
    rows = []
    for line in history_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-max_items:]


def main():
    root = Path(__file__).resolve().parents[1]
    result_path = root / "data" / "benchmark_pipeline_result.json"
    history_path = root / "data" / "benchmark_history.jsonl"
    out_path = root / "data" / "benchmark_summary.md"

    data = json.loads(result_path.read_text(encoding="utf-8"))
    verdict = data.get("verdict", {})
    steps = verdict.get("steps", {})
    recent = _load_recent_history(history_path)

    lines = []
    lines.append("# Receipt Ledger Benchmark Summary")
    lines.append("")
    lines.append(f"- rows: {data.get('rows')}")
    lines.append(f"- repeats: {data.get('repeats')}")
    lines.append(f"- overall: {'PASS' if verdict.get('all_pass') else 'FAIL'}")
    lines.append("")
    lines.append("| step | avg(s) | target(s) | pass |")
    lines.append("|---|---:|---:|:---:|")

    for step, info in steps.items():
        lines.append(
            f"| {step} | {info.get('avg_sec')} | {info.get('target_sec')} | {'✅' if info.get('pass') else '❌'} |"
        )

    if recent:
        lines.extend([
            "",
            "## Recent Runs (latest 5)",
            "",
            "| ts(UTC) | import avg(s) | export avg(s) | apply avg(s) | report avg(s) | all_pass |",
            "|---|---:|---:|---:|---:|:---:|",
        ])
        for r in recent:
            s = r.get("steps", {})
            lines.append(
                f"| {r.get('ts')} | {s.get('import', {}).get('avg_sec')} | {s.get('export_uncategorized', {}).get('avg_sec')} | {s.get('apply_feedback', {}).get('avg_sec')} | {s.get('monthly_report', {}).get('avg_sec')} | {'✅' if r.get('all_pass') else '❌'} |"
            )

    text = "\n".join(lines) + "\n"
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"saved -> {out_path}")


if __name__ == "__main__":
    main()
