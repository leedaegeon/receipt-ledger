import json
from pathlib import Path

from fixed_cost import detect_fixed_cost_candidates
from monthly_report import build_report


def build_sample():
    return [
        {
            "occurred_at": "2026-01-05 09:00:00",
            "amount": 550000,
            "direction": "expense",
            "merchant_name": "행복월세",
            "normalized_merchant_name": "행복월세",
            "category": "주거/고정비",
        },
        {
            "occurred_at": "2026-02-05 09:00:00",
            "amount": 555000,
            "direction": "expense",
            "merchant_name": "행복월세",
            "normalized_merchant_name": "행복월세",
            "category": "주거/고정비",
        },
        {
            "occurred_at": "2026-03-05 09:00:00",
            "amount": 550000,
            "direction": "expense",
            "merchant_name": "행복월세",
            "normalized_merchant_name": "행복월세",
            "category": "주거/고정비",
        },
        {
            "occurred_at": "2026-01-18 12:10:00",
            "amount": 12000,
            "direction": "expense",
            "merchant_name": "점심식사",
            "normalized_merchant_name": "점심식사",
            "category": "식비",
        },
        {
            "occurred_at": "2026-02-09 12:05:00",
            "amount": 18000,
            "direction": "expense",
            "merchant_name": "점심식사",
            "normalized_merchant_name": "점심식사",
            "category": "식비",
        },
        {
            "occurred_at": "2026-03-22 12:50:00",
            "amount": 9000,
            "direction": "expense",
            "merchant_name": "점심식사",
            "normalized_merchant_name": "점심식사",
            "category": "식비",
        },
    ]


def main():
    sample = build_sample()
    candidates = detect_fixed_cost_candidates(sample)
    assert len(candidates) == 1, f"expected 1 candidate, got {len(candidates)}"
    assert candidates[0]["normalized_merchant_name"] == "행복월세"

    report = build_report(sample, month="2026-03", account="샘플")
    assert len(report["fixed_candidates"]) == 1

    out = Path(__file__).resolve().parent.parent / "data" / "sample_fixed_cost.report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print("OK: fixed-cost detection verified")
    print(f"report -> {out}")


if __name__ == "__main__":
    main()
