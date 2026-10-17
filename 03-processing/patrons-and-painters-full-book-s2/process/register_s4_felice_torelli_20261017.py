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

GROUP = "new-person:felice-torelli-f294b4c634"
MEMBERS = ("cand-2645", "cand-2646")
KU_ID = "units/persons/felice-torelli"
CARD_PATH = "04-knowledge/units/persons/felice-torelli.md"
DATE = "2026-10-17"
ANCHOR = "s3-s4-person-felice-torelli-20261017"
DIRECT_RELATIONS = (
    "st-chp8-p203-belloni-collection",
    "st-chp8-p227-torelli-proposed-scene",
    "st-chp8-p227-torelli-scene-accepted",
    "st-chp19-p389-appendix3-conti-felice-torelli",
)
QUOTES = (
    "owned large numbers of pictures by Giovan Gioseffo dal Sole, Felice Torelli, Crespi and Gambarini,",
    "Felice Torelli wanted to paint a scene from Trojan history2—‘Pyrrhus killing Polyxena in the temple and there will be Chalchas, the soothsayer, and other half-length figures or heads depicting Aeneas and Antinorus-—in fact everything that is needed for the history, and also the tomb of Acliilles, the father of Pyrrhus.’",
    "Carracci, especially in the Galleria Farnese, and Domenichino have totally replaced in his esteem such Bolognese masters of the late Baroque as Monti or Torelli.",
    "APPENDIX 3\nDocuments relating to commissions from Stefano Conti of Lucca to Marcantonio Franceschini and Felice Torelli in thè Biblioteca Governativa, Lucca: MS. 3 299. See Chapter 8, p. 227, notes I and 2.",
)

NAME_ZH = "费利切·托雷利"
NAME_EN = "Felice Torelli"
DESC_ZH = (
    "本书第8章称 Felice Torelli 是画家：第203页把他的作品列入 Giovanni Antonio Belloni 的藏画群，第227页记其提出一幅特洛伊历史题材画；第19章附录又将 Stefano Conti 委托给 Torelli 的文书列入卢卡馆藏档案。第14章 p.348 只写姓氏 Torelli，并由书后索引归在 Felice Torelli 主项下。上述均为书内记载；作品身份、委托文件内容及完成状态依原书范围保留。"
)
DESC_EN = (
    "Chapter 8 identifies Felice Torelli as a painter: p. 203 includes his pictures in Giovanni Antonio Belloni’s collection, and p. 227 records a Trojan-history composition he proposed. The Chapter 19 appendix also lists documents for commissions from Stefano Conti to Torelli in the Lucca repository. Chapter 14 p. 348 gives only the surname Torelli, which the book’s index places under Felice Torelli. These are source-local accounts; the identities of the pictures, the contents of the commission documents, and completion status remain limited to what the book establishes."
)


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
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label}; found {count}")
    return text.replace(old, new, 1)


def make_book_source(chapter, page, filename, lines, quote, summary):
    source = card_writer.source(chapter, page, filename, lines, quote, summary)
    return {
        "citation": card_writer.BOOK_CITATION,
        "location": f"第{chapter}章，印刷页{page}；OCR L{lines}",
        "sentence_summary": source["summary"],
        "original_quotes": [{"source_span": f"lines {lines}", "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{filename}",
            "source_span": f"lines {lines}; print p. {page}",
        },
    }


def make_index_source(row_id, entry, pages):
    return {
        "citation": card_writer.BOOK_CITATION,
        "location": f"书后索引，T.csv#{row_id}",
        "sentence_summary": f"索引将 {entry} 列于页码 {pages}。",
        "original_quotes": [{"source_span": f"T.csv#{row_id}", "text": entry}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters-index",
            "source_file": "02-sources/03-Index/03-2-Index-CSV/T.csv",
            "source_span": f"T.csv#{row_id}",
        },
    }


def make_card():
    sources = [
        make_book_source("8", "203", "08_CHP-8_sec_i.md", "8", QUOTES[0],
                         "哈斯克尔列举 Belloni 所有的画作，称其中包括 Felice Torelli 的作品；本句没有识别具体画作。"),
        make_book_source("8", "227", "08_CHP-8_sec_ii.md", "192", QUOTES[1],
                         "哈斯克尔记述 Torelli 提出一幅特洛伊历史题材画，并另述 Conti 愿意接受此类画作。提出的方案与后来送达的画是否同一件仍未确定。"),
        make_book_source("14", "348", "14_CHP-14_intro.md", "20", QUOTES[2],
                         "哈斯克尔转述 Algarotti 对画家的评价变化；正文只用 Torelli 姓氏，书后索引将此页列在 Felice Torelli 项下。"),
        make_book_source("19", "389", "19_CHP-19Appendix.md", "76–77", QUOTES[3],
                         "附录标题称档案馆藏有关于 Stefano Conti 委托 Marcantonio Franceschini 与 Felice Torelli 的文书；原件未独立查阅，标题不证明每项委托均完成。"),
        make_index_source("108", "Torelli, Felice", "203, 227, 348"),
        make_index_source("109", "Torelli, Felice — commission from Stefano Conti", "389"),
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    process_link = f"../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {DESC_ZH}

**English:** {DESC_EN}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 全名 | Felice Torelli | S1，第8章 p.203 L8；S2，第8章 p.227 L192；S4，第19章 p.389 L76–77 |
| 索引主项 | Torelli, Felice | S5，[全书索引 T.csv#108](../../../02-sources/03-Index/03-2-Index-CSV/T.csv)，列 pp.203、227、348 |
| 索引子项 | commission from Stefano Conti | S6，[全书索引 T.csv#109](../../../02-sources/03-Index/03-2-Index-CSV/T.csv)，p.389 |

中文显示名“费利切·托雷利”为便于阅读的项目工作音译，未声称为既定规范译名。

### 本章相关内容

| 内容 | 书内记载与范围 | 证据 |
|---|---|---|
| Belloni 藏画 | p.203 将 Torelli 与 dal Sole、Crespi、Gambarini 并列为 Belloni 所有画作的作者；未列出具体作品。 | S1，第8章 p.203 L8；未识别作品组 `cand-12006` 仍待证 |
| 提出的画作方案 | p.227 记其想画一幅以 Pyrrhus 杀死 Polyxena 为中心的特洛伊历史画。Conti 愿接受“此类”画作；原书后来提到一幅画送达并询问题材，但没有确认送达物就是该方案。 | S2，第8章 p.227 L192；作品候选 `cand-7798` 仍 `undecided` |
| Algarotti 的评价变化 | p.348 只称 “Torelli”，并将他列为 Algarotti 后来不再推重的晚期巴洛克博洛尼亚画家之一；该页按索引归在本人物主项下。 | S3，第14章 p.348 L20；T.csv#108 |
| 委托文书定位 | 第19章附录标题将 Stefano Conti 对 Torelli 的委托文件定位于 Biblioteca Governativa, Lucca, MS. 3299；附录所列文件及相关信件没有在本项目中独立查阅。 | S4，第19章 p.389 L76–77 |

### 身份边界

本卡只对应索引主项 Torelli, Felice 及其 p.389 委托子目。与索引中另列的 Giacomo Torelli、Giuseppe Torelli 分开；不把 Giuseppe 名下的信件或 Giacomo 的舞台设计并入本人物。

This card covers the indexed Felice Torelli entry and its p. 389 commission subentry. Keep him separate from the separately indexed Giacomo and Giuseppe Torelli; do not merge Giuseppe’s letter or Giacomo’s stage-design work into this person.

## 关系与证据

### 身份与外部链接

本轮按书内完整姓名、跨章索引主项及附录全名锚点登记 source-local person；未新增外部身份记录。

### 关系记录

本卡未新增正式关系。以下直接 S2 关系候选待 S6 逐条审查：[Belloni 藏画]({process_link})（`st-chp8-p203-belloni-collection`；相关作品组 `cand-12006` 仍待证）；[Torelli 提出画作方案]({process_link})（`st-chp8-p227-torelli-proposed-scene`；作品候选 `cand-7798` 的身份及与后来送达画作的对应仍未解决）；[Conti 接受此类方案]({process_link})（`st-chp8-p227-torelli-scene-accepted`；接受此类作品不证明具体方案完成）；[附录中的委托文书]({process_link})（`st-chp19-p389-appendix3-conti-felice-torelli`；档案标题未证明每项委托完成）。没有关系写入 `relations.csv`。
"""


def update_process(text, registered_groups, registered_candidates, pending_groups, pending_candidates, manifest_count):
    if f'<a id="{ANCHOR}"></a>' in text:
        return text
    entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Felice Torelli 跨章身份组登记（{DATE}）

`cand-2645`（T.csv#108，pp.203、227、348）与 `cand-2646`（T.csv#109，p.389 子目）按相同全名及书内全名锚点保留在 `{GROUP}`，映射至 `{KU_ID}`。第8章 p.203、p.227 和第19章附录 p.389 均直接写出 Felice Torelli；第14章 p.348 正文仅写姓氏，但该页列在同一索引主项下。人物清单中没有同名 KU；Giuseppe、Giacomo Torelli 另有独立索引项，未与本组合并。

卡片覆盖 Belloni 的未具名画作群、Torelli 提出的特洛伊历史画方案、Algarotti 评价语境及 Conti 委托文书标题。作品组 `cand-12006` 与提案作品 `cand-7798` 均保持 `undecided`；提案、接受“此类”画作和后来送达的画没有被合并为一件已确认作品。附录所称文书未独立查阅。4条直接 S2 关系候选仍待 S6；没有外部身份字段或正式关系边。

S4 当前登记 {registered_groups} 组／{registered_candidates} 条候选映射；待登记 {pending_groups} 组／{pending_candidates} 条映射；KU 总数 {manifest_count}。
"""
    return text.rstrip() + entry


def update_result(text, planned_alignment, planned_manifest, planned_stats):
    candidate_rows = [row for row in planned_alignment if not row.get("external_source")]
    registered_groups = sum(row["registered_groups"] for row in planned_stats.values())
    pending_groups = sum(row["pending_groups"] for row in planned_stats.values())
    pending_candidates = sum(row["pending_candidates"] for row in planned_stats.values())
    pending_new = sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id"))
    pending_external = sum(1 for row in planned_alignment if row.get("external_source") and row["decision"] == "new" and not row.get("ku_id"))
    mapped = sum(row["new_candidates"] for row in planned_stats.values()) - pending_candidates
    text = replace_once(
        text,
        "S4 已登记524组、映射654条成员候选；尚待登记4,280组、4,324条映射。",
        f"S4 已登记{registered_groups:,}组、映射{mapped:,}条成员候选；尚待登记{pending_groups:,}组、{pending_candidates:,}条映射。",
        "S4 top-line counts",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,543 KU", f"| [KU 登记](../tables/ku-manifest.csv) | {len(planned_manifest):,} KU", "manifest count")
    old_warning = re.compile(
        "审计警告中的[\\d,]+条待登记 " + re.escape("`decision=new`") +
        " alignment 行，含[\\d,]+条候选决定映射（[\\d,]+组）和[\\d,]+条外部身份记录。"
    )
    new_warning = (
        f"审计警告中的{pending_new:,}条待登记 `decision=new` alignment 行，含{pending_candidates:,}条候选决定映射"
        f"（{pending_groups:,}组）和{pending_external:,}条外部身份记录。"
    )
    text, count = old_warning.subn(new_warning, text, count=1)
    if count != 1:
        raise AssertionError(f"pending alignment warning matches: {count}")
    start = text.find("| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |")
    end = text.find("\n\n本轮新增的 archive 身份组包括：", start)
    if start < 0 or end < 0:
        raise AssertionError("S3/S4 type summary table not found")
    text = text[:start] + summary_tools.type_table(planned_stats, candidate_rows) + text[end:]
    text = replace_once(
        text,
        "S4当前登记524组/654条候选映射；待登记4,280组/4,324条；KU总数1,543。",
        f"S4当前登记{registered_groups:,}组/{mapped:,}条候选映射；待登记{pending_groups:,}组/{pending_candidates:,}条；KU总数{len(planned_manifest):,}。",
        "S4 result count",
    )
    heading = "### S3→S4 person：Felice Torelli 跨章身份组登记（2026-10-17）"
    if heading not in text:
        text = text.rstrip() + f"""

{heading}

`cand-2645`、`cand-2646` 共映射至[Felice Torelli 人物卡](../units/persons/felice-torelli.md)。第8章 pp.203、227 与第19章附录 p.389 给出全名；第14章 p.348 的姓氏提及列于同一索引主项下。未与 Giuseppe 或 Giacomo Torelli 合并。

4条直接关系候选留待 S6。未具名 Belloni 藏画组与 Torelli 提案作品仍 `undecided`；不把 Conti 接受此类方案或后来送达的画解释为同一件作品。本卡没有新增正式关系或外部身份记录。

S4 当前登记 {registered_groups:,} 组／{mapped:,} 条候选映射；待登记 {pending_groups:,} 组／{pending_candidates:,} 条映射；KU 总数 {len(planned_manifest):,}。
"""
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the source-local Felice Torelli person group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--refresh-card", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    card_path = ROOT / CARD_PATH
    member_rows = [row for row in alignments if row.get("candidate_id") in MEMBERS and not row.get("external_source")]

    if card_path.exists() and len(member_rows) == len(MEMBERS) and all(row.get("ku_id") == KU_ID for row in member_rows):
        assert CARD_PATH in accepted and any(row["ku_id"] == KU_ID for row in manifest)
        if args.refresh_card:
            refreshed = make_card()
            if card_path.read_text(encoding="utf-8-sig") == refreshed:
                print(f"CARD CURRENT: {CARD_PATH}")
                return 0
            card_path.write_text(refreshed, encoding="utf-8-sig", newline="\n")
            print(f"CARD REFRESHED: {CARD_PATH}")
            return 0
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}")
        return 0

    assert len(manifest) == 1543, f"unexpected manifest count: {len(manifest)}"
    assert len(alignments) == 12642
    assert not card_path.exists() and CARD_PATH not in accepted
    assert len(member_rows) == len(MEMBERS)
    assert all(row["decision"] == "new" and not row.get("ku_id") and group_of(row["resolution_note"]) == GROUP for row in member_rows)
    assert all(next(row for row in candidates if row["candidate_id"] == cid)["suggested_type"] == "person" for cid in MEMBERS)
    assert not any("torelli" in (row["canonical_name"] + " " + row["name_en"] + " " + row["card_path"]).casefold() for row in manifest)
    stats_before = summary_tools.compute_stats(alignments, candidates)
    assert (sum(s["registered_groups"] for s in stats_before.values()), sum(s["pending_groups"] for s in stats_before.values()), sum(s["pending_candidates"] for s in stats_before.values())) == (524, 4280, 4324)

    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("statement_id") in DIRECT_RELATIONS:
                statements[row["statement_id"]] = row
    assert set(statements) == set(DIRECT_RELATIONS)
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements.values())
    source_pairs = (
        ("08_CHP-8_sec_i.md", QUOTES[0]),
        ("08_CHP-8_sec_ii.md", QUOTES[1]),
        ("14_CHP-14_intro.md", QUOTES[2]),
        ("19_CHP-19Appendix.md", QUOTES[3]),
    )
    for filename, quote in source_pairs:
        source = (ROOT / "02-sources" / "02-Markdown" / filename).read_text(encoding="utf-8-sig")
        assert quote in source, f"source quote mismatch: {filename}"

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in MEMBERS and not row.get("external_source"):
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
    assert len(planned_manifest) == 1544
    stats_after = summary_tools.compute_stats(planned_alignment, candidates)
    assert (sum(s["registered_groups"] for s in stats_after.values()), sum(s["pending_groups"] for s in stats_after.values()), sum(s["pending_candidates"] for s in stats_after.values())) == (525, 4279, 4322)
    assert sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id")) == 4337

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    planned_accepted = "\n".join(accepted_lines[:insert_at] + [f"- {CARD_PATH}"] + accepted_lines[insert_at:]) + "\n"
    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"), 525, 656, 4279, 4322, len(planned_manifest))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), planned_alignment, planned_manifest, stats_after)
    card_text = make_card()

    if args.dry_run:
        print(f"dry-run passed: group={GROUP} members=2 direct_relation_candidates=4 registered_groups=525 mapped_candidates=656 pending_groups=4279 pending_candidates=4322 manifest=1544 alignment=12642")
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(f"applied: group={GROUP} ku={KU_ID} members=2 direct_relation_candidates=4 registered_groups=525 mapped_candidates=656 pending_groups=4279 pending_candidates=4322 manifest=1544 alignment=12642")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
