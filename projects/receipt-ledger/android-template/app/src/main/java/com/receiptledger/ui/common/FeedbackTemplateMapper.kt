package com.receiptledger.ui.common

import org.json.JSONArray
import org.json.JSONObject

/**
 * parser/export_uncategorized.py 결과(JSON)를 앱 상태로 매핑하고,
 * 선택된 카테고리를 parser/apply_feedback.py 입력 스키마로 직렬화한다.
 */
object FeedbackTemplateMapper {

    fun parseTemplate(json: String): List<UncategorizedItem> {
        val root = JSONObject(json)
        val items = root.optJSONArray("items") ?: JSONArray()
        return buildList {
            for (i in 0 until items.length()) {
                val it = items.optJSONObject(i) ?: continue
                val normalized = it.optString("normalized_merchant_name").takeIf { s -> s.isNotBlank() }
                val merchant = it.optString("merchant_name").ifBlank { normalized ?: "(unknown)" }
                val id = normalized ?: merchant
                add(
                    UncategorizedItem(
                        id = id,
                        merchant = merchant,
                        amount = 0L,
                        date = "",
                        selectedCategory = it.optString("category").takeIf { s -> s.isNotBlank() },
                    ),
                )
            }
        }
    }

    /**
     * apply_feedback.py schema:
     * {
     *   "items": [
     *     {"merchant_name": "...", "normalized_merchant_name": "...", "category": "식비"}
     *   ]
     * }
     */
    fun toApplyFeedbackJson(items: List<UncategorizedItem>): String {
        val arr = JSONArray()
        items.forEach { item ->
            val category = item.selectedCategory?.trim().orEmpty()
            if (category.isBlank()) return@forEach
            arr.put(
                JSONObject()
                    .put("merchant_name", item.merchant)
                    .put("normalized_merchant_name", item.id)
                    .put("category", category),
            )
        }
        return JSONObject().put("items", arr).toString(2)
    }
}
