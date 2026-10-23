from __future__ import annotations

import argparse
import csv
import difflib
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
PROCESS_DIR = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
REVIEW_PATH = PROCESS_DIR / "s2-independent-review-chp8-p239-20261023.md"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
ANCHOR = "s3-s4-s5-s6-ch8-p239-inventory-custody-20261023"
PROCESS_REF = f"03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}"
KU = "units/archives/pitti-palace-apartments-picture-inventory-1716-1723"
CARD_PATH = f"04-knowledge/{KU}.md"
CARD = ROOT / CARD_PATH
INSTITUTION_KU = "units/institutions/soprintendenza-alle-gallerie-florence"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), bom, newline


def render_csv(fields, rows, bom, newline):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    payload = handle.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + payload


def render_jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")


def read_preserving_newlines(path: Path) -> str:
    return path.read_bytes().decode("utf-8-sig")


def encode_preserving_bom(path: Path, text: str) -> bytes:
    bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def atomic_write(path: Path, payload: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".codex-tmp")
    temp.write_bytes(payload)
    os.replace(temp, path)


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
        raise ValueError("archive card is already in accepted.yml")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.lstrip().startswith("-") and line.strip()[2:].strip() > card_path),
        next((i for i, line in enumerate(lines) if line.strip() == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_path}{newline}")
    return (b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8")


def group_id(row):
    match = re.search(r"(?:^|;\s*)group=([^;]+)", row.get("resolution_note", ""))
    return match.group(1) if match else ""


def primary_alignment(rows, candidate_id):
    matches = [row for row in rows if row["candidate_id"] == candidate_id and not row["external_source"]]
    if len(matches) != 1:
        raise ValueError(f"expected one primary alignment for {candidate_id}; found {len(matches)}")
    return matches[0]


def card_text():
    return f'''---
title: "《皮蒂宫公寓绘画清单》（Pitti Palace Apartments Picture Inventory, called ‘1716 Inventory’ by Haskell）"
name_en: "Pitti Palace Apartments Picture Inventory, called ‘1716 Inventory’ by Haskell"
type: archive
sub_type: inventory
evidence_status: source_backed
sources:
  - citation: "{HASKELL_CITATION}"
    location: "第8章，印刷页239，注5，源文件L451；PDF物理页45"
    sentence_summary: "Haskell gives the inventory's Italian title, says it was kept at the Soprintendenza alle Gallerie di Firenze, dates it between 1716 and 1723, calls it the ‘1716 Inventory’ for convenience, and reports the S.P.F. mark for pictures from Ferdinand's own collection."
    original_quotes:
      - source_span: "第8章，印刷页239，注5，源文件L451；PDF物理页45"
        text: "Inventario di Quadri, che si ritrovano negl'appartamenti del gran palazzo de Pitti di S.A.R., kept at the Soprintendenza alle Gallerie di Firenze. It can be dated between 1716 and 1723. For the sake of convenience I have referred to it as the 1716 Inventory. All the pictures from Ferdinand’s own collection are marked S.P.F."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SOURCE_FILE}
      source_span: "line 451; printed p.239, footnote 5; PDF physical p.45"
created: '2026-10-23'
updated: '2026-10-23'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** Haskell 第8章 p.239 注5所述的一份皮蒂宫公寓绘画清单。题名为描述性译名；原文给出意大利语题名，并称清单保存在佛罗伦萨的 Soprintendenza alle Gallerie。Haskell 将清单年代记为1716至1723年，并为方便称其为“1716 Inventory”。本卡仅登记该书内所指的清单，不表示已查阅原件或外部目录。

**English:** A picture inventory for apartments in the Pitti Palace, described in Haskell’s Chapter 8, p. 239, note 5. The English name is descriptive; Haskell supplies an Italian title and says the inventory was kept at the Soprintendenza alle Gallerie di Firenze. He dates it between 1716 and 1723 and uses “1716 Inventory” for convenience. This card records the inventory as cited in the book; the original and external catalogues were not consulted.

### 文献信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 原文题名 | Inventario di Quadri, che si ritrovano negl'appartamenti del gran palazzo de Pitti di S.A.R. | S1，第8章印刷页239注5，L451 |
| Haskell所报年代范围 | 1716–1723；这是Haskell对清单年代的记述 | S1，第8章印刷页239注5，L451 |
| Haskell的便利称呼 | “1716 Inventory”；Haskell明言为方便使用此称呼 | S1，第8章印刷页239注5，L451 |
| Haskell所报标记范围 | Haskell称 Ferdinand 自有收藏中的画作标记为 S.P.F.；不扩展缩写，也不推及所有皮蒂宫画作 | S1，第8章印刷页239注5，L451 |

### 本章相关内容

Haskell 将这份清单与 Ferdinand 收藏的绘画联系起来，并报告其保管地点；本卡不据此推断作品清单的完整性、藏品所有权、标记缩写含义或机构在1716–1723年间的沿革。

## 关系与证据

### 关系候选入口

保管地点候选及“S.P.F.”标记的身份边界见[全书过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。
'''


def build_plan():
    plans: dict[Path, bytes] = {}
    candidates_fields, candidates, candidates_bom, candidates_nl = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    for candidate_id in ["cand-8053", "cand-8054", "cand-8057"]:
        if candidate_id not in candidate_by_id:
            raise ValueError(f"missing candidate {candidate_id}")

    alignment_fields, alignments, alignment_bom, alignment_nl = read_csv(TABLES / "alignment.csv")
    institution_alignment = primary_alignment(alignments, "cand-8053")
    archive_alignment = primary_alignment(alignments, "cand-8054")
    mark_alignment = primary_alignment(alignments, "cand-8057")
    if institution_alignment["alignment_id"] != "aln-8228" or institution_alignment["decision"] != "new" or institution_alignment["ku_id"]:
        raise ValueError("cand-8053 primary S3 state changed; re-review before applying")
    if group_id(institution_alignment) != "sg3-institution-cand-8053":
        raise ValueError("cand-8053 identity group changed")
    if archive_alignment["alignment_id"] != "aln-8229" or archive_alignment["decision"] != "new" or archive_alignment["ku_id"]:
        raise ValueError("cand-8054 primary S3 state changed; re-review before applying")
    if group_id(archive_alignment) != "archive-group-1cacae0e1693":
        raise ValueError("cand-8054 identity group changed")
    if mark_alignment["alignment_id"] != "aln-8232" or mark_alignment["decision"] != "undecided":
        raise ValueError("cand-8057 primary S3 state changed; re-review before applying")
    if CARD.exists() or any(row["ku_id"] == KU for row in read_csv(TABLES / "ku-manifest.csv")[1]):
        raise FileExistsError("Pitti inventory card or KU already exists")
    if any(line.strip() == f"- {CARD_PATH}" for line in (ROOT / "04-knowledge" / "accepted.yml").read_text(encoding="utf-8-sig").splitlines()):
        raise ValueError("Pitti inventory already appears in accepted.yml")
    process_text = read_preserving_newlines(PROCESS_PATH)
    if ANCHOR in process_text:
        raise ValueError("process anchor already exists")
    source_text = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    required_source_phrases = [
        "Inventario di Quadri, che si ritrovano negl'appartamenti del gran palazzo de Pitti di S.A.R.",
        "kept at the Soprintendenza alle Gallerie di Firenze",
        "between 1716 and 1723",
        "1716 Inventory",
        "marked S.P.F.",
    ]
    if any(phrase not in source_text for phrase in required_source_phrases):
        raise ValueError("p.239 source wording changed; re-check scan and statement before applying")

    statements_path = TABLES / "book-statements.jsonl"
    statement_raw = statements_path.read_bytes()
    statement_bom = statement_raw.startswith(b"\xef\xbb\xbf")
    statement_text = statement_raw.decode("utf-8-sig")
    statement_lines = statement_text.splitlines(keepends=True)
    statements = [json.loads(line) for line in statement_lines if line.strip()]
    by_statement = {row["statement_id"]: row for row in statements}
    custody_id = "st-chp8-p239-note5-inventory-description"
    mark_id = "st-chp8-p239-note5-spf-mark"
    for statement_id in [custody_id, mark_id, "st-chp8-p239-note5-inventory-date-and-label"]:
        if statement_id not in by_statement:
            raise ValueError(f"missing source statement {statement_id}")
    if by_statement[custody_id].get("qualifiers", {}).get("relation_candidate") is not True:
        raise ValueError("inventory custody statement is no longer an S6 candidate")
    if by_statement[mark_id].get("qualifiers", {}).get("relation_candidate") is not True:
        raise ValueError("S.P.F. statement is no longer an S6 candidate")

    review = read_preserving_newlines(REVIEW_PATH)
    if "本页 S2 statement 总数未增" not in review or "cand-8054` 与保管机构 `cand-8053` 未在本批登记" not in review:
        raise ValueError("p.239 S2 review note changed; update it deliberately before applying")
    if "18条 `true`、`false` 22条" not in review and "`true` 18条、`false` 22条" not in review:
        raise ValueError("p.239 relation-candidate tally changed; re-count before applying")

    # S3 is reopened only because registration needs an identity comparison and the page supplies a cross-chapter match.
    institution_alignment["decision"] = "same"
    institution_alignment["ku_id"] = INSTITUTION_KU
    institution_alignment["process_ref"] = PROCESS_REF
    institution_alignment["resolution_note"] = (
        "group=sg3-institution-cand-8053; cross-chapter identity recheck triggered by this S4 endpoint registration: "
        "Haskell ch. 8 p.239 n.5 names "
        "Soprintendenza alle Gallerie di Firenze as the inventory's reported repository; the existing institution KU "
        "records the same Soprintendenza alle Gallerie in Florence from Haskell's front matter and institutional "
        "context. Same identity is limited to the named Florence institution; this does not assert institutional "
        "continuity during 1716–1723 or verify the inventory's custody independently."
    )
    archive_alignment["ku_id"] = KU
    archive_alignment["process_ref"] = PROCESS_REF
    archive_alignment["resolution_note"] += (
        " S4 registered this existing S3 new group as a source-limited archive KU; no original or external catalogue was consulted."
    )
    mark_alignment["process_ref"] = PROCESS_REF
    mark_alignment["resolution_note"] = (
        "group=sg3-term-cand-8057; a linked S2 mention now establishes that Haskell reports the S.P.F. mark for pictures from Ferdinand's own "
        "collection. The initials are not expanded, and the source does not establish whether this is a term, a "
        "notation, or another type of object. Retain undecided pending type/identity evidence; the statement is "
        "preserved as an inventory-content field, not a formal KU-to-KU relation."
    )
    plans[TABLES / "alignment.csv"] = render_csv(alignment_fields, alignments, alignment_bom, alignment_nl)

    card = card_text()
    preview_path = CARD.with_name(CARD.name + ".codex-preview")
    if preview_path.exists():
        raise FileExistsError(f"refusing to overwrite existing preview {preview_path}")
    try:
        preview_path.write_text(card, encoding="utf-8", newline="\n")
        field_rows, sources, warnings, table_count = extract_records([{"ku_id": KU, "card_path": preview_path.relative_to(ROOT).as_posix()}])
    finally:
        preview_path.unlink(missing_ok=True)
    if warnings or table_count != 1 or len(field_rows) != 4 or set(sources) != {SOURCE_ID}:
        raise ValueError(f"S5 extraction failed: tables={table_count}; fields={len(field_rows)}; warnings={warnings}; sources={sorted(sources)}")
    if any(row["evidence_status"] != "source_backed" for row in field_rows):
        raise ValueError("one or more S5 fields lack source-backed evidence")
    enrichment_path = TABLES / "enrichment.jsonl"
    existing_enrichments = [json.loads(line) for line in enrichment_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    assign_ids(field_rows, enrichment_path)
    old_ids = {row.get("enrichment_id") for row in existing_enrichments}
    old_occurrences = {row.get("occurrence_id") for row in existing_enrichments}
    if any(row.get("enrichment_id") in old_ids or row.get("occurrence_id") in old_occurrences for row in field_rows):
        raise ValueError("S5 identifier or occurrence collision")
    if [row["enrichment_id"] for row in field_rows] != [f"enr-{i:05d}" for i in range(16365, 16369)]:
        raise ValueError("S5 ID baseline changed; re-evaluate without assuming IDs")
    enrichment_bytes = enrichment_path.read_bytes()
    newline = b"\r\n" if b"\r\n" in enrichment_bytes else b"\n"
    if enrichment_bytes and not enrichment_bytes.endswith((b"\n", b"\r")):
        enrichment_bytes += newline
    addition = newline.join(json.dumps(row, ensure_ascii=False).encode("utf-8") for row in field_rows) + newline
    plans[enrichment_path] = enrichment_bytes + addition

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest, manifest_bom, manifest_nl = read_csv(manifest_path)
    if not any(row["ku_id"] == INSTITUTION_KU and row["type"] == "institution" for row in manifest):
        raise ValueError("existing Soprintendenza KU/type missing from manifest")
    if any(row["ku_id"] == KU for row in manifest):
        raise ValueError("Pitti archive KU already in manifest")
    manifest.append({
        "ku_id": KU,
        "type": "archive",
        "canonical_name": "《皮蒂宫大公寓绘画清单》",
        "name_en": "Pitti Palace Apartments Picture Inventory, called ‘1716 Inventory’ by Haskell",
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": CARD_PATH,
    })
    plans[manifest_path] = render_csv(manifest_fields, manifest, manifest_bom, manifest_nl)
    plans[ROOT / "04-knowledge" / "accepted.yml"] = accepted_with(CARD_PATH)
    plans[CARD] = card.encode("utf-8")

    # The source says “kept at”; use the controlled, domain-compatible predicate with the exact role and scope recorded.
    relations_path = TABLES / "relations.csv"
    relation_fields, relations, relation_bom, relation_nl = read_csv(relations_path)
    numeric_ids = [int(match.group(1)) for row in relations if (match := re.fullmatch(r"rel-(\d+)", row["relation_id"]))]
    if max(numeric_ids, default=0) != 1617:
        raise ValueError("relation ID baseline changed; re-evaluate before adding a relation")
    if any(custody_id in row.get("source_span", "") for row in relations):
        raise ValueError("inventory custody statement already has a relation row")
    domain_range = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))["domain_range"]
    predicate = "located_at"
    if predicate not in domain_range:
        raise ValueError("located_at is absent from the controlled domain-range table")
    domain = set(domain_range[predicate]["domain"])
    value_range = set(domain_range[predicate]["range"])
    types = {row["ku_id"]: row["type"] for row in manifest}
    if types.get(KU) not in domain or types.get(INSTITUTION_KU) not in value_range:
        raise ValueError("located_at domain/range does not accept archive -> institution")
    relation = {
        "relation_id": "rel-1618",
        "subject_ku_id": KU,
        "object_ku_id": INSTITUTION_KU,
        "predicate": predicate,
        "time": "",
        "role": "Haskell所述保管机构",
        "scope": "Haskell p.239 n.5 reports that the inventory was kept at this institution. This records the reported holding location in Haskell’s account only; it does not establish custody during 1716–1723, ownership, or institutional continuity across that date range.",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": "line 451; printed p.239, footnote 5; PDF physical p.45; statement=st-chp8-p239-note5-inventory-description",
        "source_file": SOURCE_FILE,
        "note": "The source wording is ‘kept at’; controlled predicate held_at is unavailable. located_at is used for the reported repository role with scope explicitly narrowed. The inventory and repository record were not independently consulted.",
    }
    relations.append(relation)
    plans[relations_path] = render_csv(relation_fields, relations, relation_bom, relation_nl)

    # S.P.F. remains a source-backed inventory-content fact, not a formal relation candidate.
    by_statement[mark_id]["qualifiers"]["relation_candidate"] = False
    by_statement[mark_id]["qualifiers"]["relation_candidate_note"] = (
        "This reports an inventory-mark convention for pictures from Ferdinand’s own collection. Preserve it as a source-backed "
        "archive-content field; the initials and their type are unresolved, and no controlled predicate expresses this as a "
        "formal KU-to-KU relation. This reclassification does not reject Haskell’s source claim."
    )
    serialized_statements = []
    for line in statement_lines:
        if not line.strip():
            serialized_statements.append(line)
            continue
        row = json.loads(line)
        if row.get("statement_id") == mark_id:
            ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            serialized_statements.append(json.dumps(by_statement[mark_id], ensure_ascii=False, separators=(",", ":")) + ending)
        else:
            serialized_statements.append(line)
    plans[statements_path] = (b"\xef\xbb\xbf" if statement_bom else b"") + "".join(serialized_statements).encode("utf-8")

    # Update the existing p.239 review record without changing the unified S2 review numerator.
    updated_review = review.replace("本批将 p.239注3 的 Zanotti 书目引注补定为书内 `cites` 候选，现为 `true` 18条、`false` 22条、未分类0条。", "本批将 p.239注3 的 Zanotti 书目引注补定为书内 `cites` 候选，现为 `true` 18条、`false` 22条、未分类0条。随后对注5的 S.P.F. 标记重新做关系类型审查：该断言属于清单内容约定而非可表达的 KU 间关系，修订后 p.239 共 `true` 17条、`false` 23条、未分类0条；源事实保留为 S5 字段，不构成对来源的否定。")
    updated_review = updated_review.replace("注5库存对象 `cand-8054` 与保管机构 `cand-8053` 未在本批登记；后者名称与已登记的 Soprintendenza 机构卡相近，需先核对跨章身份后再写回 S4。", "注5库存对象 `cand-8054` 与保管机构 `cand-8053` 在本页初始批次未登记；随后以当前注册触发跨章身份复核：`cand-8053` 的名称与佛罗伦萨既有 Soprintendenza 机构 KU 相同，主决定改为 `same`；`cand-8054` 沿用既有 `new` 组并已登记为 archive KU。")
    updated_review = updated_review.replace("注5库存—保管机构候选未裁决：机构身份仍需与现有 KU 比较，库存 `cand-8054` 的 S4 登记及相关 S6 `held_at` 关系后续处理；S.P.F. 标记候选仍保留现有未决身份，不据缩写造正式关系。", "注5库存登记后，`st-chp8-p239-note5-inventory-description` 已裁为 formal `rel-1618 located_at`（archive→institution），角色与范围限定为 Haskell 所报告的保管地点；不推断1716–1723年的机构沿革、同期保管或所有权。`st-chp8-p239-note5-spf-mark` 从 S6 relation candidates 中撤出，作为来源支持的清单内容字段保留；`cand-8057` 仍为 S3 `undecided`，缩写扩展与对象类型待证。")
    if updated_review == review:
        raise ValueError("p.239 review note did not change; expected text replacements failed")
    if "修订后 p.239 共 `true` 17条、`false` 23条" not in updated_review or "rel-1618 located_at" not in updated_review:
        raise ValueError("p.239 review record lacks the new relation-candidate counts or S6 decision")
    plans[REVIEW_PATH] = encode_preserving_bom(REVIEW_PATH, updated_review)

    process_addition = f'''\n\n<a id="{ANCHOR}"></a>\n\n### 第八章 p.239 皮蒂宫绘画清单端点与保管地点（2026-10-23）\n\n**触发与身份裁决。** S4登记准备触发对 `cand-8053` 的定点 S3复核。扫描页45（印刷页239）注5给出清单原文题名，并称其“kept at the Soprintendenza alle Gallerie di Firenze”；本书章前图片来源及既有机构卡亦记录位于佛罗伦萨的 `Soprintendenza alle Gallerie`。据同一机构名称与城市范围，`aln-8228` 改为 `same → {INSTITUTION_KU}`。该决定限于哈斯克尔所指的佛罗伦萨机构身份，不主张机构在1716–1723年间已存在或连续，也不独立验证清单保管状态。\n\n`cand-8054` 沿用 `archive-group-1cacae0e1693` 的既有 S3 `new` 决定，登记为 `{KU}`。范围仅为 Haskell p.239 n.5 所述绘画清单；描述性英文名不是原始题名，原件及外部目录未查。`cand-8057` 有了本页明确的 S2 mention：Haskell 将 S.P.F. 作为 Ferdinand 自有收藏画作的标记，但未展开缩写。更新 `aln-8232` 的未决理由，保持 `undecided`，待证类型／身份不强分为术语或其他记号。\n\n**S5字段。** 新卡增加4条 `source_backed` 字段（`{field_rows[0]['enrichment_id']}`–`{field_rows[-1]['enrichment_id']}`）：意大利语原题、Haskell所报1716–1723年代范围、其为方便使用的“1716 Inventory”称呼、以及 S.P.F. 标记仅适用于其所述 Ferdinand 自有收藏画作。所有字段均定位至第8章 p.239 n.5、源文件L451；不把年代范围压缩为1716年，不扩写 S.P.F.，也不推及所有皮蒂宫画作。\n\n**S6逐候选裁决。** `st-chp8-p239-note5-inventory-description` 的端点现为已登记 archive KU 和既有 institution KU。原文谓词 `held_at` 不在受控词表；以域值域兼容的 `located_at` 建立 formal `rel-1618`，角色记为 Haskell 所报告的保管机构，时间留空，scope 明确不主张清单年代期间的保管、所有权或机构沿革。`st-chp8-p239-note5-spf-mark` 不构成受控的 KU 间关系，`relation_candidate` 改为 `false`；该处理保留原断言及 S5 标记字段，不是否定来源事实。\n\n**S2边界。** 本批没有增加 statement 或 mention，也不将 p.239 的40条逐条核读并入统一 S2 独立复核分子。p.239 relation candidates 由18 true／22 false调整为17 true／23 false；净关系候选减少1条，新增1条 formal 关系。\n'''
    process_newline = "\r\n" if "\r\n" in process_text else "\n"
    process_addition = process_addition.replace("\n", process_newline)
    plans[PROCESS_PATH] = encode_preserving_bom(
        PROCESS_PATH,
        process_text.rstrip("\r\n") + process_addition.rstrip("\r\n") + process_newline,
    )

    # Preserve exact candidate disposition in the primary row and avoid silently changing other identities.
    if group_id(archive_alignment) != "archive-group-1cacae0e1693" or group_id(mark_alignment) != "sg3-term-cand-8057":
        raise ValueError("candidate identity group changed during planning")
    return plans, field_rows, relation


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Register the p.239 Pitti inventory endpoint, fields, and relation.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed batch; default is read-only diff preview")
    parser.add_argument("--quiet", action="store_true", help="print only the plan summary")
    args = parser.parse_args()
    plans, field_rows, relation = build_plan()
    print(f"mode={'apply' if args.apply else 'preview'} files={len(plans)} s5_fields={len(field_rows)} relation={relation['relation_id']}:{relation['predicate']}")
    if not args.quiet:
        for path, payload in plans.items():
            old = path.read_bytes() if path.exists() else b""
            before = old.decode("utf-8-sig", errors="replace").splitlines(keepends=True)
            after = payload.decode("utf-8-sig", errors="replace").splitlines(keepends=True)
            diff = difflib.unified_diff(before, after, fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)))
            print("".join(diff), end="")
    if args.apply:
        for path, payload in plans.items():
            atomic_write(path, payload)
        print("apply_complete=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
