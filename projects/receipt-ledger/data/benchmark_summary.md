# Receipt Ledger Benchmark Summary

- rows: 5000
- repeats: 1
- overall: PASS

| step | avg(s) | target(s) | pass |
|---|---:|---:|:---:|
| import | 1.0582 | 5.0 | ✅ |
| export_uncategorized | 0.0318 | 1.0 | ✅ |
| apply_feedback | 0.0995 | 1.0 | ✅ |
| monthly_report | 0.0975 | 1.0 | ✅ |

## Recent Runs (latest 5)

| ts(UTC) | import avg(s) | Δimport | export avg(s) | Δexport | apply avg(s) | Δapply | report avg(s) | Δreport | all_pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 2026-03-02T14:32:17.639002+00:00 | 1.0631 | - | 0.0513 | - | 0.1153 | - | 0.0728 | - | ✅ |
| 2026-03-02T14:36:54.753338+00:00 | 1.0631 | 0.0 | 0.0513 | 0.0 | 0.1153 | 0.0 | 0.0728 | 0.0 | ✅ |
| 2026-03-03T12:59:28.037499+00:00 | 1.0582 | -0.0049 | 0.0318 | -0.0195 | 0.0995 | -0.0158 | 0.0975 | +0.0247 | ✅ |
