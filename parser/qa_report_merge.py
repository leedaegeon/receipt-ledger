import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    bench_json = root / "data" / "benchmark_pipeline_result.json"
    smoke_json = root / "data" / "qa_smoke_report.json"
    out_md = root / "data" / "qa_integrated_summary.md"

    b = json.loads(bench_json.read_text(encoding="utf-8"))
    s = json.loads(smoke_json.read_text(encoding="utf-8"))

    bench_pass = bool(b.get("verdict", {}).get("all_pass"))
    failed = [c for c in s.get("cases", []) if not c.get("pass")]
    failed_count = int(s.get("failed_count", len(failed)))
    max_failures = int(s.get("max_failures", 0))
    smoke_policy_pass = failed_count <= max_failures
    smoke_reported_pass = bool(s.get("all_pass"))
    overall_policy_pass = bench_pass and smoke_policy_pass

    lines = [
        "# Receipt Ledger Integrated QA Summary",
        "",
        f"- status(policy): {'✅ PASS' if overall_policy_pass else '❌ FAIL'}",
        f"- benchmark: {'✅ PASS' if bench_pass else '❌ FAIL'}",
        f"- smoke(policy): {'✅ PASS' if smoke_policy_pass else '❌ FAIL'} (failed={failed_count}, allowed={max_failures})",
        f"- smoke(reported): {'✅ PASS' if smoke_reported_pass else '❌ FAIL'}",
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

    lines.extend([
        "",
        "## Exceptions/Smoke (D13)",
        "",
        f"- suite: {s.get('suite')}",
        f"- overall(reported): {'PASS' if smoke_reported_pass else 'FAIL'}",
        f"- policy: {'PASS' if smoke_policy_pass else 'FAIL'} (failed={failed_count}, allowed={max_failures})",
        f"- cases: {len(s.get('cases', []))}",
        "",
    ])

    if max_failures > 0:
        lines.append(f"> ⚠️ `max_failures={max_failures}` 설정으로 일부 실패가 허용됩니다.")
        lines.append("")

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
