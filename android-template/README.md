# Android Compose Template

업로드 → 미분류 검수 → 월간 리포트 화면 뼈대입니다.

## 포함 파일
- `ui/upload/UploadScreen.kt`
- `ui/review/UncategorizedReviewScreen.kt`
- `ui/report/ReportScreen.kt`
- `ui/common/Models.kt`

## 연결 포인트
- UploadScreen: run_import.py 호출
- UncategorizedReviewScreen: export_uncategorized.py + apply_feedback.py 호출
- ReportScreen: monthly_report.py 호출
