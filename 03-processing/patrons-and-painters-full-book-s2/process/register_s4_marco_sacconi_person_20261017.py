from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CANDIDATE = "cand-2325"
GROUP = "new-person:marco-sacconi-334444e5e2"
KU_ID = "units/persons/marco-sacconi"
CARD_REL = "04-knowledge/units/persons/marco-sacconi.md"
NAME_ZH = "马尔科·萨科尼"
NAME_EN = "Marco Sacconi"
SOURCE_FILE = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"

SOURCES = [
    {
        "location": "第8章；印刷页233；OCR L275–277",
        "span": "lines 275–277; print p. 233",
        "summary": "正文以 Sacconi 指称 Ferdinand de’ Medici 的 protégée，记述将其送往 Venice、经济支持、安排在 Niccolò Cassana 手下工作，以及作品委托、警告和 Corpus Domini 展示。书后索引将该人物列为 Sacconi, Marco。",
        "quotes": [
            ("line 275", "Nor does Ferdinand’s particular protege Sacconi appear to have lived up to his hopes, though he too was sent to Venice."),
            ("lines 276–277", "The Grand Prince took the deepest interest in his career. He provided for him financially when his father died and kept him working under Niccolo Cassana."),
            ("lines 276–277", "for a St Sebastian ‘as he must learn to paint full length figures’"),
            ("line 277", "Cassana’s guidance, but warns him to be ‘meno flemmatico’. He arranges for his pictures to be exhibited on Corpus Domini"),
        ],
    },
    {
        "location": "第8章；印刷页240；OCR L357",
        "span": "line 357; print p. 240",
        "summary": "Haskell 称 Ferdinand de’ Medici 对 Sacconi 采取了同一展示政策；该句承接此前的展览叙述，未指明具体画作或场地。",
        "quotes": [("line 357", "He adopted the same policy towards Sacconi")],
    },
]

RELATION_IDS = {
    "st-chp8-p233-sacconi-patronage",
    "st-chp8-p233-sacconi-deep-interest",
    "st-chp8-p233-sacconi-under-cassana",
    "st-chp8-p233-sacconi-sent-to-venice",
    "st-chp8-p233-sacconi-full-length-figure-instruction",
    "st-chp8-p233-sacconi-warning",
    "st-chp8-p233-sacconi-corpus-domini-exhibition",
    "st-chp8-p240-ferdinand-displayed-policy-to-sacconi",
}
NON_RELATION_IDS = {
    "st-chp8-p233-sacconi-colour-and-exhibition",
    "st-chp8-p233-sacconi-outcome",
    "st-chp8-p233-sacconi-picture-humour",
}

BODY = """### 描述

**中文：** 本卡对应第8章 p.233、p.240 的 Sacconi，以及书后索引“Sacconi, Marco”。Haskell 称其为 Grand Prince Ferdinand de’ Medici 特别扶助的画家，记述其被送往 Venice、父亲去世后获经济支持、在 Niccolò Cassana 手下工作，以及若干绘画委托、批评和 Corpus Domini 展示安排。正文没有在这些段落写出 Marco 全名，身份以索引全名和同一条目页码定位；相关评价及书信内容仍是 Haskell 的转述。中文显示名为项目工作音译。[第8章 p.233](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L275–277）；[第8章 p.240](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L357）；[书后索引 S.csv#13](../../../02-sources/02-Markdown/22_CHP-22Index.md)（L2881）

**English:** This card represents Sacconi as named on pp.233 and 240 of Chapter 8 and indexed as “Sacconi, Marco.” Haskell describes him as a painter specially supported by Grand Prince Ferdinand de’ Medici, and recounts his being sent to Venice, receiving financial support after his father’s death, working under Niccolò Cassana, and receiving painting orders, criticism, and Corpus Domini exhibition arrangements. The prose passages do not give Marco’s full name; the indexed name and page references provide the book-local identification. The appraisals and correspondence remain Haskell’s reports. The Chinese display name is a project working transliteration. [Chapter 8, p.233](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md) (L275–277); [Chapter 8, p.240](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md) (L357); [Index S.csv#13](../../../02-sources/02-Markdown/22_CHP-22Index.md) (L2881)

### 名称与身份边界

- 对应 S3 候选 `cand-2325`（S.csv#13，索引页码233、240），保持独立人物组 `new-person:marco-sacconi-334444e5e2`。正文仅写姓氏 Sacconi；索引提供 Marco 全名形式，作为本书内定位锚点。
- 既有 S3 组以索引全名及 p.233、p.240 的同一人物语境聚合；不据仅有姓氏的正文提及扩展至其他 Sacconi。
- “送往 Venice”是被动句，原文没有指出执行者；父亲未具名。本卡不补入相关人物或书外履历。

### 关系与证据

以下8条 S2 关系候选留待 S6；本卡未新增正式关系：

- `st-chp8-p233-sacconi-patronage`
- `st-chp8-p233-sacconi-deep-interest`
- `st-chp8-p233-sacconi-under-cassana`（Cassana 已有 person KU）
- `st-chp8-p233-sacconi-sent-to-venice`（Venice 已有 place KU；执行者未明）
- `st-chp8-p233-sacconi-full-length-figure-instruction`
- `st-chp8-p233-sacconi-warning`
- `st-chp8-p233-sacconi-corpus-domini-exhibition`
- `st-chp8-p240-ferdinand-displayed-policy-to-sacconi`

`st-chp8-p233-sacconi-colour-and-exhibition`、`st-chp8-p233-sacconi-outcome`、`st-chp8-p233-sacconi-picture-humour` 是 Haskell 或所引 Ferdinand 的评价性非关系陈述，维持原分类。
"""


def make_card() -> str:
    source_rows = []
    for source in SOURCES:
        source_rows.append({
            "citation": BOOK,
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote} for span, quote in source["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": source["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{fm}---\n\n## 内容\n\n{BODY}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Marco Sacconi's source-local person group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    decisions = {
        r["candidate_id"]: r for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "person"
    row = decisions[CANDIDATE]
    assert row["decision"] == "new" and not row.get("ku_id")
    assert sync.get_group(row.get("resolution_note", "")) == GROUP
    group_members = [
        r for r in alignments
        if r.get("candidate_id") and not r.get("external_source") and r["decision"] == "new"
        and sync.get_group(r.get("resolution_note", "")) == GROUP
    ]
    assert [r["candidate_id"] for r in group_members] == [CANDIDATE]
    assert not (ROOT / CARD_REL).exists() and CARD_REL not in accepted
    assert not any(r.get("ku_id") == KU_ID or r.get("card_path") == CARD_REL for r in manifest)
    assert not any(
        r.get("type") == "person"
        and (r.get("name_en", "").casefold() == NAME_EN.casefold()
             or r.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for r in manifest
    )
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    index_text = " ".join((ROOT / "02-sources/02-Markdown/22_CHP-22Index.md").read_text(encoding="utf-8-sig").split())
    for source in SOURCES:
        for _, quote in source["quotes"]:
            assert " ".join(quote.split()) in source_text, quote
    assert "Sacconi, Marco, 233, 240" in index_text

    statements = sync.load_statements()
    direct = [
        s for s in statements
        if CANDIDATE in (s.get("subject_candidate_id"), s.get("object_candidate_id"))
    ]
    assert {s["statement_id"] for s in direct} == RELATION_IDS | NON_RELATION_IDS
    assert {
        s["statement_id"] for s in direct
        if s.get("qualifiers", {}).get("relation_candidate") is True
    } == RELATION_IDS
    assert decisions["cand-1609"]["ku_id"] == "units/persons/ferdinand-grand-prince-tuscany"
    assert decisions["cand-0593"]["ku_id"] == "units/persons/niccolo-cassana"
    assert decisions["cand-3401"]["ku_id"] == "units/places/venice"

    planned_alignment = [dict(r) for r in alignments]
    target = next(r for r in planned_alignment if r.get("candidate_id") == CANDIDATE and not r.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID, "type": "person", "canonical_name": NAME_ZH,
        "name_en": NAME_EN, "source_task": TASK, "card_path": CARD_REL,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 349 and totals["registered_members"] == 453
    assert totals["pending_groups"] == 4489 and totals["pending_members"] == 4565
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    audit_old = "4,581条待登记 `decision=new` alignment 行，含4,566条候选决定映射（4,490组）和15条外部身份记录。"
    audit_new = "4,580条待登记 `decision=new` alignment 行，含4,565条候选决定映射（4,489组）和15条外部身份记录。"
    assert audit_old in result_text
    result_text = result_text.replace(audit_old, audit_new, 1)
    process_note = (
        "\n\n### S4 person：Marco Sacconi 跨页人物组登记（2026-10-17）\n\n"
        "`cand-2325`（S.csv#13，页码233、240）保持 S3 source-local 人物组 `new-person:marco-sacconi-334444e5e2`，"
        "登记为[Marco Sacconi 人物卡](../../../04-knowledge/units/persons/marco-sacconi.md)。正文两页仅以 Sacconi 指称，索引给出 Marco 全名；未用外部身份扩展书内资料。"
        "8条直接 relation_candidate 留待 S6，3条颜色、成效和幽默评价保持非关系陈述。Ferdinand de’ Medici、Niccolò Cassana 与 Venice 均复用已有 KU；本轮未写 relations.csv。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_note = (
        "\n\n### S4 person：Marco Sacconi（2026-10-17）\n\n"
        "`cand-2325`→[Marco Sacconi 人物卡](../units/persons/marco-sacconi.md)。页233、240的姓氏提及由书后索引全名定位；8条直接关系候选留待 S6，3条评价性陈述保持非关系。"
        "未新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig") + process_note
    result_text += result_note

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("S4 person dry-run passed: cand-2325 maps to one source-local Marco Sacconi KU")
        print("8 relation candidates and 3 non-relational appraisals verified across pp.233 and 240")
        print("Ferdinand de' Medici, Niccolò Cassana, and Venice reuse targets verified; no external identity source added")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}")
        print(f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; new alignment rows pending=4,580")
        print("no files changed")
        return 0

    (ROOT / CARD_REL).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Marco Sacconi registered; manifest={len(planned_manifest)}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
