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

CANDIDATES = ("cand-0927",)
GROUP = "new-person:daniele-dolfin-iii-b39c2311e9"
KU_ID = "units/persons/daniele-dolfin-iii"
CARD_REL = "04-knowledge/units/persons/daniele-dolfin-iii.md"
CHAPTER = "02-sources/02-Markdown/09_CHP-9_intro.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/D.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp9-p252-daniele-iii-public-service",
    "st-chp9-p252-daniele-iii-will-programme",
    "st-chp9-p252-daniele-iv-brother-of-iii",
    "st-chp9-p252-dionisio-younger-brother-of-iii",
    "st-chp9-p252-daniele-iii-will-shed-blood",
    "st-chp9-p253-roman-epics-commemorate-daniele-dolfin",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页252–253；OCR L119、129",
            "sentence_summary": (
                "第252页以 Daniele III 指称此人，称其于1729年去世、终身服务威尼斯共和国，并记其遗嘱陈述；"
                "同段称 Daniele IV 为其兄弟。第253页提到 Daniele Dolfin，并称 Tiepolo 的 Roman epics 纪念 Antonio Barbaro 与 Daniele Dolfin。"
                "索引将第252、253页均列于 Dolfin, Daniele III 主项；以上事实依 Haskell 的叙述和索引范围保存，相关关系候选待 S6 裁决。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 119",
                    "text": (
                        "Daniele III, who died in 1729, served the State abroad and at home throughout his life and was "
                        "considered one of the finest orators of the day."
                    ),
                },
                {
                    "source_span": "line 119",
                    "text": "His brother, Daniele IV, who died in the same year, was one of the most heroic commanders in the Turkish wars",
                },
                {
                    "source_span": "line 129",
                    "text": (
                        "The heroic days of an Antonio Barbaro or a Daniele Dolfin must now have seemed almost as remote "
                        "as the Roman epics with which he had commemorated them"
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "lines 119, 129; print pp. 252–253",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；D.csv#29；印刷页252、253",
            "sentence_summary": "书后索引以 Dolfin, Daniele III 为主项，定位第252、253页。",
            "original_quotes": [
                {
                    "source_span": "index entry D.csv#29",
                    "text": "| Dolfin, Daniele III |  |  |  | 252, 253 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry D.csv#29",
            },
        },
    ]
    frontmatter = {
        "title": "丹尼埃莱·多尔芬三世（Daniele Dolfin III）",
        "name_en": "Daniele Dolfin III",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    pp252_253 = f"[第9章 pp.252–253](../../../{CHAPTER})（L119、129）"
    index = f"[书后索引](../../../{INDEX_FILE})（D.csv#29）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应书后索引主项“Dolfin, Daniele III”（D.csv#29），其页码为252、253。第252页正文称 Daniele III 于1729年去世；第253页以 Daniele Dolfin 指称 Tiepolo 的 Roman epics 所纪念的人物，索引将该页归在同一主项下。Haskell另将 Daniele IV 称为 Daniele III 的兄弟。以上均按原书与索引表述保存；本次仅登记人物身份映射，亲缘、公共服务、遗嘱内容和纪念关系候选仍待 S6 裁决。{pp252_253} {index}

**English:** This card records the person indexed as “Dolfin, Daniele III” (D.csv#29), with references to pp.252 and 253. The p.252 passage names Daniele III and says that he died in 1729; p.253 refers to a Daniele Dolfin commemorated by Tiepolo’s Roman epics, and the index places that page under the same entry. Haskell also identifies Daniele IV as Daniele III’s brother. These statements are preserved as presented in the book and index. This S4 action registers the person identity mapping only; kinship, public service, will, and commemoration candidates remain for S6 adjudication. {pp252_253} {index}

### 身份边界

本卡按索引主项 Dolfin, Daniele III 登记。Daniele IV 与 Daniele Dolfin（Archbishop of Udine）分别列为独立索引项；既有 Dionisio Dolfin 人物卡及 Dolfin family KU 也保持独立。本卡不将 Daniele III 的人物身份并入家族对象。

This card follows the index entry Dolfin, Daniele III. Daniele IV and Daniele Dolfin (Archbishop of Udine) have separate index entries; the existing Dionisio Dolfin person card and Dolfin family KU also remain distinct. The identity is not merged into the family object.

## 关系与证据

6条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Daniele Dolfin III's S3 person identity group in S4.")
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

    assert not (ROOT / CARD_REL).exists()
    assert CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en") or "").casefold() == "daniele dolfin iii"
        for row in manifest
    ), "Daniele Dolfin III person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "D.csv#29"
    assert candidate["canonical_name"] == "Dolfin, Daniele III"
    assert candidate["index_page_range"] == "252, 253"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    chapter = (ROOT / CHAPTER).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "Daniele III, who died in 1729, served the State abroad and at home throughout his life" in chapter
    assert "a Daniele Dolfin must now have seemed almost as remote as the Roman epics" in chapter
    assert "| Dolfin, Daniele III |  |  |  | 252, 253 |" in index_text
    assert "| Dolfin, Daniele IV |  |  |  | 252 |" in index_text
    assert "| Dolfin, Daniele (Archbishop of Udine) |  |  |  | 253n |" in index_text

    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == RELATION_CANDIDATES, direct_relations

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATES[0] and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "丹尼埃莱·多尔芬三世",
        "name_en": "Daniele Dolfin III",
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-daniele-dolfin-iii-person\"></a>\n\n"
        "### S4 person：Daniele Dolfin III 身份组登记（2026-10-17）\n\n"
        f"`cand-0927`（D.csv#29，pp.252、253）保持 S3 组 `{GROUP}`，映射至[Daniele Dolfin III 人物卡]"
        f"(../../../{CARD_REL})。第252页正文称 Daniele III，第253页作 Daniele Dolfin；索引将两页列于同一主项。"
        "Daniele IV 和 Daniele Dolfin（Archbishop of Udine）为索引中的分立项，既有 Dionisio Dolfin 及 Dolfin family KU 保持独立。"
        "6条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。本轮未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Daniele Dolfin III 身份组登记（2026-10-17）\n\n"
        f"`cand-0927`（D.csv#29）映射至[Daniele Dolfin III 人物卡]"
        "(../units/persons/daniele-dolfin-iii.md)。索引将 pp.252、253 列于同一人物主项；"
        "Daniele IV 与 Daniele Dolfin（Udine 大主教）保持区分，6条直接关系候选仍待 S6。未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
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
        print(f"S4 Daniele Dolfin III dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"identity_group={GROUP}; candidates={len(group_rows)}; direct_relation_candidates={len(direct_relations)}")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / CARD_REL).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATES[0]} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
