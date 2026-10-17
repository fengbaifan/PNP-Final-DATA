from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATES = ("cand-7931",)
GROUP = "archive-group-f87eaeb73c93"
KU_ID = "units/archives/karl-loth-letter-to-grand-prince-ferdinand-1691-08-14"
CARD_REL = "04-knowledge/units/archives/karl-loth-letter-to-grand-prince-ferdinand-1691-08-14.md"
CH8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {"st-chp8-p233-note5-loth-letter"}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第8章注5；印刷页233；OCR L423",
            "sentence_summary": (
                "Haskell经 Fogolari 1937 转述一封 Karl Loth 于1691年8月14日写给 Prince 的信：信中感谢对方赠送油和酒，"
                "并说 Loth 将开始临摹提香《圣彼得殉难》。篇章上下文将该 Prince 指向 Grand Prince Ferdinand。"
                "本书引用和原信未在本任务中独立查阅，临摹计划不证明作品已完成。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 423",
                    "text": (
                        "5 Fogolari, 1937, publishes a letter from Loth of 14 August 1691 thanking the Prince for a present of oil and wine "
                        "and telling him that he is about to embark on a copy of Titian’s St Peter Martyr."
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH8,
                "source_span": "line 423; print p. 233, note 5",
            },
        }
    ]
    frontmatter = {
        "title": (
            "卡尔·洛特致费迪南多大公的信（1691年8月14日）"
            "（Letter from Karl Loth to Grand Prince Ferdinand, 14 August 1691）"
        ),
        "name_en": "Letter from Karl Loth to Grand Prince Ferdinand, 14 August 1691",
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source = f"[第8章 p.233 注5](../../../{CH8})（L423）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记 Haskell 在第8章注5中提及的一封具体书信：Karl Loth 于1691年8月14日写给 Prince；篇章上下文将其指向 Grand Prince Ferdinand。Haskell称信中感谢对方赠送油和酒，并说自己将开始临摹提香《圣彼得殉难》。卡片标题为便于识别而拟定的描述性标题，不是原件题名。Haskell经 Fogolari 1937 转述；该刊本与原信均未在本任务中独立查阅，因而卡片只记录书内可追溯的文献身份和转述范围，不声称已读信件全文。{source}

**English:** This card registers a specific letter mentioned in Chapter 8 note 5: Karl Loth wrote to the Prince on 14 August 1691; the chapter context identifies the recipient as Grand Prince Ferdinand. Haskell says the letter thanks him for a gift of oil and wine and reports Loth’s intention to begin a copy after Titian’s St Peter Martyr. The bilingual title is descriptive and is not presented as an original title. Haskell reports the letter through Fogolari 1937; neither that publication nor the letter was independently consulted for this task. The card therefore records the document identity and the scope of the book’s report, not a claim to have read the letter in full. {source}

### 文献身份边界

候选 `cand-7931` 指 1691年8月14日的具体书信，不是 Fogolari 1937 这一刊载来源。书信及刊本未独立查阅；Haskell 的转述是本卡当前唯一书内依据。原信未给出自题名，本卡的中英文题名均为描述性拟题。书中所述临摹提香作品是计划，不能据此认定临摹已经完成。

Candidate `cand-7931` denotes the specific letter dated 14 August 1691, not the Fogolari 1937 publication in which it is cited. Neither the letter nor the publication was independently consulted; Haskell’s account is the present book-based evidence. No original title is supplied, so both card titles are descriptive. The reported plan to copy Titian does not establish that the copy was completed.

## 关系与证据

1条直接 S2 `relation_candidate` 保留待 S6：`st-chp8-p233-note5-loth-letter`（Karl Loth → 本信）。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cited 1691 Karl Loth letter archive identity in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert not (ROOT / CARD_REL).exists()
    assert CARD_REL not in accepted
    assert not any(
        row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL
        or (row.get("type") == "archive" and (row.get("name_en") or "").casefold() == "letter from karl loth to grand prince ferdinand, 14 august 1691")
        for row in manifest
    ), "Karl Loth letter archive KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["canonical_name"] == "Letter from Karl Loth to Grand Prince Ferdinand (1691-08-14; cited in Fogolari 1937)"
    assert candidate["suggested_type"] == "archive"
    assert candidate["candidate_source_ref"] == "chp-8:08_CHP-8_sec_ii:l372-461#L423"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    chapter = (ROOT / CH8).read_text(encoding="utf-8-sig")
    assert "letter from Loth of 14 August 1691" in chapter
    assert "thanking the Prince for a present of oil and wine" in chapter
    assert "about to embark on a copy of Titian’s St Peter Martyr" in chapter
    assert alignment_by_id["cand-1442"]["ku_id"] == "units/persons/johann-karl-loth"

    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == RELATION_CANDIDATES, direct_relations

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATES[0] and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "卡尔·洛特致费迪南多大公的信（1691年8月14日）",
        "name_en": "Letter from Karl Loth to Grand Prince Ferdinand, 14 August 1691",
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-karl-loth-letter-1691-08-14-archive\"></a>\n\n"
        "### S4 archive：Karl Loth 致 Grand Prince Ferdinand 的信（1691-08-14）登记（2026-10-17）\n\n"
        f"`cand-7931`（source anchor: {candidate['candidate_source_ref']}）沿用 S3 archive 组 `{GROUP}`，映射至"
        f"[该书信档案卡](../../../{CARD_REL})。Haskell 注5经 Fogolari 1937 转述此信日期、收信人和内容；"
        "刊本与原信未独立查阅，卡片使用描述性题名，不声称读取全文。\n\n"
        "此候选作为 Loth 人物的直接 archive 端点单独登记；`st-chp8-p233-note5-loth-letter` 保留待 S6，未新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 archive：Karl Loth 致 Grand Prince Ferdinand 的信（1691-08-14）登记（2026-10-17）\n\n"
        f"`cand-7931` 映射至[书信档案卡](../units/archives/karl-loth-letter-to-grand-prince-ferdinand-1691-08-14.md)。"
        "身份依据限于 Haskell 对 Fogolari 1937 的转述；刊本与原信未独立查阅。"
        "与 Loth 的 1 条直接关系候选仍待 S6，未登记正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 Karl Loth letter archive dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"identity_group={GROUP}; candidates={len(group_rows)}; direct_relation_candidates={len(direct_relations)}")
        print("source_scope=Haskell reports Fogolari 1937; letter and publication not independently consulted")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / CARD_REL).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATES[0]} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
