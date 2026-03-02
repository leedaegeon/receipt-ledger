import argparse
import json
from dataclasses import asdict
from pathlib import Path

from tossbank_parser import parse_csv_with_invalid, parse_pdf_with_invalid


def parse_args():
    ap = argparse.ArgumentParser(description="Import bank statement and normalize transactions")
    ap.add_argument("input", help="Input statement file (.csv|.pdf)")
    ap.add_argument("--out-dir", default=None, help="Output directory (default: input file directory)")
    ap.add_argument("--month", default=None, help="Target month label (e.g. 2026-02)")
    ap.add_argument("--account", default="토스뱅크", help="Account label")
    ap.add_argument("--fixed-cost-amount-tolerance-ratio", type=float, default=0.15)
    ap.add_argument("--fixed-cost-amount-tolerance-abs", type=int, default=10000)
    ap.add_argument("--fixed-cost-min-months", type=int, default=2)
    ap.add_argument("--fixed-cost-min-average-amount", type=int, default=30000)
    return ap.parse_args()


def main():
    args = parse_args()
    p = Path(args.input)
    if not p.exists():
        raise SystemExit(f"File not found: {p}")

    fixed_cost_options = {
        "amount_tolerance_ratio": args.fixed_cost_amount_tolerance_ratio,
        "amount_tolerance_abs": args.fixed_cost_amount_tolerance_abs,
        "min_months": args.fixed_cost_min_months,
        "min_average_amount": args.fixed_cost_min_average_amount,
    }

    try:
        if p.suffix.lower() == ".csv":
            txs, invalid = parse_csv_with_invalid(p, account_label=args.account, fixed_cost_options=fixed_cost_options)
        elif p.suffix.lower() == ".pdf":
            txs, invalid = parse_pdf_with_invalid(p, account_label=args.account, fixed_cost_options=fixed_cost_options)
        else:
            raise SystemExit("Unsupported format. Use .csv or .pdf")
    except UnicodeDecodeError as e:
        raise SystemExit(f"입력 파일 인코딩 오류(UTF-8 필요): {p} ({e})")
    except json.JSONDecodeError as e:
        raise SystemExit(f"입력 JSON 형식 오류: {p} ({e})")
    except ValueError as e:
        raise SystemExit(f"입력 데이터 오류: {e}")
    except Exception as e:
        raise SystemExit(f"파싱 실패: {type(e).__name__}: {e}")

    out_dir = Path(args.out_dir) if args.out_dir else p.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    prefix = p.stem
    if args.month:
        prefix = f"{prefix}.{args.month}"

    normalized = [asdict(x) for x in txs]
    normalized_path = out_dir / f"{prefix}.normalized.json"
    normalized_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2, default=str))

    invalid_payload = {
        "meta": {
            "source_file": str(p),
            "month": args.month,
            "account": args.account,
            "count": len(invalid),
        },
        "rows": invalid,
    }
    invalid_path = out_dir / f"{prefix}.invalid.json"
    invalid_path.write_text(json.dumps(invalid_payload, ensure_ascii=False, indent=2, default=str))

    print(f"parsed={len(normalized)} invalid={len(invalid)}")
    print(f"normalized -> {normalized_path}")
    print(f"invalid_report -> {invalid_path}")


if __name__ == "__main__":
    main()
