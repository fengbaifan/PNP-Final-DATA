"""Controlled S2 migration for p.287 notes in merged source L535-L539.

Printed note 2 is already captured in body segment L215-L216 and is deliberately
not duplicated here. OCR note 5 is numbered 6 and reads Vertuc; the print reads
5 and Vertue.
"""
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
NOTES_SEGMENT = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINES_SHA = "3b00c3d3c0d437990930793bc40735a651dfe3ef96f14dc24d302e8a60631156"
BACKUP = ".bak-s2-chp10-p287-notes1-3-5-6-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_body = "\n".join(src[490:634])
if hashlib.sha256(notes_body.encode("utf-8")).hexdigest() != EXPECTED_NOTES_SHA:
    raise SystemExit("merged note segment changed")
if hashlib.sha256("\n".join(src[534:539]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.287 notes 1, 3-6 changed")
if not src[534].startswith("1 English Taste") or not src[535].startswith("3 Watson"):
    raise SystemExit("p.287 notes 1 or 3 changed")
if not src[536].startswith("4 McSwiny spelt") or not src[537].startswith("6 Vertuc") or not src[538].startswith("6 There have been many articles"):
    raise SystemExit("p.287 notes 4-6 changed")

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9349:
    raise SystemExit(f"candidate sequence changed: {maximum}")
notes_cov = cov.get(NOTES_SEGMENT)
if not notes_cov or (notes_cov["disposition"], notes_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("merged note coverage status changed")
if notes_cov["source_line_ranges"] != "L492-534":
    raise SystemExit(f"merged note coverage range changed: {notes_cov['source_line_ranges']}")

BODY_TARGETS = {
    "st-chp10-p287-amigoni-canvases": (1, 535),
    "st-chp10-p287-venetian-patronage": (3, 536),
    "st-chp10-p287-mcswiny-stage-career": (4, 537),
    "st-chp10-p287-van-dyck-engraving-plan": (5, 538),
    "st-chp10-p287-van-dyck-plan-failed": (5, 538),
    "st-chp10-p287-mcswiny-tomb-scheme": (6, 539),
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(BODY_TARGETS) <= by_sid.keys():
    raise SystemExit(f"p.287 body note targets missing: {set(BODY_TARGETS)-by_sid.keys()}")
for sid, (marker, source_line) in BODY_TARGETS.items():
    q = by_sid[sid].get("qualifiers", {})
    if q.get("footnote_marker") != marker or not q.get("footnote_text_pending"):
        raise SystemExit(f"p.287 marker {marker} state changed on {sid}")
note2 = by_sid.get("st-chp10-p287-footnote-2")
if not note2 or note2.get("segment_id") != "chp-10:10_CHP-10_intro:l206-216" or note2.get("qualifiers", {}).get("footnote_text_pending"):
    raise SystemExit("p.287 printed note 2 is not already resolved in the body segment")

REQUIRED = {"cand-1466", "cand-2803", "cand-5903", "cand-5986", "cand-5874", "cand-5875",
            "cand-7255", "cand-8467", "cand-8933", "cand-9347", "cand-1602", "cand-0822"}
if not REQUIRED <= cids:
    raise SystemExit(f"required existing candidates missing: {REQUIRED-cids}")

NEW_CANDIDATES = [
    ("cand-9350", "English Taste in the Eighteenth Century, 1955-6, p.26 (citation locator; author unresolved)", "archive",
     "Short-form source cited for Amigoni's Jupiter and Io canvases. The title, date range and page are recorded as Haskell gives them; the cited source was not consulted."),
    ("cand-9351", "Hussey (surname-only author in p.287 note 1; identity unresolved)", "person",
     "Haskell cites Hussey, 1955, p.43. No first name or work title is supplied."),
    ("cand-9352", "Hussey, 1955, p.43 (citation locator; work unresolved)", "archive",
     "Short-form source locator in Haskell's p.287 note 1; cited page was not consulted."),
    ("cand-9353", "Watson (surname-only author in p.287 notes 3 and 6; possible identity with cand-2803 unresolved)", "person",
     "Watson is cited for a 1949 Burlington Magazine article and a 1953 article on McSwiny commissions. The surname-only references are kept open; identity with F. J. B. Watson (cand-2803) is for S3."),
    ("cand-9354", "Watson, Burlington Magazine, 1949, pp.75-79 (article locator; title unresolved)", "archive",
     "Short-form locator in p.287 note 3. The article title and cited pages were not consulted."),
    ("cand-9355", "Whitley (surname-only author in p.287 note 4; identity unresolved)", "person",
     "Haskell gives only the surname Whitley with volume I pages 9, 11 and 24-26; identity is not inferred."),
    ("cand-9356", "Whitley, vol.I, pp.9, 11, 24-26 (citation locator; work unresolved)", "archive",
     "Short-form source locator in Haskell's p.287 note 4; OCR 'ir' at p.11 is corrected from the print in S2; cited pages were not consulted."),
    ("cand-9357", "Unidentified librettos for operas adapted by Owen McSwiny, reported at the British Museum", "archive",
     "Haskell's p.287 note 4 says a number of librettos for operas adapted by McSwiny were then in the British Museum. The number, titles and current holdings are not specified or independently verified."),
    ("cand-9358", "Voss (surname-only author in p.287 note 6; possible identity with cand-5874 unresolved)", "person",
     "Haskell cites Voss, 1926, pp.32-37. The existing Voss candidate concerns another short-form citation; identity is deferred to S3."),
    ("cand-9359", "Voss, 1926, pp.32-37 (citation locator; work unresolved)", "archive",
     "One of the references listed for articles on McSwiny's commissions. Title and venue are not supplied and the cited pages were not consulted."),
    ("cand-9360", "Arslan (surname-only author in p.287 note 6; possible identity with cand-8467 unresolved)", "person",
     "Haskell lists Arslan references from 1932, 1933 and 1955. A chapter-9 Arslan candidate exists, but cross-chapter identity is deferred to S3."),
    ("cand-9361", "Arslan, 1932, pp.128-140 (citation locator; work unresolved)", "archive",
     "Short-form reference in Haskell's p.287 note 6; cited pages were not consulted."),
    ("cand-9362", "Arslan, 1933, pp.244-248 (citation locator; work unresolved)", "archive",
     "Continuation of the Arslan reference in Haskell's p.287 note 6; cited pages were not consulted."),
    ("cand-9363", "Zucchini (surname-only author in p.287 note 6; identity unresolved)", "person",
     "Haskell lists a 1933 Zucchini citation for McSwiny commissions; no full name is supplied."),
    ("cand-9364", "Zucchini, 1933, pp.23-30 (citation locator; work unresolved)", "archive",
     "Short-form reference in Haskell's p.287 note 6; cited pages were not consulted."),
    ("cand-9365", "Borenius (surname-only author in p.287 note 6; identity unresolved)", "person",
     "Haskell lists a 1936 Borenius citation for McSwiny commissions; no full name is supplied."),
    ("cand-9366", "Borenius, 1936, pp.245-246 (citation locator; work unresolved)", "archive",
     "Short-form reference in Haskell's p.287 note 6; cited pages were not consulted."),
    ("cand-9367", "Watson, 1953, pp.362-365 (citation locator; work unresolved)", "archive",
     "Short-form reference in Haskell's p.287 note 6; title and venue are not supplied and cited pages were not consulted."),
    ("cand-9368", "Constable (surname-only author in p.287 note 6; distinct from artist cand-0822, identity unresolved)", "person",
     "Haskell cites Constable, 1954, p.154 for McSwiny commissions. Do not merge with John Constable; no full author identity is supplied."),
    ("cand-9369", "Constable, 1954, p.154 (citation locator; work unresolved)", "archive",
     "Short-form reference in Haskell's p.287 note 6; OCR punctuation is checked against print and the cited page was not consulted."),
    ("cand-9370", "Arslan, 1955, pp.189-192 (citation locator; work unresolved)", "archive",
     "Short-form reference in Haskell's p.287 note 6; associated surname-only author candidate cand-9360; cited pages were not consulted."),
    ("cand-9371", "Rivani (bracketed surname in p.287 note 6; identity unresolved)", "person",
     "The source brackets the surname [Rivani] before 1959, preserving uncertainty in the citation; no identity is inferred."),
    ("cand-9372", "[Rivani], 1959 (bracketed citation locator; work unresolved)", "archive",
     "Haskell brackets the surname and gives only the year. The source and the reason for brackets are not established."),
    ("cand-9373", "Mazza (surname-only author in p.287 note 6; distinct from artist cand-1602, identity unresolved)", "person",
     "Haskell lists a Mazza, 1976 citation. Do not identify the author with Giuseppe Mazza; the work and author remain unresolved."),
    ("cand-9374", "Mazza, 1976 (citation locator in p.287 note 6; work unresolved)", "archive",
     "Short-form reference listed for articles on McSwiny commissions; title, venue and cited content are not supplied or consulted."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if len(new_ids) != 25 or new_ids & cids:
    raise SystemExit("planned candidate IDs changed or already exist")
new_candidates = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES_SEGMENT}#L{535 if cid in {'cand-9350','cand-9351','cand-9352'} else 536 if cid in {'cand-9353','cand-9354'} else 537 if cid in {'cand-9355','cand-9356','cand-9357'} else 539}",
} for cid, name, kind, detail in NEW_CANDIDATES]

new_mentions = []
notes_start = sum(len(src[n - 1]) + 1 for n in range(491, 535))


def add_mention(local, line_no, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p287notes-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[line_no - 1]
    at = line.find(surface)
    if at < 0:
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = notes_start + sum(len(src[n - 1]) + 1 for n in range(535, line_no)) + at
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": NOTES_SEGMENT, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention("n1-english-taste", 535, "English Taste in the Eighteenth Century, 1955-6, p. 26", "cand-9350", "Citation locator only; cited page not consulted.")
add_mention("n1-hussey-author", 535, "Hussey", "cand-9351", "Surname-only author; identity unresolved.")
add_mention("n1-hussey-locator", 535, "Hussey, 1955, p. 43", "cand-9352", "Citation locator only; cited page not consulted.")
add_mention("n3-watson-author", 536, "Watson", "cand-9353", "Surname-only author; possible identity with cand-2803 deferred to S3.")
add_mention("n3-burlington", 536, "Burlington Magazine", "cand-5903", "Periodical named in citation; article not consulted.")
add_mention("n3-watson-locator", 536, "Watson, in Burlington Magazine, 1949, pp. 75-9", "cand-9354", "Citation locator only; title and cited pages unresolved/unread.")
add_mention("n4-mcswiny", 537, "McSwiny", "cand-1466")
add_mention("n4-dnb", 537, "Dictionary of National Biography", "cand-9347", "Short-form reference; edition and cited entry not supplied or consulted.")
add_mention("n4-whitley-author", 537, "Whitley", "cand-9355", "Surname-only author; identity unresolved.")
add_mention("n4-whitley-locator", 537, "Whitley, I, pp. 9, ir, 24-6", "cand-9356", "OCR 'ir' reads as print '11'; cited pages not consulted.")
add_mention("n4-librettos", 537, "a number of librettos for operas adapted by him which are now in the British Museum", "cand-9357", "Unidentified archive group; the number and titles are not given, and 'now' is source-relative.")
add_mention("n4-british-museum", 537, "British Museum", "cand-5986", "Repository named in Haskell's note; present-day holdings not verified.")
add_mention("n5-vertue-author", 538, "Vertuc", "cand-8933", "OCR reads 'Vertuc'; print reads Vertue.")
add_mention("n5-vertue-locator", 538, "Vertuc, III, p. 82", "cand-7255", "Print reads Vertue, vol.III, p.82; citation locator only, page not consulted.")
add_mention("n6-mcswiny", 539, "McSwiny", "cand-1466")
add_mention("n6-voss-author", 539, "Voss", "cand-9358", "Surname-only author; possible identity with cand-5874 deferred to S3.")
add_mention("n6-voss-locator", 539, "Voss, 1926, pp. 32-7", "cand-9359", "Citation locator only; cited pages not consulted.")
add_mention("n6-arslan-author", 539, "Arslan", "cand-9360", "Surname-only author; possible identity with cand-8467 deferred to S3.")
add_mention("n6-arslan-1932", 539, "Arslan, 1932, pp. 128-40", "cand-9361", "Citation locator only; cited pages not consulted.")
add_mention("n6-arslan-1933", 539, "1933, pp. 244-8", "cand-9362", "Continuation of the preceding Arslan citation; cited pages not consulted.")
add_mention("n6-zucchini-author", 539, "Zucchini", "cand-9363", "Surname-only author; identity unresolved.")
add_mention("n6-zucchini-locator", 539, "Zucchini, 1933, pp. 23-30", "cand-9364", "Citation locator only; cited pages not consulted.")
add_mention("n6-borenius-author", 539, "Borenius", "cand-9365", "Surname-only author; identity unresolved.")
add_mention("n6-borenius-locator", 539, "Borenius, 1936, pp. 245-6", "cand-9366", "Citation locator only; cited pages not consulted.")
add_mention("n6-watson-author", 539, "Watson", "cand-9353", "Surname-only author; reused within this note cluster; identity with F.J.B. Watson remains for S3.")
add_mention("n6-watson-locator", 539, "Watson, 1953, pp. 362-5", "cand-9367", "Citation locator only; title and cited pages not consulted.")
add_mention("n6-constable-author", 539, "Constable", "cand-9368", "Surname-only author; distinct identity from artist John Constable is unresolved, do not merge.")
add_mention("n6-constable-locator", 539, "Constable, 1954, p. 154!", "cand-9369", "OCR punctuation checked against print; citation locator only, page not consulted.")
add_mention("n6-arslan-1955", 539, "Arslan, 1955, pp. 189-92", "cand-9370", "Citation locator only; author candidate remains surname-only and pages unread.")
add_mention("n6-rivani-author", 539, "Rivani", "cand-9371", "The surname is bracketed in print; the reason for brackets is unresolved.")
add_mention("n6-rivani-locator", 539, "[Rivani] 1959", "cand-9372", "Bracketed surname and year only; no title or cited content supplied.")
add_mention("n6-mazza-author", 539, "Mazza", "cand-9373", "Surname-only author; do not merge with artist Giuseppe Mazza, cand-1602.")
add_mention("n6-mazza-locator", 539, "Mazza, 1976", "cand-9374", "Citation locator only; title, venue and cited content are unresolved.")

if len(new_mentions) != 33:
    raise SystemExit(f"planned p.287 note mention count changed: {len(new_mentions)}")
if len(new_ids) != 25:
    raise SystemExit(f"planned p.287 candidate count changed: {len(new_ids)}")

SPELL_STATEMENT = "st-chp10-notes-p287-mcswiny-spelling-variants"
LIBRETTO_STATEMENT = "st-chp10-notes-p287-librettos-held-british-museum"
LITERATURE_STATEMENT = "st-chp10-notes-p287-literature-on-mcswiny-commissions"
new_statement_ids = {SPELL_STATEMENT, LIBRETTO_STATEMENT, LITERATURE_STATEMENT}
if new_statement_ids & sids:
    raise SystemExit("one or more planned statement IDs already exist")
line4 = src[536]
spell_quote = "McSwiny spelt his name in a great number of different ways at various stages in his career"
libretto_quote = "a number of librettos for operas adapted by him which are now in the British Museum"
line6 = src[538]
line6_quote = line6[2:]
if spell_quote not in line4 or libretto_quote not in line4 or "There have been many articles" not in line6_quote:
    raise SystemExit("p.287 note 4/6 claim text changed")

new_statements = [
    {
        "statement_id": SPELL_STATEMENT, "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-1466", "object_candidate_id": None,
        "predicate": "mcswiny_name_spelling_varied_across_career_stages",
        "qualifiers": {
            "source_line_start": 537, "source_line_end": 537, "printed_page": 287, "pdf_physical_page": 16,
            "claim": "Haskell says McSwiny spelled his name in many different ways at different stages of his career; this note does not enumerate those forms.",
            "speaker": "Haskell, footnote", "text_layer": "authorial note",
            "qualification": "Haskell cites the Dictionary of National Biography and Whitley for career outlines. The citation pages were not consulted, and no individual spelling variant or identity distinction is inferred.",
            "mentioned_candidate_ids": ["cand-1466", "cand-9347", "cand-9355", "cand-9356"],
            "footnote_number": 4, "related_body_statement_ids": ["st-chp10-p287-mcswiny-stage-career"],
            "relation_candidate": False, "cited_material_not_independently_consulted": True,
        },
        "original_quote": spell_quote + ",", "origin": "book", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    },
    {
        "statement_id": LIBRETTO_STATEMENT, "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-9357", "object_candidate_id": "cand-5986",
        "predicate": "haskell_reports_librettos_for_mcswiny_adapted_operas_at_british_museum",
        "qualifiers": {
            "source_line_start": 537, "source_line_end": 537, "printed_page": 287, "pdf_physical_page": 16,
            "claim": "Haskell says that a number of librettos for operas adapted by McSwiny were then at the British Museum.",
            "speaker": "Haskell, footnote", "text_layer": "authorial note",
            "qualification": "The number and titles are not given. 'Now' is Haskell's source-time report, not a verification of current holdings. The librettos are not individually identified and no individual work relation is inferred.",
            "mentioned_candidate_ids": ["cand-1466", "cand-9357", "cand-5986"],
            "footnote_number": 4, "related_body_statement_ids": ["st-chp10-p287-mcswiny-stage-career"],
            "relation_candidate": True, "cited_material_not_independently_consulted": True,
        },
        "original_quote": libretto_quote + ".", "origin": "book", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    },
    {
        "statement_id": LITERATURE_STATEMENT, "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-1466", "object_candidate_id": None,
        "predicate": "haskell_lists_literature_on_mcswiny_commissions",
        "qualifiers": {
            "source_line_start": 539, "source_line_end": 539, "printed_page": 287, "pdf_physical_page": 16,
            "claim": "Haskell says many articles on McSwiny's commissions had appeared and lists references dated 1926-1976.",
            "speaker": "Haskell, footnote", "text_layer": "bibliographical note",
            "qualification": "This records Haskell's characterization and citation list only; none of the listed works was consulted, and their titles or findings are not inferred.",
            "mentioned_candidate_ids": [row[0] for row in NEW_CANDIDATES if row[2] in {"archive", "person"}],
            "footnote_number": 6, "related_body_statement_ids": ["st-chp10-p287-mcswiny-tomb-scheme"],
            "relation_candidate": False, "cited_material_not_independently_consulted": True,
        },
        "original_quote": line6_quote, "origin": "book", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    },
]

cand_by_id = {row["candidate_id"]: row for row in candidates}
cand_by_id["cand-7255"]["detail"] = (cand_by_id["cand-7255"].get("detail", "") +
    " P.287 note 5 cites vol.III p.82; the scan reads Vertue while OCR has Vertuc and misnumbers this printed note 5 as 6. The cited page was not consulted.").strip()
cand_by_id["cand-9347"]["detail"] = (cand_by_id["cand-9347"].get("detail", "") +
    " P.287 note 4 also cites the Dictionary for McSwiny's biographical outline; the entry was not consulted.").strip()
cand_by_id["cand-5986"]["detail"] = (cand_by_id["cand-5986"].get("detail", "") +
    " Haskell's p.287 note 4 reports unidentified librettos for McSwiny-adapted operas there at source-time; this does not verify current holdings.").strip()
cand_by_id["cand-5903"]["detail"] = (cand_by_id["cand-5903"].get("detail", "") +
    " P.287 note 3 cites a 1949 Watson article at pp.75-79; the article was not consulted.").strip()

note_statement_for_marker = {1: [], 3: [], 4: [SPELL_STATEMENT, LIBRETTO_STATEMENT], 5: [], 6: [LITERATURE_STATEMENT]}
marker_to_line = {1: 535, 3: 536, 4: 537, 5: 538, 6: 539}
for sid, (marker, source_line) in BODY_TARGETS.items():
    q = by_sid[sid]["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES_SEGMENT
    q["footnote_source_line"] = source_line
    q["footnote_note_statement_ids"] = note_statement_for_marker[marker]
    addendum = {
        1: " P.287 note 1 cites English Taste (1955-6, p.26) and Hussey (1955, p.43); both references remain unread.",
        3: " P.287 note 3 cites Watson in Burlington Magazine (1949, pp.75-79); article title and content remain unverified.",
        4: " P.287 note 4 adds Haskell's claim about McSwiny's spelling variants and a source-time report of unidentified librettos at the British Museum; note statements preserve these separately.",
        5: " P.287 printed note 5 cites Vertue, vol.III p.82; OCR misnumbers it as 6 and reads Vertuc. The scan correction is recorded in S2 only.",
        6: " P.287 note 6 lists scholarship on McSwiny commissions; citation references are recorded without asserting their contents.",
    }[marker]
    q["qualification"] = (q.get("qualification", "") + addendum).strip()
    q["cited_material_not_independently_consulted"] = True

new_candidates = new_candidates
candidates_by_id_new = {row["candidate_id"]: row for row in new_candidates}
all_references_for_literature = sorted(new_ids)
new_statements[-1]["qualifiers"]["mentioned_candidate_ids"] = ["cand-1466"] + all_references_for_literature

notes_cov["source_line_ranges"] = "L492-539"
notes_cov["note"] = (notes_cov.get("note", "") +
    " P.287 printed notes 1, 3-6 at L535-L539 are migrated; printed note 2 is already captured with its quotation in body segment l206-216 and is not duplicated. Note 1 cites English Taste and Hussey; note 3 cites Watson/Burlington Magazine; note 4 records McSwiny spelling variation, DNB/Whitley references and unidentified libretto holdings at the British Museum; note 5 is OCRed as 6/Vertuc but print reads 5/Vertue; note 6 lists scholarship on McSwiny commissions. Three source-grounded statements were added for note 4 and note 6; cited works remain unread. L540 onward remains pending.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p287 merged notes L535-L539 verified against CHP-10.pdf physical page 16")
print("printed note 2 is already represented in body L215-L216; migrating notes 1, 3, 4, 5, 6 only")
print("planned new candidates=25, mentions=33, statements=3; source citations remain unverified")
print("p287 note 5 OCR 6/Vertuc corrected to printed 5/Vertue in S2 only")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
candidates.extend(new_candidates)
mentions.extend(new_mentions)
statements.extend(new_statements)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print(f"applied; recovery copies use suffix {BACKUP}")
