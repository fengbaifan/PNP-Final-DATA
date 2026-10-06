#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 435."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l1022-1057"
SEGMENT_SHA = "85dd9b22afaa7b6c4bb571221f8a53c1f3a7b79b238790d5df3df1e0225cfcc5"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l985-1020"
XREF_TARGET_SEGMENT = "chp-21:21_CHP-21Bibliography:l577-614"
BACKUP_SUFFIX = ".bak-s2-chp21-bibliography-l1022-1057-20261007"

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
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
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
segment_text = "\n".join(source_lines[1021:1057])
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
) != (SOURCE_FILE, 1022, 1057, SEGMENT_SHA, SOURCE_SHA):
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
    11405,
    26635,
    11908,
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
xref_target_coverage = coverage_by_id.get(XREF_TARGET_SEGMENT)
if not xref_target_coverage or (
    xref_target_coverage["disposition"],
    xref_target_coverage["migration_status"],
) != ("reviewed", "complete"):
    raise SystemExit("cross-reference target segment is not reviewed")


candidate_updates = [
    {
        "id": "cand-11171",
        "type": "archive",
        "expected": "Radcliffe, 1978 publication cited at p.401 note 4 (title unspecified)",
        "name": "Anthony Radcliffe, ‘Two Bronzes from the Circle of Bernini’ (Apollo, 1978, pp. 418–423)",
        "detail": "Bibliography p.435 identifies the title and pp.418–423 for the 1978 citation at p.401. The article was not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-10478",
        "type": "archive",
        "expected": "Radicchio, 1786, history of Prà della Valle (p.365 note 2 citation locator)",
        "name": "Radicchio, Don Vincenzo, Descrizione della general idea concepita, ed in gran parte effettuata dall’eccellentissimo signore Andrea Memmo quando fu ... nel MDCCLXXV, e VI proveditor straordinario della città di Padova sul materiale del Prato, che denominavasi della Valle onde renderlo utile anche per la potentissima via del diletto a quel popolo ed a maggior decoro della stessa città (Roma, 1786)",
        "detail": "Bibliography p.435 supplies the printed title and author form for the p.365 note 2 locator. The printed ellipsis after ‘quando fu’ is retained; the omitted wording is not inferred. The book was not independently consulted, and any cross-chapter person alignment remains for S3.",
    },
    {
        "id": "cand-9329",
        "type": "archive",
        "expected": "Rapparini manuscripts published in Düsseldorf in 1958 (source set identified in p.282 note 1)",
        "name": "Rapparini, Die Rapparini-Handschrift (ed. Hermine Kühn-Steinhausen, Düsseldorf, 1958)",
        "detail": "Bibliography p.435 identifies the title, editor, place, and year for the manuscript edition mentioned at p.282 note 1. The edition and cited text were not independently consulted; the relation to the separately indexed Rapparini work remains distinct.",
    },
    {
        "id": "cand-10054",
        "type": "archive",
        "expected": "A. Rava, 1911 (bibliographic citation fragment in printed note 3)",
        "name": "A. Rava, ‘Contributo alla biografia di Pietro Longhi’ (Rassegna Contemporanea, IV, 1911, pp. 297–307)",
        "detail": "Bibliography p.435 identifies the title, journal, volume, year, and pages behind the earlier p.340 note 3 citation fragment. The article was not independently consulted.",
    },
    {
        "id": "cand-10305",
        "type": "archive",
        "expected": "Rava, 1913, pp.58–61 (citation locator in p.354 note 4)",
        "name": "A. Rava, ‘Incisioni su stagno di Francesco Algarotti’ (L’Arte, 1913, pp. 58–61)",
        "detail": "Bibliography p.435 identifies the title and journal behind the p.354 note 4 locator; the printed pages match pp.58–61. The article was not independently consulted.",
    },
    {
        "id": "cand-4993",
        "type": "archive",
        "expected": "Redig de Campos (1936), cited source; title unspecified",
        "name": "D. Redig de Campos, ‘Intorno a due quadri d’altare di Van Dyck per il Gesù di Roma ritrovati in Vaticano’ (Bollettino d’Arte, XXX, 1936, pp. 150–165)",
        "detail": "Bibliography p.435 identifies the title and full journal locator for the earlier 1936 citation. The article was not independently consulted.",
    },
    {
        "id": "cand-10189",
        "type": "archive",
        "expected": "Mostra dei Remondini (1958)",
        "name": "Remondini exhibition catalogue (G. Barioli, ed., Bassano, 1958)",
        "detail": "Bibliography p.435 identifies this as a Remondini exhibition catalogue edited by G. Barioli and published at Bassano in 1958. The catalogue was not independently consulted.",
    },
    {
        "id": "cand-7755",
        "type": "archive",
        "expected": "Amico Ricci source cited as volume II, page 436 (title unresolved)",
        "name": "Amico Ricci, Memorie storiche delle arti e degli artisti della Marca d’Ancona (2 vols., Macerata, 1834)",
        "detail": "Bibliography p.435 identifies the full title, two-volume extent, place, and year for the earlier volume II, p.436 citation. The cited volume and page were not independently consulted.",
    },
    {
        "id": "cand-7602",
        "type": "archive",
        "expected": "Giuseppe Richa, Notizie istoriche delle chiese Fiorentine (volume III cited)",
        "name": "Giuseppe Richa, Notizie istoriche delle chiese Fiorentine divise ne’ suoi quartieri (10 vols., Firenze, 1754–62)",
        "detail": "Bibliography p.435 confirms the printed title form ‘istoriche’, ten-volume extent, and Firenze 1754–62 for the previously cited volume III. The cited volume was not independently consulted.",
    },
    {
        "id": "cand-4807",
        "type": "archive",
        "expected": "Richard, volume VI, pages 57–62 (cited reference)",
        "name": "Abbé Richard, Description historique et critique de l’Italie (6 vols., Dijon, 1766)",
        "detail": "Bibliography p.435 identifies the work, six-volume extent, place, and year behind the earlier volume VI, pp.57–62 citation. The cited pages were not independently consulted.",
    },
    {
        "id": "cand-5024",
        "type": "archive",
        "expected": "Untitled book by Louis Richeôme (1611)",
        "name": "Louis Richeôme, La peinture spirituelle (Lyon, 1611)",
        "detail": "Bibliography p.435 supplies the printed title, place, and year for the earlier citation to Richeôme’s book. The book was not independently consulted.",
    },
    {
        "id": "cand-4367",
        "type": "archive",
        "expected": "de Rinaldis article in Bollettino d’Arte (1936, pp. 577–580); title unspecified",
        "name": "A. de Rinaldis, ‘D’Arpino e Caravaggio’ (Bollettino d’Arte, XXIX, 1936, pp. 577–580)",
        "detail": "Bibliography p.435 identifies the title and volume for the earlier 1936 Bollettino d’Arte citation; the printed pp.577–580 match. The article was not independently consulted.",
    },
    {
        "id": "cand-4368",
        "type": "archive",
        "expected": "de Rinaldis article in Archivi (1936, pp. 110–118); title unspecified",
        "name": "A. de Rinaldis, ‘Le opere d’arte sequestrate al Cavalier d’Arpino’ (Archivi, 1936, pp. 110–118)",
        "detail": "Bibliography p.435 identifies the title and journal for the earlier 1936 Archivi citation; the printed pp.110–118 match. The article was not independently consulted.",
    },
    {
        "id": "cand-6605",
        "type": "archive",
        "expected": "Lettere inedite di Salvator Rosa a G. B. Ricciardi (Roma, 1939)",
        "name": "A. de Rinaldis, Lettere inedite di Salvator Rosa a G. B. Ricciardi (Roma, 1939)",
        "detail": "Bibliography p.435 confirms the printed author form and publication place/year. Earlier chapter locators to this work remain separate for S3 comparison; the book and cited pages were not independently consulted.",
    },
    {
        "id": "cand-5792",
        "type": "archive",
        "expected": "Rinehart 1961 publication cited at page 52 for Cassiano's letter to Galli",
        "name": "S. Rinehart, ‘Cassiano dal Pozzo (1588–1657), Some unpublished letters’ (Italian Studies, 1961, pp. 35–59)",
        "detail": "Bibliography p.435 identifies the title, journal, year, and pages behind the earlier page 52 locator; page 52 falls within the printed pp.35–59. The article and cited page were not independently consulted.",
    },
    {
        "id": "cand-5793",
        "type": "person",
        "expected": "Rinehart, author cited for the 1961 publication",
        "name": "Rinehart, S. (author cited for the 1961 publication)",
        "detail": "The bibliography prints the author form S. Rinehart for both the 1961 article and a See also pointer to Haskell and Rinehart. No full given name or independent person identity is established; retain for S3.",
    },
    {
        "id": "cand-7352",
        "type": "archive",
        "expected": "H. Ritschl, catalogue of the Harrach picture gallery in Vienna",
        "name": "H. Ritschl, Katalog der Erlaucht Gräflich Harrachschen Gemälde-Galerie in Wien (Wien, 1926)",
        "detail": "Bibliography p.435 identifies the German title, place, and year for the earlier passim citation. The catalogue and cited passages were not independently consulted.",
    },
    {
        "id": "cand-9372",
        "type": "archive",
        "expected": "[Rivani], 1959 (bracketed citation locator; work unresolved)",
        "name": "[Rivani, G.], ‘Opere di Donato Creti nella Raccolta della Cassa di Risparmio di Bologna’ (Strenna Storica Bolognese, 1959)",
        "detail": "Bibliography p.435 identifies the printed article title and periodical while retaining the author’s square brackets. The source of that editorial uncertainty and the author identity remain unresolved; the article was not independently consulted.",
    },
    {
        "id": "cand-10141",
        "type": "archive",
        "expected": "Roberti, 1900, pp.326-35 (p.333 note 1 citation locator)",
        "name": "T. Roberti, ‘Lettere inedite di Gasparo Gozzi al tipografo Giambattista Remondini’ (Antologia Veneta, 1900, pp. 326–335)",
        "detail": "Bibliography p.435 identifies the article title and journal; its printed pp.326–335 correspond to the earlier p.333 note 1 locator. The article was not independently consulted; the author identity remains for S3.",
    },
    {
        "id": "cand-9930",
        "type": "person",
        "expected": "J. G. Robertson (author cited at p.318 notes 3–4; identity unresolved)",
        "detail": "Bibliography p.435 prints J. G. Robertson as author of The genesis of romantic theory (Cambridge, 1923). This title is an S3 comparison for the separate p.318 citation locators, not an established match; full personal identity remains unresolved.",
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
        "id": "cand-11427",
        "name": "L. van Puyvelde, ‘Les “Saint Ignace” et “Saint François Xavier” de Rubens’ (Gazette des Beaux-Arts, 1959, I, pp. 225–236)",
        "detail": "Bibliography entry at printed p.435. The article was not independently consulted; retain its printed author form for S3 comparison with the existing Puyvelde person candidate.",
        "source_line": 1023,
    },
    {
        "id": "cand-11428",
        "name": "S. Rinehart, ‘Poussin et la famille dal Pozzo’ (Actes du Colloque Poussin, 1960, I, pp. 19–30)",
        "detail": "Bibliography entry at printed p.435. Keep distinct from the separately listed 1961 Italian Studies article and the Haskell and Rinehart 1960 article; none was independently consulted in this S2 pass.",
        "source_line": 1046,
    },
    {
        "id": "cand-11429",
        "name": "J. G. Robertson, The genesis of romantic theory (Cambridge, 1923)",
        "detail": "Bibliography entry at printed p.435. Keep separate from prior J. G. Robertson citation locators pending S3; the book and cited passages were not independently consulted.",
        "source_line": 1056,
    },
]

natural_keys = {}
for row in candidates:
    key = (row["canonical_name"].strip().casefold(), row["suggested_type"].casefold())
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
    record("cand-11427", 1023, 1024, "Puyvelde, L. van", "‘Les “Saint Ignace” et “Saint François Xavier” de Rubens’", "Gazette des Beaux-Arts, 1959, I, pp. 225–236", "journal article", corrections=[{"line": 1024, "ocr": "23ó. -", "print": "236.", "note": "The page image reads 236 and ends the entry after the period; the OCR trailing dash is not part of the entry."}], related=["cand-4976"]),
    record("cand-11171", 1025, 1025, "Radcliffe, Anthony", "‘Two Bronzes from the Circle of Bernini’", "Apollo, 1978, pp. 418–423", "journal article", corrections=[{"line": 1025, "ocr": "41842Z", "print": "418–423", "note": "The page image confirms the page range 418–423."}], related=["cand-10968"]),
    record("cand-10478", 1026, 1026, "Radicchio, Don Vincenzo", "Descrizione della general idea concepita, ed in gran parte effettuata dall’eccellentissimo signore Andrea Memmo quando fu ... nel MDCCLXXV, e VI proveditor straordinario della città di Padova sul materiale del Prato, che denominavasi della Valle onde renderlo utile anche per la potentissima via del diletto a quel popolo ed a maggior decoro della stessa città", "Roma 1786", "book", notes=["The page image prints an ellipsis after ‘quando fu’; the omitted wording is not inferred. A small raised mark after ‘straordinario’ is unclear and is not transcribed as title text."], related=["cand-2089"]),
    record("cand-9329", 1027, 1028, "Rapparini", "Die Rapparini-Handschrift", "herausgegeben und kommentiert von Hermine Kühn-Steinhausen, Düsseldorf 1958", "edited manuscript publication", related=["cand-2108"]),
    record("cand-10054", 1029, 1029, "Rava, A.", "‘Contributo alla biografia di Pietro Longhi’", "Rassegna Contemporanea, IV, 1911, pp. 297–307", "journal article"),
    record("cand-10305", 1030, 1030, "Rava, A.", "‘Incisioni su stagno di Francesco Algarotti’", "L’Arte, 1913, pp. 58–61", "journal article"),
    record("cand-6579", 1031, 1031, "Rava, A.", "‘Il teatro Ottoboni nel Palazzo della Cancelleria’", "Quaderni del Centro Nazionale di Studi di Storia dell’Architettura, III, 1942", "journal article"),
    record("cand-4993", 1032, 1032, "Redig de Campos, D.", "‘Intorno a due quadri d’altare di Van Dyck per il Gesù di Roma ritrovati in Vaticano’", "Bollettino d’Arte, XXX, 1936, pp. 150–165", "journal article"),
    record("cand-10189", 1033, 1033, "Remondini", "catalogo della mostra", "a cura di G. Barioli, Bassano 1958", "exhibition catalogue"),
    record("cand-8267", 1034, 1034, "Renaldis, Conte Girolamo de", "Memorie storiche dei tre ultimi secoli del patriarcato d’Aquileia (1411–1751)", "Udine 1888", "book", related=["cand-8266"]),
    record("cand-7069", 1035, 1036, "Reni, Guido", "catalogo critico della mostra", "a cura di G. C. Cavalli; saggio introduttivo di C. Gnudi; Bologna 1954", "exhibition catalogue"),
    record("cand-7755", 1037, 1038, "Ricci, Amico", "Memorie storiche delle arti e degli artisti della Marca d’Ancona", "2 vols., Macerata 1834", "book", corrections=[{"line": 1037, "ocr": "2 vols..", "print": "2 vols.,", "note": "The page image shows a comma after vols.; the entry continues with the place on the next line."}], related=["cand-7756"]),
    record("cand-7602", 1039, 1040, "Richa, Giuseppe", "Notizie istoriche delle chiese Fiorentine divise ne’ suoi quartieri", "10 vols., Firenze 1754–62", "book", corrections=[{"line": 1039, "ocr": "¡storiche; io vols.", "print": "istoriche; 10 vols.", "note": "The page image reads the historical spelling ‘istoriche’ and the numeral 10."}], related=["cand-7601"]),
    record("cand-4807", 1041, 1041, "Richard, l’Abbé", "Description historique et critique de l’Italie", "6 vols., Dijon 1766", "book", related=["cand-2188"]),
    record("cand-5024", 1042, 1042, "Richeôme, Louis", "La peinture spirituelle", "Lyon 1611", "book", related=["cand-2192"]),
    record("cand-4367", 1043, 1043, "Rinaldis, A. de", "‘D’Arpino e Caravaggio’", "Bollettino d’Arte, XXIX, 1936, pp. 577–580", "journal article", corrections=[{"line": 1043, "ocr": "193 6; 5 77-5 80", "print": "1936; 577–580", "note": "The page image confirms the year and page range without inserted spaces."}], related=["cand-6369"]),
    record("cand-4368", 1044, 1044, "Rinaldis, A. de", "‘Le opere d’arte sequestrate al Cavalier d’Arpino’", "Archivi, 1936, pp. 110–118", "journal article", corrections=[{"line": 1044, "ocr": "110118", "print": "110–118", "note": "The page image shows the range 110–118, split at the line ending."}], related=["cand-6369"]),
    record("cand-6605", 1045, 1045, "Rinaldis, A. de", "Lettere inedite di Salvator Rosa a G. B. Ricciardi", "Roma 1939", "book", related=["cand-6369", "cand-6205", "cand-6370"]),
    record("cand-11428", 1046, 1046, "Rinehart, S.", "‘Poussin et la famille dal Pozzo’", "Actes du Colloque Poussin, 1960, I, pp. 19–30", "conference proceedings contribution", corrections=[{"line": 1046, "ocr": "i960,1", "print": "1960, I", "note": "The page image reads 1960, volume I."}], related=["cand-5793"]),
    record("cand-5792", 1047, 1048, "Rinehart, S.", "‘Cassiano dal Pozzo (1588–1657), Some unpublished letters’", "Italian Studies, 1961, pp. 35–59", "journal article", related=["cand-5793"]),
    record("cand-7352", 1050, 1051, "Ritschl, H.", "Katalog der Erlaucht Gräflich Harrachschen Gemälde-Galerie in Wien", "Wien 1926", "catalogue"),
    record("cand-9372", 1052, 1053, "[Rivani, G.]", "‘Opere di Donato Creti nella Raccolta della Cassa di Risparmio di Bologna’", "Strenna Storica Bolognese, 1959", "journal article", related=["cand-9371"]),
    record("cand-10141", 1054, 1055, "Roberti, T.", "‘Lettere inedite di Gasparo Gozzi al tipografo Giambattista Remondini’", "Antologia Veneta, 1900, pp. 326–335", "journal article", corrections=[{"line": 1055, "ocr": "3 26-3 3 5", "print": "326–335", "note": "The page image confirms pp.326–335."}], related=["cand-10131"]),
    record("cand-11429", 1056, 1056, "Robertson, J. G.", "The genesis of romantic theory", "Cambridge 1923", "book", corrections=[{"line": 1056, "ocr": "}. G.", "print": "J. G.", "note": "The page image confirms the author initials J. G."}], related=["cand-9930", "cand-9932", "cand-9933"]),
    record("cand-7895", 1057, 1057, "Robiony, E.", "‘La Madonna dal collo lungo di Parmigianino’", "Rivista d’Arte, 1904, pp. 19–22", "journal article", related=["cand-7896"]),
]

if len(candidate_updates) != 20 or len(new_candidates) != 3 or len(entries) != 25:
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
        raise SystemExit(f"source quote must occur once: {candidate_id}")
    start_char = positions[0]
    end_char = start_char + len(quote)
    mention_id = f"m-chp21-bib-l1022-1057-{index:03d}"
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

    statement_id = f"st-chp21-bib-l1022-1057-entry-{index:02d}"
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
            "printed_page": 435,
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

# L1049 is an author cross-reference to the already reviewed Haskell and Rinehart
# article at L596. It is recorded as a bibliography pointer, not a new authorship edge.
xref_candidate = candidate_by_id.get("cand-5793")
xref_target = candidate_by_id.get("cand-5658")
if not xref_candidate or xref_candidate.get("suggested_type") != "person":
    raise SystemExit("Rinehart author candidate missing or wrong type")
if not xref_target or xref_target.get("suggested_type") != "archive":
    raise SystemExit("Haskell and Rinehart target publication candidate missing or wrong type")
xref_line = source_lines[1048]
xref_surface = "Rinehart, S."
if xref_line.count(xref_surface) != 1:
    raise SystemExit("Rinehart author surface is not unique on L1049")
xref_offset = len("\n".join(source_lines[1021:1048])) + 1 + xref_line.index(xref_surface)
xref_end = xref_offset + len(xref_surface)
xref_mention_id = "m-chp21-bib-l1022-1057-026"
xref_mention_key = (SEGMENT, "cand-5793", str(xref_offset), str(xref_end))
if xref_mention_id in mention_ids or xref_mention_key in mention_keys:
    raise SystemExit("duplicate author cross-reference mention")
xref_mention = {field: "" for field in mention_fields}
xref_mention.update(
    mention_id=xref_mention_id,
    segment_id=SEGMENT,
    candidate_id="cand-5793",
    surface_form=xref_surface,
    start_char=xref_offset,
    end_char=xref_end,
    note="Bibliography author cross-reference; target at L596–597 was reviewed and matched to cand-5658.",
)
new_mentions.append(xref_mention)
xref_id = "st-chp21-bib-l1022-1057-xref-rinehart-haskell"
xref_claim = "Haskell’s bibliography directs the Rinehart, S. author heading to Haskell and Rinehart."
if xref_id in statement_ids or (SEGMENT, " ".join(xref_claim.split()).casefold()) in existing_claim_keys:
    raise SystemExit("duplicate author cross-reference statement")
new_statements.append(
    {
        "statement_id": xref_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-5793",
        "object_candidate_id": "cand-5658",
        "predicate": "bibliography_author_cross_reference",
        "qualifiers": {
            "source_line_start": 1049,
            "source_line_end": 1049,
            "claim": xref_claim,
            "speaker": "Haskell’s bibliography",
            "relation_candidate": False,
            "mentioned_candidate_ids": ["cand-5793"],
            "text_layer": "bibliography cross-reference",
            "qualification": "The See also pointer runs from the printed S. Rinehart author form to the Haskell and Rinehart entry. The target matches the already reviewed L596–597 entry for cand-5658; this pointer does not independently establish additional authorship facts or resolve Rinehart’s identity.",
            "cross_reference_type": "see_also",
            "target_source_line": 596,
            "target_segment_id": XREF_TARGET_SEGMENT,
            "target_source_line_status": "reviewed; matched to cand-5658",
            "related_candidate_ids_for_s3": ["cand-5793", "cand-5658"],
        },
        "original_quote": xref_line,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
)
covered_lines.add(1049)
if covered_lines != set(range(1023, 1058)):
    raise SystemExit(f"bibliography lines not covered exactly: {sorted(set(range(1023, 1058)) - covered_lines)}")

if len(new_mentions) != 26 or len(new_statements) != 26:
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
    quote = statement["original_quote"]
    if quote not in segment_text:
        raise SystemExit(f"statement quote outside source segment: {statement['statement_id']}")

coverage_row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1023-1057",
    note="Printed p.435: 25 publication records and one See also author cross-reference reviewed; see process/stages.md.",
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
    "candidate_count": 11408,
    "mention_count": 26661,
    "statement_count": 11934,
    "coverage_complete": 610,
    "coverage_queued": 101,
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
    "publication_statements": len(entries),
    "cross_reference_statements": 1,
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
