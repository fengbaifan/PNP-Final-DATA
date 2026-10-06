"""Controlled S2 migration for printed p.360; dry-run by default."""
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
BODY_PREV = "chp-14:14_CHP-14_intro:l126-137"
BODY = "chp-14:14_CHP-14_intro:l139-146"
BODY_NEXT = "chp-14:14_CHP-14_intro:l148-149"
BODY_NEXT2 = "chp-14:14_CHP-14_intro:l151-153"
BODY_NEXT3 = "chp-14:14_CHP-14_intro:l155-166"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BACKUP_SUFFIX = ".bak-s2-chp14-p360-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.360 S2 migration")
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
for line_number, required in [
    (140, "battle only to be resolved after his death"),
    (142, "the desire to please"),
    (142, "his sexual tastes seem to have been as unstable"),
    (144, "Caylus,3 ‘sont [sic] de ces gens"),
    (145, "John Constable whiled away the long winter evenings"),
    (146, "Non omnis mortar"),
    (218, "comments of Girolamo Zanetti in 1743"),
    (219, "Cecilia Emo vedova Morosini"),
    (219, "8 In a letter to Paciaudi, edited by Charles Nisard, II, p. 27"),
    (220, "C. R. Leslie: Memoirs of the Life of John Constable"),
]:
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

for segment_id in (BODY_PREV, BODY, BODY_NEXT, BODY_NEXT2, BODY_NEXT3, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if (
    coverage_by_id[BODY_PREV]["migration_status"] != "partial"
    or coverage_by_id[BODY]["migration_status"] != "pending"
    or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
    or coverage_by_id[BODY_NEXT2]["migration_status"] != "pending"
    or coverage_by_id[BODY_NEXT3]["migration_status"] != "pending"
    or coverage_by_id[NOTES]["migration_status"] != "partial"
    or coverage_by_id[NOTES]["source_line_ranges"] != "L169-217"
):
    raise SystemExit("S2 coverage preconditions changed")
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 10414:
    raise SystemExit("candidate sequence changed; expected max cand-10414")
if "st-chp14-p359-algarotti-synthesis-styles-partial" not in statement_by_id:
    raise SystemExit("missing open p.359 cross-page statement")
if not statement_by_id["st-chp14-p359-algarotti-synthesis-styles-partial"]["predicate"].endswith("_partial"):
    raise SystemExit("p.359 continuation was already revised")
if "st-fm-pl-p60-tomb" not in statement_by_id:
    raise SystemExit("missing existing Plate 60 tomb caption reference")

new_candidates = [
    ("cand-10415", "Girolamo Zanetti’s comments on Algarotti (1743; published 1885)", "archive", NOTES, 218,
     "Citation trail for comments attributed to Girolamo Zanetti in 1743 and published in 1885; the specific publication and pages are not supplied in this note."),
    ("cand-10416", "L. Melchiori (editor named in p.360 note 1)", "person", NOTES, 218,
     "Source form for the editor named as publisher of Gaspare Patriarchi’s 1758 words; full name and publication details are not supplied here."),
    ("cand-10417", "Gaspare Patriarchi’s words (1758; published by L. Melchiori, p.22)", "archive", NOTES, 218,
     "Citation trail for words attributed to Gaspare Patriarchi in 1758 and published by L. Melchiori on page 22; the underlying publication was not independently consulted."),
    ("cand-10418", "Cecilia Emo (called widow Morosini, later Contessa Zenobio in Biffi’s quotation)", "person", NOTES, 219,
     "A woman named in Haskell’s quotation of Giambattista Biffi; preserve the quoted forms Cecilia Emo, widow Morosini, and later Contessa Zenobio without external identity or title verification."),
    ("cand-10419", "Charles Nisard (editor named in p.360 note 3)", "person", NOTES, 219,
     "Editor named for a letter to Paciaudi in volume II, page 27; no further bibliographic or biographical details are supplied in this note."),
    ("cand-10420", "Letter to Paciaudi edited by Charles Nisard (vol. II, p.27; p.360 n.3)", "archive", NOTES, 219,
     "Citation trail for a letter to Paciaudi, edited by Charles Nisard, volume II, page 27; the letter’s author and text are not identified in this note."),
    ("cand-10421", "C. R. Leslie (author named in p.360 note 4)", "person", NOTES, 220,
     "Author named in the citation to Memoirs of the Life of John Constable; retained in the cited source form."),
    ("cand-10422", "C. R. Leslie, Memoirs of the Life of John Constable (London, 1951), p.7", "archive", NOTES, 220,
     "Bibliographic citation supplied in p.360 note 4; not independently consulted."),
]
for cid, name, suggested_type, segment_id, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment_id}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

segment_bounds = {BODY: (139, 146), NOTES: (168, 220)}
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
    mention_id = f"m-chp14-p360-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(pos), "end_char": str(end), "note": note,
    })
    mention_counter += 1


# Page 360 body: preserve Haskell's account, quotations, and qualifications.
add_mention(BODY, "cand-0050", "Algarotti")
add_mention(BODY, "cand-0059", "early neo-classicism")
add_mention(BODY, "cand-0050", "his heart", "Pronoun refers to Algarotti.")
add_mention(BODY, "cand-2569", "Tiepolo")
add_mention(BODY, "cand-2569", "the Venetian artist", "Appositional reference to Tiepolo.")
add_mention(BODY, "cand-6439", "antiquity")
add_mention(BODY, "cand-2551", "Mauro")
add_mention(BODY, "cand-2551", "Tesi")
add_mention(BODY, "cand-6439", "neo-classicism")
add_mention(BODY, "cand-0050", "his personal temperament", "Pronoun refers to Algarotti.")
add_mention(BODY, "cand-0050", "his most pronounced characteristic", "Pronoun refers to Algarotti.")
add_mention(BODY, "cand-0050", "his sexual tastes", "Attributed characterization by Haskell; not an independently verified diagnosis.")
add_mention(BODY, "cand-0050", "he found it impossibly difficult", "Pronoun refers to Algarotti.")
add_mention(BODY, "cand-0050", "his writings", "Pronoun refers to Algarotti.")
add_mention(BODY, "cand-0615", "Caylus", "Name is split by a source line break after ‘Comte de’.")
add_mention(BODY, "cand-0050", "him", "Pronoun refers to Algarotti.")
add_mention(BODY, "cand-0822", "John Constable")
add_mention(BODY, "cand-0050", "his works", "Pronoun refers to Algarotti.")
add_mention(BODY, "cand-0050", "his memory", "Pronoun refers to Algarotti.")
add_mention(BODY, "cand-1303", "Horace")
add_mention(BODY, "cand-1080", "Frederick the Great")
add_mention(BODY, "cand-4042", "Plate 60", "Cross-reference to the existing list-of-plates caption; no identity claim about the physical monument and depicted print is added.")

# Page 360 notes: citation candidates remain source-local and unverified.
add_mention(NOTES, "cand-9280", "Girolamo Zanetti")
add_mention(NOTES, "cand-10415", "1743 (published 1885)")
add_mention(NOTES, "cand-9970", "Gaspare Patriarchi")
add_mention(NOTES, "cand-10417", "in 1758", "Citation context for the new source candidate; the named author is linked separately.")
add_mention(NOTES, "cand-10416", "L. Melchiori")
add_mention(NOTES, "cand-10260", "Halsband")
add_mention(NOTES, "cand-0373", "Giambattista Biffi")
add_mention(NOTES, "cand-0373", "he wrote", "Pronoun refers to Giambattista Biffi.")
add_mention(NOTES, "cand-10418", "Cecilia Emo")
add_mention(NOTES, "cand-10418", "vedova Morosini")
add_mention(NOTES, "cand-10418", "Contessa Zenobio")
add_mention(NOTES, "cand-9832", "see p. 328, note 5", "Source's own cross-reference; does not independently prove that this is the same letter as the p.328 archival citation.")
add_mention(NOTES, "cand-1802", "Paciaudi")
add_mention(NOTES, "cand-10420", "II, p. 27", "Citation locator for the letter candidate; Paciaudi and Nisard are linked by separate mentions.")
add_mention(NOTES, "cand-10419", "Charles Nisard")
add_mention(NOTES, "cand-10421", "C. R. Leslie")
add_mention(NOTES, "cand-10422", "Memoirs of the Life of John Constable, London 1951, p. 7")

unmentioned_new_candidates = {row[0] for row in new_candidates} - {row["candidate_id"] for row in planned_mentions}
if unmentioned_new_candidates:
    raise SystemExit(f"new candidates without an S2 mention anchor: {sorted(unmentioned_new_candidates)}")


def quote(segment_id, line_start, line_end):
    return "\n".join(source_lines[line_start - 1:line_end])


def footnote(marker, note_lines, statement_ids, body_line_range):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": note_lines, "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": body_line_range,
        "footnote_note_statement_ids": list(statement_ids),
    }


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", speaker="Haskell", qualification="",
                  mentioned=(), original_quote_override=None, **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 360, "pdf_physical_page": 14,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": original_quote_override if original_quote_override is not None else quote(segment_id, line_start, line_end),
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


previous = statement_by_id["st-chp14-p359-algarotti-synthesis-styles-partial"]
previous["predicate"] = previous["predicate"].removesuffix("_partial")
previous["qualifiers"]["claim"] = (
    "Haskell says Algarotti was always trying to synthesize two styles just beginning to clash; "
    "the sentence continues that the battle could only be resolved after Algarotti's death."
)
previous["qualifiers"]["qualification"] = (
    "The p.359 sentence is closed by p.360 L140. The continuation is separately recorded as "
    "st-chp14-p360-synthesis-resolution."
)
previous["qualifiers"]["cross_reference_segments"] = [BODY]
previous["qualifiers"]["cross_reference_text"] = "p.359 L137 continues at p.360 L140 and closes there."
previous["qualifiers"]["cross_reference_statement_ids"] = ["st-chp14-p360-synthesis-resolution"]

add_statement(
    "st-chp14-p360-synthesis-resolution", BODY, "cand-0059", None,
    "styles_battle_resolved_only_after_algarottis_death", 140, 140,
    "Haskell completes his account of Algarotti’s attempted synthesis by saying the conflict between the two styles could be resolved only after Algarotti’s death.",
    qualification="This closes the p.359 L137 sentence; the later discussion of Algarotti’s continuing allegiance to an older tradition is recorded separately.",
    mentioned=["cand-0059", "cand-0076", "cand-0050"], cross_reference_segments=[BODY_PREV],
    cross_reference_text="Continuation of p.359 L137; the opening words at p.360 L140 close that sentence.",
    cross_reference_statement_ids=["st-chp14-p359-algarotti-synthesis-styles-partial"])

add_statement(
    "st-chp14-p360-algarotti-attached-to-older-tradition", BODY, "cand-0050", None,
    "remained_attached_to_older_less_austere_tradition_despite_neoclassical_stage_props", 140, 140,
    "Haskell says that although Algarotti played with the stage props of early neo-classicism, his heart remained with an older, less austere tradition.",
    qualification="This is Haskell’s characterization of Algarotti’s position, not a claim that he rejected every neo-classical idea.",
    mentioned=["cand-0050", "cand-6439"])

add_statement(
    "st-chp14-p360-tiepolo-ideal-painter", BODY, "cand-0050", "cand-2569",
    "regarded_tiepolo_as_ideal_painter", 140, 140,
    "Haskell says Algarotti found in Tiepolo the ideal painter.",
    qualification="Reported by Haskell; no independent letter or statement by Algarotti is asserted here.",
    mentioned=["cand-0050", "cand-2569"], relation_candidate=True)

add_statement(
    "st-chp14-p360-reported-tiepolo-admired-antiquity", BODY, "cand-0050", "cand-2569",
    "reported_tiepolo_admiration_of_antiquity", 140, 140,
    "Haskell says Algarotti reported Tiepolo’s admiration of antiquity with satisfaction.",
    qualification="This records Algarotti’s report as represented by Haskell, not an independently verified statement by Tiepolo.",
    mentioned=["cand-0050", "cand-2569", "cand-6439"])

add_statement(
    "st-chp14-p360-encouraged-tesi-painterly-qualities", BODY, "cand-0050", "cand-2551",
    "encouraged_painterly_qualities_of_tesi", 140, 141,
    "Haskell says Algarotti was keen to encourage the painterly qualities of the essentially architectural artist Mauro Tesi.",
    qualification="The source describes Algarotti’s encouragement; it does not define a particular commission in this sentence.",
    mentioned=["cand-0050", "cand-2551"], relation_candidate=True)

add_statement(
    "st-chp14-p360-representative-early-neoclassicism", BODY, "cand-0050", "cand-6439",
    "described_as_representative_of_early_neoclassicism", 142, 142,
    "Haskell calls Algarotti a fairly representative figure of this early stage of neo-classicism.",
    qualification="The wording is qualified as ‘fairly representative’ and applies to an early stage.",
    mentioned=["cand-0050", "cand-6439"])

add_statement(
    "st-chp14-p360-temperament-and-vacillation", BODY, "cand-0050", None,
    "temperament_partly_responsible_for_vacillating_views", 142, 142,
    "Haskell says Algarotti’s personal temperament was at least partly responsible for the vacillating nature of many of his views.",
    qualification="Haskell presents this as a partial explanation, not the sole cause of every change in view.",
    mentioned=["cand-0050"])

add_statement(
    "st-chp14-p360-contemporaries-desire-to-please", BODY, "cand-0050", None,
    "contemporaries_agreed_desire_to_please_even_at_cost_of_consistency", 142, 142,
    "Haskell says all Algarotti’s contemporaries agreed that his most pronounced characteristic was a desire to please everyone, even at the cost of consistency.",
    qualification="This is Haskell’s report of a consensus among contemporaries; the source does not identify each speaker in the body text.",
    mentioned=["cand-0050"], **footnote(1, "L218", ["st-chp14-p360-note1-zanetti", "st-chp14-p360-note1-patriarchi"], "L142"))

add_statement(
    "st-chp14-p360-sexual-tastes-seem-unstable", BODY, "cand-0050", None,
    "sexual_tastes_seem_as_unstable_as_artistic_views", 142, 142,
    "Haskell writes that Algarotti’s sexual tastes seemed as unstable as his artistic views.",
    qualification="Retain ‘seem’ and attribute this historical characterization to Haskell; the note says Halsband discussed the subject, but neither source was independently consulted here.",
    mentioned=["cand-0050", "cand-10260"], **footnote(2, "L219", ["st-chp14-p360-note2-halsband", "st-chp14-p360-note2-biffi-cecilia"], "L142"))

add_statement(
    "st-chp14-p360-difficulty-committing", BODY, "cand-0050", None,
    "found_it_difficult_to_commit_himself", 143, 143,
    "Haskell says Algarotti found it impossibly difficult to commit himself, comparing him with people in the stated psychological condition.",
    qualification="The source’s comparison is preserved as Haskell’s interpretation; it is not converted into a clinical diagnosis.",
    mentioned=["cand-0050"] , ocr_corrections=[{"source_line": 143, "ocr": "-psychological", "print": "psychological"}])

add_statement(
    "st-chp14-p360-writings-criticized-as-flabby", BODY, "cand-0050", None,
    "writings_criticized_for_flabbiness", 143, 143,
    "Haskell says this difficulty committing himself accounts for an element of flabbiness often criticized in Algarotti’s writings.",
    text_layer="authorial evaluation", qualification="This is Haskell’s evaluative explanation of a criticism, not a bibliographic fact.",
    mentioned=["cand-0050"])

add_statement(
    "st-chp14-p360-caylus-quote", BODY, "cand-0615", "cand-0050",
    "criticized_algarotti_as_leaving_nothing_after_him", 143, 144,
    "Haskell quotes the dogmatic Comte de Caylus saying of Algarotti, ‘sont [sic] de ces gens qui ont vécu et qui ne laissent rien après eux.’",
    text_layer="quotation reproduced by Haskell", speaker="Comte de Caylus, quoted by Haskell",
    qualification="Preserve Haskell’s [sic] and the original French; the cited source was not independently consulted.",
    mentioned=["cand-0615", "cand-0050"], **footnote(3, "L219", ["st-chp14-p360-note3-paciaudi-letter"], "L144"))

add_statement(
    "st-chp14-p360-responsive-artists", BODY, "cand-0050", None,
    "found_more_responsive_readers_among_artists", 144, 145,
    "Haskell says Algarotti found more responsive readers in the more sympathetic world of artists.",
    qualification="This is Haskell’s contrast between artists and the preceding criticism; the individual readers are not named here.",
    mentioned=["cand-0050"])

add_statement(
    "st-chp14-p360-constable-studied-works", BODY, "cand-0822", "cand-0050",
    "studied_algarottis_works_more_than_thirty_years_after_his_death", 145, 145,
    "Haskell says that more than thirty years after Algarotti’s death, John Constable spent long winter evenings studying his works.",
    qualification="This is Haskell’s report, supported in the book by the p.360 note 4 citation; Leslie’s memoir was not independently consulted.",
    mentioned=["cand-0822", "cand-0050", "cand-10421", "cand-10422"], relation_candidate=True,
    **footnote(4, "L220", ["st-chp14-p360-note4-leslie-memoir"], "L145"))

add_statement(
    "st-chp14-p360-frederick-erected-monument", BODY, "cand-1080", "cand-0050",
    "erected_monument_to_memory_of", 146, 146,
    "Haskell says Frederick the Great erected a monument to Algarotti’s memory.",
    qualification="The body points to Plate 60. The existing list-of-plates caption is cross-referenced, but the physical monument is not equated here with the depicted print.",
    mentioned=["cand-1080", "cand-0050", "cand-4042", "cand-4107", "cand-3777", "cand-3956"],
    relation_candidate=True, cross_reference_segments=["front-matter:00_05_List_of_Plates:l123-138"],
    cross_reference_text="Plate 60 points to the existing caption ‘G. Volpato: Mourners at Tomb of Francesco Algarotti in Pisa’.",
    cross_reference_statement_ids=["st-fm-pl-p60-tomb"])

add_statement(
    "st-chp14-p360-inscription-adapts-horace", BODY, "cand-0050", "cand-1303",
    "memorial_inscription_adapted_from_horace", 146, 146,
    "Haskell says the inscription ‘Algarottus non omnis’ adapts Horace’s ‘Non omnis moriar’ and was placed on the monument erected to Algarotti’s memory.",
    qualification="Print reads ‘moriar’; S0 OCR reads ‘mortar’. The inscription text and its reported placement remain attributed to Haskell.",
    mentioned=["cand-0050", "cand-1303", "cand-1080", "cand-4042"],
    ocr_corrections=[{"source_line": 146, "ocr": "Non omnis mortar", "print": "Non omnis moriar"}],
    cross_reference_statement_ids=["st-chp14-p360-frederick-erected-monument", "st-fm-pl-p60-tomb"])

# Footnotes 1–4 on p.360 are distinct from p.359's orphaned Gabbrielli note 4.
add_statement(
    "st-chp14-p360-note1-zanetti", NOTES, "cand-9280", "cand-10415",
    "cites_1743_comments_published_1885", 218, 218,
    "P.360 note 1 cites comments by Girolamo Zanetti from 1743, published in 1885.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The specific publication and pages are not supplied; the cited material was not independently consulted.",
    mentioned=["cand-9280", "cand-10415"], cited_source_independently_consulted=False)

add_statement(
    "st-chp14-p360-note1-patriarchi", NOTES, "cand-9970", "cand-10417",
    "cites_1758_words_published_by_melchiori_page_22", 218, 218,
    "P.360 note 1 cites Gaspare Patriarchi’s words from 1758, published by L. Melchiori on page 22.",
    speaker="Haskell’s note", text_layer="citation trail and quotation",
    qualification="L. Melchiori and the underlying publication are not further identified; the source was not independently consulted.",
    mentioned=["cand-9970", "cand-10416", "cand-10417"], cited_source_independently_consulted=False)

add_statement(
    "st-chp14-p360-note2-halsband", NOTES, "cand-10260", None,
    "discussed_algarottis_homosexual_tendencies", 219, 219,
    "P.360 note 2 says that Halsband discussed Algarotti’s homosexual tendencies.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="Halsband is supplied by surname only; the work and pages are not identified here and were not independently consulted.",
    mentioned=["cand-10260"], original_quote_override=source_lines[218].split("On the other hand")[0].rstrip(),
    cited_source_independently_consulted=False)

add_statement(
    "st-chp14-p360-note2-biffi-cecilia", NOTES, "cand-0373", None,
    "reported_1773_quotation_about_algarotti_and_cecilia_emo", 219, 219,
    "Haskell quotes Giambattista Biffi, writing in Venice in 1773, as saying that Algarotti ardently loved a woman still living there and naming her as Cecilia Emo, widow Morosini, later Contessa Zenobio.",
    speaker="Giambattista Biffi, quoted by Haskell", text_layer="quotation reproduced by Haskell",
    qualification="The Italian quotation is retained as printed/OCR text. The note cross-references p.328 note 5; that cross-reference is not treated as independent proof that this is the same manuscript as the p.328 archival citation.",
    mentioned=["cand-0373", "cand-10418", "cand-9832"],
    original_quote_override=source_lines[218].split(" . 8 In a letter to Paciaudi")[0].rstrip(),
    cross_reference_segments=["chp-10:10_CHP-10_sec_ii:l273-349"],
    cross_reference_text="P.360 note 2 explicitly says ‘see p. 328, note 5’.",
    cross_reference_statement_ids=["st-chp10-p328-n05-biffi-letter-citation"],
    cited_source_independently_consulted=False)

add_statement(
    "st-chp14-p360-note3-paciaudi-letter", NOTES, None, "cand-10420",
    "cites_letter_to_paciaudi_edited_by_nisard_volume_ii_page_27", 219, 219,
    "P.360 note 3 cites a letter to Paciaudi edited by Charles Nisard, volume II, page 27.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The letter’s author and text are not identified here. OCR reads the note marker as 8; the p.360 print shows note 3. The cited edition was not independently consulted.",
    mentioned=["cand-1802", "cand-10419", "cand-10420"],
    original_quote_override="8 In a letter to Paciaudi, edited by Charles Nisard, II, p. 27.",
    ocr_corrections=[{"source_line": 219, "ocr": "8 In a letter", "print": "3 In a letter"}],
    cited_source_independently_consulted=False)

add_statement(
    "st-chp14-p360-note4-leslie-memoir", NOTES, "cand-10421", "cand-10422",
    "cites_leslie_memoir_volume_page", 220, 220,
    "P.360 note 4 cites C. R. Leslie’s Memoirs of the Life of John Constable, London 1951, page 7.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The cited memoir and page were not independently consulted; this is p.360’s own note 4 and is distinct from p.359 note 4’s Gabbrielli citation.",
    mentioned=["cand-10421", "cand-10422", "cand-0822"], cited_source_independently_consulted=False)

# Explicitly retain the unresolved p.359 n.4 body-marker anomaly; p.360 n.4 is not its continuation.
orphan_note = statement_by_id["st-chp14-p359-note4-gabbrielli-general-discussion"]
orphan_note["qualifiers"].update({
    "footnote_marker": "4", "footnote_segment": BODY_PREV,
    "footnote_body_line_range": "not located in p.359 L127-137",
    "footnote_body_link_status": "orphan_unresolved",
    "footnote_anomaly": "P.359 n.4 has no visible body marker on printed p.359; p.360 L145 marker 4 is separately linked to Leslie, Memoirs, p.7.",
})

new_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp14-p360-")}
expected_statement_count = 22
if len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.360 statements, got {len(new_statement_ids)}")

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L127-137",
    "note": "Printed p.359 read against CHP-14.pdf physical p.13. L137 closes at p.360 L140. Notes 1–3 link to p.359 body markers; p.359 n.4 (Gabbrielli) has no visible body marker located on L127–137 and remains an explicit orphan audit item. Do not link it to p.360 n.4 (Leslie). S2-only print corrections recorded; S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L140-146",
    "note": "Printed p.360 read against CHP-14.pdf physical p.14. Closes the p.359 synthesis sentence; records Haskell’s discussion of Algarotti, Tiepolo, Tesi, Caylus, Constable, and the Frederick/inscription passage. P.360 body notes 1–4 link to L218–220. The Plate 60 pointer cross-references the existing caption without equating its print with the physical monument. OCR/print corrections recorded in S2 only; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L169-220",
    "note": "Consolidated notes through p.360 n.4 (L220) read and recorded. P.360 notes 1–4 are separately linked to p.360 body markers. P.359 n.4 Gabbrielli citation remains an explicit orphan audit item because no body marker was located on p.359; p.360 n.4 is Leslie and is not linked to it. Cited sources were not independently consulted; S0 unchanged.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA,
    "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "updated_statements": ["st-chp14-p359-algarotti-synthesis-styles-partial", "st-chp14-p359-note4-gabbrielli-general-discussion"],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
}

if args.apply:
    touched = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in touched:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions + planned_mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps(result, ensure_ascii=False, indent=2))
