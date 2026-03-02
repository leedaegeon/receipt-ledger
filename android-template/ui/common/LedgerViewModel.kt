package com.receiptledger.ui.common

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class LedgerViewModel(
    private val pipeline: LedgerPipeline,
    private val reviewFileGateway: ReviewFileGateway,
    private val savedStateHandle: SavedStateHandle,
) : ViewModel() {

    private val restoredRecentCategories: List<String> =
        savedStateHandle.get<ArrayList<String>>("recentCategories")?.toList().orEmpty()

    private val _uploadState = MutableStateFlow(UploadUiState())
    val uploadState: StateFlow<UploadUiState> = _uploadState.asStateFlow()

    private val _reviewState = MutableStateFlow(ReviewUiState())
    val reviewState: StateFlow<ReviewUiState> = _reviewState.asStateFlow()

    private val _reportState = MutableStateFlow(ReportUiState())
    val reportState: StateFlow<ReportUiState> = _reportState.asStateFlow()

    fun onFilePicked(uri: String, displayName: String?) {
        _uploadState.update {
            it.copy(
                pickedUri = uri,
                displayName = displayName,
                error = null,
            )
        }
        savedStateHandle["pickedUri"] = uri
        savedStateHandle["displayName"] = displayName
    }

    fun runImport(month: String, account: String) {
        val uri = uploadState.value.pickedUri ?: return
        viewModelScope.launch {
            _uploadState.update { it.copy(importing = true, error = null) }
            runCatching {
                pipeline.importStatement(
                    inputPath = uri,
                    month = month,
                    account = account,
                )
            }.onSuccess { result ->
                _uploadState.update { it.copy(importing = false, lastImport = result) }
                savedStateHandle["normalizedPath"] = result.normalizedPath
                prepareReviewTemplate(result.normalizedPath)
            }.onFailure { e ->
                _uploadState.update { it.copy(importing = false, error = e.message ?: "import failed") }
            }
        }
    }

    fun loadReviewTemplate(templatePath: String) {
        runCatching {
            reviewFileGateway.loadTemplate(templatePath)
        }.onSuccess { items ->
            _reviewState.value = ReviewUiState(
                templatePath = templatePath,
                items = items,
                recentCategories = restoredRecentCategories,
                pendingSelections = items.count { it.selectedCategory == null },
            )
        }.onFailure { e ->
            _reviewState.value = ReviewUiState(error = e.message ?: "template load failed")
        }
    }

    fun prepareReviewTemplate(normalizedPath: String) {
        viewModelScope.launch {
            _reviewState.update { it.copy(loading = true, error = null) }
            runCatching {
                pipeline.exportUncategorized(normalizedPath)
            }.onSuccess { tpl ->
                loadReviewTemplate(tpl.path)
                _reviewState.update { it.copy(loading = false) }
            }.onFailure {
                // 템플릿 I/O가 아직 연결되지 않은 환경을 위한 fallback
                seedReviewItemsForTemplate()
                _reviewState.update { it.copy(loading = false) }
            }
        }
    }

    /**
     * 템플릿 연결 전까지는 목데이터로 검수 화면 동작을 확인한다.
     */
    fun seedReviewItemsForTemplate() {
        _reviewState.value = ReviewUiState(
            items = listOf(
                UncategorizedItem(id = "1", merchant = "배달의민족", amount = 18500, date = "2026-03-01"),
                UncategorizedItem(id = "2", merchant = "스타벅스", amount = 6100, date = "2026-03-01"),
            ),
            recentCategories = restoredRecentCategories,
            pendingSelections = 2,
        )
    }

    fun onReviewCategorySelected(itemId: String, category: String) {
        _reviewState.update { state ->
            val updated = state.items.map { item ->
                if (item.id == itemId) item.copy(selectedCategory = category) else item
            }
            val recent = listOf(category) + state.recentCategories.filterNot { it == category }
            val trimmed = recent.take(5)
            savedStateHandle["recentCategories"] = ArrayList(trimmed)

            state.copy(
                items = updated,
                recentCategories = trimmed,
                pendingSelections = updated.count { it.selectedCategory == null },
                error = null,
            )
        }
    }

    fun saveReviewFeedback(normalizedPath: String, feedbackPath: String) {
        viewModelScope.launch {
            _reviewState.update { it.copy(saving = true, error = null) }
            runCatching {
                reviewFileGateway.writeFeedback(feedbackPath, _reviewState.value.items)
                pipeline.applyFeedback(normalizedPath, feedbackPath)
            }.onSuccess {
                _reviewState.update { it.copy(saving = false) }
            }.onFailure { e ->
                _reviewState.update { it.copy(saving = false, error = e.message ?: "feedback save failed") }
            }
        }
    }

    fun buildMonthlyReport(month: String, account: String) {
        val normalizedPath = uploadState.value.lastImport?.normalizedPath ?: return
        viewModelScope.launch {
            _reportState.update { it.copy(loading = true, error = null) }
            runCatching {
                pipeline.buildMonthlyReport(normalizedPath = normalizedPath, month = month, account = account)
            }.onSuccess { report ->
                _reportState.update { it.copy(loading = false, result = report) }
            }.onFailure { e ->
                _reportState.update { it.copy(loading = false, error = e.message ?: "report build failed") }
            }
        }
    }
}

/**
 * ViewModel Factory Note:
 * - Compose/NavGraph scope에서 동일 인스턴스를 쓰려면 owner(LocalViewModelStoreOwner/NavBackStackEntry) 고정 필요.
 * - SavedStateHandle 사용 시 CreationExtras 기반 create() 구현이 안전.
 */
class LedgerViewModelFactory(
    private val pipeline: LedgerPipeline,
    private val reviewFileGateway: ReviewFileGateway = ReviewFileGateway(),
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>, extras: androidx.lifecycle.CreationExtras): T {
        val savedStateHandle = androidx.lifecycle.SavedStateHandle.createHandle(extras, null)
        @Suppress("UNCHECKED_CAST")
        return LedgerViewModel(
            pipeline = pipeline,
            reviewFileGateway = reviewFileGateway,
            savedStateHandle = savedStateHandle,
        ) as T
    }
}
