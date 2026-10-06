"""Controlled S2 migration for p.313-314 notes; dry-run by default."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"
P313 = "chp-10:10_CHP-10_sec_ii:l72-81"
P314 = "chp-10:10_CHP-10_sec_ii:l83-93"
P313_PREV = "chp-10:10_CHP-10_sec_ii:l17-32"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BACKUP_SUFFIX = ".bak-s2-chp10-p313-314-notes-20261003"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write p.313-314 notes and links")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_note_starts = {
    284: "1 Apart from those reproduced by Morassi",
    285: "2 A number of these have turned up",
    286: "3 See the published inventory",
    287: "4 See Chapter 10.",
    288: "1 A number of pictures recommended",
    289: "2 See White and Sewter",
    290: "3 See the published inventory",
    291: "4 There are ten pictures by Marieschi",
}
for line_number, prefix in expected_note_starts.items():
    if not source_lines[line_number - 1].startswith(prefix):
        raise SystemExit(f"canonical note boundary changed at L{line_number}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
candidate_ids = set(candidate_by_id)
mention_ids = {row["mention_id"] for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
statement_ids = set(statement_by_id)
coverage = {row["segment_id"]: row for row in coverage_rows}

state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (9877, 9890, 20978, 9326):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment in (P313, P314, P313_PREV, NOTES):
    if segment not in coverage:
        raise SystemExit(f"required coverage row missing: {segment}")
for segment in (P313, P314, NOTES):
    if (coverage[segment]["disposition"], coverage[segment]["migration_status"]) != ("reviewed", "partial"):
        raise SystemExit(f"expected reviewed/partial coverage for {segment}")
for prefix in ("st-chp10-p313-n0", "st-chp10-p314-n0"):
    if any(sid.startswith(prefix) for sid in statement_ids):
        raise SystemExit(f"note statements already exist for {prefix}")
if any(row["mention_id"].startswith("m-s2-ch10-p313-314-note-") for row in mentions):
    raise SystemExit("p.313-314 note mentions already exist")
for sid in (
    "st-chp10-p313-surviving-guardi-portraits-quality",
    "st-chp10-p313-guardi-turkish-scenes-after-van-mour",
    "st-chp10-p314-piazzetta-chief-agent-for-schulenburg",
    "st-chp10-p314-social-satire-interpretation-qualified",
    "st-chp10-p314-schulenburg-owned-seven-ceruti-pictures",
    "st-chp10-p314-schulenburg-owned-views-and-landscapes-by-six-artists",
):
    if sid not in statement_by_id:
        raise SystemExit(f"body statement missing: {sid}")
if candidate_by_id.get("cand-9884", {}).get("canonical_name") != "Inventaire de la Galerie de feu Mgr. le Feldtnarechal Comte de Schulenburg (published inventory, n.d.)":
    raise SystemExit("expected OCR-form inventory candidate cand-9884 not found")

# S2 in the p.313 body had mapped plural picture objects to repeated Guardi person candidates.
# Re-type those referents as work groups; cross-object identity remains for S3.
new_candidates = []


def add_candidate(cid, name, kind, detail, line, segment=NOTES):
    if cid in candidate_ids or any(row["candidate_id"] == cid for row in new_candidates):
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment}#L{line}",
    })
    new_candidates.append(row)


add_candidate("cand-9891", "Pignatti (author cited at p.313 note 1; identity unresolved)", "person", "Surname-only author reference; no identity beyond Haskell's citation is assumed.", 284)
add_candidate("cand-9892", "Pignatti, 1960, page 105 (citation locator)", "archive", "Cited for a Schulenburg portrait attributed to Gian Antonio Guardi at Museo Correr. The cited page was not independently consulted.", 284)
add_candidate("cand-9893", "Watson, 1960, pages 3-13 (citation locator)", "archive", "Cited for the reported attribution of a Guardi picture series. The cited pages were not independently consulted.", 285)
add_candidate("cand-9894", "Angelo Trevisani (named in p.314 note 1; identity unresolved)", "person", "The printed note gives this name. Keep distinct from the existing Angiolo Trevisani candidate until S3 alignment establishes identity.", 288)
add_candidate("cand-9895", "Records of pictures recommended to Schulenburg, Archives in Hanover (unspecified)", "archive", "P.314 note 1 says recommendations by Piazzetta, Pittoni, and Angelo Trevisani are recorded in archives in Hanover; no repository, shelfmark, or individual picture is specified.", 288)
add_candidate("cand-9896", "White (author cited with Sewter at p.314 note 2; identity unresolved)", "person", "Surname-only author reference; no identity beyond Haskell's citation is assumed.", 289)
add_candidate("cand-9897", "Sewter (author cited with White at p.314 note 2; identity unresolved)", "person", "Surname-only author reference; no identity beyond Haskell's citation is assumed.", 289)
add_candidate("cand-9898", "White and Sewter, 1959, pages 96-100 (citation locator)", "archive", "Cited in relation to the p.314 discussion of a proposed social-satire interpretation. Title and authors' full identities are not supplied here; cited pages were not independently consulted.", 289)
add_candidate("cand-9899", "Levey, Arte Veneta, 1958, page 221 (citation locator)", "archive", "Cited for the subsequent English sale of Ceruti pictures. Article title and Levey's full identity are not supplied here; the cited page was not independently consulted.", 290)
add_candidate("cand-9900", "Surviving portraits of Schulenburg by Gian Antonio Guardi (unspecified group)", "work", "The plural referent in p.313 L76 points back to a succession of Schulenburg portraits by Guardi; no individual titles or dates are given. Keep distinct from the specific Museo Correr portrait in note 1.", 76, P313)
add_candidate("cand-9901", "Turkish scenes copied by Gian Antonio Guardi after Van Mour engravings, 1742-1743 (series)", "work", "Haskell describes the series as an example of Guardi's delicate fantasy; note 2 reports Watson's attribution to Gian Antonio rather than Francesco Guardi. Individual scenes and engravings are not identified.", 76, P313)
add_candidate("cand-9902", "Portrait of Schulenburg attributed to Gian Antonio Guardi at Museo Correr (Pignatti, 1960, p.105)", "work", "Specific portrait cited in p.313 note 1. Attribution is reported as attributed, not settled; no title, date, current catalogue record, or relation to Plate 53a is established.", 284)
add_candidate("cand-9903", "Museo Correr, Venice (museum named in p.313 note 1)", "institution", "Named as the location of a portrait in Haskell's note; current institutional name and present custody were not independently checked.", 284)
add_candidate("cand-9904", "Venice (place named in p.313 note 1)", "place", "Named as the location of Museo Correr in the note; identity alignment with repeated index candidates is deferred to S3.", 284)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []
segment_bounds = {P313: (72, 81), P314: (83, 93), NOTES: (273, 349)}


def add_mention(cid, segment, line_no, needle, note="", occurrence=0):
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention candidate missing: {cid}")
    start_line, end_line = segment_bounds[segment]
    if not start_line <= line_no <= end_line:
        raise SystemExit(f"mention line outside segment: {segment} L{line_no}")
    line = source_lines[line_no - 1]
    matches = []
    cursor = 0
    while True:
        at = line.find(needle, cursor)
        if at < 0:
            break
        matches.append(at)
        cursor = at + max(1, len(needle))
    if occurrence >= len(matches):
        raise SystemExit(f"mention needle missing at L{line_no}: {needle!r}")
    at = matches[occurrence]
    surface = line[at:at + len(needle)]
    segment_text = "\n".join(source_lines[start_line - 1:end_line])
    start = sum(len(source_lines[index - 1]) + 1 for index in range(start_line, line_no)) + at
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention offset mismatch: {segment} L{line_no} {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p313-314-note-{len(new_mentions) + 1:04d}",
        "segment_id": segment,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


# Correct the p.313 body referents without changing the canonical OCR source.
body_mentions = {row["mention_id"]: row for row in mentions}
body_reassignments = {
    "m-s2-ch10-p313-0028": ("cand-9900", "portraits"),
    "m-s2-ch10-p313-0032": ("cand-9900", "those that have survived"),
    "m-s2-ch10-p313-0034": ("cand-9901", "little Turkish scenes"),
}
for mention_id, (candidate_id, surface) in body_reassignments.items():
    row = body_mentions.get(mention_id)
    if not row or row["surface_form"] != surface or row["candidate_id"] not in {"cand-1247", "cand-1251"}:
        raise SystemExit(f"expected p.313 object mention not found: {mention_id}")
    row["candidate_id"] = candidate_id

# Named people, sources, and works in the canonical p.313-314 note block.
for cid, line, needle in [
    ("cand-8257", 284, "Morassi"),
    ("cand-9891", 284, "Pignatti"),
    ("cand-9892", 284, "Pignatti, i960, p. 105"),
    ("cand-2401", 284, "Schulenburg"),
    ("cand-1245", 284, "Gian Antonio Guardi"),
    ("cand-9902", 284, "the portrait of Schulenburg"),
    ("cand-9903", 284, "Museo Correr"),
    ("cand-9904", 284, "Venice"),
    ("cand-2803", 285, "Watson"),
    ("cand-9893", 285, "Watson, i960, pp. 3-13"),
    ("cand-1245", 285, "Gian Antonio"),
    ("cand-1239", 285, "Francesco Guardi"),
    ("cand-9901", 285, "the series"),
    ("cand-9884", 286, "Inventaire de la Galerie de feu Mgr. le Feldtnarechal Comte de Schulenburg"),
    ("cand-8257", 286, "Morassi"),
    ("cand-9885", 286, "Morassi, 1952, pp. 85-91"),
    ("cand-3862", 288, "Piazzetta"),
    ("cand-3870", 288, "Pittoni"),
    ("cand-9894", 288, "Angelo Trevisani"),
    ("cand-9895", 288, "Archives in Hanover"),
    ("cand-9896", 289, "White"),
    ("cand-9897", 289, "Sewter"),
    ("cand-9898", 289, "White and Sewter, 1959, pp. 96-100"),
    ("cand-9884", 290, "published inventory"),
    ("cand-9338", 290, "Levey"),
    ("cand-9899", 290, "Levey, in Arte Veneta, 1958, p. 221"),
    ("cand-8983", 290, "England"),
    ("cand-1546", 291, "Marieschi"),
    ("cand-0554", 291, "Carlevarijs"),
    ("cand-3748", 291, "Cimaroli"),
    ("cand-1334", 291, "Joli"),
    ("cand-2879", 291, "Zuccarelli"),
    ("cand-3831", 291, "Marco Ricci"),
]:
    add_mention(cid, NOTES, line, needle)

all_mentions = mentions


def span_quote(start_line, end_line):
    return "\n".join(source_lines[start_line - 1:end_line])


new_statements = []


def add_statement(sid, subject, object_id, predicate, line, claim, qualification, mentioned,
                  printed_page, physical_page, speaker="Haskell footnote", layer="bibliographic note",
                  relation_candidate=False, extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement ID already exists: {sid}")
    quote = span_quote(line, line)
    if quote not in "\n".join(source_lines[272:349]):
        raise SystemExit(f"statement quote not found in note source: {sid}")
    if subject and subject not in all_candidate_ids:
        raise SystemExit(f"missing subject candidate for {sid}: {subject}")
    if object_id and object_id not in all_candidate_ids:
        raise SystemExit(f"missing object candidate for {sid}: {object_id}")
    mentioned = list(dict.fromkeys(mentioned))
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate for {sid}")
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": printed_page,
        "pdf_physical_page": physical_page,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
    }
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": sid,
        "segment_id": NOTES,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


# Page 313, printed p.313 / PDF physical page 46.
add_statement("st-chp10-p313-n01-portrait-attribution", "cand-9902", "cand-1245", "attributed_to",
              284, "Haskell cites Pignatti for a portrait of Schulenburg at Museo Correr attributed to Gian Antonio Guardi.",
              "This is a reported attribution, not an identity decision. Pignatti p.105 was not independently consulted; the portrait is not identified with Plate 53a or any other work.",
              ["cand-9902", "cand-2401", "cand-1245", "cand-9903", "cand-9904", "cand-9891", "cand-9892", "cand-8257"], 313, 46,
              relation_candidate=True,
              extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p313-surviving-guardi-portraits-quality"],
                     "citations": [{"source_candidate_id": "cand-9892", "author_candidate_id": "cand-9891", "year": "1960", "page": "105"}],
                     "ocr_corrections": [{"source_line": 284, "ocr": "i960", "print": "1960"}]})
add_statement("st-chp10-p313-n01-portrait-museum-location", "cand-9902", "cand-9903", "located_at",
              284, "Haskell locates the cited Schulenburg portrait at Museo Correr, Venice.",
              "This location is reported by Haskell through the note; no current catalogue or custody was checked.",
              ["cand-9902", "cand-2401", "cand-9903", "cand-9904"], 313, 46,
              relation_candidate=True,
              extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p313-surviving-guardi-portraits-quality"]})
add_statement("st-chp10-p313-n02-exhibition-and-sale-appearances", "cand-9901", None, "works_appeared_in_exhibitions_and_sales",
              285, "Haskell says a number of the preceding works had appeared in exhibitions and sales in the last few years.",
              "The footnote marker follows the Turkish-scenes discussion; 'these' is preserved as a contextual reference and is not resolved to individually identified works. Relative time is measured from Haskell's publication.",
              ["cand-9901", "cand-1245"], 313, 46,
              extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p313-guardi-turkish-scenes-after-van-mour"],
                     "relative_time_phrase": "during the last few years"})
add_statement("st-chp10-p313-n02-watson-series-attribution", "cand-9901", "cand-1245", "reported_attribution_to_gian_antonio_guardi",
              285, "Haskell reports that Watson attributes the series to Gian Antonio rather than Francesco Guardi.",
              "Watson's attribution is reported through Haskell and was not independently consulted. The series is linked to the Turkish-scenes passage by the footnote marker; individual works remain unidentified.",
              ["cand-9901", "cand-1245", "cand-1239", "cand-2803", "cand-9893"], 313, 46,
              speaker="Watson, as reported by Haskell", layer="attribution reported in footnote", relation_candidate=True,
              extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p313-guardi-turkish-scenes-after-van-mour"],
                     "citations": [{"source_candidate_id": "cand-9893", "author_candidate_id": "cand-2803", "year": "1960", "pages": ["3", "13"]}],
                     "ocr_corrections": [{"source_line": 285, "ocr": "i960", "print": "1960"}]})
add_statement("st-chp10-p313-n03-inventory-reference", "cand-2401", "cand-9884", "cites_published_schulenburg_collection_inventory",
              286, "Haskell identifies the Schulenburg published inventory and says Morassi refers to it in the 1952 discussion, pages 85-91.",
              "The inventory and Morassi's cited pages were not independently consulted. The printed title reads 'Feldmarechal'; OCR at this line reads 'Feldtnarechal'.",
              ["cand-2401", "cand-9884", "cand-8257", "cand-9885"], 313, 46,
              extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p313-schulenburg-collection-history-and-genre-paintings"],
                     "citations": [{"source_candidate_id": "cand-9884", "work_title": "Inventaire de la Galerie de feu Mgr. le Feldmarechal Comte de Schulenburg"},
                                   {"source_candidate_id": "cand-9885", "author_candidate_id": "cand-8257", "year": "1952", "pages": ["85", "91"]}],
                     "ocr_corrections": [{"source_line": 286, "ocr": "Feldtnarechal", "print": "Feldmarechal"}]})
add_statement("st-chp10-p313-n04-chapter-cross-reference", None, None, "cross_references_printed_chapter",
              287, "Haskell's note directs the reader to Chapter 10.",
              "The note gives no page or section locator. It is preserved as a printed cross-reference without mapping it to a project chapter or asserting that it is a new source.",
              [], 313, 46, layer="internal cross-reference",
              extra={"footnote_number": 4, "linked_body_statement_ids": ["st-chp10-p313-pittoni-schulenburg-commission-and-reputation"],
                     "cross_reference_target": {"printed_chapter_number": 10, "specific_destination": "unresolved"}})

# Page 314, printed p.314 / PDF physical page 47.
for artist_id, suffix, artist_name in [
    ("cand-3862", "piazzetta", "Piazzetta"),
    ("cand-3870", "pittoni", "Pittoni"),
    ("cand-9894", "angelo-trevisani", "Angelo Trevisani"),
]:
    add_statement(f"st-chp10-p314-n01-{suffix}-recommended-pictures", artist_id, "cand-2401", "recommended_pictures_to",
                  288, f"Haskell says pictures recommended to Schulenburg by {artist_name} are recorded in Hanover archives.",
                  "The note gives no individual picture titles, dates, archive repository, or shelfmark. 'Angelo Trevisani' is kept distinct from Angiolo Trevisani pending S3 alignment.",
                  [artist_id, "cand-2401", "cand-9895"], 314, 47, layer="archival fact reported in footnote", relation_candidate=True,
                  extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p314-piazzetta-chief-agent-for-schulenburg"],
                         "archive_candidate_id": "cand-9895", "specific_picture_titles": "not supplied"})
add_statement("st-chp10-p314-n02-white-sewter-citation", "cand-9617", "cand-9898", "cites_discussion_of_social_satire_interpretation",
              289, "Haskell cites White and Sewter, 1959, pages 96-100, alongside the proposed social-satire interpretation.",
              "The cited pages were not independently consulted; this citation does not change Haskell's explicit statement that the interpretation is almost certainly wrong.",
              ["cand-9617", "cand-9896", "cand-9897", "cand-9898"], 314, 47,
              extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p314-social-satire-interpretation-qualified"],
                     "citations": [{"source_candidate_id": "cand-9898", "authors": ["cand-9896", "cand-9897"], "year": "1959", "pages": ["96", "100"]}]})
add_statement("st-chp10-p314-n03-inventory-reference", "cand-2401", "cand-9884", "cites_published_inventory_for_ceruti_pictures",
              290, "Haskell points to the published Schulenburg inventory for the Ceruti pictures.",
              "The inventory was not independently consulted; the note's cross-reference is attached to the statement about seven Ceruti pictures.",
              ["cand-2401", "cand-9604", "cand-9884"], 314, 47,
              extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p314-schulenburg-owned-seven-ceruti-pictures"],
                     "citations": [{"source_candidate_id": "cand-9884"}]})
add_statement("st-chp10-p314-n03-ceruti-sale-in-england", "cand-9604", "cand-8983", "subsequent_sale_in_england_reported_by_levey",
              290, "Haskell says Levey discusses the subsequent sale in England of the Ceruti pictures.",
              "This is a sale claim attributed to Haskell's citation of Levey; the cited page was not independently consulted and no sale date or buyer is given.",
              ["cand-9604", "cand-8983", "cand-9338", "cand-9899", "cand-9884"], 314, 47,
              speaker="Haskell citing Levey", layer="sale reported in footnote", relation_candidate=True,
              extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p314-schulenburg-owned-seven-ceruti-pictures"],
                     "citations": [{"source_candidate_id": "cand-9899", "author_candidate_id": "cand-9338", "periodical": "Arte Veneta", "year": "1958", "page": "221"}]})

for artist_id, work_id, suffix, count, artist_name in [
    ("cand-1546", "cand-9608", "marieschi", 10, "Michele Marieschi"),
    ("cand-0554", "cand-9609", "carlevarijs", 6, "Luca Carlevarijs"),
    ("cand-3748", "cand-9610", "cimaroli", 4, "Giovan Battista Cimaroli"),
    ("cand-1334", "cand-9611", "joli", 2, "Antonio Joli"),
    ("cand-3831", "cand-9612", "marco-ricci", 6, "Marco Ricci"),
    ("cand-2879", "cand-9613", "zuccarelli", 9, "Francesco Zuccarelli"),
]:
    add_statement(f"st-chp10-p314-n04-{suffix}-count", "cand-2401", work_id, "owned_number_of_pictures_by_artist",
                  291, f"Haskell's p.314 note reports {count} pictures by {artist_name} in Schulenburg's collection.",
                  "The note continues the preceding collection statement. Individual titles, dates, and current locations are not supplied; the count is attributed to Haskell and not independently checked.",
                  ["cand-2401", artist_id, work_id], 314, 47, layer="collection quantity in authorial footnote", relation_candidate=True,
                  extra={"footnote_number": 4, "linked_body_statement_ids": ["st-chp10-p314-schulenburg-owned-views-and-landscapes-by-six-artists"],
                         "artist_candidate_id": artist_id, "reported_count": count, "count_unit": "pictures"})

all_statements = statements + new_statements
statement_by_id = {row["statement_id"]: row for row in all_statements}


def add_footnote_ref(body_statement_id, marker, source_line, note_statement_ids):
    row = statement_by_id.get(body_statement_id)
    if not row:
        raise SystemExit(f"body statement missing: {body_statement_id}")
    q = row["qualifiers"]
    if q.get("footnote_marker") != marker or q.get("pending_note_source_line") != source_line:
        raise SystemExit(f"unexpected body footnote marker/source line: {body_statement_id}")
    q["footnote_text_pending"] = False
    q["footnote_segment"] = NOTES
    refs = q.setdefault("footnote_refs", [])
    ref = {"marker": marker, "segment_id": NOTES, "source_line": source_line}
    if ref not in refs:
        refs.append(ref)
    ids = q.setdefault("footnote_statement_ids", [])
    for note_statement_id in note_statement_ids:
        if note_statement_id not in statement_by_id:
            raise SystemExit(f"note statement missing for footnote ref: {note_statement_id}")
        if note_statement_id not in ids:
            ids.append(note_statement_id)
    q["footnote_body_link_status"] = "linked"


for body_statement_id, marker, line, note_ids in [
    ("st-chp10-p313-surviving-guardi-portraits-quality", 1, 284, ["st-chp10-p313-n01-portrait-attribution", "st-chp10-p313-n01-portrait-museum-location"]),
    ("st-chp10-p313-guardi-turkish-scenes-after-van-mour", 2, 285, ["st-chp10-p313-n02-exhibition-and-sale-appearances", "st-chp10-p313-n02-watson-series-attribution"]),
    ("st-chp10-p313-schulenburg-collection-history-and-genre-paintings", 3, 286, ["st-chp10-p313-n03-inventory-reference"]),
    ("st-chp10-p313-pittoni-schulenburg-commission-and-reputation", 4, 287, ["st-chp10-p313-n04-chapter-cross-reference"]),
    ("st-chp10-p314-piazzetta-chief-agent-for-schulenburg", 1, 288, ["st-chp10-p314-n01-piazzetta-recommended-pictures", "st-chp10-p314-n01-pittoni-recommended-pictures", "st-chp10-p314-n01-angelo-trevisani-recommended-pictures"]),
    ("st-chp10-p314-social-satire-interpretation-qualified", 2, 289, ["st-chp10-p314-n02-white-sewter-citation"]),
    ("st-chp10-p314-schulenburg-owned-seven-ceruti-pictures", 3, 290, ["st-chp10-p314-n03-inventory-reference", "st-chp10-p314-n03-ceruti-sale-in-england"]),
    ("st-chp10-p314-schulenburg-owned-views-and-landscapes-by-six-artists", 4, 291, [f"st-chp10-p314-n04-{suffix}-count" for suffix in ("marieschi", "carlevarijs", "cimaroli", "joli", "marco-ricci", "zuccarelli")]),
]:
    add_footnote_ref(body_statement_id, marker, line, note_ids)

# Replace incorrect person-to-person object mappings with the picture-group objects named by the prose.
portrait_quality = statement_by_id["st-chp10-p313-surviving-guardi-portraits-quality"]
portrait_quality["subject_candidate_id"] = "cand-9900"
portrait_quality["object_candidate_id"] = None
portrait_quality["qualifiers"]["mentioned_candidate_ids"] = ["cand-9900", "cand-1245"]
portrait_quality["qualifiers"]["qualification"] += " The plural referent is represented by a provisional work-group candidate rather than a repeated person candidate."
turkish_scenes = statement_by_id["st-chp10-p313-guardi-turkish-scenes-after-van-mour"]
turkish_scenes["object_candidate_id"] = "cand-9901"
turkish_scenes["qualifiers"]["mentioned_candidate_ids"] = ["cand-1245", "cand-9901", "cand-1712"]
turkish_scenes["qualifiers"]["qualification"] += " The picture-group referent is represented as a work candidate; its attribution is separately stated in the linked footnote."

candidate_rows = candidates + new_candidates
candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
candidate_by_id["cand-9884"]["canonical_name"] = "Inventaire de la Galerie de feu Mgr. le Feldmarechal Comte de Schulenburg (published inventory, n.d.)"
candidate_by_id["cand-9884"]["detail"] += " P.313 print confirms 'Feldmarechal'; the raw OCR form 'Feldtnarechal' remains in the source transcription and its correction is recorded with that note."

all_mentions = mentions + new_mentions
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate ID")
if len({row["mention_id"] for row in all_mentions}) != len(all_mentions):
    raise SystemExit("duplicate mention ID")
if len({row["statement_id"] for row in all_statements}) != len(all_statements):
    raise SystemExit("duplicate statement ID")
for row in all_mentions:
    if row["candidate_id"] not in candidate_by_id:
        raise SystemExit(f"missing mention foreign key: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    if row["subject_candidate_id"] and row["subject_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"missing statement subject: {row['statement_id']}")
    if row["object_candidate_id"] and row["object_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"missing statement object: {row['statement_id']}")
    if any(cid not in candidate_by_id for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"missing statement mention foreign key: {row['statement_id']}")

coverage[P313].update({
    "migration_status": "complete",
    "source_line_ranges": "L72-81; notes L284-287",
    "note": "Printed p.313 notes 1-4 (canonical L284-287) are transcribed as citation, attribution, and cross-reference claims and linked to their body statements. The L81 fragment remains linked to p.314 L84. Picture-group referents at L76 were corrected from repeated Guardi person candidates to provisional work candidates.",
})
coverage[P314].update({
    "migration_status": "complete",
    "source_line_ranges": "L83-93; notes L288-291",
    "note": "Printed p.314 notes 1-4 (canonical L288-291) are linked, including the named artists' picture recommendations and the six artist-specific quantity claims. The L93 sentence remains linked to its p.315 L96 continuation.",
})
coverage[NOTES].update({
    "migration_status": "partial",
    "source_line_ranges": "L274-291; L325-349",
    "note": "P.311-314 notes L274-291 are reviewed and linked; L325-349 remains previously processed. The remaining gap is L292-324 (p.315-323 notes).",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
all_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_statements.sort(key=lambda row: row["statement_id"])
print(f"p.313-314 note preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("body corrections: 3 p.313 picture mentions remapped from Guardi person entries to provisional work groups")
print("coverage changes: p.313 partial->complete; p.314 partial->complete; consolidated notes remain partial")
print(f"totals: {len(candidate_rows)} candidates, {len(all_mentions)} mentions, {len(all_statements)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, all_mentions)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; recovery copies created with suffix {BACKUP_SUFFIX}")
