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

## 현재 제약
현재 런타임에는 PDF 텍스트 추출 라이브러리가 없어 `parse_pdf`는 placeholder입니다.
따라서 지금은 **PDF를 CSV로 변환해서** `parse_csv` 경로로 검증합니다.

## 다음 액션
1. PDF extractor 연결 (pypdf 또는 pdfplumber)
2. 토스뱅크 실제 파일 라인 파싱 룰 추가
3. Invalid row 리포트 UI와 연결
