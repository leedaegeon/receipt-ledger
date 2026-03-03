# Receipt Ledger Integrated QA Summary

- status(policy): ✅ PASS
- benchmark: ✅ PASS
- smoke(policy): ✅ PASS (failed=0, allowed=0)
- smoke(reported): ✅ PASS

## Benchmark (D12)

- rows: 5000
- repeats: 1
- overall: PASS
- pipeline_total_avg_sec: 1.2341

| step | avg(s) | target(s) | pass |
|---|---:|---:|:---:|
| import | 1.0562 | 5.0 | ✅ |
| export_uncategorized | 0.0299 | 1.0 | ✅ |
| apply_feedback | 0.0684 | 1.0 | ✅ |
| monthly_report | 0.0796 | 1.0 | ✅ |

## Exceptions/Smoke (D13)

- suite: all
- overall(reported): PASS
- policy: PASS (failed=0, allowed=0)
- smoke_escalate_threshold: 3
- cases: 15

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
| empty-feedback | ✅ |
| encoding-csv | ✅ |
| empty-csv | ✅ |
| bad-quoted-csv | ✅ |
| bad-nul-csv | ✅ |
| invalid-pdf | ✅ |
| empty-pdf | ✅ |
| unsupported-extension | ✅ |
