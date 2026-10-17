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
ANCHOR = "s4-person-direct-endpoints-qr-middle-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def target(primary, entry, index_name, pages, group, slug, name_zh, name_en, name_rows, sources, zh, en, context_zh, context_en, relations, endpoints):
    return {
        "primary": primary, "entry": entry, "index_name": index_name, "canonical_name": index_name, "pages": pages,
        "group": group, "ku": f"units/persons/{slug}", "card": f"04-knowledge/units/persons/{slug}.md",
        "name_zh": name_zh, "name_en": name_en, "name_rows": name_rows, "sources": sources,
        "zh": zh, "en": en, "context_zh": context_zh, "context_en": context_en,
        "relations": relations, "endpoints": endpoints, "external": None,
    }


TARGETS = [
    target(
        "cand-2138", "Q-R.csv#65", "Rezzonico, Lodovico", "254", "new-person:lodovico-rezzonico-dd8b30f008", "lodovico-rezzonico",
        "洛多维科·雷佐尼科", "Lodovico Rezzonico",
        [("索引名", "Rezzonico, Lodovico", "S1（索引Q-R.csv#65）"), ("正文姓名形式", "Lodovico Rezzonico", "S2（第9章p.254）")],
        [template.source("第9章导论；印刷页254", "Haskell称Lodovico Rezzonico于1758年与Faustina Savorgnan结婚，并称其父为Aurelio、叔父为后来当选教皇的Carlo。", "married Lodovico Rezzonico, second son", "02-sources/02-Markdown/09_CHP-9_intro.md", "line 137; print p.254"), template.source("第9章导论；印刷页254", "同段明确称Aurelio为Lodovico之父，并称其兄弟Carlo后来当选为Clement XIII。", "Aurelio, Lodovico’s father", "02-sources/02-Markdown/09_CHP-9_intro.md", "lines 137–139; print p.254")],
        "本卡按索引Q-R.csv#65登记Lodovico Rezzonico。第9章p.254称他于1758年与Faustina Savorgnan结婚；同段将Aurelio称为其父、Carlo称为其叔父。此人分别于Aurelio Rezzonico和Carlo Rezzonico既有KU区分。",
        "This card registers Lodovico Rezzonico under index Q-R.csv#65. Chapter 9, p.254, says he married Faustina Savorgnan in 1758 and identifies Aurelio as his father and Carlo as his uncle. He remains distinct from the existing KUs for Aurelio Rezzonico and Carlo Rezzonico.",
        "索引页段和正文全名支持书内组；亲属身份按原文保留，不据此扩展家族成员。",
        "The indexed page and full body name support the source-local group; kinship is preserved as stated without expanding family membership.",
        ["st-chp9-p254-aurelio-father-of-lodovico", "st-chp9-p254-faustina-lodovico-marriage"],
        {"st-chp9-p254-aurelio-father-of-lodovico": ("cand-2136", "cand-2138", "father_of_lodovico_rezzonico"), "st-chp9-p254-faustina-lodovico-marriage": ("cand-2378", "cand-2138", "married_in_1758")},
    ),
    target(
        "cand-2139", "Q-R.csv#66", "Ribera, Don Ferdinando Afan de", "136", "new-person:afan-de-ferdinando-ribera-369de73a8f", "don-ferdinando-afan-de-ribera",
        "唐·费迪南多·阿凡·德·里贝拉", "Don Ferdinando Afan de Ribera",
        [("索引名", "Ribera, Don Ferdinando Afan de", "S1（索引Q-R.csv#66）"), ("正文称名", "Don Ferdinando", "S2（第5章p.135）"), ("正文续页姓名形式", "Afan de Ribera", "S2（第5章p.136）"), ("正文称谓", "the Viceroy of Naples", "S2（第5章p.136）")],
        [template.source("第5章第III节；印刷页135", "Haskell称Van Laer将八幅动物版画献给Don Ferdinando；身份在下一页续接。", "the artist dedicated a series of eight engravings of animals to Don Ferdinando", "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "line 34; print p.135"), template.source("第5章第III节；印刷页136", "续页将Don Ferdinando续称为Afan de Ribera，并称其为那不勒斯总督。", "Afan de Ribera, the Viceroy of Naples", "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "line 37; print p.136")],
        "本卡按索引Q-R.csv#66登记Don Ferdinando Afan de Ribera。第5章p.135以Don Ferdinando指称版画的受献者，p.136续文补出Afan de Ribera及那不勒斯总督称谓；这是书内身份识别，不添加外部匹配。",
        "This card registers Don Ferdinando Afan de Ribera under index Q-R.csv#66. Chapter 5, p.135, refers to the dedicatee of the engravings as Don Ferdinando; the continuation on p.136 supplies Afan de Ribera and the title Viceroy of Naples. This is a source-local identification, with no external match added.",
        "候选cand-2139由两页续接语句明确识别；p.136的身份句是语境断言，不另立正式关系。",
        "Candidate cand-2139 is identified by the passage continued across the two pages; the p.136 identity sentence is contextual and creates no formal relation.",
        ["st-chp5-p135-van-laer-dedicated-eight-animal-engravings"],
        {"st-chp5-p135-van-laer-dedicated-eight-animal-engravings": ("cand-6132", "cand-2139", "dedicated_to")},
    ),
    target(
        "cand-2146", "Q-R.csv#73", "Ricchini, Francesco Maria", "215", "new-person:francesco-maria-ricchini-03415a916c", "francesco-maria-ricchini",
        "弗朗切斯科·马里亚·里基尼", "Francesco Maria Ricchini",
        [("索引名", "Ricchini, Francesco Maria", "S1（索引Q-R.csv#73）"), ("正文姓名形式", "Francesco Maria Ricchini", "S2（第8章第II节p.215）")],
        [template.source("第8章第II节；印刷页215", "Haskell称贝加莫圣母玛利亚教堂的穹顶由米兰建筑师Francesco Maria Ricchini于1612年规划。", "the dome which was planned by the Milanese architect Francesco Maria Ricchini in 1612", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "lines 13–14; print p.215")],
        "本卡按索引Q-R.csv#73登记建筑师Francesco Maria Ricchini。第8章p.215称他于1612年规划贝加莫圣母玛利亚教堂穹顶；规划与之后的灰泥覆盖及壁画装饰分开。",
        "This card registers architect Francesco Maria Ricchini under index Q-R.csv#73. Chapter 8, p.215, says he planned the dome of Santa Maria Maggiore in Bergamo in 1612; planning is distinct from the later stucco covering and fresco decoration.",
        "正文和索引均给出全名；不将规划者与之后施工、装饰者混同。",
        "The body and index both give his full name; the planner is kept distinct from later builders and decorators.",
        ["st-chp8-p215-ricchini-planned-dome-1612"],
        {"st-chp8-p215-ricchini-planned-dome-1612": ("cand-2146", "cand-7636", "planned_dome_in_1612")},
    ),
    target(
        "cand-2188", "Q-R.csv#115", "Richard, Abbé", "335", "new-person:abbe-richard-b9f32ee805", "abbe-richard",
        "阿贝·理查德", "Abbé Richard",
        [("索引名", "Richard, Abbé", "S1（索引Q-R.csv#115）"), ("正文称谓", "Abbé Richard", "S2（第13章导论p.335）")],
        [template.source("第13章导论；印刷页335", "Haskell称该版《耶路撒冷解放》受到Abbé Richard赞赏；注4将其引文指向Richard第二卷p.492，经Morazzoni转引。", "It was much admired by the Abbé Richard", "02-sources/02-Markdown/13_CHP-13_intro.md", "lines 37–39; print p.335")],
        "本卡登记索引Q-R.csv#115所列Abbé Richard。正文仅提供修院称谓与姓氏，没有给出名字；注4所引Richard卷册及Morazzoni转引未独立查阅。此书内人物与既有Richard Mead卡分开，不作外部身份匹配。",
        "This card registers Abbé Richard under index Q-R.csv#115. The body supplies only the ecclesiastical title and surname, not a given name; the cited Richard volume and Morazzoni intermediary were not independently consulted. This source-local person remains separate from the existing Richard Mead card, with no external identity match added.",
        "保留Abbé Richard的原书称谓；不给出未见于来源的名字。",
        "The source form Abbé Richard is retained; no given name absent from the source is supplied.",
        ["st-chp13-p335-gerusalemme-admired-by-richard"],
        {"st-chp13-p335-gerusalemme-admired-by-richard": ("cand-2188", "cand-9990", "admired_gerusalemme_liberata_edition")},
    ),
    target(
        "cand-2198", "Q-R.csv#125", "Rigaud, Hyacinthe", "285", "new-person:hyacinthe-rigaud-27fb3b4435", "hyacinthe-rigaud",
        "雅辛特·里戈", "Hyacinthe Rigaud",
        [("索引名", "Rigaud, Hyacinthe", "S1（索引Q-R.csv#125）"), ("正文姓氏形式", "Rigaud", "S2（第10章导论p.285）")],
        [template.source("第10章导论；印刷页285", "Haskell称Carriera在巴黎期间遇见Rigaud与Watteau，并称两人表达了对她的赞赏。正文仅用Rigaud姓氏，名字形式来自索引。", "She met Rigaud and Watteau, both of whom expressed their deep admiration", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 186; print p.285")],
        "本卡按索引Q-R.csv#125登记Hyacinthe Rigaud。第10章p.285正文只用Rigaud姓氏，并称Carriera遇见他及Watteau、两人表达赞赏；未添加外部身份记录。",
        "This card registers Hyacinthe Rigaud under index Q-R.csv#125. Chapter 10, p.285, uses only the surname Rigaud and says Carriera met him and Watteau, both expressing admiration; no external identity record is added.",
        "索引提供名字Hyacinthe，正文在对应页段只用姓氏Rigaud。",
        "The index supplies the given name Hyacinthe; the body passage on the indexed page uses only the surname Rigaud.",
        ["st-chp10-p285-carriera-met-artists"],
        {"st-chp10-p285-carriera-met-artists": ("cand-0581", "cand-2198", "met")},
    ),
]

CORRECTIONS = {
    "cand-2138": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2138 by identical normalized full-name/explicit-alias anchor (lodovico rezzonico), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#65 and p.254 body both give Lodovico Rezzonico; the same passage identifies Aurelio as his father and Carlo as his uncle. Keep distinct from those existing Rezzonico KUs. No external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2139": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2139 by identical normalized full-name/explicit-alias anchor (afan de ferdinando ribera), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#66 points to p.136; the body introduces Don Ferdinando at p.135 and continues on p.136 with Afan de Ribera, the Viceroy of Naples. This explicit source continuation supports the book-local identity; no external match is added. KU assignment remains for S4.",
    ),
    "cand-2146": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2146 by identical normalized full-name/explicit-alias anchor (francesco maria ricchini), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#73 and the chapter 8 p.215 body both give the full name Francesco Maria Ricchini in the dome-planning passage. No external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2188": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2188 by identical normalized full-name/explicit-alias anchor (abbe richard), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#115 locates p.335, where the body uses only Abbé Richard; no given name is supplied. The citation to Richard, volume II, p.492, is mediated through Morazzoni and was not independently checked. Keep distinct from Richard Mead; no external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2198": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2198 by identical normalized full-name/explicit-alias anchor (hyacinthe rigaud), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#125 supplies Hyacinthe and points to p.285, where the body mentions only Rigaud. The full display name is therefore index-derived and the source-local match remains unverified externally. No external identity source was accessed; KU assignment remains for S4.",
    ),
}

STATEMENT_QUALIFICATION_CORRECTIONS = {
    "st-chp5-p135-van-laer-dedicated-eight-animal-engravings": (
        "The dedicatee’s full name and office continue at p.136 L37; identity alignment remains an S3 task.",
        "The p.136 continuation identifies Don Ferdinando as Afan de Ribera, Viceroy of Naples; source-local S3 identity decision is recorded under cand-2139, without an external match.",
    ),
    "st-chp5-p136-complete-don-ferdinando-identification": (
        "This is a source identity claim retained for S3 alignment; it is not a relationship edge.",
        "This source identity claim completes the p.135 dedicatee and supports the source-local S3 group for cand-2139; it is not a relationship edge.",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct Q-R middle person S3 rationales and register five direct endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    template.TARGETS = TARGETS
    template.DATE, template.ANCHOR, template.PROCESS_REF = DATE, ANCHOR, PROCESS_REF
    base, sync = template.helper.base, template.helper.base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statement_text = STATEMENTS.read_text(encoding="utf-8-sig")
    statement_lines = statement_text.splitlines()
    statements = [json.loads(line) for line in statement_lines if line.strip()]
    statement_by_id = {r["statement_id"]: r for r in statements}
    cards = {t["card"]: template.make_card(t) for t in TARGETS}

    for t in TARGETS:
        candidate, row = candidate_by_id[t["primary"]], alignment_by_id[t["primary"]]
        assert candidate.get("suggested_type") == "person"
        assert (candidate.get("canonical_name"), candidate.get("index_entry_id"), candidate.get("index_page_range")) == (t["canonical_name"], t["entry"], t["pages"])
        assert row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == t["group"], t["primary"]
        assert not row.get("ku_id") or row.get("ku_id") == t["ku"]
        members = [r["candidate_id"] for r in alignments if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == t["group"]]
        assert members == [t["primary"]]
        filename, index_id = t["entry"].split("#", 1)
        index_lines = (ROOT / "02-sources/03-Index/03-2-Index-CSV" / filename).read_text(encoding="utf-8-sig").splitlines()
        index_row = next(csv.reader([index_lines[int(index_id) + 1]]))
        assert index_row[0] == t["index_name"] and t["pages"] in index_row[-1]
        direct = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == t["primary"] or r.get("object_candidate_id") == t["primary"])}
        assert direct == set(t["endpoints"]), (t["primary"], sorted(direct))
        for statement_id, expected in t["endpoints"].items():
            row = statement_by_id[statement_id]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == expected
        for item in t["sources"]:
            source = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", source), (t["primary"], item["span"])

    planned_alignments = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    for candidate_id, (old, new) in CORRECTIONS.items():
        row = planned_by_id[candidate_id]
        if old in row.get("resolution_note", ""):
            row["resolution_note"] = row["resolution_note"].replace(old, new, 1)
        else:
            assert new in row.get("resolution_note", ""), f"unexpected S3 rationale for {candidate_id}"

    corrected_statement_ids = set()
    planned_statement_lines = list(statement_lines)
    for i, line in enumerate(planned_statement_lines):
        if not line.strip():
            continue
        statement = json.loads(line)
        correction = STATEMENT_QUALIFICATION_CORRECTIONS.get(statement.get("statement_id"))
        if not correction:
            continue
        old, new = correction
        qualification = statement.get("qualifiers", {}).get("qualification", "")
        if qualification == old:
            statement["qualifiers"]["qualification"] = new
            planned_statement_lines[i] = json.dumps(statement, ensure_ascii=False)
        else:
            assert qualification == new, statement.get("statement_id")
        corrected_statement_ids.add(statement["statement_id"])
    assert corrected_statement_ids == set(STATEMENT_QUALIFICATION_CORRECTIONS)
    newline = "\r\n" if "\r\n" in statement_text else "\n"
    planned_statement_text = newline.join(planned_statement_lines).rstrip("\r\n") + newline

    paths = {t["card"]: ROOT / t["card"] for t in TARGETS}
    if all(planned_by_id[t["primary"]].get("ku_id") == t["ku"] for t in TARGETS):
        for t in TARGETS:
            assert paths[t["card"]].read_text(encoding="utf-8-sig") == cards[t["card"]]
            assert t["ku"] in manifest_by_ku and t["card"] in accepted_paths
        print("ALREADY REGISTERED: all Q-R middle person groups, S3 rationales, and continuation notes are present.")
        return 0
    assert all(not planned_by_id[t["primary"]].get("ku_id") and t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not paths[t["card"]].exists() for t in TARGETS), "partial S4 registration requires explicit reconciliation"

    before_stats = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(r[key] for r in before_stats.values()) for key in next(iter(before_stats.values()))}
    planned_manifest, planned_accepted = list(manifest), list(accepted_lines)
    for t in TARGETS:
        row = planned_by_id[t["primary"]]
        row["ku_id"], row["process_ref"] = t["ku"], PROCESS_REF
        row["resolution_note"] += f" S4 registration ({DATE}): group {t['group']} -> {t['ku']}; source-backed person registration only; direct S2 relation candidates remain for S6."
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
        planned_accepted = base.insert_accepted(planned_accepted, t["card"])
    planned_manifest.sort(key=lambda r: r["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(r[key] for r in stats.values()) for key in next(iter(stats.values()))}
    count = len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + count
    assert totals["registered_members"] == before_totals["registered_members"] + count
    assert totals["pending_groups"] == before_totals["pending_groups"] - count
    assert totals["pending_members"] == before_totals["pending_members"] - count
    assert len(planned_manifest) == len(manifest) + count

    additions, card_count = template.extract_card_fields(cards)
    field_count = sum(len(t["name_rows"]) for t in TARGETS)
    assert card_count == count and len(additions) == field_count and all(r.get("evidence_status") == "source_backed" for r in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    current = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id", "")) for r in current}
    ids = {r.get("enrichment_id", "") for r in current}
    max_id = max((int(m.group(1)) for value in ids if (m := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for number, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + number:05d}"
        assert (row["ku_id"], row["field"], row["value"], row.get("source_id", "")) not in keys
        assert row["enrichment_id"] not in ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(r, ensure_ascii=False) for r in additions) + "\n"

    process_text = base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3理由校正与S4人物直接端点登记：Q-R索引中段（{DATE}）\n\n"
    process_text += "- S3理由校正：cand-2138由索引和p.254正文全名支持，并按正文亲属措辞与Aurelio、Carlo既有KU区分。cand-2139由p.135的Don Ferdinando及p.136续文Afan de Ribera明确识别；对应source identity statement的S3待办文字已更新，未增加关系边。cand-2146索引和正文均给出Francesco Maria Ricchini。cand-2188正文只称Abbé Richard，名字未提供；引文经Morazzoni转引，原刊未核，并与Richard Mead分开。cand-2198名字Hyacinthe来自索引，正文p.285仅称Rigaud。五项S3决定均保持new，原自我匹配式说明已撤回并以可追溯的页段证据替换。\n"
    for t in TARGETS:
        process_text += f"- {t['primary']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}与相应正文页段支持source-local人物登记；直接S2关系候选{', '.join(t['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    relation_count = sum(len(t["relations"]) for t in TARGETS)
    process_text += f"\n本批登记{count}个S3 new人物组、{count}条候选映射和{field_count}条source_backed名称字段；{relation_count}条直接S2关系候选留待S6，未新增正式关系或来源。登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。\n"
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += f"\n\n### S3理由校正与S4人物直接端点登记：Q-R索引中段（{DATE}）\n\n登记Lodovico Rezzonico、Don Ferdinando Afan de Ribera、Francesco Maria Ricchini、Abbé Richard与Hyacinthe Rigaud五个source-local人物组；校正五条S3证据说明，保留new决定。{relation_count}条直接S2关系候选留待S6，未新增正式关系。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"

    with tempfile.TemporaryDirectory(prefix="pnp-s4-qr-middle-persons-") as temp_name:
        temp = Path(temp_name)
        alignment_stage, manifest_stage = temp / "alignment.csv", temp / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: alignment_stage.read_bytes(), MANIFEST: manifest_stage.read_bytes(),
            ENRICHMENT: template.with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            STATEMENTS: template.with_bom(planned_statement_text, STATEMENTS.read_bytes()),
            ACCEPTED: template.with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: template.with_bom(process_text.rstrip("\r\n") + "\n", PROCESS.read_bytes()),
            RESULT: template.with_bom(result_text.rstrip("\r\n") + "\n", RESULT.read_bytes()),
        }
        for t in TARGETS:
            writes[ROOT / t["card"]] = template.with_bom(cards[t["card"]])
    if args.dry_run:
        print(f"S3/S4 dry-run passed: groups={count}; s3_rationale_corrections={len(CORRECTIONS)}; source_statement_qualifications_updated={len(STATEMENT_QUALIFICATION_CORRECTIONS)}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}; no files changed")
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
    print(f"applied: groups={count}; s3_rationale_corrections={len(CORRECTIONS)}; source_statement_qualifications_updated={len(STATEMENT_QUALIFICATION_CORRECTIONS)}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
