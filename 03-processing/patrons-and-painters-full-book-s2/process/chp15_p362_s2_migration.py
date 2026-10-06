"""Controlled S2 migration for printed p.362 and notes 1–2; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_SHA = "798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
BODY_PREV = "chp-15:15_CHP-15_sec_i:l3-14"
BODY = "chp-15:15_CHP-15_sec_i:l16-25"
BODY_NEXT = "chp-15:15_CHP-15_sec_i:l27-36"
NOTES = "chp-15:15_CHP-15_sec_i:l43-56"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp15-p362-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.362 S2 migration")
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
    raise SystemExit("chapter 15 body source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-15 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in [
    (17, "not surprising that they tended to turn away from painting"),
    (17, "Filippo Farsetti.1 He was born in 1703"),
    (18, "immense collection he assembled in his family palace near the Rialto"),
    (19, "Ventura Furlani to make casts"),
    (21, "Michelangelo’s Risen Christ"),
    (22, "Giambologna’s Mercury and Bernini’s Neptune"),
    (24, "family estates at S. Maria di Sala"),
    (25, "Doric columns from the Temple of the Dea Concordia in Rome which were ceded to"),
    (44, "family history published by his cousin Tommaso Giuseppe in 1778"),
    (45, "[Andrea Memmo], 1786, p. 60"),
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

for segment_id in (BODY_PREV, BODY, BODY_NEXT, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if (
    coverage_by_id[BODY_PREV]["migration_status"] != "partial"
    or coverage_by_id[BODY]["migration_status"] != "pending"
    or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
    or coverage_by_id[NOTES]["migration_status"] != "pending"
):
    raise SystemExit("S2 coverage preconditions changed")
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 10430:
    raise SystemExit("candidate sequence changed; expected max cand-10430")
PREV_STATEMENT = "st-chp15-p361-enlightenment-different-patronage-partial"
if PREV_STATEMENT not in statement_by_id or not statement_by_id[PREV_STATEMENT]["predicate"].endswith("_partial"):
    raise SystemExit("missing p.361 open cross-page statement")

new_candidates = [
    ("cand-10431", "Farsetti family of Filippo Farsetti (as described in p.362)", "family", BODY, 17,
     "Source-relative family candidate: Haskell calls Filippo Farsetti’s birth family exceedingly rich and says it acquired patrician status in 1664. Its genealogy is not supplied here."),
    ("cand-10432", "Farsetti country house at S. Maria di Sala described on p.362", "place", BODY, 24,
     "The villa is described as a residence designed to hold Farsetti’s expanding collections. Keep distinct from the family palace near the Rialto and from the unrealized Padua plan."),
    ("cand-10433", "S. Maria di Sala, location of Farsetti family estates (p.362)", "place", BODY, 24,
     "Location named for Farsetti’s family estates; no more precise administrative or modern geographical identity is inferred."),
    ("cand-10434", "Plan to build a Roman-type villa at Padua (Farsetti, p.362)", "event", BODY, 24,
     "Unrealized building plan: Haskell says a dispute with local landowners made construction at Padua impossible. Do not represent the planned villa as an existing building."),
    ("cand-10435", "Forty-two Doric columns ceded for Farsetti’s villa (p.362–363)", "work", BODY, 25,
     "Group of architectural columns said to come from the Temple of the Dea Concordia. The p.362 sentence continues at p.363 L28 with the Pope as donor; exact individual columns are not identified."),
    ("cand-10436", "Temple of the Dea Concordia named as the source of columns (p.362)", "place", BODY, 25,
     "Source wording locates the named temple ‘in Rome’; this citation is preserved as written, without external correction or identification."),
    ("cand-10437", "Michelangelo’s Risen Christ in Santa Maria sopra Minerva", "work", BODY, 21,
     "Statue named by Haskell as one of four works Farsetti chose to represent modern sculpture; keep distinct from Bernini’s planned Risen Christ for the baldacchino."),
    ("cand-10438", "Santa Maria sopra Minerva, location of Michelangelo’s Risen Christ", "place", BODY, 21,
     "Church named as the location of the Risen Christ statue; the broader city is not repeated in this clause."),
    ("cand-10439", "Bacchus by Jacopo Sansovino in Farsetti’s sculpture selection", "work", BODY, 21,
     "Statue named as one of four examples of modern sculpture selected by Farsetti; no further date or object history is supplied here."),
    ("cand-10440", "Mercury by Giambologna in Farsetti’s sculpture selection", "work", BODY, 22,
     "Statue named as one of four examples of modern sculpture selected by Farsetti; no further date or object history is supplied here."),
    ("cand-10441", "Neptune by Gian Lorenzo Bernini in Farsetti’s sculpture selection", "work", BODY, 22,
     "Statue named as one of four examples of modern sculpture selected by Farsetti; no further date or object history is supplied here."),
    ("cand-10442", "Principal works by Raphael and Annibale Carracci copied by Luigi Pozzi for Farsetti", "work", BODY, 19,
     "Unidentified group of principal works copied by Pozzi. Individual titles, count, and object identities are not supplied in this passage."),
    ("cand-10443", "Family history of the Farsetti published by Tommaso Giuseppe in 1778", "archive", NOTES, 44,
     "Citation trail in p.362 note 1; title and cited passages are not specified, and the source was not independently consulted."),
    ("cand-10444", "Pamphlet by P. A. Paravia (1829), cited in p.362 note 1", "archive", NOTES, 44,
     "Citation trail in p.362 note 1; title and pages are not supplied, and the pamphlet was not independently consulted."),
    ("cand-10445", "P. A. Paravia (author named in p.362 note 1)", "person", NOTES, 44,
     "Person preserved in the note’s source form; the initials are not expanded and no external identity is inferred."),
    ("cand-10446", "Giovanni Sforza (author named in p.362 note 1)", "person", NOTES, 44,
     "Person named as author of a 1911 article cited by Haskell; no additional biographical identity is inferred."),
    ("cand-10447", "Giovanni Sforza’s 1911 article on Filippo Farsetti and the family (pp.153–195)", "archive", NOTES, 44,
     "Citation trail in p.362 note 1; article title and journal are not supplied here, and it was not independently consulted."),
    ("cand-10448", "Venetian neo-classical movement described in Haskell’s p.362 account", "term", BODY, 18,
     "Historical movement behind which Haskell places Farsetti; retain the author’s evaluative framing and do not treat ‘most important figure’ as an independently tested ranking."),
    ("cand-10449", "Dutch and Flemish painting as a Farsetti collecting interest (p.362)", "term", BODY, 22,
     "Source-specific collecting preference: Haskell says Farsetti showed great enthusiasm for Dutch and Flemish works; no individual works are named in this sentence."),
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

segment_bounds = {BODY: (16, 25), NOTES: (43, 56)}
segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(16, 26)},
    NOTES: {number: source_lines[number - 1] for number in range(43, 57)},
}
segment_texts = {sid: "\n".join(segment_lines[sid][n] for n in range(first, last + 1))
                 for sid, (first, last) in segment_bounds.items()}
segment_offsets = {}
for sid, (first, last) in segment_bounds.items():
    offset = 0
    segment_offsets[sid] = {}
    for number in range(first, last + 1):
        segment_offsets[sid][number] = offset
        offset += len(segment_lines[sid][number]) + 1

planned_mentions = []
mention_counter = 1


def add_mention(segment_id, candidate_id, surface, source_line, note=""):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    line = segment_lines[segment_id][source_line]
    line_offset = segment_offsets[segment_id][source_line]
    occupied = [
        (int(row["start_char"]), int(row["end_char"]))
        for row in mentions + planned_mentions
        if row["segment_id"] == segment_id and line_offset <= int(row["start_char"]) < line_offset + len(line)
    ]
    search_from = 0
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            raise SystemExit(f"surface not found on {segment_id} L{source_line}: {surface!r}")
        start = line_offset + pos
        end = start + len(surface)
        if not any(start < old_end and old_start < end for old_start, old_end in occupied):
            break
        search_from = pos + 1
    mention_id = f"m-chp15-p362-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions + planned_mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_counter += 1


# Body: p.362 physically follows the unnumbered chapter opening and carries the running head 362.
add_mention(BODY, "cand-1002", "Filippo Farsetti", 17)
add_mention(BODY, "cand-1002", "He", 17, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-10431", "exceedingly rich family", 17)
add_mention(BODY, "cand-8294", "patrician status", 17)
add_mention(BODY, "cand-1002", "he", 17, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-1411", "Padre Lodoli", 17)
add_mention(BODY, "cand-1002", "he too", 17, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-8108", "Venetian nobility", 17)
add_mention(BODY, "cand-1002", "he lived", 17, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-4653", "Paris", 17)
add_mention(BODY, "cand-1002", "his status", 17, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-1002", "his time, energy and money", 17, "Pronouns refer to Filippo Farsetti.")
add_mention(BODY, "cand-1002", "Farsetti’s tastes", 18)
add_mention(BODY, "cand-1002", "his collecting", 18, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-10448", "neo-classical movement", 18)
add_mention(BODY, "cand-3401", "Venice", 18)
add_mention(BODY, "cand-1002", "him", 18, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-1005", "immense collection", 18, "Index sub-entry for Farsetti’s collection of casts from antique statues.")
add_mention(BODY, "cand-1010", "family palace", 18, "Index crosswalk candidate is Palazzo Farsetti on p.363; exact building identity will be checked against that continuation.")
add_mention(BODY, "cand-9206", "Rialto", 18)
add_mention(BODY, "cand-1005", "casts taken from antique statues", 18)
add_mention(BODY, "cand-3462", "Europe", 18)
add_mention(BODY, "cand-4490", "Rome", 18)
add_mention(BODY, "cand-2137", "Carlo Rezzonico", 18)
add_mention(BODY, "cand-2137", "Pope Clement", 18, "The title continues across the OCR line break as ‘XIII’ on L19; Haskell identifies this as Carlo Rezzonico’s papal name. Index candidate cand-2898 is only a ‘see under Rezzonico’ cross-reference.")
add_mention(BODY, "cand-2137", "XIII", 19, "Continuation of the title ‘Pope Clement’ at the end of L18; same person as Carlo Rezzonico.")
add_mention(BODY, "cand-4490", "Rome", 19)
add_mention(BODY, "cand-1091", "Ventura Furlani", 19)
add_mention(BODY, "cand-1005", "casts", 19)
add_mention(BODY, "cand-2032", "Luigi Pozzi", 19)
add_mention(BODY, "cand-10442", "principal works", 19)
add_mention(BODY, "cand-2098", "Raphael", 19)
add_mention(BODY, "cand-0576", "Annibale Carracci", 19)
add_mention(BODY, "cand-1002", "his taste", 20, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-10448", "neoclassicism", 20, "OCR form lacks the hyphen used in the preceding ‘neo-classical’ phrase; the source wording is retained.")
add_mention(BODY, "cand-1661", "Michelangelo", 21)
add_mention(BODY, "cand-10437", "Risen Christ", 21)
add_mention(BODY, "cand-10438", "Santa Maria sopra Minerva", 21)
add_mention(BODY, "cand-2355", "Sansovino", 21)
add_mention(BODY, "cand-10439", "Bacchus", 21)
add_mention(BODY, "cand-1160", "Giambologna", 22)
add_mention(BODY, "cand-10440", "Mercury", 22)
add_mention(BODY, "cand-0323", "Bernini", 22)
add_mention(BODY, "cand-10441", "Neptune", 22)
add_mention(BODY, "cand-1006", "small collection of paintings", 22)
add_mention(BODY, "cand-2879", "Zuccarelli", 22)
add_mention(BODY, "cand-10449", "Dutch and Flemish", 22)
add_mention(BODY, "cand-1006", "pictures", 22)
add_mention(BODY, "cand-1002", "his outlook", 22, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-3401", "Venetian", 22)
add_mention(BODY, "cand-1006", "paintings", 22)
add_mention(BODY, "cand-1005", "sculptures", 22)
add_mention(BODY, "cand-10432", "country house", 22)
add_mention(BODY, "cand-1002", "he had assembled", 23, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-1005", "collections", 23)
add_mention(BODY, "cand-3401", "Venice", 23)
add_mention(BODY, "cand-1002", "He", 24, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-10434", "Roman-type villa", 24)
add_mention(BODY, "cand-1803", "Padua", 24)
add_mention(BODY, "cand-10433", "S. Maria di Sala", 24)
add_mention(BODY, "cand-10432", "The villa", 24)
add_mention(BODY, "cand-1002", "his expanding collections", 24, "Pronoun refers to Filippo Farsetti.")
add_mention(BODY, "cand-3401", "Venetian", 24)
add_mention(BODY, "cand-10432", "A convex bay", 24, "Architectural feature of the country house; not a separate building candidate.")
add_mention(BODY, "cand-10432", "main block", 24, "Architectural part of the same villa.")
add_mention(BODY, "cand-10432", "lower two-storey wings", 24, "Architectural parts of the same villa.")
add_mention(BODY, "cand-10432", "small, square pavilions", 24, "Architectural parts of the same villa.")
add_mention(BODY, "cand-10432", "rectangular arcades", 24, "Architectural parts of the same villa.")
add_mention(BODY, "cand-10435", "forty-two", 24, "Quantity is at the end of L24; the object noun continues on L25.")
add_mention(BODY, "cand-10435", "Doric columns", 25, "Continuation of the quantity phrase at the end of L24.")
add_mention(BODY, "cand-10436", "Temple of the Dea Concordia", 25)
add_mention(BODY, "cand-4490", "Rome", 25)

# Notes 1–2 on the same printed page, extracted in the consolidated notes segment.
add_mention(NOTES, "cand-10443", "family history", 44)
add_mention(NOTES, "cand-1013", "Tommaso Giuseppe", 44)
add_mention(NOTES, "cand-10443", "1778", 44)
add_mention(NOTES, "cand-10444", "pamphlet", 44)
add_mention(NOTES, "cand-10444", "1829", 44)
add_mention(NOTES, "cand-10445", "P. A. Paravia", 44)
add_mention(NOTES, "cand-1002", "Farsetti", 44)
add_mention(NOTES, "cand-1006", "gallery", 44)
add_mention(NOTES, "cand-10431", "other members of the family", 44)
add_mention(NOTES, "cand-10446", "Giovanni Sforza", 44)
add_mention(NOTES, "cand-10447", "article", 44)
add_mention(NOTES, "cand-10447", "1911, pp. 153-95", 44)
add_mention(NOTES, "cand-1647", "Andrea Memmo", 45)
add_mention(NOTES, "cand-8812", "1786, p. 60", 45)

unmentioned_new_candidates = {row[0] for row in new_candidates} - {row["candidate_id"] for row in planned_mentions}
if unmentioned_new_candidates:
    raise SystemExit(f"new candidates without an S2 mention anchor: {sorted(unmentioned_new_candidates)}")


def quote(segment_id, line_start, line_end):
    first, last = segment_bounds[segment_id]
    if not first <= line_start <= line_end <= last:
        raise SystemExit(f"quote span outside segment {segment_id}: L{line_start}-{line_end}")
    return "\n".join(segment_lines[segment_id][n] for n in range(line_start, line_end + 1))


def footnote(marker, note_line, statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": f"L{note_line}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": "L17",
        "footnote_note_statement_ids": list(statement_ids),
    }


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", speaker="Haskell", qualification="",
                  mentioned=(), original_quote_override=None, **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 362, "pdf_physical_page": 2,
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


add_statement(
    "st-chp15-p362-men-turn-away-from-painting", BODY, None, None,
    "unnamed_distinguished_men_tended_to_turn_away_from_painting", 17, 17,
    "Haskell says it is not surprising that the few distinguished men just discussed tended to turn away from painting.",
    qualification="The pronoun ‘they’ continues p.361’s ‘few men of great distinction’; the source does not provide a complete roster.",
    mentioned=[], cross_reference_segments=[BODY_PREV], cross_reference_text="Continuation of p.361 L14 ‘though it is’; the caveat closes at p.362 L17.")
previous = statement_by_id[PREV_STATEMENT]
previous["predicate"] = previous["predicate"].removesuffix("_partial")
previous["qualifiers"]["claim"] = (
    "Haskell says a few distinguished men showed that the Enlightenment as it reached Venice suggested new possibilities for a different kind of patronage, "
    "and adds that it is not surprising they tended to turn away from painting."
)
previous["qualifiers"]["qualification"] = (
    "P.361 L14 continues at p.362 L17. ‘They’ refers to the few men of distinction; the source does not enumerate them."
)
previous["qualifiers"]["cross_reference_segments"] = [BODY]
previous["qualifiers"]["cross_reference_text"] = "The p.361 sentence closes with p.362 L17’s caveat about turning away from painting."
previous["qualifiers"]["cross_reference_statement_ids"] = ["st-chp15-p362-men-turn-away-from-painting"]

add_statement(
    "st-chp15-p362-farsetti-greatest-influence-new-patronage", BODY, "cand-1002", "cand-10430",
    "exercised_greatest_influence_in_new_kind_of_patronage", 17, 17,
    "Haskell identifies Filippo Farsetti as the man who exercised the greatest influence in this new direction of patronage.",
    qualification="‘In this way’ links back to the p.361 discussion of Enlightenment and different patronage; it is Haskell’s evaluative ranking.",
    mentioned=["cand-1002", "cand-10430"], relation_candidate=True,
    cross_reference_segments=[BODY_PREV], cross_reference_text="‘In this way’ refers to the p.361 discussion of new patronage.",
    **footnote(1, 44, ["st-chp15-p362-note1-family-history", "st-chp15-p362-note1-paravia-pamphlet", "st-chp15-p362-note1-sforza-article"]))
add_statement(
    "st-chp15-p362-farsetti-born-1703", BODY, "cand-1002", None,
    "born_in_1703", 17, 17,
    "Haskell says Filippo Farsetti was born in 1703.",
    mentioned=["cand-1002"], **footnote(1, 44, ["st-chp15-p362-note1-family-history", "st-chp15-p362-note1-paravia-pamphlet", "st-chp15-p362-note1-sforza-article"]))
add_statement(
    "st-chp15-p362-farsetti-family-rich-and-patrician-status-1664", BODY, "cand-10431", "cand-8294",
    "exceedingly_rich_family_acquired_patrician_status_in_1664", 17, 17,
    "Haskell describes Farsetti’s birth family as exceedingly rich and says it had acquired patrician status only in 1664.",
    qualification="‘Only’ is retained; the passage gives no earlier family genealogy or account of the status process.",
    mentioned=["cand-1002", "cand-10431", "cand-8294"], **footnote(1, 44, ["st-chp15-p362-note1-family-history", "st-chp15-p362-note1-paravia-pamphlet", "st-chp15-p362-note1-sforza-article"]))
add_statement(
    "st-chp15-p362-farsetti-pupil-of-lodoli", BODY, "cand-1002", "cand-1411",
    "became_pupil_of_padre_lodoli_at_about_age_17_or_18", 17, 17,
    "Haskell says Farsetti became Padre Lodoli’s pupil at about age 17 or 18.",
    qualification="The age is approximate; no birth-to-pupil year is calculated.",
    mentioned=["cand-1002", "cand-1411"], relation_candidate=True,
    **footnote(2, 45, ["st-chp15-p362-note2-memmo-1786"]))
add_statement(
    "st-chp15-p362-lodoli-direct-inspirer-of-three-patrons", BODY, "cand-1411", None,
    "described_as_direct_inspirer_of_three_patrons_in_chapter", 17, 17,
    "Haskell calls Lodoli the direct inspirer of all three patrons discussed in the chapter.",
    qualification="The three patrons are not enumerated in this clause; no additional identities are inferred.",
    mentioned=["cand-1411", "cand-1002"], **footnote(2, 45, ["st-chp15-p362-note2-memmo-1786"]))
add_statement(
    "st-chp15-p362-farsetti-travelled-and-wider-cultural-range", BODY, "cand-1002", "cand-8108",
    "travelled_extensively_and_acquired_wider_cultural_range_than_typical_venetian_nobility", 17, 17,
    "Haskell says Farsetti travelled a great deal and acquired a much wider cultural range than was common in the Venetian nobility.",
    qualification="This is Haskell’s comparison; it does not name all destinations or define a measurable cultural range.",
    mentioned=["cand-1002", "cand-8108"], **footnote(1, 44, ["st-chp15-p362-note1-family-history", "st-chp15-p362-note1-paravia-pamphlet", "st-chp15-p362-note1-sforza-article"]))
add_statement(
    "st-chp15-p362-farsetti-lived-in-paris", BODY, "cand-1002", "cand-4653",
    "lived_for_some_years_in_paris", 17, 17,
    "Haskell says Farsetti lived for some years in Paris.",
    qualification="The duration is imprecise in the source.", mentioned=["cand-1002", "cand-4653"],
    **footnote(1, 44, ["st-chp15-p362-note1-family-history", "st-chp15-p362-note1-paravia-pamphlet", "st-chp15-p362-note1-sforza-article"]))
add_statement(
    "st-chp15-p362-farsetti-became-abate-to-avoid-political-responsibilities", BODY, "cand-1002", None,
    "became_abate_to_avoid_political_responsibilities_of_status", 17, 17,
    "Haskell says Farsetti avoided the political responsibilities attached to his status by becoming an abate.",
    qualification="The source presents this as his reason; it does not name an office or formal appointment.",
    mentioned=["cand-1002"], **footnote(1, 44, ["st-chp15-p362-note1-family-history", "st-chp15-p362-note1-paravia-pamphlet", "st-chp15-p362-note1-sforza-article"]))
add_statement(
    "st-chp15-p362-farsetti-devoted-resources-to-arts", BODY, "cand-1002", None,
    "devoted_most_time_energy_and_money_to_arts", 17, 17,
    "Haskell says most of Farsetti’s time, energy and money was devoted to the arts.",
    qualification="‘Most’ is preserved; no amount or particular arts expenditure is inferred.", mentioned=["cand-1002"],
    **footnote(1, 44, ["st-chp15-p362-note1-family-history", "st-chp15-p362-note1-paravia-pamphlet", "st-chp15-p362-note1-sforza-article"]))
add_statement(
    "st-chp15-p362-farsetti-collecting-chronology-not-known", BODY, "cand-1002", "cand-1006",
    "originality_of_tastes_could_be_better_gauged_with_more_collecting_chronology", 18, 18,
    "Haskell says Farsetti’s taste would be easier to assess if more were known about the chronology of his collecting.",
    qualification="This records the author’s stated evidentiary limit, not a claim that chronology is unavailable from all sources.",
    mentioned=["cand-1002", "cand-1006"])
add_statement(
    "st-chp15-p362-farsetti-important-behind-venetian-neoclassicism", BODY, "cand-1002", "cand-10448",
    "by_far_most_important_figure_behind_venetian_neoclassical_movement", 18, 18,
    "Haskell calls Farsetti by far the most important figure behind the neo-classical movement in Venice.",
    qualification="This is Haskell’s evaluative characterization; it is not presented as an independently tested ranking.",
    mentioned=["cand-1002", "cand-10448", "cand-3401"])
add_statement(
    "st-chp15-p362-farsetti-considered-most-significant-patron", BODY, "cand-1002", None,
    "contemporaries_and_successors_considered_him_citys_most_significant_patron", 18, 18,
    "Haskell says that as the century advanced Farsetti’s contemporaries and successors considered him the city’s most significant patron.",
    qualification="This is Haskell’s account of reputation over time, not a unanimous or quantified survey.",
    mentioned=["cand-1002", "cand-3401"])
add_statement(
    "st-chp15-p362-farsetti-cast-collection-in-family-palace", BODY, "cand-1002", "cand-1005",
    "assembled_immense_cast_collection_in_family_palace_near_rialto", 18, 18,
    "Haskell says Farsetti assembled an immense collection of casts from antique statues in his family palace near the Rialto.",
    qualification="The index candidate for Palazzo Farsetti is used as a location crosswalk; p.363 names the palace, and identity will be checked against that continuation.",
    mentioned=["cand-1002", "cand-1005", "cand-1010", "cand-9206"], relation_candidate=True)
add_statement(
    "st-chp15-p362-casts-from-antiquity-europe-and-rome", BODY, "cand-1005", None,
    "casts_taken_from_antique_statues_across_europe_especially_rome", 18, 18,
    "Haskell says the casts represented antique statues from across Europe, especially Rome.",
    qualification="The passage does not enumerate individual statues, artists, or transfer dates.",
    mentioned=["cand-1005", "cand-3462", "cand-4490"])
add_statement(
    "st-chp15-p362-rezzonico-cousin-of-farsetti", BODY, "cand-2137", "cand-1002",
    "cousin_of", 18, 18,
    "Haskell identifies Carlo Rezzonico as Farsetti’s cousin.",
    qualification="This source-level kinship statement remains a candidate for S6, not a formal relation edge.",
    mentioned=["cand-2137", "cand-1002"], relation_candidate=True)
add_statement(
    "st-chp15-p362-rezzonico-became-pope-clement-xiii-1758", BODY, "cand-2137", None,
    "became_pope_clement_xiii_in_1758", 18, 19,
    "Haskell says Carlo Rezzonico became Pope Clement XIII in 1758.",
    qualification="Pope Clement XIII is the papal name/title of Carlo Rezzonico, not a second person; the index entry ‘Clement XIII, Pope’ is only a cross-reference to Rezzonico.",
    mentioned=["cand-2137"])
add_statement(
    "st-chp15-p362-farsetti-assurance-in-rome", BODY, "cand-1002", "cand-4490",
    "moved_with_assurance_in_rome_like_an_english_milord", 19, 19,
    "Haskell characterizes Farsetti as moving in Rome with the assurance of an English milord.",
    text_layer="authorial characterization",
    qualification="This is Haskell’s simile for Farsetti’s manner; it does not assert English nationality, title, or a documented status.",
    mentioned=["cand-1002", "cand-4490"])
add_statement(
    "st-chp15-p362-rezzonico-intervention-enabled-farsetti-collection", BODY, "cand-2137", "cand-1005",
    "intervened_to_enable_farsetti_cast_collection", 18, 18,
    "Haskell says Farsetti was able to assemble the cast collection through the intervention of his cousin Carlo Rezzonico.",
    qualification="The source does not specify the intervention’s form; do not infer a particular papal permission or transaction.",
    mentioned=["cand-2137", "cand-1002", "cand-1005"], relation_candidate=True)
add_statement(
    "st-chp15-p362-furlani-employed-to-make-casts", BODY, "cand-1002", "cand-1091",
    "employed_ventura_furlani_to_make_casts_from_main_statues_of_antiquity", 19, 19,
    "Haskell says Farsetti employed the sculptor Ventura Furlani to make casts from the principal antique statues.",
    qualification="The source does not identify the individual statues copied in this clause.",
    mentioned=["cand-1002", "cand-1091", "cand-1005"], relation_candidate=True)
add_statement(
    "st-chp15-p362-pozzi-copied-principal-works", BODY, "cand-1002", "cand-10442",
    "employed_luigi_pozzi_to_copy_principal_works_of_raphael_and_carracci", 19, 19,
    "Haskell says Farsetti employed Luigi Pozzi to copy principal works by Raphael and Annibale Carracci.",
    qualification="The works are unnamed and uncounted; the attributed group is descriptive, not an identification of individual originals or copies.",
    mentioned=["cand-1002", "cand-2032", "cand-10442", "cand-2098", "cand-0576"], relation_candidate=True)
add_statement(
    "st-chp15-p362-farsetti-selected-four-modern-sculptures", BODY, "cand-1002", None,
    "selected_four_statues_to_represent_modern_sculpture_despite_not_being_hidebound", 20, 20,
    "Haskell says Farsetti’s taste was not as hidebound as that of later, more rigid neo-classical theorists, as shown by his choice of four statues to represent modern sculpture.",
    qualification="This introduces four separately recorded statues; ‘modern sculpture’ is the category stated by Haskell.",
    mentioned=["cand-1002", "cand-10448"], cross_reference_statement_ids=[
        "st-chp15-p362-risen-christ-selected", "st-chp15-p362-bacchus-selected",
        "st-chp15-p362-mercury-selected", "st-chp15-p362-neptune-selected"])
add_statement(
    "st-chp15-p362-risen-christ-selected", BODY, "cand-1002", "cand-10437",
    "selected_as_example_of_modern_sculpture", 21, 21,
    "Farsetti selected Michelangelo’s Risen Christ at Santa Maria sopra Minerva as one of the four statues representing modern sculpture.",
    qualification="The source names the church but gives no installation date or current state.",
    mentioned=["cand-1002", "cand-1661", "cand-10437", "cand-10438"], relation_candidate=True)
add_statement(
    "st-chp15-p362-bacchus-selected", BODY, "cand-1002", "cand-10439",
    "selected_as_example_of_modern_sculpture", 21, 21,
    "Farsetti selected Sansovino’s Bacchus as one of the four statues representing modern sculpture.",
    mentioned=["cand-1002", "cand-2355", "cand-10439"], relation_candidate=True)
add_statement(
    "st-chp15-p362-mercury-selected", BODY, "cand-1002", "cand-10440",
    "selected_as_example_of_modern_sculpture", 22, 22,
    "Farsetti selected Giambologna’s Mercury as one of the four statues representing modern sculpture.",
    mentioned=["cand-1002", "cand-1160", "cand-10440"], relation_candidate=True)
add_statement(
    "st-chp15-p362-neptune-selected", BODY, "cand-1002", "cand-10441",
    "selected_as_example_of_modern_sculpture", 22, 22,
    "Farsetti selected Bernini’s Neptune as one of the four statues representing modern sculpture.",
    mentioned=["cand-1002", "cand-0323", "cand-10441"], relation_candidate=True)
add_statement(
    "st-chp15-p362-farsetti-small-painting-collection", BODY, "cand-1002", "cand-1006",
    "owned_small_collection_of_paintings", 22, 22,
    "Haskell says Farsetti also had a small collection of paintings.",
    qualification="The note describes pictures in a Farsetti gallery; no individual painting is identified in this body sentence.",
    mentioned=["cand-1002", "cand-1006"], relation_candidate=True)
add_statement(
    "st-chp15-p362-few-contemporaries-in-paintings", BODY, "cand-1006", "cand-2879",
    "few_contemporary_painters_represented_apart_from_zuccarelli", 22, 22,
    "Haskell says few contemporaries were represented in Farsetti’s small painting collection apart from the inevitable Zuccarelli.",
    qualification="This is the author’s summary of the collection; it does not identify individual paintings by Zuccarelli.",
    mentioned=["cand-1006", "cand-2879"])
add_statement(
    "st-chp15-p362-farsetti-enthusiastic-for-dutch-flemish", BODY, "cand-1002", "cand-10449",
    "showed_great_enthusiasm_for_dutch_and_flemish_art", 22, 22,
    "Haskell says Farsetti showed great enthusiasm for Dutch and Flemish art.",
    qualification="No individual artists or works are named in this sentence.", mentioned=["cand-1002", "cand-10449"])
add_statement(
    "st-chp15-p362-farsetti-owned-pictures-attributed-to-italian-masters", BODY, "cand-1002", "cand-1006",
    "owned_pictures_attributed_to_wide_range_of_seventeenth_century_italian_masters", 22, 22,
    "Haskell says Farsetti owned pictures attributed to a wide range of seventeenth-century Italian masters.",
    qualification="Retain ‘attributed to’; the artists and pictures are not enumerated.", mentioned=["cand-1002", "cand-1006"])
add_statement(
    "st-chp15-p362-farsetti-cosmopolitan-outlook", BODY, "cand-1002", None,
    "outlook_cosmopolitan_rather_than_venetian_reflected_in_painting_sculpture_and_house", 22, 22,
    "Haskell characterizes Farsetti’s outlook as cosmopolitan rather than Venetian, reflected in his paintings, the strong classical bias of his sculptures, and the architecture of his country house.",
    qualification="This is Haskell’s interpretation of the combined choices, not a claim that Farsetti lacked Venetian ties.",
    mentioned=["cand-1002", "cand-1006", "cand-1005", "cand-10432", "cand-3401"])
add_statement(
    "st-chp15-p362-this-surpassed-venetian-collections-referent-unresolved", BODY, None, None,
    "unnamed_referent_surpassed_venetian_collections_in_extravagance", 23, 23,
    "Haskell writes that ‘This’ far surpassed in extravagance even the collections Farsetti had assembled in Venice.",
    qualification="The antecedent of ‘This’ is unresolved in the current sentence; it may refer to the country house or its collection. Do not assign it to a specific object before the following passage is read.",
    mentioned=["cand-1002", "cand-1005", "cand-1006", "cand-3401"], referent_status="unresolved")
add_statement(
    "st-chp15-p362-padua-villa-plan-abandoned-after-dispute", BODY, "cand-1002", "cand-10434",
    "planned_roman_type_villa_at_padua_abandoned_after_landowner_dispute", 24, 24,
    "Haskell says Farsetti originally planned a Roman-type villa at Padua, but a dispute with local landowners made this impossible.",
    qualification="The villa remained a plan; do not create an extant building or infer the dispute’s details.",
    mentioned=["cand-1002", "cand-10434", "cand-1803"], relation_candidate=True)
add_statement(
    "st-chp15-p362-farsetti-estates-at-s-maria-di-sala", BODY, "cand-1002", "cand-10433",
    "turned_to_family_estates_at_s_maria_di_sala_after_padua_plan_failed", 24, 24,
    "Haskell says Farsetti turned instead to the family estates at S. Maria di Sala, a few miles away.",
    qualification="The source gives only a relative distance and does not specify the local landowners’ identity.",
    mentioned=["cand-1002", "cand-10433"], relation_candidate=True)
add_statement(
    "st-chp15-p362-country-villa-design-description", BODY, "cand-10432", None,
    "villa_designed_for_expanding_collections_unlike_venetian_prototypes_closer_to_austrian_pattern", 24, 24,
    "Haskell says the villa was designed to hold Farsetti’s expanding collections, was unlike standard Venetian prototypes, and in some ways was closer to the Austrian pattern.",
    qualification="‘In some ways’ is retained; the comparison is not generalized to all Austrian or Venetian architecture.",
    mentioned=["cand-10432", "cand-1002", "cand-1005", "cand-1006", "cand-3401"])
add_statement(
    "st-chp15-p362-country-villa-central-convex-bay", BODY, "cand-10432", None,
    "central_convex_bay_projected_from_main_block", 24, 24,
    "Haskell describes a convex bay at the centre of the villa projecting from the main block.",
    qualification="This architectural feature is recorded as part of the villa, not a separate building.", mentioned=["cand-10432"])
add_statement(
    "st-chp15-p362-country-villa-wings-and-pavilions", BODY, "cand-10432", None,
    "main_block_joined_by_lower_two_storey_wings_to_small_square_pavilions", 24, 24,
    "Haskell says the main block was joined by lower two-storey wings to small square pavilions at each end.",
    qualification="The source describes the plan; no measured dimensions are supplied.", mentioned=["cand-10432"])
add_statement(
    "st-chp15-p362-country-villa-arcades-and-columns-partial", BODY, "cand-10432", "cand-10435",
    "lower_storey_arcades_contained_42_doric_columns_from_temple_partial", 24, 25,
    "Haskell says the lower storey of the wings consisted of rectangular arcades containing forty-two Doric columns from the Temple of the Dea Concordia in Rome.",
    qualification="The p.362 sentence ends with ‘which were ceded to’; the recipient and donor continue at p.363 L28. The temple’s location is recorded as printed.",
    mentioned=["cand-10432", "cand-10435", "cand-10436", "cand-4490"], predicate_status="partial",
    cross_reference_segments=[BODY_NEXT], cross_reference_text="P.362 L25 ends ‘which were ceded to’; continuation is p.363 L28.",
    cross_reference_text_pending=True)

add_statement(
    "st-chp15-p362-note1-family-history", NOTES, "cand-1013", "cand-10443",
    "cites_farsetti_family_history_published_1778", 44, 44,
    "P.362 note 1 cites relevant passages in a Farsetti family history published by Tommaso Giuseppe in 1778.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The history’s title and exact passages are not specified; it was not independently consulted.",
    mentioned=["cand-1013", "cand-10431", "cand-10443"], cited_source_independently_consulted=False)
add_statement(
    "st-chp15-p362-note1-paravia-pamphlet", NOTES, "cand-10445", "cand-10444",
    "cites_paravia_pamphlet_of_1829", 44, 44,
    "P.362 note 1 cites a pamphlet by P. A. Paravia from 1829.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The title and pages are not supplied; it was not independently consulted.",
    mentioned=["cand-10445", "cand-10444"], cited_source_independently_consulted=False)
add_statement(
    "st-chp15-p362-note1-sforza-article", NOTES, "cand-10446", "cand-10447",
    "cites_sforza_1911_article_pages_153_195", 44, 44,
    "P.362 note 1 cites Giovanni Sforza’s 1911 article, pages 153–195, for pictures in the Farsetti gallery and information about Filippo and other family members.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The article title and journal are not supplied; the article was not independently consulted.",
    mentioned=["cand-10446", "cand-10447", "cand-1002", "cand-1006", "cand-10431"],
    cited_source_independently_consulted=False)
add_statement(
    "st-chp15-p362-note2-memmo-1786", NOTES, "cand-1647", "cand-8812",
    "cites_memmo_1786_page_60_for_farsetti_admiration_of_lodoli", 45, 45,
    "P.362 note 2 cites Andrea Memmo’s 1786 work, page 60, for Farsetti’s admiration of Lodoli.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The cited page was not independently consulted.",
    mentioned=["cand-1647", "cand-8812", "cand-1002", "cand-1411"], cited_source_independently_consulted=False)

partial_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p362-")}
expected_statement_count = 42
if len(partial_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.362 statements, got {len(partial_statement_ids)}")

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-14",
    "note": "Printed p.361 body at CHP-15.pdf physical p.1 is closed by the p.362 L17 continuation. The full ‘though it is not surprising…’ sentence is recorded across both source segments; p.362 then opens the Farsetti account. Notes 1–2 are linked to the consolidated note segment. S2-only OCR corrections remain outside S0.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L16-25",
    "note": "Printed p.362 checked against CHP-15.pdf physical p.2 (running head 362). Closes p.361’s unfinished sentence, records Farsetti’s biography, patronage, collections and villa, and reads notes 1–2 at consolidated lines 44–45. The final column sentence continues at p.363 L28; ‘This’ at L23 retains an unresolved antecedent. S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L44-45",
    "note": "Read p.362 notes 1–2 against CHP-15.pdf physical p.2 and linked them to body markers at L17. Remaining consolidated note lines L46-56 belong to later printed pages and stay pending until their source-order review.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA,
    "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(partial_statement_ids),
    "updated_statements": [PREV_STATEMENT],
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
