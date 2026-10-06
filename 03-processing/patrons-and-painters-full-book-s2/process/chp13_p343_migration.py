"""Controlled S2 migration for printed p.343; dry-run by default."""
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
BODY = "chp-13:13_CHP-13_intro:l107-114"
PREVIOUS = "chp-13:13_CHP-13_intro:l98-105"
NEXT = "chp-13:13_CHP-13_intro:l116-122"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BODY_SHA = "743ef09cf9ff747cb574bdd900aabff98a8567d461a268ca362c5aa3dfd5ef71"
BACKUP_SUFFIX = ".bak-s2-chp13-p343-20261003"
PREVIOUS_STATEMENT = "st-chp13-p342-zanetti_1752_rare_print_exception_fragment"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.343 S2 migration")
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
if source_lines[106] != "[Page 343]":
    raise SystemExit("p.343 page anchor changed")
body_text = "\n".join(source_lines[106:114])
if hashlib.sha256(body_text.encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("p.343 source segment changed")
for line, required in {
    108: "prints of Giulio Romano engraved by Marc’Antonio",
    109: "Yet although completeness was his principal aim",
    110: "Mannerist and ‘picturesque’ works",
    111: "the younger A. M. Zanetti",
    112: "rediscovery of the process for making chiaroscuro woodcuts",
    113: "the etchings of Tiepolo",
    114: "Delle Antiche Statue Greche e Romane",
}.items():
    if required not in source_lines[line - 1]:
        raise SystemExit(f"required p.343 text missing at L{line}")

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
    len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions), len(statements),
)
if state != (10077, 10090, 21704, 9672):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment_id in (BODY, PREVIOUS, NEXT, NOTES):
    if segment_id not in coverage:
        raise SystemExit(f"required coverage row missing: {segment_id}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.343 is not queued/pending")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.342 is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("chapter 13 notes are not queued/pending")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.343 rows already exist")
if PREVIOUS_STATEMENT not in statement_by_id:
    raise SystemExit(f"required p.342 continuation statement missing: {PREVIOUS_STATEMENT}")

new_candidates = []
new_mentions = []
new_statements = []
candidate_specs = [
    ("cand-10091", "Lascivious prints of Giulio Romano engraved by Marc’Antonio with Aretino’s sonnets", "work",
     "The 1752 quotation identifies this print group but says Zanetti had never seen it. Marc’Antonio and Aretino remain separate name candidates pending S3.", 108),
    ("cand-10092", "Marc’Antonio (engraver named with Giulio Romano prints; identity pending)", "person",
     "The source gives only the name Marc’Antonio. Do not identify him as Marcantonio Raimondi before S3.", 108),
    ("cand-10093", "Aretino (author named for sonnets accompanying Giulio Romano prints; identity pending)", "person",
     "The source gives only the surname Aretino in a possessive construction. Retain for S3 identity alignment.", 108),
    ("cand-10094", "Prince of Liechtenstein (recipient of Zanetti’s woodcut set; identity not stated here)", "person",
     "The body names the title but not the prince. Keep separate from named Liechtenstein candidates until S3.", 112),
    ("cand-10095", "Mannerist and picturesque works resembling rococo in Zanetti’s print preferences", "term",
     "Haskell groups the works by stylistic resemblance and collecting preference; preserve this as his characterization.", 110),
    ("cand-10096", "Works by Ugo da Carpi and Parmigianino engraved by Faldoni for Zanetti", "work",
     "The passage gives no individual titles or count. It says Zanetti had the works engraved by Faldoni.", 110),
    ("cand-10097", "Prints by Rembrandt and Callot bought by Zanetti on foreign travels", "work",
     "The artists stand for prints in this discussion; the passage does not identify individual print titles.", 111),
    ("cand-10098", "Twelve drawings by Castiglione engraved by Zanetti in 1759", "work",
     "The source gives a count, artist, agent, and year but no individual drawing titles.", 111),
    ("cand-10099", "Artists and expert connoisseur collectors who prefer lively broad-stroke prints", "term",
     "A group described in the younger A. M. Zanetti’s quoted preface; its members are not named.", 111),
    ("cand-10100", "General public preferring carefully finished high-contrast prints", "term",
     "A readership group in the younger A. M. Zanetti’s quoted distinction; do not treat as every individual reader.", 111),
    ("cand-10101", "Unnamed English, French, and Venetian friends dedicated individual woodcut sheets", "term",
     "The passage identifies recipient categories, not individual people or organizations.", 112),
    ("cand-10102", "Rococo and neo-classical styles in Haskell’s account of Zanetti’s taste", "term",
     "Haskell says the two styles were not in conflict for Zanetti and similar amateurs; retain as an interpretive claim.", 113),
    ("cand-10103", "Etchings by Tiepolo published by Zanetti", "work",
     "The text refers to Tiepolo’s etchings as a group and says Zanetti was the first to publish them; note 4 remains pending.", 113),
]
new_ids = {spec[0] for spec in candidate_specs}
if new_ids & set(candidate_by_id):
    raise SystemExit(f"p.343 candidate IDs already exist: {sorted(new_ids & set(candidate_by_id))}")
for cid, name, kind, detail, line in candidate_specs:
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid, "canonical_name": name, "suggested_type": kind, "status": "open",
        "detail": detail, "candidate_origin": "body-mention", "candidate_source_ref": f"{BODY}#L{line}",
    })
    new_candidates.append(row)
all_candidate_ids = set(candidate_by_id) | new_ids

body_lines = {number: source_lines[number - 1] for number in range(107, 115)}
segment_text = "\n".join(body_lines[number] for number in range(107, 115))
line_offsets = {}
offset = 0
for number in range(107, 115):
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
        "mention_id": f"m-s2-ch13-p343-{len(new_mentions) + 1:03d}",
        "segment_id": BODY, "candidate_id": cid, "surface_form": surface,
        "start_char": start, "end_char": start + len(surface), "note": note,
    })
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention FK missing: {cid}")
    new_mentions.append(row)


mention_specs = [
    (108, "prints of Giulio Romano", "cand-10091"),
    (108, "Giulio Romano", "cand-1194"),
    (108, "Marc’Antonio", "cand-10092"),
    (108, "Aretino’s", "cand-10093"),
    (108, "these", "cand-10091", "Anaphoric reference to the Giulio Romano prints."),
    (108, "Italy", "cand-3461"), (108, "Holland", "cand-6084"),
    (108, "France", "cand-5317"), (108, "England", "cand-8983"),
    (108, "a number of copies of some print", "cand-2850"),
    (108, "a single fine copy", "cand-2850"),
    (108, "three or four or even more copies of a rare print", "cand-2850"),
    (108, "several different examples of one", "cand-2850"),
    (108, "one little print missing from my collection", "cand-2850"),
    (108, "all the spare copies", "cand-2850"),
    (109, "completeness was his principal aim", "cand-2838"),
    (109, "certain preferences", "cand-10095"),
    (110, "Mannerist and ‘picturesque’ works", "cand-10095"),
    (110, "the rococo", "cand-10102"),
    (110, "Ugo da Carpi", "cand-0568"),
    (110, "Parmigianino", "cand-1839"),
    (110, "whom he had engraved by", "cand-10096", "The works are by Ugo da Carpi and Parmigianino; Zanetti is the commissioning subject."),
    (111, "Faldoni", "cand-0988"),
    (111, "Rembrandtand", "cand-2117", "OCR spacing correction is recorded in S2 only."),
    (111, "Callot", "cand-0482"),
    (111, "whomhe bought on his foreign travels", "cand-10097", "OCR spacing correction is recorded in S2 only."),
    (111, "Castiglione", "cand-0602"),
    (111, "twelve of whose drawings he himself engraved in 1759", "cand-10098"),
    (111, "the younger A. M. Zanetti", "cand-2856"),
    (111, "artists and, with them, those collectors who are held to be perfect connoisseurs", "cand-10099"),
    (111, "the general public", "cand-10100"),
    (111, "carefully finished prints", "cand-10100"),
    (111, "strong contrasts of light and shade", "cand-10100"),
    (111, "Zanetti belonged in the first of these two groups", "cand-2838"),
    (112, "Zanetti himself", "cand-2838"),
    (112, "the process for making chiaroscuro woodcuts in three or four different colours", "cand-2852"),
    (112, "during his \" stay in London", "cand-2838", "The OCR stray quote is corrected against the print in S2 only."),
    (112, "London", "cand-1422"),
    (112, "about fifty cuts in all", "cand-2853"),
    (112, "copied or adapted from his Parmigianino drawings", "cand-2853"),
    (112, "Parmigianino", "cand-1839", "The possessive refers to the drawings after Parmigianino."),
    (112, "the Prince of Liechtenstein", "cand-10094"),
    (112, "the set as a whole", "cand-2853"),
    (112, "individual sheets", "cand-2853"),
    (112, "English, French and Venetian friends", "cand-10101"),
    (112, "the scholarly and the fanciful", "cand-2838", "Haskell's interpretation of Zanetti's taste and the woodcut set."),
    (113, "the rococo and the neo-classical", "cand-10102"),
    (113, "Zanetti", "cand-2838"),
    (113, "a passion for antiquity", "cand-2838"),
    (113, "the etchings of Tiepolo", "cand-10103"),
    (113, "he was the first to publish", "cand-2838"),
    (113, "of a lively and extremely spirited taste and worthy of the highest praise", "cand-10103"),
    (113, "Francesco Algarotti", "cand-0041"),
    (113, "apparent contradictions in his taste", "cand-0041", "The possessive refers to Algarotti."),
    (113, "Zanetti felt no such qualms", "cand-2838"),
    (114, "His most important work", "cand-2846"),
    (114, "Delle Antiche Statue Greche e Romane", "cand-2846"),
    (114, "by Albrizzi", "cand-0025"),
    (114, "In it", "cand-2846", "The pronoun refers to Delle Antiche Statue Greche e Romane."),
]
for spec in mention_specs:
    add_mention(*spec)

corrections = [
    {"source_line": 108, "ocr": "Aretino’s.sonnets", "print": "Aretino’s sonnets", "basis": "CHP-13.pdf physical page 12."},
    {"source_line": 108, "ocr": "’ ' -", "print": "’", "basis": "CHP-13.pdf physical page 12; remove trailing OCR artifacts after the quotation."},
    {"source_line": 111, "ocr": "Rembrandtand", "print": "Rembrandt and", "basis": "CHP-13.pdf physical page 12."},
    {"source_line": 111, "ocr": "whomhe", "print": "whom he", "basis": "CHP-13.pdf physical page 12."},
    {"source_line": 112, "ocr": "He - revived", "print": "He revived", "basis": "CHP-13.pdf physical page 12."},
    {"source_line": 112, "ocr": 'his " stay', "print": "his stay", "basis": "CHP-13.pdf physical page 12."},
    {"source_line": 113, "ocr": "Zanetti, had", "print": "Zanetti had", "basis": "CHP-13.pdf physical page 12."},
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


note_map = {
    1: (343, "L235"), 2: (343, "L236"), 3: (343, "L237"), 4: (343, "L238"),
    6: (342, "L233"),
}


def note_ref(marker):
    page, line = note_map[marker]
    return {
        "footnote_marker": str(marker), "footnote_printed_page": page,
        "footnote_text_pending": True, "footnote_segment": NOTES,
        "footnote_line_range": line, "footnote_body_link_status": "pending",
    }


def add_statement(suffix, subject, obj, predicate, first, last, qfirst, qlast, claim,
                  qualification, mentioned, *, speaker="Haskell", layer="authorial narrative",
                  notes=(), relation_candidate=False, cross_refs=()):
    sid = f"st-chp13-p343-{suffix}"
    if sid in statement_by_id:
        raise SystemExit(f"duplicate statement ID: {sid}")
    quote = excerpt(first, last, qfirst, qlast)
    ids = list(dict.fromkeys(mentioned + [candidate for candidate in (subject, obj) if candidate]))
    if any(cid not in all_candidate_ids for cid in ids):
        raise SystemExit(f"missing candidate FK: {sid}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last,
        "printed_page": 343, "pdf_physical_page": 12,
        "claim": claim, "speaker": speaker, "text_layer": layer,
        "qualification": qualification, "mentioned_candidate_ids": ids,
        "ocr_corrections": [row for row in corrections if first <= row["source_line"] <= last],
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if notes:
        refs = [note_ref(marker) for marker in notes]
        qualifiers["footnote_refs"] = refs
        qualifiers["footnote_marker"] = refs[0]["footnote_marker"] if len(refs) == 1 else [r["footnote_marker"] for r in refs]
        qualifiers["footnote_text_pending"] = True
        qualifiers["footnote_body_link_status"] = "pending"
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross_refs:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(
            qualifiers.get("cross_reference_segments", []) + list(cross_refs)
        ))
    new_statements.append({
        "statement_id": sid, "segment_id": BODY,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })


add_statement("zanetti_never_seen_giulio_romano_prints", "cand-2838", "cand-10091",
              "said_he_had_never_seen_giulio_romano_prints", 108, 108,
              "I have never seen these", "England.",
              "In the 1752 quotation, Zanetti says he had never seen the Giulio Romano prints engraved by Marc’Antonio with Aretino’s sonnets in Italy, Holland, France, or England.",
              "The quotation continues the exception list begun at p.342 L105; note 6 cites the 1752 letter, while note 7 concerns the Annibale dish. The printed phrase's names and claim remain at the source's level.",
              ["cand-2838", "cand-10091", "cand-1194", "cand-10092", "cand-10093", "cand-3461", "cand-6084", "cand-5317", "cand-8983"],
              speaker="Zanetti, quoted by Haskell", layer="embedded first-person quotation", notes=(6,), cross_refs=(PREVIOUS,))
add_statement("zanetti_preferred_single_fine_copy", "cand-2838", "cand-2850",
              "preferred_one_fine_copy_over_many_copies", 108, 108,
              "At various times I have owned", "of a rare print.",
              "Zanetti says he sometimes owned several copies of a print but considered one fine copy sufficient and rejected collectors' boasting about multiple copies of rare prints.",
              "First-person account in the 1752 letter; this reports his stated preference, not a count of his holdings; note 6 remains pending.",
              ["cand-2838", "cand-2850"], speaker="Zanetti, quoted by Haskell", layer="embedded first-person quotation", notes=(6,))
add_statement("zanetti_disregarded_multiple_examples", "cand-2838", "cand-2850",
              "took_little_account_of_multiple_examples_of_a_print", 108, 108,
              "And so, when I have owned several different examples", "taken little account of it.",
              "Zanetti says that when he owned several different examples of one print, even a rare one, he took little account of them.",
              "First-person account in the 1752 letter; note 6 remains pending.",
              ["cand-2838", "cand-2850"], speaker="Zanetti, quoted by Haskell", layer="embedded first-person quotation", notes=(6,))
add_statement("zanetti_exchanged_spares_for_missing_print", "cand-2838", "cand-2850",
              "gave_spare_copies_for_a_missing_print_and_made_such_exchanges", 108, 108,
              "And for one little print missing", "mad exchanges of this kind.’",
              "Zanetti says he often gave away spare copies for a print missing from his collection that he could not buy, and frequently made such exchanges.",
              "First-person account in the 1752 letter; the missing print is unidentified; note 6 remains pending.",
              ["cand-2838", "cand-2850"], speaker="Zanetti, quoted by Haskell", layer="embedded first-person quotation", notes=(6,))
add_statement("zanetti_completeness_and_selective_preferences", "cand-2838", "cand-10095",
              "aimed_at_completeness_while_showing_selective_print_preferences", 109, 109,
              "Yet although completeness", "certain preferences",
              "Haskell says completeness was Zanetti's principal aim, although he also showed certain preferences among prints.",
              "The characterization is Haskell's synthesis; the preferences are specified in the following source lines.",
              ["cand-2838", "cand-10095"])
add_statement("zanetti_preferred_mannerist_picturesque_works", "cand-2838", "cand-10095",
              "preferred_mannerist_and_picturesque_works_close_to_rococo", 110, 110,
              "above all for those Mannerist", "the rococo:",
              "Haskell says Zanetti particularly preferred Mannerist and picturesque works that most closely resembled the rococo.",
              "This is Haskell's stylistic characterization, not a formal classification assigned by Zanetti.",
              ["cand-2838", "cand-10095", "cand-10102"])
add_statement("zanetti_had_ugo_and_parmigianino_works_engraved", "cand-2838", "cand-10096",
              "had_works_by_ugo_da_carpi_and_parmigianino_engraved_by_faldoni", 110, 111,
              "Ugo da Carpi and Parmigianino", "Faldoni;",
              "Zanetti had works by Ugo da Carpi and Parmigianino engraved by Faldoni.",
              "The passage gives no titles or count; note 1 belongs to the later Castiglione drawings statement.",
              ["cand-2838", "cand-10096", "cand-0568", "cand-1839", "cand-0988"], relation_candidate=True)
add_statement("zanetti_bought_rembrandt_callot_prints_abroad", "cand-2838", "cand-10097",
              "bought_prints_by_rembrandt_and_callot_on_foreign_travels", 111, 111,
              "Rembrandtand Callot", "foreign travels;",
              "Zanetti bought prints by Rembrandt and Callot during his foreign travels.",
              "The source identifies no titles; OCR spacing is corrected in qualifiers only.",
              ["cand-2838", "cand-10097", "cand-2117", "cand-0482"], relation_candidate=True)
add_statement("zanetti_engraved_castiglione_drawings_1759", "cand-2838", "cand-10098",
              "engraved_twelve_castiglione_drawings_in_1759", 111, 111,
              "Castiglione, twelve of whose drawings", "in 1759.",
              "Zanetti himself engraved twelve drawings by Castiglione in 1759.",
              "The drawings are not individually titled; note 1 maps to L235 and remains pending.",
              ["cand-2838", "cand-10098", "cand-0602"], notes=(1,), relation_candidate=True)
add_statement("younger_zanetti_on_lively_print_preferences", "cand-2856", "cand-10099",
              "said_artists_and_expert_connoisseurs_preferred_lively_broad_stroke_prints", 111, 111,
              "There are people", "perfect connoisseurs.",
              "The younger A. M. Zanetti says artists and collectors regarded as perfect connoisseurs like prints engraved with speed, liveliness, and broad strokes.",
              "This is a quotation in the preface to a 1760 publication; note 2 maps to L236 and remains pending.",
              ["cand-2856", "cand-10099"], speaker="The younger A. M. Zanetti, quoted by Haskell",
              layer="embedded quotation", notes=(2,))
add_statement("younger_zanetti_on_general_public_print_preferences", "cand-2856", "cand-10100",
              "said_general_public_preferred_carefully_finished_high_contrast_prints", 111, 111,
              "On the other hand the general public", "at first sight.’",
              "The younger A. M. Zanetti says the general public likes carefully finished prints with strong light-and-shade contrasts that strike the imagination at first sight.",
              "This is the source's audience distinction, not a universal claim about every reader; note 2 remains pending.",
              ["cand-2856", "cand-10100"], speaker="The younger A. M. Zanetti, quoted by Haskell",
              layer="embedded quotation", notes=(2,))
add_statement("haskell_places_zanetti_in_first_print_group", "cand-2838", "cand-10099",
              "belonged_to_the_group_preferring_lively_prints", 111, 111,
              "There can be no doubt", "two groups.",
              "Haskell concludes that Zanetti belonged to the first of the two print-preference groups described by the younger namesake.",
              "This is Haskell's inference from the preceding discussion; note 2 remains pending.",
              ["cand-2838", "cand-10099", "cand-10100", "cand-2856"], notes=(2,))
add_statement("zanetti_rediscovered_chiaroscuro_woodcut_process", "cand-2838", "cand-2852",
              "considered_rediscovery_of_multicolour_chiaroscuro_woodcuts_his_most_important_achievement", 112, 112,
              "Zanetti himself considered", "different colours.",
              "Zanetti considered his rediscovery of the process for making chiaroscuro woodcuts in three or four colours his most important achievement.",
              "The technique/process candidate is reused from the index; preserve Zanetti's own evaluation as reported by Haskell.",
              ["cand-2838", "cand-2852"])
add_statement("zanetti_revived_technique_and_made_about_fifty_cuts", "cand-2838", "cand-2853",
              "revived_technique_in_london_and_made_about_fifty_cuts", 112, 112,
              "He - revived this technique", "Parmigianino drawings.",
              "During his stay in London, Zanetti revived the sixteenth-century technique and produced about fifty cuts, mostly copied or adapted from his Parmigianino drawings.",
              "The print group is not individually titled; record the OCR corrections in this line without editing S0.",
              ["cand-2838", "cand-2853", "cand-1422", "cand-1839"])
add_statement("zanetti_destroyed_plates_and_dedicated_woodcut_set", "cand-2838", "cand-2853",
              "destroyed_plates_and_dedicated_set_to_prince_of_liechtenstein", 112, 112,
              "He then destroyed the plates", "Prince of Liechtenstein,",
              "Zanetti destroyed the plates and dedicated the woodcut set as a whole to the Prince of Liechtenstein.",
              "The prince is named only by title; his identity is not resolved. Dedication note 3 maps to L237 and remains pending.",
              ["cand-2838", "cand-2853", "cand-10094"], notes=(3,), relation_candidate=True)
add_statement("zanetti_dedicated_individual_sheets_to_friends", "cand-2838", "cand-10101",
              "dedicated_individual_sheets_to_english_french_and_venetian_friends", 112, 112,
              "while individual sheets were dedicated", "Venetian friends.",
              "Individual sheets were dedicated to English, French, and Venetian friends.",
              "The recipients are unnamed; note 3 maps to L237 and remains pending.",
              ["cand-2838", "cand-2853", "cand-10101"], notes=(3,), relation_candidate=True)
add_statement("haskell_on_woodcuts_and_scholarly_fanciful_taste", "cand-2853", "cand-2838",
              "woodcuts_reflected_scholarly_and_fanciful_combination_in_zanettis_taste", 112, 113,
              "As works of art these are not very attractive", "Europe.",
              "Haskell says the woodcuts are not very attractive as works of art but are important because they faithfully reflect the scholarly and fanciful combination in Zanetti's taste and that of similar amateurs elsewhere in Europe.",
              "This is Haskell's interpretive assessment; the final word crosses onto p.343 L113.",
              ["cand-2853", "cand-2838"], cross_refs=(PREVIOUS,))
add_statement("rococo_and_neo_classical_not_in_conflict", "cand-10102", None,
              "were_not_in_conflict_for_these_amateurs", 113, 113,
              "For these men", "not in conflict.",
              "Haskell says that for these amateurs the rococo and neo-classical were not in conflict.",
              "Retain this as the author's interpretation of their taste, not a general claim about all artists or collectors.",
              ["cand-10102", "cand-2838"])
add_statement("zanetti_passion_for_antiquity_and_tiepolo_etchings", "cand-2838", "cand-10103",
              "had_passion_for_antiquity_and_enthusiasm_for_tiepolo_etchings", 113, 113,
              "Zanetti, had a passion", "worthy of the highest praise’.",
              "Haskell says Zanetti had a passion for antiquity and was equally enthusiastic about Tiepolo's etchings, which he described as lively and spirited and worthy of the highest praise.",
              "The punctuation/comma after Zanetti is an OCR error noted in S2; note 4 maps to L238 and remains pending.",
              ["cand-2838", "cand-10103", "cand-2569"], notes=(4,),
              speaker="Haskell with an embedded quotation", layer="authorial narrative with embedded quotation")
add_statement("zanetti_first_to_publish_tiepolo_etchings", "cand-2838", "cand-10103",
              "was_the_first_to_publish_tiepolo_etchings", 113, 113,
              "which he was the first to publish", "publish",
              "Haskell says Zanetti was the first to publish Tiepolo's etchings.",
              "Retain the author's attribution; footnote 4 maps to L238 and remains pending, so no publication date is added here.",
              ["cand-2838", "cand-10103", "cand-2569"], notes=(4,), relation_candidate=True)
add_statement("algarotti_retained_style_synthesis_but_worried", "cand-0041", None,
              "retained_synthesis_of_opposing_styles_but_worried_about_contradictions", 113, 113,
              "Francesco Algarotti was one", "his taste.",
              "Haskell says Algarotti was among the last to retain this synthesis of opposing styles, but his more theoretical cast of mind made him worry about apparent contradictions in his taste.",
              "This is Haskell's characterization, not an independently verified statement by Algarotti.",
              ["cand-0041", "cand-10102"])
add_statement("zanetti_felt_no_style_qualms", "cand-2838", "cand-10102",
              "felt_no_qualms_about_apparent_style_contradictions", 113, 113,
              "Zanetti felt no such qualms", "qualms.",
              "Haskell says Zanetti felt no qualms about the apparent contradictions in his taste.",
              "This refers to Haskell's preceding comparison with Algarotti.",
              ["cand-2838", "cand-10102", "cand-0041"])
add_statement("delle_antiche_statue_publication_history", "cand-2838", "cand-2846",
              "begun_in_1725_and_published_fifteen_years_later_by_albrizzi", 114, 114,
              "His most important work", "(by Albrizzi).",
              "Haskell says Zanetti's Delle Antiche Statue Greche e Romane was begun in 1725 and published fifteen years later by Albrizzi.",
              "The following sentence begins at p.343 L114 ('In it Zanetti subordinated') and continues onto p.344; the work's contents and significance remain open.",
              ["cand-2838", "cand-2846", "cand-0025"], relation_candidate=True,
              cross_refs=(NEXT,))

all_candidates = sorted(candidates + new_candidates, key=lambda row: row["candidate_id"])
all_mentions = sorted(mentions + new_mentions,
                      key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
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
    if not (107 <= q["source_line_start"] <= q["source_line_end"] <= 114):
        raise SystemExit(f"invalid source line range: {row['statement_id']}")
    if any(cid not in all_candidate_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"statement candidate FK missing: {row['statement_id']}")

# Close the p.342 quotation with its p.343 referent while keeping its p.342 anchor.
prior = statement_by_id[PREVIOUS_STATEMENT]
prior["predicate"] = "said_he_could_show_any_rare_print_except_named_dish_and_giulio_romano_prints"
prior["qualifiers"]["claim"] = (
    "In the 1752 quotation, Zanetti says he could hope to show any rare print requested except the dish engraved with a Bacchanal by Annibale and the lascivious prints of Giulio Romano engraved by Marc’Antonio with Aretino’s sonnets."
)
prior["qualifiers"]["qualification"] = (
    "The open exception list from p.342 L105 closes at p.343 L108. The second item is the Giulio Romano prints; Zanetti's following statement that he had never seen 'these' is recorded separately. Note 6 cites the 1752 letter and note 7 gives the dish quotation; both note texts remain pending."
)
prior["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
    prior["qualifiers"].get("mentioned_candidate_ids", []) +
    ["cand-10091", "cand-1194", "cand-10092", "cand-10093", "cand-3461", "cand-6084", "cand-5317", "cand-8983"]
))
# Keep original_quote anchored to its p.342 segment; the p.343 continuation is
# represented by the separate p.343 statement and cross_reference_segments.

coverage[PREVIOUS].update({
    "disposition": "reviewed", "migration_status": "partial",
    "note": "Printed p.342 body reviewed against CHP-13.pdf physical page 11. The p.342 L105 exception list is closed at p.343 L108; the second item is prints of Giulio Romano, which Zanetti says he had never seen. Notes 1–7 map to consolidated notes L227–234 and remain pending in source order.",
})
coverage[BODY].update({
    "disposition": "reviewed", "migration_status": "partial",
    "source_line_ranges": "L107-114",
    "note": "Printed p.343 body reviewed against CHP-13.pdf physical page 12. Notes 1–4 map to consolidated notes L235–238 and remain pending in source order. The final sentence begins 'In it Zanetti subordinated' and continues on p.344 L116; preserve the open clause. OCR corrections are recorded in S2 only.",
})
coverage_rows = [coverage[row["segment_id"]] for row in coverage_rows]

print(f"p.343 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements; p.342 quote closed")
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
