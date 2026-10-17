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

CANDIDATE_ID = "cand-5287"
GROUP = "workgrp-02e05bf99bb333"
KU_ID = "units/works/gaulli-gesu-apse-adoration-of-the-lamb-fresco"
CARD_REL = "04-knowledge/units/works/gaulli-gesu-apse-adoration-of-the-lamb-fresco.md"
NAME_ZH = "耶稣堂后殿《羔羊崇拜》壁画"
NAME_EN = "Adoration of the Lamb Fresco in the Apse of the Gesù"
ANCHOR = "s4-work-gaulli-gesu-apse-adoration-of-the-lamb-20261017"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
QUOTES = (
    "In the apse, which was completed only after the death of Oliva, Gaulli was required to return to the more abstruse levels of theology which had characterised his frescoes in the dome.",
    "He revived the subject of The Adoration of the Lamb which had been hardly seen in Rome since the mosaics in S. Prassede and S. Maria Maggiore many hundred years earlier.",
)
EXPECTED_RELATION_IDS = {
    "st-chp3-seciv-l75-81-baroque-transfer-judgment",
    "st-chp3-seciv-l75-81-christ-suffering-theme",
    "st-chp3-seciv-l75-81-iconographic-elements",
    "st-chp3-seciv-l75-81-possible-farnese-concession",
    "st-chp3-seciv-l75-81-return-to-dome-theology",
    "st-chp3-seciv-l75-81-revived-lamb-subject",
    "st-chp3-seciv-l75-81-triumphant-tone",
}


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": "第3章；印刷页84；OCR L76；PDF physical p. 26",
            "sentence_summary": "Haskell将Gesù后殿与Gaulli联系起来，并称其复兴《羔羊崇拜》题材；古代罗马马赛克指向相同图像题材，非同一作品。",
            "original_quotes": [
                {"source_span": "line 76; print p. 84; PDF physical p. 26", "text": quote}
                for quote in QUOTES
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "line 76; print p. 84; PDF physical p. 26",
            },
        }],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[第3章书内来源](../../../{SOURCE_FILE})"
    relation_lines = "\n".join(f"- `{sid}`" for sid in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** Haskell第3章描述Gesù后殿的作品，并称Gaulli在该处复兴《羔羊崇拜》题材；同段把这一题材与数百年前S. Prassede和S. Maria Maggiore的马赛克区分为不同作品。中文题名为依地点和题材拟定的描述性暂题，不声称是原题。本卡只指Gesù后殿的壁画，不与Gaulli在该教堂的穹顶／拱顶作品、旧马赛克或图像题材本身合并。{source_link}

**English:** Chapter 3 describes the work in the apse of the Gesù and says Gaulli revived the subject of the Adoration of the Lamb there; the same passage distinguishes this work from mosaics at S. Prassede and S. Maria Maggiore made centuries earlier. The Chinese title is a descriptive working title based on location and subject, not an asserted original title. This card identifies only the apse fresco, separate from Gaulli’s dome or vault works in the church, earlier mosaics, and the iconographic subject itself. {source_link}

### 题名与身份范围

- 中文描述性暂题：耶稣堂后殿《羔羊崇拜》壁画。
- English descriptive working title: Adoration of the Lamb Fresco in the Apse of the Gesù.
- 作品身份：特定建筑空间中的壁画对象；《羔羊崇拜》作为图像题材及先前马赛克均保持独立对象边界。

## 关系与证据

### 关系记录

当前没有新增正式关系。以下7条直接S2关系候选继续待S6逐条核对；关于题材选择原因的两种解释、Gaulli与作品的联系及作者评价按原有语气保留：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-defined Gesù apse Adoration fresco work in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_alignments = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate = candidate_by_id[CANDIDATE_ID]
    alignment = candidate_alignments[CANDIDATE_ID]
    assert candidate.get("suggested_type") == "work"
    assert candidate.get("canonical_name") == "Gaulli's Adoration of the Lamb fresco in the Gesù apse"
    assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    assert len(manifest_targets) <= 1
    registered = bool(manifest_targets) and alignment.get("ku_id") == KU_ID and CARD_REL in accepted_paths and card_path.exists()
    if registered:
        assert len(manifest_targets) == 1 and manifest_targets[0].get("name_en") == NAME_EN
        assert card_path.read_text(encoding="utf-8-sig") == make_card()
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 7 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and not alignment.get("ku_id") and not card_path.exists() and CARD_REL not in accepted_paths
    assert not any(
        row.get("type") == "work" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "The Gesù apse Adoration of the Lamb fresco already exists as a work KU"

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
    normalized_source = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for quote in QUOTES:
        assert " ".join(quote.split()) in normalized_source, quote

    planned_alignment = [dict(row) for row in alignments]
    planned_alignment_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_alignment_by_id[CANDIDATE_ID]["ku_id"] = KU_ID
    planned_alignment_by_id[CANDIDATE_ID]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; distinct from dome/vault projects, earlier mosaics, and the iconographic subject."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "work",
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
        "### S4 work：Gaulli的Gesù后殿《羔羊崇拜》壁画登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`（`{GROUP}`）登记为[后殿壁画知识卡](../../../{CARD_REL})。"
        "Haskell第3章第84页描述Gesù后殿中Gaulli与《羔羊崇拜》题材的联系，并明确以数百年前S. Prassede和S. Maria Maggiore的马赛克作为旧有题材对照。此作品与manifest中Gaulli的Gesù穹顶／拱顶项目及《耶稣圣名的胜利》分别登记；候选题名为描述性暂题。"
        "7条直接S2关系候选仍待S6，包括作者联系、题材关系、作者推断与评价；未新增正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### work：Gesù后殿《羔羊崇拜》壁画 S4 登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}` → [作品卡](../units/works/gaulli-gesu-apse-adoration-of-the-lamb-fresco.md)。题名为描述性暂题；后殿壁画、旧马赛克和图像题材分别保留。7条直接关系候选仍待S6，未新增正式关系。\n\n"
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
        print(f"S4 work dry-run passed: {GROUP} -> {KU_ID}")
        print(f"direct relation candidates={len(direct_relations)}; source=ch.3 p.84 PDF physical p.26; existing dome/vault works remain separate")
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
