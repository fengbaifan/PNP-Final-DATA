from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATE_ID = "cand-5039"
GROUP = "workgrp-8e3da8b6b4eae3"
KU_ID = "units/works/visitation-chapel-altar-painting"
CARD_REL = "04-knowledge/units/works/visitation-chapel-altar-painting.md"
NAME_ZH = "未具名的访亲小堂祭坛画"
NAME_EN = "Altar painting for the Chapel of the Visitation"
ANCHOR = "s4-work-visitation-chapel-altarpiece-20261017"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_QUOTE = (
    "In 1582, well before the completion of the church, the Oratorians had commissioned an altar painting "
    "to be placed in the Chapel of the Visitation. For this they turned to Federico Barocci in Urbino."
)
EXPECTED_RELATION_IDS = {
    "st-chp3-secii-l40-52-barocci-painted-commission",
    "st-chp3-secii-l40-52-barocci-picture-aesthetic-effect",
    "st-chp3-secii-l40-52-oratorians-commission-visitation-altarpiece",
    "st-chp3-secii-l40-52-philip-concealed-picture-effects",
    "st-chp3-secii-l40-52-reported-philip-ecstasy",
    "st-chp3-secii-l40-52-visitation-painting-arrived-rome",
    "st-chp3-secii-l62-72-order-assimilated-barocci-masterpiece",
}


def make_card() -> str:
    source = {
        "citation": BOOK_CITATION,
        "location": "第3章；印刷页69；L49",
        "sentence_summary": (
            "Haskell称奥拉托利会于1582年委托一幅祭坛画，预定置于 Chapel of the Visitation，并称他们为此转向 Urbino 的 Federico Barocci。"
            "该段未给作品原题或明确题材；‘四年后到达罗马’保留为原书相对时间，不计算具体年份。"
        ),
        "original_quotes": [{"source_span": "L49; print p. 69", "text": SOURCE_QUOTE}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": "L49; print p. 69",
        },
    }
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [source],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[第3章 p.69](../../../{SOURCE_FILE})（L49）"
    relation_lines = "\n".join(f"- `{statement_id}`" for statement_id in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** 本卡对应 Haskell 所述一幅为 Chapel of the Visitation 委托的祭坛画。第3章称奥拉托利会于1582年委托此画，并为此转向 Urbino 的 Federico Barocci。此段没有提供作品原题，也未明确指出画中题材；中英文名称均为依小堂名称拟定的描述性工作题名，“访亲”指小堂名称，不表示画作题材。{source_link}

**English:** This card represents the altar painting described by Haskell as commissioned for the Chapel of the Visitation. Chapter 3 says the Oratorians commissioned it in 1582 and turned to Federico Barocci at Urbino. The passage supplies neither an original title nor an explicit subject. Both names are descriptive working titles based on the chapel's name; “Visitation” identifies the chapel, not an asserted subject of the painting. {source_link}

### 作品身份与边界

- 作品类型：祭坛画；原书用语为 “altar painting”。{source_link}
- 委托与预定安置语境：1582年委托，拟置于 Chapel of the Visitation；本段不据此确认最终安装。{source_link}
- 创作归属语境：Haskell称委托者为此转向 Federico Barocci；该角色关系仍是S2候选，待S6裁决。{source_link}
- 其他限定：原书称该画“四年后”到达罗马；本卡保留相对时间，不换算具体年份。{source_link}

## 关系与证据

### 关系记录

当前没有新增正式关系。以下7条直接涉及本作品候选的S2关系候选仍留待S6逐条核对关系类型、端点和限定：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the untitled Chapel of the Visitation altar painting in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    candidate = candidate_by_id[CANDIDATE_ID]
    alignment = alignment_by_id[CANDIDATE_ID]
    assert candidate.get("suggested_type") == "work"
    assert candidate.get("candidate_source_ref") == "chp-3:03_CHP-3_sec_ii:l40-52#L49"
    assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    assert len(manifest_targets) <= 1
    card_path = ROOT / CARD_REL
    registered = bool(manifest_targets) and alignment.get("ku_id") == KU_ID and CARD_REL in accepted_paths and card_path.exists()
    if registered:
        assert len(manifest_targets) == 1 and manifest_targets[0].get("canonical_name") == NAME_ZH
        assert card_path.read_text(encoding="utf-8-sig") == make_card()
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 7 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and not alignment.get("ku_id") and not card_path.exists() and CARD_REL not in accepted_paths
    assert not any(
        row.get("type") == "work" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "an exact work title already exists"

    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == {CANDIDATE_ID}, group_members
    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == EXPECTED_RELATION_IDS, (direct_relations, EXPECTED_RELATION_IDS)
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    assert " ".join(SOURCE_QUOTE.split()) in source_text

    planned_alignment = [dict(row) for row in alignments]
    planned_alignment_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_alignment_by_id[CANDIDATE_ID]["ku_id"] = KU_ID
    planned_alignment_by_id[CANDIDATE_ID]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 work：Chapel of the Visitation 祭坛画身份组登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`（`{GROUP}`）登记为[未具名访亲小堂祭坛画作品卡](../../../{CARD_REL})。"
        "原书明确委托、预定小堂、转向 Barocci 及相对时间，但未给作品原题或题材；卡片据此采用描述性工作题名，不把小堂名称当作画作题材。"
        "7条直接关系候选均留待S6，没有写入正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### work：Chapel of the Visitation 祭坛画身份组 S4 登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}` → [作品卡](../units/works/visitation-chapel-altar-painting.md)。"
        "题名为描述性工作题名；原书未说明原题或画作题材。7条直接S2关系候选仍待S6裁决，未新增正式关系。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 work dry-run passed: {GROUP} -> {KU_ID}")
        print(f"direct relation candidates={len(direct_relations)}; source quotations=1; exact work-name collision=none")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,}->{len(planned_manifest):,}"
        )
        print("no files changed")
        return 0

    card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
