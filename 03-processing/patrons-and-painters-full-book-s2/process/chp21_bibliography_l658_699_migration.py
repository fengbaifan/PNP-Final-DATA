#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 427."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l658-699"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "f13f3e705185e96f51cbf120bab19d4f07a88023dc68290b13caf60b6be76eb0"
BACKUP = ".bak-s2-chp21-bibliography-l658-699-20261007"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("bibliography Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("bibliography PDF changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[657:699])
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

if (len(candidates), len(mentions), len(statements), len(coverage)) != (
    11347,
    26392,
    11667,
    832,
):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (
    coverage_by_id[SEGMENT]["disposition"],
    coverage_by_id[SEGMENT]["migration_status"],
) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

# Confirm both See-also targets were already read and have an explicit local
# bibliography-list statement before recording these pointers.
target_statements = {
    "st-chp21-bib-l577-614-entry-13": ("cand-8638", 595),
    "st-chp21-bib-l538-575-entry-05": ("cand-11345", 544),
}
for statement_id, (candidate_id, line) in target_statements.items():
    target = statement_by_id.get(statement_id)
    if not target or target.get("object_candidate_id") != candidate_id:
        raise SystemExit(f"missing/changed bibliography pointer target: {statement_id}")
    qualifiers = target.get("qualifiers") or {}
    if (
        target.get("segment_id") != f"chp-21:21_CHP-21Bibliography:l{538 if line == 544 else 577}-{575 if line == 544 else 614}"
        or qualifiers.get("source_line_start") != line
    ):
        raise SystemExit(f"bibliography pointer target anchor changed: {statement_id}")

# Refine citations only where local title/year/pages or the surrounding note
# make a unique book-bibliography match. Incomplete or inconsistent locators
# remain distinct and are linked for S3 instead of being merged.
candidate_updates = [
    {
        "id": "cand-3420", "type": "archive", "expected": "L’Hoggidi",
        "name": "Secondo Lancellotti, L’Hoggidi overo il mondo non peggiore nè più calamitoso del passato (Venezia, 1627)",
        "detail": "Printed p.427 supplies the full title and Venezia 1627 for the work already cited in Haskell’s note. The note says it was first published in 1627 and often reprinted; the work was not independently consulted. The Lancellotti index candidates remain separate for S3 identity review.",
    },
    {
        "id": "cand-5473", "type": "archive", "expected": "Lanckoronska (1935), cited publication; title and edition unresolved",
        "name": "K. Lanckoronska, Decoracja Kosciola Il Gesù (Lvov, 1935)",
        "detail": "Printed p.427 supplies the title and Lvov 1935 for the Lanckoronska (1935) publication already cited in the book. The page image reads ‘Il Gesù’; S0 OCR has ‘II Gesù’. The cited work was not independently consulted and author identity remains for S3.",
    },
    {
        "id": "cand-8956", "type": "archive",
        "expected": "K. Lankheit, 'Florentiner Bronze-arbeiten für Kurfürst Johann Wilhelm von der Pfalz' (1956)",
        "name": "K. Lankheit, ‘Florentiner Bronze-arbeiten für Kurfürst Johann Wilhelm von der Pfalz’ (Münchner Jahrbuch der bildenden Kunst, 1956, pp. 185–210)",
        "detail": "Printed p.427 supplies the periodical and page range for the matching p.403 note citation. The article was not independently consulted; the initialed author form remains distinct from the Lankheit person candidates until S3.",
    },
    {
        "id": "cand-10860", "type": "archive",
        "expected": "Irving Lavin’s analysis of Bernini’s transformation of the crossing of St Peter’s (1968; title unspecified)",
        "name": "Irving Lavin, Bernini and the Crossing of Saint Peter’s (New York, 1968)",
        "detail": "Printed p.427 supplies the title and publication details for the Lavin 1968 analysis named in the postscript and cited at p.397 n.1. The work and cited pages were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-10931", "type": "archive",
        "expected": "Irving Lavin’s 1972 article on Bernini and the Jesuits (title unspecified)",
        "name": "Irving Lavin, ‘Bernini’s death’ (Art Bulletin, 1972, pp. 159–186)",
        "detail": "Printed p.427 lists the sole Lavin 1972 article, pp.159–186, which contains the p.399 n.3 locator at pp.169–171. The article was not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-10853", "type": "archive",
        "expected": "Marilyn Aronberg Lavin’s publication of Barberini family inventories (title unspecified)",
        "name": "Marilyn Aronberg Lavin, Seventeenth-Century Barberini Documents and Inventories of Art (New York, 1975)",
        "detail": "Printed p.427 supplies the title and New York 1975 for the inventory publication discussed on p.396. Its contents were not independently consulted; Marilyn Aronberg Lavin remains separate from similarly named candidates until S3.",
    },
    {
        "id": "cand-6165", "type": "archive",
        "expected": "Unidentified publication by Leman cited in Haskell p.139 n.3, pp.13 ff.",
        "name": "A. Leman, Recueil des Instructions Générales aux Nonces Ordinaires de France de 1624 à 1634 (Paris, 1919)",
        "detail": "The p.139 n.3 locator ‘Leman, pp.13 ff.’ matches the sole Leman item in the local bibliography, whose title concerns instructions to French nuncios. The work was not independently consulted; the citation’s full publication details come only from p.427.",
    },
    {
        "id": "cand-10237", "type": "archive",
        "expected": "Aurelio Lepre, 1959, pp.80-99 (article title unspecified)",
        "name": "A. Lepre, ‘Note sull’Algarotti’ (Società, 1959, fasc. I, pp. 80–99)",
        "detail": "Printed p.427 supplies the article title and journal for the exact 1959, pp.80–99 citation. The article was not independently consulted; the cited-page text remains unverified.",
    },
    {
        "id": "cand-10298", "type": "archive",
        "expected": "Levey, Burlington Magazine, 1957, pp. 89–91 (citation locator in p.353 note 1)",
        "name": "M. Levey, ‘Tiepolo’s “Empire of Flora”’ (Burlington Magazine, 1957, pp. 89–91)",
        "detail": "Printed p.427 supplies the title for the exact p.353 n.1 journal and page locator. The article was not independently consulted; person-level identity remains for S3.",
    },
    {
        "id": "cand-9463", "type": "archive",
        "expected": "Michael Levey, ‘The modello for Tiepolo’s altarpiece at Nymphenburg’ (Burlington Magazine, 1957, pp.256-261; citation locator)",
        "name": "M. Levey, ‘The modello for Tiepolo’s altarpiece at Nymphenburg’ (Burlington Magazine, 1957, pp. 256–261)",
        "detail": "Printed p.427 confirms the title, journal, year and page range for the p.295 n.5 citation. The article was not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-8453", "type": "archive",
        "expected": "Levey, Journal of Warburg Institute, 1957, pages 298–317 (citation locator)",
        "name": "M. Levey, ‘Tiepolo’s treatment of classical story at Villa Valmarana’ (Journal of the Warburg and Courtauld Institutes, 1957, pp. 298–317)",
        "detail": "Printed p.427 supplies the article title and full journal name for the p.296 note locator. The page image reads ‘Valmarana’ and ‘Journal of the Warburg and Courtauld Institutes’; the article was not independently consulted. Author identity remains for S3.",
    },
    {
        "id": "cand-9899", "type": "archive",
        "expected": "Levey, Arte Veneta, 1958, page 221 (citation locator)",
        "name": "M. Levey, ‘A note on Marshall Schulenburg’s collection’ (Arte Veneta, 1958, p. 221)",
        "detail": "Printed p.427 identifies the exact title for the p.284 n.4 citation to Levey, Arte Veneta (1958), p.221. The article and cited page were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-9518", "type": "archive",
        "expected": "M. Levey, “Wilson and Zuccarelli at Venice” (Burlington Magazine, 1959, pp.139–143; citation locator)",
        "name": "M. Levey, ‘Wilson and Zuccarelli at Venice’ (Burlington Magazine, 1959, pp. 139–143)",
        "detail": "Printed p.427 confirms the exact title and range for the p.301 n.7 citation. The article and cited pages were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-9443", "type": "archive",
        "expected": "M. Levey, 'Francesco Zuccarelli in England' (Italian Studies, 1959, pp.1-20)",
        "name": "M. Levey, ‘Francesco Zuccarelli in England’ (Italian Studies, 1959, pp. 1–20)",
        "detail": "Printed p.427 confirms the title and range for the p.292 n.5 citation. The article and cited pages were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-8436", "type": "archive",
        "expected": "Michael Levey, Painting in 18th century Venice (London, 1959; citation locator)",
        "name": "M. Levey, Painting in 18th century Venice (London, 1959)",
        "detail": "Printed p.427 confirms the short-form title and London 1959 for the p.296 n.2 citation. The book and cited page were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-10302", "type": "archive",
        "expected": "Levey, Burlington Magazine, 1960, pp.250–257 (citation locator in p.354 note 2)",
        "name": "M. Levey, ‘Two paintings by Tiepolo from the Algarotti Collection’ (Burlington Magazine, 1960, pp. 250–257)",
        "detail": "Printed p.427 supplies the title for the exact p.354 n.2 journal, year and page-range citation. The article and cited pages were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-11097", "type": "archive",
        "expected": "Michael Levey's 1962 study of Canaletto's altered Venice view for Joseph Smith",
        "name": "M. Levey, ‘Canaletto’s Fourteen Paintings and Visentini’s Prospectus Magni Canalis’ (Burlington Magazine, 1962, pp. 333–341)",
        "detail": "Printed p.427 supplies the title, journal and range for the 1962 Levey study described in the postscript. The article was not independently consulted; its interpretation and person identity remain for S3.",
    },
    {
        "id": "cand-11000", "type": "archive",
        "expected": "Michael Levey's catalogue of later Italian pictures in the Queen's collection",
        "name": "M. Levey, The later Italian pictures in the collection of Her Majesty the Queen (London, 1964)",
        "detail": "Printed p.427 supplies the title and London 1964 for the catalogue discussed in the postscript. Its contents were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-11140", "type": "archive",
        "expected": "Michael Levey's 1978 article on the Tiepolo portrait theory",
        "name": "M. Levey, ‘Three slight revisions to Tiepolo scholarship’ (Arte Veneta, 1978, pp. 418–422)",
        "detail": "Printed p.427 supplies the exact title, journal and range for the postscript’s Levey 1978 citation. The article was not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-6239", "type": "archive",
        "expected": "“Poesie e lettere inedite di Salvator Rosa” (Biblioteca dell’Archivum Romanicum, 1950)",
        "name": "U. Limentani, ‘Poesie e lettere inedite di Salvator Rosa’ (Biblioteca dell’Archivum Romanicum, 1950)",
        "detail": "Printed p.427 supplies the author for the title cited at pp.143 and 187 notes. The cited publication and pages were not independently consulted; the page-187 citation’s source statement and claim qualifiers remain unchanged.",
    },
    {
        "id": "cand-6206", "type": "archive",
        "expected": "Limentani (1961), cited analysis, pp. 163-179",
        "name": "U. Limentani, La satira nel Seicento (Milano-Napoli, 1961)",
        "detail": "Printed p.427 supplies the title and place for the Limentani 1961 analysis cited at pp.143–144. The book and cited pages were not independently consulted. The distinct co-authored Spini and Limentani locator cand-6377 remains unresolved and is linked for S3.",
    },
    {
        "id": "cand-4842", "type": "archive",
        "expected": "Litta, cited genealogical publication; title and edition unspecified",
        "name": "Pompeo Litta, Famiglie celebri italiane (Milano e Torino, 1819–81)",
        "detail": "Printed p.427 supplies the title, publication places and printed date range for the Litta citation in p.55 n.1. The publication and cited passage were not independently consulted; the date range is retained as printed.",
    },
    {
        "id": "cand-8324", "type": "archive",
        "expected": "Livan 1935, pages 406-408, cited on p.254 note 1",
        "name": "Lina Livan, ‘Alcune date su Palazzo Rezzonico’ (Rivista di Venezia, 1935, pp. 406–408)",
        "detail": "Printed p.427 supplies the title and journal for the exact 1935, pp.406–408 locator cited at p.254 n.1. The article and cited pages were not independently consulted; the bibliography contributor heading remains source-derived.",
    },
    {
        "id": "cand-9483", "type": "archive",
        "expected": "Alessandro Longhi, Compendio delle vite de’ pittori veneziani istorici più rinomati del presente secolo (Venezia, 1762; citation locator)",
        "name": "Alessandro Longhi, Compendio delle vite de’ pittori veneziani istorici più rinomati del presente secolo (Venezia, 1762)",
        "detail": "Printed p.427 confirms the title and Venezia 1762 for the A. Longhi citation in p.297 n.6. The book and cited passage were not independently consulted; the bibliographic author form remains linked to the Longhi index candidate for S3.",
    },
]

natural_keys = {}
for row in candidates:
    if not row.get("index_entry_id") and row.get("suggested_type", "").strip():
        key = (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
        natural_keys.setdefault(key, set()).add(row["candidate_id"])

for update in candidate_updates:
    candidate = candidate_by_id.get(update["id"])
    if not candidate or candidate.get("suggested_type") != update["type"]:
        raise SystemExit(f"missing/wrong-type candidate: {update['id']}")
    if candidate["canonical_name"] != update["expected"]:
        raise SystemExit(f"candidate identity label changed: {update['id']}")
    old_key = (
        candidate["canonical_name"].strip().casefold(),
        candidate["suggested_type"].strip().casefold(),
    )
    new_key = (update["name"].strip().casefold(), candidate["suggested_type"].strip().casefold())
    collisions = natural_keys.get(new_key, set()) - {update["id"]}
    if collisions:
        raise SystemExit(f"candidate name collision {update['id']}: {sorted(collisions)}")
    natural_keys.get(old_key, set()).discard(update["id"])
    natural_keys.setdefault(new_key, set()).add(update["id"])
    candidate["canonical_name"] = update["name"]
    candidate["detail"] = update["detail"]

new_candidate_specs = [
    (
        "cand-11369", "archive",
        "Klaus Lankheit, Florentinsche Barockplastik—Die Kunst am Hofe der Letzten Medici (1670–1743; München, 1962)",
        "Printed p.427 lists this book. The spelling ‘Florentinsche’ is confirmed by the page image and is retained as printed. The book was not independently consulted; link the title- and page-only Lankheit citations for S3 without assuming they refer to this work.",
        664,
    ),
    (
        "cand-11370", "archive",
        "Madeleine Laurain-Portemer, ‘La politique artistique de Mazarin’ (Atti dei Convegni Lincei, 35, 1977, pp. 41–76)",
        "Printed p.427 lists this article and the Colloquio italo-francese context. The article was not independently consulted.",
        665,
    ),
    (
        "cand-11371", "archive",
        "E. Lavagnino, Gli artisti italiani in Germania, III: I pittori e gl’incisori (Roma, 1943)",
        "Printed p.427 lists volume III. The existing Lavagnino citation candidate is linked for S3, but page-only citations at p.282–283 do not specify a volume and are not assigned to this book here. The book was not independently consulted.",
        667,
    ),
    (
        "cand-11372", "archive",
        "V. Lazari, Notizia delle opere d’arte e d’antichità della Raccolta Correr (Venezia, 1859)",
        "Printed p.427 lists this publication. The text and cited pages were not independently consulted; the initialed Lazari person candidate remains separate for S3.",
        672,
    ),
    (
        "cand-11373", "archive",
        "M. Levey, ‘Tiepolo’s “Banquet of Cleopatra” at Melbourne’ (Arte Veneta, 1955, pp. 199–203)",
        "Printed p.427 lists pp.199–203. The p.352 n.1 citation candidate prints pp.193–203; the discrepancy is preserved and the locator stays separate for S3. The article was not independently consulted.",
        676,
    ),
    (
        "cand-11374", "archive",
        "C. A. Levi, Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni (Venezia, 1900)",
        "Printed p.427 lists this publication. Related C. A. Levi volume/page citations elsewhere in the book remain separate for S3; this work was not independently consulted.",
        691,
    ),
    (
        "cand-11375", "person",
        "M. Levey (author heading in Haskell’s bibliography; identity unresolved)",
        "Source-derived person candidate for the printed heading ‘Levey, M.’ and its See also pointer to the Haskell and Levey article. Do not merge with full-name or note-specific Levey candidates before S3.",
        690,
    ),
    (
        "cand-11376", "person",
        "Lina Livan (contributor heading in Haskell’s bibliography; identity unresolved)",
        "Source-derived person candidate for the printed heading ‘Livan, Lina’. Its See also pointer targets the Gradenigo edition that names Lina Livan as editor; no external identity alignment is asserted.",
        698,
    ),
]

new_candidates = []
for candidate_id, candidate_type, canonical_name, detail, source_line in new_candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (canonical_name.strip().casefold(), candidate_type.casefold())
    if natural_keys.get(key):
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {canonical_name}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=canonical_name,
        suggested_type=candidate_type,
        status="open",
        detail=detail,
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{source_line}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.setdefault(key, set()).add(candidate_id)

entries = [
    {"candidate_id":"cand-3420","start":659,"end":660,"author":"Lancellotti, Secondo","title":"L’Hoggidi overo il mondo non peggiore nè più calamitoso del passato","details":"Venezia 1627","kind":"book","related":["cand-1355","cand-1356"]},
    {"candidate_id":"cand-5473","start":661,"end":661,"author":"Lanckoronska, K.","title":"Decoracja Kosciola Il Gesù","details":"Lvov 1935","kind":"book","corrections":[{"line":661,"ocr":"II Gesù","print":"Il Gesù"}]},
    {"candidate_id":"cand-8956","start":662,"end":663,"author":"Lankheit, K.","title":"Florentiner Bronze-arbeiten für Kurfürst Johann Wilhelm von der Pfalz","details":"Münchner Jahrbuch der bildenden Kunst, 1956, pp. 185-210","kind":"journal article","related":["cand-10997"],"corrections":[{"line":663,"ocr":"Miinchner","print":"Münchner"}]},
    {"candidate_id":"cand-11369","start":664,"end":664,"author":"Lankheit, Klaus","title":"Florentinsche Barockplastik—Die Kunst am Hofe der Letzten Medici","details":"1670-1743, München 1962","kind":"book","related":["cand-10997","cand-11182","cand-11191"],"page_image_notes":["The printed page reads ‘Florentinsche’; this spelling is preserved despite its unusual form."] ,"corrections":[{"line":664,"ocr":"16701743","print":"1670-1743"}]},
    {"candidate_id":"cand-11370","start":665,"end":666,"author":"Laurain-Portemer, Madeleine","title":"La politique artistique de Mazarin","details":"Atti dei Convegni Lincei, 35 (Colloquio italo-francese: Il Cardinale Mazzarino in Francia), 1977, pp. 41-76","kind":"journal article"},
    {"candidate_id":"cand-11371","start":667,"end":667,"author":"Lavagnino, E.","title":"Gli artisti italiani in Germania, III: I pittori e gl’incisori","details":"Roma 1943","kind":"book","related":["cand-7251","cand-9457"]},
    {"candidate_id":"cand-10860","start":668,"end":668,"author":"Lavin, Irving","title":"Bernini and the Crossing of Saint Peter’s","details":"New York 1968","kind":"book","related":["cand-10859"]},
    {"candidate_id":"cand-10931","start":669,"end":669,"author":"Lavin, Irving","title":"Bernini’s death","details":"Art Bulletin, 1972, pp. 159-186","kind":"journal article","related":["cand-10859"]},
    {"candidate_id":"cand-10853","start":670,"end":671,"author":"Lavin, Marilyn Aronberg","title":"Seventeenth-Century Barberini Documents and Inventories of Art","details":"New York 1975","kind":"book","related":["cand-4787"]},
    {"candidate_id":"cand-11372","start":672,"end":672,"author":"Lazari, V.","title":"Notizia delle opere d’arte e d’antichità della Raccolta Correr","details":"Venezia 1859","kind":"book","related":["cand-10702"]},
    {"candidate_id":"cand-6165","start":673,"end":674,"author":"Leman, A.","title":"Recueil des Instructions Générales aux Nonces Ordinaires de France de 1624 à 1634","details":"Paris 1919","kind":"book"},
    {"candidate_id":"cand-10237","start":675,"end":675,"author":"Lepre, A.","title":"Note sull’Algarotti","details":"Società, 1959, fasc. I, pp. 80-99","kind":"journal article","related":["cand-10236"],"corrections":[{"line":675,"ocr":"fase, i","print":"fasc. I"}]},
    {"candidate_id":"cand-11373","start":676,"end":676,"author":"Levey, M.","title":"Tiepolo’s ‘Banquet of Cleopatra’ at Melbourne","details":"Arte Veneta, 1955, pp. 199-203","kind":"journal article","related":["cand-10281","cand-11375","cand-10999","cand-10297"],"page_image_notes":["The p.352 n.1 locator candidate prints pp.193-203; the bibliography prints pp.199-203. Preserve the mismatch and leave consolidation for S3."]},
    {"candidate_id":"cand-10298","start":677,"end":677,"author":"Levey, M.","title":"Tiepolo’s ‘Empire of Flora’","details":"Burlington Magazine, 1957, pp. 89-91","kind":"journal article","related":["cand-11375","cand-10999","cand-10297"]},
    {"candidate_id":"cand-9463","start":678,"end":679,"author":"Levey, M.","title":"The modello for Tiepolo’s altarpiece at Nymphenburg","details":"Burlington Magazine, 1957, pp. 256-261","kind":"journal article","related":["cand-11375","cand-10999"],"corrections":[{"line":679,"ocr":"PP256-261","print":"pp. 256-261"}]},
    {"candidate_id":"cand-8453","start":680,"end":680,"author":"Levey, M.","title":"Tiepolo’s treatment of classical story at Villa Valmarana","details":"Journal of the Warburg and Courtauld Institutes, 1957, pp. 298-317","kind":"journal article","related":["cand-11375","cand-10999"],"corrections":[{"line":680,"ocr":"Valtnarana","print":"Valmarana"}]},
    {"candidate_id":"cand-9899","start":681,"end":681,"author":"Levey, M.","title":"A note on Marshall Schulenburg’s collection","details":"Arte Veneta, 1958, p. 221","kind":"journal article","related":["cand-11375","cand-10999"]},
    {"candidate_id":"cand-9518","start":682,"end":682,"author":"Levey, M.","title":"Wilson and Zuccarelli at Venice","details":"Burlington Magazine, 1959, pp. 139-143","kind":"journal article","related":["cand-11375","cand-10999","cand-9517"]},
    {"candidate_id":"cand-9443","start":683,"end":683,"author":"Levey, M.","title":"Francesco Zuccarelli in England","details":"Italian Studies, 1959, pp. 1-20","kind":"journal article","related":["cand-11375","cand-10999","cand-9442"]},
    {"candidate_id":"cand-8436","start":684,"end":684,"author":"Levey, M.","title":"Painting in 18th century Venice","details":"London 1959","kind":"book","related":["cand-11375","cand-10999"]},
    {"candidate_id":"cand-10302","start":685,"end":685,"author":"Levey, M.","title":"Two paintings by Tiepolo from the Algarotti Collection","details":"Burlington Magazine, 1960, pp. 250-257","kind":"journal article","related":["cand-11375","cand-10999"],"corrections":[{"line":685,"ocr":"i960","print":"1960"}]},
    {"candidate_id":"cand-11097","start":686,"end":687,"author":"Levey, M.","title":"Canaletto’s Fourteen Paintings and Visentini’s Prospectus Magni Canalis","details":"Burlington Magazine, 1962, pp. 333-341","kind":"journal article","related":["cand-11375","cand-10999"]},
    {"candidate_id":"cand-11000","start":688,"end":688,"author":"Levey, M.","title":"The later Italian pictures in the collection of Her Majesty the Queen","details":"London 1964","kind":"book","related":["cand-11375","cand-10999"]},
    {"candidate_id":"cand-11140","start":689,"end":689,"author":"Levey, M.","title":"Three slight revisions to Tiepolo scholarship","details":"Arte Veneta, 1978, pp. 418-422","kind":"journal article","related":["cand-11375","cand-10999"]},
    {"candidate_id":"cand-11374","start":691,"end":692,"author":"Levi, C. A.","title":"Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni","details":"Venezia 1900","kind":"book","related":["cand-10567","cand-10659","cand-10732"]},
    {"candidate_id":"cand-6239","start":693,"end":694,"author":"Limentani, U.","title":"Poesie e lettere inedite di Salvator Rosa","details":"Biblioteca dell’Archivum Romanicum, 1950","kind":"journal article or series monograph","related":["cand-6376"]},
    {"candidate_id":"cand-6206","start":695,"end":695,"author":"Limentani, U.","title":"La satira nel Seicento","details":"Milano-Napoli, 1961","kind":"book","related":["cand-6376","cand-6377"]},
    {"candidate_id":"cand-4842","start":696,"end":696,"author":"Litta, Pompeo","title":"Famiglie celebri italiane","details":"Milano e Torino, 1819-81","kind":"multi-volume work"},
    {"candidate_id":"cand-8324","start":697,"end":697,"author":"Livan, Lina","title":"Alcune date su Palazzo Rezzonico","details":"Rivista di Venezia, 1935, pp. 406-408","kind":"journal article","related":["cand-11376"],"corrections":[{"line":697,"ocr":"193 5","print":"1935"}]},
    {"candidate_id":"cand-9483","start":699,"end":699,"author":"Longhi, Alessandro","title":"Compendio delle vite de’ pittori veneziani istorici più rinomati del presente secolo","details":"Venezia 1762","kind":"book","related":["cand-1424"]},
]

cross_references = [
    {
        "statement_id": "st-chp21-bib-l658-699-xref-levey-haskell",
        "line": 690,
        "subject_id": "cand-11375",
        "object_id": "cand-8638",
        "target_line": 595,
        "target_segment": "chp-21:21_CHP-21Bibliography:l577-614",
        "target_status": "reviewed; bibliography-list statement present",
        "predicate": "bibliography_author_cross_reference",
        "claim": "Haskell’s bibliography directs the ‘Levey, M.’ heading to the Haskell and Levey article ‘Art exhibitions in 18th-century Venice’.",
        "note": "The target is the already reviewed p.425 bibliography record at L595. This preserves the printed See also path; the identity of M. Levey relative to person candidates from other chapters remains for S3.",
        "related": ["cand-11375", "cand-8638", "cand-10999", "cand-9442", "cand-9517", "cand-10297"],
    },
    {
        "statement_id": "st-chp21-bib-l658-699-xref-livan-gradenigo",
        "line": 698,
        "subject_id": "cand-11376",
        "object_id": "cand-11345",
        "target_line": 544,
        "target_segment": "chp-21:21_CHP-21Bibliography:l538-575",
        "target_status": "reviewed; bibliography-list statement present",
        "predicate": "bibliography_contributor_cross_reference",
        "claim": "Haskell’s bibliography directs the ‘Livan, Lina’ heading to the Gradenigo edition of Notizie d’arte, which identifies Lina Livan as editor.",
        "note": "The target is the already reviewed bibliography record at L544. The printed pointer and the edition’s named editorial role are recorded; no external identity alignment is asserted.",
        "related": ["cand-11376", "cand-11345"],
    },
]

covered_lines = {line for entry in entries for line in range(entry["start"], entry["end"] + 1)}
covered_lines.update(ref["line"] for ref in cross_references)
if covered_lines != set(range(659, 700)):
    raise SystemExit(f"bibliography line coverage incomplete: missing={sorted(set(range(659,700))-covered_lines)}")
if len(entries) != 30 or len(cross_references) != 2:
    raise SystemExit("unexpected page bibliography record count")

mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
new_statements = []
statement_ids = {row["statement_id"] for row in statements}
existing_claim_keys = {
    (
        row.get("segment_id", ""),
        " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold(),
    )
    for row in statements
    if isinstance(row.get("qualifiers"), dict)
}


def source_quote(entry):
    return "\n".join(source_lines[entry["start"] - 1:entry["end"]])


def add_mention(candidate_id, surface, note):
    positions = [index for index in range(len(segment_text)) if segment_text.startswith(surface, index)]
    if len(positions) != 1:
        raise SystemExit(f"mention span text absent or ambiguous for {candidate_id}: {surface!r}")
    position = positions[0]
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    mention_id = f"m-chp21-bib-l658-699-{len(new_mentions) + 1:03d}"
    if mention_id in mention_ids:
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    row = {field: "" for field in mention_fields}
    row.update(
        mention_id=mention_id,
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=position,
        end_char=end,
        note=note,
    )
    new_mentions.append(row)
    mention_keys.add(key)
    mention_ids.add(mention_id)


def add_statement(statement_id, claim, quote, start, end, object_id, predicate, qualifiers, subject_id=None):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    statement_ids.add(statement_id)
    existing_claim_keys.add(claim_key)
    row = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject_id,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": start,
            "source_line_end": end,
            "claim": claim,
            "speaker": "Haskell’s bibliography",
            "relation_candidate": False,
            "mentioned_candidate_ids": [subject_id] if subject_id else [object_id],
            **qualifiers,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    if not quote or quote not in "\n".join(source_lines[start - 1:end]):
        raise SystemExit(f"statement quote/line validation failed: {statement_id}")
    new_statements.append(row)


for index, entry in enumerate(entries, start=1):
    candidate_id = entry["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type bibliographic candidate: {candidate_id}")
    related = entry.get("related", [])
    for related_id in related:
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    quote = source_quote(entry)
    add_mention(
        candidate_id,
        quote,
        "S0 bibliography entry; page-image OCR readings and S3 candidate comparisons are recorded on its statement.",
    )
    qualifiers = {
        "text_layer": "bibliographic entry",
        "qualification": "This records the bibliography entry only; the cited publication was not independently consulted in this S2 pass.",
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 427,
        },
    }
    if entry.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("page_image_notes"):
        qualifiers["page_image_notes"] = entry["page_image_notes"]
    if related:
        qualifiers["related_candidate_ids_for_s3"] = related
    claim = f"Haskell lists {entry['title']} in the bibliography."
    add_statement(
        f"st-chp21-bib-l658-699-entry-{index:02d}",
        claim,
        quote,
        entry["start"],
        entry["end"],
        candidate_id,
        "bibliography_lists_publication",
        qualifiers,
    )

for ref in cross_references:
    subject_id = ref["subject_id"]
    object_id = ref["object_id"]
    if subject_id not in candidate_by_id or object_id not in candidate_by_id:
        raise SystemExit(f"cross-reference candidate FK missing: {subject_id} -> {object_id}")
    quote = source_lines[ref["line"] - 1]
    add_mention(
        subject_id,
        quote,
        "Printed bibliography See also heading; target and identity status are recorded on the statement.",
    )
    qualifiers = {
        "text_layer": "bibliography cross-reference",
        "qualification": ref["note"],
        "cross_reference_type": "see_also",
        "target_source_line": ref["target_line"],
        "target_segment_id": ref["target_segment"],
        "target_source_line_status": ref["target_status"],
        "related_candidate_ids_for_s3": ref["related"],
    }
    add_statement(
        ref["statement_id"],
        ref["claim"],
        quote,
        ref["line"],
        ref["line"],
        object_id,
        ref["predicate"],
        qualifiers,
        subject_id=subject_id,
    )

if len(new_candidates) != 8 or len(new_mentions) != 32 or len(new_statements) != 32:
    raise SystemExit("unexpected migration row counts")
if [row["candidate_id"] for row in new_candidates] != [f"cand-{i}" for i in range(11369, 11377)]:
    raise SystemExit("new candidate IDs are not the expected next sequence")

for statement in new_statements:
    if statement["object_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
    if statement.get("subject_candidate_id") and statement["subject_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"statement subject FK missing: {statement['statement_id']}")
    qualifiers = statement["qualifiers"]
    for field in ("mentioned_candidate_ids", "related_candidate_ids_for_s3"):
        for candidate_id in qualifiers.get(field, []):
            if candidate_id not in candidate_by_id:
                raise SystemExit(f"{field} FK missing: {statement['statement_id']}: {candidate_id}")

for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")
ordered_mentions = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(ordered_mentions, ordered_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L659-699"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.427 contains 30 publication records and two See also pointers; the [Page 427] marker is not a record. "
    "Reused 24 existing archive candidates and added six archive records plus two source-derived contributor candidates. "
    "The Levey 1955 citation locator pp.193-203 remains separate from the bibliography range pp.199-203; the Lavagnino page-only references also remain unresolved. "
    "Page-image OCR readings are recorded in statements; cited contents were not independently consulted."
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "candidate_updates": len(candidate_updates),
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "candidate_count_after": len(all_candidates),
    "mention_count_after": len(all_mentions),
    "statement_count_after": len(all_statements),
    "coverage_rows": len(all_coverage),
    "cross_reference_targets": {ref["statement_id"]: ref["object_id"] for ref in cross_references},
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup_path = path.with_name(path.name + BACKUP)
        if backup_path.exists():
            raise SystemExit(f"backup already exists: {backup_path}")
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
