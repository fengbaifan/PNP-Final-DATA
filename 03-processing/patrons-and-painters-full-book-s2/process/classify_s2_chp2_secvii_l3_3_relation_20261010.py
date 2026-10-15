from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_vii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-2.pdf"
SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l3-3"
STATEMENT_ID = "st-chp2-secvii-l3-3-parma-consequences-fragment"
EXPECTED_HASHES = {
    "table": "579927439e9f649c9f99b5760335e68300e173d01e68e4cc09151905cd249d77",
    "candidates": "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    "coverage": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "source": "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c",
    "pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
}
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-vii-l3-3-20261010"
NOTE = (
    "The phrase 'dispute with the Duke of Parma' names the relation. The judgment about "
    "its consequences is Haskell's evaluation; the final comparison continues in the "
    "linked statement on print p.59."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def read_jsonl(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    decoded = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in decoded else "\n"
    rows = [json.loads(line) for line in decoded.splitlines() if line.strip()]
    return rows, bom, newline


def write_jsonl(path: Path, rows, bom: bool, newline: str) -> None:
    text = newline.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows
    ) + newline
    data = (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")
    temp = path.with_suffix(path.suffix + ".s2tmp")
    temp.write_bytes(data)
    temp.replace(path)


def preflight():
    paths = {
        "table": STATEMENTS,
        "candidates": CANDIDATES,
        "coverage": COVERAGE,
        "source": SOURCE,
        "pdf": PDF,
    }
    actual = {name: sha256(path) for name, path in paths.items()}
    if actual != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: expected={EXPECTED_HASHES}; actual={actual}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = [row for row in csv.DictReader(handle) if row.get("segment_id") == SEGMENT_ID]
    if (
        len(coverage) != 1
        or coverage[0].get("disposition") != "reviewed"
        or coverage[0].get("migration_status") != "complete"
    ):
        raise SystemExit(f"coverage preflight failed: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    rows, bom, newline = read_jsonl(STATEMENTS)
    selected = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    if len(selected) != 2:
        raise SystemExit(f"segment row count changed: {len(selected)}")
    target = [row for row in selected if row.get("statement_id") == STATEMENT_ID]
    if len(target) != 1:
        raise SystemExit(f"target statement count changed: {len(target)}")
    row = target[0]
    qualifiers = row.get("qualifiers") or {}
    if qualifiers.get("relation_candidate") is not None:
        raise SystemExit("target statement was already classified")
    if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != (
        "cand-4904", "cand-4905"
    ):
        raise SystemExit("statement endpoints changed")
    if not {"cand-4904", "cand-4905"}.issubset(candidate_ids):
        raise SystemExit("one or more candidate endpoints are missing")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if normalize(row.get("original_quote", "")) not in normalize(source_lines[2]):
        raise SystemExit("source quote does not match L3")
    if normalize(qualifiers.get("claim", "")).find("dispute with the Duke of Parma") < 0:
        raise SystemExit("claim no longer names the disputed relation")
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    return rows, row, bom, newline, actual


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows, row, bom, newline, hashes = preflight()
    preview = {
        "statement_id": STATEMENT_ID,
        "predicate": row.get("predicate"),
        "subject_candidate_id": row.get("subject_candidate_id"),
        "object_candidate_id": row.get("object_candidate_id"),
        "relation_candidate": True,
        "relation_candidate_note": NOTE,
    }
    if args.dry_run:
        print(json.dumps({"preflight": "passed", "hashes": hashes, "change": preview}, ensure_ascii=False, indent=2))
        return

    shutil.copy2(STATEMENTS, BACKUP)
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = True
    qualifiers["relation_candidate_note"] = NOTE
    write_jsonl(STATEMENTS, rows, bom, newline)
    after = sha256(STATEMENTS)
    if after == hashes["table"]:
        raise SystemExit("write-back unexpectedly produced no table change")
    print(json.dumps({
        "applied": STATEMENT_ID,
        "backup": str(BACKUP.relative_to(ROOT)),
        "before_sha256": hashes["table"],
        "after_sha256": after,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
