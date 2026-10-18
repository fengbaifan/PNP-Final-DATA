from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
CANONICAL_KU = "units/persons/marshal-schulenburg"
DUPLICATE_KU = "units/persons/johann-matthias-schulenburg"
CANONICAL_CARD = ROOT / "04-knowledge" / f"{CANONICAL_KU}.md"
DUPLICATE_CARD = ROOT / "04-knowledge" / f"{DUPLICATE_KU}.md"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s3-schulenburg-duplicate-ku-reconciliation-20261018"
MAIN_CANDIDATE = "cand-2401"
OLD_GROUP = "new-person:johann-marshal-matthias-schulenburg-240303b710"
EXISTING_SAME_CANDIDATE = "cand-3835"
TARGETS = {
    "cand-2402": ("S.csv#90", "and Canaletto", "312"),
    "cand-2403": ("S.csv#91", "and Gian Antonio Guardi", "312, 313"),
    "cand-2404": ("S.csv#92", "comparison of collection with Smith's", "315"),
    "cand-2408": ("S.csv#96", "interest in contemporary Venetian sculpture", "312"),
    "cand-2414": ("S.csv#102", "taste for naturalistic and genre painting", "314"),
}
UNCHANGED_NEIGHBORS = {
    "cand-2405": ("new", "", "event"),
    "cand-2406": ("undecided", "", "work"),
    "cand-2407": ("undecided", "", "work"),
    "cand-2409": ("undecided", "", "work"),
    "cand-2410": ("undecided", "", "work"),
    "cand-2411": ("new", "", "event"),
    "cand-2412": ("undecided", "", "work"),
    "cand-2413": ("undecided", "", "event"),
}
EXPECTED_NEW_SOURCE_FILES = {
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    "02-sources/02-Markdown/09_CHP-9_intro.md",
    "02-sources/02-Markdown/20_CHP-20Postscript.md",
}


def decision_rows(alignment_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }


def read_card(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8-sig")
    assert text.startswith("---\n"), f"missing YAML frontmatter: {path}"
    end = text.index("\n---\n", 4)
    metadata = yaml.safe_load(text[4:end])
    return metadata, text[end + 5 :]


def render_card(metadata: dict, body: str) -> str:
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{frontmatter}---\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge the duplicate S4 Schulenburg person KU and reuse the existing canonical person KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    by_id = decision_rows(alignments)
    assert len(by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    manifest_by_ku = {row["ku_id"]: row for row in manifest}

    assert CANONICAL_KU in manifest_by_ku and manifest_by_ku[CANONICAL_KU]["type"] == "person"
    assert manifest_by_ku[CANONICAL_KU]["name_en"] == "Johann Matthias von der Schulenburg"
    assert DUPLICATE_KU in manifest_by_ku and manifest_by_ku[DUPLICATE_KU]["type"] == "person"
    assert manifest_by_ku[DUPLICATE_KU]["name_en"] == "Johann Matthias Schulenburg"
    main_candidate = candidate_by_id[MAIN_CANDIDATE]
    main_alignment = by_id[MAIN_CANDIDATE]
    assert main_candidate["suggested_type"] == "person"
    assert main_candidate["index_entry_id"] == "S.csv#89"
    assert main_candidate["canonical_name"] == "Schulenburg, Marshal Johann Matthias"
    assert main_alignment["decision"] == "new" and main_alignment["ku_id"] == DUPLICATE_KU
    assert sync.get_group(main_alignment["resolution_note"]) == OLD_GROUP
    old_group_members = {
        cid for cid, row in by_id.items()
        if row["decision"] == "new" and sync.get_group(row.get("resolution_note", "")) == OLD_GROUP
    }
    assert old_group_members == {MAIN_CANDIDATE}

    same_candidate = candidate_by_id[EXISTING_SAME_CANDIDATE]
    same_alignment = by_id[EXISTING_SAME_CANDIDATE]
    assert same_candidate["suggested_type"] == "person"
    assert same_alignment["decision"] == "same" and same_alignment["ku_id"] == CANONICAL_KU

    same_headword_ids = {
        row["candidate_id"] for row in candidates
        if row["canonical_name"] == main_candidate["canonical_name"]
        and row["suggested_type"] == "person"
        and row["index_source_file"] == "S.csv"
    }
    assert same_headword_ids == {MAIN_CANDIDATE} | set(TARGETS)
    for cid, (index_entry, sub_entry, pages) in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["index_entry_id"] == index_entry
        assert candidate["canonical_name"] == main_candidate["canonical_name"]
        assert candidate["sub_entry"] == sub_entry
        assert candidate["index_page_range"] == pages
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert "index-seeded candidate has no mapped S2 mention" in alignment["resolution_note"]

    for cid, (decision, ku_id, kind) in UNCHANGED_NEIGHBORS.items():
        assert candidate_by_id[cid]["suggested_type"] == kind
        assert (by_id[cid]["decision"], by_id[cid]["ku_id"]) == (decision, ku_id)

    canonical_metadata, canonical_body = read_card(CANONICAL_CARD)
    duplicate_metadata, _ = read_card(DUPLICATE_CARD)
    assert canonical_metadata["name_en"] == "Johann Matthias von der Schulenburg"
    assert duplicate_metadata["name_en"] == "Johann Matthias Schulenburg"
    duplicate_sources = duplicate_metadata.get("sources", [])
    duplicate_source_files = {row["evidence_ref"]["source_file"] for row in duplicate_sources}
    assert duplicate_source_files == EXPECTED_NEW_SOURCE_FILES
    assert len(duplicate_sources) == 3

    relation_rows = sync.read_csv(TABLES / "relations.csv")[1]
    assert not any(
        row.get("subject_ku_id") == DUPLICATE_KU or row.get("object_ku_id") == DUPLICATE_KU
        for row in relation_rows
    ), "formal relations already target the canonical KU; unexpected duplicate-KU relation found"
    enrichment_rows = [
        json.loads(line)
        for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    assert not any(row.get("ku_id") == DUPLICATE_KU for row in enrichment_rows)

    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = decision_rows(planned_alignments)
    for cid in {MAIN_CANDIDATE} | set(TARGETS):
        row = planned_by_id[cid]
        previous_decision = row["decision"]
        row["decision"] = "same"
        row["ku_id"] = CANONICAL_KU
        row["process_ref"] = f"{TASK}#{ANCHOR}"
        if cid == MAIN_CANDIDATE:
            row["resolution_note"] += (
                f" S3跨章复核（{DATE}）：撤回原new组{OLD_GROUP}，原S4登记与新卡路径保留为历史。"
                "第10章p.311的全名Johann Matthias Schulenburg与前言图版、SIRBeC所用全名"
                "Johann Matthias von der Schulenburg指向同一人：Haskell同段记其萨克森家族出身和1661年出生，"
                "与既有KU的1661–1747、威尼斯军职记录相合；第9章p.267和第20章p.407的收藏语境亦连续。"
                f"既有候选{EXISTING_SAME_CANDIDATE}已same至{CANONICAL_KU}。因此cand-2401由{previous_decision}改为"
                f"same → {CANONICAL_KU}。原重复卡的书内来源已并入既有人物卡，重复manifest/accepted登记与卡文件已合并撤下；"
                "formal relations原已指向既有KU，本次未改关系端点。"
            )
        else:
            index_entry, sub_entry, pages = TARGETS[cid]
            row["resolution_note"] += (
                f" S3复核（{DATE}）：原undecided理由保留为历史；{index_entry}是人物主项"
                f"“Schulenburg, Marshal Johann Matthias”（S.csv#89）下的person型子目“{sub_entry}”，"
                f"印刷页码为{pages}。主项cand-2401已same至规范人物KU {CANONICAL_KU}；"
                "第10章p.311全名与第9章p.267、第20章p.407的同书跨章语境相符。"
                f"该子目仍指主项人物，故改判same → {CANONICAL_KU}。Canaletto、Gian Antonio Guardi、"
                "Joseph Smith及艺术、收藏措辞保留为索引定位，不据此合并其他人物或新建正式关系。"
            )

    for before, after in zip(alignments, planned_alignments):
        if before.get("candidate_id") not in ({MAIN_CANDIDATE} | set(TARGETS)):
            assert before == after, f"unexpected alignment change: {before.get('candidate_id')}"

    planned_manifest = [dict(row) for row in manifest if row["ku_id"] != DUPLICATE_KU]
    assert len(manifest) - len(planned_manifest) == 1
    assert not any(row["ku_id"] == DUPLICATE_KU for row in planned_manifest)
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    duplicate_accepted_line = f"- 04-knowledge/{DUPLICATE_KU}.md"
    assert accepted_text.count(duplicate_accepted_line) == 1
    planned_accepted_text = accepted_text.replace(duplicate_accepted_line + "\n", "", 1)

    planned_metadata = dict(canonical_metadata)
    existing_sources = planned_metadata.get("sources", [])
    existing_source_keys = {
        (row.get("evidence_ref", {}).get("source_file"), row.get("evidence_ref", {}).get("source_span"))
        for row in existing_sources
    }
    additions = [
        row for row in duplicate_sources
        if (row["evidence_ref"]["source_file"], row["evidence_ref"]["source_span"]) not in existing_source_keys
    ]
    assert len(additions) == 3
    planned_metadata["sources"] = existing_sources + additions
    planned_metadata["updated"] = DATE
    planned_metadata["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

    context_zh = (
        "### 本书语境\n\n"
        "第10章以 Johann Matthias Schulenburg 全名识别此人，称其出身萨克森家族、1661年出生；第9章记其购入"
        "包含多幅 Castiglione 作品的一批藏画；第20章后记回顾其收藏研究。以上为 Haskell 的书内叙述。\n\n"
        "**English:** Chapter 10 names Johann Matthias Schulenburg and says he came from a Saxon family and was born in 1661. "
        "Chapter 9 reports his purchase of a group that included several works by Castiglione; the Chapter 20 postscript "
        "reviews scholarship on his collection. These remain Haskell's reports.\n\n"
    )
    old_english_description = (
        "**English:** A field marshal in Venetian service, collector and patron who employed Piazzetta for artistic commissions and collection assessment.\n\n"
    )
    assert canonical_body.count(old_english_description) == 1
    planned_body = canonical_body.replace(
        old_english_description,
        old_english_description + context_zh,
        1,
    )
    identity_boundary = (
        "### 身份边界\n\n"
        "中文：第10章的书内形式“Johann Matthias Schulenburg”与前言图版及既有人物记录采用的"
        "“Johann Matthias von der Schulenburg”归为同一人；S.csv#89主项及其人物子目指向此人。"
        "第10章p.311暂依索引定位，OCR页标异常仍待页图核对。第9章p.267与第20章p.407提供跨章收藏语境。"
        "这些书内陈述不替代外部核验，购买、赞助及艺术往来仍按既有证据状态保留。\n\n"
        "English: Chapter 10's form “Johann Matthias Schulenburg” and the “Johann Matthias von der Schulenburg” form "
        "used in the plate list and existing person record refer to the same person; the S.csv#89 index headword and "
        "its person subentries point to him. The Chapter 10 p. 311 locator follows the index provisionally, and its OCR "
        "page marker still awaits image review. Chapter 9 (p. 267) and Chapter 20 (p. 407) provide further collection context. "
        "These book statements do not replace external verification; claims about purchases, patronage, and artistic dealings "
        "retain their existing evidence status.\n\n"
    )
    assert planned_body.count("## 关系与证据\n") == 1
    planned_body = planned_body.replace("## 关系与证据\n", identity_boundary + "## 关系与证据\n", 1)
    planned_canonical_card = render_card(planned_metadata, planned_body)

    before = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(item[key] for item in before.values()) for key in next(iter(before.values()))}
    assert totals["same_candidates"] == before_totals["same_candidates"] + 1 + len(TARGETS)
    assert totals["new_candidates"] == before_totals["new_candidates"] - 1
    assert totals["new_groups"] == before_totals["new_groups"] - 1
    assert totals["registered_groups"] == before_totals["registered_groups"] - 1
    assert totals["registered_members"] == before_totals["registered_members"] - 1
    assert totals["same_kus"] == before_totals["same_kus"]
    assert totals["undecided"] == before_totals["undecided"] - len(TARGETS)
    for key in ("pending_groups", "pending_members", "conflict", "excluded", "total"):
        assert totals[key] == before_totals[key]
    assert stats["person"]["same_candidates"] == before["person"]["same_candidates"] + 1 + len(TARGETS)
    assert stats["person"]["same_kus"] == before["person"]["same_kus"]
    assert stats["person"]["undecided"] == before["person"]["undecided"] - len(TARGETS)

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Schulenburg跨章身份复核并复用既有人物KU（{DATE}）\n\n"
        "- cand-2401（S.csv#89）原为new并于S4登记成独立卡；现改为same → "
        f"[{CANONICAL_KU}](../../../04-knowledge/{CANONICAL_KU}.md)。第10章p.311明确写作Johann Matthias Schulenburg，"
        "同段称其出身萨克森家族、1661年出生；既有KU采用带“von der”的形式，前言图版及SIRBeC条目均指向"
        "1661–1747年的威尼斯军人和收藏者。第9章p.267、 第20章p.407与图版53a提供连续书内／馆藏语境；"
        f"既有cand-3835已same至同一KU。旧new组{OLD_GROUP}及S4登记作为历史保留；其重复卡内容并入既有人物卡，"
        "重复manifest与accepted记录及重复卡文件移除。\n"
        "- cand-2402（S.csv#90，and Canaletto，p.312）、cand-2403（#91，and Gian Antonio Guardi，pp.312–313）、"
        "cand-2404（#92，comparison of collection with Smith's，p.315）、cand-2408（#96，interest in contemporary Venetian sculpture，p.312）"
        "与cand-2414（#102，taste for naturalistic and genre painting，p.314）均由undecided改判same，映射至同一既有人物KU。"
        "子目只是人物索引定位；不把Canaletto、Guardi或Joseph Smith并入Schulenburg，也不由子目建立正式关系。\n"
        "- 相邻事件cand-2405、cand-2411、cand-2413及作品cand-2406、cand-2407、cand-2409、cand-2410、cand-2412保持原类型与决定。"
        "现有五条formal relations继续指向规范人物KU；本批未更改关系表。\n"
        f"- 更新后S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，"
        f"undecided={sync.fmt(totals['undecided'])}；S4已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条、待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU={len(planned_manifest)}。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text += (
        f"\n\n### S3 person：Schulenburg跨章同一性与重复KU合并（{DATE}）\n\n"
        "cand-2401及五条人物索引子目均映射至既有人物KU；其重复S4卡已合并来源后撤下，原正式关系端点保持不变。"
        f"详情见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})及alignment.csv。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: same additions={1 + len(TARGETS)}->{CANONICAL_KU}; "
            f"retired_new_group={OLD_GROUP}; same={totals['same_candidates']}/{totals['same_kus']}; "
            f"new_groups={totals['new_groups']}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"undecided={totals['undecided']}; merged_sources={len(additions)}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; accepted duplicate removed; relations_unchanged=5"
        )
        return 0

    CANONICAL_CARD.write_text(planned_canonical_card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text(planned_accepted_text, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    DUPLICATE_CARD.unlink()
    print(
        f"applied: same additions={1 + len(TARGETS)}->{CANONICAL_KU}; "
        f"same={totals['same_candidates']}/{totals['same_kus']}; "
        f"new_groups={totals['new_groups']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
