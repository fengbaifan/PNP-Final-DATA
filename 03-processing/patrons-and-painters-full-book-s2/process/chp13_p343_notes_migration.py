"""Controlled S2 migration for printed p.343 notes; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
BODY = "chp-13:13_CHP-13_intro:l107-114"
PREVIOUS_BODY = "chp-13:13_CHP-13_intro:l98-105"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p343-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.343 note migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_fragments = {
    235: "Lorenzetti, 1917, p. 122.",
    236: "In the preface to Varie Pitture a Fresco",
    237: "Among these were Mariette, Crozat, Vleughels",
    238: "Zanetti may well have published these as early as 1743.",
}
for line_number, fragment in expected_fragments.items():
    if fragment not in source_lines[line_number - 1]:
        raise SystemExit(f"source line L{line_number} changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}

table_state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if table_state != (10200, 10213, 22110, 9861):
    raise SystemExit(f"unexpected table pre-state: {table_state}")
if BODY not in coverage or PREVIOUS_BODY not in coverage or NOTES not in coverage:
    raise SystemExit("p.342/p.343 body or consolidated notes coverage row missing")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.343 body is not reviewed/partial with printed notes pending")
if coverage[NOTES]["source_line_ranges"] != "L180-234":
    raise SystemExit("consolidated-notes cursor changed")
if any(row["segment_id"] == NOTES and row["mention_id"].startswith("m-s2-ch13-p343-notes-") for row in mentions):
    raise SystemExit("p.343 note mentions already exist")
if any(row["segment_id"] == NOTES and row["statement_id"].startswith("st-chp13-p343-notes-") for row in statements):
    raise SystemExit("p.343 note statements already exist")

body_note_targets = {
    "1": ["st-chp13-p343-zanetti_engraved_castiglione_drawings_1759"],
    "2": [
        "st-chp13-p343-haskell_places_zanetti_in_first_print_group",
        "st-chp13-p343-younger_zanetti_on_lively_print_preferences",
        "st-chp13-p343-younger_zanetti_on_general_public_print_preferences",
    ],
    "3": [
        "st-chp13-p343-zanetti_dedicated_individual_sheets_to_friends",
        "st-chp13-p343-zanetti_destroyed_plates_and_dedicated_woodcut_set",
    ],
    "4": ["st-chp13-p343-zanetti_first_to_publish_tiepolo_etchings"],
}
for marker, ids in body_note_targets.items():
    for statement_id in ids:
        if statement_id not in statement_by_id:
            raise SystemExit(f"p.343 footnote {marker} target missing: {statement_id}")
        refs = statement_by_id[statement_id].get("qualifiers", {}).get("footnote_refs", [])
        if not any(
            ref.get("footnote_marker") == marker
            and ref.get("footnote_printed_page") == 343
            and ref.get("footnote_text_pending")
            for ref in refs
        ):
            raise SystemExit(f"p.343 footnote {marker} is not pending on {statement_id}")

cross_page_note6_targets = [
    "st-chp13-p343-zanetti_disregarded_multiple_examples",
    "st-chp13-p343-zanetti_exchanged_spares_for_missing_print",
    "st-chp13-p343-zanetti_never_seen_giulio_romano_prints",
    "st-chp13-p343-zanetti_preferred_single_fine_copy",
]
for statement_id in cross_page_note6_targets:
    if statement_id not in statement_by_id:
        raise SystemExit(f"p.342 note 6 cross-page target missing: {statement_id}")
    refs = statement_by_id[statement_id].get("qualifiers", {}).get("footnote_refs", [])
    if not any(
        ref.get("footnote_marker") == "6"
        and ref.get("footnote_printed_page") == 342
        and ref.get("footnote_text_pending")
        for ref in refs
    ):
        raise SystemExit(f"p.342 note 6 is not pending on cross-page p.343 statement {statement_id}")
note6_id = "st-chp13-p342-notes-note6-letter-to-gori-locator"
if note6_id not in statement_by_id:
    raise SystemExit("migrated p.342 note 6 statement missing")

wrong_note4_target = "st-chp13-p343-zanetti_passion_for_antiquity_and_tiepolo_etchings"
wrong_q = statement_by_id[wrong_note4_target].get("qualifiers", {})
if not any(r.get("footnote_marker") == "4" and r.get("footnote_printed_page") == 343 for r in wrong_q.get("footnote_refs", [])):
    raise SystemExit("expected p.343 note 4 overlink was not found for correction")

new_candidate_ids = {"cand-10214"}
if new_candidate_ids & set(candidate_by_id):
    raise SystemExit(f"candidate IDs already exist: {sorted(new_candidate_ids & set(candidate_by_id))}")
new_candidates = []


def add_candidate(candidate_id, name, kind, detail, line_number):
    if any(row["canonical_name"].casefold() == name.casefold() for row in candidates):
        raise SystemExit(f"candidate name already exists: {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
    })
    new_candidates.append(row)


add_candidate(
    "cand-10214",
    "Richard Mead (physician named among Zanetti's dedicatees; identity pending)",
    "person",
    "P.343 note 3 names Dr Richard Mead among recipients of Zanetti's dedicated sheets. The note supplies no further identifying details; compare with any later or indexed Mead reference at S3.",
    237,
)

candidate_by_id["cand-10192"]["detail"] += (
    " P.343 notes 1 and 4 also cite pages 122 and 55 respectively; note 4 cautiously reports that Zanetti may have published Tiepolo etchings as early as 1743."
)
candidate_by_id["cand-10117"]["detail"] = (
    "Publication cited in p.343 note 2 as the preface source for the younger Zanetti passage. "
    "The printed title is Varie Pitture a Fresco de' Principali Maestri Veneziani (1760); "
    "the book was not independently consulted."
)

all_candidate_ids = set(candidate_by_id) | new_candidate_ids
notes_text = "\n".join(source_lines[178:251])
line_offsets = {}
offset = 0
for line_number in range(179, 252):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1
new_mentions = []


def add_mention(line_number, surface, candidate_id, note="", occurrence=0):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"candidate FK missing for mention {surface!r}: {candidate_id}")
    line_text = source_lines[line_number - 1]
    positions, cursor = [], 0
    while True:
        at = line_text.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention text missing at L{line_number}: {surface!r}")
    start = line_offsets[line_number] + positions[occurrence]
    end = start + len(surface)
    if notes_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    key = (NOTES, candidate_id, str(start), str(end))
    if key in {
        (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
        for row in mentions + new_mentions
    }:
        raise SystemExit(f"duplicate mention at L{line_number}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p343-notes-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": note,
    })
    new_mentions.append(row)


mention_specs = [
    (235, "Lorenzetti, 1917, p. 122", "cand-10192", "Cited page not consulted."),
    (235, "Lorenzetti", "cand-9947", "Reuse surname-only cited author candidate."),
    (236, "Varie Pitture a Fresco de'Principali Maestri Veneziani, 1760", "cand-10117", "Printed title as transcribed; S2 notes the missing space after de'."),
    (237, "Mariette", "cand-1547"),
    (237, "Crozat", "cand-0894"),
    (237, "Vleughels", "cand-2789"),
    (237, "the Duke of Devonshire", "cand-0918"),
    (237, "Sir Andrew Fountaine", "cand-1060"),
    (237, "Dr Richard Mead", "cand-10214", "New person candidate; identity pending."),
    (237, "Joseph Smith", "cand-2442", "Reuse the indexed Smith candidate; specific identity alignment remains for S3."),
    (237, "Rosalba Carriera", "cand-0581"),
    (237, "Zaccaria Sagredo", "cand-2329"),
    (238, "Lorenzetti, 1917, p. 55", "cand-10192", "Cited page not consulted."),
    (238, "Lorenzetti", "cand-9947", "Reuse surname-only cited author candidate."),
    (238, "1743", "cand-10103", "The date remains Haskell's qualified possibility, not a verified publication year."),
]
for spec in mention_specs:
    add_mention(*spec)

ocr_corrections = [{
    "source_line": 236,
    "ocr": "de'Principali",
    "print": "de’ Principali",
    "basis": "CHP-13.pdf physical page 12.",
}]

new_statement_specs = [
    {
        "id": "st-chp13-p343-notes-note1-lorenzetti-page122",
        "marker": "1", "line": 235,
        "subject": "cand-10192", "object": "cand-10098",
        "predicate": "lorenzetti_1917_page_122_cited_for_1759_castiglione_prints",
        "claim": "P.343 note 1 cites Lorenzetti, 1917, page 122, for the preceding account of Zanetti's 1759 prints after Castiglione drawings.",
        "qualification": "This is a book-internal citation locator; Lorenzetti's page was not consulted.",
        "mentioned": ["cand-10192", "cand-9947", "cand-10098"],
        "citations": [{"source_candidate_id": "cand-10192", "author_candidate_id": "cand-9947", "year": "1917", "page": "122"}],
        "linked": body_note_targets["1"],
    },
    {
        "id": "st-chp13-p343-notes-note2-varie-pitture-preface-source",
        "marker": "2", "line": 236,
        "subject": "cand-2859", "object": "cand-10117",
        "predicate": "younger_zanetti_print_preferences_cited_to_1760_preface",
        "claim": "P.343 note 2 locates the younger Zanetti passage in the preface to Varie Pitture a Fresco de' Principali Maestri Veneziani (1760).",
        "qualification": "The title is transcribed from the print; the missing space after de' is recorded as an S2 correction only. The book was not consulted.",
        "mentioned": ["cand-2859", "cand-10117"],
        "citations": [{"source_candidate_id": "cand-10117", "publication_year": 1760, "locator": "preface"}],
        "linked": body_note_targets["2"], "ocr_corrections": ocr_corrections,
    },
    {
        "id": "st-chp13-p343-notes-note3-named-dedicatees",
        "marker": "3", "line": 237,
        "subject": "cand-2838", "object": "cand-10101",
        "predicate": "footnote_names_examples_of_people_receiving_dedicated_sheets",
        "claim": "Haskell names Mariette, Crozat, Vleughels, the Duke of Devonshire, Sir Andrew Fountaine, Dr Richard Mead, Joseph Smith, Rosalba Carriera, and Zaccaria Sagredo among the recipients of Zanetti's dedicated sheets.",
        "qualification": "The note says 'among these'; it does not identify which individual sheet went to each person. Names and titles are preserved as printed; their identities are for S3 alignment.",
        "mentioned": ["cand-2838", "cand-10101", "cand-1547", "cand-0894", "cand-2789", "cand-0918", "cand-1060", "cand-10214", "cand-2442", "cand-0581", "cand-2329"],
        "citations": [{"source_candidate_id": "cand-10101", "named_recipients": ["cand-1547", "cand-0894", "cand-2789", "cand-0918", "cand-1060", "cand-10214", "cand-2442", "cand-0581", "cand-2329"]}],
        "linked": body_note_targets["3"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p343-notes-note4-lorenzetti-possible-1743-date",
        "marker": "4", "line": 238,
        "subject": "cand-10192", "object": "cand-10103",
        "predicate": "lorenzetti_1917_page55_suggests_possible_1743_publication",
        "claim": "Citing Lorenzetti, 1917, page 55, Haskell says Zanetti may well have published the Tiepolo etchings as early as 1743.",
        "qualification": "Preserve 'may well' and 'as early as': 1743 is a qualified possibility attributed to the cited source, not a verified publication date. Lorenzetti's page was not consulted.",
        "mentioned": ["cand-10192", "cand-9947", "cand-10103"],
        "citations": [{"source_candidate_id": "cand-10192", "author_candidate_id": "cand-9947", "year": "1917", "page": "55"}],
        "linked": body_note_targets["4"],
    },
]

new_statements = []
note_statement_ids_by_marker = {str(n): [] for n in range(1, 5)}
for spec in new_statement_specs:
    for candidate_id in spec["mentioned"]:
        if candidate_id not in all_candidate_ids:
            raise SystemExit(f"statement candidate missing: {spec['id']} -> {candidate_id}")
    qualifiers = {
        "source_line_start": spec["line"],
        "source_line_end": spec["line"],
        "printed_page": 343,
        "pdf_physical_page": 12,
        "claim": spec["claim"],
        "speaker": "Haskell, printed footnote",
        "text_layer": "secondary source note and citation",
        "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"],
        "footnote_marker": spec["marker"],
        "footnote_printed_page": 343,
        "linked_body_statement_ids": spec["linked"],
        "citations": spec["citations"],
    }
    if spec.get("relation_candidate"):
        qualifiers["relation_candidate"] = True
    if spec.get("ocr_corrections"):
        qualifiers["ocr_corrections"] = spec["ocr_corrections"]
    new_statements.append({
        "statement_id": spec["id"],
        "segment_id": NOTES,
        "subject_candidate_id": spec["subject"],
        "object_candidate_id": spec["object"],
        "predicate": spec["predicate"],
        "qualifiers": qualifiers,
        "original_quote": source_lines[spec["line"] - 1],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })
    note_statement_ids_by_marker[spec["marker"]].append(spec["id"])


def link_body_statement(statement_id, marker, printed_page, note_ids):
    qualifiers = statement_by_id[statement_id].setdefault("qualifiers", {})
    refs = qualifiers.setdefault("footnote_refs", [])
    matching = [
        ref for ref in refs
        if ref.get("footnote_marker") == marker and ref.get("footnote_printed_page") == printed_page
    ]
    if not matching:
        raise SystemExit(f"footnote {marker} p.{printed_page} missing from {statement_id}")
    if not any(ref.get("footnote_text_pending") for ref in matching):
        raise SystemExit(f"footnote {marker} p.{printed_page} is already linked on {statement_id}")
    for ref in matching:
        ref["footnote_text_pending"] = False
        ref["footnote_body_link_status"] = "linked"
        ref["footnote_note_statement_ids"] = note_ids
    qualifiers["footnote_note_statement_ids"] = sorted(set(qualifiers.get("footnote_note_statement_ids", [])) | set(note_ids))
    qualifiers["footnote_text_pending"] = False
    qualifiers["footnote_body_link_status"] = "linked"


for marker, body_ids in body_note_targets.items():
    note_ids = note_statement_ids_by_marker[marker]
    if not note_ids:
        raise SystemExit(f"no note statements for p.343 marker {marker}")
    for statement_id in body_ids:
        link_body_statement(statement_id, marker, 343, note_ids)

# P.342 note 6 cites the letter for a quotation that continues into p.343.
for statement_id in cross_page_note6_targets:
    link_body_statement(statement_id, "6", 342, [note6_id])
note6_qualifiers = statement_by_id[note6_id].setdefault("qualifiers", {})
note6_qualifiers["linked_body_statement_ids"] = sorted(
    set(note6_qualifiers.get("linked_body_statement_ids", [])) | set(cross_page_note6_targets)
)

# The p.343 note 4 is specifically attached to the publication-date claim, not the preceding
# broad statement about Zanetti's taste for antiquity and Tiepolo's etchings.
wrong_q["footnote_refs"] = [
    ref for ref in wrong_q.get("footnote_refs", [])
    if not (ref.get("footnote_marker") == "4" and ref.get("footnote_printed_page") == 343)
]
if not wrong_q["footnote_refs"]:
    wrong_q.pop("footnote_refs", None)
for key in ("footnote_marker", "footnote_printed_page", "footnote_text_pending", "footnote_body_link_status", "footnote_segment", "footnote_line_range", "footnote_note_statement_ids"):
    wrong_q.pop(key, None)

for marker, body_ids in body_note_targets.items():
    for statement_id in body_ids:
        refs = statement_by_id[statement_id].get("qualifiers", {}).get("footnote_refs", [])
        if any(ref.get("footnote_marker") == marker and ref.get("footnote_text_pending") for ref in refs):
            raise SystemExit(f"p.343 footnote {marker} remains pending on {statement_id}")
for statement_id in cross_page_note6_targets:
    refs = statement_by_id[statement_id].get("qualifiers", {}).get("footnote_refs", [])
    if any(ref.get("footnote_marker") == "6" and ref.get("footnote_printed_page") == 342 and ref.get("footnote_text_pending") for ref in refs):
        raise SystemExit(f"p.342 note 6 remains pending on p.343 continuation {statement_id}")

for row in new_statements:
    if row["original_quote"] not in notes_text:
        raise SystemExit(f"statement quote not found in source segment: {row['statement_id']}")
for row in new_mentions:
    if notes_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"final mention span failed: {row['mention_id']}")

coverage[NOTES]["source_line_ranges"] = "L180-238"
coverage[NOTES]["note"] = (
    "Notes L180-234 (pp.332-342) and p.343 notes 1-4 at L235-238 are migrated and linked. "
    "The p.342 note 6 letter locator is also linked across the p.342-343 continuous quotation. "
    "Mirrored caption lines L247-248, p.344 notes L239-246, and p.345 notes L249-251 remain; the composite segment remains partial."
)
coverage[BODY]["migration_status"] = "complete"
coverage[BODY]["source_line_ranges"] = "L107-114"
coverage[BODY]["note"] = (
    "Printed p.343 body and notes 1-4 were checked against CHP-13.pdf physical page 12 and linked to their marked claims. "
    "The p.342 note 6 locator is linked across the continuous p.342-343 Zanetti quotation. "
    "The final 'In it Zanetti subordinated' clause continues at p.344 L116. OCR corrections are recorded in S2 only; cited pages were not consulted."
)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = [statement_by_id.get(row["statement_id"], row) for row in statements] + new_statements
if len({r["candidate_id"] for r in candidate_out}) != len(candidate_out):
    raise SystemExit("candidate IDs are not unique after migration")
if len({r["mention_id"] for r in mention_out}) != len(mention_out):
    raise SystemExit("mention IDs are not unique after migration")
if len({r["statement_id"] for r in statement_out}) != len(statement_out):
    raise SystemExit("statement IDs are not unique after migration")

print(f"candidate rows: {len(candidates)} -> {len(candidate_out)} (+{len(new_candidates)})")
print(f"mention rows: {len(mentions)} -> {len(mention_out)} (+{len(new_mentions)})")
print(f"statement rows: {len(statements)} -> {len(statement_out)} (+{len(new_statements)})")
print("coverage: p.343 body partial -> complete; consolidated notes advance L180-234 -> L180-238 and remain partial")
print("p.343 notes 1-4 linked; p.342 note 6 is linked to the p.343 continuation of its quotation")
print("p.343 note 4 overlink removed from the broad taste statement; 1743 remains a qualified possibility")
print("print correction recorded only in S2: de'Principali -> de’ Principali")
print("cited book and Lorenzetti pages were not independently consulted")
if not args.apply:
    print("dry-run only; review this delta before rerunning with --apply")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
if any(path.exists() for path in backups):
    raise SystemExit("one or more migration backup paths already exist")
for original, backup in zip(targets, backups):
    shutil.copy2(original, backup)
write_csv(candidate_path, candidate_fields, candidate_out)
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statement_out)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied with four table backups:")
for path in backups:
    print(f"  {path.relative_to(ROOT)}")
