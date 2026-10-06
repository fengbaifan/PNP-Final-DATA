#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 413."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l87-127"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "ef9fcd4e36fac62f01d868ff2fd9809bf39e57fc25ec98540cb9e24af072d373"
BACKUP = ".bak-s2-chp21-bibliography-l87-127-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("bibliography Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("bibliography PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[86:127])
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
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11211, 25985, 11261, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

new_candidate_specs = [
    ("cand-11233", "Sandrina Bandera, ‘Un corrispondente cremonese di Leopoldo de’ Medici’ (Paragone, 1979)", "archive", 94, "Bibliography entry gives this article's title, issue number, year, and pages; cited contents were not independently consulted."),
    ("cand-11234", "Urbano Barberini, ‘Pietro da Cortona e l’arazzeria Barberini’ (Bollettino d’Arte, 1950)", "archive", 97, "Bibliography entry records the article and two page spans; contents were not independently consulted."),
    ("cand-11235", "Urbano Barberini, ‘Gli arazzi e i cartoni della serie Vita di Urbano VIII’ (Bollettino d’Arte, 1968)", "archive", 99, "Bibliography entry identifies the article about the Barberini tapestry series; contents were not independently consulted."),
    ("cand-11236", "A. Bardella, ‘Come si acquistava la nobiltà Veneta nella seconda metà del ’600’ (Vicenza, 1937)", "archive", 104, "Bibliography entry lists a May–June 1937 publication in Vicenza; publication format beyond the printed entry is not inferred."),
    ("cand-11237", "G. Baretti, An account of the manners and customs of Italy (London, 1768)", "archive", 106, "Bibliography entry identifies the London 1768 publication; its contents were not independently consulted."),
    ("cand-11238", "Niccolò Barozzi and Guglielmo Berchet, Relazioni degli Stati Europei, Series III: Italy, Rome (2 vols., 1877–1878)", "archive", 107, "Bibliography and p.413 image identify a two-volume set, 1877–78. S0 OCR omits the printed line ‘2 vols., 1877-8’; keep this set separate from volume-specific candidates cand-4365 and cand-6006 pending S3."),
    ("cand-11239", "Michele Battagia, Delle Accademie Veneziane (Venice, 1826)", "archive", 119, "Bibliography entry identifies the Venice 1826 publication; S0 OCR misreads the surname, corrected from the PDF image in statement qualifiers."),
    ("cand-11240", "E. Battisti, ‘Alcune “Vite” inedite di L. Pascoli’ (Commentari, 1953)", "archive", 122, "Bibliography entry supplies the article title and page range; cited contents were not independently consulted."),
    ("cand-11241", "E. Battisti, L’Antirinascimento (Milan, 1962)", "archive", 124, "Bibliography entry identifies the Milan 1962 book; it remains distinct from Battisti's separate 1953 and 1958 articles."),
]

entries = [
    {"candidate_id":"cand-4846","start":88,"end":88,"author":"Baldinucci, Filippo","title":"Notizie de’ Professori del disegno da Cimabue in qua, Secolo V dal 1610 al 1670","details":"Vol. VI, Florence, 1728","kind":"book volume","related":["cand-8601"]},
    {"candidate_id":"cand-4548","start":89,"end":90,"author":"Baldinucci, Filippo","title":"Vita del Cavaliere Gio. Lorenzo Bernini","details":"Edited with notes by Sergio Samek Ludovici, Milan, 1948","kind":"edited book"},
    {"candidate_id":"cand-6181","start":91,"end":93,"author":None,"title":"I Bamboccianti, Pittori della vita popolare nel seicento","details":"Exhibition organized by Alessandro Morandotti; catalogue edited by Giuliano Briganti; Organizzazione Mostre d’Arte ‘Antiquaria’, Rome, 1950","kind":"exhibition catalogue"},
    {"candidate_id":"cand-11233","start":94,"end":95,"author":"Bandera, Sandrina","title":"Un corrispondente cremonese di Leopoldo de’ Medici: Giovan Battista Natali e la provenienza dei disegni cremonesi degli Uffizi","details":"Paragone, 1979 (347), pp. 34–116","kind":"journal article"},
    {"candidate_id":"cand-4378","start":96,"end":96,"author":"Banti, Anna","title":"Europa Milleseicentosei—diario di viaggio di Bernardo Bizoni","details":"Milan, 1942","kind":"book"},
    {"candidate_id":"cand-11234","start":97,"end":98,"author":"Barberini, Urbano","title":"Pietro da Cortona e l’arazzeria Barberini","details":"Bollettino d’Arte, 1950, pp. 43–51 and 145–152","kind":"journal article"},
    {"candidate_id":"cand-11235","start":99,"end":100,"author":"Barberini, Urbano","title":"Gli arazzi e i cartoni della serie ‘Vita di Urbano VIII’ della Arazzeria Barberini","details":"Bollettino d’Arte, 1968, pp. 92–100","kind":"journal article","corrections":[{"line":99,"ocr":"Vili","print":"VIII"}]},
    {"candidate_id":"cand-4852","start":101,"end":101,"author":"Barbi, Michele","title":"Notizie della vita e delle opere di Francesco Bracciolini","details":"Florence, 1897","kind":"book"},
    {"candidate_id":"cand-11099","start":102,"end":103,"author":"Barcham, William","title":"Canaletto and a Commission from Consul Smith","details":"Art Bulletin, 1977, pp. 383–393","kind":"journal article","corrections":[{"line":103,"ocr":"PP383-393","print":"pp. 383–393"}]},
    {"candidate_id":"cand-11236","start":104,"end":105,"author":"Bardella, A.","title":"Come si acquistava la nobiltà Veneta nella seconda metà del ’600","details":"Vicenza, May–June 1937","kind":"periodical contribution"},
    {"candidate_id":"cand-11237","start":106,"end":106,"author":"Baretti, G.","title":"An account of the manners and customs of Italy","details":"London, 1768","kind":"book"},
    {"candidate_id":"cand-11238","start":107,"end":108,"author":"Barozzi, Niccolò e Berchet, Guglielmo","title":"Relazioni degli Stati Europei lette al Senato dagli Ambasciatori Veneti del secolo decimosettimo, Serie III—Italia: Relazioni di Roma","details":"2 vols., 1877–1878; publication place not stated in this entry","kind":"edited documentary series","print_only_text":"2 vols., 1877-8.","related":["cand-4365","cand-6006"]},
    {"candidate_id":"cand-7872","start":109,"end":109,"author":"Bartarelli, Aldo","title":"Anton Domenico Gabbiani","details":"Rivista d’Arte, 1951, pp. 107–130","kind":"journal article","corrections":[{"line":109,"ocr":"13'0","print":"130"}]},
    {"candidate_id":"cand-7868","start":110,"end":111,"author":"Bartolozzi, Sebastiano Benedetto","title":"Vita di Antonio Franchi Lucchese, pittor fiorentino","details":"Florence, 1754","kind":"book","quote":"Bartolozzi, Sebastiano Benedetto: Vita di Antonio Franchi Lucchese, pittor fiorentino, Firenze\n1754","corrections":[{"line":111,"ocr":"1754Bartsch","print":"1754. [new line] Bartsch"}]},
    {"candidate_id":"cand-5609","start":111,"end":111,"author":"Bartsch, Adam","title":"Le Peintre Graveur","details":"Leipzig, 1854","kind":"book","quote":"Bartsch, Adam: Le Peintre Graveur, Leipzig 1854."},
    {"candidate_id":"cand-10907","start":112,"end":114,"author":"Baschet, Armand","title":"Négotiation d’œuvres de tapisserie de Flandre et de France par le nonce Guido Bentivoglio pour le Cardinal Borghèse (1610–1621)","details":"Gazette des Beaux-Arts, 1861 (XI), pp. 406–415; 1862 (XII), pp. 32–45","kind":"journal article","corrections":[{"line":112,"ocr":"Negotiation","print":"Négotiation"},{"line":113,"ocr":"Borghése","print":"Borghèse"}]},
    {"candidate_id":"cand-9842","start":115,"end":115,"author":"Bassi, Elena","title":"La Regia Accademia di Belle Arti di Venezia","details":"Florence, 1941","kind":"book"},
    {"candidate_id":"cand-8183","start":116,"end":117,"author":"Bassi, Elena","title":"Episodi dell’edilizia veneziana nel secolo XVII e XVIII—Palazzo Pesaro","details":"Critica d’Arte, 1959, pp. 240–264","kind":"journal article","corrections":[{"line":117,"ocr":"19 5 9","print":"1959"}]},
    {"candidate_id":"cand-7021","start":118,"end":118,"author":"Batiffol, Louis","title":"La vie intime d’une reine de France au XVIIème siècle","details":"Paris, 1906","kind":"book"},
    {"candidate_id":"cand-11239","start":119,"end":119,"author":"Battagia, Michele","title":"Delle Accademie Veneziane—dissertazione storica","details":"Venice, 1826","kind":"book","corrections":[{"line":119,"ocr":"Battegia","print":"Battagia"}]},
    {"candidate_id":"cand-8369","start":120,"end":120,"author":"Battistella, O.","title":"La Villa Soderini","details":"Nervesa, 1903","kind":"book","corrections":[{"line":120,"ocr":"Battistélla","print":"Battistella"}]},
    {"candidate_id":"cand-8815","start":121,"end":121,"author":"Battistella, O.","title":"Gaetano Zompini","details":"Bologna, 1930","kind":"book"},
    {"candidate_id":"cand-11240","start":122,"end":122,"author":"Battisti, E.","title":"Alcune ‘Vite’ inedite di L. Pascoli","details":"Commentari, 1953, pp. 30–43","kind":"journal article","corrections":[{"line":122,"ocr":"Z0-4Z","print":"30–43"}]},
    {"candidate_id":"cand-9479","start":123,"end":123,"author":"Battisti, E.","title":"Juvarra a Sant’Ildefonso","details":"Commentari, 1958, pp. 273–297","kind":"journal article"},
    {"candidate_id":"cand-11241","start":124,"end":124,"author":"Battisti, E.","title":"L’Antirinascimento","details":"Milan, 1962","kind":"book"},
    {"candidate_id":"cand-7351","start":125,"end":125,"author":"Baudi di Vesme, A.","title":"Sull’acquisto fatto da Carlo Emanuele III, Re di Sardegna, della quadreria del Principe Eugenio di Savoia","details":"Miscellanea di Storia Italiana, 1886, pp. 161–256","kind":"journal article"},
    {"candidate_id":"cand-10410","start":126,"end":127,"author":"Baudi di Vesme, A.","title":"Paralipomeni tiepoleschi","details":"In Scritti in onore di R. Renier, Torino, 1912","kind":"essay in collected volume"},
]
if len(entries) != 27 or len({entry["candidate_id"] for entry in entries}) != 27:
    raise SystemExit("bibliography entry specification is incomplete or duplicated")

natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
    for row in candidates
}
new_candidates = []
for candidate_id, name, kind, line_number, detail in new_candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (name.casefold(), kind.casefold())
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {name}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=name,
        suggested_type=kind,
        status="open",
        detail=detail,
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{line_number}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

for entry in entries:
    candidate = candidate_by_id.get(entry["candidate_id"])
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {entry['candidate_id']}")

candidate_detail_updates = {
    "cand-4378": "Bibliography line 96 identifies this short-form diary reference as Anna Banti, Europa Milleseicentosei—diario di viaggio di Bernardo Bizoni (Milan, 1942); the book was not independently consulted.",
    "cand-6181": "Bibliography lines 91–93 supply the catalogue subtitle and organizer/editor details for the 1950 I Bamboccianti exhibition; contents were not independently consulted.",
    "cand-4852": "Bibliography line 101 identifies Barbi’s publication as Notizie della vita e delle opere di Francesco Bracciolini (Florence, 1897); contents were not independently consulted.",
    "cand-11099": "Bibliography lines 102–103 identify the postscript’s Barcham reference as ‘Canaletto and a Commission from Consul Smith’ (Art Bulletin, 1977, pp. 383–393); article not independently consulted.",
    "cand-8183": "Bibliography lines 116–117 identify the 1959 Elena Bassi article as ‘Episodi dell’edilizia veneziana nel secolo XVII e XVIII—Palazzo Pesaro’; article not independently consulted.",
    "cand-8369": "Bibliography line 120 identifies the 1903 Battistella reference as La Villa Soderini; cited pages were not independently consulted.",
    "cand-8815": "Bibliography line 121 identifies the 1930 Battistella reference as Gaetano Zompini; cited pages were not independently consulted.",
    "cand-10907": "Bibliography lines 112–114 give the title and two-part publication details for the Baschet material on Guido Bentivoglio; the cited articles were not independently consulted.",
    "cand-7351": "Bibliography line 125 supplies the title ‘Sull’acquisto fatto da Carlo Emanuele III, Re di Sardegna, della quadreria del Principe Eugenio di Savoia’ (1886); article not independently consulted.",
    "cand-10410": "Bibliography lines 126–127 identify the 1912 Baudi di Vesme reference as ‘Paralipomeni tiepoleschi’ in Scritti in onore di R. Renier; cited pages were not independently consulted.",
}
for candidate_id, detail in candidate_detail_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type short-citation candidate: {candidate_id}")
    if detail in candidate.get("detail", ""):
        raise SystemExit(f"candidate detail already updated: {candidate_id}")

mentions = list(mentions)
mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
line_offsets = {}
offset = 0
for line_number in range(87, 128):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1
new_mentions = []

def add_mention(entry, candidate_id):
    surface = entry.get("quote") or "\n".join(source_lines[entry["start"] - 1:entry["end"]])
    position = segment_text.find(surface)
    if position < 0 or segment_text.find(surface, position + 1) >= 0:
        raise SystemExit(f"mention span text absent or ambiguous for {candidate_id}: {surface!r}")
    start = position
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(start), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} L{entry['start']}-{entry['end']}")
    row = {field: "" for field in mention_fields}
    row.update(
        mention_id=f"m-chp21-bib-l87-127-{len(new_mentions)+1:03d}",
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=start,
        end_char=end,
        note="Complete bibliography entry. OCR omissions/corrections from the physical page are recorded in its statement qualifiers.",
    )
    new_mentions.append(row)
    mention_keys.add(key)

for entry in entries:
    add_mention(entry, entry["candidate_id"])

new_statements = []
for index, entry in enumerate(entries, start=1):
    raw = entry.get("quote") or "\n".join(source_lines[entry["start"] - 1:entry["end"]])
    qualifier = {
        "source_line_start": entry["start"],
        "source_line_end": entry["end"],
        "claim": f"Haskell lists {entry['title']} in the book bibliography.",
        "speaker": "Haskell’s bibliography",
        "text_layer": "bibliographic entry",
        "qualification": "This statement records the printed bibliography entry; the cited publication was not independently consulted in this S2 pass.",
        "relation_candidate": False,
        "mentioned_candidate_ids": [entry["candidate_id"]],
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 413,
        },
    }
    if entry.get("corrections"):
        qualifier["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("print_only_text"):
        qualifier["page_image_text_missing_from_s0"] = {
            "text": entry["print_only_text"],
            "location": "CHP-21Bibliography.pdf physical page 3, immediately after the Barozzi–Berchet entry",
            "handling": "preserved as a page-image addendum; S0 source text is not rewritten",
        }
    if entry.get("related"):
        qualifier["related_candidate_ids_for_s3"] = entry["related"]
    new_statements.append({
        "statement_id": f"st-chp21-bib-l87-127-entry-{index:02d}",
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": entry["candidate_id"],
        "predicate": "bibliography_lists_publication",
        "qualifiers": qualifier,
        "original_quote": raw,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    })

if len(new_mentions) != 27 or len(new_statements) != 27 or len(new_candidates) != 9:
    raise SystemExit("unexpected migration row counts")
for statement in new_statements:
    if statement["statement_id"] in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement['statement_id']}")
    if statement["object_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L87-127"
coverage_by_id[SEGMENT]["note"] = "Printed p.413 contains 27 publication entries; p.413 image supplies ‘2 vols., 1877-8.’ missing from S0 OCR and confirms line-level corrections. Entries are bibliographic records, not claims that the cited publications were read."
all_candidates = candidates + sorted(new_candidates, key=lambda row: int(row["candidate_id"].split("-")[1]))
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment": SEGMENT,
    "new_publication_candidates": [row["candidate_id"] for row in new_candidates],
    "reused_publication_candidates": 27 - len(new_candidates),
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "candidate_detail_updates": sorted(candidate_detail_updates),
    "page_image_text_missing_from_s0": "2 vols., 1877-8.",
    "coverage": {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L87-127"},
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP)
        if backup.exists():
            raise SystemExit(f"recovery copy already exists: {backup.name}")
        shutil.copy2(path, backup)
    for candidate_id, detail in candidate_detail_updates.items():
        old = candidate_by_id[candidate_id].get("detail", "").rstrip()
        candidate_by_id[candidate_id]["detail"] = f"{old} {detail}".strip()
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
