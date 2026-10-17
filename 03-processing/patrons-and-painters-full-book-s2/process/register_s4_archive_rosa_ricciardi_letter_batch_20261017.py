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
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_iv.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
ANCHOR = "s4-rosa-ricciardi-letters-batch-20261017"

ITEMS = (
    {
        "candidate_id": "cand-11572",
        "group": "archive-group-d50591c140c4",
        "ku_id": "units/archives/rosa-letter-to-ricciardi-1666-10-09",
        "card_rel": "04-knowledge/units/archives/rosa-letter-to-ricciardi-1666-10-09.md",
        "candidate_name": "Letter from Salvator Rosa to G. B. Ricciardi, 9 October 1666",
        "source_ref": "chp-5:05_CHP-5_sec_iv:l39-54#L40",
        "source_line": "L40",
        "title_cn": "萨尔瓦多·罗萨致吉安巴蒂斯塔·里恰尔迪的信（1666年10月9日）",
        "name_en": "Letter from Salvator Rosa to G. B. Ricciardi, 9 October 1666",
        "print_locator": "print p. 143, note 1",
        "source_span": "line 40; print p. 143, note 1",
        "quote": "1 Letter to Ricciardi of 9 October 1666—Limentani, 1950, p. 138.",
        "summary_cn": (
            "Haskell第5章注1提到1666年10月9日致Ricciardi的信，并引Limentani（1950）第138页；"
            "章节相连正文将该通信归于Salvator Rosa。信件与被引页面未独立查阅。"
        ),
        "summary_en": (
            "Chapter 5 note 1 cites a letter to Ricciardi dated 9 October 1666 and points to Limentani (1950), page 138; "
            "the connected passage identifies Salvator Rosa as the writer. Neither the letter nor the cited page was independently consulted."
        ),
        "boundary_cn": "题名为描述性工作题名，并非原信题名；书信作者由相连正文语境识别，未据此推定原件馆藏地或完整内容。",
        "boundary_en": "The title is a descriptive working title, not an original title. The writer is identified from the connected passage; no repository or full letter content is inferred.",
        "relation_ids": (
            "st-chp5-seciv-note-l40-p143-marker1",
            "st-chp5-l40-letter-authored-by",
            "st-chp5-l40-letter-addressed-to",
        ),
        "recipient_note": "Ricciardi is given in the note; Rosa is identified through linked body context.",
        "ocr_note": "",
    },
    {
        "candidate_id": "cand-11573",
        "group": "archive-group-9dfe4a51adaf",
        "ku_id": "units/archives/rosa-letter-to-ricciardi-1651-04-24",
        "card_rel": "04-knowledge/units/archives/rosa-letter-to-ricciardi-1651-04-24.md",
        "candidate_name": "Letter from Salvator Rosa to G. B. Ricciardi, 24 April 1651",
        "source_ref": "chp-5:05_CHP-5_sec_iv:l39-54#L48",
        "source_line": "L48",
        "title_cn": "萨尔瓦多·罗萨致吉安巴蒂斯塔·里恰尔迪的信（1651年4月24日）",
        "name_en": "Letter from Salvator Rosa to G. B. Ricciardi, 24 April 1651",
        "print_locator": "print p. 144, note 4",
        "source_span": "line 48; print p. 144, note 4",
        "quote": "4 De Rinaldis, 1939, p. 17—Letter of 24 April 1651.",
        "summary_cn": (
            "Haskell第5章注4以De Rinaldis（1939）第17页为据，列出1651年4月24日致Ricciardi的信；"
            "章节相连正文将该信归于Salvator Rosa。原信与刊本未独立查阅。"
        ),
        "summary_en": (
            "Chapter 5 note 4 cites De Rinaldis (1939), page 17, for a letter to Ricciardi dated 24 April 1651; "
            "the connected passage identifies Salvator Rosa as the writer. The letter and publication were not independently consulted."
        ),
        "boundary_cn": "题名为描述性工作题名，不是原信自题；作者和收信人依据该注与相连正文语境，未推定馆藏地或原件内容。",
        "boundary_en": "The title is descriptive, not an original title. The writer and recipient follow the note and connected passage; no repository or original-letter content is inferred.",
        "relation_ids": (
            "st-chp5-seciv-note-l48-p144-marker4",
            "st-chp5-l48-letter-authored-by",
            "st-chp5-l48-letter-addressed-to",
        ),
        "recipient_note": "The note gives the date and citation; the connected passage supplies the correspondence context.",
        "ocr_note": "",
    },
    {
        "candidate_id": "cand-11574",
        "group": "archive-group-4315528bb872",
        "ku_id": "units/archives/rosa-letter-to-ricciardi-1651-05-12",
        "card_rel": "04-knowledge/units/archives/rosa-letter-to-ricciardi-1651-05-12.md",
        "candidate_name": "Letter from Salvator Rosa to G. B. Ricciardi, 12 May 1651",
        "source_ref": "chp-5:05_CHP-5_sec_iv:l39-54#L49",
        "source_line": "L49",
        "title_cn": "萨尔瓦多·罗萨致吉安巴蒂斯塔·里恰尔迪的信（1651年5月12日）",
        "name_en": "Letter from Salvator Rosa to G. B. Ricciardi, 12 May 1651",
        "print_locator": "print p. 144, note 5",
        "source_span": "line 49; print p. 144, note 5",
        "quote": "5 ibid., p. 19—Letter of 12 May 1Ó51.",
        "summary_cn": (
            "Haskell第5章注5以ibid.第19页为据，列出1651年5月12日致Ricciardi的信；"
            "章节相连正文将该信归于Salvator Rosa。书页OCR将年份识作1Ó51，印本文字读作1651；原信与刊本未独立查阅。"
        ),
        "summary_en": (
            "Chapter 5 note 5 cites ibid., page 19, for a letter to Ricciardi dated 12 May 1651; "
            "the connected passage identifies Salvator Rosa as the writer. The OCR reads 1Ó51, while the printed page reads 1651; "
            "the letter and publication were not independently consulted."
        ),
        "boundary_cn": "题名为描述性工作题名，不是原信自题。年份校读只处理Haskell书内OCR与印本差异，不表示核读了被引刊本或书信。",
        "boundary_en": "The title is descriptive, not an original title. The year reading resolves an OCR/print variation in Haskell's book and does not imply consultation of the cited publication or letter.",
        "relation_ids": (
            "st-chp5-seciv-note-l49-p144-marker5",
            "st-chp5-l49-letter-authored-by",
            "st-chp5-l49-letter-addressed-to",
        ),
        "recipient_note": "The note supplies the date and locator; author/recipient roles are linked to the surrounding book passage.",
        "ocr_note": "OCR: 1Ó51；印本：1651。",
    },
    {
        "candidate_id": "cand-11575",
        "group": "archive-group-45db0f263e84",
        "ku_id": "units/archives/rosa-letter-to-ricciardi-1662-05-13",
        "card_rel": "04-knowledge/units/archives/rosa-letter-to-ricciardi-1662-05-13.md",
        "candidate_name": "Letter from Salvator Rosa to G. B. Ricciardi, 13 May 1662",
        "source_ref": "chp-5:05_CHP-5_sec_iv:l39-54#L50",
        "source_line": "L50",
        "title_cn": "萨尔瓦多·罗萨致吉安巴蒂斯塔·里恰尔迪的信（1662年5月13日）",
        "name_en": "Letter from Salvator Rosa to G. B. Ricciardi, 13 May 1662",
        "print_locator": "print p. 144, note 6",
        "source_span": "line 50; print p. 144, note 6",
        "quote": "6 Bottari, I, p. 450. Letter of 13 May 1662.",
        "summary_cn": (
            "Haskell第5章注6将1662年5月13日致Ricciardi的信定位至Bottari卷I第450页；"
            "章节相连正文将该信归于Salvator Rosa。原信与Bottari刊本未独立查阅。"
        ),
        "summary_en": (
            "Chapter 5 note 6 locates a letter to Ricciardi dated 13 May 1662 in Bottari, volume I, page 450; "
            "the connected passage identifies Salvator Rosa as the writer. Neither the letter nor Bottari's edition was independently consulted."
        ),
        "boundary_cn": "题名为描述性工作题名，不是原信自题；作者和收信人依据脚注及相连正文语境，不推定原件或刊本内容。",
        "boundary_en": "The title is descriptive, not an original title. Writer and recipient follow the note and connected passage; no original or edition content is inferred.",
        "relation_ids": (
            "st-chp5-seciv-note-l50-p144-marker6",
            "st-chp5-l50-letter-authored-by",
            "st-chp5-l50-letter-addressed-to",
        ),
        "recipient_note": "The note gives the letter date and Bottari locator; the connected passage supplies the correspondence roles.",
        "ocr_note": "",
    },
    {
        "candidate_id": "cand-11576",
        "group": "archive-group-08e32659351b",
        "ku_id": "units/archives/rosa-letter-to-ricciardi-1664-05-21",
        "card_rel": "04-knowledge/units/archives/rosa-letter-to-ricciardi-1664-05-21.md",
        "candidate_name": "Letter from Salvator Rosa to G. B. Ricciardi, 21 May 1664",
        "source_ref": "chp-5:05_CHP-5_sec_iv:l39-54#L51",
        "source_line": "L51",
        "title_cn": "萨尔瓦多·罗萨致吉安巴蒂斯塔·里恰尔迪的信（1664年5月21日）",
        "name_en": "Letter from Salvator Rosa to G. B. Ricciardi, 21 May 1664",
        "print_locator": "print p. 145, note 1",
        "source_span": "line 51; print p. 145, note 1",
        "quote": "1 De Rinaldis, 1939, p. 164—Letter ofZI May 1664.",
        "summary_cn": (
            "Haskell第5章注1以De Rinaldis（1939）第164页为据，列出1664年5月21日的信；"
            "收信人由章节相连正文语境识别为Ricciardi，作者为Salvator Rosa。OCR将日期读作ZI，印本文字读作21；原信与刊本未独立查阅。"
        ),
        "summary_en": (
            "Chapter 5 note 1 cites De Rinaldis (1939), page 164, for a letter dated 21 May 1664; "
            "the connected passage identifies Ricciardi as recipient and Salvator Rosa as writer. The OCR reads ZI, while the printed page reads 21; "
            "the letter and publication were not independently consulted."
        ),
        "boundary_cn": "题名为描述性工作题名，不是原信自题；本注不明写收信人，Ricciardi身份来自相连正文语境。OCR与印本日期异文仅按书页校读。",
        "boundary_en": "The title is descriptive, not an original title. This note does not name the recipient; Ricciardi is identified from the connected passage. The date variant is resolved only against the printed book page.",
        "relation_ids": (
            "st-chp5-seciv-note-l51-p145-marker1",
            "st-chp5-l51-letter-authored-by",
            "st-chp5-l51-letter-addressed-to",
        ),
        "recipient_note": "Recipient is contextual in the connected passage and is not named in the footnote itself.",
        "ocr_note": "OCR: ZI May 1664；印本：21 May 1664。",
    },
    {
        "candidate_id": "cand-11954",
        "group": "archive-group-1ae78d2d6f6e",
        "ku_id": "units/archives/rosa-letter-to-ricciardi-1651-05-27",
        "card_rel": "04-knowledge/units/archives/rosa-letter-to-ricciardi-1651-05-27.md",
        "candidate_name": "Letter from Salvator Rosa to G. B. Ricciardi, 27 May 1651",
        "source_ref": "chp-5:05_CHP-5_sec_iv:l39-54#L41",
        "source_line": "L41",
        "title_cn": "萨尔瓦多·罗萨致吉安巴蒂斯塔·里恰尔迪的信（1651年5月27日）",
        "name_en": "Letter from Salvator Rosa to G. B. Ricciardi, 27 May 1651",
        "print_locator": "print p. 143, note 2",
        "source_span": "line 41; print p. 143, note 2",
        "quote": (
            "2 Baldinucci, VI, 1728, p. 581. Rosa referred to himself as a Stoic in a letter to Ricciardi "
            "dated 27 May 1651—Limentani, 1950, p. 79."
        ),
        "summary_cn": (
            "Haskell第5章注2称Rosa于1651年5月27日致Ricciardi的信中自称Stoic，并引Limentani（1950）第79页。"
            "原信与被引页面未独立查阅。"
        ),
        "summary_en": (
            "Chapter 5 note 2 says Rosa described himself as a Stoic in a letter to Ricciardi dated 27 May 1651 and cites Limentani (1950), page 79. "
            "Neither the letter nor the cited page was independently consulted."
        ),
        "boundary_cn": "题名为描述性工作题名，不是原信自题；本卡只记录Haskell的书内转引及定位，不扩展Stoic一语的思想史含义。",
        "boundary_en": "The title is descriptive, not an original title. This card records Haskell's citation and locator only and does not extend the historical meaning of the word Stoic.",
        "relation_ids": (
            "st-chp5-l41-letter-authored-by",
            "st-chp5-l41-letter-addressed-to",
        ),
        "recipient_note": "The source note itself names Rosa and Ricciardi.",
        "ocr_note": "",
    },
)


def make_card(item: dict) -> str:
    source = {
        "citation": BOOK_CITATION,
        "location": f"第5章；{item['print_locator']}；OCR {item['source_line']}",
        "sentence_summary": item["summary_cn"],
        "original_quotes": [{"source_span": item["source_line"], "text": item["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": item["source_span"],
        },
    }
    frontmatter = {
        "title": f"{item['title_cn']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": [source],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[第5章书内来源](../../../{SOURCE_FILE})（{item['source_line']}；{item['print_locator']}）"
    endpoints = (
        "- 作者：萨尔瓦多·罗萨（`cand-2236` → `units/persons/salvator-rosa`）\n"
        "- 收信人：吉安巴蒂斯塔·里恰尔迪（`cand-2187` → `units/persons/giambattista-ricciardi`）"
    )
    if len(item["relation_ids"]) == 3:
        endpoints += "\n- 书目引注端点：Haskell 本书（`cand-2962` → `units/archives/patrons-and-painters`）"
    relation_lines = "\n".join(f"- `{sid}`" for sid in item["relation_ids"])
    body = f"""## 内容

### 描述

**中文：** {item['summary_cn']} {source_link}

**English:** {item['summary_en']} {source_link}

### 文献身份边界

**中文：** {item['boundary_cn']} {item['recipient_note']} {item['ocr_note']}

**English:** {item['boundary_en']} {item['recipient_note']} {item['ocr_note']}

原书未给该信独立原题；中文名称为忠实描述性暂题，信件及所引刊本均未在本批独立查阅。

### 端点映射

{endpoints}

## 关系与证据

本卡不新增正式关系。以下S2关系候选保留在`book-statements.jsonl`，待S6复核：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register six dated Rosa-Ricciardi correspondence identities as archive KUs.")
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
    statements = sync.load_statements()
    all_candidate_ids = {item["candidate_id"] for item in ITEMS}
    expected_relation_ids = {sid for item in ITEMS for sid in item["relation_ids"]}
    actual_relation_ids = {
        row["statement_id"]
        for row in statements
        if (row.get("subject_candidate_id") in all_candidate_ids or row.get("object_candidate_id") in all_candidate_ids)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual_relation_ids == expected_relation_ids, (actual_relation_ids, expected_relation_ids)
    assert alignment_by_id["cand-2236"].get("ku_id") == "units/persons/salvator-rosa"
    assert alignment_by_id["cand-2187"].get("ku_id") == "units/persons/giambattista-ricciardi"
    assert alignment_by_id["cand-2962"].get("ku_id") == "units/archives/patrons-and-painters"

    registration_states = []
    for item in ITEMS:
        cid = item["candidate_id"]
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "archive"
        assert candidate.get("canonical_name") == item["candidate_name"], (cid, candidate.get("canonical_name"))
        assert candidate.get("candidate_source_ref") == item["source_ref"]
        assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == item["group"]
        group_members = {
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        card_path = ROOT / item["card_rel"]
        name_matches = [
            row for row in manifest
            if row.get("type") == "archive" and (row.get("name_en") or "").casefold() == item["name_en"].casefold()
        ]
        assert len(name_matches) <= 1
        existing = (
            card_path.exists()
            and item["card_rel"] in accepted_paths
            and any(row.get("ku_id") == item["ku_id"] and row.get("card_path") == item["card_rel"] for row in manifest)
            and alignment.get("ku_id") == item["ku_id"]
        )
        registration_states.append(existing)
        if not existing:
            assert not card_path.exists() and item["card_rel"] not in accepted_paths
            assert not name_matches
            source = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
            assert item["quote"] in source, (cid, item["source_line"])

    if all(registration_states):
        print("ALREADY REGISTERED: 6 dated letters; 6 archive groups; 6 candidate mappings; 17 relation candidates remain non-formal.")
        return 0
    assert not any(registration_states), "partial batch registration detected; inspect cards and mappings before proceeding"

    planned_alignment = [dict(row) for row in alignments]
    for item in ITEMS:
        target = next(
            row for row in planned_alignment
            if row.get("candidate_id") == item["candidate_id"] and not row.get("external_source")
        )
        target["ku_id"] = item["ku_id"]
        target["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."
    planned_manifest = list(manifest)
    for item in ITEMS:
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "archive",
            "canonical_name": item["title_cn"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_rows = []
    result_rows = []
    for item in ITEMS:
        process_rows.append(
            f"- `{item['candidate_id']}`沿用S3组`{item['group']}`，登记为"
            f"[{item['name_en']}](../../../{item['card_rel']})。依据限于{item['print_locator']}；"
            f"原信及所引刊本未在本批独立查阅。关系候选{', '.join(f'`{sid}`' for sid in item['relation_ids'])}保留待S6。"
        )
        result_rows.append(
            f"- `{item['candidate_id']}` → [书信卡](../units/archives/{Path(item['card_rel']).name})；"
            "原题未给，工作题名为描述性暂题，原信及刊本未独立查阅。"
        )
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 archive：Rosa–Ricciardi 分日期书信身份登记（2026-10-17）\n\n"
        + "\n".join(process_rows)
        + "\n\n六个日期各作为独立书信身份组登记，没有合并成通信集。通信双方复用已映射人物KU；"
        "11572等候选中由正文语境补出的作者／收信人继续按相应S2语境限定。Haskell转引的Limentani、De Rinaldis、Bottari页码未在本批复核；"
        "OCR与印本日期差异见各卡。没有写入正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 archive：Rosa–Ricciardi 六封分日期书信登记（2026-10-17）\n\n"
        + "\n".join(result_rows)
        + "\n六个S3 `new` 组各登记为一个archive KU；日期不同，未合并为通信集。17条书内关系候选均未转为正式关系；"
        "作者、收信人和被引刊物的证据范围见卡片与`book-statements.jsonl`。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    for item in sorted(ITEMS, key=lambda value: value["card_rel"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > item["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {item['card_rel']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("S4 Rosa-Ricciardi archive dry-run passed")
        for item in ITEMS:
            print(f"  {item['candidate_id']} -> {item['ku_id']} ({item['group']})")
        print("groups=6; candidate_mappings=6; relation_candidates=17; formal_relations_added=0")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,}->{len(planned_manifest):,}"
        )
        print("no files changed")
        return 0

    for item in ITEMS:
        (ROOT / item["card_rel"]).write_text(make_card(item), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=6; candidate_mappings=6; registered="
        f"{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
