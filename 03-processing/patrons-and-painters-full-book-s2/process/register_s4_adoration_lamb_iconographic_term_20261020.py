from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
TABLES = ROOT / "04-knowledge" / "tables"
sys.path.insert(0, str(PROCESS_DIR))

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync
import register_s4_work_second_scuola_scheme_20261020 as s4_helpers

PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
AGENTS_PATH = ROOT / "AGENTS.md"

CANDIDATE = "cand-5291"
GROUP = "sg3-term-cand-5291"
KU_ID = "units/terms/adoration-of-the-lamb-iconographic-subject"
CARD_REL = "04-knowledge/units/terms/adoration-of-the-lamb-iconographic-subject.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "羔羊崇拜图像主题"
NAME_EN = "Adoration of the Lamb (iconographic subject)"
DATE = "2026-10-20"
PROCESS_ANCHOR = "s4-term-adoration-lamb-iconographic-subject-20261020"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
SOURCE_FILE = "03_CHP-3_sec_iv.md"
SOURCE_QUOTE = (
    "He revived the subject of The Adoration of the Lamb which had been hardly seen in Rome "
    "since the mosaics in S. Prassede and S. Maria Maggiore many hundred years earlier."
)
ICONOGRAPHY_QUOTE = (
    "Much of the traditional iconography was used. The Book on the throne is sealed with seven "
    "seals, and before it burn seven torches. Twenty-four ancients adore the Lamb; behind are "
    "youths with palms and angels trumpeting and lifting up their thuribles to fill them with prayers."
)
RELATION_IDS = {
    "st-chp3-seciv-l75-81-ancient-maggiore-mosaic",
    "st-chp3-seciv-l75-81-ancient-prassede-mosaic",
    "st-chp3-seciv-l75-81-baroque-transfer-judgment",
    "st-chp3-seciv-l75-81-iconographic-elements",
    "st-chp3-seciv-l75-81-revived-lamb-subject",
    "st-chp3-seciv-l75-81-theme-in-oliva-writings",
}


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": "第3章，印刷页84；OCR L76",
            "sentence_summary": "哈斯克尔将羔羊崇拜称为后殿图像主题，并描述其传统图像元素及罗马较早的马赛克实例。",
            "original_quotes": [
                {"source_span": "line 76; print p. 84", "text": SOURCE_QUOTE},
                {"source_span": "line 76; print p. 84", "text": ICONOGRAPHY_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{SOURCE_FILE}",
                "source_span": "line 76; print p. 84",
            },
        }],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 定义与范围

**中文：** 本术语记录哈斯克尔在第3章 p.84 所称的羔羊崇拜图像主题。哈斯克尔称 Gaulli 在耶稣堂后殿恢复了这一主题，并指出在罗马，继 S. Prassede 与 S. Maria Maggiore 的马赛克之后，数百年间很少再见到这一主题。他描述的图像元素包括封印之书、七个印、七支火炬、二十四位长老、持棕枝的青年以及吹号和焚香的天使。此术语指图像主题本身，不指 Gaulli 的后殿壁画、两处较早的马赛克或拱顶原拟表现的基督受难主题。上述年代与艺术史表述均为哈斯克尔的书内陈述，未在本卡独立核验。来源：[第3章 p.84](../../../02-sources/02-Markdown/{SOURCE_FILE}#L76)。

**English:** This term records the iconographic subject Haskell calls the Adoration of the Lamb (Chapter 3, p. 84). Haskell says Gaulli revived the subject in the Gesù apse and notes that in Rome it had hardly been seen since the mosaics at S. Prassede and S. Maria Maggiore many centuries earlier. He describes its imagery as including the sealed book with seven seals, seven torches, twenty-four elders, youths with palms, and angels with trumpets and thuribles. The term denotes the subject itself, not Gaulli’s apse fresco, the two earlier mosaics, or the glorification of Christ’s suffering proposed for the vault. These chronological and art-historical statements remain Haskell’s account and have not been independently verified here. Source: [Chapter 3, p. 84](../../../02-sources/02-Markdown/{SOURCE_FILE}#L76).

### 书内用例

候选 `cand-5291` 来自哈斯克尔对后殿主题、传统图像元素及 Oliva 著述中相关主题的叙述。现有作品 KU [耶稣堂后殿《羔羊崇拜》壁画](../works/gaulli-gesu-apse-adoration-of-the-lamb-fresco.md)记录具体壁画；本术语与该壁画及更早马赛克分别登记。

## 关系与证据

### 关系记录

以下6条直接 S2 关系候选保留待 S6 逐条裁决；本卡不预判关系类型、方向或事实成立：{", ".join(f"`{item}`" for item in sorted(RELATION_IDS))}。
"""


def preserve_bom_write_csv(path: Path, fieldnames, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fieldnames, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Adoration of the Lamb subject in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert CANDIDATE in candidate_by_id
    assert candidate_by_id[CANDIDATE].get("suggested_type") == "term"

    target_rows = [
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(target_rows) == 1
    target = target_rows[0]
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert result_sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row.get("candidate_id") for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "term"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for row in manifest
    ), "same-title term already exists in the manifest"

    source_text = " ".join((ROOT / "02-sources" / "02-Markdown" / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    assert " ".join(SOURCE_QUOTE.split()) in source_text
    assert " ".join(ICONOGRAPHY_QUOTE.split()) in source_text

    statements = result_sync.load_statements()
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_ids = {row["statement_id"] for row in direct_statements}
    relation_ids = {
        row["statement_id"] for row in direct_statements
        if row.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert direct_ids == RELATION_IDS, (direct_ids - RELATION_IDS, RELATION_IDS - direct_ids)
    assert relation_ids == RELATION_IDS

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] = (
        (planned_target.get("resolution_note") or "")
        + f" S4 registration: mapped {GROUP} to {KU_ID}; term denotes the iconographic subject, distinct from the apse fresco and earlier mosaics."
    )
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "term",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]

    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    before_queue = s4_helpers.compute_direct_queue(candidate_by_id, alignments, statements)
    direct_queue = s4_helpers.compute_direct_queue(candidate_by_id, planned_alignment, statements)
    assert before_queue["groups"] == direct_queue["groups"] + 1
    assert before_queue["members"] == direct_queue["members"] + 1
    assert before_queue["endpoint_candidates"] == direct_queue["endpoint_candidates"] + 1

    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_entry = (
        "\n\n### S4 term：羔羊崇拜图像主题（2026-10-20）\n\n"
        f"`{CANDIDATE}` 沿用既有S3 `new`组 `{GROUP}`，登记至[羔羊崇拜图像主题卡](../units/terms/adoration-of-the-lamb-iconographic-subject.md)。"
        "第3章 p.84 将其作为 Gaulli 后殿壁画所表现的主题，并分别提及较早的 S. Prassede、S. Maria Maggiore 马赛克；"
        "主题、壁画和马赛克保持分立。6条直接 S2 关系候选留待 S6，本批未新增正式关系、外部身份或 S5 字段。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])}组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])}条映射；"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射。"
    )
    result_text = result_text.rstrip() + result_entry + "\n"

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text = s4_helpers.refresh_knowledge_table(process_text, stats)
    process_entry = (
        "\n\n<a id=\"" + PROCESS_ANCHOR + "\"></a>\n\n"
        "### S4 term：羔羊崇拜图像主题（2026-10-20）\n\n"
        f"`{CANDIDATE}`沿用S3 `new`术语组 `{GROUP}`，登记为[羔羊崇拜图像主题卡](../../../{CARD_REL})。"
        "第3章 p.84 是本卡身份与定义的书内依据：哈斯克尔称 Gaulli 在耶稣堂后殿恢复了该主题，"
        "提到 S. Prassede 与 S. Maria Maggiore 的早期马赛克，并描述封印之书、七盏灯、二十四长老、持棕枝青年及吹号和焚香天使等传统图像元素。"
        "本卡将主题与后殿壁画、两处较早马赛克以及拱顶原拟表现的基督受难主题分开；所有年代和艺术史表述仅记为哈斯克尔所述，未作外部核验。"
        f"6条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）仍待 S6；本批不登记 formal 关系或 S5 字段。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}组／{result_sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射；"
        f"直接端点队列由{before_queue['groups']}组／{before_queue['members']}成员降至{direct_queue['groups']}组／{direct_queue['members']}成员。"
        "S2 第3章复核指出 `st-chp3-seciv-l75-81-revived-lamb-subject` 将主题误指向作品候选；本次只登记正确类型的主题KU，不改动该statement，待S2修订时再按复核意见回核。"
    )
    process_text = process_text.rstrip() + process_entry + "\n"
    enrichment = [
        json.loads(line)
        for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    agents_text = s4_helpers.refresh_agents(
        AGENTS_PATH.read_text(encoding="utf-8-sig"), totals, direct_queue,
        statements, result_sync.read_csv(TABLES / "relations.csv")[1], enrichment,
    )

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 term dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"source anchor=chapter 3 p.84 L76; direct S2 relation candidates={len(relation_ids)}; no formal edge created")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(
            f"registered={totals['registered_groups']:,}/{totals['new_groups']:,} groups, "
            f"{totals['registered_members']:,}/{totals['new_candidates']:,} mappings; "
            f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}"
        )
        print(f"direct queue={before_queue['groups']:,}/{before_queue['members']:,} -> {direct_queue['groups']:,}/{direct_queue['members']:,}")
        print("result, process table, and AGENTS snapshot refreshed in memory only")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8", newline="\n")
    preserve_bom_write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    preserve_bom_write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']:,}/{totals['registered_members']:,}; "
        f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}; "
        f"direct={before_queue['groups']:,}->{direct_queue['groups']:,} groups"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
