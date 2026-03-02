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
    private val pythonBin: String = System.getenv("RECEIPT_LEDGER_PYTHON_BIN") ?: "python3",
    private val parserDir: File = File(
        System.getenv("RECEIPT_LEDGER_PARSER_DIR")
            ?: File(workspaceDir, "projects/receipt-ledger/parser").absolutePath,
    ),
    private val outDir: File = File(
        System.getenv("RECEIPT_LEDGER_DATA_DIR")
            ?: File(workspaceDir, "projects/receipt-ledger/data").absolutePath,
    ),
) : LedgerPipeline {

    init {
        validateEnvironment()
    }

    private fun validateEnvironment() {
        require(parserDir.exists() && parserDir.isDirectory) {
            "parserDir not found: ${parserDir.absolutePath} (set RECEIPT_LEDGER_PARSER_DIR)"
        }
        val requiredScripts = listOf(
            "run_import.py",
            "export_uncategorized.py",
            "apply_feedback.py",
            "monthly_report.py",
        )
        val missing = requiredScripts.filterNot { File(parserDir, it).exists() }
        require(missing.isEmpty()) {
            "missing parser scripts in ${parserDir.absolutePath}: ${missing.joinToString()}"
        }

        val probe = ProcessBuilder(pythonBin, "--version")
            .redirectErrorStream(true)
            .start()
        val output = probe.inputStream.bufferedReader().readText()
        val exit = probe.waitFor()
        require(exit == 0) {
            "python executable check failed: $pythonBin (set RECEIPT_LEDGER_PYTHON_BIN)\n$output"
        }
    }

    private fun requireReadableFile(path: String, label: String): File {
        val file = File(path)
        require(file.exists() && file.isFile && file.canRead()) {
            "$label file not readable: ${file.absolutePath}"
        }
        return file
    }

    private fun requireOutputFile(path: File, label: String): File {
        require(path.exists() && path.isFile) {
            "$label output not found: ${path.absolutePath}"
        }
        return path
    }

    private fun runCommand(vararg args: String): String {
        val script = args.firstOrNull()
        if (script != null) {
            require(File(parserDir, script).exists()) {
                "parser script not found: ${File(parserDir, script).absolutePath}"
            }
        }

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
            val input = requireReadableFile(inputPath, "input")
            runCommand(
                "run_import.py",
                input.absolutePath,
                "--month",
                month,
                "--account",
                account,
                "--out-dir",
                outDir.absolutePath,
            )

            val prefix = "${input.nameWithoutExtension}.$month"
            val normalized = requireOutputFile(File(outDir, "$prefix.normalized.json"), "normalized")
            val invalid = requireOutputFile(File(outDir, "$prefix.invalid.json"), "invalid")

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
        val normalized = requireReadableFile(normalizedPath, "normalized")
        val outPath = File(normalized.parentFile, "${normalized.nameWithoutExtension}.feedback.template.json")
        runCommand("export_uncategorized.py", normalized.absolutePath, "--out", outPath.absolutePath)
        requireOutputFile(outPath, "feedback template")

        val meta = JSONObject(outPath.readText()).optJSONObject("meta")
        FeedbackTemplate(
            path = outPath.absolutePath,
            merchantCount = meta?.optInt("unique_merchants", 0) ?: 0,
            uncategorizedCount = meta?.optInt("uncategorized_expense_count", 0) ?: 0,
        )
    }

    override suspend fun applyFeedback(normalizedPath: String, feedbackPath: String): ApplyResult = withContext(Dispatchers.IO) {
        val normalized = requireReadableFile(normalizedPath, "normalized")
        val feedback = requireReadableFile(feedbackPath, "feedback")
        val stdout = runCommand("apply_feedback.py", normalized.absolutePath, feedback.absolutePath)

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
            val normalized = requireReadableFile(normalizedPath, "normalized")
            val outPath = File(normalized.parentFile, "${normalized.nameWithoutExtension}.report.json")
            runCommand(
                "monthly_report.py",
                normalized.absolutePath,
                "--month",
                month,
                "--account",
                account,
                "--out",
                outPath.absolutePath,
            )

            requireOutputFile(outPath, "report")
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
