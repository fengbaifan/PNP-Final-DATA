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

CANDIDATE = "cand-8104"
GROUP = "sg3-term-cand-8104"
KU_ID = "units/terms/venetian-artists-collective-category"
CARD_REL = "04-knowledge/units/terms/venetian-artists-collective-category.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "威尼斯艺术家集合称谓"
NAME_EN = "Venetian artists (collective category)"
DATE = "2026-10-20"
PROCESS_ANCHOR = "s4-term-venetian-artists-collective-category-20261020"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
SOURCE_8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE_10 = "02-sources/02-Markdown/10_CHP-10_intro.md"
RELATION_IDS = {
    "st-chp10-p278-english-patrons-enable-venetian-artists",
    "st-chp10-p287-venetian-patronage",
    "st-chp10-p298-venetian-artists-drawn-to-foreign-cities",
    "st-chp8-p241-note5-gabburri-correspondence",
    "st-chp8-p241-venetian-and-neapolitan-contingents",
}
SOURCES = [
    (SOURCE_8, "第8章，印刷页241，来源转录 L365", "line 365; print p. 241",
     "Haskell 称威尼斯人的作品在1706年展览中占突出位置。",
     "Venetians made an impressive showing in the exhibition"),
    (SOURCE_8, "第8章，印刷页241脚注5，来源转录 L461", "line 461; print p. 241, note 5",
     "脚注称 Francesco Gabburri 通过书信与威尼斯艺术家保持联系。",
     "Francesco Gabburri, the connoisssur of drawings, also kept in touch with Venetian artists"),
    (SOURCE_10, "第10章，印刷页278，来源转录 L33", "line 33; print p. 278",
     "Haskell 称英国赞助使威尼斯艺术家离开故土成为值得考虑的选择。",
     "The English too made it worthwhile for Venetian artists to leave their native country"),
    (SOURCE_10, "第10章，印刷页287，来源转录 L210–211", "lines 210–211; print p. 287",
     "Haskell 称英国赞助者继续雇用威尼斯画家，但通常将工作限于风景、景观和肖像画。",
     "The English went on employing Venetian painters, but with rare exceptions they confined themselves to views, landscapes and portraits"),
    (SOURCE_10, "第10章，印刷页298，来源转录 L351–352", "lines 351–352; print p. 298",
     "Haskell 称威尼斯最优秀的一些艺术家及其作品被带往多个外国城市。",
     "many of the city’s best artists and their pictures were drawn to London"),
]


def make_card() -> str:
    source_rows = [{
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": span,
        },
    } for source_file, location, span, summary, quote in SOURCES]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p241 = f"[第8章 p.241](../../../{SOURCE_8}#L365)"
    n241 = f"[第8章 p.241脚注5](../../../{SOURCE_8}#L461)"
    p278 = f"[第10章 p.278](../../../{SOURCE_10}#L33)"
    p287 = f"[第10章 p.287](../../../{SOURCE_10}#L210)"
    p298 = f"[第10章 p.298](../../../{SOURCE_10}#L351)"
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Haskell 在第8、10章中使用的“威尼斯艺术家／威尼斯人”集合性类别。书中将该称谓用于展览参展者、与佛罗伦萨通信的艺术家、英国赞助语境中的威尼斯画家，以及被带往海外城市的艺术家。相关段落没有提供固定成员名单，也不证明这些语境所指为同一批个人。本术语不表示组织、固定团体或完整艺术史群体；这里不推定成员的国籍、居住地或确切范围。{p241}；{n241}；{p278}；{p287}；{p298}

**English:** This card records the collective category “Venetian artists” or “Venetians” as Haskell uses it in Chapters 8 and 10. The term appears for exhibition participants, artists in correspondence with a Florentine collector, Venetian painters in the context of English patronage, and artists whose works were taken to foreign cities. The passages provide no fixed membership list and do not establish that the same individuals are meant in each context. This term denotes neither an organization nor a stable or exhaustive art-historical group. No precise membership, nationality, or residence rule is inferred here. {p241}; {n241}; {p278}; {p287}; {p298}

### 书内用例

- 1706年展览：Haskell称“Venetians”在展览中表现突出；作品和参展者未在该句列全。{p241}
- 书信往来：脚注称 Gabburri 与威尼斯艺术家保持联系；未列出通信对象名单，也未独立查阅脚注所引书信集。{n241}
- 英国赞助：Haskell分别叙述英国赞助促使威尼斯艺术家离乡，以及英国赞助者通常委托威尼斯画家绘制风景、景观和肖像画。{p278}；{p287}
- 海外流动：Haskell称威尼斯一些最好的艺术家及其作品被带往伦敦、巴黎等城市，未指明具体个人、作品或路线。{p298}

上述均为 Haskell 的书内表述；本卡只界定集合称谓，不据其建立个体身份或正式关系。

## 关系与证据

### 关系记录

以下5条直接 S2 关系候选仍待 S6 逐条裁决；本卡不预判关系类型、方向或事实成立：{", ".join(f"`{item}`" for item in sorted(RELATION_IDS))}。
"""
    return f"---\n{fm}---\n\n{body}"


def preserve_bom_write_csv(path: Path, fieldnames, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fieldnames, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Venetian artists term in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert candidate_by_id[CANDIDATE].get("suggested_type") == "term"
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
    assert not any(row.get("type") == "term" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)

    source_files = {SOURCE_8, SOURCE_10}
    source_text = {source: " ".join((ROOT / source).read_text(encoding="utf-8-sig").split()) for source in source_files}
    for source_file, _, _, _, quote in SOURCES:
        assert " ".join(quote.split()) in source_text[source_file], quote

    statements = result_sync.load_statements()
    direct_statements = [row for row in statements if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE]
    direct_ids = {row["statement_id"] for row in direct_statements}
    relation_ids = {row["statement_id"] for row in direct_statements if row.get("qualifiers", {}).get("relation_candidate") is True}
    assert direct_ids == RELATION_IDS, (direct_ids - RELATION_IDS, RELATION_IDS - direct_ids)
    assert relation_ids == RELATION_IDS

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] = (planned_target.get("resolution_note", "")
        + f" S4 registration: mapped {GROUP} to {KU_ID}; term denotes Haskell's flexible collective category, with no fixed membership inferred.")
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID, "type": "term", "canonical_name": NAME_ZH, "name_en": NAME_EN,
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
        "\n\n### S4 term：威尼斯艺术家集合称谓（2026-10-20）\n\n"
        f"`{CANDIDATE}`沿用S3 `new`组 `{GROUP}`，登记至[威尼斯艺术家集合称谓卡](../units/terms/venetian-artists-collective-category.md)。"
        "该卡记录哈斯克尔在第8、10章中用于展览、书信、英国赞助与海外流动叙述的集合性称谓；不设固定成员名单，亦不把不同语境推为同一群体。"
        "5条直接 S2 关系候选留待 S6；未新增正式关系、外部身份或 S5 字段。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])}组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])}条映射；"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射。\n"
    )

    process_text = s4_helpers.refresh_knowledge_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    process_entry = (
        "\n\n<a id=\"" + PROCESS_ANCHOR + "\"></a>\n\n"
        "### S4 term：威尼斯艺术家集合称谓（2026-10-20）\n\n"
        f"`{CANDIDATE}`沿用S3 `new`术语组 `{GROUP}`，登记为[威尼斯艺术家集合称谓卡](../../../{CARD_REL})。"
        "第8章 p.241 及其脚注5、第10章 pp.278、287、298 均提供书内用例，覆盖展览参展者、Gabburri书信往来、英国赞助与艺术品/艺术家海外流动。"
        "各段没有固定成员名单；本卡不推定不同用例指同一批个人，不给成员范围添加国籍、居住地或完整性条件。"
        "5条直接S2关系候选仍待S6；本次不登记formal边或S5字段。"
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
        print(f"S4 term dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"source anchors=2 chapters/5 references; direct S2 relation candidates={len(relation_ids)}; no formal edge created")
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
