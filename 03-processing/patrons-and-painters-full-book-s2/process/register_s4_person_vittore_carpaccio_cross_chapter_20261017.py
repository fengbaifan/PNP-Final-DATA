from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_archive_memmo_query_sheet_20261017 as process_sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "new-person:carpaccio-vittore-89b0809b12"
MEMBERS = ("cand-0565", "cand-0566")
KU_ID = "units/persons/vittore-carpaccio"
CARD_REL = "04-knowledge/units/persons/vittore-carpaccio.md"
NAME_ZH = "维托雷·卡帕乔"
NAME_EN = "Vittore Carpaccio"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
INDEX_PATH = "02-sources/03-Index/03-2-Index-CSV/C.csv"
CH16_QUOTE = "Carpaccio’s famous scenes of the Life of St Ursula."
CH20_QUOTE = "Carpaccio"
RELATION_STATEMENTS = (
    "st-chp16-p376-toninotto-del-pian-prints-after-carpaccio",
    "st-chp20-p410-della-lena-painter-appreciations",
)
PROCESS_ANCHOR = "s4-person-vittore-carpaccio-20261017"
S3_RATIONALE = (
    " S3 cross-chapter identity rationale (2026-10-17): C.csv#89 is the main index entry at p.410; C.csv#90 is its "
    "p.376 subentry 'Scenes from Life of St Ursula'. Both normalize to the same full-name form 'Carpaccio, Vittore'. "
    "Chapter 16 names Carpaccio's scenes as the source for Giovanni del Pian's prints; the postscript separately "
    "names Carpaccio among the painters admired in Della Lena's treatise. The matching name form and cross-chapter "
    "contexts support one source-local person identity, not a merger with the source-cycle or later print series. "
    "No external identity source was accessed."
)


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def source_rows():
    return [
        {
            "citation": "Francis Haskell, *Patrons and Painters*, index of names.",
            "location": "C.csv#89 (p.410, main entry) and C.csv#90 (p.376, subentry 'Scenes from Life of St Ursula').",
            "sentence_summary": "两条索引记录均使用规范化姓名 Carpaccio, Vittore；p.376 子目将其与《圣乌尔苏拉生平》场景相连。",
            "original_quotes": [
                {"source_span": "C.csv#89; print p. 410", "text": "Carpaccio, Vittore"},
                {"source_span": "C.csv#90; print p. 376", "text": "Carpaccio, Vittore"},
                {"source_span": "C.csv#90; print p. 376", "text": "Scenes from Life of St Ursula"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters-index",
                "source_file": INDEX_PATH,
                "source_span": "entries C.csv#89–90; print pp. 376, 410",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第16章，印刷页376，Markdown 行44。",
            "sentence_summary": "哈斯克尔称 Giovanni del Pian 于1785年出版的九幅大幅版画以 Carpaccio 的《圣乌尔苏拉生平》场景为原型；原作循环与版画组分开。",
            "original_quotes": [
                {"source_span": "line 44; print p. 376", "text": CH16_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "source_span": "line 44; print p. 376",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第20章后记，印刷页410，Markdown 行207；所述 Della Lena 文献未独立查阅。",
            "sentence_summary": "哈斯克尔称 Della Lena 对 Guardi 的热情不妨碍他欣赏 Vivarini、Carpaccio 和 Bellini 的“美丽质朴”。",
            "original_quotes": [
                {"source_span": "line 207; print p. 410", "text": CH20_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "source_span": "line 207; print p. 410",
            },
        },
    ]


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    index = "../../../02-sources/03-Index/03-2-Index-CSV/C.csv"
    ch16 = "../../../02-sources/02-Markdown/16_CHP-16_intro.md"
    ch20 = "../../../02-sources/02-Markdown/20_CHP-20Postscript.md"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔索引所列画家 Vittore Carpaccio（索引规范形式：Carpaccio, Vittore）。第16章称 Giovanni del Pian 于1785年出版的一组版画取材于 Carpaccio 的《圣乌尔苏拉生平》场景；第20章后记又在讨论 Della Lena 的艺术品鉴赏时列出 Carpaccio。身份范围限于本书及索引可支持的这位画家；本轮不补充生卒年、传记或外部权威身份。

**English:** This card records the painter Vittore Carpaccio as named in Haskell’s index under the form “Carpaccio, Vittore.” Chapter 16 says that a 1785 series of prints by Giovanni del Pian was based on Carpaccio’s scenes from the Life of St Ursula; the postscript in Chapter 20 also names Carpaccio in its account of Della Lena’s artistic appreciation. The identity is limited to what the book and its index support; no dates, biography, or external authority identity are added in this pass.

### 名称

- **索引规范形式：** Carpaccio, Vittore；正文展示形式：Vittore Carpaccio。[人物索引 C.csv#89–90](../../../{index})（pp.376, 410）
- **中文展示名：** 维托雷·卡帕乔，为姓名音译；不声称为官方译名。

### 书内提及

- **第16章 p.376：** 哈斯克尔称 Giovanni del Pian 于1785年出版九幅大幅版画，取材于 Carpaccio 的《圣乌尔苏拉生平》场景。[原书](../../../{ch16})（L44）。版画组与被称为 Carpaccio 场景的源作品循环不合并；个别版画题名及出版 imprint 未载。
- **第20章后记 p.410：** 哈斯克尔概述 Della Lena 对 Guardi、Vivarini、Carpaccio、Bellini 等人的艺术欣赏；所引 Della Lena 文献未在本轮独立查阅。[原书](../../../{ch20})（L207）。

## 关系与证据

未登记正式关系。`st-chp16-p376-toninotto-del-pian-prints-after-carpaccio` 与 `st-chp20-p410-della-lena-painter-appreciations` 均为直接 S2 关系候选，留待 S6 核对端点和关系类型；第16章 statement 将本候选列入 `mentioned_candidate_ids`，并未把它设为现有 subject/object。该身份登记不新增正式边，也不把 Della Lena 所引文献中的评价当作已独立核验的原件内容。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Vittore Carpaccio identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decision_by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id for cid in MEMBERS)
    group_members = {
        cid for cid, row in decision_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    expected_index = {
        "cand-0565": ("C.csv#89", "", "410"),
        "cand-0566": ("C.csv#90", "Scenes from Life of St Ursula", "376"),
    }
    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        assert candidate.get("suggested_type") == "person"
        assert decision_by_id[cid].get("decision") == "new" and not decision_by_id[cid].get("ku_id")
        assert (candidate.get("index_entry_id"), candidate.get("sub_entry"), candidate.get("index_page_range")) == expected_index[cid]

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "person" and NAME_EN.casefold() == (row.get("name_en") or "").casefold() for row in manifest)
    index_text = (ROOT / INDEX_PATH).read_text(encoding="utf-8-sig")
    assert '"Carpaccio, Vittore",,,,410' in index_text
    assert '"Carpaccio, Vittore",,Scenes from Life of St Ursula,,376' in index_text
    source_checks = (
        ("02-sources/02-Markdown/16_CHP-16_intro.md", (CH16_QUOTE,)),
        ("02-sources/02-Markdown/20_CHP-20Postscript.md", (CH20_QUOTE,)),
    )
    for relative, quotes in source_checks:
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        for quote in quotes:
            assert normalized(quote) in normalized(source_text), f"source quote changed: {relative}: {quote!r}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = [
        row for row in statements
        if set(MEMBERS).intersection((row.get("qualifiers") or {}).get("mentioned_candidate_ids", []))
    ]
    pending_relations = [
        row for row in related
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert {row["statement_id"] for row in pending_relations} == set(RELATION_STATEMENTS)
    assert not any(row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS for row in related)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        row = planned_by_id[cid]
        if S3_RATIONALE.strip() not in row["resolution_note"]:
            row["resolution_note"] += S3_RATIONALE
        row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
        row["ku_id"] = KU_ID

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated person card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    assert f"<a id=\"{PROCESS_ANCHOR}\"></a>" not in next_process
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S3/S4 person：Vittore Carpaccio 跨章身份组登记（{DATE}）\n\n"
        f"- `{GROUP}` 含 `cand-0565`（C.csv#89，p.410 主项）与 `cand-0566`（C.csv#90，p.376《Scenes from Life of St Ursula》子目）。"
        f"同一规范人名及两章书内上下文支持一位 source-local person，登记为[{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（`{KU_ID}`）。\n"
        "- 第16章 p.376 将 Giovanni del Pian 的1785年版画与 Carpaccio 的圣乌尔苏拉场景相连；第20章后记 p.410 将 Carpaccio 列入 Della Lena 欣赏的画家。"
        "仅记录这两处书内提及，不补生卒年或外部生平；原作循环与版画组保持分开。\n"
        f"- 关系候选 `{RELATION_STATEMENTS[0]}`、`{RELATION_STATEMENTS[1]}` 留待 S6；本批未创建正式关系。\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
            f"mentioned_statements={len(related)}; relation_candidates_pending={len(pending_relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; card_frontmatter=valid"
        )
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
        f"mentioned_statements={len(related)}; relation_candidates_pending={len(pending_relations)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
