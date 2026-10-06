#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 434."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l985-1020"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "76480a4c281b0439c39ad8cbf2680ad60a3bb93b46f4b95a4e3a38206a213f70"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l928-983"
BACKUP = ".bak-s2-chp21-bibliography-l985-1020-20261007"
SOURCE_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"

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
segment_text = "\n".join(source_lines[984:1020])
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
) != (SOURCE_FILE, 985, 1020, SEGMENT_SHA, SOURCE_SHA):
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
    11400,
    26606,
    11879,
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
        "id": "cand-5151",
        "type": "archive",
        "expected": "Ponnelle and Bordet, cited publication; title unspecified",
        "name": "L. Ponnelle and L. Bordet, St Philip Neri and the Roman society of his times (London, 1932)",
        "detail": "Bibliography p.434 supplies the title and London 1932 publication data for this earlier citation. The book was not independently consulted.",
    },
    {
        "id": "cand-10513",
        "type": "archive",
        "expected": "Lorenzo da Ponte, p.52 (citation locator in Haskell p.368 note 4)",
        "name": "Lorenzo da Ponte, Memorie (Milano, 1960)",
        "detail": "Bibliography p.434 identifies the work behind Haskell's p.368 note 4 locator. The memoirs and cited page were not independently consulted.",
    },
    {
        "id": "cand-4372",
        "type": "archive",
        "expected": "Pope-Hennessy (1946), cited publication, pp. 186–191; title unspecified",
        "name": "J. Pope-Hennessy, ‘Two portraits of Domenichino’ (Burlington Magazine, 1946, pp. 186–191)",
        "detail": "Bibliography p.434 identifies the article matching the existing 1946, pp.186–191 citation locator. The article was not independently consulted.",
    },
    {
        "id": "cand-5158",
        "type": "archive",
        "expected": "Pope-Hennessy (1948), cited publication, p. 121, no. 1741; title unspecified",
        "name": "J. Pope-Hennessy, Domenichino drawings in the Royal Library at Windsor Castle (London, 1948)",
        "detail": "Bibliography p.434 identifies the book cited for Domenichino drawing no.1741. The book and cited page were not independently consulted.",
    },
    {
        "id": "cand-8652",
        "type": "archive",
        "expected": "Popham and Wilde, 1949, p.14 (citation locator; title pending bibliography review)",
        "name": "A. E. Popham and J. Wilde, Italian drawings of the XV and XVI centuries in the Royal Library at Windsor Castle (London, 1949)",
        "detail": "Bibliography p.434 identifies the book behind the existing p.14 citation locator. The book and cited page were not independently consulted; author identity alignment remains for S3.",
    },
    {
        "id": "cand-6352",
        "type": "archive",
        "expected": "Portoghesi (1955), cited publication; title unspecified",
        "name": "P. Portoghesi, ‘I monumenti borrominiani della Basilica Lateranense’ (Quaderni dell’Istituto di Storia dell’Architettura, Luglio 1955)",
        "detail": "Bibliography p.434 supplies the title and journal details for the existing 1955 citation. The article was not independently consulted.",
    },
    {
        "id": "cand-4326",
        "type": "archive",
        "expected": "Il palazzo, la villa e la chiesa di S. Vincenzo a Bassano (Portoghesi, 1957)",
        "name": "P. Portoghesi, ‘Il palazzo, la villa e la chiesa di S. Vincenzo a Bassano’ (Bollettino d’Arte, 1957, pp. 222–240)",
        "detail": "Bibliography p.434 confirms the article title, journal, year and pages for the existing citation; the tentative author/year match is now textually supported. The article was not independently consulted.",
    },
    {
        "id": "cand-10884",
        "type": "archive",
        "expected": "Posner’s study of Del Monte and the early works of Caravaggio (title unspecified)",
        "name": "Donald Posner, ‘Caravaggio’s homo-erotic early works’ (Art Quarterly, 1971, pp. 301–324)",
        "detail": "Bibliography p.434 identifies the article relevant to Haskell's report of Posner's interpretation. The article was not independently consulted; Posner's personal identity remains unresolved for S3.",
    },
    {
        "id": "cand-4857",
        "type": "archive",
        "expected": "Posse (1925), cited publication; title and locator unspecified",
        "name": "H. Posse, Der römische Maler Andrea Sacchi (Leipzig, 1925)",
        "detail": "Bibliography p.434 supplies the title and place for the existing 1925 citation. The book was not independently consulted.",
    },
    {
        "id": "cand-9455",
        "type": "archive",
        "expected": "H. Posse, Die Staatliche Gemäldegalerie zu Dresden, first section (Dresden and Berlin, 1929; citation locator)",
        "name": "H. Posse, Die Staatliche Gemäldegalerie zu Dresden—Erste Abteilung: Die romanischen Länder (Dresden und Berlin, 1929)",
        "detail": "Bibliography p.434 supplies the full first-section title and publication places for the existing 1929 locator. The book was not independently consulted.",
    },
    {
        "id": "cand-10276",
        "type": "archive",
        "expected": "Posse, 1931 (citation in p.351 note 2)",
        "name": "H. Posse, Die Briefe des Grafen Francesco Algarotti an den sächsischen Hof und seine Bilderkäufe für die Dresdner Gemäldgalerie 1743–1747 (Jahrbuch der Preuszischen Kunstsammlungen, 1931, Beiheft)",
        "detail": "Bibliography p.434 supplies the printed title and supplement details for this 1931 citation candidate. Keep the separate Letter no.8 locator cand-8597 available for S3 comparison; the publication and cited letters were not independently consulted.",
    },
    {
        "id": "cand-9298",
        "type": "archive",
        "expected": "Powell, pp.68-70, 110, 147 (citation locator; title and edition unresolved)",
        "name": "N. Powell, From Baroque to Rococo (London, 1959)",
        "detail": "Bibliography p.434 identifies the book behind the cited pages. The book and cited pages were not independently consulted.",
    },
    {
        "id": "cand-11127",
        "type": "archive",
        "expected": "Giovanni da Pozzo's publication of the full text of Algarotti's will",
        "name": "Giovanni da Pozzo, ‘Il Testamento dell’Algarotti’ (Atti dell’Istituto Veneto di Scienze, Lettere ed Arti, 1963–4, Tomo CXXII, Classe di scienze morali e lettere, pp. 181–192)",
        "detail": "Bibliography p.434 identifies the published text of Algarotti's will, distinct from the 1764 will itself (cand-10333). The journal article was not independently consulted.",
    },
    {
        "id": "cand-4849",
        "type": "archive",
        "expected": "Presenzini, cited publication; title and locator unspecified",
        "name": "A. Presenzini, Vita ed opere del pittore Andrea Camassei (Assisi, 1880)",
        "detail": "Bibliography p.434 supplies the title and publication details for the existing citation. The book and cited passage were not independently consulted.",
    },
    {
        "id": "cand-11212",
        "type": "archive",
        "expected": "Previtali 1964, pp. 153-158 (p.410 note 1; title pending bibliography reconciliation)",
        "name": "G. Previtali, La Fortuna dei Primitivi dal Vasari ai Neoclassici (Torino, 1964)",
        "detail": "Bibliography p.434 identifies the 1964 work behind the p.410, pp.153–158 citation. Keep it separate from ambiguous short citation cand-9509; the cited pages and book were not independently consulted.",
    },
    {
        "id": "cand-11031",
        "type": "archive",
        "expected": "Prinz's analysis of the formation of the Uffizi self-portrait gallery",
        "name": "Wolfram Prinz, Die Sammlung der Selbstbildnisse in den Uffizien—Band I: Geschichte der Sammlung (Berlin, 1971)",
        "detail": "Bibliography p.434 identifies the cited first volume on the history of the Uffizi self-portrait collection. The book was not independently consulted.",
    },
    {
        "id": "cand-11185",
        "type": "archive",
        "expected": "Procacci, Lucia e Ugo, publication cited at p.404 note 2 (title and year unspecified)",
        "name": "Lucia and Ugo Procacci, ‘Il carteggio di Marco Boschini con il Cardinale Leopoldo de’ Medici’ (Saggi e Memorie di storia dell’arte, 4, Venezia, 1965, pp. 85–114)",
        "detail": "Bibliography p.434 identifies the article behind the p.404 note 2 citation. The article was not independently consulted; preserve the source's printed author forms pending S3 identity alignment.",
    },
    {
        "id": "cand-6195",
        "type": "archive",
        "expected": "Prota-Giurleo, cited publication, p. 77",
        "name": "U. Prota-Giurleo, Pittori Napoletani del Seicento (Napoli, 1953)",
        "detail": "Bibliography p.434 identifies the book behind the existing p.77 citation. The book and cited page were not independently consulted.",
    },
    {
        "id": "cand-5598",
        "type": "archive",
        "expected": "La vie et l’œuvre de Claudio Monteverdi (H. Prunières, Paris, 1926)",
        "name": "La vie et l’œuvre de Claudio Monteverdi (H. Prunières, Paris, 1926)",
        "detail": "Bibliography p.434 page-image review confirms the title form l’œuvre; S0 OCR reads l’ceuvre. The 1926 book was not independently consulted.",
    },
    {
        "id": "cand-11065",
        "type": "person",
        "expected": "Puppi (scholar cited by surname on p.405)",
        "detail": "Bibliography p.434 prints the author as Lionelli for the Valmarana article and Lionello for the Cordellina article. Preserve both forms for S3 identity alignment; the p.405 notes now map to distinct publication candidates.",
    },
    {
        "id": "cand-11066",
        "type": "archive",
        "expected": "Puppi research on Valmarana and Cordellina patronage",
        "detail": "This earlier provisional candidate was shared by p.405 notes 5 and 6. Bibliography p.434 identifies two distinct publications, now recorded as cand-11425 and cand-11426, and the p.405 citation/body statements have been remapped. Retain this grouping record for S3 reconciliation rather than treating it as a third publication.",
    },
]

for update in candidate_updates:
    row = candidate_by_id.get(update["id"])
    if not row or row.get("suggested_type") != update["type"]:
        raise SystemExit(f"missing/wrong-type candidate update: {update['id']}")
    if row["canonical_name"] != update["expected"]:
        raise SystemExit(f"candidate pre-state changed: {update['id']}")
    if "name" in update:
        row["canonical_name"] = update["name"]
    row["detail"] = update["detail"]

new_candidate_specs = [
    {
        "id": "cand-11422",
        "name": "Pöllnitz, Baron Charles Louis de, Mémoires contenant les observations qu’il a faites dans ses voyages (3 vols., Liège, 1734)",
        "detail": "Bibliography entry at printed p.434. Keep volume-specific Pöllnitz citation candidates separate for S3; the volumes were not independently consulted.",
        "source_line": 986,
        "related": ["cand-8788", "cand-9330"],
    },
    {
        "id": "cand-11423",
        "name": "Mercedes Precerutti Garberi, ‘Di alcuni dipinti perduti del Tiepolo’ (Commentari, 1958, pp. 110–123)",
        "detail": "Bibliography entry at printed p.434. The article was not independently consulted.",
        "source_line": 1007,
    },
    {
        "id": "cand-11424",
        "name": "G. Previtali, ‘Collezionisti di primitivi nel Settecento’ (Paragone, 1959, no. 113, pp. 3–32)",
        "detail": "Bibliography entry at printed p.434. Keep distinct from the 1964 Previtali book; the p.301 short citation remains ambiguous and is linked only as an S3 comparison. The article was not independently consulted.",
        "source_line": 1009,
        "related": ["cand-9509"],
    },
    {
        "id": "cand-11425",
        "name": "Puppi, Lionelli, ‘I Tiepolo a Vicenza e le statue dei “nani” di Villa Valmarana a S. Bastiano’ (Atti dell’Istituto Veneto di Scienze, Lettere ed Arti, 1967–8, Tomo CXXVI, Classe di scienze morali, lettere ed arti, pp. 211–250)",
        "detail": "Bibliography entry at printed p.434; the author is printed as Lionelli. Its pp.211–250 match p.405 note 5, which gives the year 1968. The article was not independently consulted; retain the printed name variant and prior grouped candidate for S3.",
        "source_line": 1019,
        "related": ["cand-11065", "cand-11066"],
    },
    {
        "id": "cand-11426",
        "name": "Puppi, Lionello, ‘Carlo Cordellina committente d’artisti’ (Arte Veneta, 1968, pp. 212–216)",
        "detail": "Bibliography entry at printed p.434; the author is printed as Lionello. Its title and pp.212–216 match p.405 note 6. The article was not independently consulted; retain the printed name variant and prior grouped candidate for S3.",
        "source_line": 1020,
        "related": ["cand-11065", "cand-11066"],
    },
]

natural_keys = {}
for row in candidates:
    key = (row["canonical_name"].strip().casefold(), row["suggested_type"].casefold())
    natural_keys.setdefault(key, set()).add(row["candidate_id"])
new_candidates = []
for spec in new_candidate_specs:
    candidate_id = spec["id"]
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (spec["name"].strip().casefold(), "archive")
    if natural_keys.get(key):
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {spec['name']}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=spec["name"],
        suggested_type="archive",
        status="open",
        detail=spec["detail"],
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{spec['source_line']}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.setdefault(key, set()).add(candidate_id)


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
    record("cand-11422", 986, 986, "Pöllnitz, Baron Charles Louis de", "Mémoires contenant les observations qu’il a faites dans ses voyages", "3 vols., Liège 1734", "three-volume book", corrections=[{"line": 986, "ocr": "Memories", "print": "Mémoires", "note": "The page image shows the French title with é."}], related=["cand-8788", "cand-9330"]),
    record("cand-5151", 987, 987, "Ponnelle, L. and Bordet, L.", "St Philip Neri and the Roman society of his times", "London 1932", "book"),
    record("cand-10513", 988, 988, "Ponte, Lorenzo da", "Memorie", "Milano 1960", "book", corrections=[{"line": 988, "ocr": "i960", "print": "1960", "note": "The page image reads 1960."}]),
    record("cand-4372", 989, 989, "Pope-Hennessy, J.", "‘Two portraits of Domenichino’", "Burlington Magazine, 1946, pp. 186–191", "journal article", corrections=[{"line": 989, "ocr": "ofDomenichino", "print": "of Domenichino", "note": "The page image has a space between the words."}]),
    record("cand-5158", 990, 991, "Pope-Hennessy, J.", "Domenichino drawings in the Royal Library at Windsor Castle", "London 1948", "book"),
    record("cand-7064", 992, 992, "Pope-Hennessy, J.", "‘Some bronze statues by Francesco Fanelli’", "Burlington Magazine, 1953, pp. 157–162", "journal article"),
    record("cand-8652", 993, 994, "Popham, A. E. and Wilde, J.", "Italian drawings of the XV and XVI centuries in the Royal Library at Windsor Castle", "London 1949", "book", related=["cand-8661", "cand-8662"]),
    record("cand-6352", 995, 995, "Portoghesi, P.", "‘I monumenti borrominiani della Basilica Lateranense’", "Quaderni dell’Istituto di Storia dell’Architettura, Luglio 1955", "journal article"),
    record("cand-4326", 996, 997, "Portoghesi, P.", "‘Il palazzo, la villa e la chiesa di S. Vincenzo a Bassano’", "Bollettino d’Arte, 1957, pp. 222–240", "journal article"),
    record("cand-10884", 998, 998, "Posner, Donald", "‘Caravaggio’s homo-erotic early works’", "Art Quarterly, 1971, pp. 301–324", "journal article", related=["cand-10883"]),
    record("cand-4857", 999, 999, "Posse, H.", "Der römische Maler Andrea Sacchi", "Leipzig 1925", "book"),
    record("cand-9455", 1000, 1001, "Posse, H.", "Die Staatliche Gemäldegalerie zu Dresden—Erste Abteilung: Die romanischen Länder", "Dresden und Berlin 1929", "book"),
    record("cand-10276", 1002, 1002, "Posse, H.", "Die Briefe des Grafen Francesco Algarotti an den sächsischen Hof und seine Bilderkäufe für die Dresdner Gemäldgalerie 1743–1747", "Jahrbuch der Preuszischen Kunstsammlungen, 1931, Beiheft", "journal supplement", related=["cand-8597"], notes=["Preserve the printed spellings Gemäldgalerie and Preuszischen; the listed publication and cited letters were not independently checked."]),
    record("cand-4634", 1003, 1003, "Poussin, Nicolas", "Correspondance publiée d’après les originaux par Ch. Jouanny", "Paris 1911", "book"),
    record("cand-4633", 1004, 1004, "Poussin, Nicolas", "catalogue de l’exposition par Sir Anthony Blunt", "Paris 1960", "exhibition catalogue", corrections=[{"line": 1004, "ocr": "i960", "print": "1960", "note": "The page image reads 1960."}]),
    record("cand-9298", 1005, 1005, "Powell, N.", "From Baroque to Rococo", "London 1959", "book"),
    record("cand-11127", 1006, 1006, "Pozzo, Giovanni da", "‘Il Testamento dell’Algarotti’", "Atti dell’Istituto Veneto di Scienze, Lettere ed Arti, 1963–4, Tomo CXXII (Classe di scienze morali e lettere), pp. 181–192", "journal article", corrections=[{"line": 1006, "ocr": "pp. i8r-i92", "print": "pp. 181–192", "note": "The page image reads 181–192."}]),
    record("cand-11423", 1007, 1007, "Precerutti Garberi, Mercedes", "‘Di alcuni dipinti perduti del Tiepolo’", "Commentari, 1958, pp. 110–123", "journal article"),
    record("cand-4849", 1008, 1008, "Presenzini, A.", "Vita ed opere del pittore Andrea Camassei", "Assisi 1880", "book", corrections=[{"line": 1008, "ocr": "Presenzin!", "print": "Presenzini", "note": "The page image reads Presenzini."}]),
    record("cand-11424", 1009, 1009, "Previtali, G.", "‘Collezionisti di primitivi nel Settecento’", "Paragone, 1959, no. 113, pp. 3–32", "journal article", related=["cand-9509"]),
    record("cand-11212", 1010, 1010, "Previtali, G.", "La Fortuna dei Primitivi dal Vasari ai Neoclassici’", "Torino 1964", "book"),
    record("cand-11031", 1011, 1012, "Prinz, Wolfram", "Die Sammlung der Selbstbildnisse in den Uffizien—Band I: Geschichte der Sammlung", "Berlin 1971", "book"),
    record("cand-11185", 1013, 1013, "Procacci, Lucia & Ugo", "‘Il carteggio di Marco Boschini con il Cardinale Leopoldo de’ Medici’", "Saggi e Memorie di storia dell’arte, 4, 1965, Venezia, pp. 85–114", "journal article", corrections=[{"line": 1013, "ocr": "Luda", "print": "Lucia", "note": "The page image reads Lucia."}]),
    record("cand-6195", 1014, 1014, "Prota-Giurleo, U.", "Pittori Napoletani del Seicento", "Napoli 1953", "book", corrections=[{"line": 1014, "ocr": "double quote before Prota-Giurleo", "print": "no quotation mark; margin scan mark only", "note": "The page image shows a left-margin scan mark, not a leading quotation mark."}]),
    record("cand-4861", 1015, 1015, "Prunières, H.", "L’opéra italien en France avant Lulli", "Paris 1913", "book", corrections=[{"line": 1015, "ocr": "LuUi", "print": "Lulli", "note": "The page image reads Lulli."}]),
    record("cand-5598", 1016, 1016, "Prunières, H.", "La vie et l’œuvre de Claudio Monteverdi", "Paris 1926", "book", corrections=[{"line": 1016, "ocr": "l’ceuvre", "print": "l’œuvre", "note": "The page image shows œuvre."}]),
    record("cand-7846", 1017, 1018, "Puliti, L.", "Cenni storici della vita del serenissimo Ferdinando dei Medici, Gran Principe di Toscana", "Firenze 1875", "book", corrections=[{"line": 1017, "ocr": "Media, Gran Prindpe", "print": "Medici, Gran Principe", "note": "The page image confirms the family name and title."}]),
    record("cand-11425", 1019, 1019, "Puppi, Lionelli", "‘I Tiepolo a Vicenza e le statue dei “nani” di Villa Valmarana a S. Bastiano’", "Atti dell’Istituto Veneto di Scienze, Lettere ed Arti, 1967–8, Tomo CXXVI (Classe di scienze morali, lettere ed arti), pp. 211–250", "journal article", corrections=[{"line": 1019, "ocr": "),,pp.", "print": "), pp.", "note": "The page image has a single comma before pp."}], notes=["The page prints the author's given-name form as Lionelli; retain it for S3 comparison with the next entry, printed Lionello."], related=["cand-11065", "cand-11066"]),
    record("cand-11426", 1020, 1020, "Puppi, Lionello", "‘Carlo Cordellina committente d’artisti’", "Arte Veneta, 1968, pp. 212–216", "journal article", notes=["The page prints the author's given-name form as Lionello, unlike Lionelli in the preceding entry; retain both forms for S3 comparison."], related=["cand-11065", "cand-11066"]),
]

if len(candidate_updates) != 21 or len(new_candidate_specs) != 5 or len(entries) != 29:
    raise SystemExit(
        f"unexpected entry counts: updates={len(candidate_updates)}, "
        f"new_candidates={len(new_candidate_specs)}, entries={len(entries)}"
    )

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


def source_quote(entry):
    return "\n".join(source_lines[entry["start"] - 1 : entry["end"]])


for index, entry in enumerate(entries, start=1):
    candidate_id = entry["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type bibliographic candidate: {candidate_id}")
    for related_id in entry["related"]:
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")

    quote = source_quote(entry)
    positions = [i for i in range(len(segment_text)) if segment_text.startswith(quote, i)]
    if len(positions) != 1:
        raise SystemExit(f"source quote must occur once: {candidate_id} {quote!r}")
    start_char = positions[0]
    end_char = start_char + len(quote)
    mention_id = f"m-chp21-bib-l985-1020-{index:03d}"
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

    statement_id = f"st-chp21-bib-l985-1020-entry-{index:02d}"
    if statement_id in statement_ids:
        raise SystemExit(f"duplicate statement ID: {statement_id}")
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
            "printed_page": 434,
        },
    }
    if entry["corrections"]:
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    if entry["page_image_notes"]:
        qualifiers["page_image_notes"] = entry["page_image_notes"]
    if entry["related"]:
        qualifiers["related_candidate_ids_for_s3"] = entry["related"]
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

# Bibliography p.434 resolves two p.405 footnote locators previously stored as one
# provisional Puppi source. Preserve the old candidate but map citations and body
# mentions to publication-specific archive candidates.
statement_by_id = {row["statement_id"]: row for row in statements}
mention_by_id = {row["mention_id"]: row for row in mentions}
reconciliation_updates = [
    {
        "statement_id": "st-chp20-p405-puppi-corrects-valmarana-fresco-commission",
        "expected_object": "cand-2594",
        "expected_qualification": "The strong wording is Haskell's assessment of Puppi's demonstration. Chapter 9 p.258 says Leonardo seems to have headed the family when the frescoes were painted; it does not itself state that he commissioned them. The cited note 5 remains queued; the fresco cycle is reused from its indexed p.258 candidate.",
        "old_candidate": "cand-11066",
        "new_candidate": "cand-11425",
        "expected_quote": "Pallucchini.3 Of the individual families referred to in this chapter, the patronage of the Zenobio has been looked at in some detail,4 and Puppi has demonstrated beyond the shadow of a doubt that I was quite wrong in attributing to the sweet-tempered and humble Leonardo Valmarana the commissioning of Tiepolo’s frescoes in the family\nVilla near Vicenza illustrating scenes from Homer, Virgil, Ariosto and Tasso. These beautiful works, so different in seeling from those generally produced by Tiepolo for the local nobility, were in fact commissioned by Conte Giustino Valmarana (who died in 1757)—about whom we know little except that he was a very rich, efficient and retiring landowner5 Puppi has also given us new information about the patronage of Carlo Cordellina (another employer of Tiepolo), and especially about the palace in\nVicenza which he began to have built in 1770 at the age of 73 and where he died eighteen years later.6",
        "qualification": "The strong wording is Haskell's assessment of Puppi's demonstration. Chapter 9 p.258 says Leonardo seems to have headed the family when the frescoes were painted; it does not itself state that he commissioned them. The p.405 note 5 now maps to bibliography candidate cand-11425 by the matching pp.211–250 range; the bibliography gives 1967–8 while the note gives 1968. The article was not independently consulted.",
        "note_id": None,
    },
    {
        "statement_id": "st-chp20-p405-cordellina-vicenza-palace",
        "expected_object": "cand-11069",
        "expected_qualification": "The palace has no formal name here; a possible match to the previously described Cordellina house candidate cand-8375 remains unresolved. Note 6 remains queued and the cited source was not independently consulted.",
        "old_candidate": "cand-11066",
        "new_candidate": "cand-11426",
        "expected_quote": "Villa near Vicenza illustrating scenes from Homer, Virgil, Ariosto and Tasso. These beautiful works, so different in seeling from those generally produced by Tiepolo for the local nobility, were in fact commissioned by Conte Giustino Valmarana (who died in 1757)—about whom we know little except that he was a very rich, efficient and retiring landowner5 Puppi has also given us new information about the patronage of Carlo Cordellina (another employer of Tiepolo), and especially about the palace in\nVicenza which he began to have built in 1770 at the age of 73 and where he died eighteen years later.6",
        "qualification": "The palace has no formal name here; a possible match to the previously described Cordellina house candidate cand-8375 remains unresolved. The p.405 note 6 now maps to bibliography candidate cand-11426 by title and pp.212–216. The article was not independently consulted.",
        "note_id": None,
    },
    {
        "statement_id": "st-chp20-p405-n05-citation",
        "expected_object": "cand-11066",
        "expected_qualification": "Short citations only; missing title, edition, and full identity are not inferred. Cited works were not independently consulted.",
        "old_candidate": "cand-11066",
        "new_candidate": "cand-11425",
        "expected_quote": "5 Puppi, 1968, pp. 211-50.",
        "qualification": "Bibliography p.434 identifies the cited article as ‘I Tiepolo a Vicenza e le statue dei “nani” di Villa Valmarana a S. Bastiano’; its printed pp.211–250 match this locator. The printed year forms differ (1967–8 in the bibliography; 1968 in the note). The article was not independently consulted.",
        "note_id": "m-s2-chp20-notes-p405-006",
        "expected_mention": ("Puppi, 1968, pp. 211-50", "1810", "1833"),
    },
    {
        "statement_id": "st-chp20-p405-n06-citation",
        "expected_object": "cand-11066",
        "expected_qualification": "Short citations only; missing title, edition, and full identity are not inferred. Cited works were not independently consulted.",
        "old_candidate": "cand-11066",
        "new_candidate": "cand-11426",
        "expected_quote": "6 Puppi, 1968, pp. 212-16.",
        "qualification": "Bibliography p.434 identifies the cited article as ‘Carlo Cordellina committente d’artisti’; its printed title, year and pp.212–216 match this locator. The article was not independently consulted.",
        "note_id": "m-s2-chp20-notes-p405-008",
        "expected_mention": ("Puppi, 1968, pp. 212-16", "1837", "1860"),
    },
]
for update in reconciliation_updates:
    statement = statement_by_id.get(update["statement_id"])
    if not statement:
        raise SystemExit(f"missing p.405 statement: {update['statement_id']}")
    qualifiers = statement.get("qualifiers") or {}
    if statement.get("object_candidate_id") != update["expected_object"]:
        raise SystemExit(f"p.405 object pre-state changed: {update['statement_id']}")
    if statement.get("original_quote") != update["expected_quote"]:
        raise SystemExit(f"p.405 quote pre-state changed: {update['statement_id']}")
    if qualifiers.get("qualification") != update["expected_qualification"]:
        raise SystemExit(f"p.405 qualification pre-state changed: {update['statement_id']}")
    mentioned = qualifiers.get("mentioned_candidate_ids", [])
    if update["old_candidate"] not in mentioned:
        raise SystemExit(f"p.405 mention list pre-state changed: {update['statement_id']}")
    qualifiers["mentioned_candidate_ids"] = [
        update["new_candidate"] if cid == update["old_candidate"] else cid
        for cid in mentioned
    ]
    qualifiers["qualification"] = update["qualification"]
    qualifiers.setdefault("related_candidate_ids_pending_alignment", [])
    if update["old_candidate"] not in qualifiers["related_candidate_ids_pending_alignment"]:
        qualifiers["related_candidate_ids_pending_alignment"].append(update["old_candidate"])
    statement["qualifiers"] = qualifiers
    if update["note_id"]:
        statement["object_candidate_id"] = update["new_candidate"]
        mention = mention_by_id.get(update["note_id"])
        if not mention or mention.get("candidate_id") != update["old_candidate"]:
            raise SystemExit(f"p.405 mention pre-state changed: {update['note_id']}")
        if (
            mention.get("surface_form"),
            str(mention.get("start_char")),
            str(mention.get("end_char")),
        ) != update["expected_mention"]:
            raise SystemExit(f"p.405 mention quote/offset pre-state changed: {update['note_id']}")
        mention["candidate_id"] = update["new_candidate"]

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
    if statement["original_quote"] != "\n".join(source_lines[start - 1 : end]):
        raise SystemExit(f"statement source-line validation failed: {statement['statement_id']}")

for row in new_mentions:
    start_char, end_char = int(row["start_char"]), int(row["end_char"])
    if segment_text[start_char:end_char] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")
ordered_mentions = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(ordered_mentions, ordered_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mentions: {left['mention_id']} and {right['mention_id']}")

coverage_row["disposition"] = "reviewed"
coverage_row["migration_status"] = "complete"
coverage_row["source_line_ranges"] = "L986-1020"
coverage_row["note"] = (
    "Printed p.434 contains 29 bibliography entries at L986–1020; L985 is only a page marker. "
    "Five archive candidates were added and existing citation candidates were supplemented. "
    "Bibliography p.434 disambiguates the two Puppi p.405 citations by their titles and page ranges."
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
            "p405_reconciled_statements": len(reconciliation_updates),
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
