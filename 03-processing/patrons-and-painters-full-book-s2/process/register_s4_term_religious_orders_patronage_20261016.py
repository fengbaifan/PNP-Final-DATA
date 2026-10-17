from __future__ import annotations

import argparse
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

GROUP = "sg3-term-religiousorderspatronageby"
CANDIDATES = ("cand-2114", "cand-2115")
UNDECIDED_INDEX_ONLY = ("cand-2113", "cand-2116")
KU_ID = "units/terms/patronage-by-religious-orders"
CARD_REL = "04-knowledge/units/terms/patronage-by-religious-orders.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "宗教修会的艺术赞助"
NAME_EN = "Patronage by Religious Orders"
BOOK_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "location": "第3章第I节；印刷页63；OCR L12–14",
        "summary": "哈斯克尔指出，耶稣会及其他宗教修会的赞助，比表面看来更受一系列复杂事件限制。",
        "quotes": (
            (
                "line 12",
                "For in fact the patronage of the Jesuits and the other Orders was very much more circumscribed by a large number of complex events than is immediately apparent.",
            ),
        ),
        "span": "lines 12–14; print p. 63",
    },
    {
        "location": "第3章第I节；印刷页64；OCR L17–22",
        "summary": "哈斯克尔既记载宗教修会影响力扩大，也指出其长期财力短缺、教堂营建依赖罗马权势家族支持；他还称修会已深度融入社会。",
        "quotes": (
            (
                "line 17",
                "acquired increasing riches and influence.",
            ),
            (
                "line 20",
                "Thus it came about that the Jesuits (and the other religious Orders) were too closely integrated into the very fabric of society to impose any distinct accent of their own, even had that been their intention.",
            ),
            (
                "line 22",
                "For, curiously enough, their triumphant success in every field was for a long time accompanied by an extreme shortage of money which made their church building absolutely dependent on the support of the powerful families who ruled Rome.",
            ),
        ),
        "span": "lines 17–22; print p. 64",
    },
    {
        "location": "第3章第I节；印刷页65；OCR L27–33",
        "summary": "哈斯克尔将修会赞助置于贵族法律与财政力量、教宗及廷臣赞助渠道和世俗君主优先权的张力中，并指出各力量在17世纪不同时期的强弱不同。",
        "quotes": (
            (
                "line 27",
                "The patronage of the Orders was deeply affected by this tendency, and the building and decoration of their churches can best be studied as a reflection of the dialectic that ensued from it—the clash, sometimes hostile, sometimes so smooth as to be almost imperceptible, between two different types of patron, one with the spiritual authority that came from having a saint as founder, the other with the money.",
            ),
            (
                "line 28",
                "On the whole the patronage of the popes and their courtiers was mainly directed into far more personal channels than the uncomfortably autonomous churches of the religious Orders.",
            ),
            (
                "line 30",
                "And even then it was recognised by everyone concerned that the claims of secular princes came first:",
            ),
            (
                "lines 32–33",
                "Thus the decoration of the Gesù, S. Ignazio, S. Andrea della Valle, the Chiesa Nuova and other churches belonging to the principal religious Orders depended on a synthesis derived from conflicting forces which varied greatly in strength at different periods of the seventeenth century. This can best be understood if these churches are studied before, during and, above all, after the reign of Urban VIII.",
            ),
        ),
        "span": "lines 27–33; print p. 65",
    },
)


def make_card() -> str:
    sources = []
    for item in SOURCES:
        sources.append(
            {
                "citation": BOOK_CITATION,
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [
                    {"source_span": span, "text": quote}
                    for span, quote in item["quotes"]
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": "02-sources/02-Markdown/03_CHP-3_sec_i.md",
                    "source_span": item["span"],
                },
            }
        )

    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p63 = "[第3章 p.63](../../../02-sources/02-Markdown/03_CHP-3_sec_i.md)（L12–14）"
    p64 = "[第3章 p.64](../../../02-sources/02-Markdown/03_CHP-3_sec_i.md)（L17–22）"
    p65 = "[第3章 p.65](../../../02-sources/02-Markdown/03_CHP-3_sec_i.md)（L27–33）"
    body = f"""## 内容

### 描述

**中文：** 本术语记录哈斯克尔第3章对17世纪罗马宗教修会艺术赞助的讨论，涉及耶稣会、奥拉托利会、泰阿提纳会等。作者将修会教堂的营建与装饰置于复杂且随时期变化的赞助关系中：宗教组织获得影响力的同时，修会营建长期受财力短缺限制，并依赖罗马权势家族；贵族的法律与财政力量、教宗及廷臣的赞助渠道，以及世俗君主对艺术家的优先要求，也共同限定修会可获得的资源。这里记录的是本书组织的历史讨论主题，不把各修会视为具有统一制度或固定艺术风格。{p63} {p64} {p65}

**English:** This term records Haskell’s Chapter 3 discussion of artistic patronage by religious orders in seventeenth-century Rome, including the Jesuits, Oratorians and Theatines. He places the building and decoration of their churches within complex patronage relations that changed over time. While religious organizations gained influence, construction by the orders was for a long period constrained by financial shortages and dependence on powerful Roman families. Aristocratic legal and financial power, papal and court patronage, and secular princes’ prior claims also shaped the resources available to the orders. This is the topic as framed in the book; it does not imply a uniform system or fixed artistic style shared by all orders. {p63} {p64} {p65}

### 本章相关内容

- 哈斯克尔概述，17世纪多数时期教会内成立、旨在推动反宗教改革的宗教组织影响力上升；耶稣会、奥拉托利会和泰阿提纳会在教会等级体系中占据重要职位。该概述不表示每个修会的资源和赞助能力相同。
- 作者指出，耶稣会及其他修会的艺术赞助受复杂事件制约；修会成功并未消除长期财力短缺，教堂营建依赖统治罗马的权势家族。作者也把修会深度融入社会与其难以形成独立艺术特色联系起来，但保留“即使他们有此意图”的反事实限定。
- 第65页将修会赞助放入精神权威与经济力量之间的张力中，并指出教宗、廷臣和世俗君主竞争艺术家资源；其强弱在17世纪各时期变化。哈斯克尔建议将相关教堂置于 Urban VIII 任期前、中、后进行考察。以上均是作者的论述与解释，不扩写为对各宗教修会的普遍制度判断。

## 关系与证据

### 关系记录

当前没有已登记的正式关系。13条直接 S2 陈述中12条为关系候选，逐条保留在[原书陈述表](../../tables/book-statements.jsonl)，留待 S6 按端点、类型、方向、语境和证据审查。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register the source-backed term for patronage by religious orders in S4."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert all(cid in candidate_by_id for cid in CANDIDATES)
    assert all(candidate_by_id[cid].get("suggested_type") == "term" for cid in CANDIDATES)
    assert all(decisions[cid]["decision"] == "new" and not decisions[cid].get("ku_id") for cid in CANDIDATES)
    assert all(result_sync.get_group(decisions[cid].get("resolution_note", "")) == GROUP for cid in CANDIDATES)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)
    for cid in UNDECIDED_INDEX_ONLY:
        assert decisions[cid]["decision"] == "undecided" and not decisions[cid].get("ku_id")
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted
    assert not any(
        row.get("type") == "term"
        and "religious order" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".lower()
        and "patronage" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".lower()
        for row in manifest
    ), "a same-type religious-orders patronage term already exists in the manifest"

    for item in SOURCES:
        source_text = " ".join(
            (ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_i.md")
            .read_text(encoding="utf-8-sig").split()
        )
        for span, quote in item["quotes"]:
            assert " ".join(quote.split()) in source_text, (item["location"], span, quote)

    statements = result_sync.load_statements()
    candidate_set = set(CANDIDATES)
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in candidate_set
        or row.get("object_candidate_id") in candidate_set
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 13 and len(direct_relations) == 12
    assert {row.get("segment_id") for row in direct} == {
        "chp-3:03_CHP-3_sec_i:l3-14",
        "chp-3:03_CHP-3_sec_i:l16-24",
        "chp-3:03_CHP-3_sec_i:l26-33",
    }

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in candidate_set and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest)
    planned_manifest.append(
        {
            "ku_id": KU_ID,
            "type": "term",
            "canonical_name": NAME_ZH,
            "name_en": NAME_EN,
            "source_task": TASK,
            "card_path": CARD_REL,
        }
    )
    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S4 term：宗教修会的艺术赞助登记（2026-10-16）\n\n"
        f"`cand-2114` 与 `cand-2115`（`{GROUP}`）映射至[宗教修会的艺术赞助术语卡](../../../04-knowledge/units/terms/patronage-by-religious-orders.md)。"
        "身份依据为第3章印刷页63–65中直接讨论耶稣会及其他宗教修会赞助的三段原文；既有“艺术赞助”卡为一般上位术语，不是同一粒度的对象。"
        "索引项 `cand-2113`（Q-R.csv#40）及 `cand-2116`（Q-R.csv#43）仅有索引定位、缺正文身份锚点，继续保留 undecided，不随本次登记映射。"
        "13条直接 S2 陈述中12条关系候选仍待 S6；本次未生成正式关系或 S5 补足。"
        f"S4 累计登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    result_note = (
        "\n\n### term：宗教修会的艺术赞助 S4 登记（2026-10-16）\n\n"
        f"`cand-2114` 与 `cand-2115` 映射至[宗教修会的艺术赞助术语卡](../units/terms/patronage-by-religious-orders.md)。"
        "该术语按本书第3章语境限定为17世纪罗马宗教修会艺术赞助，记录影响其营建及装饰资源的复杂且随时期变化的力量，不概括为统一的修会制度。"
        "同组索引项 `cand-2113` 与 `cand-2116` 因没有正文锚点仍为 undecided；13条直接陈述中的12条关系候选留待 S6。"
        f"全书 S4 当前登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 term dry-run passed: {', '.join(CANDIDATES)} -> {KU_ID}")
        print(f"group members={len(group_rows)}; direct statements={len(direct)}; relation candidates={len(direct_relations)}")
        print("print pp.63–65 quotations checked; two index-only candidates remain undecided")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    result_sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    result_sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {', '.join(CANDIDATES)} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; "
        f"pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
