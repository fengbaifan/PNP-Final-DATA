"""Controlled S2 migration for chapter 16 p.377 and the continued p.376 note 3."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-16.pdf"
SOURCE_SHA = "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff"
PDF_SHA = "6bfb3e331f0ac2421d31279f97b08b17486f0e2c32451a10a6798cf31424af5f"
BODY_PREV = "chp-16:16_CHP-16_intro:l38-46"
BODY = "chp-16:16_CHP-16_intro:l48-64"
NOTES = "chp-16:16_CHP-16_intro:l69-89"
BACKUP_SUFFIX = ".bak-s2-chp16-p377-celotti-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 16 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-16 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = {
    48: "[Page 377]", 49: "ones caused, some anxiety to the Inquisitors of State",
    50: "Domenico on whose behalf he negotiated a few commissions",
    52: "Luigi Celotti, who survived the downfall of the Republic",
    53: "Paris and his native Venice", 55: "Choral Books of the Papal Chapel in the Vatican",
    56: "Of his eight Canalettos", 58: "composition fougueuse",
    59: "They were outside the main currents of the intellectual life of Venice",
    60: "by Valerio Vannetti in Roveredo", 62: "A letter from him to G. B. Tiepolo",
    64: "Archivio di Stato, Venice—Inquisitori, 540",
    85: "Levi, I, p. cxxxv", 86: "Gazzetta di Venezia, 4 Maggio 1821",
    87: "Christies’, 26 May 1825", 88: "Noticele Tableaux",
    89: "doni la vente aura lieu le luridi 14 Novembre 1814",
}
for line_number, fragment in required.items():
    if fragment.casefold() not in source_lines[line_number - 1].casefold():
        raise SystemExit(f"required source text changed at L{line_number}: {fragment}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
if (coverage_by_id[BODY_PREV]["migration_status"] != "partial"
        or coverage_by_id[BODY]["disposition"] != "queued"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "partial"
        or coverage_by_id[NOTES]["source_line_ranges"] != "L70-84"):
    raise SystemExit("S2 coverage preconditions changed")
if any(row["segment_id"] == BODY for row in mentions):
    raise SystemExit("p.377 segment already has mention rows")
if any(row.get("statement_id", "").startswith("st-chp16-p377-") for row in statements):
    raise SystemExit("p.377 statements already exist")
if "cand-8793" not in candidate_by_id or "cand-10462" not in candidate_by_id:
    raise SystemExit("required shared citation candidates are missing")
previous_swajer_id = "st-chp16-p376-swajer-secret-manuscripts-partial"
previous_note3_id = "st-chp16-p376-note3-swajer-correspondence-partial"
previous_swajer = statement_by_id.get(previous_swajer_id)
previous_note3 = statement_by_id.get(previous_note3_id)
if not previous_swajer or not previous_note3:
    raise SystemExit("p.376 partial continuation statements are missing")
if previous_swajer["qualifiers"].get("predicate_status") != "partial" or BODY not in previous_swajer["qualifiers"].get("cross_reference_segments", []):
    raise SystemExit("p.376 Swajer body statement is not in expected partial state")
if previous_note3["qualifiers"].get("predicate_status") != "partial" or BODY not in previous_note3["qualifiers"].get("cross_reference_segments", []):
    raise SystemExit("p.376 note 3 is not in expected partial state")

body_lines = {number: source_lines[number - 1] for number in range(48, 65)}
note_lines = {number: source_lines[number - 1] for number in range(69, 90)}
segment_lines = {BODY: body_lines, NOTES: note_lines}
segment_texts = {key: "\n".join(lines.values()) for key, lines in segment_lines.items()}
segment_line_offsets = {}
for segment_id, lines in segment_lines.items():
    segment_line_offsets[segment_id] = {}
    offset = 0
    for line_number, line in lines.items():
        segment_line_offsets[segment_id][line_number] = offset
        offset += len(line) + 1

new_candidates = [
    ("cand-10647", "Unidentified portrait of Amadeo Swajer painted by Antonio Canova", "work", BODY, 50,
     "The source says Canova painted Swajer's portrait; it supplies no title, date, medium, or location."),
    ("cand-10648", "'Amateur éclairé' as the self-description in Celotti's sale notices", "term", BODY, 53,
     "The phrase is quoted from announcements that Celotti used to advertise works for disposal; it is not a formal title or organization."),
    ("cand-10649", "Papal Chapel in the Vatican (referent not further specified)", "", BODY, 55,
     "Named as the source context for choral books; the passage does not distinguish a chapel space from the institution using it."),
    ("cand-10650", "Choral Books of the Papal Chapel in the Vatican", "archive", BODY, 55,
     "The books are identified as the source of illuminated miniatures taken during the French Revolution; no titles or repository shelfmarks are supplied."),
    ("cand-10651", "Illuminated miniatures taken from the Papal Chapel's Choral Books during the French Revolution", "work", BODY, 54,
     "An unnamed group of illuminated miniatures that Haskell says Celotti was famous for; individual images and present locations are unspecified."),
    ("cand-10652", "Unidentified old-master pictures owned and sold by Luigi Celotti", "work", BODY, 55,
     "Haskell describes old masters of all sorts but gives no titles, number, or individual attributions."),
    ("cand-10653", "Unidentified eighteenth-century Venetian paintings owned by Luigi Celotti", "work", BODY, 55,
     "The source gives no individual titles, number, or locations."),
    ("cand-10654", "Eight unidentified Canaletto paintings in Luigi Celotti's collection", "work", BODY, 56,
     "Haskell gives the count and artist; individual titles and locations are not supplied."),
    ("cand-10655", "Four Canaletto paintings enriched with figures by Giambattista Tiepolo", "work", BODY, 56,
     "A four-work subset of Celotti's eight Canalettos, described in an 1807 recommendation; individual titles are not supplied."),
    ("cand-10656", "Unidentified Sebastiano Ricci pastoral scene in Luigi Celotti's collection", "work", BODY, 57,
     "The source gives a genre and a French critical description, but no title, date, or location."),
    ("cand-10657", "Giambattista Tiepolo sketch of the Rape of Ganymede in Celotti's collection", "work", BODY, 57,
     "The source identifies the subject but gives no title, date, or location; S1 has a matching Tiepolo index subentry to review in S3."),
    ("cand-10658", "Unidentified allegorical Tiepolo sketch in Celotti's collection", "work", BODY, 58,
     "The source identifies only an allegorical subject, without title, date, or location."),
    ("cand-10659", "Levi, volume I, page cxxxv (citation locator for Celotti's reported death)", "archive", NOTES, 85,
     "Haskell cites only Levi, volume I, page cxxxv; the full title and edition are not identified here, and the cited page was not consulted."),
    ("cand-10660", "Announcement 'Agli amatori delle Arti belle' in Gazzetta di Venezia, 4 May 1821", "archive", NOTES, 86,
     "The citation identifies an announcement and newspaper date; the issue and page were not independently consulted."),
    ("cand-10661", "Christie's sale record, 26 May 1825 (miniatures described by William Young Ottley)", "archive", NOTES, 87,
     "Haskell gives an auction venue and date and says Ottley described the miniatures; no lot number or catalogue title is supplied."),
    ("cand-10662", "Notice de Tableaux par les plus grands maîtres d'Italie, cabinet de M. Celotti de Venise, Paris 1807", "archive", NOTES, 88,
     "Haskell cites this sale catalogue; its OCR title is retained as source anchor and its page was not consulted."),
    ("cand-10663", "Notice d'une collection de tableaux appartenant à Celotti, sale of 14 November 1814", "archive", NOTES, 89,
     "Haskell cites a sale catalogue and notes that the bracketed Celotti wording was added in ink to the copy he saw; the printed M.r is an honorific, not a middle initial, and that copy was not consulted."),
    ("cand-10664", "Valerio Vannetti (correspondent of Amadeo Swajer named in p.377 note 3)", "person", BODY, 60,
     "Named as a correspondent writing from Roveredo; no further identity is supplied in the note."),
    ("cand-10665", "Roveredo (place named in Swajer's correspondence note)", "place", BODY, 60,
     "The note supplies this place-name but no fuller geographic identification."),
    ("cand-10666", "Letters from Valerio Vannetti in Roveredo to Amadeo Swajer (1750s–1760s)", "archive", BODY, 60,
     "Haskell describes a volume of letters, mostly about literature; the letters were not independently consulted."),
    ("cand-10667", "Letters from the Durazzo family in Genoa to Amadeo Swajer (1780s–1790s)", "archive", BODY, 61,
     "Haskell describes another set, mostly about politics, and says Swajer was in close touch with the family; the letters were not consulted."),
    ("cand-10668", "Letter from Amadeo Swajer to Giambattista Tiepolo, published by Urbani de Ghelthof in 1879", "archive", BODY, 62,
     "Haskell cites the published letter at pages 19 and 32; the letter and publication were not independently consulted."),
    ("cand-10669", "Letter from Gian Domenico Tiepolo to Amadeo Swajer, published by Urbani de Ghelthof in 1879", "archive", BODY, 62,
     "Haskell cites the published letter at pages 19 and 32; the letter and publication were not independently consulted."),
    ("cand-10670", "King of France named in Swajer's letter about Tiepolo's 'consaputo quadro' (ruler unidentified)", "person", BODY, 63,
     "The letter names only the royal office; no monarch is inferred from the painting or period."),
    ("cand-10671", "Unidentified Tiepolo picture called 'consaputo quadro' in Swajer's letter about the King of France", "work", BODY, 63,
     "The letter refers to a picture without giving its title, subject, date, commission status, or location."),
    ("cand-10672", "Ateneo Veneto, May 1937 (citation locator on Urbani de Ghelthof's use of documents)", "archive", BODY, 64,
     "Haskell cites this periodical item as the basis for caution about Urbani de Ghelthof's documentary reliability; it was not independently consulted."),
]
for cid, name, suggested_type, segment_id, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    candidate = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment_id}#L{source_line}",
    }
    candidates.append(candidate)
    candidate_by_id[cid] = candidate

shared_publication = candidate_by_id["cand-8793"]
old_publication_detail = shared_publication["detail"]
expected_publication_detail = "The p.270, p.273 and p.274 notes use this same 1879 publication; cited pages not independently consulted."
if old_publication_detail != expected_publication_detail:
    raise SystemExit("unexpected shared Urbani de Ghelthof candidate detail")
shared_publication["detail"] = (
    "The p.270, p.273 and p.274 notes cite pp.100-117 and 123-126; p.377 note 3 also cites pp.19 and 32. "
    "The cited pages and publication were not independently consulted."
)

planned_mentions = []
mention_counter = 0


def add_mention(candidate_id, surface, segment_id, line_start, line_end=None, note="", occurrence=0):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    if line_end is None:
        line_end = line_start
    start_bound = segment_line_offsets[segment_id][line_start]
    end_bound = segment_line_offsets[segment_id][line_end] + len(segment_lines[segment_id][line_end])
    text = segment_texts[segment_id][start_bound:end_bound]
    positions = []
    search_from = 0
    while True:
        pos = text.find(surface, search_from)
        if pos < 0:
            break
        positions.append(pos)
        search_from = pos + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface occurrence not found at L{line_start}-{line_end}: {surface!r} #{occurrence + 1}")
    start = start_bound + positions[occurrence]
    end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions
                if row["segment_id"] == segment_id]
    for other_start, other_end in occupied:
        overlaps = start < other_end and other_start < end
        nested = ((start <= other_start and other_end <= end)
                  or (other_start <= start and end <= other_end))
        if overlaps and (not nested or (start, end) == (other_start, other_end)):
            raise SystemExit(f"mention has duplicate or crossing span: {surface!r} at L{line_start}-{line_end}")
    mention_counter += 1
    planned_mentions.append({
        "mention_id": f"m-chp16-p377-celotti-{mention_counter:04d}",
        "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


mention_specs = [
    # P.377 body: complete Swajer continuation and transition to Celotti.
    ("cand-10643", "ones", BODY, 49, None, "Resolves to Swajer's 'secret' manuscripts on p.376.", 0),
    ("cand-10524", "Inquisitors of State", BODY, 49, None, "Reuses the institution candidate named as State Inquisition on p.376.", 0),
    ("cand-10643", "them all", BODY, 49, None, "The manuscripts acquired by the Inquisitors; antecedent is p.376 L46.", 0),
    ("cand-2534", "he", BODY, 49, None, "Anaphoric reference to Amadeo Swajer from p.376.", 0),
    ("cand-2569", "Giambattista Tiepolo", BODY, 49, None, "Artist in contact with Swajer.", 0),
    ("cand-2624", "Gian\nDomenico", BODY, 49, 50, "The source line break splits the name; mapped to the index candidate for Gian Domenico Tiepolo.", 0),
    ("cand-0535", "Canova", BODY, 50, None, "Reuses the page-specific index candidate whose subentry is Swajer's portrait.", 0),
    ("cand-2534", "his", BODY, 50, None, "Possessive reference to Swajer in 'his portrait'.", 0),
    ("cand-10647", "his portrait", BODY, 50, None, "The portrait is not titled or located.", 0),
    ("cand-0622", "Luigi Celotti", BODY, 52, None, "Full name as printed across the page break from the title 'Abate'.", 0),
    ("cand-8838", "Republic", BODY, 52, None, "Venetian political entity, distinct from the city.", 0),
    ("cand-0622", "he", BODY, 52, None, "Anaphoric reference to Luigi Celotti.", 0),
    ("cand-1422", "London", BODY, 52, None, "City where Celotti reappeared in the account.", 0),
    ("cand-4653", "Paris", BODY, 53, None, "City where Celotti reappeared in the account.", 0),
    ("cand-2719", "Venice", BODY, 53, None, "His native city in this sentence.", 0),
    ("cand-10648", "amateur éclairé", BODY, 53, None, "Quoted phrase in Celotti's disposal notices.", 0),
    ("cand-3399", "Vatican", BODY, 55, None, "Uses the existing Vatican place candidate.", 0),
    ("cand-9828", "French Revolution", BODY, 55, None, "Historical event named as the time of removal.", 0),
    ("cand-10651", "illumined miniature paintings taken from the\nChoral Books of the Papal Chapel in the Vatican during the French Revolution", BODY, 54, 55, "S0 reads 'illumined'; retain that exact span. Unnamed work group; the source describes the books and removal context.", 0),
    ("cand-10650", "Choral Books", BODY, 55, None, "Manuscript books named as the source of the miniatures.", 0),
    ("cand-10649", "Papal Chapel", BODY, 55, None, "The exact building/institution referent is not specified.", 0),
    ("cand-4288", "old masters", BODY, 55, None, "Existing broad art-historical term candidate.", 0),
    ("cand-10652", "old masters of all sorts", BODY, 55, None, "Unidentified works described as owned and sold by Celotti.", 0),
    ("cand-10653", "eighteenth-century Venetian paintings", BODY, 55, None, "Unidentified group of paintings.", 0),
    ("cand-0126", "dealers", BODY, 56, None, "Collective comparison with previously discussed art dealers.", 0),
    ("cand-10654", "eight Canalettos", BODY, 56, None, "Aggregate work group; the source gives no individual titles.", 0),
    ("cand-0498", "Canaletto", BODY, 56, None, "Artist within the plural 'Canalettos'.", 0),
    ("cand-10655", "four", BODY, 56, None, "The four-work subset of the eight Canalettos described in the following French text.", 0),
    ("cand-2569", "Tiepolo", BODY, 57, None, "Artist credited with figures in the four Canaletto paintings and described as Celotti's friend.", 0),
    ("cand-2154", "Sebastiano Ricci", BODY, 57, None, "Existing main index candidate for the artist.", 0),
    ("cand-10656", "Sebastiano Ricci pastoral scene", BODY, 57, None, "Unidentified painting; no title or location is supplied.", 0),
    ("cand-2569", "Tiepolo", BODY, 57, None, "Artist of the sketches; source gives the family name.", 1),
    ("cand-10657", "Rape of\nGanymede", BODY, 57, 58, "Subject of one unidentified Tiepolo sketch.", 0),
    ("cand-3436", "Ganymede", BODY, 58, None, "Mythological figure named in the sketch subject.", 0),
    ("cand-10658", "an allegorical subject", BODY, 58, None, "The second sketch's subject remains unspecified.", 0),
    ("cand-2719", "Venice", BODY, 59, None, "City in Haskell's generalization about intellectual life.", 0),
    # P.376 note 3 continuation at the foot of p.377.
    ("cand-10664", "Valerio Vannetti", BODY, 60, None, "Correspondent named in the continuation of p.376 note 3.", 0),
    ("cand-10665", "Roveredo", BODY, 60, None, "Place named in the correspondence locator; exact location unresolved.", 0),
    ("cand-7360", "Durazzo family", BODY, 61, None, "Reuses the existing family candidate from Haskell's Genoa account.", 0),
    ("cand-1131", "Genoa", BODY, 61, None, "City named in the correspondence locator.", 0),
    ("cand-2534", "him", BODY, 62, None, "Anaphoric reference to Amadeo Swajer in the letter locator.", 0),
    ("cand-2569", "G. B. Tiepolo", BODY, 62, None, "Initialed name for Giambattista Tiepolo in the letter citation.", 0),
    ("cand-2624", "G. D. Tiepolo", BODY, 62, None, "Initialed name for Gian Domenico Tiepolo in the letter citation.", 0),
    ("cand-8793", "Urbani de\nGhelthof", BODY, 62, 63, "Reuses the existing 1879 publication citation candidate.", 0),
    ("cand-10670", "King of\nFrance", BODY, 63, 64, "Unidentified royal office in the Tiepolo letter.", 0),
    ("cand-10671", "consaputo quadro", BODY, 63, 64, "The title/identity of the picture is not supplied.", 0),
    ("cand-10672", "Ateneo Veneto, Maggio 1937", BODY, 64, None, "Citation locator for Haskell's caution about the source's document use.", 0),
    ("cand-2534", "His", BODY, 64, None, "Possessive reference to Swajer's papers and manuscripts.", 0),
    ("cand-10172", "Archivio di Stato, Venice", BODY, 64, None, "Existing repository candidate; the source gives an Inquisitori record locator.", 0),
    ("cand-10462", "Inquisitori, 540, p. 164", BODY, 64, None, "Reuses the existing specific archive citation candidate.", 0),
    # P.377 notes 1-5 in the consolidated footnotes segment.
    ("cand-10659", "Levi, I, p. cxxxv", NOTES, 85, None, "Footnote 1 citation locator; source not consulted.", 0),
    ("cand-8532", "Levi", NOTES, 85, None, "Author named by surname only in the note.", 0),
    ("cand-10660", "Agli amatori delle Arti belle", NOTES, 86, None, "Title of the cited newspaper announcement.", 0),
    ("cand-2719", "Venezia", NOTES, 86, None, "Italian city name in the newspaper title; maps to Venice candidate.", 0),
    ("cand-10660", "Gazzetta di Venezia, 4 Maggio 1821", NOTES, 86, None, "Dated newspaper citation in footnote 2.", 0),
    ("cand-9400", "Christies’", NOTES, 87, None, "Reuses the existing auction-house institution candidate.", 0),
    ("cand-10661", "Christies’, 26 May 1825", NOTES, 87, None, "Dated sale citation in footnote 3.", 0),
    ("cand-1793", "William Young Ottley", NOTES, 87, None, "Existing indexed author named as the describer of the miniatures.", 0),
    ("cand-10662", "Noticele Tableaux, par les plus grands maitres dTtalie,... composant le cabinet de M. Celottide Venise...., Paris 1807", NOTES, 88, None, "Source OCR title span; print reading is recorded in corrections, not written back to S0.", 0),
    ("cand-0622", "Celotti", NOTES, 88, None, "Person named as the owner of the 1807 catalogue collection.", 0),
    ("cand-4653", "Paris", NOTES, 88, None, "Publication place named in the citation.", 0),
    ("cand-10663", "Notice d’une collection de tableaux [appartenant à M.r Celotti] doni la vente aura lieu le luridi 14 Novembre 1814", NOTES, 89, None, "Source OCR title/citation span; print readings are recorded separately.", 0),
    ("cand-0622", "Celotti", NOTES, 89, None, "Owner named in the bracketed wording of the catalog title.", 0),
    ("cand-2569", "Tiepolos", NOTES, 89, None, "Plural artist name in the 1814 sales note.", 0),
    ("cand-1901", "Piazzettas", NOTES, 89, None, "Plural artist name in the 1814 sales note.", 0),
]
for candidate_id, surface, segment_id, line_start, line_end, note, occurrence in mention_specs:
    add_mention(candidate_id, surface, segment_id, line_start, line_end, note, occurrence)

body49, body50 = source_lines[48], source_lines[49]
body51, body52, body53 = source_lines[50], source_lines[51], source_lines[52]
body54, body55, body56 = source_lines[53], source_lines[54], source_lines[55]
body57, body58, body59 = source_lines[56], source_lines[57], source_lines[58]
note60, note61, note62, note63, note64 = [source_lines[n - 1] for n in range(60, 65)]
note85, note86, note87, note88, note89 = [source_lines[n - 1] for n in range(85, 90)]

def corr(line, ocr, printed):
    return {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": line,
            "ocr": ocr, "print": printed, "basis": "CHP-16.pdf physical page 5."}


corrections_l49 = [corr(49, "caused, some", "caused some")]
corrections_l52 = [corr(52, "hewas", "he was")]
corrections_l58 = [corr(58, ". . ..6", ". . ..5")]
corrections_l64 = [
    corr(64, "should perhaps.be", "should perhaps be"),
    corr(64, "some,caution", "some caution"),
]
corrections_note85 = [corr(85, "abouf’1846", "about 1846")]
corrections_note88 = [
    corr(88, "Noticele", "Notice de"), corr(88, "maitres", "maîtres"),
    corr(88, "dTtalie", "d’Italie"), corr(88, "Celottide", "Celotti de"),
    corr(88, "Venise....", "Venise…"),
]
corrections_note89 = [
    corr(89, "doni", "dont"), corr(89, "luridi", "lundi"), corr(89, "6 In 1814", "5 In 1814"),
]

note3_previous_id = previous_note3_id
note1_id = "st-chp16-p377-note1-levi-celotti-date"
note2_id = "st-chp16-p377-note2-celotti-advertisement"
note3_id = "st-chp16-p377-note3-christies-miniatures"
note4_id = "st-chp16-p377-note4-celotti-1807-catalogue"
note5_id = "st-chp16-p377-note5-celotti-1814-sale"
note3_cont_ids = [
    "st-chp16-p377-note3-vannetti-correspondence",
    "st-chp16-p377-note3-durazzo-correspondence",
    "st-chp16-p377-note3-published-swajer-tiepolo-letter",
    "st-chp16-p377-note3-published-gian-domenico-swajer-letter",
    "st-chp16-p377-note3-letter-and-consaputo-quadro",
    "st-chp16-p377-note3-ghelthof-provenance-claim",
    "st-chp16-p377-note3-ghelthof-reliability-caution",
    "st-chp16-p377-note3-state-archive-locator",
]


def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, speaker, text_layer, qualification, mentioned_ids, quote,
                   relation_candidate=False, **extra_qualifiers):
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 377, "pdf_physical_page": 5,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned_ids,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    qualifiers.update(extra_qualifiers)
    statements.append({
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject_id, "object_candidate_id": object_id,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
    })


note1_link = {
    "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L85-L85",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L52", "footnote_note_statement_ids": [note1_id],
    "footnote_link_note": "P.377 note 1 cites Levi for Celotti's reported death date.",
}
note2_link = {
    "footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L86-L86",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L53", "footnote_note_statement_ids": [note2_id],
    "footnote_link_note": "P.377 note 2 identifies one of Celotti's disposal announcements.",
}
note3_link = {
    "footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L87-L87",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L54-L55", "footnote_note_statement_ids": [note3_id],
    "footnote_link_note": "P.377 note 3 gives a Christie's locator and says Ottley described the miniatures.",
}
note4_link = {
    "footnote_marker": "4", "footnote_segment": NOTES, "footnote_line_range": "L88-L88",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L56-L58", "footnote_note_statement_ids": [note4_id],
    "footnote_link_note": "P.377 note 4 cites the 1807 Celotti catalogue connected with the collection descriptions.",
}
note5_link = {
    "footnote_marker": "5", "footnote_segment": NOTES, "footnote_line_range": "L89-L89",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L52-L58", "footnote_note_statement_ids": [note5_id],
    "footnote_link_note": "Page image shows note 5; S0 reads 6. Note 5 records a further 1814 sale.",
}

# Complete the p.376 sentence with a page-local quote and a cross-reference.
make_statement(
    "st-chp16-p377-swajer-inquisitors-conclusion", BODY, "cand-2534", "cand-10643",
    "possible_dispersal_caused_anxiety_and_inquisitors_acquired_all_secret_manuscripts", 49, 49,
    "The continuation says possible dispersal of Swajer's secret manuscripts caused anxiety to the Inquisitors of State, who acquired them all.",
    "Haskell", "authorial report", "The p.376 phrase 'possible dispersal' remains qualified; the p.377 continuation supplies the reaction and acquisition.",
    ["cand-2534", "cand-10643", "cand-10524"], body49,
    relation_candidate=True, cross_reference_statement_ids=["st-chp16-p376-swajer-secret-manuscripts-partial"],
    ocr_corrections=corrections_l49,
)
# Swajer's named contacts and actions.
make_statement(
    "st-chp16-p377-swajer-in-contact-with-giambattista-tiepolo", BODY, "cand-2534", "cand-2569",
    "was_in_touch_with_giambattista_tiepolo", 49, 50,
    "Haskell says Swajer was in touch with Giambattista Tiepolo.",
    "Haskell", "authorial report", "This records contact only; it does not by itself establish friendship or a commission.",
    ["cand-2534", "cand-2569"], body49 + "\n" + body50, relation_candidate=True,
)
make_statement(
    "st-chp16-p377-swajer-negotiated-gian-domenico-commissions", BODY, "cand-2534", "cand-2624",
    "negotiated_a_few_commissions_on_behalf_of_gian_domenico_tiepolo", 49, 50,
    "Haskell says Swajer negotiated a few commissions on behalf of Gian Domenico Tiepolo.",
    "Haskell", "authorial report", "The wording's nearest antecedent is Gian Domenico; no commissions or patrons are identified.",
    ["cand-2534", "cand-2569", "cand-2624"], body49 + "\n" + body50, relation_candidate=True,
)
make_statement(
    "st-chp16-p377-canova-painted-swajer-portrait", BODY, "cand-0535", "cand-10647",
    "painted_portrait_of_amadeo_swajer", 50, 50,
    "Haskell says Canova painted Swajer's portrait.",
    "Haskell", "authorial report", "The portrait is not titled, dated, or located in this passage.",
    ["cand-0535", "cand-10647", "cand-2534"], body50, relation_candidate=True,
)
make_statement(
    "st-chp16-p377-swajer-portrait-subject", BODY, "cand-10647", "cand-2534",
    "portrait_of_amadeo_swajer", 50, 50,
    "The portrait painted by Canova depicts Amadeo Swajer.",
    "Haskell", "authorial report", "Subject identification follows the possessive 'his' after the Swajer discussion.",
    ["cand-10647", "cand-2534", "cand-0535"], body50, relation_candidate=True,
)

# Celotti's dealer activity, works, and Haskell's evaluative language.
make_statement(
    "st-chp16-p377-celotti-dealer-characterization", BODY, "cand-0622", None,
    "described_as_more_adventurous_and_successful_dealer_than_preceding_collectors", 51, 52,
    "Haskell characterizes Celotti as a more adventurous and successful dealer than those previously discussed.",
    "Haskell", "authorial evaluation", "The comparison is Haskell's characterization, not an independently measured ranking.",
    ["cand-0622", "cand-0126"], body51 + "\n" + body52,
)
make_statement(
    "st-chp16-p377-celotti-survived-republic-fall", BODY, "cand-0622", "cand-8838",
    "survived_fall_of_venetian_republic_by_half_a_century", 52, 52,
    "Haskell says Celotti survived the fall of the Republic by half a century.",
    "Haskell", "authorial report", "No exact death date is inferred here; note 1 separately reports about 1846.",
    ["cand-0622", "cand-8838"], body52, relation_candidate=True,
)
make_statement(
    "st-chp16-p377-celotti-at-home-in-all-regimes", BODY, "cand-0622", None,
    "characterized_as_at_home_in_all_regimes_as_long_as_clients_bought_his_pictures", 52, 52,
    "Haskell says Celotti was at home in all regimes so long as he had clients to buy his pictures.",
    "Haskell", "authorial characterization", "The phrase is Haskell's account of adaptability, not a specific political office.",
    ["cand-0622"], body52,
)
make_statement(
    "st-chp16-p377-celotti-assembled-and-dispersed-collections", BODY, "cand-0622", None,
    "repeatedly_built_up_and_dispersed_collections_in_london_paris_and_venice", 52, 53,
    "Haskell says Celotti repeatedly built collections and dispersed them, appearing in London, Paris, and his native Venice.",
    "Haskell", "authorial report", "The cities are locations in the account; no individual collection or itinerary is specified.",
    ["cand-0622", "cand-1422", "cand-4653", "cand-2719"], body52 + "\n" + body53,
)
make_statement(
    "st-chp16-p377-celotti-advertised-disposal-as-amateur-eclaire", BODY, "cand-0622", "cand-10648",
    "sale_notices_described_an_amateur_eclaire_wishing_to_dispose_of_works", 53, 53,
    "Haskell says discreet newspaper announcements usually preceded Celotti's appearances, saying an 'amateur éclairé' wished to dispose of some works of art.",
    "Haskell", "authorial report quoting notices", "The phrase is an advertisement's wording as reported by Haskell; no individual notice is identified in the body.",
    ["cand-0622", "cand-10648"], body53, relation_candidate=True, **note2_link,
)
make_statement(
    "st-chp16-p377-celotti-miniatures-from-papal-choral-books", BODY, "cand-0622", "cand-10651",
    "included_illuminated_miniatures_taken_from_papal_choral_books_during_french_revolution", 54, 55,
    "Among the works advertised for disposal were illuminated miniatures taken from the Papal Chapel's Choral Books in the Vatican during the French Revolution.",
    "Haskell", "authorial report quoting notice", "The source says Celotti was famous for such mediaeval treasures; no individual miniature or current location is identified.",
    ["cand-0622", "cand-10651", "cand-10650", "cand-10649", "cand-3399", "cand-9828"], body54 + "\n" + body55,
    relation_candidate=True, **note3_link,
)
make_statement(
    "st-chp16-p377-celotti-owned-and-sold-old-masters", BODY, "cand-0622", "cand-10652",
    "owned_and_sold_unidentified_old_masters", 55, 55,
    "Haskell says Celotti owned and sold old masters of all sorts.",
    "Haskell", "authorial report", "Individual pictures and attributions are not identified.",
    ["cand-0622", "cand-10652", "cand-4288"], body55, relation_candidate=True,
)
make_statement(
    "st-chp16-p377-celotti-owned-eighteenth-century-venetian-paintings", BODY, "cand-0622", "cand-10653",
    "owned_many_eighteenth_century_venetian_paintings", 55, 55,
    "Haskell says Celotti owned many eighteenth-century Venetian paintings.",
    "Haskell", "authorial report", "No number, title, or location is supplied.",
    ["cand-0622", "cand-10653"], body55, relation_candidate=True,
)
make_statement(
    "st-chp16-p377-haskell-infers-celotti-salesmanship-and-taste", BODY, "cand-0622", None,
    "haskell_infers_salesmanship_and_individual_taste_from_rhapsodic_accounts", 56, 56,
    "Haskell says Celotti's rhapsodic accounts suggest both salesmanship and genuine individual taste similar to that of some humbler dealers.",
    "Haskell", "explicit authorial inference", "The sentence opens 'It is legitimate to infer'; its conclusions remain Haskell's interpretation.",
    ["cand-0622", "cand-0126"], body56,
)
make_statement(
    "st-chp16-p377-celotti-eight-canaletto-paintings", BODY, "cand-0622", "cand-10654",
    "owned_eight_canaletto_paintings_four_enriched_with_tiepolo_figures", 56, 57,
    "Haskell says Celotti owned eight Canalettos, four of which were praised for their composition and execution and enriched with figures by Tiepolo.",
    "Haskell", "authorial report with quoted catalogue text", "The French passage is quoted from the 1807 recommendation; the individual paintings are unnamed.",
    ["cand-0622", "cand-10654", "cand-0498", "cand-10655", "cand-2569"], body56 + "\n" + body57,
    relation_candidate=True, **note4_link,
)
make_statement(
    "st-chp16-p377-celotti-four-canalettos-with-tiepolo-figures", BODY, "cand-10655", "cand-2569",
    "four_canaletto_paintings_enriched_with_figures_by_tiepolo", 56, 57,
    "The 1807 catalogue description says four of Celotti's Canalettos were enriched with figures by Tiepolo.",
    "Haskell quoting catalogue", "bibliographic quotation", "The figures are attributed to Tiepolo; no individual painting or figure is identified.",
    ["cand-10655", "cand-0498", "cand-2569"], body56 + "\n" + body57, relation_candidate=True,
)
make_statement(
    "st-chp16-p377-celotti-tiepolo-friendship-as-catalogue-wording", BODY, "cand-0622", "cand-2569",
    "described_as_friend_of_tiepolo_in_1807_catalogue", 57, 57,
    "The quoted 1807 catalogue calls Tiepolo 'son ami' in its recommendation of the Canaletto paintings.",
    "1807 catalogue as quoted by Haskell", "bibliographic quotation", "This records the catalogue's wording, not independent proof of a personal friendship.",
    ["cand-0622", "cand-2569"], body57, relation_candidate=True,
)
make_statement(
    "st-chp16-p377-celotti-sebastiano-ricci-pastoral", BODY, "cand-0622", "cand-10656",
    "owned_sebastiano_ricci_pastoral_scene_described_as_fresh_in_colour_and_light_in_brushwork", 57, 57,
    "Haskell describes Celotti's Sebastiano Ricci pastoral scene as having fresh colour and a light brush.",
    "Haskell quoting a sale description", "bibliographic quotation", "The French appraisal is retained as a source characterization; the work is unidentified.",
    ["cand-0622", "cand-10656", "cand-2154"], body57, relation_candidate=True,
)
make_statement(
    "st-chp16-p377-celotti-tiepolo-rape-of-ganymede-sketch", BODY, "cand-0622", "cand-10657",
    "owned_tiepolo_sketch_of_rape_of_ganymede", 57, 58,
    "Haskell says Celotti's Tiepolo sketches included one of the Rape of Ganymede.",
    "Haskell quoting a sale description", "bibliographic quotation", "The index has a Giambattista Tiepolo sketch subentry; identity of the object remains for S3.",
    ["cand-0622", "cand-10657", "cand-2569", "cand-3436", "cand-2608"], body57 + "\n" + body58,
    relation_candidate=True,
)
make_statement(
    "st-chp16-p377-celotti-tiepolo-allegorical-sketch", BODY, "cand-0622", "cand-10658",
    "owned_tiepolo_sketch_of_unidentified_allegorical_subject", 57, 58,
    "Haskell says Celotti's Tiepolo sketches also included one with an allegorical subject.",
    "Haskell quoting a sale description", "bibliographic quotation", "The allegorical subject and sketch are unidentified.",
    ["cand-0622", "cand-10658", "cand-2569"], body57 + "\n" + body58,
    relation_candidate=True,
)
make_statement(
    "st-chp16-p377-haskell-generalizes-dealers-collections-and-patronage", BODY, None, None,
    "haskell_generalizes_similar_status_collection_and_patronage_outside_venetian_intellectual_currents", 59, 59,
    "Haskell concludes that the dealers shared social status and similar collection and patronage patterns and stood outside Venice's main intellectual currents.",
    "Haskell", "authorial synthesis", "This is a group-level interpretation of the collectors discussed, not an individually attributed fact about Celotti alone.",
    ["cand-2719"], body59,
)

# Complete the p.376 note 3, whose continuation is printed in the p.377 footnote block.
make_statement(
    note3_cont_ids[0], BODY, "cand-2534", "cand-10666",
    "letters_from_valerio_vannetti_in_roveredo_to_swajer", 60, 60,
    "The continued note identifies a volume of letters from Valerio Vannetti in Roveredo to Swajer.",
    "Haskell's note", "archival locator", "The volume dates from the 1750s–1760s and is described as mostly concerned with literature; it was not consulted.",
    ["cand-2534", "cand-10664", "cand-10665", "cand-10666"], note60,
    cited_source_independently_consulted=False, footnote_marker="3", footnote_segment=NOTES,
    footnote_line_range="L84-L84", footnote_text_pending=False, footnote_body_link_status="linked",
    footnote_body_line_range="L46", footnote_note_statement_ids=[note3_previous_id],
)
make_statement(
    note3_cont_ids[1], BODY, "cand-2534", "cand-10667",
    "letters_from_durazzo_family_in_genoa_to_swajer", 60, 61,
    "The note identifies another set of letters from the Durazzo family in Genoa, with whom Swajer was in close touch.",
    "Haskell's note", "archival locator", "The set dates from the 1780s–1790s and is described as mostly about politics; it was not consulted.",
    ["cand-2534", "cand-10667", "cand-7360", "cand-1131"], note60 + "\n" + note61,
    cited_source_independently_consulted=False, footnote_marker="3", footnote_segment=NOTES,
    footnote_line_range="L84-L84", footnote_text_pending=False, footnote_body_link_status="linked",
    footnote_body_line_range="L46", footnote_note_statement_ids=[note3_previous_id],
)
make_statement(
    note3_cont_ids[2], BODY, "cand-10668", "cand-8793",
    "published_by_urbani_de_ghelthof_1879_at_page_19", 62, 62,
    "The note says the letter from Swajer to G. B. Tiepolo was published by Urbani de Ghelthof in 1879, page 19.",
    "Haskell's note", "bibliographic locator", "The letter and cited publication page were not independently consulted.",
    ["cand-2534", "cand-2569", "cand-10668", "cand-8793"], note62,
    cited_source_independently_consulted=False, footnote_marker="3", footnote_segment=NOTES,
    footnote_line_range="L84-L84", footnote_text_pending=False, footnote_body_link_status="linked",
    footnote_body_line_range="L46", footnote_note_statement_ids=[note3_previous_id],
)
make_statement(
    note3_cont_ids[3], BODY, "cand-10669", "cand-8793",
    "published_by_urbani_de_ghelthof_1879_at_page_32", 62, 62,
    "The note says the letter from G. D. Tiepolo to Swajer was published by Urbani de Ghelthof in 1879, page 32.",
    "Haskell's note", "bibliographic locator", "The letter and cited publication page were not independently consulted.",
    ["cand-2534", "cand-2624", "cand-10669", "cand-8793"], note62,
    cited_source_independently_consulted=False, footnote_marker="3", footnote_segment=NOTES,
    footnote_line_range="L84-L84", footnote_text_pending=False, footnote_body_link_status="linked",
    footnote_body_line_range="L46", footnote_note_statement_ids=[note3_previous_id],
)
make_statement(
    note3_cont_ids[4], BODY, "cand-10668", "cand-10671",
    "letter_referred_to_tiepolo_picture_for_unidentified_king_of_france", 63, 64,
    "The note says the Swajer letter to G. B. Tiepolo refers to Tiepolo's 'consaputo quadro' for the King of France.",
    "Haskell's note", "archival locator and reported letter content", "Neither the picture nor the French monarch is identified.",
    ["cand-10668", "cand-2569", "cand-10670", "cand-10671"], note63 + "\n" + note64,
    cited_source_independently_consulted=False, footnote_marker="3", footnote_segment=NOTES,
    footnote_line_range="L84-L84", footnote_text_pending=False, footnote_body_link_status="linked",
    footnote_body_line_range="L46", footnote_note_statement_ids=[note3_previous_id],
    ocr_corrections=corrections_l64,
)
make_statement(
    note3_cont_ids[5], BODY, "cand-10668", "cand-8793",
    "letter_claimed_as_part_of_urbani_de_ghelthofs_own_collection", 63, 63,
    "Haskell reports that the letter was claimed to belong to Urbani de Ghelthof's own collection.",
    "Haskell's note", "attributed provenance", "This is a reported claim, not verified provenance.",
    ["cand-10668", "cand-8793"], note63,
    cited_source_independently_consulted=False, footnote_marker="3", footnote_segment=NOTES,
    footnote_line_range="L84-L84", footnote_text_pending=False, footnote_body_link_status="linked",
    footnote_body_line_range="L46", footnote_note_statement_ids=[note3_previous_id],
)
make_statement(
    note3_cont_ids[6], BODY, "cand-8793", "cand-10672",
    "documentary_reliability_of_urbani_de_ghelthof_questioned_by_1937_item", 64, 64,
    "Haskell cites an Ateneo Veneto item from May 1937 as evidence that Urbani de Ghelthof was far from reliable in his use of documents.",
    "Haskell's note", "source criticism", "This is Haskell's reason for caution; the 1937 item was not independently consulted.",
    ["cand-8793", "cand-10672"], note64,
    cited_source_independently_consulted=False, footnote_marker="3", footnote_segment=NOTES,
    footnote_line_range="L84-L84", footnote_text_pending=False, footnote_body_link_status="linked",
    footnote_body_line_range="L46", footnote_note_statement_ids=[note3_previous_id],
    ocr_corrections=corrections_l64,
)
make_statement(
    note3_cont_ids[7], BODY, "cand-2534", "cand-10462",
    "papers_and_manuscripts_mentioned_in_inquisitori_di_stato_archive_record", 64, 64,
    "The note locates a mention of Swajer's papers and manuscripts in the Archivio di Stato, Venice, Inquisitori 540, page 164, dated 30 May 1792.",
    "Haskell's note", "archival locator", "The archival record was not consulted; this reuses the existing specific citation candidate.",
    ["cand-2534", "cand-10172", "cand-10462"], note64,
    cited_source_independently_consulted=False, footnote_marker="3", footnote_segment=NOTES,
    footnote_line_range="L84-L84", footnote_text_pending=False, footnote_body_link_status="linked",
    footnote_body_line_range="L46", footnote_note_statement_ids=[note3_previous_id],
)

# P.377 footnotes 1-5. The source prints note 5 at L89; OCR reads 6.
make_statement(
    note1_id, NOTES, "cand-10659", "cand-0622", "note_reports_celotti_died_about_1846", 85, 85,
    "Haskell's note cites Levi, volume I, page cxxxv, for a report that Celotti died about 1846.",
    "Haskell's note", "secondary citation", "The date is approximate and the cited page was not consulted.",
    ["cand-10659", "cand-8532", "cand-0622"], note85,
    cited_source_independently_consulted=False, ocr_corrections=corrections_note85, **note1_link,
)
make_statement(
    note2_id, NOTES, "cand-10660", "cand-0622", "note_cites_celotti_notice_in_gazzetta_4_may_1821", 86, 86,
    "Haskell's note cites the announcement 'Agli amatori delle Arti belle' in Gazzetta di Venezia, 4 May 1821.",
    "Haskell's note", "bibliographic locator", "The newspaper issue was not independently consulted.",
    ["cand-10660", "cand-0622", "cand-2719"], note86,
    cited_source_independently_consulted=False, **note2_link,
)
make_statement(
    note3_id, NOTES, "cand-10661", "cand-9400", "note_cites_christies_sale_26_may_1825_and_ottley_description", 87, 87,
    "Haskell's note cites Christie's, 26 May 1825, and says William Young Ottley described the miniatures.",
    "Haskell's note", "auction locator", "No lot number or sale catalogue title is supplied; neither the sale record nor Ottley's description was consulted.",
    ["cand-10661", "cand-9400", "cand-1793"], note87,
    cited_source_independently_consulted=False, **note3_link,
)
make_statement(
    note4_id, NOTES, "cand-10662", "cand-0622", "note_cites_celotti_sale_catalogue_paris_1807", 88, 88,
    "Haskell's note cites the Paris 1807 catalogue Notice de Tableaux, describing the cabinet of M. Celotti de Venise.",
    "Haskell's note", "bibliographic locator", "The catalogue was not independently consulted; page-image readings are recorded as OCR corrections only.",
    ["cand-10662", "cand-0622", "cand-4653"], note88,
    cited_source_independently_consulted=False, ocr_corrections=corrections_note88, **note4_link,
)
make_statement(
    note5_id, NOTES, "cand-10663", "cand-0622", "note_cites_celotti_sale_catalogue_14_november_1814", 89, 89,
    "Haskell's note cites an 1814 catalogue for a further sale of Tiepolo and Piazzetta works and says the bracketed Celotti wording was written in ink in the copy he saw.",
    "Haskell's note", "bibliographic locator and copy-specific observation", "The sale catalogue and annotated copy were not consulted; the printed note number is 5 although S0 reads 6.",
    ["cand-10663", "cand-0622", "cand-2569", "cand-1901"], note89,
    cited_source_independently_consulted=False, ocr_corrections=corrections_note89, **note5_link,
)

# Cross-link and complete p.376's previously partial statement and footnote.
previous_swajer["qualifiers"]["predicate_status"] = "complete"
previous_swajer["qualifiers"]["qualification"] = (
    "P.377 L49 completes the sentence: the possible dispersal caused anxiety to the Inquisitors of State, who acquired all the manuscripts."
)
previous_swajer["qualifiers"]["cross_reference_text_pending"] = False
previous_swajer["qualifiers"]["cross_reference_statement_ids"] = ["st-chp16-p377-swajer-inquisitors-conclusion"]
previous_note3["qualifiers"]["predicate_status"] = "complete"
previous_note3["qualifiers"]["qualification"] = (
    "P.377 source lines 60–64 continue note 3 with the Vannetti and Durazzo correspondence groups, two Tiepolo letters, "
    "the provenance caveat, and the Archivio di Stato locator."
)
previous_note3["qualifiers"]["cross_reference_text_pending"] = False
previous_note3["qualifiers"]["cross_reference_statement_ids"] = note3_cont_ids
previous_note3["qualifiers"]["footnote_text_pending"] = False
previous_note3["qualifiers"]["footnote_body_link_status"] = "linked"
previous_note3["qualifiers"]["footnote_link_note"] = "The p.376 note continues in the p.377 footnote block at source lines 60–64."

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L39-46",
    "note": "P.376 L46's Swajer manuscripts sentence is completed by the p.377 continuation at L49.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L49-64",
    "note": "P.377 body L49-59 and the continuation of p.376 note 3 at L60-64 are migrated; page image confirms printed page 377.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L70-89",
    "note": "Merged notes L70-84 were migrated on p.373-376; p.376 note 3 continues at p.377 L60-64; p.377 notes 1-5 at L85-89 are now migrated.",
})

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp16-p377-")]
if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidates),
        "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
        "completed_statements": [previous_swajer_id, previous_note3_id],
        "coverage": {BODY_PREV: "complete", BODY: "complete", NOTES: "complete"},
        "new_candidate_ids": [row[0] for row in new_candidates],
        "new_statement_ids": new_statement_ids,
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)

mentions.extend(planned_mentions)
write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps({
    "mode": "applied", "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
    "completed_statements": [previous_swajer_id, previous_note3_id],
    "completed_segments": [BODY_PREV, BODY, NOTES],
    "backups": [path.name + BACKUP_SUFFIX for path in (candidate_path, mention_path, statement_path, coverage_path)],
}, ensure_ascii=False))
