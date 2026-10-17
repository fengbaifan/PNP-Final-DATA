from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
import sys
from io import StringIO
from pathlib import Path

import yaml

PROCESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "new-person:jean-mariette-pierre-69263c8b1d"
CANDIDATE_ID = "cand-1547"
ALIGNMENT_ID = "aln-1882"
KU_ID = "units/persons/pierre-jean-mariette"
CARD_REL = "04-knowledge/units/persons/pierre-jean-mariette.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-pierre-jean-mariette-20261016"

BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv_text(fieldnames, rows) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in lines):
        raise ValueError("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "全书索引 M.csv#85；定位第6、10、13–15章相关页段",
            "sentence_summary": "索引以Mariette, Pierre-Jean为主项，列出pp.165、284n、285、331、341、343n、361。",
            "original_quotes": [{"source_span": "M.csv#85", "text": "Mariette, Pierre-Jean"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
                "source_span": "M.csv#85",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第6章 p.165；OCR L39",
            "sentence_summary": "Haskell将一段关于Sebastiano Ricci的传闻归于Mariette，并明确引语以‘j’ai entendu dire’开头；不据此确立引语内容为独立事实。",
            "original_quotes": [{"source_span": "line 39; print p. 165", "text": "j’ai entendu dire"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
                "source_span": "line 39; print p. 165",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.285；OCR L180–181",
            "sentence_summary": "Haskell转述Mariette对被毁壁画的评价；本卡只保留这是作者报告的评论语境。",
            "original_quotes": [{"source_span": "lines 180–181; print p. 285", "text": "Mariette, who strongly condemned, this destruction"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "lines 180–181; print p. 285",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第13章 p.341；OCR L92–93、L225（注3）",
            "sentence_summary": "正文称Zanetti在巴黎遇见Mariette并与之通信；注3称Mariette在其Ahecedario中记述Zanetti，并称Zanetti遗赠一幅Rosalba粉彩画给这位法国鉴赏家。以上均保留为Haskell的书内转述。",
            "original_quotes": [
                {"source_span": "lines 92–93; print p. 341", "text": "Mariette, with whom he corresponded to the end of his life"},
                {"source_span": "line 225; print p. 341 n. 3", "text": "Mariette wrote a charming account of Zanetti in his Ahecedario"},
                {"source_span": "line 225; print p. 341 n. 3", "text": "the French connoisseur"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "source_span": "lines 92–93, 225; print p. 341 and n. 3",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章 p.351；OCR L181，注2",
            "sentence_summary": "脚注引述Algarotti于1751年2月13日致Mariette的信，并说明该信见Opere。",
            "original_quotes": [{"source_span": "line 181; print p. 351 n. 2", "text": "Algarotti’s letter to Mariette of 13 February 1751"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "source_span": "line 181; print p. 351 n. 2",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第15章 p.361；OCR L9、L12",
            "sentence_summary": "脚注列出Mariette于1768年4月15日致Temanza的信并称由Müntz刊布；正文转述Mariette对Zanetti绘画前景的判断。",
            "original_quotes": [
                {"source_span": "line 9; print p. 361 n. 2", "text": "Letter from Mariette to Temanza of 15 April 1768"},
                {"source_span": "line 12; print p. 361", "text": "Mariette wrote that he assumed that his pictures too would soon be leaving Venice"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/15_CHP-15_intro.md",
                "source_span": "lines 9, 12; print p. 361 and n. 2",
            },
        },
    ]
    frontmatter = {
        "title": "皮埃尔-让·马里埃特（Pierre-Jean Mariette）",
        "name_en": "Pierre-Jean Mariette",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 M.csv#85](../../../02-sources/03-Index/03-2-Index-CSV/M.csv)"
    ch6 = "[第6章 p.165](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md)（L39）"
    ch10 = "[第10章 p.285](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L180–181）"
    ch13 = "[第13章 p.341](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L92–93、L225）"
    ch14 = "[第14章 p.351](../../../02-sources/02-Markdown/14_CHP-14_intro.md)（L181）"
    ch15 = "[第15章 p.361](../../../02-sources/02-Markdown/15_CHP-15_intro.md)（L9、L12）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录《赞助人与画家》索引所列的 Pierre-Jean Mariette。正文在第6、10、13–15章以 Mariette 称呼此人；第13章脚注称其为法国鉴赏家。相关段落包含作者转引、嵌套引语和信件书目，本卡只保留可由本书确认的姓名与身份，不扩写未经本书支持的生平。中文显示名为项目工作音译。{idx} {ch6} {ch10} {ch13} {ch14} {ch15}

**English:** This unit records Pierre-Jean Mariette as named in the index of *Patrons and Painters*. The prose refers to him as Mariette across Chapters 6, 10, and 13–15; a Chapter 13 footnote calls him a French connoisseur. The passages include Haskell’s reports, nested quotations, and bibliographic references to letters. This card records only the name and identity supported by the book and adds no unsupported biographical details. The Chinese display name is a project working transliteration. {idx} {ch6} {ch10} {ch13} {ch14} {ch15}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Pierre-Jean Mariette | S1，M.csv#85 |
| 索引形式 | Mariette, Pierre-Jean | S1，M.csv#85 |
| 正文称名 | Mariette | S2，第6、10、13–15章，见本卡sources定位 |
| 身份 | 法国鉴赏家（French connoisseur） | S4，第13章 p.341 注3 |

### 本书相关语境

索引 M.csv#85 列出 pp.165、284n、285、331、341、343n、361。第6章 p.165 将关于 Ricci 的说法作为 Mariette 的传闻转述，原文以 “j’ai entendu dire” 限定；第10章 p.285 转述其对壁画毁坏的评价。第13章 p.341 叙述 Zanetti 与 Mariette 的往来，并在注3提及 Mariette 的 *Ahecedario* 记述；第14章 p.351 脚注列出 Algarotti 1751年致 Mariette 的信；第15章 p.361 脚注列出 Mariette 致 Temanza 的1768年书信。以上书内关系与转引主张仍按原 statement 的证据和限定处理，不在本卡中确立为正式关系，也不视为已独立查阅被引原件。{idx} {ch6} {ch10} {ch13} {ch14} {ch15}

The index entry M.csv#85 lists pp. 165, 284n, 285, 331, 341, 343n, and 361. Chapter 6, p. 165, presents a statement about Ricci as hearsay attributed to Mariette, explicitly qualified by “j’ai entendu dire”; Chapter 10, p. 285, reports his criticism of the destruction of the frescoes. Chapter 13, p. 341, describes Zanetti’s contact with Mariette and note 3 refers to Mariette’s account in the *Ahecedario*. A Chapter 14 footnote lists Algarotti’s 1751 letter to Mariette, and a Chapter 15 note lists Mariette’s 1768 letter to Temanza. These source claims and relations remain within the wording and evidentiary limits of the original statements; this card establishes no formal relation and does not imply independent consultation of cited originals. {idx} {ch6} {ch10} {ch13} {ch14} {ch15}

## 关系与证据

### 关系记录

本轮未新增正式关系。涉及 Zanetti、Ricci、Algarotti、Temanza 及信件的陈述仍留在原 S2 statements，待 S6 逐条审查。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Pierre-Jean Mariette in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next((row for row in candidates if row.get("candidate_id") == CANDIDATE_ID), None)
    assert candidate and candidate.get("suggested_type") == "person"
    primary = next((row for row in alignment if row.get("alignment_id") == ALIGNMENT_ID), None)
    assert primary and primary.get("candidate_id") == CANDIDATE_ID
    assert primary.get("decision") == "new" and not primary.get("ku_id")
    assert GROUP in primary.get("resolution_note", "")
    group_rows = [
        row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and GROUP in row.get("resolution_note", "")
    ]
    assert [row.get("candidate_id") for row in group_rows] == [CANDIDATE_ID]
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(
        row.get("type") == "person" and row.get("name_en") == "Pierre-Jean Mariette"
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_m = (ROOT / "02-sources/03-Index/03-2-Index-CSV/M.csv").read_text(encoding="cp1252")
    assert "Mariette, Pierre-Jean" in index_m
    assert "Algarotti’s letter to Mariette of 13 February 1751" in (ROOT / "02-sources/02-Markdown/14_CHP-14_intro.md").read_text(encoding="utf-8-sig")
    assert "the French connoisseur" in (ROOT / "02-sources/02-Markdown/13_CHP-13_intro.md").read_text(encoding="utf-8-sig")
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID
    ]
    relation_candidates = [
        row for row in direct_statements
        if row.get("qualifiers", {}).get("relation_candidate")
    ]
    assert len(direct_statements) == 10 and len(relation_candidates) == 7

    planned_alignment = [dict(row) for row in alignment]
    mapped = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "皮埃尔-让·马里埃特",
        "name_en": "Pierre-Jean Mariette",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 6

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_insert = (
        f"### S4 person：Pierre-Jean Mariette 跨章候选登记（{DATE}）\n\n"
        f"- `cand-1547`（M.csv#85）→ `{GROUP}` → `{KU_ID}`。新增双语人物卡、manifest、accepted路径；候选决定行映射至该KU。书内索引全名和第13章‘French connoisseur’称谓支持有限身份字段；未增加外部生平或身份标识。\n"
        f"- 该候选在第6、10、13–15章有直接 S2 端点；10条直接陈述中7条为关系候选，均留待S6，另3条为非关系陈述。Haskell所引传闻、信件书目及关系语句按原限定保留；未读原始引文，也未写入正式关系。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组、待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Pierre-Jean Mariette 跨章候选登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-1547`（M.csv#85）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`；没有同名person KU，未把相近姓氏或索引项目并入。新卡只录索引全名、正文称名及Haskell第13章注3所称French connoisseur，不补生卒、籍贯或外部身份。\n"
        "- 身份与跨章语境依据包括第6章p.165的明示传闻引语、第10章p.285对壁画毁坏的评论、第13章p.341正文及注3、第14章p.351注2和第15章p.361正文／注2。后几处的往来、信件及作品评价仍属原书陈述；不据书目引用声称已读原件。\n"
        "- 10条直接S2陈述中7条为关系候选，均留待S6；另3条不标为关系候选。本轮没有新增relations.csv边、archive/work KU或外部身份记录。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。\n"
    )

    outputs = {
        ALIGNMENT: write_csv_text(alignment_fields, planned_alignment),
        MANIFEST: write_csv_text(manifest_fields, planned_manifest),
        ACCEPTED: accepted_text,
        CARD_PATH: card_text,
        PROCESS: process_text,
        RESULT: result_text,
    }
    for path in outputs:
        assert not path.with_name(path.name + BACKUP_SUFFIX).exists()

    if args.dry_run:
        for path, updated in outputs.items():
            current = path.read_text(encoding="utf-8-sig") if path.exists() else ""
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE_ID}->{GROUP}->{KU_ID}; registered="
            f"{totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
            f"direct_statements={len(direct_statements)}; relation_candidates={len(relation_candidates)}"
        )
        return 0

    backups = []
    try:
        for path in outputs:
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if path.exists():
                shutil.copy2(path, backup)
            else:
                backup.write_text("NEW FILE: created by S4 Pierre-Jean Mariette registration\n", encoding="utf-8")
            backups.append((path, backup))
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    except Exception:
        for path, backup in backups:
            if backup.read_text(encoding="utf-8-sig").startswith("NEW FILE:"):
                if path.exists():
                    path.unlink()
            else:
                shutil.copy2(backup, path)
        raise

    print(
        f"applied: {CANDIDATE_ID}->{GROUP}->{KU_ID}; registered={totals['registered_groups']}/"
        f"{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; direct_statements={len(direct_statements)}; "
        f"relation_candidates={len(relation_candidates)}; backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
