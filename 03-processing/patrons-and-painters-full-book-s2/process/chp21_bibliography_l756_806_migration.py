#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 429."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l756-806"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_MANIFEST_SHA = "de7758f160bc3289ccf52bdbe39053590143a975fae9fe14af57bcee4946ba18"
SEGMENT_TEXT_SHA = "de7758f160bc3289ccf52bdbe39053590143a975fae9fe14af57bcee4946ba18"
BACKUP = ".bak-s2-chp21-bibliography-l756-806-20261007"

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
segment_text = "\n".join(source_lines[755:806])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_TEXT_SHA:
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
    756,
    806,
    SEGMENT_MANIFEST_SHA,
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
    11367,
    26459,
    11733,
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

candidate_updates = [
    {
        "id": "cand-7388",
        "expected": "A. Maresca di Serracapriola, Il museo del duca di Martina (Napoli Nobilissima, 1893)",
        "name": "A. Maresca di Serracapriola, ‘Il museo del duca di Martina’ (Napoli Nobilissima, 1893, pp. 49–52, 74–77, 109–111)",
        "detail": "Printed p.429 supplies the full article locator for this existing citation. The article was not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-10704",
        "expected": "G. Mariacher, 1957, Museo Correr catalogue through the Renaissance",
        "name": "G. Mariacher, Il Museo Correr di Venezia; dipinti dal XIV al XVI secolo (Venezia, 1957)",
        "detail": "Printed p.429 confirms the complete title and publication place for this existing catalogue citation. The catalogue was not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-6587",
        "expected": "Mariette IV p.393; title unspecified",
        "name": "P. J. Mariette, Abecedario et autres notes inédites de cet amateur sur les arts et les artistes (6 vols., Paris, 1853–1862)",
        "detail": "Printed p.429 identifies the six-volume Abecedario set corresponding to the existing volume IV, p.393 locator. The cited passage was not independently consulted; related Mariette locators remain for S3.",
    },
    {
        "id": "cand-9922",
        "expected": "Maugain (minimal citation locator)",
        "name": "G. Maugain, Évolution intellectuelle de l’Italie 1657–1750 (Paris, 1909)",
        "detail": "Printed p.429 supplies the full title and publication details for this existing citation. The book was not independently consulted; the page image confirms the initial accented É.",
    },
    {
        "id": "cand-9289",
        "expected": "Mauroner, 1945 (citation locator; pp.51 and 37 note 17; title unresolved)",
        "name": "F. Mauroner, Luca Carlevarijs (Venezia, 1945)",
        "detail": "Printed p.429 supplies the title and publication place for the existing 1945 locators; cited pages were not independently consulted.",
    },
    {
        "id": "cand-10606",
        "expected": "Mauroner, 1947, pp. 48-50 (quotations from Strange-Sasso letters)",
        "name": "F. Mauroner, ‘Collezionisti e vedutisti settecenteschi a Venezia’ (Arte Veneta, 1947, pp. 48–50)",
        "detail": "Printed p.429 confirms the title, periodical and pages for the existing 1947 locator. The article was not independently consulted.",
    },
    {
        "id": "cand-10452",
        "expected": "Mazzotti (1954), p.133, cited in p.363 note 1",
        "name": "G. Mazzotti, Le Ville Venete—catalogo (3a edizione, Treviso, 1954)",
        "detail": "Printed p.429 confirms the title and third edition for this existing p.133 locator. The page image reads Mazzotti; S0 has Mazzetti.",
    },
    {
        "id": "cand-9972",
        "expected": "Melchiori, page 142 (citation locator for the 1761 Gennari letter)",
        "name": "L. Melchiori, Lettere e letterati a Venezia e Padova a mezzo il secolo XVIII (Padova, 1942)",
        "detail": "Printed p.429 supplies the title and publication details for the existing p.142 locator. The cited page was not independently consulted.",
    },
    {
        "id": "cand-11197",
        "expected": "Meloni Trkulja, 1972 publication cited at p.404 notes 15 and 18 (title unspecified)",
        "name": "Silvia Meloni Trkulja, ‘Luca Giordano a Firenze’ (Paragone, 1972, no. 267, pp. 25–74)",
        "detail": "Printed p.429 supplies the title, issue and pages for the existing 1972 locators. The article was not independently consulted; the periodical heading is restored from the page image.",
    },
    {
        "id": "cand-11189",
        "expected": "Meloni Trkulja, 1975 publication cited at p.404 note 4 (title unspecified)",
        "name": "Silvia Meloni Trkulja, ‘Leopoldo de’ Medici collezionista’ (Paragone, 1975, no. 307, pp. 15–38)",
        "detail": "Printed p.429 supplies the title, issue and pages for the existing 1975 locator. The article was not independently consulted; OCR spacing and punctuation are corrected from the page image.",
    },
    {
        "id": "cand-11199",
        "expected": "Merriman publication cited at p.405 note 1 (title and year unspecified)",
        "name": "Mina Pajes Merriman, ‘Giuseppe Maria Crespi’s “Jupiter among the Corybantes”’ (Burlington Magazine, 1976, pp. 464–472)",
        "detail": "Printed p.429 supplies the title, periodical, year and pages for the existing 1976 citation. The article was not independently consulted; the OCR joins its opening to the prior entry.",
    },
    {
        "id": "cand-4948",
        "expected": "Mezzetti, 1955, cited publication, p. 253; title unspecified",
        "name": "A. Mezzetti, ‘Contributi a Carlo Maratti’ (Rivista dell’Istituto Nazionale d’Archeologia e Storia dell’Arte, 1955, pp. 253–354)",
        "detail": "Printed p.429 supplies the complete article title, periodical and pages for the existing p.253 locator. The article was not independently consulted; the journal title is restored from the page image.",
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
    ("cand-11389", "L. Marcheix, Un Parisien à Rome et à Naples en 1632 (Paris, 1897)", "Bibliography entry at printed p.429. Keep distinct from the title-unresolved Marcheix locator pending S3; the book was not independently consulted.", 757, "archive"),
    ("cand-11390", "G. Mariacher, ‘Il continuatore del Longhena a Palazzo Pesaro ed altre notizie inedite’ (Ateneo Veneto, 1951, pp. 1–6)", "Bibliography entry at printed p.429. The article was not independently consulted; its periodical line is displaced in OCR.", 761, "archive"),
    ("cand-11391", "Abbate Orazio Marrini, Serie di Ritratti di Celebri Pittori dipinti di propria mano (2 vols., Firenze, 1765)", "Bibliography entry at printed p.429. Retain the printed surname Marrini; a similarly named Martini citation remains separate for S3. The work was not independently consulted.", 767, "archive"),
    ("cand-11392", "C. A. Martin, Storia civile e politica del commercio dei Veneziani (8 vols., Venezia, 1798–1808)", "Bibliography entry at printed p.429. The eight-volume work was not independently consulted.", 769, "archive"),
    ("cand-11393", "W. Martin, ‘The life of a Dutch artist’—Part VI: ‘How the painter sold his work’ (Burlington Magazine, XI, 1907, pp. 357–369)", "Bibliography entry at printed p.429. The article was not independently consulted; its periodical heading is split around the entry in OCR.", 771, "archive"),
    ("cand-11394", "Francesco Marucelli, Indice del Mare Magnum (Roma, 1882 edition by Guido Biagi)", "Bibliography entry at printed p.429. Keep distinct from the Mare Magnum and Biagi-introduction citations pending S3; the publication was not independently consulted.", 775, "archive"),
    ("cand-11395", "L. Matina, Ducalis Regiae Lararium (Venezia, 1659)", "Bibliography entry at printed p.429. Keep the publication candidate separate from the index person candidate pending S3; the work was not independently consulted.", 777, "archive"),
    ("cand-11396", "A. Matteoli, ‘Macchie di sole e pittura: carteggio L. Cigoli–G. Galilei 1609–1613’ (Accademia degli Euteleti, 1959)", "Bibliography entry at printed p.429. Keep distinct from the A. Matteoli editor/person candidate pending S3; the article was not independently consulted.", 778, "archive"),
    ("cand-11397", "Barbara Mazza, ‘La vicenda dei “Tombeaux des Princes”: Matrici, storia e fortuna della serie Swiny tra Bologna e Venezia’ (Saggi e Memorie di storia dell’arte, 10, 1976, pp. 79–102)", "Bibliography entry at printed p.429. The article was not independently consulted; page-image review restores the title/journal order and issue number.", 788, "archive"),
    ("cand-11398", "[Andrea Memmo], Riflessioni sopra alcuni equivoci sensi espressi dall’Ornatissimo Autore Della Orazione recitata in Venezia nell’Accademia di Pittura nel 1787 (Padova, 1788)", "Bibliography entry at printed p.429. Preserve the author attribution in brackets as printed; the work was not independently consulted.", 798, "archive"),
    ("cand-11399", "Decio Memmoli, Vita dell’Eminentissimo Signor Cardinale Gio. Garzio Mellino (Roma, 1644)", "Bibliography entry at printed p.429. The page image corrects the OCR spelling of the dedicatee’s surname; the book was not independently consulted.", 800, "archive"),
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
    {"candidate_id": "cand-11389", "start": 757, "end": 757, "author": "Marcheix, L.", "title": "Un Parisien à Rome et à Naples en 1632", "details": "Paris 1897", "kind": "book", "related": ["cand-7000"]},
    {"candidate_id": "cand-7388", "start": 758, "end": 760, "author": "Maresca di Serracapriola, A.", "title": "‘Il museo del duca di Martina’", "details": "Napoli Nobilissima, 1893, pp. 49–52, 74–77 and 109–111", "kind": "journal article", "corrections": [{"line": 758, "ocr": "Napoli Nobilissima,", "print": "in Napoli Nobilissima,", "note": "The periodical heading is displaced above the author/title in OCR and belongs to this article."}]},
    {"candidate_id": "cand-11390", "start": 761, "end": 763, "author": "Mariacher, G.", "title": "‘Il continuatore del Longhena a Palazzo Pesaro ed altre notizie inedite’", "details": "Ateneo Veneto, 1951, pp. 1–6", "kind": "journal article", "corrections": [{"line": 762, "ocr": "Ateneo Veneto,", "print": "in Ateneo Veneto,", "note": "The periodical heading interrupts the article entry in OCR; the page image places it after the title."}]},
    {"candidate_id": "cand-10704", "start": 764, "end": 764, "author": "Mariacher, G.", "title": "Il Museo Correr di Venezia; dipinti dal XIV al XVI secolo", "details": "Venezia 1957", "kind": "book"},
    {"candidate_id": "cand-6587", "start": 765, "end": 766, "author": "Mariette, P. J.", "title": "Abecedario et autres notes inédites de cet amateur sur les arts et les artistes …", "details": "ouvrage publié … par Ph. de Chennevières et A. de Montaiglon, Paris, 6 vols., 1853–1862", "kind": "six-volume publication set", "related": ["cand-1547", "cand-10196", "cand-9334"], "corrections": [{"line": 765, "ocr": "Manette, P. J.: Àbecedario", "print": "Mariette, P. J.: Abecedario", "note": "The page image reads Mariette and Abecedario."}, {"line": 766, "ocr": "pai", "print": "par", "note": "OCR misreads the printed preposition."}, {"line": 766, "ocr": "18531862", "print": "1853–1862", "note": "The printed year range is hyphenated across the line break."}]},
    {"candidate_id": "cand-11391", "start": 767, "end": 768, "author": "Marrini, Abbate Orazio", "title": "Serie di Ritratti di Celebri Pittori dipinti di propria mano", "details": "2 vols., Firenze 1765", "kind": "two-volume book set", "related": ["cand-7926"], "corrections": [{"line": 767, "ocr": "Martini, Abbate Orazio", "print": "Marrini, Abbate Orazio", "note": "The page image shows the surname Marrini with a double r; retain it as printed and keep the similarly named Martini candidate separate for S3."}]},
    {"candidate_id": "cand-11392", "start": 769, "end": 769, "author": "Martin, C. A.", "title": "Storia civile e politica del commercio dei Veneziani", "details": "8 vols., Venezia 1798–1808", "kind": "eight-volume book set", "corrections": [{"line": 769, "ocr": "17981808", "print": "1798–1808", "note": "OCR omits the printed date-range separator."}]},
    {"candidate_id": "cand-11393", "start": 770, "end": 773, "author": "Martin, W.", "title": "‘The life of a Dutch artist’—Part VI: ‘How the painter sold his work’", "details": "Burlington Magazine, XI, 1907, pp. 357–369", "kind": "journal article", "corrections": [{"line": 770, "ocr": "Burlington", "print": "in Burlington", "note": "The publisher heading is displaced above the author/title in OCR."}, {"line": 771, "ocr": "lise", "print": "life", "note": "The page image reads life."}, {"line": 771, "ocr": "thè", "print": "the", "note": "The page image has no accent."}, {"line": 772, "ocr": "Magazine,", "print": "Burlington Magazine,", "note": "The journal title continues across the OCR line break."}]},
    {"candidate_id": "cand-9859", "start": 774, "end": 774, "author": "Martyn, Thomas", "title": "A Tour through Italy", "details": "new edition, London [1791]", "kind": "book"},
    {"candidate_id": "cand-11394", "start": 775, "end": 776, "author": "Marucelli, Francesco", "title": "Indice del Mare Magnum", "details": "pubblicata a cura del Prof. Dott. Guido Biagi, Roma 1882", "kind": "book", "related": ["cand-6410", "cand-6412"], "page_image_notes": ["Keep this named 1882 publication distinct from the related Mare Magnum and Biagi-introduction citation candidates pending S3."]},
    {"candidate_id": "cand-11395", "start": 777, "end": 777, "author": "Matina, L.", "title": "Ducalis Regiae Lararium", "details": "Venezia 1659", "kind": "book", "related": ["cand-1578"]},
    {"candidate_id": "cand-11396", "start": 778, "end": 778, "author": "Matteoli, A.", "title": "‘Macchie di sole e pittura: carteggio L. Cigoli-G. Galilei 1609-1613’", "details": "Accademia degli Euteleti, Città di San Miniato 1959", "kind": "journal article / institutional publication", "related": ["cand-5713"]},
    {"candidate_id": "cand-9922", "start": 779, "end": 779, "author": "Maugain, G.", "title": "Évolution intellectuelle de l’Italie 1657–1750", "details": "Paris 1909", "kind": "book", "corrections": [{"line": 779, "ocr": "Evolution", "print": "Évolution", "note": "The page image shows the initial acute accent."}]},
    {"candidate_id": "cand-9289", "start": 780, "end": 780, "author": "Mauroner, F.", "title": "Luca Carlevarijs", "details": "Venezia 1945", "kind": "book"},
    {"candidate_id": "cand-10606", "start": 781, "end": 782, "author": "Mauroner, F.", "title": "‘Collezionisti e vedutisti settecenteschi a Venezia’", "details": "Arte Veneta, 1947, pp. 48–50", "kind": "journal article", "corrections": [{"line": 781, "ocr": "Arte Veneta,", "print": "in Arte Veneta,", "note": "The periodical heading is displaced before the author in OCR."}]},
    {"candidate_id": "cand-7082", "start": 783, "end": 783, "author": "Mazarin, G.", "title": "Epistolario inedito", "details": "pubblicato da Carlo Morbio, Milano 1842", "kind": "edited correspondence"},
    {"candidate_id": "cand-7083", "start": 784, "end": 785, "author": "Mazarin, G.", "title": "Lettres pendant son ministère", "details": "recueillies et publiées par M. A. Chéruel, 9 vols., Paris 1872–1906", "kind": "nine-volume edited correspondence", "corrections": [{"line": 785, "ocr": "1906. .", "print": "1906.", "note": "The trailing OCR period is not present in print."}]},
    {"candidate_id": "cand-7044", "start": 786, "end": 787, "author": "", "title": "Mazarin, homme d’état et collectionneur 1602–1661", "details": "exposition organisée pour le troisième centenaire de sa mort, Bibliothèque Nationale, Paris 1961", "kind": "exhibition catalogue"},
    {"candidate_id": "cand-11397", "start": 788, "end": 790, "author": "Mazza, Barbara", "title": "‘La vicenda dei “Tombeaux des Princes”: Matrici, storia e fortuna della serie Swiny tra Bologna e Venezia’", "details": "Saggi e Memorie di storia dell’arte, 10, 1976, pp. 79–102", "kind": "journal article", "corrections": [{"line": 789, "ocr": "Saggi e Memorie di storia dell’arte, serie Swiny tra Bologna e Venezia’ in io, 1976, pp.", "print": "serie Swiny tra Bologna e Venezia’ in Saggi e Memorie di storia dell’arte, 10, 1976, pp.", "note": "The page image continues the article title before naming the journal; OCR interleaves the title and journal."}, {"line": 789, "ocr": "io, 1976", "print": "10, 1976", "note": "The page image reads issue 10."}]},
    {"candidate_id": "cand-10452", "start": 791, "end": 791, "author": "Mazzotti, G.", "title": "Le Ville Venete—catalogo", "details": "3a edizione, Treviso 1954", "kind": "catalogue", "corrections": [{"line": 791, "ocr": "Mazzetti, G.:_Le", "print": "Mazzotti, G.: Le", "note": "The page image reads Mazzotti and separates the author punctuation from the title."}]},
    {"candidate_id": "cand-9972", "start": 792, "end": 792, "author": "Melchiori, L.", "title": "Lettere e letterati a Venezia e Padova a mezzo il secolo XVIII", "details": "Padova 1942", "kind": "book"},
    {"candidate_id": "cand-11197", "start": 793, "end": 794, "author": "Meloni Trkulja, Silvia", "title": "‘Luca Giordano a Firenze’", "details": "Paragone, 1972 (267), pp. 25–74", "kind": "journal article", "corrections": [{"line": 793, "ocr": "Paragone,", "print": "in Paragone,", "note": "The periodical heading is displaced above the article in OCR."}]},
    {"candidate_id": "cand-11189", "start": 795, "end": 796, "author": "Meloni Trkulja, Silvia", "title": "‘Leopoldo de’ Medici collezionista’", "details": "Paragone, 1975 (307), pp. 15–38", "kind": "journal article", "corrections": [{"line": 795, "ocr": "Paragone,", "print": "in Paragone,", "note": "The periodical heading is displaced above the article in OCR."}, {"line": 796, "ocr": ". Meloni", "print": "Meloni", "note": "The page image has no initial period."}, {"line": 796, "ocr": "3 07", "print": "307", "note": "OCR inserts a space within the issue number."}, {"line": 796, "ocr": "15-3 8", "print": "15–38", "note": "The page image gives the page range 15–38."}]},
    {"candidate_id": "cand-8812", "start": 797, "end": 797, "author": "[Memmo, Andrea]", "title": "Elementi dell’architettura lodoliana", "details": "Roma 1786", "kind": "book with bracketed author attribution"},
    {"candidate_id": "cand-11398", "start": 798, "end": 799, "author": "[Memmo, Andrea]", "title": "Riflessioni sopra alcuni equivoci sensi espressi dall’Ornatissimo Autore Della Orazione recitata in Venezia nell’Accademia di Pittura nel 1787", "details": "In Padova 1788", "kind": "book with bracketed author attribution"},
    {"candidate_id": "cand-11399", "start": 800, "end": 801, "author": "Memmoli, Decio", "title": "Vita dell’Eminentissimo Signor Cardinale Gio. Garzio Mellino", "details": "Roma 1644", "kind": "book", "mentions": ["Memmoli, Decio"], "corrections": [{"line": 800, "ocr": "Meliino", "print": "Mellino", "note": "The page image reads Mellino."}, {"line": 801, "ocr": "1644Merriman", "print": "1644.\nMerriman", "note": "The page image ends this entry after 1644 and begins the next entry on a new line."}]},
    {"candidate_id": "cand-11199", "start": 801, "end": 803, "author": "Merriman, Mina Pajes", "title": "‘Giuseppe Maria Crespi’s “Jupiter among the Corybantes”’", "details": "Burlington Magazine, 1976, pp. 464–472", "kind": "journal article", "mentions": ["Merriman"], "corrections": [{"line": 801, "ocr": "Merriman,\"", "print": "Merriman,", "note": "The page image has no quotation mark after the author separator; OCR joins the opening to the previous entry."}, {"line": 801, "ocr": "thè", "print": "the", "note": "The page image reads the without an accent."}]},
    {"candidate_id": "cand-4948", "start": 804, "end": 806, "author": "Mezzetti, A.", "title": "‘Contributi a Carlo Maratti’", "details": "Rivista dell’Istituto Nazionale d’Archeologia e Storia dell’Arte, 1955, pp. 253–354", "kind": "journal article", "corrections": [{"line": 804, "ocr": "Rivista dell’Istituto Nazionale d’Archeologia e Storia", "print": "in Rivista dell’Istituto Nazionale d’Archeologia e Storia", "note": "The journal heading is displaced before the entry in OCR."}, {"line": 805, "ocr": "‘Contributi a Carlo Maratti’ in dell’Arte,", "print": "‘Contributi a Carlo Maratti’ in Rivista dell’Istituto Nazionale d’Archeologia e Storia dell’Arte,", "note": "The journal title continues around the article entry in OCR."}]},
]

entry_memmoli = entries[25]
memmoli_prefix, merriman_remainder = source_lines[800].split("Merriman,", 1)
if not memmoli_prefix.endswith("1644") or not merriman_remainder.startswith('"'):
    raise SystemExit("unexpected OCR join at L801")
entry_memmoli["quote"] = "\n".join(source_lines[799:800]) + "\n" + memmoli_prefix
entries[26]["quote"] = (
    "Merriman," + merriman_remainder + "\n" + source_lines[801] + "\n" + source_lines[802]
)
entries[26]["corrections"].append(
    {
        "line": 801,
        "ocr": "1644Merriman,",
        "print": "1644.\nMerriman,",
        "note": "The page image separates the prior record from Merriman’s article.",
    }
)

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
    mention_id = f"m-chp21-bib-l756-806-{len(new_mentions) + 1:03d}"
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


def add_statement(statement_id, entry, candidate_id):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    predicate = entry.get("predicate", "bibliography_lists_publication")
    title = entry["title"].strip("‘’\" ")
    claim = entry.get("claim") or f"Haskell lists {title} in the bibliography."
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
        "text_layer": entry.get("text_layer", "bibliographic entry"),
        "qualification": entry.get(
            "qualification",
            "This records the bibliography entry only; the cited publication was not independently consulted in this S2 pass.",
        ),
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 429,
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
            "predicate": predicate,
            "qualifiers": qualifiers,
            "original_quote": quote,
            "origin": "book",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        }
    )


for index, entry in enumerate(entries, start=1):
    candidate_id = entry["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    expected_type = "event" if entry.get("predicate") == "bibliography_lists_event" else "archive"
    if not candidate or candidate.get("suggested_type") != expected_type:
        raise SystemExit(f"missing/wrong-type bibliographic candidate: {candidate_id}")
    for related_id in entry.get("related", []):
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    quote = source_quote(entry)
    for surface in entry.get("mentions", [quote]):
        if surface not in quote:
            raise SystemExit(f"mention is outside source quote: {candidate_id} {surface!r}")
        add_mention(
            candidate_id,
            surface,
            "S0 bibliography entry; page-image readings and S3 comparisons are recorded on its statement.",
        )
    add_statement(f"st-chp21-bib-l756-806-entry-{index:02d}", entry, candidate_id)

if len(new_candidates) != 11 or len(new_mentions) != 28 or len(new_statements) != 28:
    raise SystemExit(
        f"unexpected migration row counts: candidates={len(new_candidates)}, "
        f"mentions={len(new_mentions)}, statements={len(new_statements)}"
    )

for statement in new_statements:
    if statement["object_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
    qualifiers = statement["qualifiers"]
    for field in ("mentioned_candidate_ids", "related_candidate_ids_for_s3"):
        for candidate_id in qualifiers.get(field, []):
            if candidate_id not in candidate_by_id:
                raise SystemExit(f"{field} FK missing: {statement['statement_id']}: {candidate_id}")

for row in new_mentions:
    if segment_text[int(row["start_char"]) : int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")
ordered_mentions = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(ordered_mentions, ordered_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")

coverage_row["disposition"] = "reviewed"
coverage_row["migration_status"] = "complete"
coverage_row["source_line_ranges"] = "L757-806"
coverage_row["note"] = (
    "Printed p.429 contains 28 bibliography entries, including one exhibition catalogue; "
    "[Page 429] at L756 is only a page marker. Reused 17 archive candidates and added 11 archive "
    "candidates. Page-image review restores displaced journal headings, "
    "corrects OCR spellings and dates, and separates the Memmoli/Merriman entry boundary at L801. "
    "Uncertain citation identities remain linked for S3; cited contents were not independently consulted."
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
            "candidate_count_after": len(all_candidates),
            "mention_count_after": len(all_mentions),
            "statement_count_after": len(all_statements),
            "coverage_rows": len(all_coverage),
            "publication_statements": sum(
                row["predicate"] == "bibliography_lists_publication" for row in new_statements
            ),
            "event_statements": sum(
                row["predicate"] == "bibliography_lists_event" for row in new_statements
            ),
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
