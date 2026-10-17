from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"

CANDIDATE = "cand-8262"
GROUP = "sg3-institution-cand-8262"
KU_ID = "units/institutions/correr-library"
CARD_REL = "04-knowledge/units/institutions/correr-library.md"
MUSEUM_KU = "units/institutions/museo-correr"
MARKER = "### S3 跨章身份复用纠偏：Biblioteca Correr 对应既有 Correr Library（2026-10-16）"


def read_csv(path):
    return card_writer.read_csv(path)


def write_csv(path, fields, rows):
    card_writer.write_csv(path, fields, rows)


def totals(rows):
    candidate_rows = [r for r in rows if r.get("candidate_id") and not r.get("external_source")]
    decisions = Counter(r["decision"] for r in candidate_rows)
    same_kus = {r["ku_id"] for r in candidate_rows if r["decision"] == "same" and r.get("ku_id")}
    new_groups = defaultdict(list)
    for row in candidate_rows:
        if row.get("decision") == "new":
            group = card_writer.get_group(row.get("resolution_note", ""))
            assert group, f"new decision lacks group: {row['candidate_id']}"
            new_groups[group].append(row)
    registered = {g: members for g, members in new_groups.items() if any(r.get("ku_id") for r in members)}
    mapped = sum(bool(r.get("ku_id")) for members in registered.values() for r in members)
    pending = [r for r in candidate_rows if r["decision"] == "new" and not r.get("ku_id")]
    return {
        "same": decisions["same"], "same_kus": len(same_kus),
        "new": decisions["new"], "new_groups": len(new_groups),
        "conflict": decisions["conflict"], "excluded": decisions["excluded"], "undecided": decisions["undecided"],
        "registered_groups": len(registered), "mapped": mapped,
        "pending_groups": len(new_groups) - len(registered), "pending_members": len(pending),
    }


def update_result(result, current):
    s3_pattern = re.compile(r"same=[\d,]+（指向[\d,]+个既有 KU）、new=[\d,]+（[\d,]+个身份组）")
    result, n = s3_pattern.subn(
        f"same={current['same']:,}（指向{current['same_kus']:,}个既有 KU）、new={current['new']:,}（{current['new_groups']:,}个身份组）",
        result,
        count=1,
    )
    assert n == 1, "could not update current S3 summary"
    s4_pattern = re.compile(r"S4 已登记\s*[\d,]+组、映射[\d,]+条成员候选；尚待登记[\d,]+组、[\d,]+条映射。")
    result, n = s4_pattern.subn(
        f"S4 已登记{current['registered_groups']:,}组、映射{current['mapped']:,}条成员候选；"
        f"尚待登记{current['pending_groups']:,}组、{current['pending_members']:,}条映射。",
        result,
        count=1,
    )
    assert n == 1, "could not update current S4 summary"
    return result


def main():
    parser = argparse.ArgumentParser(description="Map Biblioteca Correr to the existing Correr Library institution KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, manifest = read_csv(MANIFEST_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    library_manifest = next((r for r in manifest if r.get("ku_id") == KU_ID), None)
    museum_manifest = next((r for r in manifest if r.get("ku_id") == MUSEUM_KU), None)
    card_path = ROOT / CARD_REL
    accepted = (ROOT / "04-knowledge" / "accepted.yml").read_text(encoding="utf-8-sig")
    process = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result = RESULT_PATH.read_text(encoding="utf-8-sig")

    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE]["suggested_type"] == "institution"
    row = alignment_by_id[CANDIDATE]
    assert row["decision"] == "new" and not row.get("ku_id")
    assert card_writer.get_group(row["resolution_note"]) == GROUP
    group_rows = [
        r for r in alignments if r.get("candidate_id") and not r.get("external_source")
        and r["decision"] == "new" and card_writer.get_group(r.get("resolution_note", "")) == GROUP
    ]
    assert [r["candidate_id"] for r in group_rows] == [CANDIDATE]
    assert library_manifest and library_manifest["type"] == "institution" and library_manifest["card_path"] == CARD_REL
    assert museum_manifest and museum_manifest["type"] == "institution" and MUSEUM_KU != KU_ID
    assert card_path.exists() and CARD_REL in accepted
    assert "Correr Library" in card_path.read_text(encoding="utf-8-sig")

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    direct = [r for r in statements if r.get("subject_candidate_id") == CANDIDATE or r.get("object_candidate_id") == CANDIDATE]
    relation_rows = [r for r in direct if (r.get("qualifiers") or {}).get("relation_candidate") is True]
    assert len(direct) == 15, f"unexpected direct statement count: {len(direct)}"
    assert len(relation_rows) == 15, f"unexpected relation candidate count: {len(relation_rows)}"

    source_checks = (
        ("09_CHP-9_intro.md", "the Biblioteca Correr—MSS. P.D. C2193/I"),
        ("16_CHP-16_intro.md", "Biblioteca Correr, Venice—MSS. Raccolta Cicogna 3006/9"),
        ("17_CHP-17_sec_i.md", "in the Biblioteca Correr: Cod. Cicogna 3007/XIII"),
    )
    for file_name, quote in source_checks:
        source = ROOT / "02-sources" / "02-Markdown" / file_name
        source_text = " ".join(source.read_text(encoding="utf-8-sig").split())
        assert " ".join(quote.split()) in source_text, (file_name, quote)

    planned = [dict(r) for r in alignments]
    target = next(r for r in planned if r.get("candidate_id") == CANDIDATE and not r.get("external_source"))
    previous_note = target["resolution_note"]
    target["decision"] = "same"
    target["ku_id"] = KU_ID
    target["process_ref"] = "S3-cross-chapter-institution-reuse-2026-10-16"
    target["resolution_note"] = (
        f"source_ref={candidate_by_id[CANDIDATE]['candidate_source_ref']}; existing_ku={CARD_REL}; "
        f"S3 cross-chapter institution correction 2026-10-16: same -> {KU_ID}. "
        "Across Chapters 9, 16, and 17 the book uses Biblioteca Correr as a repository locator; "
        "the accepted Correr Library card records the same library, its Venice location, manuscripts and archival holdings, "
        "and cites the official Museo Correr library description. Map to the library, not to the distinct parent museum "
        f"{MUSEUM_KU}; specific manuscripts, inventories, and printed sources remain archive candidates. "
        f"prior_decision=new; prior_group={GROUP}; prior_resolution_note={previous_note}"
    )
    current = totals(planned)
    updated_result = update_result(result, current)
    assert MARKER not in process and MARKER not in updated_result
    process_note = (
        f"\n\n{MARKER}\n\n"
        f"`{CANDIDATE}` 原裁为新 institution 组 `{GROUP}`；现映射至既有[科雷尔图书馆机构卡]"
        "(../../../04-knowledge/units/institutions/correr-library.md)。"
        "第9章关于 Sagredo 资料及 Longhi inventory 的注释、第16章 Cicogna 手稿定位、第17章 Manfrin 目录与书信注释，"
        "均以 Biblioteca Correr 指称该图书馆。既有卡片以 Correr Library 为英文名称，来源包括本书第一版序言及馆方 Library 页面。"
        f"映射不指向父机构 Museo Correr（{MUSEUM_KU}）；各被引手稿、目录和书信仍按 archive 对象分别处理。"
        f"15条直接 S2 陈述全部为关系候选，留待 S6。S3 现为 same={current['same']:,}（{current['same_kus']:,}个既有 KU）、"
        f"new={current['new']:,}（{current['new_groups']:,}组）、conflict={current['conflict']}、excluded={current['excluded']}、"
        f"undecided={current['undecided']:,}；S4 已登记{current['registered_groups']:,}组/{current['mapped']:,}条映射，"
        f"待登记{current['pending_groups']:,}组/{current['pending_members']:,}条。原 new 理由保留于 alignment。"
    )
    result_note = (
        "\n\n### institution：Biblioteca Correr 复用既有 Correr Library（2026-10-16）\n\n"
        f"`{CANDIDATE}` 改为 same 并映射至[科雷尔图书馆](../units/institutions/correr-library.md)，不映射至父机构 Museo Correr。"
        "该书第9、16、17章均以 Biblioteca Correr 定位文献；各具体文献仍是独立 archive 候选，15条关系候选留待 S6。"
        f"当前 S3 same={current['same']:,}（{current['same_kus']:,}个既有 KU）、new={current['new']:,}（{current['new_groups']:,}组）；"
        f"S4 已登记{current['registered_groups']:,}组/{current['mapped']:,}条映射，待登记{current['pending_groups']:,}组/{current['pending_members']:,}条。"
    )
    process += process_note
    updated_result += result_note

    if args.dry_run:
        print(f"S3 reuse dry-run passed: {CANDIDATE} -> {KU_ID}; parent museum remains separate")
        print(f"direct statements={len(direct)}; relation candidates={len(relation_rows)}; cross-chapter source quotes={len(source_checks)}")
        print(
            f"S3 same={current['same']:,}/{current['same_kus']:,} KUs; new={current['new']:,}/{current['new_groups']:,} groups; "
            f"S4 pending={current['pending_groups']:,} groups/{current['pending_members']:,} candidates"
        )
        print("library card and official source reference checked; no files changed")
        return 0

    write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(updated_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; same={current['same']:,}/{current['same_kus']:,}; "
        f"new={current['new']:,}/{current['new_groups']:,}; "
        f"S4 pending={current['pending_groups']:,}/{current['pending_members']:,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
