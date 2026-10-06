"""Controlled S2 migration for printed p.316; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l108-117"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l95-106"
EXPECTED_MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENT_SHA = "7ec8534f6a5d8a00a026f86d3825580aed692c791f583e86777c89c11055f685"
BACKUP_SUFFIX = ".bak-s2-chp10-p316-20261003"
PREVIOUS_STATEMENT_ID = "st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment"
CONTINUATION_STATEMENT_ID = "st-chp10-p316-two-life-scenes-noted-about-streits-pictures"
NEXT_SEGMENT = "chp-10:10_CHP-10_sec_ii:l119-131"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.316 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[107:117]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.316 S2 source segment changed")
if segment_lines[0] != "[Page 316]" or not segment_lines[-1].endswith("Venetian society."):
    raise SystemExit("p.316 segment boundaries changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
table_state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if table_state != (9634, 9647, 20233, 8951):
    raise SystemExit(f"table state changed; re-read current table counts before migration: {table_state}")

REQUIRED = {
    "schulenburg": "cand-2401", "smith": "cand-2440", "streit": "cand-2519",
    "frederick": "cand-1079", "amigoni": "cand-0099", "pesne": "cand-1888",
    "canaletto": "cand-3738", "sebastiano_ricci": "cand-2154", "pittoni": "cand-3870",
    "piazzetta": "cand-3862", "zuccarelli": "cand-2879", "nogari": "cand-1743",
    "rembrandt": "cand-3471", "republic_of_venice": "cand-8838", "grand_canal": "cand-8178",
    "rialto_area": "cand-9206", "streit_collection": "cand-9627", "four_canalettos": "cand-9633",
    "two_life_scenes": "cand-9634", "streit_portrait": "cand-9636", "streit_notes": "cand-9637",
    "streit_father": "cand-9641", "genre_painting": "cand-9606",
}
for label, candidate_id in REQUIRED.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required candidate missing: {label}={candidate_id}")

coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.316 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.315 segment to remain partial pending its notes")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.316 already has S2 mention or statement rows")

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


add_candidate("cand-9648", "Canaletto view of the Grand Canal from Campo S. Sofia toward the Rialto", "work", "The first of the two life-related Canalettos mentioned at p.315; no formal title or present location is supplied. Keep distinct from other Rialto views.", 109)
add_candidate("cand-9649", "Campo S. Sofia in Venice", "place", "Named as the viewpoint for the Grand Canal scene in Streit’s collection; no building or address is identified.", 110)
add_candidate("cand-9650", "Palazzo Foscari in Venice", "place", "Haskell says Streit lived in this palace; do not merge with other Foscari palaces or infer a modern address.", 110)
add_candidate("cand-9651", "Canaletto view of Campo di Rialto connected with Streit’s business", "work", "The second of the two life-related views; title, date, and present location are not supplied.", 110)
add_candidate("cand-9652", "Campo di Rialto in Venice", "place", "Named as the location of Streit’s business activities and the subject of a Canaletto view; distinguish from the broader Rialto area candidate.", 110)
add_candidate("cand-9653", "Two further Canaletto night scenes of the Vigilie festivals in Streit’s collection", "work", "Two additional pictures beyond the pair of scenes about Streit’s life; their individual titles and locations are not supplied.", 111)
add_candidate("cand-9654", "Vigilie di S. Pietro", "event", "A Republic ceremony or festival represented in one of Streit’s Canaletto night scenes; retain the Italian wording and do not conflate it with a church/place.", 111)
add_candidate("cand-9655", "Vigilie di S. Marta", "event", "A Republic ceremony or festival represented in one of Streit’s Canaletto night scenes; Haskell calls it the most popular of such occasions.", 111)
add_candidate("cand-9656", "Canaletto’s unnamed followers", "", "An unnamed group of artists whose paintings record official processions; group membership and individual identities are not given.", 111)
add_candidate("cand-9657", "Several paintings by Canaletto’s followers showing official processions", "work", "A group of unidentified pictures recording the Doge’s participation in official processions; no individual titles or makers are named.", 111)
add_candidate("cand-9658", "Unnamed Doge represented in Venetian procession paintings", "person", "The Doge is not named or dated in this passage; do not identify him from the depicted processions.", 111)
add_candidate("cand-9659", "Official processions of the Doge recorded in paintings", "event", "An unspecified group of processions represented in pictures by Canaletto’s followers; no individual occasion is identified.", 111)
add_candidate("cand-9660", "Allegorical ‘Glory of Venice’ in Streit’s collection (destroyed)", "work", "A named allegorical picture that Haskell says culminated this section of the collection and had been destroyed by the time of writing; maker and destruction date are unstated.", 112)
add_candidate("cand-9661", "Pesne portraits of Frederick the Great and the Queen of Prussia for Streit", "work", "A pair or group of royal portraits commissioned by Streit; no titles, dates, or present locations are supplied.", 113)
add_candidate("cand-9662", "Unnamed Queen of Prussia portrayed for Streit", "person", "Haskell names the royal title but not the sitter; do not infer her personal identity from Frederick’s title or the date.", 113)
add_candidate("cand-9663", "Portraits of Streit’s father, mother, and sister", "work", "A group of family portraits that Haskell says hung on Streit’s walls; no titles, artists, or dates are supplied.", 113)
add_candidate("cand-9664", "Unnamed mother of Sigismund Streit", "person", "Mentioned only as the subject of a portrait; no name or other identifying detail is given.", 113)
add_candidate("cand-9665", "Unnamed sister of Sigismund Streit", "person", "Mentioned only as the subject of a portrait; no name or other identifying detail is given.", 113)
add_candidate("cand-9666", "Four portraits of Sigismund Streit", "work", "Haskell says four portraits of Streit hung on his walls and that none wholly satisfied him. The Plate 53b reference accompanies the group, but the text does not identify which portrait it depicts.", 113)
add_candidate("cand-9667", "Ten other pictures painted by Amigoni for Streit, 1739–1746", "work", "A group separate from Amigoni’s portrait of Streit; subjects are Old Testament and mythological, but the ten pictures are not individually inventoried here.", 115)
add_candidate("cand-9668", "Amigoni painting of ‘Lot and his Daughters’ for Streit", "work", "A subject-specific work cited in Haskell’s comparison of Amigoni’s pictures; distinct from the different Lot and his Daughters work already attributed to Carlo Loth.", 115)
add_candidate("cand-9669", "Amigoni painting of ‘Solomon adoring the Idols’ for Streit", "work", "A subject-specific work cited in Haskell’s comparison; the exact title and present location are not independently established.", 115)
add_candidate("cand-9670", "Amigoni painting of ‘Bathsheba’ for Streit", "work", "A subject-specific work cited in Haskell’s comparison; distinct from other Bathsheba paintings and from the general subject term.", 115)
add_candidate("cand-9671", "Amigoni painting of ‘The Sacrifice of Isaac’ for Streit", "work", "A subject-specific work cited in Haskell’s comparison; distinct from other paintings of the same subject already in the candidates table.", 115)
add_candidate("cand-9672", "A couple of Zuccarelli landscapes in Streit’s collection", "work", "Haskell reports two landscapes without identifying titles, dates, or locations.", 116)
add_candidate("cand-9673", "Unidentified Dutch picture in Streit’s collection", "work", "Haskell mentions one unspecified Dutch picture; no maker, subject, or date is given.", 116)
add_candidate("cand-9674", "‘Teste di fantasia’ (imaginary half-length portrait type)", "term", "Italian genre label explained by Haskell as imaginary half-length portraits, usually of older sitters; preserve it as an art term rather than a person or a single work.", 116)
add_candidate("cand-9675", "Two Nogari fantasy portraits in Streit’s collection", "work", "Two examples of the ‘teste di fantasia’ type; the source names an old man with a pipe and pouch and an old woman with glasses.", 116)
add_candidate("cand-9676", "Nogari portrait ‘Old Man with a Pipe and Tobacco Pouch’ for Streit", "work", "One of two fantasy portraits in Streit’s collection; printed title-like wording is retained without inferring date or present location.", 116)
add_candidate("cand-9677", "Nogari portrait ‘Old Woman with Glasses’ for Streit", "work", "One of two fantasy portraits in Streit’s collection; printed title-like wording is retained without inferring date or present location.", 117)
add_candidate("cand-9678", "Nogari’s four allegories of Education and other elevating pictures for Streit", "work", "Haskell reports four allegories of Education and additional elevating subjects; only the allegories are explicitly counted.", 117)
add_candidate("cand-9679", "Pastoral and mildly erotic tendency in Amigoni’s pictures for Streit", "term", "Haskell’s stylistic characterization of the pictures; it is an authorial interpretation, not an independent classification.", 115)
add_candidate("cand-9680", "Businessman as an art-patron class", "term", "Haskell describes this class as increasingly familiar later but still rare in the early eighteenth century; the passage uses Streit as its example.", 115)
add_candidate("cand-9681", "Unidentified Northern artists cited as influences on Nogari", "", "An unnamed group; Rembrandt is singled out as an example, but the passage supplies no membership list.", 116)
add_candidate("cand-9682", "Unnamed progressive circles in Venetian society", "", "Haskell says this genre was gaining support in some such circles; no individuals or institutional boundaries are specified.", 117)
add_candidate("cand-9683", "Portraits of royalty as a shared collecting taste", "term", "Haskell compares Streit’s taste with Schulenburg’s; no complete portrait inventory is supplied.", 113)
add_candidate("cand-9684", "Old Testament and mythological subject repertoire in Amigoni’s Streit pictures", "term", "Haskell groups these subject traditions as the repertoire for Amigoni’s ten other pictures; he does not inventory all the subjects.", 115)

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
    relative_line = line_no - 108
    start = sum(len(item) + 1 for item in segment_lines[:relative_line]) + starts[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch on L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p316-{len(new_mentions) + 1:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


MENTIONS = [
    (109, "his pictures", "cand-9627", "Completes p.315’s cross-page phrase about the pictures in Streit’s collection."),
    (109, "One", "cand-9648", "Anaphor for the first of the two life-related Canaletto scenes described at p.315 L106."),
    (109, "the Grand Canal", "cand-8178"),
    (110, "Campo S. Sofia", "cand-9649"),
    (110, "the Rialto", "cand-9206"),
    (110, "Streit himself", "cand-2519"),
    (110, "Palazzo Foscari", "cand-9650"),
    (110, "The other view", "cand-9651"),
    (110, "Campo di Rialto", "cand-9652"),
    (110, "his business activities", "cand-2519", "Corefers to Streit; the statement locates these activities at Campo di Rialto."),
    (111, "He", "cand-2519", "Corefers to Streit."),
    (111, "the Republic", "cand-8838", "The political entity whose ceremonies and festivals are represented."),
    (111, "Two more Canalettos", "cand-9653"),
    (111, "Vigilie di S. Pietro", "cand-9654"),
    (111, "di S. Marta", "cand-9655"),
    (111, "the latter", "cand-9655", "Corefers to Vigilie di S. Marta."),
    (111, "several other paintings", "cand-9657"),
    (111, "Canaletto’s followers", "cand-9656"),
    (111, "the Doge", "cand-9658"),
    (111, "official processions", "cand-9659"),
    (112, "Streit’s collection", "cand-9627"),
    (112, "Glory of Venice", "cand-9660"),
    (113, "Streit", "cand-2519"),
    (113, "Schulenburg", "cand-2401"),
    (113, "portraits of royalty", "cand-9683"),
    (113, "Antoine Pesne", "cand-1888", "The duplicate index candidate cand-1889 remains separate for S3 identity review."),
    (113, "Frederick the Great", "cand-1079"),
    (113, "Queen.of Prussia", "cand-9662", "OCR punctuation is corrected against the scan; personal identity remains unnamed."),
    (113, "representations of himself", "cand-9666", "Corefers to Streit’s self-portraits."),
    (113, "his family", "cand-9663", "The following clause specifies portraits of his father, mother, and sister."),
    (113, "his father", "cand-9641"),
    (113, "his mother", "cand-9664"),
    (113, "his sister", "cand-9665"),
    (113, "four of himself", "cand-9666"),
    (113, "Plate 53b", "cand-9636", "The captioned portrait is referred to after the group of four; which portrait in the group is not specified."),
    (114, "Schulenburg", "cand-2401"),
    (114, "Pittoni", "cand-3870"),
    (114, "Piazzetta", "cand-3862"),
    (114, "Smith", "cand-2440"),
    (115, "Sebastiano Ricci", "cand-2154"),
    (115, "Streit", "cand-2519"),
    (115, "Amigoni", "cand-0099"),
    (115, "his portrait", "cand-9636", "The Amigoni portrait already identified in the p.315 prose and Plate 53b caption."),
    (115, "ten other pictures", "cand-9667"),
    (115, "Their subjects", "cand-9667", "Refers to Amigoni’s ten other pictures."),
    (115, "Old Testament and mythological repertoire", "cand-9684"),
    (115, "Ricci", "cand-2154", "Later comparison with Amigoni’s pictures.", 1),
    (115, "Pittoni", "cand-3870"),
    (115, "pastoral", "cand-9679"),
    (115, "mildly erotic", "cand-9679"),
    (115, "Lot and his Daughters", "cand-9668"),
    (115, "Solomon adoring the Idols", "cand-9669"),
    (115, "Bathsheba", "cand-9670"),
    (115, "Sacrifice of Isaac", "cand-9671"),
    (115, "the tired businessman", "cand-9680", "Haskell’s example is Streit; preserve the author’s ‘doubtless’ as conjectural."),
    (115, "This class of patron", "cand-9680"),
    (116, "Streit", "cand-2519"),
    (116, "a couple of Zuccarelli landscapes", "cand-9672"),
    (116, "the odd Dutch picture", "cand-9673"),
    (116, "his collection", "cand-9627"),
    (116, "Giuseppe Nogari", "cand-1743"),
    (116, "This painter", "cand-1743", "Corefers to Giuseppe Nogari."),
    (116, "teste di fantasia", "cand-9674"),
    (116, "imaginary half-length portraits", "cand-9674", "Haskell’s gloss of the Italian term."),
    (116, "Northern artists", "cand-9681"),
    (116, "Rembrandt", "cand-3471"),
    (116, "Streit", "cand-2519", "Named as owner of the two Nogari portraits.", 1),
    (116, "two of these", "cand-9675", "Refers to two portraits of the ‘teste di fantasia’ type."),
    (116, "Old man with a Pipe and Tobacco Pouch", "cand-9676"),
    (116, "Old", "cand-9677", "Starts the second work title, completed on the next source line.", 1),
    (117, "Woman with Glasses", "cand-9677", "Completes the title begun as ‘an Old’ at the end of L116."),
    (117, "Nogari", "cand-1743", "Named as the painter employed by Streit."),
    (117, "four allegories of Education and other elevating subjects", "cand-9678"),
    (117, "the artist", "cand-1743", "Corefers to Nogari."),
    (117, "mawkish genre", "cand-9606", "Haskell’s evaluative characterization."),
    (117, "he clearly found more congenial", "cand-1743", "‘He’ refers to Nogari; footnote 4 awaits canonical note L297."),
    (117, "‘progressive’ circles in Venetian society", "cand-9682"),
]
for item in MENTIONS:
    add_mention(*item)

candidate_by_id = {row["candidate_id"]: row for row in candidates}
candidate_by_id["cand-9633"]["detail"] = (
    "Four Canaletto pictures in Streit’s collection. P.315 identifies two life-related views, described at p.316 L109-110; "
    "p.316 L111 reports two further night scenes of the Vigilie di S. Pietro and di S. Marta. The four individual works "
    "are not otherwise catalogued here."
)
candidate_by_id["cand-9634"]["detail"] = (
    "Two of Streit’s four Canalettos showing scenes directly concerned with his life. P.316 describes one view from "
    "Campo S. Sofia toward Rialto and the other at Campo di Rialto; retain each as a separate work candidate."
)
candidate_by_id["cand-9636"]["detail"] = (
    "Amigoni portrait of Sigismund Streit identified by Plate 53b and p.315 L105. P.316 L113 refers to four portraits "
    "of Streit with a Plate 53b pointer, but does not specify which of the four this picture is."
)

statement_by_id = {row["statement_id"]: row for row in statements}
previous_statement = statement_by_id.get(PREVIOUS_STATEMENT_ID)
if not previous_statement or previous_statement["qualifiers"].get("continuation_segment_id") != SEGMENT:
    raise SystemExit("p.315 Canaletto statement changed or lost its p.316 continuation link")

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, relation_candidate=False, extra=None):
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored: {statement_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 316,
        "pdf_physical_page": 49,
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
    CONTINUATION_STATEMENT_ID, "cand-2519", "cand-9637", "pointed-to-his-own-notes-about-his-pictures",
    109, 109,
    "The two life-related Canaletto scenes are connected to Streit’s long notes about his pictures.",
    "his pictures,1",
    "Continues the p.315 sentence about two of four Canalettos and Streit’s notes; footnote 1 awaits canonical note L294.",
    ["cand-2519", "cand-9627", "cand-9634", "cand-9637"], True,
    {"continuation_of_statement_id": PREVIOUS_STATEMENT_ID, "footnote_marker": 1, "pending_note_source_line": 294},
)
add_statement(
    "st-chp10-p316-first-life-canaletto-view", "cand-9648", "cand-9634", "first-of-two-life-related-canaletto-scenes",
    109, 110,
    "The first life-related Canaletto scene is a Grand Canal view looking southeast from Campo S. Sofia toward the Rialto.",
    "One portrayed a sweep of the Grand Canal looking south-east from the\nCampo S. Sofia to the Rialto.",
    "‘One’ refers to the two scenes introduced at p.315 L106; no formal title is supplied.",
    ["cand-9648", "cand-9634", "cand-8178", "cand-9649", "cand-9206"], True,
)
add_statement(
    "st-chp10-p316-streit-in-gondola-in-first-view", "cand-9648", "cand-2519", "depicts-streit-standing-in-a-gondola",
    110, 110,
    "The foreground of the first view shows Streit standing in a gondola.",
    "Well in the foreground is a gondola in which stands Streit himself",
    "This is the scene’s depicted figure, not a claim that the event occurred exactly as painted.",
    ["cand-9648", "cand-2519"], True,
)
add_statement(
    "st-chp10-p316-streit-lived-in-palazzo-foscari", "cand-2519", "cand-9650", "lived-in-palazzo-foscari",
    110, 110,
    "Haskell says Streit lived in Palazzo Foscari, visible behind the gondola in the view.",
    "behind can be seen the Palazzo Foscari in which he lived.",
    "The source names the palace but does not resolve its precise modern identification.",
    ["cand-9648", "cand-2519", "cand-9650"], True,
)
add_statement(
    "st-chp10-p316-second-life-canaletto-view-at-campo-di-rialto", "cand-9651", "cand-9652", "view-of-streits-business-site-at-campo-di-rialto",
    110, 110,
    "The other life-related view depicts Campo di Rialto, where Streit’s business activities took place.",
    "The other view was of the Campo di Rialto in which his business activities were carried out.",
    "‘The other view’ refers to the second of the two scenes introduced at p.315; the business is not otherwise specified.",
    ["cand-9651", "cand-9634", "cand-9652", "cand-2519"], True,
)
add_statement(
    "st-chp10-p316-streit-sought-republic-ceremony-pictures", "cand-2519", "cand-8838", "sought-pictures-of-republic-ceremonies-and-festivals",
    111, 111,
    "Haskell says Streit was keen to have pictures of ceremonies and festivals of the Republic of Venice.",
    "He was equally keen to have pictures of the ceremonies and festivals of the Republic.",
    "This is a collecting preference; it does not establish a commission for every picture described below.",
    ["cand-2519", "cand-8838", "cand-9627"], False,
)
add_statement(
    "st-chp10-p316-two-night-canaletto-scenes-show-vigili", "cand-9653", "cand-9654", "depicts-vigilie-di-s-pietro-and-di-s-marta",
    111, 111,
    "Two further Canaletto night scenes in Streit’s collection show the Vigilie di S. Pietro and di S. Marta.",
    "Two more Canalettos, among his very rare night scenes, show the Vigilie di S. Pietro and di S. Marta",
    "The two events are represented by two additional works beyond the pair of life-related views; exact one-to-one object titles are not supplied.",
    ["cand-9653", "cand-9633", "cand-3738", "cand-2519", "cand-9627", "cand-9654", "cand-9655"], True,
)
add_statement(
    "st-chp10-p316-vigilia-di-s-marta-most-popular", "cand-9655", None, "described-as-most-popular-of-such-occasions",
    111, 111,
    "Haskell calls the Vigilie di S. Marta the most popular of the occasions under discussion.",
    "the latter the most popular of all such occasions",
    "‘The latter’ refers to Vigilie di S. Marta; this is Haskell’s characterization.",
    ["cand-9655"], False,
)
add_statement(
    "st-chp10-p316-follower-paintings-record-doge-processions", "cand-9657", "cand-9658", "records-doge-taking-part-in-official-processions",
    111, 111,
    "Several other paintings by Canaletto’s followers record the Doge taking part in official processions.",
    "several other paintings by Canaletto’s followers recorded the Doge taking part in official processions.2",
    "The pictures and Doge are not individually identified; footnote 2 awaits canonical note L295 and may clarify an attribution.",
    ["cand-9657", "cand-9656", "cand-9658", "cand-9659"], True,
    {"footnote_marker": 2, "pending_note_source_line": 295},
)
add_statement(
    "st-chp10-p316-glory-of-venice-destroyed", "cand-9627", "cand-9660", "collection-culminated-in-allegory-destroyed",
    112, 112,
    "Haskell says the section of Streit’s collection culminated in an allegorical Glory of Venice that had been destroyed.",
    "This section of Streit’s collection culminated in an allegorical ‘Glory of Venice’ which has unfortunately been destroyed...",
    "The artist, destruction date, and other work details are not supplied.",
    ["cand-9627", "cand-9660"], True,
)
add_statement(
    "st-chp10-p316-streit-shared-schulenburg-royal-portrait-taste", "cand-2519", "cand-2401", "shared-taste-for-portraits-of-royalty",
    113, 113,
    "Haskell says Streit shared Schulenburg’s taste for portraits of royalty.",
    "Streit shared Schulenburg’s taste for portraits of royalty",
    "This is a comparison of collecting taste, not evidence of a personal relationship beyond what the sentence states.",
    ["cand-2519", "cand-2401", "cand-9683"], False,
)
add_statement(
    "st-chp10-p316-streit-regarded-pesne-as-friend", "cand-2519", "cand-1888", "identified-as-friend-of-antoine-pesne",
    113, 113,
    "Haskell identifies Antoine Pesne as Streit’s friend.",
    "his friend Antoine Pesne",
    "An identically named index candidate cand-1889 remains for S3 review; the body mention is mapped to cand-1888.",
    ["cand-2519", "cand-1888"], True,
)
add_statement(
    "st-chp10-p316-streit-commissioned-pesne-royal-portraits", "cand-2519", "cand-9661", "commissioned-pesne-to-paint-frederick-and-queen-of-prussia",
    113, 113,
    "Haskell says Streit commissioned Pesne to paint Frederick the Great and the Queen of Prussia.",
    "he commissioned his friend Antoine Pesne to paint Frederick the Great and the Queen.of Prussia.",
    "The OCR period in Queen.of is absent from the print; the Queen is not named, and the works have no titles here.",
    ["cand-2519", "cand-1888", "cand-1079", "cand-9662", "cand-9661"], True,
    {"ocr_print_correction": "Queen.of -> Queen of"},
)
add_statement(
    "st-chp10-p316-streit-liked-self-and-family-representations", "cand-2519", "cand-9666", "liked-representations-of-himself-and-family",
    113, 113,
    "Haskell says Streit particularly liked representations of himself and his family.",
    "But, above all, he liked to see representations of himself-and his family.",
    "The print reads ‘himself and’; ‘family’ is specified next as father, mother, and sister.",
    ["cand-2519", "cand-9666", "cand-9663"], False,
    {"ocr_print_correction": "himself-and -> himself and"},
)
add_statement(
    "st-chp10-p316-streit-displayed-family-portraits", "cand-9663", "cand-2519", "portraits-of-father-mother-and-sister-hung-on-streits-walls",
    113, 113,
    "Haskell says portraits of Streit’s father, mother, and sister hung on his walls.",
    "Portraits of his father, his mother and his sister hung from his walls",
    "The source does not name the relatives, painters, or works, and does not specify a room or palace.",
    ["cand-9663", "cand-2519", "cand-9641", "cand-9664", "cand-9665"], True,
)
add_statement(
    "st-chp10-p316-four-streit-portraits-did-not-satisfy-him", "cand-9666", "cand-2519", "none-of-four-portraits-wholly-satisfied-streit",
    113, 113,
    "Haskell says none of Streit’s four portraits wholly satisfied him.",
    "as well as four of himself (Plate 53b)—not one of which wholly satisfied him.",
    "Plate 53b points to an example; which of the four is shown is not specified in this clause.",
    ["cand-9666", "cand-2519", "cand-9636"], False,
)
add_statement(
    "st-chp10-p316-amigoni-compared-with-smith-and-schulenburg-painters", "cand-2519", "cand-0099", "turned-to-amigoni-after-collectors-painter-contrasts",
    114, 115,
    "Haskell contrasts Schulenburg’s Pittoni and Piazzetta collecting and Smith’s Sebastiano Ricci collecting with Streit’s turn to Amigoni.",
    "Schulenburg was an enthusiastic collector of Pittoni and Piazzetta, Smith of\nSebastiano Ricci—it seems almost inevitable that Streit should have turned to Amigoni",
    "‘It seems almost inevitable’ is Haskell’s interpretation, not a documented commission rationale.",
    ["cand-2401", "cand-3870", "cand-3862", "cand-2440", "cand-2154", "cand-2519", "cand-0099"], False,
)
add_statement(
    "st-chp10-p316-amigoni-painted-streit-portrait-and-ten-other-pictures", "cand-0099", "cand-9667", "painted-portrait-and-ten-other-pictures-for-streit-1739-1746",
    115, 115,
    "Haskell says Amigoni painted Streit’s portrait and ten other pictures for him between 1739 and 1746.",
    "Amigoni, who painted his portrait and ten other pictures for him between 1739 and 1746.3",
    "The portrait is the work already captioned on Plate 53b; footnote 3 awaits canonical note L296, which may clarify the portrait date.",
    ["cand-0099", "cand-2519", "cand-9636", "cand-9667"], True,
    {"footnote_marker": 3, "pending_note_source_line": 296},
)
add_statement(
    "st-chp10-p316-amigoni-picture-subjects-old-testament-and-mythological", "cand-9667", "cand-9684", "subjects-from-popular-old-testament-and-mythological-repertoire",
    115, 115,
    "Haskell says the subjects of Amigoni’s other pictures belonged to popular Old Testament and mythological repertoires.",
    "Their subjects were among the most popular of the Old Testament and mythological repertoire",
    "The passage gives examples below but does not inventory all ten pictures.",
    ["cand-9667", "cand-9684"], False,
)
add_statement(
    "st-chp10-p316-amigoni-pictures-lacked-ricci-pittoni-heroic-melodrama", "cand-9667", None, "lacked-glitter-and-heroic-melodrama-of-ricci-and-pittoni",
    115, 115,
    "Haskell says these pictures lacked the glitter or heroic melodrama he associates with Ricci and Pittoni.",
    "but they had none of the glitter or heroic melodrama of Ricci or Pittoni.",
    "This is an evaluative comparison by Haskell.",
    ["cand-9667", "cand-2154", "cand-3870"], False,
)
add_statement(
    "st-chp10-p316-amigoni-pictures-tend-pastoral-or-mildly-erotic", "cand-9667", "cand-9679", "tended-to-pastoral-or-mildly-erotic-subjects",
    115, 115,
    "Haskell characterizes Amigoni’s pictures for Streit as tending toward the pastoral or mildly erotic.",
    "In them everything tends to the pastoral or the mildly erotic.",
    "Preserve this as Haskell’s characterization of the group, not a definitive genre assignment for every work.",
    ["cand-9667", "cand-9679"], False,
)
add_statement(
    "st-chp10-p316-amigoni-pictures-suave-delicate-no-key-change", "cand-9667", None, "suave-delicate-no-emotional-change-between-four-subjects",
    115, 115,
    "Haskell describes the pictures as suave and delicate and sees no emotional change of key between four named subjects.",
    "Suave and delicate, with no emotional change of key between Lot and his Daughters and Solomon adoring the Idols or between Bathsheba and the Sacrifice of Isaac",
    "The four subject-specific work candidates are separate Amigoni pictures; other works in the ten-picture group are not enumerated.",
    ["cand-9667", "cand-9668", "cand-9669", "cand-9670", "cand-9671"], False,
)
add_statement(
    "st-chp10-p316-amigoni-pictures-intended-to-soothe-streit", "cand-9667", "cand-2519", "doubtless-intended-to-soothe-tired-businessman",
    115, 115,
    "Haskell says the pictures were doubtless intended to soothe the tired businessman, referring to Streit.",
    "they were doubtless intended to be soothing to the eye of the tired businessman.",
    "‘Doubtless’ marks Haskell’s interpretation; it is not a documented statement of the patron’s or painter’s intent.",
    ["cand-9667", "cand-2519", "cand-9680"], False,
)
add_statement(
    "st-chp10-p316-businessman-patron-class-rare-in-early-eighteenth-century", "cand-9680", None, "later-more-familiar-but-then-rare",
    115, 115,
    "Haskell says this class of businessman-patron became more familiar later but remained rare in the early eighteenth century.",
    "This class of patron has since become much more familiar; in the early eighteenth century he was still rare.",
    "This is Haskell’s historical generalization, not a population count.",
    ["cand-9680", "cand-2519"], False,
)
add_statement(
    "st-chp10-p316-streit-owned-zuccarelli-landscapes-and-dutch-picture", "cand-2519", "cand-9627", "owned-zuccarelli-landscapes-and-one-dutch-picture",
    116, 116,
    "Haskell says Streit owned a couple of Zuccarelli landscapes and one unspecified Dutch picture.",
    "Streit naturally owned a couple of Zuccarelli landscapes and the odd Dutch picture",
    "The two landscapes and Dutch picture have no titles, dates, or locations in this passage.",
    ["cand-2519", "cand-9627", "cand-2879", "cand-9672", "cand-9673"], True,
)
add_statement(
    "st-chp10-p316-nogari-only-other-artist-well-represented", "cand-9627", "cand-1743", "only-other-artist-well-represented-in-streit-collection",
    116, 116,
    "Haskell says Giuseppe Nogari was the only other artist well represented in Streit’s collection.",
    "but the only other artist well represented in his collection was Giuseppe Nogari.",
    "‘Other’ follows Haskell’s prior discussion of Canaletto; it does not imply no works by other artists at all.",
    ["cand-9627", "cand-1743"], True,
)
add_statement(
    "st-chp10-p316-nogari-known-for-teste-di-fantasia", "cand-1743", "cand-9674", "famous-for-imaginary-half-length-portraits",
    116, 116,
    "Haskell says Nogari was famous above all for ‘teste di fantasia’, imaginary half-length portraits.",
    "This painter was famous above all for his ‘teste di fantasia’—imaginary half-length portraits",
    "The Italian term and the author’s English gloss are retained together.",
    ["cand-1743", "cand-9674"], False,
)
add_statement(
    "st-chp10-p316-nogari-portraits-influenced-by-northern-artists-and-rembrandt", "cand-1743", "cand-9681", "portraits-influenced-by-northern-artists-especially-rembrandt",
    116, 116,
    "Haskell says the portrait type was strongly influenced by Northern artists, especially Rembrandt, and usually depicted old men and women.",
    "strongly influenced by Northern artists especially Rembrandt, usually of old men and women.",
    "The Northern artists are unnamed as a group; Rembrandt is explicitly named as an example.",
    ["cand-9674", "cand-9681", "cand-3471"], False,
)
add_statement(
    "st-chp10-p316-streit-owned-two-nogari-fantasy-portraits", "cand-2519", "cand-9675", "owned-two-nogari-fantasy-portraits",
    116, 117,
    "Haskell says Streit had two such portraits: an Old man with a Pipe and Tobacco Pouch and an Old Woman with Glasses.",
    "Streit had two of these—an Old man with a Pipe and Tobacco Pouch and an Old\nWoman with Glasses",
    "The named works are separate candidates; neither is identified with other fantasy-head groups in the book.",
    ["cand-2519", "cand-9675", "cand-9674", "cand-9676", "cand-9677"], True,
)
add_statement(
    "st-chp10-p316-streit-employed-nogari-for-education-allegories", "cand-2519", "cand-9678", "employed-nogari-to-paint-four-education-allegories-and-other-elevating-subjects",
    117, 117,
    "Haskell says Streit employed Nogari to paint four allegories of Education and other elevating subjects.",
    "but he also employed Nogari to paint four allegories of Education and other elevating subjects",
    "The sentence counts four allegories of Education; it does not specify the number of additional elevating pictures.",
    ["cand-2519", "cand-1743", "cand-9678"], True,
)
add_statement(
    "st-chp10-p316-nogari-turned-elevating-subjects-to-mawkish-genre", "cand-9678", "cand-9606", "turned-subjects-into-mawkish-genre-pretexts",
    117, 117,
    "Haskell says Nogari characteristically turned these elevating subjects into pretexts for rather mawkish genre.",
    "which were characteristically turned by the artist into pretexts for rather mawkish genre",
    "This is Haskell’s evaluative characterization; ‘the artist’ refers to Nogari.",
    ["cand-9678", "cand-1743", "cand-9606"], False,
)
add_statement(
    "st-chp10-p316-nogari-found-genre-more-congenial", "cand-1743", "cand-9606", "found-genre-more-congenial",
    117, 117,
    "Haskell says genre was the branch of art Nogari clearly found more congenial.",
    "a branch of the art which he clearly found more congenial4",
    "‘He’ refers to Nogari; footnote 4 awaits canonical note L297.",
    ["cand-1743", "cand-9606"], False,
    {"footnote_marker": 4, "pending_note_source_line": 297},
)
add_statement(
    "st-chp10-p316-genre-gaining-support-in-progressive-circles", "cand-9606", "cand-9682", "gaining-support-in-some-venetian-progressive-circles",
    117, 117,
    "Haskell says genre was gaining support at the time in some of the more progressive circles in Venetian society.",
    "which, as will be seen in the following chapter, was winning much support at the time in some of the more ‘progressive’ circles in Venetian society.",
    "This is Haskell’s period assessment and cross-reference to the following chapter; it does not establish a named organization.",
    ["cand-9606", "cand-9682"], False,
    {"cross_reference": "following chapter; next printed chapter heading is Chapter 12"},
)

statement_by_id[CONTINUATION_STATEMENT_ID] = new_statements[0]
previous_statement["qualifiers"]["qualification"] = (
    "The two scenes are a subset of Streit’s four Canalettos; p.316 L109–110 now identifies their views. "
    "Footnote 1 awaits canonical note L294."
)
previous_statement["qualifiers"]["continuation_closed_by_statement_id"] = CONTINUATION_STATEMENT_ID

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
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in new_mentions)
for left, right in zip(spans, spans[1:]):
    if left[1] > right[0]:
        raise SystemExit(f"overlapping p.316 mention spans: {left[2]} and {right[2]}")

previous_coverage_note = coverage[PREVIOUS_SEGMENT].get("note", "")
coverage[PREVIOUS_SEGMENT]["note"] = previous_coverage_note + " " + (
    "Read p.315 against CHP-10.pdf physical p.48. The L106 sentence about two life-related Canaletto scenes is closed by "
    f"{CONTINUATION_STATEMENT_ID} at p.316 L109; p.315 remains partial pending footnotes at canonical notes L292–293."
)
coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L109-117",
    "note": (
        "Read printed p.316 against CHP-10.pdf physical p.49. L109 closes the p.315 sentence about two life-related "
        "Canalettos and Streit’s notes. L109–113 describes the two views, Republic festivals, procession pictures, the "
        "destroyed Glory of Venice, and Streit’s royal/family portraits; L114–117 compares collecting choices and records "
        "Amigoni and Nogari works and Haskell’s stylistic judgments. Footnotes 1–4 await canonical notes L294–297, so "
        "coverage remains partial. Print corrections recorded without changing S0: Queen.of -> Queen of; himself-and -> "
        "himself and. The source em dash after Ricci matches the print. All uncatalogued or unnamed objects and "
        "groups retain explicit limits; the Queen and Doge are not identified beyond their titles."
    ),
})

print(f"p.316 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("p.315 life-scene continuation closed; four Canaletto works now distinguished as two personal views and two festival scenes")
print(f"coverage: p.316 reviewed/partial; next source segment {NEXT_SEGMENT}; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
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
