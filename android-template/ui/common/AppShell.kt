package com.receiptledger.ui.common

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import com.receiptledger.ui.report.ReportScreen
import com.receiptledger.ui.review.UncategorizedReviewScreen
import com.receiptledger.ui.upload.UploadScreen

private enum class Tab(val label: String) {
    Upload("업로드"),
    Review("미분류"),
    Report("리포트"),
}

/**
 * 통합 검증용 샘플 셸.
 * 실제 앱에서는 NavHost + DI로 치환 권장.
 */
@Composable
fun AppShell(viewModel: LedgerViewModel) {
    var tab by remember { mutableStateOf(Tab.Upload) }

    val uploadState by viewModel.uploadState.collectAsState()
    val reviewState by viewModel.reviewState.collectAsState()
    val reportState by viewModel.reportState.collectAsState()

    LaunchedEffect(uploadState.lastImport?.normalizedPath) {
        if (uploadState.lastImport != null) {
            tab = Tab.Review
        }
    }

    Scaffold(
        bottomBar = {
            NavigationBar {
                Tab.entries.forEach { t ->
                    NavigationBarItem(
                        selected = tab == t,
                        onClick = { tab = t },
                        label = { Text(t.label) },
                        icon = {},
                    )
                }
            }
        },
    ) { innerPadding ->
        when (tab) {
            Tab.Upload -> UploadScreen(
                state = uploadState,
                viewModel = viewModel,
                onStartImport = { viewModel.runImport(month = "2026-03", account = "tossbank") },
            )

            Tab.Review -> UncategorizedReviewScreen(
                state = reviewState,
                categories = listOf("식비", "카페", "생활", "쇼핑", "교통", "주거/통신"),
                onItemCategorySelected = viewModel::onReviewCategorySelected,
                onSaveFeedback = {
                    val normalized = uploadState.lastImport?.normalizedPath ?: return@UncategorizedReviewScreen
                    val feedbackPath = normalized.replace(".normalized.json", ".feedback.template.json")
                    viewModel.saveReviewFeedback(normalizedPath = normalized, feedbackPath = feedbackPath)
                },
            )

            Tab.Report -> ReportScreen(
                report = reportState.result,
                loading = reportState.loading,
                error = reportState.error,
                onBuildReport = { viewModel.buildMonthlyReport(month = "2026-03", account = "tossbank") },
            )
        }
    }
}
