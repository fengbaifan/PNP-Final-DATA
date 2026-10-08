#!/usr/bin/env python3
"""Semantically adjudicate Chapter 7's 40 candidate-surface prompts.

The surface scanner is a locator only. This locked writer verifies the full
prompt partition, source spans, candidate links, and statement preconditions
before it can add candidates, mentions, or statement references.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "465463a534129239b1ec06ad0f2614cc8e553cd7639d3a1ce56911e33e06ae23",
    "04-knowledge/tables/mentions.csv": "52a5b14c3ca39e3127ed89a491452f8043cb6a9b9092d19c6898241f80d38b58",
    "04-knowledge/tables/book-statements.jsonl": "c1ba516072b1a54969c1de7a6763afe22ff984bca1469581ee49acdfa007cec3",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "scripts/audit_s2_candidate_surfaces.py": "44874e88e4940af624ad7b91b6f3e7d016f8c4083c203114e354b6e6622901ba",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    "02-sources/02-Markdown/07_CHP-7_sec_iv.md": "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
}


def accepted(segment_id: str, start: int, surface: str, candidate_id: str,
             note: str) -> dict[str, object]:
    return {
        "segment_id": segment_id,
        "start_char": start,
        "end_char": start + len(surface),
        "surface_form": surface,
        "candidate_id": candidate_id,
        "note": note,
    }


def no_write(segment_id: str, start: int, surface: str, reason: str) -> dict[str, object]:
    return {
        "segment_id": segment_id,
        "start_char": start,
        "end_char": start + len(surface),
        "surface_form": surface,
        "reason": reason,
    }


SI_21 = "chp-7:07_CHP-7_sec_i:l21-29"
SI_102 = "chp-7:07_CHP-7_sec_i:l102-111"
SI_113 = "chp-7:07_CHP-7_sec_i:l113-126"
SI_128 = "chp-7:07_CHP-7_sec_i:l128-138"
SI_140 = "chp-7:07_CHP-7_sec_i:l140-148"
SI_160 = "chp-7:07_CHP-7_sec_i:l160-168"
SI_170 = "chp-7:07_CHP-7_sec_i:l170-176"
SI_205 = "chp-7:07_CHP-7_sec_i:l205-213"
SI_232 = "chp-7:07_CHP-7_sec_i:l232-241"
SI_243 = "chp-7:07_CHP-7_sec_i:l243-257"
SI_268 = "chp-7:07_CHP-7_sec_i:l268-280"
SI_282 = "chp-7:07_CHP-7_sec_i:l282-291"
SI_293 = "chp-7:07_CHP-7_sec_i:l293-389"
SI_45 = "chp-7:07_CHP-7_sec_i:l45-59"
SIV_23 = "chp-7:07_CHP-7_sec_iv:l23-36"
SIV_48 = "chp-7:07_CHP-7_sec_iv:l48-61"
SIV_63 = "chp-7:07_CHP-7_sec_iv:l63-75"
SIV_77 = "chp-7:07_CHP-7_sec_iv:l77-87"
SIV_97 = "chp-7:07_CHP-7_sec_iv:l97-119"

ACCEPTED = [
    accepted("chp-7:07_CHP-7_sec_i:l113-126", 2500, "Italian art", "cand-4131",
             "Names the field of Italian art in Haskell's account of its overseas dissemination."),
    accepted(SI_128, 2164, "art patrons", "cand-4129",
             "Directly describes the three named families as art patrons; reuse the existing term candidate."),
    accepted(SI_21, 1768, "collection", "cand-11486",
             "Refers to the collection holding the two named Titian paintings; title, scope, and collection identity remain unresolved."),
    accepted(SI_21, 2675, "Naples", "cand-1722",
             "The city is named directly; reuse the index city candidate already used for this local passage."),
    accepted(SI_243, 898, "drawings", "cand-11487",
             "The drawings supplied by Le Brun are a distinct, source-bounded design group for Guidi's Versailles sculpture; title, count, and survival are unknown."),
    accepted(SI_268, 2170, "Naples", "cand-1722",
             "The city is named directly in the Del Carpio passage; reuse the same local city candidate as its nearby statements."),
    accepted(SI_293, 3617, "Louvre", "cand-3254",
             "The note names the museum as a holding location; use the accepted Louvre Museum institution candidate, while keeping the painting-to-museum pairing unresolved."),
    accepted(SI_293, 4427, "palace", "cand-6796",
             "The note's palace is the Bentivoglio palace whose Lante transfer chain is already recorded in this chapter."),
    accepted(SI_293, 5936, "visit to Paris", "cand-11488",
             "A distinct 1664 visit with named participants, year, and destination; retain both participant identities as unresolved."),
    accepted(SI_293, 6140, "Battle", "cand-7106",
             "This is the particular Rosa painting in the 1697 transfer report, not the generic index subentry."),
    accepted(SI_293, 7682, "collection", "cand-6976",
             "Harris's note refers back to Del Carpio's Rome collection already represented by the type-pending candidate."),
    accepted(SIV_63, 2375, "Italian painting", "cand-11017",
             "Names Italian painting as the field of Lord Exeter's collecting; preserve its distinction from Italian art generally."),
    accepted(SIV_63, 2665, "Italian painting", "cand-11017",
             "Names Italian painting as the field of Lord Exeter's unprecedented commission scale."),
    accepted(SIV_77, 753, "English patronage", "cand-0969",
             "The phrase names the practice Shaftesbury is said to have encouraged; the existing statement's England place endpoint is corrected to this term."),
    accepted(SIV_77, 900, "Italian art", "cand-4131",
             "Names the field of Shaftesbury's contacts; use the broad existing Italian art term."),
    accepted(SIV_77, 1603, "drawings", "cand-7241",
             "These are the already represented Prudence and Justice drawings sent to Shaftesbury by Closterman."),
    accepted(SIV_97, 301, "Prince", "cand-1405",
             "The note's Prince is Wenzel of Liechtenstein, the subject of the linked statement; the mention is not Machiavelli's Prince."),
]

NO_WRITE = [
    no_write(SI_102, 162, "character", "Haskell's 'angelic character' is a generic evaluation, not a person or named entity."),
    no_write(SI_102, 2301, "subject", "Subject-matter of small bronzes is a generic art category, not a distinct work or topic entity."),
    no_write(SI_140, 103, "subject", "The word refers to the unresolved subject of Titian paintings, not an entity called Subject."),
    no_write(SI_140, 1818, "artistic tastes", "This describes Mazarin's disposition; the index match belongs to Joseph Smith and is an unrelated subentry."),
    no_write(SI_160, 130, "contracts", "The passage refers generally to Algardi cancelling his contracts with the French; it identifies no discrete contract or documentary record."),
    no_write(SI_160, 2398, "fortune", "'Reversals of fortune' is an idiom, not Salvator Rosa's work Fortune."),
    no_write(SI_170, 1874, "subject", "This describes the quality and subject-matter of Mazarin's gallery pictures generically."),
    no_write(SI_205, 206, "subject", "The schoolmaster story is used as a painting subject, not as a named work or concept entity."),
    no_write(SI_21, 728, "churches", "Churches occur in a generic list of decoration sites; no church is identified."),
    no_write(SI_232, 1643, "subject", "This means a subject suitable for the artist's visions of royalty, not a named entity."),
    no_write(SI_232, 1849, "character", "This refers to individual traits expressed in the bust, not a separate person or concept."),
    no_write(SI_282, 313, "aristocracy", "A generic social class in the phrase 'irresponsible aristocracy'; the matched index subentry is unrelated."),
    no_write(SI_45, 269, "prince", "The phrase 'home of a great prince' is a generic status description and does not identify a prince."),
    no_write(SIV_23, 2278, "altarpieces", "A broad artwork genre, not an individually identified work or bounded group in this passage."),
    no_write(SIV_23, 2708, "gardens", "The text alludes to gardens as a general motif; it does not identify a place."),
    no_write(SIV_23, 2826, "subject", "This is a generic reference to the subject of a discussion, not an entity."),
    no_write(SIV_48, 1255, "portraits", "Portraits are a broad genre here, not a specific portrait or bounded group."),
    no_write(SIV_48, 2282, "bologna", "The lower-case word means Bologna sausage in a food list, not the city."),
    no_write(SIV_48, 2555, "subject", "This is the generic subject of an allegorical fresco, not a distinct entity."),
    no_write(SIV_63, 1021, "patronage of Italian artists", "The phrase describes Isham and Exeter's general practice; the surface candidates are unrelated Johann Wilhelm/Prince Eugene index subentries."),
    no_write(SIV_77, 463, "prices", "'Fabulous prices' is a generic economic description, not one of the unrelated people-index subentries."),
    no_write(SIV_77, 814, "subject", "'The whole subject' means the general topic of patronage, not an entity."),
    no_write(SIV_77, 1519, "subject", "This is the generic art subject Shaftesbury chose for a proposed sculpture project."),
]

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11486",
        "index_entry_id": "",
        "canonical_name": "Cardinal Aldobrandini’s collection containing Titian’s Bacchanal and Worship of Venus (identity and scope unresolved)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Titian’s Bacchanal and Worship of Venus had been in Cardinal Aldobrandini’s collection. No formal name, scope, location, or collection type is supplied. Keep distinct from other Aldobrandini painting groups pending S3.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-7:07_CHP-7_sec_i:l21-29#L25",
    },
    {
        "candidate_id": "cand-11487",
        "index_entry_id": "",
        "canonical_name": "Drawings provided by Charles Le Brun for Domenico Guidi’s Versailles sculptured group",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Guidi’s group for the gardens at Versailles was to be based on drawings provided by Le Brun. No title, count, exact designs, or survival status is given. Keep this source-reported design group distinct from cand-7241, the Prudence and Justice drawings sent to Shaftesbury.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-7:07_CHP-7_sec_i:l243-257#L246",
    },
    {
        "candidate_id": "cand-11488",
        "index_entry_id": "",
        "canonical_name": "Cardinal Chigi’s 1664 visit to Paris accompanied by Canini (identities unresolved)",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell reports that Canini accompanied Cardinal Chigi on a visit to Paris in 1664. No given names are supplied for either person; retain the report and event without resolving participant identities.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-7:07_CHP-7_sec_i:l293-389#L365",
    },
]

STATEMENT_LINKS = {
    "st-chp7-p171-i15": ["cand-11486"],
    "st-chp7-p179-i23": ["cand-4131"],
    "st-chp7-p180-i23": ["cand-4129"],
    "st-chp7-p180-n4-cite-poussin-catalog": ["cand-3254"],
    "st-chp7-p180-n4-pair-location": ["cand-3254"],
    "st-chp7-p187-n4-canini-accompanied-cardinal-chigi": ["cand-11488"],
    "st-chp7-p189-i07": ["cand-11487"],
    "st-chp7-p190-n5-haskell-acknowledges-harris": ["cand-6976"],
    "st-chp7-p197-england-lacks-italian-painting": ["cand-11017"],
    "st-chp7-p197-exeter-unique-commission-scale": ["cand-11017"],
    "st-chp7-p198-shaftesbury-italy-visit": ["cand-4131"],
}
ENGLISH_PATRONAGE_STATEMENT = "st-chp7-p198-shaftesbury-welcomed-patronage"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(relative: str) -> str:
    return sha256_bytes((ROOT / relative).read_bytes())


def verify_hashes() -> dict[str, str]:
    actual = {relative: sha256_path(relative) for relative in EXPECTED_HASHES}
    mismatches = {
        relative: {"expected": EXPECTED_HASHES[relative], "actual": actual[relative]}
        for relative in EXPECTED_HASHES
        if actual[relative] != EXPECTED_HASHES[relative]
    }
    if mismatches:
        raise RuntimeError(f"Locked inputs changed; re-review before writing: {json.dumps(mismatches)}")
    return actual


def read_csv_rows(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    reader = csv.DictReader(io.StringIO(text))
    return raw, list(reader.fieldnames or []), rows


def newline_for(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def append_csv_rows(raw: bytes, columns: list[str], rows: list[dict[str, str]]) -> bytes:
    eol = newline_for(raw)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator=eol)
    for row in rows:
        writer.writerow(row)
    addition = buffer.getvalue().encode("utf-8")
    separator = b"" if raw.endswith((b"\n", b"\r")) else eol.encode("ascii")
    return raw + separator + addition


def jsonl_records(raw: bytes) -> tuple[list[str], list[dict[str, object]], str, bool]:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    if len(records) != len(lines):
        raise ValueError("Unexpected blank JSONL line; refusing to rewrite the table.")
    return lines, records, eol, has_bom


def mention_id(row: dict[str, object]) -> str:
    key = "|".join(str(row[key]) for key in ("segment_id", "start_char", "end_char", "candidate_id"))
    return "m-s2-chp7-surface-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def build_plan() -> dict[str, object]:
    summary, prompts = surface_audit.audit("chp-7", 6)
    signatures = {
        (str(hit["segment_id"]), int(hit["start_char"]), int(hit["end_char"]), str(hit["surface_form"]))
        for hit in prompts
    }
    expected_accepted = {
        (str(row["segment_id"]), int(row["start_char"]), int(row["end_char"]), str(row["surface_form"]))
        for row in ACCEPTED
    }
    expected_no_write = {
        (str(row["segment_id"]), int(row["start_char"]), int(row["end_char"]), str(row["surface_form"]))
        for row in NO_WRITE
    }
    if len(ACCEPTED) != 17 or len(NO_WRITE) != 23:
        raise ValueError("The adjudication partition must contain 17 accepted and 23 no-write prompts.")
    if expected_accepted & expected_no_write:
        raise ValueError("Accepted and no-write prompt signatures overlap.")
    if signatures != expected_accepted | expected_no_write:
        missing = sorted((expected_accepted | expected_no_write) - signatures)
        extra = sorted(signatures - (expected_accepted | expected_no_write))
        raise ValueError(f"Prompt set differs from the adjudication: missing={missing}; extra={extra}")
    if int(summary["reviewed_segments_scanned"]) != 47 or int(summary["uncovered_candidate_surface_spans"]) != 40:
        raise ValueError(f"Unexpected scanner scope or count: {summary}")

    segment_text: dict[str, str] = {}
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines():
        if not line:
            continue
        segment = json.loads(line)
        if segment.get("chapter") != "chp-7":
            continue
        source_path = ROOT / segment["source_file"]
        source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
        segment_text[segment["segment_id"]] = "\n".join(
            source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])]
        )
    for row in ACCEPTED:
        text = segment_text.get(str(row["segment_id"]))
        if text is None or text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
            raise ValueError(f"Accepted mention does not match its locked source span: {row}")

    candidate_raw, candidate_columns, existing_candidates = read_csv_rows(CANDIDATES)
    mention_raw, mention_columns, existing_mentions = read_csv_rows(MENTIONS)
    candidate_ids = {row["candidate_id"] for row in existing_candidates}
    numeric_ids = [int(match.group(1)) for value in candidate_ids if (match := re.fullmatch(r"cand-(\d+)", value))]
    if max(numeric_ids, default=0) != 11485:
        raise ValueError(f"Candidate sequence changed; expected current maximum cand-11485, got {max(numeric_ids, default=0)}")
    new_ids = [str(row["candidate_id"]) for row in NEW_CANDIDATES]
    if len(set(new_ids)) != len(new_ids) or set(new_ids) & candidate_ids:
        raise ValueError("New candidate IDs are duplicated or already present.")
    if new_ids != [f"cand-{number}" for number in (11486, 11487, 11488)]:
        raise ValueError(f"Unexpected candidate allocation: {new_ids}")

    mention_ids = {row["mention_id"] for row in existing_mentions}
    occupied: dict[str, list[tuple[int, int]]] = {}
    for row in existing_mentions:
        occupied.setdefault(row["segment_id"], []).append((int(row["start_char"]), int(row["end_char"])))
    planned_mentions: list[dict[str, str]] = []
    for item in ACCEPTED:
        record = {key: str(item[key]) for key in ("segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note")}
        record["mention_id"] = mention_id({**record, "start_char": int(record["start_char"]), "end_char": int(record["end_char"])})
        if record["mention_id"] in mention_ids:
            raise ValueError(f"Mention ID already exists: {record['mention_id']}")
        if record["candidate_id"] not in candidate_ids | set(new_ids):
            raise ValueError(f"Mention refers to a missing candidate: {record}")
        start, end = int(record["start_char"]), int(record["end_char"])
        if any(start < old_end and end > old_start for old_start, old_end in occupied.get(record["segment_id"], [])):
            raise ValueError(f"Mention overlaps an existing span: {record}")
        if any(start < int(other["end_char"]) and end > int(other["start_char"])
               for other in planned_mentions if other["segment_id"] == record["segment_id"]):
            raise ValueError(f"Planned mentions overlap: {record}")
        mention_ids.add(record["mention_id"])
        planned_mentions.append(record)

    statements_raw = STATEMENTS.read_bytes()
    statement_lines, statement_rows, statement_eol, statement_bom = jsonl_records(statements_raw)
    statement_map = {str(row["statement_id"]): row for row in statement_rows}
    if len(statement_map) != len(statement_rows):
        raise ValueError("Statement IDs are not unique.")
    required_ids = set(STATEMENT_LINKS) | {ENGLISH_PATRONAGE_STATEMENT}
    if not required_ids <= statement_map.keys():
        raise ValueError(f"Missing statement update targets: {sorted(required_ids - statement_map.keys())}")
    before = statement_map[ENGLISH_PATRONAGE_STATEMENT]
    if (before.get("subject_candidate_id") != "cand-2426"
            or before.get("object_candidate_id") != "cand-7200"
            or before.get("predicate") != "welcomed_and_stimulated_english_patronage"):
        raise ValueError("English-patronage statement no longer has the reviewed pre-state.")
    updates: dict[str, dict[str, object]] = {}
    for statement_id, ids in STATEMENT_LINKS.items():
        record = statement_map[statement_id]
        qualifiers = record.setdefault("qualifiers", {})
        current = qualifiers.setdefault("mentioned_candidate_ids", [])
        for candidate_id in ids:
            if candidate_id not in current:
                current.append(candidate_id)
        updates[statement_id] = record
    english = statement_map[ENGLISH_PATRONAGE_STATEMENT]
    english["object_candidate_id"] = "cand-0969"
    english_mentions = english.setdefault("qualifiers", {}).setdefault("mentioned_candidate_ids", [])
    english["qualifiers"]["mentioned_candidate_ids"] = [
        candidate_id for candidate_id in english_mentions if candidate_id != "cand-7200"
    ]
    if "cand-0969" not in english["qualifiers"]["mentioned_candidate_ids"]:
        english["qualifiers"]["mentioned_candidate_ids"].append("cand-0969")
    updates[ENGLISH_PATRONAGE_STATEMENT] = english

    all_candidate_ids = candidate_ids | set(new_ids)
    for statement_id, record in updates.items():
        for field in ("subject_candidate_id", "object_candidate_id"):
            value = record.get(field)
            if value is not None and value not in all_candidate_ids:
                raise ValueError(f"Updated {statement_id} has missing {field} candidate {value}")
        for value in record.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if value not in all_candidate_ids:
                raise ValueError(f"Updated {statement_id} has missing mentioned candidate {value}")

    candidate_output = append_csv_rows(candidate_raw, candidate_columns, NEW_CANDIDATES)
    mention_output = append_csv_rows(mention_raw, mention_columns, planned_mentions)
    statement_output_lines = list(statement_lines)
    for index, line in enumerate(statement_lines):
        record = json.loads(line)
        statement_id = str(record["statement_id"])
        if statement_id in updates:
            statement_output_lines[index] = json.dumps(updates[statement_id], ensure_ascii=False)
    statement_text = statement_eol.join(statement_output_lines) + statement_eol
    if statement_bom:
        statement_text = "\ufeff" + statement_text
    statement_output = statement_text.encode("utf-8")

    plan_content = {
        "accepted": ACCEPTED,
        "no_write": NO_WRITE,
        "new_candidates": NEW_CANDIDATES,
        "statement_links": STATEMENT_LINKS,
        "english_patronage_statement": ENGLISH_PATRONAGE_STATEMENT,
    }
    plan_sha = hashlib.sha256(
        json.dumps(plan_content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "scanner_summary": summary,
        "accepted": ACCEPTED,
        "no_write": NO_WRITE,
        "new_candidates": NEW_CANDIDATES,
        "planned_mentions": planned_mentions,
        "statement_updates": updates,
        "plan_sha256": plan_sha,
        "outputs": {
            CANDIDATES: candidate_output,
            MENTIONS: mention_output,
            STATEMENTS: statement_output,
        },
        "before_hashes": {
            "04-knowledge/tables/entity-candidates.csv": sha256_bytes(candidate_raw),
            "04-knowledge/tables/mentions.csv": sha256_bytes(mention_raw),
            "04-knowledge/tables/book-statements.jsonl": sha256_bytes(statements_raw),
        },
    }


def atomic_write(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def apply_plan(plan: dict[str, object]) -> Path:
    recovery = Path(tempfile.gettempdir()) / f"pnp-s2-chp7-surface-prompts-{datetime.now():%Y%m%d-%H%M%S}"
    recovery.mkdir(parents=True, exist_ok=False)
    paths = list(plan["outputs"].keys())
    for path in paths:
        shutil.copy2(path, recovery / path.name)
    try:
        for path, data in plan["outputs"].items():
            atomic_write(path, data)
    except Exception:
        for path in paths:
            shutil.copy2(recovery / path.name, path)
        raise
    return recovery


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the locked, preflighted changes")
    args = parser.parse_args()
    verify_hashes()
    plan = build_plan()
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "scanner": plan["scanner_summary"],
        "accepted_mentions": len(plan["planned_mentions"]),
        "no_write_prompts": len(plan["no_write"]),
        "new_candidates": len(plan["new_candidates"]),
        "updated_statements": len(plan["statement_updates"]),
        "plan_sha256": plan["plan_sha256"],
        "before_hashes": plan["before_hashes"],
    }, ensure_ascii=False))
    if not args.apply:
        return 0
    recovery = apply_plan(plan)
    try:
        after_hashes = {path.name: sha256_bytes(data) for path, data in plan["outputs"].items()}
        summary, prompts = surface_audit.audit("chp-7", 6)
        no_write_signatures = {
            (str(row["segment_id"]), int(row["start_char"]), int(row["end_char"]), str(row["surface_form"]))
            for row in plan["no_write"]
        }
        after_signatures = {
            (str(hit["segment_id"]), int(hit["start_char"]), int(hit["end_char"]), str(hit["surface_form"]))
            for hit in prompts
        }
        if after_signatures != no_write_signatures or int(summary["uncovered_candidate_surface_spans"]) != len(plan["no_write"]):
            raise RuntimeError(f"Post-write scanner set differs from no-write decisions: {summary}")
    except Exception:
        for path in plan["outputs"]:
            shutil.copy2(recovery / path.name, path)
        raise
    print(json.dumps({
        "post_write_scanner": summary,
        "remaining_prompts_match_no_write": True,
        "after_hashes": after_hashes,
        "recovery_directory": str(recovery),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
