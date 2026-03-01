# DOMAIN.md

## 1) 목적
영수증 촬영 한 번으로 **결제일/금액/점포명/카테고리**를 자동 저장하는 초간단 가계부 앱의 도메인 규칙을 정의한다.

## 2) 제품 정의
- 한 줄 정의: "영수증 자동입력 기반 3초 가계부"
- 타깃: 수기 입력이 귀찮은 개인 사용자
- MVP 범위: 오프라인 중심, 서버리스

## 3) 핵심 엔터티
### Transaction
- id (UUID)
- type (expense|income)
- amount (Long, KRW 기준 원 단위)
- paymentDate (LocalDate)
- merchantName (String)
- categoryId (String)
- memo (String?)
- receiptId (UUID?)
- createdAt / updatedAt

### Receipt
- id (UUID)
- imageUri (로컬 경로)
- ocrRawText (String)
- parseStatus (success|partial|failed)
- capturedAt

### Category
- id
- name
- color
- icon
- isDefault

## 4) 비즈니스 규칙
1. amount > 0 이어야 저장 가능
2. paymentDate 미검출 시 "오늘" 기본값 + 사용자 확인 필수
3. category 미검출 시 "미분류"로 저장
4. OCR 실패여도 수동 입력 저장 가능
5. 동일 이미지 중복 저장은 해시로 감지(옵션)

## 5) 처리 상태
CAPTURED → OCR_DONE → PARSED → REVIEWED → SAVED
- 예외: OCR_FAILED, PARSE_PARTIAL

## 6) 자동분류 규칙
- 1차: 점포명 키워드 사전 매핑
- 2차: 사용자 수정 이력 우선 적용
- 실패 시: 미분류

## 7) 품질 지표
- 날짜 자동 추출 정확도
- 금액 자동 추출 정확도
- 상호명 자동 추출 정확도
- 카테고리 추천 정확도
- 저장 완료까지 평균 시간

## 8) 비기능 요구사항
- 오프라인 동작 필수
- 로컬 저장(서버 전송 없음)
- 앱 잠금(PIN/생체)
- 크래시 프리 세션 99%+
