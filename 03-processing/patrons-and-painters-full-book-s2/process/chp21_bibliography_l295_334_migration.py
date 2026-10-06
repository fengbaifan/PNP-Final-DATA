#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 418."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l295-334"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "460c4d7f3e5ceec4bdd987c0d3f15cc8c765ca07774161d2fc6e75b63f755f97"
BACKUP = ".bak-s2-chp21-bibliography-l295-334-20261004"

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
segment_text = "\n".join(source_lines[294:334])
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
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11256, 26124, 11400, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

new_candidate_specs = [
    ("cand-11278", "James Byam Shaw, Paintings by Old Masters at Christ Church, Oxford (London, 1967)", 297, "The bibliography identifies the Christ Church catalogue; its contents were not independently consulted."),
    ("cand-11279", "P. Angelo Calogerà, Raccolta d’opuscoli scientifici, e filologici, 51 vols. (Venice, 1728–1754)", 301, "The bibliography identifies a 51-volume publication set. Keep distinct from the volume-I citation locator cand-9952 pending S3 identity review; contents were not independently consulted."),
    ("cand-11280", "G. Canevazzi, Papa Clemente IX poeta (Modena, 1900)", 308, "The bibliography identifies the book; keep distinct from the author-only Beani and Canevazzi citation candidate cand-4862 pending S3 identity review. Contents were not independently consulted."),
    ("cand-11281", "Lorenzo Cardella, Memorie storiche de’ Cardinali della Santa Romana Chiesa, 9 vols. (Rome, 1792–97)", 314, "The bibliography identifies a nine-volume edition. Keep distinct from the volume-VII citation locator cand-5480 pending S3 identity review; contents were not independently consulted."),
    ("cand-11282", "Jacques Casanova de Seingalt, Histoire de ma vie, édition intégrale, 6 vols. (Paris–Wiesbaden, 1960–1962)", 319, "The bibliography identifies this six-volume edition. Keep distinct from the author person candidate cand-0591 pending S3 identity review; contents were not independently consulted."),
    ("cand-11283", "Comte de Caylus, Correspondance inédite avec le P. Paciandi, edited by C. Nisard, 2 vols. (Paris, 1877)", 324, "The bibliography identifies the two-volume edition; correspondence contents were not independently consulted."),
]

entries = [
    {"candidate_id":"cand-10373","start":296,"end":296,"author":"Byam Shaw, J.","title":"Two drawings by Domenico Tiepolo, and a note on the date of the frescoes at the Villa Contarini-Pisani","details":"Burlington Magazine, 1960, pp. 529–530","kind":"journal article","related":["cand-8433"],"corrections":[{"line":296,"ocr":"i960, pp. 529-530. ‘","print":"1960, pp. 529–530."}]},
    {"candidate_id":"cand-11278","start":297,"end":297,"author":"Byam Shaw, J.","title":"Paintings by Old Masters at Christ Church, Oxford","details":"London, 1967","kind":"collection catalogue"},
    {"candidate_id":"cand-4959","start":298,"end":299,"author":"Calberg, M.","title":"Hommage au Pape Urbain VIII—Tapisserie de la manufacture Barberini à Rome","details":"Bulletin des Musées Royaux d’Art et d’Histoire, 4ème série, 1959, pp. 99–110","kind":"journal article","corrections":[{"line":298,"ocr":"Vili","print":"VIII"},{"line":299,"ocr":"serie","print":"série"}]},
    {"candidate_id":"cand-4845","start":300,"end":300,"author":"Callari, Luigi","title":"I Palazzi di Roma","details":"3rd ed., Rome, 1944","kind":"book"},
    {"candidate_id":"cand-11279","start":301,"end":301,"author":"[Calogerà, P. Angelo]","title":"Raccolta d’opuscoli scientifici, e filologici","details":"51 vols., Venice, 1728–1754","kind":"edited serial collection","related":["cand-9952"]},
    {"candidate_id":"cand-6585","start":302,"end":302,"author":"Cametti, Alberto","title":"Arcangelo Corelli: i suoi quadri e i suoi violini","details":"Roma, 1927, pp. 412–423","kind":"journal article"},
    {"candidate_id":"cand-11010","start":303,"end":304,"author":"Campbell, Malcolm","title":"Medici Patronage and the Baroque: A Reappraisal","details":"Art Bulletin, 1966, pp. 133–141","kind":"journal article"},
    {"candidate_id":"cand-11011","start":305,"end":305,"author":"Campbell, Malcolm","title":"Pietro da Cortona and the Pitti Palace","details":"Princeton, 1977","kind":"book"},
    {"candidate_id":"cand-4847","start":306,"end":306,"author":"Campori, G.","title":"Lettere artistiche inedite","details":"Modena, 1866","kind":"book"},
    {"candidate_id":"cand-6593","start":307,"end":307,"author":"Canal, Vincenzo da","title":"Vita di Gregorio Lazzarini","details":"Venice, 1809","kind":"book"},
    {"candidate_id":"cand-11280","start":308,"end":308,"author":"Canevazzi, G.","title":"Papa Clemente IX poeta","details":"Modena, 1900","kind":"book","related":["cand-4862"],"corrections":[{"line":308,"ocr":"19ÖO","print":"1900"}]},
    {"candidate_id":"cand-10455","start":309,"end":310,"author":"Canova, Antonio; edited by Elena Bassi","title":"I quaderni di viaggio (1779–1780)","details":"Venice, 1959","kind":"edited diary collection","mention_surface":"I quaderni di viaggio (1779-1780)","corrections":[{"line":310,"ocr":"1959Cantalamessa","print":"1959. [new entry] Cantalamessa"}]},
    {"candidate_id":"cand-4785","start":310,"end":311,"author":"Cantalamessa, Giulio","title":"Le gallerie fidecommissarie romane","details":"Le Gallerie Nazionali Italiane, vol. I, 1894, pp. 79–101","kind":"journal article","mention_surface":"Cantalamessa, Giulio"},
    {"candidate_id":"cand-6999","start":312,"end":312,"author":"Capecelatro, Francesco","title":"Degli annali della Città di Napoli","details":"Naples, 1849","kind":"book"},
    {"candidate_id":"cand-11281","start":314,"end":315,"author":"Cardella, Lorenzo","title":"Memorie storiche de’ Cardinali della Santa Romana Chiesa","details":"9 vols., Rome, 1792–97","kind":"book set","related":["cand-5480"]},
    {"candidate_id":"cand-5803","start":316,"end":316,"author":"Carusi, Enrico","title":"Lettere di Galeazzo Arconato a Cassiano dal Pozzo per lavori sui manoscritti di Leonardo da Vinci","details":"Accademia e Biblioteche d’Italia, vol. III, 1929–30, pp. 504–518","kind":"journal article"},
    {"candidate_id":"cand-5644","start":317,"end":317,"author":"Carutti, Domenico","title":"Breve storia della Accademia dei Lincei","details":"Rome, 1883","kind":"book"},
    {"candidate_id":"cand-11160","start":318,"end":318,"author":"Casale, Vittorio","title":"Trattato della pittura e scultura ‘opera stampata ad istanza del S.r Pietro da Cortona’","details":"Paragone, 1976, no. 313, pp. 67–99","kind":"journal article"},
    {"candidate_id":"cand-11282","start":319,"end":320,"author":"Casanova de Seingalt, Jacques","title":"Histoire de ma vie—édition intégrale","details":"6 vols., Paris–Wiesbaden, 1960–1962","kind":"edited autobiography","related":["cand-0591"],"corrections":[{"line":319,"ocr":"Casanova de Scingali","print":"Casanova de Seingalt"},{"line":319,"ocr":"edition intégrale","print":"édition intégrale"},{"line":320,"ocr":"' 6 vols.","print":"6 vols."}]},
    {"candidate_id":"cand-8047","start":321,"end":321,"author":"Casini, Giorgio","title":"Aggiunte al Crespi","details":"L’Archiginnasio, January–June 1941, pp. 42–50","kind":"journal article"},
    {"candidate_id":"cand-4958","start":322,"end":323,"author":"Cavallo, Adolf S.","title":"Notes on the Barberini tapestry manufactory at Rome","details":"Bulletin of the Museum of Fine Arts, Boston, Spring 1957, pp. 17–26","kind":"journal article"},
    {"candidate_id":"cand-11283","start":324,"end":325,"author":"Caylus, Comte de; edited by C. Nisard","title":"Correspondance inédite avec le P. Paciandi","details":"2 vols., Paris, 1877","kind":"edited correspondence"},
    {"candidate_id":"cand-4558","start":326,"end":326,"author":"Ceccarelli, Giuseppe","title":"I Sacchetti","details":"Rome, 1946","kind":"book"},
    {"candidate_id":"cand-7583","start":327,"end":327,"author":"Ceci, Giuseppe","title":"Un mercante mecenate del secolo XVII: Gaspare Roomer","details":"Napoli Nobilissima, 1920, pp. 160–164","kind":"journal article"},
    {"candidate_id":"cand-9428","start":328,"end":329,"author":"Chaloner, W. H.","title":"The Egertons in Italy and the Netherlands, 1729–1734","details":"Bulletin of the John Rylands Library, 1949–50, pp. 157–170","kind":"journal article","corrections":[{"line":329,"ocr":"170. _","print":"170."}]},
    {"candidate_id":"cand-7102","start":330,"end":330,"author":"Chantelou, Paul Fréart de; published and annotated by L. Lalanne","title":"Journal du voyage du chev. Bernin en France—manuscrit inédit","details":"Gazette des Beaux-Arts, 1877–84","kind":"published manuscript / journal installment"},
    {"candidate_id":"cand-9312","start":331,"end":331,"author":"Charlton, John","title":"Chiswick House and Gardens","details":"London, 1958","kind":"book"},
    {"candidate_id":"cand-11007","start":332,"end":332,"author":"Chiarini, Marco","title":"Artisti alla Corte Granducale","details":"Florence, 1969","kind":"exhibition catalogue"},
    {"candidate_id":"cand-11039","start":333,"end":334,"author":"Chiarini, Marco","title":"I Quadri della Collezione del Principe Ferdinando di Toscana","details":"Paragone, 1975, nos. 301, 303, and 305, pp. 57–98, 75–108, and 55–88 respectively","kind":"journal article published in three installments"},
]

if len(entries) != 29 or len({entry["candidate_id"] for entry in entries}) != 29:
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
    "cand-10373": "Bibliography print p. 418 identifies the 1960 Byam Shaw article as ‘Two drawings by Domenico Tiepolo, and a note on the date of the frescoes at the Villa Contarini-Pisani’ in Burlington Magazine, pp. 529–530. The existing p.357 locator cand-8433 may refer to this same publication; identity consolidation is deferred to S3. Article not independently consulted.",
    "cand-4959": "Bibliography print p. 418 identifies the article as M. Calberg, ‘Hommage au Pape Urbain VIII—Tapisserie de la manufacture Barberini à Rome’ (Bulletin des Musées Royaux d’Art et d’Histoire, 4ème série, 1959, pp. 99–110). Article not independently consulted.",
    "cand-11010": "Bibliography print p. 418 identifies the article as Malcolm Campbell, ‘Medici Patronage and the Baroque: A Reappraisal’ (Art Bulletin, 1966, pp. 133–141). Article not independently consulted.",
    "cand-11011": "Bibliography print p. 418 identifies the book as Malcolm Campbell, Pietro da Cortona and the Pitti Palace (Princeton, 1977). Book not independently consulted.",
    "cand-4847": "Bibliography print p. 418 identifies the 1866 publication as G. Campori, Lettere artistiche inedite (Modena). Contents not independently consulted.",
    "cand-10455": "Bibliography print p. 418 identifies the edited edition as Antonio Canova, I quaderni di viaggio (1779–1780), edited by Elena Bassi (Venice, 1959). Cited pages were not independently consulted.",
    "cand-4785": "Bibliography print p. 418 identifies the article as Giulio Cantalamessa, ‘Le gallerie fidecommissarie romane’ (Le Gallerie Nazionali Italiane, vol. I, 1894, pp. 79–101). Article not independently consulted.",
    "cand-6999": "Bibliography print p. 418 identifies the book as Francesco Capecelatro, Degli annali della Città di Napoli (Naples, 1849). Contents not independently consulted.",
    "cand-10851": "Bibliography print p. 418 names the coauthor as Silvia Carandini and redirects her author heading to ‘Fagiolo dell’Arca and Carandini’, the joint study candidate cand-10852. This supplies the name used in the book bibliography but is not independent identity verification; do not merge with indexed Carandini family members.",
    "cand-5803": "Bibliography print p. 418 identifies Enrico Carusi’s article as ‘Lettere di Galeazzo Arconato a Cassiano dal Pozzo per lavori sui manoscritti di Leonardo da Vinci’ (Accademia e Biblioteche d’Italia, vol. III, 1929–30, pp. 504–518). Article not independently consulted.",
    "cand-5644": "Bibliography print p. 418 identifies Domenico Carutti’s book as Breve storia della Accademia dei Lincei (Rome, 1883). Contents not independently consulted.",
    "cand-11160": "Bibliography print p. 418 identifies Vittorio Casale’s article as ‘Trattato della pittura e scultura “opera stampata ad istanza del S.r Pietro da Cortona”’ (Paragone, 1976, no. 313, pp. 67–99). Article not independently consulted.",
    "cand-8047": "Bibliography print p. 418 confirms Giorgio Casini’s ‘Aggiunte al Crespi’ as L’Archiginnasio (January–June 1941), pp. 42–50. Article not independently consulted.",
    "cand-4958": "Bibliography print p. 418 identifies Adolf S. Cavallo’s article as ‘Notes on the Barberini tapestry manufactory at Rome’ (Bulletin of the Museum of Fine Arts, Boston, Spring 1957, pp. 17–26). Article not independently consulted.",
    "cand-4558": "Bibliography print p. 418 identifies Giuseppe Ceccarelli’s book as I Sacchetti (Rome, 1946). Contents not independently consulted.",
    "cand-9312": "Bibliography print p. 418 identifies John Charlton’s book as Chiswick House and Gardens (London, 1958). Contents not independently consulted.",
    "cand-11007": "Bibliography print p. 418 identifies the exhibition catalogue as Marco Chiarini, Artisti alla Corte Granducale (Florence, 1969). Catalogue not independently consulted.",
    "cand-11039": "Bibliography print p. 418 identifies Chiarini’s ‘I Quadri della Collezione del Principe Ferdinando di Toscana’ as a 1975 article published in three Paragone installments: no. 301, pp. 57–98; no. 303, pp. 75–108; and no. 305, pp. 55–88. The parts are preserved as one bibliography record pending identity review; article not independently consulted.",
}
for candidate_id, detail in candidate_detail_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") not in ("archive", "person"):
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
    row.update(mention_id=f"m-chp21-bib-l295-334-{len(new_mentions)+1:03d}", segment_id=SEGMENT,
               candidate_id=candidate_id, surface_form=surface, start_char=position, end_char=end, note=note)
    new_mentions.append(row)
    mention_keys.add(key)


def add_statement(statement_id, subject_id, object_id, predicate, quote, line_start, line_end, claim,
                  text_layer, qualification, mentioned_ids, extra=None, record=None):
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
        "text_layer": text_layer,
        "qualification": qualification,
        "relation_candidate": False,
        "mentioned_candidate_ids": mentioned_ids,
    }
    if record:
        qualifier["bibliographic_record"] = record
    if extra:
        qualifier.update(extra)
    statement = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject_id,
        "object_candidate_id": object_id,
        "predicate": predicate,
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
                "S0 bibliography entry; page-image corrections and candidate alignment notes are recorded in the statement qualifiers.")
    extras = {}
    if entry.get("corrections"):
        extras["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("related"):
        extras["related_candidate_ids_for_s3"] = entry["related"]
    if entry.get("related"):
        extras["related_candidate_ids_for_s3"] = entry["related"]
    add_statement(
        f"st-chp21-bib-l295-334-entry-{index:02d}", None, entry["candidate_id"],
        "bibliography_lists_publication", quote, entry["start"], entry["end"],
        f"Haskell lists {entry['title']} in the book bibliography.",
        "bibliographic entry",
        "This statement records the bibliography entry; the cited publication was not independently consulted in this S2 pass.",
        [entry["candidate_id"]], extra=extras,
        record={"author_as_printed": entry["author"], "title_as_printed": entry["title"],
                "publication_details_as_printed": entry["details"], "record_kind": entry["kind"], "printed_page": 418},
    )

crossref_quote = source_lines[312]
add_mention("cand-10851", "Carandini, Silvia", "Source heading of a printed bibliography author cross-reference.")
add_mention("cand-10850", "Fagiolo dell’Arca", "Named lead author in the target of the printed bibliography cross-reference.")
add_statement(
    "st-chp21-bib-l295-334-crossref-01", "cand-10851", "cand-10852", "bibliography_cross_reference",
    crossref_quote, 313, 313,
    "Haskell’s bibliography redirects the author heading ‘Carandini, Silvia’ to the joint entry ‘Fagiolo dell’Arca and Carandini’.",
    "bibliographic cross-reference",
    "Records the printed author-entry direction to the joint study candidate; it does not independently establish an external identity or publication contents.",
    ["cand-10851", "cand-10850", "cand-10852"],
    extra={"cross_reference_type":"see", "identity_resolution_deferred_to":"S3", "target_publication_entry_source_line":458},
)

if len(new_candidates) != 6 or len(new_mentions) != 31 or len(new_statements) != 30:
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
coverage_by_id[SEGMENT]["source_line_ranges"] = "L295-334"
coverage_by_id[SEGMENT]["note"] = "Printed p.418 contains 29 publication records and one author cross-reference. Reused 23 archive candidates and added 6; the Carandini-to-Fagiolo author pointer links to existing person/study candidates without an external identity claim. Page-image review restores OCR-split Canova/Cantalamessa entries and corrects names, dates, accents, and stray marks; source OCR remains unchanged. Cited works were not independently consulted."
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
    "bibliography_cross_reference": {"subject":"cand-10851", "target":"cand-10852", "predicate":"bibliography_cross_reference"},
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "candidate_detail_updates": sorted(candidate_detail_updates),
    "page_image_corrections": ["L296 i960→1960 and remove stray quote", "L298 Vili→VIII", "L299 série accent", "L308 19ÖO→1900", "L309–310 split Canova/Cantalamessa entries", "L319 Scingali→Seingalt and édition accent", "L320 remove stray opening mark", "L329 remove trailing underscore"],
    "coverage": {"disposition":"reviewed", "migration_status":"complete", "source_line_ranges":"L295-334"},
}, ensure_ascii=False, indent=2))

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
