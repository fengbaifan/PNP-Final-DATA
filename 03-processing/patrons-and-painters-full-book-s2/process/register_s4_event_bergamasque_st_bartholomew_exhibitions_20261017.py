from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATES = ("cand-11728",)
GROUP = "sg3-event-cand-11728"
KU_ID = "units/events/bergamasque-community-st-bartholomew-exhibitions-rome"
CARD_REL = "04-knowledge/units/events/bergamasque-community-st-bartholomew-exhibitions-rome.md"
CH5 = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp5-p125-bergamasque-devotional-purpose",
    "st-chp5-p125-bergamasque-exhibition-practice",
    "st-chp5-p125-bergamasque-venue-funding",
    "st-chp5-p125-bergamasque-exhibition-celebrated-saint",
    "st-chp5-p125-guardiano-paid-bergamasque-exhibitions",
    "st-chp5-p125-bergamasque-exhibitions-honoured-devotees",
    "st-chp5-p125-all-isola-exhibitions-less-important",
}
ENDPOINTS = {
    "cand-6027": ("institution", "new", "sg3-institution-cand-6027"),
    "cand-11729": ("place", "new", "sg3-place-cand-11729"),
    "cand-6028": ("person", "undecided", None),
    "cand-11730": ("person", "undecided", None),
    "cand-11734": ("term", "undecided", "sg3-term-cand-11734"),
    "cand-11736": ("event", "new", "sg3-event-cand-11736"),
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第5章；印刷页125；OCR L56–57",
            "sentence_summary": (
                "Haskell称罗马贝加莫社群有时在8月24日举办较有组织的圣巴托洛梅奥瞻礼画展，地点为 S. Bartolomeo 教堂庭院，"
                "费用由 Guardiano 支付，展览敬奉圣人及其信众。起始年份不确定；Haskell称其至迟在1650年已兴盛。"
                "另称 S. Bartolomeo all’Isola 的瞻礼画展较不重要；该系列与本卡事件系列分开。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 56",
                    "text": (
                        "More organised exhibitions were sometimes held on 24 August by the Bergamasque community in Rome "
                        "to celebrate the feast day of their patron saint, St Bartholomew."
                    ),
                },
                {
                    "source_span": "line 57",
                    "text": (
                        "These took place in the courtyard of the church of S. Bartolomeo and were paid for by the Guardiano. "
                        "As in all Roman exhibitions of this kind, the occasion served primarily to put on a spectacular decorative show "
                        "in honour of the saint and his devotees. The façade of the church was hung with tapestries, as were the houses "
                        "round about, and an observer confessed that it was hard to decide which was the more impressive: the general-effect "
                        "created by the hangings outside or the pictures spread round the inner courtyard. It is not certain when the exhibitions "
                        "began, but they were certainly flourishing by 1650. S. Bartolomeo all’Isola arranged exhibitions for the saint’s name day, "
                        "but they were less important."
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH5,
                "source_span": "lines 56–57; print p. 125",
            },
        }
    ]
    frontmatter = {
        "title": (
            "罗马贝加莫社群圣巴托洛梅奥瞻礼画展系列"
            "（Bergamasque Community's St Bartholomew Feast Day Exhibitions in Rome）"
        ),
        "name_en": "Bergamasque Community's St Bartholomew Feast Day Exhibitions in Rome",
        "type": "event",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source = f"[第5章 p.125](../../../{CH5})（L56–57）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记 Haskell 所述罗马贝加莫社群的瞻礼画展系列：有时在每年8月24日圣巴托洛梅奥瞻礼举办较有组织的展览，地点为 S. Bartolomeo 教堂庭院，由 Guardiano 支付费用。Haskell称展览敬奉圣人及其信众，教堂立面和周边住宅悬挂挂毯，画作陈列于庭院；起始年份不详，至迟在1650年已兴盛。此卡的中英文题名为描述性名称，不是原书给出的正式系列标题。{source}

**English:** This card records the exhibition series Haskell describes for the Bergamasque community in Rome. More organised exhibitions were sometimes held on the feast day of St Bartholomew, 24 August, in the courtyard of S. Bartolomeo and paid for by the Guardiano. Haskell says the event honoured the saint and his devotees, with tapestries hung on the church façade and nearby houses and pictures displayed in the courtyard. The start date is unknown; Haskell says the exhibitions were flourishing by 1650. The bilingual card title is descriptive and is not presented as a formal title from the book. {source}

### 身份边界

S3 身份组 `{GROUP}` 仅含 `cand-11728`，指向一组周期性瞻礼画展，不对应单一年度场次；不得补定起始年份。Haskell另提及 S. Bartolomeo all’Isola 举办的圣人瞻礼展览（`cand-11736`，S3 `new`），本卡与该事件组分开。教堂地点、贝加莫社群、未具名 Guardiano、圣巴托洛梅奥和信众均按各自候选的当前 S3 状态保留，不在本轮合并入本事件卡。

S3 group `{GROUP}` contains only `cand-11728` and denotes a recurring feast-day exhibition series, not a single annual occurrence; no start year is inferred. Haskell separately mentions the saint's name-day exhibitions arranged by S. Bartolomeo all'Isola (`cand-11736`, S3 `new`); this event group remains distinct. The church, Bergamasque community, unnamed Guardiano, St Bartholomew, and devotees retain their own current S3 candidate states and are not merged into this event card.

## 关系与证据

7条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。其中社群 `cand-6027`、教堂地点 `cand-11729` 和另一瞻礼展系列 `cand-11736` 为各自独立的 S3 `new` 候选、仍待 S4；圣人 `cand-6028`、未具名 Guardiano `cand-11730` 与信众 `cand-11734` 仍为 S3 `undecided`。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Bergamasque St Bartholomew exhibition-series event identity in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert not (ROOT / CARD_REL).exists()
    assert CARD_REL not in accepted
    assert not any(
        row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL
        or (row.get("type") == "event" and (row.get("name_en") or "").casefold() == "bergamasque community's st bartholomew feast day exhibitions in rome")
        for row in manifest
    ), "Bergamasque exhibition-series event KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["canonical_name"] == "Bergamasque community's recurring St Bartholomew exhibitions in Rome (p.125)"
    assert candidate["suggested_type"] == "event"
    assert candidate["candidate_source_ref"] == "chp-5:05_CHP-5_sec_i:l51-58#L56"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    for cid, (expected_type, expected_decision, expected_group) in ENDPOINTS.items():
        endpoint = candidate_by_id[cid]
        endpoint_alignment = alignment_by_id[cid]
        assert endpoint.get("suggested_type") == expected_type
        assert endpoint_alignment.get("decision") == expected_decision
        if expected_group:
            assert sync.get_group(endpoint_alignment.get("resolution_note", "")) == expected_group

    source_text = (ROOT / CH5).read_text(encoding="utf-8-sig")
    assert "More organised exhibitions were sometimes held on 24 August" in source_text
    assert "by the Bergamasque community in Rome" in source_text
    assert "courtyard of the church of S. Bartolomeo and were paid for by the Guardiano" in source_text
    assert "not certain when the exhibitions began" in source_text and "flourishing by 1650" in source_text
    assert "S. Bartolomeo all’Isola arranged exhibitions for the saint’s name day" in source_text

    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == RELATION_CANDIDATES, direct_relations

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATES[0] and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "event",
        "canonical_name": "罗马贝加莫社群圣巴托洛梅奥瞻礼画展系列",
        "name_en": "Bergamasque Community's St Bartholomew Feast Day Exhibitions in Rome",
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-bergamasque-st-bartholomew-exhibitions-event\"></a>\n\n"
        "### S4 event：罗马贝加莫社群圣巴托洛梅奥瞻礼画展系列登记（2026-10-17）\n\n"
        f"`cand-11728`（第5章 p.125，L56–57）沿用 S3 事件组 `{GROUP}`，映射至[事件卡]"
        f"(../../../{CARD_REL})。卡片保留 8月24日、地点、资助者、纪念对象及“起始年份不确定、至迟1650年已兴盛”的原文范围。"
        "`cand-11736`（S. Bartolomeo all’Isola 瞻礼展系列）为不同 S3 new 事件组，不合并。\n\n"
        "7条直接 relation_candidate 保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。端点去向："
        "`cand-6027` institution new、`cand-11729` place new、`cand-11736` event new 均待 S4；"
        "`cand-6028`、`cand-11730`、`cand-11734` 保持 S3 undecided。本轮未新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 event：罗马贝加莫社群圣巴托洛梅奥瞻礼画展系列登记（2026-10-17）\n\n"
        f"`cand-11728` 映射至[事件卡](../units/events/bergamasque-community-st-bartholomew-exhibitions-rome.md)。"
        "登记的是周期性系列，起始年份未知、至迟1650年已兴盛；S. Bartolomeo all’Isola 瞻礼展系列保持独立。"
        "7条关系候选留待 S6，未登记正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 Bergamasque exhibition event dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"identity_group={GROUP}; candidates={len(group_rows)}; direct_relation_candidates={len(direct_relations)}")
        print("distinct_event=cand-11736 (S3 new); remaining endpoints=cand-6027,cand-11729,cand-6028,cand-11730,cand-11734")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / CARD_REL).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATES[0]} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
