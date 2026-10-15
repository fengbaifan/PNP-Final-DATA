from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
EXPECTED_TABLE_SHA = "9ae439a6e9e09e3af8e49cefb30f201fc69f3658cecb1a9b12d026dcfc210549"
EXPECTED_SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-quote-coverage-edges-20261013")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair two verified S2 citation/coverage boundary issues.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview; default is preview")
    args = parser.parse_args()
    if digest(TABLE) != EXPECTED_TABLE_SHA:
        raise SystemExit("protected statement table hash changed")
    if digest(SOURCE) != EXPECTED_SOURCE_SHA:
        raise SystemExit("protected S0 source hash changed")

    rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    brawl = by_id["st-chp2-seciv-l45-52-taddeo-brawl-and-murder"]
    palace = by_id["st-chp2-seciv-l54-63-barberini-palace-departure-from-tradition"]
    if brawl.get("original_quote") != "Within three years he was involved in a street brawl.":
        raise SystemExit("unexpected p.47 quote; refusing to overwrite")
    if (palace.get("qualifiers", {}).get("source_line_start"), palace.get("qualifiers", {}).get("source_line_end")) != (52, 55):
        raise SystemExit("unexpected p.48 source-line range; refusing to overwrite")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    brawl_quote = "Within three years he was involved in a street brawl"
    palace_quote = "tradition of the sixteenth-century Roman palace."
    if brawl_quote not in source_lines[47] or palace_quote not in source_lines[54]:
        raise SystemExit("verified quote fragment no longer matches S0")

    brawl["original_quote"] = brawl_quote
    palace["qualifiers"]["source_line_start"] = 55
    palace["qualifiers"]["source_line_end"] = 55
    palace["original_quote"] = palace_quote
    payload = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "preview",
        "changes": [
            {"statement_id": brawl["statement_id"], "old_quote": "Within three years he was involved in a street brawl.", "new_quote": brawl_quote, "source_lines": [48, 48]},
            {"statement_id": palace["statement_id"], "old_source_lines": [52, 55], "new_source_lines": [55, 55], "new_quote": palace_quote, "continuation_of": palace["qualifiers"].get("continuation_of_statement_id")},
        ],
        "expected_table_sha256": EXPECTED_TABLE_SHA,
        "preview_payload_sha256": hashlib.sha256(payload).hexdigest(),
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"recovery copy already exists; refusing overwrite: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".repair-", delete=False) as handle:
            temp_path = Path(handle.name)
            handle.write(payload)
        os.replace(temp_path, TABLE)
        temp_path = None
        print(json.dumps({"result": "applied", "backup": BACKUP.name, "written_sha256": digest(TABLE)}, indent=2))
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise


if __name__ == "__main__":
    main()
