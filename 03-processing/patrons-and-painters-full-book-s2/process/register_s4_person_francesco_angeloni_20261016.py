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

GROUP = "new-person:angeloni-francesco-24d9ba915a"
CANDIDATE_ID = "cand-0107"
ALIGNMENT_ID = "aln-0442"
KU_ID = "units/persons/francesco-angeloni"
CARD_REL = "04-knowledge/units/persons/francesco-angeloni.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-francesco-angeloni-20261016"
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
            "location": "全书索引 A.csv#108；列第2章p.53注、第4章p.114及第6章p.158",
            "sentence_summary": "索引主项为Angeloni, Francesco，页码覆盖第2、4、6章的正文及注释锚点。",
            "original_quotes": [{"source_span": "A.csv#108", "text": "Angeloni, Francesco"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
                "source_span": "A.csv#108",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第2章 p.53 注；OCR L230",
            "sentence_summary": "脚注指向一封1640年9月1日致Francesco Angeloni的信，说明书内注释中的全名锚点；Bellori所刊信件未独立查阅。",
            "original_quotes": [
                {"source_span": "line 230; print p. 53, note 2", "text": "See his letter of 1 September 1640 to Francesco Angeloni published by Bellori, p. 358."}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "source_span": "line 230; print p. 53, note 2",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第4章 p.114；OCR L173及注释L291",
            "sentence_summary": "Haskell称Angeloni为考古学者，并列举其奖章收藏与Annibale Carracci素描；注释报告Cassiano、Poussin及其他同时代人曾提及他。",
            "original_quotes": [
                {
                    "source_span": "line 173; print p. 114",
                    "text": "his friend the archaeologist Francesco Angeloni with his large collection of medals and his drawings by Annibale Carracci",
                },
                {
                    "source_span": "line 291; print p. 114, note 1",
                    "text": "There are frequent references to Angeloni by Cassiano himself (Lumbroso, p. 200), Poussin (Correspondance—passim) and other contemporaries.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "source_span": "lines 173, 291; print p. 114",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第6章 p.158；OCR L22–26",
            "sentence_summary": "Haskell称Angeloni为古物学者、收藏家和作家，并在介绍Bellori时称其为监护人；Bellori是其侄子的说法以was said to be限定。",
            "original_quotes": [
                {
                    "source_span": "lines 23–26; print p. 158",
                    "text": "was said to be the nephew of the antiquarian collector and writer\nFrancesco Angeloni who was certainly his guardian",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md",
                "source_span": "lines 22–26; print p. 158",
            },
        },
    ]
    frontmatter = {
        "title": "弗朗切斯科·安杰洛尼（Francesco Angeloni）",
        "name_en": "Francesco Angeloni",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 A.csv#108](../../../02-sources/03-Index/03-2-Index-CSV/A.csv)"
    ch2 = "[第2章 p.53 注](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L230）"
    ch4 = "[第4章 p.114](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L173、291）"
    ch6 = "[第6章 p.158](../../../02-sources/02-Markdown/06_CHP-6_sec_iv.md)（L22–26）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应索引中的 Francesco Angeloni。第4章称其为考古学者；第6章称其为古物学者、收藏家和作家。中文展示名为项目工作音译。{idx} {ch2} {ch4} {ch6}

**English:** This unit corresponds to Francesco Angeloni in the index. Chapter 4 calls him an archaeologist; Chapter 6 describes him as an antiquarian, collector, and writer. The Chinese display name is a project working transliteration. {idx} {ch2} {ch4} {ch6}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Francesco Angeloni | S1，A.csv#108 |
| 索引形式 | Angeloni, Francesco | S1，A.csv#108 |
| 身份 | 考古学者（archaeologist） | S2，第4章 p.114 |
| 身份 | 古物学者（antiquarian） | S2，第6章 p.158 |
| 身份 | 收藏家（collector） | S2，第6章 p.158 |
| 身份 | 作家（writer） | S2，第6章 p.158 |

### 本书相关语境

第4章将Angeloni置于Cassiano dal Pozzo的艺术与学术讨论中，并列其奖章收藏和Annibale Carracci素描；同页注释称同时代人曾多次提及他。第6章介绍其收藏、写作及与Bellori相关的语境；Haskell对Bellori亲缘身份使用“was said to be”的转述限定。本卡不把这些来源陈述提升为已独立核验的关系。{ch4} {ch6}

Chapter 4 places Angeloni in its discussion of Cassiano dal Pozzo’s artistic and scholarly circle and mentions his medal collection and Annibale Carracci drawings; a note on the same page reports that contemporaries often referred to him. Chapter 6 discusses his collecting and writing in connection with Bellori; Haskell qualifies the kinship claim about Bellori with “was said to be.” These source statements are not presented here as independently verified relations. {ch4} {ch6}

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
    parser = argparse.ArgumentParser(description="Register the Francesco Angeloni identity group in S4.")
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
        row.get("type") == "person" and row.get("name_en", "").casefold() == "francesco angeloni"
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_bytes = (ROOT / "02-sources/03-Index/03-2-Index-CSV/A.csv").read_bytes()
    ch2 = (ROOT / "02-sources/02-Markdown/02_CHP-2_sec_iv.md").read_text(encoding="utf-8-sig")
    ch4 = (ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md").read_text(encoding="utf-8-sig")
    ch6 = (ROOT / "02-sources/02-Markdown/06_CHP-6_sec_iv.md").read_text(encoding="utf-8-sig")
    assert b"Angeloni, Francesco" in index_bytes
    assert "letter of 1 September 1640 to Francesco Angeloni" in ch2
    assert "his friend the archaeologist Francesco Angeloni" in ch4
    assert "frequent references to Angeloni by Cassiano himself" in ch4
    assert "was said to be the nephew of the antiquarian collector and writer" in ch6

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
    assert len(direct_statements) == 9 and len(relation_candidates) == 8 and len(non_relation_statements) == 1

    planned_alignment = [dict(row) for row in alignment]
    mapped = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "弗朗切斯科·安杰洛尼",
        "name_en": "Francesco Angeloni",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 4

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_insert = (
        f"### S4 person：Francesco Angeloni 跨章人物组登记（{DATE}）\n\n"
        f"- `cand-0107`（A.csv#108，pp.53n、114、158）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`；既有manifest无同名人物KU。卡片登记姓名及书内明确称为考古学者、古物学者、收藏家和作家的身份，不补外部生平。\n"
        f"- 9条直接S2陈述中8条为关系候选、1条为非关系评价；8条关系候选留待S6。Bellori为其侄子的表述保留‘was said to be’限定，Cassiano、Poussin、Carracci图像相关主张仍以Haskell文本为依据；所引文献未独立查阅。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增6条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Francesco Angeloni 跨章人物组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-0107`（A.csv#108）保持S3组 `{GROUP}`，登记为 `{KU_ID}`。第2章p.53注、第4章p.114和第6章p.158的全名锚点与索引范围相合；无既有人物KU命中，未访问外部身份源。\n"
        "- 卡片字段限于全名、索引形式及Haskell明确提供的身份称谓：archaeologist、antiquarian、collector、writer。Bellori被称作Angeloni侄子的表述为‘was said to be’，只保留报告性主张；监护关系、朋友关系、勋章收藏、Carracci素描所有权和同时代人提及频率均按原S2 qualifiers 保留，不写入正式关系。\n"
        "- 9条直接S2 statements中8条为relation_candidate、1条为作者评价。Cassiano、Poussin、其他同时代人的引述及Bellori关系均未据书内书目提升为外部核验。8条关系候选留待S6，本轮不修改 `relations.csv`。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增6条source-backed字段记录，来源数不变、unverified保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。\n"
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
                backup.write_text("NEW FILE: created by S4 Francesco Angeloni registration\n", encoding="utf-8")
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
