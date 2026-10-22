from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.build_field_facts import assign_ids, extract_records  # noqa: E402

TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SOURCE_ID = "haskell-1980-rev-ed"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s3-s4-s5-s6-chp7-p175-baglione-muses-20261023"
)
CANDIDATE = "cand-6693"
ALIGNMENT = "aln-6870"
GROUP = "workgrp-" + hashlib.sha256(
    b"cand-6693|ten-pictures-apollo-muses-baglione-rome"
).hexdigest()[:14]
KU_ID = "units/works/ten-pictures-apollo-muses-baglione-rome"
CARD_PATH = "04-knowledge/units/works/ten-pictures-apollo-muses-baglione-rome.md"
RICHELIEU = "units/persons/armand-jean-du-plessis-de-richelieu"
STATEMENTS = {
    "st-chp7-p175-i17": ("cand-1523", CANDIDATE),
    "st-chp7-p175-i18": ("cand-1631", CANDIDATE),
    "st-chp7-p175-i19": (CANDIDATE, "cand-2189"),
}
ANCHOR = "s3-s4-s5-s6-chp7-p175-baglione-muses-20261023"
SOURCE_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged edition "
    "(Yale University Press, 1980; this printing 2006)."
)
CARD = f'''---
title: "乔瓦尼·巴廖内自罗马带来的阿波罗与缪斯十幅画（Ten pictures of Apollo and the Muses brought from Rome by Giovanni Baglione）"
name_en: "Ten pictures of Apollo and the Muses brought from Rome by Giovanni Baglione"
type: work
evidence_status: source_backed
sources:
  - citation: "{SOURCE_CITATION}"
    location: "Chapter 7, printed p. 175, lines 64–65; PDF physical p. 9"
    sentence_summary: "Haskell reports ten pictures of Apollo and the Muses brought from Rome by Giovanni Baglione a few years earlier, then records Ferdinando’s proposal to send them as a gift."
    original_quotes:
      - source_span: "Chapter 7, printed p. 175, lines 64–65"
        text: "ten pictures of Apollo and the Muses which Giovanni Baglione had brought with him from Rome a few years earlier"
      - source_span: "Chapter 7, printed p. 175, line 64"
        text: "He therefore proposed sending ten pictures"
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SOURCE_FILE}
      source_span: "Chapter 7, printed p. 175, lines 64–65; PDF physical p. 9"
created: '2026-10-23'
updated: '2026-10-23'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 哈斯克尔记载，乔瓦尼·巴廖内几年前从罗马带来十幅以阿波罗与缪斯为题的画作；费迪南多随后提议将这组画作为礼物送出。本知识元只表示原文界定的作品群，不代表已知各单件画作、作者归属或正式题名，也不表示礼物已送达或获接受。

**English:** Haskell reports that Giovanni Baglione had brought ten pictures of Apollo and the Muses from Rome a few years earlier, and that Ferdinando later proposed sending them as a gift. This unit represents only the source-defined group; it does not identify individual pictures, establish their makers or formal titles, or imply that the proposed gift was delivered or accepted.

### 名称与作品信息

| 字段 | 值 | 证据 |
|---|---|---|
| 来源所称作品群 | 十幅以阿波罗与缪斯为题的画作 | S1 |
| 数量 | 十幅 | S1 |
| 来源所称主题 | 阿波罗与缪斯 | S1 |
| 来源所报此前来处 | 乔瓦尼·巴廖内几年前从罗马带来；不据此认定作者 | S1 |
| 个体身份 | 原文未列出十幅画的单件身份、题名或作者 | S1 |
| 礼物状态 | 费迪南多提议送出；送达与接受情况未由该段确认 | S1 |

## 关系与证据

### 身份与外部链接

本作品群按 Haskell 第7章 p.175 的原文范围登记；未将其与《公共幸福战胜危险》或其他已登记作品合并，亦未确认十幅画的外部身份。

### 关系记录

关系记录以 `relations.csv` 中正式边为准；礼物提议及玛丽对画中缪斯形象的要求尚无可准确表达且可证的正式关系谓词，裁决见下方过程记录。

### 关系候选入口

[全书 S2–S6 过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})
'''


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), bom, newline


def render_csv(fields: list[str], rows: list[dict[str, str]], bom: bool, newline: str) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + handle.getvalue().encode("utf-8")


def render_jsonl(rows: list[dict], newline: str = "\n") -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + newline for row in rows).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".codex-tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def accepted_with(card_path: str) -> bytes:
    path = ROOT / "04-knowledge" / "accepted.yml"
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "units:":
        raise ValueError("accepted.yml does not begin with units:")
    existing = {line.strip()[2:].strip() for line in lines if line.lstrip().startswith("-")}
    if card_path in existing:
        raise ValueError(f"accepted.yml already contains {card_path}")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.lstrip().startswith("-") and line.strip()[2:].strip() > card_path),
        next((i for i, line in enumerate(lines) if line.strip() == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_path}{newline}")
    return (b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8")


def required_one(rows: list[dict], key: str, value: str) -> dict:
    found = [row for row in rows if row.get(key) == value]
    if len(found) != 1:
        raise ValueError(f"expected exactly one {key}={value}, found {len(found)}")
    return found[0]


def build_plan() -> dict[Path, bytes]:
    plans: dict[Path, bytes] = {}
    candidates_path = TABLES / "entity-candidates.csv"
    candidate_fields, candidates, candidate_bom, candidate_eol = read_csv(candidates_path)
    candidate = required_one(candidates, "candidate_id", CANDIDATE)
    if candidate["suggested_type"] != "work":
        raise ValueError("candidate type changed")

    alignment_path = TABLES / "alignment.csv"
    align_fields, alignments, align_bom, align_eol = read_csv(alignment_path)
    alignment = required_one(alignments, "alignment_id", ALIGNMENT)
    if alignment["candidate_id"] != CANDIDATE or alignment["decision"] != "undecided" or alignment["ku_id"]:
        raise ValueError("candidate alignment changed from expected undecided state")
    if "group=" in (alignment.get("resolution_note") or ""):
        raise ValueError("candidate already has a group decision")
    old_note = alignment.get("resolution_note", "")
    alignment["decision"] = "new"
    alignment["ku_id"] = KU_ID
    alignment["process_ref"] = PROCESS_REF
    alignment["resolution_note"] = (
        f"group={GROUP}; S3 new: the source defines one ten-picture group, but no individual picture identities, "
        "titles, or makers are supplied. Keep distinct from other works and preserve the proposed-gift status. "
        f"prior_s3_rationale={old_note}"
    )
    plans[alignment_path] = render_csv(align_fields, alignments, align_bom, align_eol)

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest, manifest_bom, manifest_eol = read_csv(manifest_path)
    if any(row["ku_id"] == KU_ID for row in manifest) or (ROOT / CARD_PATH).exists():
        raise ValueError("planned KU or card already exists")
    if any(row["name_en"].casefold() == "ten pictures of apollo and the muses brought from rome by giovanni baglione".casefold() for row in manifest):
        raise ValueError("same English title already exists")
    manifest.append({
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": "乔瓦尼·巴廖内自罗马带来的阿波罗与缪斯十幅画",
        "name_en": "Ten pictures of Apollo and the Muses brought from Rome by Giovanni Baglione",
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": CARD_PATH,
    })
    plans[manifest_path] = render_csv(manifest_fields, manifest, manifest_bom, manifest_eol)
    plans[ROOT / CARD_PATH] = CARD.encode("utf-8")
    plans[ROOT / "04-knowledge" / "accepted.yml"] = accepted_with(CARD_PATH)

    source_text = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    if "ten pictures of" not in source_text or "Apollo and the Muses" not in source_text or "Baglione" not in source_text:
        raise ValueError("expected Haskell source wording was not found")

    statement_path = TABLES / "book-statements.jsonl"
    statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    if any(statement_id not in statement_by_id for statement_id in STATEMENTS):
        raise ValueError("one or more direct S6 statements are missing")
    for statement_id, (subject, object_) in STATEMENTS.items():
        row = statement_by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != (subject, object_):
            raise ValueError(f"S2 endpoints changed for {statement_id}")
        if qualifiers.get("relation_candidate") is not True:
            raise ValueError(f"{statement_id} is no longer a relation candidate")

    enrichment_path = TABLES / "enrichment.jsonl"
    existing_enrichment = [json.loads(line) for line in enrichment_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    preview_card_path = CARD_PATH + ".preview"
    preview_card = ROOT / preview_card_path
    try:
        preview_card.write_text(CARD, encoding="utf-8", newline="\n")
        additions, source_registry, warnings, cards_with_tables = extract_records(
            [{"ku_id": KU_ID, "card_path": preview_card_path}]
        )
    finally:
        preview_card.unlink(missing_ok=True)
    if cards_with_tables != 1 or len(additions) != 6 or warnings:
        raise ValueError(f"field extraction mismatch: tables={cards_with_tables}, fields={len(additions)}, warnings={warnings}")
    if set(source_registry) != {SOURCE_ID} or any(row.get("evidence_status") != "source_backed" for row in additions):
        raise ValueError("new card fields are not all source-backed to the Haskell source")
    assign_ids(additions, enrichment_path)
    existing_occurrences = {row.get("occurrence_id") for row in existing_enrichment}
    if any(row.get("occurrence_id") in existing_occurrences for row in additions):
        raise ValueError("new enrichment occurrence duplicates an existing row")
    plans[enrichment_path] = enrichment_path.read_bytes() + render_jsonl(additions)

    relations_path = TABLES / "relations.csv"
    relation_fields, relations, relation_bom, relation_eol = read_csv(relations_path)
    relation_numbers = [int(m.group(1)) for row in relations if (m := re.fullmatch(r"rel-(\d+)", row.get("relation_id", "")))]
    relation_id = f"rel-{max(relation_numbers, default=0) + 1:04d}"
    if any(row["relation_id"] == relation_id for row in relations):
        raise ValueError("next relation id is already used")
    relation = {
        "relation_id": relation_id,
        "subject_ku_id": KU_ID,
        "object_ku_id": RICHELIEU,
        "predicate": "influenced",
        "time": "",
        "role": "间接引起对曼图亚的关注",
        "scope": "Haskell says the proposed pictures indirectly turned Cardinal Richelieu’s attention toward Mantua. This records only the reported indirect influence on his attention; it does not say Richelieu acquired the ten pictures.",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": "Chapter 7, printed p. 175 L65; PDF physical p. 9; statement=st-chp7-p175-i19",
        "source_file": SOURCE_FILE,
        "note": "The source explicitly marks the effect as indirect; acquisition and delivery are not inferred.",
    }
    if any(
        row.get("subject_ku_id") == relation["subject_ku_id"]
        and row.get("predicate") == relation["predicate"]
        and row.get("object_ku_id") == relation["object_ku_id"]
        and row.get("scope") == relation["scope"]
        for row in relations
    ):
        raise ValueError("natural-key duplicate formal relation")
    domain_range = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))["domain_range"]
    if relation["predicate"] not in domain_range:
        raise ValueError("influenced is absent from the relation domain/range matrix")
    types = {row["ku_id"]: row["type"] for row in manifest}
    allowed = domain_range[relation["predicate"]]
    if "work" not in allowed["domain"] or types.get(RICHELIEU) not in allowed["range"]:
        raise ValueError("influenced work-to-person domain/range is not allowed")
    relations.append(relation)
    plans[relations_path] = render_csv(relation_fields, relations, relation_bom, relation_eol)

    knowledge_path = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
    knowledge = knowledge_path.read_text(encoding="utf-8-sig")
    if ANCHOR in knowledge:
        raise ValueError("process anchor already exists")
    enrichment_ids = [row["enrichment_id"] for row in additions]
    next_block = f'''

<a id="{ANCHOR}"></a>
### S3身份分组／S4登记／S5来源字段／S6裁决：第七章 p.175 阿波罗与缪斯十幅画（2026-10-23）

**S3跨章身份决定。** 将 `cand-6693`（`aln-6870`）从undecided裁为new，建立来源限定作品群 `{GROUP}`，登记KU `{KU_ID}`。身份粒度为原文明确的十幅画作群；不把未名单件画、画家或版本视为已识别对象，也不与《公共幸福战胜危险》合并。Haskell称这组画由Giovanni Baglione几年前从罗马带来，并记费迪南多提议作为礼物送出。提议不证明送达、接收或接受。

**S4/S5。** 新增一张work卡及一条候选映射；卡内六项S1来源字段的enrichment ID为 `{", ".join(enrichment_ids)}`，均由Haskell第7章印刷页175 L64–65（PDF物理页9）支持。未作外部作品身份确认。

**S6逐候选裁决。** 本批覆盖与该作品群直接相关的三条关系候选；S2 statements与mentions未改动，也未计入独立S2审读。

| statement_id | 决定 | 去向与边界 |
|---|---|---|
| `st-chp7-p175-i17` | pending | 费迪南多提议将画作作为礼物送出；该句未标明接收者，也不证明实际送达或接受。保留S2断言，不造已完成的赠与关系。 |
| `st-chp7-p175-i18` | pending | 玛丽要求限制缪斯的裸露与放荡描绘；原文未说明要求是否实施，当前受控谓词不能精确表达该请求，不以赞助或委托关系代替。 |
| `st-chp7-p175-i19` | formal | 新增 `{relation_id} influenced`：作品群→黎塞留。只记录Haskell明确称其“间接”引起黎塞留对曼图亚的关注，不推断购入或取得这十幅画。 |

**批后统计。** S3主决定12,390/12,410；new为5,033（4,802组），undecided为5,220，缺主决定20项。S4登记1,549/4,802组、1,766/5,033条映射；待登记3,253组／3,267条映射。S5为12,458条字段（1,634条unverified）。S6累计613/10,478（384 formal、162 pending、67 rejected）；`relations.csv`为1,602条（1,593 formal、9 pending）。本批未改变S2独立复核分子；全书S2尚未接收，S3–S6仍未全书收口。
'''
    plans[knowledge_path] = (knowledge + next_block).encode("utf-8")

    return plans


def main() -> int:
    parser = argparse.ArgumentParser(description="Register and adjudicate the source-defined Baglione picture group.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed, scoped S3/S4/S5/S6 batch")
    args = parser.parse_args()
    plans = build_plan()
    for path, payload in plans.items():
        old = path.read_bytes() if path.exists() else b""
        print(f"{path.relative_to(ROOT)}: {len(old)} -> {len(payload)} bytes; changed={old != payload}")
    print(f"planned: S3 1 candidate new; S4 1 work KU; S5 6 source-backed fields; S6 3 decisions (1 formal, 2 pending), 1 formal relation row.")
    if not args.apply:
        print("preview only; pass --apply after reviewing this scoped batch")
        return 0
    for path, payload in plans.items():
        atomic_write(path, payload)
    print("applied Baglione picture-group batch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
