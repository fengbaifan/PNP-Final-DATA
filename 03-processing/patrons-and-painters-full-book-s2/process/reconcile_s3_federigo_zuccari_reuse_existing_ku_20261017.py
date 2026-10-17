from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_crosschapter_person_endpoints_20261017_batch6 as precedent

sync = precedent.sync
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CANDIDATE = "cand-2885"
KU_ID = "units/persons/federigo-zuccari"
DATE = "2026-10-17"
ANCHOR = "s3-federigo-zuccari-reuse-20261017"


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct Federigo Zuccari from a duplicate new group to same existing KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_rows = [row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(candidate_rows) == 1
    row = candidate_rows[0]
    assert row.get("decision") == "new" and not row.get("ku_id"), row
    assert candidate_by_id[CANDIDATE].get("suggested_type") == "person"
    manifest_entry = next((entry for entry in manifest if entry.get("ku_id") == KU_ID), None)
    assert manifest_entry and manifest_entry.get("type") == "person"
    card_path = ROOT / str(manifest_entry["card_path"])
    assert card_path.exists()
    assert any(
        entry.get("candidate_id") == "cand-3030"
        and entry.get("decision") == "same"
        and entry.get("ku_id") == KU_ID
        for entry in alignments
    ), "existing same alignment for the exact source name is missing"

    quote = "Federigo Zuccari’s well-meant, but not very successful, attempts to bring it to life in 1593 and 1594."
    source = ROOT / "02-sources/02-Markdown/01_CHP-1.md"
    assert " ".join(quote.split()) in " ".join(source.read_text(encoding="utf-8-sig").split())
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_relation_ids = {
        statement["statement_id"] for statement in statements
        if (statement.get("subject_candidate_id") == CANDIDATE or statement.get("object_candidate_id") == CANDIDATE)
        and (statement.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relation_ids == {"st-chp3-secii-l6-17-pious-ladies-introduced-zuccari"}

    planned_alignment = [dict(item) for item in alignments]
    planned = next(item for item in planned_alignment if item.get("candidate_id") == CANDIDATE and not item.get("external_source"))
    planned["ku_id"] = KU_ID
    planned["decision"] = "same"
    planned["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    planned["resolution_note"] = (
        "source_ref=candidate=cand-2885;index_entry=UVWXYZ.csv#222;index_pages=17, 30, 66;"
        "s2_mentions=m-chp2-seci-l108-119-0006@02-sources/02-Markdown/02_CHP-2_sec_i.md#L108-119[Federigo Zuccari],"
        "m-chp3-secii-l6-17-0027@02-sources/02-Markdown/03_CHP-3_sec_ii.md#L6-17[Federigo Zuccari]; "
        "prior_new_group=new-person:federigo-zuccari-2774f913d3; same_target=units/persons/federigo-zuccari; "
        "existing_KU_card=04-knowledge/units/persons/federigo-zuccari.md; "
        "prior_same_alignment=aln-3307[cand-3030 -> units/persons/federigo-zuccari]; "
        "identity_evidence=the existing card's chapter 1 source contains the exact name Federigo Zuccari, "
        "and the current chapters 2 and 3 repeat that exact personal name; the existing KU identifies this source form as Federico Zuccari and has prior external identity alignment; "
        "S4 duplicate preflight exposed the missed accepted KU; corrected from new to same; no new KU created."
    )

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(result[key] for result in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    result_append = f"""

### S3/S4 复核：Federigo Zuccari 复用既有人物 KU（{DATE}）

`cand-2885`原列为`new-person:federigo-zuccari-2774f913d3`，在S4查重时发现应复用[Federico Zuccari人物卡](../units/persons/federigo-zuccari.md)。该卡已有`cand-3030`通过`aln-3307`映射至同一KU，且第一章来源原句已明确写出“Federigo Zuccari”；第2、3章重复该精确姓名。故将`cand-2885`改为`same`并映射至既有KU，不新建卡；原`new`决定及漏检更正理由保留于过程记录与对齐行。第3章未具名贵妇引入画家的关系候选仍待S6。

当前对齐决定为same {sync.fmt(totals['same_candidates'])}条、new {sync.fmt(totals['new_candidates'])}条（{sync.fmt(totals['new_groups'])}组）；S4新组已登记{sync.fmt(totals['registered_groups'])}组，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条映射；KU总数{sync.fmt(len(manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="{ANCHOR}"></a>

### S3/S4复核：Federigo Zuccari 同一人物复用（{DATE}）

- 全书候选`cand-2885`原分入`new-person:federigo-zuccari-2774f913d3`。S4写入预检命中既有`units/persons/federigo-zuccari`卡，停止新建并回查身份依据。
- 既有卡的第一章来源L681–683明确出现“Federigo Zuccari”，该人物已由`cand-3030`经`aln-3307`映射至现有KU。当前S3候选`cand-2885`在第2章p.30及第3章p.66使用同一全名；既有卡将来源形式Federigo对应规范名Federico Zuccari，并保留既有外部身份核对。姓名形式及对象语境一致，判为同一人物。
- 将`cand-2885`当前决定改为`same` → `units/persons/federigo-zuccari`，在`alignment.csv`保留原alignment ID和原新组作为历史说明，并记录本次查重更正。无新增KU、卡片或accepted.yml项；直接关系候选`st-chp3-secii-l6-17-pious-ladies-introduced-zuccari`仍待S6。

The full-book candidate was initially assigned a new group. S4's duplicate check found an accepted Federico Zuccari person KU whose chapter 1 source gives the exact form “Federigo Zuccari,” already aligned through cand-3030. The full name recurs in chapters 2 and 3, so cand-2885 now reuses that KU. The original new grouping is retained in the alignment rationale; no duplicate card was created. The direct relation candidate remains pending S6.
"""
    process_next = PROCESS.read_text(encoding="utf-8-sig").rstrip() + process_append

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} new -> same {KU_ID}")
        print(
            f"same={totals['same_candidates']}; new={totals['new_candidates']}/{totals['new_groups']}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged"
        )
        print("direct_relation_candidates=1 remains pending S6; no card, KU, formal relation, or S5 row will be added")
        return 0

    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE} -> same {KU_ID}; manifest={len(manifest)} unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
