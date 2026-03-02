# 토스뱅크 내역서 매핑 스펙 (v0.1)

## 1) 대상
- 기관: 토스뱅크
- 문서: 월간 계좌 거래내역서 (PDF / CSV / 엑셀 변환본)
- 목표: 거래행을 표준 Transaction 스키마로 정규화

## 2) 표준 스키마 (앱 내부)
- occurredAt: LocalDateTime
- amount: Long (KRW 원 단위, 절대값)
- direction: expense | income | transfer | unknown
- merchantName: String
- normalizedMerchantName: String
- memo: String?
- accountLabel: String?
- sourceRowHash: String (중복 제거 키 생성용)

## 3) 토스뱅크 컬럼 후보 매핑
실제 파일마다 헤더가 달라질 수 있어, 아래 후보명으로 탐지:

### 날짜/시간 후보
- 거래일시
- 거래일
- 일시
- 시간
- 승인일시

### 금액 후보
- 거래금액
- 출금금액
- 입금금액
- 금액
- 결제금액

### 적요/거래처 후보
- 적요
- 거래내용
- 거래처
- 상대계좌명
- 메모

### 잔액 후보 (선택)
- 거래후잔액
- 잔액

## 4) 파싱 규칙

### 4.1 날짜 파싱
허용 포맷:
- yyyy-MM-dd HH:mm:ss
- yyyy.MM.dd HH:mm
- yyyy-MM-dd
- yyyy/MM/dd HH:mm

시간이 없으면 00:00:00으로 보정.

### 4.2 금액 파싱
- 쉼표/원/공백 제거 후 숫자 추출
- 음수 표기, 출금/입금 컬럼 분리 형태 모두 처리
- 최종 저장은 절대값(amount>0)
- direction 판단으로 의미 분리

### 4.3 direction 판정 우선순위
1. 출금금액 > 0 => expense
2. 입금금액 > 0 => income
3. 거래구분 컬럼이 있으면 키워드 매칭
   - 출금/결제/이체출금 => expense 또는 transfer
   - 입금/이체입금 => income 또는 transfer
4. 적요 키워드
   - "이체", "송금", "입출금" + 본인계좌 패턴 => transfer
5. 미판정 => unknown

### 4.4 merchantName 정규화
- 앞뒤 공백 제거
- 연속 공백 1개로 축소
- 특수문자 과다 제거(단, 브랜드 식별에 필요한 -,_는 유지)
- normalizedMerchantName은 소문자/공백정리/법인표기(주식회사 등) 제거

## 5) 카테고리 초기 룰 (토스뱅크용)
- 편의점: CU, GS25, 세븐일레븐, 이마트24
- 카페: 스타벅스, 투썸, 메가커피, 컴포즈, 빽다방
- 식비: 배달의민족, 요기요, 쿠팡이츠, 음식점, 식당
- 교통: 카카오T, 택시, 지하철, 버스
- 쇼핑: 쿠팡, 네이버페이, 11번가, 무신사
- 통신/구독: SKT, KT, LGU+, NETFLIX, YOUTUBE, SPOTIFY
- 금융이체: 토스, 이체, 송금, 자동이체

매칭 실패 시: 미분류

## 6) 중복 제거 키
sourceRowHash = SHA-1(
  occurredAt(분 단위) + amount + normalizedMerchantName + accountLabel
)

추가 규칙:
- 동일 hash + 동일 importId는 중복으로 간주
- 다른 importId라도 동일 월 내 동일 hash가 반복되면 사용자 확인 팝업 옵션

## 7) 오류 행 처리
- 필수 2개 미충족(날짜/금액/적요 중 2개 미충족) => invalid row
- invalid row는 별도 탭에 보관
- 사용자 수동 매핑 후 재처리 가능

## 8) QA 테스트 케이스 (최소)
1. 출금/입금 컬럼 분리형 CSV
2. 단일 금액 컬럼 + 거래구분 텍스트형
3. 날짜만 있고 시간 없는 파일
4. 적요가 비어있는 행
5. 천단위/음수/괄호 표기 금액
6. 동일 파일 재업로드 중복 검증

## 9) 구현 체크리스트
- [ ] TossBankHeaderDetector 구현 (후보 헤더 매칭)
- [ ] TossBankNormalizer 구현 (날짜/금액/적요 정규화)
- [ ] DirectionResolver 구현
- [ ] MerchantNormalizer 구현
- [ ] CategoryRuleEngine v1 연결
- [ ] DedupHash 생성/검증
- [ ] InvalidRow 리포트 UI 연결

## 10) 오픈 이슈
- 토스뱅크 PDF 텍스트 추출 품질 편차
- 암호화 PDF 대응 여부
- 본인계좌 이체를 transfer로 안정 분류하는 패턴 강화 필요
