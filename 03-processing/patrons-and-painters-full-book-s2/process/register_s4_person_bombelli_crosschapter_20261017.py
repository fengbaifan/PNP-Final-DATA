from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
MEMBERS = ["cand-0383", "cand-0384"]
GROUP = "new-person:bombelli-sebastiano-c6f300a2fb"
KU_ID = "units/persons/sebastiano-bombelli"
NAME_ZH = "塞巴斯蒂亚诺·邦贝利"
NAME_EN = "Sebastiano Bombelli"
CARD_REL = f"04-knowledge/{KU_ID}.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/B.csv"
RELATION_IDS = {"st-chp10-p278-hapsburgs-summon-bombelli"}
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-bombelli-crosschapter-20261017"
ANCHOR = "s4-person-bombelli-crosschapter-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."


def decode_index() -> str:
    raw = (ROOT / INDEX_FILE).read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第8章，印刷页227；OCR L200",
            "sentence_summary": "Haskell称 Bombelli 是城中主要肖像画家，并说 Stefano Conti 的妻子、儿子和本人肖像由其绘制。",
            "original_quotes": [{
                "source_span": "line 200; print p. 227",
                "text": "He had the portraits of his wife, his son and himself painted by Sebastiano Bombelli, the leading portraitist in the city",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "line 200; print p. 227",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页278；OCR L29–30",
            "sentence_summary": "Haskell称哈布斯堡方面召 Bombelli 前往 Vienna；来源只记录该项召请。",
            "original_quotes": [{
                "source_span": "lines 29–30; print p. 278",
                "text": "The Hapsburgs summoned Sebastiano Bombelli to Vienna",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "lines 29–30; print p. 278",
            },
        },
        {
            "citation": INDEX_CITATION,
            "location": "全书索引 B.csv#230 与 B.csv#231",
            "sentence_summary": "Bombelli 主项定位 p.227、278；肖像子项定位 p.227。",
            "original_quotes": [
                {"source_span": "B.csv#230", "text": "Bombelli Sebastiano — 227, 278"},
                {"source_span": "B.csv#231", "text": "portraits of Stefano Conti and his family — 227"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "B.csv#230–231",
            },
        },
    ]
    fm = yaml.safe_dump({
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000)
    rel_text = ", ".join(sorted(RELATION_IDS))
    ch8 = "[第8章 p.227](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)"
    ch10 = "[第10章 p.278](../../../02-sources/02-Markdown/10_CHP-10_intro.md)"
    index = f"[索引 B.csv#230–231](../../../{INDEX_FILE})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** Haskell 在第8章 p.227 称 Sebastiano Bombelli 为城中主要肖像画家，并记载 Stefano Conti 的妻子、儿子和本人肖像由他绘制；第10章 p.278 又称 Hapsburgs 召他前往 Vienna。书后索引主项覆盖 p.227、278，肖像子项单列 p.227，与第8章正文相合。本卡只记录书内的同一人物及两处语境，不补充外部生平，也不将“召往”扩写成任职或宫廷身份。〔{ch8}；{ch10}；{index}〕

**English:** In Chapter 8, p.227, Haskell calls Sebastiano Bombelli the leading portraitist in the city and says he painted portraits of Stefano Conti, his wife, and their son. Chapter 10, p.278, says the Hapsburgs summoned him to Vienna. The index main entry covers pp.227 and 278, and its portrait subentry points to p.227, matching the Chapter 8 passage. This card records the same person and these two contexts in the book; it adds no external biography and does not expand “summoned” into an appointment or court office. ({ch8}; {ch10}; {index})

### 身份与来源边界

- 第8、10章均使用全名 Sebastiano Bombelli；索引主项两页码与正文相合，肖像子项是人物主项下的工作定位，不另建人物或作品 KU。
- cand-0383（主项）与 cand-0384（肖像子项）同属一个 S3 new person 组；拼写和索引结构均未显示人物冲突。
- 本卡不推断 Hapsburgs 的机构范围，也不把召请表述为正式任职。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 关系候选（{rel_text}）留待 S6；KU 登记不代表关系裁决。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#s4-person-bombelli-crosschapter-20261017)。
"""


def insert_accepted(lines: list[str]) -> list[str]:
    entry = f"- {CARD_REL}"
    assert entry not in lines
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > CARD_REL),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Sebastiano Bombelli person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    for cid in MEMBERS:
        assert candidate_by_id[cid]["suggested_type"] == "person"
        assert candidate_by_id[cid]["canonical_name"] == "Bombelli Sebastiano"
    assert candidate_by_id[MEMBERS[0]]["index_entry_id"] == "B.csv#230"
    assert candidate_by_id[MEMBERS[1]]["index_entry_id"] == "B.csv#231"
    assert candidate_by_id[MEMBERS[1]]["sub_entry"] == "portraits of Stefano Conti and his family"

    group_members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert group_members == MEMBERS
    member_rows = [
        row for row in alignments
        if row.get("candidate_id") in MEMBERS and not row.get("external_source")
    ]
    assert len(member_rows) == 2 and all(not row.get("ku_id") for row in member_rows)
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)
    assert not (ROOT / CARD_REL).exists()
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert CARD_REL not in accepted_lines

    ch8 = (ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md").read_text(encoding="utf-8-sig")
    ch10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    index = decode_index()
    assert "portraits of his wife, his son and himself painted by Sebastiano Bombelli" in ch8
    assert "Sebastiano Bombelli, the leading portraitist in the city" in ch8
    assert "The Hapsburgs summoned\nSebastiano Bombelli to Vienna" in ch10
    assert 'Bombelli Sebastiano,,,,"227, 278"' in index
    assert "Bombelli Sebastiano,,portraits of Stefano Conti and his family,,227" in index

    statements = {
        row["statement_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    direct = {
        row["statement_id"] for row in statements.values()
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and MEMBERS[0] in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct == RELATION_IDS

    planned_alignments = [dict(row) for row in alignments]
    for row in planned_alignments:
        if row.get("candidate_id") in MEMBERS and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] += (
                f" S4登记（{DATE}）：{GROUP} 中的候选映射至 {KU_ID}；本组含两条候选映射、一个来源限定 person KU。"
                "直接 S2 关系候选仍待 S6。"
            )

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = insert_accepted(accepted_lines)
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4968
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 667
    assert totals["registered_members"] == 824
    assert totals["pending_groups"] == 4118
    assert totals["pending_members"] == 4144

    next_process = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in next_process
    next_process = next_process.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Sebastiano Bombelli 跨章身份组登记（{DATE}）\n\n"
        f"S3 身份组 {GROUP} 含 cand-0383（B.csv#230 主项，pp.227、278）与 cand-0384（B.csv#231 肖像子项，p.227），"
        f"共同映射至 [{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。第8章 p.227 与第10章 p.278 均用同一全名；"
        "卡片只记录书内两个锚点，不补外部传记或职位。\n"
        f"- 直接关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6；未新增 formal relations。\n"
        f"- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_result = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    next_result, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        next_result,
        count=1,
    )
    assert count == 1
    next_result += (
        f"\n\n### S4 person：Sebastiano Bombelli 跨章身份组登记（{DATE}）\n\n"
        f"cand-0383、cand-0384 → [{NAME_ZH}（{NAME_EN}）](../units/persons/sebastiano-bombelli.md)；"
        "第8章 p.227 正文对应索引肖像子目，第10章 p.278 主项提供跨章同名锚点。直接关系候选留待 S6。"
    )

    assert len(planned_manifest) == len(manifest) + 1
    if args.dry_run:
        print(
            f"dry-run passed: {GROUP}->{KU_ID}; members={len(MEMBERS)}; relation_candidates={len(direct)}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    (ROOT / CARD_REL).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP}->{KU_ID}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
