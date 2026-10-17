from __future__ import annotations

import argparse
import json
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

TARGET_IDS = ("cand-0821", "cand-2780")
EXISTING_SAME_ID = "cand-3233"
IDENTITY_GROUP = "sg3-institution-virtuosi-al-pantheon"
KU_ID = "units/institutions/accademia-dei-virtuosi-al-pantheon"
CARD_REL = "04-knowledge/units/institutions/accademia-dei-virtuosi-al-pantheon.md"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
OFFICIAL_HISTORY = "https://www.accademiavirtuosi.it/storia"
MARKER = "### S3 institution：Congregazione dei Virtuosi 复用既有万神殿 Virtuosi 学院（2026-10-16）"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile Haskell's Congregazione dei Virtuosi and index aliases to the accepted Pantheon academy KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    card_path = ROOT / CARD_REL
    card_text = card_path.read_text(encoding="utf-8-sig")

    assert CARD_REL in accepted and card_path.exists()
    assert "1542" in card_text and "1543" in card_text and "Compagnia" in card_text and "Q610627" in card_text
    existing_rows = [r for r in manifest if r.get("ku_id") == KU_ID]
    assert len(existing_rows) == 1
    same_row = existing_rows[0]
    assert same_row.get("type") == "institution" and same_row.get("card_path") == CARD_REL

    expected = {
        "cand-0821": ("C.csv#351", "Congregazione dei Virtuosi", "new"),
        "cand-2780": ("UVWXYZ.csv#116", "Virtuosi, Congregazione dei", "undecided"),
    }
    previous_rows = {}
    for cid, (index_id, name, decision) in expected.items():
        candidate = candidate_by_id[cid]
        assert candidate.get("suggested_type") == "institution"
        assert candidate.get("index_entry_id") == index_id
        assert candidate.get("canonical_name") == name
        assert candidate.get("index_page_range") == "126"
        row = decisions[cid]
        assert row.get("decision") == decision and not row.get("ku_id")
        previous_rows[cid] = row

    existing_alias = decisions[EXISTING_SAME_ID]
    assert existing_alias.get("decision") == "same" and existing_alias.get("ku_id") == KU_ID
    existing_candidate = candidate_by_id[EXISTING_SAME_ID]
    assert existing_candidate.get("candidate_source_ref") == CARD_REL

    source = ROOT / SOURCE_FILE
    source_text = " ".join(source.read_text(encoding="utf-8-sig").split())
    for quote in (
        "Congregazione dei Virtuosi",
        "confraternity consisting largely of artists",
        "which had been founded in 1543",
        "Congregazione dei Virtuosi and of the Accademia di S. Luca",
    ):
        assert quote in source_text, quote

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == "cand-0821" or row.get("object_candidate_id") == "cand-0821"
    ]
    relation_rows = [
        row for row in direct
        if row.get("qualifiers", {}).get("relation_candidate") is True
    ]
    assert len(direct) == 11 and len(relation_rows) == 7
    assert all(row.get("segment_id") == "chp-5:05_CHP-5_sec_i:l60-74" for row in direct)
    assert MARKER not in process_text and MARKER not in result_text

    planned = [dict(row) for row in alignments]
    for cid in TARGET_IDS:
        target = next(
            row for row in planned
            if row.get("candidate_id") == cid and not row.get("external_source")
        )
        previous_note = target["resolution_note"]
        previous_process_ref = target["process_ref"]
        target["decision"] = "same"
        target["ku_id"] = KU_ID
        target["process_ref"] = "S3-cross-chapter-institution-reuse-2026-10-16"
        target["resolution_note"] = (
            f"group={IDENTITY_GROUP}; source_ref={expected[cid][0]} p.126; existing_ku={CARD_REL}; "
            "S3 cross-chapter institution correction 2026-10-16: same -> " + KU_ID + ". "
            "Haskell ch.5 p.126 identifies the Pantheon Congregazione dei Virtuosi as an artist confraternity; "
            "the accepted same-type Pantheon Virtuosi institution card and its official history describe the same Roman body, "
            "founded at the Pantheon, originally called Compagnia, later described as a Congregazione and elevated to Academy. "
            f"Official history: {OFFICIAL_HISTORY} (accessed 2026-10-16; history paragraphs on 1542 foundation, 1543 social activity, "
            "the Congregazione and the later Academy status). The book's 1543 foundation wording and the official 1542 foundation / "
            "1543 activity dates remain a source-level date distinction for later content review, not evidence of two institutions. "
            "The reverse index form at the same p.126 is an alias lead to this anchored institution; cand-3233 already maps to the same KU. "
            f"prior_decision={expected[cid][2]}; prior_group={result_sync.get_group(previous_note)}; prior_process_ref={previous_process_ref}; "
            f"prior_resolution_note={previous_note}"
        )

    stats = result_sync.summarize_by_type(candidates, planned)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    updated_result = result_sync.update_result(result_text, stats, totals, len(manifest))
    process_note = (
        f"\n\n{MARKER}\n\n"
        f"`cand-0821`（C.csv#351）原裁为 new，`cand-2780`（UVWXYZ.csv#116）原为 undecided；现均映射至既有[万神殿 Virtuosi 学院机构卡](../../../04-knowledge/units/institutions/accademia-dei-virtuosi-al-pantheon.md)，与已 same 的 `cand-3233` 汇合到 `{KU_ID}`。"
        "第5章 p.126 将 Congregazione dei Virtuosi 描述为主要由艺术家组成、1543年成立的 confraternity；同页记 Velasquez 为该团体成员。既有机构卡的官方历史页（"
        f"[机构历史](<{OFFICIAL_HISTORY}>)，2026-10-16访问）说明该 Pantheon 团体1542年创立、原称 Compagnia、1543年开始社会活动，并在后续沿革中称为 Congregazione、最终升格为学院。地点、团体称谓、历史职能及成员证据表明是同一连续机构，不另建新 institution。"
        "官方叙述的1542年创立与 Haskell 的1543年成立表述并列保留；官方页面将1543年说明为社会活动开始，日期表述差异属于后续内容核读事项，不拆分身份。"
        "`cand-2780` 是同页反序索引项，无独立正文锚点；其名称和页码与正文锚定的 `cand-0821` 完全对应，故复用同一 KU。普通词义的 `cand-5499` 与第3章未具名群体 `cand-11605` 均保持边界，不并入本机构。"
        f"11条直接 S2 陈述中的7条关系候选仍留待 S6；本次不修改原书陈述、不新增关系或 KU。S3 现为 same={result_sync.fmt(totals['same_candidates'])}（{result_sync.fmt(totals['same_kus'])}个既有 KU）、new={result_sync.fmt(totals['new_candidates'])}（{result_sync.fmt(totals['new_groups'])}组）、conflict={result_sync.fmt(totals['conflict'])}、excluded={result_sync.fmt(totals['excluded'])}、undecided={result_sync.fmt(totals['undecided'])}；S4 已登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。原决定及理由保存在 alignment。"
    )
    result_note = (
        "\n\n### institution：Congregazione dei Virtuosi 复用既有万神殿 Virtuosi 学院（2026-10-16）\n\n"
        f"`cand-0821` 与反序索引项 `cand-2780` 改为 same，映射至[既有机构卡](../units/institutions/accademia-dei-virtuosi-al-pantheon.md)；`cand-3233` 已指向同一 KU。依据为第5章 p.126 的名称、Pantheon语境和成员记载，以及机构官方历史所述的名称沿革和1542/1543时间区分。"
        "Haskell与官方网页的成立年份表述保留为后续内容级核对事项，不据此拆分机构身份；相关关系候选仍留待 S6。"
        f"当前 S3 same={result_sync.fmt(totals['same_candidates'])}（{result_sync.fmt(totals['same_kus'])}个既有 KU）、new={result_sync.fmt(totals['new_candidates'])}（{result_sync.fmt(totals['new_groups'])}组）、undecided={result_sync.fmt(totals['undecided'])}；S4 待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条映射。"
    )
    updated_process = process_text + process_note
    updated_result += result_note

    if args.dry_run:
        print("S3 institution reuse dry-run passed: cand-0821, cand-2780 -> " + KU_ID)
        print("existing alias cand-3233 already maps to this KU; 11 direct statements, 7 relation candidates left for S6")
        print("Haskell p.126 name/member evidence and official history continuity checked; 1542/1543 wording retained as a content-level issue")
        print(
            f"S3 same={result_sync.fmt(totals['same_candidates'])}/{result_sync.fmt(totals['same_kus'])} KUs; "
            f"new={result_sync.fmt(totals['new_candidates'])}/{result_sync.fmt(totals['new_groups'])} groups; "
            f"undecided={result_sync.fmt(totals['undecided'])}; S4 pending={result_sync.fmt(totals['pending_groups'])} groups/"
            f"{result_sync.fmt(totals['pending_members'])} candidates; manifest={len(manifest):,} (unchanged)"
        )
        return 0

    result_sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(updated_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(updated_result, encoding="utf-8-sig", newline="\n")
    print("applied S3 reuse: cand-0821, cand-2780 -> " + KU_ID)
    print(
        f"same={result_sync.fmt(totals['same_candidates'])}/{result_sync.fmt(totals['same_kus'])} KUs; "
        f"new={result_sync.fmt(totals['new_candidates'])}/{result_sync.fmt(totals['new_groups'])} groups; "
        f"undecided={result_sync.fmt(totals['undecided'])}; S4 pending={result_sync.fmt(totals['pending_groups'])}/"
        f"{result_sync.fmt(totals['pending_members'])}; manifest={len(manifest):,} unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
