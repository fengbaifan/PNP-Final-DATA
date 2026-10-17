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
ANCHOR = "s4-person-direct-endpoints-del-rosso-family-20261018"
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
        "cand-2279", "Q-R.csv#207", "Rosso, Andrea del (grandfather of Andrea, Lorenzo, and Ottavio del Rosso)", "211, 212",
        "new-person:andrea-del-rosso-grandfather-2279", "andrea-del-rosso-grandfather",
        "安德烈亚·德尔·罗索（安德烈亚、洛伦佐与奥塔维奥三兄弟之祖父）",
        "Andrea del Rosso (grandfather of Andrea, Lorenzo, and Ottavio del Rosso)",
        [("索引名", "Rosso, Andrea del (grandfather of Andrea, Lorenzo, and Ottavio del Rosso)", "S1（索引Q-R.csv#207）"), ("正文称谓", "their grandfather", "S2（第8章第I节p.211）"), ("正文姓名形式", "Andrea", "S2（第8章第I节p.212）")],
        [template.source("第8章第I节；印刷页211", "Haskell在比较del Rosso兄弟与其前辈时称‘their grandfather’；S3记录已将其与后来出生的Andrea del Rosso分开。", "their grandfather", "02-sources/02-Markdown/08_CHP-8_sec_i.md", "line 89; print p.211"), template.source("第8章第I节；印刷页212", "延续段落称Andrea曾在Theatine教堂为其守护圣人建造家族礼拜堂。", "Andrea had had built in the Theatine church of S. Gaetano a sumptuous family chapel", "02-sources/02-Markdown/08_CHP-8_sec_i.md", "line 99; print p.212")],
        "本卡登记索引Q-R.csv#207所列Andrea del Rosso，即索引说明中的三兄弟祖父。第8章pp.211–212先称其为兄弟们的祖父，再以Andrea续述其为守护圣人修建家族礼拜堂；S3已将这一代与既有Andrea del Rosso人物KU区分。",
        "This card registers Andrea del Rosso under index Q-R.csv#207, identified in the index as the grandfather of the three brothers. Chapter 8, pp.211–212, first calls him their grandfather and continues with Andrea’s family chapel for his name-saint; S3 has kept this generation distinct from the existing Andrea del Rosso KU.",
        "全名采用索引形式，正文称谓和续文共同支撑其代际身份；不将其与生于1640年的孙辈合并。",
        "The index supplies the full display form; the body’s kinship label and continuation support the generation distinction from the grandson born in 1640.",
        ["st-chp8-p211-forebears-grandfather-open", "st-chp8-p212-grandfather-andrea-built-chapel"],
        {"st-chp8-p211-forebears-grandfather-open": ("cand-7489", "cand-2279", "comparison_with_forebears_begins_grandfather_account_continues"), "st-chp8-p212-grandfather-andrea-built-chapel": ("cand-2279", "cand-7522", "grandfather_andrea_had_family_chapel_built_for_his_name_saint")},
    ),
    target(
        "cand-2280", "Q-R.csv#208", "Rosso, Antonio del", "211n", "new-person:antonio-del-rosso-7dc9d7753f", "antonio-del-rosso",
        "安东尼奥·德尔·罗索", "Antonio del Rosso",
        [("索引名", "Rosso, Antonio del", "S1（索引Q-R.csv#208）"), ("正文名", "Antonio", "S2（第8章第I节p.211）")],
        [template.source("第8章第I节；印刷页211", "Haskell称Antonio与Giovanni Battista是第四兄弟Nicola之子；del Rosso家族姓氏由索引和同段家族语境支持。", "the two sons, Antonio and Giovanni Battista, of a fourth brother Nicola", "02-sources/02-Markdown/08_CHP-8_sec_i.md", "line 96; print p.211")],
        "本卡按索引Q-R.csv#208登记Antonio del Rosso。第8章p.211只在家族段落中以Antonio称呼他，并称其为Nicola之子；不给出额外传记或外部身份。",
        "This card registers Antonio del Rosso under index Q-R.csv#208. Chapter 8, p.211, names him only as Antonio in the family passage and identifies him as Nicola’s son; no further biography or external identity is added.",
        "索引提供del Rosso姓氏，正文提供名字Antonio和父子语境；正文没有重复全名。",
        "The index supplies the del Rosso surname, while the body gives Antonio and the father-son context; the body does not repeat the full name.",
        ["st-chp8-p211-nicola-father-of-antonio"],
        {"st-chp8-p211-nicola-father-of-antonio": ("cand-2285", "cand-2280", "nicola_del_rosso_father_of_antonio_del_rosso")},
    ),
    target(
        "cand-2281", "Q-R.csv#209", "Rosso, Giovanni Battista del", "211n", "new-person:battista-del-giovanni-rosso-6a1d2554fa", "giovanni-battista-del-rosso",
        "乔瓦尼·巴蒂斯塔·德尔·罗索", "Giovanni Battista del Rosso",
        [("索引名", "Rosso, Giovanni Battista del", "S1（索引Q-R.csv#209）"), ("正文名", "Giovanni Battista", "S2（第8章第I节p.211）")],
        [template.source("第8章第I节；印刷页211", "Haskell称Giovanni Battista与Antonio是第四兄弟Nicola之子；del Rosso家族姓氏由索引和同段家族语境支持。", "the two sons, Antonio and Giovanni Battista, of a fourth brother Nicola", "02-sources/02-Markdown/08_CHP-8_sec_i.md", "line 96; print p.211")],
        "本卡按索引Q-R.csv#209登记Giovanni Battista del Rosso。第8章p.211只在家族段落中以Giovanni Battista称呼他，并称其为Nicola之子；不给出额外传记或外部身份。",
        "This card registers Giovanni Battista del Rosso under index Q-R.csv#209. Chapter 8, p.211, names him only as Giovanni Battista in the family passage and identifies him as Nicola’s son; no further biography or external identity is added.",
        "索引提供del Rosso姓氏，正文提供名字Giovanni Battista和父子语境；正文没有重复全名。",
        "The index supplies the del Rosso surname, while the body gives Giovanni Battista and the father-son context; the body does not repeat the full name.",
        ["st-chp8-p211-nicola-father-of-giovanni-battista"],
        {"st-chp8-p211-nicola-father-of-giovanni-battista": ("cand-2285", "cand-2281", "nicola_del_rosso_father_of_giovanni_battista_del_rosso")},
    ),
]

CORRECTIONS = {
    "cand-2280": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2280 by identical normalized full-name/explicit-alias anchor (antonio del rosso), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#208 supplies the full entry Rosso, Antonio del; p.211 body names Antonio as one of Nicola's two sons within the del Rosso family passage. The surname is index-linked, not repeated in the body. No external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2281": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2281 by identical normalized full-name/explicit-alias anchor (battista del giovanni rosso), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. Index Q-R.csv#209 supplies the full entry Rosso, Giovanni Battista del; p.211 body names Giovanni Battista as the other son of Nicola within the del Rosso family passage. The surname is index-linked, not repeated in the body. No external identity source was accessed; KU assignment remains for S4.",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three distinct del Rosso family person groups and refine two S3 rationales.")
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
        filename, index_id = t["entry"].split("#", 1)
        index_lines = (ROOT / "02-sources/03-Index/03-2-Index-CSV" / filename).read_text(encoding="utf-8-sig").splitlines()
        index_row = next(csv.reader([index_lines[int(index_id) + 1]]))
        assert index_row[0] == t["index_name"] and t["pages"] in index_row[-1]
        direct = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == t["primary"] or r.get("object_candidate_id") == t["primary"])}
        assert direct == set(t["endpoints"]), (t["primary"], sorted(direct))
        for statement_id, expected in t["endpoints"].items():
            statement = statement_by_id[statement_id]
            assert (statement.get("subject_candidate_id"), statement.get("object_candidate_id"), statement.get("predicate")) == expected
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

    paths = {t["card"]: ROOT / t["card"] for t in TARGETS}
    if all(planned_by_id[t["primary"]].get("ku_id") == t["ku"] for t in TARGETS):
        for t in TARGETS:
            assert paths[t["card"]].read_text(encoding="utf-8-sig") == cards[t["card"]]
            assert t["ku"] in manifest_by_ku and t["card"] in accepted_paths
        print("ALREADY REGISTERED: the grandfather and Nicola's two sons remain distinct and are fully registered.")
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3家族身份组校正与S4登记：del Rosso三代人物（{DATE}）\n\n"
    process_text += "- S3身份边界承接2026-10-16已记录的修正：cand-2279是兄弟三人的祖父，与既有cand-2275（生于1640年的Andrea del Rosso）分代；p.211的祖父称谓和p.212的Andrea续文支撑该组。cand-2280和cand-2281的索引分别给出Antonio del Rosso与Giovanni Battista del Rosso，正文p.211只给名字并说明二人是Nicola之子；原‘正文全名’理由撤回，姓氏按索引与家族上下文定位。三项均各自保留new组，不互相合并，不作外部匹配。\n"
    for t in TARGETS:
        process_text += f"- {t['primary']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}与相应正文页段支持source-local人物登记；直接S2关系候选{', '.join(t['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    relation_count = sum(len(t["relations"]) for t in TARGETS)
    process_text += f"\n本批登记{count}个S3 new人物组、{count}条候选映射和{field_count}条source_backed名称字段；{relation_count}条直接S2关系候选留待S6，未新增正式关系、S2断言或来源。登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。\n"
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += f"\n\n### S3家族身份组校正与S4登记：del Rosso三代人物（{DATE}）\n\n登记Andrea del Rosso（兄弟三人之祖父）、Antonio del Rosso与Giovanni Battista del Rosso三个source-local人物组；保留祖父与孙辈同名者的分代裁决，并修正两条正文姓名证据说明。{relation_count}条直接S2关系候选留待S6，未新增正式关系。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"

    with tempfile.TemporaryDirectory(prefix="pnp-s4-del-rosso-family-") as temp_name:
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
