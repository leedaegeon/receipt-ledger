package com.receiptledger.ui.common

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.receiptledger.ui.report.ReportScreen
import com.receiptledger.ui.review.UncategorizedReviewScreen
import com.receiptledger.ui.upload.UploadScreen

@Composable
fun AppShell(
    vm: LedgerViewModel,
    pickedFilePath: String,
    onPickFile: () -> Unit,
) {
    val ui by vm.ui.collectAsState()
    var tab by remember { mutableStateOf(0) }
    val month = "2026-02"
    val account = "토스뱅크"

    Column(modifier = Modifier.fillMaxSize()) {
        TabRow(selectedTabIndex = tab) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("업로드") })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("미분류") })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("리포트") })
        }

        when (tab) {
            0 -> UploadScreen(
                onPickFile = onPickFile,
                onRunImport = { m, a -> vm.importStatement(pickedFilePath, m, a) },
                importStatus = ui.importStatus,
            )

            1 -> UncategorizedReviewScreen(
                items = ui.uncategorizedItems,
                onPickCategory = { item, category -> vm.setCategory(item, category) },
                onApplyFeedback = { vm.applyFeedback(month, account) },
            )

            2 -> ReportScreen(
                summary = ui.reportSummary,
                uncategorizedCount = ui.uncategorizedCount,
                onRefreshReport = { vm.refreshReport(month, account) },
            )
        }
    }
}
