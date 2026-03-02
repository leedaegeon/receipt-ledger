# Android Compose Template

업로드 → 미분류 검수 → 월간 리포트 화면 뼈대 + ViewModel 템플릿입니다.

## 포함 파일
- `ui/upload/UploadScreen.kt`
  - `ActivityResultContracts.OpenDocument()` 기반 파일 선택기 wiring
  - URI 영구 권한(`takePersistableUriPermission`) 예시
- `ui/review/UncategorizedReviewScreen.kt`
  - 미분류 목록 + 항목 탭 시 다이얼로그 오픈 흐름
- `ui/review/CategorySelectionDialog.kt`
  - 미분류 거래 카테고리 선택 다이얼로그 템플릿(검색/최근 카테고리/empty state 포함)
- `ui/common/Models.kt`
- `ui/common/PipelineRunner.kt` (parser Python 스크립트 실행 계층)
- `ui/common/FeedbackTemplateMapper.kt`
  - `export_uncategorized.py` 결과 파싱
  - `apply_feedback.py` 입력 JSON 직렬화
- `ui/common/ReviewFileGateway.kt`
  - 템플릿 읽기/피드백 쓰기 I/O 샘플
- `ui/common/LedgerViewModel.kt`
  - 상태/이벤트
  - `LedgerViewModelFactory` + `SavedStateHandle` 생성 노트
- `ui/common/AppShell.kt`
  - 업로드/검수/리포트 탭 기반 통합 샘플
- `ui/report/ReportScreen.kt`
  - 월간 요약 카드 렌더링 템플릿

## ViewModel Factory 노트
- Compose/NavGraph 스코프에서 동일 ViewModel을 공유하려면 동일 owner를 사용하세요.
- `SavedStateHandle` 사용 시 `CreationExtras` 기반 Factory 구현이 안전합니다.
- DI(Hilt/Koin) 도입 전에는 `LedgerViewModelFactory(pipeline)`를 명시적으로 주입하세요.

## 연결 포인트
- UploadScreen: 파일 선택 → `onFilePicked(uri, displayName)` → `runImport(...)`
- Review: Import 성공 후 `prepareReviewTemplate(normalizedPath)`로 템플릿 준비 → 아이템 탭 → `CategorySelectionDialog` → `onReviewCategorySelected()` 반영 → `saveReviewFeedback()`
- Report: `buildMonthlyReport(...)` 결과를 `reportState`로 바인딩해 요약 표시 (`ReportScreen`)
- 통합 샘플: `AppShell(viewModel)`에서 탭 전환으로 전체 플로우 검증

## 주의사항
- 현재 템플릿은 **UI/상태 흐름 검증용**입니다.
- 실제 배포 앱에서는 Python 실행 대신 Kotlin 이식/서버 API/임베디드 런타임 전략이 필요합니다.
