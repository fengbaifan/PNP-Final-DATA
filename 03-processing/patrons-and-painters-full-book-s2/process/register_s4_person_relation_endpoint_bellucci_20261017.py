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
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-bellucci-direct-endpoint-20261017"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
CANDIDATE = "cand-0285"
GROUP = "new-person:battista-bellucci-giovanni-dbf80f5eed"
KU_ID = "units/persons/giovanni-battista-bellucci"
NAME_ZH = "乔万尼·巴蒂斯塔·贝卢奇"
NAME_EN = "Giovanni Battista Bellucci"
CARD_REL = f"04-knowledge/{KU_ID}.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/B.csv"
INDEX_ENTRY = "B.csv#132"
RELATION_IDS = {
    "st-chp8-p203-bellucci-crespi-pictures",
    "st-chp8-p203-bellucci-dal-sole-pictures",
}


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第8章，印刷页203；OCR L8",
                "sentence_summary": "Haskell将 Giovanni Battista Bellucci 称为另一位商人，并称其拥有 Crespi 与 dal Sole 的作品。",
                "original_quotes": [
                    {"source_span": "line 8", "text": "another businessman, Giovanni Battista Bellucci"},
                    {"source_span": "line 8", "text": "also owned works by Crespi"},
                    {"source_span": "line 8", "text": "and many more by dal Sole"},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                    "source_span": "line 8; print p. 203",
                },
            },
            {
                "citation": INDEX_CITATION,
                "location": f"全书索引 {INDEX_ENTRY}",
                "sentence_summary": "索引以 Bellucci, Giovanni Battista 列出人物主项。",
                "original_quotes": [{"source_span": INDEX_ENTRY, "text": "Bellucci, Giovanni Battista"}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": INDEX_FILE,
                    "source_span": INDEX_ENTRY,
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    chapter_link = "[第8章，印刷页203](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)"
    index_link = f"[索引 {INDEX_ENTRY}](../../../{INDEX_FILE})"
    relation_text = ", ".join(sorted(RELATION_IDS))
    return f"""---
{fm}---

## 内容

### 描述

**中文：** Haskell将Giovanni Battista Bellucci另列为一位博洛尼亚商人，称其拥有Crespi的作品及更多dal Sole的作品。同一段此前提到Giovanni Antonio Belloni；“another businessman”明确区分两人。本卡仅记录书内人物身份和收藏陈述，不补充外部生平。〔{chapter_link}；{index_link}〕

**English:** Haskell names Giovanni Battista Bellucci as another Bolognese merchant and says that he owned works by Crespi and many more by dal Sole. In the same paragraph, “another businessman” distinguishes him from Giovanni Antonio Belloni. This card records only the person and collection statements in the book and adds no external biography. ({chapter_link}; {index_link})

### 名称与身份

- 原书姓名与索引主项一致：Giovanni Battista Bellucci；中文名为本项目工作音译。
- 同段的 Giovanni Antonio Belloni 是不同人物，身份组保持分开。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。两条直接 S2 收藏关系候选（{relation_text}）留待 S6 审查；本卡登记不等于关系裁决。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#s4-person-bellucci-direct-endpoint-20261017)。
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
    parser = argparse.ArgumentParser(description="Register Giovanni Battista Bellucci as one S4 person endpoint.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    candidate, alignment = candidate_by_id[CANDIDATE], alignment_by_id[CANDIDATE]
    assert candidate["canonical_name"] == "Bellucci, Giovanni Battista"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    belloni = alignment_by_id["cand-0271"]
    assert belloni["ku_id"] == "units/persons/giovanni-antonio-belloni"
    assert sync.get_group(belloni.get("resolution_note", "")) != GROUP
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not (ROOT / CARD_REL).exists() and CARD_REL not in accepted_lines
    assert not any(
        row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    )
    chapter = (ROOT / "02-sources/02-Markdown/08_CHP-8_sec_i.md").read_text(encoding="utf-8-sig")
    assert "another businessman, Giovanni Battista Bellucci, also owned works by" in chapter
    assert "Crespi and many more by dal Sole" in chapter
    index_bytes = (ROOT / INDEX_FILE).read_bytes()
    try:
        index = index_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        index = index_bytes.decode("cp1252")
    assert "Bellucci, Giovanni Battista" in index
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
        "Two direct S2 collection relation candidates remain pending S6."
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
    planned_accepted = insert_accepted(list(accepted_lines))
    card = make_card()
    card_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert card_match and isinstance(yaml.safe_load(card_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    next_process = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    anchor = '<a id="s4-person-bellucci-direct-endpoint-20261017"></a>'
    assert anchor not in next_process
    next_process = next_process.rstrip() + (
        f"\n\n{anchor}\n\n### S4 person：Giovanni Battista Bellucci 直接端点登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持单成员 new 组 {GROUP}，登记为 [{NAME_ZH}（{NAME_EN}）]"
        f"(../../../{CARD_REL})（{KU_ID}）。第8章 p.203 与索引 B.csv#132 同指该人；同段将 Bellucci 明确称作"
        "另一位商人，与 Belloni 分开，故保留 cand-0285 与 cand-0271 两个独立人物组。\n"
        f"- 两条直接关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6；未写入 formal relations 或 enrichment。"
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
        f"\n\n### S4 person：Giovanni Battista Bellucci 直接端点登记（{DATE}）\n\n"
        f"{CANDIDATE} → [{NAME_ZH}（{NAME_EN}）](../units/persons/giovanni-battista-bellucci.md)；"
        "与 Belloni 分属不同人物组，两条收藏关系候选留待 S6。"
    )

    assert len(planned_manifest) == len(manifest) + 1
    assert totals["registered_groups"] == 663
    assert totals["registered_members"] == 819
    assert totals["pending_groups"] == 4123
    assert totals["pending_members"] == 4149
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
