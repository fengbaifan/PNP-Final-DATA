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
ANCHOR = "s4-person-relation-endpoint-adrian-van-der-werff-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

T = {
    "candidate": "cand-2808",
    "group": "new-person:adrian-der-van-werff-df0c099420",
    "ku": "units/persons/adrian-van-der-werff",
    "card": "04-knowledge/units/persons/adrian-van-der-werff.md",
    "name_zh": "阿德里安·范德韦尔夫",
    "name_en": "Adrian van der Werff",
    "candidate_name": "Werff, Adrian van der",
    "index_entry": "UVWXYZ.csv#145",
    "index_file": "UVWXYZ.csv",
    "index_name": "Werff, Adrian van der",
    "index_page": "283",
    "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    "source_span": "line 153; print p. 283",
    "source_quote": "Both Weenix and Van det Werff were invited by him to Düsseldorf,",
    "source_fragments": [
        "Adrian van der Werff",
        "though the latter refused to accept an official post as court painter",
        "work exclusively for the Elector for six months in every year",
        "large numbers of his smooth, light, enamelled paintings",
        "found their way into Johann Wilhelm",
    ],
    "location": "第10章；印刷页283；OCR L153",
    "summary": (
        "Haskell称Adrian van der Werff与Jan Weenix受Johann Wilhelm邀请前往Düsseldorf；Van der Werff拒绝正式宫廷画家职位，"
        "但同意每年六个月专为选侯工作，并有大量作品进入选侯画廊。S2保留限定：来源未证明Weenix接受邀请，也未证明该工作安排每年均实际履行。"
    ),
    "description_zh": (
        "哈斯克尔在第10章称Adrian van der Werff与Jan Weenix受Johann Wilhelm邀请前往Düsseldorf；随后称Van der Werff拒绝正式宫廷画家职位，"
        "但同意每年六个月专为选侯工作，并记其大量画作进入选侯画廊。S2限定：文本不证明Weenix接受邀请，也不证明该安排每年均实际履行。"
        "同段审美引文未注明说话者，因此本卡不将其归给特定人物。"
    ),
    "description_en": (
        "In Chapter 10, Haskell says Adrian van der Werff and Jan Weenix were invited by Johann Wilhelm to Düsseldorf. Haskell then says "
        "van der Werff declined an official court-painter post but agreed to work exclusively for the Elector six months each year, and that "
        "many of his paintings entered the Elector’s gallery. The source does not establish that Weenix accepted the invitation or that the "
        "work arrangement was fulfilled every year. The speaker of a nested aesthetic quotation in the passage is unidentified, so this card "
        "does not attribute it to a named person."
    ),
    "related_context_zh": (
        "S2关系候选`st-chp10-p283-weenix-werff-invited`、`st-chp10-p283-werff-refused-office-agreed-exclusive-work`及"
        "`st-chp10-p283-werff-paintings-entered-gallery`均保留待S6；Johann Wilhelm端点已复用既有KU，未新增正式关系。"
    ),
    "related_context_en": (
        "S2 relation candidates `st-chp10-p283-weenix-werff-invited`, `st-chp10-p283-werff-refused-office-agreed-exclusive-work`, and "
        "`st-chp10-p283-werff-paintings-entered-gallery` remain for S6; the Johann Wilhelm endpoint reuses an existing KU and no formal relation was added."
    ),
    "relation_id": "st-chp10-p283-werff-refused-office-agreed-exclusive-work",
    "other_candidate": "cand-1325",
    "other_decision": "same",
    "other_ku": "units/persons/johann-wilhelm-elector-palatine",
    "statement_subject": "cand-2808",
    "statement_object": "cand-1325",
    "statement_predicate": "van_der_werff_declined_court_post_but_agreed_exclusive_seasonal_work",
    "statement_fragment": "refused to accept an official post as court painter",
    "process_ref": PROCESS_REF,
    "extra_sources": [
        {
            "location": "第10章；印刷页283；OCR L153",
            "summary": "Haskell称Van der Werff拒绝正式宫廷画家职位，但同意每年六个月专为选侯工作；S2注明未证明该安排每年均实际履行。",
            "span": "line 153; print p. 283",
            "quote": "though the latter refused to accept an official post as court painter, he agreed to work exclusively for the Elector for six months in every year,",
        },
        {
            "location": "第10章；印刷页283；OCR L153",
            "summary": "Haskell称大量Van der Werff画作进入Johann Wilhelm画廊；同句的审美引文发言者未注明。",
            "span": "line 153; print p. 283",
            "quote": "large numbers of his smooth, light, enamelled paintings",
        },
    ],
}

RELATED_STATEMENT_IDS = [
    "st-chp10-p283-weenix-werff-invited",
    "st-chp10-p283-werff-refused-office-agreed-exclusive-work",
    "st-chp10-p283-werff-paintings-entered-gallery",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Adrian van der Werff's source-backed S3 person group in S4.")
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

    primary = statement_by_id[T["relation_id"]]
    assert primary.get("qualifiers", {}).get("relation_candidate") is True
    assert primary.get("subject_candidate_id") == T["statement_subject"]
    assert primary.get("object_candidate_id") == T["statement_object"]
    assert primary.get("predicate") == T["statement_predicate"]
    assert T["statement_fragment"] in primary.get("original_quote", "")
    for statement_id in RELATED_STATEMENT_IDS:
        assert statement_by_id[statement_id].get("qualifiers", {}).get("relation_candidate") is True
        assert "cand-2808" in statement_by_id[statement_id].get("qualifiers", {}).get("mentioned_candidate_ids", []) or statement_by_id[statement_id].get("subject_candidate_id") == "cand-2808"
    assert alignment_by_id[T["other_candidate"]].get("decision") == T["other_decision"]
    assert alignment_by_id[T["other_candidate"]].get("ku_id") == T["other_ku"]

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
    assert totals["registered_groups"] == 737 and totals["registered_members"] == 908
    assert totals["pending_groups"] == 4039 and totals["pending_members"] == 4053
    assert len(planned_manifest) == len(manifest) + 1

    process_text = base.replace_process_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 person relation endpoint：Adrian van der Werff（2026-10-17）\n\n"
        "`cand-2808` 登记为[Adrian van der Werff](../../../04-knowledge/units/persons/adrian-van-der-werff.md)。"
        "第10章p.283称其与Jan Weenix受Johann Wilhelm邀请，并记其拒绝正式宫廷画家职位、同意每年六个月专为选侯工作，且大量画作进入画廊。"
        "S2限定未证明Weenix接受邀请或该安排每年均履行；同段审美引文的发言者未识别。三条S2关系候选保留待S6，未新增正式边。\n\n"
        f"本批登记1组/1条映射；累计S4已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条，KU={sync.fmt(len(planned_manifest))}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        "\n\n### S4 人物身份组登记：Adrian van der Werff（2026-10-17）\n\n"
        "`cand-2808` → `units/persons/adrian-van-der-werff`。卡片依据第10章p.283及索引记录其邀约、拒绝正式宫廷职位、季节性专属工作和画作入藏陈述，"
        "保留未接受邀约、未证明每年履行及引文发言者未识别等限定。三条S2关系候选留待S6，未新增正式关系。\n\n"
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
        print("S4 person dry-run passed: Adrian van der Werff singleton group; index, source, and three S2 candidate checks passed.")
        print(f"{T['candidate']} -> {T['ku']}; relation_candidates={len(RELATED_STATEMENT_IDS)}; existing_endpoint={T['other_candidate']}:{T['other_ku']}")
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
