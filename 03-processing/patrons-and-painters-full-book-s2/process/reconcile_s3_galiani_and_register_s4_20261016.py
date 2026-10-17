from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
STAGES = PROCESS_DIR / "stages.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"
PERSON_CANDIDATE = "cand-1102"
ARCHIVE_MEMBERS = ("cand-1103", "cand-9706")
ARCHIVE_GROUP = "archive-group-4ef32237dfae"
PREVIOUS_ARCHIVE_GROUP = "archive-group-d425674fd21e"
PERSON_GROUP = "sg3-person-cand-1102"
PERSON_KU = "units/persons/abate-galiani"
PERSON_CARD_REL = "04-knowledge/units/persons/abate-galiani.md"
ARCHIVE_KU = "units/archives/della-moneta-treatise-1750"
ARCHIVE_CARD_REL = "04-knowledge/units/archives/della-moneta-treatise-1750.md"
PERSON_ZH = "加利亚尼"
PERSON_EN = "Abate Galiani"
ARCHIVE_ZH = "《论货币》"
ARCHIVE_EN = "On Money"
ORIGINAL_TITLE = "Della Moneta"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/G.csv"
QUOTE = "in 1750 appeared the Abate Galiani’s treatise Della Moneta;"
STATEMENT_ID = "st-chp10-p318-galiani-della-moneta-appeared-in-1750"
MENTION_ID = "m-s2-ch10-p318-0012"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s3-s4-galiani-20261016"


def source_row(sentence_summary: str):
    return {
        "citation": BOOK_CITATION,
        "location": "第10章，印刷页318；Markdown 行136；Haskell 的书内陈述，未指明具体版次或存世副本。",
        "sentence_summary": sentence_summary,
        "original_quotes": [{"source_span": "lines 136", "text": QUOTE}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": "lines 136; print p. 318; PDF physical p. 51",
        },
    }


def person_card_text():
    frontmatter = {
        "title": f"{PERSON_ZH}（{PERSON_EN}）",
        "name_en": PERSON_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [source_row(
            "第10章印刷页318称 Abate Galiani 的论著 *Della Moneta* 于1750年问世；本卡只据此保留原书所用人名形式及其与该论著的联系。"
        )],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    evidence = "[第10章 p.318](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L136）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记 Haskell 第10章所称的 Abate Galiani。第318页将 *Della Moneta* 称为他的论著，并记其于1750年问世。卡片保留原书的人名形式，不推定其完整个人姓名、生卒、籍贯或其他传记；中文显示名为姓氏音译。{evidence}

**English:** This card records the person named by Haskell as Abate Galiani. On p. 318, Haskell describes *Della Moneta* as his treatise and says it appeared in 1750. The record preserves the name form used in the book and does not infer a fuller personal name, dates, birthplace, or other biography. The Chinese display name transliterates the surname. {evidence}

### 名称与身份

- **原书人名形式：** Abate Galiani；原书未在此处提供个人全名。此形式中的 `Abate` 保留为原书称谓，不另判定其法律姓名或教职状态。{evidence}
- **书内身份：** Haskell 将 *Della Moneta* 称为 Abate Galiani 的论著，并记其于1750年问世；本卡不据此扩展作者生平或作品清单。{evidence}

## 关系与证据

当前没有登记正式关系。与 *Della Moneta* 的作者／论著关系保留为一条 S2 关系候选，待 S6 裁决。{evidence}
"""


def archive_card_text():
    frontmatter = {
        "title": f"{ARCHIVE_ZH}（{ARCHIVE_EN}）",
        "name_en": ARCHIVE_EN,
        "type": "archive",
        "sub_type": "treatise",
        "evidence_status": "source_backed",
        "sources": [source_row(
            "第10章印刷页318将 *Della Moneta* 指为 Abate Galiani 的论著，并称其于1750年问世；索引下的 Della Moneta 子目与正文书名对应。具体刊本、版本及出版地未由本段确定。"
        )],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    evidence = "[第10章 p.318](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L136）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录 Haskell 第10章所称的论著 *Della Moneta*。正文称其为 Abate Galiani 的论著，并记其于1750年问世。该段没有给出出版地、出版者、版次或特定存世副本；本卡登记文本层级身份，不指向某个未明版本。中文题名为描述性工作译名。{evidence}

**English:** This card records the treatise *Della Moneta* named in Haskell’s Chapter 10. The passage calls it Abate Galiani’s treatise and says it appeared in 1750. It does not give a place or publisher, identify an edition, or point to a particular surviving copy; this record is at text level and does not designate an unspecified version. The English display title is a descriptive working translation. {evidence}

### 文献身份与版本边界

- **原题名：** *Della Moneta*；Haskell 第10章 p.318 正文及全书索引子目均指向该题名。{evidence}
- **文献类型：** 论著（treatise）；S3 身份粒度为文本，不推定具体初版、再版或副本。{evidence}
- **书内责任者：** Haskell 称其为 Abate Galiani 的论著；责任者人物入口为[Abate Galiani](../persons/abate-galiani.md)。此链接提供身份导航，不表示正式关系已登记。{evidence}
- **问世时间：** Haskell 称其于1750年问世；本卡不将此表述扩展为已核验的出版地、出版者或版本信息。{evidence}
- **显示题名：** 中文“《论货币》”与英文 “On Money” 均为描述性工作译名；原题名保留意大利语。{evidence}

### 身份边界

S3 新身份组 `{ARCHIVE_GROUP}` 包含索引子目候选 `cand-1103` 与正文题名候选 `cand-9706`，二者指向同一文本。它与人物候选 `cand-1102` 分开；不据同一索引责任者或作者联系合并人物与文献，也不扩展为某一具体版本。

## 关系与证据

当前没有登记正式关系。`Della Moneta` 与 Abate Galiani 及1750年问世信息对应一条直接 S2 关系候选，端点现已映射至本卡和人物卡，仍待 S6 裁决。{evidence}
"""


def add_manifest_row(manifest, ku_id, kind, canonical_name, name_en, card_rel):
    return list(manifest) + [{
        "ku_id": ku_id,
        "type": kind,
        "canonical_name": canonical_name,
        "name_en": name_en,
        "source_task": TASK,
        "card_path": card_rel,
    }]


def group_append_note(note: str, text: str) -> str:
    return note + " " + text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Correct the Galiani S2 endpoint mapping, reconcile S3 groups, and register person/text KUs."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    mention_fields, mentions = sync.read_csv(TABLES / "mentions.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    stages_text = STAGES.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    statements_path = TABLES / "book-statements.jsonl"
    statements = [
        json.loads(line)
        for line in statements_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert candidate_by_id[PERSON_CANDIDATE].get("suggested_type") == "person"
    assert candidate_by_id[PERSON_CANDIDATE].get("canonical_name") == "Galiani, Abate"
    assert candidate_by_id[PERSON_CANDIDATE].get("index_entry_id") == "G.csv#9"
    assert candidate_by_id["cand-1103"].get("suggested_type") == "archive"
    assert candidate_by_id["cand-1103"].get("sub_entry") == "della Moneta"
    assert candidate_by_id["cand-9706"].get("suggested_type") == "archive"
    assert decisions[PERSON_CANDIDATE].get("decision") == "undecided"
    assert decisions["cand-1103"].get("decision") == "new"
    assert sync.get_group(decisions["cand-1103"].get("resolution_note", "")) == ARCHIVE_GROUP
    assert decisions["cand-9706"].get("decision") == "new"
    assert sync.get_group(decisions["cand-9706"].get("resolution_note", "")) == PREVIOUS_ARCHIVE_GROUP

    mention_by_id = {row["mention_id"]: row for row in mentions}
    mention = mention_by_id[MENTION_ID]
    assert mention.get("candidate_id") == "cand-1103"
    assert mention.get("surface_form") == "Abate Galiani"
    statement_by_id = {row["statement_id"]: row for row in statements}
    statement = statement_by_id[STATEMENT_ID]
    assert statement.get("subject_candidate_id") == "cand-1103"
    assert statement.get("object_candidate_id") == "cand-9706"
    assert statement.get("qualifiers", {}).get("relation_candidate") is True
    assert statement.get("original_quote") == QUOTE
    assert "Abate Galiani" in (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    assert "Della Moneta" in (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    assert "della Moneta" in (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")

    person_path = ROOT / PERSON_CARD_REL
    archive_path = ROOT / ARCHIVE_CARD_REL
    assert not person_path.exists() and not archive_path.exists()
    assert PERSON_CARD_REL not in accepted and ARCHIVE_CARD_REL not in accepted
    for target in (PERSON_KU, ARCHIVE_KU):
        assert not any(row.get("ku_id") == target for row in manifest)
    assert not any(
        row.get("type") == "person"
        and PERSON_EN.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    assert not any(
        row.get("type") == "archive"
        and ORIGINAL_TITLE.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    targets = [
        TABLES / "alignment.csv", TABLES / "mentions.csv", statements_path,
        TABLES / "ku-manifest.csv", ACCEPTED, KNOWLEDGE, STAGES, RESULT,
    ]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in targets), "recovery backup already exists"
    assert "S3/S4 follow-up: Galiani" not in knowledge_text
    assert "第十章 p.318 Abate Galiani 端点回核" not in stages_text

    planned_mentions = [dict(row) for row in mentions]
    planned_mention = next(row for row in planned_mentions if row["mention_id"] == MENTION_ID)
    planned_mention["candidate_id"] = PERSON_CANDIDATE
    planned_mention["note"] = (
        "Rechecked the source syntax: Abate Galiani is the person named as the owner/author of the treatise; "
        "map this mention to person candidate cand-1102. The separate title Della Moneta maps to archive cand-9706; "
        "cand-1103 is the index-subentry archive candidate."
    )

    planned_statements = [dict(row) for row in statements]
    planned_statement = next(row for row in planned_statements if row["statement_id"] == STATEMENT_ID)
    planned_statement["subject_candidate_id"] = PERSON_CANDIDATE
    planned_statement["object_candidate_id"] = "cand-9706"
    planned_statement["qualifiers"] = dict(planned_statement["qualifiers"])
    planned_statement["qualifiers"]["mentioned_candidate_ids"] = [PERSON_CANDIDATE, "cand-9706"]
    planned_statement["qualifiers"]["qualification"] += (
        " S2 mapping correction (2026-10-16): Abate Galiani is mapped to the person candidate cand-1102; "
        "the treatise remains object cand-9706."
    )

    planned_alignment = [dict(row) for row in alignments]
    planned_decisions = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    old_person_note = planned_decisions[PERSON_CANDIDATE]["resolution_note"]
    planned_decisions[PERSON_CANDIDATE]["decision"] = "new"
    planned_decisions[PERSON_CANDIDATE]["resolution_note"] = (
        f"source_ref=chp-10:10_CHP-10_sec_ii:l133-142#L136; index_entry=G.csv#9; "
        f"mention={MENTION_ID}; statement={STATEMENT_ID}; group={PERSON_GROUP}; "
        "New source-local person named Abate Galiani in Haskell's p.318 passage; no exact person KU in the current manifest. "
        "Preserve this source form; the passage does not provide a fuller personal name or establish an external identity. "
        f"prior_undecided_reason={old_person_note}"
    )
    planned_decisions[PERSON_CANDIDATE]["process_ref"] = "S3-S4-follow-up-2026-10-16"
    old_archive_note = planned_decisions["cand-9706"]["resolution_note"]
    planned_decisions["cand-9706"]["resolution_note"] = old_archive_note.replace(
        f"group={PREVIOUS_ARCHIVE_GROUP}", f"group={ARCHIVE_GROUP}", 1
    ) + (
        f" S3 follow-up correction: merged with cand-1103 in {ARCHIVE_GROUP}; "
        "both candidates identify the same Della Moneta text from the page-specific index subentry and p.318 body title. "
        f"Previous group label retained here for traceability: {PREVIOUS_ARCHIVE_GROUP}."
    )
    planned_decisions["cand-9706"]["process_ref"] = "S3-S4-follow-up-2026-10-16"
    planned_decisions["cand-1103"]["resolution_note"] += (
        f" S3 follow-up correction: cand-9706 is the same Della Moneta text; "
        f"mention {MENTION_ID} was reattributed to person cand-1102. Group retained as {ARCHIVE_GROUP}."
    )
    planned_decisions["cand-1103"]["process_ref"] = "S3-S4-follow-up-2026-10-16"
    assert {
        cid for cid, row in planned_decisions.items()
        if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == ARCHIVE_GROUP
    } == set(ARCHIVE_MEMBERS)
    assert sync.get_group(planned_decisions[PERSON_CANDIDATE]["resolution_note"]) == PERSON_GROUP

    planned_alignment_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in ARCHIVE_MEMBERS:
        planned_alignment_by_id[cid]["ku_id"] = ARCHIVE_KU
        planned_alignment_by_id[cid]["resolution_note"] += f" S4 registration: mapped {ARCHIVE_GROUP} to {ARCHIVE_KU}."
    planned_alignment_by_id[PERSON_CANDIDATE]["ku_id"] = PERSON_KU
    planned_alignment_by_id[PERSON_CANDIDATE]["resolution_note"] += f" S4 registration: mapped {PERSON_GROUP} to {PERSON_KU}."

    planned_manifest = add_manifest_row(
        manifest, PERSON_KU, "person", PERSON_ZH, PERSON_EN, PERSON_CARD_REL
    )
    planned_manifest = add_manifest_row(
        planned_manifest, ARCHIVE_KU, "archive", ARCHIVE_ZH, ARCHIVE_EN, ARCHIVE_CARD_REL
    )
    person_card = person_card_text()
    archive_card = archive_card_text()
    for card in (person_card, archive_card):
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated KU frontmatter is invalid"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    s2_append = (
        f"\n\n### 第十章 p.318 Abate Galiani 端点回核（{DATE}）\n\n"
        f"复核 `m-s2-ch10-p318-0012` 后发现其表面形式“Abate Galiani”误映射至 archive 候选 `cand-1103`；第10章 p.318 L136 的语法将人物与其论著 *Della Moneta* 分开，现将该mention改映射至已有 person 候选 `cand-1102`。原 statement `{STATEMENT_ID}` 的主语同步改为 `cand-1102`，宾语保留 `cand-9706`；原文引句、断言内容、来源锚点及关系候选状态不变。\n"
        f"`cand-1103` 是 Galiani 索引下的 *della Moneta* 文献子项，索引页318与正文候选 `cand-9706` 的同题名文本相合；两者归入同一 archive 身份组。未新增或删除候选、mention、statement，也未把人物并入文献。"
    )
    s3_s4_append = (
        f"\n\n### S3/S4 follow-up: Galiani 人物端点与 *Della Moneta* 文本身份（{DATE}）\n\n"
        f"- S2 端点回核后，`cand-1102`（person）由原 `undecided` 改为 `new`，组 `{PERSON_GROUP}`。第10章 p.318 L136 明确称 Abate Galiani 的论著 *Della Moneta* 于1750年问世；当前 manifest 无同一人物 KU。裁决只保留原书人名形式，不扩展个人全名、传记或外部身份。\n"
        f"- S3 archive 组将 `cand-1103`（Galiani 索引中的 *della Moneta* 子项）与 `cand-9706`（正文具名论著）合并为 `{ARCHIVE_GROUP}`。两者同为 archive、题名对应同一文本且均锚定 p.318；没有证据表明指向不同版次。`cand-9706` 原组标记 `{PREVIOUS_ARCHIVE_GROUP}` 保存在其 `resolution_note` 的更正说明中。\n"
        f"- S4：`cand-1102` → `{PERSON_KU}`；`cand-1103,cand-9706` → `{ARCHIVE_KU}`。分别建立人物与文本卡，双语显示名均保留限定；文献卡不指定版次、出版地或存世副本。\n"
        f"- `{STATEMENT_ID}` 现以 `cand-1102` 为人物主语、`cand-9706` 为论著宾语；1条直接关系候选保持待 S6 裁决。本次未新增正式关系、外部身份标识或 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_knowledge = knowledge_text + s3_s4_append
    next_stages = stages_text + s2_append
    next_accepted_lines = accepted.splitlines()
    for card_rel in (PERSON_CARD_REL, ARCHIVE_CARD_REL):
        insert_at = next(
            (i for i, line in enumerate(next_accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
            next((i for i, line in enumerate(next_accepted_lines) if line == "claims:"), len(next_accepted_lines)),
        )
        next_accepted_lines.insert(insert_at, f"- {card_rel}")
    next_accepted = "\n".join(next_accepted_lines) + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: S2 {MENTION_ID} cand-1103->{PERSON_CANDIDATE}; "
            f"S3 person undecided->new; archive groups merged; "
            f"{PERSON_CANDIDATE}->{PERSON_KU}; {','.join(ARCHIVE_MEMBERS)}->{ARCHIVE_KU}; "
            f"relation_candidates_pending=1; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    write_targets = {
        TABLES / "alignment.csv": None,
        TABLES / "mentions.csv": None,
        statements_path: None,
        TABLES / "ku-manifest.csv": None,
        ACCEPTED: next_accepted,
        KNOWLEDGE: next_knowledge,
        STAGES: next_stages,
        RESULT: next_result,
    }
    for path in write_targets:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    person_path.write_text(person_card, encoding="utf-8-sig", newline="\n")
    archive_path.write_text(archive_card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "mentions.csv", mention_fields, planned_mentions)
    statements_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in planned_statements) + "\n",
        encoding="utf-8-sig",
        newline="\n",
    )
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    for path, content in write_targets.items():
        if content is not None:
            path.write_text(content, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: S2 endpoint remapped; S3 person/ archive decisions corrected; "
        f"registered {PERSON_KU} and {ARCHIVE_KU}; relation_candidates_pending=1; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"recovery backups={len(write_targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
