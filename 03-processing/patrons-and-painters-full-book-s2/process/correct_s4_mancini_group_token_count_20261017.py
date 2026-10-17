from __future__ import annotations

import argparse
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
CANDIDATE = "cand-1508"
GROUP = "archive-group-fb110b11a649"
OLD_FRAGMENT = f"group={GROUP}. The p.120 note cites Mancini, vol.I, p.249"
NEW_FRAGMENT = f"group={GROUP}; The p.120 note cites Mancini, vol.I, p.249"
ANCHOR = "s3-mancini-group-token-normalization-20261017"


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize one S3 group-token delimiter and correct S4 group counts without changing the identity decision.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    target = by_id[CANDIDATE]
    assert target.get("decision") == "new"
    assert target.get("ku_id") == "units/archives/mancini-considerazioni-sulla-pittura-1956"
    assert target.get("resolution_note", "").count(OLD_FRAGMENT) == 1
    planned = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_target = planned_by_id[CANDIDATE]
    planned_target["resolution_note"] = planned_target["resolution_note"].replace(OLD_FRAGMENT, NEW_FRAGMENT, 1)
    planned_target["resolution_note"] += (
        " S3 group-token delimiter correction (2026-10-17): changed only the punctuation after the existing group token "
        "so cand-1508 parses with cand-6089 in the same identity group; no candidate decision or KU mapping changed."
    )

    before_decisions = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    after_decisions = [row for row in planned if row.get("candidate_id") and not row.get("external_source")]
    assert Counter(row["decision"] for row in before_decisions) == Counter(row["decision"] for row in after_decisions)
    assert len(before_decisions) == len(after_decisions) == len(candidates)
    assert planned_by_id[CANDIDATE]["ku_id"] == target["ku_id"]
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    old_result_line = "S4 当前登记585组/730条映射，待登记4,214组/4,245条；KU总数1,603。"
    new_result_line = (
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(manifest))}。"
    )
    assert result_next.count(old_result_line) == 1
    result_next = result_next.replace(old_result_line, new_result_line, 1)

    process_current = PROCESS.read_text(encoding="utf-8-sig")
    old_process_line = "S4 当前登记585组/730条候选映射；待登记4,214组/4,245条；KU总数1,603。"
    new_process_line = (
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(manifest))}。"
    )
    assert process_current.count(old_process_line) == 1
    process_next = process_current.replace(old_process_line, new_process_line, 1).rstrip()
    process_next += f"""

<a id="{ANCHOR}"></a>

### S3组号分隔符核正：Mancini 1956年版（2026-10-17）

`cand-1508`与`cand-6089`此前已判为同一身份组并映射到同一 KU；`cand-1508` 的组号后误用句点，使分组统计把后续说明文字并入组号，导致登记组数多计1。现将组号后的标点改为分号，候选决定、组号主体、KU映射和原理由均保留。重算后S4为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射已登记，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数仍为{sync.fmt(len(manifest))}。这是计数与机器解析边界更正，不是新的身份裁决。

`cand-1508` and `cand-6089` were already assigned to the same identity group and KU. A period after the group token on `cand-1508` caused the grouping parser to absorb following prose and count a second group. The separator is now a semicolon; the decision, identity, KU mapping, and prior rationale remain unchanged. Counts were recalculated; this corrects parsing and reporting only.
"""

    if args.dry_run:
        print(f"dry-run passed: decision_counts_unchanged={dict(Counter(row['decision'] for row in before_decisions))}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}")
        print("No files changed; identity decisions and KU mappings are unchanged.")
        return 0

    sync.write_csv(ALIGNMENT, alignment_fields, planned)
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
