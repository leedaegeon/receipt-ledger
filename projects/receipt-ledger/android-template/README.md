# Android Compose Template

업로드 → 미분류 검수 → 월간 리포트 화면 뼈대 + ViewModel 템플릿입니다.

## 포함 파일
- `ui/upload/UploadScreen.kt`
  - `ActivityResultContracts.OpenDocument()` 기반 파일 선택기 wiring
  - URI 영구 권한(`takePersistableUriPermission`) 예시
  - `UploadScreenContent` + Preview 샘플 추가
- `ui/review/UncategorizedReviewScreen.kt`
  - 미분류 목록 + 항목 탭 시 다이얼로그 오픈 흐름
  - Preview 샘플 추가
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
  - `seedUploadForPreview` / `seedReviewItemsForTemplate`로 샘플 상태 주입
  - `LedgerViewModelFactory` + `SavedStateHandle` 생성 노트
- `ui/common/SampleData.kt`
  - 프리뷰용 샘플 상태 + `DemoLedgerPipeline`
- `ui/common/AppShell.kt`
  - 업로드/검수/리포트 탭 기반 통합 샘플
  - `@Preview` 진입점 + 자동 탭 전환/성공 스낵바
- `ui/report/ReportScreen.kt`
  - 월간 요약 카드 렌더링 템플릿 + Preview

## Preview-friendly 개선 포인트
- Python/파일 시스템 의존이 없어도 `DemoLedgerPipeline`으로 화면 렌더링 가능
- `AppShellPreview`에서 샘플 import/review 상태를 미리 주입해 즉시 확인 가능
- Upload/Review/Report 각각 단독 Preview 제공
- Import 완료 시 Upload → Review 자동 전환 + 스낵바 표시
- Review 저장 성공 시 스낵바(`카테고리 저장 성공`) 표시

## Android Studio 실행 절차 (체크리스트)

> 현재 템플릿은 `ui/**` 중심입니다. 앱 모듈의 `MainActivity`/`setContent { AppShell(...) }` 연결은 프로젝트 쪽에서 최종 구성하세요.

- [ ] Android Studio 최신 안정 버전 설치
- [ ] JDK 17 및 Android SDK(Compile SDK 34+) 준비
- [ ] 프로젝트 열기: `projects/receipt-ledger/android-template`
- [ ] Gradle Sync 완료 확인
- [ ] 에뮬레이터(또는 실기기) 실행
- [ ] 앱 진입점에서 `AppShell(viewModel)` 연결
  - 데모/프리뷰 목적: `LedgerViewModel(DemoLedgerPipeline(), ReviewFileGateway(), SavedStateHandle())`
  - 실제 파이프라인: `LedgerViewModelFactory(ProcessLedgerPipeline())`
- [ ] Run 실행 후 화면 확인

### 실행 확인 포인트 (체크리스트)
- [ ] Upload 탭: 파일 선택 버튼/분석 버튼 렌더링
- [ ] 샘플 import 성공 시 Review 탭으로 자동 이동되는지 확인
- [ ] Review 탭: 미분류 목록 카드 + 카테고리 다이얼로그 열림 확인
- [ ] 카테고리 저장 후 `카테고리 저장 성공` 스낵바 확인
- [ ] Report 탭: 리포트 갱신 버튼/요약 카드 렌더링 확인

## ViewModel Factory 노트
- Compose/NavGraph 스코프에서 동일 ViewModel을 공유하려면 동일 owner를 사용하세요.
- `SavedStateHandle` 사용 시 `CreationExtras` 기반 Factory 구현이 안전합니다.
- DI(Hilt/Koin) 도입 전에는 `LedgerViewModelFactory(pipeline)`를 명시적으로 주입하세요.

## 연결 포인트
- UploadScreen: 파일 선택 → `onFilePicked(uri, displayName)` → `runImport(...)`
- Review: Import 성공 후 `prepareReviewTemplate(normalizedPath)`로 템플릿 준비 → 아이템 탭 → `CategorySelectionDialog` → `onReviewCategorySelected()` 반영 → `saveReviewFeedback()`
- Report: `buildMonthlyReport(...)` 결과를 `reportState`로 바인딩해 요약 표시 (`ReportScreen`)
- 통합 샘플: `AppShell(viewModel)`에서 탭 전환으로 전체 플로우 검증

## 로컬 실행 가이드
- 프로젝트 전체 로컬 실행/스모크 테스트 절차: [`../LOCAL_RUN_GUIDE.md`](../LOCAL_RUN_GUIDE.md)

## 주의사항
- 현재 템플릿은 **UI/상태 흐름 검증용**입니다.
- 실제 배포 앱에서는 Python 실행 대신 Kotlin 이식/서버 API/임베디드 런타임 전략이 필요합니다.
