from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l141-145"
SEGMENT_SHA = "6ee183c4a1a0fb2eacd040ac7a9d12a50fc521cd13caabbc49aeaa15ebf3645b"
SOURCE_SHA = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l141-145-assessments-20261012"
EXPECTED = {
    "book-statements.jsonl": "99e72dcba8f05a176db6657a66c64b4f2c0a7aa686e50acdf8206de42dce9603",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "6f07c527e14642fd0d702629b67139a17ad4e1a547b113181aab9cf37561c2f2",
}
UNSET_IDS = {
    "st-chp2-secii-l141-145-pope-bewildered-and-adamant",
    "st-chp2-secii-l141-145-reni-picture-evaluation",
    "st-chp2-secii-l141-145-riches-and-devotion-authorial-context",
}
RECEPTION_ID = "st-chp2-secii-l141-145-reni-picture-reception"
FALSE_NOTES = {
    "st-chp2-secii-l141-145-pope-bewildered-and-adamant": (
        "Haskell's conjecture that Urban VIII must have been bewildered and his description of him as adamant are "
        "authorial psychological characterization, not a relation claim; preserve the stated uncertainty."
    ),
    "st-chp2-secii-l141-145-reni-picture-evaluation": (
        "The description of the painting's grace as classical and somewhat mannered is Haskell's aesthetic judgment. "
        "The separate claim about its reputation is recorded in the linked reception statement."
    ),
    "st-chp2-secii-l141-145-riches-and-devotion-authorial-context": (
        "This is Haskell's broad social interpretation of the Capuchins' opposition; it does not identify a bounded "
        "society or assert a relation between independently identified entities."
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def classify(row: dict, value: bool, note: str, candidate_ids: list[str]) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = value
    qualifiers["relation_candidate_note"] = note
    qualifiers["mentioned_candidate_ids"] = candidate_ids
    if not value:
        qualifiers.pop("open_endpoint_reason", None)


def append_unique(items: list[str], value: str) -> list[str]:
    return items if value in items else [*items, value]


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve remaining classifications and separate Reni's reception claim in CHP-2 L141-145.")
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected printed p.43 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected p.43 unset statement set: {sorted(unset)}")
    if RECEPTION_ID in statement_by_id:
        raise SystemExit(f"planned statement ID already exists: {RECEPTION_ID}")
    if "cand-4544" not in candidate_ids:
        raise SystemExit("the Guido Reni painting candidate is missing")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[140:145])
    aesthetic_quote = "a work whose classical and somewhat mannered grace"
    reception_quote = "made it among the most admired of its time1;"
    if aesthetic_quote not in source_text or reception_quote not in source_text:
        raise SystemExit("the planned Reni quote split does not match protected p.43 source lines")

    aesthetic = statement_by_id["st-chp2-secii-l141-145-reni-picture-evaluation"]
    picture_sent = statement_by_id["st-chp2-secii-l141-145-reni-archangel-picture-sent"]
    citation_id = "st-chp2-secii-l147-193-cite-malvasiaII-p26"
    citation = statement_by_id.get(citation_id)
    if not citation:
        raise SystemExit("the p.43 Malvasia citation statement is missing")
    if picture_sent.get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("the Reni painting's commission/sending relation is no longer classified")
    if len([row for row in coverage if row.get("segment_id") == SEGMENT_ID]) != 1:
        raise SystemExit("expected one p.43 coverage row")
    if "m-chp2-secii-l141-145-0031" not in {row["mention_id"] for row in mentions}:
        raise SystemExit("the existing precise mention of the Reni painting is missing")

    for statement_id, note in FALSE_NOTES.items():
        row = statement_by_id[statement_id]
        subject = row.get("subject_candidate_id")
        mentioned = [subject] if subject else []
        if statement_id == "st-chp2-secii-l141-145-riches-and-devotion-authorial-context":
            mentioned = ["cand-3405"]
        classify(row, False, note, mentioned)

    aesthetic["predicate"] = "authorial_artistic_assessment"
    aesthetic["qualifiers"]["claim"] = "Haskell describes the painting's grace as classical and somewhat mannered."
    aesthetic["qualifiers"]["text_layer"] = "authorial aesthetic evaluation"
    aesthetic["qualifiers"]["qualification"] = (
        "This is Haskell's aesthetic judgment; the reported reception claim is separated into its own statement."
    )
    aesthetic["original_quote"] = aesthetic_quote
    aesthetic["qualifiers"].pop("footnote_marker", None)
    aesthetic["qualifiers"].pop("footnote_segment", None)
    aesthetic["qualifiers"].pop("linked_note_statement_ids", None)
    aesthetic["qualifiers"]["linked_statement_ids"] = [
        item for item in aesthetic["qualifiers"].get("linked_statement_ids", []) if item != citation_id
    ]

    reception = {
        "statement_id": RECEPTION_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-4544",
        "object_candidate_id": None,
        "predicate": "received_historical_admiration_reported",
        "qualifiers": {
            "source_line_start": 144,
            "source_line_end": 144,
            "claim": "Haskell reports that Guido Reni's The Archangel Michael trampling on the Devil was among the most admired works of its time.",
            "speaker": "Haskell",
            "text_layer": "authorial reputation report",
            "qualification": "This is Haskell's account of the picture's reputation; the phrase is not an independently verified reception history.",
            "print_page": "43",
            "pdf_page": 28,
            "footnote_marker": 1,
            "footnote_segment": "chp-2:02_CHP-2_sec_ii:l147-193",
            "ocr_note": aesthetic["qualifiers"].get("ocr_note", ""),
            "linked_statement_ids": [picture_sent["statement_id"], citation_id],
            "linked_note_statement_ids": [citation_id],
        },
        "original_quote": reception_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    }
    classify(
        reception,
        True,
        "Haskell explicitly reports the work among the most admired of its time. Preserve this as source-attributed reception, separate from his aesthetic judgment; do not infer a named audience.",
        ["cand-4544"],
    )
    reception["qualifiers"]["open_endpoint_reason"] = (
        "The work's admirers are implied by the reception claim but no individuals, institution, or bounded audience group are named."
    )
    statements.insert(statements.index(aesthetic) + 1, reception)
    picture_sent["qualifiers"]["linked_statement_ids"] = append_unique(
        picture_sent["qualifiers"].get("linked_statement_ids", []), RECEPTION_ID
    )
    for key in ("linked_body_statement_ids", "linked_statement_ids"):
        values = [item for item in citation["qualifiers"].get(key, []) if item != aesthetic["statement_id"]]
        citation["qualifiers"][key] = append_unique(values, RECEPTION_ID)
    if any(
        row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
        for row in statements
    ):
        raise SystemExit("p.43 segment still has unset relation_candidate values")
    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("statement IDs are not unique after write preparation")

    coverage_row = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    coverage_note = (
        " S2 follow-up classifies the Pope's inferred bewilderment and Haskell's broad riches/devotion interpretation as non-relational. "
        "The Reni sentence is split: aesthetic description remains an authorial assessment, while 'among the most admired of its time' "
        "is a source-attributed reception candidate with an unnamed, open audience endpoint. The existing Malvasia II, p.26 citation "
        "and exact painting mention are linked to the separated claim. Printed p.43 (PDF page 28) confirms footnote marker 1 follows 'time'; S0 remains unchanged."
    )
    if coverage_note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_note

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    print(json.dumps({
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "classified_unset_ids": sorted(UNSET_IDS),
        "new_statement_ids": [RECEPTION_ID],
        "new_statement_relation_candidate": True,
        "new_candidates": 0,
        "new_mentions": 0,
        "reception_audience_endpoint": "open; no named or bounded audience inferred",
        "citation_crosslinks_updated": True,
        "remaining_unset_in_segment": [],
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if written_by_id[RECEPTION_ID]["qualifiers"].get("relation_candidate") is not True:
            raise SystemExit("the Reni reception classification was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
        "statement_count": len(statements),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
