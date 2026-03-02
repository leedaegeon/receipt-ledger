# Receipt Ledger Integrated QA Summary

## Benchmark (D12)

- rows: 5000
- repeats: 1
- overall: PASS

| step | avg(s) | target(s) | pass |
|---|---:|---:|:---:|
| import | 1.0631 | 5.0 | ✅ |
| export_uncategorized | 0.0513 | 1.0 | ✅ |
| apply_feedback | 0.1153 | 1.0 | ✅ |
| monthly_report | 0.0728 | 1.0 | ✅ |

## Exceptions/Smoke (D13)

- suite: benchmark
- overall: PASS
- cases: 1 (failed: 0)

### All Cases

| case | pass |
|---|:---:|
| benchmark-5000 | ✅ |
