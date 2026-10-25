#!/usr/bin/env python3
"""Guarded S4/S5/S6 registration for Haskell's report of the 1646 Romanelli letter."""
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

import yaml

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
TASK = "patrons-and-painters-full-book-s2"
ANCHOR = "s4-s5-s6-chp7-romanelli-barberini-letter-20261025"
PROCESS_REL = f"03-processing/{TASK}/process/knowledge.md"
RECOVERY_REL = "06-runtime/recovery/s4-s5-s6-chp7-romanelli-barberini-letter-20261025"

CANDIDATE_ID = "cand-7073"
ALIGNMENT_ID = "aln-7249"
GROUP = "archive-group-3dbb7c123061"
KU_ID = "units/archives/romanelli-letter-to-francesco-barberini-1646-07-06"
CARD_REL = "04-knowledge/units/archives/romanelli-letter-to-francesco-barberini-1646-07-06.md"
TITLE = "罗马内利致弗朗切斯科·巴贝里尼书信（Letter from Giovan Francesco Romanelli to Francesco Barberini, 6 July 1646）"
NAME_EN = "Letter from Giovan Francesco Romanelli to Francesco Barberini, 6 July 1646"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SOURCE_BOOK_KU = "units/archives/patrons-and-painters"
AUTHOR_KU = "units/persons/romanelli"
ADDRESSEE_KU = "units/persons/francesco-barberini"
AUTHOR_CANDIDATE = "cand-2208"
ADDRESSEE_CANDIDATE = "cand-0203"
AUTHOR_STATEMENT = "st-chp7-p181-n4-letter-authored-by"
ADDRESSEE_STATEMENT = "st-chp7-p181-n4-letter-addressed-to"
EXPECTED_QUOTE = "4 Letter from Romanelli to Francesco Barberini of 6 July 1646—Pollak, 1913, p. 52."

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "7bc213a5894ec74a11440fbbd02019a3f97ea0dfc9c38609ed2ab536fcf289f2",
    "04-knowledge/tables/alignment.csv": "1f7b69059d4e9671e2800024a5724776dce21145cd3f73d4e7006af2d76d52a3",
    "04-knowledge/tables/ku-manifest.csv": "1a4a0b8aefce3db134748ea5bd4705fb0e295847d1be79ebc805890aecd08e50",
    "04-knowledge/tables/relations.csv": "ca159bc42d35c48b5f75331ba582323bbd4d4acd9f924f80b9d005eb092a84a1",
    "04-knowledge/tables/book-statements.jsonl": "6632f474de3d0f84f432f9ae9efc447adb27016c94e85bb3af5c243181520f67",
    "04-knowledge/tables/sources.csv": "eb980bfe15f86b7871359ee419cdfc40ba4df1324477356807f000f3a78e122e",
    "04-knowledge/accepted.yml": "9dce568b41654ac4985c23cd831b85dd7e60d7cedf60de0f65b697d4a5d56dbb",
    PROCESS_REL: "75640de464b80afaf1368cbe3430b1edec44d2763d66dd27f2bf1b9b035e12c2",
    SOURCE_FILE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}


def digest(data: bytes) -> str:
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
    payload = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if bom else payload


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def next_relation_ids(rows: list[dict[str, str]]) -> tuple[str, str]:
    last = max(
        (int(row["relation_id"][4:]) for row in rows
         if row.get("relation_id", "").startswith("rel-") and row["relation_id"][4:].isdigit()),
        default=0,
    )
    return f"rel-{last + 1:04d}", f"rel-{last + 2:04d}"


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in lines):
        raise SystemExit(f"accepted.yml already contains {CARD_REL}")
    candidates = [i for i, line in enumerate(lines)
                  if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL]
    at = candidates[0] if candidates else next((i for i, line in enumerate(lines) if line == "claims:"), len(lines))
    lines.insert(at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def make_card() -> str:
    return f'''---
title: '{TITLE}'
name_en: '{NAME_EN}'
type: archive
sub_type: letter
created: '2026-10-25'
updated: '2026-10-25'
evidence_status: source_backed
sources:
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第7章，印刷页181注4，Markdown L342；CHP-7.pdf物理页15。'
    sentence_summary: '注4称为Romanelli致Francesco Barberini、日期为1646年7月6日的信，并给出Pollak 1913年第52页定位；原信及该书页未独立查阅。'
    original_quotes:
      - source_span: 'line 342; printed p. 181, note 4; CHP-7.pdf physical page 15'
        text: '{EXPECTED_QUOTE}'
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SOURCE_FILE}
      source_span: 'line 342; printed p. 181, note 4; CHP-7.pdf physical page 15'
process_ref: {PROCESS_REL}#{ANCHOR}
---

## 内容

### 描述

**中文：** 本卡依哈斯克尔第7章印刷页181注4，登记其所报告的罗马内利致弗朗切斯科·巴贝里尼书信，日期为1646年7月6日。注释给出Pollak（1913）第52页定位。卡片记录的是哈斯克尔对该信的识别与引注；未独立查阅Pollak该页、信件刊本或原件。中文题名为描述性工作译名。

**English:** This card records the letter from Romanelli to Francesco Barberini dated 6 July 1646, as identified in Haskell’s Chapter 7, p. 181, note 4. The note gives a locator to Pollak (1913), p. 52. This unit records Haskell’s identification and citation; Pollak’s page, any printed transcription, and the original letter were not independently consulted. The Chinese title is descriptive.

### 文献身份与定位

| 字段 | 内容 | 依据 |
|---|---|---|
| 文献类型 | 书信 | S1；第7章，印刷页181注4，L342 |
| 书内日期 | 6 July 1646 | S1；第7章，印刷页181注4，L342 |
| 书内作者 | Romanelli | S1；第7章，印刷页181注4，L342 |
| 书内收信人 | Francesco Barberini | S1；第7章，印刷页181注4，L342 |
| 书内引注定位 | Pollak, 1913, p. 52（Haskell注释所给定位，未独立核实） | S1；第7章，印刷页181注4，L342 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|

### 身份与外部链接

S3身份组 `{GROUP}` 的`new`候选 `{CANDIDATE_ID}` 映射至本KU。文中注4只以Romanelli姓氏指称作者；候选全名及人物身份沿用既有跨章S3对齐至 [{AUTHOR_KU}](../persons/romanelli.md)。收信人复用 [{ADDRESSEE_KU}](../persons/francesco-barberini.md)。未据此增加外部身份标识。
'''


def validate_and_plan():
    for rel, expected in EXPECTED_HASHES.items():
        path = ROOT / rel
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise SystemExit(f"baseline changed; refusing to apply: {rel}")

    candidate_fields, candidates, _, _ = read_csv(TABLES / "entity-candidates.csv")
    candidate_rows = [row for row in candidates if row.get("candidate_id") == CANDIDATE_ID]
    if len(candidate_rows) != 1 or candidate_rows[0].get("suggested_type") != "archive":
        raise SystemExit("expected one archive candidate cand-7073")
    if candidate_rows[0].get("canonical_name") != (
        "Letter from Giovan Francesco Romanelli to Cardinal Francesco Barberini "
        "(1646-07-06; cited in Pollak 1913, p.52)"
    ):
        raise SystemExit("candidate identity text changed")

    align_path = TABLES / "alignment.csv"
    align_fields, alignments, align_bom, align_nl = read_csv(align_path)
    target_rows = [row for row in alignments if row.get("candidate_id") == CANDIDATE_ID]
    if len(target_rows) != 1:
        raise SystemExit(f"expected one alignment for {CANDIDATE_ID}; got {len(target_rows)}")
    target_alignment = target_rows[0]
    if (target_alignment.get("alignment_id") != ALIGNMENT_ID or target_alignment.get("decision") != "new"
            or target_alignment.get("ku_id")):
        raise SystemExit("expected the current S3 new decision with no S4 mapping")
    if f"group={GROUP}" not in target_alignment.get("resolution_note", ""):
        raise SystemExit("expected S3 archive group is missing")
    group_members = {row["candidate_id"] for row in alignments
                     if row.get("decision") == "new" and f"group={GROUP}" in row.get("resolution_note", "")}
    if group_members != {CANDIDATE_ID}:
        raise SystemExit(f"unexpected group members: {sorted(group_members)}")

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest, manifest_bom, manifest_nl = read_csv(manifest_path)
    if any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest):
        raise SystemExit("target KU is already in the manifest")
    if any(row.get("name_en", "").casefold() == NAME_EN.casefold()
           for row in manifest if row.get("type") == "archive"):
        raise SystemExit("a matching archive title is already registered")
    for ku_id, expected_type in ((AUTHOR_KU, "person"), (ADDRESSEE_KU, "person"),
                                 (SOURCE_BOOK_KU, "archive")):
        rows = [row for row in manifest if row.get("ku_id") == ku_id]
        if len(rows) != 1 or rows[0].get("type") != expected_type:
            raise SystemExit(f"missing or mistyped endpoint KU: {ku_id}")
    for row in manifest:
        if row.get("ku_id") in {AUTHOR_KU, ADDRESSEE_KU, SOURCE_BOOK_KU}:
            if not (ROOT / row["card_path"]).is_file():
                raise SystemExit(f"endpoint card missing: {row['card_path']}")
    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"target card already exists: {CARD_REL}")

    source_rows = [row for row in read_csv(TABLES / "sources.csv")[1]
                   if row.get("source_id") == SOURCE_ID]
    if len(source_rows) != 1:
        raise SystemExit("Haskell source registry entry is missing or duplicated")

    statements = [json.loads(line) for line in
                  (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    endpoint_candidates = [statement for statement in statements
                           if (statement.get("qualifiers") or {}).get("relation_candidate") is True
                           and CANDIDATE_ID in (statement.get("subject_candidate_id"),
                                                statement.get("object_candidate_id"))]
    by_id = {statement.get("statement_id"): statement for statement in endpoint_candidates}
    if set(by_id) != {AUTHOR_STATEMENT, ADDRESSEE_STATEMENT} or len(endpoint_candidates) != 2:
        raise SystemExit(f"expected exactly the two known S6 candidates, found {sorted(by_id)}")
    for statement_id, other_candidate, predicate in (
        (AUTHOR_STATEMENT, AUTHOR_CANDIDATE, "letter_authored_by"),
        (ADDRESSEE_STATEMENT, ADDRESSEE_CANDIDATE, "letter_addressed_to"),
    ):
        statement = by_id[statement_id]
        qualifiers = statement.get("qualifiers") or {}
        if (statement.get("subject_candidate_id") != CANDIDATE_ID
                or statement.get("object_candidate_id") != other_candidate
                or statement.get("predicate") != predicate
                or statement.get("original_quote") != EXPECTED_QUOTE
                or statement.get("source_file") != SOURCE_FILE
                or qualifiers.get("source_line_start") != 342
                or qualifiers.get("source_line_end") != 342
                or qualifiers.get("printed_page") != 181
                or qualifiers.get("date") != "1646-07-06"
                or qualifiers.get("footnote_link_status") != "linked"
                or qualifiers.get("footnote_text_pending") is not False):
            raise SystemExit(f"source-backed relation candidate changed: {statement_id}")

    types = yaml.safe_load((ROOT / ".agents/skills/ingest/references/relation-types.yml").read_text(encoding="utf-8"))
    ranges = yaml.safe_load((ROOT / "01-domain/relation-domain-range.yml").read_text(encoding="utf-8"))
    for predicate, domain_type, range_type in (("authored_by", "archive", "person"),
                                                ("addressed_to", "archive", "person")):
        if predicate not in types.get("types", []):
            raise SystemExit(f"predicate is not controlled: {predicate}")
        specification = (ranges.get("domain_range") or {}).get(predicate)
        if specification and (domain_type not in specification.get("domain", [])
                              or range_type not in specification.get("range", [])):
            raise SystemExit(f"domain/range mismatch for {predicate}: {domain_type}->{range_type}")

    relation_path = TABLES / "relations.csv"
    relation_fields, relations, relation_bom, relation_nl = read_csv(relation_path)
    if any(underlying in row.get("source_span", "") for row in relations
           for underlying in (AUTHOR_STATEMENT, ADDRESSEE_STATEMENT)):
        raise SystemExit("a target statement already has an S6 table record")
    pairs = {(row.get("subject_ku_id"), row.get("predicate"), row.get("object_ku_id"))
             for row in relations}
    if ((KU_ID, "authored_by", AUTHOR_KU) in pairs
            or (KU_ID, "addressed_to", ADDRESSEE_KU) in pairs):
        raise SystemExit("a target relation already exists")
    author_relation_id, addressee_relation_id = next_relation_ids(relations)
    if any(row.get("relation_id") in {author_relation_id, addressee_relation_id} for row in relations):
        raise SystemExit("allocated relation ID collision")

    new_manifest = list(manifest) + [{
        "ku_id": KU_ID, "type": "archive", "canonical_name": TITLE,
        "name_en": NAME_EN, "source_task": TASK, "card_path": CARD_REL,
    }]
    new_relations = list(relations) + [
        {
            "relation_id": author_relation_id, "subject_ku_id": KU_ID, "object_ku_id": AUTHOR_KU,
            "predicate": "authored_by", "time": "1646-07-06", "role": "author",
            "scope": "Haskell第7章印刷页181注4明称该信为Romanelli致Francesco Barberini，日期为1646年7月6日。本边只记录哈斯克尔对书信作者的报告；Pollak第52页、刊本及原信均未独立查阅。",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID,
            "source_span": f"Chapter 7, printed p.181, note 4, L342; statement={AUTHOR_STATEMENT}",
            "source_file": SOURCE_FILE,
            "note": "The author is reported as Romanelli in Haskell's footnote; the full name follows the existing cross-chapter S3 person alignment. The cited Pollak page and letter were not independently consulted.",
        },
        {
            "relation_id": addressee_relation_id, "subject_ku_id": KU_ID, "object_ku_id": ADDRESSEE_KU,
            "predicate": "addressed_to", "time": "1646-07-06", "role": "addressee",
            "scope": "Haskell第7章印刷页181注4明称该信致Francesco Barberini，日期为1646年7月6日。本边只记录哈斯克尔对收信人的报告；Pollak第52页、刊本及原信均未独立查阅。",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID,
            "source_span": f"Chapter 7, printed p.181, note 4, L342; statement={ADDRESSEE_STATEMENT}",
            "source_file": SOURCE_FILE,
            "note": "The recipient is explicitly named in Haskell's footnote. The cited Pollak page and letter were not independently consulted.",
        },
    ]

    alignments = [dict(row) for row in alignments]
    target_alignment = next(row for row in alignments if row.get("candidate_id") == CANDIDATE_ID)
    target_alignment["ku_id"] = KU_ID
    target_alignment["resolution_note"] += (
        f" S4 registration: mapped {GROUP} to {KU_ID}; the S2 anchor is Haskell's Chapter 7 p.181 note 4, "
        "which reports the individual letter, author, addressee, date, and Pollak 1913 p.52 locator. "
        "The letter and cited page were not independently consulted."
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

### S4–S5–S6：第7章 p.181 注4，Romanelli致Francesco Barberini书信（2026-10-25）

**证据边界与S3组。** `{CANDIDATE_ID}`沿用S3组`{GROUP}`中的`new`决定（`{ALIGNMENT_ID}`），本批不重开S3。Haskell第7章印刷页181注4（Markdown L342；`CHP-7.pdf`物理页15）写明“Letter from Romanelli to Francesco Barberini of 6 July 1646”，并引Pollak（1913）第52页。此处只足以登记一件被明确区分的书信记录；未独立查阅Pollak该页、刊本或原信，不把它们的内容当作直接核验。作者候选`{AUTHOR_CANDIDATE}`与收信人候选`{ADDRESSEE_CANDIDATE}`分别沿用既有`{AUTHOR_KU}`及`{ADDRESSEE_KU}`人物身份。

**S4登记。** 将`{CANDIDATE_ID}`映射至`{KU_ID}`，新增单件书信KU及卡片，并写入accepted、manifest。名称中的Romanelli全名遵循其既有跨章S3对齐；注4原文仅用姓氏。未添加外部标识或推断Pollak页码以外的出版、馆藏或原件信息。

**S5字段。** 新增5条由同一条书内证据支持的字段：文献类型、书内日期、书内作者、书内收信人、书内引注定位。引注定位仅照录“Pollak, 1913, p. 52”；未据此扩写书目全名或断言已查阅刊本。

**S6逐条裁决。** `{AUTHOR_STATEMENT}`裁决为formal，登记`{author_relation_id} authored_by`（书信→Romanelli）；`{ADDRESSEE_STATEMENT}`裁决为formal，登记`{addressee_relation_id} addressed_to`（书信→Francesco Barberini）。两条边均以Haskell第7章p.181注4为证，时间按注释明确报告的1646-07-06保存，分别保留author与addressee角色。两种谓词及archive→person端点均符合受控词表和domain/range。Pollak第52页的刊载关系属于另一个未核实问题：当前没有对应的S2 relation_candidate，且该页未查阅；暂不建立formal关系，也不计入本批两项S6裁决，待获得该页证据后再评估。

本批不改S2 statement、mention或独立复核分子；S6只对上列两条relation_candidate作出formal裁决。
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
    return files, (author_relation_id, addressee_relation_id), (len(manifest), len(new_manifest), len(relations), len(new_relations))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    files, relation_ids, counts = validate_and_plan()
    print(f"S4/S5/S6 plan: {GROUP} -> {KU_ID}")
    print(f"S6: {AUTHOR_STATEMENT} -> {relation_ids[0]} authored_by; {ADDRESSEE_STATEMENT} -> {relation_ids[1]} addressed_to")
    print(f"manifest: {counts[0]} -> {counts[1]}; relations: {counts[2]} -> {counts[3]}; S5 source-backed fields queued: 5")
    print(f"files planned: {len(files)}; S2 tables and independent-review counts unchanged")
    if args.dry_run:
        print("DRY RUN passed; no files changed")
        return 0

    recovery_root = ROOT / RECOVERY_REL
    if recovery_root.exists():
        raise SystemExit(f"recovery path already exists; refusing to overwrite: {RECOVERY_REL}")
    recovery_root.mkdir(parents=True)
    backups: list[tuple[Path, Path]] = []
    created: list[Path] = []
    try:
        for path in files:
            if path.exists():
                backup = recovery_root / "original" / path.relative_to(ROOT)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup)
                backups.append((path, backup))
            else:
                created.append(path)
        for path, data in files.items():
            atomic_write(path, data)
    except BaseException:
        for path, backup in reversed(backups):
            atomic_write(path, backup.read_bytes())
        for path in created:
            path.unlink(missing_ok=True)
        raise
    print(f"APPLIED; recovery snapshot: {RECOVERY_REL}; backed up {len(backups)} existing files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
