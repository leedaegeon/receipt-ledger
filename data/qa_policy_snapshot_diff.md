# QA Policy Snapshot Diff

- prev: 2026-03-03T15:02:14.919454+00:00
- curr: 2026-03-03T15:07:21.070401+00:00
- changed_count: 1

## Key Changes

### benchmark
- `benchmark.pipeline_total_avg_sec`: `1.1346` -> `1.1114`

| key | prev | curr | changed |
|---|---|---|:---:|
| benchmark.all_pass | True | True |  |
| benchmark.pipeline_total_avg_sec | 1.1346 | 1.1114 | ✅ |
| benchmark.fixed_cost_options.amount_tolerance_ratio | 0.15 | 0.15 |  |
| benchmark.fixed_cost_options.amount_tolerance_abs | 10000 | 10000 |  |
| benchmark.fixed_cost_options.min_months | 3 | 3 |  |
| benchmark.fixed_cost_options.min_average_amount | 30000 | 30000 |  |
| smoke.failed_count | None | None |  |
| smoke.max_failures | None | None |  |
| action_policy.smoke_escalate_threshold | 3 | 3 |  |
| action_policy.escalated_high_count | 0 | 0 |  |
