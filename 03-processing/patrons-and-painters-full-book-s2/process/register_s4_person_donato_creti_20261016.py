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

GROUP = "new-person:creti-donato-4d75402fa5"
CANDIDATE_ID = "cand-0889"
ALIGNMENT_ID = "aln-1224"
KU_ID = "units/persons/donato-creti"
CARD_REL = "04-knowledge/units/persons/donato-creti.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-donato-creti-20261016"

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
            "location": "全书索引 C.csv#423；定位第7、8、10、14章相关页段",
            "sentence_summary": "索引以Creti, Donato为主项，列出pp.189、222、223、288、351。",
            "original_quotes": [{"source_span": "C.csv#423", "text": "Creti, Donato"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/C.csv",
                "source_span": "C.csv#423",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章 p.189；OCR L253–255",
            "sentence_summary": "Haskell以“We are told”引出对Donato Creti等博洛尼亚画家仰慕Louis XIV的转述，保留其间接来源语气。",
            "original_quotes": [{"source_span": "lines 253–255; print p. 189", "text": "We are told that Carlo Cignani, Benedetto Gennari, Luigi Quaini and Donato Creti were all keen admirers of Louis XIV"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "source_span": "lines 253–255; print p. 189",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第8章 pp.222–223；OCR L135–142",
            "sentence_summary": "Haskell称Creti为画家，并讨论其与Crespi作品的比较及Ruffo对Creti的兴趣；荣誉称号的授予者、时间和性质未由此段确定。",
            "original_quotes": [
                {"source_span": "lines 135–136; print p. 222", "text": "Donato Creti. He was so fond of this painter that he used to sit"},
                {"source_span": "lines 140–141; print p. 223", "text": "watching him at work for hours and had him created Cavaliere dello speron d'oro"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "lines 135–142; print pp. 222–223",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.288；OCR L227",
            "sentence_summary": "OCR转录作Donato Cred；同章迁移记录说明对照纸本校作Creti，索引及其他正文锚点亦作Creti。此处保留来源转录差异，不另立人名。",
            "original_quotes": [{"source_span": "line 227; print p. 288", "text": "Donato Cred"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 227; print p. 288; OCR reading checked against scan in S2 migration record",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章 p.351；OCR L50–53",
            "sentence_summary": "Haskell将Donato Creti列入Algarotti拟议的画廊题材计划，并在地区列表中把他置于Bologna语境；提案不证明实际委托或出生地。",
            "original_quotes": [{"source_span": "lines 50–53; print p. 351", "text": "along with Balestra and Donato Creti—one of the very rare occasions in the eighteenth century when French and Italian artists were required to co-operate in a single venture"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "source_span": "lines 50–53; print p. 351",
            },
        },
    ]
    frontmatter = {
        "title": "多纳托·克雷蒂（Donato Creti）",
        "name_en": "Donato Creti",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 C.csv#423](../../../02-sources/03-Index/03-2-Index-CSV/C.csv)"
    ch7 = "[第7章 p.189](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L253–255）"
    ch8 = "[第8章 pp.222–223](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L135–142）"
    ch10 = "[第10章 p.288](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L227；OCR校读见S2过程记录）"
    ch14 = "[第14章 p.351](../../../02-sources/02-Markdown/14_CHP-14_intro.md)（L50–53）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应全书索引中的 Donato Creti。第7、8、14章直接写作Donato Creti；第10章OCR转录作“Donato Cred”，S2迁移记录已对照纸本校读为Creti。第8章将其称为画家；本卡不补入书外生平或身份标识。中文显示名为项目工作音译。{idx} {ch7} {ch8} {ch10} {ch14}

**English:** This unit records Donato Creti as indexed in *Patrons and Painters*. Chapters 7, 8, and 14 spell the name Donato Creti; the Chapter 10 OCR transcription reads “Donato Cred,” which the S2 migration record checked against the printed page and corrected to Creti. Chapter 8 calls him a painter. No external biography or authority identifier is added. The Chinese display name is a project working transliteration. {idx} {ch7} {ch8} {ch10} {ch14}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Donato Creti | S1，C.csv#423 |
| 索引形式 | Creti, Donato | S1，C.csv#423 |
| 身份 | 画家 | S3，第8章 p.222 |

### 本书相关语境

索引 C.csv#423 列出 pp.189、222、223、288、351。第7章p.189以“We are told”引出Creti仰慕Louis XIV的转述；第8章pp.222–223描述Ruffo对其绘画的兴趣及“Cavaliere dello speron d'oro”称谓，但授予权力、日期与称号性质未明，相关term候选仍待裁决。第10章p.288的OCR姓名差异已在S2过程记录对照纸本校读，不把“Cred”另建为对象。第14章p.351记Algarotti拟议的画廊题材安排与法、意艺术家合作；该提案不等同于实际委托或完成。人物互动、收藏、授予称号及创作关系均留在原S2 statements，待S6逐条审查。{idx} {ch7} {ch8} {ch10} {ch14}

The index entry C.csv#423 lists pp. 189, 222, 223, 288, and 351. Chapter 7, p. 189, introduces a report of Creti’s admiration for Louis XIV with “We are told.” Chapters 8, pp. 222–223, describe Ruffo’s interest in Creti’s painting and the title “Cavaliere dello speron d'oro,” but do not establish the granting authority, date, or nature of the title; the related term candidate remains unresolved. The Chapter 10, p. 288, OCR name variant was checked against the printed page in the S2 processing record and is not treated as a separate entity. Chapter 14, p. 351, records Algarotti’s proposed gallery subjects and a planned French-Italian artistic venture; a proposal does not establish a completed commission. Personal interactions, collection, title, and creative relations remain in the original S2 statements for item-by-item S6 review. {idx} {ch7} {ch8} {ch10} {ch14}

## 关系与证据

### 关系记录

本轮未新增正式关系。7条以该人物为直接端点的S2关系候选仍待S6逐条审查。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Donato Creti in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next((row for row in candidates if row.get("candidate_id") == CANDIDATE_ID), None)
    assert candidate and candidate.get("suggested_type") == "person"
    primary = next((row for row in alignment if row.get("alignment_id") == ALIGNMENT_ID), None)
    assert primary and primary.get("candidate_id") == CANDIDATE_ID
    assert primary.get("decision") == "new" and not primary.get("ku_id")
    assert GROUP in primary.get("resolution_note", "")
    group_rows = [
        row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and GROUP in row.get("resolution_note", "")
    ]
    assert [row.get("candidate_id") for row in group_rows] == [CANDIDATE_ID]
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en") == "Donato Creti" for row in manifest)
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_c = (ROOT / "02-sources/03-Index/03-2-Index-CSV/C.csv").read_text(encoding="utf-8-sig")
    ch10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    assert "Creti, Donato" in index_c and "Donato Cred" in ch10
    assert "OCR reads Cred; physical page reads Creti" in (PROCESS_DIR / "chp10_p288_migration.py").read_text(encoding="utf-8-sig")
    assert "had him created Cavaliere dello speron d'oro" in (ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md").read_text(encoding="utf-8-sig")

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
    assert len(direct_statements) == 9 and len(relation_candidates) == 7

    planned_alignment = [dict(row) for row in alignment]
    mapped = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "多纳托·克雷蒂",
        "name_en": "Donato Creti",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 5

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_insert = (
        f"### S4 person：Donato Creti 跨章候选登记（{DATE}）\n\n"
        f"- `cand-0889`（C.csv#423）→ `{GROUP}` → `{KU_ID}`。新增双语人物卡、manifest、accepted路径；索引全名及第7、8、14章正文称名支持独立人物KU。第10章p.288 OCR作Cred，按S2对照纸本校读为Creti，来源原文未改。\n"
        f"- 9条直接S2陈述中7条为关系候选，均留待S6；另2条为非关系陈述。称号对象 `cand-7745` 仍为undecided，未作人物属性或新增term KU。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组、待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Donato Creti 跨章候选登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-0889`（C.csv#423）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`；无既有人物KU命中。索引Creti, Donato及第7、8、14章的全名/指称共同支持书内人物身份；第10章OCR写Donato Cred，`chp10_p288_migration.py`记录已对照纸本校读为Creti，未改写原来源。\n"
        "- 新卡限于姓名、索引形式及书内画家身份。Haskell对Creti与Crespi的比较、Ruffo的观看／收藏／授予称号叙述、Louis XIV仰慕报告和Algarotti提案均保留原statement及限定，不升级为正式关系；授勋权力和日期不明，相关term候选 `cand-7745` 继续undecided。\n"
        "- 9条直接S2陈述中7条为关系候选，另2条为非关系陈述；关系候选待S6逐条审查。本轮没有新增 `relations.csv` 边、term KU或外部身份记录。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。\n"
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
                backup.write_text("NEW FILE: created by S4 Donato Creti registration\n", encoding="utf-8")
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
