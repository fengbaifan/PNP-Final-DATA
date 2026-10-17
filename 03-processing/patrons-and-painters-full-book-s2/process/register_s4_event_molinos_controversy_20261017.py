from __future__ import annotations

import argparse
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
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
CID = "cand-5253"
GROUP = "sg3-event-cand-5253"
KU = "units/events/molinos-controversy-jesuits-roman-church"
CARD = f"04-knowledge/{KU}.md"
NAME_ZH = "莫利诺斯与罗马教会、耶稣会的争议"
NAME_EN = "Molinos Controversy involving the Jesuits and Roman Church"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATIONS = [
    "st-chp3-seciv-l48-56-jesuit-opposition",
    "st-chp3-seciv-l48-56-jesuits-and-oliva-implicated",
    "st-chp3-seciv-l48-56-molinos-arrived-1664",
    "st-chp3-seciv-l48-56-roman-church-controversy",
    "st-chp3-seciv-l58-67-reaction-and-power-assertion",
    "st-chp3-seciv-l48-56-oliva-implicated",
    "st-chp3-seciv-l58-67-jesuits-assert-power",
]


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第3章；印刷页81；OCR L52–56",
            "sentence_summary": "Haskell places the controversy in the 1670s, says the trouble began soon after Molinos's arrival in 1664, and describes the Society of Jesus and its General Oliva as centrally implicated.",
            "original_quotes": [
                {"source_span": "lines 52–54", "text": "During the 1670s, when the frescoes were being devised and executed, the Roman Church was shaken by the most serious controversy that had faced it since the Council of Trent."},
                {"source_span": "lines 53–54", "text": "Crucially implicated, at the very centre of the whirlwind, was the Society of Jesus and, in particular, its General, Oliva."},
                {"source_span": "line 54", "text": "The trouble had started soon after the arrival in 1664 of a Spanish priest, Miguel de Molinos"},
                {"source_span": "lines 54–55", "text": "Both of these views—and particularly the latter—were directly opposed to those of the Jesuits, who soon reacted strongly with all the intellectual and political weapons at their command."},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "lines 52–56",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第3章；印刷页82；OCR L59–60",
            "sentence_summary": "Haskell interprets the Jesuit response as partly shaped by concern over influence; the causal account remains explicitly qualified.",
            "original_quotes": [
                {"source_span": "line 59", "text": "This, no doubt, played its part in the violence of their reaction"},
                {"source_span": "line 60", "text": "as often happens in complex disputes, the issues were not wholly clear-cut."},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "lines 59–60",
            },
        },
    ]
    fm = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": PROCESS_REF,
    }
    body = """## 内容

### 描述

**中文：** 本卡记录哈斯克尔第3章所述莫利诺斯争议：作者称罗马教会在1670年代受到重大争议冲击，并说事端在西班牙教士 Miguel de Molinos 于1664年抵达后不久开始。争议围绕每日领圣餐及强调被动默观等教义展开；哈斯克尔称耶稣会及其总会长 Oliva 处于争议中心，并叙述耶稣会对相关教义的反应。书内段落没有给出精确起讫日期；本卡名称是描述性工作名，不声称为历史事件的正式名称。关于反应动机的判断保留作者的 “no doubt” 等限定。

**English:** This card records the Molinos controversy described in Chapter 3. Haskell says the Roman Church was shaken by a major controversy during the 1670s and that the trouble began soon after the Spanish priest Miguel de Molinos arrived in 1664. The dispute concerned doctrines including daily communion and greater emphasis on passive contemplation. Haskell places the Society of Jesus and its General Oliva at the centre and describes the Jesuits' response. The passage gives no precise start or end date; the card title is descriptive, not a claimed formal historical name. Haskell's qualifications, including “no doubt” about the motivations behind the response, are retained.

### 活动性质与时间

- 性质：围绕教义并涉及罗马教会、耶稣会及 Miguel de Molinos 的历史争议。
- 时间：事端据称在 Molinos 1664年抵达后不久开始；Haskell 以1670年代描述争议对罗马教会的影响。原文未给精确起讫日期。
- 证据边界：第81页注2所引研究仅作为 Haskell 的书内引注记录；本卡没有独立查阅该研究。

## 关系与证据

7条直接 S2 `relation_candidate` 留待 S6：`st-chp3-seciv-l48-56-jesuit-opposition`, `st-chp3-seciv-l48-56-jesuits-and-oliva-implicated`, `st-chp3-seciv-l48-56-molinos-arrived-1664`, `st-chp3-seciv-l48-56-roman-church-controversy`, `st-chp3-seciv-l58-67-reaction-and-power-assertion`, `st-chp3-seciv-l48-56-oliva-implicated`, `st-chp3-seciv-l58-67-jesuits-assert-power`。关系方向、端点与历史表述限定仍待逐条裁决；本卡未新增正式关系。
"""
    return f"---\n{yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    candidate = next(row for row in candidates if row["candidate_id"] == CID)
    decision = next(row for row in alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    assert candidate["suggested_type"] == "event"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    assert KU not in manifest_by_id and not (ROOT / CARD).exists()
    assert f"- {CARD}" not in accepted_lines
    assert not any(
        row["type"] == "event" and any(token in (row["canonical_name"] + row["name_en"]).casefold()
                                         for token in ("molinos", "quietism"))
        for row in manifest
    ), "possible existing event KU for the Molinos controversy"

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    for sid in RELATIONS:
        assert sid in statements
        item = statements[sid]
        assert item.get("qualifiers", {}).get("relation_candidate") is True
        assert CID in (item.get("subject_candidate_id"), item.get("object_candidate_id"))

    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") == CID and not row.get("external_source"):
            row["ku_id"] = KU
            row["resolution_note"] = (row.get("resolution_note", "") +
                f" S4 registration: mapped {GROUP} to {KU}; descriptive event label retained.")
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
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-molinos-controversy-event\"></a>\n\n"
        "### S4 event：莫利诺斯争议登记（2026-10-17）\n\n"
        f"`{CID}` 沿用 S3 事件组 `{GROUP}`，登记为 `{KU}`。第3章 p.81–82 将争议放在1670年代，并称事端在 Molinos 1664年抵达后不久开始；"
        "段落以耶稣会、Oliva、罗马教会及教义冲突描述事件，不提供精确起讫日期。卡名为描述性工作名，脚注文献未独立核读。"
        "7条直接 relation_candidate 留待 S6，未新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 event：莫利诺斯争议登记（2026-10-17）\n\n"
        f"`{CID}` 映射至[莫利诺斯与罗马教会、耶稣会的争议](../units/events/molinos-controversy-jesuits-roman-church.md)。"
        "时间范围按 Haskell 的“1664年抵达后不久”及“1670年代”表述保留，未补确切起讫日期。"
        "7条直接关系候选留待 S6，未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 event dry-run passed: group={GROUP}; candidates=1; direct relation candidates={len(RELATIONS)}")
        print("date_scope=1664 arrival plus controversy in the 1670s; exact bounds unknown; formal_relations_added=0")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / CARD).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / CARD).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
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
