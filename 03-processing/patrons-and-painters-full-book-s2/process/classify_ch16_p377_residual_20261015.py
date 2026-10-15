#!/usr/bin/env python3
"""Classify the remaining p.377 S2 statements with a guarded preview/apply."""

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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
SEGMENT_ID = "chp-16:16_CHP-16_intro:l48-64"
SOURCE_FILE = "02-sources/02-Markdown/16_CHP-16_intro.md"
EXPECTED_HASHES = {
    "entity-candidates.csv": "748e71911a51e1cd8ed28e2099c6c67007b2b424566706f46780a0ac4d81c407",
    "mentions.csv": "10d23307c99a5dae6ac5762f82226304a898edff922ad6e56617fee7ea61147a",
    "book-statements.jsonl": "ed7de8336d2e11e7cfdd6ea62add33b7ce84166d2017a09ecb2086a41cb5d930",
}
EXPECTED_SEGMENT_HASH = "ca1b6e336639596df69fb2c839e3124326d283b5eaaefa33bfcf014261c7ee4c"
PERSON_ID = "cand-12253"
PERSON_MENTION_ID = "m-chp16-p377-celotti-0069"
NEW_STATEMENT_IDS = {
    "st-chp16-p377-celotti-salesmanship-inference",
    "st-chp16-p377-note3-picture-for-king-of-france",
}
PENDING_IDS = {
    "st-chp16-p377-celotti-at-home-in-all-regimes",
    "st-chp16-p377-haskell-infers-celotti-salesmanship-and-taste",
    "st-chp16-p377-note3-vannetti-correspondence",
    "st-chp16-p377-note3-durazzo-correspondence",
    "st-chp16-p377-note3-published-swajer-tiepolo-letter",
    "st-chp16-p377-note3-published-gian-domenico-swajer-letter",
    "st-chp16-p377-note3-letter-and-consaputo-quadro",
    "st-chp16-p377-note3-ghelthof-provenance-claim",
    "st-chp16-p377-note3-ghelthof-reliability-caution",
    "st-chp16-p377-note3-state-archive-locator",
}
BACKUP_SUFFIX = ".bak-s2-ch16-p377-residual-20261015"
NOTE3_LINK = {
    "footnote_marker": "3",
    "footnote_segment": "chp-16:16_CHP-16_intro:l69-89",
    "footnote_line_range": "L84-L84",
    "footnote_text_pending": False,
    "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L46",
    "footnote_note_statement_ids": [
        "st-chp16-p376-note3-swajer-correspondence-partial"
    ],
}
NOTE4_LINK = {
    "footnote_marker": "4",
    "footnote_segment": "chp-16:16_CHP-16_intro:l69-89",
    "footnote_line_range": "L88-L88",
    "footnote_text_pending": False,
    "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L56-L58",
    "footnote_note_statement_ids": ["st-chp16-p377-note4-celotti-1807-catalogue"],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bytes]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames:
        raise ValueError(f"Missing CSV header: {path}")
    return list(reader.fieldnames), list(reader), raw


def csv_append_bytes(rows: list[dict[str, str]], fields: list[str]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise", lineterminator="\r\n")
    for row in rows:
        writer.writerow(row)
    return stream.getvalue().encode("utf-8")


def jsonl_update(
    raw: bytes,
    updates: dict[str, dict],
    insert_after: dict[str, list[dict]],
) -> bytes:
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    body = raw[len(bom) :]
    output: list[bytes] = []
    seen: set[str] = set()
    for raw_line in body.splitlines(keepends=True):
        ending = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n" if raw_line.endswith(b"\n") else b""
        payload = json.loads(raw_line[: -len(ending)] if ending else raw_line)
        statement_id = payload.get("statement_id")
        if statement_id in updates:
            payload.update(updates[statement_id])
            seen.add(statement_id)
            output.append(json.dumps(payload, ensure_ascii=False).encode("utf-8") + ending)
        else:
            output.append(raw_line)
        for new_row in insert_after.get(statement_id, []):
            output.append(json.dumps(new_row, ensure_ascii=False).encode("utf-8") + (ending or b"\n"))
    if seen != set(updates):
        raise ValueError(f"Expected to update {sorted(updates)}, found {sorted(seen)}")
    return bom + b"".join(output)


def source_segment_text() -> str:
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    return "\n".join(lines[47:64])


def note4_fields() -> dict:
    values = dict(NOTE4_LINK)
    values["footnote_link_note"] = (
        "P.377 note 4 cites the 1807 Celotti catalogue connected with the collection descriptions."
    )
    return values


def note3_fields() -> dict:
    values = dict(NOTE3_LINK)
    values["footnote_link_note"] = (
        "Printed note 3 starts at p.376 L84 and continues on p.377 L60-L64."
    )
    return values


def build_outputs() -> tuple[dict[Path, bytes], dict]:
    paths = {name: TABLES / name for name in EXPECTED_HASHES}
    for name, path in paths.items():
        current = sha256(path.read_bytes())
        if current != EXPECTED_HASHES[name]:
            raise ValueError(f"Stale input {name}: {current}")

    segment_text = source_segment_text()
    segment_rows = [
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("The p.377 source segment fingerprint changed.")
    expected_person_span = "Urbani de Ghelthof"
    if segment_text[2606:2624] != expected_person_span:
        raise ValueError("The p.377 person mention span no longer matches the source.")

    candidate_fields, candidates, candidate_raw = read_csv(paths["entity-candidates.csv"])
    mention_fields, mentions, mention_raw = read_csv(paths["mentions.csv"])
    if candidate_fields != [
        "candidate_id", "index_entry_id", "canonical_name", "index_page_range",
        "suggested_type", "status", "index_source_file", "sub_entry", "detail",
        "exclude_reason", "candidate_origin", "candidate_source_ref",
    ]:
        raise ValueError("Unexpected entity-candidate schema.")
    if mention_fields != [
        "mention_id", "segment_id", "candidate_id", "surface_form",
        "start_char", "end_char", "note",
    ]:
        raise ValueError("Unexpected mention schema.")
    if len(candidates) != 12230 or len(mentions) != 25955:
        raise ValueError(f"Unexpected input table sizes: {len(candidates)} candidates, {len(mentions)} mentions.")
    if any(row["candidate_id"] == PERSON_ID for row in candidates):
        raise ValueError(f"Candidate ID already exists: {PERSON_ID}")
    if any(row["mention_id"] == PERSON_MENTION_ID for row in mentions):
        raise ValueError(f"Mention ID already exists: {PERSON_MENTION_ID}")

    statements_path = paths["book-statements.jsonl"]
    statement_raw = statements_path.read_bytes()
    statement_rows = []
    for line in statement_raw.decode("utf-8-sig").splitlines():
        if line.strip():
            statement_rows.append(json.loads(line))
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    if len(statement_by_id) != len(statement_rows):
        raise ValueError("Duplicate statement IDs in input table.")
    if not NEW_STATEMENT_IDS.isdisjoint(statement_by_id):
        raise ValueError("A new statement ID already exists.")
    segment_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    pending_now = {
        row["statement_id"]
        for row in segment_rows
        if row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if pending_now != PENDING_IDS:
        raise ValueError(f"Pending p.377 rows changed: {sorted(pending_now)}")

    candidate_rows = [
        {
            "candidate_id": PERSON_ID,
            "index_entry_id": "",
            "canonical_name": "Urbani de Ghelthof (person named in Haskell's p.377 note 3)",
            "index_page_range": "",
            "suggested_type": "person",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": (
                "Haskell's note says the Swajer letter was claimed to belong to this person's own collection "
                "and questions his use of documents. The same name appears nearby as author of the 1879 "
                "publication, but this person candidate remains distinct from that publication; no further "
                "identity is independently established."
            ),
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L64",
        }
    ]
    candidate_text = candidate_raw
    if candidate_text and not candidate_text.endswith((b"\n", b"\r")):
        candidate_text += b"\r\n"
    candidate_text += csv_append_bytes(candidate_rows, candidate_fields)

    mention_rows = [
        {
            "mention_id": PERSON_MENTION_ID,
            "segment_id": SEGMENT_ID,
            "candidate_id": PERSON_ID,
            "surface_form": expected_person_span,
            "start_char": "2606",
            "end_char": "2624",
            "note": (
                "Person named as the claimed owner of the Swajer letter; kept distinct from the 1879 "
                "publication candidate with the same name."
            ),
        }
    ]
    mention_text = mention_raw
    if mention_text and not mention_text.endswith((b"\n", b"\r")):
        mention_text += b"\r\n"
    mention_text += csv_append_bytes(mention_rows, mention_fields)

    updates: dict[str, dict] = {}
    insert_after: dict[str, list[dict]] = {}

    at_home = statement_by_id["st-chp16-p377-celotti-at-home-in-all-regimes"]
    q = dict(at_home["qualifiers"])
    q["relation_candidate"] = False
    q["relation_candidate_note"] = (
        "Conditional characterization of commercial adaptability; no specific purchase, client, "
        "or political role is asserted."
    )
    updates[at_home["statement_id"]] = {"qualifiers": q}

    taste = statement_by_id["st-chp16-p377-haskell-infers-celotti-salesmanship-and-taste"]
    q = dict(taste["qualifiers"])
    q.update(
        {
            "claim": (
                "Haskell infers that Celotti had a genuine individual taste similar to that of some "
                "previously recorded humbler dealers."
            ),
            "text_layer": "explicit authorial inference",
            "qualification": (
                "The similarity is Haskell's inference and concerns an unspecified subset of the "
                "humbler dealers previously recorded; the group membership is not enumerated."
            ),
            "mentioned_candidate_ids": ["cand-0622", "cand-0126"],
            "relation_candidate": True,
            "relation_candidate_note": (
                "Explicit comparison of Celotti's taste with a source-defined subset of earlier dealers."
            ),
        }
    )
    q.update(note4_fields())
    updates[taste["statement_id"]] = {
        "object_candidate_id": "cand-0126",
        "predicate": "haskell_infers_celotti_taste_similar_to_some_humbler_dealers",
        "qualifiers": q,
        "original_quote": (
            "a genuine and individual taste which is similar to that of some of the humbler dealers "
            "so far recorded"
        ),
    }

    salesmanship = {
        "statement_id": "st-chp16-p377-celotti-salesmanship-inference",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0622",
        "object_candidate_id": None,
        "predicate": "haskell_infers_celotti_had_a_gift_for_salesmanship",
        "qualifiers": {
            "source_line_start": 56,
            "source_line_end": 56,
            "printed_page": 377,
            "pdf_physical_page": 5,
            "claim": "Haskell infers from Celotti's rhapsodic accounts a considerable gift for salesmanship.",
            "speaker": "Haskell",
            "text_layer": "explicit authorial inference",
            "qualification": (
                "This is an attributed inference about a personal skill, not an assertion of a specific "
                "sale, buyer, or transaction."
            ),
            "mentioned_candidate_ids": ["cand-0622"],
            "relation_candidate": False,
            "relation_candidate_note": "Personal attribute inference with no distinct relation endpoint.",
            **note4_fields(),
        },
        "original_quote": "a considerable gift for salesmanship",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    insert_after[taste["statement_id"]] = [salesmanship]

    simple_true_ids = {
        "st-chp16-p377-note3-vannetti-correspondence",
        "st-chp16-p377-note3-durazzo-correspondence",
        "st-chp16-p377-note3-published-swajer-tiepolo-letter",
        "st-chp16-p377-note3-published-gian-domenico-swajer-letter",
        "st-chp16-p377-note3-state-archive-locator",
    }
    for statement_id in simple_true_ids:
        row = statement_by_id[statement_id]
        q = dict(row["qualifiers"])
        q["relation_candidate"] = True
        if statement_id.endswith("state-archive-locator"):
            q["relation_candidate_note"] = (
                "The note locates Swajer's papers and manuscripts in a specific archive record."
            )
        updates[statement_id] = {"qualifiers": q}

    letter_picture = statement_by_id["st-chp16-p377-note3-letter-and-consaputo-quadro"]
    q = dict(letter_picture["qualifiers"])
    q.update(
        {
            "claim": "Haskell's note says the Swajer letter refers to Tiepolo's 'consaputo quadro'.",
            "text_layer": "reported letter content",
            "qualification": (
                "The letter is known here only through Haskell's note; the picture is unidentified and "
                "the cited letter was not independently consulted."
            ),
            "mentioned_candidate_ids": ["cand-10668", "cand-2569", "cand-10671"],
            "relation_candidate": True,
            "relation_candidate_note": "The note explicitly says the letter refers to the picture.",
        }
    )
    q.pop("ocr_corrections", None)
    updates[letter_picture["statement_id"]] = {
        "qualifiers": q,
        "original_quote": "The former, which refers to Tiepolo’s ‘consaputo quadro’",
    }
    picture_for_king = {
        "statement_id": "st-chp16-p377-note3-picture-for-king-of-france",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-10671",
        "object_candidate_id": "cand-10670",
        "predicate": "described_in_the_letter_as_for_the_king_of_france",
        "qualifiers": {
            "source_line_start": 63,
            "source_line_end": 64,
            "printed_page": 377,
            "pdf_physical_page": 5,
            "claim": "Haskell's note describes the picture as Tiepolo's 'consaputo quadro' for the King of France.",
            "speaker": "Haskell's note",
            "text_layer": "reported letter content",
            "qualification": (
                "The monarch and picture are unidentified; 'for' is retained as the note's wording and "
                "is not expanded into a documented commission or ownership claim."
            ),
            "mentioned_candidate_ids": ["cand-10668", "cand-2569", "cand-10671", "cand-10670"],
            "cited_source_independently_consulted": False,
            "relation_candidate": True,
            "relation_candidate_note": (
                "The source explicitly describes the picture as for the King of France."
            ),
            **note3_fields(),
        },
        "original_quote": "Tiepolo’s ‘consaputo quadro’ for the King of\nFrance",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    insert_after[letter_picture["statement_id"]] = [picture_for_king]

    provenance = statement_by_id["st-chp16-p377-note3-ghelthof-provenance-claim"]
    q = dict(provenance["qualifiers"])
    q.update(
        {
            "source_line_start": 64,
            "source_line_end": 64,
            "claim": (
                "Haskell reports that the Swajer letter was claimed to belong to Urbani de Ghelthof's "
                "own collection."
            ),
            "qualification": (
                "This is an attributed claim of collection provenance, not independently verified ownership; "
                "the person candidate remains distinct from the cited publication."
            ),
            "mentioned_candidate_ids": ["cand-10668", PERSON_ID],
            "relation_candidate": True,
            "relation_candidate_note": "The note explicitly attributes the claimed collection ownership.",
        }
    )
    updates[provenance["statement_id"]] = {
        "object_candidate_id": PERSON_ID,
        "qualifiers": q,
        "original_quote": "is claimed to belong to Urbani de Ghelthof’s own collection",
    }

    reliability = statement_by_id["st-chp16-p377-note3-ghelthof-reliability-caution"]
    q = dict(reliability["qualifiers"])
    q.update(
        {
            "claim": (
                "Haskell cites an Ateneo Veneto item from May 1937 as reason to treat Urbani de "
                "Ghelthof's documentary use with caution."
            ),
            "qualification": (
                "This is Haskell's source criticism; the 1937 item was not independently consulted."
            ),
            "mentioned_candidate_ids": [PERSON_ID, "cand-10672"],
            "relation_candidate": True,
            "relation_candidate_note": (
                "The note explicitly presents the 1937 item as a basis for its caution about the person's "
                "documentary reliability."
            ),
        }
    )
    updates[reliability["statement_id"]] = {
        "subject_candidate_id": PERSON_ID,
        "qualifiers": q,
        "original_quote": (
            "and should perhaps.be treated with some,caution, as it appears (Ateneo Veneto, Maggio 1937) "
            "that he was far from reliable in his use of documents"
        ),
    }

    if set(updates) != PENDING_IDS:
        raise ValueError(f"Unexpected set of p.377 updates: {sorted(updates)}")

    statement_text = jsonl_update(
        statement_raw,
        updates,
        insert_after,
    )
    outputs = {
        paths["entity-candidates.csv"]: candidate_text,
        paths["mentions.csv"]: mention_text,
        statements_path: statement_text,
    }
    expected_counts = {
        "candidate_rows": 12231,
        "mention_rows": 25956,
        "statement_rows": 15098,
        "remaining_unclassified": 97,
    }
    preview = {
        "updates": sorted(updates),
        "new_statements": sorted(NEW_STATEMENT_IDS),
        "new_candidate": PERSON_ID,
        "new_mention": PERSON_MENTION_ID,
        "expected_counts": expected_counts,
        "output_hashes": {path.name: sha256(data) for path, data in outputs.items()},
        "backup_paths": [
            str(path.with_name(path.name + BACKUP_SUFFIX))
            for path in outputs
        ],
    }
    return outputs, preview


def write_atomically(outputs: dict[Path, bytes]) -> None:
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise FileExistsError("A dated backup already exists; refusing to overwrite it.")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    staged: dict[Path, Path] = {}
    try:
        for path, data in outputs.items():
            fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
            temp_path = Path(temp_name)
            staged[path] = temp_path
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        for path, temp_path in staged.items():
            os.replace(temp_path, path)
    except Exception:
        for path, backup in backups.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    finally:
        for temp_path in staged.values():
            if temp_path.exists():
                temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes after all guards pass")
    args = parser.parse_args()
    outputs, preview = build_outputs()
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if args.apply:
        write_atomically(outputs)
        print("APPLIED")
    else:
        print("PREVIEW ONLY; no tables changed.")


if __name__ == "__main__":
    main()
