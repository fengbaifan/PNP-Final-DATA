from __future__ import annotations

import argparse
import json
import re
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
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
CANDIDATE = "cand-0171"
EXISTING_SAME = "cand-3846"
KU_ID = "units/persons/niccolo-bambini"
CARD_REL = f"04-knowledge/{KU_ID}.md"
GROUP = "new-person:bambini-niccolo-d2c7887763"
ANCHOR = "s3-bambini-existing-ku-20261017"
RELATION_IDS = {
    "st-chp9-p247-bambini-frescoes",
    "st-chp9-p252-bambini-painted-library-frescoes",
    "st-chp9-p252-vendramin-cycle-attributed-to-bambini",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct the S3 identity of Niccolò Bambini to the accepted person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    manifest_row = next(row for row in manifest if row.get("ku_id") == KU_ID)
    card_path = ROOT / CARD_REL
    card = card_path.read_text(encoding="utf-8-sig")
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))

    assert candidate_by_id[CANDIDATE]["suggested_type"] == "person"
    assert candidate_by_id[CANDIDATE]["canonical_name"] == "Bambini, Niccolò"
    assert decisions[CANDIDATE]["decision"] == "new" and not decisions[CANDIDATE].get("ku_id")
    assert sync.get_group(decisions[CANDIDATE].get("resolution_note", "")) == GROUP
    assert decisions[EXISTING_SAME]["decision"] == "same" and decisions[EXISTING_SAME]["ku_id"] == KU_ID
    assert manifest_row["type"] == "person" and manifest_row["name_en"] == "Nicolò Bambini"
    assert CARD_REL in accepted and card_frontmatter["type"] == "person"
    assert card_frontmatter["name_en"] == "Nicolò Bambini"

    body = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    index_bytes = (ROOT / "02-sources/03-Index/03-2-Index-CSV/B.csv").read_bytes()
    try:
        index = index_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        index = index_bytes.decode("cp1252")
    plate_list = (ROOT / "02-sources/02-Markdown/00_05_List_of_Plates.md").read_text(encoding="utf-8-sig")
    assert "commissioned from Niccolo\nBambini a ceiling painting" in body
    assert "decorated with frescoes by Niccolo Bambini" in body
    assert "These have been attributed to Niccolo Bambini" in body
    assert '"Bambini, Niccolò",,,,"247, 249, 251, 252, 270"' in index
    assert "Niccolo Bambini: Allegory of Venice (Ca’ Pesaro, Venice)" in plate_list

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct == RELATION_IDS

    planned_alignments = [dict(row) for row in alignments]
    decision = next(row for row in planned_alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    decision["decision"] = "same"
    decision["ku_id"] = KU_ID
    decision["process_ref"] = "S3-full-book-2026-10-17"
    decision["resolution_note"] += (
        f" S3复核（{DATE}）：撤回 new 组 {GROUP}，改为 same → {KU_ID}。本候选书后索引 B.csv#18 的定位页"
        "247、249、251、252、270与第9章多处 Bambini 提及相符；p.252 正文明确写 Niccolo Bambini，"
        "与现有卡来源所载图版42b签名及既有 cand-3846 same 映射相互印证。Nicolò/Niccolò 为来源拼写差异，"
        "不拆为不同人物。原 new 组及旧理由保留在本行供追溯；不得重复登记 KU。三条直接 S2 关系候选仍待 S6。"
    )

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Niccolò Bambini 既有身份复核（{DATE}）\n\n"
        f"- {CANDIDATE} 原先列为 new 组 {GROUP}；复核后改为 same → [{KU_ID}](../../../{CARD_REL})。"
        "已有 Bambini 人物卡在 accepted.yml 与 ku-manifest.csv 中均为有效 person KU；第9章正文 p.249、p.252 的"
        "Niccolo Bambini 提及、索引 B.csv#18 的五组页码、图版42b来源及既有 cand-3846 same 决定共同指向同一人物。"
        "现行卡采用 Nicolò Bambini，书内索引作 Niccolò、正文多作 Niccolo；这些拼写差异保留，不生成重复卡。\n"
        f"- 三条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）仍待 S6；本次不改变关系表、卡片或补足字段。"
        f"\n- S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个 KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组；S4 已登记"
        f"{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条，待登记"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert count == 1
    result_text += (
        f"\n\n### S3 person：Niccolò Bambini 既有身份复核（{DATE}）\n\n"
        f"{CANDIDATE} 原 new 组改为 same → [{KU_ID}](../units/persons/niccolo-bambini.md)。正文、索引、图版42b及既有同人候选"
        "互相印证；原 new 组及旧理由保留在 alignment 中，未重复登记 KU。三条直接关系候选留待 S6。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} new->{KU_ID} same; direct_relation_candidates={len(direct)}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; "
            f"new={totals['new_candidates']}/{totals['new_groups']}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE} same->{KU_ID}; manifest unchanged at {len(manifest)} KU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
