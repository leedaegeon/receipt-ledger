package com.receiptledger.ui.report

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.receiptledger.ui.common.ReportResult
import com.receiptledger.ui.common.SampleData

@Composable
fun ReportScreen(
    report: ReportResult?,
    loading: Boolean,
    error: String?,
    onBuildReport: () -> Unit,
) {
    Column(
        modifier = Modifier.padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Button(
            modifier = Modifier.fillMaxWidth(),
            enabled = !loading,
            onClick = onBuildReport,
        ) {
            Text(if (loading) "리포트 생성 중..." else "리포트 갱신")
        }

        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }

        if (report == null) {
            Text("아직 생성된 리포트가 없습니다.")
            return
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("리포트 파일: ${report.reportPath}", style = MaterialTheme.typography.bodySmall)
                Text("총수입: ${report.summary.totalIncome}원")
                Text("총지출: ${report.summary.totalExpense}원")
                Text("순현금흐름: ${report.summary.netCashflow}원")
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
private fun ReportScreenPreview() {
    ReportScreen(
        report = SampleData.previewReportResult,
        loading = false,
        error = null,
        onBuildReport = {},
    )
}
