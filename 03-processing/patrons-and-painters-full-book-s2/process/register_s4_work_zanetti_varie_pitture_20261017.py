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
ANCHOR = "s4-work-zanetti-varie-pitture-20261017"
GROUP = "workgrp-25c14f82a2c959"
CANDIDATES = ("cand-2859", "cand-10117")
UNDECIDED_AUTHOR = "cand-2854"
KU_ID = "units/works/varie-pitture-a-fresco-principal-venetian-masters"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "《威尼斯主要名家的各式壁画》"
NAME_EN = "Various Fresco Paintings by the Principal Venetian Masters"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv"
CHP13_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
BIBLIOGRAPHY_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
QUOTES = {
    "index_title": "Varie Pitture a Fresco",
    "copies": "His own drawings and prints were limited to copies of some of the great classic artists which he published as",
    "title_ocr": "Varíe Pitture a Fresco in 1760",
    "preface": "In the preface to Varie Pitture a Fresco de'Principali Maestri Veneziani, 1760.",
    "bibliography": "Zanetti, A. M.: Varie pitture a fresco de’ principali maestri veneziani, Venezia 1760.",
}
PUBLICATION_STATEMENT = "st-chp13-p345-varie-pitture-1760"
PREFACE_STATEMENT = "st-chp13-p343-notes-note2-varie-pitture-preface-source"
BIBLIOGRAPHY_STATEMENT = "st-chp21-bib-l1261-1299-entry-14"


def make_card() -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, index, s.v. Zanetti, A. M., the Younger.",
            "location": "书后索引，UVWXYZ.csv#196；印刷页345。",
            "sentence_summary": "索引把 Varie Pitture a Fresco 列在 Zanetti, A. M., the Younger 主项下，并指向第13章 p.345。",
            "original_quotes": [
                {"source_span": "UVWXYZ.csv#196", "text": QUOTES["index_title"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters-index",
                "source_file": INDEX_FILE,
                "source_span": "UVWXYZ.csv#196",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 13, p. 345.",
            "location": "第13章，印刷页345；OCR L163–164。",
            "sentence_summary": "哈斯克尔称较年轻的 Zanetti 的绘画与版画限于临摹古典名家作品，并以 Varie Pitture a Fresco 之名于1760年出版；原文 OCR 将 Varie 误作 Varíe，S2 校读记录以印本为准。",
            "original_quotes": [
                {"source_span": "lines 163–164; print p. 345", "text": QUOTES["copies"]},
                {"source_span": "line 164; print p. 345", "text": QUOTES["title_ocr"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP13_FILE,
                "source_span": "lines 163–164; print p. 345",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 13, p. 343, n. 2.",
            "location": "第13章，印刷页343注2；OCR L236。",
            "sentence_summary": "脚注将相关论述定位于1760年版本的序言；被引版本未独立查读。",
            "original_quotes": [
                {"source_span": "line 236; print p. 343 n. 2", "text": QUOTES["preface"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP13_FILE,
                "source_span": "line 236; print p. 343 n. 2",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, bibliography, p. 441.",
            "location": "书目，印刷页441；OCR L1284。",
            "sentence_summary": "书目署名 Zanetti, A. M.，列出题名及 Venezia、1760；书目记录不证明本项目已查阅该出版物。",
            "original_quotes": [
                {"source_span": "line 1284; print p. 441", "text": QUOTES["bibliography"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": BIBLIOGRAPHY_FILE,
                "source_span": "line 1284; print p. 441",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
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

### 题名

- 原文题名：Varie pitture a fresco de’ principali maestri veneziani；哈斯克尔正文简写为 Varie Pitture a Fresco。[S1–S4]
- 中文描述性译题：《威尼斯主要名家的各式壁画》；英文描述性译题：Various Fresco Paintings by the Principal Venetian Masters。均为工作译名，不声称是官方译名。
- 第13章 p.345 的 OCR 写作 Varíe；S2 校读记载印本为 Varie，本卡沿用校读后的拼写。[S2]

### 作品信息

**中文：** 哈斯克尔称“较年轻的 Zanetti”制作了古典名家作品的摹本，并于1760年以 Varie Pitture a Fresco 之名出版；书目将作者署名列为 Zanetti, A. M.。本卡依 S3 类型决定记录为视觉作品／图册，不把书目引文另拆成第二个对象。被引出版物及其图像未独立查阅，作品的具体图像、媒介、技法、数量和版本内容仍未确认。[S2–S4]

**English:** Haskell says that the “younger Zanetti” made copies after classic artists and published them in 1760 as Varie Pitture a Fresco; the bibliography gives the author as “Zanetti, A. M.” Following the S3 type decision, this card records the visual work or album and does not split the bibliographic citation into a second object. The cited publication and its images were not independently consulted, so its specific images, medium, technique, number of items, and edition contents remain unconfirmed. [S2–S4]

### 作者身份边界

正文称 Antonio Maria the Younger，书目署名为 A. M. Zanetti；同名堂亲关系及其与既有人物 KU 的对应仍未裁定（cand-2854，S3 undecided）。本卡只保留来源中的署名与归属说法，不据此确认该人物身份或建立正式创作者关系。[S2, S4]

## 关系与证据

当前没有正式关系。{PUBLICATION_STATEMENT} 保留为作品与未决人物候选之间的 S2 关系候选，待人物身份及角色证据裁决后再由 S6 审查。{PREFACE_STATEMENT} 是脚注书目定位，不是历史关系；{BIBLIOGRAPHY_STATEMENT} 只证明哈斯克尔书目列出该出版物。

### 来源

- S1：书后索引 UVWXYZ.csv#196，子目 Varie Pitture a Fresco。
- S2：第13章 p.345，关于临摹古典名家及1760年出版的叙述；OCR 校读依 S2 记录。
- S3：第13章 p.343 n.2，将相关论述定位于1760年版本序言；原出版物未查读。
- S4：书目 p.441，作者署名、题名、出版地和年份。
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
    parser = argparse.ArgumentParser(description="Register the Varie Pitture work group in S4.")
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

    assert all(candidate_map[cid].get("suggested_type") == "work" for cid in CANDIDATES)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)
    for cid in CANDIDATES:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert decisions[UNDECIDED_AUTHOR].get("decision") == "undecided"
    assert not decisions[UNDECIDED_AUTHOR].get("ku_id")
    assert candidate_map["cand-2855"].get("suggested_type") == "archive"
    assert candidate_map["cand-2858"].get("suggested_type") == "archive"
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "work" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English title already exists in manifest"

    source_texts = {
        INDEX_FILE: (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig"),
        CHP13_FILE: (ROOT / CHP13_FILE).read_text(encoding="utf-8-sig"),
        BIBLIOGRAPHY_FILE: (ROOT / BIBLIOGRAPHY_FILE).read_text(encoding="utf-8-sig"),
    }
    assert QUOTES["index_title"] in source_texts[INDEX_FILE]
    assert QUOTES["copies"] in source_texts[CHP13_FILE]
    assert QUOTES["title_ocr"] in source_texts[CHP13_FILE]
    assert QUOTES["preface"] in source_texts[CHP13_FILE]
    assert QUOTES["bibliography"] in source_texts[BIBLIOGRAPHY_FILE]
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    publication = statements[PUBLICATION_STATEMENT]
    assert publication.get("subject_candidate_id") == "cand-10117"
    assert publication.get("object_candidate_id") == UNDECIDED_AUTHOR
    assert publication["qualifiers"].get("relation_candidate") is True
    preface = statements[PREFACE_STATEMENT]
    assert preface.get("object_candidate_id") == "cand-10117"
    assert preface["qualifiers"].get("relation_candidate") is False
    bibliography = statements[BIBLIOGRAPHY_STATEMENT]
    assert bibliography.get("object_candidate_id") == "cand-10117"
    assert bibliography["qualifiers"].get("relation_candidate") is False

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: visual-work identity group {GROUP} maps to {KU_ID}; related person endpoint cand-2854 remains undecided."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "work",
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

### S4 work：Zanetti《Varie Pitture a Fresco》跨章作品组登记（{DATE}）

既有 S3 组 {GROUP} 的 `cand-2859`（UVWXYZ.csv#196，Zanetti 主项下的 Varie Pitture a Fresco 子目）与 `cand-10117`（第13章正文及第21章书目链接）均为 `new`，统一映射至[《威尼斯主要名家的各式壁画》作品卡](../../../04-knowledge/units/works/varie-pitture-a-fresco-principal-venetian-masters.md)。第13章 p.345 说“较年轻的 Zanetti”制作古典名家作品的摹本，并于1760年以 Varie Pitture a Fresco 之名出版；第21章书目列完整题名、A. M. Zanetti、Venezia 和1760年。被引出版物未独立查阅，卡片不补图像目录、媒介、技法、数量或具体版本内容。

作品类型依据图像摹本／视觉图册语境；仅因被书目列载，不另复制成 archive KU。相关文本出版物候选 `cand-2855` 与 `cand-2858` 类型不同，继续各按其自身 S3 决定处理。作者候选 `cand-2854` 仍为 `undecided`，不映射人物 KU；因此 `{PUBLICATION_STATEMENT}` 的创作者／出版者关系保持待 S3 身份解决后再交 S6。`{PREFACE_STATEMENT}` 是引用定位，`{BIBLIOGRAPHY_STATEMENT}` 是书目记录，均不升级为关系。本次未修改 `relations.csv`，未新增 S5 enrichment。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 work：Zanetti《Varie Pitture a Fresco》（{DATE}）\n\n"
        "跨章索引与正文候选映射至一张 work KU；出版物未独立查读，作者人物候选 cand-2854 仍未决，关系保持待证。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {', '.join(CANDIDATES)} are the complete two-member S3 group {GROUP}")
        print(f"preserved {UNDECIDED_AUTHOR} as undecided; no creator identity or formal relation asserted")
        print("verified index title, chapter 13 publication statement, preface locator, bibliography record, and separate archive candidates")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv and enrichment.jsonl unchanged")
        print("planned writes: one bilingual work card, accepted.yml, ku-manifest.csv, two alignment mappings, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Varie Pitture work group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
