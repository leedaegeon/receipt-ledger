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
```
기대 출력(요약):
- `- import: PASS avg=...s target<=5.0s`
- `- export_uncategorized: PASS avg=...s target<=1.0s`
- `- apply_feedback: PASS avg=...s target<=1.0s`
- `- monthly_report: PASS avg=...s target<=1.0s`
- `- overall: PASS`

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

# (e) 손상 PDF fixture
python3 run_import.py ./fixtures/invalid.pdf
```
기대 결과:
- (a) `리포트 생성 실패: 입력 JSON 파일이 비어 있습니다.`
- (b) `손상된 JSON 형식입니다:`
- (c) `입력 데이터 오류: 필수 헤더 누락:`
- (d) `입력 파일 인코딩 오류` 또는 `CSV 인코딩 오류`
- (e) `PDF 텍스트 추출 실패` 또는 `지원되지 않는 형식`
- 추가 확인(선택): 손상 CSV/PDF에서 `CSV 형식 오류`, `PDF 텍스트 추출 실패` 메시지 확인

### 5-3) D13 Smoke 자동 검증 (원커맨드)
```bash
cd projects/receipt-ledger/parser
python3 qa_smoke.py --suite all --report-json ../data/qa_smoke_report.json
# 또는 분리 실행
python3 qa_smoke.py --suite benchmark --report-json ../data/qa_smoke_report.json
python3 qa_smoke.py --suite exceptions --report-json ../data/qa_smoke_report.json
python3 qa_smoke_summary.py
cat ../data/qa_smoke_summary.md
python3 qa_report_merge.py
cat ../data/qa_integrated_summary.md
```
기대 결과:
- 마지막 줄 `QA_SMOKE_OK`
- benchmark suite에서 `overall: PASS` 포함
- 실패 시 어떤 케이스가 깨졌는지 `FAIL <label>: ...` 형태로 즉시 표시
- `qa_smoke_summary.md`에 passed/failed 카운트 + 실패 케이스 테이블 표시
- 재현용 fixture 위치: `projects/receipt-ledger/parser/fixtures/`

CI 실행 위치:
- `.github/workflows/receipt-ledger-qa.yml`
- 성공 시 benchmark 결과 아티팩트(`receipt-ledger-benchmark`) 업로드

### 5-4) 고정비 탐지 파라미터 조정
기본값은 유지되며 필요 시 CLI로 조정 가능합니다.
```bash
python3 run_import.py ../data/tossbank_statement_2026-03.pdf --fixed-cost-min-months 3
python3 monthly_report.py ../data/tossbank_statement_2026-03.normalized.json --fixed-cost-min-months 3
```

---

필요 시 이 문서를 기준으로 CI smoke job(예: import → export_uncategorized → monthly_report)으로 확장하세요.
