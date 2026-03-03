import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + ("\n" + p.stderr if p.stderr else "")


def assert_contains(text: str, needle: str, label: str):
    if needle not in text:
        raise AssertionError(f"[{label}] expected '{needle}' in output, got:\n{text}")


def parse_args():
    ap = argparse.ArgumentParser(description="Receipt-ledger QA smoke runner")
    ap.add_argument("--suite", choices=["all", "benchmark", "exceptions"], default="all")
    ap.add_argument("--report-json", default=None, help="Optional path to save suite/case pass-fail report")
    ap.add_argument("--max-failures", type=int, default=0, help="Allowed failure count before non-zero exit")
    ap.add_argument("--smoke-escalate-threshold", type=int, default=3, help="Metadata: threshold used to escalate recurring smoke issues")
    return ap.parse_args()


def _case(label: str, fn, results: list[dict]):
    try:
        fn()
        results.append({"label": label, "pass": True, "error": None})
    except Exception as e:
        results.append({"label": label, "pass": False, "error": str(e)})


def run_benchmark_suite(parser_dir: Path) -> list[dict]:
    results: list[dict] = []

    def _benchmark():
        rc, out = run(
            [
                sys.executable,
                "benchmark_pipeline.py",
                "--rows",
                "5000",
                "--repeats",
                "1",
                "--fail-on-target",
                "--out",
                "../data/benchmark_pipeline_result.json",
            ],
            parser_dir,
        )
        if rc != 0:
            raise AssertionError(f"[benchmark] failed\n{out}")
        assert_contains(out, "pipeline_total_avg_sec", "benchmark")
        assert_contains(out, "overall: PASS", "benchmark")

    _case("benchmark-5000", _benchmark, results)
    return results


def run_exception_suite(parser_dir: Path) -> list[dict]:
    fixtures = parser_dir / "fixtures"
    results: list[dict] = []

    def _empty_json():
        empty = fixtures / "empty.json"
        rc, out = run([sys.executable, "monthly_report.py", str(empty)], parser_dir)
        if rc == 0:
            raise AssertionError("[empty-json] expected failure")
        assert_contains(out, "입력 JSON 파일이 비어 있습니다", "empty-json")

    def _broken_json():
        broken = fixtures / "broken.json"
        rc, out = run([sys.executable, "export_uncategorized.py", str(broken)], parser_dir)
        if rc == 0:
            raise AssertionError("[broken-json] expected failure")
        assert_contains(out, "손상된 JSON 형식입니다", "broken-json")

    def _missing_header():
        bad_csv = fixtures / "missing_header.csv"
        rc, out = run([sys.executable, "run_import.py", str(bad_csv)], parser_dir)
        if rc == 0:
            raise AssertionError("[missing-header] expected failure")
        assert_contains(out, "필수 헤더 누락", "missing-header")

    def _invalid_option():
        sample_csv = parser_dir.parent / "data" / "sample_tossbank.csv"
        rc, out = run(
            [sys.executable, "run_import.py", str(sample_csv), "--fixed-cost-min-months", "0"],
            parser_dir,
        )
        if rc == 0:
            raise AssertionError("[invalid-option] expected failure")
        assert_contains(out, "--fixed-cost-min-months 는 1 이상", "invalid-option")

    def _bad_feedback():
        normalized = fixtures / "minimal.normalized.json"
        bad_feedback = fixtures / "bad_feedback.json"
        rc, out = run([sys.executable, "apply_feedback.py", str(normalized), str(bad_feedback)], parser_dir)
        if rc == 0:
            raise AssertionError("[bad-feedback] expected failure")
        assert_contains(out, "feedback items의 모든 항목은 객체(dict)", "bad-feedback")

    def _encoding_csv():
        cp949_csv = fixtures / "cp949.csv"
        rc, out = run([sys.executable, "run_import.py", str(cp949_csv)], parser_dir)
        if rc == 0:
            raise AssertionError("[encoding-csv] expected failure")
        assert_contains(out, "인코딩 오류", "encoding-csv")

    def _empty_csv():
        empty_csv = fixtures / "empty.csv"
        rc, out = run([sys.executable, "run_import.py", str(empty_csv)], parser_dir)
        if rc == 0:
            raise AssertionError("[empty-csv] expected failure")
        assert_contains(out, "CSV 파일이 비어 있습니다", "empty-csv")

    def _bad_quoted_csv():
        bad_quoted = fixtures / "bad_quoted.csv"
        rc, out = run([sys.executable, "run_import.py", str(bad_quoted)], parser_dir)
        if rc == 0:
            raise AssertionError("[bad-quoted-csv] expected failure")
        assert_contains(out, "CSV 형식 오류", "bad-quoted-csv")

    def _bad_nul_csv():
        bad_nul = fixtures / "bad_nul.csv"
        rc, out = run([sys.executable, "run_import.py", str(bad_nul)], parser_dir)
        if rc == 0:
            raise AssertionError("[bad-nul-csv] expected failure")
        assert_contains(out, "CSV 파일 손상 오류(NUL 바이트 포함)", "bad-nul-csv")

    def _invalid_pdf():
        invalid_pdf = fixtures / "invalid.pdf"
        rc, out = run([sys.executable, "run_import.py", str(invalid_pdf)], parser_dir)
        if rc == 0:
            raise AssertionError("[invalid-pdf] expected failure")
        if ("PDF 텍스트 추출 실패" not in out) and ("지원되지 않는 형식" not in out):
            raise AssertionError(f"[invalid-pdf] expected PDF extraction failure message, got:\n{out}")

    def _empty_pdf():
        empty_pdf = fixtures / "empty.pdf"
        rc, out = run([sys.executable, "run_import.py", str(empty_pdf)], parser_dir)
        if rc == 0:
            raise AssertionError("[empty-pdf] expected failure")
        assert_contains(out, "PDF 파일이 비어 있습니다", "empty-pdf")

    def _unsupported_extension():
        unsupported = fixtures / "unsupported.txt"
        rc, out = run([sys.executable, "run_import.py", str(unsupported)], parser_dir)
        if rc == 0:
            raise AssertionError("[unsupported-extension] expected failure")
        assert_contains(out, "지원하지 않는 파일 형식", "unsupported-extension")

    _case("empty-json", _empty_json, results)
    _case("broken-json", _broken_json, results)
    _case("missing-header", _missing_header, results)
    _case("invalid-option", _invalid_option, results)
    _case("bad-feedback", _bad_feedback, results)
    _case("encoding-csv", _encoding_csv, results)
    _case("empty-csv", _empty_csv, results)
    _case("bad-quoted-csv", _bad_quoted_csv, results)
    _case("bad-nul-csv", _bad_nul_csv, results)
    _case("invalid-pdf", _invalid_pdf, results)
    _case("empty-pdf", _empty_pdf, results)
    _case("unsupported-extension", _unsupported_extension, results)
    return results



def main():
    args = parse_args()
    parser_dir = Path(__file__).resolve().parent

    report = {"suite": args.suite, "cases": []}

    if args.suite in ("all", "benchmark"):
        report["cases"].extend(run_benchmark_suite(parser_dir))
    if args.suite in ("all", "exceptions"):
        report["cases"].extend(run_exception_suite(parser_dir))

    report["all_pass"] = all(c["pass"] for c in report["cases"])
    report["smoke_escalate_threshold"] = args.smoke_escalate_threshold

    if args.report_json:
        p = Path(args.report_json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"saved -> {p}")

    failed = [c for c in report["cases"] if not c["pass"]]
    report["failed_count"] = len(failed)
    report["max_failures"] = args.max_failures

    if len(failed) > args.max_failures:
        for c in failed:
            print(f"FAIL {c['label']}: {c['error']}")
        raise SystemExit(f"QA_SMOKE_FAIL: failed={len(failed)} allowed={args.max_failures}")

    print("QA_SMOKE_OK")


if __name__ == "__main__":
    main()
