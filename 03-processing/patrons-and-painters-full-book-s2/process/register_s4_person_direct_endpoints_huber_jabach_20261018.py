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
ANCHOR = "s4-person-direct-endpoints-huber-imperiali-jabach-james-johann-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [
    {
        "primary": "cand-1306", "members": ["cand-1306"], "expected_name": "Huber, Jean", "expected_pages": "",
        "group": "new-person:huber-jean-79331e446d", "ku": "units/persons/jean-huber", "card": "04-knowledge/units/persons/jean-huber.md",
        "name_zh": "让·于贝尔", "name_en": "Jean Huber",
        "name_rows": [("索引名", "Huber, Jean", "S1（索引H.csv#22）"), ("正文姓名形式", "Huber", "S2（第15章p.370）")],
        "sources": [src("第15章第II节；印刷页370", "Haskell称Querini宅邸内陈列有Huber从多个角度绘制的Voltaire头像版画。", "Engravings designed to bring home the point hung round the walls, among them one by Huber of the head of Voltaire taken from a number of different angles.", "02-sources/02-Markdown/15_CHP-15_sec_ii.md", "line 67; print p.370")],
        "zh": "本卡登记索引H.csv#22的Jean Huber。第15章p.370以姓氏Huber称其为一幅Voltaire头像版画的创作者；本卡不据此补写其他生平或作品归属。",
        "en": "This card registers Jean Huber under index H.csv#22. Chapter 15, p.370, names him by surname as the maker of an engraving of Voltaire’s head; no further biography or attribution is added.",
        "context_zh": "Haskell将这幅版画置于Querini宅邸的陈设语境中。直接S2候选st-chp15-p370-huber-engraving-created-by-huber保留待S6裁决。",
        "context_en": "Haskell places the engraving in the context of the decoration of Querini’s house. The direct S2 candidate st-chp15-p370-huber-engraving-created-by-huber remains for S6 review.",
        "relations": ["st-chp15-p370-huber-engraving-created-by-huber"],
        "endpoints": {"st-chp15-p370-huber-engraving-created-by-huber": "created_by"},
    },
    {
        "primary": "cand-1312", "members": ["cand-1312"], "expected_name": "Imperiali, Francesco", "expected_pages": "288n",
        "group": "new-person:francesco-imperiali-98d434bd1c", "ku": "units/persons/francesco-imperiali", "card": "04-knowledge/units/persons/francesco-imperiali.md",
        "name_zh": "弗朗切斯科·因佩里亚利", "name_en": "Francesco Imperiali",
        "name_rows": [("索引名", "Imperiali, Francesco", "S1（索引I.csv#3）"), ("正文姓名形式", "Francesco Imperiali of Rome", "S2（第10章p.288注2）")],
        "sources": [src("第10章导论注2；印刷页288", "Haskell称Francesco Imperiali of Rome绘制了King George I的纪念碑，并说明其中一个版本属于Lord Kemsley。", "Francesco Imperiali of Rome painted the monument to King George I, a version of which belongs to Lord Kemsley", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 541; print p.288 n.2")],
        "zh": "本卡登记索引I.csv#3及第10章p.288注2所称Francesco Imperiali of Rome。原书将其与King George I纪念碑相联系；本卡只保存这项来源归属，不扩展作者身份或作品版本信息。",
        "en": "This card registers Francesco Imperiali of Rome as named in index I.csv#3 and chapter 10, p.288 n.2. The book associates him with the monument to King George I; the card preserves that source attribution without extending it to further biographical or version claims.",
        "context_zh": "注2称纪念碑的一个版本属于Lord Kemsley。直接S2候选st-chp10-p288-n02-imperiali-monument留待S6裁决，版本与所有权语境仍以原书为限。",
        "context_en": "Note 2 says that one version of the monument belonged to Lord Kemsley. The direct S2 candidate st-chp10-p288-n02-imperiali-monument remains for S6 review, with version and ownership context limited to the book.",
        "relations": ["st-chp10-p288-n02-imperiali-monument"],
        "endpoints": {"st-chp10-p288-n02-imperiali-monument": "imperiali_painted_monument_to_king_george_i"},
    },
    {
        "primary": "cand-1316", "members": ["cand-1316"], "expected_name": "Jabach, Everard", "expected_pages": "184",
        "group": "new-person:everard-jabach-3e5e428848", "ku": "units/persons/everard-jabach", "card": "04-knowledge/units/persons/everard-jabach.md",
        "name_zh": "埃弗哈德·雅巴赫", "name_en": "Everard Jabach",
        "name_rows": [("索引名", "Jabach, Everard", "S1（索引J，K.csv#0）"), ("正文姓名形式", "Everard Jabach", "S2（第7章p.184）")],
        "sources": [src("第7章第I节；印刷页184", "Haskell称Mazarin委托德国银行家Everard Jabach替他购买其前任对手收藏中的若干绘画。", "Mazarin managed to take an interest in these affairs across the Channel and commissioned the rich German banker Everard Jabach to buy for him a number of pictures from the collection of his former rival.", "02-sources/02-Markdown/07_CHP-7_sec_i.md", "line 171; print p.184")],
        "zh": "本卡登记索引J，K.csv#0所列Everard Jabach。第7章p.184称Mazarin委托他购买若干绘画；“德国银行家”及委托事项均保留为Haskell在该段的表述。",
        "en": "This card registers Everard Jabach under index J, K.csv#0. Chapter 7, p.184, says Mazarin commissioned him to buy a number of pictures; the description “German banker” and the commission remain attributed to Haskell’s account.",
        "context_zh": "书中将此次购买置于Charles I画廊出售后的跨海艺术交易语境。直接S2候选st-chp7-p184-i02留待S6裁决；不据此判定具体作品或购买结果。",
        "context_en": "The book places the purchase in the cross-Channel art trade following the sale of Charles I’s picture gallery. The direct S2 candidate st-chp7-p184-i02 remains for S6 review; no specific pictures or purchase outcome are inferred.",
        "relations": ["st-chp7-p184-i02"],
        "endpoints": {"st-chp7-p184-i02": "mazarin_commissioned_jabach_to_buy_collection_pictures"},
    },
    {
        "primary": "cand-1318", "members": ["cand-1318"], "expected_name": "James III of England", "expected_pages": "203",
        "group": "new-person:england-iii-james-of-d1d84625ab", "ku": "units/persons/james-iii-of-england", "card": "04-knowledge/units/persons/james-iii-of-england.md",
        "name_zh": "英格兰的詹姆斯三世", "name_en": "James III of England",
        "name_rows": [("索引名", "James III of England", "S1（索引J，K.csv#2）"), ("正文称谓", "the exiled ‘James III’", "S2（第8章p.203）")],
        "sources": [src("第8章第I节；印刷页203", "Haskell称博洛尼亚商人Giovanni Antonio Belloni曾慷慨接待流亡中的“James III”。", "Giovanni Antonio Belloni, for instance, who gave splendid hospitality to the exiled ‘James III’", "02-sources/02-Markdown/08_CHP-8_sec_i.md", "line 8; print p.203")],
        "zh": "本卡登记索引J，K.csv#2所列James III of England。第8章p.203以流亡中的“James III”称呼Belloni接待的对象；本卡保留原书称谓，不扩展为未由本轮证据确认的姓名或头衔。",
        "en": "This card registers James III of England under index J, K.csv#2. Chapter 8, p.203, calls Belloni’s guest the exiled “James III”; the card retains the book’s form and adds no name or title not established in this review.",
        "context_zh": "Haskell称Belloni向流亡中的James III提供款待。直接S2候选st-chp8-p203-belloni-hospitality-james-iii留待S6裁决；款待关系尚未登记为正式边。",
        "context_en": "Haskell says Belloni gave hospitality to the exiled James III. The direct S2 candidate st-chp8-p203-belloni-hospitality-james-iii remains for S6 review; no formal hospitality edge is registered.",
        "relations": ["st-chp8-p203-belloni-hospitality-james-iii"],
        "endpoints": {"st-chp8-p203-belloni-hospitality-james-iii": "hosted_person"},
    },
    {
        "primary": "cand-1324", "members": ["cand-1324"], "expected_name": "Johann Georg III of Saxony", "expected_pages": "194",
        "group": "new-person:georg-iii-johann-of-saxony-d06916a347", "ku": "units/persons/johann-georg-iii-of-saxony", "card": "04-knowledge/units/persons/johann-georg-iii-of-saxony.md",
        "name_zh": "萨克森的约翰·格奥尔格三世", "name_en": "Johann Georg III of Saxony",
        "name_rows": [("索引名", "Johann Georg III of Saxony", "S1（索引J，K.csv#8）"), ("正文姓名形式", "Johann Georg III of Saxony", "S2（第7章p.194）")],
        "sources": [src("第7章第IV节；印刷页194", "Haskell称截至1669年Johann Georg III of Saxony雇用了意大利画家Stefano Cadani在Dresden工作。", "By 1669 Johann Georg III of Saxony was employing an Italian painter called Stefano Cadani at Dresden", "02-sources/02-Markdown/07_CHP-7_sec_iv.md", "line 24; print p.194")],
        "zh": "本卡登记索引J，K.csv#8及第7章p.194所称Johann Georg III of Saxony。Haskell将其与截至1669年Stefano Cadani在Dresden的受雇情况相联系；本卡不扩写其他宫廷或艺术赞助事实。",
        "en": "This card registers Johann Georg III of Saxony as named in index J, K.csv#8 and chapter 7, p.194. Haskell connects him with Stefano Cadani’s employment at Dresden by 1669; no further court or patronage facts are added.",
        "context_zh": "该句称Cadani为意大利画家，随后另提Arrighini为Georg Wilhelm建造剧院。直接S2候选st-chp7-p194-cadani-employed-dresden留待S6裁决。",
        "context_en": "The sentence calls Cadani an Italian painter and then separately mentions Arrighini building a theatre for Georg Wilhelm. The direct S2 candidate st-chp7-p194-cadani-employed-dresden remains for S6 review.",
        "relations": ["st-chp7-p194-cadani-employed-dresden"],
        "endpoints": {"st-chp7-p194-cadani-employed-dresden": "employed_italian_painter_at_dresden"},
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register five S3 person groups used as direct S2 relation endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    template.TARGETS = TARGETS
    template.DATE, template.ANCHOR, template.PROCESS_REF = DATE, ANCHOR, PROCESS_REF
    sync = template.helper.base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    main_rows = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    main_by_id = {row["candidate_id"]: row for row in main_rows}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}

    for target in TARGETS:
        candidate = candidate_by_id[target["primary"]]
        target["entry"] = candidate["index_entry_id"]
        target["index_name"] = candidate["canonical_name"]
        target["pages"] = candidate["index_page_range"]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("canonical_name") == target["expected_name"]
        assert candidate.get("index_page_range") == target["expected_pages"]
        for cid in target["members"]:
            row = main_by_id[cid]
            assert row.get("decision") == "new"
            assert sync.get_group(row.get("resolution_note", "")) == target["group"]
            assert not row.get("ku_id") or row.get("ku_id") == target["ku"]
        members = [row["candidate_id"] for row in main_rows if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == target["group"]]
        assert members == target["members"], (target["group"], members)
        index_file, _ = target["entry"].split("#", 1)
        hits = [r for r in template.helper.base.read_index_rows(index_file) if r.get("Main Entry") == target["index_name"] and r.get("Page Numbers") == target["pages"]]
        assert len(hits) == 1, (target["entry"], hits)
        direct = {
            r["statement_id"]: r for r in statements
            if (r.get("qualifiers") or {}).get("relation_candidate") is True
            and (r.get("subject_candidate_id") == target["primary"] or r.get("object_candidate_id") == target["primary"])
        }
        assert set(direct) == set(target["endpoints"]), (target["primary"], sorted(direct), sorted(target["endpoints"]))
        for statement_id, predicate in target["endpoints"].items():
            assert direct[statement_id].get("predicate") == predicate
        for item in target["sources"]:
            source_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            normalized = re.sub(r"\s+", " ", source_text)
            assert re.sub(r"\s+", " ", item["quote"]) in normalized, (target["primary"], item["span"])
        card_path = ROOT / target["card"]
        mapped = main_by_id[target["primary"]].get("ku_id") == target["ku"]
        assert (target["ku"] in manifest_by_ku) == (target["card"] in accepted_paths) == card_path.exists() == mapped

    cards = {target["card"]: template.make_card(target) for target in TARGETS}
    all_registered = all(all(main_by_id[cid].get("ku_id") == target["ku"] for cid in target["members"]) for target in TARGETS)
    if all_registered:
        for target in TARGETS:
            assert (ROOT / target["card"]).read_text(encoding="utf-8-sig") == cards[target["card"]]
        print("ALREADY REGISTERED: all five person groups and their candidate mappings are present.")
        return 0
    assert not any(main_by_id[cid].get("ku_id") for target in TARGETS for cid in target["members"]), "partial registration requires explicit reconciliation"

    before_stats = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for target in TARGETS:
        row = planned_by_id[target["primary"]]
        row["ku_id"], row["process_ref"] = target["ku"], PROCESS_REF
        row["resolution_note"] += f" S4 registration ({DATE}): group {target['group']} -> {target['ku']}; source-backed person identity registration; direct S2 relation candidates remain for S6."
        planned_manifest.append({"ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"], "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"]})
        planned_accepted = template.helper.base.insert_accepted(planned_accepted, target["card"])
    planned_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == before_totals["registered_members"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    additions, cards_with_tables = template.extract_card_fields(cards)
    expected_name_fields = sum(len(t["name_rows"]) for t in TARGETS)
    assert cards_with_tables == len(TARGETS) and len(additions) == expected_name_fields
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Huber、Imperiali、Jabach、James III与Johann Georg III（{DATE}）\n\n"
    for t in TARGETS:
        process_text += f"- `{t['primary']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}与所列书内页段构成身份及来源锚点；直接S2关系候选{', '.join(t['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    relation_count = sum(len(t["relations"]) for t in TARGETS)
    process_text += (
        f"\n本批登记{len(TARGETS)}个S3 new人物组、{len(TARGETS)}条候选映射和{expected_name_fields}条source_backed名称字段；"
        f"{relation_count}条直接S2关系候选留待S6。本批无外部身份行、无正式关系、无来源登记变更。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为"
        f"{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接端点登记：Huber、Imperiali、Jabach、James III与Johann Georg III（{DATE}）\n\n"
        "登记Jean Huber、Francesco Imperiali、Everard Jabach、James III of England与Johann Georg III of Saxony五个人物组。"
        f"本批5条候选映射、10条source_backed名称字段和{relation_count}条直接S2关系候选；均保留原书来源限定，关系待S6，未新增正式边。"
        f"KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    sync = template.helper.base.sync
    with tempfile.TemporaryDirectory(prefix="pnp-s4-huber-jabach-persons-") as temp_name:
        temp = Path(temp_name)
        a_stage, m_stage = temp / "alignment.csv", temp / "ku-manifest.csv"
        sync.write_csv(a_stage, alignment_fields, planned_alignments)
        sync.write_csv(m_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: a_stage.read_bytes(), MANIFEST: m_stage.read_bytes(),
            ENRICHMENT: template.with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: template.with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: template.with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: template.with_bom(result_text + "\n", RESULT.read_bytes()),
        }
        for t in TARGETS:
            writes[ROOT / t["card"]] = template.with_bom(cards[t["card"]])

    if args.dry_run:
        print(f"S4 dry-run passed: groups={len(TARGETS)}; candidate_mappings={len(TARGETS)}; name_fields={expected_name_fields}; direct_relation_candidates={relation_count}.")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
        print("formal_relations_added=0; candidate_backlog_changed=0; sources_registry_changed=0; no files changed")
        return 0

    originals = {path: path.read_bytes() if path.exists() else None for path in writes}
    try:
        for path, content in writes.items():
            template.atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            if content is None:
                if path.exists(): path.unlink()
            else: template.atomic_write(path, content)
        raise
    print(f"applied: groups={len(TARGETS)}; candidate_mappings={len(TARGETS)}; name_fields={expected_name_fields}; relation_candidates={relation_count}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
