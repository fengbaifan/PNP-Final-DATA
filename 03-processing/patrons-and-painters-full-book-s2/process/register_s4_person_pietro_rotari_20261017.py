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
CID = "cand-2288"
GROUP = "new-person:pietro-rotari-9ec7a16898"
KU_ID = "units/persons/pietro-rotari"
CARD_REL = f"04-knowledge/{KU_ID}.md"
NAME_ZH = "彼得罗·罗塔里"
NAME_EN = "Pietro Rotari"
PROCESS_ANCHOR = "s4-pietro-rotari-person-20261017"
CH10_SOURCE = "02-sources/02-Markdown/10_CHP-10_intro.md"
INDEX_SOURCE = "02-sources/03-Index/03-2-Index-CSV/Q-R.csv"
QUOTE_P295 = "Another Venetian artist working at Dresden who left at this time was Pietro Rotari from Verona, who had arrived in 1750."
QUOTE_P297 = (
    "Pietro Rotari had gone to St Petersburg from his native Verona as early as 1756, and until his death there six years later "
    "he painted several hundred pictures of all kinds ranging from portraits to mythologies."
)
RELATION_IDS = (
    "st-chp10-p295-note3-rotari-dresden-departure",
    "st-chp10-p297-rotari-pictures",
    "st-chp10-p297-rotari-st-petersburg",
)
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def card_text() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页295注3；Markdown L565。",
            "sentence_summary": (
                "注3称 Pietro Rotari 是在德累斯顿工作的威尼斯艺术家之一，称他‘at this time’离开，并说他1750年抵达。"
                "离开时间与后文时间线不在本卡擅自调和；其所引 Bellotto 图录未独立查阅。"
            ),
            "original_quotes": [
                {"source_span": "line 565; print p. 295, note 3", "text": QUOTE_P295},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH10_SOURCE,
                "source_span": "line 565; print p. 295, note 3",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页297；Markdown L340。",
            "sentence_summary": (
                "正文称 Pietro Rotari 出生于 Verona，1756年已前往 St Petersburg，六年后在那里去世，并画了数百幅肖像、神话等不同题材的画。"
                "该数量是来源中的概数，单幅作品未识别。"
            ),
            "original_quotes": [
                {"source_span": "line 340; print p. 297", "text": QUOTE_P297},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH10_SOURCE,
                "source_span": "line 340; print p. 297",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "全书索引 Q-R.csv#216。",
            "sentence_summary": "索引以 Rotari, Pietro 为人物主项，并指向第295页注释及第297页正文。",
            "original_quotes": [{"source_span": "Q-R.csv#216", "text": "Rotari, Pietro"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_SOURCE,
                "source_span": "Q-R.csv#216",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch10 = f"[第10章 pp.295、297](../../../{CH10_SOURCE})（L565、340）"
    index = f"[全书索引 Q-R.csv#216](../../../{INDEX_SOURCE})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “Rotari, Pietro” 列出人物，指向第295页注3和第297页。第295页注3称 Pietro Rotari 是在德累斯顿工作的威尼斯艺术家之一，1750年抵达，并称他 “at this time” 离开。第297页正文另称他来自 Verona，1756年已前往 St Petersburg，六年后在那里去世，并画了数百幅不同题材的作品。两处关于离开和迁居的时间表述保持原样，本卡不推算或调和其精确时间；注3所引 Bellotto 图录未独立查阅。中文名为项目工作音译。{ch10} {index}

**English:** The index lists “Rotari, Pietro” and points to note 3 on p. 295 and the text on p. 297. Note 3 calls Pietro Rotari a Venetian artist working at Dresden, says he arrived in 1750, and reports that he left “at this time.” The p. 297 text separately says that he went from his native Verona to St Petersburg by 1756, died there six years later, and painted several hundred pictures of different kinds. The departure and migration chronology is retained as stated, without calculating or reconciling exact dates; the Bellotto catalogue cited in note 3 was not independently consulted. The Chinese name is a project working transliteration. {ch10} {index}

### 名称与身份范围

- **索引姓名：** Rotari, Pietro；正文以 Pietro Rotari 指称。中文标题为项目工作音译。{index} {ch10}
- **身份依据：** 索引的页码指向注3与正文两处；本卡依据同一全名和索引定位登记书内人物，不添加外部身份标识或生平。{index}
- **作品范围：** “several hundred pictures”按来源概数保留；没有把未识别的数百幅作品合并成一个作品 KU。{ch10}
- **时间边界：** 注3的 “left at this time” 未给具体离开年份；后文所述1756年赴 St Petersburg 与六年后去世不据此反推离开德累斯顿的精确年份。{ch10}

## 关系与证据

3条直接 S2 关系候选（{", ".join(RELATION_IDS)}）留待 S6 核对端点、类型、方向、语境与证据，本卡未新增正式关系。德累斯顿端点已登记为[德累斯顿](../places/dresden.md)；St Petersburg 地点候选 cand-2343 仍待 S4；数百幅未识别绘画候选 cand-9152 仍为 S3 undecided，不因此建立作品关系。{ch10}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Pietro Rotari's person identity group in S4")
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
    assert CID in candidate_by_id and CID in decision_by_id
    assert candidate_by_id[CID].get("suggested_type") == "person"
    decision = decision_by_id[CID]
    assert decision.get("decision") == "new" and not decision.get("ku_id")
    assert group_of(decision.get("resolution_note", "")) == GROUP
    group_members = {
        cid for cid, row in decision_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == {CID}, group_members
    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted_lines
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and any(row.get(key, "").strip().casefold() == NAME_EN.casefold() for key in ("canonical_name", "name_en"))
        for row in manifest
    ), "possible existing Pietro Rotari person KU"
    assert f'<a id="{PROCESS_ANCHOR}"></a>' not in process_text
    assert "S4 person：Pietro Rotari 登记" not in result_text

    ch10_text = (ROOT / CH10_SOURCE).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_SOURCE).read_text(encoding="utf-8-sig")
    assert normalized(QUOTE_P295) in normalized(ch10_text)
    assert normalized(QUOTE_P297) in normalized(ch10_text)
    assert "Rotari, Pietro" in index_text

    statements = [
        json.loads(line)
        for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statement_by_id = {row["statement_id"]: row for row in statements}
    direct = [
        row for row in statements
        if CID in {row.get("subject_candidate_id"), row.get("object_candidate_id")}
    ]
    assert {row["statement_id"] for row in direct} == set(RELATION_IDS)
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is True for row in direct)
    assert statement_by_id[RELATION_IDS[0]].get("object_candidate_id") == "cand-0947"
    assert statement_by_id[RELATION_IDS[1]].get("object_candidate_id") == "cand-9152"
    assert statement_by_id[RELATION_IDS[2]].get("object_candidate_id") == "cand-2343"

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id[CID]["ku_id"] = KU_ID
    planned_by_id[CID]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; 3 direct relation candidates remain pending S6."
    planned_manifest = [dict(row) for row in manifest]
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated person card frontmatter is invalid"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = previous.refresh_process_type_table(process_text, stats)
    next_process += (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        "### S4 person：Pietro Rotari 登记（2026-10-17）\n\n"
        f"- cand-2288 保持 S3 new 组 {GROUP}，映射至 [{NAME_ZH}](../../../{CARD_REL})（{KU_ID}）。Q-R.csv#216 将 “Rotari, Pietro” 指向第295页注3及第297页正文；两处全名和索引页码相互吻合。\n"
        "- 第295页“left at this time”不折算为年份，也不与第297页1756年赴 St Petersburg 的叙述调和；注3所引 Bellotto 图录未独立查阅。未识别的数百幅画作 cand-9152 保持 undecided，St Petersburg cand-2343 保持 S3 new、待 S4。3条直接关系候选留待 S6。\n"
        f"\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    next_result += (
        "\n\n### S4 person：Pietro Rotari 登记（2026-10-17）\n\n"
        f"cand-2288 映射至 [彼得罗·罗塔里](../units/persons/pietro-rotari.md)。索引和第10章 pp.295、297提供同一书内身份锚点；"
        "时间表述保留原样，3条关系候选待 S6，未识别作品组不登记为 KU。"
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
        print(f"S4 person dry-run passed: group={GROUP}; candidates=1; KU={KU_ID}")
        print("timeline qualifier retained; 3 direct relation candidates pending S6; unnamed picture group remains undecided")
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
        f"applied: group={GROUP}; candidate={CID} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
