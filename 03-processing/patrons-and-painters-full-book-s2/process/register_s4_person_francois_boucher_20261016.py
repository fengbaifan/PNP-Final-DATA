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

GROUP = "new-person:boucher-francois-2b86c8ca6d"
CANDIDATE_IDS = ["cand-0421", "cand-0422", "cand-0423"]
ALIGNMENT_IDS = ["aln-0756", "aln-0757", "aln-0758"]
KU_ID = "units/persons/francois-boucher"
CARD_REL = "04-knowledge/units/persons/francois-boucher.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-francois-boucher-20261016"

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
            "location": "全书索引 B.csv#268–270；定位第9、10、13、14章相关页段",
            "sentence_summary": "三条同名索引记录均列Boucher, François；其中两个子目分别为and Count Tessin与designs for Tombeaux des Princes。",
            "original_quotes": [
                {"source_span": "B.csv#268", "text": "Boucher, François"},
                {"source_span": "B.csv#269", "text": "and Count Tessin"},
                {"source_span": "B.csv#270", "text": "designs for Tombeaux des Princes"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
                "source_span": "B.csv#268–270",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章 p.257；OCR L177",
            "sentence_summary": "Haskell以Boucher和Fragonard作为法国洛可可绘画的例子，并称威尼斯没有相应人物。",
            "original_quotes": [{"source_span": "line 177; print p. 257", "text": "There is no Venetian equivalent to a Boucher or a Fragonard"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "line 177; print p. 257",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.291；OCR L253–266、L551（注1）",
            "sentence_summary": "Haskell称Boucher设计了《Tombeaux des Princes》中的英雄铭牌装饰框，并为Newton纪念铭牌绘制奖章图案。",
            "original_quotes": [
                {"source_span": "lines 260–261; print p. 291", "text": "a rich decorative frieze designed by Boucher"},
                {"source_span": "line 551; print p. 291 n. 1", "text": "Boucher, however, drew the medallion of Newton and the signs of the Zodiac"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "lines 253–266, 551; print p. 291 and n. 1",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.293；OCR L279–290",
            "sentence_summary": "Haskell将Boucher列为Tessin收藏中的突出法国艺术家，并称Tessin曾于1737年向他订画。",
            "original_quotes": [{"source_span": "lines 279–290; print p. 293", "text": "especially Boucher"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "lines 279–290; print p. 293",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第13章 p.335；OCR L35–37",
            "sentence_summary": "Haskell比较Piazzetta《耶路撒冷的解放》牧歌式构图与Boucher，并判断Piazzetta描绘的世界较不人工。",
            "original_quotes": [{"source_span": "lines 36–37; print p. 335", "text": "have some of the quality of Boucher"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "source_span": "lines 35–37; print p. 335",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章 p.351；OCR L50–51",
            "sentence_summary": "Haskell记Algarotti将Boucher列入拟为画廊绘制轻快雅致题材的艺术家名单，并说明该计划需要法国与意大利艺术家合作。",
            "original_quotes": [{"source_span": "lines 50–51; print p. 351", "text": "he included Boucher among the artists to be given ‘soggetti graziosi e leggeri’"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "source_span": "lines 50–51; print p. 351",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章 p.354；OCR L77–78",
            "sentence_summary": "Haskell以Boucher在巴黎形成风尚的风格描述Algarotti所订《戴安娜浴场》的特点。",
            "original_quotes": [{"source_span": "lines 77–78; print p. 354", "text": "in the style which Boucher had made fashionable in Paris"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "source_span": "lines 77–78; print p. 354",
            },
        },
    ]
    frontmatter = {
        "title": "弗朗索瓦·布歇（François Boucher）",
        "name_en": "François Boucher",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 B.csv#268–270](../../../02-sources/03-Index/03-2-Index-CSV/B.csv)"
    ch9 = "[第9章 p.257](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L177）"
    ch10p291 = "[第10章 p.291](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L253–266、L551）"
    ch10p293 = "[第10章 p.293](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L279–290）"
    ch13 = "[第13章 p.335](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L35–37）"
    ch14p351 = "[第14章 p.351](../../../02-sources/02-Markdown/14_CHP-14_intro.md)（L50–51）"
    ch14p354 = "[第14章 p.354](../../../02-sources/02-Markdown/14_CHP-14_intro.md)（L77–78）"
    body = f"""## 内容

### 描述

**中文：** 本卡合并《赞助人与画家》索引中三条明确写作“Boucher, François”的人物候选：主项、and Count Tessin子项及designs for Tombeaux des Princes子项。第9、10、13、14章的Boucher称名均落在相应法国绘画、版画设计及艺术赞助语境中。身份范围依据书内全名和跨章上下文，不补入书外生平、作品目录或外部身份信息。中文显示名为项目工作音译。{idx} {ch9} {ch10p291} {ch10p293} {ch13} {ch14p351} {ch14p354}

**English:** This unit combines three person candidates indexed as “Boucher, François” in *Patrons and Painters*: the main entry, the “and Count Tessin” subentry, and the “designs for Tombeaux des Princes” subentry. References to Boucher in Chapters 9, 10, 13, and 14 occur in contexts of French painting, print design, and art patronage. The identity scope follows the book’s full name and cross-chapter contexts; no external biography, work catalogue, or authority identity is added. The Chinese display name is a project working transliteration. {idx} {ch9} {ch10p291} {ch10p293} {ch13} {ch14p351} {ch14p354}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | François Boucher | S1，B.csv#268–270 |
| 索引形式 | Boucher, François | S1，B.csv#268 |
| 索引子目 | and Count Tessin | S1，B.csv#269 |
| 索引子目 | designs for Tombeaux des Princes | S1，B.csv#270 |
| 正文称名 | Boucher | S2，第9章 p.257 |

### 本书相关语境

索引主项及两个子项分别指向第9、10、13、14章的不同页段。第10章p.291称Boucher为《Tombeaux des Princes》英雄铭牌的装饰设计者，并记其为Newton纪念铭牌绘制奖章图案；第10章p.293将其列入Tessin收藏语境。第13章p.335以其艺术作比较，第14章pp.351、354记载其被纳入画廊题材计划，并以其风格讨论Tiepolo画作。以上具体创作、委托、收藏及合作关系均留在原S2 statements，待S6逐条审查。{idx} {ch9} {ch10p291} {ch10p293} {ch13} {ch14p351} {ch14p354}

The index main entry and its two subentries point to different passages in Chapters 9, 10, 13, and 14. Chapter 10, p. 291, names Boucher as the designer of decorative friezes for the hero plates in *Tombeaux des Princes* and says he drew the medallion for Newton’s monument; p. 293 places him in the context of Tessin’s collection. Chapter 13, p. 335, uses his art as a comparison, and Chapter 14, pp. 351 and 354, discusses his inclusion in a gallery plan and uses his style to describe a Tiepolo painting. These specific creation, commission, collection, and collaboration claims remain in the original S2 statements for item-by-item S6 review. {idx} {ch9} {ch10p291} {ch10p293} {ch13} {ch14p351} {ch14p354}

## 关系与证据

### 关系记录

本轮未新增正式关系。三条索引候选映射至同一人物KU；7条直接S2陈述中的关系候选仍待S6审查。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the François Boucher person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert all(cid in candidate_by_id for cid in CANDIDATE_IDS)
    assert all(candidate_by_id[cid].get("suggested_type") == "person" for cid in CANDIDATE_IDS)
    primary_rows = [row for row in alignment if row.get("alignment_id") in ALIGNMENT_IDS]
    assert [row.get("alignment_id") for row in primary_rows] == ALIGNMENT_IDS
    assert [row.get("candidate_id") for row in primary_rows] == CANDIDATE_IDS
    assert all(row.get("decision") == "new" and not row.get("ku_id") and GROUP in row.get("resolution_note", "") for row in primary_rows)
    group_rows = [
        row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and GROUP in row.get("resolution_note", "")
    ]
    assert [row.get("candidate_id") for row in group_rows] == CANDIDATE_IDS
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en") == "François Boucher" for row in manifest)
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_b = (ROOT / "02-sources/03-Index/03-2-Index-CSV/B.csv").read_text(encoding="utf-8-sig")
    ch10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    assert "designs for Tombeaux des Princes" in index_b
    assert "a rich decorative frieze designed by" in ch10 and "Boucher" in ch10
    assert "he included Boucher among the artists" in (ROOT / "02-sources/02-Markdown/14_CHP-14_intro.md").read_text(encoding="utf-8-sig")

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") in CANDIDATE_IDS or row.get("object_candidate_id") in CANDIDATE_IDS
    ]
    relation_candidates = [
        row for row in direct_statements
        if row.get("qualifiers", {}).get("relation_candidate")
    ]
    assert len(direct_statements) == 7 and len(relation_candidates) == 7

    planned_alignment = [dict(row) for row in alignment]
    for aid in ALIGNMENT_IDS:
        row = next(item for item in planned_alignment if item.get("alignment_id") == aid)
        row["ku_id"] = KU_ID
        row["resolution_note"] += f" S4 registration ({DATE}): mapped this member to {KU_ID} under group {GROUP}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "弗朗索瓦·布歇",
        "name_en": "François Boucher",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 7

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_insert = (
        f"### S4 person：François Boucher 三候选跨章组登记（{DATE}）\n\n"
        f"- `cand-0421`、`cand-0422`、`cand-0423`（B.csv#268–270）→ `{GROUP}` → `{KU_ID}`。三条索引同名主项／子项候选共同映射到一张双语人物卡，新增manifest与accepted路径；未发现同名person KU。\n"
        f"- 书内索引全名及第9、10、13、14章上下文支持跨章身份组。7条直接S2陈述均为关系候选，全部留待S6；本轮没有新增正式关系或外部身份记录。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组、待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：François Boucher 三候选跨章组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-0421`（B.csv#268，主项）、`cand-0422`（B.csv#269，and Count Tessin）及`cand-0423`（B.csv#270，designs for Tombeaux des Princes）保持S3组 `{GROUP}`，现共同映射至 `{KU_ID}`。三条索引均为Boucher, François；候选子项分别定位于同一索引主项下，正文跨章以Boucher称画家/设计者。未将索引子目拆成独立person或work KU。\n"
        "- 既有manifest没有François Boucher人物卡；S3未访问外部身份源。本卡仅录书内全名、三个索引锚点和跨章语境，不补书外生平。p.291设计陈述、Tessin收藏／委托、Algarotti画廊计划、风格比较和相关人物互动仍按原S2 statements保留。\n"
        "- 三条成员候选对应的7条直接S2陈述均标为关系候选，留待S6逐项审查；未新增 `relations.csv` 边或外部身份行。\n"
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
            f"dry-run passed: {CANDIDATE_IDS}->{GROUP}->{KU_ID}; registered="
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
                backup.write_text("NEW FILE: created by S4 François Boucher registration\n", encoding="utf-8")
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
        f"applied: {CANDIDATE_IDS}->{GROUP}->{KU_ID}; registered={totals['registered_groups']}/"
        f"{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; direct_statements={len(direct_statements)}; "
        f"relation_candidates={len(relation_candidates)}; backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
