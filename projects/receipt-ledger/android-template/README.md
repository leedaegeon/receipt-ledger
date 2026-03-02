# Android Compose Template

업로드 → 미분류 검수 → 월간 리포트 화면 뼈대 + ViewModel 템플릿입니다.

## 포함 파일
- `ui/upload/UploadScreen.kt`
  - `ActivityResultContracts.OpenDocument()` 기반 파일 선택기 wiring
  - URI 영구 권한(`takePersistableUriPermission`) 예시
- `ui/review/UncategorizedReviewScreen.kt`
  - 미분류 목록 + 항목 탭 시 다이얼로그 오픈 흐름
- `ui/review/CategorySelectionDialog.kt`
  - 미분류 거래 카테고리 선택 다이얼로그 템플릿
- `ui/common/Models.kt`
- `ui/common/PipelineRunner.kt` (현재 Stub 인터페이스)
- `ui/common/LedgerViewModel.kt`
  - 상태/이벤트
  - `LedgerViewModelFactory` + `SavedStateHandle` 생성 노트

## ViewModel Factory 노트
- Compose/NavGraph 스코프에서 동일 ViewModel을 공유하려면 동일 owner를 사용하세요.
- `SavedStateHandle` 사용 시 `CreationExtras` 기반 Factory 구현이 안전합니다.
- DI(Hilt/Koin) 도입 전에는 `LedgerViewModelFactory(pipeline)`를 명시적으로 주입하세요.

## 연결 포인트
- UploadScreen: 파일 선택 → `onFilePicked(uri, displayName)` → `runImport(...)`
- Review: 아이템 탭 → `CategorySelectionDialog` → `onReviewCategorySelected()` 반영 → `saveReviewFeedback()`
- Report: `buildMonthlyReport(...)` 호출 후 요약 표시

## 주의사항
- 현재 템플릿은 **UI/상태 흐름 검증용**입니다.
- 실제 배포 앱에서는 Python 실행 대신 Kotlin 이식/서버 API/임베디드 런타임 전략이 필요합니다.
