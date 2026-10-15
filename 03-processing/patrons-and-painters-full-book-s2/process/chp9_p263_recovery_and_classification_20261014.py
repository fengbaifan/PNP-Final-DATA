"""Reconcile missing p.263 mentions and unset S2 relation-candidate decisions.

Defaults to a read-only preflight. The printed p.263 page and its notes were
reviewed against CHP-9.pdf physical page 25. Mention specifications are read
as data from the earlier, non-executed p.263-p.264 migration script; this
script never imports or executes that broader migration.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
LEGACY_SPEC = PROCESS / "chp9_p263_p264_migration.py"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"

P263 = "chp-9:09_CHP-9_intro:l231-238"
P264 = "chp-9:09_CHP-9_intro:l240-249"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SEGMENT_HASHES = {
    P263: "403d813c6d986e4009cf2beb125153ce96b8b605547380e83dd806954d14dd56",
    NOTES: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
EXPECTED_HASHES = {
    MENTIONS: "6a50be3ab6c35d345d3355f9a32e4618fe0085910d788ba6bfc7ec33cff3b2e7",
    STATEMENTS: "61303c8d4a9f1c47e7efe7f62b5a755de41706ea6e981c7c8d6ceed8ee062780",
    COVERAGE: "d7f06f7c6678a9c595f12858968ccfaa2332a0cb288357d054f55b0dada46905",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SOURCE: "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    LEGACY_SPEC: "f917d572ed0ffbbc026d9f7f580d8ef64e023592b8a4e6a1522c6eecc3442eab",
}
BACKUP_SUFFIX = ".bak-s2-chp9-p263-reconciliation-20261014"

CLASSIFICATIONS = {
    "st-chp9-p263264-breval-dilettante": False,
    "st-chp9-p263264-breval-patron-reputation": False,
    "st-chp9-p263264-da-canal-meschini-praise": False,
    "st-chp9-p263264-gradenigo-1710-art-collection": True,
    "st-chp9-p263264-keysler-gallery-report": True,
    "st-chp9-p263264-sagredo-patron-collector": False,
    "st-chp9-p263264-sagredo-temperament": False,
    "st-chp9-p263264-will-archival-locator": True,
    "st-chp9-p263264-wright-anecdote-locator": False,
}
REASONS = {
    "st-chp9-p263264-breval-dilettante": (
        "S2: the footnote supplies a citation and nested quotation already captured in the body claim; "
        "it adds no separate historical relation."
    ),
    "st-chp9-p263264-breval-patron-reputation": (
        "S2: this reports a contemporary reputation and a visitor's impression, not a discrete patronage "
        "or ownership event; preserve it as attributed reception content."
    ),
    "st-chp9-p263264-da-canal-meschini-praise": (
        "S2: these are retrospective rankings and characterizations relayed by Haskell, not directed "
        "historical relations."
    ),
    "st-chp9-p263264-gradenigo-1710-art-collection": (
        "S2: the cited manuscript reports Sagredo's acquisition of prints and drawings by 1710; retain "
        "the attributed collecting claim, while leaving individual works and the generic object endpoint "
        "unresolved for S6."
    ),
    "st-chp9-p263264-keysler-gallery-report": (
        "S2: retain Keysler's attributed report about the Sagredo gallery's contents as a relation candidate, "
        "with the qualification that he could not enter and the cited account was not independently consulted."
    ),
    "st-chp9-p263264-sagredo-patron-collector": (
        "S2: this is Haskell's comparative characterization of Sagredo's individuality, not a specific "
        "patronage event or a census of Venetian patrons."
    ),
    "st-chp9-p263264-sagredo-temperament": (
        "S2: this is Haskell's hedged character assessment and reported anecdote, not a separate entity relation."
    ),
    "st-chp9-p263264-will-archival-locator": (
        "S2: Haskell explicitly locates the will at the Archivio di Stato and identifies its date and notary; "
        "retain the archival-location candidate, but the will and archive endpoints and original record "
        "require S6 review because the cited document was not independently examined."
    ),
    "st-chp9-p263264-wright-anecdote-locator": (
        "S2: this is a bibliographic locator for the anecdote, not an additional historical relation; "
        "Wright's cited page was not independently consulted."
    ),
}
EXPECTED_GLOBAL_BEFORE = {True: 9662, False: 3986, None: 1181}


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


class _ReplaceSegmentNames(ast.NodeTransformer):
    def visit_Name(self, node):
        values = {"P263": P263, "P264": P264, "NOTES": NOTES}
        if node.id in values:
            return ast.copy_location(ast.Constant(values[node.id]), node)
        return node


legacy_tree = ast.parse(LEGACY_SPEC.read_text(encoding="utf-8-sig"))
mention_specs = None
for node in legacy_tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "M" for t in node.targets):
        mention_specs = ast.literal_eval(_ReplaceSegmentNames().visit(node.value))
        break
if mention_specs is None or len(mention_specs) != 75:
    raise SystemExit("legacy mention specification changed; inspect before continuing")
mention_specs = [
    spec for spec in mention_specs
    if spec[0] == P263 or (spec[0] == NOTES and 414 <= spec[1] <= 419)
]
if len(mention_specs) != 44:
    raise SystemExit(f"expected 44 p.263 mentions, found {len(mention_specs)}")

_, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()

existing_ids = {row["mention_id"] for row in current_mentions}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in current_mentions}
new_mentions = []
for segment_id, line, suffix, candidate_id, surface, note, *optional in mention_specs:
    if segment_id not in (P263, NOTES) or candidate_id not in candidate_ids:
        raise SystemExit(f"missing segment or candidate in mention spec: {suffix}")
    line_text = source_lines[line - 1]
    start_at, actual_surface = 0, surface
    pos = line_text.find(surface)
    if pos < 0 and "\ufffd" in surface:
        parts = re.split("\ufffd+", surface)
        pattern = "".join(re.escape(part) + (r"\S" if i < len(parts) - 1 else "")
                          for i, part in enumerate(parts))
        match = re.search(pattern, line_text)
        if match:
            pos, actual_surface = match.start(), match.group(0)
    if pos < 0:
        raise SystemExit(f"source text does not contain mention spec: line {line}, {surface!r}")
    meta = segments[segment_id]
    segment_offset = sum(len(source_lines[n - 1]) + 1 for n in range(meta["line_start"], line))
    start, end = segment_offset + pos, segment_offset + pos + len(actual_surface)
    mention_id = f"m-chp9-p263264-{suffix}"
    span = (segment_id, str(start), str(end))
    if mention_id in existing_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention id: {mention_id}")
    if span in existing_spans or any(
        (row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention span: {mention_id}")
    segment_text = "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])
    if segment_text[start:end] != actual_surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": actual_surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

unset_ids = {
    row["statement_id"] for row in statement_rows
    if row["statement_id"].startswith("st-chp9-p263264-")
    and row.get("qualifiers", {}).get("printed_page") == 263
    and row.get("qualifiers", {}).get("relation_candidate") is None
}
if unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.263 unset classifications: {sorted(unset_ids)}")
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
if after[True] != before[True] + 3 or after[False] != before[False] + 6 or after[None] != before[None] - 9:
    raise SystemExit(f"unexpected classification delta: before={dict(before)}, after={dict(after)}")

for sid in (P263, NOTES):
    if sid not in coverage_by_id or coverage_by_id[sid]["migration_status"] != "complete":
        raise SystemExit(f"unexpected S2 coverage state for {sid}")
coverage_by_id[P263]["note"] += (
    " 2026-10-14 reconciliation restored 21 body mentions and 23 p.263 note mentions after exact source-span "
    "validation; nine previously unset relation_candidate fields were reviewed (3 true, 6 false)."
)
coverage_by_id[NOTES]["note"] += (
    " 2026-10-14 reconciliation restored 23 p.263 note mentions from the source-verified migration specification."
)

summary = {
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "printed_page": 263,
    "pdf_physical_page": 25,
    "recovered_mentions": len(new_mentions),
    "mention_distribution": dict(Counter(row["segment_id"] for row in new_mentions)),
    "mention_line_distribution": dict(Counter(
        str(spec[1]) for spec in mention_specs
    )),
    "classified_statements": {"true": 3, "false": 6, "unset_closed": 9},
    "global_statements": len(statement_rows),
    "global_classifications_after": {"true": after[True], "false": after[False], "unset": after[None]},
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write verified p.263 mention and classification updates")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, STATEMENTS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more p.263 reconciliation backups already exist")
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
