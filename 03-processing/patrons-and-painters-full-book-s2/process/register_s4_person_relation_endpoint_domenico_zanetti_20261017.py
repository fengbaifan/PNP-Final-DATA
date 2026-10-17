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
ANCHOR = "s4-person-relation-endpoint-domenico-zanetti-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

T = {
    "candidate": "cand-2860",
    "group": "new-person:domenico-zanetti-fb3b4156cf",
    "ku": "units/persons/domenico-zanetti",
    "card": "04-knowledge/units/persons/domenico-zanetti.md",
    "name_zh": "多梅尼科·扎内蒂",
    "name_en": "Domenico Zanetti",
    "candidate_name": "Zanetti, Domenico",
    "index_entry": "UVWXYZ.csv#197",
    "index_file": "UVWXYZ.csv",
    "index_name": "Zanetti, Domenico",
    "index_page": "284n",
    "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    "source_span": "line 524; print p. 284, note 1",
    "source_quote": "Another Venetian painter who worked extensively for the Elector at Diisseldorf was Domenico Zanetti—de Pigage.",
    "source_fragments": ["Another Venetian painter who worked extensively for the Elector", "Domenico Zanetti", "—de Pigage"],
    "location": "第10章；印刷页284；注1；OCR L524",
    "summary": (
        "Haskell注1称Domenico Zanetti是另一位在Düsseldorf长期为选侯工作的威尼斯画家；原OCR为Diisseldorf，S2记录校为Düsseldorf。"
        "原句在姓名后接“—de Pigage”，其功能与身份仍未确定。"
    ),
    "description_zh": (
        "哈斯克尔在第10章注1称Domenico Zanetti是另一位在Düsseldorf长期为选侯工作的威尼斯画家。原OCR写作“Diisseldorf”，"
        "S2按印刷页记录校为“Düsseldorf”。原句姓名后附“—de Pigage”，其功能及其与Nicolas de Pigage的关系未明；该后缀未并入Zanetti姓名。"
        "这条人物陈述未在本任务中独立核验。"
    ),
    "description_en": (
        "In Chapter 10 note 1, Haskell identifies Domenico Zanetti as another Venetian painter who worked extensively for the Elector at Düsseldorf. "
        "The OCR form “Diisseldorf” is corrected in S2 to “Düsseldorf” based on the printed page. The phrase “—de Pigage” follows the name, "
        "but its function and relation to Nicolas de Pigage are unresolved; it is not incorporated into Zanetti’s name. The biographical statement "
        "was not independently verified for this task."
    ),
    "related_context_zh": (
        "S2关系候选`st-chp10-notes-p284n1-zanetti-elector-dusseldorf`指向已复用的Johann Wilhelm KU；“de Pigage”仍为候选cand-9332（undecided），"
        "S2只列出其可能关联cand-9322，未判定身份或关系。该候选关系留待S6。"
    ),
    "related_context_en": (
        "S2 relation candidate `st-chp10-notes-p284n1-zanetti-elector-dusseldorf` points to the reused Johann Wilhelm KU; “de Pigage” remains "
        "candidate cand-9332 (undecided), with cand-9322 listed only as a possible identity. S2 does not resolve that identity or relation; this candidate remains for S6."
    ),
    "relation_id": "st-chp10-notes-p284n1-zanetti-elector-dusseldorf",
    "other_candidate": "cand-1325",
    "other_decision": "same",
    "other_ku": "units/persons/johann-wilhelm-elector-palatine",
    "other_unresolved": "cand-9332",
    "possible_identity": "cand-9322",
    "statement_subject": "cand-2860",
    "statement_object": "cand-1325",
    "statement_predicate": "domenico_zanetti_worked_extensively_for_johann_wilhelm_at_dusseldorf",
    "statement_fragment": "Domenico Zanetti",
    "process_ref": PROCESS_REF,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Domenico Zanetti's source-backed S3 person group in S4.")
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

    candidate = candidate_by_id[T["candidate"]]
    alignment = alignment_by_id[T["candidate"]]
    assert candidate.get("suggested_type") == "person" and candidate.get("canonical_name") == T["candidate_name"]
    assert candidate.get("index_entry_id") == T["index_entry"]
    assert sync.get_group(alignment.get("resolution_note", "")) == T["group"]
    group_members = [
        row["candidate_id"] for row in alignment_rows
        if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == T["group"]
    ]
    assert group_members == [T["candidate"]]
    index_hits = [
        row for row in base.load_index_rows(T["index_file"])
        if row.get("Main Entry") == T["index_name"] and row.get("Page Numbers") == T["index_page"]
        and row.get("Sub-entry", "") == candidate.get("sub_entry", "")
    ]
    assert len(index_hits) == 1, index_hits
    source = (ROOT / T["source_file"]).read_text(encoding="utf-8-sig")
    assert all(fragment in source for fragment in T["source_fragments"])

    statement = statement_by_id[T["relation_id"]]
    assert statement.get("qualifiers", {}).get("relation_candidate") is True
    assert statement.get("subject_candidate_id") == T["statement_subject"]
    assert statement.get("object_candidate_id") == T["statement_object"]
    assert statement.get("predicate") == T["statement_predicate"]
    assert T["statement_fragment"] in statement.get("original_quote", "")
    assert alignment_by_id[T["other_candidate"]].get("decision") == T["other_decision"]
    assert alignment_by_id[T["other_candidate"]].get("ku_id") == T["other_ku"]
    assert alignment_by_id[T["other_unresolved"]].get("decision") == "undecided"
    assert T["possible_identity"] in statement.get("qualifiers", {}).get("possible_identity_candidates", [])

    name_matches = [row for row in manifest if row.get("type") == "person" and (row.get("name_en") or "").casefold() == T["name_en"].casefold()]
    assert len(name_matches) <= 1
    assert (T["ku"] in manifest_by_ku) == bool(name_matches)
    assert not name_matches or name_matches[0].get("ku_id") == T["ku"]
    card_path = ROOT / T["card"]
    aligned = alignment.get("ku_id", "") == T["ku"]
    assert aligned == (T["card"] in accepted_paths) == card_path.exists()
    if aligned:
        assert card_path.read_text(encoding="utf-8-sig") == base.make_card(T)
        print(f"ALREADY REGISTERED: {T['group']} -> {T['ku']}")
        return 0
    assert alignment.get("decision") == "new" and not alignment.get("ku_id")

    planned_alignment = [dict(row) for row in alignments]
    row = next(row for row in planned_alignment if row.get("candidate_id") == T["candidate"] and not row.get("external_source"))
    row["ku_id"] = T["ku"]
    row["resolution_note"] += f" S4 registration: mapped {T['group']} to {T['ku']}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": T["ku"],
        "type": "person",
        "canonical_name": f"{T['name_zh']}（{T['name_en']}）",
        "name_en": T["name_en"],
        "source_task": TASK,
        "card_path": T["card"],
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(r[key] for r in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["same_candidates"] == 1898 and totals["same_kus"] == 1040
    assert totals["new_candidates"] == 4961 and totals["new_groups"] == 4776
    assert totals["registered_groups"] == 739 and totals["registered_members"] == 910
    assert totals["pending_groups"] == 4037 and totals["pending_members"] == 4051
    assert len(planned_manifest) == len(manifest) + 1

    process_text = base.replace_process_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 person relation endpoint：Domenico Zanetti（2026-10-17）\n\n"
        "`cand-2860` 登记为[Domenico Zanetti](../../../04-knowledge/units/persons/domenico-zanetti.md)。"
        "第10章注1称其为在Düsseldorf为选侯工作的威尼斯画家；索引提供人物全名与页码，原文后缀“de Pigage”保留未决，不并入姓名。"
        "S2列`cand-9332`为undecided，可能关联`cand-9322`，未作身份或关系判断；Haskell陈述未独立核验。S2关系候选留待S6。\n\n"
        f"本批登记1组/1条映射；累计S4已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条，KU={sync.fmt(len(planned_manifest))}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        "\n\n### S4 人物身份组登记：Domenico Zanetti（2026-10-17）\n\n"
        "`cand-2860` → `units/persons/domenico-zanetti`。记录Haskell第10章注1的画家身份与为选侯工作的陈述；“de Pigage”后缀及其与"
        "Nicolas de Pigage候选的可能关系仍待证，不作姓名合并。关系留待S6，未新增正式关系。\n\n"
        f"本批1组/1条映射；累计已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU={sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > T["card"]),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {T['card']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    assert len([line for line in planned_accepted.splitlines() if line.startswith("- 04-knowledge/units/")]) == len(planned_manifest)

    if args.dry_run:
        print("S4 person dry-run passed: Domenico Zanetti singleton group; source, index, relation, and unresolved-suffix checks passed.")
        print(f"{T['candidate']} -> {T['ku']}; relation_candidate={T['relation_id']}; suffix_candidate={T['other_unresolved']}:undecided; possible_identity={T['possible_identity']}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}")
        print("formal_relations_added=0; enrichment_rows_changed=0; no files changed")
        return 0

    card_path.write_text(base.make_card(T), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=1; candidate_mappings=1; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
