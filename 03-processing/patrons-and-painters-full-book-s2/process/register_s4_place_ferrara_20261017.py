from __future__ import annotations

import argparse
import json
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

CANDIDATE_IDS = ("cand-1017",)
GROUP = "sg3-place-ferrara"
KU_ID = "units/places/ferrara"
CARD_REL = "04-knowledge/units/places/ferrara.md"
NAME_ZH = "费拉拉"
NAME_EN = "Ferrara"
ANCHOR = "s4-place-ferrara-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
        "location": "第2章；印刷页25；L48",
        "source_span": "L48; print p. 25",
        "quote": "on his visit to Ferrara to take over the city",
        "summary_cn": "第2章称 Ferrara 为 city，并叙述1598年到该城接管的情境；本卡只据此确认书内城市地点指称。",
        "summary_en": "Chapter 2 calls Ferrara a city in its account of the 1598 visit to take it over; this supports the book's city-place reference only.",
    },
    {
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
        "location": "第2章；印刷页48；L57",
        "source_span": "L57; print p. 48",
        "quote": "The Bentivoglio came from Ferrara, where they had for centuries been one of the most distinguished families.",
        "summary_cn": "第2章以 Ferrara 作为 Bentivoglio 家族相关叙述中的城市地点；其家族起源与支系限定保留在原段及注释，不在此扩写。",
        "summary_en": "Chapter 2 uses Ferrara as the city-place in its Bentivoglio account; the family-origin and branch qualifications remain in the source passage and note and are not expanded here.",
    },
    {
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章；印刷页221；L118–119",
        "source_span": "L118-L119; print p. 221",
        "quote": "before going to Ferrara, with which his connection was particularly close. He remained there from 1710 as\nLegate and from 1717 as Archbishop until 1738",
        "summary_cn": "第8章先点名 Ferrara，随后以 there 指该城并叙述 Tommaso Ruffo 的驻地职务；此处只作地点身份的跨章语境依据。",
        "summary_en": "Chapter 8 names Ferrara and then uses “there” for Ruffo's offices; this is retained only as cross-chapter context for the place identity.",
    },
)

EXPECTED_RELATION_IDS = {
    "st-chp2-seci-l44-53-ferrara-mechanism",
    "st-chp2-seciv-l190-245-bentivoglio-branch",
    "st-chp2-seciv-l54-63-bentivoglio-family-origin-and-standing",
    "st-chp2-seciv-l54-63-ferrara-devolves-to-papacy-1598",
    "st-chp8-p221-ruffo-legate-in-ferrara-from-1710",
    "st-chp8-p221-ruffo-archbishop-in-ferrara-1717-1738",
    "st-chp8-p222-six-popes-benefited-ferrara-or-legate",
}


def make_card() -> str:
    sources = []
    for item in SOURCES:
        sources.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary_cn"],
            "original_quotes": [{"source_span": item["source_span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["source_file"],
                "source_span": item["source_span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    links = [
        "[第2章 p.25](../../../02-sources/02-Markdown/02_CHP-2_sec_i.md)",
        "[第2章 p.48](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)",
        "[第8章 p.221](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)",
    ]
    citations = " ".join(links)
    relation_lines = "\n".join(f"- `{statement_id}`" for statement_id in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** 费拉拉（Ferrara）是本书多章直接称作 city 或 town 的城市地点。第2章以其作为1598年接管叙述中的城市，第8章又以其作为相关驻地语境。此卡只登记城市地点身份；政治转移、家族沿革、任职及收藏等陈述仍按原书语境保留为独立S2候选，不在本卡扩写为完整城市史。{citations}

**English:** Ferrara is a city-place that the book directly calls a city or town in multiple chapters. Chapter 2 uses it as the city in an account of the 1598 takeover, while Chapter 8 uses it as a setting for later offices. This card registers only the city-place identity; statements about political transfer, family history, offices, and collections remain separate S2 candidates in their source context and are not expanded into a city history here. {citations}

### 名称与身份范围

- 书内名称：Ferrara；中文显示名“费拉拉”为本卡的中文译名。{links[0]}
- 地点性质：城市地点；书中另以 town 指称。{links[0]} {links[1]}
- 跨章指称：第2章涉及1598年城市接管及 Bentivoglio 语境；第8章涉及 Cardinal Tommaso Ruffo 在当地任职的叙述。具体候选陈述均保留原有证据限定。{links[1]} {links[2]}

## 关系与证据

### 关系记录

当前没有新增正式关系。以下7条直接涉及 `cand-1017` 的S2关系候选仍留待S6逐条裁决；本卡不把共现或候选状态转成正式关系：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Ferrara cross-chapter place identity in S4.")
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
    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    candidate = candidate_by_id["cand-1017"]
    alignment = alignment_by_id["cand-1017"]
    assert candidate.get("suggested_type") == "place"
    assert candidate.get("canonical_name") == "Ferrara"
    assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    assert len(manifest_targets) <= 1
    registered = bool(manifest_targets) and alignment.get("ku_id") == KU_ID and CARD_REL in accepted_paths and card_path.exists()
    if registered:
        assert len(manifest_targets) == 1 and manifest_targets[0].get("canonical_name") == NAME_ZH
        assert card_path.read_text(encoding="utf-8-sig") == make_card()
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 7 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and not alignment.get("ku_id") and not card_path.exists() and CARD_REL not in accepted_paths
    assert not any(
        row.get("type") == "place" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "Ferrara already exists as a place KU"

    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(CANDIDATE_IDS), group_members
    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATE_IDS or row.get("object_candidate_id") in CANDIDATE_IDS)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == EXPECTED_RELATION_IDS, (direct_relations, EXPECTED_RELATION_IDS)
    for item in SOURCES:
        text = " ".join((ROOT / item["source_file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in text, (item["source_file"], item["source_span"])

    planned_alignment = [dict(row) for row in alignments]
    planned_alignment_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_alignment_by_id["cand-1017"]["ku_id"] = KU_ID
    planned_alignment_by_id["cand-1017"]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "place",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 place：Ferrara 跨章城市身份组登记（2026-10-17）\n\n"
        f"`cand-1017`（`{GROUP}`）登记为[费拉拉地点卡](../../../{CARD_REL})。S3以第2章及第8章的直接城市指称归为一个地点身份组；"
        "本卡仅记录地名和城市地点范围。7条直接关系候选仍待S6逐条裁决，没有写入正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### place：Ferrara 跨章身份组 S4 登记（2026-10-17）\n\n"
        f"`cand-1017` → [费拉拉地点卡](../units/places/ferrara.md)。第2章与第8章均以 Ferrara 指称城市地点；"
        "7条直接S2关系候选未转为正式关系。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
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
        print(f"S4 place dry-run passed: {GROUP} -> {KU_ID}")
        print(f"direct relation candidates={len(direct_relations)}; source quotations={len(SOURCES)}")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,}->{len(planned_manifest):,}"
        )
        print("no files changed")
        return 0

    card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
