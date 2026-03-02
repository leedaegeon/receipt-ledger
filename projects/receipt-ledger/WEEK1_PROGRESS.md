# Week 1 진행현황 (토스뱅크 기준)

## 완료
- [x] D4 파서 v1 구조 생성 (CSV + PDF)
- [x] D5 헤더 후보 자동 매핑 로직
- [x] D6 정규화/분류 엔진 v1
- [x] D7 해시 기반 중복 제거
- [x] 샘플 데이터 E2E 검증 (`sample_tossbank.csv`)
- [x] 실파일 PDF E2E 검증 (`tossbank_statement_2026-03.pdf`)

## 산출물
- `parser/models.py`
- `parser/normalize.py`
- `parser/classifier.py`
- `parser/dedup.py`
- `parser/pdf_extract.js`
- `parser/tossbank_parser.py`
- `parser/run_import.py`
- `data/sample_tossbank.csv`
- `data/sample_tossbank.normalized.json`
- `data/tossbank_statement_2026-03.normalized.json`

## 검증 결과
- 실파일 파싱: 160건
- direction 분포(보정 후): expense 71 / income 84 / transfer 중심 정리
- 카테고리 미분류 비율: **16.9%** (71건 중 12건)
- 월간 리포트 JSON 생성 완료
  - 총수입 8,034,868원
  - 총지출 6,019,934원
  - 순현금흐름 2,014,934원

## 다음 우선순위
1. 오류행 리포트 + 수동 분류 반영(학습)
2. UI 연결용 API 스펙 정리
3. 고정비 후보 정확도 개선
