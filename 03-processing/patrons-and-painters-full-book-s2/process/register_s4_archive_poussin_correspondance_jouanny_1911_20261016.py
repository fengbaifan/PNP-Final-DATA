from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"
GROUP = "archive-group-449d2522330e"
MEMBERS = ("cand-4634",)
KU_ID = "units/archives/poussin-correspondance-jouanny-1911"
CARD_REL = "04-knowledge/units/archives/poussin-correspondance-jouanny-1911.md"
NAME_ZH = "尼古拉·普桑书信集"
NAME_EN = "Nicolas Poussin’s Correspondence (edited by Ch. Jouanny)"
ORIGINAL_TITLE = "Correspondance publiée d’après les originaux par Ch. Jouanny"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "7", "page": "176", "file": "07_CHP-7_sec_i.md", "lines": "315",
        "quote": "3 ibid., p. 31, note 2. 4 ibid., pp. 36 and 37; Brigand, 1962, p. 142.",
        "summary": "第7章 p.176 注3–4以 ibid. 回指 Poussin Correspondance，并引用第31页注2及第36–37页。",
        "note": "引用页码属于 Jouanny 编订的1911年版；本次未查阅被引版本。",
    },
    {
        "chapter": "21", "page": "433", "file": "21_CHP-21Bibliography.md", "lines": "1003",
        "quote": "Poussin, Nicolas: Correspondance publiée d’après les originaux par Ch. Jouanny, Paris 1911.",
        "summary": "第21章参考书目印刷页433列 Nicolas Poussin、Jouanny 编订的题名、Paris 与1911年。",
        "note": "按书目记录识别版次，不将书目信息当作已读原件或书信内容证据。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        location = f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}"
        if item.get("note"):
            location += f"；{item['note']}"
        rows.append({
            "citation": BOOK_CITATION,
            "location": location,
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    return rows


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "correspondence edition",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记 Nicolas Poussin 的 *{ORIGINAL_TITLE}*，即 Ch. Jouanny 编订、1911年在 Paris 出版的书信集。Haskell 第4、6、7章多次引用该版不同页码；第21章参考书目给出完整题名、编者、出版地和年份。此 KU 标识 Haskell 所引的1911年出版物，不表示已独立查阅该书、核实所称原件或读过其中的信件。

**English:** This card records Nicolas Poussin’s *{ORIGINAL_TITLE}*, the correspondence edition prepared by Ch. Jouanny and published in Paris in 1911. Chapters 4, 6, and 7 cite different pages of this edition, and Chapter 21’s bibliography supplies the full title, editor, place, and year. This KU identifies the 1911 publication cited by Haskell; it does not indicate independent consultation of the volume, verification of the originals it references, or reading of the individual letters.

### 书目身份

- **原题名：** *{ORIGINAL_TITLE}*；第21章参考书目，印刷页433。
- **责任者／编者：** Nicolas Poussin；Ch. Jouanny 编订。
- **出版信息：** Paris，1911年。
- **本书引用位置：** Haskell 引该版 pp.15、31注2、34、36–37、130、188、316 等；这些页码属于 Jouanny 1911年版。被引页未在本次登记中独立查阅。

### 身份边界

S3 新组 `archive-group-449d2522330e` 仅含出版物候选 `cand-4634`。被该书刊载或由 Haskell 转述的个别信件保持为各自 archive 候选，不并入此出版物；出版物的书目信息也不单独证明信件原件、作者归属或文本内容。当前 manifest 中没有同题同版 archive KU。

## 关系与证据

当前没有登记正式关系。S2 中八条关于 Haskell 引用该1911年版的关系候选留待 S6 核对端点、引用方向、各自书信语境及证据范围。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Jouanny 1911 Poussin correspondence edition in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id for cid in MEMBERS)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and ORIGINAL_TITLE.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    for item in SOURCES:
        text = " ".join((ROOT / "02-sources" / "02-Markdown" / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in text, (item["file"], item["quote"])

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert len(direct) == 9 and len(relations) == 8, (len(direct), len(relations))

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated archive card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n### S4 archive：Poussin 1911年 Jouanny 编订《书信集》身份组登记（{DATE}）\n\n"
        f"- `cand-4634` → `{GROUP}` → `{KU_ID}`；9条直接 S2 断言，其中8条书目引用候选留待 S6。"
        "第21章 p.433 参考书目列题名、Ch. Jouanny、Paris 与1911年；第4、6、7章注释提供不同页码的书内引用位置。"
        "个别信件与被引出版物保持对象边界；本次不新增正式关系、外部身份记录或 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_process = process_text + process_append

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; sources={len(SOURCES)}; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; direct_statements={len(direct)}; "
        f"relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
