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
SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l5-19"
EXPECTED_HASHES = {
    "table": "a530a75b1081f557c9ed991226885bc4fad99b19bc8118e616e05f8916fd57e1",
    "candidates": "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    "coverage": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "source": "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c",
    "pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
}
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-vii-l5-19-20261010"
TARGET_IDS = {
    "st-chp2-secvii-l5-19-antonio-flight-1645",
    "st-chp2-secvii-l5-19-antonio-returns-and-xenophon-picture",
    "st-chp2-secvii-l5-19-barberini-effects-continuation",
    "st-chp2-secvii-l5-19-barberini-security-and-foreign-policy",
    "st-chp2-secvii-l5-19-bernini-association-and-rivals",
    "st-chp2-secvii-l5-19-bernini-completes-urban-tomb",
    "st-chp2-secvii-l5-19-financial-inquiry-threat",
    "st-chp2-secvii-l5-19-francesco-praises-vouet",
    "st-chp2-secvii-l5-19-francesco-returns-1648",
    "st-chp2-secvii-l5-19-francesco-taddeo-follow-into-exile",
    "st-chp2-secvii-l5-19-giori-urges-congratulations",
    "st-chp2-secvii-l5-19-hostility-and-rome-crisis",
    "st-chp2-secvii-l5-19-innocent-election-and-sacchetti",
    "st-chp2-secvii-l5-19-romanelli-letter-and-exile",
    "st-chp2-secvii-l5-19-rome-properties-and-taddeo-wife",
    "st-chp2-secvii-l5-19-tapestry-series-production",
    "st-chp2-secvii-l5-19-theatre-reopens-and-rospigliosi-resumes",
}
NOTES = {
    "st-chp2-secvii-l5-19-barberini-effects-continuation": (
        "This completes the L3 sentence across the page break. The phrase 'of great importance' "
        "is Haskell's comparison of the War of Castro's effects on the Barberini, not a measured outcome."
    ),
    "st-chp2-secvii-l5-19-francesco-taddeo-follow-into-exile": (
        "The source says Francesco and Taddeo joined Antonio in France four months after his "
        "September 1645 flight. Keep the brothers in related_person_candidate_ids and preserve "
        "the relative interval; no exact arrival date is stated."
    ),
    "st-chp2-secvii-l5-19-hostility-and-rome-crisis": (
        "The source reports a sequence of political and city consequences during the crisis; "
        "do not infer a single direct cause for every listed event."
    ),
}


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
    by_id = {row.get("statement_id"): row for row in selected}
    pending = {
        row["statement_id"]
        for row in selected
        if row.get("subject_candidate_id")
        and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if pending != TARGET_IDS:
        raise SystemExit(
            f"pending statement scope changed: missing={TARGET_IDS-pending}; unexpected={pending-TARGET_IDS}"
        )
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for statement_id in sorted(TARGET_IDS):
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        start, end = qualifiers.get("source_line_start"), qualifiers.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
            raise SystemExit(f"invalid source line anchor: {statement_id}")
        anchor = normalize("\n".join(source_lines[start - 1:end]))
        if normalize(row.get("original_quote", "")) not in anchor:
            raise SystemExit(f"source quote does not match line anchor: {statement_id}")
        if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
            raise SystemExit(f"bilateral endpoint missing: {statement_id}")
        if (
            row["subject_candidate_id"] not in candidate_ids
            or row["object_candidate_id"] not in candidate_ids
        ):
            raise SystemExit(f"candidate endpoint missing: {statement_id}")
    continuation = by_id.get("st-chp2-secvii-l5-19-barberini-effects-continuation")
    if not continuation or continuation["qualifiers"].get("source_line_start") != 6:
        raise SystemExit("L3 cross-page continuation changed")
    if "1645" not in normalize(by_id["st-chp2-secvii-l5-19-antonio-flight-1645"]["qualifiers"].get("print_ocr_correction", "")):
        raise SystemExit("print confirmation of the 1645 date changed")
    return rows, by_id, bom, newline, actual


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows, by_id, bom, newline, hashes = preflight()
    preview = [
        {
            "statement_id": statement_id,
            "predicate": by_id[statement_id].get("predicate"),
            "subject_candidate_id": by_id[statement_id].get("subject_candidate_id"),
            "object_candidate_id": by_id[statement_id].get("object_candidate_id"),
            "relation_candidate": True,
            "relation_candidate_note": NOTES.get(statement_id),
        }
        for statement_id in sorted(TARGET_IDS)
    ]
    if args.dry_run:
        print(json.dumps({"preflight": "passed", "hashes": hashes, "changes": preview}, ensure_ascii=False, indent=2))
        return

    shutil.copy2(STATEMENTS, BACKUP)
    for row in rows:
        statement_id = row.get("statement_id")
        if statement_id in TARGET_IDS:
            qualifiers = row.setdefault("qualifiers", {})
            qualifiers["relation_candidate"] = True
            if statement_id in NOTES:
                qualifiers["relation_candidate_note"] = NOTES[statement_id]
    write_jsonl(STATEMENTS, rows, bom, newline)
    after = sha256(STATEMENTS)
    if after == hashes["table"]:
        raise SystemExit("write-back unexpectedly produced no table change")
    print(json.dumps({
        "applied": len(TARGET_IDS),
        "backup": str(BACKUP.relative_to(ROOT)),
        "before_sha256": hashes["table"],
        "after_sha256": after,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
