from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "sg3-place-villa-cordellina-montecchio"
MEMBERS = ("cand-8376", "cand-10279")
KU_ID = "units/places/villa-cordellina-montecchio"
CARD_REL = "04-knowledge/units/places/villa-cordellina-montecchio.md"
NAME_ZH = "蒙泰基奥的科尔德利纳别墅"
NAME_EN = "Villa Cordellina at Montecchio"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
ANCHOR = "s3-s4-place-villa-cordellina-montecchio-20261017"

SOURCES = (
    {
        "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "location": "第9章，印刷页256；L160；PDF物理页18",
        "span": "line 160; print p. 256; PDF physical p. 18",
        "quote": "And so he built himself two houses, one in his native Vicenza and one in the country at Montecchio. To decorate the latter he summoned Tiepolo",
        "summary": "Haskell区分Cordellina在Vicenza的住宅与Montecchio乡间住宅，并说Tiepolo受召装饰后者；本卡仅指乡间地点，另一住宅不并入。",
    },
    {
        "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        "location": "第14章，印刷页352；L57；PDF物理页6",
        "span": "line 57; print p. 352; PDF physical p. 6",
        "quote": "an exceedingly friendly letter from the Villa Cordellina, which he was then decorating",
        "summary": "Haskell称Tiepolo在1743年10月从Villa Cordellina写信，并说他当时正在装饰该处；此处与第9章的Montecchio乡间住宅构成同一地点的跨章身份证据，装饰关系本身仍待S6。",
    },
)

OLD_DETAILS = {
    "cand-8376": "S3 cross-chapter review 2026-10-17: the Montecchio country house where Tiepolo decorated is named Villa Cordellina at p.352 (cand-10279); the two chapter anchors identify the same place.",
    "cand-10279": "S3 cross-chapter review 2026-10-17: Villa Cordellina at Montecchio is the country house where Haskell says Tiepolo was decorating; same place identity as cand-8376. The source does not supply a separate formal building title.",
}
NEW_DETAILS = {
    "cand-8376": "S3 cross-chapter review 2026-10-17: the Montecchio country house where Tiepolo decorated is named Villa Cordellina at chapter 14 p.352 (cand-10279); the ch.9 anchor is source line 160, printed p.256. The two chapter anchors identify the same place.",
    "cand-10279": "S3 cross-chapter review 2026-10-17: Villa Cordellina at Montecchio is the country house where Haskell says Tiepolo was decorating; same place identity as cand-8376 (ch.9 source line 160, printed p.256; ch.14 p.352). The source does not supply a separate formal building title.",
}


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def make_card() -> str:
    sources = []
    for item in SOURCES:
        sources.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p256 = "[第9章 p.256](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L160）"
    p352 = "[第14章 p.352](../../../02-sources/02-Markdown/14_CHP-14_intro.md)（L57）"
    relation_list = "\n".join((
        "- `st-chp9-p256-cordellina-built-montecchio-house`",
        "- `st-chp14-p352-tiepolo-decorated-villa-cordellina`",
    ))
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡指向Haskell在第9章称为Montecchio乡间住宅、并在第14章称为Villa Cordellina的同一地点。第9章明确将其与Cordellina位于Vicenza的另一住宅分开；第14章则将Tiepolo当时装饰的Villa Cordellina置于1743年10月写信的语境。此卡只记录书内支持的地点身份和名称，不补定现代行政边界、现存状态或未由来源给出的正式建筑名。中文名为描述性工作译名。{p256} {p352}

**English:** This unit represents the place that Haskell describes in Chapter 9 as Cordellina’s country house at Montecchio and names in Chapter 14 as Villa Cordellina. Chapter 9 distinguishes it from Cordellina’s other house in Vicenza; Chapter 14 places Tiepolo at Villa Cordellina while he was decorating it in October 1743. The unit records only the place identity and names supported by the book. It does not add modern administrative boundaries, present survival, or a formal building title not supplied by the source. The English display name is descriptive. {p256} {p352}

### 名称与身份边界

- **书内名称：** `Villa Cordellina`；Haskell另以“one in the country at Montecchio”定位此处。{p256} {p352}
- **类型：** 建筑与乡间住宅地点（place）；本卡登记地点身份，不登记Tiepolo所作的壁画/室内作品为地点的一部分。
- **分开对象：** 第9章明言Cordellina还在其故乡Vicenza建有另一住宅；该宅邸由独立候选组`sg3-place-cordellina-vicenza-house`保留，不并入本卡。{p256}
- **页码校正：** 此组第9章锚点是Markdown行L160，印刷页为p.256；S3过程记录中旧写法“p.160”把源行号误作页码，现已更正候选detail与alignment理由，不改变身份决定。{p256}

## 关系与证据

当前没有正式关系。以下2条直接S2关系候选仍待S6；本次地点身份登记不自动确立Cordellina建造住宅或Tiepolo装饰的正式关系：

{relation_list}"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Villa Cordellina place group in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    align_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(candidate_by_id[cid].get("suggested_type") == "place" for cid in MEMBERS)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    card_path = ROOT / CARD_REL
    registered = [r for r in manifest if r.get("ku_id") == KU_ID and r.get("card_path") == CARD_REL]
    if registered and card_path.exists() and CARD_REL in accepted and all(decisions[cid].get("ku_id") == KU_ID for cid in MEMBERS):
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 2 relation candidates remain non-formal.")
        return 0
    for cid in MEMBERS:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
        assert candidate_by_id[cid].get("detail") == OLD_DETAILS[cid], (cid, candidate_by_id[cid].get("detail"))
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)

    for item in SOURCES:
        source = ROOT / item["file"]
        text = " ".join(source.read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in text, (item["file"], item["quote"])

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [row for row in statements if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert {row.get("statement_id") for row in relations} == {
        "st-chp9-p256-cordellina-built-montecchio-house",
        "st-chp14-p352-tiepolo-decorated-villa-cordellina",
    }

    planned_candidates = [dict(row) for row in candidates]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}
    for cid in MEMBERS:
        planned_candidate_by_id[cid]["detail"] = NEW_DETAILS[cid]
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for cid in MEMBERS:
        row = planned_by_id[cid]
        if cid == "cand-8376":
            row["resolution_note"] = row["resolution_note"].replace(
                "P.160 Cordellina house at Montecchio",
                "printed p.256 (source line L160) Cordellina house at Montecchio",
            )
            assert "printed p.256 (source line L160)" in row["resolution_note"]
        else:
            row["resolution_note"] = row["resolution_note"].replace(
                "p.160 Cordellina house at Montecchio",
                "p.256 (source line L160) Cordellina house at Montecchio",
            )
            assert "p.256 (source line L160)" in row["resolution_note"]
        row["ku_id"] = KU_ID
        row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; locator clarified as ch.9 source L160 / printed p.256."

    planned_manifest = list(manifest)
    planned_manifest.append({"ku_id": KU_ID, "type": "place", "canonical_name": NAME_ZH, "name_en": NAME_EN, "source_task": TASK, "card_path": CARD_REL})
    card = make_card()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated place card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 evidence locator correction / S4 place：Villa Cordellina at Montecchio（{DATE}）\n\n"
        "S3原过程段落及候选说明中的“p.160”误把来源Markdown行号L160写作印刷页。现据`st-chp9-p256-cordellina-built-montecchio-house`、第9章页标与PDF物理页记录更正为印刷p.256（PDF物理页18）；候选detail及两条alignment rationale已原位更正，S3身份决定仍为同一跨章new组，不改变候选去向。\n"
        f"- `{MEMBERS[0]}`（第9章p.256，源行L160）与`{MEMBERS[1]}`（第14章p.352）统一登记至[{NAME_EN}地点卡](../../../{CARD_REL})。Haskell分别称Montecchio乡间住宅和Villa Cordellina；第9章另述的Vicenza住宅仍由独立候选组保留。\n"
        "- 2条直接关系候选（Cordellina建宅、Tiepolo装饰）留待S6；未新增正式关系、现代地理断言或独立建筑作品对象。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = process_text + process_append
    next_result += (
        f"\n\n### place：Villa Cordellina at Montecchio 跨章身份组 S4 登记（{DATE}）\n\n"
        f"`{MEMBERS[0]}`（第9章p.256，源行L160）与`{MEMBERS[1]}`（第14章p.352）映射至[地点卡](../units/places/villa-cordellina-montecchio.md)。修正此前把L160误写成印刷页p.160的定位；Vicenza住宅保持独立。2条关系候选待S6。\n\n"
        f"S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )

    if args.dry_run:
        print(f"S4 place dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; relation candidates pending={len(relations)}")
        print(f"locator correction: p.160 -> source line L160 / printed p.256; manifest={len(manifest)}->{len(planned_manifest)}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; no files changed")
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "entity-candidates.csv", candidate_fields, planned_candidates)
    sync.write_csv(TABLES / "alignment.csv", align_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; relation candidates pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
