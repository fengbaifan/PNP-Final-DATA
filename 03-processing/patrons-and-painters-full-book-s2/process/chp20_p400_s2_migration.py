#!/usr/bin/env python3
"""Controlled S2 migration for p.400 of the second-edition postscript."""

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
EXPECTED_SOURCE = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
EXPECTED_PDF = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
P399 = "chp-20:20_CHP-20Postscript:l38-44"
P400 = "chp-20:20_CHP-20Postscript:l46-57"
P401 = "chp-20:20_CHP-20Postscript:l81-96"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
CHP3_TREATISE = "chp-3:03_CHP-3_sec_i:l16-24"
CHP4_CASSIANO = "chp-4:04_CHP-4_sec_ii:l232-308"
OPEN_400 = "st-chp20-p400-cassiano-journal-publication-open"
BACKUP_SUFFIX = ".bak-s2-chp20-p400-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


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


for path, expected in ((SOURCE, EXPECTED_SOURCE), (PDF, EXPECTED_PDF)):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)}")

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

for sid in (P399, P400, P401, NOTES, CHP3_TREATISE, CHP4_CASSIANO):
    if sid not in segment_by_id:
        raise SystemExit(f"missing registered segment: {sid}")
if (coverage_by_id[P399]["disposition"], coverage_by_id[P399]["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.399 must be reviewed/complete before p.400")
if (coverage_by_id[P400]["disposition"], coverage_by_id[P400]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.400 is no longer queued/pending")
if coverage_by_id[P401]["disposition"] != "queued":
    raise SystemExit("p.401 must remain queued while p.400 opens the journal sentence")
if segment_by_id[P400]["sha256"] != "863f1d5c8f7b6d883cbb4086fabb6b670bbc70da68d79020529b9f1c980104bb":
    raise SystemExit("registered p.400 S0 hash changed")
if segment_by_id[P400]["asset_sha256"] != EXPECTED_SOURCE:
    raise SystemExit("p.400 source asset hash is inconsistent")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text400 = "\n".join(source_lines[segment_by_id[P400]["line_start"] - 1 : segment_by_id[P400]["line_end"]])
if hashlib.sha256(text400.encode("utf-8")).hexdigest() != segment_by_id[P400]["sha256"]:
    raise SystemExit("p.400 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment_by_id[P400]["line_start"], segment_by_id[P400]["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

candidate_specs = [
    ("cand-10934", "Enggass’s article on the Gesù altar of St Ignatius (1974; title unspecified)", "archive", 47, "Footnote 1 cites Enggass, 1974; the article was not independently consulted."),
    ("cand-10935", "Enggass’s book on eighteenth-century sculpture in Rome (1976; title unspecified)", "archive", 47, "Footnote 2 cites Enggass, 1976; the book was not independently consulted."),
    ("cand-10936", "Statues by Théodon and Legros in the Gesù (individual works unspecified)", "work", 47, "The passage names the sculptors but does not identify individual statues."),
    ("cand-10937", "Vittorio Casale", "person", 48, "Named as editor and researcher on the Ottonelli–Pietro da Cortona treatise; identity alignment is deferred to S3."),
    ("cand-10938", "Censor’s comments on Ottonelli and Pietro da Cortona’s treatise (document unspecified)", "archive", 49, "Casale’s later discovery of the censor’s comments is reported; the comments were not independently consulted."),
    ("cand-10939", "Documents on the early building history of the Oratorian Chiesa Nuova (published and analysed by Jacob Hess)", "archive", 50, "The underlying documents and Hess’s publication are cited but not independently consulted here."),
    ("cand-10940", "Jacob Hess", "person", 51, "Named as the scholar who published and analysed documents; identity alignment is deferred to S3."),
    ("cand-10941", "Patrons of individual Chiesa Nuova chapels (unnamed group)", "term", 51, "A role-based group whose attempts to retain decorative autonomy are described; no individual patrons are named."),
    ("cand-10942", "Cardinal Cesi’s letter to an unnamed leading Oratorian (1581; quoted by Haskell)", "archive", 51, "The addressee is not named; footnote 6 cites Bonadonna Russo, 1968, p. 135. The original letter was not consulted."),
    ("cand-10943", "Maria Teresa Bonadonna Russo", "person", 51, "Named as publisher of the letter and related correspondence; identity alignment is deferred to S3."),
    ("cand-10944", "Letters on Oratorian patronage published by Bonadonna Russo (group; titles unspecified)", "archive", 52, "The passage refers to this letter and many similar letters without identifying the full publication set."),
    ("cand-10945", "Monsignor Angelo Cesi (brother of Cardinal Cesi; identity alignment pending)", "person", 53, "Keep distinct in S2 from the indexed Bishop Angelo Cesi candidate until global identity alignment."),
    ("cand-10946", "Inventories dated 1689 and 1695 of collections associated with Carlo Antonio and Gabriele dal Pozzo", "archive", 55, "Haskell does not unambiguously pair each date with one owner in this sentence; preserve the two-inventory group."),
    ("cand-10947", "Gabriele (son of Carlo Antonio; surname unspecified in the passage)", "person", 55, "The passage gives only the forename and identifies him as Carlo Antonio’s son; do not add a normalized surname as settled identity."),
    ("cand-10948", "French pictures recorded in the 1689/1695 dal Pozzo inventories (individual works unspecified)", "work", 55, "A subset of the inventory contents said to have been studied in detail; no individual paintings are named."),
    ("cand-10949", "Harris, 1970 article on Cassiano dal Pozzo’s journey to Spain (title unspecified)", "archive", 55, "Footnote 10 gives only Harris, 1970; cited scholarship was not independently consulted."),
    ("cand-10950", "Cassiano dal Pozzo’s journey to Spain in 1626", "event", 55, "The passage dates the journey to 1626; details beyond the reported journal account are not added."),
    ("cand-10951", "Unidentified now-lost portrait of Cardinal Barberini by the young Velasquez (as reported by Haskell)", "work", 55, "The Cardinal’s identity remains unresolved here; the portrait is explicitly described as lost."),
    ("cand-10952", "Unidentified now-lost portrait of Cardinal Barberini by Juan van der Hamen (as reported by Haskell)", "work", 56, "The portrait is explicitly described as lost; keep it distinct from the Velasquez portrait."),
    ("cand-10953", "Cassiano dal Pozzo’s journal of his Spain journey (specific manuscript and edition unresolved)", "archive", 56, "Only a section is said to have been published in full; the destination sentence continues on p.401."),
    ("cand-10954", "Brejon publication cited for the Cassiano inventory documents (title unspecified)", "archive", 57, "Footnotes 8–9 give short-form citations; the full publication identity awaits the bibliography pass."),
    ("cand-10955", "Brejon (surname-only author cited in p.400 footnotes)", "person", 57, "Retain the surname form until bibliography review and S3 alignment."),
    ("cand-10956", "Harris (surname-only author cited with year 1970)", "person", 57, "Retain the surname form until bibliography review and S3 alignment."),
]

existing_keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
for cid, name, kind, line_number, detail in candidate_specs:
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
        "candidate_source_ref": f"{P400}#L{line_number}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

mention_specs = [
    ("cand-10929", "his monograph on Gaulli", 47, 47, "Reuse the 1964 Gaulli monograph candidate from p.399.", 0),
    ("cand-10928", "Enggass", 47, 47, "Reuse Robert Enggass from p.399.", 0),
    ("cand-10934", "essential article on the altar of St Ignatius in the Gesù", 47, 47, "The title is not supplied; footnote 1 is linked separately.", 0),
    ("cand-5246", "altar of St Ignatius", 47, 47, "Reuse the specific left-transept altar candidate; do not merge it with the Gesù High Altar.", 0),
    ("cand-5200", "Gesù", 47, 47, "Reuse the Church of the Gesù candidate.", 0),
    ("cand-10935", "kra book on eighteenth-century sculpture in Rome", 47, 47, "Anchor preserves the S0 OCR surface ‘kra’; the page image reads ‘a’. Footnote 2 cites Enggass, 1976; title unspecified.", 0),
    ("cand-10936", "statues by Théodon and Legros in the church", 47, 47, "The passage reports a group of statues without individual titles.", 0),
    ("cand-2566", "Théodon", 47, 47, "Reuse the indexed Jean Baptiste Théodon candidate; S3 will align duplicate index entries.", 0),
    ("cand-1379", "Legros", 47, 47, "Reuse the indexed Pierre Legros candidate; S3 will align duplicate index entries.", 0),
    ("cand-3403", "Jesuit patronage", 47, 47, "Reuse the Jesuit institution candidate in the postscript context.", 0),
    ("cand-10937", "Vittorio Casale", 48, 48, "New named scholar/editor; identity alignment is deferred to S3.", 0),
    ("cand-4979", "the treatise on painting and sculpture jointly written by the Jesuit father Ottonelli and by Pietro da Cortona", 48, 48, "Reuse the treatise candidate from chapter 3; this p.400 edition is the same named work by its authors and subject.", 0),
    ("cand-1800", "Ottonelli", 48, 48, "Reuse the indexed Ottonelli candidate.", 0),
    ("cand-0342", "Pietro da Cortona", 48, 48, "Reuse the indexed Pietro da Cortona candidate.", 0),
    ("cand-3403", "Jesuit father", 48, 48, "The modifier identifies Ottonelli’s order; reuse the Jesuit institution candidate.", 0),
    ("cand-10938", "the censor’s comments on it", 49, 49, "The comments are a distinct documentary object; title and repository are not supplied.", 0),
    ("cand-10937", "Casale’s subsequent discovery", 49, 49, "Coreference to Vittorio Casale.", 0),
    ("cand-3403", "Jesuit circles", 49, 49, "Reuse the Jesuit institution candidate.", 0),
    ("cand-3402", "Other religious orders", 50, 50, "Reuse the Oratorian order candidate as the specific order discussed in the following sentence.", 0),
    ("cand-5450", "Oratorian Chiesa Nuova", 50, 50, "Reuse the Church of the Chiesa Nuova place candidate.", 0),
    ("cand-10939", "documents about the early building history of the Oratorian Chiesa Nuova", 50, 50, "Hess’s documents are reported, not independently consulted.", 0),
    ("cand-10940", "Jacob Hess", 51, 51, "New named scholar; identity alignment is deferred to S3.", 0),
    ("cand-3402", "that Order", 51, 51, "Coreference to the Oratorians.", 0),
    ("cand-10941", "patrons of individual chapels", 51, 51, "Unnamed role group whose decorative autonomy is described.", 0),
    ("cand-0640", "Cardinal Cesi", 51, 51, "Reuse indexed Cardinal Pier Donato Cesi candidate; S3 will verify global identity.", 0),
    ("cand-0995", "Cardinal Farnese", 51, 51, "Reuse the Alessandro Cardinal Farnese candidate already named in this postscript.", 0),
    ("cand-3403", "the Jesuits", 51, 51, "Reuse the Jesuit institution candidate.", 0),
    ("cand-10942", "There is no need to send me copies of the plans so that a design that appeals to my taste can be chosen", 51, 51, "Quoted words attributed by Haskell to Cardinal Cesi’s 1581 letter.", 0),
    ("cand-10942", "my taste will be whatever satisfies you and the other Fathers", 51, 51, "Continuation of Cesi’s quoted letter.", 0),
    ("cand-3402", "leading Oratorian", 51, 51, "The addressee is described by role but not named.", 0),
    ("cand-3402", "the other Fathers", 51, 51, "Coreference to the Oratorians.", 0),
    ("cand-10943", "Maria Teresa Bonadonna\nRusso", 51, 52, "The source line break divides the surname; identity alignment is deferred to S3.", 0),
    ("cand-10944", "this and many other letters to the same effect", 52, 52, "Reuse the group of letters published by Bonadonna Russo.", 0),
    ("cand-1427", "Martino Longhi the Elder", 52, 52, "Reuse the indexed architect candidate.", 0),
    ("cand-5450", "the church", 52, 52, "Coreference to Chiesa Nuova.", 0),
    ("cand-0640", "the Cardinal’s intervention", 52, 52, "Coreference to Cardinal Cesi; Haskell says the attribution is probable.", 0),
    ("cand-10945", "Monsignor Angelo Cesi", 53, 53, "Keep a source-specific person candidate until S3 aligns him with the indexed Bishop Angelo Cesi entry.", 0),
    ("cand-2036", "Cassiano dal Pozzo", 55, 55, "Reuse the indexed Cassiano dal Pozzo candidate.", 0),
    ("cand-10946", "the inventories, dated 1689 and 1695", 55, 55, "The sentence describes two inventories as a group; it does not map each date to an owner explicitly.", 0),
    ("cand-2035", "Cassiano’s brother and heir Carlo Antonio", 55, 55, "Reuse the indexed Carlo Antonio dal Pozzo candidate; relationship is recorded as Haskell reports it.", 0),
    ("cand-10947", "the latter’s son Gabriele", 55, 55, "The passage gives a forename only; ‘the latter’ refers to Carlo Antonio; keep identity unresolved.", 0),
    ("cand-10948", "the French pictures recorded in these inventories", 55, 55, "Unspecified picture group; no individual object is named.", 0),
    ("cand-10949", "an article on his journey to Spain in 1626", 55, 55, "Harris 1970 is supplied in footnote 10; title and author identity remain unresolved here.", 0),
    ("cand-10950", "his journey to Spain in 1626", 55, 55, "Coreference to Cassiano dal Pozzo.", 0),
    ("cand-10951", "a (now lost) portrait of Cardinal Barberini by the young\nVelasquez", 55, 56, "The source line break divides the artist’s name from the preceding phrase; keep the sitter unresolved and note the portrait is lost.", 0),
    ("cand-5915", "Cardinal Barberini", 55, 55, "Reuse the source-specific unresolved Cardinal Barberini candidate from chapter 4; do not identify him as Maffeo here.", 0),
    ("cand-2709", "the young\nVelasquez", 55, 56, "The source line break divides the phrase; reuse an indexed Velasquez candidate and defer global identity to S3.", 0),
    ("cand-10952", "one (also lost) by Juan van der Hamen", 56, 56, "A distinct lost portrait, preferred by Cassiano in Haskell’s account.", 0),
    ("cand-1287", "Juan van der Hamen", 56, 56, "Reuse the indexed painter candidate.", 0),
    ("cand-10953", "his journal", 56, 56, "Coreference to Cassiano dal Pozzo; the manuscript and edition are unspecified.", 0),
    ("cand-10954", "9 Brejon", 57, 57, "Printed p.400 footnote 9; full citation awaits bibliography review.", 0),
    ("cand-10955", "Brejon", 57, 57, "Surname-only author mention nested within footnote 9; keep identity unresolved.", 0),
    ("cand-10949", "Harris, 1970", 57, 57, "Printed p.400 footnote 10 identifies the cited article by surname and year.", 0),
    ("cand-10956", "Harris", 57, 57, "Surname-only author mention nested within footnote 10; keep identity unresolved.", 0),
]

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p400-{ordinal:03d}"
    if mention_id in existing_mention_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention target missing or not open: {cid}")
    lower = line_offset[first]
    upper = line_offset[last] + len(source_lines[last - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text400.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(f"surface not found on p.400 lines {first}-{last}: {surface!r}")
        cursor = found + 1
    new_mentions.append({
        "mention_id": mention_id, "segment_id": P400, "candidate_id": cid,
        "surface_form": surface, "start_char": str(found),
        "end_char": str(found + len(surface)), "note": note,
    })
    existing_mention_ids.add(mention_id)

intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
                   for row in [*mentions, *new_mentions] if row["segment_id"] == P400)
for index, left in enumerate(intervals):
    for right in intervals[index + 1 :]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing p.400 mention spans: {left[2]} / {right[2]}")

NOTE_LINES = {1: 226, 2: 226, 3: 227, 4: 227, 5: 228, 6: 228, 7: 229, 8: 230, 9: 57, 10: 57}


def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer,
                   qualification, candidate_ids, relation=False, footnote_markers=None, extra=None):
    qualifiers = {
        "source_line_start": first, "source_line_end": last,
        "printed_page": 400, "pdf_physical_page": 5,
        "claim": claim, "speaker": speaker, "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation,
    }
    if footnote_markers:
        refs = []
        pending = False
        for marker in footnote_markers:
            line_number = NOTE_LINES[marker]
            sid = P400 if marker in (9, 10) else NOTES
            refs.append({"marker": marker, "segment_id": sid, "source_line": line_number})
            pending = pending or sid == NOTES
        qualifiers.update({
            "footnote_markers": footnote_markers,
            "footnote_text_pending": pending,
            "footnote_segment": NOTES if pending else P400,
            "footnote_refs": refs,
            "footnote_statement_ids": [],
            "footnote_body_link_status": "pending" if pending else "linked_in_segment",
        })
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id, "segment_id": P400,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[first - 1:last]),
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "origin": "book",
    }


new_statements = [
    make_statement("st-chp20-p400-enggass-jesuit-altar-article", 47, 47, "cand-10928", "cand-10934",
        "enggass_wrote_article_on_the_gesu_altar_of_st_ignatius",
        "Haskell says that, besides his Gaulli monograph, Robert Enggass wrote an essential article on the altar of St Ignatius in the Gesù.",
        "Haskell", "authorial report of scholarship",
        "The article title is not supplied; footnote 1 cites Enggass, 1974. The article was not independently consulted.",
        ["cand-10928", "cand-10929", "cand-10934", "cand-5246", "cand-5200"], relation=True,
        footnote_markers=[1], extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p400-enggass-rome-sculpture-book", 47, 47, "cand-10928", "cand-10935",
        "enggass_book_added_knowledge_of_theodon_and_legros_statues_and_jesuit_patronage",
        "Haskell says Enggass’s book on eighteenth-century sculpture in Rome added to knowledge of statues by Théodon and Legros in the Gesù and thereby to knowledge of Jesuit patronage.",
        "Haskell", "authorial report of scholarship",
        "Footnote 2 cites Enggass, 1976; the book and individual statues were not independently consulted or identified.",
        ["cand-10928", "cand-10935", "cand-10936", "cand-2566", "cand-1379", "cand-5200", "cand-3403"], relation=True,
        footnote_markers=[2], extra={"cited_material_not_independently_consulted": True,
            "ocr_corrections": [{"source_line": 47, "ocr": "kra book", "print": "a book", "basis": "CHP-20Postscript.pdf physical page 5"}]}),
    make_statement("st-chp20-p400-casale-ottonelli-treatise-and-censor", 48, 49, "cand-10937", "cand-4979",
        "casale_edition_examined_authors_contributions_and_censor_comments",
        "Haskell reports that Vittorio Casale’s edition of the jointly written painting-and-sculpture treatise examined the theologian’s and artist’s contributions; Casale’s later discovery of the censor’s comments provides evidence of how the issues were discussed in Jesuit circles.",
        "Haskell reporting Casale", "authorial report of a scholarly edition and archival discovery",
        "Reuse the treatise already mentioned in chapter 3. Footnotes 3 and 4 cite Ottonelli and Berrettini, and Casale; neither the edition nor censor’s comments were independently consulted.",
        ["cand-10937", "cand-4979", "cand-1800", "cand-0342", "cand-10938", "cand-3403"], relation=True,
        footnote_markers=[3, 4], extra={"cited_material_not_independently_consulted": True,
            "cross_reference_segments": [{"segment_id": CHP3_TREATISE, "source_line_start": 16, "source_line_end": 24}]}),
    make_statement("st-chp20-p400-oratorian-building-history-and-chapel-autonomy", 50, 51, "cand-10940", "cand-10939",
        "hess_documents_showed_oratorian_control_and_patronal_autonomy_at_chiesa_nuova",
        "Haskell says Jacob Hess’s published and analysed documents on the early building history of the Oratorian Chiesa Nuova provide further evidence of the Order’s control of its construction and show that patrons of individual chapels tried to maintain autonomy over decoration.",
        "Haskell reporting Hess", "authorial report of documentary research",
        "The documents and Hess’s cited publication were not independently consulted. The sentence describes attempted autonomy, not complete control by patrons.",
        ["cand-10940", "cand-10939", "cand-5450", "cand-3402", "cand-10941"], relation=True,
        footnote_markers=[5], extra={"cited_material_not_independently_consulted": True,
            "ocr_corrections": [{"source_line": 51, "ocr": "autonomy-that", "print": "autonomy—that", "basis": "CHP-20Postscript.pdf physical page 5"}]}),
    make_statement("st-chp20-p400-cesi-self-restraint-and-1581-letter", 51, 51, "cand-0640", "cand-3402",
        "cesi_self_restraint_gave_oratorians_control_and_is_contrasted_with_farnese",
        "Haskell attributes Oratorian control in part to the exceptional self-restraint of Cardinal Cesi, contrasting it with Cardinal Farnese’s treatment of the Jesuits, and quotes Cesi’s 1581 letter saying he would accept whatever satisfied the Oratorian fathers rather than choose a design to suit his own taste.",
        "Haskell quoting Cardinal Cesi", "author-attributed interpretation and embedded letter quotation",
        "Haskell presents the control explanation as his interpretation. The letter is quoted second-hand; its leading Oratorian addressee is unnamed, and footnote 6 cites Bonadonna Russo, 1968, p. 135.",
        ["cand-0640", "cand-3402", "cand-10942", "cand-0995", "cand-3403"], relation=True,
        footnote_markers=[6], extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p400-bonadonna-russo-longhi-and-angelo-cesi", 52, 53, "cand-10943", "cand-1427",
        "bonadonna_russo_qualifies_cesi_intervention_in_longhi_appointment",
        "Haskell says Maria Teresa Bonadonna Russo publishes Cesi’s letter and similar correspondence, but also notes her view that the Cardinal probably intervened in appointing Martino Longhi the Elder as the church’s second architect; Monsignor Angelo Cesi, identified as the Cardinal’s brother, was less accommodating.",
        "Haskell reporting Bonadonna Russo", "authorial report of a qualified scholarly interpretation",
        "The appointment’s connection to the Cardinal is explicitly probable. Reuse the indexed Cardinal Cesi and Longhi candidates but keep Monsignor Angelo Cesi source-specific until S3 alignment. Footnote 7 cites Bonadonna Russo, 1967 and 1968.",
        ["cand-10943", "cand-10944", "cand-0640", "cand-1427", "cand-10945", "cand-5450"], relation=True,
        footnote_markers=[7], extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p400-cassiano-family-inventory-discovery", 55, 55, "cand-10946", "cand-2036",
        "newly_reported_1689_and_1695_inventories_document_cassiano_family_collections",
        "Haskell reports a recent discovery, referred to in print but not yet published, of inventories dated 1689 and 1695 concerning the collections of Cassiano dal Pozzo’s brother and heir Carlo Antonio and Carlo Antonio’s son Gabriele.",
        "Haskell", "authorial report of unpublished documentary discovery",
        "The sentence does not clearly pair each date with one collection. The inventories were not independently consulted; footnote 8 points to Brejon, p. 94, note 21, and Marcello del Piazzo’s 1969 discovery.",
        ["cand-10946", "cand-2036", "cand-2035", "cand-10947", "cand-10954"], relation=True,
        footnote_markers=[8], extra={"cited_material_not_independently_consulted": True,
            "cross_reference_segments": [{"segment_id": CHP4_CASSIANO, "source_line_start": 232, "source_line_end": 308}]}),
    make_statement("st-chp20-p400-french-pictures-in-inventories", 55, 55, "cand-10948", "cand-10946",
        "only_french_pictures_from_the_inventories_had_been_studied_in_detail",
        "Haskell says only the French pictures recorded in these inventories had been studied in detail.",
        "Haskell", "authorial status report about scholarship",
        "This limits the reported research coverage; it does not imply the inventories contain only French pictures. Footnote 9 is reproduced on source line 57.",
        ["cand-10948", "cand-10946"], relation=False, footnote_markers=[9]),
    make_statement("st-chp20-p400-cassiano-1626-journey-and-portrait-preference", 55, 56, "cand-10949", "cand-10950",
        "harris_article_illuminated_cassianos_taste_through_1626_spain_journey_and_portrait_comparison",
        "Haskell says an article on Cassiano’s 1626 journey to Spain illuminated his early taste: Cassiano reportedly disapproved of a now-lost portrait of Cardinal Barberini by the young Velasquez as melancholy and severe, preferring another now-lost portrait by Juan van der Hamen.",
        "Haskell reporting an article cited as Harris, 1970", "source-attributed art-historical interpretation",
        "The article is cited but not independently consulted. Preserve the quoted Italian description, the two works as distinct and lost, and the Cardinal’s identity as unresolved.",
        ["cand-10949", "cand-10950", "cand-2036", "cand-10951", "cand-5915", "cand-2709", "cand-10952", "cand-1287"], relation=True,
        footnote_markers=[10], extra={"cited_material_not_independently_consulted": True,
            "cross_reference_segments": [{"segment_id": CHP4_CASSIANO, "source_line_start": 232, "source_line_end": 308}]}),
    make_statement(OPEN_400, 56, 56, "cand-10953", "cand-2036",
        "only_part_of_cassianos_journal_was_published_full_sentence_open_across_page",
        "Haskell begins to say that only the section of Cassiano’s journal describing his visit to a destination is published in full; the destination and sentence continue on p.401.",
        "Haskell", "authorial report of publication scope",
        "This segment ends at ‘the’; keep the destination unresolved until the p.401 continuation is reviewed.",
        ["cand-10953", "cand-2036"], relation=False,
        extra={"open_across_segment": True, "continues_in_segment": P401,
            "cross_reference_segments": [{"segment_id": CHP4_CASSIANO, "source_line_start": 232, "source_line_end": 308}]}),
]

statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    sid = row["statement_id"]
    if sid in statement_ids:
        raise SystemExit(f"statement ID already exists: {sid}")
    statement_ids.add(sid)
    if row["original_quote"] not in text400:
        raise SystemExit(f"statement quote not contained in p.400 segment: {sid}")
    for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate {cid}")
    for ref in row["qualifiers"].get("cross_reference_segments", []):
        if ref["segment_id"] not in segment_by_id:
            raise SystemExit(f"statement references missing segment {ref['segment_id']}")

coverage_by_id[P400]["disposition"] = "reviewed"
coverage_by_id[P400]["migration_status"] = "partial"
coverage_by_id[P400]["source_line_ranges"] = "L47-57"
coverage_by_id[P400]["note"] = (
    "Printed p.400 (PDF physical page 5) read against the page image. ‘Chapter 4’ is a postscript update heading; the prose remains part of the second-edition postscript. "
    "Processes Enggass, Casale/Ottonelli, Hess and Oratorian patronage, Cesi correspondence, and Cassiano dal Pozzo inventory and portrait updates. "
    "The final journal-publication sentence ends at ‘the’ and continues on p.401; footnotes 1-8 link to the queued notes segment, while p.400 footnotes 9-10 are transcribed at L57. "
    "Page-image OCR corrections are recorded on statements."
)

files_to_backup = [candidate_path, mention_path, statement_path, coverage_path]
if args.apply:
    for path in files_to_backup:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, [*mentions, *new_mentions])
    write_jsonl(statement_path, [*statements, *new_statements])
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied p.400 S2 migration; backups use suffix {BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print(f"p.400 is partial; open statement {OPEN_400} continues on p.401")
    print("p.400 heading ‘Chapter 4’ is treated as an update heading within the second-edition postscript")
