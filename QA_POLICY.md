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
- `status` (`open`/`done`)
- `priority`, `source_suite`, `task`, `owner`, `due`, `verify`
- 메타: `created_at`, `source_suite`(report 레벨)
- 히스토리: `qa_action_history.jsonl`에 `id/status/priority/source_suite` 누적
- 반복 요약: `qa_action_recurrence.md`에서 id별 출현 횟수 확인
- smoke 반복 승격 기준: `smokeEscalateThreshold` (기본 3, workflow_dispatch로 조정 가능)
- 정책 스냅샷: `qa_policy_snapshot.json`에 실행 시점 정책값/결과 저장
- 스냅샷 이력: `qa_policy_snapshot_history.jsonl` 누적
- 스냅샷 diff: `qa_policy_snapshot_diff.md`로 직전 실행과 변경점 비교
  - `changed_count`와 `Key Changes` 섹션으로 핵심 변경점 빠르게 확인
  - Key Changes는 `benchmark/smoke/action_policy` 그룹으로 정리
  - CI 입력 `failOnPolicyChange=true`면 `changed_count>0`에서 실패 처리 가능
- workflow_dispatch input:
  - `maxAllowedFailures` (default: 0)
  - `failOnUnassignedHigh` (default: false)

정책 판정:
- policy PASS 조건 = `failed_count <= max_failures`

## 3) 통합 판정

`qa_integrated_summary.md` 기준:
- status(policy) = benchmark PASS AND smoke(policy) PASS
- 운영 기본값: 보수적 모드 (`failOnRegression=true`, `maxAllowedFailures=0`)
