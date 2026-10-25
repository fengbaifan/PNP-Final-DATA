#!/usr/bin/env python3
"""Guarded registration of the Bjurström 1961 citation and author endpoints."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
TASK = "patrons-and-painters-full-book-s2"
ANCHOR = "s4-s5-s6-chp7-p182-bjurstrom-torelli-1961-20261025"
RECOVERY_REL = "06-runtime/recovery/s4-s5-s6-chp7-bjurstrom-1961-20261025"

ARCHIVE_CANDIDATE = "cand-7075"
ARCHIVE_ALIGNMENT = "aln-7251"
ARCHIVE_GROUP = "archive-group-63cebb2e5e5a"
ARCHIVE_KU = "units/archives/giacomo-torelli-baroque-stage-design-1961"
ARCHIVE_CARD = "04-knowledge/units/archives/giacomo-torelli-baroque-stage-design-1961.md"
ARCHIVE_TITLE = "《贾科莫·托雷利与巴洛克舞台设计》（Giacomo Torelli and Baroque Stage Design）"
ARCHIVE_NAME_EN = "Giacomo Torelli and Baroque Stage Design"

PERSON_CANDIDATE = "cand-7076"
PERSON_ALIGNMENT = "aln-7252"
PERSON_GROUP = "new-person:bjurstrom-per-cf789b97bb"
PERSON_KU = "units/persons/per-bjurstrom"
PERSON_CARD = "04-knowledge/units/persons/per-bjurstrom.md"
PERSON_TITLE = "佩尔·比尤尔斯特伦（Per Bjurström）"
PERSON_NAME_EN = "Per Bjurström"

SOURCE_BOOK_KU = "units/archives/patrons-and-painters"
S6_STATEMENT = "st-chp7-p182-n1-cite-bjurstrom"
BIBLIOGRAPHY_STATEMENT = "st-chp21-bib-l165-205-entry-11"
SOURCE_ID = "haskell-1980-rev-ed"
EXPECTED_CLAIM = (
    "Haskell’s book cites Giacomo Torelli and Baroque Stage Design "
    "(Per Bjurström, Stockholm 1961) at Bjurström, Giacomo Torelli and "
    "Baroque Stage Design (1961) in footnote 1. The prior note records: "
    "Footnote 1 also cites Bjurström’s 1961 Giacomo Torelli and Baroque Stage Design."
)
REPLACEMENT_CLAIM = "Haskell’s footnote 1 cites Bjurström, 1961."

EXPECTED_HASHES = {
    "04-knowledge/tables/alignment.csv": "5c5bdcb2afcc779327c783676bafcac53c29942bca89cc4305d5933517cc61a6",
    "04-knowledge/tables/ku-manifest.csv": "ddae64309f515346f8e93780c9baa8241d893616478d6ea03a01d4e592505073",
    "04-knowledge/tables/relations.csv": "e2231de119cbcfd0bb8d1d1dc67961eeaf435ee9e617af4d42b6935c4b66d709",
    "04-knowledge/accepted.yml": "568422fcdcd97b8f7ce7c8fbfb62243e416816bf80e255d9f261f3c306a21f7e",
    "04-knowledge/tables/book-statements.jsonl": "41dcfdeddbed5e33316c72fc48f4bc8a3a57f012ae41a374a4b5eb2e7ca640bd",
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md": "c98e6f02d2e26b85c8f62bd7ccb8ae4d562ba65a934150e451abed55f6ca7150",
    "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    "02-sources/02-Markdown/21_CHP-21Bibliography.md": "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3",
}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    if not reader.fieldnames:
        raise SystemExit(f"missing CSV header: {path}")
    return list(reader.fieldnames), list(reader), bom, newline


def write_csv(headers, rows, bom: bool, newline: str) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as f:
        temporary = Path(f.name)
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)


def next_relation_ids(rows) -> tuple[str, str]:
    last = max(
        (int(r["relation_id"][4:]) for r in rows
         if r.get("relation_id", "").startswith("rel-") and r["relation_id"][4:].isdigit()),
        default=0,
    )
    return f"rel-{last + 1:04d}", f"rel-{last + 2:04d}"


def archive_card() -> str:
    return f'''---
title: "{ARCHIVE_TITLE}"
name_en: "{ARCHIVE_NAME_EN}"
type: archive
sub_type: book
created: '2026-10-25'
updated: '2026-10-25'
evidence_status: source_backed
sources:
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第7章，印刷页182注1，Markdown L343；CHP-7.pdf物理页16。'
    sentence_summary: '注1列出Bjurström, 1961，作为本段关于Giacomo Torelli的书目引注；所引专著未独立查阅。'
    original_quotes:
      - source_span: 'line 343; printed p. 182, note 1; CHP-7.pdf physical page 16'
        text: '1 Prunières, 1913, p. 68; Bjurström, 1961.'
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/07_CHP-7_sec_i.md
      source_span: 'line 343; printed p. 182, note 1; CHP-7.pdf physical page 16'
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第21章书目，印刷页415，Markdown L183；CHP-21Bibliography.pdf物理页5。'
    sentence_summary: '书目以Bjurström, Per署名专著，列出原题、Stockholm及1961年；页图核对该项。'
    original_quotes:
      - source_span: 'line 183; printed p. 415; CHP-21Bibliography.pdf physical page 5'
        text: 'Bjurström, Per: Giacomo Torelli and Baroque Stage Design, Stockholm 1961.'
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/21_CHP-21Bibliography.md
      source_span: 'line 183; printed p. 415; CHP-21Bibliography.pdf physical page 5'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}
---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第21章书目所列 Per Bjurström 的专著 *Giacomo Torelli and Baroque Stage Design*（Stockholm，1961）。第7章印刷页182注1将“Bjurström, 1961”作为该段有关Giacomo Torelli的引注。本卡只表示这条书目记录；专著及被引内容未由本项目独立查阅。中文题名为描述性工作译名。

**English:** This card records Per Bjurström’s monograph *Giacomo Torelli and Baroque Stage Design* (Stockholm, 1961), listed in Haskell’s Chapter 21 bibliography. Chapter 7, printed page 182, note 1 cites “Bjurström, 1961” in the passage on Giacomo Torelli. This unit represents the bibliographic record only; neither the monograph nor its cited contents was independently consulted. The Chinese display title is a descriptive working translation.

### 文献身份与定位

| 字段 | 内容 | 依据 |
|---|---|---|
| 文献类型 | 学术文献／专著；按书目所列书籍记录 | S2；第21章书目 p.415，L183；页图核对 |
| 书内责任者形式 | Bjurström, Per | S2；第21章书目 p.415，L183；页图核对 |
| 原题名 | Giacomo Torelli and Baroque Stage Design | S2；第21章书目 p.415，L183；页图核对 |
| 出版地 | Stockholm | S2；第21章书目 p.415，L183；页图核对 |
| 出版年 | 1961 | S2；第21章书目 p.415，L183；页图核对 |

## 关系与证据

### 身份与外部链接

S3身份组 `{ARCHIVE_GROUP}` 的 `new` 候选 `{ARCHIVE_CANDIDATE}` 映射至本KU。该组表示书目所列的1961年专著，不表示查阅该书或其被引内容。书内作者形式与人物KU [{PERSON_TITLE}](../persons/per-bjurstrom.md)相连。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
'''


def person_card() -> str:
    return f'''---
title: "{PERSON_TITLE}"
name_en: "{PERSON_NAME_EN}"
type: person
created: '2026-10-25'
updated: '2026-10-25'
evidence_status: source_backed
sources:
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第21章书目，印刷页415，Markdown L183；CHP-21Bibliography.pdf物理页5。'
    sentence_summary: '书目将Bjurström, Per列为1961年专著作者；页图核对书内姓名形式。该来源不支持传记信息。'
    original_quotes:
      - source_span: 'line 183; printed p. 415; CHP-21Bibliography.pdf physical page 5'
        text: 'Bjurström, Per: Giacomo Torelli and Baroque Stage Design, Stockholm 1961.'
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/21_CHP-21Bibliography.md
      source_span: 'line 183; printed p. 415; CHP-21Bibliography.pdf physical page 5'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}
---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔书目所列作者形式“Bjurström, Per”，按正序呈现为 Per Bjurström。书目将其署名于1961年专著 *Giacomo Torelli and Baroque Stage Design*。第7章以“Bjurström, 1961”引注该书；第10及第20章的姓氏形式已在S3跨章身份组内对齐至此姓名。本卡仅表达书内姓名与书目作者角色，不补写生卒、国籍或传记。中文姓名为工作音译。

**English:** This card records the author form “Bjurström, Per” in Haskell’s bibliography, rendered in direct order as Per Bjurström. The bibliography credits him with the 1961 monograph *Giacomo Torelli and Baroque Stage Design*. Chapter 7 cites “Bjurström, 1961”; surname-only forms in Chapters 10 and 20 are aligned to this name within the S3 cross-chapter identity group. This card records only the in-book name and bibliographic author role; it adds no dates, nationality, or biography.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 书内责任者姓名形式 | Per Bjurström（书目倒置形式：Bjurström, Per） | S1；第21章书目 p.415，L183；页图核对 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
'''


def insert_accepted(text: str, card_paths: list[str]) -> str:
    lines = text.splitlines()
    for card_path in card_paths:
        if any(line.strip() == f"- {card_path}" for line in lines):
            raise SystemExit(f"accepted.yml already contains {card_path}")
    for card_path in card_paths:
        candidates = [i for i, line in enumerate(lines)
                      if line.startswith("- 04-knowledge/units/") and line[2:] > card_path]
        at = candidates[0] if candidates else next((i for i, line in enumerate(lines) if line == "claims:"), len(lines))
        lines.insert(at, f"- {card_path}")
    return "\n".join(lines) + "\n"


def validate_and_plan():
    for rel, expected in EXPECTED_HASHES.items():
        path = ROOT / rel
        if not path.exists() or sha(path.read_bytes()) != expected:
            raise SystemExit(f"baseline changed; refusing to apply: {rel}")

    _, candidates, _, _ = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row.get("candidate_id"): row for row in candidates}
    archive_candidate = candidate_by_id.get(ARCHIVE_CANDIDATE)
    person_candidate = candidate_by_id.get(PERSON_CANDIDATE)
    if not archive_candidate or archive_candidate.get("suggested_type") != "archive":
        raise SystemExit("Bjurström monograph candidate is missing or no longer an archive")
    if "Giacomo Torelli and Baroque Stage Design" not in archive_candidate.get("canonical_name", ""):
        raise SystemExit("archive candidate title changed")
    if not person_candidate or person_candidate.get("suggested_type") != "person":
        raise SystemExit("Per Bjurström person candidate is missing or no longer a person")
    if person_candidate.get("canonical_name") != "Per Bjurström":
        raise SystemExit("person candidate name changed")

    align_path = TABLES / "alignment.csv"
    align_fields, alignments, align_bom, align_nl = read_csv(align_path)
    alignment_targets = {}
    for candidate_id, alignment_id, group in (
        (ARCHIVE_CANDIDATE, ARCHIVE_ALIGNMENT, ARCHIVE_GROUP),
        (PERSON_CANDIDATE, PERSON_ALIGNMENT, PERSON_GROUP),
    ):
        target_rows = [row for row in alignments if row.get("candidate_id") == candidate_id]
        if len(target_rows) != 1:
            raise SystemExit(f"expected one alignment row for {candidate_id}; got {len(target_rows)}")
        target = target_rows[0]
        if target.get("alignment_id") != alignment_id or target.get("decision") != "new" or target.get("ku_id"):
            raise SystemExit(f"expected an unmapped S3 new decision for {candidate_id}")
        if f"group={group}" not in target.get("resolution_note", ""):
            raise SystemExit(f"S3 identity group missing for {candidate_id}")
        group_members = {row["candidate_id"] for row in alignments
                         if row.get("decision") == "new" and f"group={group}" in row.get("resolution_note", "")}
        if group_members != {candidate_id}:
            raise SystemExit(f"unexpected S3 group membership for {candidate_id}: {sorted(group_members)}")
        alignment_targets[candidate_id] = target

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest, manifest_bom, manifest_nl = read_csv(manifest_path)
    for ku_id, card_path in ((ARCHIVE_KU, ARCHIVE_CARD), (PERSON_KU, PERSON_CARD)):
        if any(row.get("ku_id") == ku_id or row.get("card_path") == card_path for row in manifest):
            raise SystemExit(f"target KU already registered: {ku_id}")
        if (ROOT / card_path).exists():
            raise SystemExit(f"target card already exists: {card_path}")
    if any(row.get("name_en", "").casefold() == ARCHIVE_NAME_EN.casefold()
           for row in manifest if row.get("type") == "archive"):
        raise SystemExit("a matching archive English title already exists")
    if any(row.get("name_en", "").casefold() == PERSON_NAME_EN.casefold()
           for row in manifest if row.get("type") == "person"):
        raise SystemExit("a matching person English name already exists")
    if not any(row.get("ku_id") == SOURCE_BOOK_KU and row.get("type") == "archive" for row in manifest):
        raise SystemExit("the citing book KU is missing")

    source_rows = [row for row in read_csv(TABLES / "sources.csv")[1] if row.get("source_id") == SOURCE_ID]
    if len(source_rows) != 1:
        raise SystemExit("Haskell source registry entry is missing or duplicated")

    statements_path = TABLES / "book-statements.jsonl"
    statement_lines = statements_path.read_text(encoding="utf-8-sig").splitlines()
    statements = [json.loads(line) for line in statement_lines]
    targets = [s for s in statements if s.get("statement_id") == S6_STATEMENT]
    bib_targets = [s for s in statements if s.get("statement_id") == BIBLIOGRAPHY_STATEMENT]
    if len(targets) != 1 or len(bib_targets) != 1:
        raise SystemExit("expected one citation statement and one bibliography statement")
    statement = targets[0]
    if (statement.get("predicate") != "cites" or statement.get("subject_candidate_id") != "cand-2962"
            or statement.get("object_candidate_id") != ARCHIVE_CANDIDATE
            or (statement.get("qualifiers") or {}).get("relation_candidate") is not True):
        raise SystemExit("the chapter 7 citation candidate changed")
    if (statement.get("qualifiers") or {}).get("claim") != EXPECTED_CLAIM:
        raise SystemExit("the citation statement claim changed; review before applying")
    bibliography = bib_targets[0]
    bibliographic_record = (bibliography.get("qualifiers") or {}).get("bibliographic_record") or {}
    if (bibliography.get("object_candidate_id") != ARCHIVE_CANDIDATE
            or bibliographic_record.get("printed_page") != 415
            or bibliographic_record.get("author_as_printed") != "Bjurström, Per"
            or bibliographic_record.get("publication_details_as_printed") != "Stockholm, 1961"):
        raise SystemExit("the chapter 21 bibliographic identity record changed")

    relation_path = TABLES / "relations.csv"
    relation_fields, relations, relation_bom, relation_nl = read_csv(relation_path)
    existing_pairs = {(row.get("subject_ku_id"), row.get("predicate"), row.get("object_ku_id"))
                      for row in relations}
    if ((SOURCE_BOOK_KU, "cites", ARCHIVE_KU) in existing_pairs
            or (ARCHIVE_KU, "authored_by", PERSON_KU) in existing_pairs):
        raise SystemExit("a target relation already exists")
    cite_id, author_id = next_relation_ids(relations)
    if any(row.get("relation_id") in {cite_id, author_id} for row in relations):
        raise SystemExit("allocated relation IDs already exist")

    new_manifest = list(manifest) + [
        {"ku_id": ARCHIVE_KU, "type": "archive", "canonical_name": ARCHIVE_TITLE,
         "name_en": ARCHIVE_NAME_EN, "source_task": TASK, "card_path": ARCHIVE_CARD},
        {"ku_id": PERSON_KU, "type": "person", "canonical_name": PERSON_TITLE,
         "name_en": PERSON_NAME_EN, "source_task": TASK, "card_path": PERSON_CARD},
    ]
    new_relations = list(relations) + [
        {
            "relation_id": cite_id, "subject_ku_id": SOURCE_BOOK_KU, "object_ku_id": ARCHIVE_KU,
            "predicate": "cites", "time": "", "role": "第7章脚注书目引文",
            "scope": "Haskell第7章印刷页182注1引“Bjurström, 1961”；第21章p.415书目以“Bjurström, Per”著录《Giacomo Torelli and Baroque Stage Design》，列Stockholm及1961年。仅记录书内引注，不表示项目查阅被引专著或其内容。",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID,
            "source_span": "Chapter 7, printed p.182, note 1, L343; statement=st-chp7-p182-n1-cite-bjurstrom; bibliography: Chapter 21, printed p.415, L183",
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "note": "The printed note cites ‘Bjurström, 1961’; the bibliography identifies the book and its publication details. The cited monograph and its contents were not independently consulted.",
        },
        {
            "relation_id": author_id, "subject_ku_id": ARCHIVE_KU, "object_ku_id": PERSON_KU,
            "predicate": "authored_by", "time": "1961", "role": "书目责任者归属",
            "scope": "Haskell第21章印刷页415书目以“Bjurström, Per”著录《Giacomo Torelli and Baroque Stage Design》（Stockholm，1961）。本边记录书内书目责任者归属，不声称独立核验作者身份或专著内容。",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID,
            "source_span": "Chapter 21, printed p.415, L183; statement=st-chp21-bib-l165-205-entry-11",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
            "note": "Bibliographic authorship is structural and is not an S2 relation-candidate adjudication.",
        },
    ]

    alignments = [dict(row) for row in alignments]
    for candidate_id, ku_id, group, note in (
        (ARCHIVE_CANDIDATE, ARCHIVE_KU, ARCHIVE_GROUP,
         " S4 registration: mapped the 1961 monograph group to this archive KU; Chapter 7 p.182 note 1 and Chapter 21 p.415 bibliography identify the same cited book."),
        (PERSON_CANDIDATE, PERSON_KU, PERSON_GROUP,
         " S4 registration: mapped the Per Bjurström cross-chapter person group to this source-limited person KU; the Chapter 21 p.415 bibliography gives the full author form."),
    ):
        target = next(row for row in alignments if row.get("candidate_id") == candidate_id)
        target["ku_id"] = ku_id
        target["resolution_note"] += note

    statement["qualifiers"]["claim"] = REPLACEMENT_CLAIM
    statements_bytes = ("\n".join(json.dumps(item, ensure_ascii=False) for item in statements) + "\n").encode("utf-8")
    original_statements_raw = statements_path.read_bytes()
    if original_statements_raw.startswith(b"\xef\xbb\xbf"):
        statements_bytes = b"\xef\xbb\xbf" + statements_bytes

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_raw = accepted_path.read_bytes()
    accepted_bom = accepted_raw.startswith(b"\xef\xbb\xbf")
    accepted_nl = "\r\n" if b"\r\n" in accepted_raw else "\n"
    accepted_text = accepted_raw.decode("utf-8-sig")
    accepted_text = insert_accepted(accepted_text, [ARCHIVE_CARD, PERSON_CARD])
    accepted_bytes = accepted_text.replace("\n", accepted_nl).encode("utf-8")
    if accepted_bom:
        accepted_bytes = b"\xef\xbb\xbf" + accepted_bytes

    process_path = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
    process_raw = process_path.read_bytes()
    process_bom = process_raw.startswith(b"\xef\xbb\xbf")
    process_nl = "\r\n" if b"\r\n" in process_raw else "\n"
    process_text = process_raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if f'<a id="{ANCHOR}"></a>' in process_text:
        raise SystemExit("process anchor already exists")
    if not process_text.endswith("\n"):
        process_text += "\n"
    process_text += f'''

<a id="{ANCHOR}"></a>

### S4–S5–S6：第7章 Bjurström《Giacomo Torelli and Baroque Stage Design》（1961）（2026-10-25）

**证据与跨章身份。** `cand-7075`沿用S3身份组`{ARCHIVE_GROUP}`的`new`决定（`{ARCHIVE_ALIGNMENT}`）。第7章印刷页182注1（`CHP-7.pdf`物理页16；Markdown L343）扫描页读作“Bjurström, 1961”；第21章印刷页415书目（`CHP-21Bibliography.pdf`物理页5；L183）扫描页读作“Bjurström, Per: Giacomo Torelli and Baroque Stage Design, Stockholm 1961.” 两处支持同一专著的书目身份；专著与被引内容均未独立查阅。`cand-7076`沿用`{PERSON_GROUP}`的person `new`身份组（`{PERSON_ALIGNMENT}`）；依据完整书目责任者形式以及S3已核定的章7、章10、章20姓氏引注对应，限定为书内人名，不补传记或外部身份。

**S4登记。** 专著候选映射至`{ARCHIVE_KU}`；Per Bjurström人物候选映射至`{PERSON_KU}`。均按现有S3分组执行，不变更身份决定。两卡登记至accepted与manifest。

**S5字段。** 专著新增5条`source_backed`书目字段：文献类型、责任者形式、原题名、出版地、出版年；人物卡新增1条书内责任者姓名形式。中文书名与姓名为工作译名／音译，不据此声称官方译名。书目没有出版者或内容摘要，未补写。

**S6裁决及statement清理。** `{S6_STATEMENT}`formal为`{cite_id} cites`，《赞助人与画家》→该专著，范围限Haskell第7章注1的书内引注，并用第21章书目明确作品身份。另以`{author_id} authored_by`记录书目责任者；该结构性边不属于S2关系候选裁决分母。同步把S2引注claim中误混入的过程摘要移除，改为“Haskell’s footnote 1 cites Bjurström, 1961.”，保留原脚注和声明结构；未增加statement或mention，亦未增加S2复核分子。

本批S3既有决定未重开；未查阅Bjurström专著或其引用内容。
'''
    process_text = process_text.replace("\n", process_nl)
    process_bytes = process_text.encode("utf-8")
    if process_bom:
        process_bytes = b"\xef\xbb\xbf" + process_bytes

    files = {
        align_path: write_csv(align_fields, alignments, align_bom, align_nl),
        manifest_path: write_csv(manifest_fields, new_manifest, manifest_bom, manifest_nl),
        relation_path: write_csv(relation_fields, new_relations, relation_bom, relation_nl),
        accepted_path: accepted_bytes,
        statements_path: statements_bytes,
        ROOT / ARCHIVE_CARD: archive_card().encode("utf-8-sig"),
        ROOT / PERSON_CARD: person_card().encode("utf-8-sig"),
        process_path: process_bytes,
    }
    return files, (cite_id, author_id), (len(manifest), len(new_manifest), len(relations), len(new_relations))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    files, relation_ids, counts = validate_and_plan()
    print(f"S4/S5/S6 plan: {ARCHIVE_GROUP} -> {ARCHIVE_KU}; {PERSON_GROUP} -> {PERSON_KU}")
    print(f"relations: {relation_ids[0]} cites (S6 candidate); {relation_ids[1]} authored_by (bibliographic structure)")
    print(f"manifest: {counts[0]} -> {counts[1]}; relations: {counts[2]} -> {counts[3]}; planned source-backed fields: 6")
    print(f"files planned: {len(files)}; one S2 claim is cleaned; candidate/mention/statement counts stay unchanged")
    if args.dry_run:
        print("DRY RUN passed; no files changed")
        return 0

    recovery_root = ROOT / RECOVERY_REL
    if recovery_root.exists():
        raise SystemExit(f"recovery path already exists; refusing to overwrite: {recovery_root}")
    recovery_root.mkdir(parents=True)
    backups = []
    try:
        for path in files:
            if path.exists():
                rel = path.relative_to(ROOT)
                backup = recovery_root / "original" / rel
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup)
                backups.append((path, backup))
        for path, data in files.items():
            atomic_write(path, data)
    except BaseException:
        for path, backup in reversed(backups):
            atomic_write(path, backup.read_bytes())
        raise
    print(f"APPLIED; recovery snapshot: {RECOVERY_REL}; backed up {len(backups)} existing files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
