from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s3-correction-existing-archive-duplicates-20261017"

CORRECTIONS = (
    {
        "candidate": "cand-3541",
        "group": "archive-group-ad7b3715e8f9",
        "ku_id": "units/archives/camassei-sebastian-receipt",
        "card": "04-knowledge/units/archives/camassei-sebastian-receipt.md",
        "evidence": "Haskell第1章p.10注1 L372以相同的Bertolotti Artisti bolognesi pp.161–162收据识别Andrea Camassei；既有卡已逐项读取该同一引文及付款文书，来源与对象定位完全重合。",
    },
    {
        "candidate": "cand-3543",
        "group": "archive-group-957100686406",
        "ku_id": "units/archives/gini-cortona-letter-1666",
        "card": "04-knowledge/units/archives/gini-cortona-letter-1666.md",
        "evidence": "Haskell第1章p.11注1 L415–418记Onorato Gini 1666年书信并称由Claretta 1885 p.516概述；既有卡记录相同发信人、年份、转引和内容语境，收信人及原件号同样未明。",
    },
    {
        "candidate": "cand-3549",
        "group": "archive-group-c9cd423af65c",
        "ku_id": "units/archives/testi-fontana-bernini-letter",
        "card": "04-knowledge/units/archives/testi-fontana-bernini-letter.md",
        "evidence": "Haskell第1章p.17 L699–703所引Fulvio Testi致Conte Francesco Fontana信，与既有卡相同；既有卡已用Fraschetti p.108刊引补出1633-01-29日期，候选1633年描述对应这一书信。",
    },
    {
        "candidate": "cand-3558",
        "group": "archive-group-74048430b6b1",
        "ku_id": "units/archives/arragona-mantua-letter-1621",
        "card": "04-knowledge/units/archives/arragona-mantua-letter-1621.md",
        "evidence": "Haskell第1章p.14 L542–547、567–568记Mantua驻罗马代理Fabrizio Arragona于1621-10-09致一名未具名公国大臣，刊于Luzio p.295；既有卡定位到同一日期、发信人、收信角色与刊布链。",
    },
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct four full-book archive alignments that duplicate existing source-local KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidates = sync.read_csv(TABLES / "entity-candidates.csv")[1]
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest = sync.read_csv(TABLES / "ku-manifest.csv")[1]
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    process_text = PROCESS.read_text(encoding="utf-8-sig").rstrip()
    result_text = RESULT.read_text(encoding="utf-8-sig")

    planned = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }
    for item in CORRECTIONS:
        cid = item["candidate"]
        candidate = candidate_by_id[cid]
        row = decision_by_id[cid]
        assert candidate.get("suggested_type") == "archive"
        assert row.get("decision") == "new" and not row.get("ku_id"), (cid, row.get("decision"), row.get("ku_id"))
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        group_members = {
            other["candidate_id"]
            for other in alignments
            if other.get("candidate_id") and not other.get("external_source")
            and other.get("decision") == "new"
            and sync.get_group(other.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        assert item["ku_id"] in manifest_by_id and manifest_by_id[item["ku_id"]].get("card_path") == item["card"]
        assert (ROOT / item["card"]).is_file()
        target = planned_by_id[cid]
        target["decision"] = "same"
        target["ku_id"] = item["ku_id"]
        target["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        target["resolution_note"] += (
            f" S3 correction ({DATE}): replace prior new decision with same -> {item['ku_id']}; "
            f"source-local duplicate verified against existing card. Evidence: {item['evidence']}"
        )

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(result_text, stats, totals, len(manifest))
    process_append = f"""

<a id="{ANCHOR}"></a>

### S3 更正：四项书内文书已对应既有archive KU（{DATE}）

S4重复对象预检发现下列全书S3新组与既有章前/单章KU指向同一件文献。保留原S3 `new` 文字作为历史，在当前决定列改为`same`并直接映射到唯一既有KU，不新建重复卡：

| 候选 | 当前决定 | 既有KU | 对齐依据 |
|---|---|---|---|
{chr(10).join(f"| `{x['candidate']}`（原组 `{x['group']}`） | `same` | `{x['ku_id']}` | {x['evidence']} |" for x in CORRECTIONS)}

本次只修正身份去向，不改写来源、既有卡内容或S6关系；后续S4计数按修正后的S3决定重算。当前S4新组已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(manifest))}。
"""
    process_next = process_text + process_append

    if args.dry_run:
        print("dry-run passed: " + "; ".join(f"{x['candidate']} -> same {x['ku_id']}" for x in CORRECTIONS))
        print(
            f"same_candidates={totals['same_candidates']}; same_kus={totals['same_kus']}; "
            f"registered_new_groups={totals['registered_groups']}; pending_new_groups={totals['pending_groups']}; "
            f"pending_new_members={totals['pending_members']}; manifest={len(manifest)}"
        )
        print("no KUs or accepted paths will be added; existing S6 records remain unchanged")
        print("no files changed")
        return 0

    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned)
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: corrected={len(CORRECTIONS)}; same_candidates={totals['same_candidates']}; "
        f"same_kus={totals['same_kus']}; registered_new_groups={totals['registered_groups']}; "
        f"pending_new_groups={totals['pending_groups']}; pending_new_members={totals['pending_members']}; "
        f"manifest={len(manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
