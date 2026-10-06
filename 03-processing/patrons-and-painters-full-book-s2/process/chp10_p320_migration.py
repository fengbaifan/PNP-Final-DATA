"""Controlled S2 migration for printed p.320; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l151-163"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l144-149"
NEXT_SEGMENT = "chp-10:10_CHP-10_sec_ii:l165-173"
PREVIOUS_QUOTATION = "st-chp10-p319-conti-painters-fantasy-quoted-principles"
EXPECTED_MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENT_SHA = "ca9b13f097c70411ec22b3ea274eca40603a0eb053de5ef9b7473fdee422a2f0"
BACKUP_SUFFIX = ".bak-s2-chp10-p320-typefix-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.320 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[150:163]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.320 S2 source segment changed")
if segment_lines[0] != "[Page 320]" or not segment_lines[-1].endswith("but"):
    raise SystemExit("p.320 segment boundaries changed")

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
if table_state != (9719, 9732, 20472, 9046):
    raise SystemExit(f"table state changed; re-read current table counts before migration: {table_state}")

coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.320 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.319 to remain partial pending its notes")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.320 already has S2 mention or statement rows")

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


add_candidate("cand-9733", "Unidentified modello cited as a justification for Conti's painterly fantasy", "work", "Haskell says this seems to be a modello by Tiepolo or Pittoni; its exact identity and attribution are unresolved.", 152)
add_candidate("cand-9734", "Process for making colour woodcuts", "procedure", "The source says Zanetti announced its rediscovery to Conti; no technical description is provided here.", 155)
add_candidate("cand-9735", "Genius as an artistic concept", "term", "The source describes its emergence as acceptance of the artist's vagaries; the claim is Haskell's periodization.", 156)
add_candidate("cand-9736", "Minori Osservanti (religious order)", "institution", "Named as the order of which Lodoli was a brother; the passage gives no further organizational detail.", 157)
add_candidate("cand-9737", "Unidentified palace of Consul Joseph Smith on the Grand Canal", "place", "The palace is spatially described but not named; do not identify it with a known building from outside this passage.", 157)
add_candidate("cand-9738", "Carlo Lodoli's unnamed private school in Venice", "institution", "A school opened for the sons of leading families and Lodoli's friends; it has no proper name in the source.", 158)
add_candidate("cand-9739", "Inquisitori di Stato (Venetian state body)", "institution", "Named in the account of Lodoli's dispute over using State documents for teaching.", 159)
add_candidate("cand-9740", "Autobiography of Giambattista Vico", "archive", "The text is unnamed beyond this generic title; Haskell says it was first published in Venice.", 161)
add_candidate("cand-9741", "More enlightened Venetian figures associated with Carlo Lodoli", "", "A partly named collective; retain type as unresolved rather than treating it as a formal institution.", 161)
add_candidate("cand-9742", "Venetian aristocrats who admired Carlo Lodoli (unnamed group)", "", "The source gives no names; the group is reported as a temporary circle of admirers.", 162)

candidate_ids.update(row["candidate_id"] for row in new_candidates)
new_mentions = []


def line_offset(line_no):
    if line_no < 151:
        raise SystemExit(f"p.320 mention starts before its segment: L{line_no}")
    return sum(len(line) + 1 for line in segment_lines[:line_no - 151])


def add_mention(line_no, surface, candidate_id, note="", occurrence=0):
    if candidate_id not in candidate_ids:
        raise SystemExit(f"mention references unknown candidate {candidate_id}: {surface!r}")
    expected_start = line_offset(line_no)
    line = source_lines[line_no - 1]
    starts = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(expected_start + at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text not found on L{line_no}: {surface!r} occurrence {occurrence}")
    start = starts[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch on L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


MENTIONS = [
    (152, "Tiepolo", "cand-2569", "Haskell presents him only as a possible author of the unspecified modello.", 0),
    (152, "Pittoni", "cand-1950", "Haskell presents him only as a possible author of the unspecified modello.", 0),
    (152, "modello", "cand-9733", "The precise work and attribution are not identified.", 0),
    (153, "Conti", "cand-0826", "The statement limits what can be claimed about his aesthetics and influence.", 0),
    (154, "him", "cand-0826", "Corefers to Conti in the account of the letter from Zanetti.", 0),
    (155, "Zanetti", "cand-2838", "The index identifies A. M. Zanetti the Elder.", 0),
    (155, "process for making colour woodcuts", "cand-9734", "A procedure whose rediscovery Zanetti announced to Conti.", 0),
    (155, "Francesco Algarotti", "cand-0046", "Reuses the p.320 index candidate for Algarotti and Conti.", 0),
    (155, "him", "cand-0827", "Corefers to Conti in the indexed Algarotti correspondence context.", 0),
    (155, "this Italian pioneer", "cand-0827", "Corefers to Conti, whose ideas Algarotti adopted.", 0),
    (155, "Newton", "cand-1739", "Named as the subject of the ideas Conti helped Algarotti understand.", 0),
    (156, "Algarotti", "cand-0046", "Named as the subject of Haskell's claim about retaining creative fantasy.", 0),
    (156, "creative fantasy", "cand-0992", "The topic is connected to the p.318 fantasy/reason discussion but retained here as an art concept.", 0),
    (156, "Conti", "cand-0826", "Named as the source from which Algarotti inherited this belief.", 0),
    (156, "unfettered-imagination", "cand-0992", "Retains the printed/OCR hyphenated phrase as an idea in the same discussion.", 0),
    (156, "Saverio Bettinelli", "cand-0369", "Named as the author of the 1769 work.", 0),
    (156, "Delientusiasmo", "cand-0370", "The scan reads Dell'entusiasmo; OCR omitted the apostrophe and second l.", 0),
    (156, "Milan", "cand-3418", "Place of publication as given in the source.", 0),
    (156, "‘genius’", "cand-9735", "Named as an emerging artistic concept in Haskell's account.", 0),
    (157, "Venice", "cand-2719", "The city context for Lodoli's activity.", 0),
    (157, "Conti", "cand-0826", "Named in the comparison with the more immediately stimulating thinker.", 0),
    (157, "Consul Smith’s", "cand-2440", "The palace is identified by its owner/occupant, Joseph Smith.", 0),
    (157, "palace", "cand-9737", "The text locates but does not name the palace.", 0),
    (157, "Grand Canal", "cand-8178", "The geographic reference locates Smith's palace.", 0),
    (157, "Padre Carlo Lodoli", "cand-1411", "The main index candidate for Lodoli is reused.", 0),
    (157, "Minori Osservanti", "cand-9736", "Named religious order; the p.320 index does not provide a separate candidate.", 0),
    (158, "Lodoli", "cand-1411", "Named as the subject of the biographical account.", 0),
    (158, "Rome", "cand-4490", "One destination in Lodoli's travel account.", 0),
    (158, "Italy", "cand-3461", "The source refers to other parts of Italy.", 0),
    (158, "Venice", "cand-2719", "Lodoli's native city and return destination.", 0),
    (158, "private school", "cand-9738", "The school is unnamed and retained as a provisional institution candidate.", 0),
    (158, "This school", "cand-9738", "The source describes its curriculum and operation.", 0),
    (159, "Galileo", "cand-1105", "One of Lodoli's favourite authors.", 0),
    (159, "Bacon", "cand-0155", "One of Lodoli's favourite authors.", 0),
    (159, "Cicero", "cand-0747", "Named as an author used in Lodoli's teaching.", 0),
    (159, "Puffendorf", "cand-2069", "The printed surname appears as Puffendorf; preserve the source form while reusing the index candidate.", 0),
    (159, "Inquisitori di Stato", "cand-9739", "Named state body involved in Lodoli's dispute.", 0),
    (160, "Vico", "cand-2771", "The p.320 index candidate has an Autobiography subentry.", 0),
    (161, "Autobiography", "cand-9740", "The specific work by Vico, first published in Venice according to Haskell.", 0),
    (161, "Venice", "cand-2719", "The stated place of first publication.", 0),
    (161, "Republic", "cand-8838", "The Republic of Venice as the political entity employing a chief censor.", 0),
    (161, "more enlightened figures in the city", "cand-9741", "A partially named collective, including the following three people.", 0),
    (161, "Andrea Memmo", "cand-1642", "Named among Lodoli's associations.", 0),
    (161, "Angelo Querini", "cand-2075", "Named among Lodoli's associations.", 0),
    (161, "Giambattista", "cand-1844", "The given name of Lodoli's associate, whose surname continues at the start of the next source line.", 0),
    (162, "Pasquali", "cand-1844", "The surname completes the associate's name across the line break; identified as a publisher.", 0),
    (162, "Consul Smith", "cand-2440", "The source says nearly all of the named/associated figures were Smith's friends.", 0),
    (162, "Venetian aristocracy", "cand-9742", "An unnamed social group said to include admirers of Lodoli for a time.", 0),
    (162, "Montesquieu", "cand-1696", "Named as one of Lodoli's contacts outside Venice.", 0),
    (162, "Scipione Maffei", "cand-1487", "Named as one of Lodoli's contacts outside Venice.", 0),
    (163, "Lodoli", "cand-1411", "Named in the description of his appearance and manner.", 0),
]

for item in MENTIONS:
    add_mention(*item)
new_mentions.sort(key=lambda row: int(row["start_char"]))
for index, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-s2-ch10-p320-{index:04d}"
for left, right in zip(new_mentions, new_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping p.320 mention spans: {left['surface_form']} and {right['surface_form']}")

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, relation_candidate=False, extra=None):
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in p.320: {statement_id}")
    if any(cid not in candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 320,
        "pdf_physical_page": 53,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial claim",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
    }
    if extra:
        qualifiers.update(extra)
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
    "st-chp10-p320-modello-possibly-justifies-conti-fantasy", "cand-0829", "cand-9733", "may-justify-contis-painterly-fantasy",
    152, 152,
    "Haskell suggests that the quoted criteria may be the very justification for a modello by Tiepolo or Pittoni.",
    "This seems to be the very justification of a modello by Tiepolo or Pittoni.",
    "'Seems' is retained; the particular modello and which of the two artists made it are unresolved.",
    ["cand-0829", "cand-0992", "cand-9733", "cand-2569", "cand-1950"], False,
)
add_statement(
    "st-chp10-p320-conti-references-too-brief-for-aesthetic-system", "cand-0826", None, "references-insufficient-to-claim-coherent-aesthetic-ideas-or-major-influence",
    153, 153,
    "Haskell says the detached references are too brief to claim that Conti had coherent aesthetic ideas or played much part in encouraging particular painters.",
    "Such detached references are too brief for us to claim that Conti had any coherent aesthetic ideas or that they played much part in encouraging any particular painters.",
    "This explicit limitation narrows the interpretation of Conti's ideas and influence.",
    ["cand-0826"],
)
add_statement(
    "st-chp10-p320-zanetti-announced-colour-woodcut-process-to-conti", "cand-2838", "cand-9734", "announced-rediscovery-of-process-to-conti",
    154, 155,
    "Haskell says Conti showed interest in the arts and that A. M. Zanetti the Elder wrote to announce his rediscovery of the colour woodcut process to Conti.",
    "But we know that he showed an interest in the arts, for it was to him that the elder\nZanetti wrote to announce his rediscovery of the process for making colour woodcuts1;",
    "The correspondence date and technical details are not given here. Footnote 1 awaits canonical note L308.",
    ["cand-0826", "cand-2838", "cand-9734"], True,
    {"footnote_marker": 1, "pending_note_source_line": 308},
)
add_statement(
    "st-chp10-p320-algarotti-and-conti-corresponded-constantly", "cand-0046", "cand-0827", "constant-correspondence-with-conti",
    155, 155,
    "Haskell says Francesco Algarotti was in constant correspondence with Conti.",
    "Francesco Algarotti, who was in constant correspondence with him",
    "'Him' refers to Conti; this statement does not infer dates or the full extent of the correspondence.",
    ["cand-0046", "cand-0827", "cand-0826"], True,
)
add_statement(
    "st-chp10-p320-algarotti-took-ideas-from-conti-on-newton", "cand-0046", "cand-0826", "took-over-many-ideas-on-newton-from-conti",
    155, 155,
    "Haskell says Algarotti took over many ideas from Conti in understanding Newton.",
    "took over many ideas from this Italian pioneer in the understanding of Newton.",
    "'This Italian pioneer' refers to Conti; the source does not enumerate the ideas.",
    ["cand-0046", "cand-0827", "cand-0826", "cand-1739"], True,
)
add_statement(
    "st-chp10-p320-algarotti-fantasy-belief-inherited-from-conti", "cand-0046", "cand-0826", "creative-fantasy-belief-largely-inherited-from-conti",
    156, 156,
    "Haskell says Algarotti retained his belief in creative fantasy even in his most neoclassical phase and that this belief was largely inherited from Conti.",
    "As we will see, even in his most neo-classical phase Algarotti never lost his belief in the vital importance of creative fantasy, and it is certain that this belief was largely inherited from Conti.",
    "The inherited relation is Haskell's assertion; 'largely' is retained.",
    ["cand-0046", "cand-0992", "cand-0826"], True,
)
add_statement(
    "st-chp10-p320-eighteenth-century-fantasy-discourse-and-bettinelli", "cand-0992", "cand-9735", "support-for-unfettered-imagination-merges-into-genius-acceptance",
    156, 156,
    "Haskell traces support for the artist's right to unfettered imagination through eighteenth-century Italian thought and says it merged into acceptance of the artistic genius, as expressed in Bettinelli's 1769 work.",
    "Indeed, a thin trickle of support for the artist’s right to make use of his unfettered-imagination runs right through Italian eighteenth-century thought until with Saverio Bettinelli’s Delientusiasmo per le Belle Arti (Milan, 1769) it merges into outright acceptance of the ‘genius’ with all his vagaries.",
    "This is Haskell's broad intellectual-historical account. Print reads Dell'entusiasmo; the canonical OCR title remains unchanged. The cited work is named, but the claim does not establish an exact causal pathway.",
    ["cand-0992", "cand-0369", "cand-0370", "cand-9735", "cand-3418"], False,
)
add_statement(
    "st-chp10-p320-lodoli-artistic-ideas-more-immediately-stimulating-than-conti", "cand-1411", "cand-0826", "ideas-more-immediately-stimulating-but-not-more-effective-than-conti",
    157, 157,
    "Haskell says Lodoli's artistic ideas proved more immediately stimulating than Conti's, even if they were no more effective in practice.",
    "But there was in Venice during the first half of the eighteenth century a thinker whose artistic ideas were to prove far more immediately stimulating than those of Conti, even if no more effective in practice.",
    "The comparison is Haskell's evaluation and distinguishes immediate stimulation from practical effectiveness.",
    ["cand-1411", "cand-0826", "cand-2719"], False,
)
add_statement(
    "st-chp10-p320-lodoli-frequented-smith-grand-canal-palace", "cand-1411", "cand-9737", "frequented-consul-smiths-palace-on-grand-canal",
    157, 157,
    "Haskell says Padre Carlo Lodoli was among the men who frequented Consul Smith's palace on the Grand Canal.",
    "Among the men who frequented Consul Smith’s palace on the Grand Canal was Padre Carlo Lodoli",
    "The palace is unnamed; do not assign it a building identity from this passage alone.",
    ["cand-1411", "cand-2440", "cand-9737", "cand-8178"], True,
)
add_statement(
    "st-chp10-p320-lodoli-brother-of-minori-osservanti", "cand-1411", "cand-9736", "brother-of-religious-order",
    157, 157,
    "Haskell describes Lodoli as a brother of the Minori Osservanti.",
    "a brother of the Minori Osservanti.2",
    "The order is named; footnote 2 awaits canonical note L309.",
    ["cand-1411", "cand-9736"], True,
    {"footnote_marker": 2, "pending_note_source_line": 309},
)
add_statement(
    "st-chp10-p320-lodoli-studied-mathematics-and-french", "cand-1411", None, "studied-mathematics-and-french",
    158, 158,
    "Haskell says Lodoli had studied mathematics and French.",
    "Lodoli had studied mathematics and French",
    "The source does not specify where or when these studies took place.",
    ["cand-1411"],
)
add_statement(
    "st-chp10-p320-lodoli-travelled-and-returned-to-venice-1720", "cand-1411", "cand-2719", "travelled-in-rome-and-italy-returned-to-venice-in-1720",
    158, 158,
    "Haskell says Lodoli travelled in Rome and other parts of Italy and returned at age 30 to Venice in 1720.",
    "travelled in Rome and other parts of Italy and returned at the age of 30 to his native Venice in 1720.",
    "Preserve the stated age and year; no birth date or exact itinerary is inferred.",
    ["cand-1411", "cand-4490", "cand-3461", "cand-2719"], True,
)
add_statement(
    "st-chp10-p320-lodoli-opened-private-school-for-families-and-friends", "cand-1411", "cand-9738", "opened-private-school-for-sons-of-leading-families-and-friends",
    158, 158,
    "Haskell says Lodoli opened a private school for the sons of some leading families and his friends.",
    "Here he opened a private school for the sons of some of the leading families as well as those of his friends.",
    "The school is not named and the families/pupils are not identified.",
    ["cand-1411", "cand-9738"], True,
)
add_statement(
    "st-chp10-p320-lodoli-school-run-on-advanced-modern-lines", "cand-9738", None, "run-on-advanced-modern-lines",
    158, 158,
    "Haskell says Lodoli's school was run on the most advanced, modern lines.",
    "This school was run on the most advanced, modern lines.",
    "This is Haskell's characterization; no specific curriculum or institutional rules are listed in this sentence.",
    ["cand-9738"],
)
add_statement(
    "st-chp10-p320-galileo-favourite-author-of-lodoli", "cand-1411", "cand-1105", "named-as-favourite-author-of-lodoli",
    158, 159,
    "Haskell names Galileo among Lodoli's favourite authors.",
    "Lodoli’s favourite authors were\nGalileo",
    "The sentence continues with Bacon as another favourite author.",
    ["cand-1411", "cand-1105", "cand-0155"], True,
)
add_statement(
    "st-chp10-p320-bacon-favourite-author-of-lodoli", "cand-1411", "cand-0155", "named-as-favourite-author-of-lodoli",
    158, 159,
    "Haskell names Bacon among Lodoli's favourite authors.",
    "Lodoli’s favourite authors were\nGalileo and Bacon",
    "The statement preserves Haskell's plural description of favourite authors.",
    ["cand-1411", "cand-1105", "cand-0155"], True,
)
add_statement(
    "st-chp10-p320-lodoli-took-pupils-to-visit-libraries-and-scholars", "cand-1411", None, "took-pupils-to-visit-libraries-and-scholars",
    159, 159,
    "Haskell says Lodoli took his pupils to visit libraries and distinguished scholars.",
    "he took his pupils to visit libraries and distinguished scholars.",
    "The libraries and scholars are unnamed.",
    ["cand-1411", "cand-9738"],
)
add_statement(
    "st-chp10-p320-lodoli-taught-cicero-on-duties", "cand-1411", "cand-0747", "taught-from-cicero-on-duties-of-man",
    159, 159,
    "Haskell says Lodoli brought pupils up on Cicero concerning the duties of man.",
    "He brought them up on Cicero",
    "The particular work by Cicero is not specified; the teaching claim is reported by Haskell.",
    ["cand-1411", "cand-0747", "cand-9738"], True,
)
add_statement(
    "st-chp10-p320-lodoli-taught-puffendorf-on-duties", "cand-1411", "cand-2069", "taught-from-puffendorf-on-duties-of-man",
    159, 159,
    "Haskell says Lodoli brought pupils up on Puffendorf concerning the duties of man.",
    "Puffendorf on the duties of man.",
    "The source's printed spelling Puffendorf is retained; the particular work is not specified.",
    ["cand-1411", "cand-2069", "cand-9738"], True,
)
add_statement(
    "st-chp10-p320-lodoli-dispute-with-inquisitori-over-state-documents", "cand-1411", "cand-9739", "dispute-over-using-state-documents-in-literary-teaching",
    159, 159,
    "Haskell says Lodoli had a brush with the Inquisitori di Stato because he insisted on using State documents as material for grammatical and literary investigation.",
    "And he had a brush with the Inquisitori di Stato because he insisted on using State documents as suitable subject-matter for grammatical and literary investigation.",
    "No proceeding, date, or specific document is named.",
    ["cand-1411", "cand-9739"], True,
)
add_statement(
    "st-chp10-p320-lodoli-admired-vico", "cand-1411", "cand-2771", "admired-vico",
    159, 160,
    "Haskell says Lodoli was a keen admirer of Vico.",
    "He was a keen admirer of\nVico",
    "This is Haskell's characterization of Lodoli's regard for Vico.",
    ["cand-1411", "cand-2771"], True,
)
add_statement(
    "st-chp10-p320-lodoli-among-those-who-persuaded-vico-to-write-autobiography", "cand-1411", "cand-9740", "among-those-who-persuaded-vico-to-write-autobiography",
    160, 161,
    "Haskell says Lodoli was among those who persuaded Vico to write his Autobiography.",
    "he was among those who persuaded the Neapolitan philosopher to write his\nAutobiography",
    "Lodoli was one among multiple persuaders; the work is first referred to by a generic title.",
    ["cand-1411", "cand-2771", "cand-9740"], True,
)
add_statement(
    "st-chp10-p320-vico-autobiography-first-published-in-venice", "cand-9740", "cand-2719", "first-published-in-venice",
    161, 161,
    "Haskell says Vico's Autobiography was first published in Venice.",
    "Autobiography, which was first published in Venice.3",
    "Footnote 3 awaits canonical note L310; the publication venue is the city, not the Republic as a publisher.",
    ["cand-2771", "cand-9740", "cand-2719"], False,
    {"footnote_marker": 3, "pending_note_source_line": 310},
)
add_statement(
    "st-chp10-p320-lodoli-appointed-chief-censor-of-republic", "cand-1411", "cand-8838", "appointed-chief-censor-with-conscientious-liberal-duties",
    161, 161,
    "Haskell says Lodoli was appointed chief censor of the Republic and carried out the duties conscientiously but in a liberal spirit.",
    "After some years he was appointed chief censor of the Republic with duties which he carried out conscientiously but in a liberal spirit.",
    "The exact appointment date and formal title are not supplied.",
    ["cand-1411", "cand-8838"], True,
)
add_statement(
    "st-chp10-p320-lodoli-associated-with-andrea-memmo", "cand-1411", "cand-1642", "associated-with-enlightened-venetian-figure-especially",
    161, 161,
    "Haskell says Lodoli became associated with more enlightened figures in Venice, especially Andrea Memmo.",
    "He soon became associated with a number of the more enlightened figures in the city—Andrea Memmo, especially",
    "'Especially' marks Memmo's particular prominence in the account.",
    ["cand-1411", "cand-9741", "cand-1642"], True,
)
add_statement(
    "st-chp10-p320-lodoli-associated-with-angelo-querini", "cand-1411", "cand-2075", "also-associated-with-enlightened-venetian-figure",
    161, 161,
    "Haskell also names Angelo Querini among the more enlightened figures associated with Lodoli.",
    "but also Angelo Querini",
    "The relation is reported by Haskell without further dates or institutional affiliation.",
    ["cand-1411", "cand-9741", "cand-2075"], True,
)
add_statement(
    "st-chp10-p320-lodoli-associated-with-pasquali-publisher", "cand-1411", "cand-1844", "also-associated-with-giambattista-pasquali-publisher",
    161, 162,
    "Haskell also names Giambattista Pasquali, identified as a publisher, among the figures associated with Lodoli.",
    "and Giambattista\nPasquali, the publisher",
    "The source gives Pasquali's occupational role here but no specific publication.",
    ["cand-1411", "cand-9741", "cand-1844"], True,
)
add_statement(
    "st-chp10-p320-associated-figures-nearly-all-smiths-friends", "cand-9741", "cand-2440", "nearly-all-associated-figures-were-smiths-friends",
    162, 162,
    "Haskell says nearly all the associated figures were also friends of Consul Smith.",
    "Nearly all these were also friends of Consul Smith",
    "'Nearly all' is retained; the sentence does not identify every friend or establish formal association for every member of the collective.",
    ["cand-9741", "cand-2440"], True,
)
add_statement(
    "st-chp10-p320-lodoli-had-admirers-among-venetian-aristocracy", "cand-1411", "cand-9742", "had-admirers-among-venetian-aristocracy-for-a-time",
    162, 162,
    "Haskell says Lodoli had a number of admirers among the Venetian aristocracy for a time.",
    "for a time he had a number of admirers among the Venetian aristocracy.",
    "The group and duration are not further specified.",
    ["cand-1411", "cand-9742"], True,
)
add_statement(
    "st-chp10-p320-lodoli-in-touch-with-montesquieu", "cand-1411", "cand-1696", "in-touch-with-outside-venice",
    162, 162,
    "Haskell says Lodoli was in touch with Montesquieu outside Venice.",
    "Outside Venice he was in touch with Montesquieu",
    "No dates or medium of contact are specified.",
    ["cand-1411", "cand-1696"], True,
)
add_statement(
    "st-chp10-p320-lodoli-in-touch-with-scipione-maffei", "cand-1411", "cand-1487", "in-touch-with-outside-venice",
    162, 162,
    "Haskell says Lodoli was also in touch with Scipione Maffei outside Venice.",
    "and Scipione Maffei.",
    "The statement is the completion of the preceding contact list; no dates or medium of contact are specified.",
    ["cand-1411", "cand-1487"], True,
)
add_statement(
    "st-chp10-p320-lodoli-gruff-outspoken-and-sentence-continues", "cand-1411", None, "described-as-uncouth-gruff-and-unusually-outspoken",
    163, 163,
    "Haskell describes Lodoli as uncouth and gruff and says his outspokenness would hardly have been tolerated in anyone else.",
    "In appearance Lodoli was uncouth and his manner was gruff. He indulged in a degree of outspokenness which would hardly have been tolerated in anyone else; but",
    "The sentence continues on p.321; the contrast introduced by 'but' is not inferred before the continuation is read.",
    ["cand-1411"], False,
    {"continuation_segment_id": NEXT_SEGMENT, "statement_continues": True},
)

previous_hits = [row for row in statements if row.get("statement_id") == PREVIOUS_QUOTATION]
if len(previous_hits) != 1:
    raise SystemExit(f"expected one p.319 quotation statement, found {len(previous_hits)}")
previous_statement = previous_hits[0]
q = previous_statement.get("qualifiers", {})
if previous_statement.get("segment_id") != PREVIOUS_SEGMENT or q.get("statement_continues") is not True or q.get("continuation_segment_id") != SEGMENT:
    raise SystemExit("p.319 quotation continuation state changed")
if previous_statement.get("original_quote", "").splitlines()[-1] != "‘The painter’s fantasy’, he wrote,4 ‘should be expressed in breadth of knowledge, in subtlety and correctness of draughtsmanship, in liveliness and vigour of execution. Moreover,":
    raise SystemExit("p.319 quotation anchor changed")
previous_statement_updated = json.loads(json.dumps(previous_statement))
previous_statement_updated["qualifiers"]["statement_continues"] = False
previous_statement_updated["qualifiers"]["continuation_completion_quote"] = "it should excite the senses and the passions, and grace requires it to move away somewhat from nature so as to be the better adapted to the judgement and pleasure of the senses.’"
previous_statement_updated["qualifiers"]["continuation_completed_by_segment_id"] = SEGMENT
previous_statement_updated["qualifiers"]["claim"] = (
    "Haskell quotes Conti as saying painterly fantasy requires breadth of knowledge, subtle and correct drawing, lively and vigorous execution, "
    "should excite the senses and passions, and may move somewhat away from nature to suit judgment and sensory pleasure."
)

statement_ids = {row["statement_id"] for row in statements}
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("p.320 statement ID already exists")
candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = [previous_statement_updated if row is previous_statement else row for row in statements] + new_statements

old_note = coverage[PREVIOUS_SEGMENT].get("note", "")
needle = "The final quoted word 'Moreover,' continues at " + SEGMENT
if old_note.count(needle) != 1:
    raise SystemExit("p.319 coverage note does not contain the expected quote continuation")
coverage[PREVIOUS_SEGMENT]["note"] = old_note.replace(
    needle,
    "The quotation closes on p.320 L152; p.319 remains partial pending footnotes at canonical notes L304–307",
).replace(
    "coverage remains partial pending that continuation and those notes.",
    "coverage remains partial pending those notes.",
)
coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L152-163",
    "note": (
        f"Read printed p.320 against CHP-10.pdf physical p.53. L152 closes Conti's p.319 quotation; Haskell then cautiously suggests a "
        "modello by Tiepolo or Pittoni may justify it, while explicitly warning that detached references cannot establish coherent "
        "aesthetic ideas or major painterly influence. L154–156 records elder Zanetti's notice of the colour-woodcut process, Algarotti's "
        "correspondence and inheritance of Conti's fantasy ideas, and Haskell's broad account through Bettinelli. L157–163 introduces "
        "Lodoli and records his order, Smith's unnamed palace, education/travel, school, authors and teaching, Inquisitori dispute, Vico's "
        "Autobiography, censorship office, associates, Smith connections, and contacts outside Venice. "
        f"Added {len(new_candidates)} candidates, {len(new_mentions)} exact mentions, and {len(new_statements)} statements; "
        "identity and formal relation decisions remain deferred. Print comparison: OCR `Delientusiasmo` is printed "
        "`Dell'entusiasmo`; footnote marker at canonical L310 is printed 3, not OCR 8. Footnotes 1–3 await canonical notes L308–310. L163's "
        "final 'but' continues at " + NEXT_SEGMENT + "; coverage remains partial pending that continuation and the notes."
    ),
})

print(f"p.320 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements; close one p.319 quotation")
print(f"coverage: p.320 reviewed/partial; next source segment {NEXT_SEGMENT}; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
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
