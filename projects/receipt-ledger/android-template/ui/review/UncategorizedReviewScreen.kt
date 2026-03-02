package com.receiptledger.ui.review

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.receiptledger.ui.common.ReviewUiState
import com.receiptledger.ui.common.SampleData
import com.receiptledger.ui.common.UncategorizedItem

@Composable
fun UncategorizedReviewScreen(
    state: ReviewUiState,
    categories: List<String>,
    onItemCategorySelected: (itemId: String, category: String) -> Unit,
    onSaveFeedback: () -> Unit,
) {
    var selectedItem by remember { mutableStateOf<UncategorizedItem?>(null) }

    Column(
        modifier = Modifier.padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Row(modifier = Modifier.fillMaxWidth()) {
            Text(
                text = "미분류 ${state.items.size}건",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.weight(1f),
            )
            Button(onClick = onSaveFeedback, enabled = !state.saving) {
                Text(if (state.saving) "저장 중..." else "카테고리 저장")
            }
        }

        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(state.items, key = { it.id }) { item ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { selectedItem = item },
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(item.merchant, style = MaterialTheme.typography.bodyLarge)
                        Text("${item.date} · ${item.amount}원", style = MaterialTheme.typography.bodySmall)
                        Text(
                            text = "선택: ${item.selectedCategory ?: "미선택"}",
                            style = MaterialTheme.typography.bodySmall,
                            color = if (item.selectedCategory == null) {
                                MaterialTheme.colorScheme.error
                            } else {
                                MaterialTheme.colorScheme.primary
                            },
                        )
                    }
                }
            }
        }

        state.lastApplyResult?.let { result ->
            Text(
                text = "저장 완료 · 규칙 ${result.updatedRules}개 반영 / 재분류 ${result.recategorizedCount}건 (총 규칙 ${result.rulesTotal})",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.primary,
            )
        }

        state.error?.let {
            Text(text = it, color = MaterialTheme.colorScheme.error)
        }
    }

    selectedItem?.let { item ->
        CategorySelectionDialog(
            merchant = item.merchant,
            amountLabel = "${item.amount}원",
            categories = categories,
            recentCategories = state.recentCategories,
            currentSelection = item.selectedCategory,
            onSelect = { category ->
                onItemCategorySelected(item.id, category)
                selectedItem = null
            },
            onDismiss = { selectedItem = null },
        )
    }
}

@Preview(showBackground = true)
@Composable
private fun UncategorizedReviewScreenPreview() {
    UncategorizedReviewScreen(
        state = ReviewUiState(
            items = SampleData.previewReviewItems,
            recentCategories = SampleData.previewRecentCategories,
            pendingSelections = 2,
        ),
        categories = listOf("식비", "카페", "생활", "쇼핑", "교통", "주거/통신"),
        onItemCategorySelected = { _, _ -> },
        onSaveFeedback = {},
    )
}
