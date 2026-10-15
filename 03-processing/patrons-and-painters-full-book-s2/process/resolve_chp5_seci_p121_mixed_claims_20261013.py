from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md"
SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l9-15"
NOTE_SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l125-147"
PARENT_CLAUDE = "st-chp5-p121-claude-record"
PARENT_GUIDICCIONI = "st-chp5-p121-guidiccioni-attributions"
NOTE1_STATEMENT = "st-chp5-note-p121-n1-citation"
NEW_SALE_STATEMENT = "st-chp5-p121-copies-sold-as-originals"
COPY_GROUP = "cand-11907"
DOUBTFUL_WORKS_GROUP = "cand-11908"
EXPECTED_HASHES = {
    STATEMENTS: "130f195aaa72d67856bf0c92b522e76e1a9e60cc83554bc90aabc0c4ccda2949",
    CANDIDATES: "f01b843fe582a4a89df2350d13505a278c92ce93e138e5a58094295380d99dc3",
    MENTIONS: "9531f65cd13150c82ea34e00a2d5a940b2ac2291b5bb1891726daecc92437ecf",
}
EXPECTED_SOURCE_SHA = "d038ae7e4e778a83837f2cc9532e73b7cf65f14dd69ef72ec7f9269435a50144"
MENTION_IDS = {"m-chp5-p121-s2-copies-group", "m-chp5-p121-s2-doubtful-works"}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp5-p121-mixed-claims-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp5-p121-open-work-groups-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp5-p121-open-work-groups-20261013"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_csv(raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def render_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    result = output.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + result if raw.startswith(b"\xef\xbb\xbf") else result


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve mixed source claims and open work groups on printed page 121.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha(raw[path]) != expected:
            raise SystemExit(f"protected table changed: {path.name}")
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("one or more protected backups already exist")

    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SOURCE_SHA:
        raise SystemExit("protected S0 segment metadata changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha(source_text.encode("utf-8")) != EXPECTED_SOURCE_SHA:
        raise SystemExit("protected S0 segment changed")
    copy_surface = "copies of his works"
    copy_start = source_text.index(copy_surface)
    sale_end = source_text.index("as originals", copy_start) + len("as originals")
    doubtful_start = source_text.index("many a doubtful")
    doubtful_end = source_text.index("Perino del Vaga", doubtful_start) + len("Perino del Vaga")
    doubtful_surface = source_text[doubtful_start:doubtful_end]
    record_start = source_text.index("and as early as 1635 Claude")
    record_end = source_text.index("all his paintings", record_start) + len("all his paintings")
    copy_quote = source_text[copy_start:sale_end]
    record_quote = source_text[record_start:record_end]
    if (copy_start, sale_end, doubtful_start, doubtful_end) != (199, 265, 564, 626):
        raise SystemExit("protected source spans changed")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements) or any(sid in by_id for sid in (NEW_SALE_STATEMENT,)):
        raise SystemExit("duplicate or unexpected statement ID")
    for sid in (PARENT_CLAUDE, PARENT_GUIDICCIONI):
        if sid not in by_id or "relation_candidate" in (by_id[sid].get("qualifiers") or {}):
            raise SystemExit(f"protected target missing or already classified: {sid}")
    note1 = by_id.get(NOTE1_STATEMENT)
    if not note1 or NEW_SALE_STATEMENT in (note1.get("qualifiers") or {}).get("linked_body_statement_ids", []):
        raise SystemExit("footnote back-link target missing or already modified")
    for sid in (PARENT_CLAUDE, PARENT_GUIDICCIONI):
        if by_id[sid].get("segment_id") != SEGMENT_ID:
            raise SystemExit(f"segment identity changed for {sid}")
    if by_id[PARENT_CLAUDE].get("subject_candidate_id") != "cand-0767" or by_id[PARENT_CLAUDE].get("object_candidate_id") != "":
        raise SystemExit("Claude parent endpoints changed")
    if by_id[PARENT_GUIDICCIONI].get("subject_candidate_id") != "cand-1281" or by_id[PARENT_GUIDICCIONI].get("object_candidate_id") != "":
        raise SystemExit("Guidiccioni parent endpoints changed")
    if by_id[PARENT_GUIDICCIONI].get("original_quote", "").find("many a doubtful") < 0:
        raise SystemExit("Guidiccioni quotation changed")

    candidate_fields, candidates = load_csv(raw[CANDIDATES])
    mention_fields, mentions = load_csv(raw[MENTIONS])
    if {field for field in ("candidate_id", "canonical_name", "suggested_type", "status", "detail", "candidate_origin", "candidate_source_ref")} - set(candidate_fields):
        raise SystemExit("candidate table contract changed")
    if {field for field in ("mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note")} - set(mention_fields):
        raise SystemExit("mention table contract changed")
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    if candidate_ids.intersection({COPY_GROUP, DOUBTFUL_WORKS_GROUP}) or mention_ids.intersection(MENTION_IDS):
        raise SystemExit("new candidate or mention IDs already exist")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11906:
        raise SystemExit("candidate sequence changed")

    parent_claude = by_id[PARENT_CLAUDE]
    q = parent_claude.setdefault("qualifiers", {})
    q["claim"] = "Haskell says that as early as 1635 Claude found himself compelled to keep a record of all his paintings."
    q["qualification"] = "The date is reported by Haskell and qualifies Claude's recordkeeping; the adjoining copy sales are recorded separately and are not individually dated."
    q["relation_candidate"] = False
    q["relation_candidate_note"] = "This is the single-person recordkeeping claim. The distinct statement about copies sold as originals is recorded as a relation candidate below."
    q["related_statement_ids"] = [NEW_SALE_STATEMENT]
    parent_claude["original_quote"] = record_quote
    parent_claude["object_candidate_id"] = None

    parent_guidiccioni = by_id[PARENT_GUIDICCIONI]
    q = parent_guidiccioni.setdefault("qualifiers", {})
    parent_guidiccioni["object_candidate_id"] = DOUBTFUL_WORKS_GROUP
    q["claim"] = "Haskell suggests Guidiccioni may well have been tricked by dealers into acquiring unidentified works bearing doubtful attributions to Michelangelo, Raphael, and Perino del Vaga."
    q["qualification"] = "Preserves Haskell's explicit uncertainty; the individual works and dealers are unidentified, and the quoted attribution labels do not establish authorship."
    q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + [DOUBTFUL_WORKS_GROUP]))
    q["relation_candidate"] = True
    q["relation_candidate_note"] = "Source-attributed S2 relation candidate: Guidiccioni may have acquired a source-defined group of unidentified works with doubtful attributions. This neither identifies individual works nor confirms the attributions."

    note4_id = "st-chp5-p121-note4-citation"
    if note4_id not in by_id or "relation_candidate" in (by_id[note4_id].get("qualifiers") or {}):
        raise SystemExit("footnote 4 citation target missing or already classified")
    note4 = by_id[note4_id]
    note4["subject_candidate_id"] = None
    note4["object_candidate_id"] = None
    note4["qualifiers"]["relation_candidate"] = False
    note4["qualifiers"]["relation_candidate_note"] = "Bibliographic locator only; it is not an entity-to-entity or domain relation."

    sale_qualifiers = {
        "source_line_start": 10,
        "source_line_end": 10,
        "claim": "Haskell says that unidentified copies of Claude's works were being sold throughout Rome as originals.",
        "speaker": "Haskell",
        "text_layer": "authorial narration",
        "qualification": "No particular copy or seller is identified. The adjoining 'as early as 1635' dates Claude's recordkeeping and does not independently date each sale.",
        "mentioned_candidate_ids": [COPY_GROUP, "cand-0767", "cand-4490"],
        "pdf_physical_page": 2,
        "printed_page_locator": "p.121",
        "footnote_numbers": [1],
        "footnote_marker": 1,
        "footnote_segment": NOTE_SEGMENT_ID,
        "footnote_target_line": 126,
        "footnote_link_status": "linked",
        "footnote_links": [{
            "marker": 1,
            "note_line": 126,
            "note_segment": NOTE_SEGMENT_ID,
            "note_statement_ids": [NOTE1_STATEMENT],
            "status": "linked",
        }],
        "relation_candidate": True,
        "relation_candidate_note": "Source-attributed S2 relation candidate: a group of copies of Claude's paintings was sold in Rome as originals. The works and sellers are unidentified; no sale details are independently verified.",
        "related_statement_ids": [PARENT_CLAUDE],
    }
    new_sale_statement = {
        "statement_id": NEW_SALE_STATEMENT,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": COPY_GROUP,
        "object_candidate_id": "cand-4490",
        "predicate": "sold_as_originals_in",
        "qualifiers": sale_qualifiers,
        "original_quote": copy_quote,
        "origin": "book",
        "source_file": segment["source_file"],
    }
    statements.append(new_sale_statement)

    linked = note1["qualifiers"].setdefault("linked_body_statement_ids", [])
    linked.append(NEW_SALE_STATEMENT)

    new_candidates = [
        {
            "candidate_id": COPY_GROUP,
            "index_entry_id": "",
            "canonical_name": "Unidentified copies of Claude Lorrain's paintings reportedly sold as originals in Rome",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell reports that copies of Claude's paintings were sold throughout Rome as originals. No individual copy, seller, or sale record is identified here; the source does not independently verify the sales.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L10",
        },
        {
            "candidate_id": DOUBTFUL_WORKS_GROUP,
            "index_entry_id": "",
            "canonical_name": "Unidentified works with doubtful attributions to Michelangelo, Raphael, and Perino del Vaga",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell suggests Lelio Guidiccioni may well have been tricked into acquiring a group of works described through doubtful attribution labels. No title or individual work is identified, and the artists named in those labels are not treated as verified makers.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L10-11",
        },
    ]
    new_mentions = [
        {
            "mention_id": "m-chp5-p121-s2-copies-group",
            "segment_id": SEGMENT_ID,
            "candidate_id": COPY_GROUP,
            "surface_form": source_text[copy_start:copy_start + len(copy_surface)],
            "start_char": str(copy_start),
            "end_char": str(copy_start + len(copy_surface)),
            "note": "Source-defined group of copies; no individual work or seller is identified.",
        },
        {
            "mention_id": "m-chp5-p121-s2-doubtful-works",
            "segment_id": SEGMENT_ID,
            "candidate_id": DOUBTFUL_WORKS_GROUP,
            "surface_form": doubtful_surface,
            "start_char": str(doubtful_start),
            "end_char": str(doubtful_end),
            "note": "The quoted names are doubtful attribution labels for unidentified works, not work titles or confirmed authorship.",
        },
    ]
    for mention in new_mentions:
        if source_text[int(mention["start_char"]):int(mention["end_char"])] != mention["surface_form"]:
            raise SystemExit(f"mention span mismatch: {mention['mention_id']}")
    candidates.extend(new_candidates)
    mentions.extend(new_mentions)

    statement_output = ("\n".join(json.dumps(row, ensure_ascii=False) for row in statements) + "\n").encode("utf-8")
    candidate_output = render_csv(raw[CANDIDATES], candidate_fields, candidates)
    mention_output = render_csv(raw[MENTIONS], mention_fields, mentions)
    rendered = {STATEMENTS: statement_output, CANDIDATES: candidate_output, MENTIONS: mention_output}
    print("Chapter 5 section I p.121 preview:")
    print(f"classified false: {PARENT_CLAUDE} (person-level recordkeeping claim)")
    print(f"classified true: {PARENT_GUIDICCIONI} -> {DOUBTFUL_WORKS_GROUP} (qualified possible acquisition)")
    print(f"classified false: {note4_id} (citation locator)")
    print(f"new relation: {COPY_GROUP} -> cand-4490 (copies sold as originals in Rome)")
    for candidate in new_candidates:
        print(f"candidate: {candidate['candidate_id']} [{candidate['suggested_type']}, open] {candidate['canonical_name']}")
    for mention in new_mentions:
        print(f"mention: {mention['mention_id']} {mention['surface_form']!r} [{mention['start_char']},{mention['end_char']})")
    for path, output in rendered.items():
        print(f"{path.relative_to(ROOT)}: {sha(raw[path])} -> {sha(output)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return

    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    for path, output in rendered.items():
        temporary = path.with_name(path.name + ".tmp-s2-chp5-p121-mixed-claims")
        temporary.write_bytes(output)
        temporary.replace(path)
    print("mode=apply; backups=" + ", ".join(path.name for path in BACKUPS.values()))


if __name__ == "__main__":
    main()
