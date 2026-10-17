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
ANCHOR = "s4-person-direct-endpoints-loredan-lovisa-batch-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HOLD_MARKER = "S4 pending identity evidence: unnamed Duke of Lorraine"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [
    {
        "primary": "cand-1437", "members": ["cand-1437"], "expected_name": "Loredan, Antonio", "expected_pages": "256",
        "group": "new-person:antonio-loredan-d07ef14ba2", "ku": "units/persons/antonio-loredan", "card": "04-knowledge/units/persons/antonio-loredan.md",
        "name_zh": "安东尼奥·洛雷丹", "name_en": "Antonio Loredan",
        "name_rows": [("索引名", "Loredan, Antonio", "S1（索引L.csv#94）"), ("正文姓名形式", "Antonio", "S2（第9章p.256）")],
        "sources": [src("第9章导论；印刷页256", "Haskell称Loredan家族另一成员Antonio离开Padua总督职位时被一位演说者比作Pompey；原文只说发生于“大约同一时期”。", "another member of the Loredan family, Antonio, was, on leaving the governorship of Padua, compared to Pompey.7", "02-sources/02-Markdown/09_CHP-9_intro.md", "line 164; print p.256")],
        "zh": "本卡登记索引L.csv#94所列Antonio Loredan。第9章p.256称他是Loredan家族另一成员，并称他离开Padua总督职位时曾被演说者比作Pompey；Haskell只说发生在“大约同一时期”，未给出其离任的确切日期。注7所引演说未在本批独立查阅。",
        "en": "This card registers Antonio Loredan under index L.csv#94. Chapter 9, p.256, identifies him as another member of the Loredan family and says an orator compared him to Pompey when he left the governorship of Padua. Haskell gives only “about the same time,” not an exact date for his departure. The oration cited in note 7 was not independently consulted in this batch.",
        "context_zh": "本段将Antonio与同页另述的Pietro Loredan区分；不把Pietro的1724年日期移用于Antonio。直接S2候选st-chp9-p256-antonio-loredan-pompey-comparison留待S6裁决。",
        "context_en": "The passage distinguishes Antonio from Pietro Loredan, discussed nearby; Pietro’s 1724 date is not transferred to Antonio. Direct S2 candidate st-chp9-p256-antonio-loredan-pompey-comparison remains for S6 review.",
        "relations": ["st-chp9-p256-antonio-loredan-pompey-comparison"],
        "endpoints": {"st-chp9-p256-antonio-loredan-pompey-comparison": "antonio_loredan_departure_from_padua_compared_to_pompey"},
    },
    {
        "primary": "cand-1438", "members": ["cand-1438"], "expected_name": "Loredan, Pietro", "expected_pages": "256",
        "group": "new-person:loredan-pietro-d8a0532873", "ku": "units/persons/pietro-loredan", "card": "04-knowledge/units/persons/pietro-loredan.md",
        "name_zh": "皮耶特罗·洛雷丹", "name_en": "Pietro Loredan",
        "name_rows": [("索引名", "Loredan, Pietro", "S1（索引L.csv#95）"), ("正文姓名形式", "Pietro Loredan", "S2（第9章p.256）")],
        "sources": [src("第9章导论；印刷页256", "Haskell称Pietro Loredan于1724年离开中立的Venice前往由他指挥的Legnano要塞，一位演说者提及Mucius Scaevola的英勇。", "Thus in 1724 when Pietro\nLoredan left a neutral Venice for the fortress of Legnano of which he was commander, an orator alluded to the heroism of Mucius Scaevola6", "02-sources/02-Markdown/09_CHP-9_intro.md", "lines 163-164; print p.256")],
        "zh": "本卡登记索引L.csv#95所列Pietro Loredan。第9章p.256称他于1724年离开中立的Venice前往由他指挥的Legnano要塞；Haskell说一位演说者借此提及Mucius Scaevola的英勇。注6所引演说未在本批独立查阅。",
        "en": "This card registers Pietro Loredan under index L.csv#95. Chapter 9, p.256, says that in 1724 he left neutral Venice for the fortress of Legnano, which he commanded; Haskell says an orator invoked the heroism of Mucius Scaevola. The oration cited in note 6 was not independently consulted in this batch.",
        "context_zh": "该页另述Antonio Loredan离任及Pompey比较；两人按各自姓名分组，未合并为同一人。直接S2候选st-chp9-p256-pietro-loredan-1724-mucius-comparison留待S6裁决。",
        "context_en": "The page separately discusses Antonio Loredan’s departure and the Pompey comparison; the two men remain separate identity groups. Direct S2 candidate st-chp9-p256-pietro-loredan-1724-mucius-comparison remains for S6 review.",
        "relations": ["st-chp9-p256-pietro-loredan-1724-mucius-comparison"],
        "endpoints": {"st-chp9-p256-pietro-loredan-1724-mucius-comparison": "pietro_loredan_departure_compared_to_mucius_scaevola"},
    },
    {
        "primary": "cand-1439", "members": ["cand-1439"], "expected_name": "Lorenzi, Francesco", "expected_pages": "255n",
        "group": "new-person:francesco-lorenzi-3ec9131e80", "ku": "units/persons/francesco-lorenzi", "card": "04-knowledge/units/persons/francesco-lorenzi.md",
        "name_zh": "弗朗切斯科·洛伦齐", "name_en": "Francesco Lorenzi",
        "name_rows": [("索引名", "Lorenzi, Francesco", "S1（索引L.csv#96）"), ("正文姓名形式", "Francesco Lorenzi", "S2（第9章p.255注1）")],
        "sources": [
            src("第9章导论注1；印刷页255", "Haskell转述Zannandreis关于Lorenzi为Tiepolo提供寓意方案的说法。", "Thus Zannandreis, writing (p. 426) about the Veronese painter Francesco Lorenzi, suggests that it was he who provided Tiepolo with an allegorical scheme for glorifying the King of Spain.", "02-sources/02-Markdown/09_CHP-9_intro.md", "print p.255 n.1"),
            src("第9章导论；印刷页255", "Haskell紧接着指出这则故事可能是为彰显Lorenzi学识而编出的传闻。", "Though this may well be an apocryphal story designed to show off Lorenzi’s culture", "02-sources/02-Markdown/09_CHP-9_intro.md", "line 155; print p.255"),
        ],
        "zh": "本卡登记索引L.csv#96所列Francesco Lorenzi。第9章p.255注1转述Zannandreis称Lorenzi曾为Tiepolo提供颂扬西班牙国王的寓意方案；正文随即称此事“很可能是杜撰的故事”。本卡保留嵌套转述与不确定性，不据此断言方案已完成。",
        "en": "This card registers Francesco Lorenzi under index L.csv#96. Chapter 9, p.255 n.1, relays Zannandreis’s account that Lorenzi supplied Tiepolo with an allegorical scheme glorifying the King of Spain; the main text immediately calls it a story that may well be apocryphal. The nested report and uncertainty are retained, and completion of the scheme is not asserted.",
        "context_zh": "来源链为Haskell转述Zannandreis，且正文对故事真实性存疑。直接S2候选st-chp9-p255-lorenzi-scheme-report留待S6裁决。",
        "context_en": "The source chain is Haskell reporting Zannandreis, and the main text questions the story’s reliability. Direct S2 candidate st-chp9-p255-lorenzi-scheme-report remains for S6 review.",
        "relations": ["st-chp9-p255-lorenzi-scheme-report"],
        "endpoints": {"st-chp9-p255-lorenzi-scheme-report": "lorenzi_reportedly_supplied_tiepolo_scheme_to_glorify_king_of_spain"},
    },
    {
        "primary": "cand-1452", "members": ["cand-1452"], "expected_name": "Lovisa, Domenico", "expected_pages": "332, 333",
        "group": "new-person:domenico-lovisa-46b41e2e35", "ku": "units/persons/domenico-lovisa", "card": "04-knowledge/units/persons/domenico-lovisa.md",
        "name_zh": "多梅尼科·洛维萨", "name_en": "Domenico Lovisa",
        "name_rows": [("索引名", "Lovisa, Domenico", "S1（索引L.csv#110）"), ("正文姓名形式", "Domenico Lovisa", "S2（第13章p.332）")],
        "sources": [
            src("第13章导论；印刷页332", "Haskell称Il Gran Teatro delle Pitture e Prospettive di Venezia于1720年由Domenico Lovisa出版，并概述书中图像内容。", "II Gran Teatro delle Pitture e Prospettive di Venezia, published in 1720 by Domenico Lovisa with drawings of famous monuments and pictures by a number of artists, including the young Tiepolo.", "02-sources/02-Markdown/13_CHP-13_intro.md", "line 12; print p.332"),
            src("第13章导论；印刷页333", "Haskell在下一页将前述书籍识别为Lovisa赞助的出版项目。", "Such was the book sponsored by Domenico Lovisa.", "02-sources/02-Markdown/13_CHP-13_intro.md", "lines 14-15; print p.333"),
        ],
        "zh": "本卡登记索引L.csv#110所列Domenico Lovisa。第13章p.332称他于1720年出版《Il Gran Teatro delle Pitture e Prospettive di Venezia》；p.333将前述书籍称为他赞助的项目。出版者与赞助者是分别表述的角色。p.332转录的标题首字母“I”校读为“Il”，依据已记录于S2的OCR更正。",
        "en": "This card registers Domenico Lovisa under index L.csv#110. Chapter 13, p.332, says he published Il Gran Teatro delle Pitture e Prospettive di Venezia in 1720; p.333 identifies the preceding book as a venture sponsored by him. Publisher and sponsor are recorded as distinct roles. The initial “I” in the p.332 transcription is read as “Il,” following the OCR correction documented in S2.",
        "context_zh": "p.332出版断言与p.333赞助断言指向同一书籍，但关系类型分别保留。直接S2候选st-chp13-p332-lovisa-gran-teatro-publication-and-illustrations与st-chp13-p333-lovisa-book-sponsored-example留待S6逐条裁决。",
        "context_en": "The publication statement on p.332 and sponsorship statement on p.333 refer to the same book but retain distinct relation types. Direct S2 candidates st-chp13-p332-lovisa-gran-teatro-publication-and-illustrations and st-chp13-p333-lovisa-book-sponsored-example remain for individual S6 review.",
        "relations": ["st-chp13-p332-lovisa-gran-teatro-publication-and-illustrations", "st-chp13-p333-lovisa-book-sponsored-example"],
        "endpoints": {
            "st-chp13-p332-lovisa-gran-teatro-publication-and-illustrations": "published_by",
            "st-chp13-p333-lovisa-book-sponsored-example": "sponsored_by",
        },
    },
]

HOLD = {
    "candidate_id": "cand-1441", "group": "new-person:lorraine-of-dc18d315ff", "name": "Lorraine, Duke of",
    "pages": "267", "statement_id": "st-chp9-p267-lorraine-claim",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four source-backed S3 person groups and preserve one title-only identity as pending.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    template.TARGETS = TARGETS
    template.DATE, template.ANCHOR, template.PROCESS_REF = DATE, ANCHOR, PROCESS_REF
    sync = template.helper.base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    main_rows = [r for r in alignments if r.get("candidate_id") and not r.get("external_source")]
    main_by_id = {r["candidate_id"]: r for r in main_rows}
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

    for t in TARGETS:
        candidate = candidate_by_id[t["primary"]]
        t["entry"], t["index_name"], t["pages"] = candidate["index_entry_id"], candidate["canonical_name"], candidate["index_page_range"]
        assert candidate.get("suggested_type") == "person"
        assert (candidate.get("canonical_name"), candidate.get("index_page_range")) == (t["expected_name"], t["expected_pages"])
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
        for sid, predicate in t["endpoints"].items():
            assert direct[sid].get("predicate") == predicate
        for item in t["sources"]:
            source_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", source_text), (t["primary"], item["span"])
        path = ROOT / t["card"]
        mapped = row.get("ku_id") == t["ku"]
        assert (t["ku"] in manifest_by_ku) == (t["card"] in accepted_paths) == path.exists() == mapped

    hold_candidate = candidate_by_id[HOLD["candidate_id"]]
    hold_row = main_by_id[HOLD["candidate_id"]]
    assert hold_candidate.get("canonical_name") == HOLD["name"] and hold_candidate.get("index_entry_id") == "L.csv#99"
    assert hold_candidate.get("index_page_range") == HOLD["pages"] and hold_candidate.get("suggested_type") == "person"
    assert hold_row.get("decision") == "new" and sync.get_group(hold_row.get("resolution_note", "")) == HOLD["group"]
    assert not hold_row.get("ku_id")
    hold_members = [r["candidate_id"] for r in main_rows if r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == HOLD["group"]]
    assert hold_members == [HOLD["candidate_id"]]
    hold_statement = next(s for s in statements if s.get("statement_id") == HOLD["statement_id"])
    assert (hold_statement.get("qualifiers") or {}).get("relation_candidate") is True
    hold_source = (ROOT / hold_statement["source_file"]).read_text(encoding="utf-8-sig")
    assert "the Duke of Lorraine successfully established his claim to be heir to the Gonzaga effects" in re.sub(r"\s+", " ", hold_source)

    cards = {t["card"]: template.make_card(t) for t in TARGETS}
    all_registered = all(main_by_id[t["primary"]].get("ku_id") == t["ku"] for t in TARGETS)
    hold_done = HOLD_MARKER in hold_row.get("resolution_note", "")
    if all_registered and hold_done:
        for t in TARGETS:
            assert (ROOT / t["card"]).read_text(encoding="utf-8-sig") == cards[t["card"]]
        print("ALREADY REGISTERED: four person groups and the title-only S4 hold are recorded.")
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
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
        planned_accepted = template.helper.base.insert_accepted(planned_accepted, t["card"])
    planned_hold = planned_by_id[HOLD["candidate_id"]]
    if not hold_done:
        planned_hold["process_ref"] = PROCESS_REF
        planned_hold["resolution_note"] += (
            f" {HOLD_MARKER} ({DATE}): index L.csv#99 and p.267 identify only an unnamed title; "
            "the passage does not establish the duke's personal identity. No KU is created; keep this source-local candidate pending until a reliable identity anchor is available."
        )

    planned_manifest.sort(key=lambda r: r["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {k: sum(r[k] for r in stats.values()) for k in next(iter(stats.values()))}
    batch_size = len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + batch_size
    assert totals["registered_members"] == before_totals["registered_members"] + batch_size
    assert totals["pending_groups"] == before_totals["pending_groups"] - batch_size
    assert totals["pending_members"] == before_totals["pending_members"] - batch_size
    assert len(planned_manifest) == len(manifest) + batch_size

    additions, card_tables = template.extract_card_fields(cards)
    name_fields = sum(len(t["name_rows"]) for t in TARGETS)
    assert card_tables == batch_size and len(additions) == name_fields and all(r.get("evidence_status") == "source_backed" for r in additions)
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Loredan、Lorenzi与Lovisa（{DATE}）\n\n"
    for t in TARGETS:
        process_text += f"- `{t['primary']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}（页码{t['pages']}）与书内页段支持source-local人物登记；直接S2关系候选{', '.join(t['relations'])}留待S6裁决，不登记正式关系。\n"
    process_text += (
        f"- `{HOLD['candidate_id']}`（`{HOLD['group']}`）保留S4待证：索引L.csv#99与第9章p.267只给出“Duke of Lorraine”爵号，未给个人姓名；"
        "alignment resolution_note记录不建KU及其待补身份依据。\n"
    )
    relation_count = sum(len(t["relations"]) for t in TARGETS)
    process_text += (
        f"\n本批登记{batch_size}个S3 new人物组、{batch_size}条候选映射和{name_fields}条source_backed名称字段；"
        f"{relation_count}条直接S2关系候选留待S6，另1组因身份锚点仅为未具名爵号而保持待证。"
        "保留Antonio的日期限定、Pietro演说引文未独立查阅状态、Lorenzi的嵌套转述和可能伪托、Lovisa出版与赞助两种角色及标题OCR更正。本批无外部身份行、无正式关系、无来源登记变更。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接端点登记：Loredan、Lorenzi与Lovisa（{DATE}）\n\n登记Antonio Loredan、Pietro Loredan、Francesco Lorenzi与Domenico Lovisa四个人物组。"
        f"本批{batch_size}条候选映射、{name_fields}条source_backed名称字段及{relation_count}条直接S2关系候选；关系待S6，未新增正式边。"
        "Duke of Lorraine仅有爵号，身份锚点不足，记为S4待证且不创建KU。"
        f"KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-loredan-lovisa-") as td:
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
        for t in TARGETS:
            writes[ROOT / t["card"]] = template.with_bom(cards[t["card"]])

    if args.dry_run:
        print(f"S4 dry-run passed: groups={batch_size}; candidate_mappings={batch_size}; name_fields={name_fields}; direct_relation_candidates={relation_count}.")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
        print("hold=cand-1441 title-only Duke of Lorraine; no KU; pending identity evidence")
        print("formal_relations_added=0; candidate_backlog_changed=0; sources_registry_changed=0; no files changed")
        return 0
    originals = {p: p.read_bytes() if p.exists() else None for p in writes}
    try:
        for p, content in writes.items():
            template.atomic_write(p, content)
    except Exception:
        for p, content in originals.items():
            if content is None:
                if p.exists():
                    p.unlink()
            else:
                template.atomic_write(p, content)
        raise
    print(f"applied: groups={batch_size}; candidate_mappings={batch_size}; name_fields={name_fields}; relation_candidates={relation_count}; KU={len(planned_manifest)}; formal_relations_added=0")
    print("hold=cand-1441 title-only Duke of Lorraine; no KU; pending identity evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
