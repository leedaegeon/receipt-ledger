# DOMAIN.md

## 1) 목적
사용자가 한 달치 **계좌내역(PDF/엑셀/CSV)** 을 업로드하면,
자동으로 거래를 정규화·분류하여 **월간 가계부를 생성/분석**하는 앱의 도메인 규칙을 정의한다.

## 2) 제품 정의
- 한 줄 정의: "월간 계좌내역 업로드 한 번으로 끝내는 자동 가계부"
- 타깃: 수기 입력 없이 월 단위 소비를 빠르게 정리하고 싶은 사용자
- MVP 범위: 오프라인 우선(온디바이스 처리), 서버리스

## 3) 입력 데이터 범위
### 지원 포맷 (MVP)
- PDF (은행/카드 명세서)
- XLSX / XLS
- CSV

### 최소 필수 컬럼(정규화 전)
- 거래일시(또는 날짜)
- 거래금액
- 거래처/적요(가맹점명)

### 선택 컬럼
- 입출금 구분
- 계좌/카드 식별자
- 잔액
- 통화

## 4) 핵심 엔터티
### StatementImport
- id (UUID)
- sourceType (pdf|xlsx|csv)
- fileUri (로컬 경로)
- importedAt
- parseStatus (success|partial|failed)
- totalRows
- validRows
- invalidRows

### Transaction
- id (UUID)
- importId (UUID)
- occurredAt (LocalDateTime)
- amount (Long, KRW 원 단위)
- direction (expense|income|transfer|unknown)
- merchantName (String)
- normalizedMerchantName (String)
- categoryId (String)
- memo (String?)
- accountLabel (String?)
- createdAt / updatedAt

### Category
- id
- name
- parentId (nullable)
- color
- icon
- isDefault

### MonthlyReport
- id (UUID)
- yearMonth (YYYY-MM)
- totalExpense
- totalIncome
- netCashflow
- topCategories (JSON)
- generatedAt

### RuleDictionary
- id
- ruleType (merchant_keyword|regex|amount_pattern)
- pattern
- targetCategoryId
- priority
- isActive

## 5) 비즈니스 규칙
1. 업로드 파일 1개는 StatementImport 1건으로 기록
2. Transaction 저장 조건: 날짜 + 금액 + 적요 중 2개 이상 유효
3. amount = 0 인 행은 기본 제외(옵션으로 포함 가능)
4. 동일 거래 중복 제거 키: (occurredAt, amount, normalizedMerchantName, accountLabel)
5. category 미분류 시 "미분류"로 저장
6. transfer(계좌이체/대체)로 판정된 거래는 기본 분석 합계에서 제외 옵션 제공
7. 사용자가 수정한 카테고리는 RuleDictionary에 로컬 학습 반영

## 6) 처리 파이프라인
UPLOADED → PARSED → NORMALIZED → DEDUPED → CLASSIFIED → REVIEWED → REPORTED
- 실패 분기: PARSE_FAILED / PARTIAL_SUCCESS

## 7) 분류 정책
### 1차: 룰 기반
- merchant keyword 매핑 (예: 스타벅스 → 카페)
- 정규식 매핑 (예: `택시|카카오T` → 교통)

### 2차: 사용자 학습 반영
- 사용자가 바꾼 분류를 동일 merchant에 우선 적용

### 3차: 예외 처리
- 실패 시 미분류

## 8) 분석 산출물 (MVP)
- 월 총지출 / 총수입 / 순현금흐름
- 카테고리별 지출 합계/비중
- 고정비 후보(반복 결제 추정)
- 상위 지출 거래 Top N

## 9) 품질 지표
- 파싱 성공률 (validRows / totalRows)
- 자동 분류 정확도 (수정 전후 기준)
- 중복 제거 정확도
- 업로드→리포트 생성 소요시간

## 10) 비기능 요구사항
- 오프라인 동작 필수
- 개인정보 외부 전송 없음
- 파일 원본 로컬 저장/삭제 제어
- 대용량(최소 5,000행) 처리 시 앱 비정상 종료 금지

## 11) 보안/개인정보
- 로컬 DB 암호화(SQLCipher 또는 OS 암호화 저장소 활용)
- 앱 잠금(PIN/생체)
- 민감 데이터(계좌번호 일부) 마스킹 표시
- 사용자가 원하면 원본 파일 즉시 삭제 가능

## 12) 에러/예외 정책
- 파싱 실패 행은 "오류 행 리스트"로 분리 제공
- 헤더 인식 실패 시 컬럼 수동 매핑 UI 제공
- 통화/날짜 포맷 충돌 시 기본 규칙 + 사용자 선택

## 13) 릴리즈 기준 (DoD)
- 주요 은행/카드 예시 파일 10종에서 파싱 성공률 90%+
- 월간 리포트 자동 생성 성공률 95%+
- 미분류 비율 25% 이하 (초기 기준)
- 크래시 프리 세션 99%+
