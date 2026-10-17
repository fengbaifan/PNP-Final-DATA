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

GROUP = "new-person:amedeo-ii-of-savoy-vittorio-bf13fb4fc0"
CANDIDATE_ID = "cand-2388"
ALIGNMENT_ID = "aln-2723"
KU_ID = "units/persons/vittorio-amedeo-ii-duke-of-savoy"
CARD_REL = "04-knowledge/units/persons/vittorio-amedeo-ii-duke-of-savoy.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-vittorio-amedeo-ii-20261016"
DISPLAY_NAME = "维托里奥·阿梅代奥二世"
NAME_EN = "Vittorio Amedeo II, Duke of Savoy"
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
            "location": "全书索引 S.csv#76；列第3章p.89、第7章pp.200、202",
            "sentence_summary": "索引主项为Savoy, Vittorio Amedeo II, Duke of，并将三页列在同一人物项下。",
            "original_quotes": [
                {"source_span": "S.csv#76", "text": "Savoy, Vittorio Amedeo II, Duke of"}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/S.csv",
                "source_span": "S.csv#76",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第3章 p.89；OCR L125–135",
            "sentence_summary": "Haskell将该事件置于1680年Oliva召Pozzo赴罗马之后，称萨伏依公爵要求Pozzo返往装饰一座未具名画廊。",
            "original_quotes": [
                {
                    "source_span": "lines 125, 133–135; print p. 89",
                    "text": "The Duke of Savoy, in whose service the artist had previously worked",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "lines 125–135; print p. 89",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章 p.200；OCR L7–10",
            "sentence_summary": "Haskell在西班牙王位继承战争语境中以Victor Amadeus of Savoy称呼该公爵。",
            "original_quotes": [
                {
                    "source_span": "line 10; print p. 200",
                    "text": "Victor Amadeus of Savoy",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
                "source_span": "line 10; print p. 200",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章 p.202；OCR L59–60",
            "sentence_summary": "Haskell称Victor Amadeus与Juvarra改变了Turin的艺术赞助局面，并吸引外地画家或至少其作品。",
            "original_quotes": [
                {
                    "source_span": "lines 59–60; print p. 202",
                    "text": "Victor Amadeus was able, with the help of his artistic dictator Filippo Juvarra, to change all this",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
                "source_span": "lines 59–60; print p. 202",
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
    idx = "[全书索引 S.csv#76](../../../02-sources/03-Index/03-2-Index-CSV/S.csv)"
    ch3 = "[第3章 p.89](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L125–135）"
    ch7p200 = "[第7章 p.200](../../../02-sources/02-Markdown/07_CHP-7_sec_v.md)（L7–10）"
    ch7p202 = "[第7章 p.202](../../../02-sources/02-Markdown/07_CHP-7_sec_v.md)（L59–60）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录全书索引中的 Vittorio Amedeo II, Duke of Savoy。索引将第3章p.89和第7章pp.200、202列在同一主项下；第3章将Pozzo与公爵的事件置于1680年赴罗马之后，第7章叙述Victor Amadeus of Savoy在西班牙王位继承战争中的转向及其与Juvarra对Turin艺术赞助的影响。中文展示名为项目工作音译。{idx} {ch3} {ch7p200} {ch7p202}

**English:** This unit records Vittorio Amedeo II, Duke of Savoy, as indexed. The index places Chapter 3, p. 89, and Chapter 7, pp. 200 and 202, under the same entry. Chapter 3 situates the Duke’s dealings with Pozzo after the 1680 summons to Rome; Chapter 7 describes Victor Amadeus of Savoy during the War of the Spanish Succession and his and Juvarra’s effect on artistic patronage in Turin. The Chinese display name is a project working transliteration. {idx} {ch3} {ch7p200} {ch7p202}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Vittorio Amedeo II, Duke of Savoy | S1，S.csv#76 |
| 索引形式 | Savoy, Vittorio Amedeo II, Duke of | S1，S.csv#76 |
| 书内姓名形式 | Victor Amadeus of Savoy | S2，第7章 p.200 |
| 身份 | Duke of Savoy | S2，第3章 p.89；第7章 p.200 |

### 本书相关语境

第3章在1680年Oliva召Pozzo赴罗马的叙述后，记录公爵曾召回Pozzo装饰未具名画廊，并向教会当局交涉；第7章在西班牙王位继承战争背景下称Victor Amadeus of Savoy脱离Louis XIV的控制，并叙述他与Juvarra推动Turin艺术赞助。索引将页89、200、202列入同一人物项；对书中九条关系候选仍分别保留其对象、限定和未决端点。{ch3} {ch7p200} {ch7p202}

Chapter 3 records the Duke’s recall of Pozzo to decorate an unnamed gallery after Oliva’s 1680 summons to Rome, followed by appeals to church authorities. Chapter 7 describes Victor Amadeus of Savoy breaking from Louis XIV during the War of the Spanish Succession and his and Juvarra’s role in Turin’s artistic patronage. The index places pp. 89, 200, and 202 under one person entry; nine relation candidates retain their individual objects, qualifications, and unresolved endpoints. {ch3} {ch7p200} {ch7p202}

## 关系与证据

### 身份与外部链接

本卡仅登记书内身份依据；当前没有外部身份链接。

This unit records identity evidence from the book; no external identity link is currently recorded.

### 关系记录

当前没有正式关系记录。书内9条直接关系候选保留在断言账本中，尚未转为正式关系；另有1条关于公爵误以为耶稣会拒绝许可的陈述按S2登记为非关系候选。

No formal relations are recorded. Nine direct relation candidates from the book remain in the statement ledger and have not been converted into formal relations; one additional statement about the Duke’s reported belief that the Jesuits had refused permission remains classified as a non-relation candidate in S2.
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Vittorio Amedeo II of Savoy in S4.")
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
        row.get("type") == "person" and row.get("name_en", "").casefold() in {
            NAME_EN.casefold(), "victor amadeus of savoy", "vittorio amedeo ii"
        }
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/S.csv").read_text(encoding="utf-8-sig")
    ch3 = (ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md").read_text(encoding="utf-8-sig")
    ch7 = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_v.md").read_text(encoding="utf-8-sig")
    assert "Savoy, Vittorio Amedeo II, Duke of" in index_text
    assert "When in 1680 General Oliva summoned" in ch3 and "The Duke of Savoy, in whose service" in ch3
    assert "Victor Amadeus of Savoy broke loose" in ch7
    assert "Victor Amadeus was able, with the help of his artistic dictator" in ch7

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
    assert len(direct_statements) == 10 and len(relation_candidates) == 9

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
        f"### S4 person：Vittorio Amedeo II, Duke of Savoy 跨两章身份组登记（{DATE}）\n\n"
        f"- `cand-2388`（S.csv#76，pp.89、200、202）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`。p.89叙述置于1680年Oliva召Pozzo赴罗马之后；p.200–202转入西班牙王位继承战争，索引将三页列在同一姓名项下，年代语境相容。\n"
        f"- 卡片保留索引姓名`Vittorio Amedeo II`与正文形式`Victor Amadeus of Savoy`，只记录萨伏依公爵身份和书内语境；9条直接S2陈述为关系候选，另1条信念陈述为非关系候选。本轮不新增正式边。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Vittorio Amedeo II, Duke of Savoy 跨两章身份组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-2388`（S.csv#76）保持S3组 `{GROUP}`，登记为 `{KU_ID}`。索引同一主项列p.89、200、202；p.89段落接在1680年Oliva召Pozzo赴罗马之后，p.200–202进入西班牙王位继承战争及Turin艺术赞助，年代语境相容。S3按完整姓名/显式异名锚点分组；现有manifest无Vittorio/ Victor Amadeus II人物卡，未访问外部身份源。\n"
        "- 卡片保留索引形式`Vittorio Amedeo II, Duke of Savoy`和正文拼写`Victor Amadeus of Savoy`，不以标题推演未见于原文的生平信息。\n"
        "- 10条直接S2 statements中9条为relation_candidate，1条记录公爵的误认并按非关系陈述保留。9条涉及Pozzo任职/召回/许可、对教宗申诉、对耶稣会施压、未具名个人信件、与Juvarra共同改变Turin局面、吸引画家或作品及追随其他赞助人先例；全部留待S6。本轮不写`relations.csv`，不把绘画/作品分支消歧。\n"
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
                backup.write_text("NEW FILE: created by S4 Vittorio Amedeo II registration\n", encoding="utf-8")
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
