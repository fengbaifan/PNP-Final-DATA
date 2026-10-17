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
ANCHOR = "s4-person-direct-endpoints-john-sobieski-leblon-batch-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [
    {
        "primary": "cand-1332", "members": ["cand-1332"], "expected_name": "John Sobieski, King of Poland", "expected_pages": "129",
        "group": "new-person:john-of-poland-sobieski-831a5af6fd", "ku": "units/persons/john-sobieski-king-of-poland", "card": "04-knowledge/units/persons/john-sobieski-king-of-poland.md",
        "name_zh": "波兰国王扬·索别斯基", "name_en": "John Sobieski, King of Poland",
        "name_rows": [("索引名", "John Sobieski, King of Poland", "S1（索引J，K.csv#16）"), ("正文称谓", "King John of Poland", "S2（第5章p.129）")],
        "sources": [src("第5章第I节；印刷页129", "Haskell称教宗希望宣传波兰国王约翰取得的胜利，并鼓励其遗孀借出一批肖像与战役画。", "the victories won by King John of Poland and encouraged his widow to lend a series of portraits and battle pictures for this purpose.", "02-sources/02-Markdown/05_CHP-5_sec_i.md", "lines 102–103; print p.129")],
        "zh": "本卡将索引J，K.csv#16的John Sobieski, King of Poland与第5章p.129的King John of Poland归为同一书内人物身份。书中所述胜利及其遗孀借画情节仍按Haskell的表述记录，不作外部核实。",
        "en": "This card groups the index form John Sobieski, King of Poland (J, K.csv#16) with King John of Poland in chapter 5, p.129. The victories and the account of his widow lending pictures remain attributed to Haskell and are not independently verified here.",
        "context_zh": "段落分别提到胜利宣传和遗孀借出肖像与战役画。两条直接S2关系候选st-chp5-p129-king-john-victory-group、st-chp5-p129-john-sobieski-widow留待S6逐条裁决。",
        "context_en": "The passage separately mentions publicising victories and the widow lending portraits and battle pictures. The direct S2 candidates st-chp5-p129-king-john-victory-group and st-chp5-p129-john-sobieski-widow remain for individual S6 review.",
        "relations": ["st-chp5-p129-king-john-victory-group", "st-chp5-p129-john-sobieski-widow"],
        "endpoints": {"st-chp5-p129-king-john-victory-group": "won_victory_group", "st-chp5-p129-john-sobieski-widow": "widow_of"},
    },
    {
        "primary": "cand-1335", "members": ["cand-1335"], "expected_name": "Jones, Inigo", "expected_pages": "178, 309",
        "group": "new-person:inigo-jones-a18fbfb698", "ku": "units/persons/inigo-jones", "card": "04-knowledge/units/persons/inigo-jones.md",
        "name_zh": "伊尼戈·琼斯", "name_en": "Inigo Jones",
        "name_rows": [("索引名", "Jones, Inigo", "S1（索引J，K.csv#19）"), ("正文姓名形式", "Inigo Jones", "S2（第10章p.309）")],
        "sources": [src("第10章导论；印刷页309", "Haskell称十一幅图像中有五幅描绘Inigo Jones的作品，并将其与其他英国建筑师分列。", "Five of the eleven pictures portray works by Inigo Jones, two by Lord Burlington, two by Colen Campbell, one by Roger Morris, and one—curiously enough—by Vanbrugh", "02-sources/02-Markdown/10_CHP-10_intro.md", "lines 469–470; print p.309")],
        "zh": "本卡登记索引J，K.csv#19所列Inigo Jones。第10章p.309称十一幅图像中有五幅描绘Jones的作品；这句话不等同于将图像本身归为Jones创作。",
        "en": "This card registers Inigo Jones under index J, K.csv#19. Chapter 10, p.309, says five of eleven pictures portray works by Jones; this does not attribute the pictures themselves to Jones.",
        "context_zh": "原文讨论一组图像所描绘的建筑作品，按Jones、Burlington、Campbell、Morris及Vanbrugh分别计数。直接S2候选st-chp10-p309-five-pictures-after-jones留待S6裁决。",
        "context_en": "The passage discusses architectural works depicted in a group of pictures and counts them separately under Jones, Burlington, Campbell, Morris, and Vanbrugh. The direct S2 candidate st-chp10-p309-five-pictures-after-jones remains for S6 review.",
        "relations": ["st-chp10-p309-five-pictures-after-jones"],
        "endpoints": {"st-chp10-p309-five-pictures-after-jones": "five_of_eleven_pictures_portray_works_by_inigo_jones"},
    },
    {
        "primary": "cand-1343", "members": ["cand-1343"], "expected_name": "La Fosse, Charles de", "expected_pages": "284",
        "group": "new-person:charles-de-fosse-la-0e31b8e216", "ku": "units/persons/charles-de-la-fosse", "card": "04-knowledge/units/persons/charles-de-la-fosse.md",
        "name_zh": "夏尔·德·拉福斯", "name_en": "Charles de la Fosse",
        "name_rows": [("索引名", "La Fosse, Charles de", "S1（索引L.csv#0）"), ("正文姓名形式", "Charles de la Fosse；De La Fosse", "S2（第10章p.284；注4）")],
        "sources": [
            src("第10章导论；印刷页284", "Haskell称Ricci抵达时Charles de la Fosse住在Crozat家中，并处于其八十岁且生命最后一年。", "When Ricci arrived, Charles de la Fosse, who had himself been to London, was lodged in Crozat’s house. He was in his eightieth and last year", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 171; print p.284"),
            src("第10章导论注4；印刷页284", "Haskell转述经Levey引自Walpole《Anecdotes》的La Fosse对Ricci的评语，并推测该评语大概作于前述场合。", "De La Fosse’s reported remark to Ricci, ‘Paint nothing but Paul Veroneses and no more Riccis’, quoted by Levey, 1959, p. 22, from Walpole’s Anecdotes must presumably have been made on this occasion.", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 527; print p.284 n.4"),
        ],
        "zh": "本卡登记索引L.csv#0所列Charles de la Fosse。第10章p.284及注4分别记载其在Crozat家中的居住与一则经Levey转引自Walpole的评语；后者是否作于该场合是Haskell的推测。",
        "en": "This card registers Charles de la Fosse under index L.csv#0. Chapter 10, p.284, and note 4 report his lodging with Crozat and a remark transmitted by Levey from Walpole; Haskell only presumes that the remark was made on that occasion.",
        "context_zh": "原书称其去过伦敦、处于八十岁且生命最后一年；注4的评语保留转引链及推测语气。两条直接S2关系候选st-chp10-p284-la-fosse-lodged-and-aged、st-chp10-notes-p284n4-la-fosse-remark-to-ricci留待S6。",
        "context_en": "The book says he had been to London and was in his eightieth and last year; note 4 retains the reported-source chain and conjectural wording. The direct S2 candidates st-chp10-p284-la-fosse-lodged-and-aged and st-chp10-notes-p284n4-la-fosse-remark-to-ricci remain for S6.",
        "relations": ["st-chp10-p284-la-fosse-lodged-and-aged", "st-chp10-notes-p284n4-la-fosse-remark-to-ricci"],
        "endpoints": {"st-chp10-p284-la-fosse-lodged-and-aged": "la_fosse_lodged_at_crozat_house_in_final_year", "st-chp10-notes-p284n4-la-fosse-remark-to-ricci": "haskell_reports_de_la_fosse_remark_to_ricci_and_probably_places_it_at_crozat_house"},
    },
    {
        "primary": "cand-1363", "members": ["cand-1363"], "expected_name": "Langetti, Giovanni Battista", "expected_pages": "234n",
        "group": "new-person:battista-giovanni-langetti-0431e4284a", "ku": "units/persons/giovanni-battista-langetti", "card": "04-knowledge/units/persons/giovanni-battista-langetti.md",
        "name_zh": "乔瓦尼·巴蒂斯塔·兰盖蒂", "name_en": "Giovanni Battista Langetti",
        "name_rows": [("索引名", "Langetti, Giovanni Battista", "S1（索引L.csv#20）"), ("正文姓名形式", "Langetti", "S2（第8章p.234注）")],
        "sources": [src("第8章第II节注；印刷页234", "Haskell转述Ratti称Langetti曾受Ferdinand雇用于Florence，同时立即指出该说法不可能：Langetti于1676年去世，而亲王当时年仅11岁。", "Ratti (Soprani/Ratti, H, 26), who reports seeing a portrait and a picture of card players by him in the Medici collection, says that Langetti was actually employed by Ferdinand in Florence. But this is impossible as Langetti died in 1676 when the Prince was only aged 11.", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "line 289; print p.234 n.")],
        "zh": "本卡登记索引L.csv#20所列Giovanni Battista Langetti。第8章p.234注转述Ratti关于其受雇于Ferdinand的说法，并在同一注中以Langetti卒于1676年、亲王当时仅11岁指出该说法不可能；本卡同时保留两层表述。",
        "en": "This card registers Giovanni Battista Langetti under index L.csv#20. Chapter 8, p.234 n., reports Ratti’s claim that he worked for Ferdinand, then calls it impossible because Langetti died in 1676 when the Prince was only eleven; both layers are retained.",
        "context_zh": "关系候选为Haskell转述的Ratti报告，且同一原注已提出年代矛盾；不把该受雇说法登记为已确认事实。直接S2候选st-chp8-p234-langetti-report留待S6审查。",
        "context_en": "The relation candidate is Ratti’s claim as reported by Haskell, and the same note raises a chronological contradiction; the employment claim is not registered as established fact. The direct S2 candidate st-chp8-p234-langetti-report remains for S6 review.",
        "relations": ["st-chp8-p234-langetti-report"],
        "endpoints": {"st-chp8-p234-langetti-report": "ratti_reported_langetti_employed_by_ferdinand_in_florence"},
    },
    {
        "primary": "cand-1375", "members": ["cand-1375"], "expected_name": "LeBlon, Jakob Christoffel", "expected_pages": "408",
        "group": "new-person:christoffel-jakob-leblon-559fe2b5aa", "ku": "units/persons/jakob-christoffel-le-blon", "card": "04-knowledge/units/persons/jakob-christoffel-le-blon.md",
        "name_zh": "雅各布·克里斯托费尔·勒布隆", "name_en": "Jakob Christoffel Le Blon",
        "name_rows": [("索引名", "LeBlon, Jakob Christoffel", "S1（索引L.csv#32）"), ("后记姓名形式（原书拼写）", "Jakob Christoffel Le Bion", "S2（第20章后记p.408）")],
        "sources": [src("第20章后记；印刷页408", "Haskell转述James Byam Shaw将Antonio Conti感兴趣的德国画家认作Jakob Christoffel Le Bion，并称其发明在英意两地产生影响。", "James Byam Shaw has shown that the German painter in whom Antonio Conti was interested because his invention of a new method of colour printing could be related to the theories of Sir Isaac Newton was in fact Jakob Christoffel Le Bion, whose invention made a notable impact in England as well as in Italy.", "02-sources/02-Markdown/20_CHP-20Postscript.md", "lines 178–179; print p.408")],
        "zh": "本卡登记索引L.csv#32所列Jakob Christoffel LeBlon；第20章后记按原书拼写为Le Bion，并将身份判断归于James Byam Shaw。此处只保存Haskell的转述，不独立验证人物身份或其发明的影响。",
        "en": "This card registers Jakob Christoffel LeBlon under index L.csv#32; the postscript spells the name “Le Bion” and attributes the identification to James Byam Shaw. The card records Haskell’s report without independently verifying the identity or the invention’s impact.",
        "context_zh": "后记称Antonio Conti曾关注这位德国画家及其与Newton理论相关的新彩色印刷方法，并转述Byam Shaw将其认作Le Bion。直接S2候选st-chp20-p408-byam-shaw-identifies-le-blon留待S6裁决。",
        "context_en": "The postscript says Antonio Conti was interested in this German painter and a new colour-printing method related to Newton’s theories, then reports Byam Shaw’s identification as Le Bion. The direct S2 candidate st-chp20-p408-byam-shaw-identifies-le-blon remains for S6 review.",
        "relations": ["st-chp20-p408-byam-shaw-identifies-le-blon"],
        "endpoints": {"st-chp20-p408-byam-shaw-identifies-le-blon": "identifies_contis_german_painter_as_le_blon"},
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register five source-backed person groups used as direct S2 relation endpoints.")
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
        assert (candidate.get("canonical_name"), candidate.get("index_page_range")) == (target["expected_name"], target["expected_pages"])
        row = main_by_id[target["primary"]]
        assert row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == target["group"]
        assert not row.get("ku_id") or row.get("ku_id") == target["ku"]
        members = [r["candidate_id"] for r in main_rows if r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == target["group"]]
        assert members == target["members"], (target["group"], members)
        index_file, _ = target["entry"].split("#", 1)
        index_hits = [r for r in template.helper.base.read_index_rows(index_file) if r.get("Main Entry") == target["index_name"] and r.get("Page Numbers") == target["pages"]]
        assert len(index_hits) == 1, (target["entry"], index_hits)
        direct = {r["statement_id"]: r for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == target["primary"] or r.get("object_candidate_id") == target["primary"])}
        assert set(direct) == set(target["endpoints"]), (target["primary"], sorted(direct), sorted(target["endpoints"]))
        for sid, predicate in target["endpoints"].items():
            assert direct[sid].get("predicate") == predicate
            assert direct[sid].get("subject_candidate_id") == target["primary"] or direct[sid].get("object_candidate_id") == target["primary"]
        for item in target["sources"]:
            text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            normalized = re.sub(r"\s+", " ", text)
            assert re.sub(r"\s+", " ", item["quote"]) in normalized, (target["primary"], item["span"])
        path = ROOT / target["card"]
        mapped = row.get("ku_id") == target["ku"]
        assert (target["ku"] in manifest_by_ku) == (target["card"] in accepted_paths) == path.exists() == mapped

    cards = {t["card"]: template.make_card(t) for t in TARGETS}
    all_registered = all(main_by_id[t["primary"]].get("ku_id") == t["ku"] for t in TARGETS)
    if all_registered:
        for t in TARGETS: assert (ROOT / t["card"]).read_text(encoding="utf-8-sig") == cards[t["card"]]
        print("ALREADY REGISTERED: all five person groups and their candidate mappings are present.")
        return 0
    assert not any(main_by_id[t["primary"]].get("ku_id") for t in TARGETS), "partial registration requires explicit reconciliation"

    before_stats = sync.summarize_by_type(candidates, alignments)
    before_totals = {k: sum(r[k] for r in before_stats.values()) for k in next(iter(before_stats.values()))}
    planned_alignments = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        row = planned_by_id[t["primary"]]
        row["ku_id"], row["process_ref"] = t["ku"], PROCESS_REF
        row["resolution_note"] += f" S4 registration ({DATE}): group {t['group']} -> {t['ku']}; source-backed person identity registration; direct S2 relation candidates remain for S6."
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
        planned_accepted = template.helper.base.insert_accepted(planned_accepted, t["card"])
    planned_manifest.sort(key=lambda r: r["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {k: sum(r[k] for r in stats.values()) for k in next(iter(stats.values()))}
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == before_totals["registered_members"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    additions, card_tables = template.extract_card_fields(cards)
    name_fields = sum(len(t["name_rows"]) for t in TARGETS)
    assert card_tables == len(TARGETS) and len(additions) == name_fields
    assert all(r.get("evidence_status") == "source_backed" for r in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id", "")) for r in existing}
    ids = {r.get("enrichment_id", "") for r in existing}
    max_id = max((int(m.group(1)) for v in ids if (m := re.fullmatch(r"enr-(\d+)", v))), default=0)
    for i, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id+i:05d}"
        assert (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(r, ensure_ascii=False) for r in additions) + "\n"

    process_text = template.helper.base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：John Sobieski、Inigo Jones、La Fosse、Langetti与Le Blon（{DATE}）\n\n"
    for t in TARGETS:
        process_text += f"- `{t['primary']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}与所列书内页段构成身份和来源锚点；直接S2关系候选{', '.join(t['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    relations = sum(len(t["relations"]) for t in TARGETS)
    process_text += (
        f"\n本批登记{len(TARGETS)}个S3 new人物组、{len(TARGETS)}条候选映射和{name_fields}条source_backed名称字段；{relations}条直接S2关系候选留待S6。"
        "Langetti条目同时保留Haskell转述Ratti及同注提出的年代矛盾；La Fosse评语保留Levey/Walpole转引和Haskell推测；Le Blon保留后记拼写变体及Byam Shaw归属。"
        "本批无外部身份行、无正式关系、无来源登记变更。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接端点登记：John Sobieski、Inigo Jones、La Fosse、Langetti与Le Blon（{DATE}）\n\n"
        "登记John Sobieski、Inigo Jones、Charles de la Fosse、Giovanni Battista Langetti与Jakob Christoffel LeBlon五个人物组。"
        f"本批5条候选映射、10条source_backed名称字段和{relations}条直接S2关系候选；保留Langetti的书内年代矛盾、La Fosse的转引及推测语气、Le Blon的拼写与归属限定。关系待S6，未新增正式边。"
        f"KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-john-sobieski-leblon-") as td:
        temp = Path(td)
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
        for t in TARGETS: writes[ROOT / t["card"]] = template.with_bom(cards[t["card"]])

    if args.dry_run:
        print(f"S4 dry-run passed: groups={len(TARGETS)}; candidate_mappings={len(TARGETS)}; name_fields={name_fields}; direct_relation_candidates={relations}.")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
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
    print(f"applied: groups={len(TARGETS)}; candidate_mappings={len(TARGETS)}; name_fields={name_fields}; relation_candidates={relations}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
