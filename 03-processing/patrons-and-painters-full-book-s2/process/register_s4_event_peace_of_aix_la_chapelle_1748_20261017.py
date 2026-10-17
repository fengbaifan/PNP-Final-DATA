from __future__ import annotations

import argparse
import csv
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
ENTITY_PATH = TABLES / "entity-candidates.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CID = "cand-0019"
GROUP = "sg3-event-cand-0019"
KU = "units/events/peace-of-aix-la-chapelle-1748"
CARD = f"04-knowledge/{KU}.md"
NAME_ZH = "艾克斯-拉夏贝尔和约（1748）"
NAME_EN = "Peace of Aix-la-Chapelle (1748)"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
STATEMENT_ID = "st-chp10-p318-peace-aix-as-starting-point-for-new-spirit-in-italy"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
QUOTE = "then, the peace of Aix-la-Chapelle in 1748 is usually taken as the starting-point for a new spirit in Italy."


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_card() -> str:
    source = {
        "citation": BOOK_CITATION,
        "location": "第10章；印刷页317–318；OCR L133–134",
        "sentence_summary": (
            "Haskell acknowledges earlier achievements and says that the 1748 Peace of Aix-la-Chapelle is usually "
            "taken as the starting point for a new spirit in Italy. This is a reported periodization, not a claim "
            "that Enlightenment ideas first appeared then or that the treaty caused them."
        ),
        "original_quotes": [
            {"source_span": "line 133; print p.317", "text": "Although much had been achieved before"},
            {"source_span": "line 134; print p.318", "text": QUOTE},
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": "lines 133–134; print pp.317–318",
        },
    }
    front_matter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "evidence_status": "source_backed",
        "sources": [source],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    body = """## 内容

### 描述

**中文：** 哈斯克尔先承认此前已有重要成就，继而称1748年的艾克斯-拉夏贝尔和约常被视为意大利出现一种“新精神”的起点。这是作者转述的断代惯例，不表示启蒙思想此前不存在，也不主张该和约直接造成了意大利思想变化。

**English:** Haskell first acknowledges significant earlier achievements, then says that the 1748 Peace of Aix-la-Chapelle is usually taken as the starting point for a “new spirit” in Italy. This records a reported periodization; it does not imply that Enlightenment ideas were absent before then or that the treaty directly caused intellectual change in Italy.

### 基本信息

- **事件性质：** 和约；本书在此处将其作为一种历史断代的参照。
- **时间：** 1748年。引文未给签订的具体日期。
- **地点：** 该处以和约名称指称事件，未进一步说明签订地点。
- **参与者与条款：** 本段未列参与方、签约者或具体条款，本卡不补入。
- **来源解释：** “常被视为意大利出现一种新精神的起点”是 Haskell 对通行断代说法的归述；句中的“usually taken”保留其限定。

## 关系与证据

### 来源

- [Francis Haskell, *Patrons and Painters*](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)，第10章，印刷页317–318，L133–134。跨页上下文分别写有“Although much had been achieved before”及“then, the peace of Aix-la-Chapelle in 1748 is usually taken as the starting-point for a new spirit in Italy.”

### 关系审查

- 相关 S2 断言为作者对意大利思想变化的断代判断，标记为非关系候选；没有据此建立事件与“新精神”之间的因果关系。
- 本卡只收录该书段落提供的事件标识和年份；未独立核对和约文本或其他研究。
"""
    return "---\n" + yaml.safe_dump(front_matter, allow_unicode=True, sort_keys=False, width=110) + "---\n\n" + body


def main():
    parser = argparse.ArgumentParser(description="Register the 1748 Peace of Aix-la-Chapelle event in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = read_csv(ENTITY_PATH)
    alignment_fields, alignment = read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    candidate = next(row for row in candidates if row["candidate_id"] == CID)
    decision = next(row for row in alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert candidate["suggested_type"] == "event"
    assert candidate["canonical_name"] == "Aix-la-Chapelle, Peace of"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    assert KU not in manifest_by_id and not (ROOT / CARD).exists()
    assert not any(
        row["type"] == "event" and "aix-la-chapelle" in (row["ku_id"] + row["canonical_name"] + row["name_en"]).casefold()
        for row in manifest
    ), "possible existing Peace of Aix-la-Chapelle event KU"
    assert f"- {CARD}" not in accepted_lines

    statements = sync.load_statements()
    statement = next(row for row in statements if row["statement_id"] == STATEMENT_ID)
    assert statement["subject_candidate_id"] == CID
    assert statement["qualifiers"]["relation_candidate"] is False
    assert "1748" in statement["qualifiers"]["claim"]
    source_text = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    assert "Although much had been achieved before" in source_text
    assert "then, the peace of Aix-la-Chapelle in 1748 is usually taken" in source_text

    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") == CID and not row.get("external_source"):
            row["ku_id"] = KU
            row["resolution_note"] += (
                f" S4 registration: mapped {GROUP} to {KU}; source card preserves the author's 'usually taken' "
                "periodization and does not infer causation or a first appearance of Enlightenment thought."
            )

    planned_manifest = [dict(row) for row in manifest]
    planned_manifest.append({
        "ku_id": KU,
        "type": "event",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_anchor = "<a id=\"s4-aix-la-chapelle-peace-1748\"></a>"
    process_entry = (
        f"\n\n{process_anchor}\n\n### S4 event：1748年艾克斯-拉夏贝尔和约（2026-10-17）\n\n"
        f"`{CID}` 沿用 S3 事件组 `{GROUP}`，登记为 `{KU}`。第10章跨 p.317–318 承认此前已有成就，称1748年和约“usually taken”作为意大利出现新精神的起点；"
        "卡片将此保留为 Haskell 所述的断代判断，不写成启蒙思想的唯一开端或和约的因果效果。来源未列参与方、条款或签订具体日期，本次未补入。"
        "对应 S2 断言不是关系候选，没有新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    assert process_anchor not in process_text
    process_text += process_entry
    result_text += (
        "\n\n### S4 event：1748年艾克斯-拉夏贝尔和约\n\n"
        f"`{CID}` 映射至[艾克斯-拉夏贝尔和约（1748）](../units/events/peace-of-aix-la-chapelle-1748.md)。"
        "卡片保留 Haskell 对其作为意大利“新精神”断代起点的限定表述；不推导启蒙思想的首次出现或因果关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    planned_accepted = list(accepted_lines)
    planned_accepted.insert(insert_at, f"- {CARD}")

    if args.dry_run:
        print(f"S4 event dry-run passed: group={GROUP}; candidates=1; statement={STATEMENT_ID}")
        print("source=Haskell, ch.10, pp.317-318; event year=1748; treaty parties/terms/date not specified here")
        print("author's periodization retained; relation_candidate=false; formal_relations_added=0")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / CARD).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / CARD).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=1; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
