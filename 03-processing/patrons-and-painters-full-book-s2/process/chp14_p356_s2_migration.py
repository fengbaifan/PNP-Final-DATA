"""Controlled S2 migration for printed p.356; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
BODY_PREV = "chp-14:14_CHP-14_intro:l85-95"
BODY = "chp-14:14_CHP-14_intro:l97-105"
BODY_NEXT = "chp-14:14_CHP-14_intro:l107-116"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BACKUP_SUFFIX = ".bak-s2-chp14-p356-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.356 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


source_bytes = SOURCE.read_bytes()
pdf_bytes = PDF.read_bytes()
source_hash = hashlib.sha256(source_bytes).hexdigest()
pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
if source_hash != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if pdf_hash != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in {
    98: "employed by Consul Smith, and a year or two earlier Bonomo had written",
    99: "In 1746, after about two and a half years in Venice",
    100: "Algarotti left Italy and did not return there until 1753",
    101: "Giovanni Marchiori to produce some figures for a church in",
    103: "Great.",
    104: "neo-Palladianism that he had seen in England",
    105: "plans of Lord Burlington’s house at Chiswick",
    194: "Letter from Bonomo dated 28 January 1740/1 in Treviso, MSS. 1256",
    195: "ibid., letters of 11 April, 20 May, 7 June, 5 November 1749",
    196: "ibid., letters of 25 October 1750 and 23 April 1752",
    197: "letter to Bonomo from Carcassonne of 2 July 1738",
    198: "Quoted by Treat, p. 209",
    199: "Letters of December 1742 in Treviso, MSS. 1256",
    200: "See letters to Frederick the Great of 4 August and 13 December 1751",
}.items():
    if required not in source_lines[line_number - 1]:
        raise SystemExit(f"required source text changed at L{line_number}")
if "Frederick the Great and his courtiers" not in source_lines[100]:
    raise SystemExit("required adviser phrase changed at L101")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, BODY_NEXT, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if (coverage_by_id[BODY_PREV]["migration_status"] != "partial"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "partial"
        or coverage_by_id[NOTES]["source_line_ranges"] != "L169-193"):
    raise SystemExit("S2 coverage preconditions changed")

previous_statement_id = "st-chp14-p355-canaletto-intensively-employed-partial"
if previous_statement_id not in statement_by_id:
    raise SystemExit("missing p.355 open cross-page statement")
if statement_by_id[previous_statement_id]["object_candidate_id"] is not None:
    raise SystemExit("p.355 Canaletto statement was already closed or revised")

new_candidates = [
    ("cand-10328", "Unidentified figures commissioned from Giovanni Marchiori for a church in Berlin (p.356)", "work", 102,
     "Haskell reports a commission for some figures but supplies no subject, number, medium, church name, or evidence that the figures were completed."),
    ("cand-10329", "Francesco Algarotti’s commission to Giovanni Marchiori for figures for a Berlin church (p.356)", "event", 102,
     "Commission reported by Haskell; the church, figures, date, and documentary source are unspecified on this page."),
    ("cand-10330", "Francesco Algarotti’s letter of introduction for Edmé Bouchardon (p.356)", "archive", 102,
     "Haskell reports an introduction letter for Bouchardon but gives no date, exact text, or independent identifier."),
    ("cand-10331", "Unidentified Veronese painting considered by Algarotti as a gift for Horace Walpole (1738; p.356)", "work", 102,
     "The painting is not titled or otherwise identified; the cited letter expresses a conditional intention depending on price."),
    ("cand-10332", "Two unidentified pictures bequeathed by Francesco Algarotti to William Pitt the Elder (1764; p.356)", "work", 102,
     "The will is reported to leave two pictures but neither work is identified here."),
    ("cand-10333", "Francesco Algarotti’s will drawn up in 1764", "archive", 102,
     "Referenced by Haskell for a bequest of two unidentified pictures; the will itself was not independently consulted."),
    ("cand-10334", "Unidentified suitable pictures from Algarotti and Bonomo’s collection sought for sale abroad (p.356)", "work", 102,
     "Haskell says Algarotti asked Bonomo to select suitable examples for disposal abroad; the works and the collection’s identity are unspecified."),
    ("cand-10335", "Letter from Bonomo dated 28 January 1740/1 about Canaletto’s prices and commissions (p.356 n.1)", "archive", 194,
     "Haskell cites a letter in Treviso MSS. 1256 and prints an Italian passage; the manuscript was not independently consulted and the works meant by ‘farli’ are unresolved."),
    ("cand-10336", "Letter dated 11 April 1749 cited in p.356 n.2 (Treviso MSS. 1256)", "archive", 195,
     "One of four separately dated letters listed by Haskell; sender, recipient, and individual contents are not specified in the note."),
    ("cand-10337", "Letter dated 25 October 1750 cited in p.356 n.3 (Treviso MSS. 1256)", "archive", 196,
     "One of two separately dated letters listed by Haskell; sender, recipient, and individual contents are not specified in the note."),
    ("cand-10338", "Letter to Bonomo from Carcassonne dated 2 July 1738 (p.356 n.4)", "archive", 197,
     "Haskell quotes the letter about a conditional purchase of a Veronese as a gift to Walpole; the manuscript was not independently consulted."),
    ("cand-10339", "Letters dated December 1742 cited in p.356 n.6", "archive", 199,
     "The note locates the letters in Treviso MSS. 1256 but does not identify their dates, authors, recipients, or contents individually."),
    ("cand-10340", "Letter to Frederick the Great dated 4 August 1751 (Opere XV, pp.153–155; p.356 n.7)", "archive", 200,
     "One of two separately dated letters cited by Haskell; the text and edition were not independently consulted."),
    ("cand-10341", "Potsdam, mentioned as a place where Francesco Algarotti spent time (p.356)", "place", 100,
     "Place is identified directly by the book text; no external alignment is attempted in S2."),
    ("cand-10342", "Unidentified plans of Lord Burlington’s house at Chiswick requested by Algarotti (p.356)", "work", 105,
     "The plans are requested as illustrations; no set, date, maker, or present location is specified."),
    ("cand-10343", "Unidentified original drawings by Andrea Palladio requested by Algarotti (p.356)", "work", 105,
     "The drawings are mentioned as a group without individual subjects, dates, or repositories."),
    ("cand-10344", "Neo-Palladianism encountered by Algarotti in England (p.356)", "term", 104,
     "The term names an architectural tendency in Haskell’s account; this candidate records the book’s concept use, not an external definition."),
    ("cand-10345", "Ida Treat, p.209 (locator for the Diderot quotation about Algarotti’s bequest; p.356 n.5)", "archive", 198,
     "Pinpoint locator cited by Haskell; Treat’s book and the quoted passage were not independently consulted."),
    ("cand-10346", "Letter dated 20 May 1749 cited in p.356 n.2 (Treviso MSS. 1256)", "archive", 195,
     "One of four separately dated letters listed by Haskell; sender, recipient, and individual contents are not specified in the note."),
    ("cand-10347", "Letter dated 7 June 1749 cited in p.356 n.2 (Treviso MSS. 1256)", "archive", 195,
     "One of four separately dated letters listed by Haskell; sender, recipient, and individual contents are not specified in the note."),
    ("cand-10348", "Letter dated 5 November 1749 cited in p.356 n.2 (Treviso MSS. 1256)", "archive", 195,
     "One of four separately dated letters listed by Haskell; sender, recipient, and individual contents are not specified in the note."),
    ("cand-10349", "Letter dated 23 April 1752 cited in p.356 n.3 (Treviso MSS. 1256)", "archive", 196,
     "One of two separately dated letters listed by Haskell; sender, recipient, and individual contents are not specified in the note."),
    ("cand-10350", "Letter to Frederick the Great dated 13 December 1751 (Opere XV, pp.153–155; p.356 n.7)", "archive", 200,
     "One of two separately dated letters cited by Haskell; the text and edition were not independently consulted."),
    ("cand-10351", "Francesco Algarotti’s letter of introduction for Bernhard Rode (p.356)", "archive", 102,
     "Haskell reports an introduction letter for Rode but gives no date, exact text, or independent identifier."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    if candidate_by_id and int(cid.split("-")[1]) <= max(int(k.split("-")[1]) for k in candidate_by_id):
        raise SystemExit(f"candidate ID is not above the current maximum: {cid}")
    seg = NOTES if source_line >= 168 else BODY
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{seg}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

segment_bounds = {BODY: (97, 105), NOTES: (168, 220)}
segment_texts = {sid: "\n".join(source_lines[first - 1:last]) for sid, (first, last) in segment_bounds.items()}
planned_mentions = []
mention_counter = 1


def add_mention(segment_id, candidate_id, surface, note=""):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    text = segment_texts[segment_id]
    occupied = [(int(r["start_char"]), int(r["end_char"])) for r in mentions + planned_mentions if r["segment_id"] == segment_id]
    start = 0
    while True:
        pos = text.find(surface, start)
        if pos < 0:
            original = text.find(surface)
            collisions = [r for r in mentions + planned_mentions if r["segment_id"] == segment_id
                          and int(r["start_char"]) < original + len(surface)
                          and original < int(r["end_char"])]
            raise SystemExit(f"surface not found in {segment_id}: {surface!r}; overlaps={collisions}")
        end = pos + len(surface)
        if not any(pos < old_end and old_start < end for old_start, old_end in occupied):
            break
        start = pos + 1
    mention_id = f"m-chp14-p356-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(pos), "end_char": str(end), "note": note,
    })
    mention_counter += 1


# Body and cross-page sentence, following the printed text from p.355 to p.356.
add_mention(BODY, "cand-2440", "Consul Smith")
add_mention(BODY, "cand-0040", "Bonomo")
add_mention(BODY, "cand-0082", "Venice")
add_mention(BODY, "cand-0065", "Algarotti")
add_mention(BODY, "cand-3461", "Italy")
add_mention(BODY, "cand-0947", "Dresden")
add_mention(BODY, "cand-3906", "Berlin")
add_mention(BODY, "cand-10341", "Potsdam")
add_mention(BODY, "cand-3461", "Italy")
add_mention(BODY, "cand-1080", "Frederick the Great")
add_mention(BODY, "cand-3906", "Berlin")
add_mention(BODY, "cand-0047", "Algarotti")
add_mention(BODY, "cand-3461", "Italian")
add_mention(BODY, "cand-2719", "Venetian")
add_mention(BODY, "cand-1541", "Giovanni Marchiori")
add_mention(BODY, "cand-10329", "commision")
add_mention(BODY, "cand-10328", "some figures")
add_mention(BODY, "cand-3906", "Berlin")
add_mention(BODY, "cand-0040", "Bonomo")
add_mention(BODY, "cand-3461", "Italy")
add_mention(BODY, "cand-4653", "Paris")
add_mention(BODY, "cand-0420", "Bouchardon")
add_mention(BODY, "cand-2207", "Rode")
add_mention(BODY, "cand-3781", "Tiepolo")
add_mention(BODY, "cand-10331", "a Veronese")
add_mention(BODY, "cand-2798", "Walpole")
add_mention(BODY, "cand-10333", "his will")
add_mention(BODY, "cand-10332", "two pictures")
add_mention(BODY, "cand-1947", "elder Pitt")
add_mention(BODY, "cand-0919", "Diderot")
add_mention(BODY, "cand-10334", "suitable examples")
add_mention(BODY, "cand-10330", "letters of introduction, for instance, for the French sculptor")
add_mention(BODY, "cand-10351", "German painter")
add_mention(BODY, "cand-1080", "Frederick the\nGreat")
add_mention(BODY, "cand-10344", "neo-Palladianism")
add_mention(BODY, "cand-8983", "England")
add_mention(BODY, "cand-1080", "Frederick")
add_mention(BODY, "cand-0470", "Lord Burlington")
add_mention(BODY, "cand-0471", "house at Chiswick")
add_mention(BODY, "cand-10342", "plans of")
add_mention(BODY, "cand-1807", "Palladio")
add_mention(BODY, "cand-10343", "original drawings")
add_mention(BODY, "cand-3461", "Italy")
add_mention(BODY, "cand-0049", "He also wrote to acquaintances",
            "The sentence stops at ‘supply’ on p.356 and continues on p.357; the supplied items are not inferred here.")
add_mention(BODY, "cand-3461", "Italy")

# Footnotes 1-7 on printed p.356.
add_mention(NOTES, "cand-10335", "dated 28 January 1740/1")
add_mention(NOTES, "cand-0040", "Bonomo")
add_mention(NOTES, "cand-0498", "Canaletto")
add_mention(NOTES, "cand-9209", "Treviso")
add_mention(NOTES, "cand-10251", "MSS. 1256")
add_mention(NOTES, "cand-10336", "11 April")
add_mention(NOTES, "cand-10346", "20 May")
add_mention(NOTES, "cand-10347", "7 June")
add_mention(NOTES, "cand-10348", "5 November 1749")
add_mention(NOTES, "cand-10337", "25 October 1750")
add_mention(NOTES, "cand-10349", "23 April 1752")
add_mention(NOTES, "cand-10338", "Carcassonne of 2 July 1738")
add_mention(NOTES, "cand-0040", "Bonomo")
add_mention(NOTES, "cand-2755", "Veronese")
add_mention(NOTES, "cand-2798", "Walpole")
add_mention(NOTES, "cand-8983", "Inghilterra")
add_mention(NOTES, "cand-10345", "p. 209")
add_mention(NOTES, "cand-10231", "Treat")
add_mention(NOTES, "cand-10246", "roi de Prusse")
add_mention(NOTES, "cand-1947", "M. Guillaume Pitt")
add_mention(NOTES, "cand-10339", "Letters of December 1742")
add_mention(NOTES, "cand-9209", "Treviso")
add_mention(NOTES, "cand-10251", "MSS. 1256")
add_mention(NOTES, "cand-10340", "4 August")
add_mention(NOTES, "cand-10350", "13 December 1751")
add_mention(NOTES, "cand-1080", "Frederick the Great")
add_mention(NOTES, "cand-10229", "Opéré, XV")

unmentioned_new_candidates = {row[0] for row in new_candidates} - {row["candidate_id"] for row in planned_mentions}
if unmentioned_new_candidates:
    raise SystemExit(f"new candidates without an S2 mention anchor: {sorted(unmentioned_new_candidates)}")


def quote(segment_id, line_start, line_end):
    return "\n".join(source_lines[line_start - 1:line_end])


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", qualification="", mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 356, "pdf_physical_page": 10,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(segment_id, line_start, line_end),
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


def footnote(marker, note_lines, linked_statement):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": note_lines, "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_note_statement_ids": [linked_statement],
    }


# Complete the p.355 sentence without replacing its source-local quotation.
previous = statement_by_id[previous_statement_id]
previous["object_candidate_id"] = "cand-2440"
previous["predicate"] = "reported_as_intensively_employed_by_consul_smith"
previous["qualifiers"].update({
    "claim": "Haskell says Canaletto was still intensively employed by Consul Smith; he adds that Bonomo had written a year or two earlier that commissions kept Canaletto several years on a painting.",
    "qualification": "The sentence begins on p.355 L95 and closes at p.356 L98. The p.356 continuation is linked rather than copied into the p.355 source quotation. Note 1 reports a high price and a multi-year completion time but does not identify the works meant by ‘farli’.",
    "mentioned_candidate_ids": ["cand-0498", "cand-2440", "cand-0040"],
    "cross_reference_segments": [BODY, NOTES],
    "cross_reference_text": "p.356 L98 closes the sentence with ‘employed by Consul Smith…’; p.356 n.1 at L194 cites Bonomo’s letter.",
    **footnote(1, "L194", "st-chp14-p356-note1-bonomo-canaletto-price-time"),
})

# Body statements: travel, patronage, artistic networks, gifts, and architecture.
add_statement(
    "st-chp14-p356-algarotti-left-italy-1746-returned-1753", BODY, "cand-0065", "cand-3461",
    "left_italy_in_1746_returned_in_1753", 99, 100,
    "Haskell reports that Algarotti left Italy in 1746 after about two and a half years in Venice, apart from one short break, and did not return until 1753.",
    qualification="The durations are Haskell’s approximate chronology; the short break is not dated.",
    mentioned=["cand-0065", "cand-0082", "cand-2719", "cand-3461"], relation_candidate=True,
    ocr_corrections=[{"source_line": 100, "ocr": "thistime", "print": "this time", "basis": "CHP-14.pdf physical page 10."}])

add_statement(
    "st-chp14-p356-algarotti-between-berlin-potsdam", BODY, "cand-0065", "cand-3906",
    "spent_most_of_next_seven_years_between_berlin_and_potsdam", 100, 100,
    "After going first to Dresden, Algarotti soon left for Berlin and spent most of the next seven years between Berlin and Potsdam.",
    qualification="‘Most of the next seven years’ is retained as the book’s wording; it is not converted into continuous residence.",
    mentioned=["cand-0065", "cand-0947", "cand-3906", "cand-10341"], relation_candidate=True)

add_statement(
    "st-chp14-p356-adviser-frederick-berlin-arts-plans", BODY, "cand-0047", "cand-1080",
    "advised_frederick_amid_plans_for_berlin_as_arts_centre", 100, 101,
    "Haskell says Algarotti acted as adviser to Frederick the Great and his courtiers, who had ambitious plans to turn Berlin into a major centre of the arts.",
    qualification="The planned status of Berlin is attributed to Frederick and his courtiers; it is not recorded as an achieved institution.",
    mentioned=["cand-0047", "cand-1080", "cand-3906"], relation_candidate=True)

add_statement(
    "st-chp14-p356-promoted-italian-venetian-art-abroad", BODY, "cand-0063", None,
    "promoted_italian_and_especially_venetian_art_abroad", 101, 101,
    "Haskell characterizes Algarotti’s promotion of Italian, especially Venetian, art abroad as driven by several motives.",
    qualification="This is Haskell’s interpretation of motives, not a direct statement by Algarotti.",
    mentioned=["cand-0063", "cand-3461", "cand-2719"])

add_statement(
    "st-chp14-p356-marchiori-berlin-church-commission", BODY, "cand-0063", "cand-1541",
    "obtained_commission_for_figures_for_church_in_berlin", 101, 102,
    "Haskell reports that Algarotti obtained a commission for sculptor Giovanni Marchiori to produce some figures for an unnamed church in Berlin.",
    qualification="The church and figures are unidentified, and the wording does not establish completion. The attached note lists letters in Treviso MSS. 1256 but the manuscripts were not inspected here.",
    mentioned=["cand-0063", "cand-1541", "cand-10328", "cand-10329", "cand-3906"],
    relation_candidate=True,
    ocr_corrections=[{"source_line": 101, "ocr": "commision", "print": "commission", "basis": "CHP-14.pdf physical page 10."}],
    **footnote(2, "L195", "st-chp14-p356-note2-letters-1749"))

add_statement(
    "st-chp14-p356-bonomo-honour-of-italy-quotation", BODY, "cand-0063", "cand-0040",
    "urged_bonomo_for_honour_of_italy", 102, 102,
    "Haskell quotes Algarotti urging Bonomo to act ‘for the honour of Italy’, followed by the French phrase ‘hors de Paris point de salut’.",
    text_layer="authorial report quoting Algarotti",
    qualification="The quotation is presented through Haskell’s account; no independent letter consultation is claimed.",
    mentioned=["cand-0063", "cand-0040", "cand-3461", "cand-4653"],
    relation_candidate=True, **footnote(2, "L195", "st-chp14-p356-note2-letters-1749"))

add_statement(
    "st-chp14-p356-encouraged-foreign-artists-study-in-italy", BODY, "cand-0063", None,
    "encouraged_foreign_artists_to_study_in_italy", 102, 102,
    "Haskell says Algarotti encouraged foreign artists to study in Italy and provided letters of introduction for Bouchardon and Rode.",
    qualification="The letters are not individually dated or identified; their collective candidate remains a citation-level object.",
    mentioned=["cand-0063", "cand-0420", "cand-2207", "cand-10330", "cand-10351", "cand-3461"],
    relation_candidate=True, **footnote(3, "L196", "st-chp14-p356-note3-letters-1750-1752"))

add_statement(
    "st-chp14-p356-rode-influence-tiepolo-prospective", BODY, "cand-2207", "cand-3781",
    "was_expected_to_be_much_influenced_by", 102, 102,
    "Haskell says the German painter Rode was to be much influenced by Tiepolo.",
    qualification="The source uses prospective wording (‘was to be’); this is not recast as a verified completed influence claim.",
    mentioned=["cand-2207", "cand-3781"], relation_candidate=True,
    **footnote(3, "L196", "st-chp14-p356-note3-letters-1750-1752"))

add_statement(
    "st-chp14-p356-prestige-through-successful-coup", BODY, "cand-0047", None,
    "prestige_gained_with_each_successful_coup", 102, 102,
    "Haskell says Algarotti understood that his own prestige increased with every successful ‘coup’.",
    qualification="‘Coup’ is retained as Haskell’s characterization of a successful acquisition or intervention; no specific event is supplied in this clause.",
    mentioned=["cand-0047"])

add_statement(
    "st-chp14-p356-expensive-presents-to-influential-people", BODY, "cand-0047", None,
    "was_anxious_to_give_expensive_presents_to_the_right_people", 102, 102,
    "Haskell describes Algarotti as excessively anxious to give expensive presents to the right people.",
    qualification="This is Haskell’s evaluative description; the specific gift discussed next is separately recorded with its conditional wording.",
    mentioned=["cand-0047"])

add_statement(
    "st-chp14-p356-veronese-for-walpole-conditional-1738", BODY, "cand-0057", "cand-2798",
    "planned_to_acquire_veronese_for_walpole_in_1738", 102, 102,
    "Haskell says Algarotti was planning as early as 1738 to obtain a Veronese for Horace Walpole.",
    qualification="The work is unidentified. Note 4 quotes a conditional proposal dependent on the price being mediocre; it does not establish purchase or delivery.",
    mentioned=["cand-0057", "cand-10331", "cand-2755", "cand-2798"], relation_candidate=True,
    **footnote(4, "L197", "st-chp14-p356-note4-carcassonne-letter"))

add_statement(
    "st-chp14-p356-will-bequest-two-pictures-to-pitt", BODY, "cand-0057", "cand-1947",
    "bequeathed_two_pictures_to_william_pitt_in_1764", 102, 102,
    "Haskell reports that Algarotti’s will, drawn up in 1764, left two pictures to William Pitt the Elder.",
    qualification="Neither picture is identified. The sarcastic response is attributed to Diderot through Treat in note 5, not independently checked.",
    mentioned=["cand-0057", "cand-10332", "cand-10333", "cand-1947", "cand-0919"], relation_candidate=True,
    **footnote(5, "L198", "st-chp14-p356-note5-treat-diderot-quotation"))

add_statement(
    "st-chp14-p356-diderot-sarcastic-reaction-to-bequest", BODY, "cand-0919", "cand-0057",
    "sarcastically_commented_on_bequest_to_prussian_king_and_pitt", 102, 102,
    "Haskell reports that Diderot made sarcastic comments about the bequests to the king of Prussia and Pitt.",
    qualification="The quoted wording is supplied by Treat p.209 in note 5; it is a secondary quotation chain and has not been independently consulted.",
    mentioned=["cand-0919", "cand-10246", "cand-1947", "cand-10345"], relation_candidate=True,
    **footnote(5, "L198", "st-chp14-p356-note5-treat-diderot-quotation"))

add_statement(
    "st-chp14-p356-saw-opportunities-for-financial-gain", BODY, "cand-0063", None,
    "saw_opportunities_for_financial_gain", 102, 102,
    "Haskell says Algarotti undoubtedly saw opportunities for financial gain.",
    qualification="The assertion is Haskell’s; note 6 points to December 1742 letters in Treviso MSS. 1256, which were not independently consulted.",
    mentioned=["cand-0063", "cand-10339", "cand-9209", "cand-10251"],
    **footnote(6, "L199", "st-chp14-p356-note6-letters-december-1742"))

add_statement(
    "st-chp14-p356-asked-bonomo-to-select-pictures-from-their-collection", BODY, "cand-0063", "cand-0040",
    "asked_bonomo_to_select_suitable_pictures_for_sale_abroad", 102, 102,
    "Haskell says Algarotti repeatedly asked Bonomo to inspect ‘their collection’ and send suitable examples for disposal abroad.",
    qualification="The pronoun ‘their’ is not resolved: the text does not establish whether it means the family collection on p.355, the joint collection candidate from p.347, or another collection. The suitable pictures are unidentified and are not equated with canvases sent to Dresden on p.355.",
    mentioned=["cand-0063", "cand-0040", "cand-10223", "cand-10224", "cand-10312", "cand-10334"],
    relation_candidate=True,
    candidate_identity_questions=[{"candidate_id": "cand-10223", "issue": "p.356 ‘their collection’ is not explicitly identified as the personal collection described on p.347."},
                                 {"candidate_id": "cand-10224", "issue": "p.356 ‘their collection’ may refer to an Algarotti–Bonomo joint collection, but the pronoun is not resolved."},
                                 {"candidate_id": "cand-10312", "issue": "Do not merge the p.356 collection reference with the distinct family collection described on p.355 without evidence."}])

add_statement(
    "st-chp14-p356-kept-in-touch-with-venetian-market", BODY, "cand-0063", None,
    "kept_in_touch_with_venetian_art_market_and_new_patrons", 102, 102,
    "Haskell says Algarotti remained in close touch with the Venetian art market and sought pictures likely to appeal to his new patrons.",
    qualification="The prospective patrons and pictures are not individually named.",
    mentioned=["cand-0063", "cand-2719"])

add_statement(
    "st-chp14-p356-mixed-motives-in-dresden-purchases-and-frederick-proposals", BODY, "cand-0063", None,
    "mixed_motives_visible_in_dresden_purchases_and_proposals_to_frederick", 102, 103,
    "Haskell says the mixed motives can be traced in Algarotti’s Dresden purchases and proposals to Frederick the Great.",
    qualification="This is Haskell’s retrospective interpretation; individual purchases and proposals are not enumerated in this sentence.",
    mentioned=["cand-0063", "cand-0073", "cand-0148", "cand-0947", "cand-1080"], relation_candidate=True)

add_statement(
    "st-chp14-p356-algarotti-saw-neo-palladianism-in-england", BODY, "cand-0049", "cand-10344",
    "encountered_neo_palladianism_in_england", 104, 104,
    "Haskell says Algarotti had been struck by the neo-Palladianism he saw in England some years earlier.",
    qualification="The book does not specify a precise date or building in this sentence.",
    mentioned=["cand-0049", "cand-10344", "cand-8983"])

add_statement(
    "st-chp14-p356-sought-illustrations-to-convince-frederick", BODY, "cand-0049", "cand-1080",
    "sought_illustrations_to_convince_frederick_of_neo_palladianism", 104, 105,
    "Algarotti tried to obtain illustrations to convince Frederick of the merits of neo-Palladianism, including plans of Lord Burlington’s house at Chiswick and original drawings of Palladio.",
    qualification="The requested plans and drawings are unnamed groups; no evidence here establishes that they were obtained or sent.",
    mentioned=["cand-0049", "cand-1080", "cand-0470", "cand-0471", "cand-10342", "cand-1807", "cand-10343"],
    relation_candidate=True, **footnote(7, "L200", "st-chp14-p356-note7-frederick-letters"))

add_statement(
    "st-chp14-p356-letter-to-acquaintances-for-supply-partial", BODY, "cand-0049", None,
    "wrote_to_acquaintances_in_italy_asking_them_to_supply_partial", 105, 105,
    "Haskell begins a statement that Algarotti wrote to acquaintances in Italy asking them to supply something; the sentence stops at p.356 L105 and continues on p.357.",
    qualification="The requested objects are not supplied in the p.356 segment and are left unresolved until the adjacent p.357 segment is read.",
    mentioned=["cand-0049", "cand-3461"],
    cross_reference_segments=[BODY_NEXT], cross_reference_text="sentence continues after ‘asking them to supply’ at p.357 L108")

# Page 356 footnote statements preserve the cited-source chain and print/OCR differences.
add_statement(
    "st-chp14-p356-note1-bonomo-canaletto-price-time", NOTES, "cand-0040", "cand-0498",
    "letter_reports_high_price_and_years_to_complete_paintings", 194, 194,
    "P.356 note 1 cites a 28 January 1740/1 letter from Bonomo in Treviso MSS. 1256, quoting him that Canaletto would ask a considerable price and several years to complete paintings because he was pressed by commissions.",
    text_layer="authorial bibliographic note quoting Bonomo",
    qualification="Haskell’s note is the available evidence here; the letter was not independently consulted. The antecedent of Italian ‘farli’ is not identified and is not assigned to any particular works.",
    mentioned=["cand-0040", "cand-0498", "cand-10335", "cand-9209", "cand-10251"],
    cross_reference_segments=[BODY_PREV, BODY], cross_reference_text="explains the p.355–356 report that Canaletto was employed by Consul Smith",
    ocr_corrections=[{"source_line": 194, "ocr": "T1", "print": "Il", "basis": "CHP-14.pdf physical page 10."},
                     {"source_line": 194, "ocr": "pretcnderebbe", "print": "pretenderebbe", "basis": "CHP-14.pdf physical page 10."}])

add_statement(
    "st-chp14-p356-note2-letters-1749", NOTES, None, None,
    "cites_four_letters_in_treviso_mss_1256", 195, 195,
    "P.356 note 2 cites letters dated 11 April, 20 May, 7 June, and 5 November 1749, using ‘ibid.’ to continue the Treviso MSS. 1256 reference.",
    text_layer="authorial bibliographic note",
    qualification="The note supplies dates but not individual senders, recipients, or contents; the manuscripts were not independently consulted.",
    mentioned=["cand-10336", "cand-10346", "cand-10347", "cand-10348"], cross_reference_segments=[BODY],
    cross_reference_text="listed after the p.356 account of Marchiori’s commission and Algarotti’s appeal to Bonomo")

add_statement(
    "st-chp14-p356-note3-letters-1750-1752", NOTES, None, None,
    "cites_letters_of_1750_and_1752_in_treviso_mss_1256", 196, 196,
    "P.356 note 3 cites letters dated 25 October 1750 and 23 April 1752, using ‘ibid.’ for Treviso MSS. 1256.",
    text_layer="authorial bibliographic note",
    qualification="The note does not identify the individual letters’ senders, recipients, or contents; the manuscripts were not independently consulted.",
    mentioned=["cand-10337", "cand-10349"], cross_reference_segments=[BODY],
    cross_reference_text="listed after the report of letters of introduction for Bouchardon and Rode")

add_statement(
    "st-chp14-p356-note4-carcassonne-letter", NOTES, "cand-0047", "cand-10338",
    "letter_expresses_conditional_veronese_purchase_for_walpole", 197, 197,
    "P.356 note 4 quotes a 2 July 1738 letter to Bonomo from Carcassonne: if the price of the Veronese were only moderate, Algarotti would favor buying it as a gift for Cavalier Walpole in England, which might facilitate an unspecified idea.",
    text_layer="authorial bibliographic note quoting Algarotti",
    qualification="The proposal is conditional and does not establish a purchase, gift, or completed outcome. The manuscript was not independently consulted.",
    mentioned=["cand-0047", "cand-10338", "cand-0040", "cand-10331", "cand-2755", "cand-2798", "cand-8983"],
    cross_reference_segments=[BODY], cross_reference_text="supports the p.356 statement that Algarotti planned to obtain a Veronese for Walpole",
    ocr_corrections=[{"source_line": 197, "ocr": "fame un regalo", "print": "farne un regalo", "basis": "CHP-14.pdf physical page 10."},
                     {"source_line": 197, "ocr": "facilitate", "print": "facilitare", "basis": "CHP-14.pdf physical page 10."},
                     {"source_line": 197, "ocr": "1’esecuzione", "print": "l’esecuzione", "basis": "CHP-14.pdf physical page 10."}])

add_statement(
    "st-chp14-p356-note5-treat-diderot-quotation", NOTES, "cand-10231", "cand-0919",
    "treat_quotes_diderot_on_vanity_of_bequests", 198, 198,
    "P.356 note 5 says the French passage is quoted by Treat, p.209; the passage attributes to Diderot a remark that Algarotti’s bequests to the king of Prussia and William Pitt publicly displayed his friendship with great men and showed vanity.",
    text_layer="authorial bibliographic note; secondary quotation attributed to Diderot",
    qualification="Haskell cites Treat and does not identify a primary Diderot source in this note. Neither Treat nor the underlying source was independently consulted.",
    mentioned=["cand-10345", "cand-10231", "cand-10232", "cand-0919", "cand-10246", "cand-1947", "cand-10333"],
    cross_reference_segments=[BODY], cross_reference_text="follows Haskell’s p.356 account of the 1764 will and two pictures left to Pitt")

add_statement(
    "st-chp14-p356-note6-letters-december-1742", NOTES, None, "cand-10339",
    "cites_december_1742_letters_in_treviso_mss_1256", 199, 199,
    "P.356 note 6 cites letters of December 1742 in Treviso MSS. 1256.",
    text_layer="authorial bibliographic note",
    qualification="No exact dates, senders, recipients, or individual letter contents are given; the cited letters were not independently consulted.",
    mentioned=["cand-10339", "cand-9209", "cand-10251"], cross_reference_segments=[BODY],
    cross_reference_text="attached to Haskell’s statement about opportunities for financial gain")

add_statement(
    "st-chp14-p356-note7-frederick-letters", NOTES, None, None,
    "cites_two_letters_to_frederick_in_opere_xv", 200, 200,
    "P.356 note 7 cites letters to Frederick the Great dated 4 August and 13 December 1751 in Opere, volume XV, pages 153–155.",
    text_layer="authorial bibliographic note",
    qualification="The note identifies a published locator; the letters and volume were not independently consulted.",
    mentioned=["cand-10340", "cand-10350", "cand-1080", "cand-10229"], cross_reference_segments=[BODY],
    cross_reference_text="supports the p.356 account of requesting Chiswick plans and Palladio drawings",
    ocr_corrections=[{"source_line": 200, "ocr": "Opéré", "print": "Opere", "basis": "CHP-14.pdf physical page 10."}])

new_statements = [row for row in statements if row["statement_id"].startswith("st-chp14-p356-")]
new_statement_ids = {row["statement_id"] for row in new_statements}
for row in statements:
    if row["statement_id"].startswith("st-chp14-p356-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        if row["original_quote"] not in segment_texts[row["segment_id"]]:
            raise SystemExit(f"statement quote missing from source: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in candidate_by_id:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in candidate_by_id:
                raise SystemExit(f"mentioned candidate missing: {row['statement_id']} -> {cid}")
        for note_id in row["qualifiers"].get("footnote_note_statement_ids", []):
            if note_id not in new_statement_ids:
                raise SystemExit(f"footnote statement missing: {row['statement_id']} -> {note_id}")

for row in planned_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment_texts[row["segment_id"]][start:end] != row["surface_form"]:
        raise SystemExit(f"mention anchor mismatch: {row['mention_id']} {row['surface_form']!r}")
spans_by_segment = {}
for row in planned_mentions:
    spans_by_segment.setdefault(row["segment_id"], []).append(
        (int(row["start_char"]), int(row["end_char"]), row["mention_id"], row["surface_form"]))
for seg, spans in spans_by_segment.items():
    spans.sort()
    for left, right in zip(spans, spans[1:]):
        if left[1] > right[0]:
            raise SystemExit(f"overlapping mentions in {seg}: {left[2]} / {right[2]}")

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L86-95",
    "note": "Printed p.355 read against CHP-14.pdf physical p.9. L86 closes the p.354 sentence; L95’s Canaletto sentence closes at p.356 L98. Note 1 is linked at p.356 L194; S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L98-105",
    "note": "Printed p.356 read against CHP-14.pdf physical p.10. L98 closes the p.355 Canaletto sentence. L105 ends after ‘supply’; its sentence continues in p.357 segment L107-116. Notes 1-7 at L194-200 are linked; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-200",
    "note": "Printed p.347-p.356 notes read against CHP-14.pdf physical pages 1-10. P.356 notes 1-7 at L194-200 are transcribed and linked; later notes remain pending.",
})

print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": source_hash, "pdf_sha256": pdf_hash,
    "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statements),
    "updated_statements": [previous_statement_id],
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
    candidates.extend([])
    mentions.extend(planned_mentions)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
