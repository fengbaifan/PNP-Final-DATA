#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 415."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l165-205"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "3538bdc1764882c9225da55c438f8a4335d62981f4697f565ef83dec77ecb19e"
BACKUP = ".bak-s2-chp21-bibliography-l165-205-20261004"

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
segment_text = "\n".join(source_lines[164:205])
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
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11227, 26039, 11316, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

new_candidate_specs = [
    ("cand-11249", "Jan Bialostocki, ‘Une idée de Léonard réalisée par Poussin’ (Revue des Arts, 1954, pp. 131–136)", 170, "The bibliography identifies the article and range; contents were not independently consulted."),
    ("cand-11250", "Jan Bialostocki, ‘Poussin et le “Traité de la Peinture” de Léonard’ (Actes du Colloque Poussin, 1960, vol. I, pp. 133–140)", 172, "The bibliography identifies the proceedings article and range; contents were not independently consulted."),
    ("cand-11251", "Anthony Blunt, ‘The Annunciation by Nicolas Poussin’ (Bulletin de la Société Poussin, vol. I, 1947, pp. 18–25)", 195, "The bibliography identifies the article; contents were not independently consulted."),
    ("cand-11252", "Anthony Blunt, ‘A neo-Palladian programme executed by Visentini and Zuccarelli for Consul Smith’ (Burlington Magazine, 1958, pp. 283–284)", 200, "The bibliography identifies the article; contents were not independently consulted."),
]

entries = [
    {"candidate_id":"cand-11123","start":166,"end":167,"author":"Bettagno, Alessandro","title":"Caricature di Anton Maria Zanetti—Fondazione Giorgio Cini","details":"Exhibition catalogue; Venice, Vicenza, 1969","kind":"exhibition catalogue"},
    {"candidate_id":"cand-10142","start":168,"end":168,"author":"Bettinelli, Saverio","title":"Lettere inglesi","details":"No publication details stated in this entry","kind":"publication; format and edition unspecified"},
    {"candidate_id":"cand-8549","start":169,"end":169,"author":"Bevilacqua, Ippolito","title":"Memorie della vita di Giambettino Cignaroli, eccellente dipintor veronese","details":"Verona, 1771","kind":"book"},
    {"candidate_id":"cand-11249","start":170,"end":171,"author":"Bialostocki, Jan","title":"Une idée de Léonard réalisée par Poussin","details":"Revue des Arts, 1954, pp. 131–136","kind":"journal article","corrections":[{"line":170,"ocr":"pp. 131—\n136.","print":"pp. 131–136"}]},
    {"candidate_id":"cand-11250","start":172,"end":172,"author":"Bialostocki, Jan","title":"Poussin et le ‘Traité de la Peinture’ de Léonard","details":"Actes du Colloque Poussin, 1960, vol. I, pp. 133–140","kind":"proceedings article","corrections":[{"line":172,"ocr":"i960","print":"1960"}]},
    {"candidate_id":"cand-8787","start":173,"end":174,"author":"Bianchini, Giuseppe","title":"La chiesa di S. Maria di Nazareth detta degli Scalzi in Venezia","details":"Venice, 1894","kind":"book"},
    {"candidate_id":"cand-8271","start":175,"end":176,"author":"Biasutti, Mons. Dott. Guglielmo","title":"Storia e Guida del Palazzo Arcivescovile di Udine","details":"Udine, 1958","kind":"book"},
    {"candidate_id":"cand-6458","start":177,"end":178,"author":"Bildt, Baron C. de","title":"Queen Christina’s pictures","details":"The Nineteenth Century, vol. LVI, 1904, pp. 989–1003","kind":"journal article"},
    {"candidate_id":"cand-5596","start":179,"end":180,"author":"Bildt, C. di","title":"Cristina di Svezia e Paolo Giordano II duca di Bracciano","details":"Archivio della Società Romana di Storia Patria, 1906, pp. 5–32","kind":"journal article"},
    {"candidate_id":"cand-11101","start":181,"end":182,"author":"Binion, Alice","title":"From Schulenburg’s Gallery and Records","details":"Burlington Magazine, 1970, pp. 297–303","kind":"journal article","corrections":[{"line":182,"ocr":"PP297-303","print":"pp. 297–303"}]},
    {"candidate_id":"cand-7075","start":183,"end":183,"author":"Bjurström, Per","title":"Giacomo Torelli and Baroque Stage Design","details":"Stockholm, 1961","kind":"book"},
    {"candidate_id":"cand-9445","start":184,"end":184,"author":"Bjurström, Per","title":"Carl Gustaf Tessin as a collector of drawings","details":"Contributions to the History and Theory of Art, Figura, new series 6, Uppsala, 1967, pp. 99–120","kind":"journal article"},
    {"candidate_id":"cand-10390","start":185,"end":186,"author":"Blainville, de","title":"Travels through Holland, Germany, Switzerland and Italy","details":"3 vols., London, 1767","kind":"book"},
    {"candidate_id":"cand-5981","start":187,"end":187,"author":"Blunt, Anthony","title":"Poussin’s ‘Et in Arcadia Ego’","details":"Art Bulletin, 1938, pp. 96–100","kind":"journal article"},
    {"candidate_id":"cand-6005","start":188,"end":189,"author":"Blunt, Anthony","title":"The heroic and the ideal landscape in the work of Nicolas Poussin","details":"Journal of the Warburg and Courtauld Institutes, 1944, pp. 154–168","kind":"journal article"},
    {"candidate_id":"cand-4635","start":190,"end":190,"author":"Blunt, Anthony","title":"French drawings in the Royal Collection at Windsor Castle","details":"London, 1945","kind":"book"},
    {"candidate_id":"cand-5904","start":191,"end":192,"author":"Blunt, Anthony","title":"Two newly discovered landscapes by Nicolas Poussin","details":"Burlington Magazine, 1945, pp. 186–189","kind":"journal article"},
    {"candidate_id":"cand-9522","start":193,"end":194,"author":"Blunt, Anthony","title":"Pictures by Sebastiano and Marco Ricci in the Royal Collections","details":"Burlington Magazine, 1946, pp. 263–268, and 1947, pp. 101–102","kind":"journal article"},
    {"candidate_id":"cand-11251","start":195,"end":196,"author":"Blunt, Anthony","title":"The Annunciation by Nicolas Poussin","details":"Bulletin de la Société Poussin, vol. I, 1947, pp. 18–25","kind":"journal article","corrections":[{"line":195,"ocr":"Poussinin Bulletin","print":"Poussin’ in Bulletin"}]},
    {"candidate_id":"cand-7101","start":197,"end":197,"author":"Blunt, Anthony","title":"Art and Architecture in France 1500–1700","details":"London, 1953","kind":"book"},
    {"candidate_id":"cand-8654","start":198,"end":199,"author":"Blunt, Anthony","title":"The drawings of Castiglione and Stefano della Bella at Windsor Castle","details":"London, 1954","kind":"book"},
    {"candidate_id":"cand-11252","start":200,"end":201,"author":"Blunt, Anthony","title":"A neo-Palladian programme executed by Visentini and Zuccarelli for Consul Smith","details":"Burlington Magazine, 1958, pp. 283–284","kind":"journal article"},
    {"candidate_id":"cand-5618","start":202,"end":202,"author":"Blunt, Anthony","title":"Poussin dans les Musées de province","details":"Revue des Arts, January–February 1958, pp. 5–16","kind":"journal article"},
    {"candidate_id":"cand-4863","start":203,"end":203,"author":"Blunt, Anthony","title":"The Palazzo Barberini: the contributions of Maderno, Bernini and Pietro da Cortona","details":"Journal of the Warburg and Courtauld Institutes, 1958, pp. 256–287","kind":"journal article"},
    {"candidate_id":"cand-7018","start":204,"end":205,"author":"Blunt, Anthony","title":"Poussin studies VIII—a series of Anchorite subjects commissioned by Philip IV from Poussin, Claude and others","details":"Burlington Magazine, 1959, pp. 389–390","kind":"journal article"},
]
if len(entries) != 25 or len({entry["candidate_id"] for entry in entries}) != 25:
    raise SystemExit("bibliography entry specification is incomplete or duplicated")

natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
    for row in candidates
}
new_candidates = []
for candidate_id, name, line_number, detail in new_candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (name.casefold(), "archive")
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {name}")
    row = {field: "" for field in candidate_fields}
    row.update(candidate_id=candidate_id, canonical_name=name, suggested_type="archive", status="open",
               detail=detail, candidate_origin="body-mention", candidate_source_ref=f"{SEGMENT}#L{line_number}")
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

for entry in entries:
    candidate = candidate_by_id.get(entry["candidate_id"])
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {entry['candidate_id']}")

candidate_detail_updates = {
    "cand-11123": "Bibliography lines 166–167 identify Bettagno’s 1969 exhibition catalogue as Caricature di Anton Maria Zanetti—Fondazione Giorgio Cini (Venice exhibition catalogue; Vicenza, 1969). Contents were not independently consulted.",
    "cand-8549": "Bibliography line 169 identifies the Bevilacqua reference as Memorie della vita di Giambettino Cignaroli, eccellente dipintor veronese (Verona, 1771); contents were not independently consulted.",
    "cand-8787": "Bibliography lines 173–174 identify Bianchini’s publication as La chiesa di S. Maria di Nazareth detta degli Scalzi in Venezia (Venice, 1894); contents were not independently consulted.",
    "cand-6458": "Bibliography lines 177–178 identify Bildt’s article as ‘Queen Christina’s pictures’ in The Nineteenth Century, vol. LVI (1904), pp. 989–1003; article not independently consulted.",
    "cand-5596": "Bibliography lines 179–180 identify Bildt’s article as ‘Cristina di Svezia e Paolo Giordano II duca di Bracciano’ (Archivio della Società Romana di Storia Patria, 1906, pp. 5–32); article not independently consulted.",
    "cand-11101": "Bibliography lines 181–182 identify Alice Binion’s article as ‘From Schulenburg’s Gallery and Records’ (Burlington Magazine, 1970, pp. 297–303); the citation locator is corrected from the S0 OCR and the article was not independently consulted.",
    "cand-10390": "Bibliography lines 185–186 identify Blainville’s work as Travels through Holland, Germany, Switzerland and Italy (3 vols., London, 1767), matching the earlier volume-I locator; cited contents were not independently consulted.",
    "cand-5981": "Bibliography line 187 identifies Blunt’s 1938 article as ‘Poussin’s “Et in Arcadia Ego”’ (Art Bulletin, pp. 96–100); article not independently consulted.",
    "cand-6005": "Bibliography lines 188–189 identify the 1944 article as ‘The heroic and the ideal landscape in the work of Nicolas Poussin’ (Journal of the Warburg and Courtauld Institutes, pp. 154–168), matching the earlier p.165 ff. locator; article not independently consulted.",
    "cand-4635": "Bibliography line 190 identifies the 1945 Blunt book as French drawings in the Royal Collection at Windsor Castle (London); contents were not independently consulted.",
    "cand-5904": "Bibliography lines 191–192 identify Blunt’s Burlington Magazine article as ‘Two newly discovered landscapes by Nicolas Poussin’ (1945, pp. 186–189); article not independently consulted.",
    "cand-8654": "Bibliography lines 198–199 identify the 1954 Blunt book cited at pp. 24 and 36 as The drawings of Castiglione and Stefano della Bella at Windsor Castle (London); cited pages were not independently consulted.",
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
new_mentions = []
new_statements = []
existing_claim_keys = {
    (row.get("segment_id", ""), " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold())
    for row in statements if isinstance(row.get("qualifiers"), dict)
}


def source_quote(entry):
    return "\n".join(source_lines[entry["start"] - 1:entry["end"]])


def add_mention(entry):
    surface = source_quote(entry)
    position = segment_text.find(surface)
    if position < 0 or segment_text.find(surface, position + 1) >= 0:
        raise SystemExit(f"mention span text absent or ambiguous for {entry['candidate_id']}: {surface!r}")
    end = position + len(surface)
    key = (SEGMENT, entry["candidate_id"], str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {entry['candidate_id']} L{entry['start']}-{entry['end']}")
    row = {field: "" for field in mention_fields}
    row.update(mention_id=f"m-chp21-bib-l165-205-{len(new_mentions)+1:03d}", segment_id=SEGMENT,
               candidate_id=entry["candidate_id"], surface_form=surface, start_char=position, end_char=end,
               note="Complete S0 bibliography entry. Page-image OCR corrections, where present, are recorded in statement qualifiers.")
    new_mentions.append(row)
    mention_keys.add(key)


def add_statement(index, entry):
    statement_id = f"st-chp21-bib-l165-205-entry-{index:02d}"
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    title = entry["title"]
    claim = f"Haskell lists {title} in the book bibliography."
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    existing_claim_keys.add(claim_key)
    qualifier = {
        "source_line_start": entry["start"],
        "source_line_end": entry["end"],
        "claim": claim,
        "speaker": "Haskell’s bibliography",
        "text_layer": "bibliographic entry",
        "qualification": "This statement records the bibliography entry; the cited publication was not independently consulted in this S2 pass.",
        "relation_candidate": False,
        "mentioned_candidate_ids": [entry["candidate_id"]],
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": title,
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 415,
        },
    }
    if entry.get("corrections"):
        qualifier["page_image_ocr_corrections"] = entry["corrections"]
    statement = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": entry["candidate_id"],
        "predicate": "bibliography_lists_publication",
        "qualifiers": qualifier,
        "original_quote": source_quote(entry),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    new_statements.append(statement)
    statement_by_id[statement_id] = statement


for entry in entries:
    add_mention(entry)
for index, entry in enumerate(entries, start=1):
    add_statement(index, entry)

if len(new_mentions) != 25 or len(new_statements) != 25 or len(new_candidates) != 4:
    raise SystemExit("unexpected migration row counts")
for statement in new_statements:
    if statement["object_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
    start, end = statement["qualifiers"]["source_line_start"], statement["qualifiers"]["source_line_end"]
    if statement["original_quote"] not in "\n".join(source_lines[start - 1:end]):
        raise SystemExit(f"statement quote/line validation failed: {statement['statement_id']}")
for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L165-205"
coverage_by_id[SEGMENT]["note"] = "Printed p.415 contains 25 bibliography entries. PDF comparison confirms S0 entries and supplies OCR corrections for a page range, year, Binion page locator, and the merged word break in Blunt’s Annunciation title; no whole-entry omission found on this page. These are bibliographic references, not evidence that cited contents were read."
all_candidates = candidates + sorted(new_candidates, key=lambda row: int(row["candidate_id"].split("-")[1]))
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment": SEGMENT,
    "new_publication_candidates": [row["candidate_id"] for row in new_candidates],
    "reused_candidates_for_entries": 25 - len(new_candidates),
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "candidate_detail_updates": sorted(candidate_detail_updates),
    "page_image_corrections": ["L170–171 pp.131—136 → pp.131–136", "L172 i960 → 1960", "L182 PP297-303 → pp.297–303", "L195 Poussinin → Poussin’ in"],
    "coverage": {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L165-205"},
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
