from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

ITEMS = {
    "cand-6826": {
        "group": "workgrp-514a6d48f6643e",
        "ku_id": "units/works/guido-reni-rape-of-helen",
        "card_rel": "04-knowledge/units/works/guido-reni-rape-of-helen.md",
        "type": "work",
        "name_zh": "圭多·雷尼《海伦被劫》",
        "name_en": "The Rape of Helen by Guido Reni",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "source": {
            "location": "第7章；印刷页184；OCR L175–176",
            "span": "lines 175–176; print p. 184",
            "summary": "Haskell 称 Louis Phélipeaux de la Vrillière 在1635年前某时购入 Guido Reni 的《The Rape of Helen》，并说该画数年前曾由 Marie de Medici 购得；作品创作日期和后续流传未由此段确定。",
            "quotes": [
                ("lines 175–176", "Some time before 1635 he acquired a large and famous picture by Guido Reni of The Rape of Helen"),
                ("line 176", "which had been purchased by Marie de Medici a few years"),
            ],
        },
        "body": """### 描述

**中文：** 本卡对应 Haskell 第7章 p.184 所称 Guido Reni 的《The Rape of Helen》。作者称 Louis Phélipeaux de la Vrillière 在1635年前某时购入此画，并说 Marie de Medici 数年前曾购得该画。原书此段没有确定作品创作日期、现存版本或后续流传；中文题名为项目工作译名。[第7章 p.184](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L175–176）

**English:** This card represents Guido Reni’s *The Rape of Helen* as described on p.184 of Chapter 7. Haskell says that Louis Phélipeaux de la Vrillière acquired the painting some time before 1635 and that Marie de Medici had purchased it some years earlier. The passage does not establish the work’s creation date, surviving version, or later provenance. The Chinese title is a project working translation. [Chapter 7, p.184](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md) (L175–176)

### 名称与身份边界

- 对应 S3 候选 `cand-6826`（第7章 p.184 正文提及），保持独立 work 组 `workgrp-514a6d48f6643e`；书内以作品名和 Guido Reni 归属识别。
- 与既有[Pietro da Cortona《Rape of Helen》](pietro-da-cortona-rape-of-helen.md)分开：该卡对应另一位作者的作品，题名相近不表示同一对象。
- 中文题名仅为便于阅读的项目工作译名；本卡不补充来源之外的作品身份或现状。

### 关系与证据

`st-chp7-p184-i17` 是本卡唯一直接 S2 关系候选，留待 S6 判断购藏关系、方向和时间限定；本卡未新增正式关系。
""",
    },
    "cand-6828": {
        "group": "sg3-term-cand-6828",
        "ku_id": "units/terms/la-vrilliere-heroic-antique-themes",
        "card_rel": "04-knowledge/units/terms/la-vrilliere-heroic-antique-themes.md",
        "type": "term",
        "name_zh": "La Vrillière 所选古代英雄题材",
        "name_en": "Heroic Themes from the World of Antiquity Chosen by La Vrillière",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "source": {
            "location": "第7章；印刷页184；OCR L174–175",
            "span": "lines 174–175; print p. 184",
            "summary": "Haskell 将 La Vrillière 所选择的古代题材描述为崇高、英雄性的题材，并置于与 Mazarin 收藏趣味的比较中。该表述限定于作者对具体收藏者选择的讨论。",
            "quotes": [
                ("lines 174–175", "La Vrillière chose from the artists he employed themes taken from the high, heroic world of antiquity."),
            ],
        },
        "body": """### 描述

**中文：** 本卡记录 Haskell 对 La Vrillière 所选题材的描述：取自古代“崇高、英雄性的世界”。该说法出现在作者与 Mazarin 收藏趣味的对照中，指向书内特定语境，不作为普遍适用的艺术门类或既定知识层级。中文显示名是项目描述性译名。[第7章 p.184](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L174–175）

**English:** This card records Haskell’s description of the subjects chosen by La Vrillière as drawn from the “high, heroic world of antiquity.” The phrase occurs in the author’s comparison of this patron’s taste with Mazarin’s; it is limited to that source context and is not treated as a universal art category or a pre-established knowledge hierarchy. The Chinese display name is a project descriptive translation. [Chapter 7, p.184](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md) (L174–175)

### 语境与边界

- 对应 S3 候选 `cand-6828`，保持 source-local term 组 `sg3-term-cand-6828`。
- 仅表达 Haskell 对这段收藏叙述中题材选择的描述；不推定某一件作品、某个艺术家群体或普遍风格分类。

### 关系与证据

`st-chp7-p184-i16` 是与 La Vrillière 人物卡直接关联的 S2 关系候选，留待 S6；本卡未新增正式关系。
""",
    },
    "cand-7462": {
        "group": "sg3-term-cand-7462",
        "ku_id": "units/terms/later-painters-inspired-by-venetians-patronised-by-van-den-einden",
        "card_rel": "04-knowledge/units/terms/later-painters-inspired-by-venetians-patronised-by-van-den-einden.md",
        "type": "term",
        "name_zh": "受威尼斯画家影响并受范登埃因登赞助的后辈画家",
        "name_en": "Later Painters Inspired by Venetian Artists and Patronised by Ferdinand van den Einden",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "source": {
            "location": "第8章；印刷页208；OCR L59",
            "span": "line 59; print p. 208",
            "summary": "Haskell 称 Ferdinand van den Einden 属于较年轻一代，并特别赞助受威尼斯画家启发的后辈画家；该群体在此处未逐一列名。",
            "quotes": [
                ("line 59", "But, being of a younger generation, it was the later painters, inspired by the Venetians, whom he specially patronised."),
            ],
        },
        "body": """### 描述

**中文：** 本卡记录第8章 p.208 中 Haskell 对 Ferdinand van den Einden 所赞助的一类后辈画家的描述：这些画家受威尼斯画家启发。原文没有在此列出该群体成员；本卡不补列名单，不把该称谓转为正式组织或完整艺术史群体。中文显示名是项目描述性译名。[第8章 p.208](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L59）

**English:** This card records Haskell’s description on p.208 of Chapter 8 of the later painters patronised by Ferdinand van den Einden as inspired by Venetian artists. The passage does not name the group’s members. This card supplies no membership list and does not turn the description into a formal organization or a complete art-historical group. The Chinese display name is a project descriptive translation. [Chapter 8, p.208](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md) (L59)

### 语境与边界

- 对应 S3 候选 `cand-7462`，保持 source-local term 组 `sg3-term-cand-7462`。
- “较年轻一代”以原文比较语境保留，不推断具体出生年代；成员身份未由该段逐一确定。

### 关系与证据

`st-chp8-p208-ferdinand-sponsored-later-venetian-inspired-painters` 是与 Ferdinand 人物卡直接关联的 S2 关系候选，留待 S6；本卡未新增正式关系。
""",
    },
}


def make_card(item: dict) -> str:
    source = item["source"]
    frontmatter = {
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": item["type"],
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK,
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote} for span, quote in source["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["source_file"],
                "source_span": source["span"],
            },
        }],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{fm}---\n\n## 内容\n\n{item['body']}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three source-backed direct work/term endpoints in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    decisions = {
        r["candidate_id"]: r for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    statements = sync.load_statements()

    for cid, item in ITEMS.items():
        row = decisions[cid]
        assert candidate_by_id[cid]["suggested_type"] == item["type"]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        members = [
            r for r in alignments
            if r.get("candidate_id") and not r.get("external_source") and r["decision"] == "new"
            and sync.get_group(r.get("resolution_note", "")) == item["group"]
        ]
        assert [r["candidate_id"] for r in members] == [cid]
        assert not (ROOT / item["card_rel"]).exists()
        assert item["card_rel"] not in accepted
        assert not any(r.get("ku_id") == item["ku_id"] or r.get("card_path") == item["card_rel"] for r in manifest)
        assert not any(
            r.get("type") == item["type"]
            and (r.get("name_en", "").casefold() == item["name_en"].casefold()
                 or r.get("canonical_name", "").casefold() == item["name_zh"].casefold())
            for r in manifest
        )
        text = " ".join((ROOT / item["source_file"]).read_text(encoding="utf-8-sig").split())
        for _, quote in item["source"]["quotes"]:
            assert " ".join(quote.split()) in text, (cid, quote)
        direct = [
            s for s in statements
            if cid in (s.get("subject_candidate_id"), s.get("object_candidate_id"))
        ]
        assert len(direct) == 1 and direct[0].get("qualifiers", {}).get("relation_candidate") is True
    assert decisions["cand-6820"]["decision"] == "undecided"
    assert decisions["cand-6846"]["decision"] == "undecided"
    assert any(r.get("ku_id") == "units/works/pietro-da-cortona-rape-of-helen" for r in manifest)

    planned_alignment = [dict(r) for r in alignments]
    planned_by_id = {
        r["candidate_id"]: r for r in planned_alignment
        if r.get("candidate_id") and not r.get("external_source")
    }
    planned_manifest = list(manifest)
    for cid, item in ITEMS.items():
        planned_by_id[cid]["ku_id"] = item["ku_id"]
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."
        planned_manifest.append({
            "ku_id": item["ku_id"], "type": item["type"], "canonical_name": item["name_zh"],
            "name_en": item["name_en"], "source_task": TASK, "card_path": item["card_rel"],
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 348 and totals["registered_members"] == 452
    assert totals["pending_groups"] == 4490 and totals["pending_members"] == 4566
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    audit_old = "4,584条待登记 `decision=new` alignment 行，含4,569条候选决定映射（4,493组）和15条外部身份记录。"
    audit_new = "4,581条待登记 `decision=new` alignment 行，含4,566条候选决定映射（4,490组）和15条外部身份记录。"
    assert audit_old in result_text
    result_text = result_text.replace(audit_old, audit_new, 1)
    stale = "其他 new work/term 端点仍待 S4。未新增正式关系。"
    updated = "cand-6826、cand-6828、cand-7462 三个直接 work/term 端点现已登记；本批未新增正式关系。"
    assert stale in result_text
    result_text = result_text.replace(stale, updated, 1)

    people_cards = {
        "04-knowledge/units/persons/ferdinand-van-den-einden.md": (
            "（术语端点 `cand-7462`：new，待 S4）",
            "（术语端点 [cand-7462](../terms/later-painters-inspired-by-venetians-patronised-by-van-den-einden.md)：new，已登记）",
        ),
        "04-knowledge/units/persons/louis-phelipeaux-de-la-vrilliere.md": (
            "（古代英雄题材术语 `cand-6828`：new，待 S4）",
            "（古代英雄题材术语 [cand-6828](../terms/la-vrilliere-heroic-antique-themes.md)：new，已登记）",
        ),
    }
    people_card_texts = {}
    for rel, (old, new) in people_cards.items():
        text = (ROOT / rel).read_text(encoding="utf-8-sig")
        assert text.count(old) == 1, (rel, old)
        people_card_texts[rel] = text.replace(old, new)
    louis_rel = "04-knowledge/units/persons/louis-phelipeaux-de-la-vrilliere.md"
    assert people_card_texts[louis_rel].count("（Reni《The Rape of Helen》") == 0
    # Update the separate work endpoint to its new KU without implying an accepted relation.
    old_work_status = "（Guido Reni《The Rape of Helen》`cand-6826`：new，待 S4）"
    new_work_status = "（Guido Reni《The Rape of Helen》[cand-6826](../works/guido-reni-rape-of-helen.md)：new，已登记）"
    assert people_card_texts[louis_rel].count(old_work_status) == 1
    people_card_texts[louis_rel] = people_card_texts[louis_rel].replace(old_work_status, new_work_status)

    process_note = (
        "\n\n### S4 work/term：La Vrillière 与 van den Einden 的直接端点（2026-10-17）\n\n"
        "`cand-6826` 登记为[Guido Reni《The Rape of Helen》作品卡](../../../04-knowledge/units/works/guido-reni-rape-of-helen.md)；"
        "它与既有 Pietro da Cortona 同题作品分开。`cand-6828` 登记为[La Vrillière 古代英雄题材术语卡](../../../04-knowledge/units/terms/la-vrilliere-heroic-antique-themes.md)，"
        "`cand-7462` 登记为[van den Einden 赞助的受威尼斯影响后辈画家术语卡](../../../04-knowledge/units/terms/later-painters-inspired-by-venetians-patronised-by-van-den-einden.md)。"
        "三者均依 S3 new 分组各登记一个 KU；两个 term 只记录 Haskell 的书内描述，不建立涌现层级、普遍类别或完整成员名单。"
        "三条直接关系候选留待 S6；La Vrillière palace `cand-6820` 与绘画系列 `cand-6846` 仍为 undecided，本批未写 relations.csv。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_note = (
        "\n\n### S4 work/term：La Vrillière 与 van den Einden 的直接端点（2026-10-17）\n\n"
        "`cand-6826`→[Guido Reni《The Rape of Helen》作品卡](../units/works/guido-reni-rape-of-helen.md)；"
        "`cand-6828`→[古代英雄题材术语卡](../units/terms/la-vrilliere-heroic-antique-themes.md)；"
        "`cand-7462`→[受威尼斯影响的后辈画家术语卡](../units/terms/later-painters-inspired-by-venetians-patronised-by-van-den-einden.md)。"
        "三条直接关系候选留待 S6，未新增正式关系；相似题名的 Pietro da Cortona《Rape of Helen》保持独立。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig") + process_note
    result_text += result_note

    accepted_lines = accepted.splitlines()
    for item in sorted(ITEMS.values(), key=lambda x: x["card_rel"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > item["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {item['card_rel']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("S4 direct work/term dry-run passed: cand-6826 (work), cand-6828 and cand-7462 (terms)")
        print("all three S3 new groups have one candidate and one traceable book statement; work title collision is separated by artist")
        print("La Vrillière palace and painting-series candidates remain undecided; relations are not written")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}")
        print(f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; new alignment rows pending=4,581")
        print("no files changed")
        return 0

    for item in ITEMS.values():
        (ROOT / item["card_rel"]).write_text(make_card(item), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    for rel, text in people_card_texts.items():
        (ROOT / rel).write_text(text, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: 3 work/term KUs registered; manifest={len(planned_manifest)}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
