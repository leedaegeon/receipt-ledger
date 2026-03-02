package com.receiptledger.ui.upload

import androidx.compose.foundation.layout.*
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun UploadScreen(
    onPickFile: () -> Unit,
    onRunImport: (month: String, account: String) -> Unit,
    importStatus: String,
) {
    var month by remember { mutableStateOf("2026-02") }
    var account by remember { mutableStateOf("토스뱅크") }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("업로드")
        Text("월: $month")
        Text("계좌: $account")
        Button(onClick = onPickFile) { Text("파일 선택") }
        Button(onClick = { onRunImport(month, account) }) { Text("파일 분석 시작") }
        Text("상태: $importStatus")
    }
}
