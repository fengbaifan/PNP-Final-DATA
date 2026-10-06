#!/usr/bin/env python3
"""Controlled S2 migration for the opening of the second-edition postscript, p.396."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
EXPECTED = {
    SOURCE: "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90",
    PDF: "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788",
}
P396 = "chp-20:20_CHP-20Postscript:l3-12"
P397 = "chp-20:20_CHP-20Postscript:l14-24"
BACKUP_SUFFIX = ".bak-s2-chp20-p396-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


for path, expected in EXPECTED.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)} ({actual})")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(x) for x in statement_path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
coverage_fields, coverage = read_csv(coverage_path)
segments = [json.loads(x) for x in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if x.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
statement_by_id = {row["statement_id"]: row for row in statements}

if P396 not in segment_by_id or P396 not in coverage_by_id or P397 not in segment_by_id:
    raise SystemExit("missing S0/S2 row for p.396–397 continuation")
if (coverage_by_id[P396]["disposition"], coverage_by_id[P396]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.396 should be queued/pending: {coverage_by_id[P396]}")
if (coverage_by_id[P397]["disposition"], coverage_by_id[P397]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.397 continuation should be queued/pending: {coverage_by_id[P397]}")

segment = segment_by_id[P396]
if segment["sha256"] != "3fed41fedf29bc39cfade8d7ab767c1390975387b2b6711ba3a90db50f5ae67a":
    raise SystemExit("registered p.396 S0 hash changed")
if segment["asset_sha256"] != EXPECTED[SOURCE]:
    raise SystemExit("p.396 source asset hash is inconsistent")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text396 = "\n".join(source_lines[segment["line_start"] - 1 : segment["line_end"]])
if hashlib.sha256(text396.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit("p.396 S0 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment["line_start"], segment["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1


def quote(first_line, last_line):
    return "\n".join(source_lines[first_line - 1 : last_line])


new_candidate_specs = [
    ("cand-10850", "Fagiolo dell’Arca (scholar cited in the second-edition postscript)", "person",
     "The printed page reads Fagiolo dell’Arca; the规范 OCR has ‘dell’Area’. Given name is not supplied in this passage."),
    ("cand-10851", "Carandini (coauthor cited with Fagiolo dell’Arca; identity unresolved)", "person",
     "The postscript names Carandini only by surname; do not merge with the indexed Carandini family members."),
    ("cand-10852", "Study of seventeenth-century Roman festivals by Fagiolo dell’Arca and Carandini (title unspecified)", "archive",
     "Haskell describes this study but gives no title here. The publication and cited research were not independently consulted."),
    ("cand-10853", "Marilyn Aronberg Lavin’s publication of Barberini family inventories (title unspecified)", "archive",
     "The postscript says the well-indexed publication transformed knowledge of Barberini patronage and collecting; exact title is not supplied here."),
    ("cand-10854", "Cesare d’Onofrio", "person",
     "Named as the author/publisher of further documents on Maffeo Barberini; identity and bibliography remain for S3/S2 bibliography review."),
    ("cand-10855", "Documents on Maffeo Barberini published by Cesare d’Onofrio (title unspecified)", "archive",
     "The postscript says the documents illuminate Maffeo Barberini’s character and poetry; titles and cited pages are not supplied in this segment."),
    ("cand-10856", "Roberto Longhi, 1963 publication cited for an alternative Maffeo portrait (title unspecified)", "archive",
     "The adjacent page footnote identifies Longhi, 1963; the cited publication was not consulted."),
    ("cand-10857", "Portrait in the Corsini collection once presented as a Caravaggio portrait of Maffeo Barberini (work unresolved)", "work",
     "Haskell says the first edition reproduced this picture as a candidate portrait and later notes the Barberini inventories do not record such a portrait. Do not merge with the Longhi version."),
    ("cand-10858", "Longhi version: alternative Maffeo Barberini portrait reproduced with tentative attribution (work unresolved)", "work",
     "Haskell says Longhi published this as another candidate, substituted it in the Italian edition after seeing a photograph, and reproduces it with a very tentative attribution. No specific title or present collection is given."),
    ("cand-10859", "Irving Lavin", "person",
     "Named for an analysis of Bernini’s transformation of the crossing of St Peter’s; further identity alignment is deferred to S3."),
    ("cand-10860", "Irving Lavin’s analysis of Bernini’s transformation of the crossing of St Peter’s (1968; title unspecified)", "archive",
     "The cited analysis is described in the postscript and footnoted on p.397 as Lavin, I., 1968; neither publication nor cited pages were consulted."),
    ("cand-10861", "Crossing of St Peter’s Basilica discussed in Lavin’s analysis (interior place; boundaries unspecified)", "place",
     "The passage concerns Bernini’s transformation of the basilica crossing; retain the architectural space as distinct from the basilica and from artworks."),
    ("cand-10862", "Corsini collection named as the former location of the first-edition portrait (identity/type unresolved)", "",
     "The postscript supplies only ‘the Corsini collection’; do not identify a modern gallery or treat the collection as the portrait itself."),
    ("cand-10863", "Undisclosed private collection said to hold Longhi’s alternative portrait (identity/type unresolved)", "",
     "Haskell explicitly withholds the collection’s identity. It is distinct from the Corsini collection and should not be expanded."),
]
existing_keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
candidate_source_lines = {
    "cand-10850": 6, "cand-10851": 6, "cand-10852": 6, "cand-10853": 9,
    "cand-10854": 10, "cand-10855": 10, "cand-10856": 11, "cand-10857": 11,
    "cand-10858": 11, "cand-10859": 12, "cand-10860": 12, "cand-10861": 12,
    "cand-10862": 11, "cand-10863": 11,
}
for cid, name, kind, detail in new_candidate_specs:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.casefold())
    if key in existing_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P396}#L{candidate_source_lines[cid]}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

mention_specs = [
    ("cand-10850", "Fagiolo dell’Area", 6, 6, "OCR reads ‘Area’; the printed page reads ‘Arca’.", 0),
    ("cand-10851", "Carandini", 6, 6, "Surname only; distinct from indexed Carandini family members.", 0),
    ("cand-4490", "the city", 6, 6, "Anaphoric reference to Rome in the same sentence.", 0),
    ("cand-10852", "their study of seventeenth-century festivals", 6, 6, "Study title not given; cited work not consulted.", 0),
    ("cand-4490", "Baroque Rome", 7, 7, "Place named as the subject area of the postscript’s evaluation.", 0),
    ("cand-0198", "Barberini family", 9, 9, "Family whose members’ patronage and collecting are discussed.", 0),
    ("cand-10853", "well-indexed publication by Marilyn Lavin of all the inventories", 9, 9, "Publication title unspecified; later bibliography pass may add citation detail.", 0),
    ("cand-4787", "Marilyn Lavin", 9, 9, "Reuse the existing author candidate.", 0),
    ("cand-4779", "all the inventories", 9, 9, "Reuse the previously registered body of Barberini inventory records; distinguish it from Lavin’s publication.", 0),
    ("cand-4490", "Rome", 9, 9, "Place where Haskell says he was working.", 0),
    ("cand-10854", "Cesare d’Onofrio", 10, 10, "Named in the postscript; no full bibliography supplied here.", 0),
    ("cand-10855", "Further documents published by Cesare d’Onofrio", 10, 10, "Publication/document set; title unspecified.", 0),
    ("cand-0209", "Maffeo Barberini (Pope Urban VIII)", 10, 10, "Full name and papal identification as printed.", 0),
    ("cand-0272", "Bellori", 11, 11, "Bellori is the authority Haskell says specifically states the attribution.", 0),
    ("cand-0544", "Caravaggio", 11, 11, "First occurrence: the reported attribution of a portrait.", 0),
    ("cand-0551", "a portrait of Maffeo Barberini", 11, 11, "Reuse the index subentry as the general portrait claim; individual Corsini and Longhi versions remain distinct candidates.", 0),
    ("cand-1507", "Mancini", 11, 11, "Giulio Mancini candidate from the index; contemporary hint is reported by Haskell.", 0),
    ("cand-10857", "a well-known but not at all good portrait in the Corsini collection", 11, 11, "Specific first-edition picture, kept distinct from the Longhi version.", 0),
    ("cand-10862", "Corsini collection", 11, 11, "Collection identity and type remain unresolved.", 0),
    ("cand-0198", "the Barberini", 11, 11, "Family identified as the portrait’s earlier owner in Haskell’s account.", 0),
    ("cand-5505", "Roberto Longhi", 11, 11, "Reuse the existing person candidate.", 0),
    ("cand-10858", "another candidate for the role", 11, 11, "Longhi’s separate alternative portrait; no title or present collection is given.", 0),
    ("cand-10863", "undisclosed private collection", 11, 11, "The passage explicitly withholds its identity; distinct from the Corsini collection.", 0),
    ("cand-10858", "‘Longhi version’", 11, 11, "The reproduced alternative has only a very tentative attribution.", 0),
    ("cand-10857", "the Corsini picture", 11, 11, "The first-edition picture, distinct from the Longhi version.", 0),
    ("cand-4779", "the Barberini inventories", 11, 11, "Haskell says these records do not contain a portrait of Maffeo by Caravaggio; the records themselves were not consulted here.", 0),
    ("cand-0209", "Maffeo", 11, 11, "Second occurrence, in Haskell’s statement about the inventory evidence.", 1),
    ("cand-0544", "Caravaggio", 11, 11, "Second occurrence, in the inventory-based qualification.", 1),
    ("cand-0209", "young and energetic Barberini", 11, 11, "The Longhi version’s subject as described by Haskell; retain his tentative attribution.", 0),
    ("cand-3806", "Howard Hibbard", 12, 12, "Reuse the accepted-unit candidate; the source names the author in full.", 0),
    ("cand-5163", "monograph on Carlo Maderno", 12, 12, "Reuse the 1971 Hibbard publication candidate; the title remains unspecified.", 0),
    ("cand-4873", "Carlo Maderno", 12, 12, "Reuse the existing source-derived person candidate.", 0),
    ("cand-10859", "Irving Lavin", 12, 12, "Named for the analysis continuing onto p.397.", 0),
    ("cand-10860", "analysis of Bernini’s transformation of the crossing of St Peter’s", 12, 12, "Cited analysis; publication title remains unspecified.", 0),
    ("cand-0295", "Bernini", 12, 12, "Bernini’s transformation is reported through Lavin’s analysis.", 0),
    ("cand-10861", "the crossing", 12, 12, "Interior architectural space of St Peter’s; continuation on p.397 supplies the end of the sentence.", 0),
    ("cand-0713", "St Peter’s", 12, 12, "Reuse the index candidate for the basilica; keep the crossing as its interior space.", 0),
    ("cand-1479", "the family palace", 12, 12, "Adjacent context suggests the Barberini palace; retain as a candidate link pending S3.", 0),
]

new_mentions = []
mention_ids = {r["mention_id"] for r in mentions}
for ordinal, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, start=1):
    mid = f"m-chp20-p396-{ordinal:03d}"
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention target missing or closed: {cid}")
    lower = line_offset[first]
    upper = line_offset[last] + len(source_lines[last - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text396.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(f"surface not found in p.396 lines {first}-{last}: {surface!r}")
        cursor = found + 1
    new_mentions.append({
        "mention_id": mid, "segment_id": P396, "candidate_id": cid,
        "surface_form": surface, "start_char": str(found),
        "end_char": str(found + len(surface)), "note": note,
    })
    mention_ids.add(mid)

intervals = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"])
                   for r in [*mentions, *new_mentions] if r["segment_id"] == P396)
for index, left in enumerate(intervals):
    for right in intervals[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing p.396 mention spans: {left[2]} / {right[2]}")


def make_statement(sid, first, last, obj, predicate, claim, text_layer, qualification, candidate_ids,
                   relation=False, extra=None):
    qualifiers = {
        "source_line_start": first, "source_line_end": last,
        "printed_page": 396, "pdf_physical_page": 1,
        "claim": claim, "speaker": "Haskell",
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation,
        "cited_material_not_independently_consulted": True,
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid, "segment_id": P396,
        "subject_candidate_id": None, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(first, last),
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "origin": "book",
    }


new_statements = [
    make_statement("st-chp20-p396-fagiolo-carandini-study", 6, 7, "cand-10852",
        "recent_study_of_roman_festivals_and_its_relevance_to_patrons_and_politics",
        "Haskell says Fagiolo dell’Arca and Carandini assembled visual and documentary material on seventeenth-century Roman festivals. He says their study illuminates festivals’ relations to the arts, patrons, politics, and intellectual climate, and would be valuable to readers concerned with Baroque Rome.",
        "authorial assessment of recent scholarship",
        "The study is cited but not independently consulted. Page-image reading corrects OCR ‘dell’Area’ to printed ‘dell’Arca’; no given names or title are added.",
        ["cand-10850", "cand-10851", "cand-10852", "cand-4490"], relation=True,
        extra={"cross_reference_segments": ["chp-20:20_CHP-20Postscript:l211-280"],
               "ocr_corrections": [{"source_line": 6, "ocr": "dell’Area", "print": "dell’Arca", "basis": "CHP-20Postscript.pdf physical page 1"}]}),
    make_statement("st-chp20-p396-lavin-barberini-inventory-publication", 9, 9, "cand-10853",
        "lavin_publication_transformed_knowledge_of_barberini_patronage_and_collecting",
        "Haskell says Marilyn Lavin’s well-indexed publication of Barberini family inventories transformed knowledge of the family’s patronage and collecting, including inventories that had eluded him during his work in Rome.",
        "authorial assessment of published scholarship",
        "The cited publication is not identified by title in this passage and was not independently consulted; distinguish the publication from the inventory records themselves.",
        ["cand-10853", "cand-4787", "cand-0198", "cand-4779", "cand-4490"], relation=True),
    make_statement("st-chp20-p396-donofrio-documents-on-maffeo", 10, 10, "cand-10855",
        "donofrio_documents_concern_maffeo_barberinis_character_and_poetry",
        "Haskell says further documents published by Cesare d’Onofrio are useful for elucidating Maffeo Barberini’s character and poetry; he says one major patronage problem is more confusing than before.",
        "authorial assessment and unresolved interpretation",
        "The cited documents and patronage problem are not resolved here; the sentence states Haskell’s evaluation, not a new biographical fact.",
        ["cand-10854", "cand-10855", "cand-0209"], relation=True),
    make_statement("st-chp20-p396-bellori-mancini-caravaggio-portrait-claim", 11, 11, "cand-0551",
        "bellori_attributed_maffeo_barberini_portrait_to_caravaggio_with_mancini_as_earlier_hint",
        "Haskell reports that Bellori specifically says Caravaggio painted a portrait of Maffeo Barberini and that Mancini had already hinted at the identification.",
        "Haskell’s report of earlier authors’ claims",
        "Bellori and Mancini are cited in the page footnote; their texts were not independently consulted in this S2 pass. This general portrait claim does not identify either later picture candidate.",
        ["cand-0272", "cand-0544", "cand-0209", "cand-0551", "cand-1507"], relation=True,
        extra={"cross_reference_segments": ["chp-20:20_CHP-20Postscript:l211-280"]}),
    make_statement("st-chp20-p396-first-edition-corsini-portrait", 11, 11, "cand-10857",
        "first_edition_presented_corsini_picture_as_caravaggio_portrait_of_maffeo",
        "Haskell says the first edition followed other writers in reproducing and describing a portrait in the Corsini collection as Caravaggio’s portrait of Maffeo; he says the picture had originally belonged to the Barberini.",
        "retrospective account of first-edition attribution",
        "This is Haskell’s account of the earlier attribution, not a settled authorship or identity decision. Keep this picture separate from Longhi’s alternative.",
        ["cand-10857", "cand-10862", "cand-0198", "cand-0544", "cand-0209"], relation=True),
    make_statement("st-chp20-p396-inventory-qualification-of-caravaggio-portrait", 11, 11, "cand-4779",
        "barberini_inventories_record_no_maffeo_portrait_by_caravaggio_according_to_haskell",
        "Haskell says the Barberini inventories record no portrait of Maffeo by Caravaggio.",
        "authorial report of inventory evidence",
        "The inventories are cited as evidence but are not independently consulted here. Preserve this as Haskell’s report and its conflict with prior portrait attributions.",
        ["cand-4779", "cand-0209", "cand-0544", "cand-10857"], relation=True),
    make_statement("st-chp20-p396-longhi-alternative-portrait", 11, 11, "cand-10858",
        "longhi_published_alternative_maffeo_portrait_and_haskell_used_it_with_tentative_attribution",
        "Haskell says Roberto Longhi published another candidate portrait in an undisclosed private collection. After seeing a photograph, Haskell substituted it for the Corsini picture in the Italian edition and later reproduced it with a very tentative attribution, praising its force as a portrait of the young Maffeo Barberini.",
        "retrospective account of alternative portrait attribution",
        "The private collection remains undisclosed. Haskell’s attribution is explicitly very tentative; do not conclude the work is by Caravaggio or identify it with the Corsini picture.",
        ["cand-5505", "cand-10856", "cand-10858", "cand-10857", "cand-0209"], relation=True,
        extra={"cross_reference_segments": ["chp-20:20_CHP-20Postscript:l211-280"]}),
    make_statement("st-chp20-p396-hibbard-maderno-monograph", 12, 12, "cand-5163",
        "hibbard_monograph_clarified_origins_of_the_family_palace",
        "Haskell says Howard Hibbard’s monograph on Carlo Maderno greatly clarified understanding of the origins of the family palace.",
        "authorial assessment of scholarship",
        "The source names Howard Hibbard and footnote 6 identifies a 1971 publication; title and the precise palace identity are not supplied in this segment.",
        ["cand-3806", "cand-5163", "cand-4873", "cand-1479"], relation=True,
        extra={"cross_reference_segments": ["chp-20:20_CHP-20Postscript:l211-280"]}),
    make_statement("st-chp20-p396-lavin-bernini-crossing-open", 12, 12, "cand-10860",
        "lavin_analysis_of_berninis_st_peters_crossing_confirms_haskells_impression_open",
        "Haskell says Irving Lavin’s analysis of Bernini’s transformation of the St Peter’s crossing confirms his own less formal impression; the sentence opens a quotation about a process that continues on p.397.",
        "authorial assessment with cross-page quotation",
        "The statement remains open across p.396–397. The quote and qualification must be closed against the continuation before this segment can become complete; Lavin’s study was not independently consulted.",
        ["cand-10859", "cand-10860", "cand-0295", "cand-10861", "cand-0713"], relation=True,
        extra={"cross_reference_segments": [P397], "open_across_segment": True}),
]

existing_statement_ids = {r["statement_id"] for r in statements}
for row in new_statements:
    if row["statement_id"] in existing_statement_ids:
        raise SystemExit(f"statement ID already exists: {row['statement_id']}")
    existing_statement_ids.add(row["statement_id"])
    if row["original_quote"] not in text396:
        raise SystemExit(f"statement quote not contained in p.396 segment: {row['statement_id']}")
    for cid in row["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate {cid}")
    for ref_id in row["qualifiers"].get("cross_reference_segments", []):
        if ref_id not in segment_by_id:
            raise SystemExit(f"statement references missing source segment {ref_id}")

mentions.extend(new_mentions)
statements.extend(new_statements)
coverage_by_id[P396]["disposition"] = "reviewed"
coverage_by_id[P396]["migration_status"] = "partial"
coverage_by_id[P396]["source_line_ranges"] = "L3-12"
coverage_by_id[P396]["note"] = (
    "Printed p.396 (PDF physical page 1) read against the page image. Processes the second-edition postscript opening, "
    "new research references, Lavin and d’Onofrio publications, competing Maffeo portrait claims, and Hibbard/Lavin "
    "scholarship. OCR ‘dell’Area’ corrected to printed ‘dell’Arca’ in S2 qualifiers. The final Lavin quotation continues "
    "on p.397 and remains partial; cited publications and inventories were not independently consulted."
)

files_to_backup = [candidate_path, mention_path, statement_path, coverage_path]
if args.apply:
    for path in files_to_backup:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print("applied p.396 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(new_candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("p.396 marked reviewed/partial because the Lavin quotation continues on printed p.397")
    print("separate portraits, tentative attribution, prior inventory conflict, and source limitations are preserved")
