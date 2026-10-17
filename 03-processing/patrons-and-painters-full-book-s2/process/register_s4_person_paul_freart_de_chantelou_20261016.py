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

GROUP = "new-person:chantelou-de-freart-paul-258ab261f8"
CANDIDATE_ID = "cand-0648"
ALIGNMENT_ID = "aln-0983"
KU_ID = "units/persons/paul-freart-de-chantelou"
CARD_REL = "04-knowledge/units/persons/paul-freart-de-chantelou.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-paul-freart-de-chantelou-20261016"
DISPLAY_NAME = "保罗·弗雷阿尔·德·尚特卢"
NAME_EN = "Paul Fréart de Chantelou"
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
            "location": "全书索引 C.csv#172；列第4章p.106、第6章p.146、第7章p.176",
            "sentence_summary": "索引主项为Chantelou, Paul-Fréart de，页码覆盖三章正文身份与语境锚点。",
            "original_quotes": [
                {"source_span": "C.csv#172", "text": "Chantelou, Paul-Fréart de"}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/C.csv",
                "source_span": "C.csv#172",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第4章 p.106；OCR L96",
            "sentence_summary": "Haskell称Chantelou为Poussin的朋友，并叙述其将Cassiano的手稿与摹画副本带到巴黎。",
            "original_quotes": [
                {
                    "source_span": "line 96; print p. 106",
                    "text": "Poussin’s friend, Paul Freart de Chantelou, who took it to Paris",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "source_span": "line 96; print p. 106",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第6章 p.146；OCR L3–4",
            "sentence_summary": "Haskell称Poussin于1645年8月写信给其巴黎赞助人Chantelou；引文中的评价仍归于被引述的Poussin。",
            "original_quotes": [
                {
                    "source_span": "lines 3–4; print p. 146",
                    "text": "his Parisian patron Chantelou",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "source_span": "lines 3–4; print p. 146",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章 p.176；OCR L83–84",
            "sentence_summary": "Haskell称Surintendant des Bâtiments派遣Chantelou为代理人赴罗马；官员本人未具名。",
            "original_quotes": [
                {
                    "source_span": "lines 83–84; print p. 176",
                    "text": "sent his agent, Paul-Fréart de Chantelou, to Rome",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "source_span": "lines 83–84; print p. 176",
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
    idx = "[全书索引 C.csv#172](../../../02-sources/03-Index/03-2-Index-CSV/C.csv)"
    ch4 = "[第4章 p.106](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L96）"
    ch6 = "[第6章 p.146](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L3–4）"
    ch7 = "[第7章 p.176](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L83–84）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录索引中的 Paul Fréart de Chantelou。第4章称其为Poussin的朋友并叙述其将一套手稿与摹画带到巴黎；第6章称其为Poussin的巴黎赞助人；第7章称其为Surintendant des Bâtiments派往罗马的代理人。中文展示名为项目工作音译。{idx} {ch4} {ch6} {ch7}

**English:** This unit records Paul Fréart de Chantelou as indexed. Chapter 4 calls him Poussin’s friend and says he took a set of a manuscript version and copied drawings to Paris; Chapter 6 calls him Poussin’s Parisian patron; Chapter 7 identifies him as the agent sent to Rome by the Surintendant des Bâtiments. The Chinese display name is a project working transliteration. {idx} {ch4} {ch6} {ch7}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Paul Fréart de Chantelou | S1，C.csv#172；S2，第7章 p.176 |
| 索引形式 | Chantelou, Paul-Fréart de | S1，C.csv#172 |
| 姓名拼写变体 | Paul Freart de Chantelou（未标重音符） | S2，第4章 p.106 |
| 身份角色 | Poussin的巴黎赞助人 | S2，第6章 p.146 |
| 身份角色 | Surintendant des Bâtiments派往罗马的代理人（1640） | S2，第7章 p.176；官员未具名 |

### 本书相关语境

第4章把Chantelou与Poussin的友谊及其携带Cassiano手稿和摹画副本赴巴黎的叙述相连；第6章记录Poussin致巴黎赞助人Chantelou的信；第7章记载他受未具名的Surintendant des Bâtiments派遣赴罗马，并承担招募画家、雕塑家、建筑师及其他工匠的任务，后来护送Poussin及几位未具名画家返程。以上均按各条S2陈述及其原有语境限定。{ch4} {ch6} {ch7}

Chapter 4 connects Chantelou with Poussin’s friendship and his carrying Cassiano’s manuscript-and-drawing copy to Paris; Chapter 6 records Poussin’s letter to his Parisian patron; Chapter 7 describes his mission to Rome on behalf of an unnamed Surintendant des Bâtiments, including recruitment and his later escort of Poussin and a few unnamed painters. These claims retain the qualifications recorded in their individual S2 statements. {ch4} {ch6} {ch7}

## 关系与证据

### 身份与外部链接

本卡仅登记书内身份依据；当前没有外部身份链接。

This unit records identity evidence from the book; no external identity link is currently recorded.

### 关系记录

当前没有正式关系记录。书内7条直接关系候选保留在断言账本中，尚未转为正式关系。

No formal relations are recorded. Seven direct relation candidates from the book remain in the statement ledger and have not been converted into formal relations.
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Paul Fréart de Chantelou in S4.")
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

    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/C.csv").read_text(encoding="utf-8-sig")
    ch4 = (ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md").read_text(encoding="utf-8-sig")
    ch6 = (ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md").read_text(encoding="utf-8-sig")
    ch7 = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md").read_text(encoding="utf-8-sig")
    assert "Chantelou, Paul-Fréart de" in index_text
    assert "Paul Freart de Chantelou" in ch4 and "who took it to Paris" in ch4
    assert "Parisian patron Chantelou" in ch6
    assert "Paul-Fréart de Chantelou, to Rome" in ch7

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
    assert len(direct_statements) == 7 and len(relation_candidates) == 7

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
        f"### S4 person：Paul Fréart de Chantelou 跨三章身份组登记（{DATE}）\n\n"
        f"- `cand-0648`（C.csv#172，pp.106、146、176）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`。索引全名与第4章无重音写法、第6章简称及第7章全名相合；既有manifest无同名person KU。\n"
        f"- 卡片仅记录书内姓名、拼写变体、Poussin的巴黎赞助人及受未具名Surintendant派遣的代理人角色；中文展示名标为项目工作音译。7条直接S2陈述均为关系候选，全部留待S6；本轮未新增正式关系。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增5条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Paul Fréart de Chantelou 跨三章身份组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-0648`（C.csv#172）保持S3组 `{GROUP}`，登记为 `{KU_ID}`。索引列第4章p.106、第6章p.146和第7章p.176；正文全名/简称跨章相合，S3已按完整姓名锚点分组，现有person KU无同名命中，未访问外部身份源。\n"
        "- 卡片保留第4章无重音写法`Paul Freart de Chantelou`，记录第6章的巴黎赞助人角色和第7章受未具名Surintendant派遣赴罗马的代理人角色；不补该官员姓名。中文展示名注明为工作音译。\n"
        "- 7条直接S2 statements均为relation_candidate，涉及友谊、文稿/摹画副本赠与和携带、书信、罗马差遣、招募任务及返程护送，全部留待S6逐条审查。本轮不新增`relations.csv`边，不扩展未具名作品或人员端点。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增5条source-backed字段记录，来源数不变、unverified保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。\n"
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
                backup.write_text("NEW FILE: created by S4 Paul Fréart de Chantelou registration\n", encoding="utf-8")
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
