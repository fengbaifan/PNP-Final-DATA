"""Controlled S2 migration for the printed p.318 notes; dry-run by default."""

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
BODY = "chp-10:10_CHP-10_sec_ii:l133-142"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BACKUP_SUFFIX = ".bak-s2-chp10-p318-notes-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.318 note rows and links")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected = {
    300: "1 In a letter of 1766 quoted by Natali, p. 5.",
    301: "2 For Giannone’s residence and expulsion from Venice see Pierantoni; for Pilati see Brol.",
    302: "3 See J. G. Robertson and Moncallero, I.",
    303: "4 For Conti see Robertson, Chapter IV, and Vol. II of his Prose e Poesie, 1756.",
}
for line_no, text in expected.items():
    if source_lines[line_no - 1] != text:
        raise SystemExit(f"canonical p.318 note changed at L{line_no}")

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
statement_by_id = {row["statement_id"]: row for row in statements}
statement_ids = set(statement_by_id)
coverage = {row["segment_id"]: row for row in coverage_rows}

state = (len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates), len(mentions), len(statements))
if state != (9909, 9922, 21048, 9357):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment in (BODY, NOTES):
    if segment not in coverage:
        raise SystemExit(f"required coverage row missing: {segment}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.318 body is not reviewed/partial")
if coverage[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated footnote segment is not partial")
if any(sid.startswith("st-chp10-p318-n0") for sid in statement_ids):
    raise SystemExit("p.318 note statements already exist")
if any(row["mention_id"].startswith("m-s2-ch10-p318-note-") for row in mentions):
    raise SystemExit("p.318 note mentions already exist")
body_markers = [
    ("st-chp10-p318-voltaire-commented-on-intellectual-revival", 1, 300),
    ("st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled", 2, 301),
    ("st-chp10-p318-arcadia-and-french-critics-stimulated-debate", 3, 302),
    ("st-chp10-p318-conti-among-italian-intellectuals-seeking-travel", 4, 303),
]
for sid, marker, line in body_markers:
    row = statement_by_id.get(sid)
    if not row or row["qualifiers"].get("footnote_marker") != marker or row["qualifiers"].get("pending_note_source_line") != line:
        raise SystemExit(f"expected pending body footnote not found: {sid}")
for cid in ("cand-0114", "cand-0826", "cand-1164", "cand-1930", "cand-2791", "cand-2719", "cand-6460", "cand-8838", "cand-9685", "cand-9704", "cand-9716"):
    if cid not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {cid}")

new_candidates = []


def add_candidate(cid, name, kind, detail, line):
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
        "candidate_source_ref": f"{NOTES}#L{line}",
    })
    new_candidates.append(row)


add_candidate("cand-9923", "Natali (author cited at p.318 note 1; identity unresolved)", "person", "Surname-only author quoted for the 1766 letter; no full identity is inferred.", 300)
add_candidate("cand-9924", "Natali, page 5 (citation locator)", "archive", "Cited as the location where the 1766 letter is quoted. The cited page was not independently consulted.", 300)
add_candidate("cand-9925", "Voltaire letter of 1766 on Italian intellectual revival (quoted by Natali)", "archive", "Haskell links the preceding Voltaire comment to a letter quoted by Natali at page 5; recipient, title, manuscript, and current location are unspecified.", 300)
add_candidate("cand-9926", "Pierantoni (author cited at p.318 note 2; identity unresolved)", "person", "Surname-only author reference for Giannone’s residence and expulsion from Venice; no full identity is inferred.", 301)
add_candidate("cand-9927", "Pierantoni (citation locator for Giannone’s Venice residence and expulsion)", "archive", "The note supplies no title, date, or page; cited source not independently consulted.", 301)
add_candidate("cand-9928", "Brol (author cited at p.318 note 2; identity unresolved)", "person", "Surname-only reference for Pilati; no full identity is inferred.", 301)
add_candidate("cand-9929", "Brol (citation locator for Pilati)", "archive", "The note supplies no title, date, or page; cited source not independently consulted.", 301)
add_candidate("cand-9930", "J. G. Robertson (author cited at p.318 notes 3–4; identity unresolved)", "person", "Initials and surname only; full identity and the titles of cited works remain unresolved.", 302)
add_candidate("cand-9931", "Moncallero (author cited at p.318 note 3; identity unresolved)", "person", "Surname-only author reference; no full identity is inferred.", 302)
add_candidate("cand-9932", "J. G. Robertson and Moncallero, I (citation locator)", "archive", "The printed note gives a joint citation followed by Roman numeral I; its precise bibliographic meaning is not expanded here.", 302)
add_candidate("cand-9933", "J. G. Robertson, Chapter IV (citation locator for Conti)", "archive", "Cited in Haskell’s note for Antonio Conti. The work title and chapter contents are not supplied or independently checked.", 303)
add_candidate("cand-9934", "Conti, Prose e Poesie, volume II, 1756 (citation locator)", "archive", "The note says ‘his Prose e Poesie’ after ‘For Conti’; this is read contextually as Antonio Conti, pending confirmation from the bibliography. The volume was not consulted.", 303)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []
note_block = "\n".join(source_lines[272:349])


def add_mention(cid, line_no, needle, note):
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention candidate missing: {cid}")
    line = source_lines[line_no - 1]
    at = line.find(needle)
    if at < 0:
        raise SystemExit(f"mention needle missing at L{line_no}: {needle!r}")
    offset = sum(len(source_lines[index - 1]) + 1 for index in range(273, line_no)) + at
    if note_block[offset:offset + len(needle)] != needle:
        raise SystemExit(f"mention offset mismatch at L{line_no}: {needle!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p318-note-{len(new_mentions) + 1:04d}",
        "segment_id": NOTES,
        "candidate_id": cid,
        "surface_form": needle,
        "start_char": offset,
        "end_char": offset + len(needle),
        "note": note,
    })
    new_mentions.append(row)


for cid, line, needle, note in [
    ("cand-9925", 300, "letter of 1766", "The letter is identified only by year and its quotation in Natali."),
    ("cand-9923", 300, "Natali", "Surname of the cited author."),
    ("cand-9924", 300, "p. 5", "Specific page cited by Haskell."),
    ("cand-1164", 301, "Giannone", "Existing Pietro Giannone candidate reused."),
    ("cand-2719", 301, "Venice", "Existing Venice place candidate from the same body passage reused."),
    ("cand-9926", 301, "Pierantoni", "Surname of the cited author for Giannone."),
    ("cand-1930", 301, "Pilati", "Existing Carlo Antonio Pilati candidate reused."),
    ("cand-9928", 301, "Brol", "Surname of the cited author for Pilati."),
    ("cand-9930", 302, "J. G. Robertson", "Author named by initials and surname."),
    ("cand-9931", 302, "Moncallero", "Surname of the second cited author."),
    ("cand-0826", 303, "Conti", "Existing Antonio Conti candidate used by the linked body statement."),
    ("cand-9930", 303, "Robertson", "Surname of the cited author; identity is kept at the same unresolved candidate."),
    ("cand-9933", 303, "Chapter IV", "Chapter locator cited for Conti."),
    ("cand-9934", 303, "Prose e Poesie", "Work title and volume locator named in the note."),
]:
    add_mention(cid, line, needle, note)

new_statements = []


def add_statement(sid, subject, object_id, predicate, line, claim, qualification, mentioned, body_id, marker,
                  relation_candidate=False, extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement ID already exists: {sid}")
    quote = source_lines[line - 1]
    if not quote.startswith(f"{line - 299} "):
        raise SystemExit(f"note quote boundary changed: {sid}")
    if subject not in all_candidate_ids or object_id not in all_candidate_ids:
        raise SystemExit(f"statement candidate missing: {sid}")
    mentioned = list(dict.fromkeys(mentioned))
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"statement mention candidate missing: {sid}")
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": 318,
        "pdf_physical_page": 51,
        "claim": claim,
        "speaker": "Haskell footnote",
        "text_layer": "bibliographic citation",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
        "footnote_number": marker,
        "linked_body_statement_ids": [body_id],
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


add_statement("st-chp10-p318-n01-voltaire-letter-natali-citation", "cand-2791", "cand-9925", "comment_in_1766_letter_quoted_by_natali",
              300, "Haskell links the preceding report of Voltaire’s 1766 comment on Italian intellectual revival to a letter quoted by Natali, page 5.",
              "The recipient, title, and manuscript details are not given; Natali’s page was not independently consulted.",
              ["cand-2791", "cand-0974", "cand-9923", "cand-9924", "cand-9925"],
              "st-chp10-p318-voltaire-commented-on-intellectual-revival", 1, True,
              {"citations": [{"source_candidate_id": "cand-9924", "author_candidate_id": "cand-9923", "page": "5"}], "letter_date": "1766"})
add_statement("st-chp10-p318-n02-pierantoni-giannone-citation", "cand-1164", "cand-9927", "cites_pierantoni_for_giannone_venice_residence_and_expulsion",
              301, "Haskell directs readers to Pierantoni for Giannone’s residence in Venice and expulsion from the city.",
              "The title, date, and page are not supplied; the cited source was not independently consulted.",
              ["cand-1164", "cand-2719", "cand-9926", "cand-9927"],
              "st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled", 2,
              extra={"citations": [{"source_candidate_id": "cand-9927", "author_candidate_id": "cand-9926"}]})
add_statement("st-chp10-p318-n02-brol-pilati-citation", "cand-1930", "cand-9929", "cites_brol_for_pilati",
              301, "Haskell directs readers to Brol for Pilati.",
              "The note does not specify which details about Pilati are covered; the cited source was not independently consulted.",
              ["cand-1930", "cand-9928", "cand-9929"],
              "st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled", 2,
              extra={"citations": [{"source_candidate_id": "cand-9929", "author_candidate_id": "cand-9928"}]})
add_statement("st-chp10-p318-n03-robertson-moncallero-debate-citation", "cand-6460", "cand-9932", "cites_robertson_and_moncallero_for_debate",
              302, "Haskell cites J. G. Robertson and Moncallero, I, in the note attached to the account of debate about fantasy and reason.",
              "The printed Roman numeral I is retained without assuming whether it denotes a volume or another subdivision; neither cited work was independently consulted.",
              ["cand-6460", "cand-0992", "cand-2110", "cand-9716", "cand-9930", "cand-9931", "cand-9932"],
              "st-chp10-p318-arcadia-and-french-critics-stimulated-debate", 3,
              extra={"citations": [{"source_candidate_id": "cand-9932", "author_candidate_ids": ["cand-9930", "cand-9931"], "printed_locator": "I"}]})
add_statement("st-chp10-p318-n04-robertson-chapter-iv-conti-citation", "cand-0826", "cand-9933", "cites_robertson_chapter_iv_for_conti",
              303, "Haskell directs readers to Robertson, Chapter IV, for Antonio Conti.",
              "The work title and cited chapter were not identified or independently consulted.",
              ["cand-0826", "cand-9930", "cand-9933"],
              "st-chp10-p318-conti-among-italian-intellectuals-seeking-travel", 4,
              extra={"citations": [{"source_candidate_id": "cand-9933", "author_candidate_id": "cand-9930", "chapter": "IV"}]})
add_statement("st-chp10-p318-n04-conti-prose-e-poesie-citation", "cand-0826", "cand-9934", "cites_prose_e_poesie_volume_ii_1756_for_conti",
              303, "Haskell also cites volume II of Prose e Poesie, dated 1756, in the note on Antonio Conti.",
              "The pronoun ‘his’ is read contextually as Antonio Conti because he is the immediate antecedent; confirm against the bibliography. The volume was not consulted.",
              ["cand-0826", "cand-9934"],
              "st-chp10-p318-conti-among-italian-intellectuals-seeking-travel", 4,
              extra={"citations": [{"source_candidate_id": "cand-9934", "author_candidate_id": "cand-0826", "year": "1756", "volume": "II"}],
                     "pronoun_resolution": "his -> Antonio Conti, provisional contextual reading"})

all_statements = statements + new_statements
statement_by_id = {row["statement_id"]: row for row in all_statements}


def add_footnote_ref(body_statement_id, marker, line, note_ids):
    row = statement_by_id.get(body_statement_id)
    if not row:
        raise SystemExit(f"body statement missing: {body_statement_id}")
    q = row["qualifiers"]
    if q.get("footnote_marker") != marker or q.get("pending_note_source_line") != line:
        raise SystemExit(f"unexpected footnote marker/line: {body_statement_id}")
    q["footnote_text_pending"] = False
    q["footnote_segment"] = NOTES
    ref = {"marker": marker, "segment_id": NOTES, "source_line": line}
    refs = q.setdefault("footnote_refs", [])
    if ref not in refs:
        refs.append(ref)
    ids = q.setdefault("footnote_statement_ids", [])
    for sid in note_ids:
        if sid not in ids:
            ids.append(sid)
    q["footnote_body_link_status"] = "linked"


add_footnote_ref("st-chp10-p318-voltaire-commented-on-intellectual-revival", 1, 300,
                 ["st-chp10-p318-n01-voltaire-letter-natali-citation"])
add_footnote_ref("st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled", 2, 301,
                 ["st-chp10-p318-n02-pierantoni-giannone-citation", "st-chp10-p318-n02-brol-pilati-citation"])
add_footnote_ref("st-chp10-p318-arcadia-and-french-critics-stimulated-debate", 3, 302,
                 ["st-chp10-p318-n03-robertson-moncallero-debate-citation"])
add_footnote_ref("st-chp10-p318-conti-among-italian-intellectuals-seeking-travel", 4, 303,
                 ["st-chp10-p318-n04-robertson-chapter-iv-conti-citation", "st-chp10-p318-n04-conti-prose-e-poesie-citation"])

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate ID")
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention ID")
if len({row["statement_id"] for row in all_statements}) != len(all_statements):
    raise SystemExit("duplicate statement ID")
candidate_id_set = {row["candidate_id"] for row in candidate_rows}
if any(row["candidate_id"] not in candidate_id_set for row in new_mentions):
    raise SystemExit("missing mention candidate foreign key")
for row in new_statements:
    if row["subject_candidate_id"] not in candidate_id_set or row["object_candidate_id"] not in candidate_id_set:
        raise SystemExit(f"missing statement endpoint: {row['statement_id']}")
    if any(cid not in candidate_id_set for cid in row["qualifiers"]["mentioned_candidate_ids"]):
        raise SystemExit(f"missing statement mention foreign key: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in new_mentions)
for left, right in zip(spans, spans[1:]):
    if left[1] > right[0]:
        raise SystemExit(f"overlapping p.318 note mention spans: {left[2]} and {right[2]}")

coverage[BODY].update({
    "migration_status": "complete",
    "source_line_ranges": "L131,L134-142; notes L300-303",
    "note": "Printed p.318 was checked against CHP-10.pdf physical p.51. Body claims and notes 1–4 at canonical L300–303 are reviewed and linked. Natali, Pierantoni, Brol, Robertson, and Moncallero remain unresolved shorthand citations; the source chronology and attribution are not independently verified.",
})
coverage[NOTES].update({
    "source_line_ranges": "L274-303; L325-349",
    "note": "P.311–318 notes L274–303 are reviewed and linked; L325–349 was previously processed. The remaining gap is L304–324 (p.319–323 notes).",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_statements.sort(key=lambda row: row["statement_id"])
print(f"p.318 note preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage changes: p.318 partial->complete; consolidated note coverage extends through L303")
print(f"totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(all_statements)} statements")
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
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
