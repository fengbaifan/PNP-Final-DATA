#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 433."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l928-983"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "df71b743497fc6b4e376cf05c947ac620142e900b5e0ea3ffde3f305a9d36edc"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l883-926"
BACKUP = ".bak-s2-chp21-bibliography-l928-983-20261007"

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
segment_text = "\n".join(source_lines[927:983])
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
    928,
    983,
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
    11391,
    26574,
    11847,
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
        "id": "cand-5533",
        "expected": "Rime, e Satire di Paolo Giordano II, Duca di Bracciano (Bracciano, 1649)",
        "name": "Paolo Giordano II, duca di Bracciano, Rime e Satire (Bracciano, 1649)",
        "detail": "Bibliography p.433 confirms the printed title form Rime e Satire and the 1649 Bracciano edition. The volume was not independently consulted.",
    },
    {
        "id": "cand-10444",
        "expected": "Pamphlet by P. A. Paravia (1829), cited in p.362 note 1",
        "name": "[Paravia, P. A.], Delle lodi dell’Ab. Filippo Farsetti patrizio veneziano (Venezia, 1829)",
        "detail": "Bibliography p.433 supplies the title and place for the existing Paravia 1829 locator. The pamphlet was not independently consulted.",
    },
    {
        "id": "cand-9484",
        "expected": "K. T. Parker, Canaletto drawings in the Royal Library at Windsor Castle (London, 1948; citation locator)",
        "name": "K. T. Parker, Canaletto drawings in the Royal Library at Windsor Castle (London, 1948)",
        "detail": "Bibliography p.433 confirms the title and London 1948 publication data for the existing citation locator. The book and cited pages were not independently consulted.",
    },
    {
        "id": "cand-4376",
        "expected": "Giambattista Passeri, Vite de’ Pittori Scultori et Architetti (Jacob Hess ed., Leipzig and Vienna, 1934)",
        "name": "G. B. Passeri, Vite de’ Pittori Scultori et Architetti dall’anno 1641 sino all’anno 1673 (Jacob Hess ed., Leipzig und Wien, 1934)",
        "detail": "Bibliography p.433 confirms the title span, Jacob Hess edition, and Leipzig/Vienna 1934 publication data for the existing citation candidate. The cited edition was not independently consulted.",
    },
    {
        "id": "cand-4237",
        "expected": "Pastor, volume XIII (edition unspecified)",
        "name": "Pastor, volume XIII (edition unspecified)",
        "detail": "Bibliography p.433 identifies the series as Storia dei Papi dalla fine del medioevo, Italian version by Pio Cenci, Roma 1943, but does not state a volume number. This remains the volume XIII locator from p.64; do not assume it identifies the same volume or edition. Compare with bibliography candidate cand-11414 at S3.",
    },
    {
        "id": "cand-5958",
        "expected": "Patrignani, cited 1948 reference on Camillo Massimi (title unspecified)",
        "name": "A. Patrignani, ‘Una rara medaglia del Card. Camillo Massimi (1620–1678)’ (Rivista italiana di Numismatica, 1948, pp. 92–97)",
        "detail": "Bibliography p.433 supplies the article title, journal, year and pages for this existing 1948 locator. The article was not independently consulted.",
    },
    {
        "id": "cand-4996",
        "expected": "Pecchiai (1952), cited publication; title unspecified",
        "name": "P. Pecchiai, Il Gesù di Roma (Roma, 1952)",
        "detail": "Bibliography p.433 supplies the title and publication place for the existing 1952 reference. The book was not independently consulted.",
    },
    {
        "id": "cand-4575",
        "expected": "Pecchiai (1959), cited publication, pp. 130 ff.; title unspecified",
        "name": "P. Pecchiai, I Barberini (Roma, 1959)",
        "detail": "Bibliography p.433 supplies the title and publication place for the existing 1959 locator. The cited pages and book were not independently consulted.",
    },
    {
        "id": "cand-9285",
        "expected": "Mostra di Pellegrini, 1959, p.15 (citation locator)",
        "name": "Giovanni Antonio Pellegrini, Disegni e Dipinti (exhibition catalogue edited by Alessandro Bettagno, Venezia, 1959)",
        "detail": "Bibliography p.433 identifies the catalogue behind this p.15 citation locator. Keep the p.56 and plate 92 locators cand-9302 and cand-9453 separate for S3; the catalogue was not independently consulted.",
    },
    {
        "id": "cand-10989",
        "expected": "Catalogue of Italian seventeenth-century paintings still in Spain by Perez Sanchez",
        "name": "Alfonso E. Perez Sanchez, Pintura Italiana del S. XVII en España (Madrid, 1965)",
        "detail": "Bibliography p.433 supplies the printed title, author form and publication data for this existing catalogue candidate. The book was not independently consulted.",
    },
    {
        "id": "cand-4369",
        "expected": "Paola della Pergola, collecting study, volumes I–II (1955–1959); title unspecified",
        "name": "Paola della Pergola, Galleria Borghese—I Dipinti (2 vols., Roma, 1955–1959)",
        "detail": "Bibliography p.433 supplies the title and two-volume publication data for the existing citation candidate. The volumes were not independently consulted.",
    },
    {
        "id": "cand-7655",
        "expected": "La basilica di Santa Maria Maggiore in Bergamo (P. Pesenti, 1938)",
        "name": "P. Pesenti, La basilica di Santa Maria Maggiore in Bergamo (Bergamo, 1938)",
        "detail": "Bibliography p.433 confirms the author and publication place for the existing candidate. The book was not independently consulted.",
    },
    {
        "id": "cand-9950",
        "expected": "Petrocchi, 1947 (citation locator)",
        "name": "M. Petrocchi, Razionalismo architettonico e razionalismo storiografico (Roma, 1947)",
        "detail": "Bibliography p.433 supplies the title and publication place for the existing 1947 citation locator. The book was not independently consulted.",
    },
    {
        "id": "cand-11173",
        "expected": "Petrocchi, 1970 publication cited at p.401 note 5, p.158 (title unspecified)",
        "name": "M. Petrocchi, Roma nel Seicento (Bologna, 1970)",
        "detail": "Bibliography p.433 supplies the title and publication place for the existing 1970 citation locator. The book and cited page were not independently consulted.",
    },
    {
        "id": "cand-7835",
        "expected": "La stirpe de’ Medici di Cafaggiolo (G. Pieraccini, 3 vols., Firenze 1925)",
        "name": "G. Pieraccini, La stirpe de’ Medici di Cafaggiolo (3 vols., Firenze, 1925)",
        "detail": "Bibliography p.433 confirms the printed author form, three-volume extent, and Florence 1925 publication data. The cited work was not independently read.",
    },
    {
        "id": "cand-9927",
        "expected": "Pierantoni (citation locator for Giannone’s Venice residence and expulsion)",
        "name": "A. Pierantoni, Lo sfratto di P. Giannone a Venezia (Roma, 1892)",
        "detail": "Bibliography p.433 supplies the title and publication data for the existing Pierantoni citation locator. The book was not independently consulted.",
    },
    {
        "id": "cand-4472",
        "expected": "Mostra di Pietro da Cortona (1956)",
        "name": "Pietro da Cortona (exhibition catalogue curated by A. Marabottini, Cortona and Roma, 1956)",
        "detail": "Bibliography p.433 supplies the curator and places for the existing 1956 exhibition-catalogue candidate. The catalogue was not independently consulted.",
    },
    {
        "id": "cand-9892",
        "expected": "Pignatti, 1960, page 105 (citation locator)",
        "name": "T. Pignatti, Il Museo Correr di Venezia—dipinti del XVII e XVIII secolo (Venezia, 1960)",
        "detail": "Bibliography p.433 identifies the title and scope behind the existing page 105 locator. Keep the different Mariacher catalogue of fourteenth- to sixteenth-century paintings separate; the cited page and catalogues were not independently consulted.",
    },
    {
        "id": "cand-7657",
        "expected": "La decorazione pittorica seicentesca di S. Maria Maggiore (Angelo Pinetti, 1916)",
        "name": "A. Pinetti, ‘La decorazione pittorica seicentesca di S. Maria Maggiore’ (Bollettino della Civica Biblioteca di Bergamo, 1916, pp. 113–142)",
        "detail": "Bibliography p.433 supplies the journal and page range for the existing 1916 citation candidate. The article was not independently consulted.",
    },
    {
        "id": "cand-7695",
        "expected": "Di alcuni quadri settecenteschi di Bergamo e provincia tornati da Roma (Angelo Pinetti, Fiera di Bergamo, 1920)",
        "name": "A. Pinetti, ‘Di alcuni quadri settecenteschi di Bergamo e provincia tornati da Roma’ (La Fiera di Bergamo, 1920)",
        "detail": "Bibliography p.433 confirms the printed author form and periodical for the existing 1920 citation candidate. The article was not independently consulted; no page range is printed.",
    },
    {
        "id": "cand-4547",
        "expected": "Pintard, cited publication, p. 262; title unspecified",
        "name": "R. Pintard, Le libertinage érudit dans la première moitié du XVII siècle (Paris, 1943)",
        "detail": "Bibliography p.433 supplies the title and Paris 1943 publication data for the existing p.262 locator. The cited page and book were not independently consulted.",
    },
    {
        "id": "cand-7949",
        "expected": "La Pittura del Seicento a Venezia (1959 catalogue cited by Haskell)",
        "name": "Pittura del Seicento a Venezia (exhibition catalogue, Venezia, 1959)",
        "detail": "Bibliography p.433 confirms the catalogue form and publication place for the existing citation candidate. The catalogue was not independently consulted.",
    },
    {
        "id": "cand-10872",
        "expected": "Poirier’s publication on the classical/baroque debate (title unspecified)",
        "name": "Maurice Poirier, ‘Pietro da Cortona e il dibattito disegno-colore’ (Prospettiva, 1979, no. 16, pp. 23–30)",
        "detail": "Bibliography p.433 supplies the article title, journal issue and pages for this existing citation candidate. The article was not independently consulted.",
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
    {
        "id": "cand-11413",
        "name": "Lione Pascoli, Vite de’ Pittori, Scultori ed Architetti moderni (vols. I–II; facsimile edition, Roma, 1933)",
        "detail": "Bibliography entry at printed p.433. Related volume-specific citations remain separate for S3. The facsimile set was not independently consulted.",
        "source_line": 932,
    },
    {
        "id": "cand-11414",
        "name": "Ludovico Barone von Pastor, Storia dei Papi dalla fine del medioevo (Italian version by Pio Cenci, Roma, 1943; volume unspecified)",
        "detail": "Bibliography entry at printed p.433. The entry gives no volume number; volume-specific Pastor citations remain separate for S3. The work was not independently consulted.",
        "source_line": 934,
    },
    {
        "id": "cand-11415",
        "name": "Nicolas Claude Fabri de Peiresc, Lettres publiées par P.-Tamizey de Larroque (7 vols., Paris, 1888–1898)",
        "detail": "Bibliography entry at printed p.433. Keep distinct from manuscript correspondence candidates pending S3; the volumes were not independently consulted.",
        "source_line": 941,
    },
    {
        "id": "cand-11416",
        "name": "N. Pevsner, Academies of art, Past and present (Cambridge, 1940)",
        "detail": "Bibliography entry at printed p.433. The book was not independently consulted.",
        "source_line": 951,
    },
    {
        "id": "cand-11417",
        "name": "Nicolas de Pigage, La galerie électorale de Düsseldorf (Bruxelles, 1781)",
        "detail": "Bibliography entry at printed p.433. The book was not independently consulted.",
        "source_line": 956,
    },
    {
        "id": "cand-11418",
        "name": "P. Pirri, ‘Intagliatori Gesuiti Italiani dei Secoli XVI e XVII’ (Archivum Historicum Societatis Jesu, 1952, pp. 3–59)",
        "detail": "Bibliography entry at printed p.433. The article was not independently consulted.",
        "source_line": 968,
    },
    {
        "id": "cand-11419",
        "name": "G. Pisano, ‘L’ultimo prefetto dell’Urbe—Don Taddeo Barberini’ (Roma, 1931, pp. 103–120, 155–164)",
        "detail": "Bibliography entry at printed p.433. The article was not independently consulted.",
        "source_line": 972,
    },
    {
        "id": "cand-11420",
        "name": "Magnus von Platen (editor), Queen Christina of Sweden—documents and studies (Stockholm, 1966)",
        "detail": "Bibliography entry at printed p.433. The edited volume was not independently consulted.",
        "source_line": 975,
    },
    {
        "id": "cand-11421",
        "name": "O. Pollak, Die Kunsttätigkeit unter Urban VIII (2 vols., Wien, 1927 and 1931)",
        "detail": "Bibliography entry at printed p.433. Keep the volume I and II citation candidates separate for S3; the work was not independently consulted.",
        "source_line": 983,
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
    record("cand-5533", 929, 929, "Paolo Giordano II, duca di Bracciano", "Rime e Satire", "Bracciano 1649", "book", corrections=[{"line": 929, "ocr": "Rime e Satira Bracciano 1649", "print": "Rime e Satire, Bracciano 1649", "note": "The page image reads Satire and separates the title from the place with a comma."}]),
    record("cand-10444", 930, 930, "[Paravia, P. A.]", "Delle lodi dell’Ab. Filippo Farsetti patrizio veneziano", "Venezia 1829", "book", related=["cand-10445"]),
    record("cand-9484", 931, 931, "Parker, K. T.", "Canaletto drawings in the Royal Library at Windsor Castle", "London 1948", "book", corrections=[{"line": 931, "ocr": "thè Royal", "print": "the Royal", "note": "The page image has no grave accent."}], related=["cand-9538"]),
    record("cand-11413", 932, 932, "Pascoli, Lione", "Vite de’ Pittori, Scultori ed Architetti moderni", "vols. I, 1730 and II, 1736; facsimile edition published by R. Istituto d’Archeologia e Storia dell’Arte, Roma 1933", "two-volume facsimile edition", related=["cand-4834", "cand-4552"]),
    record("cand-4376", 933, 933, "Passeri, G. B.", "Vite de’ Pittori Scultori et Architetti dall’anno 1641 sino all’anno 1673", "herausgegeben von Jacob Hess, Leipzig und Wien 1934", "book", corrections=[{"line": 933, "ocr": "1Ó41", "print": "1641", "note": "The page image reads 1641."}], notes=["The small trailing scan mark after 1934 is not part of the bibliographic details."]),
    record("cand-11414", 934, 935, "Pastor, Ludovico Barone von", "Storia dei Papi dalla fine del medioevo", "versione italiana di Mons. Prof. Pio Cenci, Roma 1943; volume not stated", "multi-volume work; volume unspecified", related=["cand-4237", "cand-4366", "cand-4836"]),
    record("cand-5958", 936, 938, "Patrignani, A.", "Una rara medaglia del Card. Camillo Massimi (1620–1678)", "Rivista italiana di Numismatica, 1948, pp. 92–97", "journal article", corrections=[{"line": 936, "ocr": "Rivista italiana", "print": "Rivista italiana", "note": "The page image places these words after ‘in’ on the Patrignani entry; the S0 line order is preserved in the quote."}, {"line": 938, "ocr": "Numismatica, di 1948", "print": "di Numismatica, 1948", "note": "The page image restores the journal continuation and removes the displaced ‘di’."}]),
    record("cand-4996", 939, 939, "Pecchiai, P.", "Il Gesù di Roma", "Roma 1952", "book"),
    record("cand-4575", 940, 940, "Pecchiai, P.", "I Barberini", "Roma 1959", "book"),
    record("cand-11415", 941, 942, "Peiresc, Nicolas Claude Fabri de", "Lettres publiées par P.-Tamizey de Larroque", "7 vols., Paris 1888–98", "seven-volume publication", related=["cand-4381"]),
    record("cand-9285", 943, 945, "Pellegrini, Giovanni Antonio", "Disegni e Dipinti", "catalogo della mostra, a cura di Alessandro Bettagno, Venezia 1959", "exhibition catalogue", related=["cand-9302", "cand-9453"]),
    record("cand-10989", 946, 946, "Perez Sanchez, Alfonso E.", "Pintura Italiana del S. XVII en España", "Madrid 1965", "book", corrections=[{"line": 946, "ocr": "Espana", "print": "España", "note": "The page image has ñ."}]),
    record("cand-4369", 947, 947, "Pergola, Paola della", "Galleria Borghese—I Dipinti", "2 vols., Roma 1955–9", "two-volume catalogue"),
    record("cand-7655", 948, 948, "Pesenti, P.", "La basilica di Santa Maria Maggiore in Bergamo", "Bergamo 1938", "book", corrections=[{"line": 948, "ocr": ". Pesenti", "print": "Pesenti", "note": "The leading dot is an OCR artifact; the page image begins the entry at Pesenti."}]),
    record("cand-9950", 949, 949, "Petrocchi, M.", "Razionalismo architettonico e razionalismo storiografico", "Roma 1947", "book"),
    record("cand-11173", 950, 950, "Petrocchi, M.", "Roma nel Seicento", "Bologna 1970", "book"),
    record("cand-11416", 951, 951, "Pevsner, N.", "Academies of art, Past and present", "Cambridge 1940", "book", related=["cand-3537"]),
    record("cand-7835", 952, 952, "Pieraccini, G.", "La stirpe de’ Medici di Cafaggiolo", "3 vols., Firenze 1925", "three-volume book"),
    record("cand-9927", 953, 953, "Pierantoni, A.", "Lo sfratto di P. Giannone a Venezia", "Roma 1892", "book"),
    record("cand-4472", 954, 955, "Pietro da Cortona", "Pietro da Cortona", "mostra a cura di A. Marabottini, Cortona e Roma 1956", "exhibition catalogue", corrections=[{"line": 955, "ocr": "—-mostra", "print": "—mostra", "note": "The page image has a single dash before mostra."}]),
    record("cand-11417", 956, 956, "Pigage, Nicolas de", "La galerie électorale de Düsseldorf", "Bruxelles 1781", "book", related=["cand-9322"]),
    record("cand-9892", 957, 957, "Pignatti, T.", "Il Museo Correr di Venezia—dipinti del XVII e XVIII secolo", "Venezia 1960", "museum catalogue", corrections=[{"line": 957, "ocr": "i960", "print": "1960", "note": "The page image reads 1960."}], related=["cand-10704"]),
    record("cand-7657", 958, 961, "Pinetti, A.", "La decorazione pittorica seicentesca di S. Maria Maggiore", "Bollettino della Civica Biblioteca di Bergamo, 1916, pp. 113–142", "journal article", notes=["The source places ‘Bollettino della Civica’ at L958 before the author line; the page image shows it as the journal continuation after the title."]),
    record("cand-7695", 962, 965, "Pinetti A.", "Di alcuni quadri settecenteschi di Bergamo e provincia tornati da Roma", "La Fiera di Bergamo, 1920", "journal article", corrections=[{"line": 963, "ocr": "Pinetti A:,. ", "print": "Pinetti A.", "note": "The page image has no comma after the initial and no trailing punctuation before the colon."}], notes=["The source places ‘La’ at L962 before the author line; the page image shows it after ‘in’ in this entry."]),
    record("cand-4547", 966, 966, "Pintard, R.", "Le libertinage érudit dans la première moitié du XVII siècle", "Paris 1943", "book"),
    record("cand-11418", 967, 970, "Pirri, P.", "Intagliatori Gesuiti Italiani dei Secoli XVI e XVII", "Archivum Historicum Societatis Jesu, 1952, pp. 3–59", "journal article", notes=["The journal-title fragments at L967 and L969 are displaced around the Pirri entry in S0; the page image confirms one continuous journal title."]),
    record("cand-11419", 971, 972, "Pisano, G.", "L’ultimo prefetto dell’Urbe—Don Taddeo Barberini", "Roma, 1931, pp. 103–120 and 155–164", "journal article", corrections=[{"line": 972, "ocr": "~ Pisano", "print": "Pisano", "note": "The leading mark is a scan artifact at the left margin."}], notes=["The source line ‘Roma,’ at L971 is a continuation displaced before the author by OCR; the page image places it after ‘in’ in this entry."]),
    record("cand-7949", 973, 974, "", "Pittura del Seicento a Venezia", "catalogo della mostra, Venezia 1959", "exhibition catalogue"),
    record("cand-11420", 975, 976, "von Platen, Magnus (editor)", "Queen Christina of Sweden—documents and studies", "Stockholm 1966", "edited book", related=["cand-11179"]),
    record("cand-10872", 977, 978, "Poirier, Maurice", "Pietro da Cortona e il dibattito disegno-colore", "Prospettiva, 1979 (16), pp. 23–30", "journal article", corrections=[{"line": 978, "ocr": "pp. 23-30. ,", "print": "pp. 23–30.", "note": "The page image has a terminal period and no following comma."}], related=["cand-10871"]),
    record("cand-4359", 979, 982, "Pollak, O.", "Italienische Künstlerbriefe aus der Barockzeit", "Jahrbuch der Königlich-Preuszischen Kunstsammlungen, 1913—Beiheft", "journal supplement", notes=["The journal title and supplement designation are split across L979–982 in S0; the page image confirms one continuous entry."]),
    record("cand-11421", 983, 983, "Pollak, O.", "Die Kunsttätigkeit unter Urban VIII", "2 vols., Wien 1927 and 1931", "two-volume book", related=["cand-4556", "cand-4550"]),
]

if len(candidate_updates) != 23 or len(new_candidate_specs) != 9 or len(entries) != 32:
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
    mention_id = f"m-chp21-bib-l928-983-{index:03d}"
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

    statement_id = f"st-chp21-bib-l928-983-entry-{index:02d}"
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
            "printed_page": 433,
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
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        }
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
coverage_row["source_line_ranges"] = "L929-983"
coverage_row["note"] = (
    "Printed p.433 contains 32 bibliography entries; [Page 433] at L928 is only a page marker. "
    "Reused existing archive candidates where a matching citation was already recorded and added nine "
    "publication candidates. The page image restores several OCR-displaced journal-title fragments."
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
