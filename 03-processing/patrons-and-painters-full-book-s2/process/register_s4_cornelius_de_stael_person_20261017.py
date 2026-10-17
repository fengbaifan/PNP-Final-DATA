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

CANDIDATES = ("cand-2504", "cand-6082")
GROUP = "new-person:cornelius-de-stael-012d225974"
KU_ID = "units/persons/cornelius-de-stael"
CARD_REL = "04-knowledge/units/persons/cornelius-de-stael.md"
NAME_EN = "Cornelius de Stael"
TITLE = "科内利乌斯·德·斯塔尔（Cornelius de Stael）"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
RELATION_IDS = {
    "st-chp5-p122-stael-preference",
    "st-chp5-p122-stael-business-with-painters",
    "st-chp5-note-p122-n6-letter-source",
}
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
ANCHOR = "s4-cornelius-de-stael-person-20261017"


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第5章；印刷页122；OCR L25",
            "sentence_summary": (
                "Haskell将Cornelius de Stael称为dealer，并转述其1663年向客户表达的观点：与画家交易麻烦，"
                "他更愿意购买已经完成的画作。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 25",
                    "text": "as one dealer, Cornelius de Stael, explained to a client in 1663",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "line 25; print p. 122",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第5章；印刷页122；注6；OCR L137",
            "sentence_summary": (
                "Haskell注6称一封1663年6月9日由Cornelius de Stael致Don Antonio Ruffo的信，"
                "并指向V. Russo第170页；原信、被引刊本及V. Russo身份未在本任务中独立查阅。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 137",
                    "text": "Letter from Cornelius de Stael to Don Antonio Ruffo dated 9 June 1663",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "line 137; print p. 122, note 6",
            },
        },
    ]
    frontmatter = {
        "title": TITLE,
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    src1 = f"[第5章 p.122](../../../{SOURCE_FILE})（L25）"
    src2 = f"[第5章 p.122 注6](../../../{SOURCE_FILE})（L137）"
    body = f"""## 内容

### 描述

**中文：** Haskell在第5章将Cornelius de Stael称为dealer，转述他于1663年向客户表示，与画家交易十分麻烦，自己更愿意购买已经完成的画作。第5章注6又引用一封1663年6月9日由de Stael致Don Antonio Ruffo的信。此卡只保留本书可追溯的人物身份范围；不补写生卒年、出生地或其他传记信息。原信、V. Russo刊本及其身份均未在本任务中独立查阅。{src1} {src2}

**English:** In Chapter 5 Haskell calls Cornelius de Stael a dealer and reports his 1663 explanation to a client that dealing with painters was troublesome and that he preferred buying pictures already painted. Note 6 in the same chapter cites a letter from de Stael to Don Antonio Ruffo dated 9 June 1663. This card is limited to the person identity traceable in the book; it adds no birth or death dates, birthplace, or other biography. The letter, V. Russo's publication, and Russo's identity were not independently consulted for this task. {src1} {src2}

### 本书相关内容

同一完整姓名见于第5章正文及注6。正文把他置于1663年与客户讨论向画家委托新作、或购买已完成画作的语境；注6另引其致Don Antonio Ruffo的书信。书内相邻锚点支持本候选组的身份归并，不据此推导书外履历。{src1} {src2}

## 关系与证据

本卡未新增正式关系。下列S2关系候选仍在`book-statements.jsonl`，待端点与证据进入S6审查：

- `st-chp5-p122-stael-preference`
- `st-chp5-p122-stael-business-with-painters`
- `st-chp5-note-p122-n6-letter-source`（书信候选`cand-6083`）

注6所列刊者`V. Russo`对应候选`cand-11913`，当前S3身份待决；本卡不推补其全名或刊本信息。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S3 Cornelius de Stael person group as one person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
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
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual_relations == RELATION_IDS, actual_relations

    card_path = ROOT / CARD_REL
    current_manifest = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    current_name = [
        row for row in manifest
        if row.get("type") == "person" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
    ]
    assert len(current_name) <= 1, "person name already exists in manifest"
    registered = (
        len(current_manifest) == 1
        and card_path.exists()
        and CARD_REL in accepted_paths
        and all(alignment_by_id[cid].get("ku_id") == KU_ID for cid in CANDIDATES)
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
            print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; candidate_mappings=2; relation_candidates=3 remain non-formal.")
        return 0

    assert not current_manifest and not card_path.exists() and CARD_REL not in accepted_paths
    assert not current_name, "a person KU with this exact English name already exists; inspect before registration"

    group_members = {
        row["candidate_id"]
        for row in alignments
        if row.get("candidate_id")
        and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(CANDIDATES), group_members
    for cid in CANDIDATES:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "person"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == GROUP

    source = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    assert "as one dealer, Cornelius de Stael, explained to a client in 1663" in source
    assert "Letter from Cornelius de Stael to Don Antonio Ruffo dated 9 June 1663" in source

    planned_alignment = [dict(row) for row in alignments]
    for cid in CANDIDATES:
        target = next(
            row for row in planned_alignment
            if row.get("candidate_id") == cid and not row.get("external_source")
        )
        target["ku_id"] = KU_ID
        target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": TITLE,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 person：Cornelius de Stael 跨章同组登记（2026-10-17）\n\n"
        f"`cand-2504`（S.csv#193；p.122）与`cand-6082`（第5章 p.122 注6）沿用S3组`{GROUP}`，"
        f"合登记为[{KU_ID}](../../../{CARD_REL})。两处均明确给出相同全名；正文称其为dealer，注6引用其1663年6月9日致Don Antonio Ruffo的信。"
        "人物卡限定于书内有据身份，不补传记。注6列出的V. Russo仍为候选`cand-11913`，身份待决；原信和被引刊本未独立查阅。"
        "3条直接S2关系候选保留待S6，本批未写入正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Cornelius de Stael 身份组登记（2026-10-17）\n\n"
        f"`cand-2504`与`cand-6082`作为一个S3人物身份组映射至[人物卡](../units/persons/cornelius-de-stael.md)。"
        "人物卡仅记录Haskell对其dealer身份及1663年书信的书内描述；V. Russo身份、原信和刊本未核。"
        "3条直接关系候选仍待S6。\n\n"
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
        print(f"S4 person dry-run passed: {CANDIDATES} -> {KU_ID}; identity_group={GROUP}")
        print("groups=1; candidate_mappings=2; relation_candidates=3; formal_relations_added=0")
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
        f"applied: groups=1; candidate_mappings=2; registered="
        f"{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
