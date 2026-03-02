import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + ("\n" + p.stderr if p.stderr else "")


def assert_contains(text: str, needle: str, label: str):
    if needle not in text:
        raise AssertionError(f"[{label}] expected '{needle}' in output, got:\n{text}")


def main():
    parser_dir = Path(__file__).resolve().parent

    # 1) benchmark 5k (quick repeat=1)
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
    assert_contains(out, "overall: PASS", "benchmark")

    with tempfile.TemporaryDirectory(prefix="receipt-ledger-qa-") as td:
        work = Path(td)

        # 2) empty json
        empty = work / "empty.json"
        empty.write_text("", encoding="utf-8")
        rc, out = run([sys.executable, "monthly_report.py", str(empty)], parser_dir)
        if rc == 0:
            raise AssertionError("[empty-json] expected failure")
        assert_contains(out, "입력 JSON 파일이 비어 있습니다", "empty-json")

        # 3) corrupt json
        broken = work / "broken.json"
        broken.write_text("{broken", encoding="utf-8")
        rc, out = run([sys.executable, "export_uncategorized.py", str(broken)], parser_dir)
        if rc == 0:
            raise AssertionError("[broken-json] expected failure")
        assert_contains(out, "손상된 JSON 형식입니다", "broken-json")

        # 4) missing csv headers
        bad_csv = work / "missing_header.csv"
        bad_csv.write_text("foo,bar\n1,2\n", encoding="utf-8")
        rc, out = run([sys.executable, "run_import.py", str(bad_csv)], parser_dir)
        if rc == 0:
            raise AssertionError("[missing-header] expected failure")
        assert_contains(out, "필수 헤더 누락", "missing-header")

        # 5) invalid fixed-cost option
        sample_csv = parser_dir.parent / "data" / "sample_tossbank.csv"
        rc, out = run(
            [
                sys.executable,
                "run_import.py",
                str(sample_csv),
                "--fixed-cost-min-months",
                "0",
            ],
            parser_dir,
        )
        if rc == 0:
            raise AssertionError("[invalid-option] expected failure")
        assert_contains(out, "--fixed-cost-min-months 는 1 이상", "invalid-option")

        # 6) invalid feedback schema
        normalized = work / "sample.normalized.json"
        normalized.write_text('[{"occurred_at":"2026-03-01 10:00:00","amount":1000,"direction":"expense","merchant_name":"테스트"}]', encoding="utf-8")
        bad_feedback = work / "bad.feedback.json"
        bad_feedback.write_text('{"items": ["bad"]}', encoding="utf-8")
        rc, out = run([sys.executable, "apply_feedback.py", str(normalized), str(bad_feedback)], parser_dir)
        if rc == 0:
            raise AssertionError("[bad-feedback] expected failure")
        assert_contains(out, "feedback items의 모든 항목은 객체(dict)", "bad-feedback")

    print("QA_SMOKE_OK")


if __name__ == "__main__":
    main()
