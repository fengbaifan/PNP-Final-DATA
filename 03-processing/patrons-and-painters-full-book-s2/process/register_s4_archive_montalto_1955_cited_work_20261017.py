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
CID = "cand-6355"
GROUP = "archive-group-f033e02efa56"
KU = "units/archives/l-montalto-frescoes-palazzo-pamphilj-valmontone-1955"
CARD = f"04-knowledge/{KU}.md"
NAME_ZH = "瓦尔蒙托内潘菲利宫壁画"
NAME_EN = "The Frescoes of Palazzo Pamphilj in Valmontone"
STATEMENTS = [
    "st-chp1-secii-p13-n1-cites-montalto-p287-mola-payment",
    "st-chp1-secii-p13-n3-cites-montalto-p287-mola-materials",
    "st-chp1-secii-p13-n5-cites-montalto-pp287-289-mola-treatment",
    "st-chp1-secii-p7-n3-cites-montalto-p288",
    "st-chp1-secii-p9-n4-cites-montalto-p290",
    "st-chp6-notes-l126-p149-n4-montalto-citation",
]
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCES = [
    {
        "location": "书后书目；OCR L836–837",
        "summary": "Haskell's bibliography identifies L. Montalto's article by its Italian title, journal, year, and page range.",
        "span": "lines 836–837",
        "quote": "Montalto, L.: ‘Gli affreschi del Palazzo Pamphilj in Valmontone’ in Commentari, 1955, pp. 267-302.",
        "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    },
    {
        "location": "第1章；印刷页7；OCR L232–233",
        "summary": "Haskell's note cites Montalto, p. 288; the cited article page was not independently consulted.",
        "span": "lines 232–233",
        "quote": "Montalto, p. 288.",
        "file": "02-sources/02-Markdown/01_CHP-1.md",
    },
    {
        "location": "第1章；印刷页9；OCR L329",
        "summary": "Haskell's note cites Montalto, p. 290; this records a citation locator only.",
        "span": "line 329",
        "quote": "Montalto, p. 290.",
        "file": "02-sources/02-Markdown/01_CHP-1.md",
    },
    {
        "location": "第1章；印刷页13；OCR L506、519、522",
        "summary": "Three notes cite Montalto, pp. 287 and 289. The source processing records the p. 287 OCR spacing correction; the article itself was not consulted.",
        "span": "lines 506, 519, 522",
        "quote": "Montalto, p. 2 8 7; Montalto, p. 287; Montalto, pp. 287 and 289.",
        "file": "02-sources/02-Markdown/01_CHP-1.md",
    },
    {
        "location": "第6章；印刷页149注4；OCR L126",
        "summary": "Haskell's note cites Montalto, pp. 267–302, matching the page range in the bibliography.",
        "span": "line 126",
        "quote": "4 ibid., p. 371, and Montalto, pp. 267-302.",
        "file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
    },
]


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
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
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 本卡登记哈斯克尔书后书目所列的一篇论文，原题为 “Gli affreschi del Palazzo Pamphilj in Valmontone”，刊于 *Commentari*（1955），页267–302。中文显示名是原题的工作译名。哈斯克尔第1章和第6章的注释多次指向该文不同页码。本文本只核实本书的书目著录与引注路径；论文原文及所引页码均未独立查阅，因此不据引注内容补写论文结论。

**English:** This card records the article listed in Haskell's bibliography as “Gli affreschi del Palazzo Pamphilj in Valmontone,” published in *Commentari* (1955), pp. 267–302. The Chinese display name is a working translation of the Italian title. Notes in Chapters 1 and 6 cite different pages of the article. This record verifies only the bibliography entry and citation trail in Haskell's book; neither the article nor its cited pages was independently consulted, so no findings are attributed to it here.

### 书目身份与范围

- 原题：Gli affreschi del Palazzo Pamphilj in Valmontone。
- 作者著录：L. Montalto；现有书内著录仅给出首字母，不据此识别具体作者。
- 刊物与年份：Commentari，1955。
- 页码：书目著录为267–302；哈斯克尔注释对本文的引注定位包括第287、288、289、290页。
- 本卡不把 L. Montalto 与人物候选 `cand-3413` 或任何同姓人物认定为同一身份。

## 关系与证据

6条书内引注路径保留待 S6：`st-chp1-secii-p13-n1-cites-montalto-p287-mola-payment`, `st-chp1-secii-p13-n3-cites-montalto-p287-mola-materials`, `st-chp1-secii-p13-n5-cites-montalto-pp287-289-mola-treatment`, `st-chp1-secii-p7-n3-cites-montalto-p288`, `st-chp1-secii-p9-n4-cites-montalto-p290`, `st-chp6-notes-l126-p149-n4-montalto-citation`。本卡未新增正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_lines = accepted.splitlines()
    candidate = next(row for row in candidates if row["candidate_id"] == CID)
    decision = next(row for row in alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    assert candidate["suggested_type"] == "archive"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    assert sum(
        1 for row in alignment
        if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ) == 1, "unexpected members in the S3 archive identity group"
    assert KU not in manifest_by_id and not (ROOT / CARD).exists()
    assert f"- {CARD}" not in accepted_lines
    assert not any(
        row["type"] == "archive" and "montalto" in (row["canonical_name"] + row["name_en"]).casefold()
        for row in manifest
    ), "possible same-type archive already exists"

    statements = sync.load_statements()
    statement_by_id = {row["statement_id"]: row for row in statements}
    for sid in STATEMENTS:
        assert sid in statement_by_id, f"missing citation statement: {sid}"
        item = statement_by_id[sid]
        assert item.get("qualifiers", {}).get("relation_candidate"), f"not marked as relation candidate: {sid}"
        assert CID in item.get("qualifiers", {}).get("mentioned_candidate_ids", []), f"candidate not anchored: {sid}"

    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") == CID and not row.get("external_source"):
            row["ku_id"] = KU
            row["resolution_note"] = (row.get("resolution_note", "") +
                f" S4 registration: mapped {GROUP} to {KU}; identity limited to the cited bibliographic work.")
    planned_manifest = [dict(row) for row in manifest]
    planned_manifest.append({
        "ku_id": KU,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-montalto-1955-archive\"></a>\n\n"
        "### S4 archive：L. Montalto 1955 年论文书目身份登记（2026-10-17）\n\n"
        f"`{CID}` 沿用 S3 `new` 组 `{GROUP}`，映射至 `{KU}`。书后书目给出原题、刊物、年份与页码；"
        "第1章与第6章注释多次引用该文。卡片仅确认 Haskell 书内的书目身份及引注路径，论文和所引页码未独立查阅；"
        "作者只保留书目中的首字母，不与 `cand-3413` 等人物候选合并。6条 citation relation_candidate 留待 S6，未新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 archive：L. Montalto 1955 年论文登记（2026-10-17）\n\n"
        f"`{CID}` 映射至 [《瓦尔蒙托内潘菲利宫壁画》](../units/archives/l-montalto-frescoes-palazzo-pamphilj-valmontone-1955.md)。"
        "书内书目身份及跨章注释引注可追溯；原文与引注页未独立查阅，作者身份不扩展为具名人物。"
        "6条直接 citation relation_candidate 留待 S6。"
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
        print(f"S4 archive dry-run passed: group={GROUP}; candidates=1; citation relation candidates={len(STATEMENTS)}")
        print("source_access=Haskell bibliography and notes only; author identity unresolved; no formal relations added")
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
        f"applied: group={GROUP}; candidates=1; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
