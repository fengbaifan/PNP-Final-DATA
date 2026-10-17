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
CID = "cand-0463"
GROUP = "new-person:andrea-brustolon-fc71fb65c2"
KU_ID = "units/persons/andrea-brustolon"
CARD_REL = f"04-knowledge/{KU_ID}.md"
NAME_ZH = "安德烈亚·布鲁斯托隆"
NAME_EN = "Andrea Brustolon"
PROCESS_ANCHOR = "s4-andrea-brustolon-person-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCES = (
    {
        "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章，印刷页337；Markdown L54、56。",
        "span": "lines 54, 56; print p. 337",
        "summary": "Haskell称 Brustolon 为《Dactylografa Smithiana》图版及其中一幅特定尾页图的雕刻者；该书未独立查阅。",
        "quotes": (
            ("line 54; print p. 337", "This contained 100 plates engraved by Brustolon,"),
            ("line 56; print p. 337", "an endplate of Perseus and the Head of Medusa, engraved by Brustolon from a drawing by Pietro Antonio Novelli"),
        ),
    },
    {
        "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章，印刷页340；Markdown L87。",
        "span": "line 87; print p. 340",
        "summary": "Haskell称 Canaletto 的杜卡尔仪式图稿原计划由 Brustolon 雕刻；文本记录计划，不证明最终完成。",
        "quotes": (("line 87; print p. 340", "to be engraved by Brustolon."),),
    },
    {
        "file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
        "location": "全书索引 B.csv#310。",
        "span": "B.csv#310",
        "summary": "索引以 Brustolon, Andrea 为主项，并指向第337与340页。",
        "quotes": (("B.csv#310", "Brustolon, Andrea"),),
    },
)
RELATION_IDS = (
    "st-chp13-p337-dactylografa-contained-100-brustolon-plates",
    "st-chp13-p337-dactylografa-medusa-endplate-engraved-after-novelli",
    "st-chp13-p340-canaletto-drawings-intended-for-engraving-by-brustolon",
)


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def card_text() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
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
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch13 = "[第13章 pp.337、340](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L54、56、87）"
    index = "[全书索引 B.csv#310](../../../02-sources/03-Index/03-2-Index-CSV/B.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “Brustolon, Andrea” 为人物主项，指向第337与340页；第13章正文两处以 Brustolon 指称同一雕刻者。哈斯克尔称《Dactylografa Smithiana》含有由 Brustolon 雕刻的100幅图版，并特别指出他依据 Pietro Antonio Novelli 的图稿刻制了一幅 Perseus 与 Medusa 题材尾页图。第340页则说 Canaletto 的杜卡尔仪式图稿“拟由” Brustolon 雕刻，故只记录计划。以上为书内叙述，未对外部生平或原书实物作核验。中文名为本项目工作音译。{ch13} {index}

**English:** The book’s index lists “Brustolon, Andrea” as a person entry and points to pp. 337 and 340; Chapter 13 refers to the same engraver by surname in both places. Haskell says the *Dactylografa Smithiana* contained 100 plates engraved by Brustolon and singles out an endplate of Perseus and the Head of Medusa, engraved after a drawing by Pietro Antonio Novelli. On p. 340, Haskell says Canaletto’s drawings of Ducal ceremonies were “to be engraved” by Brustolon, which records a plan rather than proof of completion. These are statements in the book; no external biography or copy of the illustrated book was consulted. The Chinese name is a project working transliteration. {ch13} {index}

### 名称与书内身份

- **索引姓名：** Brustolon, Andrea；正文 pp.337、340 以姓氏指称。中文标题为项目工作音译，不代表已核定的标准译名。{index} {ch13}
- **身份依据：** 索引将该姓名对应至两处正文页码；本卡限于此书内身份，不增加出生、死亡、地点或外部身份标识。{index}
- **表述边界：** 100幅版画和特定尾页图是 Haskell 对《Dactylografa Smithiana》的记述；Canaletto 图稿的雕刻关系仍是书中所述计划。{ch13}

## 关系与证据

涉及本人的3条直接 S2 关系候选（{", ".join(RELATION_IDS)}）留待 S6 核对端点、类型、方向、语境与证据，本卡未新增正式关系。相关候选端点包括已登记的 [《Dactylografa Smithiana》](../archives/dactylografa-smithiana.md)、[Pietro Antonio Novelli](pietro-antonio-novelli.md) 与 [Canaletto](canaletto.md)；关系尚未正式采纳。{ch13}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Andrea Brustolon as one S4 person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_lines = accepted.splitlines()
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
        and "brustolon" in " ".join(row.values()).casefold()
        for row in manifest
    ), "possible existing Andrea Brustolon person KU"
    assert f'<a id="{PROCESS_ANCHOR}"></a>' not in process_text
    assert "S4 person：Andrea Brustolon 登记" not in result_text

    for item in SOURCES:
        source_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
        for _, quote in item["quotes"]:
            assert normalized(quote) in normalized(source_text), f"source quote changed: {item['file']}"

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
    assert statement_by_id[RELATION_IDS[0]].get("object_candidate_id") == CID
    assert statement_by_id[RELATION_IDS[1]].get("subject_candidate_id") == CID
    assert statement_by_id[RELATION_IDS[2]].get("object_candidate_id") == CID

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id[CID]["ku_id"] = KU_ID
    planned_by_id[CID]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; S2 relation candidates remain pending S6."
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
        "### S4 person：Andrea Brustolon 登记（2026-10-17）\n\n"
        f"- cand-0463 保持 S3 new 组 {GROUP}，映射至 [{NAME_ZH}](../../../{CARD_REL})（{KU_ID}）。Haskell 索引以 Brustolon, Andrea 为主项并指向 p.337、p.340；两页正文均以 Brustolon 指称雕刻者。身份限于书内索引与正文锚点，不添加外部生平或标识。\n"
        "- 第13章称《Dactylografa Smithiana》有100幅由 Brustolon 雕刻的图版，并称特定 Perseus 与 Medusa 尾页图由他依据 Pietro Antonio Novelli 图稿雕刻；对 Canaletto 仪式图稿的雕刻仅记为计划。3条直接关系候选留待 S6，未添加正式关系。\n"
        f"\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    next_result += (
        "\n\n### S4 person：Andrea Brustolon 登记（2026-10-17）\n\n"
        f"cand-0463 映射至 [安德烈亚·布鲁斯托隆](../units/persons/andrea-brustolon.md)。索引与第13章 p.337、p.340 提供姓名及书内身份锚点；"
        "3条版画和雕刻计划关系候选仍待 S6，未登记为正式关系。"
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
        print(f"direct relation candidates={len(RELATION_IDS)}; all remain pending S6; no external identity claim")
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
