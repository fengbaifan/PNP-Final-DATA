#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 422."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l461-496"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "7557618d47d33b1607c53475cd17836a0d58b362d02a071473f5f1562828ed67"
BACKUP = ".bak-s2-chp21-bibliography-l461-496-20261007"

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
segment_text = "\n".join(source_lines[460:496])
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
    11300,
    26246,
    11520,
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

# Entry boundaries and OCR corrections were checked against PDF physical page 12.
entries = [
    {"candidate_id": "cand-4331", "start": 462, "end": 463,
     "author": "Faldi, Italo",
     "title": "Paolo Guidotti e gli affreschi della “Sala del Cavaliere” nel Palazzo di Bassano di - Sutri",
     "details": "Bollettino d’Arte, 1957, pp. 278-295", "kind": "journal article",
     "page_image_notes": ["The print has a line-initial hyphen before Sutri; the mark is retained in title_as_printed."]},
    {"candidate_id": "cand-11322",
     "new_name": "Conte Marco Fantuzzi, Opere del Canonico Giovanni Andrea Lazzarini (Pesaro, 1806)",
     "new_detail": "Bibliography-level publication record; kept distinct from the volume/page citation locator cand-10366 pending S3; the contents were not independently consulted.",
     "start": 464, "end": 464, "author": "Fantuzzi, Conte Marco",
     "title": "Opere del Canonico Giovanni Andrea Lazzarini", "details": "Pesaro 1806",
     "kind": "book", "related": ["cand-10366"]},
    {"candidate_id": "cand-10443", "start": 465, "end": 465,
     "author": "Farsetti, T. G.",
     "title": "Notizie della famiglia Farsetti con l’albero e le vite di sei uomini illustri a quella spettanti",
     "details": "Venezia 1778", "kind": "book"},
    {"candidate_id": "cand-11323",
     "new_name": "Félibien, Entretiens sur les vies et sur les ouvrages des plus excellens peintres anciens et modernes . . . (nouvelle édition, 6 vols., Trévoux, 1725)",
     "new_detail": "Six-volume set-level publication record; kept distinct from the volume-III page-530 citation locator cand-7077 pending S3; cited contents were not independently consulted.",
     "start": 466, "end": 466, "author": "Félibien",
     "title": "Entretiens sur les vies et sur les ouvrages des plus excellens peintres anciens et modernes . . .",
     "details": "nouvelle édition, 6 vols., Trévoux 1725", "kind": "book set",
     "related": ["cand-7077"],
     "corrections": [{"line": 466, "ocr": "modernes    nouvelle édition",
                      "print": "modernes . . . nouvelle édition"}]},
    {"candidate_id": "cand-5156", "start": 467, "end": 467,
     "author": "Felici, Giuseppe", "title": "Villa Ludovisi in Roma",
     "details": "Roma 1952", "kind": "book"},
    {"candidate_id": "cand-4576", "start": 468, "end": 469,
     "author": "Feliciangeli, B.",
     "title": "Il Cardinale Angelo Giori da Camerino e G. L. Bernini",
     "details": "Sanseverino-Marche 1917", "kind": "book"},
    {"candidate_id": "cand-8777", "start": 470, "end": 470,
     "author": "Ferrari, L.", "title": "I Carmelitani Scalzi a Venezia",
     "details": "Venezia 1882", "kind": "book"},
    {"candidate_id": "cand-9460", "start": 471, "end": 472,
     "author": "Ferrari, Luigi",
     "title": "Gli acquisti dell’Algarotti pel Regio Museo di Dresda",
     "details": "L’Arte, 1900, pp. 150-154", "kind": "journal article"},
    {"candidate_id": "cand-5604", "start": 473, "end": 473,
     "author": "Ferrero, G. G.", "title": "Marino e i Marinisti",
     "details": "Milano-Napoli, 1954", "kind": "book",
     "corrections": [{"line": 473, "ocr": "Milano-Napoli,' 1954",
                      "print": "Milano-Napoli, 1954"}]},
    {"candidate_id": "cand-11324",
     "new_name": "Girolamo Festari, Giornale del viaggio nella Svizzera fatto da Angelo Querini Senatore Veneziano nel 1777 (Venezia, 1835)",
     "new_detail": "The bibliography names Festari and prints ‘a cura di E. Cicogna’; the source does not specify further contributor roles, and the work was not independently consulted.",
     "start": 474, "end": 475, "author": "Festari, Girolamo",
     "title": "Giornale del viaggio nella Svizzera fatto da Angelo Querini Senatore Veneziano nel 1777",
     "details": "a cura di E. Cicogna, Venezia 1835", "kind": "book"},
    {"candidate_id": "cand-9441", "start": 476, "end": 476,
     "author": "Finberg, Hilda", "title": "Canaletto in England",
     "details": "Walpole Society, IX, 1920-1, pp. 21 ff., and X, pp. 75-78",
     "kind": "multi-part journal article",
     "corrections": [{"line": 476, "ocr": "pp. 21 if.", "print": "pp. 21 ff."}]},
    {"candidate_id": "cand-11325",
     "new_name": "M. H. Fisch and T. G. Bergin, The autobiography of Giambattista Vico (New York, 1944)",
     "new_detail": "The bibliography identifies this 1944 publication; it does not state the contributors’ roles. Kept distinct from the generic work candidate cand-9740 and the pages-183–184 citation locator cand-9955 pending S3; contents were not independently consulted.",
     "start": 477, "end": 477, "author": "Fisch, M. H. and Bergin, T. G.",
     "title": "The autobiography of Giambattista Vico", "details": "New York 1944",
     "kind": "book publication; contributor roles unspecified",
     "related": ["cand-9740", "cand-9955"]},
    {"candidate_id": "cand-11326",
     "new_name": "John Fleming, ‘Cardinal Albani’s drawings at Windsor—their purchase by James Adam for George III’ (Connoisseur, 1958)",
     "new_detail": "Solo-authored article as listed in the bibliography; kept distinct from the Vermeule and Fleming 1958 page-164 citation locator cand-5928 pending S3 comparison; the article was not independently consulted.",
     "start": 478, "end": 479, "author": "Fleming, John",
     "title": "Cardinal Albani’s drawings at Windsor—their purchase by James Adam for George III",
     "details": "Connoisseur, 1958, vol. 142, pp. 164-169", "kind": "journal article",
     "related": ["cand-5928"],
     "corrections": [{"line": 478, "ocr": "‘Fleming, John:", "print": "Fleming, John:"}]},
    {"candidate_id": "cand-9557", "start": 480, "end": 480,
     "author": "Fleming, John", "title": "Messrs. Robert and James Adam: Art dealers (I)",
     "details": "Connoisseur, 1959, vol. 144, pp. 168-171", "kind": "journal article",
     "corrections": [{"line": 480, "ocr": "Mssrs.", "print": "Messrs."}]},
    {"candidate_id": "cand-9558", "start": 481, "end": 481,
     "author": "Fleming, John", "title": "Robert Adam and his circle",
     "details": "London 1962", "kind": "book"},
    {"candidate_id": "cand-8229", "start": 482, "end": 482,
     "author": "Florio, Daniele", "title": "Le Grazie",
     "details": "Venezia 1766", "kind": "book"},
    {"candidate_id": "cand-8655", "start": 483, "end": 483,
     "author": "Fochessati, G.", "title": "I Gonzaga di Mantova e l’ultimo duca",
     "details": "Milano 1930", "kind": "book"},
    {"candidate_id": "cand-9844", "start": 484, "end": 484,
     "author": "Fogolari, Gino", "title": "L’Accademia Veneziana di Pittura e Scoltura del Settecento",
     "details": "L’Arte, 1913, pp. 364-394", "kind": "journal article",
     "quote_override": "Fogolari, Gino: ‘L’Accademia Veneziana di Pittura e Scoltura del Settecento’ in L’Arte, 1913, pp. 364-394",
     "corrections": [{"line": 484, "ocr": "394Fogolari, Gino:",
                      "print": "394. [new item] Fogolari, Gino:"}]},
    {"candidate_id": "cand-11327",
     "new_name": "Gino Fogolari, ‘Il bozzetto del Tiepolo per il trasporto della Santa Casa di Loreto’ (Bollettino d’Arte, 1931, pp. 18-32)",
     "new_detail": "The bibliography identifies the article; it was not independently consulted.",
     "start": 484, "end": 484, "author": "Fogolari, Gino",
     "title": "Il bozzetto del Tiepolo per il trasporto della Santa Casa di Loreto",
     "details": "Bollettino d’Arte, 1931, pp. 18-32", "kind": "journal article",
     "quote_override": "Fogolari, Gino: ‘Il bozzetto del Tiepolo per il trasporto della Santa Casa di Loreto’ in Bollettino d’Arte, 1931, pp. 18-32."},
    {"candidate_id": "cand-7894", "start": 485, "end": 485,
     "author": "Fogolari, Gino",
     "title": "Lettere pittoriche del Gran Principe Ferdinando di Toscana a Niccolò Cassana (1698-1709)",
     "details": "Rivista del R. Istituto d’Archeologia e Storia dell’Arte, 1937, pp. 145-186",
     "kind": "journal article",
     "corrections": [{"line": 485, "ocr": "193 7", "print": "1937"}]},
    {"candidate_id": "cand-11328",
     "new_name": "Gino Fogolari, ‘Lettere inedite di G. B. Tiepolo’ (Nuova Antologia, 1942)",
     "new_detail": "The bibliography identifies the article; it was not independently consulted.",
     "start": 486, "end": 487, "author": "Fogolari, Gino",
     "title": "Lettere inedite di G. B. Tiepolo",
     "details": "Nuova Antologia, 1942, Sett.-Ott., pp. 32-37", "kind": "journal article",
     "quote_override": "Fogolari, Gino: ‘Lettere inedite di G. B. Tiepolo’ in Nuova Antologia, 1942, Sett.-Ott., pp.\n32-37",
     "corrections": [{"line": 487, "ocr": "32-37Fomiciova",
                      "print": "32-37. [new item] Fomiciova"}]},
    {"candidate_id": "cand-11208", "start": 487, "end": 487,
     "author": "Fomiciova, Tamara",
     "title": "Alcune opere di artisti della cerchia di Tiepolo nei musei dell’U.R.S.S.",
     "details": "Arte Veneta, 1971, pp. 212-220", "kind": "journal article",
     "quote_override": "Fomiciova, Tamara: ‘Alcune opere di artisti della cerchia di Tiepolo nei musei dell’U.R.S.S.’ in Arte Veneta, 1971, pp. 212-220.",
     "corrections": [{"line": 487, "ocr": "32-37Fomiciova",
                      "print": "32-37. [new item] Fomiciova"}]},
    {"candidate_id": "cand-11329",
     "new_name": "G. J. Fontana, Cento palazzi di Venezia—prima ristampa dall’originale (Venezia, 1934)",
     "new_detail": "The bibliography identifies the book and its reprint note; it was not independently consulted.",
     "start": 488, "end": 488, "author": "Fontana, G. J.",
     "title": "Cento palazzi di Venezia—prima ristampa dall’originale",
     "details": "Venezia 1934", "kind": "book",
     "corrections": [{"line": 488, "ocr": "Venezia-—prima", "print": "Venezia—prima"}]},
    {"candidate_id": "cand-11155", "start": 489, "end": 490,
     "author": "Fontana, Vincenzo",
     "title": "Girolamo Manfrin e la manifattura tabacchi a Venezia di Bernardino Maccaruzzi",
     "details": "Bollettino dei Musei Civici Veneziani, 1977, pp. 51-63",
     "kind": "journal article"},
    {"candidate_id": "cand-11330",
     "new_name": "[G. B. Fontanella], Memorie intorno la vita di Carlo Cordellina (Venezia, 1801)",
     "new_detail": "The author form is bracketed in the bibliography; its attribution and alignment to the person candidate were not independently resolved.",
     "start": 491, "end": 491, "author": "[Fontanella, G. B.]",
     "title": "Memorie intorno la vita di Carlo Cordellina", "details": "Venezia 1801",
     "kind": "book; bracketed author attribution"},
    {"candidate_id": "cand-4838", "start": 492, "end": 492,
     "author": "", "title": "Les Français à Rome",
     "details": "Exhibition at Hôtel de Rohan, Paris 1961",
     "kind": "exhibition reference; catalogue status unresolved"},
    {"candidate_id": "cand-4553", "start": 493, "end": 493,
     "author": "Fraschetti, S.", "title": "Il Bernini", "details": "Milano 1900", "kind": "book"},
    {"candidate_id": "cand-7253", "start": 494, "end": 495,
     "author": "Freeden, Max H. von",
     "title": "Quellen zur Geschichte des Barocks in Franken unter dem Einfluss des Hauses Schönborn",
     "details": "I. Teil, zweiter Halbband, Würzburg 1955", "kind": "book volume"},
    {"candidate_id": "cand-9466", "start": 496, "end": 496,
     "author": "Freeden, Max H. von", "title": "Das Meisterwerk des G. B. Tiepolo",
     "details": "München 1956", "kind": "book"},
]

if len(entries) != 29 or len({row["candidate_id"] for row in entries}) != 29:
    raise SystemExit("bibliography publication specification is incomplete or duplicated")
covered_lines = {line for entry in entries for line in range(entry["start"], entry["end"] + 1)}
if covered_lines != set(range(462, 497)):
    raise SystemExit("bibliography entry line coverage is incomplete")

expected_name_updates = {
    "cand-4331": (
        "Paolo Guidotti e gli affreschi della Sala del Cavaliere nel Palazzo di Bassano di Sutri (Faldi, 1957)",
        "Italo Faldi, Paolo Guidotti e gli affreschi della “Sala del Cavaliere” nel Palazzo di Bassano di Sutri (Bollettino d’Arte, 1957)",
        "Printed bibliography p.422 confirms the cited article title and publication details; the article was not independently consulted.",
    ),
    "cand-10443": (
        "Family history of the Farsetti published by Tommaso Giuseppe in 1778",
        "T. G. Farsetti, Notizie della famiglia Farsetti con l’albero e le vite di sei uomini illustri a quella spettanti (Venezia, 1778)",
        "Printed bibliography p.422 supplies the title and publication place; cited contents were not independently consulted.",
    ),
    "cand-5156": (
        "Felici, cited publication on Cardinal Ludovico Ludovisi’s collections; title unspecified",
        "Giuseppe Felici, Villa Ludovisi in Roma (Roma, 1952)",
        "Printed bibliography p.422 identifies the previously unspecified title and publication details; contents were not independently consulted.",
    ),
    "cand-4576": (
        "Feliciangeli, cited source; title and locator unspecified",
        "B. Feliciangeli, Il Cardinale Angelo Giori da Camerino e G. L. Bernini (Sanseverino-Marche, 1917)",
        "Printed bibliography p.422 supplies the title and publication details; cited content was not independently consulted.",
    ),
    "cand-8777": (
        "L. Ferrari, 1882 (citation locator; cited p.22 and p.269 note 2)",
        "L. Ferrari, I Carmelitani Scalzi a Venezia (Venezia, 1882)",
        "Printed bibliography p.422 identifies the work behind this short citation; the cited pamphlet and Ferrari book were not independently consulted.",
    ),
    "cand-9441": (
        "Hilda Finberg, 'Canaletto in England' (Walpole Society, 1920-1; citation locator)",
        "Hilda Finberg, ‘Canaletto in England’ (Walpole Society IX (1920-1), pp. 21 ff.; X, pp. 75-78)",
        "Printed bibliography p.422 supplies the two volume references and locators; the article was not independently consulted.",
    ),
    "cand-9557": (
        "John Fleming, Mssrs. Robert and James Adam: Art dealers (I), Connoisseur 144 (1959), pp.168-171",
        "John Fleming, ‘Messrs. Robert and James Adam: Art dealers (I)’ (Connoisseur, vol. 144, 1959, pp. 168-171)",
        "Printed p.422 confirms the title spelling and publication details; cited page 171 was not independently consulted.",
    ),
    "cand-8655": (
        "Fochessati, p.278 (citation locator; title pending bibliography review)",
        "G. Fochessati, I Gonzaga di Mantova e l’ultimo duca (Milano, 1930)",
        "Printed bibliography p.422 identifies the work behind the p.278 citation; the cited page was not independently consulted.",
    ),
    "cand-9844": (
        "L’Accademia Veneziana di Pittura e Scoltura del Settecento (1913)",
        "Gino Fogolari, ‘L’Accademia Veneziana di Pittura e Scoltura del Settecento’ (L’Arte, 1913, pp. 364-394)",
        "Printed bibliography p.422 supplies the full journal and page details; the article was not independently consulted.",
    ),
    "cand-11208": (
        "Fomiciova publication cited at p.406 note 8 (title and year unspecified)",
        "Tamara Fomiciova, ‘Alcune opere di artisti della cerchia di Tiepolo nei musei dell’U.R.S.S.’ (Arte Veneta, 1971, pp. 212-220)",
        "Printed bibliography p.422 identifies the article and publication details; it was not independently consulted.",
    ),
    "cand-11155": (
        "Vincenzo Fontana's article on Girolamo Manfrin's tobacco manufacture",
        "Vincenzo Fontana, ‘Girolamo Manfrin e la manifattura tabacchi a Venezia di Bernardino Maccaruzzi’ (Bollettino dei Musei Civici Veneziani, 1977, pp. 51-63)",
        "Printed bibliography p.422 identifies the title and publication details; the article was not independently consulted.",
    ),
    "cand-4838": (
        "Les Français à Rome exhibition catalogue (Paris, 1961)",
        "Les Français à Rome (Paris exhibition, 1961)",
        "Printed bibliography p.422 describes an exhibition at Hôtel de Rohan; a p.202 note associates item 250 with the Archives Nationales. Preserve both source descriptions without resolving the venue or catalogue status.",
    ),
    "cand-4553": (
        "Fraschetti, cited publication, p. 107; title unspecified",
        "S. Fraschetti, Il Bernini (Milano, 1900)",
        "Printed bibliography p.422 identifies the work behind the p.107 citation; the cited page was not independently consulted.",
    ),
}

natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold()): row["candidate_id"]
    for row in candidates
    if row["suggested_type"].strip().casefold() == "archive"
}
for candidate_id, (expected, updated, detail) in expected_name_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type bibliography candidate: {candidate_id}")
    if candidate["canonical_name"] != expected:
        raise SystemExit(f"candidate identity label changed: {candidate_id}")
    key = (updated.strip().casefold(), "archive")
    collision = natural_keys.get(key)
    if collision and collision != candidate_id:
        raise SystemExit(f"candidate rename collides with archive candidate {collision}: {candidate_id}")
    natural_keys.pop((expected.strip().casefold(), "archive"), None)
    natural_keys[key] = candidate_id
    candidate["canonical_name"] = updated
    candidate["detail"] = f'{candidate.get("detail", "").rstrip()} {detail}'.strip()

new_candidates = []
for entry in entries:
    if not entry.get("new_name"):
        continue
    candidate_id = entry["candidate_id"]
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (entry["new_name"].strip().casefold(), "archive")
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {entry['new_name']}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=entry["new_name"],
        suggested_type="archive",
        status="open",
        detail=entry["new_detail"],
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{entry['start']}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys[key] = candidate_id

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
        mention_id=f"m-chp21-bib-l461-496-{len(new_mentions) + 1:03d}",
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
        "S0 bibliography entry; page-image OCR corrections are recorded on its statement.",
    )
    record = {
        "author_as_printed": entry["author"],
        "title_as_printed": entry["title"],
        "publication_details_as_printed": entry["details"],
        "record_kind": entry["kind"],
        "printed_page": 422,
    }
    qualifiers = {
        "text_layer": "bibliographic entry",
        "qualification": (
            "This records the book bibliography entry only; the cited publication or event record "
            "was not independently consulted in this S2 pass."
        ),
        "bibliographic_record": record,
    }
    if entry.get("page_image_notes"):
        qualifiers["page_image_notes"] = entry["page_image_notes"]
    if entry.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("related"):
        qualifiers["related_candidate_ids_for_s3"] = entry["related"]
    add_statement(
        f"st-chp21-bib-l461-496-entry-{index:02d}",
        candidate_id,
        quote,
        entry["start"],
        entry["end"],
        f'Haskell lists {entry["title"]} in the bibliography.',
        qualifiers,
    )

if len(new_candidates) != 9 or len(new_mentions) != 29 or len(new_statements) != 29:
    raise SystemExit("unexpected migration row counts")
if [row["candidate_id"] for row in new_candidates] != [
    f"cand-{number}" for number in range(11322, 11331)
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
coverage_by_id[SEGMENT]["source_line_ranges"] = "L461-496"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.422 contains 29 bibliography entries, including an exhibition reference; "
    "the [Page 422] marker is not a record. "
    "Reused 20 archive candidates and added 9. Fantuzzi, Félibien, Vico-edition, and Fleming "
    "locator overlaps remain distinct candidates for S3; the bracketed Fontanella byline is "
    "unresolved. PDF physical page 12 OCR corrections and two fused-entry splits are recorded "
    "in statement qualifiers; S0 remains unchanged. Cited works were not independently consulted."
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "printed_page": 422,
    "publication_records": len(entries),
    "reused_archive_candidates": len(entries) - len(new_candidates),
    "new_archive_candidates": [row["candidate_id"] for row in new_candidates],
    "candidate_labels_refined": len(expected_name_updates),
    "deferred_candidate_comparisons": [
        "cand-10366", "cand-7077", "cand-9740", "cand-9955", "cand-5928"
    ],
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
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
