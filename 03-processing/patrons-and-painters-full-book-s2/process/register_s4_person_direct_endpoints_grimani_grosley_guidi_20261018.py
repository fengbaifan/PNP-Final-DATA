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
ANCHOR = "s4-person-direct-endpoints-grimani-grosley-guidi-20261018"
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
        "cand-1234", "G.csv#144", "Grimani, Doge", "272", "new-person:doge-grimani-ee5c26c638", "doge-grimani",
        "格里马尼总督", "Doge Grimani",
        [("索引称谓", "Grimani, Doge", "S1（索引G.csv#144）"), ("正文称谓", "Doge Grimani", "S2（第9章第II节p.272）")],
        [template.source("第9章第II节；印刷页272", "Haskell称1745年决定重建教堂时由Doge Grimani奠基；正文未给出其名字。", "The first stone was therefore laid by Doge Grimani when in 1745 it was decided to rebuild the church", "02-sources/02-Markdown/09_CHP-9_sec_ii.md", "line 57; print p.272")],
        "本卡保留索引与正文的称谓Doge Grimani，不补出个人名字。第9章p.272将其置于1745年决定重建威尼斯Pietà教堂的语境，并称其主持奠基。",
        "This card retains the index and body form Doge Grimani without supplying a personal given name. Chapter 9, p.272, places him in the 1745 decision to rebuild Venice's Pietà church and says he laid its first stone.",
        "既有S3裁决将其保留为按称谓识别的书内人物组，与一般性的威尼斯总督机构候选及Cardinal Grimani候选分开；不作外部姓名匹配。",
        "The existing S3 decision retains a title-based source-local person group, separate from the generic Doge of Venice institution candidate and the Cardinal Grimani candidate; no external personal-name match is made.",
        ["st-chp9-p272-doge-grimani-rebuild"],
        {"st-chp9-p272-doge-grimani-rebuild": ("cand-1234", "cand-8551", "doge_grimani_laid_first_stone_when_rebuild_decided_1745")},
    ),
    target(
        "cand-1235", "G.csv#145", "Grosley, Pierre Jean", "301n, 332", "new-person:grosley-jean-pierre-ebde05d809", "pierre-jean-grosley",
        "皮埃尔·让·格罗斯莱", "Pierre Jean Grosley",
        [("索引名", "Grosley, Pierre Jean", "S1（索引G.csv#145）"), ("正文称名", "Grosley", "S2（第10章注1 p.301；第13章p.332）")],
        [template.source("第10章导论注1；印刷页301", "Haskell称Grosley于1758年在威尼斯，继而转引其对Pasquali印刷所资金来源的评论；被引U卷p.99未独立核查。", "Grosley, who was in Venice in 1758, writes", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 589; print p.301 n.1"), template.source("第13章导论；印刷页332", "Haskell称旅人Grosley观察到威尼斯获许可出版法译本的情况，并引其与巴黎相比的评论。", "the traveller Grosley noted that", "02-sources/02-Markdown/13_CHP-13_intro.md", "line 7; print p.332")],
        "本卡按索引G.csv#145登记Pierre Jean Grosley。第10章p.301注1称Grosley于1758年在威尼斯并转引其评论；第13章p.332又称旅人Grosley并引其出版许可比较。两处书内出现由同一索引项定位；不将可能的书目匹配写成已核实来源。",
        "This card registers Pierre Jean Grosley under index G.csv#145. Chapter 10, p.301 n.1, places Grosley in Venice in 1758 and quotes his comment; chapter 13, p.332, again names the traveller Grosley and quotes his comparison of publication permissions. The book indexes both passages under one entry; a possible bibliography match is not treated as verified.",
        "正文只称Grosley，Pierre Jean由索引提供；被引U卷p.99与书目候选的对应仍未核实。第10章转引的资金评论是直接S2关系候选。",
        "The body uses Grosley, with Pierre Jean supplied by the index; the cited U volume, p.99, has not been matched to the bibliography candidate. The funding comment quoted in chapter 10 is a direct S2 relation candidate.",
        ["st-chp10-p301-note1-grosley-quote"],
        {"st-chp10-p301-note1-grosley-quote": ("cand-1235", "cand-9172", "quoted_report_of_smith_funding_pasquali_press")},
    ),
    target(
        "cand-1277", "G.csv#187", "Guidi, Domenico", "189, 198", "new-person:domenico-guidi-8bb3bdb48b", "domenico-guidi",
        "多梅尼科·圭迪", "Domenico Guidi",
        [("索引名", "Guidi, Domenico", "S1（索引G.csv#187）"), ("正文姓名形式", "Domenico Guidi", "S2（第7章p.189、p.198）")],
        [template.source("第7章第I节；印刷页189", "Haskell称Domenico Guidi是受路易十四选中、为凡尔赛花园制作雕塑群的罗马雕塑家。", "Domenico Guidi, was chosen by Louis ‘from all those not only in Italy but in the whole of Europe’ to make one of the sculptured groups for the gardens at Versailles", "02-sources/02-Markdown/07_CHP-7_sec_i.md", "line 246; print p.189"), template.source("第7章第IV节；印刷页198", "Haskell称Closterman寄给Shaftesbury由Domenico Guidi创作的审慎与正义素描；同名及雕塑语境与p.189索引条目一致。", "Closterman sent him some drawings of Prudence and Justice by Domenico Guidi", "02-sources/02-Markdown/07_CHP-7_sec_iv.md", "line 83; print p.198")],
        "本卡按索引G.csv#187登记Domenico Guidi。第7章p.189记载路易十四选择他制作凡尔赛花园雕塑群；p.198又称Closterman寄送其审慎与正义素描。索引将两处页码列于同一人物项。",
        "This card registers Domenico Guidi under index G.csv#187. Chapter 7, p.189, reports Louis XIV's selection of him for a Versailles garden group; p.198 also names him as the maker of Closterman's drawings of Prudence and Justice. The index places both pages under the same person entry.",
        "两章段落均给出全名并处于雕塑及设计语境；p.189的遴选断言是直接S2关系候选。p.198关于Closterman寄送素描的关系候选仍以Closterman和素描对象为端点，本卡只作同名语境证据。",
        "Both chapter passages give the full name in sculptural and design contexts; the p.189 selection is a direct S2 relation candidate. The p.198 drawing statement remains mapped to Closterman and the drawing object; this card uses it only as same-person context evidence.",
        ["st-chp7-p189-i06"],
        {"st-chp7-p189-i06": ("cand-1447", "cand-1277", "selected_guidi_to_make_versailles_sculptured_group")},
    ),
]

CORRECTIONS = {
    "cand-1235": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-1235 by identical normalized full-name/explicit-alias anchor (grosley jean pierre), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no exact Pierre Jean Grosley KU matched. Index G.csv#145 supplies the full name and links pp.301n and 332; the body names Grosley in both the 1758 Venice note and the traveller's publication-permission observation. The possible match between the cited U p.99 and a bibliography record remains unresolved. No external identity source was accessed; source-local KU assignment remains for S4.",
    ),
    "cand-1277": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-1277 by identical normalized full-name/explicit-alias anchor (domenico guidi), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no exact Domenico Guidi KU matched. Index G.csv#187 and chapter 7 pp.189, 198 give the same full name in sculptural contexts; keep the Louis XIV selection endpoint at p.189 distinct from the p.198 Closterman-to-drawings statement, which does not currently use Guidi as a relation endpoint. No external identity source was accessed; source-local KU assignment remains for S4.",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three G-section person endpoints while preserving the title-only Grimani decision and cross-chapter identities.")
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
        print("ALREADY REGISTERED: Doge Grimani, Pierre Jean Grosley, and Domenico Guidi are registered with current evidence notes.")
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
    for t in TARGETS:
        row = planned_by_id[t["primary"]]
        row["ku_id"], row["process_ref"] = t["ku"], PROCESS_REF
        row["resolution_note"] += f" S4 registration ({DATE}): group {t['group']} -> {t['ku']}; source-backed person registration only; direct S2 relation candidates remain for S6."

    before_stats = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(r[key] for r in before_stats.values()) for key in next(iter(before_stats.values()))}
    planned_manifest, planned_accepted = list(manifest), list(accepted_lines)
    for t in TARGETS:
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3身份组交接与S4登记：Grimani、Grosley、Guidi（{DATE}）\n\n"
    process_text += "- cand-1234：沿用本日既有S3标题身份审查，登记为Doge Grimani书内人物KU，不补姓名；1745年奠基语境将其与一般性的威尼斯总督机构候选分开，Cardinal Grimani仍按现有S3记录保持未决。\n"
    process_text += "- cand-1235：修正旧的自我匹配式new理由。索引G.csv#145定位p.301n与p.332；前者转引1758年在威尼斯的Grosley，后者称旅人Grosley并引其出版许可观察，支持同一书内人物组。引文U p.99与书目条目的对应仍未证实。\n"
    process_text += "- cand-1277：修正旧的自我匹配式new理由。索引G.csv#187将p.189与p.198并列；两处正文均称Domenico Guidi，分别置于凡尔赛雕塑遴选及Closterman寄送其素描的语境。p.198关系候选仍映射Closterman与素描对象，本批不把Guidi增作该statement的端点。\n"
    for t in TARGETS:
        process_text += f"- {t['primary']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}与正文页段支持书内人物登记；直接S2关系候选{', '.join(t['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    relation_count = sum(len(t["relations"]) for t in TARGETS)
    process_text += f"\n本批保留1个标题身份S3决定并校正{len(CORRECTIONS)}条new身份理由，登记{count}个new人物组、{count}条候选映射和{field_count}条source_backed名称字段；{relation_count}条直接S2关系候选留待S6，未新增正式关系或来源。登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。\n"
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += f"\n\n### S3身份组交接与S4登记：Grimani、Grosley、Guidi（{DATE}）\n\n登记Doge Grimani（保留标题形式）、Pierre Jean Grosley（合并索引所指p.301n与p.332书内出现）、Domenico Guidi（合并p.189与p.198书内出现）三个source-local人物组。三条直接S2关系候选留待S6；未新增正式关系。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"

    with tempfile.TemporaryDirectory(prefix="pnp-s4-grimani-grosley-guidi-") as temp_name:
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
        print(f"S3/S4 dry-run passed: title_only=1; rationale_corrections={len(CORRECTIONS)}; new_groups={count}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}; no files changed")
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
    print(f"applied: title_only=1; rationale_corrections={len(CORRECTIONS)}; new_groups={count}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
