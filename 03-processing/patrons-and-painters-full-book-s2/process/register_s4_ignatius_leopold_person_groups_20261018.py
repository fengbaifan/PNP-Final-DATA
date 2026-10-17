from __future__ import annotations

import argparse
import csv
import json
import re
import sys
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
ANCHOR = "s4-person-direct-endpoints-ignatius-leopold-groups-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [
    {
        "primary": "cand-1309",
        "members": ["cand-1309"],
        "entry": "I.csv#0",
        "index_name": "Ignatius, St",
        "canonical_name": "Ignatius, St",
        "pages": "64",
        "group": "new-person:st-ignatius-jesuit-founder-20261018",
        "ku": "units/persons/ignatius-of-loyola",
        "card": "04-knowledge/units/persons/ignatius-of-loyola.md",
        "name_zh": "圣依纳爵·罗耀拉",
        "name_en": "Ignatius of Loyola",
        "name_rows": [
            ("索引名", "Ignatius, St", "S1（索引I.csv#0）"),
            ("正文姓名形式", "Ignatius；St Ignatius", "S2（第3章p.64；第20章后记p.399）"),
        ],
        "sources": [
            src(
                "第3章第I节；印刷页64",
                "Haskell称教宗格列高利十五世主持将耶稣会的Ignatius与Francis Xavier及Philip Neri列为圣人的封圣仪式。",
                "One of this Pope’s most important actions was to decree the canonisation of the two great Jesuits, Ignatius and Francis Xavier, and the founder of the Oratorians Philip Neri",
                "02-sources/02-Markdown/03_CHP-3_sec_i.md",
                "line 18; print p.64",
            ),
            src(
                "第20章后记；印刷页399",
                "Haskell转述Buser对Jerome Nadal福音默想书插图及其影响的讨论，并称该书由St Ignatius委托。",
                "Drawing attention to the engravings in a book of gospel meditations by the Jesuit Jerome Nadal, which had been commissioned by St Ignatius himself",
                "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "line 40; print p.399",
            ),
        ],
        "zh": "本卡将索引I.csv#0的“Ignatius, St”与第3章p.64及第20章后记p.399所称Ignatius／St Ignatius归为同一人物；外部身份入口支持展开为Ignatius of Loyola。此身份对应不独立核实Haskell关于封圣、委托或艺术影响的陈述。",
        "en": "This card groups the index form “Ignatius, St” (I.csv#0) with Ignatius / St Ignatius in chapter 3, p.64, and the postscript, p.399; the external identity record supports the expanded name Ignatius of Loyola. The identity match does not independently verify Haskell’s statements about canonisation, the commission, or artistic influence.",
        "context_zh": "第3章将Ignatius置于耶稣会创立者语境；后记称Nadal福音默想书由St Ignatius委托。八条直接S2关系候选均保留原文语境与证据，待S6逐条裁决。",
        "context_en": "Chapter 3 places Ignatius in the context of the Jesuit founder; the postscript says St Ignatius commissioned Nadal’s gospel-meditation book. All eight direct S2 relation candidates retain their source context and evidence for individual S6 review.",
        "relations": [
            "st-chp3-seci-l16-24-gregory-canonisation-ignatius",
            "st-chp3-seciv-l130-139-scenes-depict-ignatius",
            "st-chp3-seciv-l141-150-pozzo-adapted-reference-to-ignatius",
            "st-chp3-seciv-l141-150-pozzo-explained-honour-to-ignatius",
            "st-chp3-seciv-l152-163-chapel-conceived-for-founder",
            "st-chp20-p399-nadal-engravings-commission-and-influence",
            "st-chp3-seciv-l141-150-ignatius-encouraged-disciples-rhetorical-question",
            "st-chp3-seciv-l141-150-fresco-depicts-ignatius-transmitting-ray",
        ],
        "endpoints": {
            "st-chp3-seci-l16-24-gregory-canonisation-ignatius": ("cand-1455", "cand-1309", "decreed_canonisation_of"),
            "st-chp3-seciv-l130-139-scenes-depict-ignatius": ("cand-5365", "cand-1309", "depicts_aspects_of_ignatius_sojourn_in_this_world_and_the_next"),
            "st-chp3-seciv-l141-150-pozzo-adapted-reference-to-ignatius": ("cand-2034", "cand-1309", "adapted_church_reference_to_st_ignatius"),
            "st-chp3-seciv-l141-150-pozzo-explained-honour-to-ignatius": ("cand-5074", "cand-1309", "meant_redeemer_honoured_ignatius_for_glory_of_his_name"),
            "st-chp3-seciv-l152-163-chapel-conceived-for-founder": ("cand-5236", "cand-1309", "described_as_elaborate_chapel_dedicated_to_order_founder"),
            "st-chp20-p399-nadal-engravings-commission-and-influence": ("cand-1309", "cand-10922", "st_ignatius_commissioned_nadal_meditation_book_whose_engravings_influenced_jesuit_art"),
            "st-chp3-seciv-l141-150-ignatius-encouraged-disciples-rhetorical-question": ("cand-1309", "cand-5393", "reported_ignatius_exhortation_to_disciples"),
            "st-chp3-seciv-l141-150-fresco-depicts-ignatius-transmitting-ray": ("cand-5074", "cand-1309", "depicts_ignatius_receiving_and_transmitting_ray"),
        },
        "external": {
            "candidate_id": "cand-1309",
            "source": "Vatican, Congregation for Catholic Education",
            "id": "https://www.vatican.va/roman_curia/congregations/ccatheduc/documents/rc_con_ccatheduc_doc_20021119_press-release_en.html",
            "label": "Saint Ignatius of Loyola",
            "url": "https://www.vatican.va/roman_curia/congregations/ccatheduc/documents/rc_con_ccatheduc_doc_20021119_press-release_en.html",
            "scope": "身份消歧；用于将书内St Ignatius对应至Ignatius of Loyola，不验证书内封圣、委托或艺术影响陈述。",
        },
    },
    {
        "primary": "cand-1397",
        "members": ["cand-1397", "cand-8097"],
        "entry": "L.csv#54",
        "index_name": "Leopold I, Grand Duke of Tuscany",
        "canonical_name": "Leopold I, Grand Duke of Tuscany",
        "pages": "366, 371",
        "group": "new-person:pietro-leopoldo-grand-duke-of-tuscany-20261018",
        "ku": "units/persons/pietro-leopoldo-grand-duke-of-tuscany",
        "card": "04-knowledge/units/persons/pietro-leopoldo-grand-duke-of-tuscany.md",
        "name_zh": "彼得罗·莱奥波尔多",
        "name_en": "Pietro Leopoldo",
        "name_rows": [
            ("索引名", "Leopold I, Grand Duke of Tuscany", "S1（索引L.csv#54）"),
            ("正文称谓", "Grand Duke of Tuscany", "S2（第15章p.366）"),
            ("展览题名中的姓名与头衔", "Pietro Leopoldo, Arciduca d'Austria", "S2（第8章p.203注3）"),
        ],
        "sources": [
            src(
                "第15章第II节；印刷页366",
                "Haskell称托斯卡纳大公为帕多瓦Prato della Valle雕像计划中的两座雕像（Petrarch与Galileo）付款。",
                "The Grand Duke of Tuscany paid for two—Petrarch and Galileo",
                "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "line 21; print p.366",
            ),
            src(
                "第8章第II节注3；印刷页203",
                "Haskell所引1767年展览题名将Pietro Leopoldo列为Arciduca d’Austria。",
                "Il trionfo Jelle Bell'Arti renduto gloriosissimo sotto gli auspicj delle LL.AA.RR. Pietro Leopoldo Arciduca d'Austria . . . e Maria Luisa di Borbone.",
                "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "line 459; print p.203 n.3",
            ),
        ],
        "zh": "本卡将索引L.csv#54的“Leopold I, Grand Duke of Tuscany”与第8章p.203注3展览题名中的Pietro Leopoldo合为一人。Treccani传记记录支持其为Pietro Leopoldo；第15章关于雕像付款的说法仍只是Haskell的原书陈述。",
        "en": "This card groups the index entry “Leopold I, Grand Duke of Tuscany” (L.csv#54) with Pietro Leopoldo named in the exhibition title cited in chapter 8, p.203 n.3. The Treccani biography supports the identity as Pietro Leopoldo; the chapter 15 statement about paying for statues remains Haskell’s book report.",
        "context_zh": "第15章p.366称Grand Duke of Tuscany为Petrarch与Galileo两座雕像付款；该句及第8章展览题名均保留各自来源语境。两条直接S2关系候选待S6逐条裁决；本卡与神圣罗马帝国皇帝Leopold I分立。",
        "context_en": "Chapter 15, p.366, says the Grand Duke of Tuscany paid for the statues of Petrarch and Galileo; that statement and the chapter 8 exhibition title retain their separate source contexts. Both direct S2 relation candidates remain for individual S6 review; this person is distinct from Emperor Leopold I.",
        "relations": [
            "st-chp15-p366-grandduke-funds-petrarch-galileo-statues",
            "st-chp15-p366-grandduke-pays-for-galileo-statue",
        ],
        "endpoints": {
            "st-chp15-p366-grandduke-funds-petrarch-galileo-statues": ("cand-1397", "cand-10496", "grand_duke_of_tuscany_paid_for_petrarch_statue"),
            "st-chp15-p366-grandduke-pays-for-galileo-statue": ("cand-1397", "cand-10497", "grand_duke_of_tuscany_paid_for_galileo_statue"),
        },
        "external": {
            "candidate_id": "cand-1397",
            "source": "Treccani, Dizionario Biografico degli Italiani",
            "id": "https://www.treccani.it/enciclopedia/pietro-leopoldo-d-asburgo-lorena-granduca-di-toscana-poi-imperatore-del-sacro-romano-impero-come-leopoldo-ii_%28Dizionario-Biografico%29/",
            "label": "Pietro Leopoldo d’Asburgo-Lorena",
            "url": "https://www.treccani.it/enciclopedia/pietro-leopoldo-d-asburgo-lorena-granduca-di-toscana-poi-imperatore-del-sacro-romano-impero-come-leopoldo-ii_%28Dizionario-Biografico%29/",
            "scope": "身份消歧；支持1765年起任托斯卡纳大公、后来成为皇帝Leopold II的Pietro Leopoldo身份，不验证书中雕像付款陈述。",
        },
    },
    {
        "primary": "cand-1398",
        "members": ["cand-1398"],
        "entry": "L.csv#55",
        "index_name": "Leopold I, Holy Roman Emperor",
        "canonical_name": "Leopold I, Holy Roman Emperor",
        "pages": "193",
        "group": "new-person:leopold-i-holy-roman-emperor-20261018",
        "ku": "units/persons/leopold-i-holy-roman-emperor",
        "card": "04-knowledge/units/persons/leopold-i-holy-roman-emperor.md",
        "name_zh": "利奥波德一世",
        "name_en": "Leopold I, Holy Roman Emperor",
        "name_rows": [
            ("索引名", "Leopold I, Holy Roman Emperor", "S1（索引L.csv#55）"),
            ("正文姓名形式", "Emperor Leopold I；Leopold", "S2（第7章p.193）"),
        ],
        "sources": [
            src(
                "第7章第IV节；印刷页193",
                "Haskell称Archduke Leopold Wilhelm于1662年去世后将财产留给其侄、皇帝Leopold I，并称Leopold统治时期为1658至1705年。",
                "On his death in 1662 the Archduke left all his possessions to his nephew, the Emperor Leopold I. Leopold, who ruled from 1658 to 1705",
                "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "lines 9–10; print p.193",
            ),
        ],
        "zh": "本卡登记索引L.csv#55及第7章p.193所称皇帝Leopold I。Deutsche Biographie／GND身份记录与该人物及1658—1705年的统治期相符；本卡不据此独立核实原书所述赞助活动。",
        "en": "This card registers Emperor Leopold I as named in index L.csv#55 and chapter 7, p.193. The Deutsche Biographie / GND identity record matches the ruler and the 1658–1705 reign dates; this card does not independently verify the book’s patronage statements.",
        "context_zh": "第7章p.193将Leopold I与Leopold Wilhelm的遗产继承相连，并记其委托Burnacini设计宫殿新翼及舞台布景。四条直接S2关系候选保留待S6逐条裁决；与Pietro Leopoldo（后来成为Leopold II）分立。",
        "context_en": "Chapter 7, p.193, connects Leopold I with Leopold Wilhelm’s bequest and says he commissioned a palace wing and stage sets from Burnacini. All four direct S2 relation candidates remain for individual S6 review; he is distinct from Pietro Leopoldo, later Emperor Leopold II.",
        "relations": [
            "st-chp7-p193-leopold-bequest",
            "st-chp7-p193-leopold-commissions-stage-sets",
            "st-chp7-p193-leopold-commissions-wing",
            "st-chp7-p193-leopold-i-patronage",
        ],
        "endpoints": {
            "st-chp7-p193-leopold-bequest": ("cand-1399", "cand-1398", "left_possessions_to_nephew"),
            "st-chp7-p193-leopold-commissions-stage-sets": ("cand-1398", "cand-7151", "commissioned_from_burnacini"),
            "st-chp7-p193-leopold-commissions-wing": ("cand-1398", "cand-7150", "commissioned_from_burnacini"),
            "st-chp7-p193-leopold-i-patronage": ("cand-1398", "cand-3461", "patronage_and_turn_to_italian_artists"),
        },
        "external": {
            "candidate_id": "cand-1398",
            "source": "Deutsche Biographie / GND",
            "id": "118571869",
            "label": "Leopold I",
            "url": "https://www.deutsche-biographie.de/gnd118571869.html?language=en",
            "scope": "身份消歧；GND 118571869记录与索引及第7章p.193所指人物对应，不验证赞助、委托或继承陈述。",
        },
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three S3 person groups (four candidate mappings) for Ignatius and the two distinct Leopolds.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    template.TARGETS = TARGETS
    template.DATE = DATE
    template.ANCHOR = ANCHOR
    template.PROCESS_REF = PROCESS_REF
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
    cards = {target["card"]: template.make_card(target) for target in TARGETS}

    for target in TARGETS:
        assert target["ku"] not in manifest_by_ku or manifest_by_ku[target["ku"]].get("card_path") == target["card"]
        for cid in target["members"]:
            candidate, alignment = candidate_by_id[cid], main_by_id[cid]
            assert candidate.get("suggested_type") == "person"
            assert alignment.get("decision") == "new"
            assert sync.get_group(alignment.get("resolution_note", "")) == target["group"]
            assert not alignment.get("ku_id") or alignment.get("ku_id") == target["ku"]
        actual_members = [
            row["candidate_id"] for row in main_rows
            if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == target["group"]
        ]
        assert actual_members == target["members"], (target["group"], actual_members)
        index_file, _index_id = target["entry"].split("#", 1)
        index_rows = template.helper.base.read_index_rows(index_file)
        hits = [row for row in index_rows if row.get("Main Entry") == target["index_name"] and target["pages"] == row.get("Page Numbers")]
        assert len(hits) == 1, (target["entry"], hits)
        expected_direct = set(target["endpoints"])
        actual_direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and (row.get("subject_candidate_id") in target["members"] or row.get("object_candidate_id") in target["members"])
        }
        assert actual_direct == expected_direct, (target["group"], sorted(actual_direct), sorted(expected_direct))
        for statement_id, expected in target["endpoints"].items():
            row = statement_by_id[statement_id]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == expected
        for item in target["sources"]:
            text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            normalized_text = re.sub(r"\s+", " ", text)
            normalized_quote = re.sub(r"\s+", " ", item["quote"])
            assert normalized_quote in normalized_text or all(
                part in normalized_text for part in [normalized_quote[:32], normalized_quote[-24:]]
            ), (target["primary"], item["span"])
        card_path = ROOT / target["card"]
        alignment_by_state = [main_by_id[cid].get("ku_id", "") == target["ku"] for cid in target["members"]]
        registered_state = bool(alignment_by_state) and all(alignment_by_state)
        assert all(alignment_by_state) or not any(alignment_by_state), (target["group"], alignment_by_state)
        assert (target["card"] in accepted_paths) == card_path.exists() == registered_state
        if registered_state:
            assert card_path.read_text(encoding="utf-8-sig") == cards[target["card"]]
        else:
            assert target["ku"] not in manifest_by_ku
        external = target["external"]
        ext_matches = [
            row for row in alignments if row.get("candidate_id") == external["candidate_id"]
            and row.get("external_source") == external["source"] and row.get("external_id") == external["id"]
        ]
        assert len(ext_matches) == 1 and ext_matches[0].get("decision") == "new"
        assert not ext_matches[0].get("ku_id") or ext_matches[0].get("ku_id") == target["ku"]

    all_registered = all(all(main_by_id[cid].get("ku_id") == t["ku"] for cid in t["members"]) for t in TARGETS)
    if all_registered:
        for target in TARGETS:
            ext = target["external"]
            ext_row = next(r for r in alignments if r.get("candidate_id") == ext["candidate_id"] and r.get("external_source") == ext["source"] and r.get("external_id") == ext["id"])
            assert ext_row.get("ku_id") == target["ku"]
            assert manifest_by_ku[target["ku"]].get("card_path") == target["card"]
        print("ALREADY REGISTERED: the three person groups, four candidate mappings, and three authority rows are present.")
        return 0
    assert not any(main_by_id[cid].get("ku_id") for t in TARGETS for cid in t["members"]), "partial registration requires explicit reconciliation"

    before_stats = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    member_count = sum(len(target["members"]) for target in TARGETS)
    relation_count = sum(len(target["relations"]) for target in TARGETS)
    external_count = sum(bool(target.get("external")) for target in TARGETS)
    for target in TARGETS:
        for cid in target["members"]:
            row = planned_by_id[cid]
            row["ku_id"] = target["ku"]
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] += f" S4 registration ({DATE}): group {target['group']} -> {target['ku']}; source-backed person identity registration; direct S2 relation candidates remain for S6."
        planned_manifest.append({
            "ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"],
            "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"],
        })
        planned_accepted = template.helper.base.insert_accepted(planned_accepted, target["card"])
        ext = target["external"]
        ext_row = next(row for row in planned_alignments if row.get("candidate_id") == ext["candidate_id"] and row.get("external_source") == ext["source"] and row.get("external_id") == ext["id"])
        ext_row["ku_id"] = target["ku"]
        ext_row["process_ref"] = PROCESS_REF
        ext_row["resolution_note"] += f" S4 registration maps this authority identity row to {target['ku']} under {target['group']}."
    planned_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == before_totals["registered_members"] + member_count
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - member_count
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    additions, cards_with_tables = template.extract_card_fields(cards)
    expected_name_fields = sum(len(target["name_rows"]) for target in TARGETS)
    assert cards_with_tables == len(TARGETS)
    assert len(additions) == expected_name_fields + external_count, (len(additions), expected_name_fields, external_count)
    assert sum(row.get("evidence_status") == "source_backed" for row in additions) == expected_name_fields
    assert sum(row.get("evidence_status") == "unverified" for row in additions) == external_count
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    existing_enrichment = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) for row in existing_enrichment}
    existing_ids = {row.get("enrichment_id", "") for row in existing_enrichment}
    max_id = max((int(match.group(1)) for value in existing_ids if (match := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for number, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + number:05d}"
        key = (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", ""))
        assert key not in natural_keys
        assert row["enrichment_id"] not in existing_ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in additions) + "\n"

    process_text = template.helper.base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Ignatius与两位Leopold（{DATE}）\n\n"
    for target in TARGETS:
        relation_text = ", ".join(target["relations"])
        candidate_text = "、".join(f"`{cid}`" for cid in target["members"])
        process_text += (
            f"- {candidate_text}（`{target['group']}`）→ [{target['name_zh']}（{target['name_en']}）]"
            f"(../../../04-knowledge/{target['ku']}.md)。索引{target['entry']}及所列书内页段构成来源身份依据；"
            f"外部身份入口仅作消歧（{target['external']['source']}）；直接S2关系候选：{relation_text}，留待S6逐条裁决。无正式关系写入。\n"
        )
    process_text += (
        f"\n本批登记{len(TARGETS)}个S3 new人物组、{member_count}条候选映射、{expected_name_fields}条source_backed名称字段和"
        f"{external_count}条unverified外部身份导航字段；外部标识只留在alignment.csv。{relation_count}条直接S2关系候选继续待S6；"
        "Pietro Leopoldo（cand-1397、cand-8097）合为一组，与Holy Roman Emperor Leopold I（cand-1398）分开。本批未新增正式关系或扩写原书事实。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为"
        f"{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接端点登记：Ignatius与两位Leopold（{DATE}）\n\n"
        "登记Ignatius of Loyola、Pietro Leopoldo（cand-1397与cand-8097共用一KU）及Holy Roman Emperor Leopold I三组人物身份。"
        f"本批{member_count}条候选映射、{external_count}条外部身份行和{relation_count}条直接S2关系候选；身份外证仅用于消歧，关系仍待S6，未新增正式边。"
        f"当前KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    import tempfile
    with tempfile.TemporaryDirectory(prefix="pnp-s4-ignatius-leopold-") as temp_name:
        temp = Path(temp_name)
        a_stage, m_stage = temp / "alignment.csv", temp / "ku-manifest.csv"
        sync.write_csv(a_stage, alignment_fields, planned_alignments)
        sync.write_csv(m_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: a_stage.read_bytes(),
            MANIFEST: m_stage.read_bytes(),
            ENRICHMENT: template.with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: template.with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: template.with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: template.with_bom(result_text + "\n", RESULT.read_bytes()),
        }
        for target in TARGETS:
            writes[ROOT / target["card"]] = template.with_bom(cards[target["card"]])

    if args.dry_run:
        print(f"S4 dry-run passed: groups={len(TARGETS)}; candidate_mappings={member_count}; name_fields={expected_name_fields}; external_identity_rows={external_count}; direct_relation_candidates={relation_count}.")
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
    print(f"applied: groups={len(TARGETS)}; candidate_mappings={member_count}; name_fields={expected_name_fields}; external_identity_rows={external_count}; relation_candidates={relation_count}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
