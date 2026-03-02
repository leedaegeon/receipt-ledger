# REPORT_SCHEMA.md (v1)

## 1) normalized.json
거래 정규화 결과 배열.

```json
[
  {
    "occurred_at": "2026-02-24 21:54:31",
    "amount": 3500,
    "direction": "expense",
    "merchant_name": "씨유인덕원점",
    "normalized_merchant_name": "씨유인덕원점",
    "category": "편의점",
    "memo": null,
    "account_label": "토스뱅크",
    "source_row_hash": "...",
    "fixed_cost_candidate": false,
    "fixed_cost_confidence": null
  }
]
```

## 2) invalid.json
오류행 리포트.

```json
{
  "meta": {
    "source_file": "...pdf",
    "month": "2026-02",
    "account": "토스뱅크",
    "count": 3
  },
  "rows": [
    { "line": 122, "reason": "unmatched_transaction_line", "raw": "..." }
  ]
}
```

## 3) report.json
월간 리포트 표준.

```json
{
  "meta": {
    "schema_version": "v1",
    "month": "2026-02",
    "account": "토스뱅크",
    "currency": "KRW"
  },
  "summary": {
    "total_income": 8034868,
    "total_expense": 6019934,
    "net_cashflow": 2014934,
    "expense_count": 71,
    "income_count": 84
  },
  "category_breakdown": [
    { "category": "쇼핑", "amount": 2173912, "ratio": 36.11 }
  ],
  "top_expenses": [],
  "fixed_candidates": [
    {
      "merchant_name": "행복월세",
      "normalized_merchant_name": "행복월세",
      "category": "주거/고정비",
      "month_count": 3,
      "span_months": 3,
      "coverage": 1.0,
      "average_amount": 551667,
      "min_amount": 550000,
      "max_amount": 555000,
      "max_variation_ratio": 0.006,
      "confidence": 0.996,
      "last_paid_at": "2026-03-05 09:00:00",
      "monthly_amounts": [
        { "month": "2026-01", "amount": 550000 }
      ]
    }
  ],
  "uncategorized": {
    "count": 12,
    "items": []
  }
}
```

## 4) reprocess 입력 스키마(editable)
`reprocess_invalid.py` 입력용 수동 수정 포맷.

```json
{
  "rows": [
    {
      "selected": true,
      "date_text": "2026-02-10 12:00:00",
      "direction_text": "출금",
      "amount_text": "-12000",
      "merchant_text": "점포명"
    }
  ]
}
```
