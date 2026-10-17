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
KU_ID = "units/persons/guercino"
CARD_PATH = "04-knowledge/units/persons/guercino.md"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/giovanni-francesco-detto-il-guercino-barbieri_(Dizionario-Biografico)/"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/G.md"
TARGETS = {
    "cand-1258": {
        "index_entry": "G.csv#168",
        "page_range": "xvii, 9, 14, 28, 56, 73, 98, 176, 177, 178, 196, 203, 207, 209, 210, 216, 217, 222, 241, 262",
        "sub_entry": "",
        "reason": "主项 G.csv#168 跨章定位 Guercino (Francesco Barbieri)；第1章 p.14、 第7章及第8章 pp.209–210 的 S2 提及指向同一画家，但原备注因单名形式暂缓。Treccani DBI 条目标题为“BARBIERI, Giovanni Francesco detto il Guercino”，与既有人物 KU 的全名 Giovanni Francesco Barbieri 相合。",
    },
    "cand-1265": {
        "index_entry": "G.csv#175",
        "page_range": "14",
        "sub_entry": "payment",
        "reason": "子项 G.csv#175 将 payment 定位至 p.14；同页第1章 L76–82 讨论 Guercino 按人物收费，且主项 cand-1258 在该段已有 S2 提及锚点。",
    },
    "cand-1274": {
        "index_entry": "G.csv#184",
        "page_range": "14, 209, 210",
        "sub_entry": "work for Don Antonio Ruffo",
        "reason": "子项 G.csv#184 将 Guercino 为 Don Antonio Ruffo 工作定位至 pp.14、209–210；第8章 L68–70 明称 Guercino 与 Ruffo 的画作和逐人物收费往来，主项 cand-1258 的 S2 提及锚点覆盖该段。",
    },
}

EXTERNAL_ALIGNMENT = {
    "candidate_id": "cand-1258",
    "ku_id": KU_ID,
    "external_source": "Treccani DBI",
    "external_id": TRECCANI_URL,
    "decision": "same",
    "accessed_date": "2026-10-17",
    "process_ref": "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-guercino-cross-chapter",
    "resolution_note": "Identity comparison only: DBI volume 6 (1964), entry heading “BARBIERI, Giovanni Francesco detto il Guercino,” directly identifies the full name and epithet corresponding to index form “Guercino (Francesco Barbieri)” and existing KU “Giovanni Francesco Barbieri.” The entry was read on 2026-10-17; no biographical facts were imported.",
}

PROCESS_NOTE = """\

### S3 person 跨章复核：Guercino 索引主项及子项复用既有人物 KU（2026-10-17）

`cand-1258`（G.csv#168，索引全名形式为 Guercino (Francesco Barbieri)，页码横跨章前至第9章）及其索引子项 `cand-1265`（G.csv#175，payment，p.14）、`cand-1274`（G.csv#184，work for Don Antonio Ruffo，pp.14、209–210）此前均列 `undecided`。正文锚点：第1章 p.14 L76–82 记 Guercino 按画中人物收费；第7章 p.176–178 及第8章 pp.209–210 多处以 Guercino 指称同一画家；子项页码与主项及 S2 提及相符。既有 KU 的英文名为 Giovanni Francesco Barbieri，不能仅凭别名相似自动合并，故本次读取 Treccani《意大利人传记辞典》第6卷（1964）同名条目，标题明确为 “BARBIERI, Giovanni Francesco detto il Guercino”（https://www.treccani.it/enciclopedia/giovanni-francesco-detto-il-guercino-barbieri_(Dizionario-Biografico)/；访问日期2026-10-17）；该身份记录将全名与别名直接相连，支持复用 [Guercino 人物卡](../../../04-knowledge/units/persons/guercino.md)。因此三条候选均改为 `same` → `units/persons/guercino`，原未决理由保留于候选行；alignment 中另加一条 Treccani 外部身份记录，绑定主候选 `cand-1258`。该记录只支持人物身份，不据此新增生平事实；本轮不改写任何 S2 关系候选或 `relations.csv`。
"""

RESULT_NOTE = """\

### S3 person：Guercino 跨章身份组复用既有人物（2026-10-17）

- `cand-1258`（G.csv#168，Guercino (Francesco Barbieri)）及子项 `cand-1265`（payment，p.14）、`cand-1274`（work for Don Antonio Ruffo，pp.14、209–210）由 `undecided` 改为 `same` → [乔万尼·弗朗切斯科·巴尔比耶里人物卡](../units/persons/guercino.md)。第1章 p.14、第7章及第8章 pp.209–210 的正文／S2 提及与索引主项、子项定位相符。
- 身份名称差异由 Treccani《意大利人传记辞典》第6卷（1964）条目标题 “BARBIERI, Giovanni Francesco detto il Guercino” 核对，支持索引别名与既有 KU 的同一性；该条目只作为身份依据，不导入生平事实。另存一条 Treccani 外部 identity alignment，绑定主候选 `cand-1258`，访问日期 2026-10-17。
- 三条候选的旧暂缓理由均保留并追加本次依据；不将作品、委托或收费叙述转为正式关系。S3 计数更新为 same=1,798（1,030个 KU）、undecided=5,488；alignment 总行数增至 12,633（其中外部身份记录 227 条）。
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, f"expected exactly one {label} anchor, found {count}"
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the Guercino cross-chapter index identity group to the existing person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    _, manifest = sync.read_csv(MANIFEST_PATH)
    _, mentions = sync.read_csv(TABLES / "mentions.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_alignment = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert all(cid in candidate_by_id and cid in candidate_alignment for cid in TARGETS)
    for cid, info in TARGETS.items():
        candidate = candidate_by_id[cid]
        row = candidate_alignment[cid]
        assert row["decision"] == "undecided" and not row.get("ku_id")
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "Guercino (Francesco Barbieri)"
        assert candidate["index_entry_id"] == info["index_entry"]
        assert candidate["index_page_range"] == info["page_range"]
        assert candidate["sub_entry"] == info["sub_entry"]
    assert any(row.get("ku_id") == KU_ID and row.get("type") == "person" and row.get("name_en") == "Giovanni Francesco Barbieri" for row in manifest)
    assert (ROOT / CARD_PATH).exists()
    assert any(row.get("candidate_id") == "cand-1258" and row.get("external_source") == "Treccani DBI" for row in alignments) is False

    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    expected_index_rows = [
        "| Guercino (Francesco Barbieri) |  |  |  | xvii, 9, 14, 28, 56, 73, 98, 176, 177, 178, 196, 203, 207, 209, 210, 216, 217, 222, 241, 262 |",
        "| Guercino (Francesco Barbieri) |  | payment |  | 14 |",
        "| Guercino (Francesco Barbieri) |  | work for Don Antonio Ruffo |  | 14, 209, 210 |",
    ]
    assert all(line in index_text for line in expected_index_rows)

    chapter1 = (ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md").read_text(encoding="utf-8-sig")
    chapter7 = (ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md").read_text(encoding="utf-8-sig")
    chapter8 = (ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_i.md").read_text(encoding="utf-8-sig")
    assert "Guercino enforced his own practice of charging a certain sum for every figure painted" in chapter1
    assert "another was Guercino" in chapter7
    assert "a fixed rate of 125 ducats for each figure" in chapter8
    assert "work for Don Antonio Ruffo" in index_text
    assert any(row["mention_id"] == "m-chp1-secii-0125" and row["candidate_id"] == "cand-1258" for row in mentions)
    assert any(row["mention_id"] == "m-chp8-p209-036" and row["candidate_id"] == "cand-1258" for row in mentions)
    assert "Dizionario Biografico degli Italiani 6 (1964)" in (ROOT / CARD_PATH).read_text(encoding="utf-8-sig")

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
            + TARGETS[cid]["reason"]
        )

    alignment_numbers = [
        int(row["alignment_id"][4:])
        for row in alignments
        if row.get("alignment_id", "").startswith("aln-") and row["alignment_id"][4:].isdigit()
    ]
    external_row = {field: "" for field in alignment_fields}
    external_row.update(EXTERNAL_ALIGNMENT)
    external_row["alignment_id"] = f"aln-{max(alignment_numbers) + 1:04d}"
    planned_alignment.append(external_row)

    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert RESULT_NOTE.strip() not in result_text
    assert PROCESS_NOTE.strip() not in process_text

    result_text = replace_once(
        result_text,
        "12,632 条：12,406 条候选决定记录及 226 条外部身份记录",
        "12,633 条：12,406 条候选决定记录及 227 条外部身份记录",
        "alignment artifact count",
    )
    result_text = replace_once(
        result_text,
        "same=1,795（指向1,030个 KU）、new=5,012（4,834个身份组）、conflict=8、excluded=100、undecided=5,491。",
        "same=1,798（指向1,030个 KU）、new=5,012（4,834个身份组）、conflict=8、excluded=100、undecided=5,488。",
        "top S3 summary",
    )
    result_text = replace_once(result_text, "| same | 1,795 | 指向 1,030 个 KU |", "| same | 1,798 | 指向 1,030 个 KU |", "same decision count row")
    result_text = replace_once(
        result_text,
        "| undecided | 5,491 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        "| undecided | 5,488 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        "undecided decision count row",
    )
    result_text = replace_once(
        result_text,
        "| person | 1,022→389 | 1,167／1,079 | 135／944；972 | 3 | 7 | 1,266 |",
        "| person | 1,025→389 | 1,167／1,079 | 135／944；972 | 3 | 7 | 1,263 |",
        "person type summary row",
    )
    result_text = replace_once(
        result_text,
        "| **合计** | **1,795→1,030** | **5,012／4,834** | **372／4,462；4,531** | **8** | **100** | **5,491** |",
        "| **合计** | **1,798→1,030** | **5,012／4,834** | **372／4,462；4,531** | **8** | **100** | **5,488** |",
        "overall S4 type table total row",
    )
    result_anchor = "### S4 按类型登记进度"
    assert result_text.count(result_anchor) == 1
    result_text = result_text.replace(result_anchor, RESULT_NOTE.strip() + "\n\n" + result_anchor, 1)
    process_text = process_text.rstrip() + PROCESS_NOTE + "\n"

    print(f"S3 Guercino cross-chapter dry-run passed: {len(TARGETS)} candidates -> same {KU_ID}")
    print(f"Treccani identity record verified and will be appended as {external_row['alignment_id']}")
    print("chapter/index anchors and existing KU verified; prior undecided rationales retained; no relations changed")
    if args.dry_run:
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: cand-1258, cand-1265, and cand-1274 now reuse Guercino person KU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
