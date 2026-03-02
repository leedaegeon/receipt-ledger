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
```
- 측정 단계: `run_import.py` → `export_uncategorized.py` → `apply_feedback.py` → `monthly_report.py`
- 기본 목표(평균): import ≤ 5s, export ≤ 1s, apply ≤ 1s, report ≤ 1s
- 기대 출력 예:
  - `- import: PASS avg=...s target<=5.0s`
  - `- overall: PASS`
- 결과 파일: `../data/benchmark_pipeline_result.json` (`verdict.all_pass` 포함)

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
- 기대: 각 스크립트가 `입력 파일 인코딩 오류`, `손상된 JSON 형식`, `필수 헤더 누락`, `CSV 형식 오류`, `PDF 텍스트 추출 실패` 등 명확한 에러 메시지 출력

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
python3 qa_smoke.py --suite all
# 또는 분리 실행
python3 qa_smoke.py --suite benchmark
python3 qa_smoke.py --suite exceptions
```
- 기대 출력: `QA_SMOKE_OK`
- 포함 검증:
  - 5,000행 벤치마크 목표 통과(`overall: PASS`)
  - `fixtures/empty.json` 빈 JSON 에러 메시지
  - `fixtures/broken.json` 손상 JSON 에러 메시지
  - `fixtures/missing_header.csv` 헤더 누락 에러 메시지
  - `fixtures/cp949.csv` 인코딩 에러 메시지
  - `fixtures/invalid.pdf` PDF 추출/형식 에러 메시지
  - 고정비 옵션 유효성 에러 메시지
  - `fixtures/bad_feedback.json` feedback schema 에러 메시지

CI 준비:
```bash
# GitHub Actions: .github/workflows/receipt-ledger-qa.yml
# 수동 실행(workflow_dispatch) 또는 parser 변경 시 자동 실행
# matrix suite: benchmark / exceptions 로 분리 실행
```

## 다음 액션
1. qa_smoke.py를 CI job으로 연결
2. fixture 기반 상세 케이스(encoding/csv quoting/pdf failure) 확장
3. Android 템플릿과 parser smoke 결과 연동(개발자 메뉴)
