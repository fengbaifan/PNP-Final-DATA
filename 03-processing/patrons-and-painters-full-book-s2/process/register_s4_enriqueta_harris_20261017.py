from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import s3_reuse_sassoferrato_candidates_20261017 as summary_tools
import register_s4_valmarana_cluster_batch_20261015 as card_writer

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "new-person:enriqueta-harris-df8f6c82dc"
MEMBERS = ("cand-1292", "cand-11166")
KU_ID = "units/persons/enriqueta-harris"
CARD_PATH = "04-knowledge/units/persons/enriqueta-harris.md"
DATE = "2026-10-17"
ANCHOR = "s3-s4-person-enriqueta-harris-20261017"
NAME_ZH = "恩里克塔·哈里斯"
NAME_EN = "Enriqueta Harris"
DIRECT_RELATIONS = (
    "st-chp7-p190-n1-cite-harris-1960",
    "st-chp7-p190-n1-cite-harris-1961",
    "st-chp7-p190-n5-cite-harris-1957",
    "st-chp7-p190-n5-haskell-acknowledges-harris",
)
SOURCES = (
    card_writer.source(
        "4", "116", "04_CHP-4_sec_ii.md", "296",
        "Enriqueta Harris in Burlington Magazine, 1958, p. 299.",
        "第4章脚注以全名列出 Harris 在 Burlington Magazine 的1958年文章引文定位；该文未在本项目中独立查阅。",
    ),
    card_writer.source(
        "7", "190", "07_CHP-7_sec_i.md", "378",
        "I am most grateful to Enriqueta Harris for this and much further information about del Carpio’s collection.",
        "第7章脚注中 Haskell 以全名致谢 Harris 提供有关 del Carpio 收藏的信息；致谢不独立验证相关信息。",
    ),
    card_writer.source(
        "20", "401", "20_CHP-20Postscript.md", "231",
        "Harris and de Andres.",
        "第20章后记注1仅以 Harris 与 de Andrés 的姓氏形式给出短引；OCR 未显示重音，页图校正记录在 S2。",
    ),
    card_writer.source(
        "21", "412", "21_CHP-21Bibliography.md", "66",
        "See Harris, Enriqueta and Andrés, Gregorio de.",
        "第21章书目交叉指引将 Gregorio de Andrés 条目指向 Harris, Enriqueta 与 Andrés 的联合条目。",
    ),
    card_writer.source(
        "21", "425", "21_CHP-21Bibliography.md", "578",
        "Harris, Enriqueta & Andres, Gregorio de:",
        "第21章书目 p.425 的联合署名列出 Harris, Enriqueta 与 Gregorio de Andrés；本行 OCR 写作 Andres，p.412 交叉指引保留重音形式。被引文章未独立查阅。",
    ),
)
INDEX_SOURCE = {
    "citation": card_writer.BOOK_CITATION,
    "location": "书后索引，H.csv#8；p.190 n.",
    "sentence_summary": "索引以 Harris, Enriqueta 为主项，定位到第7章 p.190 注释。",
    "original_quotes": [{"source_span": "H.csv#8", "text": "Harris, Enriqueta"}],
    "evidence_ref": {
        "doc_id": "patrons-and-painters-index",
        "source_file": "02-sources/03-Index/03-2-Index-CSV/H.csv",
        "source_span": "H.csv#8",
    },
}
DESCRIPTION_ZH = (
    "书后索引以全名 Harris, Enriqueta 指向第7章 p.190 注释。第4章 p.116 注释以全名列出 Harris 的期刊引文；"
    "第7章 p.190 注5又以全名致谢她提供有关 del Carpio 收藏的信息。第20章 p.401 注1仅写 Harris and de Andres；"
    "第21章 p.412 的书目交叉指引把 Andrés 条目指向 Harris, Enriqueta 与 Andrés 的联合项，第21章 p.425 记录相应合署名。"
    "书内姓名及交叉书目线索支持将这些候选归为同一人物；"
    "本卡不独立验证被引文章或致谢所涉信息。"
)
DESCRIPTION_EN = (
    "The book’s index gives the full name Harris, Enriqueta at chapter 7 p. 190 n. Chapter 4 p. 116 n. gives a full-name journal citation, "
    "and chapter 7 p. 190 n. 5 thanks Enriqueta Harris for information about Del Carpio’s collection. Chapter 20 p. 401 n. 1 gives only "
    "“Harris and de Andres,” while the p. 412 bibliography cross-reference points to the joint Harris, Enriqueta and Andrés, Gregorio de entry on p. 425. These in-book name and bibliography "
    "cues support grouping the candidates as one person; this card does not independently verify the cited articles or acknowledged information."
)
BT = chr(96)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_of(note):
    match = re.search(r"(?:^|; )group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label}; found {count}")
    return text.replace(old, new, 1)


def book_source(spec):
    return {
        "citation": card_writer.BOOK_CITATION,
        "location": f"第{spec['chapter']}章，印刷页{spec['page']}；OCR L{spec['lines']}",
        "sentence_summary": spec["summary"],
        "original_quotes": [{"source_span": f"lines {spec['lines']}", "text": spec["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{spec['file']}",
            "source_span": f"lines {spec['lines']}; print p. {spec['page']}",
        },
    }


def make_card():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [INDEX_SOURCE, *[book_source(spec) for spec in SOURCES]],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {DESCRIPTION_ZH}

**English:** {DESCRIPTION_EN}

### 名称

英文规范名依照本书索引和书目写作 Enriqueta Harris。中文显示名“恩里克塔·哈里斯”为项目工作音译，不声称是固定规范译名。

The English name follows the spelling in the book’s index and bibliography. The Chinese rendering 恩里克塔·哈里斯 is a working transliteration for this project, not a claimed standard form.

### 身份边界

本卡仅指索引主项及 p.401 注1姓氏形式经 p.412/p.425 书目交叉线索对齐的 Enriqueta Harris。引用定位和致谢作为书内语境保存；被引文章及所述信息未独立核验。

This card refers only to the Enriqueta Harris identified by the index and the p. 412/p. 425 bibliography cues for the surname form in p. 401 n. 1. Citation locators and the acknowledgment remain in their book context; the cited articles and acknowledged information were not independently verified.

## 关系与证据

本次没有新增正式关系。四条 S2 关系候选留待 S6：{BT}{DIRECT_RELATIONS[0]}{BT}、{BT}{DIRECT_RELATIONS[1]}{BT}、{BT}{DIRECT_RELATIONS[2]}{BT}（书目引用端点及方向待审）；{BT}{DIRECT_RELATIONS[3]}{BT}（Haskell 的致谢陈述）。第4章 p.116 的期刊定位和第20章 p.401 的短引不因出现在注释中就自动转为正式关系。
"""


def update_process(text, stats, manifest_count):
    if f'<a id="{ANCHOR}"></a>' in text:
        return text
    registered_groups = sum(row["registered_groups"] for row in stats.values())
    pending_groups = sum(row["pending_groups"] for row in stats.values())
    pending_members = sum(row["pending_candidates"] for row in stats.values())
    registered_members = sum(row["new_candidates"] for row in stats.values()) - pending_members
    entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Enriqueta Harris 跨章身份组登记（{DATE}）

cand-1292（H.csv#8，第7章 p.190 n.）与 cand-11166（第20章 p.401 n.1）按相同全名／书目交叉线索保留在 {GROUP}，共映射至[恩里克塔·哈里斯人物卡](../../../04-knowledge/units/persons/enriqueta-harris.md)。第4章 p.116 注释与第7章 p.190 n.5 给出全名；第20章短引的 Harris 经第21章 p.412 的书目交叉指引及 p.425 联合署名与 Harris, Enriqueta 相合。人物清单未见同名 KU。归组只解决书内身份，不证明所引文章或致谢信息。

卡片记录索引 H.csv#8、第4章 p.116、第7章 p.190、第20章 p.401 及第21章 pp.412、425 的可定位依据。OCR 中 de Andres 的重音校正沿用 S2 页图记录；没有新增外部身份来源。

四条 S2 关系候选 {BT}{DIRECT_RELATIONS[0]}{BT}、{BT}{DIRECT_RELATIONS[1]}{BT}、{BT}{DIRECT_RELATIONS[2]}{BT}、{BT}{DIRECT_RELATIONS[3]}{BT} 留待 S6；第4章 p.116 的两个期刊定位和第20章 p.401 的短引仍按 citation-only 语境处理。本次未新增正式关系。

S4 当前登记 {registered_groups:,} 组／{registered_members:,} 条候选映射；待登记 {pending_groups:,} 组／{pending_members:,} 条映射；KU 总数 {manifest_count:,}。
"""
    return text.rstrip() + entry


def update_result(text, planned_alignment, planned_manifest, planned_stats):
    candidate_rows = [row for row in planned_alignment if not row.get("external_source")]
    registered_groups = sum(row["registered_groups"] for row in planned_stats.values())
    pending_groups = sum(row["pending_groups"] for row in planned_stats.values())
    pending_members = sum(row["pending_candidates"] for row in planned_stats.values())
    registered_members = sum(row["new_candidates"] for row in planned_stats.values()) - pending_members
    pending_new = sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id"))
    pending_external = sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id") and row.get("external_source"))

    text = replace_once(
        text,
        "S4 已登记526组、映射658条成员候选；尚待登记4,278组、4,320条映射。",
        f"S4 已登记{registered_groups:,}组、映射{registered_members:,}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "S4 top-line counts",
    )
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,545 KU",
        f"| [KU 登记](../tables/ku-manifest.csv) | {len(planned_manifest):,} KU",
        "manifest count",
    )

    warning = re.compile(
        "审计警告中的[\\d,]+条待登记 " + re.escape(BT) + "decision=new" + re.escape(BT) +
        " alignment 行，含[\\d,]+条候选决定映射（[\\d,]+组）和[\\d,]+条外部身份记录。"
    )
    warning_text = (
        f"审计警告中的{pending_new:,}条待登记 {BT}decision=new{BT} alignment 行，含{pending_members:,}条候选决定映射"
        f"（{pending_groups:,}组）和{pending_external:,}条外部身份记录。"
    )
    text, count = warning.subn(warning_text, text, count=1)
    if count != 1:
        raise AssertionError(f"pending-new warning matches: {count}")

    start = text.find("| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |")
    end = text.find("\n\n本轮新增的 archive 身份组包括：", start)
    if start < 0 or end < 0:
        raise AssertionError("S3/S4 type summary table not found")
    text = text[:start] + summary_tools.type_table(planned_stats, candidate_rows) + text[end:]

    heading = "### S3→S4 person：Enriqueta Harris 跨章身份组登记（2026-10-17）"
    if heading not in text:
        text = text.rstrip() + f"""

{heading}

cand-1292 与 cand-11166 共映射至[恩里克塔·哈里斯人物卡](../units/persons/enriqueta-harris.md)。索引主项及第4、7、20、21章的全名／短引／书目线索支持这一书内身份组；不补写外部生平或把引文关系提前正式化。

四条引用与致谢关系候选留待 S6；本次未新增正式关系。被引文章和致谢所涉信息未独立核验。

S4 当前登记 {registered_groups:,} 组／{registered_members:,} 条候选映射；待登记 {pending_groups:,} 组／{pending_members:,} 条映射；KU 总数 {len(planned_manifest):,}。
"""
    return text


def main():
    parser = argparse.ArgumentParser(description="Register Enriqueta Harris as one cross-chapter person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    member_rows = [row for row in alignments if row["candidate_id"] in MEMBERS and not row.get("external_source")]
    card_path = ROOT / CARD_PATH
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    if card_path.exists() and len(member_rows) == len(MEMBERS) and all(row.get("ku_id") == KU_ID for row in member_rows):
        assert CARD_PATH in accepted_text and any(row["ku_id"] == KU_ID for row in manifest)
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}")
        return 0

    assert len(manifest) == 1545, f"unexpected manifest count: {len(manifest)}"
    assert len(alignments) == 12642, f"unexpected alignment count: {len(alignments)}"
    assert sum(1 for row in alignments if row.get("external_source")) == 235
    assert not card_path.exists() and CARD_PATH not in accepted_text
    assert set(candidate_map) >= set(MEMBERS)
    assert len(member_rows) == len(MEMBERS)
    assert all(candidate_map[cid]["suggested_type"] == "person" for cid in MEMBERS)
    assert candidate_map[MEMBERS[0]]["canonical_name"] == "Harris, Enriqueta"
    assert candidate_map[MEMBERS[1]]["canonical_name"].startswith("Enriqueta Harris")
    assert all(row["decision"] == "new" and not row.get("ku_id") and group_of(row["resolution_note"]) == GROUP for row in member_rows)
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    person_names = " ".join(
        row["canonical_name"] + " " + row["name_en"] + " " + row["card_path"]
        for row in manifest if row["type"] == "person"
    ).casefold()
    assert "enriqueta harris" not in person_names

    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in DIRECT_RELATIONS:
                statements[statement["statement_id"]] = statement
    assert set(statements) == set(DIRECT_RELATIONS)
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements.values())
    for spec in SOURCES:
        source_path = ROOT / "02-sources" / "02-Markdown" / spec["file"]
        source_text = source_path.read_text(encoding="utf-8-sig")
        assert spec["quote"] in source_text, f"source excerpt missing from {spec['file']}"
    index_path = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "H.csv"
    assert "Harris, Enriqueta" in index_path.read_text(encoding="utf-8-sig")

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row["candidate_id"] in MEMBERS and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1546
    planned_stats = summary_tools.compute_stats(planned_alignment, candidates)
    assert (
        sum(row["registered_groups"] for row in planned_stats.values()),
        sum(row["pending_groups"] for row in planned_stats.values()),
        sum(row["pending_candidates"] for row in planned_stats.values()),
    ) == (527, 4277, 4318)

    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text = update_process(
        PROCESS_PATH.read_text(encoding="utf-8-sig"),
        planned_stats,
        len(planned_manifest),
    )
    result_text = update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"),
        planned_alignment,
        planned_manifest,
        planned_stats,
    )
    card_text = make_card()

    if args.dry_run:
        print(
            f"dry-run passed: group={GROUP} members={','.join(MEMBERS)} ku={KU_ID} "
            f"registered_groups=527 mapped_candidates=660 pending_groups=4277 pending_candidates=4318 "
            f"manifest_after={len(planned_manifest)} alignment_after={len(planned_alignment)}"
        )
        print("planned writes: card, accepted.yml, ku-manifest.csv, alignment.csv, process/knowledge.md, result")
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        f"applied: group={GROUP} ku={KU_ID} members={len(MEMBERS)} "
        f"registered_groups=527 mapped_candidates=660 pending_groups=4277 pending_candidates=4318 "
        f"manifest={len(planned_manifest)} alignment={len(planned_alignment)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
