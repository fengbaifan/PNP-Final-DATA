from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-place-cordellina-vicenza-house-20261017"
CANDIDATES = ("cand-8375", "cand-11069")
GROUP = "sg3-place-cordellina-vicenza-house"
KU_ID = "units/places/carlo-cordellina-vicenza-house"
CARD_REL = "04-knowledge/units/places/carlo-cordellina-vicenza-house.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "卡洛·科尔代利纳在维琴察的住宅"
NAME_EN = "Carlo Cordellina’s Vicenza House"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CHP9_FILE = "02-sources/02-Markdown/09_CHP-9_intro.md"
CHP20_FILE = "02-sources/02-Markdown/20_CHP-20Postscript.md"
QUOTE_CH9 = "And so he built himself two houses, one in his native Vicenza and one in the country at Montecchio."
QUOTE_CH20 = (
    "especially about the palace in\nVicenza which he began to have built in 1770 "
    "at the age of 73 and where he died eighteen years later."
)
RELATION_IDS = (
    "st-chp9-p256-cordellina-built-vicenza-house",
    "st-chp20-p405-cordellina-vicenza-palace",
)


def make_card() -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, ch. 9, p. 256.",
            "location": "第9章，印刷页256；OCR L160；PDF物理页18",
            "sentence_summary": "哈斯克尔说 Cordellina 在故乡 Vicenza 与乡间 Montecchio 各建一处住宅，并将后者与 Tiepolo 的装饰联系起来。",
            "original_quotes": [{"source_span": "L160; print p. 256; PDF physical p. 18", "text": QUOTE_CH9}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP9_FILE,
                "source_span": "L160; print p. 256; PDF physical p. 18",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, postscript, p. 405.",
            "location": "第20章后记，印刷页405；OCR L143–144；PDF物理页14",
            "sentence_summary": "哈斯克尔转述 Puppi 对 Carlo Cordellina 的新资料，称其在 Vicenza 的宫殿于1770年开始营建；原文未给正式建筑题名。",
            "original_quotes": [{"source_span": "L143–144; print p. 405; PDF physical p. 14", "text": QUOTE_CH20}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP20_FILE,
                "source_span": "L143–144; print p. 405; PDF physical p. 14",
            },
        },
    ]
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
    pending = "\n".join(f"- `{sid}`" for sid in RELATION_IDS)
    body = f"""## 内容

### 描述

**中文：** 本卡按既有 S3 跨章决定，指向哈斯克尔第9章 p.256 所称 Cordellina 在故乡 Vicenza 的住宅，以及后记 p.405 所称、1770年开始营建的 Vicenza 宫殿。S3 已将两处描述对齐为同一地点。原书未给正式建筑题名；本卡采用描述性暂题，不补更精确地址、现存状态或外部身份信息。p.405 的生平信息是哈斯克尔转述 Puppi，未独立查读 Puppi 文献。

**English:** Under the existing S3 cross-chapter decision, this card represents the house Haskell describes in chapter 9, p. 256 as Cordellina’s residence in his native Vicenza, and the palace in Vicenza that the postscript on p. 405 says he began building in 1770. S3 aligned the two descriptions as one place. The book gives no formal building title; this card uses a descriptive working title and adds no precise address, present survival status, or external identity information. The biographical detail on p. 405 is Haskell’s report of Puppi and Puppi’s source was not independently consulted.

### 名称与身份边界

| 字段 | 值 | 依据 |
|---|---|---|
| 第9章地点描述 / Chapter 9 place description | one in his native Vicenza | 第9章，印刷页256；S1 |
| 后记地点描述 / Postscript place description | the palace in Vicenza | 后记，印刷页405；S2 |
| 报告的营建起始年 / Reported construction start | 1770 | 后记，印刷页405；哈斯克尔转述 Puppi；S2 |
| 建筑正式名称 / Formal building title | 原书未提供 | 第9章与后记的描述；S1、S2 |

**中文：** 第9章明确区分 Vicenza 城内住宅与 Montecchio 乡间住宅；后者已单独登记为[蒙泰基奥的科尔德利纳别墅](villa-cordellina-montecchio.md)。本卡只对应 Vicenza 地点，不将城市本身或 Montecchio 别墅并入。

**English:** Chapter 9 distinguishes Cordellina’s house in Vicenza from his country house at Montecchio; the latter is registered separately as [Villa Cordellina at Montecchio](villa-cordellina-montecchio.md). This card represents only the Vicenza place, not the city itself or the Montecchio villa.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

以下书内关系候选仍待 S6 裁决：

{pending}
"""
    return f"---\n{fm}---\n\n{body}"


def insert_accepted_path(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Cordellina Vicenza house group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert all(cid in candidate_map and candidate_map[cid].get("suggested_type") == "place" for cid in CANDIDATES)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == list(CANDIDATES)
    for cid in CANDIDATES:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert candidate_map["cand-8375"].get("candidate_source_ref") == "chp-9:09_CHP-9_intro:l157-165#L160"
    assert candidate_map["cand-11069"].get("candidate_source_ref") == "chp-20:20_CHP-20Postscript:l137-148#L143"
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "place" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English title already exists in manifest"

    chapter9 = (ROOT / CHP9_FILE).read_text(encoding="utf-8-sig")
    postscript = (ROOT / CHP20_FILE).read_text(encoding="utf-8-sig")
    assert QUOTE_CH9 in chapter9 and QUOTE_CH20 in postscript
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    for sid, cid in zip(RELATION_IDS, CANDIDATES):
        statement = statements[sid]
        assert statement.get("object_candidate_id") == cid
        assert statement["qualifiers"].get("relation_candidate") is True

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: cross-chapter place group {GROUP} maps to {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "place",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_entry = f"""

<a id="{ANCHOR}"></a>

### S4 place：Carlo Cordellina 的维琴察住宅跨章组登记（{DATE}）

`cand-8375`（第9章 p.256，“one in his native Vicenza”）与 `cand-11069`（后记 p.405，1770年开始营建的 Vicenza palace）是既有 S3 组 `{GROUP}` 的两条候选。S3 依据跨章地点和人物锚点裁为同一地点，并明确原书没有正式建筑题名。现以描述性暂题登记为[卡洛·科尔代利纳在维琴察的住宅](../../../04-knowledge/units/places/carlo-cordellina-vicenza-house.md)。Montecchio 的 Villa Cordellina 保持为另一地点 KU；本卡不扩写地址、现存状态或外部建筑身份。

`st-chp9-p256-cordellina-built-vicenza-house` 与 `st-chp20-p405-cordellina-vicenza-palace` 仍是书内关系候选，留待 S6。p.405 的生平信息为哈斯克尔转述 Puppi，Puppi 文献未独立查读；本次不修改 `relations.csv`。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 place：Cordellina 维琴察住宅（{DATE}）\n\n"
        "第9章住宅候选与后记宫殿候选按既有跨章 S3 组映射到一张地点 KU；正式题名、地址和现存状态未由原书提供。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {', '.join(CANDIDATES)} are the complete two-member S3 group {GROUP}")
        print("verified chapter 9 and postscript passages plus the existing separate Montecchio villa KU")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv unchanged")
        print("planned writes: one bilingual place card, accepted.yml, ku-manifest.csv, two alignment mappings, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Cordellina Vicenza place group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
