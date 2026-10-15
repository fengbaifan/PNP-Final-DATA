"""Close non-relation classifications on previously reviewed p.358; dry-run by default."""
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
TABLE_SHA256 = "ad511facc1f7bb4a7ac66c65e519463969a57448517488891a44b10c0553e3e2"
BACKUP_SUFFIX = ".bak-s2-ch14-p358-classification-20261014"

# These reviewed rows are interpretation, aesthetic description, broad narrative,
# or citation locators. Concrete creator, commission, employment, advice, and
# archive relations in the same passage already have their own atomic statements.
FALSE_STATEMENTS = {
    "st-chp14-p358-letters-attribution-to-type",
    "st-chp14-p358-algarotti-attitude-to-palladian-architecture",
    "st-chp14-p358-frivolous-outlook-and-neoclassical-reform",
    "st-chp14-p358-picturesque-criterion",
    "st-chp14-p358-flemish-painter-style-description",
    "st-chp14-p358-later-architectural-fantasies",
    "st-chp14-p358-classical-building-structure",
    "st-chp14-p358-moved-to-bologna-and-met-pesci-tesi",
    "st-chp14-p358-classical-building-as-main-element",
    "st-chp14-p358-fanciful-background-as-foil",
    "st-chp14-p358-insisted-on-picturesque-element",
    "st-chp14-p358-italian-and-flemish-combination",
    "st-chp14-p358-piranesi-parallel-and-admiration",
    "st-chp14-p358-limits-of-picturesque-invention-partial",
    "st-chp14-p358-note1-blainville-report",
    "st-chp14-p358-note2-berlin-letter-source",
    "st-chp14-p358-note3-opere-letters",
    "st-chp14-p358-note3-hercolani-manuscript",
    "st-chp14-p358-note3-raccolta-introduction",
    "st-chp14-p358-note4-pesci-letter-locator",
    "st-chp14-p358-note5-pesci-letter-locator",
    "st-chp14-p358-note6-opere-locator",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.358 classifications")
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
p358 = [row for row in rows if row.get("qualifiers", {}).get("printed_page") == 358]
by_id = {row["statement_id"]: row for row in rows}
unset = {
    row["statement_id"] for row in p358
    if "relation_candidate" not in row.get("qualifiers", {})
}
if len(p358) != 36 or unset != FALSE_STATEMENTS:
    raise SystemExit(f"p.358 reviewed statement set changed: total={len(p358)}, symmetric_difference={sorted(unset ^ FALSE_STATEMENTS)}")
if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in p358) != 14:
    raise SystemExit("p.358 relation-candidate count differs from the reviewed page result")
for statement_id in FALSE_STATEMENTS:
    by_id[statement_id]["qualifiers"]["relation_candidate"] = False

output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
report = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "page": 358,
    "statements": {"total": 36, "relation_candidate_true": 14, "relation_candidate_false": 22, "unset": 0},
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
