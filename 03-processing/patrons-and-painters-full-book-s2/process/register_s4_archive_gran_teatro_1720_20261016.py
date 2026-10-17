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
GROUP = "archive-group-9db379e0572e"
MEMBERS = ("cand-1453",)
KU_ID = "units/archives/il-gran-teatro-pitture-prospettive-venezia-1720"
CARD_REL = "04-knowledge/units/archives/il-gran-teatro-pitture-prospettive-venezia-1720.md"
NAME_ZH = "《威尼斯绘画与透视大剧场》"
NAME_EN = "The Grand Theatre of Painting and Perspectives of Venice"
ORIGINAL_TITLE = "Il Gran Teatro delle Pitture e Prospettive di Venezia"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCES = [
    {
        "page": "332",
        "file": "13_CHP-13_intro.md",
        "lines": "12",
        "quote": (
            "II Gran Teatro delle Pitture e Prospettive di Venezia, published in 1720 by "
            "Domenico Lovisa with drawings of famous monuments and pictures by a number of "
            "artists, including the young Tiepolo."
        ),
        "summary": (
            "第13章称 *Il Gran Teatro delle Pitture e Prospettive di Venezia* 于1720年由 "
            "Domenico Lovisa 出版，包含著名纪念建筑的图绘及多位艺术家的画作，包括年轻时的 Tiepolo；"
            "同段称该出版物面向旅行者。Markdown OCR 将冠词识为“II”，S2 按 CHP-13.pdf 实体页1读作“Il”。"
        ),
        "location_note": "Markdown OCR 将冠词识为“II”；S2 按 CHP-13.pdf 实体页1读作“Il”，本卡沿用索引与 S2 身份组形式。",
        "source_span": "lines 12; print p. 332",
    },
    {
        "page": "333",
        "file": "13_CHP-13_intro.md",
        "lines": "16",
        "quote": "Such was the book sponsored by Domenico\nLovisa.",
        "summary": (
            "第13章第333页以跨页回指将前页所述出版物作为 Domenico Lovisa 资助的项目；"
            "本条身份指向由 S2 关联到第332页书名的同一出版物。"
        ),
        "location_note": "S2 将本句跨页回指至第332页的《Il Gran Teatro》；出版与资助作为不同角色保留。",
        "source_span": "lines 16; print p. 333",
    },
]


def source_rows():
    rows = []
    for item in SOURCES:
        location = f"第13章，印刷页{item['page']}；Markdown 行{item['lines']}"
        if item.get("location_note"):
            location += f"；{item['location_note']}"
        rows.append({
            "citation": BOOK_CITATION,
            "location": location,
            "sentence_summary": item["summary"],
            "original_quotes": [{
                "source_span": f"lines {item['lines']}",
                "text": item["quote"],
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": item["source_span"],
            },
        })
    return rows


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "illustrated book",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p332 = "[第13章 p.332](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L12）"
    p333 = "[第13章 p.333](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L16）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第13章所述的1720年出版物 *{ORIGINAL_TITLE}*。书内称其由 Domenico Lovisa 出版，载有著名纪念建筑的图绘及多位艺术家的画作，包括年轻时的 Giambattista Tiepolo，并称两种威尼斯出版物面向旅行者；第333页将本书回指为 Lovisa 资助的出版项目。上述信息均为哈斯克尔的书内记载，未独立查阅该出版物。中英文显示名均为描述性工作译名。{p332} {p333}

**English:** This card records the 1720 publication *{ORIGINAL_TITLE}* described in Haskell’s Chapter 13. Haskell says that Domenico Lovisa published it, that it contains drawings of famous monuments and pictures by several artists, including the young Giambattista Tiepolo, and that the two Venetian publications discussed there were intended for travellers. On p. 333 he refers back to this book as a publishing venture sponsored by Lovisa. These are statements in Haskell’s book; the publication was not independently consulted. The Chinese and English display names are descriptive working translations. {p332} {p333}

### 文献身份与书内记载

- **原题名：** *{ORIGINAL_TITLE}*；第13章正文及索引使用该题名。第13章 Markdown OCR 行12将冠词识为 `II`；S2 按 CHP-13.pdf 实体页1读取为 `Il`。本卡采用 S3 组的读法，保留原始 OCR 差异，不声称已校勘原版刊物。{p332}
- **出版年份：** 1720；Haskell 第13章 p.332 明载。现有依据未给出出版地、具体印刷者、版次、卷数或馆藏号，本卡不补写。{p332}
- **出版者：** Domenico Lovisa；Haskell 称其出版该书。S2 另将 p.333 的回指记录为 Lovisa 资助该项目；出版与资助是分开的书内角色陈述。其人物候选 `cand-1452` 有单独的 S3 新组，未并入本 archive 组。{p332} {p333}
- **内容与受众：** 书内称其含著名纪念建筑的图绘及多位艺术家的画作，并将年轻的 Giambattista Tiepolo 列为其中一位；原文未列全体艺术家或逐幅作品。Haskell 同段称其面向旅行者。{p332}
- **显示名称：** 中文名与英文名均为描述性工作译名；原题名保留意大利语形式。{p332}

### 身份边界

S3 新身份组 `{GROUP}` 仅含 archive 候选 `cand-1453`。它不与同段提及的 *Le Fabriche e Vedute di Venetia*、Marieschi 1741 年景观出版物、出版者 Domenico Lovisa 人物候选 `cand-1452` 或 Tiepolo 人物 KU 合并；文中未逐一辨明的图绘和画作也不在本组另立 work KU。

## 关系与证据

当前没有登记正式关系。与出版者、插图艺术家及受众有关的4条直接 S2 关系候选留待 S6；本次只登记出版物身份，不把来源字段或正文叙述转为正式关系。{p332} {p333}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Il Gran Teatro in S4")
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
    assert set(MEMBERS) <= set(candidate_by_id)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
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
        source_text = " ".join((ROOT / "02-sources" / "02-Markdown" / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, (item["file"], item["quote"])

    statements = sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert len(direct) == 4 and len(relations) == 4, (len(direct), len(relations))

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
        f"\n\n### S4 archive：《Il Gran Teatro delle Pitture e Prospettive di Venezia》1720年出版物身份组登记（{DATE}）\n\n"
        f"- `cand-1453` → `{GROUP}` → `{KU_ID}`；依据第13章 p.332 的题名、1720年出版信息及第333页跨页回指，并以索引 L.csv#111 作为候选锚点。OCR 的 `II` 与 S2 在 CHP-13.pdf 实体页1读取的 `Il` 区别已记录；显示译名为工作译名，不扩展未载的出版信息。\n"
        "- 直接 S2 记录4条，均为关系候选：出版者 Domenico Lovisa、其资助角色、插图艺术家（含已复用人物 KU Giambattista Tiepolo）及旅行者受众；4条均留待 S6。Lovisa 的人物候选 `cand-1452` 属独立 S3 person 新组，未并入本 archive 组；未新增正式关系或 S5 补足。\n"
        "- 本卡不合并同段另述的 *Le Fabriche e Vedute di Venetia* 与 Marieschi 1741 年出版物，也不将未逐一辨明的插图拆成 work KU。原出版物未独立查阅。\n\n"
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
