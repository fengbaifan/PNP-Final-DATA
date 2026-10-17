from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge/tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge/results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge/accepted.yml"
DATE = "2026-10-16"

CANDIDATE = "cand-2480"
GROUP = "new-person:dal-gioseffo-giovan-sole-8d002c1de3"
KU_ID = "units/persons/giovan-gioseffo-dal-sole"
CARD_REL = "04-knowledge/units/persons/giovan-gioseffo-dal-sole.md"
CARD = ROOT / CARD_REL
NAME_ZH = "乔万·乔塞福·达·索莱"
NAME_EN = "Giovan Gioseffo dal Sole"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/dal-sole-giovan-gioseffo/"
ICCD_URL = "https://catalogo.cultura.gov.it/Agent/ef70dcf458ce0fe3baa6ccd39cf07ed6"
BACKUP_SUFFIX = ".bak-s4-giovan-gioseffo-dal-sole-20261016"

BOOK_SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
        "location": "第7章 p.201；OCR L49–52",
        "span": "lines 49–52; print p. 201",
        "summary": "第7章将 Dal Sole 列入欧根亲王收藏中的博洛尼亚画家。",
        "quotes": (("line 50", "dal Sole and many other Bolognese painters"),),
    },
    {
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "location": "第8章 p.203；OCR L8–9",
        "span": "lines 8–9; print p. 203",
        "summary": "正文写出 Giovan Gioseffo dal Sole，并将其作品置于博洛尼亚商人 Giovanni Antonio Belloni 的收藏语境。",
        "quotes": (("line 8", "Giovan Gioseffo dal Sole, Felice Torelli, Crespi and Gambarini"),),
    },
    {
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md",
        "location": "第8章 p.214 注；OCR note L1",
        "span": "note line 1; print p. 214",
        "summary": "注释再次写出 Giovan Gioseffo dal Sole，并记载其作品为收藏者持有。",
        "quotes": (("note line 1", "They owned large historical pictures by Giovan Gioseffo dal Sole and Francesco Monti"),),
    },
    {
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章 pp.223、225、227；OCR L142、164、196",
        "span": "lines 142, 164, 196; print pp. 223, 225, 227",
        "summary": "三处正文分别以全名或姓氏提及 Dal Sole，语境涉及委托、绘画创作及 Conti 收藏。",
        "quotes": (
            ("line 142", "Giovan Gioseffo dal Sole"),
            ("line 164", "Giovan Gioseffo dal Sole"),
            ("line 196", "Dal Sole"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章 p.282 及注3；OCR L147、522",
        "span": "lines 147, 522; print p. 282 and note 3",
        "summary": "第10章写作 Gian Gioseffo dal Sole，并记载其为选帝侯 Johann Wilhelm 创作的两件作品。",
        "quotes": (
            ("line 147", "Gian Gioseffo dal Sole"),
            ("note line 522", "Dal Sole a St Teresa wounded by Christ and a Rape of the Sabines"),
        ),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/S.csv",
        "location": "全书索引 S.csv#169",
        "span": "S.csv#169",
        "summary": "索引以 Sole, Giovan Gioseffo dal 列出该人物并给出跨章页码。",
        "quotes": (("S.csv#169", "Sole, Giovan Gioseffo dal"),),
    },
)


def source_row(item: dict) -> dict:
    return {
        "citation": BOOK_CITATION,
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [
            {"source_span": span, "text": quote}
            for span, quote in item["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": item["source_file"],
            "source_span": item["span"],
        },
    }


def make_card() -> str:
    sources = [source_row(item) for item in BOOK_SOURCES]
    sources.extend(
        [
            {
                "citation": f'Treccani, "Dal Sóle, Giovan Gioseffo." {TRECCANI_URL} Accessed {DATE}.',
                "location": "Enciclopedia on line, biografie in arti visive; entry heading and biography",
                "sentence_summary": "Treccani uses the name Giovan Gioseffo dal Sole and identifies him as a painter born in Bologna in 1654 and deceased there in 1719.",
            },
            {
                "citation": f"Catalogo Generale dei Beni Culturali (ICCD), Agent ef70dcf458ce0fe3baa6ccd39cf07ed6. {ICCD_URL} Accessed {DATE}.",
                "location": "Agent authority record; attributed works listed under Dal Sole Giovan Gioseffo",
                "sentence_summary": "The Italian national catalogue records the name form Dal Sole Giovan Gioseffo and dates 1654/1719; individual listed works are explicitly marked attributed and are not treated here as verified attributions.",
            },
        ]
    )
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch7 = "[第7章 p.201](../../../02-sources/02-Markdown/07_CHP-7_sec_v.md)（L49–52）"
    ch8a = "[第8章 p.203](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L8–9）"
    ch8n = "[第8章 p.214 注](../../../02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md)（L1）"
    ch8b = "[第8章 pp.223、225、227](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L142、164、196）"
    ch10 = "[第10章 p.282](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L147、注3 L522）"
    index = "[全书索引 S.csv#169](../../../02-sources/03-Index/03-2-Index-CSV/S.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “Sole, Giovan Gioseffo dal” 列出人物。第7章将 Dal Sole 列入欧根亲王收藏中的博洛尼亚画家；第8章在商人收藏、绘画委托及创作语境中多次以 Giovan Gioseffo dal Sole 或 Dal Sole 称呼他；第10章写作 Gian Gioseffo dal Sole，并提到他为 Johann Wilhelm 创作的作品。Treccani《百科全书》以 Giovan Gioseffo dal Sole 立目，记其为博洛尼亚画家（1654–1719）。中文名为项目工作译名。{ch7} {ch8a} {ch8n} {ch8b} {ch10} {index} [Treccani]({TRECCANI_URL})

**English:** The book’s index lists “Sole, Giovan Gioseffo dal.” Chapter 7 includes Dal Sole among the Bolognese painters represented in Prince Eugene’s collection. Chapter 8 names Giovan Gioseffo dal Sole or Dal Sole in contexts involving merchant collections, commissions, and painting. Chapter 10 uses “Gian Gioseffo dal Sole” and mentions works made for Johann Wilhelm. Treccani’s encyclopedia identifies Giovan Gioseffo dal Sole as a painter from Bologna (1654–1719). The Chinese name is a project working transliteration. {ch7} {ch8a} {ch8n} {ch8b} {ch10} {index} [Treccani]({TRECCANI_URL})

### 名称与书内身份

- **索引与标准姓名：** 索引作 Sole, Giovan Gioseffo dal；Treccani 标目为 Giovan Gioseffo dal Sole。第10章作 Gian Gioseffo dal Sole，另有 Dal Sole 简称；全书章节、赞助人语境及 Treccani 人物条目支持同一画家的书内指称，不据拼写差异另拆人物。{index} {ch8a} {ch8b} {ch10} [Treccani]({TRECCANI_URL})
- **外部目录范围：** ICCD 国家目录以 “Dal Sole Giovan Gioseffo (attribuito)” 标记相关作品，其条目支持姓名形式与年代目录记录；因作品归属明标 attributed，本卡不将这些目录作品作为已确认的 Dal Sole 作品。 [ICCD 国家目录]({ICCD_URL})

## 关系与证据

当前没有登记正式关系。涉及该人物的17条 S2 陈述中15条为关系候选，均留待 S6 逐条核查；第10章所列两件作品另有各自候选身份记录，作者归属和作品指代仍按原文与候选证据分别审查。{ch7} {ch8a} {ch8n} {ch8b} {ch10}
    """


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    assert CARD_REL not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def contains_candidate(value, candidate_id: str) -> bool:
    if isinstance(value, dict):
        return any(contains_candidate(item, candidate_id) for item in value.values())
    if isinstance(value, list):
        return any(contains_candidate(item, candidate_id) for item in value)
    return value == candidate_id


def source_text(item: dict) -> str:
    return " ".join((ROOT / item["source_file"]).read_text(encoding="utf-8-sig").split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Giovan Gioseffo dal Sole identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate = candidate_by_id[CANDIDATE]
    target = next(row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Sole, Giovan Gioseffo dal"
    assert candidate.get("index_entry_id") == "S.csv#169"
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and NAME_EN.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in BOOK_SOURCES:
        normalized = source_text(item)
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized, (item["source_file"], quote)
    _, index_rows = sync.read_csv(ROOT / "02-sources/03-Index/03-2-Index-CSV/S.csv")
    index_row = index_rows[int(candidate["index_entry_id"].split("#")[1])]
    assert index_row.get("Main Entry") == candidate["canonical_name"]

    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    related = [row for row in statements if contains_candidate(row, CANDIDATE)]
    relation_count = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in related)
    assert len(related) == 17, f"unexpected statement count involving candidate: {len(related)}"
    assert relation_count == 15, f"unexpected relation-candidate count involving candidate: {relation_count}"

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = "S3-full-book-2026-10-16"
    planned_target["resolution_note"] = (
        f"source_ref=entity-candidates.csv#{CANDIDATE};index_entry=S.csv#169;"
        "index_pages=200n, 201, 214n, 223, 225, 227, 237n, 282;"
        "s2_mentions=m-chp10-p282-dal_sole,m-chp10-p282notes-dal-sole,m-chp7-p201-p202-042,"
        "m-chp7-p200-p202-notes-005,m-chp7-p200-p202-notes-033,m-chp8-p203-058,m-chp8-p203-065,"
        "m-chp8-p212-214-notes-039,m-chp8-p223-dal-sole,m-chp8-p225-dal-sole,m-chp8-p227-dal-sole;"
        "reviewed_sources=ch7:p201;ch8:p203,p214n,p223,p225,p227;ch10:p282;"
        f"prior_decision=new (2026-10-15);group={GROUP};"
        "S3 review: the index and ch8 give Giovan Gioseffo dal Sole; ch10 gives Gian Gioseffo dal Sole and its note links Dal Sole to works for Johann Wilhelm. "
        "Treccani, Dal Sóle, Giovan Gioseffo, https://www.treccani.it/enciclopedia/dal-sole-giovan-gioseffo/, accessed 2026-10-16, identifies a Bologna painter (1654-1719); "
        "ICCD authority record ef70dcf458ce0fe3baa6ccd39cf07ed6 records Dal Sole Giovan Gioseffo, 1654/1719, with listed works marked attributed. "
        "No same-identity person KU exists in the manifest; the distinct archive author Gioseffo Guidalotti Franchini is not this painter. "
        f"Identity decision remains new; S4 registration mapped {GROUP} to {KU_ID}."
    )

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 277 and totals["registered_members"] == 347, totals
    assert totals["pending_groups"] == 4556 and totals["pending_members"] == 4658, totals
    next_result = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    marker = "。各组来源、身份边界和映射更正见[过程记录]"
    assert next_result.count(marker) == 1
    result_insert = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[乔万·乔塞福·达·索莱人物卡]"
        "(../units/persons/giovan-gioseffo-dal-sole.md)，15条关系候选留待 S6" + marker
    )
    next_result = next_result.replace(marker, result_insert, 1)

    note = (
        f"\n### S4 person：{NAME_EN} 跨章身份组登记（{DATE}）\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 人物身份组只含一个候选。索引 S.csv#169 与第7章 p.201、第8章 pp.203、214注、223、225、227、"
        "第10章 p.282 的正文共同提供跨章身份锚点。第8章和索引作 Giovan Gioseffo dal Sole，第10章作 Gian Gioseffo dal Sole；Treccani《百科全书》"
        "以 Giovan Gioseffo dal Sole 立目并记其为博洛尼亚画家（1654–1719）。ICCD 国家目录记录同一姓名和年代，其具体作品条目标为 attributed，"
        "本卡不把这些作品归属升级为已确认。未发现同身份既有 person KU；Gioseffo Guidalotti Franchini 是不同 archive 作者，不合并。中文名为项目工作译名。\n"
        f"- 涉及该人物的17条 S2 陈述中15条为关系候选，均留待 S6 逐条核查；未建立正式关系，未开展 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"### S4 person：{NAME_EN} 跨章身份组登记（{DATE}）" not in knowledge_text
    next_knowledge = knowledge_text + note
    next_accepted = insert_accepted(accepted)

    output = {
        ACCEPTED: next_accepted,
        KNOWLEDGE: next_knowledge,
        RESULT: next_result,
        CARD: card,
    }
    # Build CSV previews using the same serializer as the project helper.
    from io import StringIO
    import csv

    for path, headers, rows in (
        (ALIGNMENT, alignment_fields, planned_alignment),
        (MANIFEST, manifest_fields, planned_manifest),
    ):
        buffer = StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        output[path] = buffer.getvalue()

    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in output if path != CARD)
    if args.dry_run:
        for path, updated in output.items():
            if path == CARD:
                print(f"--- create {CARD_REL} ({len(updated)} characters)")
                print("\n".join(updated.splitlines()[:18]))
                continue
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE} -> {KU_ID}; group_members=1; source_records={len(BOOK_SOURCES)+2}; "
            f"related_statements={len(related)}; relation_candidates_pending={relation_count}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    backups: list[tuple[Path, Path]] = []
    for path in output:
        if path == CARD:
            continue
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        shutil.copy2(path, backup)
        backups.append((path, backup))
    try:
        for path, updated in output.items():
            path.write_text(updated, encoding="utf-8-sig", newline="\n")
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        if CARD.exists():
            CARD.unlink()
        raise
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; relation_candidates_pending={relation_count}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
