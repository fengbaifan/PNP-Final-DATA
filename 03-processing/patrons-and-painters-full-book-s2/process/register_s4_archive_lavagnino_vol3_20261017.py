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
ANCHOR = "s4-archive-lavagnino-artisti-italiani-germania-iii-20261017"
CANDIDATES = ("cand-7251", "cand-11371")
GROUP = "archive-group-lavagnino-artists-germany-vol3-1943"
KU_ID = "units/archives/lavagnino-artisti-italiani-germania-iii-1943"
CARD_REL = "04-knowledge/units/archives/lavagnino-artisti-italiani-germania-iii-1943.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "《在德国的意大利艺术家》第三卷：画家与版画家"
NAME_EN = "Italian Artists in Germany, III: Painters and Printmakers"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CHP7_FILE = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
CHP10_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
BIBLIOGRAPHY_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
SOURCE_QUOTE = (
    "3 Lavagnino, p. 69, and Heilbronner, pp. 887-904.",
    "1 Lavagnino, p. 66.",
    "Lavagnino, E.: Gli artisti italiani in Germania, III: I pittori e gl’incisori, Roma 1943.",
    "Lavagnino, p. 85",
    "Lavagnino, p. 120, and M. Goering, 1937, pp. 233-50.",
    "2 Lavagnino, p. 115.",
)
RELATION_IDS = (
    "st-chp7-p193-n3-cite-lavagnino",
    "st-chp7-p194-n1-lavagnino",
)
BIBLIOGRAPHY_STATEMENT = "st-chp21-bib-l658-699-entry-06"


def make_card() -> str:
    source_specs = (
        {
            "citation": f"{BOOK_CITATION}, ch. 7, p. 193, n. 3.",
            "location": "第7章第四节，印刷页193注3；OCR L99",
            "summary": "哈斯克尔注3引用 Lavagnino 第III卷第69页；该被引页面未独立查读。",
            "quote": SOURCE_QUOTE[0],
            "file": CHP7_FILE,
            "span": "L99; print p. 193 n. 3",
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 7, p. 194, n. 1.",
            "location": "第7章第四节，印刷页194注1；OCR L100",
            "summary": "哈斯克尔注1引用 Lavagnino 第66页；该被引页面未独立查读。",
            "quote": SOURCE_QUOTE[1],
            "file": CHP7_FILE,
            "span": "L100; print p. 194 n. 1",
        },
        {
            "citation": f"{BOOK_CITATION}, bibliography, p. 427.",
            "location": "书目，印刷页427；OCR L667",
            "summary": "书目完整列出 E. Lavagnino 的书名、卷次副题、出版地 Roma 与年份1943。",
            "quote": SOURCE_QUOTE[2],
            "file": BIBLIOGRAPHY_FILE,
            "span": "L667; print p. 427",
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 10, p. 282, n. 3.",
            "location": "第10章，印刷页282注3；OCR L522",
            "summary": "此注引用 Lavagnino 第85页，但未标卷次；S3 未将该引注归入本卡所指第III卷。",
            "quote": SOURCE_QUOTE[3],
            "file": CHP10_FILE,
            "span": "L522; print p. 282 n. 3",
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 10, p. 283, n. 2.",
            "location": "第10章，印刷页283注2；OCR L523",
            "summary": "此注引用 Lavagnino 第120页，但未标卷次；S3 未将该引注归入本卡所指第III卷。",
            "quote": SOURCE_QUOTE[4],
            "file": CHP10_FILE,
            "span": "L523; print p. 283 n. 2",
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 10, p. 294, n. 2.",
            "location": "第10章，印刷页294注2；OCR L562",
            "summary": "此注仅写 Lavagnino 第115页，卷次及其与本卡书目的对应关系未核。",
            "quote": SOURCE_QUOTE[5],
            "file": CHP10_FILE,
            "span": "L562; print p. 294 n. 2",
        },
    )
    sources = []
    for item in source_specs:
        sources.append({
            "citation": item["citation"],
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
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
    cited = "\n".join(f"- `{sid}`" for sid in RELATION_IDS)
    body = f"""## 内容

### 描述

**中文：** 本卡依据哈斯克尔书后书目登记 E. Lavagnino 所著《在德国的意大利艺术家》第III卷《画家与版画家》（中文工作译题）。书目列其出版地为 Roma、出版年为1943。第7章 pp.193–194 的脚注分别引用第69、66页；被引原书和页面均未独立查读，因此卡片只记录书目身份和哈斯克尔的引文定位，不转述被引内容。

**English:** This card records the volume by E. Lavagnino listed in Haskell’s bibliography as *Gli artisti italiani in Germania, III: I pittori e gl’incisori* (working English translation: *Italian Artists in Germany, III: Painters and Printmakers*). The entry gives Roma and 1943. Haskell’s chapter 7 notes on pp. 193–194 cite pp. 69 and 66 respectively. Neither the cited volume nor those pages was independently consulted, so this card records bibliographic identity and Haskell’s citation locators without summarizing the cited work.

### 书目记录

| 字段 | 值 | 依据 |
|---|---|---|
| 书目题名（原文） / Title as printed | Gli artisti italiani in Germania, III: I pittori e gl’incisori | 第21章书目，印刷页427；S3 |
| 作者署名 / Author as printed | E. Lavagnino | 第21章书目，印刷页427；S3 |
| 卷次 / Volume | III | 第21章书目，印刷页427；S3 |
| 副题 / Subtitle | I pittori e gl’incisori | 第21章书目，印刷页427；S3 |
| 出版地点 / Publication place | Roma | 第21章书目，印刷页427；S3 |
| 出版年份 / Publication year | 1943 | 第21章书目，印刷页427；S3 |
| 文献类型 / Record type | 图书 / book | 第21章书目，印刷页427；S3 |

### 哈斯克尔的引用位置

| 字段 | 值 | 依据 |
|---|---|---|
| 哈斯克尔 p.193 n.3 的被引页 / Cited page in Haskell p.193 n.3 | 第69页；原书未查读 | 第7章 p.193 n.3；S1 |
| 哈斯克尔 p.194 n.1 的被引页 / Cited page in Haskell p.194 n.1 | 第66页；原书未查读 | 第7章 p.194 n.1；S2 |
| 未归入本卷的引注（p.282 n.3） / Unassigned citation (p.282 n.3) | Lavagnino 第85页；引注未标卷次 | 第10章 p.282 n.3；S4 |
| 未归入本卷的引注（p.283 n.2） / Unassigned citation (p.283 n.2) | Lavagnino 第120页；引注未标卷次 | 第10章 p.283 n.2；S5 |
| 卷次待核的引注（p.294 n.2） / Citation with unresolved volume (p.294 n.2) | Lavagnino 第115页；卷次与本卷对应关系未核 | 第10章 p.294 n.2；S6 |

### 阅读与范围

**中文：** 当前依据限于哈斯克尔的脚注和书目。未从本书目记录推定出版者、完整作者姓名、被引页面内容或未标卷次引注的具体卷册。

**English:** The current evidence is limited to Haskell’s notes and bibliography. No publisher, expanded author name, content of the cited pages, or volume assignment for citations that omit a volume is inferred from this record.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

书内脚注引用候选仍待 S6 裁决：

{cited}
"""
    return f"---\n{fm}---\n\n{body}"


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
    parser = argparse.ArgumentParser(description="Register the Lavagnino volume III archive group in S4.")
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

    assert all(cid in candidate_map and candidate_map[cid].get("suggested_type") == "archive" for cid in CANDIDATES)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == list(CANDIDATES)
    for cid in CANDIDATES:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert candidate_map["cand-11371"].get("candidate_source_ref") == "chp-21:21_CHP-21Bibliography:l658-699#L667"
    assert candidate_map["cand-7251"].get("candidate_source_ref") == "chp-7:07_CHP-7_sec_iv:l97-119#L99"
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English title already exists in manifest"

    source_texts = {
        CHP7_FILE: (ROOT / CHP7_FILE).read_text(encoding="utf-8-sig"),
        CHP10_FILE: (ROOT / CHP10_FILE).read_text(encoding="utf-8-sig"),
        BIBLIOGRAPHY_FILE: (ROOT / BIBLIOGRAPHY_FILE).read_text(encoding="utf-8-sig"),
    }
    assert SOURCE_QUOTE[0] in source_texts[CHP7_FILE]
    assert SOURCE_QUOTE[1] in source_texts[CHP7_FILE]
    assert SOURCE_QUOTE[2] in source_texts[BIBLIOGRAPHY_FILE]
    assert all(quote in source_texts[CHP10_FILE] for quote in SOURCE_QUOTE[3:])
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    for sid in RELATION_IDS:
        statement = statements[sid]
        assert statement.get("object_candidate_id") == "cand-7251"
        assert statement["qualifiers"].get("relation_candidate") is True
    bibliography_statement = statements[BIBLIOGRAPHY_STATEMENT]
    assert bibliography_statement.get("object_candidate_id") == "cand-11371"
    assert bibliography_statement["qualifiers"].get("relation_candidate") is False

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: cross-chapter archive group {GROUP} maps to {KU_ID}."

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

### S4 archive：E. Lavagnino《Gli artisti italiani in Germania》第III卷跨章组登记（{DATE}）

`cand-7251`（第7章 p.193 n.3、p.194 n.1 引文候选）与 `cand-11371`（第21章 p.427 书目候选）属于既有 S3 跨章组 `{GROUP}`，据书目中的作者、卷次、副题、出版地和年份对应为同一册。现以一张[《在德国的意大利艺术家》第三卷：画家与版画家](../../../04-knowledge/units/archives/lavagnino-artisti-italiani-germania-iii-1943.md) archive KU 接收两条候选映射。中文、英文题名均为项目工作译题；书目只署名 `E. Lavagnino`，未补作者全名或出版者。

`st-chp7-p193-n3-cite-lavagnino` 与 `st-chp7-p194-n1-lavagnino` 保留为 S2 书内引用关系候选，留待 S6；被引原书及 p.69、p.66 均未独立查读。p.282 n.3 的 p.85 与 p.283 n.2 的 p.120 未标卷次，按 S3 决定不归入本卷；p.294 n.2 的 p.115 也未核准其卷次归属。书目陈述 `st-chp21-bib-l658-699-entry-06` 仅支持出版记录，不登记为正式关系。本次未修改 `relations.csv`。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 archive：E. Lavagnino 第III卷（{DATE}）\n\n"
        "第7章脚注与第21章书目候选按同一跨章 S3 组映射至一张 archive KU；被引原书未读，其他未标卷次引注继续待核。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {', '.join(CANDIDATES)} are the complete two-member S3 group {GROUP}")
        print("verified chapter 7 citation notes, chapter 21 bibliography record, and unassigned chapter 10 locators")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv unchanged")
        print("planned writes: one bilingual archive card, accepted.yml, ku-manifest.csv, two alignment mappings, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Lavagnino volume III archive group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
