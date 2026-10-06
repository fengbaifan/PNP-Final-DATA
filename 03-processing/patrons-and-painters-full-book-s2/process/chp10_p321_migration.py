"""Controlled S2 migration for printed p.321; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l165-173"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l151-163"
NEXT_SEGMENT = "chp-10:10_CHP-10_sec_ii:l175-178"
PREVIOUS_STATEMENT = "st-chp10-p320-lodoli-gruff-outspoken-and-sentence-continues"
EXPECTED_MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENT_SHA = "2c5d35a670267696a93aa11f9c12a5d3baf3edc64196ffc240d530413bddc06c"
BACKUP_SUFFIX = ".bak-s2-chp10-p321-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.321 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[164:173]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.321 S2 source segment changed")
if segment_lines[0] != "[Page 321]" or not segment_lines[-1].endswith("intention had been"):
    raise SystemExit("p.321 segment boundaries changed")

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
if table_state != (9729, 9742, 20523, 9078):
    raise SystemExit(f"table state changed; re-read current table counts before migration: {table_state}")

coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.321 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.320 to remain partial pending its notes")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.321 already has S2 mention or statement rows")

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


add_candidate("cand-9743", "Great noblemen in Lodoli's reported argument (unnamed social class)", "", "The quotation names a social class but no individuals; its role in the passage is conditional, not a documented commission list.", 167)
add_candidate("cand-9744", "Good craftsmen in Lodoli's reported argument (unnamed group)", "", "The quotation describes unnamed craftsmen whose livelihood is discussed conditionally.", 167)
add_candidate("cand-9745", "Radicals tolerated in conservative society (unnamed social group)", "", "Haskell's general characterization of the logic attached to Lodoli's reported remark; no people are named.", 167)
add_candidate("cand-9746", "Functional architecture based on reason and comfort as Lodoli's position", "term", "Haskell presents the position as mediated by contemporaries because Lodoli's own writings were lost.", 168)
add_candidate("cand-9747", "Late Baroque architectural style in Lodoli's account", "term", "The style of Lodoli's youth which Haskell says he rejected; retain the passage-specific architectural context.", 168)
add_candidate("cand-9748", "Classicism beginning to replace late Baroque architecture in Lodoli's account", "term", "The emerging style Haskell says Lodoli also rejected; do not merge automatically with other classicism candidates.", 168)
add_candidate("cand-9749", "Classical art as an authority questioned by Lodoli", "term", "The passage says Lodoli challenged its supposedly infallible authority and notes differing interpretations.", 168)
add_candidate("cand-9750", "Architecture of antiquity investigated by Lodoli", "term", "Haskell describes Lodoli's dispassionate investigation; no particular ancient building beyond the Pantheon is identified.", 168)
add_candidate("cand-9751", "Unnamed writer quoted on Lodoli's overwhelming manner", "person", "The body says only 'one writer'; p.321 footnote 1 may identify the cited source, which remains pending note review.", 169)
add_candidate("cand-9752", "Critics who shared Lodoli's views of the Baroque (unnamed group)", "", "A group in Haskell's account of the 'impudent impostor' characterization; individual critics are not named.", 169)
add_candidate("cand-9753", "Minori Osservanti monastery outside S. Francesco della Vigna", "place", "The monastery is not named separately; retain its distinction from both the order and the nearby church.", 169)
add_candidate("cand-9754", "Church of S. Francesco della Vigna", "place", "Named as a spatial reference for the unidentified Minori Osservanti monastery.", 169)
add_candidate("cand-9755", "Ospedale della Pietà (institution named in the Massari modello account)", "institution", "The hospital is the institution whose governor invited Lodoli to inspect the model; keep distinct from its church building.", 170)
add_candidate("cand-9756", "Giorgio Massari's modello for the proposed Church of the Pietà", "work", "The architectural model is named but not described further; distinguish it from the proposed church and later building.", 170)
add_candidate("cand-9757", "Unidentified governor of the Ospedale della Pietà", "person", "The governor is not named; retained as the inviter in the account of Lodoli's review of Massari's model.", 170)
add_candidate("cand-9758", "More open-minded thinkers of Lodoli's day (unnamed group)", "", "Haskell says Lodoli made an impact on some of this group but gives no individual names.", 171)

candidate_ids.update(row["candidate_id"] for row in new_candidates)
new_mentions = []


def line_offset(line_no):
    if line_no < 165:
        raise SystemExit(f"p.321 mention starts before its segment: L{line_no}")
    return sum(len(line) + 1 for line in segment_lines[:line_no - 165])


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
    (166, "this", "cand-1411", "Corefers to Lodoli's outspokenness at the end of p.320 L163.", 0),
    (166, "he", "cand-1411", "Corefers to Lodoli in the explanation of why his outspokenness was tolerated.", 0),
    (166, "him", "cand-1411", "Corefers to Lodoli, who was not taken wholly seriously.", 0),
    (167, "great noblemen", "cand-9743", "An unnamed social class in Lodoli's quoted argument.", 0),
    (167, "their generosity", "cand-9743", "Corefers to the great noblemen.", 0),
    (167, "good craftsmen", "cand-9744", "An unnamed group whose livelihood is described conditionally.", 0),
    (167, "radicals", "cand-9745", "Haskell's general comparison after the quotation.", 0),
    (168, "Lodoli", "cand-1411", "Named as the subject of Haskell's account of his ideas.", 0),
    (168, "functional architecture", "cand-9746", "A position attributed through contemporaries, not Lodoli's surviving writings.", 0),
    (168, "reason and comfort", "cand-9746", "The criteria Haskell says Lodoli made arbiters of style.", 0),
    (168, "late Baroque", "cand-9747", "A style Haskell says Lodoli rejected.", 0),
    (168, "classicism", "cand-9748", "The emerging style Haskell says Lodoli also rejected.", 0),
    (168, "architecture of antiquity", "cand-9750", "The field of Lodoli's investigation in Haskell's account.", 0),
    (168, "infallible authority", "cand-9749", "The authority attributed to classical art/antiquity and challenged by Lodoli.", 0),
    (168, "the Pantheon", "cand-4236", "Named as the ancient building Lodoli said was not perfect.", 0),
    (168, "classical art", "cand-9749", "The object of differing interpretations in the reported account.", 0),
    (169, "Lodoli’s", "cand-1411", "Named as the subject of the account of influence on current architecture.", 0),
    (169, "one writer", "cand-9751", "Unnamed in the body; footnote 1 awaits review at canonical note L311.", 0),
    (169, "critics who shared his views of the Baroque", "cand-9752", "An unnamed group said to regard him as an impudent impostor.", 0),
    (169, "he", "cand-1411", "Corefers to Lodoli in the account of how critics regarded him.", 0),
    (169, "monastery of his own Order", "cand-9753", "The building where Lodoli made functional modifications; distinct from the order.", 0),
    (169, "Minori Osservanti", "cand-9736", "Reuses the p.320 candidate for the religious order.", 0),
    (169, "S. Francesco della Vigna", "cand-9754", "Named as the church outside which the monastery stood.", 0),
    (170, "He", "cand-1411", "Corefers to Lodoli, the invitee.", 0),
    (170, "governor", "cand-9757", "The unnamed office-holder who invited Lodoli.", 0),
    (170, "Ospedale della Pietà", "cand-9755", "The institution whose governor issued the invitation.", 0),
    (170, "Lodoli", "cand-1411", "Named as the reviewer of Massari's model.", 0),
    (170, "Massari’s", "cand-1562", "Reuses the indexed Giorgio Massari candidate.", 0),
    (170, "tnodello", "cand-9756", "OCR reads tnodello; the print reads modello.", 0),
    (170, "proposed church", "cand-8551", "Reuses the Church of the Pietà place candidate; exact identity remains for S3.", 0),
    (170, "the architect", "cand-1562", "Local textual coreference to Massari after his modello is introduced; not external identity verification.", 0),
    (170, "Palladio", "cand-1807", "Named as an example in the architect's hypothetical comparison.", 0),
    (170, "Vignola", "cand-2775", "Named as an example in the architect's hypothetical comparison.", 0),
    (171, "he", "cand-1411", "Corefers to Lodoli in the account of his effect on other thinkers.", 0),
    (171, "more open-minded thinkers of the day", "cand-9758", "An unnamed group affected by Lodoli according to Haskell.", 0),
    (172, "Gaspare Gozzi", "cand-1220", "Reuses the indexed essayist candidate.", 0),
    (172, "Lodoli in mind", "cand-1411", "Haskell's inferred referent of Gozzi's complaint.", 0),
    (173, "Francesco Algarotti", "cand-0048", "Reuses the index candidate specifically linking Algarotti with Carlo Lodoli.", 0),
    (173, "Lodoli’s opinions", "cand-1412", "Uses the indexed Lodoli–Algarotti subentry for the relation context.", 0),
    (173, "their author", "cand-1411", "The author of the opinions is Lodoli.", 0),
    (173, "Algarotti’s interest", "cand-0048", "The interest in Lodoli that he had originally welcomed.", 0),
]

for item in MENTIONS:
    add_mention(*item)
new_mentions.sort(key=lambda row: int(row["start_char"]))
for index, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-s2-ch10-p321-{index:04d}"
for left, right in zip(new_mentions, new_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping p.321 mention spans: {left['surface_form']} and {right['surface_form']}")

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, speaker="Haskell",
                  text_layer="authorial claim", relation_candidate=False, extra=None):
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in p.321: {statement_id}")
    if any(cid not in candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 321,
        "pdf_physical_page": 54,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
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
    "st-chp10-p321-lodoli-enjoyed-licensed-jester-privileges", "cand-1411", None, "enjoyed-some-privileges-of-licensed-jester",
    166, 166,
    "Haskell says Lodoli enjoyed some of the privileges of a licensed jester.",
    "He enjoyed some of the privileges of the licensed jester.",
    "'Some' is retained; 'licensed jester' is Haskell's metaphor, not an office or formal title.",
    ["cand-1411"],
)
add_statement(
    "st-chp10-p321-lodoli-turned-back-from-awkward-situations", "cand-1411", None, "knew-how-to-turn-back-when-situation-became-awkward",
    166, 166,
    "Haskell says Lodoli knew how to turn back when a situation was becoming awkward.",
    "Besides, he knew how to turn back when the situation was becoming awkward.",
    "The source gives no specific episode; retain this as Haskell's general characterization.",
    ["cand-1411"],
)
add_statement(
    "st-chp10-p321-lodoli-quoted-on-noble-luxury-and-craftsmen", "cand-1411", None, "did-not-object-to-noble-luxury-because-generosity-sustained-craftsmen",
    167, 167,
    "Haskell quotes Lodoli as saying he did not object to great noblemen's luxury because without their generosity, ambition, or whim many craftsmen would starve.",
    "‘never objected to the luxury of great noblemen, for without their generosity, ambition or whim countless good craftsmen would die of starvation’",
    "The words are attributed to Lodoli by Haskell. Preserve the conditional counterfactual and do not turn it into evidence of a specific commission or patronage relationship.",
    ["cand-1411", "cand-9743", "cand-9744"], speaker="Carlo Lodoli (quoted by Haskell)",
    text_layer="reported quotation",
)
add_statement(
    "st-chp10-p321-haskell-characterizes-remark-as-radical-logic", "cand-1411", "cand-9745", "remark-compared-to-radical-logic-tolerated-in-conservative-society",
    167, 167,
    "Haskell characterizes the reasoning as a kind often used by radicals tolerated in conservative society.",
    "—the sort of perverse logic that has often been used by radicals tolerated in a conservative society.",
    "This is Haskell's evaluative comparison following the quotation, not Lodoli's wording.",
    ["cand-1411", "cand-9745"],
)
add_statement(
    "st-chp10-p321-lodoli-moral-political-ideas-sometimes-difficult-to-express", "cand-1411", None, "moral-and-political-ideas-sometimes-difficult-to-express-openly",
    168, 168,
    "Haskell says Lodoli must sometimes have found it difficult to express his moral and political ideas openly.",
    "Though Lodoli must sometimes have found it difficult to express openly his moral and political ideas",
    "'Must sometimes' is retained as Haskell's inference, not stated certainty.",
    ["cand-1411"],
)
add_statement(
    "st-chp10-p321-lodoli-saw-arts-as-inextricably-linked", "cand-1411", None, "viewed-the-arts-as-inextricably-linked",
    168, 168,
    "Haskell says that, in Lodoli's view, these matters were inextricably linked.",
    "though in his view they were all inextricably linked.",
    "The antecedent of 'they' is retained as broad in the text; this does not assume a more specific theory than Haskell states.",
    ["cand-1411"],
)
add_statement(
    "st-chp10-p321-lodoli-functional-architecture-reason-comfort-style", "cand-1411", "cand-9746", "insisted-on-functional-architecture-with-reason-and-comfort-as-arbiters",
    168, 168,
    "As interpreted by most contemporaries because his writings were lost, Lodoli insisted on functional architecture in which reason and comfort were the final arbiters of style.",
    "As interpreted for us by most of his contemporaries (for his own writings were lost), Lodoli insisted on a wholly functional architecture in which reason and comfort should be the final arbiters of style.",
    "This is a mediated account of Lodoli's position, not a quotation from his surviving writings.",
    ["cand-1411", "cand-1420", "cand-9746"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-lodoli-rejected-late-baroque-architecture", "cand-1411", "cand-9747", "rejected-late-baroque-of-his-youth",
    168, 168,
    "Haskell says Lodoli rejected the late Baroque of his own youth.",
    "In this way he was rejecting not merely the late Baroque of his own youth",
    "The source's claim concerns Lodoli's architectural views; it is Haskell's characterization.",
    ["cand-1411", "cand-9747"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-lodoli-rejected-emerging-classicism", "cand-1411", "cand-9748", "also-rejected-classicism-beginning-to-replace-late-baroque",
    168, 168,
    "Haskell says Lodoli also rejected the classicism beginning to replace the late Baroque.",
    "but also the classicism that was beginning to replace it.",
    "'Beginning to replace' is retained as a contemporaneous transition, not a completed replacement.",
    ["cand-1411", "cand-9748", "cand-9747"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-lodoli-investigated-architecture-of-antiquity", "cand-1411", "cand-9750", "dispassionately-investigated-architecture-of-antiquity",
    168, 168,
    "Haskell says Lodoli's dispassionate investigation of ancient architecture shocked his contemporaries.",
    "Nothing'shocked his contemporaries more than his dispassionate investigation of the architecture of antiquity.",
    "The print reads 'Nothing shocked'; the OCR joins the words. The judgment of contemporaries is Haskell's account.",
    ["cand-1411", "cand-9750"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-lodoli-questioned-antiquitys-infallible-authority", "cand-1411", "cand-9749", "called-infallible-classical-authority-into-question",
    168, 168,
    "Haskell says Lodoli did not condemn ancient architecture outright but called its supposed infallible authority into question.",
    "He certainly did not condemn it out of hand, but he called its infallible authority into question.",
    "The antecedent of 'it' is the architecture of antiquity; the criticism is not a wholesale condemnation.",
    ["cand-1411", "cand-9749", "cand-9750"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-lodoli-said-pantheon-was-not-perfect", "cand-1411", "cand-4236", "said-pantheon-was-not-perfect",
    168, 168,
    "Haskell reports that Lodoli said even the Pantheon was not perfect.",
    "Even the Pantheon, he said, was not perfect;",
    "This is a reported judgment attributed to Lodoli; it does not specify which feature he criticized.",
    ["cand-1411", "cand-4236"], speaker="Carlo Lodoli (reported by Haskell)", text_layer="reported claim",
    relation_candidate=True,
)
add_statement(
    "st-chp10-p321-lodoli-classical-art-had-different-interpretations", "cand-1411", "cand-9749", "said-classical-art-had-been-interpreted-differently",
    168, 168,
    "Haskell reports Lodoli's point that classical art had been interpreted in different ways.",
    "and in any case everyone had interpreted classical art in a different manner.",
    "The claim is kept within Haskell's reported account; 'everyone' is not expanded into a list of interpreters.",
    ["cand-1411", "cand-9749"], speaker="Carlo Lodoli (reported by Haskell)", text_layer="reported claim",
)
add_statement(
    "st-chp10-p321-lodoli-influence-on-current-architecture-negligible", "cand-1411", None, "influence-on-current-architecture-described-as-negligible",
    169, 169,
    "Haskell says Lodoli's influence on current architecture was negligible, perhaps because one writer found his manner overwhelming.",
    "As far as current architecture went, Lodoli’s influence was negligible, perhaps because",
    "'Perhaps' is retained; the causal explanation points to the separate quotation from an unnamed writer.",
    ["cand-1411"],
)
add_statement(
    "st-chp10-p321-unnamed-writer-complained-of-lodoli-overwhelming-manner", "cand-9751", "cand-1411", "writer-complained-lodoli-was-overwhelming",
    169, 169,
    "An unnamed writer complained that Lodoli was overwhelming when alone and caused days of indigestion.",
    "‘when he is on his own he is so overwhelming that he gives me indigestion for days afterwards’",
    "The writer is unnamed in the body; p.321 note 1 awaits review at canonical L311. 'Indigestion' is retained as the quoted metaphor.",
    ["cand-9751", "cand-1411"], speaker="Unnamed writer (quoted by Haskell)", text_layer="reported quotation",
)
add_statement(
    "st-chp10-p321-critics-regarded-lodoli-as-impudent-impostor", "cand-9752", "cand-1411", "critics-considered-lodoli-an-impudent-impostor",
    169, 169,
    "Haskell says that even critics who shared Lodoli's views of the Baroque considered him an impudent impostor.",
    "even among critics who shared his views of the Baroque he was considered to be an ‘impudent impostor’.1",
    "The passive attribution is kept to an unnamed group; footnote 1 awaits canonical note L311.",
    ["cand-9752", "cand-1411", "cand-9747"], relation_candidate=True,
    extra={"footnote_marker": 1, "pending_note_source_line": 311},
)
add_statement(
    "st-chp10-p321-lodoli-modified-order-monastery-on-one-occasion", "cand-1411", "cand-9753", "introduced-functional-modifications-into-order-monastery-once",
    169, 169,
    "Haskell says Lodoli practised only once, introducing functional modifications into a monastery of his order outside S. Francesco della Vigna.",
    "He himself only practised on one occasion, when he introduced some functional modifications into the monastery of his own Order, the Minori Osservanti, outside'S. Francesco della Vigna.2",
    "The print reads 'outside S.'; OCR adds an apostrophe. Note 2 awaits canonical L312. The monastery is kept distinct from the Minori Osservanti order and from the nearby church.",
    ["cand-1411", "cand-9753", "cand-9736", "cand-9754"], relation_candidate=True,
    extra={"footnote_marker": 2, "pending_note_source_line": 312},
)
add_statement(
    "st-chp10-p321-pieta-governor-invited-lodoli-to-view-massari-model", "cand-9757", "cand-1411", "invited-lodoli-to-inspect-massari-model-for-proposed-church",
    170, 170,
    "Haskell says the governor of the Ospedale della Pietà invited Lodoli to look at Giorgio Massari's modello for the proposed church.",
    "He was once invited by the governor of the Ospedale della Pietà to look at Massari’s tnodello for the proposed church.",
    "The print reads 'modello'; OCR reads 'tnodello'. The proposed church reuses the Church of the Pietà place candidate; identity remains for S3.",
    ["cand-9757", "cand-9755", "cand-1411", "cand-1562", "cand-9756", "cand-8551"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-lodoli-criticised-massari-model-on-logical-grounds", "cand-1411", "cand-9756", "criticised-model-on-logical-grounds",
    170, 170,
    "Haskell says Lodoli began criticizing the model on logical grounds.",
    "When Lodoli began to criticise this on logicalgrounds",
    "The print reads 'logical grounds'; OCR joins the words. The criticism is directed at the model, not at Massari personally.",
    ["cand-1411", "cand-9756"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-massari-explained-risk-of-new-conception", "cand-1562", None, "hypothetically-said-conventional-facade-would-be-chosen-over-new-design",
    170, 170,
    "The architect answering after Massari's model says that if he submitted a wholly new conception, a plan imitating Palladio or Vignola would be chosen instead, and asks who would support his family.",
    "‘If I were to submit some totally new conception, however reasonable, I could be quite sure that the plans of some other architect, imitating for example a façade of Palladio or Vignola, would be chosen instead of mine. And then who would support my family?’",
    "The answer is locally attributed to Massari through 'the architect' after his model is named; this is textual coreference, not external verification. The claim is hypothetical and does not establish that Palladio or Vignola designed the proposed church.",
    ["cand-1562", "cand-1807", "cand-2775"], speaker="The architect answering after Massari's modello (local coreference to Giorgio Massari)",
    text_layer="reported quotation",
)
add_statement(
    "st-chp10-p321-lodoli-impacted-open-minded-thinkers", "cand-1411", "cand-9758", "made-impact-on-some-open-minded-thinkers",
    171, 171,
    "Haskell says Lodoli made an impact on some of the more open-minded thinkers of the day.",
    "Yet he made an impact on some of the more open-minded thinkers of the day.",
    "'Some' is retained; the group is unnamed.",
    ["cand-1411", "cand-9758"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-gozzi-must-have-had-lodoli-in-mind", "cand-1220", "cand-1411", "must-certainly-have-had-lodoli-in-mind-in-ornamentation-critique",
    172, 172,
    "Haskell says Gaspare Gozzi must certainly have had Lodoli in mind when criticizing ornamentation-heavy building.",
    "The essayist Gaspare Gozzi must certainly have had Lodoli in mind when he complained",
    "'Must certainly' is retained as Haskell's inference; it is not direct evidence that Gozzi named Lodoli.",
    ["cand-1220", "cand-1411"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-gozzi-quoted-on-building-for-passers-by", "cand-1220", None, "criticised-building-for-passers-by-over-inhabitants",
    172, 172,
    "Haskell quotes Gozzi criticizing building that serves the eyes of passers-by more than its inhabitants and imagining that empty houses would seem to contain giants.",
    "‘we put so much into ornamentation that we build more for the eyes of passers-by than for the people who actually five in houses: and if someone were to come from a country where houses are used just as shelter from the cold and the rain and were to see our houses and not their inhabitants, he would think that they must all be giants’.3",
    "The print reads 'live in houses'; OCR reads 'five'. The giant comparison is retained as Gozzi's metaphor. Note 3 awaits canonical L313.",
    ["cand-1220"], speaker="Gasparo Gozzi (quoted by Haskell)", text_layer="reported quotation",
    extra={"footnote_marker": 3, "pending_note_source_line": 313},
)
add_statement(
    "st-chp10-p321-algarotti-somewhat-feared-public-opinion", "cand-0048", None, "somewhat-feared-public-opinion",
    173, 173,
    "Haskell says Francesco Algarotti was, as usual, somewhat scared of public opinion.",
    "Francesco Algarotti was, as usual, somewhat scared of public opinion",
    "'As usual' and 'somewhat' are retained as Haskell's characterization.",
    ["cand-0048"],
)
add_statement(
    "st-chp10-p321-algarotti-produced-distorted-version-of-lodoli-opinions", "cand-0048", "cand-1412", "produced-distorted-version-of-lodoli-opinions",
    173, 173,
    "Haskell says Algarotti produced a rather distorted version of Lodoli's opinions.",
    "and he produced a rather distorted version of Lodoli’s opinions",
    "'Rather distorted' is Haskell's judgment; the account of Lodoli's response is recorded separately.",
    ["cand-0048", "cand-1412", "cand-1411"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-lodoli-was-not-pleased-by-algarotti-version", "cand-1411", "cand-0048", "version-of-lodoli-opinions-failed-to-please-him",
    173, 173,
    "Haskell says the distorted version failed to please Lodoli.",
    "which failed to please their author",
    "'Their author' refers to Lodoli, the author of the opinions as described here.",
    ["cand-1411", "cand-0048"], relation_candidate=True,
)
add_statement(
    "st-chp10-p321-lodoli-originally-welcomed-algarotti-interest-fragment", "cand-1411", "cand-0048", "originally-welcomed-algarotti-interest-and-friendly-intention",
    173, 173,
    "Haskell says Lodoli had originally welcomed Algarotti's interest; the description of the intention continues on p.322.",
    "though he had originally welcomed Algarotti’s interest and the intention had been",
    "'He' refers to Lodoli. The final word describing the intention is not inferred before p.322 is read.",
    ["cand-1411", "cand-0048"], relation_candidate=True,
    extra={"continuation_segment_id": NEXT_SEGMENT, "statement_continues": True},
)

previous_hits = [row for row in statements if row.get("statement_id") == PREVIOUS_STATEMENT]
if len(previous_hits) != 1:
    raise SystemExit(f"expected one p.320 continuing statement, found {len(previous_hits)}")
previous_statement = previous_hits[0]
previous_qualifiers = previous_statement.get("qualifiers", {})
if (previous_statement.get("segment_id") != PREVIOUS_SEGMENT
        or previous_qualifiers.get("statement_continues") is not True
        or previous_qualifiers.get("continuation_segment_id") != SEGMENT
        or previous_statement.get("original_quote", "").splitlines()[-1].split()[-1] != "but"):
    raise SystemExit("p.320 final sentence continuation state changed")
previous_statement_updated = json.loads(json.dumps(previous_statement))
previous_statement_updated["qualifiers"]["statement_continues"] = False
previous_statement_updated["qualifiers"]["continuation_completion_quote"] = "this is almost certainly because he was not taken wholly seriously even by those who most admired him."
previous_statement_updated["qualifiers"]["continuation_completed_by_segment_id"] = SEGMENT
previous_statement_updated["qualifiers"]["claim"] = (
    "Haskell describes Lodoli as uncouth and gruff and says his outspokenness would hardly have been tolerated in anyone else; "
    "he suggests this was almost certainly because Lodoli was not taken wholly seriously even by those who most admired him."
)
previous_statement_updated["qualifiers"]["qualification"] = (
    "The 'almost certainly' is retained; Haskell's explanation for the tolerance of Lodoli's outspokenness remains an inference."
)

statement_ids = {row["statement_id"] for row in statements}
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("p.321 statement ID already exists")
candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = [previous_statement_updated if row is previous_statement else row for row in statements] + new_statements

old_previous_note = coverage[PREVIOUS_SEGMENT].get("note", "")
continuation_needle = "L163's final 'but' continues at " + SEGMENT + "; coverage remains partial pending that continuation and the notes."
if old_previous_note.count(continuation_needle) != 1:
    raise SystemExit("p.320 coverage note does not contain the expected p.321 continuation")
coverage[PREVIOUS_SEGMENT]["note"] = old_previous_note.replace(
    continuation_needle,
    "L163's final 'but' is completed by p.321 L166; p.320 remains partial pending footnotes at canonical notes L308–310.",
)

coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L166-173",
    "note": (
        "Read printed p.321 against CHP-10.pdf physical p.54. L166 completes the p.320 sentence about Lodoli's outspokenness; "
        "L166–167 records Haskell's licensed-jester comparison and Lodoli's attributed argument about noble luxury and craftsmen's "
        "livelihood. L168 reports an account of functional architecture mediated through contemporaries, Lodoli's rejection of the "
        "late Baroque and emerging classicism, and his investigation of antiquity/Pantheon. L169 reports negligible contemporary "
        "architectural influence, an unnamed writer's criticism, the 'impudent impostor' characterization, and Lodoli's one recorded "
        "architectural intervention at a Minori Osservanti monastery. L170 records the governor's invitation to inspect Massari's "
        "modello and keeps the architect's hypothetical explanation distinct from Lodoli's criticism. L171–173 covers Haskell's claim "
        "about open-minded thinkers, Gaspare Gozzi's criticism and Algarotti's distorted account of Lodoli. Added "
        f"{len(new_candidates)} candidates, {len(new_mentions)} exact mentions, and {len(new_statements)} statements. Print corrections "
        "recorded without changing S0: linked.- -> linked.—; Nothing'shocked -> Nothing shocked; outside'S. -> outside S.; tnodello -> "
        "modello; logicalgrounds -> logical grounds; five in houses -> live in houses. Footnotes 1–3 await canonical notes L311–313. "
        "The final clause at L173 continues at " + NEXT_SEGMENT + "; coverage remains partial pending that continuation and the notes."
    ),
})

print(f"p.321 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements; close one p.320 sentence")
print(f"coverage: p.321 reviewed/partial; next source segment {NEXT_SEGMENT}; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
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
