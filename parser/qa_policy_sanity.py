import re
from pathlib import Path


CHECKLIST_HINTS = {
    "workflow": "- [ ] .github/workflows/receipt-ledger-qa.yml의 workflow_dispatch 기본값을 QA_POLICY.md와 일치시켰는지 확인",
    "policy": "- [ ] projects/receipt-ledger/QA_POLICY.md에 누락된 정책 키/설명을 추가했는지 확인",
    "sync": "- [ ] parser/qa_policy_sanity.py 규칙과 문서/워크플로우를 동시에 업데이트했는지 확인",
}


def _extract_workflow_defaults(workflow_text: str) -> dict[str, str]:
    keys = [
        "regressionThresholdSec",
        "failOnRegression",
        "maxAllowedFailures",
        "failOnUnassignedHigh",
        "smokeEscalateThreshold",
        "failOnPolicyChange",
        "policyChangeFailMin",
    ]
    out: dict[str, str] = {}
    for key in keys:
        m = re.search(rf"\n\s*{re.escape(key)}:\n(?:\s+.*\n)*?\s+default:\s*'([^']+)'", workflow_text)
        if m:
            out[key] = m.group(1)
    return out


def _expect_contains(policy_text: str, token: str, label: str, errors: list[str]):
    if token not in policy_text:
        errors.append(f"QA_POLICY.md 누락: {label} ({token})")


def _hint_for_error(err: str) -> tuple[str, str]:
    if err.startswith("workflow default mismatch:"):
        return (
            "hint: .github/workflows/receipt-ledger-qa.yml 의 workflow_dispatch.inputs 기본값을 QA_POLICY.md와 맞추세요.",
            CHECKLIST_HINTS["workflow"],
        )
    if "QA_POLICY.md 누락" in err:
        return (
            "hint: projects/receipt-ledger/QA_POLICY.md에 해당 정책 키/설명을 추가하세요.",
            CHECKLIST_HINTS["policy"],
        )
    return (
        "hint: parser/qa_policy_sanity.py 규칙과 문서/워크플로우를 동기화하세요.",
        CHECKLIST_HINTS["sync"],
    )


def _write_checklist(path: Path, ok: bool, entries: list[str]):
    lines = ["# QA Policy Sanity Checklist", ""]
    lines.append(f"- status: {'PASS' if ok else 'FAIL'}")
    lines.append("")
    if entries:
        lines.extend(entries)
    else:
        lines.append("- [x] 정책/워크플로우 기본값 정합성 확인 완료")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    root = Path(__file__).resolve().parents[1]
    workflow = root.parents[1] / ".github" / "workflows" / "receipt-ledger-qa.yml"
    policy = root / "QA_POLICY.md"
    checklist_out = root / "data" / "qa_policy_sanity_checklist.md"

    if not workflow.exists():
        raise SystemExit(f"workflow not found: {workflow}")
    if not policy.exists():
        raise SystemExit(f"policy not found: {policy}")

    wf_text = workflow.read_text(encoding="utf-8")
    policy_text = policy.read_text(encoding="utf-8")

    defaults = _extract_workflow_defaults(wf_text)
    required_defaults = {
        "regressionThresholdSec": "0.2",
        "failOnRegression": "true",
        "maxAllowedFailures": "0",
        "failOnUnassignedHigh": "false",
        "smokeEscalateThreshold": "3",
        "failOnPolicyChange": "false",
        "policyChangeFailMin": "1",
    }

    errors: list[str] = []
    for k, expected in required_defaults.items():
        got = defaults.get(k)
        if got != expected:
            errors.append(f"workflow default mismatch: {k} expected={expected} got={got}")

    _expect_contains(policy_text, "failOnPolicyChange", "policy change gate input", errors)
    _expect_contains(policy_text, "policyChangeFailMin", "policy change threshold input", errors)
    _expect_contains(policy_text, "fixed_cost_options", "fixed-cost option tracking", errors)
    _expect_contains(policy_text, "pipeline_total_avg_sec", "pipeline total metric tracking", errors)

    checklist_items: list[str] = []
    if errors:
        print("QA_POLICY_SANITY_FAIL")
        for e in errors:
            print(f"- {e}")
            hint, checklist = _hint_for_error(e)
            print(f"  {hint}")
            if checklist not in checklist_items:
                checklist_items.append(checklist)
        _write_checklist(checklist_out, ok=False, entries=checklist_items)
        print(f"saved -> {checklist_out}")
        raise SystemExit(1)

    print("QA_POLICY_SANITY_OK")
    for k in required_defaults:
        print(f"- {k}={defaults[k]}")
    _write_checklist(checklist_out, ok=True, entries=[])
    print(f"saved -> {checklist_out}")


if __name__ == "__main__":
    main()
