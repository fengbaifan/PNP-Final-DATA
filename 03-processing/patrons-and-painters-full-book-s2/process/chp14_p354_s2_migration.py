"""Controlled S2 migration for printed p.354 body and notes 1-5; dry-run by default."""
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
BODY_PREV = "chp-14:14_CHP-14_intro:l63-71"
BODY = "chp-14:14_CHP-14_intro:l73-83"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
BACKUP_SUFFIX = ".bak-s2-chp14-p354-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.354 S2 migration")
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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in {
    74: "Banquet of Cleopatra Algarotti laid great stress",
    75: "At about the same time as he ordered these pictures",
    76: "Algarotti commissioned a picture by Tiepolo for himself",
    77: "In this painting the artist shows",
    78: "between the ‘public’ and the ‘private’",
    79: "Newton’s discoveries in optics",
    80: "Giorgione and Titian",
    81: "Tiepolo’s influence on Algarotti",
    82: "Castiglione, Salvator Rosa",
    83: "constantly trying to reconcile this vision",
    186: "Knox, p. 16",
    187: "Levey in Burlington Migazine",
    188: "Algarotti’s ideas on the subject",
    189: "Rava, 1913, pp. 58-61",
    190: "In the Saggio sopra I’AccaJemia di Francia",
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
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if (coverage_by_id[BODY_PREV]["migration_status"] != "partial"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "partial"
        or coverage_by_id[NOTES]["source_line_ranges"] != "L169-185"):
    raise SystemExit("S2 coverage preconditions changed")

new_candidates = [
    ("cand-10299", "Saxony (regional place named in p.354)", "place", 76,
     "Geographic region named as the location of Algarotti’s important patrons; do not conflate it with the Electorate or an individual ruler."),
    ("cand-10300", "Francesco Algarotti’s drawings and etchings of Oriental heads (unnamed works, p.354)", "work", 81,
     "Haskell says Algarotti produced these works for his amusement under Tiepolo’s influence; no individual title, date, or location is given."),
    ("cand-10301", "Knox, p.16 (short-form citation locator in p.354 note 1)", "archive", 186,
     "The note supplies only surname and page; title, date, edition, and author identity remain unresolved."),
    ("cand-10302", "Levey, Burlington Magazine, 1960, pp.250–257 (citation locator in p.354 note 2)", "archive", 187,
     "Short citation as printed; article title and bibliography match are deferred. The cited article/pages were not independently consulted."),
    ("cand-10303", "Francesco Algarotti letter to Eustachio Zanotti, 13 May 1756 (Opere VIII, pp.48–52 locator)", "archive", 188,
     "Haskell’s note describes the letter’s statement about the recent emergence of the white-ground proposal; the letter was not independently consulted."),
    ("cand-10304", "Watson, 1955, p.214 (citation locator in p.354 note 3)", "archive", 188,
     "Short citation only; article title and match to existing Watson author candidates remain unresolved."),
    ("cand-10305", "Rava, 1913, pp.58–61 (citation locator in p.354 note 4)", "archive", 189,
     "Short citation only; title, author identity, and publication details remain unresolved."),
    ("cand-10306", "Saggio sopra l’Accademia di Francia che è in Roma (Opere III, p.296 locator)", "archive", 190,
     "Treatise cited for Algarotti’s later summary of Tiepolo; citation is reported in Haskell’s note and was not independently checked."),
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

segment_bounds = {BODY: (73, 83), NOTES: (168, 220)}
segment_offsets = {}
for segment_id, (line_start, line_end) in segment_bounds.items():
    offset = 0
    for number in range(line_start, line_end + 1):
        segment_offsets[(segment_id, number)] = offset
        offset += len(source_lines[number - 1]) + (1 if number < line_end else 0)
mention_counter = 1
planned_mentions = []


def add_mention(segment_id, candidate_id, surface, line_number, pos, note=""):
    global mention_counter
    start = segment_offsets[(segment_id, line_number)] + pos
    end = start + len(surface)
    mention_id = f"m-chp14-p354-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    row = {"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
           "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note}
    mentions.append(row)
    planned_mentions.append(row)
    mention_counter += 1


def add_surface(segment_id, candidate_id, surface, line_numbers, note=""):
    matched = False
    for number in line_numbers:
        line = source_lines[number - 1]
        search_from = 0
        while True:
            pos = line.find(surface, search_from)
            if pos < 0:
                break
            matched = True
            add_mention(segment_id, candidate_id, surface, number, pos, note)
            search_from = pos + 1
    if not matched:
        raise SystemExit(f"surface not found in requested lines: {segment_id} {surface!r} {line_numbers}")


def add_pronoun(segment_id, candidate_id, form, number, occurrence=0, note="Coreference resolved from the local passage context."):
    matches = list(re.finditer(rf"(?<![\w]){re.escape(form)}(?![\w])", source_lines[number - 1]))
    if occurrence >= len(matches):
        raise SystemExit(f"pronoun not found: L{number} {form!r} #{occurrence}")
    add_mention(segment_id, candidate_id, form, number, matches[occurrence].start(), note)


for surface, cid, lines in [
    ("Banquet of Cleopatra", "cand-4101", [74]),
    ("Algarotti", "cand-0052", [74, 75, 76, 78, 80, 81, 82, 83]),
    ("classicism", "cand-9266", [74]),
    ("Saxony", "cand-10299", [76]),
    ("Tiepolo", "cand-3781", [76, 81, 82]),
    ("Bath of Diana", "cand-2580", [76]),
    ("this painting", "cand-2580", [77]),
    ("the artist", "cand-3781", [77, 79, 81]),
    ("Boucher", "cand-0421", [77]),
    ("Paris", "cand-4653", [78]),
    ("classical", "cand-9266", [78, 81]),
    ("Newton", "cand-1739", [79]),
    ("Giorgione", "cand-1188", [80]),
    ("Titian", "cand-2630", [80]),
    ("drawings and etchings of oriental heads", "cand-10300", [81]),
    ("Raphael", "cand-2098", [81]),
    ("Poussin", "cand-1984", [81]),
    ("Paolo", "cand-2755", [81]),
    ("Castiglione", "cand-0602", [82]),
    ("Salvator Rosa", "cand-2236", [82]),
    ("neo-classical", "cand-6010", [83]),
    ("Knox", "cand-10301", [186]),
    ("Levey", "cand-10297", [187]),
    ("in Burlington Migazine, i960, pp. 250-7", "cand-10302", [187]),
    ("Saggio sopra la Pittura", "cand-0074", [188]),
    ("Eustachio Zanotti", "cand-2863", [188]),
    ("13 May 1756", "cand-10303", [188]),
    ("Watson", "cand-9353", [188]),
    ("1955, p. 214", "cand-10304", [188]),
    ("Rava, 1913, pp. 58-61", "cand-10305", [189]),
    ("Saggio sopra I’AccaJemia di Francia che è in Roma", "cand-10306", [190]),
]:
    add_surface(BODY if lines[0] < 168 else NOTES, cid, surface, lines)

for cid, form, number, occurrence in [
    ("cand-0052", "he", 75, 0), ("cand-0052", "his", 75, 0),
    ("cand-3781", "his", 78, 0), ("cand-0052", "his", 78, 1),
    ("cand-0052", "his", 79, 0), ("cand-0052", "He", 79, 0),
    ("cand-0052", "he", 79, 0), ("cand-0052", "he", 79, 1), ("cand-0052", "he", 79, 2),
    ("cand-0067", "them", 79, 0), ("cand-3781", "his", 79, 1),
    ("cand-0052", "he", 81, 0), ("cand-0052", "he", 81, 1), ("cand-0052", "he", 81, 2),
    ("cand-2580", "it", 77, 0), ("cand-2580", "it", 78, 0),
    ("cand-0052", "his", 81, 0), ("cand-0052", "his", 81, 1),
    ("cand-0052", "his", 81, 2), ("cand-0052", "his", 81, 3),
    ("cand-3781", "his", 81, 4), ("cand-3781", "his", 81, 5),
    ("cand-2573", "this", 81, 1),
    ("cand-3781", "this", 83, 0),
]:
    add_pronoun(BODY, cid, form, number, occurrence)


def quote(start, end, exact):
    allowed = "\n".join(source_lines[start - 1:end])
    if exact not in allowed:
        raise SystemExit(f"statement quotation is not present in L{start}-L{end}: {exact[:100]!r}")
    return exact


def q(start, end, claim, layer, qualification, candidate_ids, **extra):
    out = {
        "source_line_start": start, "source_line_end": end, "printed_page": 354,
        "pdf_physical_page": 8, "claim": claim, "speaker": "Haskell",
        "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    out.update(extra)
    return out


def add_statement(statement_id, segment_id, subject, obj, predicate, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    start, end = qualifiers["source_line_start"], qualifiers["source_line_end"]
    bounds = (73, 83) if segment_id == BODY else (168, 220)
    if not (bounds[0] <= start <= end <= bounds[1]):
        raise SystemExit(f"statement span escapes segment: {statement_id}")
    row = {"statement_id": statement_id, "segment_id": segment_id,
           "subject_candidate_id": subject, "object_candidate_id": obj,
           "predicate": predicate, "qualifiers": qualifiers,
           "original_quote": original_quote, "origin": "book", "source_file": SOURCE_FILE}
    statements.append(row)
    statement_by_id[statement_id] = row


def add_note_statement(statement_id, qualifiers, original_quote):
    add_statement(statement_id, NOTES, None, None, "bibliographic_note", qualifiers, original_quote)


note_links = {
    "1": ["st-chp14-p354-note1-knox-locator"],
    "2": ["st-chp14-p354-note2-levey-locator"],
    "3": ["st-chp14-p354-note3-color-theory-sources", "st-chp14-p354-note3-white-ground-proposal"],
    "4": ["st-chp14-p354-note4-rava-locator"],
    "5": ["st-chp14-p354-note5-saggio-locator"],
}

add_statement("st-chp14-p354-banquet-classicism-and-accuracy", BODY, "cand-0052", "cand-4101",
    "stressed_classicism_and_accuracy_in_banquet_scenes",
    q(74, 74, "Continuing p.353’s comparison, Haskell says Algarotti stressed classicism and accuracy in the Banquet of Cleopatra scenes and carefully chose antique sculpture and correct uniforms.",
      "authorial report of artistic priorities", "This completes p.353 L71 ‘As in The’; the preference is attributed to Algarotti by Haskell.",
      ["cand-0052", "cand-4101", "cand-9266"], cross_reference_segments=[BODY_PREV],
      cross_reference_text="completes the p.353 L71 phrase ‘As in The’", footnote_marker="1",
      footnote_segment=NOTES, footnote_line_range="L186", footnote_text_pending=False,
      footnote_body_link_status="linked", footnote_note_statement_ids=note_links["1"]),
    quote(74, 74, "Banquet of Cleopatra Algarotti laid great stress on the classicism and accuracy of the two scenes, going to particular trouble in his choice of antique sculpture and correct uniforms.1"))

add_statement("st-chp14-p354-bruhl-pictures-for-patrons-in-saxony", BODY, "cand-0052", "cand-10299",
    "ordered_preceding_pictures_for_important_patrons_in_saxony",
    q(75, 76, "Haskell identifies the two preceding pictures as orders for Algarotti’s important patrons in Saxony.",
      "authorial report", "‘These pictures’ links to the two distinct p.353 Maecenas and Flora commissions; the phrase does not identify which patron received which work.",
      ["cand-0052", "cand-2597", "cand-2590", "cand-0458", "cand-0149", "cand-10299"],
      cross_reference_segments=["chp-14:14_CHP-14_intro:l63-71"],
      cross_reference_text="the two p.353 works commissioned for Brühl; no one-to-one recipient mapping is added",
      candidate_identity_questions=[{"candidate_id": "cand-10256", "issue": "P.354 names Saxony as the patrons’ location; keep the geographic place separate from the Electorate institution candidate, which is not acting in this sentence."}]),
    quote(75, 76, "At about the same time as he ordered these pictures for his important patrons in\nSaxony"))

add_statement("st-chp14-p354-bath-of-diana-commissioned-for-algarotti", BODY, "cand-0052", "cand-2580",
    "commissioned_picture_for_himself",
    q(76, 76, "Algarotti commissioned a Tiepolo picture for himself, identified as the Bath of Diana.",
      "authorial report", "The S1 index candidate supplies the subject-based work label; no version, date, or present location is stated.",
      ["cand-0052", "cand-3781", "cand-2580"], relation_candidate=True,
      cross_reference_segments=["chp-14:14_CHP-14_intro:l63-71"],
      cross_reference_text="contrasts the private Bath of Diana commission with the preceding works for Saxon patrons",
      footnote_marker="2", footnote_segment=NOTES, footnote_line_range="L187",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=note_links["2"]),
    quote(76, 76, "Saxony, Algarotti commissioned a picture by Tiepolo for himself—the Bath of Diana.2"))

add_statement("st-chp14-p354-bath-of-diana-tiepolo-attribution", BODY, "cand-2580", "cand-3781",
    "attributed_to_tiepolo_in_haskell_narrative",
    q(76, 76, "Haskell identifies Tiepolo as the painter of the Bath of Diana.",
      "authorial report", "This records Haskell’s attribution only; no external attribution verification is claimed.",
      ["cand-2580", "cand-3781"], relation_candidate=True),
    quote(76, 76, "a picture by Tiepolo for himself—the Bath of Diana"))

add_statement("st-chp14-p354-bath-of-diana-boucher-style", BODY, "cand-2580", "cand-0421",
    "described_as_relaxed_sensual_scene_in_boucher_fashion",
    q(77, 78, "Haskell describes the Bath of Diana as a relaxed, sensual scene of naked nymphs in a style Boucher had made fashionable in Paris.",
      "authorial visual and stylistic description", "This is Haskell’s stylistic comparison, not a claim that Boucher designed or influenced the specific picture.",
      ["cand-2580", "cand-0421", "cand-4653"]),
    quote(77, 78, "In this painting the artist shows altogether different preoccupations: it is a relaxed, sensual scene of naked nymphs in the style which Boucher had made fashionable in\nParis"))

add_statement("st-chp14-p354-bath-of-diana-reflects-algarotti-tastes", BODY, "cand-2580", "cand-0052",
    "interpreted_as_reflecting_eclectic_cosmopolitan_tastes",
    q(78, 78, "Haskell says the picture is exceptional among Tiepolo’s works and clearly reflects Algarotti’s eclectic, cosmopolitan tastes, which moved between public and private interests.",
      "authorial interpretation", "The characterization is Haskell’s reading of the work and of period taste.",
      ["cand-2580", "cand-3781", "cand-0052"]),
    quote(78, 78, "and it is quite exceptional among his works, clearly reflecting Algarotti’s eclectic, cosmopolitan tastes, which like those of so many people at the time veered widely between the ‘public’ and the ‘private’."))

add_statement("st-chp14-p354-algarotti-classical-bias", BODY, "cand-0052", "cand-9266",
    "described_as_having_clear_classical_bias",
    q(78, 78, "Haskell says Algarotti’s classical bias is generally clear.",
      "authorial assessment", "This is an attributed characterization, not a measured stylistic classification.",
      ["cand-0052", "cand-9266"]),
    quote(78, 78, "In general, however, his classical bias is clear:"))

add_statement("st-chp14-p354-colour-influence-difficult-to-assess", BODY, "cand-0052", None,
    "influence_of_algarotti_views_on_colour_difficult_to_assess",
    q(79, 79, "Haskell says the influence of Algarotti’s views on colour is more difficult to assess.",
      "authorial assessment", "Haskell distinguishes the clear classical bias from the less certain influence on colour.",
      ["cand-0052", "cand-0067"]),
    quote(79, 79, "it is more difficult to assess the influence of his views on colour."))

add_statement("st-chp14-p354-algarotti-advocated-study-of-newton-optics", BODY, "cand-0052", "cand-0067",
    "advocated_study_of_newton_optics_by_artists",
    q(79, 79, "Haskell says Algarotti wanted artists to study Newton’s optical discoveries, which he had propagated earlier.",
      "authorial report", "The passage reports Algarotti’s advocacy; it does not state that artists adopted the discoveries.",
      ["cand-0052", "cand-0067", "cand-1739"], relation_candidate=True,
      footnote_marker="3", footnote_segment=NOTES, footnote_line_range="L188",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=note_links["3"]),
    quote(79, 79, "He was particularly keen that Newton’s discoveries in optics, which he had propagated some years earlier, should be studied by artists"))

add_statement("st-chp14-p354-discussed-optics-and-encouraged-lighter-palette", BODY, "cand-0052", "cand-3781",
    "inferred_discussion_of_optics_and_encouragement_to_lighten_palette",
    q(79, 79, "Haskell says there can be little doubt that Algarotti discussed Newton’s optical discoveries with Tiepolo and must have encouraged him to lighten his palette.",
      "authorial inference", "The ‘little doubt’ and ‘must certainly’ formulations are Haskell’s inference, not documentary proof of either conversation or instruction.",
      ["cand-0052", "cand-3781", "cand-0067", "cand-1739"], relation_candidate=True,
      footnote_marker="3", footnote_segment=NOTES, footnote_line_range="L188",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=note_links["3"]),
    quote(79, 79, "there can be little doubt that he must have discussed them with Tiepolo and that he must certainly have encouraged the artist to lighten his palette."))

add_statement("st-chp14-p354-algarotti-on-colourist-works", BODY, "cand-0052", None,
    "located_real_answers_about_colour_in_great_colourists_works",
    q(79, 80, "After theoretical discussion, Haskell says Algarotti admitted that the real answers lay in the works of great colourists such as Giorgione and Titian.",
      "authorial report of Algarotti’s view", "The judgment is attributed to Algarotti through Haskell; the cited treatise and letter have not been independently read.",
      ["cand-0052", "cand-1188", "cand-2630", "cand-0074", "cand-10303"],
      footnote_marker="3", footnote_segment=NOTES, footnote_line_range="L188",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=note_links["3"]),
    quote(79, 80, "But after some theoretical discussion of the problems involved Algarotti himself admits that the real answers are to be found in the works of the great colourists such as\nGiorgione and Titian"))

add_statement("st-chp14-p354-new-scientific-knowledge-justifies-practice", BODY, "cand-0052", "cand-0067",
    "valued_new_scientific_knowledge_as_theoretical_justification_for_existing_practice",
    q(80, 80, "Haskell says the new scientific knowledge mattered more as theoretical justification for existing practice than as a source of new departures.",
      "authorial assessment of Algarotti’s position", "The source’s comparative judgment is retained; it is not generalized to all scientific knowledge or artists.",
      ["cand-0052", "cand-0067", "cand-1739"],
      ocr_corrections=[{"source_line": 80, "ocr": "newscientific", "print": "new scientific", "basis": "CHP-14.pdf physical page 8."}]),
    quote(80, 80, "the newscientific knowledge is valuable more because it provides a theoretical justification for existing practice than because it makes for new departures."))

add_statement("st-chp14-p354-algarotti-influence-on-tiepolo", BODY, "cand-0052", "cand-3781",
    "influenced_tiepolo_at_this_stage",
    q(81, 81, "Haskell judges Algarotti’s influence on Tiepolo at this stage to have been considerable.",
      "authorial assessment", "The relation remains a book-derived S2 candidate, not a formal edge; Haskell’s assessment is not independently verified.",
      ["cand-0052", "cand-3781", "cand-2573"], relation_candidate=True),
    quote(81, 81, "Algarotti’s influence on Tiepolo at this stage was thus considerable"))

add_statement("st-chp14-p354-early-forties-classical-phase", BODY, "cand-3781", "cand-9266",
    "early_1740s_described_as_peak_of_classical_phase",
    q(81, 81, "Haskell says art historians have agreed that the early 1740s marked the peak of Tiepolo’s classical phase.",
      "authorial report of scholarly consensus", "The consensus is reported by Haskell and has not been independently surveyed.",
      ["cand-3781", "cand-9266"],
      ocr_corrections=[{"source_line": 81, "ocr": "beenagreed", "print": "been agreed", "basis": "CHP-14.pdf physical page 8."}]),
    quote(81, 81, "it has always beenagreed by art historians that the early ’forties marked the peak of the artist’s classical phase."))

add_statement("st-chp14-p354-tiepolo-influence-on-algarotti", BODY, "cand-3781", "cand-0052",
    "influenced_algarotti_in_artistic_and_critical_work",
    q(81, 81, "Haskell says Tiepolo’s influence on Algarotti was just as great and could be seen in Algarotti’s drawings and etchings and, more importantly, in his critical ideas.",
      "authorial assessment", "Haskell’s causal interpretation is retained; the drawings and etchings are not attributed to Tiepolo.",
      ["cand-3781", "cand-0052", "cand-2573", "cand-10300", "cand-2586"], relation_candidate=True,
      footnote_marker="4", footnote_segment=NOTES, footnote_line_range="L189",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=note_links["4"],
      candidate_identity_questions=[{"candidate_id": "cand-2586", "issue": "S1 lists Tiepolo drawings of Oriental heads at p.260n; this p.354 sentence says Algarotti produced the drawings and etchings under Tiepolo’s influence. Preserve as distinct work groups pending S3/source comparison."}]),
    quote(81, 81, "But just as great was Tiepolo’s influence on Algarotti: an influence observable both in the drawings and etchings of oriental heads that he produced for his amusement during these years,4 and—much more importantly—in the development of his critical ideas."))

add_statement("st-chp14-p354-algarotti-oriental-head-works", BODY, "cand-0052", "cand-10300",
    "produced_drawings_and_etchings_of_oriental_heads_for_amusement",
    q(81, 81, "Haskell says Algarotti produced drawings and etchings of Oriental heads for his amusement during these years.",
      "authorial report", "No individual title, date, or location is given; the works are distinct from the separately indexed Tiepolo drawings of Oriental heads.",
      ["cand-0052", "cand-10300", "cand-3781"], relation_candidate=True,
      footnote_marker="4", footnote_segment=NOTES, footnote_line_range="L189",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=note_links["4"]),
    quote(81, 81, "the drawings and etchings of oriental heads that he produced for his amusement during these years"))

add_statement("st-chp14-p354-contact-modified-algarotti-ideas", BODY, "cand-3781", "cand-0052",
    "first_contact_with_practising_artist_modified_preconceptions",
    q(81, 81, "Haskell calls Tiepolo Algarotti’s first real contact with a practising artist of genius and says the contact modified some of Algarotti’s theoretical and preconceived notions.",
      "authorial interpretation", "This is Haskell’s explanation of intellectual change, not a direct statement by either person.",
      ["cand-3781", "cand-0052"], relation_candidate=True),
    quote(81, 81, "For this was Algarotti’s first real contact with a practising artist of genius, and it inevitably modified some of his more theoretical and preconceived notions."))

add_statement("st-chp14-p354-tiepolo-comments-and-venetian-dilemma", BODY, "cand-0052", "cand-3781",
    "comments_on_tiepolo_mark_dilemma_for_venetian_painting_admirers",
    q(81, 81, "Haskell sees Algarotti’s comments on Tiepolo as an early sign of a dilemma that would increasingly perplex admirers of Venetian painting.",
      "authorial interpretation", "The dilemma is Haskell’s framing; its full terms are developed in the continuation beyond p.354.",
      ["cand-0052", "cand-3781", "cand-2719"], relation_candidate=True),
    quote(81, 81, "In fact, we find in his comments on Tiepolo a first indication of that dilemma that was more and more going to perplex admirers of Venetian painting as the century advanced."))

add_statement("st-chp14-p354-learning-brio-fantasy", BODY, "cand-0052", "cand-3781",
    "praised_learning_while_attracted_to_brio_and_fantasy",
    q(81, 81, "Haskell says that although Algarotti praised Tiepolo as learned in the spirit of Raphael or Poussin, he was at least as attracted to Tiepolo’s brio and fantasy.",
      "authorial interpretation", "The contrast is Haskell’s account of Algarotti’s response; ‘learned’ remains a quoted characterization.",
      ["cand-0052", "cand-3781", "cand-2098", "cand-1984"]),
    quote(81, 81, "For despite Algarotti’s attempts to praise the artist as ‘learned’ in the spirit of Raphael or Poussin, he was at least as much attracted by another aspect of Tiepolo’s art: his brio and his fantasy."))

add_statement("st-chp14-p354-algarotti-later-tiepolo-summary", BODY, "cand-0052", "cand-3781",
    "later_summarized_tiepolo_as_fertile_imagination_combining_multiple_manners",
    q(81, 82, "Haskell quotes Algarotti’s later summary of Tiepolo as an imaginative painter combining the manner of Paolo with Castiglione, Salvator Rosa, and fanciful painters, using delightful colour and free brushwork.",
      "authorial report with embedded quotation", "The wording is Haskell’s transcription of Algarotti; the cited treatise in note 5 was not independently consulted.",
      ["cand-0052", "cand-3781", "cand-2755", "cand-0602", "cand-2236", "cand-10306"], relation_candidate=True,
      footnote_marker="5", footnote_segment=NOTES, footnote_line_range="L190",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=note_links["5"]),
    quote(81, 82, "Later he was to sum up Tiepolo as ‘a painter of the most fertile imagination, who has managed to combine the manner of Paolo with that of\nCastiglione, Salvator Rosa and the most fanciful (bizzari) painters, the whole treated with delightful colours and an incredible freedom of brushstrokes’.5"))

add_statement("st-chp14-p354-reconcile-tiepolo-vision-with-neo-classical-demands", BODY, "cand-0052", "cand-3781",
    "sought_to_reconcile_tiepolo_vision_with_neo_classical_demands",
    q(83, 83, "Haskell begins to say that Algarotti was trying to reconcile his vision of Tiepolo with neo-classical demands; the sentence continues on p.355.",
      "authorial interpretation", "The passage ends mid-sentence. Retain this as partial until the p.355 continuation identifies the demands more fully.",
      ["cand-0052", "cand-3781", "cand-6010"], relation_candidate=True,
      cross_reference_segments=["chp-14:14_CHP-14_intro:l85-95"],
      cross_reference_text="sentence continues on p.355"),
    quote(83, 83, "- - constantly trying to reconcile this vision of Tiepolo with the demands of neo-classical"))

add_note_statement("st-chp14-p354-note1-knox-locator",
    q(186, 186, "P.354 note 1 cites Knox, page 16.", "authorial bibliographic note",
      "Only a short citation is supplied; title, date, edition, and author identity are unresolved.",
      ["cand-10301"], cross_reference_segments=[BODY], cross_reference_text="footnote 1 after the Banquet comparison"),
    quote(186, 186, "1 Knox, p. 16."))
add_note_statement("st-chp14-p354-note2-levey-locator",
    q(187, 187, "P.354 note 2 cites Levey’s Burlington Magazine article from 1960, pages 250–257, on the picture and the relation between the two men.",
      "authorial bibliographic note", "OCR ‘Migazine’ and ‘i960’ are corrected in this S2 record from CHP-14.pdf physical page 8; the article was not independently consulted.",
      ["cand-10297", "cand-10302"], cross_reference_segments=[BODY],
      cross_reference_text="footnote 2 after the Bath of Diana commission",
      ocr_corrections=[{"source_line": 187, "ocr": "Migazine, i960", "print": "Magazine, 1960", "basis": "CHP-14.pdf physical page 8."}]),
    quote(187, 187, "2 For this picture, and the relations between the two men generally, see the important article by Levey in Burlington Migazine, i960, pp. 250-7."))
add_note_statement("st-chp14-p354-note3-color-theory-sources",
    q(188, 188, "P.354 note 3 locates Algarotti’s color views in Saggio sopra la Pittura and a 13 May 1756 letter to Eustachio Zanotti, and cites Watson, 1955, page 214, for the suggestion that these ideas mattered especially for Tiepolo.",
      "authorial bibliographic note and report", "The note’s publication citations were not independently checked. OCR ‘in-21’/‘VIH’ are corrected to printed ‘111-21’/‘VIII’ in this S2 record; do not infer that the white-ground idea originated in 1756 beyond the note’s phrasing.",
      ["cand-0052", "cand-0074", "cand-10303", "cand-2863", "cand-9353", "cand-10304"],
      cross_reference_segments=[BODY], cross_reference_text="connects to the p.354 color discussion and the Haskell inference about Tiepolo’s palette",
      ocr_corrections=[{"source_line": 188, "ocr": "in-21; Opere, VIH", "print": "111-21; Opere, VIII", "basis": "CHP-14.pdf physical page 8."}]),
    quote(188, 188, "3 Algarotti’s ideas on the subject are discussed in his Saggio sopra la Pittura (Opere, III, pp. in-21) and in a letter to Eustachio Zanotti of 13 May 1756 (Opere, VIH, pp. 48-52) in which he implies that the ‘fantasia’ that artists should paint on white grounds rather than on the more usual reddish brown has only just occurred to him. The suggestion that these ideas were especially important for Tiepolo has been made by Watson, 1955, p. 214."))
add_statement("st-chp14-p354-note3-white-ground-proposal", NOTES, "cand-0052", "cand-10303",
    "letter_reported_as_saying_white_ground_idea_had_only_just_occurred",
    q(188, 188, "Haskell says the 13 May 1756 letter implies that the idea of artists painting fantasia on white rather than reddish-brown ground had only just occurred to Algarotti.",
      "authorial report of a letter", "The letter itself was not consulted; retain Haskell’s ‘implies’ and ‘only just occurred’ wording without claiming a verified date of invention.",
      ["cand-0052", "cand-10303", "cand-2863"], cross_reference_segments=[BODY],
      cross_reference_text="qualifies the color-theory discussion linked to footnote 3"),
    quote(188, 188, "in which he implies that the ‘fantasia’ that artists should paint on white grounds rather than on the more usual reddish brown has only just occurred to him"))
add_note_statement("st-chp14-p354-note4-rava-locator",
    q(189, 189, "P.354 note 4 cites Rava, 1913, pages 58–61, for the preceding reference to Algarotti’s drawings and etchings.",
      "authorial bibliographic note", "The publication is not identified beyond surname, year, and pages and was not independently consulted.",
      ["cand-10305"], cross_reference_segments=[BODY], cross_reference_text="footnote 4 after the Oriental-head drawings and etchings"),
    quote(189, 189, "4 Rava, 1913, pp. 58-61."))
add_note_statement("st-chp14-p354-note5-saggio-locator",
    q(190, 190, "P.354 note 5 identifies Saggio sopra l’Accademia di Francia che è in Roma, Opere III, page 296, as the source for Algarotti’s quoted summary.",
      "authorial bibliographic note", "The OCR title and volume numeral are corrected from the printed page; the treatise was not independently consulted.",
      ["cand-10306"], cross_reference_segments=[BODY], cross_reference_text="footnote 5 after the later summary of Tiepolo",
      ocr_corrections=[{"source_line": 190, "ocr": "I’AccaJemia ... Opere, HI", "print": "l’Accademia ... Opere, III", "basis": "CHP-14.pdf physical page 8."}]),
    quote(190, 190, "5 In the Saggio sopra I’AccaJemia di Francia che è in Roma (Opere, HI, p. 296)."))

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L64-71",
    "note": "Printed p.353 sentence ‘As in The’ closes at p.354 L74 (‘Banquet of Cleopatra’); linked to st-chp14-p354-banquet-classicism-and-accuracy. S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L74-83",
    "note": "Printed p.354 read against CHP-14.pdf physical p.8. L74 closes p.353; L83 ends mid-sentence at ‘neo-classical’ and continues on p.355. Notes 1-5 at L186-190 are linked; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-190",
    "note": "Printed notes p.347-p.354 read against CHP-14.pdf physical pages 1-8. P.354 notes 1-5 are linked to the Banquet comparison, Bath of Diana, color discussion, Oriental-head works, and later Tiepolo summary; later notes remain pending.",
})

# Verify exact source anchors, foreign keys, and non-overlapping mention intervals before writing.
known_ids = set(candidate_by_id)
for row in planned_mentions:
    seg = row["segment_id"]
    start, end = int(row["start_char"]), int(row["end_char"])
    bounds = segment_bounds[seg]
    segment_text = "\n".join(source_lines[bounds[0] - 1:bounds[1]])
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention anchor mismatch: {row['mention_id']} {row['surface_form']!r}")
    if row["candidate_id"] not in known_ids:
        raise SystemExit(f"mention candidate missing: {row['mention_id']} -> {row['candidate_id']}")
for segment_id in (BODY, NOTES):
    spans = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"], r["surface_form"])
                   for r in planned_mentions if r["segment_id"] == segment_id)
    for left, right in zip(spans, spans[1:]):
        if left[1] > right[0]:
            raise SystemExit(f"overlapping mentions: {left[2]} {left[3]!r} / {right[2]} {right[3]!r}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p354-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        if row["original_quote"] not in "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]]):
            raise SystemExit(f"statement quote missing from source: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in known_ids:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in known_ids:
                raise SystemExit(f"statement mentioned candidate missing: {row['statement_id']} -> {cid}")

new_statements = [row for row in statements if row["statement_id"].startswith("st-chp14-p354-")]
print(json.dumps({"mode": "apply" if args.apply else "dry-run", "new_candidates": len(new_candidates),
                  "new_mentions": len(planned_mentions), "new_statements": len(new_statements),
                  "coverage_updates": {BODY_PREV: coverage_by_id[BODY_PREV], BODY: coverage_by_id[BODY], NOTES: coverage_by_id[NOTES]}},
                 ensure_ascii=False, indent=2))

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
