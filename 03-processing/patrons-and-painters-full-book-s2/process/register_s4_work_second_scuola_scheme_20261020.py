from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
AGENTS_PATH = ROOT / "AGENTS.md"

CANDIDATE = "cand-8742"
GROUP = "workgrp-30ad0d8bb1910a"
KU_ID = "units/works/scuola-del-carmine-second-ceiling-scheme"
CARD_REL = "04-knowledge/units/works/scuola-del-carmine-second-ceiling-scheme.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "卡尔米内学院第二套天顶装饰方案"
NAME_EN = "Second Ceiling Decoration Scheme for the Scuola del Carmine"
SOURCE_FILE = "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980), ch. 9, p. 273."
)
DIRECT_IDS = {
    "st-chp9-p273-second-scheme-chosen-and-executed",
    "st-chp9-p273-second-scheme-virtues",
    "st-chp9-p273-tiepolo-proposed-second-scuola-scheme",
    "st-chp9-p273-second-scheme-depicts-faith",
    "st-chp9-p273-second-scheme-depicts-hope",
    "st-chp9-p273-second-scheme-depicts-charity",
}
RELATION_IDS = DIRECT_IDS - {"st-chp9-p273-second-scheme-virtues"}
QUOTES = (
    ("line 67; print p. 273", "Tiepolo proposed two alternatives."),
    ("line 67; print p. 273", "the surrounding canvases were to depict the virtues"),
    (
        "line 67; print p. 273",
        "this second plan was chosen and carried out with a few modifications.",
    ),
)


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第9章，印刷页273，来源转录第67行",
                "sentence_summary": (
                    "Haskell 称 Tiepolo 为 Scuola del Carmine 主厅装饰提出两个方案。"
                    "第二方案以启迪兄弟会成员的德性为周围画布主题，包括信、望、爱及其他德性；"
                    "Haskell 称第二方案经少量修改后被选中并实施。"
                ),
                "original_quotes": [
                    {"source_span": span, "text": quote} for span, quote in QUOTES
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "line 67; print p. 273",
                },
            }
        ],
        "created": "2026-10-20",
        "updated": "2026-10-20",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p273 = "[第9章 p.273](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L67）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Haskell 所述 Tiepolo 为 Scuola del Carmine 主厅装饰提出的第二套方案。两种方案共用拟置于天顶中央的圣母像：圣母与先知以利亚、以利沙及天使同在，并将肩衣交给圣西门·斯托克。第二套方案把周围画布设想为启迪兄弟会成员的德性形象，包括信、望、爱及其他未具名德性。Haskell 称第二方案被选中并经少量修改后实施。此卡登记的是书内可辨认的设计对象，不把其内容逐项等同于存世画作，也不重建未详述的最终配置。{p273}

**English:** This card records the second scheme that Haskell says Tiepolo proposed for decorating the main room of the Scuola del Carmine. Both alternatives shared a planned central ceiling panel showing the Virgin with Elijah, Elisha, and angels handing the scapular to St Simeon Stock. In the second scheme, the surrounding canvases were to represent virtues that should inspire the Brethren, including Faith, Hope, Charity, and other unnamed virtues. Haskell says this second plan was selected and carried out with a few modifications. This unit identifies the design described in the book; it does not equate each planned subject with a surviving canvas or reconstruct the unspecified final arrangement. {p273}

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性暂题 | {NAME_ZH} / {NAME_EN} | S1；第9章 p.273 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 对象性质 | 主厅天顶装饰的第二套设计方案；属于可辨认的 work 设计对象 | S1；第9章 p.273 |
| 提案者 | Haskell 称 Tiepolo 提出两个备选方案；此处保留为书内记述，不以本卡登记建立正式关系 | S1；第9章 p.273 |
| 共同中央构图 | 两个方案均设圣母、以利亚、以利沙与天使向圣西门·斯托克交付肩衣 | S1；第9章 p.273 |
| 第二方案的周围画布主题 | 启迪兄弟会成员的德性；明列 Faith、Hope、Charity，另有未具名项目 | S1；第9章 p.273 |
| 书内实施状态 | Haskell 称第二方案被选中并经少量修改后实施；具体修改及最终画布对应关系未在此处说明 | S1；第9章 p.273 |

### 本章相关内容

第一方案的周围画布表现兄弟会成员获救的特权，第二方案则改为德性主题；两个提案共用中央构图。Haskell 另称 Tiepolo 对德性的描述取自 Ripa 的图像志手册插图，并以“must have known by heart”作作者推断。本卡保留方案的书内语境，不据此补写外部作者关系或存世作品身份。{p273}

## 关系与证据

### 正式关系

本次没有新增正式关系。6 条直接 S2 statement 中，5 条标记为关系候选，分别涉及 Tiepolo 提案、方案选择及三项具名德性；均留待 S6 逐条裁决：{", ".join(f"`{item}`" for item in sorted(RELATION_IDS))}。
"""
    return f"---\n{fm}---\n\n{body}"


def build_knowledge_table(stats: dict) -> str:
    lines = [
        "| 类型 | 候选 | same | new（组/成员） | conflict | excluded | undecided | S4已登记（组/成员） | S4待登记（组/成员） |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    totals = defaultdict(int)
    keys = (
        "total", "same_candidates", "new_groups", "new_candidates", "conflict",
        "excluded", "undecided", "registered_groups", "registered_members",
        "pending_groups", "pending_members",
    )
    for kind in result_sync.TYPE_ORDER:
        item = stats[kind]
        label = kind
        lines.append(
            f"| {label} | {result_sync.fmt(item['total'])} | "
            f"{result_sync.fmt(item['same_candidates'])} | "
            f"{result_sync.fmt(item['new_groups'])} / {result_sync.fmt(item['new_candidates'])} | "
            f"{result_sync.fmt(item['conflict'])} | {result_sync.fmt(item['excluded'])} | "
            f"{result_sync.fmt(item['undecided'])} | "
            f"{result_sync.fmt(item['registered_groups'])} / {result_sync.fmt(item['registered_members'])} | "
            f"{result_sync.fmt(item['pending_groups'])} / {result_sync.fmt(item['pending_members'])} |"
        )
        for key in keys:
            totals[key] += item[key]
    lines.append(
        f"| **合计** | **{result_sync.fmt(totals['total'])}** | "
        f"**{result_sync.fmt(totals['same_candidates'])}** | "
        f"**{result_sync.fmt(totals['new_groups'])} / {result_sync.fmt(totals['new_candidates'])}** | "
        f"**{result_sync.fmt(totals['conflict'])}** | **{result_sync.fmt(totals['excluded'])}** | "
        f"**{result_sync.fmt(totals['undecided'])}** | "
        f"**{result_sync.fmt(totals['registered_groups'])} / {result_sync.fmt(totals['registered_members'])}** | "
        f"**{result_sync.fmt(totals['pending_groups'])} / {result_sync.fmt(totals['pending_members'])}** |"
    )
    return "\n".join(lines)


def refresh_knowledge_table(text: str, stats: dict) -> str:
    header = "| 类型 | 候选 | same | new（组/成员） | conflict | excluded | undecided | S4已登记（组/成员） | S4待登记（组/成员） |"
    start = text.index(header)
    end = text.index("\n\n", start)
    return text[:start] + build_knowledge_table(stats) + text[end:]


def compute_direct_queue(candidate_by_id: dict, alignments: list, statements: list) -> dict:
    endpoint_ids = set()
    for statement in statements:
        if statement.get("qualifiers", {}).get("relation_candidate") is not True:
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            candidate_id = statement.get(key)
            if candidate_id in candidate_by_id:
                endpoint_ids.add(candidate_id)

    new_groups = defaultdict(list)
    for row in alignments:
        candidate_id = row.get("candidate_id", "")
        if (
            candidate_id in candidate_by_id
            and row.get("decision") == "new"
            and not row.get("external_source")
        ):
            group = result_sync.get_group(row.get("resolution_note", ""))
            assert group
            new_groups[group].append(row)

    pending = {}
    for group, members in new_groups.items():
        mapped = [member.get("ku_id", "") for member in members]
        if all(mapped):
            assert len(set(mapped)) == 1
            continue
        assert not any(mapped), f"partially registered group: {group}"
        pending[group] = members

    direct = {
        group: members
        for group, members in pending.items()
        if any(member.get("candidate_id") in endpoint_ids for member in members)
    }
    type_stats = defaultdict(lambda: {"groups": 0, "members": 0, "endpoint_candidates": 0})
    direct_candidate_ids = set()
    for members in direct.values():
        kind = candidate_by_id[members[0]["candidate_id"]].get("suggested_type", "") or "未分类"
        type_stats[kind]["groups"] += 1
        type_stats[kind]["members"] += len(members)
        for member in members:
            if member.get("candidate_id") in endpoint_ids:
                direct_candidate_ids.add(member["candidate_id"])
    for kind, values in type_stats.items():
        values["endpoint_candidates"] = sum(
            1
            for members in direct.values()
            for member in members
            if member.get("candidate_id") in endpoint_ids
            and (candidate_by_id[member["candidate_id"]].get("suggested_type", "") or "未分类") == kind
        )
    return {
        "groups": len(direct),
        "members": sum(len(members) for members in direct.values()),
        "endpoint_candidates": len(direct_candidate_ids),
        "types": dict(type_stats),
        "non_direct_groups": len(pending) - len(direct),
        "non_direct_members": sum(len(members) for members in pending.values())
        - sum(len(members) for members in direct.values()),
    }


def refresh_agents(text: str, totals: dict, direct: dict, statements: list, relations: list, enrichment: list) -> str:
    relation_candidates = [
        row for row in statements
        if row.get("qualifiers", {}).get("relation_candidate") is True
    ]
    missing_subject_only = sum(
        not row.get("subject_candidate_id") and bool(row.get("object_candidate_id"))
        for row in relation_candidates
    )
    missing_object_only = sum(
        bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id")
        for row in relation_candidates
    )
    missing_both = sum(
        not row.get("subject_candidate_id") and not row.get("object_candidate_id")
        for row in relation_candidates
    )
    missing_any = sum(
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
        for row in relation_candidates
    )
    source_missing = [row for row in relations if not row.get("source_id")]
    formal_missing = sum(row.get("status") == "formal" for row in source_missing)
    pending_missing = sum(row.get("status") == "pending" for row in source_missing)
    unverified = sum(
        str(row.get("evidence_status", row.get("verification_status", row.get("status", "")))).casefold() == "unverified"
        for row in enrichment
    )
    kinds = {
        "person": "人物", "institution": "机构", "event": "事件", "place": "地点",
        "work": "作品", "archive": "档案", "term": "术语",
    }
    queue_details = "、".join(
        f"{kinds.get(kind, kind)} {values['groups']}组／{values['members']}成员"
        for kind, values in sorted(direct["types"].items(), key=lambda item: item[0])
    )
    summary = (
        f"项目版本为初始化阶段的 0.1.0；全书 S2 内部处理已完成，尚未独立语义验收。当前快照（2026-10-20）："
        f"S3 决定记录覆盖 {result_sync.fmt(totals['total'])} 个候选且均有可追溯去向："
        f"same={result_sync.fmt(totals['same_candidates'])}（指向 {result_sync.fmt(totals['same_kus'])} 个既有 KU）、"
        f"new={result_sync.fmt(totals['new_candidates'])}（{result_sync.fmt(totals['new_groups'])} 个身份组）、"
        f"conflict={result_sync.fmt(totals['conflict'])}、excluded={result_sync.fmt(totals['excluded'])}、"
        f"undecided={result_sync.fmt(totals['undecided'])}（其中 622 项未分类）；这表示决定记录覆盖齐全，不表示冲突与待证身份已解决。"
        f"S4 已登记 {result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])} 个新增身份组 "
        f"（{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])} 条候选映射），"
        f"待登记 {result_sync.fmt(totals['pending_groups'])} 组／{result_sync.fmt(totals['pending_members'])} 条映射；"
        f"直接关系端点待登队列为 {direct['groups']} 组／{direct['endpoint_candidates']} 个候选／{direct['members']} 条组成员映射"
        f"（{queue_details}），另有 {direct['non_direct_groups']} 组／{direct['non_direct_members']} 条非直接映射待登记。"
        f"S2 有 {len(relation_candidates):,} 条关系候选；{missing_any:,} 条至少缺一个候选端点ID"
        f"（仅缺object {missing_object_only:,}、仅缺subject {missing_subject_only:,}、两端均缺 {missing_both:,}）。"
        f"S6关系表有 {len(relations):,} 条记录（{sum(row.get('status') == 'formal' for row in relations):,} formal、"
        f"{sum(row.get('status') == 'pending' for row in relations):,} pending），其中 {len(source_missing):,} 条缺结构化source_id"
        f"（{formal_missing:,}条formal、{pending_missing:,}条pending）。"
        f"S5字段表 {len(enrichment):,} 条、其中 {unverified:,} 条unverified；S5、S6尚未全书收口。"
        f"S6关系表行数不代表S2候选的逐条裁决覆盖。旧批次计数以[全书当前结果](04-knowledge/results/patrons-and-painters-full-book-s2.md)"
        "及其结构化表为准；[第一章结果](04-knowledge/results/patrons-and-painters-chp-1.md)仅说明独立历史任务，不由规则版本或文件数量推导全书完成。"
        "知识发现与页面暂停。有效对象见 [accepted.yml](04-knowledge/accepted.yml)；遗留文件与未处理来源不自动成为成果。"
    )
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith("项目版本为初始化阶段的")]
    assert len(matches) == 1
    lines[matches[0]] = summary
    return "\n".join(lines) + "\n"


def preserve_bom_write_csv(path: Path, fieldnames, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fieldnames, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the second Scuola del Carmine ceiling scheme in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_rows = [
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(candidate_rows) == 1
    target = candidate_rows[0]
    assert candidate_by_id[CANDIDATE].get("suggested_type") == "work"
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert result_sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row.get("candidate_id") for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    assert not any(
        row.get("type") == "work"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for row in manifest
    ), "same-title work already exists in the manifest"

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for _, quote in QUOTES:
        assert " ".join(quote.split()) in source_text, quote

    statements = result_sync.load_statements()
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_ids = {row["statement_id"] for row in direct_statements}
    relation_ids = {
        row["statement_id"] for row in direct_statements
        if row.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert direct_ids == DIRECT_IDS, (direct_ids - DIRECT_IDS, DIRECT_IDS - direct_ids)
    assert relation_ids == RELATION_IDS, (relation_ids - RELATION_IDS, RELATION_IDS - relation_ids)

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] = (
        (planned_target.get("resolution_note") or "")
        + f" S4 registration: mapped {GROUP} to {KU_ID}; card identifies the source-described second scheme, "
        "not a reconstruction of the exact executed canvas programme."
    )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    direct_queue = compute_direct_queue(candidate_by_id, planned_alignment, statements)
    before_queue = compute_direct_queue(candidate_by_id, alignments, statements)
    assert before_queue["groups"] == direct_queue["groups"] + 1
    assert before_queue["members"] == direct_queue["members"] + 1
    assert before_queue["endpoint_candidates"] == direct_queue["endpoint_candidates"] + 1
    assert direct_statements

    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text += (
        "\n\n### S4 work：Scuola del Carmine 第二套天顶装饰方案（2026-10-20）\n\n"
        f"`{CANDIDATE}` 沿用既有 S3 `new` 组 `{GROUP}`，登记至"
        f"[第二套天顶装饰方案卡](../units/works/scuola-del-carmine-second-ceiling-scheme.md)。"
        "第9章 p.273 称 Tiepolo 提出两种主厅装饰方案；第二方案以启迪兄弟会的德性为周围画布主题，"
        "并与第一方案区分。Haskell 称第二方案经少量修改后被选择并实施；本卡不推定具体修改、存世画作身份或最终配置。"
        f"6条直接 S2 statement 中5条关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6；"
        "本批未改动 S2 statements/mentions，未新增 formal 关系、外部身份核验或 S5 补足。"
        f"S4 当前登记 {result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])} 组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])} 条映射；"
        f"待登记 {result_sync.fmt(totals['pending_groups'])} 组／{result_sync.fmt(totals['pending_members'])} 条映射。"
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text = refresh_knowledge_table(process_text, stats)
    process_text += (
        "\n\n### S4 work：Scuola del Carmine 第二套天顶装饰方案（2026-10-20）\n\n"
        f"`{CANDIDATE}` 沿用既有 S3 `new` 身份组 `{GROUP}`，登记为"
        f"[第二套天顶装饰方案卡](../../../{CARD_REL})。第9章 p.273 称 Tiepolo 提出主厅装饰的两个方案，"
        "第二方案拟以 Faith、Hope、Charity 等德性装饰周围画布；中央画面与第一方案相同。Haskell 称该第二方案经少量修改后被选中并实施。"
        "卡片将其限定为来源描述的设计对象，不声称已核实任何对应存世画布、修改细节或最终配置；未新增外部身份或 S5 字段。"
        f"6条直接 S2 statement 中5条关系候选（{', '.join(sorted(RELATION_IDS))}）保留待 S6；本批未写入正式关系。"
        f"登记后 S4 已登记 {result_sync.fmt(totals['registered_groups'])} 组／{result_sync.fmt(totals['registered_members'])} 条候选映射，"
        f"待登记 {result_sync.fmt(totals['pending_groups'])} 组／{result_sync.fmt(totals['pending_members'])} 条映射。"
    )
    agents_text = refresh_agents(
        AGENTS_PATH.read_text(encoding="utf-8-sig"), totals, direct_queue,
        statements, result_sync.read_csv(TABLES / "relations.csv")[1],
        [json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()],
    )

    if args.dry_run:
        print(f"S4 work dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"group members={len(group_rows)}; direct statements={len(direct_statements)}; relation candidates={len(relation_ids)}")
        print(f"source quotations checked={len(QUOTES)}; no surviving-canvas identity or exact executed scheme inferred")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(
            f"registered={totals['registered_groups']:,}/{totals['new_groups']:,} groups, "
            f"{totals['registered_members']:,}/{totals['new_candidates']:,} mappings; "
            f"pending={totals['pending_groups']:,} groups/{totals['pending_members']:,} mappings"
        )
        print(
            f"direct endpoint queue={before_queue['groups']:,} groups/{before_queue['members']:,} members "
            f"-> {direct_queue['groups']:,}/{direct_queue['members']:,}; "
            f"non-direct={direct_queue['non_direct_groups']:,}/{direct_queue['non_direct_members']:,}"
        )
        print("knowledge.md type table, current result, and AGENTS.md snapshot refreshed in memory only")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8", newline="\n")
    preserve_bom_write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    preserve_bom_write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (
            i for i, line in enumerate(accepted_lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']:,}/{totals['registered_members']:,}; "
        f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}; "
        f"direct={before_queue['groups']:,}->{direct_queue['groups']:,} groups"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
