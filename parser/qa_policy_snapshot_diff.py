import json
from pathlib import Path


KEYS = [
    ("benchmark", "all_pass"),
    ("smoke", "failed_count"),
    ("smoke", "max_failures"),
    ("action_policy", "smoke_escalate_threshold"),
    ("action_policy", "escalated_high_count"),
]


def _get(d, path):
    cur = d
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def main():
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


if __name__ == "__main__":
    main()
