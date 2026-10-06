"""Controlled S2 migration for p.308-310 notes; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
P307 = "chp-10:10_CHP-10_intro:l445-454"
P308 = "chp-10:10_CHP-10_intro:l456-466"
P309 = "chp-10:10_CHP-10_intro:l468-479"
P310 = "chp-10:10_CHP-10_intro:l481-489"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "f86bdce652339d718ca40068c0c679e339e10e76c179790bbf0c976299d209bf"
EXPECTED_P308_CONTINUATION_SHA = "ee18c1134b7c96ee2bbc67224a0690b65c47acfc62f0cfa64941f9b18886f5d8"
BACKUP_SUFFIX = ".bak-s2-chp10-p308-p310-notes-20261002"


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


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_span = "\n".join(source_lines[620:634])
continuation = source_lines[465]
if sha(notes_span) != EXPECTED_NOTES_SHA:
    raise SystemExit(f"notes L621-L634 changed: {sha(notes_span)}")
if sha(continuation) != EXPECTED_P308_CONTINUATION_SHA:
    raise SystemExit(f"p.308 continuation L466 changed: {sha(continuation)}")
if not source_lines[620].startswith("1 Most of these overdoors") or "accidentally added an extra x" not in continuation:
    raise SystemExit("p.308 note-1 anchors changed")

cp, mp, sp, vp = [TABLES / name for name in (
    "entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv"
)]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if (len(candidates), maximum) != (9543, 9556):
    raise SystemExit(f"candidate state changed: count={len(candidates)} max={maximum}")
expected_coverage = {
    NOTES: ("L492-620", "partial"),
    P307: ("L446-454", "partial"),
    P308: ("L457-465", "partial"),
    P309: ("L469-479", "partial"),
    P310: ("L482-489", "partial"),
}
for segment_id, (line_range, status) in expected_coverage.items():
    row = cov.get(segment_id)
    if not row or (row["source_line_ranges"], row["migration_status"]) != (line_range, status):
        raise SystemExit(f"coverage precondition changed for {segment_id}: {row}")

by_sid = {row["statement_id"]: row for row in statements}
body_links = {
    "st-chp10-p308-two-roman-capricci-for-smith": (2, 461),
    "st-chp10-p308-smith-continued-overdoor-series": (3, 464),
    "st-chp10-p309-nogari-portrait-commission": (1, 472),
    "st-chp10-p309-memmo-on-books-and-visentini": (2, 476),
    "st-chp10-p309-tiepolo-commission-came-to-nothing": (3, 478),
    "st-chp10-p309-visentini-built-marble-facade": (4, 478),
    "st-chp10-p309-possible-smith-employment-of-zais": (5, 478),
    "st-chp10-p309-smith-acquired-sagredo-old-masters": (6, 479),
    "st-chp10-p310-country-house-holdings": (1, 483),
    "st-chp10-p310-1756-royal-negotiations-war": (2, 485),
    "st-chp10-p310-smith-gave-up-theatre-box": (3, 486),
    "st-chp10-p310-smith-return-and-italy-travel-plan": (4, 487),
    "st-chp10-p310-james-adam-meeting-and-assessment": (5, 487),
    "st-chp10-p310-1762-sale-to-george-iii": (6, 488),
}
for sid, (marker, _) in body_links.items():
    row = by_sid.get(sid)
    if not row or row.get("qualifiers", {}).get("footnote_marker") != marker or row["qualifiers"].get("footnote_text_pending") is not True:
        raise SystemExit(f"body footnote state changed: {sid}")
resignation = by_sid["st-chp10-p310-smith-resigned-consulship"]["qualifiers"]
if resignation.get("footnote_marker") != 4 or resignation.get("footnote_text_pending") is not True:
    raise SystemExit("unexpected p.310 erroneous marker state")
series_statement = by_sid["st-chp10-p307-next-commissioned-series-aim"]["qualifiers"]
if "footnote_marker" in series_statement:
    raise SystemExit("p.308 marker 1 was already assigned")

NEW_CANDIDATES = [
    ("cand-9557", "John Fleming, Mssrs. Robert and James Adam: Art dealers (I), Connoisseur 144 (1959), pp.168-171", "archive",
     "Exact local bibliography match at 21_CHP-21Bibliography.md L480; p.310 note 1 cites p.171. Bibliographic identification only; cited page not independently read.", 630),
    ("cand-9558", "John Fleming, Robert Adam and his circle (London, 1962)", "archive",
     "Exact local bibliography entry at 21_CHP-21Bibliography.md L481; p.310 note 5 cites p.270. The cited pages and the letters were not independently consulted.", 634),
    ("cand-9559", "Francis Haskell, Algarotti and Tiepolo’s ‘Banquet of Cleopatra’ (Burlington Magazine, 1958), pp.212-213", "archive",
     "Exact local bibliography match at 21_CHP-21Bibliography.md L582; cited pages were not independently consulted.", 626),
    ("cand-9560", "Frances Vivian, 1963 citation at pp.157-162 (title unresolved)", "archive",
     "P.308 note 3 cites Vivian (1963), pp.157-162. The local bibliography lists Vivian’s Italian Studies article from 1963 at pp.54-66, so that entry is not treated as a confirmed match; cited pages and publication identity remain unresolved.", 623),
    ("cand-9561", "G. A. Moschini, 1924 citation at p.82 (title unresolved)", "archive",
     "P.309 note 5 cites G. A. Moschini, 1924, p.82. No exact local bibliography entry has been identified; cited page not independently consulted.", 628),
    ("cand-9562", "Atti del notaio Lodovico Gabrieli, record 7564, p.12v, 22 March 1756", "archive",
     "Specific notarial record locator printed in p.310 note 3. Underlying register and catalogue record were not independently consulted; reuse the broader archival series candidate cand-9485 as its source context.", 632),
    ("cand-9563", "Letter from Joseph Smith to William Pitt, 29 October 1760 (State Papers 99/68, f.96)", "archive",
     "Specific letter locator printed in p.310 note 4 at the Public Record Office. Neither the document nor the catalogue entry was independently consulted; do not merge with other State Papers 99/68 folio/page records.", 633),
    ("cand-9564", "Jenny Adam (recipient named in p.310 note 5)", "person",
     "Named as a recipient in the citation to James Adam’s letters; personal identity and her relation to the Adam family are not resolved here.", 634),
    ("cand-9565", "Letter from James Adam dated 27 August 1760, cited as addressed to Robert and Jenny Adam", "archive",
     "P.310 note 5 groups letters dated 20 and 27 August 1760 and names Robert and Jenny Adam; recipient-to-date allocation is not further specified. The letter is known only through Fleming, 1962, p.270.", 634),
    ("cand-9566", "Exhibition of The King’s Pictures, 1946-1947, catalogue no.440", "archive",
     "Catalogue/item locator cited in p.308 note 1. The specific catalogue record and item title were not independently checked.", 466),
    ("cand-9567", "Exhibition of The King’s Pictures, Royal Academy of Arts, London, 1946-1947", "event",
     "The local bibliography index identifies the exhibition at Royal Academy of Arts, London, 1946-1947 (21_CHP-21Bibliography.md L648). The cited catalogue item was not independently checked.", 466),
]
existing_names = {row["canonical_name"] for row in candidates}
new_candidates = []
new_cids = set()
for cid, name, kind, detail, line_no in NEW_CANDIDATES:
    if cid in cids or cid in new_cids or name in existing_names:
        raise SystemExit(f"candidate ID or natural key already exists: {cid} {name}")
    source_segment = P308 if line_no == 466 else NOTES
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{source_segment}#L{line_no}",
    })
    new_cids.add(cid)

ENTITY = {
    "smith": "cand-2440", "blunt": "cand-0379", "cust": "cand-9525", "cust_work": "cand-9526",
    "padua": "cand-1803", "vivian": "cand-9553", "memmo": "cand-1642", "memmo_work": "cand-8812",
    "haskell": "cand-9423", "gradenigo": "cand-8507", "gradenigo_work": "cand-8508",
    "moschini": "cand-1709", "zais": "cand-2830", "zuccarelli": "cand-2883",
    "blunt_croft": "cand-9340", "sagredo_doc": "cand-8598", "orlandi": "cand-7136",
    "orlandi_work": "cand-7137", "robert_adam": "cand-0012", "james_adam": "cand-0011",
    "parker": "cand-9538", "parker_work": "cand-9484", "notary": "cand-1096",
    "archive_series": "cand-9485", "pitt": "cand-1947", "pro": "cand-8289",
    "letter_20_aug": "cand-9519", "fleming": "cand-9520", "canaletto_series": "cand-9239",
    "horses": "cand-9245", "smith_roman_capricci": "cand-9249",
}
for key, cid in ENTITY.items():
    if cid not in cids:
        raise SystemExit(f"missing required candidate {key}: {cid}")

new_mentions = []
new_mids = set()


def add_mention(mid, segment_id, first_line, last_line, line_no, surface, cid, note="", occurrence=0):
    if mid in mids or mid in new_mids:
        raise SystemExit(f"duplicate mention ID: {mid}")
    if cid not in cids | new_cids:
        raise SystemExit(f"mention candidate missing: {mid} -> {cid}")
    line = source_lines[line_no - 1]
    positions = [match.start() for match in re.finditer(re.escape(surface), line)]
    if occurrence >= len(positions):
        raise SystemExit(f"surface occurrence not found on L{line_no}: {surface!r}")
    segment_prefix = "\n".join(source_lines[first_line - 1:line_no - 1])
    start = len(segment_prefix) + (1 if segment_prefix else 0) + positions[occurrence]
    new_mentions.append({
        "mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start),
        "end_char": str(start + len(surface)), "note": note,
    })
    new_mids.add(mid)


M = [
    ("m-s2-ch10-p308n1-horses", NOTES, 491, 634, 621, "Horses of St Mark’s", "cand-9245", "The work named in the cited dating note."),
    ("m-s2-ch10-p308n2-cust", NOTES, 491, 634, 622, "Cust", "cand-9525", "Surname-only author citation."),
    ("m-s2-ch10-p308n2-work", NOTES, 491, 634, 622, "p. 153", "cand-9526", "Short-form bibliographic locator; cited page unread."),
    ("m-s2-ch10-p308n2-padua", NOTES, 491, 634, 622, "Padua", "cand-1803", "Place named as a possible source for the imaginary settings."),
    ("m-s2-ch10-p308n3-blunt", NOTES, 491, 634, 623, "Blunt", "cand-0379", "Author named in short-form citation."),
    ("m-s2-ch10-p308n3-vivian", NOTES, 491, 634, 623, "Vivian", "cand-9553", "Author named in short-form citation."),
    ("m-s2-ch10-p308n3-vivian-work", NOTES, 491, 634, 623, "Vivian, 1963, pp. 157-62", "cand-9560", "Exact citation; local 1963 bibliography entry has a different page range."),
    ("m-s2-ch10-p309n1-cust", NOTES, 491, 634, 624, "Cust", "cand-9525", "Surname-only author citation."),
    ("m-s2-ch10-p309n1-work", NOTES, 491, 634, 624, "p. i6i", "cand-9526", "OCR locator; page image reads p.161."),
    ("m-s2-ch10-p309n2-memmo", NOTES, 491, 634, 625, "Andrea Memmo", "cand-1642", "Author named in brackets in the note."),
    ("m-s2-ch10-p309n2-work", NOTES, 491, 634, 625, "1786, p. 1", "cand-8812", "Citation to Memmo's 1786 work; title and page not verified."),
    ("m-s2-ch10-p309n3-haskell", NOTES, 491, 634, 626, "Haskell", "cand-9423", "Author named in short-form citation."),
    ("m-s2-ch10-p309n3-work", NOTES, 491, 634, 626, "Burlington Magazine, 1958, pp. 212-3", "cand-9559", "Exact local bibliography match; cited pages unread."),
    ("m-s2-ch10-p309n4-gradenigo", NOTES, 491, 634, 627, "Gradenigo", "cand-8507", "Surname-only author citation."),
    ("m-s2-ch10-p309n4-work", NOTES, 491, 634, 627, "p. 5", "cand-8508", "Short-form locator; work and cited page unresolved."),
    ("m-s2-ch10-p309n5-moschini", NOTES, 491, 634, 628, "G. A. Moschini", "cand-1709", "Author named in citation; identity alignment is deferred."),
    ("m-s2-ch10-p309n5-work", NOTES, 491, 634, 628, "1924, p. 82", "cand-9561", "Citation locator; title unresolved and cited page unread."),
    ("m-s2-ch10-p309n5-zais", NOTES, 491, 634, 628, "Giuseppe Zais", "cand-2830", "Artist named in the quoted claim."),
    ("m-s2-ch10-p309n5-zuccarelli", NOTES, 491, 634, 628, "Francesco Zuccarelli", "cand-2883", "Artist named in the quoted claim."),
    ("m-s2-ch10-p309n5-smith", NOTES, 491, 634, 628, "Console Smith", "cand-2440", "Joseph Smith as named in the Italian quotation."),
    ("m-s2-ch10-p309n6-publication", NOTES, 491, 634, 629, "Blunt and Croft-Murray", "cand-9340", "Joint publication citation; cited page unread."),
    ("m-s2-ch10-p309n6-document", NOTES, 491, 634, 629, "p. 24", "cand-8598", "Specific published archival document citation."),
    ("m-s2-ch10-p310n1-orlandi", NOTES, 491, 634, 630, "Orlandi", "cand-7136", "Author named in short-form citation."),
    ("m-s2-ch10-p310n1-work", NOTES, 491, 634, 630, "pp. 79-80 and 206", "cand-7137", "Citation to Orlandi's Abecedario Pittorico; cited pages unread."),
    ("m-s2-ch10-p310n1-robert-adam", NOTES, 491, 634, 630, "Robert Adam", "cand-0012", "Visitor named in the reported 1757 visit."),
    ("m-s2-ch10-p310n1-smith", NOTES, 491, 634, 630, "Consul Smith", "cand-2440", "Host named in the reported visit."),
    ("m-s2-ch10-p310n1-mogliano", NOTES, 491, 634, 630, "Mogliano", "cand-9207", "Location associated with Smith's country house; exact house identity not independently checked."),
    ("m-s2-ch10-p310n1-fleming", NOTES, 491, 634, 630, "Fleming, 1959, p. 171", "cand-9557", "Exact bibliography match for article; cited page unread."),
    ("m-s2-ch10-p310n2-parker", NOTES, 491, 634, 631, "Parker", "cand-9538", "Author named in short-form citation."),
    ("m-s2-ch10-p310n2-work", NOTES, 491, 634, 631, "p. 11", "cand-9484", "Page locator within the locally matched 1948 publication; cited page unread."),
    ("m-s2-ch10-p310n3-record", NOTES, 491, 634, 632, "Atti del notaio Lodovico Gabrieli, 7564, p. i2v, 22 Marzo 1756", "cand-9562", "Page image reads p.12v; specific record locator not independently consulted."),
    ("m-s2-ch10-p310n3-notary", NOTES, 491, 634, 632, "Lodovico Gabrieli", "cand-1096", "Notary named in the record citation."),
    ("m-s2-ch10-p310n3-series", NOTES, 491, 634, 632, "Archivio di Stato, Venice", "cand-9485", "Repository and archival-series context; current catalogue record not checked."),
    ("m-s2-ch10-p310n4-letter", NOTES, 491, 634, 633, "Letter from Smith to William Pitt of 29 October 1760", "cand-9563", "Specific letter as identified in the note."),
    ("m-s2-ch10-p310n4-pitt", NOTES, 491, 634, 633, "William Pitt", "cand-1947", "Named recipient; exact identity is not re-adjudicated here."),
    ("m-s2-ch10-p310n4-pro", NOTES, 491, 634, 633, "Public Record Office", "cand-8289", "Repository wording retained as printed."),
    ("m-s2-ch10-p310n4-state-papers", NOTES, 491, 634, 633, "State Papers 99/68, f. 96", "cand-9563", "Specific folio locator, kept distinct from other records in State Papers 99/68."),
    ("m-s2-ch10-p310n5-james", NOTES, 491, 634, 634, "James", "cand-0011", "Letter writer as named in the note."),
    ("m-s2-ch10-p310n5-robert", NOTES, 491, 634, 634, "Robert", "cand-0012", "Recipient named in the note; no new identity decision."),
    ("m-s2-ch10-p310n5-jenny", NOTES, 491, 634, 634, "Jenny", "cand-9564", "Recipient named by first name only; identity unresolved."),
    ("m-s2-ch10-p310n5-date1", NOTES, 491, 634, 634, "20", "cand-9519", "20 August 1760 letter already represented by an existing candidate; date is read with the surrounding note."),
    ("m-s2-ch10-p310n5-date2", NOTES, 491, 634, 634, "27 August 1760", "cand-9565", "Second letter date as printed; exact recipient allocation is not specified."),
    ("m-s2-ch10-p310n5-fleming", NOTES, 491, 634, 634, "Fleming, 1962, p. 270", "cand-9558", "Exact local bibliography book entry; cited page unread."),
    ("m-s2-ch10-p308n1-cont-blunt", P308, 456, 466, 466, "Sir Anthony Blunt", "cand-0379", "Author named in the note-1 continuation."),
    ("m-s2-ch10-p308n1-cont-catalogue", P308, 456, 466, 466, "Exhibition of The King’s Pictures, 1946-7, No. 440", "cand-9566", "Printed catalogue locator; catalogue item not checked."),
]
for row in M:
    add_mention(*row)

new_statements = []
new_sids = set()


def add_statement(sid, segment_id, first, last, line_start, line_end, subject, obj, predicate,
                  claim, speaker, text_layer, qualification, mentioned, relation=False,
                  marker=None, page=None, physical=None, body_ids=(), citations=(),
                  crossrefs=(), ocr_marker=None, quote=None):
    if sid in sids or sid in new_sids:
        raise SystemExit(f"duplicate statement ID: {sid}")
    original = "\n".join(source_lines[line_start - 1:line_end]) if quote is None else quote
    if original not in "\n".join(source_lines[first - 1:last]):
        raise SystemExit(f"statement quote outside segment: {sid}")
    q = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": page, "pdf_physical_page": physical,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation,
    }
    if marker is not None:
        q["footnote_marker"] = marker
        q["footnote_text_pending"] = False
    if body_ids:
        q["related_body_statement_ids"] = list(body_ids)
    if citations:
        q["citations"] = list(citations)
        q["cited_material_not_independently_consulted"] = True
    if crossrefs:
        q["cross_reference_segments"] = list(crossrefs)
    if ocr_marker is not None:
        q["ocr_footnote_marker"] = ocr_marker
        q["printed_footnote_marker"] = marker
    new_statements.append({
        "statement_id": sid, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": q, "original_quote": original,
        "source_file": SOURCE_FILE, "origin": "book",
    })
    new_sids.add(sid)


# p.308 note 1 is split between the consolidated notes and page-level OCR.
add_statement("st-chp10-p308-note1-overdoor-dating", NOTES, 491, 634, 621, 621,
              "cand-2440", "cand-9239", "reports_overdoor_and_horses_dates",
              "Haskell says most of Smith's overdoors are dated 1744, while the Horses of St Mark’s is dated in Roman fashion A.U.C.; the page-level continuation equates the date with 1753 and attributes the extra x to an accidental addition by Canaletto.",
              "Haskell, footnote", "footnote claim with cross-page OCR continuation",
              "The merged note OCR stops before A.U.C. 1332; p.308 L466 supplies the continuation. The cited explanation and catalogue item are not independently consulted.",
              ["cand-2440", "cand-9239", "cand-9245", "cand-0379", "cand-9566", "cand-9567"],
              marker=1, page=308, physical=37,
              body_ids=["st-chp10-p307-next-commissioned-series-aim", "st-chp10-p308-note1-date-explanation"],
              citations=[{"catalogue_candidate_id": "cand-9566", "event_candidate_id": "cand-9567", "item": "440"}],
              crossrefs=[P307, P308])
add_statement("st-chp10-p308-note1-date-explanation", P308, 456, 466, 466, 466,
              "cand-0379", "cand-9566", "attributes_date_error_to_accidental_extra_x",
              "The p.308 continuation says Anthony Blunt explains the A.U.C. date as equivalent to 1753 because Canaletto accidentally added an extra x, and points to catalogue no.440.",
              "Haskell reporting Blunt", "reported scholarly explanation and catalogue citation",
              "The explanation is recorded as Haskell's report of Blunt; the catalogue and cited discussion were not independently consulted.",
              ["cand-0379", "cand-9566", "cand-9567", "cand-9239"],
              page=308, physical=37, body_ids=["st-chp10-p307-next-commissioned-series-aim"],
              citations=[{"catalogue_candidate_id": "cand-9566", "event_candidate_id": "cand-9567", "item": "440"}],
              crossrefs=[NOTES], quote=continuation)

add_statement("st-chp10-p308-note2-cust-padua", NOTES, 491, 634, 622, 622,
              "cand-9249", "cand-1803", "may_be_inspired_by",
              "Haskell says the settings are imaginary but appear to have been inspired by Padua, citing Cust page 153.",
              "Haskell, footnote", "reported interpretation and citation",
              "The source passage itself qualifies the Padua connection as apparent; Cust and the cited page were not independently consulted.",
              ["cand-9525", "cand-9526", "cand-1803", "cand-9249"], page=308, physical=37,
              marker=2, body_ids=["st-chp10-p308-two-roman-capricci-for-smith"],
              citations=[{"author_candidate_id": "cand-9525", "publication_candidate_id": "cand-9526", "page": "153"}], crossrefs=[P308])
add_statement("st-chp10-p308-note3-blunt-vivian-citations", NOTES, 491, 634, 623, 623,
              "cand-4863", "cand-9560", "cites_studies_on_overdoor_dates_and_series",
              "Haskell cites Blunt (1958), pages 283-284, and Vivian (1963), pages 157-162, in relation to the overdoors.",
              "Haskell, footnote", "bibliographic citations",
              "Blunt's 1958 article matches the local bibliography. Vivian's cited page range does not match the local Italian Studies 1963 entry at pp.54-66; her citation remains unmatched. Neither cited item was read.",
              ["cand-0379", "cand-4863", "cand-9553", "cand-9560"], page=308, physical=37,
              marker=3, body_ids=["st-chp10-p308-smith-continued-overdoor-series"],
              citations=[{"author_candidate_id": "cand-0379", "publication_candidate_id": "cand-4863", "pages": "283-284", "bibliography_match": "exact local title/year"},
                        {"author_candidate_id": "cand-9553", "publication_candidate_id": "cand-9560", "year": "1963", "pages": "157-162", "bibliography_match": "unresolved; local 1963 entry has pp.54-66"}], crossrefs=[P308])

add_statement("st-chp10-p309-note1-cust-reference", NOTES, 491, 634, 624, 624,
              "cand-9525", "cand-9526", "cites_cust_page_for_smith_collection_context",
              "Haskell cites Cust page 161.", "Haskell, footnote", "bibliographic locator",
              "The OCR reads p. i6i; p.309 page image confirms p.161. The cited page was not read.",
              ["cand-9525", "cand-9526"], page=309, physical=38, marker=1,
              body_ids=["st-chp10-p309-nogari-portrait-commission"],
              citations=[{"author_candidate_id": "cand-9525", "publication_candidate_id": "cand-9526", "page": "161"}], crossrefs=[P309])
add_statement("st-chp10-p309-note2-memmo-reference", NOTES, 491, 634, 625, 625,
              "cand-1642", "cand-8812", "cites_memmo_1786_page_one",
              "Haskell cites Andrea Memmo's 1786 work, page 1.", "Haskell, footnote", "bibliographic locator",
              "The title, cited page and exact match to the broader Memmo 1786 candidate were not independently checked.",
              ["cand-1642", "cand-8812"], page=309, physical=38, marker=2,
              body_ids=["st-chp10-p309-memmo-on-books-and-visentini"],
              citations=[{"author_candidate_id": "cand-1642", "publication_candidate_id": "cand-8812", "year": "1786", "page": "1"}], crossrefs=[P309])
add_statement("st-chp10-p309-note3-haskell-reference", NOTES, 491, 634, 626, 626,
              "cand-9423", "cand-9559", "cites_haskell_article_and_internal_chapter",
              "Haskell cites his 1958 Burlington Magazine article at pages 212-213 and directs the reader to chapter 14.",
              "Haskell, footnote", "bibliographic citation and internal cross-reference",
              "The article title/year/pages match the local bibliography, but the cited pages were not read. The chapter pointer is not a claim about the article's contents.",
              ["cand-9423", "cand-9559"], page=309, physical=38, marker=3,
              body_ids=["st-chp10-p309-tiepolo-commission-came-to-nothing"],
              citations=[{"author_candidate_id": "cand-9423", "publication_candidate_id": "cand-9559", "year": "1958", "pages": "212-213"},
                        {"internal_reference": "Chapter 14"}], crossrefs=[P309])
add_statement("st-chp10-p309-note4-gradenigo-reference", NOTES, 491, 634, 627, 627,
              "cand-8507", "cand-8508", "cites_gradenigo_page_five",
              "Haskell cites Gradenigo page 5.", "Haskell, footnote", "bibliographic locator",
              "The cited page and the short-form work identification remain unresolved; it may be the same source cited at p.260 note 4, p.91.",
              ["cand-8507", "cand-8508"], page=309, physical=38, marker=4,
              body_ids=["st-chp10-p309-visentini-built-marble-facade"],
              citations=[{"author_candidate_id": "cand-8507", "publication_candidate_id": "cand-8508", "page": "5", "same_as_other_locator": "possible; unresolved"}], crossrefs=[P309])
for sid, object_id, label in [
    ("st-chp10-p309-note5-smith-patron-of-zais", "cand-2830", "Giuseppe Zais"),
    ("st-chp10-p309-note5-smith-patron-of-zuccarelli", "cand-2883", "Francesco Zuccarelli"),
]:
    add_statement(sid, NOTES, 491, 634, 628, 628, "cand-2440", object_id,
                  "reports_smith_as_great_protector",
                  f"Haskell quotes G. A. Moschini as saying that {label} had a great protector in Consul Smith.",
                  "Moschini as quoted by Haskell", "reported claim in an Italian quotation",
                  "This is a reported patronage claim, not independent proof of a formal patronage relation. Moschini's cited 1924 page 82 was not consulted; preserve the ellipsis and source wording.",
                  ["cand-1709", "cand-9561", "cand-2440", object_id], relation=True, page=309, physical=38,
                  marker=5, body_ids=["st-chp10-p309-possible-smith-employment-of-zais"],
                  citations=[{"author_candidate_id": "cand-1709", "publication_candidate_id": "cand-9561", "year": "1924", "page": "82", "quoted_text_language": "Italian"}], crossrefs=[P309],
                  ocr_marker=6, quote=source_lines[627])
add_statement("st-chp10-p309-note6-blunt-croft_murray-document", NOTES, 491, 634, 629, 629,
              "cand-8598", "cand-2440", "cites_document_for_smiths_sagredo_purchases",
              "Haskell directs the reader to a document published by Blunt and Croft-Murray at page 24, in connection with Smith's acquisition of old-master paintings from the Sagredo heirs.",
              "Haskell, footnote", "archival publication locator",
              "The document and cited page were not independently consulted. The OCR labels this as note 8; p.309 page image shows printed note 6.",
              ["cand-9340", "cand-8598", "cand-2440", "cand-9263"], page=309, physical=38,
              marker=6, body_ids=["st-chp10-p309-smith-acquired-sagredo-old-masters"],
              citations=[{"publication_candidate_id": "cand-9340", "document_candidate_id": "cand-8598", "page": "24"}], crossrefs=[P309], ocr_marker=8)

add_statement("st-chp10-p310-note1-adam-visit-citations", NOTES, 491, 634, 630, 630,
              "cand-0012", "cand-2440", "reports_robert_adams_1757_visit_and_cites_sources",
              "Haskell cites Orlandi pages 79-80 and 206 and Fleming 1959 page 171 for Robert Adam's 1757 visit to Consul Smith at Mogliano and Adam's praise of Smith's small, well-preserved collection of pictures by great masters.",
              "Robert Adam as quoted by Haskell", "reported visit and nested quotation with citations",
              "The Adam quotation is relayed by Haskell; Orlandi and Fleming pages were not independently read. The OCR's final quotation punctuation remains as a source transcription issue, not a claim about exact wording.",
              ["cand-7136", "cand-7137", "cand-0012", "cand-2440", "cand-9207", "cand-9557", "cand-9520"],
              page=310, physical=39, marker=1, body_ids=["st-chp10-p310-country-house-holdings"],
              citations=[{"author_candidate_id": "cand-7136", "publication_candidate_id": "cand-7137", "pages": "79-80, 206"},
                        {"author_candidate_id": "cand-9520", "publication_candidate_id": "cand-9557", "year": "1959", "page": "171"}], crossrefs=[P310])
add_statement("st-chp10-p310-note2-parker-reference", NOTES, 491, 634, 631, 631,
              "cand-9538", "cand-9484", "cites_parker_page_eleven",
              "Haskell cites K. T. Parker page 11.", "Haskell, footnote", "bibliographic locator",
              "The local bibliography identifies Parker's 1948 Canaletto drawings publication; the cited page was not read.",
              ["cand-9538", "cand-9484"], page=310, physical=39, marker=2,
              body_ids=["st-chp10-p310-1756-royal-negotiations-war"],
              citations=[{"author_candidate_id": "cand-9538", "publication_candidate_id": "cand-9484", "page": "11"}], crossrefs=[P310])
add_statement("st-chp10-p310-note3-gabrieli-record", NOTES, 491, 634, 632, 632,
              "cand-1096", "cand-9562", "cites_notarial_act_for_theatre_box_context",
              "Haskell cites an act in notary Lodovico Gabrieli's register 7564, page 12 verso, dated 22 March 1756, in connection with Smith's theatre box.",
              "Haskell, footnote", "archival locator",
              "The page image reads p.12v; the source OCR reads p.i2v. The cited register and catalogue entry were not independently consulted.",
              ["cand-1096", "cand-9562", "cand-9485", "cand-2440", "cand-9277"], page=310, physical=39, marker=3,
              body_ids=["st-chp10-p310-smith-gave-up-theatre-box"],
              citations=[{"notary_candidate_id": "cand-1096", "record_candidate_id": "cand-9562", "series_candidate_id": "cand-9485", "register": "7564", "page": "12v", "date": "22 March 1756"}], crossrefs=[P310])
add_statement("st-chp10-p310-note4-smith-pitt-letter", NOTES, 491, 634, 633, 633,
              "cand-2440", "cand-1947", "identifies_smith_pitt_letter_locator",
              "Haskell identifies a letter from Smith to William Pitt dated 29 October 1760 in the Public Record Office, State Papers 99/68, folio 96.",
              "Haskell, footnote", "archival letter locator",
              "The manuscript and catalogue entry were not independently consulted. This is the source for the travel-plan statement only; it does not independently document the resignation statement.",
              ["cand-2440", "cand-1947", "cand-8289", "cand-9563", "cand-8983"], page=310, physical=39, marker=4,
              body_ids=["st-chp10-p310-smith-return-and-italy-travel-plan"],
              citations=[{"letter_candidate_id": "cand-9563", "sender_candidate_id": "cand-2440", "recipient_candidate_id": "cand-1947", "repository_candidate_id": "cand-8289", "series": "State Papers 99/68", "folio": "96", "date": "29 October 1760"}], crossrefs=[P310])
add_statement("st-chp10-p310-note5-adam-letters", NOTES, 491, 634, 634, 634,
              "cand-0011", "cand-9558", "cites_adam_letters_published_by_fleming",
              "Haskell cites letters from James Adam to Robert and Jenny Adam dated 20 and 27 August 1760, published by Fleming in 1962 at page 270.",
              "Haskell, footnote", "published letter citations",
              "The two letters and cited page were not independently consulted. The first date reuses the existing 20 August letter candidate; the second letter and Jenny Adam remain source-local and unresolved. OCR labels this as note 6, while p.310 shows printed note 5.",
              ["cand-0011", "cand-0012", "cand-9564", "cand-9519", "cand-9565", "cand-9520", "cand-9558"],
              page=310, physical=39, marker=5, body_ids=["st-chp10-p310-james-adam-meeting-and-assessment"],
              citations=[{"author_candidate_id": "cand-9520", "publication_candidate_id": "cand-9558", "year": "1962", "page": "270", "letter_candidates": ["cand-9519", "cand-9565"]}], crossrefs=[P310], ocr_marker=6)
add_statement("st-chp10-p310-note6-appendix-reference", NOTES, 491, 634, 634, 634,
              "cand-2440", None, "cross_references_appendix",
              "Haskell directs the reader to Appendix 5 for further information about Smith's 1762 sale to George III.",
              "Haskell, footnote", "internal cross-reference",
              "This is an internal pointer, not independent confirmation of the sale details. OCR labels this as note 8; p.310 shows printed note 6.",
              ["cand-2440", "cand-9278"], page=310, physical=39, marker=6,
              body_ids=["st-chp10-p310-1762-sale-to-george-iii"], citations=[{"internal_reference": "Appendix 5"}],
              crossrefs=[P310], ocr_marker=8)

# Confirm all references before editing body markers or tables.
all_candidate_ids = cids | new_cids
all_statement_ids = sids | new_sids
for row in new_mentions:
    if row["candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"missing mention candidate FK: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    for cid in [row["subject_candidate_id"], row["object_candidate_id"], *q["mentioned_candidate_ids"]]:
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"missing statement candidate FK: {row['statement_id']} -> {cid}")
    for sid in q.get("related_body_statement_ids", []):
        if sid not in all_statement_ids:
            raise SystemExit(f"missing body statement FK: {row['statement_id']} -> {sid}")

for sid, (marker, marker_line) in body_links.items():
    q = by_sid[sid]["qualifiers"]
    q["footnote_text_pending"] = False
    q["printed_marker_line"] = marker_line
series_statement["footnote_marker"] = 1
series_statement["footnote_text_pending"] = False
series_statement["printed_marker_line"] = 457
resignation.pop("footnote_marker", None)
resignation.pop("footnote_text_pending", None)
resignation.pop("printed_marker_line", None)

candidate_updates = {
    "cand-4863": "Local bibliography L203 identifies the article as Anthony Blunt, ‘The Palazzo Barberini: the contributions of Maderno, Bernini and Pietro da Cortona’ (Journal of the Warburg and Courtauld Institutes, 1958, pp.256-287); p.308 note 3 cites pp.283-284. The article and cited pages were not read.",
    "cand-9526": "Additional short-form citations: p.308 note 2, p.153, and p.309 note 1, p.161, alongside p.303 p.153. Treat as the same unresolved Cust publication candidate; title and cited pages remain unverified.",
    "cand-8508": "Additional locator p.5 in p.309 note 4. It may be the same Gradenigo source cited at p.260 note 4, p.91; title, edition, and cited pages remain unresolved.",
    "cand-9484": "P.310 note 2 cites p.11; cited page remains unread.",
    "cand-7137": "P.310 note 1 additionally cites pp.79-80 and 206; cited pages remain unread.",
    "cand-8598": "P.309 note 6 cites the published document at p.24 in connection with Smith's purchases from the Sagredo heirs; the document and publication page remain unread.",
    "cand-9340": "P.309 note 6 gives the joint publication short-form citation at p.24; cited page remains unread.",
    "cand-9485": "P.310 note 3 specifies register 7564, p.12v, dated 22 March 1756; this specific act is separately represented by cand-9562 and was not independently consulted.",
    "cand-8812": "P.309 note 2 cites p.1 of a Memmo 1786 work; title and exact work identity remain unresolved, and the cited page was not read.",
}
for cid, append_text in candidate_updates.items():
    if cid not in cids:
        raise SystemExit(f"candidate update target missing: {cid}")
    candidate = next(row for row in candidates if row["candidate_id"] == cid)
    if append_text in candidate["detail"]:
        raise SystemExit(f"candidate update already applied: {cid}")
    candidate["detail"] = (candidate["detail"].rstrip() + " " + append_text).strip()

new_coverage_notes = {
    NOTES: ("L492-634", "complete", "Merged notes processed through p.310 note 6 at L634. Printed p.308 notes 1-3, p.309 notes 1-6 and p.310 notes 1-6 are linked to body statements. P.308 note 1 continues at page-level OCR L466; p.309 OCR footnote numbers 6/8 correspond to printed notes 5/6, and p.310 OCR 6/8 likewise correspond to printed 5/6. The Vivian 1963 page range does not match the local 1963 bibliography entry; citation identity remains unresolved."),
    P307: ("L446-454", "complete", "Printed p.307 notes 1-4 are linked. Note 1 marker is printed at p.308 L457, where the sentence 'of Palladio' closes."),
    P308: ("L457-466", "complete", "Printed p.308 notes 1-3 are linked. The p.308 note-1 date explanation at L466 is retained as a page-level OCR continuation; note 1 marker follows 'of Palladio' at L457. P.308 body and cross-page sentence are complete through p.309 L469."),
    P309: ("L469-479", "complete", "Printed p.309 notes 1-6 are linked. Page image confirms OCR note numbers 6 and 8 at L628-L629 should be printed notes 5 and 6. The final Canaletto sentence closes at p.310 L482."),
    P310: ("L482-489", "complete", "Printed p.310 notes 1-6 are linked. Page image confirms OCR note numbers 6 and 8 at L634 should be printed notes 5 and 6. Note 4 supports the quoted travel-plan statement; it is not linked to the separate consulship-resignation statement. Note 6 points to Appendix 5."),
}
for segment_id, (ranges, status, note) in new_coverage_notes.items():
    cov[segment_id].update({"disposition": "reviewed", "migration_status": status,
                            "source_line_ranges": ranges, "note": note})

summary = {
    "mode": "APPLY" if __import__("sys").argv[-1:] == ["--apply"] else "DRY-RUN",
    "source_sha256": EXPECTED_ASSET_SHA,
    "notes_sha256": sha(notes_span), "p308_continuation_sha256": sha(continuation),
    "new_candidates": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "body_footnote_links": len(body_links) + 1,
    "removed_erroneous_marker": "st-chp10-p310-smith-resigned-consulship footnote 4",
    "coverage": {segment_id: values[:2] for segment_id, values in new_coverage_notes.items()},
}
print(json.dumps(summary, ensure_ascii=True, indent=2))

if __import__("sys").argv[-1:] == ["--apply"]:
    paths = (cp, mp, sp, vp)
    for path in paths:
        backup = Path(str(path) + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(cp, cf, candidates + new_candidates)
    write_csv(mp, mf, mentions + new_mentions)
    write_jsonl(sp, statements + new_statements)
    write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
    print("Applied with four recoverable table backups.")
