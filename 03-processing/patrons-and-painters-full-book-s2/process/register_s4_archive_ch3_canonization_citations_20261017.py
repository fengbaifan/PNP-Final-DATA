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
SOURCE_CH3 = "02-sources/02-Markdown/03_CHP-3_sec_i.md"
SOURCE_BIB = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SPECS = [
    {
        "candidate": "cand-4992",
        "group": "archive-group-ecd7f6180feb",
        "ku_id": "units/archives/ignatius-xavier-canonization-centenary-1923",
        "name_zh": "圣依纳爵与圣方济各·沙勿略封圣三百周年纪念集",
        "name_en": "Remembrances of the Third Centenary of the Canonization of Saints Ignatius of Loyola and Francis Xavier",
        "anchor": "s4-archive-ignatius-xavier-canonization-centenary-20261017",
        "quotes": [
            {
                "location": "第3章，印刷页64，注3；OCR L38。",
                "summary": "脚注列出纪念集的题名、Roma 与 1923 年，并在该段引用语境中提及此文献。",
                "quote": "La Canonizazzione dei Santi Ignazio di Lojola e Francesco Saverio—Ricordi del terzo centenario, Roma 1923",
                "span": "OCR line 38; print p. 64, note 3",
                "source_file": SOURCE_CH3,
            }
        ],
        "relations": ["st-chp3-seci-l35-43-canonization-volume-citation"],
        "paragraph_zh": (
            "本卡记录哈斯克尔第3章注3所列的一卷出版文献。原书引文题名为 "
            "*La Canonizazzione dei Santi Ignazio di Lojola e Francesco Saverio—Ricordi del terzo centenario*，"
            "并列出版地 Roma、年份 1923。题名与出版信息仅按该脚注登记；未据此确认出版者、编者、完整版次或馆藏，也未独立查阅该卷。"
            "中文和英文名称为描述性工作译名，不声称是正式译题。"
        ),
        "paragraph_en": (
            "This unit records a published volume listed in Haskell’s chapter 3, note 3. "
            "The cited title is *La Canonizazzione dei Santi Ignazio di Lojola e Francesco Saverio—Ricordi del terzo centenario*, "
            "with Roma and 1923 given. Title and publication details are recorded only as that note presents them; "
            "publisher, editor, full edition details, and holding institution are not established, and the volume was not independently consulted. "
            "The Chinese and English names are descriptive working translations, not asserted formal translations."
        ),
        "process_note": (
            "cand-4992（archive-group-ecd7f6180feb）映射至[封圣三百周年纪念集 archive 卡]"
            "(../../../04-knowledge/units/archives/ignatius-xavier-canonization-centenary-1923.md)。"
            "第3章 p.64 注3列原题、Roma、1923；题名逐字保留 Haskell 印刷文本中的拼写。原卷与独立目录记录未查阅，"
            "故不补出版者、编者、馆藏或完整版本信息。该脚注关系候选留待 S6。"
        ),
    },
    {
        "candidate": "cand-4993",
        "group": "archive-group-220a5b4072d7",
        "ku_id": "units/archives/redig-de-campos-van-dyck-gesu-article-1936",
        "name_zh": "梵戴克为罗马耶稣堂创作、后于梵蒂冈发现的两幅祭坛画",
        "name_en": "Two Altarpieces by Van Dyck for the Gesù in Rome Rediscovered in the Vatican",
        "anchor": "s4-archive-redig-de-campos-van-dyck-gesu-1936-20261017",
        "quotes": [
            {
                "location": "第3章，印刷页64，注3；OCR L38。",
                "summary": "脚注以 Redig de Campos, 1936 补充该处关于封圣纪念叙述与画作的引文。",
                "quote": "and also Redig de Campos, 1936.",
                "span": "OCR line 38; print p. 64, note 3",
                "source_file": SOURCE_CH3,
            },
            {
                "location": "第21章，印刷页435，书目条目；OCR L1032。",
                "summary": "书目列出作者形式 Redig de Campos, D.、意大利文题名、期刊 Bollettino d’Arte、1936 年、卷 XXX 与页码 150–165。",
                "quote": "Redig de Campos, D.: ‘Intorno a due quadri d’altare di Van Dyck per il Gesù di Roma ritrovati in Vaticano’ in Bollettino d’Arte, 1936, XXX, pp. 150-165.",
                "span": "OCR line 1032; print p. 435",
                "source_file": SOURCE_BIB,
            },
        ],
        "relations": ["st-chp3-seci-l35-43-redig-de-campos-citation"],
        "paragraph_zh": (
            "本卡记录哈斯克尔第3章注3引用并在第21章书目中完整列出的学术论文。书目作者形式为 Redig de Campos, D.，"
            "原题为 *Intorno a due quadri d’altare di Van Dyck per il Gesù di Roma ritrovati in Vaticano*，"
            "刊于 *Bollettino d’Arte*，1936 年，卷 XXX，pp. 150–165。作者缩写按原书保留，不展开姓名；论文未独立查阅。"
            "中文和英文名称为描述性工作译名。"
        ),
        "paragraph_en": (
            "This unit records an academic article cited in Haskell’s chapter 3, note 3 and fully listed in chapter 21. "
            "The bibliography gives the author form as Redig de Campos, D., the original title *Intorno a due quadri d’altare di Van Dyck per il Gesù di Roma ritrovati in Vaticano*, "
            "and publication in *Bollettino d’Arte*, 1936, volume XXX, pp. 150–165. The initials are retained as printed; the author’s name is not expanded, and the article was not independently consulted. "
            "The Chinese and English names are descriptive working translations."
        ),
        "process_note": (
            "cand-4993（archive-group-220a5b4072d7）映射至[Redig de Campos 论文 archive 卡]"
            "(../../../04-knowledge/units/archives/redig-de-campos-van-dyck-gesu-article-1936.md)。"
            "第3章 p.64 注3给出作者姓氏与年份，第21章 p.435 书目条目提供题名、期刊、卷、年份与页码；论文原文未独立查阅。"
            "注释引用关系候选留待 S6，书目条目只作为本卡身份依据。"
        ),
    },
]


def make_card(spec: dict) -> str:
    source_entries = []
    for item in spec["quotes"]:
        source_entries.append({
            "citation": f"{BOOK_CITATION}, {item['location']}.",
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["source_file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{spec['name_zh']}（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": source_entries,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{spec['anchor']}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_links = []
    for item in spec["quotes"]:
        if item["source_file"] == SOURCE_CH3:
            source_links.append("[第3章 p.64 注3](../../../02-sources/02-Markdown/03_CHP-3_sec_i.md#L38)")
        else:
            source_links.append("[第21章 p.435 书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L1032)")
    source_links = list(dict.fromkeys(source_links))
    return f"""---
{fm}---

## 内容

### 文献身份与题名

**中文：** {spec['paragraph_zh']} {'；'.join(source_links)}

**English:** {spec['paragraph_en']} {'; '.join(source_links)}

### 出版与阅读状态

上述题名和出版信息是哈斯克尔提供的书内书目记录。未据书目引注推出文献内容，未登记未见的版次、作者全名、出版者或馆藏信息。

## 关系与证据

当前没有已登记的正式关系。S2 引用候选 {spec['relations'][0]} 留待 S6 核对对应语境及端点；文献内容未独立查读。未新增 S5 enrichment。
"""


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
    parser = argparse.ArgumentParser(description="Register two chapter 3 cited publications as S4 archive KUs.")
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
    statements = {row["statement_id"]: row for row in sync.load_statements()}

    for spec in SPECS:
        cid = spec["candidate"]
        candidate = candidate_map[cid]
        alignment = decisions[cid]
        card_rel = f"04-knowledge/{spec['ku_id']}.md"
        assert candidate.get("suggested_type") == "archive"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == spec["group"]
        group_rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert [row["candidate_id"] for row in group_rows] == [cid]
        assert not (ROOT / card_rel).exists(), f"target card already exists: {card_rel}"
        assert card_rel not in accepted_text
        assert not any(row.get("ku_id") == spec["ku_id"] or row.get("card_path") == card_rel for row in manifest)
        assert not any(
            row.get("type") == "archive" and row.get("name_en", "").casefold() == spec["name_en"].casefold()
            for row in manifest
        ), f"duplicate English archive title: {spec['name_en']}"
        for item in spec["quotes"]:
            source = (ROOT / item["source_file"]).read_text(encoding="utf-8-sig")
            assert " ".join(item["quote"].split()) in " ".join(source.split()), f"source quote missing for {cid}"
        statement = statements[spec["relations"][0]]
        assert statement.get("qualifiers", {}).get("relation_candidate") is True
        assert cid in {
            statement.get("subject_candidate_id"), statement.get("object_candidate_id"),
            *statement.get("qualifiers", {}).get("mentioned_candidate_ids", []),
        }

    planned_alignment = [dict(row) for row in alignments]
    for spec in SPECS:
        mapped = [row for row in planned_alignment if row.get("candidate_id") == spec["candidate"] and not row.get("external_source")]
        assert len(mapped) == 1
        mapped[0]["ku_id"] = spec["ku_id"]
        mapped[0]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{spec['anchor']}"
        mapped[0]["resolution_note"] += (
            f" S4 registration: source-cited archive group {spec['group']} maps to {spec['ku_id']}; "
            "cited document content was not independently consulted and its citation relation remains for S6."
        )

    planned_manifest = list(manifest)
    for spec in SPECS:
        planned_manifest.append({
            "ku_id": spec["ku_id"],
            "type": "archive",
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

### S4 archive：第3章封圣纪念出版物与 Redig de Campos 论文（{DATE}）

按两个独立 S3 archive 组分别登记：{SPECS[0]['process_note']} {SPECS[1]['process_note']}

两项引用关系候选 {SPECS[0]['relations'][0]}、{SPECS[1]['relations'][0]} 留待 S6；对应事件组 cand-4980 尚未登记，本批不预建关系。relations.csv 与 enrichment.jsonl 未变更，也未新增正式关系或 S5 enrichment。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_text = result_text.rstrip() + (
        f"\n\n### S4 archive：两条耶稣堂封圣史文献引用（{DATE}）\n\n"
        "两个单成员 archive 组分别登记为1923年封圣三百周年纪念集与 Redig de Campos 1936年论文；前者仅按第3章脚注书目线索登记，"
        "后者按脚注与第21章书目交叉定位。两项所引文献均未独立查阅，引用关系留待 S6；未新增正式关系或 S5 补足。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    planned_accepted = insert_accepted_paths(accepted_text)
    cards = [(ROOT / f"04-knowledge/{spec['ku_id']}.md", make_card(spec)) for spec in SPECS]

    if args.dry_run:
        print("dry-run passed: both S3 archive groups are complete and map one candidate to one KU")
        print("source quotations verified: ch. 3 p. 64 note 3; ch. 21 p. 435 bibliography")
        print("citation relation candidates preserved: 2; cited documents not independently consulted")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; accepted paths unique")
        print("planned writes: two bilingual archive cards, accepted.yml, ku-manifest.csv, two alignment mappings, process record, result")
        return 0

    for path, content in cards:
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: cand-4992 -> {SPECS[0]['ku_id']}; cand-4993 -> {SPECS[1]['ku_id']}; "
        f"manifest={len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

