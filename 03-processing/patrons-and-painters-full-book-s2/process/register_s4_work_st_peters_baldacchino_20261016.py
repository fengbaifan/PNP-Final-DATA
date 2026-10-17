from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import fitz
import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

CANDIDATE = "cand-4234"
GROUP = "workgrp-f64cef5b787fe5"
KU_ID = "units/works/baldacchino-st-peters-basilica"
CARD_REL = "04-knowledge/units/works/baldacchino-st-peters-basilica.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "圣彼得大殿华盖"
NAME_EN = "Baldacchino of St Peter’s Basilica"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "location": "第2章；印刷页34；OCR L39–40",
        "summary": "第2章称 Bernini 于1624年7月开始制作这件华盖以替换临时结构，并称整个工程在九年后完成；该句未给出具体完工年份。",
        "quotes": (
            ("lines 39", "In July 1624, less than a year after Urban’s assumption of power, Bernini began work on a gigantic baldacchino to replace the one that had been temporarily set above the supposed tomb of St Peter."),
            ("lines 40", "After nine years the whole project was eventually completed."),
        ),
        "span": "lines 39–40; print p. 34",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    },
    {
        "location": "第2章；印刷页35；OCR L43–47；PDF物理页16",
        "summary": (
            "第2章描述华盖的图像方案、巴贝里尼家族徽记、Pantheon青铜移用及费用。OCR将 L47 的 scudi 误读为 soldi；"
            "扫描印刷页16读作 scudi。本卡按扫描页保留原文读数；金额及收入比例仍只是 Haskell 的报告。"
        ),
        "quotes": (
            ("lines 43–44", "It had been planned to crown the edifice with a huge statue of the Risen Christ. At a later stage this was changed to a Cross, and the effect was to dedicate the monument to Christ’s passion rather than His triumph."),
            ("lines 46–47", "Urban VIII probably played a direct part in outlining the iconographical scheme: certainly he made sure that he should be closely identified with it."),
            ("lines 47", "The cost had been enormous—200,000 scudi or a tenth of the annual income of the papal states; and the removal, at Bernini’s suggestion, of bronze from the Pantheon, a step which led to a bitter little epigram from the Pope’s own doctor and the first of the grumblings that were to accompany many of his enterprises."),
        ),
        "span": "lines 43–47; print p. 35; PDF physical p. 16",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    },
    {
        "location": "第4章；印刷页97；OCR L27",
        "summary": "第4章提及 Bernini 在制作青铜铸件时曾暂离其 baldacchino 工作；该处用于核对跨章回指，不据此认定铸件属于华盖。",
        "quotes": (
            ("lines 27", "Bernini took time off from his work on the baldacchino to direct the operation."),
        ),
        "span": "lines 27; print p. 97",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
    },
    {
        "location": "第20章后记；印刷页397；OCR L15；PDF物理页2",
        "summary": "后记称 Hibbard 对 Lavin 著作的讨论及有关 Borromini 的研究使 Haskell 原先对 Bernini 与 Barberini 赞助者的直接归属需要限定；引述的研究本轮未独立查阅。",
        "quotes": (
            ("lines 15", "On the other hand, Hibbard’s discussion of Lavin’s book and of recent literature on Borromini shows that my straightforward attribution of the baldacchino to Bernini and his Barberini patrons needs some qualification."),
        ),
        "span": "lines 15; print p. 397; PDF physical p. 2",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
    },
)


def make_card():
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["source_file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch2p34 = "[第2章 p.34](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L39–40）"
    ch2p35 = "[第2章 p.35](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L43–47）"
    scanp35 = "[扫描印刷页](../../../02-sources/01-book/CHP-2.pdf)（PDF物理页16；印刷页35）"
    ch4p97 = "[第4章 p.97](../../../02-sources/02-Markdown/04_CHP-4_sec_i.md)（L27）"
    ch20p397 = "[第20章后记 p.397](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)（L15）"
    scanp397 = "[后记扫描页](../../../02-sources/01-book/CHP-20Postscript.pdf)（PDF物理页2；印刷页397）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录圣彼得大殿中央区域的 monumental baldacchino（华盖）作品。哈斯克尔称 Bernini 于1624年7月开始制作，以替代一座曾临时安置在“被认为是圣彼得之墓”上方的结构；第2章称整个工程在九年后完成，但没有给出具体完工年份。中文名称为描述性译名。{ch2p34}

**English:** This unit records the monumental baldacchino in the central area of St Peter’s Basilica. Haskell says Bernini began work on it in July 1624, replacing a temporary structure that had been set above the “supposed tomb of St Peter”; Chapter 2 says the project was completed after nine years but gives no calendar year for completion. The Chinese name is descriptive. {ch2p34}

### 作品性质与创作进程

- 作品类型：位于圣彼得大殿中央区域的 monumental baldacchino；圣彼得大殿建筑本体是独立的地点对象。此英文原称据原书用词，中文题名为描述性译名。{ch2p34} [圣彼得大殿地点卡](../places/st-peters-basilica.md)
- 开始制作：1624年7月；原书称其替换先前临时设置于“被认为是圣彼得之墓”上方的结构。{ch2p34}
- 工程完成：原书称“九年后”完成；不将持续时间换算为未明示的公历年份。{ch2p34}
- 图像方案：最初计划以一尊大型复活基督像加冕，后来改为十字架；Haskell 将这一变化解释为强调基督受难而非胜利。此为作者对方案寓意的说明。{ch2p35}
- 材料与费用记载：Haskell称工程青铜短缺通过移用 Pantheon 的青铜应对，并报告总费用为200,000 scudi、约为教宗国年收入的十分之一；扫描印刷页 p.35 读作 *scudi*，对应 OCR 的 *soldi* 为误读。金额及比例仅记录为 Haskell 的说法，未在本轮独立核实。{ch2p35} {scanp35}

### 跨章记载与归属限定

- 第4章 p.97 提及 Bernini 从 baldacchino 工作中暂时抽身去指挥一项青铜铸造操作；该句作为跨章回指，不据此认定该铸件属于华盖。{ch4p97}
- 第20章后记回顾较新的 Bernini 与 Borromini 研究后，明确称 Haskell 对作品直接归于 Bernini 及其 Barberini 赞助者的说法“需要一些限定”。因此本卡登记作品身份，同时保留作者归属状态；所引 Hibbard、Lavin 及相关研究未在本轮独立查阅。{ch20p397} {scanp397}

## 关系与证据

### 关系记录

当前没有已登记的正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main():
    parser = argparse.ArgumentParser(description="Register the St Peter's Baldacchino work identity in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_candidate = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE].get("suggested_type") == "work"
    alignment = alignment_by_candidate[CANDIDATE]
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert result_sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted
    assert not any(
        row.get("type") == "work"
        and any(term in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".lower()
                for term in ("baldacchino", "baldachin"))
        for row in manifest
    ), "a same-object work KU already exists in the manifest"

    for item in SOURCES:
        source = ROOT / item["source_file"]
        source_text = " ".join(source.read_text(encoding="utf-8-sig").split())
        for span, quote in item["quotes"]:
            normalized = " ".join(quote.split())
            # The two print readings differ from OCR only where the scanned page corrected it.
            if item["source_file"].endswith("02_CHP-2_sec_ii.md") and "200,000 scudi" in quote:
                assert "200,000 soldi" in source_text
                continue
            if item["source_file"].endswith("20_CHP-20Postscript.md"):
                normalized = normalized.replace("the baldacchino", "thebaldacchino")
            assert normalized in source_text, (item["location"], span, quote)

    pdf = fitz.open(ROOT / "02-sources/01-book/CHP-2.pdf")
    try:
        printed_p35 = pdf[15].get_text()
        assert re.search(r"\b35\b", printed_p35[:120]), "selected PDF page is not printed p.35"
        # The embedded text layer preserves the known OCR misread; the scan image was visually checked.
        assert re.search(r"200,000\s+soldi", printed_p35, flags=re.I), "known PDF text-layer reading changed"
    finally:
        pdf.close()

    statements = result_sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 15, f"unexpected direct statement count: {len(direct)}"
    assert len(direct_relations) == 14, f"unexpected direct relation candidate count: {len(direct_relations)}"
    cost = next(row for row in direct if row.get("statement_id") == "st-chp2-secii-l42-50-cost_reported")
    assert "scudi" in cost.get("qualifiers", {}).get("claim", "")
    assert "scudi" in cost.get("qualifiers", {}).get("qualification", "")
    attribution = next(row for row in direct if row.get("statement_id") == "st-chp20-p397-hibbard-qualifies-baldacchino-attribution")
    assert "needs qualification" in attribution.get("qualifiers", {}).get("claim", "")

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S4 work：圣彼得大殿华盖跨章身份组登记（2026-10-16）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）映射至[圣彼得大殿华盖作品卡](../../../04-knowledge/units/works/baldacchino-st-peters-basilica.md)。"
        "同一候选的书内提及横跨第2章、 第4章及第20章后记，S3 判为一个 work 身份组；地点圣彼得大殿、临时前置结构及 Pantheon 地点不并入本作品。"
        "第2章 p.34 称 Bernini 于1624年7月开始，九年后完成而未给公历完工年；p.35记方案变更及 Pantheon 青铜移用。"
        "已核 p.35 扫描印刷页（CHP-2 PDF物理页16）：费用词读作 scudi；book-statements 的 S2 qualifier 已记录 OCR soldi 与印刷 scudi 的校正，本轮不改 S2 表。"
        "第20章后记 p.397 将 Haskell 对 Bernini 及 Barberini patrons 的直接归属表述限定为需要进一步限定；所引研究未独立查阅，卡片保留该状态。"
        "15条直接 S2 陈述中的14条关系候选留待 S6；未新增正式关系、外部身份记录或 S5 补足。"
        f"S4 累计登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    result_note = (
        "\n\n### work：圣彼得大殿华盖 S4 登记（2026-10-16）\n\n"
        f"`{CANDIDATE}` 映射至[圣彼得大殿华盖作品卡](../units/works/baldacchino-st-peters-basilica.md)。"
        "跨章证据来自第2章 p.34–35、第4章 p.97 与第20章后记 p.397；卡片保留九年工期但不推算完工年，"
        "记录后记对 Bernini 与 Barberini 直接归属的限定，并依扫描页校正 p.35 的费用货币 OCR。"
        "15条直接陈述中14条关系候选留待 S6；本轮未新增正式关系、外部身份记录或 S5 补足。"
        f"全书 S4 当前登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 work dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"group members={len(group_rows)}; direct statements={len(direct)}; relation candidates={len(direct_relations)}")
        print("Chapter 2/4/20 source quotations checked; PDF p.35 text layer retains OCR soldi, while the scan image was visually read as scudi")
        print("Haskell's postscript qualification retained; manifest/accepted paths unique; no files changed")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}")
        print(f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    result_sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    result_sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; "
        f"pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
