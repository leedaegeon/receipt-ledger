package com.receiptledger.ui.common

data class ImportResult(
    val normalizedPath: String,
    val invalidPath: String,
    val parsedCount: Int,
    val invalidCount: Int,
)

data class FeedbackTemplate(
    val path: String,
    val merchantCount: Int,
    val uncategorizedCount: Int,
)

data class ApplyResult(
    val updatedRules: Int,
    val recategorizedCount: Int,
    val rulesTotal: Int,
)

data class ReportSummary(
    val totalIncome: Long,
    val totalExpense: Long,
    val netCashflow: Long,
)

data class ReportResult(
    val reportPath: String,
    val summary: ReportSummary,
)

data class UploadUiState(
    val pickedUri: String? = null,
    val displayName: String? = null,
    val importing: Boolean = false,
    val lastImport: ImportResult? = null,
    val error: String? = null,
)

data class UncategorizedItem(
    val id: String,
    val merchant: String,
    val amount: Long,
    val date: String,
    val suggestedCategory: String? = null,
    val selectedCategory: String? = null,
)

data class ReviewUiState(
    val loading: Boolean = false,
    val templatePath: String? = null,
    val items: List<UncategorizedItem> = emptyList(),
    val recentCategories: List<String> = emptyList(),
    val saving: Boolean = false,
    val pendingSelections: Int = 0,
    val lastApplyResult: ApplyResult? = null,
    val error: String? = null,
)

data class ReportUiState(
    val loading: Boolean = false,
    val result: ReportResult? = null,
    val error: String? = null,
)
