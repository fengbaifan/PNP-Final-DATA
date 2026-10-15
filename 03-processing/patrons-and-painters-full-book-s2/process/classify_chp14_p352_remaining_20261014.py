"""Classify remaining p.352 S2 statements using the completed semantic review."""
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
EXPECTED_SHA256 = "7834f996117d4d8156eeaa08cac5dd7ef29708e056e3f460aa578dc89c30b56d"
BACKUP_SUFFIX = ".bak-s2-ch14-p352-classification-20261014"

REASONS = {
    "st-chp14-p352-first-indication-of-relations": "Haskell's framing of the episode as an indication about the nature of a relationship is metanarrative; it does not assert a concrete historical relation type.",
    "st-chp14-p352-no-evidence-prior-venice-contact": "A bounded statement about absence of evidence is retained as a claim, not converted into a contact or non-contact relation.",
    "st-chp14-p352-tiepolo-appraisal-and-reservation": "Attributed appraisal of Tiepolo's style and standing; it is not a concrete relation between entities.",
    "st-chp14-p352-tiepolo-recognition": "A collective critical reputation claim with no identified recognizing agent; it is preserved as narrative status, not a relation edge candidate.",
    "st-chp14-p352-friendly-letter-from-villa-cordellina": "This compound report is retained for its tone and discussion content; the letter's author and addressee are represented by the two separate atomic statements already present.",
    "st-chp14-p352-sketch-outdoor-setting": "Description of the modello's depicted setting and visual quality; it does not identify a distinct historical place or relation endpoint.",
    "st-chp14-p352-large-version-loggia-and-capital": "Description of the large version's composition and inferred setting, not a relation between identified entities.",
    "st-chp14-p352-cleopatra-description-continuation": "Cross-page visual description of Cleopatra and attendants, linked to its continuation on p.353; no entity relation is asserted.",
    "st-chp14-p352-note1-picture-history": "Bibliographic locator to Levey and Haskell; the cited publications are linked in the processing record, and this row lacks a source-to-publication relation endpoint pair.",
    "st-chp14-p352-note2-prior-contact": "The note explicitly limits the evidence for contact before 1743; the possible Milan meeting and Morassi's attributed friendship claim are recorded separately.",
    "st-chp14-p352-note3-tiepolo-letter": "Bibliographic locator for the 26 October 1743 letter; the author and addressee are recorded in separate atomic statements.",
    "st-chp14-p352-large-version-not-in-original-series": "An explicit exclusion from the earlier five-work series is retained as a qualified claim, not treated as a positive membership relation.",
    "st-chp14-p352-modello-shows-tiepolo-original-intentions": "Interpretive description of what the modello reveals about artistic intention, not a concrete historical relation between the artist and work.",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.352 classifications")
args = parser.parse_args()


def read_jsonl():
    return [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def sha(data):
    return hashlib.sha256(data).hexdigest()


if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
    raise SystemExit("canonical chapter 14 source changed")
before_bytes = STATEMENTS.read_bytes()
if sha(before_bytes) != EXPECTED_SHA256:
    raise SystemExit("statement table changed since p.352 classification was prepared")
rows = read_jsonl()
by_id = {row["statement_id"]: row for row in rows}
target_ids = set(REASONS)
missing = target_ids - by_id.keys()
if missing:
    raise SystemExit(f"p.352 statement missing: {sorted(missing)}")
page_rows = [row for row in rows if row["statement_id"].startswith("st-chp14-p352-")]
if len(page_rows) != 31:
    raise SystemExit(f"unexpected p.352 statement count: {len(page_rows)}")
for statement_id in target_ids:
    q = by_id[statement_id].get("qualifiers", {})
    if q.get("relation_candidate") is not None:
        raise SystemExit(f"expected unset classification for {statement_id}")
    q["relation_candidate"] = False
    q["relation_candidate_note"] = REASONS[statement_id]

after_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "page_statements": len(page_rows),
    "classified_false": len(target_ids),
    "remaining_unset": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in page_rows),
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
