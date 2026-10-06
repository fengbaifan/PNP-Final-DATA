"""Controlled S2 migration for printed pp.326-327 and consolidated notes L333-337."""
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
PREVIOUS = "chp-10:10_CHP-10_sec_ii:l203-208"
BODY326 = "chp-10:10_CHP-10_sec_ii:l210-222"
BODY327 = "chp-10:10_CHP-10_sec_ii:l224-239"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BODY326_SHA = "a1fa6e3f087678b633dc4f2a33ff371c3852bd3923ee85b85ee787a4c259484b"
BODY327_SHA = "0932b9d6e7b24dc84a8fad20a510cdf979f7af80a8055204c687917e86f684e4"
NOTES_SLICE_SHA = "2e992c7e68f34364e7ad43c10e74a12bbbeb9a7f9d2e30f884b4fa83cfb19a2e"
BACKUP_SUFFIX = ".bak-s2-chp10-p326-327-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed pp.326-327 rows after making recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != MARKDOWN_SHA:
    raise SystemExit("canonical source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
line_map = {
    BODY326: {n: source_lines[n - 1] for n in range(210, 223)},
    BODY327: {n: source_lines[n - 1] for n in range(224, 240)},
    NOTES: {n: source_lines[n - 1] for n in range(273, 350)},
}
segment_text = {sid: "\n".join(lines.values()) for sid, lines in line_map.items()}
checks = {
    BODY326: BODY326_SHA,
    BODY327: BODY327_SHA,
}
for sid, expected in checks.items():
    if hashlib.sha256(segment_text[sid].encode("utf-8")).hexdigest() != expected:
        raise SystemExit(f"registered source segment changed: {sid}")
notes_review_slice = "\n".join(source_lines[332:337])
if hashlib.sha256(notes_review_slice.encode("utf-8")).hexdigest() != NOTES_SLICE_SHA:
    raise SystemExit("consolidated note slice L333-337 changed")
if line_map[BODY326][210] != "[Page 326]" or line_map[BODY327][224] != "[Page 327]":
    raise SystemExit("printed-page boundaries changed")
if not line_map[BODY326][217].endswith("much more obviously"):
    raise SystemExit("p.326 body no longer ends at the registered continuation")
if not line_map[BODY327][239].endswith("being large."):
    raise SystemExit("p.326 note continuation no longer closes at the registered endpoint")

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
if state != (9776, 9789, 20725, 9208):
    raise SystemExit(f"unexpected table pre-state: {state}")
for sid in (PREVIOUS, BODY326, BODY327, NOTES):
    if sid not in coverage:
        raise SystemExit(f"required coverage row missing: {sid}")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.325 is not reviewed/partial")
for sid in (BODY326, BODY327):
    if (coverage[sid]["disposition"], coverage[sid]["migration_status"]) != ("queued", "pending"):
        raise SystemExit(f"expected queued/pending coverage for {sid}")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"], coverage[NOTES]["source_line_ranges"]) != ("reviewed", "partial", "L325-332"):
    raise SystemExit("consolidated notes are not in the expected p.324-325 partial state")
for sid in (BODY326, BODY327):
    if any(row["segment_id"] == sid for row in mentions) or any(row["segment_id"] == sid for row in statements):
        raise SystemExit(f"body rows already exist for {sid}")
if any(row["segment_id"] == NOTES and 333 <= int(row.get("qualifiers", {}).get("source_line_start", 0)) <= 337 for row in statements):
    raise SystemExit("note statements L333-337 already exist")

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


# Unnamed or separately identifiable referents and works; no external alignment is asserted.
add_candidate("cand-9790", "Unidentified government surveillance actor(s) in the Giorgio Pisani episode", "term", "Haskell shifts from a singular government spy to plural spies at the palace celebration; neither individual identities nor continuity between them is established.", BODY326, 211)
add_candidate("cand-9791", "Bienpensants opposed to the Pisani pamphlet imagery", "term", "Haskell uses the French term for those hostile to the allegorical prints; the passage does not identify the individuals or define a formal group.", BODY326, 213)
add_candidate("cand-9792", "Giorgio Pisani's 1780 election and public entry as Procuratore di San Marco", "event", "Haskell dates Pisani's election to 1780 and describes the appointment, congratulations, tribute, pamphlets, and procession; keep the evening palace celebration as a related but distinct event.", BODY326, 211)
add_candidate("cand-9793", "Unidentified tribute written by Gasparo Gozzi for Giorgio Pisani", "archive", "Haskell says Gozzi wrote a tribute after Pisani's appointment but supplies no title or full text here.", BODY326, 213)
add_candidate("cand-9794", "Componimenti poetici in occasione del solenne ingresso di Sua Eccellenza Missier Zorzi Pisani (Trevigi, 1780)", "archive", "Title and imprint are split between p.326 n.1 and the page-bottom continuation; the cited pamphlet was not independently consulted.", NOTES, 333)
add_candidate("cand-9795", "Poesie per il solenne ingresso di Sua Eccellenza Mss.r Zorzi Pisani (Venezia, 1780)", "archive", "Title and imprint are split across OCR lines in p.326 n.1; the cited pamphlet was not independently consulted.", BODY326, 218)
add_candidate("cand-9796", "Il Patriotismo. Poemetto per l’ingresso di Sua Eccellenza M.r Giorgio Pisani (Venezia, 1780)", "archive", "Pamphlet title and imprint cited in p.326 n.1; the cited pamphlet was not independently consulted.", BODY326, 219)
add_candidate("cand-9797", "Antonio Paluello", "person", "Named as printer of the Trevigi edition cited in p.326 n.1; identity is not externally aligned.", BODY326, 218)
add_candidate("cand-9798", "Carlo Palese", "person", "Named as printer of the Venetian edition cited in p.326 n.1; identity is not externally aligned.", BODY326, 219)
add_candidate("cand-9799", "Stamperia Albrizziana", "institution", "Printing establishment named in the p.326 n.1 imprint; distinguish the press from the indexed Accademia Albrizziana pending alignment.", BODY326, 220)
add_candidate("cand-9800", "Ambri", "person", "Surname-only author cited for chapter 6 on Montesquieu's reputation in Venice; full identity is not supplied here.", BODY326, 222)
add_candidate("cand-9801", "Ambri, chapter 6, cited on Montesquieu's reputation in Venice", "archive", "Citation locator in p.326 n.1; the cited chapter was not independently consulted.", BODY326, 222)
add_candidate("cand-9802", "Giorgio Pisani's illustrated visiting card", "work", "A card designed by Pisani and considered provocative at the time; Haskell says it is difficult to interpret. Its original location and later history are not supplied.", BODY326, 214)
add_candidate("cand-9803", "Four allegorical paintings commissioned by Lazzaro Riviera from Felice Boscarati", "work", "Haskell describes four paintings intended to illustrate an ideal philosophical and educational system for young men; no titles or surviving-object identities are given.", BODY326, 216)
add_candidate("cand-9804", "Ideal philosophical and educational system for young men represented in Riviera's allegories", "term", "An unnamed program that Haskell says the four paintings were designed to illustrate; do not identify a school or formal doctrine.", BODY326, 216)
add_candidate("cand-9805", "Large engraved copies of Riviera's four allegorical paintings", "work", "Haskell says the paintings were copied in large engravings with garbled Latin text beneath; no engraver or surviving impressions are identified here.", BODY326, 216)
add_candidate("cand-9806", "La Educazione Virile, explanatory pamphlets in French and Italian (Verona, 1773)", "archive", "P.327 n.3 identifies Riviera's two explanatory pamphlet versions and publication place/date; neither version was independently consulted.", BODY327, 237)
add_candidate("cand-9807", "Political allegorical pictures displayed along Giorgio Pisani's procession route", "work", "Haskell describes images outside the Procuratie Nuove showing political disorder and the Procurator rebuilding public buildings; exact titles, authorship, and object identities are not supplied.", BODY326, 217)
add_candidate("cand-9808", "Procuratie Nuove", "place", "Building named as the display location for political pictures; no more precise space is identified.", BODY327, 225)
add_candidate("cand-9809", "Giuliano Giampiccoli's view-print of Campo di S. Maria Formosa", "work", "Haskell says Pisani commissioned a view of the campo where his palace was situated; the print was hurriedly withdrawn and is not otherwise identified.", BODY327, 227)
add_candidate("cand-9810", "Campo di S. Maria Formosa, Venice", "place", "Square named as the subject of Giampiccoli's print and the location of an unidentified Pisani palace.", BODY327, 227)
add_candidate("cand-9811", "Unidentified Giorgio Pisani palace at Campo di S. Maria Formosa", "place", "The passage locates Pisani's palace in this campo but does not name or identify the building.", BODY327, 227)
add_candidate("cand-9812", "Giorgio Pisani's 1780 palace-entry celebration", "event", "Haskell describes a large celebration at the palace on the evening of the procession; the event is kept distinct from Pisani's election and public entry.", BODY327, 229)
add_candidate("cand-9813", "Unidentified painting of Giorgio Pisani with political emblems at the palace celebration", "work", "A picture described in an anonymous spy report as showing Freedom, Power, Sovereignty, governmental collapse, and a new system; preserve this as a reported interpretation.", BODY327, 229)
add_candidate("cand-9814", "Printed menus for Giorgio Pisani's palace celebration", "archive", "Haskell says two French lines were printed on the menus; no surviving menu or printer is identified.", BODY327, 230)
add_candidate("cand-9815", "Saying circulated during Giorgio Pisani's 1780 entry", "term", "Italian saying quoted on p.327; preserve the source wording and do not treat the prophecy as a documented prediction by an identified speaker.", BODY327, 233)
add_candidate("cand-9816", "Arrest of Giorgio Pisani in 1780", "event", "Haskell says the Inquisitors moved into action four days after the procession and arrested Pisani; exact arrest date is not stated.", BODY327, 234)
add_candidate("cand-9817", "Molmenti, author cited for the visiting-card reproduction", "person", "Surname-only author reference in p.326 n.2; full identity is not inferred.", NOTES, 334)
add_candidate("cand-9818", "Molmenti, 1908, vol. III, pp. 45-46", "archive", "Citation for a reproduction and comments on Pisani's visiting card; cited pages were not independently consulted.", NOTES, 334)
add_candidate("cand-9819", "Zannandreis, p. 416, cited on Pisani's arrest", "archive", "Page locator supplied in p.327 n.2; title and edition are not supplied here, and the cited page was not independently consulted.", NOTES, 337)
add_candidate("cand-9820", "Moschini, author cited in 1924, p. 145", "person", "Surname-only author reference; do not merge at S2 with the indexed Abate G. A. Moschini candidate.", NOTES, 337)
add_candidate("cand-9821", "Moschini, 1924, p. 145", "archive", "Citation for the report of Cristoforo dall'Acqua's prints at Pisani's entry; cited page was not independently consulted.", NOTES, 337)
add_candidate("cand-9822", "Francesco Donado", "person", "Addressee named in the p.327 n.1 citation to a set of family letters; identity is not externally aligned.", NOTES, 336)
add_candidate("cand-9823", "Gio. Mattia Balbi", "person", "Named as the writer of the letters cited in p.327 n.1; retain the source's abbreviated form and do not expand the name.", NOTES, 336)
add_candidate("cand-9824", "Memorie Storiche della Correzione 1780, raccolte in XXIV Lettere Familiari (Biblioteca Correr, MSS. Cicogna 2229)", "archive", "P.327 n.1 cites a 1780 set of twenty-four family letters by Gio. Mattia Balbi to Francesco Donado; the manuscript was not independently consulted.", NOTES, 336)
add_candidate("cand-9825", "Raccolta Gherro, vol. VIII (Biblioteca Correr)", "archive", "Collection locator for prints by Cristoforo dall'Acqua cited in p.327 n.3; the collection was not independently consulted.", BODY327, 237)
add_candidate("cand-9826", "Emblematic prints by Cristoforo dall'Acqua cited in Raccolta Gherro, vol. VIII", "work", "Haskell says the prints are dated before 1780; he distinguishes their dates from the uncertain claim that pictures or prints were exhibited at Pisani's entry.", BODY327, 237)
add_candidate("cand-9827", "Settecento Paintings, Arcade Gallery, February-March 1957", "archive", "Sale/exhibition reference cited for a version of one picture; Haskell says it is unlikely to have been an original. The catalogue or sale record was not independently consulted.", BODY327, 238)
add_candidate("cand-9828", "French Revolution", "event", "Used by Haskell as a chronological endpoint for his statement that politics and art separated; no more specific event is discussed here.", BODY327, 236)
add_candidate("cand-9829", "Unidentified less offensive poem published to celebrate Giorgio Pisani's entry", "archive", "Haskell begins a sentence about a poem among those published to celebrate Pisani; the title is supplied in the following p.328 segment and remains to be linked there.", BODY327, 237)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []


def add_mention(segment, line_no, surface, cid, note="", occurrence=0):
    if segment not in line_map or cid not in all_candidate_ids:
        raise SystemExit(f"invalid mention segment/candidate: {segment} {surface!r} {cid}")
    line = line_map[segment][line_no]
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
    first_line = min(line_map[segment])
    start = sum(len(line_map[segment][n]) + 1 for n in range(first_line, line_no)) + starts[occurrence]
    if segment_text[segment][start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch at L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p326-327-{len(new_mentions) + 1:04d}",
        "segment_id": segment,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


# p.326 prose and the page-bottom continuation of footnote 1.
add_mention(BODY326, 211, "Inquisitori di Stato", "cand-9739")
add_mention(BODY326, 211, "government spy", "cand-9790", "Unnamed; do not infer identity or equivalence to the later plural spies.")
add_mention(BODY326, 212, "Procuratore di San Marco", "cand-8449")
add_mention(BODY326, 213, "Gozzi", "cand-1223")
add_mention(BODY326, 213, "bienpensants", "cand-9791")
add_mention(BODY326, 213, "Montesquieu", "cand-1696")
add_mention(BODY326, 213, "Il Patriotismo", "cand-9796")
add_mention(BODY326, 214, "Giorgio Pisani", "cand-1942")
add_mention(BODY326, 214, "visiting-card", "cand-9802")
add_mention(BODY326, 215, "the card", "cand-9802")
add_mention(BODY326, 216, "Procurator", "cand-8449")
add_mention(BODY326, 216, "Pisani", "cand-1942")
add_mention(BODY326, 216, "Lazzaro Riviera", "cand-2204")
add_mention(BODY326, 216, "Felice Boscarati", "cand-0411")
add_mention(BODY326, 216, "Venice", "cand-2719")
add_mention(BODY326, 216, "four allegorical pictures", "cand-9803")
add_mention(BODY326, 216, "ideal philosophical and educational system", "cand-9804")
add_mention(BODY326, 216, "large engravings", "cand-9805")
add_mention(BODY326, 217, "the artist himself", "cand-0411", "Local antecedent is Felice Boscarati at L216; the wording gives an alternative attribution, not a settled action.")
add_mention(BODY326, 217, "Pisani’s advisers", "cand-1942", "Advisers are unnamed; the sentence gives them as one possible agent, not a confirmed attribution.")
add_mention(BODY326, 217, "The Inquisitors", "cand-9739")
add_mention(BODY326, 218, "Trevigi", "cand-9209", "Retain source spelling; the index candidate is Treviso and identity awaits S3.")
add_mention(BODY326, 218, "Antonio Paluello", "cand-9797")
add_mention(BODY326, 218, "Poesie peril solenne ingresso di Sua Eccellenza Mss.r", "cand-9795", "Title continues on L219; OCR reads 'peril' for printed 'per il' and joins 'PisaniIn'.")
add_mention(BODY326, 219, "Zorzi Pisani", "cand-1942")
add_mention(BODY326, 219, "Carlo Palese", "cand-9798")
add_mention(BODY326, 219, "Il Patriotismo", "cand-9796")
add_mention(BODY326, 220, "Giorgio Pisani", "cand-1942")
add_mention(BODY326, 220, "Stamperia Albrizziana", "cand-9799")
add_mention(BODY326, 221, "Biblioteca Marciana", "cand-9448")
add_mention(BODY326, 221, "Venice", "cand-2719")
add_mention(BODY326, 222, "Montesquieu", "cand-1696")
add_mention(BODY326, 222, "Ambri", "cand-9800")
add_mention(BODY326, 222, "chapter 6", "cand-9801")

# p.327 body, the p.326 footnote 3 continuation, and p.327 footnotes.
add_mention(BODY327, 225, "Procuratie Nuove", "cand-9808")
add_mention(BODY327, 226, "Procurator", "cand-8449")
add_mention(BODY327, 227, "Pisani", "cand-1942")
add_mention(BODY327, 227, "Giampiccoli", "cand-1163")
add_mention(BODY327, 227, "Campo di S. Maria Formosa", "cand-9810")
add_mention(BODY327, 227, "his palace", "cand-9811")
add_mention(BODY327, 227, "the print", "cand-9809")
add_mention(BODY327, 227, "Giorgio pisani", "cand-1942", "Source capitalization is retained in the Latin inscription.")
add_mention(BODY327, 229, "the procession", "cand-9792")
add_mention(BODY327, 229, "the palace", "cand-9812")
add_mention(BODY327, 229, "Spies", "cand-9790", "Plural agents are unnamed; no identity is inferred.")
add_mention(BODY327, 229, "a picture", "cand-9813")
add_mention(BODY327, 230, "the menus", "cand-9814")
add_mention(BODY327, 233, "Oggi Bordello, dimani in Castello; oggi 1’Ingresso, dimani ii Processo. Dio ti guardi.", "cand-9815", "OCR contains numeral-like 1/ii; page image reads l'Ingresso/il Processo. Preserve OCR surface and record the print reading in S2.")
add_mention(BODY327, 234, "the Inquisitors", "cand-9739")
add_mention(BODY327, 235, "Pisani", "cand-1942")
add_mention(BODY327, 235, "Felice Boscarati", "cand-0411")
add_mention(BODY327, 235, "Cristoforo dall’Acqua", "cand-0010")
add_mention(BODY327, 236, "French Revolution", "cand-9828")
add_mention(BODY327, 236, "Venetian Republic", "cand-3678")
add_mention(BODY327, 237, "Pisani’s", "cand-1942")
add_mention(BODY327, 237, "Cristoforo dall’Acqua", "cand-0010")
add_mention(BODY327, 237, "Biblioteca Correr", "cand-8262")
add_mention(BODY327, 237, "Raccolta Gherro, Vol. VIII", "cand-9825")
add_mention(BODY327, 237, "Riviera", "cand-2204")
add_mention(BODY327, 237, "La Educazione Virile", "cand-9806")
add_mention(BODY327, 237, "Verona", "cand-8681")
add_mention(BODY327, 237, "Zannandreis", "cand-8359")
add_mention(BODY327, 237, "Moschini", "cand-9820")
add_mention(BODY327, 237, "Pisani’s entry", "cand-9792")
add_mention(BODY327, 237, "less offensive poems", "cand-9829")
add_mention(BODY327, 237, "Boscarati", "cand-0411")
add_mention(BODY327, 238, "Settecento Paintings", "cand-9827")
add_mention(BODY327, 239, "Arcade Gallery", "cand-9827", "Venue is retained in the cited sale/exhibition record; it is not treated as an identified building.")

# Consolidated footnote rows L333-337.
add_mention(NOTES, 333, "Missier Zorzi Pisani", "cand-1942")
add_mention(NOTES, 334, "Molmenti", "cand-9817")
add_mention(NOTES, 335, "Zannandreis", "cand-8359")
add_mention(NOTES, 336, "Grimaldo", "cand-9783")
add_mention(NOTES, 336, "Memorie Storiche della Correzione 1780", "cand-9824")
add_mention(NOTES, 336, "Francesco Donado", "cand-9822")
add_mention(NOTES, 336, "Gio. Mattia Balbi", "cand-9823")
add_mention(NOTES, 336, "Biblioteca Correr", "cand-8262")
add_mention(NOTES, 336, "MSS. Cicogna 2229", "cand-9824")
add_mention(NOTES, 337, "Zannandreis", "cand-8359")
add_mention(NOTES, 337, "Moschini", "cand-9820")

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


F1 = [
    {"marker": 1, "segment_id": NOTES, "source_line": 333},
    {"marker": 1, "segment_id": BODY326, "source_line": 218},
]
F2 = [{"marker": 2, "segment_id": NOTES, "source_line": 334}]
F3 = [
    {"marker": 3, "segment_id": NOTES, "source_line": 335},
    {"marker": 3, "segment_id": BODY327, "source_line": 237},
]
F327_1 = [{"marker": 1, "segment_id": NOTES, "source_line": 336}]
F327_2 = [{"marker": 2, "segment_id": NOTES, "source_line": 337}]
F327_3 = [{"marker": 3, "segment_id": NOTES, "source_line": 337}]

add_statement("st-chp10-p326-support-and-state-surveillance", BODY326, "cand-1942", "cand-9790", "attracted_support_and_surveillance",
              211, 211, 326, 59,
              "Haskell says Pisani's activity brought him some support as well as the attention of a government spy.",
              "And this won him some support—as well as the attentions of a government spy.",
              "'This' refers to Pisani's preceding political stance; the spy is unnamed and is not identified with the plural spies at the later celebration.",
              ["cand-1942", "cand-9790", "cand-9789"])
add_statement("st-chp10-p326-inquisitori-opposition", BODY326, "cand-1942", "cand-9739", "opposed_inquisitori_di_stato",
              211, 211, 326, 59,
              "The p.325 comparison with Angelo Querini closes by describing the Inquisitori di Stato as increasingly active; this is the institutional target of Pisani's opposition in the preceding clause.",
              "active Inquisitori di Stato.",
              "The beginning of the sentence is on p.325 L208. Preserve the comparative adverb 'increasingly'; do not infer a formal prosecution or a specific policy from this clause.",
              ["cand-1942", "cand-2075", "cand-9739"],
              extra={"continuation_from_segment_id": PREVIOUS, "continuation_from_statement_id": "st-chp10-p325-pisani-querini-opposition-sentence-continues", "continuation_prefix": "the increasingly"})
add_statement("st-chp10-p326-election-1780", BODY326, "cand-1942", "cand-8449", "elected_to_office",
              211, 212, 326, 59,
              "After complicated intrigues, Pisani was elected Procuratore di San Marco in 1780.",
              "In 1780, after complicated intrigues, he was suddenly elected\nProcuratore di San Marco.",
              "The election and date are Haskell's account; the process is not reconstructed beyond his wording.",
              ["cand-1942", "cand-8449", "cand-9792"], extra={"event_candidate_id": "cand-9792", "date_as_stated": "1780"})
add_statement("st-chp10-p326-appointment-enthusiasm", BODY326, "cand-1942", "cand-9792", "appointment_greeted_with_enthusiasm",
              212, 213, 326, 59,
              "Haskell says the appointment was greeted with great enthusiasm, with congratulations and a tribute by Gasparo Gozzi.",
              "The appointment was greeted with great enthusiasm.\nCongratulations poured in, Gozzi wrote a tribute",
              "This describes the reception of the appointment; it does not establish a single organized ceremony or identify the congratulators.",
              ["cand-1942", "cand-9792", "cand-1223", "cand-9793"])
add_statement("st-chp10-p326-pamphlet-prints-hostility", BODY326, "cand-9792", "cand-9791", "entry_pamphlet_imagery_angered_bienpensants",
              213, 213, 326, 59,
              "Haskell says pamphlets printed in Pisani's honour contained allegorical prints that aroused hostility among the bienpensants.",
              "in the pamphlets that were printed in his honour were included strange allegorical prints that aroused the hostility of the bienpensants",
              "The pamphlets and prints are described collectively here; the footnote names three poem pamphlets but does not establish that each contained every image described.",
              ["cand-9792", "cand-9791", "cand-9794", "cand-9795", "cand-9796"],
              extra={"footnote_marker": 1, "footnote_segment": NOTES, "footnote_refs": F1, "footnote_statement_ids": ["st-chp10-p326-n01-pamphlet-titles", "st-chp10-p326-n01-marciana-set", "st-chp10-p326-n01-montesquieu-reference"], "footnote_body_link_status": "linked"})
add_statement("st-chp10-p326-montesquieu-frontispiece", BODY326, "cand-9794", "cand-1696", "frontispiece_depicts_montesquieu_works",
              213, 213, 326, 59,
              "One frontispiece depicts a reclining nude youth while a putto carries works of Montesquieu; Haskell says those works were controversial in Venetian society.",
              "in one frontispiece a nude youth reclined while a putto carried aloft the works of Montesquieu which were highly controversial in Venetian society",
              "The image and controversy are Haskell's descriptions; the specific works of Montesquieu are not named.",
              ["cand-9794", "cand-1696", "cand-2719"])
add_statement("st-chp10-p326-justice-temple-frontispiece", BODY326, "cand-9795", "cand-1942", "frontispiece_implies_pisani_alone_would_ascend_justice_temple",
              213, 213, 326, 59,
              "A second frontispiece shows steps leading to a temple presumed to represent Justice and implies that Pisani alone was prepared to climb them.",
              "on another, steps were shown leading up to a Temple, presumably of Justice, with the implication that Pisani alone was prepared to climb them",
              "'Presumably' and 'with the implication' mark interpretation, not a certain identification of the depicted temple or the artist's intent.",
              ["cand-9795", "cand-1942"])
add_statement("st-chp10-p326-il-patriotismo-title", BODY326, "cand-9796", "cand-9792", "poem_set_named_il_patriotismo",
              213, 213, 326, 59,
              "Haskell says a third set of poems was significantly called Il Patriotismo.",
              "a third set of poems was called, significantly, Il Patriotismo.",
              "The cited title is recorded in the p.326 note; no independent copy or edition has been examined.",
              ["cand-9796", "cand-9792"], extra={"footnote_marker": 1, "footnote_segment": NOTES, "footnote_refs": F1, "footnote_statement_ids": ["st-chp10-p326-n01-pamphlet-titles"], "footnote_body_link_status": "linked"})
add_statement("st-chp10-p326-visiting-card-reception", BODY326, "cand-1942", "cand-9802", "designed_provocative_visiting_card",
              214, 214, 326, 59,
              "Haskell says Pisani designed a visiting card that was difficult to interpret but was considered provocative at the time.",
              "Giorgio Pisani made matters worse by designing a strange visiting-card, which has proved difficult to interpret, but which was considered provocative at the time.",
              "The difficulty of interpretation and contemporary reception are both attributed to Haskell; no settled iconographic reading is asserted.",
              ["cand-1942", "cand-9802"], extra={"footnote_marker": 2, "footnote_segment": NOTES, "footnote_refs": F2, "footnote_statement_ids": ["st-chp10-p326-n02-molmenti-reference"], "footnote_body_link_status": "linked"})
add_statement("st-chp10-p326-visiting-card-iconography", BODY326, "cand-9802", "cand-1942", "visiting_card_depicts_symbols_and_inscription",
              214, 215, 326, 59,
              "The card shows a young man with a sail bearing Pisani's name and title, a swan and star, a cat with a rod and liberty cap, and a gondola prow.",
              "It shows a young man, leaning on a ramp to which is attached a sail with the words IL procurator GIORGIO pisani. He holds a swan and above his head there shines a star.\nOn the left of the card is a cat",
              "Record the depicted motifs without treating them as identified portraits, a documented political program, or a stable interpretation.",
              ["cand-9802", "cand-1942"])
add_statement("st-chp10-p326-procurator-procession-picture-custom", BODY326, "cand-8449", "cand-9807", "palaces_displayed_pictures_for_procurator_procession",
              216, 216, 326, 59,
              "Haskell describes a custom of hanging pictures on palaces along a new Procurator's procession route, often specially commissioned for the occasion.",
              "It was the custom when a new Procurator was elected to have the palaces along which the procession would have to pass hung with pictures which were very often specially commissioned for the occasion.",
              "Haskell presents this as a custom; he does not identify all palaces or claim every display was a special commission.",
              ["cand-8449", "cand-9792", "cand-9807"])
add_statement("st-chp10-p326-authorities-misunderstanding", BODY326, "cand-1942", "cand-9789", "offended_authorities_probably_misunderstood",
              216, 216, 326, 59,
              "Haskell says Pisani and his friends offended the authorities, though he thinks the trouble seems to have arisen from a misunderstanding amid prevailing tension.",
              "Here too Pisani and his friends offended the authorities, though the trouble seems to have been caused by a misunderstanding natural enough in the prevailing tension.",
              "'Seems' marks Haskell's explanation as qualified. It is not a finding that the pictures had no political content.",
              ["cand-1942", "cand-9789", "cand-9807"])
add_statement("st-chp10-p326-riviera-commission", BODY326, "cand-2204", "cand-9803", "commissioned_four_allegorical_pictures",
              216, 216, 326, 59,
              "A few years earlier, Lazzaro Riviera commissioned Felice Boscarati to paint four allegorical pictures designed to illustrate an ideal philosophical and educational system for young men.",
              "Lazzaro Riviera, had commissioned a local artist, Felice Boscarati, to paint four allegorical pictures of the most incomprehensible subtlety designed to illustrate a sort of ideal philosophical and educational system for young men.",
              "The system is unnamed, the pictures are not individually titled, and Haskell's evaluative description is not converted into an objective property.",
              ["cand-2204", "cand-0411", "cand-9803", "cand-9804"])
add_statement("st-chp10-p326-riviera-engravings-and-pamphlet", BODY326, "cand-2204", "cand-9805", "paintings_copied_into_engravings_and_explained_in_pamphlet",
              216, 216, 326, 59,
              "Haskell says the pictures were copied in large engravings with garbled Latin text and accompanied by an explanatory pamphlet.",
              "he had them copied in large engravings with a text in garbled Latin underneath and issued an equally incomprehensible pamphlet to explain them.",
              "The antecedent 'he' is locally Riviera; p.327 n.3 names the pamphlet La Educazione Virile and says French and Italian versions appeared in 1773, without independent consultation.",
              ["cand-2204", "cand-9803", "cand-9805", "cand-9806"])
add_statement("st-chp10-p326-boscarati-official-painter", BODY326, "cand-0411", "cand-1942", "appointed_as_pisani_official_painter",
              216, 216, 326, 59,
              "After Boscarati moved to Venice, Pisani took him up as his official painter.",
              "Boscarati moved to Venice and was taken up by Pisani as his official painter.",
              "Haskell's wording does not establish a formal salaried appointment or an institution called a court.",
              ["cand-0411", "cand-1942", "cand-2719"])
add_statement("st-chp10-p326-picture-display-agency-alternatives", BODY326, "cand-9807", "cand-1942", "displayed_with_uncertain_agency_and_intent",
              217, 217, 326, 59,
              "The pictures were displayed along the route; Haskell gives either Boscarati's opportunism or Pisani's advisers' taste for abstruse symbolism as possible causes.",
              "displayed along the processional route—either by the artist himself in order to take advantage of his situation or by Pisani’s advisers who rather liked abstruse symbolism for its own sake.",
              "These are alternative explanations, not a resolved attribution. The advisers are unnamed; the source does not establish that they commissioned the pictures.",
              ["cand-9807", "cand-0411", "cand-1942"])
add_statement("st-chp10-p326-inquisitors-interpret-allegories", BODY326, "cand-9739", "cand-9807", "interpreted_allegories_as_subversive_propaganda",
              217, 217, 326, 59,
              "Haskell says the Inquisitors decided the allegories were intended as subversive propaganda and says they had some reason to be suspicious.",
              "they decided that the allegories were intended as subversive propaganda.3 They had some reason to be suspicious",
              "This is Haskell's account of the Inquisitors' interpretation; it does not establish the artist's or Pisani's intent. Footnote 3 qualifies the attribution and dating of related images.",
              ["cand-9739", "cand-9807"], extra={"footnote_marker": 3, "footnote_segment": NOTES, "footnote_refs": F3, "footnote_statement_ids": ["st-chp10-p326-n03-haskell-explanation", "st-chp10-p326-n03-dating-and-exhibition"], "footnote_body_link_status": "linked"})
add_statement("st-chp10-p327-political-pictures-procuratie", BODY327, "cand-9807", "cand-9808", "political_pictures_showed_disorder_and_rebuilding",
              225, 226, 327, 60,
              "Haskell says more obviously political pictures outside the Procuratie Nuove showed a sleeping lion, unbalanced scales, liberty cap, collapsing public buildings, and the Procurator rebuilding them while encouraging his sons to copy him.",
              line_map[BODY327][225] + "\n" + line_map[BODY327][226],
              "The sentence begins on p.326 L217. The images' meaning is Haskell's description; no individual picture, maker, or sons are identified.",
              ["cand-9807", "cand-9808", "cand-8449"],
              extra={"continuation_from_segment_id": BODY326, "continuation_prefix": "for other pictures, much more obviously", "footnote_marker": 1, "footnote_segment": NOTES, "footnote_refs": F327_1, "footnote_statement_ids": ["st-chp10-p327-n01-grimaldo-balbi-citation"], "footnote_body_link_status": "linked"})
add_statement("st-chp10-p327-giampiccoli-print-commission", BODY327, "cand-1942", "cand-9809", "commissioned_view_print_from_giampiccoli",
              227, 227, 327, 60,
              "Pisani commissioned Giampiccoli to make a view of Campo di S. Maria Formosa, where his palace was situated.",
              "Pisani commissioned from Giampiccoli, one of the most prolific engravers of the day, a view of the Campo di S. Maria Formosa in which his palace was situated.",
              "The specific palace is not identified. The print is a provisional local work candidate, not matched to a surviving impression.",
              ["cand-1942", "cand-1163", "cand-9809", "cand-9810", "cand-9811"])
add_statement("st-chp10-p327-print-inscription-and-withdrawal", BODY327, "cand-9809", "cand-1942", "inscription_praised_pisani_and_print_withdrawn",
              227, 228, 327, 60,
              "The print's Latin inscription praised Pisani's service, scientific culture, and support for public liberty; Haskell says the combination of self-advertisement and freedom references was considered dangerous and the print was hurriedly withdrawn.",
              "At the base of the print were the words eccel.mo Giorgio pisani divi marco merito procuratori ac\nUNO EX QUINQUEVIRIS CORRECTORIBUS. UTILIUM SCIENTIARUM CULTU, ET PUBLICAE libertatis studio praeclaro MOECENATi humanissimo. The combination' of selfadvertisement and references to freedom was considered dangerous and the print was hurriedly withdrawn.",
              "OCR spacing/punctuation in the Latin and English is visibly imperfect. The print's inscription is not treated as an independently verified translation or as evidence that Pisani controlled the narrative.",
              ["cand-9809", "cand-1942"], extra={"ocr_corrections": [{"source_line": 228, "ocr": "The combination'", "print": "The combination"}, {"source_line": 228, "ocr": "selfadvertisement", "print": "self-advertisement"}]})
add_statement("st-chp10-p327-palace-celebration-surveillance", BODY327, "cand-9812", "cand-9790", "celebration_observed_by_unnamed_spies",
              229, 230, 327, 60,
              "Haskell says a large celebration took place at Pisani's palace on the evening of the procession and that spies moved among the guests, reporting a painting with emblems of freedom, power, sovereignty, governmental collapse, and a new system.",
              "But the real trouble came on the evening of the procession when a huge celebration was held in the palace. Spies moved among the guests and nosed in the main reception room ‘a picture showing Pisani with various emblems denoting Freedom, Power,\nSovereignty, and the collapse of the present form of government and the adoption of a completely new system’. The atmosphere was fraught with suspicion",
              "The painting's program is quoted from the spies' reported observation; Haskell does not independently identify its maker or assert that the reported political meaning was the painter's intention.",
              ["cand-9812", "cand-9792", "cand-9790", "cand-9813", "cand-1942", "cand-9789"])
add_statement("st-chp10-p327-menu-verse-and-circulating-saying", BODY327, "cand-9814", "cand-9815", "menu_verse_and_saying_reflected_suspicion",
              230, 233, 327, 60,
              "Haskell says French verses were printed on the celebration menus, guests must have felt uneasy, and an Italian saying about Pisani's entry and possible trial circulated.",
              "even the menus were carefully noted, for on them were printed two lines in French:\nLa science, le bon cœur, l’Amour patriotique\nSont-ils les fondements de la République.\nThe guests must have felt uneasy, and the saying went around: ‘Oggi Bordello, dimani in Castello; oggi 1’Ingresso, dimani ii Processo. Dio ti guardi.’",
              "The source gives the French lines and the Italian saying as reported speech; the OCR's numeral-like characters are corrected against the print in S2 only.",
              ["cand-9814", "cand-9815", "cand-2719"], extra={"ocr_corrections": [{"source_line": 233, "ocr": "1’Ingresso", "print": "l'Ingresso"}, {"source_line": 233, "ocr": "ii Processo", "print": "il Processo"}]})
add_statement("st-chp10-p327-inquisitors-act-four-days-later", BODY327, "cand-9739", "cand-9816", "inquisitors_acted_four_days_after_procession",
              234, 234, 327, 60,
              "Haskell says the prophecy was apt enough and the Inquisitors acted four days later.",
              "The prophecy was apt enough. Four days later the Inquisitors moved into action.",
              "The exact calendar date is not supplied; 'apt enough' is Haskell's retrospective assessment.",
              ["cand-9739", "cand-9816", "cand-9815"])
add_statement("st-chp10-p327-pisani-arrest-boscarati-trouble", BODY327, "cand-1942", "cand-9816", "pisani_arrested_and_boscarati_also_in_trouble",
              235, 235, 327, 60,
              "Haskell says Pisani was arrested and Boscarati also had trouble after the disgrace of his patron; he characterizes Boscarati as fond of satire.",
              "Pisani was arrested, and his painter Felice Boscarati, who was dangerously fond of satire, also had trouble after the disgrace of his patron.2",
              "The passage does not specify a charge, sentence, or the nature of Boscarati's trouble. 'Dangerously fond of satire' is Haskell's characterization.",
              ["cand-1942", "cand-0411", "cand-9816"], extra={"footnote_marker": 2, "footnote_segment": NOTES, "footnote_refs": F327_2, "footnote_statement_ids": ["st-chp10-p327-n02-zannandreis-citation"], "footnote_body_link_status": "linked"})
add_statement("st-chp10-p327-dallacqua-not-involved-report", BODY327, "cand-0010", "cand-1942", "later_writer_noted_dallacqua_not_involved_in_downfall",
              235, 236, 327, 60,
              "Haskell says a later writer considered it significant that Cristoforo dall'Acqua had not also been involved in Pisani's downfall.",
              "a later writer thought it worth recording as significant the fact that Cristoforo dall’Acqua, the engraver of the emblematic pictures, had not also been involved in\nPisani’s downfall.3",
              "The later writer is unnamed; non-involvement is reported as the writer's observation, not as proof that dall'Acqua was investigated or accused.",
              ["cand-0010", "cand-1942", "cand-9826"], extra={"footnote_marker": 3, "footnote_segment": NOTES, "footnote_refs": F327_3, "footnote_statement_ids": ["st-chp10-p327-n03-moschini-citation"], "footnote_body_link_status": "linked"})
add_statement("st-chp10-p327-politics-and-art-separation", BODY327, "cand-9789", "cand-3678", "politics_and_art_separated_until_revolution_and_republic_collapse",
              236, 236, 327, 60,
              "Haskell says politics and art separated thereafter until the French Revolution and the collapse of the Venetian Republic.",
              "Thereafter politics and art separated until the French Revolution and the collapse of the Venetian Republic.",
              "This is Haskell's broad periodizing claim, not a claim that all political art ended or that the two events were simultaneous.",
              ["cand-9789", "cand-9828", "cand-3678"])
add_statement("st-chp10-p327-less-offensive-poem-open", BODY327, "cand-9792", "cand-9829", "less_offensive_entry_poem_introduction_continues",
              237, 237, 327, 60,
              "Haskell begins identifying one of the less offensive poems published to celebrate Pisani; the sentence continues on p.328 with the poem's title.",
              line_map[BODY327][237].split(" were especially commissioned for Pisani’s entry.", 1)[0],
              "This is main text above the p.327 footnote rule, not part of p.326 footnote 3. The next segment is required to identify which poem is meant.",
              ["cand-9792", "cand-9829"],
              extra={"continuation_to_segment_id": "chp-10:10_CHP-10_sec_ii:l241-246", "continuation_status": "open"})

# p.326 footnotes, including the p.327 continuation of note 3.
add_statement("st-chp10-p326-n01-pamphlet-titles", NOTES, "cand-9792", "cand-9794", "cites_publication_for_pisani_entry_poems",
              333, 333, 326, 59,
              "The note begins a citation to Componimenti poetici for Pisani's entry; the imprint and two further pamphlet titles continue in the p.326 page-bottom text.",
              "1 Componimenti poetici in occasione del solenne ingresso di Sua Eccellenza Missier Zorzi Pisani ... In.",
              "This is the book's bibliographic note, not an independently consulted pamphlet. The following source segment supplies the continuation of the imprint and the other listed pamphlets.",
              ["cand-9792", "cand-9794", "cand-9795", "cand-9796", "cand-1942"], speaker="Haskell's note", layer="bibliographic citation",
              extra={"continuation_to_segment_id": BODY326, "continuation_line_start": 218, "continuation_line_end": 220, "continuation_status": "closed", "cited_source_independently_consulted": False})
add_statement("st-chp10-p326-n01-marciana-set", BODY326, "cand-9448", "cand-9794", "pamphlet_set_held_and_marked_with_hostile_comments",
              221, 221, 326, 59,
              "Haskell says a set of the pamphlets at Biblioteca Marciana, Misc. 212, carries eighteenth-century comments such as Perfidioso and Seditioso.",
              "The set of these pamphlets in the Biblioteca Marciana, Venice [Misc. 212] are all marked in an eighteenth-century hand with indignant comments such as Perfidioso, Seditioso, etc.",
              "The repository and shelfmark are quoted from Haskell's note; the manuscript/printed set was not independently consulted.",
              ["cand-9448", "cand-2719", "cand-9794", "cand-9795", "cand-9796"], speaker="Haskell's note", layer="bibliographic note",
              extra={"footnote_marker": 1, "cited_source_independently_consulted": False})
add_statement("st-chp10-p326-n01-montesquieu-reference", BODY326, "cand-1696", "cand-9801", "cites_ambri_on_montesquieu_reputation_in_venice",
              221, 222, 326, 59,
              "Haskell directs readers to Ambri, chapter 6, for Montesquieu's reputation in Venice.",
              "For the reputation of\nMontesquieu in Venice see Ambri, chapter 6.",
              "A citation pointer only; the chapter and its account were not independently consulted.",
              ["cand-1696", "cand-2719", "cand-9800", "cand-9801"], speaker="Haskell's note", layer="bibliographic note",
              extra={"footnote_marker": 1, "cited_source_independently_consulted": False})
add_statement("st-chp10-p326-n02-molmenti-reference", NOTES, "cand-9817", "cand-9818", "cites_molmenti_reproduction_and_comments",
              334, 334, 326, 59,
              "Haskell cites Molmenti, 1908, vol. III, pages 45-46, for a reproduction and comments on the visiting card.",
              "2 See the reproduction and comments in Molmenti, 1908, ID, pp. 45-6.",
              "The scan reads III; OCR 'ID' is a page-image correction recorded in S2. The cited volume and pages were not independently consulted.",
              ["cand-9817", "cand-9818", "cand-9802"], speaker="Haskell's note", layer="bibliographic citation",
              extra={"footnote_marker": 2, "cited_source_independently_consulted": False, "ocr_corrections": [{"source_line": 334, "ocr": "ID", "print": "III"}]})
add_statement("st-chp10-p326-n03-haskell-explanation", NOTES, "cand-2204", "cand-9803", "haskell_qualifies_attribution_of_allegorical_pictures",
              335, 335, 326, 59,
              "Haskell calls his explanation of the mysterious episode the only coherent one and disputes a claim by Zannandreis about the paintings; the note continues on p.327.",
              "3 This is the only coherent explanation I can give of this very mysterious episode. The paintings and their destination were referred to by Zannandreis, p. 415, but he is clearly wrong when he says that they",
              "The sentence continues at the footnote below the rule on p.327. The preceding line above that rule begins the p.328 main-text sentence and must not be folded into this note.",
              ["cand-2204", "cand-9803", "cand-8359"], speaker="Haskell's note", layer="authorial note",
              extra={"continuation_to_segment_id": BODY327, "continuation_line_start": 237, "continuation_line_end": 239, "continuation_status": "closed", "footnote_marker": 3, "cited_source_independently_consulted": False})
add_statement("st-chp10-p326-n03-dating-and-exhibition", BODY327, "cand-9826", "cand-1942", "notes_dates_and_qualifies_possible_1780_exhibition",
              237, 239, 326, 60,
              "In the continuation of p.326 note 3, Haskell rejects the claim that the pictures or prints were specially commissioned for Pisani's entry, citing pre-1780 dates for dall'Acqua prints and 1773 publication of Riviera's pamphlets; he nevertheless sees good reason to believe the pictures or prints were exhibited in 1780, citing Zannandreis, Moschini, and the close Pisani-Boscarati relationship.",
              line_map[BODY327][237][line_map[BODY327][237].find("were especially commissioned"): ] + "\n" + line_map[BODY327][238] + "\n" + line_map[BODY327][239],
              "This quote starts below the footnote rule on p.327. The main-text phrase above the rule is excluded and handled as a separate open statement. Haskell's exhibition claim is qualified; cited collections, pamphlets, Zannandreis, and Moschini were not independently consulted.",
              ["cand-9826", "cand-0010", "cand-8262", "cand-9825", "cand-2204", "cand-9806", "cand-8681", "cand-8359", "cand-9820", "cand-1942", "cand-0411"], speaker="Haskell's note", layer="authorial note",
              extra={"continuation_from_statement_id": "st-chp10-p326-n03-haskell-explanation", "footnote_marker": 3, "footnote_segment": NOTES, "footnote_refs": F3, "cited_source_independently_consulted": False})

# p.327 footnotes 1-3; these are citation locators, not independently verified evidence.
add_statement("st-chp10-p327-n01-grimaldo-balbi-citation", NOTES, "cand-9783", "cand-9824", "cites_grimaldo_and_balbi_family_letters",
              336, 336, 327, 60,
              "Haskell cites Grimaldo and a 1780 collection of twenty-four family letters written by Gio. Mattia Balbi to Francesco Donado, held at Biblioteca Correr as MSS. Cicogna 2229.",
              "1 Grimaldo and Memorie Storiche della Correzione 1780, raccolte in XXIV Lettere Familiari scritte al N.U. S.r Francesco Donado .. . dal N.U. S.r Gio. Mattia Balbi—Biblioteca Correr, Venice, MSS. Cicogna 2229.",
              "The source citation is recorded as printed/OCRed; neither Grimaldo nor the manuscript was independently consulted. Do not infer the title's precise institutional meaning from 'Correzione'.",
              ["cand-9783", "cand-9824", "cand-9822", "cand-9823", "cand-8262"], speaker="Haskell's note", layer="bibliographic citation",
              extra={"footnote_marker": 1, "cited_source_independently_consulted": False})
add_statement("st-chp10-p327-n02-zannandreis-citation", NOTES, "cand-8359", "cand-9819", "cites_zannandreis_page_416",
              337, 337, 327, 60,
              "Haskell cites Zannandreis, page 416, for the account connected to Pisani's arrest.",
              "2 Zannandreis, p. 416.",
              "Citation locator only; the cited page was not independently consulted.",
              ["cand-8359", "cand-9819", "cand-1942"], speaker="Haskell's note", layer="bibliographic citation",
              extra={"footnote_marker": 2, "cited_source_independently_consulted": False})
add_statement("st-chp10-p327-n03-moschini-citation", NOTES, "cand-9820", "cand-9821", "cites_moschini_1924_page_145",
              337, 337, 327, 60,
              "Haskell cites Moschini, 1924, page 145, in connection with dall'Acqua's prints at Pisani's entry.",
              "3 Moschini, 1924, p. 145.",
              "Citation locator only; the author's identity and cited work are not resolved here, and the page was not independently consulted.",
              ["cand-9820", "cand-9821", "cand-0010", "cand-1942"], speaker="Haskell's note", layer="bibliographic citation",
              extra={"footnote_marker": 3, "cited_source_independently_consulted": False})

if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("statement id already exists")

# Close the p.325 -> p.326 sentence without changing its source-local quotation.
previous_statement = next((row for row in statements if row["statement_id"] == "st-chp10-p325-pisani-querini-opposition-sentence-continues"), None)
if not previous_statement:
    raise SystemExit("open p.325 continuation statement is missing")
previous_quals = previous_statement["qualifiers"]
if previous_quals.get("continuation_status") != "open" or previous_quals.get("continuation_to_segment_id") != BODY326:
    raise SystemExit("p.325 continuation is not in the expected open state")
previous_quals.update({
    "continuation_status": "closed",
    "continuation_closed_by_segment_id": BODY326,
    "continuation_line_start": 211,
    "continuation_line_end": 211,
    "continuation_suffix": "active Inquisitori di Stato.",
    "mentioned_candidate_ids": sorted(set(previous_quals.get("mentioned_candidate_ids", [])) | {"cand-9739"}),
    "qualification": "The sentence closes at p.326 L211 with the increasingly active Inquisitori di Stato. Preserve the comparison with Angelo Querini and do not infer a specific prosecution or policy.",
})

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
all_ids = {row["candidate_id"] for row in candidate_rows}
for row in new_statements:
    quals = row["qualifiers"]
    if any(cid not in all_ids for cid in quals["mentioned_candidate_ids"]):
        raise SystemExit(f"missing mentioned candidate in {row['statement_id']}")
    for field in ("subject_candidate_id", "object_candidate_id"):
        if row[field] and row[field] not in all_ids:
            raise SystemExit(f"missing {field} in {row['statement_id']}")
for row in statement_rows:
    for sid in row.get("qualifiers", {}).get("footnote_statement_ids", []):
        if sid not in statement_ids and sid not in {new["statement_id"] for new in new_statements}:
            raise SystemExit(f"dangling footnote statement reference in {row['statement_id']}: {sid}")

coverage[PREVIOUS].update({
    "migration_status": "complete",
    "source_line_ranges": "L203-208",
    "note": "P.325 body and notes L329-332 are complete; the final comparison with Angelo Querini closes at p.326 L211, with continuation and footnote statements linked.",
})
coverage[BODY326].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L210-222",
    "note": "Printed p.326 body and its page-bottom continuation of note 1 reviewed against CHP-10.pdf physical page 59. The p.325 sentence closes at L211; the final sentence continues at p.327 L225. Notes 1-3 are linked to the consolidated notes and p.327 note continuation.",
})
coverage[BODY327].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L224-239",
    "note": "Printed p.327 body and the continuation of p.326 footnote 3 reviewed against CHP-10.pdf physical page 60. The sentence from p.326 L217 closes at L225-226. Main-text L237 begins a new sentence that continues at p.328 L241; its phrase above the footnote rule is kept separate from the note continuation below it. P.327 notes 1-3 are linked from the consolidated notes segment.",
})
coverage[NOTES].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L325-337",
    "note": "P.324-325 notes L325-332 and p.326-327 notes L333-337 reviewed and linked to body statements, including the p.326 note 3 continuation at p.327 L237-239. Earlier L284-324 and later lines remain pending.",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
statement_rows.sort(key=lambda row: row["statement_id"])
print(f"p.326-327 + notes L333-337 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage changes: p.325 partial->complete; p.326 queued->complete; p.327 queued->partial pending p.328 L241; notes remain partial through L337")
print(f"totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
