import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    result_path = root / "data" / "benchmark_pipeline_result.json"
    out_path = root / "data" / "benchmark_summary.md"

    data = json.loads(result_path.read_text(encoding="utf-8"))
    verdict = data.get("verdict", {})
    steps = verdict.get("steps", {})

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

    text = "\n".join(lines) + "\n"
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"saved -> {out_path}")


if __name__ == "__main__":
    main()
