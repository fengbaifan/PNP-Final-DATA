from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-archive-luzio-gonzaga-gallery-1913-20261017"
GROUP = "archive-group-32cf29336a05"
CANDIDATES = ("cand-7052",)
KU_ID = "units/archives/luzio-gonzaga-gallery-1913"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "《贡扎加画廊售予英国（1627–38）》"
NAME_EN = "The Gonzaga Gallery Sold to England in 1627–38"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CHP1_FILE = "02-sources/02-Markdown/01_CHP-1.md"
CHP7_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
BIBLIOGRAPHY_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
QUOTE_P10 = "Luzio, p. 292."
QUOTE_P13 = "Luzio, p. 48"
QUOTE_P14 = "Luzio, p. 295"
QUOTE_P177 = "3 Luzio, pp. 63-167."
QUOTE_BIB = "Luzio, Alessandro: La galleria dei Gonzaga venduta all’Inghilterra nel 1627-38, Milano 1913."
CITATION_IDS = (
    "st-chp1-secii-p13-n3-cites-luzio-p48-gozadini",
    "st-chp1-secii-p10-n4-cites-luzio-p292",
    "st-chp1-secii-p14-n2-cites-luzio-p48-reni",
    "st-chp1-secii-p14-n5-cites-luzio-p295-arragona-letter",
    "st-chp7-p177-n3-cite-luzio",
)
BIBLIOGRAPHY_STATEMENT = "st-chp21-bib-l701-754-entry-12"
HASKELL_CANDIDATE = "cand-2962"


def make_card() -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, bibliography, p. 428.",
            "location": "书目，印刷页428；OCR L722。",
            "sentence_summary": "哈斯克尔书目列出 Alessandro Luzio、题名 La galleria dei Gonzaga venduta all’Inghilterra nel 1627-38、Milano 和1913年。",
            "original_quotes": [
                {"source_span": "line 722; print p. 428", "text": QUOTE_BIB},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": BIBLIOGRAPHY_FILE,
                "source_span": "line 722; print p. 428",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 1, pp. 10, 13–14.",
            "location": "第一章，印刷页10注4、13注3、14注2与注5；OCR L377, 516, 563, 567–568。",
            "sentence_summary": "哈斯克尔分别引用 Luzio pp. 292、48、48、295；被引页及原书未独立查读。",
            "original_quotes": [
                {"source_span": "line 377; print p. 10 n. 4", "text": QUOTE_P10},
                {"source_span": "line 516; print p. 13 n. 3", "text": QUOTE_P13},
                {"source_span": "line 563; print p. 14 n. 2", "text": QUOTE_P13},
                {"source_span": "lines 567–568; print p. 14 n. 5", "text": QUOTE_P14},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP1_FILE,
                "source_span": "lines 377, 516, 563, 567–568; print pp. 10, 13–14",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 7, p. 177, n. 3.",
            "location": "第7章第一节，印刷页177注3；OCR L321。",
            "sentence_summary": "哈斯克尔注3引用 Luzio pp. 63–167；这是引文定位，不是对 Luzio 内容的核验。",
            "original_quotes": [
                {"source_span": "line 321; print p. 177 n. 3", "text": QUOTE_P177},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP7_FILE,
                "source_span": "line 321; print p. 177 n. 3",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 书目名称

- 原文题名：La galleria dei Gonzaga venduta all’Inghilterra nel 1627-38。[S1]
- 中文描述性译题：《贡扎加画廊售予英国（1627–38）》；英文描述性译题：The Gonzaga Gallery Sold to England in 1627–38。均为工作译名，不声称是出版物的官方译名。

### 书目记录

**中文：** 哈斯克尔书目将该书署名 Alessandro Luzio，出版地点为 Milano，年份为1913。此卡登记被引书目的来源内身份；Luzio 原书与下列被引页均未独立查读，不据脚注概述其内容。[S1–S3]

**English:** Haskell’s bibliography gives Alessandro Luzio as the author, Milano as the publication place, and 1913 as the year. This card records the source-local identity of the cited book. Neither Luzio’s book nor the cited pages below was independently consulted, so their contents are not summarized here. [S1–S3]

### 哈斯克尔的引用位置

- 第1章 p.10 n.4：Luzio p.292。[S2]
- 第1章 p.13 n.3 与 p.14 n.2：Luzio p.48；第1章 p.14 n.5：Luzio p.295。[S2]
- 第7章 p.177 n.3：Luzio pp.63–167。[S3]

这些页码仅记录哈斯克尔给出的引用定位，不证明 Luzio 原书相应页已核验，也不把被引信件或材料内容转写为本卡事实。

## 关系与证据

当前没有正式关系。下列书内引文候选留待 S6 逐条审查：

{chr(10).join(f"- {sid}" for sid in CITATION_IDS)}

书目陈述 {BIBLIOGRAPHY_STATEMENT} 仅支持出版记录，不登记为正式关系。
"""


def insert_accepted_path(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Luzio's 1913 Gonzaga gallery book in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert candidate_map[CANDIDATES[0]].get("suggested_type") == "archive"
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == list(CANDIDATES)
    assert decisions[CANDIDATES[0]].get("decision") == "new" and not decisions[CANDIDATES[0]].get("ku_id")
    assert decisions[HASKELL_CANDIDATE].get("decision") == "same"
    assert decisions[HASKELL_CANDIDATE].get("ku_id") == "units/archives/patrons-and-painters"
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English title already exists in manifest"

    source_texts = {
        CHP1_FILE: (ROOT / CHP1_FILE).read_text(encoding="utf-8-sig"),
        CHP7_FILE: (ROOT / CHP7_FILE).read_text(encoding="utf-8-sig"),
        BIBLIOGRAPHY_FILE: (ROOT / BIBLIOGRAPHY_FILE).read_text(encoding="utf-8-sig"),
    }
    assert QUOTE_P10 in source_texts[CHP1_FILE]
    assert source_texts[CHP1_FILE].count(QUOTE_P13) >= 2
    assert QUOTE_P14 in source_texts[CHP1_FILE]
    assert QUOTE_P177 in source_texts[CHP7_FILE]
    assert QUOTE_BIB in source_texts[BIBLIOGRAPHY_FILE]
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    for sid in CITATION_IDS:
        statement = statements[sid]
        assert statement.get("subject_candidate_id") == HASKELL_CANDIDATE
        assert statement.get("object_candidate_id") == CANDIDATES[0]
        assert statement["qualifiers"].get("relation_candidate") is True
    bibliography = statements[BIBLIOGRAPHY_STATEMENT]
    assert bibliography.get("object_candidate_id") == CANDIDATES[0]
    assert bibliography["qualifiers"].get("relation_candidate") is False

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: source-local bibliographic identity group {GROUP} maps to {KU_ID}; cited pages and work contents remain unverified."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_entry = f"""

<a id="{ANCHOR}"></a>

### S4 archive：Alessandro Luzio《La galleria dei Gonzaga》书目组登记（{DATE}）

单成员 S3 组 {GROUP}（`cand-7052`）依据第21章书目、多个脚注引用和第7章 p.177 n.3 的卷册标题定位，登记为[贡扎加画廊书目卡](../../../04-knowledge/units/archives/luzio-gonzaga-gallery-1913.md)。哈斯克尔书目列 Alessandro Luzio、题名 La galleria dei Gonzaga venduta all’Inghilterra nel 1627-38、Milano、1913；第1章脚注引用 Luzio pp.48、292、295，第7章脚注引用 pp.63–167。被引原书及页面未独立查读，卡片只登记书目身份与哈斯克尔提供的引文定位。

五条 S2 引用候选 {', '.join(CITATION_IDS)} 继续留待 S6 逐条审查；书目陈述 {BIBLIOGRAPHY_STATEMENT} 仅支持出版记录。端点哈斯克尔对应既有 archive KU `units/archives/patrons-and-painters`。本次未把脚注内容升级为 Luzio 原书的事实，未修改 `relations.csv`，未新增 S5 enrichment。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 archive：Luzio 贡扎加画廊书目组（{DATE}）\n\n"
        "单成员 S3 文献候选登记为 archive KU；仅保存 Haskell 书目记录及引用页码，原书内容未独立查读，五条引用关系留待 S6。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATES[0]} is the complete single-member S3 archive group {GROUP}")
        print("verified the bibliography identity, five Haskell citation locators, and existing Haskell archive endpoint")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv and enrichment.jsonl unchanged")
        print("planned writes: one bilingual archive card, accepted.yml, ku-manifest.csv, one alignment mapping, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Luzio archive group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
