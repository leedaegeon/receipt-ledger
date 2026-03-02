import argparse
import csv
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path
from statistics import mean
from time import perf_counter


def parse_args():
    ap = argparse.ArgumentParser(description="Benchmark parser pipeline (import/export_uncategorized/apply_feedback/monthly_report)")
    ap.add_argument("--rows", type=int, default=5000, help="Synthetic CSV row count (default: 5000)")
    ap.add_argument("--repeats", type=int, default=3, help="Repeat count per step (default: 3)")
    ap.add_argument("--out", default=None, help="Output JSON path")
    ap.add_argument("--target-import-sec", type=float, default=5.0, help="Target avg seconds for import step")
    ap.add_argument("--target-export-sec", type=float, default=1.0, help="Target avg seconds for export_uncategorized step")
    ap.add_argument("--target-apply-sec", type=float, default=1.0, help="Target avg seconds for apply_feedback step")
    ap.add_argument("--target-report-sec", type=float, default=1.0, help="Target avg seconds for monthly_report step")
    ap.add_argument("--fail-on-target", action="store_true", help="Exit with non-zero code if any target fails")
    return ap.parse_args()


def make_synthetic_csv(path: Path, rows: int):
    random.seed(42)
    merchants = ["스타벅스", "쿠팡", "GS25", "배달의민족", "넷플릭스", "KT", "SKT", "마켓컬리", "올리브영"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["거래일시", "거래구분", "거래금액", "적요"])
        w.writeheader()
        for i in range(rows):
            month = (i % 6) + 1
            day = (i % 27) + 1
            hour = (i % 23)
            minute = (i * 7) % 59
            merchant = merchants[i % len(merchants)]
            amount = random.choice([4500, 12000, 19800, 32000, 55000, 89000])
            gubun = "출금"
            if merchant in ("KT", "SKT", "넷플릭스"):
                amount = random.choice([33000, 35000, 39000])
            w.writerow(
                {
                    "거래일시": f"2026-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00",
                    "거래구분": gubun,
                    "거래금액": f"-{amount:,}",
                    "적요": merchant,
                }
            )


def run(cmd: list[str], cwd: Path):
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p.stdout


def measure(cmd: list[str], cwd: Path, repeats: int) -> dict:
    samples = []
    for _ in range(repeats):
        t0 = perf_counter()
        run(cmd, cwd)
        samples.append(perf_counter() - t0)
    return {
        "samples_sec": [round(x, 4) for x in samples],
        "avg_sec": round(mean(samples), 4),
        "min_sec": round(min(samples), 4),
        "max_sec": round(max(samples), 4),
    }


def main():
    args = parse_args()
    parser_dir = Path(__file__).resolve().parent

    with tempfile.TemporaryDirectory(prefix="receipt-ledger-bench-") as td:
        work = Path(td)
        csv_path = work / "synthetic.csv"
        normalized_path = work / "synthetic.normalized.json"
        feedback_path = work / "feedback.json"

        make_synthetic_csv(csv_path, args.rows)

        import_cmd = [
            sys.executable,
            "run_import.py",
            str(csv_path),
            "--out-dir",
            str(work),
            "--month",
            "2026-03",
        ]
        export_cmd = [sys.executable, "export_uncategorized.py", str(normalized_path)]
        apply_cmd = [sys.executable, "apply_feedback.py", str(normalized_path), str(feedback_path)]
        report_cmd = [sys.executable, "monthly_report.py", str(normalized_path), "--month", "2026-03"]

        # warmup import + feedback file 생성
        run(import_cmd, parser_dir)
        normalized_path = work / "synthetic.2026-03.normalized.json"
        run([sys.executable, "export_uncategorized.py", str(normalized_path)], parser_dir)
        template = json.loads((work / "synthetic.2026-03.normalized.feedback.template.json").read_text(encoding="utf-8"))
        items = template.get("items", [])[:20]
        for it in items:
            it["category"] = "생활"
        feedback_path.write_text(json.dumps({"items": items}, ensure_ascii=False, indent=2), encoding="utf-8")

        normalized_path = work / "synthetic.2026-03.normalized.json"
        export_cmd = [sys.executable, "export_uncategorized.py", str(normalized_path)]
        apply_cmd = [sys.executable, "apply_feedback.py", str(normalized_path), str(feedback_path)]
        report_cmd = [sys.executable, "monthly_report.py", str(normalized_path), "--month", "2026-03"]

        steps = {
            "import": measure(import_cmd, parser_dir, args.repeats),
            "export_uncategorized": measure(export_cmd, parser_dir, args.repeats),
            "apply_feedback": measure(apply_cmd, parser_dir, args.repeats),
            "monthly_report": measure(report_cmd, parser_dir, args.repeats),
        }

        targets = {
            "import": args.target_import_sec,
            "export_uncategorized": args.target_export_sec,
            "apply_feedback": args.target_apply_sec,
            "monthly_report": args.target_report_sec,
        }
        verdicts = {
            step: {
                "avg_sec": steps[step]["avg_sec"],
                "target_sec": targets[step],
                "pass": steps[step]["avg_sec"] <= targets[step],
            }
            for step in steps
        }

        result = {
            "rows": args.rows,
            "repeats": args.repeats,
            "python": sys.executable,
            "targets_sec": targets,
            "steps": steps,
            "verdict": {
                "all_pass": all(v["pass"] for v in verdicts.values()),
                "steps": verdicts,
            },
        }

        out = Path(args.out) if args.out else parser_dir.parent / "data" / "benchmark_pipeline_result.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("\n[benchmark summary]")
        for step, info in result["verdict"]["steps"].items():
            status = "PASS" if info["pass"] else "FAIL"
            print(f"- {step}: {status} avg={info['avg_sec']}s target<={info['target_sec']}s")
        print(f"- overall: {'PASS' if result['verdict']['all_pass'] else 'FAIL'}")
        print(f"saved -> {out}")

        if args.fail_on_target and not result["verdict"]["all_pass"]:
            raise SystemExit("benchmark target failed")


if __name__ == "__main__":
    main()
