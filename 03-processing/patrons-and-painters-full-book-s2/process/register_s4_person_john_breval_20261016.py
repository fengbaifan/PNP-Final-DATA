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

GROUP = "new-person:breval-john-03249744d6"
CANDIDATE_ID = "cand-0451"
ALIGNMENT_ID = "aln-0786"
KU_ID = "units/persons/john-breval"
CARD_REL = "04-knowledge/units/persons/john-breval.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-john-breval-20261016"
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
            "location": "全书索引 B.csv#298；列pp.222、266、301、306、307",
            "sentence_summary": "索引主项为Breval, John，页码覆盖第8至10章中对该姓名的引用和来访者记述。",
            "original_quotes": [{"source_span": "B.csv#298", "text": "Breval, John"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
                "source_span": "B.csv#298",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第8章 p.222；OCR L132–133",
            "sentence_summary": "Haskell称Breval曾到Ferrara观看并评论Castiglione等人的绘画；评论作为Haskell引文出现。",
            "original_quotes": [
                {"source_span": "lines 132–133; print p. 222", "text": "John Breval on a visit to\nFerrara commented on some of these"}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "lines 132–133; print p. 222",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章 pp.263、266；OCR L234–236、304–305",
            "sentence_summary": "Haskell分别引用Breval对Sagredo的来访印象和其版画收藏的评论；注释指向Breval 1738年版第I卷p.230，原书未独立查阅。",
            "original_quotes": [
                {
                    "source_span": "lines 234–236; print p. 263",
                    "text": "could hear of but one remarkable Dilettante, the noble Sagredo",
                },
                {
                    "source_span": "lines 304–305; print p. 266",
                    "text": "John Breval wrote that he ‘is reckoned to have the largest Collection of Prints of any man in Europe’",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "lines 234–236, 304–305; print pp. 263, 266",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.301；OCR L389",
            "sentence_summary": "Haskell将Breval列为Joseph Smith曾接待的英国鉴赏家或艺术家之一。",
            "original_quotes": [
                {
                    "source_span": "line 389; print p. 301",
                    "text": "At one time or another John Breval, Horace Walpole, Richard Wilson, Sir Joshua Reynolds, James Wyatt and Robert Adam were all welcomed by him.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 389; print p. 301",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 pp.306–307；OCR L441、446",
            "sentence_summary": "Haskell称鉴赏家Breval曾参观Smith的收藏并见到一件小雕像；p.306与续页p.307对该像分别出现Aesculapio与Priapus称谓，保留原书差异，不裁定对象身份。",
            "original_quotes": [
                {
                    "source_span": "line 441; print p. 306",
                    "text": "the connoisseur John Breval visited Smith’s collection and was shown a little statuette which represented ‘seemingly an Aesculapio",
                },
                {
                    "source_span": "line 446; print p. 307",
                    "text": "Priapus; with a Pudendum of monstrous proportion’",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "lines 441, 446; print pp. 306–307",
            },
        },
    ]
    frontmatter = {
        "title": "约翰·布雷瓦尔（John Breval）",
        "name_en": "John Breval",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 B.csv#298](../../../02-sources/03-Index/03-2-Index-CSV/B.csv)"
    ch8 = "[第8章 p.222](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L132–133）"
    ch9 = "[第9章 pp.263、266](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L234–236、304–305）"
    ch10a = "[第10章 p.301](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L389）"
    ch10b = "[第10章 pp.306–307](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L441、446）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应全书索引中的 John Breval。第8、9章引用其对绘画、收藏与鉴赏活动的评论；第10章称其为鉴赏家，并记述他曾访问Joseph Smith的收藏。中文展示名为项目工作音译。{idx} {ch8} {ch9} {ch10a} {ch10b}

**English:** This unit corresponds to John Breval in the book index. Chapters 8 and 9 quote his comments on paintings, collections, and connoisseurship; Chapter 10 calls him a connoisseur and records a visit to Joseph Smith’s collection. The Chinese display name is a project working transliteration. {idx} {ch8} {ch9} {ch10a} {ch10b}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | John Breval | S1，B.csv#298 |
| 索引形式 | Breval, John | S1，B.csv#298 |
| 身份 | 鉴赏家 | S2，第10章 p.306 |

### 本书相关语境

第8章以Haskell引述呈现Breval对Ferrara画作的评论；第9章两处引用其对Zaccaria Sagredo及其收藏的评价。Haskell所注Breval 1738年版第I卷p.230未独立查阅。第10章记述Breval访问Smith收藏；p.306称其所见小雕像“seemingly an Aesculapio”，续页p.307又称“Priapus”，这里保留两处书内称谓，不裁定雕像身份。{ch8} {ch9} {ch10a} {ch10b}

Chapter 8 presents Breval’s comments on paintings in Ferrara as quoted by Haskell; Chapter 9 quotes two of his assessments of Zaccaria Sagredo and the collection. The cited 1738 edition of Breval, volume I, p. 230, was not independently consulted. Chapter 10 records his visit to Smith’s collection; p. 306 calls a statuette “seemingly an Aesculapio,” while the continuation on p. 307 calls it “Priapus.” Both labels are retained as they appear in the book, without deciding the object’s identity. {ch8} {ch9} {ch10a} {ch10b}

## 关系与证据

### 身份与外部链接

本卡仅登记书内身份依据；当前没有外部身份链接。

This unit records identity evidence from the book; no external identity link is currently recorded.

### 关系记录

当前没有正式关系记录。书内直接关系候选保留在断言账本中，尚未转为正式关系。

No formal relations are recorded. Direct relation candidates from the book remain in the statement ledger and have not been converted into formal relations.
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the John Breval identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE_ID)
    assert candidate.get("suggested_type") == "person"
    group_rows = [
        row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and f"group={GROUP}" in row.get("resolution_note", "")
    ]
    assert len(group_rows) == 1 and group_rows[0].get("candidate_id") == CANDIDATE_ID
    primary = group_rows[0]
    assert primary.get("alignment_id") == ALIGNMENT_ID and not primary.get("ku_id")
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(
        row.get("type") == "person" and row.get("name_en", "").casefold() == "john breval"
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/B.csv").read_text(encoding="utf-8-sig")
    ch8 = (ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md").read_text(encoding="utf-8-sig")
    ch9 = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    ch10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    assert "Breval, John" in index_text and "222, 266, 301, 306, 307" in index_text
    assert "John Breval on a visit to\nFerrara commented" in ch8
    assert "John Breval wrote that he" in ch9 and "could hear of but one remarkable" in ch9
    assert "John Breval" in ch10 and "seemingly an Aesculapio" in ch10 and "Priapus; with a Pudendum" in ch10

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
    non_relation_statements = [row for row in direct_statements if not row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct_statements) == 9 and len(relation_candidates) == 6 and len(non_relation_statements) == 3

    planned_alignment = [dict(row) for row in alignment]
    mapped = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "约翰·布雷瓦尔",
        "name_en": "John Breval",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 5

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_insert = (
        f"### S4 person：John Breval 跨三章身份组登记（{DATE}）\n\n"
        f"- `cand-0451`（B.csv#298，pp.222、266、301、306、307）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`。既有manifest无同名人物KU；索引全名及第8、9、10章同名锚点相合。新卡仅记录姓名和书内鉴赏家身份，不补外部生平。\n"
        f"- 9条直接S2陈述中6条为关系候选、3条为非关系陈述；6条留待S6逐项审查。第9章引述的Breval 1738年版未独立查阅；第10章小雕像在p.306与p.307的称谓差异保留，未裁定对象身份。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：John Breval 跨三章身份组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-0451`（B.csv#298）保持S3组 `{GROUP}`，映射至 `{KU_ID}`。索引列pp.222、266、301、306、307；第8、9、10章均以John Breval全名锚定同一书内人物。无既有人物KU命中，未访问外部身份源。\n"
        "- 卡片只收录全名、索引形式与第10章明确称作connoisseur的书内身份。第8章Ferrara绘画评论、第9章对Sagredo及其收藏的引语，以及第10章Smith访客记述留作书内语境。Breval 1738年卷I p.230仅见Haskell转引，未独立查阅。\n"
        "- 9条直接S2 statements中6条为relation_candidate，另3条记录嵌套引文或评价语境，不构成独立正式关系。p.306将小雕像称作‘seemingly an Aesculapio’，p.307续文称‘Priapus’；差异保留，未新建或裁定该对象。6条关系候选留待S6；本轮不修改 `relations.csv`。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录，来源数不变、unverified保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。\n"
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
                backup.write_text("NEW FILE: created by S4 John Breval registration\n", encoding="utf-8")
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
