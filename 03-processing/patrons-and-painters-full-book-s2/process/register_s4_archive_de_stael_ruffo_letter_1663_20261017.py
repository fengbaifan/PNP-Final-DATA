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

CANDIDATE_ID = "cand-6083"
GROUP = "archive-group-cd4ab1cc6b5f"
KU_ID = "units/archives/de-stael-letter-to-ruffo-1663-06-09"
CARD_REL = "04-knowledge/units/archives/de-stael-letter-to-ruffo-1663-06-09.md"
NAME_EN = "Letter from Cornelius de Stael to Don Antonio Ruffo, 9 June 1663"
TITLE = "科内利乌斯·德·斯塔尔致唐·安东尼奥·鲁福的信（1663年6月9日）"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
RELATION_IDS = {
    "st-chp5-note-p122-n6-letter-source",
    "st-chp5-note-p122-n6-letter-addressed-to",
    "st-chp5-note-p122-n6-letter-published-by",
}
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
ANCHOR = "s4-de-stael-ruffo-letter-1663-06-09-20261017"


def make_card() -> str:
    sources = [{
        "citation": BOOK_CITATION,
        "location": "第5章；印刷页122；注6；OCR L137",
        "sentence_summary": (
            "Haskell注6著录Cornelius de Stael于1663年6月9日致Don Antonio Ruffo的一封信，"
            "并称其由V. Russo刊布于第170页。原信与被引刊本未在本任务中独立查阅。"
        ),
        "original_quotes": [{
            "source_span": "line 137",
            "text": (
                "Letter from Cornelius de Stael to Don Antonio Ruffo dated 9 June 1663 "
                "published by V. Russo, p; 170."
            ),
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": "line 137; print p. 122, note 6",
        },
    }]
    frontmatter = {
        "title": f"{TITLE}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[第5章 p.122 注6](../../../{SOURCE_FILE})（L137）"
    body = f"""## 内容

### 描述

**中文：** Haskell第5章注6著录一封1663年6月9日由Cornelius de Stael致Don Antonio Ruffo的信，并称该信刊于V. Russo第170页。本卡以通信双方、日期和该书内引文识别书信；原信、刊本均未独立查阅。{source_link}

**English:** Chapter 5 note 6 records a letter from Cornelius de Stael to Don Antonio Ruffo dated 9 June 1663 and says it was published by V. Russo on page 170. This card identifies the letter by its correspondents, date, and citation in the book; neither the letter nor the publication was independently consulted. {source_link}

### 文献身份边界

**中文：** 中英文题名均为描述性工作题名，不是原信题名。Haskell没有在该注中给出档案馆藏地或被引刊本题名。`V. Russo`对应候选`cand-11913`仍待S3身份裁决，并与另一条V. Russo候选`cand-3530`保持分开；本卡不推补刊者全名或刊本书目信息。书中OCR转录`p; 170`，本卡保留原抽取形式，不据此作刊本校勘。

**English:** Both titles are descriptive working titles, not an original title. Haskell's note gives neither an archival repository for the letter nor the title of the cited publication. `V. Russo` is candidate `cand-11913`, whose S3 identity remains undecided and is kept separate from another V. Russo candidate, `cand-3530`; no full name or publication metadata is inferred. The book OCR transcribes `p; 170`; this card preserves that extracted form and does not claim to have collated the publication.

## 关系与证据

本卡不新增正式关系。以下S2关系候选仍在`book-statements.jsonl`，待S6依据端点和证据裁决：

- 作者：`st-chp5-note-p122-n6-letter-source`（`cand-6082` → 本信）
- 收信人：`st-chp5-note-p122-n6-letter-addressed-to`（本信 → `cand-2297`）
- 刊者：`st-chp5-note-p122-n6-letter-published-by`（本信 → `cand-11913`，身份待决）
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Haskell's cited 1663 de Stael-Ruffo letter in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE_ID)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    statements = sync.load_statements()

    actual_relations = {
        row["statement_id"]
        for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual_relations == RELATION_IDS, actual_relations
    assert candidate.get("suggested_type") == "archive"
    assert candidate.get("canonical_name") == "Letter from Cornelius de Stael to Don Antonio Ruffo dated 9 June 1663"
    assert candidate.get("candidate_source_ref") == "chp-5:05_CHP-5_sec_i:l125-147#L137"

    author = alignment_by_id["cand-6082"]
    recipient = alignment_by_id["cand-2297"]
    publisher = alignment_by_id["cand-11913"]
    assert author.get("ku_id") == "units/persons/cornelius-de-stael"
    assert recipient.get("ku_id") == "units/persons/antonio-ruffo"
    assert publisher.get("decision") == "undecided" and not publisher.get("ku_id")

    card_path = ROOT / CARD_REL
    target_manifest = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    exact_name_manifest = [
        row for row in manifest
        if row.get("type") == "archive" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
    ]
    assert len(exact_name_manifest) <= 1
    registered = (
        len(target_manifest) == 1
        and card_path.exists()
        and CARD_REL in accepted_paths
        and alignment_by_id[CANDIDATE_ID].get("ku_id") == KU_ID
    )
    if registered:
        expected = make_card()
        current = card_path.read_text(encoding="utf-8-sig")
        if current != expected:
            if not args.apply:
                print(f"registered KU found but card content differs: {CARD_REL}; run --apply to refresh the generated card")
                return 1
            card_path.write_text(expected, encoding="utf-8-sig", newline="\n")
            print(f"refreshed generated card only: {CARD_REL}")
        else:
            print(f"ALREADY REGISTERED: {CANDIDATE_ID} -> {KU_ID}; 3 relation candidates remain non-formal.")
        return 0

    assert not target_manifest and not card_path.exists() and CARD_REL not in accepted_paths
    assert not exact_name_manifest, "same archive name already exists; inspect the target KU before registration"
    alignment = alignment_by_id[CANDIDATE_ID]
    assert alignment.get("decision") == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    members = {
        row["candidate_id"]
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert members == {CANDIDATE_ID}, members

    source = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    assert "Letter from Cornelius de Stael to Don Antonio Ruffo dated 9 June 1663" in source
    assert "published by V. Russo, p; 170." in source

    planned_alignment = [dict(row) for row in alignments]
    target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE_ID and not row.get("external_source")
    )
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": TITLE,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 archive：Cornelius de Stael 致 Don Antonio Ruffo 书信（1663-06-09）登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`沿用S3组`{GROUP}`，映射至[书信档案卡](../../../{CARD_REL})。"
        "Haskell第5章 p.122 注6给出书信双方、日期及V. Russo第170页的刊布线索；原信和被引刊本未独立查阅。"
        "作者cand-6082与收信人cand-2297已有KU映射；刊者候选cand-11913仍为undecided，且不与cand-3530合并。"
        "3条直接S2关系候选保留待S6，本批未新增正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 archive：de Stael–Ruffo 书信身份登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`映射至[书信档案卡](../units/archives/de-stael-letter-to-ruffo-1663-06-09.md)。"
        "身份依据限于Haskell第5章 p.122 注6；原信与刊本未独立查阅。刊者`V. Russo`身份仍待决，3条关系候选留待S6。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
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
        print(f"S4 archive dry-run passed: {CANDIDATE_ID} -> {KU_ID}; identity_group={GROUP}")
        print("groups=1; candidate_mappings=1; relation_candidates=3; unresolved_publisher=cand-11913; formal_relations_added=0")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,}->{len(planned_manifest):,}"
        )
        print("no files changed")
        return 0

    card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=1; candidate_mappings=1; registered="
        f"{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
