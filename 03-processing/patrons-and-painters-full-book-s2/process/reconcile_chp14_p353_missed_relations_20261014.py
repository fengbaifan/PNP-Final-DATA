"""Restore three explicit p.353 reception/preference relation candidates."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
SOURCE_SHA256 = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
EXPECTED_SHA256 = "6a4b0d3bbcfa0fe32d64e5c39df29f6cb447550547cb665b0f86a95493aa75f6"
BACKUP_SUFFIX = ".bak-s2-ch14-p353-relation-reconcile-20261014"
REASONS = {
    "st-chp14-p353-algarotti-praises-architectural-and-perspectival-features": "Haskell explicitly reports Algarotti's approval of the named painting's architectural reality, historical accuracy, perspective, and grandeur; retain as a source-attributed reception relation.",
    "st-chp14-p353-algarotti-praises-pictorial-scholarship": "Haskell explicitly reports Algarotti's admiration for the painting's pictorial scholarship; the term and work are separately identified and linked.",
    "st-chp14-p353-king-prefers-old-masters": "The source attributes a collecting preference to the King: increasing his old-master collection over commissioning contemporary artists. This records an expressed priority, not a completed acquisition.",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="restore the omitted p.353 relation candidates")
args = parser.parse_args()


def sha(data):
    return hashlib.sha256(data).hexdigest()


if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
    raise SystemExit("canonical chapter 14 source changed")
before_bytes = STATEMENTS.read_bytes()
if sha(before_bytes) != EXPECTED_SHA256:
    raise SystemExit("statement table changed since the p.353 relation audit")
rows = [json.loads(line) for line in before_bytes.decode("utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
for statement_id, reason in REASONS.items():
    row = by_id.get(statement_id)
    if row is None:
        raise SystemExit(f"missing p.353 statement: {statement_id}")
    q = row.setdefault("qualifiers", {})
    if q.get("relation_candidate") is not False:
        raise SystemExit(f"expected a prior false classification for {statement_id}")
    if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
        raise SystemExit(f"relation endpoint missing for {statement_id}")
    q["relation_candidate"] = True
    q["relation_candidate_note"] = reason

after_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "restored_relation_candidates": list(REASONS),
    "count": len(REASONS),
    "before_sha256": sha(before_bytes),
    "after_sha256": sha(after_bytes),
}, ensure_ascii=False, indent=2))

if args.apply:
    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    if backup.exists():
        if sha(backup.read_bytes()) != EXPECTED_SHA256:
            raise SystemExit(f"existing backup differs from the pre-write table: {backup.name}")
    else:
        shutil.copy2(STATEMENTS, backup)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENTS.parent, delete=False) as handle:
        handle.write(after_bytes.decode("utf-8"))
        temp_path = Path(handle.name)
    temp_path.replace(STATEMENTS)
    print(json.dumps({"written_sha256": sha(STATEMENTS.read_bytes()), "backup": backup.name}))
