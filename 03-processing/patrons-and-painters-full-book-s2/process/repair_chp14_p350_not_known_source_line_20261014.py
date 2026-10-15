"""Extend one p.350 statement's source line range to include its exact quote."""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
EXPECTED_TABLE = "c1d24f32f8d9abfe49b3685fa32c9edbe7ef6647762993d1af52c0d925e077de"
EXPECTED_SOURCE = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
SID = "st-chp14-p350-not-known-in-venice"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch14-p350-source-line-repair-20261014")

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); args = ap.parse_args()
    if digest(TABLE) != EXPECTED_TABLE or digest(SOURCE) != EXPECTED_SOURCE:
        raise SystemExit("source or statement table hash changed")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    quote = "he was not well known in\nVenice"
    if quote not in "\n".join(lines[35:37]):
        raise SystemExit("the exact p.350 L36-37 quote is not present")
    original = TABLE.read_text(encoding="utf-8-sig").splitlines()
    rows = [json.loads(x) for x in original if x.strip()]
    matches = [r for r in rows if r["statement_id"] == SID]
    if len(matches) != 1: raise SystemExit("target statement missing or duplicated")
    q = matches[0].get("qualifiers") or {}
    if q.get("source_line_start") != 36 or q.get("source_line_end") != 36 or matches[0].get("original_quote") != quote:
        raise SystemExit("target statement is not in the expected pre-repair state")
    q["source_line_end"] = 37
    matches[0]["qualifiers"] = q
    by_id = {r["statement_id"]: r for r in rows}
    payload = ("\n".join(json.dumps(by_id[json.loads(line)["statement_id"]], ensure_ascii=False, separators=(",", ":"))
                           if json.loads(line)["statement_id"] == SID else line for line in original) + "\n").encode("utf-8")
    print(f"statement={SID}; corrected_source_lines=36-37; sha256={hashlib.sha256(payload).hexdigest()}")
    if not args.apply:
        print("dry_run=true; no files written"); return 0
    if BACKUP.exists(): raise SystemExit("repair backup already exists")
    shutil.copy2(TABLE, BACKUP)
    TABLE.write_bytes(payload)
    if digest(TABLE) != hashlib.sha256(payload).hexdigest():
        shutil.copy2(BACKUP, TABLE); raise SystemExit("post-write hash mismatch; original restored")
    print(f"applied=true; backup={BACKUP.name}")
    return 0

if __name__ == "__main__": sys.exit(main())
