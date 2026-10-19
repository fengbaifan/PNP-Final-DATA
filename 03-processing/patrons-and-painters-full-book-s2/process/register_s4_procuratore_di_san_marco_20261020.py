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

CANDIDATE = "cand-8449"
GROUP = "sg3-term-cand-8449"
KU_ID = "units/terms/procuratore-di-san-marco-office"
CARD_REL = "04-knowledge/units/terms/procuratore-di-san-marco-office.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "圣马可 Procuratore 职位"
NAME_EN = "Procuratore di San Marco office"
DATE = "2026-10-20"
PROCESS_ANCHOR = "s4-term-procuratore-di-san-marco-office-20261020"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
SOURCE_9 = "02-sources/02-Markdown/09_CHP-9_intro.md"
SOURCE_10 = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
SOURCE_15 = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
RELATION_IDS = {
    "st-chp9-p258-marco-held-procuratore-and-doge-offices",
    "st-chp9-p259-pietro-foscarini-procuratore",
    "st-chp10-p326-election-1780",
    "st-chp10-p327-political-pictures-iconography",
    "st-chp15-p367-memmo-assumed-procurator-office-1787",
}
SOURCES = [
    {
        "file": SOURCE_9,
        "location": "第9章，印刷页258，来源转录 L186",
        "span": "line 186; print p. 258",
        "summary": "Haskell称 Marco Foscarini 自1741年起担任 Procuratore di San Marco。",
        "quote": "As Procuratore di San Marco from 1741",
    },
    {
        "file": SOURCE_9,
        "location": "第9章，印刷页259，来源转录 L193",
        "span": "line 193; print p. 259",
        "summary": "Haskell称前任业主 Pietro Foscarini 是一名 Procuratore di San Marco。",
        "quote": "Pietro Foscarini, himself a Procuratore di San Marco",
    },
    {
        "file": SOURCE_10,
        "location": "第10章，印刷页326，来源转录 L211–212",
        "span": "lines 211–212; print p. 326",
        "summary": "Haskell称 Pisani 于1780年在复杂的政治周旋后当选该职位。",
        "quote": "In 1780, after complicated intrigues, he was suddenly elected Procuratore di San Marco.",
    },
    {
        "file": SOURCE_10,
        "location": "第10章，印刷页327，来源转录 L225–226",
        "span": "lines 225–226; print p. 327",
        "summary": "政治图像描绘一名 Procurator 重建公共建筑并鼓励其儿子效仿；该人未被识别。",
        "quote": "the public buildings collapsing, and the Procurator occupied in rebuilding them and encouraging his own sons to copy him",
    },
    {
        "file": SOURCE_15,
        "location": "第15章，印刷页367，来源转录 L32",
        "span": "line 32; print p. 367",
        "summary": "Haskell称 Memmo 于1787年返威尼斯就任该职位，任命发生在两年前。",
        "quote": "In 1787 he returned to Venice to take up the post of Procuratore di San Marco to which he had been appointed two years earlier.",
    },
]


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p258 = f"[第9章 p.258](../../../{SOURCE_9}#L186)"
    p259 = f"[第9章 p.259](../../../{SOURCE_9}#L193)"
    p326 = f"[第10章 p.326](../../../{SOURCE_10}#L211)"
    p327 = f"[第10章 p.327](../../../{SOURCE_10}#L225)"
    p367 = f"[第15章 p.367](../../../{SOURCE_15}#L128)"
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Haskell 在威尼斯政治叙述中使用的 Procuratore di San Marco 职位称谓。书中将其作为职位或职务来叙述：Marco Foscarini 自1741年起担任该职，Pietro Foscarini 也被称为 Procuratore；Haskell称 Pisani 于1780年当选，Andrea Memmo 则于1787年返威尼斯就任其两年前获任命的职位。第10章另提及一幅政治图像中的未具名 Procurator。此卡只界定书中所指的职位术语，不补写其制度职能、任职规则或上述任职记载的外部核验，也不把图像人物等同于 Pisani 或其他已知人物。{p258}；{p259}；{p326}；{p327}；{p367}

**English:** This card records the office title *Procuratore di San Marco* as Haskell uses it in his account of Venetian politics. The book treats it as an office or post: Marco Foscarini held it from 1741, and Pietro Foscarini is also called a Procuratore; Haskell says Pisani was elected in 1780, while Andrea Memmo returned to Venice to take up the post in 1787 after having been appointed two years earlier. Chapter 10 also mentions an unnamed Procurator in a political picture. This card identifies only the office term used in the book. It does not supply the office’s institutional functions or appointment rules, independently verify the reported tenures, or identify the figure in the picture with Pisani or any other known person. {p258}; {p259}; {p326}; {p327}; {p367}

### 名称与范围

书内意大利语称谓为 *Procuratore di San Marco*。本卡按 S3 候选类型记录为职位术语；它不等同于任职人物、任职事件或威尼斯机构本身。相关书内用例见 {p258}、{p259} 和 {p326}。

### 书内用例

- Haskell 将 Marco Foscarini 自1741年起的任职与其后短暂担任 Doge 分别叙述。{p258}
- Haskell 将 Pietro Foscarini 称作 Procuratore di San Marco；此处的 Pietro 与 Marco Foscarini 是不同人物。{p259}
- Haskell 称 Pisani 于1780年当选该职位。{p326}
- 第10章 p.327 的图像叙述只称一位 Procurator，未给出其姓名；图像对象候选 `cand-9807` 仍待身份裁决。{p327}
- Haskell 称 Memmo 于1787年返威尼斯就任该职位，并明确区分两年前获任命与后来就任。{p367}

以上仅记录 Haskell 的书内表述；本卡不据职位称谓建立任职关系或身份合并。

## 关系与证据

### 关系记录

以下5条直接 S2 关系候选均留待 S6 逐条裁决；本卡不预判关系类型、方向或事实成立：{", ".join(f"`{item}`" for item in sorted(RELATION_IDS))}。
"""
    return f"---\n{fm}---\n\n{body}"


def preserve_bom_write_csv(path: Path, fieldnames, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fieldnames, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Procuratore di San Marco in S4.")
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

    source_paths = {SOURCE_9, SOURCE_10, SOURCE_15}
    source_text = {
        source: " ".join((ROOT / source).read_text(encoding="utf-8-sig").split())
        for source in source_paths
    }
    for item in SOURCES:
        assert " ".join(item["quote"].split()) in source_text[item["file"]], item["span"]

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
        + f" S4 registration: mapped {GROUP} to {KU_ID}; source usage identifies an office term only, without an inferred office structure or an identity for the unnamed Procurator in the p.327 image."
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
        "\n\n### S4 term：圣马可 Procuratore 职位（2026-10-20）\n\n"
        f"`{CANDIDATE}`沿用既有S3 `new`组 `{GROUP}`，登记至[圣马可 Procuratore 职位卡](../units/terms/procuratore-di-san-marco-office.md)。"
        "第9、10、15章分别称 Marco Foscarini、Pietro Foscarini、Pisani 与 Memmo 曾担任、当选或就任该职位；"
        "第10章 p.327 的政治图像只称一位未具名 Procurator，未据此识别其身份。五条直接 S2 关系候选留待 S6；"
        "未新增正式关系、外部身份或 S5 字段。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])}组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])}条映射；"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射。"
    )
    result_text = result_text.rstrip() + result_entry + "\n"

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text = s4_helpers.refresh_knowledge_table(process_text, stats)
    process_entry = (
        "\n\n<a id=\"" + PROCESS_ANCHOR + "\"></a>\n\n"
        "### S4 term：圣马可 Procuratore 职位（2026-10-20）\n\n"
        f"`{CANDIDATE}`沿用S3 `new`术语组 `{GROUP}`，登记为[圣马可 Procuratore 职位卡](../../../{CARD_REL})。"
        "类型依据为候选表和S3身份裁决；第9章 p.258、p.259以及第10章 p.326、p.327和第15章 p.367提供跨章书内用例。"
        "Haskell分别报告 Marco Foscarini自1741年任职、Pietro Foscarini的职位称谓、Pisani于1780年当选、"
        "图像中未具名Procurator，以及Memmo于1787年就任且早两年获任命。本卡将对象范围限于职位术语，"
        "不补写制度职能或任命规则，不把图像人物映射到已知人物；以上未作外部核验。"
        f"5条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）仍待 S6；本批不登记 formal 关系或 S5 字段。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}组／{result_sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射；"
        f"直接端点队列由{before_queue['groups']}组／{before_queue['members']}成员降至{direct_queue['groups']}组／{direct_queue['members']}成员。"
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
        print(f"source anchors=5 chapters/pages; direct S2 relation candidates={len(relation_ids)}; no formal edge created")
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
