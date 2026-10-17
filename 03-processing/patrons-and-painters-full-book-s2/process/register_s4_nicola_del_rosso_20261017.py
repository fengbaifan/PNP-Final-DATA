from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s3-s4-person-nicola-del-rosso-20261017"
CANDIDATES = ("cand-2285", "cand-7611")
GROUP = "new-person:del-nicola-rosso-e3ae15d1b4"
KU_ID = "units/persons/nicola-del-rosso"
CARD_REL = "04-knowledge/units/persons/nicola-del-rosso.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "尼科拉·德尔·罗索"
NAME_EN = "Nicola del Rosso"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/Q-R.csv"
SOURCE_211 = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE_212 = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
RELATION_IDS = (
    "st-chp8-p211-nicola-father-of-antonio",
    "st-chp8-p211-nicola-father-of-giovanni-battista",
    "st-chp8-p212-n5-panciatichi-nicola-kinship",
)
NON_RELATION_ID = "st-chp8-p211-nicola-died-1710"

SOURCES = (
    {
        "location": "书后索引，Q-R.csv#213；索引定位 p.211、p.212 n.5",
        "summary": "索引主项 Rosso, Nicola del 定位至正文 p.211 与注释 p.212 n.5；该项提供书内定位。",
        "quote": '"Rosso, Nicola del",,,,"211, 212n"',
        "span": "Q-R.csv#213",
        "doc_id": "patrons-and-painters-index",
        "file": INDEX_FILE,
    },
    {
        "location": "第8章，印刷页211；OCR L84–96",
        "summary": "Haskell 称德尔罗索家族继承人是第四个兄弟 Nicola 的两个儿子 Antonio 与 Giovanni Battista；该段称 Nicola 于1710年去世。该句的关系候选与去世年份陈述分别保留。",
        "quote": "The heirs were the two sons, Antonio and Giovanni Battista, of a fourth brother Nicola who died in 1710",
        "span": "lines 84–96; print p. 211",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_211,
    },
    {
        "location": "第8章注释，印刷页212；OCR L126–157，注5",
        "summary": "注5以全名 Nicola del Rosso 指认第四个兄弟，并称参议员 Francesco Panciatichi 是他的岳父。",
        "quote": "was the father-in-law of Nicola del Rosso, the fourth brother.",
        "span": "line 153; print p. 212 n. 5",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_212,
    },
)


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": item["doc_id"],
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relations = "\n".join(f"- `{sid}`" for sid in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第8章 p.211 与 p.212 注5 所述、并由索引主项定位的 Nicola del Rosso。p.211 将他称作 Rosso 家族的第四个兄弟，记述其两个儿子 Antonio 与 Giovanni Battista 作为继承人，并称他于1710年去世。p.212 注5 以全名 Nicola del Rosso 重提“第四个兄弟”，并称参议员 Francesco Panciatichi 是他的岳父。中文显示名为项目工作音译；本卡不补写书外生平。

**English:** This card records the Nicola del Rosso discussed on p. 211 and p. 212 n. 5 of Haskell’s chapter 8 and located by the index main entry. On p. 211 Haskell identifies him as the fourth Rosso brother, says that his two sons Antonio and Giovanni Battista were the heirs, and reports that he died in 1710. Note 5 on p. 212 names Nicola del Rosso in full as “the fourth brother” and says that Senator Francesco Panciatichi was his father-in-law. The Chinese display name is a project working transliteration; no external biography is added.

### 名称与身份边界

索引主项 `Rosso, Nicola del`（Q-R.csv#213）列 p.211、p.212 n.5。p.211 的“第四个兄弟 Nicola”与 p.212 注5 的全名及相同“四弟”限定相合；候选 `cand-2285` 与 `cand-7611` 据此保留在同一个人物组。Antonio 与 Giovanni Battista 是文中另列的儿子，不与父亲合并。去世于1710年的内容是 Haskell 的叙述，不是关系边。

The index main entry `Rosso, Nicola del` (Q-R.csv#213) lists p. 211 and p. 212 n. 5. The “fourth brother Nicola” on p. 211 matches the full name and same “fourth brother” qualification in note 5; candidates `cand-2285` and `cand-7611` therefore remain in one person group. Antonio and Giovanni Battista are separately named as his sons and are not merged with him. The 1710 death statement is Haskell’s narration, not a relation edge.

## 关系与证据

本次没有新增正式关系。以下3条直接 S2 关系候选留待 S6 逐项审查：

{relations}

`{NON_RELATION_ID}` 是去世年份陈述，维持非关系状态。本次未写入 `relations.csv`。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the two-candidate Nicola del Rosso person group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    if (
        CARD_PATH.exists()
        and any(row.get("ku_id") == KU_ID for row in manifest)
        and all(decisions[cid].get("decision") == "new" and decisions[cid].get("ku_id") == KU_ID for cid in CANDIDATES)
        and all(sync.get_group(decisions[cid].get("resolution_note", "")) == GROUP for cid in CANDIDATES)
    ):
        print("ALREADY REGISTERED: Nicola del Rosso two-candidate person group")
        return 0

    assert len(manifest) == 1553 and len(alignments) == 12642
    assert all(candidate_map[cid]["suggested_type"] == "person" for cid in CANDIDATES)
    assert all(decisions[cid]["decision"] == "new" and not decisions[cid].get("ku_id") for cid in CANDIDATES)
    assert all(sync.get_group(decisions[cid].get("resolution_note", "")) == GROUP for cid in CANDIDATES)
    members = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in members} == set(CANDIDATES)
    assert not CARD_PATH.exists() and CARD_REL not in ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)

    for rel, snippets in {
        INDEX_FILE: ("Rosso, Nicola del", "211, 212n"),
        SOURCE_211: ("The heirs were the two sons, Antonio and Giovanni Battista, of a fourth brother Nicola who died in 1710",),
        SOURCE_212: ("was the father-in-law of Nicola del Rosso, the fourth brother.",),
    }.items():
        text = (ROOT / rel).read_text(encoding="utf-8-sig")
        for snippet in snippets:
            assert snippet in text, f"source excerpt missing from {rel}: {snippet}"

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    direct = [row for row in statements.values() if set(CANDIDATES) & {row.get("subject_candidate_id"), row.get("object_candidate_id")}]
    assert {row["statement_id"] for row in direct} == set(RELATION_IDS) | {NON_RELATION_ID}
    assert all(statements[sid]["qualifiers"].get("relation_candidate") is True for sid in RELATION_IDS)
    assert statements[NON_RELATION_ID]["qualifiers"].get("relation_candidate") is False

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    assert len(planned_manifest) == 1554
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert (totals["registered_groups"], totals["registered_members"], totals["pending_groups"], totals["pending_members"]) == (535, 670, 4269, 4309)

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_warning = "审计警告中的4,326条待登记 `decision=new` alignment 行，含4,311条候选决定映射（4,270组）和15条外部身份记录。"
    new_warning = "审计警告中的4,324条待登记 `decision=new` alignment 行，含4,309条候选决定映射（4,269组）和15条外部身份记录。"
    assert old_warning in result_text
    result_text = result_text.replace(old_warning, new_warning, 1)

    process_entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Nicola del Rosso 两候选跨页并组登记（{DATE}）

`cand-2285`（Q-R.csv#213，主项定位 p.211、p.212 n.5）与 `cand-7611`（p.212 n.5 全名正文候选）共同保留在 `{GROUP}`，登记为[Nicola del Rosso 人物卡](../../../04-knowledge/units/persons/nicola-del-rosso.md)。p.211 称第四个兄弟 Nicola 的两名儿子 Antonio 与 Giovanni Battista 为继承人，并称 Nicola 于1710年去世；p.212 n.5 再以全名指认“第四个兄弟”，并称其岳父为 Francesco Panciatichi。索引主项、全名和亲属限定支持同一人物。去世年份是非关系陈述；未补外部生平。

3条直接 S2 关系候选 `{RELATION_IDS[0]}`、`{RELATION_IDS[1]}`、`{RELATION_IDS[2]}` 留待 S6；本次未新增正式关系或写入 `relations.csv`。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip() + process_entry
    result_note = (
        f"\n\n### S3→S4 person：Nicola del Rosso（{DATE}）\n\n"
        "`cand-2285`、`cand-7611`→[Nicola del Rosso 人物卡](../units/persons/nicola-del-rosso.md)。p.211 的第四兄弟与 p.212 n.5 的全名、亲属限定相合。"
        "3条直接关系候选留待 S6；去世年份陈述不作为关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("dry-run passed: cand-2285 and cand-7611 map to one Nicola del Rosso person KU")
        print("p.211 and p.212 n.5 full-name, fourth-brother and kinship evidence verified")
        print("three relation candidates remain for S6; 1710 death statement remains non-relational")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; pending-new alignment rows=4,324; relations unchanged")
        print("planned writes: person card, accepted.yml, ku-manifest.csv, alignment.csv, process record, result")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Nicola del Rosso registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
