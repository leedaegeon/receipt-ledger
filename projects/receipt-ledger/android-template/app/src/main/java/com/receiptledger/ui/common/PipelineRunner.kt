package com.receiptledger.ui.common

import org.json.JSONObject
import java.io.File

class PipelineRunner(
    private val workingDir: File,
    private val pythonBin: String = "python3",
    private val parserDir: File = File(workingDir, "projects/receipt-ledger/parser"),
) {

    private fun run(vararg args: String): String {
        val pb = ProcessBuilder(listOf(pythonBin) + args.toList())
            .directory(parserDir)
            .redirectErrorStream(true)
        val p = pb.start()
        val out = p.inputStream.bufferedReader().readText()
        val code = p.waitFor()
        if (code != 0) error("Command failed($code): ${args.joinToString(" ")}\n$out")
        return out
    }

    fun importStatement(inputPath: String, month: String, account: String, outDir: String): ImportResult {
        run("run_import.py", inputPath, "--month", month, "--account", account, "--out-dir", outDir)

        val input = File(inputPath)
        val prefix = "${input.nameWithoutExtension}.$month"
        val normalized = File(outDir, "$prefix.normalized.json")
        val invalid = File(outDir, "$prefix.invalid.json")

        val invalidObj = JSONObject(invalid.readText())
        val invalidCount = invalidObj.getJSONObject("meta").optInt("count", 0)

        val normalizedArr = org.json.JSONArray(normalized.readText())
        return ImportResult(
            normalizedPath = normalized.absolutePath,
            invalidPath = invalid.absolutePath,
            parsedCount = normalizedArr.length(),
            invalidCount = invalidCount,
        )
    }

    fun exportUncategorized(normalizedPath: String): String {
        run("export_uncategorized.py", normalizedPath)
        val p = File(normalizedPath)
        return File(p.parentFile, "${p.nameWithoutExtension}.feedback.template.json").absolutePath
    }

    fun applyFeedback(normalizedPath: String, feedbackPath: String): String {
        return run("apply_feedback.py", normalizedPath, feedbackPath)
    }

    fun buildReport(normalizedPath: String, month: String, account: String): String {
        run("monthly_report.py", normalizedPath, "--month", month, "--account", account)
        val p = File(normalizedPath)
        return File(p.parentFile, "${p.nameWithoutExtension}.report.json").absolutePath
    }
}