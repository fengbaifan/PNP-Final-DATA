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
ANCHOR = "s4-person-relation-endpoint-gabriel-gruppello-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

T = {
    "candidate": "cand-1236",
    "group": "new-person:gabriel-gruppello-e9d71c9bc0",
    "ku": "units/persons/gabriel-gruppello",
    "card": "04-knowledge/units/persons/gabriel-gruppello.md",
    "name_zh": "加布里埃尔·格鲁佩洛",
    "name_en": "Gabriel Gruppello",
    "candidate_name": "Gruppello, Gabriel",
    "index_entry": "G.csv#146",
    "index_file": "G.csv",
    "index_name": "Gruppello, Gabriel",
    "index_page": "282",
    "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    "source_span": "lines 142-143; print p. 282",
    "source_quote": (
        "much of the art created at\nDusseldorf during these years, such as the bronze equestrian statue by the Flemish sculptor Gabriel Gruppello, "
        "was inspired by the Elector’s passion for self-display."
    ),
    "source_fragments": [
        "the bronze equestrian statue by the Flemish sculptor Gabriel Gruppello",
        "was inspired by the Elector’s passion for self-display",
    ],
    "location": "第10章；印刷页282；OCR L142-L143",
    "summary": "Haskell举例称，Düsseldorf时期的艺术包括Flemish雕塑家Gabriel Gruppello制作的一尊青铜骑马雕像，并称其体现选侯对自我展示的热衷。未给出雕像年代或现存地点。",
    "description_zh": (
        "哈斯克尔在第10章称，Düsseldorf时期的艺术包括Flemish雕塑家Gabriel Gruppello制作的一尊青铜骑马雕像，并将该雕像作为"
        "Johann Wilhelm热衷自我展示的例子。此卡只记录书中给出的姓名、雕塑家称谓与该例证；原文没有提供雕像年代或现存地点。"
    ),
    "description_en": (
        "In Chapter 10, Haskell says that art at Düsseldorf included a bronze equestrian statue by the Flemish sculptor Gabriel Gruppello "
        "and presents it as an example of Johann Wilhelm’s passion for self-display. This card records only the name, sculptor description, "
        "and example reported in the book; the passage gives no date or present location for the statue."
    ),
    "related_context_zh": "S2作品候选cand-8951（Gabriel Gruppello制作的青铜骑马雕像）仍为S3 new、待S4登记；S2关系候选`st-chp10-p282-gruppello-statue`保留待S6，本卡不新增正式边。",
    "related_context_en": "S2 work candidate cand-8951 (the bronze equestrian statue by Gabriel Gruppello) remains S3 new and awaits S4; relation candidate `st-chp10-p282-gruppello-statue` remains for S6, with no formal edge added here.",
    "relation_id": "st-chp10-p282-gruppello-statue",
    "other_candidate": "cand-8951",
    "other_decision": "new",
    "statement_subject": "cand-1236",
    "statement_object": "cand-8951",
    "statement_predicate": "gruppello_statue_reflected_wilhelms_self_display",
    "statement_fragment": "bronze equestrian statue by the Flemish sculptor Gabriel Gruppello",
    "process_ref": PROCESS_REF,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Gabriel Gruppello's source-backed S3 person group in S4.")
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
    assert not alignment_by_id[T["other_candidate"]].get("ku_id")

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
    assert totals["registered_groups"] == 738 and totals["registered_members"] == 909
    assert totals["pending_groups"] == 4038 and totals["pending_members"] == 4052
    assert len(planned_manifest) == len(manifest) + 1

    process_text = base.replace_process_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 person relation endpoint：Gabriel Gruppello（2026-10-17）\n\n"
        "`cand-1236` 登记为[Gabriel Gruppello](../../../04-knowledge/units/persons/gabriel-gruppello.md)。第10章称其为Flemish雕塑家，"
        "并以其一尊青铜骑马雕像说明Düsseldorf时期艺术与Johann Wilhelm自我展示之间的联系；原文没有给出雕像日期或现存地点。"
        "对应作品候选 `cand-8951` 仍待S4；S2关系候选留待S6，未新增正式边。\n\n"
        f"本批登记1组/1条映射；累计S4已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条，KU={sync.fmt(len(planned_manifest))}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        "\n\n### S4 人物身份组登记：Gabriel Gruppello（2026-10-17）\n\n"
        "`cand-1236` → `units/persons/gabriel-gruppello`。卡片记录Haskell第10章的雕塑家称谓与青铜骑马雕像例证；"
        "雕像候选仍待S4，日期与现存地点未知，S2关系候选留待S6且未新增正式关系。\n\n"
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
        print("S4 person dry-run passed: Gabriel Gruppello singleton group; source, index, and S2 work-endpoint checks passed.")
        print(f"{T['candidate']} -> {T['ku']}; relation_candidate={T['relation_id']}; work_endpoint={T['other_candidate']}:new")
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
