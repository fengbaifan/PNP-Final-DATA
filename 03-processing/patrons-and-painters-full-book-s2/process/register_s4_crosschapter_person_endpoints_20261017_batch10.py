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
        "candidate": "cand-1336",
        "group": "new-person:apostate-julian-faf208b96a",
        "ku_id": "units/persons/julian-the-apostate",
        "card_rel": "04-knowledge/units/persons/julian-the-apostate.md",
        "canonical_name": "背教者尤利安（Julian the Apostate）",
        "name_en": "Julian the Apostate",
        "anchor": "s4-person-julian-the-apostate-20261017",
        "description_cn": "第4章称Cassiano所藏图稿序言可参照1630年在巴黎重印的Julian the Apostate作品集，并由哈斯克尔转述Petau序言为阅读Julian辩护的理由；第7章又称Verrio在Hampton Court的壁画题材取自Julian the Apostate的著作。第4章相关陈述是哈斯克尔对Petau序言的概述，本卡不写成Petau原文已独立核实。",
        "description_en": "Chapter 4 says Cassiano's proposed preface to his drawing volumes could use the preface to a 1630 Paris edition of Julian the Apostate's works, and Haskell summarizes Petau's defense of reading Julian. Chapter 7 says the subject of Verrio's Hampton Court fresco was drawn from Julian's writings. The chapter 4 statement is Haskell's summary of Petau's preface and is not presented as independently verified from Petau's text.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "lines": [127],
                "location": "第4章，印刷页109；OCR L127",
                "span": "line 127; print p. 109",
                "quote": "what P. Denis Petau wrote as a preface to his edition of the works of Julian the Apostate republished in Paris in 1630",
                "summary": "哈斯克尔称Cassiano提出以Petau为1630年巴黎重印的Julian the Apostate作品集所写序言作为图稿集序言；随后对Petau辩护阅读Julian的理由作概述。",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "lines": [59],
                "location": "第7章，印刷页196；OCR L59",
                "span": "line 59; print p. 196",
                "quote": "whose subject was chosen from the writings of Julian the Apostate",
                "summary": "哈斯克尔称Verrio在Hampton Court创作的一幅寓意壁画，其题材取自Julian the Apostate的著作。",
            },
        ),
        "statement_ids": (
            "st-chp4-sec-ii-p109-petau-preface-argument",
        ),
    },
    {
        "candidate": "cand-2800",
        "group": "new-person:goffredo-wals-e36dbf4df9",
        "ku_id": "units/persons/goffredo-wals",
        "card_rel": "04-knowledge/units/persons/goffredo-wals.md",
        "canonical_name": "戈弗雷多·瓦尔斯（Goffredo Wals）",
        "name_en": "Goffredo Wals",
        "anchor": "s4-person-goffredo-wals-20261017",
        "description_cn": "第5章称Claude有说法是在罗马展览中看到Flemish画家Goffredo Wals的风景画后前往那不勒斯师从他，原文保留“is supposed to have”限定；第8章收藏叙述中出现拼作“Gioffredo Wals”的形式。本卡保留该拼写异文，不把传闻语气改写为确定师承。",
        "description_en": "Chapter 5 says Claude is supposed to have seen landscapes by the Flemish artist Goffredo Wals at a Roman exhibition and then gone to Naples to study under him; the source's “is supposed to have” qualification is retained. Chapter 8 gives the spelling “Gioffredo Wals” in a collection account. This entry preserves the spelling variant and does not turn the reported story into a certain apprenticeship.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "lines": [53],
                "location": "第5章，印刷页125；OCR L53",
                "span": "line 53; print p. 125",
                "quote": "Claude is supposed to have seen landscapes by the Flemish artist Goffredo Wals at an exhibition in Rome and to have been so struck with them that he went to study under him in Naples",
                "summary": "哈斯克尔保留“is supposed to have”限定，称Claude据说看过Goffredo Wals的风景画后去那不勒斯师从他；未提供日期。",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "lines": [35, 36],
                "location": "第8章，印刷页206；OCR L35–36",
                "span": "lines 35–36; print p. 206",
                "quote": "Cornelius Poelenburgh, Corneille Schut, Gioffredo Wals, Gerard van dor Bos",
                "summary": "哈斯克尔在Roomer的收藏画家名单中以“Gioffredo Wals”拼写该名；与第5章“Goffredo Wals”形式并存。",
            },
        ),
        "statement_ids": (
            "st-chp5-p125-claude-studied-under-wals",
        ),
    },
    {
        "candidate": "cand-1168",
        "group": "new-person:giacinto-gigli-cef75d311f",
        "ku_id": "units/persons/giacinto-gigli",
        "card_rel": "04-knowledge/units/persons/giacinto-gigli.md",
        "canonical_name": "贾钦托·吉利（Giacinto Gigli）",
        "name_en": "Giacinto Gigli",
        "anchor": "s4-person-giacinto-gigli-20261017",
        "description_cn": "第5章以OCR形式“Giacinto GigE”提及一位小公务员兼业余诗人，并称其细致记录宗教节庆与奇迹事件的日记反映了宏大社交圈之外的罗马生活；书内索引G.csv第77行给出姓名“Gigli, Giacinto”。第6章注释再次以Gigli为相关引文出处。本卡保留OCR读法和索引全名依据，不将该日记版本说成已独立查阅。",
        "description_en": "Chapter 5's OCR reads “Giacinto GigE” for a minor civil servant and amateur poet whose detailed diary recorded religious festivals and miraculous occurrences, offering a view of Roman life outside grander social circles. The book index, G.csv line 77, gives the name “Gigli, Giacinto.” Chapter 6 cites Gigli again in a note. This entry preserves the OCR form and index evidence without implying that the diary edition was independently consulted.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "lines": [123],
                "location": "第5章，印刷页131；OCR L123",
                "span": "line 123; print p. 131",
                "quote": "men like Giacinto GigE, minor civil servant and amateur poet, who kept a detailed diary diEgently recording the great religious festivals and miraculous occurrences",
                "summary": "哈斯克尔称Giacinto GigE为小公务员兼业余诗人，并称其日记记录宗教节庆和奇迹事件；S2记录印本读作Gigli及diligently，OCR误读分别为GigE、diEgently。",
            },
            {
                "file": "02-sources/03-Index/03-2-Index-CSV/G.csv",
                "lines": [77],
                "location": "书内索引，G.csv L77；页码131、122注",
                "span": "line 77; index locator lists p. 131 and p. 122 note",
                "quote": "Gigli, Giacinto",
                "summary": "书内索引将人物列为Gigli, Giacinto，并列出第5章正文与第6章注释页码。",
            },
            {
                "file": "02-sources/02-Markdown/06_CHP-6_intro.md",
                "lines": [11],
                "location": "第6章注4；OCR L11",
                "span": "line 11; chapter 6, note 4",
                "quote": "For the effects of the war in Rome see Gigli, pp. 203-40.",
                "summary": "第6章注4再次引用Gigli关于罗马战争影响的页码；该书目对象未在本任务中独立查阅。",
            },
        ),
        "statement_ids": (
            "st-chp5-p131-gigli-diary",
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

### S4 person：跨章关系端点——Julian the Apostate、Goffredo Wals 与 Giacinto Gigli（{DATE}）

`cand-1336`（`{ITEMS[0]['group']}`）登记为[Julian the Apostate](../units/persons/julian-the-apostate.md)，依据第4章1630年版本语境及第7章作品题材提及；第4章对Petau序言的说明仍是Haskell转述。`cand-2800`（`{ITEMS[1]['group']}`）登记为[Goffredo Wals](../units/persons/goffredo-wals.md)，第5章原文的“is supposed to have”限定保留，第8章异写“Gioffredo”并存。`cand-1168`（`{ITEMS[2]['group']}`）登记为[Giacinto Gigli](../units/persons/giacinto-gigli.md)，第5章OCR“Giacinto GigE”与书内索引全名相对照，第6章注释再次出现Gigli；OCR读法及日记未独立查阅的状态均保留。

三组各新增一个person KU和一条候选映射；3条直接S2关系候选均待S6。本次不新增正式关系或外部身份核验状态。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-julian-wals-gigli-20261017"></a>

### S4 person：三组跨章人物关系端点（{DATE}）

- `cand-1336`（`{ITEMS[0]['group']}`）依据第4章p.109全名及第7章p.196对Verrio题材的再次提及登记为[Julian the Apostate](../../../04-knowledge/units/persons/julian-the-apostate.md)。关系候选`st-chp4-sec-ii-p109-petau-preface-argument`是Haskell对Petau序言的摘要，不视作已独立核对Petau原文。
- `cand-2800`（`{ITEMS[1]['group']}`）依据第5章p.125全名及第8章p.206收藏名单异写登记为[Goffredo Wals](../../../04-knowledge/units/persons/goffredo-wals.md)。`Goffredo`与`Gioffredo`两种原书OCR形式均保留；`st-chp5-p125-claude-studied-under-wals`中的`is supposed to have`限定不转写为确定师承。
- `cand-1168`（`{ITEMS[2]['group']}`）依据第5章p.131叙述和书内索引G.csv L77登记为[Giacinto Gigli](../../../04-knowledge/units/persons/giacinto-gigli.md)。正文OCR作“Giacinto GigE”，书内索引列作“Gigli, Giacinto”；第6章注4再次引用Gigli。正文所述日记版本未独立查阅，OCR中“diEgently”与印本“diligently”的校读保留在证据摘要中。
- 三组各新增一个person KU与一条候选映射；3条直接S2关系候选仍待S6，本次不新增正式关系或外部身份核验状态。

The three groups follow the cross-chapter names and spellings recorded in the book. The Petau passage remains a mediated summary, the Wals apprenticeship remains qualified as reported, and the Gigli OCR form is compared with the book index. All three relation candidates remain pending S6; no formal relation or external identity verification was added.

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
