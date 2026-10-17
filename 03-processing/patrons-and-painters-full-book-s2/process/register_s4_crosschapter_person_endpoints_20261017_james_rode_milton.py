from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_three_crosschapter_person_endpoints_20261017 as prior  # noqa: E402
import register_s4_crosschapter_person_endpoints_20261017_mazza_goya_mattielli as template  # noqa: E402

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
ANCHOR = "s4-crosschapter-person-endpoints-james-rode-milton-20261017"
DATE = "2026-10-17"

BOOK_CITATION = template.BOOK_CITATION
INDEX_CITATION = template.INDEX_CITATION

TARGETS = [
    {
        "candidate": "cand-1317",
        "group": "new-person:england-ii-james-of-95bd33d65c",
        "ku": "units/persons/james-ii-of-england",
        "name_zh": "英格兰国王詹姆斯二世",
        "name_en": "James II of England",
        "index_entry": "J，K.csv#1",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/J，K.csv",
        "index_line": 3,
        "index_quote": "James II of England",
        "index_span": "J，K.csv#1; CSV line 3; pp. 196, 280, 286",
        "chapters": "第7、10章；索引 J，K.csv#1",
        "relation_ids": [
            "st-chp10-p280-sheffield-supported-jamesii",
            "st-chp10-p286-powis-political-history",
            "st-chp7-p196-jamesii-demand_for_italian_artists",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "line_start": 55,
                "line_end": 55,
                "location": "第7章，印刷页196；OCR L55",
                "span": "OCR line 55; print p. 196",
                "summary": "Haskell将1685年后对意大利艺术家需求的增加与James H的复辟天主教政策联系起来。",
                "quote_text": "James H’s attempts to restore CathoEcism to England led to an unprecedented demand for the work of these Italian artists.",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 61,
                "line_end": 61,
                "location": "第10章，印刷页280；OCR L61",
                "span": "OCR line 61; print p. 280",
                "summary": "Haskell称John Sheffield曾坚定支持James II。",
                "quote_text": "he had been a staunch supporter of James II",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 200,
                "line_end": 200,
                "location": "第10章，印刷页286；OCR L200",
                "span": "OCR line 200; print p. 286",
                "summary": "Haskell称Lord Powis曾是James H最忠实的追随者之一，并记其遭逮捕。",
                "quote_text": "He had been one of James H’s most loyal followers, and as a consequence had been arrested on more than one occasion, the last time being during the Jacobite alarm of 1715.",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“James II of England”及第7、10章中的James II提及。索引列第7章p.196和第10章pp.280、286；第10章p.280写作“James II”，"
            "第7章p.196与第10章p.286的OCR转录作“James H”。本卡保留这些来源读法，不将书内对其政策及追随者的叙述升级为外部核验事实；相关关系候选留待S6审查。"
        ),
        "description_en": (
            "This card represents the index entry “James II of England” and the James II references in chapters 7 and 10. The index lists chapter 7 p.196 and chapter 10 pp.280 and 286; the OCR reads “James II” on p.280 and “James H” on pp.196 and 286. These readings are retained as transcribed. Haskell’s accounts of the king’s policies and followers are not presented as externally verified facts; the relation candidates remain for S6 review."
        ),
        "identity_extra": "索引全名列出第7章p.196及第10章pp.280、286；OCR“James H”异文保留。未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-1317 remains the source-local person group new-person:england-ii-james-of-95bd33d65c. Index J，K.csv#1 supplies the full name and pp.196/280/286; chapter 10 p.280 explicitly reads James II while chapter 7 p.196 and chapter 10 p.286 OCR read “James H”. No exact existing person KU matched; no external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-2207",
        "group": "new-person:bernhard-rode-f729759924",
        "ku": "units/persons/bernhard-rode",
        "name_zh": "贝恩哈德·罗德",
        "name_en": "Bernhard Rode",
        "index_entry": "Q-R.csv#134",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
        "index_line": 136,
        "index_quote": "Rode, Bernhard",
        "index_span": "Q-R.csv#134; CSV line 136; p. 410",
        "chapters": "第14、20章；索引 Q-R.csv#134",
        "relation_ids": [
            "st-chp14-p356-rode-influence-tiepolo-prospective",
            "st-chp14-p356-algarotti-provided-introduction-for-rode",
            "st-chp20-p410-tomb-painting-attribution-dispute",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "line_start": 102,
                "line_end": 102,
                "location": "第14章，印刷页356；OCR L102",
                "span": "OCR line 102; print p. 356",
                "summary": "Haskell称Algarotti为德国画家Rode提供赴意学习的介绍信，并说他将深受Tiepolo影响。",
                "quote_text": "the German painter Rode who was to be much influenced by Tiepolo",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "line_start": 202,
                "line_end": 202,
                "location": "Postscript，印刷页410；OCR L202",
                "span": "OCR line 202; print p. 410",
                "summary": "Haskell称早期作者将一幅画归于Bernhard Rode，但Marianne Roland-Michel认为更可能由意大利艺术家所作。",
                "quote_text": "earlier writers in ascribing it to Bernhard Rode, but Marianne Roland-Michel who has made a special study of it believes it much more likely to be by an Italian artist.",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Rode, Bernhard”及第14章的Rode与Postscript中的Bernhard Rode。第14章称Algarotti为德国画家Rode提供介绍信，并预计他会受到Tiepolo影响；"
            "Postscript记录早期作者将一幅画归于Rode，同时转述Marianne Roland-Michel认为更可能出自意大利艺术家。作者归属争议按原文保留；相关书内关系候选留待S6审查。"
        ),
        "description_en": (
            "This card represents the index entry “Rode, Bernhard” and the references to Rode in chapter 14 and Bernhard Rode in the Postscript. Chapter 14 says Algarotti provided an introduction for the German painter Rode and expected him to be influenced by Tiepolo. The Postscript reports an attribution to Bernhard Rode by earlier writers alongside Marianne Roland-Michel’s view that an Italian artist was more likely. The attribution dispute is retained as stated; the book’s relation candidates remain for S6 review."
        ),
        "identity_extra": "第14章p.356的Rode与Postscript p.410的Bernhard Rode及索引Q-R.csv#134相合；作品归属争议另行保留。未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-2207 remains the source-local person group new-person:bernhard-rode-f729759924. Chapter 14 p.356 calls Rode a German painter; the Postscript p.410 gives Bernhard Rode, matching index Q-R.csv#134. No exact existing person KU matched; no external identity source was accessed. The painting attribution dispute is a separate book claim, not an identity conflict."
        ),
    },
    {
        "candidate": "cand-1668",
        "group": "new-person:john-milton-f3686fb04d",
        "ku": "units/persons/john-milton",
        "name_zh": "约翰·弥尔顿",
        "name_en": "John Milton",
        "index_entry": "M.csv#208",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "index_line": 210,
        "index_quote": "Milton, John",
        "index_span": "M.csv#208; CSV line 210; pp. 58, 96",
        "chapters": "第2、4、10章；索引 M.csv#208",
        "relation_ids": [
            "st-chp2-seciv-l181-188-chi-soffre-speri-seen-by-milton",
            "st-chp4-sec-i-l20-24-milton-captivated-by-baroni",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "line_start": 183,
                "line_end": 183,
                "location": "第2章，印刷页58；OCR L183",
                "span": "OCR line 183; print p. 58",
                "summary": "Haskell称《Chi soffre, speri》曾由Milton观看。",
                "quote_text": "Chi soffre, speri which was seen by Milton",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
                "line_start": 22,
                "line_end": 22,
                "location": "第4章，印刷页96；OCR L22",
                "span": "OCR line 22; print p. 96",
                "summary": "Haskell称歌者Leonora Baroni曾使Milton倾心。",
                "quote_text": "the singer who so captivated Milton",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "line_start": 147,
                "line_end": 147,
                "location": "第10章，印刷页319；OCR L147",
                "span": "OCR line 147; print p. 319",
                "summary": "Haskell称Conti通过翻译Milton、Dryden等诗人表达对英国文学的欣赏；此页不在索引M.csv#208所列页码内。",
                "quote_text": "He showed his appreciation of English literature by translating Milton, Dryden and other poets",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Milton, John”及第2、4、10章中的Milton提及。第2章称《Chi soffre, speri》曾由Milton观看；第4章称歌者Leonora Baroni曾使Milton倾心；"
            "第10章另称Conti翻译Milton等英国诗人，该页未列于索引范围。前两项关系候选留待S6审查；这里不扩写其生平或著作目录。"
        ),
        "description_en": (
            "This card represents the index entry “Milton, John” and Milton references in chapters 2, 4, and 10. Chapter 2 says Milton saw Chi soffre, speri; chapter 4 calls Leonora Baroni a singer who captivated Milton; chapter 10 says Conti translated Milton among other English poets, on a page not listed in the index entry’s page range. The first two relation candidates remain for S6 review. No biography or works list is inferred here."
        ),
        "identity_extra": "第2、4章p.58、96与索引M.csv#208相合；第10章p.319另有Milton提及但不在索引页码范围内，保留该差异。未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-1668 remains the source-local person group new-person:john-milton-f3686fb04d. Index M.csv#208 gives John Milton and pp.58/96, matching the chapter 2 and 4 references; chapter 10 p.319 has an additional Milton mention outside that index locator. No exact existing person KU matched; no external identity source was accessed."
        ),
    },
]


def source_quote(item: dict) -> str:
    path = ROOT / item["file"]
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        # Preserve the index files' original Windows single-byte encoding.
        lines = path.read_text(encoding="cp1252").splitlines()
    block = "\n".join(lines[item["line_start"] - 1 : item["line_end"]])
    quote = item["quote_text"]
    assert quote in block, f"quote missing: {item['file']}:{item['line_start']}–{item['line_end']}"
    return quote


def main() -> None:
    parser = argparse.ArgumentParser(description="Register three reviewed cross-chapter person groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    template.TASK = TASK
    template.ANCHOR = ANCHOR
    template.CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    template.PROCESS_REF = PROCESS_REF
    template.DATE = DATE
    template.source_quote = source_quote

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by = {r["candidate_id"]: r for r in candidates}
    planned = [dict(r) for r in alignments]
    planned_by = {
        r["candidate_id"]: r
        for r in planned
        if r.get("candidate_id") and not r.get("external_source")
    }
    manifest_by = {r["ku_id"]: r for r in manifest}
    statements = {
        r["statement_id"]: r
        for r in (
            json.loads(line)
            for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    accepted_lines = template.read_text(ACCEPTED_PATH).splitlines()
    cards = {}
    registered_flags = []

    for t in TARGETS:
        cid, ku = t["candidate"], t["ku"]
        c, a = candidate_by[cid], planned_by[cid]
        assert c["suggested_type"] == "person"
        assert a["decision"] == "new" and a.get("ku_id", "") in ("", ku)
        assert sync.get_group(a.get("resolution_note", "")) == t["group"]
        members = [
            r["candidate_id"]
            for r in alignments
            if r.get("candidate_id")
            and not r.get("external_source")
            and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == t["group"]
        ]
        assert members == [cid], f"unexpected members in {t['group']}: {members}"
        card_path = ROOT / f"04-knowledge/{ku}.md"
        accepted_ref = f"- 04-knowledge/{ku}.md" in accepted_lines
        flags = [a.get("ku_id") == ku, ku in manifest_by, card_path.exists(), accepted_ref]
        assert len(set(flags)) == 1, f"partial registration state for {t['group']}: {flags}"
        registered = flags[0]
        registered_flags.append(registered)
        name_matches = [
            r for r in manifest
            if r["type"] == "person" and r.get("name_en", "").casefold() == t["name_en"].casefold()
        ]
        assert not name_matches or (registered and all(r["ku_id"] == ku for r in name_matches))
        for item in t["sources"]:
            source_quote(item)
        source_quote({"file": t["index_file"], "line_start": t["index_line"], "line_end": t["index_line"], "quote_text": t["index_quote"]})
        for sid in t["relation_ids"]:
            assert sid in statements
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
        if registered:
            assert card_path.read_text(encoding="utf-8-sig") == template.make_card(t)
            assert a.get("process_ref") == PROCESS_REF
            assert f"S4 registration: group {t['group']} mapped to {ku};" in a.get("resolution_note", "")
            assert c.get("detail") == t["s3_note"]
        else:
            a["ku_id"] = ku
            a["process_ref"] = PROCESS_REF
            a["resolution_note"] += (
                f" {t['s3_note']} S4 registration: group {t['group']} mapped to {ku}; "
                f"{len(t['relation_ids'])} direct relation candidates remain pending S6."
            )
            c["detail"] = t["s3_note"]
            cards[card_path] = template.make_card(t)

    newly_registered = sum(not flag for flag in registered_flags)
    planned_manifest = [dict(r) for r in manifest]
    for t, registered in zip(TARGETS, registered_flags):
        if not registered:
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
    for t, registered in zip(TARGETS, registered_flags):
        if not registered:
            planned_accepted = prior.insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")
    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before_totals = sync.build_type_table(before_stats)
    stats = sync.summarize_by_type(candidate_by.values(), planned)
    _, totals = sync.build_type_table(stats)
    assert len(planned_manifest) == len(manifest) + newly_registered
    assert totals["registered_groups"] == before_totals["registered_groups"] + newly_registered
    assert totals["pending_groups"] == before_totals["pending_groups"] - newly_registered
    assert totals["pending_members"] == before_totals["pending_members"] - newly_registered

    process_text = template.read_text(PROCESS_PATH)
    process_heading = "### S3→S4 person：James II、Bernhard Rode 与 John Milton 登记（2026-10-17）"
    process_record = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"{process_heading}\n\n"
        "按索引词头、跨章称名锚点及既有同类型KU复核三组person `new` 身份组；均未发现可复用人物卡，各组各登记一个KU。"
        "James II由J，K.csv#1与第7、10章锚定，OCR“James H”异文保留；Bernhard Rode由第14章姓氏提及、Postscript第20章全名及Q-R.csv#134归组，画作归属争议单独保留；"
        "John Milton由第2、4章正文与M.csv#208归组，第10章p.319另有Milton提及但不在索引页码范围内。未加入外部身份事实。8条S2直接关系候选仍待S6逐条审查，本批未新增正式关系边。\n\n"
        "| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
    )
    for t in TARGETS:
        process_record += f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['chapters']} | {len(t['relation_ids'])} |\n"
    process_record += "\n"
    if f'<a id="{ANCHOR}"></a>' in process_text:
        assert process_heading in process_text and all(t["group"] in process_text for t in TARGETS)
    else:
        process_text += process_record

    result_text = sync.update_result(template.read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    result_heading = process_heading
    if result_heading in result_text:
        assert all(t["ku"] in result_text for t in TARGETS)
    else:
        result_text += f"\n\n{result_heading}\n\n"
        for t in TARGETS:
            result_text += (
                f"- `{t['candidate']}` / `{t['group']}` → "
                f"[{t['name_zh']}（{t['name_en']}）](../{t['ku']}.md)；{t['chapters']}；"
                f"{len(t['relation_ids'])}条直接关系候选留待S6。\n"
            )
        result_text += "\n本批未新增正式关系或外部身份断言；OCR异文和来源归属争议均予保留。\n"

    if args.dry_run:
        state = "ALREADY REGISTERED" if newly_registered == 0 else "DRY-RUN OK"
        print(f"{state}: person groups={len(TARGETS)}; cards to create={len(cards)}; direct relation candidates={sum(len(t['relation_ids']) for t in TARGETS)}")
        print(
            f"manifest: {len(manifest):,}->{len(planned_manifest):,}; registered groups: "
            f"{before_totals['registered_groups']:,}->{totals['registered_groups']:,}; "
            f"pending groups: {before_totals['pending_groups']:,}->{totals['pending_groups']:,}; "
            f"pending candidate mappings: {before_totals['pending_members']:,}->{totals['pending_members']:,}"
        )
        for t in TARGETS:
            print(f"{t['candidate']} -> {t['ku']}; group={t['group']}; {len(t['relation_ids'])} S6 candidates")
        return
    if newly_registered == 0:
        print(f"ALREADY REGISTERED: groups={len(TARGETS)}; cards={len(cards)}")
        return

    for path, card in cards.items():
        path.write_bytes(card.encode("utf-8"))
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned)
    sync.write_csv(ENTITY_PATH, candidate_fields, candidates)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(template.keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(template.keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(template.keep_bom_bytes(RESULT_PATH, result_text))
    print(f"APPLIED: groups={newly_registered}; cards={len(cards)}; registered={totals['registered_groups']:,}; pending={totals['pending_groups']:,}")


if __name__ == "__main__":
    main()
