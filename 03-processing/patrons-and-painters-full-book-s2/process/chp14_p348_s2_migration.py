"""Controlled S2 migration for printed p.348 body and notes 1-3; dry-run by default."""
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
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
P347 = "chp-14:14_CHP-14_intro:l3-12"
BODY = "chp-14:14_CHP-14_intro:l14-21"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
BACKUP_SUFFIX = ".bak-s2-chp14-p348-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.348 S2 migration")
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
    15: "who helped, to put into practice most of Francesco’s ambitious plans",
    16: "After leaving Bologna Algarotti returned to the Veneto for a short time.",
    17: "‘1 go again and again to look at the divine works of Palladio",
    18: "Raphael’s St John the Baptist disappointing after the S. Cecilia in Bologna",
    19: "In February 1734 he moved on to Rome.",
    20: "‘These magnificent ruins’, he writes,2",
    21: "Very soon after his arrival he met Giovanni Bottari",
    171: "1 See his letters to F. M. Zanotti between 1732 and 1734",
    172: "2 Letter of 22 February 1734 to his brother Bonomo in Treviso",
    173: "3 See letters to F. M. and Eustachio Zanotti and Antonio Conti from Rome",
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

for segment_id in (P347, BODY, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if coverage_by_id[P347]["disposition"] != "reviewed" or coverage_by_id[P347]["migration_status"] != "partial":
    raise SystemExit("p.347 body segment is not in the expected partial state")
if coverage_by_id[BODY]["disposition"] != "queued":
    raise SystemExit("p.348 body segment is not queued; refusing to overwrite")
if coverage_by_id[NOTES]["disposition"] != "reviewed" or coverage_by_id[NOTES]["migration_status"] != "partial":
    raise SystemExit("combined p.347-361 notes segment is not in the expected partial state")

new_candidates = [
    ("cand-10240", "Benvenuto Cellini's Perseus (work admired by Algarotti in Florence)", "work", 17,
     "Work named in Haskell's account. The passage supplies no further title or version identification."),
    ("cand-10241", "Doors of the Baptistery in Florence admired by Algarotti (maker/version unspecified)", "work", 17,
     "The source names the doors but does not specify a particular gate, maker, or version."),
    ("cand-10242", "Raphael's St John the Baptist (painting cited in p.348; exact version unresolved)", "work", 18,
     "Descriptive work candidate following Haskell's short title. Do not infer a specific version or current location."),
    ("cand-10243", "Raphael's S. Cecilia in Bologna (painting cited in p.348; exact version unresolved)", "work", 18,
     "Descriptive work candidate following Haskell's short title and location; exact version is not established here."),
    ("cand-10244", "Unidentified paintings by Titian in the Grand Ducal collections at Florence", "work", 18,
     "Plural group of paintings; no titles, count, or individual work identities supplied."),
    ("cand-10245", "Grand Ducal collections at Florence (collection identity/type unresolved)", "", 18,
     "The source does not specify which collection or distinguish repository, institution, and accumulated collection."),
    ("cand-10246", "Prussia (destination of the Palladio cult in Haskell's account)", "place", 17,
     "Geographic/political region is named as the destination of the architectural cult; no specific court, city, or agent is supplied here."),
    ("cand-10247", "Unnamed Roman scholars and antiquarians critical of contemporary art (group described by Haskell)", "", 21,
     "A group is described but not named or institutionally identified; do not turn it into an academy."),
    ("cand-10248", "Algarotti's letters to F. M. Zanotti, 1732-1734 (cited in p.348 note 1)", "archive", 171,
     "Group of letters identified by addressee and date range in Haskell's note; letters were not independently consulted."),
    ("cand-10249", "Opere, volumes XI-XII (citation locator for p.348 note 1)", "archive", 171,
     "Short publication locator only; do not automatically merge with the descriptive 1791 seventeen-volume edition candidate cand-10229 before S3/bibliography review."),
    ("cand-10250", "Algarotti's letter to Bonomo, 22 February 1734 (Treviso MSS. 1256)", "archive", 172,
     "Letter identified by date, addressee, and shelfmark in Haskell's note; the manuscript was not consulted."),
    ("cand-10251", "Archivio Comunale, Treviso, MSS. 1256 (repository citation in p.348 note 2)", "institution", 172,
     "Repository as cited; keep distinct from Biblioteca Comunale, Treviso candidate cand-9450 pending S3."),
    ("cand-10252", "Algarotti's Rome letters to F. M. and Eustachio Zanotti and Antonio Conti, Feb-June 1734", "archive", 173,
     "Letter group identified in Haskell's note; manuscripts/publication were not independently consulted."),
    ("cand-10253", "Opere, volumes X and XII (citation locator for p.348 note 3)", "archive", 173,
     "Short publication locator as printed. Keep distinct from p.348 note 1 locator until bibliography review."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES if source_line >= 169 else BODY}#L{source_line}",
    })
    candidate_by_id[cid] = candidates[-1]

segment_bounds = {BODY: (14, 21), NOTES: (168, 220)}
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
    for number in line_numbers:
        line = source_lines[number - 1]
        search_from = 0
        while True:
            pos = line.find(surface, search_from)
            if pos < 0:
                break
            start = segment_offsets[(segment_id, number)] + pos
            end = start + len(surface)
            if not any(seg == segment_id and cid == candidate_id and s <= start and end <= e
                       for seg, cid, s, e in occupied_same_candidate):
                mention_id = f"m-chp14-p348-{mention_counter:04d}"
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


def add_pronouns(segment_id, candidate_id, forms, line_numbers, note="Coreference resolved from the immediate passage context."):
    import re
    global mention_counter
    for number in line_numbers:
        line = source_lines[number - 1]
        for form in forms:
            for match in re.finditer(rf"(?<![\w]){re.escape(form)}(?![\w])", line):
                start = segment_offsets[(segment_id, number)] + match.start()
                end = start + len(form)
                if any(seg == segment_id and cid == candidate_id and s <= start and end <= e
                       for seg, cid, s, e in occupied_same_candidate):
                    continue
                mention_id = f"m-chp14-p348-{mention_counter:04d}"
                if mention_id in mention_by_id:
                    raise SystemExit(f"mention ID already exists: {mention_id}")
                mentions.append({
                    "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                    "surface_form": form, "start_char": str(start), "end_char": str(end), "note": note,
                })
                mention_by_id[mention_id] = mentions[-1]
                occupied_same_candidate.add((segment_id, candidate_id, start, end))
                mention_counter += 1


# P.348 body mentions: use the page-specific index entries where available and retain unresolved objects locally.
for surface, cid, lines in [
    ("Bonomo", "cand-0040", [19]), ("Francesco’s", "cand-0061", [15]),
    ("Italy", "cand-3461", [15]), ("Bologna", "cand-3398", [16, 18]),
    ("Algarotti", "cand-0061", [16]), ("Veneto", "cand-4207", [16]),
    ("Venice", "cand-2719", [16]), ("Venetian", "cand-2719", [16]),
    ("Bolognese", "cand-3398", [16]), ("Padua", "cand-1803", [16]),
    ("Vicenza", "cand-2769", [16, 17]), ("Verona", "cand-7661", [16]),
    ("Veronese", "cand-2755", [16]), ("Guido Reni", "cand-2124", [16]),
    ("Palladio", "cand-1807", [16, 17]), ("neo-classicism", "cand-6439", [16]),
    ("Prussia", "cand-10246", [17]), ("Florence", "cand-3397", [17]),
    ("Cellini’s", "cand-0621", [17]), ("Perseus", "cand-10240", [17]),
    ("the doors of the Baptistery", "cand-10241", [17]),
    ("Raphael’s", "cand-2105", [18]), ("St John the Baptist", "cand-10242", [18]),
    ("S. Cecilia", "cand-10243", [18]), ("the Titians", "cand-10244", [18]),
    ("Grand Ducal collections", "cand-10245", [18]),
    ("Fra Bartolommeo", "cand-0252", [18]), ("Rome", "cand-4490", [19, 20, 21]),
    ("Francesco Zanotti", "cand-2864", [19]), ("St Peter’s", "cand-6960", [20]),
    ("Pantheon", "cand-4236", [20]), ("Baroque", "cand-4500", [20, 21]),
    ("Carracci", "cand-0576", [20]), ("Galleria Farnese", "cand-5423", [20]),
    ("Domenichino", "cand-0932", [20]), ("Monti", "cand-1698", [20]),
    ("Torelli", "cand-2645", [20]), ("Bernini", "cand-0295", [20]),
    ("Borromini", "cand-0404", [20]), ("Fulvio Testi", "cand-2560", [20]),
    ("Marino", "cand-1548", [20, 21]), ("Giovanni Bottari", "cand-0417", [21]),
    ("Winckelmann", "cand-2816", [21]), ("Mengs", "cand-1652", [21]),
    ("scholars and antiquarians in Rome", "cand-10247", [21]),
]:
    add_surface(BODY, cid, surface, lines)
add_surface(BODY, "cand-0040", "who", [15], note="Relative pronoun continuing the p.347 clause whose antecedent is Bonomo.")
add_surface(BODY, "cand-0040", "his brother", [19], note="Algarotti's brother Bonomo; immediate family context.")
add_pronouns(BODY, "cand-0061", ["him"], [15])
add_pronouns(BODY, "cand-0061", ["He", "he", "his"], [16, 18])
add_pronouns(BODY, "cand-0050", ["he", "His"], [17])
add_pronouns(BODY, "cand-0068", ["he", "his", "He"], [19, 20, 21])
add_pronouns(BODY, "cand-0417", ["whom"], [21], note="Relative pronoun refers to Giovanni Bottari.")

# Printed notes 1-3 on physical p.2.
for surface, cid, lines in [
    ("F. M. Zanotti", "cand-2864", [171]), ("Opere, XI and XII", "cand-10249", [171]),
    ("Letter of 22 February 1734", "cand-10250", [172]), ("Bonomo", "cand-0040", [172]),
    ("Treviso, Archivio Comunale, MSS. 1256", "cand-10251", [172]),
    ("F. M.", "cand-2864", [173]), ("Eustachio Zanotti", "cand-2863", [173]),
    ("Antonio Conti", "cand-0826", [173]), ("Rome", "cand-4490", [173]),
    ("Opere, X and XII", "cand-10253", [173]),
]:
    add_surface(NOTES, cid, surface, lines)
add_surface(NOTES, "cand-10248", "letters to F. M. Zanotti between 1732 and 1734", [171])
add_surface(NOTES, "cand-10252", "letters to F. M. and Eustachio Zanotti and Antonio Conti from Rome between February and June 1734", [173])
add_pronouns(NOTES, "cand-0061", ["his"], [171], note="In note 1, 'his letters' refers to Francesco Algarotti.")
add_pronouns(NOTES, "cand-0068", ["his"], [172], note="In note 2, 'his brother' refers to Francesco Algarotti.")


def quote(start, end, exact):
    allowed = "\n".join(source_lines[start - 1:end])
    if exact not in allowed:
        raise SystemExit(f"statement quotation is not present in L{start}-L{end}: {exact[:90]!r}")
    return exact


def q(start, end, claim, layer, qualification, candidate_ids, **extra):
    out = {
        "source_line_start": start, "source_line_end": end, "printed_page": 348,
        "pdf_physical_page": 2, "claim": claim, "speaker": "Haskell",
        "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    out.update(extra)
    return out


def add_statement(statement_id, segment_id, subject, obj, predicate, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    start, end = qualifiers["source_line_start"], qualifiers["source_line_end"]
    bounds = (14, 21) if segment_id == BODY else (168, 220)
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


link1 = {"footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L171",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p348-note1-letters"]}
link2 = {"footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L172",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p348-note2-letter"]}
link3 = {"footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L173",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p348-note3-letters"]}

add_statement("st-chp14-p348-bonomo-plans-and-gossip", BODY, "cand-0040", "cand-0061", "supported_plans_and_informed",
    q(15, 15, "Bonomo helped put Francesco's ambitious plans into practice and kept him informed of social and artistic gossip in Italy.",
      "biographical narrative", "The grammatical subject is supplied by the p.347 clause ending 'it was Bonomo'; the continuation is quoted only from this segment.",
      ["cand-0040", "cand-0061", "cand-3461"], relation_candidate=True,
      ocr_corrections=[{"source_line": 15, "ocr": "helped, to", "print": "helped to", "basis": "CHP-14.pdf physical page 2."}],
      cross_reference_segments=[P347], cross_reference_text="it was Bonomo"),
    quote(15, 15, "who helped, to put into practice most of Francesco’s ambitious plans and who in turn kept him regularly informed of the social and artistic gossip of Italy."))
add_statement("st-chp14-p348-return-to-veneto", BODY, "cand-0061", None, "travel_and_return",
    q(16, 16, "After leaving Bologna, Algarotti returned to the Veneto briefly and travelled between Venice, Padua, Vicenza, and Verona; Haskell locates the first evidence of his artistic interest in this period.",
      "biographical narrative", "The passage gives a brief itinerary but no exact dates or duration beyond 'a short time'.",
      ["cand-0061", "cand-3398", "cand-4207", "cand-2719", "cand-1803", "cand-2769", "cand-7661"]),
    quote(16, 16, "After leaving Bologna Algarotti returned to the Veneto for a short time. He travelled between Venice, Padua, Vicenza and Verona, and it is now that we first hear of his interest in the arts."))
add_statement("st-chp14-p348-early-taste", BODY, "cand-0061", None, "artistic_taste_characterization",
    q(16, 16, "Haskell calls Algarotti's expressed taste conventional among cultivated dilettantes, linking praise of Veronese and Guido Reni to his Venetian and Bolognese upbringing and his enthusiasm for Palladio to early neo-classicism in the Veneto.",
      "authorial interpretation", "Comparative stylistic assessment by Haskell, not an independently verified statement about all dilettantes.",
      ["cand-0061", "cand-2755", "cand-2124", "cand-1807", "cand-2719", "cand-3398", "cand-6439", "cand-4207"],
      ocr_corrections=[{"source_line": 16, "ocr": "passionate, enthusiasm", "print": "passionate enthusiasm", "basis": "CHP-14.pdf physical page 2."}]),
    quote(16, 16, "The taste he expresses is conventional enough, and in no way differs from that of the majority of cultivated dilettantes of the day. Admiration for Veronese and Guido Reni—the two painters he specially singles out for praise—was the natural result of his Venetian and Bolognese upbringing; while his passionate, enthusiasm for the works of Palladio was characteristic of the early stages of neo-classicism in the Veneto:"))
add_statement("st-chp14-p348-palladio-quote-and-prussia", BODY, "cand-0061", "cand-1807", "praised_and_promoted_architectural_cult",
    q(17, 17, "Algarotti wrote from Vicenza in August 1732 that he repeatedly admired Palladio's works; Haskell says his later career showed more than lip service and that he helped spread the architect's cult to Prussia.",
      "Haskell's report of a quoted letter and later career", "The quoted praise is attributed to Algarotti; the later interpretation and characterization are Haskell's. No specific work or recipient in Prussia is named.",
      ["cand-0061", "cand-1807", "cand-2769", "cand-10246"], relation_candidate=True,
      ocr_corrections=[
        {"source_line": 17, "ocr": "‘1 go", "print": "‘I go", "basis": "CHP-14.pdf physical page 2."},
        {"source_line": 17, "ocr": "Up service", "print": "lip service", "basis": "CHP-14.pdf physical page 2."},
        {"source_line": 17, "ocr": "Prussia.-Towards", "print": "Prussia. Towards", "basis": "CHP-14.pdf physical page 2."},
      ]),
    quote(17, 17, "‘1 go again and again to look at the divine works of Palladio without ever growing tired of them’, he wrote from Vicenza in August 1732. His later career was to show him paying far more than mere Up service to the divine Palladio, and he helped to spread the cult for the architect to Prussia."))
add_statement("st-chp14-p348-florence-visit", BODY, "cand-0061", "cand-3397", "travelled_and_viewed_art",
    q(17, 17, "Toward the end of 1733 Algarotti went to Florence for three months and admired Cellini's Perseus and the Baptistery doors.",
      "biographical narrative", "The doors are not identified by maker or version; the Perseus is named but no further version details are given.",
      ["cand-0061", "cand-3397", "cand-0621", "cand-10240", "cand-10241"]),
    quote(17, 17, "Towards the end of 1733 he went to Florence, where he stayed three months. He admired Cellini’s Perseus and the doors of the Baptistery;"))
add_statement("st-chp14-p348-raphael-titian-bartolommeo", BODY, "cand-0061", None, "artistic_response_and_first_encounter",
    q(18, 18, "Haskell reports that Algarotti found Raphael's St John the Baptist disappointing after S. Cecilia in Bologna, was excited by Titian paintings in the Grand Ducal collections, and was overwhelmed by Fra Bartolommeo, whom he had just heard of for the first time.",
      "biographical narrative", "The Titian paintings are unnamed and plural; footnote 1 points to cited letters but does not independently verify these evaluations.",
      ["cand-0061", "cand-2105", "cand-10242", "cand-10243", "cand-10244", "cand-10245", "cand-0252"], **link1),
    quote(18, 18, "Raphael’s St John the Baptist disappointing after the S. Cecilia in Bologna; talked of the excitement of discovering the Titians in the Grand Ducal collections; and above all he was overwhelmed by the greatness of Fra Bartolommeo, of whom he now heard for the first time.1"))
add_statement("st-chp14-p348-move-to-rome", BODY, "cand-0068", None, "travel_and_correspondence_context",
    q(19, 20, "In February 1734 Algarotti moved to Rome and wrote to his brother Bonomo and to Francesco Zanotti about the city's impact.",
      "biographical narrative", "The letters are described but not independently consulted; note 2 identifies one cited letter to Bonomo.",
      ["cand-0068", "cand-4490", "cand-0040", "cand-2864"]),
    quote(19, 20, "In February 1734 he moved on to Rome. In letters to his brother and to Francesco\nZanotti he describes the impact of the city."))
add_statement("st-chp14-p348-ruins-and-pantheon", BODY, "cand-0068", None, "architectural_judgement",
    q(20, 20, "In a quoted letter Algarotti says Rome's ruins surpass any modern building in perfect condition and compares St Peter's unfavourably with the Pantheon.",
      "Haskell's report of a quoted letter", "The comparison is attributed to Algarotti in a letter; the letter is cited by footnote 2 but was not independently consulted.",
      ["cand-0068", "cand-4490", "cand-6960", "cand-4236"], relation_candidate=False, **link2),
    quote(20, 20, "‘These magnificent ruins’, he writes,2 ‘are more beautiful than any modern building in perfect condition,’ and in his dogmatic reverence for antiquity he compares St Peter’s unfavourably with the Pantheon."))
add_statement("st-chp14-p348-revolt-against-baroque", BODY, "cand-0068", None, "authorial_contextualization",
    q(20, 20, "Algarotti claims that his reverence for antiquity runs against current taste, while Haskell says revolt against the Baroque was already underway and characterizes Algarotti as no great rebel.",
      "Haskell's contextualization of Algarotti's reported claim", "Separates Algarotti's self-positioning from Haskell's correction and qualification.",
      ["cand-0068", "cand-4500"]),
    quote(20, 20, "He claims that in taking up this attitude he is running against current taste, but in fact the revolt against the Baroque was already well under way when he arrived in Rome and in any case Algarotti was never to be much of a rebel."))
add_statement("st-chp14-p348-judgement-shaken", BODY, "cand-0068", None, "changed_artistic_judgement",
    q(20, 20, "Haskell says Algarotti's judgement of paintings was severely shaken by what he saw in Rome.",
      "authorial summary of Algarotti's reported judgement", "The sentence is attributed to Algarotti by Haskell; footnote 3 points to cited letters, not independently consulted.",
      ["cand-0068", "cand-4490"], **link3),
    quote(20, 20, "More interesting is his judgement on pictures which, he says, has been severely shaken by what he has seen.3"))
add_statement("st-chp14-p348-carracci-domenichino", BODY, "cand-0068", None, "changed_estimation_of_painters",
    q(20, 20, "Haskell says Carracci, especially in the Galleria Farnese, and Domenichino displaced Monti and Torelli in Algarotti's esteem.",
      "authorial summary of Algarotti's reported judgement", "The named painters and gallery are retained; no specific individual paintings are identified.",
      ["cand-0068", "cand-0576", "cand-5423", "cand-0932", "cand-1698", "cand-2645"]),
    quote(20, 20, "Carracci, especially in the Galleria Farnese, and Domenichino have totally replaced in his esteem such Bolognese masters of the late Baroque as Monti or Torelli."))
add_statement("st-chp14-p348-baroque-equivalence", BODY, "cand-0068", None, "art_and_literature_comparison",
    q(20, 21, "Haskell notes that Algarotti equates Baroque art and literature by pairing Bernini and Borromini with Fulvio Testi and Marino, a comparison that later became commonplace in criticism.",
      "authorial interpretation", "The passage reports an analogy and Haskell's claim about its later critical currency; it does not establish direct influence.",
      ["cand-0068", "cand-4500", "cand-0295", "cand-0404", "cand-2560", "cand-1548"]),
    quote(20, 21, "It is notable too that he equates Baroque art and literature—Bernini and Borromini with Fulvio Testi and\nMarino—in a way that was later to become a commonplace of criticism."))
add_statement("st-chp14-p348-bottari-correspondence", BODY, "cand-0068", "cand-0417", "corresponded_with",
    q(21, 21, "Soon after arriving in Rome Algarotti met Giovanni Bottari and began a lifelong correspondence with him.",
      "biographical narrative", "The passage states a lifelong correspondence; the letters themselves are not identified or consulted here.",
      ["cand-0068", "cand-4490", "cand-0417"], relation_candidate=True),
    quote(21, 21, "Very soon after his arrival he met Giovanni Bottari, with whom he began a lifelong correspondence."))
add_statement("st-chp14-p348-roman-scholars", BODY, "cand-0417", "cand-10247", "member_of_scholarly_group",
    q(21, 21, "Haskell describes Bottari as part of a Roman group of scholars and antiquarians who opposed contemporary art on theoretical grounds and prepared the way for neo-classicism before Winckelmann and Mengs.",
      "authorial historical interpretation", "The group is unnamed and not identified as a formal institution; Haskell gives a broad generational chronology.",
      ["cand-0417", "cand-10247", "cand-4490", "cand-6439", "cand-2816", "cand-1652"]),
    quote(21, 21, "Bottari was one of a group of scholars and antiquarians in Rome who disapproved of contemporary art on theoretical grounds and who, for a full generation before Winckelmann and Mengs, were preparing the way for neo-classicism."))
add_statement("st-chp14-p348-first-approach-to-painting", BODY, "cand-0068", None, "intellectual_network_and_artistic_approach",
    q(21, 21, "Haskell says Algarotti's first approach to painting came through scholars, often pedantic, rather than artists and collectors, who later broadened his views.",
      "authorial interpretation", "This is Haskell's interpretation of an intellectual pathway, not an exhaustive account of all contacts.",
      ["cand-0068", "cand-0417", "cand-10247"],
      ocr_corrections=[{"source_line": 21, "ocr": "artists.and collectors", "print": "artists and collectors", "basis": "CHP-14.pdf physical page 2."}]),
    quote(21, 21, "This then was Algarotti’s first approach to painting. It was made through scholars, often guilty of the greatest pedantry, rather than through artists.and collectors, who were later to liberalise his views."))
add_statement("st-chp14-p348-limited-artist-contact", BODY, "cand-0068", None, "artist_contact_assessment",
    q(21, 21, "Haskell says that on Algarotti's only visit to Rome, at age 22, he appears to have had little if any contact with living artists.",
      "authorial assessment", "Haskell qualifies the claim with 'appears' and 'little if any'; the next sentence begins at the end of this source segment and continues on p.349.",
      ["cand-0068", "cand-4490"]),
    quote(21, 21, "On this, his only visit to Rome, made at the age of 22, Algarotti appears in fact to have had little if any contact with living artists."))

# Note text is connected to printed markers but remains Haskell's citation trail, not independent evidence.
add_statement("st-chp14-p348-note1-letters", NOTES, None, None, "bibliographic_note",
    q(171, 171, "Note 1 directs readers to Algarotti's letters to F. M. Zanotti from 1732-1734 in Opere volumes XI and XII.",
      "authorial bibliographic note", "The cited volumes and letters were not independently consulted.",
      ["cand-0061", "cand-2864", "cand-10248", "cand-10249"]),
    quote(171, 171, source_lines[170]))
add_statement("st-chp14-p348-note2-letter", NOTES, None, None, "bibliographic_note",
    q(172, 172, "Note 2 cites a letter dated 22 February 1734 to Bonomo in Treviso, Archivio Comunale, MSS.1256.",
      "authorial bibliographic note", "The letter and repository record were not independently consulted; do not merge the repository with Biblioteca Comunale, Treviso without review.",
      ["cand-0040", "cand-10250", "cand-10251"]),
    quote(172, 172, source_lines[171]))
add_statement("st-chp14-p348-note3-letters", NOTES, None, None, "bibliographic_note",
    q(173, 173, "Note 3 cites Algarotti letters to F. M. and Eustachio Zanotti and Antonio Conti from Rome between February and June 1734, published in Opere volumes X and XII.",
      "authorial bibliographic note", "The letters and cited volumes were not independently consulted.",
      ["cand-0068", "cand-2864", "cand-2863", "cand-0826", "cand-4490", "cand-10252", "cand-10253"]),
    quote(173, 173, source_lines[172]))

# The p.347 sentence is now closed by p.348 L15. P.348 L21 ends mid-sentence ('less than'),
# and the consolidated notes segment continues after p.348.
coverage_by_id[P347].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-12",
    "note": "Printed p.347 opening page read against CHP-14.pdf physical p.1. The trailing body clause at L11 is closed by p.348 L15 and linked to st-chp14-p348-bonomo-plans-and-gossip; L12 is note 1's continuation linked to L169. Print corrections are in statement qualifiers; S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L14-21",
    "note": "Printed p.348 read against CHP-14.pdf physical p.2. Closes the p.347 Bonomo clause at L15. The final sentence ends at 'He remained less than' and continues in p.349 segment l23-33; leave partial until closed. S0 unchanged; print corrections are in statement qualifiers.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-173",
    "note": "Printed p.347 notes 1-2 and p.348 notes 1-3 read and linked to their body markers. P.347 note 1 continuation at body L12 is cross-linked. Notes for later printed pages remain pending.",
})

# Preflight foreign keys and exact character anchors for this batch.
known_ids = set(candidate_by_id)
for row in mentions:
    if row["mention_id"].startswith("m-chp14-p348-"):
        seg = row["segment_id"]
        bounds = segment_bounds[seg]
        text = "\n".join(source_lines[bounds[0] - 1:bounds[1]])
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']}")
        if row["candidate_id"] not in known_ids:
            raise SystemExit(f"mention candidate missing: {row['mention_id']}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p348-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in known_ids:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")

new_mentions = [r for r in mentions if r["mention_id"].startswith("m-chp14-p348-")]
new_statements = [r for r in statements if r["statement_id"].startswith("st-chp14-p348-")]
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "new_candidates": len(new_candidates), "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage_updates": {P347: coverage_by_id[P347], BODY: coverage_by_id[BODY], NOTES: coverage_by_id[NOTES]},
}, ensure_ascii=False, indent=2))

if args.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
