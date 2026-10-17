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

CANDIDATE_ID = "cand-1350"
GROUP = "new-person:labia-maria-60556f1ddc"
KU_ID = "units/persons/maria-labia"
CARD_REL = "04-knowledge/units/persons/maria-labia.md"
NAME_ZH = "玛丽亚·拉比亚"
NAME_EN = "Maria Labia"
ANCHOR = "s4-person-maria-labia-20261017"
SOURCE_FILE = "02-sources/02-Markdown/09_CHP-9_intro.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
QUOTE = "Moreover, Maria Labia, doyenne of the family and a ‘femme sur le retour qui a été fort belle et fort galante’, owned a famous collection of jewelry of which she was especially proud."
EXPECTED_RELATION_IDS = {
    "st-chp9-p257-maria-labia-doyenne-and-description",
    "st-chp9-p257-maria-labia-identifies-with-cleopatra",
    "st-chp9-p257-maria-labia-jewelry-collection",
    "st-chp9-p257-tiepolo-delicate-compliment-to-maria",
}


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页257；OCR L168",
            "sentence_summary": "哈斯克尔称 Maria Labia 为 Labia 家族的 doyenne，并提及她拥有一组珍爱的珠宝；同段关于她与Cleopatra的对应及Tiepolo恭维意图，属于作者解释。",
            "original_quotes": [{
                "source_span": "lines 168; print p. 257",
                "text": QUOTE,
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "lines 168; print p. 257",
            },
        }],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[第9章书内来源](../../../{SOURCE_FILE})"
    relation_lines = "\n".join(f"- `{sid}`" for sid in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** Haskell在第9章以全名 Maria Labia 指称Labia家族的一名成员，称其为家族的“doyenne”，并在讨论Tiepolo的宴饮题材时提到她拥有珍爱的珠宝收藏。关于她与Cleopatra珍珠赌约的对应，以及Tiepolo有意恭维她，均是Haskell在同段提出的解释，不作为Maria本人的自述或直接证词。中文名“玛丽亚·拉比亚”为工作音译。{source_link}

**English:** In Chapter 9 Haskell names Maria Labia as a member of the Labia family, calls her its “doyenne,” and mentions her valued jewelry collection while discussing Tiepolo’s banquet subject. Haskell’s proposed identification of Maria with Cleopatra in the pearl-wager story, and his inference that Tiepolo intended a compliment, remain authorial interpretations rather than Maria’s testimony. The Chinese display name is a working transliteration. {source_link}

### 姓名与身份范围

- 书中全名：Maria Labia。{source_link}
- 中文显示名：“玛丽亚·拉比亚”为工作音译，不声明为已核定通行译名。{source_link}
- 身份边界：本卡指向书中具名个人；既有Labia家族卡继续表示家族整体，个人珠宝及书内称谓不自动作为家族财产或正式成员关系登记。{source_link}

## 关系与证据

### 关系记录

当前没有新增正式关系。以下4条直接S2关系候选保留于`book-statements.jsonl`，待S6逐条核对端点、关系语义及作者限定；其中珠宝集合尚未完成类型裁决：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Maria Labia's source-supported person identity in S4.")
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
    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    candidate = candidate_by_id[CANDIDATE_ID]
    alignment = alignment_by_id[CANDIDATE_ID]
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Labia, Maria"
    assert candidate.get("index_entry_id") == "L.csv#7"
    assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    assert len(manifest_targets) <= 1
    registered = bool(manifest_targets) and alignment.get("ku_id") == KU_ID and CARD_REL in accepted_paths and card_path.exists()
    if registered:
        assert len(manifest_targets) == 1 and manifest_targets[0].get("name_en") == NAME_EN
        assert card_path.read_text(encoding="utf-8-sig") == make_card()
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 4 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and not alignment.get("ku_id") and not card_path.exists() and CARD_REL not in accepted_paths
    assert not any(
        row.get("type") == "person" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "Maria Labia already exists as a person KU"

    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == {CANDIDATE_ID}, group_members
    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == EXPECTED_RELATION_IDS, (direct_relations, EXPECTED_RELATION_IDS)
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    assert " ".join(QUOTE.split()) in source_text

    planned_alignment = [dict(row) for row in alignments]
    planned_alignment_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    target_alignment = planned_alignment_by_id[CANDIDATE_ID]
    target_alignment["ku_id"] = KU_ID
    target_alignment["resolution_note"] = target_alignment["resolution_note"].replace(
        "KU assignment remains for S4.",
        "S3 recorded the identity decision for S4 registration; the mapping is applied below.",
    )
    target_alignment["resolution_note"] += f" S4 registration applied: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
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
        "### S4 person：Maria Labia 人物身份登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`（`{GROUP}`）登记为[Maria Labia人物卡](../../../{CARD_REL})。"
        "S3依据索引L.csv#7及第9章第257页正文全名，将其与Labia家族卡区分为个人人物KU；书内称谓和作者对Cleopatra对应及Tiepolo创作意图的推断均保留来源限定。"
        "4条直接关系候选仍待S6；珠宝集合端点尚未完成类型裁决，未新增正式关系或外部身份记录。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### person：Maria Labia 书内身份组 S4 登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}` → [人物卡](../units/persons/maria-labia.md)。"
        "卡片仅保留第9章第257页的人物名称与书内语境，将家族整体与个人区分；珠宝收藏及作者解释按来源边界陈述。4条直接S2关系候选仍待S6，未新增正式关系或外部身份断言。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    planned_accepted = "\n".join(accepted_lines[:insert_at] + [f"- {CARD_REL}"] + accepted_lines[insert_at:]) + "\n"

    if args.dry_run:
        print(f"S4 person dry-run passed: {GROUP} -> {KU_ID}")
        print(f"direct relation candidates={len(direct_relations)}; source quotation=ch. 9 p. 257; index=L.csv#7")
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
        f"applied: {GROUP} -> {KU_ID}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
