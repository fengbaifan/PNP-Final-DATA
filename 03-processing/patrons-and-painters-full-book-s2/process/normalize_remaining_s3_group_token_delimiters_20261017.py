from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ANCHOR = "s3-remaining-group-token-delimiter-normalization-20261017"
REPLACEMENTS = {
    "cand-1515": (
        "group=archive-group-4ec5e3284567. Appendix 7 prints",
        "group=archive-group-4ec5e3284567; Appendix 7 prints",
    ),
    "cand-1532": (
        "group=archive-group-ff938f5595f2. The Appendix 1 heading",
        "group=archive-group-ff938f5595f2; The Appendix 1 heading",
    ),
    "cand-1549": (
        "group=archive-group-marino-adone-epic. Haskell names",
        "group=archive-group-marino-adone-epic; Haskell names",
    ),
    "cand-1551": (
        "group=archive-group-c659964650de. The index subentry",
        "group=archive-group-c659964650de; The index subentry",
    ),
    "cand-1791": (
        "group=archive-group-osservatore-veneto-periodical, mapped to",
        "group=archive-group-osservatore-veneto-periodical; mapped to",
    ),
}
EXPECTED_GROUPS = {
    "cand-1515": "archive-group-4ec5e3284567",
    "cand-1532": "archive-group-ff938f5595f2",
    "cand-1549": "archive-group-marino-adone-epic",
    "cand-1551": "archive-group-c659964650de",
    "cand-1791": "archive-group-osservatore-veneto-periodical",
}


def group_token(note: str) -> str | None:
    match = re.search(r"(?:^|[;| ])group=([A-Za-z0-9:-]+)", note)
    return match.group(1) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize five punctuation errors after existing S3 group tokens and refresh current group counts.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid, (old, new) in REPLACEMENTS.items():
        current = planned_by_id[cid]
        assert current.get("decision") == "new"
        assert current.get("resolution_note", "").count(old) == 1, cid
        assert group_token(current["resolution_note"]) == EXPECTED_GROUPS[cid], cid
        current["resolution_note"] = current["resolution_note"].replace(old, new, 1)
        current["resolution_note"] += (
            " S3 group-token delimiter correction (2026-10-17): punctuation after the existing group token was normalized; "
            "no candidate decision, identity, or KU mapping was changed."
        )
        assert sync.get_group(current["resolution_note"]) == EXPECTED_GROUPS[cid], (cid, sync.get_group(current["resolution_note"]))

    # The three listed two-member groups must now resolve to exactly two S3 candidates each.
    for cid, peers in {
        "cand-1515": {"cand-1515", "cand-10849"},
        "cand-1532": {"cand-1532", "cand-5338"},
        "cand-1551": {"cand-1551", "cand-4464"},
    }.items():
        expected = EXPECTED_GROUPS[cid]
        members = {
            row["candidate_id"] for row in planned
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == expected
        }
        assert members == peers, (expected, members)

    before = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    after = [row for row in planned if row.get("candidate_id") and not row.get("external_source")]
    assert len(before) == len(after) == len(candidates)
    assert Counter(row["decision"] for row in before) == Counter(row["decision"] for row in after)
    assert all(by_id[cid].get("ku_id", "") == planned_by_id[cid].get("ku_id", "") for cid in REPLACEMENTS)

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 584
    assert totals["registered_members"] == 730
    assert totals["pending_groups"] == 4211
    assert totals["pending_members"] == 4245
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    old_result = "S4 当前登记584组/730条映射，待登记4,214组/4,245条；KU总数1,603。"
    new_result = "S4 当前登记584组/730条映射，待登记4,211组/4,245条；KU总数1,603。"
    assert result_next.count(old_result) == 1
    result_next = result_next.replace(old_result, new_result, 1)

    process_current = PROCESS.read_text(encoding="utf-8-sig")
    old_process = "S4 当前登记584组/730条候选映射；待登记4,214组/4,245条；KU总数1,603。"
    new_process = "S4 当前登记584组/730条候选映射；待登记4,211组/4,245条；KU总数1,603。"
    assert process_current.count(old_process) == 1
    process_next = process_current.replace(old_process, new_process, 1).rstrip()
    process_next += f"""

<a id="{ANCHOR}"></a>

### S3组号分隔符核正：Manfrin、耶稣档案与Marino组（2026-10-17）

全表复核发现5条`new`候选的`group=`字段在身份组号后直接接入解释文字：`cand-1515`、`cand-1532`、`cand-1549`、`cand-1551`、`cand-1791`。将句点或逗号改为分号，使解析器只读取原组号；这5条候选的S3决定、KU映射和理由内容均未改变。`cand-1515`与`cand-10849`、`cand-1532`与`cand-5338`、`cand-1551`与`cand-4464`各自解析为同一双候选组，修正后待登记组数减少3；`cand-1549`和`cand-1791`为单成员组，修正不改变登记组数。

重算后当前S3为new=4,975个候选／4,795个身份组；S4已登记584组／730条映射，待登记4,211组／4,245条；KU总数1,603。该修正只校正组号解析和统计，不增加或撤销身份决定。

Five `new` alignment notes had punctuation immediately after an identity-group token, causing the parser to absorb following prose. Delimiters were normalized for `cand-1515`, `cand-1532`, `cand-1549`, `cand-1551`, and `cand-1791`; decisions, mappings, and rationale text were retained. Three two-candidate groups now parse as one group each, reducing pending S4 groups by three. The two single-member group fixes do not change group counts.
"""

    if args.dry_run:
        print("dry-run passed: five group-token delimiters normalized; candidate decisions and KU mappings unchanged")
        print(f"new={totals['new_candidates']}/{totals['new_groups']} groups; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}")
        print("No files changed.")
        return 0

    sync.write_csv(ALIGNMENT, alignment_fields, planned)
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: new={totals['new_candidates']}/{totals['new_groups']} groups; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
