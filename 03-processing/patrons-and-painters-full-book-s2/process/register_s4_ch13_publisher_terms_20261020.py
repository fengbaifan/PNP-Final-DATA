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

SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
SOURCE_QUOTE = (
    "They dealt either in sets of loose prints or in illustrated books. In either case they employed "
    "the print makers and commissioned drawings or sometimes paintings from the artists they found suitable. "
    "In this way they were considerable patrons in their own right"
)
DATE = "2026-10-20"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)

ITEMS = [
    {
        "candidate": "cand-12120",
        "group": "sg3-term-cand-12120",
        "ku_id": "units/terms/printmakers-employed-by-venetian-publishers",
        "card_rel": "04-knowledge/units/terms/printmakers-employed-by-venetian-publishers.md",
        "zh": "威尼斯出版商雇用的雕版工",
        "en": "Printmakers employed by Venetian publishers",
        "anchor": "s4-term-printmakers-employed-by-publishers-20261020",
        "relations": {
            "st-chp13-p333-publishers-employed-printmakers",
            "st-chp13-p333-publishers-patronized-printmakers",
        },
        "summary_zh": "Haskell称经营散页版画或插图书的出版商雇用雕版工。",
        "summary_en": "Haskell says publishers dealing in loose prints or illustrated books employed printmakers.",
        "description_zh": (
            "本术语记录 Haskell 第13章 p.333 所述由出版商雇用的雕版工群体，语境为经营散页版画或插图书的出版活动。"
            "原文没有列出个人、职业组织或固定成员名单；本卡不表示所有出版商或所有版画制作人员，也不推定该群体与受委托绘图的艺术家群体互不重叠。"
        ),
        "description_en": (
            "This term records the printmakers whom Haskell says publishers employed in the context of producing sets of loose prints or illustrated books (Chapter 13, p. 333). "
            "The passage names no individuals, professional organization, or fixed membership. The term does not cover every publisher or printmaking practitioner, and it does not imply that printmakers and commissioned artists were mutually exclusive groups."
        ),
    },
    {
        "candidate": "cand-12121",
        "group": "sg3-term-cand-12121",
        "ku_id": "units/terms/artists-selected-for-venetian-publishers-commissions",
        "card_rel": "04-knowledge/units/terms/artists-selected-for-venetian-publishers-commissions.md",
        "zh": "威尼斯出版商选用于委托的艺术家",
        "en": "Artists selected for Venetian publishers' commissions",
        "anchor": "s4-term-artists-selected-for-publishers-commissions-20261020",
        "relations": {
            "st-chp13-p333-publishers-as-patrons-and-reliance-on-patronage",
            "st-chp13-p333-publishers-commissioned-suitable-artists",
        },
        "summary_zh": "Haskell称出版商委托适合其出版项目的艺术家绘制图画，有时也作画。",
        "summary_en": "Haskell says publishers commissioned drawings, and sometimes paintings, from artists they found suitable.",
        "description_zh": (
            "本术语记录 Haskell 第13章 p.333 所述由出版商按项目适合度选用的艺术家群体；来源称其受委托绘制图画，有时也绘制油画。"
            "原文未提供个人名单或具体委托对应关系。本卡表示来源定义的选择类别，不表示固定团体，也不推定其成员与出版商雇用的雕版工互斥。"
        ),
        "description_en": (
            "This term records the artists whom Haskell says Venetian publishers selected as suitable for their publishing ventures, commissioning drawings and sometimes paintings from them (Chapter 13, p. 333). "
            "The passage provides no individual list or assignment of particular commissions. The term denotes a source-defined selection category, not a fixed organization, and it does not imply that its members were mutually exclusive from employed printmakers."
        ),
    },
]


def make_card(item: dict) -> str:
    frontmatter = {
        "title": f"{item['zh']}（{item['en']}）",
        "name_en": item["en"],
        "type": "term",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": "第13章，印刷页333，来源转录 L17",
            "sentence_summary": item["summary_zh"],
            "original_quotes": [{"source_span": "line 17; print p. 333", "text": SOURCE_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "line 17; print p. 333",
            },
        }],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    quote_ref = f"[第13章 p.333](../../../{SOURCE_FILE}#L17)"
    relation_list = ", ".join(f"`{sid}`" for sid in sorted(item["relations"]))
    body = f"""## 内容

### 描述

**中文：** {item['description_zh']} {quote_ref}

**English:** {item['description_en']} {quote_ref}

### 本章相关内容

Haskell 将出版商经营的出版形式、其雇用的雕版工和其选用的艺术家置于同一段出版活动叙述中。本术语只保留各候选所指的来源类别，不推定具体人员、委托作品、成员范围或群体边界。{quote_ref}

## 关系与证据

### 关系记录

以下两条直接 S2 关系候选保留待 S6 逐条裁决；本卡不预判关系成立、方向或类型：{relation_list}。
"""
    return f"---\n{fm}---\n\n{body}"


def preserve_bom_write_csv(path: Path, fieldnames, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fieldnames, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two source-backed Chapter 13 term endpoints in S4.")
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
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    assert " ".join(SOURCE_QUOTE.split()) in source_text

    statements = result_sync.load_statements()
    for item in ITEMS:
        candidate = item["candidate"]
        candidate_row = candidate_by_id[candidate]
        alignment = alignment_by_candidate[candidate]
        assert candidate_row.get("suggested_type") == "term"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert result_sync.get_group(alignment.get("resolution_note", "")) == item["group"]
        group_rows = [
            row for row in alignments if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and result_sync.get_group(row.get("resolution_note", "")) == item["group"]
        ]
        assert [row.get("candidate_id") for row in group_rows] == [candidate]
        assert not (ROOT / item["card_rel"]).exists()
        assert item["ku_id"] not in manifest_by_id
        assert not any(row.get("card_path") == item["card_rel"] for row in manifest)
        assert not any(
            row.get("type") == "term" and row.get("name_en", "").casefold() == item["en"].casefold()
            for row in manifest
        )

        direct = [
            row for row in statements
            if row.get("subject_candidate_id") == candidate or row.get("object_candidate_id") == candidate
        ]
        direct_ids = {row["statement_id"] for row in direct}
        relation_ids = {
            row["statement_id"] for row in direct
            if row.get("qualifiers", {}).get("relation_candidate") is True
        }
        assert direct_ids == item["relations"], (candidate, direct_ids - item["relations"], item["relations"] - direct_ids)
        assert relation_ids == item["relations"]
        for statement in direct:
            other_candidates = {
                endpoint for endpoint in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
                if endpoint and endpoint != candidate
            }
            assert other_candidates, statement["statement_id"]
            for endpoint in other_candidates:
                mapped_ku = alignment_by_candidate.get(endpoint, {}).get("ku_id", "")
                assert mapped_ku and mapped_ku in manifest_by_id, (statement["statement_id"], endpoint)
                assert (ROOT / manifest_by_id[mapped_ku]["card_path"]).exists(), (statement["statement_id"], mapped_ku)

    planned_alignment = [dict(row) for row in alignments]
    for item in ITEMS:
        target = next(row for row in planned_alignment if row.get("candidate_id") == item["candidate"] and not row.get("external_source"))
        target["ku_id"] = item["ku_id"]
        target["resolution_note"] = (
            target.get("resolution_note", "")
            + f" S4 registration: mapped {item['group']} to {item['ku_id']}; source-defined term category, no individual membership inferred."
        )
    planned_manifest = list(manifest) + [{
        "ku_id": item["ku_id"], "type": "term", "canonical_name": item["zh"], "name_en": item["en"],
        "source_task": TASK, "card_path": item["card_rel"],
    } for item in ITEMS]
    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    before_queue = s4_helpers.compute_direct_queue(candidate_by_id, alignments, statements)
    direct_queue = s4_helpers.compute_direct_queue(candidate_by_id, planned_alignment, statements)
    assert before_queue["groups"] == direct_queue["groups"] + len(ITEMS)
    assert before_queue["members"] == direct_queue["members"] + len(ITEMS)
    assert before_queue["endpoint_candidates"] == direct_queue["endpoint_candidates"] + len(ITEMS)

    result_text = result_sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text = result_text.rstrip() + (
        "\n\n### S4 term：第13章威尼斯出版商的两个来源类别端点（2026-10-20）\n\n"
        "`cand-12120`与`cand-12121`沿用各自既有S3 `new`术语组，分别登记为出版商雇用的雕版工、"
        "以及出版商选用于图画委托的艺术家类别。两组共享第13章 p.333 的出版活动语境，来源不提供个人名单；"
        "不推定两类人员互斥或完全相同。4条直接S2关系候选留待S6逐条裁决；本批不新增正式关系、外部身份或S5字段。"
        f"登记后S4已登记{result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])}组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])}条映射；"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射。\n"
    )

    process_text = s4_helpers.refresh_knowledge_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    process_entry = (
        "\n\n<a id=\"s4-ch13-publisher-terms-20261020\"></a>\n\n"
        "### S4 term：第13章威尼斯出版商的两个来源类别端点（2026-10-20）\n\n"
        "按候选表和既有S3裁决，`cand-12120`（`sg3-term-cand-12120`）登记为[出版商雇用的雕版工](../../../04-knowledge/units/terms/printmakers-employed-by-venetian-publishers.md)，"
        "`cand-12121`（`sg3-term-cand-12121`）登记为[出版商选用于委托的艺术家](../../../04-knowledge/units/terms/artists-selected-for-venetian-publishers-commissions.md)。"
        "第13章 p.333 将两类来源称谓置于散页版画与插图书出版活动中：出版商雇用 print makers，并委托适合者绘图、有时绘画。"
        "分别保留来源所示类别，不生成成员名单、个人身份或互斥关系。四条直接S2关系候选（`st-chp13-p333-publishers-employed-printmakers`、"
        "`st-chp13-p333-publishers-patronized-printmakers`、`st-chp13-p333-publishers-as-patrons-and-reliance-on-patronage`、"
        "`st-chp13-p333-publishers-commissioned-suitable-artists`）留待S6逐条裁决；不写formal边或S5字段。"
        f"登记后S4已登记{result_sync.fmt(totals['registered_groups'])}组／{result_sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射；"
        f"直接端点队列由{before_queue['groups']}组／{before_queue['members']}成员降至{direct_queue['groups']}组／{direct_queue['members']}成员。"
        "第13章S2独立审读覆盖该页，但章级仍有其他未修问题；本次登记不代表关系成立或章节接收。"
    )
    process_text = process_text.rstrip() + process_entry + "\n"
    enrichment = [
        json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    agents_text = s4_helpers.refresh_agents(
        AGENTS_PATH.read_text(encoding="utf-8-sig"), totals, direct_queue,
        statements, result_sync.read_csv(TABLES / "relations.csv")[1], enrichment,
    )

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_lines = accepted.splitlines()
    planned_paths = []
    for item in ITEMS:
        assert item["card_rel"] not in accepted
        insert_at = next((i for i, line in enumerate(accepted_lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > item["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)))
        accepted_lines.insert(insert_at, f"- {item['card_rel']}")
        planned_paths.append(item["card_rel"])
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("S4 publisher-term dry-run passed: " + "; ".join(
            f"{item['candidate']} -> {item['ku_id']}" for item in ITEMS
        ))
        print(f"source anchor=chapter 13 p.333; direct S2 relation candidates={sum(len(item['relations']) for item in ITEMS)}; no formal edge created")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted paths unique={len(planned_paths)}")
        print(f"registered={totals['registered_groups']:,}/{totals['new_groups']:,} groups, {totals['registered_members']:,}/{totals['new_candidates']:,} mappings; pending={totals['pending_groups']:,}/{totals['pending_members']:,}")
        print(f"direct queue={before_queue['groups']:,}/{before_queue['members']:,} -> {direct_queue['groups']:,}/{direct_queue['members']:,}")
        print("result, process record, and AGENTS snapshot refreshed in memory only")
        return 0

    for item in ITEMS:
        (ROOT / item["card_rel"]).write_text(make_card(item), encoding="utf-8", newline="\n")
    preserve_bom_write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    preserve_bom_write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(f"applied: registered {len(ITEMS)} term groups; direct={before_queue['groups']}->{direct_queue['groups']} groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
