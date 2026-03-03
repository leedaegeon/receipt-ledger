# Receipt Ledger 로컬 실행 가이드

이 문서는 `projects/receipt-ledger` 기준으로 **파서(Python)** + **Android 템플릿(JVM/Compose)** 를 로컬에서 점검하는 최소 절차를 정리합니다.

## 1) 사전 요구사항

- Python 3.10+
- Node.js 22+ (`pdf_extract.js` 경유 PDF 파싱 시 필요, 프로젝트 기준 고정)
- (선택) Android Studio / Gradle 환경

권장 작업 위치:

```bash
cd /home/node/.openclaw/workspace
```

## 2) 빠른 파서 실행 (CLI)

```bash
cd projects/receipt-ledger/parser
```

### 2-1) PDF 파싱용 Node 의존성 설치 (최초 1회)

```bash
npm init -y
npm i pdf-parse
```

간단 확인:
```bash
node -e "console.log(process.version, require('pdf-parse/package.json').version)"
node pdf_extract.js ../data/tossbank_statement_2026-03.pdf | head -n 5
```

### 2-2) Import 실행

```bash
python3 run_import.py ../data/tossbank_statement_2026-03.pdf --month 2026-03 --account 토스뱅크 --out-dir ../data
```

생성 확인:

- `projects/receipt-ledger/data/*.normalized.json`
- `projects/receipt-ledger/data/*.invalid.json`

후속:

```bash
python3 export_uncategorized.py ../data/tossbank_statement_2026-03.2026-03.normalized.json --out ../data/tossbank_statement_2026-03.2026-03.normalized.feedback.template.json
python3 monthly_report.py ../data/tossbank_statement_2026-03.2026-03.normalized.json --month 2026-03 --account 토스뱅크 --out ../data/tossbank_statement_2026-03.2026-03.normalized.report.json
```

## 3) Android `ProcessLedgerPipeline` 로컬 실행 전제

`android-template/ui/common/PipelineRunner.kt`의 `ProcessLedgerPipeline`는 초기화 시 아래를 검증합니다.

1. parser 디렉터리 존재 여부
2. 필수 스크립트 존재 여부
   - `run_import.py`
   - `export_uncategorized.py`
   - `apply_feedback.py`
   - `monthly_report.py`
3. Python 실행파일 유효 여부 (`python --version`)

### 환경변수 오버라이드

기본값 대신 커스텀 경로를 쓰려면:

- `RECEIPT_LEDGER_PYTHON_BIN` (기본: `python3`)
- `RECEIPT_LEDGER_PARSER_DIR` (기본: `<workspace>/projects/receipt-ledger/parser`)
- `RECEIPT_LEDGER_DATA_DIR` (기본: `<workspace>/projects/receipt-ledger/data`)

예시:

```bash
export RECEIPT_LEDGER_PYTHON_BIN=/usr/bin/python3
export RECEIPT_LEDGER_PARSER_DIR=/home/me/work/receipt-ledger/parser
export RECEIPT_LEDGER_DATA_DIR=/home/me/work/receipt-ledger/data
```

## 4) 최소 Smoke Test 절차

아래 4단계가 모두 통과하면 로컬 파이프라인 기본 동작은 정상으로 봅니다.

1. **Import 성공**
   - 입력 파일이 읽기 가능해야 함
   - `*.normalized.json`, `*.invalid.json` 생성 확인
2. **Uncategorized Export 성공**
   - normalized 파일 입력
   - `*.feedback.template.json` 생성 확인
3. **Feedback Apply 성공**
   - normalized + feedback 파일 입력
   - stdout에 `rules_updated`, `recategorized`, `rules_total` 파싱 가능
4. **Monthly Report 성공**
   - `*.report.json` 생성 확인
   - summary(`total_income`, `total_expense`, `net_cashflow`) 파싱 가능

### 실패 시 체크리스트

- Python 경로 오타 / 실행권한 문제
- parser 경로 오타
- 입력 파일 경로 오타 또는 읽기 권한 부족
- JSON 산출물이 실제 생성되지 않았는데 후속 단계로 진행한 경우
- `CalledProcessError ... pdf_extract.js` 발생 시:
  1) `node pdf_extract.js <pdf경로>` 단독 실행으로 Node 에러 원문 확인
  2) `node -v`가 22+인지 확인
  3) `PDFParse is not a constructor`가 나오면 `npm i pdf-parse` 재설치 후 `pdf_extract.js`를 현재 저장소 버전으로 되돌린 뒤 재시도

## 5) D12 검증 절차 (성능 + 예외 처리)

### 5-1) 성능 벤치마크
```bash
cd projects/receipt-ledger/parser
python3 benchmark_pipeline.py --rows 5000 --repeats 3 --fail-on-target --out ../data/benchmark_pipeline_result.json
# 고정비 임계값 오버라이드 포함 측정(선택)
python3 benchmark_pipeline.py --rows 5000 --repeats 3 --fixed-cost-min-months 3 --out ../data/benchmark_pipeline_result.json
python3 benchmark_history.py
python3 benchmark_summary.py --regression-threshold-sec 0.2 --stddev-threshold-sec 0.05 --fail-on-regression
python3 qa_report_merge.py
cat ../data/benchmark_summary.md
cat ../data/qa_integrated_summary.md
# 옵션 검증(실패 기대)
python3 benchmark_pipeline.py --rows 0
```
기대 출력(요약):
- `- import: PASS avg=...s target<=5.0s`
- `- export_uncategorized: PASS avg=...s target<=1.0s`
- `- apply_feedback: PASS avg=...s target<=1.0s`
- `- monthly_report: PASS avg=...s target<=1.0s`
- `- import: PASS avg=...s stddev=...s target<=5.0s`
- `- pipeline_total_avg_sec: ...s`
- `- overall: PASS`
- `benchmark_summary.md`의 Recent Runs에서 Δ(이전 실행 대비 증감) 확인
- `benchmark_pipeline_result.json`에서 `fixed_cost_options`가 전달값과 일치하는지 확인
- `benchmark_summary.md` 상단의 `fixed_cost_options: ...` 표시 확인
- `qa_integrated_summary.md`의 `pipeline_total_avg_sec`, `fixed_cost_options`, smoke policy 상태 확인
- `benchmark_pipeline.py --rows 0` 실행 시 `benchmark 옵션 오류: --rows 는 1 이상이어야 합니다.` 출력
- Δ가 +0.2s 초과인 step은 `Regression Warning` 섹션에 표시
- stddev가 0.05s 초과인 step은 `Variance Warning` 섹션에 표시
- `qa_policy_brief.py` 실행 시 Variance Warning 기반 `VAR-*` action item이 자동 생성됨(반복 시 HIGH 승격)

정밀 확인 명령:
```bash
python3 - <<'PY'
import json
p='../data/benchmark_pipeline_result.json'
d=json.load(open(p, encoding='utf-8'))
print('all_pass=', d['verdict']['all_pass'])
for k,v in d['verdict']['steps'].items():
    print(k, 'avg=', v['avg_sec'], 'target=', v['target_sec'], 'pass=', v['pass'])
PY
python3 benchmark_summary.py
cat ../data/benchmark_summary.md
```

### 5-2) 예외 처리
```bash
# (a) 빈 파일
: > ../data/empty.json
python3 monthly_report.py ../data/empty.json

# (b) 손상 형식 JSON
printf '{broken' > ../data/broken.json
python3 export_uncategorized.py ../data/broken.json

# (c) CSV 필수 헤더 누락
printf 'foo,bar\n1,2\n' > ../data/missing_header.csv
python3 run_import.py ../data/missing_header.csv

# (d) CSV 인코딩 오류(cp949 fixture)
python3 run_import.py ./fixtures/cp949.csv

# (e) 빈 CSV fixture
python3 run_import.py ./fixtures/empty.csv

# (f) 손상 CSV fixture(따옴표/구분자)
python3 run_import.py ./fixtures/bad_quoted.csv

# (g) 손상 CSV fixture(NUL)
python3 run_import.py ./fixtures/bad_nul.csv

# (h) 손상 PDF fixture
python3 run_import.py ./fixtures/invalid.pdf

# (i) 빈 PDF fixture
python3 run_import.py ./fixtures/empty.pdf

# (j) 지원하지 않는 확장자
python3 run_import.py ./fixtures/unsupported.txt

# (k) monthly_report 고정비 옵션 유효성
python3 monthly_report.py ./fixtures/minimal.normalized.json --fixed-cost-amount-tolerance-ratio -0.1

# (l) apply_feedback 빈 feedback 파일
python3 apply_feedback.py ./fixtures/minimal.normalized.json ./fixtures/empty.json

# (m) apply_feedback 빈 normalized 배열
python3 apply_feedback.py ./fixtures/empty_list.json ./fixtures/bad_feedback.json
```
기대 결과(문구 일부 일치 기준):
- (a) `리포트 생성 실패: 입력 JSON 파일이 비어 있습니다.`
- (b) `손상된 JSON 형식입니다:`
- (c) `입력 데이터 오류: 필수 헤더 누락:`
- (d) `CSV 인코딩 오류(UTF-8/UTF-8-SIG 필요, cp949 등 비지원)`
- (e) `CSV 파일이 비어 있습니다.`
- (f) `CSV 형식 오류: 유효 거래 행을 파싱하지 못했습니다.`
- (g) `CSV 파일 손상 오류(NUL 바이트 포함)`
- (h) `PDF 텍스트 추출 실패` 또는 `지원되지 않는 형식`
- (i) `PDF 파일이 비어 있습니다.`
- (j) `지원하지 않는 파일 형식입니다(.txt)`
- (k) `리포트 생성 실패: --fixed-cost-amount-tolerance-ratio 는 0 이상이어야 합니다.`
- (l) `feedback JSON 파일이 비어 있습니다.`
- (m) `normalized transaction 배열이 비어 있습니다.`
- 추가 확인(선택): 손상 CSV/PDF에서 `CSV 형식 오류`, `PDF 텍스트 추출 실패` 메시지 확인

### 5-3) D13 Smoke 자동 검증 (원커맨드)
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
# recurrence 표의 source_suites(top)로 POLICY-SANITY 반복 여부 확인
# policy 출처 반복 횟수(policy_occurrences)가 임계치 이상이면 POLICY-SANITY 우선순위 HIGH 승격
python3 qa_policy_snapshot.py
cat ../data/qa_policy_snapshot.json
python3 qa_policy_snapshot_history.py
python3 qa_policy_snapshot_diff.py
# 정책 변화 fail gate(옵션)
python3 qa_policy_snapshot_diff.py --fail-on-policy-change --policy-change-fail-min 1
python3 qa_policy_sanity.py
# 기대 출력: QA_POLICY_SANITY_OK
# 실패 시 각 오류 아래 hint 라인으로 수정 위치(.github/workflows/... 또는 QA_POLICY.md) 확인
# 추가 산출물: ../data/qa_policy_sanity_checklist.md (수정 체크리스트)
# CI Job Summary의 "QA Policy Sanity" 섹션에서도 동일 결과+체크리스트 확인 가능
cat ../data/qa_policy_snapshot_diff.md
# changed_count, Key Changes 섹션 확인
# fixed_cost_options.* 및 pipeline_total_avg_sec 변화도 함께 확인
# CI에서도 동일하게 qa_policy_snapshot_diff.py fail 옵션으로 정책 변화 gate 적용
# qa_policy_sanity.py로 QA_POLICY.md와 workflow_dispatch 기본값 일치 여부 확인
```
기대 결과:
- 마지막 줄 `QA_SMOKE_OK`
- benchmark suite에서 `overall: PASS` 포함
- benchmark 결과 JSON에서 `rows=5000`, `fixed_cost_options.min_months=3` 자동 검증
- 실패 시 어떤 케이스가 깨졌는지 `FAIL <label>: ...` 형태로 즉시 표시
- `qa_smoke_summary.md`에 passed/failed 카운트 + 실패 케이스 테이블 표시
- `qa_integrated_summary.md` 상단에서 policy 상태(`failed <= max_failures`) 확인
- `qa_policy_brief.md`에서 우선순위(HIGH/MEDIUM)와 Action Items(owner/due/verify) 확인
- `qa_action_items.json`에서 `created_at`, `source_suite`, `id`, `status` 메타 확인
- `qa_action_history.jsonl`로 action item 반복 출현 여부 확인
- `qa_action_recurrence.md`에서 id별 반복 횟수 확인
- `qa_policy_snapshot.json`으로 실행 시점 정책값/결과 스냅샷 비교
- 재현용 fixture 위치: `projects/receipt-ledger/parser/fixtures/`

CI 실행 위치:
- `.github/workflows/receipt-ledger-qa.yml`
- workflow_dispatch에서 기준 조정 가능:
  - `regressionThresholdSec` (기본 0.2)
  - `failOnRegression` (기본 true)
  - `maxAllowedFailures` (기본 0)
  - `failOnUnassignedHigh` (기본 false)
  - `smokeEscalateThreshold` (기본 3)
  - `failOnPolicyChange` (기본 false)
  - `policyChangeFailMin` (기본 1)
- 성공 시 benchmark 결과 아티팩트(`receipt-ledger-benchmark`) 업로드

### 5-4) D13 parser 회귀 테스트 (샘플 데이터 기준)
파싱/미분류/리포트의 핵심 결과를 한 번에 고정값 회귀 검증합니다.

```bash
cd projects/receipt-ledger/parser
python3 qa_parser_regression.py --report-json ../data/qa_parser_regression_report.json
```

검증 항목:
- `run_import.py` 결과: `parsed=6`, `invalid=0`
- `export_uncategorized.py` 결과:
  - 미분류 지출 `2건`
  - 고유 거래처 `2개` (`한식당 점심`, `netflix`)
- `monthly_report.py` 결과(요약):
  - `total_income=2500000`
  - `total_expense=33700`
  - `net_cashflow=2466300`
  - 카테고리 금액: `미분류=27900`, `카페=4500`, `교통=1300`

디버깅 용도(산출물 디렉터리 유지):
```bash
python3 qa_parser_regression.py --keep-artifacts --work-dir ../data/.tmp_regression
```

### 5-5) 고정비 탐지 파라미터 조정
기본값은 `fixed_cost.py`의 공통 설정(`ratio=0.15`, `abs=10000`, `min_months=2`, `min_average_amount=30000`)을 사용하며, 필요 시 CLI로 조정 가능합니다.
```bash
python3 run_import.py ../data/tossbank_statement_2026-03.pdf --fixed-cost-min-months 3
python3 monthly_report.py ../data/tossbank_statement_2026-03.normalized.json --fixed-cost-min-months 3
```

---

정책 기준은 `projects/receipt-ledger/QA_POLICY.md`를 기준으로 관리하세요.

필요 시 이 문서를 기준으로 CI smoke job(예: import → export_uncategorized → monthly_report)으로 확장하세요.
