from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
CANDIDATE = "cand-4577"
GROUP = "archive-group-4f5f75670a57"
KU_ID = "units/archives/claude-lorrain-paintings-1961"
CARD_REL = "04-knowledge/units/archives/claude-lorrain-paintings-1961.md"
CARD_PATH = ROOT / CARD_REL
ANCHOR = "s4-archive-rothlisberger-claude-lorrain-paintings-1961-20261017"
INHA_URL = "https://agorha.inha.fr/ark:/54721/6ca774b1-afc0-47eb-ac34-561be13db605"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
        "location": "第2章注，OCR L190",
        "span": "OCR line 190",
        "quote": "for the complété list see Rothlisberger, 1961, p. 153.",
        "summary": "Haskell以第153页作为Claude作品完整目录的引文定位；未独立查阅该页。",
    },
    {
        "file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
        "location": "第2章注4，OCR L217、L243",
        "span": "OCR lines 217 and 243",
        "quote": "see Rothlisberger, 1961, p. 121.",
        "summary": "Haskell以第121页定位所述作品分布；未独立查阅该页。",
    },
    {
        "file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
        "location": "第2章注，OCR L243",
        "span": "OCR line 243",
        "quote": "For Claude’s will see Rothlisberger, 1961, p. 67.",
        "summary": "Haskell引用第67页，并以ibid.指向第127页；这里只记录书目定位。",
    },
    {
        "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "location": "第4章注5，印刷页118；OCR L307",
        "span": "OCR line 307; printed page 118",
        "quote": "Rothlisberger, 1961, pp. 428 and 433.",
        "summary": "第4章注5引同一1961年出版物第428、433页；未独立查阅。",
    },
    {
        "file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
        "location": "第6章注1，OCR L156",
        "span": "OCR line 156",
        "quote": "For Lorenzo Onofrio and Claude I have closely followed Rothlisberger, 1961, p. 374,",
        "summary": "Haskell说明本段叙述所据的第374页；该引文仅支持出版物身份与定位。",
    },
    {
        "file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
        "location": "第6章第5节注1，OCR L48",
        "span": "OCR line 48",
        "quote": "Rothlisberger, s, p. 369.",
        "summary": "OCR记载Rothlisberger第369页；原文拼写/扫描差异保留在S2记录中。",
    },
    {
        "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "location": "第7章注4，印刷页172；OCR L305",
        "span": "OCR line 305; printed page 172",
        "quote": "4 Röthlisberger, 1961,1, pp. 15 5-60;",
        "summary": "第7章明确标注卷I并引第155–160页；OCR间隔照录，不据此断言其他未标卷引文的分卷。",
    },
    {
        "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "location": "第7章注8，印刷页182；OCR L347",
        "span": "OCR line 347; printed page 182",
        "quote": "8 Rothlisberger, 1961,1, p. 274,",
        "summary": "第7章明确标注卷I第274页；注中转述的内容未在本任务独立核查。",
    },
    {
        "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "location": "第21章书目，印刷页436；OCR L1075",
        "span": "OCR line 1075; printed page 436",
        "quote": "Röthlisberger, M.: Claude Lorrain—The Paintings, 2 vols., Yale and London 1961.",
        "summary": "书目给出作者缩写、完整题名、两卷本及Yale and London 1961著录。",
    },
)


def make_sources() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in SOURCES:
        rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    rows.append({
        "citation": f"Institut national d'histoire de l'art (INHA), AGORHA, Claude Lorrain. The paintings. {INHA_URL}. Accessed {DATE}.",
        "location": "AGORHA Identification / Référence complète / Auteurs / Date d’édition",
        "sentence_summary": "INHA著录Marcel Röthlisberger为作者，并给出该书两卷本、New Haven、1961年的完整记录；仅用于身份与书目核对。",
        "original_quotes": [{
            "source_span": "AGORHA record, Identification, lines 33–36 and 45–69",
            "text": "Röthlisberger, Marcel. Claude Lorrain. The paintings, deux volumes, New Haven, 1961.",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": INHA_URL,
            "source_span": "AGORHA record, Identification, lines 33–36 and 45–69",
        },
    })
    return rows


def card_text() -> str:
    source_links = [
        "[第2章 p.153定位](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md#L190)",
        "[第2章 p.121及p.67、p.127定位](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md#L217)",
        "[第4章 pp.428、433定位](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md#L307)",
        "[第6章 p.374定位](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md#L156)",
        "[第6章 p.369定位](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md#L48)",
        "[第7章卷I pp.155–160及p.274定位](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md#L305)",
        "[第21章书目 p.436](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L1075)",
    ]
    links = "；".join(source_links)
    fm = {
        "title": "克劳德·洛兰绘画集（Claude Lorrain—The Paintings, 1961）",
        "name_en": "Claude Lorrain—The Paintings (1961)",
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": make_sources(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    frontmatter = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{frontmatter}---

## 内容

### 描述

**中文：** 本卡登记哈斯克尔第21章书目所列 *Claude Lorrain—The Paintings*（两卷本，Yale and London，1961）。第2、4、6、7章多处引用该书；其中第7章两条注明确标作卷I。INHA AGORHA 将作者全名著录为 Marcel Röthlisberger，并记录两卷本、New Haven、1961年。相关书页和卷册未在本次S4登记中直接查阅；书目身份不核验这些引文所述事实。{links}；[INHA AGORHA书目记录]({INHA_URL})

**English:** This card registers the two-volume *Claude Lorrain—The Paintings* (Yale and London, 1961) listed in Haskell’s chapter 21 bibliography. Chapters 2, 4, 6, and 7 cite the publication; two chapter 7 notes explicitly identify volume I. INHA AGORHA gives Marcel Röthlisberger as author and records a two-volume edition published in New Haven in 1961. The cited pages and volumes were not directly consulted during this S4 registration; bibliographic identity does not verify the claims made through those citations. {links}; [INHA AGORHA bibliographic record]({INHA_URL})

### 书目身份与范围

- **原题名：** *Claude Lorrain—The Paintings*。
- **中文工作名：** 《克劳德·洛兰绘画集》；仅为检索展示名，不声称为正式中译题名。
- **责任者：** 第21章书目作 `Röthlisberger, M.`；INHA记录给出全名 Marcel Röthlisberger。身份依据仅用于补全书目责任者。
- **版本范围：** 本卡对应书目所列1961年两卷本出版物。第7章两处明确标卷I（pp.155–160、p.274）；其他章节引文未逐条标卷，本卡不把未标卷页码强行分配到具体卷册。
- **对象边界：** 这是关于 Claude Lorrain 绘画的书目对象，不是 Claude Lorrain 人物卡，也不代表书中所论单幅绘画的作品身份或归属已获验证。

## 关系与证据

当前没有本任务新增的正式关系。直接 S2 关系候选 `st-chp6-notes-l156-p156-n1-1`、`st-chp6-p162-n1-cite`、`st-chp7-p172-n4-cite-rothlisberger` 与 `st-chp7-p182-n5-cite-rothlisberger` 留待S6复核；其余书目引文只作本卡的身份与定位依据。
"""


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S3-aligned 1961 Röthlisberger Claude Lorrain paintings publication as one S4 archive KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id)
    candidate = candidate_by_id[CANDIDATE]
    decision = decisions[CANDIDATE]
    assert candidate.get("suggested_type") == "archive"
    assert candidate.get("canonical_name") == "Claude Lorrain—The Paintings (M. Röthlisberger, 1961), vol. I"
    assert decision.get("decision") == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == {CANDIDATE}, group_members
    assert not CARD_PATH.exists() and CARD_REL not in ACCEPTED.read_text(encoding="utf-8-sig")
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and row.get("name_en", "").casefold() == "claude lorrain—the paintings (1961)".casefold()
        for row in manifest
    )
    assert any(row.get("type") == "person" and row.get("ku_id") == "units/persons/claude-lorrain" for row in manifest)

    for item in SOURCES:
        source_text = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, item

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    relation_candidates = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert len(direct) == 10 and len(relation_candidates) == 4

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id[CANDIDATE]["ku_id"] = KU_ID
    planned_by_id[CANDIDATE]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    planned_by_id[CANDIDATE]["resolution_note"] += (
        f" S4 registration (2026-10-17): {GROUP} maps to {KU_ID}; one 1961 two-volume book identity, "
        "with volume-I citation locators retained where Haskell explicitly marks them. This does not verify cited page contents or add formal S6 relations."
    )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "克劳德·洛兰绘画集",
        "name_en": "Claude Lorrain—The Paintings (1961)",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    fm = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert fm and isinstance(yaml.safe_load(fm.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_next = result_next.rstrip() + f"""

### S4 archive：Röthlisberger《Claude Lorrain—The Paintings》（{DATE}）

`{CANDIDATE}`（`{GROUP}`）登记为1961年两卷本书目身份，对应[archive KU](../units/archives/claude-lorrain-paintings-1961.md)。第21章书目给出题名、责任者缩写、卷数和出版项；第2、4、6、7章引文与INHA AGORHA记录共同支持书目身份，后者列作者全名Marcel Röthlisberger。只在原文明确标注时记录卷I页码；未标卷的引文不强行分册。10条直接S2陈述中4条关系候选仍待S6；书目登记不验证页内事实。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""

    process_append = f"""

<a id="{ANCHOR}"></a>

### S4 archive：Röthlisberger《Claude Lorrain—The Paintings》（{DATE}）

- `{CANDIDATE}`（`{GROUP}`）登记至[Claude Lorrain绘画集 archive KU](../../../{CARD_REL})。第21章p.436书目列出两卷本 *Claude Lorrain—The Paintings*，Yale and London 1961；第2、4、6、7章的页码引文指向同一书目身份。INHA AGORHA完整著录作者 Marcel Röthlisberger、两卷本与New Haven 1961（{INHA_URL}）。
- 本卡覆盖该两卷本书目身份；第7章两注明确标卷I，其余未标卷的定位不强行分配到具体卷册。已存在的 Claude Lorrain 人物卡不与本书合并；书目身份不验证书中引文内容或具体绘画归属。
- 10条直接S2陈述中4条为关系候选，保留待S6；本次只登记KU，不新增正式关系或S5补足。

This one-member S3 archive group is registered as the bibliographic identity of the 1961 two-volume publication. Haskell’s chapters 2, 4, 6, and 7 cite the same title-year record, and chapter 21 supplies the bibliography entry. INHA AGORHA records Marcel Röthlisberger as author and gives the two-volume New Haven 1961 publication. Volume I is retained only for citations explicitly marked as such in chapter 7. The book remains distinct from the Claude Lorrain person KU. Four direct S2 relation candidates remain pending S6; no formal relation or S5 enrichment was added.

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = PROCESS.read_text(encoding="utf-8-sig").rstrip() + process_append
    accepted_next = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} -> {KU_ID}; group_members={len(group_members)}; direct_statements={len(direct)}; relation_candidates_pending={len(relation_candidates)}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}")
        print("No files changed; no S5 enrichment or S6 formal relation rows will be written.")
        return 0

    CARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    CARD_PATH.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_next, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
