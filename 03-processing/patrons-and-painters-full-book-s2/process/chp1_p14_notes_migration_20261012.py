#!/usr/bin/env python3
"""Atomize printed p.14 notes after protected S0/table checks.

Default mode is a read-only preview. Pass --apply to write the three S2 tables.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
NOTE_SEG = "chp-1:01_CHP-1_sec_ii:l168-239"
BODY_SEG = "chp-1:01_CHP-1_sec_ii:l79-84"
SOURCE_FULL = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md"
SOURCE_SEGMENT = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
OLD_ID = "st-chp1-secii-notes-correspondence-examples"
BACKUP_SUFFIX = ".bak-s2-chp1-secii-p14-notes-20261012"
EXPECTED = {
    "book-statements.jsonl": "89da2a23fdec461686f04bb27146aa1997b5b0c4e0e0ec6492802511c93f401b",
    "entity-candidates.csv": "fd67cc44fa25b9a12f652e384afe37d263c830dc005b21d83a2a3ff0fd211929",
    "mentions.csv": "7616252f7494ffc3cc4a0036c833cd06b804ac9c0a88fd8fc75cabd2718b1717",
    "s2-coverage.csv": "3a851d5de826f9b9d45436bb99f68726b8db1762c02020d4d3c57f745ce5642e",
}
SOURCE_SHA = "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb"
SEGMENT_ASSET_SHA = "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268"
SEGMENT_SHA = "b5560e20ceb3b9b531266ac26966dd0a7f76c6ce8bbc82f6664a9a95d68af258"
PRINT_PAGE = 14
PDF_PAGE = 13
MARKER_LINES = {1: 531, 2: 534, 3: 537, 4: 540, 5: 547, 6: 552}
BODY_IDS = {
    1: ["st-chp1-secii-l79-84-08"],
    2: ["st-chp1-secii-l79-84-02"],
    3: ["st-chp1-secii-l79-84-03"],
    4: ["st-chp1-secii-l79-84-04"],
    5: ["st-chp1-secii-l79-84-10", "st-chp1-secii-l79-84-11"],
    6: ["st-chp1-secii-l79-84-06"],
}
CORRECTIONS_6 = [
    {"source_line": 569, "ocr": "9", "print": "6", "basis": "CHP-1.pdf physical page 13"},
    {"source_line": 569, "ocr": "Ruffe", "print": "Ruffo", "basis": "CHP-1.pdf physical page 13"},
    {"source_line": 569, "ocr": "Rufifo", "print": "Ruffo", "basis": "CHP-1.pdf physical page 13"},
    {"source_line": 570, "ocr": "P- 97-", "print": "p. 97", "basis": "CHP-1.pdf physical page 13"},
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_with_offsets(text: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    offsets: list[int] = []
    previous_space = False
    for index, char in enumerate(text):
        if char.isspace():
            if not previous_space:
                chars.append(" ")
                offsets.append(index)
            previous_space = True
        else:
            chars.append(char)
            offsets.append(index)
            previous_space = False
    return "".join(chars), offsets


def excerpt(lines: list[str], start: int, end: int, phrase: str) -> str:
    raw = "\n".join(lines[start - 1 : end])
    normalized, positions = normalize_with_offsets(raw)
    target = " ".join(phrase.split())
    offset = normalized.find(target)
    if offset < 0:
        raise ValueError(f"quote missing from S0 L{start}-{end}: {phrase}")
    return raw[positions[offset] : positions[offset + len(target) - 1] + 1]


def normalized_span(text: str, phrase: str, occurrence: int = 0) -> tuple[int, int, str]:
    normalized, positions = normalize_with_offsets(text)
    target = " ".join(phrase.split())
    cursor = 0
    offset = -1
    for _ in range(occurrence + 1):
        offset = normalized.find(target, cursor)
        if offset < 0:
            raise ValueError(f"mention phrase missing from flattened source segment: {phrase}")
        cursor = offset + len(target)
    start = positions[offset]
    end = positions[offset + len(target) - 1] + 1
    surface = text[start:end]
    if "\n" in surface or "\r" in surface:
        raise ValueError(f"mention surface crosses a source line: {phrase}")
    return start, end, surface


def append_unique(target: list, values: list) -> list:
    for value in values:
        if value not in target:
            target.append(value)
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all protected checks pass; default is preview")
    args = parser.parse_args()

    for name, expected in EXPECTED.items():
        actual = digest(TABLES / name)
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE_FULL) != SOURCE_SHA:
        raise SystemExit("protected full S0 source file changed")
    if digest(SOURCE_SEGMENT) != SEGMENT_ASSET_SHA:
        raise SystemExit("protected S0 section file changed")

    paths = {name: TABLES / name for name in EXPECTED}
    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    full_lines = SOURCE_FULL.read_text(encoding="utf-8-sig").splitlines()
    section_lines = SOURCE_SEGMENT.read_text(encoding="utf-8-sig").splitlines()
    flat_note = " ".join(" ".join(section_lines[167:239]).split())
    segments = read_jsonl(TABLES / "segments.jsonl")
    segment = next((row for row in segments if row.get("segment_id") == NOTE_SEG), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SEGMENT_ASSET_SHA:
        raise SystemExit("protected note segment fingerprint changed")
    if len(full_lines) < 570 or len(section_lines) < 239:
        raise SystemExit("protected source range is incomplete")

    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(statement_by_id) != len(statements) or len(candidate_by_id) != len(candidates):
        raise SystemExit("duplicate statement or candidate IDs in protected tables")
    if OLD_ID not in statement_by_id or statement_by_id[OLD_ID]["segment_id"] != NOTE_SEG:
        raise SystemExit("expected p.14 broad note row is missing or moved")

    def mk_row(
        suffix: str,
        predicate: str,
        claim: str,
        start: int,
        end: int,
        phrase: str,
        marker: int,
        mentioned: list[str],
        *,
        subject: str | None = None,
        obj: str | None = None,
        speaker: str | None = None,
        text_layer: str,
        qualification: str,
        relation_note: str | None = None,
        date: str | None = None,
        corrections: list[dict] | None = None,
        extra: dict | None = None,
    ) -> dict:
        body_ids = BODY_IDS[marker]
        q = {
            "source_line_start": start,
            "source_line_end": end,
            "printed_page": PRINT_PAGE,
            "pdf_physical_page": PDF_PAGE,
            "claim": claim,
            "speaker": speaker or f"Haskell footnote {marker}",
            "text_layer": text_layer,
            "qualification": qualification,
            "relation_candidate": True,
            "mentioned_candidate_ids": mentioned,
            "footnote_marker": marker,
            "footnote_number": marker,
            "footnote_segment": NOTE_SEG,
            "footnote_refs": [{"marker": marker, "segment_id": NOTE_SEG, "source_line": MARKER_LINES[marker]}],
            "related_segment": BODY_SEG,
            "related_body_statement_ids": body_ids,
            "linked_body_statement_ids": body_ids,
            "related_source_lines": [MARKER_LINES[marker]],
            "footnote_link_status": "linked",
            "footnote_text_pending": False,
        }
        if date:
            q["date"] = date
        if relation_note:
            q["relation_candidate_note"] = relation_note
        if corrections:
            q["ocr_corrections"] = corrections
        if extra:
            q.update(extra)
        return {
            "statement_id": f"st-chp1-secii-p14-{suffix}",
            "segment_id": NOTE_SEG,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": q,
            "original_quote": excerpt(full_lines, start, end, phrase),
            "origin": "book",
            "source_file": "02-sources/02-Markdown/01_CHP-1.md",
        }

    def mk_letter_rows(
        marker: int,
        key: str,
        label: str,
        letter_id: str,
        author_id: str,
        author_name: str,
        recipient_id: str,
        recipient_name: str,
        date: str,
        start: int,
        end: int,
        author_phrase: str,
        recipient_phrase: str,
        corrections: list[dict] | None = None,
    ) -> list[dict]:
        return [
            mk_row(
                f"n{marker}-{key}-letter-authored-by", "letter_authored_by",
                f"Haskell identifies {author_name} as the author of the {date} letter {label}.",
                start, end, author_phrase, marker, [letter_id, author_id], subject=letter_id, obj=author_id,
                text_layer="letter attribution mediated by Haskell",
                qualification="The original letter was not independently consulted; author and date are recorded as Haskell prints them.",
                relation_note="The note explicitly names the writer and the date for this specific letter; no broader correspondence relation is inferred.",
                date=date, corrections=corrections,
            ),
            mk_row(
                f"n{marker}-{key}-letter-addressed-to", "letter_addressed_to",
                f"Haskell identifies {recipient_name} as the addressee of the {date} letter {label}.",
                start, end, recipient_phrase, marker, [letter_id, recipient_id], subject=letter_id, obj=recipient_id,
                text_layer="letter metadata mediated by Haskell",
                qualification="The original letter was not independently consulted; the note supplies this addressee for the specific letter.",
                relation_note="This is a source-defined addressee role for one dated letter, not an ongoing correspondence relation.",
                date=date, corrections=corrections,
            ),
        ]

    new_statements: list[dict] = []
    citation_specs = [
        {
            "marker": 1, "key": "mancini-i-p140", "start": 562, "end": 562,
            "quote": "Mancini, I, p. 140", "claim": "Haskell cites Giulio Mancini, volume I, page 140, for the munificent patron who leaves the reward to the artist's discretion.",
            "author": "cand-1507", "publication": "cand-6089", "locator": "Mancini, I, p. 140",
            "mention": "m-chp1-secii-p14-n1-mancini-i-p140", "occurrence": 0, "cited_document": None, "body": BODY_IDS[1],
        },
        {
            "marker": 2, "key": "luzio-p48-reni", "start": 563, "end": 563,
            "quote": "Luzio, p. 48", "claim": "Haskell cites Luzio, page 48, for the immediately preceding report about the Duke of Mantua and Guido Reni.",
            "author": "cand-3515", "publication": "cand-7052", "locator": "Luzio, p. 48",
            "mention": "m-chp1-secii-p14-n2-luzio-p48", "occurrence": 1, "cited_document": None, "body": BODY_IDS[2],
        },
        {
            "marker": 3, "key": "faldi-1957-pp278-295", "start": 564, "end": 564,
            "quote": "Faldi, 1957, pp. 278-95", "claim": "Haskell cites Faldi's 1957 study, pages 278–295, for the Paolo Guidotti example.",
            "author": "cand-3516", "publication": "cand-4331", "locator": "Faldi, 1957, pp. 278–95",
            "mention": "m-chp1-secii-p14-n3-faldi-1957-pp278-295", "occurrence": 0, "cited_document": None, "body": BODY_IDS[3],
        },
        {
            "marker": 4, "key": "boyer-p238-salviati-letter", "start": 565, "end": 566,
            "quote": "Ferdinand Boyer, 1931, p. 238", "claim": "Haskell says that the 22 July 1662 Salviati letter was published by Ferdinand Boyer in 1931, page 238.",
            "author": "cand-3517", "publication": "cand-11262", "locator": "Boyer, 1931, p. 238",
            "mention": "m-chp1-secii-p14-n4-boyer-1931-p238", "occurrence": 0, "cited_document": "cand-3557", "body": BODY_IDS[4],
        },
        {
            "marker": 5, "key": "luzio-p295-arragona-letter", "start": 567, "end": 568,
            "quote": "Luzio, p. 295", "claim": "Haskell says that the 9 October 1621 Arragona letter was published by Luzio, page 295.",
            "author": "cand-3515", "publication": "cand-7052", "locator": "Luzio, p. 295",
            "mention": "m-chp1-secii-p14-n5-luzio-p295", "occurrence": 0, "cited_document": "cand-3558", "body": BODY_IDS[5],
        },
        {
            "marker": 6, "key": "v-ruffo-p97-guercino-letter", "start": 569, "end": 570,
            "quote": "V. Rufifo, P- 97-", "claim": "Haskell says that the 25 September 1649 Guercino letter was published by V. Ruffo, page 97; the print corrects S0 OCR variants.",
            "author": "cand-3474", "publication": "cand-6454", "locator": "V. Ruffo, p. 97",
            "mention": "m-chp1-secii-p14-n6-v-ruffo-p97", "occurrence": 0, "cited_document": "cand-3559", "body": BODY_IDS[6],
            "corrections": CORRECTIONS_6,
        },
    ]

    note_context: dict[int, list[str]] = {1: [], 2: [], 3: []}
    note_context[4] = ["st-chp1-secii-p14-n4-salviati-letter-authored-by", "st-chp1-secii-p14-n4-salviati-letter-addressed-to"]
    note_context[5] = ["st-chp1-secii-p14-n5-arragona-letter-authored-by", "st-chp1-secii-p14-n5-arragona-letter-addressed-to"]
    note_context[6] = ["st-chp1-secii-p14-n6-guercino-letter-authored-by", "st-chp1-secii-p14-n6-guercino-letter-addressed-to"]

    new_statements.extend(mk_letter_rows(
        4, "salviati", "to Cardinal Leopoldo de’ Medici", "cand-3557", "cand-3475", "Jacopo Salviati",
        "cand-1629", "Cardinal Leopoldo de’ Medici", "1662-07-22", 565, 566,
        "Jacopo Salviati", "Cardinal Leopoldo de’ Medici",
    ))
    new_statements.extend(mk_letter_rows(
        5, "arragona", "to an unnamed ducal chancellor", "cand-3558", "cand-3476", "Fabrizio Arragona",
        "cand-11840", "an unnamed ducal chancellor", "1621-10-09", 567, 568,
        "Fabrizio Arragona", "a ducal chancellor",
    ))
    new_statements.extend(mk_letter_rows(
        6, "guercino", "to Don Antonio Ruffo", "cand-3559", "cand-1258", "Guercino",
        "cand-2297", "Don Antonio Ruffo", "1649-09-25", 569, 570,
        "Guercino", "Don Antonio Ruffe", CORRECTIONS_6,
    ))

    citation_rows: dict[int, dict] = {}
    for spec in citation_specs:
        marker = spec["marker"]
        note_ids = note_context[marker]
        citations = [{
            "source_candidate_id": spec["author"],
            "publication_candidate_id": spec["publication"],
            "locator": spec["locator"],
        }]
        extra = {
            "citation_candidate_id": spec["author"],
            "citation_publication_candidate_id": spec["publication"],
            "citation_locator": spec["locator"],
            "citations": citations,
            "citation_mention_ids": [spec["mention"]],
            "cited_material_not_independently_consulted": True,
            "cited_document_candidate_id": spec["cited_document"],
            "linked_statement_ids": note_ids,
            "related_note_statement_ids": note_ids,
        }
        row = mk_row(
            f"n{marker}-cites-{spec['key']}", "cites", spec["claim"], spec["start"], spec["end"], spec["quote"], marker,
            ["cand-2962", spec["author"], spec["publication"]] + ([spec["cited_document"]] if spec["cited_document"] else []),
            subject="cand-2962", obj=spec["publication"], text_layer="bibliographic citation locator",
            qualification="This records Haskell's citation path and locator; the cited pages, publication contents and cited letter were not independently consulted.",
            relation_note="This is a source citation candidate, not an independently verified fact about the cited material.",
            corrections=spec.get("corrections"), extra=extra,
        )
        if spec["cited_document"] is None:
            row["qualifiers"].pop("cited_document_candidate_id", None)
        citation_rows[marker] = row
        new_statements.append(row)

    for marker, note_ids in note_context.items():
        if note_ids:
            cite_id = citation_rows[marker]["statement_id"]
            for note_id in note_ids:
                next(row for row in new_statements if row["statement_id"] == note_id)["qualifiers"]["linked_statement_ids"] = [cite_id]

    # Place each citation after its letter metadata in printed note order.
    order = {row["statement_id"]: index for index, row in enumerate(new_statements)}
    new_statements.sort(key=lambda row: (row["qualifiers"]["footnote_marker"], order[row["statement_id"]]))

    mention_specs = [
        ("m-chp1-secii-p14-n1-mancini-i-p140", "cand-6089", "Mancini, I, p. 140", "Exact citation locator for Giulio Mancini volume I, page 140; the cited page was not independently consulted.", 0),
        ("m-chp1-secii-p14-n2-luzio-p48", "cand-7052", "Luzio, p. 48", "Exact p.14 footnote 2 citation locator; the earlier p.13 occurrence is occurrence 0, and the cited page was not independently consulted.", 1),
        ("m-chp1-secii-p14-n3-faldi-1957-pp278-295", "cand-4331", "Faldi, 1957, pp. 278-95", "Exact citation locator to the bibliography-identified 1957 Faldi study; the cited pages were not independently consulted.", 0),
        ("m-chp1-secii-p14-n4-boyer-1931-p238", "cand-11262", "Ferdinand Boyer, 1931, p. 238", "Exact locator to Boyer's 1931 publication of the Salviati letter; cited page not independently consulted.", 0),
        ("m-chp1-secii-p14-n5-luzio-p295", "cand-7052", "Luzio, p. 295", "Exact locator to Luzio's 1913 publication of the Arragona letter; cited page not independently consulted.", 0),
        ("m-chp1-secii-p14-n6-v-ruffo-p97", "cand-6454", "V. Rufifo, P97-", "S0 OCR locator; printed p.14 confirms V. Ruffo, p.97. The cited page was not independently consulted.", 0),
        ("m-chp1-secii-p14-n5-ducal-chancellor", "cand-11840", "a ducal chancellor", "Unnamed addressee of Arragona's 9 October 1621 letter; no personal identity is inferred.", 0),
    ]
    new_mentions = []
    for mention_id, candidate_id, phrase, note, occurrence in mention_specs:
        start, end, surface = normalized_span(flat_note, phrase, occurrence)
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": NOTE_SEG,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    # Update exact existing mentions where the page image clarifies identity or role.
    mention_by_id = {row["mention_id"]: row for row in mentions}
    mention_updates = {
        "m-chp1-secii-0508": ("cand-1507", "The surrounding body names Giulio Mancini; this note cites his Considerazioni, volume I, page 140."),
        "m-chp1-secii-0511": (None, "Luzio cited at page 48; the publication is matched to the bibliography candidate cand-7052, while this person mention is retained."),
        "m-chp1-secii-0512": (None, "Luzio citation for publication of Arragona's 1621 letter at page 295; bibliography publication candidate cand-7052, cited page unconsulted."),
        "m-chp1-secii-0513": (None, "Faldi is cited for the Guidotti example at pages 278–295; bibliography publication candidate cand-4331, cited pages unconsulted."),
        "m-chp1-secii-0514": (None, "Ferdinand Boyer is named as publisher of the Salviati letter; bibliography candidate cand-11262 records the 1931 article, page 238 unconsulted."),
        "m-chp1-secii-0393": (None, "Rome is where the note identifies Arragona as the Mantuan agent; it is not described as a departure destination or as the letter's endpoint."),
        "m-chp1-secii-0375": (None, "Recipient of Guercino's dated letter; S0 OCR reads Ruffe, while printed p.14 confirms Ruffo."),
        "m-chp1-secii-0368": (None, "OCR variant of publisher V. Ruffo; printed p.14 confirms the name and page 97."),
    }
    if not set(mention_updates).issubset(mention_by_id):
        raise SystemExit(f"expected p.14 mentions missing: {sorted(set(mention_updates) - set(mention_by_id))}")
    for mention_id, (candidate_id, note) in mention_updates.items():
        if candidate_id:
            mention_by_id[mention_id]["candidate_id"] = candidate_id
        mention_by_id[mention_id]["note"] = note

    citation_mention_ids = {spec["marker"]: spec["mention"] for spec in citation_specs}
    for marker, row in citation_rows.items():
        if row["qualifiers"]["citation_mention_ids"] != [citation_mention_ids[marker]]:
            raise SystemExit(f"citation mention mismatch for marker {marker}")

    new_ids = [row["statement_id"] for row in new_statements]
    if len(new_statements) != 12 or len(new_ids) != len(set(new_ids)) or set(new_ids) & set(statement_by_id):
        raise SystemExit(f"unexpected or colliding p.14 statements: {len(new_statements)}")
    candidate_ids = set(candidate_by_id)
    referenced = set()
    for row in new_statements:
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key):
                referenced.add(row[key])
        referenced.update(row["qualifiers"].get("mentioned_candidate_ids", []))
        if row["original_quote"] not in "\n".join(full_lines[row["qualifiers"]["source_line_start"] - 1 : row["qualifiers"]["source_line_end"]]):
            raise SystemExit(f"source quote is outside protected lines: {row['statement_id']}")
        marker = row["qualifiers"]["footnote_marker"]
        if marker not in BODY_IDS or row["qualifiers"]["footnote_refs"] != [{"marker": marker, "segment_id": NOTE_SEG, "source_line": MARKER_LINES[marker]}]:
            raise SystemExit(f"incorrect body/note marker mapping: {row['statement_id']}")
    referenced.update(row["candidate_id"] for row in new_mentions)
    missing = sorted(referenced - candidate_ids)
    if missing:
        raise SystemExit(f"missing candidate foreign keys: {missing}")
    existing_mention_ids = {row["mention_id"] for row in mentions}
    if len(existing_mention_ids) != len(mentions) or any(row["mention_id"] in existing_mention_ids for row in new_mentions):
        raise SystemExit("duplicate mention IDs in protected tables")
    natural_keys = {(row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"]) for row in mentions}
    for row in new_mentions:
        key = (row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"])
        if key in natural_keys:
            raise SystemExit(f"duplicate mention natural key: {key}")
        natural_keys.add(key)
        a, b = int(row["start_char"]), int(row["end_char"])
        if flat_note[a:b] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']}")
    if mention_by_id["m-chp1-secii-0508"]["candidate_id"] != "cand-1507":
        raise SystemExit("Mancini mention was not mapped to the named Giulio Mancini candidate")
    final_mentions = mentions + new_mentions
    keys = [(row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"]) for row in final_mentions]
    if len(keys) != len(set(keys)):
        raise SystemExit("p.14 mention update creates a duplicate natural key")

    # Replace the broad row, then create reciprocal links only for printed markers 1–6.
    rebuilt_statements = []
    inserted = False
    for row in statements:
        if row["statement_id"] == OLD_ID:
            rebuilt_statements.extend(new_statements)
            inserted = True
            continue
        rebuilt_statements.append(row)
    if not inserted:
        raise SystemExit("failed to replace the protected p.14 note row")
    rebuilt_by_id = {row["statement_id"]: row for row in rebuilt_statements}
    precise_links = {
        "st-chp1-secii-l79-84-08": [citation_rows[1]["statement_id"]],
        "st-chp1-secii-l79-84-02": [citation_rows[2]["statement_id"]],
        "st-chp1-secii-l79-84-03": [citation_rows[3]["statement_id"]],
        "st-chp1-secii-l79-84-04": [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_marker"] == 4],
        "st-chp1-secii-l79-84-10": [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_marker"] == 5],
        "st-chp1-secii-l79-84-11": [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_marker"] == 5],
        "st-chp1-secii-l79-84-06": [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_marker"] == 6],
    }
    for row in rebuilt_statements:
        q = row.get("qualifiers", {})
        for field in ("linked_statement_ids", "related_body_statement_ids", "linked_body_statement_ids", "footnote_statement_ids"):
            if field in q:
                q[field] = [value for value in q[field] if value != OLD_ID]
    for body_id, note_ids in precise_links.items():
        if body_id not in rebuilt_by_id:
            raise SystemExit(f"expected p.14 body statement missing: {body_id}")
        q = rebuilt_by_id[body_id].setdefault("qualifiers", {})
        q["linked_statement_ids"] = [value for value in q.get("linked_statement_ids", []) if value != OLD_ID]
        append_unique(q["linked_statement_ids"], note_ids)
    for row in new_statements:
        q = row["qualifiers"]
        for body_id in q["linked_body_statement_ids"]:
            if row["statement_id"] not in rebuilt_by_id[body_id]["qualifiers"].get("linked_statement_ids", []):
                raise SystemExit(f"body/note link is not reciprocal: {row['statement_id']} / {body_id}")
        for target in q.get("linked_statement_ids", []):
            if target not in rebuilt_by_id:
                raise SystemExit(f"linked note statement missing: {row['statement_id']} -> {target}")
            if row["statement_id"] not in rebuilt_by_id[target]["qualifiers"].get("linked_statement_ids", []):
                raise SystemExit(f"note/citation link is not reciprocal: {row['statement_id']} / {target}")

    note_coverage = [row for row in coverage if row["segment_id"] == NOTE_SEG]
    if len(note_coverage) != 1:
        raise SystemExit("expected exactly one coverage row for the merged p.14 notes")
    note_coverage[0]["note"] = note_coverage[0]["note"].rstrip() + (
        " Printed p.14 (PDF physical p.13) notes 1–6 were checked against the page image. "
        "The broad correspondence/citation row for L562–570 was replaced by 12 source-specific citation and letter-metadata statements. "
        "The 1662 Salviati–Leopoldo, 1621 Arragona–unnamed ducal chancellor, and 1649 Guercino–Antonio Ruffo letters reuse existing candidates; "
        "the chancellor remains unnamed. Citation locators were linked to the bibliography candidates; cited letters and pages were not independently consulted. "
        "The print confirms note 6 (not OCR 9), Ruffo (not Ruffe/Rufifo), and p.97 (not OCR P- 97-); S0 is unchanged. No KU or formal relation was added."
    )

    # Confirm all candidate and statement links remain resolvable after replacing the broad row.
    all_statement_ids = set(rebuilt_by_id)
    if OLD_ID in all_statement_ids:
        raise SystemExit("broad p.14 note row still exists")
    for row in new_statements:
        q = row["qualifiers"]
        for key in ("linked_statement_ids", "related_note_statement_ids", "linked_body_statement_ids", "related_body_statement_ids"):
            missing_targets = sorted(set(q.get(key, [])) - all_statement_ids)
            if missing_targets:
                raise SystemExit(f"statement link targets missing for {row['statement_id']}: {missing_targets}")

    updated = {
        "book-statements.jsonl": rebuilt_statements,
        "mentions.csv": mentions + new_mentions,
        "s2-coverage.csv": coverage,
    }
    summary = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-1.pdf print p.14 / S0 L562-570",
        "replaced_statement_ids": [OLD_ID],
        "new_statement_count": len(new_statements),
        "new_statement_ids": new_ids,
        "new_mention_count": len(new_mentions),
        "new_mention_ids": [row["mention_id"] for row in new_mentions],
        "updated_existing_mentions": sorted(mention_updates),
        "coverage_disposition": note_coverage[0]["disposition"],
        "coverage_migration_status": note_coverage[0]["migration_status"],
        "source_unchanged": True,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    write_names = set(updated)
    backups: dict[str, Path] = {}
    temp_paths: dict[str, Path] = {}
    try:
        for name in write_names:
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
        for name, rows in updated.items():
            path = paths[name]
            temp = path.with_name(path.name + ".tmp-s2-p14")
            if temp.exists():
                raise SystemExit(f"stale temp file exists; refusing overwrite: {temp.name}")
            if name.endswith(".jsonl"):
                write_jsonl(temp, rows)
            else:
                write_csv(temp, rows)
            temp_paths[name] = temp
        for name, temp in temp_paths.items():
            os.replace(temp, paths[name])
    except Exception:
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        for temp in temp_paths.values():
            if temp.exists():
                temp.unlink()
        raise
    summary["backups"] = {name: path.name for name, path in backups.items()}
    summary["post_hashes"] = {name: digest(paths[name]) for name in write_names}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
