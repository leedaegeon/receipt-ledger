import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    integrated = root / "data" / "qa_integrated_summary.md"
    bench = root / "data" / "benchmark_pipeline_result.json"
    smoke = root / "data" / "qa_smoke_report.json"
    out = root / "data" / "qa_policy_brief.md"

    status_line = "- status(policy): (unknown)"
    if integrated.exists():
        for line in integrated.read_text(encoding="utf-8").splitlines():
            if line.startswith("- status(policy):"):
                status_line = line
                break

    lines = ["# QA Policy Brief", "", status_line, ""]

    if bench.exists():
        b = json.loads(bench.read_text(encoding="utf-8"))
        failing_steps = [
            k for k, v in b.get("verdict", {}).get("steps", {}).items() if not v.get("pass")
        ]
        lines.append("## Benchmark Fail Steps")
        if failing_steps:
            for s in failing_steps:
                lines.append(f"- ❌ {s}")
        else:
            lines.append("- 없음")
        lines.append("")

    if smoke.exists():
        s = json.loads(smoke.read_text(encoding="utf-8"))
        failed_cases = [c for c in s.get("cases", []) if not c.get("pass")]
        lines.append("## Smoke Failed Cases")
        if failed_cases:
            for c in failed_cases:
                lines.append(f"- ❌ {c.get('label')}: {(c.get('error') or '').replace(chr(10), ' ')}")
        else:
            lines.append("- 없음")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
