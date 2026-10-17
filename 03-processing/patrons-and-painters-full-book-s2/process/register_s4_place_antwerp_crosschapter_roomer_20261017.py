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
TASK_ID = "patrons-and-painters-full-book-s2"
SOURCES = [
    {
        "file": "02-sources/02-Markdown/03_CHP-3_sec_i.md",
        "location": "第3章，印刷页64；OCR L19。",
        "summary": "Haskell称耶稣会士在 Antwerp 出版 Imago primi saeculi 以纪念会规获批百周年。",
        "quote": "Jesuits of Antwerp published to celebrate the centenary",
        "span": "OCR line 19; print p. 64",
        "url": "../../../02-sources/02-Markdown/03_CHP-3_sec_i.md#L19",
        "label": "第3章 p.64",
    },
    {
        "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "location": "第8章，印刷页205；OCR L24。",
        "summary": "Haskell明确称 Gaspar Roomer 于16世纪末出生在 Antwerp，并以约略年代限定该陈述。",
        "quote": "He was born of a good family in Antwerp towards the end of the sixteenth century",
        "span": "OCR line 24; print p. 205",
        "url": "../../../02-sources/02-Markdown/08_CHP-8_sec_i.md#L24",
        "label": "第8章 p.205",
    },
]
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CANDIDATE = "cand-4983"
GROUP = "sg3-place-cand-4983"
KU_ID = "units/places/antwerp"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "安特卫普"
NAME_EN = "Antwerp"
ANCHOR = "s4-place-antwerp-cross-chapter-roomer-20261017"
RELATION_ID = "st-chp8-p205-roomer-origin-residence-gallery"
ROOMER_CANDIDATE = "cand-2223"
ROOMER_KU = "units/persons/gaspar-roomer"


def make_card() -> str:
    source_entries = []
    for item in SOURCES:
        source_entries.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": source_entries,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK_ID}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    link1 = f"[{SOURCES[0]['label']}]({SOURCES[0]['url']})"
    link2 = f"[{SOURCES[1]['label']}]({SOURCES[1]['url']})"
    return f"""---
{fm}---

## 内容

### 地点身份

**中文：** 本卡记录哈斯克尔所称的安特卫普城市地点。第3章称耶稣会士在 Antwerp 出版《Imago primi saeculi》以纪念会规获批百周年；第8章明确称 Gaspar Roomer 于16世纪末出生在 Antwerp。两处分别支持城市名称及其书内地点参照。{link1}（L19）；{link2}（L24）

**English:** This unit records the city Haskell names as Antwerp. Chapter 3 says that the Jesuits of Antwerp published *Imago primi saeculi* to celebrate the centenary of the approval of their statutes; chapter 8 explicitly says that Gaspar Roomer was born in Antwerp toward the end of the sixteenth century. These passages identify the same city in separate source contexts. {link1} (L19); {link2} (L24)

### 对象边界

此 KU 表示城市本身，不与耶稣会机构、出版物或 Gaspar Roomer 合并。本卡不补充坐标、历史边界、行政沿革或现代状态。

## 关系与证据

当前没有已登记的正式关系。S2 关系候选 {RELATION_ID} 记载 Roomer 的出生地点，留待 S6 核对端点与证据；[Gaspar Roomer 人物卡](../persons/gaspar-roomer.md)仅作身份入口。本卡未新增 S5 enrichment。
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
    parser = argparse.ArgumentParser(description="Register Antwerp as the cross-chapter Roomer birthplace endpoint in S4.")
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
    assert candidate.get("suggested_type") == "place"
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert candidate.get("candidate_source_ref", "").endswith("#L19")
    assert not CARD_PATH.exists()
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "place" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English place name already exists"

    for item in SOURCES:
        source_text = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, f"source quote missing: {item['file']}"

    statement = next(row for row in sync.load_statements() if row.get("statement_id") == RELATION_ID)
    assert statement.get("qualifiers", {}).get("relation_candidate") is True
    assert statement.get("subject_candidate_id") == ROOMER_CANDIDATE
    assert statement.get("object_candidate_id") == CANDIDATE
    assert decisions[ROOMER_CANDIDATE].get("ku_id") == ROOMER_KU
    assert (ROOT / f"04-knowledge/{ROOMER_KU}.md").exists()

    planned_alignment = [dict(row) for row in alignments]
    mapped = [row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(mapped) == 1
    mapped[0]["ku_id"] = KU_ID
    mapped[0]["process_ref"] = f"03-processing/{TASK_ID}/process/knowledge.md#{ANCHOR}"
    mapped[0]["resolution_note"] += (
        f" S4 registration: source-backed city group {GROUP} maps to {KU_ID}; "
        "the Roomer birthplace relation remains a candidate for S6."
    )

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "place",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK_ID,
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

### S4 place：安特卫普跨章地点端点（{DATE}）

单成员 S3 地点组 {GROUP}（{CANDIDATE}）映射至[安特卫普地点卡](../../../04-knowledge/{KU_ID}.md)。第3章 p.64 将 Antwerp 作为耶稣会士出版 Imago primi saeculi 的城市，第8章 p.205 又明确记载 Gaspar Roomer 出生于 Antwerp，支持两个章节指向同一城市地点。现有 Roomer 人物端点 {ROOMER_CANDIDATE} 已复用至 {ROOMER_KU}。

关系候选 {RELATION_ID} 保留待 S6 审查；本次只登记城市身份，不写入出生地正式边，不新增 S5 enrichment。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_text = result_text.rstrip() + (
        f"\n\n### S4 place：安特卫普跨章地点端点（{DATE}）\n\n"
        "单成员地点组 cand-4983 登记为安特卫普城市 KU；第3章的出版地点与第8章 Gaspar Roomer 出生地点共同支持跨章对应。"
        "Roomer 已有人物 KU；出生地关系候选留待 S6，未新增正式关系或 S5 补足。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} is the complete single-member S3 place group {GROUP}")
        print(f"verified two source quotations and mapped person endpoint {ROOMER_CANDIDATE} -> {ROOMER_KU}")
        print(f"S6 relation candidate preserved: {RELATION_ID}")
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

