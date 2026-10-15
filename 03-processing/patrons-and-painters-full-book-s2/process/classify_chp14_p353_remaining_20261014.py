"""Classify remaining p.353 S2 statements after semantic re-audit."""
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
EXPECTED_SHA256 = "26d08faa3071147601e94a92e9fd3f1a401ca9173483ac09d9882037264ef0be"
BACKUP_SUFFIX = ".bak-s2-ch14-p353-classification-20261014"

REASONS = {
    "st-chp14-p353-cleopatra-comparison-closed": "Cross-page completion of Haskell's visual comparison of the attendants; preserved as work description, not an independent entity relation.",
    "st-chp14-p353-completed-version-classical-composition": "Formal and stylistic interpretation of the composition, not a concrete historical relation between the painting and an independent entity.",
    "st-chp14-p353-greyhound-version-comparison": "Compares the position and pictorial role of a depicted animal between versions; the animal is not independently identified as an entity.",
    "st-chp14-p353-jug-replaced-by-greek-vase": "Describes changes to depicted objects within the composition; the jug and vase are not separately identified works or historical objects.",
    "st-chp14-p353-excavations-and-vase-forms": "Haskell's prospective art-historical interpretation about the circulation of vase forms; it does not report a specific find, transfer, or completed event.",
    "st-chp14-p353-mark-antony-helmet-change": "Describes iconographic details in the completed composition; no extant helmet or eagle object is identified.",
    "st-chp14-p353-isis-and-serapis-statues": "Describes represented figures and compositional features, not identified extant statues or a historical relation to the painting.",
    "st-chp14-p353-algarotti-letter-and-engraving-plan": "Compound report retained with its undated and unverified source qualification; authorship, addressee, and intended engraving transfer are already recorded in separate atomic statements.",
    "st-chp14-p353-algarotti-praises-architectural-and-perspectival-features": "Attributed critical appraisal of a painting; the approval is not modeled as a historical relation candidate.",
    "st-chp14-p353-algarotti-praises-pictorial-scholarship": "Attributed critical appraisal using a source-specific term, not a concrete historical relation.",
    "st-chp14-p353-roman-school-prerogative": "Haskell's qualified account of an artistic tradition and its perceived prerogative; not a formal school-membership or institutional relation.",
    "st-chp14-p353-classical-claim-and-period-comparison": "Comparative art-historical evaluation attributed to Haskell, not a historical relation between the painting and a separate entity.",
    "st-chp14-p353-king-prefers-old-masters": "Haskell's account of collecting priorities, already bounded as an interpretation; it does not identify an acquired work or a specific commission.",
    "st-chp14-p353-note1-picture-locations-and-source": "Compound bibliographic note; the two reported work-to-museum locations are already represented by separate atomic statements, while the cited article is linked as a locator.",
    "st-chp14-p353-note1-leonardis-engraving": "The note's plate reproduction information is cross-linked to the existing Plate 68b caption statements; it duplicates edition-level caption metadata rather than adding a separate historical relation.",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.353 classifications")
args = parser.parse_args()


def sha(data):
    return hashlib.sha256(data).hexdigest()


if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
    raise SystemExit("canonical chapter 14 source changed")
before_bytes = STATEMENTS.read_bytes()
if sha(before_bytes) != EXPECTED_SHA256:
    raise SystemExit("statement table changed since p.353 classification was prepared")
rows = [json.loads(line) for line in before_bytes.decode("utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
page_rows = [row for row in rows if row["statement_id"].startswith("st-chp14-p353-")]
if len(page_rows) != 35:
    raise SystemExit(f"unexpected p.353 statement count: {len(page_rows)}")
if set(REASONS) != {row["statement_id"] for row in page_rows if row.get("qualifiers", {}).get("relation_candidate") is None}:
    raise SystemExit("the p.353 unset statement set changed")
for statement_id, reason in REASONS.items():
    q = by_id[statement_id].setdefault("qualifiers", {})
    q["relation_candidate"] = False
    q["relation_candidate_note"] = reason

after_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "page_statements": len(page_rows),
    "classified_false": len(REASONS),
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
