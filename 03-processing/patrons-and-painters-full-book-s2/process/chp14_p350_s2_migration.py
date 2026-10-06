"""Controlled S2 migration for printed p.350 body and notes 1-3; dry-run by default."""
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
BODY_PREV = "chp-14:14_CHP-14_intro:l23-33"
BODY = "chp-14:14_CHP-14_intro:l35-44"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
BACKUP_SUFFIX = ".bak-s2-chp14-p350-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.350 S2 migration")
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
    36: "in 173 7 there is no evidence",
    37: "to prove such a feature of his career",
    39: "art gallery which was being formed by Augustus of Saxony.",
    40: "Padre Lodoli owned just such a collection.3",
    44: "He tried to base his",
    178: "To his brother Bonomo, 5 September 1741",
    179: "Opere, Vin, pp. 351-88.",
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
    raise SystemExit("p.349 body segment is not in the expected partial state")
if coverage_by_id[BODY]["disposition"] != "queued":
    raise SystemExit("p.350 body segment is not queued; refusing to overwrite")
if coverage_by_id[NOTES]["disposition"] != "reviewed" or coverage_by_id[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated chapter 14 notes segment is not in the expected partial state")

new_candidates = [
    ("cand-10264", "Unidentified portrait of Francesco Algarotti discussed in a 1741 letter", "work", 36,
     "A portrait was being painted of Algarotti and is evaluated in a letter quoted by Haskell; the painter, location, title, and present whereabouts are unspecified."),
    ("cand-10265", "Francesco Algarotti letter to Bonomo, 5 September 1741 (Treviso MSS. 1256)", "archive", 178,
     "Letter identified by recipient, date, and abbreviated Treviso shelfmark in p.350 note 1; the manuscript was not independently consulted."),
    ("cand-10266", "Opere, volume VIII, pages 351-388 (citation locator in p.350 note 2)", "archive", 179,
     "Citation locator printed as Opere, VIII, pp. 351-88; edition and cited pages were not independently checked."),
    ("cand-10267", "First rediscovery of the primitives in eighteenth-century collecting (Haskell's phrase)", "term", 39,
     "Haskell's interpretive label for collections of early-Italian works assembled as historical evidence and Renaissance precursors; preserve his qualification that this need not indicate a change in taste."),
    ("cand-10268", "Romantics as a later comparator for collecting early-Italian art", "term", 40,
     "Haskell invokes the Romantics as a later case in which collection-building would correspond to a change in taste."),
    ("cand-10269", "Padre Lodoli's collection of early-Italian works (details referred to Chapter 12)", "", 40,
     "The source says Lodoli owned such a collection and points to Chapter 12. The collection has no fitting current taxonomy type and no individual works are identified on p.350."),
    ("cand-10270", "Unnamed living artists considered for Algarotti's Dresden gallery scheme", "", 43,
     "The scheme proposed commissioning works by living artists but names no artists or completed commissions; retain the group and plan status without inventing endpoints."),
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

segment_bounds = {BODY: (35, 44), NOTES: (168, 220)}
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
                mention_id = f"m-chp14-p350-{mention_counter:04d}"
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
    matched = False
    for number in line_numbers:
        line = source_lines[number - 1]
        for form in forms:
            for match in re.finditer(rf"(?<![\w]){re.escape(form)}(?![\w])", line):
                matched = True
                start = segment_offsets[(segment_id, number)] + match.start()
                end = start + len(form)
                if any(seg == segment_id and cid == candidate_id and s == start and e == end
                       for seg, cid, s, e in occupied_same_candidate):
                    continue
                mention_id = f"m-chp14-p350-{mention_counter:04d}"
                if mention_id in mention_by_id:
                    raise SystemExit(f"mention ID already exists: {mention_id}")
                mentions.append({
                    "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                    "surface_form": form, "start_char": str(start), "end_char": str(end), "note": note,
                })
                mention_by_id[mention_id] = mentions[-1]
                occupied_same_candidate.add((segment_id, candidate_id, start, end))
                mention_counter += 1
    if not matched:
        raise SystemExit(f"pronouns not found in requested lines: {segment_id} {forms} {line_numbers}")


# Printed p.350 body references; keep index subentries and previously created candidates distinct until S3.
for item in [
    ("north of Europe", "cand-3594", [36]),
    ("Berlin", "cand-9073", [36]),
    ("Rembrandt", "cand-2117", [36]),
    ("Giorgione", "cand-1188", [36]),
    ("Venice", "cand-2719", [36, 37]),
    ("living artists", "cand-10270", [43]),
    ("Voltaire", "cand-2791", [36]),
    ("London", "cand-1422", [36]),
    ("Paris", "cand-4653", [36]),
    ("Newtonianismo", "cand-10258", [36]),
    ("Dresden", "cand-0947", [39]),
    ("Augustus", "cand-0151", [39]),
    ("Saxony", "cand-10256", [39]),
    ("art gallery", "cand-9091", [39]),
    ("gallery", "cand-9091", [39]),
    ("Algarotti", "cand-0075", [39, 40, 41]),
    ("the first rediscovery of the primitives", "cand-10267", [39]),
    ("the Renaissance", "cand-3578", [40]),
    ("Romantics", "cand-10268", [40]),
    ("Padre Lodoli", "cand-1411", [40]),
    ("such a collection", "cand-10269", [40]),
    ("Muratori", "cand-1717", [41]),
    ("a number of works by living artists", "cand-10270", [43]),
    ("the artists concerned", "cand-10270", [43]),
    ("Castiglione", "cand-0602", [44]),
    ("Claude", "cand-0767", [44]),
    ("Algarotti’s appraisal", "cand-0056", [44]),
    ("Venetian", "cand-2719", [44]),
]:
    surface, cid, lines, *note = item
    add_surface(BODY, cid, surface, lines, note=note[0] if note else "")

# Person coreference follows the p.350 index subentries most relevant to each passage.
add_pronouns(BODY, "cand-0056", ["he", "He", "him", "his"], [36, 37, 38, 44])
add_pronouns(BODY, "cand-0071", ["he", "his", "His"], [39])
add_pronouns(BODY, "cand-0075", ["He", "he", "his"], [40, 41])
add_pronouns(BODY, "cand-0072", ["he", "his"], [42, 43])
add_surface(BODY, "cand-2719", "native city", [36], note="In this chapter the native city is Venice; source wording retained.")
add_surface(BODY, "cand-0056", "his", [44], note="Algarotti's incomplete sentence continues onto p.351.")

add_surface(BODY, "cand-10264", "a portrait being painted of him", [36])
for item in [
    ("To his brother Bonomo", "cand-10265", [178]),
    ("5 September 1741", "cand-10265", [178]),
    ("Treviso, MSS. 1256", "cand-10251", [178]),
    ("Opere, Vin, pp. 351-88", "cand-10266", [179],
     "Source OCR reads Vin; the printed p.350 image reads VIII."),
]:
    surface, cid, lines, *note = item
    add_surface(NOTES, cid, surface, lines, note=note[0] if note else "")
add_surface(NOTES, "cand-0040", "Bonomo", [178])


def quote(start, end, exact):
    allowed = "\n".join(source_lines[start - 1:end])
    if exact not in allowed:
        raise SystemExit(f"statement quotation is not present in L{start}-L{end}: {exact[:90]!r}")
    return exact


def q(start, end, claim, layer, qualification, candidate_ids, **extra):
    out = {
        "source_line_start": start, "source_line_end": end, "printed_page": 350,
        "pdf_physical_page": 4, "claim": claim, "speaker": "Haskell",
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


link1 = {"footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L178",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p350-note1-letter"]}
link2 = {"footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L179",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p350-note2-opere"]}
link3 = {"footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L179",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p350-note3-chapter12"]}

add_statement("st-chp14-p350-rococo-influence-context", BODY, "cand-0056", None, "influence_contextualized",
    q(36, 36, "Haskell adds that indications suggest Algarotti drew inspiration from artists more appreciated in northern Europe than in Venice.",
      "authorial inference", "This continues the p.349 inference about French rococo and Algarotti's temperament; the wording presents indications, not a directly documented causal statement.",
      ["cand-0056", "cand-3594", "cand-2719"],
      cross_reference_segments=[BODY_PREV], cross_reference_text="completes st-chp14-p349-french-rococo-influence-inference"),
    quote(36, 36, "and there are many indications that he turned for inspiration to artists who were appreciated more in the north of Europe than in his native city."))
add_statement("st-chp14-p350-portrait-letter", BODY, "cand-0056", "cand-10264", "wrote_about_portrait",
    q(36, 36, "In 1741, while in Berlin, Algarotti wrote that a portrait being painted of him had a force between Rembrandt and Giorgione and was beautiful beyond measure.",
      "quoted correspondence reported by Haskell", "The Italian phrase is attributed to a letter; note 1 identifies it as addressed to Bonomo on 5 September 1741. The portrait's maker and location are unspecified.",
      ["cand-0056", "cand-9073", "cand-2117", "cand-1188", "cand-10264", "cand-10265"],
      speaker="Algarotti, as quoted by Haskell", relation_candidate=True, **link1),
    quote(36, 36, "Thus in Berlin in 1741 he was to write of a portrait being painted of him that it was ‘d’una forza tra il Rembrandt e il Giorgione bello bellissimo’.1"))
add_statement("st-chp14-p350-no-evidence-of-living-artist-contact", BODY, "cand-0056", None, "no_evidence_of_contact",
    q(36, 36, "Haskell says there is no evidence that Algarotti had particular contact with living artists during his 1737 Venice visit beyond looking carefully at their works.",
      "authorial evidence qualification", "Preserves the source's 'no evidence' formulation; it does not claim to prove that no contact occurred. OCR spaces the year as 173 7; print reads 1737.",
      ["cand-0056", "cand-2719"], ocr_corrections=[
          {"source_line": 36, "ocr": "173 7", "print": "1737", "basis": "CHP-14.pdf physical page 4."}]),
    quote(36, 36, "However, during his visit to Venice in 173 7 there is no evidence that he had any particular contact with living artists beyond looking carefully at their works."))
add_statement("st-chp14-p350-youth-status-and-associations", BODY, "cand-0056", None, "biographical_context",
    q(36, 37, "Haskell describes Algarotti at age 25 as still young, with Newtonianismo unpublished; despite friendship with Voltaire and social success in London and Paris, he was not wealthy, was not well known in Venice, and had not yet formed the powerful associations later useful to his career.",
      "authorial biographical synthesis", "All status judgments are attributed to Haskell and limited to the account of the 1737 Venice visit.",
      ["cand-0056", "cand-10258", "cand-2791", "cand-1422", "cand-4653", "cand-2719"]),
    quote(36, 37, "He was still only a young man of 25; his Newtonianismo had not yet been published; and though he had already made friends with Voltaire and been a social success in London and Paris, he was not very rich, he was not well known in\nVenice and he had not yet formed any of those powerful associations which were later to prove such a feature of his career and to be so very useful to him."))
add_statement("st-chp14-p350-importance-from-1742", BODY, "cand-0056", None, "became_important_in_art_world",
    q(38, 38, "Haskell marks 1742 as the point when Algarotti first became important in the international art world and says his activities as patron and critic are well documented from then on.",
      "authorial periodization", "This is Haskell's assessment of historical importance and documentary visibility.",
      ["cand-0056"]),
    quote(38, 38, "It is in 1742 that he first assumes real importance as a figure in the international art world, and from now on we are well informed about his activities as patron and critic."))
add_statement("st-chp14-p350-dresden-gallery-plan", BODY, "cand-0071", "cand-9091", "planned_extension_of_gallery",
    q(39, 39, "In 1742 at Dresden, Algarotti drew up a plan to extend and complete the art gallery being formed by Augustus of Saxony.",
      "biographical narrative", "The gallery mention maps to the previously indexed Dresden Gallery candidate cand-9091; the p.347 source-derived gallery candidate cand-10222 remains distinct pending S3. Note 2 cites Opere, volume VIII, pages 351-388.",
      ["cand-0071", "cand-0947", "cand-0151", "cand-10256", "cand-9091", "cand-10266"],
      relation_candidate=True, **link2),
    quote(39, 39, "In that year, in Dresden, he drew up a plan for extending and completing the spectacular art gallery which was being formed by Augustus of Saxony.2"))
add_statement("st-chp14-p350-scholarly-historical-approach", BODY, "cand-0075", None, "replaced_personal_taste_with_historical_approach",
    q(39, 40, "Haskell says the plan reveals a scholarly approach to art characteristic of Algarotti and his century: instead of organizing galleries by a collector's personal taste, Algarotti adopted a historian's outlook.",
      "authorial interpretation", "Distinguishes Haskell's account of Algarotti's proposal from a general claim about every earlier gallery.",
      ["cand-0075", "cand-0071", "cand-9091"]),
    quote(39, 40, "His proposals are remarkably interesting. In the first place they reveal that scholarly approach to art which was to remain characteristic of him and his century. Until now art galleries had usually been built up according to the collector’s personal tastes. Algarotti rejects this conception and substitutes for it the outlook of the historian."))
add_statement("st-chp14-p350-gallery-represent-history-and-schools", BODY, "cand-0075", "cand-9091", "proposed_representative_history_of_painting",
    q(39, 39, "Algarotti wanted the Dresden gallery to represent the whole history of painting through its finest representatives of all schools.",
      "authorial report of a proposal", "This describes the intended scheme, not a claim that it was fully implemented.",
      ["cand-0075", "cand-9091"]),
    quote(39, 39, "He wants the gallery to reflect the whole history of painting and to include the finest representatives of all schools."))
add_statement("st-chp14-p350-rediscovery-of-primitives", BODY, "cand-0075", "cand-10267", "interpreted_collecting_as_historical_evidence",
    q(39, 40, "Haskell says this historical approach led toward what he calls the first rediscovery of the primitives: eighteenth-century collections of early-Italian works were assembled as evidence and Renaissance precursors, not because taste had changed as it later would with the Romantics.",
      "authorial interpretation", "Preserves Haskell's distinction between evidential collecting in the eighteenth century and a later change in taste; the phrase 'first rediscovery' is his interpretive label.",
      ["cand-0075", "cand-10267", "cand-10268", "cand-3578"]),
    quote(39, 40, "It is evident that such an approach inevitably led (though not in Algarotti himself) to what we can call ‘the first rediscovery of the primitives’—in other words those collections of the works of early-Italian artists which were built up in the eighteenth century not because they corresponded to any real change in taste (as was to be the case with the\nRomantics somewhat later) but because they were looked upon as valuable evidence and as precursors of the Renaissance."))
add_statement("st-chp14-p350-lodoli-collection", BODY, "cand-1411", "cand-10269", "owned_collection",
    q(40, 40, "Haskell says Padre Lodoli owned a collection of the kind just described and directs readers to Chapter 12 for it.",
      "authorial cross-reference", "The collection is kept as an untyped candidate because its individual works and structure are not specified on p.350; no Chapter 12 details are imported here.",
      ["cand-1411", "cand-10269"], relation_candidate=True, **link3),
    quote(40, 40, "We have seen that Padre Lodoli owned just such a collection.3"))
add_statement("st-chp14-p350-followed-historians", BODY, "cand-0075", "cand-1717", "followed_historical_method",
    q(40, 41, "Haskell says Algarotti followed historians such as Muratori and was among the first to apply their principles to large-scale art collecting.",
      "authorial interpretation", "The passage names Muratori as an example but does not specify a single text or direct collaboration.",
      ["cand-0075", "cand-1717"]),
    quote(40, 41, "Algarotti was in fact following in the footsteps of historians such as\nMuratori, but he was among the first to apply their principles to the collecting of art on a large scale."))
add_statement("st-chp14-p350-proposed-living-artist-commissions", BODY, "cand-0072", "cand-10270", "proposed_commissioning_of",
    q(42, 43, "Haskell identifies commissioning works by living artists as the most interesting part of Algarotti's scheme and says it anticipated critical opinion of the time.",
      "authorial interpretation of a plan", "This is a planned component of the scheme, not proof that any particular commission was completed; the artists are unnamed.",
      ["cand-0072", "cand-10270"], relation_candidate=True),
    quote(42, 43, "This approach must be borne in mind when we consider what is to us the most interesting part of his scheme, though this is not how it appeared to his royal master:\nthe commissioning 'of a number of works by living artists. For here too he was in advance of much critical opinion in his day."))
add_statement("st-chp14-p350-detailed-subjects-and-style-awareness", BODY, "cand-0072", None, "recognized_artistic_style_differences",
    q(43, 43, "Haskell says Algarotti specified subjects in detail and stressed contact between writer and painter, while showing greater-than-usual awareness of artists' different styles and letting those differences guide his approach.",
      "authorial interpretation", "The account concerns the scheme and its method; it does not identify specific works or claim that every proposal was executed.",
      ["cand-0072", "cand-10270"]),
    quote(43, 43, "Though he still insisted on giving the subjects in great detail to the artists concerned and was always to stress the importance of contacts between the literary man and the painter, he showed far greater awareness than most patrons of their different styles, and these differences determined his approach."))
add_statement("st-chp14-p350-patron-subject-specialization", BODY, None, None, "matched_commissions_to_specialization",
    q(44, 44, "Haskell generalizes that patrons matched subjects to artists' specializations, giving animal-filled pictures as suitable for Castiglione and landscape as essential to works ordered from Claude.",
      "authorial generalization with examples", "These are examples of a general commissioning principle, not evidence here of specific commissions by Algarotti.",
      ["cand-0602", "cand-0767"]),
    quote(44, 44, "Patrons had always recognised that certain artists specialised in particular subjects and had regulated their commissions accordingly: a picture which could include many animals was suitable for Castiglione, while landscape was an essential ingredient of any picture ordered from Claude."))
add_statement("st-chp14-p350-appraisal-of-venetian-artists", BODY, "cand-0056", None, "evaluated_artists_with_unusual_sensitivity",
    q(44, 44, "Haskell says Algarotti's appraisal of Venetian artists was more subtle, sensitive, and deep than the general patronage practice just described.",
      "authorial interpretation", "The following sentence begins 'He tried to base his' and continues on p.351; the continuation is not inferred here.",
      ["cand-0056", "cand-2719"]),
    quote(44, 44, "But Algarotti’s appraisal of the different Venetian artists was far more subtle and sensitive, and went very much deeper."))

add_statement("st-chp14-p350-note1-letter", NOTES, None, None, "bibliographic_note",
    q(178, 178, "Note 1 identifies a letter to Bonomo dated 5 September 1741 and cites Treviso, MSS. 1256.",
      "authorial bibliographic note", "The manuscript and repository catalogue were not independently consulted; the note does not spell out the repository institution.",
      ["cand-0040", "cand-10251", "cand-10265"],
      cross_reference_segments=[BODY], cross_reference_text="letter marker after the quoted portrait description"),
    quote(178, 178, source_lines[177]))
add_statement("st-chp14-p350-note2-opere", NOTES, None, None, "bibliographic_note",
    q(179, 179, "Note 2 cites Opere, volume VIII, pages 351-388, for the Dresden gallery plan.",
      "authorial bibliographic note", "OCR reads 'Vin'; the printed p.350 image reads 'VIII'. The cited pages were not independently consulted.",
      ["cand-0071", "cand-9091", "cand-10266"],
      ocr_corrections=[{"source_line": 179, "ocr": "Vin", "print": "VIII", "basis": "CHP-14.pdf physical page 4."}],
      cross_reference_segments=[BODY], cross_reference_text="footnote 2 marker after the Augustus of Saxony reference"),
    quote(179, 179, "2 Opere, Vin, pp. 351-88."))
add_statement("st-chp14-p350-note3-chapter12", NOTES, None, None, "internal_chapter_reference",
    q(179, 179, "Note 3 directs the reader to Chapter 12 for the reference to Padre Lodoli's collection.",
      "authorial internal cross-reference", "The target chapter is recorded as printed; no chapter-level content is imported into this statement.",
      ["cand-1411", "cand-10269"],
      cross_reference_segments=[BODY], cross_reference_text="footnote 3 marker after the Lodoli collection statement"),
    quote(179, 179, "3 See Chapter 12."))

# P.350 closes the p.349 inference but ends with a new sentence continuing on p.351.
coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L23-33",
    "note": "Printed p.349 read against CHP-14.pdf physical p.3. Its final inference sentence continues in p.350 L36 and closes with 'native city'; linked to st-chp14-p350-rococo-influence-context. S0 unchanged; print corrections are in statement qualifiers.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L35-44",
    "note": "Printed p.350 read against CHP-14.pdf physical p.4. Closes the p.349 inference and links notes 1-3 to their body markers. L44 ends 'He tried to base his' and continues on p.351 L46; leave partial until closed. OCR corrections are in S2 qualifiers; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-179",
    "note": "Printed notes p.347-p.350 read against CHP-14.pdf physical pages 1-4. Notes 1-3 on p.350 are linked to the portrait letter, gallery plan, and Lodoli collection statements. Later-page notes remain pending.",
})

# Preflight foreign keys and exact character anchors for this batch.
known_ids = set(candidate_by_id)
for row in mentions:
    if row["mention_id"].startswith("m-chp14-p350-"):
        seg = row["segment_id"]
        bounds = segment_bounds[seg]
        text = "\n".join(source_lines[bounds[0] - 1:bounds[1]])
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']} {row['surface_form']!r}")
        if row["candidate_id"] not in known_ids:
            raise SystemExit(f"mention candidate missing: {row['mention_id']}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p350-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in known_ids:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in known_ids:
                raise SystemExit(f"statement mentioned candidate missing: {row['statement_id']} -> {cid}")

new_mentions = [r for r in mentions if r["mention_id"].startswith("m-chp14-p350-")]
new_statements = [r for r in statements if r["statement_id"].startswith("st-chp14-p350-")]
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
