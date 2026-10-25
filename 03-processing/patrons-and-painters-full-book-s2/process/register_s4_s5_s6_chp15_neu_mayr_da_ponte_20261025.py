#!/usr/bin/env python3
"""Guarded registration of two cross-chapter bibliography groups and Da Ponte."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s3-s4-s5-s6-chp15-neu-mayr-da-ponte-20261025"
)
BACKUP_SUFFIX = ".bak-s4-s5-s6-chp15-neu-mayr-da-ponte-20261025"

ARCHIVE_NEU_ID = "units/archives/neu-mayr-prato-della-valle-1807"
ARCHIVE_DAP_ID = "units/archives/lorenzo-da-ponte-memorie-1960"
PERSON_DAP_ID = "units/persons/lorenzo-da-ponte"
ARCHIVE_NEU_PATH = "04-knowledge/units/archives/neu-mayr-prato-della-valle-1807.md"
ARCHIVE_DAP_PATH = "04-knowledge/units/archives/lorenzo-da-ponte-memorie-1960.md"
PERSON_DAP_PATH = "04-knowledge/units/persons/lorenzo-da-ponte.md"
S3_PERSON_GROUP = "person-group-" + hashlib.sha256(
    b"Lorenzo da Ponte|chp15-p368-note4|chp21-p434-entry"
).hexdigest()[:12]
EXPECTED_EXISTING_CARD_HASHES = {
    ARCHIVE_NEU_PATH: "a6371ef7a6355dd04a85dafb573261685607ff4e6db970f257a335d098b825b1",
    ARCHIVE_DAP_PATH: "1e92010729274dd8ad19b8014e038e4a6b09498b4f4f0de0ca27058e16ffafc1",
    PERSON_DAP_PATH: "127a3cd35d818be724ea5cf80d346f9ce7aa169a9ca3ea8d3205f897f22b747f",
}

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "aa659419f1c92a16f52cae410e656619e88c68a319d93730a16a702fa5d9bc41",
    "04-knowledge/tables/alignment.csv": "90ab0a8c672cfb248561132b67816e450c38c7e91995985dbc4e4ecf31bc2df7",
    "04-knowledge/tables/mentions.csv": "51ae25ac0ac91770220eaffa58ad80042e647b9c18e8cea415265832ab4b7648",
    "04-knowledge/tables/candidate-backlog.csv": "b9f1dc1274671407d268c3e8ff31cfe9aca79cfc350a1306d01edeee3c312843",
    "04-knowledge/tables/ku-manifest.csv": "66308a77ec8838ed9938df64819d70b8a7d04b87b1886bfbb6cfd05216f24e2a",
    "04-knowledge/tables/enrichment.jsonl": "129d6397f8ec78c740159b366639d620df5f38a0c52a7e7c56b3dc56a0195e9a",
    "04-knowledge/tables/relations.csv": "0882029dd4a54c742d0ecc53049d351bb593908fd2c6124e03e8e82d66640b70",
    "04-knowledge/accepted.yml": "0cc2484da9d4b5aa0a556b4c754b24bd96a50ef590fbcfcdc9c19750c060f8a2",
    "04-knowledge/tables/book-statements.jsonl": "41dcfdeddbed5e33316c72fc48f4bc8a3a57f012ae41a374a4b5eb2e7ca640bd",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "02-sources/02-Markdown/15_CHP-15_sec_ii.md": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "02-sources/02-Markdown/21_CHP-21Bibliography.md": "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3",
}
EXPECTED_PREVIOUS_BACKUP_HASHES = {
    "04-knowledge/tables/mentions.csv": "51ae25ac0ac91770220eaffa58ad80042e647b9c18e8cea415265832ab4b7648",
    "04-knowledge/tables/candidate-backlog.csv": "b9f1dc1274671407d268c3e8ff31cfe9aca79cfc350a1306d01edeee3c312843",
    "04-knowledge/tables/enrichment.jsonl": "129d6397f8ec78c740159b366639d620df5f38a0c52a7e7c56b3dc56a0195e9a",
    "04-knowledge/accepted.yml": "0cc2484da9d4b5aa0a556b4c754b24bd96a50ef590fbcfcdc9c19750c060f8a2",
    ARCHIVE_NEU_PATH: "14ea8162a8ba29cd56a779d38ca8d45353f5800b3fbaefdd0820b537e0f0b0f1",
    ARCHIVE_DAP_PATH: "f4474cdfbdf23ff14e689bc9b233a8d5376cd235b4361c54830ee5b08ef7f7d6",
    PERSON_DAP_PATH: "b3176deab8320943abace1cab1e7bf6075a45bd7581e1fdb4ba486366fc31088",
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


def write_csv(headers, rows, bom, newline) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=headers, extrasaction="ignore", lineterminator=newline
    )
    writer.writeheader()
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def next_number(rows, key, prefix):
    values = [
        int(row[key][len(prefix):])
        for row in rows
        if row.get(key, "").startswith(prefix)
        and row[key][len(prefix):].isdigit()
    ]
    return max(values, default=0) + 1


def table_id(ku_id: str, section: str) -> str:
    token = f"{ku_id}|{section}|1|字段|值|证据"
    return "tbl-" + hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]


def make_enrichment(enrichment_id, ku_id, section, field, value, evidence, row_index):
    citation = (
        "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
        "(New Haven and London: Yale University Press, 1980; this printing 2006)"
    )
    return {
        "enrichment_id": enrichment_id,
        "ku_id": ku_id,
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
            f"{ku_id}|{field}|{value}".encode("utf-8")
        ).hexdigest()[:16],
        "table_id": table_id(ku_id, section),
        "table_section": section,
        "has_header": True,
        "table_header": ["字段", "值", "证据"],
        "row_index": row_index,
        "cells": [field, value, evidence],
        "unit_evidence_status": "source_backed",
    }


def cards():
    citation = (
        "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
        "(New Haven and London: Yale University Press, 1980; this printing 2006)"
    )
    neu = f'''---
title: "《普拉托·德拉·瓦莱图说，或帕多瓦雕像广场图说》（Illustration of the Prato della Valle, or the Piazza of the Statues of Padua）"
name_en: "Illustration of the Prato della Valle, or the Piazza of the Statues of Padua"
type: archive
evidence_status: source_backed
sub_type: book
sources:
  - citation: "{citation}"
    location: 第15章印刷页365注2，footnote segment L92；续文见正文段 L12。
    sentence_summary: Haskell's note directs readers to Neu-Mayr (1807) for figures and inscriptions associated with the Prà della Valle.
    original_quotes:
      - source_span: printed p.365, note 2, L92; continuation at L12
        text: "2 For the history of the Pri della Valle see Radicchio, 1786, and for the figures, inscriptions, etc."
      - source_span: printed p.365, note 2 continuation, L12
        text: "see Neu-Mayr, 1807."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/15_CHP-15_sec_ii.md
      source_span: printed p.365, note 2, L92; continuation L12
  - citation: "{citation}"
    location: 第21章印刷页431，书目 L874–875。
    sentence_summary: The bibliography gives the author form, full Italian title, place, and year.
    original_quotes:
      - source_span: printed p.431, L874–875
        text: "Neu-Mayr, A.: Illustrazione del Prato della Valle ossia della Piazza delle Statue di Padova, — Padova 1807."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/21_CHP-21Bibliography.md
      source_span: printed p.431, L874–875
created: '2026-10-25'
updated: '2026-10-25'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 本卡记录 Haskell 第15章印刷页365注2简称“Neu-Mayr, 1807”所指的书目身份；第21章印刷页431列出作者著录形式、意大利文题名、出版地和年份。中文题名与英文转译为描述性工作题名，不声称为正式译名。被引出版物未独立查阅；作者仅按书目所印首字母记录，不据此扩写人物身份。

**English:** This card records the bibliographic identity behind “Neu-Mayr, 1807” in Haskell's chapter 15, page 365, note 2. The chapter 21 bibliography, printed page 431, gives the author form, Italian title, place, and year. The Chinese title and English rendering are descriptive working titles, not claimed official translations. The cited publication was not independently consulted; the author is recorded only by the initial printed in the bibliography, without expanding the person's identity.

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 作者（书目形式） | Neu-Mayr, A. | S1：Haskell，第21章印刷页431，书目 L874–875。 |
| 原书所录题名 | Illustrazione del Prato della Valle ossia della Piazza delle Statue di Padova | S1：Haskell，第21章印刷页431，书目 L874–875。 |
| 出版地 | Padova | S1：Haskell，第21章印刷页431，书目 L874–875。 |
| 出版年 | 1807 | S1：Haskell，第21章印刷页431，书目 L874–875。 |
| 文献类型 | book（书目记录） | S1：Haskell，第21章印刷页431，书目 L874–875。 |

### 本章相关内容

Haskell's note refers readers to this publication for figures and inscriptions associated with the Prà della Valle. This records the citation's stated scope, not the book's contents or Haskell's use of a particular passage.

**English:** Haskell's note refers readers to this publication for figures and inscriptions associated with the Prà della Valle. This records the citation's stated scope, not the book's contents or Haskell's use of a particular passage.

## 关系与证据

### 身份与外部链接

Cross-chapter S3 group `archive-group-c8faf880aceb`; the chapter 15 locator and chapter 21 bibliography entry identify one source-local publication. No external bibliographic record or copy was consulted.

### 关系记录

'''
    dap = f'''---
title: "《洛伦佐·达·蓬特回忆录》（Lorenzo da Ponte's Memoirs）"
name_en: "Lorenzo da Ponte's Memoirs"
type: archive
evidence_status: source_backed
sub_type: book
sources:
  - citation: "{citation}"
    location: 第15章印刷页368注4，L101。
    sentence_summary: Haskell cites Lorenzo da Ponte, page 52, for the account of Memmo's open house.
    original_quotes:
      - source_span: printed p.368, note 4, L101
        text: "4 Lorenzo da Ponte, p. 52."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/15_CHP-15_sec_ii.md
      source_span: printed p.368, note 4, L101
  - citation: "{citation}"
    location: 第21章印刷页434，书目 L988。
    sentence_summary: The bibliography gives the author form, title, place, and year; the page image reads 1960.
    original_quotes:
      - source_span: printed p.434, L988
        text: "Ponte, Lorenzo da: Memorie, Milano i960."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/21_CHP-21Bibliography.md
      source_span: printed p.434, L988
created: '2026-10-25'
updated: '2026-10-25'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 本卡记录 Haskell 第15章印刷页368注4所引的 Lorenzo da Ponte《Memorie》书目身份。第21章印刷页434将作者倒置著录为“Ponte, Lorenzo da”，并列出版地 Milano 和年份 1960；页图校读确认 OCR 的“i960”为“1960”。中文题名及英文 Memoirs 为描述性工作译名，非原书正式译名。该书及注中第52页均未独立查阅。

**English:** This card records the bibliographic identity of Lorenzo da Ponte's *Memorie*, cited in Haskell's chapter 15, page 368, note 4. The chapter 21 bibliography inverts the author name as “Ponte, Lorenzo da” and lists Milano and 1960; the page image confirms that OCR “i960” reads “1960.” “Memoirs” is a descriptive English rendering, not claimed as the publication's official English title. Neither the book nor the cited page 52 was independently consulted.

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 作者（书目形式） | Ponte, Lorenzo da | S1：Haskell，第21章印刷页434，书目 L988；印本页图将OCR i960校读为1960。 |
| 原书所录题名 | Memorie | S1：Haskell，第21章印刷页434，书目 L988；印本页图将OCR i960校读为1960。 |
| 出版地 | Milano | S1：Haskell，第21章印刷页434，书目 L988；印本页图将OCR i960校读为1960。 |
| 出版年 | 1960 | S1：Haskell，第21章印刷页434，书目 L988；印本页图将OCR i960校读为1960。 |
| 文献类型 | book（书目记录） | S1：Haskell，第21章印刷页434，书目 L988；印本页图将OCR i960校读为1960。 |

### 本章相关内容

Haskell cites page 52 for his account of Memmo's open house. The note records a citation only and does not establish what that page says.

**English:** Haskell cites page 52 for his account of Memmo's open house. The note records a citation only and does not establish what that page says.

## 关系与证据

### 身份与外部链接

Cross-chapter S3 group `archive-group-7e201dbe015a`; the note form and bibliography entry identify one source-local publication. No external catalogue or copy was consulted.

### 关系记录

'''
    person = f'''---
title: "洛伦佐·达·蓬特（Lorenzo da Ponte）"
name_en: "Lorenzo da Ponte"
type: person
evidence_status: source_backed
sources:
  - citation: "{citation}"
    location: 第15章印刷页368注4，L101。
    sentence_summary: The note gives the author name as Lorenzo da Ponte in a short-form citation.
    original_quotes:
      - source_span: printed p.368, note 4, L101
        text: "4 Lorenzo da Ponte, p. 52."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/15_CHP-15_sec_ii.md
      source_span: printed p.368, note 4, L101
  - citation: "{citation}"
    location: 第21章印刷页434，书目 L988。
    sentence_summary: The bibliography prints the inverted author form “Ponte, Lorenzo da” for Memorie.
    original_quotes:
      - source_span: printed p.434, L988
        text: "Ponte, Lorenzo da: Memorie, Milano i960."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/21_CHP-21Bibliography.md
      source_span: printed p.434, L988
created: '2026-10-25'
updated: '2026-10-25'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 本卡仅记录 Haskell 第15章注4与第21章书目中用于《Memorie》责任者的姓名形式。两处姓名的正序与倒置形式均指向该书的同一书目责任者；本卡不补写生卒、职业、传记或外部身份标识。

**English:** This card records only the name forms Haskell uses for the author of *Memorie* in chapter 15, note 4, and the chapter 21 bibliography. The forward and inverted forms refer to the same bibliographic author of that publication. This card adds no dates, occupation, biography, or external identity identifier.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 书内正序姓名形式 | Lorenzo da Ponte | S1：Haskell，第15章印刷页368注4 L101；第21章印刷页434书目 L988。仅记书内姓名形式。 |
| 书目倒置姓名形式 | Ponte, Lorenzo da | S1：Haskell，第15章印刷页368注4 L101；第21章印刷页434书目 L988。仅记书内姓名形式。 |

## 关系与证据

### 身份与外部链接

This is a source-local person identity grouped from the chapter 15 note and chapter 21 author form. No external identity record was consulted or asserted.

### 关系记录

'''
    return {
        ARCHIVE_NEU_PATH: neu.encode("utf-8"),
        ARCHIVE_DAP_PATH: dap.encode("utf-8"),
        PERSON_DAP_PATH: person.encode("utf-8"),
    }


def preflight():
    for rel, expected in EXPECTED_HASHES.items():
        path = ROOT / rel
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"input changed since review: {rel}")

    outputs: dict[Path, bytes] = {}
    candidate_path = TABLES / "entity-candidates.csv"
    c_headers, candidates, c_bom, c_nl = read_csv(candidate_path)
    align_path = TABLES / "alignment.csv"
    a_headers, alignments, a_bom, a_nl = read_csv(align_path)
    mention_path = TABLES / "mentions.csv"
    m_headers, mentions, m_bom, m_nl = read_csv(mention_path)
    backlog_path = TABLES / "candidate-backlog.csv"
    b_headers, backlog, b_bom, b_nl = read_csv(backlog_path)
    manifest_path = TABLES / "ku-manifest.csv"
    k_headers, manifest, k_bom, k_nl = read_csv(manifest_path)
    relation_path = TABLES / "relations.csv"
    r_headers, relations, r_bom, r_nl = read_csv(relation_path)

    by_candidate = {r["candidate_id"]: r for r in candidates}
    for cid, group in (("cand-10479", "archive-group-c8faf880aceb"),
                       ("cand-10513", "archive-group-7e201dbe015a")):
        row = by_candidate.get(cid)
        if not row or row.get("suggested_type") != "archive":
            raise SystemExit(f"expected S3 archive candidate missing: {cid}")
        matches = [r for r in alignments if r.get("candidate_id") == cid]
        if len(matches) != 1 or matches[0].get("decision") != "new" or matches[0].get("ku_id"):
            raise SystemExit(f"candidate is not an unmapped S3 new group: {cid}")
        if f"group={group}" not in matches[0].get("resolution_note", ""):
            raise SystemExit(f"unexpected S3 identity group for {cid}")
    if any(r.get("canonical_name", "").casefold() == "lorenzo da ponte"
           and r.get("suggested_type") == "person" for r in candidates):
        raise SystemExit("source-local Lorenzo da Ponte person candidate already exists")
    if any(r.get("ku_id") in (ARCHIVE_NEU_ID, ARCHIVE_DAP_ID, PERSON_DAP_ID) for r in manifest):
        raise SystemExit("planned KU already exists in manifest")
    for card_path, expected in EXPECTED_EXISTING_CARD_HASHES.items():
        path = ROOT / card_path
        if not path.is_file() or sha(path.read_bytes()) != expected:
            raise SystemExit(f"unexpected pre-existing draft card: {card_path}")

    candidate_id = f"cand-{next_number(candidates, 'candidate_id', 'cand-'):05d}"
    alignment_id = f"aln-{next_number(alignments, 'alignment_id', 'aln-'):05d}"
    backlog_id = f"bl-{next_number(backlog, 'backlog_id', 'bl-'):04d}"
    next_enr = next_number(
        [json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()],
        "enrichment_id", "enr-",
    )
    next_rel = next_number(relations, "relation_id", "rel-")

    person_candidate = {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": "Lorenzo da Ponte",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The chapter 15 note and chapter 21 bibliography give forward and inverted name forms for the author of Memorie. Register a source-local author identity only; no biography or external identity is asserted.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-15:15_CHP-15_sec_ii:l90-113#L101",
    }
    candidates.append(person_candidate)
    outputs[candidate_path] = write_csv(c_headers, candidates, c_bom, c_nl)

    alignment = {
        "alignment_id": alignment_id,
        "candidate_id": candidate_id,
        "ku_id": PERSON_DAP_ID,
        "external_source": "",
        "external_id": "",
        "decision": "new",
        "accessed_date": "",
        "process_ref": PROCESS_REF,
        "legacy_ku_id": "",
        "resolution_note": (
            f"source_ref=chp-15:15_CHP-15_sec_ii:l90-113#L101 | "
            f"related_bibliography=chp-21:21_CHP-21Bibliography:l985-1020#L988; "
            f"group={S3_PERSON_GROUP}; the note form Lorenzo da Ponte and bibliography form "
            "Ponte, Lorenzo da identify the same source-local author of Memorie; no external identity expansion."
        ),
    }
    alignments.append(alignment)
    for cid, ku_id, group in (
        ("cand-10479", ARCHIVE_NEU_ID, "archive-group-c8faf880aceb"),
        ("cand-10513", ARCHIVE_DAP_ID, "archive-group-7e201dbe015a"),
    ):
        row = next(r for r in alignments if r.get("candidate_id") == cid)
        row["ku_id"] = ku_id
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += (
            f"; S4 registration: mapped {group} to {ku_id}; cited publication not independently consulted."
        )
    outputs[align_path] = write_csv(a_headers, alignments, a_bom, a_nl)

    archive_entry_mention = next(
        (m for m in mentions if m.get("mention_id") == "m-chp21-bib-l985-1020-003"), None
    )
    if not archive_entry_mention or archive_entry_mention.get("start_char") != "228" or archive_entry_mention.get("end_char") != "268":
        raise SystemExit("bibliography entry mention changed; cannot split author and publication spans")
    archive_entry_mention["surface_form"] = "Memorie, Milano i960."
    archive_entry_mention["start_char"] = "247"
    archive_entry_mention["end_char"] = "268"
    archive_entry_mention["note"] = "S0 bibliography title/publication details; the author name is a separate non-overlapping mention."
    new_mentions = [
        {
            "mention_id": "m-chp21-bib-l985-1020-entry-03-author",
            "segment_id": "chp-21:21_CHP-21Bibliography:l985-1020",
            "candidate_id": candidate_id,
            "surface_form": "Ponte, Lorenzo da",
            "start_char": "228",
            "end_char": "245",
            "note": "Author form printed in the Haskell bibliography entry for Memorie.",
        }
    ]
    if {m["mention_id"] for m in new_mentions} & {m["mention_id"] for m in mentions}:
        raise SystemExit("planned mention id already exists")
    mentions.extend(new_mentions)
    outputs[mention_path] = write_csv(m_headers, mentions, m_bom, m_nl)

    backlog.append({
        "backlog_id": backlog_id,
        "canonical_name": "Lorenzo da Ponte",
        "suggested_type": "person",
        "status": "completed",
        "source_id": "haskell-1980-rev-ed",
        "source_ref": "chp-21:21_CHP-21Bibliography:l985-1020#L988",
        "statement_id": "st-chp21-bib-l985-1020-entry-03",
        "endpoint_role": "author of cand-10513",
        "candidate_id": candidate_id,
        "ku_id": PERSON_DAP_ID,
        "decision_note": (
            f"Backlog candidate {candidate_id} was adjudicated as a source-local person group "
            f"{S3_PERSON_GROUP} and registered as {PERSON_DAP_ID}. Haskell's chapter 15 note and "
            "chapter 21 author form support the attribution; no biography or external identity is asserted."
        ),
        "process_ref": PROCESS_REF,
    })
    outputs[backlog_path] = write_csv(b_headers, backlog, b_bom, b_nl)

    manifest.extend([
        {"ku_id": ARCHIVE_NEU_ID, "type": "archive", "canonical_name": "《普拉托·德拉·瓦莱图说，或帕多瓦雕像广场图说》（Illustration of the Prato della Valle, or the Piazza of the Statues of Padua）", "name_en": "Illustration of the Prato della Valle, or the Piazza of the Statues of Padua", "source_task": "patrons-and-painters-full-book-s2", "card_path": ARCHIVE_NEU_PATH},
        {"ku_id": ARCHIVE_DAP_ID, "type": "archive", "canonical_name": "《洛伦佐·达·蓬特回忆录》（Lorenzo da Ponte's Memoirs）", "name_en": "Lorenzo da Ponte's Memoirs", "source_task": "patrons-and-painters-full-book-s2", "card_path": ARCHIVE_DAP_PATH},
        {"ku_id": PERSON_DAP_ID, "type": "person", "canonical_name": "洛伦佐·达·蓬特（Lorenzo da Ponte）", "name_en": "Lorenzo da Ponte", "source_task": "patrons-and-painters-full-book-s2", "card_path": PERSON_DAP_PATH},
    ])
    outputs[manifest_path] = write_csv(k_headers, manifest, k_bom, k_nl)

    enrichment_raw = (TABLES / "enrichment.jsonl").read_bytes()
    evidence_neu = "S1：Haskell，第21章印刷页431，书目 L874–875。"
    evidence_dap = "S1：Haskell，第21章印刷页434，书目 L988；印本页图将OCR i960校读为1960。"
    evidence_person = "S1：Haskell，第15章印刷页368注4 L101；第21章印刷页434书目 L988。仅记书内姓名形式。"
    field_groups = [
        (ARCHIVE_NEU_ID, "内容 / 基本信息", [
            ("作者（书目形式）", "Neu-Mayr, A.", evidence_neu),
            ("原书所录题名", "Illustrazione del Prato della Valle ossia della Piazza delle Statue di Padova", evidence_neu),
            ("出版地", "Padova", evidence_neu),
            ("出版年", "1807", evidence_neu),
            ("文献类型", "book（书目记录）", evidence_neu),
        ]),
        (ARCHIVE_DAP_ID, "内容 / 基本信息", [
            ("作者（书目形式）", "Ponte, Lorenzo da", evidence_dap),
            ("原书所录题名", "Memorie", evidence_dap),
            ("出版地", "Milano", evidence_dap),
            ("出版年", "1960", evidence_dap),
            ("文献类型", "book（书目记录）", evidence_dap),
        ]),
        (PERSON_DAP_ID, "内容 / 名称", [
            ("书内正序姓名形式", "Lorenzo da Ponte", evidence_person),
            ("书目倒置姓名形式", "Ponte, Lorenzo da", evidence_person),
        ]),
    ]
    enrichments = []
    current = next_enr
    for ku_id, section, fields in field_groups:
        for i, (field, value, evidence) in enumerate(fields, start=1):
            enrichments.append(make_enrichment(f"enr-{current}", ku_id, section, field, value, evidence, i))
            current += 1
    append_sep = b"" if not enrichment_raw or enrichment_raw.endswith((b"\n", b"\r")) else b"\n"
    outputs[TABLES / "enrichment.jsonl"] = enrichment_raw + append_sep + b"\n".join(
        json.dumps(r, ensure_ascii=False, separators=(",", ":")).encode("utf-8") for r in enrichments
    ) + b"\n"

    new_relations = [
        {
            "relation_id": f"rel-{next_rel:04d}",
            "subject_ku_id": "units/archives/patrons-and-painters",
            "object_ku_id": ARCHIVE_NEU_ID,
            "predicate": "cites",
            "time": "",
            "role": "bibliographic citation",
            "scope": "Haskell第15章印刷页365注2指引读者参见Neu-Mayr以了解Prà della Valle相关雕像与铭文；第21章p.431书目确认书目身份。仅记录书内引注，不表示被引书已查阅。",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 15, printed p.365, note 2, L92; continuation at L12; related bibliography entry: Chapter 21, printed p.431, L874–875; statements=st-chp15-p365-note2-neu-mayr-1807;st-chp21-bib-l846-881-entry-22",
            "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
            "note": "Cross-chapter S3 group archive-group-c8faf880aceb; the cited publication was not independently consulted.",
        },
        {
            "relation_id": f"rel-{next_rel+1:04d}",
            "subject_ku_id": "units/archives/patrons-and-painters",
            "object_ku_id": ARCHIVE_DAP_ID,
            "predicate": "cites",
            "time": "",
            "role": "bibliographic citation",
            "scope": "Haskell第15章印刷页368注4引Lorenzo da Ponte第52页；第21章p.434书目确认《Memorie》及书目责任者。仅记录书内引注与书目身份，不表示该书或第52页已查阅。",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 15, printed p.368, note 4, L101; related bibliography entry: Chapter 21, printed p.434, L988; statements=st-chp15-p368-note4-open-house-reference;st-chp21-bib-l985-1020-entry-03",
            "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
            "note": "Cross-chapter S3 group archive-group-7e201dbe015a; the cited publication and cited page were not independently consulted.",
        },
        {
            "relation_id": f"rel-{next_rel+2:04d}",
            "subject_ku_id": ARCHIVE_DAP_ID,
            "object_ku_id": PERSON_DAP_ID,
            "predicate": "authored_by",
            "time": "",
            "role": "bibliographic author attribution",
            "scope": "Haskell第21章印刷页434书目以“Ponte, Lorenzo da”著录《Memorie》；本关系仅记录书内责任者归属，不作外部身份扩展。",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 21, printed p.434, L988; source-local author form; statement=st-chp21-bib-l985-1020-entry-03",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
            "note": f"Structural authorship relation; person is the source-local S3 group {S3_PERSON_GROUP}; cited book not independently consulted.",
        },
    ]
    natural_keys = {
        tuple(r.get(k, "").strip() for k in ("subject_ku_id", "predicate", "object_ku_id", "time", "role", "scope"))
        for r in relations
    }
    for relation in new_relations:
        key = tuple(relation[k].strip() for k in ("subject_ku_id", "predicate", "object_ku_id", "time", "role", "scope"))
        if key in natural_keys or any(r.get("relation_id") == relation["relation_id"] for r in relations):
            raise SystemExit(f"duplicate planned relation: {relation['relation_id']}")
        natural_keys.add(key)
        relations.append(relation)
    outputs[relation_path] = write_csv(r_headers, relations, r_bom, r_nl)

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_raw = accepted_path.read_bytes()
    accepted_bom = accepted_raw.startswith(b"\xef\xbb\xbf")
    accepted_text = accepted_raw.decode("utf-8-sig")
    additions = [ARCHIVE_NEU_PATH, ARCHIVE_DAP_PATH, PERSON_DAP_PATH]
    for path in additions:
        if f"- {path}" in accepted_text:
            raise SystemExit(f"accepted path already exists: {path}")
    claims = re.search(r"(?m)^claims:\r?$", accepted_text)
    if not claims:
        raise SystemExit("accepted.yml does not have expected units/claims boundary")
    accepted_newline = "\r\n" if "\r\n" in accepted_text else "\n"
    accepted_text = (
        accepted_text[:claims.start()]
        + "".join(f"- {path}{accepted_newline}" for path in additions)
        + accepted_text[claims.start():]
    )
    accepted_bytes = accepted_text.encode("utf-8")
    outputs[accepted_path] = (b"\xef\xbb\xbf" + accepted_bytes) if accepted_bom else accepted_bytes
    outputs.update({ROOT / p: b for p, b in cards().items()})

    preview = {
        "s3": {
            "archive-group-c8faf880aceb": {"candidate": "cand-10479", "decision": "new", "ku_id": ARCHIVE_NEU_ID},
            "archive-group-7e201dbe015a": {"candidate": "cand-10513", "decision": "new", "ku_id": ARCHIVE_DAP_ID},
            S3_PERSON_GROUP: {"candidate": candidate_id, "decision": "new", "identity_scope": "source-local Lorenzo da Ponte author form", "ku_id": PERSON_DAP_ID},
        },
        "mentions_added": [m["mention_id"] for m in new_mentions],
        "s4_kus_added": [ARCHIVE_NEU_ID, ARCHIVE_DAP_ID, PERSON_DAP_ID],
        "s5_fields_added": len(enrichments),
        "s6_candidate_decisions": {"formal_cites": 2, "structural_authorship": 1},
        "backlog": {"id": backlog_id, "status": "completed", "candidate_id": candidate_id},
        "relations": new_relations,
        "outputs": {str(p.relative_to(ROOT)): {"bytes": len(data), "sha256": sha(data)} for p, data in outputs.items()},
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
                rel = str(path.relative_to(ROOT)).replace("\\", "/")
                allowed_hashes = {sha(path.read_bytes())}
                if rel in EXPECTED_PREVIOUS_BACKUP_HASHES:
                    allowed_hashes.add(EXPECTED_PREVIOUS_BACKUP_HASHES[rel])
                if sha(backup.read_bytes()) not in allowed_hashes:
                    raise SystemExit(f"existing backup differs from reviewed baseline: {backup}")
            else:
                shutil.copy2(path, backup)
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".s4tmp")
        temp.write_bytes(data)
        temp.replace(path)
    print(json.dumps({"applied": True, "preview": preview}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
