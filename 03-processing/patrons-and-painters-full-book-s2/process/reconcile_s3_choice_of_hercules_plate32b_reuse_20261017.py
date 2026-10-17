from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ENTITY_PATH = TABLES / "entity-candidates.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CID = "cand-7245"
GROUP = "workgrp-de01ab2bdfc994"
KU = "units/works/paolo-de-matteis-the-choice-of-hercules"
STATEMENTS = [
    "st-chp7-p198-haskell-on-shaftesbury-executant",
    "st-chp7-p198-shaftesbury-de-matteis-choice-hercules",
    "st-chp7-p199-choice-hercules-failed-to-convey-thought",
    "st-chp7-p199-shaftesbury-satisfied-with-picture",
    "st-chp7-p198-shaftesbury-applied-ideas-to-choice-of-hercules",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row["candidate_id"] == CID)
    alignment_row = next(row for row in alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    assert candidate["suggested_type"] == "work"
    assert alignment_row["decision"] == "new" and not alignment_row.get("ku_id")
    assert sync.get_group(alignment_row.get("resolution_note", "")) == GROUP
    assert KU in manifest_by_id and manifest_by_id[KU]["type"] == "work"
    assert (ROOT / manifest_by_id[KU]["card_path"]).exists()

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    for sid in STATEMENTS:
        assert sid in statements and statements[sid].get("qualifiers", {}).get("relation_candidate")
    assert "Hercules at the Crossroads" in statements["st-chp7-p198-shaftesbury-de-matteis-choice-hercules"]["original_quote"]
    assert "The choice of Hercules" in (ROOT / manifest_by_id[KU]["card_path"]).read_text(encoding="utf-8-sig")

    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") == CID and not row.get("external_source"):
            row["decision"] = "same"
            row["ku_id"] = KU
            row["process_ref"] = "S3-cross-chapter-work-reuse-2026-10-17"
            row["resolution_note"] = (
                f"prior_group={GROUP}; S3 correction 2026-10-17: same as existing work KU {KU}. "
                "The body identifies the experiment as Hercules at the Crossroads between Vice and Virtue; its cross-referenced Plate 32b "
                "caption names Paolo de Matteis, The Choice of Hercules, Temple Newsam, Leeds. The accepted KU records this same plate and version."
            )
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s3-choice-of-hercules-plate32b-work-reuse\"></a>\n\n"
        "### S3 work 复用修正：Paolo de Matteis 图版32b（2026-10-17）\n\n"
        f"`{CID}` 原 `new` 组 `{GROUP}` 与既有 `{KU}` 为同一作品。第7章 p.198 称 Shaftesbury 选择 Paolo de Matteis 创作 “Hercules at the Crossroads between Vice and Virtue”，"
        "并交叉引用图版32b；图版目录及现有作品卡均记录 Paolo de Matteis 的《The Choice of Hercules》、Temple Newsam、Leeds。"
        "据此将候选改为 `same` 并复用现有 KU，不重复建卡；5条直接 relation_candidate 仍依 S6 处理，本次未改正式关系。\n\n"
        f"S4 登记仍为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )
    result_text += (
        "\n\n### S3 work：Choice of Hercules 图版32b复用（2026-10-17）\n\n"
        f"`{CID}` 从原 `new` 身份组修正为 `same`，映射至[Paolo de Matteis《The Choice of Hercules》图版32b作品卡](../units/works/paolo-de-matteis-the-choice-of-hercules.md)。"
        "第7章正文与图版目录的题名及图版号对应；不重复建卡。5条候选关系留待 S6。"
        f"S4 登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )

    if args.dry_run:
        print(f"S3 work reuse dry-run passed: {CID} -> same {KU}; no new KU")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,} (unchanged)"
        )
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CID}=same->{KU}; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
