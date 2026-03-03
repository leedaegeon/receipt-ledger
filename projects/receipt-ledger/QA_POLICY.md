# Receipt Ledger QA Policy

D12/D13 자동검증에서 사용하는 실패 기준을 명시한다.

## 1) Benchmark 정책 (D12)

기본 목표(5,000행):
- import avg <= 5.0s
- export_uncategorized avg <= 1.0s
- apply_feedback avg <= 1.0s
- monthly_report avg <= 1.0s

회귀 정책:
- 최근 실행 대비 step avg 증가폭(Δ)이 `regressionThresholdSec` 초과 시 회귀 경고
- `failOnRegression=true`이면 CI 실패 처리

관련 옵션:
- `benchmark_pipeline.py --fail-on-target`
- `benchmark_summary.py --regression-threshold-sec <sec> --fail-on-regression`
- workflow_dispatch input:
  - `regressionThresholdSec` (default: 0.2)
  - `failOnRegression` (default: true)

## 2) Smoke/Exception 정책 (D13)

기본 원칙:
- fixture 기반 예외 케이스를 실행하고 메시지/종료코드 검증
- 실패 케이스 수가 허용치 초과 시 CI 실패

관련 옵션:
- `qa_smoke.py --max-failures <n> --report-json <path>`
- `check_action_item_ownership.py --fail-on-unassigned-high`

Action Item 포맷:
- `id` (예: `BENCH-import`, `SMOKE-invalid-pdf`)
- `priority`, `source_suite`, `task`, `owner`, `due`, `verify`
- 메타: `created_at`, `source_suite`(report 레벨)
- workflow_dispatch input:
  - `maxAllowedFailures` (default: 0)
  - `failOnUnassignedHigh` (default: false)

정책 판정:
- policy PASS 조건 = `failed_count <= max_failures`

## 3) 통합 판정

`qa_integrated_summary.md` 기준:
- status(policy) = benchmark PASS AND smoke(policy) PASS
- 운영 기본값: 보수적 모드 (`failOnRegression=true`, `maxAllowedFailures=0`)
