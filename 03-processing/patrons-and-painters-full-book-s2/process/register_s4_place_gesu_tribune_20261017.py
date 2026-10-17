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
ANCHOR = "s4-place-gesu-tribune-20261017"
CANDIDATE = "cand-5000"
GROUP = "sg3-place-cand-5000"
KU_ID = "units/places/tribune-of-gesu"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "耶稣堂祭坛席空间"
NAME_EN = "Tribune of the Gesù"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
SOURCE_SPAN = "lines 6–17; print p. 66"
RELATION_STATEMENTS = {
    "st-chp3-seciv-l152-163-borgognone-was-to-decorate-tribune",
    "st-chp3-seciv-l16-24-cardinal-reserved-decoration",
    "st-chp3-seciv-l16-24-farnese-heirs",
    "st-chp3-seciv-l165-177-duke-refused-tribune-permission",
    "st-chp3-seciv-l165-177-members-and-architects-preferred-tribune",
    "st-chp3-seciv-l26-33-duke-professed-anxiety",
    "st-chp3-seciv-l75-81-farnese-tribune-mosaic-intention",
}


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 66.",
                "location": "第3章，印刷页66；OCR L6–17。",
                "sentence_summary": (
                    "哈斯克尔称 Cardinal Alessandro Farnese 将耶稣堂祭坛席装饰专留给家族；"
                    "其去世后，工程须获继承人许可。"
                ),
                "original_quotes": [
                    {
                        "source_span": "lines 8–9; print p. 66",
                        "text": "reserved the adornment of the tribune",
                    },
                    {
                        "source_span": "lines 8–9; print p. 66",
                        "text": "nothing could be done without the permission of his heirs",
                    },
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": SOURCE_SPAN,
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "[第3章 p.66](../../../02-sources/02-Markdown/03_CHP-3_sec_ii.md)（L8–9）"
    return f"""---
{fm}---

## 内容

### 空间身份

**中文：** 本卡记录原书所称耶稣堂的祭坛席空间。哈斯克尔说 Cardinal Alessandro Farnese 将该空间及 High Altar 的装饰专留给家族；他去世后，装饰工程须得到继承人许可。中文名称是描述性译名，英文原词保留用于身份定位。本卡不据此补充精确建筑边界或装饰现状。{source_link}

**English:** This unit records the architectural space Haskell calls the Gesù’s tribune. He says Cardinal Alessandro Farnese reserved its decoration, together with that of the High Altar, for his family; after Farnese’s death, work required the heirs’ permission. The Chinese title is descriptive, and the source’s English term is retained for identification. No precise architectural boundary or present decorative state is inferred. {source_link}

### 对象边界

祭坛席是[罗马耶稣堂](gesu-rome.md)内部空间，不与教堂建筑、High Altar 或其装饰作品合并。正文链接仅作导航；祭坛席与建筑、装饰计划及相关人物之间的正式关系留待 S6 审查。

## 关系与证据

当前没有已登记的正式关系。7条关系候选 `{', '.join(sorted(RELATION_STATEMENTS))}` 留待 S6 核对端点与证据。其中继承人候选 `cand-5007` 与参与决策的群体候选 `cand-5427` 仍为 S3 undecided；相关关系不得因本地点登记而提前成立。未新增 S5 enrichment。
"""


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
    parser = argparse.ArgumentParser(description="Register the Gesù tribune as an interior place in S4.")
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

    assert candidate_map[CANDIDATE].get("suggested_type") == "place"
    target = decisions[CANDIDATE]
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "place" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English place name already exists in manifest"

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    source_quotes = (
        "reserved the adornment of the tribune",
        "nothing could be done without the permission of his heirs",
    )
    assert all(" ".join(quote.split()) in source_text for quote in source_quotes)
    existing_endpoints = {
        "cand-0995": "units/persons/cardinal-alessandro-farnese",
        "cand-0997": "units/persons/duke-parma-ghezzi",
        "cand-0399": "units/persons/jacques-courtois",
    }
    assert all(decisions[cid].get("ku_id") == target_ku for cid, target_ku in existing_endpoints.items())
    assert decisions["cand-5007"].get("decision") == "undecided"
    assert decisions["cand-5427"].get("decision") == "undecided"

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    direct = {
        row["statement_id"]: row for row in statements.values()
        if CANDIDATE in {
            row.get("subject_candidate_id"), row.get("object_candidate_id"),
            *row.get("qualifiers", {}).get("mentioned_candidate_ids", []),
        }
    }
    assert RELATION_STATEMENTS.issubset(direct)
    assert all(direct[sid].get("qualifiers", {}).get("relation_candidate") is True for sid in RELATION_STATEMENTS)

    planned_alignment = [dict(row) for row in alignments]
    mapped = [
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(mapped) == 1
    mapped[0]["ku_id"] = KU_ID
    mapped[0]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    mapped[0]["resolution_note"] += f" S4 registration: source-backed interior place group {GROUP} maps to {KU_ID}; relations and unresolved endpoint identities remain for S6."

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
    process_text += f"""

<a id="{ANCHOR}"></a>

### S4 place：耶稣堂祭坛席内部空间（{DATE}）

单成员 S3 地点组 `{GROUP}`（`{CANDIDATE}`）映射至[耶稣堂祭坛席空间地点卡](../../../04-knowledge/units/places/tribune-of-gesu.md)。第3章 p.66 明确称 Cardinal Alessandro Farnese 将祭坛席装饰专留给家族，并称其死后装饰工程须获继承人许可。该对象是耶稣堂内部建筑空间，区别于教堂建筑、High Altar 与装饰作品。

7条关联关系候选留待 S6；`cand-5007` 继承人和 `cand-5427` 决策参与者群体仍为 S3 undecided。未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_text = result_text.rstrip() + (
        f"\n\n### S4 place：耶稣堂祭坛席内部空间（{DATE}）\n\n"
        f"`{CANDIDATE}` 映射至[祭坛席地点卡](../units/places/tribune-of-gesu.md)。"
        "地点依据第3章 p.66 的家族专属装饰和继承人许可叙述登记；继承人及决策群体仍待证，7条关系候选留待 S6。"
        "未新增正式关系或 S5 补足。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} is the complete single-member S3 place group {GROUP}")
        print(f"verified {len(source_quotes)} source quotations and {len(existing_endpoints)} mapped person endpoints")
        print(f"S6 relation candidates preserved: {len(RELATION_STATEMENTS)}; unresolved endpoint groups preserved: cand-5007, cand-5427")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; accepted path unique")
        print("planned writes: one bilingual place card, accepted.yml, ku-manifest.csv, one alignment mapping, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
