from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-2.pdf"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l171-179"
EXPECTED_TABLE_SHA256 = "b430d3b35669dd81245454218c940934e9039c261c93ef1899c0c47662a54bcd"
EXPECTED_SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
EXPECTED_PDF_SHA256 = "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-iv-l171-179-20261010"
SPLIT_SOURCE_ID = "st-chp2-seciv-l171-179-prelates-admire-performance"
SPLIT_NEW_ID = "st-chp2-seciv-l171-179-prelates-admire-castrati"

CLASSIFICATIONS = {
    "st-chp2-seciv-l171-179-bellori-nota-reports-poussin-work-owned": True,
    "st-chp2-seciv-l171-179-bouchard-attends-first-performance-continuation": True,
    "st-chp2-seciv-l171-179-bouchard-room-description": True,
    "st-chp2-seciv-l171-179-bracciolini-authored-elettione": True,
    "st-chp2-seciv-l171-179-claude-will-bequeathed-two-drawings": True,
    "st-chp2-seciv-l171-179-claude-will-quote-good-advice": True,
    "st-chp2-seciv-l171-179-poussin-interpreted-rospigliosi-poems": True,
    "st-chp2-seciv-l171-179-poussin-works-convey-view-of-destiny": True,
    SPLIT_SOURCE_ID: True,
    "st-chp2-seciv-l171-179-rospigliosi-accompanied-francesco-to-spain": True,
    "st-chp2-seciv-l171-179-rospigliosi-appreciated-claude-alongside-poussin": True,
    "st-chp2-seciv-l171-179-rospigliosi-commentary-on-elettione": True,
    "st-chp2-seciv-l171-179-rospigliosi-commentary-published-1628-age-28": False,
    "st-chp2-seciv-l171-179-rospigliosi-evidently-close-friend-of-claude": True,
    "st-chp2-seciv-l171-179-rospigliosi-gained-barberini-favour": True,
    "st-chp2-seciv-l171-179-rospigliosi-owned-three-claude-landscapes": True,
    "st-chp2-seciv-l171-179-rospigliosi-patron-of-painters-especially-poussin": True,
    "st-chp2-seciv-l171-179-rospigliosi-poet-and-art-lover-at-urban-court": True,
    "st-chp2-seciv-l171-179-rospigliosi-tuscan": True,
    "st-chp2-seciv-l171-179-rospigliosi-wrote-s-alessio-libretto": True,
    "st-chp2-seciv-l171-179-s-alessio-performance-and-plot": True,
    "st-chp2-seciv-l171-179-young-barberini-cardinals-greet-guests": True,
}

NOTES = {
    "st-chp2-seciv-l171-179-poussin-works-convey-view-of-destiny": (
        "This is Haskell's interpretation of themes translated into Poussin's works; "
        "the interpretation is not attributed to the artist himself."
    ),
    SPLIT_SOURCE_ID: (
        "The source says the prelates admired the beauty of the pages assigned women's roles; "
        "the object endpoint is the existing pages group candidate."
    ),
    "st-chp2-seciv-l171-179-rospigliosi-evidently-close-friend-of-claude": (
        "Haskell infers the friendship from Claude's bequest and quoted thanks; retain the "
        "author's inferential qualification."
    ),
    "st-chp2-seciv-l171-179-young-barberini-cardinals-greet-guests": (
        "The statement concerns two unnamed young Barberini cardinals in the performance event; "
        "the family endpoint records affiliation and does not identify either cardinal."
    ),
    "st-chp2-seciv-l171-179-rospigliosi-commentary-published-1628-age-28": (
        "This statement records the commentary's publication year and the author's age at that "
        "date. The work-author relation is stated separately; this row is bibliographic and "
        "biographical metadata, not an additional relation between its endpoints."
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
    return [json.loads(line) for line in decoded.splitlines() if line.strip()], bom, newline


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
        coverage = [row for row in csv.DictReader(handle) if row.get("segment_id") == SEGMENT_ID]
    if len(coverage) != 1 or coverage[0].get("disposition") != "reviewed" or coverage[0].get("migration_status") != "complete":
        raise SystemExit(f"coverage preflight failed: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    required_candidates = {"cand-0419", "cand-0440", "cand-0767", "cand-1984", "cand-2263", "cand-3464", "cand-3983", "cand-4730", "cand-4780", "cand-4781", "cand-4793", "cand-4794", "cand-4795", "cand-4796", "cand-4797", "cand-4801", "cand-4804", "cand-4806", "cand-4808", "cand-4809", "cand-4810"}
    if not required_candidates.issubset(candidate_ids):
        raise SystemExit(f"candidate preflight failed: missing={required_candidates-candidate_ids}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    rows, bom, newline = read_jsonl(STATEMENTS)
    selected = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    selected_by_id = {row.get("statement_id"): row for row in selected}
    expected_ids = set(CLASSIFICATIONS)
    if len(selected) != 30 or not expected_ids.issubset(selected_by_id):
        raise SystemExit(
            f"statement scope mismatch: expected 30 total / {len(expected_ids)} unclassified; "
            f"actual={len(selected)}; missing={expected_ids-set(selected_by_id)}"
        )
    preclassified = set(selected_by_id) - expected_ids
    if len(preclassified) != 8 or any(
        (selected_by_id[statement_id].get("qualifiers") or {}).get("relation_candidate") is not True
        for statement_id in preclassified
    ):
        raise SystemExit(f"preclassified rows changed unexpectedly: {preclassified}")
    if any(row.get("statement_id") == SPLIT_NEW_ID for row in rows):
        raise SystemExit(f"new split statement already exists: {SPLIT_NEW_ID}")
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    for statement_id in expected_ids:
        row = selected_by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        if qualifiers.get("relation_candidate") is not None:
            raise SystemExit(f"statement already classified: {statement_id}")
        start, end = qualifiers.get("source_line_start"), qualifiers.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
            raise SystemExit(f"invalid source line anchor: {statement_id}")
        source_anchor = normalize("\n".join(source_lines[start - 1:end]))
        if normalize(row.get("original_quote", "")) not in source_anchor:
            raise SystemExit(f"source quote does not match line anchor: {statement_id}")
        if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
            raise SystemExit(f"bilateral endpoint preflight failed: {statement_id}")

    split_row = selected_by_id[SPLIT_SOURCE_ID]
    if (split_row.get("subject_candidate_id"), split_row.get("object_candidate_id")) != ("cand-4808", "cand-4780"):
        raise SystemExit("prelate statement endpoints changed unexpectedly")
    if not all(token in split_row.get("original_quote", "") for token in ("prelates", "pages", "castrati")):
        raise SystemExit("prelate statement quote no longer contains the three source mentions")
    return rows, selected_by_id, bom, newline, actual_hashes


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows, selected, bom, newline, hashes = preflight()
    changes = []
    split_copy = None
    for statement_id, is_relation in CLASSIFICATIONS.items():
        row = selected[statement_id]
        qualifiers = row.setdefault("qualifiers", {})
        before = {
            "subject_candidate_id": row.get("subject_candidate_id"),
            "object_candidate_id": row.get("object_candidate_id"),
            "predicate": row.get("predicate"),
            "relation_candidate": qualifiers.get("relation_candidate"),
            "relation_candidate_note": qualifiers.get("relation_candidate_note"),
        }
        qualifiers["relation_candidate"] = is_relation
        if statement_id in NOTES:
            qualifiers["relation_candidate_note"] = NOTES[statement_id]
        if statement_id == SPLIT_SOURCE_ID:
            row["object_candidate_id"] = "cand-4809"
            row["predicate"] = "audience-admires-pages-in-women-roles"
            qualifiers["claim"] = "Bouchard’s account says the prelates admired the beauty of the pages assigned the women’s roles."
            qualifiers["mentioned_candidate_ids"] = ["cand-4808", "cand-4809"]
            split_copy = deepcopy(row)
            split_copy["statement_id"] = SPLIT_NEW_ID
            split_copy["object_candidate_id"] = "cand-4810"
            split_copy["predicate"] = "audience-admires-castrati-in-women-roles"
            split_copy_qualifiers = split_copy.setdefault("qualifiers", {})
            split_copy_qualifiers["claim"] = "Bouchard’s account says the prelates admired the beauty of the castrati assigned the women’s roles."
            split_copy_qualifiers["mentioned_candidate_ids"] = ["cand-4808", "cand-4810"]
            split_copy_qualifiers["relation_candidate_note"] = (
                "The source says the prelates admired the beauty of castrati assigned women's roles; "
                "the object endpoint is the existing castrati group candidate."
            )
        after = {
            "subject_candidate_id": row.get("subject_candidate_id"),
            "object_candidate_id": row.get("object_candidate_id"),
            "predicate": row.get("predicate"),
            "relation_candidate": qualifiers.get("relation_candidate"),
            "relation_candidate_note": qualifiers.get("relation_candidate_note"),
        }
        changes.append({"statement_id": statement_id, "before": before, "after": after})

    split_index = next(i for i, row in enumerate(rows) if row.get("statement_id") == SPLIT_SOURCE_ID)
    rows.insert(split_index + 1, split_copy)
    changes.append({"new_statement_id": SPLIT_NEW_ID, "subject_candidate_id": "cand-4808", "object_candidate_id": "cand-4810", "relation_candidate": True})

    if args.dry_run:
        print(json.dumps({"mode": "dry-run", "input_sha256": hashes, "updated_existing": len(CLASSIFICATIONS), "added_statements": 1, "changes": changes}, ensure_ascii=False, indent=2))
        return

    if sha256(STATEMENTS) != EXPECTED_TABLE_SHA256:
        raise SystemExit("table changed after preflight; refusing to apply")
    shutil.copy2(STATEMENTS, BACKUP)
    write_jsonl(STATEMENTS, rows, bom, newline)
    print(json.dumps({
        "mode": "applied",
        "backup": str(BACKUP.relative_to(ROOT)),
        "input_sha256": EXPECTED_TABLE_SHA256,
        "output_sha256": sha256(STATEMENTS),
        "updated_existing": len(CLASSIFICATIONS),
        "added_statements": 1,
        "relation_true_added": sum(CLASSIFICATIONS.values()) + 1,
        "relation_false_added": sum(not value for value in CLASSIFICATIONS.values()),
        "changes": changes,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
