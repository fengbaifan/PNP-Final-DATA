from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_person_relation_endpoints_andreosi_audran_barbarigo_20261017 as base  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ANCHOR = "s3-reassessment-saverio-savini-gubbio-terms-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

DECISIONS = [
    {
        "candidate": "cand-2377",
        "type": "person",
        "prior_group": "new-person:saverio-savini-9e01fb818f",
        "target": "units/persons/saverio-savini",
        "target_candidate": "cand-3100",
        "target_card": "04-knowledge/units/persons/saverio-savini.md",
        "source_fragment": "terms laid down for Saverio Savini in Gubbio in 1608 published by Gualandi",
        "record_note": (
            "原先按索引姓名Saverio Savini列为new；复核发现它与既有Salvio Savini卡片的来源锚点完全相同："
            "Haskell第1章印刷页9注1、Gubbio、1608、Gualandi卷IV第60页。既有人物卡已保留书内Saverio拼写，并依据已登记的外部来源将该书内拼写解释为Salvio Savini；"
            "候选cand-3100已映射该人物KU。故cand-2377改判same并映射至同一KU，不另建人物。"
        ),
    },
    {
        "candidate": "cand-12277",
        "type": "archive",
        "prior_group": "archive-group-1bc4e22efce4",
        "target": "units/archives/savini-gubbio-terms-1608",
        "target_candidate": "cand-2967",
        "target_card": "04-knowledge/units/archives/savini-gubbio-terms-1608.md",
        "source_fragment": "terms laid down for Saverio Savini in Gubbio in 1608 published by Gualandi",
        "record_note": (
            "原先由S2锚点建议为new archive；复核发现同页同注已由既有archive卡记录，且cand-2967已映射该KU。"
            "本候选与既有卡的来源、人物、地点、年份及Gualandi卷页完全一致，指向同一被引契约条款文本，不另建archive。"
        ),
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Reassess two S3 groups against existing Savini person and archive KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_rows = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in alignment_rows}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}

    source = (ROOT / "02-sources/02-Markdown/01_CHP-1.md").read_text(encoding="utf-8-sig")
    assert DECISIONS[0]["source_fragment"] in source
    assert DECISIONS[1]["source_fragment"] in source
    assert "Saverio Savini" in (ROOT / DECISIONS[0]["target_card"]).read_text(encoding="utf-8-sig")
    person_card = (ROOT / DECISIONS[0]["target_card"]).read_text(encoding="utf-8-sig")
    archive_card = (ROOT / DECISIONS[1]["target_card"]).read_text(encoding="utf-8-sig")
    assert "Salvio Savini" in person_card and "Saverio Savini" in person_card
    assert "Gualandi" in archive_card and "Gubbio" in archive_card and "1608" in archive_card
    assert "units/persons/saverio-savini" in manifest_by_ku
    assert "units/archives/savini-gubbio-terms-1608" in manifest_by_ku

    for item in DECISIONS:
        cid = item["candidate"]
        c = candidate_by_id[cid]
        a = alignment_by_id[cid]
        target_candidate = alignment_by_id[item["target_candidate"]]
        assert c.get("suggested_type") == item["type"]
        assert target_candidate.get("decision") == "same" and target_candidate.get("ku_id") == item["target"]
        assert manifest_by_ku[item["target"]].get("type") == item["type"]
        assert item["source_fragment"] in source
        if a.get("decision") == "new" and not a.get("ku_id"):
            assert sync.get_group(a.get("resolution_note", "")) == item["prior_group"]
        else:
            assert a.get("decision") == "same" and a.get("ku_id") == item["target"]

    statement = statement_by_id["st-chp1-secii-notes-local-commissions-savini-minnitti"]
    assert statement.get("qualifiers", {}).get("relation_candidate") is True
    assert statement.get("object_candidate_id") == "cand-2377"
    assert statement.get("subject_candidate_id") == "cand-12277"
    assert "Gualandi" in statement.get("qualifiers", {}).get("claim", "")

    if all(alignment_by_id[item["candidate"]].get("decision") == "same" and alignment_by_id[item["candidate"]].get("ku_id") == item["target"] for item in DECISIONS):
        print("ALREADY REASSESSED: both candidate groups map to their existing same-type KUs.")
        return 0

    planned_alignment = [dict(row) for row in alignments]
    for item in DECISIONS:
        row = next(row for row in planned_alignment if row.get("candidate_id") == item["candidate"] and not row.get("external_source"))
        row["decision"] = "same"
        row["ku_id"] = item["target"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += (
            f" | S3 reassessment 2026-10-17: prior decision=new, prior_group={item['prior_group']}; "
            f"now same -> {item['target']}. {item['record_note']}"
        )

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["same_candidates"] == 1898 and totals["same_kus"] == 1040
    assert totals["new_candidates"] == 4961 and totals["new_groups"] == 4776
    assert totals["registered_groups"] == 735 and totals["registered_members"] == 906
    assert totals["pending_groups"] == 4041 and totals["pending_members"] == 4055
    assert len(manifest) == 1754

    process_text = base.replace_process_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S3复核：Saverio／Salvio Savini 与Gubbio条款archive（2026-10-17）\n\n"
        "复核`cand-2377`（Saverio Savini）与既有`units/persons/saverio-savini`、`cand-12277`（Gualandi刊布的Savini 1608 Gubbio条款）与既有"
        "`units/archives/savini-gubbio-terms-1608`。两项候选都指向第1章印刷页9注1同一来源锚点：Gubbio、1608、Saverio Savini、Gualandi卷IV第60页；"
        "既有人物卡保留书内Saverio拼写，并记录与外部来源所用Salvio Savini姓名的对齐；既有archive卡记录同一被引条款及其限制。"
        "因此前者从`new`改为`same`→既有人物KU，后者从`new`改为`same`→既有archive KU；两个旧new组号保留在alignment历史备注中，不创建重复KU。"
        "被引Gualandi刊本和原始合同本任务未另行查阅；本次只复用已有卡片中留存的身份/来源证据。S2 statement保留待S6复核，未改relations.csv。\n\n"
        f"改判后S3：same={sync.fmt(totals['same_candidates'])}候选→{sync.fmt(totals['same_kus'])}个既有KU；"
        f"new={sync.fmt(totals['new_candidates'])}候选/{sync.fmt(totals['new_groups'])}组。S4累计已登记"
        f"{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU={sync.fmt(len(manifest))}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    result_text += (
        "\n\n### S3复核：Savini跨章重复候选映射既有KU（2026-10-17）\n\n"
        "`cand-2377` 由 `new` 改为 `same` → `units/persons/saverio-savini`；`cand-12277` 由 `new` 改为 `same` → "
        "`units/archives/savini-gubbio-terms-1608`。二者与既有卡都对应第1章p.9注1同一段Gubbio 1608年、Saverio Savini、Gualandi IV p.60书目锚点；"
        "既有人物卡已记录Saverio/SALVIO姓名差异及支持依据，故不另建KU。原new组号和变更理由保存在alignment行；没有新增正式关系。\n\n"
        f"改判后 same={sync.fmt(totals['same_candidates'])}→{sync.fmt(totals['same_kus'])}个既有KU；"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组；S4已登记"
        f"{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条，待登记"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    if args.dry_run:
        print("S3 reassessment dry-run passed: both candidate source anchors duplicate accepted person/archive evidence.")
        for item in DECISIONS:
            print(f"{item['candidate']} new({item['prior_group']}) -> same {item['target']}")
        print(f"same={totals['same_candidates']}->{totals['same_kus']}; new={totals['new_candidates']}/{totals['new_groups']}; pending_S4={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}")
        print("formal_relations_changed=0; cards_changed=0; no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: revised=2 candidate decisions; same={totals['same_candidates']}->{totals['same_kus']}; "
        f"new={totals['new_candidates']}/{totals['new_groups']}; S4 pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(manifest)}; formal_relations_changed=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
