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
        "candidate": "cand-2361",
        "group": "new-person:andrea-del-sarto-914ca633fc",
        "ku_id": "units/persons/andrea-del-sarto",
        "card_rel": "04-knowledge/units/persons/andrea-del-sarto.md",
        "canonical_name": "安德烈亚·德尔·萨托（Andrea del Sarto）",
        "name_en": "Andrea del Sarto",
        "anchor": "s4-person-andrea-del-sarto-20261017",
        "description_cn": "第2章将Andrea del Sarto列入Cardinal Barberini宫中旧大师绘画的举例；第9章又称Manin宫画廊藏有其绘画。第2章为集合层级描述，没有指明具体作品、数量或年代。本卡仅登记人物身份及书内语境。",
        "description_en": "Chapter 2 includes Andrea del Sarto among the old masters whose paintings were represented in Cardinal Barberini's palace; chapter 9 also says that pictures by him were in the Manin palace gallery. The chapter 2 passage describes an aggregate and identifies no individual work, count, or date. This entry records the person and the contexts in the book.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "lines": [113, 114],
                "location": "第2章，印刷页30；OCR L113–114",
                "span": "lines 113–114; print p. 30",
                "quote": "paintings—by old masters such as Raphael, Correggio, Andrea del Sarto, Giulio Romano, Parmigianino and others",
                "summary": "哈斯克尔将Andrea del Sarto列为Cardinal Barberini宫中旧大师绘画的举例；此集合性表述没有列出具体作品。",
            },
            {
                "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "lines": [108, 109],
                "location": "第9章，印刷页251；OCR L108–109",
                "span": "lines 108–109; print p. 251",
                "quote": "In the gallery were bronzes by Giambologna and Sansovino and pictures by Giovanni da Udine and Andrea del Sarto.",
                "summary": "哈斯克尔称Manin家族大运河宫殿画廊中有Andrea del Sarto的绘画。",
            },
        ),
        "statement_ids": (
            "st-chp2-seci-l108-119-palace-paintings-by-andrea-del-sarto",
        ),
    },
    {
        "candidate": "cand-4876",
        "group": "new-person:da-giovanni-giovanni-san-a3958ee8ea",
        "ku_id": "units/persons/giovanni-da-san-giovanni",
        "card_rel": "04-knowledge/units/persons/giovanni-da-san-giovanni.md",
        "canonical_name": "乔瓦尼·达·圣乔瓦尼（Giovanni da San Giovanni）",
        "name_en": "Giovanni da San Giovanni",
        "anchor": "s4-person-giovanni-da-san-giovanni-20261017",
        "description_cn": "第2章注释转述Baldinucci关于Giovanni da San Giovanni创作《夜之战车》、与两名法国人冲突及Bentivoglio赞助其在罗马发展的叙述；第4章又将他列入Giordano II Orsini周围的艺术家与音乐家。轶事保留为哈斯克尔转述的来源链，不作为独立核实的事实。",
        "description_en": "A chapter 2 footnote relays Baldinucci's story that Giovanni da San Giovanni worked on the *Carro della Notte*, fought two Frenchmen, and owed his success in Rome to Bentivoglio's patronage. Chapter 4 also lists him among the artists and musicians around Giordano II Orsini. The anecdote remains attributed to Haskell's reported source chain and is not presented as independently verified.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "lines": [218, 219],
                "location": "第2章，印刷页49，注6续；OCR L218–219",
                "span": "lines 218–219; print p. 49, note 6 continuation",
                "quote": "Baldinucci (VI, 1728, pp. 25-7) has a long story of Giovanni da San Giovanni working on a Carro della Notte",
                "summary": "哈斯克尔注释转述Baldinucci关于Giovanni da San Giovanni与《夜之战车》及两名法国人的轶事；相关叙述保留为转引链。",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
                "lines": [13, 14, 15],
                "location": "第4章，印刷页95页标后；OCR L13–15",
                "span": "lines 13–15; print page marker at line 6 reads p. 95",
                "quote": "around which there gravitated a dazzling group of artists and musicians, including Giulio Parigi, Jacques Callot, Giovanni da San Giovanni, Filippo Napoletano and Gerolamo Frescobaldi.",
                "summary": "哈斯克尔将Giovanni da San Giovanni列入围绕Giordano II Orsini的艺术家与音乐家群体。",
            },
        ),
        "statement_ids": (
            "st-chp2-seciv-l190-245-baldinucci-anecdote",
        ),
    },
    {
        "candidate": "cand-1446",
        "group": "new-person:louis-xiii-56b02fc735",
        "ku_id": "units/persons/louis-xiii",
        "card_rel": "04-knowledge/units/persons/louis-xiii.md",
        "canonical_name": "路易十三世（Louis XIII）",
        "name_en": "Louis XIII",
        "anchor": "s4-person-louis-xiii-20261017",
        "description_cn": "第2章称Louis XIII在1625年遣人代表团离开巴黎前送来一份礼物；相邻句提到他们房间墙上已挂有七幅挂毯，但原文没有在同一分句中明确将两者等同。第7章又称Louis XIII于1643年去世。本卡保留这一语境，不扩大礼物对象的认定。",
        "description_en": "Chapter 2 says Louis XIII sent a gift shortly before the Barberini party left Paris in 1625. The adjacent sentence mentions seven tapestries already hanging in their apartments, but the source does not explicitly equate the gift with those tapestries in one clause. Chapter 7 also says Louis XIII was dead by 1643. This entry preserves that context without expanding the identification of the gift.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "lines": [8, 9, 10],
                "location": "第2章，印刷页44；OCR L8–10",
                "span": "lines 8–10; print p. 44",
                "quote": "shortly before their departure they found, on returning to their apartments, a splendid gift sent by Louis XIII to sweeten their disappointment. Already hanging on the walls were seven great tapestries depicting scenes from The Lise of Constantine woven from cartoons by Rubens.",
                "summary": "哈斯克尔称Barberini一行离开巴黎前收到Louis XIII赠送的礼物；相邻句称房间中已挂有七幅《君士坦丁生平》挂毯，但未在同一句中明言礼物与这七幅挂毯相同。",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "lines": [143],
                "location": "第7章，印刷页181；OCR L143",
                "span": "line 143; print p. 181",
                "quote": "By the middle of 1643 both Richelieu and Louis XIII were dead",
                "summary": "哈斯克尔称截至1643年年中，Richelieu与Louis XIII均已去世。",
            },
        ),
        "statement_ids": (
            "st-chp2-seciv-l6-17-louis-xiii-tapestry-gift",
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
        card = precedent.card_text(item)
        cards.append((item, card, card_path))

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_append = f"""

### S4 person：跨章关系端点——Andrea del Sarto、Giovanni da San Giovanni 与 Louis XIII（{DATE}）

`cand-2361`登记为[Andrea del Sarto](../units/persons/andrea-del-sarto.md)，依据第2章p.30与第9章p.251的跨章具名提及；第2章只将其列入宫殿绘画群组的举例，具体作品未定。`cand-4876`登记为[Giovanni da San Giovanni](../units/persons/giovanni-da-san-giovanni.md)，第2章注释转述Baldinucci轶事，第4章将其列入Orsini周围的艺术家圈。`cand-1446`登记为[Louis XIII](../units/persons/louis-xiii.md)；第2章将赠礼与已悬挂的七幅挂毯连续叙述，但未明言二者相同，第7章记其于1643年年中已去世。

三组各新增一个person KU和一条候选映射；3条直接S2关系候选全部保留待S6。本次不将原书集合性、转述性或相邻句推断升级为正式边。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-clear-crosschapter-endpoints-20261017"></a>

### S4 person：四组跨章人物关系端点（{DATE}）

- `cand-2361`（`{ITEMS[0]['group']}`）依据第2章p.30和第9章p.251的同一全名提及登记为[Andrea del Sarto](../../../04-knowledge/units/persons/andrea-del-sarto.md)。第2章只把他列在Cardinal Barberini宫中旧大师绘画群组的举例中；关系候选`st-chp2-seci-l108-119-palace-paintings-by-andrea-del-sarto`限定为群组层级，不能解释为该组每幅画皆由他创作。
- `cand-4876`（`{ITEMS[1]['group']}`）依据第2章注释中的全名及第4章重复全名登记为[Giovanni da San Giovanni](../../../04-knowledge/units/persons/giovanni-da-san-giovanni.md)。第2章相关叙述经Haskell转述Baldinucci；直接候选`st-chp2-seciv-l190-245-baldinucci-anecdote`不表示原始轶事已独立核实。
- `cand-1446`（`{ITEMS[2]['group']}`）依据第2、7章重复全名登记为[Louis XIII](../../../04-knowledge/units/persons/louis-xiii.md)。第2章把礼物与房间中已有的挂毯相邻叙述，原文未在同一分句明确等同；关系候选`st-chp2-seciv-l6-17-louis-xiii-tapestry-gift`保留此来源限定。
- 三组各新增一个person KU与一条候选映射；3条关系候选仍待S6。本次不新增正式关系或外部身份核验状态。

The three groups follow repeated full names across chapters. The Barberini palace attribution remains aggregate, the Giovanni anecdote remains mediated through Baldinucci, and the identification of Louis XIII's gift with the adjacent tapestries remains unresolved. All three relation candidates remain pending S6; no formal relations or external verification statuses were added.

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
