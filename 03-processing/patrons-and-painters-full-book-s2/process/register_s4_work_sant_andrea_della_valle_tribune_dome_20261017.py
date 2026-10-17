from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-work-sant-andrea-tribune-dome-decoration-20261017"
CANDIDATE = "cand-5064"
GROUP = "workgrp-2c7580b60f39a4"
KU_ID = "units/works/s-andrea-della-valle-tribune-dome-decoration"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "谷地圣安德烈堂祭坛席与穹顶装饰项目"
NAME_EN = "Decoration of the tribune and dome of S. Andrea della Valle"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
SOURCE_SPAN = "lines 76–81; print p. 72"
RELATION_STATEMENTS = {
    "st-chp3-secii-l74-81-decoration-major-baroque-achievement",
    "st-chp3-secii-l74-81-largest-single-artist-commission-so-far",
    "st-chp3-secii-l74-81-theatines-not_part_of_commission_decisions",
    "st-chp3-secii-l74-81-lanfranco-completed-task-by-1628",
    "st-chp3-secii-l74-81-domenichino-completed-task-by-1628",
    "st-chp3-secii-l74-81-montalto-retained-decoration-control",
    "st-chp3-secii-l74-81-montalto-grandiose-decoration-plans",
}


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 72.",
                "location": "第3章，印刷页72；OCR L76–81。",
                "sentence_summary": (
                    "哈斯克尔先叙述 Montalto 对祭坛席与穹顶的委托安排，后述 Domenichino 获得工作、"
                    "Lanfranco 获得穹顶并与其分担装饰；作者称两位画家至1628年已完成各自任务，"
                    "并评价圣安德烈堂装饰是当时最重要的巴洛克成就。"
                ),
                "original_quotes": [
                    {
                        "source_span": "line 76; print p. 72",
                        "text": "had reserved the main features of the decoration for himself",
                    },
                    {
                        "source_span": "line 77; print p. 72",
                        "text": "by far the largest commission of its kind yet given to a single artist",
                    },
                    {
                        "source_span": "line 78; print p. 72",
                        "text": "Domenichino was given the job",
                    },
                    {
                        "source_span": "line 78; print p. 72",
                        "text": "Lanfranco should at least be given the dome",
                    },
                    {
                        "source_span": "line 81; print p. 72",
                        "text": "By 1628, when both artists had completed their tasks",
                    },
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": SOURCE_SPAN,
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "[第3章 p.72](../../../02-sources/02-Markdown/03_CHP-3_sec_ii.md)（L76–81）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔叙述的谷地圣安德烈堂祭坛席与穹顶装饰项目。约1616年，枢机 Montalto 曾承诺把整个祭坛席与穹顶交由 Lanfranco；后来 Domenichino 争取并获得装饰工作，Montalto 又坚持至少将穹顶交给 Lanfranco，最终两位画家分担委托。哈斯克尔称两人至1628年已完成各自任务。此记录呈现委托范围和分配变化，不把初始承诺写成最终安排，也不把整项委托等同于 Lanfranco 的单件穹顶壁画。哈斯克尔称圣安德烈堂装饰为当时最重要的巴洛克成就，这是作者的评价。{source_link}

**English:** This unit records Haskell’s account of the decoration project for the tribune and dome of S. Andrea della Valle. Around 1616, Cardinal Montalto promised the entire tribune and dome to Lanfranco; Domenichino later sought and received the decorative commission, after which Montalto insisted that Lanfranco receive at least the dome. The two painters ultimately shared the commission, and Haskell says both had completed their respective tasks by 1628. This record preserves the changing scope and allocation: the initial promise is not treated as the final arrangement, and the broader commission is not equated with Lanfranco’s individual dome fresco. Haskell calls the church’s decoration the most important Baroque achievement to that point; this is the author’s evaluation. {source_link}

### 对象边界

本卡记录祭坛席与穹顶装饰的整体委托；已登记的[兰弗兰科圣安德烈堂穹顶壁画](lanfranco-dome-fresco-s-andrea-della-valle.md)为其中单独描述的作品对象，二者不合并。地点见[谷地圣安德烈堂](../places/sant-andrea-della-valle.md)。卡内链接用于导航，不代替 S6 对作品组成、委托、作者和地点关系的正式审查。

## 关系与证据

当前没有已登记的正式关系。7条关系候选 `{', '.join(sorted(RELATION_STATEMENTS))}` 留待 S6 逐条审查；两条未标为 relation candidate 的聚合陈述继续作为 S2 断言保留。Baroque 术语候选 `cand-4500` 尚未完成 S4，本卡不提前建立对应关系。未新增 S5 enrichment。
"""


def insert_accepted_path(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S. Andrea della Valle decoration work in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert candidate_map[CANDIDATE].get("suggested_type") == "work"
    target = decisions[CANDIDATE]
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "work"
        and "tribune" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".casefold()
        and "s. andrea della valle" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".casefold()
        for row in manifest
    ), "same overall decoration work appears to exist already; inspect before proceeding"

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    source_quotes = (
        "had reserved the main features of the decoration for himself",
        "by far the largest commission of its kind yet given to a single artist",
        "Domenichino was given the job",
        "Lanfranco should at least be given the dome",
        "By 1628, when both artists had completed their tasks",
    )
    assert all(" ".join(quote.split()) in source_text for quote in source_quotes)

    endpoint_targets = {
        "cand-1876": "units/persons/alessandro-peretti-montalto",
        "cand-1359": "units/persons/giovanni-lanfranco",
        "cand-0934": "units/persons/domenichino",
        "cand-2565": "units/institutions/theatines",
    }
    assert all(decisions[cid].get("ku_id") == target_ku for cid, target_ku in endpoint_targets.items())
    assert decisions["cand-5065"].get("ku_id") == "units/works/lanfranco-dome-fresco-s-andrea-della-valle"

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    direct = {
        row["statement_id"]: row for row in statements.values()
        if row.get("subject_candidate_id") == CANDIDATE
        or row.get("object_candidate_id") == CANDIDATE
    }
    assert RELATION_STATEMENTS.issubset(direct)
    assert all(direct[sid].get("qualifiers", {}).get("relation_candidate") is True for sid in RELATION_STATEMENTS)
    aggregate_claims = {
        "st-chp3-secii-l74-81-church-completed-by-1628",
        "st-chp3-secii-l74-81-compromise-shared-commission-and-enmity",
    }
    assert aggregate_claims.issubset(direct)
    assert all(direct[sid].get("qualifiers", {}).get("relation_candidate") is False for sid in aggregate_claims)
    assert decisions["cand-4500"].get("decision") == "new" and not decisions["cand-4500"].get("ku_id")

    planned_alignment = [dict(row) for row in alignments]
    mapped = [
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(mapped) == 1
    mapped[0]["ku_id"] = KU_ID
    mapped[0]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    mapped[0]["resolution_note"] += f" S4 registration: source-backed multi-artist decoration work group {GROUP} maps to {KU_ID}; its artist-specific dome work remains separate and all formal relations remain for S6."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_text += f"""

<a id="{ANCHOR}"></a>

### S4 work：谷地圣安德烈堂祭坛席与穹顶装饰项目（{DATE}）

单成员 S3 作品组 `{GROUP}`（`{CANDIDATE}`）映射至[圣安德烈堂祭坛席与穹顶装饰项目作品卡](../../../04-knowledge/units/works/s-andrea-della-valle-tribune-dome-decoration.md)。第3章 p.72 记录 Montalto 的初始承诺及后来委托分配变化：Domenichino 获得装饰工作，Lanfranco 获得穹顶部分，两位画家分担委托；哈斯克尔称两人至1628年完成各自任务。初始承诺不等于最终分配。本卡记录整体项目，与已登记的 Lanfranco 穹顶壁画作品分别处理；正式作品组成及人物、地点、术语关系留待 S6。

关联的 {len(RELATION_STATEMENTS)} 条关系候选留待 S6；两条聚合陈述未标为 relation candidate，仍作为 S2 断言保留。`cand-4500` 巴洛克术语候选尚待 S4；未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_text = result_text.rstrip() + (
        f"\n\n### S4 work：谷地圣安德烈堂祭坛席与穹顶装饰项目（{DATE}）\n\n"
        f"`{CANDIDATE}` 映射至[项目作品卡](../units/works/s-andrea-della-valle-tribune-dome-decoration.md)。"
        "卡片区分 Montalto 的初始承诺、Domenichino 与 Lanfranco 后来的分工，以及已单独登记的 Lanfranco 穹顶壁画；"
        f"{len(RELATION_STATEMENTS)} 条关系候选留待 S6，`cand-4500` 术语端点仍待 S4。未新增正式关系或 S5 补足。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} is the complete single-member S3 work group {GROUP}")
        print(f"verified {len(source_quotes)} source quotations, {len(endpoint_targets)} mapped endpoints, and a separate Lanfranco dome work")
        print(f"S6 relation candidates preserved: {len(RELATION_STATEMENTS)}; aggregate S2 claims preserved: {len(aggregate_claims)}")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; accepted path unique")
        print("planned writes: one bilingual work card, accepted.yml, ku-manifest.csv, one alignment mapping, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
