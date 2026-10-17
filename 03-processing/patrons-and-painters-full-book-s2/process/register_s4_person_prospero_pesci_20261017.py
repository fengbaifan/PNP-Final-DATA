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

CANDIDATES = ("cand-1887", "cand-10374")
GROUP = "new-person:pesci-prospero-a4b78e3c88"
KU_ID = "units/persons/prospero-pesci"
CARD_REL = "04-knowledge/units/persons/prospero-pesci.md"
NAME_ZH = "普罗斯佩罗·佩西"
NAME_EN = "Prospero Pesci"
ANCHOR = "s4-person-prospero-pesci-20261017"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCES = (
    {
        "location": "第14章；印刷页358；L121",
        "source_span": "L121; print p. 358",
        "quote": "two artists, Prospero Pesci and Mauro Tesi, whom he employed to give expression to his ideas",
        "summary_cn": "第14章称 Algarotti 于1756年移居 Bologna 后遇到并雇用 Prospero Pesci 与 Mauro Tesi 两位艺术家，以表达其构想；此处未提供 Pesci 的生平信息。",
        "summary_en": "Chapter 14 says that after Algarotti moved to Bologna in 1756 he encountered and employed Prospero Pesci and Mauro Tesi to give expression to his ideas; the passage provides no biography of Pesci.",
    },
    {
        "location": "第14章；印刷页357；注7；L206",
        "source_span": "L206; print p. 357, note 7",
        "quote": "Letter to Prospero Pesci of 28 September 1759 in Opere, VHI, pp. 89-100.",
        "summary_cn": "第14章注7将一封1759年9月28日致 Prospero Pesci 的信定位至 Opere 卷册第89–100页；该刊本未在本批独立查阅。",
        "summary_en": "Chapter 14 note 7 locates a letter to Prospero Pesci dated 28 September 1759 in Opere, pages 89–100; the edition was not independently consulted in this batch.",
    },
)
EXPECTED_RELATION_IDS = {
    "st-chp14-p357-note7-letter-addressed-to-pesci",
    "st-chp14-p358-employed-pesci",
    "st-chp14-p358-pesci-instruction-on-varied-tones",
    "st-chp14-p358-pesci-sketch-composer-analogy",
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
    source_link = f"[第14章书内来源](../../../{SOURCE_FILE})"
    relation_lines = "\n".join(f"- `{sid}`" for sid in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** Haskell 在第14章将 Prospero Pesci 与 Mauro Tesi 并列为 Algarotti 于 Bologna 遇到并雇用的艺术家，称 Algarotti 常让他们依据自己的草图作画。第357页注7另列一封1759年9月28日致 Prospero Pesci 的信。此卡仅记录书内姓名和活动语境；中文名为工作音译，不补写生卒、完整生平或外部身份。{source_link}

**English:** In Chapter 14 Haskell names Prospero Pesci alongside Mauro Tesi as an artist whom Algarotti encountered and employed in Bologna, often directing them to work from his sketches. Note 7 on page 357 also cites a letter to Prospero Pesci dated 28 September 1759. This card records only the name and context supplied by the book; the Chinese name is a working transliteration, and no dates, full biography, or external identity are added. {source_link}

### 姓名与身份范围

- 书内全名：Prospero Pesci；索引主项为“Pesci, Prospero”（P.csv#88），正文及脚注均给出同一全名锚点。{source_link}
- 中文显示名：“普罗斯佩罗·佩西”为工作音译，不声明为已核定通行译名。{source_link}
- 书内角色：Haskell称其为艺术家，并将其与 Mauro Tesi 并列在 Algarotti 的雇用与草图语境中；具体作品和关系保留为S2候选。{source_link}

## 关系与证据

### 关系记录

当前没有新增正式关系。以下4条S2关系候选保留于`book-statements.jsonl`，待S6逐条核对关系语义、转述来源及时间限定：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Prospero Pesci's cross-candidate person identity group in S4.")
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
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    card_path = ROOT / CARD_REL

    expected_names = {
        "cand-1887": "Pesci, Prospero",
        "cand-10374": "Prospero Pesci (recipient named in p.357 n.7)",
    }
    for cid in CANDIDATES:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("canonical_name") == expected_names[cid]
        assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    assert len(manifest_targets) <= 1
    registered = (
        bool(manifest_targets) and all(alignment_by_id[cid].get("ku_id") == KU_ID for cid in CANDIDATES)
        and CARD_REL in accepted_paths and card_path.exists()
    )
    if registered:
        assert len(manifest_targets) == 1 and manifest_targets[0].get("canonical_name") == NAME_ZH
        assert card_path.read_text(encoding="utf-8-sig") == make_card()
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 4 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and all(not alignment_by_id[cid].get("ku_id") for cid in CANDIDATES)
    assert not card_path.exists() and CARD_REL not in accepted_paths
    assert not any(
        row.get("type") == "person" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "Prospero Pesci already exists as a person KU"
    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(CANDIDATES), group_members
    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == EXPECTED_RELATION_IDS, (direct_relations, EXPECTED_RELATION_IDS)
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for item in SOURCES:
        assert " ".join(item["quote"].split()) in source_text, item["source_span"]

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for cid in CANDIDATES:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
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
        "### S4 person：Prospero Pesci 跨候选人物组登记（2026-10-17）\n\n"
        f"`{', '.join(CANDIDATES)}`（`{GROUP}`）共同登记为[Prospero Pesci人物卡](../../../{CARD_REL})。"
        "索引主项与第14章正文、脚注的全名相合；两条候选映射至同一人物KU。卡片只保留Haskell所述艺术家与Algarotti草图语境，中文名为工作音译。"
        "4条直接关系候选仍待S6，未新增正式关系或外部身份记录。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### person：Prospero Pesci 跨候选身份组 S4 登记（2026-10-17）\n\n"
        f"`{CANDIDATES[0]}`、`{CANDIDATES[1]}`共同映射至[Prospero Pesci人物卡](../units/persons/prospero-pesci.md)。"
        "索引主项、正文全名与1759年书信收信人全名互相对应；4条直接S2关系候选仍待S6，未新增正式关系。\n\n"
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
        print(f"candidate_mappings={len(CANDIDATES)}; direct relation candidates={len(direct_relations)}; source quotations={len(SOURCES)}")
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
        f"applied: {GROUP} -> {KU_ID}; candidate_mappings={len(CANDIDATES)}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
