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
GROUP = "archive-group-la-harpe-filosofo-dell-alpi-1780"
MEMBERS = ("cand-1345", "cand-9829")
KU_ID = "units/archives/il-filosofo-dell-alpi-ode"
CARD_REL = "04-knowledge/units/archives/il-filosofo-dell-alpi-ode.md"
NAME_ZH = "《阿尔卑斯山哲人》"
NAME_EN = "The Philosopher of the Alps"
ORIGINAL_TITLE = "Il Filosofo dell’Alpi"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "10", "page": "327", "file": "02-Markdown/10_CHP-10_sec_ii.md", "lines": "237",
        "quote": "Among the less offensive poems that had been published to celebrate Pisani’s",
        "summary": "第10章印刷页327的段落在跨页处提及庆祝 Pisani 的诗作；现有 Markdown OCR 该行后半出现语法损坏，须与 p.328 续句及 S2 锚点合读。",
        "note": "不单凭此残缺 OCR 行裁定句法；书内原件页未在本轮复核。",
    },
    {
        "chapter": "10", "page": "328", "file": "02-Markdown/10_CHP-10_sec_ii.md", "lines": "242",
        "quote": "election was one called II Filosofo dell’Alpi.1",
        "summary": "第10章印刷页328续接前页段落，点名 Il Filosofo dell’Alpi，并称其为关于阿尔卑斯山与自然的热情作品，译自法语且受 Rousseau 影响。",
        "note": "Markdown 将冠词识别为 II；卡片题名采用 S3 身份组的阅读形式 Il，并保留转录差异。",
    },
    {
        "chapter": "10", "page": "328", "file": "02-Markdown/10_CHP-10_sec_ii.md", "lines": "338",
        "quote": "1 II Filosofo del!Alpi—Ode del Signor de la Harpe del!AccademiaFrancese liberamente ridotta in Versi Sciolti italiani da Giuseppe Fossati Veneziano..... In. Venezia per Giacomo Storti, MDCCLXXX.",
        "summary": "第10章印刷页328注1把标题列作 ode，署 de la Harpe，称 Giuseppe Fossati 将其自由改写为意大利无韵诗，并列 Venezia、Giacomo Storti 与 MDCCLXXX（1780）刊记。",
        "note": "照录 Markdown OCR 中的 II、del!、连写与省略号；未对照扫描页或查阅该印本，标点和拼写不作校勘。",
    },
    {
        "chapter": "10", "page": "328", "file": "03-Index/03-2-Index-CSV/L.csv", "lines": "4",
        "quote": "La Harpe,,Il Filosofo dell'Alpi,,328",
        "summary": "全书索引在 La Harpe 名下列出 Il Filosofo dell’Alpi，指向印刷页328；它与第10章正文候选共同构成该 S3 身份组。",
        "note": "索引子条目用于候选映射，不表示另一个文本版本。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        location = f"第{item['chapter']}章，印刷页{item['page']}；文件行{item['lines']}"
        if item.get("note"):
            location += f"；{item['note']}"
        rows.append({
            "citation": BOOK_CITATION,
            "location": location,
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    return rows


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "ode",
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

**中文：** 本卡记录 Haskell 第10章所称的 ode *{ORIGINAL_TITLE}*。正文将其描述为关于阿尔卑斯山与自然、译自法语并受 Rousseau 影响的作品；注1所引刊记称 de la Harpe 作、Giuseppe Fossati 将其自由改写为意大利无韵诗，由 Giacomo Storti 于 Venezia 刊行，时间为1780年。上述身份与版本信息仅据 Haskell 正文、注释和索引；未查阅该刊本。中文标题为描述性工作译名。

**English:** This card records the ode *{ORIGINAL_TITLE}* named in Chapter 10. Haskell describes it as an enthusiastic work about the Alps and Nature, translated from French and influenced by Rousseau. The imprint quoted in note 1 attributes it to de la Harpe, says Giuseppe Fossati freely rendered it into Italian blank verse, and gives Giacomo Storti, Venezia, and 1780. These identity and edition details are based on Haskell’s text, note, and index; the printed item was not consulted. The Chinese title is a descriptive working translation.

### 文献身份与刊记

- **题名：** 正文与索引作 *Il Filosofo dell’Alpi*；注释 OCR 作 `II Filosofo del!Alpi`。本卡采用 S3 身份组使用的题名阅读，原始转录差异留在来源摘录中，未声称已据扫描页校勘。
- **文献形式：** 注释将其称为 ode；据候选与 S3 决定，本卡指向诗作文本，不指某一存世实物副本。
- **署名与改写：** 注释刊记署 de la Harpe，并称 Giuseppe Fossati 将其自由改写为意大利无韵诗；本卡不补充二人的外部身份。
- **刊记：** Venezia，Giacomo Storti，MDCCLXXX（1780）；这是 Haskell 所引刊记，不等同于已检查刊本或馆藏记录。

### 身份边界

S3 新组 `{GROUP}` 由索引子条目候选 `cand-1345` 和第10章正文候选 `cand-9829` 组成，同映射为该 ode 文本。它与 de la Harpe 人物候选 `cand-1344`、Giuseppe Fossati、Giacomo Storti、Accademia Francese 及 Giorgio Pisani 候选分开；不将 p.326 另述的宣传册或版画并入本组。跨页 p.327 的现存 OCR 有断句／识别损坏，本卡保留该限制，不据残句扩展事实。

## 关系与证据

当前没有登记正式关系。直接 S2 中的7条关系候选留待 S6；候选数量及去向见过程记录。对象身份登记不表示这些关系已成立，也不表示被引刊本已独立核验。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Il Filosofo dell'Alpi in S4")
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
        and "il filosofo dell'alpi" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    for item in SOURCES:
        source_file = ROOT / "02-sources" / Path(item["file"])
        source_text = " ".join(source_file.read_text(encoding="utf-8-sig").split())
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
        f"\n\n### S4 archive：de la Harpe《Il Filosofo dell’Alpi》身份组登记（{DATE}）\n\n"
        f"- `cand-1345`（索引子条目）与 `cand-9829`（第10章正文）→ `{GROUP}` → `{KU_ID}`；两条 S3 new 候选对应一张 archive KU。索引 p.328 与正文 p.328 的题名互证；注1刊记称其为 de la Harpe 的 ode，由 Giuseppe Fossati 改写成意大利无韵诗，Giacomo Storti 于 Venezia 刊行，MDCCLXXX（1780）。未查阅该刊本。\n"
        "- 直接 S2 记录8条，其中7条关系候选留待 S6。第10章 p.327 跨页段的 Markdown OCR 有语法损坏，按 p.328 续文和既有 S2 记录保留，不从损坏句段外推。S3 已将诗作与同页另述的宣传册／版画分开；人物与出版者端点亦不并入本 KU。\n"
        "- 题名转录存在正文 `II` 与索引 `Il`、注释 OCR `del!` 的差异；卡片采用组内规范题名并保留来源摘录，不声称扫描页校勘。未新增正式关系或 S5 外部补足。\n\n"
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
