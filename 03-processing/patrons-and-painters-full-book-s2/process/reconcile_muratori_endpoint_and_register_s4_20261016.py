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
PERSON_CANDIDATE = "cand-1717"
INDEX_ARCHIVE = "cand-1718"
TEXT_ARCHIVE = "cand-9705"
GROUP = "archive-group-muratori-della-pubblica-felicita-text"
KU_ID = "units/archives/della-pubblica-felicita-1749"
CARD_REL = "04-knowledge/units/archives/della-pubblica-felicita-1749.md"
NAME_ZH = "《论公共幸福：良善君主的目标》"
NAME_EN = "On Public Happiness, the Aim of Good Princes"
ORIGINAL_TITLE = "Della pubblica felicità, oggetto de’ buoni principi"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
QUOTE = (
    "In 1749 Muratori published his\n"
    "Della puhblica felicita, oggetto de’buoni principi whose title alone proclaimed the advanced ideas inherent in the thesis;"
)
STATEMENT_ID = "st-chp10-p318-muratori-published-della-pubblica-felicita"
MENTION_ID = "m-s2-ch10-p318-0010"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s2-s4-muratori-20261016"


def make_card():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "treatise",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": (
                "第10章，印刷页318；Markdown 行135–136；Markdown OCR 的题名拼写与重音由 S2 对照 "
                "CHP-10.pdf 物理页51记录校读；不表示查阅 Muratori 原著。"
            ),
            "sentence_summary": (
                "第10章称 Muratori 于1749年出版其论著，并评论题名体现论旨中的先进观念。"
                "Markdown OCR 写作“Della puhblica felicita, oggetto de’buoni principi”；S2 对照扫描印本记录为 "
                "*Della pubblica felicità, oggetto de’ buoni principi*。"
            ),
            "original_quotes": [{"source_span": "lines 135–136", "text": QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "lines 135–136; print p. 318; PDF physical p. 51",
            },
        }],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    evidence = "[第10章 p.318](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L135–136）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记 Haskell 第10章提及的论著 *{ORIGINAL_TITLE}*。正文称 Muratori 于1749年出版此书，并评论题名本身体现了论旨中的先进观念。Markdown OCR 行136将题名识为 `Della puhblica felicita, oggetto de’buoni principi`；S2 对照 Haskell 扫描印本，记录为 *Della pubblica felicità, oggetto de’ buoni principi*。本卡记录 Haskell 的书内说法，不表示查阅 Muratori 原著。中英文显示题名均为描述性工作译名。{evidence}

**English:** This card records the treatise *{ORIGINAL_TITLE}* named in Haskell’s Chapter 10. The passage says Muratori published it in 1749 and comments that the title itself expressed advanced ideas in its thesis. Markdown OCR line 136 reads `Della puhblica felicita, oggetto de’buoni principi`; S2 compared Haskell’s scanned page and recorded the reading as *Della pubblica felicità, oggetto de’ buoni principi*. This card records Haskell’s account and does not imply consultation of Muratori’s work. The Chinese and English display titles are descriptive working translations. {evidence}

### 文献身份与版本边界

- **原题名：** *Della pubblica felicità, oggetto de’ buoni principi*；Haskell 第10章 p.318。Markdown OCR 异文及扫描印本校读范围已保留在来源记录中。{evidence}
- **作者与出版年份：** Haskell 称 Muratori 于1749年出版该论著；本卡不据此扩展具体出版地、出版者、版次或存世副本。人物全名及外部身份未由本段单独确认。{evidence}
- **题名译文：** 中文“《论公共幸福：良善君主的目标》”及英文 “On Public Happiness, the Aim of Good Princes” 为描述性工作译名；原题名保留意大利语。{evidence}

### 身份边界

S3 新身份组 `{GROUP}` 由索引子项候选 `{INDEX_ARCHIVE}` 与正文题名候选 `{TEXT_ARCHIVE}` 组成，指向同一文本。人物候选 `{PERSON_CANDIDATE}` 与本 archive 分开；其完整个人身份仍处于 S3 待证状态。本卡不将来源提及扩展为外部人物身份，也不指定该论著的具体刊本。

## 关系与证据

当前没有登记正式关系。Haskell 关于 Muratori 于1749年出版此论著的 statement 保留为一条 S2 关系候选；人物端点身份待 S3 决定，正式边留待 S6。{evidence}
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Correct Muratori's person mention mapping and register the 1749 treatise archive in S4."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidates_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
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
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decision_by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert candidate_by_id[PERSON_CANDIDATE].get("suggested_type") == "person"
    assert candidate_by_id[PERSON_CANDIDATE].get("canonical_name") == "Muratori, L. A."
    assert candidate_by_id[INDEX_ARCHIVE].get("suggested_type") == "archive"
    assert candidate_by_id[INDEX_ARCHIVE].get("sub_entry") == "Della pubblica felicità oggetto de' buoni principi"
    assert candidate_by_id[TEXT_ARCHIVE].get("suggested_type") == "archive"
    assert decision_by_id[PERSON_CANDIDATE].get("decision") == "undecided"
    for cid in (INDEX_ARCHIVE, TEXT_ARCHIVE):
        assert decision_by_id[cid].get("decision") == "new"
        assert sync.get_group(decision_by_id[cid].get("resolution_note", "")) == GROUP

    mention_by_id = {row["mention_id"]: row for row in mentions}
    mention = mention_by_id[MENTION_ID]
    assert mention.get("candidate_id") == INDEX_ARCHIVE and mention.get("surface_form") == "Muratori"
    statement_by_id = {row["statement_id"]: row for row in statements}
    statement = statement_by_id[STATEMENT_ID]
    assert statement.get("subject_candidate_id") == INDEX_ARCHIVE
    assert statement.get("object_candidate_id") == TEXT_ARCHIVE
    assert statement.get("qualifiers", {}).get("relation_candidate") is True
    assert statement.get("original_quote") == QUOTE
    assert "Della puhblica felicita" in (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    assert "Della pubblica felicità" in (ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "M.csv").read_text(encoding="utf-8-sig")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and ORIGINAL_TITLE.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    assert "S2 mapping correction: Muratori p.318" not in stages_text
    assert "S4 archive: Della pubblica felicità" not in knowledge_text
    targets = [
        TABLES / "mentions.csv", statements_path, TABLES / "ku-manifest.csv",
        ACCEPTED, KNOWLEDGE, STAGES, RESULT,
    ]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in targets), "recovery backup already exists"

    planned_mentions = [dict(row) for row in mentions]
    planned_mention = next(row for row in planned_mentions if row["mention_id"] == MENTION_ID)
    planned_mention["candidate_id"] = PERSON_CANDIDATE
    planned_mention["note"] = (
        "Maps the named author form Muratori to the existing person candidate cand-1717 (L. A. Muratori). "
        "Keep distinct from the Della pubblica felicità archive title candidate cand-9705; the person's S3 identity remains undecided."
    )

    planned_statements = [dict(row) for row in statements]
    planned_statement = next(row for row in planned_statements if row["statement_id"] == STATEMENT_ID)
    planned_statement["subject_candidate_id"] = PERSON_CANDIDATE
    planned_statement["object_candidate_id"] = TEXT_ARCHIVE
    planned_statement["qualifiers"] = dict(planned_statement["qualifiers"])
    planned_statement["qualifiers"]["mentioned_candidate_ids"] = [PERSON_CANDIDATE, TEXT_ARCHIVE]
    planned_statement["qualifiers"]["qualification"] += (
        " S2 endpoint mapping correction (2026-10-16): 'Muratori' maps to person candidate cand-1717; "
        "its S3 identity remains undecided because the source form supplies initials only."
    )

    planned_alignment = [dict(row) for row in alignments]
    planned_decisions = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    person_note = planned_decisions[PERSON_CANDIDATE]["resolution_note"]
    planned_decisions[PERSON_CANDIDATE]["resolution_note"] = person_note + (
        f" Additional mapped mention {MENTION_ID} at chp-10 p.318 L135; "
        "this passage confirms the source-local person reference but does not resolve the full name, "
        "so the existing undecided status remains."
    )
    archive_note = planned_decisions[INDEX_ARCHIVE]["resolution_note"]
    planned_decisions[INDEX_ARCHIVE]["resolution_note"] = archive_note.replace(
        f"mentions={MENTION_ID}", f"former_S2_mention_mapping={MENTION_ID} (corrected to person {PERSON_CANDIDATE})", 1
    ) + " The index subentry remains part of this archive identity group; the p.318 author mention is not mapped to it."
    planned_decisions[INDEX_ARCHIVE]["process_ref"] = "S2-S4-follow-up-2026-10-16"
    planned_decisions[PERSON_CANDIDATE]["process_ref"] = "S2-S3-follow-up-2026-10-16"
    assert {
        cid for cid, row in planned_decisions.items()
        if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    } == {INDEX_ARCHIVE, TEXT_ARCHIVE}
    assert planned_decisions[PERSON_CANDIDATE]["decision"] == "undecided"

    planned_alignment_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in (INDEX_ARCHIVE, TEXT_ARCHIVE):
        planned_alignment_by_id[cid]["ku_id"] = KU_ID
        planned_alignment_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = make_card()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated archive card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    s2_append = (
        f"\n\n### 第十章 p.318 Muratori 人物／论著端点更正（{DATE}）\n\n"
        f"复核 `{MENTION_ID}` 后发现表面形式“Muratori”误映射至 archive 候选 `{INDEX_ARCHIVE}`；该候选实际是 *Della pubblica felicità* 的索引子项。现将 mention 与 `{STATEMENT_ID}` 主语改映射至人物候选 `{PERSON_CANDIDATE}`，论著宾语保持 `{TEXT_ARCHIVE}`。Haskell 原句、statement claim、题名 OCR 及扫描印本校读未改；人物候选因全名仅有 initials 仍保持 S3 `undecided`。候选、mention、statement 数量不变。"
    )
    s4_append = (
        f"\n\n### S4 archive：Muratori《Della pubblica felicità》1749年论著身份组登记（{DATE}）\n\n"
        f"- `{INDEX_ARCHIVE}`（索引子项）与 `{TEXT_ARCHIVE}`（正文题名）→ `{GROUP}` → `{KU_ID}`；第10章 p.318 记 Muratori 于1749年出版该论著。S2 对照扫描页校读题名为 `{ORIGINAL_TITLE}`，原 OCR 形式保留在 sources.original_quotes 与过程记录；具体版次、出版地及存世副本未由本段确定。\n"
        f"- p.318 的人物 mention 与 statement 主语已从 archive 子项候选移至 `{PERSON_CANDIDATE}`。该 person 候选保留 `undecided`（只有缩写形式，尚无全名对齐）；因此作者／出版关系候选继续待证，本批不登记人物 KU、不新增正式关系或 S5 补足。\n"
        f"- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_knowledge = knowledge_text + s4_append
    next_stages = stages_text + s2_append
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    next_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: S2 {MENTION_ID} {INDEX_ARCHIVE}->{PERSON_CANDIDATE}; "
            f"statement subject corrected; {PERSON_CANDIDATE} stays undecided; "
            f"archive {INDEX_ARCHIVE},{TEXT_ARCHIVE}->{KU_ID}; relation_candidates_pending=1; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
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
    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
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
        f"applied: S2 Muratori endpoint corrected; S3 person remains undecided; "
        f"registered {GROUP} -> {KU_ID}; relation_candidates_pending=1; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"recovery backups={len(write_targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
