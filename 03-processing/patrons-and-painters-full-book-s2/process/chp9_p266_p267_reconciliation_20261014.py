"""Restore omitted p.266-p.267 mentions and close reviewed S2 classifications.

The body mention specifications are recovered from the dated p.266-p.267
migration backup. Consolidated-note specifications are read as data from the
legacy migration script; that script is parsed but never executed here.
Defaults to a read-only, hash-pinned preflight.
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
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BODY_BACKUP = TABLES / "mentions.csv.bak-s2-chp9-notes-p265-p267-20261001"
LEGACY_NOTES = PROCESS / "chp9_p265_p267_notes_migration.py"

BODY_266 = "chp-9:09_CHP-9_intro:l303-311"
BODY_267 = "chp-9:09_CHP-9_intro:l313-321"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SEGMENT_HASHES = {
    BODY_266: "6153ee105244f9e9bf25cd7cfbffef26cd195c6648061760e56bd83c9de98270",
    BODY_267: "3b6bb69ba75dac969f2059036fd7dd45a1a67b771e41ba507f85bd982dc70080",
    NOTES: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
EXPECTED_HASHES = {
    MENTIONS: "126cab66191b4d7693bac5df960ef4a4f22cb7f03ff773dea6004c0cf4a90ac8",
    STATEMENTS: "2629059b7fcc4ef77f097caf78980249e16606b4192d65c71618b52e1c755ac2",
    COVERAGE: "5a4e1dafff6c04bdacbeceb3782ed2617f2291c9e5f3eaf3d0e093a7e4c960d6",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    BODY_BACKUP: "720b174688c078c534de300619979fffaddfa367473abe4d02b09ac24bd77f8a",
    LEGACY_NOTES: "2fd379fff88b9c2f9b14f5d6d4912593f7d9807f5d6e28540a3e00cb62e164df",
}
BACKUP_SUFFIX = ".bak-s2-chp9-p266-p267-reconciliation-20261014"

CLASSIFICATIONS = {
    "st-chp9-p266-attributed-artists-in-volumes": True,
    "st-chp9-p266-breval-assessment": False,
    "st-chp9-p266-note1-breval-crossreference": False,
    "st-chp9-p266-note2-moschini-source": False,
    "st-chp9-p266-note3-dacanal-fontana-citations": False,
    "st-chp9-p266-note4-smith-will-citation": False,
    "st-chp9-p266-note5-popham-wilde-citation": False,
    "st-chp9-p266-note7-blunt-citation": False,
    "st-chp9-p266-note8-chapter-reference": False,
    "st-chp9-p266-original-pieces-and-attention": True,
    "st-chp9-p266-reputation-and-collection": True,
    "st-chp9-p267-ferdinando-death-in-padua": True,
    "st-chp9-p267-imagined-image-of-sagredo": False,
    "st-chp9-p267-mantua-pictures-entered-venetian-market": True,
    "st-chp9-p267-note1-chapter-reference": False,
    "st-chp9-p267-note2-smith-will-citation": False,
    "st-chp9-p267-note3-fochessati-citation": False,
    "st-chp9-p267-note4-malamani-citation": False,
    "st-chp9-p267-note5-blunt-citation": False,
    "st-chp9-p267-posthumous-castiglione-reception": True,
    "st-chp9-p267-sagredo-importance-in-taste": False,
    "st-chp9-p267-seller-of-drawings-unknown": False,
}
REASONS = {
    "st-chp9-p266-attributed-artists-in-volumes": (
        "S2: Haskell reports works attributed to named artists within the drawing volumes; preserve "
        "the attribution relation while keeping individual sheets and authorship unverified."
    ),
    "st-chp9-p266-breval-assessment": (
        "S2: this nested quotation records Breval's judgment about Sagredo's reputation, not a specific "
        "entity-to-entity relation suitable for S6."
    ),
    "st-chp9-p266-note1-breval-crossreference": (
        "S2: this is an internal note cross-reference only; it adds no independent evidence or relation."
    ),
    "st-chp9-p266-note2-moschini-source": (
        "S2: this is a bibliographic citation locator; the cited page was not independently consulted."
    ),
    "st-chp9-p266-note3-dacanal-fontana-citations": (
        "S2: this is a pair of short-form citation locators; neither cited page was independently consulted."
    ),
    "st-chp9-p266-note4-smith-will-citation": (
        "S2: this is a citation to the published will, not an independently checked source claim or formal relation."
    ),
    "st-chp9-p266-note5-popham-wilde-citation": (
        "S2: this is a bibliographic locator for Popham and Wilde; the cited page was not independently consulted."
    ),
    "st-chp9-p266-note7-blunt-citation": (
        "S2: this is a bibliographic locator for Blunt; the cited page was not independently consulted."
    ),
    "st-chp9-p266-note8-chapter-reference": (
        "S2: this is an internal chapter pointer only; it does not assert a new entity relation."
    ),
    "st-chp9-p266-original-pieces-and-attention": (
        "S2: Haskell reports that the purchased group included original works and attracted contemporary "
        "connoisseur attention; retain these acquisition and reception claims without identifying sheets."
    ),
    "st-chp9-p266-reputation-and-collection": (
        "S2: the passage explicitly states that Sagredo collected prints and drawings; retain this "
        "collector-to-medium relation while treating the surrounding reputation language as Haskell's evaluation."
    ),
    "st-chp9-p267-ferdinando-death-in-padua": (
        "S2: Haskell reports Ferdinando Carlo's death at Padua and age; retain the person-event-place "
        "claim with the quoted characterization attributed to Haskell."
    ),
    "st-chp9-p267-imagined-image-of-sagredo": (
        "S2: this is Haskell's explicitly imagined reading of Sagredo's character, not a documented event or relation."
    ),
    "st-chp9-p267-mantua-pictures-entered-venetian-market": (
        "S2: Haskell explicitly reports Mantuan pictures appearing on the Venetian market; keep the "
        "market movement claim distinct from any unverified individual sale."
    ),
    "st-chp9-p267-note1-chapter-reference": (
        "S2: this is an internal chapter pointer only; it adds no independent evidence or relation."
    ),
    "st-chp9-p267-note2-smith-will-citation": (
        "S2: this is a citation locator for the published will; neither the will nor cited page was independently consulted."
    ),
    "st-chp9-p267-note3-fochessati-citation": (
        "S2: this is a short-form bibliographic locator; the cited page was not independently consulted."
    ),
    "st-chp9-p267-note4-malamani-citation": (
        "S2: this is a bibliographic locator plus an internal chapter pointer; the cited page was not independently consulted."
    ),
    "st-chp9-p267-note5-blunt-citation": (
        "S2: this is a bibliographic locator for Blunt; the cited page was not independently consulted."
    ),
    "st-chp9-p267-posthumous-castiglione-reception": (
        "S2: Haskell explicitly describes the time-bound reception of Castiglione's prints and drawings; "
        "preserve the reception claim without making it an absolute statement about every earlier viewer."
    ),
    "st-chp9-p267-sagredo-importance-in-taste": (
        "S2: this is Haskell's evaluative judgment of Sagredo's historical significance, not a discrete "
        "entity relation or independently measured rank."
    ),
    "st-chp9-p267-seller-of-drawings-unknown": (
        "S2: this records an explicitly unresolved seller identity, not a positive relation; retain the "
        "provenance hypothesis in its separate qualified statement."
    ),
}
EXPECTED_GLOBAL_BEFORE = {True: 9672, False: 3998, None: 1159}


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
    raise SystemExit("legacy note candidate specification changed")
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
    is_target = (
        (mention_id.startswith("m-chp9-p266n") and line_no in {433, 434, 435, 436, 437, 438, 439, 440})
        or (mention_id.startswith("m-chp9-p267n") and line_no in {441, 442, 443, 444, 445})
    )
    if not is_target:
        continue
    note_specs.append((mention_id, line_no, resolve_candidate(args[2]), ast.literal_eval(args[3]), ast.literal_eval(args[4])))
if len(note_specs) != 27:
    raise SystemExit(f"expected 27 consolidated-note mentions for p.266-p.267, found {len(note_specs)}")

_, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()

_, body_backup_rows = read_csv(BODY_BACKUP)
body_specs = []
for printed_page, segment_id in ((266, BODY_266), (267, BODY_267)):
    part = [
        row for row in body_backup_rows
        if row["segment_id"] == segment_id and row["mention_id"].startswith(f"m-chp9-p{printed_page}-")
    ]
    expected = 40 if printed_page == 266 else 31
    if len(part) != expected or len({row["mention_id"] for row in part}) != expected:
        raise SystemExit(f"p.{printed_page}: expected {expected} unique body mentions, found {len(part)}")
    body_specs.extend(part)

new_mentions = list(body_specs)
for mention_id, line_no, candidate_id, surface, note in note_specs:
    line_text = source_lines[line_no - 1]
    pos = line_text.find(surface)
    if pos < 0:
        raise SystemExit(f"source text does not contain note mention {mention_id}: {surface!r}")
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
new_ids, new_spans = set(), set()
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
    if row["statement_id"].startswith(("st-chp9-p266-", "st-chp9-p267-"))
    and row.get("qualifiers", {}).get("printed_page") in {266, 267}
    and row.get("qualifiers", {}).get("relation_candidate") is None
}
if unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.266-p.267 unset classifications: {sorted(unset_ids)}")
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
if after[True] != before[True] + 6 or after[False] != before[False] + 16 or after[None] != before[None] - 22:
    raise SystemExit(f"unexpected classification delta: before={dict(before)}, after={dict(after)}")

for sid in (BODY_266, BODY_267, NOTES):
    if sid not in coverage_by_id or coverage_by_id[sid]["migration_status"] != "complete":
        raise SystemExit(f"unexpected S2 coverage state for {sid}")
coverage_by_id[BODY_266]["note"] += (
    " 2026-10-14 reconciliation restored 40 omitted p.266 body mentions from the dated migration backup "
    "after exact source-span validation; 11 unset statements were reviewed (3 true, 8 false)."
)
coverage_by_id[BODY_267]["note"] += (
    " 2026-10-14 reconciliation restored 31 omitted p.267 body mentions from the dated migration backup "
    "after exact source-span validation; 11 unset statements were reviewed (3 true, 8 false)."
)
coverage_by_id[NOTES]["note"] += (
    " 2026-10-14 reconciliation restored 27 p.266-p.267 consolidated-note mentions at L433-445 "
    "after exact source-span validation."
)

summary = {
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "printed_pages": [266, 267],
    "pdf_physical_pages": [32, 33],
    "recovered_mentions": len(new_mentions),
    "mention_distribution": dict(Counter(row["segment_id"] for row in new_mentions)),
    "note_line_distribution": dict(Counter(str(item[1]) for item in note_specs)),
    "classified_statements": {"true": 6, "false": 16, "unset_closed": 22},
    "global_statements": len(statement_rows),
    "global_classifications_after": {"true": after[True], "false": after[False], "unset": after[None]},
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write verified p.266-p.267 mention and classification updates")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, STATEMENTS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more p.266-p.267 reconciliation backups already exist")
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
