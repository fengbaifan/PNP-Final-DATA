"""Controlled S2 migration for printed p.347 body and notes 1-2; dry-run by default."""
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
BODY = "chp-14:14_CHP-14_intro:l3-12"
TITLE = "chp-14:14_CHP-14_intro:l1-1"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
BACKUP_SUFFIX = ".bak-s2-chp14-p347-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.347 S2 migration")
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
required_lines = {
    1: "# 14 CHP-14 intro",
    6: "T has always been acknowledged that among the Venetian art patrons of the",
    7: "Ieighteenth century Francesco Algarotti holds a leading position:",
    9: "Francesco Algarotti (Plate 486) was born in Venice in 1712",
    10: "Bonomo, himself a man of great taste",
    11: "Bonomo that Francesco wrote from half the great courts of Europe",
    12: "80-99. Other references are noticed as they occur.",
    169: "1 The literature on Algarotti is vast.",
    170: "2 For the Bologna of this period and Algarotti’s relationships there",
}
for line_number, required in required_lines.items():
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

for segment_id in (TITLE, BODY, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if coverage_by_id[TITLE]["disposition"] != "queued":
    raise SystemExit("p.347 title disposition changed; refusing to overwrite")
if coverage_by_id[BODY]["disposition"] != "queued":
    raise SystemExit("p.347 body segment disposition changed; refusing to overwrite")
if coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("combined notes segment disposition changed; refusing to overwrite")

# The source-derived objects retain local identity boundaries for the later global S3 pass.
new_candidates = [
    ("cand-10222", "Dresden royal gallery (Algarotti's 1742 scheme)", "institution", 7,
     "The royal art gallery being formed at Dresden for Augustus; keep distinct from the previously indexed Dresden Gallery candidate cand-9091 pending S3."),
    ("cand-10223", "Francesco Algarotti's own collection of paintings (p.347 comparison)", "", 7,
     "Haskell distinguishes this collection from the later-mentioned joint collection with Bonomo. The current taxonomy has no personal-collection type; do not merge the two."),
    ("cand-10224", "Francesco Algarotti and Bonomo's joint picture collection", "", 11,
     "The source says Bonomo bought many pictures that made up their joint collection. Collection identity/type is left unresolved; distinct from Francesco's own collection mentioned earlier on p.347."),
    ("cand-10225", "Francesco Algarotti's unnamed father (described as a rich merchant)", "person", 9,
     "Unnamed person. The immediate sequence identifies the rich merchant as the father, but supplies no personal name or further identity."),
    ("cand-10226", "The Zanotti brothers (collective reference in p.347)", "", 9,
     "Collective wording retained as printed. Do not assign the occurrence to Eustachio or F. M. Zanotti individually; p.348 notes name both in another correspondence context."),
    ("cand-10227", "Michelessi (surname-only author cited in p.347 note 1)", "person", 169,
     "Surname only; the cited Memorie and the author's identity have not been independently checked."),
    ("cand-10228", "Michelessi's Memorie (short title cited in p.347 note 1)", "archive", 169,
     "Short title only. Haskell says it appeared six years after Algarotti's death; publication details and text were not independently consulted."),
    ("cand-10229", "Seventeen-volume edition of Algarotti's works (Venice, Carlo Palese; first volume, 1791)", "archive", 169,
     "Descriptive bibliographic candidate based on Haskell's note. No formal title is supplied in this note; do not assume identity with other Opere citations before S3/bibliography review."),
    ("cand-10230", "Short Latin life of Francesco Algarotti dedicated to Bonomo (Farsetti)", "archive", 169,
     "Haskell calls it short and rare; full title, edition, and text were not supplied or independently consulted."),
    ("cand-10231", "Ida Treat (author cited for a modern life of Algarotti)", "person", 169,
     "Name as cited; identity and cited biography are not independently checked here."),
    ("cand-10232", "Ida Treat's complete modern life of Francesco Algarotti (title unspecified)", "archive", 169,
     "Descriptive citation candidate; Haskell calls it the only complete modern life. Title, edition, and text not supplied or consulted."),
    ("cand-10233", "Annamaria Gabrielli (author cited in p.347 note 1)", "person", 169,
     "Full name as printed; do not merge automatically with other Gabrielli candidates pending S3."),
    ("cand-10234", "Annamaria Gabrielli, 1938, pp.155-169 (Algarotti aesthetics citation)", "archive", 169,
     "Exact short citation as printed; title, edition, and cited pages were not independently consulted."),
    ("cand-10235", "Annamaria Gabrielli, 1939, pp.24-31 (Algarotti aesthetics citation)", "archive", 169,
     "Exact short citation as printed; title, edition, and cited pages were not independently consulted."),
    ("cand-10236", "Aurelio Lepre (author cited in p.347 note 1)", "person", 169,
     "Full name as printed; article identity is not externally aligned."),
    ("cand-10237", "Aurelio Lepre, 1959, pp.80-99 (article title unspecified)", "archive", 169,
     "Citation spans note 1 line 169 and its continuation at source line 12. The full article title and cited text were not independently consulted."),
    ("cand-10238", "Bosdari (surname-only author cited in p.347 note 2)", "person", 170,
     "Surname only; identity is not determined from this citation."),
    ("cand-10239", "Bosdari, 1928, pp.157-222 (Algarotti's Bologna relationships citation)", "archive", 170,
     "Short citation only; title, edition, and text were not independently consulted."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    candidates.append({
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": suggested_type,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES if source_line >= 169 else BODY}#L{source_line}",
    })
    candidate_by_id[cid] = candidates[-1]

segment_bounds = {BODY: (3, 12), NOTES: (168, 220)}
segment_offsets = {}
for segment_id, (line_start, line_end) in segment_bounds.items():
    offset = 0
    for number in range(line_start, line_end + 1):
        segment_offsets[(segment_id, number)] = offset
        offset += len(source_lines[number - 1]) + (1 if number < line_end else 0)

occupied_same_candidate = set()
mention_counter = 1


def add_surface(segment_id, candidate_id, surface, line_numbers):
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
            key = (segment_id, candidate_id, start, end)
            # A full-name mention makes a nested surname mention of the same candidate redundant.
            if not any(seg == segment_id and cid == candidate_id and s <= start and end <= e
                       for seg, cid, s, e in occupied_same_candidate):
                mention_id = f"m-chp14-p347-{mention_counter:04d}"
                if mention_id in mention_by_id:
                    raise SystemExit(f"mention ID already exists: {mention_id}")
                mentions.append({
                    "mention_id": mention_id,
                    "segment_id": segment_id,
                    "candidate_id": candidate_id,
                    "surface_form": surface,
                    "start_char": str(start),
                    "end_char": str(end),
                    "note": "",
                })
                mention_by_id[mention_id] = mentions[-1]
                occupied_same_candidate.add(key)
                mention_counter += 1
            search_from = pos + 1


def add_pronouns(segment_id, candidate_id, forms, line_numbers, note="Coreference resolved from the immediate passage context."):
    global mention_counter
    import re
    for number in line_numbers:
        line = source_lines[number - 1]
        for form in forms:
            for match in re.finditer(rf"(?<![\w]){re.escape(form)}(?![\w])", line):
                start = segment_offsets[(segment_id, number)] + match.start()
                end = start + len(form)
                if any(seg == segment_id and cid == candidate_id and s <= start and end <= e
                       for seg, cid, s, e in occupied_same_candidate):
                    continue
                mention_id = f"m-chp14-p347-{mention_counter:04d}"
                if mention_id in mention_by_id:
                    raise SystemExit(f"mention ID already exists: {mention_id}")
                mentions.append({
                    "mention_id": mention_id,
                    "segment_id": segment_id,
                    "candidate_id": candidate_id,
                    "surface_form": form,
                    "start_char": str(start),
                    "end_char": str(end),
                    "note": note,
                })
                mention_by_id[mention_id] = mentions[-1]
                occupied_same_candidate.add((segment_id, candidate_id, start, end))
                mention_counter += 1


# Body entities, locations, and explicit coreference in printed p.347.
for surface, cid, lines in [
    ("Francesco Algarotti", "cand-0043", [7, 9]),
    ("Algarotti", "cand-0043", [7]),
    ("Consul Smith", "cand-2440", [7]),
    ("his own collection of paintings", "cand-10223", [7]),
    ("royal gallery at Dresden", "cand-10222", [7]),
    ("Dresden", "cand-0947", [7]),
    ("Tiepolo", "cand-2572", [7]),
    ("Canaletto", "cand-0499", [7]),
    ("Venetian", "cand-2719", [6, 7, 8]),
    ("Venice", "cand-2719", [8, 9]),
    ("Rome", "cand-4490", [9]),
    ("Bologna", "cand-3398", [9]),
    ("Europe", "cand-3462", [8, 11]),
    ("European", "cand-3462", [8]),
    ("Italy", "cand-3461", [11]),
    ("Plate 486", "cand-4034", [9]),
    ("Eustachio Manfredi", "cand-1511", [9]),
    ("Zanotti brothers", "cand-10226", [9]),
    ("a rich merchant", "cand-10225", [9]),
    ("his father", "cand-10225", [9]),
    ("his elder brother", "cand-0040", [9]),
    ("Bonomo", "cand-0040", [10, 11]),
    ("Francesco", "cand-0043", [10, 11]),
    ("their joint collection", "cand-10224", [11]),
]:
    add_surface(BODY, cid, surface, lines)
add_pronouns(BODY, "cand-0043", ["He", "he", "his", "His", "him"], [7, 8, 9])
add_pronouns(BODY, "cand-0040", ["himself", "whose"], [10])

# P.347 footnotes 1-2; citation locators stay source-specific until bibliography review.
for surface, cid, lines in [
    ("Michelessi", "cand-10227", [169]),
    ("Memorie", "cand-10228", [169]),
    ("first volume of the seventeen-volume edition of Algarotti’s works", "cand-10229", [169]),
    ("Carlo Palese", "cand-9798", [169]),
    ("Venice", "cand-2719", [169]),
    ("T. G. Farsetti", "cand-1013", [169]),
    ("Latin life", "cand-10230", [169]),
    ("Francesco’s", "cand-0043", [169]),
    ("Bonomo", "cand-0040", [169]),
    ("Ida Treat", "cand-10231", [169]),
    ("complete modern life", "cand-10232", [169]),
    ("Annamaria Gabrielli", "cand-10233", [169]),
    ("1938, pp. 155-69", "cand-10234", [169]),
    ("1939, pp. 24-31", "cand-10235", [169]),
    ("Aurelio Lepre", "cand-10236", [169]),
    ("1959, pp.", "cand-10237", [169]),
    ("80-99", "cand-10237", [12]),
    ("Bologna", "cand-3398", [170]),
    ("Algarotti’s", "cand-0043", [170]),
    ("Bosdari", "cand-10238", [170]),
    ("Bosdari, 1928, pp. 157-222", "cand-10239", [170]),
]:
    add_surface(NOTES if lines[0] >= 169 else BODY, cid, surface, lines)
add_pronouns(NOTES, "cand-0043", ["his"], [169], note="In footnote 1, 'his death' refers to Francesco Algarotti.")


def quote(start, end, exact):
    allowed = "\n".join(source_lines[start - 1:end])
    if exact not in allowed:
        raise SystemExit(f"statement quotation is not present in L{start}-L{end}: {exact[:90]!r}")
    return exact


def body_qualifiers(start, end, claim, layer, qualification, candidate_ids, **extra):
    q = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 347,
        "pdf_physical_page": 1,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    q.update(extra)
    return q


def add_statement(statement_id, segment_id, subject, obj, predicate, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    start = qualifiers["source_line_start"]
    end = qualifiers["source_line_end"]
    if segment_id == BODY and not (3 <= start <= end <= 12):
        raise SystemExit(f"statement span escapes body segment: {statement_id}")
    if segment_id == NOTES and not (168 <= start <= end <= 220):
        raise SystemExit(f"statement span escapes notes segment: {statement_id}")
    row = {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": original_quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


link_note1 = {
    "footnote_marker": "1",
    "footnote_segment": NOTES,
    "footnote_line_range": "L169; continuation L12 in the body segment",
    "footnote_text_pending": False,
    "footnote_body_link_status": "linked",
    "footnote_note_statement_ids": ["st-chp14-p347-note1-bibliography", "st-chp14-p347-note1-continuation"],
    "footnote_scope_note": "Bibliographic reading guidance; it is not a primary citation for the birth/merchant claim.",
}
link_note2 = {
    "footnote_marker": "2",
    "footnote_segment": NOTES,
    "footnote_line_range": "L170",
    "footnote_text_pending": False,
    "footnote_body_link_status": "linked",
    "footnote_note_statement_ids": ["st-chp14-p347-note2-bosdari"],
}

add_statement(
    "st-chp14-p347-leading-position", BODY, "cand-0043", None, "authorial_assessment",
    body_qualifiers(6, 7,
        "Haskell places Francesco Algarotti among the leading Venetian art patrons, attributing the standing chiefly to his articulated artistic taste and close contacts with leading painters; he contrasts these factors with a less striking personal picture collection and relatively few commissions for living artists for the Dresden royal gallery.",
        "authorial assessment", "Comparative evaluation by Haskell; the passage does not enumerate the commissioned works or define a numerical comparison.",
        ["cand-0043", "cand-10223", "cand-2440", "cand-10222", "cand-0947", "cand-2572", "cand-0499"],
        relation_candidate=True,
        ocr_corrections=[
            {"source_line": 6, "ocr": "T has", "print": "It has", "basis": "CHP-14.pdf physical page 1."},
            {"source_line": 7, "ocr": "Ieighteenth", "print": "eighteenth", "basis": "CHP-14.pdf physical page 1."},
        ]),
    quote(6, 7, "T has always been acknowledged that among the Venetian art patrons of the\nIeighteenth century Francesco Algarotti holds a leading position: not so much for his own collection of paintings (which was never as striking as that of Consul Smith), or for those he commissioned for the royal gallery at Dresden (which were few in number as far as living artists were concerned); but chiefly for his clearly expressed artistic tastes and for his very close contacts with the leading painters of the day, especially the two greatest—Tiepolo and Canaletto."),
)
add_statement(
    "st-chp14-p347-patronage-tensions", BODY, "cand-0043", None, "patronage_identity_characterization",
    body_qualifiers(7, 8,
        "Haskell presents Algarotti as embodying tensions in Venetian art patronage: bourgeois yet close to princes and patricians, receptive to Enlightenment ideas yet connected to the old order, a Venetian patriot rarely present in Venice, and engaged with advanced European ideas.",
        "authorial characterization", "These are Haskell's interpretive social and intellectual characterizations, not separately evidenced status records.",
        ["cand-0043", "cand-2719", "cand-3462"]),
    quote(7, 8, "Moreover, Algarotti conveniently sums up all the confused tendencies in Venetian art patronage that have so far been recorded. He was a bourgeois, but the intimate friend of princes and patricians; he toyed with ‘enlightened’ theories, but was closely tied to the old order; he was a\nVenetian patriot of sorts, though rarely in Venice, and he was in touch with all the most advanced European ideas."),
)
add_statement(
    "st-chp14-p347-receptive-character", BODY, "cand-0043", None, "authorial_interpretation_of_intellectual_temperament",
    body_qualifiers(8, 8,
        "Haskell attributes Algarotti's difficulty choosing among opposing tendencies to weaknesses of reasoning and temperament, describes him as receptive to new European experiences, and says his artistic ideas and dates of contact with Venetian painters require study across stages of his life.",
        "authorial interpretation", "The psychological assessment and proposed research framing are Haskell's, not direct self-description by Algarotti.",
        ["cand-0043", "cand-3462", "cand-2719"]),
    quote(8, 8, "Above all the very weaknesses of his reasoning power and temperament made him unable to choose between the opposing tensions which he tried so hard to reconcile. His was an exceptionally receptive character, open to all the new experiences that were coming to the fore in Europe, and in evaluating his influence on the painters of the day it is therefore important to investigate what were his artistic ideas at various stages in his life, and also when exactly he came into contact with the painters of Venice."),
)
add_statement(
    "st-chp14-p347-birth", BODY, "cand-0043", "cand-2719", "born_in",
    body_qualifiers(9, 9,
        "Haskell states that Francesco Algarotti was born in Venice in 1712 and was the second son of a rich merchant.",
        "biographical narrative", "The father is unnamed. Footnote 1 supplies bibliographic reading guidance, not a direct evidentiary citation for these details.",
        ["cand-0043", "cand-2719", "cand-10225"],
        relation_candidate=True, **link_note1,
        ocr_corrections=[{"source_line": 9, "ocr": "Plate 486", "print": "Plate 48d", "basis": "CHP-14.pdf physical page 1."}]),
    quote(9, 9, "Francesco Algarotti (Plate 486) was born in Venice in 1712, the second son of a rich merchant."),
)
add_statement(
    "st-chp14-p347-education", BODY, "cand-0043", None, "education_and_study",
    body_qualifiers(9, 9,
        "Haskell says Algarotti studied for a year in Rome, then in Bologna from 1726 after his father's death, principally natural sciences and mathematics, interests he retained.",
        "biographical narrative", "No school or named teacher is identified in this passage; the father's identity remains unresolved.",
        ["cand-0043", "cand-4490", "cand-3398", "cand-10225"],
        relation_candidate=True,
        ocr_corrections=[{"source_line": 9, "ocr": "Use", "print": "life", "basis": "CHP-14.pdf physical page 1."}]),
    quote(9, 9, "He was educated for a year in Rome, and in 1726, after the death of his father, in Bologna, where he studied principally the natural sciences and mathematics, in which he was always to be interested."),
)
add_statement(
    "st-chp14-p347-bologna-contacts", BODY, "cand-0043", None, "correspondence_and_scholarly_contacts",
    body_qualifiers(9, 9,
        "Haskell says Algarotti maintained contact with Bologna's scholarly world and corresponded regularly with Eustachio Manfredi, the collectively named Zanotti brothers, and other student acquaintances.",
        "biographical narrative", "The collective Zanotti wording is not assigned to either brother individually; the cited letters and identities have not been independently checked.",
        ["cand-0043", "cand-3398", "cand-1511", "cand-10226"],
        relation_candidate=True, **link_note2),
    quote(9, 9, "He kept up the contacts he made with the scholarly world of Bologna until the end of his Use, and remained in constant correspondence with Eustachio Manfredi, the Zanotti brothers and others whom he met during his student days.2"),
)
add_statement(
    "st-chp14-p347-bonomo-kinship-and-influence", BODY, "cand-0040", "cand-0043", "elder_brother_of",
    body_qualifiers(9, 10,
        "Haskell identifies Bonomo as Francesco's elder brother, describes him as a man of great taste, and judges his influence on Francesco considerable but difficult to evaluate.",
        "authorial characterization", "The kinship is explicit; the assessment of influence is expressly difficult to evaluate.",
        ["cand-0040", "cand-0043"], relation_candidate=True),
    quote(9, 10, "His other strong attachment was with his elder brother\nBonomo, himself a man of great taste, whose influence on the more mercurial and spectacular Francesco was certainly considerable though difficult to evaluate."),
)
add_statement(
    "st-chp14-p347-francesco-wrote-to-bonomo", BODY, "cand-0043", "cand-0040", "corresponded_with",
    body_qualifiers(10, 11,
        "Haskell says Francesco wrote to Bonomo from many of Europe's great courts.",
        "biographical narrative", "The phrase 'half the great courts' is Haskell's broad characterization; the courts are not individually identified.",
        ["cand-0043", "cand-0040", "cand-3462"], relation_candidate=True),
    quote(10, 11, "It was to\nBonomo that Francesco wrote from half the great courts of Europe;"),
)
add_statement(
    "st-chp14-p347-bonomo-joint-collection", BODY, "cand-0040", "cand-10224", "acquired_for_joint_collection",
    body_qualifiers(11, 11,
        "Haskell says Bonomo bought many of the pictures that formed the joint collection of Bonomo and Francesco.",
        "biographical narrative", "The next clause begins 'it was Bonomo' but continues on p.348; that separate claim is not closed by this statement.",
        ["cand-0040", "cand-0043", "cand-10224"], relation_candidate=True),
    quote(11, 11, "it was Bonomo who bought many of the pictures that made up their joint collection;"),
)

add_statement(
    "st-chp14-p347-note1-bibliography", NOTES, None, None, "bibliographic_note",
    body_qualifiers(169, 169,
        "Haskell's note surveys cited Algarotti literature: Michelessi's Memorie and the Palese Venice edition, Farsetti's Latin life, Ida Treat's modern biography, Gabrielli's 1938/1939 studies, and Lepre's 1959 article.",
        "authorial bibliographic note", "These works are recorded as cited references only; none was independently consulted here. The final Lepre page range continues at source line 12.",
        ["cand-10227", "cand-10228", "cand-10229", "cand-9798", "cand-1013", "cand-10230", "cand-10231", "cand-10232", "cand-10233", "cand-10234", "cand-10235", "cand-10236", "cand-10237", "cand-0040", "cand-2719"]),
    quote(169, 169, source_lines[168]),
)
add_statement(
    "st-chp14-p347-note1-continuation", BODY, None, None, "bibliographic_note_continuation",
    body_qualifiers(12, 12,
        "The p.347 note 1 continuation completes Aurelio Lepre's cited page range as 80-99 and says further references are given as the chapter proceeds.",
        "authorial bibliographic note", "This OCR line belongs to note 1, not to the p.347 body paragraph; it is linked to note 1 at source line 169.",
        ["cand-10236", "cand-10237"],
        note_number="1", cross_reference_segments=[NOTES], cross_reference_statement_ids=["st-chp14-p347-note1-bibliography"]),
    quote(12, 12, source_lines[11]),
)
add_statement(
    "st-chp14-p347-note2-bosdari", NOTES, None, None, "bibliographic_note",
    body_qualifiers(170, 170,
        "Haskell directs readers to Bosdari 1928, pp.157-222, for the Bologna of Algarotti's period and his relationships there.",
        "authorial bibliographic note", "The citation's title, edition, and cited pages were not independently consulted.",
        ["cand-3398", "cand-0043", "cand-10238", "cand-10239"]),
    quote(170, 170, source_lines[169]),
)

# The title is generated metadata; the p.347 body has one open clause continued at p.348,
# and the consolidated chapter-note source proceeds beyond p.347.
coverage_by_id[TITLE].update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L1-1",
    "note": "Generated Markdown filename heading only; not printed book content and contains no claim or entity mention.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L3-12",
    "note": "Printed p.347 opening page semantically read against CHP-14.pdf physical p.1. L12 is the continuation of note 1, not body prose, and is linked to note segment L169. The final body clause ends with 'it was Bonomo' at L11 and continues in the p.348 segment; close it before marking complete. Print corrections are recorded in statement qualifiers; S0 remains unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L169-170",
    "note": "Printed p.347 notes 1-2 read against CHP-14.pdf physical p.1 and linked to body footnote markers. Note 1 continues at body-segment L12; notes beginning at L171 belong to later printed pages and remain pending.",
})

# Table-level preflight: all new references resolve and every span matches source text.
known_candidate_ids = set(candidate_by_id)
for row in mentions:
    if row["segment_id"] in (BODY, NOTES) and row["mention_id"].startswith("m-chp14-p347-"):
        text = "\n".join(source_lines[segment_bounds[row["segment_id"]][0] - 1:segment_bounds[row["segment_id"]][1]])
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']}")
        if row["candidate_id"] not in known_candidate_ids:
            raise SystemExit(f"mention candidate missing: {row['mention_id']}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p347-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in known_candidate_ids:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")

new_mentions = [row for row in mentions if row["mention_id"].startswith("m-chp14-p347-")]
new_statements = [row for row in statements if row["statement_id"].startswith("st-chp14-p347-")]
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage_updates": {TITLE: coverage_by_id[TITLE], BODY: coverage_by_id[BODY], NOTES: coverage_by_id[NOTES]},
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
