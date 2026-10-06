"""Controlled S2 migration for printed p.318; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l133-142"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l119-131"
NEXT_SEGMENT = "chp-10:10_CHP-10_sec_ii:l144-149"
EXPECTED_MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENT_SHA = "57b6e165a2c8f95415fc2a8380d33ed655868ea9708af26e222398d11764fbb6"
BACKUP_SUFFIX = ".bak-s2-chp10-p318-20261003"
PREVIOUS_CONTINUATION_STATEMENT = "st-chp10-p318-peace-aix-as-starting-point-for-new-spirit-in-italy"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.318 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[132:142]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.318 S2 source segment changed")
if segment_lines[0] != "[Page 318]" or not segment_lines[-1].endswith("satisfactory to both"):
    raise SystemExit("p.318 segment boundaries changed")

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
if table_state != (9691, 9704, 20367, 9004):
    raise SystemExit(f"table state changed; re-read current table counts before migration: {table_state}")

coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.318 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.317 segment to remain partial pending notes and sentence closure")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.318 already has S2 mention or statement rows")

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


add_candidate("cand-9705", "Della pubblica felicità, oggetto de' buoni principi (L. A. Muratori)", "archive", "The passage cites the work by a shortened title; the scanned print was used to distinguish the title from OCR errors.", 136)
add_candidate("cand-9706", "Della Moneta (treatise by Abate Galiani)", "archive", "A named treatise said to have appeared in 1750; no edition or place of publication is supplied here.", 136)
add_candidate("cand-9707", "Dei delitti e delle pene (treatise by Cesare Beccaria)", "archive", "The named work is described as epoch-making and welcomed in Paris; this records Haskell's characterization.", 136)
add_candidate("cand-9708", "Censorship as a filter on Enlightenment ideas in Venice", "term", "Haskell says ideas might pass through censorship without much difficulty; this does not identify a particular censor or policy.", 138)
add_candidate("cand-9709", "Venetian political interest in maintaining the status quo", "term", "Haskell presents this interest as too powerful for the Republic to originate Enlightenment doctrines; retain the author's interpretation.", 139)
add_candidate("cand-9710", "Abolition of aristocratic rule as a premise of Enlightenment doctrines", "term", "Haskell says nearly all the doctrines in this context presupposed this change; do not generalize to every Enlightenment idea.", 139)
add_candidate("cand-9711", "Unnamed Venetian described as Beccaria's most vigorous opponent", "person", "The source does not name this person; do not identify the opponent from outside context or from later sections.", 139)
add_candidate("cand-9712", "Other unnamed unorthodox thinkers expelled from Venetian territory", "", "The group follows the named Giannone, Pilati, and Baretti; no additional members are supplied.", 140)
add_candidate("cand-9713", "Unnamed intellectual friends of Caterina Dolfin Tron", "", "An unnamed group whom Haskell says might discuss ideas with her; no individuals are listed.", 139)
add_candidate("cand-9714", "Unidentified library of Consul Joseph Smith in Venice", "place", "Haskell says ideas might have been discussed there; this is a provisional spatial reading, not a located or catalogued library.", 139)
add_candidate("cand-9715", "Italian literary and philosophical circles debating fantasy and reason", "", "The text names no members or institutions; the group is described by its discussion topic and period.", 141)
add_candidate("cand-9716", "Unnamed French critics who attacked Marino and Tasso's style", "", "No critics are identified; the source describes their criticism of style, not a formal organization.", 141)
add_candidate("cand-9717", "Unnamed followers of Giambattista Marino", "", "The source names no followers individually; they are included in the style criticized by French critics.", 141)
add_candidate("cand-9718", "Visual arts as an extension of the fantasy-and-reason debate", "term", "Haskell says an unnamed Venetian extended this discussion into visual arts; the scope is limited to this passage.", 141)
add_candidate("cand-9719", "Other writers influenced by Antonio Conti's discussion", "", "Haskell says Conti influenced other writers; no members or specific works are named here.", 141)
add_candidate("cand-9720", "Other leading figures whom Antonio Conti contacted in Paris (unnamed group)", "", "Malebranche and Fontenelle are named separately; the other contacts are not identified.", 142)
add_candidate("cand-9721", "Italian writers becoming aware of the distance from wider European thought (unnamed group)", "", "A broad collective in Haskell's account; keep distinct for now from the more specific travellers discussed on pp.317–318.", 135)

candidate_ids.update(row["candidate_id"] for row in new_candidates)
new_mentions = []


def line_offset(line_no):
    if line_no < 133:
        raise SystemExit(f"p.318 mention starts before its segment: L{line_no}")
    return sum(len(line) + 1 for line in segment_lines[:line_no - 133])


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
        starts = [at for at in starts if segment_text[:at].count("\n") + 133 == line_no]
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
    (134, "peace of Aix-la-Chapelle", "cand-0019", "Uses the p.318 index candidate for the named 1748 peace."),
    (134, "new spirit", "cand-0974", "The phrase refers to the new spirit in Italy framed as Enlightenment in the chapter."),
    (134, "Italy", "cand-3461", "Named as the setting of the new intellectual spirit."),
    (134, "Voltaire", "cand-2791", "The passage reports Voltaire's 1766 observation indirectly; it is not a direct quotation here."),
    (135, "Alps", "cand-9702", "Voltaire's attention is described as turning south across the Alps."),
    (135, "intellectual revival", "cand-0974", "The revival is the topic of Voltaire's reported comment."),
    (135, "Italy", "cand-3461", "Named in the claim about writers across Italy."),
    (135, "Europe", "cand-3462", "The reference is to the rest of Europe, not to a specific state."),
    (135, "writers", "cand-9721", "An unnamed group whose awareness and response are generalized by Haskell."),
    (135, "Muratori", "cand-1718", "The page-specific index candidate has the title as its subentry."),
    (136, "Della puhblica felicita, oggetto de’buoni principi", "cand-9705", "Canonical OCR title; the scanned print reads 'Della pubblica felicità, oggetto de’ buoni principi'."),
    (136, "Abate Galiani", "cand-1103", "Uses the page-specific index candidate with the Della Moneta subentry."),
    (136, "Della Moneta", "cand-9706", "A named treatise, kept distinct from its author's person candidate."),
    (136, "Antonio Genovesi", "cand-1133", "Named in the professorship claim."),
    (136, "Naples", "cand-3534", "Reuses the existing place candidate; the chair is located in Naples."),
    (136, "political economy", "cand-8404", "Reuses the existing term candidate for political economy."),
    (136, "Europe", "cand-3462", "The source calls Genovesi the first professor of political economy in Europe."),
    (136, "Beccaria", "cand-0266", "The page-specific index subentry is Dei delitti e delle pene; person identity remains S3 work."),
    (136, "Dei delitti e delle pene", "cand-9707", "A named treatise by Beccaria."),
    (136, "Paris", "cand-4653", "Haskell says Beccaria was welcomed there; no institution or event is named."),
    (136, "Galileo", "cand-1105", "The source refers to the earlier silencing of Galileo without specifying the mechanism here."),
    (137, "Italy", "cand-3461", "Named as being in the vanguard of contemporary thought."),
    (138, "Venice", "cand-2723", "The index candidate's p.318 subentry is censorship in Venice."),
    (138, "censorship", "cand-9708", "An institutional constraint discussed as a possible filter, not identified with a named censor."),
    (138, "Consul\nSmith’s", "cand-2440", "Smith's name is split by the OCR line break; p.318 index identifies Joseph Smith."),
    (139, "library", "cand-9714", "The named Consul Smith's library is treated provisionally as a place; the text says discussion there only perhaps occurred."),
    (139, "Caterina Dolfin", "cand-0925", "The index has a Dolfin entry; the next token supplies her married surname."),
    (139, "Tron", "cand-2655", "The index also has a Tron entry for Caterina Dolfin; S3 will reconcile the person candidates."),
    (139, "intellectual friends", "cand-9713", "The friends are unnamed."),
    (139, "Venetian interest in maintaining the status quo", "cand-9709", "Records Haskell's political interpretation without treating it as a measured public consensus."),
    (139, "the Republic", "cand-8838", "Corefers to the Republic of Venice as a political actor, not the city as a place."),
    (139, "Enlightenment", "cand-0976", "The p.318 index candidate is the Enlightenment in Italy, opposition in Venice."),
    (139, "a Venetian", "cand-9711", "An unnamed individual whom Haskell calls Beccaria's most vigorous opponent."),
    (139, "Beccaria", "cand-0265", "The source names Beccaria in the opposition claim; keep this distinct from the work-specific index candidate used at L136."),
    (139, "abolition of rule by aristocracy", "cand-9710", "Haskell says nearly all the doctrines in this context presupposed this change."),
    (139, "Pietro Giannone", "cand-1164", "Named among thinkers expelled from Venetian territory."),
    (139, "Carlo Antonio Pilati", "cand-1930", "Named among thinkers expelled from Venetian territory."),
    (140, "Baretti", "cand-0245", "The given name Giuseppe ends the previous OCR line; this surname completes the name across the line break."),
    (140, "other unorthodox thinkers", "cand-9712", "The additional members are not named."),
    (140, "her territory", "cand-8838", "Corefers to the Republic of Venice; do not map this to the city or assert individual expulsion evidence beyond the source."),
    (140, "foreign influences", "cand-8127", "Reuses the existing term candidate for foreign influences on Venetian ideas."),
    (141, "Italian literary and philosophical circles", "cand-9715", "The circles and their members are unnamed."),
    (141, "fantasy", "cand-0992", "The index candidate uses the paired topic Fantasy and reason for the discussion of creation."),
    (141, "reason", "cand-2110", "A second index seed reverses the paired topic as Reason and fantasy; retain both candidates for S3."),
    (141, "formation", "cand-6460", "Reuses the existing event candidate for the Society of Arcadia's formation."),
    (141, "Society of Arcadia", "cand-0114", "The named institution whose call to reason is described."),
    (141, "French critics", "cand-9716", "The critics are unnamed; their target is the style of Marino and Tasso."),
    (141, "Marino", "cand-1548", "Giambattista Marino, named in the source and index."),
    (141, "his followers", "cand-9717", "Corefers to unnamed followers of Marino."),
    (141, "Tasso", "cand-2544", "Torquato Tasso, named in the source and index."),
    (141, "a Venetian", "cand-0826", "The next sentence identifies the contributing Venetian as Antonio Conti; this is a local textual coreference, not external identity alignment."),
    (141, "visual arts", "cand-9718", "The field into which the debate was sometimes extended."),
    (141, "other writers", "cand-9719", "The writers influenced by Conti are unnamed."),
    (142, "Antonio Conti", "cand-0826", "Uses the p.318 index candidate for the person named in the following sentence."),
    (142, "Italian intellectuals", "cand-9696", "The growing travelling intellectual group continues the p.317 discussion; membership remains unnamed except for Conti."),
    (142, "a visit to", "cand-0975", "Anchors the p.318 index subentry concerning Italian intellectuals' contacts with England and France."),
    (142, "England", "cand-8983", "One of the destinations said to be essential to avoid provincialism."),
    (142, "France", "cand-5317", "One of the destinations said to be essential to avoid provincialism."),
    (142, "Venice", "cand-2719", "Named as the place whose provincialism Conti sought to avoid."),
    (142, "Paris", "cand-4653", "Conti's stated 1713 destination."),
    (142, "Malebranche", "cand-1499", "Named among Conti's contacts in Paris."),
    (142, "Fontenelle", "cand-1050", "Named among Conti's contacts in Paris."),
    (142, "other leading figures", "cand-9720", "The other Paris contacts are not identified."),
    (142, "Two years later he", "cand-0828", "The p.318 index has a Conti-and-Newton entry; the phrase refers to Conti and preserves the relative interval without calculating a year."),
    (142, "the Channel", "cand-6810", "Reuses the existing place candidate for Haskell's cross-Channel reference."),
    (142, "SirTsaac Newton", "cand-1739", "The scanned print reads 'Sir Isaac Newton'; OCR merged the initial I and T."),
    (142, "the relationship", "cand-0828", "The initial Conti–Newton relationship; the sentence continues on p.319."),
]

for item in MENTIONS:
    add_mention(*item)
new_mentions.sort(key=lambda row: int(row["start_char"]))
for index, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-s2-ch10-p318-{index:04d}"
for left, right in zip(new_mentions, new_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping p.318 mention spans: {left['surface_form']} and {right['surface_form']}")

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, relation_candidate=False, extra=None):
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in p.318: {statement_id}")
    if any(cid not in candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 318,
        "pdf_physical_page": 51,
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


def add_cross_page_statement(statement_id, subject, object_id, predicate, claim,
                             previous_quote, current_quote, qualification, mentioned):
    previous_source = source_lines[130]
    current_source = source_lines[133]
    if previous_quote not in previous_source or current_quote not in current_source:
        raise SystemExit(f"cross-page quote fragments are not anchored: {statement_id}")
    if any(cid not in candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 134,
            "source_line_end": 134,
            "printed_page": 318,
            "pdf_physical_page": 51,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "authorial claim",
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": False,
            "continuation_from_segment_id": PREVIOUS_SEGMENT,
            "continuation_prefix": previous_quote,
        },
        "original_quote": current_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


add_cross_page_statement(
    PREVIOUS_CONTINUATION_STATEMENT, "cand-0019", "cand-0974", "usually-taken-as-starting-point-for-new-spirit-in-italy",
    "Haskell acknowledges earlier achievements but says the 1748 Peace of Aix-la-Chapelle is usually taken as the starting point for a new spirit in Italy.",
    "Although much had been achieved before",
    "then, the peace of Aix-la-Chapelle in 1748 is usually taken as the starting-point for a new spirit in Italy.",
    "The sentence crosses the page boundary p.317–318; 'usually taken' attributes a conventional periodization rather than an uncontested date for the first appearance of Enlightenment ideas.",
    ["cand-0019", "cand-0974", "cand-3461"],
)
add_statement(
    "st-chp10-p318-voltaire-commented-on-intellectual-revival", "cand-2791", "cand-0974", "in-1766-reported-revival-had-been-under-way-about-twenty-years",
    134, 135,
    "Haskell reports that in 1766 Voltaire commented on an Italian intellectual revival and suggested it had been under way for about twenty years.",
    "When in 1766 Voltaire turned his attention southwards across the\nAlps and commented on the great intellectual revival that had taken place he suggested that it had been going on for about twenty years.",
    "This is Haskell's indirect report of Voltaire, not a direct quotation; 'about twenty years' is approximate. Footnote 1 awaits canonical note L300.",
    ["cand-2791", "cand-9702", "cand-0974"], False,
    {"footnote_marker": 1, "pending_note_source_line": 300},
)
add_statement(
    "st-chp10-p318-italian-writers-narrowed-cultural-distance", "cand-9721", "cand-3462", "became-aware-of-distance-and-began-to-narrow-it",
    135, 135,
    "Haskell says changes were striking and that writers across Italy recognized the distance from the rest of Europe and began to narrow it.",
    "The changes had been very striking indeed. All over Italy writers had become aware of the distance that separated them from the rest of Europe and had begun to narrow it.",
    "This is Haskell's account of writers' awareness and response, not a quantified measure of cultural convergence.",
    ["cand-9721", "cand-3461", "cand-3462"],
)
add_statement(
    "st-chp10-p318-muratori-published-della-pubblica-felicita", "cand-1718", "cand-9705", "published-in-1749",
    135, 136,
    "Haskell says Muratori published Della pubblica felicità, oggetto de' buoni principi in 1749 and comments on the advanced ideas signalled by its title.",
    "In 1749 Muratori published his\nDella puhblica felicita, oggetto de’buoni principi whose title alone proclaimed the advanced ideas inherent in the thesis;",
    "The scanned print reads 'pubblica felicità' and separates 'de’ buoni'; S0 OCR is unchanged. This records Haskell's comment on the title, not independent analysis of the book.",
    ["cand-1718", "cand-9705"], True,
)
add_statement(
    "st-chp10-p318-galiani-della-moneta-appeared-in-1750", "cand-1103", "cand-9706", "treatise-appeared-in-1750",
    136, 136,
    "Haskell says Abate Galiani's treatise Della Moneta appeared in 1750.",
    "in 1750 appeared the Abate Galiani’s treatise Della Moneta;",
    "No edition, publisher, or place of publication is specified in this passage.",
    ["cand-1103", "cand-9706"], True,
)
add_statement(
    "st-chp10-p318-genovesi-first-professor-of-political-economy", "cand-1133", "cand-8404", "took-chair-in-naples-in-1754-as-first-professor-in-europe",
    136, 136,
    "Haskell says Antonio Genovesi took up a chair in Naples in 1754 as Europe's first professor of political economy.",
    "in 1754 Antonio Genovesi took up his chair in Naples as the first professor of political economy in Europe;",
    "This is Haskell's priority claim; the passage does not name the university or the chair's official title.",
    ["cand-1133", "cand-3534", "cand-8404", "cand-3462"], True,
)
add_statement(
    "st-chp10-p318-beccaria-published-dei-delitti-and-welcomed-in-paris", "cand-0266", "cand-9707", "published-in-1764-and-welcomed-in-paris",
    136, 136,
    "Haskell says Beccaria published Dei delitti e delle pene in 1764 and was rapturously welcomed in Paris.",
    "in 1764 Beccaria published his epoch-making Dei delitti e delle pene and was rapturously welcomed in Paris.",
    "'Epoch-making' and 'rapturously welcomed' are Haskell's evaluations; the index's work subentry is attached to the Beccaria person candidate pending S3.",
    ["cand-0266", "cand-9707", "cand-4653"], True,
)
add_statement(
    "st-chp10-p318-italy-in-vanguard-of-contemporary-thought", "cand-3461", None, "entered-vanguard-of-contemporary-thought",
    136, 137,
    "Haskell says that for the first time since Galileo's silencing, Italy was in the vanguard of contemporary thought.",
    "For the first time since the silencing of Galileo\nItaly was in the vanguard of contemporary thought.",
    "'Silencing' is the author's wording; this passage does not specify the proceeding or equate it with a particular event record.",
    ["cand-3461", "cand-1105"],
)
add_statement(
    "st-chp10-p318-venice-played-little-direct-part", "cand-2723", None, "played-little-direct-part-in-these-changes",
    138, 138,
    "Haskell says Venice played little direct part in the changes just described.",
    "In these changes Venice had played little direct part.",
    "The claim is explicitly limited to a little direct part; it does not say that ideas were absent from Venice.",
    ["cand-2723", "cand-0974"],
)
add_statement(
    "st-chp10-p318-venetian-status-quo-limited-doctrine-origin", "cand-9709", "cand-8838", "too-powerful-to-originate-enlightenment-doctrines-despite-possible-filtering-and-discussion",
    138, 139,
    "Haskell says ideas might pass through censorship and be discussed in Joseph Smith's library or by Caterina Dolfin Tron and her friends, but Venetian interest in the status quo prevented the Republic from originating Enlightenment doctrines.",
    "Though the ideas might filter through the censorship without too much difficulty and be discussed perhaps in Consul\nSmith’s library or by Caterina Dolfin Tron and her intellectual friends, Venetian interest in maintaining the status quo was too powerful for the Republic to become the originator of any of the doctrines of the ‘Enlightenment’",
    "Retain 'might' and 'perhaps'; the library discussions are possibilities, not confirmed events. 'The Republic' is the Venetian political entity. The source's evaluation is not a measured account of all Venetian opinion.",
    ["cand-9708", "cand-0976", "cand-2440", "cand-9714", "cand-0925", "cand-2655", "cand-9713", "cand-9709", "cand-8838"],
    True,
)
add_statement(
    "st-chp10-p318-enlightenment-doctrines-presupposed-end-of-aristocratic-rule", "cand-0976", "cand-9710", "nearly-all-presupposed-abolition-of-aristocratic-rule",
    139, 139,
    "Haskell says nearly all the doctrines under discussion presupposed the abolition of rule by aristocracy.",
    "nearly all of which presupposed the abolition of rule by aristocracy.",
    "'Nearly all' is retained; the pronoun refers to the preceding Enlightenment doctrines, not to Beccaria alone.",
    ["cand-0976", "cand-9710"],
)
add_statement(
    "st-chp10-p318-unnamed-venetian-opposed-beccaria", "cand-9711", "cand-0265", "described-as-most-vigorous-opponent-of-beccaria",
    139, 139,
    "Haskell says an unnamed Venetian proved to be Beccaria's most vigorous opponent.",
    "it was indeed a Venetian who proved to be the most vigorous opponent of Beccaria",
    "The person's name is not given in this passage; no identity is inferred.",
    ["cand-9711", "cand-0265"], True,
)
add_statement(
    "st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled", "cand-8838", None, "rapidly-expelled-named-and-other-unorthodox-thinkers-from-venetian-territory",
    139, 140,
    "Haskell says Pietro Giannone, Carlo Antonio Pilati, Giuseppe Baretti, and other unorthodox thinkers were rapidly expelled from Venetian territory.",
    "Pietro Giannone, Carlo Antonio Pilati, Giuseppe\nBaretti and other unorthodox thinkers were rapidly expelled from her territory.",
    "'Her territory' refers to the Republic of Venice. The source provides no individual dates or separate expulsion details here. Footnote 2 awaits canonical note L301.",
    ["cand-1164", "cand-1930", "cand-0245", "cand-9712", "cand-8838"], True,
    {"footnote_marker": 2, "pending_note_source_line": 301},
)
add_statement(
    "st-chp10-p318-foreign-influences-and-spread-of-ideas", "cand-8127", "cand-9691", "gradual-spread-of-ideas-in-circles-most-open-to-foreign-influences-with-effects-on-art",
    140, 140,
    "Haskell says ideas spread gradually in circles most in touch with foreign influences and would have important effects on art.",
    "And yet, especially in those circles which were most in touch with foreign influences, we can trace the gradual spread of ideas which, among other things, were to have important effects on art.",
    "The circles are unnamed and the effects on art are prospective in the author's account.",
    ["cand-8127", "cand-9691"],
)
add_statement(
    "st-chp10-p318-fantasy-and-reason-debate-in-italian-circles", "cand-9715", "cand-0992", "debated-relative-proportions-in-the-creative-act",
    141, 141,
    "Haskell says an issue frequently discussed in early-eighteenth-century Italian literary and philosophical circles was the relative role of fantasy and reason in creative activity.",
    "One of the problems that was most discussed in Italian literary and philosophical circles in the early years of the eighteenth century was that of the relative proportions that fantasy and reason should assume in the creative act.",
    "The participants and their institutions are unnamed; preserve the two index candidates Fantasy and reason / Reason and fantasy for later alignment.",
    ["cand-9715", "cand-0992", "cand-2110"],
)
add_statement(
    "st-chp10-p318-arcadia-and-french-critics-stimulated-debate", "cand-6460", "cand-9716", "formation-and-contact-with-critics-stimulated-fantasy-reason-debate",
    141, 141,
    "Haskell says the debate was stimulated by the Society of Arcadia's deliberate call to reason and by French critics who attacked the style of Marino, his followers, and Tasso.",
    "The discussion had been stimulated by the formation of the Society of Arcadia with its deliberate call to reason and by contact with French critics who had attacked the style not only of Marino and his followers but of Tasso himself.",
    "The Society and formation event reuse existing candidates; the French critics and Marino's followers remain unnamed. Footnote 3 awaits canonical note L302.",
    ["cand-6460", "cand-0114", "cand-9716", "cand-1548", "cand-9717", "cand-2544", "cand-0992", "cand-2110"], True,
    {"footnote_marker": 3, "pending_note_source_line": 302},
)
add_statement(
    "st-chp10-p318-conti-extended-debate-into-visual-arts", "cand-0826", "cand-9718", "extended-discussion-into-visual-arts-and-influenced-other-writers",
    141, 141,
    "Haskell says a Venetian contributor, identified in the next sentence as Antonio Conti, sometimes extended the debate into visual arts and played some part in their development mainly through influence on other writers.",
    "Among those who made interesting contributions to the debate that followed was a Venetian who sometimes extended the discussion into the field of the visual arts and thus—mainly through his influence on other writers— played some part in their development.",
    "The local textual referent is Antonio Conti, named immediately afterward. 'Some part' and 'mainly through' limit the author's claim. Footnote 4 later in the paragraph awaits L303.",
    ["cand-0826", "cand-9718", "cand-9719"], True,
)
add_statement(
    "st-chp10-p318-conti-among-italian-intellectuals-seeking-travel", "cand-0826", "cand-9696", "among-pioneers-who-saw-visit-to-england-and-france-as-essential",
    142, 142,
    "Haskell says Conti was among the pioneers of a growing group of Italian intellectuals who considered a visit to England and France essential to avoid Venice's stifling provincialism.",
    "Antonio Conti, of noble origins, was among the pioneers of that growing number of Italian intellectuals who realised that a visit to England and France was essential to avoid the stifling provincialism of Venice.",
    "The group is not enumerated; the sentence states their view of travel, not that all members made the same journey. Footnote 4 awaits canonical note L303.",
    ["cand-0826", "cand-9696", "cand-0975", "cand-8983", "cand-5317", "cand-2719"], True,
    {"footnote_marker": 4, "pending_note_source_line": 303},
)
add_statement(
    "st-chp10-p318-conti-visited-paris-in-1713", "cand-0826", "cand-4653", "went-to-paris-in-1713-at-age-36-and-contacted-intellectuals",
    142, 142,
    "Haskell says Conti went to Paris in 1713 at age 36 and was in touch with Malebranche, Fontenelle, and other leading figures.",
    "In 1713, at the age of 36, he went to Paris, where he was in touch with Malebranche, Fontenelle and other leading figures.",
    "The source names only two of the other contacts; note 4 cites Robertson and the 1756 edition of Prose e Poesie.",
    ["cand-0826", "cand-4653", "cand-1499", "cand-1050", "cand-9720"], True,
)
add_statement(
    "st-chp10-p318-conti-crossed-channel-and-met-newton", "cand-0826", "cand-1739", "two-years-later-crossed-channel-and-met-newton",
    142, 142,
    "Haskell says Conti crossed the Channel two years after the 1713 Paris visit and met Isaac Newton, who became the most influential man in Conti's life.",
    "Two years later he crossed the Channel and met SirTsaac Newton, who was to become the most influential man in his Use.",
    "'Two years later' is retained rather than recalculated as a new date. The scan reads 'Sir Isaac Newton'; OCR merged the letters. This is Haskell's account of the meeting and influence.",
    ["cand-0826", "cand-0828", "cand-6810", "cand-1739"], True,
)
add_statement(
    "st-chp10-p318-conti-newton-relationship-initially-satisfactory", "cand-0826", "cand-1739", "initial-relationship-highly-satisfactory-to-both",
    142, 142,
    "Haskell says the initial relationship between Conti and Newton was highly satisfactory to both.",
    "At first the relationship was highly satisfactory to both",
    "The sentence is cut off at the page boundary and continues in the next source segment; do not infer the later course of the relationship until p.319 is read.",
    ["cand-0826", "cand-0828", "cand-1739"], True,
    {"continuation_segment_id": NEXT_SEGMENT, "statement_continues": True},
)

previous_segment_text = "\n".join(source_lines[118:131])
if not any(row["statement_id"] == PREVIOUS_CONTINUATION_STATEMENT for row in new_statements):
    raise SystemExit("p.317 cross-page sentence was not closed")
if not any(row["statement_id"] == "st-chp10-p318-conti-newton-relationship-initially-satisfactory" for row in new_statements):
    raise SystemExit("p.318 final partial relationship statement is missing")
statement_ids = {row["statement_id"] for row in statements}
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("p.318 statement ID already exists")

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements

previous_note = coverage[PREVIOUS_SEGMENT].get("note", "")
coverage[PREVIOUS_SEGMENT]["note"] = previous_note + (
    " p.317 L131 'Although much had been achieved before' is completed on p.318 by "
    f"{PREVIOUS_CONTINUATION_STATEMENT}; the p.317 segment remains partial pending footnotes at canonical notes L298–299."
)
coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L134-142",
    "note": (
        "Read printed p.318 against CHP-10.pdf physical p.51. L134 'then' completes p.317's sentence about earlier achievements "
        f"and the 1748 Peace of Aix-la-Chapelle; the cross-page statement is {PREVIOUS_CONTINUATION_STATEMENT}. L134–137 covers "
        "Voltaire's reported comment, writers' response across Italy, three named publications, Genovesi's chair, Beccaria, and "
        "Haskell's claim that Italy entered the vanguard of contemporary thought. L138–140 covers Venice, censorship, Smith's "
        "library, Caterina Dolfin Tron, the Republic's status quo, Beccaria's unnamed opponent, expulsions, and foreign influences. "
        "L141–142 covers the fantasy/reason debate, Arcadia, French critics, and Antonio Conti's intellectual and travel context. "
        "Added 17 candidates, exact mentions, and 21 statements; existing indexed people, places, events, and terms were reused. "
        "The final Conti–Newton relationship sentence continues at " + NEXT_SEGMENT + ". Footnotes 1–4 await canonical notes L300–303. "
        "Print corrections recorded without changing S0: Della puhblica felicita -> Della pubblica felicità; de’buoni -> de’ buoni; "
        "SirTsaac -> Sir Isaac. Printed-page source numbering and OCR line segmentation are retained. Coverage remains partial pending "
        "the next-page continuation and those notes; contested historical claims, identities, and formal relations remain for later stages."
    ),
})

print(f"p.318 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print(f"coverage: p.318 reviewed/partial; next source segment {NEXT_SEGMENT}; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
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
