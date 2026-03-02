# Android Compose Template (Receipt Ledger)

`android-template`는 **Android Studio에서 바로 Run 가능한 최소 앱 뼈대**와,
`receipt-ledger/parser` Python 파이프라인 연동 샘플을 함께 제공합니다.

---

## 0) 이번 버전 핵심

- `MainActivity` + `setContent { AppShell(...) }` + 기본 테마 연결 완료
- `demo/live` **product flavor**로 파이프라인 전환 가능
  - `demo`: `DemoLedgerPipeline` (즉시 실행/데모용)
  - `live`: `ProcessLedgerPipeline` (실데이터/Python 연결)
- Upload → Review → Report 흐름을 한 앱에서 바로 확인 가능

---

## 1) 바로 실행(데모) 경로 — 초보자용

가장 빠르게 화면이 뜨는 경로입니다.

### 사전 준비
- Android Studio 최신 안정 버전
- JDK 17
- Android SDK (Compile SDK 34 이상)

### 실행 순서
1. Android Studio에서 `projects/receipt-ledger/android-template` 열기
2. Gradle Sync 완료 대기
3. Build Variant를 `demoDebug`로 선택
4. 에뮬레이터/실기기 선택 후 **Run**

### 기대 결과
- 앱 시작 시 바로 `AppShell` 표시
- 하단 탭(업로드/미분류/리포트) 이동 가능
- 실제 파일 없이도 데모 플로우 상태 확인 가능

---

## 2) 실데이터 연결 경로 — Python 파이프라인 연동

> `live` flavor는 `ProcessLedgerPipeline`을 사용해 `parser/*.py`를 호출합니다.

### 전제 조건
- `projects/receipt-ledger/parser` 스크립트가 존재해야 함
- 실행 환경에 Python 사용 가능해야 함
- Android Studio Run 구성에서 아래 환경변수 설정 권장

- `RECEIPT_LEDGER_PYTHON_BIN` (예: `python3`)
- `RECEIPT_LEDGER_PARSER_DIR` (예: `/.../projects/receipt-ledger/parser`)
- `RECEIPT_LEDGER_DATA_DIR` (예: `/.../projects/receipt-ledger/data`)

### 실행 순서
1. Build Variant를 `liveDebug`로 변경
2. Run
3. Upload 탭에서 파일 선택 후 `파일 분석 시작`
4. Review/Report 탭에서 후속 동작 검증

### 주의
- 현재 구현은 **개발/로컬 연동 샘플**입니다.
- 실기기 배포 앱에서는 Python 직접 실행 대신
  - 서버 API
  - Kotlin 이식
  - 별도 런타임 전략
  중 하나로 전환이 필요합니다.

---

## 3) flavor 전환 요약

`app/build.gradle.kts`

- `demo` flavor: `BuildConfig.USE_DEMO_PIPELINE = true`
- `live` flavor: `BuildConfig.USE_DEMO_PIPELINE = false`

`MainActivity`에서 `BuildConfig.USE_DEMO_PIPELINE` 값을 보고
`DemoLedgerPipeline` / `ProcessLedgerPipeline`를 선택합니다.

---

## 4) 포함된 주요 파일

- `app/src/main/java/com/receiptledger/MainActivity.kt`
- `app/src/main/java/com/receiptledger/ui/theme/Theme.kt`
- `app/src/main/java/com/receiptledger/ui/common/AppShell.kt`
- `app/src/main/java/com/receiptledger/ui/common/LedgerViewModel.kt`
- `app/src/main/java/com/receiptledger/ui/common/PipelineRunner.kt`
- `app/src/main/java/com/receiptledger/ui/upload/UploadScreen.kt`
- `app/src/main/java/com/receiptledger/ui/review/UncategorizedReviewScreen.kt`
- `app/src/main/java/com/receiptledger/ui/report/ReportScreen.kt`

---

## 5) 빠른 점검 체크리스트

- [ ] `demoDebug` Run 시 첫 화면 즉시 표시
- [ ] 업로드 탭/미분류 탭/리포트 탭 전환 정상
- [ ] `liveDebug`에서 환경변수 누락 시 명확한 에러 메시지 확인
- [ ] `liveDebug`에서 parser 연결 시 import/review/report 흐름 동작

---

## 참고
- 프로젝트 전체 로컬 실행/스모크 테스트: [`../LOCAL_RUN_GUIDE.md`](../LOCAL_RUN_GUIDE.md)
