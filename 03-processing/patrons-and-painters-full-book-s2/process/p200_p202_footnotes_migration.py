"""Controlled S2 migration of the p.200-202 footnotes.

The default run is read-only. OCR stays unchanged; print corrections are
recorded in S2 statement qualifiers. The reversed Plate 30/31 OCR fragment at
L69 is already represented by the front-matter plate list and is not duplicated.
"""
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
SOURCE_REL = "02-sources/02-Markdown/07_CHP-7_sec_v.md"
SOURCE_PATH = ROOT / SOURCE_REL
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
SEGMENT_PATH = TABLES / "segments.jsonl"
NOTE_SEGMENT = "chp-7:07_CHP-7_sec_v:l62-76"
P200_SEGMENT = "chp-7:07_CHP-7_sec_v:l9-18"
P201_SEGMENT = "chp-7:07_CHP-7_sec_v:l42-55"
P202_SEGMENT = "chp-7:07_CHP-7_sec_v:l57-60"
BACKUP_SUFFIX = ".bak-s2-chp7-p200-p202-notes-20260930"
NEW_CANDIDATE_IDS = [f"cand-{n:04d}" for n in range(7347, 7357)]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_rows = read_jsonl(SEGMENT_PATH)
segments = {row["segment_id"]: row for row in segment_rows}
if len(segments) != len(segment_rows):
    raise SystemExit("segments.jsonl contains duplicate IDs")
note_meta = segments.get(NOTE_SEGMENT)
if not note_meta or note_meta["source_file"] != SOURCE_REL:
    raise SystemExit(f"missing or unexpected segment: {NOTE_SEGMENT}")
if (note_meta["line_start"], note_meta["line_end"]) != (62, 76):
    raise SystemExit("target segment bounds changed; review before migration")
if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != note_meta["asset_sha256"]:
    raise SystemExit("source asset fingerprint changed; rebuild segments and review")

candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
mention_fields, mention_rows = read_csv(MENTION_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
statement_rows = read_jsonl(STATEMENT_PATH)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

if any(row["segment_id"] == NOTE_SEGMENT for row in mention_rows):
    raise SystemExit("mentions already exist for the note segment; inspect before rerunning")
if any(row["segment_id"] == NOTE_SEGMENT for row in statement_rows):
    raise SystemExit("statements already exist for the note segment; inspect before rerunning")
if coverage_by_id.get(NOTE_SEGMENT, {}).get("disposition") != "queued":
    raise SystemExit("expected queued note coverage; inspect before rerunning")
if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) != 7346:
    raise SystemExit("candidate ID sequence changed; allocate IDs from current table")
for segment_id in (P200_SEGMENT, P201_SEGMENT, P202_SEGMENT):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing related coverage row: {segment_id}")


def candidate(cid, name, typ, detail, line):
    return {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": typ,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTE_SEGMENT}#L{line}",
    }


new_candidates = [
    candidate(
        "cand-7347",
        "Archivio Storico per la Province Napoletane (1906), p. 453; article unspecified",
        "archive",
        "Periodical citation in Haskell's p.200 footnote 5 for the report that 'Binchs' was back in Naples in 1719; cited page not independently read.",
        67,
    ),
    candidate(
        "cand-7348",
        "Ferdinando Bologna, Francesco Solimena (Napoli, 1958)",
        "archive",
        "Bibliographic candidate cited as Bologna, p.191 in p.200 footnote 4; the cited page is not independently read, and the bibliography segment remains for S2 review.",
        66,
    ),
    candidate(
        "cand-7349",
        "Ilg, work on Prince Eugene (Wien, 1889; title as transcribed in bibliography)",
        "archive",
        "Cited as Ilg, passim in p.201 footnote 2; bibliographic title is a locator from the OCR bibliography and awaits that segment's S2 review.",
        71,
    ),
    candidate(
        "cand-7350",
        "H. Tietze, article on Prince Eugene, pp. 891-907 (1933; title as transcribed in bibliography)",
        "archive",
        "Cited in p.201 footnote 2; the bibliography supplies a candidate title, but the cited article and pages were not independently read.",
        71,
    ),
    candidate(
        "cand-7351",
        "A. Baudi di Vesme, 1886 study of Carlo Emanuele III's acquisition of Prince Eugene's picture collection",
        "archive",
        "Cited at p.201 footnote 2, pp.161-256; the bibliography supplies a title candidate, but the cited article was not independently read.",
        71,
    ),
    candidate(
        "cand-7352",
        "H. Ritschl, catalogue of the Harrach picture gallery in Vienna",
        "archive",
        "Cited as Ritschl, passim in p.200 footnote 7; title-level identification follows the bibliography OCR, with date and cited passages unverified.",
        68,
    ),
    candidate(
        "cand-7353",
        "Carlo Emanuele III of Savoy",
        "person",
        "Named in Haskell's p.201 footnote 2 as the buyer of much of Prince Eugene's picture collection; identity is not aligned with other candidates here.",
        71,
    ),
    candidate(
        "cand-7354",
        "British fleet in the Mediterranean (as described in Haskell's p.200 footnote)",
        "institution",
        "Military organization named only in the footnote's description of Admiral Byng's command from 1718; no formal unit name is supplied.",
        67,
    ),
    candidate(
        "cand-7355",
        "Count Harrach's surviving picture collection",
        "",
        "Collection mentioned as evidence of Harrach's patronage; the current taxonomy has no collection type and the specific collection identity is unresolved.",
        68,
    ),
    candidate(
        "cand-7356",
        "Neapolitan art (Haskell's patronage category)",
        "term",
        "Cultural/artistic category named in p.200 footnote 7; retain the wording and scope of Haskell's claim.",
        68,
    ),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate ID already exists")


# line, source-exact surface, candidate ID, note
mention_specs = [
    (63, "Soprani", "cand-5160", "Citation to the two-volume Soprani work; footnote 1 gives vol. I, p.120."),
    (63, "3rd Earl ofPeterborough", "cand-1891", "The OCR omits a space in the title; Haskell only says Pekemburgh may possibly be this person."),
    (63, "Italy", "cand-3461", "Destination in the note's possible Peterborough identification."),
    (63, "Spain", "cand-5120", "Geographic origin named in the note."),
    (63, "dal Sole", "cand-2480", "Artist named in the note's account of commissions."),
    (63, "Zanotti", "cand-7115", "Citation to Storia dell'Accademia Clementina, vol. I, p.309."),
    (64, "Soprani", "cand-5160", "Citation to vol. II, p.115; cited page not independently read."),
    (65, "duc d’Estrées", "cand-0983", "Existing index candidate; the note says he arrived in Naples in 1702."),
    (65, "Naples", "cand-3534", "Place of the reported 1702 arrival."),
    (65, "de Dominici", "cand-4835", "Citation to vol. IV, p.321."),
    (65, "de Matteis", "cand-1581", "Existing Paolo de Matteis candidate; the note reports work for Crozat in Paris."),
    (65, "Pierre Crozat", "cand-0894", "Use the index candidate covering p.200n; the cited identity is not otherwise resolved here."),
    (65, "Loret", "cand-6583", "Citation to the existing Loret publication candidate, p.543."),
    (65, "Paris", "cand-4653", "Place in the note's account of de Matteis's work for Crozat."),
    (66, "duc d’Orléans", "cand-1786", "Use the index candidate covering p.200n; retain the source's title form."),
    (66, "Regent", "cand-1786", "Title that the note says he later held; same source candidate as the duc d’Orléans."),
    (66, "Solimena", "cand-2484", "Artist whom the note says Orléans invited to Paris in 1715."),
    (66, "Paris", "cand-4653", "Destination of Solimena's reported 1715 invitation."),
    (66, "Bologna", "cand-7348", "Citation to Ferdinando Bologna, Francesco Solimena, p.191."),
    (66, "contemporary Italian art", "cand-4131", "Subject of the patronage claim in Haskell's note."),
    (67, "De Dominici", "cand-4835", "Citation to vol. IV, pp.258 and 336."),
    (67, "Binchs", "cand-7301", "Footnote's source-form name; keep separate from Admiral Byng until S3."),
    (67, "Naples", "cand-3534", "The note says this person had been back in Naples in 1719."),
    (67, "Archivio Storico per la Province Napoletane", "cand-7347", "Periodical locator for the 1906 report, p.453."),
    (67, "Admiral Byng", "cand-0475", "Existing index candidate; Haskell's proposed identity is recorded without merging candidates."),
    (67, "British fleet in the Mediterranean", "cand-7354", "Organization whose command is attributed to Byng from 1718."),
    (68, "Harrach", "cand-1291", "Existing index candidate; the note characterizes his patronage."),
    (68, "surviving collection", "cand-7355", "Source-derived collection candidate; no collection type is available in the current taxonomy."),
    (68, "Ritschl", "cand-7352", "Citation to the Harrach gallery catalogue, passim."),
    (68, "de Dominici", "cand-4835", "Citation to vol. IV, pp.46, 439, 441, 444, and 571."),
    (68, "Neapolitan art", "cand-7356", "Haskell's category in the claim about Harrach's patronage."),
    (70, "Crespi", "cand-0871", "Existing index candidate cited for works in Prince Eugene's gallery."),
    (70, "dal Sole", "cand-2480", "Existing candidate used in the p.201 body passage."),
    (70, "Zanotti", "cand-7115", "Citation to Storia dell'Accademia Clementina, vol. I, p.302 and vol. II, p.45."),
    (71, "Ug", "cand-7349", "Source OCR reads Ug; the scan reads Ilg. Citation locator: passim."),
    (71, "Tietze", "cand-7350", "Citation to the 1933 article, pp.891-907."),
    (71, "the collection", "cand-7309", "Anaphora to Prince Eugene's dispersed picture collection in the p.201 body."),
    (71, "Carlo Emanuele III of Savoy", "cand-7353", "Named buyer of much, not all, of the collection in Haskell's note."),
    (71, "Baudi di Vesme", "cand-7351", "Citation to the 1886 study, pp.161-256."),
    (72, "Zanotti", "cand-7115", "Citation to vol. I, p.275."),
    (73, "ibid.", "cand-7115", "Ibid. continues the Zanotti citation from note 3."),
    (74, "De Dominici", "cand-4835", "Citation to vol. IV, pp.432-433 and 439."),
    (75, "Zanotti", "cand-7115", "Citation to vol. II, p.234."),
    (76, "Claretta", "cand-4995", "Reuse the existing 1893 cited-publication candidate; the cited pages are not independently read."),
]

mentions = []
all_candidate_ids = candidate_ids | new_candidate_ids
for line_number, surface, candidate_id, note in mention_specs:
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {surface} -> {candidate_id}")
    line_text = source_lines[line_number - 1]
    first = line_text.find(surface)
    if first < 0 or line_text.find(surface, first + 1) >= 0:
        raise SystemExit(f"source-exact mention missing or repeated; review occurrence: L{line_number} {surface!r}")
    base = sum(len(source_lines[n - 1]) + 1 for n in range(62, line_number))
    start = base + first
    end = start + len(surface)
    segment_text = "\n".join(source_lines[61:76])
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch: L{line_number} {surface!r}")
    mentions.append({
        "mention_id": f"m-chp7-p200-p202-notes-{len(mentions)+1:03d}",
        "segment_id": NOTE_SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })
if {row["mention_id"] for row in mentions} & existing_mention_ids:
    raise SystemExit("planned mention ID collision")


def statement(
    sid, line, page, pdf_page, predicate, claim, qualification, *,
    subject=None, obj=None, mentioned=(), quote=None, marker=None,
    text_layer="footnote", linked=(), related_segment=None,
    related_lines=(), citations=None, corrections=None,
):
    source_text = source_lines[line - 1]
    quote = quote or source_text.strip()
    if quote not in source_text:
        raise SystemExit(f"quote not present in source L{line}: {sid}")
    q = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": page,
        "pdf_physical_page": pdf_page,
        "claim": claim,
        "speaker": "Haskell footnote",
        "text_layer": text_layer,
        "qualification": qualification,
        "footnote_marker": marker,
        "footnote_segment": NOTE_SEGMENT,
        "related_segment": related_segment,
        "related_source_lines": list(related_lines),
        "linked_body_statement_ids": list(linked),
        "mentioned_candidate_ids": list(mentioned),
    }
    if citations:
        q["citations"] = citations
    if corrections:
        q["ocr_corrections"] = corrections
    return {
        "statement_id": sid,
        "segment_id": NOTE_SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


body_p200 = [
    "st-chp7-p200-v-pekemburgh-commissions-parodi-bust",
    "st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles",
    "st-chp7-p200-v-destrees-visits-naples-with-philip-v",
    "st-chp7-p200-v-destrees-takes-paolo-to-paris",
    "st-chp7-p200-v-destrees-introduces-paolo-to-nobles-bankers",
    "st-chp7-p200-v-contemporary-painting-interest-at-versailles",
    "st-chp7-p200-v-paolo-works-for-binchs-and-daun",
    "st-chp7-p200-v-daun-responsible-for-naples-capture",
    "st-chp7-p200-v-daun-first-viceroy-and-patronage",
    "st-chp7-p200-v-harrach-continues-process-after-1728",
]
body_p201 = [
    "st-chp7-p201-v-caprara-commissions-bologna-paintings",
    "st-chp7-p201-v-eugene-private-patron",
    "st-chp7-p201-v-picture-collection-dispersed",
    "st-chp7-p201-v-collection-contained-flemish-primitives",
    "st-chp7-p201-v-eugene-reputation-among-italians",
    "st-chp7-p201-v-eugene-gallery-pictures",
    "st-chp7-p201-v-list-not-exhaustive",
    "st-chp7-p201-v-pictures-by-neapolitan-painters",
    "st-chp7-p201-v-eugene-boni-virgil-portrait",
]
body_p202 = ["st-chp7-p202-v-savoy-transformed-after-war"]
body_statement_ids = set(body_p200 + body_p201 + body_p202)
if not body_statement_ids <= existing_statement_ids:
    missing = sorted(body_statement_ids - existing_statement_ids)
    raise SystemExit(f"missing body statements needed for footnote links: {missing}")

corrections_p200_n1 = [
    {"source_line": 63, "ocr": "tbe", "reading": "the", "basis": "CHP-7.pdf physical p.38"},
    {"source_line": 63, "ocr": "ofPeterborough", "reading": "of Peterborough", "basis": "CHP-7.pdf physical p.38"},
]
corrections_p200_n5 = [
    {"source_line": 67, "ocr": "6", "reading": "5", "basis": "CHP-7.pdf physical p.38 footnote marker"},
    {"source_line": 67, "ocr": "bave", "reading": "have", "basis": "CHP-7.pdf physical p.38"},
    {"source_line": 67, "ocr": "‘Binchs,", "reading": "‘Binchs’,", "basis": "CHP-7.pdf physical p.38"},
]
corrections_p200_n2 = [
    {"source_line": 64, "ocr": "...", "reading": ".", "basis": "CHP-7.pdf physical p.38"},
]
corrections_p201_n1 = [
    {"source_line": 70, "ocr": "H", "reading": "II", "basis": "CHP-7.pdf physical p.43"},
    {"source_line": 70, "ocr": "4$", "reading": "45", "basis": "CHP-7.pdf physical p.43"},
]
corrections_p201_n2 = [
    {"source_line": 71, "ocr": "Ug", "reading": "Ilg", "basis": "CHP-7.pdf physical p.43"},
]
corrections_p202_n1 = [
    {"source_line": 76, "ocr": "i893", "reading": "1893", "basis": "CHP-7.pdf physical p.44"},
]

statements = [
    statement(
        "st-chp7-p200-n1-possible-peterborough", 63, 200, 38,
        "possible_identity_proposed_as",
        "Haskell says Admiral ‘Pekemburgh’ may possibly be the 3rd Earl of Peterborough.",
        "This is explicitly a possibility in the footnote. Keep cand-7285 and cand-1891 separate until S3 identity alignment.",
        subject="cand-7285", obj="cand-1891", mentioned=["cand-7285", "cand-1891"],
        quote="This may possibly be tbe famous 3rd Earl ofPeterborough",
        marker=1, related_segment=P200_SEGMENT, related_lines=[11],
        linked=[body_p200[0]], corrections=corrections_p200_n1,
    ),
    statement(
        "st-chp7-p200-n1-peterborough-travel", 63, 200, 38,
        "travelled_to_italy_from_spain",
        "The note says the 3rd Earl of Peterborough came from Spain to Italy for a few months in 1707 and returned for a much longer period in the next decade.",
        "These biographical details occur under Haskell's possible identification; they do not establish that the body figure ‘Pekemburgh’ was Peterborough.",
        subject="cand-1891", mentioned=["cand-1891", "cand-5120", "cand-3461"],
        quote="who arrived in Italy from Spain for a few months in 1707 and then returned for a much longer period in the next decade",
        marker=1, related_segment=P200_SEGMENT, related_lines=[11],
        linked=[body_p200[0]], corrections=corrections_p200_n1,
    ),
    statement(
        "st-chp7-p200-n1-peterborough-commissions-dal-sole", 63, 200, 38,
        "commissioned_pictures_from",
        "Haskell says Peterborough certainly commissioned a number of pictures from dal Sole during the longer Italian stay.",
        "This claim is part of the footnote's possible identification context; cited pages were not independently read.",
        subject="cand-1891", obj="cand-2480", mentioned=["cand-1891", "cand-2480"],
        quote="when he certainly commissioned a number of pictures from dal Sole",
        marker=1, related_segment=P200_SEGMENT, related_lines=[11],
        linked=[body_p200[0]],
    ),
    statement(
        "st-chp7-p200-n1-cite-soprani", 63, 200, 38,
        "footnote_citation",
        "Footnote 1 cites Soprani, vol. I, p.120, in connection with the possible Peterborough identification.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-5160", mentioned=["cand-5160"],
        quote="Soprani, H, p. 120", marker=1, text_layer="bibliographic pointer",
        related_segment=P200_SEGMENT, related_lines=[11],
        linked=[body_p200[0], "st-chp7-p200-n1-possible-peterborough", "st-chp7-p200-n1-peterborough-travel"],
        citations=[{"source_candidate_id": "cand-5160", "volume": "I", "page": "120"}],
        corrections=[{"source_line": 63, "ocr": "H", "reading": "I", "basis": "CHP-7.pdf physical p.38"}],
    ),
    statement(
        "st-chp7-p200-n1-cite-zanotti", 63, 200, 38,
        "footnote_citation",
        "Footnote 1 cites Zanotti, vol. I, p.309, after the claim about Peterborough commissioning pictures from dal Sole.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-7115", mentioned=["cand-7115"],
        quote="Zanotti, I, p. 309", marker=1, text_layer="bibliographic pointer",
        related_segment=P200_SEGMENT, related_lines=[11],
        linked=[body_p200[0], "st-chp7-p200-n1-peterborough-commissions-dal-sole"],
        citations=[{"source_candidate_id": "cand-7115", "volume": "I", "page": "309"}],
    ),
    statement(
        "st-chp7-p200-n2-cite-soprani", 64, 200, 38,
        "footnote_citation",
        "Footnote 2 cites Soprani, vol. II, p.115, for the de Ferrari/Noailles passage.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-5160", mentioned=["cand-5160"],
        quote="Soprani, II, p. 115", marker=2, text_layer="bibliographic pointer",
        related_segment=P200_SEGMENT, related_lines=[11],
        linked=[body_p200[1]],
        citations=[{"source_candidate_id": "cand-5160", "volume": "II", "page": "115"}],
        corrections=corrections_p200_n2,
    ),
    statement(
        "st-chp7-p200-n3-destrees-arrival", 65, 200, 38,
        "arrived_in_naples_in_1702",
        "Haskell's note says the duc d’Estrées arrived in Naples in 1702.",
        "Reported by Haskell's footnote; the cited page was not independently read.",
        subject="cand-0983", obj="cand-3534", mentioned=["cand-0983", "cand-3534"],
        quote="The duc d’Estrées arrived in Naples in 1702",
        marker=3, related_segment=P200_SEGMENT, related_lines=[11, 12],
        linked=[body_p200[2]],
    ),
    statement(
        "st-chp7-p200-n3-matteis-crozat", 65, 200, 38,
        "worked_for",
        "Haskell's note says Paolo de Matteis worked for Pierre Crozat among other patrons in Paris.",
        "No specific work or date is named; this remains an attributed source statement.",
        subject="cand-1581", obj="cand-0894", mentioned=["cand-1581", "cand-0894", "cand-4653"],
        quote="In Paris de Matteis worked for Pierre Crozat among other patrons",
        marker=3, related_segment=P200_SEGMENT, related_lines=[11, 12],
        linked=[body_p200[3], body_p200[4]],
    ),
    statement(
        "st-chp7-p200-n3-cite-de-dominici", 65, 200, 38,
        "footnote_citation",
        "Footnote 3 cites de Dominici, vol. IV, p.321, for d’Estrées's 1702 arrival in Naples.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-4835", mentioned=["cand-4835"],
        quote="de Dominici, IV, p. 321", marker=3, text_layer="bibliographic pointer",
        related_segment=P200_SEGMENT, related_lines=[11],
        linked=["st-chp7-p200-n3-destrees-arrival"],
        citations=[{"source_candidate_id": "cand-4835", "volume": "IV", "page": "321"}],
    ),
    statement(
        "st-chp7-p200-n3-cite-loret", 65, 200, 38,
        "footnote_citation",
        "Footnote 3 cites Loret, p.543, for de Matteis's Paris work for Crozat.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-6583", mentioned=["cand-6583"],
        quote="Loret, p. 543", marker=3, text_layer="bibliographic pointer",
        related_segment=P200_SEGMENT, related_lines=[11, 12],
        linked=["st-chp7-p200-n3-matteis-crozat"],
        citations=[{"source_candidate_id": "cand-6583", "page": "543"}],
    ),
    statement(
        "st-chp7-p200-n4-orleans-in-artlovers", 66, 200, 38,
        "included_among_younger_art_lovers",
        "Haskell says the duc d’Orléans was certainly among the younger art lovers who were tiring of the official style at Versailles.",
        "This is the author's identification within a group, not evidence of a separate formal organization.",
        subject="cand-1786", obj="cand-7290", mentioned=["cand-1786", "cand-7290", "cand-7305", "cand-7287"],
        quote="Among these was certainly the duc d’Orléans, later tojbe Regent",
        marker=4, related_segment=P200_SEGMENT, related_lines=[11, 12],
        linked=[body_p200[5]],
    ),
    statement(
        "st-chp7-p200-n4-orleans-invites-solimena", 66, 200, 38,
        "invited_solimena_to_paris_in_1715",
        "Haskell's note says the duc d’Orléans invited Solimena to Paris in 1715.",
        "Reported by the footnote; the cited page was not independently read.",
        subject="cand-1786", obj="cand-2484", mentioned=["cand-1786", "cand-2484", "cand-4653"],
        quote="who in 1715 invited Solimena to Paris",
        marker=4, related_segment=P200_SEGMENT, related_lines=[11, 12],
        linked=[body_p200[5]],
    ),
    statement(
        "st-chp7-p200-n4-orleans-patronage", 66, 200, 38,
        "important_patron_of_contemporary_italian_art",
        "Haskell describes the duc d’Orléans as an important patron of contemporary Italian art.",
        "Authorial characterization; do not infer particular commissions beyond the stated Solimena invitation.",
        subject="cand-1786", obj="cand-4131", mentioned=["cand-1786", "cand-4131"],
        quote="became an important patron of contemporary Italian art",
        marker=4, related_segment=P200_SEGMENT, related_lines=[11, 12],
        linked=[body_p200[5]],
    ),
    statement(
        "st-chp7-p200-n4-cite-bologna", 66, 200, 38,
        "footnote_citation",
        "Footnote 4 cites Bologna, p.191, for the 1715 Solimena invitation.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-7348", mentioned=["cand-7348"],
        quote="Bologna, p. 191", marker=4, text_layer="bibliographic pointer",
        related_segment=P200_SEGMENT, related_lines=[11, 12],
        linked=["st-chp7-p200-n4-orleans-invites-solimena"],
        citations=[{"source_candidate_id": "cand-7348", "page": "191"}],
    ),
    statement(
        "st-chp7-p200-n5-binchs-return-naples", 67, 200, 38,
        "reported_back_in_naples_by_1719",
        "Haskell's note says the person called ‘Binchs’ had been back in Naples in 1719.",
        "This remains a footnote-level report attached to the source-form candidate; no independent verification is implied.",
        subject="cand-7301", obj="cand-3534", mentioned=["cand-7301", "cand-3534", "cand-0475"],
        quote="‘Binchs, whom we know to bave been back in Naples in 1719",
        marker=5, related_segment=P200_SEGMENT, related_lines=[13],
        linked=[body_p200[6], body_p200[7]],
        corrections=corrections_p200_n5,
    ),
    statement(
        "st-chp7-p200-n5-binchs-identified-byng", 67, 200, 38,
        "author_identifies_as",
        "Haskell says the admiral he calls ‘Binchs’ must be Admiral Byng.",
        "Record Haskell's identity claim only; keep cand-7301 and cand-0475 separate until S3 alignment.",
        subject="cand-7301", obj="cand-0475", mentioned=["cand-7301", "cand-0475"],
        quote="must be Admiral Byng", marker=5, related_segment=P200_SEGMENT, related_lines=[13],
        linked=[body_p200[6], body_p200[7]],
        corrections=corrections_p200_n5,
    ),
    statement(
        "st-chp7-p200-n5-byng-fleet-command", 67, 200, 38,
        "described_as_commander_of",
        "Haskell's note describes Admiral Byng as commander of the British fleet in the Mediterranean from 1718.",
        "Source-attributed role and start date; this does not resolve the separate ‘Binchs’ candidate.",
        subject="cand-0475", obj="cand-7354", mentioned=["cand-0475", "cand-7354"],
        quote="as from 1718 Commander of the British fleet in the Mediterranean",
        marker=5, related_segment=P200_SEGMENT, related_lines=[13],
        linked=[body_p200[6]],
        corrections=corrections_p200_n5,
    ),
    statement(
        "st-chp7-p200-n5-cite-de-dominici", 67, 200, 38,
        "footnote_citation",
        "Footnote 5 cites de Dominici, vol. IV, pp.258 and 336.",
        "Bibliographic pointer only; the cited pages were not independently read.",
        obj="cand-4835", mentioned=["cand-4835"],
        quote="De Dominici, IV, pp. 258 and 336", marker=5, text_layer="bibliographic pointer",
        related_segment=P200_SEGMENT, related_lines=[13],
        linked=["st-chp7-p200-n5-binchs-return-naples", "st-chp7-p200-n5-binchs-identified-byng"],
        citations=[{"source_candidate_id": "cand-4835", "volume": "IV", "pages": ["258", "336"]}],
        corrections=corrections_p200_n5,
    ),
    statement(
        "st-chp7-p200-n5-cite-archivio", 67, 200, 38,
        "footnote_citation",
        "Footnote 5 cites Archivio Storico per la Province Napoletane (1906), p.453, for the Naples return report.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-7347", mentioned=["cand-7347"],
        quote="Archivio Storico per la Province Napoletane, 1906, p. 453",
        marker=5, text_layer="bibliographic pointer",
        related_segment=P200_SEGMENT, related_lines=[13],
        linked=["st-chp7-p200-n5-binchs-return-naples"],
        citations=[{"source_candidate_id": "cand-7347", "year": 1906, "page": "453"}],
        corrections=corrections_p200_n5,
    ),
    statement(
        "st-chp7-p200-n7-harrach-patronage", 68, 200, 38,
        "described_as_most_enthusiastic_austrian_patron_of",
        "Haskell calls Count Harrach the most enthusiastic Austrian patron of Neapolitan art and points to his surviving collection.",
        "The superlative is Haskell's; the note does not enumerate the collection or establish its present location.",
        subject="cand-1291", obj="cand-7356",
        mentioned=["cand-1291", "cand-7355", "cand-7356"],
        quote="Harrach was the most enthusiastic Austrian patron of Neapolitan art, as can be seen from his surviving collection",
        marker=7, related_segment=P200_SEGMENT, related_lines=[16],
        linked=[body_p200[9]],
    ),
    statement(
        "st-chp7-p200-n7-cite-ritschl", 68, 200, 38,
        "footnote_citation",
        "Footnote 7 cites Ritschl, passim, on Harrach's surviving picture collection.",
        "Bibliographic pointer only; the cited catalogue and entries were not independently read.",
        obj="cand-7352", mentioned=["cand-7352"],
        quote="Ritschl, passim", marker=7, text_layer="bibliographic pointer",
        related_segment=P200_SEGMENT, related_lines=[16],
        linked=["st-chp7-p200-n7-harrach-patronage"],
        citations=[{"source_candidate_id": "cand-7352", "locator": "passim"}],
    ),
    statement(
        "st-chp7-p200-n7-cite-de-dominici", 68, 200, 38,
        "footnote_citation",
        "Footnote 7 cites de Dominici, vol. IV, pp.46, 439, 441, 444, and 571.",
        "Bibliographic pointer only; the cited pages were not independently read.",
        obj="cand-4835", mentioned=["cand-4835"],
        quote="de Dominici, IV, pp. 46, 439, 441, 444, 571", marker=7,
        text_layer="bibliographic pointer", related_segment=P200_SEGMENT,
        related_lines=[16], linked=["st-chp7-p200-n7-harrach-patronage"],
        citations=[{"source_candidate_id": "cand-4835", "volume": "IV", "pages": ["46", "439", "441", "444", "571"]}],
    ),
    statement(
        "st-chp7-p201-n1-cite-zanotti-i", 70, 201, 43,
        "footnote_citation",
        "Footnote 1 cites Zanotti, vol. I, p.302, for the Crespi and dal Sole passage.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-7115", mentioned=["cand-7115"],
        quote="Zanotti, I, p. 302", marker=1, text_layer="bibliographic pointer",
        related_segment=P201_SEGMENT, related_lines=[43, 50],
        linked=[body_p201[0], body_p201[5]],
        citations=[{"source_candidate_id": "cand-7115", "volume": "I", "page": "302"}],
        corrections=corrections_p201_n1,
    ),
    statement(
        "st-chp7-p201-n1-cite-zanotti-ii", 70, 201, 43,
        "footnote_citation",
        "Footnote 1 also cites Zanotti, vol. II, p.45.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-7115", mentioned=["cand-7115"],
        quote="H, p. 4$", marker=1, text_layer="bibliographic pointer",
        related_segment=P201_SEGMENT, related_lines=[43, 50],
        linked=[body_p201[0], body_p201[5]],
        citations=[{"source_candidate_id": "cand-7115", "volume": "II", "page": "45"}],
        corrections=corrections_p201_n1,
    ),
    statement(
        "st-chp7-p201-n2-eugene-collection-acquired", 71, 201, 43,
        "much_of_collection_bought_by",
        "Haskell's note says much of Prince Eugene's dispersed picture collection was bought by Carlo Emanuele III of Savoy.",
        "Preserve ‘much of’ rather than treating the whole collection as acquired; this remains Haskell's report through a citation, not an independently verified transaction.",
        subject="cand-7309", obj="cand-7353", mentioned=["cand-7309", "cand-7353", "cand-2385"],
        quote="For the fate of the collection much of which was bought by Carlo Emanuele III of Savoy",
        marker=2, related_segment=P201_SEGMENT, related_lines=[45, 48],
        linked=[body_p201[1], body_p201[2], body_p201[3]],
        corrections=corrections_p201_n2,
    ),
    statement(
        "st-chp7-p201-n2-cite-ilg", 71, 201, 43,
        "footnote_citation",
        "Footnote 2 cites Ilg, passim.",
        "General bibliographic pointer; the cited work was not independently read.",
        obj="cand-7349", mentioned=["cand-7349"],
        quote="Ug, passim", marker=2, text_layer="bibliographic pointer",
        related_segment=P201_SEGMENT, related_lines=[45, 48],
        linked=[body_p201[1], body_p201[2], body_p201[3]],
        citations=[{"source_candidate_id": "cand-7349", "locator": "passim"}],
        corrections=corrections_p201_n2,
    ),
    statement(
        "st-chp7-p201-n2-cite-tietze", 71, 201, 43,
        "footnote_citation",
        "Footnote 2 cites Tietze, pp.891-907.",
        "Bibliographic pointer only; the cited pages were not independently read.",
        obj="cand-7350", mentioned=["cand-7350"],
        quote="Tietze, pp. 891-907", marker=2, text_layer="bibliographic pointer",
        related_segment=P201_SEGMENT, related_lines=[45, 48],
        linked=[body_p201[1], body_p201[2], body_p201[3]],
        citations=[{"source_candidate_id": "cand-7350", "pages": ["891", "907"]}],
    ),
    statement(
        "st-chp7-p201-n2-cite-baudi", 71, 201, 43,
        "footnote_citation",
        "Footnote 2 directs readers to Baudi di Vesme (1886), pp.161-256, for the collection's fate.",
        "Bibliographic pointer only; the cited article was not independently read.",
        obj="cand-7351", mentioned=["cand-7351"],
        quote="Baudi di Vesme, 1886, pp. 161-256", marker=2,
        text_layer="bibliographic pointer", related_segment=P201_SEGMENT,
        related_lines=[45, 48],
        linked=["st-chp7-p201-n2-eugene-collection-acquired"],
        citations=[{"source_candidate_id": "cand-7351", "year": 1886, "pages": ["161", "256"]}],
    ),
    statement(
        "st-chp7-p201-n3-cite-zanotti", 72, 201, 43,
        "footnote_citation",
        "Footnote 3 cites Zanotti, vol. I, p.275, for the description of Eugene as a protector of the fine arts.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-7115", mentioned=["cand-7115"],
        quote="Zanotti, I, p. 275", marker=3, text_layer="bibliographic pointer",
        related_segment=P201_SEGMENT, related_lines=[49],
        linked=[body_p201[4]],
        citations=[{"source_candidate_id": "cand-7115", "volume": "I", "page": "275"}],
    ),
    statement(
        "st-chp7-p201-n4-cite-zanotti", 73, 201, 43,
        "footnote_citation",
        "Footnote 4 continues the Zanotti citation, vol. I, p.302 and vol. II, p.43.",
        "Ibid. refers to the Zanotti work cited in footnote 3; the cited pages were not independently read.",
        obj="cand-7115", mentioned=["cand-7115"],
        quote="ibid., I, p. 302, and II, p. 43", marker=4,
        text_layer="bibliographic pointer", related_segment=P201_SEGMENT,
        related_lines=[50],
        linked=[body_p201[5], body_p201[6]],
        citations=[{"source_candidate_id": "cand-7115", "volume": "I", "page": "302"}, {"source_candidate_id": "cand-7115", "volume": "II", "page": "43"}],
    ),
    statement(
        "st-chp7-p201-n5-cite-de-dominici", 74, 201, 43,
        "footnote_citation",
        "Footnote 5 cites de Dominici, vol. IV, pp.432-433 and 439, alongside the Ghislandi reference.",
        "Bibliographic pointer only; the cited pages were not independently read.",
        obj="cand-4835", mentioned=["cand-4835"],
        quote="De Dominici, IV, pp. 432-3, 439", marker=5,
        text_layer="bibliographic pointer", related_segment=P201_SEGMENT,
        related_lines=[50],
        linked=[body_p201[5], body_p201[7]],
        citations=[{"source_candidate_id": "cand-4835", "volume": "IV", "pages": ["432-433", "439"]}],
    ),
    statement(
        "st-chp7-p201-n6-cite-zanotti", 75, 201, 43,
        "footnote_citation",
        "Footnote 6 cites Zanotti, vol. II, p.234, for the Boni commission.",
        "Bibliographic pointer only; the cited page was not independently read.",
        obj="cand-7115", mentioned=["cand-7115"],
        quote="Zanotti, II, p. 234", marker=6, text_layer="bibliographic pointer",
        related_segment=P201_SEGMENT, related_lines=[51],
        linked=[body_p201[8]],
        citations=[{"source_candidate_id": "cand-7115", "volume": "II", "page": "234"}],
    ),
    statement(
        "st-chp7-p202-n1-cite-claretta", 76, 202, 44,
        "footnote_citation",
        "Footnote 1 cites Claretta (1893), pp.1-309, in the Savoy art-patronage discussion.",
        "Bibliographic pointer only; the cited pages were not independently read. Reuse the existing 1893 publication candidate pending the bibliography segment's S2 review.",
        obj="cand-4995", mentioned=["cand-4995"],
        quote="Claretta, i893, pp. 1-309", marker=1,
        text_layer="bibliographic pointer", related_segment=P202_SEGMENT,
        related_lines=[59],
        linked=[body_p202[0]],
        citations=[{"source_candidate_id": "cand-4995", "year": 1893, "pages": ["1", "309"]}],
        corrections=corrections_p202_n1,
    ),
]

if len({row["statement_id"] for row in statements}) != len(statements):
    raise SystemExit("duplicate planned statement IDs")
if {row["statement_id"] for row in statements} & existing_statement_ids:
    raise SystemExit("planned statement ID already exists")
for row in statements:
    q = row["qualifiers"]
    if not set(q["mentioned_candidate_ids"]) <= all_candidate_ids:
        raise SystemExit(f"statement references missing candidate: {row['statement_id']}")
    for key in ("subject_candidate_id", "object_candidate_id"):
        if row[key] and row[key] not in all_candidate_ids:
            raise SystemExit(f"{key} references missing candidate: {row['statement_id']}")
    if not set(q["linked_body_statement_ids"]) <= existing_statement_ids | {s["statement_id"] for s in statements}:
        raise SystemExit(f"statement links to missing statement: {row['statement_id']}")


def updated_coverage_rows():
    output = []
    for old in coverage_rows:
        row = dict(old)
        if row["segment_id"] == NOTE_SEGMENT:
            row.update({
                "disposition": "reviewed",
                "migration_status": "complete",
                "source_line_ranges": "L63-68,L70-76",
                "note": (
                    "p.200 footnotes 1-5 and 7, p.201 footnotes 1-6, and p.202 footnote 1 read against "
                    "CHP-7.pdf physical pp.38, 43-44 and migrated with body backlinks. L67 OCR footnote "
                    "number 6 is printed 5; the p.200 note 6 is the text already migrated at L18. L69 is "
                    "reversed Plate 30/31 caption OCR already covered by front-matter plate-list lines 87-90; "
                    "it adds no distinct claim. Cited pages were not independently consulted."
                ),
            })
        elif row["segment_id"] == P200_SEGMENT:
            row["note"] = (
                "p.200 body and footnote 6 (the text present at L18) read against CHP-7.pdf physical p.38. "
                "Footnote 6 is cross-linked to the claims at L13; footnotes 1-5 and 7 in the later composite "
                "block L62-76 are now migrated. The L17 sentence ending 'furnishing' closes at p.201 L43. "
                "S2 corrections: printed 'further' for OCR 'Anther'; printed 'Pascoli, II' for OCR 'H'; "
                "printed 'Ghislandi' for OCR 'Gliislandi'. Source text unchanged."
            )
            row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L10-18"})
        elif row["segment_id"] == P201_SEGMENT:
            row["note"] = (
                "Printed p.201 body read against CHP-7.pdf physical p.43. Closes the p.200 L17 sentence at "
                "L43; records the Prince Eugene patronage account, Vienna transition, named palace/work "
                "references, and OCR corrections 'sine arts' to 'fine arts' and 'Galli-Bibbiena' to "
                "'Galli-Bibiena'. Footnotes 1-6 are now migrated from composite segment L62-76 and linked "
                "to the relevant body statements."
            )
        elif row["segment_id"] == P202_SEGMENT:
            row["note"] = (
                "Printed p.202 body read against CHP-7.pdf physical p.44; L58 closes the p.201 Vienna "
                "civilisation sentence. L59-60 covers the Savoy/Turin transition. Footnote 1 is now "
                "migrated from composite segment L62-76 and linked to the p.202 Savoy statement."
            )
        output.append(row)
    return output


updated_coverage = updated_coverage_rows()
target_coverage = next(row for row in updated_coverage if row["segment_id"] == NOTE_SEGMENT)
if (target_coverage["disposition"], target_coverage["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("note coverage did not close")

previous_note6 = [
    row for row in statement_rows
    if row["segment_id"] == P200_SEGMENT and row.get("qualifiers", {}).get("footnote_marker") == 6
]
if not previous_note6:
    raise SystemExit("expected the existing p.200 footnote 6 at L18 to remain in place")
updated_body_rows = []
for row in statement_rows:
    row = dict(row)
    q = dict(row.get("qualifiers", {}))
    if row["statement_id"] == "st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles":
        q["footnote_marker"] = 2
    elif row["statement_id"] == "st-chp7-p200-v-destrees-introduces-paolo-to-nobles-bankers":
        q["footnote_marker"] = 3
    row["qualifiers"] = q
    updated_body_rows.append(row)

preview = {
    "mode": "dry-run",
    "source_segment": NOTE_SEGMENT,
    "new_candidates": len(new_candidates),
    "new_mentions": len(mentions),
    "new_statements": len(statements),
    "existing_body_footnote_markers_added": {
        "st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles": 2,
        "st-chp7-p200-v-destrees-introduces-paolo-to-nobles-bankers": 3,
    },
    "coverage_to_complete": [NOTE_SEGMENT, P200_SEGMENT],
    "p201_p202_coverage": "remains reviewed/complete; footnote link notes updated",
    "ocr_corrections": corrections_p200_n1 + corrections_p200_n2 + corrections_p200_n5 + corrections_p201_n1 + corrections_p201_n2 + corrections_p202_n1,
    "candidate_ids": NEW_CANDIDATE_IDS,
    "statement_ids": [row["statement_id"] for row in statements],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (CANDIDATE_PATH, MENTION_PATH, STATEMENT_PATH, COVERAGE_PATH):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_rows.extend(new_candidates)
mention_rows.extend(mentions)
updated_body_rows.extend(statements)
write_csv_atomic(CANDIDATE_PATH, candidate_fields, candidate_rows)
write_csv_atomic(MENTION_PATH, mention_fields, mention_rows)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENT_PATH.parent, delete=False, suffix=".tmp") as stream:
    for row in updated_body_rows:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary = Path(stream.name)
temporary.replace(STATEMENT_PATH)
write_csv_atomic(COVERAGE_PATH, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
