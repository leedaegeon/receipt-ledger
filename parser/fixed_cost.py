from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, is_dataclass
from datetime import datetime
from statistics import mean
from typing import Any

DEFAULT_FIXED_COST_OPTIONS: dict[str, float | int] = {
    "amount_tolerance_ratio": 0.15,
    "amount_tolerance_abs": 10000,
    "min_months": 2,
    "min_average_amount": 30000,
}


def _to_dict(item: Any) -> dict:
    if isinstance(item, dict):
        return item
    if is_dataclass(item):
        return asdict(item)
    return dict(item)


def _parse_occurred_at(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    text = str(value)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text, fmt)
            if fmt == "%Y-%m-%d":
                return dt.replace(hour=0, minute=0, second=0)
            return dt
        except ValueError:
            continue
    raise ValueError(f"Unsupported occurred_at format: {value}")


def _month_index(dt: datetime) -> int:
    return dt.year * 12 + dt.month


def normalize_fixed_cost_options(overrides: dict | None = None) -> dict[str, float | int]:
    opts = dict(DEFAULT_FIXED_COST_OPTIONS)
    if overrides:
        opts.update(overrides)

    if opts["amount_tolerance_ratio"] < 0:
        raise ValueError("--fixed-cost-amount-tolerance-ratio 는 0 이상이어야 합니다.")
    if opts["amount_tolerance_abs"] < 0:
        raise ValueError("--fixed-cost-amount-tolerance-abs 는 0 이상이어야 합니다.")
    if int(opts["min_months"]) < 1:
        raise ValueError("--fixed-cost-min-months 는 1 이상이어야 합니다.")
    if int(opts["min_average_amount"]) < 0:
        raise ValueError("--fixed-cost-min-average-amount 는 0 이상이어야 합니다.")

    opts["min_months"] = int(opts["min_months"])
    opts["amount_tolerance_abs"] = int(opts["amount_tolerance_abs"])
    opts["amount_tolerance_ratio"] = float(opts["amount_tolerance_ratio"])
    opts["min_average_amount"] = int(opts["min_average_amount"])
    return opts


def detect_fixed_cost_candidates(
    items: list[Any],
    amount_tolerance_ratio: float = 0.15,
    amount_tolerance_abs: int = 10000,
    min_months: int = 2,
    min_average_amount: int = 30000,
) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for item in items:
        row = _to_dict(item)
        if row.get("direction") != "expense":
            continue
        merchant = row.get("normalized_merchant_name") or row.get("merchant_name") or ""
        category = row.get("category") or "미분류"
        if not merchant:
            continue
        grouped[(merchant, category)].append(row)

    candidates: list[dict] = []
    for (merchant, category), txs in grouped.items():
        month_totals: dict[str, int] = defaultdict(int)
        month_dates: dict[str, datetime] = {}

        for tx in txs:
            occurred_at = _parse_occurred_at(tx.get("occurred_at"))
            month_key = occurred_at.strftime("%Y-%m")
            month_totals[month_key] += int(tx.get("amount") or 0)
            month_dates[month_key] = max(month_dates.get(month_key, occurred_at), occurred_at)

        if len(month_totals) < min_months:
            continue

        month_keys = sorted(month_totals.keys())
        first_month = datetime.strptime(month_keys[0] + "-01", "%Y-%m-%d")
        last_month = datetime.strptime(month_keys[-1] + "-01", "%Y-%m-%d")
        span_months = (_month_index(last_month) - _month_index(first_month)) + 1
        month_coverage = len(month_totals) / span_months if span_months > 0 else 0

        monthly_amounts = list(month_totals.values())
        avg_amount = mean(monthly_amounts)
        if avg_amount < min_average_amount:
            continue

        max_abs_delta = max(abs(v - avg_amount) for v in monthly_amounts)
        max_ratio_delta = max_abs_delta / avg_amount
        amount_stable = (max_ratio_delta <= amount_tolerance_ratio) or (max_abs_delta <= amount_tolerance_abs)

        if not amount_stable:
            continue
        if month_coverage < 0.6:
            continue

        stability_score = max(0.0, 1.0 - max_ratio_delta)
        coverage_score = min(1.0, month_coverage)
        confidence = round((stability_score * 0.6) + (coverage_score * 0.4), 3)

        candidates.append(
            {
                "merchant_name": txs[0].get("merchant_name"),
                "normalized_merchant_name": merchant,
                "category": category,
                "month_count": len(month_totals),
                "span_months": span_months,
                "coverage": round(month_coverage, 3),
                "average_amount": round(avg_amount),
                "min_amount": min(monthly_amounts),
                "max_amount": max(monthly_amounts),
                "max_variation_ratio": round(max_ratio_delta, 3),
                "confidence": confidence,
                "last_paid_at": max(month_dates.values()).strftime("%Y-%m-%d %H:%M:%S"),
                "monthly_amounts": [{"month": m, "amount": month_totals[m]} for m in month_keys],
            }
        )

    return sorted(candidates, key=lambda x: (-x["confidence"], -x["average_amount"]))


def annotate_fixed_cost_candidates(transactions: list[Any], candidates: list[dict]) -> None:
    candidate_keys = {(c["normalized_merchant_name"], c["category"]): c for c in candidates}

    for tx in transactions:
        merchant = tx.normalized_merchant_name
        category = tx.category or "미분류"
        c = candidate_keys.get((merchant, category))
        tx.fixed_cost_candidate = bool(c)
        tx.fixed_cost_confidence = c.get("confidence") if c else None
