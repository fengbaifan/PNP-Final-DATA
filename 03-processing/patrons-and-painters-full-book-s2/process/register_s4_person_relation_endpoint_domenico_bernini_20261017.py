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
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
CANDIDATE = "cand-0294"
GROUP = "new-person:bernini-domenico-e245cae3bd"
KU_ID = "units/persons/domenico-bernini"
NAME_ZH = "多梅尼科·贝尔尼尼"
NAME_EN = "Domenico Bernini"
CARD_REL = f"04-knowledge/{KU_ID}.md"
INDEX_ENTRY = "B.csv#141"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/B.csv"
RELATION_IDS = {
    "st-chp2-seciv-l190-245-later-bernini-account",
    "st-chp7-p191-i07",
    "st-chp7-p191-i08",
}
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-domenico-bernini-20261017"


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
            "location": "第2章，印刷页58，注8；OCR L245",
            "sentence_summary": "Haskell称艺术家的儿子 Domenico 多年后写下同一场合的另一种叙述。",
            "original_quotes": [{
                "source_span": "line 245; print p. 58, note 8",
                "text": "Another account of the same occasion was written many years later by the artist’s son Domenico",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "source_span": "line 245; print p. 58, note 8",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章，印刷页191；OCR L271",
            "sentence_summary": "Haskell称 Del Carpio 从 Bernini 的儿子 Domenico 处购得一幅 Bernini 自画像素描。",
            "original_quotes": [{
                "source_span": "line 271; print p. 191",
                "text": "one of his self-portrait drawings from his son Domenico",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "source_span": "line 271; print p. 191",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章，印刷页191，注3；OCR L381",
            "sentence_summary": "同页注3将一项第28页引文著录为 Domenico Bernino。",
            "original_quotes": [{
                "source_span": "line 381; print p. 191, note 3",
                "text": "Domenico Bernino, p. 28.",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "source_span": "line 381; print p. 191, note 3",
            },
        },
    ]
    sources.append({
        "citation": INDEX_CITATION,
        "location": f"全书索引 {INDEX_ENTRY}",
        "sentence_summary": "索引以 Bernini, Domenico 列出人物主项，并定位至 p.58 注、p.85 与 p.191。",
        "original_quotes": [{"source_span": INDEX_ENTRY, "text": "Bernini, Domenico"}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": INDEX_FILE,
            "source_span": INDEX_ENTRY,
        },
    })
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
    relation_text = ", ".join(sorted(RELATION_IDS))
    ch2_link = "[第2章 p.58 注8](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)"
    ch7_link = "[第7章 p.191](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)"
    index_link = f"[索引 {INDEX_ENTRY}](../../../{INDEX_FILE})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 第2章注8提到“艺术家的儿子 Domenico”多年后写下同一场合的另一种叙述；第7章 p.191 明称 Domenico 为 Bernini 之子，并称 Del Carpio 从其子处购得一幅 Bernini 自画像素描。同页注3的引文形式为 “Domenico Bernino”，书后索引以 “Bernini, Domenico” 定位 p.58 注、p.85 与 p.191。本卡记录 Haskell 书内的姓名和角色，不补充外部生平或文献身份。〔{ch2_link}；{ch7_link}；{index_link}〕

**English:** Chapter 2, note 8, refers to “the artist’s son Domenico,” who wrote another account of the occasion many years later. Chapter 7, p.191, explicitly identifies Domenico as Bernini’s son and says Del Carpio acquired one of Bernini’s self-portrait drawings from him. The note on that page cites “Domenico Bernino,” while the index entry “Bernini, Domenico” points to p.58 n., p.85, and p.191. This card records the name and role in Haskell’s account and adds no external biography or bibliographic identity. ({ch2_link}; {ch7_link}; {index_link})

### 名称与身份

- 书后索引规范形式：Bernini, Domenico；正文注释形式：Domenico Bernino。
- 身份边界限于书内关于 Bernini 之子的记载；本轮未核验外部生平或 cited work 的书目身份。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。三条直接 S2 关系候选（{relation_text}）保留待 S6 审查；KU 登记不代表关系裁决。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#s4-person-domenico-bernini-20261017)。
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
    parser = argparse.ArgumentParser(description="Register Domenico Bernini as one S4 person relation endpoint.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    alignment = next(row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    assert candidate["canonical_name"] == "Bernini, Domenico" and candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert members == [CANDIDATE]
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(
        row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    )
    assert not (ROOT / CARD_REL).exists()
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert CARD_REL not in accepted_lines
    ch2 = (ROOT / "02-sources/02-Markdown/02_CHP-2_sec_iv.md").read_text(encoding="utf-8-sig")
    ch7 = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md").read_text(encoding="utf-8-sig")
    assert "Another account of the same occasion was written many years later by the artist’s son Domenico" in ch2
    assert "one of his self-portrait drawings from his son\nDomenico" in ch7
    assert "Domenico Bernino, p. 28." in ch7
    assert "Bernini, Domenico" in decode_index()
    statements = {
        row["statement_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    relation_rows = [statements[sid] for sid in RELATION_IDS if sid in statements]
    assert len(relation_rows) == len(RELATION_IDS)
    assert all(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        for row in relation_rows
    )

    planned_alignments = [dict(row) for row in alignments]
    planned_alignment = next(row for row in planned_alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    planned_alignment["ku_id"] = KU_ID
    planned_alignment["process_ref"] = PROCESS_REF
    planned_alignment["resolution_note"] += (
        f" S4 registration ({DATE}): mapped {GROUP} to {KU_ID}; bilingual source-backed person card created. "
        "Three direct S2 relation candidates remain pending S6."
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
    next_process = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    anchor = '<a id="s4-person-domenico-bernini-20261017"></a>'
    assert anchor not in next_process
    next_process = next_process.rstrip() + (
        f"\n\n{anchor}\n\n### S4 person：Domenico Bernini 直接关系端点登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持单成员 new 组 {GROUP}，登记为 [{NAME_ZH}（{NAME_EN}）]"
        f"(../../../{CARD_REL})（{KU_ID}）。第2章 p.58 注8称艺术家的儿子 Domenico 多年后写下另一种叙述；第7章 p.191"
        "正文明确将 Domenico 称为 Bernini 之子，注3列出 Domenico Bernino；书后索引 B.csv#141 将 p.58 注、p.85 与"
        "p.191 汇于同一人物主项。该组身份仅限书内证据。\n"
        f"- 三条直接关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6；未新增 formal relations。"
        f"\n- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
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
        f"\n\n### S4 person：Domenico Bernini 直接关系端点登记（{DATE}）\n\n"
        f"{CANDIDATE} → [{NAME_ZH}（{NAME_EN}）](../units/persons/domenico-bernini.md)；"
        "书内姓名与索引跨页定位相符，三条直接关系候选留待 S6。"
    )

    assert len(planned_manifest) == len(manifest) + 1
    assert totals["registered_groups"] == 666
    assert totals["registered_members"] == 822
    assert totals["pending_groups"] == 4120
    assert totals["pending_members"] == 4146
    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} {GROUP}->{KU_ID}; relation_candidates={len(relation_rows)}; "
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
        f"applied: {CANDIDATE}->{KU_ID}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
