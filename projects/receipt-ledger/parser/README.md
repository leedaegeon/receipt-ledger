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
```

## PDF 처리
- `pdf-parse`(Node) 기반 텍스트 추출기를 연결했습니다.
- `pdf_extract.js`를 통해 PDF 텍스트를 추출하고, Python 파서가 거래행을 정규식으로 파싱합니다.

## 실파일 검증
```bash
python3 run_import.py ../data/tossbank_statement_2026-03.pdf
# parsed=160 -> tossbank_statement_2026-03.normalized.json
```

## 다음 액션
1. 분류 룰 고도화(미분류 축소)
2. Invalid row 리포트 및 수동 매핑 UI 연결
3. 월간 리포트 집계 모듈 연결
