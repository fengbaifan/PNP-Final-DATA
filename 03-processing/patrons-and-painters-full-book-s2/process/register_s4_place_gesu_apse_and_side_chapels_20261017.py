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
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SPECS = [
    {
        "candidate": "cand-5001",
        "group": "sg3-place-cand-5001",
        "ku_id": "units/places/apse-of-gesu",
        "name_zh": "耶稣堂后殿空间",
        "name_en": "Apse of the Gesù",
        "anchor": "s4-place-gesu-apse-20261017",
        "line": 8,
        "quote": "plans were made for the apse to be covered with mosaics.",
        "summary": (
            "第3章称已有以马赛克覆盖耶稣堂后殿的计划，并在同段另行称述祭坛席与 High Altar 的家族专属装饰。"
        ),
        "relations": ["st-chp3-seciv-l75-81-apse-after-oliva"],
    },
    {
        "candidate": "cand-5002",
        "group": "sg3-place-cand-5002",
        "ku_id": "units/places/side-chapels-of-gesu",
        "name_zh": "耶稣堂侧礼拜堂群",
        "name_en": "Side Chapels of the Gesù",
        "anchor": "s4-place-gesu-side-chapels-20261017",
        "line": 9,
        "quote": "They were thus compelled to concentrate on the side-chapels.",
        "summary": (
            "第3章以复数 side-chapels 称呼耶稣堂的一组侧礼拜堂，叙述耶稣会在主装饰工程停滞后转向这些空间。"
        ),
        "relations": [
            "st-chp3-secii-l6-17-jesuits-concentrated-on-side-chapels",
            "st-chp3-secii-l6-17-pious-ladies-paid-chapel-structure",
            "st-chp3-secii-l6-17-side-chapels-attracted-pious-ladies",
            "st-chp3-secii-l115-123-chapel-patronage",
            "st-chp20-p399-hibbard-jesuit-control",
            "st-chp20-p399-nadal-engravings-commission-and-influence",
        ],
    },
]


def make_card(spec: dict) -> str:
    source_end = "9" if spec["candidate"] == "cand-5001" else "11"
    frontmatter = {
        "title": f"{spec['name_zh']}（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": "place",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 66.",
                "location": f"第3章，印刷页66；来源 OCR L{spec['line']}–{source_end}。",
                "sentence_summary": spec["summary"],
                "original_quotes": [
                    {
                        "source_span": f"OCR line {spec['line']}; print p. 66",
                        "text": spec["quote"],
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": f"OCR lines {spec['line']}–{source_end}; printed p. 66",
                },
            }
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{spec['anchor']}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "[第3章 p.66](../../../02-sources/02-Markdown/03_CHP-3_sec_ii.md)"

    if spec["candidate"] == "cand-5001":
        body = f"""## 内容

### 空间身份

**中文：** 本卡记录哈斯克尔在第3章称为耶稣堂 apse 的内部建筑空间。第66页称，Cardinal Alessandro Farnese 去世前已有以马赛克覆盖后殿的计划。同段另行称述 Farnese 将祭坛席与 High Altar 的装饰保留给家族。本卡保留原书分别命名的对象，不据此断言它们边界互不重叠，也不补写现状。{source_link}（L8–9）

**English:** This unit records the interior architectural space Haskell calls the Gesù’s apse. On p. 66 he says plans had been made to cover it with mosaics before Cardinal Alessandro Farnese died. In the same passage, he separately names the tribune and High Altar as objects whose adornment Farnese reserved to his family. This card preserves the source’s distinct names without asserting non-overlapping boundaries or adding a present-day condition. {source_link} (L8–9)

### 对象边界

后殿与已登记的[祭坛席地点卡](tribune-of-gesu.md)分别对应原书的 apse 与 tribune；二者的精确空间关系未在本卡建立。[罗马耶稣堂](gesu-rome.md)作为主建筑身份入口。

## 关系与证据

当前没有已登记的正式关系。S2 关系候选 `{spec['relations'][0]}` 记载后殿完成时间与 Oliva 去世的对应，留待 S6 核验端点和证据。本卡不新增 S5 enrichment。
"""
    else:
        body = f"""## 内容

### 空间身份

**中文：** 本卡记录哈斯克尔在耶稣堂早期装饰叙述中统称的侧礼拜堂群。第66页以复数 side-chapels 指称这些内部空间，并称主装饰工程停滞后，耶稣会转而集中于此。此为集合性地点记录；原文未列全体成员，本卡不补列具体礼拜堂或认定群内成员。{source_link}（L9–11）

**English:** This unit records the collective group of chapels Haskell refers to as the Gesù’s side-chapels in his account of the church’s early decoration. On p. 66 he uses the plural “side-chapels” for these interior spaces and says the Jesuits turned their efforts to them after the main decoration stalled. The source does not enumerate the complete set; this card does not identify specific members. {source_link} (L9–11)

### 对象边界

这是原书复数总称对应的集合性地点，不替代已单独登记的具体礼拜堂卡，也不据此建立具体成员或包含关系。[罗马耶稣堂](gesu-rome.md)仅作身份导航入口。

## 关系与证据

当前没有已登记的正式关系。以下 S2 关系候选留待 S6 逐条核对：{', '.join(spec['relations'])}。未新增 S5 enrichment。
"""
    return f"---\n{fm}---\n\n{body}"


def insert_accepted_paths(text: str) -> str:
    lines = text.splitlines()
    for spec in SPECS:
        card_rel = f"04-knowledge/{spec['ku_id']}.md"
        assert f"- {card_rel}" not in lines
        insert_at = next(
            (
                i for i, line in enumerate(lines)
                if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel
            ),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Gesù apse and side-chapels place groups in S4.")
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
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    statements = {row["statement_id"]: row for row in sync.load_statements()}

    for spec in SPECS:
        cid = spec["candidate"]
        candidate = candidate_map[cid]
        alignment = decisions[cid]
        card_rel = f"04-knowledge/{spec['ku_id']}.md"
        card_path = ROOT / card_rel
        assert candidate.get("suggested_type") == "place"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == spec["group"]
        assert candidate.get("candidate_source_ref", "").endswith(f"#L{spec['line']}")
        group_rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert [row["candidate_id"] for row in group_rows] == [cid]
        assert not card_path.exists(), f"target card already exists: {card_path}"
        assert card_rel not in accepted_text
        assert not any(row.get("ku_id") == spec["ku_id"] or row.get("card_path") == card_rel for row in manifest)
        assert not any(
            row.get("type") == "place" and row.get("name_en", "").casefold() == spec["name_en"].casefold()
            for row in manifest
        ), f"duplicate English place name: {spec['name_en']}"
        assert " ".join(spec["quote"].split()) in source_text, f"source quote missing for {cid}"
        for sid in spec["relations"]:
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            mentioned = {
                statement.get("subject_candidate_id"),
                statement.get("object_candidate_id"),
                *statement.get("qualifiers", {}).get("mentioned_candidate_ids", []),
            }
            assert cid in mentioned, f"{sid} is not linked to {cid}"

    planned_alignment = [dict(row) for row in alignments]
    for spec in SPECS:
        mapped = [row for row in planned_alignment if row.get("candidate_id") == spec["candidate"] and not row.get("external_source")]
        assert len(mapped) == 1
        mapped[0]["ku_id"] = spec["ku_id"]
        mapped[0]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{spec['anchor']}"
        mapped[0]["resolution_note"] += (
            f" S4 registration: source-backed place group {spec['group']} maps to {spec['ku_id']}; "
            "specific spatial boundaries and formal relations remain unasserted pending S6."
        )

    planned_manifest = list(manifest)
    for spec in SPECS:
        planned_manifest.append({
            "ku_id": spec["ku_id"],
            "type": "place",
            "canonical_name": spec["name_zh"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": f"04-knowledge/{spec['ku_id']}.md",
        })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_text += f"""

<a id="{SPECS[0]['anchor']}"></a>
<a id="{SPECS[1]['anchor']}"></a>

### S4 place：耶稣堂后殿与侧礼拜堂群（{DATE}）

按 S3 的两个单成员地点组分别登记：`cand-5001`（`{SPECS[0]['group']}`）→ [耶稣堂后殿地点卡](../../../04-knowledge/{SPECS[0]['ku_id']}.md)；`cand-5002`（`{SPECS[1]['group']}`）→ [耶稣堂侧礼拜堂群地点卡](../../../04-knowledge/{SPECS[1]['ku_id']}.md)。第3章 p.66 分别以 apse、tribune 和 side-chapels 指称后殿、祭坛席及侧礼拜堂群；本批保持这些名称对应的身份边界，不将后殿与祭坛席断言为边界互不重叠的空间，也不将复数侧礼拜堂群拆成未被逐一识别的成员。

后殿与祭坛席的术语区分另经外部资料交叉核对：《耶稣堂》官方介绍分别称述 catino dell'abside 与 tribuna 的装饰；Nayyar 的同行评审研究亦分别讨论 apse vault 与 tribune patronage rights。此核对只支持保留原书分别命名的参照，不补写精确建筑边界或现状：[官方教堂介绍](https://www.chiesadelgesu.org/documenti/presentazione_chiesa_del_gesu_roma.pdf)；[Nayyar, “Joshua and the Jesuits: The Battle for the Apse of the Gesù”](https://brill.com/view/journals/jjs/3/2/article-p211_3.pdf)。

后殿关系候选 `{SPECS[0]['relations'][0]}` 与侧礼拜堂群的 {len(SPECS[1]['relations'])} 条候选关系留待 S6；未具名继承人 `cand-5007`、决策参与者群体 `cand-5427` 和 pious ladies 术语候选 `cand-5008` 维持原 S3 待决状态。已有单体礼拜堂 KU 与侧礼拜堂群分开保留，本批不推定具体成员或建立包含边。未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_text = result_text.rstrip() + (
        f"\n\n### S4 place：耶稣堂后殿与侧礼拜堂群（{DATE}）\n\n"
        "两个独立 S3 地点组分别登记为耶稣堂后殿和侧礼拜堂群 KU；原书对 apse、tribune 与 side-chapels 的分别命名得到保留，"
        "不据此断言后殿与祭坛席的精确边界，也不拆分未具名的群体成员。后殿 1 条、侧礼拜堂群 6 条关系候选留待 S6；"
        "cand-5007、cand-5427 与 cand-5008 保持待决。未新增关系或 S5 补足。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    planned_accepted = insert_accepted_paths(accepted_text)
    cards = [(ROOT / f"04-knowledge/{spec['ku_id']}.md", make_card(spec)) for spec in SPECS]

    if args.dry_run:
        print("dry-run passed: both candidates are complete, single-member S3 place groups")
        print("source quotations verified: cand-5001, cand-5002")
        print(f"S6 relation candidates preserved: {sum(len(s['relations']) for s in SPECS)}")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; accepted paths unique")
        print("planned writes: two bilingual place cards, accepted.yml, ku-manifest.csv, two alignment mappings, process record, result")
        return 0

    for path, content in cards:
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: cand-5001 -> {SPECS[0]['ku_id']}; cand-5002 -> {SPECS[1]['ku_id']}; "
        f"manifest={len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
