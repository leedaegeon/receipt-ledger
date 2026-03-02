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
    private val savedStateHandle: SavedStateHandle,
) : ViewModel() {

    private val _uploadState = MutableStateFlow(UploadUiState())
    val uploadState: StateFlow<UploadUiState> = _uploadState.asStateFlow()

    private val _reviewState = MutableStateFlow(ReviewUiState())
    val reviewState: StateFlow<ReviewUiState> = _reviewState.asStateFlow()

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
            }.onFailure { e ->
                _uploadState.update { it.copy(importing = false, error = e.message ?: "import failed") }
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
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>, extras: androidx.lifecycle.CreationExtras): T {
        val savedStateHandle = androidx.lifecycle.SavedStateHandle.createHandle(extras, null)
        @Suppress("UNCHECKED_CAST")
        return LedgerViewModel(
            pipeline = pipeline,
            savedStateHandle = savedStateHandle,
        ) as T
    }
}
