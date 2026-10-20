from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_s5_s6_archive_citations_20261020 as archive_batch
import scripts.build_field_facts as field_facts

TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
RELATIONS_PATH = TABLES / "relations.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
AGENTS_PATH = ROOT / "AGENTS.md"

DATE = "2026-10-21"
ANCHOR = "s4-s5-s6-da-canal-cross-chapter-citations-20261021"
BIB = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
CH6 = "02-sources/02-Markdown/06_CHP-6_sec_v.md"
CH7 = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
KU_ID = "units/archives/vincenzo-da-canal-vita-gregorio-lazzarini-1809"
CARD_PATH = f"04-knowledge/{KU_ID}.md"
STATEMENTS = ["st-chp6-p166-n2-canal", "st-chp7-p195-n3-da-canal"]

BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SPEC = {
    "candidate": "cand-6593",
    "group": "archive-group-aa69e7e50bc3",
    "ku_id": KU_ID,
    "type": "archive",
    "sub_type": "book",
    "name_zh": "格雷戈里奥·拉扎里尼传",
    "name_en": "Vita di Gregorio Lazzarini",
    "sources": [
        {
            "location": "第21章书目，印刷页418，Markdown L307。",
            "summary": "书目以“Canal, Vincenzo da”形式著录 *Vita di Gregorio Lazzarini (1732)*，出版项为 Venezia 1809；这里只记录 Haskell 的书目形式。",
            "source_file": BIB,
            "span": "line 307; printed p. 418",
            "quotes": ["Canal, Vincenzo da: Vita di Gregorio Lazzarini (1732), Venezia 1809."],
            "link": "[第21章 p.418 书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L307)",
        },
        {
            "location": "第6章，印刷页166注2，Markdown L70。",
            "summary": "注2以“da Canal, p. 69”标注对该书的引文位置；本记录不表示被引页或所述事实已独立核实。",
            "source_file": CH6,
            "span": "line 70; printed p. 166 n. 2",
            "quotes": ["da Canal, p. 69."],
            "link": "[第6章 p.166 注2](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md#L70)",
        },
        {
            "location": "第7章，印刷页195注3，Markdown L105。",
            "summary": "注3明确引用 Da Canal，尤其 pp. 71–73；被引页未在本批独立阅读。",
            "source_file": CH7,
            "span": "line 105; printed p. 195 n. 3",
            "quotes": ["3 Da Canal, especially pp. 71-3."],
            "link": "[第7章 p.195 注3](../../../02-sources/02-Markdown/07_CHP-7_sec_iv.md#L105)",
        },
    ],
    "fields": [
        ("文献类型", "图书（据 Haskell 书目）", "S1；第21章书目，印刷页418，L307"),
        ("原题名及书目括注", "*Vita di Gregorio Lazzarini (1732)*；括注照录，本批不判断其含义", "S1；第21章书目，印刷页418，L307"),
        ("书目责任者形式", "Vincenzo da Canal（照录 Haskell 书目形式；未据此推断外部身份）", "S1；第21章书目，印刷页418，L307"),
        ("出版项", "Venezia 1809", "S1；第21章书目，印刷页418，L307"),
        ("Haskell 书内引注定位", "第6章 p.166 注2：da Canal, p. 69；被引页未独立阅读", "S2；第6章印刷页166注2，L70"),
        ("Haskell 书内引注定位", "第7章 p.195 注3：Da Canal, especially pp. 71–73；被引页未独立阅读", "S3；第7章印刷页195注3，L105"),
    ],
    "paragraph_zh": (
        "本卡登记 Haskell 第21章书目所列出版物 *Vita di Gregorio Lazzarini (1732)*（Venezia，1809）；"
        "中文显示名为描述性工作译名。“(1732)”按原书括注保留，本批不判断其含义。第6章注2和第7章注3分别给出 p.69 与 pp.71–73 的引注定位；"
        "本批未独立查阅该出版物或被引页，也不将作者候选 cand-7781 与文献对象合并。"
    ),
    "paragraph_en": (
        "This unit records the publication *Vita di Gregorio Lazzarini (1732)* (Venezia, 1809) as listed in Haskell’s chapter 21 bibliography. "
        "The Chinese display title is a descriptive working translation. The parenthetical “(1732)” is transcribed without assigning it a meaning. "
        "Chapter 6 note 2 and chapter 7 note 3 cite pp. 69 and 71–73 respectively. Neither the publication nor its cited pages was independently consulted; "
        "person candidate cand-7781 is not merged with this archive object."
    ),
}


def write_text_preserving(path: Path, text: str) -> None:
    raw = path.read_bytes() if path.exists() else b""
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    encoding = "utf-8-sig" if bom else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        handle.write(text.replace("\n", newline))


def write_csv_preserving(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in raw else "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def extract_fields(card_text: str, manifest_rows: list[dict]) -> list[dict]:
    old_base = field_facts.BASE
    with tempfile.TemporaryDirectory(prefix="pnp-s4-da-canal-") as temp_name:
        temp_root = Path(temp_name)
        field_facts.BASE = temp_root
        card = temp_root / CARD_PATH
        card.parent.mkdir(parents=True, exist_ok=True)
        card.write_text(card_text, encoding="utf-8-sig", newline="\n")
        try:
            rows, _, warnings, cards_with_tables = field_facts.extract_records(
                [row for row in manifest_rows if row["ku_id"] == KU_ID]
            )
        finally:
            field_facts.BASE = old_base
    assert not warnings, warnings
    assert cards_with_tables == 1 and len(rows) == len(SPEC["fields"]), (cards_with_tables, len(rows))
    assert all(row["source_ids"] == ["haskell-1980-rev-ed"] for row in rows), rows
    assert all(row["evidence_status"] == "source_backed" and row["origin"] == "book" for row in rows)
    field_facts.assign_ids(rows, ENRICHMENT_PATH)
    return rows


def replace_one(text: str, pattern: str, replacement: str, label: str) -> str:
    result, count = re.subn(pattern, replacement, text, count=1, flags=re.M)
    assert count == 1, f"could not update {label}"
    return result


def format_type_counts(type_counts: dict[str, tuple[int, int]]) -> str:
    labels = {
        "person": "person", "institution": "institution", "event": "event",
        "place": "place", "work": "work", "archive": "archive", "term": "term",
        "family": "family", "procedure": "procedure",
    }
    order = ["person", "institution", "event", "place", "work", "archive", "term", "family", "procedure"]
    return "、".join(
        f"{labels[k]} {type_counts.get(k, (0, 0))[0]}组／{type_counts.get(k, (0, 0))[1]}成员"
        for k in order if type_counts.get(k, (0, 0))[0]
    ) or "无"


def build_relation_rows(existing: list[dict]) -> list[dict]:
    next_id = max(int(row["relation_id"].split("-")[1]) for row in existing) + 1
    locators = [
        {
            "statement": STATEMENTS[0], "role": "第6章 p.166 注2书目引文",
            "scope": "Haskell第6章p.166注2明确引 Da Canal, p. 69；只记录书内引注，不表示被引页或所述事实已核验。",
            "span": "line 70; printed p. 166 n. 2", "source_file": CH6,
        },
        {
            "statement": STATEMENTS[1], "role": "第7章 p.195 注3书目引文",
            "scope": "Haskell第7章p.195注3明确引 Da Canal，especially pp. 71–73；只记录书内引注，不表示被引页或所述事实已核验。",
            "span": "line 105; printed p. 195 n. 3", "source_file": CH7,
        },
    ]
    return [
        {
            "relation_id": f"rel-{next_id + index:04d}",
            "subject_ku_id": "units/archives/patrons-and-painters",
            "object_ku_id": KU_ID,
            "predicate": "cites",
            "time": "",
            "role": item["role"],
            "scope": item["scope"],
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": item["span"],
            "source_file": item["source_file"],
            "note": f"S2 statement: {item['statement']}. The edge records Haskell’s citation only; the cited publication and page were not consulted.",
        }
        for index, item in enumerate(locators)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Da Canal archive endpoint and adjudicate two cited-page statements.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    archive_batch.DATE = DATE
    archive_batch.ANCHOR = ANCHOR
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    relation_fields, relations = sync.read_csv(RELATIONS_PATH)
    _, source_rows = sync.read_csv(TABLES / "sources.csv")
    statements = sync.load_statements()
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    statement_by_id = {row["statement_id"]: row for row in statements}
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    agents_text = AGENTS_PATH.read_text(encoding="utf-8-sig")

    candidate = candidate_by_id[SPEC["candidate"]]
    decision = decisions[SPEC["candidate"]]
    assert candidate.get("suggested_type") == "archive"
    assert decision.get("decision") == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == SPEC["group"]
    members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == SPEC["group"]
    ]
    assert members == [SPEC["candidate"]], members
    assert not (ROOT / CARD_PATH).exists() and CARD_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    assert not any(row["type"] == "archive" and row["name_en"].casefold() == SPEC["name_en"].casefold() for row in manifest)
    assert "haskell-1980-rev-ed" in {row["source_id"] for row in source_rows}
    assert ANCHOR not in process_text and ANCHOR not in result_text
    assert all(statement_id in statement_by_id for statement_id in STATEMENTS)
    for statement_id in STATEMENTS:
        statement = statement_by_id[statement_id]
        assert statement.get("qualifiers", {}).get("relation_candidate") is True, statement_id
        assert statement.get("subject_candidate_id") == "cand-2962", statement_id
        assert statement.get("object_candidate_id") == SPEC["candidate"], statement_id
        assert not any(statement_id in row.get("note", "") for row in relations), statement_id

    source_ids = {row["source_id"] for row in source_rows}
    card_text = archive_batch.make_archive_card(SPEC)
    fm_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    frontmatter = yaml.safe_load(fm_match.group(1))
    assert all(field_facts.citation_identity(item["citation"])[0] in source_ids for item in frontmatter["sources"])
    for source in SPEC["sources"]:
        source_text = (ROOT / source["source_file"]).read_text(encoding="utf-8-sig")
        normalized_source = " ".join(source_text.split())
        for quote in source["quotes"]:
            assert " ".join(quote.split()) in normalized_source, quote

    planned_alignment = [dict(row) for row in alignments]
    planned_decision = next(row for row in planned_alignment if row.get("candidate_id") == SPEC["candidate"] and not row.get("external_source"))
    planned_decision["ku_id"] = KU_ID
    planned_decision["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    planned_decision["resolution_note"] += (
        f" S4 registration: {SPEC['group']} maps to {KU_ID}; Haskell book-local bibliography and citations only; "
        "parenthetical (1732) retained without interpretation and no external identity or cited-page claim added."
    )

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID, "type": "archive", "canonical_name": SPEC["name_zh"],
        "name_en": SPEC["name_en"], "source_task": TASK, "card_path": CARD_PATH,
    }]
    planned_accepted = archive_batch.insert_accepted_paths(accepted_text, [CARD_PATH])
    new_relation_rows = build_relation_rows(relations)
    relation_keys = {
        (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"])
        for row in relations
    }
    for row in new_relation_rows:
        key = (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"])
        assert key not in relation_keys, key
        relation_keys.add(key)
    planned_relations = relations + new_relation_rows

    new_fields = extract_fields(card_text, planned_manifest)
    planned_field_count = sum(1 for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()) + len(new_fields)
    planned_enrichment = [*new_fields]

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    direct_groups, direct_candidates, direct_members, direct_types = archive_batch.summarize_relation_endpoint_queue(
        candidates, planned_alignment, planned_manifest, statements
    )
    pending_groups = totals["pending_groups"]
    pending_members = totals["pending_members"]
    non_direct_groups = pending_groups - direct_groups
    non_direct_members = pending_members - direct_members

    s6_match = re.search(r"([\d,]+)/([\d,]+)条S2关系候选（([\d,]+) formal、([\d,]+) pending、([\d,]+) rejected）", result_text)
    assert s6_match, "current cumulative S6 counts not found in result"
    s6_total, s6_denominator, s6_formal, s6_pending, s6_rejected = [int(value.replace(",", "")) for value in s6_match.groups()]
    assert s6_total == s6_formal + s6_pending + s6_rejected
    assert s6_denominator == sum(1 for row in statements if (row.get("qualifiers") or {}).get("relation_candidate") is True)
    next_s6 = (s6_total + len(STATEMENTS), s6_denominator, s6_formal + len(STATEMENTS), s6_pending, s6_rejected)

    current_unverified = sum(1 for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip() and json.loads(line).get("evidence_status") == "unverified")
    relation_status = {name: sum(1 for row in planned_relations if row["status"] == name) for name in ("formal", "pending", "rejected")}
    updated_result = result_text
    n_decisions = totals["total"]
    s3_start = updated_result.index("## S3 身份决定与交接")
    s3_table_start = updated_result.index("| S3 决定 |", s3_start)
    s3_table_end = updated_result.index("\n\n", s3_table_start)
    s3_table = "\n".join([
        "| S3 决定 | 候选数 | 去向 |",
        "|---|---:|---|",
        f"| same | {sync.fmt(totals['same_candidates'])} | 指向 {sync.fmt(totals['same_kus'])} 个既有 KU |",
        f"| new | {sync.fmt(totals['new_candidates'])} | 按 {sync.fmt(totals['new_groups'])} 个当前身份组进入 S4；每组登记一个 KU |",
        f"| conflict | {sync.fmt(totals['conflict'])} | 冲突两侧与来源依据保留在对齐行，等待解决证据 |",
        f"| excluded | {sync.fmt(totals['excluded'])} | 含 48 项 S1 排除及其余 S3 类型/对象边界排除 |",
        f"| undecided | {sync.fmt(totals['undecided'])} | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        f"| **合计** | **{sync.fmt(n_decisions)}** | 每个候选一条当前决定记录 |",
    ])
    updated_result = updated_result[:s3_table_start] + s3_table + updated_result[s3_table_end:]
    matrix_marker = "| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |"
    matrix_start = updated_result.index(matrix_marker)
    matrix_end = updated_result.index("\n\n", matrix_start)
    type_table, _ = sync.build_type_table(stats)
    updated_result = updated_result[:matrix_start] + type_table + updated_result[matrix_end:]

    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as handle:
        mention_count = sum(1 for _ in csv.DictReader(handle))
    statement_counts = {"true": 0, "false": 0, "unset": 0}
    for statement in statements:
        value = (statement.get("qualifiers") or {}).get("relation_candidate")
        statement_counts["true" if value is True else "false" if value is False else "unset"] += 1
    # The result table counts extra alignment rows beyond one current decision row per candidate.
    external_alignment_count = len(planned_alignment) - len(candidates)
    assert external_alignment_count >= 0
    source_count = len(source_rows)
    missing_relation_source = sum(not row.get("source_id") for row in planned_relations)
    with (TABLES / "candidate-backlog.csv").open(encoding="utf-8-sig", newline="") as handle:
        backlog_rows = list(csv.DictReader(handle))
    backlog_completed = sum(row.get("status") == "completed" for row in backlog_rows)
    backlog_pending = sum(row.get("status") == "pending" for row in backlog_rows)
    artifact_rows = {
        "KU 登记": f"| [KU 登记](../tables/ku-manifest.csv) | {len(planned_manifest):,} KU；新组登记与待登记分类型统计见下表 |",
        "实体候选": f"| [实体候选](../tables/entity-candidates.csv) | {len(candidates):,} candidates（新增 Callot《La Fiera dell'Impruneta》版画 work 候选；含直接关系端点候选 Luigi Pavini、Alessandro Farnese 公爵与 Paul Bonnefon） |",
        "提及账本": f"| [提及账本](../tables/mentions.csv) | {mention_count:,} mentions |",
        "原书断言及关系候选": f"| [原书断言及关系候选](../tables/book-statements.jsonl) | {len(statements):,} statements；relation_candidate true {statement_counts['true']:,}、false {statement_counts['false']:,}、unset {statement_counts['unset']:,} |",
        "覆盖账本": "| [覆盖账本](../tables/s2-coverage.csv) | 832段全部完成登记与迁移 |",
        "全书对齐": f"| [全书对齐](../tables/alignment.csv) | {len(planned_alignment):,} 条：{len(candidates):,} 条候选决定记录及 {external_alignment_count:,} 条独立外部身份记录；候选决定数见下表 |",
        "字段表": f"| [字段表](../tables/enrichment.jsonl) | {planned_field_count:,}条，其中{current_unverified:,}条 unverified |",
        "来源登记": f"| [来源登记](../tables/sources.csv) | {source_count:,} 条来源记录 |",
        "关系表": f"| [关系表](../tables/relations.csv) | {len(planned_relations):,}条：{relation_status['formal']:,} formal、{relation_status['pending']:,} pending；{missing_relation_source}条缺结构化 `source_id`；S2另有{statement_counts['true']:,}条`relation_candidate=true`的statement，二者不是同一计数口径 |",
        "候选待办": f"| [候选待办](../tables/candidate-backlog.csv) | {len(backlog_rows)}条记录：{backlog_completed}条 completed、{backlog_pending}条 pending；既有对象与待决关系端点分别处理 |",
    }
    for key, line in artifact_rows.items():
        updated_result = replace_one(updated_result, rf"^\| \[{re.escape(key)}\]\([^\n]+$", line, f"result artifact {key}")
    status_lines = {
        "S4": (f"- **S4：** 已登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条候选映射；待登记{pending_groups:,}组／{pending_members:,}条映射，直接端点{direct_groups:,}组／{direct_members:,}条组成员映射。"),
        "S5": (f"- **S5：** 字段表{planned_field_count:,}条，其中{current_unverified:,}条为 `unverified`；未核字段按证据逐项处理。"),
        "S6": (f"- **S6：** 关系表{len(planned_relations):,}条（{relation_status['formal']:,} formal、{relation_status['pending']:,} pending）；过程记录累计逐条裁决{next_s6[0]:,}/{next_s6[1]:,}条S2关系候选（{next_s6[2]:,} formal、{next_s6[3]:,} pending、{next_s6[4]:,} rejected），其余{next_s6[1]-next_s6[0]:,}条待逐项裁决。"),
    }
    for stage, line in status_lines.items():
        updated_result = replace_one(updated_result, rf"^- \*\*{stage}：\*\*.*$", line, f"result {stage} stage summary")

    new_plan_line = (
        f"S4已登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条映射；"
        f"直接端点待登记{direct_groups:,}组／{direct_members:,}条成员映射（{format_type_counts(direct_types)}），"
        f"非直接队列{non_direct_groups:,}组／{non_direct_members:,}条。S5有{current_unverified:,}条unverified（字段表{planned_field_count:,}条）。"
        f"S6已逐项裁决{next_s6[0]:,}/{next_s6[1]:,}条（{next_s6[2]:,} formal、{next_s6[3]:,} pending、{next_s6[4]:,} rejected），尚有{next_s6[1]-next_s6[0]:,}条。"
    )
    updated_result = replace_one(updated_result, r"S4已登记[^\n]*?S6已逐项裁决[^\n]*", new_plan_line, "planning baseline")

    direct_priority = "、".join(
        f"{name} {count[0]}组/{count[1]}映射"
        for name, count in sorted(direct_types.items(), key=lambda item: (-item[1][0], item[0]))
    )
    updated_result = replace_one(
        updated_result,
        r"(?m)^2\. \*\*以关系解锁度推进S4，并当批完成对应S6。\*\*.*$",
        "2. **以关系解锁度推进S4，并当批完成对应S6。** 优先身份锚点清楚、证据充分且能解锁较多候选的直接端点；按对象类型和共同来源簇组织。当前直接端点队列分型为" + direct_priority + "。每组完整核对成员映射、补必要书内字段，并逐条裁决端点齐备的S6候选；组数只用于排队，具体顺序仍按单组能处理的关系候选和证据完整度确定。",
        "S4/S6 plan",
    )

    batch_result = (
        f"### S4/S5/S6 archive：Da Canal《Vita di Gregorio Lazzarini》跨章引注（{DATE}）\n\n"
        f"沿用既有 S3 `new` 组 `archive-group-aa69e7e50bc3`，将 `cand-6593` 登记为 archive KU；第21章书目 L307 记作 *Vita di Gregorio Lazzarini (1732)*、Venezia 1809。括注原样保留，不赋予其未证实含义；作者人物候选 `cand-7781` 不与文献合并。按原书支持新增{len(new_fields)}条 `source_backed` 字段。\n\n"
        f"S6 对第6章 p.166 注2和第7章 p.195 注3两条关系候选逐条裁为 formal `cites`，分别登记 `{new_relation_rows[0]['relation_id']}`、`{new_relation_rows[1]['relation_id']}`。关系只表达 Haskell 的书内引注；出版物及被引页均未独立查阅。批后 S4 {totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条映射；S5字段{planned_field_count:,}条（{current_unverified:,}条 `unverified`）；S6累计{next_s6[0]:,}/{next_s6[1]:,}项裁决；关系表{len(planned_relations):,}条。逐条依据见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。\n"
    )
    date_marker = f"更新日期：{DATE}。\n"
    assert date_marker in updated_result
    updated_result = updated_result.replace(date_marker, date_marker + "\n" + batch_result + "\n", 1)

    # The current overview is the canonical operational snapshot; update its live S4/S5/S6 values.
    direct_group_text = f"{direct_groups:,}组／{direct_members:,}条组成员映射"
    non_direct_text = f"{non_direct_groups:,}组／{non_direct_members:,}条"
    agents_stage_block = (
        f"S4已登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条候选映射；"
        f"待登记{pending_groups:,}组／{pending_members:,}条映射，其中直接关系端点{direct_group_text}，非直接映射{non_direct_text}。"
        f"S5字段表{planned_field_count:,}条、其中{current_unverified:,}条unverified。"
        f"S6关系表{len(planned_relations):,}条（{relation_status['formal']:,} formal、{relation_status['pending']:,} pending），"
        f"过程记录累计逐条裁决{next_s6[0]:,}/{next_s6[1]:,}条S2关系候选（{next_s6[2]:,} formal、{next_s6[3]:,} pending、{next_s6[4]:,} rejected）；"
        f"其余{next_s6[1]-next_s6[0]:,}条待逐项裁决，全部关系均有结构化source_id。"
    )
    agents_text = replace_one(agents_text, r"S4已登记[^。]*。S5字段表[^。]*。S6关系表[^。]*。", agents_stage_block, "AGENTS stage snapshot")

    process_note = f"""

<a id="{ANCHOR}"></a>

### S4/S5/S6 archive：Da Canal《Vita di Gregorio Lazzarini》跨章引注（{DATE}）

沿用 S3 既有 `new` 组 `{SPEC['group']}`，仅将 `cand-6593` 映射到新建 archive KU `{KU_ID}`。第21章书目 p.418 L307 明列 “Canal, Vincenzo da: Vita di Gregorio Lazzarini (1732), Venezia 1809”；身份判断来自本书的书目与跨章引注，不是外部目录或对出版物的直接查阅。题名括注 `(1732)` 照录，不推断为创作年、版本年或其他年代。责任者只保留 Haskell 书目形式；人物候选 `cand-7781` 继续独立。

卡片以第21章书目、第6章 p.166 n.2（L70）和第7章 p.195 n.3（L105）为来源，新增 {len(new_fields)} 条 `source_backed` 字段。第6章引文 p.69 与第7章引文 pp.71–73 都是该出版物的 locator；两处页码不构成不同文献身份。被引页和出版物均未独立核读。

**S6逐条裁决：** 两条候选的端点分别为 `cand-2962`（已登记 `units/archives/patrons-and-painters`）与 `cand-6593`（本批登记为 `{KU_ID}`）。`footnote_citation` 按受控域值映射为 `cites`；两条边分开保留章节、注号和 locator。决定只确认 Haskell 明示引注，不确认被引内容。

| statement_id | 原书定位 | 决定 | 正式关系 |
|---|---|---|---|
| `{STATEMENTS[0]}` | 第6章 p.166 n.2，L70；“da Canal, p. 69” | formal `cites`；只表示书内引注 | `{new_relation_rows[0]['relation_id']}` |
| `{STATEMENTS[1]}` | 第7章 p.195 n.3，L105；“Da Canal, especially pp. 71-3” | formal `cites`；只表示书内引注 | `{new_relation_rows[1]['relation_id']}` |

批后 S4 登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条映射；待登记{pending_groups:,}组／{pending_members:,}条，其中直接端点{direct_groups:,}组／{direct_candidates:,}个候选／{direct_members:,}条成员映射，非直接{non_direct_groups:,}组／{non_direct_members:,}条。S5字段表{planned_field_count:,}条、{current_unverified:,}条 `unverified`。S6累计逐条裁决{next_s6[0]:,}/{next_s6[1]:,}条（{next_s6[2]:,} formal、{next_s6[3]:,} pending、{next_s6[4]:,} rejected）；关系表{len(planned_relations):,}条（{relation_status['formal']:,} formal、{relation_status['pending']:,} pending）。
"""
    updated_process = process_text.rstrip() + process_note

    if args.dry_run:
        print(f"dry-run passed: one existing S3 archive group -> {KU_ID}")
        print(f"source quotes checked: {sum(len(s['quotes']) for s in SPEC['sources'])} across chapters 6, 7, and 21")
        print(f"S5 fields: {len(new_fields)} source_backed; enrichment {planned_field_count-len(new_fields):,}->{planned_field_count:,}")
        print(f"S6: {len(STATEMENTS)} formal cites -> {new_relation_rows[0]['relation_id']} and {new_relation_rows[1]['relation_id']}; domain/range and natural keys pass")
        print(f"S4: {totals['registered_groups']:,}/{totals['new_groups']:,} groups; pending {pending_groups:,} groups/{pending_members:,} mappings")
        print(f"direct endpoint queue: {direct_groups:,} groups/{direct_candidates:,} candidates/{direct_members:,} mappings; types: {format_type_counts(direct_types)}")
        print("planned writes: one card; accepted.yml; ku-manifest.csv; alignment.csv; relations.csv; enrichment.jsonl; process/result/AGENTS snapshots")
        return 0

    (ROOT / CARD_PATH).parent.mkdir(parents=True, exist_ok=True)
    write_text_preserving(ROOT / CARD_PATH, card_text)
    write_csv_preserving(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv_preserving(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    write_csv_preserving(RELATIONS_PATH, relation_fields, planned_relations)
    write_text_preserving(ACCEPTED_PATH, planned_accepted)
    with ENRICHMENT_PATH.open("a", encoding="utf-8", newline="\n") as handle:
        for row in planned_enrichment:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    write_text_preserving(PROCESS_PATH, updated_process)
    write_text_preserving(RESULT_PATH, updated_result.rstrip() + "\n")
    write_text_preserving(AGENTS_PATH, agents_text)
    print(f"applied: one archive KU; S4 registered {totals['registered_groups']:,}/{totals['new_groups']:,} groups")
    print(f"S6: 2 formal cites ({new_relation_rows[0]['relation_id']}, {new_relation_rows[1]['relation_id']}); S5: {len(new_fields)} source_backed fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
