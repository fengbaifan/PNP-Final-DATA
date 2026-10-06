"""Controlled S2 migration for p.325 body and p.324-325 footnotes; dry-run by default."""
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
BODY = "chp-10:10_CHP-10_sec_ii:l203-208"
PREVIOUS = "chp-10:10_CHP-10_sec_ii:l194-201"
NEXT = "chp-10:10_CHP-10_sec_ii:l210-222"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BODY_SHA = "16e22c3f4e71979566b340ab472f5e56f67b2e3a0397bca82fa54ab3def9e5a6"
NOTES_SHA = "2086c564ebfd3eacc34753e6c6242b6d44a8e5d6f01c8ef32a4f8ef23de8a593"
BACKUP_SUFFIX = ".bak-s2-chp10-p324-325-20261003"


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
parser.add_argument("--apply", action="store_true", help="write p.325 and p.324-325 note rows after recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_lines = {number: source_lines[number - 1] for number in range(203, 209)}
note_lines = {number: source_lines[number - 1] for number in range(325, 333)}
body_text = "\n".join(body_lines.values())
note_text = "\n".join(note_lines.values())
if hashlib.sha256(body_text.encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("p.325 source segment changed")
if hashlib.sha256(note_text.encode("utf-8")).hexdigest() != NOTES_SHA:
    raise SystemExit("p.324-325 note source span changed")
if body_lines[203] != "[Page 325]" or not body_lines[208].endswith("the increasingly"):
    raise SystemExit("p.325 segment boundaries changed")

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
if state != (9764, 9777, 20672, 9179):
    raise SystemExit(f"unexpected table pre-state: {state}")
if BODY not in coverage or NEXT not in coverage or NOTES not in coverage or PREVIOUS not in coverage:
    raise SystemExit("required coverage row is missing")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.324 is not reviewed/partial")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.325 is not queued/pending")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("note segment is not queued/pending")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.325 already has mention or statement rows")
if any(row["segment_id"] == NOTES and 325 <= int(row.get("qualifiers", {}).get("source_line_start", 0)) <= 332 for row in statements):
    raise SystemExit("p.324-325 note span already has statements")

new_candidates = []


def add_candidate(cid, name, kind, detail, line, segment):
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


add_candidate("cand-9778", "Andrea Tessier", "person", "Named as the author of a cited 1882 article on Francesco Maggiotto; identity is not externally aligned here.", 329, NOTES)
add_candidate("cand-9779", "Andrea Tessier, ‘Di Francesco Maggiotto—pittore veneziano’ (Archivio Veneto, 1882, pp. 289–315)", "archive", "The p.325 note cites Tessier, 1882, pp.289–315; the local bibliography supplies the article title and journal. The article and pages were not independently consulted.", 329, NOTES)
add_candidate("cand-9780", "Poesie in lode del celebre ritrattista viniziano il signor Alessandro Longhi (Venice, 1770)", "archive", "Publication cited in p.324 n.3 for a dedication to Carlo Goldoni; its text is known here only through Haskell's quotation.", 327, NOTES)
add_candidate("cand-9781", "Gasparo Gozzi, Lettere familiari (Venice, 1808)", "archive", "Cited at p.325 n.2, vol.I, p.239, for a letter Haskell dates parenthetically to 1782; the cited edition and page were not independently consulted.", 330, NOTES)
add_candidate("cand-9782", "Gasparo Gozzi, L’abitazione d’un filosofo creduto pazzo (cited at Opere, vol. IV, p. 5)", "archive", "Title and locator supplied by p.324 n.4; the collection edition and cited page were not independently consulted.", 328, NOTES)
add_candidate("cand-9783", "C. Grimaldo, Giorgio Pisani e il suo tentativo di riforma (Venice, 1907)", "archive", "P.325 n.4 directs readers to Grimaldo; the local bibliography supplies the title and publication details. The source was not independently consulted.", 332, NOTES)
add_candidate("cand-9784", "Peasants as a social class in the p.325 discussion of genre painting", "term", "Unspecified peasant group depicted in Gozzi's fable, Tiepolo's rural scenes and Maggiotto's genre painting; no membership or individual works are identified.", 204, BODY)
add_candidate("cand-9785", "Unidentified villa owned by Gian Domenico Tiepolo", "place", "Haskell says Gian Domenico confined some satirical frescoes to his own villa; the building's name and location are not supplied here.", 205, BODY)
add_candidate("cand-9786", "Unidentified satirical frescoes by Gian Domenico Tiepolo in his own villa", "work", "Unspecified group of frescoes concerning Venetian life; no titles or building identity are given.", 205, BODY)
add_candidate("cand-9787", "Unidentified satirical drawings by Gian Domenico Tiepolo on Venetian life", "work", "Haskell says the drawings were presumably distributed only among friends; no titles or recipients are identified.", 205, BODY)
add_candidate("cand-9788", "Flemish tradition of mocking peasants in genre painting", "term", "A pictorial tradition invoked in Haskell's critical comparison; no particular painter, work or source is named.", 206, BODY)
add_candidate("cand-9789", "Venetian government and polity in Giorgio Pisani’s p.325 reform account", "institution", "Local political referent in Haskell's account of Pisani and the Barnabotti; keep distinct from Venice the city pending S3 alignment.", 208, BODY)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []


def add_mention(segment, line_no, surface, cid, note="", occurrence=0):
    lines = body_lines if segment == BODY else note_lines
    text = body_text if segment == BODY else note_text
    if cid not in all_candidate_ids:
        raise SystemExit(f"candidate missing for mention {surface!r}: {cid}")
    starts = []
    cursor = 0
    line = lines[line_no]
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text missing at L{line_no}: {surface!r} occurrence {occurrence}")
    first_line = min(lines)
    start = sum(len(lines[index]) + 1 for index in range(first_line, line_no)) + starts[occurrence]
    if segment == NOTES:
        # Mention offsets are relative to the complete consolidated note segment (L273-349),
        # not just the currently reviewed slice (L325-332).
        start += sum(len(source_lines[index]) + 1 for index in range(272, 324))
    if text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch at L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p325-{len(new_mentions) + 1:04d}",
        "segment_id": segment,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


# p.325 body: names, objects, locations, and explicit pronominal references.
add_mention(BODY, 204, "Millet", "cand-1667", "Index entry Jean-François Millet; comparison does not identify a specific work.")
add_mention(BODY, 204, "Gian Domenico Tiepolo", "cand-2626")
add_mention(BODY, 204, "Giambattista", "cand-2569", "The named father; keep distinct from Gian Domenico Tiepolo.")
add_mention(BODY, 204, "soresteria", "cand-8445", "OCR corrected from the scan to ‘foresteria’; source text is not rewritten.")
add_mention(BODY, 204, "Villa Valmarana", "cand-8444")
add_mention(BODY, 204, "Vicenza", "cand-2769")
add_mention(BODY, 204, "Gozzi", "cand-1220", "Possessive reference to the author of the fable.")
add_mention(BODY, 204, "peasants", "cand-9784")
add_mention(BODY, 204, "Gian Domenico", "cand-2626", "Repeated reference to Gian Domenico Tiepolo.", occurrence=1)
add_mention(BODY, 205, "his own villa", "cand-9785", "The possessive refers to Gian Domenico Tiepolo; the building remains unidentified.")
add_mention(BODY, 205, "frescoes", "cand-9786")
add_mention(BODY, 205, "drawings", "cand-9787")
add_mention(BODY, 205, "Francesco", "cand-1489", "First part of a name split across the OCR line break; continues as Maggiotto on L206.")
add_mention(BODY, 206, "Maggiotto", "cand-1489", "Second part of the split name Francesco Maggiotto.")
add_mention(BODY, 206, "Longhi", "cand-1429")
add_mention(BODY, 206, "Zompini", "cand-2874", "Gaetano Zompini index candidate.")
add_mention(BODY, 206, "peasants", "cand-9784", "Repeated social-category reference.")
add_mention(BODY, 206, "Flemish tradition of mockery", "cand-9788")
add_mention(BODY, 207, "Gozzi", "cand-1220")
add_mention(BODY, 207, "Giotto", "cand-1191")
add_mention(BODY, 207, "Arena chapel", "cand-0686", "Index entry under Churches, Padua.")
add_mention(BODY, 207, "Padua", "cand-1803", "The city, not its university or a polity.")
add_mention(BODY, 207, "Church", "cand-4244", "Institutional Church; distinct from the Arena chapel building.")
add_mention(BODY, 207, "Andrea Memmo", "cand-1642")
add_mention(BODY, 207, "Padua", "cand-1803", occurrence=1)
add_mention(BODY, 208, "Gozzi", "cand-1220")
add_mention(BODY, 208, "Giorgio Pisani", "cand-1942")
add_mention(BODY, 208, "Barnabotti", "cand-0246", "Indexed social class; its identity and scope remain for S3.")
add_mention(BODY, 208, "government", "cand-9789", "Political institution in the Venetian reform context.")
add_mention(BODY, 208, "Venice", "cand-9789", "Political referent here; distinct from the city candidate.")
add_mention(BODY, 208, "Angelo Querini", "cand-2075")
add_mention(BODY, 208, "State", "cand-9789", "Political referent; preserve Haskell's comparison and wording.")

# p.324-325 notes: retain cited-source locators without implying independent consultation.
add_mention(NOTES, 325, "Pascoli, I, p. 31", "cand-4834", "Citation locator for Lione Pascoli, volume I.")
add_mention(NOTES, 326, "Osservatore Veneto", "cand-1791", "Periodical title; the cited issue was not independently consulted.")
add_mention(NOTES, 327, "Goldoni", "cand-1205", occurrence=0)
add_mention(NOTES, 327, "Alessandro Longbi", "cand-1424", "OCR surname corrected to Longhi from the page image.")
add_mention(NOTES, 327, "Pietro", "cand-1429", "Pietro Longhi, named as Alessandro Longhi’s father.")
add_mention(NOTES, 327, "Poesie in lode del celebre ritrattista viniziano il signor", "cand-9780")
add_mention(NOTES, 327, "Girolamo Garganego", "cand-1114")
add_mention(NOTES, 327, "Goldoni", "cand-1205", occurrence=1)
add_mention(NOTES, 327, "Alessandro Longhi", "cand-1424")
add_mention(NOTES, 327, "Goldoni", "cand-1205", occurrence=2)
add_mention(NOTES, 327, "Michael Levey", "cand-3843")
add_mention(NOTES, 328, "Gozzi, IV, p. 5", "cand-1220", "Short citation to the volume containing the fable.")
add_mention(NOTES, 328, "filosofo creduto pazzo", "cand-9782", "Title phrase in the citation; source edition was not consulted.")
add_mention(NOTES, 329, "Andrea Tessier", "cand-9778")
add_mention(NOTES, 329, "Considerazioni elettriche", "cand-1490", "Indexed title of the cited Maggiotto treatise.")
add_mention(NOTES, 329, "Francesco Maggiotto", "cand-1489")
add_mention(NOTES, 329, "Biblioteca Correr", "cand-8262", "Repository in the locator; manuscript not consulted.")
add_mention(NOTES, 330, "G. Gozzi", "cand-1220")
add_mention(NOTES, 330, "Lettere familiari", "cand-9781")
add_mention(NOTES, 332, "Giorgio Pisani", "cand-1942")
add_mention(NOTES, 332, "Grimaldo", "cand-9783", "Bibliographic identity matched to the local bibliography; source not consulted.")

new_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
for left, right in zip(new_mentions, new_mentions[1:]):
    if left["segment_id"] == right["segment_id"] and int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")
if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")

new_statements = []


def add_statement(sid, segment, subject, obj, predicate, start, end, page, physical, claim, quote,
                  qualification, mentioned, *, speaker="Haskell", layer="authorial claim",
                  extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement id already exists: {sid}")
    text = body_text if segment == BODY else note_text
    if quote not in text:
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
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


add_statement("st-chp10-p325-jibe-and-pictures-anticipate-millet", BODY, "", "cand-1667", "fable-pictures-seem-to-anticipate-millet",
              204, 204, 325, 58,
              "Haskell says the jibe about exaggerated foreshortenings has an obvious but unnamed target, while the pictures described in Gozzi's fable seem to anticipate Millet rather than contemporary Venetian painting.",
              "summer clouds, but the actual pictures described seem to anticipate Millet rather than anything being produced in contemporary Venice.",
              "The antecedent begins at p.324 L201; Haskell does not name the jibe's target here. 'Seem to anticipate' is preserved as an interpretation, not a provenance or influence claim.",
              ["cand-1667", "cand-1220"], extra={"continuation_from_segment_id": PREVIOUS, "continuation_prefix": "There can be no doubt who is referred to in the jibe about exaggerated soreshortenings appearing through the"})
add_statement("st-chp10-p325-gian-domenico-painted-rural-scenes-at-valmarana", BODY, "cand-2626", "cand-8446", "painted-rural-scenes-in-foresteria",
              204, 204, 325, 58,
              "Haskell says Gian Domenico Tiepolo painted rural-life scenes in the foresteria of Villa Valmarana near Vicenza.",
              "Gian Domenico Tiepolo, the son of Giambattista, did paint in the soresteria of the Villa Valmarana near Vicenza some scenes from rural Use",
              "OCR 'soresteria' and 'Use' are corrected from the scan to 'foresteria' and 'life'. The work group and place remain locally identified candidates; no modern catalogue identity is asserted.",
              ["cand-2626", "cand-2569", "cand-8444", "cand-8445", "cand-8446", "cand-2769"], extra={"relation_candidate": True, "ocr_corrections": [{"source_line": 204, "ocr": "soresteria", "print": "foresteria"}, {"source_line": 204, "ocr": "rural Use", "print": "rural life"}]})
add_statement("st-chp10-p325-gian-domenico-son-of-giambattista", BODY, "cand-2626", "cand-2569", "son_of",
              204, 204, 325, 58,
              "Haskell identifies Gian Domenico Tiepolo as the son of Giambattista Tiepolo.",
              "Gian Domenico Tiepolo, the son of Giambattista",
              "Explicit relationship stated by Haskell; the formal edge remains for S6.", ["cand-2626", "cand-2569"], extra={"relation_candidate": True})
add_statement("st-chp10-p325-valmarana-scenes-realistic-and-sympathetic", BODY, "cand-2626", "cand-8446", "described-as-realistic-beautiful-and-sympathetic",
              204, 204, 325, 58,
              "Haskell calls the rural scenes realistic by the standards of their day and beautiful and sympathetic.",
              "which were certainly realistic by the standards of his day, but beautiful and sympathetic as they are",
              "This is Haskell's evaluative description, not an independently verified attribution or judgement.", ["cand-2626", "cand-8446"])
add_statement("st-chp10-p325-valmarana-scenes-do-not-match-fable-programme", BODY, "cand-2626", "cand-8446", "scenes-do-not-conform-to-gozzi-fable-programme",
              204, 204, 325, 58,
              "Haskell says the scenes hardly fit the programme represented by Gozzi's philosopher because peasants are shown eating or resting rather than working.",
              "they hardly conform to the programme drawn up by Gozzi’s philosopher—if only because the peasants are always shown eating or resting rather than at work.",
              "The comparison is Haskell's interpretation of a fictional programme and Tiepolo's scenes; it does not identify the fable's painter.", ["cand-2626", "cand-8446", "cand-1220", "cand-9784"])
add_statement("st-chp10-p325-gian-domenico-most-influenced-by-social-ideas", BODY, "cand-2626", "", "described-as-most-influenced-by-new-social-ideas",
              204, 204, 325, 58,
              "Haskell identifies Gian Domenico as the artist most influenced by new ideas about society.",
              "Gian Domenico was certainly the artist most influenced by the new ideas on society",
              "This is Haskell's comparative assessment; the scope of the comparison is the artists discussed in the surrounding passage.", ["cand-2626"])
add_statement("st-chp10-p325-gian-domenico-limited-satirical-observations", BODY, "cand-2626", "cand-9786", "confined-satirical-observations-to-private-frescoes-and-drawings",
              204, 205, 325, 58,
              "Haskell says Gian Domenico confined satirical observations of Venetian life to frescoes in his own villa or drawings, which were presumably circulated only among friends.",
              "he confined his satirical observations of\nVenetian life to frescoes in his own villa or to drawings which were presumably distributed only among friends.",
              "The frescoes, drawings and villa are unspecified groups/places. 'Presumably' applies to distribution of the drawings and is retained.", ["cand-2626", "cand-9785", "cand-9786", "cand-9787"], extra={"relation_candidate": True})
add_statement("st-chp10-p325-maggiotto-scientific-invention-and-treatise", BODY, "cand-1489", "cand-1490", "invented-machine-and-wrote-electrical-treatise",
              205, 206, 325, 58,
              "Haskell says Francesco Maggiotto was affected by advanced scientific ideas, invented an electrical machine and wrote a treatise on it.",
              "Another artist at the end of the century, Francesco\nMaggiotto, was so far affected by advanced scientific ideas that he actually invented an electrical machine and wrote a treatise on the subject.1",
              "The treatise is indexed as Considerazioni elettriche and cited in n.1; neither it nor Tessier's cited article has been independently consulted. The machine is not separately identified.", ["cand-1489", "cand-1490"], extra={"relation_candidate": True, "footnote_marker": 1, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 329, "source_line_end": 329}]})
add_statement("st-chp10-p325-maggiotto-oscillates-between-longhi-and-zompini", BODY, "cand-1489", "", "genre-painting-compared-with-longhi-and-zompini",
              206, 206, 325, 58,
              "Haskell says Maggiotto's genre paintings shifted unsteadily between a coarse version of Longhi and a sentimental interpretation of the more ruthless Zompini.",
              "in his many genre paintings he veered rather unsteadily between a coarse version of Longhi and a sentimental interpretation of the more ruthless Zompini",
              "This is Haskell's critical comparison, not a formal relationship or a judgement independently verified here.", ["cand-1489", "cand-1429", "cand-2874"])
add_statement("st-chp10-p325-maggiotto-flemish-mockery-undermines-labor-dignity", BODY, "cand-1489", "cand-9788", "peasant-scenes-revert-to-mocking-tradition",
              206, 206, 325, 58,
              "Haskell says Maggiotto tended to depict peasants through a crude Flemish tradition of mockery that did little to assert the dignity of labour.",
              "when showing peasants he was always tempted to revert to a crude Flemish tradition of mockery which did little to assert the dignity of labour.",
              "The statement is Haskell's evaluative characterization. The tradition and peasant group are broad terms, not specific works or named collectives.", ["cand-1489", "cand-9784", "cand-9788"])
add_statement("st-chp10-p325-gozzi-returned-to-didactic-painting", BODY, "cand-1220", "", "returned-to-didactic-possibilities-of-painting",
              207, 207, 325, 58,
              "Haskell says Gozzi later returned to the didactic possibilities of painting.",
              "In later years Gozzi turned again to the didactic possibilities of painting.",
              "No exact date is given in this sentence; the following visit is dated 1782.", ["cand-1220"])
add_statement("st-chp10-p325-gozzi-visited-arena-chapel-in-1782", BODY, "cand-1220", "cand-0686", "visited-arena-chapel-in-1782",
              207, 207, 325, 58,
              "Haskell says Gozzi visited Giotto's Arena chapel in Padua in 1782.",
              "In 1782 he visited Giotto’s Arena chapel in Padua",
              "The location is the Arena chapel in Padua; Giotto is the historical artist named in the work's customary title, not the visitor.",
              ["cand-1220", "cand-1191", "cand-0686", "cand-1803"], extra={"relation_candidate": True, "footnote_marker": 2})
add_statement("st-chp10-p325-gozzi-letter-advocates-public-virtue-images", BODY, "cand-1220", "", "letter-proposes-public-images-of-civic-and-patrician-virtue",
              207, 207, 325, 58,
              "In a letter to an unnamed friend, Gozzi asks why painting and sculpture do not publicly represent patrician piety, nobility, patriotic service, support for literature, spending on artists and honour paid to writers.",
              "the piety of some of our patricians and had these displayed in cloisters or schools",
              "The quotation is attributed to Gozzi through Haskell; recipient identity is not supplied. Its proposed programme is not treated as a completed commission.",
              ["cand-1220"], speaker="Gasparo Gozzi, as quoted by Haskell", layer="nested quotation", extra={"footnote_marker": 2, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 330, "source_line_end": 330}]})
add_statement("st-chp10-p325-gozzi-public-display-idea-described-as-new", BODY, "cand-1220", "", "public-display-of-these-themes-described-as-new",
              207, 207, 325, 58,
              "Haskell says such themes were common in private palaces, while Gozzi's idea of making them public was new.",
              "such themes were commonplace in private palaces, but Gozzi’s idea to make them public was a new one.",
              "The novelty claim is Haskell's interpretation; he does not claim that the themes themselves were new.", ["cand-1220"])
add_statement("st-chp10-p325-haskell-says-memmo-implemented-similar-padua-scheme", BODY, "cand-1642", "", "put-into-effect-similar-scheme-in-padua-in-1782",
              207, 207, 325, 58,
              "Haskell says Andrea Memmo was putting a similar scheme into effect in Padua in the same year, 1782, and directs readers to a later chapter.",
              "in that very year, in Padua itself, Andrea Memmo was putting into effect a scheme very similar to the one he was calling for",
              "Haskell writes 'must have been aware', marking this as an inference. The scheme is not identified here and the later chapter remains to be read.",
              ["cand-1642", "cand-1803", "cand-1220"], extra={"footnote_marker": 3, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 331, "source_line_end": 331}]})
add_statement("st-chp10-p325-pisani-seen-as-temporary-advanced-figure", BODY, "cand-1942", "", "seen-by-gozzi-and-others-as-advanced-figure",
              208, 208, 325, 58,
              "Haskell says Gozzi and many others saw Giorgio Pisani for a year or two as an advanced figure battling entrenched conservatism.",
              "Gozzi himself and many others saw him for a year or two as an ‘advanced’ figure battling against the entrenched forces of conservatism.",
              "The view is attributed to Gozzi and others, and its duration is explicitly limited to a year or two.", ["cand-1942", "cand-1220"])
add_statement("st-chp10-p325-pisani-barnabotti-and-government-trouble", BODY, "cand-1942", "cand-0246", "identified-as-barnabotti-member-class",
              208, 208, 325, 58,
              "Haskell identifies Pisani as belonging to the Barnabotti, a class of poor nobles said to have caused the government trouble during the eighteenth century.",
              "Giorgio Pisani belonged to that class of poor nobles, the Barnabotti, which caused the government so much trouble during the eighteenth century.",
              "Membership and characterization are Haskell's account; the political institution remains a local candidate pending S3.", ["cand-1942", "cand-0246", "cand-9789"], extra={"relation_candidate": True, "footnote_marker": 4})
add_statement("st-chp10-p325-pisani-reforms-favor-self-and-friends", BODY, "cand-1942", "", "agitated-for-reforms-primarily-benefiting-self-and-friends",
              208, 208, 325, 58,
              "Haskell says that after entering politics Pisani agitated for reforms designed more to improve his and his friends' conditions than to help the State.",
              "he agitated violently for a series of reforms which were designed far more to improve the conditions of himself and his friends than to help the State as a whole.",
              "This is Haskell's assessment of the reforms' purpose, not an independently verified motive.", ["cand-1942", "cand-9789"])
add_statement("st-chp10-p325-pisani-proposes-return-to-sacred-laws", BODY, "cand-1942", "", "remedy-framed-as-return-to-sacred-laws-of-past",
              208, 208, 325, 58,
              "Haskell says Pisani's proposed remedy for Venice's ills was a return to the sacred laws of the past.",
              "The remedy for all the evils that afflicted Venice lay in a return to",
              "The claim summarizes Haskell's account of Pisani's political rhetoric; it is not treated as an enacted policy.", ["cand-1942", "cand-9789"], extra={"ocr_corrections": [{"source_line": 208, "ocr": "sacred laws of the pass", "print": "sacred laws of the past"}]})
add_statement("st-chp10-p325-pisani-querini-opposition-sentence-continues", BODY, "cand-1942", "cand-2075", "compared-with-querini-in-opposition-to-elites",
              208, 208, 325, 58,
              "Haskell compares Pisani with Angelo Querini and says the logic of Pisani's position drove him to oppose the rich and powerful; the sentence continues on p.326.",
              "like Angelo Querini a generation earlier, he was driven by the logic of his position to oppose the rich and the powerful and above all the increasingly",
              "The final object of 'increasingly' is not present in this segment. Do not close the statement until p.326 L211 identifies the continuation.",
              ["cand-1942", "cand-2075"], extra={"continuation_to_segment_id": NEXT, "continuation_status": "open"})

# Footnote 1-4 on each page: bibliographic locators and cross-reference claims.
add_statement("st-chp10-p324-n1-pascoli-citation", NOTES, "", "cand-4834", "footnote_citation", 325, 325, 324, 57,
              "P.324 note 1 cites Pascoli, volume I, page 31, for the earlier comparison with the Bamboccianti.",
              "Pascoli, I, p. 31.", "The cited edition and page were not independently consulted.", ["cand-4834"],
              speaker="Haskell footnote", layer="bibliographic citation", extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p324-pascoli-made-similar-point-about-bamboccianti", "st-chp10-p324-pascoli-principle-good-work-deserves-reputation"], "citations": [{"source_candidate_id": "cand-4834", "volume": "I", "page": "31"}]})
add_statement("st-chp10-p324-n2-osservatore-citation", NOTES, "", "cand-1791", "footnote_citation", 326, 326, 324, 57,
              "P.324 note 2 cites the 14 February 1761 issue of Osservatore Veneto for Gozzi's statement about Longhi.",
              "Osservatore Veneto, 14 Febbraio 1761.", "The cited issue was not independently consulted.", ["cand-1791"],
              speaker="Haskell footnote", layer="bibliographic citation", extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p324-gozzi-praised-longhi-realism"], "citations": [{"source_candidate_id": "cand-1791", "date": "1761-02-14"}]})
add_statement("st-chp10-p324-n3-dedication-compares-goldoni-and-longhi", NOTES, "cand-1114", "cand-1424", "dedication-compares-goldoni-and-alessandro-longhi",
              327, 327, 324, 57,
              "Haskell calls the 1770 comparison of Carlo Goldoni with Alessandro Longhi, Pietro Longhi's son, very vague; the quoted dedication distinguishes their means but says both paint and describes an old friendship and mutual praise.",
              "very vague comparison was to be made between Goldoni and Alessandro Longbi",
              "The note's OCR surname 'Longbi' is corrected to Longhi from the page image. This is a distinct Goldoni–Alessandro Longhi comparison and does not identify the Tiepolo in p.324's preceding sentence.",
              ["cand-1205", "cand-1424", "cand-1429", "cand-1114", "cand-9780"],
              speaker="Girolamo Garganego in a dedication quoted by Haskell", layer="nested quotation",
              extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p324-gozzi-ready-to-compare-tiepolo-and-longhi", "st-chp10-p324-haskell-infers-longhi-superior-to-tiepolo"], "relation_candidate": True, "ocr_corrections": [{"source_line": 327, "ocr": "Alessandro Longbi", "print": "Alessandro Longhi"}], "citations": [{"source_candidate_id": "cand-9780", "year": "1770"}]})
add_statement("st-chp10-p324-n3-levey-affinity-citation", NOTES, "cand-3843", "cand-8436", "suggested-affinity-between-goldoni-and-alessandro-longhi",
              327, 327, 324, 57,
              "Haskell says Michael Levey had recently suggested an affinity between Goldoni and Alessandro Longhi, citing his 1959 book at page 156.",
              "the suggestion that there is an affinity between Goldoni and Alessandro Longhi has been made by Michael Levey, 1959",
              "The book is matched to the local bibliography entry for Painting in 18th century Venice; page 156 and the book were not independently consulted.",
              ["cand-3843", "cand-1205", "cand-1424", "cand-8436"], speaker="Haskell footnote", layer="bibliographic citation",
              extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p324-haskell-infers-longhi-superior-to-tiepolo"], "citations": [{"source_candidate_id": "cand-8436", "page": "156", "year": "1959"}]})
add_statement("st-chp10-p324-n4-gozzi-fable-source", NOTES, "", "cand-9782", "footnote_citation", 328, 328, 324, 57,
              "P.324 note 4 identifies the Gozzi source of the philosopher fable as L’abitazione d’un filosofo creduto pazzo, volume IV, page 5.",
              "Gozzi, IV, p. 5", "The note's cited volume and page were not independently consulted; the local bibliography lists a second edition of Gozzi's Opere, but edition matching remains unverified.", ["cand-1220", "cand-9782"],
              speaker="Haskell footnote", layer="bibliographic citation", extra={"footnote_number": 4, "linked_body_statement_ids": ["st-chp10-p324-gozzi-fable-old-philosopher-described-as-wise", "st-chp10-p324-gozzi-fable-natural-images-and-beautified-nature", "st-chp10-p324-gozzi-fable-honours-laboring-class"], "citations": [{"source_candidate_id": "cand-9782", "volume": "IV", "page": "5"}]})
add_statement("st-chp10-p325-n1-magggiotto-source-citations", NOTES, "", "cand-9779", "footnote_citation", 329, 329, 325, 58,
              "P.325 note 1 cites Andrea Tessier's 1882 article on Maggiotto, pages 289–315, and Maggiotto's Considerazioni elettriche, located at Biblioteca Correr, Misc. 105113.",
              "Andrea Tessier, 1882, pp. 289-315, and Considerazioni elettriche del signor Francesco Maggiotto",
              "The local bibliography identifies Tessier's article title. The treatise has no date or publisher in the note; neither cited source nor the manuscript locator was independently consulted.", ["cand-9778", "cand-9779", "cand-1489", "cand-1490", "cand-8262"],
              speaker="Haskell footnote", layer="bibliographic citation", extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p325-maggiotto-scientific-invention-and-treatise"], "citations": [{"source_candidate_id": "cand-9779", "pages": ["289", "315"], "year": "1882"}, {"source_candidate_id": "cand-1490", "repository_candidate_id": "cand-8262", "shelfmark": "Misc. 105113"}]})
add_statement("st-chp10-p325-n2-gozzi-letter-citation", NOTES, "", "cand-9781", "footnote_citation", 330, 330, 325, 58,
              "P.325 note 2 cites Gozzi's Lettere familiari, 1808 edition, volume I, page 239, and parenthetically suggests 1782 as the undated letter's date.",
              "Lettere familiari: 1808,1, p. 239",
              "The bracketed date is an editorial suggestion, not a date printed on the letter; the cited page was not independently consulted.", ["cand-1220", "cand-9781"],
              speaker="Haskell footnote", layer="bibliographic citation", extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p325-gozzi-letter-advocates-public-virtue-images"], "citations": [{"source_candidate_id": "cand-9781", "volume": "I", "page": "239", "edition_year": "1808", "suggested_letter_date": "1782"}], "ocr_corrections": [{"source_line": 330, "ocr": "1808,1", "print": "1808, I"}]})
add_statement("st-chp10-p325-n3-chapter-cross-reference", NOTES, "", "", "cross_reference_to_later_chapter", 331, 331, 325, 58,
              "P.325 note 3 directs the reader to Chapter 15 for the related Memmo scheme.", "See Chapter 15.",
              "The referenced chapter has not yet been processed for this task; the cross-reference is not independent corroboration.", ["cand-1642"], speaker="Haskell footnote", layer="internal cross-reference",
              extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p325-haskell-says-memmo-implemented-similar-padua-scheme"], "cross_reference_target": "Chapter 15"})
add_statement("st-chp10-p325-n4-grimaldo-citation", NOTES, "", "cand-9783", "footnote_citation", 332, 332, 325, 58,
              "P.325 note 4 refers readers seeking information on Giorgio Pisani to Grimaldo; the local bibliography identifies the cited work as Giorgio Pisani e il suo tentativo di riforma (Venice, 1907).",
              "For Giorgio Pisani see Grimaldo.", "The bibliographic match comes from the local bibliography; the cited work was not independently consulted.", ["cand-1942", "cand-9783"],
              speaker="Haskell footnote", layer="bibliographic citation", extra={"footnote_number": 4, "linked_body_statement_ids": ["st-chp10-p325-pisani-seen-as-temporary-advanced-figure", "st-chp10-p325-pisani-barnabotti-and-government-trouble"], "citations": [{"source_candidate_id": "cand-9783", "year": "1907"}]})

# Link body footnote markers to the actual note statements above.
all_statements = statements + new_statements
statement_by_id = {row["statement_id"]: row for row in all_statements}


def add_footnote_ref(statement_id, marker, line, note_statement_ids):
    row = statement_by_id.get(statement_id)
    if not row:
        raise SystemExit(f"body statement missing for footnote {marker}: {statement_id}")
    refs = row["qualifiers"].setdefault("footnote_refs", [])
    ref = {"marker": marker, "segment_id": NOTES, "source_line": line, "citation_statement_ids": note_statement_ids}
    if ref not in refs:
        refs.append(ref)


for sid in ["st-chp10-p324-pascoli-made-similar-point-about-bamboccianti", "st-chp10-p324-pascoli-principle-good-work-deserves-reputation"]:
    add_footnote_ref(sid, 1, 325, ["st-chp10-p324-n1-pascoli-citation"])
add_footnote_ref("st-chp10-p324-gozzi-praised-longhi-realism", 2, 326, ["st-chp10-p324-n2-osservatore-citation"])
add_footnote_ref("st-chp10-p324-haskell-infers-longhi-superior-to-tiepolo", 3, 327, ["st-chp10-p324-n3-dedication-compares-goldoni-and-longhi", "st-chp10-p324-n3-levey-affinity-citation"])
for sid in ["st-chp10-p324-gozzi-fable-old-philosopher-described-as-wise", "st-chp10-p324-gozzi-fable-natural-images-and-beautified-nature", "st-chp10-p324-gozzi-fable-honours-laboring-class"]:
    add_footnote_ref(sid, 4, 328, ["st-chp10-p324-n4-gozzi-fable-source"])
add_footnote_ref("st-chp10-p325-maggiotto-scientific-invention-and-treatise", 1, 329, ["st-chp10-p325-n1-magggiotto-source-citations"])
add_footnote_ref("st-chp10-p325-gozzi-letter-advocates-public-virtue-images", 2, 330, ["st-chp10-p325-n2-gozzi-letter-citation"])
add_footnote_ref("st-chp10-p325-haskell-says-memmo-implemented-similar-padua-scheme", 3, 331, ["st-chp10-p325-n3-chapter-cross-reference"])
add_footnote_ref("st-chp10-p325-pisani-barnabotti-and-government-trouble", 4, 332, ["st-chp10-p325-n4-grimaldo-citation"])

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = all_statements
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate id")
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")
all_ids = {row["candidate_id"] for row in candidate_rows}
for row in new_mentions:
    if row["candidate_id"] not in all_ids:
        raise SystemExit(f"missing mention candidate: {row['mention_id']}")
for row in new_statements:
    quals = row["qualifiers"]
    if any(cid not in all_ids for cid in quals["mentioned_candidate_ids"]):
        raise SystemExit(f"missing mentioned candidate: {row['statement_id']}")
    if row["subject_candidate_id"] and row["subject_candidate_id"] not in all_ids:
        raise SystemExit(f"missing statement subject: {row['statement_id']}")
    if row["object_candidate_id"] and row["object_candidate_id"] not in all_ids:
        raise SystemExit(f"missing statement object: {row['statement_id']}")

coverage[PREVIOUS].update({"migration_status": "complete", "source_line_ranges": "L194-201", "note": "P.324 body, its four footnotes L325-328 and the p.325 continuation at L204 are now semantically linked. Its final sentence closes on p.325; no p.324 body gap remains."})
coverage[BODY].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L203-208", "note": "Printed p.325 body reviewed against CHP-10.pdf physical page 58. The final comparison with Angelo Querini stops at 'increasingly' and continues at p.326 L211. Footnotes L329-332 were semantically recorded in the consolidated notes segment."})
coverage[NOTES].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L325-332", "note": "P.324 notes 1-4 (L325-328) and p.325 notes 1-4 (L329-332) reviewed and linked to body statements. Earlier notes in this consolidated segment and later lines remain pending."})

candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
statement_rows.sort(key=lambda row: row["statement_id"])
print(f"p.325 + p.324-325 notes preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage changes: p.324 partial->complete; p.325 queued->partial; consolidated notes queued->partial")
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
