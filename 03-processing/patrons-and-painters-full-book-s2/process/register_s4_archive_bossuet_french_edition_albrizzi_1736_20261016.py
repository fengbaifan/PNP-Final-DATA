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
GROUP = "archive-group-f295307228d2"
MEMBERS = ("cand-9987",)
KU_ID = "units/archives/bossuet-french-edition-albrizzi-1736"
CARD_REL = "04-knowledge/units/archives/bossuet-french-edition-albrizzi-1736.md"
NAME_ZH = "博须埃著作法文全集（阿尔布里齐版，1736年起）"
NAME_EN = "Complete French Edition of Bossuet’s Works (Albrizzi, Begun 1736)"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "13", "page": "334", "file": "13_CHP-13_intro.md", "lines": "29",
        "quote": "In 1736 he began to bring out a complete edition in French of the works of Bossuet, each volume of which was dedicated to a member of the Austrian royal family.",
        "summary": "第13章印刷页334称 Giambattista Albrizzi 于1736年开始刊行 Bossuet 著作的法文全集，每卷献给奥地利王室成员。",
        "note": "按上下文将 he 指向 Albrizzi；该版原书未查阅。",
    },
    {
        "chapter": "13", "page": "335", "file": "13_CHP-13_intro.md", "lines": "33",
        "quote": "Piazzetta began drawing for Albrizzi’s Bossuet a series of vignettes and illustrations of a delicate fantasy that were as new to Venetian books as they were to him.",
        "summary": "第13章印刷页335称 Piazzetta 为 Albrizzi 的 Bossuet 版绘制一组小图饰与插图。",
        "note": "这是 Haskell 对该出版物插图的叙述，不表示本轮查阅各卷或核实插图。",
    },
    {
        "chapter": "13", "page": "334", "file": "13_CHP-13_intro.md", "lines": "188",
        "quote": "3 This seems clear from the dedication of the eighth volume of the Bossuet in 1755.",
        "summary": "第13章 p.334 注3以1755年 Bossuet 版第八卷献词作为相邻论断的依据。",
        "note": "只确认书内提及第八卷及其献词年份，不据此推断全集的总卷数。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        location = f"第{item['chapter']}章，印刷页{item['page']}；Markdown 行{item['lines']}"
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
        "sub_type": "multi-volume edition",
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

**中文：** 本卡登记 Haskell 所述 Giambattista Albrizzi 于1736年开始刊行的 Bossuet 著作法文全集。第13章称每卷献给奥地利王室成员，并称 Piazzetta 为该版绘制小图饰与插图；注3提到1755年献给奥地利王室成员的第八卷。上述均为 Haskell 的书内叙述；本版各卷及具体被引卷均未在本轮查阅。中文题名为据描述拟定的工作名称，不是原版题名。

**English:** This card records the French-language complete edition of Bossuet’s works that Haskell says Giambattista Albrizzi began issuing in 1736. Chapter 13 says each volume was dedicated to a member of the Austrian royal family and that Piazzetta drew vignettes and illustrations for the edition; note 3 mentions a dedication of its eighth volume in 1755. These are Haskell’s statements; the volumes and cited passages were not consulted in this pass. The Chinese title is a descriptive working label, not an original edition title.

### 版本身份与范围

- **书内描述：** Bossuet 著作的法文全集；Haskell 称 Albrizzi 于1736年开始刊行。
- **卷册与献词：** Haskell 说明各卷分别献给奥地利王室成员；注3提及1755年第八卷献词。这里不推断总卷数或连续出版终年。
- **插图：** Haskell 将该版一组小图饰与插图归于 Piazzetta 的绘制工作；具体图像、卷册和印本未独立核验。
- **题名与刊记缺口：** 本书未给此版的确切原题名、完整刊记或总卷数；卡片不补造。

### 身份边界

S3 新组 {GROUP} 仅含 archive 候选 cand-9987，指向 Haskell 所述法文多卷版整体。它与 Bossuet 人物、Albrizzi 出版者人物、Piazzetta 人物及同章提及的其他出版物分开；也不把第八卷当作另一已识别版次或将单卷候选并入本组。

## 关系与证据

当前没有登记正式关系。7条直接 S2 关系候选留待 S6；本卡的身份登记不自动确认出版、献词或插图关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Albrizzi's French Bossuet edition in S4")
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
        and any(term in " ".join(row.values()).casefold() for term in ("bossuet", "french edition of bossuet"))
        for row in manifest
    )
    for item in SOURCES:
        source_text = " ".join((ROOT / "02-sources/02-Markdown" / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, (item["file"], item["quote"])

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
    assert len(direct) == 8 and len(relations) == 7, (len(direct), len(relations))

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
        f"\n\n### S4 archive：Albrizzi 1736年起 Bossuet 法文全集身份组登记（{DATE}）\n\n"
        f"- cand-9987 → {GROUP} → {KU_ID}。第13章 pp.334–335 称 Albrizzi 于1736年开始刊行 Bossuet 著作法文全集，每卷有奥地利王室成员献词，Piazzetta 为其绘制插图；注3提及1755年第八卷献词。未查阅该版各卷。\n"
        "- 直接 S2 记录8条，其中7条关系候选留待 S6。现有书内材料没有确切原题、完整刊记或总卷数；登记只指向该多卷版整体，不推断总卷数，也不单独建卷册卡。\n"
        "- 未新增正式关系、外部书目身份或 S5 补足。\n\n"
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
