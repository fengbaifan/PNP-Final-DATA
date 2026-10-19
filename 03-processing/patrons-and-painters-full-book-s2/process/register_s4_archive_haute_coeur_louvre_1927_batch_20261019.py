from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
RELATION_PATH = TABLES / "relations.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
ENTRY_PATH = ROOT / "AGENTS.md"

CANDIDATE = "cand-7097"
AUTHOR_CANDIDATE = "cand-7096"
GROUP = "archive-group-0161a6742171"
KU_ID = "units/archives/hautecoeur-histoire-chateaux-louvre-tuileries-1927"
CARD_PATH = "04-knowledge/units/archives/hautecoeur-histoire-chateaux-louvre-tuileries-1927.md"
PROCESS_REF = (
    f"03-processing/{TASK}/process/knowledge.md"
    "#s3-s4-hautecoeur-1927-archive-registration-20261019"
)
NAME_ZH = "《卢浮宫与杜乐丽宫城堡史》"
NAME_EN = "The History of the Châteaux of the Louvre and the Tuileries"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCES = {
    "bib": "Hautecœur, L.: L’Histoire des Chateaux du Louvre et des Tuileries, Paris 1927.",
    "p185n2": "1 de Cosnac, pp. 169 ff. 2 Hautecoeur, pp. 39-49.",
    "p185n3": "3 ibid., pp. 84-9. 4 Alazard, pp. 18-28 and 55-86.",
    "p187n6": "6 For this section see, apart from Blunt, 1953, and Wittkower, 1938, Hautecœur and Chantelou.",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def csv_text(fields, rows, bom=True):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" if bom else "") + stream.getvalue()


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one occurrence, got {count}"
    return text.replace(old, new, 1)


def update_current_summaries(process, result, entry):
    process = replace_once(
        process,
        "| archive | 2,100 | 90 | 1,240 / 1,298 | 0 | 18 | 694 | 121 / 170 | 1,119 / 1,128 |",
        "| archive | 2,100 | 90 | 1,240 / 1,298 | 0 | 18 | 694 | 122 / 171 | 1,118 / 1,127 |",
        "process archive type row",
    )
    process = replace_once(
        process,
        "| **合计** | **12,407** | **1,981** | **4,811 / 5,026** | **9** | **100** | **5,291** | **1,194 / 1,388** | **3,617 / 3,638** |",
        "| **合计** | **12,407** | **1,981** | **4,811 / 5,026** | **9** | **100** | **5,291** | **1,195 / 1,389** | **3,616 / 3,637** |",
        "process S3/S4 total row",
    )
    process = replace_once(
        process,
        "3,617组、3,638条成员映射尚待登记；",
        "3,616组、3,637条成员映射尚待登记；",
        "process current S4 snapshot",
    )

    result = replace_once(
        result,
        "S4已登记1,194组、映射1,388条成员候选；尚待登记3,617组、3,638条映射，其中直接关系端点待登记队列为1,863组／1,863条候选映射。",
        "S4已登记1,195组、映射1,389条成员候选；尚待登记3,616组、3,637条映射，其中直接关系端点待登记队列为1,862组／1,862条候选映射。",
        "result current S4 snapshot",
    )
    result = replace_once(
        result,
        "| [KU 登记](../tables/ku-manifest.csv) | 2,211 KU；",
        "| [KU 登记](../tables/ku-manifest.csv) | 2,214 KU；",
        "result manifest count",
    )
    result = replace_once(
        result,
        "| [关系表](../tables/relations.csv) | 1,236条：1,234 formal、2 pending；",
        "| [关系表](../tables/relations.csv) | 1,239条：1,237 formal、2 pending；",
        "result relation row count",
    )

    result = replace_once(result, "S6关系表有1,236条记录（1,234 formal、2 pending）", "S6关系表有1,239条记录（1,237 formal、2 pending）", "result current relation summary")
    result = result.replace("S3 为12,407个候选记录了现行决定及可追溯去向", "S3 为12,407个唯一候选记录了现行决定及可追溯去向")

    strict_line = next(line for line in result.splitlines() if line.startswith("2026-10-19 最新 strict-stage 表审计通过："))
    updated_strict = strict_line
    for old, new in (
        ("KU=2,213", "KU=2,214"),
        ("S4已登记1,194组／1,388条候选映射，待登记3,617组／3,638条，其中直接关系端点队列1,863组／1,863条。",
         "S4已登记1,195组／1,389条候选映射，待登记3,616组／3,637条，其中直接关系端点队列1,862组／1,862条。"),
        ("S6关系表有1,234条formal和2条pending", "S6关系表有1,237条formal和2条pending"),
        ("S4待登记new候选映射3,638条", "S4待登记new候选映射3,637条"),
    ):
        assert old in updated_strict, old
        updated_strict = updated_strict.replace(old, new)
    result = replace_once(result, strict_line, updated_strict, "result strict-stage line")

    queue_line = next(line for line in result.splitlines() if line.startswith("直接关系端点待登队列按类型（组／候选成员）为："))
    updated_queue = queue_line.replace("archive 481／481", "archive 480／480")
    assert updated_queue != queue_line
    result = replace_once(result, queue_line, updated_queue, "result direct endpoint type queue")

    history_line = next(line for line in result.splitlines() if line.startswith("历史快照：1,902组"))
    updated_history = history_line.replace(
        "Alazard／Strozzi本批前为1,864组／1,864条；当前队列以本结果顶部及下方最新统计为准：1,863组／1,863条。",
        "Alazard／Strozzi批次前为1,864组／1,864条；该批后为1,863组／1,863条；Hautecœur档案登记后当前为1,862组／1,862条。",
    )
    assert updated_history != history_line
    result = replace_once(result, history_line, updated_history, "result historical queue line")

    plan_s4 = next(line for line in result.splitlines() if line.startswith("2. **S4 按类型先登记直接关系端点**"))
    updated_s4 = plan_s4.replace("1,863个待登记组", "1,862个待登记组").replace("档案481", "档案480").replace("1,754组", "1,754组").replace("3,617个待登记组", "3,616个待登记组")
    assert updated_s4 != plan_s4
    result = replace_once(result, plan_s4, updated_s4, "result S4 plan")
    plan_s7 = next(line for line in result.splitlines() if line.startswith("5. **S7 重建发布快照**"))
    updated_s7 = plan_s7.replace("当前2,213 KU及1,236条关系", "当前2,214 KU及1,239条关系")
    assert updated_s7 != plan_s7
    result = replace_once(result, plan_s7, updated_s7, "result S7 plan")

    entry_line = next(line for line in entry.splitlines() if line.startswith("项目版本为初始化阶段的 0.1.0；"))
    updated_entry = entry_line
    for old, new in (
        ("1,194／4,811个新增身份组（1,388条候选映射），3,617组／3,638条映射待登记；直接关系端点待登队列为1,863组／1,863条候选映射，其中人物31组、机构96组、事件144组、地点232组、作品340组、档案481组、术语539组。",
         "1,195／4,811个新增身份组（1,389条候选映射），3,616组／3,637条映射待登记；直接关系端点待登队列为1,862组／1,862条候选映射，其中人物31组、机构96组、事件144组、地点232组、作品340组、档案480组、术语539组。"),
        ("S6关系表有1,236条记录（1,234 formal、2 pending）", "S6关系表有1,239条记录（1,237 formal、2 pending）"),
    ):
        assert old in updated_entry, old
        updated_entry = updated_entry.replace(old, new)
    entry = replace_once(entry, entry_line, updated_entry, "AGENTS current summary")
    return process, result, entry


def source_record(file, location, quote, summary, span):
    return {
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{file}",
            "source_span": span,
        },
    }


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": [
            source_record(
                "21_CHP-21Bibliography.md",
                "第21章书目，印刷页425，Markdown 行598。",
                SOURCES["bib"],
                "书目列出 `Hautecœur, L.`、原题、Paris 及1927年；S2校读记录印本题名为 `Châteaux`。",
                "line 598; printed p. 425",
            ),
            source_record(
                "07_CHP-7_sec_i.md",
                "第7章，印刷页185，注2，Markdown 行358。",
                SOURCES["p185n2"],
                "注2以作者姓氏和 pp.39–49 定位该书；引文页面未独立阅读。",
                "line 358; printed p. 185, note 2",
            ),
            source_record(
                "07_CHP-7_sec_i.md",
                "第7章，印刷页185，注3，Markdown 行359。",
                SOURCES["p185n3"],
                "注3以 `ibid.` 回指注2，定位 pp.84–89；引文页面未独立阅读。",
                "line 359; printed p. 185, note 3",
            ),
            source_record(
                "07_CHP-7_sec_i.md",
                "第7章，印刷页187，注6，Markdown 行367。",
                SOURCES["p187n6"],
                "注6并列提及 Hautecœur 与 Chantelou；第21章书目唯一项识别本书。",
                "line 367; printed p. 187, note 6",
            ),
        ],
        "created": "2026-10-19",
        "updated": "2026-10-19",
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    bib_link = "[第21章书目 p.425](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（line 598）"
    n2_link = "[第7章 p.185 注2](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（line 358）"
    n3_link = "[第7章 p.185 注3](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（line 359）"
    n6_link = "[第7章 p.187 注6](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（line 367）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记哈斯克尔第21章书目所列的法语图书 *L’Histoire des Châteaux du Louvre et des Tuileries*，书目记作 Paris, 1927。责任者形式仅为 “Hautecœur, L.”；目前没有依据将首字母扩写为全名或对应到某一外部人物。第7章注释以 pp.39–49、pp.84–89 和 “Hautecœur” 定位该书；被引页面未独立阅读。中文和英文展示题名为描述性暂译，不是已核实的正式译名。本卡不推断出版者、ISBN、版本或原书内容。

**English:** This card records the French-language book *L’Histoire des Châteaux du Louvre et des Tuileries*, listed in Haskell’s chapter 21 bibliography as Paris, 1927. The author form is given only as “Hautecœur, L.”; the initial is not expanded and is not aligned to an external person. Chapter 7 notes point to pp. 39–49, pp. 84–89, and “Hautecœur”; those pages have not been independently read. The Chinese and English display titles are descriptive translations, not verified published titles. No publisher, ISBN, edition, or book content is inferred.

### 书目身份与引文定位

- **法语原题（按 S2 页图校读）：** *L’Histoire des Châteaux du Louvre et des Tuileries*；OCR 转录为 `Chateaux`，S2 记录印本校读为 `Châteaux`。{bib_link}
- **中文描述性暂译：** {NAME_ZH}；非原题。{bib_link}
- **英文描述性暂译：** {NAME_EN}；非书目原载英文题名。{bib_link}
- **责任者形式：** `Hautecœur, L.`；全名未证。{bib_link}
- **出版地／年：** Paris, 1927。{bib_link}
- **第7章 p.185 引文：** 注2定位 pp.39–49；注3的 `ibid., pp.84–89` 回指注2。{n2_link}；{n3_link}；被引页未独立阅读。
- **第7章 p.187 引文：** 注6并列提及 Hautecœur 与 Chantelou；出版物依书目唯一项识别。{n6_link}；被引页未独立阅读。

### 身份边界

S3 组 `archive-group-0161a6742171` 仅含 `cand-7097`，S4 登记为本卡。作者候选 `cand-7096` 仍为 S3 `undecided`：书内形式只有首字母；本卡不猜测全名，不连接人物 KU，也不据书目责任字段建立 `authored_by` 正式关系。

## 关系与证据

第7章三处注释登记为 Haskell 对本书的引用。关系只表达引用路径，不验证被引书或页面内容；第21章书目著录 statement 保持书目元数据，不另建关系边。
"""
    return f"---\n{yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)}---\n\n{body}"


def main():
    parser = argparse.ArgumentParser(description="Register Hautecœur's 1927 archive KU and three citation edges")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = read_csv(CANDIDATE_PATH)
    relation_fields, relations = read_csv(RELATION_PATH)
    sources_fields, source_rows = read_csv(TABLES / "sources.csv")
    candidates_by_id = {r["candidate_id"]: r for r in candidates}
    align_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    source_ids = {r.get("source_id") for r in source_rows}

    assert CANDIDATE in candidates_by_id and candidates_by_id[CANDIDATE]["suggested_type"] == "archive"
    assert AUTHOR_CANDIDATE in candidates_by_id and candidates_by_id[AUTHOR_CANDIDATE]["suggested_type"] == "person"
    assert align_by_id[CANDIDATE]["decision"] == "new" and not align_by_id[CANDIDATE].get("ku_id")
    assert align_by_id[AUTHOR_CANDIDATE]["decision"] == "undecided" and not align_by_id[AUTHOR_CANDIDATE].get("ku_id")
    assert f"group={GROUP}" in align_by_id[CANDIDATE]["resolution_note"]
    group_rows = [r for r in alignments if r.get("decision") == "new" and f"group={GROUP}" in r.get("resolution_note", "")]
    assert [r["candidate_id"] for r in group_rows] == [CANDIDATE]
    assert not any(r.get("ku_id") == KU_ID or r.get("card_path") == CARD_PATH for r in manifest)
    card_path = ROOT / CARD_PATH
    assert not card_path.exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_PATH not in accepted
    assert "haskell-1980-rev-ed" in source_ids
    assert [r["relation_id"] for r in relations[-1:]] == ["rel-1236"]
    assert len(relations) == 1236 and sum(r.get("status") == "formal" for r in relations) == 1234

    domain_range = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8-sig"))
    assert "archive" in domain_range["domain_range"]["cites"]["domain"]
    assert "archive" in domain_range["domain_range"]["cites"]["range"]

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    expected_statements = {
        "st-chp7-p185-n2-cite-hautecoeur": (358, 185),
        "st-chp7-p185-n3-cite-hautecoeur": (359, 185),
        "st-chp7-p187-n6-cite-hautecoeur": (367, 187),
    }
    by_statement = {s["statement_id"]: s for s in statements}
    assert set(expected_statements).issubset(by_statement)
    for sid, (line_no, printed_page) in expected_statements.items():
        st = by_statement[sid]
        q = st["qualifiers"]
        assert st["subject_candidate_id"] == "cand-2962" and st["object_candidate_id"] == CANDIDATE
        assert st["predicate"] == "cites" and q["relation_candidate"] is True
        assert q["source_line_start"] == line_no and q["printed_page"] == printed_page
    for key, source_file in (("bib", "21_CHP-21Bibliography.md"), ("p185n2", "07_CHP-7_sec_i.md"), ("p185n3", "07_CHP-7_sec_i.md"), ("p187n6", "07_CHP-7_sec_i.md")):
        actual = (ROOT / "02-sources" / "02-Markdown" / source_file).read_text(encoding="utf-8-sig")
        assert SOURCES[key] in actual, f"source quote changed: {source_file}:{key}"

    planned_alignment = [dict(r) for r in alignments]
    target_alignment = next(r for r in planned_alignment if r.get("candidate_id") == CANDIDATE and not r.get("external_source"))
    target_alignment["ku_id"] = KU_ID
    target_alignment["process_ref"] = PROCESS_REF
    target_alignment["resolution_note"] += f" | S4 registered as {KU_ID}"
    planned_candidates = [dict(r) for r in candidates]
    candidate = next(r for r in planned_candidates if r["candidate_id"] == CANDIDATE)
    candidate["detail"] = (
        "Haskell’s bibliography lists L’Histoire des Châteaux du Louvre et des Tuileries, Paris 1927; "
        "S2 records the print-image correction from OCR Chateaux to Châteaux. Chapter 7 notes 2, 3 (ibid. to note 2), and 6 cite this publication; cited pages were not independently read. "
        "S3 new group archive-group-0161a6742171 is registered as units/archives/hautecoeur-histoire-chateaux-louvre-tuileries-1927. "
        "The responsible-author form Hautecœur, L. remains unresolved as candidate cand-7096; no full name is inferred."
    )

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_PATH,
    })
    planned_relations = list(relations)
    relation_payloads = [
        ("rel-1237", "line 358; printed p.185, note 2", "第7章 p.185 注2；Hautecoeur, pp.39–49；被引页未独立阅读", "Haskell脚注以Hautecoeur及pp.39–49定位该书；只记录引用路径。"),
        ("rel-1238", "line 359; printed p.185, note 3", "第7章 p.185 注3；ibid., pp.84–9（回指注2）；被引页未独立阅读", "ibid.按S2脚注衔接记录回指注2；不独立核验被引书内容。"),
        ("rel-1239", "line 367; printed p.187, note 6", "第7章 p.187 注6；Hautecœur与Chantelou并列；书目唯一项识别本书；被引页未独立阅读", "注6以Hautecœur称引；本书端点由第21章唯一书目项映射。"),
    ]
    for relation_id, source_span, scope, note in relation_payloads:
        planned_relations.append({
            "relation_id": relation_id,
            "subject_ku_id": "units/archives/patrons-and-painters",
            "object_ku_id": KU_ID,
            "predicate": "cites",
            "time": "",
            "role": "脚注引文",
            "scope": scope,
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": source_span,
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "note": note,
        })

    planned_process = PROCESS_PATH.read_text(encoding="utf-8-sig")
    planned_result = RESULT_PATH.read_text(encoding="utf-8-sig")
    planned_entry = ENTRY_PATH.read_text(encoding="utf-8-sig")
    planned_process, planned_result, planned_entry = update_current_summaries(planned_process, planned_result, planned_entry)

    process_batch = (
        f'<a id="{PROCESS_REF.rsplit("#", 1)[1]}"></a>\n\n'
        "### S3–S4 archive：Hautecœur《L’Histoire des Châteaux du Louvre et des Tuileries》（2026-10-19）\n\n"
        "- `cand-7097` 沿用 `new` 组 `archive-group-0161a6742171`，登记为 `units/archives/hautecoeur-histoire-chateaux-louvre-tuileries-1927`。第21章 p.425 书目给出作者责任者形式 `Hautecœur, L.`、法语题名和 Paris 1927；S2页图校读将 OCR `Chateaux` 订正为印本 `Châteaux`。出版物身份仅依书内书目，不声称查阅外部目录或原书。\n"
        "- `cand-7096`（`L. Hautecœur`）仍为 `undecided`：书目仅列首字母，现有材料不足以恢复全名或与外部人物对齐。档案卡保留原责任者形式和该待证边界；不新建人物KU，也不建立 `authored_by` 正式关系。\n"
        "- 第7章 p.185 注2（line 358）、注3（line 359；`ibid.` 回指注2）及 p.187 注6（line 367）分别登记为 `rel-1237`–`rel-1239` `cites`，source 均为 `haskell-1980-rev-ed`。注6的出版物端点由第21章唯一书目项识别。三处被引页未独立阅读；书目责任者 statement 的 `relation_candidate=false`，未另造关系边。\n"
        "- 本批新增1个KU、1条候选映射、3条正式关系；archive 已登记122组／171条映射，待登记1,118组／1,127条。全书S4已登记1,195组／1,389条，待登记3,616组／3,637条；直接关系端点队列由1,863组降至1,862组，archive子队列由481组降至480组。\n\n"
    )
    planned_process = replace_once(
        planned_process,
        "### 跨章补充裁决：Valmarana 壁画组（2026-10-15）",
        process_batch + "### 跨章补充裁决：Valmarana 壁画组（2026-10-15）",
        "insert process batch note",
    )
    batch_result = (
        "### S3–S4 archive：Hautecœur《L’Histoire des Châteaux du Louvre et des Tuileries》登记（2026-10-19）\n\n"
        "`cand-7097` 沿用既有 `new` 决定，登记为单成员档案组并完成 S4；第21章书目记录责任者形式 `Hautecœur, L.`、原题及 Paris 1927。"
        "第7章 p.185 注2、注3及 p.187 注6 的三条 `cites` 候选登记为 `rel-1237`–`rel-1239` formal，定位依赖书目唯一项及注3的 ibid. 回指；被引页未独立阅读。"
        "责任者候选 `cand-7096` 仍为 S3 `undecided`（来源只有首字母），不扩写全名、不建立 `authored_by` 边。新增1个KU、1条映射和3条正式关系，直接端点队列减少1组。"
        f"[过程记录](../../03-processing/{TASK}/process/knowledge.md#s3-s4-hautecoeur-1927-archive-registration-20261019)。\n\n"
    )
    planned_result = replace_once(planned_result, "### 后续工作规划", batch_result + "### 后续工作规划", "insert result batch note")

    direct_line = next(line for line in planned_result.splitlines() if line.startswith("直接关系端点待登队列按类型（组／候选成员）为："))
    new_direct_line = direct_line.replace("archive 481／481", "archive 480／480")
    planned_result = replace_once(planned_result, direct_line, new_direct_line, "direct endpoint archive count")
    historical_line = next(line for line in planned_result.splitlines() if line.startswith("历史快照：1,902组"))
    new_history_line = historical_line.replace(
        "Alazard／Strozzi本批前为1,864组／1,864条；当前队列以本结果顶部及下方最新统计为准：1,863组／1,863条。",
        "Alazard／Strozzi批次前为1,864组／1,864条；该批后为1,863组／1,863条；Hautecœur档案登记后当前为1,862组／1,862条。",
    )
    planned_result = replace_once(planned_result, historical_line, new_history_line, "historical direct endpoint count")
    plan_s4 = next(line for line in planned_result.splitlines() if line.startswith("2. **S4 按类型先登记直接关系端点**"))
    new_plan_s4 = plan_s4.replace("1,863个待登记组", "1,862个待登记组").replace("档案481", "档案480").replace("3,617个待登记组", "3,616个待登记组")
    planned_result = replace_once(planned_result, plan_s4, new_plan_s4, "S4 plan count")
    plan_s7 = next(line for line in planned_result.splitlines() if line.startswith("5. **S7 重建发布快照**"))
    new_plan_s7 = plan_s7.replace("当前2,213 KU及1,236条关系", "当前2,214 KU及1,239条关系")
    planned_result = replace_once(planned_result, plan_s7, new_plan_s7, "S7 release count")

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\ufeff" + "\n".join(accepted_lines) + "\n"

    planned_files = {
        ROOT / CARD_PATH: card_text(),
        MANIFEST_PATH: csv_text(manifest_fields, planned_manifest, bom=False),
        ALIGNMENT_PATH: csv_text(alignment_fields, planned_alignment),
        CANDIDATE_PATH: csv_text(candidate_fields, planned_candidates),
        RELATION_PATH: csv_text(relation_fields, planned_relations),
        ACCEPTED_PATH: planned_accepted,
        PROCESS_PATH: planned_process,
        RESULT_PATH: planned_result,
        ENTRY_PATH: planned_entry,
    }

    assert len(planned_manifest) == 2214
    assert len(planned_relations) == 1239 and sum(r.get("status") == "formal" for r in planned_relations) == 1237
    assert len(manifest) == 2213 and len(relations) == 1236
    assert target_alignment["ku_id"] == KU_ID
    assert all(r.get("ku_id") == "" for r in group_rows if r["candidate_id"] != CANDIDATE)
    assert all(r["source_id"] == "haskell-1980-rev-ed" and r["status"] == "formal" for r in planned_relations[-3:])
    assert "cand-7096" in card_text() and "authored_by" in card_text()

    if args.dry_run:
        print(f"S4 archive dry-run passed: {CANDIDATE} / {GROUP} -> {KU_ID}")
        print("author cand-7096 remains undecided; 3 source citations and source_id verified; no authored_by edge proposed")
        print("new rows=1 KU, 1 mapping, 3 formal cites; expected totals KU=2,214, relations=1,239, S4 pending=3,616 groups/3,637 members")
        print("process, result, AGENTS, accepted manifest, alignment, candidates, relations, and bilingual card diffs prepared; no files changed")
        return 0

    to_write = list(planned_files.items())
    with tempfile.TemporaryDirectory(prefix="pnp-s4-hautecoeur-") as temp_dir:
        backup_root = Path(temp_dir)
        existed = {}
        for path, _ in to_write:
            existed[path] = path.exists()
            if path.exists():
                backup = backup_root / f"{len(existed):02d}-{path.name}"
                shutil.copy2(path, backup)
                existed[path] = backup
        try:
            for path, content in to_write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8", newline="\n")
        except Exception:
            for path, backup in existed.items():
                if isinstance(backup, Path):
                    shutil.copy2(backup, path)
                elif not backup and path.exists():
                    path.unlink()
            raise
    print(f"applied: {CANDIDATE} -> {KU_ID}; relations=rel-1237..rel-1239; KU={len(planned_manifest)}; pending=3,616/3,637")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
