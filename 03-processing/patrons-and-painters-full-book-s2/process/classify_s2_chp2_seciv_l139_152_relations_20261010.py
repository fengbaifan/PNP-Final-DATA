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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-2.pdf"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l139-152"
EXPECTED_TABLE_SHA256 = "f42703623c6147ef89b672e5ff214ecd059ab36b6c74123f893086f09926007c"
EXPECTED_SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
EXPECTED_PDF_SHA256 = "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-iv-l139-152-20261010"


# Every bilateral statement in this segment expresses a relation. Three additional
# one-ended statements express relations whose unbounded group/referent is not named.
# The Cantalamessa citation endpoint is normalized to the book -> cited-publication
# direction using the existing book candidate and the exact bibliographic mention.
CLASSIFICATIONS = {
    "st-chp2-seciv-l139-152-1642-volume-describes-palace-contents": {},
    "st-chp2-seciv-l139-152-barberini-pictures-sold-and-sale-catalogue": {},
    "st-chp2-seciv-l139-152-barberini-revive-roman-chivalric-past": {},
    "st-chp2-seciv-l139-152-bouchard-attends-first-performance-fragment": {},
    "st-chp2-seciv-l139-152-lavin-publishes-barberini-inventories": {},
    "st-chp2-seciv-l139-152-montagu-points-author-to-tessin-account": {},
    "st-chp2-seciv-l139-152-operatic-performances-and-theatre-transfer": {},
    "st-chp2-seciv-l139-152-orbaan-partly-publishes-1631-inventory": {},
    "st-chp2-seciv-l139-152-palace-theatre-as-striking-feature": {},
    "st-chp2-seciv-l139-152-sacchi-illustrates-bentivoglio-joust-book": {},
    "st-chp2-seciv-l139-152-sacchi-paints-joust-culmination": {},
    "st-chp2-seciv-l139-152-taddeo-marriage-and-palestrina-rights": {},
    "st-chp2-seciv-l139-152-taddeo-prefecture-ceremony-and-tassi-painting": {},
    "st-chp2-seciv-l139-152-tessin-account-locator-and-date": {},
    "st-chp2-seciv-l139-152-waterhouse-points-author-to-sale-catalogue": {},
    "st-chp2-seciv-l139-152-cantalamessa-bibliographic-pointer": {
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-4785",
    },
    "st-chp2-seciv-l139-152-barberini-wealth-and-revival-interpretation": {
        "relation_candidate_note": (
            "Haskell links Barberini wealth consumption to harm to unnamed ‘oldest families’; "
            "no bounded family-group endpoint or specific mechanism is identified, so the object remains open."
        ),
    },
    "st-chp2-seciv-l139-152-joust-pastiche-receives-delighted-approval": {
        "relation_candidate_note": (
            "The source reports approval of the joust's feudal pastiche but does not name the approving audience; "
            "the object endpoint remains open."
        ),
    },
    "st-chp2-seciv-l139-152-palace-filled-with-art-and-treasures": {
        "relation_candidate_note": (
            "The source says the palace was filled with works and treasures but identifies no bounded collection "
            "or individual object; the object endpoint remains open."
        ),
    },
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
    actual_hashes = {
        "table": sha256(STATEMENTS),
        "source": sha256(SOURCE),
        "pdf": sha256(PDF),
    }
    expected_hashes = {
        "table": EXPECTED_TABLE_SHA256,
        "source": EXPECTED_SOURCE_SHA256,
        "pdf": EXPECTED_PDF_SHA256,
    }
    if actual_hashes != expected_hashes:
        raise SystemExit(f"input hash mismatch: expected={expected_hashes}; actual={actual_hashes}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage_rows = list(csv.DictReader(handle))
    coverage = [row for row in coverage_rows if row.get("segment_id") == SEGMENT_ID]
    if len(coverage) != 1 or coverage[0].get("disposition") != "reviewed" or coverage[0].get("migration_status") != "complete":
        raise SystemExit(f"coverage preflight failed: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    if not {"cand-2962", "cand-4785"}.issubset(candidate_ids):
        raise SystemExit("citation endpoint candidate preflight failed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    rows, bom, newline = read_jsonl(STATEMENTS)
    selected = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    selected_by_id = {row.get("statement_id"): row for row in selected}
    if len(selected) != len(CLASSIFICATIONS) or set(selected_by_id) != set(CLASSIFICATIONS):
        raise SystemExit(
            f"statement scope mismatch: expected={len(CLASSIFICATIONS)}; "
            f"actual={len(selected)}; missing={set(CLASSIFICATIONS)-set(selected_by_id)}; "
            f"extra={set(selected_by_id)-set(CLASSIFICATIONS)}"
        )

    for statement_id, updates in CLASSIFICATIONS.items():
        row = selected_by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        if qualifiers.get("relation_candidate") is not None:
            raise SystemExit(f"statement already classified: {statement_id}")
        start = qualifiers.get("source_line_start")
        end = qualifiers.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
            raise SystemExit(f"invalid source line anchor: {statement_id}")
        source_anchor = normalize("\n".join(source_lines[start - 1:end]))
        if normalize(row.get("original_quote", "")) not in source_anchor:
            raise SystemExit(f"source quote does not match line anchor: {statement_id}")
        if "relation_candidate_note" in updates:
            if not row.get("subject_candidate_id") or row.get("object_candidate_id"):
                raise SystemExit(f"open endpoint preflight failed: {statement_id}")
        elif statement_id == "st-chp2-seciv-l139-152-cantalamessa-bibliographic-pointer":
            if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != ("cand-4785", None):
                raise SystemExit("Cantalamessa citation endpoint changed unexpectedly")
        elif not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
            raise SystemExit(f"bilateral endpoint preflight failed: {statement_id}")

    return rows, selected_by_id, bom, newline, actual_hashes


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows, selected, bom, newline, hashes = preflight()
    changes = []
    for statement_id, values in CLASSIFICATIONS.items():
        row = selected[statement_id]
        qualifiers = row.setdefault("qualifiers", {})
        before = {
            "subject_candidate_id": row.get("subject_candidate_id"),
            "object_candidate_id": row.get("object_candidate_id"),
            "relation_candidate": qualifiers.get("relation_candidate"),
            "relation_candidate_note": qualifiers.get("relation_candidate_note"),
        }
        row["subject_candidate_id"] = values.get("subject_candidate_id", row.get("subject_candidate_id"))
        row["object_candidate_id"] = values.get("object_candidate_id", row.get("object_candidate_id"))
        qualifiers["relation_candidate"] = True
        if "relation_candidate_note" in values:
            qualifiers["relation_candidate_note"] = values["relation_candidate_note"]
        after = {
            "subject_candidate_id": row.get("subject_candidate_id"),
            "object_candidate_id": row.get("object_candidate_id"),
            "relation_candidate": qualifiers.get("relation_candidate"),
            "relation_candidate_note": qualifiers.get("relation_candidate_note"),
        }
        changes.append({"statement_id": statement_id, "before": before, "after": after})

    if args.dry_run:
        print(json.dumps({"mode": "dry-run", "input_sha256": hashes, "updates": changes}, ensure_ascii=False, indent=2))
        return

    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    if sha256(STATEMENTS) != EXPECTED_TABLE_SHA256:
        raise SystemExit("table changed after preflight; refusing to apply")
    shutil.copy2(STATEMENTS, BACKUP)
    write_jsonl(STATEMENTS, rows, bom, newline)
    print(json.dumps({
        "mode": "applied",
        "backup": str(BACKUP.relative_to(ROOT)),
        "input_sha256": EXPECTED_TABLE_SHA256,
        "output_sha256": sha256(STATEMENTS),
        "updated_statements": len(changes),
        "changes": changes,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
