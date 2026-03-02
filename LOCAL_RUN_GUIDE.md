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

---

필요 시 이 문서를 기준으로 CI smoke job(예: import → export_uncategorized → monthly_report)으로 확장하세요.
