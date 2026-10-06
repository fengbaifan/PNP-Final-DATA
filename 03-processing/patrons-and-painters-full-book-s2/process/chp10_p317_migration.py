"""Controlled S2 migration for printed p.317; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l119-131"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l108-117"
EXPECTED_MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENT_SHA = "a8e3ff5fca7f961532bea42166ba052a51643d887ed2b96b0ccfbc720ee160e0"
BACKUP_SUFFIX = ".bak-s2-chp10-p317-20261003"
NEXT_SEGMENT = "chp-10:10_CHP-10_sec_ii:l133-142"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.317 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[118:131]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.317 S2 source segment changed")
if segment_lines[0] != "[Page 317]" or segment_lines[2] != "THE ENLIGHTENMENT" or not segment_lines[-1].endswith("achieved before"):
    raise SystemExit("p.317 segment boundaries changed")

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
if table_state != (9671, 9684, 20310, 8984):
    raise SystemExit(f"table state changed; re-read current table counts before migration: {table_state}")

coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.317 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.316 segment to remain partial pending its notes")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.317 already has S2 mention or statement rows")

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


add_candidate("cand-9685", "Intellectual revolution beginning in England and France in the 1690s", "term", "Haskell's retrospective account of intellectual changes; 'was to destroy' is prospective wording, not a claim of instant change.", 123)
add_candidate("cand-9686", "Supremacy of a single secular or religious authority as a basis of judgment", "term", "The source says this authority was seriously questioned; it names no particular ruler, church, or institution.", 124)
add_candidate("cand-9687", "Reason as the ultimate criterion of judgment", "term", "Haskell describes a gradual shift in standards of judgment; do not treat it as an institution or a measured process.", 124)
add_candidate("cand-9688", "Toleration as an accepted principle in Enlightenment-era Europe", "term", "Retains Haskell's qualified account that toleration came to be accepted little by little and grudgingly.", 124)
add_candidate("cand-9689", "Diversity as an accepted principle in Enlightenment-era Europe", "term", "Retains Haskell's qualified account that diversity came to be accepted little by little and grudgingly.", 124)
add_candidate("cand-9690", "Trade replacing landholding as an index of wealth", "term", "Records the stated change in the indicator of wealth; the passage gives no measure or date for its completion.", 124)
add_candidate("cand-9691", "Changing patronage and the arts in eighteenth-century Europe", "term", "A broad change in patronage and the arts described by Haskell; its pace is qualified as first gradual and then faster.", 125)
add_candidate("cand-9692", "Royalty and the Church as incumbent art-patronage powers in England and France (unnamed collective)", "", "The collective is not resolved into named institutions; the source claims they no longer monopolised leading painters.", 125)
add_candidate("cand-9693", "New aristocratic and middle-class patrons in England and France (unnamed groups)", "", "The source names social categories, not identifiable patrons; it says these patrons rejected the Baroque cosmology.", 125)
add_candidate("cand-9694", "All-embracing cosmology of the Baroque", "term", "A conceptual framework Haskell says the new patrons rejected; retain as his characterization.", 125)
add_candidate("cand-9695", "Renewed interest in realism as an eighteenth-century artistic tendency", "term", "The passage characterizes this tendency as often tinged with satire or didactic elements; do not collapse it into a specific work's realism.", 126)
add_candidate("cand-9696", "Italian writers, artists, and intellectuals seeking new developments abroad (unnamed group)", "", "No members are named; the passage says more of this group were compelled to travel to London or Paris.", 130)
add_candidate("cand-9697", "Foreigners crossing the Alps into Italy as soldiers or tourists (unnamed group)", "", "The source supplies occupational descriptions but no individual identities or count beyond 'vast numbers'.", 129)
add_candidate("cand-9698", "Learned journals connected with Paris (unnamed periodicals)", "archive", "The passage names no journal titles; the same plural journals are later described as carrying controversial articles.", 130)
add_candidate("cand-9699", "Controversial articles on the state of Italian culture (unnamed publications)", "archive", "The articles are not individually titled or attributed; they are said to have appeared in the journals after a cultural stocktaking.", 130)
add_candidate("cand-9700", "State of Italian culture as a subject of eighteenth-century stocktaking", "term", "A collective subject of debate in the passage, not a named institution or a finding independently verified here.", 130)
add_candidate("cand-9701", "Seventeenth-century culture in the context of the Society of Arcadia", "term", "The source says the Society's creation symbolically broke with this culture, significantly only in literature.", 128)
add_candidate("cand-9702", "The Alps", "place", "The mountain range crossed by the unnamed foreigners; distinguish it from the existing candidate for the region north of the Alps.", 130)
add_candidate("cand-9703", "Mausoleum to Galileo at the Florentine church of S. Croce", "work", "The source describes an attempted prevention of its erection in 1737; this entry does not decide whether the project or a built monument is meant.", 130)
add_candidate("cand-9704", "Galileo's Dialogo (short title as cited by Haskell)", "archive", "The italicized short title is retained without expanding the title or resolving Haskell's publication-date claim.", 131)

candidate_ids.update(row["candidate_id"] for row in new_candidates)
new_mentions = []


def line_offset(line_no):
    return sum(len(line) + 1 for line in segment_lines[:line_no - 119])


def add_mention(line_no, surface, candidate_id, note="", occurrence=0):
    if candidate_id not in candidate_ids:
        raise SystemExit(f"mention references unknown candidate {candidate_id}: {surface!r}")
    expected_start = line_offset(line_no)
    if "\n" in surface:
        starts = []
        cursor = 0
        while True:
            at = segment_text.find(surface, cursor)
            if at < 0:
                break
            starts.append(at)
            cursor = at + 1
        starts = [at for at in starts if segment_text[:at].count("\n") + 119 == line_no]
    else:
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
    (121, "THE ENLIGHTENMENT", "cand-0974", "Chapter heading; index candidate specifically covers Enlightenment in Italy on pp.317–331."),
    (122, "ENICE", "cand-2719", "The print reads VENICE; its decorative initial V is displaced to the next OCR line prefix 'VThe'."),
    (122, "Europe", "cand-3462", "Named as the wider region contrasted with Venice."),
    (123, "England", "cand-8983", "Named as one setting for the intellectual changes described."),
    (123, "France", "cand-5317", "Named as one setting for the intellectual changes described."),
    (123, "intellectual revolution", "cand-9685", "Haskell's term for the beginning of the late-seventeenth-century changes."),
    (124, "Baroque civilisation", "cand-4500", "Haskell's social-cultural category; this is not an independent periodization claim."),
    (124, "any one authority, whether secular or religious", "cand-9686", "The source does not name an authority or identify a particular religious body."),
    (124, "Reason", "cand-9687", "Capitalization follows the source's abstract use of Reason as a criterion."),
    (124, "tolerance", "cand-9688", "Retains the source's gradual and qualified account."),
    (124, "diversity", "cand-9689", "Retains the source's gradual and qualified account."),
    (124, "Trade began to replace landholding as an index of wealth", "cand-9690", "The printed page has a sentence space after 'accepted.'; the OCR includes a leading hyphen before Trade."),
    (125, "patronage and the arts", "cand-9691", "The passage describes changes in their nature without naming a specific institution."),
    (125, "England", "cand-8983", "Second mention in the chapter opening."),
    (125, "France", "cand-5317", "Second mention in the chapter opening."),
    (125, "royalty and the Church", "cand-9692", "Unnamed incumbent patronage powers; not split into unsupported individual institutions."),
    (125, "new patrons, whether aristocratic or middle class", "cand-9693", "Social categories only; the passage supplies no named members."),
    (125, "all-embracing cosmology of the Baroque", "cand-9694", "The phrase is Haskell's characterization of what the new patrons rejected."),
    (126, "rococo", "cand-8836", "Use the existing broad Rococo-as-European-fashion candidate; this sentence does not restrict it to France."),
    (126, "Baroque", "cand-4500", "The source contrasts its formal language with the Rococo style."),
    (126, "realism", "cand-9695", "A renewed interest, not a claim that all works were realist."),
    (126, "neo-classicism", "cand-6439", "Reuses the existing candidate for Neoclassicism as an emerging artistic tendency."),
    (126, "painting", "cand-1805", "The sentence introduces painting's social significance; its fuller discussion is indexed on pp.328–329."),
    (126, "fifteenthand sixteenth-century humanists", "cand-4731", "The print reads 'fifteenth- and sixteenth-century'; OCR lost the hyphen and intervening space at a line break."),
    (127, "Italy", "cand-3461", "Named as the setting for the Italian response."),
    (127, "Rome", "cand-4490", "Named as the place of the Society's creation."),
    (127, "creation", "cand-6460", "The Society of Arcadia's 1690 formation; reuses the existing event candidate."),
    (127, "Society of\nArcadia", "cand-0114", "The proper name crosses the OCR line break; the print names the Society of Arcadia."),
    (128, "seventeenth-century culture", "cand-9701", "The source limits the symbolic break to the field of literature."),
    (129, "Europe", "cand-3462", "The phrase 'rest of Europe' continues from the previous OCR line."),
    (129, "foreigners", "cand-9697", "An unnamed group; the author gives no individual identities."),
    (130, "Alps", "cand-9702", "Named as the mountain range crossed by the visitors."),
    (130, "soldiers", "cand-9697", "One of the unnamed group's roles in the source."),
    (130, "tourists", "cand-9697", "One of the unnamed group's roles in the source."),
    (130, "learned journals", "cand-9698", "Unnamed periodicals said to be in touch with Paris."),
    (130, "Paris", "cand-4653", "First Paris mention: the journals' intellectual connection."),
    (130, "Italy", "cand-3461", "The author says Italy initially saw nothing comparable to the changes in England and France."),
    (130, "France", "cand-5317", "Third mention; the changes are said to have shaken France and England."),
    (130, "England", "cand-8983", "Third mention; the changes are said to have shaken France and England."),
    (130, "those Italians", "cand-9696", "Corefers to the following unnamed writers, artists, and intellectuals."),
    (130, "writers", "cand-9696", "One of the source's unnamed intellectual roles."),
    (130, "artists", "cand-9696", "One of the source's unnamed intellectual roles."),
    (130, "intellectuals", "cand-9696", "One of the source's unnamed intellectual roles."),
    (130, "new developments", "cand-9685", "The phrase refers to the preceding European intellectual changes."),
    (130, "London", "cand-1422", "One of two alternative destinations, not a claim that the group visited both cities."),
    (130, "Paris", "cand-4653", "Second Paris mention: one of two alternative travel destinations.", 1),
    (130, "Italian culture", "cand-9700", "The state of Italian culture is the subject of the later stocktaking."),
    (130, "the journals", "cand-9698", "Corefers to the learned journals mentioned earlier in the sentence."),
    (130, "controversial articles", "cand-9699", "Unnamed articles; the source gives no titles or authors."),
    (130, "enlightened’ ideas", "cand-0974", "The print uses quotation marks around 'enlightened'; the OCR has mismatched opening punctuation."),
    (130, "the Pope", "cand-0862", "The book's index names Lorenzo Corsini at p.317; the prose itself says only 'the Pope', so identity remains for S3."),
    (130, "mausoleum", "cand-9703", "A mausoleum to Galileo; the source does not resolve proposal versus completed monument."),
    (130, "Galileo", "cand-1105", "The indexed person is named explicitly as the mausoleum's subject."),
    (130, "Florentine", "cand-3397", "The source identifies Florence adjectivally; the building's precise identity is not expanded here."),
    (130, "S. Croce", "cand-0685", "Uses the index candidate for the church listed under Churches at p.317."),
    (130, "his", "cand-1107", "Corefers to Galileo; the index's p.317 subentry specifically identifies the Dialogo context."),
    (131, "Dialogo", "cand-9704", "Italicized short title in the print; do not expand it or resolve its publication history at S2."),
]

for item in MENTIONS:
    add_mention(*item)
new_mentions.sort(key=lambda row: int(row["start_char"]))
for index, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-s2-ch10-p317-{index:04d}"
for left, right in zip(new_mentions, new_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping p.317 mention spans: {left['surface_form']} and {right['surface_form']}")

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, relation_candidate=False, extra=None):
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored: {statement_id}")
    if any(cid not in candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 317,
        "pdf_physical_page": 50,
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
    "st-chp10-p317-venice-seemed-immobile-while-europe-changed", "cand-2719", "cand-3462", "seemed-immobile-while-europe-changed",
    122, 122,
    "Haskell opens by contrasting Venice's apparent immobility with change in Europe.",
    "ENICE had remained immobile—or so it seemed—but Europe had changed.",
    "This is explicitly qualified by 'or so it seemed'; the missing initial V is an OCR/drop-cap displacement confirmed against the print.",
    ["cand-2719", "cand-3462"],
)
add_statement(
    "st-chp10-p317-intellectual-revolution-in-england-and-france", "cand-9685", "cand-4500", "began-in-1690s-and-was-to-undermine-baroque-civilisation",
    123, 124,
    "Haskell says the last decade of the seventeenth century in England and France saw the beginnings of an intellectual revolution that was to undermine the foundations of Baroque civilisation.",
    "The last ten years of the seventeenth century in England and France had seen the beginnings of an intellectual revolution that was to destroy the foundations On which\nBaroque civilisation had rested.",
    "The phrase 'was to destroy' is prospective in Haskell's account; the print has lowercase 'on' across the line break. Footnote 1 at canonical notes L298 remains pending.",
    ["cand-9685", "cand-8983", "cand-5317", "cand-4500"], False,
    {"footnote_marker": 1, "pending_note_source_line": 298},
)
add_statement(
    "st-chp10-p317-supremacy-of-authority-questioned", "cand-9686", None, "supremacy-of-any-one-authority-seriously-questioned",
    124, 124,
    "Haskell says the absolute supremacy of any single secular or religious authority was seriously questioned.",
    "The absolute supremacy of any one authority, whether secular or religious, was seriously questioned.",
    "No particular ruler, church, or authority is named.",
    ["cand-9686"],
)
add_statement(
    "st-chp10-p317-reason-becomes-ultimate-criterion", "cand-9687", "cand-9686", "slowly-took-place-as-ultimate-criterion-of-judgement",
    124, 124,
    "Haskell says Reason slowly replaced authority as the ultimate criterion of judgement.",
    "Reason slowly took its place as the ultimate criterion of judgement.",
    "The pace is qualified as gradual; this records the author's historical interpretation.",
    ["cand-9687", "cand-9686"],
)
add_statement(
    "st-chp10-p317-tolerance-and-diversity-gradually-accepted", "cand-9688", "cand-9689", "came-to-be-accepted-gradually-and-grudgingly",
    124, 124,
    "Haskell says tolerance and diversity came to be accepted little by little and grudgingly.",
    "Little by little and however grudgingly, tolerance and diversity came to be accepted.",
    "The sentence gives neither a date nor a measure of acceptance.",
    ["cand-9688", "cand-9689"],
)
add_statement(
    "st-chp10-p317-trade-replaces-landholding-as-wealth-index", "cand-9690", None, "began-to-replace-landholding-as-an-index-of-wealth",
    124, 124,
    "Haskell says trade began to replace landholding as an index of wealth.",
    "Trade began to replace landholding as an index of wealth.",
    "The printed page has a sentence break before Trade; the OCR inserted a hyphen. The claim is a broad historical characterization, not a quantified transition.",
    ["cand-9690"],
)
add_statement(
    "st-chp10-p317-change-affected-patronage-and-arts", "cand-9685", "cand-9691", "profoundly-affected-nature-of-patronage-and-arts",
    125, 125,
    "Haskell says the changes first gradually and then increasingly rapidly affected the nature of patronage and the arts.",
    "These great changes at first gradually and then with ever-increasing speed profoundly affected the nature of patronage and the arts.",
    "The source's sequence and pace are retained; no specific patron or institution is identified here.",
    ["cand-9685", "cand-9691"],
)
add_statement(
    "st-chp10-p317-royalty-and-church-no-longer-monopolised-painters", "cand-9692", None, "no-longer-monopolised-leading-painters-in-england-and-france",
    125, 125,
    "Haskell says royalty and the Church no longer monopolised the leading painters in England and France.",
    "In both England and France royalty and the Church no longer monopolised the leading painters.",
    "The collective institutions and painters are unnamed; 'no longer monopolised' is the author's generalization, not an absolute claim that they ceased patronage.",
    ["cand-9692", "cand-8983", "cand-5317"],
)
add_statement(
    "st-chp10-p317-new-patrons-rejected-baroque-cosmology", "cand-9693", "cand-9694", "rejected-all-embracing-baroque-cosmology",
    125, 125,
    "Haskell says new aristocratic or middle-class patrons rejected the all-embracing cosmology of the Baroque.",
    "And the new patrons, whether aristocratic or middle class, rejected the all-embracing cosmology of the Baroque.",
    "The social categories are unnamed and not assigned to individual patrons; this is Haskell's account of their outlook.",
    ["cand-9693", "cand-9694"],
)
add_statement(
    "st-chp10-p317-eighteenth-century-artistic-tendencies", "cand-9685", "cand-8836", "rococo-realism-and-neoclassicism-encouraged-and-dropped",
    126, 126,
    "Haskell describes Rococo, renewed interest in realism, and Neoclassicism as styles encouraged and dropped as the eighteenth century progressed.",
    "As the eighteenth century progressed, various styles were encouraged and dropped: a light-hearted rococo, which took over much of the formal language of the Baroque without its moral seriousness; a renewed interest in realism, often tinged with satire or didactic elements; an austere return to neo-classicism.",
    "The examples are tendencies that overlapped; the sentence does not assign each style to one social class or identify a single origin.",
    ["cand-8836", "cand-4500", "cand-9695", "cand-6439"],
)
add_statement(
    "st-chp10-p317-styles-not-class-bound-and-overlapped", "cand-8836", None, "genesis-confused-and-styles-overlapped-across-social-classes",
    126, 126,
    "Haskell says the genesis of these styles is confused, none can be identified with one social class, and they frequently overlapped.",
    "The genesis of all these styles is confused; none of them can be identified with any one social class; all of them frequently overlapped.",
    "This is an explicit qualification against a one-style/one-class mapping.",
    ["cand-8836", "cand-9695", "cand-6439"],
)
add_statement(
    "st-chp10-p317-renewed-investigation-of-painting-in-national-life", "cand-1805", "cand-4731", "renewed-investigation-of-paintings-role-in-national-life",
    126, 126,
    "Haskell describes a renewed inquiry into painting's role in national life, more searching than inquiries begun by fifteenth- and sixteenth-century humanists.",
    "And combined with all these changes went a renewed investigation into the part that painting should be expected to play in the life of a nation—an investigation more searching than any that had token place since that inaugurated by the fifteenthand sixteenth-century humanists.",
    "The print reads 'fifteenth- and sixteenth-century'; OCR lost the hyphen and space at a line break. 'A nation' is generic, not a named political entity.",
    ["cand-1805", "cand-4731"],
)
add_statement(
    "st-chp10-p317-society-of-arcadia-created-in-rome", "cand-6460", "cand-0114", "created-in-rome-in-1690-as-symbolic-break-with-seventeenth-century-culture",
    127, 128,
    "Haskell says the Society of Arcadia's creation in Rome in 1690 marked a deliberate symbolic break with seventeenth-century culture, significantly only in literature.",
    "The creation in Rome of the Society of\nArcadia in 1690 marked a deliberate and symbolic break with seventeenth-century culture—though significantly only in the field of literature.",
    "The Society and its 1690 formation reuse existing candidates; the source names no founder and limits the break to literature.",
    ["cand-6460", "cand-0114", "cand-4490", "cand-9701"], True,
)
add_statement(
    "st-chp10-p317-foreign-visitors-strengthened-european-links", "cand-3461", "cand-3462", "links-with-europe-strengthened-by-visitors-crossing-alps",
    128, 130,
    "Haskell says links with the rest of Europe were strengthened by many foreigners crossing the Alps as soldiers or tourists at the beginning of the new century.",
    "And links with the rest of\nEurope were greatly strengthened by the vast numbers of foreigners who crossed the\nAlps either as soldiers or as tourists at the beginning of the new century.",
    "The visitors remain an unnamed group; 'vast numbers' is Haskell's wording and is not quantified.",
    ["cand-3461", "cand-3462", "cand-9697", "cand-9702"], True,
)
add_statement(
    "st-chp10-p317-italy-initially-lacked-comparable-change", "cand-3461", "cand-9685", "initially-saw-no-comparable-change-despite-european-links",
    130, 130,
    "Haskell says Italy initially saw nothing comparable to the changes that had shaken France and England, despite the journals' links with Paris.",
    "Yet despite this, and despite the blossoming of learned journals in touch with Paris, Italy at first saw nothing comparable to the great changes that had shaken France and England",
    "The claim is temporally qualified as 'at first'; the journals are unnamed and the sentence compares, rather than equates, national experiences.",
    ["cand-3461", "cand-9698", "cand-4653", "cand-5317", "cand-8983", "cand-9685"],
)
add_statement(
    "st-chp10-p317-italian-intellectuals-travelled-abroad", "cand-9696", None, "compelled-to-travel-to-london-or-paris-to-experience-new-developments",
    130, 130,
    "Haskell says more Italian writers, artists, and intellectuals who wished to experience new developments were compelled to travel to London or Paris.",
    "and more and more those Italians—writers, artists and intellectuals—who wished to experience the new developments were compelled to travel to London or Paris.",
    "The group is unnamed; London and Paris are alternative destinations, not a claim that each person visited both.",
    ["cand-9696", "cand-9685", "cand-1422", "cand-4653"], True,
)
add_statement(
    "st-chp10-p317-cultural-stocktaking-filled-journals-with-articles", "cand-9696", "cand-9699", "returning-intellectuals-stocktaking-filled-journals-with-controversial-articles",
    130, 130,
    "Haskell says a stocktaking of Italian culture by returning intellectuals filled the journals with controversial articles.",
    "On their return a great stocktaking of the state of Italian culture filled.the journals with controversial articles.",
    "The print reads 'filled the'; the OCR has a period instead of a space. The journals and articles are unnamed.",
    ["cand-9696", "cand-9700", "cand-9698", "cand-9699"],
)
add_statement(
    "st-chp10-p317-diffusion-of-enlightened-ideas-was-slow", "cand-0974", None, "prepared-ground-for-slow-and-hesitant-diffusion",
    130, 130,
    "Haskell says these developments prepared the ground for the initially slow and hesitant diffusion of enlightened ideas.",
    "AU this prepared the ground for the diffusion of'enlightened’ ideas which at first traveUed only slowly and hesitantly.",
    "The print reads 'All this', uses quotation marks around 'enlightened', and spells 'travelled'; the corrected reading is recorded here without changing S0.",
    ["cand-0974", "cand-9700"],
)
add_statement(
    "st-chp10-p317-pope-attempted-to-prevent-galileo-mausoleum", "cand-0862", "cand-9703", "tried-to-prevent-erection-in-1737",
    130, 130,
    "Haskell says that as late as 1737 the Pope tried to prevent erection of a mausoleum to Galileo at the Florentine church of S. Croce.",
    "As late as 1737 the Pope tried to prevent the erection of a mausoleum to Galileo in the Florentine church of S. Croce",
    "The prose says only 'the Pope'; the candidate mapping uses the book's p.317 index entry for Lorenzo Corsini and remains provisional for S3. The source's claim and the mausoleum's project/built status remain unverified here.",
    ["cand-0862", "cand-9703", "cand-1105", "cand-3397", "cand-0685"], True,
)
add_statement(
    "st-chp10-p317-dialogo-publication-date-claim", "cand-9704", None, "could-not-be-published-until-1744",
    130, 131,
    "Haskell says Galileo's Dialogo could not be published until 1744.",
    "his\nDialogo could not be published until 1744?",
    "'his' corefers to Galileo; the print's superscript footnote 2 is misread as '?' in OCR. Preserve this as Haskell's claim pending note L299 and later factual review.",
    ["cand-9704", "cand-1107"], False,
    {"footnote_marker": 2, "pending_note_source_line": 299},
)

statement_ids = {row["statement_id"] for row in statements}
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("p.317 statement ID already exists")

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements

coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L121-131",
    "note": (
        "Read printed p.317 against CHP-10.pdf physical p.50. The source file remains the registered 10_CHP-10_sec_ii; "
        "the print labels this section Chapter 12, THE ENLIGHTENMENT. L122–130 frames Haskell's account of the Enlightenment, "
        "changes in patronage, the Society of Arcadia, Italian intellectual exchange, and the slow diffusion of new ideas; "
        "L130–131 reports the Pope/Galileo mausoleum and Dialogo claims. Added 20 candidates, exact mentions, and statements; "
        "existing index/body candidates were reused for named places, people, styles, Arcadia, and painting's social significance. "
        "The index's Lorenzo Corsini mapping for 'the Pope' is recorded as provisional for S3. Printed corrections recorded "
        "without changing S0: Chapter spacing; the decorative V belongs to VENICE at L122, not L123 'VThe'; 'On' -> 'on'; "
        "accepted.-Trade -> accepted. Trade; token -> taken; fifteenthand -> fifteenth- and; filled.the -> filled the; "
        "AU -> All; OCR-mismatched quotation marks around enlightened; traveUed -> travelled; and 1744? -> 1744 with "
        "superscript note 2. L131's 'Although much had been achieved before' continues on p.318. Footnotes 1–2 await canonical "
        "notes L298–299. Coverage remains partial pending the p.318 continuation and those notes; type/identity decisions remain deferred."
    ),
})

print(f"p.317 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print(f"coverage: p.317 reviewed/partial; next source segment {NEXT_SEGMENT}; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
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
