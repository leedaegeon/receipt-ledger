import json
import sys
from dataclasses import asdict
from pathlib import Path

from tossbank_parser import parse_csv, parse_pdf


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_import.py <file.csv|file.pdf>")
        sys.exit(1)

    p = Path(sys.argv[1])
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(1)

    if p.suffix.lower() == ".csv":
        txs = parse_csv(p)
    elif p.suffix.lower() == ".pdf":
        txs = parse_pdf(p)
    else:
        print("Unsupported format. Use .csv or .pdf")
        sys.exit(1)

    out = [asdict(x) for x in txs]
    out_path = p.with_suffix(".normalized.json")
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    print(f"parsed={len(out)} -> {out_path}")


if __name__ == "__main__":
    main()
