from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-seci-l71-80-scipione-endpoints-20261010"
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l71-80"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"
EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "81f72dbcd0c83e6960c079d6d3438e062c0130b0bfe6d271ad528b097ec446b9",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "e6179e8cf85a5313d16bad9b24a2d7a529b6d368a39ff6339270181f084888ad",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE_FILE: "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}

TARGETS = {
    "st-chp2-seci-l71-80-arpino-picture-seizure": ("cand-0397", "cand-4278", "picture_confiscation_reported", "He obtained 105 pictures"),
    "st-chp2-seci-l71-80-scipione-authorial-assessment": ("cand-0397", None, "authorial_characterization", "Though well-born, he was a man of few intellectual attainments"),
    "st-chp2-seci-l71-80-scipione-nephew": ("cand-0397", "cand-0393", "nephew_of_reported", "his nephew Cardinal\nScipione Borghese"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def preflight() -> list[dict]:
    for relative, expected_hash in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.is_file(), f"missing input: {relative}")
        require(sha256(path) == expected_hash, f"input hash changed: {relative}")

    rows = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(set(TARGETS) <= set(by_id), "one or more endpoint targets are missing")

    for statement_id, (old_subject, object_id, predicate, quote_anchor) in TARGETS.items():
        row = by_id[statement_id]
        require(row.get("segment_id") == SEGMENT_ID, f"segment changed for {statement_id}")
        require(row.get("subject_candidate_id") == old_subject, f"subject endpoint changed for {statement_id}")
        require(row.get("object_candidate_id") == object_id, f"object endpoint changed for {statement_id}")
        require(row.get("predicate") == predicate, f"predicate changed for {statement_id}")
        require(quote_anchor in row.get("original_quote", ""), f"quote anchor changed for {statement_id}")

    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidates = {row.get("candidate_id"): row for row in csv.DictReader(handle)}
    require(candidates.get("cand-0394", {}).get("canonical_name") == "Borghese, Cardinal Scipione",
            "body-mentioned Scipione candidate changed")
    require(candidates.get("cand-0397", {}).get("index_entry_id") == "B.csv#244",
            "specialized index sub-entry candidate changed")

    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as handle:
        mentions = list(csv.DictReader(handle))
    require(any(row.get("segment_id") == SEGMENT_ID and row.get("candidate_id") == "cand-0394"
                and row.get("surface_form") == "Cardinal Scipione Borghese" for row in mentions),
            "the explicit body mention for cand-0394 is missing")

    source_lines = (ROOT / SOURCE_FILE).read_text(encoding="utf-8").splitlines()
    for statement_id, (_, _, _, quote_anchor) in TARGETS.items():
        row = by_id[statement_id]
        first = row["qualifiers"]["source_line_start"]
        last = row["qualifiers"]["source_line_end"]
        excerpt = "\n".join(source_lines[first - 1:last])
        require(quote_anchor in excerpt, f"source anchor changed for {statement_id}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Map three chapter 2 body statements to the explicit Scipione candidate mentioned in their segment.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted endpoint corrections")
    args = parser.parse_args()
    rows = preflight()
    updated = [dict(row) for row in rows]
    for row in updated:
        if row.get("statement_id") in TARGETS:
            row["subject_candidate_id"] = "cand-0394"

    print(f"PREVIEW: map 3 body statements in {SEGMENT_ID} from index sub-entry candidate cand-0397 to explicit body candidate cand-0394")
    print("  cand-0397 remains in the candidate table as the distinct B.csv#244 sub-entry; no candidates or mentions are merged.")
    print("  no predicate, relation flag, quotation or statement-count changes")
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the endpoint corrections.")
        return

    require(not BACKUP.exists(), f"backup already exists: {BACKUP.relative_to(ROOT)}")
    shutil.copy2(STATEMENTS, BACKUP)
    payload = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=STATEMENTS.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, STATEMENTS)
    print(f"APPLIED; backup: {BACKUP.relative_to(ROOT)}")
    print(f"new SHA-256: {sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
