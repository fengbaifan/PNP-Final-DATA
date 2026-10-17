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
ANCHOR = "s4-term-contracts-artistic-commissions-20261017"
GROUP = "sg3-term-contracts"
CANDIDATES = ("cand-0837", "cand-0839", "cand-0840", "cand-0841")
UNDECIDED_CANDIDATE = "cand-0838"
KU_ID = "units/terms/artistic-commission-contracts"
CARD_REL = "04-knowledge/units/terms/artistic-commission-contracts.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "艺术委托合同"
NAME_EN = "Artistic Commission Contracts"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CHP1_FILE = "02-sources/02-Markdown/01_CHP-1_sec_ii.md"
CHP9_FILE = "02-sources/02-Markdown/09_CHP-9_intro.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/C.csv"
QUOTES = {
    "scope": "Whether or not an actual contract was drawn up between him and the patron would depend on the scope of the commission,",
    "subject": "Usually the outlines of the subject would be indicated, and it was then left to the artist to add to it those elements which he found necessary for its representation.",
    "time": "After the size of the picture and the subject-matter had been decided, there came the question of the time limit, a problem of particular urgency",
    "price": "The final clause in any contract naturally referred to the price and financial arrangements.",
    "variation": "And, of course, there were many variations possible in this treatment.",
    "secular_contracts": "The almost complete absence of contracts for secular decorations in eighteenth-century Venice makes it difficult to decide how much choice of subject was left to the artist.",
}
PRICE_STATEMENT = "st-chp1-secii-l73-77-01"
SEcular_CAVEAT_STATEMENT = "st-chp9-p255-contracts-and-consultation-limits"


def make_card() -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, index, s.v. Contracts and subentries price, subject, and time limit.",
            "location": "书后索引，C.csv#367、#369–371；measurements of works 子目 C.csv#368 未纳入本卡。",
            "sentence_summary": "索引主项 Contracts 指向多章讨论；price、subject、time limit 子目指向相应合同条款讨论。",
            "original_quotes": [
                {"source_span": "C.csv#367", "text": "Contracts"},
                {"source_span": "C.csv#369", "text": "price"},
                {"source_span": "C.csv#370", "text": "subject"},
                {"source_span": "C.csv#371", "text": "time limit"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters-index",
                "source_file": INDEX_FILE,
                "source_span": "C.csv#367, #369–371",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 1, pp. 8–9.",
            "location": "第一章第二节，印刷页8–9；分节文件 lines 23, 29。",
            "sentence_summary": "是否订立实际合同取决于委托范围；题材常先给出提纲，具体表达可留给画家。",
            "original_quotes": [
                {"source_span": "line 23; print p. 8", "text": QUOTES["scope"]},
                {"source_span": "line 29; print p. 9", "text": QUOTES["subject"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP1_FILE,
                "source_span": "lines 23, 29; print pp. 8–9",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 1, p. 12.",
            "location": "第一章第二节，印刷页12；分节文件 line 65。",
            "sentence_summary": "尺寸和题材确定后，工期成为需要考虑的委托条件。",
            "original_quotes": [
                {"source_span": "line 65; print p. 12", "text": QUOTES["time"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP1_FILE,
                "source_span": "line 65; print p. 12",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 1, p. 13.",
            "location": "第一章第二节，印刷页13；分节文件 line 74。",
            "sentence_summary": "合同条款涉及价款和付款安排，具体做法存在变化。",
            "original_quotes": [
                {"source_span": "line 74; print p. 13", "text": QUOTES["price"]},
                {"source_span": "line 74; print p. 13", "text": QUOTES["variation"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP1_FILE,
                "source_span": "line 74; print p. 13",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 9, p. 255, n. 1.",
            "location": "第九章，印刷页255注1；OCR L370。",
            "sentence_summary": "哈斯克尔指出，威尼斯世俗装饰合同几乎没有存世，因而难以判定题材选择权的分配。",
            "original_quotes": [
                {"source_span": "line 370; print p. 255 n. 1", "text": QUOTES["secular_contracts"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP9_FILE,
                "source_span": "line 370; print p. 255 n. 1",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
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

### 名称

- 索引英文名称 / Indexed English name：Contracts（第1章书后索引；S3 候选组 sg3-term-contracts）。
- 中文描述名 / Chinese descriptive name：艺术委托合同（工作译名；据索引名称及本书语境拟定，不是原始文书题名）。

### 基本信息

**定义：** 本书索引“Contracts”所指的艺术委托合同概念，涉及画家承接委托时约定的条件。哈斯克尔讨论题材、工期、价款等事项，并指出是否订立实际合同取决于委托范围；条款和付款做法因项目而异。[S1–S4]

**适用范围：** 本书对委托合同及合同条件的概括性讨论，包括索引子目“subject”“time limit”“price”。[S1–S4]

**边界：** 本术语不指认某一份具体合同文书，也不把书中概述转化为统一法律规则。第9章关于威尼斯世俗装饰合同存世稀少的说明是哈斯克尔对证据状况的判断，限制了对题材选择的推断。[S5]

**English definition:** This unit represents the concept indexed as “Contracts” in the book: contracts and contractual terms arising when painters undertake commissions. Haskell discusses subject, time limits, and price, and says that whether an actual contract was drawn up depended on the scope of the commission; clauses and payment practices varied by project. [S1–S4]

**Scope:** The book’s general discussion of commission contracts and their terms, including the index subentries “subject,” “time limit,” and “price.” [S1–S4]

**Boundary:** The term identifies no single contract document and does not turn Haskell’s account into a uniform legal rule. His Chapter 9 note that few contracts for secular decorations in Venice survive limits what can be inferred about the allocation of subject choice. [S5]

### 书中讨论的条款

- 是否订立实际合同取决于委托范围；合同通常不详尽规定题材处理，画家有时可在提纲基础上补充具体内容。[S2]
- 作品尺寸和题材确定后，工期成为委托条件之一。[S3]
- 合同中的价款和付款安排存在多种做法。[S4]

## 关系与证据

当前没有正式关系。委托合同订立惯例另见[委托合同订立惯例](../procedures/commission-contracting.md)；此链接为阅读入口，不表示已登记正式关系。

### 来源

- S1：书后索引 C.csv#367、#369–371；其中 C.csv#368 子目仍待决。
- S2：第1章 pp. 8–9，`st-chp1-secii-l73-77-01` 及相关 S2 提及。
- S3：第1章 p. 12，工期作为合同条件。
- S4：第1章 p. 13，价款和付款安排；`st-chp1-secii-l73-77-01` 保留为一般性价款陈述，不据此创建正式关系。
- S5：第9章 p. 255 n.1，哈斯克尔关于世俗装饰合同存世情况的说明；不是个别合同记录。
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
    parser = argparse.ArgumentParser(description="Register the Contracts term group in S4.")
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

    assert all(candidate_map[cid].get("suggested_type") == "term" for cid in CANDIDATES)
    assert candidate_map[UNDECIDED_CANDIDATE].get("sub_entry") == "measurements of works"
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)
    for cid in CANDIDATES:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert decisions[UNDECIDED_CANDIDATE].get("decision") == "undecided"
    assert not decisions[UNDECIDED_CANDIDATE].get("ku_id")
    assert all(f"group={GROUP};" in decisions[cid].get("resolution_note", "") for cid in CANDIDATES + (UNDECIDED_CANDIDATE,))
    assert "C.csv#368 p.8; Index locator only" in decisions[UNDECIDED_CANDIDATE]["resolution_note"]
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "term" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English title already exists in manifest"

    source_texts = {
        CHP1_FILE: (ROOT / CHP1_FILE).read_text(encoding="utf-8-sig"),
        CHP9_FILE: (ROOT / CHP9_FILE).read_text(encoding="utf-8-sig"),
        INDEX_FILE: (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig"),
    }
    assert all(term in source_texts[INDEX_FILE] for term in ("Contracts", "measurements of works", "price", "subject", "time limit"))
    assert all(quote in source_texts[CHP1_FILE] for quote in (QUOTES["scope"], QUOTES["subject"], QUOTES["time"], QUOTES["price"], QUOTES["variation"]))
    assert QUOTES["secular_contracts"] in source_texts[CHP9_FILE]
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    price_statement = statements[PRICE_STATEMENT]
    assert price_statement.get("subject_candidate_id") == "cand-0839"
    assert price_statement.get("object_candidate_id") in (None, "")
    assert price_statement["qualifiers"].get("relation_candidate") is True
    caveat = statements[SEcular_CAVEAT_STATEMENT]
    assert caveat.get("object_candidate_id") == "cand-0837"
    assert caveat["qualifiers"].get("relation_candidate") is False

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: new term identity group {GROUP} maps to {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "term",
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

### S4 term：艺术委托合同跨章概念组登记（{DATE}）

按既有 S3 组 {GROUP} 登记四条 `new` 候选：`cand-0837`（C.csv#367，索引主项）、`cand-0839`（C.csv#369，price）、`cand-0840`（C.csv#370，subject）和 `cand-0841`（C.csv#371，time limit），统一映射至[艺术委托合同术语卡](../../../04-knowledge/units/terms/artistic-commission-contracts.md)。第1章 pp.8–9 说明实际合同是否订立取决于委托范围，题材条款可保留画家发挥空间；p.12 讨论工期；p.13 讨论价款及不同付款安排。描述保留个案差异，不将概述表述为统一规则。

同一索引文本组中的 `cand-0838`（C.csv#368，measurements of works，p.8）在 S3 为 `undecided`：现有记录只有索引定位，未有足以确定指涉的关联 S2 提及，因此继续不映射，不并入本卡。现有 procedure KU [委托合同订立惯例](../../../04-knowledge/units/procedures/commission-contracting.md)描述订约实践，类型和职责不同；本次没有将其改写或复制。

`{PRICE_STATEMENT}` 保留为一般性价款陈述，虽带 relation-candidate 标记但没有第二端点，不据此生成正式关系；`{SEcular_CAVEAT_STATEMENT}` 是哈斯克尔的方法性说明，不登记为关系。其他候选关系仍按既有 S6 流程处理；本次未修改 `relations.csv`，未新增 S5 enrichment。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 term：艺术委托合同（{DATE}）\n\n"
        "将 S3 组中四条 new 候选映射至一张 term KU；同组索引子目 cand-0838 因缺少关联 S2 指涉仍为 undecided，未映射。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {', '.join(CANDIDATES)} are the complete new-member set for {GROUP}")
        print(f"preserved {UNDECIDED_CANDIDATE} as undecided with no KU mapping")
        print("verified chapter 1 clauses, chapter 9 evidence caveat, and absence of an exact same-type term KU")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv and enrichment.jsonl unchanged")
        print("planned writes: one bilingual term card, accepted.yml, ku-manifest.csv, four alignment mappings, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Contracts term group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
