#!/usr/bin/env python3
"""Guarded S4/S5/S6 registration for Brunelli's 1923 book citation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
TASK = "patrons-and-painters-full-book-s2"
ANCHOR = "s3-s4-s5-s6-chp15-brunelli-unamica-1923-crosschapter-20261025"
PROCESS_REL = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-s5-s6-chp15-brunelli-unamica-20261025"

CANDIDATE_ID = "cand-9501"
GROUP = "archive-group-brunelli-amica-casanova-1923"
KU_ID = "units/archives/brunelli-unamica-del-casanova-1923"
CARD_REL = "04-knowledge/units/archives/brunelli-unamica-del-casanova-1923.md"
AUTHOR_KU = "units/persons/bruno-brunelli"
SOURCE_BOOK_KU = "units/archives/patrons-and-painters"
EXPECTED_STATEMENTS = {"st-chp15-p365-note1-brunelli-1923"}

EXPECTED_HASHES = {
    "04-knowledge/tables/alignment.csv": "28f2ee2f125b70e7f0e0779efb5eab567dcf0baa3aa549d22452f69fbd94ac0d",
    "04-knowledge/tables/ku-manifest.csv": "1aa3d5aa5255eda703317110eb527fb5ab2c8ad8caf47e1c024aef260c178f29",
    "04-knowledge/tables/relations.csv": "739d9e4e613b43adbc30a8a1b83d7977460264e82a3e15cca35a6080a8ac2ef5",
    "04-knowledge/accepted.yml": "8dfc81cb536e000b19177c414140c5128af386a94c6c0a7a138c2ef9f7ffdcfd",
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md": "293cf6ec1e2edce1410265514ce5fdd45dc61b7ca9034fc2b3dea4e57dac92d7",
    "04-knowledge/units/archives/patrons-and-painters.md": "602c175909ffffcaf1c423451a39d5618f5c4fa4cbbfe21c98f674ae5b9a98c5",
    "04-knowledge/units/persons/bruno-brunelli.md": "4e0bdfe755977f8500098eb8c0a36ef00a26e64ba436b0ffaf5ee8a19c14bda3",
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
    writer = csv.DictWriter(
        buffer, fieldnames=headers, extrasaction="ignore", lineterminator=newline
    )
    writer.writeheader()
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as f:
        temp = Path(f.name)
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def add_relations_id(rows) -> str:
    last = max(
        (int(r["relation_id"].removeprefix("rel-")) for r in rows
         if r.get("relation_id", "").startswith("rel-")
         and r["relation_id"][4:].isdigit()),
        default=0,
    )
    return f"rel-{last + 1:04d}"


def make_card() -> str:
    return """---
title: "《卡萨诺瓦的女性友人》（Un’amica del Casanova）"
name_en: "Un’amica del Casanova (A Female Friend of Casanova)"
type: archive
sub_type: book
created: '2026-10-25'
updated: '2026-10-25'
evidence_status: source_backed
sources:
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第10章，印刷页300，注5，Markdown L586。'
    sentence_summary: '脚注简称为B. Brunelli, 1923；第21章书目为该简称提供出版物身份锚点。'
    original_quotes:
      - source_span: 'line 586; printed p. 300, note 5'
        text: '5 B. Brunelli, 1923.'
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/10_CHP-10_intro.md
      source_span: 'line 586; printed p. 300, note 5'
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第15章，印刷页365，注1，Markdown L91；CHP-15.pdf物理页5。'
    sentence_summary: '注1简引Brunelli, 1923；页图确认OCR“Brunel Ji”为印本“Brunelli”。'
    original_quotes:
      - source_span: 'line 91; printed p. 365, note 1; CHP-15.pdf physical page 5'
        text: '1 Brunelli, 1923.'
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/15_CHP-15_sec_ii.md
      source_span: 'line 91; printed p. 365, note 1; CHP-15.pdf physical page 5'
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第21章书目，印刷页417，Markdown L269；CHP-21Bibliography.pdf物理页7。'
    sentence_summary: '书目列出责任者形式、原题名、出版地与出版年；页图核对该条目。'
    original_quotes:
      - source_span: 'line 269; printed p. 417; CHP-21Bibliography.pdf physical page 7'
        text: 'Brunelli, Bruno: Un’amica del Casanova, Milano 1923.'
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/21_CHP-21Bibliography.md
      source_span: 'line 269; printed p. 417; CHP-21Bibliography.pdf physical page 7'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp15-brunelli-unamica-1923-crosschapter-20261025
---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第15章印刷页365注1简引的Brunelli 1923年出版物。第21章印刷页417书目列出书名 *Un’amica del Casanova*、责任者形式“Brunelli, Bruno”、出版地Milano及出版年1923；页图核对确认该项。第10章印刷页300注5另以“B. Brunelli, 1923”引用。该书及脚注所引内容均未独立查阅。中文展示名及英文括注为工作译名，原题名保留意大利语。

**English:** This card records the 1923 publication cited briefly as “Brunelli, 1923” in Haskell’s chapter 15, page 365, note 1. The chapter 21 bibliography, page 417, lists *Un’amica del Casanova*, the printed author form “Brunelli, Bruno,” Milano, and 1923; the page image was checked. Chapter 10, page 300, note 5 also cites “B. Brunelli, 1923.” Neither the book nor the cited passages was independently consulted. The Chinese display title and English rendering are descriptive working translations; the Italian title is retained.

### 文献身份与定位

| 字段 | 内容 | 依据 |
|---|---|---|
| 文献类型 | book（书目记录） | S1、S2；第21章书目 p.417，L269；页图核对 |
| 书内责任者形式 | Brunelli, Bruno | S1、S2；第21章书目 p.417，L269；页图核对 |
| 原题名 | Un’amica del Casanova | S2；第21章书目 p.417，L269；页图核对 |
| 出版地 | Milano | S2；第21章书目 p.417，L269；页图核对 |
| 出版年 | 1923 | S1、S2；第15章 p.365 注1，L91；第21章书目 p.417，L269 |

## 关系与证据

### 身份与外部链接

跨章 S3 身份组 `archive-group-brunelli-amica-casanova-1923` 将第10章 p.300 注5、第15章 p.365 注1和第21章 p.417书目条目对应为同一来源限定出版物。未查阅外部目录、该书或其引注内容。

### 关系记录

"""


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in lines):
        raise SystemExit(f"accepted.yml already contains {CARD_REL}")
    candidates = [
        i for i, line in enumerate(lines)
        if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
    ]
    if candidates:
        at = candidates[0]
    else:
        at = next((i for i, line in enumerate(lines) if line == "claims:"), len(lines))
    lines.insert(at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def validate_and_plan():
    for rel, expected in EXPECTED_HASHES.items():
        path = ROOT / rel
        if not path.exists() or sha(path.read_bytes()) != expected:
            raise SystemExit(f"baseline changed; refusing to apply: {rel}")

    candidate_fields, candidates, _, _ = read_csv(TABLES / "entity-candidates.csv")
    candidate = next((r for r in candidates if r.get("candidate_id") == CANDIDATE_ID), None)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit("candidate is missing or no longer an archive")
    if candidate.get("canonical_name") != "Bruno Brunelli, Un’amica del Casanova (Milano, 1923; citation locator)":
        raise SystemExit("candidate identity text changed")

    align_path = TABLES / "alignment.csv"
    align_fields, alignments, align_bom, align_nl = read_csv(align_path)
    target_rows = [r for r in alignments if r.get("candidate_id") == CANDIDATE_ID]
    if len(target_rows) != 1:
        raise SystemExit(f"expected one S3 row for {CANDIDATE_ID}; got {len(target_rows)}")
    alignment = target_rows[0]
    if alignment.get("decision") != "new" or alignment.get("ku_id"):
        raise SystemExit("S3 must remain new and the KU mapping must still be empty")
    if f"group={GROUP}" not in alignment.get("resolution_note", ""):
        raise SystemExit("existing cross-chapter S3 group is missing")
    if alignment.get("external_source") or alignment.get("external_id"):
        raise SystemExit("unexpected external identity on this source-local publication")

    group_members = {
        r["candidate_id"] for r in alignments
        if r.get("candidate_id") and r.get("decision") == "new"
        and f"group={GROUP}" in r.get("resolution_note", "")
    }
    if group_members != {CANDIDATE_ID}:
        raise SystemExit(f"unexpected identity-group members: {sorted(group_members)}")

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest, manifest_bom, manifest_nl = read_csv(manifest_path)
    if any(r.get("ku_id") == KU_ID or r.get("card_path") == CARD_REL for r in manifest):
        raise SystemExit("target KU is already in ku-manifest.csv")
    author = next((r for r in manifest if r.get("ku_id") == AUTHOR_KU), None)
    source_book = next((r for r in manifest if r.get("ku_id") == SOURCE_BOOK_KU), None)
    if not author or author.get("type") != "person" or not source_book or source_book.get("type") != "archive":
        raise SystemExit("citation or author endpoint is missing or has the wrong type")
    if any(r.get("type") == "archive" and (r.get("name_en") or "").casefold() == "un’amica del casanova (a female friend of casanova)".casefold() for r in manifest):
        raise SystemExit("a same-title archive KU already exists")

    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"target card already exists: {CARD_REL}")

    statement_path = TABLES / "book-statements.jsonl"
    statements = []
    for line in statement_path.read_text(encoding="utf-8-sig").splitlines():
        import json
        statements.append(json.loads(line))
    relation_candidates = {
        s["statement_id"]: s for s in statements
        if (s.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE_ID in (s.get("subject_candidate_id"), s.get("object_candidate_id"))
    }
    if set(relation_candidates) != EXPECTED_STATEMENTS:
        raise SystemExit(f"unexpected direct relation candidates: {sorted(relation_candidates)}")
    citation = relation_candidates[next(iter(EXPECTED_STATEMENTS))]
    if (citation.get("predicate") != "cites"
            or citation.get("subject_candidate_id") != "cand-2962"
            or citation.get("object_candidate_id") != CANDIDATE_ID
            or citation.get("source_file") != "02-sources/02-Markdown/15_CHP-15_sec_ii.md"):
        raise SystemExit("the p.365 citation candidate changed")

    relation_path = TABLES / "relations.csv"
    relation_fields, relations, relation_bom, relation_nl = read_csv(relation_path)
    existing_pairs = {
        (r.get("subject_ku_id"), r.get("predicate"), r.get("object_ku_id"))
        for r in relations
    }
    if (SOURCE_BOOK_KU, "cites", KU_ID) in existing_pairs or (KU_ID, "authored_by", AUTHOR_KU) in existing_pairs:
        raise SystemExit("a target relation already exists")
    next_id = add_relations_id(relations)
    n = int(next_id.removeprefix("rel-"))
    rel_cite_id, rel_author_id = f"rel-{n:04d}", f"rel-{n + 1:04d}"
    if any(r.get("relation_id") in {rel_cite_id, rel_author_id} for r in relations):
        raise SystemExit("allocated relation IDs already exist")

    new_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "《卡萨诺瓦的女性友人》（Un’amica del Casanova）",
        "name_en": "Un’amica del Casanova (A Female Friend of Casanova)",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]

    new_relations = list(relations) + [
        {
            "relation_id": rel_cite_id,
            "subject_ku_id": SOURCE_BOOK_KU,
            "object_ku_id": KU_ID,
            "predicate": "cites",
            "time": "1923",
            "role": "第15章脚注书目引文",
            "scope": "Haskell第15章印刷页365注1引用Brunelli 1923年出版物；第21章p.417书目给出完整题名与出版项。仅记录书内引注，不表示项目查阅该书或注中所引内容。",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 15, printed p.365, note 1, L91; statement=st-chp15-p365-note1-brunelli-1923; related bibliography: Chapter 21, printed p.417, L269",
            "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
            "note": "The page image reads ‘Brunelli, 1923’ (Markdown OCR: ‘Brunel Ji, 1923’); the chapter 21 bibliography confirms the publication identity. Neither the cited publication nor its cited contents were independently consulted.",
        },
        {
            "relation_id": rel_author_id,
            "subject_ku_id": KU_ID,
            "object_ku_id": AUTHOR_KU,
            "predicate": "authored_by",
            "time": "1923",
            "role": "书目责任者归属",
            "scope": "Haskell第21章印刷页417书目以‘Brunelli, Bruno’著录《Un’amica del Casanova》；此边记录书内书目归属，不声称独立核验作者身份或著作内容。",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 21, printed p.417, L269; statement=st-chp21-bib-l243-293-entry-17",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
            "note": "The author KU is the existing cross-chapter Bruno Brunelli identity used for his 1931 article; this relation records only the author form printed for the 1923 book.",
        },
    ]

    alignments = [dict(r) for r in alignments]
    target_alignment = next(r for r in alignments if r.get("candidate_id") == CANDIDATE_ID)
    target_alignment["ku_id"] = KU_ID
    target_alignment["resolution_note"] += (
        f" S4 registration: mapped {GROUP} to {KU_ID}; the chapter 10 p.300 note 5, "
        "chapter 15 p.365 note 1, and chapter 21 p.417 bibliography identify one source-local publication."
    )

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_raw = accepted_path.read_bytes()
    accepted_bom = accepted_raw.startswith(b"\xef\xbb\xbf")
    accepted_nl = "\r\n" if b"\r\n" in accepted_raw else "\n"
    accepted_text = accepted_raw.decode("utf-8-sig")
    planned_accepted = insert_accepted(accepted_text).replace("\n", accepted_nl)
    accepted_bytes = planned_accepted.encode("utf-8")
    if accepted_bom:
        accepted_bytes = b"\xef\xbb\xbf" + accepted_bytes

    process_path = ROOT / PROCESS_REL
    process_raw = process_path.read_bytes()
    process_bom = process_raw.startswith(b"\xef\xbb\xbf")
    process_nl = "\r\n" if b"\r\n" in process_raw else "\n"
    process_text = process_raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if not process_text.endswith("\n"):
        process_text += "\n"
    process_text += f"""

<a id="{ANCHOR}"></a>

### S3–S4–S5–S6：第15章 Brunelli《Un’amica del Casanova》（1923）跨章档案登记（2026-10-25）

**跨章 S3 身份组沿用。** `{CANDIDATE_ID}`沿用`{GROUP}`及既有`new`决定。第10章p.300注5以“B. Brunelli, 1923”引用；第15章p.365注1印本页图（`CHP-15.pdf`物理页5）读作“Brunelli, 1923”；第21章p.417书目（`CHP-21Bibliography.pdf`物理页7）列为“Brunelli, Bruno: Un’amica del Casanova, Milano 1923”。作者形式、题名和年份相符，归为同一来源限定出版物。OCR原文和来源Markdown保持不变。该书与脚注所引内容均未独立查阅；没有外部身份断言。

**S4 登记。** `{CANDIDATE_ID}`映射至`{KU_ID}`并登记为[档案知识卡](../../../{CARD_REL})。既有作者人物KU `{AUTHOR_KU}`已存在，无需递归增加作者待办。S3的`new`决定未改写。

**S5 字段。** 仅从Haskell第21章p.417书目登记文献类型、书内责任者形式、原题名、出版地和出版年共5条`source_backed`字段；不补写出版社、版本、页数或作品内容。中文展示名和英文括注为工作译名。

**S6 逐项裁决。** `{next(iter(EXPECTED_STATEMENTS))}` formal为`{rel_cite_id} cites`，主语《赞助人与画家》、宾语为本书，证据为第15章p.365注1及第21章p.417书目。关系只表示Haskell的书内引注，不表示本项目查阅被引书或其第52页。另登记结构性`{rel_author_id} authored_by`，依据第21章书目；它不属于S2 `relation_candidate=true` 裁决分母。两条边分别符合archive→archive与archive→person方向。

本批不改S2 statement／mention或统一独立复核分子；不增加S3候选数。"""
    process_text = process_text.replace("\n", process_nl)
    process_bytes = process_text.encode("utf-8")
    if process_bom:
        process_bytes = b"\xef\xbb\xbf" + process_bytes

    files = {
        align_path: write_csv(align_fields, alignments, align_bom, align_nl),
        manifest_path: write_csv(manifest_fields, new_manifest, manifest_bom, manifest_nl),
        relation_path: write_csv(relation_fields, new_relations, relation_bom, relation_nl),
        accepted_path: accepted_bytes,
        ROOT / CARD_REL: make_card().encode("utf-8-sig"),
        process_path: process_bytes,
    }
    return files, (rel_cite_id, rel_author_id), (len(manifest), len(new_manifest), len(relations), len(new_relations))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    files, rel_ids, counts = validate_and_plan()
    print(f"S4/S5/S6 plan: {GROUP} -> {KU_ID}")
    print(f"relations: {rel_ids[0]} cites (S6 candidate); {rel_ids[1]} authored_by (bibliographic structure)")
    print(f"manifest: {counts[0]} -> {counts[1]}; relations table: {counts[2]} -> {counts[3]}; S5 rows queued for field-fact preview: 5")
    print(f"files planned: {len(files)}; no unrelated candidate or backlog changes")
    if args.dry_run:
        print("DRY RUN passed; no files changed")
        return 0

    backups = []
    for path in files:
        if path.exists():
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery backup already exists; refusing to overwrite: {backup}")
            backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    try:
        for path, data in files.items():
            atomic_write(path, data)
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        raise
    print(f"APPLIED; created recovery copies for {len(backups)} existing files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
