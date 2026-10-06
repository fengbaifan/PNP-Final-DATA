"""Controlled S2 migration for the printed p.320–323 notes; dry-run by default."""

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
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BACKUP_SUFFIX = ".bak-s2-chp10-p320-323-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write reviewed p.320–323 note rows and links")
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
    raise SystemExit("canonical Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_lines = {
    308: "1 Lorenzetti, 1917, p. 49, note 1.",
    309: "2 Our only source for Lodoli’s life is Andrea Memmo’s anonymous",
    310: "8 In [P. Angelo Calogerà]: Raccolta, I, 1728.",
    311: "1 Letter from the Abate Ortes to Francesco Algarotti",
    312: "2 G. AMoschini, 1815,1, p. 48.",
    313: "3 Gozzi, I, p. 26—Dialogo tra un librajo",
    314: "1 For Algarotti’s reactions to Lodoli see Kauffmann",
    315: "2 Biblioteca Correr, Venice—MSS. Cotter, Misc. XI/1348 (1140).",
    316: "3 Previtali.",
    317: "4 Tlie portrait by Alessandro Longbi is in the Accademia",
    318: "1 Goldoni: Al Signor Pietro Longhi veneziano celebre pittore",
    319: "2 Goldoni, II, p. 92—dedication of II Frappatore.",
    320: "3 Dazzi.",
    321: "4 Goldoni is not actually named, but the allusion to him is clear",
    322: "6 [Paoletti], 1832, p. 122.",
    323: "6 Letter horn Pietro Visconti to Gian Pietro Ligari",
    324: "7 Gazzetta Veneta, No. 35, 13 Agosto 1760.",
}
for line_no, prefix in expected_lines.items():
    if not source_lines[line_no - 1].startswith(prefix):
        raise SystemExit(f"canonical note boundary changed at L{line_no}")

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

state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (9933, 9946, 21088, 9372):
    raise SystemExit(f"unexpected table pre-state: {state}")
body_segments = {
    "p320": "chp-10:10_CHP-10_sec_ii:l151-163",
    "p321": "chp-10:10_CHP-10_sec_ii:l165-173",
    "p322": "chp-10:10_CHP-10_sec_ii:l175-184",
    "p323": "chp-10:10_CHP-10_sec_ii:l186-192",
}
if NOTES not in coverage or any(segment not in coverage for segment in body_segments.values()):
    raise SystemExit("required S2 coverage row missing")
if coverage[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated note segment is not partial")
for name, segment in body_segments.items():
    if (coverage[segment]["disposition"], coverage[segment]["migration_status"]) != ("reviewed", "partial"):
        raise SystemExit(f"{name} body segment is not reviewed/partial")
if any(sid.startswith("st-chp10-p320-323-n") for sid in statement_ids):
    raise SystemExit("p.320–323 note statements already exist")
if any(row["mention_id"].startswith("m-s2-ch10-p320-323-note-") for row in mentions):
    raise SystemExit("p.320–323 note mentions already exist")
if candidate_by_id["cand-8812"]["canonical_name"] != "Andrea Memmo, 1786, pp.4 ff. (citation locator; title pending)":
    raise SystemExit("expected Memmo citation candidate changed")
if candidate_by_id["cand-9774"]["detail"] != "Haskell reports an unnamed historian's claim that Longhi was punished for depicting truth. The historian is not named in the prose; note 5 cites Paoletti and qualifies the report, pending full note migration.":
    raise SystemExit("expected p.323 historian candidate changed")

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


add_candidate("cand-9947", "Lorenzetti (author cited in p.320 note 1; identity unresolved)", "person", "Surname-only author reference; the note supplies no title or full identity.", 308)
add_candidate("cand-9948", "Lorenzetti, 1917, page 49 note 1 (citation locator)", "archive", "Short bibliographic citation attached to the woodcut-process notice; the cited page was not independently consulted.", 308)
add_candidate("cand-9949", "Petrocchi (author cited in p.320 note 2; identity unresolved)", "person", "Surname-only reference; no full identity is inferred.", 309)
add_candidate("cand-9950", "Petrocchi, 1947 (citation locator)", "archive", "Haskell's additional reference for Lodoli's life; title, page, and cited content are not supplied here.", 309)
add_candidate("cand-9951", "P. Angelo Calogerà (editor named in p.320 note 3)", "person", "The source gives the abbreviated name in brackets; no further identity detail is added.", 310)
add_candidate("cand-9952", "Raccolta, volume I (P. Angelo Calogerà, 1728; citation locator)", "archive", "Cited for the first publication in Venice of Vico's Autobiography; the volume was not independently consulted.", 310)
add_candidate("cand-9953", "Fisch (author cited in p.320 note 3; identity unresolved)", "person", "Surname-only reference; full identity and work title are not supplied.", 310)
add_candidate("cand-9954", "Bergin (author cited in p.320 note 3; identity unresolved)", "person", "Surname-only reference; full identity and work title are not supplied.", 310)
add_candidate("cand-9955", "Fisch and Bergin, pages 183–184 (citation locator)", "archive", "Additional reference attached to the Vico Autobiography statement; the cited pages were not independently consulted.", 310)
add_candidate("cand-9956", "Letter from Abate Ortes to Francesco Algarotti, 26 September 1749 (Algarotti XIV, page 315)", "archive", "Letter cited in the p.321 note. Temanza page 87 is retained as a separate locator; neither cited source was independently consulted.", 311)
add_candidate("cand-9957", "Temanza, page 87 (citation locator)", "archive", "Supplementary page reference in p.321 note 1; the cited page was not independently consulted.", 311)
add_candidate("cand-9958", "G. A. Moschini, 1815, volume I, page 48 (citation locator)", "archive", "The note cites Moschini for Lodoli's monastery modifications; cited text was not independently consulted.", 312)
add_candidate("cand-9959", "Gozzi, volume I, page 26, Dialogo tra un librajo e un Forestiere (citation locator)", "archive", "Citation attached to Gozzi's reported comment on ornamental building; the text was not independently consulted.", 313)
add_candidate("cand-9960", "Kauffmann (author cited in p.322 note 1; identity unresolved)", "person", "Surname-only author reference; the note gives years 1944 and 1955 but no titles.", 314)
add_candidate("cand-9961", "Kauffmann, 1944 and 1955 (citation locator)", "archive", "References cited for Algarotti's reactions to Lodoli; neither work was independently consulted.", 314)
add_candidate("cand-9962", "Biblioteca Correr manuscript, Misc. XI/1348 (1140) (citation locator)", "archive", "The repository is Biblioteca Correr; the OCR form 'Cotter' in the shelf locator is corrected to the printed 'Correr'. The manuscript was not consulted.", 315)
add_candidate("cand-9963", "Accademia in Venice named as portrait location (institution unresolved)", "institution", "The p.322 note states that the Carlo Lodoli portrait is in an Accademia in Venice but does not identify the exact institution. The List of Plates instead says Museo Correr; conflict remains unresolved.", 317)
add_candidate("cand-9964", "[Memmo], Riflessioni, 1788 (citation locator for portrait history)", "archive", "The note refers readers to this work for the portrait's history; the work was not independently consulted.", 317)
add_candidate("cand-9965", "Goldoni, Al Signor Pietro Longhi veneziano celebre pittore, Opere XIII, page 187 (citation locator)", "archive", "Citation for Goldoni's 1750 praise of Pietro Longhi; cited text was not independently consulted.", 318)
add_candidate("cand-9966", "Goldoni, volume II, page 92, dedication of Il Frappatore (citation locator)", "archive", "Citation for Goldoni's later praise of Longhi; cited text was not independently consulted.", 319)
add_candidate("cand-9967", "Dazzi (author cited in p.323 note 3; identity unresolved)", "person", "Surname-only citation; no title, page, or full identity is given.", 320)
add_candidate("cand-9968", "Dazzi (citation locator for Goldoni's sympathies)", "archive", "The note supplies only the surname and no title or page; cited source was not independently consulted.", 320)
add_candidate("cand-9969", "Letter from Giuseppe Gennari to Gaspare Patriarchi, 5 November 1761 (published locator)", "archive", "Haskell says the letter is published by Melchiori at page 142. The letter and publication were not independently consulted.", 321)
add_candidate("cand-9970", "Patriarchi, Gaspare (recipient named in p.323 note 4)", "person", "The note gives a full name but no other identifying details; identity alignment is deferred.", 321)
add_candidate("cand-9971", "Melchiori (editor/publisher cited in p.323 note 4; identity unresolved)", "person", "Surname-only publication attribution; no full identity is inferred.", 321)
add_candidate("cand-9972", "Melchiori, page 142 (citation locator for the 1761 Gennari letter)", "archive", "The note gives a page locator but no work title; cited source was not independently consulted.", 321)
add_candidate("cand-9973", "Paoletti (author cited in p.323 note 5; identity unresolved)", "person", "Surname-only reference to the source cited for an unsupported Longhi story; no full name is inferred.", 322)
add_candidate("cand-9974", "Paoletti, 1832, page 122 (citation locator)", "archive", "Cited for the claim that Longhi was punished for depicting truth; Haskell's note rejects the evidence and says the source does not seem wholly reliable.", 322)
add_candidate("cand-9975", "Archives of the Inquisitors (repository named in p.323 note 5; identity unresolved)", "institution", "Haskell says there is no evidence for the punishment story in these archives; no exact archival institution or record is identified.", 322)
add_candidate("cand-9976", "Gazzetta Veneta, issue no. 55, 13 August 1760 (citation locator)", "archive", "The OCR gives issue 35, but the printed p.323 note reads 55. The issue was not independently consulted.", 324)

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
        "mention_id": f"m-s2-ch10-p320-323-note-{len(new_mentions) + 1:04d}",
        "segment_id": NOTES,
        "candidate_id": cid,
        "surface_form": needle,
        "start_char": offset,
        "end_char": offset + len(needle),
        "note": note,
    })
    new_mentions.append(row)


for cid, line, needle, note in [
    ("cand-9947", 308, "Lorenzetti", "Surname of cited author; identity unresolved."),
    ("cand-9948", 308, "1917, p. 49, note 1", "Bibliographic year and locator as printed."),
    ("cand-1647", 309, "Andrea Memmo", "Named author reused from the Lodoli passage; identity alignment remains a later-stage decision."),
    ("cand-8812", 309, "Elementi dell’architettura lodoliana", "The title identifies the previously unresolved 1786 Memmo citation candidate."),
    ("cand-8812", 309, "first published in Rome in 1786", "Publication place and year stated by Haskell."),
    ("cand-9949", 309, "Petrocchi", "Surname of the additional author cited by Haskell."),
    ("cand-9950", 309, "1947", "Year supplied for the additional Petrocchi reference."),
    ("cand-9951", 310, "P. Angelo Calogerà", "Editor named in brackets in the note."),
    ("cand-9952", 310, "Raccolta, I, 1728", "Publication locator for the Vico Autobiography source."),
    ("cand-9953", 310, "Fisch", "First surname in the additional citation."),
    ("cand-9954", 310, "Bergin", "Second surname in the additional citation."),
    ("cand-9955", 310, "pp. 183-4", "Page range as printed in the note."),
    ("cand-1789", 311, "Abate Ortes", "Named correspondent; reuse the existing Ortes candidate."),
    ("cand-0048", 311, "Francesco Algarotti", "Named recipient; reuse the existing candidate."),
    ("cand-9956", 311, "26 September 1749", "Date of the cited Ortes letter."),
    ("cand-9956", 311, "Algarotti, XIV, p. 315", "Publication locator for the Ortes letter."),
    ("cand-9957", 311, "Temanza, p. 87", "Additional citation locator; author candidate exists separately."),
    ("cand-1709", 312, "Moschini", "Cited author; reuse the existing Moschini candidate and retain the OCR form in this mention."),
    ("cand-9958", 312, "1815,1, p. 48", "OCR locator; print reading is 1815, I, p. 48."),
    ("cand-1220", 313, "Gozzi", "Named author reused from the body passage."),
    ("cand-9959", 313, "I, p. 26", "Volume and page locator."),
    ("cand-9959", 313, "Dialogo tra un librajo e un Forestiere", "Title as transcribed in S0."),
    ("cand-9960", 314, "Kauffmann", "Surname of cited author; identity unresolved."),
    ("cand-9961", 314, "1944 and 1955", "Years of the two cited references."),
    ("cand-8262", 315, "Biblioteca Correr", "Named repository reused from the candidate table."),
    ("cand-9962", 315, "MSS. Cotter, Misc. XI/1348 (1140)", "OCR shelf locator; print reads MSS. Correr, Misc. XI/1348 (1140)."),
    ("cand-9508", 316, "Previtali", "Reuse the existing surname-only author candidate; work identity remains unresolved."),
    ("cand-1425", 317, "Tlie portrait", "OCR spelling; the print reads 'The portrait'. The following phrase identifies this as the portrait in the p.322 discussion; preserve source-specific portrait candidates."),
    ("cand-1424", 317, "Alessandro Longbi", "OCR spelling; the print reads Alessandro Longhi."),
    ("cand-9963", 317, "Accademia in Venice", "Institution is unnamed beyond this source wording."),
    ("cand-1647", 317, "[Memmo]", "Surname in brackets; do not infer more than the linked candidate context supports."),
    ("cand-9964", 317, "Riflessioni, 1788", "Work and year cited for the portrait's history."),
    ("cand-1206", 318, "Goldoni", "Named author; reuse the existing Carlo Goldoni candidate."),
    ("cand-9965", 318, "Al Signor Pietro Longhi veneziano celebre pittore", "Title of the cited Goldoni text."),
    ("cand-9965", 318, "Opere, XIII, p. 187", "Edition and page locator."),
    ("cand-1206", 319, "Goldoni", "Named author; reuse the existing candidate."),
    ("cand-9966", 319, "II, p. 92", "Volume and page locator."),
    ("cand-9966", 319, "II Frappatore", "Title of the dedication named in the note."),
    ("cand-9967", 320, "Dazzi", "Surname-only cited author."),
    ("cand-1206", 321, "Goldoni", "Subject of the allusion as identified by Haskell."),
    ("cand-1130", 321, "Giuseppe Gennari", "Named letter writer; reuse the existing Gennari candidate."),
    ("cand-9970", 321, "Gaspare Patriarchi", "Named recipient; identity alignment deferred."),
    ("cand-9969", 321, "5 November 1761", "Date of the cited letter."),
    ("cand-9971", 321, "Melchiori", "Surname of the named publisher/editor; identity unresolved."),
    ("cand-9972", 321, "p. 142", "Page locator for the published letter."),
    ("cand-9973", 322, "[Paoletti]", "Surname of the cited source author."),
    ("cand-9974", 322, "1832, p. 122", "Publication year and page locator."),
    ("cand-9975", 322, "Archives of the Inquisitors", "Repository named in Haskell's note; exact institutional identity is unresolved."),
    ("cand-9973", 322, "and Paoletti", "Repeated author reference in the note's continuation."),
    ("cand-8465", 323, "Pietro Visconti", "Letter writer reused from the existing source candidate."),
    ("cand-1408", 323, "Gian Pietro Ligari", "Letter recipient reused from the existing candidate."),
    ("cand-8466", 323, "19 December 1749", "Date of the cited letter."),
    ("cand-8467", 323, "Arslan", "Surname-only publisher/editor candidate reused for this same 1952 letter locator."),
    ("cand-8466", 323, "1952, p. 63", "Published citation locator; same letter candidate is reused."),
    ("cand-8729", 324, "Gazzetta Veneta", "Periodical candidate reused from an earlier citation."),
    ("cand-9976", 324, "No. 35", "OCR issue number; printed p.323 reads No. 55."),
    ("cand-9976", 324, "13 Agosto 1760", "Issue date as printed."),
]:
    add_mention(cid, line, needle, note)

new_statements = []


def add_statement(sid, subject, object_id, predicate, line, printed_page, physical_page, claim, qualification,
                  mentioned, body_ids, marker, relation_candidate=False, extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement ID already exists: {sid}")
    if subject not in all_candidate_ids or object_id not in all_candidate_ids:
        raise SystemExit(f"statement candidate missing: {sid}")
    mentioned = list(dict.fromkeys(mentioned))
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"statement mention candidate missing: {sid}")
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": printed_page,
        "pdf_physical_page": physical_page,
        "claim": claim,
        "speaker": "Haskell footnote",
        "text_layer": "bibliographic citation and source qualification",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
        "footnote_number": marker,
        "linked_body_statement_ids": body_ids,
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
        "original_quote": source_lines[line - 1],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


add_statement("st-chp10-p320-323-n01-lorenzetti-citation", "cand-2838", "cand-9948", "cites_lorenzetti_for_woodcut_process_notice",
              308, 320, 53, "Haskell cites Lorenzetti, 1917, page 49 note 1, for the preceding notice about elder Zanetti and colour woodcuts.",
              "The cited page was not independently consulted; Lorenzetti's full identity and the work title are not supplied.",
              ["cand-2838", "cand-9947", "cand-9948", "cand-9734"],
              ["st-chp10-p320-zanetti-announced-colour-woodcut-process-to-conti"], 1,
              extra={"citations": [{"source_candidate_id": "cand-9948", "author_candidate_id": "cand-9947", "year": "1917", "page": "49", "note": "1"}]})
add_statement("st-chp10-p320-323-n02-memmo-elementi-lodoli-life", "cand-1411", "cand-8812", "cites_memmo_elementi_as_source_for_lodoli_life",
              309, 320, 53, "Haskell identifies Andrea Memmo's anonymous Elementi dell’architettura lodoliana, first published in Rome in 1786, as the only source for Lodoli's life, notes scattered Venetian learned-journal references, and adds Petrocchi, 1947.",
              "The title resolves the earlier title-pending citation candidate cand-8812 through this book-internal note. Neither Memmo nor Petrocchi was independently consulted; the relationship between individual claims and these sources is not expanded beyond the note.",
              ["cand-1411", "cand-1647", "cand-8812", "cand-9949", "cand-9950"],
              ["st-chp10-p320-lodoli-brother-of-minori-osservanti"], 2,
              extra={"citations": [{"source_candidate_id": "cand-8812", "author_candidate_id": "cand-1647", "title": "Elementi dell’architettura lodoliana", "publication_place": "Rome", "year": "1786"}, {"source_candidate_id": "cand-9950", "author_candidate_id": "cand-9949", "year": "1947"}], "source_identity_resolution": "Memmo 1786 title linked to existing p.309/p.272 locator by matching author, year, Lodoli subject, and cited pages; no external source consulted"})
add_statement("st-chp10-p320-323-n03-calogera-raccolta-vico-autobiography", "cand-9740", "cand-9952", "cites_calogera_raccolta_for_vico_autobiography",
              310, 320, 53, "Haskell cites P. Angelo Calogerà's Raccolta, volume I, 1728, for the note that Vico's Autobiography was first published in Venice.",
              "The OCR note marker is 8, but the print shows note 3. The publication was not independently consulted.",
              ["cand-9740", "cand-2719", "cand-9951", "cand-9952"],
              ["st-chp10-p320-vico-autobiography-first-published-in-venice"], 3,
              extra={"citations": [{"source_candidate_id": "cand-9952", "editor_candidate_id": "cand-9951", "volume": "I", "year": "1728"}], "ocr_corrections": [{"source_line": 310, "ocr_note_number": 8, "print_note_number": 3}]})
add_statement("st-chp10-p320-323-n03-fisch-bergin-vico-citation", "cand-9740", "cand-9955", "also_cites_fisch_and_bergin_for_vico_autobiography",
              310, 320, 53, "Haskell also directs readers to Fisch and Bergin, pages 183–184, in the note attached to Vico's Autobiography.",
              "The note does not state which detail is covered by this reference; the cited pages and the authors' identities were not independently checked.",
              ["cand-9740", "cand-9953", "cand-9954", "cand-9955"],
              ["st-chp10-p320-vico-autobiography-first-published-in-venice"], 3,
              extra={"citations": [{"source_candidate_id": "cand-9955", "author_candidate_ids": ["cand-9953", "cand-9954"], "pages": "183–184"}]})
add_statement("st-chp10-p320-323-n01-ortes-letter-temanza-citation", "cand-1411", "cand-9956", "cites_ortes_letter_and_temanza_for_lodoli_account",
              311, 321, 54, "Haskell cites an Abate Ortes letter to Francesco Algarotti dated 26 September 1749, published in Algarotti volume XIV page 315, and also Temanza page 87.",
              "The letter and cited pages were not independently consulted; the note does not specify which subclaim each citation supports.",
              ["cand-1411", "cand-1789", "cand-0048", "cand-9956", "cand-2546", "cand-9957"],
              ["st-chp10-p321-critics-regarded-lodoli-as-impudent-impostor"], 1,
              extra={"citations": [{"source_candidate_id": "cand-9956", "author_candidate_id": "cand-1789", "recipient_candidate_id": "cand-0048", "date": "1749-09-26", "publication": "Algarotti XIV, p.315"}, {"source_candidate_id": "cand-9957", "author_candidate_id": "cand-2546", "page": "87"}]})
add_statement("st-chp10-p320-323-n02-moschini-monastery-citation", "cand-1411", "cand-9958", "cites_moschini_for_monastery_modifications",
              312, 321, 54, "Haskell cites G. A. Moschini, 1815, volume I, page 48, for Lodoli's monastery modifications.",
              "The printed citation reads 'G. A. Moschini, 1815, I, p. 48'; the OCR spacing and volume marker differ. Moschini's cited page was not independently consulted.",
              ["cand-1411", "cand-1709", "cand-9958"],
              ["st-chp10-p321-lodoli-modified-order-monastery-on-one-occasion"], 2,
              extra={"citations": [{"source_candidate_id": "cand-9958", "author_candidate_id": "cand-1709", "year": "1815", "volume": "I", "page": "48"}], "ocr_corrections": [{"source_line": 312, "ocr": "G. AMoschini, 1815,1", "print": "G. A. Moschini, 1815, I"}]})
add_statement("st-chp10-p320-323-n03-gozzi-dialogo-citation", "cand-1220", "cand-9959", "cites_gozzi_dialogue_for_ornament_criticism",
              313, 321, 54, "Haskell cites Gozzi, volume I page 26, Dialogo tra un librajo e un Forestiere, for the reported comment on building ornament.",
              "The dialogue was not independently consulted; the note's abbreviated punctuation is retained.",
              ["cand-1220", "cand-9959"],
              ["st-chp10-p321-gozzi-quoted-on-building-for-passers-by"], 3,
              extra={"citations": [{"source_candidate_id": "cand-9959", "author_candidate_id": "cand-1220", "volume": "I", "page": "26"}]})
add_statement("st-chp10-p320-323-n01-kauffmann-algarotti-lodoli-citation", "cand-0048", "cand-9961", "cites_kauffmann_for_algarotti_reactions_to_lodoli",
              314, 322, 55, "Haskell directs readers to Kauffmann, 1944 and 1955, for Algarotti's reactions to Lodoli.",
              "The note does not give titles or pages; neither work was independently consulted.",
              ["cand-0048", "cand-1411", "cand-9960", "cand-9961"],
              ["st-chp10-p321-lodoli-originally-welcomed-algarotti-interest-fragment"], 1,
              extra={"citations": [{"source_candidate_id": "cand-9961", "author_candidate_id": "cand-9960", "years": ["1944", "1955"]}]})
add_statement("st-chp10-p320-323-n02-correr-manuscript-sonnet-citation", "cand-9759", "cand-9962", "gives_correr_manuscript_locator_for_satirical_sonnet",
              315, 322, 55, "Haskell gives a Biblioteca Correr manuscript locator, Misc. XI/1348 (1140), in the note attached to the sonnet about Lodoli and Algarotti.",
              "The print reads 'MSS. Correr'; S0 OCR gives 'MSS. Cotter'. The manuscript was not consulted, and its catalog identity is not inferred.",
              ["cand-9759", "cand-8262", "cand-9962"],
              ["st-chp10-p322-sonnet-satirised-lodoli-and-algarotti"], 2,
              extra={"citations": [{"source_candidate_id": "cand-9962", "repository_candidate_id": "cand-8262", "locator": "Misc. XI/1348 (1140)"}], "ocr_corrections": [{"source_line": 315, "ocr": "Cotter", "print": "Correr"}]})
add_statement("st-chp10-p320-323-n03-previtali-gallery-citation", "cand-1411", "cand-9509", "cites_previtali_for_lodoli_gallery_account",
              316, 322, 55, "Haskell cites Previtali for the account of Lodoli's didactic gallery.",
              "The note gives no title or page. The matching short-form citation candidate is reused, but its exact work and the author's identity remain unresolved.",
              ["cand-1411", "cand-9508", "cand-9509", "cand-9181"],
              ["st-chp10-p322-lodoli-gallery-didactic-art-history-sequence"], 3,
              extra={"citations": [{"source_candidate_id": "cand-9509", "author_candidate_id": "cand-9508"}]})
add_statement("st-chp10-p320-323-n04-portrait-location-accademia", "cand-1424", "cand-1425", "portrait_location_reported_as_accademia_in_venice",
              317, 322, 55, "Haskell's note says the Alessandro Longhi portrait of Lodoli is in an Accademia in Venice.",
              "The exact Accademia is not named. The List of Plates captions Plate 48c as Museo Correr, Venice; this source-level location conflict remains unresolved, and the index portrait candidate is not merged with the front-matter caption candidate.",
              ["cand-1424", "cand-1425", "cand-9963", "cand-3998", "cand-3661", "cand-2719"],
              ["st-chp10-p322-lodoli-knew-longhi-who-painted-plate48c-portrait"], 4, True,
              {"source_conflict": {"note_claim": {"candidate_id": "cand-1425", "location_candidate_id": "cand-9963", "source_line": 317, "reading": "Accademia in Venice"}, "plate_caption": {"candidate_id": "cand-3998", "location_candidate_id": "cand-3661", "source_file": "02-sources/02-Markdown/00_05_List_of_Plates.md", "source_line": 126, "reading": "Museo Correr, Venice"}, "resolution": "unresolved"}, "ocr_corrections": [{"source_line": 317, "ocr": "Tlie portrait", "print": "The portrait"}, {"source_line": 317, "ocr": "Alessandro Longbi", "print": "Alessandro Longhi"}]})
add_statement("st-chp10-p320-323-n04-memmo-riflessioni-portrait-history", "cand-1425", "cand-9964", "cites_memmo_riflessioni_for_portrait_history",
              317, 322, 55, "Haskell directs readers to [Memmo], Riflessioni, 1788, for the portrait's history.",
              "The cited work was not independently consulted; the note's separate location statement is retained as a source conflict with the List of Plates.",
              ["cand-1425", "cand-1647", "cand-9964"],
              ["st-chp10-p322-lodoli-knew-longhi-who-painted-plate48c-portrait"], 4,
              extra={"citations": [{"source_candidate_id": "cand-9964", "author_candidate_id": "cand-1647", "work": "Riflessioni", "year": "1788"}]})
add_statement("st-chp10-p320-323-n01-goldoni-opere-longhi-praise", "cand-1206", "cand-1429", "cites_goldoni_opere_xiii_for_1750_longhi_praise",
              318, 323, 56, "Haskell cites Goldoni's Al Signor Pietro Longhi veneziano celebre pittore in Opere, volume XIII page 187, for Goldoni's 1750 praise of Longhi.",
              "Goldoni's cited text was not independently consulted; the note's title and locator are preserved as printed.",
              ["cand-1206", "cand-1429", "cand-9965"],
              ["st-chp10-p323-goldoni-hails-longhi-seeker-of-truth-1750"], 1,
              extra={"citations": [{"source_candidate_id": "cand-9965", "author_candidate_id": "cand-1206", "work_title": "Al Signor Pietro Longhi veneziano celebre pittore", "series": "Opere", "volume": "XIII", "page": "187"}]})
add_statement("st-chp10-p320-323-n02-goldoni-frappatore-longhi-praise", "cand-1206", "cand-1429", "cites_goldoni_dedication_for_1757_longhi_praise",
              319, 323, 56, "Haskell cites Goldoni, volume II page 92, the dedication of Il Frappatore, for Goldoni's later praise of Longhi.",
              "The dedication was not independently consulted; the source's 'seven years later' remains the body's relative chronology.",
              ["cand-1206", "cand-1429", "cand-9966"],
              ["st-chp10-p323-goldoni-praises-longhi-representation-1757"], 2,
              extra={"citations": [{"source_candidate_id": "cand-9966", "author_candidate_id": "cand-1206", "volume": "II", "page": "92", "dedication_of": "Il Frappatore"}]})
add_statement("st-chp10-p320-323-n03-dazzi-goldoni-sympathies-citation", "cand-1206", "cand-9968", "cites_dazzi_for_goldoni_sympathies_comment",
              320, 323, 56, "Haskell cites Dazzi in the note attached to the inference that Goldoni's sympathies were advanced.",
              "The note supplies only the surname; no title, page, or detailed claim is inferred.",
              ["cand-1206", "cand-9967", "cand-9968"],
              ["st-chp10-p323-goldoni-sympathies-advanced-by-implication"], 3,
              extra={"citations": [{"source_candidate_id": "cand-9968", "author_candidate_id": "cand-9967"}]})
add_statement("st-chp10-p320-323-n04-gennari-letter-goldoni-allusion", "cand-1206", "cand-9969", "cites_gennari_letter_for_goldoni_allusion",
              321, 323, 56, "Haskell says Goldoni is not named in the passage but the allusion is clear in Giuseppe Gennari's letter to Gaspare Patriarchi dated 5 November 1761, published by Melchiori at page 142.",
              "The letter and Melchiori publication were not independently consulted; Haskell's 'the allusion is clear' remains his interpretation.",
              ["cand-1206", "cand-1130", "cand-9970", "cand-9969", "cand-9971", "cand-9972"],
              ["st-chp10-p323-goldoni-sympathies-advanced-by-implication"], 4,
              extra={"citations": [{"source_candidate_id": "cand-9969", "sender_candidate_id": "cand-1130", "recipient_candidate_id": "cand-9970", "date": "1761-11-05", "publication_candidate_id": "cand-9972", "editor_candidate_id": "cand-9971", "page": "142"}]})
add_statement("st-chp10-p320-323-n05-paoletti-source-and-caution", "cand-9774", "cand-9974", "cites_paoletti_for_unsupported_longhi_punishment_story",
              322, 323, 56, "Haskell cites [Paoletti], 1832, page 122, says there is no evidence for the alleged punishment in the Archives of the Inquisitors, and continues in the same printed note that Paoletti misnames the artist 'Antonio' Longhi and does not seem wholly reliable.",
              "The footnote's printed continuation is transcribed in body-segment line 192 and linked to this note. The unnamed historian in the body is not separately identity-matched to Paoletti; Haskell explicitly marks the claim unsupported.",
              ["cand-9774", "cand-1429", "cand-9973", "cand-9974", "cand-9975"],
              ["st-chp10-p323-historian-claim-longhi-punished-for-depicting-truth", "st-chp10-p323-note5-paoletti-misnaming-and-reliability"], 5,
              extra={"citations": [{"source_candidate_id": "cand-9974", "author_candidate_id": "cand-9973", "year": "1832", "page": "122"}], "repository_candidate_id": "cand-9975", "continuation_in_body_statement_id": "st-chp10-p323-note5-paoletti-misnaming-and-reliability", "ocr_corrections": [{"source_line": 322, "ocr_note_number": 6, "print_note_number": 5}]})
add_statement("st-chp10-p320-323-n06-visconti-letter-via-crucis-report", "cand-9772", "cand-8466", "cites_visconti_letter_for_reported_via_crucis_criticism",
              323, 323, 56, "Haskell cites Pietro Visconti's letter to Gian Pietro Ligari of 19 December 1749, published by Arslan in 1952 at page 63, in the note attached to the costume criticism of Tiepolo's Via Crucis series.",
              "The letter and cited publication were not independently consulted; the citation is not treated as independent verification of the reported criticism.",
              ["cand-9772", "cand-8465", "cand-1408", "cand-8466", "cand-8467"],
              ["st-chp10-p323-tiepolo-via-crucis-criticized-for-costumes"], 6,
              extra={"citations": [{"source_candidate_id": "cand-8466", "author_candidate_id": "cand-8467", "sender_candidate_id": "cand-8465", "recipient_candidate_id": "cand-1408", "date": "1749-12-19", "publication_year": "1952", "page": "63"}], "ocr_corrections": [{"source_line": 323, "ocr": "Letter horn", "print": "Letter from"}]})
add_statement("st-chp10-p320-323-n07-gazzetta-veneta-issue-longhi-comparison", "cand-1220", "cand-9976", "cites_gazzetta_issue_for_august_1760_longhi_comparison",
              324, 323, 56, "Haskell cites Gazzetta Veneta, issue no. 55, 13 August 1760, for the account of Gozzi's comparison of Longhi and Tiepolo.",
              "S0 OCR gives issue 35; the printed note reads 55. The issue was not independently consulted, and the exact article title or page is not supplied.",
              ["cand-1220", "cand-1429", "cand-2569", "cand-8729", "cand-9976"],
              ["st-chp10-p323-gozzi-compares-longhi-and-tiepolo"], 7,
              extra={"citations": [{"source_candidate_id": "cand-9976", "periodical_candidate_id": "cand-8729", "issue": "55", "date": "1760-08-13"}], "ocr_corrections": [{"source_line": 324, "ocr": "No. 35", "print": "No. 55"}]})

all_statements = statements + new_statements
statement_by_id = {row["statement_id"]: row for row in all_statements}


def add_footnote_ref(body_id, marker, line, note_ids):
    row = statement_by_id.get(body_id)
    if not row:
        raise SystemExit(f"body statement missing: {body_id}")
    q = row["qualifiers"]
    if "footnote_marker" in q:
        if q["footnote_marker"] != marker or q.get("pending_note_source_line") != line:
            raise SystemExit(f"unexpected pending note marker/line: {body_id}")
    else:
        refs = q.get("cross_reference_segments", [])
        if not any(ref.get("segment_id") == NOTES and ref.get("source_line_start") == line for ref in refs):
            raise SystemExit(f"expected p.323 note cross-reference not found: {body_id}")
        q["footnote_marker"] = marker
        q["pending_note_source_line"] = line
    q["footnote_text_pending"] = False
    q["footnote_segment"] = NOTES
    ref = {"marker": marker, "segment_id": NOTES, "source_line": line}
    refs = q.setdefault("footnote_refs", [])
    if ref not in refs:
        refs.append(ref)
    ids = q.setdefault("footnote_statement_ids", [])
    for sid in note_ids:
        if sid not in statement_by_id:
            raise SystemExit(f"note statement missing: {sid}")
        if sid not in ids:
            ids.append(sid)
    q["footnote_body_link_status"] = "linked"


add_footnote_ref("st-chp10-p320-zanetti-announced-colour-woodcut-process-to-conti", 1, 308,
                 ["st-chp10-p320-323-n01-lorenzetti-citation"])
add_footnote_ref("st-chp10-p320-lodoli-brother-of-minori-osservanti", 2, 309,
                 ["st-chp10-p320-323-n02-memmo-elementi-lodoli-life"])
add_footnote_ref("st-chp10-p320-vico-autobiography-first-published-in-venice", 3, 310,
                 ["st-chp10-p320-323-n03-calogera-raccolta-vico-autobiography", "st-chp10-p320-323-n03-fisch-bergin-vico-citation"])
add_footnote_ref("st-chp10-p321-critics-regarded-lodoli-as-impudent-impostor", 1, 311,
                 ["st-chp10-p320-323-n01-ortes-letter-temanza-citation"])
add_footnote_ref("st-chp10-p321-lodoli-modified-order-monastery-on-one-occasion", 2, 312,
                 ["st-chp10-p320-323-n02-moschini-monastery-citation"])
add_footnote_ref("st-chp10-p321-gozzi-quoted-on-building-for-passers-by", 3, 313,
                 ["st-chp10-p320-323-n03-gozzi-dialogo-citation"])
add_footnote_ref("st-chp10-p321-lodoli-originally-welcomed-algarotti-interest-fragment", 1, 314,
                 ["st-chp10-p320-323-n01-kauffmann-algarotti-lodoli-citation"])
add_footnote_ref("st-chp10-p322-sonnet-satirised-lodoli-and-algarotti", 2, 315,
                 ["st-chp10-p320-323-n02-correr-manuscript-sonnet-citation"])
add_footnote_ref("st-chp10-p322-lodoli-gallery-didactic-art-history-sequence", 3, 316,
                 ["st-chp10-p320-323-n03-previtali-gallery-citation"])
add_footnote_ref("st-chp10-p322-lodoli-knew-longhi-who-painted-plate48c-portrait", 4, 317,
                 ["st-chp10-p320-323-n04-portrait-location-accademia", "st-chp10-p320-323-n04-memmo-riflessioni-portrait-history"])
add_footnote_ref("st-chp10-p323-goldoni-hails-longhi-seeker-of-truth-1750", 1, 318,
                 ["st-chp10-p320-323-n01-goldoni-opere-longhi-praise"])
add_footnote_ref("st-chp10-p323-goldoni-praises-longhi-representation-1757", 2, 319,
                 ["st-chp10-p320-323-n02-goldoni-frappatore-longhi-praise"])
add_footnote_ref("st-chp10-p323-goldoni-sympathies-advanced-by-implication", 3, 320,
                 ["st-chp10-p320-323-n03-dazzi-goldoni-sympathies-citation"])
add_footnote_ref("st-chp10-p323-opponents-accuse-goldoni", 4, 321,
                 ["st-chp10-p320-323-n04-gennari-letter-goldoni-allusion"])
add_footnote_ref("st-chp10-p323-historian-claim-longhi-punished-for-depicting-truth", 5, 322,
                 ["st-chp10-p320-323-n05-paoletti-source-and-caution"])
add_footnote_ref("st-chp10-p323-note5-paoletti-misnaming-and-reliability", 5, 322,
                 ["st-chp10-p320-323-n05-paoletti-source-and-caution"])
add_footnote_ref("st-chp10-p323-tiepolo-via-crucis-criticized-for-costumes", 6, 323,
                 ["st-chp10-p320-323-n06-visconti-letter-via-crucis-report"])
add_footnote_ref("st-chp10-p323-gozzi-compares-longhi-and-tiepolo", 7, 324,
                 ["st-chp10-p320-323-n07-gazzetta-veneta-issue-longhi-comparison"])

body_note5 = statement_by_id["st-chp10-p323-historian-claim-longhi-punished-for-depicting-truth"]
body_note5["qualifiers"]["qualification"] = (
    "This is a reported claim expressly marked as unsupported. Footnote 5 cites [Paoletti], says there is no evidence in the Archives of the Inquisitors, "
    "and continues in body-segment line 192 that Paoletti calls the artist ‘Antonio’ Longhi and does not seem wholly reliable. The unnamed body historian "
    "is not identity-matched to Paoletti. The note is now linked to its citation statement."
)
tail_candidate = candidate_by_id["cand-9774"]
tail_candidate["detail"] = (
    "Haskell reports an unnamed historian's claim that Longhi was punished for depicting truth. The body does not name the historian; footnote 5 cites "
    "Paoletti, 1832, page 122, and qualifies the source as unsupported and not wholly reliable. Identity between the unnamed historian and Paoletti remains unresolved."
)
memmo_candidate = candidate_by_id["cand-8812"]
memmo_candidate["canonical_name"] = "Andrea Memmo, Elementi dell’architettura lodoliana (Rome, 1786; citation locator)"
memmo_candidate["detail"] = (
    "P.320 note 2 identifies the previously title-pending 1786 Memmo citations in p.272 note 6 and p.309 note 2 as Elementi dell’architettura lodoliana. "
    "The note gives pages 4 ff. and 1 in those earlier citations; the work was not independently consulted."
)

portrait_statement = statement_by_id["st-chp10-p322-lodoli-knew-longhi-who-painted-plate48c-portrait"]
portrait_q = portrait_statement["qualifiers"]
portrait_q["source_conflict"] = {
    "note_claim": {"portrait_candidate_id": "cand-1425", "location_candidate_id": "cand-9963", "source_line": 317, "reading": "Accademia in Venice"},
    "plate_caption": {"portrait_candidate_id": "cand-3998", "location_candidate_id": "cand-3661", "source_file": "02-sources/02-Markdown/00_05_List_of_Plates.md", "source_line": 126, "reading": "Museo Correr, Venice"},
    "resolution": "unresolved",
}

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
    if row["subject_candidate_id"] and row["subject_candidate_id"] not in candidate_id_set:
        raise SystemExit(f"missing statement subject: {row['statement_id']}")
    if row["object_candidate_id"] and row["object_candidate_id"] not in candidate_id_set:
        raise SystemExit(f"missing statement object: {row['statement_id']}")
    if any(cid not in candidate_id_set for cid in row["qualifiers"]["mentioned_candidate_ids"]):
        raise SystemExit(f"missing statement mention foreign key: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in new_mentions)
for left, right in zip(spans, spans[1:]):
    if left[1] > right[0]:
        raise SystemExit(f"overlapping p.320–323 note mention spans: {left[2]} and {right[2]}")

body_updates = {
    body_segments["p320"]: ("L152-163; notes L308-310", "Printed p.320 body reviewed; notes L308–310 migrated and linked."),
    body_segments["p321"]: ("L166-173; notes L311-314", "Printed p.321 body reviewed; notes L311–313 plus the p.322 note at L314 migrated and linked."),
    body_segments["p322"]: ("L176-184; notes L314-317", "Printed p.322 body reviewed; notes L314–317 migrated and linked. The p.322 footnote location conflicts with the Plate 48c caption and remains unresolved."),
    body_segments["p323"]: ("L186-192; notes L318-324", "Printed p.323 body reviewed; notes L318–324 migrated and linked. Note 5 continues across canonical S0 locations L322 and L192; issue no. 55 is confirmed from print."),
}
for segment, (ranges, note) in body_updates.items():
    coverage[segment].update({"migration_status": "complete", "source_line_ranges": ranges, "note": note})
coverage[NOTES].update({
    "migration_status": "complete",
    "source_line_ranges": "L274-349",
    "note": "The consolidated footnote segment L274–349 is fully reviewed and linked. L308–324 (printed p.320–323 notes) was compared with CHP-10.pdf physical pages 53–56; p.323 note 5 continuation at canonical L192 is linked to L322.",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_statements.sort(key=lambda row: row["statement_id"])
print(f"p.320–323 note preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage changes: p.320–323 body partials -> complete; consolidated notes L274–349 -> complete")
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
