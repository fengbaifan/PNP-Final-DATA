from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CARD_REL = "04-knowledge/units/persons/luigi-adami.md"
KU_ID = "units/persons/luigi-adami"
GROUP = "new-person:adami-luigi-02deb86d77"
PROCESS_REF = "S3-S4-full-book-2026-10-17"
CARD_PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-luigi-adami-20261017"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def keep_bom_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def insert_accepted(lines: list[str]) -> list[str]:
    entry = f"- {CARD_REL}"
    assert entry not in lines
    units_index = lines.index("units:")
    claims_index = next((i for i in range(units_index + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])), len(lines))
    insert_at = claims_index
    for i in range(units_index + 1, claims_index):
        if lines[i].startswith("- ") and lines[i][2:] > CARD_REL:
            insert_at = i
            break
    lines.insert(insert_at, entry)
    return lines


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第6章；印刷页158；OCR L16–20",
            "sentence_summary": (
                "Haskell称 Luigi Adami 是几位学术收藏者中较谦逊的一位，记其热衷于收集历史显要人物肖像；"
                "作者还转述 Adami 在1667年写信称刚获得 Lord Essex 与 Francesco Drach 的画像。"
            ),
            "original_quotes": [
                {
                    "source_span": "lines 16–17",
                    "text": "And a third and more modest of these scholarly collectors was a certain Luigi\nAdami. He too was keen to obtain portraits of the most significant men in history.",
                },
                {
                    "source_span": "lines 18–20",
                    "text": "1667 we find him writing that he has just obtained pictures of Lord Essex and‘Francesco\nDrach’ among the English as well as distinguished Germans, Spaniards, French and\nPortuguese.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md",
                "source_span": "lines 16–20; print p. 158",
            },
        },
        {
            "citation": INDEX_CITATION,
            "location": "全书索引 A.csv#13",
            "sentence_summary": "索引以 Adami, Luigi 列出人物主项。",
            "original_quotes": [{"source_span": "A.csv#13", "text": "Adami, Luigi"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
                "source_span": "A.csv#13",
            },
        },
    ]
    fm_data = {
        "title": "路易吉·阿达米（Luigi Adami）",
        "name_en": "Luigi Adami",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": CARD_PROCESS_REF,
    }
    fm = yaml.safe_dump(fm_data, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 第6章称 Luigi Adami 是一位较谦逊的学术收藏者，并记他热衷于收集历史上显要人物的肖像。Haskell转述，Adami在1667年写信称自己刚获得Lord Essex与Francesco Drach的画像；相关国别短语按原文保留，不由此判定个人国籍。中文名为项目工作音译。〔[第6章 p.158](../../../02-sources/02-Markdown/06_CHP-6_sec_iv.md)（L16–20）；[全书索引 A.csv#13](../../../02-sources/03-Index/03-2-Index-CSV/A.csv)〕

**English:** Chapter 6 describes Luigi Adami as a more modest scholarly collector and says that he was keen to obtain portraits of significant historical figures. Haskell reports that Adami wrote in 1667 that he had just obtained portraits of Lord Essex and Francesco Drach; the source's wording about national groups is retained without assigning nationality to either sitter. The Chinese name is a project working transliteration. ([Chapter 6, p. 158](../../../02-sources/02-Markdown/06_CHP-6_sec_iv.md) (lines 16–20); [book index A.csv#13](../../../02-sources/03-Index/03-2-Index-CSV/A.csv).)

## 关系与证据

### 关系记录

目前没有登记在 `relations.csv` 中的正式关系。直接 S2 关系候选 `st-chp6-p158-adami-1667-portrait-acquisitions` 与 `st-chp6-p158-adami-sought-portraits` 保留待 S6 审查。"""
    return f"---\n{fm}---\n\n{body}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Correct the Adami portrait-collection candidate type and register Luigi Adami as a person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    align_by = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    candidate_by = {r["candidate_id"]: r for r in candidates}
    manifest_by = {r["ku_id"]: r for r in manifest}
    statements_bytes = STATEMENTS_PATH.read_bytes()
    lines = statements_bytes.splitlines(keepends=True)
    statements, statement_indices = {}, {}
    for i, raw in enumerate(lines):
        d = json.loads(raw.decode("utf-8-sig"))
        statements[d["statement_id"]] = d
        statement_indices[d["statement_id"]] = i

    assert align_by["cand-0014"]["decision"] == "new" and not align_by["cand-0014"]["ku_id"]
    assert align_by["cand-0015"]["decision"] == "new" and not align_by["cand-0015"]["ku_id"]
    assert sync.get_group(align_by["cand-0014"]["resolution_note"]) == GROUP
    assert sync.get_group(align_by["cand-0015"]["resolution_note"]) == GROUP
    assert candidate_by["cand-0014"]["suggested_type"] == "person"
    assert candidate_by["cand-0015"]["suggested_type"] == "person"
    assert "collection of portraits of distinguished men" in candidate_by["cand-0015"]["sub_entry"]
    assert KU_ID not in manifest_by
    card_path = ROOT / CARD_REL
    assert not card_path.exists()

    source_path = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_iv.md"
    source = source_path.read_text(encoding="utf-8-sig")
    for phrase in ("a certain Luigi", "keen to obtain portraits of the most significant men in history", "just obtained pictures of Lord Essex"):
        assert phrase in source, phrase
    index_path = ROOT / "02-sources/03-Index/03-2-Index-CSV/A.csv"
    index_text = index_path.read_bytes().decode("cp1252")
    assert '"Adami, Luigi",,,,' in index_text
    assert 'collection of portraits of distinguished men' in index_text

    planned_candidates = [dict(r) for r in candidates]
    planned_candidate_by = {r["candidate_id"]: r for r in planned_candidates}
    planned_candidate_by["cand-0015"]["suggested_type"] = ""
    planned_candidate_by["cand-0015"]["detail"] = (
        "S3 correction (2026-10-17): index sub-entry 'collection of portraits of distinguished men' denotes a source-described portrait collection, not Luigi Adami as a second person. "
        "The current taxonomy has no faithful collection type: work denotes identifiable artistic objects and archive denotes documents. Retain as type-undecided and as an S2 object endpoint; do not merge with the person or force it into work/archive/term."
    )
    planned_alignments = [dict(r) for r in alignments]
    planned_align_by = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    collection_alignment = planned_align_by["cand-0015"]
    collection_alignment["decision"] = "undecided"
    collection_alignment["ku_id"] = ""
    collection_alignment["process_ref"] = PROCESS_REF
    collection_alignment["resolution_note"] += (
        " S3 correction (2026-10-17): this index sub-entry denotes the portrait collection, not Luigi Adami. "
        "The prior new-person group membership is retained only as historical rationale; current decision is undecided because the object is independently meaningful but no current KU type faithfully expresses a private collection of artworks. Preserve it as a direct S2 object endpoint pending type review."
    )
    person_alignment = planned_align_by["cand-0014"]
    person_alignment["ku_id"] = KU_ID
    person_alignment["process_ref"] = PROCESS_REF
    person_alignment["resolution_note"] += f" S4 registration ({DATE}): cand-0014 is the person Luigi Adami and maps to {KU_ID}; cand-0015 is a separate type-undecided portrait-collection candidate. Person relation candidates remain pending S6."

    stale_statement_ids = [
        "st-chp6-p158-adami-portrait-of-lord-essex",
        "st-chp6-p158-adami-portrait-of-francesco-drach",
    ]
    planned_statement_lines = list(lines)
    for statement_id in stale_statement_ids:
        d = statements[statement_id]
        q = d["qualifiers"]
        old = q.get("qualification", "")
        assert "type remains unresolved until S3" in old
        q["qualification"] = old.replace(
            "type remains unresolved until S3",
            "S3 now treats this as a distinct portrait-collection candidate with undecided type",
        )
        d["qualifiers"] = q
        original_line = lines[statement_indices[statement_id]]
        eol = b"\r\n" if original_line.endswith(b"\r\n") else (b"\n" if original_line.endswith(b"\n") else b"")
        planned_statement_lines[statement_indices[statement_id]] = json.dumps(d, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + eol

    planned_manifest = [dict(r) for r in manifest]
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "路易吉·阿达米（Luigi Adami）",
        "name_en": "Luigi Adami",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda r: r["ku_id"])
    accepted_lines = read_text(ACCEPTED_PATH).splitlines()
    planned_accepted = insert_accepted(list(accepted_lines))
    card = make_card()
    assert "## 关系与证据" in card and "st-chp6-p158-adami-1667-portrait-acquisitions" in card
    assert "| 字段 | 值 |" not in card

    process_text = read_text(PROCESS_PATH)
    anchor = '<a id="s3-adami-portrait-collection-type-review-20261017"></a>'
    assert anchor not in process_text
    process_text += """

<a id="s3-adami-portrait-collection-type-review-20261017"></a>

### S3 修正：Luigi Adami 人物与肖像收藏索引子目分流（2026-10-17）

`A.csv#13`（`cand-0014`）是 Luigi Adami 人物主项，继续保留 `new-person:adami-luigi-02deb86d77`。`A.csv#14`（`cand-0015`）的子目明确是 “collection of portraits of distinguished men”；第6章 p.158 的两条陈述把该对象作为 Adami 的肖像收藏端点，并另行将 Lord Essex 与 Francesco Drach 的画像列为其中对象。因此 `cand-0015` 不是第二条 Luigi Adami 人物候选，不再与 cand-0014 共用人物组。

项目 taxonomy 的 `work` 表达可辨认艺术作品、构件和设计对象，`archive` 表达文献与档案，`term` 表达概念与术语；当前类型没有忠实表达私人艺术品收藏这一集合对象的类别。故 `cand-0015` 的 suggested_type 清空，S3 决定改为 `undecided`，保留候选、索引子目、S2 端点和原组理由；不将收藏强塞为 person/work/archive/term。两条描述画像所收对象的 statement 资格说明同步为“类型待决”，不新增形式关系。相关关系端点待类型裁决后再进入 S4/S6。

### S4 person：Luigi Adami 人物登记（2026-10-17）

仅登记 `cand-0014`，映射至 `units/persons/luigi-adami`。卡片以第6章 p.158 和索引 A.csv#13 为依据，记录 Haskell 对 Adami 的肖像收藏兴趣及其对1667年书信内容的转述。中文名为项目工作音译。人物的2条直接 S2 关系候选仍待 S6；肖像收藏 `cand-0015` 不进入人物卡映射，也没有写入 `relations.csv`。
"""
    stats = sync.summarize_by_type(planned_candidates, planned_alignments)
    _, totals = sync.build_type_table(stats)
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    result_text += """

### S3 修正与 S4 person：Luigi Adami 与肖像收藏对象分流（2026-10-17）

`cand-0014` 保留为 Luigi Adami 人物并登记为 [Luigi Adami 人物卡](../units/persons/luigi-adami.md)。索引子目 `cand-0015` 指向其肖像收藏，不是第二个人物；现列为 S3 `undecided` 类型待证项，保留为 S2 对象端点，待现有类型能否表达该集合对象获得裁决。人物的2条直接关系候选待 S6；本批未新增正式关系。
"""

    assert len(planned_manifest) == len(manifest) + 1
    assert planned_align_by["cand-0014"]["ku_id"] == KU_ID
    assert planned_align_by["cand-0015"]["decision"] == "undecided" and not planned_align_by["cand-0015"]["ku_id"]
    assert len([r for r in planned_alignments if r.get("decision") == "new" and not r.get("ku_id")]) == totals["pending_members"] + 15
    assert sum(r["decision"] == "undecided" for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")) == 5474

    if args.dry_run:
        print("DRY-RUN OK: cand-0014 remains new person and maps to one KU; cand-0015 is type-undecided and removed from the person group; two stale statement notes updated.")
        print(f"manifest: {len(manifest):,}->{len(planned_manifest):,}; pending groups={totals['pending_groups']:,}; pending candidate mappings={totals['pending_members']:,}; S3 undecided={totals['undecided']:,}")
        return

    card_path.write_bytes(card.encode("utf-8"))
    sync.write_csv(ENTITY_PATH, candidate_fields, planned_candidates)
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    STATEMENTS_PATH.write_bytes(b"".join(planned_statement_lines))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(f"APPLIED: cand-0014 -> {KU_ID}; cand-0015 undecided; manifest={len(planned_manifest):,}; pending groups={totals['pending_groups']:,}")


if __name__ == "__main__":
    main()
