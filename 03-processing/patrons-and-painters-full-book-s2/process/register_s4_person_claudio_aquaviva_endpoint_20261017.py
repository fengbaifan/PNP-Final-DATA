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
CANDIDATE = "cand-0113"
GROUP = "new-person:aquaviva-claudio-aquaviva-claudio-general-fbc1409a12"
KU_ID = "units/persons/claudio-aquaviva"
NAME_ZH = "克劳迪奥·阿夸维瓦"
NAME_EN = "Claudio Aquaviva"
CARD_REL = f"04-knowledge/{KU_ID}.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/A.csv"
BODY_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
RELATION_IDS = {
    "st-chp3-secii-l19-31-aquaviva-controlled-and-shaped-scheme",
    "st-chp3-secii-l19-31-aquaviva-correspondence-raising-funds",
    "st-chp3-secii-l19-31-richeome-dedicated-book-to-aquaviva",
}
ANCHOR = "s4-person-claudio-aquaviva-endpoint-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


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


def make_card() -> str:
    fm = yaml.safe_dump({
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第3章，印刷页67–68；正文 OCR L19–31（相关句分布于该段）",
                "sentence_summary": "Haskell 以全名 Claudio Aquaviva 称一位 General，记其对 S. Vitale 装饰方案的个人关注及建议；同段另述 General Aquaviva 的筹资通信，并称 Louis Richeôme 于1611年将一本书献给 Aquaviva。三项关系候选留待 S6。",
                "original_quotes": [
                    {
                        "source_span": "line 25–26; print p.67",
                        "text": "Fiammeri under the immediate control of the General, Claudio Aquaviva, who took a strong personal interest in the scheme and made suggestions of his own.",
                    },
                    {
                        "source_span": "lines 29–30; print p.67",
                        "text": "the correspondence of General Aquaviva is often concerned with the problem of how to raise more money—jewels to be sold, gifts to be solicited and so on.",
                    },
                    {
                        "source_span": "line 31; print pp.67–68",
                        "text": "In 1611 a French Jesuit Louis Richeôme wrote a book, which he dedicated to Aquaviva",
                    },
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": BODY_FILE,
                    "source_span": "lines 25–31; print pp.67–68",
                },
            },
            {
                "citation": "Francis Haskell, *Patrons and Painters*, index.",
                "location": "全书索引 A.csv#114",
                "sentence_summary": "索引主项 Aquaviva, Claudio 定位至 p.67。",
                "original_quotes": [{"source_span": "A.csv#114", "text": "Aquaviva, Claudio — 67"}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": INDEX_FILE,
                    "source_span": "A.csv#114",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000)
    body_link = "[第3章 pp.67–68](../../../02-sources/02-Markdown/03_CHP-3_sec_ii.md)"
    index_link = f"[索引 A.csv#114](../../../{INDEX_FILE})"
    relation_text = ", ".join(sorted(RELATION_IDS))
    return f"""---
{fm}---

## 内容

### 描述

**中文：** Haskell 第3章 p.67 以全名“Claudio Aquaviva”称一位 General，并记其对 S. Vitale 装饰方案的个人关注及建议；同段称其通信常涉及筹资，并记载 Louis Richeôme 于1611年将一本书献给 Aquaviva。索引 A.csv#114 以 Aquaviva, Claudio 定位至 p.67。本卡限于这些书内身份锚点和叙述，不把三项关系候选提前确认为正式关系；中文名为工作音译，不补充书外生平。〔{body_link}；{index_link}〕

**English:** Chapter 3, p.67, gives the full name “Claudio Aquaviva” for a General and records his personal interest and suggestions concerning the decoration scheme at S. Vitale. The same passage says his correspondence often concerned fundraising and that Louis Richeôme dedicated a book to Aquaviva in 1611. Index entry A.csv#114 locates “Aquaviva, Claudio” on p.67. This card is limited to these book-based identity anchors and statements; the three relation candidates are not treated as formal relations. The Chinese display name is a working transliteration; no external biography is added. ({body_link}; {index_link})

### 身份与来源边界

- 候选 {CANDIDATE} 保持单成员 S3 new 组 {GROUP}；正文全名、后文简称与索引主项相合。
- “General”仅按原书称谓记录；不据本卡补入任职时间或外部规范身份。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。三条直接 S2 关系候选（{relation_text}）留待 S6；逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Claudio Aquaviva as a source-backed S4 person endpoint.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    decision = next(row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    assert candidate["suggested_type"] == "person"
    assert candidate["canonical_name"] == "Aquaviva, Claudio"
    assert candidate["index_entry_id"] == "A.csv#114"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert members == [CANDIDATE]
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)
    assert not (ROOT / CARD_REL).exists()
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert CARD_REL not in accepted_lines

    body = (ROOT / BODY_FILE).read_text(encoding="utf-8-sig")
    # A.csv is GBK encoded; decode it without changing the source asset.
    index = (ROOT / INDEX_FILE).read_text(encoding="gbk")
    assert "the General, Claudio Aquaviva" in body
    assert "the correspondence of General" in body and "dedicated to Aquaviva" in body
    assert '"Aquaviva, Claudio",,,,67' in index
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct == RELATION_IDS

    planned_alignments = [dict(row) for row in alignments]
    changed = next(row for row in planned_alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    changed["ku_id"] = KU_ID
    changed["process_ref"] = PROCESS_REF
    changed["resolution_note"] += (
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU_ID}；创建书内来源限定 person KU。"
        "第3章全名与索引主项一致；三条直接 S2 关系候选仍待 S6，不登记正式关系。"
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
    fm_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert fm_match and isinstance(yaml.safe_load(fm_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4968
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 678
    assert totals["registered_members"] == 839
    assert totals["pending_groups"] == 4107
    assert totals["pending_members"] == 4129

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Claudio Aquaviva 直接关系端点登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持单成员 new 组 {GROUP}，登记为 [{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "第3章 p.67 以全名称其为 General，并记其对 S. Vitale 装饰方案的个人关注和建议；同段另述其筹资通信及 Richeôme 的献书。\n"
        f"- 直接 S2 关系候选 {', '.join(sorted(RELATION_IDS))} 留待 S6；未新增 formal relations。\n"
        f"- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert count == 1
    result_text += (
        f"\n\n### S3/S4 person：Claudio Aquaviva 直接关系端点登记（{DATE}）\n\n"
        f"{CANDIDATE} → [{NAME_ZH}（{NAME_EN}）](../units/persons/claudio-aquaviva.md)；"
        "称谓与关系范围按原文保留，三项关系候选仍待 S6。"
    )

    assert len(planned_manifest) == len(manifest) + 1
    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} {GROUP}->{KU_ID}; relation_candidates={len(direct)}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    (ROOT / CARD_REL).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE}->{KU_ID}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
