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

CANDIDATES = ("cand-0265", "cand-0266")
GROUP = "new-person:beccaria-cesare-904a6681ff"
KU_ID = "units/persons/cesare-beccaria"
CARD_REL = "04-knowledge/units/persons/cesare-beccaria.md"
NAME_ZH = "切萨雷·贝卡里亚"
NAME_EN = "Cesare Beccaria"
ANCHOR = "s3-s4-person-cesare-beccaria-treccani-20261017"
SOURCE_10 = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
SOURCE_13 = "02-sources/02-Markdown/13_CHP-13_intro.md"
SOURCE_15 = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/cesare-beccaria_%28Dizionario-Biografico%29/"
TRECCANI_SOURCE = "Treccani, Dizionario Biografico degli Italiani"
EXPECTED_RELATION_IDS = {
    "st-chp10-p318-beccaria-published-dei-delitti-and-welcomed-in-paris",
    "st-chp10-p318-unnamed-venetian-opposed-beccaria",
    "st-chp10-p328-biffi-friendship-with-beccaria",
}
SOURCE_QUOTES = (
    (SOURCE_10, "in 1764 Beccaria published his epoch-making Dei delitti e delle pene and was rapturously welcomed in Paris."),
    (SOURCE_10, "it was indeed a Venetian who proved to be the most vigorous opponent of Beccaria"),
    (SOURCE_10, "Giambattista Biffi, the friend of Beccaria and Verri"),
    (SOURCE_13, "copies of Beccaria’s forbidden Dei delitti e delle pene"),
)


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页318；OCR L136、L139",
            "sentence_summary": "Haskell在第318页称Beccaria于1764年出版Dei delitti e delle pene，并提到一名未具名威尼斯人的反对；其评价词和反对关系仍按作者原话及S6候选处理。",
            "original_quotes": [
                {"source_span": "line 136; print p. 318; PDF physical p. 51", "text": SOURCE_QUOTES[0][1]},
                {"source_span": "line 139; print p. 318; PDF physical p. 51", "text": SOURCE_QUOTES[1][1]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_10,
                "source_span": "lines 136, 139; print p. 318; PDF physical p. 51",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页328；OCR L243",
            "sentence_summary": "Haskell称Giambattista Biffi为Beccaria与Verri的朋友；此书内关系候选未在本批转为正式关系。",
            "original_quotes": [{
                "source_span": "line 243; print p. 328; PDF physical p. 61",
                "text": SOURCE_QUOTES[2][1],
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_10,
                "source_span": "line 243; print p. 328; PDF physical p. 61",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第13章；印刷页337；OCR L53",
            "sentence_summary": "Haskell称Pasquali曾秘密散发Beccaria作品的副本；此处用于记录跨章提及，不归作Beccaria本人的行动。",
            "original_quotes": [{
                "source_span": "line 53; print p. 337",
                "text": SOURCE_QUOTES[3][1],
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_13,
                "source_span": "line 53; print p. 337",
            },
        },
    ]
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
    src10 = f"[第10章书内来源](../../../{SOURCE_10})"
    src13 = f"[第13章书内来源](../../../{SOURCE_13})"
    relation_lines = "\n".join(f"- `{sid}`" for sid in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** Haskell在第10章称Beccaria于1764年出版《Dei delitti e delle pene》，第13章再以作品散发为语境提及Beccaria。索引B.csv#112与B.csv#113均列全名“Beccaria, Cesare”；后者的子目是《Dei delitti e delle pene》，仍指向人物候选。Treccani《意大利人传记辞典》第7卷的“BECCARIA, Cesare”条目讨论同一作品，姓名与作品锚点相合，支持将两条索引候选归为同一人物。该书本身保留为独立archive候选`cand-9707`；本卡不吸收作品身份，也不把Haskell的关系或评价转成已核事实。{src10} {src13}

**English:** Haskell says in Chapter 10 that Beccaria published *Dei delitti e delle pene* in 1764; Chapter 13 refers to Beccaria in the context of copies of the work being distributed. Index entries B.csv#112 and B.csv#113 both give the full name “Beccaria, Cesare”; the latter has *Dei delitti e delle pene* as a subentry but remains a person candidate. Treccani’s *Dizionario Biografico degli Italiani*, volume 7, has an entry “BECCARIA, Cesare” that discusses the same work, matching the name and work anchor and supporting one person identity for both index candidates. The treatise remains a separate archive candidate, `cand-9707`; this card does not absorb the work or upgrade Haskell’s relationship claims and evaluations into verified facts. {src10} {src13}

### 姓名与身份范围

- 书中及索引全名：Cesare Beccaria；索引候选分别为B.csv#112、B.csv#113。
- 中文显示名：“切萨雷·贝卡里亚”为中文音译。
- 类型边界：本卡为人物；《Dei delitti e delle pene》是独立文献候选，未并入人物卡。

## 关系与证据

### 身份与外部链接

- Treccani《意大利人传记辞典》第7卷（1970），Franco Venturi撰：[BECCARIA, Cesare]({TRECCANI_URL})。用于核对人物全名与《Dei delitti e delle pene》作品身份；不支持Haskell所述的具体友谊、反对关系或巴黎接待评价。

### 关系记录

当前没有新增正式关系。以下3条直接S2关系候选继续待S6，分别保留作品著述、未具名反对者及Biffi友谊的原始限定：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def next_alignment_id(rows, offset=0) -> str:
    numbers = [int(row["alignment_id"].split("-", 1)[1]) for row in rows if row.get("alignment_id", "").startswith("aln-")]
    return f"aln-{max(numbers, default=0) + 1 + offset:04d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Cesare Beccaria person group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_alignments = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        candidate = candidate_by_id[cid]
        alignment = candidate_alignments[cid]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("canonical_name") == "Beccaria, Cesare"
        assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP
    assert candidate_by_id["cand-0265"].get("index_entry_id") == "B.csv#112"
    assert candidate_by_id["cand-0266"].get("index_entry_id") == "B.csv#113"
    assert candidate_by_id["cand-0266"].get("sub_entry") == "Dei delitti e delle pene"

    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    external_rows = [
        row for row in alignments
        if row.get("candidate_id") in CANDIDATES and row.get("external_source") == TRECCANI_SOURCE
    ]
    assert len(manifest_targets) <= 1 and len(external_rows) <= len(CANDIDATES)
    registered = bool(manifest_targets) and all(candidate_alignments[cid].get("ku_id") == KU_ID for cid in CANDIDATES) and CARD_REL in accepted_paths and card_path.exists() and len(external_rows) == len(CANDIDATES)
    if registered:
        assert len(manifest_targets) == 1 and all(row.get("external_id") == TRECCANI_URL for row in external_rows)
        assert card_path.read_text(encoding="utf-8-sig") == make_card()
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; two candidate mappings and Treccani corroboration rows present; 3 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and all(not candidate_alignments[cid].get("ku_id") for cid in CANDIDATES)
    assert not card_path.exists() and CARD_REL not in accepted_paths and not external_rows
    assert not any(
        row.get("type") == "person" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "Cesare Beccaria already exists as a person KU"

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
    for rel, quote in SOURCE_QUOTES:
        normalized = " ".join((ROOT / rel).read_text(encoding="utf-8-sig").split())
        assert " ".join(quote.split()) in normalized, (rel, quote)

    planned_alignment = [dict(row) for row in alignments]
    planned_candidate_alignments = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        target = planned_candidate_alignments[cid]
        target["ku_id"] = KU_ID
        target["resolution_note"] = target["resolution_note"].replace(
            "No external identity source was accessed; KU assignment remains for S4.",
            "At the initial S3 decision no external source was accessed; Treccani DBI later corroborated the identity and is recorded below.",
        )
        target["resolution_note"] += f" S4 registration applied: mapped {GROUP} to {KU_ID}."
        planned_alignment.append({
            "alignment_id": next_alignment_id(planned_alignment, offset=sum(row.get("external_source") == TRECCANI_SOURCE for row in planned_alignment)),
            "candidate_id": cid,
            "ku_id": KU_ID,
            "external_source": TRECCANI_SOURCE,
            "external_id": TRECCANI_URL,
            "decision": "same",
            "accessed_date": "2026-10-17",
            "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
            "legacy_ku_id": "",
            "resolution_note": "Identity corroboration: Franco Venturi, 'BECCARIA, Cesare,' Treccani DBI, vol. 7 (1970), identifies the person and discusses Dei delitti e delle pene; this matches the full index name and Haskell's 1764 work reference. This record corroborates identity only, not Haskell's relationship or reception claims.",
        })
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
        "### S3/S4 person：Cesare Beccaria 跨章身份核对与登记（2026-10-17）\n\n"
        f"`{', '.join(CANDIDATES)}`（`{GROUP}`）共同登记为[Cesare Beccaria人物卡](../../../{CARD_REL})。S1索引B.csv#112、B.csv#113均为全名`Beccaria, Cesare`，后者附《Dei delitti e delle pene》子目；S2分别锚定第10章第318、328页、第13章第337页和第15章第369页。第13章与第15章的表述涉及该作品，不将Pasquali或另一段落中的代词行动归给Beccaria。"
        f"外部对照：Franco Venturi, ‘BECCARIA, Cesare,’ Treccani, *Dizionario Biografico degli Italiani*, vol. 7 (1970), {TRECCANI_URL}（访问日期2026-10-17）。该条讨论同一人物及其《Dei delitti e delle pene》，与全名和第10章1764年作品锚点相合；只确认身份，不验证Haskell的‘epoch-making’、巴黎欢迎、Biffi友谊或未具名威尼斯反对者等陈述。书本身候选`cand-9707`（archive组`archive-group-47e19ac2f4b5`）保持独立，未并入人物卡；未具名对手`cand-9711`保持undecided。"
        "3条直接关系候选仍待S6；Treccani身份记录分别附于两个候选映射，未新增正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### person：Cesare Beccaria 跨章身份组 S4 登记（2026-10-17）\n\n"
        f"`{CANDIDATES[0]}`、`{CANDIDATES[1]}`共同映射至[人物卡](../units/persons/cesare-beccaria.md)。第10、13、15章的书内提及与索引全名相合；Treccani DBI记录核对已写入alignment。Treatise `Dei delitti e delle pene`保持独立archive候选；3条直接关系候选待S6。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    planned_accepted = "\n".join(accepted_lines[:insert_at] + [f"- {CARD_REL}"] + accepted_lines[insert_at:]) + "\n"

    if args.dry_run:
        print(f"S4 person dry-run passed: {GROUP} -> {KU_ID}")
        print(f"candidate mappings={len(CANDIDATES)}; chapter anchors=10,13,15; Treccani DBI identity rows={len(CANDIDATES)}; direct relation candidates={len(direct_relations)}")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; alignment={len(alignments):,}->{len(planned_alignment):,}"
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
        f"applied: {GROUP} -> {KU_ID}; candidate mappings={len(CANDIDATES)}; external identity rows={len(CANDIDATES)}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
