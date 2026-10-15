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
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
SEGMENT = "chp-7:07_CHP-7_sec_i:l259-266"
STATEMENT_BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p190-l259-266-relation-classification-20261013"
MENTION_BACKUP = TABLES / "mentions.csv.bak-s2-chp7-seci-p190-l259-266-carpio-ocr-and-entity-20261013"
EXPECTED = {
    STATEMENTS: "a2d203267d07dd86f4ce0d7a83b5044426556469a35b8d5b997ee4db653bf1c9",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    MENTIONS: "d049072b3a2bc7bb9bcec784e59be00575e2b602c6dabfa7967ff18074cbcaa5",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p190-i01": "This records Haskell's general claim that Neapolitan artists were frequently employed by the viceroys in the second half of the century.",
    "st-chp7-p190-i02": "This records the viceroys' reported intermediary role for the Spanish court or important Madrid collectors.",
    "st-chp7-p190-i03": "This records Velasquez's second Italian visit in 1649 as reported by Haskell; the route and duration are not supplied here.",
    "st-chp7-p190-i04": "This records one of Velasquez's duties: acquiring paintings and sculpture for the royal Alcazar.",
    "st-chp7-p190-i05": "This records Velasquez looking at or buying pictures in the towns he visited, especially Venice, for the Alcazar; looking is not treated as purchase.",
    "st-chp7-p190-i06": "This records the unsuccessful effort to secure a living painter for Spain; the needed painter is not identified.",
    "st-chp7-p190-i07": "This records Velasquez being told to persuade Pietro da Cortona to go to Madrid and the Oratorians' existing engagement preventing the move.",
    "st-chp7-p190-i08": "This records Velasquez's unsuccessful overtures at Modena to Colonna and Mitelli for Spanish service.",
    "st-chp7-p190-i09": "This records Velasquez returning with old-master works but no painter capable of reviving fresco painting in Spain.",
    "st-chp7-p190-i10": "This records the more satisfactory employment of sculptors and their production of copies after the antique and original works for the royal collection.",
    "st-chp7-p190-i11": "This records Colonna and Mitelli arriving in Madrid and being assiduously employed in 1658 after the earlier unsuccessful overtures.",
    "st-chp7-p190-i12": "This records Haskell's comparison of Del Carpio with the other viceroys as a politically capable and distinguished art patron.",
    "st-chp7-p190-i14": "This records Del Carpio's appointment as ambassador in Rome in 1677 and the source's age statement; the appointing authority is unnamed.",
    "st-chp7-p190-i15": "This preserves the report that Del Carpio was imprisoned for two years on suspicion of involvement in an attempt on an unnamed King's life; suspicion is not treated as proof.",
    "st-chp7-p190-i17": "This records Del Carpio owning Velasquez's Toilet of Venus by 1651; Haskell's description of it as a masterpiece is retained as attribution.",
    "st-chp7-p190-i19": "This preserves Haskell's inference that Del Carpio must have welcomed the opportunity to go to Italy; it is not direct evidence of his private response.",
    "st-chp7-p190-i20": "This records Del Carpio's visit to Carlo de Rossi's picture gallery within three months of arriving in Rome.",
    "st-chp7-p190-i23": "This records Cardinal Massimi's heirs being compelled to dispose of his property; the property itself is not itemized.",
    "st-chp7-p190-i24": "This records Del Carpio's opportunity to add to his collections after Massimi's death; the source does not specify which disposed property was acquired.",
    "st-chp7-p190-i25": "This records Haskell's account that Del Carpio bought on a grand scale; the items are not specified until the following sentence and their exact provenance is not established.",
    "st-chp7-p190-i27": "This records Del Carpio's plan to have the acquired antiquities engraved; the plan is not treated as completed.",
}

FALSE_NOTES = {
    "st-chp7-p190-i13": "This is an identity and alias statement for Del Carpio, not a relation between distinct entities; retain it as evidence for S3 identity alignment.",
    "st-chp7-p190-i16": "This describes Del Carpio's personal disposition toward painting rather than a relation between distinct entities.",
    "st-chp7-p190-i18": "This is Haskell's stylistic characterization of a painting, without a separate entity-to-entity relation.",
    "st-chp7-p190-i22": "This is a biographical condition at Massimi's death, not a relation between distinct entities.",
    "st-chp7-p190-i26": "This compound acquisition sentence is decomposed into two portrait-specific claims and one antiquities-group claim; it does not assert that every acquisition came from Massimi's estate.",
    "st-chp7-p190-i28": "This is an incomplete sentence fragment; its continuation is linked to p.191 and must be read there in full.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p190-i01": "The source describes Neapolitan artists and viceroys collectively without naming the artists, individual officeholders, or commissions.",
    "st-chp7-p190-i02": "The court and Madrid collectors are generic recipients; no individual patron or commission is identified.",
    "st-chp7-p190-i04": "The works considered for the Alcazar are not individually identified.",
    "st-chp7-p190-i06": "The painter sought for Spain is unnamed and the source does not say that any specific invitee was suitable for the post.",
    "st-chp7-p190-i07": "The person who instructed Velasquez is not named; Cortona's Oratorian engagement is explicit.",
    "st-chp7-p190-i08": "The recipient or authority for the proposed Spanish service is not identified; the two painters are retained as a source-bounded pair.",
    "st-chp7-p190-i09": "The old-master works and the painter who might have revived fresco painting are not individually identified.",
    "st-chp7-p190-i10": "Finelli and Algardi are named, but the other sculptors and the copies/original works are not itemized.",
    "st-chp7-p190-i11": "The source says the painters were employed but does not name the employer or specify their tasks.",
    "st-chp7-p190-i14": "The appointing authority is not identified; the printed page confirms the age as 48.",
    "st-chp7-p190-i15": "The King and alleged attempt are unidentified; the source states suspicion only.",
    "st-chp7-p190-i23": "The heirs are an unnamed collective and the property they disposed of is not identified or itemized.",
    "st-chp7-p190-i24": "The specific collection additions and their seller or provenance are not stated at this point in the passage.",
    "st-chp7-p190-i25": "The phrase 'bought on a grand scale' is not itemized; the text does not establish the exact provenance of every later-listed item.",
}

ENDPOINT_FIXES = {
    "st-chp7-p190-i23": {"subject": ("cand-1564", "cand-6952")},
    "st-chp7-p190-i24": {"object": ("cand-6953", None)},
    "st-chp7-p190-i25": {"object": ("cand-6953", None)},
    "st-chp7-p190-i26": {
        "subject": ("cand-0573", None),
        "object": ("cand-6953", None),
    },
}

DECOMPOSED = {
    "st-chp7-p190-i26": [
        ("st-chp7-p190-i26-massimi-portrait", "cand-2712", "Cardinal Camillo Massimi"),
        ("st-chp7-p190-i26-donna-olimpia-portrait", "cand-2713", "Donna Olimpia"),
        ("st-chp7-p190-i26-antiquities", "cand-6953", "the unidentified antiquities"),
    ]
}

OCR_MENTION_FIX = {
    "mention_id": "m-chp7-p190-063",
    "candidate_id": "cand-0573",
    "surface_form": "Hs",
    "start_char": "1900",
    "end_char": "1902",
    "note": "S0 OCR reads 'Hs'; p.190 print reads 'His', referring to Del Carpio.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def build_acquisition(parent: dict, statement_id: str, work_id: str, description: str) -> dict:
    q = parent["qualifiers"]
    claim = f"Haskell says Del Carpio acquired {description}; no specific source of this item is asserted."
    mentions = ["cand-0573", work_id]
    if work_id in {"cand-2712", "cand-2713"}:
        mentions.append("cand-2709")
        mentions.append("cand-1564" if work_id == "cand-2712" else "cand-1496")
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-0573",
        "object_candidate_id": work_id,
        "predicate": "del_carpio_acquired_source_described_item",
        "qualifiers": {
            "source_line_start": q["source_line_start"],
            "source_line_end": q["source_line_end"],
            "printed_page": q["printed_page"],
            "pdf_physical_page": q["pdf_physical_page"],
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "body",
            "qualification": "The sentence follows the account of Massimi's heirs disposing of property, but does not say this specific item came from his estate.",
            "mentioned_candidate_ids": mentions,
            "decomposed_from_statement_id": parent["statement_id"],
            "relation_candidate": True,
            "relation_candidate_note": "This is an atomic item-level acquisition claim separated from the aggregate source sentence.",
        },
        "original_quote": parent["original_quote"],
        "origin": parent["origin"],
        "source_file": parent["source_file"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.190 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (259, "[Page 190]"),
        (260, "Throughout the second half of the century Neapolitan artists"),
        (261, "He had been told to try and persuade Pietro da Cortona"),
        (261, "Giuliano Finelli, Alessandro Algardi"),
        (262, "Among all the viceroys of the second half"),
        (262, "Don Gasparo de Haro y Guzman"),
        (263, "imprisoned for two years on suspicion"),
        (264, "Toilet of Venus"),
        (265, "Within three months of his arrival in Rome"),
        (266, "Del Carpio bought on a grand scale"),
        (266, "two portraits by Velasquez"),
        (266, "a very large number of antiquities"),
        (268, "[Page 191]"),
        (269, "felt an affinity between Massimi’s classical taste and his own"),
    )
    if any(text not in source_lines[index - 1] for index, text in required_source):
        raise SystemExit("p.190/p.191 source-line guards failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES) | set(FALSE_NOTES)
    if unset != expected_targets or len(unset) != 27:
        raise SystemExit(f"p.190 target set changed: {sorted(unset ^ expected_targets)}")
    prior_friend = by_id["st-chp7-p190-i21"].get("qualifiers") or {}
    if prior_friend.get("relation_candidate") is not True or not prior_friend.get("relation_candidate_note"):
        raise SystemExit("p.190 Carlo de Rossi friendship decision changed")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 260 or end > 266 or start > end:
            raise SystemExit(f"invalid p.190 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")

    continuing = by_id["st-chp7-p190-i28"]
    continuing_q = continuing.get("qualifiers") or {}
    successor = by_id["st-chp7-p191-i01"]
    successor_q = successor.get("qualifiers") or {}
    if continuing_q.get("continuation_statement_id") != successor["statement_id"]:
        raise SystemExit("p.190 continuation target changed")
    if successor_q.get("continued_from_statement_id") != continuing["statement_id"]:
        raise SystemExit("p.191 reciprocal continuation statement changed")
    if successor.get("segment_id") != "chp-7:07_CHP-7_sec_i:l268-280" or successor_q.get("source_line_start") != 269:
        raise SystemExit("p.191 continuation anchor changed")

    mention_rows = list(csv.DictReader(io.StringIO(raw[MENTIONS].decode("utf-8-sig"), newline="")))
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(mention_by_id) != len(mention_rows):
        raise SystemExit("duplicate mention IDs")
    ocr_mention = mention_by_id.get(OCR_MENTION_FIX["mention_id"])
    for field in ("candidate_id", "surface_form", "start_char", "end_char"):
        if not ocr_mention or ocr_mention.get(field) != OCR_MENTION_FIX[field]:
            raise SystemExit(f"p.190 OCR mention changed: {field}")
    if ocr_mention.get("segment_id") != SEGMENT:
        raise SystemExit("p.190 OCR mention segment changed")

    new_ids = [sid for entries in DECOMPOSED.values() for sid, _, _ in entries]
    if any(sid in by_id for sid in new_ids):
        raise SystemExit("a decomposed p.190 statement ID already exists")
    for _, work_id, _ in DECOMPOSED["st-chp7-p190-i26"]:
        if work_id not in candidate_ids or "cand-0573" not in candidate_ids:
            raise SystemExit(f"decomposed acquisition references missing candidate: {work_id}")

    for sid, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = sid in TRUE_NOTES
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]
    for sid, endpoints in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for endpoint, (expected_old, new_value) in endpoints.items():
            field = f"{endpoint}_candidate_id"
            if row.get(field) != expected_old:
                raise SystemExit(f"{sid} {field} changed: expected {expected_old!r}, got {row.get(field)!r}")
            if new_value is not None and new_value not in candidate_ids:
                raise SystemExit(f"{sid} references missing {new_value}")
            row[field] = new_value

    for sid, endpoints in ENDPOINT_FIXES.items():
        q = by_id[sid].get("qualifiers") or {}
        for endpoint, (_, new_value) in endpoints.items():
            if new_value is not None and new_value not in q.get("mentioned_candidate_ids", []):
                raise SystemExit(f"{sid} repaired endpoint {new_value} is not present in its mention set")

    for sid, entries in DECOMPOSED.items():
        parent = by_id[sid]
        parent.setdefault("qualifiers", {})["decomposed_into_statement_ids"] = [item[0] for item in entries]

    alias = by_id["st-chp7-p190-i13"].setdefault("qualifiers", {})
    alias["qualification"] = (alias.get("qualification", "") + " The name form is retained as evidence for S3 identity alignment.").strip()
    ambassador = by_id["st-chp7-p190-i14"].setdefault("qualifiers", {})
    ambassador["ocr_corrections"] = [
        {"source_line": 263, "source_form": "48?", "print_form": "48.", "note": "The print page reads 'at the age of 48.'"},
        {"source_line": 263, "source_form": "Hs", "print_form": "His", "note": "The possessive begins the next sentence and refers to Del Carpio."},
    ]
    continuing_q = continuing.setdefault("qualifiers", {})
    continuing_q["continuation_to_segment_id"] = successor["segment_id"]
    continuing_q["continuation_status"] = "closed"
    continuing_q["continuation_source_line_start"] = successor_q["source_line_start"]
    continuing_q["continuation_source_line_end"] = successor_q["source_line_end"]

    for row in mention_rows:
        if row["mention_id"] == OCR_MENTION_FIX["mention_id"]:
            row["note"] = OCR_MENTION_FIX["note"]
            break
    else:
        raise SystemExit("p.190 OCR mention row missing")

    aggregate = by_id["st-chp7-p190-i26"]
    additions = [
        build_acquisition(aggregate, statement_id, work_id, description)
        for statement_id, work_id, description in DECOMPOSED["st-chp7-p190-i26"]
    ]
    expanded_rows: list[dict] = []
    for row in rows:
        expanded_rows.append(row)
        if row["statement_id"] == aggregate["statement_id"]:
            expanded_rows.extend(additions)
    rows = expanded_rows

    output_statements = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    output_mentions = io.StringIO(newline="")
    writer = csv.DictWriter(output_mentions, fieldnames=list(mention_rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(mention_rows)
    result_statements = output_statements.encode("utf-8")
    result_mentions = output_mentions.getvalue().encode("utf-8")

    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified_existing": len(unset),
        "relation_candidate_true_new": len(TRUE_NOTES),
        "relation_candidate_false_new": len(FALSE_NOTES),
        "preclassified_true_preserved": 1,
        "decomposed_acquisition_relations_added": len(additions),
        "total_true_after_decomposition": len(TRUE_NOTES) + 1 + len(additions),
        "total_false_after_decomposition": len(FALSE_NOTES),
        "unset_in_segment": 0,
        "endpoint_fixes": ENDPOINT_FIXES,
        "ocr_mention_note_updated": OCR_MENTION_FIX["mention_id"],
        "continuation_link": "st-chp7-p190-i28 -> st-chp7-p191-i01",
        "before_sha256": {path.name: digest(raw[path]) for path in raw},
        "after_sha256": {STATEMENTS.name: digest(result_statements), MENTIONS.name: digest(result_mentions)},
    }, ensure_ascii=True))
    if not args.apply:
        return
    if STATEMENT_BACKUP.exists() or MENTION_BACKUP.exists():
        raise SystemExit("a p.190 recovery backup already exists; refusing to overwrite")
    shutil.copy2(STATEMENTS, STATEMENT_BACKUP)
    shutil.copy2(MENTIONS, MENTION_BACKUP)
    atomic_write(STATEMENTS, result_statements)
    atomic_write(MENTIONS, result_mentions)
    print(f"statement_backup={STATEMENT_BACKUP.relative_to(ROOT)}")
    print(f"mention_backup={MENTION_BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
