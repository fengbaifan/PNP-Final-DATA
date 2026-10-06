#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 424."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l538-575"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "11f1f046fe8fad14a8bc0ae0aeb5bb9baf5eac11bf7754d6bca0524077c97f81"
BACKUP = ".bak-s2-chp21-bibliography-l538-575-20261007"

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
segment_text = "\n".join(source_lines[537:575])
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
    11322,
    26305,
    11580,
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

# Entry boundaries and OCR readings were checked against PDF physical page 14.
entries = [
    {
        "candidate_id": "cand-4854", "start": 539, "end": 540,
        "author": "[Gotti, A.]",
        "title": "Le Gallerie di Firenze—relazione al Ministro della Pubblica Istruzione in Italia",
        "details": "Firenze 1872", "kind": "book with bracketed byline",
    },
    {
        "candidate_id": "cand-4555", "start": 541, "end": 541,
        "author": "Gould, C.",
        "title": "Bernini’s bust of Mr Baker: The solution?",
        "details": "Art Quarterly, 1958, pp. 167-176", "kind": "journal article",
    },
    {
        "candidate_id": "cand-9781", "start": 542, "end": 542,
        "author": "Gozzi, Gasparo", "title": "Lettere familiari",
        "details": "Venezia 1808", "kind": "book",
    },
    {
        "candidate_id": "cand-11344", "start": 543, "end": 543,
        "new_name": "Gasparo Gozzi, Opere—edizione seconda (22 vols., Venezia, 1812)",
        "new_detail": "Twenty-two-volume set-level bibliography record; kept distinct from Gozzi work and volume/page citation candidates cand-9782 and cand-9959 pending S3; contents were not independently consulted.",
        "author": "Gozzi, Gasparo", "title": "Opere—edizione seconda",
        "details": "22 vols., Venezia 1812", "kind": "22-volume publication set",
        "related": ["cand-9782", "cand-9959"],
    },
    {
        "candidate_id": "cand-11345", "start": 544, "end": 545,
        "new_name": "Pietro Gradenigo, Notizie d’arte tratte dai Notatori e dagli Annali (edited by Lina Livan, Venezia, 1942)",
        "new_detail": "Bibliography-level edited publication record; kept distinct from the Gradenigo citation locators cand-8508, cand-10157, and cand-10808 pending S3; contents were not independently consulted.",
        "author": "Gradenigo, Pietro",
        "title": "Notizie d’arte tratte dai Notatori e dagli Annali",
        "details": "a cura di Lina Livan, Venezia 1942", "kind": "edited book",
        "corrections": [{"line": 544, "ocr": "Notatoti", "print": "Notatori"}],
        "related": ["cand-8508", "cand-10157", "cand-10808"],
    },
    {
        "candidate_id": "cand-11346", "start": 546, "end": 547,
        "new_name": "L. Grassi, ‘Pietro da Cortona e i “bozzetti” per la Galleria di Palazzo Doria Pamphili’ (Bollettino d’Arte, 1957, pp. 28-43)",
        "new_detail": "Bibliography-level article record; a detached dash-like scan mark beside the final page range is excluded from the citation; the article was not independently consulted.",
        "author": "Grassi, L.",
        "title": "Pietro da Cortona e i “bozzetti” per la Galleria di Palazzo Doria Pamphili",
        "details": "Bollettino d’Arte, 1957, pp. 28-43", "kind": "journal article",
        "page_image_notes": [
            "A detached dash-like mark appears in the margin aligned with the end of the p.547 line; S0 OCR appends it after the page range, but it is excluded from the bibliographic record."
        ],
    },
    {
        "candidate_id": "cand-9783", "start": 548, "end": 548,
        "author": "Grimaldo, C.", "title": "Giorgio Pisani e il suo tentativo di riforma",
        "details": "Venezia 1907", "kind": "book",
    },
    {
        "candidate_id": "cand-4386", "start": 549, "end": 551,
        "author": "Grisar, J.",
        "title": "Päpstliche Finanzen Nepotismus und Kirchenrecht unter Urban VIII",
        "details": "Miscellanea Historiae Pontificiae edita a Facultate Historiae Ecclesiasticae in Pontificia Universitate Gregoriana, VII, 1943, pp. 207-365",
        "kind": "journal article",
        "corrections": [{"line": 549, "ocr": "J. :", "print": "J.:"}],
    },
    {
        "candidate_id": "cand-7143", "start": 552, "end": 553,
        "author": "Griseri, A.",
        "title": "I bozzetti di Luca Giordano per l’Escaliera dell’Escorial",
        "details": "Paragone, 81, 1956, pp. 33-39", "kind": "journal article",
        "quote_override": (
            "Griseri, A.: ‘I bozzetti di Luca Giordano per l’Escaliera dell’Escorial’ "
            "in Paragone, 81, 1956,\nPP33-39"
        ),
        "corrections": [
            {
                "line": 553,
                "ocr": "PP33-39Griseri, A.:",
                "print": "pp. 33-39. [next entry begins] Griseri, A.:",
            }
        ],
    },
    {
        "candidate_id": "cand-9467", "start": 553, "end": 553,
        "author": "Griseri, A.", "title": "The Palazzo Reale at Turin",
        "details": "Connoisseur, 1957, vol. 140, pp. 145-150",
        "kind": "journal article",
        "quote_override": (
            "Griseri, A.: ‘The Palazzo Reale at Turin’ in Connoisseur, 1957, "
            "vol. 140, pp. 145-150."
        ),
        "page_image_notes": [
            "This exact mention begins immediately after the previous entry’s page range on L553; the two source spans are disjoint."
        ],
    },
    {
        "candidate_id": "cand-11347", "start": 554, "end": 554,
        "new_name": "[Grosley, Pierre Jean], Nouveaux Mémoires ou observations sur l’Italie et sur les italiens (3 vols., Londres, 1764; byline bracketed in the bibliography)",
        "new_detail": "The printed p.424 continuation supplies 3 vols. and Londres 1764; its OCR text is displaced to L1305. When the queued L1301-1306 segment is reviewed, link that exact source span to this candidate without adding a second bibliography statement. The work was not independently consulted.",
        "author": "[Grosley, Pierre Jean]",
        "title": "Nouveaux Mémoires ou observations sur l’Italie et sur les italiens",
        "details": "3 vols., Londres 1764",
        "kind": "three-volume book with bracketed byline",
        "page_image_notes": [
            "The print continues this record with '3 vols., Londres 1764.'; the OCR continuation is displaced to L1305."
        ],
    },
    {
        "candidate_id": "cand-11348", "start": 555, "end": 556,
        "new_name": "[Gualandi, Michelangelo], Memorie originali risguardanti le Belle Arti (6 vols., Bologna, 1840-5; byline bracketed in the bibliography)",
        "new_detail": "Six-volume bibliography-level set record; kept distinct from volume-I and volume-II citation locators cand-6608 and cand-7501 pending S3; the set was not independently consulted.",
        "author": "[Gualandi, Michelangelo]",
        "title": "Memorie originali risguardanti le Belle Arti",
        "details": "6 vols., Bologna, 1840-5",
        "kind": "six-volume publication set with bracketed byline",
        "related": ["cand-6608", "cand-7501"],
    },
    {
        "candidate_id": "cand-5623", "start": 557, "end": 557,
        "author": "Gualdo Priorato, Galeazzo",
        "title": "Historia della Sacra Real Maestà di Christina Alessandra Regina di Svetia",
        "details": "Venezia 1656", "kind": "book",
    },
    {
        "candidate_id": "cand-7167", "start": 558, "end": 559,
        "author": "Gualdo Priorato, Galeazzo",
        "title": "Vita del Cav. Pietro Liberi pittore padovano",
        "details": "1664, published Vicenza 1818", "kind": "book",
        "page_image_notes": [
            "A detached dash-like mark follows the printed publication details; it is excluded from the bibliographic record."
        ],
    },
    {
        "candidate_id": "cand-11044", "start": 560, "end": 560,
        "author": "Guelfi, Fausta Franchini", "title": "Alessandro Magnasco",
        "details": "Genoa 1977", "kind": "book",
    },
    {
        "candidate_id": "cand-5471", "start": 561, "end": 561,
        "author": "Guibert, J. de", "title": "La spiritualité de la Compagnie de Jésus",
        "details": "Roma 1953", "kind": "book",
        "corrections": [{"line": 561, "ocr": "Jesus", "print": "Jésus"}],
    },
    {
        "candidate_id": "cand-6592", "start": 562, "end": 562,
        "author": "Guidalotti Franchini, Gioseffo",
        "title": "Vita di Domenico Maria Viani",
        "details": "Bologna 1716", "kind": "book",
    },
    {
        "candidate_id": "cand-11349", "start": 563, "end": 563,
        "new_name": "Luisa Hager, Nymphenburg—official guide (München, 1955)",
        "new_detail": "Bibliography-level guidebook record; the guide was not independently consulted.",
        "author": "Hager, Luisa", "title": "Nymphenburg—official guide",
        "details": "München 1955", "kind": "guidebook",
        "corrections": [{"line": 563, "ocr": "officiai", "print": "official"}],
    },
    {
        "candidate_id": "cand-11350", "start": 564, "end": 564,
        "new_name": "R. Halsband, Lady Mary Wortley Montagu (Oxford, 1956)",
        "new_detail": "Bibliography-level biographical book record; the book was not independently consulted.",
        "author": "Halsband, R.", "title": "Lady Mary Wortley Montagu",
        "details": "Oxford 1956", "kind": "book",
    },
    {
        "candidate_id": "cand-4953", "start": 565, "end": 565,
        "author": "Hanotaux, G.",
        "title": "Recueil des Instructions données aux Ambassadeurs et Ministres de France—VI (Rome 1648-1687)",
        "details": "Paris 1888", "kind": "book",
        "corrections": [
            {
                "line": 565,
                "ocr": "Rome i648-i687),.Paris",
                "print": "Rome 1648-1687), Paris",
            }
        ],
    },
    {
        "candidate_id": "cand-6576", "start": 566, "end": 566,
        "author": "Hantsch, P. Hugo und Scherf, Andreas",
        "title": "Quellen zur Geschichte des Barocks in Franken unter dem Einfluss des Hauses Schönborn",
        "details": "I. Teil, erster Halbband, Augsburg 1931", "kind": "edited volume",
        "related": ["cand-7253"],
    },
    {
        "candidate_id": "cand-10870", "start": 567, "end": 567,
        "author": "Harris, Ann Sutherland", "title": "Andrea Sacchi",
        "details": "Oxford (Phaidon), 1977", "kind": "book",
    },
    {
        "candidate_id": "cand-7127", "start": 568, "end": 569,
        "author": "Harris, Enriqueta",
        "title": "El Marqués del Carpio y sus cuadros de Velázquez",
        "details": "Archivo Español de Arte, 1957, pp. 136-139",
        "kind": "journal article",
        "corrections": [
            {"line": 568, "ocr": "Marques", "print": "Marqués"},
            {"line": 568, "ocr": "Espanol", "print": "Español"},
        ],
    },
    {
        "candidate_id": "cand-11351", "start": 570, "end": 570,
        "new_name": "Enriqueta Harris, ‘Velasquez’s portrait of Camillo Massimi’ (Burlington Magazine, 1958, pp. 279-280)",
        "new_detail": "Bibliography-level article record; the page-image margin marks before the author are not part of the entry. The article was not independently consulted.",
        "author": "Harris, Enriqueta",
        "title": "Velasquez’s portrait of Camillo Massimi",
        "details": "Burlington Magazine, 1958, pp. 279-280",
        "kind": "journal article",
        "corrections": [{"line": 570, "ocr": "••\"\" ", "print": ""}],
    },
    {
        "candidate_id": "cand-11352", "start": 571, "end": 571,
        "new_name": "Enriqueta Harris, ‘La misión de Velázquez in Italia’ (Archivo Español de Arte, 1960, pp. 109-136)",
        "new_detail": "Bibliography-level article record; the article was not independently consulted.",
        "author": "Harris, Enriqueta",
        "title": "La misión de Velázquez in Italia",
        "details": "Archivo Español de Arte, 1960, pp. 109-136",
        "kind": "journal article",
        "corrections": [
            {"line": 571, "ocr": "Velazquez", "print": "Velázquez"},
            {"line": 571, "ocr": "Espanol", "print": "Español"},
            {"line": 571, "ocr": "i960", "print": "1960"},
        ],
    },
    {
        "candidate_id": "cand-11353", "start": 572, "end": 572,
        "new_name": "Enriqueta Harris, ‘A letter from Velasquez to Camillo Massimi’ (Burlington Magazine, 1960, pp. 162-166)",
        "new_detail": "Bibliography-level article record; the title spelling Velasquez is preserved as printed. The article was not independently consulted.",
        "author": "Harris, Enriqueta",
        "title": "A letter from Velasquez to Camillo Massimi",
        "details": "Burlington Magazine, 1960, pp. 162-166",
        "kind": "journal article",
        "corrections": [{"line": 572, "ocr": "i960", "print": "1960"}],
    },
    {
        "candidate_id": "cand-7119", "start": 573, "end": 573,
        "author": "Harris, Enriqueta",
        "title": "Angelo Michele Colonna y la decoración de San Antonio de los Portugueses",
        "details": "Archivo Español de Arte, pp. 101-105",
        "kind": "journal article",
        "page_image_notes": [
            "This p.423 bibliography line supplies the journal and page range but no year; the candidate’s existing 1961 date comes from another S2 source and is not copied into this entry."
        ],
        "corrections": [{"line": 573, "ocr": "Espatiol", "print": "Español"}],
    },
    {
        "candidate_id": "cand-11354", "start": 574, "end": 575,
        "new_name": "Enriqueta Harris, ‘Cassiano dal Pozzo on Diego Velázquez’ (Burlington Magazine, 1970, pp. 364-373)",
        "new_detail": "Bibliography-level article record; the article was not independently consulted.",
        "author": "Harris, Enriqueta",
        "title": "Cassiano dal Pozzo on Diego Velázquez",
        "details": "Burlington Magazine, 1970, pp. 364-373",
        "kind": "journal article",
        "corrections": [{"line": 575, "ocr": "PP364-373-", "print": "pp. 364-373"}],
    },
]

covered_lines = {line for entry in entries for line in range(entry["start"], entry["end"] + 1)}
if covered_lines != set(range(539, 576)):
    raise SystemExit("bibliography entry line coverage is incomplete")
if len(entries) != 28:
    raise SystemExit("unexpected local bibliography record count")

expected_name_updates = {
    "cand-4854": (
        "A. Gotti, cited publication; title unspecified",
        "[Gotti, A.], Le Gallerie di Firenze—relazione al Ministro della Pubblica Istruzione in Italia (Firenze, 1872; byline bracketed in the bibliography)",
        "Printed bibliography p.424 identifies the title and place/year; its square-bracket byline is retained and not converted to a confirmed author identity.",
    ),
    "cand-4555": (
        "Gould (1958), cited publication; title unspecified",
        "C. Gould, ‘Bernini’s bust of Mr Baker: The solution?’ (Art Quarterly, 1958, pp. 167-176)",
        "Printed bibliography p.424 identifies the article title and page range; the article was not independently consulted.",
    ),
    "cand-4386": (
        "J. Grisar, S.J., cited study; title, date, and edition unspecified",
        "J. Grisar, ‘Päpstliche Finanzen Nepotismus und Kirchenrecht unter Urban VIII’ (Miscellanea Historiae Pontificiae, VII, 1943, pp. 207-365)",
        "Printed bibliography p.424 supplies the article title and publication details; the cited text was not independently consulted.",
    ),
    "cand-11044": (
        "Guelfi's monograph on Alessandro Magnasco",
        "Fausta Franchini Guelfi, Alessandro Magnasco (Genoa, 1977)",
        "Printed bibliography p.424 supplies the author form and publication details; the monograph was not independently consulted.",
    ),
    "cand-5471": (
        "J. de Guibert, cited study; title and edition unresolved",
        "J. de Guibert, La spiritualité de la Compagnie de Jésus (Roma, 1953)",
        "Printed bibliography p.424 identifies the title and publication details; the book was not independently consulted.",
    ),
    "cand-6592": (
        "Guidalotti Franchini, Vita di Domenico Maria Viani (1716), p.19",
        "Gioseffo Guidalotti Franchini, Vita di Domenico Maria Viani (Bologna, 1716)",
        "Printed bibliography p.424 confirms the byline, title, place, and year; the cited page was not independently consulted.",
    ),
    "cand-4953": (
        "Hanotaux, cited publication, pp. 8 and 12–13; title and year unspecified",
        "G. Hanotaux, Recueil des Instructions données aux Ambassadeurs et Ministres de France, vol. VI (Rome 1648-1687; Paris, 1888)",
        "Printed bibliography p.424 identifies the volume and publication details; the cited pages were not independently consulted.",
    ),
    "cand-6576": (
        "Hantsch and Scherf, Quellen zur Geschichte des Barocks... (1931)",
        "Hantsch, P. Hugo and Scherf, Andreas, Quellen zur Geschichte des Barocks in Franken unter dem Einfluss des Hauses Schönborn, I. Teil, erster Halbband (Augsburg, 1931)",
        "Printed bibliography p.424 gives the first-part, first-half-volume imprint. Keep distinct from the second-half-volume candidate cand-7253 pending S3; cited pages were not independently consulted.",
    ),
    "cand-10870": (
        "Ann Sutherland Harris’s monograph on Andrea Sacchi (title unspecified)",
        "Ann Sutherland Harris, Andrea Sacchi (Oxford, Phaidon, 1977)",
        "Printed bibliography p.424 identifies the title and publication details; the monograph was not independently consulted.",
    ),
    "cand-7127": (
        "El Marques del Carpio y sus cuadros de Velázquez (Enriqueta Harris, 1957)",
        "Enriqueta Harris, ‘El Marqués del Carpio y sus cuadros de Velázquez’ (Archivo Español de Arte, 1957, pp. 136-139)",
        "Printed bibliography p.424 supplies the title spelling, journal, year, and pages; the article was not independently consulted.",
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

new_candidates = []
new_candidate_specs = [
    ("cand-11344", entries[3]["new_name"], entries[3]["new_detail"], f"{SEGMENT}#L543"),
    ("cand-11345", entries[4]["new_name"], entries[4]["new_detail"], f"{SEGMENT}#L544"),
    ("cand-11346", entries[5]["new_name"], entries[5]["new_detail"], f"{SEGMENT}#L546"),
    ("cand-11347", entries[10]["new_name"], entries[10]["new_detail"], f"{SEGMENT}#L554"),
    ("cand-11348", entries[11]["new_name"], entries[11]["new_detail"], f"{SEGMENT}#L555"),
    ("cand-11349", entries[17]["new_name"], entries[17]["new_detail"], f"{SEGMENT}#L563"),
    ("cand-11350", entries[18]["new_name"], entries[18]["new_detail"], f"{SEGMENT}#L564"),
    ("cand-11351", entries[23]["new_name"], entries[23]["new_detail"], f"{SEGMENT}#L570"),
    ("cand-11352", entries[24]["new_name"], entries[24]["new_detail"], f"{SEGMENT}#L571"),
    ("cand-11353", entries[25]["new_name"], entries[25]["new_detail"], f"{SEGMENT}#L572"),
    ("cand-11354", entries[27]["new_name"], entries[27]["new_detail"], f"{SEGMENT}#L574"),
]
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
        mention_id=f"m-chp21-bib-l538-575-{len(new_mentions) + 1:03d}",
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=position,
        end_char=end,
        note=note,
    )
    new_mentions.append(row)
    mention_keys.add(key)


def add_statement(statement_id, object_id, quote, line_start, line_end, claim, qualifiers):
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
        "predicate": "bibliography_lists_publication",
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "claim": claim,
            "speaker": "Haskell’s bibliography",
            "relation_candidate": False,
            "mentioned_candidate_ids": [object_id],
            "text_layer": "bibliographic entry",
            "qualification": (
                "This records the book bibliography entry only; the cited publication or event record "
                "was not independently consulted in this S2 pass."
            ),
            "bibliographic_record": {
                "author_as_printed": entry_author,
                "title_as_printed": entry_title,
                "publication_details_as_printed": entry_details,
                "record_kind": entry_kind,
                "printed_page": 424,
            },
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
        "S0 bibliography entry; page-image OCR corrections and scan notes are recorded on its statement.",
    )
    entry_author = entry["author"]
    entry_title = entry["title"]
    entry_details = entry["details"]
    entry_kind = entry["kind"]
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
        f"st-chp21-bib-l538-575-entry-{index:02d}",
        candidate_id,
        quote,
        entry["start"],
        entry["end"],
        f'Haskell lists {entry_title} in the bibliography.',
        qualifiers,
    )

if len(new_candidates) != 11 or len(new_mentions) != 28 or len(new_statements) != 28:
    raise SystemExit("unexpected migration row counts")
if [row["candidate_id"] for row in new_candidates] != [
    f"cand-{number}" for number in range(11344, 11355)
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
coverage_by_id[SEGMENT]["source_line_ranges"] = "L538-575"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.424 contains 28 bibliography entries; the [Page 424] marker is not a record. "
    "Reused 17 archive candidates and added 11. The two Griseri entries fused in S0 L553 are "
    "recorded with disjoint mention spans. Grosley’s printed 3-volume/Londres 1764 continuation "
    "is displaced to L1305 and will be linked to its existing candidate when that queued segment "
    "is reviewed. Page-image OCR corrections and detached scan marks are documented in statements; "
    "S0 remains unchanged. Cited works were not independently consulted."
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "printed_page": 424,
    "local_bibliography_entries": len(entries),
    "reused_archive_candidates": len(entries) - len(new_candidates),
    "new_archive_candidates": [row["candidate_id"] for row in new_candidates],
    "candidate_labels_refined": len(expected_name_updates),
    "deferred_candidate_comparisons": sorted({
        candidate_id
        for entry in entries
        for candidate_id in entry.get("related", [])
    }),
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "fused_entry_source_line": 553,
    "displaced_grosley_continuation": "chp-21:21_CHP-21Bibliography:l1301-1306#L1305",
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
