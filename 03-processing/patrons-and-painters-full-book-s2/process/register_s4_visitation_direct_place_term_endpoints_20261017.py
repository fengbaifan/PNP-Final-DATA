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
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
ANCHOR = "s4-visitation-direct-place-term-endpoints-20261017"

ITEMS = (
    {
        "candidate_id": "cand-5038",
        "group": "sg3-place-cand-5038",
        "ku_id": "units/places/chiesa-nuova-chapel-of-the-visitation",
        "card_rel": "04-knowledge/units/places/chiesa-nuova-chapel-of-the-visitation.md",
        "type": "place",
        "name_zh": "新堂圣母访亲小堂",
        "name_en": "Chapel of the Visitation at Chiesa Nuova",
        "candidate_name": "Chapel of the Visitation at Chiesa Nuova",
        "candidate_source_ref": "chp-3:03_CHP-3_sec_ii:l40-52#L49",
        "location": "第3章；印刷页69；L49",
        "source_span": "L49; print p. 69",
        "quote": "altar painting to be placed in the Chapel of the Visitation",
        "summary_cn": "第3章称一幅祭坛画预定置于 Chapel of the Visitation；S3按该段的 Chiesa Nuova 局部语境识别其建筑归属。这里只登记具名内部空间，不扩写建筑平面或现状。",
        "summary_en": "Chapter 3 says an altar painting was intended for the Chapel of the Visitation; S3 identifies its building association from the local Chiesa Nuova context. This card registers the named internal space only and adds no floor plan or present-day status.",
        "body_cn": "本卡对应第3章所称 Chapel of the Visitation。该段将此小堂置于 Chiesa Nuova 的局部叙述中，并称一幅祭坛画预定安置于此。中文显示名为工作译名；此地点卡与该祭坛画作品卡分立，不推断确切空间结构或今日状态。",
        "body_en": "This card represents the Chapel of the Visitation named in Chapter 3. The local passage places it in the Chiesa Nuova context and says an altar painting was intended for it. The Chinese display name is a working translation. This place unit remains distinct from the altar-painting work and does not infer the chapel's precise spatial layout or present-day status.",
        "relation_ids": (
            "st-chp3-secii-l40-52-barocci-painted-commission",
            "st-chp3-secii-l40-52-oratorians-commission-visitation-altarpiece",
        ),
        "relation_mode": "qualifier",
    },
    {
        "candidate_id": "cand-12314",
        "group": "sg3-term-cand-12314",
        "ku_id": "units/terms/richeome-fresco-subject-devotional-function",
        "card_rel": "04-knowledge/units/terms/richeome-fresco-subject-devotional-function.md",
        "type": "term",
        "name_zh": "里肖姆所论壁画题材的敬虔功能",
        "name_en": "Devotional Function of Fresco Subject Matter in Richeôme’s Account",
        "candidate_name": "Subject matter of the frescoes discussed by Louis Richeôme",
        "candidate_source_ref": "chp-3:03_CHP-3_sec_ii:l33-38#L35",
        "location": "第3章；印刷页68；L35",
        "source_span": "L35; print p. 68",
        "quote": "Attention must be concentrated exclusively on the subject-matter of the frescoes, which should be read like a sermon, more effective because paint lasted and words vanished.",
        "summary_cn": "Haskell转述 Richeôme 的主张：敬虔注意力应集中于壁画题材，并将其读作讲道；这是该段特定论述，不推广为普遍图像学规则。",
        "summary_en": "Haskell reports Richeôme's view that devotional attention should focus on fresco subject matter and read it like a sermon; this is limited to the argument in this passage and is not generalized as a universal iconographic rule.",
        "body_cn": "本卡记录 Haskell 所转述的 Richeôme 观点：壁画题材应成为敬虔注意力的集中对象，并可像讲道一样阅读。该术语只指本段具名论述；具体壁画题材未在此列明，也不构成所有宗教艺术的普遍规则。中文名称为描述性译名。",
        "body_en": "This card records the view attributed by Haskell to Richeôme: fresco subject matter should focus devotional attention and may be read like a sermon. The term is limited to the named argument in this passage; no particular fresco subject is identified, and the statement is not treated as a rule for all religious art. The Chinese name is a descriptive translation.",
        "relation_ids": ("st-chp3-secii-l33-38-richeome-focused-devotion-on-fresco-subject",),
        "relation_mode": "direct",
    },
    {
        "candidate_id": "cand-12316",
        "group": "sg3-term-cand-12316",
        "ku_id": "units/terms/richeome-ornamental-forms-and-devotion",
        "card_rel": "04-knowledge/units/terms/richeome-ornamental-forms-and-devotion.md",
        "type": "term",
        "name_zh": "里肖姆所述不触及敬虔的装饰形式",
        "name_en": "Ornamental Forms Described by Richeôme as Not Touching Devotion",
        "candidate_name": "Ornamental forms Richeôme says do not touch devotion",
        "candidate_source_ref": "chp-3:03_CHP-3_sec_ii:l33-38#L34",
        "location": "第3章；印刷页68；L34–L35",
        "source_span": "L34-L35; print p. 68",
        "quote": "ne touchent point votre dévotion",
        "summary_cn": "Haskell转引 Richeôme 对装饰形式的判断，称其“不触及”敬虔；该类别含多种建筑及绘画装饰，不指向某一件作品或一所特定教堂。",
        "summary_en": "Haskell quotes Richeôme's judgment that certain ornamental forms do not touch devotion; the category spans architectural and pictorial ornament and does not identify one work or a particular church.",
        "body_cn": "本卡记录 Haskell 所引 Richeôme 对装饰形式的特定判断。该段列及假壁柱、柱式、大理石祭坛、檐口、基座、绘画、浮雕和建筑装饰；“不触及敬虔”是 Richeôme 的立场，不转写为本项目的普遍评价，也不将类别归到某一具体作品或教堂。中文名称为描述性译名。",
        "body_en": "This card records the specific judgment by Richeôme quoted by Haskell about ornamental forms. The passage mentions fake pilasters, columns, marble altars, cornices, pedestals, paintings, reliefs, and architectural ornaments. “Not touching devotion” is Richeôme's position, not a general assessment adopted here; the category is not assigned to a particular work or church. The Chinese name is a descriptive translation.",
        "relation_ids": ("st-chp3-secii-l33-38-richeome-rejected-extravagant-ornament",),
        "relation_mode": "direct",
    },
)


def make_card(item: dict) -> str:
    source = {
        "citation": BOOK_CITATION,
        "location": item["location"],
        "sentence_summary": item["summary_cn"],
        "original_quotes": [{"source_span": item["source_span"], "text": item["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": item["source_span"],
        },
    }
    frontmatter = {
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": item["type"],
        "evidence_status": "source_backed",
        "sources": [source],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    link = f"[第3章书内来源](../../../{SOURCE_FILE})（{item['source_span']}）"
    relation_lines = "\n".join(f"- `{sid}`" for sid in item["relation_ids"])
    body = f"""## 内容

### 描述

**中文：** {item['body_cn']} {link}

**English:** {item['body_en']} {link}

## 关系与证据

### 关系记录

本卡没有新增正式关系。以下S2关系候选仍留待S6裁决：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register one place and two source-local term endpoints in S4.")
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
    statements = sync.load_statements()

    states = []
    for item in ITEMS:
        cid = item["candidate_id"]
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == item["type"]
        assert candidate.get("canonical_name") == item["candidate_name"]
        assert candidate.get("candidate_source_ref") == item["candidate_source_ref"]
        assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == item["group"]
        group_members = {
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        direct = []
        for row in statements:
            if item["relation_mode"] == "direct":
                touches = cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
            else:
                qualifiers = row.get("qualifiers") or {}
                touches = cid in (qualifiers.get("place_candidate_id"), qualifiers.get("work_destination_candidate_id"))
            if touches and (row.get("qualifiers") or {}).get("relation_candidate") is True:
                direct.append(row["statement_id"])
        assert set(direct) == set(item["relation_ids"]), (cid, direct, item["relation_ids"])
        source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, (cid, item["source_span"])

        card_path = ROOT / item["card_rel"]
        targets = [row for row in manifest if row.get("ku_id") == item["ku_id"] or row.get("card_path") == item["card_rel"]]
        assert len(targets) <= 1
        name_matches = [
            row for row in manifest
            if row.get("type") == item["type"]
            and ((row.get("name_en") or "").casefold() == item["name_en"].casefold()
                 or (row.get("canonical_name") or "").casefold() == item["name_zh"].casefold())
        ]
        assert len(name_matches) <= 1
        registered = bool(targets) and alignment.get("ku_id") == item["ku_id"] and item["card_rel"] in accepted_paths and card_path.exists()
        states.append(registered)
        if registered:
            assert len(targets) == 1 and targets[0].get("canonical_name") == item["name_zh"]
            assert card_path.read_text(encoding="utf-8-sig") == make_card(item)
        else:
            assert not targets and not alignment.get("ku_id") and not card_path.exists() and item["card_rel"] not in accepted_paths
            assert not name_matches, (item["type"], item["name_en"])

    if all(states):
        print("ALREADY REGISTERED: 1 place and 2 term groups; 4 relation candidates remain non-formal.")
        return 0
    assert not any(states), "partial S4 batch detected; inspect each card and mapping before proceeding"

    planned_alignment = [dict(row) for row in alignments]
    planned_alignment_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    for item in ITEMS:
        target = planned_alignment_by_id[item["candidate_id"]]
        target["ku_id"] = item["ku_id"]
        target["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."
        planned_manifest.append({
            "ku_id": item["ku_id"], "type": item["type"], "canonical_name": item["name_zh"],
            "name_en": item["name_en"], "source_task": TASK, "card_path": item["card_rel"],
        })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_entries = []
    result_entries = []
    for item in ITEMS:
        process_entries.append(
            f"- `{item['candidate_id']}`（`{item['group']}`）登记为[{item['name_en']}](../../../{item['card_rel']})。"
            f"依据限于第3章 {item['source_span']}；{len(item['relation_ids'])}条相应关系候选仍留待S6。"
        )
        result_entries.append(
            f"- `{item['candidate_id']}` → [知识卡](../{item['card_rel'].split('04-knowledge/units/')[1]})；"
            "身份范围、描述性译名及来源限定见卡片。"
        )
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 place/term：Chiesa Nuova 委托祭坛画的直接端点（2026-10-17）\n\n"
        + "\n".join(process_entries)
        + "\n\n`cand-5038`在两条关系候选的限定中作为预定安置小堂保留；`cand-12314`与`cand-12316`是Richeôme论述中的source-local term。"
        "三组分别映射，不合并地点、作品和术语；所有相关关系候选仍待S6，没有写入正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### place/term：委托祭坛画及Richeôme论述端点 S4 登记（2026-10-17）\n\n"
        + "\n".join(result_entries)
        + "\n其中1个place组和2个term组分别登记；4条直接或地点限定关系候选继续待S6，未新增正式关系。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    accepted_lines = accepted.splitlines()
    for item in sorted(ITEMS, key=lambda row: row["card_rel"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > item["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {item['card_rel']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("S4 direct endpoint dry-run passed: 1 place group + 2 term groups")
        for item in ITEMS:
            print(f"  {item['candidate_id']} -> {item['ku_id']} ({len(item['relation_ids'])} relation candidates)")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; no files changed"
        )
        return 0

    for item in ITEMS:
        (ROOT / item["card_rel"]).write_text(make_card(item), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: 3 groups; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
