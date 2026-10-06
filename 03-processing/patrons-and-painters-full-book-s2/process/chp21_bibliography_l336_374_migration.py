#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 419."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l336-374"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "5a362f0911b2e62c799a2f1f0a0beaae68337a5db0a51c9cb182c0a5338e4e0f"
BACKUP = ".bak-s2-chp21-bibliography-l336-374-20261004"

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
segment_text = "\n".join(source_lines[335:374])
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
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11262, 26155, 11430, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

new_candidate_specs = [
    ("cand-11284", "Gloria Chiarini de Anna, ‘Leopoldo de’ Medici e la sua raccolta di disegni nel Carteggio d’Artisti dell’Archivio di Stato di Firenze’ (Paragone, 1975, no. 307, pp. 38–64)", 338, "The bibliography identifies the article; the title and journal citation were checked against the page image. Article not independently consulted."),
    ("cand-11285", "Christina Queen of Sweden—a personality of European civilisation (Nationalmuseum, Stockholm, 1966)", 340, "The bibliography identifies the Nationalmuseum catalogue; catalogue contents were not independently consulted."),
    ("cand-11286", "Ignazio Ciampi, Innocenzo X Pamfili e la sua corte (Rome, 1878)", 342, "The bibliography identifies the book; contents were not independently consulted."),
    ("cand-11287", "E. Cicogna, Delle Iscrizioni Veneziane, 6 vols. in 7 (Venice, 1824–53)", 343, "The bibliography identifies a six-volume-in-seven set. Keep distinct from the volume-I citation locator cand-6550 pending S3 identity review; contents were not independently consulted."),
    ("cand-11288", "Anthony Clark, ‘Some early subject pictures by P. G. Batoni’ (Burlington Magazine, 1959, pp. 232–236)", 350, "The bibliography identifies the article; article contents were not independently consulted."),
    ("cand-11289", "Anthony Clark, ‘Lost’ frescoes by Niccolò Berrettoni (Connoisseur, 1961, vol. 148, pp. 190–193)", 351, "The bibliography identifies the article; article contents were not independently consulted."),
    ("cand-11290", "Pierre Clément, Lettres critiques (The Hague, 1767)", 353, "The bibliography identifies the book; contents were not independently consulted."),
    ("cand-11291", "Charles-Nicolas Cochin, Voyage d’Italie—nouvelle édition, 3 vols. (Lausanne, 1773)", 355, "The bibliography identifies a three-volume new edition. Keep distinct from the existing volume-III citation locator cand-8580 pending S3 identity review; contents were not independently consulted."),
    ("cand-11292", "Laura Coggiola-Pittoni, ‘Luigi Dorigny e i suoi freschi Veneziani’ (Rivista di Venezia, 1935, pp. 13–38)", 356, "The bibliography identifies the article; article contents were not independently consulted."),
    ("cand-11293", "Ferdinando Colonna di Stigliano, ‘Inventario dei quadri di casa Colonna fatto da Luca Giordano’ (Napoli Nobilissima, 1895, pp. 29–32)", 364, "The bibliography identifies the article; article contents were not independently consulted."),
    ("cand-11294", "Prospero Colonna, I Colonna (Rome, 1927)", 366, "The bibliography identifies the book; keep distinct from the different 1925 Prospero Colonna citation candidate pending S3 identity review. Contents were not independently consulted."),
    ("cand-11295", "Ugo da Como, Girolamo Muziano—note e documenti (Bergamo, 1930)", 367, "The bibliography identifies the book; contents were not independently consulted."),
    ("cand-11296", "Antonio Conti, Prose e poesie, 2 vols. (Venice, 1739 and 1756)", 374, "The bibliography identifies the two-volume set. Keep distinct from the volume-II citation locator cand-9934 pending S3 identity review; contents were not independently consulted."),
]

entries = [
    {"candidate_id":"cand-11050","start":337,"end":337,"author":"Chiarini, Marco","title":"Antonio Domenico Gabbiani e i Medici","details":"Kunst des Barock in Toskana, pp. 333–343, Munich, 1976","kind":"essay in exhibition/study volume","corrections":[{"line":337,"ocr":"pp333*343","print":"pp. 333–343"}]},
    {"candidate_id":"cand-11284","start":338,"end":339,"author":"Chiarini de Anna, Gloria","title":"Leopoldo de’ Medici e la sua raccolta di disegni nel ‘Carteggio d’Artisti’ dell’Archivio di Stato di Firenze","details":"Paragone, 1975, no. 307, pp. 38–64","kind":"journal article","corrections":[{"line":339,"ocr":"_ d’Artisti; pp. 3 8-64","print":"d’Artisti; pp. 38–64"}]},
    {"candidate_id":"cand-11285","start":340,"end":341,"author":"Christina Queen of Sweden","title":"a personality of European civilisation","details":"Nationalmuseum, Stockholm, 1966","kind":"exhibition catalogue"},
    {"candidate_id":"cand-11286","start":342,"end":342,"author":"Ciampi, Ignazio","title":"Innocenzo X Pamfili e la sua corte","details":"Rome, 1878","kind":"book"},
    {"candidate_id":"cand-11287","start":343,"end":343,"author":"Cicogna, E.","title":"Delle Iscrizioni Veneziane","details":"6 vols. in 7, Venice, 1824–53","kind":"book set","related":["cand-6550"]},
    {"candidate_id":"cand-7499","start":344,"end":344,"author":"Cinelli","title":"Le bellezze di Firenze","details":"Florence, 1677","kind":"book"},
    {"candidate_id":"cand-6359","start":345,"end":346,"author":"Cipolla, Carlo M.","title":"The decline of Italy—the case of a fully matured economy","details":"Economic History Review, 1952, pp. 178–187","kind":"journal article"},
    {"candidate_id":"cand-5985","start":347,"end":348,"author":"Claretta, Gaudenzio","title":"Relazioni d’insigni artisti e virtuosi in Roma col Duca Carlo Emanuele II di Savoia","details":"Archivio della Società Romana di Storia Patria, 1885, pp. 511–554","kind":"journal article","corrections":[{"line":348,"ocr":"Il di Savoia","print":"II di Savoia"}]},
    {"candidate_id":"cand-4995","start":349,"end":349,"author":"Claretta, Gaudenzio","title":"I Reali di Savoia munifici fautori delle arti: contributo alla storia artistica del Piemonte nel secolo XVIII","details":"Miscellanea di Storia Italiana, 1893, pp. 1–309","kind":"journal article"},
    {"candidate_id":"cand-11288","start":350,"end":350,"author":"Clark, Anthony","title":"Some early subject pictures by P. G. Batoni","details":"Burlington Magazine, 1959, pp. 232–236","kind":"journal article"},
    {"candidate_id":"cand-11289","start":351,"end":351,"author":"Clark, Anthony","title":"‘Lost’ frescoes by Niccolò Berrettoni","details":"Connoisseur, 1961, vol. 148, pp. 190–193","kind":"journal article"},
    {"candidate_id":"cand-9464","start":352,"end":352,"author":"Clemens August, Kurfürst","title":"Ausstellung in Schloss Augustusburg zu Brühl","details":"Cologne, 1961","kind":"exhibition catalogue","corrections":[{"line":352,"ocr":". Clemens","print":"Clemens"}]},
    {"candidate_id":"cand-11290","start":353,"end":353,"author":"Clément, Pierre","title":"Lettres critiques","details":"The Hague, 1767","kind":"book","corrections":[{"line":353,"ocr":"Clement","print":"Clément"}]},
    {"candidate_id":"cand-4859","start":354,"end":354,"author":"Clementi, F.","title":"Il carnevale di Roma","details":"2 vols., Rome, 1939","kind":"book set"},
    {"candidate_id":"cand-11291","start":355,"end":355,"author":"Cochin, Charles-Nicolas","title":"Voyage d’Italie—nouvelle édition","details":"3 vols., Lausanne, 1773","kind":"book set","related":["cand-8580"],"corrections":[{"line":355,"ocr":"nouvelle edition","print":"nouvelle édition"}]},
    {"candidate_id":"cand-11292","start":356,"end":356,"author":"Coggiola-Pittoni, Laura","title":"Luigi Dorigny e i suoi freschi Veneziani","details":"Rivista di Venezia, 1935, pp. 13–38","kind":"journal article"},
    {"candidate_id":"cand-8776","start":357,"end":358,"author":"Coggiola-Pittoni, Laura","title":"Di alcuni freschi inediti di Luigi Dorigny in vari centri della Serenissima","details":"Rivista di Venezia, 1935, pp. 295–314","kind":"journal article","corrections":[{"line":357,"ocr":"Serenis-","print":"Serenis- [line-break hyphen]"},{"line":358,"ocr":"’ sima’","print":"sima’"}]},
    {"candidate_id":"cand-6998","start":359,"end":360,"author":"Colapietra, Raffaele","title":"Vita pubblica e classi politiche del viceregno napoletano (1656–1734)","details":"Rome, 1961","kind":"book","corrections":[{"line":360,"ocr":"1961. ■ .","print":"1961."}]},
    {"candidate_id":"cand-9315","start":361,"end":362,"author":"Collins Baker, C. H. and Muriel","title":"The life and circumstances of James Brydges, first duke of Chandos, patron of the liberal arts","details":"Oxford, 1949","kind":"book"},
    {"candidate_id":"cand-11168","start":363,"end":363,"author":"Colombier, Pierre du","title":"Un texte négligé sur les Sacrements de Cassiano dal Pozzo","details":"Gazette des Beaux-Arts, 1964, vol. 63, pp. 89–90","kind":"journal article"},
    {"candidate_id":"cand-11293","start":364,"end":365,"author":"Colonna di Stigliano, Ferdinando","title":"Inventario dei quadri di casa Colonna fatto da Luca Giordano","details":"Napoli Nobilissima, 1895, pp. 29–32","kind":"journal article"},
    {"candidate_id":"cand-11294","start":366,"end":366,"author":"Colonna, Prospero","title":"I Colonna","details":"Rome, 1927","kind":"book"},
    {"candidate_id":"cand-11295","start":367,"end":367,"author":"Conio, Ugo da","title":"Girolamo Muziano—note e documenti","details":"Bergamo, 1930","kind":"book"},
    {"candidate_id":"cand-4209","start":368,"end":369,"author":"Conforti, Michael","title":"Pierre Legros and the role of Sculptors as Designers in late Baroque Rome","details":"Burlington Magazine, 1977, pp. 557–560","kind":"journal article"},
    {"candidate_id":"cand-9369","start":370,"end":371,"author":"Constable, W. G.","title":"An allegorical painting by Canaletto and others","details":"Burlington Magazine, 1954, p. 154","kind":"journal article","mention_surface":"An allegorical painting by Canaletto and others","corrections":[{"line":371,"ocr":"P154Constable","print":"p. 154. [new entry] Constable"}]},
    {"candidate_id":"cand-9914","start":371,"end":372,"author":"Constable, W. G.","title":"Four paintings by Antonio Canale in the Gymnasium zum Grauen Kloster, Berlin","details":"Scritti di Storia dell’Arte in onore di Lionello Venturi, 1956, vol. II, pp. 81–93","kind":"essay in collected volume","mention_surface":"Four paintings by Antonio Canale in the Gymnasium zum Grauen Kloster,\nBerlin"},
    {"candidate_id":"cand-9545","start":373,"end":373,"author":"Constable, W. G.; revised by J. G. Links","title":"Canaletto","details":"2 vols., 2nd ed., Oxford, 1976","kind":"book set"},
    {"candidate_id":"cand-11296","start":374,"end":374,"author":"Conti, Antonio","title":"Prose e poesie","details":"2 vols., Venice, 1739 and 1756","kind":"book set","related":["cand-9934"]},
]

if len(entries) != 28 or len({entry["candidate_id"] for entry in entries}) != 28:
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
    "cand-11050": "Bibliography print p. 419 identifies the 1976 Chiarini article as ‘Antonio Domenico Gabbiani e i Medici’ in Kunst des Barock in Toskana, pp. 333–343. Article not independently consulted.",
    "cand-7499": "Bibliography print p. 419 identifies Cinelli’s 1677 publication as Le bellezze di Firenze (Florence). Contents were not independently consulted.",
    "cand-6359": "Bibliography print p. 419 identifies Carlo M. Cipolla’s article as ‘The decline of Italy—the case of a fully matured economy’ (Economic History Review, 1952, pp. 178–187). Article not independently consulted.",
    "cand-5985": "Bibliography print p. 419 identifies Gaudenzio Claretta’s article as ‘Relazioni d’insigni artisti e virtuosi in Roma col Duca Carlo Emanuele II di Savoia’ (Archivio della Società Romana di Storia Patria, 1885, pp. 511–554). Article not independently consulted.",
    "cand-4995": "Bibliography print p. 419 identifies Gaudenzio Claretta’s 1893 article as ‘I Reali di Savoia munifici fautori delle arti: contributo alla storia artistica del Piemonte nel secolo XVIII’ (Miscellanea di Storia Italiana, pp. 1–309). Article not independently consulted.",
    "cand-4859": "Bibliography print p. 419 identifies F. Clementi’s cited historical publication as Il carnevale di Roma (2 vols., Rome, 1939). Contents were not independently consulted.",
    "cand-8776": "Bibliography print p. 419 identifies the article corresponding to the cited p. 304 locator as Laura Coggiola-Pittoni, ‘Di alcuni freschi inediti di Luigi Dorigny in vari centri della Serenissima’ (Rivista di Venezia, 1935, pp. 295–314). Article not independently consulted.",
    "cand-6998": "Bibliography print p. 419 identifies Raffaele Colapietra’s book as Vita pubblica e classi politiche del viceregno napoletano (1656–1734) (Rome, 1961). Contents were not independently consulted.",
    "cand-9315": "Bibliography print p. 419 identifies the 1949 book as C. H. Collins Baker and Muriel, The life and circumstances of James Brydges, first duke of Chandos, patron of the liberal arts (Oxford). The source gives no further name for Muriel; do not expand it from outside this citation. Contents not independently consulted.",
    "cand-11168": "Bibliography print p. 419 identifies Pierre du Colombier’s article as ‘Un texte négligé sur les Sacrements de Cassiano dal Pozzo’ (Gazette des Beaux-Arts, 1964, vol. 63, pp. 89–90). Article not independently consulted.",
    "cand-4209": "Bibliography print p. 419 identifies Michael Conforti’s article as ‘Pierre Legros and the role of Sculptors as Designers in late Baroque Rome’ (Burlington Magazine, 1977, pp. 557–560). Article not independently consulted.",
    "cand-9369": "Bibliography print p. 419 identifies W. G. Constable’s article as ‘An allegorical painting by Canaletto and others’ (Burlington Magazine, 1954, p. 154). Article not independently consulted.",
    "cand-9914": "Bibliography print p. 419 identifies W. G. Constable’s 1956 essay as ‘Four paintings by Antonio Canale in the Gymnasium zum Grauen Kloster, Berlin’ in Scritti di Storia dell’Arte in onore di Lionello Venturi, vol. II, pp. 81–93. Essay not independently consulted.",
    "cand-9545": "Bibliography print p. 419 identifies the 1976 second edition of Constable’s Canaletto, revised by J. G. Links, as a two-volume set (Oxford). The work was not independently consulted.",
}
for candidate_id, detail in candidate_detail_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type bibliography candidate: {candidate_id}")
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
    return entry.get("quote") or "\n".join(source_lines[entry["start"] - 1:entry["end"]])


def add_mention(candidate_id, surface, note):
    position = segment_text.find(surface)
    if position < 0 or segment_text.find(surface, position + 1) >= 0:
        raise SystemExit(f"mention span text absent or ambiguous for {candidate_id}: {surface!r}")
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update(mention_id=f"m-chp21-bib-l336-374-{len(new_mentions)+1:03d}", segment_id=SEGMENT,
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
    add_mention(entry["candidate_id"], entry.get("mention_surface", quote),
                "S0 bibliography entry; page-image corrections and any shared citation boundaries are recorded in statement qualifiers.")
    extras = {}
    if entry.get("corrections"):
        extras["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("related"):
        extras["related_candidate_ids_for_s3"] = entry["related"]
    add_statement(
        f"st-chp21-bib-l336-374-entry-{index:02d}", entry["candidate_id"], quote,
        entry["start"], entry["end"], f"Haskell lists {entry['title']} in the book bibliography.",
        {"author_as_printed": entry["author"], "title_as_printed": entry["title"],
         "publication_details_as_printed": entry["details"], "record_kind": entry["kind"], "printed_page": 419},
        extra=extras,
    )

if len(new_candidates) != 13 or len(new_mentions) != 28 or len(new_statements) != 28:
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
coverage_by_id[SEGMENT]["source_line_ranges"] = "L336-374"
coverage_by_id[SEGMENT]["note"] = "Printed p.419 contains 28 publication records. Reused 15 archive candidates and added 13. The two Coggiola-Pittoni articles are separate records; the two Constable citations merged at S0 L371 are separated using the page image and non-overlapping title mentions. OCR corrections are recorded without changing S0. Cited works were not independently consulted."
all_candidates = candidates + sorted(new_candidates, key=lambda row: int(row["candidate_id"].split("-")[1]))
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode":"apply" if ARGS.apply else "dry-run",
    "segment":SEGMENT,
    "new_publication_candidates":[row["candidate_id"] for row in new_candidates],
    "reused_publication_candidates":len(entries)-len(new_candidates),
    "publication_records":len(entries),
    "mentions_added":len(new_mentions),
    "statements_added":len(new_statements),
    "candidate_detail_updates":sorted(candidate_detail_updates),
    "page_image_corrections":["L337 pp.333*343→333–343", "L339 remove layout mark and pp.38–64", "L348 Il→II", "L352 remove leading dot", "L353 Clément accent", "L355 édition accent", "L357–358 restore Serenissima line break", "L360 remove stray mark", "L371 split two Constable entries and restore p.154"],
    "coverage":{"disposition":"reviewed","migration_status":"complete","source_line_ranges":"L336-374"},
},ensure_ascii=False,indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP)
        if backup.exists():
            if hashlib.sha256(backup.read_bytes()).hexdigest() != hashlib.sha256(path.read_bytes()).hexdigest():
                raise SystemExit(f"existing recovery copy differs from pre-state: {backup.name}")
        else:
            shutil.copy2(path, backup)
    for candidate_id, detail in candidate_detail_updates.items():
        old = candidate_by_id[candidate_id].get("detail", "").rstrip()
        candidate_by_id[candidate_id]["detail"] = f"{old} {detail}".strip()
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
