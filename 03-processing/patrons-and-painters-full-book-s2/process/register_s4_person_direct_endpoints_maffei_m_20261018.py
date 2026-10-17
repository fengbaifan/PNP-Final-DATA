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
MANIFEST = TABLES / "ku-manifest.csv"
ENRICHMENT = TABLES / "enrichment.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s4-person-direct-endpoints-maffei-m-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [
    {
        "primary": "cand-1486", "members": ["cand-1486"], "expected_name": "Maffei, Francesco", "expected_pages": "232, 248",
        "group": "new-person:francesco-maffei-fbe66c73c0", "ku": "units/persons/francesco-maffei", "card": "04-knowledge/units/persons/francesco-maffei.md",
        "name_zh": "弗朗切斯科·马费伊", "name_en": "Francesco Maffei",
        "name_rows": [("索引名", "Maffei, Francesco", "S1（索引M.csv#23）"), ("正文指称", "Maffei", "S2（第8章p.232；第9章p.248）")],
        "sources": [
            src("第8章第II节；印刷页232", "Haskell记Ferdinand初次看到一件Maffei作品并赞赏其颜料肌理；作品未具名。", "He sees a Maffei for the first time and is delighted with its ‘bellissimo impasto’", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "line 254; print p.232"),
            src("第9章导论；印刷页248", "Haskell称Maffei等人以系列画布描绘Este、Rovigo及其他省份教堂中的威尼斯总督。", "artists like Maffei, in series of canvases which filled churches in Este, Rovigo and other provinces, portrayed Venetian governors standing somewhat awkwardly in the middle of complex allegorical trappings.", "02-sources/02-Markdown/09_CHP-9_intro.md", "lines 39-40; print p.248"),
        ],
        "zh": "本卡登记索引M.csv#23所列Francesco Maffei（中文显示名为本项目工作音译）。第8章p.232记Ferdinand初次看到一件Maffei作品并赞其颜料肌理；作品未具名。第9章p.248称Maffei等人以系列画布描绘Este、Rovigo及其他省份教堂中的威尼斯总督，具体作品未列出。",
        "en": "This card records Francesco Maffei under index M.csv#23; the Chinese display name is a working transliteration. Chapter 8, p.232, says Ferdinand saw a Maffei for the first time and admired its impasto; the work is not identified. Chapter 9, p.248, says artists such as Maffei depicted Venetian governors in series of canvases for churches in Este, Rovigo, and other provinces; the specific works are not listed.",
        "context_zh": "两章的Maffei指称按同一S3候选组登记；p.232作品未具名，相关内容端点cand-8150仍为未决术语候选。",
        "context_en": "The two chapter references to Maffei are registered under the same S3 candidate group. The p.232 work is unnamed, and the related content endpoint cand-8150 remains an undecided term candidate.",
        "relations": ["st-chp9-p248-maffei-governor-canvases"],
        "endpoints": {"st-chp9-p248-maffei-governor-canvases": "maffei_canvases_portrayed_venetian_governors_in_provincial_churches"},
    },
    {
        "primary": "cand-1488", "members": ["cand-1488"], "expected_name": "Magalotti, Cardinal Lorenzo", "expected_pages": "31, 42",
        "group": "new-person:lorenzo-magalotti-fa04976cc4", "ku": "units/persons/lorenzo-magalotti", "card": "04-knowledge/units/persons/lorenzo-magalotti.md",
        "name_zh": "洛伦佐·马加洛蒂", "name_en": "Lorenzo Magalotti",
        "name_rows": [("索引名", "Magalotti, Cardinal Lorenzo", "S1（索引M.csv#25）"), ("正文姓名形式", "Lorenzo Magalotti", "S2（第2章p.31）")],
        "sources": [
            src("第2章第II节；印刷页31", "Haskell在Urban VIII任命亲属为枢机的叙述中列出Lorenzo Magalotti。", "as did his other brother’s brother-in-law Lorenzo Magalotti", "02-sources/02-Markdown/02_CHP-2_sec_ii.md", "line 3; print p.31"),
            src("第2章第II节；印刷页42", "Haskell称Cardinal Magalotti为献给圣劳伦斯的小堂积聚宝石和大理石。", "In Rome Cardinal Magalotti accumulated precious stones and marbles for one dedicated to St Lawrence", "02-sources/02-Markdown/02_CHP-2_sec_ii.md", "lines 134-135; print p.42"),
        ],
        "zh": "本卡登记索引M.csv#25所列Lorenzo Magalotti（中文显示名为本项目工作音译）。第2章p.31将其列入Urban VIII时期任命枢机的相关叙述；p.42称Cardinal Magalotti为献给圣劳伦斯的小堂积聚宝石和大理石。",
        "en": "This card records Lorenzo Magalotti under index M.csv#25; the Chinese display name is a working transliteration. Chapter 2, p.31, names him in Haskell’s account of Urban VIII’s cardinal appointments; p.42 says Cardinal Magalotti accumulated precious stones and marbles for a chapel dedicated to St Lawrence.",
        "context_zh": "p.31端点cand-3104映射到既有人物[乌尔班八世（Urban VIII）](urbano-viii.md)；p.42对象cand-4529仍为待登记地点候选。",
        "context_en": "The p.31 endpoint cand-3104 maps to the existing person [Urban VIII](urbano-viii.md); the p.42 object cand-4529 remains an unregistered place candidate.",
        "relations": ["st-chp2-sec-ii-l3-8-magalotti-cardinal", "st-chp2-secii-l127-139-magalotti-chapel-materials"],
        "endpoints": {
            "st-chp2-sec-ii-l3-8-magalotti-cardinal": "appointed_to_cardinalate",
            "st-chp2-secii-l127-139-magalotti-chapel-materials": "chapel_materials_accumulated_reported",
        },
    },
    {
        "primary": "cand-1492", "members": ["cand-1492"], "expected_name": "Magnasco, Alessandro", "expected_pages": "404",
        "group": "new-person:alessandro-magnasco-ba9ee3bdc8", "ku": "units/persons/alessandro-magnasco", "card": "04-knowledge/units/persons/alessandro-magnasco.md",
        "name_zh": "亚历山德罗·马格纳斯科", "name_en": "Alessandro Magnasco",
        "name_rows": [("索引名", "Magnasco, Alessandro", "S1（索引M.csv#29）"), ("正文姓名形式", "Magnasco", "S2（第20章后记p.404）")],
        "sources": [src("第20章后记；印刷页404", "Haskell称Chiarini与Strocchi发表的库存资料显示Grand Prince Ferdinand曾雇用画家Magnasco；作者称其赞助有限，并保留自身关于王子品味的推断。", "Ferdinand did (as I had so much hoped and expected but could never establish) employ Magnasco, a painter whose talents must surely have been congenial to him, and the significance of this (admittedly limited) patronage has been stressed by Guelfi in her monograph on the artist.", "02-sources/02-Markdown/20_CHP-20Postscript.md", "lines 127-131; print p.404")],
        "zh": "本卡登记索引M.csv#29所列Alessandro Magnasco（中文显示名为本项目工作音译）。第20章后记p.404称Chiarini与Strocchi发表的库存资料显示Grand Prince Ferdinand曾雇用画家Magnasco；Haskell称这项赞助“有限”，并将王子可能欣赏其才能作为作者推断。库存原件及Guelfi专著未在本批独立查阅。",
        "en": "This card records Alessandro Magnasco under index M.csv#29; the Chinese display name is a working transliteration. The postscript, p.404, says inventories published by Chiarini and Strocchi showed that Grand Prince Ferdinand employed the painter Magnasco. Haskell calls the patronage limited and presents the prince’s likely appreciation of Magnasco’s talents as his own inference. The inventories and Guelfi’s monograph were not independently consulted in this batch.",
        "context_zh": "端点cand-1609映射到既有人物[托斯卡纳大亲王费迪南多（Grand Prince Ferdinand of Tuscany）](ferdinand-grand-prince-tuscany.md)；不将Haskell的推断转写为已核事实。",
        "context_en": "Endpoint cand-1609 maps to the existing person [Grand Prince Ferdinand of Tuscany](ferdinand-grand-prince-tuscany.md); Haskell’s inference is not recast as a verified fact.",
        "relations": ["st-chp20-p404-inventories-magnasco-limited-patronage"],
        "endpoints": {"st-chp20-p404-inventories-magnasco-limited-patronage": "inventories_support_employment_of_magnasco_and_later_assessment"},
    },
    {
        "primary": "cand-1493", "members": ["cand-1493"], "expected_name": "Magni, Pietro", "expected_pages": "216",
        "group": "new-person:magni-pietro-d0f4dde5f1", "ku": "units/persons/pietro-magni", "card": "04-knowledge/units/persons/pietro-magni.md",
        "name_zh": "彼得罗·马尼", "name_en": "Pietro Magni",
        "name_rows": [("索引名", "Magni, Pietro", "S1（索引M.csv#30）"), ("正文姓名形式", "Pietro Magni", "S2（第8章p.216）")],
        "sources": [src("第8章第II节；印刷页216", "Haskell称1656年委员会委托那不勒斯画家Pietro Magni试画一幅，并称他当时为Mantua侯爵工作。", "in 1656 they commissioned a Neapolitan painter, Pietro Magni, who was then working for the Marquis of Mantua, to produce one picture for the site as an experiment, with the possibility, should it prove satisfactory, of being given the whole job.", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "line 25; print p.216")],
        "zh": "本卡登记索引M.csv#30所列Pietro Magni（中文显示名为本项目工作音译）。第8章p.216称他是那不勒斯画家，1656年为曼图亚侯爵工作时，受委托为贝加莫教堂试画一幅作品；后续是否取得整项装饰委托按Haskell所述保留，不补充作品题名或履历。",
        "en": "This card records Pietro Magni under index M.csv#30; the Chinese display name is a working transliteration. Chapter 8, p.216, describes him as a Neapolitan painter working for the Marquis of Mantua in 1656, when he was commissioned to make one experimental picture for a church in Bergamo. The account of whether he received the larger decoration commission remains limited to Haskell’s statement; no work title or further biography is supplied.",
        "context_zh": "另一端cand-1525仍为未登记的新人物组；不把试画扩写为完整委托或已完成作品。",
        "context_en": "The other endpoint, cand-1525, remains an unregistered new person group; the experiment is not expanded into a full commission or a completed work.",
        "relations": ["st-chp8-p216-magni-working-for-marquis-mantua"],
        "endpoints": {"st-chp8-p216-magni-working-for-marquis-mantua": "working_for_marquis_of_mantua_in_1656"},
    },
    {
        "primary": "cand-1495", "members": ["cand-1495"], "expected_name": "Maidalchini, Francesco", "expected_pages": "147",
        "group": "new-person:francesco-maidalchini-e5968ef278", "ku": "units/persons/francesco-maidalchini", "card": "04-knowledge/units/persons/francesco-maidalchini.md",
        "name_zh": "弗朗切斯科·马伊达尔基尼", "name_en": "Francesco Maidalchini",
        "name_rows": [("索引名", "Maidalchini, Francesco", "S1（索引M.csv#32）"), ("正文姓名形式", "Francesco Maidalchini", "S2（第6章p.147）")],
        "sources": [src("第6章第I节；印刷页147", "Haskell称17岁的Francesco Maidalchini由姑母Donna Olimpia选为继Camillo之后的papal nephew，并评价他未能对罗马文化产生影响。", "the 17-y earold Francesco Maidalchini who was chosen by his aunt Donna Olimpia to supersede Camillo as papal nephew was clearly not destined to make an impact on Roman culture.", "02-sources/02-Markdown/06_CHP-6_sec_i.md", "lines 17-18; print p.147")],
        "zh": "本卡登记索引M.csv#32所列Francesco Maidalchini（中文显示名为本项目工作音译）。第6章p.147称Haskell所述的17岁Francesco由姑母[Donna Olimpia（Olimpia Maidalchini）](olimpia-maidalchini.md)选为继Camillo之后的papal nephew；作者认为他未能对罗马文化产生影响。此评价保留为Haskell判断。",
        "en": "This card records Francesco Maidalchini under index M.csv#32; the Chinese display name is a working transliteration. Chapter 6, p.147, says Haskell’s 17-year-old Francesco was chosen by his aunt [Donna Olimpia (Olimpia Maidalchini)](olimpia-maidalchini.md) to succeed Camillo as papal nephew; the author judges that he did not affect Roman culture. This assessment remains attributed to Haskell.",
        "context_zh": "端点cand-1496映射至既有人物Olimpia Maidalchini；本卡只提供身份导航。",
        "context_en": "Endpoint cand-1496 maps to the existing person Olimpia Maidalchini; this card provides identity navigation only.",
        "relations": ["st-chp6-p147-francesco-maidalchini-selected"],
        "endpoints": {"st-chp6-p147-francesco-maidalchini-selected": "selects-nephew-to-supersede-camillo"},
    },
]


def make_batch_card(target: dict) -> str:
    card = template.make_card(target)
    relations = ", ".join(target["relations"])
    if relations:
        zh_display = f"直接S2候选（待S6）：{relations}。"
        en_display = f"Direct S2 relation candidates pending individual review in S6: {relations}."
    else:
        zh_display = "当前未有直接S2关系候选映射到此人物端点。"
        en_display = "S2 does not currently map this person as a direct relation-candidate endpoint."
    old = f"**English:** {zh_display}\n"
    new = f"**English:** {en_display}\n"
    assert old in card
    return card.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register five source-backed S3 person groups with direct S2 relation candidates.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--refresh-cards", action="store_true")
    args = parser.parse_args()
    template.TARGETS = TARGETS
    template.DATE, template.ANCHOR, template.PROCESS_REF = DATE, ANCHOR, PROCESS_REF
    sync = template.helper.base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    main_rows = [r for r in alignments if r.get("candidate_id") and not r.get("external_source")]
    main_by_id = {r["candidate_id"]: r for r in main_rows}
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

    for target in TARGETS:
        candidate = candidate_by_id[target["primary"]]
        target["entry"], target["index_name"], target["pages"] = candidate["index_entry_id"], candidate["canonical_name"], candidate["index_page_range"]
        assert candidate.get("suggested_type") == "person"
        assert (candidate.get("canonical_name"), candidate.get("index_page_range")) == (target["expected_name"], target["expected_pages"])
        row = main_by_id[target["primary"]]
        assert row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == target["group"]
        assert not row.get("ku_id") or row.get("ku_id") == target["ku"]
        members = [r["candidate_id"] for r in main_rows if r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == target["group"]]
        assert members == target["members"]
        index_file, _ = target["entry"].split("#", 1)
        index_hits = [r for r in template.helper.base.read_index_rows(index_file) if r.get("Main Entry") == target["index_name"] and r.get("Page Numbers") == target["pages"]]
        assert len(index_hits) == 1
        direct = {r["statement_id"]: r for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == target["primary"] or r.get("object_candidate_id") == target["primary"])}
        assert set(direct) == set(target["endpoints"]), (target["primary"], sorted(direct), sorted(target["endpoints"]))
        for statement_id, predicate in target["endpoints"].items():
            assert direct[statement_id].get("predicate") == predicate
        for item in target["sources"]:
            source_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", source_text), (target["primary"], item["span"])
        path = ROOT / target["card"]
        mapped = row.get("ku_id") == target["ku"]
        assert (target["ku"] in manifest_by_ku) == (target["card"] in accepted_paths) == path.exists() == mapped

    cards = {target["card"]: make_batch_card(target) for target in TARGETS}
    all_registered = all(main_by_id[target["primary"]].get("ku_id") == target["ku"] for target in TARGETS)
    if all_registered:
        if args.refresh_cards:
            for target in TARGETS:
                template.atomic_write(ROOT / target["card"], template.with_bom(cards[target["card"]]))
            print("refreshed five cards: removed repeated S6 context and restored English relation summaries")
            return 0
        for target in TARGETS:
            assert (ROOT / target["card"]).read_text(encoding="utf-8-sig") == cards[target["card"]]
        print("ALREADY REGISTERED: all five person groups and their source-backed name fields are recorded.")
        return 0
    assert not any(main_by_id[target["primary"]].get("ku_id") for target in TARGETS), "partial registration requires explicit reconciliation"

    before = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(row[key] for row in before.values()) for key in next(iter(before.values()))}
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest, planned_accepted = list(manifest), list(accepted_lines)
    for target in TARGETS:
        row = planned_by_id[target["primary"]]
        row["ku_id"], row["process_ref"] = target["ku"], PROCESS_REF
        row["resolution_note"] += f" S4 registration ({DATE}): group {target['group']} -> {target['ku']}; source-backed person identity registration; direct S2 relation candidates remain for S6."
        planned_manifest.append({"ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"], "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"]})
        planned_accepted = template.helper.base.insert_accepted(planned_accepted, target["card"])

    planned_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    batch_size = len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + batch_size
    assert totals["registered_members"] == before_totals["registered_members"] + batch_size
    assert totals["pending_groups"] == before_totals["pending_groups"] - batch_size
    assert totals["pending_members"] == before_totals["pending_members"] - batch_size
    assert len(planned_manifest) == len(manifest) + batch_size

    additions, card_tables = template.extract_card_fields(cards)
    name_fields = sum(len(target["name_rows"]) for target in TARGETS)
    assert card_tables == batch_size and len(additions) == name_fields and all(row.get("evidence_status") == "source_backed" for row in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) for row in existing}
    existing_ids = {row.get("enrichment_id", "") for row in existing}
    max_id = max((int(match.group(1)) for value in existing_ids if (match := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for i, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id+i:05d}"
        assert (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in existing_ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in additions) + "\n"

    process_text = template.helper.base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Maffei、Magalotti、Magnasco、Magni与Maidalchini（{DATE}）\n\n"
    for target in TARGETS:
        process_text += f"- `{target['primary']}`（`{target['group']}`）→ [{target['name_zh']}（{target['name_en']}）](../../../04-knowledge/{target['ku']}.md)。索引{target['entry']}（页码{target['pages']}）与对应书内页段支持source-local人物登记；直接S2关系候选{', '.join(target['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    process_text += (
        f"\n本批登记{batch_size}个S3 new人物组、{batch_size}条候选映射和{name_fields}条source_backed名称字段；"
        f"{sum(len(target['relations']) for target in TARGETS)}条直接S2关系候选留待S6。"
        "Maffei两章指称、Magalotti两处正文形式均按各自既有身份组处理；Magalotti与Maidalchini的相关已登记人物入口只作导航。"
        "本批未新增外部身份行、正式关系、来源登记或S2断言。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接端点登记：Maffei、Magalotti、Magnasco、Magni与Maidalchini（{DATE}）\n\n"
        f"登记Francesco Maffei、Lorenzo Magalotti、Alessandro Magnasco、Pietro Magni与Francesco Maidalchini五个人物组；"
        f"本批{batch_size}条候选映射、{name_fields}条source_backed名称字段及{sum(len(target['relations']) for target in TARGETS)}条直接S2关系候选。"
        f"关系均留待S6，未新增正式边；中文显示名均为工作音译。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-maffei-m-persons-") as td:
        temp = Path(td)
        alignment_stage, manifest_stage = temp / "alignment.csv", temp / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: alignment_stage.read_bytes(), MANIFEST: manifest_stage.read_bytes(),
            ENRICHMENT: template.with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: template.with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: template.with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: template.with_bom(result_text + "\n", RESULT.read_bytes()),
        }
        for target in TARGETS:
            writes[ROOT / target["card"]] = template.with_bom(cards[target["card"]])

    if args.dry_run:
        relation_count = sum(len(target["relations"]) for target in TARGETS)
        print(f"S4 dry-run passed: groups={batch_size}; candidate_mappings={batch_size}; name_fields={name_fields}; direct_relation_candidates={relation_count}.")
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
                if path.exists():
                    path.unlink()
            else:
                template.atomic_write(path, content)
        raise
    print(f"applied: groups={batch_size}; candidate_mappings={batch_size}; name_fields={name_fields}; relation_candidates={sum(len(target['relations']) for target in TARGETS)}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
