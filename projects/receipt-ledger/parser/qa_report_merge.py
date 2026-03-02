import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    bench_json = root / "data" / "benchmark_pipeline_result.json"
    smoke_json = root / "data" / "qa_smoke_report.json"
    out_md = root / "data" / "qa_integrated_summary.md"

    b = json.loads(bench_json.read_text(encoding="utf-8"))
    s = json.loads(smoke_json.read_text(encoding="utf-8"))

    lines = [
        "# Receipt Ledger Integrated QA Summary",
        "",
        "## Benchmark (D12)",
        "",
        f"- rows: {b.get('rows')}",
        f"- repeats: {b.get('repeats')}",
        f"- overall: {'PASS' if b.get('verdict', {}).get('all_pass') else 'FAIL'}",
        "",
        "| step | avg(s) | target(s) | pass |",
        "|---|---:|---:|:---:|",
    ]

    for step, info in (b.get("verdict", {}).get("steps", {})).items():
        lines.append(f"| {step} | {info.get('avg_sec')} | {info.get('target_sec')} | {'✅' if info.get('pass') else '❌'} |")

    failed = [c for c in s.get("cases", []) if not c.get("pass")]
    lines.extend([
        "",
        "## Exceptions/Smoke (D13)",
        "",
        f"- suite: {s.get('suite')}",
        f"- overall: {'PASS' if s.get('all_pass') else 'FAIL'}",
        f"- cases: {len(s.get('cases', []))} (failed: {len(failed)})",
        "",
    ])

    if failed:
        lines.extend(["### Failed Cases", "", "| case | error |", "|---|---|"])
        for c in failed:
            lines.append(f"| {c.get('label')} | {(c.get('error') or '').replace(chr(10), ' ')} |")
        lines.append("")

    lines.extend(["### All Cases", "", "| case | pass |", "|---|:---:|"])
    for c in s.get("cases", []):
        lines.append(f"| {c.get('label')} | {'✅' if c.get('pass') else '❌'} |")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved -> {out_md}")


if __name__ == "__main__":
    main()
