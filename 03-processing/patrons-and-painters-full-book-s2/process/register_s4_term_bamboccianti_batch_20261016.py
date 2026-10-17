from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "sg3-term-bamboccianti"
MEMBERS = ("cand-0173", "cand-0174", "cand-0177")
KU_ID = "units/terms/bamboccianti"
CARD_PATH = "04-knowledge/units/terms/bamboccianti.md"
DATE = "2026-10-16"

DESCRIPTION_ZH = (
    "本书以 Bamboccianti 指与 Pieter van Laer 及其追随者相关的画家群体／艺术现象，并以 bambocciate 指其日常生活题材的小幅画作。"
    "Haskell 将此群体置于17世纪罗马绘画、赞助、市场竞争和评价争议中；他称该名称源自 van Laer 的绰号，并指出其早期作品常描绘普通生活。"
    "本卡记录书内群体称谓，不等同于具体画作、单一绘画类型、正式组织或完整成员名册。中文显示名为工作音译，未确认通行译名。"
)
DESCRIPTION_EN = (
    "In the book, “Bamboccianti” refers to a group of painters and an artistic phenomenon associated with Pieter van Laer and his followers, "
    "while “bambocciate” refers to small pictures of everyday life. Haskell discusses the group in relation to seventeenth-century Roman painting, "
    "patronage, the market, and critical controversy. He says the name derives from van Laer’s nickname and describes early works depicting ordinary life. "
    "This card records the book’s group designation; it is not an individual painting, a single picture type, a formal organization, or a complete membership list. "
    "The Chinese display name is a working transliteration; no established Chinese rendering was confirmed."
)

SOURCES = [
    card_writer.source(
        "5", "132", "05_CHP-5_sec_iii.md", "7",
        "the support that was won by the bambocciate, those little pictures which represented scenes from everyday life",
        "哈斯克尔将 bambocciate 解释为描绘日常生活场景的小幅画作；它与指画家群体的 Bamboccianti 名称区分。",
    ),
    card_writer.source(
        "5", "132", "05_CHP-5_sec_iii.md", "8",
        "The bamboccianti—so called in derision from the nickname given to their deformed leader Pieter van Laer—",
        "哈斯克尔称 Bamboccianti 这一群体名称源自其领袖 Pieter van Laer 的绰号，并说明该称谓带有嘲讽意味。",
    ),
    card_writer.source(
        "5", "141", "05_CHP-5_sec_iii.md", "116",
        "the attacks launched on the baniboccianti by other artists and theorists",
        "OCR 行写作 baniboccianti；S2 提及记录核对页图后将印本词形校为 bamboccianti。哈斯克尔讨论其他艺术家与理论家对该群体的攻击。",
        "S2 提及记录 m-chp5-sec-iii-l115-121-001；本引文保留 OCR 原形，不将校读伪装成 OCR 原文。",
    ),
    card_writer.source(
        "5", "141", "05_CHP-5_sec_iii.md", "117",
        "their considerably cheaper prices",
        "哈斯克尔将较低价格列为竞争与批评语境中的因素；索引子目“prices for pictures”仍指向画家群体相关的市场讨论。",
    ),
    card_writer.source(
        "6", "155", "06_CHP-6_sec_i.md", "107",
        "from the bamboccianti to history painters",
        "第6章将 Bamboccianti 与历史画家并列为 Lorenzo Onofrio Colonna 曾委托作品的艺术家群体。",
    ),
    card_writer.source(
        "8", "207", "08_CHP-8_sec_i.md", "44",
        "bamboccianti and battle painters such as Pieter van Laer, Jan Miel and Borgognone",
        "第8章在 Roomer 收藏和购买语境中以 van Laer、Jan Miel、Borgognone 举例说明此画家类别。",
    ),
    card_writer.source(
        "10", "324", "10_CHP-10_sec_ii.md", "196",
        "the hambocciafiti",
        "该 OCR 行为 hambocciafiti；S2 提及记录 m-s2-ch10-p324-0003 记载据页图校读为 Bamboccianti。这里记录 Pascoli 对该群体的评论。",
        "S2 提及记录 m-s2-ch10-p324-0003；原 OCR 形保留，页图校读另行注明。",
    ),
    card_writer.source(
        "18", "384", "18_CHP-18Conclusion.md", "11",
        "the bamboccianti who hover for a few years on the brink of a new, dignified ‘realism’",
        "后记以此概括 Haskell 对该群体艺术发展和社会语境的解释；保留其评价主体，不作为无争议的艺术史定论。",
    ),
]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label} anchor; found {count}")
    return text.replace(old, new, 1)


def make_card():
    source_rows = []
    for item in SOURCES:
        location_note = item["location_note"]
        source_rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}" + (f"；{location_note}" if location_note else ""),
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}" + (f"; {location_note}" if location_note else ""),
            },
        })
    frontmatter = {
        "title": "巴姆博恰蒂画家群体（Bamboccianti）",
        "name_en": "Bamboccianti",
        "type": "term",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#term-bamboccianti-cross-chapter-s4-registration-2026-10-16",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {DESCRIPTION_ZH}

**English:** {DESCRIPTION_EN}

### 名称与用法

- 原书群体称谓：Bamboccianti；书中也使用 singular bambocciante。词源解释为 Pieter van Laer 的绰号；Haskell 将其称作带有嘲讽色彩的群体名称。（第5章，印刷页132）
- 相关作品词：bambocciate 指描绘日常生活场景的小幅画作，是作品/题材类别，不与画家群体等同。（第5章，印刷页132、141）
- 章内用法：Haskell 将该群体与 van Laer、Jan Miel、Giacomo Borgognone 等画家联系起来，并讨论其市场接受、反对意见和后续影响。此类称谓不构成完整成员名册或正式组织名。（第5章 pp.132–145；第6章 p.155；第8章 p.207）
- OCR 校读：第5章 p.141 的 `baniboccianti` 与第10章 p.324 的 `hambocciafiti` 按既有 S2 提及记录记为据页图校读的 Bamboccianti；卡片的来源摘录仍保留 OCR 原形和校读依据。

### 语境与边界

本卡记录的是索引主项下的艺术家群体/艺术现象。`cand-0174` 的 “attacks on” 和 `cand-0177` 的 “prices for pictures” 是该词条下的主题子目；其中前者讨论对该群体的批评，后者讨论相关市场价格，均不指另一独立实体。具体画作、bambocciate 作品类别、Pieter van Laer 个人以及正式组织 Schildersbent 均保持独立对象。书中没有提供完整成员名单，本卡不补列名单，也不为每位画家推定群体成员身份。

Haskell 在结论中关于该群体接近新现实主义又转为 picturesque sentimentality 的说法，作为作者评价保留；卡片不将其写成无争议的艺术史定论。（第18章，印刷页384）

## 关系与证据

### 关系记录

本批没有建立正式关系。三个候选共对应55条直接 S2 断言，其中26条标记为关系候选，涉及21个不同对端；14条的对端已有 KU，12条仍待相关对象的 S3/S4 去向明确。S6 仍须逐条审查关系类型、方向、语境和证据。

### 身份与外部链接

本卡只记录 Haskell 的书内群体称谓；本批未查询外部术语或身份数据库。
"""
    return f"---\n{fm}---\n\n{body}"


def update_process(text: str) -> str:
    entry = """### term：Bamboccianti 跨章艺术家群体 S4 登记（2026-10-16）

- `cand-0173`（索引主项，B.csv#20）、`cand-0174`（“attacks on”子目，B.csv#21）与 `cand-0177`（“prices for pictures”子目，B.csv#24）同属 S3 组 `sg3-term-bamboccianti`，共同映射到 `units/terms/bamboccianti`。第5章 p.132 说明名称来自 Pieter van Laer 的绰号，并区分指画家群体的 Bamboccianti 与指日常生活题材小画的 bambocciate；第5章 p.141 的攻击/价格子目及第6、8章和结论中的用例都回指同一群体/艺术现象。
- S2 mention notes 区分 artist group、作品类别和风格用法；索引子目不是额外实体。既有人物卡已区分 Pieter van Laer 与 Schildersbent 组织；本卡不把群体名称转为 institution、不创建完整成员表，也不将群体合并为作品类别。第5章 p.141 和第10章 p.324 有 OCR 词形异文；S2 提及账本记录其据页图校读，卡片保留 OCR 原形及该限定。
- 三条组成员对应55条直接 S2 断言，其中26条为关系候选、涉及21个不同对端；14条对端已映射、12条待 S3/S4。未新增正式关系或外部术语核验；候选关系留待 S6。
- 首次表格审计错误及修复过程见前一 term 批次；本卡沿用带出处的叙述式字段，不提前生成 S5 enrichment 属性表。脚本 dry-run 核对三候选组、原文/校读锚点、断言数和对端计数后通过。
- manifest 从1,183增至1,184；累计登记165组、212条候选映射，余4,671组、4,796条映射。term 类型已登记2组/4条候选，余930组/942条候选。

"""
    text = replace_once(text, "### 登记进度与后续\n", entry + "### 登记进度与后续\n", "S4 Bamboccianti insertion")
    text = replace_once(
        text,
        "截至威尼斯贵族阶层术语组登记后，4,836 个当前 `new` 身份组中完成164组，余4,672组；5,008条成员候选中映射209条，余4,799条。",
        "截至 Bamboccianti 术语组登记后，4,836 个当前 `new` 身份组中完成165组，余4,671组；5,008条成员候选中映射212条，余4,796条。",
        "S4 progress counts",
    )
    text = replace_once(
        text,
        "term 类型已登记1组/1条候选，余931组/945条候选。",
        "term 类型已登记2组/4条候选，余930组/942条候选。",
        "S4 term progress",
    )
    return text


def update_result(text: str) -> str:
    text = replace_once(
        text,
        "S4 已登记164组、映射209条成员候选；尚待登记4,672组、4,799条映射。",
        "S4 已登记165组、映射212条成员候选；尚待登记4,671组、4,796条映射。",
        "result current S4 counts",
    )
    text = replace_once(
        text,
        "此前已登记 Cardinal Pier Donato Cesi 人物组；本批新增 `cand-8108` 威尼斯贵族阶层 term 组。",
        "已登记 Cardinal Pier Donato Cesi 人物组和 `cand-8108` 威尼斯贵族阶层 term 组；本批登记 Bamboccianti 三候选 term 组。",
        "result latest S4 summary",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,183 KU；", "| [KU 登记](../tables/ku-manifest.csv) | 1,184 KU；", "manifest count")
    text = replace_once(
        text,
        "以及1个 term（威尼斯贵族阶层）、1个 work、2个 place 组；其余 S4 新组待登记",
        "以及2个 term（威尼斯贵族阶层、Bamboccianti）、1个 work、2个 place 组；其余 S4 新组待登记",
        "manifest type summary",
    )
    entry = """### term：Bamboccianti 跨章艺术家群体 S4 登记（2026-10-16）

`cand-0173`（B.csv#20）、`cand-0174`（“attacks on”子目，B.csv#21）与 `cand-0177`（“prices for pictures”子目，B.csv#24）已共同映射至[Bamboccianti 术语卡](../../04-knowledge/units/terms/bamboccianti.md)。第5章将 Bamboccianti 指向与 Pieter van Laer 相关的画家群体/艺术现象，并将该群体与描绘日常生活场景的 bambocciate 区分；第6、8、10章及结论提供跨章用例。卡片保留 OCR 词形及 S2 页图校读说明，不补完整成员名册；正式关系留待 S6。55条直接 S2 断言中26条为关系候选，14条对端已有 KU、12条待后续 S3/S4。manifest 从1,183增至1,184；累计登记165组、212条候选映射，余4,671组、4,796条。

"""
    return replace_once(
        text,
        "### term：威尼斯贵族阶层跨章术语组 S4 登记（2026-10-16）\n",
        entry + "### term：威尼斯贵族阶层跨章术语组 S4 登记（2026-10-16）\n",
        "result S4 Bamboccianti insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Bamboccianti S3 term group as one source-backed S4 KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(manifest) == 1183, f"unexpected manifest count: {len(manifest)}"
    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["suggested_type"] == "term" and candidate["status"] == "open"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == GROUP
    group_rows = [
        row for row in alignments
        if not row.get("external_source") and row.get("decision") == "new"
        and get_group(row["resolution_note"]) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == list(MEMBERS)
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    card_path = ROOT / CARD_PATH
    assert not card_path.exists(), card_path
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_PATH not in accepted_text
    assert not any(
        row["type"] == "term"
        and any(token in (row["canonical_name"] + " " + row["name_en"]).casefold() for token in ("bamboccianti", "bambocciate"))
        for row in manifest
    ), "same-scope term KU may already exist"

    statements = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if {statement.get("subject_candidate_id"), statement.get("object_candidate_id")} & set(MEMBERS):
                statements.append(statement)
    relation_statements = [
        row for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert (len(statements), len(relation_statements)) == (55, 26), (len(statements), len(relation_statements))
    counterpart_counts = Counter()
    for statement in relation_statements:
        other = (
            statement.get("object_candidate_id")
            if statement.get("subject_candidate_id") in MEMBERS
            else statement.get("subject_candidate_id")
        )
        counterpart_counts[bool(alignment_by_id.get(other, {}).get("ku_id"))] += 1
    assert counterpart_counts == Counter({True: 14, False: 12}), counterpart_counts

    for item in SOURCES:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(new_rows), len(groups)) == (5008, 4836)
    assert (len(registered), sum(map(len, registered.values()))) == (164, 209)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "term",
        "canonical_name": "巴姆博恰蒂画家群体",
        "name_en": "Bamboccianti",
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1184
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row["decision"] == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(r.get("ku_id") for r in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (165, 212)

    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    card_text = make_card()

    if args.dry_run:
        print(
            "dry-run passed: group=sg3-term-bamboccianti candidates=3 statements=55 "
            "relation_candidates=26 counterparts=21 mapped_statements=14 pending_statements=12 "
            "registered_groups_after=165 mapped_candidates_after=212 manifest_after=1184"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=sg3-term-bamboccianti candidates=3 statements=55 "
        "relation_candidates=26 counterparts=21 mapped_statements=14 pending_statements=12 "
        "manifest=1184 registered_groups=165 mapped_candidates=212"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
