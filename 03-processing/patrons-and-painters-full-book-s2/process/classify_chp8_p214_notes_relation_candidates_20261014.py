"""Classify p.214 footnotes and preserve an unresolved group-level ownership claim."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p214_notes_crop.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i_notes_p214_visual-transcription:l1-4"
SEGMENT_SHA = "6251d0350afb065bc2eef799260b7fb2501befb9dab467b6f67aac08656497ef"
BACKUP_SUFFIX = ".bak-s2-chp8-p214-notes-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "d8aa689f7a6b5be7a53bf62b044d9f4478ae154a3cc9378b66fdc51071788ad4",
    CANDIDATES: "279368e4d604acd42ad46d484941e8640a9e16fffb453c7b4ea07e937d89b0bc",
    MENTIONS: "49d7aaa50c1b246bbbe53d6229a914d1d9f246ce17c3dd0da81b6f1e3a237cb8",
    SOURCE: "7ab316ce528ffc7cdf49c1304339ed6337ac5b29b7839df3160ac281ee2e15dd",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "afeba1858ea9b14d0daec13925d8c5ac183b720fe9049288e05cb35bf1005811",
}

TRUE_NOTES = {
    "st-chp8-p214-n1-boni-mythological-frescoes":
        "Haskell reports a commission-like request by the Del Rosso family to Boni for palace-room mythological frescoes; the palace and individual works remain unidentified.",
    "st-chp8-p214-n1-dal-sole-monti-historical-pictures":
        "This is a source-level report of the Del Rosso family's historical picture group by dal Sole and Monti; the individual works are not named.",
    "st-chp8-p214-n4-valery-contarini-paintings":
        "This preserves Valéry's early nineteenth-century report of Giordano paintings at Palazzo Contarini, including one described as Aeneas carrying Anchises; it is not an independently verified inventory.",
    "st-chp8-p214-n4-venetian-admirers":
        "Haskell reports a reception relation between Giordano and Solimena and admirers in Venice; the admirers are unnamed and no individual ties are inferred.",
    "st-chp8-p214-n4-venetian-patrons-owned-pictures":
        "The note says the listed Venetian patron group owned pictures by one or the other of Giordano and Solimena; preserve this disjunctive group claim without assigning individual paintings to particular owners.",
}

FALSE_NOTES = {
    "st-chp8-p214-n1-cite-soprani": "This is a bibliographic locator for the Boni decoration, not an independent historical relation.",
    "st-chp8-p214-n1-cite-zanotti-vol-i": "This is a bibliographic locator for the collection's historical pictures, not an independent historical relation.",
    "st-chp8-p214-n1-cite-zanotti-vol-ii": "This is a bibliographic locator for the volume-II passage at p.120; the separate p.231 locator is registered below.",
    "st-chp8-p214-n2-cite-de-dominici": "This is a bibliographic locator attached to the Giordano canvases, not an independent historical relation.",
    "st-chp8-p214-n3-cite-de-dominici-bologna": "This is a bibliographic locator attached to the Solimena picture claim, not an independent historical relation.",
    "st-chp8-p214-n4-cite-de-dominici-bologna": "These are bibliographic locators attached to Haskell's Venetian ownership discussion, not independent historical relations.",
    "st-chp8-p214-n4-cite-loret": "This is a reading pointer for Neapolitan artists in Rome, not an independent historical relation.",
    "st-chp8-p214-n4-cite-monaco-engravings": "This is a locator to three numbered engravings used alongside the Venetian ownership account; it is not itself an independent relation among historical actors.",
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12055",
        "canonical_name": "Venetian picture-owning patrons named in Haskell's p.214 note",
        "suggested_type": "",
        "status": "open",
        "detail": "Source-defined group comprising the Labia, Procuratore Canale, Flaminio Corner, the Giovanelli and the Widmann. The text does not consistently distinguish family from individual referents or map a specific work to each owner; keep the group's type and composition open.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L4",
    },
    {
        "candidate_id": "cand-12056",
        "canonical_name": "Unidentified Giordano or Solimena pictures held by Venetian patrons",
        "suggested_type": "work",
        "status": "open",
        "detail": "Source-defined plural group. Haskell says the named Venetian patrons owned pictures by one or the other of Luca Giordano and Francesco Solimena, without titles, count, or owner-to-work allocation.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L4",
    },
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(fields: list[str], rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after guarded dry-run checks pass")
    args = parser.parse_args()
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED_HASHES:
        raise SystemExit("a reviewed table, source, PDF, or page image changed; re-review before applying")

    source_text = SOURCE.read_text(encoding="utf-8-sig")
    if sha(source_text.rstrip("\n").encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("the p.214 visual transcription changed since review")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (
        segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
        segment.get("sha256"), segment.get("asset_sha256"),
    ) != (SOURCE_REL, 1, 4, SEGMENT_SHA, EXPECTED_HASHES[SOURCE]):
        raise SystemExit("the S0 segment manifest does not match the reviewed transcription")

    statements = read_jsonl(STATEMENTS)
    by_statement = {row["statement_id"]: row for row in statements}
    if len(by_statement) != len(statements):
        raise SystemExit("statement identifiers are not unique")
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {
        row["statement_id"] for row in page_rows
        if "relation_candidate" not in (row.get("qualifiers") or {})
    }
    if len(page_rows) != 13 or unset != set(TRUE_NOTES) | set(FALSE_NOTES):
        raise SystemExit(f"unexpected p.214 note inventory: rows={len(page_rows)}, unset={len(unset)}")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    by_candidate = {row["candidate_id"]: row for row in candidates}
    by_mention = {row["mention_id"]: row for row in mentions}
    if len(by_candidate) != len(candidates) or len(by_mention) != len(mentions):
        raise SystemExit("candidate or mention identifiers are not unique")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12054:
        raise SystemExit("candidate sequence changed since review")
    new_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    new_mention_ids = {"m-chp8-p214-074", "m-chp8-p214-075"}
    new_statement_id = "st-chp8-p214-n1-cite-zanotti-vol-ii-p231"
    if new_candidate_ids & set(by_candidate) or new_mention_ids & set(by_mention) or new_statement_id in by_statement:
        raise SystemExit("a planned p.214 identifier already exists")

    text = source_text.strip("\n")
    planned_spans = [
        ("m-chp8-p214-074", "cand-12055", "the Labia, who are discussed separately in Chapter 9, the Procuratore Canale, Flaminio Corner, the Giovanelli and the Widmann"),
        ("m-chp8-p214-075", "cand-12056", "pictures by one or other of them"),
    ]
    new_mentions = []
    for mention_id, candidate_id, surface in planned_spans:
        start = text.find(surface)
        if start < 0 or text.find(surface, start + 1) >= 0 or text[start:start + len(surface)] != surface:
            raise SystemExit(f"planned source span does not match exactly: {surface!r}")
        end = start + len(surface)
        for row in mentions:
            if row["segment_id"] != SEGMENT_ID:
                continue
            other_start, other_end = int(row["start_char"]), int(row["end_char"])
            if start < other_end and end > other_start:
                contained = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
                if not contained:
                    raise SystemExit(f"planned group span overlaps non-nested mention {row['mention_id']}")
        new_mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(end),
            "note": "Source-defined group mention; nested member or work descriptions remain mapped to their existing candidates.",
        })

    for row in NEW_CANDIDATES:
        candidates.append({
            "candidate_id": row["candidate_id"], "index_entry_id": "", "canonical_name": row["canonical_name"],
            "index_page_range": "", "suggested_type": row["suggested_type"], "status": row["status"],
            "index_source_file": "", "sub_entry": "", "detail": row["detail"], "exclude_reason": "",
            "candidate_origin": row["candidate_origin"], "candidate_source_ref": row["candidate_source_ref"],
        })
    mentions.extend(new_mentions)

    for statement_id, note in TRUE_NOTES.items():
        q = dict(by_statement[statement_id].get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        by_statement[statement_id]["qualifiers"] = q
    for statement_id, note in FALSE_NOTES.items():
        q = dict(by_statement[statement_id].get("qualifiers") or {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
        by_statement[statement_id]["qualifiers"] = q

    existing_zanotti = by_statement["st-chp8-p214-n1-cite-zanotti-vol-ii"]
    existing_zanotti["qualifiers"]["claim"] = (
        "Haskell cites Zanotti, volume II, p.120, for the Del Rosso paintings."
    )

    patron_statement = by_statement["st-chp8-p214-n4-venetian-patrons-owned-pictures"]
    patron_statement["subject_candidate_id"] = "cand-12055"
    patron_statement["object_candidate_id"] = "cand-12056"
    patron_statement["predicate"] = "venetian_patron_group_owned_pictures_by_giordano_or_solimena"
    q = dict(patron_statement.get("qualifiers") or {})
    q["mentioned_candidate_ids"] = [
        "cand-12055", "cand-12056", "cand-1349", "cand-0497", "cand-0844", "cand-7617", "cand-2812", "cand-1172", "cand-2484"
    ]
    q["qualification"] = "This preserves the source's group-level disjunction. It does not assign a particular painting or artist to each named owner."
    patron_statement["qualifiers"] = q

    cite = {
        "statement_id": new_statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": None,
        "object_candidate_id": "cand-7115",
        "predicate": "footnote_citation",
        "qualifiers": {
            "source_line_start": 1, "source_line_end": 1, "printed_page": 214, "pdf_physical_page": 12,
            "claim": "Haskell cites Zanotti, volume II, p.231, for Giacomo Antonio Boni's decoration of the Del Rosso palace rooms.",
            "speaker": "Haskell footnote", "text_layer": "bibliographic pointer",
            "qualification": "Citation locator only; the cited page was not independently read.",
            "mentioned_candidate_ids": ["cand-7115", "cand-7489", "cand-0388", "cand-7615"],
            "footnote_marker": 1,
            "linked_body_statement_ids": [
                "st-chp8-p212-altar-picture-left-for-pupil-completion",
                "st-chp8-p213-collection-emphasis-on-naples-and-neglect-of-rome",
                "st-chp8-p214-durazzo-naples-continuation",
            ],
            "footnote_segment": SEGMENT_ID,
            "footnote_body_link_status": "linked",
            "citations": [{"source_candidate_id": "cand-7115", "volume": "II", "page": "231"}],
            "relation_candidate": False,
            "relation_candidate_note": "This is a bibliographic locator for the Boni decoration, not an independent historical relation.",
        },
        "original_quote": "Zanotti, II, p. 231",
        "origin": "book",
        "source_file": SOURCE_REL,
    }
    statements.append(cite)
    by_statement[new_statement_id] = cite

    new_statements = jsonl_bytes(statements)
    new_candidates = csv_bytes(candidate_fields, candidates)
    new_mentions_data = csv_bytes(mention_fields, mentions)
    counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in page_rows)
    counts[False] += 1
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES, MENTIONS)]
    print("DRY RUN p.214 footnote visual transcription")
    print(f"segment={SEGMENT_ID} existing_statements={len(page_rows)} classified={len(unset)} added_statements=1 added_candidates=2 added_mentions=2")
    print(f"segment counts after write: true={counts[True]} false={counts[False]} unset={counts[None]}")
    print(f"group endpoints: cand-12055 -> cand-12056; exact spans {planned_spans[0][2]!r}, {planned_spans[1][2]!r}")
    for path, data in [(STATEMENTS, new_statements), (CANDIDATES, new_candidates), (MENTIONS, new_mentions_data)]:
        print(f"{path.relative_to(ROOT)} before={EXPECTED_HASHES[path]} after={sha(data)}")
    if not args.apply:
        print("No files written. Use --apply to write after reviewing this summary.")
        return
    if any(path.exists() for path in backup_paths):
        raise SystemExit("a recovery backup already exists")
    for path, backup in zip((STATEMENTS, CANDIDATES, MENTIONS), backup_paths, strict=True):
        shutil.copy2(path, backup)
    for path, data in [(STATEMENTS, new_statements), (CANDIDATES, new_candidates), (MENTIONS, new_mentions_data)]:
        atomic_write(path, data)
    print("APPLIED; recovery copies:")
    for backup in backup_paths:
        print(f"  {backup.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
