#!/usr/bin/env python3
"""Apply the guarded p.117–118 Apollo and Daphne endpoint batch."""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s3-s4-s5-s6-chp4-p118-apollo-daphne-20261024"
)
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l218-227"
WORK_KU = "units/works/poussin-apollo-and-daphne-unfinished"
TERM_KU = "units/terms/fertility-sterility-conflict-poussin-theme"
WORK_CARD = "04-knowledge/" + WORK_KU + ".md"
TERM_CARD = "04-knowledge/" + TERM_KU + ".md"
MENTION_ID = "m-chp4-sec-ii-p118-0041"
TERM_PHRASE = "the conflict between fertility and sterility"
WORK_GROUP = "workgrp-d1f1c4a66e6011"
TERM_GROUP = "sg3-term-cand-11669"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "b7ba9c7bff7bf221ec368e9c0c25edca6fad52916636e1fdb43bdc9588a5976c",
    "mentions.csv": "82374ad24ce0935cc47927b3fadc94e46c33cd645af732136c9de8a257747750",
    "alignment.csv": "92ee50712ed8b2fbd0c130e4556ef732154368c226932fae7e0192c9036bd43c",
    "ku-manifest.csv": "e0f8de356ff99635052c4280f167297e9e1abe169c6390c2b32b4234c1bc35f3",
    "enrichment.jsonl": "6639f58d445807435716f494027866ce6705cdaadad6d0603a4a8b0d0a412721",
    "relations.csv": "b838260496a1150b5e1d59df92fcd2ddb7cd30f7bb357031825dd27482dc1d01",
    "accepted.yml": "e13b568a2a19231eb700293245309e5ba2b0910438bcff007aaac93f4a74f249",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_id(prefix: str, value: str) -> str:
    return prefix + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames:
        raise SystemExit(f"missing CSV header: {path}")
    return list(reader.fieldnames), list(reader), bom, newline


def write_csv(
    headers: list[str], rows: list[dict[str, str]], bom: bool, newline: str
) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=headers, extrasaction="ignore", lineterminator=newline
    )
    writer.writeheader()
    writer.writerows(rows)
    content = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + content) if bom else content


def card_table_id(ku_id: str) -> str:
    value = f"{ku_id}|内容 / 基本信息|1|字段|值|证据"
    return "tbl-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def make_enrichment(
    enrichment_id: str, ku_id: str, field: str, value: str, evidence: str
) -> dict:
    citation = (
        "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
        "(New Haven and London: Yale University Press, 1980; this printing 2006), "
        "ch. 4, p. 118."
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
        "occurrence_id": stable_id("occ-", f"{ku_id}|{field}|{value}"),
        "table_id": card_table_id(ku_id),
        "table_section": "内容 / 基本信息",
        "has_header": True,
        "table_header": ["字段", "值", "证据"],
        "row_index": 1,
        "cells": [field, value, evidence],
        "unit_evidence_status": "source_backed",
    }


def make_work_card() -> str:
    return f"""---
title: "普桑未完成的《阿波罗与达芙妮》（Poussin's unfinished Apollo and Daphne）"
name_en: "Poussin's unfinished Apollo and Daphne"
type: work
evidence_status: source_backed
sources:
- citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 4, pp. 117–118."
  location: 第4章印刷页117–118，OCR L216、L219。
  sentence_summary: >-
    Haskell describes one of Poussin’s late pictures as his last unfinished work, says Poussin gave it to Massimi in 1664, and identifies it on p. 118 as Apollo and Daphne.
  original_quotes:
  - source_span: OCR L216; printed p. 117
    text: "left uncompleted"
  - source_span: OCR L216; printed p. 117
    text: "gave to Massimi in 1664"
  - source_span: OCR L219; printed p. 118
    text: "Apollo and Daphne"
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: {SOURCE_REL}
    source_span: OCR L216, L219; printed pp. 117–118
created: '2026-10-24'
updated: '2026-10-24'
process_ref: {PROCESS_REF}
---

## 内容

### 作品身份

**中文：** 哈斯克尔将《阿波罗与达芙妮》称为普桑晚年画作中最后一件、未完成的作品，并说普桑于1664年将其赠予卡米洛·马西米。本卡记录书内身份和归属陈述；未作外部作者、存世状态或转移历史核验。

**English:** Haskell identifies Apollo and Daphne as the last unfinished picture among Poussin’s late works and says Poussin gave it to Camillo Massimi in 1664. This card records the book’s identification and attribution; authorship, survival, and transfer history have not been independently verified.

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 作品类型 | 绘画（Painting；具体媒材未载） | S1：Haskell，第4章印刷页117–118，L216、L219。 |

### 身份映射

S3身份组 {WORK_GROUP}；来源候选 cand-5988 与索引候选 cand-1992 映射至本卡。

## 关系与证据

### 关系候选入口

[本作品的关系候选及逐项裁决](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp4-p118-apollo-daphne-20261024)
"""


def make_term_card() -> str:
    return f"""---
title: "生育与不育之间的冲突（Conflict between fertility and sterility）"
name_en: "Conflict between fertility and sterility"
type: term
evidence_status: source_backed
sources:
- citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 4, p. 118."
  location: 第4章印刷页118，OCR L219。
  sentence_summary: >-
    Haskell names the conflict between fertility and sterility as a theme summed up in Apollo and Daphne, and says its wealth of classical allusion had not yet been fully interpreted.
  original_quotes:
  - source_span: OCR L219; printed p. 118
    text: "the conflict between fertility and sterility"
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: {SOURCE_REL}
    source_span: OCR L219; printed p. 118
created: '2026-10-24'
updated: '2026-10-24'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 哈斯克尔把“生育与不育之间的冲突”称为普桑长期着迷、并由《阿波罗与达芙妮》所概括的主题；他同时指出，作品中的古典典故尚未完全阐释。本条记录哈斯克尔的来源限定解释，不视为该主题的终局说明。

**English:** Haskell says the conflict between fertility and sterility had long fascinated Poussin and was summed up in Apollo and Daphne. He also says the work’s wealth of classical allusion had not yet been fully interpreted. This unit records Haskell’s source-bounded interpretation, not a final account of the theme.

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 定义与范围 | 哈斯克尔将“生育与不育之间的冲突”作为《阿波罗与达芙妮》的主题解释；作品中的古典典故尚未完全阐释。 | S1：Haskell，第4章印刷页118，L219。 |

### 身份映射

S3身份组 {TERM_GROUP}；来源候选 cand-11669 映射至本卡。

## 关系与证据

### 关系候选入口

[本主题词的关系候选及逐项裁决](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp4-p118-apollo-daphne-20261024)
"""


def prepare() -> dict[Path, bytes]:
    for name, expected in EXPECTED_SHA256.items():
        path = (ROOT / "04-knowledge" / name) if name == "accepted.yml" else (TABLES / name)
        if sha256(path.read_bytes()) != expected:
            raise SystemExit(f"source hash changed; refusing write: {path.relative_to(ROOT)}")
    if sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("Haskell source changed; refusing write")
    for relative in (WORK_CARD, TERM_CARD):
        if (ROOT / relative).exists():
            raise SystemExit(f"new card path already exists: {relative}")

    body_line = SOURCE.read_text(encoding="utf-8-sig").splitlines()[218]
    if TERM_PHRASE not in body_line:
        raise SystemExit("term phrase is absent from source line 219")

    statement_path = TABLES / "book-statements.jsonl"
    statement_text = statement_path.read_text(encoding="utf-8-sig")
    statement_lines = statement_text.splitlines()
    statement_rows = {}
    for index, line in enumerate(statement_lines):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("statement_id") in {
            "st-chp4-sec-ii-p118-apollo-daphne-title",
            "st-chp4-sec-ii-p118-apollo-theme",
            "st-chp4-sec-ii-p118-poussin-fascinated-theme",
        }:
            statement_rows[row["statement_id"]] = (index, row)
    if len(statement_rows) != 3:
        raise SystemExit("expected all three p.118 statements exactly once")

    _, title = statement_rows["st-chp4-sec-ii-p118-apollo-daphne-title"]
    _, theme = statement_rows["st-chp4-sec-ii-p118-apollo-theme"]
    _, fascinated = statement_rows["st-chp4-sec-ii-p118-poussin-fascinated-theme"]
    if "Apollo and Daphne" not in title.get("original_quote", ""):
        raise SystemExit("title statement no longer matches expected source")
    if theme["qualifiers"].get("claim") != (
        "Poussin’s Apollo and Daphne summarizes the conflict between fertility and sterility."
    ):
        raise SystemExit("theme statement changed since review; refusing blind edit")

    title["qualifiers"]["claim"] = (
        "Haskell identifies the unfinished Poussin picture discussed across pp. 117–118 as Apollo and Daphne."
    )
    title["qualifiers"]["linked_statement_ids"] = [
        "st-chp4-sec-ii-p117-unfinished-gift-1664"
    ]
    theme["qualifiers"]["claim"] = (
        "Haskell says the wealth of classical allusion in Apollo and Daphne has not yet been fully "
        "interpreted and that the painting sums up the conflict between fertility and sterility."
    )
    theme["qualifiers"]["linked_statement_ids"] = [
        "st-chp4-sec-ii-p118-apollo-daphne-title"
    ]
    theme["original_quote"] = body_line
    fascinated["qualifiers"]["claim"] = (
        "Haskell says the conflict between fertility and sterility had long fascinated Poussin."
    )
    fascinated["qualifiers"]["qualification"] = (
        "The p.118 pronoun “him” refers to Poussin, identified in the linked p.117 account of his last unfinished picture."
    )
    fascinated["qualifiers"]["linked_statement_ids"] = [
        "st-chp4-sec-ii-p117-unfinished-gift-1664",
        "st-chp4-sec-ii-p118-apollo-daphne-title",
    ]
    fascinated["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-1984", "cand-5988", "cand-11669"
    ]
    fascinated["original_quote"] = body_line
    for statement_id, (index, row) in statement_rows.items():
        statement_lines[index] = json.dumps(row, ensure_ascii=False)
    outputs: dict[Path, bytes] = {
        statement_path: ("\n".join(statement_lines) + "\n").encode("utf-8")
    }

    mention_path = TABLES / "mentions.csv"
    mention_headers, mentions, mention_bom, mention_newline = read_csv(mention_path)
    if any(row["mention_id"] == MENTION_ID for row in mentions):
        raise SystemExit(f"mention ID already exists: {MENTION_ID}")
    segment_text = "\n".join(
        SOURCE.read_text(encoding="utf-8-sig").splitlines()[217:227]
    )
    start = segment_text.index(TERM_PHRASE)
    mentions.append({
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-11669",
        "surface_form": TERM_PHRASE,
        "start_char": str(start),
        "end_char": str(start + len(TERM_PHRASE)),
        "note": "哈斯克尔明确点名的生育/不育主题；记录其来源限定解释，不作终局阐释。",
    })
    outputs[mention_path] = write_csv(
        mention_headers, mentions, mention_bom, mention_newline
    )

    alignment_path = TABLES / "alignment.csv"
    align_headers, alignments, align_bom, align_newline = read_csv(alignment_path)
    alignment_by_candidate = {row["candidate_id"]: row for row in alignments}
    expected_decisions = {
        "cand-5988": "new",
        "cand-1992": "undecided",
        "cand-11669": "undecided",
    }
    for candidate_id, decision in expected_decisions.items():
        row = alignment_by_candidate.get(candidate_id)
        if row is None or row["decision"] != decision or row["ku_id"]:
            raise SystemExit(f"unexpected S3 row for {candidate_id}")
    alignment_by_candidate["cand-5988"]["ku_id"] = WORK_KU
    index_row = alignment_by_candidate["cand-1992"]
    index_row.update({
        "ku_id": WORK_KU,
        "decision": "new",
        "process_ref": PROCESS_REF,
        "resolution_note": (
            f"source_ref=entity-candidates.csv#cand-1992; index_entry=P.csv#195; "
            f"index_sub_entry=Apollo and Daphne; matched to cand-5988 and "
            f"{SEGMENT_ID}#{MENTION_ID}; same book-described Poussin painting, not a separate work; "
            f"group={WORK_GROUP}; new KU. No external identity claim."
        ),
    })
    term_row = alignment_by_candidate["cand-11669"]
    term_row.update({
        "ku_id": TERM_KU,
        "decision": "new",
        "process_ref": PROCESS_REF,
        "resolution_note": (
            f"group={TERM_GROUP}; source_ref={SEGMENT_ID}#L219; mentions={MENTION_ID}; "
            "direct text anchor names one source-specific theme; no existing matching term KU; "
            "new. Retain Haskell's interpretive and incompletely interpreted framing."
        ),
    })
    alignment_by_candidate["cand-5988"]["process_ref"] = PROCESS_REF
    outputs[alignment_path] = write_csv(
        align_headers, alignments, align_bom, align_newline
    )

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_headers, manifest_rows, manifest_bom, manifest_newline = read_csv(manifest_path)
    if any(row["ku_id"] in {WORK_KU, TERM_KU} for row in manifest_rows):
        raise SystemExit("new KU ID already exists in manifest")
    manifest_rows.extend([
        {
            "ku_id": WORK_KU,
            "type": "work",
            "canonical_name": "普桑未完成的《阿波罗与达芙妮》",
            "name_en": "Poussin's unfinished Apollo and Daphne",
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": WORK_CARD,
        },
        {
            "ku_id": TERM_KU,
            "type": "term",
            "canonical_name": "生育与不育之间的冲突",
            "name_en": "Conflict between fertility and sterility",
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": TERM_CARD,
        },
    ])
    outputs[manifest_path] = write_csv(
        manifest_headers, manifest_rows, manifest_bom, manifest_newline
    )

    enrichment_path = TABLES / "enrichment.jsonl"
    enrichment_lines = enrichment_path.read_text(encoding="utf-8-sig").splitlines()
    enrichment_rows = [json.loads(line) for line in enrichment_lines if line.strip()]
    existing_ids = {row["enrichment_id"] for row in enrichment_rows}
    if {"enr-16716", "enr-16717"} & existing_ids:
        raise SystemExit("planned enrichment ID already exists")
    work_value = "绘画（Painting；具体媒材未载）"
    work_evidence = "S1：Haskell，第4章印刷页117–118，L216、L219。"
    term_value = (
        "哈斯克尔将“生育与不育之间的冲突”作为《阿波罗与达芙妮》的主题解释；"
        "作品中的古典典故尚未完全阐释。"
    )
    term_evidence = "S1：Haskell，第4章印刷页118，L219。"
    new_enrichments = [
        make_enrichment("enr-16716", WORK_KU, "作品类型", work_value, work_evidence),
        make_enrichment("enr-16717", TERM_KU, "定义与范围", term_value, term_evidence),
    ]
    outputs[enrichment_path] = (
        ("\n".join(enrichment_lines + [
            json.dumps(row, ensure_ascii=False, separators=(",", ":"))
            for row in new_enrichments
        ]) + "\n").encode("utf-8")
    )

    relation_path = TABLES / "relations.csv"
    rel_headers, relations, rel_bom, rel_newline = read_csv(relation_path)
    if any(row["relation_id"] in {"rel-1774", "rel-1775", "rel-1776"} for row in relations):
        raise SystemExit("planned relation ID already exists")
    new_relations = [
        {
            "relation_id": "rel-1774",
            "subject_ku_id": WORK_KU,
            "object_ku_id": "units/persons/nicolas-poussin",
            "predicate": "created_by",
            "time": "",
            "role": "哈斯克尔所述作品归属",
            "scope": "p.117 的“one such”承接普桑晚年画作；p.118 将该未完成作品命名为 Apollo and Daphne。此边仅记录书内作者归属。",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 4, printed pp. 117–118, OCR L216 and L219; statements=st-chp4-sec-ii-p117-unfinished-gift-1664;st-chp4-sec-ii-p118-apollo-daphne-title",
            "source_file": SOURCE_REL,
            "note": "Haskell-reported creator attribution only; no independent authorship verification.",
        },
        {
            "relation_id": "rel-1775",
            "subject_ku_id": WORK_KU,
            "object_ku_id": "units/persons/camillo-massimi",
            "predicate": "acquired_by",
            "time": "1664",
            "role": "受赠者",
            "scope": "Haskell称普桑于1664年临终前将其最后一件未完成作品赠予Massimi；以取得关系记录该赠与，不扩写此后的所有权链。",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 4, printed p. 117, OCR L216; statement=st-chp4-sec-ii-p117-unfinished-gift-1664",
            "source_file": SOURCE_REL,
            "note": "Book-reported gift and recipient; no later ownership or physical survival is inferred.",
        },
        {
            "relation_id": "rel-1776",
            "subject_ku_id": WORK_KU,
            "object_ku_id": TERM_KU,
            "predicate": "has_subject",
            "time": "",
            "role": "哈斯克尔的主题解释",
            "scope": "Haskell says the work sums up the conflict between fertility and sterility, while its classical allusions remain incompletely interpreted.",
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "Chapter 4, printed p. 118, OCR L219; statement=st-chp4-sec-ii-p118-apollo-theme",
            "source_file": SOURCE_REL,
            "note": "Source-level interpretive relation; not a definitive interpretation of the painting.",
        },
    ]
    natural_keys = {
        "|".join(row.get(key, "").strip() for key in (
            "subject_ku_id", "predicate", "object_ku_id", "time", "role", "scope"
        ))
        for row in relations
    }
    for row in new_relations:
        key = "|".join(row[key].strip() for key in (
            "subject_ku_id", "predicate", "object_ku_id", "time", "role", "scope"
        ))
        if key in natural_keys:
            raise SystemExit(f"duplicate S6 natural key: {row['relation_id']}")
        natural_keys.add(key)
    outputs[relation_path] = write_csv(
        rel_headers, relations + new_relations, rel_bom, rel_newline
    )

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted = accepted_path.read_text(encoding="utf-8")
    accepted_paths = [WORK_CARD, TERM_CARD]
    for relative in accepted_paths:
        if relative in accepted:
            raise SystemExit(f"accepted path already exists: {relative}")
    import re

    claims_match = re.search(r"(?m)^claims:\s*$", accepted)
    if not claims_match:
        raise SystemExit("accepted.yml units/claims boundary not found")
    prefix = accepted[:claims_match.start()].rstrip("\n")
    accepted = (
        prefix
        + "\n"
        + "\n".join(f"- {relative}" for relative in accepted_paths)
        + "\n\n"
        + accepted[claims_match.start():]
    )
    outputs[accepted_path] = accepted.encode("utf-8")
    outputs[ROOT / WORK_CARD] = make_work_card().encode("utf-8")
    outputs[ROOT / TERM_CARD] = make_term_card().encode("utf-8")
    return outputs


def apply(outputs: dict[Path, bytes]) -> None:
    originals = {path: path.read_bytes() for path in outputs if path.exists()}
    recovery = Path(tempfile.mkdtemp(prefix="pnp-apollo-daphne-"))
    staged: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        manifest = []
        for index, (path, content) in enumerate(outputs.items()):
            backup = recovery / f"original-{index}.bin"
            if path in originals:
                backup.write_bytes(originals[path])
            temporary = path.with_name(f".{path.name}.apollo-{index}.tmp")
            temporary.write_bytes(content)
            staged[path] = temporary
            manifest.append({
                "path": path.relative_to(ROOT).as_posix(),
                "had_original": path in originals,
                "output_sha256": sha256(content),
            })
        (recovery / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        for path in outputs:
            if path.exists() and path.read_bytes() != originals.get(path):
                raise RuntimeError(f"target changed after dry-run: {path}")
            if not path.exists() and path in originals:
                raise RuntimeError(f"target disappeared after dry-run: {path}")
        for path, temporary in staged.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary.replace(path)
            replaced.append(path)
        for path, content in outputs.items():
            if path.read_bytes() != content:
                raise RuntimeError(f"post-write byte verification failed: {path}")
    except BaseException:
        for path in reversed(replaced):
            if path in originals:
                restore = path.with_name(f".{path.name}.restore.tmp")
                restore.write_bytes(originals[path])
                restore.replace(path)
            else:
                path.unlink(missing_ok=True)
        shutil.rmtree(recovery, ignore_errors=True)
        raise
    else:
        shutil.rmtree(recovery)


def main() -> int:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="apply the guarded table and card updates")
    args = parser.parse_args()
    outputs = prepare()
    print(f"preflight passed: {len(outputs)} files in scope")
    for path, content in outputs.items():
        relative = path.relative_to(ROOT).as_posix()
        old = path.read_bytes() if path.exists() else b""
        state = "create" if not path.exists() else "update"
        print(f"{state}: {relative}; {sha256(old)[:12]} -> {sha256(content)[:12]}")
        if path.name in {"book-statements.jsonl", "alignment.csv", "relations.csv"}:
            diff = difflib.unified_diff(
                old.decode("utf-8-sig").splitlines(),
                content.decode("utf-8-sig").splitlines(),
                fromfile="current",
                tofile="planned",
                lineterm="",
            )
            preview = list(diff)
            if preview:
                print("\n".join(preview[:48]))
    if args.apply:
        apply(outputs)
        print(f"apply complete: {len(outputs)} files; written bytes verified")
    else:
        print("dry-run only; no files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
