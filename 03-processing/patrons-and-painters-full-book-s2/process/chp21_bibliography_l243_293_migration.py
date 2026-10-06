#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 417."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-21Bibliography.pdf"
SEGMENT = "chp-21:21_CHP-21Bibliography:l243-293"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "2c49ffb7987f2d239598f2e44a868040db8e3fe42ec3e72b299d3bfe5f5c5468"
BACKUP = ".bak-s2-chp21-bibliography-l243-293-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


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
    raise SystemExit("bibliography Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("bibliography PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[242:293])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text/hash changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11242, 26094, 11370, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

new_candidate_specs = [
    ("cand-11264", "Arnauld Bréjon de Lavergnée, ‘Tableaux de Poussin et d’autres artistes français dans la collection Dal Pozzo: deux inventaires inédits’ (Revue de l’Art, no. 19, 1973, pp. 79–96)", 246, "The bibliography identifies the article and its journal citation; the article was not independently consulted."),
    ("cand-11265", "Louis-Henri de Loménie, comte de Brienne, Mémoires, edited by Paul Bonnefon, 3 vols. (Paris, 1916–19)", 254, "The bibliography identifies a three-volume edition. Keep distinct from volume-specific citation candidates pending S3 identity review; contents were not independently consulted."),
    ("cand-11266", "G. Brigante Colonna, Olimpia Pamfili (Milan, 1941)", 256, "The bibliography identifies the publication; contents were not independently consulted."),
    ("cand-11267", "E. Brol, ‘Carlo Antonio Pilati a Venezia’ (Pro Cultura, vol. III, 1912)", 263, "The bibliography identifies the article; contents were not independently consulted."),
    ("cand-11268", "Charles de Brosses, Lettres d’Italie, 2 vols. (Dijon, 1927)", 264, "The bibliography identifies a two-volume edition; contents were not independently consulted."),
    ("cand-11269", "Horatio Brown, The Venetian printing press (London, 1891)", 265, "The bibliography identifies the book; contents were not independently consulted."),
    ("cand-11270", "M. V. Brugnoli, ‘Gli affreschi dell’Albani e del Domenichino nel Palazzo di Bassano di Sutri’ (Bollettino d’Arte, 1957, pp. 255–277)", 266, "The printed bibliography lists this article jointly with Brugnoli’s ‘Il soggiorno a Roma’; separate S2 publication candidates preserve the two titles under one shared citation. Neither article was independently consulted."),
    ("cand-11271", "Bruno Brunelli, ‘Un Senatore Veneziano ed una villa scomparsa’ (Le Tre Venezie, 1931, pp. 4–11)", 271, "The bibliography identifies the article and journal citation; the article was not independently consulted."),
    ("cand-11272", "M. Brunetti, S. Maria del Giglio volgo Zobenigo nell’arte e nella storia (Venice, 1952)", 281, "The bibliography identifies the book; contents were not independently consulted."),
    ("cand-11273", "Girolamo Brusoni, Degli Allori d’Eurota, a collection of poems (Venice, 1662)", 282, "The bibliography identifies the 1662 printed collection. Keep distinct from the already indexed literary-work candidate pending S3 identity review; contents were not independently consulted."),
    ("cand-11274", "[Grey Brydges, 5th Lord Chandos], Horae Subsecivae: observations and discourses (London, 1620)", 285, "The bibliography identifies the edition and attributes it to Grey Brydges, 5th Lord Chandos; attribution and identity remain subject to S3. Contents were not independently consulted."),
    ("cand-11275", "D. Gio. Domenico Brustoloni, Elogio funebre dell’eccellentissimo S. Flaminio Corner amplissimo Senatore (Venice, 1779)", 284, "The bibliography identifies the funeral elogio and its 1779 publication; contents were not independently consulted."),
    ("cand-11276", "Charles Burney, Musical Tours in Europe, edited by Percy Scholes, 2 vols. (Oxford, 1959)", 291, "The bibliography identifies a two-volume edition. Keep distinct from the volume-I citation locator candidate pending S3 identity review; contents were not independently consulted."),
    ("cand-11277", "Thomas Buser, ‘Jerome Nadal and early Jesuit Art in Rome’ (Art Bulletin, 1976, pp. 424–433)", 293, "The bibliography identifies the article and journal citation; the article was not independently consulted."),
]

entries = [
    {"candidate_id":"cand-9554","start":244,"end":244,"author":"Brandi, Cesare","title":"Canaletto","details":"1960","kind":"book","corrections":[{"line":244,"ocr":"i960","print":"1960"}]},
    {"candidate_id":"cand-5475","start":245,"end":245,"author":"Brauer, H. und Wittkower, R.","title":"Die Zeichnungen des Gianlorenzo Bernini","details":"Berlin, 1931","kind":"book"},
    {"candidate_id":"cand-11264","start":246,"end":247,"author":"Bréjon de Lavergnée, Arnauld","title":"Tableaux de Poussin et d’autres artistes français dans la collection Dal Pozzo: deux inventaires inédits","details":"Revue de l’Art, no. 19, 1973, pp. 79–96","kind":"journal article"},
    {"candidate_id":"cand-7254","start":248,"end":248,"author":"Brett, R. L.","title":"The Third Earl of Shaftesbury","details":"London, 1951","kind":"book"},
    {"candidate_id":"cand-7713","start":249,"end":249,"author":"Breval, John","title":"Remarks on several parts of Europe relating chiefly to their antiquities and history collected upon the spot in several tours since the year 1723","details":"2 vols., London, 1738","kind":"book"},
    {"candidate_id":"cand-5162","start":250,"end":253,"author":"[Bricarelli, C.]","title":"La chiesa di S. Ignazio e il suo architetto","details":"L’Università Gregoriana del Collegio Romano, 1924, pp. 77–100","kind":"journal article / institutional publication","related":["cand-5161"],"layout_notes":[{"source_lines":"L250–253","note":"S0 OCR places the venue before the author/title; the page image prints the author and title first, followed by L’Università Gregoriana del Collegio Romano, 1924, pp. 77–100."}]},
    {"candidate_id":"cand-11265","start":254,"end":255,"author":"Brienne, Louis-Henri de Loménie Comte de","title":"Mémoires, published by Paul Bonnefon","details":"3 vols., Paris, 1916–19","kind":"edited book set","related":["cand-7071","cand-7100"]},
    {"candidate_id":"cand-11266","start":256,"end":256,"author":"Brigante Colonna, G.","title":"Olimpia Pamfili","details":"Milan, 1941","kind":"book","corrections":[{"line":256,"ocr":"Parafili","print":"Pamfili"}]},
    {"candidate_id":"cand-6187","start":257,"end":258,"author":"Briganti, G.","title":"Cerquozzi pittore di natura morte","details":"Paragone, vol. 53, 1954, pp. 47–52","kind":"journal article","corrections":[{"line":258,"ocr":"voi. 53","print":"vol. 53"}]},
    {"candidate_id":"cand-4566","start":259,"end":260,"author":"Briganti, G.","title":"Opere inedite o poco note di Pietro da Cortona nella Pinacoteca Capitolina","details":"Bollettino dei Musei Comunali di Roma, vol. IV, 1957, pp. 5–14","kind":"journal article","corrections":[{"line":260,"ocr":"in IV","print":"IV"}]},
    {"candidate_id":"cand-4473","start":261,"end":261,"author":"Briganti, G.","title":"Pietro da Cortona","details":"Florence, 1962","kind":"book"},
    {"candidate_id":"cand-11267","start":262,"end":263,"author":"Brol, E.","title":"Carlo Antonio Pilati a Venezia","details":"Pro Cultura, vol. III, 1912","kind":"journal article","layout_notes":[{"source_lines":"L262–263","note":"The S0 transcription detaches Pro Cultura above the article; the page image associates Pro Cultura, III, 1912 with this title."}]},
    {"candidate_id":"cand-11268","start":264,"end":264,"author":"Brosses, Charles de","title":"Lettres d’Italie","details":"2 vols., Dijon, 1927","kind":"book set"},
    {"candidate_id":"cand-11269","start":265,"end":265,"author":"Brown, Horatio","title":"The Venetian printing press","details":"London, 1891","kind":"book"},
    {"candidate_id":"cand-4328","start":266,"end":268,"author":"Brugnoli, M. V.","title":"Il soggiorno a Roma di Bernardo Castello e le sue pitture nel Palazzo di Bassano di Sutri","details":"Bollettino d’Arte, 1957, pp. 255–277","kind":"journal article","mention_surface":"‘Il soggiorno a Roma di Bernardo Castello e le sue pitture nel Palazzo di\nBassano di Sutri’","layout_notes":[{"source_lines":"L266–268","note":"The printed citation shares Bollettino d’Arte, 1957, pp. 255–277 with the following article title in the same bibliography entry."}]},
    {"candidate_id":"cand-11270","start":266,"end":268,"author":"Brugnoli, M. V.","title":"Gli affreschi dell’Albani e del Domenichino nel Palazzo di Bassano di Sutri","details":"Bollettino d’Arte, 1957, pp. 255–277","kind":"journal article","mention_surface":"‘Gli affreschi dell’Albani e del Domenichino nel Palazzo di Bassano","layout_notes":[{"source_lines":"L266–268","note":"The printed citation shares Bollettino d’Arte, 1957, pp. 255–277 with the preceding article title in the same bibliography entry."}]},
    {"candidate_id":"cand-9501","start":269,"end":269,"author":"Brunelli, Bruno","title":"Un’amica del Casanova","details":"Milan, 1923","kind":"book"},
    {"candidate_id":"cand-11271","start":270,"end":271,"author":"Brunelli, Bruno","title":"Un Senatore Veneziano ed una villa scomparsa","details":"Le Tre Venezie, 1931, pp. 4–11","kind":"journal article","corrections":[{"line":271,"ocr":"pp. 4-11- '","print":"pp. 4–11."}],"layout_notes":[{"source_lines":"L270–271","note":"S0 places Le Tre Venezie before the article title; the page image prints the venue after the title."}]},
    {"candidate_id":"cand-8327","start":272,"end":272,"author":"Brunelli, Bruno e Callegari, Alfredo","title":"Ville del Brenta e degli Euganei","details":"1931","kind":"book"},
    {"candidate_id":"cand-10515","start":273,"end":274,"author":"Brunelli Bonetti, B.","title":"Un riformatore mancato—Angelo Querini","details":"Archivio Veneto, 1951, pp. 185–200","kind":"journal article","layout_notes":[{"source_lines":"L273–274","note":"S0 places Archivio Veneto before the article title; the page image prints the venue after the title."}]},
    {"candidate_id":"cand-9481","start":275,"end":277,"author":"Brunetti, M.","title":"Per la storia del viaggio in Ispagna di Gio. Batt. Tiepolo","details":"Ateneo Veneto, 1914","kind":"journal article","layout_notes":[{"source_lines":"L275–277","note":"S0 places Ateneo Veneto above the article title; the page image prints the venue after the title."}]},
    {"candidate_id":"cand-8600","start":278,"end":280,"author":"Brunetti, M.","title":"Un eccezionale collegio peritale: Piazzetta, Tiepolo, Longhi","details":"Arte Veneta, 1951, pp. 158–160","kind":"journal article","layout_notes":[{"source_lines":"L278–280","note":"S0 places Arte Veneta above the article title; the page image prints the venue after the title."}]},
    {"candidate_id":"cand-11272","start":281,"end":281,"author":"Brunetti, M.","title":"S. Maria del Giglio volgo Zobenigo nell’arte e nella storia","details":"Venice, 1952","kind":"book"},
    {"candidate_id":"cand-11273","start":282,"end":283,"author":"Brusoni, Cavalier Girolamo","title":"Degli Allori d’Eurota, poesie di diversi all’Eccellentiss. Sig. Principe D. Camillo Pamphilio raccolte dal Cav. G. B.","details":"Venice, 1662","kind":"edited poetry collection","related":["cand-6357"]},
    {"candidate_id":"cand-11274","start":284,"end":284,"author":"Brustoloni, D. Gio. Domenico","title":"Elogio funebre dell’eccellentissimo S. Flaminio Corner amplissimo Senatore ... 29 Dicembre 1778, S. Canciano","details":"Venice, 1779","kind":"funeral elogio"},
    {"candidate_id":"cand-11275","start":285,"end":286,"author":"[Brydges, Grey, 5th Lord Chandos]","title":"Horae Subsecivae: observations and discourses","details":"London, 1620","kind":"book","corrections":[{"line":286,"ocr":". 1620.","print":"1620."}]},
    {"candidate_id":"cand-7592","start":287,"end":288,"author":"Burchard, L.","title":"Rubens’ ‘Feast of Herod’ at Port Sunlight","details":"Burlington Magazine, 1953, pp. 383–387","kind":"journal article","layout_notes":[{"source_lines":"L287–288","note":"S0 detaches Burlington Magazine from the article; the page image confirms its venue, year, and pages."}]},
    {"candidate_id":"cand-7257","start":289,"end":290,"author":"Burden, Gerald","title":"Sir Thomas Isham, an English collector in Rome in 1677–8","details":"Italian Studies, 1960, pp. 1–25","kind":"journal article","corrections":[{"line":290,"ocr":"i960","print":"1960"}],"layout_notes":[{"source_lines":"L289–290","note":"S0 detaches Italian Studies from the article; the page image confirms its venue, year, and pages."}]},
    {"candidate_id":"cand-11276","start":291,"end":291,"author":"Burney, Charles; edited by Percy Scholes","title":"Musical Tours in Europe","details":"2 vols., Oxford, 1959","kind":"edited book set","related":["cand-9438"]},
    {"candidate_id":"cand-11277","start":292,"end":293,"author":"Buser, Thomas","title":"Jerome Nadal and early Jesuit Art in Rome","details":"Art Bulletin, 1976, pp. 424–433","kind":"journal article","corrections":[{"line":293,"ocr":"424-43 3","print":"424–433"}],"layout_notes":[{"source_lines":"L292–293","note":"S0 detaches Art Bulletin from the article; the page image confirms its venue, year, and pages."}]},
]

if len(entries) != 30 or len({entry["candidate_id"] for entry in entries}) != 30:
    raise SystemExit("bibliography publication specification is incomplete or duplicated")

natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
    for row in candidates
}
new_candidates = []
for candidate_id, name, line_number, detail in new_candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (name.casefold(), "archive")
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {name}")
    row = {field: "" for field in candidate_fields}
    row.update(candidate_id=candidate_id, canonical_name=name, suggested_type="archive", status="open",
               detail=detail, candidate_origin="body-mention", candidate_source_ref=f"{SEGMENT}#L{line_number}")
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

candidate_detail_updates = {
    "cand-9554": "Bibliography print p. 417 confirms Cesare Brandi, Canaletto (1960); this resolves the OCR year ‘i960’ and the possible match. Book contents were not independently consulted.",
    "cand-5162": "Bibliography print p. 417 identifies the cited publication as [Bricarelli, C.], ‘La chiesa di S. Ignazio e il suo architetto’, L’Università Gregoriana del Collegio Romano (1924), pp. 77–100. The page image confirms the OCR line-order displacement. Publication contents were not independently consulted.",
    "cand-6187": "Bibliography print p. 417 identifies the 1954 article as ‘Cerquozzi pittore di natura morte’ in Paragone, vol. 53, pp. 47–52. Article contents were not independently consulted.",
    "cand-4566": "Bibliography print p. 417 identifies the 1957 article as ‘Opere inedite o poco note di Pietro da Cortona nella Pinacoteca Capitolina’ in Bollettino dei Musei Comunali di Roma, vol. IV, pp. 5–14. Article contents were not independently consulted.",
    "cand-4328": "Bibliography print p. 417 confirms this as Brugnoli’s first of two titles in one citation: ‘Il soggiorno a Roma di Bernardo Castello e le sue pitture nel Palazzo di Bassano di Sutri’, Bollettino d’Arte (1957), pp. 255–277. The same citation also lists a second article recorded separately. Neither article was independently consulted.",
    "cand-8327": "Bibliography print p. 417 identifies the 1931 book as Brunelli and Callegari, Ville del Brenta e degli Euganei. The work was not independently consulted.",
    "cand-10515": "Bibliography print p. 417 identifies the 1951 article as ‘Un riformatore mancato—Angelo Querini’ in Archivio Veneto, pp. 185–200. Article contents were not independently consulted.",
    "cand-9481": "Bibliography print p. 417 confirms the 1914 article citation as ‘Per la storia del viaggio in Ispagna di Gio. Batt. Tiepolo’ in Ateneo Veneto. Article contents were not independently consulted.",
    "cand-8600": "Bibliography print p. 417 identifies the 1951 article as ‘Un eccezionale collegio peritale: Piazzetta, Tiepolo, Longhi’ in Arte Veneta, pp. 158–160. Article contents were not independently consulted.",
    "cand-7257": "Bibliography print p. 417 confirms the article date as 1960 (S0 OCR ‘i960’) and its citation in Italian Studies, pp. 1–25. Article contents were not independently consulted.",
    "cand-9438": "Bibliography print p. 417 identifies the set-level edition as Charles Burney, Musical Tours in Europe, edited by Percy Scholes, 2 vols., Oxford 1959. Keep this distinct from the volume-I p. 109 locator pending S3 identity review; cited contents were not independently consulted.",
}
for candidate_id, detail in candidate_detail_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type short-citation candidate: {candidate_id}")
    if detail in candidate.get("detail", ""):
        raise SystemExit(f"candidate detail already updated: {candidate_id}")

mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []
new_statements = []
existing_claim_keys = {
    (row.get("segment_id", ""), " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold())
    for row in statements if isinstance(row.get("qualifiers"), dict)
}


def source_quote(entry):
    return "\n".join(source_lines[entry["start"] - 1:entry["end"]])


def add_mention(candidate_id, surface, note):
    position = segment_text.find(surface)
    if position < 0 or segment_text.find(surface, position + 1) >= 0:
        raise SystemExit(f"mention span text absent or ambiguous for {candidate_id}: {surface!r}")
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update(mention_id=f"m-chp21-bib-l243-293-{len(new_mentions)+1:03d}", segment_id=SEGMENT,
               candidate_id=candidate_id, surface_form=surface, start_char=position, end_char=end, note=note)
    new_mentions.append(row)
    mention_keys.add(key)


def add_statement(statement_id, object_id, quote, line_start, line_end, claim, record, extra=None):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    existing_claim_keys.add(claim_key)
    qualifier = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "claim": claim,
        "speaker": "Haskell’s bibliography",
        "text_layer": "bibliographic entry",
        "qualification": "This statement records the bibliography entry; the cited publication was not independently consulted in this S2 pass.",
        "relation_candidate": False,
        "mentioned_candidate_ids": [object_id],
        "bibliographic_record": record,
    }
    if extra:
        qualifier.update(extra)
    statement = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": object_id,
        "predicate": "bibliography_lists_publication",
        "qualifiers": qualifier,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    if not quote or quote not in "\n".join(source_lines[line_start - 1:line_end]):
        raise SystemExit(f"statement quote/line validation failed: {statement_id}")
    new_statements.append(statement)
    statement_by_id[statement_id] = statement


for index, entry in enumerate(entries, start=1):
    candidate = candidate_by_id.get(entry["candidate_id"])
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {entry['candidate_id']}")
    quote = source_quote(entry)
    mention_surface = entry.get("mention_surface", quote)
    add_mention(entry["candidate_id"], mention_surface,
                "S0 bibliography entry; page-image corrections or layout notes are recorded in the statement qualifiers.")
    extras = {}
    if entry.get("corrections"):
        extras["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("layout_notes"):
        extras["page_image_layout_notes"] = entry["layout_notes"]
    if entry.get("related"):
        extras["related_candidate_ids_for_s3"] = entry["related"]
    add_statement(
        f"st-chp21-bib-l243-293-entry-{index:02d}", entry["candidate_id"], quote,
        entry["start"], entry["end"],
        f"Haskell lists {entry['title']} in the book bibliography.",
        {"author_as_printed": entry["author"], "title_as_printed": entry["title"],
         "publication_details_as_printed": entry["details"], "record_kind": entry["kind"], "printed_page": 417},
        extra=extras,
    )

if len(new_candidates) != 14 or len(new_mentions) != 30 or len(new_statements) != 30:
    raise SystemExit("unexpected migration row counts")
for statement in new_statements:
    for endpoint in (statement["subject_candidate_id"], statement["object_candidate_id"]):
        if endpoint and endpoint not in candidate_by_id:
            raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L243-293"
coverage_by_id[SEGMENT]["note"] = "Printed p.417 contains 30 publications, including two distinct Brugnoli article titles under one shared citation. Reused 16 archive candidates and added 14. Page-image review corrects OCR and restores detached/reordered journal fields; source OCR remains unchanged. The publications were not independently consulted."
all_candidates = candidates + sorted(new_candidates, key=lambda row: int(row["candidate_id"].split("-")[1]))
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment": SEGMENT,
    "new_publication_candidates": [row["candidate_id"] for row in new_candidates],
    "reused_publication_candidates": len(entries) - len(new_candidates),
    "publication_records": len(entries),
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "candidate_detail_updates": sorted(candidate_detail_updates),
    "page_image_corrections": ["L244 i960 → 1960", "L250–253 Bricarelli citation order", "L256 Parafili → Pamfili", "L258 voi. → vol.", "L260 remove OCR ‘in’ before vol. IV", "L268 Brugnoli shared journal layout", "L271 punctuation/page-range OCR", "L286 restore 1620", "L290 i960 → 1960", "L293 pp. 424–433"],
    "coverage": {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L243-293"},
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP)
        if backup.exists():
            raise SystemExit(f"recovery copy already exists: {backup.name}")
        shutil.copy2(path, backup)
    for candidate_id, detail in candidate_detail_updates.items():
        old = candidate_by_id[candidate_id].get("detail", "").rstrip()
        candidate_by_id[candidate_id]["detail"] = f"{old} {detail}".strip()
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
