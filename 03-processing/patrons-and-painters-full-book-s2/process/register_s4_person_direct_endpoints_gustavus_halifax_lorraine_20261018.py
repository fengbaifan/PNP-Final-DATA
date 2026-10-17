from __future__ import annotations

import argparse
import csv
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
ANCHOR = "s4-person-direct-endpoints-gustavus-halifax-lorraine-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def target(primary, entry, index_name, pages, old_group, group, slug, zh, en,
           name_rows, sources, desc_zh, desc_en, context_zh, context_en,
           relations, endpoints, external, s3_note):
    return {
        "primary": primary, "entry": entry, "index_name": index_name,
        "canonical_name": index_name, "pages": pages,
        "old_group": old_group, "group": group,
        "ku": f"units/persons/{slug}", "card": f"04-knowledge/units/persons/{slug}.md",
        "name_zh": zh, "name_en": en, "name_rows": name_rows,
        "sources": sources, "zh": desc_zh, "en": desc_en,
        "context_zh": context_zh, "context_en": context_en,
        "relations": relations, "endpoints": endpoints,
        "external": external, "s3_note": s3_note,
    }


TARGETS = [
    target(
        "cand-1283", "G.csv#193", "Gustavus III of Sweden", "366",
        "new-person:gustavus-iii-of-sweden-5f6ef99faa",
        "new-person:gustavus-iii-of-sweden-5f6ef99faa", "gustav-iii-of-sweden",
        "古斯塔夫三世（瑞典国王）", "Gustav III of Sweden",
        [("索引名称", "Gustavus III of Sweden", "S1（索引G.csv#193）"),
         ("正文称谓", "King of Sweden", "S2（第15章第II节p.366）")],
        [template.source("第15章第II节；印刷页366",
                         "Haskell仅称波兰国王和瑞典国王均认捐该雕像计划；第366页索引将瑞典国王列为Gustavus III。",
                         "the Kings of Poland and Sweden both subscribed",
                         "02-sources/02-Markdown/15_CHP-15_sec_ii.md", "line 21; print p.366")],
        "本卡登记《赞助人与画家》索引所列Gustavus III of Sweden；瑞典国家档案馆《瑞典传记辞典》采用Gustav III。第15章p.366正文只称瑞典国王。",
        "This card registers Gustavus III of Sweden from the book index; the Swedish Biographical Lexicon of the National Archives of Sweden uses Gustav III. Chapter 15, p.366, refers only to the King of Sweden.",
        "第15章p.366称波兰国王与瑞典国王均认捐Memmo的雕像计划。此处外部记录只用于身份匹配，不核实认捐陈述。与第6、7章cand-1284所指Gustavus Adolphus（Gustav II Adolf）分开。",
        "Chapter 15, p.366, says both the Kings of Poland and Sweden subscribed to Memmo’s statue scheme. The external record is used only for identity matching and does not verify the subscription claim. This is distinct from Gustavus Adolphus (Gustav II Adolf), candidate cand-1284 in chapters 6 and 7.",
        ["st-chp15-p366-king-of-sweden-subscribed"],
        {"st-chp15-p366-king-of-sweden-subscribed": ("cand-1283", "cand-1650", "king_of_sweden_subscribed_to_scheme")},
        {"source": "Svenskt Biografiskt Lexikon (Riksarkivet)", "id": "13317",
         "alignment_id": "13317", "url": "https://sok.riksarkivet.se/sbl/Presentation.aspx?forceOrdinarySite=true&id=13317",
         "label": "Gustav III — Svenskt Biografiskt Lexikon, record 13317",
         "scope": "身份消歧；记录列Gustav III、生卒年1746–1792及1771–1792年在位，与第15章p.366的1777年语境相符；不核实认捐陈述。"},
        "source_ref=candidate=cand-1283; index_entry=G.csv#193; source page=366; S2 mention m-chp15-p366-memmo-0056 names only Sweden in the body, while the index names Gustavus III of Sweden. The Swedish Biographical Lexicon (Riksarkivet), record 13317, identifies Gustav III as King of Sweden (1746–1792; reigned 1771–1792), matching the 1777 context. Keep separate from cand-1284 Gustavus Adolphus (Gustav II Adolf; 1611–1632). No exact existing Gustav III KU; decision new. External identity evidence does not verify the subscription claim."
    ),
    target(
        "cand-1286", "H.csv#1", "Halifax, Earl of", "286",
        "new-person:halifax-of-d914fc61b9", "new-person:halifax-of-d914fc61b9",
        "earl-of-halifax-source-local",
        "哈利法克斯伯爵（原书未具名）", "Earl of Halifax (unnamed in the source)",
        [("索引称谓", "Halifax, Earl of", "S1（索引H.csv#1）"),
         ("正文称谓", "Earl of Halifax", "S2（第10章p.286）")],
        [template.source("第10章导论；印刷页286",
                         "Haskell称在Queen’s Bed Chamber委托叙述中，Earl of Halifax表示若委托给Sebastiano Ricci，Treasury将拒绝付款；姓名未提供。",
                         "after the Earl of Halifax had said that the Treasury would refuse to pay",
                         "02-sources/02-Markdown/10_CHP-10_intro.md", "lines 194–195; print p.286")],
        "本卡只登记书中在Queen’s Bed Chamber委托叙述中出现的未具名Earl of Halifax，不推定其个人姓名或具体世袭爵号持有人。",
        "This card registers only the unnamed Earl of Halifax in the book’s account of the Queen’s Bed Chamber commission; it does not infer a personal name or a specific hereditary titleholder.",
        "Haskell报告称该伯爵表示，若委托给Sebastiano Ricci，Treasury将拒绝付款。此为原书所述的威胁，不表示Treasury实际拒付；人物身份保持书内称谓级别。",
        "Haskell reports that the earl said the Treasury would refuse payment if the commission went to Sebastiano Ricci. This records the reported threat, not an actual refusal by the Treasury; the person’s identity remains at the title-only level supplied by the book.",
        ["st-chp10-p286-queens-bedchamber-commission"],
        {"st-chp10-p286-queens-bedchamber-commission": ("cand-1286", "cand-8988", "halifax_threatened_to_block_payment_for_ricci_commission")},
        None,
        "source_ref=candidate=cand-1286; index_entry=H.csv#1; S2 mention m-chp10-p286-halifax and chapter 10 p.286 identify a particular speaker only as ‘Earl of Halifax’. Reaffirm the title-only source-local person group; no personal name or exact titleholder is supplied, and no external identity match is made. Keep separate from any named Halifax candidate unless a reliable anchor appears. Decision new; direct relation candidate remains for S6."
    ),
    target(
        "cand-1441", "L.csv#99", "Lorraine, Duke of", "267",
        "new-person:lorraine-of-dc18d315ff", "new-person:leopold-duke-of-lorraine-20261018",
        "leopold-duke-of-lorraine",
        "洛林公爵利奥波德", "Leopold, Duke of Lorraine",
        [("索引称谓", "Lorraine, Duke of", "S1（索引L.csv#99）"),
         ("正文称谓", "Duke of Lorraine", "S2（第9章p.267）")],
        [template.source("第9章导论；印刷页267",
                         "Haskell称未具名的Duke of Lorraine成功确立其作为Gonzaga财产继承人的请求；本书原句照录，不在S4解释其法律或实际结果。",
                         "Eventually the Duke of Lorraine successfully established his claim to be heir to the Gonzaga effects",
                         "02-sources/02-Markdown/09_CHP-9_intro.md", "lines 318–319; print p.267")],
        "本卡将第9章p.267未具名的Duke of Lorraine对应至Leopold, Duke of Lorraine。Stephen Griffin关于洛林公爵的研究将Leopold（1679–1729）与1708年Gonzaga继承争议相连；身份对应不改写Haskell原句。",
        "This card identifies the unnamed Duke of Lorraine on chapter 9, p.267, as Leopold, Duke of Lorraine. Stephen Griffin’s study of the duke connects Leopold (1679–1729) to the 1708 Gonzaga succession; this identity match does not revise Haskell’s wording.",
        "Haskell称该公爵成功确立其对Gonzaga财产的继承请求。外部研究则称Leopold未能取得Mantua与Monferrato；该措辞差异及请求所指范围留待S6审查，本批只裁决人物身份。",
        "Haskell says the duke successfully established his claim to the Gonzaga effects. The external study says Leopold failed to obtain Mantua and Monferrato; the wording difference and scope of the claim remain for S6 review. This batch decides identity only.",
        ["st-chp9-p267-lorraine-claim"],
        {"st-chp9-p267-lorraine-claim": ("cand-1441", "cand-11467", "duke_of_lorraine_claimed_heirship_to_gonzaga_effects")},
        {"source": "The Historical Journal / Cambridge Core", "id": "10.1017/S0018246X2100090X",
         "alignment_id": "10.1017/S0018246X2100090X",
         "url": "https://www.cambridge.org/core/journals/historical-journal/article/duke-leopold-of-lorraine-small-state-diplomacy-and-the-stuart-court-in-exile-17161729/702E0AF962B06FD9EF7FAD67D78C8A40",
         "label": "Stephen Griffin, ‘Duke Leopold of Lorraine’ (2022), The Historical Journal 65(5)",
         "scope": "身份消歧；§I称Leopold为洛林公爵（1679–1729），并在注26说明其为Ferdinando-Carlo Gonzaga继承人及1708年继承结果；只用于识别人物，不裁决Haskell的claim表述。"},
        "source_ref=candidate=cand-1441; index_entry=L.csv#99; S2 segment chp-9:09_CHP-9_intro:l313-321 identifies only ‘Duke of Lorraine’. This corrects the earlier pending note that no personal identity anchor was available. Stephen Griffin, ‘Duke Leopold of Lorraine, Small State Diplomacy, and the Stuart Court in Exile, 1716–1729’, The Historical Journal 65, no. 5 (2022), pp.1244–1261, DOI 10.1017/S0018246X2100090X, §I and n.26: identifies Duke Leopold (1679–1729), names Ferdinando-Carlo Gonzaga as the inheritance context, and reports that Leopold failed to obtain Mantua and Monferrato in 1708. The source title and context match Haskell’s unnamed duke; no exact Duke Leopold of Lorraine KU exists. Decision new under new-person:leopold-duke-of-lorraine-20261018. Keep distinct from cand-1398 Leopold I, Holy Roman Emperor, cand-1397/cand-8097 Pietro Leopoldo of Tuscany, and cand-1399 Leopold Wilhelm. Identity is resolved; the difference between Haskell’s ‘successfully established his claim’ and Griffin’s account of territorial outcome does not change the S2 statement and remains for S6 interpretation. Candidate cand-11467 (‘Gonzaga effects’) remains untyped/undecided and receives no KU."
    ),
]

OLD_GROUPS = {item["primary"]: item["old_group"] for item in TARGETS}


def build_card(item: dict) -> str:
    rendered = template.make_card(item)
    chinese = f"直接S2候选（待S6）：{', '.join(item['relations'])}。"
    english = f"Direct S2 candidate (pending S6): {', '.join(item['relations'])}."
    marker = f"**English:** {chinese}"
    assert rendered.count(marker) == 1
    return rendered.replace(marker, f"**English:** {english}", 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Gustav III, title-only Earl of Halifax, and Leopold Duke of Lorraine direct person endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    template.DATE, template.ANCHOR, template.PROCESS_REF = DATE, ANCHOR, PROCESS_REF
    template.TARGETS = TARGETS
    base, sync = template.helper.base, template.helper.base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    main_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    cards = {item["card"]: build_card(item) for item in TARGETS}
    card_paths = {item["card"]: ROOT / item["card"] for item in TARGETS}

    if all(main_by_id[item["primary"]].get("ku_id") == item["ku"] for item in TARGETS):
        for item in TARGETS:
            assert item["ku"] in manifest_by_ku and item["card"] in accepted_paths
            assert card_paths[item["card"]].read_text(encoding="utf-8-sig") == cards[item["card"]]
            ext = [row for row in alignments if row.get("candidate_id") == item["primary"] and row.get("external_source")]
            assert len(ext) == (1 if item["external"] else 0)
        print("ALREADY REGISTERED: all three person groups, mappings, and external identity rows are present.")
        return 0

    index_root = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"
    for item in TARGETS:
        candidate, row = candidate_by_id[item["primary"]], main_by_id[item["primary"]]
        assert candidate.get("suggested_type") == "person"
        assert (candidate.get("canonical_name"), candidate.get("index_entry_id"), candidate.get("index_page_range")) == (item["canonical_name"], item["entry"], item["pages"])
        assert row.get("decision") == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == item["old_group"]
        assert item["ku"] not in manifest_by_ku and item["card"] not in accepted_paths and not card_paths[item["card"]].exists()
        members = [r["candidate_id"] for r in alignments if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == item["old_group"]]
        assert members == [item["primary"]], (item["primary"], members)
        filename, index_id = item["entry"].split("#", 1)
        lines = (index_root / filename).read_text(encoding="utf-8-sig").splitlines()
        indexed = next(csv.reader([lines[int(index_id) + 1]]))
        assert indexed[0] == item["index_name"] and item["pages"] in indexed[-1]
        direct = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and item["primary"] in (r.get("subject_candidate_id"), r.get("object_candidate_id"))}
        assert direct == set(item["endpoints"]), (item["primary"], sorted(direct))
        for statement_id, expected in item["endpoints"].items():
            row = statement_by_id[statement_id]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == expected
        for entry in item["sources"]:
            source_text = (ROOT / entry["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", entry["quote"]) in re.sub(r"\s+", " ", source_text), (item["primary"], entry["span"])
        ext = [r for r in alignments if r.get("candidate_id") == item["primary"] and r.get("external_source")]
        assert not ext

    before_stats = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    max_aln = max((int(m.group(1)) for row in alignments if (m := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))), default=0)
    for item in TARGETS:
        row = next(r for r in planned_alignments if r.get("candidate_id") == item["primary"] and not r.get("external_source"))
        row["resolution_note"] = f"source_ref=candidate={item['primary']}; index_entry={item['entry']}; index_pages={item['pages']}; group={item['group']}; {item['s3_note']}"
        row["process_ref"] = PROCESS_REF
        row["ku_id"] = item["ku"]
        row["resolution_note"] += f" S4 registration ({DATE}): group {item['group']} -> {item['ku']}; source-backed person registration only; direct S2 relation candidates remain for S6."
        if item["external"]:
            ext = item["external"]
            assert not any(r.get("candidate_id") == item["primary"] and r.get("external_source") == ext["source"] for r in planned_alignments)
            max_aln += 1
            ext_note = f"Identity comparison only: {ext['scope']} Compared with the book index/body anchor for {item['primary']}; this does not verify the linked S2 claim. S4 registration maps this identity row to {item['ku']} under {item['group']}."
            planned_alignments.append({
                "alignment_id": f"aln-{max_aln:04d}", "candidate_id": item["primary"], "ku_id": item["ku"],
                "external_source": ext["source"], "external_id": ext["id"], "decision": "new",
                "accessed_date": DATE, "process_ref": PROCESS_REF, "legacy_ku_id": "", "resolution_note": ext_note,
            })
        planned_manifest.append({"ku_id": item["ku"], "type": "person", "canonical_name": item["name_zh"], "name_en": item["name_en"], "source_task": TASK, "card_path": item["card"]})
        planned_accepted = base.insert_accepted(planned_accepted, item["card"])
    planned_manifest.sort(key=lambda row: row["ku_id"])

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    count = len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + count
    assert totals["registered_members"] == before_totals["registered_members"] + count
    assert totals["pending_groups"] == before_totals["pending_groups"] - count
    assert totals["pending_members"] == before_totals["pending_members"] - count
    assert len(planned_manifest) == len(manifest) + count

    additions, cards_with_tables = template.extract_card_fields(cards)
    name_fields = sum(len(item["name_rows"]) for item in TARGETS)
    external_count = sum(1 for item in TARGETS if item["external"])
    relation_count = sum(len(item["relations"]) for item in TARGETS)
    assert cards_with_tables == count and len(additions) == name_fields + external_count
    assert sum(row.get("evidence_status") == "source_backed" for row in additions) == name_fields
    assert sum(row.get("evidence_status") == "unverified" for row in additions) == external_count
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    current = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) for row in current}
    ids = {row.get("enrichment_id", "") for row in current}
    max_enr = max((int(m.group(1)) for value in ids if (m := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for number, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_enr + number:05d}"
        assert (row["ku_id"], row["field"], row["value"], row.get("source_id", "")) not in keys
        assert row["enrichment_id"] not in ids
    planned_enrichment = enrichment_text.rstrip("\r\n") + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in additions) + "\n"

    process_text = base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3身份复核与S4人物登记：Gustav III、Halifax与Leopold of Lorraine（{DATE}）\n\n"
    process_text += "- cand-1283（G.csv#193）：第15章p.366正文只称King of Sweden，索引列Gustavus III of Sweden。瑞典国家档案馆《瑞典传记辞典》记录13317列Gustav III为瑞典国王（1746–1792，在位1771–1792），与1777年语境相符。该身份与cand-1284 Gustavus Adolphus（Gustav II Adolf，1611–1632）分开；未匹配现有KU，判new并登记为Gustav III of Sweden。外证不验证认捐陈述。\n"
    process_text += "- cand-1286（H.csv#1）：重申new人物身份组，但名称严格保留为未具名Earl of Halifax。第10章p.286确认其在Queen’s Bed Chamber委托叙述中的发言角色；未查得足以识别个人的跨章/外部锚点，也不映射至具名继承人。\n"
    process_text += "- cand-1441（L.csv#99）：修正本日早先‘仅有爵号、待身份锚点’的S4说明。第9章p.267及索引只给出Duke of Lorraine；Griffin, ‘Duke Leopold of Lorraine,’ The Historical Journal 65, no. 5 (2022), pp.1244–1261, DOI 10.1017/S0018246X2100090X, §I and n.26将Leopold (1679–1729)与Ferdinando-Carlo Gonzaga继承及1708年事件相连，足以识别本候选。与cand-1398（Holy Roman Emperor Leopold I）、cand-1397/cand-8097（Pietro Leopoldo of Tuscany）及cand-1399（Leopold Wilhelm）分开。身份由pending改为new；无现有精确KU，登记为Leopold, Duke of Lorraine。\n"
    process_text += "- cand-1441的身份匹配不裁决Haskell‘successfully established his claim’与Griffin所述未取得Mantua、Monferrato之间的表述差异；该关系候选仍待S6解释。cand-11467 ‘Gonzaga effects’仍无支持类型，保持undecided，不建KU。\n"
    for item in TARGETS:
        relations = ", ".join(item["relations"])
        external = f"；外部身份记录：{item['external']['source']}（{item['external']['id']}）" if item["external"] else "；不作外部身份映射"
        process_text += f"- {item['primary']}（{item['group']}）→ [{item['name_zh']}（{item['name_en']}）](../../../04-knowledge/{item['ku']}.md){external}；直接S2关系候选{relations}留待S6逐条裁决，不登记正式关系。\n"
    process_text += (
        f"\n本批确认/更正3项S3身份组并登记3个new person KU、3条候选映射、{name_fields}条source_backed名称字段及{external_count}条外部身份记录；"
        f"{relation_count}条直接S2关系候选留待S6。未新增正式关系、来源登记或candidate-backlog项。"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为"
        f"{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。\n"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S3身份复核与S4人物登记：Gustav III、Halifax与Leopold of Lorraine（{DATE}）\n\n"
        "登记Gustav III of Sweden（与Gustavus Adolphus分开）、未具名Earl of Halifax及Leopold, Duke of Lorraine三个new人物组。"
        "Lorraine候选由待证改为以Cambridge学术文章支持的身份匹配；Haskell继承请求的表述差异仍留S6，cand-11467仍未分类。"
        f"三条直接S2关系候选待S6；本批未新增正式关系。名称字段={name_fields}，外部身份行={external_count}，KU={len(planned_manifest)}。"
        f"详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-gustavus-halifax-lorraine-") as temp_name:
        temp = Path(temp_name)
        alignment_stage, manifest_stage = temp / "alignment.csv", temp / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: alignment_stage.read_bytes(), MANIFEST: manifest_stage.read_bytes(),
            ENRICHMENT: template.with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: template.with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: template.with_bom(process_text.rstrip("\r\n") + "\n", PROCESS.read_bytes()),
            RESULT: template.with_bom(result_text.rstrip("\r\n") + "\n", RESULT.read_bytes()),
        }
        for item in TARGETS:
            writes[ROOT / item["card"]] = template.with_bom(cards[item["card"]])
    if args.dry_run:
        print(f"S3/S4 dry-run passed: S3_decisions=3 new; new_groups={count}; candidate_mappings={count}; source_backed_name_fields={name_fields}; external_identity_rows={external_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}; no files changed")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
        return 0
    originals = {path: path.read_bytes() if path.exists() else None for path in writes}
    try:
        for path, content in writes.items():
            template.atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                template.atomic_write(path, content)
        raise
    print(f"applied: S3_decisions=3 new; new_groups={count}; candidate_mappings={count}; source_backed_name_fields={name_fields}; external_identity_rows={external_count}; relation_candidates_pending={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
