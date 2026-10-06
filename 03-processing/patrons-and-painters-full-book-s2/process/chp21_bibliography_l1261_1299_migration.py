#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 441."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l1261-1299"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l1220-1259"
SEGMENT_SHA = "5697180322dc12ae45bcab87bc06b903f0c5587eaf971fc1f14b2c5ab8d3bbf8"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
BACKUP_SUFFIX = ".bak-s2-chp21-bibliography-l1261-1299-20261007"

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
segment_text = "\n".join(source_lines[1260:1299])
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
) != (SOURCE_FILE, 1261, 1299, SEGMENT_SHA, SOURCE_SHA):
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
    11432,
    26798,
    12071,
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
        "id": "cand-7185",
        "type": "archive",
        "expected": "Neue Quellen zur Geschichte des fürstlich Liechtensteinschen Kunstbesitzes (F. Wilhelm, 1911)",
        "name": "F. Wilhelm, ‘Neue Quellen zur Geschichte des fürstlich Liechtensteinschen Kunstbesitzes’ (Jahrbuch des Kunsthistorischen Institutes der K.K. Zentralkommission, 1911, Beiblatt, pp. 87–142)",
        "detail": "The title begins on printed p.440 and the continuation on printed p.441 supplies Jahrbuch des Kunsthistorischen Institutes der K.K. Zentralkommission, 1911, Beiblatt, pp.87–142. The article and cited pages were not independently read.",
    },
    {
        "id": "cand-7230",
        "type": "archive",
        "expected": "E. Wind, ‘Julian the Apostate at Hampton Court’ (1939–40)",
        "name": "E. Wind, ‘Julian the Apostate at Hampton Court’ (Journal of the Warburg and Courtauld Institutes, III, 1939–40, pp. 127–137)",
        "detail": "Printed p.441 confirms the complete bibliography form, volume III, years 1939–40, and pp.127–137. The article and cited pages were not independently read.",
    },
    {
        "id": "cand-7111",
        "type": "archive",
        "expected": "Domenico Guidi and French classicism (Rudolf Wittkower; Journal of the Warburg and Courtauld Institutes, II, 1938–39, pp. 188–190)",
        "detail": "Printed p.441 lists this article as a separate Wittkower publication. The p.189 note 2 locator matches its year; the article and cited pages were not independently read.",
    },
    {
        "id": "cand-9311",
        "type": "archive",
        "expected": "Wittkower, 1948 (citation locator; title unresolved)",
        "name": "R. Wittkower, The Earl of Burlington and William Kent (York Georgian Society, 1948)",
        "detail": "Printed p.441 supplies the title, publisher, and year for the p.280 note 6 locator. The book and cited passage were not independently read.",
    },
    {
        "id": "cand-4383",
        "type": "archive",
        "expected": "Wittkower, The Sculptures of Gian Lorenzo Bernini (London, 1955)",
        "detail": "Printed p.441 lists the London 1955 book; the existing candidate records the chapter 2 citation locators. The book and cited pages were not independently read.",
    },
    {
        "id": "cand-4557",
        "type": "archive",
        "expected": "Art and architecture in Italy 1600 to 1750 (London, 1958)",
        "detail": "Printed p.441 confirms the 1958 edition details for the existing citation candidate. The page image reads 1958; the book and cited pages were not independently read.",
    },
    {
        "id": "cand-11170",
        "type": "archive",
        "expected": "Wittkower, 1966 publication cited at p.401 note 3 (title and edition unspecified)",
        "name": "R. Wittkower, Gian Lorenzo Bernini—the Sculptor of the Roman Baroque (2nd ed., London, 1966)",
        "detail": "Printed p.441 identifies the title and second edition for the p.401 note 3 locator, pp.203–204. The book and cited pages were not independently read.",
    },
    {
        "id": "cand-11368",
        "type": "archive",
        "expected": "R. Wittkower and Irma Jaffe (eds.), Baroque Art: The Jesuit Contribution (New York, 1972)",
        "name": "R. Wittkower and Irma Jaffé (eds.), Baroque Art: The Jesuit Contribution (New York, 1972)",
        "detail": "Printed p.441 confirms the edited volume and spells the editor's name Jaffé. The page-image correction and possible connection to the p.398 note 7 source remain explicit; the volume and cited pages were not independently read.",
    },
    {
        "id": "cand-9010",
        "type": "archive",
        "expected": "J. Woodward, ‘Amigoni as portrait painter in England’ (1957)",
        "name": "J. Woodward, ‘Amigoni as portrait painter in England’ (Burlington Magazine, 1957, pp. 21–23)",
        "detail": "Printed p.441 confirms the complete venue and page range for the p.215 note 2 citation. The article and cited pages were not independently read.",
    },
    {
        "id": "cand-10534",
        "type": "archive",
        "expected": "Giustiniana Wynne-Rosenberg, Alticchiero (Venezia, 1787)",
        "name": "Giustiniana Wynne-Rosenberg, Alticchiero (à Padoue, 1787 [as printed])",
        "detail": "Printed p.441 reads ‘à Padoue 1787’, while the earlier candidate form says Venezia 1787. Preserve this place-form discrepancy for S3/source comparison; the edition was not independently consulted.",
    },
    {
        "id": "cand-9548",
        "type": "archive",
        "expected": "Prosdocimo Zabeo, Memorie intorno l'antiquario Alvise Meneghetti (Venice, 1816)",
        "name": "Prosdocimo Zabeo, Memorie intorno l’antiquario Alvise Meneghetti (Venezia, 1816)",
        "detail": "Printed p.441 lists this publication; it is a possible source for the p.16 appraisal of Smith's medal cabinet. The cited page and book were not independently read, so source suitability is not asserted.",
    },
    {
        "id": "cand-10117",
        "type": "archive",
        "expected": "Varie Pitture a Fresco (1760)",
        "name": "A. M. Zanetti, Varie pitture a fresco de’ principali maestri veneziani (Venezia, 1760)",
        "detail": "Printed p.441 gives the full title and publication details for the younger-Zanetti passage cited at p.343 note 2. The book was not independently read; author alignment remains for S3.",
    },
    {
        "id": "cand-9837",
        "type": "archive",
        "expected": "Della Pittura Veneziana (Venezia, 1771)",
        "name": "A. M. Zanetti, Della Pittura Veneziana (Venezia, 1771)",
        "detail": "Printed p.441 confirms the bibliography author form A. M. Zanetti and the Venezia 1771 details for p.329 note 1. The work was not independently read; author alignment remains for S3.",
    },
    {
        "id": "cand-9281",
        "type": "archive",
        "expected": "Girolamo Zanetti, Elogio (1781; published 1818)",
        "name": "Girolamo Zanetti, Elogio di Rosalba Carriera letto in una privata sessione dell’Accademia di Belle Lettere ed Arti in Padova il di 6 Dicembre 1781 (Venezia, 1818)",
        "detail": "Printed p.441 supplies the complete title and Venezia 1818 publication details. Keep the title's Padova reading date, 6 December 1781, distinct from publication in 1818; the text was not independently read.",
    },
    {
        "id": "cand-7115",
        "type": "archive",
        "expected": "Storia dell’Accademia Clementina (G. P. Zanotti, 2 vols., Bologna 1739)",
        "detail": "Printed p.441 confirms the two-volume Storia dell’Accademia Clementina citation; existing page locators remain attached to this candidate. The books and cited pages were not independently read; author identity remains for S3.",
    },
    {
        "id": "cand-8794",
        "type": "archive",
        "expected": "Zarzabini, p.19 (citation locator; title pending)",
        "name": "Padre Maestro Valerio Antonio Zarzabini, Serie storica de’ Religiosi Carmelitani (Venezia, 1779)",
        "detail": "Printed p.441 supplies the title, author form, place, and year for the p.270 note 6 p.19 citation. The book and cited page were not independently read.",
    },
    {
        "id": "cand-5166",
        "type": "archive",
        "expected": "Zeri (1953), cited publication; title unspecified",
        "name": "F. Zeri, La Galleria Spada in Roma (Firenze, 1953)",
        "detail": "Printed p.441 supplies the title and publication details for the existing p.175 citation. The book and cited pages were not independently read.",
    },
    {
        "id": "cand-5135",
        "type": "archive",
        "expected": "Zeri (1957), cited publication; title unspecified",
        "name": "Federico Zeri, Pittura e Controriforma (Torino, 1957)",
        "detail": "Printed p.441 supplies the title and publication details for the existing p.146 citation. The book and cited pages were not independently read.",
    },
    {
        "id": "cand-9912",
        "type": "archive",
        "expected": "Zimmermann, pages 197–224 (citation locator)",
        "name": "H. Zimmermann, ‘Über einige Bilder der Sammlung Streit im Grauen Kloster zu Berlin’ (Zeitschrift für Kunstwissenschaft, 1954, pp. 197–224)",
        "detail": "Printed p.441 supplies the article title and periodical for the existing pp.197–224 locator. Page image review removes a stray leading OCR quotation mark before the journal title; the article and cited pages were not independently read.",
    },
    {
        "id": "cand-9364",
        "type": "archive",
        "expected": "Zucchini, 1933, pp.23-30 (citation locator; work unresolved)",
        "name": "G. Zucchini, ‘Quadri inediti di Donato Creti’ (Comune di Bologna, 1933, pp. 23–30)",
        "detail": "Printed p.441 identifies the article matching the p.287 note 6 page range. The article and cited pages were not independently read.",
    },
    {
        "id": "cand-11159",
        "type": "person",
        "expected": "Jaffé (scholar cited alongside Wittkower in p.398 note 7; identity unresolved)",
        "name": "Jaffé, Irma (bibliographic editor; identity unresolved)",
        "detail": "The p.398 note gives only Jaffé; printed p.441 gives the form Irma Jaffé and lists her as editor of Baroque Art: The Jesuit Contribution. This records the source form and role only; identity alignment remains for S3.",
    },
    {
        "id": "cand-8359",
        "type": "person",
        "expected": "Zannandreis, author cited in p.255 note 1",
        "name": "Diego Zannandreis (bibliographic author; identity unresolved)",
        "detail": "The p.255 note cites Zannandreis; printed p.441 supplies the bibliographic author form Diego. This records the source form only, without resolving identity.",
    },
    {
        "id": "cand-9911",
        "type": "person",
        "expected": "Zimmermann (author cited at p.316 notes; identity unresolved)",
        "name": "H. Zimmermann (bibliographic author; identity unresolved)",
        "detail": "Printed p.441 gives the bibliographic author form H. Zimmermann for the p.316 page locator. This records the source form only, without resolving identity.",
    },
    {
        "id": "cand-9363",
        "type": "person",
        "expected": "Zucchini (surname-only author in p.287 note 6; identity unresolved)",
        "name": "G. Zucchini (bibliographic author; identity unresolved)",
        "detail": "Printed p.441 gives the bibliographic author form G. Zucchini for the p.287 note 6 citation. This records the source form only, without resolving identity.",
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
        "id": "cand-11454",
        "name": "E. Wind, ‘Shaftesbury as a patron of art’ (Journal of the Warburg and Courtauld Institutes, II, 1938–39, pp. 185–188)",
        "detail": "Bibliography entry at printed p.441. A separate Wind article, ‘Julian the Apostate at Hampton Court’, is candidate cand-7230; keep the publications distinct. Neither article nor its cited pages was independently read.",
        "source_line": 1264,
        "related": ["cand-7230"],
    },
    {
        "id": "cand-11455",
        "name": "Edward Wright, Some observations made in travelling through France, Italy &c in the years 1720, 1721 and 1722 (2 vols., London, 1730)",
        "detail": "Bibliography entry at printed p.441. Earlier page-specific Wright citation candidates cand-8582 and cand-9888 remain separate for S3 comparison. The book and cited pages were not independently read.",
        "source_line": 1280,
        "related": ["cand-8582", "cand-9888"],
    },
    {
        "id": "cand-11456",
        "name": "Girolamo Zanetti, ‘Memorie per servire all’istoria dell’inclita città di Venezia’ (Archivio Veneto, 1885, pp. 93–148)",
        "detail": "Bibliography entry at printed p.441; the author is bracketed as [Zanetti, Girolamo] in print. Possible matches to separately described 1743 reports and citations remain for S3; the article and cited pages were not independently read.",
        "source_line": 1288,
        "related": ["cand-8781", "cand-8816", "cand-10415", "cand-9280", "cand-2862"],
    },
    {
        "id": "cand-11457",
        "name": "Diego Zannandreis, Le vite de’ Pittori, Scultori e Architetti Veronesi (edited by Giuseppe Biadego, Verona, 1891)",
        "detail": "Bibliography entry at printed p.441. Page-specific candidates cand-8360 and cand-9819 remain separate for S3 comparison. The book and cited pages were not independently read.",
        "source_line": 1290,
        "related": ["cand-8359", "cand-8360", "cand-9819"],
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


def record(candidate_id, start, end, author, title, details, kind, *,
           predicate="bibliography_lists_publication", corrections=None,
           notes=None, related=None, continuation_of=None):
    return {
        "candidate_id": candidate_id,
        "start": start,
        "end": end,
        "author": author,
        "title": title,
        "details": details,
        "kind": kind,
        "predicate": predicate,
        "corrections": corrections or [],
        "page_image_notes": notes or [],
        "related": related or [],
        "continuation_of": continuation_of,
    }


entries = [
    record("cand-7185", 1262, 1263, "Wilhelm, F.", "‘Neue Quellen zur Geschichte des fürstlich Liechtensteinschen Kunstbesitzes’", "Jahrbuch des Kunsthistorischen Institutes der K.K. Zentralkommission, 1911, Beiblatt, pp. 87–142", "journal article continuation", predicate="bibliography_continues_publication", notes=["Completes the title begun at printed p.440 L1259; the periodical citation appears only on this page."], related=["cand-7184"], continuation_of=PREVIOUS_SEGMENT),
    record("cand-11454", 1264, 1265, "Wind, E.", "‘Shaftesbury as a patron of art’", "Journal of the Warburg and Courtauld Institutes, II, 1938–39, pp. 185–188", "journal article", related=["cand-7230"]),
    record("cand-7230", 1266, 1267, "Wind, E.", "‘Julian the Apostate at Hampton Court’", "Journal of the Warburg and Courtauld Institutes, III, 1939–40, pp. 127–137", "journal article"),
    record("cand-7111", 1268, 1269, "Wittkower, R.", "‘Domenico Guidi and French classicism’", "Journal of the Warburg and Courtauld Institutes, II, 1938–39, pp. 188–190", "journal article"),
    record("cand-9311", 1270, 1271, "Wittkower, R.", "The Earl of Burlington and William Kent", "Published by the York Georgian Society, 1948", "book"),
    record("cand-4383", 1272, 1272, "Wittkower, R.", "The sculptures of Gian Lorenzo Bernini", "London 1955", "book"),
    record("cand-4557", 1273, 1273, "Wittkower, R.", "Art and architecture in Italy 1600 to 1750", "London 1958", "book", corrections=[{"line": 1273, "ocr": "London 195 8", "print": "London 1958", "note": "The page image shows 1958 without an internal space."}]),
    record("cand-11170", 1274, 1275, "Wittkower, R.", "Gian Lorenzo Bernini—the Sculptor of the Roman Baroque", "Second edition, London 1966", "book"),
    record("cand-11368", 1276, 1277, "Wittkower, R. and Jaffé, Irma (edited by)", "Baroque Art: The Jesuit Contribution", "New York 1972", "edited volume", corrections=[{"line": 1276, "ocr": "Jaffe, Irma", "print": "Jaffé, Irma", "note": "The page image shows an acute accent on the final e."}], related=["cand-10910", "cand-11159"], notes=["The book is a possible bibliographic context for the p.398 note 7 source candidate cand-10910; the exact contribution/locator mapping remains for S3."]),
    record("cand-9010", 1278, 1279, "Woodward, J.", "‘Amigoni as portrait painter in England’", "Burlington Magazine, 1957, pp. 21–23", "journal article"),
    record("cand-11455", 1280, 1281, "Wright, Edward", "Some observations made in travelling through France, Italy &c in the years 1720, 1721 and 1722", "2 vols., London 1730", "book set", related=["cand-8582", "cand-9888"]),
    record("cand-10534", 1282, 1282, "Wynne-Rosenberg, Giustiniana", "Alticchiero", "à Padoue 1787 (as printed)", "book", notes=["The print reads à Padoue; the existing candidate form says Venezia 1787. Preserve both forms for S3/source comparison."]),
    record("cand-9548", 1283, 1283, "Zabeo, Prof. Prosdocimo", "Memorie intorno l’antiquario Alvise Meneghetti", "Venezia 1816", "book", related=["cand-9549"]),
    record("cand-10117", 1284, 1284, "Zanetti, A. M.", "Varie pitture a fresco de’ principali maestri veneziani", "Venezia 1760", "book", related=["cand-2854", "cand-2859"]),
    record("cand-9837", 1285, 1285, "Zanetti, AM.", "Della Pittura Veneziana", "Venezia 1771", "book", related=["cand-2854", "cand-2855"]),
    record("cand-9281", 1286, 1287, "Zanetti, Girolamo", "Elogio di Rosalba Carriera letto in una privata sessione dell’Accademia di Belle Lettere ed Arti in Padova il di 6 Dicembre 1781", "Venezia 1818; the title states a Padova reading date of 6 December 1781", "book", related=["cand-9280", "cand-2862"], notes=["Keep the reading date in the title separate from the 1818 publication date."]),
    record("cand-11456", 1288, 1289, "[Zanetti, Girolamo]", "‘Memorie per servire all’istoria dell’inclita città di Venezia’", "Archivio Veneto, 1885, pp. 93–148", "journal article", related=["cand-8781", "cand-8816", "cand-10415", "cand-9280", "cand-2862"], notes=["The author's name is bracketed in print; do not remove the qualification or equate the separate 1743 reports at S2."]),
    record("cand-11457", 1290, 1291, "Zannandreis, Diego", "Le vite de’ Pittori, Scultori e Architetti Veronesi", "Edited by Giuseppe Biadego, Verona 1891", "book", related=["cand-8359", "cand-8360", "cand-9819"], notes=["The printed entry states edizione a cura di Giuseppe Biadego; retain Giuseppe Biadego as editor, not author."]),
    record("cand-7115", 1292, 1292, "Zanotti, G. P.", "Storia dell’Accademia Clementina", "2 vols., Bologna 1739", "book set", related=["cand-7114"]),
    record("cand-8794", 1293, 1294, "Zarzabini, Padre Maestro Valerio Antonio", "Serie storica de’ Religiosi Carmelitani", "Venezia 1779", "book"),
    record("cand-5166", 1295, 1295, "Zeri, F.", "La Galleria Spada in Roma", "Firenze 1953", "book", related=["cand-4878"]),
    record("cand-5135", 1296, 1296, "Zeri, Federico", "Pittura e Controriforma", "Torino 1957", "book", related=["cand-4878"]),
    record("cand-9912", 1297, 1298, "Zimmermann, H.", "‘Über einige Bilder der Sammlung Streit im Grauen Kloster zu Berlin’", "Zeitschrift für Kunstwissenschaft, 1954, pp. 197–224", "journal article", corrections=[{"line": 1298, "ocr": "'Zeitschrift", "print": "Zeitschrift", "note": "The page image has no leading quotation mark before the italicized journal title."}], related=["cand-9911"]),
    record("cand-9364", 1299, 1299, "Zucchini, G.", "‘Quadri inediti di Donato Creti’", "Comune di Bologna, 1933, pp. 23–30", "journal article", related=["cand-9363"]),
]

if len(candidate_updates) != 24 or len(new_candidates) != 4 or len(entries) != 24:
    raise SystemExit("unexpected candidate or publication/continuation counts")

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

for index, item in enumerate(entries, start=1):
    candidate_id = item["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {candidate_id}")
    for related_id in item["related"]:
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    for line in range(item["start"], item["end"] + 1):
        if line in line_owners:
            raise SystemExit(f"overlapping publication line range at L{line}: {candidate_id}")
        line_owners[line] = candidate_id
        covered_lines.add(line)

    quote = "\n".join(source_lines[item["start"] - 1 : item["end"]])
    positions = [i for i in range(len(segment_text)) if segment_text.startswith(quote, i)]
    if len(positions) != 1:
        raise SystemExit(f"source quote must occur once: {candidate_id} L{item['start']}")
    start_char = positions[0]
    end_char = start_char + len(quote)
    mention_id = f"m-chp21-bib-l1261-1299-{index:03d}"
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
        note="S0 bibliography entry or continuation; page-image readings, cross-page context, and S3 comparisons are recorded on its statement.",
    )
    new_mentions.append(mention_row)
    mention_ids.add(mention_id)
    mention_keys.add(mention_key)
    new_spans.append((start_char, end_char))

    statement_id = f"st-chp21-bib-l1261-1299-entry-{index:02d}"
    if statement_id in statement_ids:
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if item["continuation_of"]:
        claim = "Printed p.441 continues the F. Wilhelm article entry begun on printed p.440 with its journal citation and page range."
    else:
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
        "text_layer": "bibliographic continuation" if item["continuation_of"] else "bibliographic entry",
        "qualification": "This records only the printed bibliography entry/continuation; the cited publication and pages were not independently consulted.",
        "bibliographic_record": {
            "author_as_printed": item["author"],
            "title_as_printed": item["title"],
            "publication_details_as_printed": item["details"],
            "record_kind": item["kind"],
            "printed_page": 441,
            "pdf_physical_page": 31,
        },
    }
    if item["corrections"]:
        qualifiers["page_image_ocr_corrections"] = item["corrections"]
    if item["page_image_notes"]:
        qualifiers["page_image_notes"] = item["page_image_notes"]
    if item["related"]:
        qualifiers["related_candidate_ids_for_s3"] = item["related"]
    if item["continuation_of"]:
        qualifiers["continuation_of_segment_id"] = item["continuation_of"]
    new_statements.append(
        {
            "statement_id": statement_id,
            "segment_id": SEGMENT,
            "subject_candidate_id": None,
            "object_candidate_id": candidate_id,
            "predicate": item["predicate"],
            "qualifiers": qualifiers,
            "original_quote": quote,
            "origin": "book",
            "source_file": SOURCE_FILE,
        }
    )

if covered_lines != set(range(1262, 1300)):
    raise SystemExit(f"bibliography lines not covered exactly: {sorted(set(range(1262, 1300)) - covered_lines)}")
if len(new_mentions) != 24 or len(new_statements) != 24:
    raise SystemExit("unexpected mention/statement counts")
if any(new_spans[i][1] > new_spans[i + 1][0] for i in range(len(new_spans) - 1)):
    raise SystemExit("mention character spans overlap")

for statement in new_statements:
    for field in ("subject_candidate_id", "object_candidate_id"):
        related_id = statement.get(field)
        if related_id is not None and related_id not in candidate_by_id:
            raise SystemExit(f"statement FK missing: {statement['statement_id']} {field}={related_id}")
    for field in ("mentioned_candidate_ids", "related_candidate_ids_for_s3"):
        for related_id in statement["qualifiers"].get(field, []):
            if related_id not in candidate_by_id:
                raise SystemExit(f"{field} FK missing: {statement['statement_id']}: {related_id}")
    if statement["original_quote"] not in segment_text:
        raise SystemExit(f"statement quote outside source segment: {statement['statement_id']}")

coverage_row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1262-1299",
    note="Printed p.441: completed the Wilhelm entry continued from p.440 and reviewed 23 further publication entries with page-image checking; see process/stages.md.",
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
    "candidate_count": 11436,
    "mention_count": 26822,
    "statement_count": 12095,
    "coverage_complete": 616,
    "coverage_queued": 95,
    "coverage_excluded": 121,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "candidate_updates": len(candidate_updates),
    "new_archive_candidates": len(new_candidates),
    "bibliography_publications": 23,
    "cross_page_continuations": 1,
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
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
