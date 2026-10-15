"""Restore p.269 S2 mentions and classify its open claims against the scan."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BODY_BACKUP = TABLES / "mentions.csv.bak-s2-chp9-notes-p268-p275-20261002"
NOTE_SPEC = PROCESS / "chp9_p268_p275_notes_migration.py"
PAGE_SCAN = PROCESS / "p269_page_review_20261014.png"
BODY_SEGMENT = "chp-9:09_CHP-9_sec_ii:l18-25"
NOTES_SEGMENT = "chp-9:09_CHP-9_sec_ii:l85-127"

EXPECTED_HASHES = {
    MENTIONS: "a201fc75c0afc1412d760d1b930f00a8715d0f6eb42cf60582484d950ad2f0f8",
    STATEMENTS: "3d2209d8c3576b7d923dff69c91313aed620bcbb530837514675377ea7788457",
    COVERAGE: "2d58708c6208b124e115352e4984c6ff1674eeb43ed0974a6e044c7139a74070",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    BODY_BACKUP: "d9a81391d871228faba35176e19eab145ab85733f88b556881365864e059c32e",
    NOTE_SPEC: "8c02184e04b490be86791aca891241bd1d77e1d466374ea34b6bff4a477ab3b3",
    PAGE_SCAN: "1daeedb85eb48b422e836e072473c130272ecf671432876a5e92eda45dd6eda0",
}
SEGMENT_HASHES = {
    BODY_SEGMENT: "908c9e9ac8a5a25f91200eec9d2680beb6b8345dceb66b88392c96b51bd7530d",
    NOTES_SEGMENT: "d00ced6fff3f96f5cf574f47f45eea80ef1b6867c581d7d017f217ee2a8a5a99",
}
BACKUP_SUFFIX = ".bak-s2-chp9-p269-reconciliation-20261014"

CLASSIFICATIONS = {
    "st-chp9-p269-1743-observer-complaint-continuation": True,
    "st-chp9-p269-benefactions-and-public-alms": True,
    "st-chp9-p269-cavazza-admission-patriciate": True,
    "st-chp9-p269-frontage-praise": False,
    "st-chp9-p269-n01": False,
    "st-chp9-p269-n01-stazio-will-no-commissioner": False,
    "st-chp9-p269-n02": False,
    "st-chp9-p269-n03": False,
    "st-chp9-p269-n04": False,
    "st-chp9-p269-n05": True,
    "st-chp9-p269-pamphlet-taste-objection": False,
    "st-chp9-p269-pamphleteer-monastery-finances": True,
    "st-chp9-p269-pamphleteer-poor-relief-argument": False,
    "st-chp9-p269-pamphleteer-poverty-spirit": False,
    "st-chp9-p269-pamphleteer-worship-priority": False,
    "st-chp9-p269-parish-rebuilds-rebuttal": True,
    "st-chp9-p269-scalzi-arrival-1633": True,
    "st-chp9-p269-scalzi-luxury-pamphlet": True,
}
REASONS = {
    "st-chp9-p269-1743-observer-complaint-continuation": "S2: the attributed continuation explicitly contrasts church-building resources of religious orders with parish support and delays; preserve its group-level scope and Zanetti attribution.",
    "st-chp9-p269-benefactions-and-public-alms": "S2: Haskell reports public alms continuing to support the monks despite the church's luxury; retain the broad collective actors and author's wording.",
    "st-chp9-p269-cavazza-admission-patriciate": "S2: a named person is linked to admission to the Venetian patriciate in 1653; keep the event and date distinct from the separate façade payment.",
    "st-chp9-p269-frontage-praise": "S2: this is an attributed, qualified evaluative description of the façade, not a formal relation between independently identified entities.",
    "st-chp9-p269-n01": "S2: citation locator only; it does not itself assert the later S. Stae facts recorded in separate note statements.",
    "st-chp9-p269-n01-stazio-will-no-commissioner": "S2: this records a limit of the cited will and names no commissioner; do not infer a commissioning relation from absence of information.",
    "st-chp9-p269-n02": "S2: bibliographic citation locator only; the cited publication is not independently consulted here.",
    "st-chp9-p269-n03": "S2: bibliographic citation locator only; the cited publication is not independently consulted here.",
    "st-chp9-p269-n04": "S2: bibliographic citation locator only; the cited publication is not independently consulted here.",
    "st-chp9-p269-n05": "S2: the note supplies explicit publication and repository information for the pamphlet, supporting published_by/held_by candidates. Luigi Pavini is named as publisher but has no current entity-candidate row; retain that endpoint as unresolved for S1/S3 and do not finalize a relation.",
    "st-chp9-p269-pamphlet-taste-objection": "S2: this is Haskell's characterization of the anonymous pamphleteer's argument, without a concrete historical relation to encode.",
    "st-chp9-p269-pamphleteer-monastery-finances": "S2: the pamphlet explicitly denies a concrete claim that monastery resources were used for church decoration and reports its finances; preserve the denial and speaker as a disputed relation candidate, not an established fact.",
    "st-chp9-p269-pamphleteer-poor-relief-argument": "S2: this is a normative argument comparing worship and poverty relief, not a formal relation among the invoked religious figures and places.",
    "st-chp9-p269-pamphleteer-poverty-spirit": "S2: the pamphleteer's attributed theological and architectural defense is interpretive; it does not establish a formal relation between the Order and a specific work.",
    "st-chp9-p269-pamphleteer-worship-priority": "S2: this is a normative claim about worship and care for the poor, not a formal entity relation.",
    "st-chp9-p269-parish-rebuilds-rebuttal": "S2: Haskell names S. Toma and S. Vitale as parish churches that were either rebuilt or richly decorated; retain the alternative wording rather than assigning one action to each building.",
    "st-chp9-p269-scalzi-arrival-1633": "S2: the text gives a dated arrival event for the Scalzi in Venice and identifies the group's Carmelite affiliation; preserve both scope and date.",
    "st-chp9-p269-scalzi-luxury-pamphlet": "S2: the text links the Scalzi church expense, the austere Order and a 1732 call for a pamphleteer to justify it; keep the event and attribution without treating the defense as proof.",
}
EXPECTED_GLOBAL_BEFORE = {True: 9688, False: 4028, None: 1113}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(f.name)
    temp_path.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(f.name)
    temp_path.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"fingerprint changed; inspect before continuing: {path.relative_to(ROOT)}")

segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
for segment_id, expected in SEGMENT_HASHES.items():
    meta = segments.get(segment_id)
    if meta is None or meta["sha256"] != expected or meta["asset_sha256"] != EXPECTED_HASHES[SOURCE]:
        raise SystemExit(f"unexpected reviewed source segment: {segment_id}")

candidate_fields, candidate_rows = read_csv(CANDIDATES)
candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
candidate_ids = set(candidate_by_id)
mention_fields, current_mentions = read_csv(MENTIONS)
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
current_mention_ids = {row["mention_id"] for row in current_mentions}
if len(current_mention_ids) != len(current_mentions):
    raise SystemExit("duplicate mention IDs already exist")

_, backup_rows = read_csv(BODY_BACKUP)
new_mentions = [row.copy() for row in backup_rows if row["segment_id"] == BODY_SEGMENT]
if len(new_mentions) != 40 or len({row["mention_id"] for row in new_mentions}) != 40:
    raise SystemExit(f"expected 40 unique p.269 body mentions, found {len(new_mentions)}")
if any(row["mention_id"] in current_mention_ids for row in new_mentions):
    raise SystemExit("one or more p.269 body mentions are already present")

# Read only literal migration specs from the hash-pinned historical script; never execute it.
tree = ast.parse(NOTE_SPEC.read_text(encoding="utf-8-sig"))
assignments = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        assignments[node.targets[0].id] = node.value

def literal(name):
    if name not in assignments:
        raise SystemExit(f"missing literal in legacy note spec: {name}")
    return ast.literal_eval(assignments[name])


max_candidate = literal("MAX_CANDIDATE")
candidate_specs = literal("CANDIDATE_SPECS")
existing_candidates = literal("EXISTING")
segment_constants = {name: literal(name) for name in ("NOTES", "P270", "P271", "P272", "P273", "P275")}
candidate_key_to_id = {
    row[0]: f"cand-{max_candidate + offset:04d}"
    for offset, row in enumerate(candidate_specs, start=1)
}

def candidate_for_key(key):
    if key in candidate_key_to_id:
        return candidate_key_to_id[key]
    if key in existing_candidates:
        return existing_candidates[key]
    raise SystemExit(f"no pinned candidate mapping for note key: {key}")


note_rows = []
for key, _name, _kind, detail, line_no, surface in candidate_specs:
    if line_no not in {91, 92, 93, 94, 95}:
        continue
    segment_id = NOTES_SEGMENT
    note_rows.append((f"m-chp9-notes-{key}", candidate_for_key(key), line_no, surface, detail))

extra_mentions_node = assignments.get("EXTRA_MENTIONS")
if extra_mentions_node is None or not isinstance(extra_mentions_node, ast.List):
    raise SystemExit("unexpected EXTRA_MENTIONS format in pinned note spec")
for index, item in enumerate(extra_mentions_node.elts, start=1):
    if not isinstance(item, ast.Tuple) or len(item.elts) < 5:
        raise SystemExit(f"unexpected extra-mention spec at index {index}")
    parts = []
    for part in item.elts:
        if isinstance(part, ast.Name):
            if part.id not in segment_constants:
                raise SystemExit(f"unexpected segment constant in extra mention: {part.id}")
            parts.append(segment_constants[part.id])
        else:
            parts.append(ast.literal_eval(part))
    segment_id, line_no, key, surface, note = parts[:5]
    if segment_id == NOTES_SEGMENT and line_no in {91, 92, 93, 94, 95}:
        note_rows.append((f"m-chp9-note-extra-{index:03d}", candidate_for_key(key), line_no, surface, note))

# The prior migration spec omitted these explicit source mentions. Reuse the extant
# candidates for the donor, testator, Ferrari publication, repository, order and city.
note_rows.extend([
    ("m-chp9-p269-n01-alvise-mocenigo", "cand-1673", 91, "Doge Alvise Mocenigo", "Named donor whose legacy funded the S. Stae façade."),
    ("m-chp9-p269-n01-andrea-stazio", "cand-2508", 91, "Andrea Stazio", "Named testator who left nearly 200 ducats for S. Stae building and decoration."),
    ("m-chp9-p269-n02-ferrari", "cand-8777", 92, "L. Ferrari", "Repeated citation to the same 1882 publication cited in p.268 note 5."),
    ("m-chp9-p269-n05-ferrari", "cand-8777", 95, "Ferrari, 1882", "Repeated citation to the same 1882 publication cited in p.268 note 5."),
    ("m-chp9-p269-n05-marciana", "cand-9448", 95, "Marciana", "Repository named for the pamphlet; candidate identity remains open for S3."),
    ("m-chp9-p269-n05-scalzi", "cand-2389", 95, "Carmelitani Scalzi", "Religious order named in the pamphlet title."),
    ("m-chp9-p269-n05-venezia", "cand-2719", 95, "Venezia", "Venice named as the pamphlet's publication context; reuse the place candidate."),
])

def segment_text(segment_id):
    meta = segments[segment_id]
    return "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])


def line_offset(segment_id, line_no):
    meta = segments[segment_id]
    if not meta["line_start"] <= line_no <= meta["line_end"]:
        raise SystemExit(f"line {line_no} is outside {segment_id}")
    return sum(len(source_lines[n - 1]) + 1 for n in range(meta["line_start"], line_no))


notes_text = segment_text(NOTES_SEGMENT)
for mention_id, candidate_id, line_no, surface, note in note_rows:
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown p.269 note candidate: {mention_id} -> {candidate_id}")
    line = source_lines[line_no - 1]
    positions, cursor = [], 0
    while True:
        pos = line.find(surface, cursor)
        if pos < 0:
            break
        positions.append(pos)
        cursor = pos + 1
    if len(positions) != 1:
        raise SystemExit(f"p.269 note surface missing or ambiguous on L{line_no}: {surface!r} ({positions})")
    start = line_offset(NOTES_SEGMENT, line_no) + positions[0]
    end = start + len(surface)
    if notes_text[start:end] != surface:
        raise SystemExit(f"invalid p.269 note source span: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": NOTES_SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

unmapped_publisher = source_lines[94].find("Luigi Pavini")
if unmapped_publisher < 0:
    raise SystemExit("expected named publisher Luigi Pavini is absent from p.269 note 5 source text")
if any(row["canonical_name"].strip().casefold() == "luigi pavini" for row in candidate_rows):
    raise SystemExit("publisher candidate identity changed; re-review endpoint mapping")

existing_spans = {(r["segment_id"], int(r["start_char"]), int(r["end_char"])) for r in current_mentions}
new_ids, new_spans = set(), set()
all_spans = {}
for row in current_mentions:
    all_spans.setdefault(row["segment_id"], []).append((int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
for row in new_mentions:
    if row["mention_id"] in current_mention_ids or row["mention_id"] in new_ids:
        raise SystemExit(f"duplicate mention ID: {row['mention_id']}")
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"unknown candidate: {row['mention_id']} -> {row['candidate_id']}")
    start, end = int(row["start_char"]), int(row["end_char"])
    span = (row["segment_id"], start, end)
    if span in existing_spans or span in new_spans:
        raise SystemExit(f"duplicate exact mention span: {row['mention_id']}")
    if segment_text(row["segment_id"])[start:end] != row["surface_form"]:
        raise SystemExit(f"source-span mismatch: {row['mention_id']}")
    for other_start, other_end, other_id in all_spans.get(row["segment_id"], []):
        if max(start, other_start) < min(end, other_end):
            nested = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if not nested:
                raise SystemExit(f"crossing mention spans: {row['mention_id']} vs {other_id}")
    all_spans.setdefault(row["segment_id"], []).append((start, end, row["mention_id"]))
    new_ids.add(row["mention_id"])
    new_spans.add(span)

p269_unset = {
    row["statement_id"] for row in statement_rows
    if row["statement_id"].startswith("st-chp9-p269-")
    and row.get("qualifiers", {}).get("relation_candidate") is None
}
if p269_unset != set(CLASSIFICATIONS) or set(CLASSIFICATIONS) != set(REASONS):
    raise SystemExit(f"unexpected p.269 unset statements: {sorted(p269_unset)}")
for statement_id, value in CLASSIFICATIONS.items():
    row = statement_by_id[statement_id]
    qualifiers = row["qualifiers"]
    if qualifiers.get("relation_candidate") is not None:
        raise SystemExit(f"statement is no longer unset: {statement_id}")
    qualifiers["relation_candidate"] = value
    qualification = qualifiers.get("qualification", "").strip()
    reason = REASONS[statement_id]
    if reason not in qualification:
        qualifiers["qualification"] = (qualification + " " + reason).strip()
    if statement_id == "st-chp9-p269-n05":
        refs = qualifiers.setdefault("mentioned_candidate_ids", [])
        for candidate_id in ("cand-9448", "cand-2389", "cand-2719"):
            if candidate_id not in refs:
                refs.append(candidate_id)

before = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in read_jsonl(STATEMENTS))
after = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in statement_rows)
if dict(before) != EXPECTED_GLOBAL_BEFORE:
    raise SystemExit(f"unexpected global classification baseline: {dict(before)}")
if after[True] != before[True] + 8 or after[False] != before[False] + 10 or after[None] != before[None] - 18:
    raise SystemExit(f"unexpected classification delta: before={dict(before)}, after={dict(after)}")

body_coverage = coverage_by_id.get(BODY_SEGMENT)
notes_coverage = coverage_by_id.get(NOTES_SEGMENT)
if body_coverage is None or body_coverage["migration_status"] != "complete":
    raise SystemExit(f"unexpected p.269 body coverage: {body_coverage}")
if notes_coverage is None or notes_coverage["migration_status"] != "partial":
    raise SystemExit(f"unexpected consolidated note coverage: {notes_coverage}")
body_coverage["note"] += (
    " 2026-10-14 reconciliation restored 40 omitted p.269 body mentions from the hash-pinned migration backup; "
    "source spans, candidate IDs and overlap boundaries were checked. Classified 18 open p.269 statements: "
    "8 relation candidates and 10 non-relational claims/source locators."
)
notes_coverage["note"] += (
    " 2026-10-14 p.269 note mentions restored from the hash-pinned literal migration spec plus seven source-checked "
    "entity mentions omitted by that spec. Luigi Pavini is explicitly named as publisher but has no separate candidate; "
    "preserve as an unresolved S1/S3 endpoint. The consolidated p.268-275 notes remain partial pending p.270-275."
)

summary = {
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "printed_page": 269,
    "pdf_physical_page": 35,
    "recovered_mentions": len(new_mentions),
    "recovered_body_mentions": 40,
    "recovered_note_mentions": len(note_rows),
    "unmapped_named_endpoints": [{"name": "Luigi Pavini", "role": "publisher", "source_line": 95}],
    "classified_statements": {"true": 8, "false": 10, "unset_closed": 18},
    "global_mentions_after": len(current_mentions) + len(new_mentions),
    "global_statements": len(statement_rows),
    "global_classifications_after": {"true": after[True], "false": after[False], "unset": after[None]},
    "notes_segment_status_after": notes_coverage["migration_status"],
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the verified p.269 S2 reconciliation")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, STATEMENTS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more p.269 reconciliation backups already exist")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    try:
        write_csv(MENTIONS, mention_fields, current_mentions + new_mentions)
        write_jsonl(STATEMENTS, statement_rows)
        write_csv(COVERAGE, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; recovery backups: " + ", ".join(path.name for path in backups))
