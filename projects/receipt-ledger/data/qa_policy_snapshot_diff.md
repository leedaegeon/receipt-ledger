# QA Policy Snapshot Diff

- prev: 2026-03-03T14:07:14.555638+00:00
- curr: 2026-03-03T14:12:42.691344+00:00
- changed_count: 1

## Key Changes

### benchmark
- `benchmark.pipeline_total_avg_sec`: `1.2806` -> `1.2611`

| key | prev | curr | changed |
|---|---|---|:---:|
| benchmark.all_pass | True | True |  |
| benchmark.pipeline_total_avg_sec | 1.2806 | 1.2611 | ✅ |
| benchmark.fixed_cost_options.amount_tolerance_ratio | 0.15 | 0.15 |  |
| benchmark.fixed_cost_options.amount_tolerance_abs | 10000 | 10000 |  |
| benchmark.fixed_cost_options.min_months | 3 | 3 |  |
| benchmark.fixed_cost_options.min_average_amount | 30000 | 30000 |  |
| smoke.failed_count | None | None |  |
| smoke.max_failures | None | None |  |
| action_policy.smoke_escalate_threshold | 3 | 3 |  |
| action_policy.escalated_high_count | 0 | 0 |  |
