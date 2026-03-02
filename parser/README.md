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
python3 run_import.py ../data/sample_tossbank.csv
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
python3 monthly_report.py ../data/tossbank_statement_2026-03.normalized.json
```

## 실파일 최신 결과
- 파싱 건수: 160
- 미분류 비율(지출 기준): 16.9%

## 수동 분류 학습 (rules.json 누적)
```bash
python3 learn_rule.py "씨유인덕원점" "편의점"
python3 run_import.py ../data/tossbank_statement_2026-03.pdf
```
- `../data/rules.json`에 `normalized_merchant -> category`가 누적 저장됩니다.

## 다음 액션
1. Invalid row UI 연결 (행별 수정/재처리)
2. 사용자 수정 기반 분류 학습 자동 저장(앱 연동)
3. 고정비 후보 로직 고도화
