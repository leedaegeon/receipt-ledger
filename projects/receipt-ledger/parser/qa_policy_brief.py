import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    integrated = root / "data" / "qa_integrated_summary.md"
    bench = root / "data" / "benchmark_pipeline_result.json"
    smoke = root / "data" / "qa_smoke_report.json"
    out = root / "data" / "qa_policy_brief.md"
    out_json = root / "data" / "qa_action_items.json"

    status_line = "- status(policy): (unknown)"
    if integrated.exists():
        for line in integrated.read_text(encoding="utf-8").splitlines():
            if line.startswith("- status(policy):"):
                status_line = line
                break

    lines = ["# QA Policy Brief", "", status_line, ""]
    action_items = []

    if bench.exists():
        b = json.loads(bench.read_text(encoding="utf-8"))
        failing_steps = [
            k for k, v in b.get("verdict", {}).get("steps", {}).items() if not v.get("pass")
        ]
        lines.append("## Benchmark Fail Steps")
        if failing_steps:
            for s in failing_steps:
                lines.append(f"- 🔴 [HIGH] {s}")
                action_items.append({
                    "priority": "HIGH",
                    "task": f"benchmark step `{s}` 성능 목표 미달 원인 분석/최적화",
                    "owner": "TBD",
                    "due": "TBD",
                    "verify": "python3 benchmark_pipeline.py --rows 5000 --repeats 3 --fail-on-target --out ../data/benchmark_pipeline_result.json",
                })
        else:
            lines.append("- 없음")
        lines.append("")

    if smoke.exists():
        s = json.loads(smoke.read_text(encoding="utf-8"))
        failed_cases = [c for c in s.get("cases", []) if not c.get("pass")]
        lines.append("## Smoke Failed Cases")
        if failed_cases:
            for c in failed_cases:
                label = c.get('label')
                err = (c.get('error') or '').replace(chr(10), ' ')
                lines.append(f"- 🟠 [MEDIUM] {label}: {err}")
                action_items.append({
                    "priority": "MEDIUM",
                    "task": f"smoke case `{label}` 실패 수정 및 fixture/메시지 재검증",
                    "owner": "TBD",
                    "due": "TBD",
                    "verify": "python3 qa_smoke.py --suite exceptions --max-failures 0 --report-json ../data/qa_smoke_report.json",
                })
        else:
            lines.append("- 없음")

    lines.append("")
    lines.append("## Action Items")
    if action_items:
        for idx, item in enumerate(action_items, start=1):
            lines.append(f"### {idx}. [{item['priority']}] {item['task']}")
            lines.append(f"- owner: {item['owner']}")
            lines.append(f"- due: {item['due']}")
            lines.append(f"- verify: `{item['verify']}`")
            lines.append("")
    else:
        lines.append("- 없음 (현재 정책 기준 PASS)")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out_json.write_text(
        json.dumps(
            {
                "status_line": status_line,
                "count": len(action_items),
                "items": action_items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"saved -> {out}")
    print(f"saved -> {out_json}")


if __name__ == "__main__":
    main()
