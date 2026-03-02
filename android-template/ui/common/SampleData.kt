package com.receiptledger.ui.common

object SampleData {
    val previewImportResult = ImportResult(
        normalizedPath = "/tmp/receipt-ledger/preview.2026-03.normalized.json",
        invalidPath = "/tmp/receipt-ledger/preview.2026-03.invalid.json",
        parsedCount = 36,
        invalidCount = 1,
    )

    val previewReviewItems = listOf(
        UncategorizedItem(id = "baemin", merchant = "배달의민족", amount = 18500, date = "2026-03-01"),
        UncategorizedItem(id = "starbucks", merchant = "스타벅스", amount = 6100, date = "2026-03-01"),
        UncategorizedItem(id = "oliveyoung", merchant = "올리브영", amount = 23900, date = "2026-03-02", suggestedCategory = "생활"),
    )

    val previewRecentCategories = listOf("식비", "카페", "생활")

    val previewReportResult = ReportResult(
        reportPath = "/tmp/receipt-ledger/preview.2026-03.report.json",
        summary = ReportSummary(
            totalIncome = 3_250_000,
            totalExpense = 1_980_500,
            netCashflow = 1_269_500,
        ),
    )
}

/**
 * Android Studio Preview/Template 데모용 파이프라인.
 * 외부 Python 실행 없이 즉시 UI 상태를 확인할 수 있다.
 */
class DemoLedgerPipeline : LedgerPipeline {
    override suspend fun importStatement(inputPath: String, month: String, account: String): ImportResult {
        return SampleData.previewImportResult
    }

    override suspend fun exportUncategorized(normalizedPath: String): FeedbackTemplate {
        return FeedbackTemplate(
            path = "/tmp/receipt-ledger/preview.feedback.template.json",
            merchantCount = 3,
            uncategorizedCount = 3,
        )
    }

    override suspend fun applyFeedback(normalizedPath: String, feedbackPath: String): ApplyResult {
        return ApplyResult(
            updatedRules = 2,
            recategorizedCount = 3,
            rulesTotal = 17,
        )
    }

    override suspend fun buildMonthlyReport(normalizedPath: String, month: String, account: String): ReportResult {
        return SampleData.previewReportResult
    }
}
