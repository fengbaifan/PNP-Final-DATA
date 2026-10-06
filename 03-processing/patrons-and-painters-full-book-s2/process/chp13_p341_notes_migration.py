"""Controlled S2 migration for the four printed p.341 notes; dry-run by default."""
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
BODY = "chp-13:13_CHP-13_intro:l90-96"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
PLATE = "chp-13:13_CHP-13_intro_plates_visual-transcription:l5-7"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p341-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.341 note migration")
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
expected_note_fragments = {
    223: "See especially G. Lorenzetti, 1917, and F. Borroni.",
    224: "Marco Ricci, who painted six pictures for Zanetti",
    225: "Mariette wrote a charming account of Zanetti in his Ahecedario",
    226: "Biblioteca Marciana, Venice—MSS. Italiani—Cl. XI, Cod. CXVI, 7356.",
}
for line_number, fragment in expected_note_fragments.items():
    if fragment not in source_lines[line_number - 1]:
        raise SystemExit(f"source line L{line_number} changed")

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

table_state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if table_state != (10178, 10191, 22018, 9836):
    raise SystemExit(f"unexpected table pre-state: {table_state}")
for segment_id in (BODY, NOTES, PLATE):
    if segment_id not in coverage:
        raise SystemExit(f"required coverage row missing: {segment_id}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.341 body is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated chapter 13 notes are not reviewed/partial")
if coverage[NOTES]["source_line_ranges"] != "L180-222":
    raise SystemExit("consolidated-notes cursor changed")
if (coverage[PLATE]["disposition"], coverage[PLATE]["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("Plate 58a visual segment is not reviewed/complete")
if any(row["segment_id"] == NOTES and row["mention_id"].startswith("m-s2-ch13-p341-notes-") for row in mentions):
    raise SystemExit("p.341 note mentions already exist")
if any(row["segment_id"] == NOTES and row["statement_id"].startswith("st-chp13-p341-notes-") for row in statements):
    raise SystemExit("p.341 note statements already exist")

body_footnote_targets = {
    "1": ["st-chp13-p341-zanetti_portrait_reference_and_authorial_interest"],
    "2": ["st-chp13-p341-zanetti_friendship_with_marco_ricci"],
    "3": ["st-chp13-p341-zanetti_met_and_corresponded_with_mariette"],
    "4": [
        "st-chp13-p341-zanetti_1736_acquisitions_from_eugene_heirs",
        "st-chp13-p341-crespi_pastoral_praised",
    ],
}
for marker, ids in body_footnote_targets.items():
    for statement_id in ids:
        if statement_id not in statement_by_id:
            raise SystemExit(f"p.341 footnote {marker} target missing: {statement_id}")
        refs = statement_by_id[statement_id].get("qualifiers", {}).get("footnote_refs", [])
        if not any(ref.get("footnote_marker") == marker and ref.get("footnote_printed_page") == 341 and ref.get("footnote_text_pending") for ref in refs):
            raise SystemExit(f"p.341 footnote {marker} is not pending on {statement_id}")

# The visual transcription and caption statements already resolve the p.341 pointer.
plate_pointer = next((r for r in mentions if r["segment_id"] == BODY and r["surface_form"] == "Plate 58a"), None)
if not plate_pointer or plate_pointer["candidate_id"] != "cand-4048":
    raise SystemExit("p.341 Plate 58a mention is not mapped to the existing portrait work")
if candidate_by_id.get("cand-10059", {}).get("status") != "excluded":
    raise SystemExit("obsolete provisional Plate 58a candidate is not excluded")
for statement_id in ("st-chp13-plates58a-zocchi-attribution", "st-chp13-plates58a-depicts-zanetti", "st-chp13-plates58a-depicts-gerini"):
    if statement_id not in statement_by_id or statement_by_id[statement_id]["segment_id"] != PLATE:
        raise SystemExit(f"Plate 58a caption evidence missing: {statement_id}")

new_ids = {f"cand-{number}" for number in range(10192, 10205)}
if new_ids & set(candidate_by_id):
    raise SystemExit(f"candidate IDs already exist: {sorted(new_ids & set(candidate_by_id))}")
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
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
    })
    new_candidates.append(row)


candidate_specs = [
    ("cand-10192", "G. Lorenzetti, 1917 (citation in p.341 notes 1-3; title unresolved)", "archive",
     "Short-form citation used in notes L223-L225; note 2 cites p.138 and note 3 p.145. No title or edition is supplied here and the cited work has not been independently consulted. Keep distinct from similarly abbreviated citations pending global S3 alignment.", 223),
    ("cand-10193", "F. Borroni (short bibliographic reference; title and date unspecified)", "archive",
     "Named as a further reference in p.341 note 1. The citation supplies no title, date, publisher, or page; the underlying work has not been identified or consulted.", 223),
    ("cand-10194", "Six pictures painted by Marco Ricci for A. M. Zanetti (titles unspecified)", "work",
     "P.341 note 2 says Ricci painted six pictures for Zanetti. It does not identify their subjects or titles. Keep distinct from the six landscapes described elsewhere until S3 resolves whether the two passages refer to the same group.", 224),
    ("cand-10195", "Federico Correr (patron named in p.341 note 2; identity pending)", "person",
     "Named as an example of another patron for whom Zanetti helped Marco Ricci obtain commissions. No further identity details are supplied in this note.", 224),
    ("cand-10196", "Pierre-Jean Mariette's Abecedario (account of Zanetti)", "archive",
     "The printed note calls this Mariette's Abecedario and says it contains an account of Zanetti. No volume, page, edition, or manuscript locator is supplied here; source not independently consulted.", 225),
    ("cand-10197", "Unidentified pastel by Rosalba Carriera left to Mariette in Zanetti's will", "work",
     "P.341 note 3 reports a pastel by Rosalba left to the French connoisseur Pierre-Jean Mariette in Zanetti's will. The pastel has no title or further identifying details.", 225),
    ("cand-10198", "A. M. Zanetti's will (cited through Lorenzetti, 1917, p.145)", "archive",
     "Testamentary document cited in p.341 note 3 as recording a bequest of a Rosalba pastel to Mariette. No archival locator is supplied and the will has not been consulted.", 225),
    ("cand-10199", "Biblioteca Marciana, MSS. Italiani, Cl. XI, Cod. CXVI, 7356", "archive",
     "Manuscript volume identified in p.341 note 4 as belonging to A. M. Zanetti and containing his notes and correspondence. The shelfmark is transcribed from the printed note; the manuscript/catalogue record has not been consulted.", 226),
    ("cand-10200", "Receipt signed by Anne Marie de Savoye in Vienna, 10 August 1736", "archive",
     "Receipt described in p.341 note 4 within the cited Zanetti manuscript volume. It records a sale to Zanetti; the note does not identify the seller or establish that the signatory was the seller. Receipt not independently consulted.", 226),
    ("cand-10201", "Zanetti's Memorie de gl'acquisti fatti da me ... l'Anno 1736", "archive",
     "Memorie named in p.341 note 4 as mentioning the Castiglione but not the Poussin and describing a small copper pastoral picture. The note does not give a separate shelfmark; do not assume it is a separate volume from Cod. CXVI, 7356.", 226),
    ("cand-10202", "Unidentified Prince of Liechtenstein corresponding with A. M. Zanetti", "person",
     "A correspondent named in p.341 note 4. The title alone does not establish identity with the Prince of Liechtenstein mentioned elsewhere in the book; defer comparison to S3.", 226),
    ("cand-10203", "The 'Spagnolo di Bologna' named in Zanetti's Memorie (identity unresolved)", "person",
     "Painter referred to by this epithet in the Memorie's description of a small copper pastoral picture. The note does not name the artist; do not identify the epithet with Crespi here.", 226),
    ("cand-10204", "Fifteen gems and cameos recorded in the 1736 receipt (individual items unidentified)", "",
     "P.341 note 4 says the receipt also records fifteen gems and cameos sold to Zanetti. Their individual identities and the appropriate entity type are not established; preserve as a type-pending aggregate, not fifteen fabricated objects.", 226),
]
for spec in candidate_specs:
    add_candidate(*spec)
all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}

notes_text = "\n".join(source_lines[178:251])
line_offsets = {}
offset = 0
for line_number in range(179, 252):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

new_mentions = []
existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}


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
    key = (NOTES, candidate_id, str(start), str(end))
    if key in existing_mention_keys or any(
        (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"])) == key
        for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention at L{line_number}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p341-notes-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": note,
    })
    new_mentions.append(row)


mention_specs = [
    (223, "G. Lorenzetti, 1917", "cand-10192", "Short-form source citation; cited work not consulted."),
    (223, "Lorenzetti", "cand-9947", "Surname-only cited author; reuse current author candidate, identity remains for S3."),
    (223, "F. Borroni", "cand-10193", "Short bibliographic reference; title/date not supplied."),
    (224, "Marco Ricci", "cand-2149"),
    (224, "six pictures for Zanetti", "cand-10194", "The note gives a count and patron but no titles; distinguish from the six landscapes elsewhere pending S3."),
    (224, "Zanetti", "cand-2838"),
    (224, "Bottari, II, pp. 128-30", "cand-7516", "Reuse the cited Bottari volume II candidate; these pages have not been consulted."),
    (224, "Bottari", "cand-0417", "Cited author; reuse existing person candidate."),
    (224, "Zanetti helped to get Marco Ricci commissions from other patrons such as Federico Correr", "cand-2838", "The note reports intermediary help; the named commission details are not independently verified."),
    (224, "Marco Ricci", "cand-2149", "Second occurrence in the commission claim.", 1),
    (224, "Federico Correr", "cand-10195", "Named as an example of another patron; identity pending S3."),
    (224, "Lorenzetti, 1917, p. 138", "cand-10192", "Short-form citation locator; cited page not consulted."),
    (224, "Lorenzetti", "cand-9947", "Surname-only cited author; second occurrence."),
    (225, "Mariette", "cand-1547"),
    (225, "Ahecedario", "cand-10196", "S0 OCR reads Ahecedario; the print reads Abecedario. Correction is recorded in S2 only."),
    (225, "Zanetti", "cand-2838"),
    (225, "his will", "cand-10198", "The will is named as the source of a bequest; no archival locator is given."),
    (225, "the French connoisseur", "cand-1547", "Appositional reference to Mariette."),
    (225, "a pastel by Rosalba", "cand-10197", "Unidentified work; the printed note supplies only the artist's first name."),
    (225, "Rosalba", "cand-0581"),
    (225, "Lorenzetti, 1917, p. 145", "cand-10192", "Short-form citation locator; cited page not consulted."),
    (225, "Lorenzetti", "cand-9947", "Surname-only cited author; third occurrence."),
    (226, "Biblioteca Marciana, Venice—MSS. Italiani—Cl. XI, Cod. CXVI, 7356", "cand-10199", "Printed manuscript repository and shelfmark; not checked against the catalogue."),
    (226, "Biblioteca Marciana", "cand-9448", "Repository named in the printed locator; no current catalogue verification implied."),
    (226, "Venice", "cand-2719", "Repository location as printed."),
    (226, "A. M. Zanetti", "cand-2838", "The volume is described as belonging to Zanetti."),
    (226, "the Prince of Liechtenstein", "cand-10202", "Correspondent named only by title; keep distinct from other Liechtenstein candidates pending S3."),
    (226, "Count Tessin", "cand-2554"),
    (226, "Marshal Schulenburg", "cand-2401"),
    (226, "A receipt, dated 10 August 1736 in Vienna, signed Anne Marie de Savoye", "cand-10200", "A receipt described by Haskell in the note; original document not consulted."),
    (226, "Vienna", "cand-2772", "Location of the receipt as printed."),
    (226, "Anne Marie de Savoye", "cand-2381", "Reuse index candidate; the note identifies the signatory, not necessarily the seller."),
    (226, "un Poussin representant un Miracle des Apôtres", "cand-10069", "Work description within the receipt quotation; title and identity remain unresolved."),
    (226, "L’autre de Castiglione Benedetto avec des animaux et figures", "cand-10070", "Work description within the receipt quotation; title and identity remain unresolved."),
    (226, "fifteen gems and cameos", "cand-10204", "Aggregate named in the receipt; individual objects and type remain unresolved."),
    (226, "sold to Zanetti", "cand-2838", "The printed note reports the recipient; it does not name the seller."),
    (226, "Memorie de gl’acquisti fatti da me Antonio Mra Zanetti q Girolamo in Vienna dall’ Heredita del Pncipe Eugenio di Savoia, l’Anno 1736", "cand-10201", "Short title/description as printed in S0, retaining its abbreviated forms and OCR spelling; no separate shelfmark supplied."),
    (226, "Antonio Mra Zanetti q Girolamo", "cand-2838", "Name as printed in the cited Memorie title; do not expand the abbreviations."),
    (226, "dall’ Heredita del Pncipe Eugenio di Savoia", "cand-10068", "Inheritance phrase in the title; S2 print check corrects Pncipe to Principe."),
    (226, "Pncipe Eugenio di Savoia", "cand-2384", "S0 OCR loses letters; print reads Principe Eugenio di Savoia. Correction is recorded in S2 only."),
    (226, "the Castiglione", "cand-10070", "The note says the Memorie mentions this picture."),
    (226, "the Poussin", "cand-10069", "The note explicitly says the Memorie does not mention this picture."),
    (226, "bellissimo Quadretto in rame", "cand-10203", "Unidentified copper picture described in the Memorie; the quoted epithet does not establish identity with Crespi's p.341 pastoral."),
    (226, "lo Spagnolo di Bologna", "cand-10203", "Painter named by epithet only; do not equate with Crespi without later alignment."),
]
for spec in mention_specs:
    add_mention(*spec)

new_statement_specs = [
    {
        "id": "st-chp13-p341-notes-note1-lorenzetti-borroni-references",
        "marker": "1", "line": 223, "subject": "cand-2838", "object": "cand-10192",
        "predicate": "note_cites_lorenzetti_1917_and_f_borroni_for_zanetti_context",
        "claim": "Printed p.341 note 1 directs the reader to G. Lorenzetti (1917) and F. Borroni.",
        "qualification": "The note supplies short references only. Borroni's title and date are absent; neither cited work was independently consulted.",
        "mentioned": ["cand-2838", "cand-9947", "cand-10192", "cand-10193"],
        "citations": [
            {"source_candidate_id": "cand-10192", "author_candidate_id": "cand-9947", "year": "1917"},
            {"source_candidate_id": "cand-10193", "author_as_printed": "F. Borroni"},
        ],
        "linked": body_footnote_targets["1"],
    },
    {
        "id": "st-chp13-p341-notes-note2-ricci-painted-six-pictures-for-zanetti",
        "marker": "2", "line": 224, "subject": "cand-2149", "object": "cand-10194",
        "predicate": "painted_six_unnamed_pictures_for_zanetti",
        "claim": "The note says Marco Ricci painted six pictures for Zanetti.",
        "qualification": "No titles or subjects are supplied here. Keep the group distinct from the six landscapes described elsewhere until global S3 alignment.",
        "mentioned": ["cand-2149", "cand-10194", "cand-2838", "cand-7516", "cand-0417"],
        "citations": [{"source_candidate_id": "cand-7516", "author_candidate_id": "cand-0417", "volume": "II", "pages": "128-130"}],
        "linked": body_footnote_targets["2"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p341-notes-note2-ricci-called-zanetti-mio-amico",
        "marker": "2", "line": 224, "subject": "cand-2149", "object": "cand-2838",
        "predicate": "wrote_of_zanetti_as_mio_amico_oltre_misura_in_1723",
        "claim": "The note reports that in 1723 Marco Ricci wrote of Zanetti as ‘mio amico oltre misura’.",
        "qualification": "Preserve the quoted wording and Haskell's attribution; the cited Bottari pages have not been consulted.",
        "mentioned": ["cand-2149", "cand-2838", "cand-7516", "cand-0417"],
        "citations": [{"source_candidate_id": "cand-7516", "author_candidate_id": "cand-0417", "volume": "II", "pages": "128-130"}],
        "linked": body_footnote_targets["2"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p341-notes-note2-zanetti-helped-ricci-obtain-commissions",
        "marker": "2", "line": 224, "subject": "cand-2838", "object": "cand-2149",
        "predicate": "helped_ricci_obtain_commissions_from_other_patrons_including_federico_correr",
        "claim": "The note says Zanetti helped Marco Ricci obtain commissions from other patrons, including Federico Correr.",
        "qualification": "A broker/intermediary role is reported; the commissions and relationship are not independently corroborated here.",
        "mentioned": ["cand-2838", "cand-2149", "cand-10195", "cand-10192", "cand-9947"],
        "citations": [{"source_candidate_id": "cand-10192", "author_candidate_id": "cand-9947", "year": "1917", "page": "138"}],
        "linked": body_footnote_targets["2"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p341-notes-note3-mariette-abecedario-account-of-zanetti",
        "marker": "3", "line": 225, "subject": "cand-1547", "object": "cand-10196",
        "predicate": "abecedario_contains_mariettes_account_of_zanetti",
        "claim": "The note calls it a charming account of Zanetti by Mariette in his Abecedario.",
        "qualification": "The print reads Abecedario; S0 OCR reads Ahecedario. No page, edition, or manuscript locator is supplied, and the work was not consulted.",
        "mentioned": ["cand-1547", "cand-10196", "cand-2838", "cand-10192", "cand-9947"],
        "citations": [{"source_candidate_id": "cand-10192", "author_candidate_id": "cand-9947", "year": "1917", "page": "145"}],
        "linked": body_footnote_targets["3"],
        "ocr_corrections": [{"source_line": 225, "ocr": "Ahecedario", "print": "Abecedario", "basis": "CHP-13.pdf physical page 10."}],
    },
    {
        "id": "st-chp13-p341-notes-note3-zanetti-left-pastel-to-mariette-in-will",
        "marker": "3", "line": 225, "subject": "cand-2838", "object": "cand-1547",
        "predicate": "left_unidentified_rosalba_pastel_to_mariette_in_his_will",
        "claim": "The note says Zanetti left Mariette a pastel by Rosalba in his will.",
        "qualification": "The pastel is untitled and identified only by Rosalba's first name; preserve the will as Haskell's cited evidence, not as independently consulted.",
        "mentioned": ["cand-2838", "cand-1547", "cand-10197", "cand-10198", "cand-0581", "cand-10192", "cand-9947"],
        "citations": [{"source_candidate_id": "cand-10192", "author_candidate_id": "cand-9947", "year": "1917", "page": "145"}],
        "linked": body_footnote_targets["3"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p341-notes-note4-zanetti-volume-and-correspondence",
        "marker": "4", "line": 226, "subject": "cand-2838", "object": "cand-10199",
        "predicate": "owned_manuscript_volume_containing_notes_and_letters_to_him",
        "claim": "The note describes Cod. CXVI, 7356 as a volume belonging to A. M. Zanetti and containing his notes and letters addressed to him.",
        "qualification": "This is Haskell's description of a cited manuscript. The codex and catalogue record were not independently inspected.",
        "mentioned": ["cand-2838", "cand-10199"],
        "citations": [{"source_candidate_id": "cand-10199", "repository_candidate_id": "cand-9448", "shelfmark_as_printed": "MSS. Italiani, Cl. XI, Cod. CXVI, 7356"}],
        "linked": body_footnote_targets["4"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p341-notes-note4-volume-locator-at-biblioteca-marciana",
        "marker": "4", "line": 226, "subject": "cand-10199", "object": "cand-9448",
        "predicate": "cited_repository_and_shelfmark",
        "claim": "The printed locator places the manuscript at Biblioteca Marciana, Venice, under MSS. Italiani, Cl. XI, Cod. CXVI, 7356.",
        "qualification": "Repository and shelfmark are transcribed from Haskell's note; current custody and catalogue metadata are not independently verified.",
        "mentioned": ["cand-10199", "cand-9448", "cand-2719"],
        "citations": [{"source_candidate_id": "cand-10199", "repository_candidate_id": "cand-9448", "place_candidate_id": "cand-2719"}],
        "linked": body_footnote_targets["4"],
    },
    {
        "id": "st-chp13-p341-notes-note4-zanetti-indexed-and-summarized-volume-letters",
        "marker": "4", "line": 226, "subject": "cand-2838", "object": "cand-10199",
        "predicate": "indexed_and_summarized_the_volume_letters_at_its_beginning",
        "claim": "The note says Zanetti himself indexed and summarized the letters at the beginning of the volume.",
        "qualification": "This is Haskell's description of the cited manuscript; the codex was not inspected.",
        "mentioned": ["cand-2838", "cand-10199"],
        "citations": [{"source_candidate_id": "cand-10199", "described_action_by_candidate_id": "cand-2838"}],
        "linked": body_footnote_targets["4"],
    },
    {
        "id": "st-chp13-p341-notes-note4-volume-correspondents",
        "marker": "4", "line": 226, "subject": "cand-10199", "object": "cand-2838",
        "predicate": "contains_letters_to_zanetti_from_named_correspondents",
        "claim": "The note says the volume includes letters to Zanetti, notably from the Prince of Liechtenstein, Count Tessin, and Marshal Schulenburg.",
        "qualification": "Correspondents are identified only by the names or titles printed in the note; the individual letters were not consulted.",
        "mentioned": ["cand-10199", "cand-2838", "cand-10202", "cand-2554", "cand-2401"],
        "citations": [{"source_candidate_id": "cand-10199", "correspondent_candidate_ids": ["cand-10202", "cand-2554", "cand-2401"]}],
        "linked": body_footnote_targets["4"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p341-notes-note4-receipt-date-place-signatory",
        "marker": "4", "line": 226, "subject": "cand-10200", "object": "cand-2381",
        "predicate": "receipt_dated_vienna_1736_08_10_and_signed_by_anne_marie_de_savoye",
        "claim": "The note describes a receipt dated 10 August 1736 in Vienna and signed by Anne Marie de Savoye.",
        "qualification": "The note identifies Anne Marie as signatory, not necessarily the seller; the receipt was not consulted.",
        "mentioned": ["cand-10200", "cand-2381", "cand-2772", "cand-10199"],
        "citations": [{"source_candidate_id": "cand-10200", "container_candidate_id": "cand-10199", "date": "1736-08-10", "place_candidate_id": "cand-2772"}],
        "linked": body_footnote_targets["4"], "relation_candidate": True,
        "ocr_corrections": [{"source_line": 226, "ocr": "Pncipe", "print": "Principe", "basis": "CHP-13.pdf physical page 10."}],
    },
    {
        "id": "st-chp13-p341-notes-note4-receipt-records-items-sold-to-zanetti",
        "marker": "4", "line": 226, "subject": "cand-10200", "object": "cand-2838",
        "predicate": "receipt_records_sale_to_zanetti_of_poussin_castiglione_and_fifteen_gems_cameos",
        "claim": "The note says the receipt records a Poussin, a Castiglione with animals and figures, and fifteen gems and cameos as sold to Zanetti.",
        "qualification": "The seller is not named in the note. Both paintings remain untitled, the gem/cameo items are unidentified, and the receipt was not inspected.",
        "mentioned": ["cand-10200", "cand-2838", "cand-10069", "cand-10070", "cand-10204"],
        "citations": [{"source_candidate_id": "cand-10200", "container_candidate_id": "cand-10199", "item_candidate_ids": ["cand-10069", "cand-10070", "cand-10204"]}],
        "linked": body_footnote_targets["4"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p341-notes-note4-memorie-mentions-castiglione-not-poussin",
        "marker": "4", "line": 226, "subject": "cand-10201", "object": "cand-10070",
        "predicate": "memorie_mentions_castiglione_but_not_poussin",
        "claim": "The note says Zanetti's Memorie mentions the Castiglione but not the Poussin.",
        "qualification": "This records Haskell's comparison of the Memorie with the receipt; it does not independently establish why the Poussin is absent.",
        "mentioned": ["cand-10201", "cand-10070", "cand-10069", "cand-2838"],
        "citations": [{"source_candidate_id": "cand-10201", "container_candidate_id": "cand-10199", "mentioned_candidate_id": "cand-10070", "omitted_candidate_id": "cand-10069"}],
        "linked": body_footnote_targets["4"],
    },
    {
        "id": "st-chp13-p341-notes-note4-memorie-describes-copper-pastoral-by-epithet",
        "marker": "4", "line": 226, "subject": "cand-10201", "object": "cand-10203",
        "predicate": "memorie_describes_unidentified_copper_pastoral_as_painted_by_spagnolo_di_bologna",
        "claim": "The note quotes the Memorie describing a small, framed copper pastoral picture and credits it to ‘lo Spagnolo di Bologna’.",
        "qualification": "The epithet is not equated with Crespi here; the note does not establish that this is the same pastoral mentioned in the p.341 body.",
        "mentioned": ["cand-10201", "cand-10203", "cand-2838"],
        "citations": [{"source_candidate_id": "cand-10201", "container_candidate_id": "cand-10199", "artist_epithet_candidate_id": "cand-10203"}],
        "linked": body_footnote_targets["4"],
    },
]

new_statements = []
note_statement_ids_by_marker = {marker: [] for marker in body_footnote_targets}
for spec in new_statement_specs:
    for candidate_id in spec["mentioned"]:
        if candidate_id not in all_candidate_ids:
            raise SystemExit(f"statement candidate missing: {spec['id']} -> {candidate_id}")
    qualifiers = {
        "source_line_start": spec["line"],
        "source_line_end": spec["line"],
        "printed_page": 341,
        "pdf_physical_page": 10,
        "claim": spec["claim"],
        "speaker": "Haskell, printed footnote",
        "text_layer": "secondary source note and citation",
        "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"],
        "footnote_marker": spec["marker"],
        "footnote_printed_page": 341,
        "linked_body_statement_ids": spec["linked"],
        "citations": spec["citations"],
    }
    if spec.get("relation_candidate"):
        qualifiers["relation_candidate"] = True
    if spec.get("ocr_corrections"):
        qualifiers["ocr_corrections"] = spec["ocr_corrections"]
    new_statements.append({
        "statement_id": spec["id"],
        "segment_id": NOTES,
        "subject_candidate_id": spec["subject"],
        "object_candidate_id": spec["object"],
        "predicate": spec["predicate"],
        "qualifiers": qualifiers,
        "original_quote": source_lines[spec["line"] - 1],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })
    note_statement_ids_by_marker[spec["marker"]].append(spec["id"])

for marker, body_ids in body_footnote_targets.items():
    note_ids = note_statement_ids_by_marker[marker]
    if not note_ids:
        raise SystemExit(f"no note statements for marker {marker}")
    for statement_id in body_ids:
        qualifiers = statement_by_id[statement_id].setdefault("qualifiers", {})
        refs = qualifiers.get("footnote_refs", [])
        matching = [r for r in refs if r.get("footnote_marker") == marker and r.get("footnote_printed_page") == 341 and r.get("footnote_text_pending")]
        if not matching:
            raise SystemExit(f"pending p.341 footnote {marker} missing from {statement_id}")
        for ref in matching:
            ref["footnote_text_pending"] = False
            ref["footnote_body_link_status"] = "linked"
            ref["footnote_note_statement_ids"] = note_ids
        qualifiers["footnote_note_statement_ids"] = sorted(set(qualifiers.get("footnote_note_statement_ids", [])) | set(note_ids))
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"

# Complete the local page state only after notes 1-4 and Plate 58a are linked.
coverage[BODY]["migration_status"] = "complete"
coverage[BODY]["source_line_ranges"] = "L90-96"
coverage[BODY]["note"] = (
    "Printed p.341 body and notes 1-4 were checked against CHP-13.pdf physical page 10. "
    "All four footnotes are linked to their marked claims; the Tessin sentence closes at p.342 L99. "
    "Plate 58a resolves to existing portrait work cand-4048 through the caption segment, checked at physical page 15. "
    "OCR corrections Ahecedario->Abecedario and Pncipe->Principe are recorded in S2 only; cited sources/manuscripts remain unconsulted."
)
coverage[NOTES]["source_line_ranges"] = "L180-226"
coverage[NOTES]["note"] = (
    "Notes L180-216 (pp.332-339), p.340 notes at L217-222, and p.341 notes 1-4 at L223-226 are migrated. "
    "L227-246 and mirrored caption lines L247-248 remain to process or map; the composite segment remains partial."
)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = [
    statement_by_id.get(row["statement_id"], row) for row in statements
] + new_statements
if len({r["candidate_id"] for r in candidate_out}) != len(candidate_out):
    raise SystemExit("candidate IDs are not unique after migration")
if len({r["mention_id"] for r in mention_out}) != len(mention_out):
    raise SystemExit("mention IDs are not unique after migration")
if len({r["statement_id"] for r in statement_out}) != len(statement_out):
    raise SystemExit("statement IDs are not unique after migration")
for row in new_mentions:
    if notes_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"final mention span failed: {row['mention_id']}")
for row in new_statements:
    if row["original_quote"] not in notes_text:
        raise SystemExit(f"statement quote not found in source segment: {row['statement_id']}")
for marker, body_ids in body_footnote_targets.items():
    for statement_id in body_ids:
        refs = statement_by_id[statement_id]["qualifiers"]["footnote_refs"]
        if any(r.get("footnote_marker") == marker and r.get("footnote_text_pending") for r in refs):
            raise SystemExit(f"footnote {marker} remains pending on {statement_id}")

print(f"candidate rows: {len(candidates)} -> {len(candidate_out)} (+{len(new_candidates)})")
print(f"mention rows: {len(mentions)} -> {len(mention_out)} (+{len(new_mentions)})")
print(f"statement rows: {len(statements)} -> {len(statement_out)} (+{len(new_statements)})")
print("coverage: p.341 body partial -> complete; notes range L180-222 -> L180-226, still partial")
print("footnotes 1-4 linked; Plate 58a reuses caption-confirmed candidate cand-4048")
print("print corrections recorded only in S2: Ahecedario -> Abecedario; Pncipe -> Principe")
print("no cited book, will, receipt, or manuscript was independently consulted")
if not args.apply:
    print("dry-run only; rerun with --apply after reviewing this delta")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
if any(path.exists() for path in backups):
    raise SystemExit("one or more migration backup paths already exist")
for original, backup in zip(targets, backups):
    shutil.copy2(original, backup)
write_csv(candidate_path, candidate_fields, candidate_out)
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statement_out)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied with four table backups:")
for path in backups:
    print(f"  {path.relative_to(ROOT)}")
