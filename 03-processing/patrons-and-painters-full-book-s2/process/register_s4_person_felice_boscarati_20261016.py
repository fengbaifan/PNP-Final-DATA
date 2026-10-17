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

GROUP = "new-person:boscarati-felice-af2f756b3b"
CANDIDATE_ID = "cand-0411"
ALIGNMENT_ID = "aln-0746"
KU_ID = "units/persons/felice-boscarati"
CARD_REL = "04-knowledge/units/persons/felice-boscarati.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-felice-boscarati-20261016"
DISPLAY_NAME = "费利切·博斯卡拉蒂"
NAME_EN = "Felice Boscarati"
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
            "location": "全书索引 B.csv#258；列第10章pp.326–327、第20章后记p.408",
            "sentence_summary": "索引主项为Boscarati, Felice，页码覆盖两章中的姓名锚点。",
            "original_quotes": [
                {"source_span": "B.csv#258", "text": "Boscarati, Felice"}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
                "source_span": "B.csv#258",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.326；OCR L216–217",
            "sentence_summary": "Haskell称Felice Boscarati为当地艺术家，叙述其迁居威尼斯后被Pisani接纳为official painter；此为原文措辞，不据此推定正式薪职。",
            "original_quotes": [
                {
                    "source_span": "lines 216–217; print p. 326",
                    "text": "a local artist, Felice Boscarati",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "lines 216–217; print p. 326",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.327；OCR L235–237",
            "sentence_summary": "Haskell称其为Pisani的画家，并在脚注中提到Pisani与Boscarati关系密切；不据此单独决定关系类型。",
            "original_quotes": [
                {
                    "source_span": "lines 235, 237; print p. 327 and note 3",
                    "text": "his painter Felice Boscarati",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "lines 235, 237; print p. 327 and note 3",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第20章后记 p.408；OCR L181",
            "sentence_summary": "后记再次全名提到Felice Boscarati，并经Olivato转述其审讯证词和政治观点；审讯记录与论文未独立查阅。",
            "original_quotes": [
                {
                    "source_span": "line 181; print p. 408",
                    "text": "Felice Boscarati",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "source_span": "line 181; print p. 408",
            },
        },
    ]
    frontmatter = {
        "title": f"{DISPLAY_NAME}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 B.csv#258](../../../02-sources/03-Index/03-2-Index-CSV/B.csv)"
    ch10 = "[第10章 pp.326–327](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L216–239）"
    ch20 = "[第20章后记 p.408](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)（L174–185）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录索引中的 Felice Boscarati。第10章称其为当地艺术家，叙述其迁居威尼斯后被Giorgio Pisani接纳为其画家，并记其在Pisani失势后的处境；第20章后记再次全名提到他，并经Loredana Olivato转述其审讯证词。后两种来源层级和限定按S2原记录保留；中文展示名为项目工作音译。{idx} {ch10} {ch20}

**English:** This unit records Felice Boscarati as indexed. Chapter 10 identifies him as a local artist, says that after moving to Venice he was taken up by Giorgio Pisani as his painter, and describes his situation after Pisani’s disgrace. The Chapter 20 postscript names him again and reports his trial testimony through Loredana Olivato. The source layers and qualifications are retained as recorded in S2. The Chinese display name is a project working transliteration. {idx} {ch10} {ch20}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Felice Boscarati | S2，第10章 p.326；第20章后记 p.408 |
| 索引形式 | Boscarati, Felice | S1，B.csv#258 |
| 书内简称 | Boscarati | S2，第10章 pp.326–327；第20章后记 p.408 |
| 身份 | 当地艺术家（local artist） | S2，第10章 p.326 |

### 本书相关语境

第10章记述Boscarati为Lazzaro Riviera创作四幅寓意画，后来迁居威尼斯并被Pisani接纳为其画家；原文称“official painter”，但S2已限定不能据此推定正式薪职。第20章后记关于绘画政治风波的叙述，包含Haskell对Olivato文章及Boscarati审讯证词的转述，相关材料并未独立查阅。正文及脚注中的委托、展示、亲近关系和观点仍按各条S2陈述限定。{ch10} {ch20}

Chapter 10 says Boscarati painted four allegorical pictures for Lazzaro Riviera, later moved to Venice, and was taken up by Pisani as his painter; Haskell’s phrase “official painter” is not treated as proof of a formal salaried post. The Chapter 20 postscript discusses the political controversy around the pictures and reports Olivato’s account of Boscarati’s trial testimony. The cited article and trial record were not independently consulted. Commissions, display, closeness, and opinions remain qualified in the individual S2 statements. {ch10} {ch20}

## 关系与证据

### 身份与外部链接

本卡仅登记书内身份依据；当前没有外部身份链接。

This unit records identity evidence from the book; no external identity link is currently recorded.

### 关系记录

当前没有正式关系记录。书内6条直接关系候选保留在断言账本中，尚未转为正式关系；另1条关于讽刺倾向的评价按S2登记为非关系候选。

No formal relations are recorded. Six direct relation candidates from the book remain in the statement ledger and have not been converted into formal relations; one statement characterizing his taste for satire remains a non-relation candidate in S2.
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Felice Boscarati in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE_ID)
    assert candidate.get("suggested_type") == "person"
    group_rows = [
        row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and f"group={GROUP}" in row.get("resolution_note", "")
    ]
    assert len(group_rows) == 1 and group_rows[0].get("candidate_id") == CANDIDATE_ID
    primary = group_rows[0]
    assert primary.get("alignment_id") == ALIGNMENT_ID and not primary.get("ku_id")
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(
        row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/B.csv").read_text(encoding="utf-8-sig")
    ch10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_sec_ii.md").read_text(encoding="utf-8-sig")
    ch20 = (ROOT / "02-sources/02-Markdown/20_CHP-20Postscript.md").read_text(encoding="utf-8-sig")
    assert "Boscarati, Felice" in index_text
    assert "a local artist, Felice Boscarati" in ch10 and "his painter Felice Boscarati" in ch10
    assert "Felice Boscarati" in ch20 and "Boscarati’s evidence at the trial of Pisani" in ch20

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
    assert len(direct_statements) == 7 and len(relation_candidates) == 6

    planned_alignment = [dict(row) for row in alignment]
    mapped = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": DISPLAY_NAME,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 4

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_insert = (
        f"### S4 person：Felice Boscarati 跨两章身份组登记（{DATE}）\n\n"
        f"- `cand-0411`（B.csv#258，pp.326–327、408）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`。第10章p.326–327与第20章后记p.408均给出全名/姓氏锚点，既有manifest无同名person KU。\n"
        f"- 卡片只登记书内姓名、艺术家身份及来源限定；“official painter”不扩展为正式薪职，后记的审讯证词保留为Haskell经Olivato转述，原论文和案卷未独立查阅。6条直接关系候选留待S6，1条讽刺倾向评价保持非关系候选。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Felice Boscarati 跨两章身份组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-0411`（B.csv#258）保持S3组 `{GROUP}`，登记为 `{KU_ID}`。第10章p.326、327与第20章后记p.408重复给出全名/姓氏锚点，identity group由完整姓名和上下文对应；既有manifest无同名person KU，未访问外部身份源。\n"
        "- 卡片记录艺术家身份和Boscarati姓氏形式；原文“official painter”不据以推断正式薪职。第20章后记所引证词经过Olivato转述，未独立查阅该文或审讯档案。\n"
        "- 7条直接S2 statements中6条为relation_candidate，涉及Pisani接纳其为画家、展示图像的候选归因（保留另一种可能）、Pisani与Boscarati的关系、Pisani失势后Boscarati的处境、Boscarati证词及其后续观点；全部留待S6。1条讽刺倾向评价保持非关系候选。本轮不新增`relations.csv`边。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录，来源数不变、unverified保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。\n"
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
                backup.write_text("NEW FILE: created by S4 Felice Boscarati registration\n", encoding="utf-8")
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
