from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s3-s4-person-pietro-francavilla-20261017"
CANDIDATE = "cand-1064"
GROUP = "new-person:francavilla-pietro-c1cca1c0e8"
KU_ID = "units/persons/pietro-francavilla"
CARD_REL = "04-knowledge/units/persons/pietro-francavilla.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "彼得罗·弗朗卡维拉"
NAME_EN = "Pietro Francavilla"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/F.csv"
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
RELATION_IDS = (
    "st-chp7-p174-i08",
    "st-chp7-p174-i09",
    "st-chp7-p174-i10",
    "st-chp7-p174-i17",
)

SOURCES = (
    {
        "location": "书后索引，F.csv#79；索引定位 pp.174、178",
        "summary": "索引以 Francavilla, Pietro 为主项，定位至 pp.174、178；索引是书内定位，不独立证明传记事实。",
        "quote": '"Francavilla, Pietro"',
        "span": "F.csv#79",
        "doc_id": "patrons-and-painters-index",
        "file": INDEX_FILE,
    },
    {
        "location": "第7章，印刷页174；OCR L45–59",
        "summary": "正文以 Pietro Francavilla 全名称其为一位 Flemish-Florentine sculptor，记述其受召赴巴黎、与助手 Francesco Bordoni 同行，以及与 Pietro Tacca 完成亨利四世骑马像；称号、关系及创作角色均按 Haskell 的叙述范围保存。",
        "quote": "the Flemish-Florentine sculptor Pietro Francavilla, that he summoned him to Paris",
        "span": "lines 45–59; print p. 174",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_FILE,
    },
    {
        "location": "第7章，印刷页178；OCR L102–111",
        "summary": "正文在有关 Pietro Tacca 的段落中以姓氏 Francavilla 回顾意大利雕塑传统；按索引页码及同一姓氏和雕塑语境与 p.174 的全名候选关联。",
        "quote": "the traditions of Giambologna, Pietro Tacca and Francavilla",
        "span": "lines 102–111; print p. 178",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_FILE,
    },
)


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": item["doc_id"],
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relations = "\n".join(f"- `{sid}`" for sid in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第7章 p.174 以全名提及、并由书后索引定位至 pp.174、178 的雕塑家 Pietro Francavilla。p.174 称他为 Flemish-Florentine sculptor，记述 Marie de’ Medici 抵达巴黎后，亨利四世因其制作的奥菲斯与野兽喷泉而召他赴巴黎；Francavilla 随后与助手及未来女婿 Francesco Bordoni 一同到达。该页还称由 Giambologna 创作的亨利四世骑马像在十年后由 Pietro Tacca 与 Francavilla 完成。p.178 将 Francavilla 与 Giambologna、Pietro Tacca 并列于雕塑传统的叙述中。中文显示名为项目工作音译；卡片不补写书外生平。

**English:** This card records the sculptor Pietro Francavilla, named in full on p. 174 of Haskell’s chapter 7 and located by the book’s index at pp. 174 and 178. On p. 174 he is called a Flemish-Florentine sculptor. Haskell says that, after Marie de’ Medici arrived in Paris, Henri IV summoned Francavilla because of a fountain he had made showing Orpheus enchanting wild beasts; Francavilla soon arrived with his assistant and future son-in-law Francesco Bordoni. The page also says that the equestrian monument of Henri IV, modeled by Giambologna, was completed ten years later by Pietro Tacca and Francavilla. On p. 178 Haskell places Francavilla alongside Giambologna and Pietro Tacca in a discussion of sculptural traditions. The Chinese display name is a project working transliteration; no external biography is added.

### 名称与身份边界

索引主项 `Francavilla, Pietro`（F.csv#79）列 pp.174、178。第7章 p.174 给出全名与雕塑家身份；p.178 的 Francavilla 与 Pietro Tacca 并列，索引定位和雕塑语境支持将该姓氏指代归于同一书内人物。卡片不把同页提及视为完整生平，也不把作品创作角色或与 Bordoni 的关系提前正式化。

The index main entry `Francavilla, Pietro` (F.csv#79) lists pp. 174 and 178. Chapter 7 p. 174 supplies his full name and sculptor designation; on p. 178 Francavilla is named alongside Pietro Tacca, and the index locator and sculptural context support the same book-local identity. The card is not a complete biography; creation roles and the relationship to Bordoni are not formalized here.

## 关系与证据

本次没有新增正式关系。以下4条直接 S2 关系候选留待 S6 逐项审查：

{relations}

相关身份、委托／召赴巴黎、同行以及作品完成角色均保持原书语境；本次未写入 `relations.csv`。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Pietro Francavilla's cross-page source-local person group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    if (
        CARD_PATH.exists()
        and any(row.get("ku_id") == KU_ID for row in manifest)
        and decisions[CANDIDATE].get("ku_id") == KU_ID
        and decisions[CANDIDATE].get("decision") == "new"
    ):
        print("ALREADY REGISTERED: Pietro Francavilla person group")
        return 0

    assert len(manifest) == 1551 and len(alignments) == 12642
    assert candidate_map[CANDIDATE]["suggested_type"] == "person"
    row = decisions[CANDIDATE]
    assert row["decision"] == "new" and not row.get("ku_id")
    assert sync.get_group(row.get("resolution_note", "")) == GROUP
    members = [
        item for item in alignments
        if item.get("candidate_id") and not item.get("external_source") and item["decision"] == "new"
        and sync.get_group(item.get("resolution_note", "")) == GROUP
    ]
    assert [item["candidate_id"] for item in members] == [CANDIDATE]
    assert not CARD_PATH.exists() and CARD_REL not in ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert not any(item.get("ku_id") == KU_ID or item.get("card_path") == CARD_REL for item in manifest)
    assert not any(item.get("type") == "person" and item.get("name_en", "").casefold() == NAME_EN.casefold() for item in manifest)

    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    source_text = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    assert '"Francavilla, Pietro"' in index_text
    for quote in (
        "the Flemish-Florentine sculptor Pietro Francavilla",
        "he summoned him to Paris where he soon arrived with his assistant and future son-in-law Francesco",
        "the monument, which was completed by Pietro Tacca and Francavilla",
        "the traditions of Giambologna, Pietro Tacca and Francavilla",
    ):
        assert quote in source_text, f"source excerpt missing: {quote}"
    statements = {s["statement_id"]: s for s in sync.load_statements()}
    direct = [s for s in statements.values() if CANDIDATE in (s.get("subject_candidate_id"), s.get("object_candidate_id"))]
    assert {s["statement_id"] for s in direct} == set(RELATION_IDS)
    assert all(statements[sid]["qualifiers"].get("relation_candidate") is True for sid in RELATION_IDS)

    planned_alignment = [dict(item) for item in alignments]
    target = next(item for item in planned_alignment if item.get("candidate_id") == CANDIDATE and not item.get("external_source"))
    target["ku_id"] = KU_ID
    target["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    assert len(planned_manifest) == 1552
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert (totals["registered_groups"], totals["registered_members"], totals["pending_groups"], totals["pending_members"]) == (533, 667, 4271, 4312)

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_warning = "审计警告中的4,328条待登记 `decision=new` alignment 行，含4,313条候选决定映射（4,272组）和15条外部身份记录。"
    new_warning = "审计警告中的4,327条待登记 `decision=new` alignment 行，含4,312条候选决定映射（4,271组）和15条外部身份记录。"
    assert old_warning in result_text
    result_text = result_text.replace(old_warning, new_warning, 1)

    process_entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Pietro Francavilla 跨页人物组登记（{DATE}）

`cand-1064`（F.csv#79，索引 pp.174、178）保留 S3 source-local 人物组 `{GROUP}`，登记为[彼得罗·弗朗卡维拉人物卡](../../../04-knowledge/units/persons/pietro-francavilla.md)。第7章 p.174 给出 Pietro Francavilla 全名、Flemish-Florentine sculptor 称谓及召赴巴黎语境；同页称其与 Francesco Bordoni 同行，并由 Pietro Tacca 与 Francavilla 完成 Giambologna 创作的亨利四世骑马像。p.178 将 Francavilla 与 Giambologna、Pietro Tacca 并列于雕塑传统叙述。索引页码与正文语境支持跨页同一人物；未用外部来源补充身份或生平。

4条直接 S2 关系候选 `{RELATION_IDS[0]}`、`{RELATION_IDS[1]}`、`{RELATION_IDS[2]}`、`{RELATION_IDS[3]}` 留待 S6；本次没有新增正式关系，未写入 `relations.csv`。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip() + process_entry
    result_note = (
        f"\n\n### S3→S4 person：Pietro Francavilla（{DATE}）\n\n"
        "`cand-1064`→[彼得罗·弗朗卡维拉人物卡](../units/persons/pietro-francavilla.md)。索引 pp.174、178 与正文 p.174 全名、p.178 雕塑语境支持同一书内人物。"
        "4条直接关系候选留待 S6；本次未新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("dry-run passed: cand-1064 maps to one source-local Pietro Francavilla KU")
        print("full name, p.178 surname continuation, and four direct relation-candidate links verified")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; pending-new alignment rows=4,327; relations unchanged")
        print("planned writes: person card, accepted.yml, ku-manifest.csv, alignment.csv, process record, result")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Pietro Francavilla registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
