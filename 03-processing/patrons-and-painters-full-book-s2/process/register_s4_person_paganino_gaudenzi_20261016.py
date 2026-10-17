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

CANDIDATE = "cand-1116"
GROUP = "new-person:gaudenzi-paganino-bab47b4e3f"
KU_ID = "units/persons/paganino-gaudenzi"
CARD_REL = "04-knowledge/units/persons/paganino-gaudenzi.md"
CARD = ROOT / CARD_REL
NAME_ZH = "帕加尼诺·高登齐"
NAME_EN = "Paganino Gaudenzi"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/paganino-gaudenzi_(Dizionario-Biografico)/"
HLS_URL = "https://hls-dhs-dss.ch/it/articles/015853/2007-09-05/"
BACKUP_SUFFIX = ".bak-s4-paganino-gaudenzi-20261016"
CARD_FIX_SUFFIX = ".bak-s4-paganino-card-body-20261016"

BOOK_SOURCE = {
    "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    "location": "第4章 p.109 正文 OCR L122；p.117 注2 OCR L270",
    "span": "lines 122, 270; print pp. 109, 117 (note 2)",
    "summary": (
        "p.109 称 Paganino Gaudenzi 为学者，并记述 Cassiano 于1647年请他寄来肖像；"
        "p.117 注2将 Cassiano 与 Gaudenzi 的往来书信定位为1641至1647年。"
    ),
    "quotes": (
        ("line 122", "pressing the scholar Paganino Gaudenzi to send him his likeness"),
        ("line 270, note 2", "Letters from Cassiano to Gaudenzi between 1641 and 1647"),
    ),
}
INDEX_REL = "02-sources/03-Index/03-2-Index-CSV/G.csv"


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
    sources = [
        source_row(BOOK_SOURCE),
        {
            "citation": f'Giampiero Brunelli, "GAUDENZI, Paganino," *Dizionario Biografico degli Italiani*, vol. 52 (1999). {TRECCANI_URL} Accessed {DATE}.',
            "location": "Entry heading and biographical paragraphs on birth, death, scholarship, and correspondence with Cassiano dal Pozzo",
            "sentence_summary": (
                "The entry identifies Paganino Gaudenzi, born at Poschiavo in 1595 and deceased at Pisa in 1649; "
                "it also places his correspondence with Cassiano dal Pozzo around 1639–1640."
            ),
        },
        {
            "citation": f'Francesca Negroni, "Gaudenzi, Paganino," *Historisches Lexikon der Schweiz / Dizionario storico della Svizzera*. {HLS_URL} Accessed {DATE}.',
            "location": "Entry heading and biographical paragraphs",
            "sentence_summary": (
                "The entry gives the same name, birth and death dates and places, and records his teaching at La Sapienza and in Pisa."
            ),
        },
    ]
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
    book = "[第4章 p.109](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L122）"
    note = "[第4章 p.117 注2](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L270）"
    treccani = f"[Treccani DBI](<{TRECCANI_URL}>)"
    hls = f"[瑞士历史词典](<{HLS_URL}>)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 哈斯克尔在第4章称 Paganino Gaudenzi 为学者，记述 Cassiano dal Pozzo 于1647年请他寄来肖像，数周后又收到肖像副本。第4章注2将二人的往来书信定位为1641至1647年。Treccani《意大利人传记辞典》和《瑞士历史词典》所列姓名、年代及出生和去世地点与该人物锚点相符。此卡登记人物身份；书内肖像、书信和其他关系候选仍待 S6 审查。中文名为项目工作音译。{book} {note} {treccani} {hls}

**English:** In Chapter 4, Haskell identifies Paganino Gaudenzi as a scholar, recounts Cassiano dal Pozzo’s 1647 request for his likeness, and describes the later receipt of a portrait copy. Note 2 locates their correspondence between 1641 and 1647. The name, dates, and birth and death places in Treccani’s *Dizionario Biografico degli Italiani* and the *Historical Dictionary of Switzerland* match this person anchor. This card registers identity; portrait, correspondence, and other relation candidates from the book remain for S6 review. The Chinese name is a project working transliteration. {book} {note} {treccani} {hls}

### 名称与身份比对

- **全名：** Paganino Gaudenzi；原书第4章 p.109、Treccani 与瑞士历史词典使用相同姓名。{book} {treccani} {hls}
- **出生日期与地点：** 1595年6月3日，Poschiavo。{treccani} {hls}
- **去世日期与地点：** 1649年1月3日，Pisa。{treccani} {hls}
- **身份：** 原书称其为学者；瑞士历史词典另记其在 La Sapienza 与 Pisa 任教。{book} {hls}

### 本书语境

书内全名见第4章 p.109；该段将其置于 Cassiano dal Pozzo 肖像收藏和通信叙述中。外部人物辞典仅用于确认身份，不代替对哈斯克尔所述具体事件的核查。{book} {note}

## 关系与证据

### 身份与外部链接

- **Treccani《意大利人传记辞典》：** {treccani}；用于核对姓名、年代、出生与去世地点及人物身份。
- **瑞士历史词典：** {hls}；用于核对姓名、年代、地点及学术任教信息。

### 关系记录

当前没有登记正式关系。涉及 cand-1116 的14条 S2 关系候选留待 S6 逐条审查；本卡不将索引或同段共现自动转为正式边。未开展 S5 补足。
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


def refresh_card(dry_run: bool) -> int:
    assert CARD.exists()
    current_card = CARD.read_text(encoding="utf-8-sig")
    updated_card = make_card()
    assert current_card != updated_card, "card already matches the corrected body structure"

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    needle = (
        "- 涉及该人物的14条 S2 关系候选留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。"
        + chr(10) + chr(10)
    )
    assert knowledge_text.count(needle) == 1
    correction = (
        "- 登记后表审计发现，身份属性与外部链接的 Markdown 表格尚无对应 enrichment 行；"
        "已改为带证据的条目列表，不新增 S5 字段或 enrichment。"
    )
    updated_knowledge = knowledge_text.replace(needle, needle[:-1] + correction + chr(10) + chr(10), 1)

    output = {CARD: updated_card, KNOWLEDGE: updated_knowledge}
    assert all(not path.with_name(path.name + CARD_FIX_SUFFIX).exists() for path in output)
    if dry_run:
        for path, updated in output.items():
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)),
                tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print("card-only dry-run passed: markdown tables replaced with evidence bullets; no enrichment added")
        return 0

    backups: list[tuple[Path, Path]] = []
    for path in output:
        backup = path.with_name(path.name + CARD_FIX_SUFFIX)
        shutil.copy2(path, backup)
        backups.append((path, backup))
    try:
        for path, updated in output.items():
            path.write_text(updated, encoding="utf-8-sig", newline="")
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        raise
    print("card-only update applied; no enrichment or formal relationship was added")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Paganino Gaudenzi S4 person identity group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--card-only", action="store_true", help="refresh only the existing card body and record the correction")
    args = parser.parse_args()
    if args.card_only:
        return refresh_card(args.dry_run)

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
    assert candidate.get("canonical_name") == "Gaudenzi, Paganino"
    assert candidate.get("index_entry_id") == "G.csv#23"
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
    assert not any(
        row.get("type") == "person"
        and NAME_EN.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    ), "same-identity person KU already exists in manifest"
    assert not any(
        row.get("candidate_id") == CANDIDATE and row.get("external_source")
        for row in alignments
    ), "external identity record already exists for candidate"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    source_text = (ROOT / BOOK_SOURCE["source_file"]).read_text(encoding="utf-8-sig")
    normalized_source = normalize(source_text)
    for _, quote in BOOK_SOURCE["quotes"]:
        assert normalize(quote) in normalized_source, quote
    _, index_rows = sync.read_csv(ROOT / INDEX_REL)
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
        "S3 identity review (2026-10-16): Treccani DBI, Giampiero Brunelli, "
        f"GAUDENZI, Paganino, vol. 52 (1999), {TRECCANI_URL}, and the Swiss Historical Dictionary, "
        f"Francesca Negroni, {HLS_URL}, identify the same Paganino Gaudenzi; both give 1595–1649, "
        "with Poschiavo and Pisa as birth/death places. Treccani also places correspondence with "
        "Cassiano dal Pozzo around 1639–1640. These records support identity only, not Haskell's "
        "specific portrait, correspondence, or relationship claims. No same-identity person KU "
        "was found in the current manifest. Chinese name is a project working transliteration."
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
                "Identity comparison only: the entry names Paganino Gaudenzi and records birth at "
                "Poschiavo in 1595, death at Pisa in 1649, and correspondence with Cassiano dal Pozzo."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 1:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Dizionario storico della Svizzera (HLS)",
            "external_id": HLS_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity comparison only: the entry records Paganino Gaudenzi, 1595–1649, born at "
                "Poschiavo and deceased at Pisa."
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
    assert totals["registered_groups"] == 278 and totals["registered_members"] == 348, totals
    assert totals["pending_groups"] == 4555 and totals["pending_members"] == 4657, totals
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
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[帕加尼诺·高登齐人物卡]"
        "(../units/persons/paganino-gaudenzi.md)，14条关系候选留待 S6" + marker
    )
    next_result = next_result.replace(marker, result_insert, 1)

    note = (
        f"\n### S4 person：{NAME_EN} 身份组登记（{DATE}）\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；S3 身份组只有一个候选，对应全书索引 G.csv#23 与第4章 p.109。"
        "原书以全名称其为学者，叙述 Cassiano dal Pozzo 于1647年请他寄来肖像；p.117 注2列出1641至1647年二人往来书信。"
        f"Treccani DBI（Giampiero Brunelli, vol. 52, 1999; {TRECCANI_URL}）与瑞士历史词典"
        f"（Francesca Negroni; {HLS_URL}）均以 Paganino Gaudenzi 立目并给出1595–1649年、Poschiavo 出生及 Pisa 去世；"
        "Treccani 另记其与 Cassiano dal Pozzo 约1639至1640年有通信。两辞典用于身份比对，不证明哈斯克尔所述具体肖像、通信或关系事实。"
        "未在当前 manifest 中发现同身份人物 KU；中文名为项目工作音译。\n"
        "- 涉及该人物的14条 S2 关系候选留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"### S4 person：{NAME_EN} 身份组登记（{DATE}）" not in knowledge_text
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
                print("\n".join(updated.splitlines()[:20]))
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
            f"book_and_authority_sources=3; related_statements={len(related)}; "
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
