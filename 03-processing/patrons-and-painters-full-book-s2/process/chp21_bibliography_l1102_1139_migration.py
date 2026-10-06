#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 437."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l1102-1139"
SEGMENT_SHA = "f5cc60e16449f246c3cb146f18134a2fabb3bdeaab126afc880e595b26fef707"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l1059-1100"
BACKUP_SUFFIX = ".bak-s2-chp21-bibliography-l1102-1139-20261007"

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


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if sha256(SOURCE) != SOURCE_SHA or sha256(PDF) != PDF_SHA:
    raise SystemExit("bibliography Markdown or PDF changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1101:1139])
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
) != (SOURCE_FILE, 1102, 1139, SEGMENT_SHA, SOURCE_SHA):
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
    11411,
    26687,
    11960,
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
        "id": "cand-10322", "type": "archive",
        "expected": "Unidentified work by G. A. Selva on Algarotti’s collection (p.355 note 3 citation)",
        "name": "G. A. Selva, Catalogo dei quadri dei disegni e dei libri che trattano dell’arte del disegno della galleria del fu Sig. Conte Algarotti in Venezia (Venezia, [1776])",
        "detail": "Printed p.437 supplies the title and bracketed date for the earlier p.355 note 3 Selva locator. The bibliography record is a strong possible match, but the cited publication was not independently consulted; retain the bibliography-to-locator link for S3 confirmation.",
    },
    {
        "id": "cand-10447", "type": "archive",
        "expected": "Giovanni Sforza’s 1911 article on Filippo Farsetti and the family (pp.153–195)",
        "name": "Giovanni Sforza, ‘Il testamento d’un bibliofilo e la famiglia Farsetti di Venezia’ (Memorie della R. Accademia delle Scienze di Torino, 2a serie, vol. 61, 1911, pp. 153–195)",
        "detail": "Printed p.437 supplies the article title, journal, series, volume, year, and page range for the p.362 note 1 citation already represented here. The article and cited pages were not independently consulted; the author candidate remains subject to S3 identity alignment.",
    },
    {
        "id": "cand-11077", "type": "archive",
        "expected": "Shipley's article on hostility toward Amigoni",
        "name": "John B. Shipley, ‘Ralph, Ellys, Hogarth, and Fielding: The Cabal against Jacopo Amigoni’ (Eighteenth-Century Studies, University of California, vol. I, no. 4, June 1968, pp. 313–331)",
        "detail": "Printed p.437 supplies the complete article citation for the p.405 note 9 reference. The article and cited pages were not independently consulted; author identity alignment remains for S3 with cand-11076.",
    },
    {
        "id": "cand-8773", "type": "archive",
        "expected": "Etienne de Silhouette, volume I, p.156 (citation locator; title pending)",
        "name": "Étienne de Silhouette, Voyage de France, d’Espagne, de Portugal et d’Italie du 22 Avril 1729 au 6 Février 1730 (Paris, 1770)",
        "detail": "Printed p.437 identifies the title, itinerary dates, and Paris 1770 publication for the p.268 note 1 volume-I locator. The bibliography entry appears to identify that work, but its cited page was not consulted; confirm the precise volume mapping in S3. The printed author heading has an irregular bracket at the start of the surname, preserved in the statement’s page-image note.",
    },
    {
        "id": "cand-9066", "type": "archive",
        "expected": "Siren, pp. 103 ff. (citation locator in p.293 note 1)",
        "name": "O. Sirén, Dessins et tableaux italiens de la Renaissance dans les collections de Suède (Stockholm, 1902)",
        "detail": "Printed p.437 supplies the title and Stockholm 1902 details for the p.293 note 1 and p.304 note 6 Sirén locators. These appear to match the single bibliography entry, but cited pages were not independently consulted; retain the provisional S3 alignment with author candidate cand-9446.",
    },
    {
        "id": "cand-5502", "type": "archive",
        "expected": "Skippon, p. 650, cited publication; title and edition unspecified",
        "name": "Philip Skippon, ‘An account of a journey through parts of the Low Countries, Germany, Italy and France’ in A Collection of Voyages and Travels, vol. VI (London, 1752), pp. 359–736",
        "detail": "Printed p.437 identifies the work and its extent, which includes the previously cited p.650 locator. The separate p.679 and p.676 Skippon locators (cand-5687 and cand-6455) remain separate until S3 confirms their identity; neither the collection nor cited pages was independently consulted. The index person candidate is cand-2438.",
    },
    {
        "id": "cand-8330", "type": "archive",
        "expected": "Tabacco publication, page 38, cited on p.254 note 5",
        "name": "G. Tabacco, Andrea Tron e la crisi dell’aristocrazia senatoria a Venezia (Trieste, 1957)",
        "detail": "Printed p.437 supplies a likely full title match for the p.254 note 5, p.38 locator. The other Tabacco locators remain separate candidates cand-8774 (p.123) and cand-10477 (pp.32 ff.) pending S3 identity alignment; the cited publication and pages were not independently consulted.",
    },
    {
        "id": "cand-9314", "type": "archive",
        "expected": "H. Clifford Smith, p.26 (citation locator; work unresolved)",
        "name": "H. Clifford Smith, Buckingham Palace (London, 1930)",
        "detail": "Printed p.437 supplies the title, place, and year for the p.280 note 8 page-26 locator. The entry is a likely match, but the cited page and book were not independently consulted.",
    },
    {
        "id": "cand-11172", "type": "archive",
        "expected": "Sotheby's 1979 publication cited at p.401 note 4, pp. 31-2 (title unspecified)",
        "name": "Sotheby’s, An Exhibition of Old Master Drawings and European Bronzes from the Collection of Charles Rogers (1771–1784) and the William Cotton Bequest, on loan from The City Museum and Art Gallery, Plymouth (1979)",
        "detail": "Printed p.437 supplies the exhibition-publication title for the p.401 note 4b reference to pp.31–32. The publication candidate remains distinct from Sotheby’s institution cand-9307; neither the publication nor cited pages was independently consulted.",
    },
    {
        "id": "cand-10882", "type": "archive",
        "expected": "Luigi Spezzaferro’s study of Del Monte’s cultural formation and Caravaggio patronage (title unspecified)",
        "name": "Luigi Spezzaferro, ‘La cultura del Cardinal Del Monte e il primo tempo del Caravaggio’ (Storia dell’Arte, 1971, pp. 57–92)",
        "detail": "Printed p.437 supplies the full article citation for the p.397 note 11 short reference. This identifies the publication record only; the article and pages were not independently consulted, and it does not independently substantiate Haskell’s report about its interpretation.",
    },
    {
        "id": "cand-6395", "type": "archive",
        "expected": "Voyage d'Italie fait aux annees 1675 et 1676, vol. I (Jacob Spon and George Wheler; cited p. 232)",
        "name": "Jacob Spon and George Wheler, Voyage d’Italie . . . fait aux années 1675 et 1676 (2 vols., La Haye, 1724)",
        "detail": "Printed p.437 identifies the title and two-volume 1724 edition for the existing volume-I p.232/p.236 travel-account locators. The spaced ellipsis is printed in the title; cited pages were not independently consulted. Retain the source’s author spelling Wheler, not the OCR variant Wilder.",
    },
    {
        "id": "cand-11195", "type": "archive",
        "expected": "Strocchi publication cited at p.404 note 12 (title and year unspecified)",
        "name": "Maria Letizia Strocchi, ‘Il Gabinetto d’“opere in piccolo” del Gran Principe Ferdinando a Poggio a Caiano’ (Paragone, 1975, no. 309, pp. 115–126; 1976, no. 311, pp. 83–116)",
        "detail": "Printed p.437 identifies a two-part Strocchi bibliography entry that may match the p.404 note 12 reference and author mention; this is not yet an S3 identity decision. Neither article nor cited pages was independently consulted. The page image reads Strocchi, Maria Letizia; OCR reads Stracchi.",
    },
    {
        "id": "cand-5150", "type": "archive",
        "expected": "Strong, cited publication; title unspecified",
        "name": "E. Strong, La Chiesa Nuova (S. Maria in Vallicella) (Roma, 1923)",
        "detail": "Printed p.437 supplies the title and place/year for the p.68 note 2 Strong citation. The publication is one of the two works Haskell says informed his account of Chiesa Nuova’s early history; the book and cited passages were not independently consulted.",
    },
    {
        "id": "cand-9291", "type": "person",
        "expected": "Sensier (surname-only author cited in p.277 note 4)",
        "detail": "The p.437 bibliography prints the author form A. Sensier for a 1865 Rosalba Carriera publication. Whether this is the author behind the separate Sensier citation locators remains an S3 comparison; do not infer identity solely from surname.",
    },
    {
        "id": "cand-11076", "type": "person",
        "expected": "Shipley (writer cited by surname on p.405)",
        "detail": "The p.437 bibliography gives the author form John B. Shipley for the article about hostility toward Jacopo Amigoni. The article match is strong; personal identity alignment remains for S3.",
    },
    {
        "id": "cand-9446", "type": "person",
        "expected": "O. Sirén (author cited as Sirén in p.293 note 1)",
        "detail": "The p.437 bibliography prints O. Sirén as author of the 1902 Stockholm volume. The title likely identifies the cited p.103 ff. and p.107 locators; author identity remains for S3.",
    },
    {
        "id": "cand-11041", "type": "person",
        "expected": "Strocchi (scholar cited by surname on p.404)",
        "detail": "The p.437 page image gives the byline Maria Letizia Strocchi for a two-part article on the Gran Prince Ferdinando’s collection. It may identify the p.404 surname-only reference, but that mapping remains for S3; OCR’s Stracchi spelling is corrected from the page image.",
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
        "id": "cand-11433",
        "name": "A. Sensier, Le journal de Rosalba Carriera pendant son séjour à Paris en 1720 et 1721 (Paris, 1865)",
        "detail": "Bibliography entry at printed p.437. The book and its contents were not independently consulted. Compare with earlier Sensier and letter/document citation candidates in S3; no specific note-to-entry mapping is claimed here.",
        "source_line": 1104,
    },
    {
        "id": "cand-11434",
        "name": "Third Earl of Shaftesbury, Second Characters or The Language of Forms (edited by Benjamin Rand, Cambridge, 1914)",
        "detail": "Bibliography entry at printed p.437. This is the 1914 edited edition record, distinct from the abstract work candidate cand-6220; author and work alignment are retained for S3. The edition was not independently consulted.",
        "source_line": 1110,
    },
    {
        "id": "cand-11435",
        "name": "G. Spini, Ricerca dei libertini (Roma, 1950)",
        "detail": "Bibliography entry at printed p.437. The book was not independently consulted. Compare with person candidate cand-6375 and separate Spini/Limentani publication candidate cand-6377 in S3; no identity or work merge is asserted.",
        "source_line": 1127,
    },
    {
        "id": "cand-11436",
        "name": "Stuffmann, ‘Les tableaux de la collection de Pierre Crozat’ (Gazette des Beaux-Arts, 1968, pp. 11–144 as printed)",
        "detail": "Bibliography entry at printed p.437. The printed page range is transcribed as 11–144; institutional bibliography records give differing extents, so preserve the book’s form for S3 review. The article was not independently consulted.",
        "source_line": 1136,
    },
]

natural_keys = {}
for row in candidates:
    key = (row["canonical_name"].strip().casefold(), row["suggested_type"])
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
    record("cand-10322", 1103, 1103, "[Selva, G. A.]", "Catalogo dei quadri dei disegni e dei libri che trattano dell’arte del disegno della galleria del fu Sig. Conte Algarotti in Venezia", "Venezia [1776]", "catalogue", notes=["The author heading and date are bracketed in print. Possible match to the p.355 note 3 locator; confirm in S3.", "Accents and punctuation in the title are retained as printed; the catalogue was not independently consulted."], related=["cand-10321"]),
    record("cand-11433", 1104, 1105, "A. Sensier", "Le journal de Rosalba Carriera pendant son séjour à Paris en 1720 et 1721", "Paris 1865", "book", related=["cand-9290", "cand-9291", "cand-9333", "cand-9341"]),
    record("cand-10447", 1106, 1107, "G. Sforza", "‘Il testamento d’un bibliofilo e la famiglia Farsetti di Venezia’", "Memorie della R. Accademia delle Scienze di Torino, 2a serie, vol. 61, 1911, pp. 153–195", "journal article", corrections=[{"line": 1107, "ocr": "voi. 61", "print": "vol. 61", "note": "The page image reads vol. 61; OCR confuses the l with i."}]),
    record("cand-7847", 1108, 1109, "Bernardo Sansone Sgrilli", "Descrizione della Regia Villa, Fontane e Fabbriche di Pratolino", "Firenze 1742", "book"),
    record("cand-11434", 1110, 1111, "Shaftesbury, Third Earl of", "Second Characters or The Language of Forms", "edited by Benjamin Rand, Cambridge 1914", "edited work edition", notes=["A stray apostrophe after 1914 in the OCR/source transcription is not part of the printed entry."], related=["cand-2426", "cand-6220"]),
    record("cand-11077", 1112, 1113, "John B. Shipley", "‘Ralph, Ellys, Hogarth, and Fielding: The Cabal against Jacopo Amigoni’", "Eighteenth-Century Studies (University of California), vol. I, no. 4, June 1968, pp. 313–331", "journal article", corrections=[{"line": 1113, "ocr": "3I3-33I-,", "print": "313–331", "note": "The page image reads 313–331; OCR confuses 1 with I and includes a trailing scan mark."}], related=["cand-11076"]),
    record("cand-8773", 1114, 1115, "S[ilhouette, Étienne de]", "Voyage de France, d’Espagne, de Portugal et d’Italie du 22 Avril 1729 au 6 Février 1730", "Paris 1770", "book", notes=["The page image prints the anomalous heading S[ilhouette, Étienne de]; preserve the bracket placement in this transcription. The p.268 volume-I locator is a likely, not independently verified, match."]),
    record("cand-9066", 1116, 1117, "O. Sirén", "Dessins et tableaux italiens de la Renaissance dans les collections de Suède", "Stockholm 1902", "book", notes=["The title and bibliographic locator appear to match the cited Sirén references, but pp.103 ff. and p.107 were not consulted."], related=["cand-9446"]),
    record("cand-5502", 1118, 1118, "Philip Skippon", "An account of a journey through parts of the Low Countries, Germany, Italy and France", "in A Collection of Voyages and Travels, vol. VI, London 1752, pp. 359–736", "travel account in edited collection", corrections=[{"line": 1118, "ocr": "359736", "print": "359–736", "note": "The page image shows the range 359–736."}], notes=["Pages 650, 676, and 679 fall within the printed range; the separate citation candidates remain for S3 comparison."], related=["cand-2438", "cand-5687", "cand-6455"]),
    record("cand-7600", 1119, 1119, "S. Slive", "Rembrandt and his critics 1630–1730", "The Hague 1953", "book"),
    record("cand-9314", 1120, 1120, "H. Clifford Smith", "Buckingham Palace", "London 1930", "book", notes=["Possible match to the p.280 note 8 p.26 locator; cited page not consulted."]),
    record("cand-5592", 1121, 1121, "A. Solerti", "Musica, Ballo e Drammatica alla Corte Medicea dal 1600 al 1637", "Firenze 1905", "book"),
    record("cand-5160", 1122, 1123, "Raffaello Soprani", "Vite de’ Pittori, Scultori ed Architetti Genovesi", "in questa seconda edizione rivedute accresciute ed arrichite di note da Carlo Giuseppe Ratti, 2 vols., Genova 1768", "book", notes=["The two-volume second edition is recorded as printed. Neither volume nor cited page was independently consulted."]),
    record("cand-11172", 1124, 1125, "Sotheby’s", "An Exhibition of Old Master Drawings and European Bronzes from the Collection of Charles Rogers (1771–1784) and the William Cotton Bequest", "on loan from The City Museum and Art Gallery, Plymouth 1979", "exhibition catalogue", notes=["The publication candidate is separate from the named Sotheby’s institution. Possible match to p.401 note 4b, pp.31–32; cited pages not consulted."], related=["cand-9307"]),
    record("cand-10882", 1126, 1126, "Luigi Spezzaferro", "‘La cultura del Cardinal Del Monte e il primo tempo del Caravaggio’", "Storia dell’Arte, 1971, pp. 57–92", "journal article", notes=["The article is identified from the bibliography; its interpretation and cited pages were not independently consulted.", "The trailing dash marks after the page range in the OCR are scan artifacts, not part of the entry."]),
    record("cand-11435", 1127, 1127, "G. Spini", "Ricerca dei libertini", "Roma 1950", "book", related=["cand-6375", "cand-6377"]),
    record("cand-6395", 1128, 1129, "Jacob Spon et George Wheler", "Voyage d’Italie . . . fait aux années 1675 et 1676", "2 vols., La Haye 1724", "book", notes=["The spaced ellipsis is printed in the title. Existing volume-I p.232/p.236 citations remain unverified."], related=["cand-6396"]),
    record("cand-7867", 1130, 1130, "K. Steinbart", "‘Die Gemalten Schwänke des Pfarrers Arlotto’", "Pantheon, 1936, pp. 233–234", "journal article"),
    record("cand-7030", 1131, 1131, "C. Sterling", "‘Gentileschi in France’", "Burlington Magazine, 1958, pp. 112–120", "journal article"),
    record("cand-7048", 1132, 1132, "L. Stone", "‘The market for Italian art’", "Past and Present, 1959, pp. 92–94", "journal article"),
    record("cand-11195", 1133, 1134, "Strocchi, Maria Letizia", "‘Il Gabinetto d’‘opere in piccolo’ del Gran Principe Ferdinando a Poggio a Caiano’", "Paragone, 1975 (309), pp. 115–126 and 1976 (311), pp. 83–116", "two-part journal publication", corrections=[{"line": 1133, "ocr": "Stracchi", "print": "Strocchi", "note": "The page image clearly reads Strocchi."}, {"line": 1134, "ocr": "(zìi)", "print": "(311)", "note": "The page image reads issue 311."}], notes=["Two-year/issue entry under one bibliography item; possible match to p.404 note 12 remains for S3."], related=["cand-11041"]),
    record("cand-5150", 1135, 1135, "E. Strong", "La Chiesa Nuova (S. Maria in Vallicella)", "Roma 1923", "book"),
    record("cand-11436", 1136, 1136, "Stuffmann", "‘Les tableaux de la collection de Pierre Crozat’", "Gazette des Beaux-Arts, 1968, pp. 11–144 as printed", "journal article", corrections=[{"line": 1136, "ocr": "II-144", "print": "11–144", "note": "The page image shows 11–144; institutional records consulted give differing extents, so the source’s printed range is retained without normalization."}], notes=["National Gallery of Art bibliography records consulted during review differ on pagination (5–142; 11–143; 1–144), while the book bibliography prints 11–144. Preserve the book entry and leave the extent discrepancy for later reconciliation; the article was not independently consulted."]),
    record("cand-7268", 1137, 1138, "J. E. Sweetman", "‘Shaftesbury’s last commission’", "Journal of the Warburg and Courtauld Institutes, 1956, pp. 110–116", "journal article", corrections=[{"line": 1138, "ocr": "no-116", "print": "110–116", "note": "The page image reads 110–116."}]),
    record("cand-8330", 1139, 1139, "G. Tabacco", "Andrea Tron e la crisi dell’aristocrazia senatoria a Venezia", "Trieste 1957", "book", notes=["Possible match to the p.254 note 5 p.38 locator; other Tabacco locators remain separate for S3."], related=["cand-8774", "cand-10477"]),
]

if len(candidate_updates) != 17 or len(new_candidates) != 4 or len(entries) != 25:
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
        raise SystemExit(f"source quote must occur once: {candidate_id} L{item['start']}")
    start_char = positions[0]
    end_char = start_char + len(quote)
    mention_id = f"m-chp21-bib-l1102-1139-{index:03d}"
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

    statement_id = f"st-chp21-bib-l1102-1139-entry-{index:02d}"
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
            "printed_page": 437,
            "pdf_physical_page": 27,
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

if covered_lines != set(range(1103, 1140)):
    raise SystemExit(f"bibliography lines not covered exactly: {sorted(set(range(1103, 1140)) - covered_lines)}")
if len(new_mentions) != 25 or len(new_statements) != 25:
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
    source_line_ranges="L1103-1139",
    note="Printed p.437: 25 publication records reviewed; see process/stages.md.",
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
    "candidate_count": 11415,
    "mention_count": 26712,
    "statement_count": 11985,
    "coverage_complete": 612,
    "coverage_queued": 99,
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
