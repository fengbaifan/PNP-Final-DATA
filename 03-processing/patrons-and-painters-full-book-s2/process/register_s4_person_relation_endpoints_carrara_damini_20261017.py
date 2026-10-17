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
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s4-person-relation-endpoints-carrara-damini-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"

TARGETS = [
    {
        "candidate": "cand-3497",
        "group": "new-person:carrara-conte-ventura-ce8b0c9943",
        "ku": "units/persons/conte-ventura-carrara",
        "card": "04-knowledge/units/persons/conte-ventura-carrara.md",
        "name_zh": "文图拉·卡拉拉伯爵",
        "name_en": "Conte Ventura Carrara",
        "index_entry": "",
        "index_file": "",
        "index_name": "",
        "index_page": "",
        "source_file": "02-sources/02-Markdown/01_CHP-1.md",
        "source_span": "lines 512-513; print p. 13, note 2",
        "source_quote": "to Conte Ventura Carrara",
        "source_fragments": ["letter from Carlo Quarisinini to Conte Ventura Carrara", "dated 11 July"],
        "location": "第1章；印刷页13；注2；OCR L512-L513",
        "summary": "Haskell的注2将Conte Ventura Carrara列为Carlo Quarisinini一封1696年7月11日书信的收信人，并指向Bottari第V卷第186页。原信和Bottari刊本未在本任务中独立查阅。",
        "description_zh": (
            "哈斯克尔在第1章注2将Conte Ventura Carrara列为Carlo Quarisinini于1696年7月11日所写书信的收信人，"
            "并将引文定位至Bottari第V卷第186页。当前OCR转录作Quarisinini，S2记录其印刷本校正为Quarismini；"
            "原信及Bottari刊本未在本任务中独立查阅。本卡只记录书内可追溯的收信人身份，不补写其他传记。"
        ),
        "description_en": (
            "In Chapter 1 note 2, Haskell identifies Conte Ventura Carrara as the addressee of a letter by Carlo Quarisinini "
            "dated 11 July 1696 and cites Bottari, volume V, page 186. The OCR transcription reads Quarisinini; S2 records the "
            "printed-form correction Quarismini. Neither the original letter nor Bottari’s publication was independently consulted "
            "for this task. This card records only the recipient identity traceable in the book and adds no other biography."
        ),
        "related_context_zh": "S2书信收信关系候选指向已登记的archive KU `units/archives/quarisimini-carrara-letter-1696`；原信及被引刊本未独立查阅，正式关系留待S6。",
        "related_context_en": "The S2 letter-recipient candidate points to registered archive KU `units/archives/quarisimini-carrara-letter-1696`; the original letter and cited publication were not consulted, so the formal relation remains for S6.",
        "relation_id": "st-chp1-secii-p13-n2-quarismini-letter-addressed-to",
        "other_candidate": "cand-3546",
        "other_decision": "same",
        "other_ku": "units/archives/quarisimini-carrara-letter-1696",
        "statement_subject": "cand-3546",
        "statement_object": "cand-3497",
        "statement_predicate": "letter_addressed_to",
        "statement_fragment": "to Conte Ventura Carrara",
        "process_ref": PROCESS_REF,
    },
    {
        "candidate": "cand-0898",
        "group": "new-person:damini-vincenzo-56b50b2f63",
        "ku": "units/persons/vincenzo-damini",
        "card": "04-knowledge/units/persons/vincenzo-damini.md",
        "name_zh": "温琴佐·达米尼",
        "name_en": "Vincenzo Damini",
        "candidate_name": "Damini, Vincenzo",
        "index_entry": "D.csv#0",
        "index_file": "D.csv",
        "index_name": "Damini, Vincenzo",
        "index_page": "281",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "source_span": "lines 135-137; print p. 281",
        "source_quote": "Vincenzo Damini, a minor painter",
        "source_fragments": ["Vincenzo Damini, a minor painter", "Giacomo Leoni, an architect"],
        "location": "第10章；印刷页281；OCR L135-L137",
        "summary": "Haskell称Vincenzo Damini与Giacomo Leoni从Düsseldorf抵达英格兰，并称Damini为一位次要画家、Leoni为建筑师。",
        "description_zh": (
            "哈斯克尔在第10章称Vincenzo Damini与Giacomo Leoni从Düsseldorf抵达英格兰，并将Damini称作一位次要画家；"
            "同句将Leoni称为建筑师。索引以Damini, Vincenzo列出该人物并指向第281页。此卡只记录本书明确给出的姓名与称谓，"
            "不推写其他经历，也不把同句中的人物自动建成正式关系。"
        ),
        "description_en": (
            "In Chapter 10, Haskell says Vincenzo Damini and Giacomo Leoni arrived in England from Düsseldorf and describes Damini "
            "as a minor painter; the same sentence calls Leoni an architect. The index lists Damini, Vincenzo at page 281. This card "
            "records only the name and description stated in the book, adds no further biography, and does not turn the shared sentence "
            "into a formal relation."
        ),
        "related_context_zh": "S2关系候选 `st-chp10-p281-damini-leoni-arrivals` 保留待S6；Leoni候选cand-1394与England候选cand-4439仍待各自S4登记。",
        "related_context_en": "S2 relation candidate `st-chp10-p281-damini-leoni-arrivals` remains for S6; Leoni candidate cand-1394 and England candidate cand-4439 still await their own S4 registration.",
        "relation_id": "st-chp10-p281-damini-leoni-arrivals",
        "other_candidate": "cand-4439",
        "other_decision": "new",
        "statement_subject": "cand-0898",
        "statement_object": "cand-4439",
        "statement_predicate": "damini_and_leoni_arrived_in_england_from_dusseldorf_damini_painter_leoni_architect",
        "statement_fragment": "Vincenzo Damini, a minor painter",
        "process_ref": PROCESS_REF,
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two source-backed S3 person relation-endpoint groups in S4.")
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
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {line[2:] for line in accepted.splitlines() if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}

    registration_states = []
    for t in TARGETS:
        cid = t["candidate"]
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "person" and candidate.get("canonical_name") == t.get("candidate_name", t["name_en"])
        assert sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        group_members = [
            row["candidate_id"] for row in alignment_rows
            if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert group_members == [cid], (t["group"], group_members)
        source = (ROOT / t["source_file"]).read_text(encoding="utf-8-sig")
        assert all(fragment in source for fragment in t["source_fragments"]), cid
        if t.get("index_entry"):
            assert candidate.get("index_entry_id") == t["index_entry"]
            hits = [
                row for row in base.load_index_rows(t["index_file"])
                if row.get("Main Entry") == t["index_name"] and row.get("Page Numbers") == t["index_page"]
            ]
            assert len(hits) == 1, (t["index_entry"], hits)
        else:
            assert not candidate.get("index_entry_id")

        statement = statement_by_id[t["relation_id"]]
        assert statement.get("qualifiers", {}).get("relation_candidate") is True
        assert statement.get("subject_candidate_id") == t["statement_subject"]
        assert statement.get("object_candidate_id") == t["statement_object"]
        assert statement.get("predicate") == t["statement_predicate"]
        assert t["statement_fragment"] in statement.get("original_quote", "")
        assert alignment_by_id[t["other_candidate"]].get("decision") == t["other_decision"]
        if t.get("other_ku"):
            assert alignment_by_id[t["other_candidate"]].get("ku_id") == t["other_ku"]

        name_matches = [row for row in manifest if row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold()]
        assert len(name_matches) <= 1
        assert (t["ku"] in manifest_by_ku) == bool(name_matches)
        assert not name_matches or name_matches[0].get("ku_id") == t["ku"]
        card_path = ROOT / t["card"]
        aligned = alignment.get("ku_id", "") == t["ku"]
        assert aligned == (t["card"] in accepted_paths) == card_path.exists()
        if not aligned:
            assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        registration_states.append(aligned)

    if any(registration_states):
        assert all(registration_states), "partial registration detected"
        changed = [t for t in TARGETS if (ROOT / t["card"]).read_text(encoding="utf-8-sig") != base.make_card(t)]
        if changed and args.apply:
            for t in changed:
                (ROOT / t["card"]).write_text(base.make_card(t), encoding="utf-8-sig", newline="\n")
        print("ALREADY REGISTERED" if not changed else f"card refresh required for {len(changed)} registered KU(s)")
        return 0

    planned_alignment = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        row = next(row for row in planned_alignment if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        row["ku_id"] = t["ku"]
        row["resolution_note"] += f" S4 registration: mapped {t['group']} to {t['ku']}."
        planned_manifest.append({
            "ku_id": t["ku"],
            "type": "person",
            "canonical_name": f"{t['name_zh']}（{t['name_en']}）",
            "name_en": t["name_en"],
            "source_task": TASK,
            "card_path": t["card"],
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] == 735 and totals["registered_members"] == 906
    assert totals["pending_groups"] == 4043 and totals["pending_members"] == 4057
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    process_text = base.replace_process_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        "### S4 person relation endpoints：Carrara、Damini（2026-10-17）\n\n"
        "`cand-3497` 登记为[Conte Ventura Carrara](../../../04-knowledge/units/persons/conte-ventura-carrara.md)。"
        "Haskell第1章注2称其为一封1696年7月11日书信的收信人；S2记录OCR姓名 Quarisinini 的印刷本校正为 Quarismini，"
        "原信及Bottari刊本未独立查阅。对应archive端点复用已有KU，但正式收信关系留待S6。\n\n"
        "`cand-0898` 登记为[Vincenzo Damini](../../../04-knowledge/units/persons/vincenzo-damini.md)。"
        "第10章称Damini为次要画家，并称其与Giacomo Leoni从Düsseldorf抵达英格兰；Leoni候选 `cand-1394` 与England候选 `cand-4439` 仍待S4，"
        "该statement不转为正式关系。\n\n"
        f"本批登记2组/2条候选映射；累计S4已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条，KU={sync.fmt(len(planned_manifest))}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        "\n\n### S4 人物身份组登记：Carrara、Damini（2026-10-17）\n\n"
        "`cand-3497` → `units/persons/conte-ventura-carrara`，Haskell注2所列1696年书信收信人；原信与Bottari刊本未独立查阅，正式关系待S6。"
        "`cand-0898` → `units/persons/vincenzo-damini`，Haskell称其为次要画家，并记其与Giacomo Leoni从Düsseldorf抵达英格兰；相关候选端点仍待登记，未建立正式关系。\n\n"
        f"本批2组/2条映射；累计已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU={sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    for t in TARGETS:
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > t["card"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {t['card']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    assert len([line for line in planned_accepted.splitlines() if line.startswith("- 04-knowledge/units/")]) == len(planned_manifest)

    if args.dry_run:
        print("S4 person dry-run passed: two singleton S3 groups; source, index, statement, and endpoint checks passed.")
        for t in TARGETS:
            print(f"{t['candidate']} -> {t['ku']}; relation_candidate={t['relation_id']}; other_endpoint={t['other_candidate']}:{t['other_decision']}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}")
        print("formal_relations_added=0; enrichment_rows_changed=0; no files changed")
        return 0

    for t in TARGETS:
        (ROOT / t["card"]).write_text(base.make_card(t), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=2; candidate_mappings=2; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
