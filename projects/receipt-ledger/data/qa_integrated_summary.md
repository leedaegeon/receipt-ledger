# Receipt Ledger Integrated QA Summary

- status(policy): ✅ PASS
- benchmark: ✅ PASS
- smoke(policy): ✅ PASS (failed=0, allowed=0)
- smoke(reported): ✅ PASS

## Benchmark (D12)

- rows: 5000
- repeats: 1
- overall: PASS
- pipeline_total_avg_sec: 1.1455

| step | avg(s) | target(s) | pass |
|---|---:|---:|:---:|
| import | 0.973 | 5.0 | ✅ |
| export_uncategorized | 0.0303 | 1.0 | ✅ |
| apply_feedback | 0.0677 | 1.0 | ✅ |
| monthly_report | 0.0745 | 1.0 | ✅ |

## Exceptions/Smoke (D13)

- suite: all
- overall(reported): PASS
- policy: PASS (failed=0, allowed=0)
- smoke_escalate_threshold: 3
- cases: 14

### All Cases

| case | pass |
|---|:---:|
| benchmark-5000 | ✅ |
| empty-json | ✅ |
| broken-json | ✅ |
| missing-header | ✅ |
| invalid-option | ✅ |
| invalid-report-option | ✅ |
| bad-feedback | ✅ |
| encoding-csv | ✅ |
| empty-csv | ✅ |
| bad-quoted-csv | ✅ |
| bad-nul-csv | ✅ |
| invalid-pdf | ✅ |
| empty-pdf | ✅ |
| unsupported-extension | ✅ |
