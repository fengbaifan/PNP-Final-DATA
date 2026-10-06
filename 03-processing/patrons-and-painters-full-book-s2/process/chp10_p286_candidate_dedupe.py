"""Deduplicate a p.286 body candidate against the existing Venetian artists category."""
import csv
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
with candidate_path.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    candidate_fields = reader.fieldnames
    candidates = list(reader)
with mention_path.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    mention_fields = reader.fieldnames
    mentions = list(reader)

duplicate_id = "cand-8984"
reuse_id = "cand-8104"
duplicate = [row for row in candidates if row["candidate_id"] == duplicate_id]
reuse = [row for row in candidates if row["candidate_id"] == reuse_id]
mention_rows = [row for row in mentions if row["candidate_id"] == duplicate_id]
if len(duplicate) != 1 or len(reuse) != 1:
    raise SystemExit("expected one duplicate and one existing candidate")
if duplicate[0]["canonical_name"] != "Venetian artists as a collective category in Haskell's account":
    raise SystemExit("duplicate candidate identity changed")
if reuse[0]["canonical_name"] != "Venetian artists (collective category in Haskell's account)":
    raise SystemExit("reusable existing candidate identity changed")
if len(mention_rows) != 1 or mention_rows[0]["mention_id"] != "m-chp10-p286-venetian_artists":
    raise SystemExit("unexpected references to duplicate candidate")
if any(duplicate_id in Path(path).read_text(encoding="utf-8-sig") for path in (
        TABLES / "book-statements.jsonl", TABLES / "alignment.csv", TABLES / "enrichment.jsonl", TABLES / "relations.csv")):
    raise SystemExit("duplicate candidate has additional cross-table references; expand repair scope")

new_candidates = [row for row in candidates if row["candidate_id"] != duplicate_id]
for row in mentions:
    if row["candidate_id"] == duplicate_id:
        row["candidate_id"] = reuse_id

print(json.dumps({"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "removed_candidate": duplicate_id, "reused_candidate": reuse_id,
                  "remapped_mentions": [row["mention_id"] for row in mention_rows],
                  "candidate_count_after": len(new_candidates)}, ensure_ascii=False, indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (candidate_path, mention_path):
        backup_path = Path(str(path) + ".bak-s2-chp10-p286-candidate-dedupe-20261002")
        if backup_path.exists():
            raise SystemExit(f"backup already exists: {backup_path}")
        shutil.copy2(path, backup_path)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=candidate_path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=candidate_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(new_candidates)
        temporary = Path(stream.name)
    temporary.replace(candidate_path)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=mention_path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(mentions)
        temporary = Path(stream.name)
    temporary.replace(mention_path)
    print("Applied candidate deduplication; backups retained.")
