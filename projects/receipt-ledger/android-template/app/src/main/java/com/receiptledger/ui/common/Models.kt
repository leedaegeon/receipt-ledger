package com.receiptledger.ui.common

data class ImportResult(
    val normalizedPath: String,
    val invalidPath: String,
    val parsedCount: Int,
    val invalidCount: Int,
)

data class ReportSummary(
    val totalIncome: Long,
    val totalExpense: Long,
    val netCashflow: Long,
)

data class UncategorizedItem(
    val merchantName: String,
    val normalizedMerchantName: String,
    val count: Int,
    var category: String = "",
)
