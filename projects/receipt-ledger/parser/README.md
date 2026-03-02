# TossBank Parser Prototype (Week 1)

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

## 다음 액션
1. 앱 UI에서 미분류 리스트 화면 연결
2. 카테고리 선택 시 apply_feedback와 동일 로직 호출
3. 고정비 후보 로직 고도화
