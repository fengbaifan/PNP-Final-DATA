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

CANDIDATES = ("cand-1442",)
GROUP = "new-person:johann-karl-loth-77685471f9"
KU_ID = "units/persons/johann-karl-loth"
CARD_REL = "04-knowledge/units/persons/johann-karl-loth.md"
CH8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
CH9 = "02-sources/02-Markdown/09_CHP-9_intro.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/L.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp8-p233-loth-employment",
    "st-chp8-p233-note5-death-abel",
    "st-chp8-p233-note5-inventory",
    "st-chp8-p233-note5-loth-letter",
    "st-chp8-p233-note5-self-portrait",
    "st-chp8-p233-loth-first-visit-contact",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第8章；印刷页233；OCR L279",
            "sentence_summary": (
                "Haskell称 Grand Prince Ferdinand 在威尼斯接触到 Karl Loth，并说 Loth 至迟在1691年已为其作画，"
                "此后约七年直至去世。原文将后续接触写作作者推断。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 279",
                    "text": (
                        "Venice, among them Karl Loth with whom he must have got in touch on his first visit, for this German "
                        "artist was already painting for him by 1691 and continued to do so until his death some seven years later."
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH8,
                "source_span": "line 279; print p. 233",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第8章注5；印刷页233；OCR L423",
            "sentence_summary": (
                "Haskell转述 Fogolari 1937 所刊 Loth 1691年8月14日书信，并报告一项拟临摹提香《圣彼得殉难》、"
                "1693年送自画像至佛罗伦萨，以及《亚伯之死》和费迪南德1716年清单等信息。Fogolari、该信及目录未在本任务中独立查阅；"
                "这些指涉分别保留为关系候选和端点候选。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 423",
                    "text": (
                        "5 Fogolari, 1937, publishes a letter from Loth of 14 August 1691 thanking the Prince for a present of oil and wine "
                        "and telling him that he is about to embark on a copy of Titian’s St Peter Martyr. In 1693 he sent his self portrait "
                        "to Florence. The Pitti contains a Death of Abel by him and six of his pictures are recorded in Ferdinand’s collection "
                        "in the 1716 inventory—see p. 239, note 5, and also Fogolari, 1937, Letters 22 and 77. See catalogue entries in Ewald, 1965."
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH8,
                "source_span": "line 423; print p. 233, note 5",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页265；OCR L295",
            "sentence_summary": (
                "Haskell在第265页以全名 Johann Karl Loth 提及德国画家的宗教画作；原文 OCR 该行带有段落／括号残片，"
                "此处只用其姓名词组作为跨章身份锚点。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 295",
                    "text": "there are some religious canvases by the German Johann Karl Loth",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH9,
                "source_span": "line 295; print p. 265",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；L.csv#100–102；印刷页233、265n",
            "sentence_summary": (
                "L.csv#100 将 Johann Karl Loth 列为人物主项，页码为233和265注；另有“and Grand Prince Ferdinand”及“Death of Abel”两个子项。"
                "相关 S3 候选分别维持其当前待证状态，不据索引子项新造人物或作品身份。"
            ),
            "original_quotes": [
                {
                    "source_span": "index entry L.csv#100",
                    "text": "| Loth, Johann Karl |  |  |  | 233, 265n |",
                },
                {
                    "source_span": "index entry L.csv#101",
                    "text": "| Loth, Johann Karl |  | and Grand Prince Ferdinand |  | 233 |",
                },
                {
                    "source_span": "index entry L.csv#102",
                    "text": "| Loth, Johann Karl |  | Death of Abel |  | 233 |",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entries L.csv#100–102",
            },
        },
    ]
    frontmatter = {
        "title": "约翰·卡尔·洛特（Johann Karl Loth）",
        "name_en": "Johann Karl Loth",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch8 = f"[第8章 p.233](../../../{CH8})（L279、423）"
    ch9 = f"[第9章 p.265](../../../{CH9})（L295）"
    index = f"[书后索引](../../../{INDEX_FILE})（L.csv#100–102）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应书后索引人物主项“Loth, Johann Karl”（L.csv#100），其页码包括第8章 p.233 与第9章 p.265。第8章正文以 Karl Loth 称其为德国画家，记述其为 Grand Prince Ferdinand 作画；第9章以全名 Johann Karl Loth 提及其宗教画作。第8章注5转述 Fogolari 1937 所刊书信及若干作品、清单信息，但该文献与原信未在本任务中独立查阅。此卡仅登记跨章人物身份；六条直接关系候选留待 S6 裁决。{ch8} {ch9} {index}

**English:** This card records the person entry “Loth, Johann Karl” (L.csv#100), indexed to Chapter 8, p.233 and Chapter 9, p.265. Chapter 8 calls him Karl Loth, identifies him as a German artist, and discusses his work for Grand Prince Ferdinand; Chapter 9 uses the full form Johann Karl Loth when mentioning religious canvases. Chapter 8 note 5 reports a letter and several works and inventory references through Fogolari 1937, which was not independently consulted for this task. This step registers the cross-chapter person identity only; six direct relationship candidates remain for S6 adjudication. {ch8} {ch9} {index}

### 身份边界

S3 人物组 `{GROUP}` 仅含 `cand-1442`，由第8章的 Karl Loth 与第9章的 Johann Karl Loth 跨章提及对应索引主项 L.csv#100。索引子项 L.csv#101（“and Grand Prince Ferdinand”；`cand-1443`）和 L.csv#102（“Death of Abel”；`cand-1444`）各自仍为 S3 `undecided`；本次 S4 不改其决定，也不另造关系／作品 KU。注5中的信件 `cand-7931` 是分立 archive 候选，S3 为 `new`、仍待 S4 登记；自画像 `cand-7933` 仍为待证 work 候选。

S3 person group `{GROUP}` contains only `cand-1442`, linking the Chapter 8 form Karl Loth and Chapter 9 form Johann Karl Loth to index main entry L.csv#100. Index subentry L.csv#101 (“and Grand Prince Ferdinand”; `cand-1443`) and L.csv#102 (“Death of Abel”; `cand-1444`) remain `undecided` at S3; this S4 action neither changes those decisions nor creates additional person or work KUs. The letter in note 5 (`cand-7931`) is a separate archive candidate with an S3 `new` decision, still awaiting S4; the self-portrait (`cand-7933`) remains an unresolved work candidate.

## 关系与证据

6条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。其中 `cand-7931` 是新 archive 端点，`cand-1444` 与 `cand-7933` 是待证 work 端点。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Johann Karl Loth's cross-chapter S3 person group in S4.")
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
    assert not any(
        row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL
        or (row.get("type") == "person" and (row.get("name_en") or "").casefold() == "johann karl loth")
        for row in manifest
    ), "Johann Karl Loth person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "L.csv#100"
    assert candidate["canonical_name"] == "Loth, Johann Karl"
    assert candidate["index_page_range"] == "233, 265n"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    assert alignment_by_id["cand-1443"]["decision"] == "undecided"
    assert alignment_by_id["cand-1444"]["decision"] == "undecided"
    assert alignment_by_id["cand-7931"]["decision"] == "new"
    assert alignment_by_id["cand-7933"]["decision"] == "undecided"

    ch8_text = (ROOT / CH8).read_text(encoding="utf-8-sig")
    ch9_text = (ROOT / CH9).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "among them Karl Loth" in ch8_text and "already painting for him by 1691" in ch8_text
    assert "letter from Loth of 14 August 1691" in ch8_text and "The Pitti contains a Death of Abel" in ch8_text
    assert "German Johann Karl Loth" in ch9_text
    assert "| Loth, Johann Karl |  |  |  | 233, 265n |" in index_text
    assert "| Loth, Johann Karl |  | and Grand Prince Ferdinand |  | 233 |" in index_text
    assert "| Loth, Johann Karl |  | Death of Abel |  | 233 |" in index_text

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
        "canonical_name": "约翰·卡尔·洛特",
        "name_en": "Johann Karl Loth",
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
        "\n\n<a id=\"s4-johann-karl-loth-cross-chapter-person\"></a>\n\n"
        "### S4 person：Johann Karl Loth 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-1442`（L.csv#100，pp.233、265n）沿用 S3 组 `{GROUP}`，映射至[约翰·卡尔·洛特人物卡]"
        f"(../../../{CARD_REL})。第8章出现 Karl Loth，第9章出现 Johann Karl Loth；全名、索引页码和 S2 提及锚点支持跨章同一人物映射。"
        "卡片只记录 Haskell 的书内说法；注5转述 Fogolari 1937，未独立查阅该文献或原信。\n\n"
        "索引附项 `cand-1443`（and Grand Prince Ferdinand）与 `cand-1444`（Death of Abel）仍为 S3 undecided；"
        "信件 archive `cand-7931` 是另一 new 组、待 S4；自画像 work `cand-7933` 仍待证。6条直接 relation_candidate 保留待 S6："
        + ", ".join(sorted(RELATION_CANDIDATES))
        + "。未新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Johann Karl Loth 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-1442`（L.csv#100）映射至[Johann Karl Loth 人物卡](../units/persons/johann-karl-loth.md)。"
        "第8章的 Karl Loth 与第9章的 Johann Karl Loth 对应索引同一人物主项。"
        "L.csv#101“and Grand Prince Ferdinand”与L.csv#102“Death of Abel”所对应候选仍待证；"
        "注5信件为分立 archive 候选，待 S4；自画像 work 候选仍待证。6条直接关系候选留待 S6，未登记正式关系。"
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
        print(f"S4 Johann Karl Loth dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"identity_group={GROUP}; candidates={len(group_rows)}; direct_relation_candidates={len(direct_relations)}")
        print("unresolved=index-subentry cand-1443/cand-1444; archive cand-7931 pending S4; work cand-7933 undecided")
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
