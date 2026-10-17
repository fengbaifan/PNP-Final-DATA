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
ANCHOR = "s4-person-direct-endpoints-rota-rovere-rowlandson-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def target(primary, entry, index_name, pages, group, slug, zh, en, name_rows, sources, desc_zh, desc_en, context_zh, context_en, relations, endpoints):
    return {
        "primary": primary, "entry": entry, "index_name": index_name, "canonical_name": index_name,
        "pages": pages, "group": group, "ku": f"units/persons/{slug}",
        "card": f"04-knowledge/units/persons/{slug}.md", "name_zh": zh, "name_en": en,
        "name_rows": name_rows, "sources": sources, "zh": desc_zh, "en": desc_en,
        "context_zh": context_zh, "context_en": context_en, "relations": relations,
        "endpoints": endpoints, "external": None,
    }


TARGETS = [
    target(
        "cand-2287", "Q-R.csv#215", "Rota, Giovanni Battista", "312", "new-person:battista-giovanni-rota-738eac852a", "giovanni-battista-rota",
        "乔瓦尼·巴蒂斯塔·罗塔", "Giovanni Battista Rota",
        [("索引名", "Rota, Giovanni Battista", "S1（索引Q-R.csv#215）"), ("正文姓名形式", "Giovanni Battista Rota", "S2（第10章第II节p.312）")],
        [template.source("第10章第II节；印刷页312", "Haskell称Schulenburg于1724年向律师Giovanni Battista Rota大额购入古画和雕塑，并称Rota亦从事艺术品交易。", "from a lawyer, Giovanni Battista Rota, who also acted as an art dealer", "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "line 21; print p.312")],
        "本卡登记索引Q-R.csv#215所列Giovanni Battista Rota。第10章p.312称其为律师和艺术品交易者，并报告Schulenburg于1724年向其购入一批绘画与雕塑；该购买叙述保留为书内关系候选。",
        "This card registers Giovanni Battista Rota under index Q-R.csv#215. Chapter 10, p.312, calls him a lawyer and art dealer and reports Schulenburg's 1724 purchase of paintings and sculpture from him; the purchase remains a book-based relation candidate.",
        "正文提供全名与职业称谓；关于1724年交易的来源脚注所指档案与Edward Wright页码尚未独立核查。",
        "The body supplies his full name and occupations; the archival records and Edward Wright page cited in the note for the 1724 transaction have not been independently checked.",
        ["st-chp10-p312-1724-purchase-from-rota"],
        {"st-chp10-p312-1724-purchase-from-rota": ("cand-2401", "cand-2287", "purchased_paintings_and_sculpture_from_rota")},
    ),
    target(
        "cand-2290", "Q-R.csv#218", "Rovere, Vittoria della", "54", "new-person:della-rovere-vittoria-128b06ba87", "vittoria-della-rovere",
        "维托里娅·德拉·罗韦雷", "Vittoria della Rovere",
        [("索引名", "Rovere, Vittoria della", "S1（索引Q-R.csv#218）"), ("正文姓名形式", "Vittoria della Rovere", "S2（第2章第IV节p.54）")],
        [template.source("第2章第IV节；印刷页54", "Haskell称老公爵将其私人物品留给女儿Vittoria della Rovere，并称她为托斯卡纳大公之妻；正文未在此句给出配偶姓名。", "The old duke had left his private possessions to his daughter Vittoria della Rovere, wife of the Grand Duke of Tuscany.", "02-sources/02-Markdown/02_CHP-2_sec_iv.md", "line 123; print p.54")],
        "本卡登记索引Q-R.csv#218所列Vittoria della Rovere。第2章p.54称老公爵将私人物品留给她，并称其为托斯卡纳大公之妻；此处只记录私人物品，不推及公国公共收藏或全部家产。",
        "This card registers Vittoria della Rovere under index Q-R.csv#218. Chapter 2, p.54, says the old duke left his private possessions to her and calls her the wife of the Grand Duke of Tuscany; this concerns private possessions only, not the state's public collection or all family property.",
        "姓名由正文与索引支持；父女及私人物品继承断言是直接S2关系候选，配偶仅以称号出现。",
        "The body and index support the name; the father-daughter and private-property inheritance claim is a direct S2 relation candidate, while the spouse appears only by title.",
        ["st-chp2-seciv-l114-125-private-possession-inheritance"],
        {"st-chp2-seciv-l114-125-private-possession-inheritance": ("cand-2671", "cand-2290", "duke_leaves_private_possessions_to_daughter")},
    ),
    target(
        "cand-2291", "Q-R.csv#219", "Rowlandson, Thomas", "292", "new-person:rowlandson-thomas-587b2a4589", "thomas-rowlandson",
        "托马斯·罗兰森", "Thomas Rowlandson",
        [("索引名", "Rowlandson, Thomas", "S1（索引Q-R.csv#219）"), ("正文姓名形式", "Thomas Rowlandson", "S2（第10章导论p.292）")],
        [template.source("第10章导论；印刷页292", "Haskell称讽刺画家Thomas Rowlandson后来将Canaletto以简略笔触描绘人物的方式转用于喜剧效果。", "his shorthand of little blobs to represent the human figure was later adapted to brilliant comic purpose by the satirist Thomas Rowlandson", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 276; print p.292")],
        "本卡登记索引Q-R.csv#219所列Thomas Rowlandson。第10章p.292称其为讽刺画家，并报告他后来将Canaletto描绘人物的简略方式转用于喜剧目的；不指认具体作品。",
        "This card registers Thomas Rowlandson under index Q-R.csv#219. Chapter 10, p.292, calls him a satirist and says he later adapted Canaletto's shorthand figures for comic purpose; no particular work is identified.",
        "正文提供全名与讽刺画家称谓；对Canaletto人物画法的转用保留为直接S2关系候选。",
        "The body supplies his full name and identifies him as a satirist; the adaptation of Canaletto's figure shorthand remains a direct S2 relation candidate.",
        ["st-chp10-p292-rowlandson-adaptation"],
        {"st-chp10-p292-rowlandson-adaptation": ("cand-0528", "cand-2291", "rowlandson_later_adapted_canalettos_shorthand_figures_for_comic_purpose")},
    ),
]

CORRECTIONS = {
    "cand-2287": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2287 by identical normalized full-name/explicit-alias anchor (battista giovanni rota), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no exact existing Giovanni Battista Rota KU matched. Index Q-R.csv#215 and p.312 body give his full name; Haskell calls him a lawyer and art dealer in the Schulenburg purchase passage. No external identity source was accessed; source-local KU assignment remains for S4.",
    ),
    "cand-2290": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2290 by identical normalized full-name/explicit-alias anchor (della rovere vittoria), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no exact Vittoria della Rovere KU matched. Index Q-R.csv#218 and p.54 body give her full name; the source identifies her as the old duke's daughter and limits the bequest to his private possessions. She remains distinct from the existing Francesco Maria della Rovere KU. No external identity source was accessed; source-local KU assignment remains for S4.",
    ),
    "cand-2291": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2291 by identical normalized full-name/explicit-alias anchor (rowlandson thomas), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no exact Thomas Rowlandson KU matched. Index Q-R.csv#219 and p.292 body give his full name; the passage identifies him as a satirist and reports his later comic adaptation of Canaletto's shorthand figures. No external identity source was accessed; source-local KU assignment remains for S4.",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three Q-R person endpoints with source-specific S3 rationales.")
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
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {r["statement_id"]: r for r in statements}
    cards = {t["card"]: template.make_card(t) for t in TARGETS}
    card_paths = {t["card"]: ROOT / t["card"] for t in TARGETS}
    already = all(alignment_by_id[t["primary"]].get("decision") == "new" and alignment_by_id[t["primary"]].get("ku_id") == t["ku"] for t in TARGETS)
    if already:
        for t in TARGETS:
            assert card_paths[t["card"]].read_text(encoding="utf-8-sig") == cards[t["card"]]
            assert t["ku"] in manifest_by_ku and t["card"] in accepted_paths
        print("ALREADY REGISTERED: all three Q-R person groups and source-specific rationales are present.")
        return 0

    index_root = ROOT / "02-sources/03-Index/03-2-Index-CSV"
    for t in TARGETS:
        candidate, row = candidate_by_id[t["primary"]], alignment_by_id[t["primary"]]
        assert candidate.get("suggested_type") == "person"
        assert (candidate.get("canonical_name"), candidate.get("index_entry_id"), candidate.get("index_page_range")) == (t["canonical_name"], t["entry"], t["pages"])
        assert row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == t["group"]
        assert not row.get("ku_id")
        members = [r["candidate_id"] for r in alignments if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == t["group"]]
        assert members == [t["primary"]]
        filename, index_id = t["entry"].split("#", 1)
        lines = (index_root / filename).read_text(encoding="utf-8-sig").splitlines()
        indexed = next(csv.reader([lines[int(index_id) + 1]]))
        assert indexed[0] == t["index_name"] and t["pages"] in indexed[-1]
        direct = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and t["primary"] in (r.get("subject_candidate_id"), r.get("object_candidate_id"))}
        assert direct == set(t["endpoints"]), (t["primary"], sorted(direct))
        for statement_id, expected in t["endpoints"].items():
            row = statement_by_id[statement_id]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == expected
        for item in t["sources"]:
            source_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", source_text), (t["primary"], item["span"])

    assert all(t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not card_paths[t["card"]].exists() for t in TARGETS), "partial S4 registration requires reconciliation"
    planned_alignments = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    for cid, (old, new) in CORRECTIONS.items():
        row = planned_by_id[cid]
        if old in row.get("resolution_note", ""):
            row["resolution_note"] = row["resolution_note"].replace(old, new, 1)
        else:
            assert new in row.get("resolution_note", ""), f"unexpected S3 rationale for {cid}"

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
    planned_enrichment = enrichment_text.rstrip("\r\n") + "\n" + "\n".join(json.dumps(r, ensure_ascii=False) for r in additions) + "\n"

    process_text = base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3人物身份组理由校正与S4登记：Rota、Rovere、Rowlandson（{DATE}）\n\n"
    process_text += "- cand-2287：索引与第10章p.312正文均给出Giovanni Battista Rota全名；正文称律师及艺术品交易者。未找到精确同名既有KU，登记独立source-local人物组；注4所指档案与Edward Wright页码未独立查阅。\n"
    process_text += "- cand-2290：索引Q-R.csv#218与第2章p.54正文支持Vittoria della Rovere全名；现有Francesco Maria della Rovere KU只提供“女儿”语境，没有Vittoria人物KU，故新增source-local组。私人物品继承限于原文表述。\n"
    process_text += "- cand-2291：索引与第10章p.292正文均给出Thomas Rowlandson全名；正文称其讽刺画家并记其转用Canaletto人物简笔。未找到精确同名既有KU，登记独立source-local人物组。三组不依姓氏相似性合并，不作外部身份声明。\n"
    for t in TARGETS:
        process_text += f"- {t['primary']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}与正文页段支持书内人物登记；直接S2关系候选{', '.join(t['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    relation_count = sum(len(t["relations"]) for t in TARGETS)
    process_text += f"\n本批登记{count}个S3 new人物组、{count}条候选映射和{field_count}条source_backed名称字段；{relation_count}条直接S2关系候选留待S6，未新增正式关系或来源。登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。\n"
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += f"\n\n### S3人物身份组理由校正与S4登记：Rota、Rovere、Rowlandson（{DATE}）\n\n登记Giovanni Battista Rota、Vittoria della Rovere、Thomas Rowlandson三个source-local人物组，分别保留采购、私人物品继承、画法转用三条S2关系候选待S6。KU={len(planned_manifest)}；未新增正式关系；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"

    with tempfile.TemporaryDirectory(prefix="pnp-s4-rota-rovere-rowlandson-") as temp_name:
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
        print(f"S3/S4 dry-run passed: groups={count}; rationale_corrections={len(CORRECTIONS)}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}; no files changed")
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
    print(f"applied: groups={count}; rationale_corrections={len(CORRECTIONS)}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
