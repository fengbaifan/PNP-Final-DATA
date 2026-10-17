from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "archive-group-c9f891c0a384"
MEMBERS = ("cand-9857",)
KU_ID = "units/archives/andrea-memmo-notes-status-painters"
CARD_REL = "04-knowledge/units/archives/andrea-memmo-notes-status-painters.md"
NAME_ZH = "安德烈亚·梅莫《画家地位札记》"
NAME_EN = "Andrea Memmo’s Notes on the Status of Painters"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
CH10_SHEET_QUOTE = (
    "Among his papers there survives a sheet on which he briefly scribbled some queries "
    "to himself when preparing his-report."
)
CH10_APPENDIX_QUOTE = "1 Published in. full in Appendix 6."
APPENDIX_SOURCE_QUOTE = (
    "Andrea Memmo’s Notes on the Status of Painters (see Chapter 12, p. 330, note 1)\n"
    "I owe the knowledge of this very interesting document in the Archivio di Stato, Venice—\n"
    "Inquisitoriato alle Arti, Busta 15, fascicolo 6—to my friend Gianfranco Torcellan, to whom I am most grateful. "
    "Memmo was Inquisitore alle Arti from 1772 to 1775, but these notes were probably written two or three years before his assumption of office."
)
APPENDIX_CONTENT_QUOTE = "Leggi la vita del Montorsoli in Vasari—Letta."
RELATION_IDS = (
    "st-chp10-p330-n01-memmo-sheet-appendix",
    "st-chp19-p394-memmo-sheet-source-and-date",
    "st-chp19-p395-memmo-note-marks-life-of-montorsoli-read",
    "st-chp10-p330-memmo-preparatory-sheet",
)
PROCESS_ANCHOR = "s4-memmo-query-sheet-20261017"


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    return [
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页330，正文及注1；Markdown 行260、346。该档案原件未独立查阅。",
            "sentence_summary": (
                "Haskell 称 Andrea Memmo 在准备行会重组报告时把问题记在一张便笺上，"
                "并称便笺全文见本书附录6。"
            ),
            "original_quotes": [
                {"source_span": "line 260; print p. 330", "text": CH10_SHEET_QUOTE},
                {"source_span": "line 346; print p. 330, note 1", "text": CH10_APPENDIX_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "lines 260 and 346; print p. 330 and note 1",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第19章附录6，印刷页394–395；Markdown 行164–166、188。原件及馆藏目录未独立查阅。",
            "sentence_summary": (
                "附录以 Notes on the Status of Painters 为题重录该文件；Haskell 将其定位于"
                "威尼斯国家档案馆 Inquisitoriato alle Arti, Busta 15, fascicolo 6，"
                "并将成文时间估为梅莫于1772年就任前约两至三年。p.395转录一条关于阅读"
                "Vasari 所载 Montorsoli 生平的便笺。"
            ),
            "original_quotes": [
                {"source_span": "lines 164–166; print p. 394", "text": APPENDIX_SOURCE_QUOTE},
                {"source_span": "line 188; print p. 395", "text": APPENDIX_CONTENT_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
                "source_span": "lines 164–166 and 188; print pp. 394–395",
            },
        },
    ]


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "archival record",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch10 = "../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md"
    appendix = "../../../02-sources/02-Markdown/19_CHP-19Appendix.md"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记哈斯克尔第19章附录6以 *Andrea Memmo’s Notes on the Status of Painters* 为题刊出的档案便笺。第10章称梅莫在准备行会重组报告时把若干问题简记于纸上，注1称全文刊于附录6。附录引言将文件定位于 Archivio di Stato, Venice, Inquisitoriato alle Arti, Busta 15, fascicolo 6，并称梅莫于1772至1775年任 Inquisitore alle Arti；“就任前两三年”是哈斯克尔的估计。原件与馆藏目录均未在本轮查阅。

**English:** This card records the archival sheet printed under the Appendix 6 heading *Andrea Memmo’s Notes on the Status of Painters*. Chapter 10 says Memmo briefly wrote queries on a sheet while preparing a report on guild reorganisation, and note 1 says the text is printed in full in Appendix 6. Its introduction locates the document at Archivio di Stato, Venice, Inquisitoriato alle Arti, Busta 15, fascicolo 6, and says Memmo held the Inquisitore alle Arti office from 1772 to 1775; the proposed date two or three years before his appointment is Haskell’s estimate. Neither the manuscript nor a repository catalogue was consulted in this pass.

### 文献属性与范围

- **附录题名：** *Andrea Memmo’s Notes on the Status of Painters*；这是哈斯克尔附录标题，不据此声称为原件题名。中文展示题名为描述性工作译名。
- **文献类型：** 一张档案便笺，依哈斯克尔的叙述与附录转录登记；原件未查阅。
- **内容摘要：** 便笺涉及自由艺术从业者的税费、画家免税问题、其他城市的做法、艺术学院及行会规章等。此处概括依第10章叙述和附录转录，不据此补定其报告最终内容或政策结果。[第10章 p. 330]({ch10})（L260、346）；[第19章附录6 pp. 394–395]({appendix})（L164–166、188）
- **署名与年代：** 哈斯克尔将便笺归于 Andrea Memmo；其成文时间仅按“就任前两三年”的来源估计保留，不换算为确定年份。
- **所述档案定位：** Archivio di Stato, Venice；Inquisitoriato alle Arti；Busta 15；fascicolo 6。该层级与名称仅按哈斯克尔记录保存，本轮不作独立核验。

### 身份边界

S3 身份组 archive-group-c9f891c0a384 仅含 cand-9857，映射至本卡。它指这张画家地位便笺，不与 Andrea Memmo 人物、其著作 *Elementi dell’architettura lodoliana*、1792年 Petizion 488 财物清单、档案机构或 Inquisitori alle Arti 机构合并。附录中提及的 Vasari《Montorsoli传》仍为独立文献候选 cand-9864。

## 关系与证据

当前未登记正式关系。直接 S2 关系候选 st-chp10-p330-n01-memmo-sheet-appendix、st-chp19-p394-memmo-sheet-source-and-date、st-chp19-p395-memmo-note-marks-life-of-montorsoli-read、st-chp10-p330-memmo-preparatory-sheet 均留待 S6 逐条核对端点、方向、语境与证据。该 KU 登记不确认档案原件、转录内容或哈斯克尔的年代估计。
"""


def refresh_process_type_table(text: str, stats: dict) -> str:
    marker = "| 类型 | 候选 | same | new（组/成员） | conflict | excluded | undecided | S4已登记（组/成员） | S4待登记（组/成员） |"
    start = text.index(marker)
    end = text.index("\n\n", start)
    lines = [
        marker,
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    totals = {key: 0 for key in stats[sync.TYPE_ORDER[0]]}
    for kind in sync.TYPE_ORDER:
        item = stats[kind]
        for key in totals:
            totals[key] += item[key]
        lines.append(
            f"| {kind} | {sync.fmt(item['total'])} | {sync.fmt(item['same_candidates'])} "
            f"| {sync.fmt(item['new_groups'])} / {sync.fmt(item['new_candidates'])} "
            f"| {sync.fmt(item['conflict'])} | {sync.fmt(item['excluded'])} "
            f"| {sync.fmt(item['undecided'])} "
            f"| {sync.fmt(item['registered_groups'])} / {sync.fmt(item['registered_members'])} "
            f"| {sync.fmt(item['pending_groups'])} / {sync.fmt(item['pending_members'])} |"
        )
    lines.append(
        f"| **合计** | **{sync.fmt(totals['total'])}** | **{sync.fmt(totals['same_candidates'])}** "
        f"| **{sync.fmt(totals['new_groups'])} / {sync.fmt(totals['new_candidates'])}** "
        f"| **{sync.fmt(totals['conflict'])}** | **{sync.fmt(totals['excluded'])}** "
        f"| **{sync.fmt(totals['undecided'])}** "
        f"| **{sync.fmt(totals['registered_groups'])} / {sync.fmt(totals['registered_members'])}** "
        f"| **{sync.fmt(totals['pending_groups'])} / {sync.fmt(totals['pending_members'])}** |"
    )
    return text[:start] + "\n".join(lines) + text[end:]


def normalized(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Andrea Memmo's query sheet on painters' status in S4")
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
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decision_by_id[cid].get("decision") == "new" and not decision_by_id[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and NAME_EN.casefold() == (row.get("name_en") or "").casefold()
        for row in manifest
    )

    source_checks = (
        ("02-sources/02-Markdown/10_CHP-10_sec_ii.md", CH10_SHEET_QUOTE),
        ("02-sources/02-Markdown/10_CHP-10_sec_ii.md", CH10_APPENDIX_QUOTE),
        ("02-sources/02-Markdown/19_CHP-19Appendix.md", APPENDIX_SOURCE_QUOTE),
        ("02-sources/02-Markdown/19_CHP-19Appendix.md", APPENDIX_CONTENT_QUOTE),
    )
    for relative, quote in source_checks:
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        assert normalized(quote) in normalized(source_text), f"source quote changed: {relative}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [
        row for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert {row["statement_id"] for row in direct} == set(RELATION_IDS)
    assert {row["statement_id"] for row in relations} == set(RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated archive card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = refresh_process_type_table(process_text, stats)
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S4 archive：Andrea Memmo《画家地位札记》文献身份组登记（{DATE}）\n\n"
        f"- cand-9857 保持 S3 new 组 {GROUP}，登记为[{NAME_ZH}](../../../{CARD_REL})（{KU_ID}）。"
        "本卡只记录附录6所题的单张便笺；该标题不被当作原件题名。它与 Memmo 人物、"
        "《Elementi dell’architettura lodoliana》及 Petizion 488 财物清单分别处理。\n"
        "- Haskell 第10章 p.330称该便笺记有准备行会重组报告时提出的问题，注1称全文刊于附录6；"
        "附录 p.394给出威尼斯国家档案馆的定位，并将成文时间列为就任前约两至三年，保留为作者估计。"
        "原件、馆藏目录及所述日期未独立核验。\n"
        f"- 直接 S2 关系候选共{len(relations)}条（{', '.join(RELATION_IDS)}），全部留待 S6；"
        "本批未新增正式关系、外部身份验证或 S5 enrichment。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
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
        f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
