"""Controlled S2 migration for p.332-334 footnotes in the composite note segment."""
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
SEGMENT = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
SEGMENT_SHA = "f592d5913122cf2c4c2e7db9a39b8016c82dbc232a869018793ef11096faacb9"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-notes-p332-334-20261003"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the reviewed notes migration")
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
    raise SystemExit("source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[178:251])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("composite note source segment changed")
for token in (
    "1 For a general survey of the whole field",
    "2 Quoted by M. Berengo, 1957, p. 1322.",
    "3 See, for instance, the comments of J. G. Goethe, I, p. 38.",
    "Marin, Vin, p. 234, challenges the optimistic view",
    "1 Roberti, 1900, pp. 3 26-3 5.",
    "1 Bettinelli: Lettere inglesi—letters seconds.",
    "6 The Novelle della Repubblica delle Lettere was published as from 1729.",
):
    if token not in segment_text:
        raise SystemExit(f"required OCR source text missing: {token}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
state = (len(candidates), len(mentions), len(statements), len(coverage))
if state != (10113, 21872, 9778, 830):
    raise SystemExit(f"unexpected pre-state {state}")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
required_existing = {
    "cand-0369", "cand-08291", "cand-08514", "cand-09919", "cand-09987", "cand-09988"
}
# Candidate IDs are written without zero padding after cand-9999; normalize the required IDs below.
required_existing = {"cand-0369", "cand-8291", "cand-8514", "cand-9919", "cand-9987", "cand-9988"}
if not required_existing.issubset(candidate_by_id):
    raise SystemExit(f"required existing candidates missing: {sorted(required_existing - candidate_by_id.keys())}")

coverage_by_id = {row["segment_id"]: row for row in coverage}
if (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("composite note segment is not queued")
BODY_PAGES = {
    332: "chp-13:13_CHP-13_intro:l3-12",
    333: "chp-13:13_CHP-13_intro:l14-19",
    334: "chp-13:13_CHP-13_intro:l21-30",
}
for page, segment_id in BODY_PAGES.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"]) != ("reviewed", "partial"):
        raise SystemExit(f"unexpected p.{page} body coverage: {row}")

segment_row = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row["segment_id"] == SEGMENT), None)
if not segment_row or segment_row["sha256"] != SEGMENT_SHA or segment_row["asset_sha256"] != SOURCE_SHA:
    raise SystemExit("S0 composite segment metadata/hash changed")
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidates)
if current_max != 10126:
    raise SystemExit(f"candidate sequence changed: expected 10126, found {current_max}")

candidate_specs = [
    ("Horatio Brown", "person", "Author named in p.332 note 1. The note supplies no given bibliographic title and this identity has not been externally aligned.", 180),
    ("J. G. Goethe", "person", "Author form as printed in p.332 note 3. Do not expand the initials before S3 identity alignment.", 182),
    ("Morazzoni (author surname in p.332-334 notes)", "person", "Surname-only author named in p.332 and p.334 notes; exact identity remains unresolved.", 183),
    ("Marin (author surname in p.332 note 4)", "person", "Surname-only author cited as Marin, VIII; full name and identity remain unresolved.", 183),
    ("Roberti (author surname in p.333 note 1)", "person", "Surname-only author in a 1900 citation; identity remains unresolved pending bibliography review.", 185),
    ("Battagia (author surname in p.334 note 4)", "person", "Surname-only author cited at page 76; identity remains unresolved.", 189),
    ("Horatio Brown general survey (p.332 note 1; title not supplied)", "archive", "The note calls this a general survey of the field reproducing important documents, but gives no title, edition, or page locator.", 180),
    ("M. Berengo, 1957, p.1322 (p.332 note 2 citation locator)", "archive", "Exact short citation as printed. The cited work title and edition are not given; its text has not been independently consulted.", 181),
    ("J. G. Goethe, volume I, p.38 (p.332 note 3 citation locator)", "archive", "Short volume/page citation only; work title, edition, and cited passage are not identified here.", 182),
    ("Berengo, 1957 (p.332 note 4 citation locator)", "archive", "Short author/year citation without title or page; kept separate from the p.332 note 2 locator pending bibliography review.", 183),
    ("Morazzoni (p.332 note 4 citation locator; title and page not supplied)", "archive", "Abbreviated citation only; relation to the separately paginated Morazzoni references remains unaligned.", 183),
    ("Gallo, 1948, pp.153-214 (p.332 note 4 citation locator)", "archive", "Short citation with year and pages; title and edition are not supplied.", 183),
    ("Marin, VIII, p.234 (p.332 note 4 citation locator)", "archive", "The print reads Marin, VIII, p.234; source OCR has 'Vin'. The title represented by VIII, author identity, and edition remain unresolved.", 183),
    ("Morazzoni, p.70 (p.332 note 5 citation locator)", "archive", "Short citation with page only; title and relation to other Morazzoni citations remain unresolved.", 184),
    ("Roberti, 1900, pp.326-35 (p.333 note 1 citation locator)", "archive", "Print-verified short citation. The cited work title and author identity are not supplied; cited pages were not independently consulted.", 185),
    ("Saverio Bettinelli, Lettere inglesi, lettera seconda (p.334 note 1)", "archive", "Print-verified title of the cited letter. The note supplies no edition or publication year, and the text has not been independently consulted.", 186),
    ("Morazzoni, p.131 (p.334 note 2 citation locator)", "archive", "Short citation with page only; title and relation to other Morazzoni citations remain unresolved.", 187),
    ("Battagia, p.76 (p.334 note 4 citation locator)", "archive", "Short surname/page citation only; title and edition are not supplied.", 189),
    ("Hazard, 1946, volume I, pp.105-107 and note (p.334 note 6)", "archive", "Short author/year/volume/page citation. The title and identity of Hazard remain unresolved; cited pages were not independently consulted.", 191),
]
new_candidates = []
candidate_key = {}
for i, (name, kind, detail, line) in enumerate(candidate_specs, 10127):
    candidate_id = f"cand-{i}"
    if candidate_id in candidate_by_id or any(row["canonical_name"] == name for row in candidates):
        raise SystemExit(f"candidate ID or natural-name collision: {candidate_id} / {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line}",
    })
    new_candidates.append(row)
    candidate_key[name] = candidate_id

CID = {
    "brown": "cand-10127", "goethe": "cand-10128", "morazzoni_person": "cand-10129",
    "marin_person": "cand-10130", "roberti": "cand-10131", "battagia": "cand-10132",
    "brown_work": "cand-10133", "berengo_1957_n2": "cand-10134", "goethe_work": "cand-10135",
    "berengo_1957_n4": "cand-10136", "morazzoni_n4": "cand-10137", "gallo_1948": "cand-10138",
    "marin_viii": "cand-10139", "morazzoni_p70": "cand-10140", "roberti_1900": "cand-10141",
    "bettinelli_letter": "cand-10142", "morazzoni_p131": "cand-10143", "battagia_p76": "cand-10144",
    "hazard_1946": "cand-10145", "berengo_person": "cand-8291", "gallo_person": "cand-8514",
    "bettinelli_person": "cand-0369", "hazard_person": "cand-9919", "bossuet_edition": "cand-9987",
    "novelle": "cand-9988", "battagia_person": "cand-10132",
}

mention_specs = [
    (CID["brown"], "Horatio Brown", "Named author; no full work title is supplied."),
    (CID["brown_work"], "general survey of the whole field", "Descriptive reference to an untitled survey; title is not inferred."),
    (CID["berengo_person"], "M. Berengo", "Author form as printed; same-person alignment to the existing Marino Berengo candidate remains for S3."),
    (CID["berengo_1957_n2"], "M. Berengo, 1957, p. 1322", "Citation locator only; title and edition are not supplied."),
    (CID["goethe"], "J. G. Goethe", "Author initials retained as printed; no identity expansion."),
    (CID["goethe_work"], "J. G. Goethe, I, p. 38", "Short volume/page citation; cited title remains unknown."),
    (CID["berengo_person"], "Berengo", "Surname occurrence in the p.332 note 4 citation; identity remains pending."),
    (CID["berengo_1957_n4"], "Berengo, 1957, and", "Separate citation occurrence from p.332 note 2; not merged before bibliography review."),
    (CID["morazzoni_person"], "Morazzoni", "Surname-only author reference."),
    (CID["morazzoni_n4"], "Morazzoni.", "Abbreviated publication citation; title/page not supplied. Terminal punctuation is part of the citation span; the nested author mention is separately anchored."),
    (CID["gallo_person"], "Gallo", "Surname-only author candidate reused pending S3."),
    (CID["gallo_1948"], "Gallo, 1948, pp. 153-214", "Citation locator only; title and edition are not supplied."),
    (CID["marin_person"], "Marin", "Surname-only cited author; identity unresolved."),
    (CID["marin_viii"], "Marin, Vin, p. 234", "OCR form is anchored; print reads 'Marin, VIII, p. 234'."),
    (CID["morazzoni_person"], "Morazzoni", "Surname-only author reference in p.332 note 5."),
    (CID["morazzoni_p70"], "Morazzoni, p. 70", "Citation locator only; not merged with the p.332 note 4 citation."),
    (CID["roberti"], "Roberti", "Surname-only cited author; identity unresolved."),
    (CID["roberti_1900"], "Roberti, 1900, pp. 3 26-3 5", "OCR form is anchored; print reads pages 326-35."),
    (CID["bettinelli_person"], "Bettinelli", "Reuses the main index candidate for Saverio Bettinelli; the letter attribution is recorded by the note."),
    (CID["bettinelli_letter"], "Lettere inglesi—letters seconds", "OCR form is anchored; print reads 'Lettere inglesi—lettera seconda'."),
    (CID["morazzoni_person"], "Morazzoni", "Surname-only author reference in p.334 note 2."),
    (CID["morazzoni_p131"], "Morazzoni, p. 131", "Citation locator only; not merged with other abbreviated references."),
    (CID["bossuet_edition"], "the Bossuet", "The note refers to the already-recorded French edition; no new edition candidate is created."),
    (CID["battagia_person"], "Battagia", "Surname-only cited author; identity unresolved."),
    (CID["battagia_p76"], "Battagia, p. 76", "Citation locator only; title and edition are not supplied."),
    (CID["novelle"], "The Novelle della Repubblica delle Lettere", "The footnote supplies a publication-start statement for this already-recorded bulletin."),
    (CID["hazard_person"], "Hazard", "Reuses unresolved author candidate from a separate book note; identity alignment remains pending."),
    (CID["hazard_1946"], "Hazard, 1946,1, pp. 105-7 and note", "OCR form is anchored; print reads volume I, pages 105-7 and note."),
]
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
seen_occurrences = {}
for i, (candidate_id, surface, note) in enumerate(mention_specs, 1):
    mention_id = f"m-s2-ch13-notes-p332-334-{i:03d}"
    if mention_id in mention_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    occurrence_key = (candidate_id, surface)
    occurrence = seen_occurrences.get(occurrence_key, 0)
    seen_occurrences[occurrence_key] = occurrence + 1
    start = -1
    pos = 0
    for _ in range(occurrence + 1):
        start = segment_text.find(surface, pos)
        if start < 0:
            raise SystemExit(f"mention surface not found: {surface!r}, occurrence {occurrence}")
        pos = start + 1
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })

source_quote = lambda line: source_lines[line - 1]
ocr_corrections = {
    183: [{"source_file": "02-sources/02-Markdown/13_CHP-13_intro.md", "source_line": 183, "ocr": "Marin, Vin, p. 234", "print": "Marin, VIII, p. 234", "basis": "CHP-13.pdf physical page 1."}],
    185: [{"source_file": "02-sources/02-Markdown/13_CHP-13_intro.md", "source_line": 185, "ocr": "pp. 3 26-3 5", "print": "pp. 326-35", "basis": "CHP-13.pdf physical page 2."}],
    186: [{"source_file": "02-sources/02-Markdown/13_CHP-13_intro.md", "source_line": 186, "ocr": "Lettere inglesi—letters seconds", "print": "Lettere inglesi—lettera seconda", "basis": "CHP-13.pdf physical page 3."}],
    190: [{"source_file": "02-sources/02-Markdown/13_CHP-13_intro.md", "source_line": 190, "ocr": "6 The Novelle della Repubblica delle Lettere", "print": "5 The Novelle della Repubblica delle Lettere", "basis": "CHP-13.pdf physical page 3; the body marker and printed footnote number are 5."}],
}

note_specs = [
    ("st-chp13-p332-n1-brown-survey-citation", 180, 332, 1, None, CID["brown_work"], "footnote_citation", "The note directs readers to an untitled general survey by Horatio Brown and describes it as reproducing many important documents.", "Citation pointer only; the title, edition, and cited pages are not supplied or independently consulted.", [CID["brown"], CID["brown_work"]], ["st-chp13-p332-publishing-role-in-venetian-economy", "st-chp13-p332-republic-efforts-to-maintain-publishing-supremacy"], [{"source_candidate_id": CID["brown_work"], "author_candidate_id": CID["brown"], "reference_text": "Horatio Brown; general survey, title not supplied"}], None),
    ("st-chp13-p332-n2-berengo-citation", 181, 332, 2, None, CID["berengo_1957_n2"], "footnote_citation", "The note cites M. Berengo, 1957, page 1322, for the preceding report attributed to Grosley.", "Citation locator only; the source passage was not independently read and the initials remain unresolved.", [CID["berengo_person"], CID["berengo_1957_n2"]], ["st-chp13-p332-grosley-venice-paris-publication-permission-report"], [{"source_candidate_id": CID["berengo_1957_n2"], "author_candidate_id": CID["berengo_person"], "year": "1957", "page": "1322"}], None),
    ("st-chp13-p332-n3-goethe-citation", 182, 332, 3, None, CID["goethe_work"], "footnote_citation", "The note points to J. G. Goethe, volume I, page 38, as an example of travellers' comments on Venetian bookshops.", "Citation locator only; the work title and edition are not supplied and the cited passage was not independently read.", [CID["goethe"], CID["goethe_work"]], ["st-chp13-p332-bookshops-cultural-contact"], [{"source_candidate_id": CID["goethe_work"], "author_candidate_id": CID["goethe"], "volume": "I", "page": "38"}], None),
    ("st-chp13-p332-n4-berengo-citation", 183, 332, 4, None, CID["berengo_1957_n4"], "footnote_citation", "The note also cites a 1957 Berengo reference for the preceding discussion of Venetian publishing and engraving.", "A separate citation candidate is retained because the abbreviated note gives no page and has not yet been resolved against the bibliography.", [CID["berengo_person"], CID["berengo_1957_n4"]], ["st-chp13-p332-government-copyright-encouragement"], [{"source_candidate_id": CID["berengo_1957_n4"], "author_candidate_id": CID["berengo_person"], "year": "1957"}], ocr_corrections[183]),
    ("st-chp13-p332-n4-morazzoni-citation", 183, 332, 4, None, CID["morazzoni_n4"], "footnote_citation", "The note cites Morazzoni for the preceding discussion of Venetian publishing and engraving.", "Citation only; no title or locator is given, so it remains distinct from other Morazzoni references.", [CID["morazzoni_person"], CID["morazzoni_n4"]], ["st-chp13-p332-government-copyright-encouragement"], [{"source_candidate_id": CID["morazzoni_n4"], "author_candidate_id": CID["morazzoni_person"]}], ocr_corrections[183]),
    ("st-chp13-p332-n4-gallo-citation", 183, 332, 4, None, CID["gallo_1948"], "footnote_citation", "The note additionally cites Gallo, 1948, pages 153-214.", "Citation locator only; title and edition are not supplied and the cited pages were not independently read.", [CID["gallo_person"], CID["gallo_1948"]], ["st-chp13-p332-government-copyright-encouragement"], [{"source_candidate_id": CID["gallo_1948"], "author_candidate_id": CID["gallo_person"], "year": "1948", "pages": "153-214"}], ocr_corrections[183]),
    ("st-chp13-p332-n4-marin-counterview", 183, 332, 4, None, CID["marin_viii"], "reported_counterview", "The note reports that Marin, cited as volume VIII page 234, challenges the optimistic view generally given of eighteenth-century engraving in Venice.", "This is Haskell's report of Marin's argument, not a direct reading of Marin. The print reads VIII; the OCR has Vin.", [CID["marin_person"], CID["marin_viii"]], ["st-chp13-p332-government-copyright-encouragement"], [{"source_candidate_id": CID["marin_viii"], "author_candidate_id": CID["marin_person"], "volume": "VIII", "page": "234"}], ocr_corrections[183]),
    ("st-chp13-p332-n5-morazzoni-citation", 184, 332, 5, None, CID["morazzoni_p70"], "footnote_citation", "The note cites Morazzoni, page 70.", "Citation locator only; the title is not supplied, and this reference is not merged with other abbreviated Morazzoni citations.", [CID["morazzoni_person"], CID["morazzoni_p70"]], ["st-chp13-p332-marieschi-views-appealed-to-fragonard"], [{"source_candidate_id": CID["morazzoni_p70"], "author_candidate_id": CID["morazzoni_person"], "page": "70"}], None),
    ("st-chp13-p333-n1-roberti-citation", 185, 333, 1, None, CID["roberti_1900"], "footnote_citation", "The note cites Roberti, 1900, pages 326-35, for the preceding 1765 instructions attributed to Caterina Barbarigo.", "Print-verified citation locator; the title and full author identity are not supplied and the cited pages were not independently read. OCR spacing in the page range is corrected only in S2.", [CID["roberti"], CID["roberti_1900"]], ["st-chp13-p333-barbarigo-1765-pamphlet-instructions-through-gozzi"], [{"source_candidate_id": CID["roberti_1900"], "author_candidate_id": CID["roberti"], "year": "1900", "pages": "326-35"}], ocr_corrections[185]),
    ("st-chp13-p334-n1-bettinelli-letter-citation", 186, 334, 1, None, CID["bettinelli_letter"], "footnote_citation", "The note identifies the preceding quotation as from Saverio Bettinelli's Lettere inglesi, lettera seconda.", "The title is verified from the printed page. The edition/year and cited text have not been independently checked; the S0 OCR phrase 'letters seconds' is not treated as the printed title.", [CID["bettinelli_person"], CID["bettinelli_letter"]], ["st-chp13-p333-anonymous-quotation-on-poem-collections", "st-chp13-p334-bettinelli-criticized-opulent-poem-collection"], [{"source_candidate_id": CID["bettinelli_letter"], "author_candidate_id": CID["bettinelli_person"], "reference_text": "Lettere inglesi, lettera seconda"}], ocr_corrections[186]),
    ("st-chp13-p334-n2-morazzoni-citation", 187, 334, 2, None, CID["morazzoni_p131"], "footnote_citation", "The note cites Morazzoni, page 131, for Albrizzi's inherited business.", "Citation locator only; do not merge with the separately cited pages 70 or the uncited Morazzoni reference on p.332.", [CID["morazzoni_person"], CID["morazzoni_p131"]], ["st-chp13-p334-albrizzi-birth-and-inherited-business"], [{"source_candidate_id": CID["morazzoni_p131"], "author_candidate_id": CID["morazzoni_person"], "page": "131"}], None),
    ("st-chp13-p334-n3-bossuet-eighth-volume-1755", 188, 334, 3, CID["bossuet_edition"], None, "note_reports_dedication", "The note says the preceding point seems clear from the dedication of the eighth Bossuet volume in 1755.", "The antecedent of 'This' is not fully explicit; preserve the note's inferential wording and do not convert it into a separate claim about the son's schooling.", [CID["bossuet_edition"]], ["st-chp13-p334-albrizzi-travel-and-vienna-education"], [{"source_candidate_id": CID["bossuet_edition"], "volume": "VIII", "dedication_year": "1755"}], None),
    ("st-chp13-p334-n4-battagia-citation", 189, 334, 4, None, CID["battagia_p76"], "footnote_citation", "The note cites Battagia, page 76, for the Accademia Albrizziana.", "Citation locator only; the publication title, edition, and author's full identity are unresolved.", [CID["battagia_person"], CID["battagia_p76"]], ["st-chp13-p334-almoro-organized-academy"], [{"source_candidate_id": CID["battagia_p76"], "author_candidate_id": CID["battagia_person"], "page": "76"}], None),
    ("st-chp13-p334-n5-novelle-publication-from-1729", 190, 334, 5, CID["novelle"], None, "published_as_from_year", "The note says the Novelle della Repubblica delle Lettere was published as from 1729.", "Retain the source's 'as from' wording; this does not establish an exact first issue date. The OCR footnote label 6 is corrected to printed note 5 in S2 only.", [CID["novelle"]], ["st-chp13-p334-albrizzi-edited-weekly-bulletin"], [], ocr_corrections[190]),
    ("st-chp13-p334-n6-hazard-citation", 191, 334, 6, None, CID["hazard_1946"], "footnote_citation", "The note cites Hazard, 1946, volume I, pages 105-7 and note, for the preceding Bossuet context.", "Citation locator only; title and author identity are unresolved and the cited pages were not independently consulted.", [CID["hazard_person"], CID["hazard_1946"]], ["st-chp13-p334-bossuet-interest-and-heresy-context"], [{"source_candidate_id": CID["hazard_1946"], "author_candidate_id": CID["hazard_person"], "year": "1946", "volume": "I", "pages": "105-107 and note"}], None),
]

statement_by_id = {row["statement_id"]: row for row in statements}
new_statements = []
links_by_body = {}
for sid, line, page, note_number, subject, obj, predicate, claim, qualification, mentioned, linked, citations, corrections in note_specs:
    if sid in statement_by_id:
        raise SystemExit(f"statement ID already exists: {sid}")
    for body_id in linked:
        if body_id not in statement_by_id:
            raise SystemExit(f"linked body statement missing: {body_id}")
        links_by_body.setdefault(body_id, []).append({"note": note_number, "line": line, "statement_id": sid})
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": page,
        "pdf_physical_page": page - 331,
        "claim": claim,
        "speaker": "Haskell, printed footnote",
        "text_layer": "bibliographic citation locator" if predicate == "footnote_citation" else "footnote",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "footnote_number": note_number,
        "linked_body_statement_ids": linked,
    }
    if citations:
        qualifiers["citations"] = citations
    if corrections:
        qualifiers["ocr_corrections"] = corrections
    new_statements.append({
        "statement_id": sid,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": source_quote(line),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })

candidate_new = candidates + new_candidates
mention_new = mentions + new_mentions
statement_new = statements + new_statements
candidate_ids = {row["candidate_id"] for row in candidate_new}
if len({row["mention_id"] for row in new_mentions}) != len(new_mentions):
    raise SystemExit("duplicate planned mention IDs")
for row in new_mentions:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"mention candidate missing: {row['mention_id']}")
for row in new_statements:
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {candidate_id}")

for body_id, note_links in links_by_body.items():
    body = statement_by_id[body_id]
    refs = body["qualifiers"].setdefault("footnote_refs", [])
    for note in note_links:
        entry = {
            "footnote_marker": str(note["note"]),
            "footnote_printed_page": body["qualifiers"].get("printed_page"),
            "footnote_text_pending": False,
            "footnote_segment": SEGMENT,
            "footnote_line_range": f"L{note['line']}",
            "footnote_body_link_status": "linked",
            "footnote_note_statement_ids": [note["statement_id"]],
        }
        if not any(x.get("footnote_marker") == entry["footnote_marker"] and x.get("footnote_segment") == SEGMENT for x in refs):
            refs.append(entry)

for row in candidate_new:
    if row["candidate_id"] == CID["novelle"]:
        row["detail"] = "A weekly bulletin edited by Giambattista Albrizzi and described as commenting on and reviewing recent books from across Europe. P.334 note 5 says it was published as from 1729; this is not an exact first-issue date."

coverage_new = []
for row in coverage:
    updated = dict(row)
    if updated["segment_id"] == SEGMENT:
        updated.update({
            "disposition": "reviewed",
            "migration_status": "partial",
            "source_line_ranges": "L180-191",
            "note": "P.332 notes 1-5 (L180-184), p.333 note 1 (L185), and p.334 notes 1-6 (L186-191) were checked against CHP-13.pdf physical pages 1-3 and migrated with citation candidates and body-statement links. L192-238 and L239-246 remain; L247-248 are mirrored OCR of already transcribed Plate 57-58 material and still need explicit coverage disposition; L249-251 (p.345 notes) remain pending. S0 OCR remains unchanged. Print checks recorded in statement qualifiers: L183 Vin→VIII; L185 pp. 3 26-3 5→326-35; L186 letters seconds→lettera seconda; L190 footnote label 6→printed 5.",
        })
    if updated["segment_id"] in BODY_PAGES.values():
        page = next(page for page, body_segment in BODY_PAGES.items() if body_segment == updated["segment_id"])
        updated["migration_status"] = "complete"
        updated["note"] = f"Printed p.{page} body and its printed footnotes were checked against CHP-13.pdf and migrated. Footnote citation statements are linked by statement IDs; note references are locators, not independent verification. S0 OCR remains unchanged."
    coverage_new.append(updated)

print(f"candidates +{len(new_candidates)}; mentions +{len(new_mentions)}; note statements +{len(new_statements)}")
print("p.332-p.334 body coverage -> complete; composite note segment -> reviewed/partial L180-191")
print("print-verified S2 corrections: p.332 n.4 VIII; p.333 n.1 pages 326-35; p.334 n.1 lettera seconda; p.334 n.5 marker 5")
if not args.apply:
    print("dry-run only; pass --apply to write")
    raise SystemExit(0)

paths = (candidate_path, mention_path, statement_path, coverage_path)
backups = [Path(str(path) + BACKUP_SUFFIX) for path in paths]
if any(path.exists() for path in backups):
    raise SystemExit("a recovery backup already exists; inspect it before retrying")
for path, backup in zip(paths, backups):
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_new)
write_csv(mention_path, mention_fields, mention_new)
write_jsonl(statement_path, statement_new)
write_csv(coverage_path, coverage_fields, coverage_new)
print("applied; recovery backups saved for candidate, mention, statement, and coverage tables")
