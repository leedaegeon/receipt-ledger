# Week 1 진행현황 (토스뱅크 기준)

## 완료
- [x] D4 파서 v1 구조 생성 (CSV 우선)
- [x] D5 헤더 후보 자동 매핑 로직
- [x] D6 정규화/분류 엔진 v1
- [x] D7 해시 기반 중복 제거
- [x] 샘플 데이터로 E2E 실행 검증 (`sample_tossbank.csv`)

## 산출물
- `parser/models.py`
- `parser/normalize.py`
- `parser/classifier.py`
- `parser/dedup.py`
- `parser/tossbank_parser.py`
- `parser/run_import.py`
- `data/sample_tossbank.csv`
- `data/sample_tossbank.normalized.json`

## 블로커
- 현재 런타임에 PDF 텍스트 추출 라이브러리 부재
- 따라서 `parse_pdf`는 NotImplemented 상태

## 다음 우선순위
1. PDF extractor 의존성 확보
2. 실파일 `tossbank_statement_2026-03.pdf` 파싱 연결
3. 오류행 리포트 + 컬럼 수동 매핑 UI(앱단)
