package com.receiptledger.ui.review

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun CategorySelectionDialog(
    merchant: String,
    amountLabel: String,
    categories: List<String>,
    recentCategories: List<String> = emptyList(),
    currentSelection: String?,
    onSelect: (String) -> Unit,
    onDismiss: () -> Unit,
) {
    var query by remember { mutableStateOf("") }
    val filtered = categories.filter { it.contains(query, ignoreCase = true) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("카테고리 선택") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("가맹점: $merchant", style = MaterialTheme.typography.bodyMedium)
                Text("금액: $amountLabel", style = MaterialTheme.typography.bodySmall)

                OutlinedTextField(
                    value = query,
                    onValueChange = { query = it },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    label = { Text("카테고리 검색") },
                )

                if (recentCategories.isNotEmpty() && query.isBlank()) {
                    Text("최근 사용", style = MaterialTheme.typography.labelMedium)
                    recentCategories.forEach { category ->
                        val selected = category == currentSelection
                        Text(
                            text = if (selected) "✓ $category" else category,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { onSelect(category) }
                                .padding(vertical = 8.dp),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                    HorizontalDivider()
                }

                LazyColumn {
                    items(filtered) { category ->
                        val selected = category == currentSelection
                        Text(
                            text = if (selected) "✓ $category" else category,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { onSelect(category) }
                                .padding(vertical = 10.dp),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) { Text("닫기") }
        },
    )
}
