import re
from pathlib import Path


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


def main():
    root = Path(__file__).resolve().parents[1]
    workflow = root.parents[1] / ".github" / "workflows" / "receipt-ledger-qa.yml"
    policy = root / "QA_POLICY.md"

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

    if errors:
        print("QA_POLICY_SANITY_FAIL")
        for e in errors:
            print(f"- {e}")
        raise SystemExit(1)

    print("QA_POLICY_SANITY_OK")
    for k in required_defaults:
        print(f"- {k}={defaults[k]}")


if __name__ == "__main__":
    main()
