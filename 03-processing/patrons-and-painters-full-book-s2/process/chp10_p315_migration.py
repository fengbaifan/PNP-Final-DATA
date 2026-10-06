"""Controlled S2 migration for printed p.315 body; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l95-106"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l83-93"
NEXT_SEGMENT = "chp-10:10_CHP-10_sec_ii:l108-117"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "a7b8312b42cdedc92fa755183840f9878b7ed889c480b980a755f7aef840c6c0"
BACKUP_SUFFIX = ".bak-s2-chp10-p315-20261003"
PREVIOUS_SHIPPING_ID = "st-chp10-p314-schulenburg-picture-shipping-to-estates-fragment"
P315_CONTINUATION_ID = "st-chp10-p315-schulenburg-estates-in-germany-continuation"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.315 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[94:106]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 source segment changed")
if segment_lines[0] != "[Page 315]" or not segment_lines[-1].endswith("which he made about"):
    raise SystemExit("p.315 segment boundaries changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
table_state = (len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates), len(mentions), len(statements))
if table_state != (9612, 9625, 20174, 8916):
    raise SystemExit(f"table state changed; re-read current table counts before migration: {table_state}")

REQUIRED = {
    "schulenburg": "cand-2401", "smith": "cand-2440", "streit": "cand-2519",
    "sebastiano_ricci": "cand-2154", "carriera": "cand-0581", "canaletto": "cand-3738",
    "piazzetta": "cand-3862", "pittoni": "cand-3870", "guardi": "cand-1245",
    "marco_ricci": "cand-3831", "zuccarelli": "cand-2879", "tiepolo": "cand-2569",
    "amigoni": "cand-0099", "frederick": "cand-1079", "germany": "cand-5529",
    "berlin": "cand-4623", "venice": "cand-3401", "padua": "cand-1803",
    "schulenburg_collection": "cand-9622", "schulenburg_estates": "cand-9623",
    "shipped_picture_group": "cand-9625",
}
for label, candidate_id in REQUIRED.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required candidate missing: {label}={candidate_id}")

coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.315 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.314 segment to remain partial pending its notes")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.315 already has S2 mention or statement rows")

new_candidates = []


def add_candidate(candidate_id, canonical_name, suggested_type, detail, source_line):
    if candidate_id in candidate_ids or any(row["candidate_id"] == candidate_id for row in new_candidates):
        raise SystemExit(f"candidate id already exists: {candidate_id}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": canonical_name,
        "suggested_type": suggested_type,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{source_line}",
    })
    new_candidates.append(row)


add_candidate("cand-9626", "Joseph Smith’s picture collection in Haskell’s p.315 comparison", "", "Collection as a body of pictures, distinct from Joseph Smith as a person; the current taxonomy has no collection type.", 96)
add_candidate("cand-9627", "Sigismund Streit’s picture collection described on p.315", "", "The source treats his pictures as a collection and later says he bequeathed those he had acquired; collection type remains unresolved.", 103)
add_candidate("cand-9628", "Forty-eight pictures owned by Sigismund Streit", "work", "Haskell gives the total as forty-eight; individual works are not enumerated in this passage.", 103)
add_candidate("cand-9629", "Pictures by Sebastiano Ricci, Rosalba Carriera, and Canaletto forming much of Smith’s collection", "work", "A group identified by makers and relative prominence; individual titles and counts are not given.", 96)
add_candidate("cand-9630", "Works by Ricci, Carriera, and Canaletto weakly represented in Schulenburg’s collection", "work", "Haskell contrasts their weak representation with their prominence in Smith’s collection; he separately notes a portrait and some Ricci paintings.", 97)
add_candidate("cand-9631", "Works by Piazzetta, Pittoni, and Gian Antonio Guardi in Schulenburg’s collection", "work", "Haskell calls Schulenburg’s collection rich in works by these three painters; individual titles are not supplied here.", 98)
add_candidate("cand-9632", "Works by Marco Ricci and Zuccarelli held across Smith’s and Schulenburg’s collections", "work", "The source says both men owned works by both painters, with Smith having a far greater number; the works in the two collections are not identified as the same objects.", 98)
add_candidate("cand-9633", "Four Canaletto paintings owned by Sigismund Streit", "work", "A group of four pictures; two are further described as scenes directly concerned with Streit’s life.", 106)
add_candidate("cand-9634", "Two Canaletto scenes directly concerned with Sigismund Streit’s life", "work", "A subset of the four Canalettos; the source attributes the life connection to Streit’s own notes, which continue on p.316.", 106)
add_candidate("cand-9635", "Pictures in Streit’s collection painted to celebrate Venice’s beauties and traditions", "work", "Haskell says a strikingly high proportion of the collection had this subject; no titles or count are supplied.", 106)
add_candidate("cand-9636", "Amigoni portrait of Sigismund Streit", "work", "Named as Amigoni’s portrait in the p.315 prose and captioned ‘Amigoni: Sigismund Streit’ on Plate 53b; object identity is source-level only.", 105)
add_candidate("cand-9637", "Sigismund Streit’s long notes about his pictures", "archive", "Haskell says Streit recorded the personal-life connection of two Canaletto scenes in long notes; title, date, and repository are not given here.", 106)
add_candidate("cand-9638", "Gymnasium zum Grauen Kloster in Berlin", "institution", "Named as the institution that received Streit’s pictures and where he had been educated.", 104)
add_candidate("cand-9639", "Various institutions that received pictures bequeathed by Streit", "", "The recipient group is not enumerated; the Gymnasium zum Grauen Kloster is singled out as especially important.", 104)
add_candidate("cand-9640", "Protestant cemetery of S. Cristoforo", "place", "Named as Streit’s burial place; keep distinct from the Protestant cemetery at S. Niccolò al Lido mentioned elsewhere.", 104)
add_candidate("cand-9641", "Unidentified blacksmith who was Sigismund Streit’s father", "person", "The source identifies the father only by occupation; no name or further identity is supplied.", 104)
add_candidate("cand-9642", "Yearly speech arranged by Streit in Berlin in honour of Venice", "event", "A recurring speech is reported without its speaker, title, or institutional sponsor.", 106)
add_candidate("cand-9643", "Landscape and view painting as Smith’s collecting preference", "term", "Haskell calls this a characteristically English penchant; it is his characterization, not an independently established national trait.", 99)
add_candidate("cand-9644", "History, portrait, and genre painting as Schulenburg’s collecting preference", "term", "The three categories are grouped by Haskell as a contrast with Smith’s landscape and view preference.", 99)
add_candidate("cand-9645", "Portrait and paintings of Sebastiano Ricci owned by Schulenburg (wording ambiguous)", "work", "Haskell says Schulenburg owned ‘a portrait and some paintings of Ricci’; the wording does not settle whether the portrait depicts Ricci or is by him.", 97)
add_candidate("cand-9646", "1758 and 1763 bequests of Streit’s acquired pictures", "event", "Haskell reports bequests in both years to various institutions, especially the Gymnasium zum Grauen Kloster; object-by-recipient distribution is not itemized.", 104)
add_candidate("cand-9647", "More sophisticated collectors in Haskell’s comparison with Streit", "term", "An unnamed comparative group; the source gives no members or boundaries.", 106)

candidate_ids.update(row["candidate_id"] for row in new_candidates)
new_mentions = []


def add_mention(line_no, surface, candidate_id, note="", occurrence=0):
    line = source_lines[line_no - 1]
    starts = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text not found on L{line_no}: {surface!r} occurrence {occurrence}")
    relative_line = line_no - 95
    start = sum(len(item) + 1 for item in segment_lines[:relative_line]) + starts[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch on L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p315-{len(new_mentions) + 1:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


MENTIONS = [
    (96, "Germany", "cand-5529"),
    (96, "He", "cand-2401", "Corefers to Schulenburg."),
    (96, "dozens of pictures", "cand-9625", "Continuation of the picture shipments begun in the p.314 sentence."),
    (96, "Smith’s", "cand-9626", "Refers to Joseph Smith’s collection, not to Smith as a person."),
    (97, "Sebastiano Ricci", "cand-2154"),
    (97, "Rosalba Carriera", "cand-0581"),
    (97, "Canaletto", "cand-3738"),
    (97, "rather weakly", "cand-9630", "Haskell’s comparative qualifier for these painters’ representation in Schulenburg’s collection."),
    (97, "Schulenburg’s collection", "cand-9622", "Refers to the collection compared with Smith’s."),
    (97, "he", "cand-2401", "Corefers to Schulenburg.", 1),
    (97, "a portrait and some paintings", "cand-9645", "Separate group; ‘of Ricci’ remains ambiguous as to the portrait’s subject or maker."),
    (97, "Ricci", "cand-2154", "Painter named as the subject or maker of the paintings; distinct from the earlier full-name mention.", 1),
    (97, "Rosalba", "cand-0581", "Footnote 1 follows this personal-relationship claim.", 1),
    (97, "works", "cand-9631", "Works by the three painters named immediately afterward."),
    (98, "Piazzetta", "cand-3862"),
    (98, "Pittoni", "cand-3870"),
    (98, "Gian Antonio Guardi", "cand-1245"),
    (98, "Smith", "cand-2440"),
    (98, "owned works", "cand-9632", "Collective group; works in the two collections are not identified as identical objects."),
    (98, "Marco Ricci", "cand-3831"),
    (98, "Zuccarelli", "cand-2879"),
    (98, "Tiepolo", "cand-2569"),
    (99, "Smith", "cand-2440"),
    (99, "landscape and views", "cand-9643"),
    (99, "Schulenburg", "cand-2401"),
    (99, "history, portrait and genre", "cand-9644"),
    (102, "third foreign collector long resident", "cand-2519", "The following sentence names Sigismund Streit."),
    (102, "Venice", "cand-3401"),
    (103, "Smith", "cand-2440", "Comparison with Streit and Schulenburg.", 0),
    (103, "Schulenburg", "cand-2401", "Comparison with Streit and Smith.", 0),
    (103, "Frederick the Great", "cand-1079"),
    (103, "Sigismund Streit", "cand-2519"),
    (103, "forty-eight in all", "cand-9628", "Total number of pictures stated by Haskell."),
    (103, "some were of good quality", "cand-9628"),
    (103, "Smith", "cand-2440", "Named in the comparison of similarities and differences.", 1),
    (103, "Schulenburg", "cand-2401", "Named in the comparison of similarities and differences.", 1),
    (104, "Sigismund Streit", "cand-2519"),
    (104, "Berlin", "cand-4623", "Birthplace stated by Haskell.", 0),
    (104, "a blacksmith", "cand-9641", "Unidentified father, not a named person."),
    (104, "Venice", "cand-3401", "Arrival in 1709.", 0),
    (104, "Padua", "cand-1803"),
    (104, "Venice", "cand-3401", "Winter residence after settling in Padua.", 1),
    (104, "bequeathed", "cand-9646", "Bequest activity reported for 1758 and 1763."),
    (104, "various institutions", "cand-9639", "Unnamed recipient group; the Gymnasium is singled out."),
    (104, "Gymnasium zum Grauen Kloster", "cand-9638"),
    (104, "Berlin", "cand-4623", "Location of the Gymnasium.", 1),
    (104, "Protestant cemetery of S. Cristoforo", "cand-9640"),
    (105, "Streit’s life", "cand-2519"),
    (105, "Venice", "cand-3401"),
    (105, "Amigoni’s", "cand-0099", "Artist named in the portrait attribution."),
    (105, "portrait", "cand-9636", "Work candidate supported by the p.315 prose and Plate 53b caption."),
    (105, "yearly speech", "cand-9642"),
    (106, "Berlin", "cand-4623"),
    (106, "his adopted city", "cand-3401", "Corefers to Venice."),
    (106, "the pictures he owned", "cand-9635", "The following clause identifies the subset celebrating Venice."),
    (106, "more sophisticated collectors", "cand-9647"),
    (106, "four Canalettos", "cand-9633"),
    (106, "two showed scenes which were directly concerned with his own life", "cand-9634", "Subset of the four Canalettos; the sentence continues at p.316."),
    (106, "long notes which he made about", "cand-9637", "The object is completed as ‘his pictures’ at p.316 L109."),
]
for item in MENTIONS:
    add_mention(*item)

mention_by_id = {row["mention_id"]: row for row in mentions}
caption_sitter_mention = mention_by_id.get("m-s2-ch10-plate53-0004")
if not caption_sitter_mention or caption_sitter_mention["candidate_id"] != "cand-0099":
    raise SystemExit("expected p.314 Plate 53b full sitter mention to be mapped to the Amigoni candidate")
caption_sitter_mention["candidate_id"] = "cand-2519"
caption_sitter_mention["note"] = "OCR reversed full sitter name; print caption reads Sigismund Streit. The Amigoni portrait is separately represented by cand-9636."

statement_by_id = {row["statement_id"]: row for row in statements}
plate53a = statement_by_id.get("st-chp10-plate53a-piazzetta-schulenburg-portrait")
plate53b = statement_by_id.get("st-chp10-plate53b-amigoni-sigismund-streit-portrait")
if not plate53a or not plate53b:
    raise SystemExit("expected Plate 53a and 53b caption statements")
plate53a["qualifiers"]["relation_candidate"] = True
plate53b.update({
    "subject_candidate_id": "cand-9636",
    "object_candidate_id": "cand-2519",
    "predicate": "plate_caption_identifies_portrait_of_streit_attributed_to_amigoni",
})
plate53b["qualifiers"].update({
    "claim": "The Plate 53b caption identifies an Amigoni portrait of Sigismund Streit.",
    "qualification": "The reversed OCR name is the sitter, not the artist candidate. P.315 L105 calls this Amigoni’s portrait; cand-9636 represents the work, cand-0099 the artist, and cand-2519 the sitter.",
    "mentioned_candidate_ids": ["cand-0099", "cand-2519", "cand-9636"],
    "relation_candidate": True,
})

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, relation_candidate=False, extra=None):
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored: {statement_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 315,
        "pdf_physical_page": 48,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial claim",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
    }
    if extra:
        qualifiers.update(extra)
    if any(cid not in candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


add_statement(
    P315_CONTINUATION_ID, "cand-2401", "cand-9623", "destination-of-schulenburg-picture-shipment-was-germany",
    96, 96,
    "The p.315 opening word completes the previous sentence: Schulenburg sent picture crates back to estates in Germany.",
    "Germany.",
    "Continuation of the p.314 L93 fragment; the estates are not individually named.",
    ["cand-2401", "cand-9623", "cand-5529"], True,
    {"continuation_of_statement_id": PREVIOUS_SHIPPING_ID},
)
add_statement(
    "st-chp10-p315-schulenburg-picture-shipping-frequency", "cand-2401", "cand-9625", "sent-dozens-of-pictures-to-estates-two-or-three-times-yearly-from-1735",
    96, 96,
    "Haskell says Schulenburg began this shipping practice in 1735 and thereafter sent dozens of pictures on two or three occasions every year.",
    "He began doing this in 1735, and thereafter he sent dozens of pictures on two or three occasions every year.",
    "‘This’ refers to sending picture crates to his estates; the quantities and frequency are stated approximately.",
    ["cand-2401", "cand-9623", "cand-9625"], True,
)
add_statement(
    "st-chp10-p315-smith-collection-based-on-three-painters", "cand-9626", "cand-9629", "collection-based-largely-on-works-by-ricci-carriera-and-canaletto",
    96, 97,
    "Haskell says Smith’s collection was based largely on works by Sebastiano Ricci, Rosalba Carriera, and Canaletto.",
    "Smith’s was based largely on\nSebastiano Ricci, Rosalba Carriera and Canaletto",
    "The artists are named; individual works and counts are not supplied.",
    ["cand-9626", "cand-9629", "cand-2154", "cand-0581", "cand-3738"], True,
)
add_statement(
    "st-chp10-p315-these-painters-weakly-represented-in-schulenburg", "cand-9622", "cand-9630", "weak-representation-of-works-by-the-three-painters",
    97, 97,
    "Haskell says Ricci, Carriera, and Canaletto were represented rather weakly in Schulenburg’s collection.",
    "all painters who were represented---- rather weakly in Schulenburg’s",
    "The dash sequence is preserved from OCR; the scan shows a dash at the line end. Ricci is separately qualified by the following exception.",
    ["cand-9622", "cand-9630", "cand-2154", "cand-0581", "cand-3738"], True,
    {"ocr_print_correction": "represented---- -> represented—"},
)
add_statement(
    "st-chp10-p315-schulenburg-owned-ricci-portrait-and-paintings", "cand-9622", "cand-9645", "included-portrait-and-paintings-associated-with-ricci",
    97, 97,
    "Haskell says Schulenburg owned a portrait and some paintings of Ricci, but the wording does not settle whether the portrait depicts Ricci or is by him.",
    "though he owned a portrait and some paintings of Ricci",
    "Retain the ambiguity in ‘of Ricci’; do not turn the phrase into a secure authorship or sitter claim.",
    ["cand-9622", "cand-2401", "cand-9645", "cand-2154"], True,
)
add_statement(
    "st-chp10-p315-schulenburg-good-terms-with-carriera", "cand-2401", "cand-0581", "was-on-good-terms-with",
    97, 97,
    "Haskell says Schulenburg was on good terms with Rosalba Carriera.",
    "was on good terms with Rosalba.1",
    "Footnote 1 awaits canonical note L292; its evidence is not yet migrated.",
    ["cand-2401", "cand-0581"], True,
    {"footnote_marker": 1, "pending_note_source_line": 292},
)
add_statement(
    "st-chp10-p315-schulenburg-collection-rich-in-three-painters", "cand-9622", "cand-9631", "collection-rich-in-works-by-piazzetta-pittoni-and-guardi",
    97, 98,
    "Haskell says Schulenburg’s collection was rich in works by Piazzetta, Pittoni, and Gian Antonio Guardi.",
    "Schulenburg’s collection was rich in works by\nPiazzetta, Pittoni and Gian Antonio Guardi",
    "The individual works and their number are not specified in this sentence.",
    ["cand-9622", "cand-9631", "cand-3862", "cand-3870", "cand-1245"], True,
)
add_statement(
    "st-chp10-p315-piazzetta-pittoni-guardi-not-particularly-favoured-by-smith", "cand-2440", None, "these-three-painters-not-particularly-favoured-by-smith",
    98, 98,
    "Haskell says none of Piazzetta, Pittoni, and Guardi was particularly favoured by Smith.",
    "none of whom -was particularly favoured by Smith.",
    "The source makes a qualified preference comparison, not a claim that Smith never acquired their works; the printed text has no hyphen before ‘was’.",
    ["cand-2440", "cand-3862", "cand-3870", "cand-1245"], True,
    {"ocr_print_correction": "-was -> was"},
)
add_statement(
    "st-chp10-p315-both-collections-held-marco-ricci-and-zuccarelli-works", "cand-9632", None, "both-collections-contained-works-by-marco-ricci-and-zuccarelli",
    98, 98,
    "Haskell says both Smith and Schulenburg owned works by Marco Ricci and Zuccarelli.",
    "Both men owned works by Marco Ricci and Zuccarelli",
    "Works in the two collections are not identified as the same physical objects.",
    ["cand-2440", "cand-2401", "cand-9626", "cand-9622", "cand-9632", "cand-3831", "cand-2879"], True,
)
add_statement(
    "st-chp10-p315-smith-had-greater-number-of-ricci-and-zuccarelli-works", "cand-9632", None, "smith-held-far-greater-number-than-schulenburg",
    98, 98,
    "Haskell says Smith had a far greater number of the Marco Ricci and Zuccarelli works than Schulenburg.",
    "though Smith had a far greater number",
    "No exact count is given.",
    ["cand-2440", "cand-2401", "cand-9626", "cand-9622", "cand-9632"], False,
)
add_statement(
    "st-chp10-p315-neither-collection-had-tiepolo-paintings", None, "cand-2569", "neither-collection-contained-a-tiepolo-painting",
    98, 98,
    "Haskell says neither Smith nor Schulenburg had a painting by Tiepolo, whom he calls the finest artist of the age.",
    "Neither had any painting by the finest artist of the age,-Tiepolo.",
    "This is a negative claim about both collections and retains Haskell’s evaluative superlative; OCR punctuation is preserved.",
    ["cand-2440", "cand-2401", "cand-9626", "cand-9622", "cand-2569"], True,
)
add_statement(
    "st-chp10-p315-smith-english-landscape-and-view-penchant", "cand-2440", "cand-9643", "showed-characteristically-english-penchant-for-landscape-and-views",
    99, 99,
    "Haskell characterizes Smith as showing a characteristically English penchant for landscape and views.",
    "Smith showed a characteristically English penchant for landscape and views",
    "This is Haskell’s characterization of collecting taste, not an independently established national trait.",
    ["cand-2440", "cand-9643"], False,
)
add_statement(
    "st-chp10-p315-schulenburg-history-portrait-genre-preference", "cand-2401", "cand-9644", "preferred-history-portrait-and-genre-painting",
    99, 99,
    "Haskell characterizes Schulenburg’s taste as oriented toward history, portrait, and genre painting.",
    "Schulenburg for history, portrait and genre.",
    "This is a compressed comparative statement, contrasted with Smith’s landscape and view preference.",
    ["cand-2401", "cand-9644"], False,
)
add_statement(
    "st-chp10-p315-streit-position-between-two-patrons", "cand-2519", None, "seemed-to-occupy-position-between-smith-and-schulenburg",
    102, 102,
    "Haskell says a third foreign collector, Sigismund Streit, seemed to occupy a position midway between Smith and Schulenburg.",
    "Curiously enough a third foreign collector long resident in Venice seems to hold a position midway between those of the two great patrons who have just been discussed.",
    "‘Seems’ marks Haskell’s comparative interpretation; the heading names Streit in this section.",
    ["cand-2519", "cand-3401", "cand-2440", "cand-2401"], False,
)
add_statement(
    "st-chp10-p315-streit-businessman-and-german-comparisons", "cand-2519", None, "businessman-like-smith-and-german-like-schulenburg",
    103, 103,
    "Haskell compares Streit to Smith as a businessman and to Schulenburg as a German.",
    "A businessman like Smith, a German like Schulenburg",
    "These are comparisons, not evidence that the men had the same business activities or political status.",
    ["cand-2519", "cand-2440", "cand-2401"], False,
)
add_statement(
    "st-chp10-p315-streit-close-touch-with-frederick", "cand-2519", "cand-1079", "in-close-touch-with-frederick-the-great",
    103, 103,
    "Haskell says Streit was in close touch with Frederick the Great, as Schulenburg was.",
    "like him, in close touch with Frederick the Great",
    "‘Him’ refers to Schulenburg; no more specific relationship is stated.",
    ["cand-2519", "cand-2401", "cand-1079"], True,
)
add_statement(
    "st-chp10-p315-streit-owned-forty-eight-pictures-and-little-social-impact", "cand-2519", "cand-9628", "owned-forty-eight-pictures-and-made-little-impact-on-venetian-society",
    103, 103,
    "Haskell says Streit owned forty-eight pictures, far fewer than Smith or Schulenburg, and made little impact on Venetian society.",
    "Sigismund Streit owned far fewer pictures than cither—only forty-eight in all—and made little impact on Venetian society.",
    "The scan reads ‘either’; forty-eight is the stated total. Social impact is Haskell’s assessment.",
    ["cand-2519", "cand-9628", "cand-2440", "cand-2401"], False,
    {"ocr_print_correction": "cither -> either"},
)
add_statement(
    "st-chp10-p315-some-streit-pictures-good-quality", "cand-9628", None, "some-pictures-were-of-good-quality",
    103, 103,
    "Haskell says some of Streit’s pictures were of good quality.",
    "But some were of good quality",
    "The statement is limited to some of the pictures, not the whole collection.",
    ["cand-2519", "cand-9628"], False,
)
add_statement(
    "st-chp10-p315-streit-pictures-reflect-similarities-and-differences", "cand-9628", None, "seemed-to-reflect-streits-similarities-and-differences-with-smith-and-schulenburg",
    103, 103,
    "Haskell says the pictures seemed to reflect Streit’s similarities and differences with Smith and Schulenburg, making them worth discussing.",
    "they seem to reflect so sensitively their owner’s similarities and discrepancies with Smith and Schulenburg that they are worth discussing here.2",
    "Preserve ‘seem’; footnote 2 awaits canonical note L293.",
    ["cand-9628", "cand-2519", "cand-2440", "cand-2401"], False,
    {"footnote_marker": 2, "pending_note_source_line": 293},
)
add_statement(
    "st-chp10-p315-streit-born-in-berlin-1687", "cand-2519", "cand-4623", "born-in-berlin-in-1687",
    104, 104,
    "Haskell says Sigismund Streit was born in Berlin in 1687.",
    "Sigismund Streit was born in Berlin in 1687",
    "The source gives the year and city.",
    ["cand-2519", "cand-4623"], False,
)
add_statement(
    "st-chp10-p315-streit-son-of-blacksmith", "cand-2519", "cand-9641", "son-of-an-unidentified-blacksmith",
    104, 104,
    "Haskell identifies Streit as the son of a blacksmith but does not name his father.",
    "the son of a blacksmith",
    "Do not infer the father’s identity from the occupation.",
    ["cand-2519", "cand-9641"], True,
)
add_statement(
    "st-chp10-p315-streit-came-to-venice-in-1709", "cand-2519", "cand-3401", "came-to-venice-in-1709",
    104, 104,
    "Haskell says Streit came to Venice in 1709.",
    "he came to Venice in 1709",
    "The subject is Sigismund Streit.",
    ["cand-2519", "cand-3401"], True,
)
add_statement(
    "st-chp10-p315-streit-commercial-activities-won-him-a-fortune", "cand-2519", None, "commercial-activities-won-him-a-fortune",
    104, 104,
    "Haskell says Streit engaged in commercial activities that won him a fortune.",
    "He soon began to engage in commercial activities which won him a fortune.",
    "No business, date, or amount is specified.",
    ["cand-2519"], False,
)
add_statement(
    "st-chp10-p315-streit-retirement-padua-and-winter-venice", "cand-2519", None, "retired-1750-settled-padua-1754-and-wintered-in-venice",
    104, 104,
    "Haskell says Streit retired in 1750, settled in Padua four years later, and moved to Venice only during winters.",
    "He retired in 1750 and four years later he settled in Padua, moving to Venice only during the winters.",
    "‘Four years later’ is relative to 1750 and therefore 1754; Venice is a seasonal residence.",
    ["cand-2519", "cand-1803", "cand-3401"], False,
)
add_statement(
    "st-chp10-p315-streit-began-collecting-about-ten-years-earlier", "cand-2519", "cand-9627", "seems-to-have-begun-picture-collecting-about-ten-years-earlier",
    104, 104,
    "Haskell says Streit seems to have begun collecting pictures only about ten years earlier, when already well past middle age.",
    "He seems to have begun collecting pictures only about ten years earlier when he was already well past middle age",
    "Preserve ‘seems’ and ‘about’; do not convert the relative phrase into a certain start year.",
    ["cand-2519", "cand-9627"], False,
)
add_statement(
    "st-chp10-p315-streit-bequests-of-acquired-pictures", "cand-2519", "cand-9646", "bequeathed-acquired-pictures-in-1758-and-1763-to-institutions",
    104, 104,
    "Haskell says Streit bequeathed the pictures he had acquired in 1758 and again in 1763 to various institutions, especially the Gymnasium zum Grauen Kloster.",
    "in 1758 and again in 1763 he bequeathed those he had acquired to various institutions, especially the Gymnasium zum Grauen Kloster in Berlin where he had been educated.",
    "The source does not allocate particular pictures to particular recipients; ‘especially’ is retained.",
    ["cand-2519", "cand-9628", "cand-9639", "cand-9638", "cand-4623", "cand-9646"], True,
)
add_statement(
    "st-chp10-p315-streit-educated-at-gymnasium", "cand-2519", "cand-9638", "educated-at-gymnasium-zum-grauen-kloster",
    104, 104,
    "Haskell says Streit had been educated at the Gymnasium zum Grauen Kloster in Berlin.",
    "where he had been educated",
    "‘Where’ refers to the Gymnasium zum Grauen Kloster.",
    ["cand-2519", "cand-9638", "cand-4623"], True,
)
add_statement(
    "st-chp10-p315-streit-died-1775-and-buried-at-s-cristoforo", "cand-2519", "cand-9640", "died-bachelor-in-1775-and-buried-at-s-cristoforo",
    104, 104,
    "Haskell says Streit died a bachelor in 1775 and was buried in the Protestant cemetery of S. Cristoforo.",
    "He died, a bachelor, in 1775 and was buried in the Protestant cemetery of S. Cristoforo.",
    "The named cemetery is distinct from S. Niccolò al Lido.",
    ["cand-2519", "cand-9640"], False,
)
add_statement(
    "st-chp10-p315-streit-admired-venice", "cand-2519", "cand-3401", "admired-venice-strongly",
    105, 105,
    "Haskell says one of Streit’s strongest emotions was admiration for Venice.",
    "One of the strongest emotions in Streit’s life was his admiration for Venice",
    "This is Haskell’s characterization of Streit’s attitude.",
    ["cand-2519", "cand-3401"], True,
)
add_statement(
    "st-chp10-p315-venice-transformed-streits-situation", "cand-3401", "cand-2519", "transformed-streits-situation-and-made-him-wealthy",
    105, 105,
    "Haskell says Venice transformed Streit’s situation and made him a rich and complacent figure.",
    "the city that had transformed his situation and turned him into the rich and complacent figure",
    "This is the author’s interpretive description, not an independently verified causal account.",
    ["cand-3401", "cand-2519"], False,
)
add_statement(
    "st-chp10-p315-amigoni-portrait-depicts-streit", "cand-9636", "cand-2519", "portrait-of-streit-attributed-to-amigoni",
    105, 105,
    "Haskell refers to the figure of Streit in Amigoni’s portrait.",
    "who gazes at us from Amigoni’s portrait",
    "The Plate 53b caption reads ‘Amigoni: Sigismund Streit’; the work is distinct from the artist and sitter candidates.",
    ["cand-9636", "cand-0099", "cand-2519"], True,
)
add_statement(
    "st-chp10-p315-streit-arranged-yearly-speech-in-berlin", "cand-2519", "cand-9642", "arranged-yearly-speech-in-berlin-honouring-venice",
    105, 106,
    "Haskell says Streit arranged for a yearly speech in Berlin in honour of Venice, his adopted city.",
    "He arranged for a yearly speech to be made in\nBerlin, in honour of his adopted city",
    "The speaker, title, and institutional sponsor are not named.",
    ["cand-2519", "cand-9642", "cand-4623", "cand-3401"], True,
)
add_statement(
    "st-chp10-p315-high-proportion-of-streit-pictures-celebrated-venice", "cand-9627", "cand-9635", "high-proportion-of-pictures-celebrated-venices-beauties-and-traditions",
    106, 106,
    "Haskell says a strikingly high proportion of the pictures Streit owned were painted to celebrate Venice’s beauties and traditions.",
    "of the pictures he owned a strikingly high proportion were painted to celebrate its beauties and traditions.",
    "‘Its’ refers to Venice; no exact proportion or work titles are given.",
    ["cand-2519", "cand-9627", "cand-9635", "cand-3401"], True,
)
add_statement(
    "st-chp10-p315-streit-pictures-had-personal-meaning", "cand-9627", None, "works-held-more-specific-personal-meaning-for-streit-than-for-sophisticated-collectors",
    106, 106,
    "Haskell says works of art had a more specific and personal meaning for Streit than for more sophisticated collectors.",
    "Works of art held a far more specific and also a far more personal meaning for Streit than they did for more sophisticated collectors.",
    "This is a comparative interpretation; the unnamed comparison group is not individuated.",
    ["cand-9627", "cand-2519", "cand-9647"], False,
)
add_statement(
    "st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment", "cand-2519", "cand-9634", "two-of-four-canalettos-showed-scenes-related-to-streits-life",
    106, 106,
    "Haskell says two of Streit’s four Canalettos showed scenes directly concerned with his life, as he pointed out in long notes; the sentence continues on p.316.",
    "Of his four Canalettos, two showed scenes which were directly concerned with his own life, as he pointed out in the long notes which he made about",
    "The two scenes are a subset of the four pictures; the next source segment completes the phrase ‘about his pictures’.",
    ["cand-2519", "cand-9633", "cand-9634", "cand-3738", "cand-9637"], True,
    {"continuation_segment_id": NEXT_SEGMENT},
)

previous_shipping = statement_by_id.get(PREVIOUS_SHIPPING_ID)
if not previous_shipping or previous_shipping["qualifiers"].get("continuation_segment_id") != SEGMENT:
    raise SystemExit("p.314 shipping fragment changed or lost its continuation link")
previous_shipping["predicate"] = "sent-picture-crates-to-estates-in-germany"
previous_shipping["qualifiers"]["claim"] = "Haskell says Schulenburg was constantly sending crates of pictures back to his estates in Germany."
previous_shipping["qualifiers"]["qualification"] = "P.315 L96 completes the destination as Germany; no individual estate is named. The scan reads ‘sending crates’, while OCR joins the words."
previous_shipping["qualifiers"]["continuation_closed_by_statement_id"] = P315_CONTINUATION_ID

estate_candidate = next(row for row in candidates if row["candidate_id"] == "cand-9623")
estate_candidate["detail"] = "Plural property destinations to which Schulenburg sent picture crates; p.315 L96 confirms they were in Germany, but no individual estate is named."

coverage[PREVIOUS_SEGMENT]["note"] = (
    "Read printed p.314 against CHP-10.pdf physical p.47. The L84 opening completes the p.313 sentence; L84-91 records "
    "Piazzetta’s patronage/works, the collection’s genre and naturalist profile, and the view/landscape painters. The L93 "
    "shipping fragment is now completed by st-chp10-p315-schulenburg-estates-in-germany-continuation at p.315 L96. Coverage "
    "remains partial because footnotes 1-4 await canonical notes L288-291. Print corrections recorded without changing S0: "
    "Certain -> certain; sendingcrates -> sending crates."
)
coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L96-106",
    "note": (
        "Read printed p.315 against CHP-10.pdf physical p.48. L96 completes the previous p.314 shipment sentence; L96-99 "
        "compares Smith’s and Schulenburg’s collections, and L102-106 covers Streit’s introduction and biography. Footnote 1 "
        "awaits canonical note L292; footnote 2 awaits L293. L106 ends ‘about’ and continues at p.316 L108, so this segment "
        "remains partial. The section divider and SIGISMUND STREIT heading are structural, not additional entities. Print "
        "corrections recorded without changing S0: represented---- -> represented—; -was -> was; cither -> either; OCR punctuation "
        "at ‘age,-Tiepolo’ is normalized to the printed dash."
    ),
})

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate id")
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")
candidate_id_set = {row["candidate_id"] for row in candidate_rows}
if any(row["candidate_id"] not in candidate_id_set for row in new_mentions):
    raise SystemExit("missing mention candidate foreign key")
if any(cid not in candidate_id_set for row in new_statements for cid in row["qualifiers"]["mentioned_candidate_ids"]):
    raise SystemExit("missing statement candidate reference")
spans = sorted(
    (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
    for row in new_mentions
)
for left, right in zip(spans, spans[1:]):
    if left[1] > right[0]:
        raise SystemExit(f"overlapping p.315 mention spans: {left[2]} and {right[2]}")

print(f"p.315 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("p.314 shipment destination closed at Germany; Plate 53b corrected to separate Amigoni, portrait, and sitter")
print(f"coverage: p.315 reviewed/partial; next segment {NEXT_SEGMENT}; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
if not args.apply:
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
for path in targets:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
