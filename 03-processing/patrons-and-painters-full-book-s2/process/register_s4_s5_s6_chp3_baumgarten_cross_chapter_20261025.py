#!/usr/bin/env python3
"""Guarded S4/S5/S6 registration for the cross-chapter Baumgarten citation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s3-s4-s5-s6-chp3-baumgarten-20261025"
)
CARD_REL = "04-knowledge/units/archives/baumgarten-pierre-legros-artiste-romain-1923.md"
KU_ID = "units/archives/baumgarten-pierre-legros-artiste-romain-1923"
S3_GROUP = "archive-group-e5c8b64933ba"
SOURCE3_REL = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
SOURCE21_REL = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
EXPECTED_HASHES = {
    "entity-candidates.csv": "4101d1c147fb258733d89453e3b9ed11931a96225a2f35b305e91c2d089e32c9",
    "alignment.csv": "2c38803671f62e6b78e8d44bc6fb76722791ea91ee2c436d8d560d703bb87a67",
    "ku-manifest.csv": "9dbc1b600db1908cf0e290c69a6cf91d84e90c67a16ad60f8521ef513ef1e14c",
    "enrichment.jsonl": "f6c9ba3f7bfec0fe93c435fa64e954796a0c95981425ae91f8285fc7f41ded14",
    "relations.csv": "1478a0b99fc2f7980eea43eb59004deec366db4657b6a6fc9c978f9fc2af88f9",
    "accepted.yml": "367c81713dae1a94ace1311a8b52ed75b5eb021edb79117c0f912f0357ac7965",
    "book-statements.jsonl": "76c8ea832c03df783b8d394774ebd0eea8e333f5a9d40915cc07f539fc739170",
}
EXPECTED_SOURCE_HASHES = {
    SOURCE3_REL: "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    SOURCE21_REL: "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3",
}
BACKUP_SUFFIX = ".bak-s4-s5-s6-chp3-baumgarten-20261025"


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


def write_csv(headers, rows, bom, newline) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=headers, extrasaction="ignore", lineterminator=newline
    )
    writer.writeheader()
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def table_id() -> str:
    token = f"{KU_ID}|内容 / 基本信息|1|字段|值|证据"
    return "tbl-" + hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]


def make_enrichment(enrichment_id, field, value, evidence, row_index):
    citation = (
        "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
        "(New Haven and London: Yale University Press, 1980; this printing 2006), "
        "ch. 21, printed p. 414."
    )
    return {
        "enrichment_id": enrichment_id,
        "ku_id": KU_ID,
        "field": field,
        "value": value,
        "origin": "book",
        "source_id": "haskell-1980-rev-ed",
        "source_ids": ["haskell-1980-rev-ed"],
        "source_ref": "S1",
        "source_citations": [citation],
        "source_urls": [],
        "evidence": evidence,
        "evidence_status": "source_backed",
        "dispute": None,
        "accessed_date": "",
        "occurrence_id": "occ-" + hashlib.sha256(
            f"{KU_ID}|{field}|{value}".encode("utf-8")
        ).hexdigest()[:16],
        "table_id": table_id(),
        "table_section": "内容 / 基本信息",
        "has_header": True,
        "table_header": ["字段", "值", "证据"],
        "row_index": row_index,
        "cells": [field, value, evidence],
        "unit_evidence_status": "source_backed",
    }


def make_card() -> str:
    citation = (
        "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
        "(New Haven and London: Yale University Press, 1980; this printing 2006)"
    )
    return f'''---
title: "《罗马艺术家皮埃尔·勒格罗》（Pierre Legros, Roman Artist）"
name_en: "Pierre Legros, Roman Artist"
type: archive
evidence_status: source_backed
sub_type: book
sources:
  - citation: "{citation}"
    location: 第3章印刷页92脚注1，OCR L242。
    sentence_summary: Haskell's footnote cites Baumgarten by surname.
    original_quotes:
      - source_span: line 242; printed p.92, note 1
        text: "1 Baumgarten."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SOURCE3_REL}
      source_span: line 242; printed p.92, note 1
  - citation: "{citation}"
    location: 第21章印刷页414，书目行132。
    sentence_summary: The bibliography gives the author form, French title, place, and year as printed.
    original_quotes:
      - source_span: line 132; printed p.414
        text: "Baumgarten, S.: Pierre Legros artiste romain, Paris 1923."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SOURCE21_REL}
      source_span: line 132; printed p.414
created: '2026-10-25'
updated: '2026-10-25'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 本卡记录 Haskell 第21章书目所列的 Baumgarten 著作 *Pierre Legros artiste romain*（Paris, 1923），并连接第3章脚注中的简称“Baumgarten”。中文题名和英文转译为描述性工作名称，不声称是原书副题或官方译名。所引著作尚未独立查阅；本卡只记录 Haskell 的书内引注与书目形式。

**English:** This card records the Baumgarten publication listed in Haskell's chapter 21 bibliography as *Pierre Legros artiste romain* (Paris, 1923), linking it to the abbreviated “Baumgarten” citation in chapter 3. The Chinese title and English rendering are descriptive working titles, not claimed subtitles or official translations. The cited publication has not been independently consulted; this card records Haskell's citation and bibliographic form only.

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 作者（书目形式） | Baumgarten, S. | S1：Haskell，第21章印刷页414，书目行132。 |
| 原书所录题名 | Pierre Legros artiste romain | S1：Haskell，第21章印刷页414，书目行132。 |
| 出版项（书目形式） | Paris, 1923 | S1：Haskell，第21章印刷页414，书目行132。 |
| 文献类型 | book（书目记录） | S1：Haskell，第21章印刷页414，书目行132。 |

### 本书引用范围

Haskell 第3章印刷页92脚注1以 “Baumgarten” 指向此书。此关系表示 Haskell 的书目指引，不证明该书已查阅，也不验证其内容。

**English:** Haskell's chapter 3, page 92, note 1 uses “Baumgarten” to point to this book. The relation records Haskell's bibliographic pointer; it does not mean the cited publication was consulted or its contents verified.

## 关系与证据

### 身份与外部链接

S3 跨章身份组 `{S3_GROUP}`；候选 cand-5494 的第3章脚注简称与第21章完整书目项合并为一个 Haskell 书内文献身份。未使用外部身份库或目录。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
'''


def preflight():
    for name, expected in EXPECTED_HASHES.items():
        path = (ROOT / "04-knowledge" / name) if name == "accepted.yml" else (TABLES / name)
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed; refusing write: {name} {actual}")
    for rel, expected in EXPECTED_SOURCE_HASHES.items():
        actual = sha((ROOT / rel).read_bytes())
        if actual != expected:
            raise SystemExit(f"source changed; refusing write: {rel} {actual}")

    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"new card path already exists: {CARD_REL}")
    backup_inputs = [
        (ROOT / "04-knowledge" / name) if name == "accepted.yml" else (TABLES / name)
        for name in EXPECTED_HASHES
    ]
    for path in backup_inputs:
        if path.with_name(path.name + BACKUP_SUFFIX).exists():
            raise SystemExit(f"backup already exists: {path.name + BACKUP_SUFFIX}")

    source3 = (ROOT / SOURCE3_REL).read_text(encoding="utf-8-sig").splitlines()
    source21 = (ROOT / SOURCE21_REL).read_text(encoding="utf-8-sig").splitlines()
    if source3[241] != "1 Baumgarten.":
        raise SystemExit("chapter 3 note 1 source line changed")
    if source21[131] != "Baumgarten, S.: Pierre Legros artiste romain, Paris 1923.":
        raise SystemExit("chapter 21 bibliography source line changed")
    types_text = (ROOT / ".agents/skills/ingest/references/relation-types.yml").read_text(encoding="utf-8")
    ranges_text = (ROOT / "01-domain/relation-domain-range.yml").read_text(encoding="utf-8")
    if "  - cites\n" not in types_text or not __import__("re").search(
        r"^\s*cites:\s*\{domain:\s*\[archive\],\s*range:\s*\[archive\]\}", ranges_text, __import__("re").M
    ):
        raise SystemExit("cites is not controlled for archive -> archive")

    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as f:
        candidate_rows = list(csv.DictReader(f))
    candidate = [r for r in candidate_rows if r["candidate_id"] == "cand-5494"]
    if len(candidate) != 1 or candidate[0]["suggested_type"] != "archive":
        raise SystemExit("candidate cand-5494 changed or is not an archive")
    if "Pierre Legros artiste romain" not in candidate[0]["canonical_name"]:
        raise SystemExit("candidate identity no longer matches the bibliography")

    alignment_path = TABLES / "alignment.csv"
    align_headers, alignments, align_bom, align_newline = read_csv(alignment_path)
    aligned = [r for r in alignments if r["candidate_id"] == "cand-5494"]
    if len(aligned) != 1 or aligned[0]["decision"] != "new" or aligned[0]["ku_id"]:
        raise SystemExit("candidate cand-5494 is no longer a single unmapped S3 new row")
    alignments_by_id = {r["candidate_id"]: r for r in alignments}
    haskell = alignments_by_id.get("cand-2962")
    if not haskell or haskell["ku_id"] != "units/archives/patrons-and-painters":
        raise SystemExit("Haskell source archive endpoint is not mapped as expected")

    statement_rows = {}
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("statement_id") in {
                "st-chp3-seciv-notes-l205-243-p92-n1-baumgarten",
                "st-chp21-bib-l129-163-entry-03",
            }:
                statement_rows[row["statement_id"]] = row
    note = statement_rows.get("st-chp3-seciv-notes-l205-243-p92-n1-baumgarten")
    bibliography = statement_rows.get("st-chp21-bib-l129-163-entry-03")
    if not note or note.get("subject_candidate_id") != "cand-2962" or note.get("object_candidate_id") != "cand-5494":
        raise SystemExit("chapter 3 note statement endpoints changed")
    if note.get("predicate") != "cites" or not (note.get("qualifiers") or {}).get("relation_candidate"):
        raise SystemExit("chapter 3 note is no longer a cites S6 candidate")
    if not bibliography or bibliography.get("object_candidate_id") != "cand-5494":
        raise SystemExit("chapter 21 bibliography statement no longer supports cand-5494")
    bibliographic_record = (bibliography.get("qualifiers") or {}).get("bibliographic_record") or {}
    if bibliographic_record.get("author_as_printed") != "Baumgarten, S." or bibliographic_record.get("publication_details_as_printed") != "Paris, 1923":
        raise SystemExit("chapter 21 bibliographic details changed")

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_headers, manifest, manifest_bom, manifest_newline = read_csv(manifest_path)
    if any(r.get("ku_id") == KU_ID for r in manifest):
        raise SystemExit("target KU already exists in manifest")
    if not (ROOT / "04-knowledge/units/archives/patrons-and-painters.md").exists():
        raise SystemExit("mapped Haskell source card is missing")
    manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "Pierre Legros artiste romain (1923)",
        "name_en": "Pierre Legros, Roman Artist",
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": CARD_REL,
    })

    accepted_path = ROOT / "04-knowledge/accepted.yml"
    accepted_raw = accepted_path.read_bytes()
    accepted_bom = accepted_raw.startswith(b"\xef\xbb\xbf")
    accepted_text = accepted_raw.decode("utf-8-sig")
    accepted_newline = "\r\n" if "\r\n" in accepted_text else "\n"
    accepted_lines = accepted_text.splitlines()
    accepted_entry = f"- {CARD_REL}"
    if accepted_entry in accepted_lines:
        raise SystemExit("target card is already accepted")
    insertion = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- ") and line[2:].casefold() > CARD_REL.casefold()),
        len(accepted_lines),
    )
    accepted_lines.insert(insertion, accepted_entry)
    accepted_bytes = accepted_newline.join(accepted_lines) + accepted_newline
    accepted_bytes = accepted_bytes.encode("utf-8")
    if accepted_bom:
        accepted_bytes = b"\xef\xbb\xbf" + accepted_bytes

    enrichment_path = TABLES / "enrichment.jsonl"
    enrichment_raw = enrichment_path.read_bytes()
    enrichment_rows = [json.loads(line) for line in enrichment_raw.decode("utf-8-sig").splitlines() if line.strip()]
    if any(r.get("ku_id") == KU_ID for r in enrichment_rows):
        raise SystemExit("target KU already has enrichment fields")
    numeric_ids = [
        int(r["enrichment_id"].split("-")[1])
        for r in enrichment_rows
        if r.get("enrichment_id", "").startswith("enr-") and r["enrichment_id"].split("-")[1].isdigit()
    ]
    next_id = max(numeric_ids, default=0) + 1
    evidence = "S1：Haskell，第21章印刷页414，书目行132。"
    fields = [
        ("作者（书目形式）", "Baumgarten, S."),
        ("原书所录题名", "Pierre Legros artiste romain"),
        ("出版项（书目形式）", "Paris, 1923"),
        ("文献类型", "book（书目记录）"),
    ]
    enrichments = [
        make_enrichment(f"enr-{next_id+i}", field, value, evidence, i+1)
        for i, (field, value) in enumerate(fields)
    ]
    append_sep = b"" if not enrichment_raw or enrichment_raw.endswith((b"\n", b"\r")) else b"\n"
    enrichment_bytes = enrichment_raw + append_sep + b"\n".join(
        json.dumps(r, ensure_ascii=False, separators=(",", ":")).encode("utf-8") for r in enrichments
    ) + b"\n"
    if enrichment_raw.startswith(b"\xef\xbb\xbf") and not enrichment_bytes.startswith(b"\xef\xbb\xbf"):
        enrichment_bytes = b"\xef\xbb\xbf" + enrichment_bytes

    relation_path = TABLES / "relations.csv"
    rel_headers, relations, rel_bom, rel_newline = read_csv(relation_path)
    numeric_rel_ids = [int(r["relation_id"].split("-")[1]) for r in relations if r.get("relation_id", "").startswith("rel-") and r["relation_id"].split("-")[1].isdigit()]
    relation_id = f"rel-{max(numeric_rel_ids, default=0)+1:04d}"
    if any(r.get("relation_id") == relation_id for r in relations):
        raise SystemExit(f"planned relation ID already exists: {relation_id}")
    relation = {
        "relation_id": relation_id,
        "subject_ku_id": "units/archives/patrons-and-painters",
        "object_ku_id": KU_ID,
        "predicate": "cites",
        "time": "",
        "role": "Haskell书内书目指引",
        "scope": "第3章印刷页92脚注1以姓氏 Baumgarten 指向此书；第21章印刷页414书目提供责任者、原题、出版地与年份。仅记录 Haskell 的引注，不表示已独立查阅或验证被引著作。",
        "origin": "book",
        "status": "formal",
        "source_id": "haskell-1980-rev-ed",
        "source_span": "Chapter 3, printed p.92 note 1, L242; related bibliography entry: Chapter 21, printed p.414, L132; statements=st-chp3-seciv-notes-l205-243-p92-n1-baumgarten;st-chp21-bib-l129-163-entry-03",
        "source_file": SOURCE3_REL,
        "note": "Cross-chapter S3 group archive-group-e5c8b64933ba; the cited publication itself was not independently consulted.",
    }
    natural_keys = {
        tuple(r.get(k, "").strip() for k in ("subject_ku_id", "predicate", "object_ku_id", "time", "role", "scope"))
        for r in relations
    }
    key = tuple(relation[k].strip() for k in ("subject_ku_id", "predicate", "object_ku_id", "time", "role", "scope"))
    if key in natural_keys:
        raise SystemExit("duplicate relation natural key")
    relations.append(relation)

    aligned[0]["ku_id"] = KU_ID
    aligned[0]["process_ref"] = PROCESS_REF
    aligned[0]["resolution_note"] += f"; S4 registration: mapped {S3_GROUP} to {KU_ID}; internal cross-chapter publication identity, cited work not independently consulted."

    outputs = {
        alignment_path: write_csv(align_headers, alignments, align_bom, align_newline),
        manifest_path: write_csv(manifest_headers, manifest, manifest_bom, manifest_newline),
        enrichment_path: enrichment_bytes,
        relation_path: write_csv(rel_headers, relations, rel_bom, rel_newline),
        accepted_path: accepted_bytes,
        card_path: make_card().encode("utf-8"),
    }
    preview = {
        "candidate_id": "cand-5494",
        "s3_group": S3_GROUP,
        "decision": "new",
        "ku_id": KU_ID,
        "fields": [{"field": f, "value": v} for f, v in fields],
        "relation": relation,
        "outputs": {str(p.relative_to(ROOT)): {"bytes": len(b), "sha256": sha(b)} for p, b in outputs.items()},
    }
    return outputs, preview


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    outputs, preview = preflight()
    if args.dry_run:
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return
    for path in outputs:
        if path.exists():
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"backup already exists: {backup}")
            shutil.copy2(path, backup)
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".s4tmp")
        temp.write_bytes(data)
        temp.replace(path)
    print(json.dumps({"applied": True, "preview": preview}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
