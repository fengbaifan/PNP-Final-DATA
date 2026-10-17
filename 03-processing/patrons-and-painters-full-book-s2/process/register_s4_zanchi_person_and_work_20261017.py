from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

PERSON_GROUP = "new-person:antonio-zanchi-df48b8d0ff"
PERSON_CANDIDATES = ("cand-2834",)
PERSON_KU = "units/persons/antonio-zanchi"
PERSON_CARD = "04-knowledge/units/persons/antonio-zanchi.md"

WORK_GROUP = "workgrp-09d947ea36bdd8"
WORK_CANDIDATES = ("cand-2835", "cand-7670")
WORK_KU = "units/works/antonio-zanchi-moses-striking-rock-bergamo"
WORK_CARD = "04-knowledge/units/works/antonio-zanchi-moses-striking-rock-bergamo.md"

PERSON_RELATIONS = {
    "st-chp8-p218-zanchi-described-as-venetian",
    "st-chp8-p218-zanchi-no-fee-and-return-terms",
    "st-chp8-p218-zanchi-agrees-to-terms",
    "st-chp8-p218-zanchi-site-visit-and-venice-permission",
    "st-chp8-p218-zanchi-canvas-sent",
    "st-chp8-p218-letters-urge-zanchi-to-hurry",
    "st-chp8-p218-zanchi-canvas-completed-four-months",
    "st-chp8-p218-zanchi-receives-825-ducats",
}
WORK_RELATIONS = {
    "st-chp8-p218-zanchi-selected-for-moses-rock",
    "st-chp8-p218-experts-set-price-if-accepted",
    "st-chp8-p218-zanchi-canvas-sent",
    "st-chp8-p218-zanchi-canvas-completed-four-months",
    "st-chp8-p218-committee-deliberates-on-zanchi-canvas",
    "st-chp8-p218-committee-accepts-zanchi-canvas",
    "st-chp8-p218-zanchi-receives-825-ducats",
}


def evidence(source_file: str, location: str, source_span: str, summary: str, quotes: list[tuple[str, str]]) -> dict:
    return {
        "citation": "Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this printing 2006).",
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [
            {"source_span": span, "text": quote} for span, quote in quotes
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": source_span,
        },
    }


def card_text(fields: dict, body: str) -> str:
    frontmatter = yaml.safe_dump(fields, allow_unicode=True, sort_keys=False, width=120)
    return f"---\n{frontmatter}---\n\n{body.strip()}\n"


def make_person_card() -> str:
    source8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
    source9 = "02-sources/02-Markdown/09_CHP-9_intro.md"
    source10 = "02-sources/02-Markdown/10_CHP-10_intro.md"
    index = "02-sources/03-Index/03-1-Index-MD/UVWXYZ.md"
    fields = {
        "title": "安东尼奥·赞基（Antonio Zanchi）",
        "name_en": "Antonio Zanchi",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            evidence(source8, "第8章；印刷页218；OCR L84", "line 84; print p. 218",
                     "Haskell以全名称 Antonio Zanchi 为年轻的威尼斯画家，并记述其获选绘制《Moses striking the Rock》。",
                     [("line 84", "the young Venetian, Antonio Zanchi, was accepted and required to paint Moses striking the Rock")]),
            evidence(source9, "第9章；印刷页251；OCR L114", "line 114; print p. 251",
                     "Haskell以姓氏 Zanchi 将其列入在威尼斯装饰艺术中取得成功的画家；书后索引将该页归入 Antonio Zanchi 主项。",
                     [("line 114", "The artists with the greatest success—Zanchi, Lazzarini, Balestra, Dorigny, Bambini and others—")]),
            evidence(source10, "第10章；印刷页294；OCR L295", "line 295; print p. 294",
                     "Haskell称画家 Pietro Negri 为 Zanchi 的学生；索引将该处定位至 Antonio Zanchi 主项。",
                     [("line 295", "Pietro Negri, a pupil of Zanchi.")]),
            evidence(index, "书后索引；UVWXYZ.csv#171", "index entry UVWXYZ.csv#171",
                     "索引以 Zanchi, Antonio 为主项，汇集第8章 p.218、第9章 p.251 与第10章 p.294。",
                     [("UVWXYZ.csv#171", "| Zanchi, Antonio |  |  |  | 218, 251, 294 |")]),
        ],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-antonio-zanchi",
    }
    body = f"""## 内容

### 描述

**中文：** Haskell 第8章 p.218 以全名 Antonio Zanchi 称其为年轻的威尼斯画家，并记述他获选绘制《Moses striking the Rock》。第9章 p.251 以姓氏 Zanchi 提及其在威尼斯装饰艺术中的声望；第10章 p.294 称 Pietro Negri 为 Zanchi 的学生。三处均由书后索引主项 `Zanchi, Antonio` 定位。本卡只登记书内人物身份与相关叙述，不补充外部生平。中文名为项目工作音译。[第8章 p.218](../../../{source8})（L84）；[第9章 p.251](../../../{source9})（L114）；[第10章 p.294](../../../{source10})（L295）；[书后索引](../../../{index})（UVWXYZ.csv#171）

**English:** In Chapter 8, p.218, Haskell names Antonio Zanchi as a young Venetian painter and says he was selected to paint *Moses striking the Rock*. Chapter 9, p.251, refers to Zanchi by surname among painters successful in Venetian decoration; Chapter 10, p.294, calls Pietro Negri a pupil of Zanchi. The index groups all three references under `Zanchi, Antonio`. This card records the identity and account in the book without adding an external biography. The Chinese display name is a working transliteration. [Chapter 8, p.218](../../../{source8}) (L84); [Chapter 9, p.251](../../../{source9}) (L114); [Chapter 10, p.294](../../../{source10}) (L295); [Index](../../../{index}) (UVWXYZ.csv#171)

### 名称与身份定位

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Antonio Zanchi | 第8章 p.218 L84；索引 UVWXYZ.csv#171 |
| 索引形式 | Zanchi, Antonio | 书后索引 UVWXYZ.csv#171 |
| 跨章索引定位 | p.218、251、294 | 书后索引 UVWXYZ.csv#171；正文第8、9、10章 |
| 中文名性质 | 项目工作音译 | 项目命名 |

### 关系候选

以下8条直接 S2 关系候选保留待 S6 审查；本卡不将其登记为正式关系：`{", ".join(sorted(PERSON_RELATIONS))}`。
"""
    return card_text(fields, body)


def make_work_card() -> str:
    source = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
    index = "02-sources/03-Index/03-1-Index-MD/UVWXYZ.md"
    fields = {
        "title": "安东尼奥·赞基《摩西击石》（Antonio Zanchi, Moses striking the Rock, Bergamo）",
        "name_en": "Moses striking the Rock (Antonio Zanchi, Bergamo)",
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            evidence(source, "第8章；印刷页218–219；OCR L84–87", "lines 84, 86–87; print pp. 218–219",
                     "Haskell记述 Antonio Zanchi 获选绘制《Moses striking the Rock》，作品在威尼斯完成后由委托方接受，Zanchi 获付825杜卡特。",
                     [("line 84", "Antonio Zanchi, was accepted and required to paint Moses striking the Rock"),
                      ("lines 86–87", "In fact, it was completed within four months ... Eventually it was accepted with obvious enthusiasm ... Zanchi was paid the considerable fee of 825 ducats")]),
            evidence(index, "书后索引；UVWXYZ.csv#172–174", "index entries UVWXYZ.csv#172–174",
                     "索引将《Moses striking the Rock》及 Zanchi 在 Bergamo 的 S. Maria Maggiore 工作、付款定位至第8章 pp.218–219。",
                     [("UVWXYZ.csv#172", "| Zanchi, Antonio |  | Moses striking the Rock |  | 218, 219 |"),
                      ("UVWXYZ.csv#173", "| Zanchi, Antonio |  | work in S. Maria Maggiore, Bergamo |  | 218, 219 |"),
                      ("UVWXYZ.csv#174", "| Zanchi, Antonio |  | work in S. Maria Maggiore, Bergamo | payment | 218 |")]),
        ],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-antonio-zanchi",
    }
    body = f"""## 内容

### 描述

**中文：** 本卡登记 Haskell 第8章 pp.218–219 记述的 Antonio Zanchi《Moses striking the Rock》画作。书中称 Zanchi 获选绘制该画，在威尼斯完成后由 Bergamo 的委托方接受，并获付825杜卡特；书后索引将题名与其在 S. Maria Maggiore 的工作、付款条目定位于同一页段。原书未确认作品此后的保存地点或现存状态。题名中文为项目工作译名。[第8章 pp.218–219](../../../{source})（L84、86–87）；[书后索引](../../../{index})（UVWXYZ.csv#172–174）

**English:** This card records Antonio Zanchi’s painting *Moses striking the Rock* as described on pp.218–219 of Chapter 8. Haskell says Zanchi was selected to paint it, completed it in Venice, and received 825 ducats after the Bergamo committee accepted it. The index locates the title, his work at S. Maria Maggiore, and the payment entry in the same page range. The book does not establish the work’s later location or present state. The Chinese title is a working translation. [Chapter 8, pp.218–219](../../../{source}) (L84, 86–87); [Index](../../../{index}) (UVWXYZ.csv#172–174)

### 作品身份与范围

- S3 将索引候选 `cand-2835` 与正文候选 `cand-7670` 归入同一作品组 `{WORK_GROUP}`：索引题名、正文所述画家、题材及 Bergamo 委托语境相互对应。
- 索引将作品定位在 S. Maria Maggiore, Bergamo；正文未指出画作原定安置于该堂哪一具体门或墙面，也未说明此后的去向。
- 不与索引中归于 Ottavio Vannini、位于 p.212 的另一条同题作品子目合并；相同题材名称不足以证明是同一画作。

### 关系候选

直接涉及本作品的7条 S2 关系候选留待 S6 审查；本卡不将其登记为正式关系：`{", ".join(sorted(WORK_RELATIONS))}`。
"""
    return card_text(fields, body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S3 Antonio Zanchi person and painting groups as S4 KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    expected = {
        **{cid: ("person", PERSON_GROUP) for cid in PERSON_CANDIDATES},
        **{cid: ("work", WORK_GROUP) for cid in WORK_CANDIDATES},
    }
    for cid, (kind, group) in expected.items():
        candidate, alignment = candidate_by_id[cid], alignment_by_id[cid]
        assert candidate["suggested_type"] == kind
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == group
    assert candidate_by_id["cand-2834"]["index_entry_id"] == "UVWXYZ.csv#171"
    assert candidate_by_id["cand-2835"]["index_entry_id"] == "UVWXYZ.csv#172"
    assert not any(row.get("ku_id") in {PERSON_KU, WORK_KU} for row in manifest)
    assert not (ROOT / PERSON_CARD).exists() and not (ROOT / WORK_CARD).exists()
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert PERSON_CARD not in accepted_text and WORK_CARD not in accepted_text

    chapter8 = (ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md").read_text(encoding="utf-8-sig")
    chapter9 = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    chapter10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    index_text = (ROOT / "02-sources/03-Index/03-1-Index-MD/UVWXYZ.md").read_text(encoding="utf-8-sig")
    assert "the young Venetian, Antonio Zanchi" in chapter8
    assert "Moses striking the Rock" in chapter8 and "825 ducats" in chapter8
    assert "The artists with the greatest success—Zanchi" in chapter9
    assert "a pupil of Zanchi" in chapter10
    assert "| Zanchi, Antonio |  |  |  | 218, 251, 294 |" in index_text
    assert "| Zanchi, Antonio |  | Moses striking the Rock |  | 218, 219 |" in index_text
    statements = sync.load_statements()
    relation_ids = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and ({row.get("subject_candidate_id"), row.get("object_candidate_id")}
             & set(PERSON_CANDIDATES + WORK_CANDIDATES))
    }
    assert relation_ids == PERSON_RELATIONS | WORK_RELATIONS

    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id")}
    for cid in PERSON_CANDIDATES:
        planned_by_id[cid]["ku_id"] = PERSON_KU
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {PERSON_GROUP} to {PERSON_KU}."
    for cid in WORK_CANDIDATES:
        planned_by_id[cid]["ku_id"] = WORK_KU
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {WORK_GROUP} to {WORK_KU}."

    planned_manifest = list(manifest)
    planned_manifest.extend([
        {"ku_id": PERSON_KU, "type": "person", "canonical_name": "安东尼奥·赞基", "name_en": "Antonio Zanchi", "source_task": TASK, "card_path": PERSON_CARD},
        {"ku_id": WORK_KU, "type": "work", "canonical_name": "安东尼奥·赞基《摩西击石》", "name_en": "Moses striking the Rock (Antonio Zanchi, Bergamo)", "source_task": TASK, "card_path": WORK_CARD},
    ])
    accepted_lines = accepted_text.splitlines()
    for card_path in sorted((PERSON_CARD, WORK_CARD)):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card_path),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card_path}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    old_audit = "审计警告中的4,562条待登记 `decision=new` alignment 行，含4,547条候选决定映射（4,476组）和15条外部身份记录。"
    new_audit = "审计警告中的4,559条待登记 `decision=new` alignment 行，含4,544条候选决定映射（4,474组）和15条外部身份记录。"
    assert old_audit in result_text
    result_text = result_text.replace(old_audit, new_audit, 1)
    result_text += (
        "\n\n<a id=\"s4-antonio-zanchi\"></a>\n\n### S4 person/work：Antonio Zanchi 与《Moses striking the Rock》（2026-10-17）\n\n"
        f"`cand-2834`（UVWXYZ.csv#171）登记至[Antonio Zanchi 人物卡](../units/persons/antonio-zanchi.md)：第8章 p.218 全名、索引同一主项的 p.251 和 p.294 定位支持跨章人物归并。"
        f"`cand-2835`（UVWXYZ.csv#172）与 `cand-7670` 按既有 S3 作品组 `{WORK_GROUP}` 共映射至[《Moses striking the Rock》作品卡](../units/works/antonio-zanchi-moses-striking-rock-bergamo.md)；索引题名、正文画家及 Bergamo 委托语境相符。"
        "人物8条、作品7条直接关系候选继续待 S6；未写正式关系，未改 relations.csv。作品与索引中 Vannini 的同题子目保持区分。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4 person/work：Antonio Zanchi 与《Moses striking the Rock》（2026-10-17）\n\n"
        f"人物候选 `cand-2834` 保持 S3 组 `{PERSON_GROUP}`，登记至[Antonio Zanchi 人物卡](../../../{PERSON_CARD})。第8章 p.218 L84 明称 Antonio Zanchi；索引主项 UVWXYZ.csv#171 汇集 p.218、251、294，分别对应第8章委托叙述、第9章画家声望叙述与第10章 Negri 师承句。人物卡只登记书内身份与所载语境，不补充外部生平。\n\n"
        f"作品候选 `cand-2835`（索引 UVWXYZ.csv#172）与 `cand-7670`（第8章正文）保持同一 S3 组 `{WORK_GROUP}`，登记至[作品卡](../../../{WORK_CARD})。索引题名、p.218–219 的 Antonio Zanchi 委托叙事、Bergamo 的 S. Maria Maggiore 页面定位及付款条目相互吻合；原书未说明原定安装的具体墙面或作品后续去向。索引另有归于 Ottavio Vannini 的 p.212 同题画作，未与本对象合并。\n\n"
        f"人物直接关系候选（8条）：{', '.join(sorted(PERSON_RELATIONS))}。作品直接关系候选（7条）：{', '.join(sorted(WORK_RELATIONS))}。两集合共有画布递送、完成、付款等交叠叙述；全部留待 S6 逐条审查，本轮未写 `relations.csv`，未新增 backlog。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    person_card = make_person_card()
    work_card = make_work_card()
    if args.dry_run:
        print("S4 Antonio Zanchi person/work group dry-run passed")
        print(f"{PERSON_CANDIDATES[0]} -> {PERSON_KU}; {', '.join(WORK_CANDIDATES)} -> {WORK_KU}")
        print(f"direct relation candidates: person={len(PERSON_RELATIONS)}, work={len(WORK_RELATIONS)}; no formal relations will be written")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        print("no files changed")
        return 0

    for relpath, content in ((PERSON_CARD, person_card), (WORK_CARD, work_card)):
        card_path = ROOT / relpath
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {PERSON_KU} and {WORK_KU}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
