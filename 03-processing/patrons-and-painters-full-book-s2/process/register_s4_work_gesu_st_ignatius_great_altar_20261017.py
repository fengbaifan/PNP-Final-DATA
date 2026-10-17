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

CANDIDATE_ID = "cand-5420"
GROUP = "workgrp-6e3beccdc5b5e1"
KU_ID = "units/works/gesu-st-ignatius-great-altar-project"
CARD_REL = "04-knowledge/units/works/gesu-st-ignatius-great-altar-project.md"
NAME_ZH = "耶稣堂圣依纳爵小堂大祭坛方案"
NAME_EN = "Great Altar Project for the Chapel of St Ignatius in the Gesù"
ANCHOR = "s4-work-gesu-st-ignatius-great-altar-20261017"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
QUOTES = (
    {
        "location": "第3章；印刷页92；OCR L168",
        "source_span": "line 168; print p. 92",
        "quote": "The Jesuits thus had the money and the rights of patronage with which to build the great altar they planned.",
        "summary_cn": "第3章称耶稣会士拥有兴建其所规划大祭坛的资金与赞助权；竞赛中选择Pozzo的方案，相关讨论延续到1695年。",
    },
    {
        "location": "第3章；印刷页92；OCR L171",
        "source_span": "line 171; print p. 92",
        "quote": "Finally, in May 1695 after much hesitation, the General, Tirso Gonzalez, made his irrevocable decision and forbade any further criticisms. Pozzo was put in complete charge of the altar.",
        "summary_cn": "Haskell记述Tirso Gonzalez于1695年5月作出最终决定，并称Pozzo全面负责该祭坛；这一著录本身不补出完工日期。",
    },
    {
        "location": "第3章；印刷页92；OCR L177",
        "source_span": "line 177; print p. 92",
        "quote": "Within the altar itself there is much fineness of craftsmanship and complexity of detail. But these more subtle features—such as the bas-reliefs depicting the life and",
        "summary_cn": "Haskell开始描述祭坛工艺及其浅浮雕；句子在印刷页界处继续。",
    },
    {
        "location": "第3章；印刷页93；OCR L180",
        "source_span": "line 180; print p. 93",
        "quote": "miracles of St Ignatius—are embedded in such a mass of colour and riot of ornamentation that they are easy to overlook.",
        "summary_cn": "Haskell描述祭坛内部工艺及表现圣依纳爵生平与奇迹的浅浮雕；本卡不据此补出其后续存世或当前位置。",
    },
)
EXPECTED_RELATION_IDS = {
    "st-chp3-seciv-l165-177-doctors-figures-scheme-abandoned",
    "st-chp3-seciv-l165-177-jesuits-had-money-and-patronage-rights",
    "st-chp3-seciv-l165-177-pozzo-threatened-withdrawal-and-debates-continued",
    "st-chp3-seciv-l165-177-subtle-basreliefs-described-across-page",
    "st-chp3-seciv-l165-177-tirso-final-decision-may-1695",
    "st-chp3-seciv-l165-177-tirso-forbade-further-criticism",
    "st-chp3-seciv-l179-187-altar-reliefs-embedded-in-ornament",
}


def make_card() -> str:
    source = {
        "citation": BOOK_CITATION,
        "location": "第3章；印刷页92–93；OCR L168、L171、L177、L180",
        "sentence_summary": "Haskell记述耶稣堂圣依纳爵小堂大祭坛方案、Pozzo受命负责及浅浮雕等内部细节；竞赛与设计记载不单独确定完工日期或现存状态。",
        "original_quotes": [
            {"source_span": item["source_span"], "text": item["quote"]}
            for item in QUOTES
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": "lines 168, 171, 177, 180; print pp. 92–93",
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
    source_link = f"[第3章书内来源](../../../{SOURCE_FILE})"
    relation_lines = "\n".join(f"- `{sid}`" for sid in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** Haskell第3章记述耶稣堂圣依纳爵小堂的大祭坛方案在Tirso Gonzalez于1687年接任耶稣会总会长后重新推进，竞赛中选择Pozzo的方案；1695年5月Gonzalez作出最终决定，Pozzo全面负责该祭坛。第92–93页还描述祭坛的工艺与表现圣依纳爵生平、奇迹的浅浮雕。本卡用描述性暂题指向这一特定项目；原书没有在本处给出完工日期、现存状态或馆藏定位。{source_link}

**English:** Chapter 3 says that the great altar project for the Chapel of St Ignatius in the Gesù resumed after Tirso Gonzalez became Jesuit General in 1687; Pozzo’s plan was selected in the competition. Gonzalez made a final decision in May 1695 and Pozzo was put in charge of the altar. Pages 92–93 also describe its craftsmanship and bas-reliefs of St Ignatius’s life and miracles. This card uses a descriptive working title for that specific project; this passage supplies no completion date, survival status, or collection location. {source_link}

### 题名与身份范围

- 中文描述性暂题：耶稣堂圣依纳爵小堂大祭坛方案。
- English descriptive working title: Great Altar Project for the Chapel of St Ignatius in the Gesù.
- 对象边界：指本段所述的Gesù圣依纳爵小堂祭坛项目；不与Pietro da Cortona较早的祭坛方案合并，也不与另一座S. Ignazio教堂中的祭坛混同。完工和存世状态不由计划、竞赛或装饰细节推定。

## 关系与证据

### 关系记录

当前没有新增正式关系。以下7条直接S2关系候选继续待S6逐条核对；其中雕塑方案的放弃、作者限定及作品组成保持各自范围：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-defined great altar work candidate in the Gesù in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_alignments = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate = candidate_by_id[CANDIDATE_ID]
    alignment = candidate_alignments[CANDIDATE_ID]
    assert candidate.get("suggested_type") == "work"
    assert candidate.get("canonical_name") == "Great altar planned for the St Ignatius chapel in the Gesù"
    assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    assert len(manifest_targets) <= 1
    registered = bool(manifest_targets) and alignment.get("ku_id") == KU_ID and CARD_REL in accepted_paths and card_path.exists()
    if registered:
        assert len(manifest_targets) == 1 and manifest_targets[0].get("name_en") == NAME_EN
        assert card_path.read_text(encoding="utf-8-sig") == make_card()
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 7 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and not alignment.get("ku_id") and not card_path.exists() and CARD_REL not in accepted_paths
    assert not any(
        row.get("type") == "work" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "The Gesù great altar project already exists as a work KU"

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
    normalized_source = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for item in QUOTES:
        assert " ".join(item["quote"].split()) in normalized_source, item["source_span"]

    planned_alignment = [dict(row) for row in alignments]
    planned_alignment_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_alignment_by_id[CANDIDATE_ID]["ku_id"] = KU_ID
    planned_alignment_by_id[CANDIDATE_ID]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; completion and survival remain unasserted."
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
        "### S4 work：Gesù圣依纳爵小堂大祭坛方案登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`（`{GROUP}`）登记为[大祭坛方案知识卡](../../../{CARD_REL})。"
        "S3按Haskell第3章第92–93页确定其为Gesù圣依纳爵小堂的特定祭坛项目，与Pietro da Cortona的较早祭坛方案及S. Ignazio教堂内另一祭坛保持边界。正文记录资金与赞助权、竞赛、1695年决定及Pozzo负责等书内说法；卡片不补出完工日期、现存状态或馆藏定位。"
        "7条直接S2关系候选仍待S6，未新增正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### work：Gesù圣依纳爵小堂大祭坛方案 S4 登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}` → [作品卡](../units/works/gesu-st-ignatius-great-altar-project.md)。采用描述性暂题；本章记录方案、竞赛和祭坛内部细节，未据此补写完工或存世状态。7条直接关系候选继续待S6，未新增正式关系。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    planned_accepted = "\n".join(accepted_lines[:insert_at] + [f"- {CARD_REL}"] + accepted_lines[insert_at:]) + "\n"

    if args.dry_run:
        print(f"S4 work dry-run passed: {GROUP} -> {KU_ID}")
        print(f"direct relation candidates={len(direct_relations)}; source span=ch.3 pp.92-93; type=work project")
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
