from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "new-person:charles-england-ii-of-fba89bfc00"
CANDIDATE_ID = "cand-0656"
KU_ID = "units/persons/charles-ii-of-england"
CARD_PATH = "04-knowledge/units/persons/charles-ii-of-england.md"
RELATIONS = {
    "st-chp7-p178-i21",
    "st-chp7-p195-arlington-introduced-verrio",
    "st-chp7-p195-charlesii-motive",
    "st-chp7-p195-charlesii-no-contemporary-italian-interest",
    "st-chp7-p195-charlesii-recovers-pictures",
    "st-chp7-p195-verrio-employed-by-charlesii",
    "st-chp7-p196-gennari_salary_and_commissions",
    "st-chp7-p196-sea-triumph-description",
}


def evidence(source_file: str, location: str, span: str, summary: str, quote: str) -> dict:
    return {
        "citation": "Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this printing 2006).",
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span.split("; ")[0], "text": quote}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source_file, "source_span": span},
    }


def make_card() -> str:
    chapter_i = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
    chapter_iv = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
    index = "02-sources/03-Index/03-1-Index-MD/C.md"
    fields = {
        "title": "查理二世（Charles II of England）",
        "name_en": "Charles II of England",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            evidence(chapter_i, "第7章；印刷页178；OCR L111", "line 111; print p. 178",
                     "Haskell称 Charles, Prince of Wales 为 Duke of Newcastle 的受教者，并以 the young Prince 指称他。",
                     "The Duke was governor of Charles, Prince of Wales ... He also made an attractive little bust of the young Prince"),
            evidence(chapter_iv, "第7章；印刷页195；OCR L45–46", "lines 45–46; print p. 195",
                     "Haskell称 Charles II 于1660年即位，并记述其试图收回父亲仍可取得的画作。",
                     "After coming to the throne in 1660, Charles II made a few attempts to recover those of his father’s pictures that were still available"),
            evidence(chapter_iv, "第7章；印刷页196；OCR L49–53", "lines 49–53; print p. 196",
                     "Haskell再称 King Charles II，并记述 Verrio 的王室画作及 Gennari 获得国王与王后的委托。",
                     "a large piece with King Charles II in it"),
            evidence(index, "书后索引；C.csv#180", "index entry C.csv#180",
                     "索引以 Charles II of England 汇集第7章印刷页195–196。",
                     "| Charles II of England |  |  |  | 195, 196 |"),
        ],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-charles-ii",
    }
    body = f"""## 内容

### 描述

**中文：** 本卡登记书后索引 C.csv#180 的 Charles II of England。第7章 p.178 称其为 Charles, Prince of Wales，并在同一段落称 young Prince；同章 p.195 明确称 Charles II 于1660年即位，p.196 再称 King Charles II。书内姓名、王号与索引页码共同支持将早年王储称谓和后来的国王称谓归于同一人物。本卡限于原书叙述，不补充书外生平或生卒年。[第7章 p.178](../../../{chapter_i})（L111）；[第7章 pp.195–196](../../../{chapter_iv})（L45–53）；[书后索引](../../../{index})（C.csv#180）

**English:** This card records Charles II of England under index entry C.csv#180. Chapter 7, p.178, calls him Charles, Prince of Wales and refers to him in the same passage as the young Prince; p.195 names Charles II and dates his accession to 1660; p.196 again names King Charles II. The book’s names, royal title, and index page references support treating the earlier princely title and later king as one person. This card follows the book’s account and adds no outside biography or life dates. [Chapter 7, p.178](../../../{chapter_i}) (L111); [Chapter 7, pp.195–196](../../../{chapter_iv}) (L45–53); [Index](../../../{index}) (C.csv#180)

### 名称与身份定位

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Charles II of England | 第7章 pp.195–196；索引 C.csv#180 |
| 早年称谓 | Charles, Prince of Wales；the young Prince | 第7章 p.178 L111 |
| 王号 | Charles II；King Charles II | 第7章 pp.195–196 |
| 中文名性质 | 项目工作译名 | 项目命名 |

### 关系候选

8条直接 S2 关系候选继续待 S6 逐项审查；本卡不将其登记为正式关系：`{", ".join(sorted(RELATIONS))}`。
"""
    frontmatter = yaml.safe_dump(fields, allow_unicode=True, sort_keys=False, width=120)
    return f"---\n{frontmatter}---\n\n{body.strip()}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S3 Charles II identity group as one S4 person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    candidate, alignment = candidate_by_id[CANDIDATE_ID], alignment_by_id[CANDIDATE_ID]
    assert candidate["suggested_type"] == "person" and candidate["canonical_name"] == "Charles II of England"
    assert candidate["index_entry_id"] == "C.csv#180" and candidate["index_page_range"] == "195, 196"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not (ROOT / CARD_PATH).exists()
    assert CARD_PATH not in ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    chapter_i = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md").read_text(encoding="utf-8-sig")
    chapter_iv = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_iv.md").read_text(encoding="utf-8-sig")
    index = (ROOT / "02-sources/03-Index/03-1-Index-MD/C.md").read_text(encoding="utf-8-sig")
    assert "governor of Charles, Prince of Wales" in chapter_i and "young Prince" in chapter_i
    assert "After coming to the throne in 1660, Charles II" in chapter_iv
    assert "King Charles II" in chapter_iv
    assert "| Charles II of England |  |  |  | 195, 196 |" in index
    statement_ids = {
        row["statement_id"] for row in sync.load_statements()
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE_ID in {row.get("subject_candidate_id"), row.get("object_candidate_id")}
    }
    assert statement_ids == RELATIONS

    planned_alignments = [dict(row) for row in alignments]
    planned_alignment = next(row for row in planned_alignments if row.get("candidate_id") == CANDIDATE_ID)
    planned_alignment["ku_id"] = KU_ID
    planned_alignment["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "查理二世",
        "name_en": "Charles II of England",
        "source_task": TASK,
        "card_path": CARD_PATH,
    })
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    old_audit = "审计警告中的4,559条待登记 `decision=new` alignment 行，含4,544条候选决定映射（4,474组）和15条外部身份记录。"
    new_audit = "审计警告中的4,558条待登记 `decision=new` alignment 行，含4,543条候选决定映射（4,473组）和15条外部身份记录。"
    assert old_audit in result_text
    result_text = result_text.replace(old_audit, new_audit, 1)
    result_text += (
        "\n\n### S4 person：Charles II of England 跨章身份组（2026-10-17）\n\n"
        f"候选 `{CANDIDATE_ID}`（C.csv#180）登记至[查理二世人物卡](../units/persons/charles-ii-of-england.md)。第7章 p.178 的 Prince of Wales 称谓与 pp.195–196 的 Charles II 王号及索引主项相接；8条直接关系候选留待 S6，本轮未登记正式关系。"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-charles-ii\"></a>\n\n### S4 person：Charles II of England 跨章身份组（2026-10-17）\n\n"
        f"候选 `{CANDIDATE_ID}` 保持 S3 组 `{GROUP}`，登记至[查理二世人物卡](../../../{CARD_PATH})。第7章 p.178 L111 称 Charles, Prince of Wales，并以 young Prince 指称；同章 p.195 明称 Charles II 于1660年即位，p.196 再称 King Charles II。书后索引 C.csv#180 汇集 p.195–196。将早年王储称谓与后来的国王视为同一人物，依据是书内称谓与索引定位的延续，不扩展为书外生平或生卒年。\n\n"
        f"8条直接 S2 relation_candidate 保持原状：{', '.join(sorted(RELATIONS))}。本轮未写 `relations.csv`，未新增 backlog。S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    card = make_card()
    if args.dry_run:
        print("S4 Charles II person-group dry-run passed")
        print(f"{CANDIDATE_ID} -> {KU_ID}; eight S2 relation candidates remain unchanged")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        print("no files changed")
        return 0

    card_path = ROOT / CARD_PATH
    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE_ID} -> {KU_ID}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
