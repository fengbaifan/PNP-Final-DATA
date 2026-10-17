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
ANCHOR = "s4-person-direct-endpoints-p-late-section-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

TARGETS = [
    {
        "primary": "cand-2064", "entry": "P.csv#267", "index_name": "Procaccini, Ercole",
        "canonical_name": "Procaccini, Ercole", "pages": "216",
        "group": "new-person:ercole-procaccini-395244d722", "ku": "units/persons/ercole-procaccini",
        "card": "04-knowledge/units/persons/ercole-procaccini.md",
        "name_zh": "埃尔科莱·普罗卡奇尼", "name_en": "Ercole Procaccini",
        "name_rows": [("索引名", "Procaccini, Ercole", "S1（索引P.csv#267）"), ("正文姓名形式", "Ercole Proccaccini", "S2（第8章p.216）")],
        "sources": [template.source("第8章第II节；印刷页216", "Haskell称Cristoforo Storer为米兰画家Ercole Proccaccini的弟子；正文拼写与索引有一字母差异。", "Ercole Proccaccini, who had already had close contacts", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "lines 23–24; print p.216")],
        "zh": "本卡按索引P.csv#267登记Ercole Procaccini。第8章p.216称Cristoforo Storer为Ercole Proccaccini的弟子；正文拼写保留，未据此外查身份。",
        "en": "This card registers Ercole Procaccini under index P.csv#267. Chapter 8, p.216, calls Cristoforo Storer a pupil of Ercole Proccaccini; the body spelling is preserved, with no external identity match added.",
        "context_zh": "索引写作Procaccini, Ercole，正文写作Ercole Proccaccini；这项书内拼写差异不改变其与Andrea Procaccini的区分。",
        "context_en": "The index gives Procaccini, Ercole, while the body spells the name Ercole Proccaccini. This source-local spelling difference does not merge him with Andrea Procaccini.",
        "relations": ["st-chp8-p216-storer-pupil-proccaccini"],
        "endpoints": {"st-chp8-p216-storer-pupil-proccaccini": ("cand-2512", "cand-2064", "pupil_of")},
        "external": None,
    },
    {
        "primary": "cand-2069", "entry": "P.csv#272", "index_name": "Pufendorf, Samuel",
        "canonical_name": "Pufendorf, Samuel", "pages": "320",
        "group": "new-person:pufendorf-samuel-2430e8c679", "ku": "units/persons/samuel-pufendorf",
        "card": "04-knowledge/units/persons/samuel-pufendorf.md",
        "name_zh": "塞缪尔·普芬多夫", "name_en": "Samuel Pufendorf",
        "name_rows": [("索引名", "Pufendorf, Samuel", "S1（索引P.csv#272）"), ("正文姓氏形式", "Puffendorf", "S2（第10章p.320）")],
        "sources": [template.source("第10章第II节；印刷页320", "Haskell称Lodoli以Cicero和Puffendorf on the duties of man教育学生；此处只出现姓氏，具体著作未指明。", "Puffendorf on the duties of man.", "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "line 159; print p.320")],
        "zh": "本卡按索引P.csv#272登记Samuel Pufendorf。第10章p.320正文仅写Puffendorf，并提及“on the duties of man”；具体著作未指明，未添加外部身份匹配。",
        "en": "This card registers Samuel Pufendorf under index P.csv#272. Chapter 10, p.320, uses only the surname form Puffendorf and refers to ‘the duties of man’; no specific work or external identity match is added.",
        "context_zh": "索引在正文所指p.320处给出Samuel这一名字；正文的Puffendorf拼法与索引不同。S3据索引页段与该处语境保留为书内人物组。",
        "context_en": "The index supplies the given name Samuel for the cited p.320 passage; the body spells the surname Puffendorf. S3 retains a source-local person group based on the indexed page and passage context.",
        "relations": ["st-chp10-p320-lodoli-taught-puffendorf-on-duties"],
        "endpoints": {"st-chp10-p320-lodoli-taught-puffendorf-on-duties": ("cand-1411", "cand-2069", "taught-from-puffendorf-on-duties-of-man")},
        "external": None,
    },
    {
        "primary": "cand-2072", "entry": "P.csv#275", "index_name": "Pulzone, Scipione",
        "canonical_name": "Pulzone, Scipione", "pages": "66",
        "group": "new-person:pulzone-scipione-a1ff2a9238", "ku": "units/persons/scipione-pulzone",
        "card": "04-knowledge/units/persons/scipione-pulzone.md",
        "name_zh": "西皮奥内·普尔佐内", "name_en": "Scipione Pulzone",
        "name_rows": [("索引名", "Pulzone, Scipione", "S1（索引P.csv#275）"), ("正文姓名形式", "Scipione Pulzone", "S2（第3章第II节p.66）")],
        "sources": [template.source("第3章第II节；印刷页66", "Haskell举Scipione Pulzone为虔诚信女所引入的艺术家例子；未指明具体女性或礼拜堂。", "men Eke Scipione\nPulzone, Agostino Ciampelh", "02-sources/02-Markdown/03_CHP-3_sec_ii.md", "lines 10–11; print p.66")],
        "zh": "本卡按索引P.csv#275登记Scipione Pulzone。第3章p.66将他列为一些虔诚信女所引入的艺术家之一；原文未指明具体介绍者或礼拜堂。",
        "en": "This card registers Scipione Pulzone under index P.csv#275. Chapter 3, p.66, lists him as one of the artists introduced by some pious ladies; it does not identify a particular woman or chapel.",
        "context_zh": "正文中的Scipione与Pulzone由同页相邻mention组成完整姓名；S3保留该书内人物组。有关介绍者及具体礼拜堂的关系候选仍待S6。",
        "context_en": "Adjacent mentions of Scipione and Pulzone on the same page form the full name in the body; S3 retains this source-local person group. The introducer and specific chapel remain unresolved for S6.",
        "relations": ["st-chp3-secii-l6-17-pious-ladies-introduced-pulzone"],
        "endpoints": {"st-chp3-secii-l6-17-pious-ladies-introduced-pulzone": ("cand-5008", "cand-2072", "introduced_artist_to_side_chapels")},
        "external": None,
    },
]

CORRECTIONS = {
    "cand-2064": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2064 by identical normalized full-name/explicit-alias anchor (ercole procaccini), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. The index entry gives Procaccini, Ercole; the cited chapter 8 p.216 body spells the name Ercole Proccaccini. The indexed page and passage support this source-local group; preserve the spelling difference and keep it distinct from Andrea Procaccini. No external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2069": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2069 by identical normalized full-name/explicit-alias anchor (pufendorf samuel), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. The index entry supplies the given name Samuel; the cited chapter 10 p.320 body uses only the surname Puffendorf in a reference to duties of man. The indexed page and passage context support this source-local group; the spelling is preserved and the specific work remains unidentified. No external identity source was accessed; KU assignment remains for S4.",
    ),
    "cand-2072": (
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-2072 by identical normalized full-name/explicit-alias anchor (pulzone scipione), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.",
        "New source-local person candidate: no unique existing person KU matched. The index entry names Pulzone, Scipione; two adjacent chapter 3 p.66 mentions give Scipione and Pulzone, together forming the full name. No external identity source was accessed; KU assignment remains for S4.",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct P-section S3 evidence rationales and register three person endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    template.TARGETS = TARGETS
    template.DATE, template.ANCHOR, template.PROCESS_REF = DATE, ANCHOR, PROCESS_REF
    base = template.helper.base
    sync = base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    cards = {target["card"]: template.make_card(target) for target in TARGETS}

    for target in TARGETS:
        candidate, row = candidate_by_id[target["primary"]], alignment_by_id[target["primary"]]
        assert candidate.get("suggested_type") == "person"
        assert (candidate.get("canonical_name"), candidate.get("index_entry_id"), candidate.get("index_page_range")) == (target["canonical_name"], target["entry"], target["pages"])
        assert row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == target["group"], (target["primary"], row.get("decision"), sync.get_group(row.get("resolution_note", "")), target["group"])
        assert not row.get("ku_id") or row.get("ku_id") == target["ku"]
        members = [r["candidate_id"] for r in alignments if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == target["group"]]
        assert members == [target["primary"]]
        index_file, index_id = target["entry"].split("#", 1)
        index_lines = (ROOT / "02-sources/03-Index/03-2-Index-CSV" / index_file).read_text(encoding="utf-8-sig").splitlines()
        index_row = next(csv.reader([index_lines[int(index_id) + 1]]))
        assert index_row[0] == target["index_name"] and target["pages"] in index_row[-1]
        direct = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == target["primary"] or r.get("object_candidate_id") == target["primary"])}
        assert direct == set(target["endpoints"]), (target["primary"], sorted(direct))
        for statement_id, expected in target["endpoints"].items():
            statement = statement_by_id[statement_id]
            assert (statement.get("subject_candidate_id"), statement.get("object_candidate_id"), statement.get("predicate")) == expected
        for item in target["sources"]:
            source_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", source_text), (target["primary"], item["span"])

    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id") and not row.get("external_source")}
    for candidate_id, (old, new) in CORRECTIONS.items():
        row = planned_by_id[candidate_id]
        note = row.get("resolution_note", "")
        if old in note:
            row["resolution_note"] = note.replace(old, new, 1)
        else:
            assert new in note, f"unexpected S3 rationale for {candidate_id}"

    already_registered = all(planned_by_id[target["primary"]].get("ku_id") == target["ku"] for target in TARGETS)
    card_paths = {target["card"]: ROOT / target["card"] for target in TARGETS}
    if already_registered:
        for target in TARGETS:
            assert card_paths[target["card"]].read_text(encoding="utf-8-sig") == cards[target["card"]]
            assert target["ku"] in manifest_by_ku and target["card"] in accepted_paths
        if args.dry_run:
            print("ALREADY REGISTERED: all P-section late person groups and corrected S3 rationales are present.")
            return 0
        print("ALREADY REGISTERED: no files changed.")
        return 0
    assert all(not planned_by_id[target["primary"]].get("ku_id") and target["ku"] not in manifest_by_ku and target["card"] not in accepted_paths and not card_paths[target["card"]].exists() for target in TARGETS), "partial S4 registration requires explicit reconciliation"

    before_stats = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for target in TARGETS:
        row = planned_by_id[target["primary"]]
        row["ku_id"], row["process_ref"] = target["ku"], PROCESS_REF
        row["resolution_note"] += f" S4 registration ({DATE}): group {target['group']} -> {target['ku']}; source-backed person registration only; direct S2 relation candidates remain for S6."
        planned_manifest.append({"ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"], "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"]})
        planned_accepted = base.insert_accepted(planned_accepted, target["card"])
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
    expected_name_fields = sum(len(target["name_rows"]) for target in TARGETS)
    assert cards_with_tables == count and len(additions) == expected_name_fields
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    current_enrichment = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id", "")) for r in current_enrichment}
    ids = {r.get("enrichment_id", "") for r in current_enrichment}
    max_id = max((int(match.group(1)) for value in ids if (match := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for number, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + number:05d}"
        assert (row["ku_id"], row["field"], row["value"], row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in additions) + "\n"

    process_text = template.helper.base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3理由校正与S4人物直接端点登记：P索引末段（{DATE}）\n\n"
    process_text += "- S3理由校正：cand-2064正文拼作Ercole Proccaccini，索引为Procaccini, Ercole；以页段和索引对应支持source-local new组，保留拼写差异，并与已有Andrea Procaccini人物KU区分。cand-2069索引给出Samuel，p.320正文只写Puffendorf；此前声称正文提供完整姓名的理由撤回，具体著作仍未指明。cand-2072的Scipione与Pulzone来自同页相邻mention，合读为正文全名。三项决定均保持new，不据此新增外部身份匹配。\n"
    for target in TARGETS:
        process_text += f"- {target['primary']}（{target['group']}）→ [{target['name_zh']}（{target['name_en']}）](../../../04-knowledge/{target['ku']}.md)。索引{target['entry']}与列明的正文页段支持source-local人物登记；直接S2关系候选{', '.join(target['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    relation_count = sum(len(target["relations"]) for target in TARGETS)
    process_text += f"\n本批登记{count}个S3 new人物组、{count}条候选映射和{expected_name_fields}条source_backed名称字段；{relation_count}条直接S2关系候选留待S6，未新增正式关系、S2断言或来源。登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。\n"
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += f"\n\n### S3理由校正与S4人物直接端点登记：P索引末段（{DATE}）\n\n登记Ercole Procaccini、Samuel Pufendorf与Scipione Pulzone三个source-local人物组。修正cand-2064、cand-2069、cand-2072的S3证据表述，保留new决定；三条直接S2关系候选留待S6，未新增正式关系。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"

    with tempfile.TemporaryDirectory(prefix="pnp-s4-p-late-persons-") as temp_name:
        temp = Path(temp_name)
        alignment_stage, manifest_stage = temp / "alignment.csv", temp / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: alignment_stage.read_bytes(), MANIFEST: manifest_stage.read_bytes(),
            ENRICHMENT: template.with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: template.with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: template.with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: template.with_bom(result_text + "\n", RESULT.read_bytes()),
        }
        for target in TARGETS:
            writes[ROOT / target["card"]] = template.with_bom(cards[target["card"]])
    if args.dry_run:
        print(f"S3/S4 dry-run passed: groups={count}; s3_rationale_corrections={len(CORRECTIONS)}; name_fields={expected_name_fields}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}; no files changed")
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
    print(f"applied: groups={count}; s3_rationale_corrections={len(CORRECTIONS)}; name_fields={expected_name_fields}; direct_relation_candidates={relation_count}; formal_relations_added=0; KU={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
