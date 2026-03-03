# Receipt Ledger Integrated QA Summary

- status(policy): ✅ PASS
- benchmark: ✅ PASS
- smoke(policy): ✅ PASS (failed=0, allowed=0)
- smoke(reported): ✅ PASS

## Benchmark (D12)

- rows: 5000
- repeats: 1
- overall: PASS

| step | avg(s) | target(s) | pass |
|---|---:|---:|:---:|
| import | 0.955 | 5.0 | ✅ |
| export_uncategorized | 0.0295 | 1.0 | ✅ |
| apply_feedback | 0.0633 | 1.0 | ✅ |
| monthly_report | 0.0663 | 1.0 | ✅ |

## Exceptions/Smoke (D13)

- suite: all
- overall(reported): PASS
- policy: PASS (failed=0, allowed=0)
- cases: 8

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
