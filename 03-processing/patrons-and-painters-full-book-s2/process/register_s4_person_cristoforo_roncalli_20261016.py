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

GROUP = "new-person:cristoforo-roncalli-a72597e026"
CANDIDATE_ID = "cand-2218"
ALIGNMENT_ID = "aln-2553"
KU_ID = "units/persons/cristoforo-roncalli"
CARD_REL = "04-knowledge/units/persons/cristoforo-roncalli.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-cristoforo-roncalli-20261016"
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
            "location": "全书索引 Q-R.csv#145；列第2章p.30、第3章p.69、第4章p.94注",
            "sentence_summary": "索引主项为Roncalli, Cristoforo (Pomerancio)，页码对应全名、别名变体及脚注身份讨论。",
            "original_quotes": [
                {"source_span": "Q-R.csv#145", "text": "Roncalli, Cristoforo (Pomerancio)"}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
                "source_span": "Q-R.csv#145",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第2章 p.30；OCR L111",
            "sentence_summary": "Haskell明确将Cristoforo Roncalli称为画家，并称其为Pomarancio。",
            "original_quotes": [
                {
                    "source_span": "line 111; print p. 30",
                    "text": "accompanied by the painter Cristoforo Roncalli, known as Pomarancio.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "source_span": "line 111; print p. 30",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第3章 p.69；OCR L49–50",
            "sentence_summary": "Haskell在叙述Oratorians时使用Pomerancio这一异拼，并称该艺术家曾为St Philip画像及创作祭坛画。",
            "original_quotes": [
                {"source_span": "line 50; print p. 69", "text": "Another artist especially popular with the Congregation was Pomerancio"}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "source_span": "lines 49–50; print p. 69",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第4章 p.94 注；OCR L10–13",
            "sentence_summary": "脚注转述Longhi对Romanelli/Pomarancio的校改及Nicolson关于抄写者以Romanelli替代Roncalli的可能解释；原信和研究文献未独立查阅。",
            "original_quotes": [
                {
                    "source_span": "lines 13–14; print p. 94, note 3",
                    "text": "Nicolson plausibly suggested to me (verbally) that the error arose through a copyist substituting Romanelli for the similar word Roncalli (i.e. Pomarancio).",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/04_CHP-4_intro.md",
                "source_span": "lines 10–13; print p. 94, note 3",
            },
        },
    ]
    frontmatter = {
        "title": "克里斯托福罗·龙卡利（Cristoforo Roncalli）",
        "name_en": "Cristoforo Roncalli",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 Q-R.csv#145](../../../02-sources/03-Index/03-2-Index-CSV/Q-R.csv)"
    ch2 = "[第2章 p.30](../../../02-sources/02-Markdown/02_CHP-2_sec_i.md)（L111）"
    ch3 = "[第3章 p.69](../../../02-sources/02-Markdown/03_CHP-3_sec_ii.md)（L49–50）"
    ch4 = "[第4章 p.94 注3](../../../02-sources/02-Markdown/04_CHP-4_intro.md)（L10–13）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录索引中的 Cristoforo Roncalli。第2章称其为画家，并称其为Pomarancio；第3章出现异拼Pomerancio；第4章注3讨论Roncalli与Pomarancio的抄写及校改问题。中文展示名为项目工作音译。{idx} {ch2} {ch3} {ch4}

**English:** This unit records Cristoforo Roncalli as indexed. Chapter 2 calls him a painter known as Pomarancio; Chapter 3 uses the spelling Pomerancio; Chapter 4, note 3, discusses a copying and emendation issue involving Roncalli and Pomarancio. The Chinese display name is a project working transliteration. {idx} {ch2} {ch3} {ch4}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Cristoforo Roncalli | S2，第2章 p.30 |
| 索引形式 | Roncalli, Cristoforo (Pomerancio) | S1，Q-R.csv#145 |
| 身份 | 画家（painter） | S2，第2章 p.30 |
| 别名 | Pomarancio | S2，第2章 p.30 |
| 书内拼写变体 | Pomerancio | S2，第3章 p.69 |

### 本书相关语境

第2章以“Pomarancio”称呼Roncalli，第3章使用“Pomerancio”；第4章脚注所讨论的是一封信中Romanelli/Pomarancio的校改以及Nicolson关于抄写者可能写成Romanelli而非Roncalli的推测。后者按Haskell的转述保留为解释，不独立确认为原信内容。作品、旅行、委托和与Giustiniani的关系仍由各自S2陈述限定。{ch2} {ch3} {ch4}

Chapter 2 refers to Roncalli as “Pomarancio,” while Chapter 3 uses “Pomerancio.” Chapter 4, note 3, discusses an emendation from Romanelli to Pomarancio in a letter and Nicolson’s suggestion that a copyist may have written Romanelli instead of Roncalli. This remains Haskell’s reported explanation and is not independently confirmed as the letter’s wording. Claims about works, travel, commissions, and Giustiniani remain qualified in their individual S2 statements. {ch2} {ch3} {ch4}

## 关系与证据

### 身份与外部链接

本卡仅登记书内身份依据；当前没有外部身份链接。

This unit records identity evidence from the book; no external identity link is currently recorded.

### 关系记录

当前没有正式关系记录。书内直接关系候选保留在断言账本中，尚未转为正式关系。

No formal relations are recorded. Direct relation candidates from the book remain in the statement ledger and have not been converted into formal relations.
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Cristoforo Roncalli identity group in S4.")
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
        row.get("type") == "person" and row.get("name_en", "").casefold() in {"cristoforo roncalli", "pomerancio", "pomarancio"}
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_bytes = (ROOT / "02-sources/03-Index/03-2-Index-CSV/Q-R.csv").read_bytes()
    ch2 = (ROOT / "02-sources/02-Markdown/02_CHP-2_sec_i.md").read_text(encoding="utf-8-sig")
    ch3 = (ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md").read_text(encoding="utf-8-sig")
    ch4 = (ROOT / "02-sources/02-Markdown/04_CHP-4_intro.md").read_text(encoding="utf-8-sig")
    assert b"Roncalli, Cristoforo (Pomerancio)" in index_bytes
    assert "painter Cristoforo Roncalli, known as Pomarancio" in ch2
    # The OCR/Markdown source breaks the sentence across lines 49–50.
    assert "Another artist especially popular with the" in ch3 and "Congregation was Pomerancio" in ch3
    assert "copyist substituting Romanelli for the similar word Roncalli" in ch4

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
    assert len(direct_statements) == 8 and len(relation_candidates) == 8

    planned_alignment = [dict(row) for row in alignment]
    mapped = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "克里斯托福罗·龙卡利",
        "name_en": "Cristoforo Roncalli",
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
        f"### S4 person：Cristoforo Roncalli 跨三章身份组登记（{DATE}）\n\n"
        f"- `cand-2218`（Q-R.csv#145，pp.30、69、94n）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`。第2章全名与Pomarancio别名、第3章Pomerancio异拼和第4章注3的Roncalli校改讨论相合；既有manifest无同名person KU。\n"
        f"- 第4章关于Romanelli/Pomarancio抄写问题的说明保留Haskell转述与Nicolson可能性限定。8条直接S2陈述均为关系候选，全部留待S6；本轮未新增正式关系。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增5条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Cristoforo Roncalli 跨三章身份组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-2218`（Q-R.csv#145）保持S3组 `{GROUP}`，登记为 `{KU_ID}`。索引列第2章p.30、第3章p.69和第4章p.94注；第2章直接给出Painter Cristoforo Roncalli, known as Pomarancio，第3章用Pomerancio，第4章讨论Romanelli/Pomarancio校改及Nicolson提出的抄写可能。现有person KU无同名命中，未访问外部身份源。\n"
        "- 卡片保留Pomarancio/Pomerancio两种书内拼写，并将校改解释标为Haskell转述；不据该注释独立声称原信确写Roncalli或Pomarancio。\n"
        "- 8条直接S2 statements均为relation_candidate，涉及出行、绘画/祭坛画、作品购藏、Oratorians、Giustiniani及信件校读，全部留待S6逐条审查。本轮不新增`relations.csv`边，不合并或新建作品KU。\n"
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
                backup.write_text("NEW FILE: created by S4 Cristoforo Roncalli registration\n", encoding="utf-8")
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
