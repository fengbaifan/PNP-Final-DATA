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
        "candidate": "cand-0609",
        "group": "new-person:catherine-great-of-russia-85ee1f0320",
        "ku_id": "units/persons/catherine-the-great-russia",
        "card_rel": "04-knowledge/units/persons/catherine-the-great-russia.md",
        "canonical_name": "叶卡捷琳娜二世（Catherine the Great）",
        "name_en": "Catherine the Great",
        "anchor": "s4-person-catherine-great-russia-20261017",
        "description_cn": "第10章以Catherine购买《埃及艳后宴会》说明她对威尼斯艺术的欣赏；第20章后记则称作者此前关于她本人购买该画的假定现在看来过于自信。本卡记录书内人物身份和作者跨章判断变化，不将购买行为写作已确认事实。",
        "description_en": "Chapter 10 cites Catherine's purchase of Tiepolo's *Banquet of Cleopatra* as evidence of her admiration for Venetian art. The chapter 20 postscript says the author's earlier assumption that Catherine herself bought the painting now seems over-confident. This entry records the person and the change in the author's assessment without presenting the purchase as established fact.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "lines": [349],
                "location": "第10章，印刷页298；OCR L349",
                "span": "line 349; print p. 298",
                "quote": "Catherine’s admiration for Venetian art is testified not so much by the rather minor artists and their works that she was able to attract to her distant court as by her purchase of Tiepolo’s Banquet of Cleopatra.",
                "summary": "哈斯克尔以Catherine购买《埃及艳后宴会》说明她对威尼斯艺术的欣赏；这一购买说法在第20章后记中被重新限定。",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "lines": [157, 158],
                "location": "第20章后记，印刷页406；OCR L157–158",
                "span": "lines 157–158; print p. 406",
                "quote": "My assumption that Catherine the Great herself purchased one of the great masterpieces of the century, Tiepolo’s Banquet of Cleopatra (Plate 61b), now seems to me over-confident.",
                "summary": "哈斯克尔在后记中称自己此前关于Catherine本人购买《埃及艳后宴会》的假定现在看来过于自信；这是对先前把握程度的回撤，并非否定购买。",
            },
        ),
        "statement_ids": (
            "st-chp10-p298-catherine-tiepolo-purchase",
            "st-chp20-p406-catherine-tiepolo-purchase-reassessment",
        ),
    },
    {
        "candidate": "cand-1679",
        "group": "new-person:antonio-molinari-5e2b48c6a7",
        "ku_id": "units/persons/antonio-molinari",
        "card_rel": "04-knowledge/units/persons/antonio-molinari.md",
        "canonical_name": "安东尼奥·莫利纳里（Antonio Molinari）",
        "name_en": "Antonio Molinari",
        "anchor": "s4-person-antonio-molinari-20261017",
        "description_cn": "第5章第129页以全名Antonio Molinari记述其作品、相对死亡时间及其在罗马收藏家中的传播评价；该章OCR将原文读作“sit”，印本读作“fit”，两种读法及校正关系均保留。第10章第294页再次以Molinari提及。本卡只登记书内人物身份和语境，不将相对死亡时间换算为具体年份。",
        "description_en": "Chapter 5, page 129, names Antonio Molinari and discusses his pictures, a source-relative statement about his death, and his reception among Roman collectors. The OCR reads “sit” where the printed text reads “fit”; both readings and the correction are retained. Chapter 10, page 294, refers to Molinari again. This entry records the identity and contexts in the book without converting the relative death statement into a calendar year.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "lines": [101],
                "location": "第5章，印刷页129；OCR L101",
                "span": "line 101; print p. 129",
                "quote": "in 1707 Cardinal Grimani, in a sit of patriotic enthusiasm, sent in 23 ‘historié di maniera veneziana’ by Antonio Molinari who, although he had died 25 years earlier, was still quite unknown to Roman collectors.",
                "summary": "哈斯克尔称Grimani枢机于1707年送展23幅Antonio Molinari的威尼斯风格历史画，并说画家此前25年已去世、当时仍不为罗马收藏家熟知。该行OCR作“sit”，印本作“fit”；未据此推算具体去世年份。",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "lines": [298],
                "location": "第10章，印刷页294；OCR L298（页标见L292）",
                "span": "line 298; print p. 294",
                "quote": "and others by Molinari and Bellucci.",
                "summary": "哈斯克尔在第10章另称奥古斯都二世购入Molinari与Bellucci的作品；此处姓氏提及与第5章全名所指人物归入同一S3组。",
            },
        ),
        "statement_ids": (
            "st-chp5-p129-molinari-authorship",
            "st-chp5-p129-molinari-reception",
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
        card = precedent.card_text(item)
        cards.append((item, card, card_path))

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_append = f"""

### S4 person：跨章人物关系端点——Catherine the Great 与 Antonio Molinari（{DATE}）

`cand-0609`（`{ITEMS[0]['group']}`）登记为[叶卡捷琳娜二世](../units/persons/catherine-the-great-russia.md)。第10章p.298将购买《埃及艳后宴会》作为其欣赏威尼斯艺术的证据；第20章p.406后记称作者此前关于她本人购买该画的假定过于自信。卡片保留这一跨章判断变化，不将购买行为写作已确认事实。`cand-1679`（`{ITEMS[1]['group']}`）登记为[Antonio Molinari](../units/persons/antonio-molinari.md)，依据第5章p.129全名及第10章p.294姓氏提及。p.129 OCR读作“sit”，印本校读为“fit”；保留该校正，且不把“25 years earlier”换算为具体年份。

两组各新增一个person KU和一条候选映射；Catherine的2条、Molinari的2条直接S2关系候选均待S6。本次不新增正式关系或外部身份核验状态。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-catherine-molinari-20261017"></a>

### S4 person：跨章人物关系端点（{DATE}）

- `cand-0609`（`{ITEMS[0]['group']}`）按S3跨章身份组登记为[叶卡捷琳娜二世](../../../04-knowledge/units/persons/catherine-the-great-russia.md)。第10章p.298称其购买《埃及艳后宴会》；第20章p.406后记明确将作者此前关于她本人购买该画的假定改为“now seems to me over-confident”。这是作者对先前判断把握程度的回撤，并非否认购买。`st-chp10-p298-catherine-tiepolo-purchase`与`st-chp20-p406-catherine-tiepolo-purchase-reassessment`均留待S6，卡片未写成确定的购买关系。
- `cand-1679`（`{ITEMS[1]['group']}`）依据第5章p.129“Antonio Molinari”全名及第10章p.294“Molinari”姓氏提及登记为[Antonio Molinari](../../../04-knowledge/units/persons/antonio-molinari.md)。第5章原OCR行读作“sit of patriotic enthusiasm”，印本校读为“fit”；卡片与来源摘要保留此读法差异。来源仅称他在1707年叙述时“had died 25 years earlier”，未据此算出具体去世年份。`st-chp5-p129-molinari-authorship`与`st-chp5-p129-molinari-reception`仍为S2关系候选，待S6逐条裁决。
- 两组各新增一个person KU与一条候选映射；4条直接S2关系候选继续待S6。本次仅做S4登记，不增加外部身份核验或正式关系。

The Catherine group is registered with both the chapter 10 purchase statement and the chapter 20 retrospective qualification visible; the latter limits the author's confidence and does not negate the earlier statement. The Molinari group follows the full name in chapter 5 and surname reference in chapter 10. The OCR/print correction “sit”/“fit” and the source-relative death interval are preserved. All four direct relation candidates remain pending S6; no external identity verification or formal relation was added.

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
        print("verified_direct_relation_candidates=4; no external verification status or S6 formal relation rows will be written; no files changed")
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
