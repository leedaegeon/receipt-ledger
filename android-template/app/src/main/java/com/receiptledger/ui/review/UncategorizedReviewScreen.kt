package com.receiptledger.ui.review

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.receiptledger.ui.common.UncategorizedItem

@Composable
fun UncategorizedReviewScreen(
    items: List<UncategorizedItem>,
    onPickCategory: (UncategorizedItem, String) -> Unit,
    onApplyFeedback: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("미분류 검수")
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.weight(1f)) {
            items(items) { item ->
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${item.merchantName} (${item.count})")
                    Button(onClick = { onPickCategory(item, "식비") }) { Text(if (item.category.isBlank()) "카테고리 선택" else item.category) }
                }
            }
        }
        Button(onClick = onApplyFeedback) { Text("카테고리 저장/재분류") }
    }
}
