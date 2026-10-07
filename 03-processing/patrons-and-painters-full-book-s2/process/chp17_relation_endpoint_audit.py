"""Controlled Chapter 17 S2 relation-endpoint audit.

Defaults to dry-run. Applying changes requires the reviewed source, segment,
candidate, statement-count, note-link, and open-endpoint preconditions to match.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_NAME = "02-sources/02-Markdown/17_CHP-17_sec_i.md"
SOURCE_PATH = ROOT / SOURCE_NAME
EXPECTED_SOURCE_SHA256 = "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4"
EXPECTED_SEGMENT_HASHES = {
    "chp-17:17_CHP-17_sec_i:l3-6": "b5b2aba63a1ef5d99362371c82568c057e985b8f9ff46687903268faa600568d",
    "chp-17:17_CHP-17_sec_i:l8-20": "4f3a9cd680dade7a13248a16b40639912ff4102640ab23f823e1bf72f20c2f83",
}
EXPECTED_MAX_CANDIDATE = 11473
EXPECTED_STATEMENT_COUNT = 12228
EXPECTED_RELATION_COUNTS = (2310, 2289, 21)
EXPECTED_OPEN_ENDPOINTS = {
    "st-chp17-pi-manfrin-1786-arms-permit": ("cand-1512", None),
    "st-chp17-p380-collection-venetian-painters-span": ("cand-1513", None),
}

PERMIT_QUOTE = (
    "in 1786 we find him back again with a special permit to carry arms "
    "so as to discourage possible attempts on his life.6"
)
RETURN_QUOTE = "Venice4; but this was revoked, and in 1786 we find him back again"
COLLECTION_QUOTE = (
    "The Venetian pictures began with Mantegna and Bellini, and thereafter most of the great and lesser painters were included up to his own contemporaries,\n"
    "Francesco Guardi, and Gian Domenico Tiepolo."
)
NEW_ROWS = [
    ("st-chp17-pi-manfrin-returned-to-venice-1786", "cand-2719", "Venice"),
    ("st-chp17-p380-manfrin-collection-represented-mantegna", "cand-1522", "Mantegna"),
    ("st-chp17-p380-manfrin-collection-represented-bellini", "cand-0270", "Bellini"),
    ("st-chp17-p380-manfrin-collection-represented-guardi", "cand-1239", "Guardi"),
    ("st-chp17-p380-manfrin-collection-represented-gian-domenico-tiepolo", "cand-2624", "Gian Domenico Tiepolo"),
]
NEW_STATEMENT_IDS = {row[0] for row in NEW_ROWS}

NOTE4_ID = "st-chp17-pi-note4-1770-archive-locator"
NOTE4_QUOTE = "4 Archivio di Stato, Venice—Inquisitori, 53 8, p. 43—29 Genaro 1770."
NOTE5_ID = "st-chp17-pi-note5-1786-archive-locator"
NOTE5_QUOTE = "6 ibid., 540, p. 6—12 Giugno 1786."
P380_NOTE5_IDS = [
    "st-chp17-p380-note5-edwards-record",
]
DUPLICATED_CATALOGUE_BODY_IDS = [
    "st-chp17-p380-sale-catalogue-1856",
    "st-chp17-p380-nicoletti-catalogue-1872",
    "st-chp17-p380-undated-print-catalogue",
]
ARTISTS = {
    "cand-1522": "Mantegna",
    "cand-0270": "Bellini",
    "cand-1239": "Guardi",
    "cand-2624": "Gian Domenico Tiepolo",
}


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def encode_jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)


def atomic_write(path: Path, text: str):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        f.write(text)
        temporary = Path(f.name)
    temporary.replace(path)


def relation_counts(rows):
    relations = [r for r in rows if r.get("qualifiers", {}).get("relation_candidate") is True]
    complete = sum(bool(r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in relations)
    return len(relations), complete, len(relations) - complete


def require_literal(source_lines, line_start, line_end, quote, label):
    excerpt = "\n".join(source_lines[line_start - 1 : line_end])
    if quote not in excerpt:
        raise SystemExit(f"reviewed quote is not present in source lines for {label}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes; default is dry-run")
    parser.add_argument("--show-diff", action="store_true", help="print before/after rows in dry-run")
    args = parser.parse_args()

    candidate_path = TABLES / "entity-candidates.csv"
    statement_path = TABLES / "book-statements.jsonl"
    segment_path = TABLES / "segments.jsonl"
    if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise SystemExit("Chapter 17 source asset changed")
    source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
    segment_by_id = {r["segment_id"]: r for r in read_jsonl(segment_path)}
    for segment_id, expected_hash in EXPECTED_SEGMENT_HASHES.items():
        meta = segment_by_id.get(segment_id)
        if (
            not meta
            or meta.get("source_file") != SOURCE_NAME
            or meta.get("sha256") != expected_hash
            or meta.get("asset_sha256") != EXPECTED_SOURCE_SHA256
        ):
            raise SystemExit(f"source segment manifest changed: {segment_id}")
        excerpt = "\n".join(source_lines[int(meta["line_start"]) - 1 : int(meta["line_end"])])
        if hashlib.sha256(excerpt.encode("utf-8")).hexdigest() != expected_hash:
            raise SystemExit(f"source segment hash mismatch: {segment_id}")
    require_literal(source_lines, 6, 6, PERMIT_QUOTE, "1786 arms permit")
    require_literal(source_lines, 6, 6, RETURN_QUOTE, "1786 return to Venice")
    require_literal(source_lines, 12, 13, COLLECTION_QUOTE, "Manfrin collection span")

    with candidate_path.open(encoding="utf-8-sig", newline="") as f:
        candidates = list(csv.DictReader(f))
    statements = read_jsonl(statement_path)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    statement_by_id = {r["statement_id"]: r for r in statements}
    if len(candidate_by_id) != len(candidates) or len(statement_by_id) != len(statements):
        raise SystemExit("duplicate identifiers in candidate or statement table")
    if max(int(r["candidate_id"].split("-")[-1]) for r in candidates) != EXPECTED_MAX_CANDIDATE:
        raise SystemExit("candidate sequence changed")
    if len(statements) != EXPECTED_STATEMENT_COUNT or relation_counts(statements) != EXPECTED_RELATION_COUNTS:
        raise SystemExit(f"table counts changed: statements={len(statements)}, relations={relation_counts(statements)}")

    open_ids = {
        r["statement_id"]: (r.get("subject_candidate_id"), r.get("object_candidate_id"))
        for r in statements
        if r["statement_id"].startswith("st-chp17-")
        and r.get("qualifiers", {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    }
    if open_ids != EXPECTED_OPEN_ENDPOINTS:
        raise SystemExit(f"Chapter 17 open endpoint set changed: {open_ids}")
    if not NEW_STATEMENT_IDS.isdisjoint(statement_by_id):
        raise SystemExit("one or more planned statement IDs already exist")

    for candidate_id, expected_type in {
        "cand-1512": "person",
        "cand-2719": "place",
        "cand-10684": "archive",
        "cand-10685": "archive",
        **{candidate_id: "person" for candidate_id in ARTISTS},
    }.items():
        if candidate_by_id.get(candidate_id, {}).get("suggested_type") != expected_type:
            raise SystemExit(f"candidate type precondition changed: {candidate_id}")
    collection = candidate_by_id.get("cand-1513", {})
    if (
        collection.get("suggested_type") != ""
        or collection.get("sub_entry") != "collection"
        or collection.get("canonical_name") != "Manfrin, Girolamo"
        or candidate_by_id["cand-1512"].get("index_entry_id") == collection.get("index_entry_id")
    ):
        raise SystemExit("Manfrin collection candidate/type boundary changed")

    note4 = statement_by_id.get(NOTE4_ID)
    note5 = statement_by_id.get(NOTE5_ID)
    p380_note5 = statement_by_id.get(P380_NOTE5_IDS[0])
    if not note4 or note4.get("original_quote") != NOTE4_QUOTE:
        raise SystemExit("the p.379 note 4 banishment locator changed")
    if not note5 or note5.get("original_quote") != NOTE5_QUOTE:
        raise SystemExit("the p.379 note 5 arms-permit locator changed")
    for note_id in P380_NOTE5_IDS + DUPLICATED_CATALOGUE_BODY_IDS:
        if note_id not in statement_by_id:
            raise SystemExit(f"missing p.380 note 5 or duplicate-body statement: {note_id}")
    stale_note5_refs = [
        "st-chp17-p380-note5-edwards-record",
        "st-chp17-p380-note5-sale-catalogue",
        "st-chp17-p380-note5-nicoletti-catalogue",
        "st-chp17-p380-note5-print-catalogue",
    ]
    if p380_note5.get("qualifiers", {}).get("footnote_note_statement_ids") != stale_note5_refs:
        raise SystemExit("the p.380 note 5 stale-reference state changed")
    if (
        p380_note5["qualifiers"].get("footnote_body_link_status") != "linked"
        or p380_note5["qualifiers"].get("footnote_body_line_range") != "L13-L20"
    ):
        raise SystemExit("the p.380 note 5 to body link changed")

    before = copy.deepcopy(statement_by_id)
    permit = statement_by_id["st-chp17-pi-manfrin-1786-arms-permit"]
    permit["predicate"] = "had_special_permit_to_carry_arms_in_1786"
    permit["original_quote"] = PERMIT_QUOTE
    pq = permit["qualifiers"]
    pq["claim"] = "Haskell says Manfrin had a special permit to carry arms in 1786 to discourage possible attempts on his life."
    pq["text_layer"] = "authorial report"
    pq["qualification"] = (
        "The stated purpose is retained; the passage does not identify an actual attack or assailant. "
        "The cited archival locator was not consulted."
    )
    pq["mentioned_candidate_ids"] = ["cand-1512", "cand-10685"]
    pq["relation_candidate"] = False
    pq["footnote_marker"] = "5"
    pq["footnote_segment"] = "chp-17:17_CHP-17_intro:l7-13"
    pq["footnote_line_range"] = "L12-L12"
    pq["footnote_text_pending"] = False
    pq["footnote_body_link_status"] = "linked"
    pq["footnote_body_line_range"] = "L6-L6"
    pq["footnote_note_statement_ids"] = [NOTE5_ID]
    pq["footnote_link_note"] = "Note 5 locates the cited 1786 Inquisitori record; the record was not consulted."
    pq["ocr_corrections"] = [
        {
            "source_file": SOURCE_NAME,
            "source_line": 6,
            "ocr": "life.6",
            "print": "life.5",
            "basis": "CHP-17.pdf physical page 1, printed folio i shows note marker 5 for the permit.",
        }
    ]

    collection_span = statement_by_id["st-chp17-p380-collection-venetian-painters-span"]
    collection_span["qualifiers"]["relation_candidate"] = False
    collection_span["qualifiers"]["qualification"] = (
        "This aggregate describes the collection's represented artist span and is decomposed into four named artist endpoints below. "
        "It does not identify individual works or settle attributions; the collection candidate remains untyped pending S3."
    )
    p380_note5["qualifiers"].pop("footnote_note_statement_ids", None)

    added = []
    returned = copy.deepcopy(permit)
    returned["statement_id"] = NEW_ROWS[0][0]
    returned["subject_candidate_id"] = "cand-1512"
    returned["object_candidate_id"] = "cand-2719"
    returned["predicate"] = "returned_to_venice_in_1786"
    returned["original_quote"] = RETURN_QUOTE
    rq = returned["qualifiers"]
    rq["source_line_start"] = 6
    rq["source_line_end"] = 6
    rq["claim"] = "Haskell reports that Manfrin was back in Venice in 1786 after the banishment described immediately before."
    rq["text_layer"] = "authorial report"
    rq["qualification"] = (
        "‘Back again’ refers to Venice, the place named in the immediately preceding banishment clause. "
        "The source says the banishment was revoked but does not date the revocation; note 4 locates the 1770 banishment record, "
        "which was not consulted and does not independently establish the later return."
    )
    rq["mentioned_candidate_ids"] = ["cand-1512", "cand-2719", "cand-10684"]
    rq["relation_candidate"] = True
    rq["footnote_marker"] = "4"
    rq["footnote_segment"] = "chp-17:17_CHP-17_intro:l7-13"
    rq["footnote_line_range"] = "L11-L11"
    rq["footnote_text_pending"] = False
    rq["footnote_body_link_status"] = "linked"
    rq["footnote_body_line_range"] = "L6-L6"
    rq["footnote_note_statement_ids"] = [NOTE4_ID]
    rq["footnote_link_note"] = (
        "Note 4 locates the 1770 banishment record attached to the preceding Venice clause; it is not independent evidence of the later revocation or return."
    )
    rq["cited_source_independently_consulted"] = False
    rq.pop("ocr_corrections", None)
    added.append(returned)

    marker_correction = [
        {
            "source_file": SOURCE_NAME,
            "source_line": 13,
            "ocr": "Gian Domenico Tiepolo.",
            "print": "Gian Domenico Tiepolo.5",
            "basis": "CHP-17.pdf physical page 2 shows printed note marker 5, omitted by S0 OCR.",
        }
    ]
    for statement_id, artist_id, artist_name in NEW_ROWS[1:]:
        row = copy.deepcopy(collection_span)
        row["statement_id"] = statement_id
        row["subject_candidate_id"] = "cand-1513"
        row["object_candidate_id"] = artist_id
        row["predicate"] = "collection_represented_works_by"
        row["original_quote"] = COLLECTION_QUOTE
        q = row["qualifiers"]
        q["source_line_start"] = 12
        q["source_line_end"] = 13
        q["claim"] = f"Haskell says the Venetian pictures in Manfrin's collection represented works by {artist_name}."
        q["speaker"] = "Haskell"
        q["text_layer"] = "authorial report"
        q["qualification"] = (
            "Collection-level scope is stated by Haskell; no individual work is identified or separately attributed. "
            "The collection candidate's type remains unresolved pending S3."
        )
        if artist_id == "cand-0270":
            q["qualification"] += (
                " The source names Bellini by surname only; the indexed Giovanni Bellini mapping remains provisional for S3."
            )
        q["mentioned_candidate_ids"] = ["cand-1513", artist_id]
        q["relation_candidate"] = True
        q["footnote_marker"] = "5"
        q["footnote_segment"] = "chp-17:17_CHP-17_sec_i:l26-35"
        q["footnote_line_range"] = "L30-L30"
        q["footnote_text_pending"] = False
        q["footnote_body_link_status"] = "linked"
        q["footnote_body_line_range"] = "L13-L20"
        q["footnote_note_statement_ids"] = list(P380_NOTE5_IDS)
        q["footnote_link_note"] = (
            "Printed note 5 follows the collection span, cites Edwards's gallery record, and repeats catalogue references already represented by the body statements. "
            "The manuscript was not consulted."
        )
        q["cited_source_independently_consulted"] = False
        q["ocr_corrections"] = marker_correction
        added.append(row)

    statements.extend(added)
    statement_by_id.update({row["statement_id"]: row for row in added})
    candidate_ids = set(candidate_by_id)
    for row in statements:
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if candidate_id and candidate_id not in candidate_ids:
                raise SystemExit(f"missing statement endpoint candidate: {row['statement_id']} -> {candidate_id}")
        for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if candidate_id not in candidate_ids:
                raise SystemExit(f"missing mentioned candidate: {row['statement_id']} -> {candidate_id}")

    remaining = {
        row["statement_id"]
        for row in statements
        if row["statement_id"].startswith("st-chp17-")
        and row.get("qualifiers", {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    }
    if remaining:
        raise SystemExit(f"unexpected Chapter 17 unresolved endpoint set: {sorted(remaining)}")
    expected_after = (2313, 2294, 19)
    if len(statements) != 12233 or relation_counts(statements) != expected_after:
        raise SystemExit(f"planned aggregate counts differ: statements={len(statements)}, relations={relation_counts(statements)}")

    print("Chapter 17 S2 relation-endpoint audit plan")
    print("open endpoint candidates: 2 -> 0; return-to-Venice relation and four collection-to-artist rows added")
    print("the 1786 arms permit remains an assertion; no specific collection works or attributions are invented")
    print("removed stale p.380 note 5 statement references; duplicate catalogue details remain represented by the existing body statements")
    print(f"statements: {EXPECTED_STATEMENT_COUNT} -> {len(statements)}")
    print(f"relation candidates (total/complete/open): {EXPECTED_RELATION_COUNTS} -> {relation_counts(statements)}")
    for statement_id in sorted(set(EXPECTED_OPEN_ENDPOINTS) | NEW_STATEMENT_IDS | {NOTE5_ID, P380_NOTE5_IDS[0]}):
        row = statement_by_id[statement_id]
        q = row.get("qualifiers", {})
        print(f"{statement_id}: {row.get('subject_candidate_id') or '∅'} → {row.get('object_candidate_id') or '∅'}; relation={q.get('relation_candidate')}; {q.get('claim')}")
        if args.show_diff:
            if statement_id in before:
                print("  BEFORE", json.dumps(before[statement_id], ensure_ascii=False))
            print("  AFTER ", json.dumps(row, ensure_ascii=False))
    if not args.apply:
        print("DRY-RUN only; inspect this plan, then pass --apply to write.")
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp17-s2-relation-audit-"))
    shutil.copy2(statement_path, backup_dir / statement_path.name)
    atomic_write(statement_path, encode_jsonl(statements))
    written = read_jsonl(statement_path)
    if len(written) != 12233 or relation_counts(written) != expected_after:
        raise SystemExit("post-write verification failed; recovery copy is available")
    written_ids = {row["statement_id"] for row in written}
    if not NEW_STATEMENT_IDS <= written_ids:
        raise SystemExit("one or more planned statements are missing after write")
    print(f"APPLIED; recovery copy: {backup_dir}")


if __name__ == "__main__":
    main()
