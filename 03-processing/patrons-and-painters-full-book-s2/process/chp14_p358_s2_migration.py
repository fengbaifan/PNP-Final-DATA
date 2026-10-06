"""Controlled S2 migration for printed p.358; dry-run by default."""
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
BODY_PREV = "chp-14:14_CHP-14_intro:l107-116"
BODY = "chp-14:14_CHP-14_intro:l118-124"
BODY_NEXT = "chp-14:14_CHP-14_intro:l126-137"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BACKUP_SUFFIX = ".bak-s2-chp14-p358-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.358 S2 migration")
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
if hashlib.sha256(source_bytes).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if hashlib.sha256(pdf_bytes).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in [
    (115, "as his letters, with their description of"),
    (119, "the work were soon published, the idea gained ground"),
    (120, "Grand Canal in Venice.1"),
    (121, "Flemish artist"),
    (121, "Prospero Pesci and Mauro Tesi"),
    (122, "Caffariello"),
    (123, "the parallel - creations of Piranesi"),
    (124, "But Algarotti fully realised"),
    (208, "Blainville, I, p. 492"),
    (209, "Letter from Berlin dated 5 September 1741 in Treviso, MSS. 1256"),
    (210, "MSS. Hercolani 207"),
    (211, "Opere, VIH, p. 95"),
    (212, "ibid., p. roo"),
    (213, "ibid., pp. 104,109, in."),
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
if (coverage_by_id[BODY_PREV]["migration_status"] != "partial"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "partial"
        or coverage_by_id[NOTES]["source_line_ranges"] != "L169-207"):
    raise SystemExit("S2 coverage preconditions changed")
previous_statement_id = "st-chp14-p357-theoretical-scheme-for-view-commission-partial"
if previous_statement_id not in statement_by_id:
    raise SystemExit("missing open p.357 cross-page statement")
if statement_by_id[previous_statement_id]["predicate"] != "first_to_draw_up_theoretical_scheme_for_such_commission_partial":
    raise SystemExit("p.357 continuation was already revised")

new_candidates = [
    ("cand-10380", "Algarotti’s letters describing the proposed Canaletto view commission (p.357–358)", "archive", BODY_PREV, 115,
     "An unidentified plural body of Algarotti letters describing the proposed view commission; no dates, addressees, individual titles, or number of letters are supplied."),
    ("cand-10381", "Unidentified Flemish artist employed by Algarotti in Berlin in 1741 (p.358)", "person", BODY, 121,
     "The artist is described as Flemish and long established in Berlin; Haskell supplies no name or further identity evidence."),
    ("cand-10382", "Francesco Algarotti’s letter from Berlin dated 5 September 1741 (Treviso MSS. 1256; p.358 n.2)", "archive", NOTES, 209,
     "Haskell quotes the letter for the unnamed Flemish painter and Algarotti’s chosen subjects; the manuscript was not consulted."),
    ("cand-10383", "Treviso MSS. 1256 (repository not specified in p.358 n.2)", "archive", NOTES, 209,
     "The note gives Treviso and manuscript number only; do not choose between institution candidates cand-9450 and cand-10251."),
    ("cand-10384", "Picturesque as an artistic criterion in Algarotti’s account (p.358)", "term", BODY, 119,
     "Haskell repeatedly uses the picturesque to characterize Algarotti’s judgment and commissions; preserve it as a concept in this passage, not as an externally defined doctrine."),
    ("cand-10385", "Palladian architecture discussed in Algarotti’s explanation (p.358)", "term", BODY, 119,
     "The passage concerns Algarotti’s attitude to Palladian architecture; keep the concept distinct from Palladio’s specific Rialto plans and the proposed Canaletto view."),
    ("cand-10386", "Architectural capricci as a pictorial genre (p.357–358)", "term", BODY_PREV, 114,
     "The passage names architectural capricci as a kind of painting and links the p.358 phrase ‘this type of painting’ to the genre under discussion; no particular capriccio is identified."),
    ("cand-10387", "Algarotti’s library of archaeological books (p.358)", "", BODY, 121,
     "Haskell describes a private library used to guide architectural details, but gives no title or inventory. Type remains undecided because the current taxonomy has no clear personal-library collection type."),
    ("cand-10388", "Strada Balbi in Genoa (p.358)", "place", BODY, 119,
     "Street named in Algarotti’s comparison of picturesque urban views; no historical street identity or present alignment is independently verified."),
    ("cand-10389", "Strada Nuova in Genoa (p.358)", "place", BODY, 119,
     "Street named in Algarotti’s comparison of picturesque urban views; no historical street identity or present alignment is independently verified."),
    ("cand-10390", "Blainville, volume I, page 492 (citation locator in p.358 n.1)", "archive", NOTES, 208,
     "Citation locator for Blainville’s reported reaction to the mixture; title, edition, and cited page were not independently consulted."),
    ("cand-10391", "MSS. Hercolani 207 at Biblioteca Comunale, Bologna (p.358 n.3)", "archive", NOTES, 210,
     "Manuscript reference named by Haskell among sources for the discussion of Pesci and Tesi; manuscript and catalogue were not consulted."),
    ("cand-10392", "Introduction to Raccolta di disegni originali di Mauro Tesi (citation in p.358 n.3)", "archive", NOTES, 210,
     "Haskell points to the introduction as a source on Tesi; publication details and the cited introduction were not independently checked."),
    ("cand-10393", "Opere, volume VIII, pages 104, 109, and 111 (locator in p.358 n.6)", "archive", NOTES, 213,
     "Citation locator for Haskell’s Piranesi comparison; the edition and cited pages were not independently consulted."),
    ("cand-10394", "Caffariello (name in Algarotti’s composer analogy, p.358)", "person", BODY, 122,
     "Named as the singer for whom a composer provides bare elements of an aria; retain the source form and do not resolve identity in S2."),
    ("cand-10395", "Unidentified rough sketches by Algarotti for Pesci and Tesi (p.358)", "work", BODY, 121,
     "Haskell says Algarotti often directed Pesci and Tesi to paint from his rough sketches; no individual sketch, date, or title is identified."),
    ("cand-10396", "Landscapes of ruins and architecture commissioned from an unidentified Flemish painter in Berlin (1741; p.358)", "work", BODY, 121,
     "The body and note describe several unnamed landscapes with ruins, aqueducts, bridges, and buildings; do not invent titles, count, or surviving objects."),
]
max_existing_id = max(int(cid.split("-")[1]) for cid in candidate_by_id)
if max_existing_id != 10379:
    raise SystemExit(f"candidate sequence changed; expected max cand-10379, found cand-{max_existing_id}")
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

segment_bounds = {BODY_PREV: (107, 116), BODY: (118, 124), NOTES: (168, 220)}
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
    mention_id = f"m-chp14-p358-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(pos), "end_char": str(end), "note": note,
    })
    mention_counter += 1


# Close p.357's first clause and carry its letter-publication continuation into p.358.
add_mention(BODY_PREV, "cand-10380", "his letters")
add_mention(BODY_PREV, "cand-10386", "Architectural capricci")

# P.358 body entities and anaphoric/descriptive anchors.
add_mention(BODY, "cand-0500", "the work")
add_mention(BODY, "cand-10386", "this type of painting")
add_mention(BODY, "cand-0050", "Algarotti")
add_mention(BODY, "cand-10385", "Palladian architecture")
add_mention(BODY, "cand-0059", "Algarotti")
add_mention(BODY, "cand-2816", "Winckelmann")
add_mention(BODY, "cand-10384", "picturesque")
add_mention(BODY, "cand-10388", "Strada Balbi")
add_mention(BODY, "cand-10389", "Strada Nuova")
add_mention(BODY, "cand-1131", "Genoa")
add_mention(BODY, "cand-6320", "the Corso")
add_mention(BODY, "cand-4490", "Rome")
add_mention(BODY, "cand-8178", "Grand Canal")
add_mention(BODY, "cand-2719", "Venice")
add_mention(BODY, "cand-10384", "picturesque")
add_mention(BODY, "cand-3906", "Berlin")
add_mention(BODY, "cand-10381", "Flemish artist")
add_mention(BODY, "cand-10384", "picturesque")
add_mention(BODY, "cand-10396", "fine ruins of ancient cities, aqueducts, bridges and other buildings")
add_mention(BODY, "cand-3461", "Italy")
add_mention(BODY, "cand-10384", "picturesque")
add_mention(BODY, "cand-3398", "Bologna")
add_mention(BODY, "cand-1887", "Prospero Pesci")
add_mention(BODY, "cand-2551", "Mauro Tesi")
add_mention(BODY, "cand-10395", "his own rough sketches")
add_mention(BODY, "cand-10387", "his fine library of archaeological books")
add_mention(BODY, "cand-1887", "Pesci")
add_mention(BODY, "cand-10394", "Caffariello")
add_mention(BODY, "cand-2549", "Teniers")
add_mention(BODY, "cand-2820", "Wouwermans")
add_mention(BODY, "cand-2754", "Vernet")
add_mention(BODY, "cand-1827", "Pannini")
add_mention(BODY, "cand-10384", "the picturesque")
add_mention(BODY, "cand-1938", "Piranesi")
add_mention(BODY, "cand-2551", "Tesi")
add_mention(BODY, "cand-1887", "Pesci")

# P.358 notes 1-6, retaining cited-source and repository uncertainty.
add_mention(NOTES, "cand-0378", "Blainville")
add_mention(NOTES, "cand-10390", "I, p. 492")
add_mention(NOTES, "cand-10382", "Letter from Berlin dated 5 September 1741")
add_mention(NOTES, "cand-9209", "Treviso")
add_mention(NOTES, "cand-10383", "MSS. 1256")
add_mention(NOTES, "cand-10229", "Opere")
add_mention(NOTES, "cand-7386", "Biblioteca Comunale")
add_mention(NOTES, "cand-3398", "Bologna")
add_mention(NOTES, "cand-10391", "MSS. Hercolani 207")
add_mention(NOTES, "cand-10392", "Raccolta di disegni originali")
add_mention(NOTES, "cand-2551", "Mauro Tesi")
add_mention(NOTES, "cand-10375", "Opere, VIH, p. 95", "OCR reads VIH; p.358 print reads VIII.")
add_mention(NOTES, "cand-10375", "ibid., p. roo", "OCR reads roo; p.358 print reads 100.")
add_mention(NOTES, "cand-10393", "ibid., pp. 104,109, in.", "OCR reads in; p.358 print reads 111.")

unmentioned_new_candidates = {row[0] for row in new_candidates} - {row["candidate_id"] for row in planned_mentions}
if unmentioned_new_candidates:
    raise SystemExit(f"new candidates without an S2 mention anchor: {sorted(unmentioned_new_candidates)}")


def quote(segment_id, line_start, line_end):
    return "\n".join(source_lines[line_start - 1:line_end])


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", speaker="Haskell", qualification="",
                  mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 358, "pdf_physical_page": 12,
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


def footnote(marker, note_lines, statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": note_lines, "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_note_statement_ids": list(statement_ids),
    }


# P.357 L115 clause is complete; p.358 carries the separate publication/attribution clause.
previous = statement_by_id[previous_statement_id]
previous["predicate"] = "first_to_draw_up_theoretical_scheme_for_such_commission"
previous["qualifiers"].update({
    "claim": "Haskell says Algarotti was the first to draw up a theoretical scheme for such a commission.",
    "qualification": "The p.357 clause is complete. Its following clause about publication of Algarotti’s letters and the resulting attribution is recorded separately from p.358 L119; no claim is made that Algarotti invented architectural capriccio painting.",
    "mentioned_candidate_ids": ["cand-0044", "cand-0500", "cand-10380"],
    "cross_reference_segments": [BODY],
    "cross_reference_text": "p.357 L115 continues at p.358 L119; the publication and resulting attribution are represented by st-chp14-p358-letters-attribution-to-type.",
})

# Body statements: claims, relationships, and analytical judgments remain attributed to Haskell.
add_statement(
    "st-chp14-p358-letters-attribution-to-type", BODY, "cand-10380", "cand-10386",
    "published_letters_contributed_to_attribution_of_painting_type_to_algarotti", 119, 119,
    "Haskell says Algarotti’s letters describing the proposed work were soon published, after which the idea gained ground that he was responsible for this type of painting.",
    qualification="The letters are not individually identified. This is Haskell’s report about an attribution gaining currency, not proof that Algarotti originated the genre; the scope of ‘this type’ relative to architectural capricci and the specific Canaletto view remains open.",
    mentioned=["cand-10380", "cand-0500", "cand-10386"],
    cross_reference_segments=[BODY_PREV],
    cross_reference_text="p.357 L114–115 names architectural capricci and the proposed commission; the publication clause closes at p.358 L119.",
    candidate_identity_questions=[
        {"candidate_id": "cand-10386", "issue": "P.358 ‘this type of painting’ may refer to the architectural view/capriccio category, but its scope is not explicitly defined."},
        {"candidate_id": "cand-0500", "issue": "The specific Canaletto view is the context for the claim, but the phrase ‘this type’ should not be reduced to that individual view."},
    ])

add_statement(
    "st-chp14-p358-algarotti-attitude-to-palladian-architecture", BODY, "cand-0050", "cand-10385",
    "explanation_reveals_attitude_to_palladian_architecture", 119, 119,
    "Haskell says Algarotti’s explanation of the picture is revealing of his attitude to Palladian architecture and characteristic of his outlook.",
    qualification="This is Haskell’s interpretation of the explanation, not a direct statement by Algarotti.",
    mentioned=["cand-0050", "cand-10385"])

add_statement(
    "st-chp14-p358-frivolous-outlook-and-neoclassical-reform", BODY, "cand-0059", "cand-2816",
    "contrasted_fanciful_outlook_with_reforming_neoclassicism", 119, 119,
    "Haskell characterizes Algarotti’s outlook as essentially frivolous and lacking the reforming passion he associates with Winckelmann and neo-classical theorists.",
    qualification="The contrast is Haskell’s characterization; it does not summarize all of Algarotti’s or Winckelmann’s thought.",
    mentioned=["cand-0059", "cand-2816"])

add_statement(
    "st-chp14-p358-regularity-and-city-view-comparison", BODY, "cand-0050", "cand-10384",
    "judged_genoa_streets_less_picturesque_than_rome_and_venice_routes", 119, 120,
    "Haskell reports that Algarotti considered excessive regularity undesirable and Strada Balbi and Strada Nuova in Genoa less picturesque than the Corso in Rome or the Grand Canal in Venice.",
    qualification="This is a reported aesthetic comparison, not an objective ranking of the streets or a claim about their present-day appearance.",
    mentioned=["cand-0050", "cand-10384", "cand-10388", "cand-10389", "cand-1131", "cand-6320", "cand-4490", "cand-8178", "cand-2719"],
    relation_candidate=True, **footnote(1, "L208", ["st-chp14-p358-note1-blainville-report"]))

add_statement(
    "st-chp14-p358-picturesque-criterion", BODY, "cand-0076", "cand-10384",
    "judged_landscape_and_architectural_painting_from_picturesque_point_of_view", 120, 120,
    "Haskell says Algarotti had consistently judged landscape and architectural paintings from a picturesque point of view.",
    qualification="‘Always’ follows Haskell’s wording and is not expanded into a claim about every painting Algarotti encountered.",
    mentioned=["cand-0076", "cand-10384"])

add_statement(
    "st-chp14-p358-employed-flemish-artist-in-berlin", BODY, "cand-0065", "cand-10381",
    "employed_flemish_artist_in_berlin_by_1741", 120, 121,
    "Haskell says that in Berlin in 1741 Algarotti had employed a Flemish artist who had lived there for many years.",
    qualification="The painter is unnamed. The cited letter is reproduced in p.358 note 2 but was not independently consulted.",
    mentioned=["cand-0065", "cand-3906", "cand-10381"], relation_candidate=True,
    **footnote(2, "L209", ["st-chp14-p358-note2-berlin-letter-source"]))

add_statement(
    "st-chp14-p358-flemish-painter-style-description", BODY, "cand-10381", None,
    "described_flemish_painter_as_having_italian_dash_and_brio", 121, 121,
    "In Algarotti’s quoted description, the painter’s execution is his own, without the dry finish Algarotti associates with Flemish painters, but with Italian dash and brio.",
    text_layer="letter quotation translated and reproduced by Haskell",
    speaker="Algarotti, as quoted by Haskell",
    qualification="The letter is cited in note 2; neither the manuscript nor the translation was independently checked.",
    mentioned=["cand-10381"], **footnote(2, "L209", ["st-chp14-p358-note2-berlin-letter-source"]))

add_statement(
    "st-chp14-p358-flemish-painter-selected-subjects", BODY, "cand-0065", "cand-10396",
    "selected_subjects_for_berlin_landscape_paintings", 121, 121,
    "Haskell says the unnamed Flemish painter painted subjects chosen by Algarotti: ruins of ancient cities, aqueducts, bridges, and other buildings, with figures and soldiers dressed in the Roman manner.",
    qualification="The works are described collectively; no titles, exact count, or surviving objects are identified.",
    mentioned=["cand-0065", "cand-10396"], relation_candidate=True,
    **footnote(2, "L209", ["st-chp14-p358-note2-berlin-letter-source"]))

add_statement(
    "st-chp14-p358-later-architectural-fantasies", BODY, "cand-0058", None,
    "devoted_last_years_increasingly_to_architectural_fantasies", 121, 121,
    "Haskell says that after returning to Italy Algarotti devoted the last years of his life increasingly to similar architectural fantasies.",
    qualification="The account is qualitative and does not date every commission or imply that all later works belonged to one series.",
    mentioned=["cand-0058", "cand-10384"])

add_statement(
    "st-chp14-p358-classical-building-structure", BODY, "cand-0058", None,
    "attended_to_structure_of_classical_buildings_in_pictures", 121, 121,
    "Haskell says Algarotti also paid considerable attention to the structure of classical buildings he wanted included in his pictures.",
    qualification="No individual building or picture is identified in this sentence.",
    mentioned=["cand-0058"])

add_statement(
    "st-chp14-p358-moved-to-bologna-and-met-pesci-tesi", BODY, "cand-0066", None,
    "met_pesci_and_tesi_after_moving_to_bologna_in_1756", 121, 121,
    "Haskell says Algarotti moved to Bologna in 1756 and there came across Prospero Pesci and Mauro Tesi.",
    qualification="The wording ‘came across’ is retained; the passage does not date the start of each relationship.",
    mentioned=["cand-0066", "cand-3398", "cand-1887", "cand-2551"])

add_statement(
    "st-chp14-p358-employed-pesci", BODY, "cand-0058", "cand-1887",
    "employed_pesci_to_realize_his_ideas", 121, 121,
    "Haskell says Algarotti employed Pesci to give expression to his ideas.",
    qualification="This is an employment/commission relationship as reported by Haskell; no single contract or picture is identified here.",
    mentioned=["cand-0058", "cand-1887"], relation_candidate=True,
    **footnote(3, "L210", ["st-chp14-p358-note3-opere-letters", "st-chp14-p358-note3-hercolani-manuscript", "st-chp14-p358-note3-raccolta-introduction"]))

add_statement(
    "st-chp14-p358-employed-tesi", BODY, "cand-0058", "cand-2551",
    "employed_tesi_to_realize_his_ideas", 121, 121,
    "Haskell says Algarotti employed Tesi to give expression to his ideas.",
    qualification="This is an employment/commission relationship as reported by Haskell; no single contract or picture is identified here.",
    mentioned=["cand-0058", "cand-2551"], relation_candidate=True,
    **footnote(3, "L210", ["st-chp14-p358-note3-opere-letters", "st-chp14-p358-note3-hercolani-manuscript", "st-chp14-p358-note3-raccolta-introduction"]))

add_statement(
    "st-chp14-p358-directed-pesci-from-rough-sketches", BODY, "cand-0058", "cand-10395",
    "directed_pesci_to_paint_from_algarotti_rough_sketches", 121, 121,
    "Haskell says Algarotti often directed Pesci to paint pictures from Algarotti’s own rough sketches.",
    qualification="No individual sketch or resulting picture is named; the plural and ‘often’ are preserved.",
    mentioned=["cand-0058", "cand-1887", "cand-10395"], relation_candidate=True,
    **footnote(3, "L210", ["st-chp14-p358-note3-opere-letters", "st-chp14-p358-note3-hercolani-manuscript", "st-chp14-p358-note3-raccolta-introduction"]))

add_statement(
    "st-chp14-p358-directed-tesi-from-rough-sketches", BODY, "cand-0058", "cand-10395",
    "directed_tesi_to_paint_from_algarotti_rough_sketches", 121, 121,
    "Haskell says Algarotti often directed Tesi to paint pictures from Algarotti’s own rough sketches.",
    qualification="No individual sketch or resulting picture is named; the plural and ‘often’ are preserved.",
    mentioned=["cand-0058", "cand-2551", "cand-10395"], relation_candidate=True,
    **footnote(3, "L210", ["st-chp14-p358-note3-opere-letters", "st-chp14-p358-note3-hercolani-manuscript", "st-chp14-p358-note3-raccolta-introduction"]))

add_statement(
    "st-chp14-p358-classical-building-as-main-element", BODY, "cand-0058", None,
    "described_classical_building_as_main_element_of_composition", 121, 121,
    "Haskell says the main element in these compositions was nearly always a classical building, real or reconstructed.",
    qualification="‘Nearly always’ is retained; the passage does not make this a rule without exceptions.",
    mentioned=["cand-0058"])

add_statement(
    "st-chp14-p358-library-guided-building-details", BODY, "cand-0058", "cand-10387",
    "used_archaeological_library_to_specify_building_appearance", 121, 121,
    "Haskell says Algarotti drew on his archaeological books to instruct artists about a building’s appearance down to minute details.",
    qualification="The private library’s type remains undecided; no book titles, catalogue, or individual instruction is supplied.",
    mentioned=["cand-0058", "cand-10387"], relation_candidate=True)

add_statement(
    "st-chp14-p358-fanciful-background-as-foil", BODY, "cand-0058", "cand-10384",
    "set_fanciful_background_against_buildings_pedantic_accuracy", 121, 121,
    "Haskell says the fanciful background was intended to act as a foil to the building’s pedantic accuracy.",
    qualification="This describes Haskell’s account of the compositional principle, not a universal rule for every work.",
    mentioned=["cand-0058", "cand-10384"])

add_statement(
    "st-chp14-p358-insisted-on-picturesque-element", BODY, "cand-0076", "cand-10384",
    "repeatedly_insisted_on_picturesque_element", 121, 121,
    "Haskell says Algarotti repeatedly insisted on the picturesque element.",
    qualification="The phrase is Haskell’s synthesis of the preceding account.",
    mentioned=["cand-0076", "cand-10384"])

add_statement(
    "st-chp14-p358-pesci-sketch-composer-analogy", BODY, "cand-0058", "cand-1887",
    "compared_sketch_assistance_to_composer_providing_aria_elements", 122, 122,
    "In a letter to Pesci, Algarotti compares the help offered by his sketch to a composer providing Caffariello with the bare elements of an aria.",
    text_layer="letter quotation reproduced by Haskell",
    speaker="Algarotti, as quoted by Haskell",
    qualification="The cited Opere page is identified in note 4; the letter and edition were not independently consulted. Caffariello’s identity is unresolved.",
    mentioned=["cand-0058", "cand-1887", "cand-10394"], relation_candidate=True,
    **footnote(4, "L211", ["st-chp14-p358-note4-pesci-letter-locator"]))

add_statement(
    "st-chp14-p358-pesci-instruction-on-varied-tones", BODY, "cand-0058", "cand-1887",
    "instructed_pesci_to_vary_tones_smoothly_and_abruptly", 122, 122,
    "In the same quoted letter, Algarotti tells Pesci to vary and break up tones, moving between them smoothly and abruptly and adding the charms and attractions of art.",
    text_layer="letter quotation reproduced by Haskell",
    speaker="Algarotti, as quoted by Haskell",
    qualification="This is the wording quoted by Haskell, not independent consultation of the letter.",
    mentioned=["cand-0058", "cand-1887"], relation_candidate=True,
    **footnote(4, "L211", ["st-chp14-p358-note4-pesci-letter-locator"]))

for suffix, artist_id, artist_name in [
    ("teniers", "cand-2549", "Teniers"),
    ("wouwermans", "cand-2820", "Wouwermans"),
    ("vernet", "cand-2754", "Vernet"),
    ("pannini", "cand-1827", "Pannini"),
]:
    add_statement(
        f"st-chp14-p358-recommended-study-{suffix}", BODY, "cand-0076", artist_id,
        "recommended_study_of_painter", 122, 123,
        f"Haskell says Algarotti recommended studying {artist_name} as a model for the desired combination of styles.",
        qualification="The recommendation is reported in Haskell’s account; it is not evidence of a formal teacher-pupil relationship.",
        mentioned=["cand-0076", artist_id], relation_candidate=True,
        **footnote(5, "L212", ["st-chp14-p358-note5-pesci-letter-locator"]))

add_statement(
    "st-chp14-p358-italian-and-flemish-combination", BODY, "cand-0076", None,
    "combined_italian_draughtsmanship_with_flemish_taste", 123, 123,
    "In the quoted formulation, Algarotti says the desired result would combine the nobility of Italian draughtsmanship with Flemish taste and flavour.",
    text_layer="letter quotation reproduced by Haskell",
    speaker="Algarotti, as quoted by Haskell",
    qualification="The statement is a quoted formulation of an aesthetic aim, not evidence that every commissioned work achieved it.",
    mentioned=["cand-0076"], **footnote(5, "L212", ["st-chp14-p358-note5-pesci-letter-locator"]))

add_statement(
    "st-chp14-p358-piranesi-parallel-and-admiration", BODY, "cand-0076", "cand-1938",
    "compared_didactic_picturesque_combination_to_piranesi_and_admired_him", 123, 123,
    "Haskell says this combination of didacticism and the picturesque resembled Piranesi’s parallel creations in Rome, which Algarotti greatly admired.",
    qualification="This is Haskell’s comparison and report of admiration; the cited Opere pages were not independently consulted.",
    mentioned=["cand-0076", "cand-10384", "cand-1938", "cand-4490"],
    **footnote(6, "L213", ["st-chp14-p358-note6-opere-locator"]))

add_statement(
    "st-chp14-p358-limits-of-picturesque-invention-partial", BODY, "cand-0076", None,
    "recognized_limits_of_picturesque_invention_expected_from_architectural_painters_partial", 124, 124,
    "Haskell says Algarotti recognized limits to the picturesque invention he could expect from architectural painters such as Tesi and Pesci.",
    qualification="The sentence continues on p.359 L127 with Algarotti’s response to those limits; do not treat the p.358 clause as the complete account.",
    mentioned=["cand-0076", "cand-2551", "cand-1887"],
    cross_reference_segments=[BODY_NEXT],
    cross_reference_text="p.358 L124 continues at p.359 L127; the continuation is not migrated yet.")

# Footnote statements preserve the printed citation chain without claiming independent verification.
add_statement(
    "st-chp14-p358-note1-blainville-report", NOTES, "cand-0378", "cand-10390",
    "reported_blainville_disliked_mixture_but_admitted_some_found_it_attractive", 208, 208,
    "P.358 note 1 says Blainville disliked the mixture but admitted that some people found it attractive.",
    text_layer="Haskell’s citation summary", speaker="Blainville, as reported by Haskell",
    qualification="Blainville’s cited volume and page were not independently consulted.",
    mentioned=["cand-0378", "cand-10390"])

add_statement(
    "st-chp14-p358-note2-berlin-letter-source", NOTES, "cand-0065", "cand-10382",
    "cites_1741_berlin_letter_in_treviso_mss_1256", 209, 209,
    "P.358 note 2 identifies a letter from Berlin dated 5 September 1741 in Treviso MSS. 1256 and reproduces an Italian passage about an employed Flemish painter and subjects chosen by Algarotti.",
    text_layer="letter quotation reproduced in Haskell’s note",
    speaker="Algarotti, as quoted by Haskell",
    qualification="The manuscript was not consulted; the repository institution is not named in this note.",
    mentioned=["cand-0065", "cand-10382", "cand-9209", "cand-10383"],
    candidate_identity_questions=[
        {"candidate_id": "cand-9450", "issue": "P.358 n.2 says only Treviso MSS. 1256; it does not name Biblioteca Comunale or resolve the repository candidate."},
        {"candidate_id": "cand-10251", "issue": "P.358 n.2 says only Treviso MSS. 1256; keep distinct from institution-level citations until source/bibliography review."},
    ])

add_statement(
    "st-chp14-p358-note3-opere-letters", NOTES, None, "cand-10229",
    "points_to_many_algarotti_letters_published_in_opere", 210, 210,
    "P.358 note 3 points to many letters published in the Opere as sources for the discussion of Pesci and Tesi.",
    qualification="The editions and letters were not independently consulted.", mentioned=["cand-10229"])

add_statement(
    "st-chp14-p358-note3-hercolani-manuscript", NOTES, "cand-7386", "cand-10391",
    "cites_mss_hercolani_207_at_bologna_biblioteca_comunale", 210, 210,
    "P.358 note 3 cites MSS. Hercolani 207 at the Biblioteca Comunale in Bologna.",
    qualification="The manuscript and current repository catalogue were not consulted.",
    mentioned=["cand-7386", "cand-3398", "cand-10391"])

add_statement(
    "st-chp14-p358-note3-raccolta-introduction", NOTES, None, "cand-10392",
    "cites_introduction_to_raccolta_di_disegni_originali_di_mauro_tesi", 210, 210,
    "P.358 note 3 points especially to the introduction to the Raccolta di disegni originali di Mauro Tesi.",
    qualification="Publication details and the introduction were not independently checked.",
    mentioned=["cand-10392", "cand-2551"])

add_statement(
    "st-chp14-p358-note4-pesci-letter-locator", NOTES, None, "cand-10375",
    "cites_pesci_letter_at_opere_viii_page_95", 211, 211,
    "P.358 note 4 cites Opere VIII, page 95, for Algarotti’s letter to Pesci.",
    qualification="This locator falls within the letter pages 89–100 cited in p.357 note 7; the letter and volume were not independently consulted.",
    mentioned=["cand-10375"])

add_statement(
    "st-chp14-p358-note5-pesci-letter-locator", NOTES, None, "cand-10375",
    "cites_pesci_letter_at_opere_viii_page_100", 212, 212,
    "P.358 note 5 refers to page 100 of the same Opere VIII source cited in note 4.",
    qualification="The print reads 100; S0 OCR reads ‘roo’. The source was not independently consulted.",
    mentioned=["cand-10375"])

add_statement(
    "st-chp14-p358-note6-opere-locator", NOTES, None, "cand-10393",
    "cites_opere_viii_pages_104_109_111_for_piranesi_comparison", 213, 213,
    "P.358 note 6 cites Opere VIII, pages 104, 109, and 111, for the Piranesi comparison.",
    qualification="The print reads 111; S0 OCR reads ‘in’. The volume and pages were not independently consulted.",
    mentioned=["cand-10393"])

new_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp14-p358-")}
expected_note_ids = {
    1: ["st-chp14-p358-note1-blainville-report"],
    2: ["st-chp14-p358-note2-berlin-letter-source"],
    3: ["st-chp14-p358-note3-opere-letters", "st-chp14-p358-note3-hercolani-manuscript", "st-chp14-p358-note3-raccolta-introduction"],
    4: ["st-chp14-p358-note4-pesci-letter-locator"],
    5: ["st-chp14-p358-note5-pesci-letter-locator"],
    6: ["st-chp14-p358-note6-opere-locator"],
}
for marker, ids in expected_note_ids.items():
    for statement_id in ids:
        if statement_id not in new_statement_ids:
            raise SystemExit(f"missing statement for footnote {marker}: {statement_id}")

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L108-116",
    "note": "Printed p.357 read against CHP-14.pdf physical p.11. L108 closes p.356; footnote 4 at L116 is linked. The L115 scheme clause is complete; its publication/attribution continuation closes at p.358 L119. S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L119-124",
    "note": "Printed p.358 read against CHP-14.pdf physical p.12. L119 closes p.357 L115; L124 continues at p.359 L127. Notes 1–6 at L208–213 are linked; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-213",
    "note": "Printed notes through p.358 n.6 at L208–213 read against CHP-14.pdf physical p.12 and linked. Later page notes remain pending; S0 unchanged.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA,
    "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "updated_statements": [previous_statement_id],
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
    write_csv(coverage_path, coverage_fields, [coverage_by_id[row["segment_id"]] for row in coverage])

print(json.dumps(result, ensure_ascii=False, indent=2))
