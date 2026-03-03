import argparse
import json
from pathlib import Path


def _load_recent_history(history_path: Path, max_items: int = 5):
    if not history_path.exists():
        return []
    rows = []
    for line in history_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-max_items:]


def _fmt_delta(curr, prev):
    if curr is None or prev is None:
        return "-"
    d = round(float(curr) - float(prev), 4)
    sign = "+" if d > 0 else ""
    return f"{sign}{d}"


def parse_args():
    ap = argparse.ArgumentParser(description="Build benchmark summary markdown")
    ap.add_argument("--regression-threshold-sec", type=float, default=0.2)
    ap.add_argument("--fail-on-regression", action="store_true")
    return ap.parse_args()


def main():
    args = parse_args()

    root = Path(__file__).resolve().parents[1]
    result_path = root / "data" / "benchmark_pipeline_result.json"
    history_path = root / "data" / "benchmark_history.jsonl"
    out_path = root / "data" / "benchmark_summary.md"

    regression_threshold_sec = args.regression_threshold_sec

    data = json.loads(result_path.read_text(encoding="utf-8"))
    verdict = data.get("verdict", {})
    steps = verdict.get("steps", {})
    recent = _load_recent_history(history_path)

    lines = []
    lines.append("# Receipt Ledger Benchmark Summary")
    lines.append("")
    lines.append(f"- rows: {data.get('rows')}")
    lines.append(f"- repeats: {data.get('repeats')}")
    lines.append(f"- overall: {'PASS' if verdict.get('all_pass') else 'FAIL'}")
    lines.append(f"- pipeline_total_avg_sec: {data.get('pipeline_total_avg_sec')}")
    lines.append("")
    lines.append("| step | avg(s) | target(s) | pass |")
    lines.append("|---|---:|---:|:---:|")

    for step, info in steps.items():
        lines.append(
            f"| {step} | {info.get('avg_sec')} | {info.get('target_sec')} | {'✅' if info.get('pass') else '❌'} |"
        )

    regressions = []

    if recent:
        lines.extend([
            "",
            "## Recent Runs (latest 5)",
            "",
            "| ts(UTC) | import avg(s) | Δimport | export avg(s) | Δexport | apply avg(s) | Δapply | report avg(s) | Δreport | all_pass |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|",
        ])
        prev = None
        for r in recent:
            s = r.get("steps", {})
            imp = s.get("import", {}).get("avg_sec")
            exp = s.get("export_uncategorized", {}).get("avg_sec")
            app = s.get("apply_feedback", {}).get("avg_sec")
            rep = s.get("monthly_report", {}).get("avg_sec")

            p = (prev or {}).get("steps", {})
            p_imp = p.get("import", {}).get("avg_sec")
            p_exp = p.get("export_uncategorized", {}).get("avg_sec")
            p_app = p.get("apply_feedback", {}).get("avg_sec")
            p_rep = p.get("monthly_report", {}).get("avg_sec")

            d_imp = (float(imp) - float(p_imp)) if (imp is not None and p_imp is not None) else None
            d_exp = (float(exp) - float(p_exp)) if (exp is not None and p_exp is not None) else None
            d_app = (float(app) - float(p_app)) if (app is not None and p_app is not None) else None
            d_rep = (float(rep) - float(p_rep)) if (rep is not None and p_rep is not None) else None

            lines.append(
                f"| {r.get('ts')} | {imp} | {_fmt_delta(imp, p_imp)} | {exp} | {_fmt_delta(exp, p_exp)} | {app} | {_fmt_delta(app, p_app)} | {rep} | {_fmt_delta(rep, p_rep)} | {'✅' if r.get('all_pass') else '❌'} |"
            )

            if d_imp is not None and d_imp > regression_threshold_sec:
                regressions.append(f"import +{round(d_imp,4)}s")
            if d_exp is not None and d_exp > regression_threshold_sec:
                regressions.append(f"export_uncategorized +{round(d_exp,4)}s")
            if d_app is not None and d_app > regression_threshold_sec:
                regressions.append(f"apply_feedback +{round(d_app,4)}s")
            if d_rep is not None and d_rep > regression_threshold_sec:
                regressions.append(f"monthly_report +{round(d_rep,4)}s")

            prev = r

    if regressions:
        lines.extend([
            "",
            "## Regression Warning",
            "",
            f"- threshold: +{regression_threshold_sec}s",
        ])
        for r in regressions:
            lines.append(f"- ⚠️ {r}")

    text = "\n".join(lines) + "\n"
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"saved -> {out_path}")

    if args.fail_on_regression and regressions:
        raise SystemExit("benchmark regression detected")


if __name__ == "__main__":
    main()
