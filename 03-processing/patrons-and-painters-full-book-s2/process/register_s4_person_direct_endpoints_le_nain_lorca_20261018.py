from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import register_s4_person_direct_endpoints_h_section_20261018 as template  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
ENTITY = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ENRICHMENT = TABLES / "enrichment.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s4-person-direct-endpoints-le-nain-lorca-batch-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [
    {
        "primary": "cand-1377", "members": ["cand-1377"], "expected_name": "Le Nain, Louis", "expected_pages": "122, 184", "prior_candidate_pages": "133, 184",
        "group": "new-person:le-louis-nain-147a6ee7a9", "ku": "units/persons/louis-le-nain", "card": "04-knowledge/units/persons/louis-le-nain.md",
        "name_zh": "路易·勒南", "name_en": "Louis Le Nain",
        "name_rows": [("索引名", "Le Nain, Louis", "S1（索引L.csv#34）"), ("正文姓名形式", "Louis Le Nain", "S2（第7章p.175）")],
        "sources": [src("第7章第I节；印刷页175", "Haskell称某幅画作对Louis Le Nain等人的风格产生的影响曾被追溯。", "the influence of which has been traced on the styles of artists as different as Louis Le Nain, Laurent de la Hyre and Philippe de Champaigne", "02-sources/02-Markdown/07_CHP-7_sec_i.md", "line 63; print p.175")],
        "zh": "本卡登记索引L.csv#34所列Louis Le Nain。第7章p.175称一幅画对Le Nain等人的风格影响曾被追溯；原文未在此处指明具体研究者或证据，本卡不扩展为确定影响关系。",
        "en": "This card registers Louis Le Nain under index L.csv#34. Chapter 7, p.175, says the influence of a painting on Le Nain’s and other artists’ styles had been traced; the passage names no researcher or evidence here, so the card does not turn it into a settled influence claim.",
        "context_zh": "该段将Louis Le Nain与Laurent de la Hyre、Philippe de Champaigne并列为相关风格讨论对象。直接S2候选st-chp7-p175-i02留待S6裁决。",
        "context_en": "The passage names Louis Le Nain alongside Laurent de la Hyre and Philippe de Champaigne in the style discussion. The direct S2 candidate st-chp7-p175-i02 remains for S6 review.",
        "relations": ["st-chp7-p175-i02"], "endpoints": {"st-chp7-p175-i02": "influenced_style_of"},
    },
    {
        "primary": "cand-1378", "members": ["cand-1378"], "expected_name": "Le Vau, Louis", "expected_pages": "187",
        "group": "new-person:le-louis-vau-324972e817", "ku": "units/persons/louis-le-vau", "card": "04-knowledge/units/persons/louis-le-vau.md",
        "name_zh": "路易·勒沃", "name_en": "Louis Le Vau",
        "name_rows": [("索引名", "Le Vau, Louis", "S1（索引L.csv#35）"), ("正文姓名形式", "Le Vau", "S2（第7章p.187）")],
        "sources": [src("第7章第I节；印刷页187", "Haskell称Colbert对Le Vau抱有敌意，并称Le Vau曾是Mazarin的主要建筑师。", "Colbert was hostile to Le Vau, who had been Mazarin’s principal architect", "02-sources/02-Markdown/07_CHP-7_sec_i.md", "line 227; print p.187")],
        "zh": "本卡登记索引L.csv#35所列Louis Le Vau。第7章p.187称Colbert对其抱有敌意，并称他曾是Mazarin的主要建筑师；两项均保留为Haskell的来源表述。",
        "en": "This card registers Louis Le Vau under index L.csv#35. Chapter 7, p.187, says Colbert was hostile to him and that he had been Mazarin’s principal architect; both remain attributed to Haskell.",
        "context_zh": "该段围绕Louis XIV与Colbert对Louvre东立面的方案展开。直接S2候选st-chp7-p187-i11、st-chp7-p187-i12留待S6逐条裁决。",
        "context_en": "The passage concerns Louis XIV and Colbert’s proposals for the eastern front of the Louvre. Direct S2 candidates st-chp7-p187-i11 and st-chp7-p187-i12 remain for individual S6 review.",
        "relations": ["st-chp7-p187-i11", "st-chp7-p187-i12"],
        "endpoints": {"st-chp7-p187-i11": "hostile_to_le_vau", "st-chp7-p187-i12": "principal_architect_of"},
    },
    {
        "primary": "cand-1383", "members": ["cand-1383"], "expected_name": "Lelli, Ercole", "expected_pages": "351",
        "group": "new-person:ercole-lelli-49868de830", "ku": "units/persons/ercole-lelli", "card": "04-knowledge/units/persons/ercole-lelli.md",
        "name_zh": "埃尔科莱·莱利", "name_en": "Ercole Lelli",
        "name_rows": [("索引名", "Lelli, Ercole", "S1（索引L.csv#40）"), ("正文姓名形式（原书拼写）", "Ercole Lefli", "S2（第14章p.351）")],
        "sources": [src("第14章导论；印刷页351", "Algarotti提出的画家与题材名单在Bologna部分将Ercole Lefli与Donato Creti并列；该段提醒不少评论可能来自转述或外地收藏。", "He found subjects for Francesco de Mura and Solimena among the Neapolitans; Ercole Lefli and Donato Creti in Bologna", "02-sources/02-Markdown/14_CHP-14_intro.md", "line 51; print p.351")],
        "zh": "本卡登记索引L.csv#40所列Ercole Lelli。第14章p.351原书拼作“Ercole Lefli”，在Bologna语境中与Donato Creti并列；本卡保留异拼，不据此扩写具体委托或创作事实。",
        "en": "This card registers Ercole Lelli under index L.csv#40. Chapter 14, p.351, prints “Ercole Lefli” and places the name alongside Donato Creti in the Bologna context; the spelling is retained and no specific commission or work is inferred.",
        "context_zh": "该段说明Algarotti的名单可能依据通信者、旅行者或外地收藏所得的二手信息。直接S2候选st-chp14-p351-bologna-subjects留待S6裁决。",
        "context_en": "The passage says Algarotti’s list may draw on second-hand information from correspondents, travellers, or foreign collections. The direct S2 candidate st-chp14-p351-bologna-subjects remains for S6 review.",
        "relations": ["st-chp14-p351-bologna-subjects"], "endpoints": {"st-chp14-p351-bologna-subjects": "found_subject_for_artist_in_city_context"},
    },
    {
        "primary": "cand-1384", "members": ["cand-1384"], "expected_name": "Lely, Sir Peter", "expected_pages": "122n", "prior_candidate_pages": "135n",
        "group": "new-person:lely-peter-2424b887f2", "ku": "units/persons/sir-peter-lely", "card": "04-knowledge/units/persons/sir-peter-lely.md",
        "name_zh": "彼得·莱利爵士", "name_en": "Sir Peter Lely",
        "name_rows": [("索引名", "Lely, Sir Peter", "S1（索引L.csv#41）"), ("正文姓名形式", "Lely", "S2（第5章p.135注2）")],
        "sources": [src("第5章第III节注2；印刷页135", "Haskell称Lely似乎是Van Laer的仰慕者，并依据其拍卖目录中若干风俗场景被标作“Bamboots”作说明。", "Lely seems to have been an admirer, for in his sale catalogue (Burlington Magazine, 1943, pp. 185-191) various genre scenes are attributed to ‘Bamboots’.", "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "line 135; print p.135 n.2")],
        "zh": "本卡登记索引L.csv#41所列Sir Peter Lely。第5章p.135注2仅称他“似乎”是Van Laer的仰慕者，并以其拍卖目录所载归属作说明；保留原文的推测语气及目录归属限定。",
        "en": "This card registers Sir Peter Lely under index L.csv#41. Chapter 5, p.135 n.2, says he “seems” to have admired Van Laer and cites attributions in his sale catalogue; the tentative wording and catalogue attribution are retained.",
        "context_zh": "注2提及目录中若干风俗场景被归为“Bamboots”。直接S2候选st-chp5-notes-l135-lely-admiration留待S6裁决，不将拍卖目录归属提升为已核实作品身份。",
        "context_en": "Note 2 mentions genre scenes attributed to “Bamboots” in the catalogue. The direct S2 candidate st-chp5-notes-l135-lely-admiration remains for S6; the catalogue attribution is not upgraded to a verified work identity.",
        "relations": ["st-chp5-notes-l135-lely-admiration"], "endpoints": {"st-chp5-notes-l135-lely-admiration": "reported_admiration"},
    },
    {
        "primary": "cand-1436", "members": ["cand-1436"], "expected_name": "Lorca, Bernardino", "expected_pages": "135n",
        "group": "new-person:bernardino-lorca-c2952a5e49", "ku": "units/persons/bernardino-lorca", "card": "04-knowledge/units/persons/bernardino-lorca.md",
        "name_zh": "贝尔纳迪诺·洛尔卡", "name_en": "Bernardino Lorca",
        "name_rows": [("索引名", "Lorca, Bernardino", "S1（索引L.csv#93）"), ("正文姓名形式", "Bernardino Lorca", "S2（第5章p.135注5）")],
        "sources": [src("第5章第III节注5；印刷页135", "Haskell称罗马商人Bernardino Lorca是Van Laer的另一位朋友和仰慕者，并指向Resta书信的Bottari刊本。", "Another friend and admirer of Van Laer was the Roman merchant Bernardino Lorca—see letter of Sebastiano Resta dated 27 February 1704 published by Bottari, II, p. 106.", "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "line 138; print p.135 n.5")],
        "zh": "本卡登记索引L.csv#93所列Bernardino Lorca。第5章p.135注5将其称为Van Laer的罗马商人朋友与仰慕者，并指向经Bottari刊布的Sebastiano Resta书信；该信及转引来源未在本批独立查阅。",
        "en": "This card registers Bernardino Lorca under index L.csv#93. Chapter 5, p.135 n.5, calls him a Roman merchant and another friend and admirer of Van Laer, citing a Sebastiano Resta letter published by Bottari; neither the letter nor the cited edition was independently consulted in this batch.",
        "context_zh": "亲友与仰慕关系均是Haskell对转引书信的叙述。直接S2候选st-chp5-notes-l138-lorca-friend留待S6裁决。",
        "context_en": "The friendship and admiration are Haskell’s account of a cited letter. The direct S2 candidate st-chp5-notes-l138-lorca-friend remains for S6 review.",
        "relations": ["st-chp5-notes-l138-lorca-friend"], "endpoints": {"st-chp5-notes-l138-lorca-friend": "reported_friendship_and_admiration"},
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register five source-backed S3 person groups used as direct S2 relation endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    template.TARGETS = TARGETS
    template.DATE, template.ANCHOR, template.PROCESS_REF = DATE, ANCHOR, PROCESS_REF
    sync = template.helper.base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    candidate_fields, candidates = sync.read_csv(ENTITY)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    planned_candidates = [dict(r) for r in candidates]
    planned_candidate_by_id = {r["candidate_id"]: r for r in planned_candidates}
    main_rows = [r for r in alignments if r.get("candidate_id") and not r.get("external_source")]
    main_by_id = {r["candidate_id"]: r for r in main_rows}
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {r["statement_id"]: r for r in statements}

    for t in TARGETS:
        candidate = candidate_by_id[t["primary"]]
        t["entry"], t["index_name"], t["pages"] = candidate["index_entry_id"], candidate["canonical_name"], candidate["index_page_range"]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("canonical_name") == t["expected_name"]
        prior_pages = t.get("prior_candidate_pages")
        assert candidate.get("index_page_range") in ({prior_pages, t["expected_pages"]} if prior_pages else {t["expected_pages"]})
        if prior_pages and candidate.get("index_page_range") == prior_pages:
            planned_candidate_by_id[t["primary"]]["index_page_range"] = t["expected_pages"]
        t["pages"] = t["expected_pages"]
        row = main_by_id[t["primary"]]
        assert row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == t["group"]
        assert not row.get("ku_id") or row.get("ku_id") == t["ku"]
        members = [r["candidate_id"] for r in main_rows if r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == t["group"]]
        assert members == t["members"]
        index_file, _ = t["entry"].split("#", 1)
        index_hits = [r for r in template.helper.base.read_index_rows(index_file) if r.get("Main Entry") == t["index_name"] and r.get("Page Numbers") == t["pages"]]
        assert len(index_hits) == 1
        direct = {r["statement_id"]: r for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == t["primary"] or r.get("object_candidate_id") == t["primary"])}
        assert set(direct) == set(t["endpoints"]), (t["primary"], sorted(direct), sorted(t["endpoints"]))
        for sid, predicate in t["endpoints"].items(): assert direct[sid].get("predicate") == predicate
        for item in t["sources"]:
            text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", text), (t["primary"], item["span"])
        path = ROOT / t["card"]
        mapped = row.get("ku_id") == t["ku"]
        assert (t["ku"] in manifest_by_ku) == (t["card"] in accepted_paths) == path.exists() == mapped

    cards = {t["card"]: template.make_card(t) for t in TARGETS}
    all_registered = all(main_by_id[t["primary"]].get("ku_id") == t["ku"] for t in TARGETS)
    if all_registered:
        for t in TARGETS: assert (ROOT / t["card"]).read_text(encoding="utf-8-sig") == cards[t["card"]]
        print("ALREADY REGISTERED: all five person groups and their candidate mappings are present.")
        return 0
    assert not any(main_by_id[t["primary"]].get("ku_id") for t in TARGETS), "partial registration requires explicit reconciliation"

    before = sync.summarize_by_type(candidates, alignments)
    before_totals = {k: sum(r[k] for r in before.values()) for k in next(iter(before.values()))}
    planned_alignments = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    planned_manifest, planned_accepted = list(manifest), list(accepted_lines)
    for t in TARGETS:
        row = planned_by_id[t["primary"]]
        row["ku_id"], row["process_ref"] = t["ku"], PROCESS_REF
        row["resolution_note"] += f" S4 registration ({DATE}): group {t['group']} -> {t['ku']}; source-backed person identity registration; direct S2 relation candidates remain for S6."
        if t.get("prior_candidate_pages"):
            row["resolution_note"] += (
                f" S4 locator reconciliation ({DATE}): candidate snapshot index_page_range={t['prior_candidate_pages']} "
                f"did not match current source index {t['entry']} Page Numbers={t['expected_pages']}; "
                "the derived candidate locator was synchronized to the current index row; original S3 identity decision and group are unchanged."
            )
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
        planned_accepted = template.helper.base.insert_accepted(planned_accepted, t["card"])
    planned_manifest.sort(key=lambda r: r["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {k: sum(r[k] for r in stats.values()) for k in next(iter(stats.values()))}
    assert totals["registered_groups"] == before_totals["registered_groups"] + 5
    assert totals["registered_members"] == before_totals["registered_members"] + 5
    assert totals["pending_groups"] == before_totals["pending_groups"] - 5
    assert totals["pending_members"] == before_totals["pending_members"] - 5
    assert len(planned_manifest) == len(manifest) + 5

    additions, card_tables = template.extract_card_fields(cards)
    name_fields = sum(len(t["name_rows"]) for t in TARGETS)
    assert card_tables == 5 and len(additions) == name_fields and all(r.get("evidence_status") == "source_backed" for r in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id", "")) for r in existing}
    existing_ids = {r.get("enrichment_id", "") for r in existing}
    max_id = max((int(m.group(1)) for v in existing_ids if (m := re.fullmatch(r"enr-(\d+)", v))), default=0)
    for i, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id+i:05d}"
        assert (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in existing_ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(r, ensure_ascii=False) for r in additions) + "\n"

    process_text = template.helper.base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Le Nain、Le Vau、Lelli、Lely与Lorca（{DATE}）\n\n"
    for t in TARGETS:
        process_text += f"- `{t['primary']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}（页码{t['pages']}）与书内页段构成身份锚点；直接S2关系候选{', '.join(t['relations'])}留待S6裁决，不登记正式关系。\n"
    process_text += (
        "- 定位值差异处理：`cand-1377`原候选快照为`133, 184`，当前`L.csv#34`原行为`122, 184`；"
        "`cand-1384`原候选快照为`135n`，当前`L.csv#41`原行为`122n`。按`build_entity_candidates.py`的字段生成规则，"
        "仅将`entity-candidates.csv`中的派生`index_page_range`同步到当前索引原行；原索引文件未改，旧值与更正理由保留在本记录及对应alignment resolution_note中，S3身份分组不变。\n"
    )
    relation_count = sum(len(t["relations"]) for t in TARGETS)
    process_text += (
        f"\n本批登记5个S3 new人物组、5条候选映射和{name_fields}条source_backed名称字段；{relation_count}条直接S2关系候选留待S6。"
        "保留Le Nain影响表述的未指明来源、Lelli正文异拼、Lely的推测及目录归属限定、Lorca书信转引状态。本批无外部身份行、无正式关系、无来源登记变更。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接端点登记：Le Nain、Le Vau、Lelli、Lely与Lorca（{DATE}）\n\n"
        "登记Louis Le Nain、Louis Le Vau、Ercole Lelli、Sir Peter Lely与Bernardino Lorca五个人物组。"
        f"本批5条候选映射、10条source_backed名称字段和{relation_count}条直接S2关系候选；来源限定与不确定性均保留，关系待S6，未新增正式边。"
        "并将cand-1377、cand-1384的派生索引页码从旧快照同步至当前L.csv原行，保留前后值及S3分组不变的依据。"
        f"KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-le-nain-lorca-") as td:
        temp = Path(td)
        a_stage, m_stage, c_stage = temp / "alignment.csv", temp / "ku-manifest.csv", temp / "entity-candidates.csv"
        sync.write_csv(a_stage, alignment_fields, planned_alignments)
        sync.write_csv(m_stage, manifest_fields, planned_manifest)
        sync.write_csv(c_stage, candidate_fields, planned_candidates)
        writes = {
            ALIGNMENT: a_stage.read_bytes(), MANIFEST: m_stage.read_bytes(), ENTITY: c_stage.read_bytes(),
            ENRICHMENT: template.with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: template.with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: template.with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: template.with_bom(result_text + "\n", RESULT.read_bytes()),
        }
        for t in TARGETS: writes[ROOT / t["card"]] = template.with_bom(cards[t["card"]])

    if args.dry_run:
        print(f"S4 dry-run passed: groups=5; candidate_mappings=5; name_fields={name_fields}; direct_relation_candidates={relation_count}.")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
        print("candidate locator reconciliations=2: cand-1377 133, 184->122, 184; cand-1384 135n->122n")
        print("formal_relations_added=0; candidate_backlog_changed=0; sources_registry_changed=0; no files changed")
        return 0
    originals = {p: p.read_bytes() if p.exists() else None for p in writes}
    try:
        for p, content in writes.items(): template.atomic_write(p, content)
    except Exception:
        for p, content in originals.items():
            if content is None:
                if p.exists(): p.unlink()
            else: template.atomic_write(p, content)
        raise
    print(f"applied: groups=5; candidate_mappings=5; name_fields={name_fields}; relation_candidates={relation_count}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
