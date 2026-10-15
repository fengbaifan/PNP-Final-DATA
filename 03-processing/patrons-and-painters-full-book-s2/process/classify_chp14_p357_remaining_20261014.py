"""Close omitted non-relation classifications on previously reviewed p.357; dry-run by default."""
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
TABLE_SHA256 = "3979e00afa8018832f78e68540cd520a7e7cffc2ccdbf73c4db76e126eb15ed8"
BACKUP_SUFFIX = ".bak-s2-chp14-p357-classification-20261014"

# These are authorial summaries, evaluations, generic biography, citation locators,
# or group descriptions whose atomic relation claims are already separate rows.
FALSE_STATEMENTS = {
    "st-chp14-p357-continued-commissioning-pictures",
    "st-chp14-p357-rome-as-exemplar-for-frederick",
    "st-chp14-p357-batoni-triumph-seen-at-foscarini-palace",
    "st-chp14-p357-batoni-cleopatra-proposal-for-king",
    "st-chp14-p357-pannini-colour-and-interior-strength",
    "st-chp14-p357-left-germany-and-returned-to-venice",
    "st-chp14-p357-algarotti-no-longer-official-but-active",
    "st-chp14-p357-turn-to-architectural-painting-and-views",
    "st-chp14-p357-grand-canal-view-architectural-elements",
    "st-chp14-p357-architectural-capricci-in-rome",
    "st-chp14-p357-note1-curli-letter",
    "st-chp14-p357-note3-potsdam-letter",
    "st-chp14-p357-note4-bonomo-letter",
    "st-chp14-p357-note5-letter-and-source-chain",
    "st-chp14-p357-note6-fresco-dating",
    "st-chp14-p357-note7-pesci-letter-and-parma-version",
    "st-chp14-p357-note8-chapter-11-reference",
    "st-chp14-p357-pannini-admired-in-mead-collection",
    "st-chp14-p357-algarotti-remained-close-to-painters",
    "st-chp14-p357-algarotti-probably-continued-collecting",
    "st-chp14-p357-algarotti-admired-tiepolo-fresco",
    "st-chp14-p357-note2-letter-requested-rome-artist-details",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.357 classifications")
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
p357 = [row for row in rows if row.get("qualifiers", {}).get("printed_page") == 357]
by_id = {row["statement_id"]: row for row in rows}
unset = {
    row["statement_id"] for row in p357
    if "relation_candidate" not in row.get("qualifiers", {})
}
if len(p357) != 58 or unset != FALSE_STATEMENTS:
    raise SystemExit(f"p.357 reviewed statement set changed: total={len(p357)}, symmetric_difference={sorted(unset ^ FALSE_STATEMENTS)}")
if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in p357) != 36:
    raise SystemExit("p.357 relation-candidate count differs from the reviewed page result")
for statement_id in FALSE_STATEMENTS:
    by_id[statement_id]["qualifiers"]["relation_candidate"] = False

output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
report = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "page": 357,
    "statements": {"total": 58, "relation_candidate_true": 36, "relation_candidate_false": 22, "unset": 0},
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
