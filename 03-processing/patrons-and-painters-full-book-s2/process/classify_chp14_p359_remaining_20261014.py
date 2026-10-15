"""Close non-relation classifications on previously reviewed p.359; dry-run by default."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
SOURCE_SHA256 = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA256 = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
TABLE_SHA256 = "de2a821d0c18e2a54c77abec7d678bdc8cd46552bda1b7bf64ae507c89cb92bd"
BACKUP_SUFFIX = ".bak-s2-ch14-p359-classification-20261014"

# These are theoretical interpretations, broad aesthetic summaries, or citation
# locators; specific commissions, works, artists, and cross-page relations remain
# in their separate atomic statements.
FALSE_STATEMENTS = {
    "st-chp14-p359-classical-framework-and-pictorial-variety",
    "st-chp14-p359-no-position-for-great-pictures",
    "st-chp14-p359-theoretical-works-on-arts",
    "st-chp14-p359-evaluation-of-theoretical-works",
    "st-chp14-p359-algarotti-moved-toward-neo-classicism",
    "st-chp14-p359-qualified-theoretical-approach",
    "st-chp14-p359-reconciliation-demand-in-every-commission",
    "st-chp14-p359-algarotti-synthesis-styles-partial",
    "st-chp14-p359-note1-baudi-di-vesme-locator",
    "st-chp14-p359-note2-opere-locator",
    "st-chp14-p359-note3-gabbrielli-general-discussion",
    "st-chp14-p359-note4-gabbrielli-general-discussion",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.359 classifications")
ARGS = parser.parse_args()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as f:
        f.write(data)
        temp = Path(f.name)
    temp.replace(path)


if sha(SOURCE.read_bytes()) != SOURCE_SHA256 or sha(PDF.read_bytes()) != PDF_SHA256:
    raise SystemExit("canonical chapter 14 source changed; refusing to write")
if sha(TABLE.read_bytes()) != TABLE_SHA256:
    raise SystemExit("book-statements baseline changed; refusing to write")

rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
p359 = [row for row in rows if row.get("qualifiers", {}).get("printed_page") == 359]
by_id = {row["statement_id"]: row for row in rows}
unset = {
    row["statement_id"] for row in p359
    if "relation_candidate" not in row.get("qualifiers", {})
}
if len(p359) != 24 or unset != FALSE_STATEMENTS:
    raise SystemExit(f"p.359 reviewed statement set changed: total={len(p359)}, symmetric_difference={sorted(unset ^ FALSE_STATEMENTS)}")
if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in p359) != 12:
    raise SystemExit("p.359 relation-candidate count differs from the reviewed page result")
for statement_id in FALSE_STATEMENTS:
    by_id[statement_id]["qualifiers"]["relation_candidate"] = False

output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
report = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "page": 359,
    "statements": {"total": 24, "relation_candidate_true": 12, "relation_candidate_false": 12, "unset": 0},
    "before_sha256": TABLE_SHA256,
    "after_sha256": sha(output),
    "backup": TABLE.name + BACKUP_SUFFIX,
}
print(json.dumps(report, ensure_ascii=False, indent=2))

if ARGS.apply:
    original = TABLE.read_bytes()
    backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
    if backup.exists():
        if backup.read_bytes() != original:
            raise SystemExit(f"existing recovery copy differs from current file: {backup.name}")
    else:
        shutil.copy2(TABLE, backup)
    try:
        atomic_write(TABLE, output)
    except Exception:
        TABLE.write_bytes(original)
        raise
