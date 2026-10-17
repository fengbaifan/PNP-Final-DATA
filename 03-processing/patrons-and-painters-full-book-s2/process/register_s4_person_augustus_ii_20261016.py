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

GROUP = "new-person:augustus-ii-of-poland-e7b26d3f40"
CANDIDATE_IDS = ["cand-0146", "cand-0147"]
PRIMARY_ALIGNMENT_IDS = ["aln-0481", "aln-0482"]
EXTERNAL_ALIGNMENT_IDS = ["aln-12611", "aln-12612"]
KU_ID = "units/persons/augustus-ii-of-poland"
CARD_REL = "04-knowledge/units/persons/augustus-ii-of-poland.md"
CARD_PATH = ROOT / CARD_REL
GND_ID = "118505084"
GND_URL = "https://www.deutsche-biographie.de/gnd118505084.html"
SAEBI_URL = "https://saebi.isgv.de/biografie/Friedrich_August_I._von_Sachsen_(1670-1733)"
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-augustus-ii-of-poland-20261016"

BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
GND_CITATION = (
    f"‘Friedrich August I.’, *Deutsche Biographie*, GND 118505084. {GND_URL} Accessed {DATE}."
)
SAEBI_CITATION = (
    f"Winfried Müller, ‘Friedrich August I.,’ *Sächsische Biografie*, article 1925. {SAEBI_URL} Accessed {DATE}."
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
            "location": "全书索引 A.csv#147；索引转录行148",
            "sentence_summary": "索引主项将Augustus II of Poland与Frederick Augustus I、萨克森选帝侯身份并列，并指向pp.266、278、294。",
            "original_quotes": [{"source_span": "A.csv#147", "text": "Augustus II of Poland"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
                "source_span": "A.csv#147",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "全书索引 A.csv#148；索引转录行149",
            "sentence_summary": "同一索引人物主项下的patronage of Venetian artists子项，定位p.294。",
            "original_quotes": [{"source_span": "A.csv#148", "text": "patronage of Venetian artists"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
                "source_span": "A.csv#148",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.278；OCR L26–41",
            "sentence_summary": "Haskell将Diziani在Dresden任舞台画家三年的宫廷称为Augustus the Strong；该称谓与p.294所列Augustus II同指一人。",
            "original_quotes": [{"source_span": "lines 31–32; print p. 278", "text": "Augustus the Strong"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "lines 26–41; print p. 278",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章 p.294；OCR L292–302",
            "sentence_summary": "Haskell以Frederick Augustus I、萨克森选帝侯和波兰国王Augustus II ‘the Strong’明确对应该人物，并与其子、1733年继位的Augustus III区分。",
            "original_quotes": [
                {"source_span": "line 293; print p. 294", "text": "Frederick Augustus I"},
                {"source_span": "line 293; print p. 294", "text": "King of Poland as Augustus II"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "lines 292–302; print p. 294",
            },
        },
        {
            "citation": GND_CITATION,
            "url": GND_URL,
            "accessed_date": DATE,
            "location": "Deutsche Biographie, GND 118505084, lines 27–45, 248–259",
            "sentence_summary": "GND规范条目为Friedrich August I，记其1670年生于Dresden、1733年卒于Warschau，职能包括萨克森选帝侯与波兰国王，并列August II、August der Starke等异名。",
            "original_quotes": [
                {"source_span": "lines 27–40", "text": "Friedrich August I.; 1670–1733; Kurfürst von Sachsen; König von Polen"},
                {"source_span": "lines 42–45", "text": "August der Starke; August II. (als König von Polen)"},
            ],
            "evidence_ref": {"source_url": GND_URL, "source_span": "GND 118505084, lines 27–45, 248–259"},
        },
        {
            "citation": SAEBI_CITATION,
            "url": SAEBI_URL,
            "accessed_date": DATE,
            "location": "Sächsische Biografie, article 1925, lines 31–42, 54–71",
            "sentence_summary": "Winfried Müller以Friedrich August I (August II, der Starke)为条目名，叙述其萨克森选帝侯和波兰国王身份，并区分其子Friedrich August II (August III)。",
            "original_quotes": [
                {"source_span": "lines 40–42", "text": "Friedrich August I. (August II., der Starke); König von Polen (August II.)"},
            ],
            "evidence_ref": {"source_url": SAEBI_URL, "source_span": "article 1925, lines 31–42, 54–71"},
        },
    ]
    frontmatter = {
        "title": "波兰国王奥古斯都二世（Augustus II of Poland）",
        "name_en": "Augustus II of Poland",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx_main = "[全书索引 A.csv#147](../../../02-sources/03-Index/03-2-Index-CSV/A.csv)"
    idx_sub = "[全书索引 A.csv#148](../../../02-sources/03-Index/03-2-Index-CSV/A.csv)"
    p278 = "[第10章 p.278](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L26–41）"
    p294 = "[第10章 p.294](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L292–302）"
    gnd_md = f"[Deutsche Biographie GND 118505084]({GND_URL})"
    saebi_md = "[Sächsische Biografie: Friedrich August I.](https://saebi.isgv.de/biografie/Friedrich_August_I._von_Sachsen_%281670-1733%29)"
    body = f"""## 内容

### 描述

**中文：** 本卡登记《赞助人与画家》索引所称的波兰国王奥古斯都二世。索引主项以“Augustus II of Poland”并列其萨克森选帝侯姓名，子项记录对威尼斯画家的赞助语境；第10章p.294直接将Frederick Augustus I与波兰国王Augustus II对应，p.278使用“Augustus the Strong”。Deutsche Biographie与Sächsische Biografie均将其识别为Friedrich August I（August II，the Strong），1670–1733。既有Augustus III人物卡指向其子Friedrich August II，二者保持分立；亲属和赞助关系仍由原始statement承载，待S6审查。中文名为项目工作译名。{idx_main} {idx_sub} {p278} {p294} {gnd_md} {saebi_md}

**English:** This unit records Augustus II of Poland as indexed in *Patrons and Painters*. The main index entry pairs that name with his Saxon electoral identity, while the subentry points to patronage of Venetian artists. Chapter 10, p. 294, directly identifies Frederick Augustus I with the King of Poland Augustus II; p. 278 uses “Augustus the Strong.” Deutsche Biographie and Sächsische Biografie identify him as Friedrich August I (August II, the Strong), 1670–1733. The existing Augustus III unit refers to his son Friedrich August II and remains separate; kinship and patronage claims stay in the source statements for S6 review. The Chinese display name is a project working translation. {idx_main} {idx_sub} {p278} {p294} {gnd_md} {saebi_md}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Friedrich August I | S3，GND 118505084；Sächsische Biografie |
| 本书索引形式 | Augustus II of Poland (Frederick Augustus I, Elector of Saxony) | S1，A.csv#147 |
| 本书索引子目 | patronage of Venetian artists | S1，A.csv#148 |
| 本书别称 | Augustus the Strong | S2，{p278}；{p294} |
| 身份 | 萨克森选帝侯；波兰国王（Augustus II） | S3，GND 118505084；Sächsische Biografie；S2，{p294} |

### 生平信息

| 字段 | 值 | 证据 |
|---|---|---|
| 出生日期 | 1670年5月12日 | S3，GND 118505084 |
| 出生地 | Dresden | S3，GND 118505084 |
| 去世日期 | 1733年2月1日 | S3，GND 118505084 |
| 去世地 | Warsaw | S3，GND 118505084 |

### 本章相关内容

第10章p.278将Diziani在Dresden宫廷任职的场景称为Augustus the Strong；p.294则写明Frederick Augustus I同时为萨克森选帝侯与波兰国王Augustus II，并分别描述Dresden的艺术赞助与收藏。本文只以这些内容作为身份与语境锚点，不把书中具体雇佣、购藏或其他关系陈述在本次登记中确立为正式关系。Haskell将继位的Augustus III明确说成Augustus II之子；这一父子身份边界也由两条外部传记支持。{p278} {p294}

## 关系与证据

### 身份与外部链接

| 字段 | 值／链接 | 状态与范围 | 证据 |
|---|---|---|---|
| Deutsche Biographie / GND | {gnd_md} | GND 118505084支持规范姓名、生卒信息、身份及别名 | S3 |
| Sächsische Biografie | {saebi_md} | 支持Friedrich August I与Augustus II的姓名对应、职务及与Augustus III的身份区分 | S3 |

### 关系记录

本卡未新增正式关系。与Augustus III的人物亲缘、对威尼斯艺术家的赞助及其收藏陈述仍待S6逐条审查。

### 关系候选入口

[全书关系候选与端点记录](../../../03-processing/{TASK}/process/knowledge.md)
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Augustus II person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert all(cid in candidate_by_id for cid in CANDIDATE_IDS)
    assert [candidate_by_id[cid].get("suggested_type") for cid in CANDIDATE_IDS] == ["person", "person"]
    primary_rows = [row for row in alignment if row.get("alignment_id") in PRIMARY_ALIGNMENT_IDS]
    external_rows = [row for row in alignment if row.get("alignment_id") in EXTERNAL_ALIGNMENT_IDS]
    assert len(primary_rows) == 2 and len(external_rows) == 2
    assert [row.get("candidate_id") for row in primary_rows] == CANDIDATE_IDS
    assert all(row.get("decision") == "new" and not row.get("ku_id") and GROUP in row.get("resolution_note", "") for row in primary_rows)
    assert all(row.get("candidate_id") == CANDIDATE_IDS[0] and row.get("decision") == "new" and not row.get("ku_id") for row in external_rows)
    assert external_rows[0].get("external_id") == GND_ID
    assert external_rows[1].get("external_id") == SAEBI_URL
    group_rows = [
        row for row in alignment
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and GROUP in row.get("resolution_note", "")
    ]
    assert [row.get("candidate_id") for row in group_rows] == CANDIDATE_IDS
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert any(row.get("ku_id") == "units/persons/augustus-iii-of-poland" for row in manifest)
    assert not any(
        row.get("type") == "person" and row.get("name_en") == "Augustus II of Poland"
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    chapter10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    # The source index CSV is legacy Windows-1252; preserve it and decode only for this read-only anchor check.
    index_a = (ROOT / "02-sources/03-Index/03-2-Index-CSV/A.csv").read_text(encoding="cp1252")
    assert "scene painter for Augustus the Strong" in chapter10
    assert "Frederick Augustus I, Elector of Saxony, and since 1697 King of Poland as Augustus II" in chapter10
    assert "patronage of Venetian artists" in index_a

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    relation_candidates = [
        row for row in statements
        if row.get("qualifiers", {}).get("relation_candidate")
        and (
            row.get("subject_candidate_id") in CANDIDATE_IDS
            or row.get("object_candidate_id") in CANDIDATE_IDS
        )
    ]
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") in CANDIDATE_IDS or row.get("object_candidate_id") in CANDIDATE_IDS
    ]
    assert len(direct_statements) == 10 and len(relation_candidates) == 9

    planned_alignment = [dict(row) for row in alignment]
    for aid in PRIMARY_ALIGNMENT_IDS + EXTERNAL_ALIGNMENT_IDS:
        row = next(item for item in planned_alignment if item.get("alignment_id") == aid)
        row["ku_id"] = KU_ID
        row["resolution_note"] += f" S4 registration ({DATE}): mapped this member/identity record to {KU_ID} under group {GROUP}."

    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "波兰国王奥古斯都二世",
        "name_en": "Augustus II of Poland",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 6

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    old_result = "KU 尚未登记；10条直接 S2 陈述中的9条关系候选留待 S6。"
    new_result = f"现已登记为[Augustus II人物卡](../units/persons/augustus-ii-of-poland.md)；10条直接 S2 陈述中的9条关系候选仍留待 S6。"
    if result_text.count(old_result) != 1:
        raise ValueError("Could not update the current S3 Augustus II status in the result.")
    result_text = result_text.replace(old_result, new_result, 1)
    result_insert = (
        f"### S4 person：Augustus II of Poland 双候选组登记（{DATE}）\n\n"
        f"- `cand-0146` 与 `cand-0147` → `{GROUP}` → `{KU_ID}`。新增双语人物卡、manifest、accepted路径；两条候选决定行及 GND/Sächsische Biografie 外部身份行共同映射到该KU。\n"
        "- Deutsche Biographie GND 118505084与Winfried Müller的Sächsische Biografie条目支持Friedrich August I = Augustus II、选帝侯/波兰国王身份及1670–1733年生卒。Haskell第10章p.294明示同一对应，p.278的“Augustus the Strong”是相同别称。既有 Augustus III 卡保持独立。\n"
        f"- 10条直接S2陈述中9条为关系候选，仍待S6逐项审查；无正式关系写入。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组、待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。字段事实待 `build_field_facts.py` 预检登记。\n\n"
    )
    result_marker = "## 未解决项与交接限制"
    assert result_text.count(result_marker) == 1
    result_text = result_text.replace(result_marker, result_insert + result_marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Augustus II of Poland 双候选组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-0146`（A.csv#147，pp.266、278、294）与索引子项 `cand-0147`（A.csv#148，p.294）共同映射至 `{KU_ID}`；同一S3组内两条候选分别保留各自来源锚点。GND 118505084（aln-12611）与Sächsische Biografie（aln-12612）此前已在S3确认姓名对应、萨克森选帝侯/波兰国王身份及1670–1733年生卒；本轮将两行与两条候选决定一并映射。\n"
        "- Haskell第10章p.294将Frederick Augustus I与波兰国王Augustus II ‘the Strong’明确对应；p.278以同一别称称Diziani工作的Dresden宫廷。既有 Augustus III 卡属于其子Friedrich August II，身份保持分立，不把父子或赞助陈述写入relations.csv。\n"
        "- 新卡记录双语标题、索引/正文名称锚点、外部规范名、生卒及选帝侯/波兰国王身份。10条直接S2端点陈述中9条为关系候选，全部留待S6；本轮没有新增正式关系。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。字段表待 `build_field_facts.py` dry-run/apply。\n"
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
            f"dry-run passed: {CANDIDATE_IDS}->{GROUP}->{KU_ID}; external={EXTERNAL_ALIGNMENT_IDS}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
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
                backup.write_text("NEW FILE: created by S4 Augustus II registration\n", encoding="utf-8")
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
        f"applied: {CANDIDATE_IDS}->{GROUP}->{KU_ID}; external={EXTERNAL_ALIGNMENT_IDS}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"direct_statements={len(direct_statements)}; relation_candidates={len(relation_candidates)}; backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
