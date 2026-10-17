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

CANDIDATES = ("cand-1399",)
GROUP = "new-person:archduke-leopold-wilhelm-b4ff9984cb"
KU_ID = "units/persons/leopold-wilhelm-archduke"
CARD_REL = "04-knowledge/units/persons/leopold-wilhelm-archduke.md"
CHAPTER = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/L.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp7-p193-leopold-bequest",
    "st-chp7-p193-leopold-patronizes-vecchia",
    "st-chp7-p193-leopold-venetian-painters",
    "st-chp7-p193-liberi-vienna",
    "st-chp7-p193-loot-mitigated",
    "st-chp7-p193-n2-boschini-dedication",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第7章；印刷页193；OCR L8–10、18–19",
            "sentence_summary": (
                "Haskell称 Archduke Leopold Wilhelm 曾任 Netherlands 总督，返回时带回其在那里购得的画作，其中一些来自 Charles I 画廊；"
                "他偏爱16世纪早期威尼斯画家、赞助 Pietro della Vecchia，并说服 Pietro Liberi 于1658年前往 Vienna。"
            ),
            "original_quotes": [
                {
                    "source_span": "lines 8–10",
                    "text": (
                        "the return from the Netherlands, where he had been Governor, of the Archduke Leopold Wilhelm "
                        "with the marvellous pictures he had acquired there, some of which came from the gallery of Charles I."
                    ),
                },
                {
                    "source_span": "lines 9–10",
                    "text": (
                        "The Archduke was especially fond of the Venetian painters of the early sixteenth century and "
                        "one of the contemporaries whom he most patronised was Pietro della Vecchia"
                    ),
                },
                {
                    "source_span": "lines 10–11",
                    "text": (
                        "He also persuaded the most successful Venetian painter of the day, Pietro Liberi, to come to Vienna in 1658"
                    ),
                },
                {
                    "source_span": "line 12",
                    "text": "On his death in 1662 the Archduke left all his possessions to his nephew, the Emperor Leopold I.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "lines 8–12; print p. 193",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；L.csv#56；印刷页193",
            "sentence_summary": "书后索引以 Leopold Wilhelm, Archduke 为主项，定位第193页。",
            "original_quotes": [
                {
                    "source_span": "index entry L.csv#56",
                    "text": "| Leopold Wilhelm, Archduke |  |  |  | 193 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry L.csv#56",
            },
        },
    ]
    frontmatter = {
        "title": "利奥波德·威廉大公（Archduke Leopold Wilhelm）",
        "name_en": "Archduke Leopold Wilhelm",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p193 = f"[第7章 p.193](../../../{CHAPTER})（L8–12）"
    index = f"[书后索引](../../../{INDEX_FILE})（L.csv#56）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记书后索引“Leopold Wilhelm, Archduke”及第7章 p.193 正文所指人物。Haskell称他曾任 Netherlands 总督，返回时带回在那里购得的画作，其中部分来自 Charles I 的画廊；作者还说他尤其喜爱16世纪早期威尼斯画家、赞助 Pietro della Vecchia，并说服 Pietro Liberi 于1658年前往 Vienna。Haskell记载大公于1662年去世，并将全部财产留给侄子 Emperor Leopold I。以上均保留为书内叙述；本卡不将收藏、赞助、邀请或遗赠内容写为正式关系，也不补外部生平。{p193} {index}

**English:** This card records the person named in the index as “Leopold Wilhelm, Archduke” and in the Chapter 7 passage on p.193. Haskell says that he had been Governor of the Netherlands and returned with pictures he had acquired there, some from Charles I’s gallery. The author also says that he especially favoured early sixteenth-century Venetian painters, patronized Pietro della Vecchia, and persuaded Pietro Liberi to go to Vienna in 1658. Haskell records the Archduke’s death in 1662 and says that he left all his possessions to his nephew, Emperor Leopold I. These remain statements in the book; this card does not register collecting, patronage, recruitment, or bequest as formal relations and adds no external biography. {p193} {index}

### 身份边界

本卡只对应索引主项及第7章 p.193 的 Archduke Leopold Wilhelm。Emperor Leopold I 是其侄子，保持为独立人物；Prince Eugene、Pietro della Vecchia、Pietro Liberi、Charles I 及 Netherlands、Vienna、Prague 也分别保持独立。文中所述抢掠、收藏来源和艺术赞助均按 Haskell 的叙述范围保留。

This card refers only to the Archduke Leopold Wilhelm in the index and the Chapter 7 passage. Emperor Leopold I is identified as his nephew and remains a separate person. Prince Eugene, Pietro della Vecchia, Pietro Liberi, Charles I, the Netherlands, Vienna, and Prague also remain distinct. Accounts of looting, collection provenance, and artistic patronage are kept within Haskell’s stated scope.

## 关系与证据

6条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Archduke Leopold Wilhelm's S3 person identity group in S4.")
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
        and (row.get("name_en") or "").casefold() == "archduke leopold wilhelm"
        for row in manifest
    ), "Archduke Leopold Wilhelm person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "L.csv#56"
    assert candidate["canonical_name"] == "Leopold Wilhelm, Archduke"
    assert candidate["index_page_range"] == "193"
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
    normalized = " ".join(chapter.split())
    for quote in (
        "the Archduke Leopold Wilhelm with the marvellous pictures he had acquired there",
        "The Archduke was especially fond of the Venetian painters of the early sixteenth century",
        "He also persuaded the most successful Venetian painter of the day, Pietro Liberi, to come to Vienna in 1658",
        "On his death in 1662 the Archduke left all his possessions to his nephew, the Emperor Leopold I",
    ):
        assert " ".join(quote.split()) in normalized, quote
    assert "| Leopold Wilhelm, Archduke |  |  |  | 193 |" in index_text

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
        "canonical_name": "利奥波德·威廉大公",
        "name_en": "Archduke Leopold Wilhelm",
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
        "\n\n<a id=\"s4-leopold-wilhelm-person\"></a>\n\n"
        "### S4 person：Archduke Leopold Wilhelm 直接关系端点登记（2026-10-17）\n\n"
        f"`cand-1399`（L.csv#56，p.193）保持 S3 组 `{GROUP}`，映射至[Archduke Leopold Wilhelm 人物卡]"
        f"(../../../{CARD_REL})。索引头衔和正文全名对应。Haskell称其曾任 Netherlands 总督、带回当地购得的画作、偏爱早期威尼斯画家、"
        "赞助 Pietro della Vecchia、邀请 Pietro Liberi 前往 Vienna，并于1662年将财产留给侄子 Emperor Leopold I。"
        "6条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。本轮未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Archduke Leopold Wilhelm 身份组登记（2026-10-17）\n\n"
        f"`cand-1399`（L.csv#56）映射至[Archduke Leopold Wilhelm 人物卡]"
        "(../units/persons/leopold-wilhelm-archduke.md)。第7章 p.193 全名与书后索引相合；侄子 Emperor Leopold I 保持独立。"
        "6条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 Archduke Leopold Wilhelm dry-run passed: {CANDIDATES} -> {KU_ID}")
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
