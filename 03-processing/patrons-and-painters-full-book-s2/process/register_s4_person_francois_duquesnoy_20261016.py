from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
from io import StringIO
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

CANDIDATE = "cand-0952"
GROUP = "new-person:duquesnoy-francois-3c8db34ada"
KU_ID = "units/persons/francois-duquesnoy"
CARD_REL = "04-knowledge/units/persons/francois-duquesnoy.md"
CARD = ROOT / CARD_REL
NAME_ZH = "弗朗索瓦·迪凯努瓦"
NAME_EN = "François Duquesnoy"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/du-quesnoy-francois-detto-il-fiammingo_(Dizionario-Biografico)/"
NGA_URL = "https://www.nga.gov/artists/2107-francois-duquesnoy"
ULAN_URL = "https://www.getty.edu/vow/ULANFullDisplay?find=&nation=&role=&subjectid=500115495"
ULAN_ID = "500115495"
BACKUP_SUFFIX = ".bak-s4-francois-duquesnoy-20261016"

BOOK_SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
        "location": "第2章 p.36；OCR L53–54",
        "span": "lines 53–54; print p. 36",
        "summary": "正文称 François Duquesnoy 为佛兰德雕塑家，记述他曾在 Bernini 的 Baldacchino 项目工作，并雕刻 St Andrew 像。",
        "quotes": (
            ("lines 53–54", "A Flemish sculptor François Duquesnoy, who had worked under him on the baldacchino, carved a St Andrew"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "location": "第4章 p.104；OCR L56–58",
        "span": "lines 56–58; print p. 104",
        "summary": "正文称 Duquesnoy 的雕塑最合 Cassiano 的趣味，提及其蜡与陶土模型及 S. Maria di Loreto 的 St Susanna。",
        "quotes": (
            ("line 58", "François Duquesnoy"),
            ("lines 56–58", "The sculptor who really appealed to Cassiano’s tastes"),
            ("line 58", "St Susanna in the church of S. Maria di Loreto"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "location": "第7章 p.176 L83–89；p.179 L118–120",
        "span": "lines 83–89, 118–120; print pp. 176, 179",
        "summary": "第7章将 Duquesnoy 纳入法国招募艺术家的叙述，称他最后答应前往巴黎，却在 Livorno 即将启程时去世；p.179 的书信引文以带方括号的重构形式称 Fra[ncesco Fi]a mengo [Duquesnoy]。",
        "quotes": (
            ("line 88", "François Duquesnoy"),
            ("lines 88–89", "At long last Duquesnoy agreed to go to Paris—only to die as he was about to set sail from Livorno."),
            ("line 120", "Fra[ncesco Fi]a mengo [Duquesnoy]"),
        ),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/D.csv",
        "location": "全书索引 D.csv#54；索引所列 p.36、104、176、179",
        "span": "D.csv#54",
        "summary": "索引以 Duquesnoy, François 列出其在第2、4、7章的页码。",
        "quotes": (("D.csv#54", "Duquesnoy, François"),),
    },
)


def source_row(item: dict) -> dict:
    result = {
        "citation": BOOK_CITATION if item["source_file"].startswith("02-sources/02-Markdown/") else "Francis Haskell, *Patrons and Painters*, index",
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
    return result


def make_card() -> str:
    sources = [source_row(item) for item in BOOK_SOURCES]
    sources.extend(
        [
            {
                "citation": f'Gerardo Casale, "DU QUESNOY, François, detto il Fiammingo," *Dizionario Biografico degli Italiani*, vol. 42 (1993). {TRECCANI_URL} Accessed {DATE}.',
                "location": "Entry heading; birth and death paragraphs; sculpture discussion",
                "sentence_summary": (
                    "The DBI entry identifies the sculptor under François Du Quesnoy, born in Brussels in 1597 and deceased in Livorno in 1643; "
                    "it discusses the St Susanna and St Andrew sculptures and his work with Bernini on the Baldacchino."
                ),
            },
            {
                "citation": f"Getty Research Institute, Union List of Artist Names (ULAN), record {ULAN_ID}. {ULAN_URL} Accessed {DATE}.",
                "location": "Person record; preferred name, variant names, role, activity dates and noted works",
                "sentence_summary": (
                    "ULAN identifies Du Quesnoy, François as a Flemish sculptor and draftsman active in Italy, lists name variants including "
                    "François Duquesnoy and Francesco Fiammingo, and names St Andrew, St Susanna, and the Baldacchino. Its profile says ca. 1594–1643; "
                    "the record also shows contributing biography variants of 1594 and 1597."
                ),
            },
            {
                "citation": f"National Gallery of Art, artist record: François Duquesnoy, artist 2107. {NGA_URL} Accessed {DATE}.",
                "location": "Artist heading and biographical date line",
                "sentence_summary": "The NGA uses François Duquesnoy and gives Flemish, 1597–1643, consistent with the Treccani birth year and the book's sculptor identity.",
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
    ch2 = "[第2章 p.36](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L53–54）"
    ch4 = "[第4章 p.104](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L56–58）"
    ch7 = "[第7章 pp.176、179](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L83–89、118–120）"
    index = "[全书索引 D.csv#54](../../../02-sources/03-Index/03-2-Index-CSV/D.csv)"
    treccani = f"[Treccani DBI](<{TRECCANI_URL}>)"
    nga = f"[National Gallery of Art]({NGA_URL})"
    ulan = f"[Getty ULAN {ULAN_ID}](<{ULAN_URL}>)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引将 François Duquesnoy 的第2、4、7章页码归在同一人物项下。第2章称他为佛兰德雕塑家，记其参与 Bernini 的 Baldacchino 项目并雕刻 St Andrew；第4章称其雕塑最合 Cassiano 的趣味，提到蜡与陶土模型及 St Susanna；第7章则叙述他答应前往巴黎、却在 Livorno 启程前去世。Treccani DBI、Getty ULAN 与美国国家美术馆记录的姓名、雕塑身份和作品语境吻合。Treccani DBI 与 NGA 给1597年生，Getty ULAN 总述为约1594年，ULAN 来源项还列1597年；这一出生年异文予以保留，不据此拆分身份。中文名为项目工作音译。{ch2} {ch4} {ch7} {index} {treccani} {ulan} {nga}

**English:** The book’s index groups François Duquesnoy’s references on pages 36, 104, 176, and 179 under one person entry. Chapter 2 calls him a Flemish sculptor who worked on Bernini’s Baldacchino and carved the St Andrew; Chapter 4 says his sculpture particularly appealed to Cassiano’s taste and mentions his wax and terracotta models and St Susanna; Chapter 7 recounts that he agreed to go to Paris but died at Livorno before setting sail. Treccani’s DBI, Getty ULAN, and the National Gallery of Art records match the name, sculptor identity, and work context. Treccani and NGA give 1597 as the birth year, while Getty ULAN’s summary gives circa 1594 and its source entries also include 1597; this birth-year variation is preserved and does not split the identity. The Chinese name is a project working transliteration. {ch2} {ch4} {ch7} {index} {treccani} {ulan} {nga}

### 名称与身份比对

- **规范展示名：** François Duquesnoy，依原书第2、4、7章正文和索引。{ch2} {ch4} {ch7} {index}
- **姓名异形：** François Du Quesnoy、Du Quesnoy, François、Francesco Fiammingo；后者在第7章 p.179 引文中带方括号重构，Getty ULAN 与 Treccani 另列 Il Fiammingo 等名称形式。{ch7} {treccani} {ulan}
- **身份：** 佛兰德雕塑家；书内 St Andrew、St Susanna 和 Bernini Baldacchino 语境与 Treccani DBI、Getty ULAN 所列作品和活动吻合。{ch2} {ch4} {treccani} {ulan}
- **出生地与年份：** Brussels；Treccani DBI 与 NGA 记1597年，Getty ULAN 总述记约1594年，其条目所汇来源也出现1597年；出生年暂保留异文。{treccani} {ulan} {nga}
- **去世时间与地点：** 1643年7月19日，Livorno。{treccani}

### 本书语境

第2、4、7章的全名、连续雕塑家语境、作品锚点及法国招募叙述支持同一身份组。第7章 p.179 的 Fiammingo 拼写保留来源中的方括号重构，不作为独立人物或确定原文异名。{ch2} {ch4} {ch7}

## 关系与证据

### 身份与外部链接

- **Treccani DBI：** {treccani}；支持姓名、雕塑身份、出生与去世信息，以及 St Andrew、St Susanna 与 Baldacchino 语境。
- **Getty ULAN：** {ulan}；记录号 {ULAN_ID}，用于核对身份、姓名异形、角色、活动和作品语境；其出生年总述与记录中的来源日期存在异文。
- **National Gallery of Art：** {nga}；用于核对规范姓名、Flemish 身份及1597–1643年日期范围。

### 关系记录

当前没有登记正式关系。涉及 cand-0952 的14条 S2 关系候选留待 S6 逐条审查；正文中的作品作者、模型收藏、赞助趣味和法国招募陈述仍各按对应端点及证据裁决。本卡未开展 S5 补足。
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


def normalize(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the François Duquesnoy cross-chapter S3 group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate = candidate_by_id[CANDIDATE]
    target = next(
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Duquesnoy, François"
    assert candidate.get("index_entry_id") == "D.csv#54"
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    aliases = {NAME_EN.casefold(), "françois du quesnoy", "du quesnoy, françois", "francesco fiammingo"}
    assert not any(
        row.get("type") == "person"
        and (row.get("canonical_name", "").casefold() in aliases or row.get("name_en", "").casefold() in aliases)
        for row in manifest
    ), "same-identity person KU already exists in manifest"
    assert not any(
        row.get("candidate_id") == CANDIDATE and row.get("external_source")
        for row in alignments
    ), "external identity record already exists for candidate"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in BOOK_SOURCES:
        normalized_source = normalize((ROOT / item["source_file"]).read_text(encoding="utf-8-sig"))
        for _, quote in item["quotes"]:
            assert normalize(quote) in normalized_source, (item["source_file"], quote)
    _, index_rows = sync.read_csv(ROOT / "02-sources/03-Index/03-2-Index-CSV/D.csv")
    index_row = index_rows[int(candidate["index_entry_id"].split("#")[1])]
    assert index_row.get("Main Entry") == candidate["canonical_name"]

    statements = [
        json.loads(line)
        for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = [row for row in statements if contains_candidate(row, CANDIDATE)]
    relation_count = sum(
        row.get("qualifiers", {}).get("relation_candidate") is True
        for row in related
    )
    assert relation_count == 14, f"unexpected relation-candidate count: {relation_count}"

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    previous_note = planned_target.get("resolution_note", "")
    prior_status = "No external identity source was accessed; KU assignment remains for S4."
    assert prior_status in previous_note
    previous_note = previous_note.replace(
        prior_status,
        "Prior S3 record (2026-10-15): no external identity source was accessed at that time; "
        "the KU assignment then remained pending for S4.",
        1,
    )
    external_note = (
        "S3 identity review (2026-10-16): Treccani DBI, Gerardo Casale, DU QUESNOY, François, "
        f"vol. 42 (1993), {TRECCANI_URL}, identifies the Brussels-born sculptor (1597) and records "
        "his death at Livorno on 1643-07-19; it discusses the St Susanna, St Andrew, and Baldacchino. "
        f"Getty ULAN {ULAN_ID} ({ULAN_URL}) identifies Du Quesnoy, François, Flemish sculptor/draftsman, "
        "lists François Duquesnoy and Francesco Fiammingo among variants, and names St Andrew, St Susanna, "
        "and Baldacchino; its summary says ca. 1594–1643 while source entries include 1597. "
        f"NGA ({NGA_URL}) gives Flemish, 1597–1643. Birth-year variation is retained and does not split "
        "the identity. These records support identity only, not every Haskell relationship or work claim. "
        "No same-identity person KU was found in the current manifest."
    )
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = "S3-full-book-2026-10-16"
    planned_target["resolution_note"] = (
        previous_note + "; " + external_note
        + f" S4 registration: mapped {GROUP} to {KU_ID}."
    )

    used_alignment_ids = {
        int(match.group(1))
        for row in planned_alignment
        if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))
    }
    next_id = max(used_alignment_ids, default=0) + 1
    authority_rows = [
        {
            "alignment_id": f"aln-{next_id:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Treccani DBI",
            "external_id": TRECCANI_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity comparison only: the DBI entry identifies François Du Quesnoy, born in Brussels "
                "in 1597 and deceased in Livorno in 1643; it discusses St Susanna, St Andrew, and the Baldacchino."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 1:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Getty ULAN",
            "external_id": ULAN_ID,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity comparison only: ULAN 500115495 identifies Du Quesnoy, François, lists François Duquesnoy "
                "and Francesco Fiammingo variants, and records sculptor/draftsman, St Andrew, St Susanna, and the "
                "Baldacchino. Birth-year summary ca. 1594; source variants include 1597."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 2:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "National Gallery of Art",
            "external_id": NGA_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity comparison only: the NGA uses François Duquesnoy and gives Flemish, 1597–1643."
            ),
        },
    ]
    planned_alignment.extend(authority_rows)

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
    assert totals["registered_groups"] == 279 and totals["registered_members"] == 349, totals
    assert totals["pending_groups"] == 4554 and totals["pending_members"] == 4656, totals
    external_count = sum(bool(row.get("external_source")) for row in planned_alignment)
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(planned_manifest),
    )
    next_result, count_updates = re.subn(
        r"\d+(?=条外部身份记录单独保留)",
        str(external_count),
        next_result,
        count=1,
    )
    assert count_updates == 1, "could not refresh external identity record count"
    marker = "。各组来源、身份边界和映射更正见[过程记录]"
    assert next_result.count(marker) == 1
    result_insert = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[弗朗索瓦·迪凯努瓦人物卡]"
        "(../units/persons/francois-duquesnoy.md)，14条关系候选留待 S6" + marker
    )
    next_result = next_result.replace(marker, result_insert, 1)

    note = (
        f"\n### S4 person：{NAME_EN} 跨章身份组登记（{DATE}）\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 人物组只有一个候选。索引 D.csv#54 列第2章 p.36、第4章 p.104、第7章 pp.176、179；"
        "正文分别以全名及姓氏指称雕塑家，连续提及 Bernini Baldacchino、St Andrew、Cassiano 收藏的蜡/陶土模型、St Susanna 及法国招募叙述。"
        f"Treccani DBI（Gerardo Casale, vol. 42, 1993; {TRECCANI_URL}）以 Du Quesnoy, François 立目，记 Brussels 出生及1643年7月19日 Livorno 去世，"
        "并讨论 St Susanna、St Andrew 与 Baldacchino。Getty ULAN（500115495）记录 Du Quesnoy, François、François Duquesnoy 与 Francesco Fiammingo 等异形，"
        "并列上述作品；其总述生日约1594年，来源项另有1597年。NGA 以 François Duquesnoy 记 Flemish、1597–1643。出生年份异文保留，不据此拆分身份；"
        "这些外部记录仅用于身份比对，不证明全部书内关系或作品陈述。未发现同身份既有 person KU；中文名为项目工作音译。\n"
        "- 涉及该人物的14条 S2 关系候选留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"### S4 person：{NAME_EN} 跨章身份组登记（{DATE}）" not in knowledge_text
    next_knowledge = knowledge_text + note
    next_accepted = insert_accepted(accepted)

    output = {
        ALIGNMENT: None,
        MANIFEST: None,
        ACCEPTED: next_accepted,
        KNOWLEDGE: next_knowledge,
        RESULT: next_result,
        CARD: card,
    }
    for path, headers, rows in (
        (ALIGNMENT, alignment_fields, planned_alignment),
        (MANIFEST, manifest_fields, planned_manifest),
    ):
        buffer = StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        output[path] = buffer.getvalue()

    protected_paths = [path for path in output if path != CARD]
    assert all(
        not path.with_name(path.name + BACKUP_SUFFIX).exists()
        for path in protected_paths
    )
    if args.dry_run:
        for path, updated in output.items():
            if path == CARD:
                print(f"--- create {CARD_REL} ({len(updated)} characters)")
                print("\n".join(updated.splitlines()[:22]))
                continue
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)),
                tofile=str(path.relative_to(ROOT)) + " (updated)",
                n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE} -> {KU_ID}; group_members=1; "
            f"book_and_authority_sources={len(BOOK_SOURCES) + 3}; related_statements={len(related)}; "
            f"relation_candidates_pending={relation_count}; external_records={external_count}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    backups: list[tuple[Path, Path]] = []
    for path in protected_paths:
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
        f"external_records={external_count}; registered={totals['registered_groups']}/"
        f"{totals['registered_members']}; pending={totals['pending_groups']}/"
        f"{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())