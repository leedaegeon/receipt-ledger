import argparse
import json
from dataclasses import asdict
from pathlib import Path

from tossbank_parser import _build_tx


# editable schema per row:
# {
#   "selected": true,
#   "date_text": "2026-02-10 12:00:00",
#   "direction_text": "출금",
#   "amount_text": "-12000",
#   "merchant_text": "점포명"
# }


def parse_args():
    ap = argparse.ArgumentParser(description="Reprocess manually edited invalid rows")
    ap.add_argument("editable_json", help="Path to editable invalid rows json")
    ap.add_argument("--account", default="토스뱅크")
    return ap.parse_args()


def main():
    args = parse_args()
    p = Path(args.editable_json)
    payload = json.loads(p.read_text())
    rows = payload.get("rows", payload if isinstance(payload, list) else [])

    repaired = []
    failed = []

    for i, r in enumerate(rows):
        if not r.get("selected", True):
            continue
        try:
            tx = _build_tx(
                r.get("date_text", ""),
                r.get("direction_text", ""),
                r.get("amount_text", ""),
                r.get("merchant_text", ""),
                args.account,
            )
            repaired.append(asdict(tx))
        except Exception as e:
            failed.append({"idx": i, "reason": type(e).__name__, "row": r})

    out_ok = p.with_name(p.stem + ".repaired.json")
    out_fail = p.with_name(p.stem + ".repaired_failed.json")
    out_ok.write_text(json.dumps(repaired, ensure_ascii=False, indent=2, default=str))
    out_fail.write_text(json.dumps(failed, ensure_ascii=False, indent=2, default=str))

    print(f"repaired={len(repaired)} failed={len(failed)}")
    print(f"repaired_out -> {out_ok}")
    print(f"failed_out -> {out_fail}")


if __name__ == "__main__":
    main()
