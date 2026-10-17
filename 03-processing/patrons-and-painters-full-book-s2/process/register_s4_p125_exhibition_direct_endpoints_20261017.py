from __future__ import annotations

import argparse
import re
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
CH5 = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

TARGETS = [
    {
        "candidate": "cand-6027",
        "group": "sg3-institution-cand-6027",
        "ku": "units/institutions/bergamasque-community-rome",
        "card": "04-knowledge/units/institutions/bergamasque-community-rome.md",
        "type": "institution",
        "name_zh": "罗马贝加莫社群",
        "name_en": "Bergamasque community in Rome",
        "relations": {"st-chp5-p125-bergamasque-exhibition-practice"},
    },
    {
        "candidate": "cand-11729",
        "group": "sg3-place-cand-11729",
        "ku": "units/places/church-s-bartolomeo-bergamasque-exhibition-courtyard",
        "card": "04-knowledge/units/places/church-s-bartolomeo-bergamasque-exhibition-courtyard.md",
        "type": "place",
        "name_zh": "罗马 S. Bartolomeo 教堂及贝加莫社群画展庭院",
        "name_en": "Church of S. Bartolomeo and Bergamasque Exhibition Courtyard, Rome",
        "relations": {
            "st-chp5-p125-bergamasque-venue-funding",
            "st-chp5-p125-tapestries-hung-on-church-facade",
            "st-chp5-p125-pictures-displayed-in-courtyard",
        },
    },
    {
        "candidate": "cand-11735",
        "group": "sg3-place-cand-11735",
        "ku": "units/places/s-bartolomeo-all-isola-exhibition-site",
        "card": "04-knowledge/units/places/s-bartolomeo-all-isola-exhibition-site.md",
        "type": "place",
        "name_zh": "S. Bartolomeo all’Isola 展览地点",
        "name_en": "S. Bartolomeo all'Isola site in the exhibition account",
        "relations": {"st-chp5-p125-bartolomeo-all-isola-exhibitions"},
    },
    {
        "candidate": "cand-11736",
        "group": "sg3-event-cand-11736",
        "ku": "units/events/s-bartolomeo-all-isola-name-day-exhibitions",
        "card": "04-knowledge/units/events/s-bartolomeo-all-isola-name-day-exhibitions.md",
        "type": "event",
        "name_zh": "S. Bartolomeo all’Isola 圣人瞻礼画展系列",
        "name_en": "S. Bartolomeo all'Isola Name-Day Exhibitions",
        "relations": {
            "st-chp5-p125-artists-display-opportunity",
            "st-chp5-p125-bartolomeo-all-isola-exhibitions",
            "st-chp5-p126-fair-comparison-closed",
            "st-chp5-p125-all-isola-exhibitions-less-important",
        },
    },
    {
        "candidate": "cand-11741",
        "group": "sg3-term-cand-11741",
        "ku": "units/terms/casual-saints-day-fairs",
        "card": "04-knowledge/units/terms/casual-saints-day-fairs.md",
        "type": "term",
        "name_zh": "圣人瞻礼日集市",
        "name_en": "Casual Saints' Day Fairs",
        "relations": {"st-chp5-p126-fair-comparison-closed"},
    },
]

ENDPOINT_DECISIONS = {
    "cand-6028": "undecided",
    "cand-11730": "undecided",
    "cand-11734": "undecided",
    "cand-11740": "undecided",
}


def shared_source(location: str, spans: list[tuple[str, str]], summary: str) -> list[dict]:
    return [
        {
            "citation": BOOK_CITATION,
            "location": location,
            "sentence_summary": summary,
            "original_quotes": [
                {"source_span": span, "text": quote} for span, quote in spans
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH5,
                "source_span": "; ".join(spans and [span for span, _ in spans]),
            },
        }
    ]


def make_card(target: dict) -> str:
    cid = target["candidate"]
    if cid == "cand-6027":
        location = "第5章；印刷页125；OCR L56–57"
        summary = (
            "Haskell称罗马贝加莫社群有时在8月24日举办较有组织的圣巴托洛梅奥瞻礼画展，由 Guardiano 支付费用。"
            "原文称社群在罗马，未说明其正式组织性质、创立时间或成员范围。"
        )
        spans = [
            ("line 56", "More organised exhibitions were sometimes held on 24 August by the Bergamasque community in Rome to celebrate the feast day of their patron saint, St Bartholomew."),
            ("line 57", "These took place in the courtyard of the church of S. Bartolomeo and were paid for by the Guardiano."),
        ]
        title = "罗马贝加莫社群（Bergamasque community in Rome）"
        desc_zh = (
            "Haskell 在第5章称罗马有一个 Bergamasque community，并记其有时举办圣巴托洛梅奥瞻礼画展。"
            "本卡只登记该段所指的社群；原文没有说明其法律地位、成立时间或完整成员范围，因此不补写正式组织沿革。"
        )
        desc_en = (
            "Chapter 5 names a Bergamasque community in Rome and says it sometimes held exhibitions for St Bartholomew's feast day. "
            "This card records only the community referred to in that passage. The text does not specify its legal status, founding date, "
            "or full membership, so no formal organizational history is inferred."
        )
        boundary = (
            "社群 `cand-6027` 与其展览系列 `cand-11728`、场地 `cand-11729` 分立；不将社群等同于教堂建筑或整个 Bergamo 城市。",
            "Community candidate `cand-6027` is distinct from its exhibition series `cand-11728` and venue `cand-11729`; it is not the church building or the city of Bergamo.",
        )
        rel_note = (
            "1条直接 S2 `relation_candidate` 保留待 S6：`st-chp5-p125-bergamasque-exhibition-practice`。"
            "候选事件 KU 已建；本轮未登记正式关系。",
            "One direct S2 `relation_candidate` remains for S6: `st-chp5-p125-bergamasque-exhibition-practice`. The event KU is registered; no formal relation was added.",
        )
    elif cid == "cand-11729":
        location = "第5章；印刷页125；OCR L56–57"
        summary = (
            "Haskell 将罗马贝加莫社群的展览定位于 S. Bartolomeo 教堂庭院，并称教堂立面和周围住宅悬挂挂毯、"
            "画作陈列于内庭。原文未给出可用于进一步识别的街址或馆藏号。"
        )
        spans = [
            ("line 56", "More organised exhibitions were sometimes held on 24 August by the Bergamasque community in Rome"),
            ("line 57", "These took place in the courtyard of the church of S. Bartolomeo"),
            ("line 57", "The façade of the church was hung with tapestries, as were the houses round about, and an observer confessed that it was hard to decide which was the more impressive: the general-effect created by the hangings outside or the pictures spread round the inner courtyard."),
        ]
        title = "罗马 S. Bartolomeo 教堂及贝加莫社群画展庭院（Church of S. Bartolomeo and Bergamasque Exhibition Courtyard, Rome）"
        desc_zh = (
            "Haskell 将罗马贝加莫社群的展览场地写作 S. Bartolomeo 教堂庭院，并记教堂立面和周边住宅悬挂挂毯、画作陈列于内庭。"
            "卡片名称依本段作描述性表述；原书未提供更精确地址或建筑识别依据。"
        )
        desc_en = (
            "Haskell locates the Bergamasque community's exhibitions in the courtyard of the church of S. Bartolomeo in Rome. "
            "He describes tapestries on the façade and nearby houses, with pictures displayed in the inner courtyard. The card uses a "
            "descriptive name based on this passage; no more precise address or architectural identification is supplied."
        )
        boundary = (
            "地点候选 `cand-11729` 与贝加莫社群 `cand-6027` 分立；S3 明确要求与 `S. Bartolomeo all'Isola` 地点候选 `cand-11735` 保持区分。",
            "Place candidate `cand-11729` is distinct from the Bergamasque community `cand-6027`; S3 keeps it separate from the S. Bartolomeo all'Isola site candidate `cand-11735`.",
        )
        rel_note = (
            "3条直接 S2 `relation_candidate` 保留待 S6：`st-chp5-p125-bergamasque-venue-funding`、"
            "`st-chp5-p125-tapestries-hung-on-church-facade`、`st-chp5-p125-pictures-displayed-in-courtyard`。"
            "作品端点仍待证；本轮未登记正式关系。",
            "Three direct S2 `relation_candidate` records remain for S6: `st-chp5-p125-bergamasque-venue-funding`, "
            "`st-chp5-p125-tapestries-hung-on-church-facade`, and `st-chp5-p125-pictures-displayed-in-courtyard`. "
            "The work endpoints remain unresolved; no formal relation was added.",
        )
    elif cid == "cand-11735":
        location = "第5章；印刷页125；OCR L57"
        summary = (
            "Haskell 以 S. Bartolomeo all’Isola 指称举办圣人瞻礼展览的地点，并将该系列与贝加莫社群展览作比较。"
            "段落未判定该名称在此具体指建筑、教会组织还是周边地点。"
        )
        spans = [
            ("line 57", "S. Bartolomeo all’Isola arranged exhibitions for the saint’s name day, but they were less important."),
        ]
        title = "S. Bartolomeo all’Isola 展览地点（S. Bartolomeo all'Isola Site in the Exhibition Account）"
        desc_zh = (
            "Haskell 在第5章以 S. Bartolomeo all’Isola 指称举办圣人瞻礼展览的地点。本卡保留原文地名形式，"
            "不据该句判定所指是具体教堂建筑、教会组织还是周边地点。"
        )
        desc_en = (
            "Chapter 5 uses the name S. Bartolomeo all'Isola for the site associated with the saint's name-day exhibitions. "
            "This card preserves the source form and does not decide whether the phrase denotes a particular church building, "
            "an organization, or the surrounding site."
        )
        boundary = (
            "S3 place 候选 `cand-11735` 与举办贝加莫社群展览的 S. Bartolomeo 教堂庭院 `cand-11729` 分开；它关联的瞻礼展系列为 `cand-11736`。",
            "S3 place candidate `cand-11735` remains separate from the S. Bartolomeo courtyard venue for the Bergamasque exhibitions (`cand-11729`); its name-day exhibition series is `cand-11736`.",
        )
        rel_note = (
            "1条直接 S2 `relation_candidate` 保留待 S6：`st-chp5-p125-bartolomeo-all-isola-exhibitions`。"
            "关联事件 KU 已建；本轮未登记正式关系。",
            "One direct S2 `relation_candidate` remains for S6: `st-chp5-p125-bartolomeo-all-isola-exhibitions`. The associated event KU is registered; no formal relation was added.",
        )
    elif cid == "cand-11736":
        location = "第5章；印刷页125–126；OCR L57、61"
        summary = (
            "Haskell 称 S. Bartolomeo all’Isola 为圣人瞻礼举办展览，并认为其重要性低于贝加莫社群展览；"
            "第126页续称此类场次较圣人节集市更为庄重。原文未给出具体日期、起始年份或单次场次。"
        )
        spans = [
            ("line 57", "S. Bartolomeo all’Isola arranged exhibitions for the saint’s name day, but they were less important."),
            ("line 57", "Despite their devotional purpose the exhibitions certainly provided artists with the opportunity to display their works and were far more dignified"),
            ("line 61", "occasions than the casual saints’ day fairs. They attracted the attention of potential buyers, but it seems certain that here, as in all these exhibitions, purchases could not be made on the spot."),
        ]
        title = "S. Bartolomeo all’Isola 圣人瞻礼画展系列（S. Bartolomeo all'Isola Name-Day Exhibitions）"
        desc_zh = (
            "Haskell 称 S. Bartolomeo all’Isola 为圣人瞻礼举办展览，并认为其重要性低于罗马贝加莫社群的展览。"
            "他还将其描述为较圣人节集市更庄重的场次。此卡登记 S3 所判的事件系列；原文未提供该系列的具体日期、起始年份或单次场次。"
        )
        desc_en = (
            "Haskell says that S. Bartolomeo all'Isola arranged exhibitions for the saint's name day and ranks them below the "
            "Bergamasque community's exhibitions. He also describes them as more dignified than casual saints' day fairs. This card "
            "records the event series identified at S3; the passage supplies no specific date, start year, or individual occurrence."
        )
        boundary = (
            "S3 事件组 `sg3-event-cand-11736` 与贝加莫社群的圣巴托洛梅奥展览系列 `cand-11728` 分立。"
            "S. Bartolomeo all’Isola` 地点候选为 `cand-11735`，与另一场地 `cand-11729` 保持分开。",
            "S3 event group `sg3-event-cand-11736` remains distinct from the Bergamasque community's St Bartholomew exhibition series `cand-11728`. "
            "The S. Bartolomeo all'Isola place candidate is `cand-11735`, kept separate from the other venue `cand-11729`."
        )
        rel_note = (
            "4条直接 S2 `relation_candidate` 保留待 S6：`st-chp5-p125-artists-display-opportunity`、"
            "`st-chp5-p125-bartolomeo-all-isola-exhibitions`、`st-chp5-p126-fair-comparison-closed`、"
            "`st-chp5-p125-all-isola-exhibitions-less-important`。艺术家群体 `cand-11740` 仍为 S3 `undecided`；"
            "关联地点、另一事件和术语已有独立 KU 映射。本轮未登记正式关系。",
            "Four direct S2 `relation_candidate` records remain for S6: `st-chp5-p125-artists-display-opportunity`, "
            "`st-chp5-p125-bartolomeo-all-isola-exhibitions`, `st-chp5-p126-fair-comparison-closed`, and "
            "`st-chp5-p125-all-isola-exhibitions-less-important`. The artist-group candidate `cand-11740` remains `undecided` at S3; "
            "the associated site, other event, and term now have separate KU mappings. No formal relation was added."
        )
    else:
        location = "第5章；印刷页126；OCR L61"
        summary = (
            "Haskell 将圣人瞻礼日集市作为比较对象，称 S. Bartolomeo all’Isola 的展览比这类集市更庄重。"
            "此处指一类较随意的展售场合，不是某一场具名集市。"
        )
        spans = [
            ("line 61", "occasions than the casual saints’ day fairs."),
        ]
        title = "圣人瞻礼日集市（Casual Saints' Day Fairs）"
        desc_zh = (
            "Haskell 在第5章以 casual saints’ day fairs 指称较随意的圣人节集市，并将其与 S. Bartolomeo all’Isola 的庄重展览作比较。"
            "本卡记录这一来源用语类别，不指某个确定地点或具体集市事件。"
        )
        desc_en = (
            "Chapter 5 uses the phrase “casual saints' day fairs” for a less formal class of fair occasions and contrasts them with "
            "the more dignified S. Bartolomeo all'Isola exhibitions. This card records the source's category, not a specific venue or event."
        )
        boundary = (
            "此 term 候选 `cand-11741` 表示一类集市场合，不与事件系列 `cand-11736` 合并，也不由比较句推定某一场具体活动。",
            "Term candidate `cand-11741` denotes a class of fair occasions. It is not merged with event series `cand-11736`, and the comparison does not identify a particular occurrence."
        )
        rel_note = (
            "1条直接 S2 `relation_candidate` 保留待 S6：`st-chp5-p126-fair-comparison-closed`。"
            "关联事件 KU 已建；本轮未登记正式关系。",
            "One direct S2 `relation_candidate` remains for S6: `st-chp5-p126-fair-comparison-closed`. The associated event KU is registered; no formal relation was added."
        )

    frontmatter = {
        "title": title,
        "name_en": target["name_en"],
        "type": target["type"],
        "evidence_status": "source_backed",
        "sources": shared_source(location, spans, summary),
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source = f"[第5章 pp.125–126](../../../{CH5})（OCR L56–57、61）"
    boundary_zh, boundary_en = boundary
    rel_zh, rel_en = rel_note
    body = f"""## 内容

### 描述

**中文：** {desc_zh} {source}

**English:** {desc_en} {source}

### 身份边界

{boundary_zh}

{boundary_en}

## 关系与证据

{rel_zh}

{rel_en}
"""
    return f"---\n{fm}---\n\n{body}"


def updated_bergamasque_event_card(path: Path) -> str:
    current = path.read_text(encoding="utf-8-sig")
    old = (
        "7条直接 S2 `relation_candidate` 保留待 S6：st-chp5-p125-all-isola-exhibitions-less-important, "
        "st-chp5-p125-bergamasque-devotional-purpose, st-chp5-p125-bergamasque-exhibition-celebrated-saint, "
        "st-chp5-p125-bergamasque-exhibition-practice, st-chp5-p125-bergamasque-exhibitions-honoured-devotees, "
        "st-chp5-p125-bergamasque-venue-funding, st-chp5-p125-guardiano-paid-bergamasque-exhibitions。"
        "其中社群 `cand-6027`、教堂地点 `cand-11729` 和另一瞻礼展系列 `cand-11736` 为各自独立的 S3 `new` 候选、仍待 S4；"
        "圣人 `cand-6028`、未具名 Guardiano `cand-11730` 与信众 `cand-11734` 仍为 S3 `undecided`。本轮未登记正式关系。"
    )
    new = (
        "7条直接 S2 `relation_candidate` 保留待 S6：st-chp5-p125-all-isola-exhibitions-less-important, "
        "st-chp5-p125-bergamasque-devotional-purpose, st-chp5-p125-bergamasque-exhibition-celebrated-saint, "
        "st-chp5-p125-bergamasque-exhibition-practice, st-chp5-p125-bergamasque-exhibitions-honoured-devotees, "
        "st-chp5-p125-bergamasque-venue-funding, st-chp5-p125-guardiano-paid-bergamasque-exhibitions。"
        "社群、场地及 S. Bartolomeo all’Isola 的另一瞻礼展系列均有各自 S4 KU："
        "[罗马贝加莫社群](../institutions/bergamasque-community-rome.md)（`cand-6027`）、"
        "[S. Bartolomeo 教堂庭院](../places/church-s-bartolomeo-bergamasque-exhibition-courtyard.md)（`cand-11729`）和"
        "[S. Bartolomeo all’Isola 展览系列](s-bartolomeo-all-isola-name-day-exhibitions.md)（`cand-11736`）。"
        "圣人 `cand-6028`、未具名 Guardiano `cand-11730` 与信众 `cand-11734` 仍为 S3 `undecided`。"
        "这些关系候选均待 S6，本轮未登记正式关系。"
    )
    assert current.count(old) == 1, "Bergamasque event card endpoint status changed unexpectedly"
    return current.replace(old, new)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register new S4 endpoints for the p.125 exhibition relation cluster.")
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

    event_card_path = ROOT / "04-knowledge/units/events/bergamasque-community-st-bartholomew-exhibitions-rome.md"
    event_card_after = updated_bergamasque_event_card(event_card_path)
    seen_names = {(row.get("type"), (row.get("name_en") or "").casefold()) for row in manifest}
    target_ids = {target["candidate"] for target in TARGETS}
    assert len(target_ids) == len(TARGETS)
    for target in TARGETS:
        cid = target["candidate"]
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert not (ROOT / target["card"]).exists(), f"card already exists: {target['card']}"
        assert target["card"] not in accepted
        assert target["ku"] not in {row.get("ku_id") for row in manifest}
        assert (target["type"], target["name_en"].casefold()) not in seen_names
        assert candidate.get("suggested_type") == target["type"]
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == target["group"]
        group_rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == target["group"]
        ]
        assert {row["candidate_id"] for row in group_rows} == {cid}

    for cid, expected_decision in ENDPOINT_DECISIONS.items():
        assert alignment_by_id[cid].get("decision") == expected_decision

    source = (ROOT / CH5).read_text(encoding="utf-8-sig")
    for phrase in [
        "Bergamasque community in Rome",
        "courtyard of the church of S. Bartolomeo",
        "S. Bartolomeo all’Isola arranged exhibitions for the saint’s name day",
        "occasions than the casual saints’ day fairs",
    ]:
        assert phrase in source, phrase

    statements = sync.load_statements()
    for target in TARGETS:
        cid = target["candidate"]
        found = {
            row["statement_id"] for row in statements
            if (row.get("subject_candidate_id") == cid or row.get("object_candidate_id") == cid)
            and (row.get("qualifiers") or {}).get("relation_candidate") is True
        }
        assert found == target["relations"], (cid, found)

    planned_alignment = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for target in TARGETS:
        cid = target["candidate"]
        target_row = next(row for row in planned_alignment if row.get("candidate_id") == cid and not row.get("external_source"))
        target_row["ku_id"] = target["ku"]
        target_row["resolution_note"] += f" S4 registration: mapped {target['group']} to {target['ku']}."
        planned_manifest.append({
            "ku_id": target["ku"],
            "type": target["type"],
            "canonical_name": target["name_zh"],
            "name_en": target["name_en"],
            "source_task": TASK,
            "card_path": target["card"],
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
        "\n\n<a id=\"s4-p125-exhibition-direct-endpoint-drain\"></a>\n\n"
        "### S4 多类型：第5章 p.125–126 展览关系端点登记（2026-10-17）\n\n"
        "在 `cand-11728` 贝加莫社群瞻礼展系列登记后，继续登记其 S2 关系候选直接指向的 S3 new 身份组："
        "`cand-6027` → institution `units/institutions/bergamasque-community-rome`；"
        "`cand-11729` → place `units/places/church-s-bartolomeo-bergamasque-exhibition-courtyard`；"
        "`cand-11735` → place `units/places/s-bartolomeo-all-isola-exhibition-site`；"
        "`cand-11736` → event `units/events/s-bartolomeo-all-isola-name-day-exhibitions`；"
        "`cand-11741` → term `units/terms/casual-saints-day-fairs`。每组各登记一个 KU，均以第5章 p.125–126 原文为依据。"
        "S3 undecided 端点 `cand-6028`、`cand-11730`、`cand-11734` 与 `cand-11740` 未改决定、未分配 KU；"
        "艺术家、挂毯及庭院画作候选 `cand-11731`、`cand-11732` 保持待证。\n\n"
        "相关直接 relation_candidate 分别留待 S6 裁决；未新增正式关系。更新贝加莫事件卡的端点入口，"
        "链接已登记的社群、地点及独立 S. Bartolomeo all’Isola 系列。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    result_text += (
        "\n\n### S4 多类型：第5章展览关系端点登记（2026-10-17）\n\n"
        "直接关系端点按 S3 原决定分别登记："
        "`cand-6027` → [罗马贝加莫社群](../units/institutions/bergamasque-community-rome.md)；"
        "`cand-11729` → [S. Bartolomeo 教堂庭院](../units/places/church-s-bartolomeo-bergamasque-exhibition-courtyard.md)；"
        "`cand-11735` → [S. Bartolomeo all’Isola 地点](../units/places/s-bartolomeo-all-isola-exhibition-site.md)；"
        "`cand-11736` → [S. Bartolomeo all’Isola 瞻礼展系列](../units/events/s-bartolomeo-all-isola-name-day-exhibitions.md)；"
        "`cand-11741` → [圣人瞻礼日集市术语](../units/terms/casual-saints-day-fairs.md)。"
        "S3 undecided 的圣人、Guardiano、信众与未名艺术家群体仍待证；所有相关关系候选留待 S6。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    for card in sorted(target["card"] for target in TARGETS):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 p.125–126 direct endpoint dry-run passed: groups={len(TARGETS)}; candidates={len(target_ids)}")
        print("types=institution,place,event,term; direct_relation_candidates=8 unique statements")
        print("S3 undecided endpoints preserved: cand-6028,cand-11730,cand-11734,cand-11740,cand-11731,cand-11732")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    for target in TARGETS:
        (ROOT / target["card"]).write_text(make_card(target), encoding="utf-8-sig", newline="\n")
    event_card_path.write_text(event_card_after, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(TARGETS)}; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
