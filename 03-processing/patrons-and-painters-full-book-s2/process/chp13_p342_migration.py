"""Controlled S2 migration for printed p.342; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
BODY = "chp-13:13_CHP-13_intro:l98-105"
PREVIOUS = "chp-13:13_CHP-13_intro:l90-96"
NEXT = "chp-13:13_CHP-13_intro:l107-114"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BODY_SHA = "784beac28408e154b50a6afebd080e5c3de774cd0bd6bc8093bfbee712c4c0a0"
BACKUP_SUFFIX = ".bak-s2-chp13-p342-20261003"
PREVIOUS_STATEMENT = "st-chp13-p341-tessin_fondness_for_rococo_and_graceful_subjects"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.342 S2 migration")
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
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[97] != "[Page 342]":
    raise SystemExit("p.342 page anchor changed")
body_text = "\n".join(source_lines[97:105])
if hashlib.sha256(body_text.encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("p.342 source segment changed")
for line, required in {
    99: "use of Zanetti’s taste and scholarship",
    100: "Tessin sent friendly messages to Tiepolo",
    101: "pictures by Zuccarelli and Nogari",
    102: "thereis no evidence to showthat",
    103: "pastels and miniatures by Rosalba",
    104: "his large collection of prints",
    105: "except the dish engraved with a Bacchanal by Annibale",
}.items():
    if required not in source_lines[line - 1]:
        raise SystemExit(f"required p.342 text missing at L{line}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}

state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (10063, 10076, 21626, 9646):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment_id in (BODY, PREVIOUS, NEXT, NOTES):
    if segment_id not in coverage:
        raise SystemExit(f"required coverage row missing: {segment_id}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.342 is not queued/pending")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.341 is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("chapter 13 notes are not queued/pending")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.342 rows already exist")
if PREVIOUS_STATEMENT not in statement_by_id:
    raise SystemExit(f"required p.341 continuation statement missing: {PREVIOUS_STATEMENT}")

new_candidates = []
new_mentions = []
new_statements = []
candidate_specs = [
    ("cand-10077", "Unidentified young protégé sent by Tessin to Zanetti for instruction", "person",
     "The body does not give the young man's name. Keep his role and the report of his early death distinct from an identity claim.", 99),
    ("cand-10078", "King of Sweden who refused the sum to lure Tiepolo to Stockholm (identity unspecified)", "person",
     "Named only by royal title in this account. Do not merge with other unidentified Swedish monarch references before S3.", 100),
    ("cand-10079", "Pictures by Francesco Zuccarelli bought by Tessin from Zanetti", "work",
     "The passage gives no titles, count, or individual objects; preserve this as an unnamed group of pictures.", 101),
    ("cand-10080", "Pictures by Giuseppe Nogari bought by Tessin from Zanetti", "work",
     "The passage gives no titles, count, or individual objects; preserve this as an unnamed group of pictures.", 101),
    ("cand-10081", "Prints by G. M. Crespi bought by Tessin from Zanetti", "work",
     "The passage gives no print titles, count, or individual objects; preserve the medium stated in the source.", 101),
    ("cand-10082", "Figure commissioned from Gai for Tessin, intended to represent a Venus emerging from the Baths", "work",
     "The text reports a commission and intended subject, not that the sculpture was completed. Zanetti facilitated it; retain the intended pairing with Tessin's Bathsheba.", 101),
    ("cand-10083", "Bathsheba by Giovanni da Bologna belonging to Tessin", "work",
     "The quoted passage gives no title or medium beyond a Bathsheba. Keep the work separate from the newly commissioned figure.", 101),
    ("cand-10084", "Giovanni da Bologna (name as given for Tessin's Bathsheba; identity pending)", "person",
     "Retain the source form as a separate S2 candidate; do not resolve it to Giambologna or another index candidate before S3.", 101),
    ("cand-10085", "Pictures by Brand and Dietrich in Zanetti's collection", "work",
     "The passage names two German artists but no individual picture titles or count.", 102),
    ("cand-10086", "Older works acquired by Zanetti in France and England", "work",
     "The works are not individually identified. Haskell says some were significant and influential; do not infer titles or acquisition dates.", 102),
    ("cand-10087", "Three history paintings by Sebastiano in Zanetti's collection", "work",
     "The body gives a count and genre but no titles. The artist is mentioned only as Sebastiano and remains subject to S3 alignment.", 103),
    ("cand-10088", "About six landscapes commissioned by Zanetti from Marco Ricci", "work",
     "The source says half a dozen and that Zanetti commissioned them. No individual landscape titles are supplied.", 103),
    ("cand-10089", "Pastels and miniatures by Rosalba Carriera owned by Zanetti", "work",
     "The body provides media and artist but no titles or count. S0 reads Camera; the print reads Carriera, recorded as an S2 correction only.", 103),
    ("cand-10090", "Dish engraved with a Bacchanal by Annibale, excepted in Zanetti's 1752 statement about rare prints", "work",
     "The sentence continues onto p.343. Do not infer from this fragment whether the dish was absent, unavailable, or otherwise excepted.", 105),
]
expected_new_ids = {spec[0] for spec in candidate_specs}
if expected_new_ids & set(candidate_by_id):
    raise SystemExit(f"p.342 candidate IDs already exist: {sorted(expected_new_ids & set(candidate_by_id))}")
for cid, name, kind, detail, line in candidate_specs:
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L{line}",
    })
    new_candidates.append(row)
all_candidate_ids = set(candidate_by_id) | expected_new_ids

body_lines = {number: source_lines[number - 1] for number in range(98, 106)}
segment_text = "\n".join(body_lines[number] for number in range(98, 106))
line_offsets = {}
offset = 0
for number in range(98, 106):
    line_offsets[number] = offset
    offset += len(body_lines[number]) + 1


def add_mention(line, surface, cid, note="", occurrence=0):
    raw_line = body_lines[line]
    positions, cursor = [], 0
    while True:
        at = raw_line.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention text missing at L{line}: {surface!r} occurrence {occurrence}")
    start = line_offsets[line] + positions[occurrence]
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p342-{len(new_mentions) + 1:03d}",
        "segment_id": BODY,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention FK missing: {cid}")
    new_mentions.append(row)


mention_specs = [
    (99, "use of Zanetti’s taste and scholarship", "cand-2838"),
    (99, "his own collections", "cand-2554", "The possessive refers to Tessin; the collection is not treated as a separate institution."),
    (99, "He sent", "cand-2554"),
    (99, "him", "cand-2838", "Anaphoric reference to Zanetti."),
    (99, "a young protégé", "cand-10077"),
    (99, "for instruction", "cand-10077"),
    (99, "il s’agit de l’employer d’abord selon ses talens, et de Luy faire gagner l’argent des Ignorants, jusqu’à ce qu’il soit en état de travailler pour les Connoisseurs", "cand-10077", "Quoted French instruction passage; its cited letter remains pending note 1."),
    (99, "the unfortunate young man", "cand-10077"),
    (99, "Through Zanetti", "cand-2838", "The phrase connects the following Tiepolo message to the preceding Tessin passage."),
    (100, "Tessin", "cand-2554"),
    (100, "friendly messages", "cand-2569", "Messages sent to Tiepolo through Zanetti."),
    (100, "Tiepolo", "cand-2569"),
    (100, "the painter", "cand-2569"),
    (100, "the King of Sweden", "cand-10078"),
    (100, "him", "cand-2569", "Anaphoric reference to Tiepolo."),
    (101, "Stockholm", "cand-4790"),
    (101, "Tessin", "cand-2554"),
    (101, "from Zanetti", "cand-2838"),
    (101, "pictures by Zuccarelli", "cand-10079"),
    (101, "Zuccarelli", "cand-2879"),
    (101, "and Nogari", "cand-10080", "This introduces the second unnamed picture group in the purchase sentence."),
    (101, "Nogari", "cand-1743"),
    (101, "prints by G. M. Crespi", "cand-10081"),
    (101, "G. M. Crespi", "cand-0871"),
    (101, "his good offices", "cand-2838", "The possessive refers to Zanetti as intermediary."),
    (101, "a figure by the sculptor Gai", "cand-10082"),
    (101, "Gai", "cand-1099"),
    (101, "he considered", "cand-2554", "Tessin is the subject of the judgment."),
    (101, "un demi-Michel Ange", "cand-1099", "Tessin's quoted assessment of Gai; note 4 remains pending."),
    (101, "The figure", "cand-10082"),
    (101, "une Venus sortant des Bains", "cand-10082", "Intended iconography of the commissioned figure; not an independent mythological-person candidate."),
    (101, "une Bathsheba", "cand-10083"),
    (101, "Giovanni da Bologna", "cand-10084"),
    (101, "qui m’appartient", "cand-10083", "The quoted first person is Tessin, who says the Bathsheba belongs to him."),
    (102, "Zanetti", "cand-2838"),
    (102, "an intermediary between Venice and the rest of Europe", "cand-2844"),
    (102, "Venice", "cand-2719"),
    (102, "the rest of Europe", "cand-3462"),
    (102, "his actual collections", "cand-2838", "The possessive refers to Zanetti."),
    (102, "his own city", "cand-2719", "The city is Venice."),
    (102, "He owned", "cand-2838"),
    (102, "pictures by the German artists Brand and Dietrich", "cand-10085"),
    (102, "German", "cand-5529", "Nationality adjective attached to Brand and Dietrich."),
    (102, "Brand", "cand-0445"),
    (102, "Dietrich", "cand-0920"),
    (102, "French", "cand-5317", "Geographic/cultural modifier in the negative-evidence claim."),
    (102, "English", "cand-8983", "Geographic/cultural modifier in the negative-evidence claim."),
    (102, "thereis no evidence to showthat he ever bought modern French or English paintings, drawings or prints", "cand-2838", "Negative-evidence claim about Zanetti; OCR spacing corrections are recorded in S2 qualifiers."),
    (102, "those countries", "cand-5317", "Anaphoric reference to France and England; exact phrase applies to the older acquired works."),
    (102, "those countries", "cand-8983", "Anaphoric reference to France and England; exact phrase applies to the older acquired works."),
    (102, "some of the older works that he acquired in those countries", "cand-10086"),
    (102, "his taste", "cand-2838", "The possessive refers to Zanetti."),
    (103, "three history paintings by Sebastiano", "cand-10087"),
    (103, "Sebastiano", "cand-2154", "Only the first name appears; S1 mapping remains provisional pending S3."),
    (103, "half a dozen landscapes", "cand-10088"),
    (103, "which he commissioned from Marco Ricci", "cand-10088", "The relative clause refers to the landscapes; he is Zanetti."),
    (103, "he commissioned", "cand-2838", "Anaphoric reference to Zanetti as commissioner."),
    (103, "Marco Ricci", "cand-2149"),
    (103, "he also owned", "cand-2838"),
    (103, "pastels and miniatures", "cand-10089"),
    (103, "Rosalba", "cand-0581", "Name continues as Camera on L104 in S0 OCR; print reads Carriera."),
    (104, "Camera", "cand-0581", "OCR reads Camera; the print reads Carriera, recorded as an S2 correction only."),
    (104, "Canaletto", "cand-0498"),
    (104, "Zuccarelli", "cand-2879"),
    (104, "the medals and gems", "cand-2848"),
    (104, "London", "cand-1422"),
    (104, "Paris", "cand-4653"),
    (104, "Rotterdam", "cand-10072"),
    (104, "Vienna", "cand-2772"),
    (104, "his large collection of prints", "cand-2850", "The possessive refers to Zanetti; this is the existing S1 print-collection locator."),
    (105, "This collection", "cand-2850"),
    (105, "him", "cand-2838", "Anaphoric reference to Zanetti."),
    (105, "he wrote", "cand-2838", "The quotation is attributed to Zanetti in 1752."),
    (105, "in 1752", "cand-2838"),
    (105, "a collection of prints", "cand-2850"),
    (105, "I have assembled a collection of prints in Italy and on my travels which exceeds anything that might be expected of a private citizen", "cand-2850", "Quoted first-person statement by Zanetti; note 6 is pending."),
    (105, "Italy", "cand-3461", "Place named within Zanetti's quotation."),
    (105, "any rare print by any artist you ask for", "cand-2850", "The sentence continues beyond this segment; preserve the exception wording as incomplete."),
    (105, "the dish engraved with a Bacchanal by Annibale", "cand-10090"),
    (105, "Annibale", "cand-0576"),
]
for spec in mention_specs:
    add_mention(*spec)

corrections = [
    {"source_line": 102, "ocr": "thereis", "print": "there is", "basis": "CHP-13.pdf physical page 11."},
    {"source_line": 102, "ocr": "showthat", "print": "show that", "basis": "CHP-13.pdf physical page 11."},
    {"source_line": 104, "ocr": "Camera", "print": "Carriera", "basis": "CHP-13.pdf physical page 11."},
]


def excerpt(first, last, start_text, end_text):
    local = "\n".join(body_lines[number] for number in range(first, last + 1))
    start = local.find(start_text)
    if start < 0:
        raise SystemExit(f"statement opening text missing: {start_text!r}")
    end = local.find(end_text, start)
    if end < 0:
        raise SystemExit(f"statement closing text missing: {end_text!r}")
    return local[start:end + len(end_text)]


note_lines = {1: "L227-L228", 2: "L229", 3: "L230", 4: "L231", 5: "L232", 6: "L233", 7: "L234"}


def note_ref(marker):
    return {
        "footnote_marker": str(marker),
        "footnote_printed_page": 342,
        "footnote_text_pending": True,
        "footnote_segment": NOTES,
        "footnote_line_range": note_lines[marker],
        "footnote_body_link_status": "pending",
    }


def add_statement(suffix, subject, obj, predicate, first, last, qfirst, qlast, claim,
                  qualification, mentioned, *, speaker="Haskell",
                  layer="authorial narrative", notes=(), relation_candidate=False,
                  cross_refs=()):
    sid = f"st-chp13-p342-{suffix}"
    if sid in statement_by_id:
        raise SystemExit(f"duplicate statement ID: {sid}")
    quote = excerpt(first, last, qfirst, qlast)
    ids = list(dict.fromkeys(mentioned + [candidate for candidate in (subject, obj) if candidate]))
    if any(cid not in all_candidate_ids for cid in ids):
        raise SystemExit(f"missing candidate FK: {sid}")
    qualifiers = {
        "source_line_start": first,
        "source_line_end": last,
        "printed_page": 342,
        "pdf_physical_page": 11,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": ids,
        "ocr_corrections": [row for row in corrections if first <= row["source_line"] <= last],
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if notes:
        refs = [note_ref(marker) for marker in notes]
        qualifiers["footnote_refs"] = refs
        qualifiers["footnote_marker"] = refs[0]["footnote_marker"] if len(refs) == 1 else [row["footnote_marker"] for row in refs]
        qualifiers["footnote_printed_page"] = 342
        qualifiers["footnote_text_pending"] = True
        qualifiers["footnote_body_link_status"] = "pending"
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross_refs:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(
            qualifiers.get("cross_reference_segments", []) + list(cross_refs)
        ))
    new_statements.append({
        "statement_id": sid,
        "segment_id": BODY,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })


add_statement("tessin_used_zanetti_taste_and_scholarship", "cand-2554", "cand-2838",
              "used_zanettis_taste_and_scholarship_to_increase_own_collections", 99, 99,
              "use of Zanetti’s taste", "his own collections.",
              "The p.341 sentence continues: Tessin used Zanetti's taste and scholarship to increase his own collections.",
              "The source begins this clause on p.341 L96 with 'and he made'; note 1 maps to L227–228 and remains pending.",
              ["cand-2554", "cand-2838"], notes=(1,), relation_candidate=True, cross_refs=(PREVIOUS,))
add_statement("tessin_sent_protege_to_zanetti_for_instruction", "cand-2554", "cand-10077",
              "sent_a_young_protege_to_zanetti_for_instruction", 99, 99,
              "He sent him a young protégé", "Connoisseurs’",
              "Tessin sent a young protégé to Zanetti for instruction; the quoted letter describes the intended progression from work for inexperienced buyers to work for connoisseurs.",
              "The protégé is unnamed. Preserve the French quotation and the source's spelling; note 1 remains pending.",
              ["cand-2554", "cand-2838", "cand-10077"], notes=(1,), relation_candidate=True,
              speaker="Haskell reporting Tessin's letter, with a French quotation")
add_statement("young_protege_died", "cand-10077", None,
              "died_almost_immediately", 99, 99,
              "the unfortunate young man", "almost immediately.",
              "The unnamed young protégé died almost immediately, according to Haskell's account.",
              "No cause or more precise date is supplied; note 2 remains pending.",
              ["cand-10077"], notes=(2,))
add_statement("tessin_sent_messages_to_tiepolo_through_zanetti", "cand-2554", "cand-2569",
              "sent_friendly_messages_to_tiepolo_through_zanetti_hoping_he_was_not_offended", 100, 101,
              "Tessin sent friendly messages", "Stockholm.",
              "Through Zanetti, Tessin sent friendly messages to Tiepolo, hoping he had not been offended by the King of Sweden's refusal.",
              "The sentence begins on p.342 after 'Through Zanetti' at p.341 L99. Tessin's hope does not establish Tiepolo's actual reaction; note 3 remains pending.",
              ["cand-2554", "cand-2838", "cand-2569"], notes=(3,), relation_candidate=True, cross_refs=(PREVIOUS,))
add_statement("swedish_king_refused_tiepolo_sum", "cand-10078", "cand-2569",
              "refused_to_pay_sum_to_lure_tiepolo_to_stockholm", 100, 101,
              "the King of Sweden’s refusal", "Stockholm.",
              "The King of Sweden refused the exorbitant sum required to lure Tiepolo to Stockholm.",
              "The monarch and sum are unidentified; Haskell reports Tessin hoped Tiepolo was not offended. No response by Tiepolo is asserted; note 3 remains pending.",
              ["cand-10078", "cand-2569", "cand-4790"], notes=(3,),
              speaker="Haskell reporting the content of Tessin's messages")
add_statement("tessin_bought_zuccarelli_pictures", "cand-2554", "cand-10079",
              "bought_pictures_by_zuccarelli_from_zanetti", 101, 101,
              "bought from Zanetti pictures by Zuccarelli", "Zuccarelli",
              "Tessin bought pictures by Zuccarelli from Zanetti.",
              "The pictures are unnamed and uncounted; note 4 remains pending.",
              ["cand-2554", "cand-2838", "cand-10079", "cand-2879"], notes=(4,), relation_candidate=True)
add_statement("tessin_bought_nogari_pictures", "cand-2554", "cand-10080",
              "bought_pictures_by_nogari_from_zanetti", 101, 101,
              "and Nogari", "Nogari",
              "Tessin also bought pictures by Nogari from Zanetti.",
              "The pictures are unnamed and uncounted; note 4 remains pending.",
              ["cand-2554", "cand-2838", "cand-10080", "cand-1743"], notes=(4,), relation_candidate=True)
add_statement("tessin_bought_crespi_prints", "cand-2554", "cand-10081",
              "bought_prints_by_crespi_from_zanetti", 101, 101,
              "as well as prints by G. M. Crespi", "Crespi",
              "Tessin also bought prints by G. M. Crespi from Zanetti.",
              "No print titles or count are given; note 4 remains pending.",
              ["cand-2554", "cand-2838", "cand-10081", "cand-0871"], notes=(4,), relation_candidate=True)
add_statement("zanetti_facilitated_gai_commission", "cand-2554", "cand-10082",
              "commissioned_figure_from_gai_through_zanettis_good_offices", 101, 101,
              "used his good offices to commission", "the sculptor Gai",
              "Through Zanetti's good offices, Tessin commissioned a figure from the sculptor Gai.",
              "The body reports a commission, not its completion; note 4 remains pending.",
              ["cand-2554", "cand-2838", "cand-10082", "cand-1099"], notes=(4,), relation_candidate=True)
add_statement("tessin_assessed_gai_as_half_michelangelo", "cand-2554", "cand-1099",
              "considered_gai_un_demi_michel_ange", 101, 101,
              "whom he considered to be", "un demi-Michel Ange",
              "Tessin considered Gai 'un demi-Michel Ange'.",
              "This is Tessin's quoted assessment as reported by Haskell, not an objective ranking; note 4 remains pending.",
              ["cand-2554", "cand-1099"], notes=(4,), speaker="Haskell reporting Tessin's assessment")
add_statement("gai_figure_intended_to_pair_with_tessins_bathsheba", "cand-10082", "cand-10083",
              "was_intended_to_represent_venus_and_pair_with_tessins_bathsheba", 101, 101,
              "The figure was, characteristically enough", "qui m’appartient’.",
              "The commissioned figure was intended to represent a Venus emerging from the Baths and to pair with a Bathsheba by Giovanni da Bologna.",
              "Retain the intended future relation; no completion or title is inferred; note 4 remains pending.",
              ["cand-10082", "cand-10083", "cand-10084"], notes=(4,), relation_candidate=True,
              speaker="Haskell with an embedded quotation attributed to Tessin")
add_statement("tessin_owned_giovanni_da_bologna_bathsheba", "cand-2554", "cand-10083",
              "said_the_bathsheba_by_giovanni_da_bologna_belonged_to_him", 101, 101,
              "une Bathsheba", "qui m’appartient’.",
              "In Tessin's quoted words, the Bathsheba by Giovanni da Bologna belonged to him.",
              "The ownership claim is spoken by Tessin within the quotation; note 4 remains pending.",
              ["cand-2554", "cand-10083", "cand-10084"], notes=(4,), relation_candidate=True,
              speaker="Tessin, quoted by Haskell", layer="embedded first-person quotation")
add_statement("zanetti_intermediary_between_venice_and_europe", "cand-2838", "cand-3462",
              "frequently_acted_as_intermediary_between_venice_and_europe", 102, 102,
              "It is thus clear", "the rest of Europe.",
              "Haskell says Zanetti frequently acted as an intermediary between Venice and the rest of Europe.",
              "This is an authorial summary; specific transactions are recorded separately.",
              ["cand-2838", "cand-2844", "cand-2719", "cand-3462"], relation_candidate=True)
add_statement("zanetti_collections_limited_contemporary_art_outside_venice", "cand-2838", None,
              "collections_reflected_little_interest_in_contemporary_art_outside_venice", 102, 102,
              "But his actual collections", "his own city.",
              "Haskell says Zanetti's collections reflected very little interest in contemporary art outside Venice.",
              "This is a qualified summary, not a claim that he owned no such works.",
              ["cand-2838", "cand-2719"])
add_statement("zanetti_owned_brand_and_dietrich_pictures", "cand-2838", "cand-10085",
              "owned_pictures_by_brand_and_dietrich", 102, 102,
              "He owned pictures", "Brand and Dietrich,",
              "Zanetti owned pictures by the German artists Brand and Dietrich.",
              "No specific pictures are titled or counted.",
              ["cand-2838", "cand-10085", "cand-0445", "cand-0920"])
add_statement("no_evidence_zanetti_bought_modern_french_or_english_works", "cand-2838", None,
              "no_evidence_he_bought_modern_french_or_english_paintings_drawings_or_prints", 102, 102,
              "but thereis no evidence", "prints,",
              "Haskell reports no evidence that Zanetti ever bought modern French or English paintings, drawings, or prints.",
              "Preserve this as a statement about the surviving evidence, not proof that no such purchase occurred.",
              ["cand-2838", "cand-5317", "cand-8983"], speaker="Haskell")
add_statement("older_works_acquired_abroad_were_influential", "cand-10086", "cand-2838",
              "some_older_works_acquired_in_france_and_england_were_significant_and_influential", 102, 102,
              "though some of the older works", "his taste.",
              "Some older works Zanetti acquired in France and England were of great significance and proved influential in the development of his taste.",
              "The works and individual acquisitions remain unidentified; do not infer the kind of influence beyond the source's phrase.",
              ["cand-10086", "cand-2838", "cand-5317", "cand-8983"])
add_statement("zanetti_owned_three_sebastiano_history_paintings", "cand-2838", "cand-10087",
              "owned_three_history_paintings_by_sebastiano", 103, 103,
              "Besides three history paintings", "by Sebastiano",
              "Zanetti's collection included three history paintings by Sebastiano.",
              "The passage gives no titles; 'Sebastiano' remains a provisional S1 mapping pending S3.",
              ["cand-2838", "cand-10087", "cand-2154"])
add_statement("zanetti_commissioned_marco_ricci_landscapes", "cand-2838", "cand-10088",
              "commissioned_about_six_landscapes_from_marco_ricci", 103, 103,
              "half a dozen landscapes", "from Marco Ricci",
              "Zanetti commissioned about six landscapes from Marco Ricci.",
              "Half a dozen is retained as the source's approximate count; no titles are supplied.",
              ["cand-2838", "cand-10088", "cand-2149"], relation_candidate=True)
add_statement("zanetti_owned_carriera_pastels_and_miniatures", "cand-2838", "cand-10089",
              "owned_pastels_and_miniatures_by_rosalba_carriera", 103, 104,
              "he also owned pastels and miniatures", "Camera",
              "Zanetti also owned pastels and miniatures by Rosalba Carriera.",
              "The artist's name is split at the line break and OCR reads Camera; the print reads Carriera.",
              ["cand-2838", "cand-10089", "cand-0581"])
add_statement("zanetti_admired_canaletto_and_zuccarelli_early", "cand-2838", None,
              "admired_canaletto_and_zuccarelli_at_the_start_of_their_careers", 104, 104,
              "was a keen admirer", "their careers.",
              "Zanetti was a keen admirer of Canaletto and Zuccarelli at the very beginning of their careers.",
              "Retain Haskell's timing and characterization; do not infer a specific purchase or relationship.",
              ["cand-2838", "cand-0498", "cand-2879"])
add_statement("zanetti_brought_medals_and_gems_from_european_cities", "cand-2838", "cand-2848",
              "brought_medals_and_gems_back_from_london_paris_rotterdam_and_vienna", 104, 104,
              "the medals and gems", "Vienna,",
              "Zanetti brought medals and gems back from London, Paris, Rotterdam, and Vienna.",
              "The source gives neither dates nor individual objects; note 5 remains pending.",
              ["cand-2838", "cand-2848", "cand-1422", "cand-4653", "cand-10072", "cand-2772"],
              notes=(5,))
add_statement("zanetti_had_large_print_collection", "cand-2838", "cand-2850",
              "had_a_large_collection_of_prints", 104, 104,
              "his large collection of prints", "prints.",
              "Zanetti had a large collection of prints, which Haskell describes as especially important for its novelty.",
              "The print-collection locator is reused; note 5 remains pending.",
              ["cand-2838", "cand-2850"], notes=(5,))
add_statement("zanetti_was_proud_of_print_collection", "cand-2838", "cand-2850",
              "took_endless_pride_in_print_collection", 105, 105,
              "This collection was the source", "to him.",
              "The print collection was a source of endless pride to Zanetti.",
              "This is Haskell's description; note 6 remains pending.",
              ["cand-2838", "cand-2850"], notes=(6,))
add_statement("zanetti_1752_described_print_collection", "cand-2838", "cand-2850",
              "said_his_collection_exceeded_expectations_for_private_citizens", 105, 105,
              "With the greatest effort and expense", "private citizen.",
              "In 1752 Zanetti wrote that, with great effort and expense, he had assembled in Italy and on his travels a print collection exceeding what might be expected of a private citizen.",
              "First-person quotation attributed to Zanetti; retain the source's self-characterization and note 6 remains pending.",
              ["cand-2838", "cand-2850"], notes=(6,),
              speaker="Zanetti, quoted by Haskell", layer="embedded first-person quotation")
add_statement("zanetti_1752_rare_print_exception_fragment", "cand-2838", "cand-10090",
              "said_he_could_show_requested_rare_prints_except_an_unfinished_list", 105, 105,
              "Indeed I can hope", "Annibale",
              "In the 1752 quotation, Zanetti says he can hope to show any rare print requested, excepting a dish engraved with a Bacchanal by Annibale and a further object whose description continues on p.343.",
              "The sentence is incomplete at this segment boundary; do not infer why the items are excepted or whether the dish was in his collection; note 7 remains pending.",
              ["cand-2838", "cand-2850", "cand-10090", "cand-0576"], notes=(7,),
              speaker="Zanetti, quoted by Haskell", layer="embedded first-person quotation", cross_refs=(NEXT,))

all_candidates = sorted(candidates + new_candidates, key=lambda row: row["candidate_id"])
all_mentions = sorted(
    mentions + new_mentions,
    key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]),
)
all_statements = sorted(statements + new_statements, key=lambda row: row["statement_id"])
for key, rows in (("candidate_id", all_candidates), ("mention_id", all_mentions), ("statement_id", all_statements)):
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        raise SystemExit(f"duplicate {key}")
for row in new_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}: {row['surface_form']!r}")
for row in new_statements:
    if row["segment_id"] != BODY or row["origin"] != "book":
        raise SystemExit(f"invalid statement metadata: {row['statement_id']}")
    q = row["qualifiers"]
    if not (98 <= q["source_line_start"] <= q["source_line_end"] <= 105):
        raise SystemExit(f"invalid source line range: {row['statement_id']}")
    if any(cid not in all_candidate_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"statement candidate FK missing: {row['statement_id']}")

# p.341's open clause is now closed by p.342 L99; the prior page stays partial
# until its own notes and Plate 58a visual reference are reviewed.
previous = statement_by_id[PREVIOUS_STATEMENT]
previous["qualifiers"]["qualification"] = (
    "The p.341 L96 clause is completed at p.342 L99: Tessin used Zanetti's taste and scholarship to increase his own collections. "
    "Printed p.342 note 1 maps to L227-L228 and remains pending."
)
previous["qualifiers"]["cross_reference_segments"] = [BODY]
coverage[PREVIOUS].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "note": "Printed p.341 body reviewed against CHP-13.pdf physical page 10. Its final clause is closed at p.342 L99; notes 1–4 map to consolidated notes L223–226 and remain pending in source order. Plate 58a remains a cross-reference candidate pending review of its visual segment. OCR corrections are recorded in S2 only.",
})
coverage[BODY].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L98-105",
    "note": "Printed p.342 body reviewed against CHP-13.pdf physical page 11. Notes 1–7 map to consolidated notes L227–234 and remain pending in source order. The final quotation ends with 'and the lascivious' and continues on p.343 L108; preserve the open exception list. OCR corrections are recorded in S2 only.",
})
coverage_rows = [coverage[row["segment_id"]] for row in coverage_rows]

print(f"p.342 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("candidate additions:")
for row in new_candidates:
    print(f"  {row['candidate_id']} [{row['suggested_type']}] {row['canonical_name']}")
print("statement additions:")
for row in new_statements:
    q = row["qualifiers"]
    quote = row["original_quote"].replace("\n", " ↵ ")
    print(f"  {row['statement_id']} L{q['source_line_start']}-{q['source_line_end']} "
          f"{row['predicate']} [{row['subject_candidate_id']} -> {row['object_candidate_id'] or '—'}]: {quote}")
print("mention counts by candidate: " + ", ".join(
    f"{cid}={count}" for cid, count in sorted(Counter(row["candidate_id"] for row in new_mentions).items())
))
print("coverage: p.341 continuation closed at p.342 L99; p.341 and p.342 remain partial for pending notes/visual cross-reference")
print(f"totals: {len(all_candidates)} candidates, {len(all_mentions)} mentions, {len(all_statements)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, all_candidates)
write_csv(mention_path, mention_fields, all_mentions)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
