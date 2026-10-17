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
CANDIDATE = "cand-0372"
GROUP = "new-person:bianchi-isidoro-fb1a5df6ac"
KU_ID = "units/persons/isidoro-bianchi"
NAME_ZH = "伊西多罗·比安基"
NAME_EN = "Isidoro Bianchi"
CARD_REL = f"04-knowledge/{KU_ID}.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/B.csv"
BODY_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
RELATION_IDS = {
    "st-chp15-p371-note1-antiquarians-dedicated-books-to-querini",
    "st-chp15-p371-note1-bianchi-dedication",
}
ANCHOR = "s4-person-isidoro-bianchi-endpoint-20261017"
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
                "location": "第15章，印刷页371，注1；OCR L111",
                "sentence_summary": "Haskell 的注释称 Querini 与 Isidoro Bianchi、Francesco Milizia、Jacopo Morelli 等古物学家及新古典主义者保持联系，并说他们都曾向他题献书籍或专著。",
                "original_quotes": [{
                    "source_span": "line 111; print p. 371, note 1",
                    "text": "Querini was in touch with a number of antiquarians and neo-classicists such as Isidoro Bianchi, Francesco Milizia and Jacopo Morelli, all of whom dedicated books or monographs to him.",
                }],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": BODY_FILE,
                    "source_span": "line 111; print p. 371, note 1",
                },
            },
            {
                "citation": "Francis Haskell, *Patrons and Painters*, index.",
                "location": "全书索引 B.csv#219",
                "sentence_summary": "索引以 Bianchi, Isidoro 定位第15章 p.371 注。",
                "original_quotes": [{"source_span": "B.csv#219", "text": "Bianchi, Isidoro — 371n"}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": INDEX_FILE,
                    "source_span": "B.csv#219",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000)
    body_link = "[第15章 p.371 注1](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)"
    index_link = f"[索引 B.csv#219](../../../{INDEX_FILE})"
    relation_text = ", ".join(sorted(RELATION_IDS))
    return f"""---
{fm}---

## 内容

### 描述

**中文：** Haskell 第15章 p.371 注1列出 Isidoro Bianchi，称他与 Angelo Querini 保持交往，并与其他古物学家和新古典主义者一道向 Querini 题献书籍或专著。书后索引 B.csv#219 将同一姓名定位至该注释。本卡仅记录书内点名及来源语境，不补充外部生平或题献书目。〔{body_link}；{index_link}〕

**English:** Haskell’s Chapter 15, p.371 note 1 names Isidoro Bianchi among the antiquarians and neo-classicists in contact with Angelo Querini, and says that they dedicated books or monographs to Querini. The index entry B.csv#219 points to the same note. This card records the name and source context in the book; it adds no external biography or bibliography of the dedications. ({body_link}; {index_link})

### 身份与来源边界

- 候选 {CANDIDATE} 保持单成员 S3 new 组 {GROUP}；身份仅由 Haskell 正文注释中的全名及索引定位支持。
- 注释未给出 Bianchi 所题献书籍或专著的题名、日期；本卡不据此补建未具名出版物或个人履历。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 关系候选（{relation_text}）留待 S6；本卡不将“保持联系”或“题献”写成正式边。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Isidoro Bianchi as a source-backed S4 person relation endpoint.")
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
    assert candidate["canonical_name"] == "Bianchi, Isidoro"
    assert candidate["index_entry_id"] == "B.csv#219"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    group_members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert group_members == [CANDIDATE]
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)
    assert not (ROOT / CARD_REL).exists()
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert CARD_REL not in accepted_lines

    body = (ROOT / BODY_FILE).read_text(encoding="utf-8-sig")
    index = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "such as Isidoro Bianchi, Francesco Milizia and Jacopo Morelli" in body
    assert '"Bianchi, Isidoro",,,,371n' in index
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
        and CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct == RELATION_IDS

    planned_alignments = [dict(row) for row in alignments]
    changed = next(row for row in planned_alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    changed["ku_id"] = KU_ID
    changed["process_ref"] = PROCESS_REF
    changed["resolution_note"] += (
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU_ID}；创建双语、来源限定 person KU。"
        "两条直接 S2 关系候选留待 S6，未登记正式关系。"
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
    assert totals["registered_groups"] == 672
    assert totals["registered_members"] == 833
    assert totals["pending_groups"] == 4113
    assert totals["pending_members"] == 4135

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Isidoro Bianchi 直接关系端点登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持单成员 new 组 {GROUP}，登记为 [{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "第15章 p.371 注1与索引 B.csv#219 均给出同一全名和定位；卡片不补外部生平或未具名题献书目。\n"
        f"- 两条直接关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6；未新增 formal relations。\n"
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
        f"\n\n### S3/S4 person：Isidoro Bianchi 直接关系端点登记（{DATE}）\n\n"
        f"{CANDIDATE} → [{NAME_ZH}（{NAME_EN}）](../units/persons/isidoro-bianchi.md)；两条直接关系候选仍待 S6。"
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
