from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_crosschapter_person_endpoints_20261017_batch6 as precedent

sync = precedent.sync
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

ITEMS = (
    {
        "candidate": "cand-4787",
        "group": "new-person:aronberg-lavin-marilyn-88b8833863",
        "ku_id": "units/persons/marilyn-aronberg-lavin",
        "card_rel": "04-knowledge/units/persons/marilyn-aronberg-lavin.md",
        "canonical_name": "玛丽莲·阿伦伯格·拉文（Marilyn Aronberg Lavin）",
        "name_en": "Marilyn Aronberg Lavin",
        "anchor": "s4-person-marilyn-aronberg-lavin-20261017",
        "description_cn": "第2章注释称Barberini inventories由Marilyn Aronberg Lavin出版；第20章后记称Marilyn Lavin后来出版了作者在罗马研究期间未能找到的相关清单。当前OCR在第2章将姓氏识为“Lavili”，既有S2候选记录注明印本读作“Lavin”；本卡保留OCR与印本校读差异。未独立查阅清单或该出版物。",
        "description_en": "A chapter 2 footnote says the Barberini inventories were published by Marilyn Aronberg Lavin; the chapter 20 postscript refers to a later publication by Marilyn Lavin of inventories the author had not found while working in Rome. The chapter 2 OCR reads “Lavili”; the existing S2 candidate note records “Lavin” in print. This entry preserves the OCR and print-reading difference. The inventories and publication were not independently consulted.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "lines": [149],
                "location": "第2章，印刷页56；OCR L149，注释续文",
                "span": "line 149; print p. 56, footnote continuation",
                "quote": "The Barberini inventories have been published by Marilyn Aronberg Lavili.",
                "summary": "哈斯克尔称Barberini inventories由Marilyn Aronberg Lavin出版；候选记录注明印本拼作Lavin而OCR误识为Lavili。",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "lines": [9],
                "location": "第20章后记，印刷页396；OCR L9",
                "span": "line 9; print p. 396",
                "quote": "well-indexed publication by Marilyn Lavin of all the inventories which eluded me when I was working in Rome",
                "summary": "哈斯克尔在后记中称Marilyn Lavin出版了一部编有详细索引的清单汇编，其中包括作者在罗马工作期间未能找到的清单。",
            },
        ),
        "statement_ids": (
            "st-chp2-seciv-l139-152-lavin-publishes-barberini-inventories",
        ),
    },
    {
        "candidate": "cand-0386",
        "group": "new-person:boncampagni-ugo-gregory-xiii-064b1bab8e",
        "ku_id": "units/persons/pope-gregory-xiii",
        "card_rel": "04-knowledge/units/persons/pope-gregory-xiii.md",
        "canonical_name": "教宗格列高利十三世（Pope Gregory XIII）",
        "name_en": "Pope Gregory XIII",
        "anchor": "s4-person-pope-gregory-xiii-20261017",
        "description_cn": "第2章注释将一项“建造就是公共慈善”的说法归于Pope Gregory XIII，并注明经Baglione、Orbaan转引；第3章以全名记述Gregory XIII将S. Stefano Rotondo划拨给耶稣会，并称Pope Gregory XIII于1575年将S. Maria della Vallicella划拨给圣斐理伯·内利。本卡保留第2章引文来源链，未独立核查转引文献。",
        "description_en": "A chapter 2 footnote attributes a statement about building as public charity to Pope Gregory XIII and cites it through Baglione and Orbaan. Chapter 3 says Gregory XIII allotted S. Stefano Rotondo to the Jesuits and that Pope Gregory XIII assigned S. Maria della Vallicella to Philip Neri in 1575. This entry preserves the chapter 2 citation chain; the cited texts were not independently checked.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "lines": [152],
                "location": "第2章，印刷页32；OCR L152，注5",
                "span": "line 152; print p. 32, note 5",
                "quote": "Baglione; p. 4—of Pope Gregory XIII, quoted by Orbaan, 1920, p. xv.",
                "summary": "哈斯克尔注释将前文关于建筑与公共慈善的说法关联至Pope Gregory XIII，并说明经Baglione、Orbaan转引；转引链未独立核查。",
            },
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "lines": [19, 20],
                "location": "第3章，印刷页67；OCR L19–20",
                "span": "lines 19–20; print p. 67",
                "quote": "allotted by Gregory XIII",
                "summary": "哈斯克尔称S. Stefano Rotondo于Gregory XIII时期划拨给耶稣会。",
            },
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "lines": [38],
                "location": "第3章，印刷页68；OCR L38",
                "span": "line 38; print p. 68",
                "quote": "S. Maria deUa Vallicclla was assigned to him in 1575 by Pope Gregory XIII.",
                "summary": "哈斯克尔称Pope Gregory XIII于1575年将S. Maria della Vallicella划拨给圣斐理伯·内利；地点名保留OCR原形。",
            },
        ),
        "statement_ids": (
            "st-chp2-secii-l147-193-gregory-quotation-chain",
        ),
    },
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two cross-chapter person identity groups as S4 KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id)
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    cards: list[tuple[dict[str, object], str, Path]] = []
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    for item in ITEMS:
        cid = str(item["candidate"])
        row = decisions[cid]
        assert candidate_by_id[cid].get("suggested_type") == "person"
        assert row.get("decision") == "new" and not row.get("ku_id"), (cid, row)
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        group_members = {
            other["candidate_id"] for other in alignments
            if other.get("candidate_id") and not other.get("external_source")
            and other.get("decision") == "new"
            and sync.get_group(other.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        card_path = ROOT / str(item["card_rel"])
        assert not card_path.exists() and str(item["card_rel"]) not in accepted
        assert not any(entry.get("ku_id") == item["ku_id"] or entry.get("card_path") == item["card_rel"] for entry in manifest)
        assert not any(
            entry.get("type") == "person"
            and entry.get("name_en", "").casefold() == str(item["name_en"]).casefold()
            for entry in manifest
        ), item["name_en"]

        for source in item["sources"]:
            source_text = " ".join((ROOT / str(source["file"])).read_text(encoding="utf-8-sig").split())
            assert " ".join(str(source["quote"]).split()) in source_text, (cid, source)

        direct = [
            statement for statement in statements
            if statement.get("subject_candidate_id") == cid or statement.get("object_candidate_id") == cid
        ]
        relation_ids = {
            statement["statement_id"] for statement in direct
            if (statement.get("qualifiers") or {}).get("relation_candidate") is True
        }
        assert relation_ids == set(item["statement_ids"]), (cid, relation_ids, item["statement_ids"])

        planned_by_id[cid]["ku_id"] = item["ku_id"]
        planned_by_id[cid]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}"
        planned_by_id[cid]["resolution_note"] += (
            f" S4 registration ({DATE}): {item['group']} maps to {item['ku_id']}; "
            "cross-chapter source identity registered; no independent external identity verification or formal S6 relation is implied."
        )
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "person",
            "canonical_name": item["canonical_name"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })
        cards.append((item, precedent.card_text(item), card_path))

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_append = f"""

### S4 person：跨章关系端点——Marilyn Aronberg Lavin 与 Pope Gregory XIII（{DATE}）

`cand-4787`（`{ITEMS[0]['group']}`）登记为[Marilyn Aronberg Lavin](../units/persons/marilyn-aronberg-lavin.md)。第2章注释的OCR作“Lavili”，现有S2候选记录注明印本为“Lavin”；第20章后记再次以Marilyn Lavin称呼该出版者。两处书内姓名及语境支持本组映射，未独立查阅清单出版物。`cand-0386`（`{ITEMS[1]['group']}`）登记为[Pope Gregory XIII](../units/persons/pope-gregory-xiii.md)。第2章脚注保存经Baglione与Orbaan传递的引文归属，第3章另以全名记述两项教会划拨语境；没有独立核查前者的转引来源。

两组各新增一个person KU和一条候选映射；两条直接S2关系候选均待S6。本次不新增正式关系或外部身份核验状态。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-lavin-gregory-xiii-20261017"></a>

### S4 person：两组跨章人物关系端点（{DATE}）

- `cand-4787`（`{ITEMS[0]['group']}`）依据第2章p.56注释的全名及第20章p.396后记“Marilyn Lavin”登记为[Marilyn Aronberg Lavin](../../../04-knowledge/units/persons/marilyn-aronberg-lavin.md)。S2候选记录注明印本姓氏为Lavin、OCR误作Lavili；卡片保留原OCR引句并记校读。出版物及清单未独立查阅，关系候选`st-chp2-seciv-l139-152-lavin-publishes-barberini-inventories`留待S6。
- `cand-0386`（`{ITEMS[1]['group']}`）依据第2、3章反复出现的Pope Gregory XIII／Gregory XIII指称登记为[Pope Gregory XIII](../../../04-knowledge/units/persons/pope-gregory-xiii.md)。第2章p.32注5将公共慈善引文归于该教宗，但转引链为Baglione、Orbaan，未独立核查；第3章p.67–68记述其与两项教会划拨相关的书内语境。关系候选`st-chp2-secii-l147-193-gregory-quotation-chain`保持为来源报告链，不升为经独立核实的事实。
- 两组各新增一个person KU与一条候选映射；两条直接S2关系候选继续待S6，不新增正式关系或外部身份核验状态。

The Lavin group follows the corrected print reading in the chapter 2 footnote and the chapter 20 postscript; the inventories were not independently consulted. Gregory XIII is named across chapters 2 and 3; the chapter 2 quotation remains a mediated Baglione/Orbaan source chain. Both direct relation candidates remain pending S6, with no formal relation or external verification status added.

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = PROCESS.read_text(encoding="utf-8-sig").rstrip() + process_append
    accepted_next = accepted
    for item, _, _ in cards:
        accepted_next = precedent.insert_accepted(accepted_next, str(item["card_rel"]))

    if args.dry_run:
        print("dry-run passed: " + "; ".join(f"{item['candidate']} -> {item['ku_id']}" for item in ITEMS))
        print(
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        print("verified_direct_relation_candidates=2; no external verification status or S6 formal relation rows will be written; no files changed")
        return 0

    for _, card, card_path in cards:
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_next, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
