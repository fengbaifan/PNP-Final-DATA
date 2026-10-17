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

GROUP = "new-person:biffi-giambattista-0fc083bcf0"
CANDIDATE_ID = "cand-0373"
ALIGNMENT_ID = "aln-0708"
KU_ID = "units/persons/giambattista-biffi"
CARD_REL = "04-knowledge/units/persons/giambattista-biffi.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-giambattista-biffi-20261016"
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
            "location": "全书索引 B.csv#220；列第9章p.262注、第10章p.328及第14章p.360",
            "sentence_summary": "索引主项为Biffi, Giambattista；页码锚点分布于第9、10、14章。",
            "original_quotes": [{"source_span": "B.csv#220", "text": "Biffi, Giambattista"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
                "source_span": "B.csv#220",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章 p.262 注6；OCR L228–229（页图校读见S2过程记录）",
            "sentence_summary": "Haskell引述Gio. Battista Biffi于1773年对Palazzo Giovanelli所藏绘画的描述；档案手稿及被引库存未独立查阅。",
            "original_quotes": [
                {
                    "source_span": "lines 228–229; print p. 262, note 6",
                    "text": "wrote Gio. Battista Biffi of the Palazzo Giovanelli in 1773",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "lines 228–229; print p. 262, note 6; OCR page marker corrected in S2 record",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.328；OCR L243–244（S2记录校正页标）",
            "sentence_summary": "Haskell称Giambattista Biffi为Beccaria和Verri的朋友，引述其赞扬Zuccarelli的文字及日记中的Rousseau评价；书信、日记及Venturi著作未独立查阅。",
            "original_quotes": [
                {
                    "source_span": "line 243; print p. 328",
                    "text": "Giambattista Biffi, the friend of Beccaria and Verri",
                },
                {
                    "source_span": "lines 243–244; print p. 328",
                    "text": "The greatest genius of the century is dead.... He was my father, my guide, my master, my idol",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "lines 243–244; print p. 328; OCR page marker corrected in S2 record",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章 p.360 注2；OCR L219",
            "sentence_summary": "Haskell转引Biffi于1773年到威尼斯后写下的一段关于Algarotti与Cecilia Emo的评论；该信件仅按Haskell引文记录。",
            "original_quotes": [
                {
                    "source_span": "line 219; print p. 360, note 2",
                    "text": "when Giambattista Biffi came to Venice in 1773 nine years after Algarotti’s death he wrote",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "source_span": "line 219; print p. 360, note 2",
            },
        },
    ]
    frontmatter = {
        "title": "吉安巴蒂斯塔·比菲（Giambattista Biffi）",
        "name_en": "Giambattista Biffi",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 B.csv#220](../../../02-sources/03-Index/03-2-Index-CSV/B.csv)"
    ch9 = "[第9章 p.262 注6](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L228–229；页码校读见S2记录）"
    ch10 = "[第10章 p.328](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L243–244；页标校读见S2记录）"
    ch14 = "[第14章 p.360 注2](../../../02-sources/02-Markdown/14_CHP-14_intro.md)（L219）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应索引中的 Giambattista Biffi。第9章注6写作“Gio. Battista Biffi”，第10、14章正文或注释使用全名“Giambattista Biffi”。中文展示名为项目工作音译。{idx} {ch9} {ch10} {ch14}

**English:** This unit corresponds to Giambattista Biffi in the index. Chapter 9, note 6, gives the form “Gio. Battista Biffi,” while Chapters 10 and 14 use “Giambattista Biffi.” The Chinese display name is a project working transliteration. {idx} {ch9} {ch10} {ch14}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Giambattista Biffi | S2，第10章 p.328 |
| 索引形式 | Biffi, Giambattista | S1，B.csv#220 |
| 引用形式 | Gio. Battista Biffi | S2，第9章 p.262 注6 |

### 本书相关语境

第9章引述其1773年对Palazzo Giovanelli绘画的描述；该页OCR页标“202”经S2页图校读取作印本p.262。第10章的姓名出现于Haskell对其友谊、绘画评论和日记的叙述；OCR页标“28”经S2过程记录校正为p.328。第14章注2再次以全名引用其1773年文字。书信、日记及注释所引文献未独立查阅，相关关系和引述均保持原书归属。{ch9} {ch10} {ch14}

Chapter 9 quotes his 1773 description of the paintings at Palazzo Giovanelli; the S2 page-image check corrected the OCR page marker “202” to printed p. 262. Chapter 10 uses his name in Haskell’s account of friendship, painting criticism, and a diary; the S2 record corrected the OCR page marker “28” to p. 328. Chapter 14, note 2, again cites a 1773 text under his full name. The letters, diary, and works cited in the notes were not independently consulted; related statements remain attributed to the book. {ch9} {ch10} {ch14}

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
    parser = argparse.ArgumentParser(description="Register the Giambattista Biffi identity group in S4.")
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
        row.get("type") == "person" and row.get("name_en", "").casefold() == "giambattista biffi"
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_bytes = (ROOT / "02-sources/03-Index/03-2-Index-CSV/B.csv").read_bytes()
    ch9 = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    ch10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_sec_ii.md").read_text(encoding="utf-8-sig")
    ch14 = (ROOT / "02-sources/02-Markdown/14_CHP-14_intro.md").read_text(encoding="utf-8-sig")
    stages = (PROCESS_DIR / "stages.md").read_text(encoding="utf-8-sig")
    assert b"Biffi, Giambattista" in index_bytes
    assert "Gio. Battista Biffi" in ch9 and "[Page 202]" in ch9
    assert "Giambattista Biffi" in ch10 and "[Page 28]" in ch10
    assert "Giambattista Biffi came to Venice in 1773" in ch14
    assert "OCR页码`[Page 202]`应为印刷p.262" in stages
    assert "OCR页标`[Page 28]`" in stages and "印本为328页" in stages

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
    assert len(direct_statements) == 9 and len(relation_candidates) == 7 and len(non_relation_statements) == 2

    planned_alignment = [dict(row) for row in alignment]
    mapped = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "吉安巴蒂斯塔·比菲",
        "name_en": "Giambattista Biffi",
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
        f"### S4 person：Giambattista Biffi 跨章人物组登记（{DATE}）\n\n"
        f"- `cand-0373`（B.csv#220，pp.262n、328、360）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`。第9章Gio. Battista与第10、14章Giambattista拼写共同支持索引全名；无同名既有person KU，不补外部生平。\n"
        f"- 第9章OCR页标202已由S2对照页图校为p.262，第10章OCR页标28据S2记录校为p.328。9条直接S2陈述中7条为关系候选、2条为非关系记录；7条均留待S6。书信、日记和Venturi转引未独立查阅。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Giambattista Biffi 跨章人物组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-0373`（B.csv#220）保持S3组 `{GROUP}`，登记为 `{KU_ID}`。索引页码涵盖p.262注、p.328和p.360；第9章简写Gio. Battista Biffi，第10、14章写作Giambattista Biffi。全名与拼写变体属于同一索引人物组；既有manifest无同名person KU，未访问外部身份源。\n"
        "- 第9章源文本的OCR页标`[Page 202]`已由p.262页图对校；第10章的`[Page 28]`按S2过程记录校为印本p.328。卡片不改写S0来源。\n"
        "- 卡片仅登记索引/正文名称形式，不扩写书外职业生平。第9章1773年藏画描述、第10章友情陈述、Zuccarelli评价与Rousseau日记引文，以及第14章Biffi对Algarotti与Cecilia Emo的引述，均保留Haskell归属。Haskell引注中的Venturi、Bellori、Lumbroso、Poussin作品、未刊信及日记未独立查阅。\n"
        "- 9条直接S2 statements中7条为relation_candidate、2条为引文定位或日记事件陈述；7条关系候选留待S6。本轮未修改`relations.csv`，不裁决Palazzo Giovanelli所列作者异名。\n"
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
                backup.write_text("NEW FILE: created by S4 Giambattista Biffi registration\n", encoding="utf-8")
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
