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
GROUP = "sg3-place-cand-4258"
MEMBERS = ("cand-4258",)
KU_ID = "units/places/barberini-chapel-cupola-s-andrea-della-valle"
CARD_REL = "04-knowledge/units/places/barberini-chapel-cupola-s-andrea-della-valle.md"
NAME_ZH = "谷地圣安德烈堂巴贝里尼礼拜堂穹顶"
NAME_EN = "Cupola of the Barberini Chapel at S. Andrea della Valle"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
ANCHOR = "s3-s4-place-barberini-chapel-cupola-20261017"
PARENT_CARD = "barberini-chapel-sant-andrea-valle.md"
RELATION_ID = "st-chp2-seci-l55-69-cupola-proposal"
RELATION_ID_2 = "st-chp3-seciv-l8-14-cupola-style-comparison"
SOURCES = (
    {
        "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
        "location": "第2章，印刷页25；L52；PDF物理页6",
        "span": "line 52; print p. 25",
        "quote": "Theatine church of S. Andrea della Valle",
        "summary": "Haskell称Maffeo为自己在S. Andrea della Valle新建的Theatine教堂选择礼拜堂；该处为穹顶所在的母空间。",
    },
    {
        "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
        "location": "第2章，印刷页26；L59；PDF物理页7",
        "span": "line 59; print p. 26; PDF physical p. 7",
        "quote": "Passignani proposed that the cupola should be adorned with coloured mosaic and gilt stucco ribs, and he suggested a number of artists who would be suitable.3",
        "summary": "Haskell称Passignani提出用彩色马赛克和镀金灰泥肋装饰该穹顶，并建议合适的艺术家；这是方案陈述，不证明方案被执行。",
    },
    {
        "file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "location": "第3章，印刷页77；L11；PDF物理页19",
        "span": "line 11; print p. 77; PDF physical p. 19",
        "quote": "Pietro did little more than produce an elegant variation of the cupola of S. Andrea della Valle.",
        "summary": "Haskell将Pietro da Cortona在Chiesa Nuova的穹顶装饰与S. Andrea della Valle穹顶作风格比较；这是作者的艺术史评价，不表示两处空间或作品为同一对象。",
    },
)


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
    p25 = "[第2章 p.25](../../../02-sources/02-Markdown/02_CHP-2_sec_i.md)（L52）"
    p26 = "[第2章 p.26](../../../02-sources/02-Markdown/02_CHP-2_sec_i.md)（L59）"
    p77 = "[第3章 p.77](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L11）"
    parent_link = f"[完整礼拜堂地点卡]({PARENT_CARD})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录Haskell第2章所述巴贝里尼礼拜堂的穹顶空间。第25页将Maffeo为自己建造的礼拜堂置于S. Andrea della Valle教堂；第26页称Passignani提出以彩色马赛克和镀金灰泥肋装饰穹顶。第3章又以此穹顶作为Pietro da Cortona在Chiesa Nuova所作穹顶装饰的比较对象；该比较不把两处空间或作品合并。此卡只表示建筑内部空间，不表示装饰方案已实施，也不吸收壁画或lunette场景。{p25} {p26} {p77}

**English:** This unit records the cupola space of the Barberini Chapel described in Chapter 2. Page 25 places Maffeo’s family chapel in the Theatine church of S. Andrea della Valle; page 26 says Passignani proposed coloured mosaics and gilt stucco ribs for the cupola. Chapter 3 uses this cupola as the point of comparison for Pietro da Cortona’s cupola decoration at Chiesa Nuova; the comparison does not merge the two spaces or works. This unit represents only the architectural space. It does not claim that the proposal was executed or absorb the separately mentioned frescoes and lunette scenes. {p25} {p26} {p77}

### 名称与身份边界

- **书内语境：** Maffeo为自己在S. Andrea della Valle新建的Theatine教堂选择礼拜堂；Passignani提出穹顶装饰方案。第3章的风格比较指向另一处Chiesa Nuova穹顶，不改变本地点身份。{p25} {p26} {p77}
- **对象类型：** place，指礼拜堂内部的穹顶空间；完整礼拜堂见{parent_link}。该导航只指向母空间，不表示已经登记正式部分关系。
- **作品边界：** 彩色马赛克／镀金灰泥肋方案与穹顶壁画、lunette场景均不并入本地点。壁画候选`cand-4259`和lunette作品候选`cand-4260`仍为S3 `undecided`。
- **执行状态：** 来源只称Passignani提出装饰方案；不推定方案获准、实施或保存至今。{p26}

## 关系与证据

当前没有正式关系。直接S2候选`{RELATION_ID}`记载Passignani提出穹顶装饰方案；`{RELATION_ID_2}`记录Haskell对Pietro da Cortona穹顶装饰的风格比较。两条均待S6裁决；本卡未把方案或作者评价转为正式边。"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Barberini chapel cupola place endpoint in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
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
    assert all(cid in candidate_by_id and candidate_by_id[cid].get("suggested_type") == "place" for cid in MEMBERS)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    card_path = ROOT / CARD_REL
    registered = [r for r in manifest if r.get("ku_id") == KU_ID and r.get("card_path") == CARD_REL]
    if registered and card_path.exists() and CARD_REL in accepted and all(decisions[cid].get("ku_id") == KU_ID for cid in MEMBERS):
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; proposal relation remains pending S6.")
        return 0
    for cid in MEMBERS:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "place" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)

    for item in SOURCES:
        text = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in text, (item["file"], item["quote"])
    existing_parent = ROOT / "04-knowledge" / "units" / "places" / PARENT_CARD
    assert existing_parent.exists(), f"missing parent chapel card: {existing_parent}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [row for row in statements if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert {row.get("statement_id") for row in relations} == {RELATION_ID, RELATION_ID_2}

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; architectural space remains distinct from chapel and works."
    planned_manifest = list(manifest)
    planned_manifest.append({"ku_id": KU_ID, "type": "place", "canonical_name": NAME_ZH, "name_en": NAME_EN, "source_task": TASK, "card_path": CARD_REL})
    card = make_card()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated place card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 place：Barberini Chapel穹顶直接关系端点登记（{DATE}）\n\n"
        f"- `{MEMBERS[0]}`（`{GROUP}`）登记为[{NAME_EN}地点卡](../../../{CARD_REL})。第2章p.25将Maffeo自用礼拜堂置于S. Andrea della Valle，p.26记录Passignani提出穹顶方案；第3章p.77将该穹顶作为Pietro da Cortona在Chiesa Nuova穹顶装饰的比较对象，不把两处合并。该KU只表示礼拜堂内部建筑空间。\n"
        f"- `{RELATION_ID}`与`{RELATION_ID_2}`两条关系候选留待S6；穹顶壁画`cand-4259`与lunette作品`cand-4260`仍为S3 undecided。未推断方案实施情况、未登记正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = process_text + process_append
    next_result += (
        f"\n\n### place：Barberini Chapel cupola直接端点 S4 登记（{DATE}）\n\n"
        f"`{MEMBERS[0]}`登记至[地点卡](../units/places/barberini-chapel-cupola-s-andrea-della-valle.md)，与完整礼拜堂及作品分开。第3章p.77比较支持同一地点指称，但比较对象保持独立；2条关系候选待S6。\n\n"
        f"S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )

    if args.dry_run:
        print(f"dry-run passed: {GROUP} -> {KU_ID}; source anchors={len(SOURCES)}; relation_candidates_pending={len(relations)}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}; no files changed")
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
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
    print(f"applied: {GROUP} -> {KU_ID}; relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
