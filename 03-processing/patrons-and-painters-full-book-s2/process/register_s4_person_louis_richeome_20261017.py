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
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATE_ID = "cand-2192"
GROUP = "new-person:louis-richeome-355a5b7c18"
KU_ID = "units/persons/louis-richeome"
CARD_REL = "04-knowledge/units/persons/louis-richeome.md"
NAME_ZH = "路易·里肖姆"
NAME_EN = "Louis Richeôme"
ANCHOR = "s4-person-louis-richeome-20261017"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCES = (
    {
        "location": "第3章；印刷页67；L30–L31",
        "source_span": "L30-L31; print p. 67",
        "quote": "In 1611 a French\nJesuit Louis Richeôme wrote a book",
        "summary_cn": "第3章称 Louis Richeôme 为法国耶稣会士，并说他于1611年写作一部献给Aquaviva的书；书名在该段未给出。",
        "summary_en": "Chapter 3 identifies Louis Richeôme as a French Jesuit and says he wrote a book dedicated to Aquaviva in 1611; the passage does not give the book's title.",
    },
    {
        "location": "第3章；印刷页68；L35–L36",
        "source_span": "L35-L36; print p. 68",
        "quote": "But Richeôme’s was a last, lonely voice from the harsher days of the\nCounter Reformation",
        "summary_cn": "第3章续段再次以Richeôme指称该人，并由Haskell将其论点描述为较严峻反宗教改革时期的“last, lonely voice”；这是作者评价，不作独立人物事实。",
        "summary_en": "The continuation refers to him as Richeôme and characterizes his argument as a “last, lonely voice” from a harsher Counter-Reformation period; this is Haskell's assessment, not an independently established biographical fact.",
    },
)
EXPECTED_RELATION_IDS = {
    "st-chp3-secii-l19-31-richeome-wrote-book-1611",
    "st-chp3-secii-l33-38-haskell-calls-richeome-last-lonely-voice",
    "st-chp3-secii-l33-38-haskell-says-simplicity-doctrine-unlikely-under-urban",
    "st-chp3-secii-l33-38-richeome-focused-devotion-on-fresco-subject",
    "st-chp3-secii-l33-38-richeome-rejected-extravagant-ornament",
}


def make_card() -> str:
    sources = []
    for item in SOURCES:
        sources.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary_cn"],
            "original_quotes": [{"source_span": item["source_span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": item["source_span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[第3章书内来源](../../../{SOURCE_FILE})"
    relation_lines = "\n".join(f"- `{statement_id}`" for statement_id in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** Haskell称 Louis Richeôme 为法国耶稣会士，并记述他于1611年写作一部献给 Aquaviva、涉及 S. Andrea 与 S. Vitale 绘画的书。第3章后续再次以 Richeôme 指称该人。此卡只登记书内具名人物身份；作者对其观点的概括和评价继续按原书发言者、语气及限定理解，不据此补写生卒或完整生平。{source_link}

**English:** Haskell identifies Louis Richeôme as a French Jesuit and says that in 1611 he wrote a book dedicated to Aquaviva concerning paintings in S. Andrea and S. Vitale. The continuation refers to the same person as Richeôme. This card registers only the named person in the book; Haskell's summaries and assessments of his views retain their original speaker and qualification, and no dates or full biography are added. {source_link}

### 姓名与身份

- 书中全名：Louis Richeôme。{source_link}
- 中文显示名：“路易·里肖姆”为工作音译，不声明为已核定通行译名。{source_link}
- 书内身份：法国耶稣会士；Haskell称其于1611年写作一部献给Aquaviva的书。原书此处未列书名。{source_link}

## 关系与证据

### 关系记录

当前没有新增正式关系。以下5条S2关系候选均保留于`book-statements.jsonl`，待S6逐条核对关系类型、语境和端点；本卡不将其改写为正式关系：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-supported Louis Richeôme person group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    candidate = candidate_by_id[CANDIDATE_ID]
    alignment = alignment_by_id[CANDIDATE_ID]
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Richeôme, Louis"
    assert candidate.get("index_entry_id") == "Q-R.csv#119"
    assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    assert len(manifest_targets) <= 1
    registered = bool(manifest_targets) and alignment.get("ku_id") == KU_ID and CARD_REL in accepted_paths and card_path.exists()
    if registered:
        assert len(manifest_targets) == 1 and manifest_targets[0].get("canonical_name") == NAME_ZH
        assert card_path.read_text(encoding="utf-8-sig") == make_card()
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 5 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and not alignment.get("ku_id") and not card_path.exists() and CARD_REL not in accepted_paths
    assert not any(
        row.get("type") == "person" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "Louis Richeôme already exists as a person KU"

    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == {CANDIDATE_ID}, group_members
    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == EXPECTED_RELATION_IDS, (direct_relations, EXPECTED_RELATION_IDS)
    source_text = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    for item in SOURCES:
        assert " ".join(item["quote"].split()) in " ".join(source_text.split()), item["source_span"]

    planned_alignment = [dict(row) for row in alignments]
    planned_alignment_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_alignment_by_id[CANDIDATE_ID]["ku_id"] = KU_ID
    planned_alignment_by_id[CANDIDATE_ID]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 person：Louis Richeôme 书内人物身份登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`（`{GROUP}`）登记为[Louis Richeôme人物卡](../../../{CARD_REL})。"
        "S3依据第3章全名、French Jesuit身份和跨段复指，将索引Q-R.csv#119与正文候选归为同一书内人物组；中文名标作工作音译。"
        "5条直接关系候选仍待S6；未据此补写生平、外部身份或正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### person：Louis Richeôme 书内身份组 S4 登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}` → [人物卡](../units/persons/louis-richeome.md)。"
        "卡片只登记Haskell明确给出的姓名、French Jesuit身份及1611年写书这一语境，中文名注明工作音译；5条直接S2关系候选仍待S6。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 person dry-run passed: {GROUP} -> {KU_ID}")
        print(f"direct relation candidates={len(direct_relations)}; source quotations={len(SOURCES)}; index=Q-R.csv#119")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,}->{len(planned_manifest):,}"
        )
        print("no files changed")
        return 0

    card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
