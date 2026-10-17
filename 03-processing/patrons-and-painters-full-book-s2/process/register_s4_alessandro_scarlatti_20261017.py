from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CANDIDATE = "cand-2393"
GROUP = "new-person:alessandro-scarlatti-e86fc84234"
KU = "units/persons/alessandro-scarlatti"
CARD = "04-knowledge/units/persons/alessandro-scarlatti.md"
ANCHOR = "s4-person-alessandro-scarlatti-20261017"
STATEMENTS = {"st-chp8-p230-scarlatti-music"}


def insert_accepted(lines: list[str], card_path: str) -> list[str]:
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    entry = f"- {card_path}"
    assert entry not in lines
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_path),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def make_card() -> str:
    metadata = {
        "title": "亚历山德罗·斯卡拉蒂（Alessandro Scarlatti）",
        "name_en": "Alessandro Scarlatti",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": "全书索引 S.csv#81；所列页码230、278",
                "sentence_summary": "Haskell索引将第8章与第10章的两处 Scarlatti 提及对应到 Alessandro Scarlatti 人物主项。",
                "original_quotes": [{"source_span": "S.csv#81", "text": "Scarlatti, Alessandro"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/03-Index/03-2-Index-CSV/S.csv", "source_span": "S.csv#81"},
            },
            {
                "citation": BOOK,
                "location": "第8章 p.230；S2 L227–236",
                "sentence_summary": "Haskell在音乐和歌剧语境中写出 Alessandro Scarlatti 全名。",
                "original_quotes": [{"source_span": "S2 line 229; print p.230", "text": "Alessandro Scarlatti"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "source_span": "line 229; print p.230"},
            },
            {
                "citation": BOOK,
                "location": "第10章 p.278；S2 L26–41",
                "sentence_summary": "Haskell在谈 Pellegrini 与 Marco Ricci 的伦敦绘画时提及 Scarlatti 的歌剧《Pyrrhus and Demetrius》。",
                "original_quotes": [{"source_span": "S2 line 41; print p.278", "text": "Scarlatti's opera of Pyrrhus and Demetrius"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "source_span": "line 41; print p.278"},
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** Haskell第8章 p.230 以全名 Alessandro Scarlatti 提及此人；第10章 p.278 再以 Scarlatti 指称一部歌剧的作者。书内索引将第230与278页列在 Scarlatti, Alessandro 主项下。中文名为本项目工作音译，身份依据限于本书。

**English:** Haskell names Alessandro Scarlatti in Chapter 8, p. 230, and refers to Scarlatti as the author of an opera in Chapter 10, p. 278. The book's index lists both pages under the entry “Scarlatti, Alessandro.” The Chinese name is a working transliteration, and the identification is limited to the book.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 原文全名 | Alessandro Scarlatti | S1（第8章 p.230；索引 S.csv#81） |

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 候选 {', '.join(sorted(STATEMENTS))} 留待 S6；第8章没有给出歌剧题名，本卡不补录单件歌剧或额外关系。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter S3 person group for Alessandro Scarlatti.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    matches = [row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(matches) == 1
    alignment = matches[0]
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert group_members == [CANDIDATE]
    assert not any(row.get("ku_id") == KU for row in manifest)
    assert not (ROOT / CARD).exists()
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
    assert direct == STATEMENTS

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert f"- {CARD}" not in accepted_lines
    planned_alignments = [dict(row) for row in alignments]
    planned_alignment = next(row for row in planned_alignments if row.get("alignment_id") == alignment["alignment_id"])
    planned_alignment["ku_id"] = KU
    planned_alignment["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    planned_alignment["resolution_note"] += (
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU}；S.csv#81 将第8章 p.230 全名与第10章 p.278 的姓氏提及归于同一人物主项。"
        "仅登记书内身份；直接关系候选留待 S6。"
    )
    planned_manifest = [*manifest, {
        "ku_id": KU,
        "type": "person",
        "canonical_name": "亚历山德罗·斯卡拉蒂",
        "name_en": "Alessandro Scarlatti",
        "source_task": TASK,
        "card_path": CARD,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = insert_accepted(accepted_lines, CARD)
    card = make_card()
    header = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert header and isinstance(yaml.safe_load(header.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 692
    assert totals["registered_members"] == 853
    assert totals["pending_groups"] == 4093
    assert totals["pending_members"] == 4115
    assert len(planned_manifest) == len(manifest) + 1

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Alessandro Scarlatti 跨章身份组登记（{DATE}）\n\n"
        f"cand-2393（S.csv#81，索引页码230、278）保持单成员 new 组 {GROUP}，登记为"
        f"[亚历山德罗·斯卡拉蒂（Alessandro Scarlatti）](../../../{CARD})（{KU}）。"
        "第8章 p.230 提供全名，第10章 p.278 的姓氏与歌剧语境由索引归入同一人物主项；本卡不创建具体歌剧对象。\n"
        f"- 直接 S2 关系候选 {', '.join(sorted(STATEMENTS))} 留待 S6；未新增 formal relations。\n"
        f"- S4 登记后：{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记，"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记。"
    )

    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, matches = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert matches == 1
    result_text += (
        f"\n\n### S3/S4 person：Alessandro Scarlatti 跨章身份组登记（{DATE}）\n\n"
        f"{CANDIDATE} → [亚历山德罗·斯卡拉蒂（Alessandro Scarlatti）](../units/persons/alessandro-scarlatti.md)；"
        "第8章全名与第10章索引对应的姓氏提及归于同组；关系候选留待 S6。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE}->{KU}; relation_candidates={len(direct)}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    (ROOT / CARD).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE}->{KU}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
