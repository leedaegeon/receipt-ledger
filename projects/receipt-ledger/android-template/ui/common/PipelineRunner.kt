package com.receiptledger.ui.common

interface LedgerPipeline {
    suspend fun importStatement(inputPath: String, month: String, account: String): ImportResult
    suspend fun exportUncategorized(normalizedPath: String): FeedbackTemplate
    suspend fun applyFeedback(normalizedPath: String, feedbackPath: String): ApplyResult
    suspend fun buildMonthlyReport(normalizedPath: String, month: String, account: String): ReportResult
}

/**
 * NOTE:
 * - Concept template only.
 * - Android production apps usually cannot execute host python directly.
 * - Replace with Kotlin port / server API / embedded runtime strategy.
 */
class StubLedgerPipeline : LedgerPipeline {
    override suspend fun importStatement(inputPath: String, month: String, account: String): ImportResult {
        return ImportResult(
            normalizedPath = "data/$month.normalized.json",
            invalidPath = "data/$month.invalid.json",
            parsedCount = 0,
            invalidCount = 0,
        )
    }

    override suspend fun exportUncategorized(normalizedPath: String): FeedbackTemplate {
        return FeedbackTemplate(
            path = normalizedPath.replace(".normalized.json", ".feedback.template.json"),
            merchantCount = 0,
            uncategorizedCount = 0,
        )
    }

    override suspend fun applyFeedback(normalizedPath: String, feedbackPath: String): ApplyResult {
        return ApplyResult(updatedRules = 0, recategorizedCount = 0, rulesTotal = 0)
    }

    override suspend fun buildMonthlyReport(normalizedPath: String, month: String, account: String): ReportResult {
        return ReportResult(
            reportPath = normalizedPath.replace(".normalized.json", ".report.json"),
            summary = ReportSummary(0, 0, 0),
        )
    }
}
