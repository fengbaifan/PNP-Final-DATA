"""Controlled S2 migration for printed p.319; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l144-149"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l133-142"
NEXT_SEGMENT = "chp-10:10_CHP-10_sec_ii:l151-163"
PREVIOUS_RELATION_STATEMENT = "st-chp10-p318-conti-newton-relationship-initially-satisfactory"
EXPECTED_MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENT_SHA = "9fe4ff0e9fce9c9771d86d7d1263cae9647e95b5b350fe6371641dd3d2e61c7a"
BACKUP_SUFFIX = ".bak-s2-chp10-p319-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.319 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[143:149]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.319 S2 source segment changed")
if segment_lines[0] != "[Page 31]" or not segment_lines[-1].endswith("Moreover,"):
    raise SystemExit("p.319 segment boundaries changed")

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
if table_state != (9708, 9721, 20434, 9025):
    raise SystemExit(f"table state changed; re-read current table counts before migration: {table_state}")

coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.319 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.318 to remain partial pending its notes")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.319 already has S2 mention or statement rows")

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


add_candidate("cand-9722", "Royal Society", "institution", "Named as the institution Conti's proposed election concerned; do not infer that he was elected.", 145)
add_candidate("cand-9723", "John Dryden", "person", "Named among the English writers whose works Conti translated; identity is only the book-level candidate at S2.", 147)
add_candidate("cand-9724", "Julius Caesar (tragedy by Shakespeare)", "archive", "The play title is distinct from the Roman person and from Conti's unnamed tragedy imitating it.", 147)
add_candidate("cand-9725", "Newton's confidential notes on dating classical history", "archive", "An unnamed set of notes that Haskell says Newton showed to Conti; authorship/content remain limited to this passage.", 145)
add_candidate("cand-9726", "Unidentified public letter denouncing Antonio Conti", "archive", "No author, date, title, or publication details are supplied in this passage.", 146)
add_candidate("cand-9727", "Antonio Conti's 200 verses on Newton's philosophy", "archive", "An untitled poetic work or group described by Haskell; no manuscript or edition is identified here.", 145)
add_candidate("cand-9728", "Lost treatise on painting by Antonio Conti", "archive", "The passage identifies an untitled treatise and says it has been lost; do not infer its contents beyond later quoted material.", 149)
add_candidate("cand-9729", "camera ottica (apparatus named in Conti's account)", "", "A named optical viewing apparatus; the current taxonomy has no equipment type, so do not force a type at S2.", 149)
add_candidate("cand-9730", "Series of essays, philosophical treatises, and scientific pamphlets by Antonio Conti", "archive", "An unnamed group of writings; titles and publication status are not specified in this passage.", 149)
add_candidate("cand-9731", "Other English writers Antonio Conti met in London", "", "An unnamed collective; no members are supplied, so the candidate type remains unresolved.", 147)
add_candidate("cand-9732", "Antonio Conti's second visit to Paris (1718–1726)", "event", "The source gives an eight-year interval; retain that wording without inferring exact arrival/departure dates.", 147)

candidate_ids.update(row["candidate_id"] for row in new_candidates)
new_mentions = []


def line_offset(line_no):
    if line_no < 144:
        raise SystemExit(f"p.319 mention starts before its segment: L{line_no}")
    return sum(len(line) + 1 for line in segment_lines[:line_no - 144])


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
    (145, "Newton", "cand-1739", "Newton is the proposer of Conti's election.", 0),
    (145, "Conti", "cand-0830", "Uses the p.319 index candidate for Conti's proposed Royal Society election.", 0),
    (145, "Royal Society", "cand-9722", "The source reports a proposal for election, not confirmed membership.", 0),
    (145, "Conti", "cand-0826", "Named as the author of the verses.", 1),
    (145, "200 verses", "cand-9727", "The quantified poetic work is untitled in this account.", 0),
    (145, "Newton", "cand-1739", "Named as the subject of Conti's verses.", 1),
    (145, "second visit", "cand-9732", "This is the Paris visit later described as lasting from 1718 to 1726.", 0),
    (145, "Paris", "cand-4653", "The place of the visit during which the notes were revealed.", 0),
    (145, "Conti", "cand-0826", "Named as the person who revealed the notes.", 2),
    (145, "French", "cand-5317", "Haskell says the notes were revealed to the French; no recipients are named.", 0),
    (145, "confidential notes", "cand-9725", "The notes concern dating classical history.", 0),
    (145, "Newton", "cand-1739", "Named as the person who had shown Conti the notes.", 2),
    (146, "public letter", "cand-9726", "The letter is not identified by author or date.", 0),
    (146, "Conti", "cand-0826", "Named as the person denounced in the letter.", 0),
    (146, "his allegiance to", "cand-0828", "The p.319 Conti–Newton index candidate is used for the allegiance statement; Newton appears at the start of L147.", 0),
    (147, "Newton", "cand-1739", "Closes the previous line's allegiance phrase.", 0),
    (147, "English writers", "cand-9731", "The writers are unnamed; the source says Conti had met them in London.", 0),
    (147, "London", "cand-1422", "Named as the place where Conti met the English writers.", 0),
    (147, "Milton", "cand-1668", "The book's index candidate for John Milton is reused.", 0),
    (147, "Dryden", "cand-9723", "A named English poet without a separate p.319 index candidate.", 0),
    (147, "Sasper", "cand-2432", "The printed page reads 'Sasper'; it is not silently corrected in S0. The index candidate is Shakespeare.", 0),
    (147, "Julius Caesar", "cand-9724", "The phrase names Shakespeare's tragedy, not the Roman person.", 0),
    (147, "His second visit", "cand-9732", "The visit's eight-year span is given immediately afterward.", 0),
    (147, "Paris", "cand-4653", "Destination of Conti's second visit.", 0),
    (147, "Comte de Caylus", "cand-0615", "Named as one of Conti's Paris friendships.", 0),
    (148, "Conti", "cand-0826", "Named in the return-to-Venice statement.", 0),
    (148, "Venice", "cand-2719", "The city to which Conti returned.", 0),
    (149, "Venice", "cand-2719", "The source compares Conti's knowledge with that of Venice in his day.", 0),
    (149, "series of essays, philosophical treatises, scientific pamphlets", "cand-9730", "An unnamed body of writings; the source says these displayed his knowledge.", 0),
    (149, "Francesco Algarotti", "cand-0046", "Reuses the p.319 index candidate for Algarotti and Conti.", 0),
    (149, "treatise he wrote on painting", "cand-9728", "The unnamed painting treatise is described as lost.", 0),
    (149, "Newton", "cand-1739", "Named in the account of optical discoveries.", 0),
    (149, "Canaletto", "cand-0498", "Reuses the p.319 index candidate.", 0),
    (149, "camera ottica", "cand-9729", "Named apparatus; its type remains unresolved.", 0),
    (149, "Grand Canal", "cand-8178", "The views praised by Conti depict the Grand Canal.", 0),
    (149, "he made an interesting defence", "cand-0829", "The pronoun corefers to Conti; the p.319 index subentry concerns his defence of fantasy in painting.", 0),
    (149, "fantasy in painting", "cand-0992", "The source discusses artistic fantasy, not only the preceding literary debate.", 0),
    (149, "painter’s fantasy", "cand-0992", "The phrase begins a quotation attributed to Conti by Haskell.", 0),
]

for item in MENTIONS:
    add_mention(*item)
new_mentions.sort(key=lambda row: int(row["start_char"]))
for index, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-s2-ch10-p319-{index:04d}"
for left, right in zip(new_mentions, new_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping p.319 mention spans: {left['surface_form']} and {right['surface_form']}")

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, relation_candidate=False, extra=None):
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in p.319: {statement_id}")
    if any(cid not in candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 319,
        "pdf_physical_page": 52,
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
    "st-chp10-p319-newton-proposed-conti-election-to-royal-society", "cand-1739", "cand-9722", "proposed-election-of-conti",
    145, 145,
    "Haskell says Newton proposed Conti's election to the Royal Society.",
    "Newton proposed Conti’s election to the Royal Society",
    "A proposal is not evidence that Conti was elected; Conti is the person named in this book passage.",
    ["cand-1739", "cand-0830", "cand-9722"], True,
)
add_statement(
    "st-chp10-p319-conti-described-as-amateur-scientist", "cand-0826", None, "described-as-amateur-scientist",
    145, 145,
    "Haskell describes Conti as already an amateur scientist at the time of the Royal Society proposal.",
    "Ke was already an amateur scientist",
    "The pronoun refers to Conti; the print reads 'he' where the OCR has 'Ke'. This is Haskell's description, not an independently verified credential.",
    ["cand-0826", "cand-0830"],
)
add_statement(
    "st-chp10-p319-conti-wrote-verses-on-newton-philosophy", "cand-0826", "cand-9727", "wrote-200-verses-on-newtons-philosophy",
    145, 145,
    "Haskell says Conti wrote 200 verses on Newton's philosophy.",
    "Conti wrote 200 verses on Newton’s philosophy.",
    "The verses are not titled or otherwise bibliographically identified here.",
    ["cand-0826", "cand-9727", "cand-1739"], True,
)
add_statement(
    "st-chp10-p319-newton-showed-conti-confidential-notes", "cand-1739", "cand-9725", "showed-confidential-notes-to-conti",
    145, 145,
    "Haskell says Newton had shown Conti confidential notes on the dating of classical history.",
    "confidential notes that Newton had shown him on the dating of classical history",
    "The notes have no title, date, or repository in this passage; note 1 awaits canonical source line L304.",
    ["cand-1739", "cand-0826", "cand-9725"], True,
    {"footnote_marker": 1, "pending_note_source_line": 304},
)
add_statement(
    "st-chp10-p319-conti-revealed-notes-to-french-following-rupture", "cand-0826", "cand-9725", "revealed-newtons-notes-to-french-after-furious-break",
    145, 145,
    "Haskell says a furious break followed Conti's disclosure of Newton's confidential historical notes to the French.",
    "Later there was a furious break when on a second visit to Paris Conti revealed to the French some confidential notes that Newton had shown him on the dating of classical history.",
    "The source does not name the French recipients or explain the full circumstances; this is Haskell's account, not independent evidence of motive.",
    ["cand-0826", "cand-4653", "cand-5317", "cand-9725", "cand-1739"], True,
)
add_statement(
    "st-chp10-p319-conti-denounced-in-public-letter", "cand-0826", "cand-9726", "denounced-in-public-letter",
    146, 146,
    "Haskell says Conti was denounced in a public letter.",
    "Although he was denounced in a public letter",
    "The letter's author, date, and contents are not identified.",
    ["cand-0826", "cand-9726"], True,
)
add_statement(
    "st-chp10-p319-conti-never-abandoned-allegiance-to-newton", "cand-0826", "cand-1739", "never-abandoned-allegiance-to",
    146, 147,
    "Haskell says Conti never abandoned his allegiance to Newton.",
    "Conti never abandoned his allegiance to\nNewton",
    "The sentence crosses the OCR line break; this is Haskell's account of Conti's allegiance.",
    ["cand-0826", "cand-0828", "cand-1739"], True,
)
add_statement(
    "st-chp10-p319-conti-met-other-english-writers-in-london", "cand-0826", "cand-9731", "met-other-english-writers-in-london",
    147, 147,
    "Haskell says Conti had met many other English writers in London.",
    "the many other English writers he had met in London",
    "The writers are unnamed; no list or individual relationship is inferred.",
    ["cand-0826", "cand-9731", "cand-1422"], True,
)
add_statement(
    "st-chp10-p319-conti-translated-milton-dryden-and-other-poets", "cand-0826", None, "translated-english-literature-including-named-poets",
    147, 147,
    "Haskell says Conti translated Milton, Dryden, and other poets as an expression of his appreciation of English literature.",
    "He showed his appreciation of English literature by translating Milton, Dryden and other poets",
    "The other poets and translated works are not identified; the source gives no complete bibliography here.",
    ["cand-0826", "cand-1668", "cand-9723"],
)
add_statement(
    "st-chp10-p319-conti-wrote-on-sasper-and-imitated-julius-caesar", "cand-0826", "cand-9724", "wrote-on-shakespeare-and-imitated-julius-caesar",
    147, 147,
    "Haskell calls Conti the first Italian to write on 'Sasper' and says he imitated Shakespeare's Julius Caesar in his own tragedy.",
    "by being the first Italian to write on ‘Sasper’, whose Julius Caesar he imitated in a tragedy of his own.",
    "The printed page reads 'Sasper'; preserve that form rather than silently correcting it. Conti's tragedy is unnamed.",
    ["cand-0826", "cand-2432", "cand-9724"], True,
)
add_statement(
    "st-chp10-p319-conti-second-paris-visit-1718-1726", "cand-0826", "cand-9732", "second-paris-visit-spanned-1718-to-1726",
    147, 147,
    "Haskell says Conti's second visit to Paris lasted eight years between 1718 and 1726.",
    "His second visit to Paris lasted eight years between 1718 and 1726",
    "Retain the author's stated span; do not calculate exact arrival and departure dates.",
    ["cand-0826", "cand-9732", "cand-4653"], True,
)
add_statement(
    "st-chp10-p319-conti-friendship-with-caylus", "cand-0826", "cand-0615", "formed-friendship-with-comte-de-caylus",
    147, 147,
    "Haskell says one of Conti's many friendships was with the Comte de Caylus.",
    "among the many friendships he made was one with the Comte de Caylus.",
    "The account supplies no dates or further details of the friendship.",
    ["cand-0826", "cand-0615"], True,
)
add_statement(
    "st-chp10-p319-conti-returned-to-venice-and-died-in-1749", "cand-0826", "cand-2719", "returned-to-venice-in-1726-and-lived-until-1749",
    148, 149,
    "Haskell says Conti returned to Venice in 1726 and spent most of his time there until his death in 1749.",
    "In 1726 Conti returned to Venice, where he spent most of his time until his death in\n1749.",
    "The statement preserves 'most of his time' and does not infer an exact death date or uninterrupted residence.",
    ["cand-0826", "cand-2719"],
)
add_statement(
    "st-chp10-p319-conti-displayed-knowledge-in-writings", "cand-0826", "cand-9730", "displayed-english-french-cultural-knowledge-in-writings",
    149, 149,
    "Haskell says Conti possessed extensive knowledge of modern English and French culture, unique in Venice of his day, and displayed it in a series of writings.",
    "He had acquired a very extensive knowledge, unique in the Venice of his day, of modern English and-French culture and he proceeded to display it in a series of essays, philosophical treatises, scientific pamphlets and so on",
    "'Unique' and the breadth of the characterization are Haskell's assessment; the writings are not individually titled here.",
    ["cand-0826", "cand-2719", "cand-9730"],
)
add_statement(
    "st-chp10-p319-conti-writings-influenced-algarotti", "cand-9730", "cand-0046", "undoubtedly-influenced-francesco-algarotti",
    149, 149,
    "Haskell says Conti's writings undoubtedly influenced his friend Francesco Algarotti.",
    "which undoubtedly influenced his friend Francesco Algarotti.",
    "'Undoubtedly' and the influence claim remain attributed to Haskell; no particular writing or mechanism is identified.",
    ["cand-9730", "cand-0827", "cand-0046"], True,
)
add_statement(
    "st-chp10-p319-contis-papers-abbreviated-and-painter-connection-uncertain", "cand-0826", None, "posthumous-abbreviated-edition-limits-painter-connection-assessment",
    149, 149,
    "Haskell says Conti's papers were edited after his death in 1756 in abbreviated form, making the closeness of his connection with contemporary painters difficult to know.",
    "From time to time he wrote about the arts, but as his papers were only edited in 1756 after his death and in a very abbreviated form, it is difficult to know just how close was his connection with contemporary painters",
    "This states a limit on Haskell's knowledge; it does not establish the precise publication history of every paper.",
    ["cand-0826", "cand-9730"],
)
add_statement(
    "st-chp10-p319-conti-lost-treatise-on-painting", "cand-0826", "cand-9728", "treatise-on-painting-has-been-lost",
    149, 149,
    "Haskell says a treatise Conti wrote on painting has been lost.",
    "a treatise he wrote on painting has been lost.",
    "No title, date, or manuscript history is supplied in the body passage.",
    ["cand-0826", "cand-9728"], True,
)
add_statement(
    "st-chp10-p319-contis-vague-ideas-about-newton-optics-had-no-impact", "cand-0826", "cand-1739", "vague-ideas-about-optical-colour-effects-made-no-impact",
    149, 149,
    "Haskell says Conti had vague ideas about applying Newton's optical discoveries to colour, but these ideas made no impact.",
    "He certainly had some vague ideas about the effects that Newton’s optical discoveries ought to have on the use of colour, but these made no impact.",
    "'Vague' and 'made no impact' preserve the author's qualification and evaluation; no specific theory or audience is identified.",
    ["cand-0826", "cand-1739"], False,
    {"footnote_marker": 2, "pending_note_source_line": 305},
)
add_statement(
    "st-chp10-p319-conti-praised-canaletto-camera-ottica-views", "cand-0826", "cand-0498", "praised-canalettos-sagacity-in-camera-ottica-use",
    149, 149,
    "Haskell says Conti went out of his way to praise Canaletto's sagacity in using a camera ottica to paint Grand Canal views.",
    "He went out of his way to praise Canaletto for his sagacity in using the camera ottica to paint views of the Grand Canal.",
    "This records Haskell's account of Conti's praise; it does not identify a particular painting or camera apparatus.",
    ["cand-0826", "cand-0498", "cand-9729", "cand-8178"], True,
    {"footnote_marker": 3, "pending_note_source_line": 306},
)
add_statement(
    "st-chp10-p319-conti-defence-of-fantasy-qualified-by-unknown-date", "cand-0829", "cand-0992", "defended-fantasy-in-painting-with-polemical-intent-uncertain",
    149, 149,
    "Haskell says Conti's defence of fantasy in painting chimed with contemporary practice and suggests he did not disapprove of Venetian artists' licence, while warning that the paragraph's unknown date prevents estimating its polemical intention.",
    "And he made an interesting defence of fantasy in painting which chimed in well with contemporary practice and thus suggests that he was one of the few intellectuals of the day who did not disapprove of the licence; taken by Venetian artists—though as it is not known just when he wrote his brief paragraph on painting it is impossible to estimate its polemical intentions.",
    "The source explicitly limits the inference about Conti's attitude and says the date of the paragraph is unknown.",
    ["cand-0829", "cand-0826", "cand-0992"], False,
)
add_statement(
    "st-chp10-p319-conti-painters-fantasy-quoted-principles", "cand-0829", "cand-0992", "quoted-painterly-fantasy-as-knowledge-draughtsmanship-and-vigour",
    149, 149,
    "Haskell quotes Conti as saying painterly fantasy should combine breadth of knowledge, subtle and correct drawing, and lively, vigorous execution.",
    "‘The painter’s fantasy’, he wrote,4 ‘should be expressed in breadth of knowledge, in subtlety and correctness of draughtsmanship, in liveliness and vigour of execution. Moreover,",
    "This is a partial quotation continuing on p.320; note 4 awaits canonical source line L307. The wording is attributed to Conti by Haskell.",
    ["cand-0829", "cand-0992"], False,
    {"speaker": "Antonio Conti (quoted by Haskell)", "text_layer": "attributed quotation", "footnote_marker": 4, "pending_note_source_line": 307, "continuation_segment_id": NEXT_SEGMENT, "statement_continues": True},
)

previous_statement_hits = [row for row in statements if row.get("statement_id") == PREVIOUS_RELATION_STATEMENT]
if len(previous_statement_hits) != 1:
    raise SystemExit(f"expected one p.318 relationship statement, found {len(previous_statement_hits)}")
previous_statement = previous_statement_hits[0]
if previous_statement.get("segment_id") != PREVIOUS_SEGMENT or previous_statement.get("qualifiers", {}).get("statement_continues") is not True:
    raise SystemExit("p.318 Conti–Newton continuation state changed")
if previous_statement.get("qualifiers", {}).get("continuation_segment_id") != SEGMENT:
    raise SystemExit("p.318 relationship continuation points to an unexpected segment")
previous_statement_updated = json.loads(json.dumps(previous_statement))
previous_statement_updated["qualifiers"]["statement_continues"] = False
previous_statement_updated["qualifiers"]["continuation_completion_quote"] = "of them"

statement_ids = {row["statement_id"] for row in statements}
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("p.319 statement ID already exists")
candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = [previous_statement_updated if row is previous_statement else row for row in statements] + new_statements

old_note = coverage[PREVIOUS_SEGMENT].get("note", "")
marker = "The final Conti"
note_start = old_note.find(marker)
note_end = old_note.find(". Footnotes", note_start) if note_start >= 0 else -1
if note_start < 0 or note_end < 0 or SEGMENT not in old_note[note_start:note_end]:
    raise SystemExit("p.318 coverage note does not contain the expected pending continuation")
coverage[PREVIOUS_SEGMENT]["note"] = (
    old_note[:note_start]
    + "The final Conti–Newton relationship clause is completed by 'of them' on p.319 L145; p.318 remains partial pending footnotes at canonical notes L300–303."
    + old_note[note_end + 1:].replace(
        "Coverage remains partial pending the next-page continuation and those notes;",
        "Coverage remains partial pending those notes;",
    )
)
coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L145-149",
    "note": (
        "Read printed p.319 against CHP-10.pdf physical p.52; the OCR page label '[Page 31]' is corrected as a source-control note only. "
        "L145 completes p.318's Conti–Newton relationship sentence and reports Newton's proposed Royal Society election for Conti, "
        "Conti's verses, confidential notes, and their disclosure. L146–147 records the public-letter denunciation, continued allegiance, "
        "English writers, translations, the printed form 'Sasper', the Julius Caesar play, Conti's 1718–1726 Paris visit, and Caylus. "
        "L148–149 covers Conti's Venice return/death, writings and influence on Algarotti, the lost painting treatise, Newtonian optics, "
        "Canaletto/camera ottica, and Conti's qualified defence and quotation on painterly fantasy. Added 11 candidates, exact mentions, "
        "and 21 statements; the p.318 relationship statement continuation is now closed. Print comparison confirms 'he' where OCR has 'Ke'; "
        "the printed form 'Sasper' is retained. Footnotes 1–4 await canonical notes L304–307. The final quoted word 'Moreover,' continues at "
        + NEXT_SEGMENT + "; coverage remains partial pending that continuation and those notes. Formal identities and relations remain for later stages."
    ),
})

print(f"p.319 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements; close one p.318 continuation")
print(f"coverage: p.319 reviewed/partial; next source segment {NEXT_SEGMENT}; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
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
