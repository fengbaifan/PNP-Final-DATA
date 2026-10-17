from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_archive_memmo_query_sheet_20261017 as archive_sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "sg3-event-cand-6051"
CANDIDATE = "cand-6051"
KU_ID = "units/events/s-salvatore-in-lauro-picture-exhibition-series"
CARD_REL = "04-knowledge/units/events/s-salvatore-in-lauro-picture-exhibition-series.md"
NAME_ZH = "圣萨尔瓦托雷因劳罗教堂常规画展"
NAME_EN = "Regular Picture Exhibition at S. Salvatore in Lauro, Rome"
ANCHOR = "s4-event-salvatore-exhibition-series-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_P5 = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
SOURCE_P8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"

RELATION_IDS = {
    "st-chp5-p128-ghezzi-appointment",
    "st-chp5-p128-salvatore-series-venue",
    "st-chp5-p128-salvatore-1675-instance-of-series",
    "st-chp5-p128-salvatore-1697-instance-of-series",
    "st-chp8-p222-n4-portrait-lent-to-salvatore-exhibition",
}
QUOTES = (
    (
        SOURCE_P5,
        "There was one more regular art exhibition which began much later in the century than those so far considered. "
        "This was held in the beautiful cloisters of S. Salvatore in\nLauro, a church that was bought for the Marchigian colony in Rome by Cardinal\n"
        "Azzolini in 1669. Soon afterwards the members of this group began to celebrate the anniversary of the arrival of the Holy House in Loreto on 10 December with elaborate celebrations which included concerts and a picture exhibition.",
    ),
    (
        SOURCE_P5,
        "As from 1682 the painter Giuseppe\nGhezzi, life secretary of the Accademia di S. Luca and himself from Ascoli Piceno, was in charge of the arrangements",
    ),
    (
        SOURCE_P8,
        "But the most remarkable of all Russo’s seventeenth-century pictures must have been Velasquez’s portrait of his servant Juan de Pareja, ‘cosa stupenda’, which in 1704 he sent to an exhibition in Rome (Plate 34).",
    ),
    (
        SOURCE_P8,
        "was among those lent to the exhibition in S. Salvatore in Lauro in 1704",
    ),
)


def source(citation: str, location: str, summary: str, quotes: list[tuple[str, str]], file: str) -> dict:
    return {
        "citation": citation,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote} for span, quote in quotes],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": file,
                         "source_span": "; ".join(span for span, _ in quotes)},
    }


def card_text() -> str:
    sources = [
        source(
            BOOK_CITATION,
            "第5章，印刷页128，正文行91–95；起始年份未据相对表述换算。",
            "Haskell称这是一项常规画展，在S. Salvatore in Lauro教堂回廊举行；Marchigian colony成员在12月10日庆祝Loreto圣屋到达周年，庆典包括音乐会和画展。画作在10、11日展出；1682年起由画家Giuseppe Ghezzi负责安排。",
            [("lines 91–93; print p.128", QUOTES[0][1]), ("lines 94–95; print p.128", QUOTES[1][1])],
            SOURCE_P5,
        ),
        source(
            BOOK_CITATION,
            "第8章，印刷页222注4，正文行136–137；仅用于记录同一地点的1704年展览提及。",
            "Haskell正文称一幅Juan de Pareja肖像于1704年送展；注4进一步说该画借展至S. Salvatore in Lauro的一场展览。该场与常规系列的正式归属关系仍待S6。",
            [("line 133; print p.222", QUOTES[2][1]), ("line 136; print p.222, note 4", QUOTES[3][1])],
            SOURCE_P8,
        ),
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "sub_type": "recurring picture-exhibition series",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p128 = "[第5章 p.128](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L91–95）"
    p222 = "[第8章 p.222 注4](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L136–137）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记哈斯克尔称为“一项常规艺术展览”的 S. Salvatore in Lauro 画展系列。第5章将其置于罗马的 Marchigian colony 语境：该群体在12月10日庆祝 Loreto 圣屋到达周年，庆典包括音乐会和画展；书中说画作在10日和11日展出，并记载自1682年起由画家 Giuseppe Ghezzi 负责安排。来源只说该系列“在本世纪晚些时候开始”，没有给出确切首年。展场称为教堂回廊；对应 place 候选 cand-6053 的身份与粒度仍待证，不据此添加正式地点边。第8章另报告一幅 Juan de Pareja 肖像于1704年借展至同一地点的一场展览；该场是否属于本常规系列仍留待 S6。{p128} {p222}

**English:** This unit records the S. Salvatore in Lauro picture-exhibition series that Haskell calls “one more regular art exhibition.” Chapter 5 places it in the Roman Marchigian-colony context: the group celebrated the arrival anniversary of the Holy House in Loreto on 10 December with festivities including concerts and a picture exhibition. Haskell says the paintings remained on view on the 10th and 11th, and that painter Giuseppe Ghezzi was in charge of arrangements from 1682. The source says the series began “much later in the century” but gives no exact first year. The venue is described as the church cloisters; place candidate cand-6053 remains unresolved in identity and granularity, so no formal place edge is added. Chapter 8 separately reports that a Juan de Pareja portrait was lent to an exhibition at the same venue in 1704; whether that occurrence belonged to this regular series remains for S6. {p128} {p222}

### 活动性质与时间

| 字段 | 值 | 证据 |
|---|---|---|
| 活动性质 | 常规画展系列；不指某一届展览 | S1（第5章 p.128） |
| 关联庆典 | Marchigian colony 在12月10日庆祝 Loreto 圣屋到达周年，庆典包括音乐会和画展 | S1（第5章 p.128） |
| 作品展出日期 | 12月10日、11日；这是书内所述展出日期，不外推为系列起讫年份 | S1（第5章 p.128） |
| 开始时间 | Haskell称其开始时间较本章先述展览晚得多；未给确切年份 | S1（第5章 p.128） |

### 举办地点与安排

| 字段 | 值 | 证据 |
|---|---|---|
| 场地称谓 | S. Salvatore in Lauro 教堂的 cloisters；place 候选 cand-6053 的身份与空间粒度仍待证 | S1（第5章 p.128） |
| 安排负责人 | [Giuseppe Ghezzi](../persons/giuseppe-ghezzi.md)；Haskell称自1682年起负责展览安排 | S1（第5章 p.128） |

### 跨章提及

第8章 p.222 注4报告一幅 Pareja 肖像于1704年借展至 S. Salvatore in Lauro 的一场展览。本卡不据同一场地将该场次与常规系列合并；S3将其保留为本系列的跨章身份线索，关系候选仍待S6核对。{p222}

## 关系与证据

当前没有登记在 `relations.csv` 中的正式关系。五条直接 S2 关系候选 `st-chp5-p128-ghezzi-appointment`、`st-chp5-p128-salvatore-series-venue`、`st-chp5-p128-salvatore-1675-instance-of-series`、`st-chp5-p128-salvatore-1697-instance-of-series`、`st-chp8-p222-n4-portrait-lent-to-salvatore-exhibition` 均留待 S6；1675、1697 是独立届次候选，1704场次的系列归属也不在本卡预先裁定。"""
    return f"---\n{fm}---\n\n{body}\n"


def insert_accepted(text: str, card_rel: str) -> str:
    lines = text.splitlines()
    if f"- {card_rel}" in lines:
        raise AssertionError(f"accepted.yml already includes {card_rel}")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S. Salvatore in Lauro recurring exhibition series in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_field_facts

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    alignment = next(row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert candidate["suggested_type"] == "event"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    assert not (ROOT / CARD_REL).exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "event" and (row.get("name_en") or "").casefold() == NAME_EN.casefold() for row in manifest)

    source_texts = {path: " ".join((ROOT / path).read_text(encoding="utf-8-sig").split()) for path in (SOURCE_P5, SOURCE_P8)}
    for path, quote in QUOTES:
        assert " ".join(quote.split()) in source_texts[path], f"source quote changed: {path}"

    statements = sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    relations = {
        row["statement_id"] for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert len(direct) == 12, len(direct)
    assert relations == RELATION_IDS, relations

    card = card_text()
    fm = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert fm and isinstance(yaml.safe_load(fm.group(1)), dict)
    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "event",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]

    with tempfile.TemporaryDirectory(prefix="pnp-s4-event-salvatore-preview-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_card = temp_root / CARD_REL
        temp_card.parent.mkdir(parents=True, exist_ok=True)
        temp_card.write_text(card, encoding="utf-8-sig", newline="\n")
        original_base = build_field_facts.BASE
        build_field_facts.BASE = temp_root
        try:
            facts, source_registry, warnings, cards_with_tables = build_field_facts.extract_records(planned_manifest[-1:])
        finally:
            build_field_facts.BASE = original_base
    assert not warnings, warnings
    assert cards_with_tables == 1 and facts
    assert all(row["evidence_status"] == "source_backed" and row["source_ids"] == ["haskell-1980-rev-ed"] for row in facts)
    assert set(source_registry) <= {"haskell-1980-rev-ed"}
    build_field_facts.assign_ids(facts, TABLES / "enrichment.jsonl")
    existing_facts = [
        json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    assert not any(row.get("ku_id") == KU_ID for row in existing_facts)
    planned_facts = existing_facts + facts
    assert len({row["enrichment_id"] for row in planned_facts}) == len(planned_facts)
    unverified = sum(row.get("evidence_status") == "unverified" for row in planned_facts)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, n = re.subn(
        r"^\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$",
        f"| [既有字段表](../tables/enrichment.jsonl) | {sync.fmt(len(planned_facts))}条，其中{sync.fmt(unverified)}条 unverified |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n == 1
    process_text = archive_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### S4 event：S. Salvatore in Lauro 常规画展系列登记（{DATE}）\n\n"
        f"cand-6051 保持 S3 独立 new 组 `{GROUP}`，登记为[圣萨尔瓦托雷因劳罗教堂常规画展](../../../{CARD_REL})（{KU_ID}）。第5章 p.128 支持常规系列、12月10日庆典与画展、10–11日展出及1682年起 Ghezzi 负责安排；未推算系列首年。第8章 p.222 注4仅作为跨章线索，1704届是否属于该系列不作关系裁决。\n"
        "- 保持边界：cand-11770（1675）与 cand-11771（1697）为独立届次 event 组；cand-11942（1701）不并入系列；cand-11783（1708）仍 undecided；place cand-6053（回廊）仍 undecided。另一个 S. Giovanni Decollato 系列及其1675年届次保持分立。\n"
        f"- 12条直接 S2 陈述中5条 relation_candidate（{', '.join(sorted(RELATION_IDS))}）均留待 S6；7条其余陈述维持各自属性/限定状态。本轮没有新增 formal relation 或外部身份行。\n"
        f"- S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条，KU 总数{sync.fmt(len(planned_manifest))}，结构化字段{sync.fmt(len(planned_facts))}条。"
    )
    planned_accepted = insert_accepted(accepted, CARD_REL)

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} -> {KU_ID}; direct_statements={len(direct)}; "
            f"relation_candidates_pending={len(relations)}; new_field_rows={len(facts)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; enrichment={len(existing_facts)}->{len(planned_facts)}"
        )
        for row in facts:
            print(f"  {row['field']} | {row['value']} | {row['evidence_status']} | {row['source_ref']}")
        return 0

    (ROOT / CARD_REL).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / CARD_REL).write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    build_field_facts.write_jsonl(TABLES / "enrichment.jsonl", planned_facts)
    ACCEPTED.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; relation_candidates_pending={len(relations)}; new_field_rows={len(facts)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"enrichment={len(existing_facts)}->{len(planned_facts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
