#!/usr/bin/env python3
"""Controlled S2 migration for printed p.398 and the opening of chapter 3."""

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
P397 = "chp-20:20_CHP-20Postscript:l14-24"
P398 = "chp-20:20_CHP-20Postscript:l26-36"
P399 = "chp-20:20_CHP-20Postscript:l38-44"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
PLATE_LIST = "front-matter:00_05_List_of_Plates:l32-65"
OPEN_397 = "st-chp20-p397-agucchi-career-open"
CLOSE_398 = "st-chp20-p398-agucchi-career-closure"
BACKUP_SUFFIX = ".bak-s2-chp20-p398-20261004"

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

for sid in (P397, P398, P399, NOTES, PLATE_LIST):
    if sid not in segment_by_id:
        raise SystemExit(f"missing registered segment: {sid}")
if (coverage_by_id[P397]["disposition"], coverage_by_id[P397]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.397 must be reviewed/partial before closure")
if (coverage_by_id[P398]["disposition"], coverage_by_id[P398]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.398 should be queued/pending: {coverage_by_id[P398]}")
if segment_by_id[P398]["sha256"] != "079f6831dff0c7d1965b26066855e385170a316566f6670579fc31bee6214c76":
    raise SystemExit("registered p.398 S0 hash changed")
if segment_by_id[P398]["asset_sha256"] != EXPECTED_SOURCE:
    raise SystemExit("p.398 source asset hash is inconsistent")
if P399 not in coverage_by_id or coverage_by_id[P399]["disposition"] != "queued":
    raise SystemExit("p.399 continuation segment is not queued")
if NOTES not in coverage_by_id or coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("postscript notes are not queued for later processing")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text398 = "\n".join(source_lines[segment_by_id[P398]["line_start"] - 1 : segment_by_id[P398]["line_end"]])
if hashlib.sha256(text398.encode("utf-8")).hexdigest() != segment_by_id[P398]["sha256"]:
    raise SystemExit("p.398 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment_by_id[P398]["line_start"], segment_by_id[P398]["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

candidate_specs = [
    ("cand-10891", "Cesare d’Onofrio, 1963 publication cited for Agucchi and Villa Aldobrandini (title unspecified)", "archive", 27,
     "Footnote 1 cites d’Onofrio 1963 for his attribution of the villa description to Agucchi; title and cited pages are not given here."),
    ("cand-10892", "Agucchi’s description of Villa Aldobrandini (Belvedere) at Frascati (text identity unspecified)", "archive", 27,
     "Haskell reports a description attributed to Agucchi by d’Onofrio; no title, manuscript, or repository is supplied."),
    ("cand-10893", "Villa Aldobrandini (Belvedere) at Frascati", "place", 27,
     "The villa is named as the subject of a description; its historical and present spatial extents are not discussed here."),
    ("cand-10894", "Frascati", "place", 27,
     "Place named as the location of Villa Aldobrandini (Belvedere)."),
    ("cand-10895", "Cesare d’Onofrio, 1964 publication cited for Cardinal Aldobrandini’s Bolognese paintings (title unspecified)", "archive", 28,
     "Footnote 2 cites d’Onofrio 1964 for a qualified suggestion about paintings in Cardinal Aldobrandini’s collection; title and cited pages are not given."),
    ("cand-10896", "Cardinal Aldobrandini (identity unspecified in the p.398 passage)", "person", 28,
     "The passage supplies no given name; do not force a match to an indexed Aldobrandini cardinal before S3."),
    ("cand-10897", "Approximately forty Bolognese paintings in Cardinal Aldobrandini’s collection (individual works unspecified)", "work", 28,
     "Haskell reports d’Onofrio’s qualified alternative that Agucchi commissioned or bought this group; the approximate count and group identity remain unresolved."),
    ("cand-10898", "Inventory of Cardinal Aldobrandini’s paintings compiled by Giambattista Agucchi (record identity unspecified)", "archive", 28,
     "Haskell says Agucchi certainly drew up the inventory; no date, title, manuscript locator, or repository is supplied."),
    ("cand-10899", "Erminia and the Shepherds by Lodovico Carracci (version unspecified)", "work", 28,
     "Haskell says Agucchi commissioned the picture; no date, present location, or version identifier is given."),
    ("cand-10900", "Battisti, 1962 publication of Agucchi’s letters about Erminia and the Shepherds (title unspecified)", "archive", 28,
     "Footnote 3 cites Battisti 1962, pages 201–203 and 529–549; author identity and title are unresolved in this passage."),
    ("cand-10901", "Giambattista Agucchi’s programme for Erminia and the Shepherds (document identity unspecified)", "archive", 28,
     "Haskell says Whitfield discovered and analysed a programme for the picture; no manuscript title or locator is given."),
    ("cand-10902", "Whitfield (scholar cited for Agucchi’s programme; identity unresolved)", "person", 28,
     "The source gives only a surname; do not expand it from external or later bibliographic evidence during S2."),
    ("cand-10903", "Whitfield’s publication analysing Agucchi’s programme for Erminia and the Shepherds (title unspecified)", "archive", 28,
     "Footnote 4 cites Whitfield without a title, date, or page locator."),
    ("cand-10904", "Viola (scholar cited on Giambattista Marino’s collecting; identity unresolved)", "person", 29,
     "The source gives only a surname; do not merge with indexed people of the same surname during S2."),
    ("cand-10905", "Viola’s study of Giambattista Marino’s collecting and approach to art (title unspecified)", "archive", 29,
     "Footnote 5 cites Viola without a title, date, or page locator."),
    ("cand-10906", "Baschet (scholar or editor cited for documents on Guido Bentivoglio; identity unresolved)", "person", 30,
     "The source supplies only a surname; the role as publisher is reported by Haskell."),
    ("cand-10907", "Baschet’s 1861 and 1862 published documents on Guido Bentivoglio (titles and document identities unspecified)", "archive", 30,
     "Haskell says a series of documents was published by Baschet in 1861 and 1862; the documents and publication were not consulted."),
    ("cand-10908", "1969 symposium on Jesuits and the arts at Fordham University", "event", 32,
     "Haskell dates the symposium to 1969; its exact title and proceedings identifier are not supplied in this passage."),
    ("cand-10909", "Fordham University", "institution", 32,
     "Named as the venue of the 1969 symposium."),
    ("cand-10910", "Wittkower’s published contribution on Jesuit spiritual stewardship and church representation (title unspecified)", "archive", 33,
     "Footnote 7 cites Wittkower and Jaffé; the exact publication corresponding to the quoted suggestion is not identified here."),
    ("cand-10911", "Francis Haskell’s paper on conflicts between Jesuits and princely patrons at the 1969 symposium (title unspecified)", "archive", 34,
     "Haskell refers to his own paper; title and proceedings pages are not supplied here."),
    ("cand-10912", "James Ackerman", "person", 35,
     "Named as the scholar who investigated sources for the Gesù; identity is left for S3 alignment."),
    ("cand-10913", "James Ackerman’s investigation of the sources of the Gesù (publication unspecified)", "archive", 35,
     "The passage summarizes Ackerman’s two-camp interpretation; title and publication details are not given here."),
    ("cand-10914", "Borgia (Jesuit) camp in Ackerman’s account of Gesù architecture", "term", 35,
     "The bracketed gloss identifies this camp as Jesuit; do not merge it with the Borgia family."),
    ("cand-10915", "Farnese camp under Cardinal Alessandro Farnese in Ackerman’s account of Gesù architecture", "term", 35,
     "A camp or faction in Ackerman’s account, not a separate formal institution."),
    ("cand-10916", "Sangallesque architectural tradition", "term", 35,
     "Named as the architectural tradition associated with Ackerman’s Borgia/Jesuit camp."),
    ("cand-10917", "Princely patrons in disputes over Jesuit church architecture and decoration", "term", 34,
     "A role-based group in Haskell’s summary; no individual patrons are named in this passage."),
    ("cand-10918", "Jesuit churches discussed in Haskell’s chapter 3 (individual churches unspecified)", "place", 33,
     "The passage refers to churches collectively; do not equate this group with the Gesù alone."),
    ("cand-10919", "Religious Orders discussed in relation to the arts", "term", 32,
     "A general category in the opening sentence; the passage singles out the Jesuits but does not name the other Orders."),
]

existing_keys = {(row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold()) for row in candidates}
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
        "candidate_source_ref": f"{P398}#L{line_number}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

mention_specs = [
    ("cand-0018", "his taste in art", 27, 27, "Closes the p.397 Agucchi sentence; coreference to Giambattista Agucchi.", 0),
    ("cand-10854", "D’Onofrio", 27, 27, "Reuse the p.396 Cesare d’Onofrio candidate.", 0),
    ("cand-10891", "D’Onofrio has attributed to him", 27, 27, "The footnote identifies the cited 1963 publication; the title is unspecified.", 0),
    ("cand-0018", "him", 27, 27, "Coreference to Giambattista Agucchi.", 0),
    ("cand-10892", "a remarkably fresh, as well as detailed, description of the Villa\nAldobrandini (Belvedere) at Frascati", 27, 28, "Description attributed to Agucchi by d’Onofrio.", 0),
    ("cand-10893", "Villa\nAldobrandini (Belvedere)", 27, 28, "Named architectural place.", 0),
    ("cand-10894", "Frascati", 28, 28, "Place containing the named villa.", 0),
    ("cand-10895", "has also suggested", 27, 28, "The p.398 footnote cites d’Onofrio 1964 for this separately qualified suggestion.", 0),
    ("cand-0018", "it was Agucchi", 28, 28, "Reuse the existing Giambattista Agucchi candidate.", 0),
    ("cand-10897", "the forty or so Bolognese paintings", 28, 28, "Approximate group; no individual paintings are named.", 0),
    ("cand-10896", "Cardinal Aldobrandini’s collection", 28, 28, "The cardinal’s identity is not explicit in this passage.", 0),
    ("cand-0018", "he certainly drew up", 28, 28, "Coreference to Giambattista Agucchi; Haskell states the inventory attribution confidently.", 0),
    ("cand-10898", "the inventory", 28, 28, "Inventory of the paintings in Cardinal Aldobrandini’s collection.", 0),
    ("cand-3499", "Battisti", 28, 28, "Reuse the existing surname-only bibliographic person candidate; identity remains unresolved.", 0),
    ("cand-10900", "published a number of vivid, even if sometimes recondite, letters", 28, 28, "The p.398 note identifies the cited 1962 publication, not its title.", 0),
    ("cand-0018", "he wrote to a friend", 28, 28, "Coreference to Agucchi as the letter writer.", 0),
    ("cand-10899", "an Erminia and the Shepherds", 28, 28, "Named painting commissioned by Agucchi from Lodovico Carracci.", 0),
    ("cand-0580", "Lodovico Carracci", 28, 28, "Reuse the existing Lodovico Carracci candidate.", 0),
    ("cand-0018", "he had commissioned", 28, 28, "Coreference to Agucchi as reported by Haskell.", 0),
    ("cand-10901", "Agucchi’s ‘programme’", 28, 28, "A distinct document or interpretive programme for the named picture.", 0),
    ("cand-10902", "Whitfield", 28, 28, "Surname-only person candidate; identity unresolved.", 0),
    ("cand-10903", "Whitfield later discovered and analysed Agucchi’s ‘programme’ for this picture", 28, 28, "Cited publication is unspecified; the sentence reports Whitfield’s discovery and analysis.", 0),
    ("cand-10899", "this picture", 28, 28, "Coreference to Erminia and the Shepherds.", 0),
    ("cand-1548", "Giambattista Marino", 29, 29, "Reuse the indexed Giambattista Marino candidate.", 0),
    ("cand-4462", "The collecting and approach to art of Giambattista Marino", 29, 29, "Reuse the existing open Marino collecting candidate; contents and scope remain unspecified.", 0),
    ("cand-10904", "Viola", 30, 30, "Surname-only scholar candidate; identity unresolved.", 0),
    ("cand-10905", "studied by\nViola", 29, 30, "Cited study on Marino’s collecting; publication details are unspecified.", 0),
    ("cand-0291", "Guido Bentivoglio", 30, 30, "Reuse the indexed Cardinal Guido Bentivoglio candidate.", 0),
    ("cand-4964", "Cardinal Borghese", 30, 30, "Reuse the surname-only artistic-context candidate; identity remains unresolved at S2.", 0),
    ("cand-10907", "series of documents published by Baschet in 1861 and 1862", 30, 30, "Haskell reports the documentary series and publication dates.", 0),
    ("cand-10906", "Baschet", 30, 30, "Surname-only person candidate; identity unresolved.", 0),
    ("cand-0958", "Van Dyck", 30, 30, "Reuse the indexed Anthony van Dyck candidate.", 0),
    ("cand-4885", "Van Dyck’s magnificent portrait of the Cardinal", 30, 30, "The plate list identifies Plate 4a as Cardinal Bentivoglio; ‘the Cardinal’ refers to Guido Bentivoglio, not the Borghese patron.", 0),
    ("cand-0291", "the Cardinal", 30, 30, "Local identity resolved by the linked plate list: Cardinal Guido Bentivoglio.", 0),
    ("cand-4885", "Plate 4a", 30, 30, "Cross-reference to the portrait’s plate entry in the front-matter list.", 0),
    ("cand-10919", "various Orders", 32, 32, "General category of religious Orders discussed in relation to art.", 0),
    ("cand-3403", "the Jesuits", 32, 32, "Reuse the existing typed Jesuit institution candidate.", 0),
    ("cand-10908", "a symposium was devoted to this theme", 32, 32, "Symposium on Jesuits and the arts at Fordham in 1969.", 0),
    ("cand-10909", "Fordham\nUniversity", 32, 33, "Named venue of the symposium.", 0),
    ("cand-7473", "New York", 33, 33, "Reuse the existing place candidate.", 0),
    ("cand-10908", "1969", 33, 33, "Date of the symposium.", 0),
    ("cand-10910", "Wittkower’s suggestion", 33, 33, "The cited suggestion is associated with the symposium’s published papers; exact title is unresolved.", 0),
    ("cand-2818", "Wittkower", 33, 33, "Reuse the indexed Wittkower candidate; identity alignment remains for S3.", 0),
    ("cand-3403", "their spiritual stewardship", 33, 33, "Coreference to the Jesuits.", 0),
    ("cand-3403", "they had a firm and measurable hold on what they wanted to have represented", 33, 33, "Coreference to the Jesuits in Wittkower’s quoted proposition.", 0),
    ("cand-10918", "their churches", 33, 34, "Collective church spaces; no individual church is meant in the general clause.", 0),
    ("cand-10911", "my own paper", 33, 33, "Haskell’s contribution to the symposium; title unspecified.", 0),
    ("cand-3403", "the conflicts that repeatedly arose between the Jesuits", 33, 33, "Haskell’s own account of conflicts with princely patrons.", 0),
    ("cand-10917", "their princely patrons", 33, 33, "Role-based group; no individuals are named.", 0),
    ("cand-3403", "successive\nJesuit leaders", 33, 34, "Collective reference to leaders within the Jesuit institution.", 0),
    ("cand-10912", "James Ackerman", 34, 34, "New person candidate named in the chapter’s account.", 0),
    ("cand-10913", "his investigation of the sources of the Gesù", 34, 34, "Ackerman’s study of the church’s sources; title unspecified.", 0),
    ("cand-5200", "the Gesù", 34, 34, "Reuse the existing Church of the Gesù place candidate.", 0),
    ("cand-10914", "a Borgia [i.e. Jesuit] camp", 35, 35, "The source explicitly glosses Borgia as Jesuit; not the Borgia family.", 0),
    ("cand-10916", "the Sangallesque architectural tradition", 35, 35, "Named architectural tradition.", 0),
    ("cand-10915", "a Farnese camp", 35, 35, "Faction described by Ackerman, under Cardinal Alessandro Farnese.", 0),
    ("cand-0995", "Alessandro Cardinal Farnese", 35, 35, "Reuse the indexed Cardinal Alessandro Farnese candidate.", 0),
    ("cand-2775", "Vignola", 35, 35, "Reuse the indexed Giacomo Barozzi da Vignola candidate.", 0),
    ("cand-5006", "The\nFarnese", 35, 36, "Reuse the existing Farnese family candidate; collective family reference.", 0),
    ("cand-10917", "the princes they were", 36, 36, "Role-based characterization of the Farnese in Ackerman’s quoted account.", 0),
    ("cand-5200", "an elegant avant-garde building", 36, 36, "The unnamed building in Ackerman’s account is the Church of the Gesù.", 0),
    ("cand-10911", "But, in a persuasive", 36, 36, "Opening of Haskell’s own assessment, continued on p.399.", 0),
]

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p398-{ordinal:03d}"
    if mention_id in existing_mention_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention target missing or not open: {cid}")
    lower = line_offset[first]
    upper = line_offset[last] + len(source_lines[last - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text398.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(f"surface not found on p.398 lines {first}-{last}: {surface!r}")
        cursor = found + 1
    new_mentions.append({
        "mention_id": mention_id, "segment_id": P398, "candidate_id": cid,
        "surface_form": surface, "start_char": str(found),
        "end_char": str(found + len(surface)), "note": note,
    })
    existing_mention_ids.add(mention_id)

intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
                   for row in [*mentions, *new_mentions] if row["segment_id"] == P398)
for index, left in enumerate(intervals):
    for right in intervals[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing p.398 mention spans: {left[2]} / {right[2]}")


def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer,
                   qualification, candidate_ids, relation=False, footnote_marker=None, extra=None):
    qualifiers = {
        "source_line_start": first, "source_line_end": last,
        "printed_page": 398, "pdf_physical_page": 3,
        "claim": claim, "speaker": speaker, "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation,
    }
    if footnote_marker is not None:
        note_line = {1: 221, 2: 221, 3: 222, 4: 222, 5: 223, 6: 223, 7: 224}[footnote_marker]
        qualifiers.update({
            "footnote_marker": footnote_marker,
            "footnote_text_pending": True,
            "footnote_segment": NOTES,
            "footnote_refs": [{"marker": footnote_marker, "segment_id": NOTES, "source_line": note_line}],
            "footnote_statement_ids": [],
            "footnote_body_link_status": "pending",
        })
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id, "segment_id": P398,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[first - 1:last]),
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "origin": "book",
    }


new_statements = [
    make_statement(CLOSE_398, 27, 27, "cand-0018", None,
        "haskell_qualified_update_on_agucchis_early_career_closed",
        "Haskell completes the p.397 sentence by saying that readers now know more about Agucchi’s taste in art than about that of anyone else of the period.",
        "Haskell", "authorial transition and retrospective assessment",
        "This closes the p.397 statement; it is Haskell’s assessment of recent scholarship, not a claim that every aspect of Agucchi’s career is settled.",
        ["cand-0018"], relation=False,
        extra={"cross_reference_segments": [P397], "closes_statement_ids": [OPEN_397]}),
    make_statement("st-chp20-p398-donofrio-agucchi-villa-description", 27, 27, "cand-10854", "cand-10892",
        "donofrio_attributed_villa_aldobrandini_description_to_agucchi",
        "Haskell says d’Onofrio attributed to Agucchi a remarkably fresh and detailed description of Villa Aldobrandini (Belvedere) at Frascati.",
        "Haskell reporting d’Onofrio", "source-attributed architectural description",
        "The description, its manuscript or publication, and d’Onofrio’s cited work were not independently consulted; no title or repository is supplied.",
        ["cand-10854", "cand-10891", "cand-0018", "cand-10892", "cand-10893", "cand-10894"],
        relation=True, footnote_marker=1,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p398-agucchi-aldobrandini-paintings", 28, 28, "cand-0018", "cand-10897",
        "donofrio_suggested_agucchi_may_have_commissioned_or_bought_bolognese_paintings",
        "Haskell reports d’Onofrio’s suggestion that Agucchi commissioned or bought approximately forty Bolognese paintings in Cardinal Aldobrandini’s collection.",
        "Haskell reporting d’Onofrio", "qualified alternative about a painting group",
        "Haskell says the suggestion is plausible but lacks conclusive evidence. Preserve the alternative ‘commissioned or bought’, the approximate count, and the unnamed Cardinal Aldobrandini; none is resolved here.",
        ["cand-0018", "cand-10895", "cand-10896", "cand-10897"],
        relation=True, footnote_marker=2,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p398-agucchi-inventory", 28, 28, "cand-0018", "cand-10898",
        "agucchi_compiled_inventory_of_cardinal_aldobrandinis_paintings",
        "Haskell states that Agucchi certainly drew up the inventory of the approximately forty Bolognese paintings in Cardinal Aldobrandini’s collection.",
        "Haskell", "authorial report of an inventory",
        "The inventory itself was not consulted. The collection’s scope and the Cardinal’s identity remain unspecified in this passage.",
        ["cand-0018", "cand-10896", "cand-10897", "cand-10898"],
        relation=True, footnote_marker=2),
    make_statement("st-chp20-p398-battisti-agucchi-carracci-letters", 28, 28, "cand-3499", "cand-10900",
        "battisti_published_agucchis_letters_about_a_commissioned_carracci_painting",
        "Haskell says Battisti published vivid, sometimes recondite letters that Agucchi wrote to a friend about an Erminia and the Shepherds he had commissioned from Lodovico Carracci.",
        "Haskell reporting Battisti", "source-reported correspondence and commission",
        "The letters and Battisti’s publication were not independently consulted. The commission is reported through Haskell’s summary; no date, version, or present location is established.",
        ["cand-3499", "cand-10900", "cand-0018", "cand-10899", "cand-0580"],
        relation=True, footnote_marker=3,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p398-whitfield-agucchi-programme", 28, 28, "cand-10902", "cand-10901",
        "whitfield_discovered_and_analysed_agucchis_programme_for_the_painting",
        "Haskell says Whitfield later discovered and analysed Agucchi’s programme for Erminia and the Shepherds.",
        "Haskell reporting Whitfield", "source-reported documentary interpretation",
        "The programme and Whitfield’s publication were not independently consulted; the programme’s title, material form, and repository are not given.",
        ["cand-10902", "cand-10903", "cand-10901", "cand-10899", "cand-0018"],
        relation=True, footnote_marker=4,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p398-marino-viola-study", 29, 29, "cand-10904", "cand-10905",
        "viola_studied_giambattista_marinos_collecting_and_approach_to_art",
        "Haskell says Viola studied Giambattista Marino’s collecting and approach to art.",
        "Haskell reporting scholarship", "source-reported research scope",
        "The cited work is not independently consulted; Viola’s identity and the scope of Marino’s collection remain unresolved.",
        ["cand-10904", "cand-10905", "cand-1548", "cand-4462"],
        relation=True, footnote_marker=5,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p398-bentivoglio-borghese-baschet", 30, 30, "cand-10906", "cand-10907",
        "baschet_published_documents_on_bentivoglios_advisory_role_for_cardinal_borghese",
        "Haskell says published documents from 1861 and 1862, issued by Baschet, provide an exceptionally vivid view of Guido Bentivoglio’s role as artistic adviser and entrepreneur for Cardinal Borghese.",
        "Haskell reporting Baschet’s documents", "source-reported advisory and entrepreneurial role",
        "The documents were not independently consulted. Cardinal Borghese’s identity remains unresolved here; the passage does not establish which individual actions or projects the documents record.",
        ["cand-10906", "cand-10907", "cand-0291", "cand-4964"],
        relation=True, footnote_marker=6,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p398-bentivoglio-portrait-photograph", 30, 30, "cand-9423", "cand-4885",
        "haskell_replaced_first_edition_photograph_of_van_dyck_bentivoglio_portrait_after_cleaning",
        "Haskell says Van Dyck’s portrait of Cardinal Guido Bentivoglio had recently been cleaned and he substituted a new photograph for the one in the first edition, Plate 4a.",
        "Haskell", "edition and image documentation update",
        "The plate list identifies Plate 4a as Van Dyck’s Cardinal Bentivoglio. This statement concerns the photograph used in the book, not a change to the identity or attribution of the painting.",
        ["cand-9423", "cand-0958", "cand-0291", "cand-4885"], relation=False,
        extra={"cross_reference_segments": [PLATE_LIST]}),
    make_statement("st-chp20-p398-fordham-symposium", 32, 33, None, "cand-10908",
        "1969_fordham_symposium_on_jesuits_and_arts_published_relevant_papers",
        "Haskell says the Jesuits continued to attract widespread attention, and that a 1969 symposium on this theme was held at Fordham University in New York. He says all papers were published and some directly concern his chapter.",
        "Haskell", "authorial survey of later scholarship",
        "This records Haskell’s summary; the symposium and proceedings were not independently consulted. The OCR footnote numbering and names will be checked when the notes segment is processed.",
        ["cand-3403", "cand-10919", "cand-10908", "cand-10909", "cand-7473"],
        relation=False, footnote_marker=7,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p398-wittkower-jesuit-church-representation", 33, 33, "cand-2818", "cand-3403",
        "wittkower_proposed_jesuits_had_measurable_control_over_church_representation",
        "Haskell quotes Wittkower as saying that, whatever the path from spiritual stewardship to artistic sublimation, Jesuits had a firm and measurable hold on what they wanted represented in their churches.",
        "Wittkower, quoted and qualified by Haskell", "quoted interpretation with authorial reservation",
        "Haskell says he can accept this proposition only with great reservations. Do not recast the quotation as an established account of Jesuit control; the publication is not independently consulted.",
        ["cand-2818", "cand-10910", "cand-3403", "cand-10918"],
        relation=True, footnote_marker=7,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p398-haskell-jesuit-princely-patron-conflicts", 33, 34, "cand-9423", "cand-10911",
        "haskell_paper_described_conflicts_between_jesuits_and_princely_patronage",
        "Haskell says that in his own paper he tried again to demonstrate recurring conflicts between Jesuits and their princely patrons over church architecture and decoration, and stressed that Jesuit leaders could differ radically among themselves on artistic issues.",
        "Haskell", "authorial research summary",
        "This is Haskell’s account of his argument, not an independent survey of all Jesuit leadership or patronage disputes. No individual princely patrons or churches are identified.",
        ["cand-9423", "cand-10911", "cand-3403", "cand-10917", "cand-10918"], relation=True),
    make_statement("st-chp20-p398-ackerman-gesu-camps", 35, 36, "cand-10912", "cand-10913",
        "ackerman_described_borgia_jesuit_and_farnese_camps_in_gesu_design",
        "Haskell says Ackerman’s investigation of the Gesù’s sources identified a Borgia, explicitly glossed as Jesuit, camp committed to the Sangallesque tradition and a Farnese camp under Cardinal Alessandro Farnese supporting Vignola. In Ackerman’s quoted account, the Farnese wanted an elegant avant-garde building with a Farnese look and ultimately prevailed through their resources and lavish giving.",
        "Haskell reporting and quoting Ackerman", "source-attributed account of competing architectural camps",
        "The bracketed gloss is Haskell’s clarification; the Borgia camp is not the Borgia family. ‘The Farnese’ refers collectively to the Farnese family/camp. The quote ends on p.398; Haskell’s next evaluative sentence continues on p.399.",
        ["cand-10912", "cand-10913", "cand-5200", "cand-10914", "cand-10916", "cand-10915", "cand-0995", "cand-2775", "cand-5006", "cand-10917"],
        relation=True, extra={"cross_reference_segments": [P399],
            "ocr_corrections": [
                {"source_line": 224, "ocr": "Jaffe", "print": "Jaffé", "basis": "CHP-20Postscript.pdf physical page 3 footnote"},
                {"source_line": 223, "ocr": "6 Viola", "print": "5 Viola", "basis": "CHP-20Postscript.pdf physical page 3 footnote"},
            ]}),
    make_statement("st-chp20-p398-haskell-farnese-evaluation-open", 36, 36, "cand-9423", None,
        "haskell_opened_a_qualified_assessment_of_ackermans_account",
        "Haskell begins a qualified assessment of Ackerman’s account, but the sentence continues onto p.399.",
        "Haskell", "authorial evaluation, cross-page continuation",
        "Only the opening words are present on p.398; no evaluative conclusion is inferred.",
        ["cand-9423", "cand-10913", "cand-5006"], relation=False,
        extra={"cross_reference_segments": [P399], "open_across_segment": True}),
]

if OPEN_397 not in statement_by_id:
    raise SystemExit(f"missing open p.397 statement: {OPEN_397}")
open_statement = statement_by_id[OPEN_397]
open_qualifiers = open_statement.get("qualifiers", {})
if not open_qualifiers.get("open_across_segment"):
    raise SystemExit("p.397 Agucchi sentence is not marked open")
if CLOSE_398 in statement_by_id:
    raise SystemExit(f"closure statement already exists: {CLOSE_398}")

statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    sid = row["statement_id"]
    if sid in statement_ids:
        raise SystemExit(f"statement ID already exists: {sid}")
    statement_ids.add(sid)
    if row["original_quote"] not in text398:
        raise SystemExit(f"statement quote not contained in p.398 segment: {sid}")
    for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate {cid}")
    for ref_id in row["qualifiers"].get("cross_reference_segments", []):
        if ref_id not in segment_by_id:
            raise SystemExit(f"statement references missing segment {ref_id}")

open_qualifiers["open_across_segment"] = False
open_qualifiers["closed_by_segment"] = P398
open_qualifiers["closed_by_statement_id"] = CLOSE_398
open_qualifiers["cross_page_quote_continuation"] = (
    "more about his taste in art than we do about that of anyone else of the time"
)
open_qualifiers["qualification"] = (
    "The p.397 Agucchi transition is completed on p.398. Haskell says readers know more about Agucchi’s art taste than that of his contemporaries; "
    "this is an authorial assessment of scholarship, not a comprehensive or independently verified biography."
)
open_statement["predicate"] = "haskell_qualified_update_on_agucchis_early_career_closed"
mentions.extend(new_mentions)
statements.extend(new_statements)

coverage_by_id[P397]["migration_status"] = "complete"
coverage_by_id[P397]["note"] = coverage_by_id[P397]["note"] + " The Agucchi sentence was closed against p.398 statement `" + CLOSE_398 + "`."
coverage_by_id[P398]["disposition"] = "reviewed"
coverage_by_id[P398]["migration_status"] = "partial"
coverage_by_id[P398]["source_line_ranges"] = "L27-36"
coverage_by_id[P398]["note"] = (
    "Printed p.398 (PDF physical page 3) read against the page image. Closes p.397’s Agucchi transition; processes the remaining postscript updates and "
    "the opening of chapter 3 through Ackerman’s complete quotation. The final Haskell assessment starts at L36 and continues on p.399, so this segment is partial. "
    "The page image corrects footnote OCR ‘6 Viola’ to ‘5 Viola’ and ‘Jaffe’ to ‘Jaffé’; cited scholarship was not independently consulted."
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
    print("applied p.398 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print(f"closed p.397 statement {OPEN_397} using {CLOSE_398}")
    print("p.398 remains partial because Haskell’s next assessment continues on p.399")
