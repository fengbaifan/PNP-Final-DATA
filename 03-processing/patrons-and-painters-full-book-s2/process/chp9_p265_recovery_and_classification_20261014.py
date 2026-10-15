"""Recover the reviewed p.265 mention rows and classify six remaining S2 statements.

Defaults to a read-only preflight. The printed page was checked against
CHP-9.pdf physical page 31. The body mention rows come from the corrected
anchor backup; note mention specifications are read as data from the earlier
notes migration script, which this script never executes.
"""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
LEGACY_NOTES = PROCESS / "chp9_p265_p267_notes_migration.py"
BODY_BACKUP = TABLES / "mentions.csv.bak-s2-chp9-p265-anchor-fix-20261001"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"

BODY = "chp-9:09_CHP-9_intro:l291-301"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SEGMENT_HASHES = {
    BODY: "3820d49b66ee86388bfe238d2257d81f282963238c24fbf01a771e396f41cc83",
    NOTES: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
EXPECTED_HASHES = {
    MENTIONS: "31b280a64a32143e842e941f55176e35b6a3162f1ac16cb6586a5f365ab67b74",
    STATEMENTS: "160239dbcacfb613ae31389db17a37c7979d125dccd453ac20450a34cdbdf3bd",
    COVERAGE: "8d33e6aa839fe65b1bc77fd40d3e65d9f0a0b661a6b392892ae058912684ef23",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SOURCE: "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    BODY_BACKUP: "2e6e7ac0c95f10d0bae0ca7637437b7d29d31c018beb747fe967f3fd0c8a3cf2",
    LEGACY_NOTES: "2fd379fff88b9c2f9b14f5d6d4912593f7d9807f5d6e28540a3e00cb62e164df",
}
BACKUP_SUFFIX = ".bak-s2-chp9-p265-reconciliation-20261014"

CLASSIFICATIONS = {
    "st-chp9-p265-longhi-date-may-mark-completion": False,
    "st-chp9-p265-note1-source-locator": False,
    "st-chp9-p265-note5-vmoschini-citation": False,
    "st-chp9-p265-note6-crespi-works-identified": True,
    "st-chp9-p265-sagredo-collected-until-end-of-life": True,
    "st-chp9-p265-tiepolo-works-recorded-in-1743": True,
}
REASONS = {
    "st-chp9-p265-longhi-date-may-mark-completion": (
        "S2: this is Haskell's interpretation of the 1734 date as a completion date, not a separately "
        "documented commission or completion event."
    ),
    "st-chp9-p265-note1-source-locator": (
        "S2: this is a bibliographic locator for Haskell and Levey, 1958, p.182; neither the publication "
        "nor cited page was independently consulted."
    ),
    "st-chp9-p265-note5-vmoschini-citation": (
        "S2: this is a citation locator for V. Moschini's argument; the cited page was not independently "
        "consulted, and Haskell's commission claim remains tentative."
    ),
    "st-chp9-p265-note6-crespi-works-identified": (
        "S2: the note identifies the two works attributed to Giuseppe Maria Crespi as a Nativity and a Mission; "
        "retain the work-subject candidates while keeping titles, dates, locations and the possible Chicago "
        "match unresolved."
    ),
    "st-chp9-p265-sagredo-collected-until-end-of-life": (
        "S2: Haskell explicitly says Zaccaria continued collecting until the end of his life; no exact final "
        "acquisition or date is inferred."
    ),
    "st-chp9-p265-tiepolo-works-recorded-in-1743": (
        "S2: Haskell says the 1743 record listed an unidentified Tiepolo ceiling and several drawings; "
        "preserve the inventory relationship while keeping the record and individual works unresolved."
    ),
}
EXPECTED_GLOBAL_BEFORE = {True: 9669, False: 3995, None: 1165}


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
for sid, expected in SEGMENT_HASHES.items():
    if sid not in segments or segments[sid]["sha256"] != expected:
        raise SystemExit(f"unexpected source segment: {sid}")
    if segments[sid]["asset_sha256"] != EXPECTED_HASHES[SOURCE]:
        raise SystemExit(f"unexpected source asset reference: {sid}")

legacy_tree = ast.parse(LEGACY_NOTES.read_text(encoding="utf-8-sig"))
legacy_values = {}
for node in legacy_tree.body:
    if isinstance(node, ast.Assign):
        names = {target.id for target in node.targets if isinstance(target, ast.Name)}
        if "EXPECTED_MAX_CANDIDATE" in names:
            expected_max_candidate = ast.literal_eval(node.value)
        elif "CANDIDATE_SPECS" in names:
            candidate_specs = ast.literal_eval(node.value)
        elif "EXISTING" in names:
            existing_candidate_map = ast.literal_eval(node.value)
if expected_max_candidate != 8637 or len(candidate_specs) != 27:
    raise SystemExit("legacy p.265 notes candidate specification changed")
candidate_by_key = {
    spec[0]: f"cand-{expected_max_candidate + i:04d}"
    for i, spec in enumerate(candidate_specs, 1)
}


def resolve_candidate(node):
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        key = ast.literal_eval(node.slice)
        if node.value.id == "candidate_by_key":
            return candidate_by_key[key]
        if node.value.id == "EXISTING":
            return existing_candidate_map[key]
    return ast.literal_eval(node)


note_specs = []
for node in ast.walk(legacy_tree):
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "add_mention":
        continue
    args = node.args
    if len(args) < 5 or not isinstance(args[0], ast.Constant) or not isinstance(args[1], ast.Constant):
        continue
    mention_id, line_no = args[0].value, args[1].value
    if not (mention_id.startswith("m-chp9-p265n") and line_no in {429, 430, 431, 432}):
        continue
    note_specs.append((
        mention_id,
        line_no,
        resolve_candidate(args[2]),
        ast.literal_eval(args[3]),
        ast.literal_eval(args[4]),
    ))
if len(note_specs) != 17:
    raise SystemExit(f"expected 17 p.265 consolidated-note mentions, found {len(note_specs)}")

_, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()

_, body_backup_rows = read_csv(BODY_BACKUP)
body_mentions = [
    row for row in body_backup_rows
    if row["segment_id"] == BODY and row["mention_id"].startswith("m-chp9-p265-")
]
if len(body_mentions) != 45 or len({row["mention_id"] for row in body_mentions}) != 45:
    raise SystemExit(f"expected 45 unique corrected p.265 body mentions, found {len(body_mentions)}")

new_mentions = list(body_mentions)
for mention_id, line_no, candidate_id, surface, note in note_specs:
    line_text = source_lines[line_no - 1]
    pos = line_text.find(surface)
    if pos < 0:
        raise SystemExit(f"source text does not contain p.265 note mention {mention_id}: {surface!r}")
    meta = segments[NOTES]
    segment_offset = sum(len(source_lines[n - 1]) + 1 for n in range(meta["line_start"], line_no))
    start, end = segment_offset + pos, segment_offset + pos + len(surface)
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

existing_ids = {row["mention_id"] for row in current_mentions}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in current_mentions}
new_ids = set()
new_spans = set()
for row in new_mentions:
    if row["mention_id"] in existing_ids or row["mention_id"] in new_ids:
        raise SystemExit(f"duplicate mention id: {row['mention_id']}")
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"unknown candidate for mention: {row['mention_id']} -> {row['candidate_id']}")
    span = (row["segment_id"], row["start_char"], row["end_char"])
    if span in existing_spans or span in new_spans:
        raise SystemExit(f"duplicate mention span: {row['mention_id']}")
    meta = segments[row["segment_id"]]
    text = "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])
    if text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"source-span mismatch: {row['mention_id']}")
    new_ids.add(row["mention_id"])
    new_spans.add(span)

unset_ids = {
    row["statement_id"] for row in statement_rows
    if row["statement_id"].startswith("st-chp9-p265-")
    and row.get("qualifiers", {}).get("printed_page") == 265
    and row.get("qualifiers", {}).get("relation_candidate") is None
}
if unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.265 unset classifications: {sorted(unset_ids)}")
if set(CLASSIFICATIONS) != set(REASONS):
    raise SystemExit("classification reasons do not match the decision set")
for statement_id, value in CLASSIFICATIONS.items():
    qualifiers = statement_by_id[statement_id]["qualifiers"]
    if qualifiers.get("relation_candidate") is not None:
        raise SystemExit(f"statement is no longer unset: {statement_id}")
    qualifiers["relation_candidate"] = value
    reason = REASONS[statement_id]
    qualification = qualifiers.get("qualification", "").strip()
    if reason not in qualification:
        qualifiers["qualification"] = (qualification + " " + reason).strip()

before = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in read_jsonl(STATEMENTS))
after = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in statement_rows)
if dict(before) != EXPECTED_GLOBAL_BEFORE:
    raise SystemExit(f"unexpected global classification baseline: {dict(before)}")
if after[True] != before[True] + 3 or after[False] != before[False] + 3 or after[None] != before[None] - 6:
    raise SystemExit(f"unexpected classification delta: before={dict(before)}, after={dict(after)}")

for sid in (BODY, NOTES):
    if sid not in coverage_by_id or coverage_by_id[sid]["migration_status"] != "complete":
        raise SystemExit(f"unexpected S2 coverage state for {sid}")
coverage_by_id[BODY]["note"] += (
    " 2026-10-14 reconciliation restored 45 p.265 body and continuation mentions from the corrected anchor backup "
    "after exact source-span validation; six previously unset relation_candidate fields were reviewed (3 true, 3 false)."
)
coverage_by_id[NOTES]["note"] += (
    " 2026-10-14 reconciliation restored 17 p.265 consolidated-note mentions at L429-432 after exact source-span validation."
)

summary = {
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "printed_page": 265,
    "pdf_physical_page": 31,
    "recovered_mentions": len(new_mentions),
    "mention_distribution": dict(Counter(row["segment_id"] for row in new_mentions)),
    "note_line_distribution": dict(Counter(str(item[1]) for item in note_specs)),
    "classified_statements": {"true": 3, "false": 3, "unset_closed": 6},
    "global_statements": len(statement_rows),
    "global_classifications_after": {"true": after[True], "false": after[False], "unset": after[None]},
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write verified p.265 mention and classification updates")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, STATEMENTS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more p.265 reconciliation backups already exist")
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
