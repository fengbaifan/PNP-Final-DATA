"""Restore the reviewed p.351 mention anchors and close its S2 triage; dry-run by default."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
BODY = "chp-14:14_CHP-14_intro:l46-53"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_SHA256 = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA256 = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
STATEMENTS_SHA256 = "0172c31d756037a8309f67cb99af88fac0ceaa519ea7fa6dd814d12574bfbbcd"
MENTIONS_SHA256 = "a6bbc60cdc71c09d9b8164b52f0c4c440f87c0c344c0d24221e6b45705687703"
BACKUP_SUFFIX = ".bak-s2-chp14-p351-semantic-reconcile-20261014"

FALSE_STATEMENTS = {
    "st-chp14-p351-style-based-subject-choice",
    "st-chp14-p351-piazzetta-appraisal",
    "st-chp14-p351-pittoni-appraisal",
    "st-chp14-p351-tiepolo-appraisal",
    "st-chp14-p351-sensitivity-and-influence-limit",
    "st-chp14-p351-history-painters-in-plan",
    "st-chp14-p351-range-and-travel-influence",
    "st-chp14-p351-boucher-subjects-and-cooperation",
    "st-chp14-p351-detachment-from-rome",
    "st-chp14-p351-time-away-and-evidence-basis",
    "st-chp14-p351-old-master-preference-and-modern-art-success",
    "st-chp14-p351-augustus-old-master-preference",
    "st-chp14-p351-pictures-reported-lost",
    "st-chp14-p351-patronage-effect-visible-in-painting",
    "st-chp14-p351-note1-saggio",
    "st-chp14-p351-note2-lost-pictures",
    "st-chp14-p351-history-painters-named",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write reviewed p.351 repairs")
ARGS = parser.parse_args()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as f:
        f.write(data)
        temp = Path(f.name)
    temp.replace(path)


if sha(SOURCE.read_bytes()) != SOURCE_SHA256 or sha(PDF.read_bytes()) != PDF_SHA256:
    raise SystemExit("canonical p.351 Markdown/PDF source changed; refusing to write")

statement_path = TABLES / "book-statements.jsonl"
mention_path = TABLES / "mentions.csv"
for path, expected in ((statement_path, STATEMENTS_SHA256), (mention_path, MENTIONS_SHA256)):
    if sha(path.read_bytes()) != expected:
        raise SystemExit(f"table baseline changed: {path.name}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(source_lines[45:53])
if not body.startswith("[Page 351]\n"):
    raise SystemExit("registered p.351 body segment changed")

candidate_path = TABLES / "entity-candidates.csv"
candidate_fields, candidates = read_csv(candidate_path)
candidate_ids = {row["candidate_id"] for row in candidates}
statement_rows = read_jsonl(statement_path)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
p351_statements = [row for row in statement_rows if row.get("qualifiers", {}).get("printed_page") == 351]
if len(p351_statements) != 45:
    raise SystemExit(f"expected 45 p.351 statements, found {len(p351_statements)}")
unset_ids = {
    row["statement_id"] for row in p351_statements
    if row.get("qualifiers", {}).get("relation_candidate") is None
}
if unset_ids != FALSE_STATEMENTS:
    raise SystemExit(f"p.351 unsettled set changed: {sorted(unset_ids ^ FALSE_STATEMENTS)}")
if sum(row["qualifiers"].get("relation_candidate") is True for row in p351_statements) != 28:
    raise SystemExit("p.351 established relation-candidate count differs from the reviewed result")
for statement_id in FALSE_STATEMENTS:
    statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = False

mention_fields, mentions = read_csv(mention_path)
if any(row["mention_id"].startswith("m-chp14-p351-") for row in mentions):
    raise SystemExit("p.351 mention IDs already exist; refusing to duplicate")
segment_bounds = {BODY: (46, 53), NOTES: (168, 220)}
offsets = {}
for segment_id, (first, last) in segment_bounds.items():
    offset = 0
    for line_no in range(first, last + 1):
        offsets[(segment_id, line_no)] = offset
        offset += len(source_lines[line_no - 1]) + (1 if line_no < last else 0)

new_mentions = []
occupied = set()
counter = 1


def add_surface(segment_id, candidate_id, surface, line_numbers, note=""):
    global counter
    if candidate_id not in candidate_ids:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    matched = False
    for line_no in line_numbers:
        line = source_lines[line_no - 1]
        search_from = 0
        while True:
            pos = line.find(surface, search_from)
            if pos < 0:
                break
            matched = True
            start = offsets[(segment_id, line_no)] + pos
            end = start + len(surface)
            key = (segment_id, candidate_id, start, end)
            if key not in occupied:
                new_mentions.append({
                    "mention_id": f"m-chp14-p351-{counter:04d}",
                    "segment_id": segment_id,
                    "candidate_id": candidate_id,
                    "surface_form": surface,
                    "start_char": str(start),
                    "end_char": str(end),
                    "note": note,
                })
                occupied.add(key)
                counter += 1
            search_from = pos + 1
    if not matched:
        raise SystemExit(f"surface missing from source: {surface!r} at {line_numbers}")


def add_pronouns(segment_id, candidate_id, forms, line_numbers,
                 note="Coreference resolved from the immediate passage context."):
    global counter
    matched = False
    for line_no in line_numbers:
        line = source_lines[line_no - 1]
        for form in forms:
            for match in re.finditer(rf"(?<![\w]){re.escape(form)}(?![\w])", line):
                matched = True
                start = offsets[(segment_id, line_no)] + match.start()
                end = start + len(form)
                key = (segment_id, candidate_id, start, end)
                if key not in occupied:
                    new_mentions.append({
                        "mention_id": f"m-chp14-p351-{counter:04d}",
                        "segment_id": segment_id,
                        "candidate_id": candidate_id,
                        "surface_form": form,
                        "start_char": str(start),
                        "end_char": str(end),
                        "note": note,
                    })
                    occupied.add(key)
                    counter += 1
    if not matched:
        raise SystemExit(f"pronoun missing from source: {forms} at {line_numbers}")


for surface, cid, line_numbers, note in [
    ("Tiepolo", "cand-2572", [47, 49, 53], ""),
    ("Pittoni", "cand-1950", [47, 48, 53], ""),
    ("Piazzctta", "cand-1902", [47], "The scanned print reads Piazzetta; S0 OCR retained unchanged."),
    ("Piazzetta", "cand-1902", [48, 52, 53], ""),
    ("Zuccarelli", "cand-2879", [50, 53], ""),
    ("Pannini", "cand-1827", [50, 51], ""),
    ("Canaletto", "cand-0499", [50], ""),
    ("Boucher", "cand-0421", [50], ""),
    ("Balestra", "cand-0168", [51], ""),
    ("Donato Creti", "cand-0889", [50, 51], ""),
    ("Francesco de Mura", "cand-1716", [51], ""),
    ("Solimena", "cand-2484", [51], ""),
    ("Ercole Lefli", "cand-1383", [51], "The scanned print reads Ercole Lelli; S0 OCR retained unchanged."),
    ("Jacopo Amigoni", "cand-0094", [51], ""),
    ("Amigoni", "cand-0094", [52], ""),
    ("Mancini", "cand-1506", [51], ""),
    ("Crespi", "cand-0871", [51], ""),
    ("Venice", "cand-2719", [52], ""),
    ("Bologna", "cand-0381", [51, 52], ""),
    ("Rome", "cand-4490", [51, 52], ""),
    ("Augustus", "cand-0151", [52], ""),
    ("gallery", "cand-9091", [50, 52], ""),
    ("history painters", "cand-10278", [47, 50], ""),
    ("history picture", "cand-10278", [50], ""),
    ("The Hunt of Meleager and Atalanta", "cand-10271", [50], ""),
    ("pittore di macchia", "cand-10272", [49], ""),
    ("soggetti. graziosi e leggeri", "cand-10277", [51], "OCR includes a period after soggetti; print reads ‘soggetti graziosi e leggeri’."),
    ("the pictures that he chose for them", "cand-10273", [53], ""),
    ("Saggio sopra la Pittura", "cand-0074", [180], ""),
    ("Opere, HI, p. 125", "cand-10229", [180], "The printed p.351 image reads Opere, III, p. 125."),
    ("L. Ferrari, 1900", "cand-10275", [181], ""),
    ("pp. 150-4", "cand-10275", [181], ""),
    ("Algarotti’s letter to Mariette", "cand-10274", [181], ""),
    ("Mariette", "cand-1547", [181], ""),
    ("13 February 1751", "cand-10274", [181], ""),
    ("Opere, VW, pp. 15-40", "cand-10229", [181], "The printed p.351 image reads Opere, VIII, pp. 15-40."),
    ("Posse, 1931", "cand-10276", [181], ""),
]:
    add_surface(NOTES if line_numbers[0] >= 168 else BODY, cid, surface, line_numbers, note)

add_pronouns(BODY, "cand-0072", ["he"], [49, 51, 52, 53])
add_pronouns(BODY, "cand-0072", ["His"], [50])
add_pronouns(BODY, "cand-0072", ["his"], [53])
add_pronouns(BODY, "cand-1950", ["his"], [49], "In ‘his compositions’, the possessive refers to Pittoni.")
add_surface(BODY, "cand-0072", "Algarotti", [47, 52])
add_surface(BODY, "cand-0072", "Algarotti’s", [49])
if len(new_mentions) != 67:
    raise SystemExit(f"historical first-pass anchors differ: expected 67, found {len(new_mentions)}")

for mention_id, note in (
    ("m-chp14-p351-0062", "In ‘one of his most attractive characteristics’, ‘his’ refers to Algarotti."),
    ("m-chp14-p351-0063", "In ‘his influence on individual painters’, ‘his’ refers to Algarotti."),
):
    row = next((item for item in new_mentions if item["mention_id"] == mention_id), None)
    if row is None or row["candidate_id"] != "cand-1950":
        raise SystemExit(f"unexpected original mention mapping: {mention_id}")
    row["candidate_id"] = "cand-0072"
    row["note"] = note

for mention_id, surface, start, end, candidate_id, note in [
    ("m-chp14-p351-0068", "he", 1173, 1175, "cand-0072", "In ‘artists he proposes’, ‘he’ refers to Algarotti."),
    ("m-chp14-p351-0069", "his", 1534, 1537, "cand-1827", "In ‘his vedute’, the possessive refers to Pannini."),
    ("m-chp14-p351-0070", "his", 1715, 1718, "cand-0072", "In ‘his foreign travels’, the possessive refers to Algarotti."),
    ("m-chp14-p351-0071", "he", 1838, 1840, "cand-0072", "In ‘he included Boucher’, ‘he’ refers to Algarotti."),
    ("m-chp14-p351-0072", "He", 2095, 2097, "cand-0072", "In ‘He found subjects’, the subject refers to Algarotti."),
    ("m-chp14-p351-0073", "his", 2372, 2375, "cand-0072", "In ‘his detachment from Roman values’, the possessive refers to Algarotti."),
    ("m-chp14-p351-0074", "his", 2679, 2682, "cand-0072", "In ‘his comments’, the possessive refers to Algarotti."),
]:
    if body[start:end] != surface or candidate_id not in candidate_ids:
        raise SystemExit(f"new coreference anchor mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": BODY, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })

known_mention_ids = {row["mention_id"] for row in mentions}
for row in new_mentions:
    if row["mention_id"] in known_mention_ids:
        raise SystemExit(f"duplicate mention ID: {row['mention_id']}")
    text = body if row["segment_id"] == BODY else "\n".join(source_lines[167:220])
    if text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
mentions.extend(new_mentions)

statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statement_rows) + "\n").encode("utf-8")
from io import StringIO
buffer = StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n")
writer.writeheader()
writer.writerows(mentions)
mention_bytes = buffer.getvalue().encode("utf-8")

report = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "p351_statements": {"total": 45, "relation_candidate_true": 28, "relation_candidate_false": 17, "unset": 0},
    "p351_mentions": {"restored_first_pass": 67, "restored_review_additions": 7, "total": 74},
    "statements_before_sha256": STATEMENTS_SHA256,
    "statements_after_sha256": sha(statement_bytes),
    "mentions_before_sha256": MENTIONS_SHA256,
    "mentions_after_sha256": sha(mention_bytes),
    "backups": [statement_path.name + BACKUP_SUFFIX, mention_path.name + BACKUP_SUFFIX],
}
print(json.dumps(report, ensure_ascii=False, indent=2))

if ARGS.apply:
    originals = {statement_path: statement_path.read_bytes(), mention_path: mention_path.read_bytes()}
    for path, data in originals.items():
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if backup.read_bytes() != data:
                raise SystemExit(f"existing recovery copy differs from current source: {backup.name}")
        else:
            shutil.copy2(path, backup)
    try:
        atomic_write(statement_path, statement_bytes)
        atomic_write(mention_path, mention_bytes)
    except Exception:
        for path, data in originals.items():
            path.write_bytes(data)
        raise
