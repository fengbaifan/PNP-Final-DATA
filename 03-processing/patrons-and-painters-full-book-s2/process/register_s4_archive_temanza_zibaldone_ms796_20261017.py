from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
MEMBERS = ["cand-2547", "cand-6588"]
GROUP = "archive-group-temanza-zibaldone-ms796"
KU_ID = "units/archives/temanza-zibaldone-ms-796"
NAME_ZH = "托马索·滕曼扎未刊《Zibaldone》手稿（MS 796）"
NAME_EN = "Tommaso Temanza, unpublished Zibaldone MS 796"
CARD_REL = f"04-knowledge/{KU_ID}.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/T.csv"
BODY_FILE = "02-sources/02-Markdown/06_CHP-6_sec_v.md"
RELATION_IDS = {"st-chp6-p165-n5-cite"}
ANCHOR = "s4-archive-temanza-zibaldone-ms796-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def insert_accepted(lines: list[str]) -> list[str]:
    entry = f"- {CARD_REL}"
    assert entry not in lines
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > CARD_REL),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def make_card() -> str:
    frontmatter = yaml.safe_dump({
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第6章，印刷页165，注5；OCR L68",
                "sentence_summary": "脚注引用 Tommaso Temanza 未刊 Zibaldone，MS 796，Seminario Patriarcale, Venice。该引文作为定位记录，手稿未独立查阅。",
                "original_quotes": [{
                    "source_span": "line 68; print p. 165, note 5",
                    "text": "See the unpublished Zibaldone by Tommaso Temanza—MS. 796 in Seminario Patriarcale, Venice.",
                }],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": BODY_FILE,
                    "source_span": "line 68; print p. 165, note 5",
                },
            },
            {
                "citation": "Francis Haskell, *Patrons and Painters*, index.",
                "location": "全书索引 T.csv#10",
                "sentence_summary": "Temanza, Tommaso 子项 Zibaldone 定位至 p.165 注。",
                "original_quotes": [{"source_span": "T.csv#10", "text": "Temanza, Tommaso — Zibaldone — 165n"}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": INDEX_FILE,
                    "source_span": "T.csv#10",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000)
    body_link = "[第6章 p.165 注5](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md)"
    index_link = f"[索引 T.csv#10](../../../{INDEX_FILE})"
    relations = ", ".join(sorted(RELATION_IDS))
    return f"""---
{frontmatter}---

## 内容

### 描述

**中文：** 本知识元记录 Haskell 第6章 p.165 注5 引用的 Tommaso Temanza 未刊 Zibaldone 手稿，编号 MS 796；脚注将其定位于 Seminario Patriarcale, Venice。索引 T.csv#10 的 Temanza, Tommaso／Zibaldone 子项也定位至 p.165 注，与正文书目锚点相合。本卡对应来源中所指的具体手稿，不表示本轮查阅了手稿，也不独立验证其馆藏现状或目录层级。〔{body_link}；{index_link}〕

**English:** This unit records the unpublished Zibaldone manuscript by Tommaso Temanza cited in Haskell’s Chapter 6, p.165 note, with shelfmark MS 796. The note locates it at Seminario Patriarcale, Venice. The index entry for Temanza, Tommaso / Zibaldone also points to p.165 n., matching the bibliographic locator. This unit represents the specific manuscript as identified by the source; it does not imply that the manuscript was consulted or independently verify its current holding or catalog hierarchy. ({body_link}; {index_link})

### 对象边界

- 身份组 {GROUP} 的成员为 {', '.join(MEMBERS)}；索引子项与脚注题名、责任者及 MS 编号相合。
- 对象类型为 archive 中的未刊手稿，不与 Temanza 的其他著作或其本人合并；未推断抄本内容、日期、装订或馆藏层级。
- “Seminario Patriarcale, Venice”仅按 Haskell 注释保留为来源定位，本轮未独立查核。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 引用候选（{relations}）留待 S6；其 claim 只说明 Haskell 在注释中引用该手稿。KU 登记不代表手稿内容或引文的独立验证。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Temanza Zibaldone MS 796 archive identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert candidate_by_id[MEMBERS[0]]["suggested_type"] == "archive"
    assert candidate_by_id[MEMBERS[0]]["index_entry_id"] == "T.csv#10"
    assert candidate_by_id[MEMBERS[0]]["sub_entry"] == "Zibaldone"
    assert candidate_by_id[MEMBERS[1]]["canonical_name"] == "Temanza, unpublished Zibaldone MS 796"
    assert candidate_by_id[MEMBERS[1]]["candidate_origin"] == "body-mention"

    member_rows = [
        row for row in alignments
        if row.get("candidate_id") in MEMBERS and not row.get("external_source")
    ]
    assert len(member_rows) == 2 and all(row["decision"] == "new" and not row.get("ku_id") for row in member_rows)
    assert all(sync.get_group(row.get("resolution_note", "")) == GROUP for row in member_rows)
    current_members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert current_members == MEMBERS
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(row.get("type") == "archive" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)
    assert not (ROOT / CARD_REL).exists()
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert CARD_REL not in accepted_lines

    body = (ROOT / BODY_FILE).read_text(encoding="utf-8-sig")
    index = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "unpublished Zibaldone by Tommaso Temanza—MS. 796 in Seminario Patriarcale, Venice" in body
    assert '"Temanza, Tommaso",,Zibaldone,,165n' in index
    statements = {
        row["statement_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    relation_rows = [statements[sid] for sid in RELATION_IDS]
    assert len(relation_rows) == 1
    assert relation_rows[0]["object_candidate_id"] == MEMBERS[1]
    assert (relation_rows[0].get("qualifiers") or {}).get("relation_candidate") is True

    planned_alignments = [dict(row) for row in alignments]
    for row in planned_alignments:
        if row.get("candidate_id") in MEMBERS and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] += (
                f" S4登记（{DATE}）：{GROUP} 中的候选映射至 {KU_ID}；一个具体手稿身份组对应一个 archive KU。"
                "脚注只作引文定位，MS 796 未独立查阅；直接引用关系候选留待 S6。"
            )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = insert_accepted(accepted_lines)
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4968
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 671
    assert totals["registered_members"] == 832
    assert totals["pending_groups"] == 4114
    assert totals["pending_members"] == 4136

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 archive：Temanza 未刊 Zibaldone MS 796 登记（{DATE}）\n\n"
        f"S3 new 组 {GROUP} 含 {MEMBERS[0]}（T.csv#10 的 Zibaldone 索引子项）与 {MEMBERS[1]}（第6章 p.165 注5 的未刊手稿引用），"
        f"合并登记为 [ {NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。索引页码、题名、责任者和 MS 796 定位相合；"
        "该卡仅记录 Haskell 的引文定位，手稿未独立查阅。\n"
        f"- 直接 S2 引用候选 {', '.join(sorted(RELATION_IDS))} 留待 S6；本次未新增 formal relations。\n"
        f"- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert count == 1
    result_text += (
        f"\n\n### S3/S4 archive：Temanza 未刊 Zibaldone MS 796（{DATE}）\n\n"
        f"{MEMBERS[0]}、{MEMBERS[1]} → [{NAME_ZH}（{NAME_EN}）](../units/archives/temanza-zibaldone-ms-796.md)。"
        "手稿身份限于原书脚注和索引定位；馆藏与手稿内容未独立核验。引用候选留待 S6。"
    )

    assert len(planned_manifest) == len(manifest) + 1
    if args.dry_run:
        print(
            f"dry-run passed: {GROUP}->{KU_ID}; members={len(MEMBERS)}; relation_candidates={len(relation_rows)}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    (ROOT / CARD_REL).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP}->{KU_ID}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
