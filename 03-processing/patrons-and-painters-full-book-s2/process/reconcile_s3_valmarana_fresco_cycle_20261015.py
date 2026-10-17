from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATE_ID = "cand-2594"
GROUP = "sg3-work-valmarana-fresco-cycle"
KU_ID = "units/works/tiepolo-valmarana-fresco-cycle"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile S3 cross-chapter identity for Tiepolo's Valmarana fresco cycle"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.apply:
        parser.error("choose exactly one of --dry-run or --apply")

    candidate_fields, candidates = read_csv(TABLES / "entity-candidates.csv")
    _, manifest = read_csv(TABLES / "ku-manifest.csv")
    alignment_fields, alignments = read_csv(ALIGNMENT)
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE_ID)
    assert candidate["suggested_type"] == "work"
    assert candidate["canonical_name"] == "Tiepolo, Giambattista"
    assert "frescoes of scenes from Homer, Virgil, Tasso, and Ariosto" in candidate["sub_entry"]

    rows = [row for row in alignments if row.get("candidate_id") == CANDIDATE_ID]
    assert len(rows) == 1
    current = rows[0]
    assert current["decision"] == "undecided"
    assert not current.get("ku_id")
    assert "不是可核的 S2 body-mention" in current["resolution_note"]

    mentions = []
    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as f:
        mentions = [row for row in csv.DictReader(f) if row.get("candidate_id") == CANDIDATE_ID]
    mention_ids = {row["mention_id"] for row in mentions}
    assert {
        "m-chp9-p258-valmarana-fresco-series",
        "m-chp9-p258-frescoes-1757",
        "m-chp20-p405-017",
        "m-chp20-p405-025",
    } <= mention_ids

    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        for line in f:
            row = json.loads(line)
            statements[row["statement_id"]] = row
    assert statements["st-chp9-p258-tiepolo-painted-valmarana-fresco-cycle"]["object_candidate_id"] == CANDIDATE_ID
    assert statements["st-chp20-p405-puppi-corrects-valmarana-fresco-commission"]["object_candidate_id"] == CANDIDATE_ID
    assert statements["st-chp9-p258-tiepolo-painted-valmarana-fresco-cycle"]["qualifiers"]["printed_page"] == 258
    assert statements["st-chp20-p405-puppi-corrects-valmarana-fresco-commission"]["qualifiers"]["printed_page"] == 405

    source_258 = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
    source_405 = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
    assert "beautiful series of frescoes illustrating romantic scenes" in source_258.read_text(encoding="utf-8-sig")
    assert "were in fact commissioned by Conte Giustino Valmarana" in source_405.read_text(encoding="utf-8-sig")

    work_dir = ROOT / "04-knowledge" / "units" / "works"
    card_path = work_dir / "tiepolo-valmarana-fresco-cycle.md"
    assert not card_path.exists()
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == str(card_path.relative_to(ROOT)).replace("\\", "/") for row in manifest)

    current["decision"] = "new"
    current["resolution_note"] = (
        f"group={GROUP}; source_ref=chp-9:09_CHP-9_intro:l179-186#m-chp9-p258-valmarana-fresco-series; "
        "cross_chapter_mentions=m-chp9-p258-valmarana-fresco-series,m-chp9-p258-frescoes-1757,"
        "m-chp20-p405-017,m-chp20-p405-025; S2 statements st-chp9-p258-tiepolo-painted-valmarana-fresco-cycle "
        "and st-chp20-p405-puppi-corrects-valmarana-fresco-commission identify one Tiepolo fresco cycle at the "
        "Valmarana villa through chapters 9 and 20. The earlier undecided rationale said no verifiable S2 body "
        "mention existed; the current mention and statement records show otherwise. Haskell's p.405 postscript "
        "reports Puppi's correction: Conte Giustino Valmarana commissioned the cycle, not Leonardo; the cited "
        "article was not independently consulted. No exact same-type work KU exists; create one bounded descriptive "
        "work identity for the fresco cycle, without inferring individual fresco titles or versions. Eligible for S4.")

    decisions = [r for r in alignments if r.get("candidate_id") and not r.get("external_source")]
    assert len(decisions) == 12403
    assert sum(r["decision"] == "new" for r in decisions) == 5008
    assert sum(r["decision"] == "undecided" for r in decisions) == 5618
    assert len({r.get("candidate_id") for r in decisions}) == 12403

    print(
        "S3 cross-chapter reconciliation: candidate=cand-2594; decision=undecided->new; "
        f"group={GROUP}; planned_ku={KU_ID}; evidence=ch9:p258+ch20:p405; "
        "no existing same-type work KU"
    )
    if args.apply:
        write_csv(ALIGNMENT, alignment_fields, alignments)
        print("applied: alignment.csv updated; no KU card created in S3")
    else:
        print("dry-run passed; no files changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
