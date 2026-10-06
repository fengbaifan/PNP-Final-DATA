#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 439."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l1179-1218"
SEGMENT_SHA = "ac051b424f2edea683db2a6cacf1a96c5f54b0cb5929c9ba3aa0400e41afa60e"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l1141-1177"
BACKUP_SUFFIX = ".bak-s2-chp21-bibliography-l1179-1218-20261007"

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
segment_text = "\n".join(source_lines[1178:1218])
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
) != (SOURCE_FILE, 1179, 1218, SEGMENT_SHA, SOURCE_SHA):
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
    11420,
    26742,
    12015,
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
        "id": "cand-11192", "type": "archive",
        "expected": "Twilight of the Medici (catalogue cited at p.404 note 9)",
        "name": "Twilight of the Medici—Late Baroque Art in Florence 1670–1743 (Detroit and Florence, 1974)",
        "detail": "Printed p.439 supplies the full catalogue title and Detroit/Florence 1974 publication details for the p.404 note 9 citation. The catalogue and exhibition were not independently consulted.",
    },
    {
        "id": "cand-8793", "type": "archive",
        "expected": "Urbani de Ghelthof, 1879 (citation locator; cited pp.100-117, 123-126)",
        "name": "G. M. Urbani de Ghelthof, Tiepolo e la sua Famiglia (Venezia, 1879)",
        "detail": "Printed p.439 identifies the title and publication place/year for the 1879 source already cited at pp.19, 32, 100–117, and 123–126. The work and those cited pages were not independently consulted.",
    },
    {
        "id": "cand-11198", "type": "archive",
        "expected": "Urbino: Restauri, publication cited at p.404 note 19, pp. 532-52",
        "name": "Urbino—Restauri nelle Marche: testimonianze, acquisti e recuperi (1973)",
        "detail": "Printed p.439 supplies the full title and year for the p.404 note 19 short citation. The cited pp.532–552 and the publication were not independently consulted; the match is retained for comparison.",
    },
    {
        "id": "cand-4844", "type": "archive",
        "expected": "Vaes (1924), cited publication; title unspecified",
        "name": "M. Vaes, ‘Le séjour de Van Dyck en Italie’ (Bulletin de l’Institut Belge de Rome, 1924, pp. 163–234)",
        "detail": "Printed p.439 supplies the article title, journal, year, and page range for the p.211 note 3 Vaes 1924 p.211 locator. The article and cited page were not independently consulted.",
    },
    {
        "id": "cand-6997", "type": "archive",
        "expected": "Vaes (1931), cited publication at p.202; title unspecified",
        "name": "M. Vaes, ‘Appunti di Carel van Mander su vari pittori italiani suoi contemporanei’ (Roma, 1931, pp. 193–208)",
        "detail": "Printed p.439 supplies the title and full page range containing the p.170 note 1 p.202 locator. The item and cited page were not independently consulted.",
    },
    {
        "id": "cand-11116", "type": "archive",
        "expected": "Thomas J. McCormick's catalogue of selections from Vassar College Art Gallery",
        "name": "Vassar College Art Gallery—Selections from the Permanent Collection (Poughkeepsie, N.Y., 1967)",
        "detail": "Printed p.439 identifies the full catalogue title, place, and year. The postscript describes Thomas J. McCormick as publishing the cited canvas in his catalogue; the catalogue and p.24 were not independently consulted. Keep distinct from institution cand-11115.",
    },
    {
        "id": "cand-8798", "type": "archive",
        "expected": "Alberto Vecchi, 1960 (citation locator; title pending bibliography review)",
        "name": "A. Vecchi, La vita spirituale in ‘La Civiltà Veneziana del Settecento’ (Venezia, 1960)",
        "detail": "Printed p.439 supplies the title and publication details for the p.271 note 3 Alberto Vecchi 1960 citation. The work was not independently consulted; the note’s pronoun antecedent remains unresolved separately.",
    },
    {
        "id": "cand-11209", "type": "archive",
        "expected": "Franco Venturi, 1969 publication cited at p.408 notes 1-2 (title unspecified)",
        "name": "F. Venturi, Settecento riformatore (2 vols., Torino, 1969 and 1976)",
        "detail": "Printed p.439 lists one two-volume work with publication years 1969 and 1976. This expands the p.408 1969 locator cand-11209; retain the separate 1976 locator cand-11210 for S3 comparison. Neither volume nor cited page was independently consulted.",
    },
    {
        "id": "cand-5690", "type": "archive",
        "expected": "Vermeule, 1956, pp.32–46 (publication title unspecified)",
        "name": "C. Vermeule, ‘The dal Pozzo-Albani drawings of classical antiquities’ (Art Bulletin, 1956, pp. 32–46)",
        "detail": "Printed p.439 supplies the title and periodical details for the p.4 cited 1956 modern treatment. The article and cited pages were not independently consulted; author identity remains represented by the printed initial.",
    },
    {
        "id": "cand-8435", "type": "archive",
        "expected": "Villot, pages 169–176 (citation locator)",
        "name": "Frédéric Villot, ‘Lettre de Charles-Nicolas Cochin sur les artistes de son temps’ (Archives de l’Art Français, vol. I, 1851–52, pp. 169–176)",
        "detail": "Printed p.439 identifies the title and volume/year/page details for the p.257 note 6 Villot locator. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-8434", "type": "person",
        "expected": "Villot (surname-only citation form in p.257 note 6)",
        "name": "Frédéric Villot",
        "detail": "The p.257 note cites Villot pp.169–176; printed p.439 gives the author form Villot, Frédéric for the matching page range. This supplies the bibliographic name form without adding biographical claims.",
    },
    {
        "id": "cand-10905", "type": "archive",
        "expected": "Viola’s study of Giambattista Marino’s collecting and approach to art (title unspecified)",
        "name": "Gianni Eugenio Viola, Il verso di Narciso—tre tesi sulla poetica di Giovan Battista Marino (Roma, 1978)",
        "detail": "Printed p.439 supplies a full 1978 title by Gianni Eugenio Viola. It is a possible match for the p.398 note 5 surname-only citation about Marino and collecting, but its relevance is not demonstrated by the bibliography alone; compare in S3. The book was not consulted.",
    },
    {
        "id": "cand-10904", "type": "person",
        "expected": "Viola (scholar cited on Giambattista Marino’s collecting; identity unresolved)",
        "detail": "Printed p.439 lists a 1978 work by Gianni Eugenio Viola that may match the p.398 note 5 surname-only citation. Retain the candidate’s identity as unresolved pending S3 comparison; the book was not consulted.",
    },
    {
        "id": "cand-4728", "type": "archive",
        "expected": "Unidentified Vitzthum study cited on the Barberini ceiling (1961, pp. 427-433)",
        "name": "W. Vitzthum, ‘A comment on the iconography of Pietro da Cortona’s Barberini ceiling’ (Burlington Magazine, 1961, pp. 427–433)",
        "detail": "Printed p.439 supplies the title and journal details for the p.4 and p.96 note Vitzthum 1961 pp.427–433 citations. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-5692", "type": "archive",
        "expected": "Vitzthum publication cited in 1961, pp.513–518 (title unspecified)",
        "name": "W. Vitzthum, ‘Roman drawings at Windsor Castle’ (Burlington Magazine, 1961, pp. 513–518)",
        "detail": "Printed p.439 supplies the title and page range for the p.4 note 2 source said to add Windsor drawings. The article and cited pages were not independently consulted.",
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
        "id": "cand-11442",
        "name": "S. Ubaldi, I Buonaccorsi a Macerata, cenni storici (Macerata, 1950)",
        "detail": "Bibliography entry at printed p.439. The book was not independently consulted; compare with the previously mentioned Silvio Ubaldi candidate cand-7734.",
        "source_line": 1181,
    },
    {
        "id": "cand-11443",
        "name": "F. Valcanover, ‘Per Luca Carlevaris’ (Arte Veneta, 1952, pp. 193–194)",
        "detail": "Bibliography entry at printed p.439. The article and cited pages were not independently consulted; author identity is not expanded beyond the printed initial.",
        "source_line": 1190,
    },
    {
        "id": "cand-11444",
        "name": "J. Valfrey, Hugues de Lionne—ses ambassades en Italie 1642–1656 (Paris, 1877)",
        "detail": "Bibliography entry at printed p.439. The work was not independently consulted; author identity is not expanded beyond the printed initial.",
        "source_line": 1193,
    },
    {
        "id": "cand-11445",
        "name": "G. della Valle, Lettere Sanesi (3 vols., Roma, 1782–86)",
        "detail": "Bibliography entry at printed p.439. The three-volume set was not independently consulted; retain the printed abbreviated author form.",
        "source_line": 1194,
    },
    {
        "id": "cand-11446",
        "name": "G. da Venezia, ‘Il Metastasio di P. A. Novelli’ (Rivista di Venezia, 1934, pp. 25–34)",
        "detail": "Bibliography entry at printed p.439. The article was not independently consulted; preserve the printed author form without expanding the given name.",
        "source_line": 1198,
    },
    {
        "id": "cand-11447",
        "name": "Venise au dix-huitième siècle (Paris, Orangerie, 1971)",
        "detail": "Bibliography entry at printed p.439. The exhibition publication was not independently consulted; do not treat the title as a separate event entity.",
        "source_line": 1199,
    },
    {
        "id": "cand-11448",
        "name": "F. Venturi, ‘Un amico di Beccaria e di Verri: Profilo di Giambattista Biffi’ (Giornale Storico della Letteratura Italiana, 1957, pp. 37–76)",
        "detail": "Bibliography entry at printed p.439. The article was not independently consulted; compare the printed author initial to the existing Franco Venturi person candidate cand-2751 at S3.",
        "source_line": 1201,
    },
    {
        "id": "cand-11449",
        "name": "Don Giovanni Vianelli, Catalogo di quadri esistenti in casa il signor Don Giovanni Dr Vianelli canonico della cattedrale di Chioggia (Venezia, 1790)",
        "detail": "Bibliography entry at printed p.439. The catalogue was not independently consulted; preserve its printed title and author form.",
        "source_line": 1208,
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
    record("cand-11192", 1180, 1180, "", "Twilight of the Medici—Late Baroque Art in Florence 1670–1743", "Detroit and Florence 1974", "exhibition catalogue"),
    record("cand-11442", 1181, 1181, "Ubaldi, S.", "I Buonaccorsi a Macerata, cenni storici", "Macerata 1950", "book", related=["cand-7734"], notes=["Possible match to the earlier mention of Silvio Ubaldi; the bibliography entry itself does not prove the old citation mapping."]),
    record("cand-8793", 1182, 1182, "Urbani de Ghelthof, G. M.", "Tiepolo e la sua Famiglia", "Venezia 1879", "book"),
    record("cand-11198", 1183, 1183, "", "Urbino—Restauri nelle Marche: testimonianze, acquisti e recuperi", "1973", "exhibition catalogue", notes=["Likely title match to the p.404 note 19 citation; the cited pp.532–552 and catalogue were not consulted."]),
    record("cand-4844", 1184, 1185, "Vaes, M.", "‘Le séjour de Van Dyck en Italie’", "Bulletin de l’Institut Belge de Rome, 1924, pp. 163–234", "journal article", corrections=[{"line": 1184, "ocr": "Bulletin de ITnstitut Belge de Rome", "print": "Bulletin de l’Institut Belge de Rome", "note": "The page image confirms the journal’s printed name; the OCR misread the initial l and apostrophe."}, {"line": 1185, "ocr": "1Ó3-234", "print": "163–234", "note": "The page image reads 163–234."}], related=["cand-6386"]),
    record("cand-7584", 1186, 1187, "Vaes, M.", "‘Corneille de Wael (1592–1667)’", "Bulletin de l’Institut Belge de Rome, 1925, pp. 137–247", "journal article", related=["cand-6387"], notes=["The p.171 locator represented by cand-6387 falls within this printed page range and may identify this same article; preserve the separate citation candidate for S3 comparison."]),
    record("cand-6997", 1188, 1189, "Vaes, M.", "‘Appunti di Carel van Mander su vari pittori italiani suoi contemporanei’", "Roma, 1931, pp. 193–208", "journal article", corrections=[{"line": 1189, "ocr": "pp. 193-208. - ' ", "print": "pp. 193–208.", "note": "The trailing dash/apostrophe marks are scan/OCR artifacts, not part of the printed entry."}], related=["cand-6386"]),
    record("cand-11443", 1190, 1190, "Valcanover, F.", "‘Per Luca Carlevaris’", "Arte Veneta, 1952, pp. 193–194", "journal article"),
    record("cand-7621", 1191, 1192, "Valery, A. C. P.", "Voyages historiques, littéraires et artistiques en Italie", "2ème édition, 3 vols., Paris 1838", "book"),
    record("cand-11444", 1193, 1193, "Valfrey, J.", "Hugues de Lionne—ses ambassades en Italie 1642–1656", "Paris 1877", "book"),
    record("cand-11445", 1194, 1194, "Valle, G. della", "Lettere Sanesi", "3 vols., Roma 1782–86", "book set"),
    record("cand-11116", 1195, 1196, "Vassar College Art Gallery", "Selections from the Permanent Collection", "Poughkeepsie, N.Y. 1967", "exhibition catalogue", related=["cand-11115"]),
    record("cand-8798", 1197, 1197, "Vecchi, A.", "La vita spirituale in ‘La Civiltà Veneziana del Settecento’", "Venezia 1960", "book chapter", related=["cand-8797"]),
    record("cand-11446", 1198, 1198, "Venezia, G. da", "‘Il Metastasio di P. A. Novelli’", "Rivista di Venezia, 1934, pp. 25–34", "journal article"),
    record("cand-11447", 1199, 1199, "", "Venise au dix-huitième siècle", "Paris (Orangerie), 1971", "exhibition catalogue"),
    record("cand-4354", 1200, 1200, "Venturi, A.", "La R. Galleria Estense in Modena", "Modena 1883", "book", related=["cand-7054"]),
    record("cand-11448", 1201, 1201, "Venturi, F.", "‘Un amico di Beccaria e di Verri: Profilo di Giambattista Biffi’", "Giornale Storico della Letteratura Italiana, 1957, pp. 37–76", "journal article", related=["cand-2751"]),
    record("cand-11209", 1202, 1202, "Venturi, F.", "Settecento riformatore", "2 vols., Torino 1969 and 1976", "book set", related=["cand-11210"], notes=["The bibliography lists one two-volume work; the previously recorded 1976 locator cand-11210 remains separate pending S3 alignment."]),
    record("cand-5690", 1203, 1203, "Vermeule, C.", "‘The dal Pozzo-Albani drawings of classical antiquities’", "Art Bulletin, 1956, pp. 32–46", "journal article", related=["cand-5689"]),
    record("cand-7255", 1204, 1205, "Vertue, George", "Notebooks", "published in 6 vols., and an index by the Walpole Society, XVIII, XX, XXII, XXIV, XXVI, XXIX, XXX (1930–55)", "book set", related=["cand-8933"], notes=["Preserve the printed distinction between six volumes and a separate index; this is not a seven-volume set assertion."]),
    record("cand-9471", 1206, 1207, "Viale, V.", "‘Un dipinto del Pannini con la veduta orientale del Castello di Rivoli secondo il progetto originale di Filippo Juvarra’", "Bollettino della Società Piemontese di Archeologia e Belle Arti, 1950–1, pp. 161–169", "journal article", corrections=[{"line": 1207, "ocr": "pp. 161-169. -", "print": "pp. 161–169.", "note": "The trailing dash is a scan/OCR mark; page image confirms the article page range."}]),
    record("cand-11449", 1208, 1208, "Vianelli, Don Giovanni", "Catalogo di quadri esistenti in casa il signor Don Giovanni Dr Vianelli canonico della cattedrale di Chioggia", "Venezia 1790", "book/catalogue"),
    record("cand-7588", 1209, 1210, "Ville sur-Yllon, Ludovico de la", "‘Il palazzo dei duchi di Maddaloni alla Stella’", "Napoli Nobilissima, 1904, pp. 145–147", "journal article"),
    record("cand-8435", 1211, 1211, "Villot, Frédéric", "‘Lettre de Charles-Nicolas Cochin sur les artistes de son temps’", "Archives de l’Art Français, vol. I, 1851–2, pp. 169–176", "journal article", corrections=[{"line": 1211, "ocr": "_ Villot", "print": "Villot", "note": "The page image has no leading underscore; it is an OCR/list marker artifact."}, {"line": 1211, "ocr": "pp. 169-176. ' ", "print": "pp. 169–176.", "note": "The trailing apostrophe is not part of the printed entry."}], related=["cand-8434"]),
    record("cand-10905", 1212, 1213, "Viola, Gianni Eugenio", "Il verso di Narciso—tre tesi sulla poetica di Giovan Battista Marino", "Roma 1978", "book", related=["cand-10904"], notes=["Possible match to the p.398 note 5 surname-only source cited on Marino and collecting; confirm the mapping in S3 because the bibliography title alone does not prove relevance."]),
    record("cand-4728", 1214, 1215, "Vitzthum, W.", "‘A comment on the iconography of Pietro da Cortona’s Barberini ceiling’", "Burlington Magazine, 1961, pp. 427–433", "journal article", corrections=[{"line": 1215, "ocr": "pp. 427-43 3.", "print": "pp. 427–433.", "note": "The page image confirms pp.427–433; OCR inserted a space into the final page number."}], related=["cand-4727"]),
    record("cand-5692", 1216, 1216, "Vitzthum, W.", "‘Roman drawings at Windsor Castle’", "Burlington Magazine, 1961, pp. 513–518", "journal article", corrections=[{"line": 1216, "ocr": "pp. 513518. ,", "print": "pp. 513–518.", "note": "The page image confirms the hyphenated page range; the trailing comma is an OCR artifact."}], related=["cand-4727"]),
    record("cand-9552", 1217, 1218, "Vivian, Frances", "‘Joseph Smith and Giovanni Antonio Pellegrini’", "Burlington Magazine, 1962, pp. 330–333", "journal article", corrections=[{"line": 1218, "ocr": "pp. 330-333-", "print": "pp. 330–333.", "note": "The page image ends the locator with a period, not a hyphen."}]),
]

if len(candidate_updates) != 15 or len(new_candidates) != 8 or len(entries) != 28:
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
new_spans = []

for index, item in enumerate(entries, start=1):
    candidate_id = item["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {candidate_id}")
    for related_id in item["related"]:
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    covered_lines |= set(range(item["start"], item["end"] + 1))
    quote = "\n".join(source_lines[item["start"] - 1 : item["end"]])
    positions = [i for i in range(len(segment_text)) if segment_text.startswith(quote, i)]
    if len(positions) != 1:
        raise SystemExit(f"source quote must occur once: {candidate_id} L{item['start']}")
    start_char = positions[0]
    end_char = start_char + len(quote)
    mention_id = f"m-chp21-bib-l1179-1218-{index:03d}"
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
    new_spans.append((start_char, end_char))

    statement_id = f"st-chp21-bib-l1179-1218-entry-{index:02d}"
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
            "printed_page": 439,
            "pdf_physical_page": 29,
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

if covered_lines != set(range(1180, 1219)):
    raise SystemExit(f"bibliography lines not covered exactly: {sorted(set(range(1180, 1219)) - covered_lines)}")
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
    source_line_ranges="L1180-1218",
    note="Printed p.439: 28 publication records reviewed and page-image checked; see process/stages.md.",
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
    "candidate_count": 11428,
    "mention_count": 26770,
    "statement_count": 12043,
    "coverage_complete": 614,
    "coverage_queued": 97,
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
