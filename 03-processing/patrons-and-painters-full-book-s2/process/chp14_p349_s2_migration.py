"""Controlled S2 migration for printed p.349 body and notes 1-4; dry-run by default."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BODY_PREV = "chp-14:14_CHP-14_intro:l14-21"
BODY = "chp-14:14_CHP-14_intro:l23-33"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
BACKUP_SUFFIX = ".bak-s2-chp14-p349-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.349 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in {
    24: "a year and in November he lest for Paris.",
    28: "not alfògether well received.",
    32: "1743-5! 1753-6.",
    33: "converted by die ancient monuments",
    177: "12 February 1733 published in Opere, XI, p. 213.",
}.items():
    if required not in source_lines[line_number - 1]:
        raise SystemExit(f"required source text changed at L{line_number}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if coverage_by_id[BODY_PREV]["disposition"] != "reviewed" or coverage_by_id[BODY_PREV]["migration_status"] != "partial":
    raise SystemExit("p.348 body segment is not in the expected partial state")
if coverage_by_id[BODY]["disposition"] != "queued":
    raise SystemExit("p.349 body segment is not queued; refusing to overwrite")
if coverage_by_id[NOTES]["disposition"] != "reviewed" or coverage_by_id[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated chapter 14 notes segment is not in the expected partial state")

new_candidates = [
    ("cand-10254", "Cirey (place where Algarotti stayed with Voltaire; exact site identity unresolved)", "place", 24,
     "The source names Cirey as the place where Algarotti stayed with Voltaire; no building or precise site is established here."),
    ("cand-10255", "Russia (country in Algarotti's travel itinerary, p.349)", "place", 30,
     "Country named as part of Algarotti's travels; no itinerary details are supplied."),
    ("cand-10256", "Electorate of Saxony (political entity named in Augustus's title, p.349)", "institution", 30,
     "The source calls Augustus Elector of Saxony; retain the political entity separately from the person."),
    ("cand-10257", "Algarotti's classical taste in Haskell's p.349 discussion", "term", 33,
     "A stylistic preference discussed by Haskell; the passage asks whether travel modified it."),
    ("cand-10258", "Newtonianismo per le Dame (publication by Algarotti; edition unspecified)", "archive", 26,
     "Named book credited with bringing Algarotti immediate fame; no edition or publication imprint is supplied in this passage."),
    ("cand-10259", "Letters from Francesco Algarotti to Bonomo from Paris, November 1734-January 1736", "archive", 174,
     "A number of letters in the larger Treviso collection, identified by sender, recipient, place, and date range in Haskell's note; not independently consulted."),
    ("cand-10260", "Halsband (surname cited in p.349 note 2; work and full identity unspecified)", "person", 175,
     "The footnote gives only a surname, with no title or page locator; preserve the incomplete citation without guessing the work."),
    ("cand-10261", "Novelle della Repubblica delle Lettere, issue of 12 April 1758", "archive", 176,
     "Specific issue quoted by Haskell's note; distinguish it from the weekly bulletin candidate cand-9988."),
    ("cand-10262", "Letter by G. P. Zanotti dated 12 February 1735 (recipient unspecified)", "archive", 177,
     "Letter cited as indirect evidence of Algarotti's meetings with Crozat; the source note says it was published in Opere, XI, p.213. The letter was not consulted."),
    ("cand-10263", "Opere, volume XI, page 213 (citation locator in p.349 note 4)", "archive", 177,
     "Exact volume and page as printed in the footnote; publication edition and cited page were not independently checked."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES if source_line >= 168 else BODY}#L{source_line}",
    })
    candidate_by_id[cid] = candidates[-1]

segment_bounds = {BODY: (23, 33), NOTES: (168, 220)}
segment_offsets = {}
for segment_id, (line_start, line_end) in segment_bounds.items():
    offset = 0
    for number in range(line_start, line_end + 1):
        segment_offsets[(segment_id, number)] = offset
        offset += len(source_lines[number - 1]) + (1 if number < line_end else 0)
occupied_same_candidate = set()
mention_counter = 1


def add_surface(segment_id, candidate_id, surface, line_numbers, note=""):
    global mention_counter
    matched = False
    for number in line_numbers:
        line = source_lines[number - 1]
        search_from = 0
        while True:
            pos = line.find(surface, search_from)
            if pos < 0:
                break
            matched = True
            start = segment_offsets[(segment_id, number)] + pos
            end = start + len(surface)
            if not any(seg == segment_id and cid == candidate_id and s == start and e == end
                       for seg, cid, s, e in occupied_same_candidate):
                mention_id = f"m-chp14-p349-{mention_counter:04d}"
                if mention_id in mention_by_id:
                    raise SystemExit(f"mention ID already exists: {mention_id}")
                mentions.append({
                    "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                    "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
                })
                mention_by_id[mention_id] = mentions[-1]
                occupied_same_candidate.add((segment_id, candidate_id, start, end))
                mention_counter += 1
            search_from = pos + 1
    if not matched:
        raise SystemExit(f"surface not found in requested lines: {segment_id} {surface!r} {line_numbers}")


def add_pronouns(segment_id, candidate_id, forms, line_numbers, note="Coreference resolved from the immediate passage context."):
    global mention_counter
    for number in line_numbers:
        line = source_lines[number - 1]
        for form in forms:
            for match in re.finditer(rf"(?<![\w]){re.escape(form)}(?![\w])", line):
                start = segment_offsets[(segment_id, number)] + match.start()
                end = start + len(form)
                if any(seg == segment_id and cid == candidate_id and s == start and e == end
                       for seg, cid, s, e in occupied_same_candidate):
                    continue
                mention_id = f"m-chp14-p349-{mention_counter:04d}"
                if mention_id in mention_by_id:
                    raise SystemExit(f"mention ID already exists: {mention_id}")
                mentions.append({
                    "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                    "surface_form": form, "start_char": str(start), "end_char": str(end), "note": note,
                })
                mention_by_id[mention_id] = mentions[-1]
                occupied_same_candidate.add((segment_id, candidate_id, start, end))
                mention_counter += 1


# Printed p.349 body references; topical index candidates are retained for later S3 identity alignment.
for item in [
    ("Paris", "cand-4653", [24, 25]), ("London", "cand-1422", [25]),
    ("Pierre Crozat", "cand-0894", [24]), ("Maupertuis", "cand-1585", [24]),
    ("Voltaire", "cand-2791", [24, 25]), ("Cirey", "cand-10254", [24]),
    ("Italy", "cand-3461", [26, 29]), ("Venice", "cand-2719", [26, 28, 30, 32]),
    ("Milan", "cand-3418", [26]), ("Newtonianismo per le", "cand-10258", [26]),
    ("Dame", "cand-10258", [27], "Second line of the printed book title; joins the title fragment on L26."),
    ("Algarotti’s", "cand-0070", [28]), ("Italian", "cand-3461", [28]),
    ("Algarotti", "cand-0080", [29]),
    ("Turin", "cand-2662", [30]), ("France", "cand-5317", [30, 33]),
    ("England", "cand-8983", [30, 33]), ("Russia", "cand-10255", [30]),
    ("Frederick the Great", "cand-1079", [30]), ("Dresden", "cand-0947", [30]),
    ("Augustus", "cand-0148", [30]), ("Saxony", "cand-10256", [30]),
    ("Prussia", "cand-10246", [30]), ("Bologna", "cand-3398", [30]),
    ("Florence", "cand-3397", [31]), ("Pisa", "cand-5628", [31]),
    ("Tiepolo", "cand-2572", [32]), ("Canaletto", "cand-0499", [32]),
    ("Venetian", "cand-2719", [32]), ("Rome", "cand-4490", [33]),
    ("Carracci", "cand-0576", [33]), ("Domenichino", "cand-0932", [33]),
    ("Crozat", "cand-0894", [33]), ("Crozat", "cand-0894", [24]),
    ("French", "cand-5317", [33]), ("rococo painting", "cand-6555", [33]),
    ("classical taste", "cand-10257", [33]), ("Berlin", "cand-9073", [33]),
    ("the King", "cand-0148", [30], "Algarotti is described as working for Augustus, Elector of Saxony; the later title 'the King' is linked to Augustus III as indexed on p.349."),
]:
    surface, cid, lines, *note = item
    add_surface(BODY, cid, surface, lines, note=note[0] if note else "")

# Split the work-and-title phrasing to preserve exact per-line anchors; no title is reconstructed into S0.
add_surface(BODY, "cand-10258", "the work", [26], note="Refers to Newtonianismo per le Dame named on L26-27.")
add_surface(BODY, "cand-10258", "the book", [28], note="Refers to Newtonianismo per le Dame named on L26-27.")
add_pronouns(BODY, "cand-0080", ["he", "He", "his", "him"], [24, 25, 26, 28, 29, 30, 31, 32, 33])
add_pronouns(BODY, "cand-2791", ["whom"], [24], note="Relative pronoun refers to Voltaire, with whom Algarotti stayed at Cirey.")
add_pronouns(BODY, "cand-1079", ["who"], [30], note="Relative pronoun refers to Frederick the Great.")

for item in [
    ("Algarotti", "cand-0040", [174]),
    ("his brother Bonomo", "cand-0040", [174]),
    ("letters from Algarotti to his brother Bonomo", "cand-10259", [174]),
    ("Archivio Comunale in Treviso", "cand-10251", [174]),
    ("Paris", "cand-4653", [174]),
    ("Halsband", "cand-10260", [175]),
    ("Albrizzi’s", "cand-0025", [176]),
    ("Novelle della Repubblica delle Lettere", "cand-9988", [176]),
    ("12 April 1758", "cand-10261", [176]),
    ("G. P. Zanotti", "cand-7114", [177]),
    ("a letter from G. P. Zanotti of 12 February 1733", "cand-10262", [177],
     "The source OCR gives 1733; the printed p.349 image reads 1735. See the print-reading correction in the note statement."),
    ("12 February 1733", "cand-10262", [177],
     "OCR anchor retained exactly; the printed page reads 12 February 1735."),
    ("Opere, XI, p. 213", "cand-10263", [177]),
]:
    surface, cid, lines, *note = item
    add_surface(NOTES, cid, surface, lines, note=note[0] if note else "")


def quote(start, end, exact):
    allowed = "\n".join(source_lines[start - 1:end])
    if exact not in allowed:
        raise SystemExit(f"statement quotation is not present in L{start}-L{end}: {exact[:90]!r}")
    return exact


def q(start, end, claim, layer, qualification, candidate_ids, **extra):
    out = {
        "source_line_start": start, "source_line_end": end, "printed_page": 349,
        "pdf_physical_page": 3, "claim": claim, "speaker": "Haskell",
        "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    out.update(extra)
    return out


def add_statement(statement_id, segment_id, subject, obj, predicate, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    start, end = qualifiers["source_line_start"], qualifiers["source_line_end"]
    bounds = segment_bounds[segment_id]
    if not (bounds[0] <= start <= end <= bounds[1]):
        raise SystemExit(f"statement span escapes source segment: {statement_id}")
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers, "original_quote": original_quote,
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


link1 = {"footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L174",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p349-note1-bonomo-paris-letters"]}
link2 = {"footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L175",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p349-note2-halsband"]}
link3 = {"footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L176",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p349-note3-albrizzi-issue"]}
link4 = {"footnote_marker": "4", "footnote_segment": NOTES, "footnote_line_range": "L177",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p349-note4-zanotti-letter"]}

add_statement("st-chp14-p349-rome-to-paris", BODY, "cand-0080", "cand-4653", "departed_for",
    q(24, 24, "After remaining in Rome for less than a year, Algarotti left for Paris in November 1734.",
      "biographical narrative", "The sentence begins on p.348 L21; the p.349 continuation closes it. The printed page reads 'left'; OCR has 'lest'.",
      ["cand-0080", "cand-4490", "cand-4653"], ocr_corrections=[
          {"source_line": 24, "ocr": "lest", "print": "left", "basis": "CHP-14.pdf physical page 3."}],
      cross_reference_segments=[BODY_PREV], cross_reference_text="He remained less than a year"),
    quote(24, 24, "a year and in November he lest for Paris."))
add_statement("st-chp14-p349-paris-residence", BODY, "cand-0080", "cand-4653", "resided_in",
    q(24, 24, "Algarotti resided in Paris for some time.",
      "biographical narrative", "There refers to Paris in the preceding clause.",
      ["cand-0080", "cand-4653"]),
    quote(24, 24, "There he resided for some time"))
add_statement("st-chp14-p349-met-crozat", BODY, "cand-0080", "cand-0894", "met",
    q(24, 24, "During his Paris residence Algarotti met Pierre Crozat.",
      "biographical narrative", "Footnote 4 later cites a G. P. Zanotti letter as the indirect source for hearing of this meeting.",
      ["cand-0080", "cand-0894"], relation_candidate=True, **link4),
    quote(24, 24, "he met Pierre Crozat"))
add_statement("st-chp14-p349-met-maupertuis", BODY, "cand-0080", "cand-1585", "met",
    q(24, 24, "During his Paris residence Algarotti met Maupertuis.",
      "biographical narrative", "The source gives only the surname in the passage; candidate identity remains for S3.",
      ["cand-0080", "cand-1585"], relation_candidate=True),
    quote(24, 24, "Maupertuis"))
add_statement("st-chp14-p349-met-voltaire-and-cirey", BODY, "cand-0080", "cand-2791", "met_and_stayed_with",
    q(24, 24, "Algarotti met Voltaire and stayed with him at Cirey.",
      "biographical narrative", "Cirey is retained as a place candidate without resolving the precise site.",
      ["cand-0080", "cand-2791", "cand-10254"], relation_candidate=True),
    quote(24, 24, "Voltaire, with whom he stayed at Cirey."))
add_statement("st-chp14-p349-social-advances-hervey", BODY, "cand-0080", "cand-1298", "played_off_social_advances_from",
    q(25, 25, "Haskell says Algarotti cynically played off Lord Hervey's advances and that Hervey was enraptured by him.",
      "authorial characterization", "This is Haskell's characterization of social conduct; note 2 gives only the bare citation 'Halsband'.",
      ["cand-0080", "cand-1298", "cand-10260"], relation_candidate=True, **link2),
    quote(25, 25, "With some cynicism he played off the advances of Lord Hervey and Lady Mary Wortley Montagu, both of whom were enraptured by him."))
add_statement("st-chp14-p349-social-advances-montagu", BODY, "cand-0080", "cand-1688", "played_off_social_advances_from",
    q(25, 25, "Haskell says Algarotti cynically played off Lady Mary Wortley Montagu's advances and that she was enraptured by him.",
      "authorial characterization", "This is Haskell's characterization of social conduct; note 2 gives only the bare citation 'Halsband'.",
      ["cand-0080", "cand-1688", "cand-10260"], relation_candidate=True, **link2),
    quote(25, 25, "With some cynicism he played off the advances of Lord Hervey and Lady Mary Wortley Montagu, both of whom were enraptured by him."))
add_statement("st-chp14-p349-return-publish-newtonianismo", BODY, "cand-0080", None, "returned_and_published",
    q(25, 27, "After a short visit to Voltaire, Algarotti returned to Italy at the end of 1736, stayed about a year between Venice and Milan, and published Newtonianismo per le Dame.",
      "biographical narrative", "The book title is split across OCR lines 26-27; Haskell says its publication brought immediate fame.",
      ["cand-0080", "cand-2791", "cand-3461", "cand-2719", "cand-3418", "cand-10258"]),
    quote(25, 27, "After another short visit to Voltaire he returned to\nItaly at the very end of 1736 and stayed for about a year between Venice and Milan, where he published the work that brought him immediate fame, Newtonianismo per le\nDame."))
add_statement("st-chp14-p349-authored-newtonianismo", BODY, "cand-0080", "cand-10258", "authored_and_published",
    q(26, 27, "Algarotti published Newtonianismo per le Dame, which Haskell says brought him immediate fame.",
      "biographical narrative", "The title and authorship are given in Haskell's narrative; no edition is specified on this page.",
      ["cand-0080", "cand-10258"], relation_candidate=True),
    quote(26, 27, "where he published the work that brought him immediate fame, Newtonianismo per le\nDame."))
add_statement("st-chp14-p349-work-significance", BODY, "cand-0080", "cand-10258", "identified_as_major_contribution",
    q(27, 28, "Haskell describes Newtonianismo per le Dame as the first of a long series of works forming Algarotti's most important contribution to Italian culture: rendering complex European ideas in accessible forms.",
      "authorial interpretation", "This is Haskell's assessment of Algarotti's contribution and the work's method, not an independently verified reception history.",
      ["cand-0080", "cand-10258", "cand-3461"]),
    quote(27, 28, "It was the first of a long series of books and articles which were to constitute\nAlgarotti’s most important contribution to Italian culture—the translation into easy and attractive forms of some of the more complex and enlightened ideas of European thinkers."))
add_statement("st-chp14-p349-publication-reception", BODY, "cand-10258", None, "publication_blocked_and_received_critically",
    q(28, 28, "Haskell says the book could not be published in Venice and was not altogether well received; note 3 quotes an Albrizzi periodical warning readers to approach some expressions and sentiments with circumspection.",
      "authorial interpretation with cited contemporary reception", "The reception statement is Haskell's; the periodical passage is known here only through his note and was not independently consulted. OCR reads 'alfògether'; print reads 'altogether'.",
      ["cand-10258", "cand-2719", "cand-0025", "cand-9988", "cand-10261"], ocr_corrections=[
          {"source_line": 28, "ocr": "alfògether", "print": "altogether", "basis": "CHP-14.pdf physical page 3."}],
      **link3),
    quote(28, 28, "It was for this reason that the book proved impossible to publish in Venice and was not alfògether well received.3"))
add_statement("st-chp14-p349-left-italy-and-turin-mission", BODY, "cand-0080", None, "travelled_with_diplomatic_exception",
    q(28, 30, "After the book appeared in December 1737, Algarotti left Italy and did not return until May 1743 except for a diplomatic mission to Turin early in 1741.",
      "biographical narrative", "The source supplies a broad interval and one stated exception; the exception is not treated as a full return to Italy.",
      ["cand-0080", "cand-3461", "cand-2662"]),
    quote(28, 30, "Immediately after its appearance in December\n1737 Algarotti left Italy, not to return till May 1743 except for a diplomatic mission to\nTurin early in 1741."))
add_statement("st-chp14-p349-travel-and-frederick-court", BODY, "cand-0080", "cand-1079", "travelled_and_served_at_court",
    q(30, 30, "During this interval Algarotti travelled in France, England, and Russia before settling at the court of Frederick the Great, who made him a Count in December 1740.",
      "biographical narrative", "The source reports the title and date without providing a separate investiture document.",
      ["cand-0080", "cand-5317", "cand-8983", "cand-10255", "cand-1079"], relation_candidate=True),
    quote(30, 30, "During the interval he travelled in France, England and Russia, before settling in the court of one of his most enthusiastic admirers, Frederick the Great, who made him a Count in December 1740."))
add_statement("st-chp14-p349-worked-for-augustus-in-dresden", BODY, "cand-0080", "cand-0148", "worked_for",
    q(30, 30, "After a quarrel with Frederick the Great, Algarotti was in Dresden in 1742 working for Augustus, Elector of Saxony.",
      "biographical narrative", "The source names Augustus by title; the person candidate is kept distinct from the Electorate of Saxony candidate.",
      ["cand-0080", "cand-1079", "cand-0947", "cand-0148", "cand-10256"], relation_candidate=True),
    quote(30, 30, "But the two men quarrelled, and in 1742 he was in Dresden, working for Augustus, Elector of Saxony."))
add_statement("st-chp14-p349-venice-purchase-for-king", BODY, "cand-0080", "cand-0148", "bought_pictures_for",
    q(30, 30, "In May 1743 Algarotti visited Venice to buy pictures for Augustus III and remained there until 1745.",
      "biographical narrative", "The index identifies the King as Augustus III; this is consistent with the immediately preceding reference to Augustus, Elector of Saxony.",
      ["cand-0080", "cand-2719", "cand-0148", "cand-0073"], relation_candidate=True),
    quote(30, 30, "In May 1743 he payed a visit to Venice to buy pictures for the King, and he remained there until 1745."))
add_statement("st-chp14-p349-return-to-prussia-and-italian-residence", BODY, "cand-0080", None, "returned_and_resided",
    q(30, 31, "After 1745 Algarotti returned to Prussia for eight more years; after returning to Venice in 1753-1756 and a visit of less than a month in 1760, he lived in Bologna, Florence, and Pisa until his death in 1764.",
      "biographical narrative", "The visit lengths and residence sequence are retained as reported; the sentence does not give a specific death location.",
      ["cand-0080", "cand-10246", "cand-2719", "cand-3398", "cand-3397", "cand-5628"]),
    quote(30, 31, "He then returned to Prussia for eight more years. He was back in Venice from 1753 to 1756, after which (except for a short visit of less than a month in 1760) he lived in Bologna,\nFlorence and Pisa until his death in 1764."))
add_statement("st-chp14-p349-three-visits-to-venice", BODY, "cand-0080", "cand-2719", "returned_for_three_short_visits",
    q(32, 32, "Haskell summarizes three relatively short returns to Algarotti's native Venice: most of 1737, 1743-1745, and 1753-1756; only then was he in direct contact with Venetian artists.",
      "authorial synthesis", "The source OCR punctuation after 1743-5 is corrected from an exclamation mark to a semicolon based on the printed page.",
      ["cand-0080", "cand-2719"], ocr_corrections=[
          {"source_line": 32, "ocr": "1743-5!", "print": "1743-5;", "basis": "CHP-14.pdf physical page 3."}]),
    quote(32, 32, "Thus, after leaving Venice at the age of 20, he only returned to his native city for three relatively short visits—most of 1737; 1743-5! 1753-6. Only during these years was he in direct contact with the Venetian artists whose champion, patron and critic he professed himself."))
add_statement("st-chp14-p349-tiepolo-canaletto-active", BODY, "cand-0080", None, "artists_active_during_visits",
    q(32, 32, "Haskell says Tiepolo and Canaletto were at work in Venice during all three of Algarotti's returns.",
      "authorial synthesis", "The statement reports the artists' activity during the three periods; it does not assert that Algarotti met either artist on every visit.",
      ["cand-0080", "cand-2719", "cand-2572", "cand-0499"]),
    quote(32, 32, "Yet on all three occasions Tiepolo and Canaletto were at work in the city"))
add_statement("st-chp14-p349-correspondence-and-theoretical-influence-tiepolo", BODY, "cand-0080", "cand-2572", "corresponded_and_influenced",
    q(32, 32, "During his later years of ill health Algarotti sent Tiepolo letters and wrote theoretical treatises that Haskell says played a notable part in changing the artistic climate in which Tiepolo worked.",
      "authorial interpretation", "Haskell's account links letters and theoretical writing to a broader change in opinion; the specific effect on Tiepolo is not isolated beyond the shared context.",
      ["cand-0080", "cand-2572"], relation_candidate=True),
    quote(32, 32, "while during his later years of ill-health he bombarded them with letters and wrote theoretical treatises which played a notable part in changing the climate of opinion within which they worked."))
add_statement("st-chp14-p349-correspondence-and-theoretical-influence-canaletto", BODY, "cand-0080", "cand-0499", "corresponded_and_influenced",
    q(32, 32, "During his later years of ill health Algarotti sent Canaletto letters and wrote theoretical treatises that Haskell says played a notable part in changing the artistic climate in which Canaletto worked.",
      "authorial interpretation", "Haskell's account links letters and theoretical writing to a broader change in opinion; the specific effect on Canaletto is not isolated beyond the shared context.",
      ["cand-0080", "cand-0499"], relation_candidate=True),
    quote(32, 32, "while during his later years of ill-health he bombarded them with letters and wrote theoretical treatises which played a notable part in changing the climate of opinion within which they worked."))
add_statement("st-chp14-p349-rome-classical-conversion", BODY, "cand-0080", None, "converted_by_artistic_encounters",
    q(33, 33, "Haskell recaps that in 1734 Algarotti had been converted by Rome's ancient monuments and frescoes by the Carracci and Domenichino.",
      "authorial narrative recap", "This is Haskell's retrospective framing of the effect of the Roman visit; OCR reads 'die' and 'ofhis', while print reads 'the' and 'of his'.",
      ["cand-0080", "cand-4490", "cand-0576", "cand-0932"], ocr_corrections=[
          {"source_line": 33, "ocr": "die", "print": "the", "basis": "CHP-14.pdf physical page 3."},
          {"source_line": 33, "ocr": "ofhis", "print": "of his", "basis": "CHP-14.pdf physical page 3."}]),
    quote(33, 33, "We left him in 1734 converted by die ancient monuments of Rome and the frescoes of the Carracci and Domenichino."))
add_statement("st-chp14-p349-limited-evidence-about-crozat", BODY, "cand-0080", "cand-0894", "meeting_known_indirectly",
    q(33, 33, "Haskell says Algarotti provides little information about whether travel modified his classical taste and that his meetings with Crozat are known only indirectly; note 4 cites a G. P. Zanotti letter.",
      "authorial interpretation and evidence qualification", "The source explicitly limits the evidence; the cited letter was not independently consulted. OCR reads 1733, while the printed note reads 1735.",
      ["cand-0080", "cand-10257", "cand-8983", "cand-5317", "cand-0894", "cand-7114", "cand-10262", "cand-10263"],
      relation_candidate=True, **link4),
    quote(33, 33, "Was anything likely to modify this classical taste during the two years he then spent in England and France? Unfortunately he gives us little information on this point, and it is only indirectly that we hear of his meetings with Crozat.4"))
add_statement("st-chp14-p349-french-rococo-influence-inference", BODY, "cand-0080", "cand-6555", "influence_inferred",
    q(33, 33, "Haskell infers that French rococo painting encountered in Paris and especially Berlin must have strongly affected Algarotti's temperament.",
      "authorial inference", "The modal phrase 'must have been' marks this as Haskell's inference, not direct evidence. The sentence continues on p.350 and remains partial.",
      ["cand-0080", "cand-6555", "cand-4653", "cand-9073", "cand-10257"],
      cross_reference_segments=["chp-14:14_CHP-14_intro:l35-44"], cross_reference_text="p.350 continuation"),
    quote(33, 33, "But the effect of French rococo painting which he came across in Paris, and still more in Berlin, must have been powerful on a man ofhis temperament,"))

add_statement("st-chp14-p349-note1-bonomo-paris-letters", NOTES, None, None, "bibliographic_note",
    q(174, 174, "Note 1 says that a large collection of letters from Algarotti to Bonomo in the Archivio Comunale at Treviso includes letters from Paris between November 1734 and January 1736.",
      "authorial bibliographic note", "The note reports a collection and date range; neither the manuscripts nor repository catalogue was independently consulted.",
      ["cand-0080", "cand-0040", "cand-10251", "cand-4653", "cand-10259"]),
    quote(174, 174, source_lines[173]))
add_statement("st-chp14-p349-note2-halsband", NOTES, None, None, "bibliographic_note",
    q(175, 175, "Note 2 gives only the surname Halsband, without a title or page locator.",
      "authorial bibliographic note", "The cited work and full identity are unspecified; no bibliographic identification is inferred.",
      ["cand-10260"]),
    quote(175, 175, source_lines[174]))
add_statement("st-chp14-p349-note3-albrizzi-issue", NOTES, None, None, "bibliographic_note_and_quoted_reception",
    q(176, 176, "Note 3 quotes the 12 April 1758 issue of Novelle della Repubblica delle Lettere warning that some expressions and sentiments should be read with great circumspection, especially by Christian youth.",
      "authorial note quoting a periodical", "The Italian quotation and date are reported by Haskell; the periodical issue was not independently consulted.",
      ["cand-0025", "cand-9988", "cand-10261"]),
    quote(176, 176, source_lines[175]))
add_statement("st-chp14-p349-note4-zanotti-letter", NOTES, None, None, "bibliographic_note",
    q(177, 177, "Note 4 attributes the indirect evidence about Algarotti's meetings with Crozat to a G. P. Zanotti letter of 12 February 1735, published in Opere, volume XI, page 213.",
      "authorial bibliographic note", "The OCR reads 1733; the printed page image reads 1735. The letter, edition, and cited page were not independently consulted.",
      ["cand-0080", "cand-0894", "cand-7114", "cand-10262", "cand-10263"],
      ocr_corrections=[{"source_line": 177, "ocr": "1733", "print": "1735", "basis": "CHP-14.pdf physical page 3."}],
      cross_reference_segments=["chp-14:14_CHP-14_intro:l23-33"], cross_reference_text="footnote 4 marker after the Crozat meeting limitation"),
    quote(177, 177, source_lines[176]))

# P.349 closes the final p.348 clause, while its own last sentence continues on p.350.
coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L14-21",
    "note": "Printed p.348 read against CHP-14.pdf physical p.2. Its final clause 'He remained less than' is completed by p.349 L24 and linked to st-chp14-p349-rome-to-paris. S0 unchanged; print corrections are in statement qualifiers.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L23-33",
    "note": "Printed p.349 read against CHP-14.pdf physical p.3. Closes the p.348 Rome-duration sentence and links notes 1-4 to body statements. The last sentence ends 'on a man of his temperament,' and continues on p.350 L35; leave partial until closed. Printed readings that differ from OCR are in S2 qualifiers; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-177",
    "note": "Printed notes p.347-p.349 read against CHP-14.pdf physical pages 1-3. Notes 1-4 on p.349 are linked to their body markers. Remaining later-page notes in this consolidated source segment are pending.",
})

# Preflight foreign keys and exact character anchors for this batch.
known_ids = set(candidate_by_id)
for row in mentions:
    if row["mention_id"].startswith("m-chp14-p349-"):
        seg = row["segment_id"]
        bounds = segment_bounds[seg]
        text = "\n".join(source_lines[bounds[0] - 1:bounds[1]])
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']} {row['surface_form']!r}")
        if row["candidate_id"] not in known_ids:
            raise SystemExit(f"mention candidate missing: {row['mention_id']}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p349-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in known_ids:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in known_ids:
                raise SystemExit(f"statement mentioned candidate missing: {row['statement_id']} -> {cid}")

new_mentions = [r for r in mentions if r["mention_id"].startswith("m-chp14-p349-")]
new_statements = [r for r in statements if r["statement_id"].startswith("st-chp14-p349-")]
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "new_candidates": len(new_candidates), "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage_updates": {BODY_PREV: coverage_by_id[BODY_PREV], BODY: coverage_by_id[BODY], NOTES: coverage_by_id[NOTES]},
}, ensure_ascii=False, indent=2))

if args.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if hashlib.sha256(backup.read_bytes()).digest() != hashlib.sha256(path.read_bytes()).digest():
                raise SystemExit(f"existing backup differs from current pre-write file: {backup.name}")
        else:
            shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
