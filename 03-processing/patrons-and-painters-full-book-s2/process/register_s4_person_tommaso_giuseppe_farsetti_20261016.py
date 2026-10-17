from __future__ import annotations

import argparse
import csv
import difflib
import re
import shutil
import sys
from io import StringIO
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

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
CARD_REL = "04-knowledge/units/persons/tommaso-giuseppe-farsetti.md"
CARD_PATH = ROOT / CARD_REL
KU_ID = "units/persons/tommaso-giuseppe-farsetti"
CANDIDATE_ID = "cand-1013"
EXTERNAL_ALIGNMENT_ID = "aln-12614"
GROUP = "new-person:farsetti-giuseppe-tommaso-339a4db213"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/tommaso-giuseppe-farsetti_(Dizionario-Biografico)/"
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-tommaso-giuseppe-farsetti-20261016"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_CITATION = (
    "Paolo Preto, ‘FARSETTI, Tommaso Giuseppe,’ *Dizionario Biografico degli Italiani*, "
    "vol. 45 (1995), Treccani. " + TRECCANI_URL + f" Accessed {DATE}."
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
            "location": "全书索引 F.csv#28；索引转录行30",
            "sentence_summary": "索引以Farsetti, Tommaso Giuseppe为主项，列pp.235n、362n及364。",
            "original_quotes": [{"source_span": "F.csv#28", "text": "Farsetti, Tommaso Giuseppe; 235n, 362n, 364"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/F.csv",
                "source_span": "F.csv#28",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章 p.347n；OCR L168–170",
            "sentence_summary": "Haskell以缩写T. G. Farsetti称一篇献给Bonomo的Algarotti短篇拉丁文传记作者；卡片仅保留这是书内署名，不据此建立著作关系。",
            "original_quotes": [{"source_span": "line 169; printed p. 347 n. 1", "text": "a short and rare Latin life by T. G. Farsetti"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "source_span": "lines 168–170; printed p. 347 n. 1",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第15章 pp.362n、364；OCR L38–44",
            "sentence_summary": "Haskell p.364使用Tommaso Giuseppe全名并列1720–91；注释称相关家族史于1778年刊行。正式关系主张仍留待S6审查。",
            "original_quotes": [
                {"source_span": "line 39; printed p. 364", "text": "Tommaso Giuseppe (1720-91)"},
                {"source_span": "line 44; printed p. 364 n. 1", "text": "the family history published by his cousin Tommaso Giuseppe in 1778"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/15_CHP-15_sec_i.md",
                "source_span": "lines 38–44; printed pp. 362 n. 1, 364",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第8章 p.235n；OCR L435",
            "sentence_summary": "Haskell以T. G. Farsetti署名转引一段18世纪末描述；该嵌套引文未独立查验，不用来核实作品或引文归属。",
            "original_quotes": [{"source_span": "line 435; printed p. 235 n. 2", "text": "T. G. Farsetti referred to the ceiling as follows"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "line 435; printed p. 235 n. 8",
            },
        },
        {
            "citation": TRECCANI_CITATION,
            "url": TRECCANI_URL,
            "accessed_date": DATE,
            "location": "DBI vol. 45 (1995), ‘FARSETTI, Tommaso Giuseppe’；姓名、生卒、活动身份与地点",
            "sentence_summary": "Preto将规范条目定为Tommaso Giuseppe Farsetti，记其1720年4月16日生于威尼斯、1791年10月30日卒于帕多瓦，并称其为文人和藏书家。",
            "original_quotes": [
                {"source_span": "entry lines 21–24", "text": "FARSETTI, Tommaso Giuseppe; Nacque a Venezia il 16 apr. 1720"},
                {"source_span": "entry line 45", "text": "Il F. morì a Padova il 30 ott. 1791"},
                {"source_span": "entry line 41", "text": "Appassionato bibliofilo"},
            ],
            "evidence_ref": {
                "source_url": TRECCANI_URL,
                "source_span": "DBI vol. 45 (1995), lines 21–25, 38–45",
            },
        },
    ]
    frontmatter = {
        "title": "托马索·朱塞佩·法尔塞蒂（Tommaso Giuseppe Farsetti）",
        "name_en": "Tommaso Giuseppe Farsetti",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    index = "[全书索引 F.csv#28](../../../02-sources/03-Index/03-2-Index-CSV/F.csv)"
    ch8 = "[第8章 p.235n](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L435）"
    ch14 = "[第14章 p.347n](../../../02-sources/02-Markdown/14_CHP-14_intro.md)（L168–170）"
    ch15 = "[第15章 pp.362n、364](../../../02-sources/02-Markdown/15_CHP-15_sec_i.md)（L38–44）"
    treccani = f"[Treccani《意大利人传记辞典》条目]({TRECCANI_URL})"
    body = f"""## 内容

### 描述

**中文：** 意大利文人、藏书家。Treccani将其规范姓名列为Tommaso Giuseppe Farsetti，记其1720年4月16日生于威尼斯、1791年10月30日卒于帕多瓦。Haskell的索引、缩写署名“T. G. Farsetti”及第15章全名和生年范围共同构成本书内身份锚点；第8章嵌套转引不作为独立核实的作品证据。中文名为项目工作音译。{index} {ch8} {ch14} {ch15} {treccani}

**English:** An Italian man of letters and bibliophile. Treccani identifies him as Tommaso Giuseppe Farsetti and records his birth in Venice on 16 April 1720 and death in Padua on 30 October 1791. Haskell’s index, the abbreviated attribution “T. G. Farsetti,” and the full name and date range in Chapter 15 provide the book’s identity anchors; the nested quotation in Chapter 8 is not treated as independently verified work evidence. The Chinese name is a working transliteration. {index} {ch8} {ch14} {ch15} {treccani}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Tommaso Giuseppe Farsetti | S5，Treccani DBI |
| 本书索引形式 | Farsetti, Tommaso Giuseppe | S1，F.csv#28 |
| 本书正文缩写形式 | T. G. Farsetti | S2，{ch14}；S4，{ch8} |

### 生平信息

| 字段 | 值 | 证据 |
|---|---|---|
| 出生日期 | 1720年4月16日 | S5，Treccani DBI |
| 出生地 | 威尼斯 | S5，Treccani DBI |
| 去世日期 | 1791年10月30日 | S5，Treccani DBI |
| 去世地 | 帕多瓦 | S5，Treccani DBI |
| 身份 | 文人、藏书家 | S5，Treccani DBI |

## 关系与证据

### 身份与外部链接

{treccani}（Paolo Preto，DBI第45卷，1995；身份与生平条目）。

### 关系记录

本卡未新增正式关系。Haskell关于亲属、著述、委托、收藏及其所作作品的书内陈述仍由原始 statement 承载，待S6逐项审查；第8章经Fogolari转引的天花描述未作为独立验证事实。

### 关系候选入口

[全书关系候选与端点记录](../../../03-processing/{TASK}/process/knowledge.md)
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Tommaso Giuseppe Farsetti's person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE_ID)
    primary_matches = [
        row for row in alignment
        if row.get("candidate_id") == CANDIDATE_ID and not row.get("external_source")
    ]
    assert len(primary_matches) == 1
    primary = primary_matches[0]
    external = next(
        row for row in alignment
        if row.get("alignment_id") == EXTERNAL_ALIGNMENT_ID
        and row.get("candidate_id") == CANDIDATE_ID
        and row.get("external_source") == "Treccani DBI"
    )
    assert candidate.get("canonical_name") == "Farsetti, Tommaso Giuseppe"
    assert candidate.get("index_entry_id") == "F.csv#28"
    assert candidate.get("suggested_type") == "person"
    assert primary.get("decision") == "new" and not primary.get("ku_id")
    assert GROUP in primary.get("resolution_note", "")
    assert external.get("decision") == "new" and not external.get("ku_id")
    assert external.get("external_id") == TRECCANI_URL
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())
    assert any(row.get("ku_id") == "units/persons/filippo-farsetti" for row in manifest)
    assert any(row.get("ku_id") == "units/families/farsetti-family" for row in manifest)
    assert not any(
        row.get("type") == "person" and "Tommaso Giuseppe Farsetti" in (row.get("name_en", "") + row.get("canonical_name", ""))
        for row in manifest
    )

    ch8_text = (ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md").read_text(encoding="utf-8-sig")
    ch14_text = (ROOT / "02-sources/02-Markdown/14_CHP-14_intro.md").read_text(encoding="utf-8-sig")
    ch15_text = (ROOT / "02-sources/02-Markdown/15_CHP-15_sec_i.md").read_text(encoding="utf-8-sig")
    assert "T. G. Farsetti referred to the ceiling as follows" in ch8_text and "T. G. Farsetti" in ch14_text
    assert "Tommaso Giuseppe (1720-91)" in ch15_text
    assert "the family history published by his cousin Tommaso Giuseppe in 1778" in ch15_text

    planned_alignment = [dict(row) for row in alignment]
    planned_primary = next(row for row in planned_alignment if row.get("alignment_id") == primary["alignment_id"])
    planned_external = next(row for row in planned_alignment if row.get("alignment_id") == EXTERNAL_ALIGNMENT_ID)
    planned_primary["ku_id"] = KU_ID
    planned_primary["resolution_note"] += (
        f" S4 registration ({DATE}): new identity group {GROUP} is mapped to one person KU {KU_ID}; "
        "the decision remains new and records the already established target."
    )
    planned_external["ku_id"] = KU_ID
    planned_external["resolution_note"] += " S4 registration maps this identity authority row to the same KU."

    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "托马索·朱塞佩·法尔塞蒂",
        "name_en": "Tommaso Giuseppe Farsetti",
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
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text = result_text.replace(
        f"该候选保留 {GROUP} 的独立 new 决定，待 S4 登记。",
        f"该候选保留 {GROUP} 的独立 new 决定，现登记为[托马索·朱塞佩·法尔塞蒂人物卡](../units/persons/tommaso-giuseppe-farsetti.md)。",
        1,
    )
    if "现登记为[托马索·朱塞佩·法尔塞蒂人物卡]" not in result_text:
        raise ValueError("Could not update current S3 Farsetti status in the result.")
    result_insert = (
        f"### S4 person：Tommaso Giuseppe Farsetti 人物组登记（{DATE}）\n\n"
        f"- {CANDIDATE_ID} → {GROUP} → {KU_ID}。新增双语人物卡、manifest及accepted路径；Treccani DBI（Paolo Preto，vol. 45，1995）支持规范名、出生／去世日期与地点，以及文人、藏书家身份。Haskell索引及第8、14、15章提供跨章名称锚点；第8章的Fogolari嵌套转引没有作为独立验证事实。\n"
        "- 9条 S2 关系候选继续待S6；亲属、作品、著述、委托及收藏主张不在本次写入正式关系表。1778年家族史保持独立archive候选 cand-10443，不合并进人物KU。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。字段事实由 `build_field_facts.py` 预检并登记。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Tommaso Giuseppe Farsetti 人物组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- S3组 {GROUP} 仅含 {CANDIDATE_ID}，现映射至 {KU_ID}；当前manifest只含另一个人物 Filippo Farsetti 及Farsetti family，均保持分立。Treccani DBI规范条目为“FARSETTI, Tommaso Giuseppe”，记录1720-04-16生于威尼斯、1791-10-30卒于帕多瓦，并称其为文人和藏书家；该记录此前在S3由 {EXTERNAL_ALIGNMENT_ID} 登记，本轮把外部身份行和候选主行共同映射到该KU。\n"
        "- 新增双语person卡、manifest一条及accepted路径。卡片字段限于姓名、书内称名、出生／去世日期与地点及Treccani明示身份；Haskell第14章短篇拉丁文生平署名、第15章家族史叙述继续作为书内来源主张，关系留待S6。第8章转引经Fogolari，未作为独立核实证据；候选 cand-10443 指向的1778年家族史保持独立archive KU边界。\n"
        "- 9条直接关系候选仍待S6；未写入 `relations.csv`。`build_field_facts.py` 按 evidence → dry-run → apply 同步卡片结构字段和Treccani来源。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条；manifest={len(planned_manifest)}。\n"
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
                current.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)),
                tofile=str(path.relative_to(ROOT)) + " (updated)",
                n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE_ID}->{GROUP}->{KU_ID}; external={EXTERNAL_ALIGNMENT_ID}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
            "9 relation candidates remain for S6"
        )
        return 0

    backups = []
    for path in outputs:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if path.exists():
            shutil.copy2(path, backup)
        else:
            backup.write_text("NEW FILE: created by S4 Tommaso Giuseppe Farsetti registration\n", encoding="utf-8")
        backups.append((path, backup))
    try:
        for path, updated in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(updated, encoding="utf-8-sig", newline="\n")
    except Exception:
        for path, backup in backups:
            if backup.read_text(encoding="utf-8-sig").startswith("NEW FILE:"):
                if path.exists():
                    path.unlink()
            else:
                shutil.copy2(backup, path)
        raise
    print(
        f"applied: {CANDIDATE_ID}->{GROUP}->{KU_ID}; external={EXTERNAL_ALIGNMENT_ID}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
