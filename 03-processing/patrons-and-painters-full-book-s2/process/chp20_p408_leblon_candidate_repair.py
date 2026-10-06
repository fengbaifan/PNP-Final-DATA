#!/usr/bin/env python3
"""Redirect the p.408 Le Blon mention to the existing index candidate."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
FILES = [TABLES / "entity-candidates.csv", TABLES / "mentions.csv", TABLES / "book-statements.jsonl"]
OLD = "cand-11111"
EXISTING = "cand-1375"
EXPECTED = {
    "entity-candidates.csv": "5a042ea5842aeed0c1f486b77d0b4501eeff33cbb470ff024898f4832535d05b",
    "mentions.csv": "e29c179c6a2ba08df45b232dd6209c153035685364f430ebe1464b0e5c29bc25",
    "book-statements.jsonl": "400ff689c827ef2ca428b7cd4647779dfe9d5cdf8c0b462a6ae4abd2c4fc553e",
}
BACKUP = ".bak-s2-chp20-p408-leblon-reuse-20261004"
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

for path in FILES:
    if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED[path.name]:
        raise SystemExit(f"unexpected file state: {path.name}")

candidate_path, mention_path, statement_path = FILES
with candidate_path.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    candidate_fields, candidates = reader.fieldnames, list(reader)
existing = next((row for row in candidates if row["candidate_id"] == EXISTING), None)
duplicate = next((row for row in candidates if row["candidate_id"] == OLD), None)
if not existing or existing["canonical_name"] != "LeBlon, Jakob Christoffel" or existing["status"] != "open":
    raise SystemExit("the expected existing Le Blon candidate is unavailable")
if not duplicate or duplicate["canonical_name"] != "Jakob Christoffel Le Blon":
    raise SystemExit("the p.408 duplicate candidate is unavailable")
with mention_path.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    mention_fields, mentions = reader.fieldnames, list(reader)
old_mentions = [row for row in mentions if row["candidate_id"] == OLD]
if len(old_mentions) != 2 or any(row["segment_id"] != "chp-20:20_CHP-20Postscript:l174-185" for row in old_mentions):
    raise SystemExit("unexpected references to the duplicate candidate")
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
updated_refs = 0
for row in statements:
    if row.get("subject_candidate_id") == OLD:
        row["subject_candidate_id"] = EXISTING
        updated_refs += 1
    if row.get("object_candidate_id") == OLD:
        row["object_candidate_id"] = EXISTING
        updated_refs += 1
    q = row.get("qualifiers", {})
    ids = q.get("mentioned_candidate_ids", [])
    if OLD in ids:
        q["mentioned_candidate_ids"] = [EXISTING if cid == OLD else cid for cid in ids]
        updated_refs += ids.count(OLD)
if updated_refs != 2:
    raise SystemExit(f"expected two statement references; got {updated_refs}")
for row in mentions:
    if row["candidate_id"] == OLD:
        row["candidate_id"] = EXISTING
candidates = [row for row in candidates if row["candidate_id"] != OLD]
print(f"DRY RUN: redirect {len(old_mentions)} mentions and {updated_refs} statement references to {EXISTING}; remove duplicate candidate {OLD}")
if not args.apply:
    raise SystemExit(0)
backups = [path.with_name(path.name + BACKUP) for path in FILES]
if any(path.exists() for path in backups):
    raise SystemExit("repair backup already exists")
for path, backup in zip(FILES, backups):
    shutil.copy2(path, backup)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=candidate_path.parent, delete=False) as handle:
    writer = csv.DictWriter(handle, fieldnames=candidate_fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader(); writer.writerows(candidates); temp = Path(handle.name)
temp.replace(candidate_path)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=mention_path.parent, delete=False) as handle:
    writer = csv.DictWriter(handle, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader(); writer.writerows(mentions); temp = Path(handle.name)
temp.replace(mention_path)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statement_path.parent, delete=False) as handle:
    for row in statements:
        handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temp = Path(handle.name)
temp.replace(statement_path)
print(f"APPLIED: reuse {EXISTING}; removed {OLD}; backups use suffix {BACKUP}")
