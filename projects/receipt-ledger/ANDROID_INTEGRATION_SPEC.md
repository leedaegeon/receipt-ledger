# Android 연동 스펙 (v0.1)

## 목표
파서 파이프라인(`run_import -> export_uncategorized -> apply_feedback -> monthly_report`)을
Android 앱 화면 3개(업로드/미분류/리포트)에 연결한다.

---

## 1) 화면 구조

### A. 업로드 화면
- 입력: PDF/CSV 파일 선택
- 액션: `run_import.py` 실행
- 출력:
  - `*.normalized.json`
  - `*.invalid.json`

### B. 미분류 검수 화면
- 데이터소스: normalized.json에서 `direction=expense && category=미분류`
- 액션:
  1) `export_uncategorized.py`로 템플릿 생성
  2) 사용자 카테고리 선택
  3) `apply_feedback.py` 호출
- 결과: `rules.json` 누적 + normalized.json 재분류

### C. 월간 리포트 화면
- 액션: `monthly_report.py`
- 출력: `*.report.json`
- 표시:
  - 총수입/총지출/순현금흐름
  - 카테고리 비중
  - 상위 지출
  - 고정비 후보

---

## 2) 앱 내부 인터페이스 (권장)

```kotlin
interface LedgerPipeline {
    suspend fun importStatement(inputPath: String, month: String, account: String): ImportResult
    suspend fun exportUncategorized(normalizedPath: String): FeedbackTemplate
    suspend fun applyFeedback(normalizedPath: String, feedbackPath: String): ApplyResult
    suspend fun buildMonthlyReport(normalizedPath: String, month: String, account: String): ReportResult
}
```

### DTO
- `ImportResult(normalizedPath, invalidPath, parsedCount, invalidCount)`
- `FeedbackTemplate(path, merchantCount, uncategorizedCount)`
- `ApplyResult(updatedRules, recategorizedCount, rulesTotal)`
- `ReportResult(reportPath, summary)`

---

## 3) 명령 실행 규칙

### Import
```bash
python3 run_import.py <input> --month <YYYY-MM> --account <name> --out-dir <dir>
```

### Export Uncategorized
```bash
python3 export_uncategorized.py <normalized.json> --out <feedback.template.json>
```

### Apply Feedback
```bash
python3 apply_feedback.py <normalized.json> <feedback.template.json>
```

### Monthly Report
```bash
python3 monthly_report.py <normalized.json> --month <YYYY-MM> --account <name>
```

---

## 4) 버튼 액션 매핑

- [파일 분석 시작]
  - importStatement
- [미분류 검수]
  - exportUncategorized
- [카테고리 저장]
  - applyFeedback
- [리포트 갱신]
  - buildMonthlyReport

---

## 5) 오류 처리 UX

- Import 실패: 파일 포맷 안내 + 재선택
- invalid row 존재: `invalid.json` 개수 배지 표시
- feedback 적용 실패: 실패 merchant 리스트 노출
- report 실패: 마지막 정상 report 캐시 표시

---

## 6) 성능 기준 (초기)

- 5,000행 기준 import 5초 이내 목표
- feedback 적용 1초 이내
- report 생성 1초 이내

---

## 7) 다음 단계

1. Kotlin에서 ProcessBuilder 래퍼 작성
2. JSON DTO 파서(Moshi/Kotlinx Serialization) 연결
3. 미분류 화면에서 일괄 분류 기능 추가
