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
ANCHOR = "s4-person-direct-endpoints-princess-rossi-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def make_target(primary, entry, index_name, pages, group, slug, zh, en, name_rows, sources, desc_zh, desc_en, context_zh, context_en, relations, endpoints):
    return {
        "primary": primary, "entry": entry, "index_name": index_name, "canonical_name": index_name,
        "pages": pages, "group": group, "ku": f"units/persons/{slug}",
        "card": f"04-knowledge/units/persons/{slug}.md", "name_zh": zh, "name_en": en,
        "name_rows": name_rows, "sources": sources, "zh": desc_zh, "en": desc_en,
        "context_zh": context_zh, "context_en": context_en, "relations": relations,
        "endpoints": endpoints, "external": None,
    }


TARGETS = [
    make_target(
        "cand-2270", "Q-R.csv#198", "Rossi, Domenico", "251", "new-person:domenico-rossi-6b2f907fa1", "domenico-rossi",
        "多梅尼科·罗西", "Domenico Rossi",
        [("索引名", "Rossi, Domenico", "S1（索引Q-R.csv#198）"), ("正文姓名形式", "Domenico Rossi", "S2（第9章导论p.251）")],
        [template.source("第9章导论；印刷页251", "Haskell称建筑师Domenico Rossi与画家Luigi Dorigny是Manin家族多项工程持续使用的团队成员。", "the architect Domenico Rossi and the painter Luigi Dorigny, on many of their enterprises", "02-sources/02-Markdown/09_CHP-9_intro.md", "line 111; print p.251")],
        "本卡登记索引Q-R.csv#198所列Domenico Rossi。第9章p.251称其为建筑师，并将其列入Manin家族多项工程所用团队；不扩展其他传记身份。",
        "This card registers Domenico Rossi under index Q-R.csv#198. Chapter 9, p.251, identifies him as an architect and places him on the team employed for many Manin family projects; no further biographical identity is added.",
        "正文提供全名与建筑师身份；Manin家族的聘用断言保留为直接S2关系候选，待S6审查。",
        "The body supplies his full name and role as architect; the Manin family's employment claim remains a direct S2 relation candidate for S6 review.",
        ["st-chp9-p251-manin-employed-rossi"],
        {"st-chp9-p251-manin-employed-rossi": ("cand-1519", "cand-2270", "manin_family_employed_architect_domenico_rossi")},
    ),
    make_target(
        "cand-2271", "Q-R.csv#199", "Rossi, Luigi de'", "143", "new-person:de-luigi-rossi-565b338a56", "luigi-de-rossi",
        "路易吉·德·罗西", "Luigi de' Rossi",
        [("索引名", "Rossi, Luigi de'", "S1（索引Q-R.csv#199）"), ("正文名", "Luigi", "S2（第5章第IV节p.143）")],
        [template.source("第5章第IV节；印刷页143", "正文仅称作曲家Luigi；同句明确称其为既有KU Carlo de' Rossi的兄弟。全名形式由索引提供。", "brother of the famous composer Luigi", "02-sources/02-Markdown/05_CHP-5_sec_iv.md", "line 21; print p.143")],
        "本卡按索引Q-R.csv#199登记Luigi de' Rossi。第5章p.143正文只称Luigi，称其为著名作曲家，并明确说他是Carlo de' Rossi的兄弟；没有把兄弟合并为同一人，也未添加外部传记身份。",
        "This card registers Luigi de' Rossi under index Q-R.csv#199. Chapter 5, p.143, calls him Luigi, describes him as a famous composer, and explicitly identifies him as Carlo de' Rossi's brother; the brothers remain distinct, with no external biography added.",
        "全名形式来自索引，正文仅给名字Luigi；与Carlo的兄弟关系明确区分二人，仍作为S2候选留待S6。",
        "The index supplies the full display name while the body gives only Luigi; the explicit brother relationship distinguishes him from Carlo and remains an S2 candidate for S6.",
        ["st-chp5-p143-carlo-de-rossi-brother-of-luigi"],
        {"st-chp5-p143-carlo-de-rossi-brother-of-luigi": ("cand-2269", "cand-2271", "brother_of")},
    ),
    make_target(
        "cand-2273", "Q-R.csv#201", "Rossi, Pellegrino de'", "122", "new-person:de-pellegrino-rossi-d7ade35e0b", "pellegrino-de-rossi",
        "佩莱格里诺·德·罗西", "Pellegrino de' Rossi",
        [("索引名", "Rossi, Pellegrino de'", "S1（索引Q-R.csv#201）"), ("正文姓名形式", "Pellegrino de Rossi", "S2（第5章第I节p.122）")],
        [template.source("第5章第I节；印刷页122", "Haskell称Pellegrino de Rossi曾给Mattia Preti等失业画家提供工作；所指工作未具体说明。", "one Pellegrino de Rossi who gave work to Mattia Preti among a number of unemployed artists", "02-sources/02-Markdown/05_CHP-5_sec_i.md", "line 22; print p.122")],
        "本卡登记索引Q-R.csv#201所列Pellegrino de' Rossi。第5章p.122以全名记载其曾向包括Mattia Preti在内的失业画家提供工作；不从这段材料推断其职业、身份或其他生平。",
        "This card registers Pellegrino de' Rossi under index Q-R.csv#201. Chapter 5, p.122, names him as having given work to unemployed artists including Mattia Preti; no occupation, identity, or biography beyond this passage is inferred.",
        "正文直接提供全名；提供工作给Mattia Preti的断言保留为S2关系候选，待S6审查。",
        "The body gives the full name; the report that he gave work to Mattia Preti remains an S2 relation candidate for S6 review.",
        ["st-chp5-p122-rossi-preti"],
        {"st-chp5-p122-rossi-preti": ("cand-2273", "cand-2056", "work_given_to_artist_reported")},
    ),
]

SAME = {
    "candidate": "cand-2267", "entry": "Q-R.csv#195", "index_name": "Rossano, Princess of", "pages": "131",
    "old_group": "new-person:of-princess-rossano-c9916a7fa1", "ku": "units/persons/olimpia-aldobrandini",
    "card": "04-knowledge/units/persons/olimpia-aldobrandini.md",
    "relations": {
        "st-chp5-p131-1643-replacement-commission": ("cand-4095", "cand-2267", "commissioned_by_princess_as_replacement_for_raphael_holy_family"),
        "st-chp5-p131-paid-one-hundred-scudi": ("cand-2267", "cand-2369", "paid_artist_100_scudi_for_rosary_painting"),
        "st-chp5-p131-princess-wife-of-camillo": ("cand-2267", "cand-1814", "wife_of"),
    },
}

CORRECTIONS = {
    "cand-2270": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2270 by identical normalized full-name/explicit-alias anchor (domenico rossi), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no exact existing person KU matched. Index Q-R.csv#198 and p.251 body both give Domenico Rossi; the body identifies him as an architect employed on many Manin family projects. No external identity source was accessed; source-local KU assignment remains for S4.",
    ),
    "cand-2271": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2271 by identical normalized full-name/explicit-alias anchor (de luigi rossi), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no exact existing Luigi de' Rossi KU matched. Index Q-R.csv#199 supplies the surname while p.143 body gives only Luigi; Haskell calls him a famous composer and explicitly distinguishes him as Carlo de' Rossi's brother. No external identity source was accessed; source-local KU assignment remains for S4.",
    ),
    "cand-2273": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2273 by identical normalized full-name/explicit-alias anchor (de pellegrino rossi), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no exact existing Pellegrino de' Rossi KU matched. Index Q-R.csv#201 and p.122 body give Pellegrino de Rossi; the passage describes him providing work to Mattia Preti and other unemployed artists. No external identity source was accessed; source-local KU assignment remains for S4.",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Reuse the Rossano princess identity and register three source-local Rossi person endpoints.")
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
    already = (
        all(alignment_by_id[t["primary"]].get("decision") == "new" and alignment_by_id[t["primary"]].get("ku_id") == t["ku"] for t in TARGETS)
        and alignment_by_id[SAME["candidate"]].get("decision") == "same"
        and alignment_by_id[SAME["candidate"]].get("ku_id") == SAME["ku"]
    )
    if already:
        for t in TARGETS:
            assert card_paths[t["card"]].read_text(encoding="utf-8-sig") == cards[t["card"]]
            assert t["ku"] in manifest_by_ku and t["card"] in accepted_paths
        print("ALREADY REGISTERED: identity reuse, three source-local groups, and the chronology note are present.")
        return 0

    index_root = ROOT / "02-sources/03-Index/03-2-Index-CSV"
    source_checks = [
        ("Q-R.csv#195", "Rossano, Princess of", "131", "02-sources/02-Markdown/05_CHP-5_sec_i.md", "the Princess of Rossano"),
        ("Q-R.csv#195", "Rossano, Princess of", "131", "02-sources/02-Markdown/05_CHP-5_sec_i.md", "wife of Pope Innocent X’s nephew Camillo"),
    ]
    for entry, index_name, pages, source_file, quote in source_checks:
        filename, index_id = entry.split("#", 1)
        lines = (index_root / filename).read_text(encoding="utf-8-sig").splitlines()
        indexed = next(csv.reader([lines[int(index_id) + 1]]))
        assert indexed[0] == index_name and pages in indexed[-1]
        assert re.sub(r"\s+", " ", quote) in re.sub(r"\s+", " ", (ROOT / source_file).read_text(encoding="utf-8-sig"))
    same_candidate = candidate_by_id[SAME["candidate"]]
    same_row = alignment_by_id[SAME["candidate"]]
    assert same_candidate.get("canonical_name") == SAME["index_name"] and same_candidate.get("suggested_type") == "person"
    assert same_row.get("decision") == "new" and sync.get_group(same_row.get("resolution_note", "")) == SAME["old_group"]
    assert not same_row.get("ku_id")
    assert SAME["ku"] in manifest_by_ku and SAME["card"] in accepted_paths and (ROOT / SAME["card"]).is_file()
    existing_same = [r for r in alignments if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "same" and r.get("ku_id") == SAME["ku"]]
    assert any(r["candidate_id"] == "cand-3210" for r in existing_same), "expected cross-project identity anchor is missing"
    direct_same = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and SAME["candidate"] in (r.get("subject_candidate_id"), r.get("object_candidate_id"))}
    assert direct_same == set(SAME["relations"]), (SAME["candidate"], sorted(direct_same))
    for statement_id, expected in SAME["relations"].items():
        row = statement_by_id[statement_id]
        assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == expected

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

    planned_alignments = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    for cid, (old, new) in CORRECTIONS.items():
        row = planned_by_id[cid]
        if old in row.get("resolution_note", ""):
            row["resolution_note"] = row["resolution_note"].replace(old, new, 1)
        else:
            assert new in row.get("resolution_note", ""), f"unexpected S3 rationale for {cid}"
    princess_row = planned_by_id[SAME["candidate"]]
    princess_row["decision"] = "same"
    princess_row["ku_id"] = SAME["ku"]
    princess_row["process_ref"] = PROCESS_REF
    princess_row["resolution_note"] += (
        f" S3 correction ({DATE}): decision new -> same, mapped to {SAME['ku']}. Haskell p.131 gives only the title Princess of Rossano and calls her Camillo Pamfili's wife; the existing Olimpia Aldobrandini KU records that spouse identity and cites Treccani's identification of Olimpia Pamphili as principessa di Rossano. Reuse the existing identity; retain Haskell's 1643 timing versus the KU's 1647 marriage date as a chronology discrepancy for later claim-level review. Previous new-group rationale retained as history."
    )
    for t in TARGETS:
        row = planned_by_id[t["primary"]]
        row["ku_id"], row["process_ref"] = t["ku"], PROCESS_REF
        row["resolution_note"] += f" S4 registration ({DATE}): group {t['group']} -> {t['ku']}; source-backed person registration only; direct S2 relation candidates remain for S6."

    assert all(not alignment_by_id[t["primary"]].get("ku_id") and t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not card_paths[t["card"]].exists() for t in TARGETS), "partial S4 registration requires reconciliation"

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
    assert totals["pending_groups"] == before_totals["pending_groups"] - count - 1
    assert totals["pending_members"] == before_totals["pending_members"] - count - 1
    assert totals["same_candidates"] == before_totals["same_candidates"] + 1
    assert totals["same_kus"] == before_totals["same_kus"]
    assert len(planned_manifest) == len(manifest) + count

    additions, card_count = template.extract_card_fields(cards)
    field_count = sum(len(t["name_rows"]) for t in TARGETS)
    assert card_count == count and len(additions) == field_count and all(r.get("evidence_status") == "source_backed" for r in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id", "")) for r in existing}
    ids = {r.get("enrichment_id", "") for r in existing}
    max_id = max((int(m.group(1)) for value in ids if (m := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for number, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + number:05d}"
        assert (row["ku_id"], row["field"], row["value"], row.get("source_id", "")) not in keys
        assert row["enrichment_id"] not in ids
    planned_enrichment = enrichment_text.rstrip("\r\n") + "\n" + "\n".join(json.dumps(r, ensure_ascii=False) for r in additions) + "\n"

    process_text = base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3身份复用与S4人物端点登记：Rossano公主及Rossi（{DATE}）\n\n"
    process_text += "- S3复用：cand-2267原登记为标题身份new组。第5章p.131仅称Princess of Rossano，并称其为Camillo Pamfili之妻；现有Olimpia Aldobrandini KU已有与Camillo的配偶身份记录，且引用Treccani《意大利传记辞典》对Olimpia Pamphili（principessa di Rossano）的识别，故改判same并映射至该KU。Haskell叙述的1643年委托早于该KU所载1647年婚期，保留为待核时间差异；不以本次身份复用裁定时间主张或正式关系。三条直接S2关系候选留待S6。\n"
    process_text += "- S3新组：cand-2270正文与索引均给出建筑师Domenico Rossi；cand-2271索引补足姓氏，正文仅称Luigi，并明确其为Carlo de' Rossi之兄弟，故与Carlo分别登记；cand-2273正文给出Pellegrino de Rossi全名。三人只按各自书内证据登记source-local人物，不按Rossi姓氏相互合并或引入外部身份。\n"
    for t in TARGETS:
        process_text += f"- {t['primary']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/{t['ku']}.md)。索引{t['entry']}与正文页段支持书内人物登记；直接S2关系候选{', '.join(t['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    relation_count = sum(len(t["relations"]) for t in TARGETS) + len(SAME["relations"])
    process_text += f"- cand-2267（标题候选）→ 既有[{SAME['ku']}](../../../04-knowledge/{SAME['card'].removeprefix('04-knowledge/')})；保留日期冲突待核，三条关系候选不在S4写入正式关系。\n"
    process_text += f"\n本批将1条S3决定由new改为same，登记{count}个new人物组及{field_count}条source_backed名称字段；{relation_count}条直接S2关系候选留待S6，未新增正式关系、S2断言或来源。登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。\n"
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += f"\n\n### S3身份复用与S4人物端点登记：Rossano公主及Rossi（{DATE}）\n\ncand-2267由标题身份new改为复用Olimpia Aldobrandini既有KU，并将1643委托叙述与该KU记载的1647婚期保留为待核时间差异；Domenico Rossi、Luigi de' Rossi、Pellegrino de' Rossi分别登记为三个source-local人物组。六条直接S2关系候选均留待S6；未新增正式关系。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"

    with tempfile.TemporaryDirectory(prefix="pnp-s4-princess-rossi-") as temp_name:
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
        print(f"S3/S4 dry-run passed: reuse=1; new_groups={count}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}; no files changed")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; same={totals['same_candidates']} candidates/{totals['same_kus']} KUs")
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
    print(f"applied: reuse=1; new_groups={count}; name_fields={field_count}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
