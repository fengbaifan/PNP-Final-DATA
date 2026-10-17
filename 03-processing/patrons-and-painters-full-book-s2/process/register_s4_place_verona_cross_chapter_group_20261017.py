from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_archive_memmo_query_sheet_20261017 as previous  # noqa: E402

sync = previous.sync
ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ENTITY_PATH = TABLES / "entity-candidates.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
MEMBERS = ("cand-7661", "cand-8681")
GROUP = "sg3-place-cand-8681"
KU_ID = "units/places/verona"
CARD_REL = f"04-knowledge/{KU_ID}.md"
NAME_ZH = "维罗纳"
NAME_EN = "Verona"
PROCESS_ANCHOR = "s4-place-verona-cross-chapter-20261017"
RELATION_IDS = (
    "st-chp8-p216-brusasorci-described-as-veronese",
    "st-chp10-p327-n03-pamphlets-published-verona",
    "st-chp14-p348-travel-verona",
)
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCES = (
    {
        "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章，印刷页216；Markdown L31。",
        "span": "line 31; print p. 216",
        "summary": "Haskell将 Brusasorci 称为 Veronese；S2把该词限定为地域形容词，并将地点锚定至 Verona，不推断出生或居住。",
        "quotes": (("line 31; print p. 216", "Veronese Brusasorci"),),
    },
    {
        "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "location": "第9章，印刷页268；Markdown L9。",
        "span": "line 9; print p. 268",
        "summary": "Haskell明确写 Cignaroli in Verona。",
        "quotes": (("line 9; print p. 268", "Of Cignaroli in Verona it was claimed"),),
    },
    {
        "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章，印刷页297；Markdown L340。",
        "span": "line 340; print p. 297",
        "summary": "Haskell称 Verona 是 Rotari 的 native Verona；按书内叙述记录，不作为外部核验。",
        "quotes": (
            ("line 340; print p. 297", "Pietro Rotari had gone to St Petersburg from his native Verona as early as 1756,"),
        ),
    },
    {
        "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章第II节，印刷页311、327；Markdown L12、237。",
        "span": "lines 12, 237; print pp. 311, 327",
        "summary": "Haskell提到 Schulenburg 在 Verona 度过生命晚年、于当地去世及1773年两种小册子在 Verona 出版；均按来源叙述记录，不作为外部核验。",
        "quotes": (
            ("line 12; print p. 311", "He divided the last years of his life between Venice and Verona,"),
            ("line 237; print p. 327, note 3", "were published in Verona in 1773."),
        ),
    },
    {
        "file": "02-sources/02-Markdown/14_CHP-14.md",
        "location": "第14章，印刷页348；Markdown L16。",
        "span": "line 16; print p. 348",
        "summary": "Haskell把 Verona 列入 Algarotti 行程所经城市之一；未给出各城市访问日期。",
        "quotes": (("line 16; print p. 348", "He travelled between Venice, Padua, Vicenza and Verona"),),
    },
)


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def card_text() -> str:
    sources = []
    for item in SOURCES:
        sources.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch8 = "[第8章 p.216](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L31）"
    ch9 = "[第9章 p.268](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L9）"
    ch10_intro = "[第10章 p.297](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L340）"
    ch10_section = "[第10章第II节 pp.311、327](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L12、237）"
    ch14 = "[第14章 p.348](../../../02-sources/02-Markdown/14_CHP-14.md)（L16）"
    rotari = "[Pietro Rotari](../persons/pietro-rotari.md)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记全书中以 Verona 指称的同一城市地点。第9章 p.268 明写 “Cignaroli in Verona”；第8章 p.216 的 “Veronese Brusasorci” 由 S2 限定为地域形容词并链接至 Verona，不据此推断 Brusasorci 的出生地或居住地。第10章使用 Verona 指称 {rotari} 的 native Verona、Schulenburg 去世所在地点及1773年出版小册子的地点；第14章还将 Verona 列在 Algarotti 的行程中。以上描述均保留为 Haskell 的书内陈述。本卡表示城市地点，不包含与之同名的政治实体、机构或其他对象。{ch8} {ch9} {ch10_intro} {ch10_section} {ch14}

**English:** This card records the single city-place referred to as Verona in the book. Chapter 9, p. 268, explicitly says “Cignaroli in Verona.” Chapter 8, p. 216, uses “Veronese Brusasorci”; S2 qualifies this as a regional adjective linked to Verona, without inferring Brusasorci’s birthplace or residence. Chapter 10 uses Verona for {rotari}’s native Verona, the place where Schulenburg died, and the publication place of pamphlets in 1773; Chapter 14 also includes Verona in Algarotti’s itinerary. These remain statements in Haskell’s book. The card represents the city-place, not a same-named political entity, institution, or other object. {ch8} {ch9} {ch10_intro} {ch10_section} {ch14}

### 地点身份与范围

- **地点名称：** Verona；中文标题“维罗纳”为项目工作译名。书内存在明确地名和 regional adjective 两类锚点。{ch8} {ch9}
- **跨章身份组：** cand-7661（p.216 “Veronese”）与 cand-8681（p.268 “Cignaroli in Verona”）同属 {GROUP}，并共同映射至本卡。p.297、311、327、348 的同地名用法补强该组的跨章依据。{ch8} {ch9} {ch10_intro} {ch10_section} {ch14}
- **范围限制：** 不据某人物被称为 Veronese 推断其出生或居住；不由书内提及补充现代行政资料。{ch8}

## 关系与证据

3条直接 S2 关系候选（{", ".join(RELATION_IDS)}）留待 S6 核对端点、类型、方向、语境与证据，本卡未新增正式关系。其中 p.216 的 regional adjective 仅记录来源用语，p.327 小册子出版地与 p.348 行程关系仍分别按 statement 核验。{ch8} {ch10_section} {ch14}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register one Verona place KU for the merged S3 identity group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert all(cid in candidate_by_id and cid in decision_by_id for cid in MEMBERS)
    assert all(candidate_by_id[cid].get("suggested_type") == "place" for cid in MEMBERS)
    group_members = {
        cid for cid, row in decision_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert decision_by_id[cid].get("decision") == "new" and not decision_by_id[cid].get("ku_id")
        assert f"group={GROUP}" in decision_by_id[cid].get("resolution_note", "")
    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted_lines
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "place"
        and any(row.get(key, "").strip().casefold() == NAME_EN.casefold() for key in ("canonical_name", "name_en"))
        for row in manifest
    ), "possible existing Verona place KU"
    assert f'<a id="{PROCESS_ANCHOR}"></a>' not in process_text
    assert "S4 place：Verona 跨章地点登记" not in result_text

    source_texts = {}
    for item in SOURCES:
        relative = item["file"]
        if relative not in source_texts:
            source_texts[relative] = (ROOT / relative).read_text(encoding="utf-8-sig")
        for _, quote in item["quotes"]:
            assert normalized(quote) in normalized(source_texts[relative]), f"source quote changed: {relative}"

    statements = [
        json.loads(line)
        for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statement_by_id = {row["statement_id"]: row for row in statements}
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relation_ids = {
        row["statement_id"] for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert relation_ids == set(RELATION_IDS), relation_ids
    assert statement_by_id["st-chp8-p216-brusasorci-described-as-veronese"].get("object_candidate_id") == "cand-7661"
    assert statement_by_id["st-chp10-p327-n03-pamphlets-published-verona"].get("object_candidate_id") == "cand-8681"
    assert statement_by_id["st-chp14-p348-travel-verona"].get("object_candidate_id") == "cand-7661"

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped merged place group {GROUP} to {KU_ID}; one KU for both cross-chapter candidates."
    planned_manifest = [dict(row) for row in manifest]
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "place",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated place card frontmatter is invalid"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = previous.refresh_process_type_table(process_text, stats)
    next_process += (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        "### S4 place：Verona 跨章地点登记（2026-10-17）\n\n"
        f"- cand-7661 与 cand-8681 属于同一 S3 new 身份组 {GROUP}，共同映射至 [{NAME_ZH}](../../../{CARD_REL})（{KU_ID}）；两条候选映射只对应一张 place KU。\n"
        "- 依据覆盖第8章 p.216 的 regional adjective、第9章 p.268 的明确地点名、第10章 pp.297、311、327 与第14章 p.348 的城市用法。第216页不据 regional adjective 推断出生/居住；其余仍为 Haskell 书内叙述。\n"
        "- 3条直接关系候选留待 S6；本卡没有新增正式关系或扩展到政治实体、机构及未识别作品。\n"
        f"\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    next_result += (
        "\n\n### S4 place：Verona 跨章地点登记（2026-10-17）\n\n"
        f"cand-7661 与 cand-8681 共同映射至 [维罗纳](../units/places/verona.md)。跨第8、9、10、14章的地名及地域用语支撑同一城市地点；"
        "3条直接关系候选留待 S6。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    next_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 place dry-run passed: group={GROUP}; candidates={len(MEMBERS)}; one KU={KU_ID}")
        print(f"cross-chapter evidence spans Ch8, Ch9, Ch10 and Ch14; {len(RELATION_IDS)} direct relation candidates pending S6")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(next_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: group={GROUP}; candidates={len(MEMBERS)} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
