#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 432."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l883-926"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "6d88b39c3357751e8a7cde0ac8c41e7a9df9facc612d5ad8849eb0c7f76f4726"
BACKUP = ".bak-s2-chp21-bibliography-l883-926-20261007"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l846-881"

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
segment_text = "\n".join(source_lines[882:926])
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
    883,
    926,
    SEGMENT_SHA,
    SOURCE_SHA,
):
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
    11388,
    26543,
    11816,
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
        "id": "cand-10169",
        "expected": "Nuti, 1941, p.199 (p.337 note 2 citation locator)",
        "name": "R. Nuti, ‘Lettere di Giambattista Pasquali libraio editore in Venezia’ (Bibliofilia, 1941, pp. 193–200)",
        "detail": "Printed p.432 supplies the article title and page range for this existing 1941 locator. The article was not independently consulted.",
    },
    {
        "id": "cand-11151",
        "expected": "Loredana Olivato's 1974 article on Giuseppe Maria Sasso",
        "name": "Loredana Olivato, ‘Gli affari sono affari: Giovan Maria Sasso tratta con Tommaso degli Obizzi’ (Arte Veneta, 1974, pp. 298–304)",
        "detail": "Printed p.432 supplies the exact title and pages for this existing 1974 article candidate. The article was not independently consulted.",
    },
    {
        "id": "cand-11119",
        "expected": "Loredana Olivato's 1977 article on Boscarati and Pisani",
        "name": "Loredana Olivato, ‘Politica e retorica figurativa nella Venezia del Settecento. Alla riscoperta di un pittore singolare: Felice Boscarati’ (Arte Veneta, 1977, pp. 145–156)",
        "detail": "Printed p.432 supplies the exact title and pages for this existing 1977 article candidate. The article was not independently consulted.",
    },
    {
        "id": "cand-11184",
        "expected": "Omaggio a Leopoldo de’ Medici (exhibition catalogue cited at p.404 note 1)",
        "name": "Omaggio a Leopoldo de’ Medici—Gabinetto disegni e stampe degli Uffizi, XLIV (2 vols., 1976; Parte I—Disegni; Parte II—Ritrattini)",
        "detail": "Printed p.432 identifies the catalogue series, volume number, two-part extent and year for the existing exhibition-catalogue candidate. The catalogue was not independently consulted.",
    },
    {
        "id": "cand-7852",
        "expected": "Vita del Gran Principe Ferdinando di Toscana (attributed to Luca Ombrosi; Firenze 1887)",
        "name": "Luca Ombrosi, Vita del Gran Principe Ferdinando di Toscana (Biblioteca Grassoccia, Firenze, 1887)",
        "detail": "Printed p.432 confirms the bracketed author attribution, series and publication data for this existing candidate. The volume was not independently consulted.",
    },
    {
        "id": "cand-10891",
        "expected": "Cesare d’Onofrio, 1963 publication cited for Agucchi and Villa Aldobrandini (title unspecified)",
        "name": "Cesare d’Onofrio, La Villa Aldobrandini di Frascati (Roma, 1963)",
        "detail": "Printed p.432 supplies the title and publication place for this existing 1963 citation candidate. The book was not independently consulted.",
    },
    {
        "id": "cand-10895",
        "expected": "Cesare d’Onofrio, 1964 publication cited for Cardinal Aldobrandini’s Bolognese paintings (title unspecified)",
        "name": "Cesare d’Onofrio, ‘Inventario dei dipinti del cardinal Pietro Aldobrandini, compilato da G. B. Agucchi nel 1603’ (Palatino, 1964, pp. 15–20, 158–162, 202–211)",
        "detail": "Printed p.432 supplies the exact article title, periodical and three page ranges for this existing 1964 citation candidate. The article was not independently consulted.",
    },
    {
        "id": "cand-6385",
        "expected": "Orbaan (1914), cited publication at p.46; title unspecified",
        "name": "J. A. F. Orbaan, ‘Virtuosi al Pantheon—Archivalische Beiträge zur römischen Kunstgeschichte’ (Repertorium für Kunstwissenschaft, vol. 37, 1914–1915, pp. 17–52)",
        "detail": "Printed p.432 supplies the article title, volume, year range and pages for the existing Orbaan 1914 citation candidate. The article was not independently consulted.",
    },
    {
        "id": "cand-4373",
        "expected": "Orbaan (1920), cited publication; title unspecified",
        "name": "J. A. F. Orbaan, Documenti sul Barocco in Roma (Roma, 1920)",
        "detail": "Printed p.432 supplies the title and place for this existing Orbaan 1920 citation candidate. The book was not independently consulted.",
    },
    {
        "id": "cand-7770",
        "expected": "Unidentified d'Orsi publication on Giaquinto's work in Macerata (pp. 31-32)",
        "name": "Mario D’Orsi, Corrado Giaquinto (Roma, 1958)",
        "detail": "Printed p.432 identifies the title and publication year for this existing Giaquinto citation candidate; the author form follows the source’s reversed bibliography heading. The book was not independently consulted.",
    },
    {
        "id": "cand-5154",
        "expected": "Ortolani, cited publication on the Theatines church; title and date unspecified",
        "name": "Sergio Ortolani, S. Andrea della Valle (Roma, n.d.)",
        "detail": "Printed p.432 supplies the title and place for this existing Ortolani citation candidate. The publication year is not stated; the source was not independently consulted.",
    },
    {
        "id": "cand-8840",
        "expected": "Osti, 1951, p. 119 (bibliographic locator cited by Haskell at p.276)",
        "name": "O. Osti, ‘Sebastiano Ricci in Inghilterra’ (Commentari, 1951, pp. 119–123)",
        "detail": "Printed p.432 supplies the article title and full page range for the existing Osti citation candidate. The article was not independently consulted.",
    },
    {
        "id": "cand-4979",
        "expected": "Treatise on painting’s persuasive possibilities by Ottonelli and Pietro da Cortona (cited as Trattato)",
        "name": "[Gio. Dom. S. J. Ottonelli and Pietro da Cortona], Trattato della Pittura e Scultura, uso ed abuso loro (Firenze, 1652)",
        "detail": "Printed p.432 supplies the full title, bracketed attribution and edition date. Keep the 1973 Ottonelli–Berrettini edition candidate cand-11160 separate for S3; neither edition was independently consulted.",
    },
    {
        "id": "cand-11160",
        "expected": "Vittorio Casale publication cited for censor’s comments on the Ottonelli–Berrettini treatise (title and date unspecified)",
        "name": "Gio. Dom. Ottonelli and P. Berrettini, Trattato della Pittura e Scultura (ed. Vittorio Casale, Treviso, 1973)",
        "detail": "Printed p.432 identifies the 1973 edition and editor for this existing Casale citation candidate. Keep the 1652 edition candidate cand-4979 distinct for S3; the book was not independently consulted.",
    },
    {
        "id": "cand-6366",
        "expected": "Ozzola (1908), cited publication; title unspecified",
        "name": "L. Ozzola, ‘L’Arte alla corte di Alessandro VII’ (Archivio della Società Romana di Storia Patria, 1908, pp. 5–91)",
        "detail": "Printed p.432 supplies the title, journal and page range for this existing Ozzola citation candidate. The article was not independently consulted.",
    },
    {
        "id": "cand-6973",
        "expected": "Pacichelli, Parte IV, volume I (cited publication; title unspecified in p.191 note 9)",
        "name": "Abbate Gio: Battista Pacichelli, Memorie de’ viaggi per l’Europa Christiana (Napoli, 1685)",
        "detail": "Printed p.432 supplies the title, author form and edition for this existing Pacichelli locator. The cited part and volume locator remain in its earlier statement; the book was not independently consulted.",
    },
    {
        "id": "cand-6364",
        "expected": "P. Sforza Pallavicino, Libro V, cap.5; work title unspecified",
        "name": "P. Sforza Pallavicino, Della vita di Alessandro VII (Prato, 1839)",
        "detail": "Printed p.432 supplies the title and edition corresponding to this existing Pallavicino citation candidate. The cited text and book were not independently consulted.",
    },
    {
        "id": "cand-8820",
        "expected": "Pallucchini, 1931, pp.421-432 (citation locator; title pending)",
        "name": "R. Pallucchini, ‘Il pittore Giuseppe Angeli’ (Rivista di Venezia, 1931, pp. 421–432)",
        "detail": "Printed p.432 supplies the article title and journal for this existing 1931 locator. The article was not independently consulted.",
    },
    {
        "id": "cand-9296",
        "expected": "Pallucchini, 1933-4, pp.1491-1511 (citation locator; title unresolved)",
        "name": "R. Pallucchini, ‘Contributo alla biografia di Federico Bencovich’ (Atti del Reale Istituto Veneto di Scienze, Lettere ed Arti, 1933–1934, vol. 93, parte seconda, pp. 1491–1511)",
        "detail": "Printed p.432 supplies the title and journal issue for this existing 1933–34 citation candidate. The article was not independently consulted.",
    },
    {
        "id": "cand-10588",
        "expected": "Mostra degli Incisori Veneti del Settecento (1941), p.112",
        "name": "R. Pallucchini, Mostra degli Incisori Veneti del Settecento (Venezia, 1941)",
        "detail": "Printed p.432 identifies this as Pallucchini’s 1941 exhibition catalogue. Existing page locators remain in their statements; the catalogue was not independently consulted.",
    },
    {
        "id": "cand-10320",
        "expected": "Pallucchini, 1956, p.41 (citation locator in p.355 note 2)",
        "name": "R. Pallucchini, Piazzetta (Milano, 1956)",
        "detail": "Printed p.432 supplies the title and publication place for this existing 1956 locator. The cited page and book were not independently consulted.",
    },
    {
        "id": "cand-11063",
        "expected": "Pallucchini-edited volume on country-villa decoration",
        "name": "Gli affreschi nelle Ville Venete dal Seicento all’Ottocento: testi (prefazione by R. Pallucchini; 2 vols., Venezia, 1978)",
        "detail": "Printed p.432 supplies the title, preface role, contributor names and two-volume publication data for this existing edited-volume candidate. The volumes were not independently consulted.",
    },
    {
        "id": "cand-4955",
        "expected": "Palomino, cited publication, volume III, p. 336; title unspecified",
        "name": "Antonio Palomino, El Museo Pictorico, y escala optico (3 vols. in 2, Madrid, 1715–1724)",
        "detail": "Printed p.432 supplies the title and edition extent for this existing volume-III citation candidate. Keep the other Palomino page locator cand-7587 linked for S3; the work was not independently consulted.",
    },
    {
        "id": "cand-5474",
        "expected": "Erwin Panofsky, Imago pietatis (1927), cited page 290",
        "name": "E. Panofsky, ‘Imago pietatis’ (in Festschrift für Max J. Friedländer, Leipzig, 1927, pp. 261–308)",
        "detail": "Printed p.432 supplies the host volume and full page range for this existing Panofsky article candidate. The cited essay was not independently consulted.",
    },
    {
        "id": "cand-5712",
        "expected": "Panofsky publication cited in 1954 for the paragraph (title unspecified)",
        "name": "E. Panofsky, Galileo as critic of the arts (The Hague, 1954)",
        "detail": "Printed p.432 supplies the title and publication place for this existing Panofsky 1954 citation candidate. The book was not independently consulted.",
    },
    {
        "id": "cand-4865",
        "expected": "Erwin Panofsky (1957), cited publication; title unspecified",
        "name": "E. Panofsky, ‘Et in Arcadia ego’ (reprinted in Meaning in the Visual Arts, New York, 1957)",
        "detail": "Printed p.432 identifies the essay and its reprint volume for this existing Panofsky 1957 candidate. The volume and essay were not independently consulted.",
    },
    {
        "id": "cand-9974",
        "expected": "Paoletti, 1832, page 122 (citation locator)",
        "name": "[Ermalao Paoletti], Continuazione alla storia della Repubblica di Venezia (Venezia, 1832)",
        "detail": "Printed p.432 confirms the bracketed author form and title for this existing 1832 citation candidate. Preserve the printed name Ermalao; do not normalize it to a different form. The volume was not independently consulted.",
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

new_candidate_specs = [
    (
        "cand-11410",
        "Cesare d’Onofrio, Roma vista da Roma (Roma, 1967)",
        "Bibliography entry at printed p.432. The book was not independently consulted.",
        897,
    ),
    (
        "cand-11411",
        "R. Pallucchini, ‘Studi ricceschi—(i) Contributo a Sebastiano’ (Arte Veneta, 1952, pp. 63–84)",
        "Bibliography entry at printed p.432. Keep distinct from the author's other Ricci studies pending S3; the article was not independently consulted.",
        916,
    ),
    (
        "cand-11412",
        "Panciroli, Tesori nascosti dell’alma città di Roma (Roma, 1625)",
        "Bibliography entry at printed p.432. The printed author heading supplies no given name or initial; the book was not independently consulted.",
        921,
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
    ("cand-10169", 884, 885, "Nuti, R.", "Lettere di Giambattista Pasquali libraio editore in Venezia", "Bibliofilia, 1941, pp. 193–200", "journal article", {"related": ["cand-10167"]}),
    ("cand-11151", 886, 887, "Olivato, Loredana", "Gli affari sono affari: Giovan Maria Sasso tratta con Tommaso degli Obizzi", "Arte Veneta, 1974, pp. 298–304", "journal article", {}),
    ("cand-11119", 888, 889, "Olivato, Loredana", "Politica e retorica figurativa nella Venezia del Settecento. Alla riscoperta - di un pittore singolare: Felice Boscarati", "Arte Veneta, 1977, pp. 145–156", "journal article", {}),
    ("cand-11184", 890, 891, "", "Omaggio a Leopoldo de’ Medici—Gabinetto disegni e stampe degli Uffizi, XLIV", "1976, 2 vols. (Parte I—Disegni; Parte II—Ritrattini)", "exhibition catalogue", {}),
    ("cand-7852", 892, 893, "[Ombrosi, Luca]", "Vita del Gran Principe Ferdinando di Toscana", "in Biblioteca Grassoccia, Firenze 1887", "book", {}),
    ("cand-10891", 894, 894, "D’Onofrio, Cesare", "La Villa Aldobrandini di Frascati", "Roma 1963", "book", {"page_image_notes": ["The short trailing dash after the year appears in the OCR and is retained as printed punctuation."]}),
    ("cand-10895", 895, 896, "D’Onofrio, Cesare", "Inventario dei dipinti del cardinal Pietro Aldobrandini, compilato da G. B. Agucchi nel 1603", "Palatino, 1964, pp. 15–20, 158–162, 202–211", "journal article", {"corrections": [{"line": 896, "ocr": "15 8-162", "print": "158–162", "note": "The page image confirms the continuous page range."}]}),
    ("cand-11410", 897, 897, "D’Onofrio, Cesare", "Roma vista da Roma", "Roma 1967", "book", {"page_image_notes": ["The short trailing dash after the year is present in the page transcription and is retained as punctuation."]}),
    ("cand-6385", 898, 898, "Orbaan, J. A. F.", "Virtuosi al Pantheon—Archivalische Beiträge zur römischen Kunstgeschichte", "Repertorium für Kunstwissenschaft, vol. 37, 1914–15, pp. 17–52", "journal article", {"corrections": [{"line": 898, "ocr": "voi. 37", "print": "vol. 37", "note": "The page image reads vol. 37."}]}),
    ("cand-4373", 899, 899, "Orbaan, J. A. F.", "Documenti sul Barocco in Roma", "Roma 1920", "book", {}),
    ("cand-7137", 900, 900, "Orlandi, Pellegrino Antonio", "Abecedario Pittorico", "Venezia 1753", "book", {}),
    ("cand-7770", 901, 901, "Orsi, Mario D’", "Corrado Giaquinto", "Roma 1958", "book", {}),
    ("cand-5154", 902, 902, "Ortolani, Sergio", "S. Andrea della Valle", "Roma n.d.", "book; publication year not stated", {}),
    ("cand-8840", 903, 903, "Osti, O.", "Sebastiano Ricci in Inghilterra", "Commentari, 1951, pp. 119–123", "journal article", {}),
    ("cand-4979", 904, 905, "[Ottonelli, Gio. Dom. S. J. e Pietro da Cortona]", "Trattato della Pittura e Scultura, uso ed abuso loro", "with the printed pseudonymous byline; Firenze 1652", "book", {"related": ["cand-11160"]}),
    ("cand-11160", 906, 907, "Ottonelli, Gio. Dom.—Berrettini, P.", "Trattato della Pittura e Scultura", "a cura di Vittorio Casale, Treviso 1973", "edited book edition", {"related": ["cand-4979"]}),
    ("cand-6366", 908, 909, "Ozzola, L.", "L’Arte alla corte di Alessandro VII", "Archivio della Società Romana di Storia Patria, 1908, pp. 5–91", "journal article", {}),
    ("cand-6973", 910, 910, "Pacichelli, Abbate Gio: Battista", "Memorie de’ viaggi per l’Europa Christiana", "Napoli 1685", "book", {}),
    ("cand-6364", 911, 911, "Pallavicino, P. Sforza", "Della vita di Alessandro VII", "Prato 1839", "book", {"corrections": [{"line": 911, "ocr": "Alessandro VÌI", "print": "Alessandro VII", "note": "The page image reads the Roman numeral VII."}, {"line": 911, "ocr": "1839. .", "print": "1839.", "note": "The page image has a single terminal period."}]}),
    ("cand-8820", 912, 912, "Pallucchini, R.", "Il pittore Giuseppe Angeli", "Rivista di Venezia, 1931, pp. 421–432", "journal article", {}),
    ("cand-9296", 913, 914, "Pallucchini, R.", "Contributo alla biografia di Federico Bencovich", "Atti del Reale Istituto Veneto di Scienze, Lettere ed Arti, 1933–34, vol. 93, parte seconda, pp. 1491–1511", "journal article", {"corrections": [{"line": 914, "ocr": "voi. 93", "print": "vol. 93", "note": "The page image reads vol. 93."}]}),
    ("cand-10588", 915, 915, "Pallucchini, R.", "Mostra degli Incisori Veneti del Settecento", "Venezia 1941", "exhibition catalogue", {}),
    ("cand-11411", 916, 916, "Pallucchini, R.", "Studi ricceschi—(i) Contributo a Sebastiano", "Arte Veneta, 1952, pp. 63–84", "journal article", {}),
    ("cand-10320", 917, 917, "Pallucchini, R.", "Piazzetta", "Milano 1956", "book", {"corrections": [{"line": 917, "ocr": "_ - Pallucchini", "print": "Pallucchini", "note": "The page image begins the entry at Pallucchini; the leading OCR marks are margin artifacts."}, {"line": 917, "ocr": "1956. -", "print": "1956.", "note": "The trailing OCR dash is not part of the printed entry."}]}),
    ("cand-11063", 918, 919, "Pallucchini, R. (prefazione)", "Gli affreschi nelle Ville Venete dal Seicento all’Ottocento: testi", "Francesca d’Arcais, Franca Zava Bocazzi, Giuseppe Pavanello, 2 vols., Venezia 1978", "preface in edited volume", {}),
    ("cand-4955", 920, 920, "Palomino, Antonio", "El Museo Pictorico, y escala optico", "Madrid, 3 vols. in 2, 1715–1724", "multi-volume book set", {"related": ["cand-7587"]}),
    ("cand-11412", 921, 921, "Panciroli,", "Tesori nascosti dell’alma città di Roma", "Roma 1625", "book; given name not supplied", {}),
    ("cand-5474", 922, 923, "Panofsky, E.", "Imago pietatis", "pp. 261–308 in Festschrift für Max J. Friedländer, Leipzig 1927", "contribution to festschrift", {}),
    ("cand-5712", 924, 924, "Panofsky, E.", "Galileo as critic of the arts", "The Hague 1954", "book", {"corrections": [{"line": 924, "ocr": "thè arts", "print": "the arts", "note": "The page image has no grave accent."}]}),
    ("cand-4865", 925, 925, "Panofsky, E.", "Et in Arcadia ego", "reprinted in Meaning in the Visual Arts, New York 1957", "reprinted essay", {"corrections": [{"line": 925, "ocr": "thè Visual Arts", "print": "the Visual Arts", "note": "The page image has no grave accent."}]}),
    ("cand-9974", 926, 926, "[Paoletti, Ermalao]", "Continuazione alla storia della Repubblica di Venezia", "Venezia 1832", "book", {}),
]

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
    return "\n".join(source_lines[entry["start"] - 1 : entry["end"]])


def add_mention(candidate_id, surface):
    positions = [index for index in range(len(segment_text)) if segment_text.startswith(surface, index)]
    if len(positions) != 1:
        raise SystemExit(f"mention surface must occur once in segment: {candidate_id} {surface!r}")
    position = positions[0]
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    mention_id = f"m-chp21-bib-l883-926-{len(new_mentions) + 1:03d}"
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
            "printed_page": 432,
        },
    }
    if entry.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("page_image_notes"):
        qualifiers["page_image_notes"] = entry["page_image_notes"]
    if entry.get("related"):
        qualifiers["related_candidate_ids_for_s3"] = entry["related"]
    quote = source_quote(entry)
    if not quote or quote not in "\n".join(source_lines[entry["start"] - 1 : entry["end"]]):
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
    add_mention(candidate_id, quote)
    add_publication_statement(
        f"st-chp21-bib-l883-926-entry-{index:02d}", entry, candidate_id
    )

if len(entries) != 31 or len(candidate_updates) != 27 or len(new_candidates) != 3 or len(new_mentions) != 31 or len(new_statements) != 31:
    raise SystemExit(
        f"unexpected migration row counts: publications={len(entries)}, "
        f"candidate_updates={len(candidate_updates)}, new_candidates={len(new_candidates)}, "
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

coverage_row["disposition"] = "reviewed"
coverage_row["migration_status"] = "complete"
coverage_row["source_line_ranges"] = "L884-926"
coverage_row["note"] = (
    "Printed p.432 contains 31 publication entries; [Page 432] at L883 is only a page marker. "
    "Reused 28 archive candidates and added three archive candidates. The page image corrects "
    "the D’Onofrio inventory page range, Pallucchini volume notation and Panofsky title accents."
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
