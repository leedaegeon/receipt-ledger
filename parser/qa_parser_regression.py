import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


EXPECTED = {
    "parsed_count": 6,
    "invalid_count": 0,
    "uncategorized_expense_count": 2,
    "uncategorized_merchants": {"한식당 점심", "netflix"},
    "report_summary": {
        "total_income": 2500000,
        "total_expense": 33700,
        "net_cashflow": 2466300,
        "expense_count": 4,
        "income_count": 1,
    },
    "category_amounts": {
        "미분류": 27900,
        "카페": 4500,
        "교통": 1300,
    },
}


def run(cmd: list[str], cwd: Path):
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    out = (p.stdout or "") + ("\n" + p.stderr if p.stderr else "")
    return p.returncode, out


def assert_true(cond: bool, message: str):
    if not cond:
        raise AssertionError(message)


def parse_args():
    ap = argparse.ArgumentParser(
        description="Parser regression QA (sample_tossbank.csv 기반: parse/uncategorized/report 핵심 검증)"
    )
    ap.add_argument("--sample-csv", default="../data/sample_tossbank.csv", help="샘플 CSV 경로")
    ap.add_argument("--month", default="2026-02")
    ap.add_argument("--account", default="토스뱅크")
    ap.add_argument("--work-dir", default=None, help="산출물 작업 디렉터리(미지정 시 임시 디렉터리)")
    ap.add_argument("--keep-artifacts", action="store_true", help="검증 후에도 산출물 디렉터리 유지")
    ap.add_argument("--report-json", default=None, help="검증 결과 JSON 저장 경로")
    return ap.parse_args()


def main():
    args = parse_args()
    parser_dir = Path(__file__).resolve().parent
    sample_csv = Path(args.sample_csv)
    if not sample_csv.is_absolute():
        sample_csv = (parser_dir / sample_csv).resolve()

    assert_true(sample_csv.exists(), f"샘플 CSV 파일이 없습니다: {sample_csv}")

    temp_dir = None
    if args.work_dir:
        work_dir = Path(args.work_dir).resolve()
        work_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = tempfile.mkdtemp(prefix="receipt-ledger-regression-")
        work_dir = Path(temp_dir)

    report = {
        "sample_csv": str(sample_csv),
        "work_dir": str(work_dir),
        "steps": [],
        "all_pass": False,
    }

    try:
        # 1) Parse regression
        parse_cmd = [
            sys.executable,
            "run_import.py",
            str(sample_csv),
            "--month",
            args.month,
            "--account",
            args.account,
            "--out-dir",
            str(work_dir),
        ]
        rc, out = run(parse_cmd, parser_dir)
        assert_true(rc == 0, f"run_import 실패\n{out}")
        assert_true("parsed=6 invalid=0" in out, f"run_import 결과 요약 불일치\n{out}")
        report["steps"].append({"step": "parse", "pass": True})

        normalized_path = work_dir / f"{sample_csv.stem}.{args.month}.normalized.json"
        invalid_path = work_dir / f"{sample_csv.stem}.{args.month}.invalid.json"

        normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
        invalid = json.loads(invalid_path.read_text(encoding="utf-8"))

        assert_true(len(normalized) == EXPECTED["parsed_count"], f"normalized 개수 불일치: {len(normalized)}")
        assert_true(invalid.get("meta", {}).get("count") == EXPECTED["invalid_count"], "invalid count 불일치")
        assert_true(len(invalid.get("rows", [])) == EXPECTED["invalid_count"], "invalid rows 불일치")

        # 2) Uncategorized export regression
        feedback_path = work_dir / "sample.feedback.template.json"
        rc, out = run(
            [sys.executable, "export_uncategorized.py", str(normalized_path), "--out", str(feedback_path)], parser_dir
        )
        assert_true(rc == 0, f"export_uncategorized 실패\n{out}")

        feedback = json.loads(feedback_path.read_text(encoding="utf-8"))
        meta = feedback.get("meta", {})
        items = feedback.get("items", [])

        assert_true(
            meta.get("uncategorized_expense_count") == EXPECTED["uncategorized_expense_count"],
            f"미분류 지출 건수 불일치: {meta.get('uncategorized_expense_count')}",
        )
        assert_true(meta.get("unique_merchants") == 2, f"미분류 거래처 수 불일치: {meta.get('unique_merchants')}")

        merchants = {x.get("normalized_merchant_name") for x in items}
        assert_true(
            merchants == EXPECTED["uncategorized_merchants"],
            f"미분류 거래처 목록 불일치: {merchants}",
        )
        report["steps"].append({"step": "uncategorized", "pass": True})

        # 3) Monthly report regression
        report_path = work_dir / "sample.report.json"
        rc, out = run(
            [
                sys.executable,
                "monthly_report.py",
                str(normalized_path),
                "--month",
                args.month,
                "--account",
                args.account,
                "--out",
                str(report_path),
            ],
            parser_dir,
        )
        assert_true(rc == 0, f"monthly_report 실패\n{out}")

        monthly = json.loads(report_path.read_text(encoding="utf-8"))
        summary = monthly.get("summary", {})
        for k, v in EXPECTED["report_summary"].items():
            assert_true(summary.get(k) == v, f"summary.{k} 불일치: {summary.get(k)} != {v}")

        by_cat = {x.get("category"): x.get("amount") for x in monthly.get("category_breakdown", [])}
        for k, v in EXPECTED["category_amounts"].items():
            assert_true(by_cat.get(k) == v, f"category {k} 금액 불일치: {by_cat.get(k)} != {v}")

        assert_true(monthly.get("uncategorized", {}).get("count") == 2, "report uncategorized.count 불일치")
        report["steps"].append({"step": "monthly_report", "pass": True})

        report["all_pass"] = True
        print("PARSER_REGRESSION_OK")

    except Exception as e:
        report["error"] = str(e)
        print(f"PARSER_REGRESSION_FAIL: {e}")
        raise SystemExit(1)
    finally:
        if args.report_json:
            rp = Path(args.report_json)
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"saved -> {rp}")

        if temp_dir and not args.keep_artifacts:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
