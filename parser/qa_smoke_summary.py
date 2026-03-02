import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    report_path = root / "data" / "qa_smoke_report.json"
    out_path = root / "data" / "qa_smoke_summary.md"

    data = json.loads(report_path.read_text(encoding="utf-8"))
    lines = [
        "# Receipt Ledger QA Smoke Summary",
        "",
        f"- suite: {data.get('suite')}",
        f"- overall: {'PASS' if data.get('all_pass') else 'FAIL'}",
        "",
        "| case | pass | note |",
        "|---|:---:|---|",
    ]

    for c in data.get("cases", []):
        note = (c.get("error") or "").replace("\n", " ")
        lines.append(f"| {c.get('label')} | {'✅' if c.get('pass') else '❌'} | {note} |")

    text = "\n".join(lines) + "\n"
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"saved -> {out_path}")


if __name__ == "__main__":
    main()
