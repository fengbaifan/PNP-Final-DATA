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
ANCHOR = "s4-crosschapter-person-endpoints-dominici-sartori-viero-20261017"
DATE = "2026-10-17"

BOOK_CITATION = template.BOOK_CITATION
INDEX_CITATION = template.INDEX_CITATION

TARGETS = [
    {
        "candidate": "cand-0942, cand-7116",
        "members": ["cand-0942", "cand-7116"],
        "group": "new-person:bernardo-de-dominici-cbdb693309",
        "ku": "units/persons/bernardo-de-dominici",
        "name_zh": "贝尔纳多·德·多米尼奇",
        "name_en": "Bernardo de Dominici",
        "index_entry": "D.csv#44",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/D.csv",
        "index_line": 46,
        "index_quote": "Dominici, Bernardo de",
        "index_span": "D.csv#44; CSV line 46; p. 207",
        "chapters": "第6–8章；第21章书目；索引 D.csv#44",
        "relation_endpoints": {
            "st-chp8-p207-de-dominici-said-picture-lovers-followed-roomer-advice": "cand-0942",
            "st-chp8-p208-de-dominici-cavallino-affect": "cand-0942",
            "st-chp8-p224-n4-dominici-reports-three-pictures": "cand-7116",
        },
        "detail_by_candidate": {
            "cand-0942": (
                "S3 cross-chapter review (2026-10-17): cand-0942 and cand-7116 form "
                "new-person:bernardo-de-dominici-cbdb693309. Index D.csv#44 gives “Dominici, Bernardo de”; "
                "the chapter 21 bibliography at L430 names “Dominici, Bernardo de” as author of the four-volume "
                "Vite, while chapter 7 p.189 n.6 and chapter 8 cite De Dominici, vol. IV. The full author form, "
                "short citations, and page context support one source-local person identity. Archive candidates "
                "cand-11317 (set) and cand-4835 (vol. IV citation scope) remain distinct from this person."
            ),
            "cand-7116": (
                "S3 cross-chapter review (2026-10-17): the chapter 21 bibliography at "
                "02-sources/02-Markdown/21_CHP-21Bibliography.md#L430 names “Dominici, Bernardo de” as author "
                "of the four-volume Vite; chapter 7 p.189 n.6 at 07_CHP-7_sec_i.md#L374 cites De Dominici, "
                "vol. IV, p.50. This short citation aligns with index candidate cand-0942, D.csv#44. The "
                "four-volume title and volume-specific citation remain separate archive candidates, not person KU."
            ),
        },
        "alignment_supplements": {
            "cand-7116": (
                "S3 evidence supplement: chapter 21 bibliography 02-sources/02-Markdown/21_CHP-21Bibliography.md#L430 "
                "reads “Dominici, Bernardo de: Vite dei pittori scultori ed architetti napoletani, 4 vols., Napoli 1843”; "
                "chapter 7 p.189 n.6 at 02-sources/02-Markdown/07_CHP-7_sec_i.md#L374 cites “De Dominici, IV, p. 50.” "
                "These support the full-name/short-citation match to index candidate cand-0942. Archive candidates "
                "cand-11317 and cand-4835 remain distinct."
            )
        },
        "relation_ids": [
            "st-chp8-p207-de-dominici-said-picture-lovers-followed-roomer-advice",
            "st-chp8-p208-de-dominici-cavallino-affect",
            "st-chp8-p224-n4-dominici-reports-three-pictures",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
                "line_start": 430,
                "line_end": 430,
                "location": "第21章书目；OCR L430",
                "span": "OCR line 430; bibliography entry",
                "summary": "书目列出Bernardo de Dominici及其四卷本Vite dei pittori scultori ed architetti napoletani（Napoli, 1843）。",
                "quote_text": "Dominici, Bernardo de: Vite dei pittori scultori ed architetti napoletani, 4 vols., Napoli 1843.",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "line_start": 374,
                "line_end": 374,
                "location": "第7章，印刷页189注6；OCR L374",
                "span": "OCR line 374; print p. 189 n. 6",
                "summary": "Haskell以De Dominici, vol. IV, p. 50作为引文定位。",
                "quote_text": "De Dominici, IV, p. 50.",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "line_start": 50,
                "line_end": 50,
                "location": "第8章，印刷页207；OCR L50",
                "span": "OCR line 50; print p. 207",
                "summary": "Haskell称de Dominici在Roomer去世五十多年后写下其绘画爱好者均听从Roomer建议的说法。",
                "quote_text": "‘All picture lovers of the day followed his advice’, wrote de Dominici more than fifty years after Roomer’s death.",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "line_start": 56,
                "line_end": 56,
                "location": "第8章，印刷页208；OCR L56",
                "span": "OCR line 56; print p. 208",
                "summary": "Haskell将Bernardo Cavallino受某画作影响的说法归于de Dominici；姓名OCR异文保留。",
                "quote_text": "profoundly affected Bernardo CavaUino, we learn from de Dominici",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "line_start": 391,
                "line_end": 391,
                "location": "第8章，印刷页224注4；OCR L391",
                "span": "OCR line 391; print p. 224 n. 4",
                "summary": "Haskell引用De Dominici, vol. IV, p. 428，并称该书还提到Buonaccorsi家族的三幅Solimena画作。",
                "quote_text": "De Dominici, IV, p. 428, who also mentions three other pictures painted by Solimena for the Buonaccorsi.",
            },
        ],
        "description_zh": (
            "本卡对应第21章书目中的作者全名“Dominici, Bernardo de”及索引D.csv#44。第7章p.189注6和第8章以“De Dominici”或“de Dominici”作短引，"
            "与书目所列四卷本Vite相连；第8章p.207–208及p.224注4呈现Haskell对该书的转引。四卷本与具体卷页引文分别保留为archive候选，"
            "不并入人物卡；所引页未独立阅读，相关书内断言仍待S6审查。"
        ),
        "description_en": (
            "This card represents the full author form “Dominici, Bernardo de” in the chapter 21 bibliography and index entry D.csv#44. Chapter 7 p.189 n.6 and chapter 8 cite “De Dominici” or “de Dominici,” linked by the bibliography to the four-volume Vite. Chapter 8 pp.207–208 and p.224 n.4 contain Haskell’s reports from that source. The four-volume work and volume/page citation candidates remain separate archive objects; the cited pages have not been independently read, and the book’s relation candidates remain for S6 review."
        ),
        "identity_extra": "书目L430全名、索引D.csv#44及第7–8章短引相合；四卷本archive候选与人物分开。未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-0942 and cand-7116 remain one source-local group "
            "new-person:bernardo-de-dominici-cbdb693309. Chapter 21 bibliography L430 gives Bernardo de Dominici; "
            "chapter 7 p.189 n.6 cites De Dominici, vol. IV, p.50; chapter 8 cites de Dominici and index D.csv#44 "
            "gives the full indexed form. Archive candidates cand-11317 (the four-volume set) and cand-4835 "
            "(volume IV citation scope) are not merged into the person. No external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-2363",
        "members": ["cand-2363"],
        "group": "new-person:felicita-sartori-b7a1b9ce62",
        "ku": "units/persons/felicita-sartori",
        "name_zh": "费利奇塔·萨托里",
        "name_en": "Felicita Sartori",
        "index_entry": "S.csv#51",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/S.csv",
        "index_line": 53,
        "index_quote": "Sartori, Felicita",
        "index_span": "S.csv#51; CSV line 53; pp. 295, 344n",
        "chapters": "第10、13章；索引 S.csv#51",
        "relation_endpoints": {
            "st-chp10-p295-sartori-dresden-work": "cand-2363",
            "st-chp10-p295-sartori-marriage": "cand-2363",
            "st-chp13-p344-zanetti-employed_felicita_sartori": "cand-2363",
        },
        "relation_ids": [
            "st-chp10-p295-sartori-dresden-work",
            "st-chp10-p295-sartori-marriage",
            "st-chp13-p344-zanetti-employed_felicita_sartori",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 312,
                "line_end": 313,
                "location": "第10章，印刷页295；OCR L312–313",
                "span": "OCR lines 312–313; print p. 295",
                "summary": "Haskell称Felicita Sartori是Rosalba的学生，嫁给一名宫廷顾问，1741年到德累斯顿并为其工作。",
                "quote_text": "Rosalba’s best pupil Felicita Sartori, who had married one of his councillors, came to\nDresden in 1741 and worked extensively for him.2",
            },
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "line_start": 122,
                "line_end": 122,
                "location": "第13章，印刷页344注；OCR L122",
                "span": "OCR line 122; print p. 344 n. 1",
                "summary": "Haskell写作“Félicita Sartori”，称Zanetti雇用她作雕版师并收藏大量其作品。",
                "quote_text": "Zanetti also employed Rosalba’s pupil Félicita Sartori as an engraver and owned a large collection of her work",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Felicita Sartori”及第10、13章中的同名提及。第10章写作Felicita，第13章注释写作带重音的“Félicita”；两处姓名、索引页码与人物语境相合。"
            "婚姻、德累斯顿工作及Zanetti雇用/收藏的书内关系候选均留待S6审查；拼写变体保留。"
        ),
        "description_en": (
            "This card represents the index entry “Sartori, Felicita” and references in chapters 10 and 13. Chapter 10 spells the name Felicita; chapter 13 note 1 uses the accented form “Félicita”. The names, index locators, and person contexts align. The reported marriage, Dresden work, and Zanetti employment/collection claims remain relation candidates for S6 review; both spellings are retained."
        ),
        "identity_extra": "第10章p.295的Felicita与第13章p.344注的Félicita及索引S.csv#51相合；重音异文保留。未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-2363 remains the source-local person group "
            "new-person:felicita-sartori-b7a1b9ce62. Chapter 10 p.295 gives Felicita Sartori; chapter 13 p.344 n.1 "
            "gives Félicita Sartori; index S.csv#51 lists pp.295/344n. No exact existing person KU matched; "
            "no external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-2773",
        "members": ["cand-2773"],
        "group": "new-person:teodoro-viero-15b8599b5c",
        "ku": "units/persons/teodoro-viero",
        "name_zh": "特奥多罗·维耶罗",
        "name_en": "Teodoro Viero",
        "index_entry": "UVWXYZ.csv#109",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "index_line": 111,
        "index_quote": "Viero, Teodoro",
        "index_span": "UVWXYZ.csv#109; CSV line 111; pp. 340, 345, 368",
        "chapters": "第13、15章；索引 UVWXYZ.csv#109",
        "relation_endpoints": {
            "st-chp13-p340-viero-printer-opened-shop-1754": "cand-2773",
            "st-chp13-p345-monaco-1763-1779-editions": "cand-2773",
            "st-chp15-p368-note3-inventory-drawn-up-by-viero": "cand-2773",
        },
        "relation_ids": [
            "st-chp13-p340-viero-printer-opened-shop-1754",
            "st-chp13-p345-monaco-1763-1779-editions",
            "st-chp15-p368-note3-inventory-drawn-up-by-viero",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "line_start": 86,
                "line_end": 86,
                "location": "第13章，印刷页340；OCR L86",
                "span": "OCR line 86; print p. 340",
                "summary": "Haskell称Teodoro Viero本人也是印刷商，并于1754年开店。",
                "quote_text": "Teodoro Viero, himself a printer, who opened a shop in 1754",
            },
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "line_start": 165,
                "line_end": 165,
                "location": "第13章，印刷页345；OCR L165",
                "span": "OCR line 165; print p. 345",
                "summary": "Haskell称Pietro Monaco版画集的1779年后续版由Viero在其身后出版。",
                "quote_text": "in 1779, posthumously published by Viero",
            },
            {
                "file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "line_start": 99,
                "line_end": 100,
                "location": "第15章，印刷页368注3；OCR L99–100",
                "span": "OCR lines 99–100; print p. 368 n. 3",
                "summary": "Haskell称一份关于Memmo藏品的清单由Sasso与Viero编制，并给出Petizion 488的档案定位。",
                "quote_text": "See the inventory drawn up by Sasso and Viero in the Archivio di Stato, Venice—Petizion 488,\n30 Gennaio 1792 and 24 Febbraio 1792/3 M.V.,",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Viero, Teodoro”及第13、15章中的Teodoro Viero/Viero。第13章称其为印刷商并记其1754年开店，也提到他在身后出版Pietro Monaco版画集的1779年版；"
            "第15章注3称他与Sasso编制Memmo藏品清单。相关出版、职业及清单关系候选仍待S6审查。"
        ),
        "description_en": (
            "This card represents the index entry “Viero, Teodoro” and references to Teodoro Viero/Viero in chapters 13 and 15. Chapter 13 calls him a printer, records his shop opening in 1754, and mentions the 1779 edition of Pietro Monaco’s print collection as posthumously published by Viero. Chapter 15 note 3 says he and Sasso drew up an inventory of Memmo’s collection. These publication, occupation, and inventory relation candidates remain for S6 review."
        ),
        "identity_extra": "第13章p.340全名、p.345姓氏及第15章p.368注3与索引UVWXYZ.csv#109相合。未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-2773 remains the source-local person group "
            "new-person:teodoro-viero-15b8599b5c. Chapter 13 p.340 gives Teodoro Viero and p.345 uses Viero; "
            "chapter 15 p.368 n.3 also names Viero; index UVWXYZ.csv#109 lists pp.340/345/368. No exact existing "
            "person KU matched; no external identity source was accessed."
        ),
    },
]


def source_quote(item: dict) -> str:
    path = ROOT / item["file"]
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
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
        ku = t["ku"]
        assert all(candidate_by[cid]["suggested_type"] == "person" for cid in t["members"])
        member_rows = [planned_by[cid] for cid in t["members"]]
        assert all(a["decision"] == "new" and a.get("ku_id", "") in ("", ku) for a in member_rows)
        assert all(sync.get_group(a.get("resolution_note", "")) == t["group"] for a in member_rows)
        group_members = sorted(
            r["candidate_id"]
            for r in alignments
            if r.get("candidate_id")
            and not r.get("external_source")
            and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == t["group"]
        )
        assert group_members == sorted(t["members"]), f"unexpected members in {t['group']}: {group_members}"
        card_path = ROOT / f"04-knowledge/{ku}.md"
        accepted_ref = f"- 04-knowledge/{ku}.md" in accepted_lines
        flags = [all(a.get("ku_id") == ku for a in member_rows), ku in manifest_by, card_path.exists(), accepted_ref]
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
        for sid, endpoint in t["relation_endpoints"].items():
            assert sid in statements
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert endpoint in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
        if registered:
            assert card_path.read_text(encoding="utf-8-sig") == template.make_card(t)
            for cid, a in zip(t["members"], member_rows):
                assert a.get("process_ref") == PROCESS_REF
                assert f"S4 registration: group {t['group']} mapped to {ku};" in a.get("resolution_note", "")
                supplement = t.get("alignment_supplements", {}).get(cid)
                if supplement:
                    assert supplement in a.get("resolution_note", "")
                expected_detail = t.get("detail_by_candidate", {}).get(cid, t["s3_note"])
                assert candidate_by[cid].get("detail") == expected_detail
        else:
            for cid, a in zip(t["members"], member_rows):
                supplement = t.get("alignment_supplements", {}).get(cid)
                if supplement:
                    a["resolution_note"] += f" {supplement}"
                a["ku_id"] = ku
                a["process_ref"] = PROCESS_REF
                a["resolution_note"] += (
                    f" S4 registration: group {t['group']} mapped to {ku}; "
                    f"{len(t['relation_ids'])} direct relation candidates remain pending S6."
                )
                candidate_by[cid]["detail"] = t.get("detail_by_candidate", {}).get(cid, t["s3_note"])
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
    assert totals["pending_members"] == before_totals["pending_members"] - sum(
        len(t["members"]) for t, registered in zip(TARGETS, registered_flags) if not registered
    )

    process_text = template.read_text(PROCESS_PATH)
    process_heading = "### S3→S4 person：Bernardo de Dominici、Felicita Sartori 与 Teodoro Viero 登记（2026-10-17）"
    process_record = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"{process_heading}\n\n"
        "按S3身份组、跨章原书锚点及同类型KU复核三组person `new`；每组登记一个KU。Bernardo de Dominici组含cand-0942与cand-7116：第21章书目L430给出作者全名，"
        "第7章p.189注6的De Dominici卷IV短引及第8章p.207–208、p.224注4相连，索引D.csv#44提供同名词头；四卷本全集cand-11317与卷IV引用候选cand-4835仍是独立archive候选。"
        "Felicita/Félicita Sartori由第10、13章和S.csv#51归组；Teodoro Viero由第13、15章和UVWXYZ.csv#109归组。未加入外部身份事实。9条S2直接关系候选留待S6逐条审查，本批未新增正式关系边。\n\n"
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
        result_text += "\n本批未新增正式关系或外部身份断言；书内作者归属和引文页阅读状态按来源边界保留。\n"

    if args.dry_run:
        state = "ALREADY REGISTERED" if newly_registered == 0 else "DRY-RUN OK"
        mapping_count = sum(len(t["members"]) for t in TARGETS)
        print(f"{state}: person groups={len(TARGETS)}; candidate mappings={mapping_count}; cards to create={len(cards)}; direct relation candidates={sum(len(t['relation_ids']) for t in TARGETS)}")
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
