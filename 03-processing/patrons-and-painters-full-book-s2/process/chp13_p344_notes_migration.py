"""Controlled S2 migration for printed p.344 notes 1-8; dry-run by default."""
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
BODY = "chp-13:13_CHP-13_intro:l116-122"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p344-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.344 footnote migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in {
    239: "1 Borroni, p. 28.",
    240: "2 P. Clement, p. 124. In 1767 John Northall wrote (p. 43 8):",
    241: "3 Bottari, II, pp. 129-30.",
    242: "4 Blunt and Croft-Murray, p. 146.",
    243: "5 This was the opinion of the first editor of Rosalba’s diary",
    244: "6 G. A. Moschini, 1806, III, p. 92.",
    245: "7 Battistella, 1930, pp. 60 ff.",
    246: "8 Biblioteca Marucelliana, Florence",
    122: "Zanetti also employed Rosalba’s pupil Félicita Sartori",
}.items():
    if required not in source_lines[line_number - 1]:
        raise SystemExit(f"required source text changed at L{line_number}")

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
table_state = (len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates), len(mentions), len(statements))
if table_state != (10201, 10214, 22125, 9865):
    raise SystemExit(f"unexpected table pre-state: {table_state}")
if BODY not in coverage or NOTES not in coverage:
    raise SystemExit("p.344 body or consolidated-notes coverage row missing")
if coverage[NOTES]["source_line_ranges"] != "L180-238":
    raise SystemExit("consolidated-notes cursor changed")
if coverage[BODY]["migration_status"] != "partial":
    raise SystemExit("p.344 body coverage state changed")
if any(row["segment_id"] == NOTES and row["mention_id"].startswith("m-s2-ch13-p344-notes-") for row in mentions):
    raise SystemExit("p.344 note mentions already exist")

expected_names = {
    "cand-0417": "Bottari, Giovanni",
    "cand-0379": "Blunt, Sir Anthony",
    "cand-0789": "Clement, Abbé",
    "cand-02363": "Sartori, Felicita",
}
# Candidate IDs are not zero-padded in this table.
expected_names.pop("cand-02363")
expected_names["cand-2363"] = "Sartori, Felicita"
for candidate_id, expected_name in expected_names.items():
    if candidate_id not in candidate_by_id or candidate_by_id[candidate_id]["canonical_name"] != expected_name:
        raise SystemExit(f"expected reusable candidate changed: {candidate_id}")
for candidate_id in ("cand-10193", "cand-6200", "cand-8511", "cand-8815", "cand-9279", "cand-9339", "cand-9340", "cand-9493", "cand-9947", "cand-10192", "cand-10112", "cand-1709", "cand-2764", "cand-2838", "cand-3397", "cand-0581", "cand-1214"):
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"required reusable candidate missing: {candidate_id}")

new_candidate_ids = {f"cand-{number}" for number in range(10215, 10219)}
if new_candidate_ids & set(candidate_by_id):
    raise SystemExit(f"candidate IDs already exist: {sorted(new_candidate_ids & set(candidate_by_id))}")
new_candidates = []


def add_candidate(candidate_id, name, kind, detail, line_number):
    if any(row["canonical_name"].casefold() == name.casefold() for row in candidates):
        raise SystemExit(f"candidate name already exists: {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
        "detail": detail,
    })
    new_candidates.append(row)


add_candidate("cand-10215", "John Northall (author cited in p.344 note 2)", "person", "Named as the writer of a 1767 passage quoted by Haskell; identity not externally aligned.", 240)
add_candidate("cand-10216", "John Northall, 1767, p.438 (short-form cited source; title unresolved)", "archive", "P.344 note 2 cites Northall at page 438; title, edition, and publication details are not supplied here and the cited page was not consulted.", 240)
add_candidate("cand-10217", "P. Clement, p.124 (short-form cited source; title unresolved)", "archive", "Short citation in p.344 note 2 for the preceding Abbé Clement description; title, edition, and author identity are not inferred, and the page was not consulted.", 240)
add_candidate("cand-10218", "A. M. Zanetti letter to A. F. Gori, 26 August 1752 (Biblioteca Marucelliana, MSS. B. VIII, 13)", "archive", "P.344 note 8 gives the date, recipient, repository, and shelfmark. The adjacent quotation attributes the letter to Zanetti; the manuscript was not consulted. Keep distinct from the 22 December 1752 letter, cand-10210.", 246)

# Reuse bibliographic candidates already identified elsewhere and extend their exact locators.
candidate_by_id["cand-10193"]["detail"] += " P.344 note 1 cites page 28; the page was not consulted."
candidate_by_id["cand-6200"]["detail"] += " P.344 note 3 cites volume II, pages 129-130; those pages were not consulted."
candidate_by_id["cand-8511"]["canonical_name"] = "G. A. Moschini, 1806, volume III, pages 49, 70, and 92 (citation locators)"
candidate_by_id["cand-8511"]["detail"] += " P.344 note 6 adds page 92; the cited page was not consulted."
candidate_by_id["cand-8815"]["canonical_name"] = "Battistella, 1930, pp.38 ff. and pp.60 ff. (citation locator; title pending)"
candidate_by_id["cand-8815"]["detail"] += " P.344 note 7 adds pages 60 ff.; the cited pages were not consulted."
candidate_by_id["cand-9279"]["detail"] += " P.344 note 5 continues at L122 and cites the 1843 Memorie via p.276 note 1; that locator was not consulted."
candidate_by_id["cand-9340"]["detail"] += " P.344 note 4 cites page 146; the cited page was not consulted."
candidate_by_id["cand-10192"]["detail"] += " P.344 note 5 cites page 12 for Vianello's reported opinion; the page was not consulted."

all_candidate_ids = set(candidate_by_id) | new_candidate_ids
notes_text = "\n".join(source_lines[178:251])
line_offsets = {}
offset = 0
for line_number, line_text in enumerate(source_lines[178:251], start=179):
    line_offsets[line_number] = offset
    offset += len(line_text) + 1
new_mentions = []


def add_mention(line_number, surface, candidate_id, note="", occurrence=0):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"candidate FK missing for mention {surface!r}: {candidate_id}")
    line_text = source_lines[line_number - 1]
    positions, cursor = [], 0
    while True:
        at = line_text.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention text missing at L{line_number}: {surface!r}")
    start = line_offsets[line_number] + positions[occurrence]
    end = start + len(surface)
    if notes_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    if any(row["segment_id"] == NOTES and row["candidate_id"] == candidate_id and row["start_char"] == str(start) and row["end_char"] == str(end) for row in mentions + new_mentions):
        raise SystemExit(f"duplicate mention at L{line_number}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p344-notes-{len(new_mentions)+1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })
    new_mentions.append(row)


mention_specs = [
    (239, "Borroni", "cand-10193", "Short-form source citation; underlying work not identified or consulted."),
    (240, "P. Clement, p. 124", "cand-10217", "Short-form source citation; title and author identity remain unresolved."),
    (240, "John Northall", "cand-10215", "Quoted writer named in Haskell's note; identity not externally aligned."),
    (240, "John Northall wrote (p. 43 8)", "cand-10216", "Citation locator in S0 transcription; print reads p.438, recorded as an S2 correction."),
    (240, "Signor Lanetti’s", "cand-2838", "Printed [sic] form preserved; Haskell's context identifies the referred-to dealer as Zanetti, without normalizing the quotation."),
    (241, "Bottari, II, pp. 129-30", "cand-6200", "Short citation to the bibliographically identified Raccolta; cited pages not consulted."),
    (241, "Bottari", "cand-0417", "Author named in the citation."),
    (242, "Blunt and Croft-Murray", "cand-9340", "Short citation to the 1957 Venetian drawings volume; cited page not consulted."),
    (242, "Blunt", "cand-0379", "Coauthor named in the citation."),
    (242, "Croft-Murray", "cand-9339", "Coauthor surname named in the citation; identity remains unresolved."),
    (243, "Vianello", "cand-2764", "Named as the first editor of Rosalba's diary; preserve the short form."),
    (243, "Lorenzetti, 1917", "cand-10192", "Short-form cited publication; page 12 not consulted."),
    (243, "Lorenzetti", "cand-9947", "Author named in the cited short-form publication."),
    (244, "G. A. Moschini, 1806, III, p. 92", "cand-8511", "Short citation; title unresolved and cited page not consulted."),
    (244, "G. A. Moschini", "cand-1709", "Author named in the citation."),
    (245, "Battistella, 1930, pp. 60 ff.", "cand-8815", "Short-form cited source; title unresolved and cited pages not consulted."),
    (246, "Biblioteca Marucelliana", "cand-9493", "Repository named in the letter locator; manuscript not consulted."),
    (246, "Florence", "cand-3397", "Repository location as printed."),
    (246, "Letter of 26 August 1752 to A. F. Gori", "cand-10218", "Specific letter locator; keep separate from the 22 December 1752 letter."),
    (246, "A. F. Gori", "cand-1214", "Recipient as named in the printed locator."),
]
for spec in mention_specs:
    add_mention(*spec)

new_statement_specs = [
    {
        "id": "st-chp13-p344-notes-note1-borroni-p28", "marker": "1", "line": 239,
        "subject": "cand-10193", "object": "cand-0025", "predicate": "borroni_page28_cited_for_dactyliotheca_publisher_claim",
        "claim": "P.344 note 1 cites F. Borroni, page 28, for the Dactyliotheca passage identifying Albrizzi as publisher.",
        "qualification": "This is an internal citation locator; Borroni's page was not consulted.",
        "mentioned": ["cand-10193", "cand-0025", "cand-10012"],
        "citations": [{"source_candidate_id": "cand-10193", "page": "28"}],
        "linked": ["st-chp13-p344-albrizzi-publisher_dactyliotheca"],
    },
    {
        "id": "st-chp13-p344-notes-note2-clement-p124", "marker": "2", "line": 240,
        "subject": "cand-10217", "object": "cand-0789", "predicate": "clement_page124_cited_for_zanetti_description",
        "claim": "P.344 note 2 cites P. Clement, page 124, for the preceding Abbé Clement description of Zanetti.",
        "qualification": "The short-form citation is retained; its author, title, edition, and page contents were not independently resolved or consulted.",
        "mentioned": ["cand-10217", "cand-0789"],
        "citations": [{"source_candidate_id": "cand-10217", "page": "124", "cited_person_candidate_id": "cand-0789"}],
        "linked": ["st-chp13-p344-clement-description_of_zanetti", "st-chp13-p344-haskell-sale_catalogue_interpretation"],
    },
    {
        "id": "st-chp13-p344-notes-note2-northall-quote", "marker": "2", "line": 240,
        "subject": "cand-10216", "object": "cand-2838", "predicate": "northall_1767_quote_reports_prints_at_lanettis_sic",
        "claim": "Haskell's note quotes John Northall in 1767 as saying plates of the antiquities could be seen at Signor Lanetti's [sic], a dealer with a fine collection of pictures and drawings, including some of his own from wooden plates, cameos, and intaglios.",
        "qualification": "Preserve the quotation's printed Lanetti's [sic] form and Northall's attribution. The p.438 locator is corrected from S0's OCR spacing against CHP-13.pdf; Northall's page was not consulted.",
        "mentioned": ["cand-10215", "cand-10216", "cand-2838"],
        "citations": [{"source_candidate_id": "cand-10216", "author_candidate_id": "cand-10215", "year": "1767", "page": "438"}],
        "linked": ["st-chp13-p344-clement-description_of_zanetti", "st-chp13-p344-haskell-sale_catalogue_interpretation"],
        "ocr_corrections": [{"source_line": 240, "ocr": "p. 43 8", "print": "p. 438", "basis": "CHP-13.pdf physical page 13."}],
    },
    {
        "id": "st-chp13-p344-notes-note3-bottari-II-129-130", "marker": "3", "line": 241,
        "subject": "cand-6200", "object": "cand-2838", "predicate": "bottari_volumeII_pages129_130_cited_for_painting_claim",
        "claim": "P.344 note 3 cites Bottari, volume II, pages 129-130, for Haskell's statement that Zanetti painted for his own pleasure.",
        "qualification": "The cited pages were not consulted; the full work title follows the local bibliography candidate and remains subject to global S3 reconciliation.",
        "mentioned": ["cand-6200", "cand-0417", "cand-2838"],
        "citations": [{"source_candidate_id": "cand-6200", "author_candidate_id": "cand-0417", "volume": "II", "pages": "129-130"}],
        "linked": ["st-chp13-p344-zanetti-painted_for_pleasure"],
    },
    {
        "id": "st-chp13-p344-notes-note4-blunt-croftmurray-146", "marker": "4", "line": 242,
        "subject": "cand-9340", "object": "cand-2838", "predicate": "blunt_croft_murray_page146_cited_for_caricatures",
        "claim": "P.344 note 4 cites Blunt and Croft-Murray, page 146, for the statement that Zanetti drew operatic caricatures.",
        "qualification": "The cited page was not consulted; the coauthor identity is retained as indexed and remains for S3 alignment.",
        "mentioned": ["cand-9340", "cand-0379", "cand-9339", "cand-2838"],
        "citations": [{"source_candidate_id": "cand-9340", "author_candidate_ids": ["cand-0379", "cand-9339"], "page": "146"}],
        "linked": ["st-chp13-p344-zanetti-drew_operatic_caricatures"],
    },
    {
        "id": "st-chp13-p344-notes-note5-vianello-lorenzetti-p12", "marker": "5", "line": 243,
        "subject": "cand-10192", "object": "cand-0581", "predicate": "vianello_opinion_on_carriera_learning_cited_via_lorenzetti_p12",
        "claim": "P.344 note 5 attributes the view that Rosalba Carriera learned much from Zanetti to the first editor of her diary, Vianello, and cites Lorenzetti, 1917, page 12.",
        "qualification": "This preserves the book's attribution chain; neither Lorenzetti's cited page nor Vianello's edition was independently consulted.",
        "mentioned": ["cand-10192", "cand-9947", "cand-2764", "cand-0581", "cand-2838"],
        "citations": [{"source_candidate_id": "cand-10192", "author_candidate_id": "cand-9947", "named_editor_candidate_id": "cand-2764", "year": "1917", "page": "12"}],
        "linked": ["st-chp13-p344-carriera-learning_claim"],
        "ocr_corrections": [{"source_line": 243, "ocr": "sec Lorenzetti", "print": "see Lorenzetti", "basis": "CHP-13.pdf physical page 13."}],
    },
    {
        "id": "st-chp13-p344-notes-note5-memorie-continuation", "marker": "5", "line": 122, "segment": BODY,
        "subject": "cand-9279", "object": "cand-10112", "predicate": "1843_memorie_cited_for_felicita_sartori_employment_and_collection",
        "claim": "The p.344 continuation of note 5 cites the 1843 Memorie, via p.276 note 1, for the claims that Zanetti employed Félicita Sartori as an engraver and owned a large collection of her work.",
        "qualification": "The print spells Felicita without an accent; no date, title, or contents beyond the supplied citation are inferred. The 1843 volume is reused from the full title already recorded at p.276; it is distinct from Zanetti's 1736 Memorie candidate.",
        "mentioned": ["cand-9279", "cand-2838", "cand-2363", "cand-10112"],
        "citations": [{"source_candidate_id": "cand-9279", "publication_year": "1843", "locator": "p.276 note 1"}],
        "linked": ["st-chp13-p344-zanetti-employed_felicita_sartori", "st-chp13-p344-zanetti-owned_felicita_work"],
        "ocr_corrections": [{"source_line": 122, "ocr": "Félicita", "print": "Felicita", "basis": "CHP-13.pdf physical page 13."}],
    },
    {
        "id": "st-chp13-p344-notes-note6-moschini-III-p92", "marker": "6", "line": 244,
        "subject": "cand-8511", "object": "cand-2877", "predicate": "moschini_1806_volumeIII_page92_cited_for_zompini_employment",
        "claim": "P.344 note 6 cites G. A. Moschini, 1806, volume III, page 92, for Zanetti's employment, housing, and allowance for Gaetano Zompini.",
        "qualification": "The citation's title and edition remain unresolved; the cited page was not consulted.",
        "mentioned": ["cand-8511", "cand-1709", "cand-2838", "cand-2877"],
        "citations": [{"source_candidate_id": "cand-8511", "author_candidate_id": "cand-1709", "year": "1806", "volume": "III", "page": "92"}],
        "linked": ["st-chp13-p344-zanetti-employed_zompini"],
    },
    {
        "id": "st-chp13-p344-notes-note7-battistella-1930-p60ff", "marker": "7", "line": 245,
        "subject": "cand-8815", "object": "cand-10111", "predicate": "battistella_1930_pages60ff_cited_for_le_arti_assessment",
        "claim": "P.344 note 7 cites Battistella, 1930, pages 60 ff., in connection with Haskell's assessment of Le Arti.",
        "qualification": "The source title and cited pages remain unresolved and were not consulted.",
        "mentioned": ["cand-8815", "cand-10111"],
        "citations": [{"source_candidate_id": "cand-8815", "year": "1930", "pages": "60 ff."}],
        "linked": ["st-chp13-p344-haskell-le_arti_assessment"],
    },
    {
        "id": "st-chp13-p344-notes-note8-zanetti-gori-letter-1752-08-26", "marker": "8", "line": 246,
        "subject": "cand-10218", "object": "cand-1214", "predicate": "printed_locator_identifies_26_august_1752_gori_letter",
        "claim": "P.344 note 8 locates the letter of 26 August 1752 to A. F. Gori at Biblioteca Marucelliana, MSS. B. VIII, 13.",
        "qualification": "The locator's sender is attributed to A. M. Zanetti from the adjacent body quotation; the manuscript was not consulted. This is not the 22 December 1752 letter cited at p.342 note 6.",
        "mentioned": ["cand-10218", "cand-1214", "cand-9493", "cand-3397"],
        "citations": [{"source_candidate_id": "cand-10218", "recipient_candidate_id": "cand-1214", "repository_candidate_id": "cand-9493", "shelfmark": "MSS. B. VIII, 13", "date": "1752-08-26"}],
        "linked": ["st-chp13-p344-zanetti-1752-incomplete_letter_fragment"],
    },
]

new_statements = []
note_statement_ids_by_marker = {str(number): [] for number in range(1, 9)}
for spec in new_statement_specs:
    for candidate_id in spec["mentioned"]:
        if candidate_id not in all_candidate_ids:
            raise SystemExit(f"statement candidate missing: {spec['id']} -> {candidate_id}")
    segment = spec.get("segment", NOTES)
    line = spec["line"]
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": 344,
        "pdf_physical_page": 13,
        "claim": spec["claim"],
        "speaker": "Haskell, printed footnote",
        "text_layer": "secondary source note and citation",
        "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"],
        "footnote_marker": spec["marker"],
        "footnote_printed_page": 344,
        "linked_body_statement_ids": spec["linked"],
        "citations": spec["citations"],
        "relation_candidate": False,
    }
    if spec.get("ocr_corrections"):
        qualifiers["ocr_corrections"] = spec["ocr_corrections"]
    quote = source_lines[line - 1]
    row = {
        "statement_id": spec["id"],
        "segment_id": segment,
        "subject_candidate_id": spec["subject"],
        "object_candidate_id": spec["object"],
        "predicate": spec["predicate"],
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    }
    if row["statement_id"] in statement_by_id:
        raise SystemExit(f"duplicate statement ID: {row['statement_id']}")
    new_statements.append(row)
    note_statement_ids_by_marker[spec["marker"]].append(spec["id"])

body_note_targets = {
    "1": ["st-chp13-p344-albrizzi-publisher_dactyliotheca"],
    "2": ["st-chp13-p344-haskell-sale_catalogue_interpretation", "st-chp13-p344-clement-description_of_zanetti"],
    "3": ["st-chp13-p344-zanetti-painted_for_pleasure"],
    "4": ["st-chp13-p344-zanetti-drew_operatic_caricatures"],
    "5": ["st-chp13-p344-carriera-learning_claim", "st-chp13-p344-zanetti-employed_felicita_sartori", "st-chp13-p344-zanetti-owned_felicita_work"],
    "6": ["st-chp13-p344-zanetti-employed_zompini"],
    "7": ["st-chp13-p344-haskell-le_arti_assessment"],
    "8": ["st-chp13-p344-zanetti-1752-incomplete_letter_fragment"],
}
for marker, targets in body_note_targets.items():
    for statement_id in targets:
        if statement_id not in statement_by_id:
            raise SystemExit(f"p.344 marker {marker} target missing: {statement_id}")
        pending = statement_by_id[statement_id].get("qualifiers", {}).get("note_refs_pending", [])
        if not any(ref.get("printed_note") == int(marker) and ref.get("segment_id") == NOTES for ref in pending):
            raise SystemExit(f"p.344 marker {marker} is not pending on {statement_id}")
    if not note_statement_ids_by_marker[marker]:
        raise SystemExit(f"p.344 marker {marker} has no note statement")

# The print places note 1 only after Albrizzi's publisher clause. Remove its broad OCR-derived
# pending refs from other p.344 claims instead of converting those into false links.
allowed_targets = {statement_id for group in body_note_targets.values() for statement_id in group}
for statement_id in [sid for sid, row in statement_by_id.items() if row.get("segment_id") == BODY]:
    q = statement_by_id[statement_id].setdefault("qualifiers", {})
    pending = q.get("note_refs_pending", [])
    kept = []
    for ref in pending:
        if ref.get("segment_id") != NOTES:
            kept.append(ref)
            continue
        marker = str(ref.get("printed_note"))
        if marker not in body_note_targets:
            raise SystemExit(f"unexpected p.344 pending marker {marker} on {statement_id}")
        if statement_id not in body_note_targets[marker]:
            if marker == "1":
                continue
            raise SystemExit(f"p.344 note {marker} target mapping mismatch: {statement_id}")
        note_ids = note_statement_ids_by_marker[marker]
        refs = q.setdefault("footnote_refs", [])
        if any(r.get("footnote_marker") == marker and r.get("footnote_printed_page") == 344 for r in refs):
            raise SystemExit(f"duplicate p.344 footnote ref on {statement_id}")
        refs.append({
            "footnote_marker": marker,
            "footnote_printed_page": 344,
            "footnote_text_pending": False,
            "footnote_segment": NOTES,
            "footnote_line_range": f"L{239 + int(marker) - 1}",
            "footnote_body_link_status": "linked",
            "footnote_note_statement_ids": note_ids,
        })
        q["footnote_note_statement_ids"] = sorted(set(q.get("footnote_note_statement_ids", [])) | set(note_ids))
        q["footnote_text_pending"] = False
        q["footnote_body_link_status"] = "linked"
    if kept:
        q["note_refs_pending"] = kept
    else:
        q.pop("note_refs_pending", None)

for marker, targets in body_note_targets.items():
    note_ids = note_statement_ids_by_marker[marker]
    for statement_id in targets:
        refs = statement_by_id[statement_id].get("qualifiers", {}).get("footnote_refs", [])
        if not any(
            ref.get("footnote_marker") == marker
            and ref.get("footnote_printed_page") == 344
            and not ref.get("footnote_text_pending")
            and ref.get("footnote_note_statement_ids") == note_ids
            for ref in refs
        ):
            raise SystemExit(f"p.344 marker {marker} did not link to {statement_id}")
if any(
    ref.get("footnote_marker") == "1" and ref.get("footnote_printed_page") == 344
    for row in statement_by_id.values() if row.get("segment_id") == BODY
    for ref in row.get("qualifiers", {}).get("footnote_refs", [])
    if row["statement_id"] not in body_note_targets["1"]
):
    raise SystemExit("p.344 note 1 remains linked to a non-publisher statement")

for statement_id in ("st-chp13-p344-zanetti-employed_felicita_sartori", "st-chp13-p344-zanetti-owned_felicita_work"):
    q = statement_by_id[statement_id]["qualifiers"]
    q["speaker"] = "Haskell, printed footnote"
    q["text_layer"] = "secondary source note and citation"
    q["qualification"] = (q.get("qualification", "") + " The statement is the continuation of printed p.344 note 5 at L122, not ordinary body prose.").strip()

# The line 122 continuation is a footnote citation and source statement in the body segment;
# keep its own source-local anchor and link it to the two claims it qualifies.
continuation = next(row for row in new_statements if row["statement_id"] == "st-chp13-p344-notes-note5-memorie-continuation")
continuation["qualifiers"]["footnote_continuation"] = True

for row in new_statements:
    if row["original_quote"] not in (notes_text if row["segment_id"] == NOTES else "\n".join(source_lines[115:122])):
        raise SystemExit(f"statement quote not found in its source segment: {row['statement_id']}")
for row in new_mentions:
    if notes_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"final mention span failed: {row['mention_id']}")

coverage[NOTES]["source_line_ranges"] = "L180-246"
coverage[NOTES]["note"] = (
    "Notes L180-246 (pp.332-344) are migrated and p.332-344 printed notes are linked to their marked claims. "
    "The p.342 note 6 letter locator remains linked across the p.342-343 continuous quotation; p.344 note 5 continues at L122. "
    "Mirrored caption lines L247-248 and p.345 notes L249-251 remain; the composite segment remains partial."
)
coverage[BODY]["migration_status"] = "complete"
coverage[BODY]["source_line_ranges"] = "L116-122"
coverage[BODY]["note"] = (
    "Printed p.344 footnotes 1-8 are migrated from consolidated lines L239-L246 and linked to their marked claims. "
    "The p.344 note 5 continuation at L122 is recorded as a secondary-source note and linked to its cited Memorie. "
    "The p.344 1752 letter quotation continues after the intervening Plate 57 and closes at p.345 L162 (CHP-13.pdf physical page 18), already cross-linked to its p.345 continuation statement."
)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = [statement_by_id.get(row["statement_id"], row) for row in statements] + new_statements
if len({row["candidate_id"] for row in candidate_out}) != len(candidate_out):
    raise SystemExit("candidate IDs are not unique after migration")
if len({row["mention_id"] for row in mention_out}) != len(mention_out):
    raise SystemExit("mention IDs are not unique after migration")
if len({row["statement_id"] for row in statement_out}) != len(statement_out):
    raise SystemExit("statement IDs are not unique after migration")
if any(row["candidate_id"] not in {candidate["candidate_id"] for candidate in candidate_out} for row in mention_out):
    raise SystemExit("mention candidate FK missing after migration")
candidate_ids_out = {row["candidate_id"] for row in candidate_out}
statement_ids_out = {row["statement_id"] for row in statement_out}
for row in new_statements:
    for field in ("subject_candidate_id", "object_candidate_id"):
        if row.get(field) and row[field] not in candidate_ids_out:
            raise SystemExit(f"statement candidate FK missing: {row['statement_id']} -> {row[field]}")
    for linked_id in row.get("qualifiers", {}).get("linked_body_statement_ids", []):
        if linked_id not in statement_ids_out:
            raise SystemExit(f"linked body statement missing: {row['statement_id']} -> {linked_id}")

print(f"candidate rows: {len(candidates)} -> {len(candidate_out)} (+{len(new_candidates)})")
print(f"mention rows: {len(mentions)} -> {len(mention_out)} (+{len(new_mentions)})")
print(f"statement rows: {len(statements)} -> {len(statement_out)} (+{len(new_statements)})")
print("coverage: p.344 footnotes 1-8 linked; body complete because the 1752 letter quotation closes at p.345 L162 after the intervening Plate 57")
print("p.344 note 1 linked only to Albrizzi's publisher claim; note 2 keeps Clement and Northall attribution layers separate")
print("print corrections recorded only in S2: p.43 8 -> p.438; sec -> see; Félicita -> Felicita")
if not args.apply:
    print("dry-run only; no tables written")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
if any(path.exists() for path in backups):
    raise SystemExit("one or more migration backup paths already exist")
for path, backup in zip(targets, backups):
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_out)
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statement_out)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied with four table backups:")
for path in backups:
    print(f"  {path.relative_to(ROOT)}")
