#!/usr/bin/env python3
"""Guarded S4/S5/S6 registration for Félibien's 1725 edition."""
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
ANCHOR = "s4-s5-s6-chp7-p182-felibien-entretiens-20261025"
PROCESS_REL = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
RECOVERY_REL = "06-runtime/recovery/s4-s5-s6-chp7-felibien-20261025"

CANDIDATE_ID = "cand-7077"
ALIGNMENT_ID = "aln-7253"
GROUP = "archive-group-b5989be79137"
KU_ID = "units/archives/felibien-entretiens-trevoux-1725-six-volume-edition"
CARD_REL = "04-knowledge/units/archives/felibien-entretiens-trevoux-1725-six-volume-edition.md"
AUTHOR_KU = "units/persons/andre-felibien"
SOURCE_BOOK_KU = "units/archives/patrons-and-painters"
STATEMENT_ID = "st-chp7-p182-n2-cite-felibien"
TITLE = "《古代与现代杰出画家的生平与作品谈录》（Conversations on the Lives and Works of the Most Excellent Painters, Ancient and Modern, Trévoux 1725 edition）"
NAME_EN = "Conversations on the Lives and Works of the Most Excellent Painters, Ancient and Modern (Trévoux, 1725 edition)"

EXPECTED_HASHES = {
    "04-knowledge/tables/alignment.csv": "0901575cc3386f95b1b3a81361712a62e37648771c105ee0a4619c75bcbeaf70",
    "04-knowledge/tables/ku-manifest.csv": "1ef8bf76b8f0fdfd10f2c33aa96369b7a389866489df1feabdd85972ffe1512d",
    "04-knowledge/tables/relations.csv": "bd8a73f578373bbdca2213d1352d915b204e9c5f7da4be5d119dc0421aca94e5",
    "04-knowledge/accepted.yml": "1e962f3db1054aa005f5f0e085d05e660d7bd04640f126056cca2ea68738677d",
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md": "b59a99558e213590055ddc2348ea99900b4a53c2199d6fca52f309c0f96dcaaa",
    "04-knowledge/units/archives/patrons-and-painters.md": "0e8f0a4bb2d20b5d90f75dcc39cf295ac0dbb4683fdf5a78d3731fd0fc454677",
    "04-knowledge/units/persons/andre-felibien.md": "6b85cb452265e199aa7915f433ef88d96205763ea50596fbee832cb13f7ecc85",
    "04-knowledge/tables/entity-candidates.csv": "7bc213a5894ec74a11440fbbd02019a3f97ea0dfc9c38609ed2ab536fcf289f2",
    "04-knowledge/tables/book-statements.jsonl": "41dcfdeddbed5e33316c72fc48f4bc8a3a57f012ae41a374a4b5eb2e7ca640bd",
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


def make_card() -> str:
    return f'''---
title: "{TITLE}"
name_en: "{NAME_EN}"
type: archive
sub_type: book
created: '2026-10-25'
updated: '2026-10-25'
evidence_status: source_backed
sources:
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第7章，印刷页182注2；CHP-7.pdf物理页16；Markdown L344。'
    sentence_summary: '注2列Félibien第三卷第530页作为引注；所引书和该页未独立查阅。'
    original_quotes:
      - source_span: 'line 344; printed p. 182, note 2; CHP-7.pdf physical page 16'
        text: '2 Félibien, III, p. 530.'
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/07_CHP-7_sec_i.md
      source_span: 'line 344; printed p. 182, note 2; CHP-7.pdf physical page 16'
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第21章书目，印刷页422；CHP-21Bibliography.pdf物理页12；Markdown L466。'
    sentence_summary: '书目著录Félibien、法文原题、新版六卷、Trévoux及1725年；页图复核其省略号和出版项。'
    original_quotes:
      - source_span: 'line 466; printed p. 422; CHP-21Bibliography.pdf physical page 12'
        text: 'Félibien: Entretiens sur les vies et sur les ouvrages des plus excellens peintres anciens et modernes . . . nouvelle édition, 6 vols., Trévoux 1725.'
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/21_CHP-21Bibliography.md
      source_span: 'line 466; printed p. 422; CHP-21Bibliography.pdf physical page 12'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}
---

## 内容

### 描述

**中文：** 本卡记录Haskell第21章书目列出的Félibien《Entretiens》新版六卷本（Trévoux，1725）。第7章印刷页182注2引用第三卷第530页。本KU表示书目所指版本，不表示已查阅该书、被引卷册或被引页。中文题名和英文题名为依据法文原题的描述性工作译名。

**English:** This unit records the six-volume nouvelle édition of Félibien’s *Entretiens*, listed in Haskell’s Chapter 21 bibliography as published at Trévoux in 1725. Chapter 7, printed page 182, note 2, cites volume III, page 530. This KU represents the bibliographic edition; the book, cited volume, and cited page were not independently consulted. The Chinese and English display titles are descriptive working translations of the French original.

### 文献身份与定位

| 字段 | 内容 | 依据 |
|---|---|---|
| 文献类型 | 学术文献／对话体著作；按书目所列书籍记录 | S1；第21章书目 p.422，L466；页图核对 |
| 书目责任者形式 | Félibien | S1；第21章书目 p.422，L466；页图核对 |
| 原题名 | Entretiens sur les vies et sur les ouvrages des plus excellens peintres anciens et modernes | S1；第21章书目 p.422，L466；页图核对 |
| 版本与卷册 | nouvelle édition, 6 vols. | S1；第21章书目 p.422，L466；页图核对 |
| 出版地 | Trévoux | S1；第21章书目 p.422，L466；页图核对 |
| 出版年 | 1725 | S1；第21章书目 p.422，L466；页图核对 |

## 关系与证据

### 身份与外部链接

S3身份组 `{GROUP}` 将候选 `{CANDIDATE_ID}` 对齐至本KU。第21章书目中的责任者形式与书内索引所列 André Félibien 对应；复用既有人物KU，不据此添加外部身份标识。未查阅书目以外的外部目录或该著作。

### 关系记录
'''


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in lines):
        raise SystemExit(f"accepted.yml already contains {CARD_REL}")
    candidates = [i for i, line in enumerate(lines)
                  if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL]
    at = candidates[0] if candidates else next((i for i, line in enumerate(lines) if line == "claims:"), len(lines))
    lines.insert(at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def validate_and_plan():
    for rel, expected in EXPECTED_HASHES.items():
        path = ROOT / rel
        if not path.exists() or sha(path.read_bytes()) != expected:
            raise SystemExit(f"baseline changed; refusing to apply: {rel}")

    _, candidates, _, _ = read_csv(TABLES / "entity-candidates.csv")
    candidate = next((r for r in candidates if r.get("candidate_id") == CANDIDATE_ID), None)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit("candidate is missing or no longer an archive")
    if "Félibien" not in candidate.get("canonical_name", "") or "1725" not in candidate.get("canonical_name", ""):
        raise SystemExit("candidate identity text changed")

    align_path = TABLES / "alignment.csv"
    align_fields, alignments, align_bom, align_nl = read_csv(align_path)
    target_rows = [r for r in alignments if r.get("candidate_id") == CANDIDATE_ID]
    if len(target_rows) != 1:
        raise SystemExit(f"expected one alignment row for {CANDIDATE_ID}; got {len(target_rows)}")
    target_alignment = target_rows[0]
    if target_alignment.get("alignment_id") != ALIGNMENT_ID or target_alignment.get("decision") != "new" or target_alignment.get("ku_id"):
        raise SystemExit("expected the existing S3 new decision with an empty S4 mapping")
    if f"group={GROUP}" not in target_alignment.get("resolution_note", ""):
        raise SystemExit("the existing S3 identity group is missing")
    group_members = {r["candidate_id"] for r in alignments
                     if r.get("decision") == "new" and f"group={GROUP}" in r.get("resolution_note", "")}
    if group_members != {CANDIDATE_ID}:
        raise SystemExit(f"unexpected identity-group members: {sorted(group_members)}")

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest, manifest_bom, manifest_nl = read_csv(manifest_path)
    if any(r.get("ku_id") == KU_ID or r.get("card_path") == CARD_REL for r in manifest):
        raise SystemExit("target KU is already in ku-manifest.csv")
    author = next((r for r in manifest if r.get("ku_id") == AUTHOR_KU), None)
    source_book = next((r for r in manifest if r.get("ku_id") == SOURCE_BOOK_KU), None)
    if not author or author.get("type") != "person" or not source_book or source_book.get("type") != "archive":
        raise SystemExit("source or author KU is missing or has the wrong type")
    if any(r.get("name_en", "").casefold() == NAME_EN.casefold() for r in manifest if r.get("type") == "archive"):
        raise SystemExit("a matching archive name already exists")
    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"target card already exists: {CARD_REL}")

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()]
    candidates_for_endpoint = [s for s in statements
                               if (s.get("qualifiers") or {}).get("relation_candidate") is True
                               and CANDIDATE_ID in (s.get("subject_candidate_id"), s.get("object_candidate_id"))]
    if len(candidates_for_endpoint) != 1:
        raise SystemExit(f"expected one S6 relation candidate; got {len(candidates_for_endpoint)}")
    statement = candidates_for_endpoint[0]
    if (statement.get("statement_id") != STATEMENT_ID or statement.get("predicate") != "cites"
            or statement.get("subject_candidate_id") != "cand-2962"
            or statement.get("object_candidate_id") != CANDIDATE_ID
            or statement.get("source_file") != "02-sources/02-Markdown/07_CHP-7_sec_i.md"):
        raise SystemExit("the chapter 7 citation statement changed")

    relation_path = TABLES / "relations.csv"
    relation_fields, relations, relation_bom, relation_nl = read_csv(relation_path)
    existing_pairs = {(r.get("subject_ku_id"), r.get("predicate"), r.get("object_ku_id")) for r in relations}
    if ((SOURCE_BOOK_KU, "cites", KU_ID) in existing_pairs
            or (KU_ID, "authored_by", AUTHOR_KU) in existing_pairs):
        raise SystemExit("a target relation already exists")
    cite_id, author_id = next_relation_ids(relations)
    allocated = {cite_id, author_id}
    if any(r.get("relation_id") in allocated for r in relations):
        raise SystemExit("allocated relation IDs already exist")

    new_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": TITLE,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    new_relations = list(relations) + [
        {
            "relation_id": cite_id,
            "subject_ku_id": SOURCE_BOOK_KU,
            "object_ku_id": KU_ID,
            "predicate": "cites",
            "time": "",
            "role": "第7章注释书目引文",
            "scope": "Haskell第7章印刷页182注2引用Félibien《Entretiens》第三卷第530页；第21章p.422书目识别为Trévoux 1725年新版六卷本。仅记录书内引注，所引书与页未独立查阅。",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 7, printed p.182, note 2, L344; statement=st-chp7-p182-n2-cite-felibien; bibliography: Chapter 21, printed p.422, L466",
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "note": "The printed note reads ‘Félibien, III, p. 530’; the bibliography identifies the six-volume nouvelle édition at Trévoux in 1725. The cited publication and cited page were not independently consulted.",
        },
        {
            "relation_id": author_id,
            "subject_ku_id": KU_ID,
            "object_ku_id": AUTHOR_KU,
            "predicate": "authored_by",
            "time": "",
            "role": "书目责任者归属",
            "scope": "Haskell第21章印刷页422书目以‘Félibien’署名该六卷本著作；书内索引与既有人物KU记录 André Félibien。此边只记录书内书目责任者归属，不声称查阅原书。",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 21, printed p.422, L466; bibliography entry for Entretiens",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
            "note": "Bibliographic authorship is structural and is not an S2 relation-candidate adjudication.",
        },
    ]

    alignments = [dict(r) for r in alignments]
    target_alignment = next(r for r in alignments if r.get("candidate_id") == CANDIDATE_ID)
    target_alignment["ku_id"] = KU_ID
    target_alignment["resolution_note"] += (
        f" S4 registration: mapped {GROUP} to {KU_ID}; Chapter 7 p.182 note 2 and Chapter 21 p.422 bibliography identify the cited volume as part of the six-volume Trévoux 1725 edition."
    )

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_raw = accepted_path.read_bytes()
    accepted_bom = accepted_raw.startswith(b"\xef\xbb\xbf")
    accepted_nl = "\r\n" if b"\r\n" in accepted_raw else "\n"
    accepted_text = accepted_raw.decode("utf-8-sig")
    accepted_bytes = insert_accepted(accepted_text).replace("\n", accepted_nl).encode("utf-8")
    if accepted_bom:
        accepted_bytes = b"\xef\xbb\xbf" + accepted_bytes

    process_path = ROOT / PROCESS_REL
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

### S4–S5–S6：第7章 Félibien《Entretiens》Trévoux 1725年六卷本（2026-10-25）

**S3身份组沿用。** `{CANDIDATE_ID}`沿用既有`{GROUP}`及`new`决定（`{ALIGNMENT_ID}`），本批不重开身份裁决。第7章印刷页182注2列“Félibien, III, p. 530”；扫描页（`CHP-7.pdf`物理页16）核实该引注。第21章印刷页422书目（`CHP-21Bibliography.pdf`物理页12）列Félibien《Entretiens sur les vies et sur les ouvrages des plus excellens peintres anciens et modernes》新版六卷、Trévoux、1725；扫描页核实书目省略号及出版项。OCR Markdown在原题后省略号处为空格，来源文件保持不改。两处共同支持同一书目版本及所引第三卷定位；被引著作与第530页均未独立查阅。

**S4登记。** `{CANDIDATE_ID}`映射至`{KU_ID}`，新增档案KU并登记至accepted与manifest。书目责任者复用既有人物KU `{AUTHOR_KU}`；没有外部身份标识或传记补写。

**S5字段。** 从第21章书目新增六条`source_backed`字段：文献类型、书目责任者形式、法文原题、版本／卷册、出版地、出版年。中文与英文展示名是描述性工作译名；未添加书目未载的出版者、印次细节或内容摘要。

**S6裁决。** `{STATEMENT_ID}`逐项formal为`{cite_id} cites`，《赞助人与画家》→该书目版本，范围限第7章注2的第三卷第530页引注。另以书目责任者事实登记结构性`{author_id} authored_by`，不属于S2 relation-candidate裁决分母。两条关系方向分别符合archive→archive及archive→person。

本批不改S2 statement／mention或统一独立复核分子。
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
        card_path: make_card().encode("utf-8-sig"),
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
    print(f"S4/S5/S6 plan: {GROUP} -> {KU_ID}")
    print(f"relations: {relation_ids[0]} cites (S6 candidate); {relation_ids[1]} authored_by (bibliographic structure)")
    print(f"manifest: {counts[0]} -> {counts[1]}; relations: {counts[2]} -> {counts[3]}; S5 source-backed rows queued: 6")
    print(f"files planned: {len(files)}; no S2 statement, candidate, or unrelated backlog changes")
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
