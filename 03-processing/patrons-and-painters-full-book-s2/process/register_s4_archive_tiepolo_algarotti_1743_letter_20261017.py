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

CANDIDATES = ("cand-8379", "cand-10280")
GROUP = "archive-group-tiepolo-algarotti-letter-1743-10-26"
KU_ID = "units/archives/tiepolo-letter-to-algarotti-1743-10-26"
CARD_REL = "04-knowledge/units/archives/tiepolo-letter-to-algarotti-1743-10-26.md"
NAME_ZH = "乔万巴蒂斯塔·提埃坡罗致弗朗切斯科·阿尔加罗蒂的信（1743年10月26日）"
NAME_EN = "Letter from Giambattista Tiepolo to Francesco Algarotti, 26 October 1743"
ANCHOR = "s4-archive-tiepolo-algarotti-letter-1743-10-26"
SOURCE_9 = "02-sources/02-Markdown/09_CHP-9_intro.md"
SOURCE_14 = "02-sources/02-Markdown/14_CHP-14_intro.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
EXPECTED_RELATION_IDS = {
    "st-chp9-p256-note5-tiepolo-letter-publication",
    "st-chp14-p352-1743-letter-authored-by-tiepolo",
    "st-chp14-p352-1743-letter-addressed-to-algarotti",
}
SOURCE_QUOTES = (
    (SOURCE_9, "8 Letter from Tiepolo to Francesco Algarotti of 26 October 1743 published by Fogolari, 1.942, p. 34."),
    (SOURCE_14, "and in October Tiepolo wrote Algarotti an exceedingly friendly letter from the Villa Cordellina, which he was then decorating, saying how much he would enjoy having a discussion with him about painting.3"),
    (SOURCE_14, "3 Letter of 26 October 1743 published by G. Fogolari, 1942, p. 34."),
)


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页256；注5；OCR L377",
            "sentence_summary": "Haskell的注5把一封1743年10月26日Tiepolo致Francesco Algarotti的信定位至Fogolari 1942年刊本第34页；该信与刊本未在本批独立查阅。",
            "original_quotes": [{
                "source_span": "line 377; print p. 256, note 5; PDF physical p. 18",
                "text": SOURCE_QUOTES[0][1],
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_9,
                "source_span": "line 377; print p. 256, note 5; PDF physical p. 18",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章；印刷页352；OCR L57",
            "sentence_summary": "Haskell称Tiepolo于1743年10月从Villa Cordellina致信Algarotti，表示希望与他讨论绘画；信件全文未在本批独立查阅。",
            "original_quotes": [{
                "source_span": "line 57; print p. 352",
                "text": SOURCE_QUOTES[1][1],
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_14,
                "source_span": "line 57; print p. 352",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章；印刷页352；注3；OCR L184",
            "sentence_summary": "第14章注3将正文所述信件定为1743年10月26日，并同样定位至Fogolari 1942年刊本第34页。",
            "original_quotes": [{
                "source_span": "line 184; print p. 352, note 3",
                "text": SOURCE_QUOTES[2][1],
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_14,
                "source_span": "line 184; print p. 352, note 3",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source9 = f"[第9章书内来源](../../../{SOURCE_9})"
    source14 = f"[第14章书内来源](../../../{SOURCE_14})"
    relation_lines = "\n".join(f"- `{sid}`" for sid in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** Haskell第9章注5将其著录为Giambattista Tiepolo于1743年10月26日致Francesco Algarotti的信，并指向Fogolari 1942年刊本第34页。第14章正文也记述同年10月Tiepolo从Villa Cordellina致信Algarotti，希望与他讨论绘画；注3给出的日期和刊引与第9章注5相同。两章候选据发送人、收信人、日期及刊引归为同一封书信。原信及Fogolari刊本未在本批独立查阅。{source9} {source14}

**English:** Chapter 9 note 5 identifies this as Giambattista Tiepolo’s letter to Francesco Algarotti dated 26 October 1743 and points to Fogolari’s 1942 publication, page 34. Chapter 14 also reports that Tiepolo wrote Algarotti from Villa Cordellina in October of that year, wishing to discuss painting; note 3 gives the same date and publication locator as Chapter 9. The two chapter candidates are grouped as one letter based on the correspondents, date, and publication reference. Neither the letter nor Fogolari’s publication was independently consulted in this batch. {source9} {source14}

### 文献身份边界

本卡题名为据书内寄收件人和日期拟定的描述性工作题名，不是原信题名。第9章OCR中的注号和年份已由S2依据印刷页图像校正；原信及Fogolari 1942年刊本仍未独立查阅。

## 关系与证据

### 关系记录

当前没有新增正式关系。以下3条直接S2关系候选继续保留，待S6分别核对作者、收信人及出版著录；本卡不表示已读原信或Fogolari刊本：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Tiepolo–Algarotti letter identity group in S4.")
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
    for cid in CANDIDATES:
        candidate = candidate_by_id[cid]
        alignment = candidate_alignments[cid]
        assert candidate.get("suggested_type") == "archive"
        assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    assert len(manifest_targets) <= 1
    registered = bool(manifest_targets) and all(candidate_alignments[cid].get("ku_id") == KU_ID for cid in CANDIDATES) and CARD_REL in accepted_paths and card_path.exists()
    if registered:
        assert len(manifest_targets) == 1 and manifest_targets[0].get("name_en") == NAME_EN
        assert card_path.read_text(encoding="utf-8-sig") == make_card()
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 3 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and all(not candidate_alignments[cid].get("ku_id") for cid in CANDIDATES)
    assert not card_path.exists() and CARD_REL not in accepted_paths
    assert not any(
        row.get("type") == "archive" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "The 26 October 1743 Tiepolo–Algarotti letter already exists as an archive KU"

    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(CANDIDATES), group_members
    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == EXPECTED_RELATION_IDS, (direct_relations, EXPECTED_RELATION_IDS)
    for rel, quote in SOURCE_QUOTES:
        normalized = " ".join((ROOT / rel).read_text(encoding="utf-8-sig").split())
        assert " ".join(quote.split()) in normalized, (rel, quote)

    planned_alignment = [dict(row) for row in alignments]
    planned_candidate_alignments = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        planned_candidate_alignments[cid]["ku_id"] = KU_ID
        planned_candidate_alignments[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
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
        "### S4 archive：Tiepolo–Algarotti 1743年10月26日书信跨章身份组登记（2026-10-17）\n\n"
        f"`{', '.join(CANDIDATES)}`（`{GROUP}`）共同登记为[该书信档案卡](../../../{CARD_REL})。"
        "第9章第256页注5与第14章第352页正文、注3均指向Giambattista Tiepolo致Francesco Algarotti、1743年10月26日、Fogolari 1942年刊本第34页；发送人、收信人、日期及刊引一致，两个章节候选归入同一个archive KU。"
        "沿用S2对第9章扫描页18的校勘：OCR注号8、年份1.942分别校正为印刷注5、1942；原信和Fogolari刊本未在本批独立查阅。3条直接S2关系候选继续待S6，未新增正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### archive：Tiepolo–Algarotti书信跨章身份组 S4 登记（2026-10-17）\n\n"
        f"`{CANDIDATES[0]}`（第9章）与`{CANDIDATES[1]}`（第14章）共同映射至[同一书信档案卡](../units/archives/tiepolo-letter-to-algarotti-1743-10-26.md)。两处对通信双方、日期及Fogolari 1942年刊本第34页的著录相同；原信和刊本未独立查阅。3条直接关系候选继续待S6，未新增正式关系。\n\n"
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
        print(f"S4 archive dry-run passed: {GROUP} -> {KU_ID}")
        print(f"chapter candidates={len(CANDIDATES)}; chapters=9,14; direct relation candidates={len(direct_relations)}; citations=3")
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
