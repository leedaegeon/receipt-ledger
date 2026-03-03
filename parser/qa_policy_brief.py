import argparse
import json
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path


def parse_args():
    ap = argparse.ArgumentParser(description="Build QA policy brief")
    ap.add_argument("--smoke-escalate-threshold", type=int, default=3)
    ap.add_argument("--default-owner", default="data-pipeline")
    ap.add_argument("--default-due-days", type=int, default=3)
    return ap.parse_args()


def _default_due(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()


def _owner_for_suite(suite: str, fallback: str) -> str:
    if suite == "benchmark":
        return "perf-owner"
    if suite in ("exceptions", "all"):
        return "parser-owner"
    return fallback


def main():
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    integrated = root / "data" / "qa_integrated_summary.md"
    bench = root / "data" / "benchmark_pipeline_result.json"
    smoke = root / "data" / "qa_smoke_report.json"
    out = root / "data" / "qa_policy_brief.md"
    out_json = root / "data" / "qa_action_items.json"
    hist = root / "data" / "qa_action_history.jsonl"
    sanity = root / "data" / "qa_policy_sanity_checklist.md"

    recur = Counter()
    if hist.exists():
        for line in hist.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("id"):
                recur[row["id"]] += 1

    status_line = "- status(policy): (unknown)"
    if integrated.exists():
        for line in integrated.read_text(encoding="utf-8").splitlines():
            if line.startswith("- status(policy):"):
                status_line = line
                break

    lines = ["# QA Policy Brief", "", status_line, ""]
    action_items = []
    escalated_high = []

    sanity_status = "unknown"
    if sanity.exists():
        txt = sanity.read_text(encoding="utf-8")
        if "- status: PASS" in txt:
            sanity_status = "PASS"
        elif "- status: FAIL" in txt:
            sanity_status = "FAIL"

    lines.append("## Policy Sanity")
    lines.append(f"- qa_policy_sanity_checklist: {sanity_status}")
    if sanity_status == "FAIL":
        aid = "POLICY-SANITY"
        occ = recur.get(aid, 0)
        lines.append("- 🔴 [HIGH] 정책 문서/워크플로우 기본값 불일치")
        action_items.append({
            "id": aid,
            "status": "open",
            "priority": "HIGH",
            "source_suite": "policy",
            "task": "qa_policy_sanity_checklist.md FAIL 항목 정리 및 정책 기준/워크플로우 기본값 동기화",
            "owner": args.default_owner,
            "due": _default_due(args.default_due_days),
            "verify": "python3 qa_policy_sanity.py",
            "occurrences": occ,
        })
    lines.append("")

    if bench.exists():
        b = json.loads(bench.read_text(encoding="utf-8"))
        failing_steps = [
            k for k, v in b.get("verdict", {}).get("steps", {}).items() if not v.get("pass")
        ]
        lines.append("## Benchmark Fail Steps")
        if failing_steps:
            for s in failing_steps:
                lines.append(f"- 🔴 [HIGH] {s}")
                aid = f"BENCH-{s}"
                occ = recur.get(aid, 0)
                action_items.append({
                    "id": aid,
                    "status": "open",
                    "priority": "HIGH",
                    "source_suite": "benchmark",
                    "task": f"benchmark step `{s}` 성능 목표 미달 원인 분석/최적화",
                    "owner": _owner_for_suite("benchmark", args.default_owner),
                    "due": _default_due(args.default_due_days),
                    "verify": "python3 benchmark_pipeline.py --rows 5000 --repeats 3 --fail-on-target --out ../data/benchmark_pipeline_result.json",
                    "occurrences": occ,
                })
        else:
            lines.append("- 없음")
        lines.append("")

    smoke_suite = "unknown"
    if smoke.exists():
        s = json.loads(smoke.read_text(encoding="utf-8"))
        smoke_suite = s.get("suite") or "unknown"
        failed_cases = [c for c in s.get("cases", []) if not c.get("pass")]
        lines.append("## Smoke Failed Cases")
        if failed_cases:
            for c in failed_cases:
                label = c.get('label')
                err = (c.get('error') or '').replace(chr(10), ' ')
                lines.append(f"- 🟠 [MEDIUM] {label}: {err}")
                aid = f"SMOKE-{label}"
                occ = recur.get(aid, 0)
                pr = "HIGH" if occ >= args.smoke_escalate_threshold else "MEDIUM"
                if pr == "HIGH":
                    escalated_high.append((aid, occ))
                action_items.append({
                    "id": aid,
                    "status": "open",
                    "priority": pr,
                    "source_suite": smoke_suite,
                    "task": f"smoke case `{label}` 실패 수정 및 fixture/메시지 재검증",
                    "owner": _owner_for_suite(smoke_suite, args.default_owner),
                    "due": _default_due(args.default_due_days),
                    "verify": "python3 qa_smoke.py --suite exceptions --max-failures 0 --report-json ../data/qa_smoke_report.json",
                    "occurrences": occ,
                })
        else:
            lines.append("- 없음")

    if escalated_high:
        lines.append("")
        lines.append("## Escalated HIGH (recurrence)")
        for aid, occ in escalated_high:
            lines.append(f"- 🔺 {aid} (occurrences={occ}, threshold={args.smoke_escalate_threshold})")

    lines.append("")
    lines.append("## Action Items")
    if action_items:
        for idx, item in enumerate(action_items, start=1):
            lines.append(f"### {idx}. [{item['priority']}] {item['task']}")
            lines.append(f"- id: {item['id']}")
            lines.append(f"- status: {item['status']}")
            lines.append(f"- occurrences: {item.get('occurrences', 0)}")
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
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_suite": smoke_suite,
                "smoke_escalate_threshold": args.smoke_escalate_threshold,
                "sanity_status": sanity_status,
                "escalated_high": [
                    {"id": aid, "occurrences": occ}
                    for aid, occ in escalated_high
                ],
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
