#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 440."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l1220-1259"
SEGMENT_SHA = "e150ff8ac942307f7e59337b102e618367babaa86b8da6cda422a9e53285307c"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l1179-1218"
BACKUP_SUFFIX = ".bak-s2-chp21-bibliography-l1220-1259-20261007"

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
segment_text = "\n".join(source_lines[1219:1259])
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
) != (SOURCE_FILE, 1220, 1259, SEGMENT_SHA, SOURCE_SHA):
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
    11428,
    26770,
    12043,
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
    previous_coverage["disposition"], previous_coverage["migration_status"]
) != ("reviewed", "complete"):
    raise SystemExit("previous bibliography segment is not complete")

candidate_updates = [
    {
        "id": "cand-11092", "type": "archive",
        "expected": "Frances Vivian's scholarship on Consul Joseph Smith as merchant and collector",
        "name": "Frances Vivian, Il Console Smith mercante e collezionista (Vicenza, 1971)",
        "detail": "Printed p.440 supplies the title and Vicenza 1971 details for the postscript discussion of Vivian's book on Consul Smith. The book was not independently consulted.",
    },
    {
        "id": "cand-9359", "type": "archive",
        "expected": "Voss, 1926, pp.32-37 (citation locator; work unresolved)",
        "name": "H. Voss, ‘Gio Antonio Canal und Owen McSwiny’ (Repertorium für Kunstwissenschaft, 1926, pp. 32–37)",
        "detail": "Printed p.440 supplies the title and venue for the p.287 note 6 locator. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-5875", "type": "archive",
        "expected": "Voss article (1957), pages 25–61, cited for Flight into Egypt representations",
        "name": "H. Voss, ‘Die Flucht nach Aegypten’ (Saggi e Memorie di Storia dell’Arte, Venezia, 1957, pp. 25–61)",
        "detail": "Printed p.440 supplies the title, venue, publication place, year, and pages for the existing 1957 p.25–61 citation. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-4570", "type": "archive",
        "expected": "D. P. Walker, cited publication, pp. 205 ff.; title unspecified",
        "name": "D. P. Walker, Spiritual and demonic magic from Ficino to Campanella (London, 1958)",
        "detail": "Printed p.440 supplies the title and publication details for the earlier pp.205 ff. citation on Urban VIII and Campanella. The cited pages and book were not independently consulted.",
    },
    {
        "id": "cand-7001", "type": "archive",
        "expected": "J. Walker, cited publication at p.78; identity and title unresolved",
        "name": "J. Walker, Bellini and Titian at Ferrara (London, 1956)",
        "detail": "Printed p.440 supplies the title and London 1956 details for the p.78 citation. The cited page and book were not independently consulted; do not infer author identity from the initial alone.",
    },
    {
        "id": "cand-7058", "type": "archive",
        "expected": "Horace Walpole, Anecdotes of Painting in England, vol. II (cited as 1762, p.51)",
        "name": "Horace Walpole, Anecdotes of Painting in England (5 vols., Strawberry Hill, 1726 [as printed])",
        "detail": "Printed p.440 lists a five-volume set dated 1726; earlier citations represented by this candidate say 1762, vol. II, p.51, and p.284 note 4 also cites Anecdotes. Preserve the bibliography's printed 1726 and leave the date/edition discrepancy unresolved; no consulted passage is asserted.",
    },
    {
        "id": "cand-8596", "type": "archive",
        "expected": "Horace Walpole, 1767, page viii (citation locator)",
        "name": "Horace Walpole, Aedes Walpoliane (3rd edition, London, 1767)",
        "detail": "Printed p.440 supplies the title and third-edition details for the existing 1767 p.viii locator. Preserve the printed title spelling Walpoliane; the book and cited page were not independently consulted.",
    },
    {
        "id": "cand-6580", "type": "archive",
        "expected": "Waterhouse, 1953, p. 120; title unspecified",
        "name": "E. K. Waterhouse, ‘Some Old Masters other than Spanish at the Bowes Museum’ (Burlington Magazine, 1953, pp. 120–123)",
        "detail": "Printed p.440 supplies the article title and page range containing the earlier p.120 locator. The article and cited page were not independently consulted.",
    },
    {
        "id": "cand-7259", "type": "archive",
        "expected": "E. K. Waterhouse, ‘A note on British collecting of Italian pictures in the later seventeenth century’ (1960)",
        "name": "E. K. Waterhouse, ‘A note on British collecting of Italian pictures in the later seventeenth century’ (Burlington Magazine, 1960, pp. 54–58)",
        "detail": "Printed p.440 confirms the venue and complete pages for the previously identified p.197 note 5 p.57 citation. The article and cited page were not independently consulted.",
    },
    {
        "id": "cand-9354", "type": "archive",
        "expected": "Watson, Burlington Magazine, 1949, pp.75-79 (article locator; title unresolved)",
        "name": "F. J. B. Watson, ‘The Nazari—a forgotten family of Venetian portrait painters’ (Burlington Magazine, 1949, pp. 75–79)",
        "detail": "Printed p.440 supplies the article title for the p.287 note 3 citation. The article and cited pages were not independently consulted; compare the source-form person candidates at S3.",
    },
    {
        "id": "cand-9367", "type": "archive",
        "expected": "Watson, 1953, pp.362-365 (citation locator; work unresolved)",
        "name": "F. J. B. Watson, ‘An allegorical painting by Canaletto, Piazzetta and Cimaroli’ (Burlington Magazine, 1953, pp. 362–365)",
        "detail": "Printed p.440 supplies the title for the p.287 note 6 page locator. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-9316", "type": "archive",
        "expected": "Watson, Arte Veneta, 1954, pp.295-301 (citation locator; article title unresolved)",
        "name": "F. J. B. Watson, ‘A Venetian Settecento chapel in the English countryside’ (Arte Veneta, 1954, pp. 295–301)",
        "detail": "Printed p.440 supplies the article title for the p.281 note 2 citation on the Canons chapel. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-9301", "type": "archive",
        "expected": "Watson, Journal of R.I.B.A., 1954, pp.171-177 (citation locator; article title unresolved)",
        "name": "F. J. B. Watson, ‘English villas and Venetian decorators’ (Journal of the Royal Institute of British Architects, 1954; pp. 11–177 as printed)",
        "detail": "Printed p.440 supplies the article title but appears to give pp.11–177; the earlier p.279 note 1 locator is pp.171–177. Preserve both forms and compare the apparent page-range discrepancy in S3; the article was not consulted.",
    },
    {
        "id": "cand-10304", "type": "archive",
        "expected": "Watson, 1955, p.214 (citation locator in p.354 note 3)",
        "name": "F. J. B. Watson, ‘Giovanni Battista Tiepolo: a masterpiece and a book’ (Connoisseur, 1955, vol. 136, pp. 212–215)",
        "detail": "Printed p.440 supplies the title and complete issue/page details containing the p.354 note 3 p.214 locator. The article and cited page were not independently consulted.",
    },
    {
        "id": "cand-9893", "type": "archive",
        "expected": "Watson, 1960, pages 3-13 (citation locator)",
        "name": "F. J. B. Watson, ‘A series of “Turqueries” by Francesco Guardi’ (Baltimore Museum of Arts Quarterly, Fall 1960, pp. 3–13)",
        "detail": "Printed p.440 supplies the title and periodical details for the existing p.3–13 locator on the Guardi series. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-9353", "type": "person",
        "expected": "Watson (surname-only author in p.287 notes 3 and 6; possible identity with cand-2803 unresolved)",
        "name": "F. J. B. Watson",
        "detail": "Printed p.440 identifies F. J. B. Watson as author of the 1949 and 1953 entries matching the p.287 note 3 and note 6 locators. Preserve this source form; identity alignment with cand-2803 remains for S3.",
    },
    {
        "id": "cand-11180", "type": "archive",
        "expected": "Wethey publication cited at p.402 note 6 (title and year unspecified)",
        "name": "Harold R. Wethey, ‘The Spanish Viceroy, Luca Giordano and Andrea Vaccaro’ (Burlington Magazine, 1967, pp. 678–686)",
        "detail": "Printed p.440 supplies the article title and full citation details for the p.402 note 6 source. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-10990", "type": "person",
        "expected": "Wethey",
        "name": "Harold R. Wethey",
        "detail": "The p.402 note cites Wethey; printed p.440 identifies Harold R. Wethey as author of the matching article. This records the bibliography's name form only; no biographical claims are added.",
    },
    {
        "id": "cand-9349", "type": "archive",
        "expected": "Wheatley, vol. III, p.18 (citation locator in p.286 note 3; work unresolved)",
        "name": "H. B. Wheatley, London past and present (London, 1891)",
        "detail": "Printed p.440 supplies the title and publication details for the p.286 note 3 volume III p.18 locator. The cited volume and page were not independently consulted.",
    },
    {
        "id": "cand-9348", "type": "person",
        "expected": "Wheatley (surname-only author in p.286 note 3; identity unresolved)",
        "name": "H. B. Wheatley",
        "detail": "Printed p.440 gives the bibliography author form H. B. Wheatley for the publication matching the p.286 surname-only citation. This supplies a source form, not additional biographical evidence.",
    },
    {
        "id": "cand-9898", "type": "archive",
        "expected": "White and Sewter, 1959, pages 96-100 (citation locator)",
        "name": "D. Maxwell White and A. C. Sewter, ‘Piazzetta’s so-called Group on the Sea shore’ (Connoisseur, 1959, vol. 143, pp. 96–100)",
        "detail": "Printed p.440 supplies the article title and complete venue details for the p.314 note 2 page locator. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-9896", "type": "person",
        "expected": "White (author cited with Sewter at p.314 note 2; identity unresolved)",
        "name": "D. Maxwell White",
        "detail": "Printed p.440 gives the bibliographic author form D. Maxwell White for the p.314 note 2 citation; retain this as a source form without external identity expansion.",
    },
    {
        "id": "cand-9897", "type": "person",
        "expected": "Sewter (author cited with White at p.314 note 2; identity unresolved)",
        "name": "A. C. Sewter",
        "detail": "Printed p.440 gives the bibliographic author form A. C. Sewter for the p.314 note 2 citation; retain this as a source form without external identity expansion.",
    },
    {
        "id": "cand-10903", "type": "archive",
        "expected": "Whitfield’s publication analysing Agucchi’s programme for Erminia and the Shepherds (title unspecified)",
        "name": "Clovis Whitfield, ‘A Programme for “Erminia and the Shepherds” by G. B. Agucchi’ (Storia dell’Arte, 1973, pp. 217–229)",
        "detail": "Printed p.440 supplies the title and issue details for the postscript note 4 Whitfield source. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-10902", "type": "person",
        "expected": "Whitfield (scholar cited for Agucchi’s programme; identity unresolved)",
        "name": "Clovis Whitfield",
        "detail": "Printed p.440 gives Clovis Whitfield as author of the listed article matching the postscript note 4 surname citation. This adds the source's name form only.",
    },
    {
        "id": "cand-9356", "type": "archive",
        "expected": "Whitley, vol.I, pp.9, 11, 24-26 (citation locator; work unresolved)",
        "name": "W. T. Whitley, Artists and their friends in England 1700–1799 (2 vols., London, 1928)",
        "detail": "Printed p.440 supplies the title, two-volume extent, place, and year for the p.287 note 4 volume I locators. The cited volume and pages were not independently consulted.",
    },
    {
        "id": "cand-9355", "type": "person",
        "expected": "Whitley (surname-only author in p.287 note 4; identity unresolved)",
        "name": "W. T. Whitley",
        "detail": "Printed p.440 gives the author form W. T. Whitley for the p.287 note 4 source. This records the bibliographic name form without further identity claims.",
    },
    {
        "id": "cand-6368", "type": "archive",
        "expected": "Wibiral (1960), cited publication, pp.123–165; title unspecified",
        "name": "N. Wibiral, ‘Contributi alle ricerche sul Cortonismo in Roma—I pittori della Galleria di Alessandro VII nel Palazzo del Quirinale’ (Bollettino d’Arte, 1960, pp. 123–165)",
        "detail": "Printed p.440 supplies the title and venue for the existing 1960 pp.123–165 source locator. The article and cited pages were not independently consulted.",
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
        "id": "cand-11450",
        "name": "Frances Vivian, ‘Joseph Smith, Giovanni Poleni and Antonio Visentini’ (Italian Studies, 1963, pp. 54–66)",
        "detail": "Bibliography entry at printed p.440. It is distinct in page range from the unresolved p.308 pp.157–162 citation cand-9560; compare rather than merge at S3. The article was not independently consulted.",
        "source_line": 1221,
        "related": ["cand-9553", "cand-9560"],
    },
    {
        "id": "cand-11451",
        "name": "F. J. B. Watson, Canaletto (London, 1949)",
        "detail": "Bibliography entry at printed p.440. The book was not independently consulted; author identity comparison remains available through person candidate cand-2803.",
        "source_line": 1235,
        "related": ["cand-2803"],
    },
    {
        "id": "cand-11452",
        "name": "E. K. Waterhouse, ‘Painting in Rome in the Eighteenth Century’ (Museum Studies, Art Institute of Chicago, 1971, pp. 7–21)",
        "detail": "Bibliography entry at printed p.440. The article was not independently consulted; the author is retained in the printed initial form.",
        "source_line": 1233,
        "related": ["cand-2802"],
    },
    {
        "id": "cand-11453",
        "name": "Mark S. Weil, The History and Decoration of the Ponte S. Angelo (Pennsylvania, 1974)",
        "detail": "Bibliography entry at printed p.440. The book was not independently consulted; compare with the surname-only author candidate cand-11178 at S3.",
        "source_line": 1247,
        "related": ["cand-11178"],
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


def record(candidate_id, start, end, author, title, details, kind, *, corrections=None, notes=None, related=None, quote=None, shared_line=False):
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
        "quote": quote,
        "shared_line": shared_line,
    }


line_1225 = source_lines[1224]
first_voss_tail, separator, second_voss_tail = line_1225.partition("Voss, EL:")
if not separator or not first_voss_tail.startswith("1926, pp.") or not second_voss_tail:
    raise SystemExit("OCR-merged Voss entries at L1225 have changed")
first_voss_quote = source_lines[1223] + "\n" + first_voss_tail.rstrip()
second_voss_quote = "Voss, EL:" + second_voss_tail.removesuffix(" ~")

entries = [
    record("cand-11450", 1221, 1222, "Vivian, Frances", "‘Joseph Smith, Giovanni Poleni and Antonio Visentini’", "Italian Studies, 1963, pp. 54–66", "journal article", related=["cand-9553", "cand-9560"], notes=["The pp.54–66 bibliography entry differs from the unresolved p.308 pp.157–162 locator; keep separate for S3 comparison."]),
    record("cand-11092", 1223, 1223, "Vivian, Frances", "Il Console Smith mercante e collezionista", "Vicenza 1971", "book", related=["cand-9553"]),
    record("cand-9359", 1224, 1225, "Voss, H.", "‘Gio Antonio Canal und Owen McSwiny’", "Repertorium für Kunstwissenschaft, 1926, pp. 32–37", "journal article", quote=first_voss_quote, shared_line=True, corrections=[{"line": 1224, "ocr": "Voss, EL", "print": "Voss, H.", "note": "The page image clearly reads H.; OCR confuses the letter with EL."}, {"line": 1225, "ocr": "pp. 32-37Voss, EL:", "print": "pp. 32–37. / Voss, H.:", "note": "The page image shows the first article ending before a separate second Voss entry; OCR merged the two and omitted the period."}], related=["cand-9358"]),
    record("cand-5875", 1225, 1225, "Voss, H.", "‘Die Flucht nach Aegypten’", "Saggi e Memorie di Storia dell’Arte, Venezia 1957, pp. 25–61", "journal article", quote=second_voss_quote, shared_line=True, corrections=[{"line": 1225, "ocr": "Voss, EL", "print": "Voss, H.", "note": "The page image reads H.; the trailing tilde after the entry is a scan/OCR artifact."}], related=["cand-9358", "cand-5874"]),
    record("cand-4570", 1226, 1226, "Walker, D. P.", "Spiritual and demonic magic from Ficino to Campanella", "London 1958", "book", related=["cand-4571"]),
    record("cand-7001", 1227, 1227, "Walker, J.", "Bellini and Titian at Ferrara", "London 1956", "book", corrections=[{"line": 1227, "ocr": "Walker,}.", "print": "Walker, J.", "note": "The page image reads initial J."}, {"line": 1227, "ocr": "London 1956. ,", "print": "London 1956.", "note": "The trailing comma in OCR is not in the print."}]),
    record("cand-7058", 1228, 1228, "Walpole, Horace", "Anecdotes of Painting in England", "5 vols., Strawberry Hill 1726 (as printed)", "book set", related=["cand-2798"], notes=["The bibliography prints 1726 while an earlier locator represented by this candidate says 1762, vol.II, p.51; preserve the discrepancy for S3 edition comparison."]),
    record("cand-8596", 1229, 1229, "Walpole, Horace", "Aedes Walpoliane", "3rd edition, London 1767", "book", related=["cand-2798"], notes=["Retain the printed title spelling Walpoliane."]),
    record("cand-6580", 1230, 1231, "Waterhouse, E. K.", "‘Some Old Masters other than Spanish at the Bowes Museum’", "Burlington Magazine, 1953, pp. 120–123", "journal article", related=["cand-2802", "cand-6581"]),
    record("cand-7259", 1232, 1232, "Waterhouse, E. K.", "‘A note on British collecting of Italian pictures in the later seventeenth century’", "Burlington Magazine, 1960, pp. 54–58", "journal article", corrections=[{"line": 1232, "ocr": "i960", "print": "1960", "note": "The page image reads 1960."}], related=["cand-2802"]),
    record("cand-11452", 1233, 1234, "Waterhouse, E. K.", "‘Painting in Rome in the Eighteenth Century’", "Museum Studies, Art Institute of Chicago, 1971, pp. 7–21", "journal article", corrections=[{"line": 1234, "ocr": "pp7-21", "print": "pp. 7–21", "note": "The page image confirms the punctuation and range."}], related=["cand-2802"]),
    record("cand-11451", 1235, 1235, "Watson, F. J. B.", "Canaletto", "London 1949", "book", related=["cand-2803"]),
    record("cand-9354", 1236, 1237, "Watson, F. J. B.", "‘The Nazari—a forgotten family of Venetian portrait painters’", "Burlington Magazine, 1949, pp. 75–79", "journal article", related=["cand-9353", "cand-2803"]),
    record("cand-9367", 1238, 1239, "Watson, F. J. B.", "‘An allegorical painting by Canaletto, Piazzetta and Cimaroli’", "Burlington Magazine, 1953, pp. 362–365", "journal article", related=["cand-9353", "cand-2803"]),
    record("cand-9316", 1240, 1241, "Watson, F. J. B.", "‘A Venetian Settecento chapel in the English countryside’", "Arte Veneta, 1954, pp. 295–301", "journal article", corrections=[{"line": 1241, "ocr": "pp295-301", "print": "pp. 295–301", "note": "Restore the page-range punctuation shown in print."}], related=["cand-2803"]),
    record("cand-9301", 1242, 1243, "Watson, F. J. B.", "‘English villas and Venetian decorators’", "Journal of the Royal Institute of British Architects, 1954, pp. 11–177 (as printed)", "journal article", corrections=[{"line": 1242, "ocr": "fournal", "print": "Journal", "note": "The page image confirms Journal."}], related=["cand-2803"], notes=["Printed p.440 appears to read pp.11–177, while the earlier p.279 note 1 citation gives pp.171–177; preserve both source forms for S3 comparison."]),
    record("cand-10304", 1244, 1244, "Watson, F. J. B.", "‘Giovanni Battista Tiepolo: a masterpiece and a book’", "Connoisseur, 1955, vol. 136, pp. 212–215", "journal article", related=["cand-2803"]),
    record("cand-9893", 1245, 1246, "Watson, F. J. B.", "‘A series of “Turqueries” by Francesco Guardi’", "Baltimore Museum of Arts Quarterly, Fall 1960, pp. 3–13", "journal article", corrections=[{"line": 1246, "ocr": "Fall i960", "print": "Fall 1960", "note": "The page image reads 1960."}], related=["cand-2803"]),
    record("cand-11453", 1247, 1247, "Weil, Mark S.", "The History and Decoration of the Ponte S. Angelo", "Pennsylvania 1974", "book", related=["cand-11178"]),
    record("cand-7267", 1248, 1248, "Wells, W.", "‘Shaftesbury and Paolo de Matteis’", "Leeds Art Quarterly, Spring 1950, pp. 23–28", "journal article", corrections=[{"line": 1248, "ocr": "pp. 2328", "print": "pp. 23–28", "note": "The page image confirms the range split over the line ending."}]),
    record("cand-11180", 1249, 1250, "Wethey, Harold R.", "‘The Spanish Viceroy, Luca Giordano and Andrea Vaccaro’", "Burlington Magazine, 1967, pp. 678–686", "journal article", corrections=[{"line": 1250, "ocr": "pp. 678-686. -", "print": "pp. 678–686.", "note": "The trailing dash is a scan/OCR mark."}], related=["cand-10990"]),
    record("cand-9349", 1251, 1251, "Wheatley, H. B.", "London past and present", "London 1891", "book", related=["cand-9348"]),
    record("cand-7066", 1252, 1252, "Whinney, M. and Millar, O.", "English Art, 1625–1714", "Oxford 1957", "book", related=["cand-7067", "cand-7068"], notes=["A preceding ~\" in the OCR is a scan/list artifact, not part of this entry."]),
    record("cand-9898", 1253, 1253, "White, D. Maxwell and Sewter, A. C.", "‘Piazzetta’s so-called Group on the Sea shore’", "Connoisseur, 1959, vol. 143, pp. 96–100", "journal article", related=["cand-9896", "cand-9897"]),
    record("cand-10903", 1254, 1255, "Whitfield, Clovis", "‘A Programme for “Erminia and the Shepherds” by G. B. Agucchi’", "Storia dell’Arte, 1973, pp. 217–229", "journal article", related=["cand-10902"]),
    record("cand-9356", 1256, 1256, "Whitley, W. T.", "Artists and their friends in England 1700–1799", "2 vols., London 1928", "book set", related=["cand-9355"]),
    record("cand-6368", 1257, 1258, "Wibiral, N.", "‘Contributi alle ricerche sul Cortonismo in Roma—I pittori della Galleria di Alessandro VII nel Palazzo del Quirinale’", "Bollettino d’Arte, 1960, pp. 123–165", "journal article", corrections=[{"line": 1258, "ocr": "i960", "print": "1960", "note": "The page image reads 1960."}], related=["cand-6367"]),
    record("cand-7185", 1259, 1259, "Wilhelm, F.", "‘Neue Quellen zur Geschichte des fürstlich Liechtensteinschen Kunstbesitzes’", "Bibliographic details continue on the next printed page (source lines 1262–1263)", "journal article", related=["cand-7184"], notes=["Record only the p.440 title fragment here; complete venue and page range from the continuation in the next S2 segment before treating the bibliographic record as complete."]),
]

if len(candidate_updates) != 28 or len(new_candidates) != 4 or len(entries) != 28:
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
line_owners = {}
new_spans = []


def source_quote(item):
    if item["quote"] is not None:
        return item["quote"]
    return "\n".join(source_lines[item["start"] - 1 : item["end"]])


for index, item in enumerate(entries, start=1):
    candidate_id = item["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {candidate_id}")
    for related_id in item["related"]:
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    for line in range(item["start"], item["end"] + 1):
        owners = line_owners.setdefault(line, [])
        if owners and not (
            line == 1225
            and item["shared_line"]
            and all(owner["shared_line"] for owner in owners)
        ):
            raise SystemExit(f"overlapping publication line range at L{line}: {candidate_id}")
        owners.append(item)
    covered_lines |= set(range(item["start"], item["end"] + 1))

    quote = source_quote(item)
    positions = [i for i in range(len(segment_text)) if segment_text.startswith(quote, i)]
    if len(positions) != 1:
        raise SystemExit(f"source quote must occur once: {candidate_id} L{item['start']}")
    start_char = positions[0]
    end_char = start_char + len(quote)
    mention_id = f"m-chp21-bib-l1220-1259-{index:03d}"
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
        note="S0 bibliography entry; page-image readings, cross-page continuation, and S3 comparisons are recorded on its statement.",
    )
    new_mentions.append(mention_row)
    mention_ids.add(mention_id)
    mention_keys.add(mention_key)
    new_spans.append((start_char, end_char))

    statement_id = f"st-chp21-bib-l1220-1259-entry-{index:02d}"
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
            "printed_page": 440,
            "pdf_physical_page": 30,
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

if covered_lines != set(range(1221, 1260)):
    raise SystemExit(f"bibliography lines not covered exactly: {sorted(set(range(1221, 1260)) - covered_lines)}")
if len(line_owners.get(1225, [])) != 2 or not all(row["shared_line"] for row in line_owners[1225]):
    raise SystemExit("the merged OCR line 1225 was not split into two entries")
if len(new_mentions) != 28 or len(new_statements) != 28:
    raise SystemExit("unexpected mention/statement counts")
if any(new_spans[i][1] > new_spans[i + 1][0] for i in range(len(new_spans) - 1)):
    raise SystemExit("mention character spans overlap")

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
    source_line_ranges="L1221-1259",
    note="Printed p.440: 28 publication entries reviewed and page-image checked; Wilhelm entry continues on p.441; see process/stages.md.",
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
    "candidate_count": 11432,
    "mention_count": 26798,
    "statement_count": 12071,
    "coverage_complete": 615,
    "coverage_queued": 96,
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
