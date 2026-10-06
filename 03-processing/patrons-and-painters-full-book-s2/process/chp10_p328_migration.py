"""Controlled S2 migration for printed p.328 and consolidated notes L338-342."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"
PREVIOUS = "chp-10:10_CHP-10_sec_ii:l224-239"
BODY = "chp-10:10_CHP-10_sec_ii:l241-246"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BODY_SHA = "151bd8d05048bb8c096b06a1a31bc9a54ddd07f47b8e99fc0c8919b624799ce5"
BACKUP_SUFFIX = ".bak-s2-chp10-p328-20261003"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write reviewed p.328 rows after making recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != MARKDOWN_SHA:
    raise SystemExit("canonical source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_lines = {n: source_lines[n - 1] for n in range(241, 247)}
note_lines = {n: source_lines[n - 1] for n in range(273, 350)}
segment_text = {
    BODY: "\n".join(body_lines.values()),
    NOTES: "\n".join(note_lines.values()),
}
if hashlib.sha256(segment_text[BODY].encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("registered source segment changed: p.328")
if body_lines[241] != "[Page 28]" or not body_lines[246].endswith("these represent"):
    raise SystemExit("p.328 source boundaries changed")
note_slice = "\n".join(note_lines[n] for n in range(338, 343))
if not all(token in note_slice for token in ("Zanetti", "Baretti", "Vacchelli", "Cazzetta Veneta")):
    raise SystemExit("p.328 footnote range L338-342 changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}
state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (9816, 9829, 20804, 9244):
    raise SystemExit(f"unexpected table pre-state: {state}")
for sid in (PREVIOUS, BODY, NOTES):
    if sid not in coverage:
        raise SystemExit(f"required coverage row missing: {sid}")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.327 is not reviewed/partial")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.328 is not queued/pending")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"], coverage[NOTES]["source_line_ranges"]) != ("reviewed", "partial", "L325-337"):
    raise SystemExit("consolidated notes are not in the expected p.326-327 partial state")
continuation = next((row for row in statements if row["statement_id"] == "st-chp10-p327-less-offensive-poem-open"), None)
if not continuation or continuation.get("qualifiers", {}).get("continuation_status") != "open":
    raise SystemExit("p.327 poem continuation is not open")
candidate_by_id = {row["candidate_id"]: row for row in candidates}
if candidate_by_id.get("cand-9829", {}).get("canonical_name") != "Unidentified less offensive poem published to celebrate Giorgio Pisani's entry":
    raise SystemExit("expected open p.327 poem candidate not found")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.328 body rows already exist")
if any(row["segment_id"] == NOTES and 338 <= int(row.get("qualifiers", {}).get("source_line_start", 0)) <= 342 for row in statements):
    raise SystemExit("p.328 footnote statements already exist")

new_candidates = []


def add_candidate(cid, name, kind, detail, segment, line):
    if cid in candidate_ids or any(row["candidate_id"] == cid for row in new_candidates):
        raise SystemExit(f"candidate id already exists: {cid}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment}#L{line}",
    })
    new_candidates.append(row)


# p.327's open poem candidate is now identifiable from p.328 and its note.
candidate_by_id["cand-9829"]["canonical_name"] = "Il Filosofo dell'Alpi, poem published to celebrate Giorgio Pisani's entry (1780)"
candidate_by_id["cand-9829"]["suggested_type"] = "archive"
candidate_by_id["cand-9829"]["detail"] = (
    "P.327 begins an unfinished sentence about one of the less offensive poems celebrating Pisani; p.328 names it. "
    "P.328 n.1 identifies it as an ode by de la Harpe freely rendered into Italian verse by Giuseppe Fossati. "
    "This candidate denotes the poem, not the separate pamphlet/print items discussed on p.326."
)
add_candidate("cand-9830", "Giuseppe Fossati", "person", "Named in p.328 n.1 as the Venetian who freely rendered de la Harpe's ode into Italian verse; identity is not externally aligned.", NOTES, 338)
add_candidate("cand-9831", "Letter from A. M. Zanetti to A. F. Gori, 23 August 1738 (Biblioteca Marucelliana, B. VIII, 13, p. 289r)", "archive", "Haskell cites this letter for Zanetti's praise of Zuccarelli; the manuscript was not independently consulted. The printed shelfmark reads p.289r, although the OCR reads p.289c.", NOTES, 339)
add_candidate("cand-9832", "Unpublished letter from Giambattista Biffi to Signor Vacchelli (1773; Biblioteca Governativa, Cremona, MSS. aa.I.4)", "archive", "Haskell says the letter's existence was made known to him by Professor Franco Venturi and quotes Biffi's praise of Zuccarelli; the manuscript was not independently consulted.", NOTES, 341)
add_candidate("cand-9833", "Giambattista Biffi diary entry on Rousseau's death", "archive", "Haskell says Biffi wrote this reaction in his diary; no date or manuscript locator is supplied here. The statement is cited through Venturi, 1957, p.45, not independently verified.", BODY, 243)
add_candidate("cand-9834", "Arcadian ideal in eighteenth-century landscape painting", "term", "The passage discusses the conception of Arcadia as an artistic/literary ideal and contrasts artificial Arcadias with later naturalistic landscape treatment; distinguish this concept from the Arcadia Society candidate.", BODY, 243)
add_candidate("cand-9835", "Giacomo Storti", "person", "Named as printer in the 1780 imprint of Il Filosofo dell'Alpi; identity is not externally aligned.", NOTES, 338)
add_candidate("cand-9836", "Accademia Francese", "institution", "P.328 n.1 describes de la Harpe as of the French Academy; retain the source wording pending identity/alignment review.", NOTES, 338)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []


def add_mention(segment, line_no, surface, cid, note="", occurrence=0):
    line_map = body_lines if segment == BODY else note_lines
    if segment not in segment_text or cid not in all_candidate_ids:
        raise SystemExit(f"invalid mention segment/candidate: {segment} {surface!r} {cid}")
    line = line_map[line_no]
    starts = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text missing at L{line_no}: {surface!r} occurrence {occurrence}")
    first_line = min(line_map)
    start = sum(len(line_map[n]) + 1 for n in range(first_line, line_no)) + starts[occurrence]
    if segment_text[segment][start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch at L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p328-{len(new_mentions) + 1:04d}",
        "segment_id": segment,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


# p.328 body; every named object remains a book-level candidate pending S3.
add_mention(BODY, 242, "II Filosofo dell’Alpi", "cand-9829", "Completes the p.327 main-text sentence; the printed title uses initial I, checked against the page image.")
add_mention(BODY, 242, "Rousseau", "cand-2289")
add_mention(BODY, 242, "Francesco Zuccarelli", "cand-2879")
add_mention(BODY, 242, "elder Zanetti", "cand-2838", "A. M. Zanetti is identified in footnote 2; preserve the source's elder/younger distinction.")
add_mention(BODY, 242, "Consul Smith", "cand-2440")
add_mention(BODY, 243, "Arcadia", "cand-9834")
add_mention(BODY, 243, "Baretti", "cand-0245")
add_mention(BODY, 243, "Dr Johnson", "cand-1333")
add_mention(BODY, 243, "Giambattista Biffi", "cand-0373", occurrence=0)
add_mention(BODY, 243, "Beccaria", "cand-0265")
add_mention(BODY, 243, "Verri", "cand-2758")
add_mention(BODY, 243, "Zuccarelli", "cand-2879")
add_mention(BODY, 243, "Rousseau", "cand-2289")
add_mention(BODY, 243, "Biffi", "cand-0373", occurrence=1)
add_mention(BODY, 243, "that philosopher", "cand-2289", "Anaphoric reference to Rousseau in the preceding clause.")
add_mention(BODY, 243, "his diary", "cand-9833", "The antecedent is Biffi; the diary is reported by Haskell, with no manuscript locator here.")
add_mention(BODY, 244, "Arcadias", "cand-9834")
add_mention(BODY, 244, "Giuseppe Zais", "cand-2830")
add_mention(BODY, 245, "painting", "cand-1805", "The indexed concept is painting's social significance, not painting as a generic medium.")
add_mention(BODY, 246, "Gasparo Gozzi", "cand-1222")
add_mention(BODY, 246, "Venice", "cand-2719")

# p.328 footnotes L338-342: cited works, people, repositories, and locators.
add_mention(NOTES, 338, "II Filosofo del!Alpi", "cand-9829", "OCR has 'II' and 'del!'; print reads 'Il' and 'dell'.")
add_mention(NOTES, 338, "de la Harpe", "cand-1345")
add_mention(NOTES, 338, "AccademiaFrancese", "cand-9836", "OCR joins the words; the page image shows Accademia Francese.")
add_mention(NOTES, 338, "Giuseppe Fossati", "cand-9830")
add_mention(NOTES, 338, "Venezia", "cand-2719")
add_mention(NOTES, 338, "Giacomo Storti", "cand-9835")
add_mention(NOTES, 339, "A. M. Zanetti", "cand-2838")
add_mention(NOTES, 339, "A. F. Gori", "cand-1214")
add_mention(NOTES, 339, "Biblioteca Marucelliana", "cand-9493")
add_mention(NOTES, 339, "Florence", "cand-1041")
add_mention(NOTES, 339, "MSS. B. VIII, 13 p. 289c", "cand-9831", "OCR reads 289c; p.328 image reads 289r.")
add_mention(NOTES, 340, "Baretti", "cand-0245")
add_mention(NOTES, 340, "F. Venturi", "cand-2751", occurrence=0)
add_mention(NOTES, 341, "unpublished letter to Signor Vacchelli", "cand-9832")
add_mention(NOTES, 341, "Biblioteca Govcrnativa", "cand-8556", "OCR spelling; page image reads Biblioteca Governativa.")
add_mention(NOTES, 341, "Cremona", "cand-8556", "Repository candidate includes the city; this mention identifies its location.")
add_mention(NOTES, 341, "Professor Franco Venturi", "cand-2751")
add_mention(NOTES, 341, "Caro Zuccarelli", "cand-2879")
add_mention(NOTES, 342, "F. Venturi", "cand-2751")
add_mention(NOTES, 342, "Cazzetta Veneta", "cand-8729", "OCR reads 'Cazzetta'; p.328 image reads Gazzetta Veneta.")

new_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
for left, right in zip(new_mentions, new_mentions[1:]):
    if left["segment_id"] == right["segment_id"] and int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")
if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")

new_statements = []


def add_statement(sid, segment, subject, obj, predicate, start, end, page, physical, claim, quote,
                  qualification, mentioned, *, speaker="Haskell", layer="authorial narrative", extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement id already exists: {sid}")
    if quote not in segment_text[segment]:
        raise SystemExit(f"statement quote is not anchored: {sid}")
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {sid}")
    if subject and subject not in all_candidate_ids:
        raise SystemExit(f"missing subject candidate in {sid}")
    if obj and obj not in all_candidate_ids:
        raise SystemExit(f"missing object candidate in {sid}")
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": page,
        "pdf_physical_page": physical,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
    }
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": sid,
        "segment_id": segment,
        "subject_candidate_id": subject or None,
        "object_candidate_id": obj or None,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


F1 = [{"marker": 1, "segment_id": NOTES, "source_line": 338}]
F2 = [{"marker": 2, "segment_id": NOTES, "source_line": 339}]
F3 = [{"marker": 3, "segment_id": NOTES, "source_line": 340}]
F4 = [{"marker": 4, "segment_id": NOTES, "source_line": 340}]
F5 = [{"marker": 5, "segment_id": NOTES, "source_line": 341}]
F6 = [{"marker": 6, "segment_id": NOTES, "source_line": 342}]
F7 = [{"marker": 7, "segment_id": NOTES, "source_line": 342}]


def body_extra(marker, note_ids):
    return {
        "footnote_marker": marker,
        "footnote_segment": NOTES,
        "footnote_refs": {1: F1, 2: F2, 3: F3, 4: F4, 5: F5, 6: F6, 7: F7}[marker],
        "footnote_statement_ids": note_ids,
        "footnote_body_link_status": "linked",
    }


add_statement(
    "st-chp10-p328-filosofo-poem-identified", BODY, "cand-9829", "cand-9792", "identified_as_poem_for_pisani_entry",
    242, 242, 328, 61,
    "Haskell completes the p.327 sentence by identifying Il Filosofo dell'Alpi as one of the less offensive poems published to celebrate Pisani's election.",
    "election was one called II Filosofo dell’Alpi.1",
    "The sentence continues from p.327 L237. The poem is identified by title here; its attribution and translation are given in p.328 n.1.",
    ["cand-9829", "cand-1945", "cand-9792"],
    extra={"continuation_from_segment_id": PREVIOUS, "continuation_from_statement_id": "st-chp10-p327-less-offensive-poem-open", "continuation_prefix": "Among the less offensive poems that had been published to celebrate Pisani’s", "continuation_status": "closed", "footnote_marker": 1, "footnote_segment": NOTES, "footnote_refs": F1, "footnote_statement_ids": ["st-chp10-p328-n01-la-harpe-ode-imprint"], "footnote_body_link_status": "linked"},
)
add_statement(
    "st-chp10-p328-ode-rousseau-influence", BODY, "cand-9829", "cand-2289", "work_strongly_influenced_by",
    242, 242, 328, 61,
    "Haskell describes the ode as strongly influenced by Rousseau and says its spirit was partly responsible for Zuccarelli's outstanding success.",
    "As the title suggests, this enthusiastic work about the Alps and Nature, which had been translated from the French, was strongly influenced by Rousseau; and the spirit that informed it was partly responsible for the outstanding success of almost the only Venetian artist of the eighteenth century who won unqualified praise from every different kind of patron.",
    "This is Haskell's literary and causal interpretation; the passage does not establish Rousseau as the poem's sole source or cause of Zuccarelli's success.",
    ["cand-9829", "cand-2289", "cand-2879"],
)
add_statement(
    "st-chp10-p328-zuccarelli-praised-by-patrons", BODY, "cand-2879", None, "received_unqualified_praise_from_varied_patrons",
    242, 242, 328, 61,
    "Haskell characterizes Zuccarelli as almost the only eighteenth-century Venetian artist to receive unqualified praise from every kind of patron.",
    "almost the only Venetian artist of the eighteenth century who won unqualified praise from every different kind of patron",
    "Haskell's emphatic comparative assessment; preserve 'almost' and the period-specific scope.",
    ["cand-2879"],
)
add_statement(
    "st-chp10-p328-zanetti-praised-zuccarelli", BODY, "cand-2838", "cand-2879", "praised_as_never_sufficiently_lauded",
    242, 242, 328, 61,
    "Haskell says the elder A. M. Zanetti called Zuccarelli 'never sufficiently praised' as early as 1738.",
    "Francesco Zuccarelli was called ‘non mai abbastanza lodato’ by the elder Zanetti as early as 1738",
    "The Italian phrase is quoted by Haskell; p.328 n.2 cites Zanetti's letter to A. F. Gori. The letter was not independently consulted.",
    ["cand-2838", "cand-2879"],
    extra=body_extra(2, ["st-chp10-p328-n02-zanetti-letter-citation"]),
)
add_statement(
    "st-chp10-p328-smith-employed-zuccarelli", BODY, "cand-2440", "cand-2879", "employed_as_painter_repeatedly",
    242, 242, 328, 61,
    "Haskell says Consul Smith employed Zuccarelli constantly.",
    "Consul Smith employed him constantly",
    "The pronoun refers to Francesco Zuccarelli; no individual commission is specified in this sentence.",
    ["cand-2440", "cand-2879"],
)
add_statement(
    "st-chp10-p328-english-landscape-market", BODY, "cand-2879", "cand-2440", "success_with_english_explained_by_landscape_taste",
    242, 242, 328, 61,
    "Haskell says Zuccarelli's success with English patrons is readily explained by their already famous love of country-house life and landscape painting.",
    "his success with the English, whose love of country house Use and landscape painting was already famous, is easy to understand",
    "The source OCR reads 'Use'; the p.328 scan reads 'life'. This is Haskell's explanation of reception, not a claim that all English patrons shared one preference.",
    ["cand-2879", "cand-2440"],
    extra={"ocr_corrections": [{"source_line": 242, "ocr": "country house Use", "print": "country house life"}]},
)
add_statement(
    "st-chp10-p328-baretti-wrote-enthusiastically-of-zuccarelli", BODY, "cand-0245", "cand-2879", "wrote_enthusiastically_of",
    243, 243, 328, 61,
    "Haskell says Giuseppe Baretti wrote enthusiastically of Zuccarelli, despite being a critic of Venetian effeminacy and a close friend of Dr Johnson.",
    "Thus Baretti, chief scourge of the effeminate culture of Venice and close friend of Dr Johnson, wrote enthusiastically of him.3",
    "The characterization and friendship are reported by Haskell; note 3 cites Baretti, vol. I, p.279, which was not independently consulted.",
    ["cand-0245", "cand-2879", "cand-1333"],
    extra=body_extra(3, ["st-chp10-p328-n03-baretti-locator"]),
)
add_statement(
    "st-chp10-p328-biffi-friendship-with-beccaria", BODY, "cand-0373", "cand-0265", "friend_of_as_described",
    243, 243, 328, 61,
    "Haskell describes Giambattista Biffi as a friend of Cesare Beccaria.",
    "Giambattista Biffi, the friend of Beccaria and Verri",
    "This is a biographical relationship stated by Haskell; formal relation status remains for S6 review.",
    ["cand-0373", "cand-0265"],
    extra=body_extra(4, ["st-chp10-p328-n04-venturi-locator"]),
)
add_statement(
    "st-chp10-p328-biffi-friendship-with-verri", BODY, "cand-0373", "cand-2758", "friend_of_as_described",
    243, 243, 328, 61,
    "Haskell describes Giambattista Biffi as a friend of Pietro Verri.",
    "Giambattista Biffi, the friend of Beccaria and Verri",
    "This is a biographical relationship stated by Haskell; formal relation status remains for S6 review.",
    ["cand-0373", "cand-2758"],
    extra=body_extra(4, ["st-chp10-p328-n04-venturi-locator"]),
)
add_statement(
    "st-chp10-p328-biffi-praised-zuccarelli-in-letter", BODY, "cand-0373", "cand-2879", "praised_in_unpublished_letter",
    243, 243, 328, 61,
    "Haskell says Biffi spoke of Zuccarelli with a rapture he expressed for no other painter and quotes a 1773 letter praising Zuccarelli's landscape painting.",
    "speaks of him with a rapture that he expresses for no other painter5: ‘If only you could see this King of landscape painters! What softness, freshness, waving of leaves I His prints alone are not enough to reveal his merits, good though they are. Those limpid waters seem like glass on his canvas, and those lively and brilliant macchiette carry one up to Paradise. Dear Zuccarelli—thanks to you we do not have to envy the ancients.’",
    "Haskell translates and quotes an unpublished letter; note 5 identifies the addressee, date, repository and shelfmark and credits Venturi for knowledge of it. The manuscript was not independently consulted.",
    ["cand-0373", "cand-2879", "cand-9832", "cand-2674", "cand-2751"],
    extra={"footnote_marker": 5, "footnote_segment": NOTES, "footnote_refs": F5, "footnote_statement_ids": ["st-chp10-p328-n05-biffi-letter-citation"], "footnote_body_link_status": "linked", "reported_source_language": "Italian", "cited_source_independently_consulted": False},
)
add_statement(
    "st-chp10-p328-biffi-diary-on-rousseau", BODY, "cand-0373", "cand-2289", "diary_entry_praises_after_death",
    243, 243, 328, 61,
    "Haskell says Biffi later heard of Rousseau's death and wrote in his diary that Rousseau was the century's greatest genius and his father, guide, master and idol.",
    "when Biffi heard later of that philosopher’s death, he wrote in his diary6: ‘The greatest genius of the century is dead.... He was my father, my guide, my master, my idol... . .’",
    "The diary text is quoted through Haskell and cited to Venturi, 1957, p.45; neither the diary nor Venturi's cited page was independently consulted.",
    ["cand-0373", "cand-2289", "cand-9833", "cand-2751"],
    speaker="Giambattista Biffi (as quoted by Haskell)",
    layer="quoted diaristic text reported in authorial narrative",
    extra={"footnote_marker": 6, "footnote_segment": NOTES, "footnote_refs": F6, "footnote_statement_ids": ["st-chp10-p328-n06-venturi-locator"], "footnote_body_link_status": "linked"},
)
add_statement(
    "st-chp10-p328-arcadia-not-necessary-cause", BODY, None, "cand-2289", "not_necessary_cause_of_later_naturalistic_treatment",
    243, 244, 328, 61,
    "Haskell argues that later artists' more scrupulous and deeply felt treatment of nature was not necessarily a consequence of Rousseau's teaching.",
    "the more scrupulous and deeply felt treatment of nature that was adopted by later artists was by no means a necessary consequence of that philosopher’s teaching",
    "This is Haskell's qualification of a causal interpretation; it does not deny that Rousseau influenced some artists or ideas.",
    ["cand-0373", "cand-2289"],
)
add_statement(
    "st-chp10-p328-zais-neglected", BODY, "cand-2830", None, "more_authentic_country_interpreter_wholly_neglected",
    243, 244, 328, 61,
    "Haskell contrasts convincing artificial Arcadias with Giuseppe Zais, whom he calls a more authentic and robust interpreter of the countryside but says was wholly neglected.",
    "Purely artificial\nArcadias, suffused in a golden mist, were convincing enough for the most impassioned, believers in the natural life: while Giuseppe Zais, a more authentic and robust interpreter of the countryside, was wholly neglected.",
    "This is Haskell's comparative assessment of reception, not a measured claim about every patron or all of Zais's career.",
    ["cand-9834", "cand-2830"],
)
add_statement(
    "st-chp10-p328-midcentury-painting-social-question", BODY, "cand-1805", None, "importance_in_modern_life_debated",
    245, 245, 328, 61,
    "Haskell says a more basic question was widely discussed toward mid-century: whether painting had any importance in modern life.",
    "towards the middle of the century there was another, more basic problem that was being widely discussed. How far could painting be deemed to be of any importance whatsoever in modern life?",
    "This is the question framing the following discussion, not Haskell's settled answer.",
    ["cand-1805"],
)
add_statement(
    "st-chp10-p328-gozzi-criticism-for-journal-space", BODY, "cand-1222", "cand-1805", "addressed_social_value_after_criticism",
    246, 246, 328, 61,
    "Haskell says Gozzi was among the first in Venice to address painting's importance and admitted in 1760 that he had been criticized for devoting too much journal space to buildings, altars and pictures.",
    "Gasparo Gozzi was among the first to tackle the problem in Venice. Writing in 1760 he admitted that he had been attacked for devoting too much space, in his journalism to buildings, altars and pictures.7",
    "The argument Gozzi then gives is incomplete at the p.328 page break and continues on p.329; this statement covers only the completed claim about criticism and his subject matter.",
    ["cand-1222", "cand-1805", "cand-8729"],
    extra=body_extra(7, ["st-chp10-p328-n07-gazzetta-citation"]),
)

# Footnote evidence and locators; citations are not claims of independent consultation.
add_statement(
    "st-chp10-p328-n01-la-harpe-ode-imprint", NOTES, "cand-9829", "cand-9830", "ode_attributed_and_italian_rendering_credited",
    338, 338, 328, 61,
    "Haskell's note identifies Il Filosofo dell'Alpi as an ode by de la Harpe of the French Academy, freely rendered into Italian verse by Giuseppe Fossati; the imprint names Venice and Giacomo Storti, 1780.",
    note_lines[338],
    "Printed title and imprint checked against the p.328 scan; the cited poem itself was not independently consulted. The OCR joins title letters and punctuation.",
    ["cand-9829", "cand-1345", "cand-9830", "cand-9836", "cand-2719", "cand-9835"],
    speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 1, "cited_source_independently_consulted": False, "ocr_corrections": [{"source_line": 338, "ocr": "II Filosofo del!Alpi", "print": "Il Filosofo dell'Alpi"}, {"source_line": 338, "ocr": "del!AccademiaFrancese", "print": "dell'Accademia Francese"}]},
)
add_statement(
    "st-chp10-p328-n02-zanetti-letter-citation", NOTES, "cand-2838", "cand-9831", "cites_letter_as_locator_for_zuccarelli_praise",
    339, 339, 328, 61,
    "Haskell cites an A. M. Zanetti letter to A. F. Gori dated 23 August 1738, held at Biblioteca Marucelliana, for the contemporary praise of Zuccarelli.",
    note_lines[339],
    "The manuscript was not independently consulted. The image reads shelfmark page 289r; the OCR last character is corrected in S2 only.",
    ["cand-2838", "cand-1214", "cand-9831", "cand-9493", "cand-1041"],
    speaker="Haskell's note", layer="archival citation",
    extra={"footnote_marker": 2, "cited_source_independently_consulted": False, "ocr_corrections": [{"source_line": 339, "ocr": "p. 289c", "print": "p. 289r"}]},
)
add_statement(
    "st-chp10-p328-n03-baretti-locator", NOTES, "cand-0245", None, "citation_locator",
    340, 340, 328, 61,
    "Haskell's note cites Baretti, volume I, page 279, for the preceding description of Baretti's praise of Zuccarelli.",
    "3 Baretti, I, p. 279.",
    "The cited work and page were not independently consulted; the abbreviated volume citation is preserved as printed/OCRed.",
    ["cand-0245"], speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 3, "cited_source_independently_consulted": False},
)
add_statement(
    "st-chp10-p328-n04-venturi-locator", NOTES, None, "cand-2751", "citation_locator",
    340, 340, 328, 61,
    "Haskell cites F. Venturi, 1957, pages 37-76, in the discussion of Biffi's praise of Zuccarelli.",
    "4 F. Venturi, 1957, pp. 37-76.",
    "The abbreviated publication and cited pages were not independently consulted or resolved to a title here.",
    ["cand-2751", "cand-0373", "cand-2879"], speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 4, "cited_source_independently_consulted": False},
)
add_statement(
    "st-chp10-p328-n05-biffi-letter-citation", NOTES, "cand-0373", "cand-9832", "cites_unpublished_letter_and_quoted_text",
    341, 341, 328, 61,
    "Haskell says an unpublished 1773 letter to Signor Vacchelli at Biblioteca Governativa, Cremona, MSS. aa.I.4 contains Biffi's praise of Zuccarelli, and credits Professor Franco Venturi for knowledge of the letter.",
    note_lines[341],
    "The manuscript was not independently consulted. Preserve the note's '[sic]' and quoted wording; the page image clarifies the repository spelling and several OCR word breaks.",
    ["cand-0373", "cand-9832", "cand-2674", "cand-8556", "cand-2751", "cand-2879"],
    speaker="Haskell's note", layer="archival citation and reported quotation",
    extra={"footnote_marker": 5, "cited_source_independently_consulted": False, "ocr_corrections": [{"source_line": 341, "ocr": "Govcrnativa", "print": "Governativa"}, {"source_line": 341, "ocr": "fame conoscere il preggio", "print": "farne conoscere il pregio"}]},
)
add_statement(
    "st-chp10-p328-n06-venturi-locator", NOTES, None, "cand-2751", "citation_locator",
    342, 342, 328, 61,
    "Haskell cites F. Venturi, 1957, page 45, for Biffi's diary response to Rousseau's death.",
    "6 F. Venturi, 1957, p. 45.",
    "The cited publication and page were not independently consulted.",
    ["cand-2751", "cand-0373", "cand-2289", "cand-9833"], speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 6, "cited_source_independently_consulted": False},
)
add_statement(
    "st-chp10-p328-n07-gazzetta-citation", NOTES, "cand-1222", "cand-8729", "cites_periodical_for_gozzi_1760_statement",
    342, 342, 328, 61,
    "Haskell cites Gazzetta Veneta, 26 July 1760, for Gozzi's admission about criticism of his writing on buildings, altars and pictures.",
    "7 Cazzetta Veneta, 26 Luglio 1760.",
    "The issue/article was not independently consulted. The scan reads Gazzetta; S0 OCR is preserved.",
    ["cand-1222", "cand-8729"], speaker="Haskell's note", layer="periodical citation",
    extra={"footnote_marker": 7, "cited_source_independently_consulted": False, "ocr_corrections": [{"source_line": 342, "ocr": "Cazzetta Veneta", "print": "Gazzetta Veneta"}]},
)

if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("statement id already exists")

statement_rows = statements + new_statements
for row in new_statements:
    qualifiers = row.get("qualifiers", {})
    if any(cid not in (candidate_ids | {item["candidate_id"] for item in new_candidates}) for cid in qualifiers.get("mentioned_candidate_ids", [])):
        raise SystemExit(f"missing mentioned candidate in {row['statement_id']}")
    for field in ("subject_candidate_id", "object_candidate_id"):
        cid = row.get(field)
        if cid and cid not in (candidate_ids | {item["candidate_id"] for item in new_candidates}):
            raise SystemExit(f"missing {field} in {row['statement_id']}")
    for sid in qualifiers.get("footnote_statement_ids", []):
        if sid not in statement_ids and sid not in {new["statement_id"] for new in new_statements}:
            raise SystemExit(f"dangling footnote statement reference in {row['statement_id']}: {sid}")

# Close the p.327 main-text sentence and hand off the still-open p.328 final sentence to p.329.
for row in statements:
    if row["statement_id"] == "st-chp10-p327-less-offensive-poem-open":
        quals = row.setdefault("qualifiers", {})
        quals["continuation_status"] = "closed"
        quals["continuation_closed_by_segment_id"] = BODY
        quals["continuation_to_statement_id"] = "st-chp10-p328-filosofo-poem-identified"
previous_g = next((row for row in statements if row["statement_id"] == "st-chp10-p327-less-offensive-poem-open"), None)
if not previous_g or previous_g.get("qualifiers", {}).get("continuation_status") != "closed":
    raise SystemExit("failed to close p.327 continuation")

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
coverage_rows[coverage_rows.index(coverage[PREVIOUS])].update({
    "migration_status": "complete",
    "source_line_ranges": "L224-239",
    "note": "p.327 main-text continuation closed at p.328; p.327 notes linked.",
})
coverage_rows[coverage_rows.index(coverage[BODY])].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L241-246",
    "note": "p.327 poem sentence closed; p.328 final sentence continues at p.329 L249; p.328 footnotes 1-7 linked.",
})
coverage_rows[coverage_rows.index(coverage[NOTES])].update({
    "migration_status": "partial",
    "source_line_ranges": "L325-342",
    "note": "p.324-328 footnotes linked; continue with p.329 notes L343 onward.",
})
candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
statement_rows.sort(key=lambda row: row["statement_id"])
coverage_rows.sort(key=lambda row: row["segment_id"])

print(f"p.328 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print(f"updated candidate: cand-9829 -> {candidate_by_id['cand-9829']['canonical_name']}")
print("coverage: p.327 complete; p.328 partial; notes L325-342 partial")
print("continuation: p.327 poem sentence closed; p.328 Gozzi sentence remains open to p.329")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
for path in targets:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in targets:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied; four recovery copies saved")
