from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import register_s4_archive_memmo_query_sheet_20261017 as previous


sync = previous.sync
ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
SOURCE_GROUP = "archive-group-b3cea361eaf4"
TARGET_GROUP = "archive-group-5b4568c2a1c8"
COLLECTION_CANDIDATE = "cand-8533"
BIBLIOGRAPHY_CANDIDATE = "cand-11374"
PROCESS_ANCHOR = "s3-levi-inventory-publication-merge-20261017"

QUOTES = (
    ("02-sources/02-Markdown/09_CHP-9_intro.md",
     "A number of Venetian inventories of the eighteenth century are included in C. A. Levi’s collection of 1900."),
    ("02-sources/02-Markdown/15_CHP-15_sec_ii.md",
     "part of which Is published by Levi, II, p. 254."),
    ("02-sources/02-Markdown/15_CHP-15_sec_ii.md",
     "A very unclassified inventory of Angelo Querini’s effects at Alticchiero is published by Levi, II, p. 255."),
    ("02-sources/02-Markdown/19_CHP-19Appendix.md",
     "Archivio di Stato-Petizion 467 by C. A. Levi, II, pp. 236-48."),
    ("02-sources/02-Markdown/21_CHP-21Bibliography.md",
     "Levi, C. A.: Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni,\nVenezia 1900."),
)


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the 1900 Levi collection citation with its full bibliographic entry in S3"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert COLLECTION_CANDIDATE in candidate_by_id and BIBLIOGRAPHY_CANDIDATE in candidate_by_id
    assert candidate_by_id[COLLECTION_CANDIDATE]["suggested_type"] == "archive"
    assert candidate_by_id[BIBLIOGRAPHY_CANDIDATE]["suggested_type"] == "archive"
    assert alignment_by_id[COLLECTION_CANDIDATE]["decision"] == "new"
    assert not alignment_by_id[COLLECTION_CANDIDATE].get("ku_id")
    collection_group = group_of(alignment_by_id[COLLECTION_CANDIDATE]["resolution_note"])
    assert collection_group in {SOURCE_GROUP, TARGET_GROUP}
    assert alignment_by_id[BIBLIOGRAPHY_CANDIDATE]["decision"] == "new"
    assert not alignment_by_id[BIBLIOGRAPHY_CANDIDATE].get("ku_id")
    assert group_of(alignment_by_id[BIBLIOGRAPHY_CANDIDATE]["resolution_note"]) == TARGET_GROUP
    source_group_members = {
        cid for cid, row in alignment_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == SOURCE_GROUP
    }
    target_group_members = {
        cid for cid, row in alignment_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == TARGET_GROUP
    }
    if collection_group == SOURCE_GROUP:
        assert source_group_members == {COLLECTION_CANDIDATE}
        assert target_group_members == {BIBLIOGRAPHY_CANDIDATE}
    else:
        assert not source_group_members
        assert target_group_members == {COLLECTION_CANDIDATE, BIBLIOGRAPHY_CANDIDATE}

    for relative, quote in QUOTES:
        text = (ROOT / relative).read_text(encoding="utf-8-sig")
        assert normalized(quote) in normalized(text), f"source evidence changed: {relative}"

    planned = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }
    if collection_group == SOURCE_GROUP:
        old_collection_note = planned_by_id[COLLECTION_CANDIDATE]["resolution_note"]
        planned_by_id[COLLECTION_CANDIDATE]["resolution_note"] = re.sub(
            rf"group={re.escape(SOURCE_GROUP)}(?=[;| ])",
            f"group={TARGET_GROUP}",
            old_collection_note,
            count=1,
        )
        planned_by_id[COLLECTION_CANDIDATE]["resolution_note"] += (
            f" S3 identity reconciliation {DATE}: same publication as {BIBLIOGRAPHY_CANDIDATE}; "
            f"prior_group={SOURCE_GROUP}; Haskell’s chapter 9 note calls it Levi’s 1900 collection, "
            "chapters 15 and 19 cite the same volume II at pp. 236–255, and chapter 21 supplies the full "
            "Le Collezioni Veneziane title and Venezia 1900 bibliography record. "
            f"Keep in group {TARGET_GROUP}; no external source consulted."
        )
        planned_by_id[BIBLIOGRAPHY_CANDIDATE]["resolution_note"] += (
            f" S3 identity reconciliation {DATE}: identity peer={COLLECTION_CANDIDATE}; "
            "chapter 9’s Levi 1900 collection and the chapter 15/19 volume II citations match this full "
            "bibliographic entry; keep both candidates in this one new archive group."
        )
    else:
        assert f"prior_group={SOURCE_GROUP}" in planned_by_id[COLLECTION_CANDIDATE]["resolution_note"]
        assert f"identity peer={COLLECTION_CANDIDATE}" in planned_by_id[BIBLIOGRAPHY_CANDIDATE]["resolution_note"]

    planned_candidates = [dict(row) for row in candidates]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}
    planned_candidate_by_id[COLLECTION_CANDIDATE]["detail"] = (
        "Identified with the full bibliographic entry Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni "
        "(Venezia 1900) at chapter 21, p. 427. Chapter 9 calls it Levi’s 1900 collection; chapters 15 and 19 cite volume II, "
        "pp. 236–255. The publication itself was not independently consulted."
    )
    planned_candidate_by_id[BIBLIOGRAPHY_CANDIDATE]["detail"] = (
        "Chapter 21, p. 427 lists the exact Italian title and Venezia 1900. In S3, the chapter 9 Levi 1900 collection "
        "and chapter 15/19 volume-II citations were grouped with this publication. Other Levi volume-I citations remain "
        "undecided; the publication itself was not independently consulted."
    )

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    collection_relations = [
        row for row in statements
        if (row.get("subject_candidate_id") == COLLECTION_CANDIDATE
            or row.get("object_candidate_id") == COLLECTION_CANDIDATE)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert len(collection_relations) == 5, len(collection_relations)

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    manifest = sync.read_csv(TABLES / "ku-manifest.csv")[1]
    next_result = sync.update_result(result_text, stats, totals, len(manifest))
    next_process = previous.refresh_process_type_table(process_text, stats)
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S3 archive：C. A. Levi 1900 年出版物跨章并组（{DATE}）\n\n"
        f"- {COLLECTION_CANDIDATE} 原列为 {SOURCE_GROUP}，{BIBLIOGRAPHY_CANDIDATE} 列为 {TARGET_GROUP}。"
        f"复核后保留两者的 new 决定，统一进入 {TARGET_GROUP}；该组含这两条候选。\n"
        "- 身份依据：第9章 p.261 注2称18世纪威尼斯库存清单收录于 C. A. Levi 的1900年汇编；"
        "第15章 p.368 注3及 p.370 注1分别引 Levi 第二卷 p.254、p.255；第19章 p.391称 Petizion 467 "
        "档案所载清单由 Levi 第二卷 pp.236–248 重刊；第21章 p.427书目给出 *Le Collezioni Veneziane "
        "d’arte e d’antichità dal secolo XIV ai nostri giorni*，Venezia 1900。题名、出版地、年份和卷次相合，"
        "支持这是同一多卷本出版物，不是各项清单或底层档案本身。\n"
        f"- 原分组 {SOURCE_GROUP} 与原 new 理由保留在 {COLLECTION_CANDIDATE} 的 alignment 注释中；"
        "仅修正身份组，不改候选数或决定类型。Levi 卷I短引 cand-10659、cand-10732 仍为 undecided；"
        "未具名清单群 cand-8531、作者 initials 人物 cand-8532、Petizion 467 清单 cand-10806 "
        "及 Querini 清单 cand-10567 保持各自身份与状态。\n"
        f"- {len(collection_relations)} 条直接关系候选仍待 S6；未新增外部身份记录、KU 或正式关系。\n\n"
        f"当前 S3 为 new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}组）；"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' not in next_process:
        next_process = next_process.rstrip() + process_append + "\n"
    result_append = (
        f"\n\n### S3 archive：C. A. Levi 1900 年出版物跨章并组（{DATE}）\n\n"
        f"{COLLECTION_CANDIDATE}（第9、15、19章引文）与 {BIBLIOGRAPHY_CANDIDATE}（第21章书目）"
        f"现同属 {TARGET_GROUP}：书目所列 *Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni* "
        "（Venezia 1900）与三章中“Levi 1900年汇编”及卷II页码引文相合。两候选均保持 S3 new，"
        "合并为一个待 S4 登记的 archive KU；未独立查阅出版物。卷I短引、未具名库存群、C. A. Levi 人物身份及"
        "具体库存清单继续保持各自的 undecided/new 状态，未并入该出版物。详见"
        f"[S3裁决过程](../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR})与[对齐表](../tables/alignment.csv)。"
    )
    if "### S3 archive：C. A. Levi 1900 年出版物跨章并组" not in next_result:
        next_result = next_result.rstrip() + result_append + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: {COLLECTION_CANDIDATE}+{BIBLIOGRAPHY_CANDIDATE} -> {TARGET_GROUP}; "
            f"collection_relation_candidates={len(collection_relations)}; "
            f"new_groups={totals['new_groups']}; S4_pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned)
    sync.write_csv(TABLES / "entity-candidates.csv", candidate_fields, planned_candidates)
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {COLLECTION_CANDIDATE}+{BIBLIOGRAPHY_CANDIDATE} -> {TARGET_GROUP}; "
        f"new_groups={totals['new_groups']}; S4_pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
