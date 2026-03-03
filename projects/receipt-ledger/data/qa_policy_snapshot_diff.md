# QA Policy Snapshot Diff

- prev: 2026-03-03T00:42:00.684910+00:00
- curr: 2026-03-03T14:02:01.693318+00:00
- changed_count: 5

## Key Changes

### benchmark
- `benchmark.pipeline_total_avg_sec`: `None` -> `1.1582`
- `benchmark.fixed_cost_options.amount_tolerance_ratio`: `None` -> `0.15`
- `benchmark.fixed_cost_options.amount_tolerance_abs`: `None` -> `10000`
- `benchmark.fixed_cost_options.min_months`: `None` -> `3`
- `benchmark.fixed_cost_options.min_average_amount`: `None` -> `30000`

| key | prev | curr | changed |
|---|---|---|:---:|
| benchmark.all_pass | True | True |  |
| benchmark.pipeline_total_avg_sec | None | 1.1582 | ✅ |
| benchmark.fixed_cost_options.amount_tolerance_ratio | None | 0.15 | ✅ |
| benchmark.fixed_cost_options.amount_tolerance_abs | None | 10000 | ✅ |
| benchmark.fixed_cost_options.min_months | None | 3 | ✅ |
| benchmark.fixed_cost_options.min_average_amount | None | 30000 | ✅ |
| smoke.failed_count | None | None |  |
| smoke.max_failures | None | None |  |
| action_policy.smoke_escalate_threshold | 3 | 3 |  |
| action_policy.escalated_high_count | 0 | 0 |  |
