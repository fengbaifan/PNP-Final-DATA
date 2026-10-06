#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 425."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l577-614"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "172f465616f50b076ef1d6a92e61c5c2c1e6569a59f648852b4c9a90edd0ecb2"
BACKUP = ".bak-s2-chp21-bibliography-l577-614-20261007"

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
segment_text = "\n".join(source_lines[576:614])
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
    11333,
    26333,
    11608,
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

# Entry boundaries, record count, OCR readings, and the two fused lines were checked
# against the page image for PDF physical page 15 / printed page 425.
entries = [
    {
        "candidate_id": "cand-11165", "start": 578, "end": 578,
        "author": "Harris, Enriqueta & Andrés, Gregorio de",
        "title": "Descripción del Escorial por Cassiano dal Pozzo (1626)",
        "details": "Archivo Español de Arte, 1972 (anejo)", "kind": "journal article / supplement",
        "corrections": [
            {"line": 578, "ocr": "Andres", "print": "Andrés"},
            {"line": 578, "ocr": "Description", "print": "Descripción"},
            {"line": 578, "ocr": "Escoriai", "print": "Escorial"},
            {"line": 578, "ocr": "Archive Espatiol-de Arte", "print": "Archivo Español de Arte"},
        ],
    },
    {
        "candidate_id": "cand-5495", "start": 579, "end": 580,
        "author": "Haskell, F.",
        "title": "P. Legros and a statue of the Blessed Stanislas Kostka",
        "details": "Burlington Magazine, 1955, pp. 287-291", "kind": "journal article",
    },
    {
        "candidate_id": "cand-7790", "start": 581, "end": 581,
        "author": "Haskell, F.", "title": "Stefano Conti, patron of Canaletto and others",
        "details": "Burlington Magazine, 1956, pp. 296-300", "kind": "journal article",
        "related": ["cand-8642", "cand-9882"],
    },
    {
        "candidate_id": "cand-9559", "start": 582, "end": 582,
        "author": "Haskell, F.", "title": "Algarotti and Tiepolo’s ‘Banquet of Cleopatra’",
        "details": "Burlington Magazine, 1958, pp. 212-213", "kind": "journal article",
    },
    {
        "candidate_id": "cand-5136", "start": 583, "end": 583,
        "author": "Haskell, F.", "title": "Painting and the Counter Reformation",
        "details": "Burlington Magazine, 1958, pp. 396-399", "kind": "journal article",
    },
    {
        "candidate_id": "cand-6240", "start": 584, "end": 585,
        "author": "Haskell, F.", "title": "The market for Italian art in the 17th century",
        "details": "Past and Present, April 1959, pp. 48-59", "kind": "journal article",
        "related": ["cand-6606"],
        "page_image_notes": [
            "A detached speck after ‘April 1959,’ at the right margin is not citation punctuation; the record continues with pp. 48-59.",
            "The title resembles a separate L. Stone citation candidate (cand-7048), but the printed byline here is Haskell; do not merge them.",
        ],
    },
    {
        "candidate_id": "cand-11355", "start": 586, "end": 587,
        "new_name": "F. Haskell, ‘Art exhibitions in Seventeenth century Rome’ (Studi Secenteschi, I, 1960, pp. 107-121)",
        "new_detail": "Bibliography-level article record from printed p.425; the cited article was not independently consulted.",
        "author": "Haskell, F.", "title": "Art exhibitions in Seventeenth century Rome",
        "details": "Studi Secenteschi, I, 1960, pp. 107-121", "kind": "journal article",
        "corrections": [{"line": 586, "ocr": "i960", "print": "1960"}],
    },
    {
        "candidate_id": "cand-10717", "start": 588, "end": 589,
        "author": "Haskell, F.",
        "title": "A note on artistic contacts between Florence and Venice in the 18th century",
        "details": "Bollettino dei Musei Civici Veneziani, 1960, N. 3/4, pp. 32-37",
        "kind": "journal article", "related": ["cand-8096"],
        "corrections": [{"line": 589, "ocr": "i960", "print": "1960"}],
        "page_image_notes": [
            "The earlier Andrea Gerini citation cand-8096 may refer to this same article; keep both candidate records distinct until S3 reconciliation.",
        ],
    },
    {
        "candidate_id": "cand-9011", "start": 590, "end": 590,
        "author": "Haskell, F.", "title": "Pictures from Cambridge at Burlington House",
        "details": "Burlington Magazine, 1960, pp. 71-72", "kind": "journal article",
        "corrections": [{"line": 590, "ocr": "i960", "print": "1960"}],
        "page_image_notes": [
            "A chapter note cites Haskell, 1960, pp. 71-73; the bibliography gives pp. 71-72. The overlapping page locator supports this match, while the extra cited page remains for S3 checking.",
        ],
    },
    {
        "candidate_id": "cand-10629", "start": 591, "end": 591,
        "author": "Haskell, F.",
        "title": "Francesco Guardi as vedutista and some of his patrons",
        "details": "Journal of the Warburg and Courtauld Institutes, 1960, pp. 256-276",
        "kind": "journal article",
        "corrections": [{"line": 591, "ocr": "i960", "print": "1960"}],
    },
    {
        "candidate_id": "cand-9424", "start": 592, "end": 592,
        "author": "Haskell, F.", "title": "The Apotheosis of Newton in Art",
        "details": "Texas Quarterly, Autumn 1967, pp. 218-237", "kind": "journal article",
        "related": ["cand-11213"],
        "page_image_notes": [
            "The p.290 note about John Conduitt and Newton supports this of the two Haskell 1967 entries; the article was not independently consulted.",
        ],
    },
    {
        "candidate_id": "cand-11213", "start": 593, "end": 594,
        "author": "Haskell, F.",
        "title": "Some Collectors of Venetian Art at the end of the Eighteenth Century",
        "details": "Studies in Renaissance and Baroque Art presented to Anthony Blunt on his 60th birthday, London 1967, pp. 173-178",
        "kind": "contribution to edited volume", "related": ["cand-9424"],
        "page_image_notes": [
            "The p.410 note on Haskell’s publication of Della Lena’s Venetian treatise supports this of the two Haskell 1967 entries; the cited text was not independently consulted.",
        ],
    },
    {
        "candidate_id": "cand-8638", "start": 595, "end": 595,
        "author": "Haskell, F. and Levey, M.",
        "title": "Art exhibitions in 18th-century Venice",
        "details": "Arte Veneta, 1958, pp. 179-185", "kind": "journal article",
        "related": ["cand-10456"],
        "page_image_notes": [
            "Detached short marks at the right margin after the issue/year line are excluded from the citation.",
        ],
    },
    {
        "candidate_id": "cand-5658", "start": 596, "end": 597,
        "author": "Haskell, F. and Rinehart, S.",
        "title": "The dal Pozzo collection—some new evidence",
        "details": "Burlington Magazine, 1960, pp. 318-326", "kind": "journal article",
        "corrections": [{"line": 596, "ocr": "i960", "print": "1960"}],
    },
    {
        "candidate_id": "cand-7097", "start": 598, "end": 598,
        "author": "Hautecœur, L.",
        "title": "L’Histoire des Châteaux du Louvre et des Tuileries",
        "details": "Paris 1927", "kind": "book",
        "corrections": [{"line": 598, "ocr": "Chateaux", "print": "Châteaux"}],
    },
    {
        "candidate_id": "cand-9920", "start": 599, "end": 599,
        "author": "Hazard, P.", "title": "La crise de la conscience européenne (1680-1715)",
        "details": "Paris 1935", "kind": "book",
    },
    {
        "candidate_id": "cand-10145", "start": 600, "end": 600,
        "author": "Hazard, P.", "title": "La pensée européenne au XVIIIème siècle",
        "details": "2 vols., Paris 1946", "kind": "two-volume book set",
    },
    {
        "candidate_id": "cand-10875", "start": 601, "end": 602,
        "author": "Heikamp, Detlef",
        "title": "La Medusa del Caravaggio e l’armatura dello Scià ‘Abbas di Persia",
        "details": "Paragone, 1966 (199), pp. 62-76", "kind": "journal article",
        "page_image_notes": [
            "This is the sole Heikamp 1966 item in the bibliography and is the contextually supported match for the p.397 note; the article was not independently consulted, so retain for S3 reconciliation.",
        ],
    },
    {
        "candidate_id": "cand-7252", "start": 603, "end": 604,
        "author": "Heilbronner, P.",
        "title": "Arte italiana nel mondo—Architetti del Barocco a Monaco di Baviera",
        "details": "Le Vie d’Italia e del Mondo, 1936, pp. 887-904", "kind": "journal article",
        "page_image_notes": [
            "Detached marginal dashes beside the final line are excluded from the page range.",
        ],
    },
    {
        "candidate_id": "cand-5615", "start": 605, "end": 606,
        "author": "Hervey, M. F. S.",
        "title": "The life, correspondence and collections of Thomas Howard, Earl of Arundel",
        "details": "Cambridge 1921", "kind": "book",
        "page_image_notes": [
            "A detached mark before the continuation line is a scan artifact, not part of the entry.",
        ],
    },
    {
        "candidate_id": "cand-7062", "start": 607, "end": 608,
        "author": "Hess, J.",
        "title": "Die Gemälde des Orazio Gentileschi für das ‘Haus der Königin’ in Greenwich",
        "details": "English Miscellany, 1952, pp. 159-187", "kind": "journal article",
    },
    {
        "candidate_id": "cand-11161", "start": 609, "end": 610,
        "author": "Hess, J.",
        "title": "Contributi alla Storia della Chiesa Nuova (S. Maria in Vallicella)",
        "details": "Scritti di Storia dell’Arte in onore di Mario Salmi, 3 vols., 1963, II, pp. 215-238",
        "kind": "contribution to edited volume",
        "page_image_notes": [
            "The published Hess essay is distinct from the underlying Chiesa Nuova documents represented by cand-10939.",
        ],
    },
    {
        "candidate_id": "cand-4864", "start": 611, "end": 611,
        "author": "Hibbard, H.", "title": "The early history of S. Andrea della Valle",
        "details": "Art Bulletin, 1961, pp. 289-318", "kind": "journal article",
        "related": ["cand-5163"],
    },
    {
        "candidate_id": "cand-5163", "start": 612, "end": 612,
        "author": "Hibbard, H.", "title": "Carlo Maderno and Roman Architecture 1580-1630",
        "details": "London 1971", "kind": "book",
        "related": ["cand-4864"],
    },
    {
        "candidate_id": "cand-10885", "start": 613, "end": 614,
        "author": "Hibbard, H.",
        "title": "Recent Books on Earlier Baroque Architecture in Rome",
        "details": "Art Bulletin, 1973, pp. 127-135", "kind": "journal article",
        "quote_override": (
            "Hibbard, H.: ‘Recent Books on Earlier Baroque Architecture in Rome’ in Art Bulletin,\n"
            "1973. PPI27-I35"
        ),
        "corrections": [
            {
                "line": 614,
                "ocr": "1973. PPI27-I35Hinks",
                "print": "1973, pp. 127-135. [next entry begins] Hinks",
            }
        ],
        "page_image_notes": [
            "The OCR line fuses this page range with the next entry; the printed page image confirms a full stop, a boundary, and then the Hinks record.",
        ],
    },
    {
        "candidate_id": "cand-4353", "start": 614, "end": 614,
        "author": "Hinks, R.", "title": "Michelangelo Merisi da Caravaggio",
        "details": "London 1953", "kind": "book",
        "quote_override": "Hinks, R.: Michelangelo Merisi da Caravaggio, London 1953.",
        "page_image_notes": [
            "The entry begins after the Hibbard article’s printed page range on the same OCR line; the mentions use disjoint spans.",
        ],
    },
]

covered_lines = {line for entry in entries for line in range(entry["start"], entry["end"] + 1)}
if covered_lines != set(range(578, 615)):
    raise SystemExit("bibliography entry line coverage is incomplete")
if len(entries) != 26:
    raise SystemExit("unexpected local bibliography record count")

# Old labels are guards against silently updating a changed candidate. Details that
# became stale are replaced; other details are extended with the new print evidence.
candidate_updates = [
    {
        "id": "cand-11165", "type": "archive",
        "expected": "Harris and de Andrés, publication cited at p.401 note 1 (title and year unresolved)",
        "name": "Enriqueta Harris & Gregorio de Andrés, Descripción del Escorial por Cassiano dal Pozzo (1626) (Archivo Español de Arte, 1972, anejo)",
        "detail": "Printed p.425 identifies the publication cited at p.401 note 1; the article was not independently consulted. The named author identity is supported by the book’s byline; global alignment remains for S3.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-11166", "type": "person",
        "expected": "Harris (author cited in p.401 note 1; identity unresolved)",
        "name": "Enriqueta Harris (author cited in p.401 note 1)",
        "detail": "The p.401 note’s Harris form maps within the book to the printed byline ‘Harris, Enriqueta & Andrés, Gregorio de’ at p.425. This is source-level identification; alignment with other Harris candidates remains for S3.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-5495", "type": "archive",
        "expected": "Francis Haskell, P. Legros and a statue of the Blessed Stanislas Kostka (1955), pages 287-291",
        "name": "F. Haskell, ‘P. Legros and a statue of the Blessed Stanislas Kostka’ (Burlington Magazine, 1955, pp. 287-291)",
        "detail": "Printed p.425 confirms the article title, journal, year, and pages; it was not independently consulted.",
    },
    {
        "id": "cand-7790", "type": "archive",
        "expected": "Unidentified Haskell publication from 1956 on Stefano Conti",
        "name": "F. Haskell, ‘Stefano Conti, patron of Canaletto and others’ (Burlington Magazine, 1956, pp. 296-300)",
        "detail": "Printed p.425 supplies the title and publication details. The page-298 locators cand-8642 and cand-9882 remain separate for S3 reconciliation; the article was not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-5136", "type": "archive",
        "expected": "Haskell review (1958), p. 396; title unspecified",
        "name": "F. Haskell, ‘Painting and the Counter Reformation’ (Burlington Magazine, 1958, pp. 396-399)",
        "detail": "The exact year, periodical, and page range match the page-146 review citation; the cited pages were not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-6240", "type": "archive",
        "expected": "Haskell’s 1959 cited publication (exact title and edition to reconcile with bibliography)",
        "name": "F. Haskell, ‘The market for Italian art in the 17th century’ (Past and Present, April 1959, pp. 48-59)",
        "detail": "Printed p.425 identifies the 1959 work. Keep the separate Haskell 1959 locator cand-6606 for S3 reconciliation; do not merge with the L. Stone article candidate cand-7048, whose printed byline is different. The article was not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-6606", "type": "archive",
        "expected": "Haskell (1959), cited publication (full details unspecified)",
        "detail": "The full bibliography lists Haskell’s April 1959 Past and Present article (cand-6240), a likely match by author and year. Retain this short-form citation candidate separately for S3 reconciliation; the cited article was not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-10717", "type": "archive",
        "expected": "Haskell citation in Bollettino dei Musei Civici Veneziani, 1960, nos. 3/4, pp. 32–37",
        "name": "F. Haskell, ‘A note on artistic contacts between Florence and Venice in the 18th century’ (Bollettino dei Musei Civici Veneziani, 1960, no. 3/4, pp. 32-37)",
        "detail": "Printed p.425 confirms the title and exact issue/page locator. Compare with the earlier Andrea Gerini citation candidate cand-8096 at S3; article not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-9011", "type": "archive",
        "expected": "Unidentified Haskell 1960 source cited in note 2 (pp. 71–73)",
        "name": "F. Haskell, ‘Pictures from Cambridge at Burlington House’ (Burlington Magazine, 1960, pp. 71-72)",
        "detail": "Printed p.425 gives the title and pages 71-72, overlapping the p.290 note’s pp.71-73 locator. Preserve the one-page locator difference for S3; article not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-10629", "type": "archive",
        "expected": "Haskell, Journal of Warburg Institute, 1960 (article title unspecified)",
        "name": "F. Haskell, ‘Francesco Guardi as vedutista and some of his patrons’ (Journal of the Warburg and Courtauld Institutes, 1960, pp. 256-276)",
        "detail": "Printed p.425 identifies the title and confirms the cited pp.256-276; article not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-9424", "type": "archive",
        "expected": "Haskell, 1967 (citation in p.290 note 1; exact work unresolved)",
        "name": "F. Haskell, ‘The Apotheosis of Newton in Art’ (Texas Quarterly, Autumn 1967, pp. 218-237)",
        "detail": "The p.290 note’s John Conduitt / Newton context supports this of the two Haskell 1967 entries; printed p.425 supplies the title and details. The article was not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-11213", "type": "archive",
        "expected": "Haskell 1967 (p.410 note 4; title pending bibliography reconciliation)",
        "name": "F. Haskell, ‘Some Collectors of Venetian Art at the end of the Eighteenth Century’ (Studies in Renaissance and Baroque Art presented to Anthony Blunt, London, 1967, pp. 173-178)",
        "detail": "The p.410 note concerns Haskell’s publication of Della Lena’s Venetian treatise; that context supports this of the two Haskell 1967 entries. Bibliographic details come from printed p.425; retain for S3 because the essay was not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-8638", "type": "archive",
        "expected": "Haskell and Levey, 1958, p.182 (citation locator; title pending bibliography review)",
        "name": "F. Haskell and M. Levey, ‘Art exhibitions in 18th-century Venice’ (Arte Veneta, 1958, pp. 179-185)",
        "detail": "Printed p.425 identifies the article covering the cited pp.182 and 185. Keep the two short-form page locators, including cand-10456, linked for S3; article not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-5658", "type": "archive",
        "expected": "Haskell and Rinehart’s 1960 inventory of Cassiano’s pictures",
        "name": "F. Haskell and S. Rinehart, ‘The dal Pozzo collection—some new evidence’ (Burlington Magazine, 1960, pp. 318-326)",
        "detail": "Printed p.425 supplies the article title and publication details for the earlier Haskell and Rinehart citation; article not independently consulted.",
    },
    {
        "id": "cand-9920", "type": "archive",
        "expected": "Hazard, 1935 (minimal citation locator)",
        "name": "P. Hazard, La crise de la conscience européenne (1680-1715) (Paris, 1935)",
        "detail": "Printed p.425 supplies the title and publication place/year; the book was not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-10145", "type": "archive",
        "expected": "Hazard, 1946, volume I, pp.105-107 and note (p.334 note 6)",
        "name": "P. Hazard, La pensée européenne au XVIIIème siècle (2 vols., Paris, 1946)",
        "detail": "Printed p.425 identifies the two-volume set cited at volume I, pp.105-107; neither cited pages nor full work were independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-10875", "type": "archive",
        "expected": "Heikamp, 1966 study of Cardinal Del Monte and the Tuscan court (title unspecified)",
        "name": "Detlef Heikamp, ‘La Medusa del Caravaggio e l’armatura dello Scià ‘Abbas di Persia’ (Paragone, 1966 (199), pp. 62-76)",
        "detail": "This is the sole Heikamp 1966 bibliography entry and the contextual match for the p.397 note about Del Monte; retain the match for S3 because the article was not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-7252", "type": "archive",
        "expected": "P. Heilbronner, ‘Arte italiana nel mondo—Architetti del Barocco a Monaco di Baviera’ (1936)",
        "name": "P. Heilbronner, ‘Arte italiana nel mondo—Architetti del Barocco a Monaco di Baviera’ (Le Vie d’Italia e del Mondo, 1936, pp. 887-904)",
        "detail": "Printed p.425 confirms the periodical and page range; article not independently consulted.",
    },
    {
        "id": "cand-7062", "type": "archive",
        "expected": "J. Hess, “Die Gemälde des Orazio Gentileschi für das Haus der Königin in Greenwich” (English Miscellany, 1952)",
        "name": "J. Hess, ‘Die Gemälde des Orazio Gentileschi für das Haus der Königin in Greenwich’ (English Miscellany, 1952, pp. 159-187)",
        "detail": "Printed p.425 confirms the page range already cited in the chapter note; article not independently consulted.",
    },
    {
        "id": "cand-11161", "type": "archive",
        "expected": "Jacob Hess, 1963 publication on the early building history of Chiesa Nuova (title unspecified)",
        "name": "J. Hess, ‘Contributi alla Storia della Chiesa Nuova (S. Maria in Vallicella)’ (Scritti di Storia dell’Arte in onore di Mario Salmi, 1963, vol. II, pp. 215-238)",
        "detail": "Printed p.425 identifies the title and edited-volume location cited in the p.400 note. The essay is distinct from the underlying documents represented by cand-10939; essay not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-4864", "type": "archive",
        "expected": "Hibbard (1961), monograph on Carlo Maderno; title unspecified",
        "name": "H. Hibbard, ‘The early history of S. Andrea della Valle’ (Art Bulletin, 1961, pp. 289-318)",
        "detail": "Printed p.425 identifies the Hibbard (1961), pp.289-318 citation as this Art Bulletin article. It is distinct from the 1971 Carlo Maderno monograph candidate cand-5163. The article was not independently consulted.",
        "detail_mode": "replace",
        "source_ref": "chp-3:03_CHP-3_sec_ii:l144-179#L161",
        "expected_source_ref": "chp-2:02_CHP-2_sec_iv:l190-245#L209",
    },
    {
        "id": "cand-5163", "type": "archive",
        "expected": "Hibbard (1971), cited publication, pp. 232–234; title unspecified",
        "name": "H. Hibbard, Carlo Maderno and Roman Architecture 1580-1630 (London, 1971)",
        "detail": "Printed p.425 identifies this 1971 monograph. The 1961 S. Andrea della Valle article remains a distinct candidate, cand-4864; the p.47 monograph mention is linked here. Neither cited work was independently consulted.",
        "detail_mode": "replace",
        "source_ref": "chp-2:02_CHP-2_sec_iv:l190-245#L209",
        "expected_source_ref": "chp-3:03_CHP-3_sec_ii:l144-179#L170",
    },
    {
        "id": "cand-10885", "type": "archive",
        "expected": "Hibbard, 1973 publication discussing Lavin and recent Borromini literature (title unspecified)",
        "name": "H. Hibbard, ‘Recent Books on Earlier Baroque Architecture in Rome’ (Art Bulletin, 1973, pp. 127-135)",
        "detail": "Printed p.425 identifies the title and page range for the p.397 Hibbard (1973) citation; article not independently consulted.",
        "detail_mode": "replace",
    },
    {
        "id": "cand-4353", "type": "archive",
        "expected": "Roger Hinks (1953), cited publication, p. 104; title unspecified",
        "name": "R. Hinks, Michelangelo Merisi da Caravaggio (London, 1953)",
        "detail": "Printed p.425 supplies the book title, place, and year for the p.60 note citation; the book was not independently consulted.",
        "detail_mode": "replace",
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
    if update.get("expected_source_ref") and candidate.get("candidate_source_ref") != update["expected_source_ref"]:
        raise SystemExit(f"candidate source reference changed: {update['id']}")
    old_key = (
        candidate["canonical_name"].strip().casefold(),
        candidate["suggested_type"].strip().casefold(),
    )
    new_name = update.get("name", candidate["canonical_name"])
    new_key = (new_name.strip().casefold(), candidate["suggested_type"].strip().casefold())
    collisions = natural_keys.get(new_key, set()) - {update["id"]}
    if collisions:
        raise SystemExit(f"candidate name collision {update['id']}: {sorted(collisions)}")
    natural_keys.get(old_key, set()).discard(update["id"])
    natural_keys.setdefault(new_key, set()).add(update["id"])
    candidate["canonical_name"] = new_name
    if update.get("detail"):
        if update.get("detail_mode") == "replace":
            candidate["detail"] = update["detail"]
        else:
            candidate["detail"] = f'{candidate.get("detail", "").rstrip()} {update["detail"]}'.strip()
    if update.get("source_ref"):
        candidate["candidate_source_ref"] = update["source_ref"]

new_candidate_specs = [
    ("cand-11355", entries[6]["new_name"], entries[6]["new_detail"], f"{SEGMENT}#L586"),
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

# Printed p.425 separates the 1961 S. Andrea article from the 1971 Maderno book.
# Move only the earlier monograph mention/citation, preserving the 1961 locators.
mention_by_id = {row["mention_id"]: row for row in mentions}
monograph_mention = mention_by_id.get("m-chp2-seciv-l190-245-0038")
article_mention = mention_by_id.get("m-chp3-p71-73note-0004")
if not monograph_mention or monograph_mention.get("candidate_id") != "cand-4864":
    raise SystemExit("unexpected existing Hibbard monograph mention")
if not article_mention or article_mention.get("candidate_id") != "cand-4864":
    raise SystemExit("unexpected existing Hibbard 1961 mention")
monograph_mention["candidate_id"] = "cand-5163"
monograph_mention["note"] = "The p.425 bibliography identifies the Maderno monograph as the 1971 book; global alignment remains for S3."
article_mention["note"] = "The p.425 bibliography identifies this 1961, pp. 289-318 citation as the S. Andrea della Valle article."

statement_by_id = {row["statement_id"]: row for row in statements}
monograph_statement = statement_by_id.get("st-chp2-seciv-l190-245-citation-23")
article_statement = statement_by_id.get("st-chp3-secii-p71-note2-hibbard")
if not monograph_statement or monograph_statement.get("object_candidate_id") != "cand-4864":
    raise SystemExit("unexpected Hibbard monograph statement link")
if not article_statement or article_statement.get("object_candidate_id") != "cand-4864":
    raise SystemExit("unexpected Hibbard 1961 statement link")
monograph_statement["object_candidate_id"] = "cand-5163"
monograph_statement["qualifiers"]["cited_source_candidate_id"] = "cand-5163"
monograph_statement["qualifiers"]["qualification"] = (
    "The book bibliography at printed p.425, L612 identifies the cited Maderno monograph as the 1971 book; "
    "the cited work has not been independently consulted."
)
article_statement["qualifiers"]["qualification"] = (
    "Printed p.425, L611 identifies the Hibbard (1961), pp.289-318 citation as ‘The early history of S. Andrea della Valle’; "
    "the article has not been independently consulted."
)

mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
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
    return entry.get("quote_override") or "\n".join(
        source_lines[entry["start"] - 1:entry["end"]]
    )


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
        mention_id=f"m-chp21-bib-l577-614-{len(new_mentions) + 1:03d}",
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=position,
        end_char=end,
        note=note,
    )
    new_mentions.append(row)
    mention_keys.add(key)


def add_statement(statement_id, entry, object_id, quote, qualifiers):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim = f"Haskell lists {entry['title']} in the bibliography."
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    statement_ids.add(statement_id)
    existing_claim_keys.add(claim_key)
    row = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": object_id,
        "predicate": "bibliography_lists_publication",
        "qualifiers": {
            "source_line_start": entry["start"],
            "source_line_end": entry["end"],
            "claim": claim,
            "speaker": "Haskell’s bibliography",
            "relation_candidate": False,
            "mentioned_candidate_ids": [object_id],
            "text_layer": "bibliographic entry",
            "qualification": (
                "This records the bibliography entry only; the cited publication was not independently consulted in this S2 pass."
            ),
            "bibliographic_record": {
                "author_as_printed": entry["author"],
                "title_as_printed": entry["title"],
                "publication_details_as_printed": entry["details"],
                "record_kind": entry["kind"],
                "printed_page": 425,
            },
            **qualifiers,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    if not quote or quote not in "\n".join(source_lines[entry["start"] - 1:entry["end"]]):
        raise SystemExit(f"statement quote/line validation failed: {statement_id}")
    new_statements.append(row)


for index, entry in enumerate(entries, start=1):
    candidate_id = entry["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {candidate_id}")
    quote = source_quote(entry)
    add_mention(
        candidate_id,
        quote,
        "S0 bibliography entry; page-image OCR corrections, scan notes, and candidate reconciliation are recorded on its statement.",
    )
    qualifiers = {}
    if entry.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("page_image_notes"):
        qualifiers["page_image_notes"] = entry["page_image_notes"]
    if entry.get("related"):
        for related_id in entry["related"]:
            if related_id not in candidate_by_id:
                raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
        qualifiers["related_candidate_ids_for_s3"] = entry["related"]
    add_statement(
        f"st-chp21-bib-l577-614-entry-{index:02d}",
        entry,
        candidate_id,
        quote,
        qualifiers,
    )

if len(new_candidates) != 1 or len(new_mentions) != 26 or len(new_statements) != 26:
    raise SystemExit("unexpected migration row counts")
if [row["candidate_id"] for row in new_candidates] != ["cand-11355"]:
    raise SystemExit("new candidate ID is not the expected next sequence")

for statement in new_statements:
    object_id = statement["object_candidate_id"]
    if object_id not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
    qualifiers = statement["qualifiers"]
    for candidate_id in qualifiers.get("mentioned_candidate_ids", []):
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"mentioned candidate FK missing: {statement['statement_id']}: {candidate_id}")
    for candidate_id in qualifiers.get("related_candidate_ids_for_s3", []):
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {statement['statement_id']}: {candidate_id}")

for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")
ordered_mentions = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(ordered_mentions, ordered_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L578-614"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.425 contains 26 bibliography entries; the [Page 425] marker is not a record. "
    "Reused 25 archive candidates and added one. OCR corrections and detached scan marks are documented in statements; "
    "L614's fused Hibbard/Hinks boundary is split into disjoint mention spans. Cross-chapter citation candidates are linked for S3. "
    "The bibliography distinguishes Hibbard's 1961 S. Andrea article from the 1971 Maderno monograph; the earlier merged citation "
    "candidate and its mention/statement links were corrected. S0 remains unchanged; cited works were not independently consulted."
)

all_candidates = candidates + new_candidates
all_mentions = mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "new_candidates": len(new_candidates),
    "candidate_updates": len(candidate_updates),
    "reassigned_existing_mentions": 1,
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "candidate_count_after": len(all_candidates),
    "mention_count_after": len(all_mentions) + len(new_mentions),
    "statement_count_after": len(all_statements),
    "coverage_rows": len(all_coverage),
    "hibbard_split": {
        "1961_article": "cand-4864",
        "1971_maderno_monograph": "cand-5163",
        "moved_mention_id": "m-chp2-seciv-l190-245-0038",
    },
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup_path = path.with_name(path.name + BACKUP)
        if backup_path.exists():
            raise SystemExit(f"backup already exists: {backup_path}")
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions + new_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
