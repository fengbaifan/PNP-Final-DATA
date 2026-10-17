from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_three_crosschapter_person_endpoints_20261017 as prior  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = "S4-full-book-2026-10-17"
ANCHOR = "s3-s4-rezzonico-person-boundary-20261017"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

P254 = {
    "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    "line_start": 137,
    "line_end": 140,
    "location": "第9章，印刷页254，Markdown L137–140",
    "span": "Markdown lines 137–140; print p. 254",
    "quote_text": (
        "Aurelio, Lodovico’s father, was made\nProcuratore di S. Marco in 1751, and in that year bought one of the grandest palaces in\n"
        "Venice from the Bon family. Seven years later his brother Carlo was elected Pope as\nClement XIII."
    ),
}
P362 = {
    "file": "02-sources/02-Markdown/15_CHP-15_sec_i.md",
    "line_start": 18,
    "line_end": 19,
    "location": "第15章，印刷页362，Markdown L18–19",
    "span": "Markdown lines 18–19; print p. 362",
    "quote_text": "He was able to do this through the intervention of his cousin, Carlo Rezzonico, who became Pope Clement\nXIII in 1758.",
}

TARGETS = [
    {
        "candidate": "cand-2136",
        "group": "new-person:aurelio-rezzonico-02891a7a00",
        "ku": "units/persons/aurelio-rezzonico",
        "name_zh": "奥雷利奥·雷佐尼科",
        "name_en": "Aurelio Rezzonico",
        "index_entry": "Q-R.csv#63",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
        "index_quote": "Rezzonico, Aurelio",
        "index_span": "Q-R.csv#63; index row 65; p. 254",
        "chapters": "第9章；索引 Q-R.csv#63",
        "sources": [
            {
                **P254,
                "summary": "Haskell称Aurelio为Lodovico之父，记其1751年任Procuratore di S. Marco并购入Bon家族的一座宫殿。",
                "quote_text": "Aurelio, Lodovico’s father, was made\nProcuratore di S. Marco in 1751, and in that year bought one of the grandest palaces in\nVenice from the Bon family.",
            }
        ],
        "description_zh": (
            "本卡对应索引词头“Rezzonico, Aurelio”及第9章p.254所称Aurelio。Haskell称其为Lodovico之父，记其1751年任Procuratore di S. Marco并购入Bon家族的一座宫殿。"
            "同页另称其兄弟Carlo当选教皇Clement XIII；该兄弟是不同人物身份组，相关关系候选留待S6。"
        ),
        "description_en": (
            "This card represents the index heading “Rezzonico, Aurelio” and Aurelio named on chapter 9 p. 254. Haskell identifies him as Lodovico’s father and says he became Procuratore di S. Marco in 1751 and bought a palace from the Bon family that year. "
            "The same page names his brother Carlo as Pope Clement XIII; Carlo remains a distinct person identity group, and the relationship candidate awaits S6."
        ),
        "relation_ids": [
            "st-chp9-p254-aurelio-appointed-procuratore",
            "st-chp9-p254-aurelio-bought-bon-palace",
            "st-chp9-p254-aurelio-father-of-lodovico",
            "st-chp9-p254-carlo-rezzonico-elected-pope",
        ],
        "identity_extra": "本组指人物Aurelio Rezzonico；Rezzonico family KU与建筑/作品KU均为不同类型对象。",
        "s3_note": (
            "S3 review (2026-10-17): cand-2136 remains a distinct person group from cand-2137. Chapter 9 p.254 names Aurelio and separately calls Carlo his brother; no identity merge is made."
        ),
    },
    {
        "candidate": "cand-2137",
        "group": "new-person:carlo-rezzonico-clement-xiii-5d6bd47b3c",
        "ku": "units/persons/carlo-rezzonico-pope-clement-xiii",
        "name_zh": "卡洛·雷佐尼科",
        "name_en": "Carlo Rezzonico (Pope Clement XIII)",
        "index_entry": "Q-R.csv#64",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
        "index_quote": "Rezzonico, Carlo (Pope Clement XIII)",
        "index_span": "Q-R.csv#64; index row 66; CSV pages 254, 323; printed index transcription pp. 254, 362–363",
        "chapters": "第9、15章；索引 Q-R.csv#64 / 原索引转录",
        "sources": [
            {
                **P254,
                "summary": "Haskell称Aurelio的兄弟Carlo于1758年当选教皇Clement XIII。",
                "quote_text": "Seven years later his brother Carlo was elected Pope as\nClement XIII.",
            },
            {
                **P362,
                "summary": "Haskell明确给出Carlo Rezzonico全名，称其于1758年成为教皇Clement XIII。",
            },
            {
                "citation": INDEX_CITATION,
                "file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
                "line_start": 66,
                "line_end": 66,
                "location": "全书索引CSV Q-R.csv#64",
                "span": "Q-R.csv row 66; source CSV transcribes pages 254, 323",
                "summary": "Q-R.csv记录主项及页码254、323；与原索引转录页码362–363存在差异，原始列项未在此修改。",
                "quote_text": '"Rezzonico, Carlo (Pope Clement XIII)",,,,"254, 323"',
            },
            {
                "citation": INDEX_CITATION,
                "file": "02-sources/02-Markdown/22_CHP-22Index_intro.md",
                "line_start": 2654,
                "line_end": 2655,
                "location": "全书索引转录，Markdown L2654–2655",
                "span": "Index transcription lines 2654–2655",
                "summary": "原索引转录列出Carlo Rezzonico (Pope Clement XIII)并指向254、362–363页。",
                "quote_text": "                 Rezzonico, Carlo (Pope Clement XIII), 254,\n                    362-3                 ",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Rezzonico, Carlo (Pope Clement XIII)”及第9、15章中的Carlo Rezzonico。第9章p.254称他是Aurelio的兄弟并于1758年当选教皇Clement XIII；第15章p.362给出全名，p.363继续称“the Pope”。"
            "Q-R.csv将页码录为254、323，而原索引转录列为254、362–363；差异保留并以原索引转录和正文跨章锚点支持身份组。Clement XIII的see-under索引redirect不另立人物；Clement XI既有KU是不同教皇。"
        ),
        "description_en": (
            "This card represents the index heading “Rezzonico, Carlo (Pope Clement XIII)” and Carlo Rezzonico in chapters 9 and 15. Chapter 9 p. 254 calls him Aurelio’s brother and says he was elected Pope Clement XIII in 1758; chapter 15 p. 362 gives his full name and p. 363 continues with “the Pope.” "
            "Q-R.csv records pp. 254 and 323, while the original index transcription lists pp. 254 and 362–363; the discrepancy is retained, with the transcription and cross-chapter body anchors supporting this identity group. The Clement XIII see-under redirect is not a separate person; the existing Clement XI KU is a different pope."
        ),
        "relation_ids": [
            "st-chp9-p254-carlo-rezzonico-elected-pope",
            "st-chp15-p362-rezzonico-cousin-of-farsetti",
            "st-chp15-p362-rezzonico-intervention-enabled-farsetti-collection",
            "st-chp15-p363-pope-ceded-columns-to-farsetti",
        ],
        "identity_extra": "与Aurelio Rezzonico为两个人物组；Q-R.csv页码转录错误未静默覆盖。",
        "s3_note": (
            "S3 review (2026-10-17): cand-2137 is distinct from cand-2136 because p.254 explicitly names Carlo as Aurelio's brother; p.362 gives Carlo Rezzonico and Pope Clement XIII, and p.363 continues the same Pope. The Clement XIII redirect is not a separate person. Q-R.csv row 66 transcribes pp. 254, 323, while original index transcription lines 2654–2655 lists pp. 254, 362–363; preserve both readings and follow the latter in index_page_range."
        ),
    },
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def keep_bom_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def source_quote(item: dict) -> str:
    lines = (ROOT / item["file"]).read_text(encoding="utf-8-sig").splitlines()
    block = "\n".join(lines[item["line_start"] - 1 : item["line_end"]])
    quote = item.get("quote_text", block)
    assert quote in block, f"quote missing: {item['file']}:{item['line_start']}–{item['line_end']}"
    return quote


def make_card(t: dict) -> str:
    sources = []
    for item in t["sources"]:
        line_label = f"Markdown lines {item['line_start']}–{item['line_end']}" if item["line_start"] != item["line_end"] else f"Markdown line {item['line_start']}"
        sources.append(
            {
                "citation": item.get("citation", BOOK_CITATION),
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [{"source_span": line_label, "text": source_quote(item)}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": item["file"], "source_span": item["span"]},
            }
        )
    sources.append(
        {
            "citation": INDEX_CITATION,
            "location": f"全书索引 {t['index_entry']}",
            "sentence_summary": f"索引词头为“{t['index_quote']}”；定位见索引来源。",
            "original_quotes": [{"source_span": t["index_span"], "text": t["index_quote"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["index_file"], "source_span": t["index_span"]},
        }
    )
    frontmatter = yaml.safe_dump(
        {
            "title": f"{t['name_zh']}（{t['name_en']}）",
            "name_en": t["name_en"],
            "type": "person",
            "evidence_status": "source_backed",
            "sources": sources,
            "created": DATE,
            "updated": DATE,
            "process_ref": CARD_REF,
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    relation_rows = "\n".join(
        f"- [`{sid}`](../../tables/book-statements.jsonl)：S2直接关系候选，待S6审查。" for sid in t["relation_ids"]
    )
    return (
        f"---\n{frontmatter}---\n\n## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}\n\n**English:** {t['description_en']}\n\n"
        "## 关系与证据\n\n### 身份与外部链接\n\n"
        f"- S3人物组：候选 `{t['candidate']}`；查看 [alignment.csv](../../tables/alignment.csv) 与[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。本批未采用外部权威标识。{t['identity_extra']}\n\n"
        "### 关系记录\n\n当前没有登记在 `relations.csv` 的正式关系。以下直接关系候选仍待S6逐条审查：\n\n"
        f"{relation_rows}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Review and register the two distinct Rezzonico person groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by = {r["candidate_id"]: r for r in candidates}
    planned = [dict(r) for r in alignments]
    planned_by = {r["candidate_id"]: r for r in planned if r.get("candidate_id") and not r.get("external_source")}
    manifest_by = {r["ku_id"]: r for r in manifest}
    statements = {
        r["statement_id"]: r
        for r in (json.loads(line) for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    accepted_lines = read_text(ACCEPTED_PATH).splitlines()
    cards = {}
    relation_total = 0
    already_registered = []

    for t in TARGETS:
        cid, group, ku = t["candidate"], t["group"], t["ku"]
        c, a = candidate_by[cid], planned_by[cid]
        assert c["suggested_type"] == "person"
        assert a["decision"] == "new" and a.get("ku_id", "") in ("", ku)
        assert sync.get_group(a.get("resolution_note", "")) == group
        members = [
            r["candidate_id"]
            for r in alignments
            if r.get("candidate_id") and r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == group
        ]
        assert members == [cid], f"unexpected group members: {members}"
        card_path = ROOT / f"04-knowledge/{ku}.md"
        accepted_ref = f"- 04-knowledge/{ku}.md" in accepted_lines
        flags = [a.get("ku_id") == ku, ku in manifest_by, card_path.exists(), accepted_ref]
        assert len(set(flags)) == 1, f"partial registration state for {cid}: {flags}"
        is_registered = flags[0]
        already_registered.append(is_registered)
        name_matches = [
            r for r in manifest
            if r["type"] == "person" and r.get("name_en", "").casefold() == t["name_en"].casefold()
        ]
        assert not name_matches or (is_registered and all(r["ku_id"] == ku for r in name_matches))
        assert t["index_quote"].encode("ascii") in (ROOT / t["index_file"]).read_bytes()
        for item in t["sources"]:
            source_quote(item)
        for sid in t["relation_ids"]:
            assert sid in statements
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
        if is_registered:
            assert card_path.read_text(encoding="utf-8-sig") == make_card(t)
            assert a.get("process_ref") == PROCESS_REF
            assert f"S4 registration: group {group} mapped to {ku};" in a.get("resolution_note", "")
            assert c.get("detail") == t["s3_note"]
        else:
            a["ku_id"] = ku
            a["process_ref"] = PROCESS_REF
            a["resolution_note"] += f" {t['s3_note']} S4 registration: group {group} mapped to {ku}; {len(t['relation_ids'])} direct relation candidates remain pending S6."
            c["detail"] = t["s3_note"]
            cards[card_path] = make_card(t)
        relation_total += len(t["relation_ids"])

    planned_manifest = [dict(r) for r in manifest]
    newly_registered = sum(not registered for registered in already_registered)
    for t, registered in zip(TARGETS, already_registered):
        if registered:
            continue
        planned_manifest.append(
            {
                "ku_id": t["ku"],
                "type": "person",
                "canonical_name": f"{t['name_zh']}（{t['name_en']}）",
                "name_en": t["name_en"],
                "source_task": TASK,
                "card_path": f"04-knowledge/{t['ku']}.md",
            }
        )
    planned_manifest.sort(key=lambda r: r["ku_id"])
    planned_accepted = list(accepted_lines)
    for t, registered in zip(TARGETS, already_registered):
        if registered:
            continue
        planned_accepted = prior.insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")
    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before_totals = sync.build_type_table(before_stats)
    stats = sync.summarize_by_type(candidate_by.values(), planned)
    _, totals = sync.build_type_table(stats)
    assert len(planned_manifest) == len(manifest) + newly_registered
    assert totals["registered_groups"] == before_totals["registered_groups"] + newly_registered
    assert totals["pending_groups"] == before_totals["pending_groups"] - newly_registered
    assert totals["pending_members"] == before_totals["pending_members"] - newly_registered
    assert relation_total == 8

    process_text = read_text(PROCESS_PATH)
    anchor = f'<a id="{ANCHOR}"></a>'
    process_record = (
        "\n\n" + anchor + "\n\n"
        "### S3→S4 person：Aurelio 与 Carlo Rezzonico 身份分立复核与登记（2026-10-17）\n\n"
        "p.254明确称Carlo是Aurelio的兄弟，且Carlo当选Clement XIII；第15章p.362给出Carlo Rezzonico全名，p.363继续指称该教皇。两人维持独立S3 person new组；"
        "Rezzonico family、Ca’ Rezzonico地点及Tiepolo婚姻寓意作品保持不同KU。Clement XIII索引redirect不另立人物，既有Clement XI卡亦非同一人。"
        "Q-R.csv#64将页码录为254、323，而原索引转录列为254、362–363；两种读数均保留，candidate index_page_range沿原索引转录。分别登记两张人物卡，8条直接关系候选留待S6。\n\n"
        "| 候选 / S3身份组 | KU | 来源锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
    )
    for t in TARGETS:
        process_text += f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['chapters']} | {len(t['relation_ids'])} |\n"
    process_record += "\n"
    if anchor in process_text:
        assert all(t["candidate"] in process_text for t in TARGETS)
    else:
        process_text += process_record
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    result_heading = "### S3→S4 person：Aurelio 与 Carlo Rezzonico 身份分立复核与登记（2026-10-17）"
    if result_heading in result_text:
        assert all(t["candidate"] in result_text for t in TARGETS)
    else:
        result_text += "\n\n" + result_heading + "\n\n"
        for t in TARGETS:
            result_text += f"- `{t['candidate']}` / `{t['group']}` → [{t['name_zh']}（{t['name_en']}）](../{t['ku']}.md)；{t['chapters']}；{len(t['relation_ids'])}条直接关系候选留待S6。\n"
        result_text += "\n两人分立；本批未新增正式关系或外部身份断言。\n"

    if args.dry_run:
        state = "ALREADY REGISTERED" if newly_registered == 0 else "DRY-RUN OK"
        print(f"{state}: person groups={len(TARGETS)}; cards to create={len(cards)}; direct relation candidates={relation_total}")
        print(
            f"manifest: {len(manifest):,}->{len(planned_manifest):,}; registered groups: "
            f"{before_totals['registered_groups']:,}->{totals['registered_groups']:,}; "
            f"pending groups: {before_totals['pending_groups']:,}->{totals['pending_groups']:,}; "
            f"pending candidate mappings: {before_totals['pending_members']:,}->{totals['pending_members']:,}"
        )
        for t in TARGETS:
            print(f"{t['candidate']} -> {t['ku']}; group={t['group']}; {len(t['relation_ids'])} S6 candidates")
        if newly_registered == 0:
            return
        return

    for path, card in cards.items():
        path.write_bytes(card.encode("utf-8"))
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned)
    sync.write_csv(ENTITY_PATH, candidate_fields, candidates)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(f"APPLIED: Rezzonico person groups={len(TARGETS)}; cards={len(cards)}; registered={totals['registered_groups']:,}; pending={totals['pending_groups']:,}")


if __name__ == "__main__":
    main()
