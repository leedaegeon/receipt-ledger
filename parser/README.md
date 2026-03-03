# TossBank Parser Prototype (Week 1)

> 로컬 실행 + Android 파이프라인 smoke test 통합 문서: [`../LOCAL_RUN_GUIDE.md`](../LOCAL_RUN_GUIDE.md)

## 완료 범위 (D4~D7)
- D4 파서 v1: CSV 기반 거래 파싱
- D5 헤더 매핑: 후보 헤더 자동 탐지 로직
- D6 정규화/분류: 날짜/금액/상호명/카테고리 정규화
- D7 중복 제거: 해시 기반 dedup

## 파일
- `models.py`: 도메인 모델
- `normalize.py`: 날짜/금액/상호명/방향 정규화
- `classifier.py`: 카테고리 룰
- `dedup.py`: 중복 제거
- `tossbank_parser.py`: CSV/PDF 파서 엔트리
- `run_import.py`: 실행 스크립트

## 실행
```bash
cd projects/receipt-ledger/parser
python3 run_import.py ../data/sample_tossbank.csv --month 2026-02 --account 토스뱅크
# 생성: .normalized.json + .invalid.json
```

## PDF 처리
- `pdf-parse`(Node) 기반 텍스트 추출기를 연결했습니다.
- `pdf_extract.js`를 통해 PDF 텍스트를 추출하고, Python 파서가 거래행을 정규식으로 파싱합니다.

### 의존성 설치 (최초 1회)
```bash
cd projects/receipt-ledger/parser
npm init -y
```

- Node 22+ (프로젝트 기준 고정):
```bash
npm i pdf-parse
```

검증:
```bash
node -e "console.log(process.version, require('pdf-parse/package.json').version)"
node pdf_extract.js ../data/tossbank_statement_2026-03.pdf | head -n 5
```

## 실파일 검증
```bash
python3 run_import.py ../data/tossbank_statement_2026-03.pdf
# parsed=160 -> tossbank_statement_2026-03.normalized.json
```

## 월간 리포트 생성
```bash
python3 monthly_report.py ../data/tossbank_statement_2026-03.normalized.json --month 2026-02 --account 토스뱅크
```

## 실파일 최신 결과
- 파싱 건수: 160
- 미분류 비율(지출 기준): 16.9%

## 미분류 리스트 → 자동학습 플로우
```bash
# 1) 미분류 거래처 템플릿 추출
python3 export_uncategorized.py ../data/tossbank_statement_2026-03.2026-02.normalized.json

# 2) 생성된 *.feedback.template.json에서 category 채우기

# 3) 피드백 반영 + rules.json 자동 누적 + 기존 내역 재분류
python3 apply_feedback.py \
  ../data/tossbank_statement_2026-03.2026-02.normalized.json \
  ../data/tossbank_statement_2026-03.2026-02.normalized.feedback.template.json
```
- `../data/rules.json`에 `normalized_merchant -> category`가 누적 저장됩니다.
- 동일 거래처는 다음 import부터 자동 분류됩니다.

## D11: 고정비 후보 탐지
- `fixed_cost.py`에서 반복 거래(월 고정비) 후보를 추정합니다.
- 판정 기준:
  - 거래처(`normalized_merchant_name`) + 카테고리(`category`) 그룹
  - 월별 합계 기준으로 `min_months(기본 2)` 이상 반복
  - 금액 변동 허용치(`±15%` 또는 `±10,000원`) 이내
  - 기간 대비 월 커버리지 60% 이상
- 파서 단계(`run_import.py`) 결과의 각 거래에는 아래 필드가 포함됩니다.
  - `fixed_cost_candidate`: bool
  - `fixed_cost_confidence`: float | null
- `monthly_report.py`의 `fixed_candidates`는 키워드 하드코딩 대신 위 추정 결과를 사용합니다.

## 최소 검증 스크립트
```bash
cd projects/receipt-ledger/parser
python3 verify_fixed_cost_detection.py
```
- 기대 결과: `OK: fixed-cost detection verified`
- 산출물: `../data/sample_fixed_cost.report.json`

## D12: 성능/예외 처리 검증

### 1) 파이프라인 벤치마크 (5,000행 synthetic)
```bash
cd projects/receipt-ledger/parser
python3 benchmark_pipeline.py --rows 5000 --repeats 3 --fail-on-target --out ../data/benchmark_pipeline_result.json
# 고정비 옵션 오버라이드 포함 측정 예시:
python3 benchmark_pipeline.py --rows 5000 --repeats 3 --fixed-cost-min-months 3 --out ../data/benchmark_pipeline_result.json
# 옵션 검증 확인(실패 기대):
python3 benchmark_pipeline.py --rows 0
python3 benchmark_history.py
python3 benchmark_summary.py --regression-threshold-sec 0.2 --stddev-threshold-sec 0.05 --fail-on-regression
```
- 측정 단계: `run_import.py` → `export_uncategorized.py` → `apply_feedback.py` → `monthly_report.py`
- 기본 목표(평균): import ≤ 5s, export ≤ 1s, apply ≤ 1s, report ≤ 1s
- 기대 출력 예:
  - `- import: PASS avg=...s stddev=...s target<=5.0s`
  - `- pipeline_total_avg_sec: ...s`
  - `- overall: PASS`
- 추가 기대 출력(옵션 검증):
  - `benchmark 옵션 오류: --rows 는 1 이상이어야 합니다.`
- 결과 JSON에는 `fixed_cost_options`(실행 시점 임계값) 필드가 저장됩니다.
- `benchmark_summary.md` 상단에도 동일 옵션이 `fixed_cost_options: ...` 한 줄로 표시됩니다.
- 결과 파일:
  - `../data/benchmark_pipeline_result.json` (`verdict.all_pass` 포함)
  - `../data/benchmark_history.jsonl` (실행 이력 누적)
  - `../data/benchmark_summary.md` (최근 5회 추이 + 이전 실행 대비 Δ + 회귀 경고 + 변동성 경고 포함)
- `qa_policy_brief.py`는 Variance Warning을 읽어 `VAR-*` action item(반복 시 HIGH 승격)을 자동 생성

### 2) 입력 예외 처리 확인
```bash
# 빈 파일
: > ../data/empty.json
python3 monthly_report.py ../data/empty.json

# 손상 JSON
printf '{broken' > ../data/broken.json
python3 export_uncategorized.py ../data/broken.json

# 잘못된 인코딩(예: cp949 파일)
python3 run_import.py ../data/sample_cp949.csv
```
- 기대: 각 스크립트가 `입력 파일 인코딩 오류`, `손상된 JSON 형식`, `필수 헤더 누락`, `CSV 파일이 비어 있습니다`, `CSV 형식 오류`, `PDF 파일이 비어 있습니다`, `PDF 텍스트 추출 실패` 등 명확한 에러 메시지를 출력

### 3) 고정비 탐지 파라미터 튜닝
기본값은 유지하면서 아래 CLI 옵션으로 조정 가능합니다.
- `--fixed-cost-amount-tolerance-ratio` (기본 0.15)
- `--fixed-cost-amount-tolerance-abs` (기본 10000)
- `--fixed-cost-min-months` (기본 2)
- `--fixed-cost-min-average-amount` (기본 30000)

예시:
```bash
python3 run_import.py ../data/tossbank_statement_2026-03.pdf --fixed-cost-min-months 3
python3 monthly_report.py ../data/tossbank_statement_2026-03.normalized.json --fixed-cost-min-months 3
```

## D13 QA 자동화 준비 (Smoke)
```bash
cd projects/receipt-ledger/parser
python3 qa_smoke.py --suite all --max-failures 0 --smoke-escalate-threshold 3 --report-json ../data/qa_smoke_report.json
# 또는 분리 실행
python3 qa_smoke.py --suite benchmark --max-failures 0 --smoke-escalate-threshold 3 --report-json ../data/qa_smoke_report.json
python3 qa_smoke.py --suite exceptions --max-failures 0 --smoke-escalate-threshold 3 --report-json ../data/qa_smoke_report.json
python3 qa_smoke_summary.py
cat ../data/qa_smoke_summary.md
python3 qa_report_merge.py
cat ../data/qa_integrated_summary.md
python3 qa_policy_brief.py --default-owner parser-owner --default-due-days 3
cat ../data/qa_policy_brief.md
cat ../data/qa_action_items.json
# 참고: qa_policy_sanity_checklist.md가 FAIL이면 POLICY-SANITY(HIGH) action item 자동 생성
python3 qa_action_history.py
python3 qa_action_recurrence.py
cat ../data/qa_action_recurrence.md
# recurrence 표에서 source_suites(top)로 반복 이슈 출처(benchmark/exceptions/policy) 확인
# POLICY-SANITY는 policy 출처 반복 횟수가 smokeEscalateThreshold 이상이면 HIGH로 승격
python3 qa_policy_snapshot.py
cat ../data/qa_policy_snapshot.json
python3 qa_policy_snapshot_history.py
python3 qa_policy_snapshot_diff.py
# 정책 변화 fail gate(옵션):
python3 qa_policy_snapshot_diff.py --fail-on-policy-change --policy-change-fail-min 1
python3 qa_policy_sanity.py
# 기대 출력: QA_POLICY_SANITY_OK
# 실패 시 각 오류 아래 hint 라인으로 수정 위치(.github/workflows/... 또는 QA_POLICY.md) 안내
# 추가 산출물: ../data/qa_policy_sanity_checklist.md (수정 체크리스트)
# CI Job Summary의 "QA Policy Sanity" 섹션에 동일 결과 + 체크리스트가 첨부됨
cat ../data/qa_policy_snapshot_diff.md
# changed_count, Key Changes 섹션 확인
# fixed_cost_options.* 및 pipeline_total_avg_sec 변화도 diff 대상에 포함
# CI는 qa_policy_snapshot_diff.py의 --fail-on-policy-change/--policy-change-fail-min 옵션으로 동일 정책 적용
# qa_policy_sanity.py로 QA_POLICY.md와 workflow_dispatch 기본값 정합성 검증
```
- 기대 출력: `QA_SMOKE_OK`
- benchmark smoke는 결과 JSON(`benchmark_pipeline_result.json`)의 `rows=5000`, `fixed_cost_options.min_months=3`도 함께 검증
- summary에는 `passed/failed` 카운트와 실패 케이스 테이블이 포함됨
- integrated summary는 benchmark + exceptions 결과를 한 문서로 통합
- integrated summary 상단에 policy 상태(`failed <= max_failures`)가 표시됨
- integrated summary의 Benchmark 섹션에 `fixed_cost_options`가 표시됨
- `qa_policy_brief.md`는 실패 원인(step/case) + 우선순위(HIGH/MEDIUM) + Action Items(owner/due/verify 템플릿) 요약
- `qa_action_items.json`은 Action Items를 구조화 형태(id/status/source_suite/created_at 포함)로 저장(추적 도구 연계용)
- `qa_action_history.jsonl`은 action item 출현 이력을 누적(반복 이슈 추적용)
- `qa_action_recurrence.md`는 id별 반복 출현 횟수 요약(반복 이슈 승격 기준)
- 포함 검증:
  - 5,000행 벤치마크 목표 통과(`overall: PASS`)
  - `fixtures/empty.json` 빈 JSON 에러 메시지
  - `fixtures/broken.json` 손상 JSON 에러 메시지
  - `fixtures/missing_header.csv` 헤더 누락 에러 메시지
  - `fixtures/cp949.csv` 인코딩 에러 메시지
  - `fixtures/empty.csv` 빈 CSV 에러 메시지
  - `fixtures/bad_quoted.csv` 손상 CSV(따옴표/구분자) 에러 메시지
  - `fixtures/bad_nul.csv` 손상 CSV(NUL 바이트) 에러 메시지
  - `fixtures/invalid.pdf` PDF 추출/형식 에러 메시지
  - `fixtures/empty.pdf` 빈 PDF 에러 메시지
  - `fixtures/unsupported.txt` 지원하지 않는 확장자 에러 메시지
  - 고정비 옵션 유효성 에러 메시지(`run_import.py`, `monthly_report.py` 모두)
  - `fixtures/bad_feedback.json` feedback schema 에러 메시지
  - `fixtures/empty.json` + `apply_feedback.py` 빈 feedback 에러 메시지
  - `fixtures/empty_list.json` + `apply_feedback.py` 빈 normalized 배열 에러 메시지

## D13 QA 자동화 1단계: parser 회귀 테스트 (샘플 데이터 기준)
```bash
cd projects/receipt-ledger/parser
python3 qa_parser_regression.py --report-json ../data/qa_parser_regression_report.json
```
- 기대 출력: `PARSER_REGRESSION_OK`
- 자동 검증 범위:
  1. `run_import.py` 파싱 결과(`parsed=6`, `invalid=0`)
  2. `export_uncategorized.py` 미분류 지출/거래처 개수 및 거래처 목록
  3. `monthly_report.py` 요약 수치(수입/지출/순현금흐름/건수) + 카테고리 금액 + 미분류 건수
- 기본 샘플: `../data/sample_tossbank.csv`
- 디버깅 시 산출물 보존:
```bash
python3 qa_parser_regression.py --keep-artifacts --work-dir ../data/.tmp_regression
```

CI 준비:
```bash
# GitHub Actions: .github/workflows/receipt-ledger-qa.yml
# 수동 실행(workflow_dispatch) 또는 parser 변경 시 자동 실행
# matrix suite: benchmark / exceptions 로 분리 실행
# 각 suite는 qa_smoke_report.json + qa_smoke_summary.md 생성 후 Job Summary에 첨부
# benchmark job은 benchmark_summary.py도 추가 생성
# benchmark job summary 최상단에 status(policy) 한 줄 우선 표시
# workflow_dispatch 입력으로 기준 외부화 가능:
#   regressionThresholdSec (기본 0.2)
#   failOnRegression (기본 true)
#   maxAllowedFailures (기본 0)
#   failOnUnassignedHigh (기본 false)
#   smokeEscalateThreshold (기본 3)
#   (qa_smoke report + qa_policy_brief + policy snapshot에 반영)
#   failOnPolicyChange (기본 false)
#   policyChangeFailMin (기본 1)
```

정책 기준 문서: `../QA_POLICY.md`

## 다음 액션
1. qa_smoke.py를 CI job으로 연결
2. fixture 기반 상세 케이스(encoding/csv quoting/pdf failure) 확장
3. Android 템플릿과 parser smoke 결과 연동(개발자 메뉴)
