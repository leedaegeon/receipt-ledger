# Category Selection Dialog UX Spec (v0.1)

## 목적
미분류 거래를 빠르게 분류하면서 오분류를 줄이는 선택 다이얼로그 UX를 정의한다.

## 진입 조건
- `direction=expense && category=미분류` 항목을 탭했을 때
- 리스트에서 "카테고리 지정" 버튼 클릭 시

## 다이얼로그 구성
1. 상단 요약
   - 가맹점명(필수)
   - 거래금액(필수, 원화 포맷)
   - 거래일(선택)
2. 카테고리 목록
   - 최근 사용 카테고리(최대 5) 상단 고정
   - 전체 카테고리 가나다순
3. 행동 버튼
   - 닫기
   - (선택사항) "룰로 저장" 토글

## UX 규칙
- 단일 탭으로 즉시 선택 반영 (`onSelect(category)`)
- 선택된 항목은 체크 아이콘/강조 색상 적용
- 다이얼로그 닫아도 현재 선택 상태는 유지
- 잘못 누름 대비: 저장 전 리스트에서 재변경 가능

## 오류/예외
- 카테고리 목록 로드 실패 시
  - 본문에 오류 메시지 + 재시도 버튼 노출
- 항목 저장 실패 시
  - Snackbar: "저장 실패, 다시 시도해주세요"

## 이벤트 로깅(선택)
- `category_dialog_opened`
- `category_selected`
- `category_dialog_dismissed`

## 코드 템플릿 매핑
- UI 컴포넌트: `android-template/ui/review/CategorySelectionDialog.kt`
- 상태 소스: `LedgerViewModel.reviewState.items`
- 저장 동작: `apply_feedback.py` 반영 전 feedback json 업데이트
