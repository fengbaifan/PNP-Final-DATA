"""Controlled S2 migration for printed p.324; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l194-201"
NOTE_SEGMENT = "chp-10:10_CHP-10_sec_ii:l273-349"
NEXT_SEGMENT = "chp-10:10_CHP-10_sec_ii:l203-208"
EXPECTED_MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENT_SHA = "58fa86f2a310798b12cbde3a41cced09846465c9897299a94684f8544f040fa8"
BACKUP_SUFFIX = ".bak-s2-chp10-p324-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.324 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[193:201]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.324 S2 source segment changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
existing_mention_ids = {row["mention_id"] for row in mentions}
existing_statement_ids = {row["statement_id"] for row in statements}
table_state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if table_state != (9763, 9776, 20656, 9164):
    raise SystemExit(f"unexpected table pre-state: {table_state}")
if SEGMENT not in coverage_by_id:
    raise SystemExit("p.324 coverage row is missing")
coverage_row = coverage_by_id[SEGMENT]
if (coverage_row["disposition"], coverage_row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.324 coverage is not queued/pending")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.324 has existing mention or statement rows")

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


add_candidate(
    "cand-9777",
    "Unspecified laboring class honored in Gasparo Gozzi's fable",
    "term",
    "A class described in the fable as supporting all others through effort and the sweat of its brow. The passage does not name its members or give a formal social designation.",
    201,
)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
source_by_line = {number: source_lines[number - 1] for number in range(194, 202)}
new_mentions = []


def add_mention(line_no, surface, candidate_id, note="", occurrence=0):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"missing candidate for mention {surface!r}: {candidate_id}")
    line = source_by_line[line_no]
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
    offset = sum(len(source_lines[index]) + 1 for index in range(193, line_no - 1))
    start = offset + starts[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch on L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p324-{len(new_mentions) + 1:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


add_mention(195, "Lione", "cand-1842", "First name on this OCR line; Pascoli continues after a literal line-break marker.")
add_mention(196, "Pascoli", "cand-1842", "Index candidate for Lione Pascoli, p.324.")
add_mention(196, "hambocciafiti", "cand-0173", "OCR form is corrected to Bamboccianti from the page image.")
add_mention(196, "Guido Reni", "cand-2124", "Index candidate for Guido Reni.")
add_mention(197, "Cerquozzi", "cand-0625", "Index candidate for Michelangelo Cerquozzi.")
add_mention(197, "Gozzi", "cand-1220", "Gasparo Gozzi, whose comparison with Longhi and Tiepolo is described here.")
add_mention(197, "Tiepolo", "cand-2569", "Continuation of the comparison with Giambattista Tiepolo established on p.323; distinct from Gian Domenico's Via Crucis.")
add_mention(197, "Longhi", "cand-1429", "Index candidate for Pietro Longhi.")
add_mention(199, "Longhi", "cand-1429", "", 0)
add_mention(199, "Gozzi", "cand-1220", "", 0)
add_mention(199, "Longhi", "cand-1429", "", 1)
add_mention(199, "Longhi", "cand-1429", "", 2)
add_mention(199, "Tiepolo", "cand-2569", "Giambattista Tiepolo, as distinguished from the separately named Gian Domenico Tiepolo on p.323.")
add_mention(200, "Gasparo Gozzi", "cand-1220", "Index candidate for Gasparo Gozzi.")
add_mention(200, "Gozzi", "cand-1220", "Anaphoric reference to Gasparo Gozzi.", 1)
add_mention(201, "a class of people", "cand-9777", "Unspecified collective in the fable; no named members.")

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["candidate_id"]))
for left, right in zip(new_mentions, new_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")
if any(row["mention_id"] in existing_mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, speaker="Haskell",
                  text_layer="authorial claim", relation_candidate=False, extra=None):
    if statement_id in existing_statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"statement id already exists: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in p.324: {statement_id}")
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    if subject and subject not in all_candidate_ids:
        raise SystemExit(f"missing subject candidate in {statement_id}: {subject}")
    if object_id and object_id not in all_candidate_ids:
        raise SystemExit(f"missing object candidate in {statement_id}: {object_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 324,
        "pdf_physical_page": 57,
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


NOTE_REF = lambda start, end: [{"segment_id": NOTE_SEGMENT, "source_line_start": start, "source_line_end": end}]
add_statement(
    "st-chp10-p324-gozzi-principle-recording-grandeur-and-grace-in-nature", "cand-1220", "", "artistic-merit-as-recording-nature",
    195, 195,
    "Haskell continues his account of Gozzi's view that grandeur and grace in nature become artistic merit when recorded at their best by both artists.",
    "Grandeur and grace are each to be found in nature: artistic merit consists in recording them at their best as do both artists.",
    "The opening continues the prior page's comparison and 'both artists' refers to Pietro Longhi and Giambattista Tiepolo. It is Haskell's report of Gozzi's view, not an independent aesthetic verdict.",
    ["cand-1220", "cand-1429", "cand-2569"], speaker="Haskell reporting Gasparo Gozzi", text_layer="reported critical judgment",
    extra={"cross_reference_segments": [{"segment_id": "chp-10:10_CHP-10_sec_ii:l186-192", "source_line_start": 190, "source_line_end": 191}]},
)
add_statement(
    "st-chp10-p324-pascoli-made-similar-point-about-bamboccianti", "cand-1842", "cand-0173", "made-similar-point-about",
    196, 196,
    "Haskell says Lione Pascoli had made much the same point about the Bamboccianti roughly thirty years earlier.",
    "Pascoli had made much the same point some thirty years earlier when writing about the hambocciafiti1",
    "'Some thirty years earlier' is approximate. The OCR form is not silently normalized in the source span; the page-image correction is recorded below. Footnote 1 supplies Pascoli's citation.",
    ["cand-1842", "cand-0173"], speaker="Haskell reporting Lione Pascoli", text_layer="reported comparison",
    relation_candidate=True, extra={"cross_reference_segments": NOTE_REF(325, 325)},
)
add_statement(
    "st-chp10-p324-pascoli-principle-good-work-deserves-reputation", "cand-1842", "", "good-practice-deserves-success-and-reputation",
    196, 196,
    "The quotation attributed to Pascoli says that people deserve success and a good reputation when they practise their art well, regardless of art or manner.",
    "Whatever the art that man practises, and in whatever manner, as long as he does so well, he deserves success and a good reputation.",
    "This is a quotation cited by Haskell through Pascoli; it is not expanded into an external claim about a specific artist or artwork.",
    ["cand-1842"], speaker="Lione Pascoli as quoted by Haskell", text_layer="nested quotation",
    extra={"cross_reference_segments": NOTE_REF(325, 325)},
)
add_statement(
    "st-chp10-p324-social-context-gives-comparison-new-force", "cand-1220", "", "comparison-gains-force-in-hierarchical-society",
    196, 196,
    "Haskell says the observation gains new force when applied to actual artists in different branches of painting within a rigidly hierarchical society.",
    "when applied to actual artists working in different branches of painting in a rigidly hieratical society, the observation gains an entirely new force.",
    "The description of society and the comparison's force are Haskell's analysis; 'hieratical' is the printed wording and is retained.",
    ["cand-1220", "cand-2124", "cand-0625", "cand-2569", "cand-1429"],
)
add_statement(
    "st-chp10-p324-gozzi-ready-to-compare-tiepolo-and-longhi", "cand-1220", "cand-1429", "prepared-to-compare-with",
    197, 197,
    "Haskell contrasts the comparison Pascoli would not have made between Guido Reni and Cerquozzi with Gozzi's readiness to compare Tiepolo and Longhi.",
    "Gozzi was now prepared to compare Tiepolo and Longhi.",
    "The comparison is an art-critical juxtaposition, not evidence that either pair had a personal relationship. The Tiepolo referent follows the p.323 index distinction and is Giambattista.",
    ["cand-1220", "cand-2124", "cand-0625", "cand-2569", "cand-1429"],
    relation_candidate=True,
)
add_statement(
    "st-chp10-p324-gozzi-returned-to-question-months-later", "cand-1220", "", "returned-to-question-months-later",
    198, 198,
    "Haskell says Gozzi returned to the question a few months later with a more startling observation.",
    "A few months later he returned to the question with a much more startling observation.",
    "The pronoun refers to Gozzi in the immediately preceding comparison; no exact date is supplied in this sentence.",
    ["cand-1220"],
)
add_statement(
    "st-chp10-p324-gozzi-praised-longhi-realism", "cand-1220", "cand-1429", "praised-for-painting-observed-life",
    199, 199,
    "Haskell reports Gozzi's praise of Longhi for abandoning antique dress and imaginary characters in favour of what he saw with his own eyes.",
    "Longhi was admired, he claimed,2 ‘because he has left behind figures dressed in the antique manner and imaginary characters, and paints instead what he sees with his own eyes’. ",
    "This is Gozzi's cited view of Longhi, not a statement that Longhi never painted imagined subjects. Footnote 2 identifies the periodical source and remains pending.",
    ["cand-1220", "cand-1429"], speaker="Haskell reporting Gasparo Gozzi", text_layer="reported critical judgment",
    relation_candidate=True, extra={"cross_reference_segments": NOTE_REF(326, 326)},
)
add_statement(
    "st-chp10-p324-gozzi-insisted-longhi-realism-was-amiable", "cand-1220", "cand-1429", "insisted-on-amiable-nature-of-realism",
    199, 199,
    "Haskell says Gozzi later insisted on the amiable nature of Longhi's realism, somewhat weakening the force of the earlier praise.",
    "The force of this is somewhat weakened by his later insistence on the amiable nature of Longhi’s realism",
    "'His' refers to Gozzi. The weakening is Haskell's assessment of how this later qualification affects the earlier comparison.",
    ["cand-1220", "cand-1429"], speaker="Haskell reporting Gozzi", text_layer="reported qualification",
    relation_candidate=True,
)
add_statement(
    "st-chp10-p324-haskell-infers-longhi-superior-to-tiepolo", "cand-1429", "cand-2569", "considered-superior-to-by-gozzi",
    199, 199,
    "Haskell infers that Gozzi's statement implies he actually considered Longhi superior to Giambattista Tiepolo.",
    "it is”still a remarkable statement, for it implies that Gozzi actually considered Longhi superior to Tiepolo.3",
    "This is Haskell's inference from Gozzi's comparison, not a direct statement by Gozzi; the page image reads 'it is still'. Footnote 3 gives a later comparison as context, not proof of identity or direct influence.",
    ["cand-1220", "cand-1429", "cand-2569"], speaker="Haskell", text_layer="authorial inference",
    relation_candidate=True, extra={"ocr_corrections": [{"source_line": 199, "ocr": "it is”still", "print": "it is still"}], "cross_reference_segments": NOTE_REF(327, 327)},
)
add_statement(
    "st-chp10-p324-gozzi-fable-carries-same-point-with-social-implications", "cand-1220", "", "made-same-point-with-greater-social-implications-in-fable",
    200, 200,
    "Haskell says Gozzi made the same point in a fable with greater social implications, without directly naming an artist.",
    "Elsewhere Gasparo Gozzi made the same point with far greater social implications, though without directly naming any artist.",
    "The following allegorical story is treated as a fable, not as a literal account of Gozzi's house, collection, or transactions.",
    ["cand-1220"], speaker="Haskell", text_layer="authorial characterization",
    extra={"cross_reference_segments": NOTE_REF(328, 328)},
)
add_statement(
    "st-chp10-p324-gozzi-fable-old-philosopher-described-as-wise", "cand-1220", "", "fable-describes-apparently-mad-philosopher-as-incarnation-of-wisdom",
    200, 200,
    "In Gozzi's fable, the narrator visits an old philosopher regarded by the world as mad but described as the incarnation of true wisdom.",
    "He describes in a fable a visit he made to an old philosopher thought by the world to be mad but in fact the incarnation of true wisdom.",
    "This is the plot of a literary fable; the philosopher is not identified as a historical person.",
    ["cand-1220"], speaker="Haskell summarizing Gozzi's fable", text_layer="literary narrative",
    extra={"cross_reference_segments": NOTE_REF(328, 328)},
)
add_statement(
    "st-chp10-p324-gozzi-fable-natural-images-and-beautified-nature", "cand-1220", "", "fable-pictures-praise-natural-movement-and-beautified-nature",
    200, 201,
    "The fable's pictures are described as natural in movement and dress while more beautiful than living people; its imagined painter says he beautifies nature as it is.",
    "Each picture had beneath it a motto of some good intention. The foreshortened, figures were not overemphasised, but the movements were all natural, and the figures were all clothed like living men and women, though they were much more beautiful.",
    "The quoted pictures and painter belong to the fable. The page image removes the OCR comma after 'foreshortened'; the continuation 'my painter' is not identified with a historical artist in this segment.",
    ["cand-1220"], speaker="Gasparo Gozzi within a fable as quoted by Haskell", text_layer="nested literary quotation",
    extra={"ocr_corrections": [{"source_line": 200, "ocr": "foreshortened, figures", "print": "foreshortened figures"}], "cross_reference_segments": NOTE_REF(328, 328)},
)
add_statement(
    "st-chp10-p324-gozzi-fable-criticizes-indistinct-painting", "cand-1220", "", "fable-criticizes-unclear-light-and-figures",
    201, 201,
    "The old philosopher's speech in Gozzi's fable criticizes pictures in which people and forms seem simultaneously visible and absent.",
    "Lots of light, lots of darkness, men and women who are, and yet are not.",
    "The criticism is part of Gozzi's allegorical dialogue and is not assigned to a named painter or actual painting.",
    ["cand-1220"], speaker="Old philosopher in Gozzi's fable as quoted by Haskell", text_layer="nested literary quotation",
)
add_statement(
    "st-chp10-p324-gozzi-fable-country-life-pictures", "cand-1220", "", "fable-pictures-show-country-life-scenes",
    201, 201,
    "The fable's second room contains pictures of country scenes including ploughing, sowing, and grape gathering.",
    "In another room the walls are hung with pictures which show various scenes from country Use—ploughing, sowing, the gathering of grapes.",
    "These are pictures within the fable; OCR 'Use' is corrected to 'life' from the page image and no real works are identified.",
    ["cand-1220"], speaker="Haskell summarizing Gozzi's fable", text_layer="literary narrative",
    extra={"ocr_corrections": [{"source_line": 201, "ocr": "country Use", "print": "country life"}], "cross_reference_segments": NOTE_REF(328, 328)},
)
add_statement(
    "st-chp10-p324-gozzi-fable-honours-laboring-class", "cand-1220", "cand-9777", "fable-old-man-wishes-to-honour-laboring-class",
    201, 201,
    "In the fable, the old man says he gave away pictures of beautiful women and now wishes to honour a class whose labor supports all others.",
    "And the old man explains that whereas he used to own pictures of beautiful women, he has now given them away, and instead wishes to honour ‘a class of people, which through its efforts and the sweat of its brow is the main support of all others’. ",
    "This is an allegorical statement within Gozzi's fable, not evidence of an actual sale or donation by Gozzi. The group is left unnamed and is not assigned a specific class label beyond the quoted description.",
    ["cand-1220", "cand-9777"], speaker="Old man in Gozzi's fable as quoted by Haskell", text_layer="nested literary quotation",
    relation_candidate=True, extra={"cross_reference_segments": NOTE_REF(328, 328)},
)

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate id")
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")
all_ids = {row["candidate_id"] for row in candidate_rows}
if any(row["candidate_id"] not in all_ids for row in new_mentions):
    raise SystemExit("missing mention candidate foreign key")
if any(cid not in all_ids for row in new_statements for cid in row["qualifiers"]["mentioned_candidate_ids"]):
    raise SystemExit("missing statement candidate reference")
for row in new_statements:
    if row["subject_candidate_id"] and row["subject_candidate_id"] not in all_ids:
        raise SystemExit(f"missing statement subject: {row['statement_id']}")
    if row["object_candidate_id"] and row["object_candidate_id"] not in all_ids:
        raise SystemExit(f"missing statement object: {row['statement_id']}")

coverage_row.update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L194-201",
    "note": "Printed p.324 body reviewed against CHP-10.pdf physical page 57. Footnotes 1-4 at canonical notes L325-328 remain pending. The final sentence about a jibe and exaggerated foreshortenings continues into p.325 segment L203-208, so coverage remains partial.",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
statement_rows.sort(key=lambda row: row["statement_id"])
print(f"p.324 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage: reviewed/partial; footnotes 1-4 and a cross-page sentence remain pending")
print(f"totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
