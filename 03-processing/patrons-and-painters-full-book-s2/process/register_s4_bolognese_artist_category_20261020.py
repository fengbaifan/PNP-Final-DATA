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

CANDIDATE = "cand-4229"
GROUP = "sg3-term-cand-4229"
KU_ID = "units/terms/bolognese-artists-collective-category"
CARD_REL = "04-knowledge/units/terms/bolognese-artists-collective-category.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "博洛尼亚画家集体称谓"
NAME_EN = "Bolognese artists as a collective category"
DATE = "2026-10-20"
PROCESS_ANCHOR = "s4-term-bolognese-artists-collective-category-20261020"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
SOURCES = (
    {
        "chapter": "2",
        "page": "28",
        "file": "02_CHP-2_sec_i.md",
        "lines": "82–93",
        "quote": (
            "Old masters, the Bolognese of every tendency, Caravaggio, Rubens, the elder generation "
            "of Mannerists—all were amply represented in his collections."
        ),
        "summary": "Haskell places artists described as Bolognese among the painters represented in Cardinal Borghese’s collection.",
        "summary_zh": "哈斯克尔将博洛尼亚画家列入博尔盖塞枢机收藏所代表的画家群体。",
    },
    {
        "chapter": "2",
        "page": "34",
        "file": "02_CHP-2_sec_ii.md",
        "lines": "30–40",
        "quote": (
            "‘As Urban VIII was a Florentine, the radiance of the Bolognese came to an end.’ "
            "Thus Passeri many years later."
        ),
        "summary": "Haskell quotes Passeri’s retrospective assessment about the Bolognese under Urban VIII.",
        "summary_zh": "哈斯克尔转引 Passeri 对 Urban VIII 统治时期博洛尼亚画家影响力的回顾性评价。",
    },
    {
        "chapter": "2",
        "page": "45",
        "file": "02_CHP-2_sec_iv.md",
        "lines": "19–29",
        "quote": (
            "The committee was especially keen to get paintings from the older generation of artists, "
            "notably the Bolognese, who had so distinguished themselves during the previous reigns."
        ),
        "summary": "Haskell identifies the Bolognese as a notable older generation of artists in the committee’s selection context.",
        "summary_zh": "哈斯克尔在委员会选画语境中，将博洛尼亚画家称为此前几朝表现突出的老一辈画家。",
    },
    {
        "chapter": "5",
        "page": "123",
        "file": "05_CHP-5_sec_i.md",
        "lines": "28–33",
        "quote": (
            "His special favourites were the Bolognese and Giovanni Lanfranco from his native Parma. "
            "He befriended and commissioned works from all of these and owned a notable collection."
        ),
        "summary": "Haskell names the Bolognese among Carlo’s special favourites and says Carlo befriended and commissioned works from those named.",
        "summary_zh": "哈斯克尔称博洛尼亚画家是 Carlo 特别偏爱者之一，并称 Carlo 与这些对象交游、委托作品。",
    },
)
RELATION_IDS = {
    "st-chp2-sec-ii-l30-40-passeri-bolognese-and-urban",
    "st-chp5-p123-carlo-befriended-bolognese",
    "st-chp5-p123-carlo-commissioned-bolognese",
    "st-chp5-p123-carlo-favorite-bolognese",
}


def make_card() -> str:
    sources = []
    for item in SOURCES:
        source_file = item["file"]
        source_span = f"lines {item['lines']}; print p. {item['page']}"
        sources.append({
            "citation": BOOK_CITATION,
            "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}",
            "sentence_summary": item["summary_zh"],
            "original_quotes": [{"source_span": source_span, "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{source_file}",
                "source_span": source_span,
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述与范围

**中文：** 本术语记录哈斯克尔书中对博洛尼亚画家的集体称谓。第2章将“the Bolognese”列入博尔盖塞枢机收藏所代表的画家，称 Domenichino 与 Guercino 为博洛尼亚同乡画家，并转引 Passeri 关于 Urban VIII 时期“the Bolognese”光辉告终的说法；第5章又称“the Bolognese”是 Carlo 特别偏爱的画家，并记其与这些对象交游、委托作品。各处称谓都处于地域与艺术史叙述语境，原书没有给出固定成员名录。本卡将其限定为书内使用的地域性画家类别，不视为正式组织，不自动涵盖每一位出生于博洛尼亚的人。以上均为哈斯克尔书内陈述，未在本卡独立核验。

**English:** This term records Haskell’s collective label for Bolognese painters. Chapter 2 places “the Bolognese” among the painters represented in Cardinal Borghese’s collection, calls Domenichino and Guercino Bolognese compatriots, and quotes Passeri on the “radiance of the Bolognese” ending under Urban VIII. Chapter 5 again names “the Bolognese” among Carlo’s special favourites and says he befriended and commissioned works from those named. The passages use a regional category in art-historical contexts but provide no fixed membership list. This card treats the label as Haskell’s collective category for painters, not as a formal organization or an automatic label for everyone born in Bologna. These statements remain Haskell’s account and have not been independently verified here.

### 书内用例

- 第2章 p.28：将不同倾向的博洛尼亚画家列入博尔盖塞枢机的收藏。
- 第2章 p.34：转引 Passeri 对 Urban VIII 时期博洛尼亚画家影响力的回顾性评价；这是被转引者的判断，不作为本卡独立事实结论。
- 第2章 p.45：在委员会选画语境中称此前几朝表现突出的老一辈画家包括博洛尼亚画家。
- 第5章 p.123：称博洛尼亚画家是 Carlo 特别偏爱的对象之一；同段还提到来自 Parma 的 Giovanni Lanfranco，因此“these”不被改写为只指博洛尼亚画家。

## 关系与证据

以下4条直接 S2 关系候选仍待 S6 逐条裁决；本卡不预判关系类型、方向或事实成立：{", ".join(sorted(RELATION_IDS))}。四条候选的另一端目前均有类型相符的 KU 映射；本次登记后端点齐备，但不因此自动成为正式关系。
"""


def preserve_bom_write_csv(path: Path, fieldnames, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fieldnames, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Bolognese artists collective category in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert CANDIDATE in candidate_by_id
    assert candidate_by_id[CANDIDATE].get("suggested_type") == "term"
    assert candidate_by_id[CANDIDATE].get("candidate_source_ref") == "chp-2:02_CHP-2_sec_ii:l30-40#L32"

    target_rows = [
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(target_rows) == 1
    target = target_rows[0]
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
    assert not any(
        row.get("type") == "term"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for row in manifest
    ), "same-title term already exists in the manifest"

    for item in SOURCES:
        source = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

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
    assert direct_ids == RELATION_IDS, (direct_ids - RELATION_IDS, RELATION_IDS - direct_ids)
    assert relation_ids == RELATION_IDS
    for statement in direct_statements:
        endpoints = {statement.get("subject_candidate_id"), statement.get("object_candidate_id")} - {None, ""}
        assert CANDIDATE in endpoints and len(endpoints) == 2
        for endpoint in endpoints - {CANDIDATE}:
            aligned = next(
                row for row in alignments
                if row.get("candidate_id") == endpoint and not row.get("external_source")
            )
            target_candidate = candidate_by_id[endpoint]
            target_manifest = next(row for row in manifest if row.get("ku_id") == aligned.get("ku_id"))
            assert aligned.get("decision") in {"same", "new"} and aligned.get("ku_id")
            assert target_manifest.get("type") == target_candidate.get("suggested_type")

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] = (
        (planned_target.get("resolution_note") or "")
        + f" S4 registration: mapped {GROUP} to {KU_ID}; regional collective category for painters in the cited Haskell passages, with no fixed membership asserted."
    )
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "term",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
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

    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_entry = (
        "\n\n### S4 term：博洛尼亚画家集体称谓（2026-10-20）\n\n"
        f"{CANDIDATE} 按既有 S3 new 组 {GROUP} 登记至[术语卡](../units/terms/bolognese-artists-collective-category.md)。"
        "第2章 p.28、p.34、p.45 与第5章 p.123 的多处书内用例支持将其登记为地域性画家集体称谓；不设固定名录或正式组织身份。"
        "4条直接 S2 关系候选在本次登记后均有双方 KU 映射，仍待 S6 逐条裁决；本批未新增 formal 关系、外部身份或 S5 字段。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])}组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])}条映射；"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射。"
    )
    result_text = result_text.rstrip() + result_entry + "\n"

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text = s4_helpers.refresh_knowledge_table(process_text, stats)
    process_entry = (
        "\n\n<a id=\"" + PROCESS_ANCHOR + "\"></a>\n\n"
        "### S3→S4 term：博洛尼亚画家集体称谓（2026-10-20）\n\n"
        f"{CANDIDATE} 沿用既有 S3 new 组 {GROUP}，登记为[博洛尼亚画家集体称谓卡](../../../{CARD_REL})。"
        "S3 的跨章组包含第2章中“the Bolognese of every tendency”、Domenichino 与 Guercino 的地域性称谓、Passeri 对“the Bolognese”的回顾性评价，"
        "以及第5章 Carlo 偏爱博洛尼亚画家的记述。核对第2章 p.28、p.34、p.45 与第5章 p.123 原文后，卡片将对象限定为书内地域性画家类别，不宣称固定成员或正式组织。"
        f"4条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）在本次登记后均有双方、类型相符的 KU 映射；仍待 S6 逐条裁决，不新增 formal 关系。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}组／{result_sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射；"
        f"直接端点队列由{before_queue['groups']}组／{before_queue['members']}成员降至{direct_queue['groups']}组／{direct_queue['members']}成员。"
        "该登记沿用 S3 决定，不替代第2章独立语义复核，也不把 S2 关系候选预判为成立。"
    )
    process_text = process_text.rstrip() + process_entry + "\n"
    enrichment = [
        json.loads(line)
        for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    agents_text = s4_helpers.refresh_agents(
        AGENTS_PATH.read_text(encoding="utf-8-sig"), totals, direct_queue,
        statements, result_sync.read_csv(TABLES / "relations.csv")[1], enrichment,
    )

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 term dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"source anchors=Chapter 2 pp.28, 34, 45; Chapter 5 p.123; direct S2 relation candidates={len(relation_ids)}")
        print(f"counterpart endpoint mappings are type-matched; no formal edge created")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(
            f"registered={totals['registered_groups']:,}/{totals['new_groups']:,} groups, "
            f"{totals['registered_members']:,}/{totals['new_candidates']:,} mappings; "
            f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}"
        )
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
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']:,}/{totals['registered_members']:,}; "
        f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}; "
        f"direct={before_queue['groups']:,}->{direct_queue['groups']:,} groups"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
