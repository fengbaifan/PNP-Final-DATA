#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 436."""

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
SOURCE_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
SEGMENT = "chp-21:21_CHP-21Bibliography:l1059-1100"
SEGMENT_SHA = "853a8a80c67691ed8811145b13a8b3d56382dfb8846e3db52fc62392a793eec6"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l1022-1057"
BACKUP_SUFFIX = ".bak-s2-chp21-bibliography-l1059-1100-20261007"

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
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
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


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if sha256(SOURCE) != SOURCE_SHA or sha256(PDF) != PDF_SHA:
    raise SystemExit("bibliography Markdown or PDF changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1058:1100])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text/hash changed")

segment_rows = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
segment_row = segment_rows.get(SEGMENT)
if not segment_row or (
    segment_row.get("source_file"),
    segment_row.get("line_start"),
    segment_row.get("line_end"),
    segment_row.get("sha256"),
    segment_row.get("asset_sha256"),
) != (SOURCE_FILE, 1059, 1100, SEGMENT_SHA, SOURCE_SHA):
    raise SystemExit("source segment manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)

if (len(candidates), len(mentions), len(statements), len(coverage)) != (
    11408,
    26661,
    11934,
    832,
):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
coverage_row = coverage_by_id.get(SEGMENT)
if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != (
    "queued",
    "pending",
):
    raise SystemExit("bibliography segment is not queued")
previous_coverage = coverage_by_id.get(PREVIOUS_SEGMENT)
if not previous_coverage or (
    previous_coverage["disposition"],
    previous_coverage["migration_status"],
) != ("reviewed", "complete"):
    raise SystemExit("previous bibliography segment is not complete")


candidate_updates = [
    {
        "id": "cand-7579", "type": "archive",
        "expected": "Unidentified publication cited as van der Rohe, pp. 6-9 (p.204 n.2)",
        "name": "W. M. van der Rohe, ‘The marriage at Cana by Giuseppe Maria Crespi’ (Art Institute of Chicago Quarterly, 1958, pp. 6–9)",
        "detail": "Printed p.436 supplies the author form, article title, journal, year, and pages for the p.204 note 2 locator. The article and cited pages were not independently consulted; retain the printed author form without inferring identity.",
    },
    {
        "id": "cand-9908", "type": "archive",
        "expected": "Rohrlach, 1951, pages 198-200 (citation locator)",
        "name": "P. Rohrlach, ‘La collezione di quadri Streit nel Graues Kloster a Berlino’ (Arte Veneta, 1951, pp. 198–200)",
        "detail": "Printed p.436 supplies the title and full publication locator for the previously cited 1951 pages. Neither the article nor its cited pages was independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-9877", "type": "archive",
        "expected": "Romanin, volume VIII, page 53 (citation locator)",
        "name": "S. Romanin, Storia documentata di Venezia (2a edizione ristampata sull’unica pubblicata; 10 vols.; Venezia, 1912–21; original publication 1853–1861)",
        "detail": "Printed p.436 identifies the title, printed second-edition/reprint statement, original publication span, ten-volume extent, and Venezia 1912–21 reprint details for the earlier vol. VIII, p.53 locator. The cited volume and page were not independently consulted; Romanin's identity remains unresolved.",
    },
    {
        "id": "cand-4549", "type": "archive",
        "expected": "P. Romano, cited work, p. 41; identity and title unspecified",
        "name": "P. Romano, Pasquino e la satira in Roma (Roma, 1932)",
        "detail": "Printed p.436 supplies the title and place/year for the earlier page 41 citation. Page 41 and the work were not independently consulted; the author remains identified only by the printed initial and surname.",
    },
    {
        "id": "cand-11181", "type": "archive",
        "expected": "Pierre Rosenberg publication cited at p.403 note 1 (title and year unspecified)",
        "name": "Pierre Rosenberg, ‘Un tableau de Volterrano réattribué: l’Allégorie à la gloire de Louis XIV’ (Paragone, 1976, issue 317–319, pp. 167–172)",
        "detail": "The p.403 note identifies Rosenberg with the discussed Volterrano painting; printed p.436 gives the matching article title and locator. The article and cited pages were not independently consulted, so this resolves the bibliography record, not the painting's attribution.",
    },
    {
        "id": "cand-4384", "type": "archive",
        "expected": "Rosi, cited publication, pp. 347–370; full name and title unspecified",
        "name": "M. Rosi, ‘La congiura di Giacomo Centini contro Urbano VIII’ (Archivio della Società Romana di Storia Patria, 1899, pp. 347–370)",
        "detail": "Printed p.436 supplies the article title and journal locator, matching the earlier cited pages 347–370. The article and cited pages were not independently consulted; retain the author form M. Rosi.",
    },
    {
        "id": "cand-11103", "type": "archive",
        "expected": "Elizabetta Antoniazzi Rossi's article on minor genres in Schulenburg's collection",
        "name": "Elisabetta Antoniazzi Rossi, ‘Ulteriori considerazioni sull’inventario della collezione del Maresciallo von Schulenburg’ (Arte Veneta, 1977, pp. 126–134)",
        "detail": "Printed p.436 gives the full article title and locator. The article was not independently consulted. The source's bibliography spelling Elisabetta is retained here; the differently spelled author candidate derived from body text remains separate for S3.",
    },
    {
        "id": "cand-4577", "type": "archive",
        "expected": "Claude Lorrain—The Paintings (M. Röthlisberger, 1961), vol. I",
        "detail": "Printed p.436 records the two-volume Claude Lorrain—The Paintings, published by Yale and in London in 1961. This candidate remains the vol. I locator used in prior citations; the set and cited pages were not independently consulted, and M. Röthlisberger's identity remains for S3.",
    },
    {
        "id": "cand-11193", "type": "archive",
        "expected": "Rudolph, 1971 publication cited at p.404 note 10 (title unspecified)",
        "name": "Stella Rudolph, ‘Mecenati a Firenze tra Sei e Settecento: 1—I Committenti Privati; 2—Aspetti dello stile Cosimo III’ (Arte Illustrata, 1971, issue 49, pp. 228–239; 1972, issue 54, pp. 213–228)",
        "detail": "Printed p.436 supplies the title and two-part 1971/1972 journal locator for the Rudolph bibliography entry. The 1971 component may relate to the p.404 note 10 locator, but the bibliography's two-part structure does not itself establish how that entry maps to the separate 1973 citation. The articles were not independently consulted; retain S3 comparison with cand-11036 and cand-11194.",
    },
    {
        "id": "cand-11036", "type": "archive",
        "expected": "Stella Rudolph's articles on Cosimo III and Florentine provincial culture",
        "detail": "The related entry at printed p.436 lists ‘Mecenati a Firenze tra Sei e Settecento’ as two parts in Arte Illustrata (1971 and 1972), with the second on ‘Aspetti dello stile Cosimo III’. This is a bibliography match to the previously described multi-article reference, not a final resolution of the separate 1971 and 1973 footnote locators; compare with cand-11193 and cand-11194 in S3.",
    },
    {
        "id": "cand-6454", "type": "archive",
        "expected": "V. Ruffo, ‘La galleria Ruffo nel secolo XVII in Messina’, Bollettino d’Arte, X (1916)",
        "detail": "The p.436 bibliography confirms the article title, journal, volume X, and year 1916 already represented here. Prior p.160 and p.208 citation locators remain unconsulted; no article content is asserted.",
    },
    {
        "id": "cand-9840", "type": "archive",
        "expected": "Sulle consorterie delle Arti edificatorie in Venezia (Venezia, 1857)",
        "detail": "Printed p.436 confirms the title and Venezia 1857 publication details for the earlier p.329 note 2 citation. The publication and cited page were not independently consulted.",
    },
    {
        "id": "cand-4324", "type": "archive",
        "expected": "The Picture Gallery of Vincenzo Giustiniani (Salerno, 1960)",
        "detail": "Printed p.436 confirms the article title, Burlington Magazine, 1960, and three page ranges (21–27, 93–104, 135–150) for the previously tentative Salerno/year match. The article and cited pages were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-5464", "type": "archive",
        "expected": "Salvagnini, cited publication; title and date unspecified",
        "name": "F. A. Salvagnini, I pittori Borgognone-Cortese (Roma, 1937)",
        "detail": "Printed p.436 supplies the title, printed author initials, place, and year. The book and any cited passages were not independently consulted; no author identity beyond the printed form is inferred.",
    },
    {
        "id": "cand-7506", "type": "person",
        "expected": "Salvino Salvini",
        "detail": "Printed p.436 gives the author form ‘Salvino, Salvini’ for a 1782 catalogue of canons of the Florentine metropolitan church, compiled in 1751. This links the cited author form to a bibliography record only; it does not independently verify the person's identity or authorship history.",
    },
    {
        "id": "cand-7718", "type": "archive",
        "expected": "Museo di Palazzo Venezia-Catalogo, 1—I dipinti (A. Santangelo, Rome, 1947)",
        "name": "A. Santangelo, Museo di Palazzo Venezia-Catalogo, I—I dipinti (Roma, 1947)",
        "detail": "Printed p.436 confirms the catalogue title, Part I on paintings, Rome 1947, and printed author form for the existing p.222 note 5 locators. The catalogue and cited pages were not independently consulted.",
    },
    {
        "id": "cand-11137", "type": "archive",
        "expected": "Maria Santifaller's 1976 article on portraits of Francesco Algarotti",
        "name": "Maria Santifaller, ‘In margine alle ricerche tiepolesche. Un ritrattista germanico di Francesco Algarotti: Georg Friedrich Schmidt’ (Arte Veneta, 1976, pp. 204–209)",
        "detail": "Printed p.436 supplies the complete title, journal, year, and pages for the 1976 citation. The article was not independently consulted; retain its link to the printed author form for S3.",
    },
    {
        "id": "cand-11139", "type": "archive",
        "expected": "Maria Santifaller's 1977 article on etchings by Algarotti",
        "name": "Maria Santifaller, ‘Alcuni “griffonnages” su stagno di Francesco Algarotti e la grafica di Giambattista Tiepolo’ (Arte Veneta, 1977, pp. 135–144)",
        "detail": "Printed p.436 supplies the complete title, journal, year, and pages for the 1977 citation. The article was not independently consulted; retain its link to the printed author form for S3.",
    },
    {
        "id": "cand-11146", "type": "archive",
        "expected": "Maria Santifaller's 1978 article on Algarotti's tomb painting",
        "name": "Maria Santifaller, ‘Christian Bernhard Rode’s painting of Francesco Algarotti’s tomb in the Camposanto of Pisa at the beginning of neo-classicism’ (Burlington Magazine, February 1978, advertising supplement)",
        "detail": "Printed p.436 supplies the article title and Burlington Magazine's February 1978 advertising-supplement locator. The printed closing-quote placement near ‘advertising’ is preserved as a page-image note; the article was not independently consulted. Author identity remains for S3.",
    },
    {
        "id": "cand-10618", "type": "archive",
        "expected": "Catalogo de' quadri del q. Giammaria Sasso, che si mettono all'incanto nella sua casa al ponte di Cannareggio, n. 381",
        "name": "Catalogo de’ quadri del q. Giammaria Sasso, che si mettono all’incanto nella sua casa al ponte di Cannareggio, no. 381",
        "detail": "Printed p.436 confirms the sale-catalogue title and item no.381. No publication date or place is supplied on this page, so none is inferred; the catalogue was not independently consulted.",
    },
    {
        "id": "cand-10601", "type": "archive",
        "expected": "Sasso, Osservazioni sopra i lavori a niello (1856 edition cited by Cicogna)",
        "name": "G. M. Sasso, Osservazioni sopra i lavori di niello (a cura di E. Cicogna, per nozze Michieli-Segatti, Venezia, 1856)",
        "detail": "Printed p.436 supplies the title as printed, Cicogna editorial note, wedding-publication context, place, and year. It does not resolve the roles behind the printed author/editor wording; the edition was not independently consulted.",
    },
    {
        "id": "cand-7138", "type": "archive",
        "expected": "The battle scene without a hero—Aniello Falcone and his patrons (Fritz Saxl; Journal of the Warburg and Courtauld Institutes, III, 1939–40)",
        "detail": "Printed p.436 confirms the title, Journal of the Warburg and Courtauld Institutes, volume III, 1939–40, and pages 70–87 already associated with the cited publication candidate. The article and cited page were not independently consulted; match only the bibliography record.",
    },
    {
        "id": "cand-6440", "type": "archive",
        "expected": "Schlosser Magnino publication on Bellori’s critical theories (title unspecified)",
        "name": "J. Schlosser-Magnino, La letteratura artistica (seconda edizione, Firenze, 1956)",
        "detail": "Printed p.436 supplies the title, printed author form, second-edition statement, place, and year for the previously unspecified citation. The cited publication and pages were not independently consulted.",
    },
    {
        "id": "cand-7041", "type": "archive",
        "expected": "Seicento Europeo (Rome, 1956–1957)",
        "detail": "Printed p.436 describes Seicento Europeo as an exhibition organized by the Italian Ministry of Public Instruction under the auspices of the Council of Europe, Rome 1956–57. The exhibition publication and cited p.64 were not independently consulted.",
    },
    {
        "id": "cand-8804", "type": "archive",
        "expected": "Count Seilern, 1959, catalogue no.170 (citation/source locator)",
        "name": "[Seilern, Count A.], Italian paintings and drawings at 56 Princes Gate (London, 1959)",
        "detail": "Printed p.436 supplies the bracketed author form, catalogue title, location, and year. Haskell's earlier catalogue no.170 reference remains only a possible S3 comparison; this bibliography entry alone does not establish that item no.170 is the cited modello. The catalogue was not independently consulted.",
    },
]

for update in candidate_updates:
    row = candidate_by_id.get(update["id"])
    if not row or row.get("suggested_type") != update["type"]:
        raise SystemExit(f"missing/wrong-type candidate update: {update['id']}")
    if row.get("canonical_name") != update["expected"]:
        raise SystemExit(f"candidate pre-state changed: {update['id']}")
    if "name" in update:
        row["canonical_name"] = update["name"]
    row["detail"] = update["detail"]

new_candidate_specs = [
    {
        "id": "cand-11430",
        "name": "M. Röthlisberger, ‘Les pendants dans l’œuvre de Claude Lorrain’ (Gazette des Beaux-Arts, 1958, I, pp. 215–228)",
        "detail": "Bibliography entry at printed p.436. The article was not independently consulted; author identity and alignment with the existing M. Röthlisberger candidate remain for S3.",
        "source_line": 1073,
    },
    {
        "id": "cand-11431",
        "name": "Salvino, Salvini, Catàlogo cronologico de’ Canonici della chiesa metropolitana fiorentina compilato l’anno 1751 (Firenze, 1782)",
        "detail": "Bibliography entry at printed p.436. It is an undated-in-source title record beyond its printed 1782 publication details; the contents and author's identity were not independently verified.",
        "source_line": 1083,
    },
    {
        "id": "cand-11432",
        "name": "L. Schudt, Italienreisen im 17. und 18. Jahrhundert (Wien, 1959)",
        "detail": "Bibliography entry at printed p.436. The book was not independently consulted; author identity remains at the printed initial and surname.",
        "source_line": 1097,
    },
]

natural_keys = {}
for row in candidates:
    key = (row["canonical_name"].strip().casefold(), row["suggested_type"].casefold())
    natural_keys.setdefault(key, set()).add(row["candidate_id"])
new_candidates = []
for spec in new_candidate_specs:
    if spec["id"] in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {spec['id']}")
    key = (spec["name"].strip().casefold(), "archive")
    if natural_keys.get(key):
        raise SystemExit(f"candidate natural-key collision: {spec['id']}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=spec["id"],
        canonical_name=spec["name"],
        suggested_type="archive",
        status="open",
        detail=spec["detail"],
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{spec['source_line']}",
    )
    new_candidates.append(row)
    candidate_by_id[spec["id"]] = row
    natural_keys.setdefault(key, set()).add(spec["id"])


def record(candidate_id, start, end, author, title, details, kind, *, corrections=None, notes=None, related=None):
    return {
        "candidate_id": candidate_id,
        "start": start,
        "end": end,
        "author": author,
        "title": title,
        "details": details,
        "kind": kind,
        "corrections": corrections or [],
        "page_image_notes": notes or [],
        "related": related or [],
    }


entries = [
    record("cand-7579", 1060, 1061, "Rohe, W. M. van der", "‘The marriage at Cana by Giuseppe Maria Crespi’", "Art Institute of Chicago Quarterly, 1958, pp. 6–9", "journal article"),
    record("cand-9908", 1062, 1063, "Rohrlach, P.", "‘La collezione di quadri Streit nel Graues Kloster a Berlino’", "Arte Veneta, 1951, pp. 198–200", "journal article", related=["cand-9907"]),
    record("cand-9877", 1064, 1065, "Romanin, S.", "Storia documentata di Venezia", "2a edizione ristampata sull’unica pubblicata, 1853–1861, 10 vols., Venezia 1912–21", "book", corrections=[{"line": 1065, "ocr": "io vols.", "print": "10 vols.", "note": "The page image reads 10 vols.; the source OCR reads io."}], related=["cand-9890"]),
    record("cand-4549", 1066, 1066, "Romano, P.", "Pasquino e la satira in Roma", "Roma 1932", "book"),
    record("cand-11181", 1067, 1068, "Rosenberg, Pierre", "‘Un tableau de Volterrano réattribué: l’Allégorie à la gloire de Louis XIV’", "Paragone, 1976, (317–319), pp. 167–172", "journal article", corrections=[{"line": 1068, "ocr": "gioire", "print": "gloire", "note": "The page image reads ‘gloire’; the trailing OCR dash after the entry is a scan artifact, not bibliographic text."}]),
    record("cand-4384", 1069, 1070, "Rosi, M.", "‘La congiura di Giacomo Centini contro Urbano VIII’", "Archivio della Società Romana di Storia Patria, 1899, pp. 347–370", "journal article", corrections=[{"line": 1069, "ocr": "Urbano Vili", "print": "Urbano VIII", "note": "The page image reads VIII, a Roman numeral."}, {"line": 1070, "ocr": "R-omana", "print": "Romana", "note": "The hyphen in the source OCR is a line-break/scan artifact; the page image reads Romana."}]),
    record("cand-11103", 1071, 1072, "Rossi, Elisabetta Antoniazzi", "‘Ulteriori considerazioni sull’inventario della collezione del Maresciallo von Schulenburg’", "Arte Veneta, 1977, pp. 126–134", "journal article", related=["cand-11102"]),
    record("cand-11430", 1073, 1074, "Röthlisberger, M.", "‘Les pendants dans l’œuvre de Claude Lorrain’", "Gazette des Beaux-Arts, 1958, I, pp. 215–228", "journal article", corrections=[{"line": 1073, "ocr": "1’œuvre", "print": "l’œuvre", "note": "The page image reads lowercase l at the beginning of l’œuvre."}, {"line": 1074, "ocr": "1958,1", "print": "1958, I", "note": "The page image prints volume I, a Roman numeral."}], related=["cand-3502"]),
    record("cand-4577", 1075, 1075, "Röthlisberger, M.", "Claude Lorrain—The Paintings", "2 vols., Yale and London 1961", "book", notes=["The bibliography records a two-volume set; prior citations represented by this candidate specify vol. I. The page does not resolve the author's full identity."] , related=["cand-3502"]),
    record("cand-11193", 1076, 1078, "Rudolph, Stella", "‘Mecenati a Firenze tra Sei e Settecento: 1—I Committenti Privati; 2—Aspetti dello stile Cosimo III’", "Arte Illustrata, 1971 (49), pp. 228–239; 1972 (54), pp. 213–228", "two-part journal publication", notes=["The bibliography presents parts 1 and 2 under one entry across 1971 and 1972. Keep the possible relation to the p.404 1971 locator distinct from the separately cited 1973 item pending S3."], related=["cand-11035", "cand-11036", "cand-11194"]),
    record("cand-6454", 1079, 1079, "Ruffo, V.", "‘La galleria Ruffo nel secolo XVII in Messina’", "Bollettino d’Arte, X, 1916", "journal article"),
    record("cand-9840", 1080, 1080, "Sagredo, A.", "Sulle consorterie delle Arti edificatorie in Venezia", "Venezia 1857", "book"),
    record("cand-4324", 1081, 1081, "Salerno, L.", "‘The Picture Gallery of Vincenzo Giustiniani’", "Burlington Magazine, 1960, pp. 21–27, 93–104, 135–150", "journal article", corrections=[{"line": 1081, "ocr": "i960", "print": "1960", "note": "The page image reads 1960."}, {"line": 1081, "ocr": "13 5-150", "print": "135–150", "note": "The page image shows a continuous page range 135–150."}], related=["cand-4323"]),
    record("cand-5464", 1082, 1082, "Salvagnini, F. A.", "I pittori Borgognone-Cortese", "Roma 1937", "book"),
    record("cand-11431", 1083, 1083, "Salvino, Salvini", "Catàlogo cronologico de’ Canonici della chiesa metropolitana fiorentina compilato l’anno 1751", "Firenze 1782", "book/catalogue", related=["cand-7506"]),
    record("cand-7718", 1084, 1084, "Santangelo, A.", "Museo di Palazzo Venezia-Catalogo, I—I dipinti", "Roma 1947", "museum catalogue", corrections=[{"line": 1084, "ocr": "VeneZia", "print": "Venezia", "note": "The page image prints Venezia with ordinary capitalization."}, {"line": 1084, "ocr": "1—I", "print": "I—I", "note": "The page image uses Roman numeral I for the catalogue part."}]),
    record("cand-11137", 1085, 1086, "Santifaller, Maria", "‘In margine alle ricerche tiepolesche. Un ritrattista germanico di Francesco Algarotti: Georg Friedrich Schmidt’", "Arte Veneta, 1976, pp. 204–209", "journal article", related=["cand-11134"]),
    record("cand-11139", 1087, 1088, "Santifaller, Maria", "‘Alcuni “griffonnages” su stagno di Francesco Algarotti e la grafica di Giambattista Tiepolo’", "Arte Veneta, 1977, pp. 135–144", "journal article", related=["cand-11134"]),
    record("cand-11146", 1089, 1091, "Santifaller, Maria", "‘Christian Bernhard Rode’s painting of Francesco Algarotti’s tomb in the Camposanto of Pisa at the beginning of neo-classicism’", "Burlington Magazine, Feb. 1978, advertising supplement", "journal article", notes=["The printed closing quotation mark appears after ‘advertising’ in the phrase ‘advertising’ supplement; the supplement descriptor is recorded as publication detail, not as part of the article title."], related=["cand-11134"]),
    record("cand-10618", 1092, 1092, "Sasso, G. M.", "Catalogo de’ quadri del q. Giammaria Sasso, che si mettono all’incanto nella sua casa al ponte di Cannareggio, n. 381", "No date or place printed; catalogue no. 381", "sale catalogue", notes=["The printed abbreviation q. is retained. No publication year is supplied in the entry; none is inferred."]),
    record("cand-10601", 1093, 1093, "Sasso, G. M.", "Osservazioni sopra i lavori di niello", "a cura di E. Cicogna, per nozze Michieli-Segatti, Venezia 1856", "book", corrections=[{"line": 1093, "ocr": "MichieliSegatti", "print": "Michieli-Segatti", "note": "The page image shows a line-end hyphen after Michieli and the continuation Segatti on the next line."}]),
    record("cand-7138", 1094, 1095, "Saxl, F.", "‘The battle scene without a hero—Aniello Falcone and his patrons’", "Journal of the Warburg and Courtauld Institutes, III, 1939–40, pp. 70–87", "journal article", corrections=[{"line": 1095, "ocr": "19 3 9-40", "print": "1939–40", "note": "The page image reads 1939–40."}, {"line": 1095, "ocr": "70-8 7", "print": "70–87", "note": "The page image reads 70–87."}], related=["cand-6153"]),
    record("cand-6440", 1096, 1096, "Schlosser-Magnino, J.", "La letteratura artistica", "seconda edizione, Firenze 1956", "book"),
    record("cand-11432", 1097, 1097, "Schudt, L.", "Italienreisen im 17. und 18. Jahrhundert", "Wien 1959", "book"),
    record("cand-7041", 1098, 1099, "Seicento Europeo", "Seicento Europeo", "Exhibition organized by the Italian Ministry of Public Instruction under the auspices of the Council of Europe, Roma 1956–7", "exhibition catalogue", corrections=[{"line": 1098, "ocr": "P.L", "print": "P.I.", "note": "The page image shows the abbreviation P.I.; OCR reads P.L."}], notes=["P.I. is retained as the printed abbreviation; its expansion is given as Ministry of Public Instruction to identify the stated organizer, without treating the exhibition notice as a historical event claim."]),
    record("cand-8804", 1100, 1100, "[Seilern, Count A.]", "Italian paintings and drawings at 56 Princes Gate", "London 1959", "catalogue", notes=["Square brackets around the author heading are present in the printed entry. Do not infer that catalogue no.170 in an earlier citation is this exact item without S3 comparison."], related=["cand-8805"]),
]

if len(candidate_updates) != 25 or len(new_candidates) != 3 or len(entries) != 26:
    raise SystemExit("unexpected candidate or publication counts")

mention_ids = {row["mention_id"] for row in mentions}
mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
statement_ids = {row["statement_id"] for row in statements}
existing_claim_keys = {
    (
        row.get("segment_id", ""),
        " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold(),
    )
    for row in statements
    if isinstance(row.get("qualifiers"), dict)
}
new_mentions = []
new_statements = []
covered_lines = set()


def source_quote(item):
    return "\n".join(source_lines[item["start"] - 1 : item["end"]])


for index, item in enumerate(entries, start=1):
    candidate_id = item["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {candidate_id}")
    for related_id in item["related"]:
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    line_span = set(range(item["start"], item["end"] + 1))
    if covered_lines & line_span:
        raise SystemExit(f"overlapping publication line range: {candidate_id}")
    covered_lines |= line_span

    quote = source_quote(item)
    positions = [i for i in range(len(segment_text)) if segment_text.startswith(quote, i)]
    if len(positions) != 1:
        raise SystemExit(f"source quote must occur once: {candidate_id}")
    start_char = positions[0]
    end_char = start_char + len(quote)
    mention_id = f"m-chp21-bib-l1059-1100-{index:03d}"
    if mention_id in mention_ids:
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    mention_key = (SEGMENT, candidate_id, str(start_char), str(end_char))
    if mention_key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {mention_id}")
    mention_row = {field: "" for field in mention_fields}
    mention_row.update(
        mention_id=mention_id,
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=quote,
        start_char=start_char,
        end_char=end_char,
        note="S0 bibliography entry; page-image readings and S3 comparisons are recorded on its statement.",
    )
    new_mentions.append(mention_row)
    mention_ids.add(mention_id)
    mention_keys.add(mention_key)

    statement_id = f"st-chp21-bib-l1059-1100-entry-{index:02d}"
    if statement_id in statement_ids:
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    claim = f"Haskell lists {item['title']} in the bibliography."
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    statement_ids.add(statement_id)
    existing_claim_keys.add(claim_key)
    qualifiers = {
        "source_line_start": item["start"],
        "source_line_end": item["end"],
        "claim": claim,
        "speaker": "Haskell’s bibliography",
        "relation_candidate": False,
        "mentioned_candidate_ids": [candidate_id],
        "text_layer": "bibliographic entry",
        "qualification": "This records the bibliography entry only; the cited publication was not independently consulted in this S2 pass.",
        "bibliographic_record": {
            "author_as_printed": item["author"],
            "title_as_printed": item["title"],
            "publication_details_as_printed": item["details"],
            "record_kind": item["kind"],
            "printed_page": 436,
        },
    }
    if item["corrections"]:
        qualifiers["page_image_ocr_corrections"] = item["corrections"]
    if item["page_image_notes"]:
        qualifiers["page_image_notes"] = item["page_image_notes"]
    if item["related"]:
        qualifiers["related_candidate_ids_for_s3"] = item["related"]
    new_statements.append(
        {
            "statement_id": statement_id,
            "segment_id": SEGMENT,
            "subject_candidate_id": None,
            "object_candidate_id": candidate_id,
            "predicate": "bibliography_lists_publication",
            "qualifiers": qualifiers,
            "original_quote": quote,
            "origin": "book",
            "source_file": SOURCE_FILE,
        }
    )

if covered_lines != set(range(1060, 1101)):
    raise SystemExit(f"bibliography lines not covered exactly: {sorted(set(range(1060, 1101)) - covered_lines)}")
if len(new_mentions) != 26 or len(new_statements) != 26:
    raise SystemExit("unexpected mention/statement counts")

for statement in new_statements:
    for field in ("subject_candidate_id", "object_candidate_id"):
        candidate_id = statement.get(field)
        if candidate_id is not None and candidate_id not in candidate_by_id:
            raise SystemExit(f"statement FK missing: {statement['statement_id']} {field}={candidate_id}")
    for field in ("mentioned_candidate_ids", "related_candidate_ids_for_s3"):
        for candidate_id in statement["qualifiers"].get(field, []):
            if candidate_id not in candidate_by_id:
                raise SystemExit(f"{field} FK missing: {statement['statement_id']}: {candidate_id}")
    if statement["original_quote"] not in segment_text:
        raise SystemExit(f"statement quote outside source segment: {statement['statement_id']}")

coverage_row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1060-1100",
    note="Printed p.436: 26 publication records reviewed; see process/stages.md.",
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
after = {
    "candidate_count": len(all_candidates),
    "mention_count": len(all_mentions),
    "statement_count": len(all_statements),
    "coverage_complete": sum(row["disposition"] == "reviewed" for row in coverage),
    "coverage_queued": sum(row["disposition"] == "queued" for row in coverage),
    "coverage_excluded": sum(row["disposition"] == "excluded" for row in coverage),
}
expected_after = {
    "candidate_count": 11411,
    "mention_count": 26687,
    "statement_count": 11960,
    "coverage_complete": 611,
    "coverage_queued": 100,
    "coverage_excluded": 121,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "candidate_updates": len(candidate_updates),
    "new_archive_candidates": len(new_candidates),
    "publication_entries": len(entries),
    "new_mentions": len(new_mentions),
    "publication_statements": len(new_statements),
    **after,
}

if ARGS.apply:
    table_paths = (candidate_path, mention_path, statement_path, coverage_path)
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in table_paths]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("a migration backup already exists; refusing to overwrite it")
    for path, backup_path in zip(table_paths, backup_paths):
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

print(json.dumps(result, ensure_ascii=False, indent=2))
