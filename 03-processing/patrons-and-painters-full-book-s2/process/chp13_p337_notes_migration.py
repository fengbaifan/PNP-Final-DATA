"""Controlled S2 migration for p.337 footnotes; dry-run by default."""
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
BODY = "chp-13:13_CHP-13_intro:l52-59"
NEXT_BODY = "chp-13:13_CHP-13_intro:l61-68"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p337-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.337 footnote migration")
args = parser.parse_args()


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_prefixes = {
    53: "succeeding in the affairs that interest him",
    203: "1 [Andrea Memmo], 1786, p. 45.",
    204: "2 See his letter of 7 January 1785/6",
    205: "3 Archivio di Stato, Venice—Inquisitori di Stato, 537, p. Z2v",
    206: "4 Novelle della Repubblica delle Lettere, 8 Settembre 1736.",
    207: "5 Morazzoni, p. 116.",
    208: "6 Delle Commedie di Carlo Goldoni avvocato veneto, Vol. I, 1761",
}
for line_number, prefix in expected_prefixes.items():
    if not source_lines[line_number - 1].startswith(prefix):
        raise SystemExit(f"canonical source changed at L{line_number}")

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

state = (
    len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions), len(statements),
)
if state != (10150, 10163, 21948, 9810):
    raise SystemExit(f"unexpected table pre-state: {state}")
if set((BODY, NEXT_BODY, NOTES)) - set(coverage):
    raise SystemExit("required coverage row missing")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.337 body is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes segment is not reviewed/partial")
if any(row["segment_id"] == NOTES and row["mention_id"].startswith("m-s2-ch13-p337-notes-") for row in mentions):
    raise SystemExit("p.337 note mentions already exist")
if any(row["statement_id"].startswith("st-chp13-p337-note") for row in statements):
    raise SystemExit("p.337 note statements already exist")

body_ids = {
    "pasquali_admired": "st-chp13-p337-pasquali-admired-lodoli",
    "pasquali_censorship": "st-chp13-p337-pasquali-chafed-under-censorship",
    "beccaria_distribution": "st-chp13-p337-pasquali-secretly-distributed-beccaria-1764",
    "client_disclosure": "st-chp13-p337-pasquali-revealed-book-clients-under-pressure",
    "english_grammar": "st-chp13-p337-english-grammar-among-pasquali-early-books",
    "officium_commission": "st-chp13-p337-pasquali-employed-piazzetta-for-officium",
    "officium_plates": "st-chp13-p337-officium-plates-religious-intimacy",
    "goldoni_commercial": "st-chp13-p337-goldoni-criticised-earlier-commercial-production",
    "goldoni_economy": "st-chp13-p337-goldoni-said-paper-and-printing-economised",
    "goldoni_attention": "st-chp13-p337-goldoni-promised-increased-production-attention",
    "goldoni_cost": "st-chp13-p337-goldoni-acknowledged-higher-cost",
    "goldoni_page": "st-chp13-p337-goldoni-favoured-elegant-clean-page",
    "false_same_line": "st-chp13-p337-smith-controlled-interest-in-pasquali-firm",
}
if set(body_ids.values()) - set(statement_by_id):
    raise SystemExit("one or more expected p.337 body statements are missing")
if statement_by_id[body_ids["english_grammar"]]["qualifiers"].get("footnote_marker") != 4:
    raise SystemExit("printed p.337 note 4 is not attached to the English-grammar statement")
if statement_by_id[body_ids["false_same_line"]]["qualifiers"].get("footnote_marker") != 4:
    raise SystemExit("expected same-line false p.337 note 4 marker was not found")

candidate_specs = [
    ("cand-10164", "Conti (surname-only author of the 1728 letter cited at p.337 n.1; identity unresolved)", "person",
     "Surname-only author of a 1728 letter to Vico cited through Fisch and Bergin. Several indexed Conti candidates exist; identity alignment is deferred to S3." , 203),
    ("cand-10165", "Conti’s letter to Vico (1728; cited through Fisch and Bergin, p.184)", "archive",
     "Letter named as evidence for Lodoli’s influence. Haskell cites its publication through Fisch and Bergin; neither the letter nor the cited pages were independently consulted here.", 203),
    ("cand-10166", "Andrea Memmo, 1786, p.45 (p.337 note 1 citation locator)", "archive",
     "Citation locator only. The note supplies author, year, and page; this page was not independently consulted in this batch.", 203),
    ("cand-10167", "Pasquali’s letter to Niccola Mazzoni, 7 January 1785/6 (cited through Nuti, 1941, p.199)", "archive",
     "Letter and Italian quotation are reported by Haskell through Nuti’s 1941 publication. The letter and cited page were not independently consulted.", 204),
    ("cand-10168", "Nuti (surname-only author cited in p.337 note 2; identity unresolved)", "person",
     "Surname-only author of the 1941 publication cited for Pasquali’s letter to Niccola Mazzoni; full identity and work title are not supplied in the note.", 204),
    ("cand-10169", "Nuti, 1941, p.199 (p.337 note 2 citation locator)", "archive",
     "Citation locator only for the publication of Pasquali’s letter. The cited work and page were not independently consulted.", 204),
    ("cand-10170", "Prato (city identified as the location of bookseller Niccola Mazzoni)", "place",
     "The body and note identify Mazzoni as a bookseller in Prato. No shop address or further location is supplied.", 204),
    ("cand-10171", "Tuscany (region named in Pasquali’s quoted letter, p.337 note 2)", "place",
     "Geographic region named in the Italian quotation. This is a context-specific S2 candidate; identity alignment with other Tuscany candidates is deferred to S3.", 204),
    ("cand-10172", "Archivio di Stato, Venice (repository named in p.337 note 3)", "institution",
     "Repository named in Haskell’s citation to the Inquisitori di Stato register. The archive record and repository were not independently consulted in this batch.", 205),
    ("cand-10173", "Inquisitori di Stato, register 537, folio 32v, 27 August 1764 (p.337 note 3 citation locator)", "archive",
     "Archival locator cited by Haskell for the 1764 incident. Printed folio is 32v; the canonical OCR reads p. Z2v. The archival item was not independently consulted.", 205),
    ("cand-10174", "Novelle della Repubblica delle Lettere, issue of 8 September 1736", "archive",
     "Specific issue cited in p.337 note 4. The issue was not independently consulted; the early English grammar remains unidentified.", 206),
    ("cand-10175", "Morazzoni, p.116 (p.337 note 5 citation locator)", "archive",
     "Citation locator only for the Pasquali Officium passage. The cited page was not independently consulted.", 207),
    ("cand-10176", "Delle Commedie di Carlo Goldoni avvocato veneto, vol. I (1761), L’Autore a chi legge, pp. v–vi", "archive",
     "Specific volume and author-preface pages cited in p.337 note 6 for Goldoni’s comments. The book and cited pages were not independently consulted in this batch.", 208),
]

new_candidates = []
for candidate_id, name, kind, detail, line_number in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if any(row["canonical_name"] == name for row in candidates):
        raise SystemExit(f"candidate name already exists: {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id, "canonical_name": name, "suggested_type": kind,
        "status": "open", "detail": detail, "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
    })
    new_candidates.append(row)

all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}
for candidate_id in ("cand-1411", "cand-1844", "cand-1603", "cand-2770", "cand-9953", "cand-9954", "cand-9955", "cand-9739", "cand-9988", "cand-10129", "cand-1205", "cand-1849", "cand-1851", "cand-1643"):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"required reused candidate is missing: {candidate_id}")

def segment_text(start_line, end_line):
    return "\n".join(source_lines[start_line - 1:end_line])


mention_specs = [
    (NOTES, 179, 251, 203, "[Andrea Memmo]", "cand-1643", "Bracketed author form as printed; use the index candidate and defer identity alignment."),
    (NOTES, 179, 251, 203, "[Andrea Memmo], 1786, p. 45", "cand-10166", "Citation locator only; the cited page was not independently consulted."),
    (NOTES, 179, 251, 203, "Lodoli", "cand-1411", "Named referent of the role and influence statement."),
    (NOTES, 179, 251, 203, "Conti", "cand-10164", "Surname-only cited letter author; identity remains unresolved."),
    (NOTES, 179, 251, 203, "Vico", "cand-2770", "Recipient named in the cited letter; use the existing index candidate pending S3."),
    (NOTES, 179, 251, 203, "Conti’s letter to Vico of 1728", "cand-10165", "Letter cited as evidence for Lodoli’s influence; reported through Haskell and Fisch and Bergin."),
    (NOTES, 179, 251, 203, "Fisch", "cand-9953", "Surname-only editor/author named in the publication citation."),
    (NOTES, 179, 251, 203, "Bergin", "cand-9954", "Surname-only editor/author named in the publication citation."),
    (NOTES, 179, 251, 203, "Fisch and Bergin, p. 184", "cand-9955", "Existing combined citation locator reused; p.184 was not independently consulted."),
    (NOTES, 179, 251, 203, "Pasquali", "cand-1844", "Named as the subject of Haskell’s inference."),
    (NOTES, 179, 251, 203, "his advice", "cand-1411", "Anaphoric reference to Lodoli’s advice; the note marks the conclusion as an assumption."),
    (NOTES, 179, 251, 204, "his letter", "cand-10167", "Anaphoric reference to Pasquali’s letter to Mazzoni."),
    (NOTES, 179, 251, 204, "his", "cand-1844", "Pronoun refers to Pasquali, the letter writer named in the preceding body passage."),
    (NOTES, 179, 251, 204, "Prato", "cand-10170", "City named as the bookseller’s location; no shop address is supplied."),
    (NOTES, 179, 251, 204, "Niccola Mazzoni", "cand-1603", "The note spells the first name Niccola; the index candidate spells it Nicola. Preserve the source form and defer identity alignment."),
    (NOTES, 179, 251, 204, "Nuti", "cand-10168", "Surname-only cited author; exact identity remains unresolved."),
    (NOTES, 179, 251, 204, "Nuti, 1941, p. 199", "cand-10169", "Citation locator only; the cited publication and page were not independently consulted."),
    (NOTES, 179, 251, 204, "La Toscana", "cand-10171", "Region named in Pasquali’s Italian quotation; no inference is made about the quotation’s deictic ‘qui’."),
    (NOTES, 179, 251, 205, "Archivio di Stato, Venice", "cand-10172", "Repository as named in Haskell’s archival citation; not independently consulted."),
    (NOTES, 179, 251, 205, "Inquisitori di Stato", "cand-9739", "Existing institution candidate reused as the named series/body in the locator."),
    (NOTES, 179, 251, 205, "537, p. Z2v, 27 Agosto 1764", "cand-10173", "Locator surface follows the canonical OCR; the printed folio is 32v, and the archival item was not independently consulted."),
    (NOTES, 179, 251, 206, "Novelle della Repubblica delle Lettere", "cand-9988", "Existing periodical candidate reused; this note identifies a specific issue."),
    (NOTES, 179, 251, 206, "Novelle della Repubblica delle Lettere, 8 Settembre 1736", "cand-10174", "Specific issue citation; issue content was not independently consulted."),
    (NOTES, 179, 251, 207, "Morazzoni", "cand-10129", "Surname-only author cited for the Officium discussion; exact identity remains unresolved."),
    (NOTES, 179, 251, 207, "Morazzoni, p. 116", "cand-10175", "Citation locator only; the cited page was not independently consulted."),
    (NOTES, 179, 251, 208, "Carlo Goldoni", "cand-1205", "Named author of the cited comedies; existing person candidate reused."),
    (NOTES, 179, 251, 208, "Delle Commedie di Carlo Goldoni avvocato veneto, Vol. I, 1761—L’Autore a chi legge, pp. v and vi", "cand-10176", "Specific volume and author-preface citation; the cited pages were not independently consulted."),
    (BODY, 52, 59, 53, "Prato", "cand-10170", "City named in the body as the location of the bookseller addressed in Pasquali’s reported letter; candidate added to close this S2 mention."),
]

existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []
mention_counters = {NOTES: 0, BODY: 0}
for segment_id, segment_start, segment_end, line_number, surface, candidate_id, note in mention_specs:
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"candidate FK missing for mention {surface!r}: {candidate_id}")
    line_text = source_lines[line_number - 1]
    positions = []
    cursor = 0
    while True:
        position = line_text.find(surface, cursor)
        if position < 0:
            break
        positions.append(position)
        cursor = position + 1
    if not positions:
        raise SystemExit(f"mention text is not exact at L{line_number}: {surface!r}")
    local_segment_lines = source_lines[segment_start - 1:segment_end]
    local_line = line_number - segment_start
    start = sum(len(line) + 1 for line in local_segment_lines[:local_line]) + positions[0]
    end = start + len(surface)
    segment_value = segment_text(segment_start, segment_end)
    if segment_value[start:end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    key = (segment_id, candidate_id, str(start), str(end))
    if key in existing_mention_keys:
        raise SystemExit(f"mention already exists at L{line_number}: {surface!r} -> {candidate_id}")
    mention_counters[segment_id] += 1
    prefix = "p337-notes" if segment_id == NOTES else "p337-body"
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-{prefix}-{mention_counters[segment_id]:03d}",
        "segment_id": segment_id, "candidate_id": candidate_id, "surface_form": surface,
        "start_char": start, "end_char": end, "note": note,
    })
    new_mentions.append(row)
    existing_mention_keys.add(key)

note_links = {
    1: [body_ids["pasquali_admired"]],
    2: [body_ids["pasquali_censorship"]],
    3: [body_ids["beccaria_distribution"], body_ids["client_disclosure"]],
    4: [body_ids["english_grammar"]],
    5: [body_ids["officium_commission"], body_ids["officium_plates"]],
    6: [body_ids["goldoni_commercial"], body_ids["goldoni_economy"], body_ids["goldoni_attention"], body_ids["goldoni_cost"], body_ids["goldoni_page"]],
}

ocr_203 = [{
    "source_line": 203, "ocr": "1728. published by Fisch and Bergin",
    "print": "1728 published by Fisch and Bergin",
    "basis": "CHP-13.pdf physical page 6; the print has no full stop after 1728.",
}]
ocr_205 = [{
    "source_line": 205, "ocr": "p. Z2v", "print": "p. 32v",
    "basis": "CHP-13.pdf physical page 6; visual reading of the cited folio.",
}]

statement_specs = [
    {
        "id": "st-chp13-p337-note1-memmo-1786-p45-citation", "line": 203,
        "subject": "cand-1411", "object": "cand-10166", "predicate": "cites_memmo_1786_page_45_for_lodoli_context",
        "claim": "Printed note 1 cites Andrea Memmo, 1786, page 45, in the discussion of Pasquali’s regard for Lodoli.",
        "qualification": "Citation locator as reported by Haskell; the cited page was not independently consulted in this batch.",
        "mentioned": ["cand-1643", "cand-10166", "cand-1411", "cand-1844"],
        "linked": note_links[1], "number": 1, "layer": "bibliographic citation locator",
        "quote": "[Andrea Memmo], 1786, p. 45.",
        "citations": [{"source_candidate_id": "cand-10166", "author_candidate_id": "cand-1643", "year": "1786", "page": "45"}],
    },
    {
        "id": "st-chp13-p337-note1-lodoli-influenced-publishers-booksellers", "line": 203,
        "subject": "cand-1411", "object": None, "predicate": "as_revisore_influenced_publishers_and_booksellers",
        "claim": "Haskell says Lodoli held the role Revisore della Stampa and had considerable influence on publishers and booksellers.",
        "qualification": "This is Haskell’s reported characterization. The note cites Conti’s 1728 letter to Vico as evidence; neither that letter nor its publication was independently consulted.",
        "mentioned": ["cand-1411", "cand-10164", "cand-2770", "cand-10165", "cand-9953", "cand-9954", "cand-9955"],
        "linked": note_links[1], "number": 1, "layer": "authorial statement in footnote",
        "quote": "Lodoli, who was Revisore della Stampa, had a great influence on publishers and booksellers",
        "citations": [{"source_candidate_id": "cand-10165", "author_candidate_id": "cand-10164", "recipient_candidate_id": "cand-2770", "date": "1728", "publication_candidate_id": "cand-9955", "publication_page": "184"}],
        "relation_candidate": True,
    },
    {
        "id": "st-chp13-p337-note1-conti-letter-to-vico-1728", "line": 203,
        "subject": "cand-10164", "object": "cand-2770", "predicate": "wrote_letter_to_vico_in_1728",
        "claim": "The note identifies a 1728 letter from Conti to Vico and says it was published by Fisch and Bergin, page 184.",
        "qualification": "Surname-only Conti remains ambiguous among indexed candidates. The letter and cited publication pages were not independently consulted; this is a source claim, not a verified archival fact.",
        "mentioned": ["cand-10164", "cand-2770", "cand-10165", "cand-9953", "cand-9954", "cand-9955"],
        "linked": note_links[1], "number": 1, "layer": "cited-source description",
        "quote": "Conti’s letter to Vico of 1728. published by Fisch and Bergin, p. 184",
        "citations": [{"source_candidate_id": "cand-10165", "author_candidate_id": "cand-10164", "recipient_candidate_id": "cand-2770", "date": "1728", "publication_candidate_id": "cand-9955", "publication_page": "184"}],
        "ocr_corrections": ocr_203,
        "relation_candidate": True,
    },
    {
        "id": "st-chp13-p337-note1-haskell-infers-pasquali-attended-lodoli-advice", "line": 203,
        "subject": "cand-1844", "object": "cand-1411", "predicate": "haskell_infers_attention_to_lodoli_advice",
        "claim": "Haskell says it is reasonable to assume that Pasquali paid considerable attention to Lodoli’s advice.",
        "qualification": "Explicitly an authorial inference (“reasonable to assume”), not a directly documented relationship or independently verified fact.",
        "mentioned": ["cand-1844", "cand-1411"],
        "linked": note_links[1], "number": 1, "layer": "authorial inference in footnote",
        "quote": "it is reasonable to assume that Pasquali paid a good deal of attention to his advice.",
        "relation_candidate": True,
    },
    {
        "id": "st-chp13-p337-note2-pasquali-letter-to-mazzoni", "line": 204,
        "subject": "cand-1844", "object": "cand-1603", "predicate": "wrote_to_bookseller_about_tuscan_censorship",
        "claim": "Haskell cites a letter from Pasquali to the Prato bookseller Niccola Mazzoni dated 7 January 1785/6 and quotes Pasquali’s comparison of censorship in Tuscany with “here.”",
        "qualification": "The letter is reported through Nuti, 1941, page 199; it was not independently consulted. Preserve the source spelling Niccola and do not infer the location meant by “qui”.",
        "mentioned": ["cand-1844", "cand-10167", "cand-10170", "cand-1603", "cand-10168", "cand-10169", "cand-10171"],
        "linked": note_links[2], "number": 2, "layer": "letter quotation reported in footnote",
        "quote": "See his letter of 7 January 1785/6 to the Prato bookseller Niccola Mazzoni published by Nuti, 1941, p. 199: ‘La Toscana è felice per un altro conto giacchè non si censura i libri come qui, e si puo stampare quello si vuole... . .’",
        "citations": [{"source_candidate_id": "cand-10167", "author_candidate_id": "cand-1844", "recipient_candidate_id": "cand-1603", "date": "7 January 1785/6", "publication_candidate_id": "cand-10169", "publication_author_candidate_id": "cand-10168", "publication_year": "1941", "publication_page": "199"}],
        "relation_candidate": True,
    },
    {
        "id": "st-chp13-p337-note3-inquisitori-record-locator", "line": 205,
        "subject": "cand-10173", "object": "cand-10172", "predicate": "cites_venetian_state_archive_record_for_1764_incident",
        "claim": "Haskell cites an Inquisitori di Stato record, register 537, folio 32v, dated 27 August 1764, at the Archivio di Stato in Venice.",
        "qualification": "Citation locator only; the archival item and repository were not independently consulted. The print reads 32v; the canonical OCR reads Z2v.",
        "mentioned": ["cand-10172", "cand-9739", "cand-10173", "cand-1844", "cand-9707"],
        "linked": note_links[3], "number": 3, "layer": "archival citation locator",
        "quote": "Archivio di Stato, Venice—Inquisitori di Stato, 537, p. Z2v, 27 Agosto 1764.",
        "citations": [{"source_candidate_id": "cand-10173", "repository_candidate_id": "cand-10172", "series_candidate_id": "cand-9739", "date": "1764-08-27", "register": "537", "folio_print": "32v", "folio_ocr": "Z2v"}],
        "ocr_corrections": ocr_205,
    },
    {
        "id": "st-chp13-p337-note4-novelle-1736-issue-citation", "line": 206,
        "subject": "cand-10174", "object": "cand-9988", "predicate": "cites_novelle_issue_of_1736_09_08",
        "claim": "Printed note 4 cites the 8 September 1736 issue of Novelle della Repubblica delle Lettere.",
        "qualification": "The issue is cited as a locator for the statement about an early English grammar; neither the issue nor the unidentified grammar was independently consulted.",
        "mentioned": ["cand-9988", "cand-10174", "cand-10010", "cand-1844"],
        "linked": note_links[4], "number": 4, "layer": "periodical issue citation locator",
        "quote": "Novelle della Repubblica delle Lettere, 8 Settembre 1736.",
        "citations": [{"source_candidate_id": "cand-10174", "container_candidate_id": "cand-9988", "date": "1736-09-08"}],
    },
    {
        "id": "st-chp13-p337-note5-morazzoni-p116-citation", "line": 207,
        "subject": "cand-10175", "object": "cand-10129", "predicate": "cites_morazzoni_page_116_for_officium",
        "claim": "Printed note 5 cites Morazzoni, page 116, for the Officium discussion.",
        "qualification": "The author is identified only by surname and the cited page was not independently consulted.",
        "mentioned": ["cand-10129", "cand-10175", "cand-1849", "cand-1901"],
        "linked": note_links[5], "number": 5, "layer": "bibliographic citation locator",
        "quote": "Morazzoni, p. 116.",
        "citations": [{"source_candidate_id": "cand-10175", "author_candidate_id": "cand-10129", "page": "116", "related_work_candidate_id": "cand-1849"}],
    },
    {
        "id": "st-chp13-p337-note6-goldoni-author-preface-citation", "line": 208,
        "subject": "cand-10176", "object": "cand-1851", "predicate": "cites_goldoni_volume_one_author_preface",
        "claim": "Printed note 6 cites volume I of Delle Commedie di Carlo Goldoni avvocato veneto (1761), “L’Autore a chi legge,” pages v and vi, for Goldoni’s comments quoted on p.337.",
        "qualification": "The title and page locator are transcribed from Haskell’s note; the volume and cited pages were not independently consulted.",
        "mentioned": ["cand-10176", "cand-1205", "cand-1851"],
        "linked": note_links[6], "number": 6, "layer": "bibliographic citation locator",
        "quote": "Delle Commedie di Carlo Goldoni avvocato veneto, Vol. I, 1761—L’Autore a chi legge, pp. v and vi.",
        "citations": [{"source_candidate_id": "cand-10176", "author_candidate_id": "cand-1205", "related_work_candidate_id": "cand-1851", "year": "1761", "volume": "I", "section": "L’Autore a chi legge", "pages": "v–vi"}],
    },
]

new_statements = []
for spec in statement_specs:
    if spec["id"] in statement_by_id:
        raise SystemExit(f"statement ID already exists: {spec['id']}")
    missing = [candidate_id for candidate_id in spec["mentioned"] if candidate_id not in all_candidate_ids]
    if missing:
        raise SystemExit(f"statement {spec['id']} has missing candidate references: {missing}")
    qualifiers = {
        "source_line_start": spec["line"], "source_line_end": spec["line"],
        "printed_page": 337, "pdf_physical_page": 6, "claim": spec["claim"],
        "speaker": spec.get("speaker", "Haskell, printed footnote"),
        "text_layer": spec["layer"], "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"], "footnote_number": spec["number"],
        "linked_body_statement_ids": spec["linked"],
    }
    for optional in ("citations", "ocr_corrections", "cross_reference_segments"):
        if optional in spec:
            qualifiers[optional] = spec[optional]
    if spec.get("relation_candidate"):
        qualifiers["relation_candidate"] = True
    if spec.get("quote_mode"):
        qualifiers["quote_mode"] = spec["quote_mode"]
    row = {
        "statement_id": spec["id"], "segment_id": NOTES,
        "subject_candidate_id": spec["subject"], "object_candidate_id": spec["object"],
        "predicate": spec["predicate"], "qualifiers": qualifiers,
        "original_quote": spec["quote"], "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    }
    new_statements.append(row)

for marker, linked_ids in note_links.items():
    for linked_id in linked_ids:
        if linked_id not in statement_by_id:
            raise SystemExit(f"footnote target statement missing: {linked_id}")
    if not any(spec["number"] == marker for spec in statement_specs):
        raise SystemExit(f"no note statements for p.337 marker {marker}")

# Attach notes 1–6 only to the printed marker targets. The PDF shows note 4 after
# the English-grammar claim; the same OCR line's Smith clause carries no marker.
for marker, linked_ids in note_links.items():
    note_ids = [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_number"] == marker]
    note_lines_for_marker = [row["qualifiers"]["source_line_start"] for row in new_statements if row["qualifiers"]["footnote_number"] == marker]
    ref = {
        "footnote_marker": str(marker), "footnote_printed_page": 337,
        "footnote_text_pending": False, "footnote_segment": NOTES,
        "footnote_line_range": f"L{min(note_lines_for_marker)}-L{max(note_lines_for_marker)}",
        "footnote_body_link_status": "linked", "footnote_note_statement_ids": note_ids,
    }
    for linked_id in linked_ids:
        qualifiers = statement_by_id[linked_id].setdefault("qualifiers", {})
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers["footnote_note_statement_ids"] = sorted(set(qualifiers.get("footnote_note_statement_ids", [])) | set(note_ids))
        refs = qualifiers.setdefault("footnote_refs", [])
        if not any(item.get("footnote_marker") == str(marker) and item.get("footnote_printed_page") == 337 for item in refs):
            refs.append(ref)

false_marker_statement = statement_by_id[body_ids["false_same_line"]]
false_qualifiers = false_marker_statement.setdefault("qualifiers", {})
for key in (
    "footnote_marker", "footnote_printed_page", "footnote_text_pending", "footnote_segment",
    "footnote_body_link_status", "cross_reference_segments", "footnote_note_statement_ids", "footnote_refs",
):
    false_qualifiers.pop(key, None)
false_qualifiers["footnote_scope_exclusion"] = (
    "Printed p.337 footnote 4 follows the English-grammar statement earlier on this OCR line; "
    "it does not annotate Joseph Smith’s controlling interest. Confirmed against CHP-13.pdf physical page 6."
)

coverage[NOTES]["source_line_ranges"] = "L180-208"
coverage[NOTES]["note"] = (
    "Notes L180-191 (pp.332-334), L192-202 (pp.335-336), and L203-208 (p.337) are migrated. "
    "L209-246 and mirrored caption lines L247-248 remain to process or map; the composite segment remains partial."
)
coverage[BODY]["migration_status"] = "complete"
coverage[BODY]["source_line_ranges"] = "L52-59"
coverage[BODY]["note"] = (
    "Printed p.337 body and visible notes reviewed against CHP-13.pdf physical page 6. "
    "Footnotes 1-6 now link to consolidated notes L203-208; printed note 4 is linked only to the English-grammar claim, "
    "not the same-line Smith statement. The p.337 Goldoni quotation closes on this page; p.338 continues Haskell’s discussion."
)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = statements + new_statements
coverage_out = coverage_rows

print(f"candidate rows: {len(candidates)} -> {len(candidate_out)} (+{len(new_candidates)})")
print(f"mention rows: {len(mentions)} -> {len(mention_out)} (+{len(new_mentions)})")
print(f"statement rows: {len(statements)} -> {len(statement_out)} (+{len(new_statements)})")
print("coverage changes: p.337 body partial -> complete; consolidated notes L180-208, still partial")
print("footnote targets:")
for marker, linked_ids in note_links.items():
    print(f"  {marker}: {', '.join(linked_ids)}")
print(f"false same-line marker removed: {body_ids['false_same_line']}")

if not args.apply:
    print("dry-run only; pass --apply to write after reviewing this plan")
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup}")
    shutil.copy2(path, backup)

write_csv(candidate_path, candidate_fields, candidate_out)
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statement_out)
write_csv(coverage_path, coverage_fields, coverage_out)
print(f"applied; backups use suffix {BACKUP_SUFFIX}")
