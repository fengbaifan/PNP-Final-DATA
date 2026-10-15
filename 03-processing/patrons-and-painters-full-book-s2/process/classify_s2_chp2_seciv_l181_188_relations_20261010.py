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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l181-188"
EXPECTED_TABLE_SHA256 = "77958ab3ef7137e79a9f3b48b15ddd794cdf3f9bc3da4d814e4b8f02ce5a2c7c"
EXPECTED_SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
EXPECTED_PDF_SHA256 = "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-iv-l181-188-20261010"
SPLIT_SOURCE_ID = "st-chp2-seciv-l181-188-singers-and-spectacle-excited-public"
SPLIT_NEW_ID = "st-chp2-seciv-l181-188-spectacle-excited-public"
LANDI_ID = "st-chp2-seciv-l181-188-landi-music-characterized-as-indifferent"
SPECTATOR_ID = "st-chp2-seciv-l181-188-anonymous-spectator-describes-staged-flood"

CLASSIFICATIONS = {
    SPECTATOR_ID: True,
    "st-chp2-seciv-l181-188-bernini-built-provisional-theatre": True,
    "st-chp2-seciv-l181-188-bernini-in-charge-of-s-alessio-decor": True,
    "st-chp2-seciv-l181-188-bernini-plans-seem-conservative": True,
    "st-chp2-seciv-l181-188-bernini-wrote-and-directed-play-group": True,
    "st-chp2-seciv-l181-188-chi-soffre-speri-seen-by-milton": True,
    "st-chp2-seciv-l181-188-guests-commented-on-bernini-satirical-licence": True,
    "st-chp2-seciv-l181-188-inondazione-performed-carnival-1638": True,
    LANDI_ID: False,
    "st-chp2-seciv-l181-188-play-inspired-by-prior-year-flood": True,
    "st-chp2-seciv-l181-188-roman-spectators-impressed-by-s-alessio-scenes": True,
    "st-chp2-seciv-l181-188-rospigliosi-became-clement-ix": True,
    "st-chp2-seciv-l181-188-rospigliosi-dramas-religious-then-profane": True,
    "st-chp2-seciv-l181-188-rospigliosi-held-urban-administration-posts": True,
    "st-chp2-seciv-l181-188-rospigliosi-known-for-poems-and-verse-dramas": True,
    "st-chp2-seciv-l181-188-s-alessio-stimulated-sensational-effects": True,
    SPLIT_SOURCE_ID: True,
    "st-chp2-seciv-l181-188-spectator-accounts-used-because-no-drawings-survive": True,
}

NOTES = {
    LANDI_ID: (
        "This is Haskell's appraisal of unnamed music associated with Landi and other composers, "
        "not a relation between Landi and Rospigliosi's verse-drama group. No score or bounded "
        "music-work group is identified, so the unrelated archive endpoint is cleared."
    ),
    "st-chp2-seciv-l181-188-bernini-plans-seem-conservative": (
        "The possessive 'his surviving plans' links the plans to Bernini; retain that relation "
        "candidate while preserving Haskell's present-day aesthetic assessment."
    ),
    SPLIT_SOURCE_ID: (
        "The source identifies the singers as one stimulus that excited the public; this scalar "
        "candidate is separated from the following spectacle claim."
    ),
    SPECTATOR_ID: (
        "This is an unnamed contemporary spectator's account of theatrical effects, not a real "
        "flood or actual danger to the audience."
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
    required_candidates = {"cand-0209", "cand-0296", "cand-1357", "cand-1668", "cand-2263", "cand-4782", "cand-4793", "cand-4811", "cand-4812", "cand-4813", "cand-4814", "cand-4815", "cand-4816", "cand-4817", "cand-4818", "cand-4819", "cand-4820", "cand-4821", "cand-4822", "cand-4823", "cand-4824", "cand-4825", "cand-4826"}
    if not required_candidates.issubset(candidate_ids):
        raise SystemExit(f"candidate preflight failed: missing={required_candidates-candidate_ids}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    rows, bom, newline = read_jsonl(STATEMENTS)
    selected = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    selected_by_id = {row.get("statement_id"): row for row in selected}
    expected_ids = set(CLASSIFICATIONS)
    if len(selected) != 19 or not expected_ids.issubset(selected_by_id):
        raise SystemExit(
            f"statement scope mismatch: expected 19 total / {len(expected_ids)} unclassified; "
            f"actual={len(selected)}; missing={expected_ids-set(selected_by_id)}"
        )
    preclassified = set(selected_by_id) - expected_ids
    if len(preclassified) != 1 or any(
        (selected_by_id[statement_id].get("qualifiers") or {}).get("relation_candidate") is not True
        for statement_id in preclassified
    ):
        raise SystemExit(f"preclassified row changed unexpectedly: {preclassified}")
    if any(row.get("statement_id") == SPLIT_NEW_ID for row in rows):
        raise SystemExit(f"split statement already exists: {SPLIT_NEW_ID}")
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

    landi = selected_by_id[LANDI_ID]
    if (landi.get("subject_candidate_id"), landi.get("object_candidate_id")) != ("cand-1357", "cand-4811"):
        raise SystemExit("Landi music endpoints changed unexpectedly")
    split_row = selected_by_id[SPLIT_SOURCE_ID]
    if (split_row.get("subject_candidate_id"), split_row.get("object_candidate_id")) != ("cand-4816", "cand-4815"):
        raise SystemExit("audience-stimulus endpoints changed unexpectedly")
    spectator = selected_by_id[SPECTATOR_ID]
    if (spectator.get("qualifiers") or {}).get("source_line_end") != 188:
        raise SystemExit("spectator quote anchor changed unexpectedly")
    quote = spectator.get("original_quote", "")
    if "‘When the curtain rose,’" not in quote or "without harming anyone...." not in quote:
        raise SystemExit("spectator quotation boundary markers are missing")
    return rows, selected_by_id, source_lines, bom, newline, actual_hashes


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows, selected, source_lines, bom, newline, hashes = preflight()
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
        }
        qualifiers["relation_candidate"] = is_relation
        if statement_id in NOTES:
            qualifiers["relation_candidate_note"] = NOTES[statement_id]
        if statement_id == LANDI_ID:
            row["object_candidate_id"] = None
        if statement_id == SPLIT_SOURCE_ID:
            row["object_candidate_id"] = "cand-4814"
            row["predicate"] = "audience-excited-by-singers"
            qualifiers["claim"] = (
                "Haskell says the palace-theatre public were excited by the singers, "
                "rather than by the librettos or music."
            )
            qualifiers["ocr_corrections"] = [{
                "source_line": 184,
                "ocr": ". nor",
                "print": "nor",
                "basis": "CHP-2.pdf physical page 47",
            }]
            split_copy = deepcopy(row)
            split_copy["statement_id"] = SPLIT_NEW_ID
            split_copy["object_candidate_id"] = "cand-4815"
            split_copy["predicate"] = "audience-excited-by-spectacle-especially"
            split_qualifiers = split_copy.setdefault("qualifiers", {})
            split_qualifiers["claim"] = (
                "Haskell says the spectacle excited the palace-theatre public above all; "
                "the librettos and music did not chiefly excite them."
            )
            split_qualifiers["relation_candidate_note"] = (
                "The source gives spectacle the strongest emphasis as an audience stimulus; "
                "this scalar candidate is separated from the singers claim."
            )
        if statement_id == SPECTATOR_ID:
            quote = row["original_quote"]
            start = quote.find("‘When the curtain rose,’")
            end_marker = "without harming anyone...."
            end = quote.find(end_marker, start)
            row["original_quote"] = quote[start:end + len(end_marker)]
            qualifiers["source_line_end"] = 186
        after = {
            "subject_candidate_id": row.get("subject_candidate_id"),
            "object_candidate_id": row.get("object_candidate_id"),
            "predicate": row.get("predicate"),
            "relation_candidate": qualifiers.get("relation_candidate"),
            "relation_candidate_note": qualifiers.get("relation_candidate_note"),
        }
        changes.append({"statement_id": statement_id, "before": before, "after": after})

    if split_copy is None:
        raise SystemExit("expected split statement was not prepared")
    source_line = source_lines[183]
    if normalize(split_copy["original_quote"]) not in normalize(source_line):
        raise SystemExit("split statement quote does not match printed source line")
    split_index = next(i for i, row in enumerate(rows) if row.get("statement_id") == SPLIT_SOURCE_ID)
    rows.insert(split_index + 1, split_copy)
    changes.append({"new_statement_id": SPLIT_NEW_ID, "subject_candidate_id": "cand-4816", "object_candidate_id": "cand-4815", "relation_candidate": True})

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
