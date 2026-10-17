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
CANDIDATE = "cand-0392"
GROUP = "new-person:bordoni-francesco-67f728663d"
KU_ID = "units/persons/francesco-bordoni"
NAME_ZH = "弗朗切斯科·博尔多尼"
NAME_EN = "Francesco Bordoni"
CARD_REL = f"04-knowledge/{KU_ID}.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/B.csv"
BODY_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
RELATION_IDS = {"st-chp7-p174-i10"}
ANCHOR = "s4-person-francesco-bordoni-endpoint-20261017"
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
                "location": "第7章，印刷页174；正文 OCR L49–50",
                "sentence_summary": "Haskell 记载 Pietro Francavilla 赴巴黎时与助手、未来女婿 Francesco Bordoni 同行。该关系描述保留为作者叙述，具体关系裁决留待 S6。",
                "original_quotes": [
                    {
                        "source_span": "line 49–50; print p.174",
                        "text": "he soon arrived with his assistant and future son-in-law Francesco Bordoni.",
                    },
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": BODY_FILE,
                    "source_span": "lines 49–50; print p.174",
                },
            },
            {
                "citation": "Francis Haskell, *Patrons and Painters*, index.",
                "location": "全书索引 B.csv#239",
                "sentence_summary": "索引主项 Bordoni, Francesco 定位至 p.174。",
                "original_quotes": [{"source_span": "B.csv#239", "text": "Bordoni, Francesco — 174"}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": INDEX_FILE,
                    "source_span": "B.csv#239",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000)
    body_link = "[第7章 p.174](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)"
    index_link = f"[索引 B.csv#239](../../../{INDEX_FILE})"
    relation_text = ", ".join(sorted(RELATION_IDS))
    return f"""---
{fm}---

## 内容

### 描述

**中文：** Haskell 第7章 p.174 称 Francesco Bordoni 随 Pietro Francavilla 到达巴黎，并将 Bordoni 描述为 Francavilla 的助手和未来女婿。索引 B.csv#239 以全名定位至同页。本卡只登记这位书内具名人物；“助手”和“未来女婿”是原书关系候选的表述，尚未作为正式关系裁决。中文名为项目工作音译，不据此补充书外身份或生平。〔{body_link}；{index_link}〕

**English:** Chapter 7, p.174, says Francesco Bordoni arrived in Paris with Pietro Francavilla and describes Bordoni as Francavilla’s assistant and future son-in-law. Index entry B.csv#239 locates the full name on the same page. This card registers the named person in the book; “assistant” and “future son-in-law” remain source-reported relationship candidates and have not been adjudicated as formal relations. The Chinese display name is a working transliteration; no external identity or biography is added. ({body_link}; {index_link})

### 身份与来源边界

- 候选 {CANDIDATE} 保持单成员 S3 new 组 {GROUP}；正文全名与索引主项一致。
- 第7章 p.174 对其与 Francavilla 的关系描述仍待 S6 逐项裁决；不在本次登记中新增正式关系。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 关系候选（{relation_text}）留待 S6；逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Francesco Bordoni as a source-backed S4 person endpoint.")
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
    assert candidate["canonical_name"] == "Bordoni, Francesco"
    assert candidate["index_entry_id"] == "B.csv#239"
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
    index = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "he soon arrived with his assistant and future son-in-law Francesco" in body
    assert "Bordoni." in body
    assert '"Bordoni, Francesco",,,,174' in index
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
        "第7章全名与索引主项一致；一条直接 S2 关系候选仍待 S6，不登记正式关系。"
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
    assert totals["registered_groups"] == 676
    assert totals["registered_members"] == 837
    assert totals["pending_groups"] == 4109
    assert totals["pending_members"] == 4131

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Francesco Bordoni 直接关系端点登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持单成员 new 组 {GROUP}，登记为 [{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "第7章 p.174 以全名记载其随 Pietro Francavilla 到达巴黎，并称其为助手和未来女婿；索引 B.csv#239 定位至同页。\n"
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
        f"\n\n### S3/S4 person：Francesco Bordoni 直接关系端点登记（{DATE}）\n\n"
        f"{CANDIDATE} → [{NAME_ZH}（{NAME_EN}）](../units/persons/francesco-bordoni.md)；"
        "中文名为工作音译，关系陈述仍待 S6。"
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
