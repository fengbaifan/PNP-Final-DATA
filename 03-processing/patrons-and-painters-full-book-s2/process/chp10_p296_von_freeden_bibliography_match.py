"""S2-only correction: match p.296's Von Freeden 1956 locator to the local bibliography."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
BIB = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
BACKUP_SUFFIX = ".bak-s2-chp10-p296-vonfreeden-bibmatch-20261002"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(stream.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(stream.name)
    tmp.replace(path)


bib_text = BIB.read_text(encoding="utf-8-sig")
expected_entry = "Freeden, Max H. von: Das Meisterwerk des G. B. Tiepolo, München 1956."
if expected_entry not in bib_text:
    raise SystemExit("local bibliography entry changed or was not found")

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
statements = [json.loads(line) for line in sp.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
vf, coverage = read_csv(vp)
by_cid = {row["candidate_id"]: row for row in candidates}
by_sid = {row["statement_id"]: row for row in statements}
if by_cid["cand-9465"]["canonical_name"] != "Von Freeden (author cited in p.296 note 1; identity unresolved)":
    raise SystemExit("p.296 Von Freeden author candidate changed")
if by_cid["cand-9466"]["canonical_name"] != "Von Freeden, 1956 (p.296 note 1 citation locator; title/page unspecified)":
    raise SystemExit("p.296 Von Freeden citation candidate changed")
sid = "st-chp10-p296-note1-residenz-citation"
if sid not in by_sid or by_sid[sid]["qualifiers"]["citations"][0]["bibliography_match"] != "unresolved":
    raise SystemExit("p.296 Von Freeden statement changed")
note_row = next(r for r in coverage if r["segment_id"] == "chp-10:10_CHP-10_intro:l491-634")
if "Von Freeden 1956 remains an unresolved short-form citation" not in note_row["note"]:
    raise SystemExit("p.296 coverage summary changed")

by_cid["cand-9465"]["canonical_name"] = "Max H. von Freeden (author cited at p.296 note 1; S3 alignment pending)"
by_cid["cand-9465"]["detail"] = (
    "P.296 note 1 supplies surname and year only. The local bibliography identifies Max H. von Freeden as author of "
    "Das Meisterwerk des G. B. Tiepolo (München, 1956). Keep this author mention distinct from cand-9452, the p.293 1955 citation, until global S3 alignment."
)
by_cid["cand-9466"]["canonical_name"] = "Max H. von Freeden, Das Meisterwerk des G. B. Tiepolo (München, 1956; citation locator)"
by_cid["cand-9466"]["detail"] = (
    "Matched to the local bibliography entry by author and year. P.296 note 1 gives no page; the book and relevant passage were not independently consulted."
)
for row in mentions:
    if row["mention_id"] == "m-chp10-p296-n1-von-freeden-author":
        row["note"] = "The local bibliography expands the author to Max H. von Freeden; cross-reference to the p.293 citation remains for S3."
    elif row["mention_id"] == "m-chp10-p296-n1-von-freeden-work":
        row["note"] = "The year matches the local bibliography entry Das Meisterwerk des G. B. Tiepolo; no page is supplied and the work is unread."
q = by_sid[sid]["qualifiers"]
q["claim"] = "P.296 note 1 cites Max H. von Freeden, Das Meisterwerk des G. B. Tiepolo (1956), for the account of Tiepolo's Würzburg Residenz commission."
q["qualification"] = "The short citation matches the local bibliography by author and year. The book and relevant passage were not independently consulted."
q["citations"][0]["bibliography_match"] = "local"
q["citations"][0]["title"] = "Das Meisterwerk des G. B. Tiepolo"
note_row["note"] = note_row["note"].replace(
    "Von Freeden 1956 remains an unresolved short-form citation",
    "Von Freeden 1956 matches the local bibliography entry Das Meisterwerk des G. B. Tiepolo; the cited passage was not consulted",
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the local bibliography match")
args = parser.parse_args()
if not args.apply:
    print("DRY RUN OK: updated p.296 Von Freeden person/work locators using the local bibliography; no source facts added.")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print("APPLIED: local bibliography match recorded in candidates, mention, statement, and coverage.")
