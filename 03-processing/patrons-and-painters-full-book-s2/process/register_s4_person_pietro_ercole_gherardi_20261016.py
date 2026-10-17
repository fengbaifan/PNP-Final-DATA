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

GROUP = "new-person:ercole-gherardi-pietro-8af999ae11"
CANDIDATE_ID = "cand-1155"
ALIGNMENT_ID = "aln-1490"
KU_ID = "units/persons/pietro-ercole-gherardi"
CARD_REL = "04-knowledge/units/persons/pietro-ercole-gherardi.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-pietro-ercole-gherardi-20261016"

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
            "location": "全书索引 G.csv#62；定位第9、10、13章相关页段",
            "sentence_summary": "索引以Gherardi, Abate Pietro Ercole为主项，列出pp.236n、261n、271、272、275n、300n、302n、336n。",
            "original_quotes": [{"source_span": "G.csv#62", "text": "Gherardi, Abate Pietro Ercole"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/G.csv",
                "source_span": "G.csv#62",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章 p.261 注8；OCR L408",
            "sentence_summary": "注释列出P. E. Gherardi于1745年2月20日致L. A. Muratori的信，并指明藏于摩德纳埃斯滕塞图书馆；原信未在本批查阅。",
            "original_quotes": [{"source_span": "line 408; print p. 261 n. 8", "text": "Letter from P. E. Gherardi to L. A. Muratori of 20 February 1745 in Biblioteca Estense, Modena."}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "line 408; print p. 261 n. 8",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章 p.271 注1、p.275 注2；OCR L103、L127",
            "sentence_summary": "Haskell分别列出P. E. Gherardi于1742年10月26日和1746年2月20日致Muratori的信，均指向埃斯滕塞图书馆；不将书目引文当作已读原件。",
            "original_quotes": [
                {"source_span": "line 103; print p. 271 n. 1", "text": "Letter from P. E. Gherardi to Muratori of 26 October 1742 in the Biblioteca Estense, Modena."},
                {"source_span": "line 127; print p. 275 n. 2", "text": "On 20 February 1746 P. E. Gherardi wrote to Muratori (letter in Biblioteca Estense, Modena)"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
                "source_span": "lines 103, 127; print pp. 271 n. 1, 275 n. 2",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.302 注4；OCR L598",
            "sentence_summary": "Haskell写出Abate Pietro Ercole Gherardi全名，称其为一篇描述Smith所藏Cignani与Ricci作品的Descrizione作者、Muratori的摩德纳友人，并称二人有存于埃斯滕塞图书馆的长期通信。",
            "original_quotes": [{"source_span": "line 598; print p. 302 n. 4", "text": "The Abate Pietro Ercole Gherardi, who wrote the Descrizione of Smith’s Cignanis and Riccis, was a Modenese friend of Muratori with whom he engaged in a long correspondence, now in the Biblioteca Estense, Modena."}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 598; print p. 302 n. 4",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第13章 p.336；OCR L41–50、L202（注8）",
            "sentence_summary": "正文将一位1749年直言的共同朋友的评论归于Gherardi；注8列出其于1749年7月12日致L. A. Muratori的信及埃斯滕塞图书馆馆藏信息。",
            "original_quotes": [{"source_span": "line 202; print p. 336 n. 8", "text": "Letter from P. E. Gherardi to L. A. Muratori of 12 July 1749 in the Biblioteca Estense, Modena"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "source_span": "lines 41–50, 202; print p. 336 and n. 8",
            },
        },
    ]
    frontmatter = {
        "title": "彼得罗·埃尔科莱·盖拉尔迪（Pietro Ercole Gherardi）",
        "name_en": "Pietro Ercole Gherardi",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 G.csv#62](../../../02-sources/03-Index/03-2-Index-CSV/G.csv)"
    ch9i = "[第9章 p.261 注8](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L408）"
    ch9ii = "[第9章 pp.271、275注](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L103、L127）"
    ch10 = "[第10章 p.302 注4](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L598）"
    ch13 = "[第13章 p.336](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L41–50、L202）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录《赞助人与画家》索引所列的 Pietro Ercole Gherardi。第10章p.302注4给出全名；第9章和第13章多处以缩写P. E. Gherardi称呼此人。Haskell称其为Muratori的摩德纳友人，并将一篇Descrizione及多封书信与他相关联；这些作品和通信主张仍按原书证据范围保留，不扩写为独立核实的关系或作品记录。中文显示名为项目工作音译。{idx} {ch9i} {ch9ii} {ch10} {ch13}

**English:** This unit records Pietro Ercole Gherardi as listed in the index of *Patrons and Painters*. Chapter 10, p. 302 n. 4, gives his full name; Chapter 9 and Chapter 13 also refer to him as P. E. Gherardi. Haskell describes him as a Modenese friend of Muratori and associates him with a *Descrizione* and several letters. These work and correspondence claims remain within the book’s evidence and are not expanded into independently verified relations or work records. The Chinese display name is a project working transliteration. {idx} {ch9i} {ch9ii} {ch10} {ch13}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Pietro Ercole Gherardi | S4，第10章 p.302 注4 |
| 索引形式 | Gherardi, Abate Pietro Ercole | S1，G.csv#62 |
| 正文缩写 | P. E. Gherardi | S2，第9章 p.261 注8 |
| 称谓 | Abate | S4，第10章 p.302 注4 |

### 本书相关语境

索引 G.csv#62 列出 pp.236n、261n、271、272、275n、300n、302n、336n。第9章pp.261、271、275的注释将多封P. E. Gherardi致Muratori的信定位到摩德纳埃斯滕塞图书馆；这些手稿本身未在本批查阅。第10章p.302注4称Gherardi撰写一篇关于Smith所藏Cignani与Ricci作品的Descrizione，但该对象的题名、版本和实体边界并不明确；对应S2候选 `cand-9192` 仍待裁决，不在此登记为作品或archive KU。第13章p.336注8另列1749年信件，并引述Gherardi对Albrizzi与Pasquali的评价。相关人员、书信和著述关系留待S6逐条审查。{idx} {ch9i} {ch9ii} {ch10} {ch13}

The index entry G.csv#62 lists pp. 236n, 261n, 271, 272, 275n, 300n, 302n, and 336n. Chapter 9 notes identify several letters from P. E. Gherardi to Muratori at the Biblioteca Estense in Modena; the manuscripts were not consulted in this batch. Chapter 10, p. 302 n. 4, says Gherardi wrote a *Descrizione* of Smith’s Cignani and Ricci works, but does not settle that item’s exact title, edition, or object boundary; the corresponding S2 candidate `cand-9192` remains unresolved and is not registered here as a work or archive KU. Chapter 13, p. 336 n. 8, lists another letter from 1749 and quotes Gherardi’s comments on Albrizzi and Pasquali. Relations to people, letters, and writings remain for item-by-item S6 review. {idx} {ch9i} {ch9ii} {ch10} {ch13}

## 关系与证据

### 关系记录

本轮未新增正式关系。书中关于Muratori、Descrizione、书信及相关人物的陈述继续保留在原S2 statements；archive候选与 `cand-9192` 的对象边界仍各自待证。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Pietro Ercole Gherardi in S4.")
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
    assert not any(
        row.get("type") == "person" and row.get("name_en") == "Pietro Ercole Gherardi"
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_g = (ROOT / "02-sources/03-Index/03-2-Index-CSV/G.csv").read_text(encoding="cp1252")
    assert "Gherardi, Abate Pietro Ercole" in index_g
    assert "The Abate Pietro Ercole Gherardi" in (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    assert "Letter from P. E. Gherardi to L. A. Muratori of 12 July 1749" in (ROOT / "02-sources/02-Markdown/13_CHP-13_intro.md").read_text(encoding="utf-8-sig")

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
    assert len(direct_statements) == 10 and len(relation_candidates) == 7

    planned_alignment = [dict(row) for row in alignment]
    mapped = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "彼得罗·埃尔科莱·盖拉尔迪",
        "name_en": "Pietro Ercole Gherardi",
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
        f"### S4 person：Pietro Ercole Gherardi 跨章候选登记（{DATE}）\n\n"
        f"- `cand-1155`（G.csv#62）→ `{GROUP}` → `{KU_ID}`。新增双语人物卡、manifest、accepted路径；候选决定行映射至该KU。第10章p.302注4给出全名，索引与第9、13章缩写称名相互对应；未增加外部身份或生平事实。\n"
        f"- 该候选跨第9、10、13章有10条直接S2陈述，其中7条为关系候选，均留待S6；另3条为非关系陈述。Haskell所引书信未作为已读原件；`cand-9192` 描述的文献对象仍待裁决，本轮未登记archive/work KU或正式关系。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组、待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Pietro Ercole Gherardi 跨章候选登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-1155`（G.csv#62）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`；第10章p.302注4给出全名，章9和13的P. E. Gherardi缩写与索引页码对应。无既有人物KU命中；新卡不补外部生平字段。\n"
        "- 书内身份语境包括Haskell称其为Modenese、Muratori的友人及一篇Descrizione作者；相关书信、作品及人物关系不在此转为正式边。第9章多个脚注仅列信件与Biblioteca Estense馆藏信息，原件未查阅。S2候选 `cand-9192` 的出版物题名、版本与对象粒度未定，仍保持undecided；相关archive候选各自保留身份组，不合并为一个文献。\n"
        "- 10条直接S2陈述中7条为关系候选，均留待S6；另3条为非关系陈述。本轮未新增 `relations.csv` 边、archive/work KU或外部身份记录。\n"
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
                backup.write_text("NEW FILE: created by S4 Pietro Ercole Gherardi registration\n", encoding="utf-8")
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
