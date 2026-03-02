# Receipt Ledger Integrated QA Summary

## Benchmark (D12)

- rows: 5000
- repeats: 1
- overall: PASS

| step | avg(s) | target(s) | pass |
|---|---:|---:|:---:|
| import | 1.1537 | 5.0 | ✅ |
| export_uncategorized | 0.0533 | 1.0 | ✅ |
| apply_feedback | 0.1094 | 1.0 | ✅ |
| monthly_report | 0.0801 | 1.0 | ✅ |

## Exceptions/Smoke (D13)

- suite: all
- overall: PASS
- cases: 8 (failed: 0)

### All Cases

| case | pass |
|---|:---:|
| benchmark-5000 | ✅ |
| empty-json | ✅ |
| broken-json | ✅ |
| missing-header | ✅ |
| invalid-option | ✅ |
| bad-feedback | ✅ |
| encoding-csv | ✅ |
| invalid-pdf | ✅ |
