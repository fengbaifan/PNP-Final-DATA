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
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

ITEMS = (
    {
        "candidate_ids": ("cand-9831",),
        "group": "archive-group-af4602857b00",
        "ku_id": "units/archives/zanetti-letter-to-gori-1738-08-23-marucelliana-b-viii-13",
        "card_rel": "04-knowledge/units/archives/zanetti-letter-to-gori-1738-08-23-marucelliana-b-viii-13.md",
        "canonical_name": (
            "扎内蒂致戈里的信（1738年8月23日；Biblioteca Marucelliana, "
            "MSS. B. VIII, 13, p. 289r）"
        ),
        "name_en": (
            "Letter from A. M. Zanetti to A. F. Gori, 23 August 1738 "
            "(Biblioteca Marucelliana, MSS. B. VIII, 13, p. 289r)"
        ),
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "source_line": "L339",
        "print_locator": "print p. 328, note 2",
        "location": "第10章；印刷页328；注2；OCR L339",
        "source_span": "line 339; print p. 328, note 2",
        "original_quote": (
            "Letter from A. M. Zanetti to A. F. Gori of 23 August 1738 in Biblioteca "
            "Marucelliana, Florence —MSS. B. VIII, 13 p. 289c."
        ),
        "summary_cn": (
            "Haskell第10章注2列出一封1738年8月23日由A. M. Zanetti致A. F. Gori的信，" 
            "定位为Biblioteca Marucelliana, Florence, MSS. B. VIII, 13。书中印本文字读作p. 289r，" 
            "OCR转录作p. 289c。信件及馆藏目录未在本任务中独立查阅。"
        ),
        "summary_en": (
            "Chapter 10 note 2 identifies a letter from A. M. Zanetti to A. F. Gori dated "
            "23 August 1738 and locates it at Biblioteca Marucelliana, Florence, MSS. B. VIII, 13. "
            "The printed page reads p. 289r, while the OCR transcribes p. 289c. Neither the letter "
            "nor the repository catalogue was independently consulted for this task."
        ),
        "boundary_cn": (
            "本卡依书内日期、双方原书形式及馆藏号登记一件具体书信；中英文题名均为描述性工作题名，" 
            "不是原信题名。A. M. Zanetti、A. F. Gori及Biblioteca Marucelliana的端点映射分别保留在候选 "
            "cand-2857、cand-1214、cand-9493；尚未完成的端点身份不据此推定。"
        ),
        "boundary_en": (
            "This card identifies one specific letter from the date, the forms of the names given in the book, "
            "and the shelfmark. Both titles are descriptive working titles, not an original title. Endpoint "
            "mappings for A. M. Zanetti, A. F. Gori, and Biblioteca Marucelliana remain recorded as candidates "
            "cand-2857, cand-1214, and cand-9493; unresolved endpoint identities are not inferred here."
        ),
        "relation_ids": (
            "st-chp10-p328-n02-letter-authored-by-zanetti",
            "st-chp10-p328-n02-letter-addressed-to-gori",
            "st-chp10-p328-n02-letter-held-by-marucelliana",
        ),
        "endpoint_notes": (
            ("作者", "A. M. Zanetti", "cand-2857", "S3身份待决"),
            ("收信人", "A. F. Gori", "cand-1214", "S3身份待决"),
            ("馆藏机构", "Biblioteca Marucelliana", "cand-9493", "S3 new，S4待登记"),
        ),
        "shelfmark_note": "印本文字为p. 289r；OCR为p. 289c。此差异只涉及Haskell书内页码转录，不表示已查阅手稿。",
    },
    {
        "candidate_ids": ("cand-9832",),
        "group": "archive-group-8cfaf6d6bb80",
        "ku_id": "units/archives/biffi-letter-to-signor-vacchelli-1773-cremona-aa-i-4",
        "card_rel": "04-knowledge/units/archives/biffi-letter-to-signor-vacchelli-1773-cremona-aa-i-4.md",
        "canonical_name": (
            "吉安巴蒂斯塔·比菲致瓦凯利先生的未刊信（1773年；Biblioteca Governativa, "
            "Cremona, MSS. aa.I.4）"
        ),
        "name_en": (
            "Unpublished letter from Giambattista Biffi to Signor Vacchelli (1773; "
            "Biblioteca Governativa, Cremona, MSS. aa.I.4)"
        ),
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "source_line": "L341",
        "print_locator": "print p. 328, note 5",
        "location": "第10章；印刷页328；注5；OCR L341",
        "source_span": "line 341; print p. 328, note 5",
        "original_quote": (
            "In an unpublished letter to Signor Vacchelli in 1773 in the Biblioteca Govcrnativa, "
            "Cremona, MSS. aa.I.4."
        ),
        "summary_cn": (
            "Haskell第10章注5称Giambattista Biffi于1773年致Signor Vacchelli一封未刊信，" 
            "书中定位为Biblioteca Governativa, Cremona, MSS. aa.I.4；Haskell说明该信信息由Franco Venturi提供，" 
            "并转述其中对Zuccarelli的赞语。手稿未在本任务中独立查阅。来源OCR将馆名转成Govcrnativa，" 
            "印本文字为Governativa。"
        ),
        "summary_en": (
            "Chapter 10 note 5 describes an unpublished 1773 letter from Giambattista Biffi to Signor Vacchelli, "
            "located at Biblioteca Governativa, Cremona, MSS. aa.I.4. Haskell says the information came from "
            "Franco Venturi and reports the letter's praise of Zuccarelli. The manuscript was not independently "
            "consulted. The OCR reads Govcrnativa; the printed name is Governativa."
        ),
        "boundary_cn": (
            "题名据Haskell提供的描述性信息拟定，不是原信题名。卡片只记录Haskell对未刊信的著录及其转述链，" 
            "不声称直接读过信件。原书称收信人为Signor Vacchelli；候选cand-2674所列Giuliano Vacchelli身份尚未对齐。"
        ),
        "boundary_en": (
            "The title is descriptive and follows Haskell's report; it is not an original title. The card records "
            "Haskell's description of an unpublished letter and his reporting chain, not direct consultation of the "
            "letter. The book calls the recipient Signor Vacchelli; the identity represented by candidate cand-2674, "
            "Giuliano Vacchelli, remains unaligned."
        ),
        "relation_ids": (
            "st-chp10-p328-n05-letter-authored-by-biffi",
            "st-chp10-p328-n05-letter-addressed-to-vacchelli",
            "st-chp10-p328-n05-letter-held-by-cremona-library",
            "st-chp10-p328-n05-letter-has-subject-zuccarelli",
        ),
        "endpoint_notes": (
            ("作者", "Giambattista Biffi", "cand-0373", "已映射至units/persons/giambattista-biffi"),
            ("收信人", "Signor Vacchelli", "cand-2674", "S3身份待决"),
            ("馆藏机构", "Biblioteca Governativa, Cremona", "cand-8556", "S3 new，S4待登记"),
            ("所涉人物", "Francesco Zuccarelli", "cand-2879", "已映射至units/persons/francesco-zuccarelli"),
        ),
        "shelfmark_note": (
            "Haskell称此信未刊，并说明信息由Franco Venturi提供。OCR馆名Govcrnativa依印本文字校作Governativa；"
            "原信和馆藏目录未独立查阅。"
        ),
    },
    {
        "candidate_ids": ("cand-11571",),
        "group": "archive-group-dfcf90ed1ec3",
        "ku_id": "units/archives/rosa-letter-to-ricciardi-1660-04-02",
        "card_rel": "04-knowledge/units/archives/rosa-letter-to-ricciardi-1660-04-02.md",
        "canonical_name": "萨尔瓦多·罗萨致吉安巴蒂斯塔·里恰尔迪的信（1660年4月2日）",
        "name_en": "Letter from Salvator Rosa to G. B. Ricciardi, 2 April 1660",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
        "source_line": "L163",
        "print_locator": "print p. 142, note 4; PDF physical p. 27",
        "location": "第5章；印刷页142；注4；OCR L163",
        "source_span": "line 163; print p. 142, note 4; PDF physical p. 27",
        "original_quote": (
            "Letter from Salvator Rosa to G. B. Ricciardi dated 2 April 1660—de R...Jdis, 1939, p. 109."
        ),
        "summary_cn": (
            "Haskell第5章注4指出Salvator Rosa于1660年4月2日致G. B. Ricciardi的信，并将读者引向一项1939年刊本第109页。"
            "该刊本姓氏在书页图像中部分难辨，原信与被引刊本均未独立查阅。"
        ),
        "summary_en": (
            "Chapter 5 note 4 identifies a letter from Salvator Rosa to G. B. Ricciardi dated 2 April 1660 and points "
            "to a 1939 publication, page 109. The cited author's surname is partly illegible in the book image; neither "
            "the letter nor the cited publication was independently consulted."
        ),
        "boundary_cn": (
            "题名据书内日期与通信双方拟定，不是原信题名。被引1939年刊本仅按原书可辨形式保留为de R...Jdis，" 
            "对应候选cand-6205仍待决；本卡不推补作者全名、刊名或刊本身份。"
        ),
        "boundary_en": (
            "The title is descriptive, based on the date and correspondents given in the book, and is not an original title. "
            "The cited 1939 publication is retained in the book's partly legible form, de R...Jdis; candidate cand-6205 "
            "remains undecided. No full author name, title, or publication identity is supplied by inference."
        ),
        "relation_ids": (
            "st-chp5-notes-l163-rosa-ricciardi-letter",
            "st-chp5-l163-letter-authored-by",
            "st-chp5-l163-letter-addressed-to",
            "st-chp5-notes-l126-165-l163-letter-published-in-de-rinaldis",
        ),
        "endpoint_notes": (
            ("作者", "Salvator Rosa", "cand-2236", "已映射至units/persons/salvator-rosa"),
            ("收信人", "G. B. Ricciardi", "cand-2187", "已映射至units/persons/giambattista-ricciardi"),
            ("被引刊本", "de R...Jdis (1939), p. 109", "cand-6205", "S3身份待决"),
        ),
        "shelfmark_note": (
            "原书仅给出部分难辨的刊者姓氏形式de R...Jdis；引用目标cand-6205保持待决。"
            "书信和刊本未独立查阅。"
        ),
    },
)


def make_card(item: dict) -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary_cn"],
            "original_quotes": [
                {"source_span": item["source_line"], "text": item["original_quote"]}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["source_file"],
                "source_span": item["source_span"],
            },
        }
    ]
    frontmatter = {
        "title": f"{item['canonical_name']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#s4-archive-crosschapter-letters-20261017",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[书内来源](../../../{item['source_file']})（{item['source_line']}；{item['print_locator']}）"
    endpoint_list = "\n".join(
        f"- **{role}：** {name}（`{candidate_id}`；{status}）"
        for role, name, candidate_id, status in item["endpoint_notes"]
    )
    relation_list = "\n".join(f"- `{statement_id}`" for statement_id in item["relation_ids"])
    body = f"""## 内容

### 描述

**中文：** {item['summary_cn']} {source_link}

**English:** {item['summary_en']} {source_link}

### 文献身份边界

**中文：** {item['boundary_cn']} {item['shelfmark_note']}

**English:** {item['boundary_en']} {item['shelfmark_note']}

## 关系与证据

本卡不新增正式关系。以下为已有 S2 关系候选，保留对应端点候选和身份状态，待 S6 按证据裁决：

{endpoint_list}

关系候选：

{relation_list}
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three source-cited correspondence items as archive KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    statements = sync.load_statements()

    all_candidates = {candidate_id for item in ITEMS for candidate_id in item["candidate_ids"]}
    expected_relation_ids = {sid for item in ITEMS for sid in item["relation_ids"]}
    actual_relation_ids = {
        row["statement_id"]
        for row in statements
        if (row.get("subject_candidate_id") in all_candidates or row.get("object_candidate_id") in all_candidates)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual_relation_ids == expected_relation_ids, (actual_relation_ids, expected_relation_ids)

    registered_flags = []
    for item in ITEMS:
        card_path = ROOT / item["card_rel"]
        manifest_matches = [
            row for row in manifest
            if row.get("ku_id") == item["ku_id"] or row.get("card_path") == item["card_rel"]
        ]
        candidate_matches = [
            row for row in manifest
            if row.get("type") == "archive" and (row.get("name_en") or "").casefold() == item["name_en"].casefold()
        ]
        assert len(candidate_matches) <= 1, f"duplicate archive identity: {item['name_en']}"
        existing_alignment = [alignment_by_id[cid].get("ku_id") == item["ku_id"] for cid in item["candidate_ids"]]
        registered_flags.append(
            bool(manifest_matches)
            and card_path.exists()
            and all(existing_alignment)
            and item["card_rel"] in accepted_paths
        )

    if all(registered_flags):
        planned_manifest = [dict(row) for row in manifest]
        changed_names = []
        for item in ITEMS:
            matches = [row for row in planned_manifest if row.get("ku_id") == item["ku_id"]]
            assert len(matches) == 1, (item["ku_id"], len(matches))
            if matches[0].get("canonical_name") != item["canonical_name"]:
                changed_names.append(item["ku_id"])
                matches[0]["canonical_name"] = item["canonical_name"]
        changed_cards = []
        for item in ITEMS:
            card_path = ROOT / item["card_rel"]
            current = card_path.read_text(encoding="utf-8-sig")
            assert current.startswith("---\n")
            expected = make_card(item)
            if current != expected:
                changed_cards.append(item["card_rel"])
                if args.apply:
                    card_path.write_text(expected, encoding="utf-8-sig", newline="\n")
        process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
        process_anchor = "s4-archive-letter-title-localization-20261017"
        process_note = (
            f"\n\n<a id=\"{process_anchor}\"></a>\n\n"
            "### S4 archive：三张书信卡中文描述性题名规范化（2026-10-17）\n\n"
            "- 扎内蒂—戈里、比菲—瓦凯利、罗萨—里恰尔迪三张卡的中文展示题名改为中文描述性表达，英文名字段保持原有书内形式。\n"
            "- 只调整展示题名与`ku-manifest.csv`中的对应`canonical_name`；S3身份组、KU路径、候选映射、证据范围及关系候选均未改变。\n"
        )
        process_changed = process_anchor not in process_text
        if process_changed:
            process_text += process_note
        if (changed_cards or changed_names or process_changed) and not args.apply:
            print("REGISTERED DATA FOUND, BUT TITLE NORMALIZATION NEEDS APPLY:")
            for path in changed_cards:
                print(f"  {path}")
            for ku_id in changed_names:
                print(f"  manifest canonical_name: {ku_id}")
            if process_changed:
                print("  process note: s4-archive-letter-title-localization-20261017")
            print("run --apply to update only these title fields and the process note")
            return 1
        if args.apply:
            if changed_names:
                sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
            if process_changed:
                PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
        if changed_cards:
            print(f"refreshed {len(changed_cards)} card(s); registration tables unchanged")
        if changed_names:
            print(f"updated {len(changed_names)} manifest canonical_name value(s)")
        if process_changed and args.apply:
            print("recorded title normalization in process/knowledge.md")
        else:
            if not changed_cards and not changed_names and not process_changed:
                print("ALREADY REGISTERED: 3 archive identity groups; 3 KU cards; 3 candidate mappings; 11 S2 relation candidates remain non-formal.")
        return 0
    assert not any(registered_flags), "partial registration detected; inspect the target records before proceeding"

    for item in ITEMS:
        assert not (ROOT / item["card_rel"]).exists(), item["card_rel"]
        assert item["card_rel"] not in accepted_paths, item["card_rel"]
        assert not any(
            row.get("ku_id") == item["ku_id"] or row.get("card_path") == item["card_rel"]
            for row in manifest
        ), f"target KU already exists: {item['ku_id']}"
        assert not any(
            row.get("type") == "archive" and (row.get("name_en") or "").casefold() == item["name_en"].casefold()
            for row in manifest
        ), f"archive identity already exists: {item['name_en']}"

        aligned_group_members = {
            row["candidate_id"]
            for row in alignments
            if row.get("candidate_id")
            and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == item["group"]
        }
        assert aligned_group_members == set(item["candidate_ids"]), (item["group"], aligned_group_members)

        for candidate_id in item["candidate_ids"]:
            candidate = candidate_by_id[candidate_id]
            alignment = alignment_by_id[candidate_id]
            assert candidate.get("suggested_type") == "archive", (candidate_id, candidate.get("suggested_type"))
            assert alignment.get("decision") == "new" and not alignment.get("ku_id"), (candidate_id, alignment)
            assert sync.get_group(alignment.get("resolution_note", "")) == item["group"]
            assert candidate.get("candidate_source_ref")

        chapter = (ROOT / item["source_file"]).read_text(encoding="utf-8-sig")
        assert item["original_quote"] in chapter, (item["source_file"], item["source_line"])

    planned_alignment = [dict(row) for row in alignments]
    for item in ITEMS:
        for candidate_id in item["candidate_ids"]:
            target = next(
                row for row in planned_alignment
                if row.get("candidate_id") == candidate_id and not row.get("external_source")
            )
            target["ku_id"] = item["ku_id"]
            target["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."

    planned_manifest = list(manifest)
    for item in ITEMS:
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "archive",
            "canonical_name": item["canonical_name"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    batch_anchor = "s4-archive-crosschapter-letters-20261017"
    process_entries = []
    result_entries = []
    for item in ITEMS:
        candidate_display = "、".join(f"`{cid}`" for cid in item["candidate_ids"])
        relation_display = "、".join(f"`{sid}`" for sid in item["relation_ids"])
        process_entries.append(
            f"- {candidate_display}：S3组`{item['group']}`登记为[档案卡](../../../{item['card_rel']})。"
            f"依据限于{item['print_locator']}；{item['shelfmark_note']} 未新增正式关系；"
            f"{relation_display}保留待S6核对端点与证据。"
        )
        result_entries.append(
            f"- {candidate_display} → [档案卡](../units/archives/{Path(item['card_rel']).name})；"
            f"身份范围及未独立查阅项见卡片。关系候选待S6。"
        )
    process_text += (
        f"\n\n<a id=\"{batch_anchor}\"></a>\n\n"
        "### S4 archive：跨章书信端点登记（2026-10-17）\n\n"
        + "\n".join(process_entries)
        + "\n\n本批仅登记S3已裁决为`new`的三组档案身份；Haskell书内转引或著录是当前证据范围，"
        "没有据此声称查阅原信、馆藏目录或被引刊本。尚未映射的作者、收信人、馆藏机构及刊本端点按卡片中的候选ID保留，"
        "所有关系候选仍在`book-statements.jsonl`，本批没有写入`relations.csv`或建立正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 archive：跨章书信身份登记（2026-10-17）\n\n"
        + "\n".join(result_entries)
        + "\n\n3个S3 `new` 档案组各登记为1个KU；来源仅为Haskell书内著录/转引，原信、馆藏目录或被引刊本未在本批独立查阅。"
        "11条已有关系候选未转为正式关系；未映射端点仍待相应S3/S4处理后再进入S6。\n\n"
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
        print("S4 archive cross-chapter letters dry-run passed")
        for item in ITEMS:
            print(f"  {item['candidate_ids']} -> {item['ku_id']} ({item['group']})")
        print("groups=3; candidate_mappings=3; S2 relation_candidates=11; formal_relations_added=0")
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
        f"applied: groups=3; candidate_mappings=3; registered="
        f"{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
