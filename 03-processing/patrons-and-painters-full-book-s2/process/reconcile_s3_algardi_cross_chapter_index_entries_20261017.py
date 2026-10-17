from __future__ import annotations

import argparse
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
KU_ID = "units/persons/alessandro-algardi"
CARD_PATH = "04-knowledge/units/persons/alessandro-algardi.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/A.md"
TARGETS = {
    "cand-0037": {
        "index_entry": "A.csv#38",
        "page_range": "371",
        "sub_entry": "Hercules",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "source_line": 76,
        "source_quote": "a Hercules by Algardi",
        "decision_reason": "第15章 p.371 L76 称 Querini 所藏作品包括一件 Hercules by Algardi；索引 A.csv#38 将“Hercules”列于人物全名 Algardi, Alessandro 下，卡片已区分人物与被归属作品。",
    },
    "cand-0038": {
        "index_entry": "A.csv#39",
        "page_range": "182, 183",
        "sub_entry": "Mazarin invitation to Paris",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "source_line": 157,
        "source_quote": "In 1648 he wrote personally to Algardi",
        "decision_reason": "第7章 p.182 L157 明称 Mazarin 于1648年写信延揽 Algardi；索引 A.csv#39 将该事项列于同一人物全名 Algardi, Alessandro 下。该邀请叙述不被扩写为实际迁居。",
    },
    "cand-0039": {
        "index_entry": "A.csv#40",
        "page_range": "148",
        "sub_entry": "villa for Prince Camillo Pamfili",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
        "source_line": 34,
        "source_quote": "construction by Algardi of one of the most magnificent of all",
        "decision_reason": "第6章 p.148 L30–35 先以全名 Alessandro Algardi 称雕塑家，随后说 Prince Camillo Pamfili 的罗马别墅由 Algardi 负责建造；索引 A.csv#40 将该别墅子项列于同一人物全名下。",
    },
}

PROCESS_NOTE = """\

### S3 person 跨章复核：Alessandro Algardi 子项复用既有人物 KU（2026-10-17）

`cand-0037`（A.csv#38，Hercules，p.371）、`cand-0038`（A.csv#39，Mazarin invitation to Paris，pp.182–183）与 `cand-0039`（A.csv#40，villa for Prince Camillo Pamfili，p.148）原因缺少各自的 `mentions.csv` 映射而列 `undecided`。逐项对照索引子目与正文：第15章 p.371 L76 明称 Querini 所藏 Hercules by Algardi；第7章 p.182 L157 以 Algardi 指称 Mazarin 于1648年尝试延揽的雕塑家；第6章 p.148 L30–35 先给出全名 Alessandro Algardi，继而称 Camillo Pamfili 的罗马别墅由 Algardi 负责建造。三条索引子目均隶属同一全名主项，正文姓名、类型与语境同既有 [Alessandro Algardi 人物卡](../../../04-knowledge/units/persons/alessandro-algardi.md)一致，且跨第6、7、15章相互吻合。因此三候选改为 `same` → `units/persons/alessandro-algardi`。Hercules 仍为人物所涉作品而非本批新作品身份裁决；Mazarin 邀请保留为尝试，不写成迁居事实。原暂缓理由保留在 alignment 行。本轮不改写 S2 关系候选或 relations.csv。
"""

RESULT_NOTE = """\

### S3 person：Alessandro Algardi 三个跨章索引子项复用既有人物（2026-10-17）

- `cand-0037`（A.csv#38，Hercules，p.371）、`cand-0038`（A.csv#39，Mazarin invitation to Paris，pp.182–183）与 `cand-0039`（A.csv#40，villa for Prince Camillo Pamfili，p.148）由 `undecided` 改为 `same` → [Alessandro Algardi 人物卡](../units/persons/alessandro-algardi.md)。第15章 p.371 L76 将 Hercules 归于 Algardi；第7章 p.182 L157 以 Algardi 指称被 Mazarin 延揽的雕塑家；第6章 p.148 L30–35 给出其全名并称 Camillo Pamfili 的罗马别墅由他建造。索引子项均位于同一人物全名下，跨章身份锚点与既有 KU 相符。
- 三条 alignment 保留原暂缓理由并追加各自正文与索引证据；不把 Hercules 合并为人物、不将邀请写成迁居，也不改写正式关系。
- S3 计数更新为 same=1,795（1,030个 KU）、undecided=5,491；new 及 S4 数量不变。
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, f"expected exactly one {label} anchor, found {count}"
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve three cross-chapter Alessandro Algardi index subentries to the existing person KU.")
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
    for cid, info in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "Algardi, Alessandro"
        assert candidate["index_entry_id"] == info["index_entry"]
        assert candidate["index_page_range"] == info["page_range"]
        assert candidate["sub_entry"] == info["sub_entry"]
    assert any(row.get("ku_id") == KU_ID and row.get("type") == "person" and row.get("name_en") == "Alessandro Algardi" for row in manifest)
    assert (ROOT / CARD_PATH).exists()

    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    for cid, info in TARGETS.items():
        chapter = (ROOT / info["source_file"]).read_text(encoding="utf-8-sig")
        assert info["source_quote"] in chapter, cid
        index_row = f"| Algardi, Alessandro |  | {info['sub_entry']} |  | {info['page_range']} |"
        assert index_row in index_text, index_row
    ch6 = (ROOT / TARGETS["cand-0039"]["source_file"]).read_text(encoding="utf-8-sig")
    assert "was replaced by Alessandro Algardi" in ch6
    assert re.sub(r"\s+", " ", ch6).find("construction by Algardi of one of the most magnificent of all Roman villas") >= 0

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        cid = row.get("candidate_id")
        if cid not in TARGETS or row.get("external_source"):
            continue
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["resolution_note"] = (
            row.get("resolution_note", "")
            + " S3 2026-10-17: 原undecided理由保留；复核后改判same并复用已登记KU "
            + KU_ID
            + ". "
            + TARGETS[cid]["decision_reason"]
        )

    result_text = (ROOT / "04-knowledge" / "results" / f"{TASK}.md").read_text(encoding="utf-8-sig")
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert RESULT_NOTE.strip() not in result_text
    assert PROCESS_NOTE.strip() not in process_text

    result_text = replace_once(
        result_text,
        "same=1,792（指向1,029个 KU）、new=5,012（4,834个身份组）、conflict=8、excluded=100、undecided=5,494。",
        "same=1,795（指向1,030个 KU）、new=5,012（4,834个身份组）、conflict=8、excluded=100、undecided=5,491。",
        "top S3 summary",
    )
    result_text = replace_once(result_text, "| same | 1,792 | 指向 1,029 个 KU |", "| same | 1,795 | 指向 1,030 个 KU |", "same decision count row")
    result_text = replace_once(
        result_text,
        "| undecided | 5,494 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        "| undecided | 5,491 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        "undecided decision count row",
    )
    result_text = replace_once(
        result_text,
        "| person | 1,019→388 | 1,167／1,079 | 135／944；972 | 3 | 7 | 1,269 |",
        "| person | 1,022→389 | 1,167／1,079 | 135／944；972 | 3 | 7 | 1,266 |",
        "person type summary row",
    )
    result_text = replace_once(
        result_text,
        "| **合计** | **1,792→1,029** | **5,012／4,834** | **372／4,462；4,531** | **8** | **100** | **5,494** |",
        "| **合计** | **1,795→1,030** | **5,012／4,834** | **372／4,462；4,531** | **8** | **100** | **5,491** |",
        "overall S4 type table total row",
    )
    result_anchor = "### S4 按类型登记进度"
    assert result_text.count(result_anchor) == 1
    result_text = result_text.replace(result_anchor, RESULT_NOTE.strip() + "\n\n" + result_anchor, 1)
    process_text = process_text.rstrip() + PROCESS_NOTE + "\n"

    print(f"S3 Algardi cross-chapter dry-run passed: {len(TARGETS)} candidates -> same {KU_ID}")
    print("all three index subentries and chapter anchors verified; prior undecided rationales retained; no relations changed")
    if args.dry_run:
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: cand-0037, cand-0038, and cand-0039 now reuse Alessandro Algardi person KU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
