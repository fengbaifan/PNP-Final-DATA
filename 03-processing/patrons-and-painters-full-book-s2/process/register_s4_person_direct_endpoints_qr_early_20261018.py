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
ANCHOR = "s4-person-direct-endpoints-qr-early-20261018"
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
        "cand-2073", "Q-R.csv#0", "Quaini, Luigi", "189", "new-person:luigi-quaini-cdd63f39d2", "luigi-quaini",
        "路易吉·奎尼", "Luigi Quaini",
        [("索引名", "Quaini, Luigi", "S1（索引Q-R.csv#0）"), ("正文姓名形式", "Luigi Quaini", "S2（第7章p.189）")],
        [template.source("第7章第I节；印刷页189", "Haskell以We are told引出一则关于四位博洛尼亚画家敬慕Louis XIV的报告，并保留对其动机的作者推测。", "We are told that Carlo Cignani, Benedetto Gennari, Luigi Quaini and Donato Creti were all keen admirers of Louis XIV", "02-sources/02-Markdown/07_CHP-7_sec_i.md", "lines 253–255; print p.189")],
        "本卡按索引Q-R.csv#0登记Luigi Quaini。第7章p.189以‘We are told’转述他与其他画家敬慕Louis XIV的说法；该报告及作者对动机的推测均不作独立事实确认。",
        "This card registers Luigi Quaini under index Q-R.csv#0. Chapter 7, p.189, introduces a report that he and other painters admired Louis XIV with ‘We are told’; neither the report nor the author’s speculation about motive is independently verified here.",
        "正文在同一段列出Luigi Quaini，并明确将该说法归为转述。",
        "The body names Luigi Quaini in the same passage and explicitly attributes the account as reported information.",
        ["st-chp7-p189-i23-quaini"],
        {"st-chp7-p189-i23-quaini": ("cand-2073", "cand-1447", "bolognese_artist_was_reported_as_keen_admirer_of_louis_xiv")},
    ),
    target(
        "cand-2089", "Q-R.csv#16", "Radicchio, Don Vincenzo", "366", "new-person:radicchio-vincenzo-36639ad243", "don-vincenzo-radicchio",
        "唐·文琴佐·拉迪基奥", "Don Vincenzo Radicchio",
        [("索引名", "Radicchio, Don Vincenzo", "S1（索引Q-R.csv#16）"), ("正文姓名形式", "Don Vincenzo Radicchio", "S2（第15章p.366）"), ("正文姓氏形式", "Radicchio", "S2（第15章p.365）")],
        [template.source("第15章第II节；印刷页366", "Haskell称Don Vincenzo Radicchio是Memmo的一位秘书，并称他于1786年为Subleyras的版画撰写说明。", "Don Vincenzo Radicchio, wrote an account to accompany the engraving", "02-sources/02-Markdown/15_CHP-15_sec_ii.md", "line 22; print p.366"), template.source("第15章第II节；印刷页365", "同章前页以姓氏Radicchio继续谈及Memmo的相关书信与雕版叙述。", "Radicchio", "02-sources/02-Markdown/15_CHP-15_sec_ii.md", "body mention; print p.365")],
        "本卡按索引Q-R.csv#16登记Don Vincenzo Radicchio。第15章p.366给出全名并叙述其秘书身份及写作说明；p.365的姓氏形式按同章语境收录。相关 account 的题名、版本与原件未据此补定。",
        "This card registers Don Vincenzo Radicchio under index Q-R.csv#16. Chapter 15, p.366, gives his full name and describes him as a secretary who wrote an accompanying account; the surname form on p.365 is recorded in the same chapter context. No title, edition, or original document is inferred for the account.",
        "正文全名见p.366，前页以姓氏形式提及；外部身份未核。",
        "The full name appears on p.366 and the surname form on the preceding page; no external identity is verified.",
        ["st-chp15-p366-radicchio-account-authored-by", "st-chp15-p366-radicchio-secretary-to-memmo"],
        {"st-chp15-p366-radicchio-account-authored-by": ("cand-11526", "cand-2089", "account_authored_by_radicchio"), "st-chp15-p366-radicchio-secretary-to-memmo": ("cand-2089", "cand-1642", "radicchio_identified_as_memmos_secretary")},
    ),
    target(
        "cand-2090", "Q-R.csv#17", "Raggi, Ferdinando", "140n", "new-person:ferdinando-raggi-07e6d94c1b", "ferdinando-raggi",
        "费迪南多·拉吉", "Ferdinando Raggi",
        [("索引名", "Raggi, Ferdinando", "S1（索引Q-R.csv#17）"), ("正文称谓", "Marchese Raggi", "S2（第5章p.140注）"), ("正文姓名形式", "Ferdinando Raggi", "S2（第5章p.155注）")],
        [template.source("第5章第III节注2；印刷页140", "Haskell称Marchese Raggi于1701年借出Cerquozzi的五幅画；索引将p.140注定位于Raggi, Ferdinando。", "Marchese Raggi lent", "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "line 143; print p.140 n.2"), template.source("第5章第III节注6；印刷页155", "同章另一注称一份报告出自Ferdinando Raggi，并称其为在罗马的热那亚外交人员。", "Ferdinando Raggi, Genoese diplomatic agent in Rome", "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "line 155; print p.155 n.6")],
        "本卡按索引Q-R.csv#17登记Ferdinando Raggi。p.140注称Marchese Raggi，p.155注另以全名称一位在罗马的热那亚外交人员；按书内索引和同章语境保留为source-local组，不添加外部身份匹配，并与索引Q-R.csv#18的Monsignor Raggi分开。",
        "This card registers Ferdinando Raggi under index Q-R.csv#17. Note 2 on p.140 calls him Marchese Raggi; note 6 on p.155 separately names a Genoese diplomatic agent in Rome as Ferdinando Raggi. The source-local group follows the book’s index and chapter context, adds no external identity match, and remains separate from Monsignor Raggi in index Q-R.csv#18.",
        "p.140注的称谓与p.155注的全名按本书索引联系；没有外部证据扩展其身份。",
        "The p.140 note’s title and the p.155 note’s full name are linked through the book’s index; no external evidence extends the identity.",
        ["st-chp5-notes-l143-raggi-patronage-loan", "st-chp5-notes-l126-165-l143-raggi-loaned-five-pictures"],
        {"st-chp5-notes-l143-raggi-patronage-loan": ("cand-2090", "cand-0625", "patron_of"), "st-chp5-notes-l126-165-l143-raggi-loaned-five-pictures": ("cand-11941", "cand-2090", "lent_by")},
    ),
    target(
        "cand-2096", "Q-R.csv#23", "Ranuzzi, Vincenzo", "390, 391", "new-person:ranuzzi-vincenzo-c540db0da6", "vincenzo-ranuzzi",
        "温琴佐·拉努齐", "Vincenzo Ranuzzi",
        [("索引名", "Ranuzzi, Vincenzo", "S1（索引Q-R.csv#23）"), ("正文姓名形式", "Vincenzo Ranuzzi", "S2（第19章附录5p.390）"), ("书信署名形式", "Vincenzio Ranuzzi", "S2（第19章附录5p.391）")],
        [template.source("第19章附录5；印刷页390", "Haskell以Letter from Vincenzo Ranuzzi标注一封1708年1月31日书信。", "Letter from Vincenzo Ranuzzi of 31 January 1708", "02-sources/02-Markdown/19_CHP-19Appendix.md", "line 105; print p.390"), template.source("第19章附录5；印刷页391", "同一书信续页以Vincenzio Ranuzzi署名；手稿未独立查阅。", "Vincenzio Ranuzzi", "02-sources/02-Markdown/19_CHP-19Appendix.md", "line 113; print p.391")],
        "本卡按索引Q-R.csv#23登记Vincenzo Ranuzzi。书信标注写作Vincenzo Ranuzzi，续页署名写作Vincenzio Ranuzzi，日期均指向1708年1月31日的同一书信；原手稿未独立查阅。",
        "This card registers Vincenzo Ranuzzi under index Q-R.csv#23. The letter heading gives Vincenzo Ranuzzi, while its continuation signs Vincenzio Ranuzzi; both refer to the same letter dated 31 January 1708. The manuscript was not independently consulted.",
        "书信题头和署名保留Vincenzo/Vincenzio两种书内形式；p.391边注的缩写不在此展开。",
        "The letter heading and signature retain both book forms, Vincenzo and Vincenzio; the p.391 marginal abbreviation is not expanded here.",
        ["st-chp19-p391-ranuzzi-margin-crespi", "st-chp19-p391-ranuzzi-caldari-picture-incident"],
        {"st-chp19-p391-ranuzzi-margin-crespi": ("cand-2096", "cand-0873", "ranuzzi_letter_marginal_note_identifies_the_introduced_painter_as_crespi"), "st-chp19-p391-ranuzzi-caldari-picture-incident": ("cand-2096", "cand-10804", "ranuzzi_wrote_caldari_about_an_unspecified_incident_concerning_his_picture")},
    ),
    target(
        "cand-2112", "Q-R.csv#39", "Redi, Francesco", "229, 230", "new-person:francesco-redi-01250bf868", "francesco-redi",
        "弗朗切斯科·雷迪", "Francesco Redi",
        [("索引名", "Redi, Francesco", "S1（索引Q-R.csv#39）"), ("正文姓氏形式", "Redi", "S2（第8章p.229）"), ("正文姓名形式", "Francesco Redi", "S2（第8章p.230）")],
        [template.source("第8章第II节；印刷页229", "Haskell称Grand Prince Ferdinand受Viviani、Lorenzini与Redi等人的教育；此处只用姓氏。", "Viviani, Lorenzini, Redi", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "line 218; print p.229"), template.source("第8章第II节；印刷页230", "同一章下一页以Francesco Redi全名提及其诗作版本。", "sumptuous editions of Francesco Redi and other poets", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "line 230; print p.230")],
        "本卡按索引Q-R.csv#39登记Francesco Redi。第8章p.229以姓氏列为Ferdinand的教育者，p.230随后给出Francesco Redi全名；依索引页段和同章上下文合为书内人物组。",
        "This card registers Francesco Redi under index Q-R.csv#39. Chapter 8, p.229, names Redi by surname among Ferdinand’s educators, and p.230 gives the full name Francesco Redi; the indexed page range and chapter context support one source-local person group.",
        "p.229的姓氏形式与p.230的全名相互对应；教育与出版叙述均保持为Haskell的原书陈述。",
        "The surname form on p.229 and full name on p.230 are linked; the education and publication accounts remain attributed to Haskell.",
        ["st-chp8-p229-ferdinand-educated-by-redi"],
        {"st-chp8-p229-ferdinand-educated-by-redi": ("cand-1609", "cand-2112", "ferdinand_educated_by_francesco_redi")},
    ),
]

CORRECTIONS = {
    "cand-2073": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2073 by identical normalized full-name/explicit-alias anchor (luigi quaini), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#0 and the p.189 body both give Luigi Quaini in the reported list of Bolognese artists. The source attributes this report and the author's motive speculation; neither is independently verified. No external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2089": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2089 by identical normalized full-name/explicit-alias anchor (radicchio vincenzo), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#16 locates p.366, where the body gives Don Vincenzo Radicchio; p.365 uses the surname in the same chapter context. No external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2090": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2090 by identical normalized full-name/explicit-alias anchor (ferdinando raggi), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#17 directs p.140 n.2, where the text says Marchese Raggi; a separate p.155 n.6 names Ferdinando Raggi as a Genoese diplomatic agent in Rome. Retain this book-internal index-linked group and keep it separate from the indexed Monsignor Raggi at Q-R.csv#18; no external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2096": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2096 by identical normalized full-name/explicit-alias anchor (ranuzzi vincenzo), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#23 and the letter heading give Vincenzo Ranuzzi; the same letter's continuation signs Vincenzio Ranuzzi and repeats the 31 January 1708 date. Preserve both forms; the manuscript was not independently consulted. No external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2112": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2112 by identical normalized full-name/explicit-alias anchor (francesco redi), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#39 spans pp.229–230; p.229 uses Redi among Ferdinand's educators and p.230 gives the full name Francesco Redi. The indexed chapter context supports one source-local group; no external identity source was accessed; KU assignment remains for S4.",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct Q-R early person S3 rationales and register five direct endpoints.")
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
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
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
        file_name, index_id = t["entry"].split("#", 1)
        index_lines = (ROOT / "02-sources/03-Index/03-2-Index-CSV" / file_name).read_text(encoding="utf-8-sig").splitlines()
        index_row = next(csv.reader([index_lines[int(index_id) + 1]]))
        assert index_row[0] == t["index_name"] and t["pages"] in index_row[-1]
        direct = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == t["primary"] or r.get("object_candidate_id") == t["primary"])}
        assert direct == set(t["endpoints"]), (t["primary"], sorted(direct))
        for statement_id, expected in t["endpoints"].items():
            row = statement_by_id[statement_id]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == expected
        for item in t["sources"]:
            source_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", source_text), (t["primary"], item["span"])

    planned_alignments = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    for candidate_id, (old, new) in CORRECTIONS.items():
        row = planned_by_id[candidate_id]
        if old in row.get("resolution_note", ""):
            row["resolution_note"] = row["resolution_note"].replace(old, new, 1)
        else:
            assert new in row.get("resolution_note", ""), f"unexpected S3 rationale for {candidate_id}"

    paths = {t["card"]: ROOT / t["card"] for t in TARGETS}
    already_registered = all(planned_by_id[t["primary"]].get("ku_id") == t["ku"] for t in TARGETS)
    if already_registered:
        for t in TARGETS:
            assert paths[t["card"]].read_text(encoding="utf-8-sig") == cards[t["card"]]
            assert t["ku"] in manifest_by_ku and t["card"] in accepted_paths
        print("ALREADY REGISTERED: all Q-R early person groups and corrected S3 rationales are present.")
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3理由校正与S4人物直接端点登记：Q-R索引前段（{DATE}）\n\n"
    process_text += "- S3理由校正：cand-2073的正文全名和索引页码支持Quaini书内组，但原文将敬慕Louis XIV的说法明确作为转述，保留归因。cand-2089以p.366全名和p.365同章姓氏对齐Radicchio。cand-2090按Q-R.csv#17索引链接p.140注的Marchese Raggi，并与p.155注的Ferdinando Raggi书内形式相互参照；不与Q-R.csv#18的Monsignor Raggi合并，也不作外部身份匹配。cand-2096以同一封1708年1月31日书信的题头Vincenzo与续页署名Vincenzio归组，手稿未独立查阅。cand-2112以p.229姓氏Redi和p.230全名Francesco Redi，结合索引页段归组。五项S3决定均保持new，旧的自我匹配式说明已撤回并由上述证据依据替换。\n"
    for t in TARGETS:
        process_text += f"- {t['primary']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}与相应正文页段支持source-local人物登记；直接S2关系候选{', '.join(t['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    relation_count = sum(len(t["relations"]) for t in TARGETS)
    process_text += f"\n本批登记{count}个S3 new人物组、{count}条候选映射和{field_count}条source_backed名称字段；{relation_count}条直接S2关系候选留待S6，未新增正式关系、S2断言或来源。登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。\n"
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += f"\n\n### S3理由校正与S4人物直接端点登记：Q-R索引前段（{DATE}）\n\n登记Luigi Quaini、Don Vincenzo Radicchio、Ferdinando Raggi、Vincenzo Ranuzzi与Francesco Redi五个source-local人物组；修正五条S3证据表述并保留new决定。{relation_count}条直接S2关系候选留待S6，未新增正式关系。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"

    with tempfile.TemporaryDirectory(prefix="pnp-s4-qr-early-persons-") as temp_name:
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
        for t in TARGETS:
            writes[ROOT / t["card"]] = template.with_bom(cards[t["card"]])
    if args.dry_run:
        print(f"S3/S4 dry-run passed: groups={count}; s3_rationale_corrections={len(CORRECTIONS)}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}; no files changed")
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
    print(f"applied: groups={count}; s3_rationale_corrections={len(CORRECTIONS)}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
