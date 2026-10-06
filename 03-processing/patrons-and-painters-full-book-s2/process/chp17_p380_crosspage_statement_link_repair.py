"""Record the forward edge for the p.379-p.380 cross-page sentence."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
PREVIOUS = "st-chp17-pi-manfrin-established-as-leading-venetian-patron"
TARGETS = (
    "st-chp17-p380-manfrin-death-rumour-reaches-bologna",
    "st-chp17-p380-armanni-writes-sasso-after-rumour",
)
BACKUP_SUFFIX = ".bak-s2-chp17-p380-crosspage-link-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if "Indeed, within five years," not in lines[5] or "when a false rumour of his death" not in lines[8]:
    raise SystemExit("expected p.379-p.380 sentence boundary changed")
statements = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in statements}
if PREVIOUS not in by_id or any(sid not in by_id for sid in TARGETS):
    raise SystemExit("one or more cross-page statements are missing")
for sid in TARGETS:
    q = by_id[sid]["qualifiers"]
    if q.get("cross_reference_statement_ids"):
        raise SystemExit(f"cross-page link already exists for {sid}")
    q["cross_reference_segments"] = ["chp-17:17_CHP-17_sec_i:l3-6"]
    q["cross_reference_statement_ids"] = [PREVIOUS]
    q["cross_reference_text"] = "The sentence begins with 'Indeed, within five years,' at p.379 L6 and continues at p.380 L9-10."

if not args.apply:
    print(json.dumps({"mode": "dry-run", "targets": list(TARGETS), "cross_reference_statement_id": PREVIOUS}, ensure_ascii=False))
    raise SystemExit(0)

shutil.copy2(TABLE, TABLE.with_name(TABLE.name + BACKUP_SUFFIX))
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
    for row in statements:
        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(stream.name)
temporary.replace(TABLE)
print(json.dumps({"mode": "applied", "targets": list(TARGETS), "backup": TABLE.name + BACKUP_SUFFIX}, ensure_ascii=False))
