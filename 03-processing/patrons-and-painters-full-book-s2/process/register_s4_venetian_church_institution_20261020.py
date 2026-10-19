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

CANDIDATE = "cand-8672"
GROUP = "sg3-institution-cand-8672"
KU_ID = "units/institutions/church-as-patron-in-venice-haskell-account"
CARD_REL = "04-knowledge/units/institutions/church-as-patron-in-venice-haskell-account.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "哈斯克尔威尼斯叙述中的教会机构"
NAME_EN = "The Church as an institution in Haskell's Venetian account"
DATE = "2026-10-20"
PROCESS_ANCHOR = "s4-institution-church-as-patron-in-venice-20261020"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
SOURCE_FILE = "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
RELATION_IDS = {
    "st-chp9-p268-church-altarpiece-market",
    "st-chp9-p268-church-decoration-patrician-ideals",
    "st-chp9-p268-church-leading-patron",
    "st-chp9-p268-history-painters-church-work",
    "st-chp9-p268-noble-commissions",
}
DIRECT_NONRELATION_IDS = {"st-chp9-p268-venetian-piety-lavishness"}
SOURCES = [
    ("line 9; print p. 268", "Haskell称教会保有或提升了其在威尼斯当代艺术赞助中的领先地位。",
     "the Church retained or even increased the position she had always held as the leading patron of-contemporary art in Venice"),
    ("line 9; print p. 268", "Haskell概括威尼斯历史画家为教会创作的比例；保留其作者性估计。",
     "Of the history painters in the city virtually all devoted well over half their work to the Church"),
    ("line 10; print p. 268", "Haskell将教会对祭坛画的持续需求与现代绘画市场联系起来。",
     "With its constant demand for altarpieces the Church provided a market for modern painting that was lacking elsewhere"),
    ("line 11; print p. 268", "Haskell称教堂装饰同宫殿装饰一样反映贵族理想。",
     "the decoration of churches reflected patrician ideals fully as much as that of their palaces"),
    ("line 13; print p. 268", "Haskell称许多贵族直接负责相关委托，并在宫殿和教堂中雇用其偏爱的画家。",
     "Many nobles were, indeed, themselves directly responsible for the commissions involved and employed their own favourite artists in palace and church alike"),
]


def make_card() -> str:
    source_rows = [{
        "citation": BOOK_CITATION,
        "location": f"第9章，印刷页268，来源转录 {span}",
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": span,
        },
    } for span, summary, quote in SOURCES]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "institution",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p268_9 = f"[第9章 p.268，L9](../../../{SOURCE_FILE}#L9)"
    p268_10 = f"[第9章 p.268，L10](../../../{SOURCE_FILE}#L10)"
    p268_11 = f"[第9章 p.268，L11](../../../{SOURCE_FILE}#L11)"
    p268_13 = f"[第9章 p.268，L13](../../../{SOURCE_FILE}#L13)"
    body = f"""## 内容

### 描述

**中文：** 本卡按 S3 的 `institution` 裁决，记录 Haskell 第9章 p.268 所称在威尼斯承担艺术赞助角色的“the Church”。作者将其描述为当代艺术的领先赞助者、祭坛画需求的来源，并将教会装饰与贵族理想相联系。这里是书内叙述中的集体性机构主体；来源段没有界定其法律组织边界、具体分支或跨时期连续性。本卡不把它等同于威尼斯共和国、教宗职位、教廷国家或任何一座教堂建筑，也不以这些段落确立外部机构身份。{p268_9}；{p268_10}；{p268_11}

**English:** Following the S3 `institution` decision, this card records “the Church” as Haskell uses it on p. 268 of Chapter 9 for the institutional patron of art in Venice. The author describes it as a leading patron of contemporary art, a source of demand for altarpieces, and an institution whose church decoration reflected patrician ideals. The passage treats it as a collective institutional actor but does not define its legal organization, specific branches, or continuity across periods. This card does not equate it with the Venetian Republic, the papal office, the Papal States, or any individual church building, and the passage does not establish an external institutional identity. {p268_9}; {p268_10}; {p268_11}

### 书内角色

- 艺术赞助：Haskell称教会保有或增强其在威尼斯当代艺术中的领先赞助地位。{p268_9}
- 委托与市场语境：Haskell将持续的祭坛画需求与现代绘画市场相联系；未据此推定具体委托或画家。{p268_10}
- 装饰与社会理想：Haskell将威尼斯教堂装饰与贵族理想并置，并称许多贵族直接负责委托、在宫殿和教堂雇用偏爱的画家。{p268_11}；{p268_13}
- Haskell关于历史画家为教会创作比例的说法是作者的概括与估计，本卡不将其转写为已独立核验的统计。{p268_9}

## 关系与证据

### 关系记录

以下5条直接 S2 关系候选留待 S6 逐条裁决；本卡不预判关系类型、方向或事实成立：{", ".join(f"`{item}`" for item in sorted(RELATION_IDS))}。
"""
    return f"---\n{fm}---\n\n{body}"


def preserve_bom_write_csv(path: Path, fieldnames, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fieldnames, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Venetian Church institution in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert candidate_by_id[CANDIDATE].get("suggested_type") == "institution"
    target_rows = [row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(target_rows) == 1
    target = target_rows[0]
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert result_sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row.get("candidate_id") for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "institution" and row.get("canonical_name", "").casefold() == NAME_ZH.casefold() for row in manifest)

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for _, _, quote in SOURCES:
        assert " ".join(quote.split()) in source_text, quote

    statements = result_sync.load_statements()
    direct_statements = [row for row in statements if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE]
    direct_ids = {row["statement_id"] for row in direct_statements}
    relation_ids = {row["statement_id"] for row in direct_statements if row.get("qualifiers", {}).get("relation_candidate") is True}
    assert direct_ids == RELATION_IDS | DIRECT_NONRELATION_IDS, (
        direct_ids - RELATION_IDS - DIRECT_NONRELATION_IDS,
        RELATION_IDS | DIRECT_NONRELATION_IDS - direct_ids,
    )
    assert relation_ids == RELATION_IDS

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] = (planned_target.get("resolution_note", "")
        + f" S4 registration: mapped {GROUP} to {KU_ID}; source-local institutional Church in Haskell's p.268 Venetian account, distinct from polity, papal office and church buildings.")
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID, "type": "institution", "canonical_name": NAME_ZH, "name_en": NAME_EN,
        "source_task": TASK, "card_path": CARD_REL,
    }]
    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    before_queue = s4_helpers.compute_direct_queue(candidate_by_id, alignments, statements)
    direct_queue = s4_helpers.compute_direct_queue(candidate_by_id, planned_alignment, statements)
    assert before_queue["groups"] == direct_queue["groups"] + 1
    assert before_queue["members"] == direct_queue["members"] + 1
    assert before_queue["endpoint_candidates"] == direct_queue["endpoint_candidates"] + 1

    result_text = result_sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text = result_text.rstrip() + (
        "\n\n### S4 institution：哈斯克尔威尼斯叙述中的教会机构（2026-10-20）\n\n"
        f"`{CANDIDATE}`沿用S3 `new`组 `{GROUP}`，登记至[教会机构卡](../units/institutions/church-as-patron-in-venice-haskell-account.md)。"
        "第9章 p.268 将“the Church”作为威尼斯当代艺术的集体性赞助主体；本卡不与威尼斯共和国、教宗职位、教廷国家或单座教堂合并，不据此推定法律组织边界。"
        "5条直接 S2 关系候选留待 S6；未新增正式关系、外部身份或 S5 字段。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])}组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])}条映射；"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射。\n"
    )

    process_text = s4_helpers.refresh_knowledge_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    process_entry = (
        "\n\n<a id=\"" + PROCESS_ANCHOR + "\"></a>\n\n"
        "### S4 institution：哈斯克尔威尼斯叙述中的教会机构（2026-10-20）\n\n"
        f"`{CANDIDATE}`沿用S3 `new`机构组 `{GROUP}`，登记为[教会机构卡](../../../{CARD_REL})。"
        "类型和身份边界依候选表及S3记录；第9章 p.268 将“the Church”称为威尼斯当代艺术的领先赞助者、祭坛画需求来源，并联系教堂装饰与贵族理想。"
        "本卡只表示书内集体机构主体，不推定法律组织边界、分支或跨时期连续性；与威尼斯共和国、教宗职位、教廷国家及单座教堂保持分立。"
        f"5条直接S2关系候选（{', '.join(sorted(RELATION_IDS))}）仍待S6；本批不登记formal边或S5字段。"
        f"登记后S4已登记{result_sync.fmt(totals['registered_groups'])}组／{result_sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射；"
        f"直接端点队列由{before_queue['groups']}组／{before_queue['members']}成员降至{direct_queue['groups']}组／{direct_queue['members']}成员。"
        "独立S2复核尚在进行，本登记不构成该五条statement或相关章节的语义接收。"
    )
    process_text = process_text.rstrip() + process_entry + "\n"
    enrichment = [json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    agents_text = s4_helpers.refresh_agents(AGENTS_PATH.read_text(encoding="utf-8-sig"), totals, direct_queue,
        statements, result_sync.read_csv(TABLES / "relations.csv")[1], enrichment)

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    accepted_lines = accepted.splitlines()
    insert_at = next((i for i, line in enumerate(accepted_lines)
        if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)))
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 institution dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"source anchor=chapter 9 p.268; direct S2 relation candidates={len(relation_ids)}; no formal edge created")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(f"registered={totals['registered_groups']:,}/{totals['new_groups']:,} groups, {totals['registered_members']:,}/{totals['new_candidates']:,} mappings; pending={totals['pending_groups']:,}/{totals['pending_members']:,}")
        print(f"direct queue={before_queue['groups']:,}/{before_queue['members']:,} -> {direct_queue['groups']:,}/{direct_queue['members']:,}")
        print("result, process table, and AGENTS snapshot refreshed in memory only")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8", newline="\n")
    preserve_bom_write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    preserve_bom_write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(f"applied: {CANDIDATE} -> {KU_ID}; direct={before_queue['groups']}->{direct_queue['groups']} groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
