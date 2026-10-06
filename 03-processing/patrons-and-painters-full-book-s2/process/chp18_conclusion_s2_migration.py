"""Controlled S2 migration for the two-page conclusion, printed pp.384-385."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "18_CHP-18Conclusion.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-18Conclusion.pdf"
EXPECTED_HASHES = {
    SOURCE: "a3d40952beead96ac48136610fa3fa15f1dcdfcd1a354ef9f2c2262343aeff14",
    PDF: "750ba8a4f4e7dc72e032746f7f3b15c3c70ef97a4220491fc3aa250a91ce2e29",
}
TITLE = "chp-18:18_CHP-18Conclusion:l1-1"
P384 = "chp-18:18_CHP-18Conclusion:l3-17"
P385 = "chp-18:18_CHP-18Conclusion:l19-23"
BACKUP_SUFFIX = ".bak-s2-chp18-conclusion-20261004"

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


for path, expected in EXPECTED_HASHES.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = [
    (1, "# 18_CHP-18Conclusion"), (3, "[Page 2]"), (4, "CONCLUSION"),
    (5, "ETWEEN 1623 and 1797"), (7, "Bernini, Pietro da Cortona and Tiepolo"),
    (11, "national character"), (14, "Modern Italian historians"),
    (17, "broad culture and tolerance of Italian patrons that the"),
    (19, "[Page 385]"), (20, "answer should be sought"),
    (21, "Domenico Fetti"), (23, "fall of Venice signified"),
]
for line_number, fragment in required:
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
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (TITLE, P384, P385):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
if coverage_by_id[TITLE]["disposition"] != "queued" or coverage_by_id[TITLE]["migration_status"] != "pending":
    raise SystemExit("conclusion title coverage precondition changed")
for segment_id in (P384, P385):
    if coverage_by_id[segment_id]["disposition"] != "queued" or coverage_by_id[segment_id]["migration_status"] != "pending":
        raise SystemExit(f"conclusion content coverage precondition changed: {segment_id}")
if any(row.get("statement_id", "").startswith("st-chp18-conclusion-") for row in statements):
    raise SystemExit("conclusion statements already exist")

new_candidate_specs = [
    ("cand-10733", "Roman theocratic absolutism in Haskell's political contrast", "term", P384, 7,
     "A political order described by Haskell; not a separately named government or institution."),
    ("cand-10734", "Old and new Venetian families as a rigid oligarchic aristocracy", "term", P384, 7,
     "Collective ruling class in Haskell's contrast; no individual family is named."),
    ("cand-10735", "Social conformity in Italian art and literature (Haskell's critical problem)", "term", P384, 11,
     "Haskell's account of original artistic approaches being buried by social demands and similar conformity among writers."),
    ("cand-10736", "National character as a last-resort explanation for Italian artistic conformity", "term", P384, 11,
     "An explanatory category explicitly discussed as a last resort; the passage seeks an account beyond it."),
    ("cand-10737", "Modern Italian historians discussing conformity among contemporary writers", "term", P384, 14,
     "Unnamed collective group reported by Haskell; no individual historian is identified."),
    ("cand-10738", "Unnamed eccentric Medici prince associated with Crespi", "person", P384, 11,
     "The source gives only the role and characterization; identity is not inferred from the later Grand Prince Ferdinand comparison."),
    ("cand-10739", "Unnamed nephews of Urban VIII in Haskell's tolerance comparison", "term", P384, 14,
     "Collective reference only; the source does not name the nephews."),
    ("cand-10740", "Traditional and upstart aristocracy of Baroque Italy", "term", P385, 20,
     "Collective social order in Haskell's analogy; no single family or institution is intended."),
    ("cand-10741", "Artistic unorthodoxy in Haskell's account of Italy", "term", P385, 20,
     "Interpretive category in the phrase 'Unorthodoxy was killed with kindness'; no specific person or doctrine is named."),
    ("cand-10742", "Bourgeois painting in England and France", "term", P385, 23,
     "Historical category as described by Haskell; no particular school or work is identified."),
    ("cand-10743", "Feudal aristocracy in Haskell's England and France comparison", "term", P385, 23,
     "Collective social order; no particular family or political body is named."),
    ("cand-10744", "Artists and creative practitioners discussed collectively in Haskell's conclusion", "term", P384, 6,
     "Collective reference spanning unnamed architects, sculptors, painters and artists; it does not replace the named artists."),
    ("cand-10745", "Political authorities employing artists in Rome and Venice (unnamed collective)", "term", P384, 6,
     "Haskell identifies authorities by role and city only; no government or office is named."),
]
if any(spec[0] in candidate_by_id for spec in new_candidate_specs):
    raise SystemExit("one or more conclusion candidate IDs already exist")
for cid, name, suggested_type, source_segment, source_line, detail in new_candidate_specs:
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{source_segment}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

candidate_keys = [
    "|".join((row.get("canonical_name", "").strip().casefold(), row.get("suggested_type", "").strip().casefold()))
    for row in candidates if not row.get("index_entry_id") and row.get("suggested_type")
]
if len(candidate_keys) != len(set(candidate_keys)):
    raise SystemExit("candidate natural-key collision in current or planned candidates")

required_existing_candidates = [
    "cand-0295", "cand-0342", "cand-2569", "cand-2709", "cand-2117", "cand-1377",
    "cand-1346", "cand-1984", "cand-2804", "cand-0649", "cand-0173", "cand-2236",
    "cand-0871", "cand-0498", "cand-1411", "cand-1896", "cand-0209", "cand-2189",
    "cand-2036", "cand-1787", "cand-0894", "cand-1139", "cand-1609", "cand-0041",
    "cand-1033", "cand-1838", "cand-4490", "cand-2719", "cand-3398", "cand-1722",
    "cand-3461", "cand-3462", "cand-8983", "cand-5317", "cand-4129", "cand-4132",
    "cand-3569", "cand-9606", "cand-7730",
]
missing_candidates = [cid for cid in required_existing_candidates if cid not in candidate_by_id]
if missing_candidates:
    raise SystemExit(f"required existing candidates missing: {missing_candidates}")

segment_lines = {
    P384: {number: source_lines[number - 1] for number in range(3, 18)},
    P385: {number: source_lines[number - 1] for number in range(19, 24)},
}
segment_texts = {sid: "\n".join(lines.values()) for sid, lines in segment_lines.items()}
line_offsets = {}
for sid, lines in segment_lines.items():
    line_offsets[sid] = {}
    offset = 0
    for number, text in lines.items():
        line_offsets[sid][number] = offset
        offset += len(text) + 1

planned_mentions = []


def add_mention(candidate_id, surface, segment_id, line_number, note="", occurrence=0):
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    text = segment_lines[segment_id][line_number]
    positions = []
    cursor = 0
    while True:
        position = text.find(surface, cursor)
        if position < 0:
            break
        positions.append(position)
        cursor = position + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface not found in {segment_id} L{line_number}: {surface!r} #{occurrence + 1}")
    start = line_offsets[segment_id][line_number] + positions[occurrence]
    end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions if row["segment_id"] == segment_id]
    for other_start, other_end in occupied:
        if start < other_end and other_start < end:
            nested = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if not nested or (start, end) == (other_start, other_end):
                raise SystemExit(f"overlapping mention span: {surface!r} at {segment_id} L{line_number}")
    planned_mentions.append({
        "mention_id": f"m-chp18-conclusion-{len(planned_mentions) + 1:04d}",
        "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


# Printed p.384 (PDF physical page 1): entities, nested concepts, and cultural references.
add_mention("cand-4490", "Rome", P384, 5, "City named in the political comparison.")
add_mention("cand-2719", "Venice", P384, 5, "City named in the political comparison.")
add_mention("cand-4132", "Italian Baroque art", P384, 6, "Existing compound art-historical term; nested Italy and Baroque mentions retained.")
add_mention("cand-3461", "Italian", P384, 6, "Nested geographic descriptor in Italian Baroque art.")
add_mention("cand-3569", "Baroque", P384, 6, "Nested period/category mention in Italian Baroque art.")
add_mention("cand-4490", "Rome", P384, 7, "City as the setting for the stated theocratic political order.")
add_mention("cand-10733", "theocratic absolutism", P384, 7, "Political system described by Haskell; not a named institution.")
add_mention("cand-2719", "Venice", P384, 7, "City in the contrast with Roman authority.")
add_mention("cand-10734", "the old and new families that composed a rigid oligarchic aristocracy", P384, 7, "Collective Venetian ruling class; no specific family is named.")
add_mention("cand-10744", "architects, sculptors and painters of the first rank", P384, 6, "Unnamed collective of practitioners employed by authorities.")
add_mention("cand-10745", "those in authority", P384, 6, "Unspecified employing authorities in Rome and Venice.")
add_mention("cand-0295", "Bernini", P384, 7, "Index candidate points to p.384; source gives surname only.")
add_mention("cand-0342", "Pietro da Cortona", P384, 7, "Index candidate points to p.384.")
add_mention("cand-2569", "Tiepolo", P384, 7, "Surname form; identity is deferred to global S3 alignment.")
add_mention("cand-10744", "great artists", P384, 7, "Collective reference to artistic practitioners, alongside named examples.")
add_mention("cand-4129", "great patrons", P384, 7, "General patron category, not a named patron.")
add_mention("cand-3461", "Italian", P384, 7, "Nested geographic descriptor in the claimed Italian contribution.")
add_mention("cand-2709", "Velasquez", P384, 7, "Source spelling retained; index candidate points to p.385, where the reference is listed.")
add_mention("cand-2117", "Rembrandt", P384, 7, "Index candidate points to p.384.")
add_mention("cand-2752", "Vermeer", P384, 8, "Index candidate points to p.384.")
add_mention("cand-1377", "Louis Le Nain", P384, 8, "Existing candidate used in a prior S2 passage; source spelling retained.")
add_mention("cand-1346", "Georges de la Tour", P384, 8, "Index candidate points to p.384.")
add_mention("cand-1984", "Poussin", P384, 8, "Index candidate points to p.384.")
add_mention("cand-2804", "Watteau", P384, 8, "Index candidate points to p.384.")
add_mention("cand-0649", "Chardin", P384, 8, "Index candidate points to p.384.")
add_mention("cand-3461", "Italian", P384, 10, "Geographic descriptor in the account of Italian art.")
add_mention("cand-10735", "the pressing claims of society", P384, 11, "Phrase anchoring Haskell's account of social conformity and suppressed originality.")
add_mention("cand-10736", "‘national character’", P384, 11, "Quoted explanatory category; Haskell says an answer beyond this last resort should be sought.")
add_mention("cand-0173", "bamboccianti", P384, 11, "Collective artistic group/category in Haskell's example.")
add_mention("cand-2236", "Salvator Rosa", P384, 11, "Index candidate points to p.384.")
add_mention("cand-0871", "Crespi", P384, 11, "Index candidate points to p.384; source gives surname only.")
add_mention("cand-10738", "an eccentric Medici prince", P384, 11, "Unnamed person; not identified as the later-mentioned Grand Prince Ferdinand.")
add_mention("cand-9606", "genre painting", P384, 12, "Existing category for the art form; Haskell's evaluative framing is retained.")
add_mention("cand-0498", "Canaletto", P384, 12, "Index candidate points to p.384.")
add_mention("cand-2719", "his native city", P384, 12, "Anaphoric reference to Venice in the Canaletto clause.")
add_mention("cand-1411", "Padre Lodoli", P384, 12, "Existing candidate for Padre Carlo Lodoli; source retains the honorific.")
add_mention("cand-10735", "conformity in the writers of the time", P384, 14, "Second part of Haskell's conformity argument, now concerning writers.")
add_mention("cand-10737", "Modern Italian historians", P384, 14, "Unnamed collective group reported by Haskell.")
add_mention("cand-3462", "Europe", P384, 14, "Geographic frame of the rhetorical comparison.")
add_mention("cand-1896", "Philip IV", P384, 14, "Index candidate points to p.384.")
add_mention("cand-0209", "Urban VIII", P384, 14, "Existing candidate for Maffeo Barberini; index entry does not list this conclusion page.")
add_mention("cand-10739", "his nephews", P384, 14, "Unnamed collective referent to Urban VIII's nephews; no individuals inferred.")
add_mention("cand-2189", "Richelieu", P384, 14, "Index candidate points to p.384.")
add_mention("cand-2036", "Cassiano dal Pozzo", P384, 14, "Index candidate points to p.384.")
add_mention("cand-1787", "the Regent", P384, 15, "Index subentry points to p.384; identity remains part of global alignment.")
add_mention("cand-0894", "Crozat", P384, 15, "Index candidate points to p.384.")
add_mention("cand-1139", "Mme Geofirin", P384, 15, "S0 OCR form; p.384 image reads Mme Geoffrin, correction recorded below.")
add_mention("cand-1609", "Grand Prince Ferdinand", P384, 15, "Index candidate points to pp.384-385.")
add_mention("cand-0041", "Francesco", P384, 15, "First part of a name split across the page's wrapped lines.")
add_mention("cand-0041", "Algarotti", P384, 16, "Second part of the name split across L15-L16; identity reconciliation remains S3 work.")
add_mention("cand-4129", "Italian patrons", P384, 17, "General class of art patrons, not an individual or family.")
add_mention("cand-3461", "Italian", P384, 17, "Nested geographic descriptor in the patron category.")

# Printed p.385 (PDF physical page 2): continuation and final argument.
add_mention("cand-10740", "the aristocracy, traditional and upstart, of Baroque Italy", P385, 20, "Collective social order in Haskell's analogy; no specific family is named.")
add_mention("cand-10744", "the artists mentioned above", P385, 20, "Anaphoric collective reference to artists discussed on p.384; it does not specify one artist.")
add_mention("cand-3461", "Italy", P385, 20, "Nested location in Baroque Italy.")
add_mention("cand-10741", "Unorthodoxy", P385, 20, "Haskell's interpretive term; not an identified individual or movement.")
add_mention("cand-1033", "Domenico Fetti", P385, 21, "Source spells Fetti; the p.385 index candidate spells Feti, retained for S3 reconciliation.")
add_mention("cand-3461", "Italy", P385, 21, "Geographic frame of the comparison of artistic traditions.")
add_mention("cand-4490", "Rome", P385, 21, "City named as an important centre of painting.")
add_mention("cand-3398", "Bologna", P385, 22, "Existing city candidate; location in the comparative list of painting centres.")
add_mention("cand-1722", "Naples", P385, 22, "Existing city candidate; location in the comparative list of painting centres.")
add_mention("cand-2719", "Venice", P385, 22, "City named as an important centre of painting.")
add_mention("cand-3462", "Europe", P385, 22, "Geographic scope of the comparison with other towns.")
add_mention("cand-3461", "Italy", P385, 22, "Geographic scope of the claim about patrons' opportunities and the art galleries of the world.")
add_mention("cand-4129", "liberal patrons", P385, 22, "General patron category in Haskell's evaluative conclusion.")
add_mention("cand-10744", "architects, painters and sculptors", P385, 22, "Collective group receiving opportunities and encouragement.")
add_mention("cand-10742", "‘bourgeois’ painting", P385, 23, "Historical category as written by Haskell; quoted qualification retained.")
add_mention("cand-8983", "England", P385, 23, "Place/cultural geography in the painting comparison; not a government actor here.")
add_mention("cand-5317", "France", P385, 23, "Place/cultural geography in the painting comparison; not a government actor here.")
add_mention("cand-3461", "Italy", P385, 23, "Geographic frame in the phrase about Italian roots.")
add_mention("cand-1838", "Academy at Parma", P385, 23, "Index candidate points to p.385; Haskell describes an unsuccessful reform effort.")
add_mention("cand-7730", "the Church", P385, 23, "Unqualified institutional referent; no denomination or specific institution is inferred.")
add_mention("cand-10743", "feudal aristocracy", P385, 23, "Collective social order in Haskell's comparison; no individual family is named.")
add_mention("cand-5317", "France", P385, 23, "Repeated in the final France/England comparison.", occurrence=1)
add_mention("cand-8983", "England", P385, 23, "Repeated in the final France/England comparison.", occurrence=1)
add_mention("cand-2719", "Venice", P385, 23, "Political-cultural place in Haskell's final characterization of the Republic's fall.")
add_mention("cand-3461", "Italian", P385, 23, "Geographic descriptor in the phrase 'Italian art'.")


def quote_for(segment_id, start_line, end_line):
    return "\n".join(segment_lines[segment_id][number] for number in range(start_line, end_line + 1))


new_statement_ids = []
ocr_p384 = [
    {"source_line": 5, "ocr": "ETWEEN", "print": "BETWEEN", "basis": "CHP-18Conclusion.pdf physical page 1, printed p.384; drop-cap initial B was displaced by OCR."},
    {"source_line": 6, "ocr": "Bvital", "print": "vital", "basis": "CHP-18Conclusion.pdf physical page 1, printed p.384; displaced drop-cap B belongs before L5 ETWEEN."},
    {"source_line": 7, "ocr": "with-what", "print": "with what", "basis": "CHP-18Conclusion.pdf physical page 1, printed p.384."},
    {"source_line": 11, "ocr": "Efe", "print": "life", "basis": "CHP-18Conclusion.pdf physical page 1, printed p.384."},
    {"source_line": 11, "ocr": "of‘national", "print": "of ‘national", "basis": "CHP-18Conclusion.pdf physical page 1, printed p.384."},
]
ocr_p384_lodoli = [
    {"source_line": 13, "ocr": "- - plosive", "print": "explosive", "basis": "CHP-18Conclusion.pdf physical page 1, printed p.384; line-break hyphen and OCR noise."},
    {"source_line": 13, "ocr": "published. .", "print": "published.", "basis": "CHP-18Conclusion.pdf physical page 1, printed p.384; trailing marks are scan/OCR noise."},
]
ocr_p384_comparison = [
    {"source_line": 14, "ocr": "difficult To", "print": "difficult to", "basis": "CHP-18Conclusion.pdf physical page 1, printed p.384."},
    {"source_line": 15, "ocr": "Geofirin", "print": "Geoffrin", "basis": "CHP-18Conclusion.pdf physical page 1, printed p.384."},
]
ocr_p385 = [
    {"source_line": 20, "ocr": "above-was", "print": "above was", "basis": "CHP-18Conclusion.pdf physical page 2, printed p.385."},
]


def make_statement(suffix, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, text_layer, qualification, mentioned_ids, relation_candidate=False,
                   extra=None):
    statement_id = f"st-chp18-conclusion-{suffix}"
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 384 if segment_id == P384 else 385,
        "pdf_physical_page": 1 if segment_id == P384 else 2,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned_ids,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if extra:
        qualifiers.update(extra)
    statements.append({
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject_id, "object_candidate_id": object_id,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote_for(segment_id, start_line, end_line),
        "origin": "book", "source_file": "02-sources/02-Markdown/18_CHP-18Conclusion.md",
    })
    new_statement_ids.append(statement_id)


make_statement("p384-political-decline", P384, "cand-4490", "cand-2719",
    "political_decline_nearly_continuous_1623_1797", 5, 7,
    "Haskell says the political decline of Rome and Venice between 1623 and 1797 was almost continuous.",
    "authorial historical interpretation", "The period and degree are stated by Haskell; this is not independently verified.",
    ["cand-4490", "cand-2719"], extra={"ocr_corrections": ocr_p384})
make_statement("p384-authorities-and-artists", P384, None, None,
    "authorities_employed_leading_artists_to_project_power", 6, 7,
    "Haskell says authorities in Rome and Venice employed leading architects, sculptors and painters to impress themselves and foreigners with images of power.",
    "authorial historical interpretation", "The passage contrasts changing theocratic absolutism in Rome with Venice's old and new oligarchic families; it names no individual commission or official.",
    ["cand-4490", "cand-2719", "cand-10733", "cand-10734", "cand-10744", "cand-10745"], relation_candidate=True,
    extra={"relation_candidate_note": "Collective employment claim; authorities and practitioners are not individually named, so this is not a direct formal edge."})
make_statement("p384-artists-serving-patrons", P384, None, None,
    "achievements_show_artists_served_great_patrons_despite_unpromising_causes", 7, 7,
    "Haskell presents the achievements of Bernini, Pietro da Cortona and Tiepolo as evidence that great artists could serve great patrons with conviction and genius even when the cause seemed unpromising.",
    "authorial evaluative interpretation", "This is a collective argument, not evidence of a particular commission or relationship between each named artist and a named patron.",
    ["cand-0295", "cand-0342", "cand-2569", "cand-10744", "cand-4129"], relation_candidate=True,
    extra={"relation_candidate_note": "General statement about artists serving patrons; no specific patronage link is established for each named artist."})
make_statement("p384-italian-art-contribution", P384, None, None,
    "achievements_represent_finest_italian_contribution_to_period_art", 7, 7,
    "Haskell says these achievements and similar works represent the finest Italian contribution to the art of the period, a significance clarified by comparison with foreign artists.",
    "authorial evaluative interpretation", "The superlative is Haskell's judgment; no objective ranking is asserted.",
    ["cand-4132", "cand-3461"])
make_statement("p384-foreign-artists-and-individual-outlook", P384, None, None,
    "foreign_artists_expressed_private_outlooks_far_from_italian_public_masterpieces", 8, 9,
    "Haskell says Velasquez, Rembrandt, Vermeer, Louis Le Nain, Georges de la Tour, Poussin, Watteau and Chardin had no Italian equivalents and expressed private, individual outlooks far removed from the public masterpieces of the greatest Italians.",
    "authorial comparative interpretation", "The claim is Haskell's comparative art-historical argument, not an independently tested absence claim.",
    ["cand-2709", "cand-2117", "cand-2752", "cand-1377", "cand-1346", "cand-1984", "cand-2804", "cand-0649"])
make_statement("p384-social-demands-and-originality", P384, None, None,
    "social_claims_buried_fresh_original_approaches_in_italian_art", 10, 11,
    "Haskell allows that talent may be fortuitously distributed but says repeated cases in Italian art show fresh and original approaches buried by society's demands, prompting an explanation beyond national character.",
    "authorial explanatory interpretation", "The wording presents a line of argument and examples, not a measured causal result.",
    ["cand-3461", "cand-10735", "cand-10736"])
make_statement("p384-bamboccianti", P384, "cand-0173", None,
    "bamboccianti_moved_from_emerging_realism_to_sentimentality", 11, 11,
    "Haskell says the bamboccianti hovered for a few years near a new, dignified realism but fell into picturesque sentimentality.",
    "authorial characterization", "The group and trajectory are described by Haskell; no individual member is identified.",
    ["cand-0173", "cand-10735"])
make_statement("p384-salvator-rosa", P384, "cand-2236", None,
    "salvator_rosa_used_gifted_temperament_in_artistic_conformity", 11, 11,
    "Haskell characterizes Salvator Rosa as exploiting his gifted temperament in the cause of artistic conformity.",
    "authorial characterization", "This is Haskell's evaluative framing, not a claim about Rosa's stated intention.",
    ["cand-2236", "cand-10735"])
make_statement("p384-crespi-and-medici-prince", P384, "cand-0871", "cand-10738",
    "crespi_carried_along_an_eccentric_medici_prince_but_did_not_elevate_genre", 11, 12,
    "Haskell says Crespi could carry an eccentric Medici prince along with him but was not prepared to abandon humour and raise genre painting to a more noble status.",
    "authorial characterization", "The prince remains unnamed; 'carry along' is not expanded into a specific commission or patronage relationship.",
    ["cand-0871", "cand-10738", "cand-9606"], relation_candidate=True)
make_statement("p384-canaletto-tourist-views", P384, "cand-0498", "cand-4490",
    "canaletto_shifted_from_observant_city_backwaters_to_tourist_shorthand", 12, 12,
    "Haskell says Canaletto turned from close observation of the backwaters of his native city to stereotyped shorthand versions of familiar views for tourists.",
    "authorial characterization", "The native city is Venice by anaphora; the shift and judgment are Haskell's account.",
    ["cand-0498", "cand-4490"])
make_statement("p384-lodoli", P384, "cand-1411", None,
    "lodoli_honoured_with_official_post_but_writings_unpublished", 12, 13,
    "Haskell calls Padre Lodoli the scourge of society, notes that he held an official government post, and says his explosive writings were never published.",
    "authorial characterization and report", "The office and writings are not individually identified; OCR line-break corrections are recorded in S2.",
    ["cand-1411"], extra={"ocr_corrections": ocr_p384_lodoli})
make_statement("p384-historians-and-writers", P384, "cand-10737", None,
    "modern_italian_historians_noted_and_resented_writer_conformity", 14, 14,
    "Haskell says modern Italian historians had noted and bitterly resented the same kind of conformity among writers of the period.",
    "authorial report", "The historians and writers are unnamed; 'the same kind' refers to the earlier conformity argument.",
    ["cand-10737", "cand-10735", "cand-3461"])
make_statement("p384-patron-comparison-question", P384, None, None,
    "rhetorically_compared_tolerance_and_education_of_named_patrons", 14, 16,
    "Haskell rhetorically asks whether Philip IV was more tolerant or educated than Urban VIII and his nephews, whether Richelieu surpassed Cassiano dal Pozzo, and whether the Regent, Crozat or Mme Geoffrin surpassed Grand Prince Ferdinand or Francesco Algarotti.",
    "authorial rhetorical questions", "The question form is preserved; it does not assert a settled ranking. 'Geofirin' in S0 is corrected to 'Geoffrin' from the page image.",
    ["cand-1896", "cand-0209", "cand-10739", "cand-2189", "cand-2036", "cand-1787", "cand-0894", "cand-1139", "cand-1609", "cand-0041", "cand-3462"],
    extra={"ocr_corrections": ocr_p384_comparison})

make_statement("p385-culture-and-inherited-values", P385, None, None,
    "broad_patron_culture_may_have_stifled_revolt_through_inherited_values", 20, 20,
    "Closing a sentence begun on p.384 L17, Haskell suggests that the broad culture and tolerance of Italian patrons may have stifled artistic revolt through the self-assurance of inherited values, like humane parents whose views paralyse children without direct pressure.",
    "authorial explanatory analogy", "The causal statement is expressly tentative ('may have'); this closes p.384 L17. 'Above-was' is corrected to 'above was' in S2.",
    ["cand-4129", "cand-3461", "cand-10740", "cand-10744"], relation_candidate=True,
    extra={"continuation_from_segment_id": P384, "continuation_source_line_range": "L17-L17", "ocr_corrections": ocr_p385})
make_statement("p385-no-specific-pressure-or-doctrine", P385, None, None,
    "no_specific_pressure_or_orthodox_body_deflected_artists_in_italy", 20, 20,
    "Haskell says none of the artists named above was deflected by specific pressures and that no orthodox Academy or dominant religious organisation imposed artistic doctrines in Italy; he concludes that unorthodoxy was killed with kindness.",
    "authorial historical interpretation", "The academy and religious organisation are unnamed; this is Haskell's generalization, not a finding about every institution.",
    ["cand-10740", "cand-3461", "cand-10741", "cand-10744"], relation_candidate=True,
    extra={"ocr_corrections": ocr_p385, "relation_candidate_note": "Contains a negative collective claim about specific pressure and artistic doctrine; retain as a candidate assertion, not a formal edge."})
make_statement("p385-fetti-and-centres", P385, "cand-1033", None,
    "fetti_exception_to_withdrawn_artist_type_and_high_italian_painting_level", 21, 21,
    "Haskell calls Domenico Fetti the most beautiful exception to the relatively withdrawn artist absent in Italy, and says painting in Rome, Bologna, Naples and Venice was better than in almost any other European town.",
    "authorial comparative evaluation", "The claim and exception are Haskell's evaluation; the index spelling 'Feti' differs from the printed/source form 'Fetti' and is left for S3.",
    ["cand-1033", "cand-3461", "cand-4490", "cand-3398", "cand-1722", "cand-2719", "cand-3462"])
make_statement("p385-opportunities-and-patrons", P385, None, "cand-4129",
    "opportunities_for_artists_rarely_equalled_and_patron_debt_visible_worldwide", 22, 22,
    "Haskell says opportunities and encouragement for architects, painters and sculptors were rarely equalled and that the debt to liberal patrons could be seen in art galleries worldwide.",
    "authorial evaluative interpretation", "This is a collective assessment; no individual commission or gallery is identified.",
    ["cand-4129", "cand-3461", "cand-3462", "cand-10744"], relation_candidate=True,
    extra={"relation_candidate_note": "Collective encouragement by unspecified patrons to practitioner classes; no individual edge is asserted."})
make_statement("p385-social-collapse-and-adaptation", P385, None, None,
    "artists_tied_to_patronage_society_failed_to_adapt_after_its_collapse", 23, 23,
    "Haskell argues that artists closely tied to a particular patronage society could not adapt when that society's foundations collapsed.",
    "authorial historical interpretation", "The social model and causal explanation are Haskell's argument.",
    ["cand-10740", "cand-10744"], relation_candidate=True,
    extra={"relation_candidate_note": "General dependence of artists on a patronage society; no specific patron or artist pair is identified."})
make_statement("p385-bourgeois-painting-and-parma-academy", P385, "cand-1838", None,
    "bourgeois_painting_lacked_italian_roots_and_parma_academy_reform_failed", 23, 23,
    "Haskell says bourgeois painting in England and France had no real roots in Italy and that efforts by bodies such as the Academy at Parma to promote more modern, enlightened art had little success.",
    "authorial historical interpretation", "The Academy's effort is not described as a specific work or formal commission; the named category and outcome are those of Haskell.",
    ["cand-10742", "cand-8983", "cand-5317", "cand-3461", "cand-1838"], relation_candidate=True,
    extra={"relation_candidate_note": "The Academy's described effort to promote an artistic category is a general institutional action; no individual work or artist is named."})
make_statement("p385-france-england-and-fall-of-venice", P385, "cand-2719", None,
    "painting_renewed_in_france_england_but_venice_fall_signalled_italian_art_expiry", 23, 23,
    "Haskell contrasts the renewal of painting in France and England as Church and feudal aristocracy declined with the fall of Venice, which he calls the humiliating expiry of Italian art.",
    "authorial comparative interpretation", "This is Haskell's sweeping conclusion; 'the Church' is retained as an unqualified institutional referent and no single political actor is inferred.",
    ["cand-5317", "cand-8983", "cand-7730", "cand-10743", "cand-2719", "cand-3461"])

if len({row["mention_id"] for row in planned_mentions}) != len(planned_mentions):
    raise SystemExit("duplicate planned mention IDs")
if any(row["mention_id"] in {item["mention_id"] for item in mentions} for row in planned_mentions):
    raise SystemExit("one or more conclusion mention IDs already exist")
for row in planned_mentions:
    if row["candidate_id"] not in candidate_by_id:
        raise SystemExit(f"missing candidate for {row['mention_id']}")
    text = segment_texts[row["segment_id"]]
    start, end = int(row["start_char"]), int(row["end_char"])
    if text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span failed exact-source check: {row['mention_id']}")
for row in statements:
    if row.get("statement_id", "").startswith("st-chp18-conclusion-"):
        for key in ("subject_candidate_id", "object_candidate_id"):
            value = row.get(key)
            if value and value not in candidate_by_id:
                raise SystemExit(f"missing {key} in {row['statement_id']}: {value}")
        qualifiers = row.get("qualifiers", {})
        segment_id = row["segment_id"]
        if row["original_quote"] != quote_for(segment_id, qualifiers["source_line_start"], qualifiers["source_line_end"]):
            raise SystemExit(f"original quote does not match source lines: {row['statement_id']}")

statement_keys = []
for row in statements:
    qualifiers = row.get("qualifiers", {})
    claim = qualifiers.get("claim") or qualifiers.get("attribution") or row.get("original_quote", "")
    normalized_claim = " ".join(str(claim).split()).casefold()
    if normalized_claim:
        statement_keys.append(f"{row.get('segment_id', '')}|{normalized_claim}")
if len(statement_keys) != len(set(statement_keys)):
    raise SystemExit("book-statement natural-key collision in current or planned rows")

coverage_by_id[TITLE].update({
    "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "L1-1",
    "note": "Generated Markdown filename heading only; not printed book content. Printed conclusion starts at L3; no independent claim or entity is present.",
})
coverage_by_id[P384].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-17",
    "note": "Printed p.384 checked against CHP-18Conclusion.pdf physical page 1. Conclusion prose, named entities, argument, and OCR corrections are migrated; final clause at L17 closes on printed p.385 L20.",
})
coverage_by_id[P385].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L19-23",
    "note": "Printed p.385 checked against CHP-18Conclusion.pdf physical page 2. Closes p.384 L17; final conclusion claims and S2 OCR correction are recorded. No footnotes appear on either conclusion page.",
})

if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidate_specs),
        "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
        "coverage_updates": {TITLE: "excluded", P384: "complete", P385: "complete"},
        "candidate_ids": [item[0] for item in new_candidate_specs],
        "closed_cross_page_sentence": "p.384 L17 closed by p.385 L20",
        "ocr_correction_groups": {"p384_body": len(ocr_p384), "p384_lodoli": len(ocr_p384_lodoli), "p384_comparison": len(ocr_p384_comparison), "p385": len(ocr_p385)},
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup.name}")
    shutil.copy2(path, backup)

mentions.extend(planned_mentions)
write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps({"mode": "applied", "candidates": len(new_candidate_specs), "mentions": len(planned_mentions), "statements": len(new_statement_ids)}, ensure_ascii=False))
