package com.receiptledger.ui.upload

import android.net.Uri
import android.provider.OpenableColumns
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.receiptledger.ui.common.LedgerViewModel
import com.receiptledger.ui.common.UploadUiState

@Composable
fun UploadScreen(
    state: UploadUiState,
    viewModel: LedgerViewModel,
    onStartImport: () -> Unit,
) {
    val context = LocalContext.current

    val pickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument(),
    ) { uri: Uri? ->
        if (uri != null) {
            context.contentResolver.takePersistableUriPermission(
                uri,
                android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION,
            )
            val displayName = queryDisplayName(context, uri)
            viewModel.onFilePicked(uri.toString(), displayName)
        }
    }

    Column(
        modifier = Modifier.padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Button(
            modifier = Modifier.fillMaxWidth(),
            onClick = {
                pickerLauncher.launch(arrayOf("application/pdf", "text/*", "application/vnd.ms-excel"))
            },
        ) {
            Text("명세서 파일 선택")
        }

        Text(
            text = state.displayName ?: "선택된 파일 없음",
            style = MaterialTheme.typography.bodyMedium,
        )

        Button(
            modifier = Modifier.fillMaxWidth(),
            enabled = state.pickedUri != null && !state.importing,
            onClick = onStartImport,
        ) {
            Text(if (state.importing) "분석 중..." else "파일 분석 시작")
        }

        state.error?.let {
            Text(text = it, color = MaterialTheme.colorScheme.error)
        }
    }
}

private fun queryDisplayName(context: android.content.Context, uri: Uri): String? {
    return context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
        val idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
        if (idx >= 0 && cursor.moveToFirst()) cursor.getString(idx) else null
    }
}
