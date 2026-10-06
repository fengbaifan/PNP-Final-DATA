#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 430."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l808-844"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "131ae7f4f6fa83793cb668be24ea5028f7a809b1923353bc729989be7ab723ec"
BACKUP = ".bak-s2-chp21-bibliography-l808-844-20261007"
TARGET_SEGMENT = "chp-21:21_CHP-21Bibliography:l846-881"

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
segment_text = "\n".join(source_lines[807:844])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text/hash changed")
segment_row = next((row for row in read_jsonl(SEGMENTS) if row.get("segment_id") == SEGMENT), None)
if not segment_row or (
    segment_row.get("source_file"),
    segment_row.get("line_start"),
    segment_row.get("line_end"),
    segment_row.get("sha256"),
    segment_row.get("asset_sha256"),
) != (
    "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    808,
    844,
    SEGMENT_SHA,
    SOURCE_SHA,
):
    raise SystemExit("source segment manifest changed")
target_row = next(
    (row for row in read_jsonl(SEGMENTS) if row.get("segment_id") == TARGET_SEGMENT), None
)
if not target_row or not (target_row["line_start"] <= 861 <= target_row["line_end"]):
    raise SystemExit("Molinier cross-reference target segment changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)

if (len(candidates), len(mentions), len(statements), len(coverage)) != (
    11378,
    26487,
    11761,
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
target_coverage = coverage_by_id.get(TARGET_SEGMENT)
if not target_coverage or (target_coverage["disposition"], target_coverage["migration_status"]) != (
    "queued",
    "pending",
):
    raise SystemExit("Molinier cross-reference target is no longer queued")

candidate_updates = [
    {
        "id": "cand-5979",
        "expected": "Michaelis, cited publication p.50; title and year unspecified",
        "name": "A. Michaelis, Ancient marbles in Great Britain (Cambridge, 1882)",
        "detail": "Printed p.430 supplies the title and publication data for this existing p.50 locator. The book and cited page were not independently consulted.",
    },
    {
        "id": "cand-6571",
        "expected": "Michaud, Louis XIV et Innocent XI, vol. I (1882–83), pp. 68, 176",
        "name": "E. Michaud, Louis XIV et Innocent XI (4 vols., Paris, 1882–1883)",
        "detail": "Printed p.430 identifies the four-volume work corresponding to the existing volume-I locators. Preserve those cited pages in their statements; the work was not independently consulted.",
    },
    {
        "id": "cand-7768",
        "expected": "Unidentified D. Miller publication from 1958",
        "name": "D. Miller, ‘Per Giuseppe Gambarini’ (Arte Antica e Moderna, 1958, pp. 390–393)",
        "detail": "Printed p.430 supplies the title and periodical details for the existing 1958 locator. The article was not independently consulted.",
    },
    {
        "id": "cand-6607",
        "expected": "Miller (1960), cited publication, p. 530 (title unspecified)",
        "name": "D. Miller, ‘An unpublished letter by Giuseppe Maria Crespi’ (Burlington Magazine, 1960, pp. 530–531)",
        "detail": "Printed p.430 supplies the title and full page range for the existing p.530 locator. The article was not independently consulted; OCR joins its final page to the next Miller entry.",
    },
    {
        "id": "cand-7757",
        "expected": "Unidentified D. Miller publication from 1963",
        "name": "D. Miller, ‘The Gallery of Aeneid in the Palazzo Bonaccorsi at Macerata’ (Arte Antica e Moderna, 1963, pp. 153–158; 1964, p. 113)",
        "detail": "Printed p.430 links the 1963 and 1964 locators under one title; keep the existing 1964 citation candidate cand-7758 separate for S3 to determine whether these are installments or related publications. Neither citation was independently consulted.",
    },
    {
        "id": "cand-6361",
        "expected": "Missirini, cited publication at p.116; title and edition unspecified",
        "name": "Melchior Missirini, Memorie per servire alla storia della Romana Accademia di S. Luca (Roma, 1823)",
        "detail": "Printed p.430 supplies the title and edition date for the existing p.116 locator. The cited passage and book were not independently consulted.",
    },
    {
        "id": "cand-6457",
        "expected": "Misson, 1717, vol. II, p. 167, cited publication (title unspecified)",
        "name": "Maximilien Misson, Nouveau Voyage d’Italie (4ème édition, 4 vols., La Haye, 1717–1722)",
        "detail": "Printed p.430 supplies the title, edition, volume count and date range for the existing volume-II locator. The cited passage was not independently consulted.",
    },
    {
        "id": "cand-5873",
        "expected": "Mitchell article (1938), cited for Flight into Egypt representations",
        "name": "C. Mitchell, ‘Poussin’s “Flight into Egypt”’ (Journal of the Warburg and Courtauld Institutes, I, 1937–1938, pp. 340–343)",
        "detail": "Printed p.430 supplies the article title, periodical and pages for the existing 1938 citation. The article was not independently consulted.",
    },
    {
        "id": "cand-8510",
        "expected": "Sebastiano Molino, Orazione in lode di Marco Foscarini Procurator di S. Marco",
        "name": "Sebastiano Molino, Orazione in lode di Marco Foscarini Procurator di S. Marco (in G. A. Molin, Orazioni, elogj e vite scritte da letterati veneti patrizj, Venezia, 1795)",
        "detail": "Printed p.430 identifies the collected volume containing the already cited oration. Preserve the bracketed ‘G. A. Molin’ attribution as printed; the volume was not independently consulted.",
    },
    {
        "id": "cand-9818",
        "expected": "Molmenti, 1908, vol. III, pp. 45-46",
        "name": "P. Molmenti, La storia di Venezia nella vita privata (3 vols., Bergamo, 1908)",
        "detail": "Printed p.430 identifies the three-volume work behind the existing volume-III locator. The cited pages were not independently consulted.",
    },
    {
        "id": "cand-8326",
        "expected": "Molmenti 1909, pages 177-188, cited on p.254 note 2",
        "name": "P. Molmenti, ‘Il Palazzo Grassi a Venezia e un affresco attribuito a Tiepolo’ (Emporium, 1909, XXIX, pp. 177–188)",
        "detail": "Printed p.430 supplies the article title and issue for the existing 1909 pages 177–188 citation. The article was not independently consulted.",
    },
    {
        "id": "cand-8116",
        "expected": "Molmenti 1919 publication cited for the origins of the Venetian travel law",
        "name": "P. Molmenti, ‘Le relazioni tra patrizi veneziani e diplomatici stranieri’ (in Curiosità di Storia Veneziana, Bologna, 1919)",
        "detail": "Printed p.430 supplies the title and collection details for the existing 1919 citation. The cited pages were not independently consulted.",
    },
    {
        "id": "cand-10475",
        "expected": "P. Molmenti, ‘Un nobil huomo veneziano del secolo XVIII’, n.d. (p.364 note 4 citation locator)",
        "name": "P. Molmenti, ‘Un nobil huomo veneziano del secolo XVIII’ (in Epistolari veneziani del secolo XVIII, Milano, n.d.)",
        "detail": "Printed p.430 supplies the containing volume and place for the existing undated citation. The source does not supply a publication year; cited pages were not independently consulted.",
    },
    {
        "id": "cand-4853",
        "expected": "Jennifer Montagu (1968), cited article; title unspecified",
        "name": "Jennifer Montagu, ‘The painted enigma and French seventeenth-century art’ (Journal of the Warburg and Courtauld Institutes, 1968, pp. 307–335)",
        "detail": "Printed p.430 supplies the title, periodical and pages for the existing 1968 article locator. The article was not independently consulted.",
    },
    {
        "id": "cand-6355",
        "expected": "Montalto, cited work at pp.267–302; title and author unresolved",
        "name": "L. Montalto, ‘Gli affreschi del Palazzo Pamphilj in Valmontone’ (Commentari, 1955, pp. 267–302)",
        "detail": "Printed p.430 supplies the author initial, title and periodical for the existing pages 267–302 locator. Keep identity separate from surname-only person candidates for S3; the article was not independently consulted.",
    },
    {
        "id": "cand-9885",
        "expected": "Morassi, 1952, pages 85-91 (citation locator)",
        "name": "A. Morassi, ‘Settecento inedito III’ (Arte Veneta, 1952, pp. 85–98)",
        "detail": "Printed p.430 gives the article range as pp.85–98; Haskell’s notes cite pp.85–91. Preserve both locators as printed for S3; the article was not independently consulted.",
    },
    {
        "id": "cand-9889",
        "expected": "Morassi, 1960, pages 147-164 and 199-212 (citation locator)",
        "name": "A. Morassi, ‘Antonio Guardi ai servigj del Feldmaresciallo Schulenburg’ (Emporium, 1960, pp. 147–164 and 199–212)",
        "detail": "Printed p.430 confirms the full title and two page ranges for the existing 1960 locator; OCR reads i960. The article was not independently consulted.",
    },
    {
        "id": "cand-10137",
        "expected": "Morazzoni (p.332 note 4 citation locator; title and page not supplied)",
        "name": "G. Morazzoni, Il libro illustrato veneziano del Settecento (Milano, 1943)",
        "detail": "Printed p.430 identifies the publication matching the existing unpaginated Morazzoni locator. Separate page locators cand-10140, cand-10143, cand-10162 and cand-10175 remain linked for S3; none of the cited pages or the book was independently consulted.",
    },
    {
        "id": "cand-10188",
        "expected": "Morelli, volume V, p.348 (title unspecified in p.340 note 1)",
        "name": "Jacobo Morelli, Bibliotheca Maphaei Pinelli Veneti … descripta et annotationibus illustrata (6 vols., Venetiis, 1786)",
        "detail": "Printed p.430 supplies the six-volume catalogue title and edition for the existing volume-V, p.348 locator. The cited page and catalogue were not independently consulted.",
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
    ("cand-11400", "Conte E. Miari, Il nuovo patriziato veneto dopo la serrata del maggior consiglio e la guerra di Candia (Venezia, 1891)", "Bibliography entry at printed p.430. Retain the short printed dash after the date as punctuation; the book was not independently consulted.", 809, "archive"),
    ("cand-11401", "Molinier, Em. (author heading in Haskell’s bibliography; identity unresolved)", "Source-derived person candidate for the printed bibliography heading and its See pointer to the Müntz et Molinier entry. Full personal identity remains unresolved.", 820, "person"),
    ("cand-11402", "G. L. Moncallero, L’Arcadia, vol. I (Firenze, 1953)", "Bibliography entry at printed p.430. Keep distinct from the unresolved Robertson/Moncallero joint citation cand-9932 pending S3; the volume was not independently consulted.", 831, "archive"),
    ("cand-11403", "Balthazar de Monconys, Journal des Voyages (4 parts in 2 vols., Lyon, 1665–1666)", "Bibliography entry at printed p.430. The travel journal was not independently consulted.", 832, "archive"),
    ("cand-11404", "A. Morassi, G. B. Tiepolo (London, 1955)", "Bibliography entry at printed p.430. This book is distinct from Morassi’s separately listed 1955 article on Tiepolo’s unpublished works; the book was not independently consulted.", 839, "archive"),
    ("cand-11405", "A. Morassi, ‘Some “modelli” and other unpublished works by Tiepolo’ (Burlington Magazine, 1955, pp. 4–12)", "Bibliography entry at printed p.430. Keep separate from Morassi’s 1955 G. B. Tiepolo book; the article was not independently consulted.", 840, "archive"),
]

natural_keys = {}
for row in candidates:
    key = (row["canonical_name"].strip().casefold(), row["suggested_type"].casefold())
    natural_keys.setdefault(key, set()).add(row["candidate_id"])
new_candidates = []
for candidate_id, canonical_name, detail, source_line, candidate_type in new_candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (canonical_name.strip().casefold(), candidate_type)
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
    {"candidate_id": "cand-11400", "start": 809, "end": 809, "author": "Miari, Conte E.", "title": "Il nuovo patriziato veneto dopo la serrata del maggior consiglio e la guerra di Candia", "details": "Venezia 1891", "kind": "book", "page_image_notes": ["A short dash follows the printed date; retain it as punctuation and do not interpret it as bibliographic data."]},
    {"candidate_id": "cand-5979", "start": 810, "end": 810, "author": "Michaelis, A.", "title": "Ancient marbles in Great Britain", "details": "Cambridge 1882", "kind": "book"},
    {"candidate_id": "cand-6571", "start": 811, "end": 811, "author": "Michaud, E.", "title": "Louis XIV et Innocent XI", "details": "4 vols., Paris 1882–1883", "kind": "four-volume book set", "related": ["cand-6572"]},
    {"candidate_id": "cand-7768", "start": 812, "end": 812, "author": "Miller, D.", "title": "‘Per Giuseppe Gambarini’", "details": "Arte Antica e Moderna, 1958, pp. 390–393", "kind": "journal article"},
    {"candidate_id": "cand-6607", "start": 813, "end": 813, "author": "Miller, D.", "title": "‘An unpublished letter by Giuseppe Maria Crespi’", "details": "Burlington Magazine, 1960, pp. 530–531", "kind": "journal article", "mentions": [{"surface": "An unpublished letter by Giuseppe Maria Crespi"}], "corrections": [{"line": 813, "ocr": "i960", "print": "1960", "note": "The page image reads 1960."}, {"line": 813, "ocr": "531Miller", "print": "531.\nMiller", "note": "The image separates the end of this item from the next Miller entry."}]},
    {"candidate_id": "cand-7757", "start": 813, "end": 814, "author": "Miller, D.", "title": "‘The Gallery of Aeneid in the Palazzo Bonaccorsi at Macerata’", "details": "Arte Antica e Moderna, 1963, pp. 153–158 and 1964, p. 113", "kind": "journal article with two year locators", "mentions": [{"surface": "The Gallery of Aeneid in the Palazzo Bonaccorsi at Macerata", "candidate_id": "cand-7757"}, {"surface": "1964, p. 113", "candidate_id": "cand-7758"}], "mentioned": ["cand-7757", "cand-7758"], "related": ["cand-7758"], "corrections": [{"line": 813, "ocr": "531Miller", "print": "531.\\nMiller", "note": "The page image shows two separate Miller bibliography entries; the second begins after the first article’s page range."}]},
    {"candidate_id": "cand-6361", "start": 815, "end": 816, "author": "Missirini, Melchior", "title": "Memorie per servire alla storia della Romana Accademia di S. Luca", "details": "Roma 1823", "kind": "book"},
    {"candidate_id": "cand-6457", "start": 817, "end": 817, "author": "Misson, Maximilien", "title": "Nouveau Voyage d’Italie", "details": "4ème édition, 4 vols., La Haye 1717–1722", "kind": "four-volume book set"},
    {"candidate_id": "cand-5873", "start": 818, "end": 819, "author": "Mitchell, C.", "title": "‘Poussin’s “Flight into Egypt”’", "details": "Journal of the Warburg and Courtauld Institutes, I, 1937–1938, pp. 340–343", "kind": "journal article", "corrections": [{"line": 819, "ocr": 'pp340-343- "', "print": "pp. 340–343.", "note": "The page image confirms the punctuation and page range; trailing OCR marks are artifacts."}]},
    {"candidate_id": "cand-8510", "start": 821, "end": 822, "author": "Molino, Sebastiano", "title": "Orazione in lode di Marco Foscarini Procurator di S. Marco", "details": "in [G. A. Molin]: Orazioni, elogj e vite scritte da letterati veneti patrizj, Venezia 1795", "kind": "published oration in collected volume"},
    {"candidate_id": "cand-9818", "start": 823, "end": 823, "author": "Molmenti, P.", "title": "La storia di Venezia nella vita privata", "details": "3 vols., Bergamo 1908", "kind": "three-volume book set"},
    {"candidate_id": "cand-8326", "start": 824, "end": 825, "author": "Molmenti, P.", "title": "‘Il Palazzo Grassi a Venezia e un affresco attribuito a Tiepolo’", "details": "Emporium, 1909, XXIX, pp. 177–188", "kind": "journal article"},
    {"candidate_id": "cand-8116", "start": 826, "end": 827, "author": "Molmenti, P.", "title": "‘Le relazioni tra patrizi veneziani e diplomatici stranieri’", "details": "in Curiosità di Storia Veneziana, Bologna 1919", "kind": "contribution to edited volume"},
    {"candidate_id": "cand-10475", "start": 828, "end": 829, "author": "Molmenti, P.", "title": "‘Un nobil huomo veneziano del secolo XVIII’", "details": "in Epistolari veneziani del secolo XVIII, Milano n.d.", "kind": "contribution to edited volume; date not stated"},
    {"candidate_id": "cand-7618", "start": 830, "end": 830, "author": "Monaco, Pietro", "title": "Raccolta di centododici stampe di pittura della storia sacra incise per la prima volta in rame, e fedelmente copiate dagli originali esistenti in Venezia di celebri autori antichi e moderni", "details": "Venezia 1763", "kind": "illustrated print catalogue", "related": ["cand-10219", "cand-10116"], "page_image_notes": ["This bibliography entry identifies the 1763 edition; preserve the undated p.345 locator and posthumous 1779 edition as separate candidates for S3."]},
    {"candidate_id": "cand-11402", "start": 831, "end": 831, "author": "Moncallero, G. L.", "title": "L’Arcadia", "details": "vol. I, Firenze 1953", "kind": "book volume", "related": ["cand-9932"]},
    {"candidate_id": "cand-11403", "start": 832, "end": 832, "author": "Monconys, Balthazar de", "title": "Journal des Voyages", "details": "4 parts in 2 vols., Lyon 1665–1666", "kind": "multi-part travel journal"},
    {"candidate_id": "cand-4853", "start": 833, "end": 833, "author": "Montagu, Jennifer", "title": "‘The painted enigma and French seventeenth-century art’", "details": "Journal of the Warburg and Courtauld Institutes, 1968, pp. 307–335", "kind": "journal article"},
    {"candidate_id": "cand-7113", "start": 834, "end": 835, "author": "Montaiglon, A. de", "title": "Correspondance des Directeurs de l’Académie de France à Rome avec les Surintendants des Bâtiments", "details": "18 vols., Paris 1887–1912", "kind": "eighteen-volume publication set", "related": ["cand-7132"], "corrections": [{"line": 834, "ocr": "1’Académie", "print": "l’Académie", "note": "OCR uses the numeral 1 where the page image reads a lowercase l."}, {"line": 835, "ocr": "1912. .", "print": "1912.", "note": "The trailing OCR period is absent from print."}]},
    {"candidate_id": "cand-6355", "start": 836, "end": 837, "author": "Montalto, L.", "title": "‘Gli affreschi del Palazzo Pamphilj in Valmontone’", "details": "Commentari, 1955, pp. 267–302", "kind": "journal article"},
    {"candidate_id": "cand-9885", "start": 838, "end": 838, "author": "Morassi, A.", "title": "‘Settecento inedito III’", "details": "Arte Veneta, 1952, pp. 85–98", "kind": "journal article", "page_image_notes": ["The bibliography gives pp.85–98; Haskell’s p.312 notes cite pp.85–91. Preserve the difference for S3."]},
    {"candidate_id": "cand-11404", "start": 839, "end": 839, "author": "Morassi, A.", "title": "G. B. Tiepolo", "details": "London 1955", "kind": "book"},
    {"candidate_id": "cand-11405", "start": 840, "end": 841, "author": "Morassi, A.", "title": "‘Some “modelli” and other unpublished works by Tiepolo’", "details": "Burlington Magazine, 1955, pp. 4–12", "kind": "journal article", "corrections": [{"line": 839, "ocr": ". Morassi", "print": "Morassi", "note": "The page image does not have an initial period before the author."}, {"line": 841, "ocr": "1955. PP4-12. - ,", "print": "1955, pp. 4–12.", "note": "The page image confirms the journal year and page range; punctuation after the range is OCR noise."}]},
    {"candidate_id": "cand-9889", "start": 842, "end": 842, "author": "Morassi, A.", "title": "‘Antonio Guardi ai servigj del Feldmaresciallo Schulenburg’", "details": "Emporium, 1960, pp. 147–164 and 199–212", "kind": "journal article", "corrections": [{"line": 842, "ocr": "i960", "print": "1960", "note": "The page image reads 1960."}]},
    {"candidate_id": "cand-10137", "start": 843, "end": 843, "author": "Morazzoni, G.", "title": "Il libro illustrato veneziano del Settecento", "details": "Milano 1943", "kind": "book", "related": ["cand-10140", "cand-10143", "cand-10162", "cand-10175"]},
    {"candidate_id": "cand-10188", "start": 844, "end": 844, "author": "Morelli, J.", "title": "Bibliotheca Maphaei Pinelli Veneti … a Jacobo Morellio … descripta et annotationibus illustrata", "details": "6 vols., Venetiis 1786", "kind": "six-volume catalogue", "corrections": [{"line": 844, "ocr": "Bibliotheca Maphaei Pinelli Veneti    a Jacobo Morellio    descripta", "print": "Bibliotheca Maphaei Pinelli Veneti … a Jacobo Morellio … descripta", "note": "The page image has spaced ellipses in the title."}]},
]

line_miller = source_lines[812]
gallery_marker = "Miller, D.: ‘The Gallery of Aeneid in the Palazzo Bonaccorsi at Macerata’"
if gallery_marker not in line_miller:
    raise SystemExit("Miller 1960/1963 OCR join changed")
letter_quote, gallery_tail = line_miller.split(gallery_marker, 1)
if "531" not in letter_quote or not gallery_tail.startswith(" in Arte Antica e"):
    raise SystemExit("unexpected Miller bibliography boundary at L813")
entries[4]["quote"] = letter_quote.rstrip()
entries[5]["quote"] = gallery_marker + gallery_tail + "\n" + source_lines[813]
if "Molinier, Em: See Müntz et Molinier." != source_lines[819]:
    raise SystemExit("Molinier cross-reference line changed")

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


def add_mention(candidate_id, surface, note):
    positions = [index for index in range(len(segment_text)) if segment_text.startswith(surface, index)]
    if len(positions) != 1:
        raise SystemExit(f"mention surface must occur once in segment: {candidate_id} {surface!r}")
    position = positions[0]
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    mention_id = f"m-chp21-bib-l808-844-{len(new_mentions) + 1:03d}"
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


def add_publication_statement(statement_id, entry, candidate_id):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    title = entry["title"].strip("‘’\" ")
    claim = f"Haskell lists {title} in the bibliography."
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
        "mentioned_candidate_ids": entry.get("mentioned", [candidate_id]),
        "text_layer": "bibliographic entry",
        "qualification": "This records the bibliography entry only; the cited publication was not independently consulted in this S2 pass.",
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 430,
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
    mention_specs = entry.get("mentions", [{"surface": quote, "candidate_id": candidate_id}])
    for mention in mention_specs:
        surface = mention["surface"]
        mention_candidate_id = mention.get("candidate_id", candidate_id)
        if surface not in quote:
            raise SystemExit(f"mention is outside source quote: {mention_candidate_id} {surface!r}")
        if mention_candidate_id not in candidate_by_id:
            raise SystemExit(f"mention candidate FK missing: {mention_candidate_id}")
        add_mention(
            mention_candidate_id,
            surface,
            "S0 bibliography entry; page-image readings and S3 comparisons are recorded on its statement.",
        )
    add_publication_statement(
        f"st-chp21-bib-l808-844-entry-{index:02d}", entry, candidate_id
    )

crossref_candidate = candidate_by_id.get("cand-11401")
target_candidate = candidate_by_id.get("cand-4828")
if not crossref_candidate or crossref_candidate.get("suggested_type") != "person":
    raise SystemExit("Molinier heading candidate missing or wrong type")
if not target_candidate or target_candidate.get("suggested_type") != "archive":
    raise SystemExit("Müntz et Molinier target candidate missing or wrong type")
add_mention(
    "cand-11401",
    "Molinier, Em",
    "Bibliography author heading; the See pointer targets the queued L861 record.",
)
xref_quote = source_lines[819]
xref_claim = "Haskell’s bibliography directs the ‘Molinier, Em’ author heading to the Müntz et Molinier entry."
xref_id = "st-chp21-bib-l808-844-xref-molinier-muntz"
if xref_id in statement_ids:
    raise SystemExit(f"statement ID already exists: {xref_id}")
if (SEGMENT, " ".join(xref_claim.split()).casefold()) in existing_claim_keys:
    raise SystemExit("duplicate Molinier cross-reference claim")
new_statements.append(
    {
        "statement_id": xref_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-11401",
        "object_candidate_id": "cand-4828",
        "predicate": "bibliography_author_cross_reference",
        "qualifiers": {
            "source_line_start": 820,
            "source_line_end": 820,
            "claim": xref_claim,
            "speaker": "Haskell’s bibliography",
            "relation_candidate": False,
            "mentioned_candidate_ids": ["cand-11401"],
            "text_layer": "bibliography cross-reference",
            "qualification": "The pointer names a later author heading at L861. The target segment L846–881 is still queued, so the match to cand-4828 remains provisional until that entry is reviewed.",
            "cross_reference_type": "see_also",
            "target_source_line": 861,
            "target_segment_id": TARGET_SEGMENT,
            "target_source_line_status": "queued; target entry not yet reviewed",
            "related_candidate_ids_for_s3": ["cand-11401", "cand-4828"],
        },
        "original_quote": xref_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
)
statement_ids.add(xref_id)

if len(entries) != 26 or len(new_candidates) != 6 or len(new_mentions) != 28 or len(new_statements) != 27:
    raise SystemExit(
        f"unexpected migration row counts: publications={len(entries)}, "
        f"candidates={len(new_candidates)}, mentions={len(new_mentions)}, statements={len(new_statements)}"
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
    quote = statement["original_quote"]
    start = qualifiers["source_line_start"]
    end = qualifiers["source_line_end"]
    excerpt = "\n".join(source_lines[start - 1 : end])
    if quote not in excerpt:
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
coverage_row["source_line_ranges"] = "L809-844"
coverage_row["note"] = (
    "Printed p.430 contains 26 publication entries and one author cross-reference. "
    "[Page 430] at L808 is only a page marker. Reused 21 archive candidates and added five archive "
    "candidates plus one person candidate for the Molinier heading. The L820 pointer targets L861 "
    "in queued segment L846-881; target alignment remains provisional until that page is reviewed. "
    "The OCR fuses two Miller entries at L813; their quotes and mentions are split at the page-image boundary."
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
            "new_archive_candidates": sum(row["suggested_type"] == "archive" for row in new_candidates),
            "new_person_candidates": sum(row["suggested_type"] == "person" for row in new_candidates),
            "new_mentions": len(new_mentions),
            "new_statements": len(new_statements),
            "publication_statements": sum(row["predicate"] == "bibliography_lists_publication" for row in new_statements),
            "cross_reference_statements": sum(row["predicate"] == "bibliography_author_cross_reference" for row in new_statements),
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
