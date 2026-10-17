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
        "candidate": "cand-2495",
        "group": "new-person:micco-spadaro-2b56032967",
        "ku_id": "units/persons/micco-spadaro",
        "card_rel": "04-knowledge/units/persons/micco-spadaro.md",
        "canonical_name": "米科·斯帕达罗（Micco Spadaro）",
        "name_en": "Micco Spadaro",
        "anchor": "s4-person-micco-spadaro-20261017",
        "description_cn": "第5章注释称Micco Spadaro的绘画藏于那不勒斯圣马蒂诺博物馆；该群组与本章另述的Cerquozzi《Masaniello起义》双场景画保持区分。第8章注释另称其人物形象出现在Codazzi作品中，并记载这些画作经过Roomer、Van den Einden及Colonna收藏。本卡记录不同语境，不将其合并为单一作品组或完整收藏清单。",
        "description_en": "A chapter 5 note says that pictures by Micco Spadaro are in the Museo di San Martino, Naples; that group remains distinct from the double-scene *Revolt of Masaniello* picture discussed in the same chapter. A chapter 8 note also mentions figures by Spadaro in works by Codazzi and says those pictures passed through the Roomer, Van den Einden, and Colonna collections. This entry records the separate contexts without treating them as one work group or a complete collection inventory.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
                "lines": [97, 98],
                "location": "第5章，印刷页139；OCR L97–98",
                "span": "lines 97–98; print p. 139",
                "quote": "the almost mediaeval vision of Cerquozzi’s contemporary Micco Spadaro who depicts Masaniello like some early saint twice in the same canvas",
                "summary": "哈斯克尔称Cerquozzi的同时代人Micco Spadaro在同一画布上两次描绘Masaniello；该双场景画与注释所称圣马蒂诺博物馆绘画群保持分立。",
            },
            {
                "file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
                "lines": [152],
                "location": "第5章，印刷页139，注5续；OCR L152",
                "span": "line 152; print p. 139, note 5 continuation",
                "quote": "Micco Spadaro’s pictures are in the Museo di S. Martino, Naples.",
                "summary": "哈斯克尔称Micco Spadaro的绘画藏于那不勒斯圣马蒂诺博物馆；未给出完整作品清单。",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "lines": [136],
                "location": "第8章，印刷页204及207的注释段；OCR L136",
                "span": "line 136; chapter 8 notes mapped to pp. 204 and 207",
                "quote": "the two pictures by Codazzi with figures by Micco Spadaro",
                "summary": "哈斯克尔注释称两幅Codazzi作品带有Micco Spadaro绘制的人物，并追踪这两幅画经过的收藏。",
            },
        ),
        "statement_ids": (
            "st-chp5-notes-l126-165-l152-spadaro-workgroup-authorship",
        ),
    },
    {
        "candidate": "cand-1284",
        "group": "new-person:adolphus-gustavus-of-sweden-e13b1682aa",
        "ku_id": "units/persons/gustavus-adolphus-sweden",
        "card_rel": "04-knowledge/units/persons/gustavus-adolphus-sweden.md",
        "canonical_name": "古斯塔夫·阿道夫（Gustavus Adolphus of Sweden）",
        "name_en": "Gustavus Adolphus of Sweden",
        "anchor": "s4-person-gustavus-adolphus-sweden-20261017",
        "description_cn": "第6章称Christina在罗马展示的绘画收藏包括其父亲Gustavus Adolfus从布拉格劫掠的作品；第7章再称瑞典军队劫掠布拉格王室收藏并使其女Christina受益，姓名拼作Gustavus Adolphus。两章的拼写异文与来源各自的责任者表述均保留；本卡只登记人物端点，不独立裁决藏品转移或劫掠责任。",
        "description_en": "Chapter 6 says the pictures Christina displayed in Rome included works her father Gustavus Adolfus had looted from Prague; chapter 7 says Swedish troops looted the royal collections in Prague for the ultimate benefit of his daughter Christina and spells his name Gustavus Adolphus. Both spelling forms and each chapter's attribution of agency are preserved. This entry registers the person endpoint without independently adjudicating the collection transfer or responsibility for the looting.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md",
                "lines": [48, 49],
                "location": "第6章，印刷页160；OCR L48–49",
                "span": "lines 48–49; print p. 160",
                "quote": "her father Gustavus Adolfus had looted from Prague",
                "summary": "哈斯克尔称Christina展示的绘画收藏包括其父亲Gustavus Adolfus从布拉格劫掠的作品；相关历史主张仅按原书记录。",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "lines": [8],
                "location": "第7章，印刷页193；OCR L8",
                "span": "line 8; print p. 193",
                "quote": "The royal collections, however, had been housed in Prague, where they had been looted by Swedish troops for the ultimate benefit of Gustavus Adolphus’s daughter Christina.",
                "summary": "哈斯克尔称瑞典军队劫掠了布拉格王室收藏，最终使Gustavus Adolphus之女Christina受益。",
            },
        ),
        "statement_ids": (
            "st-chp6-p160-gustavus-looted-collection-from-prague",
        ),
    },
    {
        "candidate": "cand-0367",
        "group": "new-person:berrettoni-niccolo-e92fe6e410",
        "ku_id": "units/persons/niccolo-berrettoni",
        "card_rel": "04-knowledge/units/persons/niccolo-berrettoni.md",
        "canonical_name": "尼科洛·贝雷托尼（Niccolò Berrettoni）",
        "name_en": "Niccolò Berrettoni",
        "anchor": "s4-person-niccolo-berrettoni-20261017",
        "description_cn": "第6章注释提到Berrettoni在一座宫殿中的作品；第7章称Niccolò Berrettoni是Maratta的学生，德尔·卡尔皮奥常到其画室访问，并曾试图说服他赴马德里供职。OCR省略Niccolò的重音符号，S2记录印本作Niccolò。本卡保留姓名依据及书内职业语境，不把关系候选升级为正式师承边。",
        "description_en": "A chapter 6 note mentions work by Berrettoni in a palace. Chapter 7 identifies Niccolò Berrettoni as a pupil of Maratta, says Del Carpio visited his studio regularly, and reports that he tried to persuade him to work for the King in Madrid. The OCR omits the accent in Niccolò; S2 records the print reading as Niccolò. This entry records the name and the contexts in the book without turning the relation candidate into a formal apprenticeship edge.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md",
                "lines": [71],
                "location": "第6章，印刷页161，注4；OCR L71",
                "span": "line 71; print p. 161, note 4",
                "quote": "for the work by Berrettoni in the palace",
                "summary": "哈斯克尔注释提示参看Berrettoni在该宫殿中的作品；注中没有给出名字或具体作品题名。",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "lines": [273],
                "location": "第7章，印刷页191；OCR L273",
                "span": "line 273; print p. 191",
                "quote": "Niccolo Berrettoni, a pupil of Maratta",
                "summary": "哈斯克尔称Niccolo Berrettoni是Maratta的学生；S2记录印本姓名含重音符号Niccolò。",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "lines": [286],
                "location": "第7章，印刷页192；OCR L286",
                "span": "line 286; print p. 192",
                "quote": "Giacinto Calandrucci and Niccolo Berrettoni",
                "summary": "哈斯克尔称Del Carpio曾试图说服Niccolo Berrettoni赴马德里为国王工作；书页读作Niccolò。",
            },
        ),
        "statement_ids": (
            "st-chp7-p191-i13",
        ),
    },
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three cross-chapter person identity groups as S4 KUs.")
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

### S4 person：跨章关系端点——Micco Spadaro、Gustavus Adolphus 与 Niccolò Berrettoni（{DATE}）

`cand-2495`（`{ITEMS[0]['group']}`）登记为[Micco Spadaro](../units/persons/micco-spadaro.md)。第5章注释定位其绘画于圣马蒂诺博物馆，第8章注释另述其为Codazzi作品绘制人物；相关作品语境与《Masaniello起义》双场景画保持分离。`cand-1284`（`{ITEMS[1]['group']}`）登记为[Gustavus Adolphus of Sweden](../units/persons/gustavus-adolphus-sweden.md)，保留第6章OCR“Adolfus”与第7章“Adolphus”形式及两章各自的布拉格藏品叙述；不独立裁决劫掠责任。`cand-0367`（`{ITEMS[2]['group']}`）登记为[Niccolò Berrettoni](../units/persons/niccolo-berrettoni.md)，第6章以姓氏提及其宫殿作品，第7章两次给出全名且页图有重音符号。

三组各新增一个person KU和一条候选映射；3条直接S2关系候选均待S6。本次不新增正式关系或外部身份核验状态。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-spadaro-gustavus-berrettoni-20261017"></a>

### S4 person：三组跨章人物关系端点（{DATE}）

- `cand-2495`（`{ITEMS[0]['group']}`）依据第5章p.139全名及第8章收藏注释中的重复全名登记为[Micco Spadaro](../../../04-knowledge/units/persons/micco-spadaro.md)。`st-chp5-notes-l126-165-l152-spadaro-workgroup-authorship`所指博物馆绘画群，与第5章正文的Cerquozzi《Masaniello起义》双场景画分立；第8章Codazzi作品中的人物提及另作语境记录。
- `cand-1284`（`{ITEMS[1]['group']}`）依据第6章p.160及第7章p.193关于Christina之父的跨章指称登记为[Gustavus Adolphus of Sweden](../../../04-knowledge/units/persons/gustavus-adolphus-sweden.md)。第6章OCR读作Adolfus，候选记录注明印本为Adolphus；第7章直接使用Adolphus。两章对布拉格藏品被劫事件的责任者表述均保留，关系候选`st-chp6-p160-gustavus-looted-collection-from-prague`不作独立历史验证。
- `cand-0367`（`{ITEMS[2]['group']}`）依据第6章p.161注4姓氏及第7章p.191–192全名登记为[Niccolò Berrettoni](../../../04-knowledge/units/persons/niccolo-berrettoni.md)。第7章将其称为Maratta的学生；印本重音由S2页图记录，OCR不含重音。候选`st-chp7-p191-i13`仍待S6，不在卡片中登记正式师承边。
- 三组各新增一个person KU与一条候选映射；3条直接S2关系候选仍待S6，不新增正式关系或外部身份核验状态。

The Spadaro museum group remains distinct from the Masaniello double-scene picture. Gustavus Adolphus retains both source spellings and chapter attributions concerning the Prague collections. Berrettoni's pupil statement remains a relation candidate. All three candidates remain pending S6, with no formal relation or external identity verification added.

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
        print("verified_direct_relation_candidates=3; no external verification status or S6 formal relation rows will be written; no files changed")
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
