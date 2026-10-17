from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
KU_ID = "units/persons/carlo-barberini-brother-of-urban-viii"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/B.md"
CHAPTER_FILE = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
TARGETS = {
    "cand-0196": {
        "index_entry": "B.csv#43",
        "page_range": "31",
        "sub_entry": "purchase of Orsini and Colonna estates",
        "statement": "The index subentry at B.csv#43 points to p.31, where the immediately relevant body passage names Carlo Barberini as the buyer of the Orsini and Colonna estates.",
    },
    "cand-0197": {
        "index_entry": "B.csv#44",
        "page_range": "41",
        "sub_entry": "synopsis of Machiavelli's Prince",
        "statement": "The index subentry at B.csv#44 points to p.41 and matches st-chp2-secii-l118-125-carlo-prince-synopsis, whose subject_candidate_id is cand-0197 and whose original quote says Carlo made a Latin synopsis of Machiavelli's Prince. The surrounding passage identifies that Carlo as Urban VIII's brother.",
    },
}

PROCESS_NOTE = """\

### S3 person 复核：Carlo Barberini 的重复索引子项复用（2026-10-17）

`cand-0196`（B.csv#43，“purchase of Orsini and Colonna estates”，p.31）与 `cand-0197`（B.csv#44，“synopsis of Machiavelli's Prince”，p.41）原因缺少各自的 `mentions.csv` 映射而列 `undecided`。复核发现，前者的索引子项对应第2章 p.31 L7–8，正文明确以全名 Carlo Barberini 指称两笔地产交易的同一买方；该段已由 `cand-0194` 的 S2 提及锚定。后者对应第2章 p.41 L121–124，statement `st-chp2-secii-l118-125-carlo-prince-synopsis` 将 `cand-0197` 作为主体候选，原文说 Carlo 撰写了 Machiavelli《君主论》的拉丁文提要；同段前句已明确所指为 Urban VIII 之兄。两条索引主项均明示相同亲属身份，且子项与正文内容逐一吻合，因此现改为 `same` → `units/persons/carlo-barberini-brother-of-urban-viii`。原暂缓理由保留在 alignment 行中；该人物边界仍与 Urban VIII 的父亲 Carlo Barberini 区分。`cand-0197` 所关联的 S2 关系候选仍待 S6，本轮不创建正式关系或新增内容字段。
"""

RESULT_NOTE = """\

### S3 person：Carlo Barberini 重复索引子项复用已登记人物（2026-10-17）

- `cand-0196`（B.csv#43，地产购买，p.31）由 `undecided` 改为 `same` → [Urban VIII 之兄 Carlo Barberini 人物卡](../units/persons/carlo-barberini-brother-of-urban-viii.md)：索引子项对应正文 L7–8；正文以全名将两笔地产交易归于同一买方，并已由 `cand-0194` 的 S2 提及锚定。
- `cand-0197`（B.csv#44，马基雅维利《君主论》提要，p.41）由 `undecided` 改为 `same` → 同一人物卡：索引子项与 S2 statement `st-chp2-secii-l118-125-carlo-prince-synopsis` 相符，该 statement 明确以 `cand-0197` 为主体候选；同段将 Carlo 指明为 Urban VIII 之兄。
- 两条 alignment 均保留原暂缓理由并追加正文／索引核对依据；不将 S2 关系候选转为正式关系。S3 计数更新为 same=1,792（1,029个 KU）、undecided=5,494；new 及 S4 数量不变。
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, f"expected exactly one {label} anchor, found {count}"
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve two Carlo Barberini duplicate index subentries to the existing person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}

    assert all(cid in candidate_by_id and cid in alignment_by_id for cid in TARGETS)
    assert all(alignment_by_id[cid]["decision"] == "undecided" and not alignment_by_id[cid].get("ku_id") for cid in TARGETS)
    assert all(candidate_by_id[cid]["canonical_name"] == "Barberini, Carlo (brother to Urban VIII)" for cid in TARGETS)
    assert all(candidate_by_id[cid]["index_entry_id"] == info["index_entry"] for cid, info in TARGETS.items())
    assert all(candidate_by_id[cid]["index_page_range"] == info["page_range"] for cid, info in TARGETS.items())
    assert all(candidate_by_id[cid]["sub_entry"] == info["sub_entry"] for cid, info in TARGETS.items())

    for cid in ("cand-0194", "cand-0195"):
        row = alignment_by_id[cid]
        assert row["decision"] == "new" and row["ku_id"] == KU_ID
    assert any(row.get("ku_id") == KU_ID and row.get("type") == "person" for row in manifest)

    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    chapter_text = (ROOT / CHAPTER_FILE).read_text(encoding="utf-8-sig")
    chapter_text_flat = re.sub(r"\s+", " ", chapter_text)
    assert "| Barberini, Carlo (brother to Urban VIII) |  | purchase of Orsini and Colonna estates |  | 31 |" in index_text
    assert "| Barberini, Carlo (brother to Urban VIII) |  | synopsis of Machiavelli's Prince |  | 41 |" in index_text
    assert "the Orsini sold their estates at Monte Rotondo to Carlo Barberini; a year later the Colonna sold their Castle of Roviano to the same buyer." in chapter_text_flat
    assert "When his brother Carlo died in 1630" in chapter_text

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    synopsis = next(row for row in statements if row["statement_id"] == "st-chp2-secii-l118-125-carlo-prince-synopsis")
    assert synopsis["subject_candidate_id"] == "cand-0197"
    assert "Latin synopsis of Machiavelli’s\nPrince" in synopsis["original_quote"]

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        cid = row.get("candidate_id")
        if cid not in TARGETS or row.get("external_source"):
            continue
        old_note = row.get("resolution_note", "")
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["resolution_note"] = (
            old_note
            + " S3 2026-10-17: 原undecided理由保留；复核后据对应索引子项、正文页码与锚点改判same并复用已登记KU "
            + KU_ID
            + ". "
            + TARGETS[cid]["statement"]
        )

    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert RESULT_NOTE.strip() not in result_text
    assert PROCESS_NOTE.strip() not in process_text

    result_text = replace_once(
        result_text,
        "same=1,790（指向1,028个既有 KU）、new=5,012（4,834个身份组）、conflict=8、excluded=100、undecided=5,496。",
        "same=1,792（指向1,029个 KU）、new=5,012（4,834个身份组）、conflict=8、excluded=100、undecided=5,494。",
        "top S3 summary",
    )
    result_text = replace_once(
        result_text,
        "| same | 1,790 | 指向 1,028 个既有 KU |",
        "| same | 1,792 | 指向 1,029 个 KU |",
        "same decision count row",
    )
    result_text = replace_once(
        result_text,
        "| undecided | 5,496 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        "| undecided | 5,494 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        "undecided decision count row",
    )
    result_text = replace_once(
        result_text,
        "| person | 1,017→387 | 1,167／1,079 | 135／944；972 | 3 | 7 | 1,271 |",
        "| person | 1,019→388 | 1,167／1,079 | 135／944；972 | 3 | 7 | 1,269 |",
        "person type summary row",
    )
    result_text = replace_once(
        result_text,
        "| **合计** | **1,790→1,028** | **5,012／4,834** | **372／4,462；4,531** | **8** | **100** | **5,496** |",
        "| **合计** | **1,792→1,029** | **5,012／4,834** | **372／4,462；4,531** | **8** | **100** | **5,494** |",
        "overall S4 type table total row",
    )
    result_anchor = "### S4 按类型登记进度"
    assert result_text.count(result_anchor) == 1
    result_text = result_text.replace(result_anchor, RESULT_NOTE.strip() + "\n\n" + result_anchor, 1)
    process_text = process_text.rstrip() + PROCESS_NOTE + "\n"

    print(f"S3 Carlo Barberini duplicate-subentry dry-run passed: {len(TARGETS)} candidates -> same {KU_ID}")
    print("index/body anchors verified; prior undecided rationale retained; S3 counts updated; no relations or content facts changed")
    if args.dry_run:
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: cand-0196 and cand-0197 now reuse Carlo Barberini person KU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
