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
import register_s4_three_crosschapter_person_groups_20261017j as template  # noqa: E402

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
ANCHOR = "s4-crosschapter-person-groups-20261017k"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"

BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

TARGETS = [
    {
        "candidate": "cand-1607",
        "group": "new-person:cosimo-de-iii-medici-098cd59653",
        "ku": "units/persons/cosimo-iii-de-medici",
        "name_zh": "科西莫三世·德·美第奇",
        "name_en": "Cosimo III de' Medici",
        "index_entry": "M.csv#147",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "index_quote": "Medici, Cosimo III de'",
        "index_span": "M.csv#147; index row 149; pp. 229, 404",
        "chapters": "第8、20章；索引 M.csv#147",
        "sources": [
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "location": "第8章，印刷页229，Markdown L218",
                "summary": "Haskell明确称Grand Prince Ferdinand为Cosimo III与Marguerite d’Orléans之子。",
                "line_start": 218,
                "line_end": 218,
                "span": "Markdown line 218; print p. 229",
                "quote_text": "He was born in 1663, the son of Cosimo III and Marguerite d’Orléans.",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "location": "第二十章后记，印刷页404，Markdown L126",
                "summary": "Haskell回顾其早期著作对Cosimo III的负面评价，并转述Klaus Lankheit对其艺术角色的重新评估。",
                "line_start": 126,
                "line_end": 126,
                "span": "Markdown line 126; print p. 404",
                "quote_text": "Klaus Lankheit has shown that the role even of Cosimo III, a blinkered ‘villain’ to me in 1963 as to most previous writers, was far more positive (especially as regards sculpture) than I then suggested",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Medici, Cosimo III de'”及第8章、第20章后记中的Cosimo III。第8章明确称Grand Prince Ferdinand为Cosimo III之子；后记以相同姓名回顾Haskell早期对Cosimo III的评价，并转述Klaus Lankheit的重新评估。"
            "本卡只记录书内跨章身份，不把Haskell或被引学者的评价改写为本项目独立判断。"
        ),
        "description_en": (
            "This card represents the index heading “Medici, Cosimo III de'” and Cosimo III in chapter 8 and the chapter 20 postscript. Chapter 8 explicitly names him as Grand Prince Ferdinand’s father; the postscript returns to Cosimo III by the same name and reports Klaus Lankheit’s reassessment of his role. "
            "The card records the book’s cross-chapter identity and does not recast Haskell’s or the cited scholar’s evaluations as independent project findings."
        ),
        "relation_ids": [
            "st-chp8-p229-birth-and-parentage",
            "st-chp8-p229-parental-climate",
            "st-chp20-p404-lankheit-reassesses-cosimo-iii",
            "st-chp20-p404-late-baroque-florence-detroit-exhibition",
        ],
        "identity_extra": "p.229与p.404同名指称可直接相连；未复用其他Medici人物卡。",
    },
    {
        "candidate": "cand-2814",
        "group": "new-person:england-iii-of-william-d840b96e5c",
        "ku": "units/persons/william-iii-of-england",
        "name_zh": "英格兰的威廉三世",
        "name_en": "William III of England",
        "index_entry": "UVWXYZ.csv#151",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "index_quote": "William III of England",
        "index_span": "UVWXYZ.csv#151; index row 153; pp. 196, 280",
        "chapters": "第7、10章；索引 UVWXYZ.csv#151",
        "sources": [
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "location": "第7章，印刷页196，Markdown L60",
                "summary": "Haskell說Verrio曾為Louis XIV及其最大敵手William III服務。",
                "line_start": 59,
                "line_end": 60,
                "span": "Markdown lines 59–60; print p. 196",
                "quote_text": "Within little more than a generation he had put his art at the service of Louis XIV and his greatest enemy\nWilliam III;",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "location": "第10章，印刷页280，Markdown L53",
                "summary": "Haskell以William Bentinck為William III的親信；轉錄層將III誤作Ill，該頁印本頁圖已核對為III。",
                "line_start": 53,
                "line_end": 53,
                "span": "Markdown line 53; print p. 280; scan reads III, OCR reads Ill",
                "quote_text": "William Ill’s great favourite, the Dutch William Bentinck",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "location": "第10章注2，印刷页289，Markdown L544",
                "summary": "Haskell列出1741年《Tombeaux des Princes》所收人物，其中包括William III；此处是书中所述出版物内容。",
                "line_start": 544,
                "line_end": 544,
                "span": "Markdown line 544; note 2 on print p. 289",
                "quote_text": "These were those to William III, Tillotson, Malborough, Godolphin, Dorset, Cowper, Sir Cloudesly Shovel, Newton and Boyle/Locke/Sydenham.",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“William III of England”以及第7章、第10章中的William III。第7章将他置于Verrio服务的政治语境；第10章p.280记William Bentinck为其亲信，p.289注2将William III列入1741年出版物的题名人物。"
            "p.280转录写作William Ill，印本页图确认是III；该转录差异不形成另一人物。"
        ),
        "description_en": (
            "This card represents the index heading “William III of England” and William III in chapters 7 and 10. Chapter 7 places him in the political context of Verrio’s service; chapter 10 p. 280 names William Bentinck as his favourite, and note 2 on p. 289 lists William III among the subjects in the 1741 publication. "
            "The p. 280 text transcription reads William Ill, while the printed page image confirms III; this transcription difference does not indicate another person."
        ),
        "relation_ids": [
            "st-chp7-p196-hampton_fresco_subject",
            "st-chp7-p196-verrio-served-williamiii",
            "st-chp10-p280-williamiii-favourite-bentinck",
            "st-chp10-p289-note1-row03-subject",
        ],
        "identity_extra": "索引主项、p.196与p.280–289语境指向同一William III；p.280 OCR异读已按印本页图校正理解。",
    },
    {
        "candidate": "cand-1295",
        "group": "new-person:france-henri-iv-of-95c1a45df8",
        "ku": "units/persons/henri-iv-of-france",
        "name_zh": "法兰西的亨利四世",
        "name_en": "Henri IV of France",
        "index_entry": "H.csv#11",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/H.csv",
        "index_quote": "Henri IV of France",
        "index_span": "H.csv#11; index row 13; pp. 26, 33, 53, 173, 174",
        "chapters": "第2、7章；索引 H.csv#11",
        "sources": [
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "location": "第2章，印刷页26，Markdown L64",
                "summary": "Haskell记Maffeo Barberini曾短访巴黎，祝贺Henri IV长子的出生。",
                "line_start": 64,
                "line_end": 64,
                "span": "Markdown line 64; print p. 26",
                "quote_text": "Henri IV on the birth of his eldest son, and his return was warmly welcomed in France.",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "location": "第7章，印刷页173，Markdown L40",
                "summary": "Haskell以Henry IV轉述對其建築和政治主張的評價。",
                "line_start": 40,
                "line_end": 40,
                "span": "Markdown line 40; print p. 173",
                "quote_text": "‘On dit queje suis chiche, mais je fais trois choses bien éloignées d’avarice, car je fais la guerre, je fais l’amour et je bâtis’, boasted Henry IV.",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "location": "第7章，印刷页174，Markdown L49–52",
                "summary": "Haskell记Marie de Medici於Henri IV在位時對藝術的委託，並提及他於1610年遇刺後的政治與藝術語境。",
                "line_start": 51,
                "line_end": 52,
                "span": "Markdown lines 51–52; print p. 174",
                "quote_text": "She persuaded her uncle the Grand Duke to commission an equestrian statue of Henri\nIV from Francavilla’s master, Giambologna.",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Henri IV of France”及第2、7章中的Henri IV／Henry IV。第2章记Maffeo Barberini祝贺其长子出生；第7章以Henry IV拼写引用其言论，并在Marie de Medici的艺术委托语境中再次称Henri IV。索引所列跨页与正文姓名及称谓相合。"
        ),
        "description_en": (
            "This card represents the index heading “Henri IV of France” and Henri IV/Henry IV in chapters 2 and 7. Chapter 2 recounts Maffeo Barberini’s visit to congratulate him on the birth of his eldest son; chapter 7 uses the Henry IV spelling in a reported saying and names Henri IV again in the context of Marie de Medici’s artistic commissions. The index locators and body references support one cross-chapter identity."
        ),
        "relation_ids": [
            "st-chp2-seci-l55-69-henri-silver-service",
            "st-chp2-seci-l55-69-henri-visit",
            "st-chp7-p173-i21",
            "st-chp7-p174-i08",
        ],
        "identity_extra": "Henri/Henry为书内两章拼写差异；未另立人物或引入外部传记事实。",
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
    assert quote in block, f"quote not found: {item['file']}:{item['line_start']}"
    return quote


def main() -> None:
    parser = argparse.ArgumentParser(description="Register three cross-chapter person identity groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    template.TASK = TASK
    template.PROCESS_REF = PROCESS_REF
    template.ANCHOR = ANCHOR
    template.CARD_REF = CARD_REF
    template.DATE = DATE
    template.BOOK_CITATION = BOOK_CITATION
    template.source_quote = source_quote

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
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
    cards: dict[Path, str] = {}
    relation_total = 0

    for t in TARGETS:
        cid, group, ku = t["candidate"], t["group"], t["ku"]
        assert cid in candidate_by and cid in planned_by
        assert candidate_by[cid]["suggested_type"] == "person"
        assert planned_by[cid]["decision"] == "new" and not planned_by[cid].get("ku_id")
        assert sync.get_group(planned_by[cid].get("resolution_note", "")) == group
        members = [
            r["candidate_id"]
            for r in alignments
            if r.get("candidate_id") and r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == group
        ]
        assert members == [cid], f"unexpected group members for {group}: {members}"
        assert ku not in manifest_by and not (ROOT / f"04-knowledge/{ku}.md").exists()
        assert f"- 04-knowledge/{ku}.md" not in accepted_lines
        assert not any(r.get("name_en", "").casefold() == t["name_en"].casefold() for r in manifest if r["type"] == "person")
        assert t["index_quote"].encode("ascii") in (ROOT / t["index_file"]).read_bytes()
        for item in t["sources"]:
            source_quote(item)
        for sid in t["relation_ids"]:
            assert sid in statements
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
        cards[ROOT / f"04-knowledge/{ku}.md"] = template.make_card(t)
        row = planned_by[cid]
        row["ku_id"] = ku
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += (
            f" S4 cross-chapter registration ({DATE}): mapped {group} to {ku}; "
            f"chapter and index identity anchors retained; {len(t['relation_ids'])} direct relation candidates remain pending S6."
        )
        relation_total += len(t["relation_ids"])

    planned_manifest = [dict(r) for r in manifest]
    for t in TARGETS:
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
    for t in TARGETS:
        planned_accepted = prior.insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")

    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before_totals = sync.build_type_table(before_stats)
    stats = sync.summarize_by_type(candidate_by.values(), planned)
    _, totals = sync.build_type_table(stats)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert relation_total == sum(len(t["relation_ids"]) for t in TARGETS)

    process_text = read_text(PROCESS_PATH)
    anchor = f'<a id="{ANCHOR}"></a>'
    assert anchor not in process_text
    process_text += (
        "\n\n" + anchor + "\n\n"
        "### S4 person：三组跨章人物身份登记（2026-10-17）\n\n"
        "复核三组既有person `new` 身份组的索引词头、跨章正文锚点与既有同类型KU；未发现可复用人物卡，分别登记一个KU。"
        "只记录原书所支持的姓名、称号及语境，不增补外部传记；书内关系断言继续留待S6逐条审查。\n\n"
        "| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
    )
    for t in TARGETS:
        process_text += f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['chapters']} | {len(t['relation_ids'])} |\n"
    process_text += "\n"
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    result_text += "\n\n### S4 person：三组跨章人物身份登记（2026-10-17）\n\n"
    for t in TARGETS:
        result_text += (
            f"- `{t['candidate']}` / `{t['group']}` → [{t['name_zh']}（{t['name_en']}）]"
            f"(../units/{t['ku']}.md)；{t['chapters']}；{len(t['relation_ids'])}条直接关系候选留待S6。\n"
        )
    result_text += "\n本批未登记正式关系或外部身份标识；各卡提供候选、对齐行与过程记录入口。\n"

    if args.dry_run:
        print(f"DRY-RUN OK: person groups={len(TARGETS)}; cards={len(cards)}; direct relation candidates={relation_total}")
        print(
            f"manifest: {len(manifest):,}->{len(planned_manifest):,}; "
            f"registered groups: {before_totals['registered_groups']:,}->{totals['registered_groups']:,}; "
            f"pending groups: {before_totals['pending_groups']:,}->{totals['pending_groups']:,}; "
            f"pending candidate mappings: {before_totals['pending_members']:,}->{totals['pending_members']:,}"
        )
        for t in TARGETS:
            print(f"{t['candidate']} -> {t['ku']}; group={t['group']}; {len(t['relation_ids'])} S6 candidates")
        return

    for path, card in cards.items():
        path.write_bytes(card.encode("utf-8"))
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(
        f"APPLIED: person groups={len(TARGETS)}; cards={len(cards)}; manifest={len(planned_manifest):,}; "
        f"registered groups={totals['registered_groups']:,}; pending groups={totals['pending_groups']:,}"
    )


if __name__ == "__main__":
    main()

