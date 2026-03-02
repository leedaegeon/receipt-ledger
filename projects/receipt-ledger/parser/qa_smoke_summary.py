import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    report_path = root / "data" / "qa_smoke_report.json"
    out_path = root / "data" / "qa_smoke_summary.md"

    data = json.loads(report_path.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    passed = sum(1 for c in cases if c.get("pass"))
    failed = [c for c in cases if not c.get("pass")]

    lines = [
        "# Receipt Ledger QA Smoke Summary",
        "",
        f"- suite: {data.get('suite')}",
        f"- overall: {'PASS' if data.get('all_pass') else 'FAIL'}",
        f"- passed: {passed}",
        f"- failed: {len(failed)}",
        "",
    ]

    if failed:
        lines.extend([
            "## Failed Cases",
            "",
            "| case | error |",
            "|---|---|",
        ])
        for c in failed:
            err = (c.get("error") or "").replace("\n", " ")
            lines.append(f"| {c.get('label')} | {err} |")
        lines.append("")

    lines.extend([
        "## All Cases",
        "",
        "| case | pass | note |",
        "|---|:---:|---|",
    ])

    for c in cases:
        note = (c.get("error") or "").replace("\n", " ")
        lines.append(f"| {c.get('label')} | {'✅' if c.get('pass') else '❌'} | {note} |")

    text = "\n".join(lines) + "\n"
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"saved -> {out_path}")


if __name__ == "__main__":
    main()
