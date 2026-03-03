import argparse
import json
from pathlib import Path


KEYS = [
    ("benchmark", "all_pass"),
    ("benchmark", "pipeline_total_avg_sec"),
    ("benchmark", "fixed_cost_options", "amount_tolerance_ratio"),
    ("benchmark", "fixed_cost_options", "amount_tolerance_abs"),
    ("benchmark", "fixed_cost_options", "min_months"),
    ("benchmark", "fixed_cost_options", "min_average_amount"),
    ("smoke", "failed_count"),
    ("smoke", "max_failures"),
    ("action_policy", "smoke_escalate_threshold"),
    ("action_policy", "escalated_high_count"),
]


def parse_args():
    ap = argparse.ArgumentParser(description="Build policy snapshot diff and optionally fail on changes")
    ap.add_argument("--fail-on-policy-change", action="store_true")
    ap.add_argument("--policy-change-fail-min", type=int, default=1)
    return ap.parse_args()


def _get(d, path):
    cur = d
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def main():
    args = parse_args()
    if args.policy_change_fail_min < 1:
        raise SystemExit("policy diff 옵션 오류: --policy-change-fail-min 은 1 이상이어야 합니다.")

    root = Path(__file__).resolve().parents[1]
    hist = root / "data" / "qa_policy_snapshot_history.jsonl"
    out = root / "data" / "qa_policy_snapshot_diff.md"

    if not hist.exists():
        out.write_text("# QA Policy Snapshot Diff\n\n- history not found\n", encoding="utf-8")
        print(f"saved -> {out}")
        return

    rows = []
    for line in hist.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if len(rows) < 2:
        out.write_text("# QA Policy Snapshot Diff\n\n- not enough history (need >=2)\n", encoding="utf-8")
        print(f"saved -> {out}")
        return

    prev, cur = rows[-2], rows[-1]

    changes = []
    for path in KEYS:
        k = ".".join(path)
        pv = _get(prev, path)
        cv = _get(cur, path)
        if pv != cv:
            changes.append((k, pv, cv))

    lines = [
        "# QA Policy Snapshot Diff",
        "",
        f"- prev: {prev.get('created_at')}",
        f"- curr: {cur.get('created_at')}",
        f"- changed_count: {len(changes)}",
        "",
    ]

    if changes:
        groups = {"benchmark": [], "smoke": [], "action_policy": [], "other": []}
        for k, pv, cv in changes:
            head = k.split(".", 1)[0]
            groups[head if head in groups else "other"].append((k, pv, cv))

        lines.extend(["## Key Changes", ""])
        for g in ("benchmark", "smoke", "action_policy", "other"):
            if not groups[g]:
                continue
            lines.append(f"### {g}")
            for k, pv, cv in groups[g]:
                lines.append(f"- `{k}`: `{pv}` -> `{cv}`")
            lines.append("")

    lines.extend([
        "| key | prev | curr | changed |",
        "|---|---|---|:---:|",
    ])

    for path in KEYS:
        k = ".".join(path)
        pv = _get(prev, path)
        cv = _get(cur, path)
        changed = pv != cv
        lines.append(f"| {k} | {pv} | {cv} | {'✅' if changed else ''} |")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved -> {out}")

    if args.fail_on_policy_change and len(changes) >= args.policy_change_fail_min:
        raise SystemExit(
            f"policy snapshot changed: changed_count={len(changes)} (threshold={args.policy_change_fail_min})"
        )


if __name__ == "__main__":
    main()
