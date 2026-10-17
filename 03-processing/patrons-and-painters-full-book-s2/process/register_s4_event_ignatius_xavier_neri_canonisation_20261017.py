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
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CANDIDATE = "cand-4980"
GROUP = "sg3-event-cand-4980"
KU_ID = "units/events/gregory-xv-canonisation-ignatius-francis-xavier-philip-neri"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "格列高利十五世时期依纳爵、方济各·沙勿略与腓力·内利册封事件"
NAME_EN = "Canonisation of Ignatius, Francis Xavier, and Philip Neri under Gregory XV"
ANCHOR = "s4-event-gregory-xv-canonisation-20261017"
RELATIONS = [
    "st-chp3-seci-l16-24-canonisation-occasion-paintings",
    "st-chp3-seci-l35-43-canonization-volume-citation",
    "st-chp3-seci-l35-43-redig-de-campos-citation",
]
QUOTES = [
    "to decree the canonisation of the two great Jesuits, Ignatius and Francis Xavier, and the founder of the Oratorians Philip Neri",
    "the occasion was followed by spectacular ceremonies",
]


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 64.",
                "location": "第3章，印刷页64；OCR L17–18。",
                "sentence_summary": (
                    "Haskell称教皇 Gregory XV 颁令册封 Ignatius、Francis Xavier 与 Philip Neri；"
                    "该册封时机之后举行庆典，并与委托 Van Dyck 绘制两位耶稣会圣人的画作相接。"
                ),
                "original_quotes": [
                    {
                        "source_span": "OCR line 18; print p. 64",
                        "text": quote,
                    }
                    for quote in QUOTES
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "OCR lines 17–18; printed p. 64",
                },
            }
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "[第3章 p.64](../../../02-sources/02-Markdown/03_CHP-3_sec_i.md#L18)"
    return f"""---
{fm}---

## 内容

### 事件身份与范围

**中文：** 本卡记录哈斯克尔叙述的格列高利十五世颁令册封依纳爵、方济各·沙勿略与腓力·内利这一事件。作者称该册封时机之后举行盛大庆典，并接着提到委托 Van Dyck 为两位耶稣会圣人绘制画作。该段未给出册封的精确日期或庆典地点；本卡不补入外部日期、地点或仪式细节。{source_link}（L17–18）

**English:** This unit records Haskell’s account of Gregory XV decreeing the canonisation of Ignatius, Francis Xavier, and Philip Neri. Haskell says spectacular ceremonies followed the occasion and then mentions a commission to Van Dyck for paintings of the two Jesuit saints. The passage gives no exact date for the decree or location for the ceremonies; this card adds no external date, location, or ceremonial detail. {source_link} (L17–18)

### 与相邻事件的边界

该事件不同于紧接其后叙述的 Urban VIII 于 1639、1640 年访问耶稣堂、参加耶稣会会规获批百周年庆祝的事件候选 cand-4981；本卡不合并两者。两幅祭坛画的作品身份及归属争议也不并入本事件对象。

## 关系与证据

当前没有已登记的正式关系。S2 关系候选 {", ".join(RELATIONS)} 留待 S6 逐条核对。作品候选 cand-4977 仍为 undecided；人物候选 cand-1309 仍为 undecided。本次事件身份登记不解决这些对象的身份或关系，也不将原文提及升级为正式关系。
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
    parser = argparse.ArgumentParser(description="Register the Gregory XV canonisation event in S4.")
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
    candidate = candidate_map[CANDIDATE]
    target = decisions[CANDIDATE]
    assert candidate.get("suggested_type") == "event"
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert candidate.get("candidate_source_ref", "").endswith("#L18")
    assert not CARD_PATH.exists()
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "event" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English event identity already exists"

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    assert all(" ".join(quote.split()) in source_text for quote in QUOTES)
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    for sid in RELATIONS:
        statement = statements[sid]
        assert statement.get("qualifiers", {}).get("relation_candidate") is True
        assert CANDIDATE in {
            statement.get("subject_candidate_id"),
            statement.get("object_candidate_id"),
            *statement.get("qualifiers", {}).get("mentioned_candidate_ids", []),
        }
    assert decisions["cand-1309"].get("decision") == "undecided"
    assert decisions["cand-4977"].get("decision") == "undecided"
    assert decisions["cand-4981"].get("decision") == "new"

    planned_alignment = [dict(row) for row in alignments]
    mapped = [row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(mapped) == 1
    mapped[0]["ku_id"] = KU_ID
    mapped[0]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    mapped[0]["resolution_note"] += (
        f" S4 registration: source-backed event group {GROUP} maps to {KU_ID}; "
        "exact date/location and distinct person/work identities remain outside this registration."
    )

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "event",
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

### S4 event：格列高利十五世时期的册封事件（{DATE}）

单成员 S3 事件组 {GROUP}（{CANDIDATE}）登记至[册封事件卡](../../../04-knowledge/{KU_ID}.md)。第3章 p.64 称 Gregory XV 颁令册封 Ignatius、Francis Xavier 与 Philip Neri，并称其后举行庆典；原段未给出精确日期或庆典地点，本卡不补写。

该事件与同段随后提到的 1639–1640 年耶稣会会规获批百周年庆典候选 cand-4981 分开；Van Dyck 绘画候选 cand-4977 仍为 undecided。三条关联 S2 关系候选 {", ".join(RELATIONS)} 留待 S6。cand-1309 的 Ignatius 人物身份保持 undecided；本次不为未决人物或画作建立关系或合并身份。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_text = result_text.rstrip() + (
        f"\n\n### S4 event：格列高利十五世册封事件（{DATE}）\n\n"
        "单成员事件组 cand-4980 登记为 source-backed KU；日期与地点按原书未说明处理，"
        "不与 1639–1640 年耶稣会会规获批百周年庆典合并。3条关系候选留待 S6，cand-4977 作品身份与 cand-1309 人物身份继续待证。"
        "未新增正式关系或 S5 补足。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} is the complete single-member S3 event group {GROUP}")
        print(f"verified {len(QUOTES)} source quotations and {len(RELATIONS)} S2 relation candidates")
        print("retained undecided endpoints: cand-1309, cand-4977; separate event cand-4981 remains new")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; accepted path unique")
        print("planned writes: one bilingual event card, accepted.yml, ku-manifest.csv, one alignment mapping, process record, result")
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

