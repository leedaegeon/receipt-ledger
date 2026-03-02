package com.receiptledger.ui.report

import androidx.compose.foundation.layout.*
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.receiptledger.ui.common.ReportSummary

@Composable
fun ReportScreen(
    summary: ReportSummary,
    uncategorizedCount: Int,
    onRefreshReport: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text("월간 리포트")
        Text("총수입: ${summary.totalIncome}")
        Text("총지출: ${summary.totalExpense}")
        Text("순현금흐름: ${summary.netCashflow}")
        Text("미분류 지출: $uncategorizedCount")
        Button(onClick = onRefreshReport) { Text("리포트 갱신") }
    }
}
