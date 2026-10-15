"""Close non-relation classifications on previously reviewed p.360; dry-run by default."""
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
TABLE_SHA256 = "8e20a5b5126dab699f12067896febc9e094161daf65bd556ec8def68d61a3fed"
BACKUP_SUFFIX = ".bak-s2-ch14-p360-classification-20261014"

# Evaluations, descriptions of temperament or writing, and note citations do not
# encode a formal relation. The page's seven monument, inscription, and letter
# relations remain separately represented as S2 candidates.
FALSE_STATEMENTS = {
    "st-chp14-p360-synthesis-resolution",
    "st-chp14-p360-algarotti-attached-to-older-tradition",
    "st-chp14-p360-reported-tiepolo-admired-antiquity",
    "st-chp14-p360-representative-early-neoclassicism",
    "st-chp14-p360-temperament-and-vacillation",
    "st-chp14-p360-contemporaries-desire-to-please",
    "st-chp14-p360-sexual-tastes-seem-unstable",
    "st-chp14-p360-difficulty-committing",
    "st-chp14-p360-writings-criticized-as-flabby",
    "st-chp14-p360-caylus-quote",
    "st-chp14-p360-responsive-artists",
    "st-chp14-p360-note1-zanetti",
    "st-chp14-p360-note1-patriarchi",
    "st-chp14-p360-note2-halsband",
    "st-chp14-p360-note3-paciaudi-letter",
    "st-chp14-p360-note4-leslie-memoir",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.360 classifications")
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
p360 = [row for row in rows if row.get("qualifiers", {}).get("printed_page") == 360]
by_id = {row["statement_id"]: row for row in rows}
unset = {
    row["statement_id"] for row in p360
    if "relation_candidate" not in row.get("qualifiers", {})
}
if len(p360) != 23 or unset != FALSE_STATEMENTS:
    raise SystemExit(f"p.360 reviewed statement set changed: total={len(p360)}, symmetric_difference={sorted(unset ^ FALSE_STATEMENTS)}")
if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in p360) != 7:
    raise SystemExit("p.360 relation-candidate count differs from the reviewed page result")
for statement_id in FALSE_STATEMENTS:
    by_id[statement_id]["qualifiers"]["relation_candidate"] = False

output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
report = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "page": 360,
    "statements": {"total": 23, "relation_candidate_true": 7, "relation_candidate_false": 16, "unset": 0},
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
