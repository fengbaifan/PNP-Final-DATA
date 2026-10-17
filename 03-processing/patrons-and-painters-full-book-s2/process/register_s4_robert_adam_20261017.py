from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
GROUP = "new-person:adam-robert-145d4691c8"
KU_ID = "units/persons/robert-adam"
CARD_REL = "04-knowledge/units/persons/robert-adam.md"
CARD_PATH = ROOT / "04-knowledge" / "units" / "persons" / "robert-adam.md"
CANDIDATES = ("cand-0012", "cand-0013")
RELATION_STATEMENTS = {
    "st-chp10-p302-note1-letter-locator",
    "st-chp13-p336-adam-authored-diocletian-palace-book",
    "st-chp13-p336-adam-entrusted-book-sale-to-albrizzi",
}
DIRECT_STATEMENTS = RELATION_STATEMENTS | {"st-chp10-p310-note1-adam-visit-citations"}
ITEM = {
    "ku_id": KU_ID,
    "card_rel": CARD_REL,
    "type": "person",
    "name_zh": "罗伯特·亚当",
    "name_en": "Robert Adam",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def card_text() -> str:
    sources = [
        {
            "citation": BOOK,
            "location": "第10章；印刷页301；OCR L382–389",
            "sentence_summary": "Haskell 将 Robert Adam 列在曾受 Consul Smith 接待的英国访客中；本句不确定关系的性质或持续时间。",
            "original_quotes": [{"source_span": "p.301 访客列举", "text": "Robert Adam"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "lines 382–389; print p. 301",
            },
        },
        {
            "citation": BOOK,
            "location": "第10章；印刷页302；注1；OCR L595",
            "sentence_summary": "注释称一封 James 致 Robert Adam 的信写于 1760-08-20，并感谢 John Fleming 提供传阅副本；原信和副本未独立查阅。",
            "original_quotes": [{"source_span": "note 1", "text": "Letter from James to Robert Adam dated 20 August 1760."}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 595; print p. 302",
            },
        },
        {
            "citation": BOOK,
            "location": "第10章；印刷页310；注1；OCR L630",
            "sentence_summary": "Haskell 转述 Robert Adam 于 1757 年访问 Consul Smith 在 Mogliano 的住所并赞赏其小幅名画收藏；所引 Orlandi 与 Fleming 文献未独立查阅。",
            "original_quotes": [{"source_span": "note 1", "text": "In 1757 Robert Adam visited Consul Smith at Mogliano"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 630; print p. 310",
            },
        },
        {
            "citation": BOOK,
            "location": "第13章；印刷页336；OCR L48",
            "sentence_summary": "Haskell 称 Robert Adam 1761 年途经威尼斯时托付 Albrizzi 代售一本关于 Diocletian's palace 的书；原文未说明 Albrizzi 实际出版或印制该书。",
            "original_quotes": [{
                "source_span": "line 48",
                "text": "Robert Adam realised when he passed through in 1761 and entrusted Albrizzi with the sale of his book on Diocletian\u2019s palace.",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "source_span": "line 48; print p. 336",
            },
        },
        {
            "citation": BOOK,
            "location": "第19章附录5；印刷页392；OCR L128",
            "sentence_summary": "Haskell 引述 James 在 1760-08-20 致 Robert Adam 的信中对 Joseph Smith 财务状况的判断；该判断不是 Smith 后来破产的证明，信件和 Fleming 的出版物未独立查阅。",
            "original_quotes": [{"source_span": "line 128", "text": "On 20 August 1760 James wrote to Robert Adam of Smith"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
                "source_span": "line 128; print p. 392",
            },
        },
    ]
    fm = yaml.safe_dump(
        {
            "title": f"{ITEM['name_zh']}（{ITEM['name_en']}）",
            "name_en": ITEM["name_en"],
            "type": "person",
            "evidence_status": "source_backed",
            "sources": sources,
            "created": "2026-10-17",
            "updated": "2026-10-17",
            "process_ref": f"03-processing/{TASK}/process/knowledge.md",
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    p301 = "[第10章 p.301](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L382–389）"
    p302 = "[第10章 p.302 注1](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L595）"
    p310 = "[第10章 p.310 注1](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L630）"
    p336 = "[第13章 p.336](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L48）"
    p392 = "[附录5 p.392](../../../02-sources/02-Markdown/19_CHP-19Appendix.md)（L128）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记书中以 Robert Adam 指称的同一来源内人物。第10章将他列入曾受 Consul Smith 接待的英国访客；第13章记述他于1761年途经威尼斯时托 Albrizzi 代售一本关于戴克里先宫的书。第10章注释和第19章附录还提到 James 致 Robert 的信；信件及所引出版物未独立查阅。原文没有给出该书确切题名或实际出版情况，本卡不补充书外履历。{p301}；{p336}；{p302}；{p392}

**English:** This card records the same source-local person named Robert Adam. Chapter 10 lists him among the English visitors welcomed by Consul Smith; Chapter 13 says that during a passage through Venice in 1761 he entrusted Albrizzi with the sale of a book on Diocletian's palace. A Chapter 10 note and Appendix 5 also refer to a letter from James to Robert; neither the letter nor the cited publications was independently consulted. The book's exact title and publication status are not established, and no biography beyond these passages is added. {p301}; {p336}; {p302}; {p392}

### 名称与身份边界

- 两条 S1 索引候选 `cand-0012` 与 `cand-0013` 由 S3 归入同一人物组 `{GROUP}`；第10章和第13章正文均明称 Robert Adam。此卡只据书内全名及跨章语境登记，不以外部生平补充身份事实。
- 第10章 p.310 注1报告1757年访问并转述对收藏的评价；Haskell 所引 Orlandi 与 Fleming 页码未独立查阅。该项在 S2 中标为非关系陈述，作为语境证据保留，不升格为正式关系。{p310}

### 关系与证据

以下3条关系候选留待 S6；本卡未新增正式关系：

- `st-chp10-p302-note1-letter-locator`：James → Robert Adam；来源仅为书中注释所给信件定位，原信与副本未查阅。
- `st-chp13-p336-adam-authored-diocletian-palace-book`：Robert Adam → `cand-10002`；书名、作品身份及版本尚待对应候选裁决。
- `st-chp13-p336-adam-entrusted-book-sale-to-albrizzi`：Robert Adam → `cand-0025`；原文只说托付代售，不证明出版或印制。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Robert Adam identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_rows = [candidate_by_id[candidate_id] for candidate_id in CANDIDATES]
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert [row["canonical_name"] for row in candidate_rows] == ["Adam, Robert", "Adam, Robert"]
    assert all(row["suggested_type"] == "person" for row in candidate_rows)
    assert all(alignment_by_id[candidate_id]["decision"] == "new" and not alignment_by_id[candidate_id].get("ku_id") for candidate_id in CANDIDATES)
    assert all(sync.get_group(alignment_by_id[candidate_id].get("resolution_note", "")) == GROUP for candidate_id in CANDIDATES)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert not CARD_PATH.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == "robert adam" for row in manifest)

    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if any(candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id")) for candidate_id in CANDIDATES)
    ]
    assert {row["statement_id"] for row in direct} == DIRECT_STATEMENTS
    relation_ids = {
        row["statement_id"] for row in direct
        if row.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert relation_ids == RELATION_STATEMENTS

    ch10 = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    ch13 = (ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md").read_text(encoding="utf-8-sig")
    appendix = (ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md").read_text(encoding="utf-8-sig")
    assert "Robert Adam were aU welcomed by him." in ch10
    assert "Letter from James to Robert Adam dated 20 August 1760." in ch10
    assert "In 1757 Robert Adam visited Consul Smith at Mogliano" in ch10
    assert "Robert Adam realised when he passed through in 1761 and entrusted Albrizzi with the sale of his book on Diocletian\u2019s palace." in ch13
    assert "On 20 August 1760 James wrote to Robert Adam of Smith" in appendix

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for candidate_id in CANDIDATES:
        planned_by_id[candidate_id]["ku_id"] = KU_ID
        planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": ITEM["type"],
        "canonical_name": ITEM["name_zh"],
        "name_en": ITEM["name_en"],
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4 person：Robert Adam 跨章身份组登记（2026-10-17）\n\n"
        f"候选 `{CANDIDATES[0]}`（A.csv#11）与 `{CANDIDATES[1]}`（A.csv#12）保持 S3 人物组 `{GROUP}`，"
        f"共同映射至[Robert Adam 人物卡](../../../04-knowledge/units/persons/robert-adam.md)；同组仅登记一个 KU。"
        "第10章 p.301、302、310与第19章附录5 p.392多处出现同名；第13章 p.336再次以全名指称该人并记述1761年途经威尼斯时托 Albrizzi 代售其书。"
        "章节称谓和日期语境相容，原书关系叙述与被引信件/文献保持各自来源限定；未作外部身份补足。"
        "直接相连的3条 S2 relation_candidate 留待 S6：James 致 Robert 的信、Robert 的书对象、以及托 Albrizzi 代售。"
        "p.310 注1有关1757年访问与收藏评价的 statement 标为非关系陈述；不新增 `relations.csv` 正式边。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Robert Adam 跨章身份组（2026-10-17）\n\n"
        f"`{CANDIDATES[0]}`、`{CANDIDATES[1]}` 共映射至[Robert Adam 人物卡](../units/persons/robert-adam.md)，"
        "依据第10、13章及附录中的跨章全名锚点。3条直接关系候选留待 S6；p.310 访问叙述保留为非关系陈述。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    if args.dry_run:
        print(f"S4 Robert Adam dry-run passed: {CANDIDATES[0]}, {CANDIDATES[1]} -> {KU_ID}")
        print("cross-chapter full-name evidence: Chapters 10 and 13, plus Appendix 5")
        print(f"direct statements={len(direct)}; relation candidates={len(relation_ids)}; formal relations added=0")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("group membership, source excerpts, existing KU check, and destination uniqueness passed; no files changed")
        return 0

    CARD_PATH.write_text(card_text(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATES[0]}, {CANDIDATES[1]} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
