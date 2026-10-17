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
CID = "cand-2343"
GROUP = "sg3-place-cand-2343"
KU_ID = "units/places/st-petersburg"
CARD_REL = f"04-knowledge/{KU_ID}.md"
NAME_ZH = "圣彼得堡"
NAME_EN = "St Petersburg"
PROCESS_ANCHOR = "s4-place-st-petersburg-20261017"
CH10_SOURCE = "02-sources/02-Markdown/10_CHP-10_intro.md"
INDEX_SOURCE = "02-sources/03-Index/03-2-Index-CSV/S.csv"
QUOTE_P297 = "Pietro Rotari had gone to St Petersburg from his native Verona as early as 1756,"
QUOTE_P298_BELLOTTO = "Bernardo Bellotto was planning to go to S t Petersburg after the collapse of the Dresden court and the death of Augustus III."
QUOTE_P298_BANQUET = (
    "and its transference to\nSt Petersburg in the 1760s provides a striking reflection of the changing balance of power in Europe "
    "which had always played such an influential rôle in the diffusion of\nVenetian art."
)
INDEX_QUOTE = "St Petersburg, Venetian artists in"
RELATION_IDS = (
    "st-chp10-p297-rotari-st-petersburg",
    "st-chp10-p298-bellotto-planned-st-petersburg",
    "st-chp10-p298-banquet-transferred-and-power-balance",
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
            "location": "第10章，印刷页297；Markdown L340。",
            "sentence_summary": "Haskell称 Pietro Rotari 于1756年前往 St Petersburg，六年后在那里去世。",
            "original_quotes": [{"source_span": "line 340; print p. 297", "text": QUOTE_P297}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH10_SOURCE,
                "source_span": "line 340; print p. 297",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页298；Markdown L348。",
            "sentence_summary": "Haskell称 Bernardo Bellotto 曾计划前往 St Petersburg；这记录的是计划，不是已经完成的旅行。",
            "original_quotes": [{"source_span": "line 348; print p. 298", "text": QUOTE_P298_BELLOTTO}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH10_SOURCE,
                "source_span": "line 348; print p. 298",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页298；Markdown L350–351。",
            "sentence_summary": "Haskell称《克娄巴特拉宴会》在1760年代转移至 St Petersburg，并将此事解释为欧洲力量变化与威尼斯艺术传播的反映；该解释不自动构成具体转移原因。",
            "original_quotes": [{"source_span": "lines 350–351; print p. 298", "text": QUOTE_P298_BANQUET}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH10_SOURCE,
                "source_span": "lines 350–351; print p. 298",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "全书索引 S.csv#31。",
            "sentence_summary": "索引以“St Petersburg, Venetian artists in”设主项，并指向第297–298页。",
            "original_quotes": [{"source_span": "S.csv#31", "text": INDEX_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_SOURCE,
                "source_span": "S.csv#31",
            },
        },
    ]
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
    ch10 = f"[第10章 pp.297–298](../../../{CH10_SOURCE})（L340、348、350–351）"
    index = f"[全书索引 S.csv#31](../../../{INDEX_SOURCE})"
    rotari = "[Pietro Rotari](../persons/pietro-rotari.md)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “St Petersburg, Venetian artists in” 为主项，指向第297–298页。第10章 p.297 称 [Pietro Rotari]({rotari}) 于1756年前往 St Petersburg，并在六年后于当地去世。p.298 称 Bernardo Bellotto 曾计划前往该城；同页还称《克娄巴特拉宴会》于1760年代转移至 St Petersburg，并将其解释为欧洲力量变化与威尼斯艺术传播的反映。本卡登记的是书内所指的城市地点；没有把城市等同于俄罗斯政治实体或某一机构。书中对画作转移的解释按 Haskell 的归因保留，不据此推断该次转移的具体因果。{ch10} {index}

**English:** The index has the heading “St Petersburg, Venetian artists in,” with references to pp. 297–298. Chapter 10, p. 297, says [Pietro Rotari]({rotari}) went to St Petersburg by 1756 and died there six years later. On p. 298, Haskell reports that Bernardo Bellotto planned to go to the city; the same page says the *Banquet of Cleopatra* was transferred to St Petersburg in the 1760s and interprets this as a reflection of Europe’s changing balance of power and the diffusion of Venetian art. This card records the city as represented in the book; it does not identify the city with the Russian political entity or with an institution. The interpretation of the painting’s transfer is attributed to Haskell and is not treated as proof of its specific cause. {ch10} {index}

### 名称与地点范围

- **书内名称：** St Petersburg；中文标题“圣彼得堡”为项目工作译名。{index} {ch10}
- **类型边界：** 按来源的城市地点用法登记为 place，与俄罗斯政治实体和机构分别处理；本卡不添加现代地理行政信息。{index}
- **书内锚点：** 索引页码覆盖297、298页，正文分别提及 Rotari、Bellotto 的计划及《克娄巴特拉宴会》的转移。{index} {ch10}

## 关系与证据

3条直接 S2 关系候选（{", ".join(RELATION_IDS)}）留待 S6 核对端点、关系类型、方向、语境与证据；本卡未新增正式关系。Bellotto 前往该地仍是书中所述计划；Haskell 对画作转移与力量变化的解释不自动成为该转移的因果边。{ch10}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register St Petersburg as one source-backed place KU")
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
    assert candidate_by_id[CID].get("suggested_type") == "place"
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
        row.get("type") == "place"
        and any(row.get(key, "").strip().casefold() == NAME_EN.casefold() for key in ("canonical_name", "name_en"))
        for row in manifest
    ), "possible existing St Petersburg place KU"
    assert f'<a id="{PROCESS_ANCHOR}"></a>' not in process_text
    assert "S4 place：St Petersburg 登记" not in result_text

    ch10_text = (ROOT / CH10_SOURCE).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_SOURCE).read_text(encoding="utf-8-sig")
    for quote in (QUOTE_P297, QUOTE_P298_BELLOTTO, QUOTE_P298_BANQUET):
        assert normalized(quote) in normalized(ch10_text), f"source quote changed: {quote}"
    assert INDEX_QUOTE in index_text

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
    assert statement_by_id[RELATION_IDS[0]].get("subject_candidate_id") == "cand-2288"
    assert statement_by_id[RELATION_IDS[1]].get("subject_candidate_id") == "cand-0281"
    assert statement_by_id[RELATION_IDS[2]].get("subject_candidate_id") == "cand-9162"
    assert decision_by_id["cand-9152"].get("decision") == "undecided"

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
        "### S4 place：St Petersburg 城市地点登记（2026-10-17）\n\n"
        f"- cand-2343 保持 S3 new 组 {GROUP}，映射至 [{NAME_ZH}](../../../{CARD_REL})（{KU_ID}）。索引 S.csv#31 将“St Petersburg, Venetian artists in”指向第297–298页，正文提供 Rotari、Bellotto 计划及《克娄巴特拉宴会》转移的来源锚点。按城市地点登记，不与俄罗斯政治实体或机构合并。\n"
        "- Bellotto 前往该地仅为计划；Haskell 关于画作转移与欧洲力量变化的解释保持为作者解释。3条直接关系候选留待 S6，未添加正式关系。Rotari 人物 cand-2288 已登记；未识别绘画 cand-9152 仍 undecided。\n"
        f"\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    next_result += (
        "\n\n### S4 place：St Petersburg 城市地点登记（2026-10-17）\n\n"
        f"cand-2343 映射至 [圣彼得堡](../units/places/st-petersburg.md)。索引和第10章 pp.297–298提供多处书内锚点；"
        "Bellotto 的前往计划及 Haskell 对画作转移的解释均按来源限定保留，3条关系候选待 S6。"
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
        print(f"S4 place dry-run passed: group={GROUP}; candidates=1; KU={KU_ID}")
        print("3 direct relation candidates pending S6; city place remains separate from state or institution")
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
