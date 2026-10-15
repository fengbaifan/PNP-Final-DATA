from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch16-p375-residual-20261015")
EXPECTED_SHA256 = "044eb9db627c41e7450c7473063143ca1979b7496ff70872e496f736acd56660"
SEGMENT = "chp-16:16_CHP-16_intro:l24-36"


EDITS = {
    "st-chp16-p375-della-lena-dealers-and-scholarship": {
        "subject_candidate_id": "cand-1387",
        "object_candidate_id": None,
        "predicate": "placed_on_fringe_of_scholarship",
        "original_quote": "The Abate Giacomo della Lena, for instance, was also on the fringes of scholarship.4",
        "claim": "Haskell places Abate Giacomo della Lena on the fringes of scholarship.",
        "mentioned_candidate_ids": ["cand-1387"],
        "relation_candidate": False,
        "relation_candidate_note": "This is Haskell's qualitative characterization of Della Lena's scholarly position, not a relation to an identified institution or scholar; the adjacent dealer-cultural claim is recorded separately.",
        "open_endpoint_reason": None,
    },
    "st-chp16-p375-historian-della-lena-german-dealings": {
        "relation_candidate": True,
        "relation_candidate_note": "The reported comment explicitly connects Della Lena with picture dealing, mainly with Germans; retain both the trade claim and its attribution to an unnamed nineteenth-century historian through Haskell.",
        "open_endpoint_reason": "The German dealers or clients are not named or enumerated; Haskell relays the claim through an unidentified nineteenth-century historian, and no individual transaction is specified.",
    },
    "st-chp16-p375-della-lena-life-and-venice-office": {
        "subject_candidate_id": "cand-1387",
        "object_candidate_id": "cand-2719",
        "predicate": "spent_most_of_life_in_venice_served_as_spanish_vice_consul_and_died_there_1807",
        "original_quote": "but he spent most of his life in Venice, where he acted as Spanish vice-consul and where he died in 1807.",
        "claim": "Haskell says Della Lena spent most of his life in Venice, acted there as Spanish vice-consul, and died there in 1807.",
        "mentioned_candidate_ids": ["cand-1387", "cand-2719"],
        "relation_candidate": True,
        "relation_candidate_note": "Haskell directly locates Della Lena's long residence, vice-consular role, and death in Venice; retain the reported role and death year without inferring appointment dates.",
        "open_endpoint_reason": None,
    },
    "st-chp16-p375-della-lena-arts-and-sciences-theory": {
        "relation_candidate": False,
        "relation_candidate_note": "This is Della Lena's quoted conceptual argument about artistic and scientific value; the letter to Ortes is recorded separately, and the argument itself does not assert a relation between tracked entities.",
        "open_endpoint_reason": None,
    },
    "st-chp16-p375-guardi-flourishes-in-della-lena-world": {
        "object_candidate_id": "cand-11543",
        "predicate": "guardi_could_flourish_in_venetian_art_atmosphere_described_by_haskell",
        "mentioned_candidate_ids": ["cand-1239", "cand-11543"],
        "relation_candidate": True,
        "relation_candidate_note": "Haskell explicitly links Guardi's ability to flourish to the Venetian artistic atmosphere discussed in this passage; preserve this as an attributed aesthetic-context relation, including the contrast with literal-minded English viewers.",
        "open_endpoint_reason": None,
    },
}


NEW_ROWS = {
    "st-chp16-p375-similar-dealers-sustain-venetian-art-tradition": {
        "statement_id": "st-chp16-p375-similar-dealers-sustain-venetian-art-tradition",
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": "cand-11543",
        "predicate": "similar_dealers_tastes_helped_sustain_colour_and_fantasy_in_venetian_art",
        "qualifiers": {
            "source_line_start": 30,
            "source_line_end": 30,
            "printed_page": 375,
            "pdf_physical_page": 3,
            "claim": "Haskell says the tastes of many dealers similar to Sasso helped keep colour and fantasy alive in Venetian art.",
            "speaker": "Haskell",
            "text_layer": "authorial interpretation",
            "qualification": "This is a broad cultural attribution to unnamed dealers; Sasso is identified as the best known to English visitors, not as the sole cause.",
            "mentioned_candidate_ids": ["cand-2364", "cand-11543"],
            "relation_candidate": True,
            "relation_candidate_note": "The source directly links the tastes of dealers of Sasso's kind to sustaining the Venetian art tradition's colour and fantasy; retain the group-level relation without assigning it to individual dealers.",
            "open_endpoint_reason": "The dealers other than Sasso are unnamed and unenumerated; the Venetian art tradition is represented by existing candidate cand-11543.",
        },
        "original_quote": "Sasso was the best known of such dealers to the English, but there were many others of a similar kind, whose tastes helped to keep alive a love of colour and fantasy in Venetian art.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
    },
    "st-chp16-p375-della-lena-born-in-lucca": {
        "statement_id": "st-chp16-p375-della-lena-born-in-lucca",
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-1387",
        "object_candidate_id": "cand-1454",
        "predicate": "born_in_lucca_in_1732",
        "qualifiers": {
            "source_line_start": 31,
            "source_line_end": 31,
            "printed_page": 375,
            "pdf_physical_page": 3,
            "claim": "Haskell says Della Lena was born in Lucca in 1732.",
            "speaker": "Haskell",
            "text_layer": "authorial report",
            "qualification": "This records Haskell's stated birthplace and year; it is not an independent verification of the biographical fact.",
            "mentioned_candidate_ids": ["cand-1387", "cand-1454"],
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly states Della Lena's birth in Lucca; retain the person-to-place connection and stated year.",
        },
        "original_quote": "Della Lena had been born in Lucca in 1732,",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate() -> tuple[list[str], str, set[str]]:
    current_hash = sha256(TABLE)
    if current_hash != EXPECTED_SHA256:
        raise SystemExit(f"table hash mismatch: expected {EXPECTED_SHA256}, got {current_hash}")
    lines = TABLE.read_text(encoding="utf-8").splitlines(keepends=True)
    selected: dict[str, dict] = {}
    all_ids: set[str] = set()
    for line in lines:
        row = json.loads(line)
        all_ids.add(row["statement_id"])
        if row["statement_id"] in EDITS:
            selected[row["statement_id"]] = row
    if set(selected) != set(EDITS):
        raise SystemExit(f"statement set mismatch: missing={sorted(set(EDITS)-set(selected))}")
    for statement_id, row in selected.items():
        if row["segment_id"] != SEGMENT:
            raise SystemExit(f"wrong segment for {statement_id}: {row['segment_id']}")
        if row["qualifiers"].get("relation_candidate") is not None:
            raise SystemExit(f"statement is no longer unset: {statement_id}")
    duplicates = all_ids.intersection(NEW_ROWS)
    if duplicates:
        raise SystemExit(f"new statement IDs already exist: {sorted(duplicates)}")
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(stream)}
    needed = {"cand-11543", "cand-1239", "cand-1387", "cand-1454", "cand-2364", "cand-2719"}
    if not needed.issubset(candidate_ids):
        raise SystemExit(f"candidate IDs missing: {sorted(needed-candidate_ids)}")
    source = SOURCE.read_text(encoding="utf-8")
    for row in NEW_ROWS.values():
        if row["original_quote"] not in source:
            raise SystemExit(f"new source quote not present: {row['statement_id']}")
    return lines, current_hash, all_ids


def main() -> None:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    lines, before_hash, _ = validate()
    true_count = sum(edit["relation_candidate"] for edit in EDITS.values()) + sum(
        row["qualifiers"]["relation_candidate"] for row in NEW_ROWS.values()
    )
    false_count = len(EDITS) - sum(edit["relation_candidate"] for edit in EDITS.values())
    print(f"segment={SEGMENT} pending={len(EDITS)} new_atomic_statements={len(NEW_ROWS)} classify_true={true_count} classify_false={false_count}")
    for statement_id, edit in EDITS.items():
        print(f"{statement_id}: {str(edit['relation_candidate']).lower()} | {edit['relation_candidate_note']}")
    for statement_id, row in NEW_ROWS.items():
        print(f"new {statement_id}: {str(row['qualifiers']['relation_candidate']).lower()} | {row['qualifiers']['claim']}")
        if row["qualifiers"].get("open_endpoint_reason"):
            print(f"  open_endpoint_reason: {row['qualifiers']['open_endpoint_reason']}")
    print(f"before_sha256={before_hash}")
    if args.preview:
        print("preview only; no table or backup written")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    output: list[str] = []
    seen: set[str] = set()
    inserted: set[str] = set()
    for line in lines:
        row = json.loads(line)
        statement_id = row["statement_id"]
        edit = EDITS.get(statement_id)
        if edit:
            for key, value in edit.items():
                if key == "claim" or key == "mentioned_candidate_ids":
                    row["qualifiers"][key] = value
                elif key == "relation_candidate" or key == "relation_candidate_note":
                    row["qualifiers"][key] = value
                elif key == "open_endpoint_reason":
                    if value is None:
                        row["qualifiers"].pop(key, None)
                    else:
                        row["qualifiers"][key] = value
                else:
                    row[key] = value
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            seen.add(statement_id)
        else:
            output.append(line)
        if statement_id == "st-chp16-p375-della-lena-dealers-and-scholarship":
            output.append(json.dumps(NEW_ROWS["st-chp16-p375-similar-dealers-sustain-venetian-art-tradition"], ensure_ascii=False, separators=(",", ":")) + "\n")
            inserted.add("st-chp16-p375-similar-dealers-sustain-venetian-art-tradition")
        if statement_id == "st-chp16-p375-della-lena-life-and-venice-office":
            output.append(json.dumps(NEW_ROWS["st-chp16-p375-della-lena-born-in-lucca"], ensure_ascii=False, separators=(",", ":")) + "\n")
            inserted.add("st-chp16-p375-della-lena-born-in-lucca")
    if seen != set(EDITS):
        raise SystemExit(f"write set mismatch: {sorted(set(EDITS)-seen)}")
    if inserted != set(NEW_ROWS):
        raise SystemExit(f"insert set mismatch: {sorted(set(NEW_ROWS)-inserted)}")
    if sha256(TABLE) != before_hash:
        raise SystemExit("table changed after validation")

    shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
        temp_path = Path(stream.name)
        stream.writelines(output)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp_path, TABLE)
    print(f"backup={BACKUP}")
    print(f"after_sha256={sha256(TABLE)}")
    print(f"applied {len(EDITS)} classifications and added {len(NEW_ROWS)} atomic statements")


if __name__ == "__main__":
    main()
