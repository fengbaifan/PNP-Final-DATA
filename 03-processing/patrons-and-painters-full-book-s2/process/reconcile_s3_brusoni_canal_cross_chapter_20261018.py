from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

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
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s3-brusoni-canal-cross-chapter-20261018"
BRUSONI_CANDIDATE = "cand-0462"
BRUSONI_KU = "units/persons/girolamo-brusoni"
CANAL_CANDIDATES = ("cand-0496", "cand-0497")
CANAL_GROUP = "new-person:canal-gerolamo-1e30c99339"
CANAL_OLD_GROUP = "new-person:canale-procuratore-0f841d72a8"
CANAL_DB_ENTRY = "https://www.treccani.it/enciclopedia/francesco-solimena_(Dizionario-Biografico)/"
RELATION_IDS = {
    "st-chp6-notes-l128-p149-n6",
    "st-chp8-p214-n4-venetian-patrons-owned-pictures",
    "st-chp10-p304-smith-country-house-lease-purchase",
}


def decision_rows(alignment_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile Brusoni's index subentry and Canal/Canale cross-chapter identity groups."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    by_id = decision_rows(alignments)
    assert len(by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"

    brusoni_candidate = candidate_by_id[BRUSONI_CANDIDATE]
    brusoni = by_id[BRUSONI_CANDIDATE]
    assert brusoni_candidate["suggested_type"] == "person"
    assert brusoni_candidate["index_entry_id"] == "B.csv#309"
    assert brusoni_candidate["canonical_name"] == "Brusoni, Girolamo"
    assert brusoni_candidate["sub_entry"] == "Allori d'Eurota"
    assert brusoni["decision"] == "undecided" and not brusoni.get("ku_id")
    assert "s2_mentions=none" in brusoni["resolution_note"]
    assert any(row.get("ku_id") == BRUSONI_KU and row.get("type") == "person" for row in manifest)

    canal_rows = [by_id[cid] for cid in CANAL_CANDIDATES]
    assert all(candidate_by_id[cid]["suggested_type"] == "person" for cid in CANAL_CANDIDATES)
    assert all(row["decision"] == "new" and not row.get("ku_id") for row in canal_rows)
    assert sync.get_group(canal_rows[0]["resolution_note"]) == CANAL_GROUP
    assert sync.get_group(canal_rows[1]["resolution_note"]) == CANAL_OLD_GROUP

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    selected = {row["statement_id"]: row for row in statements if row.get("statement_id") in RELATION_IDS}
    assert set(selected) == RELATION_IDS
    assert "cand-0461" in selected["st-chp6-notes-l128-p149-n6"]["qualifiers"]["mentioned_candidate_ids"]
    assert "cand-0496" in selected["st-chp10-p304-smith-country-house-lease-purchase"]["qualifiers"]["mentioned_candidate_ids"]
    assert "cand-0497" in selected["st-chp8-p214-n4-venetian-patrons-owned-pictures"]["qualifiers"]["mentioned_candidate_ids"]
    assert all(row.get("qualifiers", {}).get("relation_candidate") is True for row in selected.values())

    planned = [dict(row) for row in alignments]
    planned_by_id = decision_rows(planned)

    planned_brusoni = planned_by_id[BRUSONI_CANDIDATE]
    planned_brusoni["decision"] = "same"
    planned_brusoni["ku_id"] = BRUSONI_KU
    planned_brusoni["process_ref"] = f"{TASK}#s3-brusoni-canal-cross-chapter-20261018"
    planned_brusoni["resolution_note"] += (
        f" S3复核（{DATE}）：原undecided理由保留为历史；B.csv#308与#309是同一Brusoni, Girolamo主项，"
        "#309的Allori d'Eurota是主项下作品子目，二者均指向印刷页149注。第6章p.149注6以全名Girolamo Brusoni"
        f"称诗集编辑者；cand-0461已登记为[{BRUSONI_KU}]，故cand-0462改判same并复用该人物KU。"
        "索引作品子目不与人物合并为作品；诗集/archive对象保持独立，脚注关系候选留待S6。"
    )

    for cid in CANAL_CANDIDATES:
        row = planned_by_id[cid]
        row["process_ref"] = f"{TASK}#s3-brusoni-canal-cross-chapter-20261018"
        if cid == "cand-0497":
            row["resolution_note"] = row["resolution_note"].replace(
                f"group={CANAL_OLD_GROUP}",
                f"prior standalone group was {CANAL_OLD_GROUP}; group={CANAL_GROUP}",
                1,
            )
        row["resolution_note"] += (
            f" S3跨章复核（{DATE}）：cand-0496（C.csv#20，Gerolamo Canal；第10章p.304）与"
            "cand-0497（C.csv#21，Procuratore Canale；第8章p.214注4）共同归入"
            f"{CANAL_GROUP}，身份决定仍为new、KU待S4。Haskell第10章将全名Gerolamo Canal与"
            "Procuratore di San Marco并列；第8章注4使用Procuratore Canale称同一语境中的威尼斯藏家。"
            f"Treccani DBI Francesco Solimena词条（{CANAL_DB_ENTRY}；访问{DATE}）在索利梅纳 patronage 语境中"
            "亦称Procuratore di San Marco Girolamo Canal，并关联一件为Canal制作的1704年作品；此为支持两处称名/职衔"
            "对应的上下文核对，不是Canal个人规范记录，故不新增外部身份ID。保留原文Canal/Canale拼写；"
            "不与Giovanni Antonio Canal/Canaletto或Fabio Canal合并。先前cand-0497独立组决定已撤回，旧组号保存在本行。"
            "相关S2关系候选留待S6，不在本次生成正式关系。"
        )

    planned_by_id[BRUSONI_CANDIDATE]["process_ref"] = f"{TASK}#s3-brusoni-canal-cross-chapter-20261018"
    before = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(item[key] for item in before.values()) for key in next(iter(before.values()))}
    assert totals["same_candidates"] == before_totals["same_candidates"] + 1
    assert totals["new_candidates"] == before_totals["new_candidates"]
    assert totals["new_groups"] == before_totals["new_groups"] - 1
    assert totals["undecided"] == before_totals["undecided"] - 1
    assert totals["pending_groups"] == before_totals["pending_groups"] - 1
    assert totals["pending_members"] == before_totals["pending_members"]
    assert stats["person"]["same_candidates"] == before["person"]["same_candidates"] + 1
    assert stats["person"]["new_groups"] == before["person"]["new_groups"] - 1
    assert stats["person"]["undecided"] == before["person"]["undecided"] - 1

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3跨章人物身份归并：Brusoni索引子项与Canal/Canale（{DATE}）\n\n"
        f"- `{BRUSONI_CANDIDATE}`（B.csv#309，Brusoni, Girolamo；子目Allori d'Eurota）由undecided改为same → "
        f"[{BRUSONI_KU}](../../../04-knowledge/{BRUSONI_KU}.md)。B.csv#308–309属于同一人名主项，#309仅列作品子目；"
        "第6章p.149注6给出Girolamo Brusoni全名。旧undecided理由在alignment.csv中保留并标明被本次直接索引结构及正文全名证据取代。"
        "子目指向的诗集/archive对象与人物仍分开，关系候选st-chp6-notes-l128-p149-n6留待S6。\n"
        f"- `{CANAL_CANDIDATES[0]}`（C.csv#20，Gerolamo Canal）与`{CANAL_CANDIDATES[1]}`（C.csv#21，Procuratore Canale）"
        f"合并为同一待登记身份组`{CANAL_GROUP}`，二者均为new；撤回的旧组`{CANAL_OLD_GROUP}`保存在cand-0497对齐行。"
        "第10章p.304的全名与职衔、第8章p.214注4的Procuratore称名由同一身份语境连接；Treccani DBI Solimena条目"
        f"（[{CANAL_DB_ENTRY}]({CANAL_DB_ENTRY})）提供上下文印证，但不是Canal个人规范记录，未填作外部身份ID。"
        "保留原书Canal/Canale拼写，不并入Canaletto/Giovanni Antonio Canal或Fabio Canal。两条S2关系候选均留待S6；"
        "该组尚无KU，进入S4待登记。\n"
        f"- 其他相关S2关系候选（{', '.join(sorted(RELATION_IDS))}）均保留原候选状态，未新增正式关系。\n"
        f"- 更新后S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，"
        f"undecided={sync.fmt(totals['undecided'])}；S4待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text += (
        f"\n\n### S3跨章人物身份归并：Brusoni与Canal/Canale（{DATE}）\n\n"
        f"cand-0462复用既有Girolamo Brusoni KU；cand-0496与cand-0497合并为待S4登记的new组"
        f"{CANAL_GROUP}。判断依据、撤回组号、Canal/Canale拼写及与Canaletto、Fabio Canal的边界见"
        f"[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})与alignment.csv。"
        "相关S2关系候选留待S6，未新增正式关系。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {BRUSONI_CANDIDATE} undecided->same/{BRUSONI_KU}; "
            f"Canal candidates={','.join(CANAL_CANDIDATES)} share {CANAL_GROUP}; "
            f"new_groups={totals['new_groups']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; undecided={totals['undecided']}; "
            f"relation_candidates_preserved={len(RELATION_IDS)}; manifest={len(manifest)}"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {BRUSONI_CANDIDATE} same->{BRUSONI_KU}; Canal group={CANAL_GROUP}; "
        f"new_groups={totals['new_groups']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
