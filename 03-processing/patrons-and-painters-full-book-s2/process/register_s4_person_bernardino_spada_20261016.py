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
CARD_REL = "04-knowledge/units/persons/bernardino-spada.md"
CARD_PATH = ROOT / CARD_REL
KU_ID = "units/persons/bernardino-spada"
CANDIDATE_ID = "cand-2493"
EXTERNAL_ALIGNMENT_ID = "aln-12613"
GROUP = "new-person:bernardino-spada-810d88ac92"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/bernardino-spada_(Dizionario-Biografico)/"
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-bernardino-spada-20261016"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_CITATION = (
    "Benedetta Borello, ‘SPADA, Bernardino,’ *Dizionario Biografico degli Italiani*, "
    "vol. 93 (2018), Treccani. " + TRECCANI_URL + f" Accessed {DATE}."
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
            "location": "第3章 p.75，印刷页；OCR L125–135",
            "sentence_summary": (
                "Haskell在谈Virgilio Spada后提到其兄弟Cardinal Bernardino，并在同段用Bernardino指称1632年购得宫殿者；"
                "此处作为书内身份锚点，关系和购置陈述保留为待S6审查的原书主张。"
            ),
            "original_quotes": [
                {"source_span": "lines 131–132; printed p. 75", "text": "He and his brother Cardinal Bernardino"},
                {"source_span": "line 131; printed p. 75", "text": "which Bernardino acquired from the Mignanelli in 1632"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "source_span": "lines 125–135; printed p. 75",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第5章 p.139；OCR L95–101",
            "sentence_summary": (
                "Haskell再次使用Cardinal Bernardino，并提到其曾任驻巴黎教廷使节；委托措辞明确保留“If it was actually painted”条件，"
                "不在本卡改写为已成立委托。"
            ),
            "original_quotes": [
                {"source_span": "line 96; printed p. 139", "text": "If it was actually painted for Cardinal Bernardino"},
                {"source_span": "line 96; printed p. 139", "text": "who had been papal nunzio in Paris"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
                "source_span": "lines 95–101; printed p. 139",
            },
        },
        {
            "citation": TRECCANI_CITATION,
            "url": TRECCANI_URL,
            "accessed_date": DATE,
            "location": "DBI vol. 93 (2018), ‘SPADA, Bernardino’；生卒、教廷任职与枢机任命条目",
            "sentence_summary": (
                "Borello将规范条目定为Bernardino Spada，记其1594年4月21日出生、1661年11月10日去世；"
                "条目记有1623年任驻巴黎教廷使节、1626年1月获任枢机及博洛尼亚使节任职至1631年。"
            ),
            "original_quotes": [
                {"source_span": "entry lines 21–25", "text": "SPADA, Bernardino; Nacque il 21 aprile 1594"},
                {"source_span": "entry lines 32–36", "text": "fu nominato nunzio a Parigi; ... lo nominò cardinale"},
                {"source_span": "entry line 55", "text": "Bernardino Spada morì il 10 novembre 1661"},
            ],
            "evidence_ref": {
                "source_url": TRECCANI_URL,
                "source_span": "DBI vol. 93 (2018), lines 21–36, 55",
            },
        },
    ]
    frontmatter = {
        "title": "贝尔纳迪诺·斯帕达（Bernardino Spada）",
        "name_en": "Bernardino Spada",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch3 = "[第3章 p.75](../../../02-sources/02-Markdown/03_CHP-3_sec_ii.md)（L125–135）"
    ch5 = "[第5章 p.139](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md)（L95–101）"
    treccani = f"[Treccani《意大利人传记辞典》条目]({TRECCANI_URL})"
    body = f"""## 内容

### 描述

**中文：** 罗马教会枢机与教廷外交官。Treccani记载他生于1594年4月21日，1623年受任驻巴黎教廷使节，1626年1月获任枢机，曾任博洛尼亚使节至1631年，1661年11月10日去世。Haskell第3章的“Cardinal Bernardino”与第5章再次出现的同一称谓，按本书语境及传记身份记录对齐为Bernardino Spada。中文名为项目工作音译。{ch3} {ch5} {treccani}

**English:** A Roman ecclesiastic and papal diplomat. Treccani records his birth on 21 April 1594, appointment as papal nuncio in Paris in 1623, appointment as cardinal in January 1626, service as legate of Bologna through 1631, and death on 10 November 1661. Haskell’s “Cardinal Bernardino” in Chapter 3 and the repeated title in Chapter 5 are aligned to Bernardino Spada on the basis of the book context and the biographical authority record. The Chinese name is a working transliteration. {ch3} {ch5} {treccani}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Bernardino Spada | Treccani DBI；S3 |
| 本书索引形式 | Spada, Cardinal Bernardino | S1，S.csv#182 |
| 本书正文称名 | Cardinal Bernardino | S2，{ch3}；{ch5} |

### 生平与职务

| 字段 | 值 | 证据 |
|---|---|---|
| 出生日期 | 1594年4月21日 | Treccani DBI |
| 去世日期 | 1661年11月10日 | Treccani DBI |
| 驻巴黎教廷使节 | 1623年12月任命 | Treccani DBI |
| 枢机任命 | 1626年1月19日 | Treccani DBI |
| 博洛尼亚使节 | 1627年获任（条目称在领红帽前三日）；任至1631年 | Treccani DBI |

## 关系与证据

### 身份与外部链接

{treccani}（Benedetta Borello，DBI第93卷，2018；身份与生平条目）。

### 关系记录

本卡未新增正式关系。Haskell关于其兄弟、任职、宫殿取得及可能委托等书内陈述仍由原始 statement 承载，待S6逐项审查；条件性委托不改写为确定事实。

### 关系候选入口

[全书关系候选与端点记录](../../../03-processing/{TASK}/process/knowledge.md#s3-personcardinal-bernardino-spada-跨章身份组复核-2026-10-16)
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Bernardino Spada person identity group in S4.")
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
    assert candidate.get("canonical_name") == "Spada, Cardinal Bernardino"
    assert candidate.get("suggested_type") == "person"
    assert primary.get("decision") == "new" and not primary.get("ku_id")
    assert GROUP in primary.get("resolution_note", "")
    assert external.get("decision") == "new" and not external.get("ku_id")
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())
    assert external.get("external_id") == TRECCANI_URL

    ch3_text = (ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md").read_text(encoding="utf-8-sig")
    ch5_text = (ROOT / "02-sources/02-Markdown/05_CHP-5_sec_iii.md").read_text(encoding="utf-8-sig")
    assert "He and his brother Cardinal Bernardino" in ch3_text
    assert "which Bernardino acquired from the Mignanelli in 1632" in ch3_text
    assert "If it was actually painted for Cardinal Bernardino" in ch5_text
    assert "who had been papal nunzio in Paris" in ch5_text

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
        "canonical_name": "贝尔纳迪诺·斯帕达",
        "name_en": "Bernardino Spada",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 3

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_insert = (
        f"### S4 person：Bernardino Spada 人物组登记（{DATE}）\n\n"
        f"- {CANDIDATE_ID} → {GROUP} → {KU_ID}。新增双语人物卡、manifest及accepted路径；Treccani DBI（Benedetta Borello，vol. 93，2018）支持规范名、生卒、枢机任命、驻巴黎教廷使节及博洛尼亚使节任期。Haskell第3、5章提供书内称名和跨章锚点。\n"
        "- 9条 S2 关系候选继续待S6；Haskell关于兄弟、宫殿取得、职务与条件性委托的断言保留原限定，本次不写入 `relations.csv`，不将“如果作品确曾绘制”改成确定委托。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。字段事实由 `build_field_facts.py` 预检并登记。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Bernardino Spada 人物组登记（{DATE}）"
    assert process_heading not in process_text
    process_note = (
        f"\n\n{process_heading}\n\n"
        f"- S3身份组 {GROUP} 仅含 {CANDIDATE_ID}，现映射至 {KU_ID}；既有同姓人物 cand-2494 → units/persons/virgilio-spada 保持独立。Treccani DBI规范条目为“SPADA, Bernardino”，记录1594-04-21至1661-11-10、1623年驻巴黎教廷使节任命、1626-01-19枢机任命，以及1627年获任博洛尼亚使节并任至1631年（条目称其在领红帽前三日获任）。该规范记录此前在S3由 {EXTERNAL_ALIGNMENT_ID} 登记，本轮把外部身份行与候选主行共同映射至同一KU。\n"
        "- 新增person卡、manifest一条、accepted路径及双语描述；字段事实仅登记姓名、书内称名、生卒和可由Treccani直接支持的教廷职务，不把书内关系候选写成正式关系。与Virgilio Spada的兄弟关系、1632年宫殿取得、枢机与Mazarin相关的可能委托等，继续以原statement为证据并留待S6；条件式委托保持未决。\n"
        f"- 9条直接关系候选仍待S6。本次不改变关系表；build_field_facts.py需在卡片登记后按 evidence → dry-run → apply 将卡片字段和Treccani来源加入字段表。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条；manifest={len(planned_manifest)}。\n"
    )
    process_text += process_note

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
            backup.write_text("NEW FILE: created by S4 Bernardino Spada registration\n", encoding="utf-8")
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
