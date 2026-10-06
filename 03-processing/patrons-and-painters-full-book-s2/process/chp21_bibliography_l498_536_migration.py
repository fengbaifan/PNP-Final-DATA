#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 423."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l498-536"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "5ba9899b5a4331e414cb249088bb631bce2d3a0be4ab8fd141de1dc3eba5121f"
BACKUP = ".bak-s2-chp21-bibliography-l498-536-20261007"
DISPLACED_NOEMI_SEGMENT = "chp-21:21_CHP-21Bibliography:l1301-1306"

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
segment_text = "\n".join(source_lines[497:536])
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
    11309,
    26275,
    11549,
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
if DISPLACED_NOEMI_SEGMENT not in coverage_by_id or (
    coverage_by_id[DISPLACED_NOEMI_SEGMENT]["disposition"],
    coverage_by_id[DISPLACED_NOEMI_SEGMENT]["migration_status"],
) != ("queued", "pending"):
    raise SystemExit("displaced Noemi source segment is not queued")

# Entry boundaries and OCR corrections were checked against PDF physical page 13.
entries = [
    {
        "candidate_id": "cand-4375", "start": 499, "end": 499,
        "author": "Friedlaender, Walter", "title": "Caravaggio Studies",
        "details": "Princeton 1955", "kind": "book",
        "corrections": [{"line": 499, "ocr": "1955. .", "print": "1955."}],
    },
    {
        "candidate_id": "cand-10878", "start": 500, "end": 501,
        "author": "Frommel, Christoph Luitpold",
        "title": "Caravaggio’s Frühwerk und der Kardinal Francesco Maria Del Monte",
        "details": "Storia dell’Arte, 1971, pp. 5-52", "kind": "journal article",
        "corrections": [
            {"line": 500, "ocr": "Früh werk", "print": "Frühwerk"},
            {"line": 500, "ocr": "Kar-dinal", "print": "Kardinal"},
        ],
    },
    {
        "candidate_id": "cand-11331", "start": 502, "end": 502,
        "new_name": "Annamaria Gabbrielli, ‘L’Algarotti e la critica d’arte in Italia nel Settecento’ (La Critica d’Arte, 1938, pp. 155-169; 1939, pp. 24-31)",
        "new_detail": "The bibliography gives one entry with two year/page ranges. Kept distinct from citation locators cand-10413 and cand-10414 pending S3; neither cited publication was independently consulted.",
        "author": "Gabbrielli, Annamaria",
        "title": "L’Algarotti e la critica d’arte in Italia nel Settecento",
        "details": "La Critica d’Arte, 1938, pp. 155-169, and 1939, pp. 24-31",
        "kind": "journal article",
        "related": ["cand-10413", "cand-10414"],
    },
    {
        "candidate_id": "cand-11332", "start": 503, "end": 503,
        "new_name": "Giuseppe Gabrieli, Il carteggio Linceo della vecchia accademia di Federico Cesi (1603-1630) (4 vols., Roma, 1939-42)",
        "new_detail": "The printed p.423 continuation supplies 4 vols. and Roma 1939-42; its OCR text is displaced to L1304. Kept distinct from citation locator cand-5642 pending S3; contents were not independently consulted.",
        "author": "Gabrieli, Giuseppe",
        "title": "Il carteggio Linceo della vecchia accademia di Federico Cesi (1603-1630)",
        "details": "4 vols., Roma 1939-42", "kind": "four-volume publication set",
        "page_image_notes": [
            "The print continues this record with '4 vols., Roma 1939-42.'; the OCR continuation is displaced to L1304. When the queued L1301-1306 segment is reviewed, link that exact source span to this candidate without adding a second bibliography statement."
        ],
        "related": ["cand-5642"],
    },
    {
        "candidate_id": "cand-5164", "start": 504, "end": 505,
        "author": "Galassi Paluzzi, C.",
        "title": "Le decorazioni della sacrestia di S. Ignazio e il loro vero autore",
        "details": "Roma, 1926, pp. 542-546", "kind": "journal article",
    },
    {
        "candidate_id": "cand-4974", "start": 506, "end": 506,
        "author": "Galassi Paluzzi, C.",
        "title": "Storia segreta dello stile dei Gesuiti",
        "details": "Roma 1951", "kind": "book",
    },
    {
        "candidate_id": "cand-11334", "start": 507, "end": 507,
        "new_name": "Galileo Galilei, Ristampa dell’edizione nazionale (20 vols., Firenze, 1929-39)",
        "new_detail": "Set-level bibliography record; kept distinct from volume-XVIII citation locator cand-5835 pending S3; contents were not independently consulted.",
        "author": "Galilei, Galileo",
        "title": "Ristampa dell’edizione nazionale",
        "details": "20 vols., Firenze 1929-39", "kind": "20-volume publication set",
        "related": ["cand-5835"],
    },
    {
        "candidate_id": "cand-11335", "start": 508, "end": 508,
        "new_name": "R. Gallo, I Pisani ed i Palazzi di S. Stefano e di Strà (Venezia, 1945)",
        "new_detail": "Bibliography-level book record; kept distinct from 1945 citation locators cand-8515 and cand-8537 pending S3; the book was not independently consulted.",
        "author": "Gallo, R.",
        "title": "I Pisani ed i Palazzi di S. Stefano e di Strà",
        "details": "Venezia 1945", "kind": "book",
        "corrections": [{"line": 508, "ocr": "Stri", "print": "Strà"}],
        "related": ["cand-8515", "cand-8537"],
    },
    {
        "candidate_id": "cand-11336", "start": 509, "end": 509,
        "new_name": "R. Gallo, ‘L’incisione nel ’700 a Venezia e a Bassano’ (Ateneo Veneto, 1948, pp. 153-214)",
        "new_detail": "Bibliography-level article record; kept distinct from 1948 citation locators cand-10138 and cand-10150 pending S3; the article was not independently consulted.",
        "author": "Gallo, R.",
        "title": "L’incisione nel ’700 a Venezia e a Bassano",
        "details": "Ateneo Veneto, 1948, pp. 153-214", "kind": "journal article",
        "corrections": [{"line": 509, "ocr": "15 3-214", "print": "153-214"}],
        "related": ["cand-10138", "cand-10150"],
    },
    {
        "candidate_id": "cand-7834", "start": 510, "end": 511,
        "author": "Galluzzi, J. R.",
        "title": "Istoria del Granducato di Toscana sotto il governo della Casa Medici",
        "details": "Firenze 1781", "kind": "book",
    },
    {
        "candidate_id": "cand-11337", "start": 512, "end": 512,
        "new_name": "Carlo Gamba, ‘Sebastiano Ricci e la sua opera fiorentina’ (Dedalo, 1924-5, pp. 289-314)",
        "new_detail": "Bibliography-level article record; cited contents were not independently consulted.",
        "author": "Gamba, Carlo",
        "title": "Sebastiano Ricci e la sua opera fiorentina",
        "details": "Dedalo, 1924-5, pp. 289-314", "kind": "journal article",
    },
    {
        "candidate_id": "cand-11338", "start": 513, "end": 514,
        "new_name": "Tommaso Gar, ‘Storia arcana ed altri scritti inediti di Marco Foscarini’ (Archivio Storico Italiano, vol. V, 1843)",
        "new_detail": "Bibliography-level article record; the volume notation is preserved as printed and the article was not independently consulted.",
        "author": "Gar, Tommaso",
        "title": "Storia arcana ed altri scritti inediti di Marco Foscarini",
        "details": "Archivio Storico Italiano, V, 1843", "kind": "journal article",
    },
    {
        "candidate_id": "cand-9343", "start": 515, "end": 515,
        "author": "Garas, Clara",
        "title": "Le plafond de la Banque Royale de Giovanni Antonio Pellegrini",
        "details": "Bulletin du Musée Hongrois des Beaux-Arts, Budapest, 1962 (21), pp. 75-93",
        "kind": "journal article",
    },
    {
        "candidate_id": "cand-10873", "start": 516, "end": 516,
        "author": "Garas, Clara",
        "title": "The Ludovisi Collection of Pictures in 1633",
        "details": "Burlington Magazine, 1967, pp. 287-289 and 339-348",
        "kind": "journal article",
    },
    {
        "candidate_id": "cand-9456", "start": 517, "end": 517,
        "author": "Garas, Clara",
        "title": "Giovanni Antonio Pellegrini in Deutschland",
        "details": "Arte Veneta, 1971, pp. 285-292", "kind": "journal article",
        "corrections": [{"line": 517, "ocr": "28 5-292", "print": "285-292"}],
    },
    {
        "candidate_id": "cand-11174", "start": 518, "end": 518,
        "author": "Garms, Jörg (editor)",
        "title": "Quellen aus dem Archiv Doria-Pamphilj zur Kunsttätigkeit in Rom unter Innocenz X",
        "details": "Rome-Wien 1972", "kind": "edited volume",
        "corrections": [
            {"line": 518, "ocr": "Garrns", "print": "Garms"},
            {"line": 518, "ocr": "(editor) :", "print": "(editor):"},
        ],
    },
    {
        "candidate_id": "cand-7122", "start": 519, "end": 519,
        "author": "Ghelli, M. E.",
        "title": "Il viceré marchese del Carpio (1683-1687)",
        "details": "Archivio storico per le province napoletane, 1933, pp. 280-318, and 1934, pp. 257-282",
        "kind": "journal article",
    },
    {
        "candidate_id": "cand-8005", "start": 520, "end": 521,
        "author": "[Gherardi, P. E.]",
        "title": "Descrizione di cartoni disegnati da C. Cignani, e de’ quadri dipinti da Sebastiano Ricci posseduti dal Signor Giuseppe Smith",
        "details": "Venezia 1749", "kind": "anonymous publication with bracketed attribution",
    },
    {
        "candidate_id": "cand-11339", "start": 522, "end": 522,
        "new_name": "Edward Gibbon, Letters (edited by J. E. Norton, 3 vols., London, 1956)",
        "new_detail": "Bibliography-level edited letter collection record; the collection was not independently consulted.",
        "author": "Gibbon, Edward",
        "title": "Letters—edited by J. E. Norton",
        "details": "3 vols., London 1956", "kind": "edited letter collection",
    },
    {
        "candidate_id": "cand-6076", "start": 523, "end": 523,
        "author": "Gigli, Giacinto",
        "title": "Diario Romano",
        "details": "a cura di Giuseppe Ricciotti, Roma 1958", "kind": "edited book",
        "related": ["cand-6269", "cand-6360"],
    },
    {
        "candidate_id": "cand-7866", "start": 524, "end": 525,
        "author": "Giglioli, O. H.",
        "title": "Su un quadro del Volterrano nella Galleria degli Uffizi creduto finora di Giovanni da San Giovanni",
        "details": "Bollettino d’Arte, 1908, pp. 335-358", "kind": "journal article",
    },
    {
        "candidate_id": "cand-4848", "start": 526, "end": 526,
        "author": "Giglioli, O. H.",
        "title": "Giovanni da San Giovanni",
        "details": "Firenze 1949", "kind": "book",
    },
    {
        "candidate_id": "cand-11340", "start": 527, "end": 528,
        "new_name": "John Gilmartin, ‘The Paintings commissioned by Pope Clement XI for the Basilica of S. Clemente in Rome’ (Burlington Magazine, 1974, pp. 305-310)",
        "new_detail": "Bibliography-level article record; the article was not independently consulted.",
        "author": "Gilmartin, John",
        "title": "The Paintings commissioned by Pope Clement XI for the Basilica of S. Clemente in Rome",
        "details": "Burlington Magazine, 1974, pp. 305-310", "kind": "journal article",
        "corrections": [{"line": 528, "ocr": "'Clemente", "print": "Clemente"}],
    },
    {
        "candidate_id": "cand-8325", "start": 529, "end": 529,
        "author": "Giussani, Antonio",
        "title": "I fasti della famiglia patrizia comasca dei Rezzonico",
        "details": "Como 1931", "kind": "book",
    },
    {
        "candidate_id": "cand-11341", "start": 530, "end": 530,
        "new_name": "Michele Giustiniani, Lettere memorabili (3 vols., Roma, 1667, 1669, 1675)",
        "new_detail": "Three-volume bibliography-level publication record; kept distinct from volume-I citation locator cand-4389 pending S3; cited contents were not independently consulted.",
        "author": "Giustiniani, Abbate Michele",
        "title": "Lettere memorabili",
        "details": "3 vols., Roma 1667, 1669, 1675", "kind": "three-volume publication set",
        "related": ["cand-4389"],
    },
    {
        "candidate_id": "cand-9331", "start": 531, "end": 531,
        "author": "Goering, M.",
        "title": "Pellegrini-Studien",
        "details": "Münchner Jahrbuch der bildenden Kunst, 1937-8, pp. 233-250",
        "kind": "journal article",
    },
    {
        "candidate_id": "cand-11342", "start": 532, "end": 532,
        "new_name": "J. G. Goethe, Viaggio in Italia (1740) (edited by A. Farinelli, Roma, 1932)",
        "new_detail": "Bibliography-level edition record; kept distinct from the volume-I, page-38 citation locator cand-10135 pending S3; the book was not independently consulted.",
        "author": "Goethe, J. G.",
        "title": "Viaggio in Italia (1740)",
        "details": "a cura di A. Farinelli, Roma 1932", "kind": "edited book",
        "related": ["cand-10135"],
    },
    {
        "candidate_id": "cand-11343", "start": 533, "end": 533,
        "new_name": "Carlo Goldoni, Tutte le opere (edited by Giuseppe Ortolani, 14 vols., Milano, 1935-1956)",
        "new_detail": "Fourteen-volume bibliography-level set; kept distinct from volume-V citation locator cand-9496 pending S3; contents were not independently consulted.",
        "author": "Goldoni, Carlo",
        "title": "Tutte le opere",
        "details": "a cura di Giuseppe Ortolani, Milano, 14 vols., 1935-1956",
        "kind": "fourteen-volume publication set",
        "related": ["cand-9496"],
    },
    {
        "candidate_id": "cand-6356", "start": 534, "end": 535,
        "author": "Golzio, V.",
        "title": "Pittori e scultori nella chiesa di S. Agnese a Piazza Navona in Roma",
        "details": "Archivi, 1933-4, pp. 300-310", "kind": "journal article",
        "corrections": [{"line": 535, "ocr": "PP300-310", "print": "pp. 300-310"}],
    },
    {
        "candidate_id": "cand-6196", "start": 536, "end": 536,
        "author": "Golzio, V.",
        "title": "Documenti artistici sul Seicento nell’Archivio Chigi",
        "details": "Roma 1939", "kind": "book",
    },
]

covered_lines = {line for entry in entries for line in range(entry["start"], entry["end"] + 1)}
if covered_lines != set(range(499, 537)):
    raise SystemExit("bibliography entry line coverage is incomplete")
if len(entries) != 30:
    raise SystemExit("unexpected local bibliography record count")

expected_name_updates = {
    "cand-4375": (
        "Friedlaender, cited source on del Monte and Caravaggio; title and edition unspecified",
        "Walter Friedlaender, Caravaggio Studies (Princeton, 1955)",
        "Printed bibliography p.423 identifies the cited title and publication year; the book was not independently consulted.",
    ),
    "cand-10878": (
        "Christoph Frommel’s publication of Cardinal Del Monte collection inventories and Caravaggio inquiry (title unspecified)",
        "Christoph Luitpold Frommel, ‘Caravaggio’s Frühwerk und der Kardinal Francesco Maria Del Monte’ (Storia dell’Arte, 1971, pp. 5-52)",
        "Printed bibliography p.423 identifies the article title and publication details; the article was not independently consulted.",
    ),
    "cand-5164": (
        "Galassi Paluzzi (1926), cited publication, p. 542; title unspecified",
        "C. Galassi Paluzzi, ‘Le decorazioni della sacrestia di S. Ignazio e il loro vero autore’ (Roma, 1926, pp. 542-546)",
        "Printed bibliography p.423 identifies the cited article and its publication details; it was not independently consulted.",
    ),
    "cand-9343": (
        "Garas, 1962 (citation locator in p.285 note 1; work unresolved)",
        "Clara Garas, ‘Le plafond de la Banque Royale de Giovanni Antonio Pellegrini’ (Bulletin du Musée Hongrois des Beaux-Arts, Budapest, 1962, vol. 21, pp. 75-93)",
        "Printed bibliography p.423 identifies the title and publication details; the cited article was not independently consulted.",
    ),
    "cand-10873": (
        "Garas, 1967 publication of an inventory of Cardinal Ludovico’s pictures (title unspecified)",
        "Clara Garas, ‘The Ludovisi Collection of Pictures in 1633’ (Burlington Magazine, 1967, pp. 287-289 and 339-348)",
        "Printed bibliography p.423 identifies the article title and page ranges; it was not independently consulted.",
    ),
    "cand-11174": (
        "Garms publication cited in p.401 note 6 for Doria-Pamphili documents (title and year unspecified)",
        "Jörg Garms (editor), Quellen aus dem Archiv Doria-Pamphilj zur Kunsttätigkeit in Rom unter Innocenz X (Rome-Wien, 1972)",
        "Printed bibliography p.423 identifies the edited volume and publication details; it was not independently consulted.",
    ),
    "cand-8005": (
        "Abate Gherardi’s anonymous 1749 account of some of Consul Smith’s pictures in Venice",
        "[Gherardi, P. E.], Descrizione di cartoni disegnati da C. Cignani, e de’ quadri dipinti da Sebastiano Ricci posseduti dal Signor Giuseppe Smith (Venezia, 1749; attribution bracketed in the bibliography)",
        "Printed bibliography p.423 supplies the title and publication details but retains a bracketed byline; authorship remains unresolved and the work was not independently consulted.",
    ),
    "cand-6076": (
        "Giacinto Gigli's diary (title unspecified)",
        "Giacinto Gigli, Diario Romano (a cura di Giuseppe Ricciotti, Roma, 1958)",
        "Printed bibliography p.423 identifies this published edition of the diary; keep separate from page locators cand-6269 and cand-6360 pending S3 comparison. The edition was not independently consulted.",
    ),
    "cand-7866": (
        "Giglioli, O. H., 1908 publication cited for the picture's history (identity unresolved)",
        "O. H. Giglioli, ‘Su un quadro del Volterrano nella Galleria degli Uffizi creduto finora di Giovanni da San Giovanni’ (Bollettino d’Arte, 1908, pp. 335-358)",
        "Printed bibliography p.423 identifies one 1908 article; correspondence to the earlier short citation remains for S3 comparison. The article was not independently consulted.",
    ),
    "cand-4848": (
        "O. H. Giglioli (1949), cited publication; title unspecified",
        "O. H. Giglioli, Giovanni da San Giovanni (Firenze, 1949)",
        "Printed bibliography p.423 identifies the title and publication place; the book was not independently consulted.",
    ),
    "cand-8325": (
        "Unspecified Giussani reference cited on p.254 note 1",
        "Antonio Giussani, I fasti della famiglia patrizia comasca dei Rezzonico (Como, 1931)",
        "Printed bibliography p.423 identifies the title and publication details; the book was not independently consulted.",
    ),
    "cand-9331": (
        "M. Goering, 1937, pp.233-250 (citation locator in p.283 note 2)",
        "M. Goering, ‘Pellegrini-Studien’ (Münchner Jahrbuch der bildenden Kunst, 1937-8, pp. 233-250)",
        "Printed bibliography p.423 supplies the article title and journal; the article was not independently consulted.",
    ),
    "cand-6356": (
        "Golzio (1933–34), cited publication at p.304; title unspecified",
        "V. Golzio, ‘Pittori e scultori nella chiesa di S. Agnese a Piazza Navona in Roma’ (Archivi, 1933-4, pp. 300-310)",
        "Printed bibliography p.423 identifies the article title and publication details; it was not independently consulted.",
    ),
    "cand-6196": (
        "Golzio (1939), cited publication, p. 3",
        "V. Golzio, Documenti artistici sul Seicento nell’Archivio Chigi (Roma, 1939)",
        "Printed bibliography p.423 identifies the cited title and publication place; the book was not independently consulted.",
    ),
}

natural_keys = {}
for row in candidates:
    if row["suggested_type"].strip().casefold() == "archive":
        key = (row["canonical_name"].strip().casefold(), "archive")
        natural_keys.setdefault(key, set()).add(row["candidate_id"])

for candidate_id, (expected, updated, detail) in expected_name_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type bibliography candidate: {candidate_id}")
    if candidate["canonical_name"] != expected:
        raise SystemExit(f"candidate identity label changed: {candidate_id}")
    old_key = (expected.strip().casefold(), "archive")
    new_key = (updated.strip().casefold(), "archive")
    collisions = natural_keys.get(new_key, set()) - {candidate_id}
    if collisions:
        raise SystemExit(f"candidate rename collides with archive candidate {sorted(collisions)}: {candidate_id}")
    natural_keys.get(old_key, set()).discard(candidate_id)
    natural_keys.setdefault(new_key, set()).add(candidate_id)
    candidate["canonical_name"] = updated
    candidate["detail"] = f'{candidate.get("detail", "").rstrip()} {detail}'.strip()

noemi_name = "Noemi Gabrieli, ‘Aggiunte a Sebastiano Ricci’ (Proporzioni, 1950, pp. 204-211)"
noemi_detail = (
    "The printed p.423 bibliography contains this article between the Giuseppe Gabrieli and Galassi Paluzzi entries. "
    "candidate_source_ref anchors to adjacent L503 in this reviewed page-image segment; its exact OCR transcription "
    "is displaced to L1304, where the separate queued segment will add the exact S0 mention. "
    "The article was not independently consulted."
)
new_candidate_specs = [
    ("cand-11331", entries[2]["new_name"], entries[2]["new_detail"], f"{SEGMENT}#L502"),
    ("cand-11332", entries[3]["new_name"], entries[3]["new_detail"], f"{SEGMENT}#L503"),
    ("cand-11333", noemi_name, noemi_detail, f"{SEGMENT}#L503"),
    ("cand-11334", entries[6]["new_name"], entries[6]["new_detail"], f"{SEGMENT}#L507"),
    ("cand-11335", entries[7]["new_name"], entries[7]["new_detail"], f"{SEGMENT}#L508"),
    ("cand-11336", entries[8]["new_name"], entries[8]["new_detail"], f"{SEGMENT}#L509"),
    ("cand-11337", entries[10]["new_name"], entries[10]["new_detail"], f"{SEGMENT}#L512"),
    ("cand-11338", entries[11]["new_name"], entries[11]["new_detail"], f"{SEGMENT}#L513"),
    ("cand-11339", entries[18]["new_name"], entries[18]["new_detail"], f"{SEGMENT}#L522"),
    ("cand-11340", entries[22]["new_name"], entries[22]["new_detail"], f"{SEGMENT}#L527"),
    ("cand-11341", entries[24]["new_name"], entries[24]["new_detail"], f"{SEGMENT}#L530"),
    ("cand-11342", entries[26]["new_name"], entries[26]["new_detail"], f"{SEGMENT}#L532"),
    ("cand-11343", entries[27]["new_name"], entries[27]["new_detail"], f"{SEGMENT}#L533"),
]
new_candidates = []
for candidate_id, canonical_name, detail, source_ref in new_candidate_specs:
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
        candidate_source_ref=source_ref,
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.setdefault(key, set()).add(candidate_id)

mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []
new_statements = []
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
    row = {field: "" for field in mention_fields}
    row.update(
        mention_id=f"m-chp21-bib-l498-536-{len(new_mentions) + 1:03d}",
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=position,
        end_char=end,
        note=note,
    )
    new_mentions.append(row)
    mention_keys.add(key)


def make_qualifiers(entry):
    result = {
        "text_layer": "bibliographic entry",
        "qualification": (
            "This records the book bibliography entry only; the cited publication or event record "
            "was not independently consulted in this S2 pass."
        ),
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 423,
        },
    }
    if entry.get("page_image_notes"):
        result["page_image_notes"] = entry["page_image_notes"]
    if entry.get("corrections"):
        result["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("related"):
        result["related_candidate_ids_for_s3"] = entry["related"]
    return result


def add_statement(statement_id, object_id, quote, line_start, line_end, claim, qualifiers,
                  predicate="bibliography_lists_publication"):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    existing_claim_keys.add(claim_key)
    row = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "claim": claim,
            "speaker": "Haskell’s bibliography",
            "relation_candidate": False,
            "mentioned_candidate_ids": [object_id],
            **qualifiers,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    if not quote or quote not in "\n".join(source_lines[line_start - 1:line_end]):
        raise SystemExit(f"statement quote/line validation failed: {statement_id}")
    new_statements.append(row)
    statement_by_id[statement_id] = row


for index, entry in enumerate(entries, start=1):
    candidate_id = entry["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {candidate_id}")
    quote = source_quote(entry)
    add_mention(
        candidate_id,
        quote,
        "S0 bibliography entry; page-image OCR corrections are recorded on its statement.",
    )
    qualifiers = make_qualifiers(entry)
    if entry.get("related"):
        for related_id in entry["related"]:
            if related_id not in candidate_by_id:
                raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    add_statement(
        f"st-chp21-bib-l498-536-entry-{index:02d}",
        candidate_id,
        quote,
        entry["start"],
        entry["end"],
        f'Haskell lists {entry["title"]} in the bibliography.',
        qualifiers,
    )

# The Noemi Gabrieli item is visible on the page image but its OCR is displaced to L1304.
# This local statement is anchored between the adjacent S0 entries, not fabricated as a mention.
page_image_anchor = "\n".join(source_lines[502:504])
noemi_record = {
    "author_as_printed": "Gabrieli, Noemi",
    "title_as_printed": "Aggiunte a Sebastiano Ricci",
    "publication_details_as_printed": "Proporzioni, 1950, pp. 204-211",
    "record_kind": "page-image addendum to p.423 segment; OCR displaced at L1304",
    "printed_page": 423,
    "page_image_transcription": "Gabrieli, Noemi: ‘Aggiunte a Sebastiano Ricci’ in Proporzioni, 1950, pp. 204-211.",
}
add_statement(
    "st-chp21-bib-l498-536-page-image-noemi-01",
    "cand-11333",
    page_image_anchor,
    503,
    504,
    "The printed p.423 bibliography includes Gabrieli, Noemi’s Aggiunte a Sebastiano Ricci article; its OCR transcription is displaced to L1304.",
    {
        "text_layer": "bibliographic entry",
        "qualification": "This records the page-image bibliography entry only; the article was not independently consulted.",
        "bibliographic_record": noemi_record,
        "page_image_source": "02-sources/01-book/CHP-21Bibliography.pdf, physical page 13",
        "anchor_explanation": (
            "original_quote reproduces the adjacent S0 OCR lines bracketing the Noemi entry; "
            "it is not the transcription of that entry. The complete print transcription is "
            "page_image_transcription. The exact OCR text also appears displaced at L1304 and "
            "must be linked when the separate queued L1301-1306 segment is reviewed."
        ),
        "displaced_s0_source_ref": f"{DISPLACED_NOEMI_SEGMENT}#L1304",
        "s0_text_unchanged": True,
    },
    predicate="bibliography_page_image_addendum",
)

if len(new_candidates) != 13 or len(new_mentions) != 30 or len(new_statements) != 31:
    raise SystemExit("unexpected migration row counts")
if [row["candidate_id"] for row in new_candidates] != [
    f"cand-{number}" for number in range(11331, 11344)
]:
    raise SystemExit("new candidate IDs are not the expected next sequence")
for statement in new_statements:
    object_id = statement["object_candidate_id"]
    if object_id not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
    for related_id in statement["qualifiers"].get("related_candidate_ids_for_s3", []):
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {statement['statement_id']}: {related_id}")
for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")
ordered_mentions = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(ordered_mentions, ordered_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L498-536"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.423 contains 31 bibliography records: 30 locally represented in L499-536 and one "
    "Noemi Gabrieli entry visible on the page image whose OCR is displaced to L1304. The [Page 423] "
    "marker is not a record. Reused 18 archive candidates and added 13, including the page-image "
    "record; refined 14 candidate labels. Related volume/page locators remain separate for S3. "
    "Page-image OCR corrections and the displaced continuation are documented in statements; "
    "S0 remains unchanged. Cited works were not independently consulted."
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "printed_page": 423,
    "local_ocr_entries": len(entries),
    "page_image_addenda": 1,
    "total_printed_records": len(entries) + 1,
    "reused_archive_candidates": len(entries) - 12,
    "new_archive_candidates": [row["candidate_id"] for row in new_candidates],
    "candidate_labels_refined": len(expected_name_updates),
    "deferred_candidate_comparisons": sorted({
        candidate_id
        for entry in entries
        for candidate_id in entry.get("related", [])
    }),
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "noemi_exact_mention_deferred_to": f"{DISPLACED_NOEMI_SEGMENT}#L1304",
    "coverage_after": {
        "disposition": coverage_by_id[SEGMENT]["disposition"],
        "migration_status": coverage_by_id[SEGMENT]["migration_status"],
    },
    "table_counts_after": {
        "candidates": len(all_candidates),
        "mentions": len(all_mentions),
        "statements": len(all_statements),
        "coverage": len(all_coverage),
    },
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP)
        if backup.exists():
            if hashlib.sha256(backup.read_bytes()).hexdigest() != hashlib.sha256(path.read_bytes()).hexdigest():
                raise SystemExit(f"refusing to overwrite a distinct backup: {backup}")
        else:
            shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
