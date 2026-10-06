#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 431."""

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
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT = "chp-21:21_CHP-21Bibliography:l846-881"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "452e318c5db9d0281edb596dd0af17224ccd515db43cf082daf86a0adc35fb08"
BACKUP = ".bak-s2-chp21-bibliography-l846-881-20261007"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l808-844"
PREVIOUS_XREF = "st-chp21-bib-l808-844-xref-molinier-muntz"

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
segment_text = "\n".join(source_lines[845:881])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text/hash changed")
segment_rows = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
segment_row = segment_rows.get(SEGMENT)
if not segment_row or (
    segment_row.get("source_file"),
    segment_row.get("line_start"),
    segment_row.get("line_end"),
    segment_row.get("sha256"),
    segment_row.get("asset_sha256"),
) != (
    "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    846,
    881,
    SEGMENT_SHA,
    SOURCE_SHA,
):
    raise SystemExit("source segment manifest changed")
previous_segment_row = segment_rows.get(PREVIOUS_SEGMENT)
if not previous_segment_row or not (
    previous_segment_row["line_start"] <= 820 <= previous_segment_row["line_end"]
):
    raise SystemExit("Molinier cross-reference source segment changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)

if (len(candidates), len(mentions), len(statements), len(coverage)) != (
    11384,
    26515,
    11788,
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
        "id": "cand-4828",
        "expected": "Müntz and Molinier (1885), cited publication; title unspecified",
        "name": "E. Müntz and Em. Molinier, ‘Le château de Fontainebleau au XVII siècle d’après des documents inédits’ (Mémoires de la Société de l’Histoire de Paris et de l’Île-de-France, XII, 1885, pp. 255–358)",
        "detail": "The page-431 bibliography entry identifies the title, journal, volume and page range for this existing citation. The article was not independently consulted.",
    },
    {
        "id": "cand-5650",
        "expected": "Naudaeana et Patiniana (Amsterdam, 1703), p.29",
        "name": "Naudaeana et Patiniana, ou Singularitez remarquables prises des conversations de Mess. Naudé et Patin (seconde édition revue, Amsterdam, 1703)",
        "detail": "Printed p.431 supplies the full title and edition form for the existing p.29 locator. The cited passage and volume were not independently consulted.",
    },
    {
        "id": "cand-6008",
        "expected": "de Nolhac, cited publication p. 25; title and year unspecified",
        "name": "P. de Nolhac, Le Virgile du Vatican et ses peintures (Paris, 1897)",
        "detail": "Printed p.431 identifies the title and publication data for the existing p.25 locator. The cited passage and book were not independently consulted.",
    },
    {
        "id": "cand-6095",
        "expected": "Letters from Ludovico Carracci to Ferrante Carlo, published by Nicodemi (1935)",
        "name": "G. Nicodemi, ‘Otto lettere di Ludovico Carracci a Don Ferrante Carlo’ (Aevum, 1935, pp. 305–313)",
        "detail": "Printed p.431 supplies the article title, journal and pages for the existing Nicodemi publication reference. The article was not independently consulted.",
    },
    {
        "id": "cand-6198",
        "expected": "Neri (1883), cited publication",
        "name": "A. Neri, Costumanze e sollazzi—aneddoti romani nel pontificato di Alessandro VII (Genova, 1883)",
        "detail": "Printed p.431 identifies the title and edition for this existing Neri citation. The cited publication was not independently consulted.",
    },
    {
        "id": "cand-7696",
        "expected": "Dizionario di erudizione stòrico-ecclesiastica da San Pietro sino ai nostri giorni (G. Moroni; cited vol. 69)",
        "name": "G. Moroni, Dizionario di erudizione storico-ecclesiastica da San Pietro sino ai nostri giorni (109 vols., Venezia, 1840–1879)",
        "detail": "Printed p.431 supplies the 109-volume extent and publication dates for this dictionary; the OCR segment omits that continuation. Existing volume locators remain in their statements; the dictionary was not independently consulted.",
    },
    {
        "id": "cand-8328",
        "expected": "Novelli publication, page 62, cited on p.254 note 4",
        "name": "Pietro Antonio Novelli, Memorie della vita—per le auspicate nozze del Marchese Giovanni Selvatico colla contessa Laura Contarini (Padova, 1834)",
        "detail": "Printed p.431 identifies a Novelli publication that may match the existing p.62 locator. Keep the separately worded Novelli citation cand-8363 linked for S3 comparison; the book was not independently consulted.",
    },
    {
        "id": "cand-8329",
        "expected": "Muraro article in Gazette des Beaux Arts, 1960, pages 19-34",
        "name": "M. Muraro, ‘L’Olympe de Tiepolo’ (Gazette des Beaux-Arts, 1960, I, pp. 19–34)",
        "detail": "Printed p.431 supplies the article title, issue and pages for this existing 1960 locator. The article was not independently consulted.",
    },
    {
        "id": "cand-8332",
        "expected": "G. A. Moschini 1806, volume II, page 105, cited on p.254 note 7",
        "name": "G. A. Moschini, Della letteratura veneziana nel secolo XVIII fino a’ nostri giorni (4 vols., Venezia, 1806)",
        "detail": "Printed p.431 reads Moschini, correcting the OCR author form Meschini, and identifies this four-volume work. Other 1806 volume/page locators with Moschini/Meschini forms remain separate for S3 comparison; the book was not independently consulted.",
    },
    {
        "id": "cand-8506",
        "expected": "G. A. Moschini, 1808, page 139 (citation locator)",
        "name": "G. A. Moschini, Della vita e delle opere del pittore Jacopo Guaranà Veneziano e di altri veneti antichi pittori (Venezia, 1808)",
        "detail": "Printed p.431 supplies the title for the existing 1808 locator. The cited page and book were not independently consulted.",
    },
    {
        "id": "cand-8536",
        "expected": "Muraro, Emporium, 1960, pages 195-218 (citation locator)",
        "name": "M. Muraro, ‘Giuseppe Zais e un “giovin signore” nelle pitture murali di Stra’ (Emporium, 1960, pp. 195–218)",
        "detail": "Printed p.431 supplies the title for the existing 1960 Emporium locator. The article was not independently consulted.",
    },
    {
        "id": "cand-8643",
        "expected": "V. Moschini, 1956, p.12 (citation locator; title pending bibliography review)",
        "name": "V. Moschini, Pietro Longhi (Milano, 1956)",
        "detail": "Printed p.431 supplies the title and publication data for the existing p.12 locator. The cited page and book were not independently consulted.",
    },
    {
        "id": "cand-9284",
        "expected": "Nisser, 1937 (citation locator; title and page not supplied)",
        "name": "W. Nisser, ‘Lord Manchester’s Reception at Venice’ (Burlington Magazine, 1937, vol. 70, pp. 30–34)",
        "detail": "Printed p.431 supplies the title, periodical and pages for the existing 1937 locator. The article was not independently consulted.",
    },
    {
        "id": "cand-9295",
        "expected": "V. Moschini, 1954, p.29 (citation locator; title unresolved)",
        "name": "V. Moschini, Canaletto (Milano, 1954)",
        "detail": "Printed p.431 supplies the title for the existing p.29 locator. The cited page and book were not independently consulted.",
    },
    {
        "id": "cand-9561",
        "expected": "G. A. Moschini, 1924 citation at p.82 (title unresolved)",
        "name": "G. A. Moschini, Dell’Incisione in Venezia (published by the Regia Accademia di Belle Arti di Venezia, 1924)",
        "detail": "Printed p.431 supplies the title and issuing institution for the existing 1924 locator. Other 1924 page locators remain linked for S3 comparison; the publication was not independently consulted.",
    },
    {
        "id": "cand-9924",
        "expected": "Natali, page 5 (citation locator)",
        "name": "G. Natali, Storia letteraria d’Italia—Il Settecento (Milano, 1929)",
        "detail": "Printed p.431 supplies the title and publication data for the existing p.5 locator. The cited page and book were not independently consulted.",
    },
    {
        "id": "cand-9958",
        "expected": "G. A. Moschini, 1815, volume I, page 48 (citation locator)",
        "name": "G. A. Moschini, Guida per la Città di Venezia (Venezia, 1815)",
        "detail": "Printed p.431 supplies the title for the existing volume-I locator. A separate p.xv citation remains linked for S3 comparison; the book was not independently consulted.",
    },
    {
        "id": "cand-10156",
        "expected": "G. A. Moschini, 1809, p. 5 (p.336 note 4 citation locator)",
        "name": "G. A. Moschini, Sulla vita e sulle opere di Pietro Brandolese (Venezia, 1809)",
        "detail": "Printed p.431 supplies the title for the existing 1809 locator. The cited page and book were not independently consulted.",
    },
    {
        "id": "cand-10183",
        "expected": "Neri, 1899, pp.109 and 114 (work title unspecified in p.339 note 2)",
        "name": "A. Neri, ‘Giuseppe Baretti e i Gesuiti’ (Giornale Storico della Letteratura Italiana, 1899, Supplemento No. 2, pp. 106–129)",
        "detail": "Printed p.431 identifies the publication matching the existing 1899 locator. The cited pages and article were not independently consulted.",
    },
    {
        "id": "cand-10359",
        "expected": "A. Neri, 1885 (publication cited for the Curli letter; p.357 n.1)",
        "name": "A. Neri, ‘Una lettera inedita di Francesco Algarotti’ (Giornale Linguistico, 1885, pp. 296–299)",
        "detail": "Printed p.431 supplies the title, periodical and pages for the existing 1885 citation. The article was not independently consulted.",
    },
    {
        "id": "cand-10425",
        "expected": "G. A. Moschini, 1810 citation in p.361 note 1",
        "name": "G. A. Moschini, Memorie sulla vita del pittore Bernardino Castelli (Venezia, 1810)",
        "detail": "Printed p.431 supplies the title for the existing 1810 citation. The cited account and book were not independently consulted.",
    },
    {
        "id": "cand-10479",
        "expected": "Neu-Mayr, 1807, figures and inscriptions of Prà della Valle (p.365 note 2 citation locator)",
        "name": "A. Neu-Mayr, Illustrazione del Prato della Valle ossia della Piazza delle Statue di Padova (Padova, 1807)",
        "detail": "Printed p.431 supplies the title and author initial for the existing 1807 locator. The book was not independently consulted.",
    },
    {
        "id": "cand-11188",
        "expected": "Muraro, 1965 publication cited at p.404 note 3 (title unspecified)",
        "name": "M. Muraro, ‘Studiosi, collezionisti e opere d’arte veneta dalle lettere al Cardinale Leopoldo de’ Medici’ (Saggi e Memorie di storia dell’arte, 4, 1965, Venezia, pp. 65–83)",
        "detail": "Printed p.431 supplies the title and publication details for the existing 1965 locator. The article was not independently consulted.",
    },
]

for update in candidate_updates:
    row = candidate_by_id.get(update["id"])
    if not row or row.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type candidate update: {update['id']}")
    if row["canonical_name"] != update["expected"]:
        raise SystemExit(f"candidate pre-state changed: {update['id']}")
    row["canonical_name"] = update["name"]
    row["detail"] = update["detail"]

person = candidate_by_id.get("cand-11401")
if not person or person.get("suggested_type") != "person":
    raise SystemExit("Molinier bibliography-heading candidate missing or wrong type")
if person.get("detail") != (
    "Source-derived person candidate for the printed bibliography heading and its See pointer "
    "to the Müntz et Molinier entry. Full personal identity remains unresolved."
):
    raise SystemExit("Molinier candidate pre-state changed")
person["detail"] = (
    "The p.431 entry confirms the printed coauthor form Em. Molinier named by the p.430 "
    "cross-reference. Personal identity remains unresolved."
)

new_candidate_specs = [
    (
        "cand-11406",
        "E. Morpurgo, Marco Foscarini e Venezia nel secolo XVIII (Firenze, 1880)",
        "Bibliography entry at printed p.431. The book was not independently consulted.",
        848,
    ),
    (
        "cand-11407",
        "E. Müntz, Les Archives des Arts—recueil de documents inédits ou peu connus, première série (Paris, 1890)",
        "Bibliography entry at printed p.431. Keep distinct from other publications attributed to Müntz; the book was not independently consulted.",
        859,
    ),
    (
        "cand-11408",
        "E. Narducci, ‘Artisti dimoranti in Roma nel rione di Campo Marzio l’anno 1656’ (Il Buonarotti, 1870, pp. 122–126)",
        "Bibliography entry at printed p.431. The article was not independently consulted.",
        865,
    ),
    (
        "cand-11409",
        "F. Noack, Das Deutschtum in Rom (Berlin und Leipzig, 1927)",
        "Bibliography entry at printed p.431. The book was not independently consulted.",
        877,
    ),
]

natural_keys = {}
for row in candidates:
    key = (row["canonical_name"].strip().casefold(), row["suggested_type"].casefold())
    natural_keys.setdefault(key, set()).add(row["candidate_id"])
new_candidates = []
for candidate_id, canonical_name, detail, source_line in new_candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (canonical_name.strip().casefold(), "archive")
    if natural_keys.get(key):
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {canonical_name}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=canonical_name,
        suggested_type="archive",
        status="open",
        detail=detail,
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{source_line}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.setdefault(key, set()).add(candidate_id)

entry_specs = [
    ("cand-7696", 847, 847, "Moroni, G.", "Dizionario di erudizione storico-ecclesiastica da San Pietro sino ai nostri giorni", "109 vols., Venezia 1840–79", "109-volume reference dictionary", {"related": ["cand-5955", "cand-6388"], "page_image_notes": ["The page image continues the entry with “109 vols., Venezia 1840–79”; this continuation is absent from the OCR segment."]}),
    ("cand-11406", 848, 848, "Morpurgo, E.", "Marco Foscarini e Venezia nel secolo XVIII", "Firenze 1880", "book", {}),
    ("cand-8332", 849, 850, "Moschini, G. A.", "Della letteratura veneziana nel secolo XVIII fino a’ nostri giorni", "4 vols., Venezia 1806", "four-volume book set", {"related": ["cand-8547", "cand-8583", "cand-8511", "cand-10187", "cand-10568", "cand-10681", "cand-10700", "cand-10809", "cand-10829"], "corrections": [{"line": 849, "ocr": "Meschini, G. A.", "print": "Moschini, G. A.", "note": "The page image clearly reads Moschini; preserve the separate Meschini-form citation candidates for S3 comparison."}]}),
    ("cand-8506", 851, 851, "Moschini, G. A.", "Della vita e delle opere del pittore Jacopo Guaranà Veneziano e di altri veneti antichi pittori", "Venezia 1808", "book", {}),
    ("cand-10156", 852, 852, "Moschini, G. A.", "Sulla vita e sulle opere di Pietro Brandolese", "Venezia 1809", "book", {}),
    ("cand-10425", 853, 853, "Moschini, G. A.", "Memorie sulla vita del pittore Bernardino Castelli", "Venezia 1810", "book", {"corrections": [{"line": 853, "ocr": "1810.,", "print": "1810.", "note": "The page image has a terminal period but no comma."}], "related": ["cand-10701"]}),
    ("cand-9958", 854, 854, "Moschini, G. A.", "Guida per la Città di Venezia", "Venezia 1815", "book", {"related": ["cand-10159"]}),
    ("cand-9561", 855, 856, "Moschini, G. A.", "Dell’Incisione in Venezia", "Published by the Regia Accademia di Belle Arti di Venezia, Venezia 1924", "institutionally issued book", {"related": ["cand-9821", "cand-9886", "cand-10191", "cand-10220", "cand-10587"], "corrections": [{"line": 855, "ocr": "Venezia-—pubblicata", "print": "Venezia—pubblicata", "note": "The page image has an em dash without the preceding OCR hyphen."}]}),
    ("cand-9295", 857, 857, "Moschini, V.", "Canaletto", "Milano 1954", "book", {}),
    ("cand-8643", 858, 858, "Moschini, V.", "Pietro Longhi", "Milano 1956", "book", {}),
    ("cand-11407", 859, 860, "Müntz, E.", "Les Archives des Arts—recueil de documents inédits ou peu connus", "Première série, Paris 1890", "first-series publication", {"corrections": [{"line": 859, "ocr": "première serie", "print": "première série", "note": "The page image includes the acute accent in série."}]}),
    ("cand-4828", 861, 861, "Müntz, E. et Molinier, Em.", "Le château de Fontainebleau au XVII siècle d’après des documents inédits", "Mémoires de la Société de l’Histoire de Paris et de l’Île-de-France, XII, 1885, pp. 255–358", "journal article", {"corrections": [{"line": 861, "ocr": "XVII siede", "print": "XVII siècle", "note": "The page image reads siècle."}, {"line": 861, "ocr": "1’Ile-de-France", "print": "l’Ile-de-France", "note": "The page image reads a lowercase l, not the numeral 1."}, {"line": 861, "ocr": "pp. 255358", "print": "pp. 255–358", "note": "The page image shows the omitted range separator."}]}),
    ("cand-8329", 862, 862, "Muraro, M.", "L’Olympe de Tiepolo", "Gazette des Beaux-Arts, 1960, I, pp. 19–34", "journal article", {"corrections": [{"line": 862, "ocr": "i960,1", "print": "1960, I", "note": "The page image reads 1960, volume I."}]}),
    ("cand-8536", 863, 863, "Muraro, M.", "Giuseppe Zais e un “giovin signore” nelle pitture murali di Stra", "Emporium, 1960, pp. 195–218", "journal article", {"corrections": [{"line": 863, "ocr": "i960", "print": "1960", "note": "The page image reads 1960."}]}),
    ("cand-11188", 864, 864, "Muraro, M.", "Studiosi, collezionisti e opere d’arte veneta dalle lettere al Cardinale Leopoldo de’ Medici", "Saggi e Memorie di storia dell’arte, 4, 1965, Venezia, pp. 65–83", "journal article", {}),
    ("cand-11408", 865, 866, "Narducci, E.", "Artisti dimoranti in Roma nel rione di Campo Marzio l’anno 1656", "Il Buonarotti, 1870, pp. 122–126", "journal article", {"corrections": [{"line": 865, "ocr": "II Buonarotti", "print": "Il Buonarotti", "note": "The page image reads capital I followed by lowercase l."}]}),
    ("cand-9924", 867, 867, "Natali, G.", "Storia letteraria d’Italia—Il Settecento", "Milano 1929", "book", {}),
    ("cand-5650", 868, 868, "", "Naudaeana et Patiniana ou Singularitez remarquables prises des conversations de Mess. Naudé et Patin", "Seconde édition revue, Amsterdam 1703", "revised second edition", {}),
    ("cand-6198", 869, 870, "Neri, A.", "Costumanze e sollazzi—aneddoti romani nel pontificato di Alessandro VII", "Genova 1883", "book", {}),
    ("cand-10359", 871, 871, "N[eri], A.", "Una lettera inedita di Francesco Algarotti", "Giornale Linguistico, 1885, pp. 296–299", "journal article", {}),
    ("cand-10183", 872, 873, "Neri, A.", "Giuseppe Baretti e i Gesuiti", "Giornale Storico della Letteratura Italiana, 1899, Supplemento No. 2, pp. 106–129", "journal article", {}),
    ("cand-10479", 874, 875, "Neu-Mayr, A.", "Illustrazione del Prato della Valle ossia della Piazza delle Statue di Padova", "Padova 1807", "book", {"page_image_notes": ["The printed continuation at L875 begins with a short dash before Padova; it is retained as punctuation, not treated as a separate record."]}),
    ("cand-6095", 876, 876, "Nicodemi, G.", "Otto lettere di Ludovico Carracci a Don Ferrante Carlo", "Aevum, 1935, pp. 305–313", "journal article", {"corrections": [{"line": 876, "ocr": "pp. 305-313Nisser", "print": "pp. 305–313.\\nNisser", "note": "The page image separates the Nicodemi entry from the following Nisser entry."}]}),
    ("cand-9284", 876, 876, "Nisser, W.", "Lord Manchester’s Reception at Venice", "Burlington Magazine, 1937, vol. 70, pp. 30–34", "journal article", {"corrections": [{"line": 876, "ocr": "Manchesters Reception", "print": "Manchester’s Reception", "note": "The page image includes the possessive apostrophe."}, {"line": 876, "ocr": "voi. 70", "print": "vol. 70", "note": "The page image reads vol. 70."}]}),
    ("cand-11409", 877, 877, "Noack, F.", "Das Deutschtum in Rom", "Berlin und Leipzig 1927", "book", {"corrections": [{"line": 877, "ocr": "Leipzig .1927", "print": "Leipzig 1927", "note": "The page image has no period before the date."}]}),
    ("cand-6008", 878, 878, "Nolhac, P. de", "Le Virgile du Vatican et ses peintures", "Paris 1897", "book", {"corrections": [{"line": 878, "ocr": "Valican", "print": "Vatican", "note": "The page image reads Vatican."}]}),
    ("cand-10216", 879, 879, "Northall, John", "Travels through Italy", "London 1767", "book", {}),
    ("cand-8328", 880, 881, "Novelli, Pietro Antonio", "Memorie della vita—per le auspicate nozze del Marchese Giovanni Selvatico colla contessa Laura Contarini", "Padova 1834", "book", {"related": ["cand-8363"]}),
]

line_mixed = source_lines[875]
split_marker = "Nisser, W.:"
if split_marker not in line_mixed:
    raise SystemExit("Nicodemi/Nisser source boundary changed at L876")
nicodemi_quote, nisser_tail = line_mixed.split(split_marker, 1)
if "305-313" not in nicodemi_quote or "Burlington Magazine" not in nisser_tail:
    raise SystemExit("unexpected Nicodemi/Nisser bibliography boundary")
entries = []
for candidate_id, start, end, author, title, details, kind, extra in entry_specs:
    row = {
        "candidate_id": candidate_id,
        "start": start,
        "end": end,
        "author": author,
        "title": title,
        "details": details,
        "kind": kind,
    }
    row.update(extra)
    entries.append(row)
entries[22]["quote"] = nicodemi_quote.rstrip()
entries[23]["quote"] = split_marker + nisser_tail

xref = next((row for row in statements if row.get("statement_id") == PREVIOUS_XREF), None)
if not xref or xref.get("predicate") != "bibliography_author_cross_reference":
    raise SystemExit("previous Molinier cross-reference statement missing")
xref_qualifiers = xref.get("qualifiers") or {}
if (
    xref.get("object_candidate_id") != "cand-4828"
    or xref_qualifiers.get("target_source_line") != 861
    or xref_qualifiers.get("target_source_line_status")
    != "queued; target entry not yet reviewed"
):
    raise SystemExit("previous Molinier cross-reference state changed")

new_mentions = []
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
new_statements = []


def source_quote(entry):
    return entry.get("quote") or "\n".join(source_lines[entry["start"] - 1 : entry["end"]])


def add_mention(candidate_id, surface):
    positions = [index for index in range(len(segment_text)) if segment_text.startswith(surface, index)]
    if len(positions) != 1:
        raise SystemExit(f"mention surface must occur once in segment: {candidate_id} {surface!r}")
    position = positions[0]
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    mention_id = f"m-chp21-bib-l846-881-{len(new_mentions) + 1:03d}"
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
        note="S0 bibliography entry; page-image readings and S3 comparisons are recorded on its statement.",
    )
    new_mentions.append(row)
    mention_keys.add(key)
    mention_ids.add(mention_id)


def add_publication_statement(statement_id, entry, candidate_id):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim = f"Haskell lists {entry['title']} in the bibliography."
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    statement_ids.add(statement_id)
    existing_claim_keys.add(claim_key)
    qualifiers = {
        "source_line_start": entry["start"],
        "source_line_end": entry["end"],
        "claim": claim,
        "speaker": "Haskell’s bibliography",
        "relation_candidate": False,
        "mentioned_candidate_ids": [candidate_id],
        "text_layer": "bibliographic entry",
        "qualification": "This records the bibliography entry only; the cited publication was not independently consulted in this S2 pass.",
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 431,
        },
    }
    if entry.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("page_image_notes"):
        qualifiers["page_image_notes"] = entry["page_image_notes"]
    if entry.get("related"):
        qualifiers["related_candidate_ids_for_s3"] = entry["related"]
    quote = source_quote(entry)
    excerpt = "\n".join(source_lines[entry["start"] - 1 : entry["end"]])
    if not quote or quote not in excerpt:
        raise SystemExit(f"statement quote/line validation failed: {statement_id}")
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
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        }
    )


for index, entry in enumerate(entries, start=1):
    candidate_id = entry["candidate_id"]
    if candidate_id not in candidate_by_id or candidate_by_id[candidate_id].get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type bibliographic candidate: {candidate_id}")
    for related_id in entry.get("related", []):
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    quote = source_quote(entry)
    if quote not in "\n".join(source_lines[entry["start"] - 1 : entry["end"]]):
        raise SystemExit(f"entry quote is outside source lines: {candidate_id}")
    add_mention(candidate_id, quote)
    add_publication_statement(
        f"st-chp21-bib-l846-881-entry-{index:02d}", entry, candidate_id
    )

if len(entries) != 28 or len(new_candidates) != 4 or len(candidate_updates) != 23 or len(new_mentions) != 28 or len(new_statements) != 28:
    raise SystemExit(
        f"unexpected migration row counts: publications={len(entries)}, "
        f"new_candidates={len(new_candidates)}, candidate_updates={len(candidate_updates)}, "
        f"mentions={len(new_mentions)}, statements={len(new_statements)}"
    )

for statement in new_statements:
    for field in ("object_candidate_id", "subject_candidate_id"):
        candidate_id = statement.get(field)
        if candidate_id is not None and candidate_id not in candidate_by_id:
            raise SystemExit(f"statement FK missing: {statement['statement_id']} {field}={candidate_id}")
    qualifiers = statement["qualifiers"]
    for field in ("mentioned_candidate_ids", "related_candidate_ids_for_s3"):
        for candidate_id in qualifiers.get(field, []):
            if candidate_id not in candidate_by_id:
                raise SystemExit(f"{field} FK missing: {statement['statement_id']}: {candidate_id}")
    start = qualifiers["source_line_start"]
    end = qualifiers["source_line_end"]
    excerpt = "\n".join(source_lines[start - 1 : end])
    if statement["original_quote"] not in excerpt:
        raise SystemExit(f"statement quote/line validation failed: {statement['statement_id']}")

for row in new_mentions:
    if segment_text[int(row["start_char"]) : int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")
ordered_mentions = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(ordered_mentions, ordered_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")

xref_qualifiers["qualification"] = (
    "The reviewed L861 entry names Müntz and Molinier in the 1885 article, confirming this "
    "bibliography pointer. The personal identity of Molinier remains unresolved."
)
xref_qualifiers["target_source_line_status"] = "reviewed; L861 confirms the target entry"
xref["qualifiers"] = xref_qualifiers

coverage_row["disposition"] = "reviewed"
coverage_row["migration_status"] = "complete"
coverage_row["source_line_ranges"] = "L847-881"
coverage_row["note"] = (
    "Printed p.431 contains 28 publication entries; [Page 431] at L846 is only a page marker. "
    "The p.430 Molinier author pointer is confirmed by the coauthored article at L861. "
    "The page image corrects several OCR readings, including Moroni's omitted volume/date line, "
    "Moschini misread as Meschini, and the fused Nicodemi/Nisser entries at L876."
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(
    json.dumps(
        {
            "mode": "apply" if ARGS.apply else "dry-run",
            "segment_id": SEGMENT,
            "candidate_updates": len(candidate_updates),
            "new_candidates": len(new_candidates),
            "new_mentions": len(new_mentions),
            "new_statements": len(new_statements),
            "publication_statements": len(new_statements),
            "previous_cross_reference_updated": PREVIOUS_XREF,
            "candidate_count_after": len(all_candidates),
            "mention_count_after": len(all_mentions),
            "statement_count_after": len(all_statements),
            "coverage_rows": len(all_coverage),
        },
        ensure_ascii=False,
        indent=2,
    )
)

if ARGS.apply:
    table_paths = (candidate_path, mention_path, statement_path, coverage_path)
    backup_paths = [path.with_name(path.name + BACKUP) for path in table_paths]
    for backup_path in backup_paths:
        if backup_path.exists():
            raise SystemExit(f"backup already exists: {backup_path}")
    for path, backup_path in zip(table_paths, backup_paths):
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
