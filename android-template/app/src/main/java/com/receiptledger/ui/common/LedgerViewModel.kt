package com.receiptledger.ui.common

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.io.File

data class LedgerUiState(
    val importStatus: String = "대기중",
    val normalizedPath: String = "",
    val feedbackPath: String = "",
    val uncategorizedItems: List<UncategorizedItem> = emptyList(),
    val reportSummary: ReportSummary = ReportSummary(0, 0, 0),
    val uncategorizedCount: Int = 0,
    val error: String? = null,
)

class LedgerViewModel(
    private val runner: PipelineRunner,
    private val outDir: File,
) : ViewModel() {

    private val _ui = MutableStateFlow(LedgerUiState())
    val ui: StateFlow<LedgerUiState> = _ui.asStateFlow()

    fun importStatement(inputPath: String, month: String, account: String) {
        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                _ui.value = _ui.value.copy(importStatus = "분석 중...", error = null)
                runner.importStatement(inputPath, month, account, outDir.absolutePath)
            }.onSuccess { r ->
                _ui.value = _ui.value.copy(
                    importStatus = "완료 (parsed=${r.parsedCount}, invalid=${r.invalidCount})",
                    normalizedPath = r.normalizedPath,
                )
                refreshReport(month, account)
            }.onFailure { e ->
                _ui.value = _ui.value.copy(importStatus = "실패", error = e.message)
            }
        }
    }

    fun loadUncategorized() {
        val normalized = _ui.value.normalizedPath
        if (normalized.isBlank()) return

        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                val feedbackPath = runner.exportUncategorized(normalized)
                val obj = JSONObject(File(feedbackPath).readText())
                val arr = obj.getJSONArray("items")
                val items = buildList {
                    for (i in 0 until arr.length()) {
                        val it = arr.getJSONObject(i)
                        add(
                            UncategorizedItem(
                                merchantName = it.optString("merchant_name"),
                                normalizedMerchantName = it.optString("normalized_merchant_name"),
                                count = it.optInt("count", 1),
                                category = it.optString("category"),
                            )
                        )
                    }
                }
                feedbackPath to items
            }.onSuccess { (path, items) ->
                _ui.value = _ui.value.copy(feedbackPath = path, uncategorizedItems = items, error = null)
            }.onFailure { e ->
                _ui.value = _ui.value.copy(error = e.message)
            }
        }
    }

    fun setCategory(item: UncategorizedItem, category: String) {
        val updated = _ui.value.uncategorizedItems.map {
            if (it.normalizedMerchantName == item.normalizedMerchantName) it.copy(category = category) else it
        }
        _ui.value = _ui.value.copy(uncategorizedItems = updated)
    }

    fun applyFeedback(month: String, account: String) {
        val normalized = _ui.value.normalizedPath
        val feedbackPath = _ui.value.feedbackPath
        if (normalized.isBlank() || feedbackPath.isBlank()) return

        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                val fp = File(feedbackPath)
                val obj = JSONObject(fp.readText())
                val arr = obj.getJSONArray("items")
                val mapped = _ui.value.uncategorizedItems.associateBy { it.normalizedMerchantName }
                for (i in 0 until arr.length()) {
                    val row = arr.getJSONObject(i)
                    val key = row.optString("normalized_merchant_name")
                    val chosen = mapped[key]?.category ?: ""
                    row.put("category", chosen)
                }
                fp.writeText(obj.toString(2))
                runner.applyFeedback(normalized, feedbackPath)
            }.onSuccess {
                refreshReport(month, account)
                loadUncategorized()
            }.onFailure { e ->
                _ui.value = _ui.value.copy(error = e.message)
            }
        }
    }

    fun refreshReport(month: String, account: String) {
        val normalized = _ui.value.normalizedPath
        if (normalized.isBlank()) return

        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                val reportPath = runner.buildReport(normalized, month, account)
                val rep = JSONObject(File(reportPath).readText())
                val summary = rep.getJSONObject("summary")
                val unc = rep.getJSONObject("uncategorized").optInt("count", 0)
                ReportSummary(
                    totalIncome = summary.optLong("total_income", 0),
                    totalExpense = summary.optLong("total_expense", 0),
                    netCashflow = summary.optLong("net_cashflow", 0),
                ) to unc
            }.onSuccess { (sum, unc) ->
                _ui.value = _ui.value.copy(reportSummary = sum, uncategorizedCount = unc, error = null)
            }.onFailure { e ->
                _ui.value = _ui.value.copy(error = e.message)
            }
        }
    }
}