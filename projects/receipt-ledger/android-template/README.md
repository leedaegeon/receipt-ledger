# Android Compose Template

업로드 → 미분류 검수 → 월간 리포트 화면 뼈대 + ViewModel + ProcessRunner 예시입니다.

## 포함 파일
- `ui/upload/UploadScreen.kt`
- `ui/review/UncategorizedReviewScreen.kt`
- `ui/report/ReportScreen.kt`
- `ui/common/Models.kt`
- `ui/common/PipelineRunner.kt` (ProcessBuilder로 python 스크립트 실행)
- `ui/common/LedgerViewModel.kt` (상태/이벤트)
- `ui/common/AppShell.kt` (탭 기반 샘플 연결)

## 연결 포인트
- UploadScreen: `run_import.py`
- UncategorizedReviewScreen: `export_uncategorized.py` + `apply_feedback.py`
- ReportScreen: `monthly_report.py`

## 주의사항
- Android 앱에서 외부 python 실행은 일반 배포 앱 구조와 맞지 않을 수 있습니다.
- 현재 템플릿은 **파이프라인 연동 개념 검증용**입니다.
- 실제 앱 배포 시엔 파서 로직을 Kotlin으로 이식하거나, 별도 런타임 전략(Chaquopy 등) 검토가 필요합니다.
