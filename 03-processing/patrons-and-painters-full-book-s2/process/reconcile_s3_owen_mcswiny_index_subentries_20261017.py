from __future__ import annotations

import argparse
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
KU_ID = "units/persons/owen-mcswiny"
TARGETS = {
    "cand-1467": {
        "index_entry": "M.csv#4",
        "page_range": "291, 292",
        "sub_entry": "and Canaletto",
        "reason": "M.csv#4 subentry “and Canaletto” points to pp.291–292. Chapter 10 p.291 L264 explicitly says McSwiny dealt in Canaletto views and was among the artist’s first foreign patrons; p.292 L267 continues his commissions for English clients. The index heading is McSwiny, Owen.",
    },
    "cand-1468": {
        "index_entry": "M.csv#5",
        "page_range": "291",
        "sub_entry": "and Joseph Smith",
        "reason": "M.csv#5 subentry “and Joseph Smith” points to p.291. Chapter 10 p.291 L264 names McSwiny as Smith’s close friend and business partner; the exact full-name index heading matches the existing same candidate cand-1466.",
    },
    "cand-1471": {
        "index_entry": "M.csv#8",
        "page_range": "288, 289, 290, 291",
        "sub_entry": "series of commemorative paintings of British worthies",
        "reason": "M.csv#8 places the “artists employed” subentry for the commemorative-paintings series on pp.288–291 under McSwiny, Owen. Chapter 10 pp.288–291 describes McSwiny’s instructions, conception and enterprise; existing S2 mentions map these passages to the already same-aligned main candidate cand-1466.",
    },
    "cand-1472": {
        "index_entry": "M.csv#9",
        "page_range": "289n",
        "sub_entry": "series of commemorative paintings of British worthies",
        "reason": "M.csv#9 places the “Venetian artists” subentry of the same series at p.289n under the identical McSwiny, Owen heading. Chapter 10 p.289 describes McSwiny’s scheme and the Venetian painters he employed; the series/person distinction remains intact.",
    },
}

PROCESS_NOTE = """\

### S3 person 复核：Owen McSwiny 的四条索引子项复用既有人物 KU（2026-10-17）

第10章早先复核已将主项 `cand-1466`（M.csv#3）从 `new` 改为 `same` → `units/persons/owen-mcswiny`，并因当时没有各自 S2 mention 映射而将邻接候选 `cand-1467`–`cand-1472` 暂列 `undecided`。本次仅复核人物型子项：`cand-1467`（M.csv#4，“and Canaletto”，pp.291–292）与 `cand-1468`（M.csv#5，“and Joseph Smith”，p.291）对应第10章 p.291 L264–p.292 L267 的同一段落，正文称 McSwiny 与 Joseph Smith合营画作交易并为 Canaletto 的外国赞助人；已有 S2 mentions `m-chp10-p291-mcswiny-commission-open` 等已锚定 McSwiny。`cand-1471`（M.csv#8，artists employed，pp.288–291）与 `cand-1472`（M.csv#9，Venetian artists，p.289n）均是同一 British worthies 纪念画系列下、隶于全名主项的身份子目；第10章 pp.288–291 叙述 McSwiny 的委托指示、系列构想与威尼斯画家，原 S2 提及集中映射在主项 `cand-1466`。四条子项均与已复用主项同名、同页段、同一人物语境相合，因此改为 `same` → `units/persons/owen-mcswiny`，旧暂缓理由逐行保留并补入当前依据。只处理 `person` 候选；作品候选 `cand-1469`、`cand-1470` 及其他对象不随本裁决改型或并入人物。关系候选与 `relations.csv` 不变。
"""

RESULT_NOTE = """\

### S3 person：Owen McSwiny 四条索引子项复用既有人物（2026-10-17）

- `cand-1467`（M.csv#4，and Canaletto，pp.291–292）、`cand-1468`（M.csv#5，and Joseph Smith，p.291）、`cand-1471`（M.csv#8，British worthies series／artists employed，pp.288–291）及 `cand-1472`（M.csv#9，同系列／Venetian artists，p.289n）由 `undecided` 改为 `same` → [Owen McSwiny 人物卡](../units/persons/owen-mcswiny.md)。四条均在同一人物全名主项下；第10章相应页段的正文内容与既有主项 `cand-1466` 的 S2 提及锚点一致。
- 原暂缓理由留存于 alignment 行；本次只复用人物 KU，不将纪念画系列、Canaletto 作品或 Smith 合作关系写成正式关系。`cand-1469`、`cand-1470` 等作品候选保持原决定。
- S3 计数更新为 same=1,802（1,030个 KU）、undecided=5,484；new、S4 与 alignment 行数不变。
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, f"expected exactly one {label} anchor, found {count}"
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve four Owen McSwiny person index subentries to the existing person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    _, manifest = sync.read_csv(MANIFEST_PATH)
    _, mentions = sync.read_csv(TABLES / "mentions.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert all(cid in candidate_by_id and cid in alignment_by_id for cid in TARGETS)
    for cid, info in TARGETS.items():
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert row["decision"] == "undecided" and not row.get("ku_id")
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "McSwiny, Owen"
        assert candidate["index_entry_id"] == info["index_entry"]
        assert candidate["index_page_range"] == info["page_range"]
        assert candidate["sub_entry"] == info["sub_entry"]
    main_candidate = alignment_by_id["cand-1466"]
    assert main_candidate["decision"] == "same" and main_candidate["ku_id"] == KU_ID
    assert any(row.get("ku_id") == KU_ID and row.get("type") == "person" for row in manifest)
    assert (ROOT / "04-knowledge/units/persons/owen-mcswiny.md").exists()

    index_text = (ROOT / "02-sources/03-Index/03-1-Index-MD/M.md").read_text(encoding="utf-8-sig")
    expected_index_rows = [
        "| McSwiny, Owen |  | and Canaletto |  | 291, 292 |",
        "| McSwiny, Owen |  | and Joseph Smith |  | 291 |",
        "| McSwiny, Owen |  | series of commemorative paintings of British worthies | artists employed | 288, 289, 290, 291 |",
        "| McSwiny, Owen |  | series of commemorative paintings of British worthies | Venetian artists | 289n |",
    ]
    assert all(line in index_text for line in expected_index_rows)

    chapter = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    assert "With his close friend, the English business man Joseph Smith" in chapter
    assert "he dealt in pastels by Rosalba Garriera" in chapter and "views by Canaletto" in chapter
    assert "McSwiny’s instructions to them" in chapter
    assert "Yet it ran into difficulties which were almost inseparable from McSwiny’s conception of the paintings" in chapter
    assert "a fine tribute to McSwiny’s enterprise and taste" in chapter
    required_main_mentions = {
        "m-chp10-p288-mcswiny_subjects",
        "m-chp10-p289-note2-mcswiny",
        "m-chp10-p291-mcswiny-commission-open",
    }
    assert required_main_mentions <= {row["mention_id"] for row in mentions if row.get("candidate_id") == "cand-1466"}

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

    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert RESULT_NOTE.strip() not in result_text
    assert PROCESS_NOTE.strip() not in process_text

    result_text = replace_once(
        result_text,
        "same=1,798（指向1,030个 KU）、new=5,012（4,834个身份组）、conflict=8、excluded=100、undecided=5,488。",
        "same=1,802（指向1,030个 KU）、new=5,012（4,834个身份组）、conflict=8、excluded=100、undecided=5,484。",
        "top S3 summary",
    )
    result_text = replace_once(result_text, "| same | 1,798 | 指向 1,030 个 KU |", "| same | 1,802 | 指向 1,030 个 KU |", "same decision count row")
    result_text = replace_once(
        result_text,
        "| undecided | 5,488 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        "| undecided | 5,484 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        "undecided decision count row",
    )
    result_text = replace_once(
        result_text,
        "| person | 1,025→389 | 1,167／1,079 | 135／944；972 | 3 | 7 | 1,263 |",
        "| person | 1,029→389 | 1,167／1,079 | 135／944；972 | 3 | 7 | 1,259 |",
        "person type summary row",
    )
    result_text = replace_once(
        result_text,
        "| **合计** | **1,798→1,030** | **5,012／4,834** | **372／4,462；4,531** | **8** | **100** | **5,488** |",
        "| **合计** | **1,802→1,030** | **5,012／4,834** | **372／4,462；4,531** | **8** | **100** | **5,484** |",
        "overall S4 type table total row",
    )
    result_anchor = "### S4 按类型登记进度"
    assert result_text.count(result_anchor) == 1
    result_text = result_text.replace(result_anchor, RESULT_NOTE.strip() + "\n\n" + result_anchor, 1)
    process_text = process_text.rstrip() + PROCESS_NOTE + "\n"

    print(f"S3 Owen McSwiny subentry dry-run passed: {len(TARGETS)} candidates -> same {KU_ID}")
    print("index/body anchors and existing same candidate verified; old undecided rationales retained; work candidates untouched")
    if args.dry_run:
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: cand-1467, cand-1468, cand-1471, and cand-1472 now reuse Owen McSwiny person KU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
