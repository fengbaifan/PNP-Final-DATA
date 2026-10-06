"""Controlled S2 migration for the Farsetti close on printed p.364; dry-run by default."""
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
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_i.md"
BODY_PREV = "chp-15:15_CHP-15_sec_i:l27-36"
BODY = "chp-15:15_CHP-15_sec_i:l38-41"
BODY_NEXT = "chp-15:15_CHP-15_sec_ii:l3-4"
NOTES = "chp-15:15_CHP-15_sec_i:l43-56"
BACKUP_SUFFIX = ".bak-s2-chp15-p364-farsetti-apply-20261004"
PREVIOUS_PARTIAL = "st-chp15-p363-daniele-continued-patronage-partial"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.364 Farsetti S2 migration")
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
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 15 body source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-15 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in [
    (39, "Daniele’s brother, Tommaso Giuseppe (1720-91)"),
    (39, "last years of his fife were embittered"),
    (39, "denounced to the Inquisitors.1 This was to no avail"),
    (40, "the influence of Farsetti seems in retrospect to have been negligible or deleterious"),
    (40, "a grëat cultural revival"),
    (41, "exemplified by Andrea Memmo"),
    (51, "Inquisitori di Stato (Busta 540), Annotazioni, p. 164—30 Maggio 1792"),
    (52, "Moschini, 1806, II, p. 114"),
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
    or coverage_by_id[NOTES]["migration_status"] != "partial"
    or coverage_by_id[NOTES]["source_line_ranges"] != "L44-50"
):
    raise SystemExit("S2 coverage preconditions changed")
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 10461:
    raise SystemExit("candidate sequence changed; expected max cand-10461")
if PREVIOUS_PARTIAL not in statement_by_id or not statement_by_id[PREVIOUS_PARTIAL]["predicate"].endswith("_partial"):
    raise SystemExit("missing open p.363 Daniele patronage statement")

new_candidates = [
    ("cand-10462", "Archivio di Stato, Venice, Inquisitori di Stato, Busta 540, Annotazioni, p.164 (30 May 1792)", "archive", NOTES, 51,
     "Citation trail in p.364 note 1 for Tommaso Giuseppe Farsetti’s denunciation of Anton Francesco. The record was not independently consulted."),
    ("cand-10463", "Moschini, 1806, volume II, p.114, cited in p.364 note 2", "archive", NOTES, 52,
     "Short-form citation for the breakup and sale of the Farsetti property and collections. Full title and cited page were not independently checked."),
    ("cand-10464", "Inquisitori di Stato of Venice, named in p.364 note 1", "institution", BODY, 39,
     "Institution identified by Haskell’s note citation to Busta 540. Do not infer additional jurisdiction or procedure from this passage."),
    ("cand-10465", "Tommaso Giuseppe Farsetti’s fine collection of books and manuscripts (p.364)", "", BODY, 39,
     "A personal collection described by Haskell; it is not presented as a named library or institutional archive. Type and contents remain unresolved."),
    ("cand-10466", "Cultural revival hoped for by Farsetti’s contemporaries (p.364)", "term", BODY, 40,
     "Haskell says contemporaries based their hopes for a great cultural revival on Farsetti’s patronage; preserve the claim as source interpretation."),
    ("cand-10467", "Support for the arts as a public service benefiting the community (p.364)", "term", BODY, 41,
     "The conception attributed to new patrons exemplified by Andrea Memmo; do not treat it as a formal programme or established outcome."),
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

segment_bounds = {BODY: (38, 41), NOTES: (43, 56)}
segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(38, 42)},
    NOTES: {number: source_lines[number - 1] for number in range(43, 57)},
}
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
    mention_id = f"m-chp15-p364-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions + planned_mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_counter += 1


def quote(segment_id, line_start, line_end):
    first, last = segment_bounds[segment_id]
    if not first <= line_start <= line_end <= last:
        raise SystemExit(f"quote span outside segment {segment_id}: L{line_start}-{line_end}")
    return "\n".join(segment_lines[segment_id][n] for n in range(line_start, line_end + 1))


def footnote(marker, note_line, body_line, statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": f"L{note_line}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": f"L{body_line}",
        "footnote_note_statement_ids": list(statement_ids),
    }


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", speaker="Haskell", qualification="",
                  mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 364, "pdf_physical_page": 4,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
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


# Close the p.363 sentence across the page break while retaining the original source span.
previous = statement_by_id[PREVIOUS_PARTIAL]
previous["predicate"] = previous["predicate"].removesuffix("_partial")
previous["qualifiers"]["predicate_status"] = "complete"
previous["qualifiers"]["qualification"] = (
    "P.364 L39 completes the phrase as ‘patronage of contemporary artists’. "
    "No particular recipients or commissions are named."
)
previous["qualifiers"]["cross_reference_segments"] = [BODY]
previous["qualifiers"]["cross_reference_text"] = "P.363 L35 ends ‘continued the’; p.364 L39 completes it as ‘patronage of contemporary artists.’"
previous["qualifiers"]["cross_reference_text_pending"] = False

# Mentions in the Farsetti close on printed p.364.
add_mention(BODY, "cand-1001", "Daniele’s", 39, "Possessive identifies Daniele Farsetti as Tommaso Giuseppe’s brother.")
add_mention(BODY, "cand-1013", "brother", 39, "Tommaso Giuseppe Farsetti is Daniele’s brother.")
add_mention(BODY, "cand-1013", "Tommaso Giuseppe", 39)
add_mention(BODY, "cand-1013", "1720-91", 39, "Dates are transcribed as printed in the source; no exact dates are inferred.")
add_mention(BODY, "cand-10465", "his fine collection of books and manuscripts", 39, "Personal collection; not a named library or institutional archive.")
add_mention(BODY, "cand-1013", "he too", 39, "Pronoun refers to Tommaso Giuseppe Farsetti.")
add_mention(BODY, "cand-10431", "the family tradition", 39)
add_mention(BODY, "cand-1013", "he wrote", 39)
add_mention(BODY, "cand-10443", "an exalted account", 39, "May refer to the Farsetti family history cited at p.362 note 1; exact work identity is left to S3.")
add_mention(BODY, "cand-1013", "he describes", 39)
add_mention(BODY, "cand-1002", "Filippo’s collecting", 39)
add_mention(BODY, "cand-1002", "enormous expense", 39, "Expense is described in relation to Filippo’s collecting.")
add_mention(BODY, "cand-1013", "his fife", 39, "OCR reads ‘fife’; the page image reads ‘life’.")
add_mention(BODY, "cand-1000", "his nephew Anton Francesco", 39, "Nephew of Tommaso Giuseppe; no additional kinship is inferred.")
add_mention(BODY, "cand-1013", "he even denounced", 39)
add_mention(BODY, "cand-10464", "the Inquisitors", 39, "P.364 note 1 names the Inquisitori di Stato in the archival locator.")
add_mention(BODY, "cand-1013", "This", 39, "Refers to the denunciation of Anton Francesco.")
add_mention(BODY, "cand-1005", "the collections", 39, "The passage does not enumerate which holdings were sold.")
add_mention(BODY, "cand-0532", "Canova", 40)
add_mention(BODY, "cand-3401", "Venice", 40)
add_mention(BODY, "cand-1002", "the influence of Farsetti", 40)
add_mention(BODY, "cand-1002", "His contemporaries", 40)
add_mention(BODY, "cand-1002", "his patronage", 40)
add_mention(BODY, "cand-10466", "grëat cultural revival", 40, "OCR diacritic is a scan artifact; the page image reads ‘great’. Hopes remain attributed to Farsetti’s contemporaries.")
add_mention(BODY, "cand-1002", "he alone", 40)
add_mention(BODY, "cand-1002", "he remains a shadowy character", 40)
add_mention(BODY, "cand-1002", "his apparent aims", 40)
add_mention(BODY, "cand-1002", "his achievements", 40)
add_mention(BODY, "cand-1002", "He", 41, "Pronoun refers to Farsetti.")
add_mention(BODY, "cand-1642", "Andrea Memmo", 41)
add_mention(BODY, "cand-10467", "a public service designed to benefit the community", 41)

# P.364 notes 1–2 belong to this source section. Notes 3–6 belong to the adjacent sec_ii segment.
add_mention(NOTES, "cand-10172", "Archivio di Stato", 51)
add_mention(NOTES, "cand-3401", "Venice", 51)
add_mention(NOTES, "cand-10464", "Inquisitori di Stato", 51)
add_mention(NOTES, "cand-10462", "Busta 540", 51, "Archival reference within the cited Inquisitori di Stato record.")
add_mention(NOTES, "cand-10462", "30 Maggio 1792", 51)
add_mention(NOTES, "cand-10463", "Moschini", 52)
add_mention(NOTES, "cand-10463", "1806, II, p. 114", 52)

add_statement(
    "st-chp15-p364-tommaso-brother-of-daniele", BODY, "cand-1013", "cand-1001",
    "brother_of_daniele_farsetti", 39, 39,
    "Haskell identifies Tommaso Giuseppe Farsetti as Daniele Farsetti’s brother.",
    mentioned=["cand-1013", "cand-1001"], relation_candidate=True)
add_statement(
    "st-chp15-p364-tommaso-preferred-books-manuscripts", BODY, "cand-1013", "cand-10465",
    "more_interested_in_books_and_manuscripts_than_art", 39, 39,
    "Haskell says Tommaso Giuseppe was more interested in his fine collection of books and manuscripts than in works of art.",
    qualification="The collection’s contents, name and institutional status are not supplied.", mentioned=["cand-1013", "cand-10465"])
add_statement(
    "st-chp15-p364-tommaso-loyal-to-family-tradition", BODY, "cand-1013", "cand-10431",
    "remained_loyal_to_farsetti_family_tradition_and_wrote_account", 39, 39,
    "Haskell says Tommaso Giuseppe remained loyal to the Farsetti family tradition and wrote an exalted account of it.",
    qualification="The account may be the family history cited at p.362 note 1, but the passage does not explicitly reidentify that work.",
    mentioned=["cand-1013", "cand-10431", "cand-10443"])
add_statement(
    "st-chp15-p364-tommaso-rueful-about-filippo-costs", BODY, "cand-1013", "cand-1002",
    "account_of_filippo_collecting_conveyed_ruefulness_about_expense", 39, 39,
    "Haskell says a note of ruefulness enters when Tommaso Giuseppe describes Filippo’s collecting and the enormous expense involved.",
    qualification="This characterizes Tommaso’s account; it does not provide a quantified total beyond the p.363 report.",
    mentioned=["cand-1013", "cand-1002"])
add_statement(
    "st-chp15-p364-tommaso-embittered-by-nephew", BODY, "cand-1013", "cand-1000",
    "last_years_embittered_by_nephew_anton_francesco_extravagance", 39, 39,
    "Haskell says the last years of Tommaso Giuseppe’s life were embittered by the dissipated extravagance of his nephew Anton Francesco.",
    qualification="The source provides no further description of the extravagance in this passage.", mentioned=["cand-1013", "cand-1000"])
add_statement(
    "st-chp15-p364-tommaso-denounced-anton-francesco", BODY, "cand-1013", "cand-1000",
    "denounced_nephew_anton_francesco_to_inquisitors", 39, 39,
    "Haskell says Tommaso Giuseppe denounced Anton Francesco to the Inquisitors.",
    qualification="P.364 note 1 cites an Inquisitori di Stato record; the record itself was not consulted.",
    mentioned=["cand-1013", "cand-1000", "cand-10464"], relation_candidate=True,
    **footnote(1, 51, 39, ["st-chp15-p364-note1-inquisitors-record"]))
add_statement(
    "st-chp15-p364-property-finally-broken-up-and-sold", BODY, "cand-10431", None,
    "denunciation_to_no_avail_property_broken_up_and_collections_sold_early_19c", 39, 39,
    "Haskell says the denunciation was to no avail and that in the first years of the nineteenth century the property was broken up and the collections sold, to the indignation of Venetian scholars.",
    qualification="The sale date is expressed only as the first years of the century; no specific year or inventory is inferred.",
    mentioned=["cand-10431", "cand-1005", "cand-1006"],
    **footnote(2, 52, 39, ["st-chp15-p364-note2-moschini"]))
add_statement(
    "st-chp15-p364-canova-only-important-artist-emerged-venice", BODY, "cand-0532", "cand-3401",
    "only_important_artist_to_emerge_from_venice_at_end_of_18c", 40, 40,
    "Haskell says Canova was the only important artist to emerge from Venice at the end of the eighteenth century.",
    qualification="This is Haskell’s evaluative characterization of importance and period, not an exhaustive census.", mentioned=["cand-0532", "cand-3401"])
add_statement(
    "st-chp15-p364-retrospective-farsetti-influence-negligible-or-deleterious", BODY, "cand-1002", None,
    "influence_seems_in_retrospect_negligible_or_deleterious", 40, 40,
    "Haskell says Farsetti’s influence seems in retrospect to have been negligible or deleterious.",
    qualification="Preserves ‘seems in retrospect’ and Haskell’s alternatives; this is not an unqualified causal finding.", mentioned=["cand-1002"])
add_statement(
    "st-chp15-p364-contemporaries-hoped-cultural-revival", BODY, "cand-1002", "cand-10466",
    "contemporaries_based_hopes_for_cultural_revival_on_farsetti_patronage", 40, 40,
    "Haskell says Farsetti’s contemporaries thought differently and based their hopes for a great cultural revival on his patronage.",
    qualification="The OCR diacritic in ‘grëat’ is not in the print; the page image reads ‘great’. The hopes are attributed to contemporaries.",
    mentioned=["cand-1002", "cand-10466"])
add_statement(
    "st-chp15-p364-farsetti-example-as-nobility-withdrew", BODY, "cand-1002", None,
    "held_up_as_example_when_nobility_no_longer_supported_arts_traditionally", 40, 40,
    "Haskell says the nobility was no longer playing its traditional role in supporting the arts and Farsetti alone was held up as an example in many poems and speeches.",
    qualification="The passage does not identify the poems or speeches.", mentioned=["cand-1002"])
add_statement(
    "st-chp15-p364-farsetti-shadowy-aims-more-interesting-than-achievements", BODY, "cand-1002", None,
    "remained_shadowy_character_more_interesting_for_apparent_aims_than_achievements", 40, 40,
    "Haskell calls Farsetti a shadowy character, more interesting for his apparent aims than for his achievements.",
    qualification="Retains ‘apparent’ and records an authorial assessment.", mentioned=["cand-1002"])
add_statement(
    "st-chp15-p364-farsetti-midway-between-patron-models", BODY, "cand-1002", "cand-1642",
    "stood_between_self_sufficient_past_patrons_and_memmo_public_service_model", 41, 41,
    "Haskell places Farsetti midway between the self-sufficient and magnificent patrons of the past and newer patrons exemplified by Andrea Memmo, who saw support for the arts as a public service benefiting the community.",
    qualification="This is Haskell’s framing of contrasting patronage models, not a claim that all patrons belonged to two fixed groups.",
    mentioned=["cand-1002", "cand-1642", "cand-10467"])

add_statement(
    "st-chp15-p364-note1-inquisitors-record", NOTES, "cand-10462", None,
    "note_cites_inquisitori_di_stato_record_for_1792_denunciation", 51, 51,
    "P.364 note 1 cites an Inquisitori di Stato record, Busta 540, Annotazioni, page 164, dated 30 May 1792.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The record was not independently consulted.", mentioned=["cand-10462", "cand-10172", "cand-10464"],
    cited_source_independently_consulted=False)
add_statement(
    "st-chp15-p364-note2-moschini", NOTES, None, "cand-10463",
    "note_cites_moschini_1806_volume_ii_page114", 52, 52,
    "P.364 note 2 cites Moschini (1806), volume II, page 114.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The cited page and full bibliographic title were not independently checked.",
    mentioned=["cand-10463"], cited_source_independently_consulted=False)

new_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p364-")}
expected_statement_count = 15
if len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.364 statements, got {len(new_statement_ids)}")

previous_partial_statement = statement_by_id[PREVIOUS_PARTIAL]
previous_partial_statement["qualifiers"]["cross_reference_statement_ids"] = []
previous_partial_statement["qualifiers"]["cross_reference_text"] = (
    "P.363 L35 ends ‘continued the’; p.364 L39 completes it as ‘patronage of contemporary artists.’"
)
coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L27-36",
    "note": "Printed p.363 body is now closed by p.364 L39, which completes Daniele Farsetti’s continued patronage. Footnote 2 at OCR L36 remains linked to the L28 quotation. S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L38-41",
    "note": "Printed p.364 checked against CHP-15.pdf physical p.4. Completes the Daniele Farsetti patronage sentence and processes the end of Haskell’s Farsetti discussion. Notes 1–2 at consolidated L51–52 are linked. OCR corrections are recorded only in S2; Andrea Memmo’s adjacent section begins in the separate sec_ii source and remains queued.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L44-52",
    "note": "P.362 notes 1–2 (L44–45), p.363 notes 1, 3–6 (L46–50), and p.364 notes 1–2 (L51–52) are processed and linked. P.364 notes 3–6 (L53–56) belong to the adjacent Andrea Memmo sec_ii segment and remain pending until that body is read.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA,
    "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "updated_statements": [PREVIOUS_PARTIAL],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
    "printed_page": 364,
    "pdf_physical_page": 4,
}
if args.apply:
    touched = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path in touched]
    collision = next((backup for _, backup in backups if backup.exists()), None)
    if collision:
        raise SystemExit(f"backup already exists: {collision.name}")
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions + planned_mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps(result, ensure_ascii=False, indent=2))
