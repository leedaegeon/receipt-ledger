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
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.receiptledger.ui.common.SampleData
import com.receiptledger.ui.common.UploadUiState

interface UploadActions {
    fun onFilePicked(uri: String, displayName: String?)
}

@Composable
fun UploadScreen(
    state: UploadUiState,
    actions: UploadActions,
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
            actions.onFilePicked(uri.toString(), displayName)
        }
    }

    UploadScreenContent(
        state = state,
        onPickFile = {
            pickerLauncher.launch(arrayOf("application/pdf", "text/*", "application/vnd.ms-excel"))
        },
        onStartImport = onStartImport,
    )
}

@Composable
fun UploadScreenContent(
    state: UploadUiState,
    onPickFile: () -> Unit,
    onStartImport: () -> Unit,
) {
    Column(
        modifier = Modifier.padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Button(
            modifier = Modifier.fillMaxWidth(),
            onClick = onPickFile,
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

        state.lastImport?.let {
            Text(
                text = "분석 완료: ${it.parsedCount}건 / invalid ${it.invalidCount}건",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.primary,
            )
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

@Preview(showBackground = true)
@Composable
private fun UploadScreenContentPreview() {
    UploadScreenContent(
        state = UploadUiState(
            pickedUri = "content://preview/sample.pdf",
            displayName = "sample_tossbank_statement.pdf",
            lastImport = SampleData.previewImportResult,
        ),
        onPickFile = {},
        onStartImport = {},
    )
}
