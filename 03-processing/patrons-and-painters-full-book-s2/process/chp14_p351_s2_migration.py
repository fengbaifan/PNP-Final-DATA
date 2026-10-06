"""Controlled S2 migration for printed p.351 body and notes 1-2; dry-run by default."""
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
BODY_PREV = "chp-14:14_CHP-14_intro:l35-44"
BODY = "chp-14:14_CHP-14_intro:l46-53"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
BACKUP_SUFFIX = ".bak-s2-chp14-p351-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.351 S2 migration")
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
    47: "choice of subjects largely on stylistic considerations.",
    48: "Piazzetta was ‘a great draughtsman",
    49: "2nd gladly decorates his compositions with architecture’;",
    50: "His undogmatic and liberal views can be seen",
    51: "He found subjects for Francesco de Mura and Solimena",
    52: "It is worth emphasising once more that Algarotti drew up this ideal list",
    53: "Pittoni, Tiepolo and Zuccarelli painted the pictures that he chose for them",
    180: "In the Saggio sopra la Pittura",
    181: "See L. Ferrari, 1900, pp. 150-4",
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
    raise SystemExit("p.350 body segment is not in the expected partial state")
if coverage_by_id[BODY]["disposition"] != "queued":
    raise SystemExit("p.351 body segment is not queued; refusing to overwrite")
if coverage_by_id[NOTES]["disposition"] != "reviewed" or coverage_by_id[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated chapter 14 notes segment is not in the expected partial state")

new_candidates = [
    ("cand-10271", "Proposed subject ‘The Hunt of Meleager and Atalanta’ for Francesco Zuccarelli", "work", 50,
     "Haskell says Zuccarelli was given a subject such as this for the Dresden scheme; the passage does not establish that this exact subject became a completed painting."),
    ("cand-10272", "‘Pittore di macchia’ as Algarotti’s characterization of Tiepolo", "term", 49,
     "A quoted stylistic description attributed to Algarotti by Haskell; retain the Italian wording and do not infer a formal school membership."),
    ("cand-10273", "Five paintings selected by Algarotti for Amigoni, Piazzetta, Pittoni, Tiepolo, and Zuccarelli for Augustus’s gallery (all reported lost)", "work", 53,
     "Haskell reports that the five artists painted pictures selected for them and that all were lost; individual titles are not supplied on p.351."),
    ("cand-10274", "Francesco Algarotti’s letter to Pierre-Jean Mariette, 13 February 1751 (published in Opere, VIII, pp.15–40)", "archive", 181,
     "Identified by addressee, date, and Haskell’s publication locator; the letter and edition were not independently consulted."),
    ("cand-10275", "L. Ferrari, 1900, pp.150–154 (citation in p.351 note 2)", "archive", 181,
     "Short bibliographic citation as printed by Haskell; title, edition, and cited pages were not independently checked."),
    ("cand-10276", "Posse, 1931 (citation in p.351 note 2)", "archive", 181,
     "Short bibliographic citation as printed by Haskell; title, edition, and cited pages were not supplied or independently checked."),
    ("cand-10277", "‘Soggetti graziosi e leggeri’ (graceful and light subjects in Algarotti’s plan)", "term", 51,
     "Haskell quotes this phrase for a proposed subject category shared by Boucher, Balestra, and Donato Creti; preserve the Italian wording and planned context."),
    ("cand-10278", "History painters as a category in Algarotti’s Dresden gallery scheme", "term", 47,
     "Haskell calls Tiepolo, Pittoni, and Piazzetta history painters and says the gallery list included only this category; this is the source’s classification, not an inferred formal school membership."),
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

segment_bounds = {BODY: (46, 53), NOTES: (168, 220)}
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
                mention_id = f"m-chp14-p351-{mention_counter:04d}"
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
                mention_id = f"m-chp14-p351-{mention_counter:04d}"
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


# Index-derived artists and places remain candidates until S3 identity review.
for item in [
    ("Tiepolo", "cand-2572", [47, 49, 53]),
    ("Pittoni", "cand-1950", [47, 48, 53]),
    ("Piazzctta", "cand-1902", [47], "The scanned print reads Piazzetta; S0 OCR retained unchanged."),
    ("Piazzetta", "cand-1902", [48, 52, 53]),
    ("Zuccarelli", "cand-2879", [50, 53]),
    ("Pannini", "cand-1827", [50, 51]),
    ("Canaletto", "cand-0499", [50]),
    ("Boucher", "cand-0421", [50]),
    ("Balestra", "cand-0168", [51]),
    ("Donato Creti", "cand-0889", [50, 51]),
    ("Francesco de Mura", "cand-1716", [51]),
    ("Solimena", "cand-2484", [51]),
    ("Ercole Lefli", "cand-1383", [51], "The scanned print reads Ercole Lelli; S0 OCR retained unchanged."),
    ("Jacopo Amigoni", "cand-0094", [51]),
    ("Amigoni", "cand-0094", [52]),
    ("Mancini", "cand-1506", [51]),
    ("Crespi", "cand-0871", [51]),
    ("Venice", "cand-2719", [52]),
    ("Bologna", "cand-0381", [51, 52]),
    ("Rome", "cand-4490", [51, 52]),
    ("Augustus", "cand-0151", [52]),
    ("gallery", "cand-9091", [50, 52]),
    ("history painters", "cand-10278", [47, 50]),
    ("history picture", "cand-10278", [50]),
    ("The Hunt of Meleager and Atalanta", "cand-10271", [50]),
    ("pittore di macchia", "cand-10272", [49]),
    ("soggetti. graziosi e leggeri", "cand-10277", [51], "OCR includes a period after soggetti; print reads ‘soggetti graziosi e leggeri’."),
    ("the pictures that he chose for them", "cand-10273", [53]),
    ("Saggio sopra la Pittura", "cand-0074", [180]),
    ("Opere, HI, p. 125", "cand-10229", [180], "The printed p.351 image reads Opere, III, p. 125."),
    ("L. Ferrari, 1900", "cand-10275", [181]),
    ("pp. 150-4", "cand-10275", [181]),
    ("Algarotti’s letter to Mariette", "cand-10274", [181]),
    ("Mariette", "cand-1547", [181]),
    ("13 February 1751", "cand-10274", [181]),
    ("Opere, VW, pp. 15-40", "cand-10229", [181], "The printed p.351 image reads Opere, VIII, pp. 15-40."),
    ("Posse, 1931", "cand-10276", [181]),
]:
    surface, cid, lines, *note = item
    add_surface(NOTES if lines[0] >= 168 else BODY, cid, surface, lines, note=note[0] if note else "")

# Coreference is linked only where the immediate clause identifies Algarotti or Pittoni.
add_pronouns(BODY, "cand-0072", ["he"], [49, 51, 52, 53])
add_pronouns(BODY, "cand-0072", ["His"], [50])
add_pronouns(BODY, "cand-0072", ["his"], [53])
add_pronouns(BODY, "cand-1950", ["his"], [49], note="In ‘his compositions’, the possessive refers to Pittoni.")
add_surface(BODY, "cand-0072", "Algarotti", [47, 52])
add_surface(BODY, "cand-0072", "Algarotti’s", [49])


def quote(start, end, exact):
    allowed = "\n".join(source_lines[start - 1:end])
    if exact not in allowed:
        raise SystemExit(f"statement quotation is not present in L{start}-L{end}: {exact[:90]!r}")
    return exact


def q(start, end, claim, layer, qualification, candidate_ids, **extra):
    out = {
        "source_line_start": start, "source_line_end": end, "printed_page": 351,
        "pdf_physical_page": 5, "claim": claim, "speaker": "Haskell",
        "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    out.update(extra)
    return out


def add_statement(statement_id, subject, obj, predicate, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    start, end = qualifiers["source_line_start"], qualifiers["source_line_end"]
    if not (46 <= start <= end <= 53):
        raise SystemExit(f"statement span escapes p.351 segment: {statement_id}")
    row = {
        "statement_id": statement_id, "segment_id": BODY,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers, "original_quote": original_quote,
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


def add_note_statement(statement_id, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    row = {
        "statement_id": statement_id, "segment_id": NOTES,
        "subject_candidate_id": None, "object_candidate_id": None,
        "predicate": "bibliographic_note", "qualifiers": qualifiers,
        "original_quote": original_quote, "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


add_statement("st-chp14-p351-style-based-subject-choice", "cand-0072", None, "planned_subject_choice_based_on_style",
    q(47, 47, "Algarotti based the choice of subjects largely on stylistic considerations.",
      "continuation of authorial interpretation", "This completes the sentence opened at p.350 L44 (‘He tried to base his’); the previous page remains separately anchored and is cross-referenced.",
      ["cand-0072", "cand-2572", "cand-1950", "cand-1902", "cand-10278"],
      cross_reference_segments=[BODY_PREV], cross_reference_text="completes st-chp14-p350-appraisal-of-venetian-artists"),
    quote(47, 47, "choice of subjects largely on stylistic considerations."))
add_statement("st-chp14-p351-piazzetta-appraisal", "cand-0072", "cand-1902", "characterized_as",
    q(48, 48, "In a quoted appraisal attributed to Algarotti, Piazzetta is described as a great draughtsman and good colourist but as having little elegance of form or expression.",
      "quoted appraisal reported by Haskell", "The appraisal is attributed to Algarotti within Haskell’s account; the primary text was not separately consulted.",
      ["cand-0072", "cand-1902"]),
    quote(48, 48, "Piazzetta was ‘a great draughtsman and a good colourist, but has little elegance of form or expression’;"))
add_statement("st-chp14-p351-pittoni-appraisal", "cand-0072", "cand-1950", "characterized_as",
    q(48, 49, "The quoted appraisal says Pittoni was distinguished for painting priests’ vestments and gladly decorated compositions with architecture.",
      "quoted appraisal reported by Haskell", "OCR reads ‘2nd gladly’; the printed page reads ‘and gladly’. The appraisal remains attributed through Haskell.",
      ["cand-0072", "cand-1950"], ocr_corrections=[{"source_line": 49, "ocr": "2nd", "print": "and", "basis": "CHP-14.pdf physical page 5."}]),
    quote(48, 49, "while Pittoni was ‘distinguished for painting the vestments of priests ...\n2nd gladly decorates his compositions with architecture’;"))
add_statement("st-chp14-p351-tiepolo-appraisal", "cand-0072", "cand-2572", "characterized_as",
    q(49, 49, "Algarotti is quoted describing Tiepolo as a spirited pittore di macchia.",
      "quoted appraisal reported by Haskell", "The Italian phrase is preserved; it is not treated as proof of formal affiliation with an art movement.",
      ["cand-0072", "cand-2572", "cand-10272"]),
    quote(49, 49, "and Tiepolo was ‘a spirited pittore di macchia;"))
add_statement("st-chp14-p351-sensitivity-and-influence-limit", "cand-0072", None, "praised_for_sensitivity_with_influence_uncertain",
    q(49, 49, "Haskell says the willingness to consider painters’ individual talents shows unusual sensitivity and a non-bullying approach, while making Algarotti’s influence on individual painters difficult to gauge.",
      "authorial interpretation", "This preserves Haskell’s explicit uncertainty about influence and does not infer individual causal effects.",
      ["cand-0072", "cand-2572", "cand-1950", "cand-1902"]),
    quote(49, 49, "How far the subjects chosen really corresponded to the particular talents of the painters concerned, or how far we today would endorse Algarotti’s analysis of those talents, is not really the question: the very fact that he was prepared to go thus far shows us that he looked at paintings with unusual sensitivity and that he had none of the bullying approach with which other patrons of the day were sometimes charged. Indeed, this openness to experience is one of his most attractive characteristics, but it makes it difficult to gauge the strength of his influence on individual painters."))
add_statement("st-chp14-p351-history-painters-in-plan", "cand-0072", "cand-10278", "limited_artist_selection_to_history_painters",
    q(50, 50, "Haskell says the gallery proposal included only history painters.",
      "authorial report of a proposal", "The statement concerns the proposed gallery list, not every artist Algarotti valued.",
      ["cand-0072", "cand-9091", "cand-10278"]),
    quote(50, 50, "It is true that only ‘history painters’ were included"))
add_statement("st-chp14-p351-zuccarelli-proposed-subject", "cand-0072", "cand-10271", "proposed_subject_for_artist",
    q(50, 50, "The proposal gave Zuccarelli a subject such as The Hunt of Meleager and Atalanta, or another sad or cheerful story matching the landscape’s mood.",
      "authorial report of a proposal", "‘Such as’ and the alternatives are retained; this does not establish that the named subject was painted.",
      ["cand-0072", "cand-2879", "cand-10271"]),
    quote(50, 50, "and this led to Zuccarelli being given a subject such as The Hunt of Meleager and Atalanta ‘or something else, either sad or cheerful, in which the story corresponds to the mood of the landscape where it takes place’"))
add_statement("st-chp14-p351-pannini-subject", "cand-0072", "cand-1827", "required_subject_for_artist",
    q(50, 50, "Pannini was required to paint ancient Romans among his vedute.",
      "authorial report of a proposal", "The passage describes a requirement in the scheme, not a completed painting.",
      ["cand-0072", "cand-1827"]),
    quote(50, 50, "and to Pannini being required to paint ancient Romans among his vedute"))
add_statement("st-chp14-p351-canaletto-omitted", "cand-0072", "cand-0499", "omitted_from_proposed_artist_list",
    q(50, 50, "Haskell says Canaletto was ignored altogether in the gallery artist choices.",
      "authorial report of a proposal", "This is the omission described for the scheme; it is not a general statement about Algarotti’s esteem for Canaletto in other contexts.",
      ["cand-0072", "cand-0499", "cand-9091"]),
    quote(50, 50, "while Canaletto was ignored altogether."))
add_statement("st-chp14-p351-range-and-travel-influence", "cand-0072", None, "artist_choices_wide_ranging_after_foreign_travels",
    q(50, 50, "Haskell describes Algarotti’s choices within the history-picture category as wide-ranging and attributes this, with ‘no doubt’, to his foreign travels.",
      "authorial interpretation", "The causal explanation is Haskell’s qualified interpretation, not an independently established causal fact.",
      ["cand-0072", "cand-10278"]),
    quote(50, 50, "Yet within the limits of the ‘history picture’ Algarotti was wide ranging, and this was no doubt due to the influence exerted by his foreign travels, far out of reach of the scholars and pedants of Italy."))
add_statement("st-chp14-p351-boucher-subjects-and-cooperation", "cand-0072", "cand-10277", "proposed_graceful_light_subjects_and_french_italian_cooperation",
    q(50, 51, "Algarotti included Boucher among artists assigned ‘soggetti graziosi e leggeri’ with Balestra and Donato Creti; Haskell calls this a rare eighteenth-century venture requiring French and Italian artists to cooperate.",
      "authorial report and interpretation", "The phrase is quoted as a planned subject category. The OCR period after ‘soggetti’ is corrected from the print; the named collaborative venture is not given a separate title.",
      ["cand-0072", "cand-0421", "cand-0168", "cand-0889", "cand-10277"],
      ocr_corrections=[{"source_line": 51, "ocr": "soggetti. graziosi", "print": "soggetti graziosi", "basis": "CHP-14.pdf physical page 5."}]),
    quote(50, 51, "For instance, despite rather a scornful aside, he included Boucher among the artists to be given\n‘soggetti. graziosi e leggeri’, along with Balestra and Donato Creti—one of the very rare occasions in the eighteenth century when French and Italian artists were required to co-operate in a single venture."))
add_statement("st-chp14-p351-neapolitan-subjects", "cand-0072", None, "found_subjects_for_neapolitan_artists",
    q(51, 51, "Haskell says Algarotti found subjects for Francesco de Mura and Solimena among the Neapolitans.",
      "authorial report of a proposal", "‘Among the Neapolitans’ is retained as the source’s regional artist grouping; no individual city or formal group is inferred.",
      ["cand-0072", "cand-1716", "cand-2484"]),
    quote(51, 51, "He found subjects for Francesco de Mura and Solimena among the Neapolitans;"))
add_statement("st-chp14-p351-bologna-subjects", "cand-0072", None, "named_artists_in_bologna_context",
    q(51, 51, "The scheme’s account names Ercole Lelli and Donato Creti in the Bologna context.",
      "authorial report of a proposal", "The sentence supplies a city context but does not assert birthplace or a formal commission beyond the surrounding plan discussion.",
      ["cand-0072", "cand-1383", "cand-0889", "cand-0381"]),
    quote(51, 51, "Ercole Lefli and Donato Creti in Bologna;"))
add_statement("st-chp14-p351-venetian-artists-and-amigoni", "cand-0072", None, "included_venetian_artists_and_amigoni_in_plan",
    q(51, 51, "Haskell refers to the four Venetian artists already discussed and Jacopo Amigoni among the artists selected in the scheme.",
      "authorial report of a proposal", "‘The four Venetians already mentioned’ is linked to the named artists in the immediate preceding passage; their separate identities remain separately anchored.",
      ["cand-0072", "cand-2572", "cand-1950", "cand-1902", "cand-0499", "cand-0094"]),
    quote(51, 51, "the four Venetians already mentioned and Jacopo Amigoni;"))
add_statement("st-chp14-p351-rome-artists", "cand-0072", None, "named_rome_artist_choices",
    q(51, 51, "Haskell says that in Rome only Mancini was selected besides the special case of Pannini.",
      "authorial report of a proposal", "‘Only’ is preserved as a limit on this part of the list.",
      ["cand-0072", "cand-1506", "cand-1827", "cand-4490"]),
    quote(51, 51, "and in Rome, only Mancini besides the rather special case of Pannini."))
add_statement("st-chp14-p351-detachment-from-rome", "cand-0072", None, "interpreted_as_detached_from_roman_values",
    q(51, 51, "Haskell interprets the list as showing Algarotti’s detachment from Roman values.",
      "authorial interpretation", "This records Haskell’s evaluation, not a neutral or independently verified description of Roman values.",
      ["cand-0072", "cand-4490"]),
    quote(51, 51, "Nothing could show more clearly his detachment from Roman values."))
add_statement("st-chp14-p351-crespi-omission-and-later-praise", "cand-0072", "cand-0871", "omitted_then_later_praised",
    q(51, 51, "Crespi was another surprising omission from the list, although Algarotti later singled him out for special praise.",
      "authorial report and cross-reference", "The later praise is supported by Haskell’s note citing Saggio sopra la Pittura and Opere III, p.125; neither source was independently consulted.",
      ["cand-0072", "cand-0871", "cand-0074", "cand-10229"], relation_candidate=True,
      footnote_marker="1", footnote_segment=NOTES, footnote_line_range="L180",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=["st-chp14-p351-note1-saggio"]),
    quote(51, 51, "The other surprising omission is Crespi, whom he was later to single out for special praise.1"))
add_statement("st-chp14-p351-time-away-and-evidence-basis", "cand-0072", None, "list_drawn_after_absence_with_qualified_secondhand_basis",
    q(52, 52, "Algarotti drew up the ideal list after being away from Venice, Bologna, and Rome for nearly five years; Haskell says many comments must therefore have relied on secondhand reports or foreign collections.",
      "authorial inference", "Preserves ‘nearly’ and Haskell’s modal ‘must have’; no individual comment is assigned a specific informant.",
      ["cand-0072", "cand-2719", "cand-0381", "cand-4490"]),
    quote(52, 52, "It is worth emphasising once more that Algarotti drew up this ideal list after.he had been away from Venice, Bologna and Rome for nearly five years, and that consequently many of his comments must have been based on what he had heard at second hand from correspondents and travellers or at best on what he had seen in foreign collections."))
add_statement("st-chp14-p351-returned-to-implement-proposals", "cand-0072", None, "returned_to_venice_to_implement_proposals",
    q(52, 52, "Soon after making the proposals, Algarotti came to Venice to try to put them into effect.",
      "authorial narrative", "‘Try to put them into effect’ expresses an intention, not completed implementation.",
      ["cand-0072", "cand-2719"]),
    quote(52, 52, "But very soon after making these proposals he came to Venice to try and put them into effect."))
add_statement("st-chp14-p351-old-master-preference-and-modern-art-success", "cand-0072", None, "modern_art_plans_partly_successful_despite_old_master_preference",
    q(52, 52, "Haskell says Augustus was much more enthusiastic about old masters, while Algarotti’s plans to promote modern art were successful to some extent.",
      "authorial assessment", "Both the comparison and partial success remain Haskell’s characterization; ‘to some extent’ is retained.",
      ["cand-0072", "cand-0151", "cand-9091"]),
    quote(52, 52, "Despite Augustus’s far greater enthusiasm for old masters, Algarotti’s plans for promoting modem art were to some extent successful."))
add_statement("st-chp14-p351-five-selected-pictures-painted-and-lost", "cand-0072", "cand-10273", "selected_pictures_painted_then_lost",
    q(52, 53, "Amigoni, Piazzetta, Pittoni, Tiepolo, and Zuccarelli painted the pictures Algarotti chose for them, and Haskell says all were lost.",
      "authorial report", "The five-picture group has no individual titles here. Note 2 cites Ferrari, a 1751 letter published in Opere VIII, and Posse; the cited materials were not independently consulted.",
      ["cand-0072", "cand-0094", "cand-1902", "cand-1950", "cand-2572", "cand-2879", "cand-10273", "cand-10274", "cand-10275", "cand-10276", "cand-10229"], relation_candidate=True,
      footnote_marker="2", footnote_segment=NOTES, footnote_line_range="L181",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=["st-chp14-p351-note2-lost-pictures"]),
    quote(52, 53, "Amigoni, Piazzetta,\nPittoni, Tiepolo and Zuccarelli painted the pictures that he chose for them, but unfortunately all have been lost.2"))

# The source phrase started on p.350 and is now complete; update its prior evidence note.
previous = statement_by_id.get("st-chp14-p350-appraisal-of-venetian-artists")
if previous is None:
    raise SystemExit("expected p.350 appraisal statement is missing")
previous["qualifiers"]["qualification"] = "The quoted appraisal is complete on p.350 L44. Its following sentence is completed at p.351 L47 and recorded as st-chp14-p351-style-based-subject-choice."
previous["qualifiers"]["cross_reference_segments"] = [BODY]
previous["qualifiers"]["cross_reference_text"] = "continuation at p.351 L47 completes the next sentence"

notes1 = {
    "source_line_start": 180, "source_line_end": 180, "printed_page": 351,
    "pdf_physical_page": 5, "claim": "Note 1 cites Algarotti’s Saggio sopra la Pittura, in Opere volume III, page 125, for the later praise of Crespi.",
    "speaker": "Haskell", "text_layer": "authorial bibliographic note",
    "qualification": "The printed page reads III; OCR reads HI. The cited edition and page were not independently consulted.",
    "mentioned_candidate_ids": ["cand-0871", "cand-0074", "cand-10229"],
    "ocr_corrections": [{"source_line": 180, "ocr": "HI", "print": "III", "basis": "CHP-14.pdf physical page 5."}],
    "cross_reference_segments": [BODY], "cross_reference_text": "footnote 1 marker after the Crespi omission and later-praise sentence",
}
notes2 = {
    "source_line_start": 181, "source_line_end": 181, "printed_page": 351,
    "pdf_physical_page": 5, "claim": "Note 2 cites L. Ferrari (1900), pages 150–154; Algarotti’s 13 February 1751 letter to Mariette published in Opere volume VIII, pages 15–40; and Posse (1931).",
    "speaker": "Haskell", "text_layer": "authorial bibliographic note",
    "qualification": "The printed page reads VIII; OCR reads VW. The letter, cited works, and editions were not independently consulted.",
    "mentioned_candidate_ids": ["cand-10274", "cand-1547", "cand-10275", "cand-10276", "cand-10229"],
    "ocr_corrections": [{"source_line": 181, "ocr": "VW", "print": "VIII", "basis": "CHP-14.pdf physical page 5."}],
    "cross_reference_segments": [BODY], "cross_reference_text": "footnote 2 marker after the statement that the five pictures were lost",
}
add_note_statement("st-chp14-p351-note1-saggio", notes1,
    quote(180, 180, "1 In the Saggio sopra la Pittura—see Opere, HI, p. 125."))
add_note_statement("st-chp14-p351-note2-lost-pictures", notes2,
    quote(181, 181, "2 See L. Ferrari, 1900, pp. 150-4, and Algarotti’s letter to Mariette of 13 February 1751 published in Opere, VW, pp. 15-40; also Posse, 1931."))

# p.350's sentence closes on p.351; p.351 itself ends mid-sentence at “a painting”.
coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L35-44",
    "note": "Printed p.350 read against CHP-14.pdf physical p.4. Its L44 sentence, ‘He tried to base his’, is completed by p.351 L47 ‘choice of subjects largely on stylistic considerations’; cross-linked to st-chp14-p351-style-based-subject-choice. S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L47-53",
    "note": "Printed p.351 read against CHP-14.pdf physical p.5; L47 completes p.350 L44. L53 ends ‘in a painting’ and continues on p.352 L56, so keep partial. Print corrections are recorded in S2 qualifiers; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-181",
    "note": "Printed notes p.347-p.351 read against CHP-14.pdf physical pages 1-5. Notes 1-2 on p.351 are linked to the Crespi praise and the five lost pictures. Later-page notes remain pending.",
})

# Preflight foreign keys and exact character anchors for this batch.
known_ids = set(candidate_by_id)
for row in mentions:
    if row["mention_id"].startswith("m-chp14-p351-"):
        seg = row["segment_id"]
        bounds = segment_bounds[seg]
        text = "\n".join(source_lines[bounds[0] - 1:bounds[1]])
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']} {row['surface_form']!r}")
        if row["candidate_id"] not in known_ids:
            raise SystemExit(f"mention candidate missing: {row['mention_id']}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p351-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in known_ids:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in known_ids:
                raise SystemExit(f"statement mentioned candidate missing: {row['statement_id']} -> {cid}")

new_mentions = [r for r in mentions if r["mention_id"].startswith("m-chp14-p351-")]
new_statements = [r for r in statements if r["statement_id"].startswith("st-chp14-p351-")]
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
