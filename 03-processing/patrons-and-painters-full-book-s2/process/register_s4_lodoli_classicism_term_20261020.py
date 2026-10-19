from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
TABLES = ROOT / "04-knowledge" / "tables"
sys.path.insert(0, str(PROCESS_DIR))

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync
import register_s4_work_second_scuola_scheme_20261020 as s4_helpers

PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
AGENTS_PATH = ROOT / "AGENTS.md"

CANDIDATE = "cand-9748"
GROUP = "sg3-term-cand-9748"
KU_ID = "units/terms/classicism-emerging-against-late-baroque-lodoli-account"
CARD_REL = "04-knowledge/units/terms/classicism-emerging-against-late-baroque-lodoli-account.md"
NAME_ZH = "洛多利论述中取代晚期巴洛克的古典主义"
NAME_EN = "Classicism Beginning to Replace the Late Baroque in Lodoli's Account"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
DATE = "2026-10-20"
ANCHOR = "s4-term-lodoli-emerging-classicism-20261020"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
QUOTE_321 = (
    "In this way he was rejecting not merely the late Baroque of his own youth, "
    "but also the classicism that was beginning to replace it."
)
QUOTE_322 = (
    "Lodoli’s keenest admirers, Andrea Memmo, Angelo Querini and Filippo Farsetti, "
    "all became strong supporters of that very classicism which Lodoli had questioned."
)
RELATION_IDS = {
    "st-chp10-p321-lodoli-rejected-emerging-classicism",
    "st-chp10-p322-farsetti-supports-classicism-questioned-by-lodoli",
    "st-chp10-p322-memmo-supports-classicism-questioned-by-lodoli",
    "st-chp10-p322-querini-supports-classicism-questioned-by-lodoli",
}
DIRECT_IDS = RELATION_IDS


def normalized(text: str) -> str:
    return " ".join(text.split())


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页321–322，来源转录 L168、L176–178",
            "sentence_summary": (
                "Haskell称洛多利所反对的样式还包括正在取代晚期巴洛克的古典主义；"
                "他又称洛多利的几位仰慕者后来支持的正是该古典主义。"
            ),
            "original_quotes": [
                {"source_span": "line 168; print p. 321", "text": QUOTE_321},
                {"source_span": "lines 176–178; print p. 322", "text": QUOTE_322},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "line 168; lines 176–178; print pp. 321–322",
            },
        }],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p321 = f"[第10章 p.321](../../../{SOURCE_FILE}#L168)"
    p322 = f"[第10章 p.322](../../../{SOURCE_FILE}#L177)"
    relations = "、".join(f"`{statement_id}`" for statement_id in sorted(RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** 本术语限于 Haskell 第10章所述、开始取代晚期巴洛克建筑的古典主义。Haskell 将洛多利主张功能性建筑解释为同时拒绝晚期巴洛克及这一新兴古典主义；他又称洛多利的几位仰慕者后来支持的正是该古典主义。本卡保留 Haskell 的历史叙述与作者判断，不扩写为普遍流派定义。{p321} {p322}

**English:** This term is limited to the classicism Haskell describes as beginning to replace late Baroque architecture. He interprets Lodoli's functional architectural position as rejecting both the late Baroque and this emerging classicism, then says that Lodoli's admirers later supported that same classicism. The unit preserves Haskell's account and attribution without expanding it into a general definition of an artistic movement. {p321} {p322}

### 名称

来源原文使用英文词 “classicism”。本卡以“{NAME_ZH}”作为按来源范围限定的描述性中文名称，不将其称为正式流派名称。{p321}

### 释义

Haskell 将其指为正在取代晚期巴洛克建筑、且被洛多利质疑的古典主义。他没有在本段给出更细的正式流派边界。{p321} {p322}

### 本章相关内容

第321页称洛多利反对晚期巴洛克，也反对正在取代它的古典主义；第322页以 “that very classicism” 回指前述对象，并说 Andrea Memmo、Angelo Querini 与 Filippo Farsetti 后来支持该古典主义。两处按来源中的明确回指保留为同一来源局部概念；此 S4 登记不判定它与其他古典主义候选或既有“新古典主义”知识元相同。{p321} {p322}

## 关系与证据

当前没有以本 KU 为端点的 S6 formal 关系。以下四条直接 S2 关系候选在 S4 登记后具备端点映射，仍须在 S6 逐条裁决；本卡不预判其正式关系类型、方向或成立状态：{relations}。
"""
    return f"---\n{fm}---\n\n{body}"


def preserve_bom_write_csv(path: Path, fieldnames, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fieldnames, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register one source-backed Chapter 10 S4 term endpoint.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_candidate = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    candidate_row = candidate_by_id[CANDIDATE]
    alignment = alignment_by_candidate[CANDIDATE]

    assert candidate_row.get("suggested_type") == "term"
    assert alignment.get("decision") == "new" and not alignment.get("ku_id")
    assert result_sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row.get("candidate_id") for row in group_rows] == [CANDIDATE]
    assert not (ROOT / CARD_REL).exists()
    assert KU_ID not in manifest_by_id
    assert not any(row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "term"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for row in manifest
    )

    source_text = normalized((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig"))
    assert normalized(QUOTE_321) in source_text
    assert normalized(QUOTE_322) in source_text
    statements = result_sync.load_statements()
    direct = [
        row for row in statements
        if CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    ]
    direct_ids = {row["statement_id"] for row in direct}
    relation_ids = {
        row["statement_id"] for row in direct
        if row.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert direct_ids == DIRECT_IDS, (direct_ids - DIRECT_IDS, DIRECT_IDS - direct_ids)
    assert relation_ids == RELATION_IDS, (relation_ids - RELATION_IDS, RELATION_IDS - relation_ids)

    for statement in direct:
        if statement["statement_id"] not in RELATION_IDS:
            continue
        other_candidates = {
            endpoint for endpoint in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
            if endpoint and endpoint != CANDIDATE
        }
        assert len(other_candidates) == 1, statement["statement_id"]
        for endpoint in other_candidates:
            mapped_ku = alignment_by_candidate.get(endpoint, {}).get("ku_id", "")
            assert mapped_ku and mapped_ku in manifest_by_id, (statement["statement_id"], endpoint)
            assert (ROOT / manifest_by_id[mapped_ku]["card_path"]).exists(), (statement["statement_id"], mapped_ku)

    relations_fields, relations = result_sync.read_csv(TABLES / "relations.csv")
    assert not any(
        row.get("subject_ku_id") == KU_ID or row.get("object_ku_id") == KU_ID
        for row in relations
    ), "new KU must not inherit or fabricate S6 formal relations"

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] = (
        target.get("resolution_note", "")
        + f" S4 registration: mapped {GROUP} to {KU_ID}; source-local classicism referent in Haskell's Chapter 10, pp. 321–322; "
        "not merged with other classicism candidates or the existing Neo-classicism KU without further S3 evidence."
    )
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID, "type": "term", "canonical_name": NAME_ZH, "name_en": NAME_EN,
        "source_task": TASK, "card_path": CARD_REL,
    }]
    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    before_queue = s4_helpers.compute_direct_queue(candidate_by_id, alignments, statements)
    after_queue = s4_helpers.compute_direct_queue(candidate_by_id, planned_alignment, statements)
    assert before_queue["groups"] == after_queue["groups"] + 1
    assert before_queue["members"] == after_queue["members"] + 1
    assert before_queue["endpoint_candidates"] == after_queue["endpoint_candidates"] + 1

    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text = result_text.rstrip() + (
        "\n\n### S4 term：洛多利论述中的新兴古典主义端点（2026-10-20）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）沿用既有 S3 `new` 决定，登记为来源局部术语“{NAME_ZH}”。"
        "第10章 p.321 称该古典主义正在取代晚期巴洛克、并处于洛多利反对的样式之列；p.322 的 “that very classicism” "
        "明确回指前者，称 Memmo、Querini、Farsetti 后来支持它。按来源回指将两处映射到同一 S3 组；不自动并入既有 Neo-classicism KU。"
        "四条直接 S2 关系候选的另一端均已有 KU，本批补齐该端点映射；关系仍待 S6 逐条裁决，不写 formal 边、外部身份或 S5 字段。"
        f"登记后 S4 为 {result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])} 组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])} 条映射；"
        f"待登记 {result_sync.fmt(totals['pending_groups'])} 组／{result_sync.fmt(totals['pending_members'])} 条映射。\n"
    )

    process_text = s4_helpers.refresh_knowledge_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 term：洛多利论述中的新兴古典主义端点（2026-10-20）\n\n"
        f"按既有 S3 决定，`{CANDIDATE}`（`{GROUP}`）登记为[洛多利论述中取代晚期巴洛克的古典主义]"
        f"(../../../{CARD_REL})。来源第10章 p.321 的 “classicism that was beginning to replace it” "
        "与 p.322 的 “that very classicism” 由明确回指连接；候选提及 `m-s2-ch10-p321-0012`、"
        "`m-s2-ch10-p322-0006` 保留在同一来源局部概念组。现有 `neo-classicism` KU 的章前序言用法并未证明与本处相同，"
        "因此本批落实既有 new 组，不自动合并。\n\n"
        "该组直接涉及四条 S2 关系候选：`st-chp10-p321-lodoli-rejected-emerging-classicism`、"
        "`st-chp10-p322-farsetti-supports-classicism-questioned-by-lodoli`、"
        "`st-chp10-p322-memmo-supports-classicism-questioned-by-lodoli`、"
        "`st-chp10-p322-querini-supports-classicism-questioned-by-lodoli`；四条的其他端点均已映射至有效 KU。"
        "它们只因本次登记而具备完整 S4 端点映射，尚未进行 S6 语义裁决；本批未写正式关系、外部身份或 S5 字段。\n\n"
        f"登记后 S4 已登记 {result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])} 组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])} 条候选映射；"
        f"待登记 {result_sync.fmt(totals['pending_groups'])} 组／{result_sync.fmt(totals['pending_members'])} 条映射。"
        f"直接端点队列由 {before_queue['groups']} 组／{before_queue['members']} 条成员映射降至 "
        f"{after_queue['groups']} 组／{after_queue['members']} 条成员映射。"
    )

    enrichment = [
        json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    agents_text = s4_helpers.refresh_agents(
        AGENTS_PATH.read_text(encoding="utf-8-sig"), totals, after_queue,
        statements, relations, enrichment,
    )

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert CARD_REL not in "\n".join(accepted_lines)
    insert_at = next((i for i, line in enumerate(accepted_lines)
        if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)))
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 Lodoli-classicism dry-run passed: {CANDIDATE} -> {KU_ID}")
        print("source anchors=Chapter 10 pp.321–322; identity group has one member; direct S2 relation candidates=4")
        print(f"all four counterpart KU/card mappings exist; no S6 formal relation created")
        print(f"S4 groups={totals['registered_groups']:,}/{totals['new_groups']:,}; mappings={totals['registered_members']:,}/{totals['new_candidates']:,}")
        print(f"direct queue={before_queue['groups']:,}/{before_queue['members']:,} -> {after_queue['groups']:,}/{after_queue['members']:,}")
        print("result, process record, and AGENTS snapshot refreshed in memory only")
        return 0

    (ROOT / CARD_REL).write_text(make_card(), encoding="utf-8", newline="\n")
    preserve_bom_write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    preserve_bom_write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(f"applied: registered {GROUP}; direct endpoint queue {before_queue['groups']} -> {after_queue['groups']} groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
