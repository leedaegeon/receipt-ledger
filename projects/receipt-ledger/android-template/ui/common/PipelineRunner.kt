package com.receiptledger.ui.common

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

interface LedgerPipeline {
    suspend fun importStatement(inputPath: String, month: String, account: String): ImportResult
    suspend fun exportUncategorized(normalizedPath: String): FeedbackTemplate
    suspend fun applyFeedback(normalizedPath: String, feedbackPath: String): ApplyResult
    suspend fun buildMonthlyReport(normalizedPath: String, month: String, account: String): ReportResult
}

/**
 * parser/*.py를 실제로 호출하는 실행 계층.
 * - 데모/개발 환경(로컬 JVM) 기준 구현
 * - Android 실기기 배포 시에는 서버 API 또는 Kotlin 이식으로 교체 필요
 */
class ProcessLedgerPipeline(
    private val workspaceDir: File = File(System.getProperty("user.dir")),
    private val pythonBin: String = "python3",
    private val parserDir: File = File(workspaceDir, "projects/receipt-ledger/parser"),
    private val outDir: File = File(workspaceDir, "projects/receipt-ledger/data"),
) : LedgerPipeline {

    private fun runCommand(vararg args: String): String {
        val pb = ProcessBuilder(listOf(pythonBin) + args.toList())
            .directory(parserDir)
            .redirectErrorStream(true)
        val proc = pb.start()
        val output = proc.inputStream.bufferedReader().readText()
        val exit = proc.waitFor()
        if (exit != 0) {
            error("pipeline command failed($exit): ${args.joinToString(" ")}\n$output")
        }
        return output
    }

    override suspend fun importStatement(inputPath: String, month: String, account: String): ImportResult =
        withContext(Dispatchers.IO) {
            outDir.mkdirs()
            runCommand(
                "run_import.py",
                inputPath,
                "--month",
                month,
                "--account",
                account,
                "--out-dir",
                outDir.absolutePath,
            )

            val input = File(inputPath)
            val prefix = "${input.nameWithoutExtension}.$month"
            val normalized = File(outDir, "$prefix.normalized.json")
            val invalid = File(outDir, "$prefix.invalid.json")

            val parsedCount = JSONArray(normalized.readText()).length()
            val invalidCount = JSONObject(invalid.readText())
                .optJSONObject("meta")
                ?.optInt("count", 0)
                ?: 0

            ImportResult(
                normalizedPath = normalized.absolutePath,
                invalidPath = invalid.absolutePath,
                parsedCount = parsedCount,
                invalidCount = invalidCount,
            )
        }

    override suspend fun exportUncategorized(normalizedPath: String): FeedbackTemplate = withContext(Dispatchers.IO) {
        val normalized = File(normalizedPath)
        val outPath = File(normalized.parentFile, "${normalized.nameWithoutExtension}.feedback.template.json")
        runCommand("export_uncategorized.py", normalizedPath, "--out", outPath.absolutePath)

        val meta = JSONObject(outPath.readText()).optJSONObject("meta")
        FeedbackTemplate(
            path = outPath.absolutePath,
            merchantCount = meta?.optInt("unique_merchants", 0) ?: 0,
            uncategorizedCount = meta?.optInt("uncategorized_expense_count", 0) ?: 0,
        )
    }

    override suspend fun applyFeedback(normalizedPath: String, feedbackPath: String): ApplyResult = withContext(Dispatchers.IO) {
        val stdout = runCommand("apply_feedback.py", normalizedPath, feedbackPath)

        fun metric(name: String): Int {
            val line = stdout.lineSequence().firstOrNull { it.startsWith("$name=") } ?: return 0
            return line.substringAfter("=").trim().toIntOrNull() ?: 0
        }

        ApplyResult(
            updatedRules = metric("rules_updated"),
            recategorizedCount = metric("recategorized"),
            rulesTotal = metric("rules_total"),
        )
    }

    override suspend fun buildMonthlyReport(normalizedPath: String, month: String, account: String): ReportResult =
        withContext(Dispatchers.IO) {
            val normalized = File(normalizedPath)
            val outPath = File(normalized.parentFile, "${normalized.nameWithoutExtension}.report.json")
            runCommand(
                "monthly_report.py",
                normalizedPath,
                "--month",
                month,
                "--account",
                account,
                "--out",
                outPath.absolutePath,
            )

            val summary = JSONObject(outPath.readText()).getJSONObject("summary")
            ReportResult(
                reportPath = outPath.absolutePath,
                summary = ReportSummary(
                    totalIncome = summary.optLong("total_income", 0),
                    totalExpense = summary.optLong("total_expense", 0),
                    netCashflow = summary.optLong("net_cashflow", 0),
                ),
            )
        }
}
