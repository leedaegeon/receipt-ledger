package com.receiptledger.ui.common

import java.io.File

/** 템플릿 I/O 샘플. 실제 앱에서는 SAF/앱 전용 저장소 정책에 맞춰 교체. */
class ReviewFileGateway {

    fun loadTemplate(templatePath: String): List<UncategorizedItem> {
        val json = File(templatePath).readText()
        return FeedbackTemplateMapper.parseTemplate(json)
    }

    fun writeFeedback(feedbackPath: String, items: List<UncategorizedItem>) {
        val payload = FeedbackTemplateMapper.toApplyFeedbackJson(items)
        File(feedbackPath).writeText(payload)
    }
}
