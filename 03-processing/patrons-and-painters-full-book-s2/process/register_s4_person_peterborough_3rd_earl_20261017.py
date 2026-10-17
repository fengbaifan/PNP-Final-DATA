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
CID = "cand-1891"
UNRESOLVED_ADMIRAL = "cand-7285"
GROUP = "new-person:3rd-of-peterborough-37b576d7e2"
KU_ID = "units/persons/3rd-earl-of-peterborough"
CARD_REL = f"04-knowledge/{KU_ID}.md"
NAME_ZH = "彼得伯勒第三代伯爵"
NAME_EN = "3rd Earl of Peterborough"
PROCESS_ANCHOR = "s4-peterborough-3rd-earl-20261017"
SOURCE = "02-sources/02-Markdown/07_CHP-7_sec_v.md"
INDEX_SOURCE = "02-sources/03-Index/03-2-Index-CSV/P.csv"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_IDS = (
    "st-chp7-p200-n1-peterborough-commissions-dal-sole",
    "st-chp7-p200-n1-peterborough-travel",
    "st-chp7-p200-n1-possible-peterborough",
    "st-chp7-p200-n1-peterborough-return-italy",
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
            "location": "第7章；印刷页200注1；Markdown L63；PDF物理页38。",
            "sentence_summary": (
                "注1以试探语气提出正文所称 Admiral ‘Pekemburgh’ 可能是第三代彼得伯勒伯爵，"
                "并在这一可能识别的语境中记录其意大利行程和向 dal Sole 委托画作；相关原始引文未独立查阅。"
            ),
            "original_quotes": [
                {"source_span": "line 63; print p. 200, note 1", "text": "This may possibly be tbe famous 3rd Earl ofPeterborough"},
                {"source_span": "line 63; print p. 200, note 1", "text": "who arrived in Italy from Spain for a few months in 1707"},
                {"source_span": "line 63; print p. 200, note 1", "text": "then returned for a much longer period in the next decade"},
                {"source_span": "line 63; print p. 200, note 1", "text": "when he certainly commissioned a number of pictures from dal Sole"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE,
                "source_span": "line 63; print p. 200, note 1; PDF physical p. 38",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "全书索引 P.csv#92。",
            "sentence_summary": "索引以 Peterborough, 3rd Earl of 为人物主项，并指向第200页注释。",
            "original_quotes": [
                {"source_span": "P.csv#92", "text": "Peterborough, 3rd Earl of"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_SOURCE,
                "source_span": "P.csv#92",
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
    ch7 = "[第7章 p.200 注1](../../../" + SOURCE + ")（L63；PDF物理页38）"
    index = "[全书索引 P.csv#92](../../../" + INDEX_SOURCE + ")"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记索引主项 “Peterborough, 3rd Earl of” 所指的书内人物。中文显示名按爵位翻译；书内材料没有给出其个人姓名，本卡不补写。第7章 p.200 注1称，正文里的 Admiral “Pekemburgh” 可能是第三代彼得伯勒伯爵，并在这一可能识别的语境中记录其1707年从西班牙抵达意大利、次十年再次长期停留，以及确曾向画家 Giovan Gioseffo dal Sole 委托若干画作。注释中的试探识别不视为已证实身份：正文人物候选 cand-7285 仍为 S3 undecided，本卡与之保持分开。OCR 转录中的 “tbe” 与 “ofPeterborough” 已按 S2 记录依据 PDF 物理页38校正为 “the” 与 “of Peterborough”；这是字面校勘，不构成人物身份依据。{ch7} {index}

**English:** This card records the in-book person listed in the index as “Peterborough, 3rd Earl of.” The Chinese display name translates the title; the book does not supply a personal name, which is not added here. Chapter 7, p. 200, note 1 says Admiral “Pekemburgh” in the text may possibly be the 3rd Earl of Peterborough, and in that tentative identification context reports his arrival in Italy from Spain in 1707, a longer return in the following decade, and commissions of pictures from Giovan Gioseffo dal Sole. The proposed identification is not treated as established: the body candidate cand-7285 remains S3 undecided and separate from this card. The OCR readings “tbe” and “ofPeterborough” are recorded in S2 as corrected to “the” and “of Peterborough” against PDF physical p. 38; this is textual correction, not identity evidence. {ch7} {index}

### 名称与身份范围

- **索引姓名形式：** Peterborough, 3rd Earl of；不据爵位自行扩写个人姓名。{index}
- **对应锚点：** 全书索引指向第200页注1；本卡只登记这个书内标题所指的人物。{index} {ch7}
- **待证边界：** Admiral “Pekemburgh” cand-7285 的身份仍为 undecided；脚注仅称“may possibly”，不据此与本卡合并。{ch7}

## 关系与证据

4条直接 S2 关系候选（{", ".join(RELATION_IDS)}）均留待 S6 核对。涉及画家与旅行地点的引述保留在原脚注的可能识别语境中；其中身份候选 {UNRESOLVED_ADMIRAL} 不因登记本卡而得到解决。本卡未新增正式关系。已登记端点：[Giovan Gioseffo dal Sole](giovan-gioseffo-dal-sole.md)、[Italy](../places/italy.md)。{ch7}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-local 3rd Earl of Peterborough person group in S4")
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
    unresolved = decision_by_id[UNRESOLVED_ADMIRAL]
    assert unresolved.get("decision") == "undecided" and not unresolved.get("ku_id")
    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted_lines
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and "peterborough" in " ".join(row.values()).casefold()
        for row in manifest
    ), "possible existing Peterborough person KU"
    assert f'<a id="{PROCESS_ANCHOR}"></a>' not in process_text
    assert "S4 person：Peterborough 3rd Earl 登记" not in result_text

    source_text = (ROOT / SOURCE).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_SOURCE).read_text(encoding="utf-8-sig")
    for quote in (
        "This may possibly be tbe famous 3rd Earl ofPeterborough",
        "who arrived in Italy from Spain for a few months in 1707",
        "then returned for a much longer period in the next decade",
        "when he certainly commissioned a number of pictures from dal Sole",
    ):
        assert normalized(quote) in normalized(source_text), f"source quote changed: {quote}"
    assert "Peterborough, 3rd Earl of" in index_text

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
    possible_identity = statement_by_id["st-chp7-p200-n1-possible-peterborough"]
    assert possible_identity.get("subject_candidate_id") == UNRESOLVED_ADMIRAL
    assert possible_identity.get("object_candidate_id") == CID
    assert "possibly" in possible_identity.get("original_quote", "").casefold()

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id[CID]["ku_id"] = KU_ID
    planned_by_id[CID]["resolution_note"] += (
        " S3 wording clarification 2026-10-17: the source identifies this source-local person by the title/ordinal "
        "3rd Earl of Peterborough, not by a full personal name; retain no inferred forename. "
        "Keep body candidate cand-7285 separate and undecided; footnote wording is tentative."
        f" S4 registration: mapped {GROUP} to {KU_ID}; 4 relation candidates remain pending S6."
    )
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
        "### S4 person：Peterborough 第三代伯爵登记（2026-10-17）\n\n"
        f"- cand-1891 保持 S3 new 组 {GROUP}，映射至 [{NAME_ZH}](../../../{CARD_REL})（{KU_ID}）。P.csv#92 列“Peterborough, 3rd Earl of”，第7章 p.200 注1也称第三代伯爵，故按书内标题登记人物；来源没有个人姓名，S3 旧说明中的“full personal name”措辞已在 alignment 附注中校正。\n"
        f"- 注1试探地提出正文 Admiral “Pekemburgh” cand-7285 可能是该伯爵；cand-7285 仍为 S3 undecided，不与本卡合并。OCR 的 tbe/ofPeterborough 校正依据记录在 S2（PDF物理页38），不影响身份裁决。4条直接关系候选留待 S6；原引述中的行程和委托均保留在可能识别语境中。\n"
        f"\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    next_result += (
        "\n\n### S4 person：Peterborough 第三代伯爵登记（2026-10-17）\n\n"
        f"cand-1891 映射至 [彼得伯勒第三代伯爵](../units/persons/3rd-earl-of-peterborough.md)。书内仅给爵位，不补个人姓名；Admiral “Pekemburgh” cand-7285 仍 undecided，未合并。4条直接关系候选保持待 S6。"
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
        print(f"S4 person dry-run passed: group={GROUP}; candidate={CID}; KU={KU_ID}")
        print(f"identity boundary preserved: {UNRESOLVED_ADMIRAL} remains undecided; 4 relation candidates remain pending S6")
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
