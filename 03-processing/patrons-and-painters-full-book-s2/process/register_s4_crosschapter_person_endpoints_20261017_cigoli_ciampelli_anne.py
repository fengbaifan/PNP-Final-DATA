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
ANCHOR = "s4-crosschapter-person-endpoints-cigoli-ciampelli-anne-20261017"
DATE = "2026-10-17"

BOOK_CITATION = template.BOOK_CITATION
INDEX_CITATION = template.INDEX_CITATION

TARGETS = [
    {
        "candidate": "cand-0756",
        "group": "new-person:cigoli-ludovico-39b93eea0c",
        "ku": "units/persons/ludovico-cigoli",
        "name_zh": "卢多维科·奇戈利",
        "name_en": "Ludovico Cigoli",
        "index_entry": "C.csv#280",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/C.csv",
        "index_line": 282,
        "index_quote": "Cigoli, Ludovico",
        "index_span": "C.csv#280; CSV line 282; p. 102",
        "chapters": "第2、4章；索引 C.csv#280",
        "relation_ids": [
            "st-chp2-seciv-l190-245-cigoli-earlier-story-scenes",
            "st-chp4-sec-ii-l33-44-cigoli-leads-florentine-style-shift",
            "st-chp4-sec-ii-l33-44-galileo-favorite-painter-cigoli",
            "st-chp4-sec-ii-l33-44-galileo-occasional-collaborator-cigoli",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "line_start": 222,
                "line_end": 222,
                "location": "第2章，印刷页102注1；OCR L222",
                "span": "OCR line 222; print p. 102 n. 1",
                "summary": "注1称Cigoli此前已在Scipione Borghese所有的宫殿中绘制过该故事的场景。",
                "quote_text": "Cigoli had already painted scenes from this story in the palace when it belonged to Scipione Borghese.",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "line_start": 44,
                "line_end": 44,
                "location": "第4章，印刷页102；OCR L44",
                "span": "OCR line 44; print p. 102",
                "summary": "Haskell称Ludovico Cigoli为Galileo偏爱的画家和偶尔合作对象，并描述其在佛罗伦萨画家中的位置。",
                "quote_text": "His favourite painter and occasional collaborator was Ludovico Cigoli, the leader of those Florentine artists who were breaking away from a late Mannerist style to a more rational and naturalistic manner.",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Cigoli, Ludovico”及第2、4章中的Ludovico Cigoli。第2章注1称Cigoli曾在Scipione Borghese所有的宫殿中绘制该故事场景；"
            "第4章将他置于Galileo的绘画交往语境，并称其为Galileo偏爱的画家及偶尔合作对象。上述书内归属与关系断言仍分别留待S6审查；本名采用工作音译。"
        ),
        "description_en": (
            "This card represents the index entry “Cigoli, Ludovico” and the Ludovico Cigoli references in chapters 2 and 4. Chapter 2 note 1 says Cigoli had painted scenes from the story at a palace when it belonged to Scipione Borghese. Chapter 4 places him in Galileo’s artistic context and calls him Galileo’s favourite painter and occasional collaborator. These source statements and relation candidates remain for separate S6 review. The Chinese display name is a working transliteration."
        ),
        "identity_extra": "第2、4章均有Cigoli姓名锚点；第4章全名与索引C.csv#280相合。未采用外部身份标识；中文名为工作音译。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-0756 remains the source-local person group new-person:cigoli-ludovico-39b93eea0c. Chapter 4 p.102 gives the full name Ludovico Cigoli; chapter 2 p.102 n.1 and index C.csv#280 provide matching anchors. No exact existing person KU matched; no external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-0744",
        "group": "new-person:agostino-ciampelli-64c825d6b8",
        "ku": "units/persons/agostino-ciampelli",
        "name_zh": "阿戈斯蒂诺·钱佩利",
        "name_en": "Agostino Ciampelli",
        "index_entry": "C.csv#268",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/C.csv",
        "index_line": 270,
        "index_quote": "Ciampelli, Agostino",
        "index_span": "C.csv#268; CSV line 270; pp. 38, 39, 66",
        "chapters": "第2、3章；索引 C.csv#268",
        "relation_ids": [
            "st-chp2-secii-l71-78-ciampelli-fresco-series-commissioned",
            "st-chp2-secii-l80-89-pietro-joined-ciampelli-at-bibiana",
            "st-chp3-secii-l6-17-pious-ladies-introduced-ciampelli",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "line_start": 72,
                "line_end": 73,
                "location": "第2章，印刷页38–39；OCR L72–73",
                "span": "OCR lines 72–73; print pp. 38–39",
                "summary": "Haskell称Agostino Ciampelli受命为S. Bibiana绘制一组壁画，并叙述其后续工作语境。",
                "quote_text": "Agostino Ciampelli, was commissioned to paint on the walls a series of frescoes illustrating the life of the Saint. He was one of the group of\n‘reformed Mannerists’",
            },
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "line_start": 88,
                "line_end": 89,
                "location": "第2章，印刷页39；OCR L88–89",
                "span": "OCR lines 88–89; print p. 39",
                "summary": "Haskell称年轻的Pietro da Cortona在S. Bibiana与Agostino Ciampelli一同工作。",
                "quote_text": "So it was that the young Pietro da Cortona joined Agostino Ciampelli in the church of\nS. Bibiana.",
            },
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "line_start": 10,
                "line_end": 11,
                "location": "第3章，印刷页66；OCR L10–11",
                "span": "OCR lines 10–11; print p. 66",
                "summary": "第3章列举被引入耶稣会侧堂项目的艺术家；本处OCR将姓氏转录为Ciampelh。",
                "quote_text": "Agostino Ciampelh and Federigo Zuccari;",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Ciampelli, Agostino”及第2、3章中的Agostino Ciampelli。第2章称其受命为S. Bibiana绘制壁画，并将Pietro da Cortona与他在该教堂的工作联系起来；"
            "第3章再次列出该姓名，但OCR作“Ciampelh”。书内关系候选仍待S6审查；中文名为工作音译，OCR异文保留。"
        ),
        "description_en": (
            "This card represents the index entry “Ciampelli, Agostino” and the Agostino Ciampelli references in chapters 2 and 3. Chapter 2 says he was commissioned to paint frescoes at S. Bibiana and places Pietro da Cortona in the same church context. Chapter 3 names him again, with the OCR reading “Ciampelh”. The source relation candidates remain for S6 review; the Chinese display name is a working transliteration and the OCR variant is retained."
        ),
        "identity_extra": "第2章第38–39页的全名与第3章第66页及索引C.csv#268相合；第3章OCR异文“Ciampelh”保留。未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-0744 remains the source-local person group new-person:agostino-ciampelli-64c825d6b8. Chapters 2 pp.38–39 give the full name Agostino Ciampelli; chapter 3 p.66 has the OCR variant “Agostino Ciampelh”; index C.csv#268 lists pp.38, 39, 66. No exact existing person KU matched; no external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-0110",
        "group": "new-person:anne-england-of-1cb5af41f1",
        "ku": "units/persons/anne-queen-of-england",
        "name_zh": "英国女王安妮",
        "name_en": "Anne, Queen of England",
        "index_entry": "A.csv#111",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
        "index_line": 113,
        "index_quote": "Anne, Queen of England",
        "index_span": "A.csv#111; CSV line 113; pp. 196–197",
        "chapters": "第7、10章；索引 A.csv#111",
        "relation_ids": [
            "st-chp10-p281-sheffield-favourite-anne",
            "st-chp7-p196-verrio_pension_open",
            "st-chp7-p197-queen-anne-employs-cassana",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "line_start": 60,
                "line_end": 60,
                "location": "第7章，印刷页196；OCR L60",
                "span": "OCR line 60; print p. 196",
                "summary": "Haskell称Verrio在1707年前仍领取Queen Anne的养老金。",
                "quote_text": "receiving a pension from Queen Anne,",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "line_start": 64,
                "line_end": 64,
                "location": "第7章，印刷页197；OCR L64",
                "span": "OCR line 64; print p. 197",
                "summary": "Haskell称Queen Anne雇用Niccolò Cassana为肖像画家，并以问号保留1714年卒年说法的不确定性。",
                "quote_text": "the Genoese artist Niccolò Cassana whom she employed as her portrait painter until his death in 1714?",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 126,
                "line_end": 126,
                "location": "第10章，印刷页281；OCR L126",
                "span": "OCR line 126; print p. 281",
                "summary": "该段OCR写作“Queen Arme”，随后称该人物去世后Sheffield退出政坛；索引和第7章锚点支持按Queen Anne归组。",
                "quote_text": "He became a special favourite of Queen Arme, and when she died he retired from politics.",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 256,
                "line_end": 256,
                "location": "第10章，印刷页291；OCR L256",
                "span": "OCR line 256; print p. 291",
                "summary": "Haskell转引的项目说明提及King William、Queen Mary、Queen Anne与King George的统治时期。",
                "quote_text": "the most memorable Transactions in the Reigns of King William and Queen Mary, Queen Anne, and King George.",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Anne, Queen of England”及第7、10章中的Queen Anne。第7章记Verrio领取来自Queen Anne的养老金，并称她雇用Niccolò Cassana为肖像画家；"
            "第10章p.281的OCR写作“Queen Arme”，该段随后以“she”指称其去世。姓名归组依据索引、第7章明名与第10章语境；OCR异文保留，相关关系断言仍待S6审查。"
        ),
        "description_en": (
            "This card represents the index entry “Anne, Queen of England” and Queen Anne references in chapters 7 and 10. Chapter 7 mentions a pension from Queen Anne for Verrio and says she employed Niccolò Cassana as a portrait painter. The OCR at chapter 10 p.281 reads “Queen Arme”; the passage then refers to her death. The grouping follows the index, the explicit chapter 7 name, and the chapter 10 context. The OCR variant is retained, and the relation candidates remain for S6 review."
        ),
        "identity_extra": "第7章第196–197页与第10章第281、291页形成跨章锚点；第10章p.281 OCR异文“Queen Arme”保留。规范显示名沿用索引；未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-0110 remains the source-local person group new-person:anne-england-of-1cb5af41f1. Index A.csv#111 names Anne, Queen of England and lists pp.196–197; chapter 7 pp.196–197 uses Queen Anne, and chapter 10 p.281 OCR reads “Queen Arme” followed by a reference to her death. The chapter 10 context is grouped with the indexed Queen Anne; no exact existing person KU matched and no external identity source was accessed."
        ),
    },
]


def source_quote(item: dict) -> str:
    path = ROOT / item["file"]
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        # A.csv retains its original Windows single-byte encoding; do not rewrite the source.
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
            template.source_quote(item)
        template.source_quote({"file": t["index_file"], "line_start": t["index_line"], "line_end": t["index_line"], "quote_text": t["index_quote"]})
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
    process_heading = "### S3→S4 person：Cigoli、Ciampelli 与 Anne, Queen of England 登记（2026-10-17）"
    process_record = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"{process_heading}\n\n"
        "按索引词头、跨章全名/称名锚点及既有同类型KU复核三组person `new` 身份组；均未发现可复用人物卡，各组各登记一个KU。"
        "Cigoli由第2、4章及C.csv#280归组；Ciampelli由第2、3章及C.csv#268归组，并保留第3章OCR异文“Ciampelh”；"
        "Anne依据第7章明名、索引A.csv#111与第10章上下文归组，第10章p.281 OCR异文“Queen Arme”保留。未加入外部身份事实。"
        "10条S2直接关系候选仍待S6逐条审查，本批未新增正式关系边。\n\n"
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
        result_text += "\n本批未新增正式关系或外部身份断言；OCR异文依来源保留。\n"

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
