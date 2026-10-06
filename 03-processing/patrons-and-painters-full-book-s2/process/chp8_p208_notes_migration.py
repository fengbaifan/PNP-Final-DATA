"""Controlled S2 migration for p.208 notes 1-7 (composite lines L138-L144)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
BIBLIOGRAPHY_REL = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l126-157"
P208_BODY_ID = "chp-8:08_CHP-8_sec_i:l53-60"
EXPECTED_MAX_CANDIDATE = 7598
BACKUP_SUFFIX = ".bak-s2-chp8-p208-notes-20261001"

BODY_LINKS = {
    1: ["st-chp8-p208-roomer-chided-giordano-new-manner"],
    2: ["st-chp8-p208-roomer-acquired-codazzi-scenes"],
    3: ["st-chp8-p208-de-wael-dedicated-print-series"],
    4: [
        "st-chp8-p208-rubens-feast-influenced-artists-leaving-caravaggism",
        "st-chp8-p208-de-dominici-cavallino-affect",
        "st-chp8-p208-many-painters-studied-feast",
    ],
    5: ["st-chp8-p208-jan-flemish-origin"],
    6: ["st-chp8-p208-three-preti-paintings-brutal-realism"],
    7: ["st-chp8-p208-ferdinand-admired-giordano-works-unknown"],
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)

segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
candidate_ids = set(candidate_by_id)
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}

segment = segments.get(SEGMENT_ID)
if not segment or segment["source_file"] != SOURCE_REL:
    raise SystemExit(f"source segment metadata missing or changed: {SEGMENT_ID}")
if (int(segment["line_start"]), int(segment["line_end"])) != (126, 157):
    raise SystemExit(f"source segment line range changed: {SEGMENT_ID}")

source_path = ROOT / SOURCE_REL
if hashlib.sha256(source_path.read_bytes()).hexdigest() != segment["asset_sha256"]:
    raise SystemExit(f"source asset fingerprint changed: {SOURCE_REL}")
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[125:157]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit(f"source line-slice hash changed: {SEGMENT_ID}")
EXPECTED_NOTE_LINES = [
    "1 De Dominici, IV, p. 131: ‘gli fece una lunga esortazione a lasciar la nuova maniera, la quale dicea esser contra rune quelle usate da’ valentuomini . . .'.",
    "2 Ruffo, p. 176.",
    "3 Bartsch, V, pp. 5-10. There is a set tn the British Museum.",
    "4 For the influence of this picture see Bologna, p. 20.",
    "5 Vaes, 1925, p. 185.",
    "6 De Dominici, IV, pp. 48-9.",
    "7 ibid, p. 140.",
]
if segment_lines[12:19] != EXPECTED_NOTE_LINES:
    raise SystemExit("p.208 note source text changed; re-review before migration")

bibliography_text = (ROOT / BIBLIOGRAPHY_REL).read_text(encoding="utf-8-sig")
RUFFO_BIBLIOGRAPHY_ENTRY = "Ruffo, V.: ‘La galleria Ruffo nel secolo XVII in Messina’ in Bollettino d’Arte, X, 1916."
if RUFFO_BIBLIOGRAPHY_ENTRY not in bibliography_text:
    raise SystemExit("the cited Ruffo publication is no longer identifiable from the book bibliography")

note_coverage = coverage_by_id.get(SEGMENT_ID)
if not note_coverage or (
    note_coverage["disposition"],
    note_coverage["migration_status"],
    note_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L127-137"):
    raise SystemExit(f"unexpected composite-note coverage state: {note_coverage}")
body_coverage = coverage_by_id.get(P208_BODY_ID)
if not body_coverage or (
    body_coverage["disposition"],
    body_coverage["migration_status"],
    body_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L54-60"):
    raise SystemExit(f"unexpected p.208 body coverage state: {body_coverage}")

body_statement_by_id = {
    row["statement_id"]: row for row in statement_rows if row.get("segment_id") == P208_BODY_ID
}
expected_body_ids = {statement_id for ids in BODY_LINKS.values() for statement_id in ids}
if not expected_body_ids <= set(body_statement_by_id):
    raise SystemExit(f"one or more p.208 body statements are missing: {sorted(expected_body_ids - set(body_statement_by_id))}")
for marker, expected_ids in BODY_LINKS.items():
    found = {
        row["statement_id"]
        for row in body_statement_by_id.values()
        if row.get("qualifiers", {}).get("footnote_marker") == marker
    }
    if marker == 2:
        if found:
            raise SystemExit(f"p.208 note 2 marker was already assigned: {sorted(found)}")
    elif found != set(expected_ids):
        raise SystemExit(f"unexpected p.208 body-link set for note {marker}: {sorted(found)}")
if body_statement_by_id[BODY_LINKS[2][0]]["qualifiers"].get("source_line_start") != 55:
    raise SystemExit("the p.208 note 2 target no longer points to the Codazzi sentence")

current_max = max(
    int(row["candidate_id"].split("-")[1])
    for row in candidate_rows
    if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()
)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")

EXISTING = {
    "de_dominici_iv": "cand-4835",
    "ruffo_1916": "cand-6454",
    "bartsch_work": "cand-5609",
    "british_museum": "cand-5986",
    "bologna_work": "cand-7348",
    "vaes_1925": "cand-7584",
    "de_wael_prints": "cand-7456",
}
if not set(EXISTING.values()) <= candidate_ids:
    raise SystemExit("one or more planned existing candidate IDs are absent")
if candidate_by_id[EXISTING["ruffo_1916"]]["canonical_name"] != "V. Ruffo, 1916, p. 290, cited publication (title unspecified)":
    raise SystemExit("the existing Ruffo citation candidate changed; review before reusing it")
if candidate_by_id[EXISTING["de_dominici_iv"]]["suggested_type"] != "archive":
    raise SystemExit("De Dominici IV candidate type changed")
if candidate_by_id[EXISTING["bartsch_work"]]["canonical_name"] != "Le Peintre Graveur (Adam Bartsch, Leipzig, 1854)":
    raise SystemExit("Bartsch work candidate changed")
if candidate_by_id[EXISTING["bologna_work"]]["canonical_name"] != "Ferdinando Bologna, Francesco Solimena (Napoli, 1958)":
    raise SystemExit("Bologna work candidate changed")


def offset_for_line(source_line: int) -> int:
    return sum(len(line) + 1 for line in segment_lines[: source_line - 126])


def make_mention(mention_id, source_line, surface, candidate_id, note, occurrence=0):
    source_text = segment_lines[source_line - 126]
    starts = []
    pos = 0
    while True:
        pos = source_text.find(surface, pos)
        if pos < 0:
            break
        starts.append(pos)
        pos += max(1, len(surface))
    if occurrence >= len(starts):
        raise SystemExit(f"mention surface occurrence is absent on L{source_line}: {surface!r} #{occurrence}")
    start = offset_for_line(source_line) + starts[occurrence]
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


new_mentions = [
    make_mention("m-chp8-p208-note-001", 138, "De Dominici", EXISTING["de_dominici_iv"], "In-book citation to volume IV, p.131; cited page not independently read."),
    make_mention("m-chp8-p208-note-002", 139, "Ruffo", EXISTING["ruffo_1916"], "Short citation mapped to the V. Ruffo 1916 bibliography entry; p.176 not independently read."),
    make_mention("m-chp8-p208-note-003", 140, "Bartsch", EXISTING["bartsch_work"], "Volume V, pp.5-10 cited for the de Wael print series; cited pages not independently read."),
    make_mention("m-chp8-p208-note-004", 140, "British Museum", EXISTING["british_museum"], "Repository named for a set in the context of de Wael's print series; no catalogue consulted."),
    make_mention("m-chp8-p208-note-005", 141, "Bologna", EXISTING["bologna_work"], "Short citation to the book-bibliography entry for Francesco Solimena; p.20 not independently read."),
    make_mention("m-chp8-p208-note-006", 142, "Vaes", EXISTING["vaes_1925"], "Short author-year citation to the 1925 Vaes article identified in the book bibliography; p.185 not independently read."),
    make_mention("m-chp8-p208-note-007", 143, "De Dominici", EXISTING["de_dominici_iv"], "In-book citation to volume IV, pp.48-49; cited pages not independently read."),
    make_mention("m-chp8-p208-note-008", 144, "ibid", EXISTING["de_dominici_iv"], "Anaphoric citation to De Dominici, volume IV, from note 6; p.140 not independently read."),
]


def make_statement(statement_id, source_line, quote, subject, object_id, predicate, claim, qualification,
                   mentioned, marker, linked_body_ids, text_layer="bibliographic pointer", extra=None):
    qualifiers = {
        "source_line_start": source_line,
        "source_line_end": source_line,
        "printed_page": 208,
        "pdf_physical_page": 6,
        "claim": claim,
        "speaker": "Haskell footnote",
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "footnote_marker": marker,
        "linked_body_statement_ids": linked_body_ids,
        "footnote_segment": SEGMENT_ID,
        "footnote_body_link_status": "linked",
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


D = EXISTING["de_dominici_iv"]
RUFFO = EXISTING["ruffo_1916"]
BARTSCH = EXISTING["bartsch_work"]
BM = EXISTING["british_museum"]
BOLOGNA = EXISTING["bologna_work"]
VAES = EXISTING["vaes_1925"]
PRINTS = EXISTING["de_wael_prints"]

new_statements = [
    make_statement(
        "st-chp8-p208-n1-cite-de-dominici", 138,
        "De Dominici, IV, p. 131: ‘gli fece una lunga esortazione a lasciar la nuova maniera, la quale dicea esser contra rune quelle usate da’ valentuomini . . .'.",
        None, D, "footnote_citation",
        "Haskell cites De Dominici, volume IV, p.131, and reproduces an Italian passage in the note attached to his report that Roomer rebuked Giordano for his new manner.",
        "Citation and quotation as printed in Haskell's note; the cited page was not consulted and the Italian passage was not independently translated or verified.",
        [D, "cand-2223", "cand-1172", "cand-7451"], 1, BODY_LINKS[1],
        text_layer="citation with reproduced quotation",
        extra={"citations": [{"source_candidate_id": D, "volume": "IV", "page": "131"}],
               "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 138, "ocr": "rune", "print": "tutte", "basis": "CHP-8.pdf physical page 6."}]},
    ),
    make_statement(
        "st-chp8-p208-n2-cite-ruffo", 139, "Ruffo, p. 176.", None, RUFFO, "footnote_citation",
        "Haskell cites p.176 of the V. Ruffo publication identified by the book bibliography for the preceding Codazzi acquisition passage.",
        "The book bibliography identifies the 1916 La galleria Ruffo article; the cited p.176 was not independently read.",
        [RUFFO, "cand-2223", "cand-0794", "cand-7447"], 2, BODY_LINKS[2],
        extra={"citations": [{"source_candidate_id": RUFFO, "page": "176"}]},
    ),
    make_statement(
        "st-chp8-p208-n3-cite-bartsch", 140, "Bartsch, V, pp. 5-10.", None, BARTSCH, "footnote_citation",
        "Haskell cites Adam Bartsch, volume V, pp.5-10, in the note attached to Jean-Baptiste de Wael's print series.",
        "Bibliographic pointer only; Bartsch's cited pages were not independently read.",
        [BARTSCH, PRINTS], 3, BODY_LINKS[3],
        extra={"citations": [{"source_candidate_id": BARTSCH, "volume": "V", "page_start": "5", "page_end": "10"}]},
    ),
    make_statement(
        "st-chp8-p208-n3-set-reported-at-british-museum", 140, "There is a set tn the British Museum.",
        PRINTS, BM, "de_wael_print_set_reported_at_british_museum",
        "Haskell adds that a set is in the British Museum, in the note attached to the de Wael print series.",
        "The anaphoric 'a set' is resolved from the immediately preceding note context as the de Wael print series; no British Museum catalogue record was consulted.",
        [PRINTS, BM, BARTSCH], 3, BODY_LINKS[3], text_layer="substantive footnote claim",
        extra={"relation_candidate": True, "anaphoric_reference": "a set", "reported_repository_candidate_id": BM,
               "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 140, "ocr": "tn", "print": "There", "basis": "CHP-8.pdf physical page 6."}]},
    ),
    make_statement(
        "st-chp8-p208-n4-cite-bologna", 141,
        "For the influence of this picture see Bologna, p. 20.", None, BOLOGNA, "footnote_citation",
        "Haskell points to Bologna, p.20, for the influence discussion of Rubens's Feast of Herod in the preceding passage.",
        "Citation locator only; the cited page was not independently read. 'This picture' refers to Rubens's Feast of Herod.",
        [BOLOGNA, "cand-4092", "cand-7460", "cand-0613"], 4, BODY_LINKS[4],
        extra={"citations": [{"source_candidate_id": BOLOGNA, "page": "20"}], "resolves_anaphora_to": "Rubens's Feast of Herod"},
    ),
    make_statement(
        "st-chp8-p208-n5-cite-vaes", 142, "Vaes, 1925, p. 185.", None, VAES, "footnote_citation",
        "Haskell cites Vaes (1925), p.185, in the note attached to his statement about Jan van den Einden's Flemish origins and seemingly lowly origins.",
        "The book bibliography identifies the 1925 Vaes article; the cited p.185 was not independently read.",
        [VAES, "cand-0915"], 5, BODY_LINKS[5],
        extra={"citations": [{"source_candidate_id": VAES, "year": "1925", "page": "185"}]},
    ),
    make_statement(
        "st-chp8-p208-n6-cite-de-dominici", 143, "De Dominici, IV, pp. 48-9.", None, D, "footnote_citation",
        "Haskell cites De Dominici, volume IV, pp.48-49, in the note attached to his inference about the three Preti paintings and brutal realism.",
        "Citation locator only; the cited pages were not independently read.",
        [D, "cand-0914", "cand-7448"], 6, BODY_LINKS[6],
        extra={"citations": [{"source_candidate_id": D, "volume": "IV", "page_start": "48", "page_end": "49"}]},
    ),
    make_statement(
        "st-chp8-p208-n7-cite-de-dominici-ibid", 144, "ibid, p. 140.", None, D, "footnote_citation",
        "Haskell's note 7 uses ibid. for De Dominici, volume IV, p.140, continuing note 6's citation.",
        "Anaphoric citation resolves to De Dominici, volume IV; the cited page was not independently read.",
        [D, "cand-0914", "cand-1172"], 7, BODY_LINKS[7],
        extra={"citations": [{"source_candidate_id": D, "volume": "IV", "page": "140"}],
               "resolves_ibid_to_statement_id": "st-chp8-p208-n6-cite-de-dominici",
               "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 144, "ocr": "ibid,", "print": "ibid.,", "basis": "CHP-8.pdf physical page 6."}]},
    ),
]

planned_mention_ids = {row["mention_id"] for row in new_mentions}
planned_statement_ids = {row["statement_id"] for row in new_statements}
if len(planned_mention_ids) != len(new_mentions) or mention_ids & planned_mention_ids:
    raise SystemExit("planned mention IDs collide")
if len(planned_statement_ids) != len(new_statements) or statement_ids & planned_statement_ids:
    raise SystemExit("planned statement IDs collide")
all_candidate_ids = candidate_ids
for row in new_mentions:
    if row["candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"mention has unknown candidate: {row['mention_id']} -> {row['candidate_id']}")
for row in new_statements:
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in all_candidate_ids:
            raise SystemExit(f"statement has unknown candidate: {row['statement_id']} -> {candidate_id}")
    if not set(row["qualifiers"]["linked_body_statement_ids"]) <= set(body_statement_by_id):
        raise SystemExit(f"statement links to missing body statement: {row['statement_id']}")

candidate_new = [dict(row) for row in candidate_rows]
for row in candidate_new:
    if row["candidate_id"] == RUFFO:
        row["canonical_name"] = "V. Ruffo, ‘La galleria Ruffo nel secolo XVII in Messina’, Bollettino d’Arte, X (1916)"
        row["detail"] = (
            "The book bibliography identifies the 1916 article. Reused for Haskell's p.160 note 2 citation to p.290 "
            "and p.208 note 2 citation to p.176; neither cited page was independently read."
        )
if candidate_new == candidate_rows:
    raise SystemExit("expected Ruffo citation candidate update was not applied")

statement_new = [dict(row) for row in statement_rows]
for row in statement_new:
    if row["statement_id"] == BODY_LINKS[2][0]:
        row["qualifiers"] = dict(row["qualifiers"])
        row["qualifiers"]["footnote_marker"] = 2

mention_new = mention_rows + new_mentions
statement_new.extend(new_statements)
coverage_new = []
for row in coverage_rows:
    copied = dict(row)
    if copied["segment_id"] == SEGMENT_ID:
        copied["source_line_ranges"] = "L127-144"
        copied["note"] = (
            "P.204 notes 1-3 (L127-129), p.205 notes 1-4 (L130-133), p.206 notes 1-2 (L134-135), "
            "p.207 notes 1-2 (L136-137), and p.208 notes 1-7 (L138-144) read against CHP-8.pdf physical pp.2-6 and migrated. "
            "P.208 note 3 adds Haskell's report that a set of de Wael prints is in the British Museum; no catalogue was consulted. "
            "Note 4's 'this picture' resolves to Rubens's Feast of Herod. Note 7 ibid. resolves to De Dominici volume IV. "
            "The OCR corrections rune -> tutte, tn -> There, and ibid, -> ibid., are recorded in S2 only. "
            "L145-L157 remain pending; compare L146-L148 with the p.211 visual transcription before reusing any material."
        )
    elif copied["segment_id"] == P208_BODY_ID:
        copied["migration_status"] = "complete"
        copied["note"] = (
            "P.208 body segment read against CHP-8.pdf physical p.6. Notes 1-7 in composite lines L138-L144 migrated and linked. "
            "The note 2 superscript after Codazzi was present in print but omitted from the existing statement metadata; marker 2 has been added. "
            "S0 remains unchanged."
        )
    coverage_new.append(copied)


def preview():
    print(f"validated segment: {SEGMENT_ID} lines 126-157")
    print("processed source range: L138-144 (p.208 notes 1-7)")
    print("new candidates: 0; existing Ruffo publication candidate enriched from book bibliography")
    print(f"new mentions: {len(new_mentions)}")
    print(f"new statements: {len(new_statements)} (7 citation statements; 1 reported repository claim)")
    print("p.208 body coverage: reviewed/complete; missing footnote marker 2 repaired")
    print("composite note coverage: reviewed/partial, L127-144; L145-157 pending")


def apply():
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    write_csv_atomic(candidate_path, candidate_fields, candidate_new)
    write_csv_atomic(mention_path, mention_fields, mention_new)
    write_jsonl_atomic(statement_path, statement_new)
    write_csv_atomic(coverage_path, coverage_fields, coverage_new)
    print("APPLIED; recovery backups retained pending audits:")
    for backup in backups:
        print(backup.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks pass")
    args = parser.parse_args()
    preview()
    if args.apply:
        apply()
    else:
        print("DRY RUN: no files written")


if __name__ == "__main__":
    main()
