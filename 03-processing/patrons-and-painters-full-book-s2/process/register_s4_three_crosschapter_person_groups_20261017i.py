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
PROCESS_EVIDENCE_PATH = ROOT / "03-processing" / TASK / "process" / "stages.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = "S4-full-book-2026-10-17"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017i"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-1237",
        "group": "new-person:giacomo-guarana-04ff210452",
        "ku": "units/persons/giacomo-guarana",
        "name_zh": "贾科莫·瓜拉纳",
        "name_en": "Giacomo Guarana",
        "index_entry": "G.csv#147",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/G.csv",
        "index_quote": "Guarana, Giacomo",
        "index_span": "G.csv#147; index row 149; pp. 260, 297, 340, 361",
        "chapters": "第9、10、13、15章；索引 G.csv#147",
        "sources": [
            {
                "file": "02-sources/01-book/CHP-9.pdf",
                "location": "第9章，印刷页260，PDF物理第22页",
                "summary": "原书页图印刷页码为260，并写出Giacomo Guarana全名，称其为Tiepolo的追随者且为该宫殿绘制壁画；Markdown页码文本层误识为200。",
                "quote_text": "Giacomo Guarana, a follower of Tiepolo, painted frescoes in the palace³;",
                "span": "PDF physical page 22; printed p. 260",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "location": "第10章，印刷页297，Markdown L341–342",
                "summary": "Haskell称Giacomo Guaraña为Ricci与Tiepolo的学生，并称其于1762年为莫斯科绘制《伊菲革涅亚的祭献》。保留转录中的Guaraña字形。",
                "line_start": 341,
                "line_end": 342,
                "span": "Markdown lines 341–342; print p. 297",
            },
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "location": "第13章，印刷页340，Markdown L83–85",
                "summary": "Haskell称Remondini通过复制版画推广包括Guarana在内的数位艺术家。",
                "line_start": 83,
                "line_end": 85,
                "span": "Markdown lines 83–85; print p. 340",
            },
            {
                "file": "02-sources/02-Markdown/15_CHP-15_sec_i.md",
                "location": "第15章，印刷页361，Markdown L4–6",
                "summary": "Haskell在谈到新一代历史画家时提到Guaraña；保留该处OCR字形与上下文。",
                "line_start": 4,
                "line_end": 6,
                "span": "Markdown lines 4–6; print p. 361",
            },
        ],
        "description_zh": (
            "本卡对应索引主项 Giacomo Guarana 在第9、10、13、15章的提及。第9章称其追随Tiepolo并为宫殿绘制壁画；"
            "第10章称他为Ricci与Tiepolo的学生，并报告其于1762年为莫斯科绘制《伊菲革涅亚的祭献》；第13章将他列入"
            "Remondini推广的艺术家；第15章又在新一代历史画家语境中提及他。第10、15章Markdown转录出现Guaraña，"
            "索引与第9、13章作Guarana；转录异形不另建人物。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card represents the index entry Giacomo Guarana across chapters 9, 10, 13, and 15. Chapter 9 calls him "
            "a follower of Tiepolo and says that he painted frescoes in the palace. Chapter 10 describes him as a pupil "
            "of Ricci and Tiepolo and reports that in 1762 he painted a Sacrifice of Iphigenia for Moscow. Chapter 13 "
            "includes him among artists popularised by the Remondini, and chapter 15 mentions him among a younger "
            "generation of history painters. The chapter 10 and 15 Markdown transcriptions use Guaraña, while the index "
            "and chapters 9 and 13 use Guarana; these source forms are retained as variants of this person. The Chinese "
            "name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp10-p297-guarana-iphigenia",
            "st-chp13-p340-remondini-popularised-guarana",
            "st-chp9-p260-guarana-frescoes",
        ],
    },
    {
        "candidate": "cand-1033",
        "group": "new-person:domenico-fetti-d78526d512",
        "ku": "units/persons/domenico-fetti",
        "name_zh": "多梅尼科·费蒂",
        "name_en": "Domenico Fetti",
        "index_entry": "F.csv#48",
        "index_file": "02-sources/01-book/CHP-22Index.pdf",
        "index_quote": "Fetti, Domenico",
        "index_span": "physical PDF page 12; printed p. 454; candidate locator F.csv#48",
        "chapters": "第7、9、18、19章；索引 F.csv#48",
        "sources": [
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "location": "第7章，印刷页175，Markdown L64–65",
                "summary": "Haskell称Domenico Fetti为Ferdinando, Duke of Mantua所雇用的意大利重要艺术家之一。",
                "line_start": 64,
                "line_end": 65,
                "span": "Markdown lines 64–65; print p. 175",
            },
            {
                "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "location": "第9章，印刷页262，Markdown L222",
                "summary": "Haskell将Fetti列入Grassi家族收藏的古代大师画家名单；此处仅为作品归属的概括性叙述。",
                "line_start": 222,
                "line_end": 222,
                "span": "Markdown line 222; print p. 262",
            },
            {
                "file": "02-sources/02-Markdown/18_CHP-18Conclusion.md",
                "location": "第18章结论，印刷页385，Markdown L21–22",
                "summary": "Haskell以Domenico Fetti作为意大利较少见的独立、内省型艺术家的例外；这是作者评价。",
                "line_start": 21,
                "line_end": 22,
                "span": "Markdown lines 21–22; print p. 385",
            },
            {
                "file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
                "location": "第19章附录，印刷页393，Markdown L150–152",
                "summary": "Haskell报告1789年匿名拍卖中有若干被说成来自Smith收藏的Fetti作品，并说明该类归属不能视为定论。",
                "line_start": 150,
                "line_end": 152,
                "span": "Markdown lines 150–152; print p. 393",
            },
        ],
        "description_zh": (
            "本卡对应索引印本词头Fetti, Domenico，并与第7、9、18、19章的Domenico Fetti／Fetti提及相连。"
            "第7章将其列为曼图亚公爵Ferdinando雇用的艺术家；第9章把Fetti列入一份古代大师名单；第18章以他为"
            "某类独立、内省型艺术家的例外，这是Haskell的评价；第19章仅报告1789年拍卖清单中被说成来自Smith收藏的"
            "若干Fetti作品，不据此确认作者或原藏。CSV与Markdown索引转录写作Feti，印本页图核为Fetti；校勘依据见03过程记录。"
            "中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card represents the printed index heading Fetti, Domenico and its Domenico Fetti/Fetti mentions in "
            "chapters 7, 9, 18, and 19. Chapter 7 lists him among artists employed by Ferdinando, Duke of Mantua; "
            "chapter 9 includes Fetti in a list of old masters; chapter 18 presents him as an exception to a type of "
            "individual and withdrawn artist, an assessment by Haskell; and chapter 19 reports pictures by Fetti said "
            "to have come from Smith's collection in an 1789 sale, without establishing their authorship or provenance. "
            "The CSV and Markdown index transcriptions read Feti; the printed index image was checked as Fetti, as "
            "documented in the processing record. The Chinese name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp7-p175-i16",
            "st-chp19-p393-1789-fetti-pictures-attribution",
        ],
    },
    {
        "candidate": "cand-1839",
        "group": "new-person:francesco-parmigianino-f05afd0c44",
        "ku": "units/persons/francesco-parmigianino",
        "name_zh": "弗朗切斯科·帕尔米贾尼诺",
        "name_en": "Francesco Parmigianino",
        "index_entry": "P.csv#39",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
        "index_quote": "Parmigianino, Francesco",
        "index_span": "P.csv#39; index row 41; pp. 30, 103, 222, 341, 343",
        "chapters": "第2、4、5、8、13章；索引 P.csv#39",
        "sources": [
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "location": "第2章，印刷页30，Markdown L112–115",
                "summary": "Haskell将Parmigianino列入Maffeo Barberini宫中旧大师作品的非穷尽名单；没有把每件作品逐一归给他。",
                "line_start": 112,
                "line_end": 115,
                "span": "Markdown lines 112–115; print p. 30",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "location": "第4章，印刷页103，Markdown L47",
                "summary": "Galileo引语中以Parmigianino作为假想画廊中的艺术家名目之一；保留为嵌套引语。",
                "line_start": 47,
                "line_end": 47,
                "span": "Markdown line 47; print p. 103",
            },
            {
                "file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "location": "第5章，印刷页128，Markdown L86–87",
                "summary": "一段转引以“the Parmigianino”列举艺术家；此处不推断具体作品身份。",
                "line_start": 86,
                "line_end": 87,
                "span": "Markdown lines 86–87; print p. 128",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "location": "第8章，印刷页222，Markdown L131–133",
                "summary": "Haskell列举Cardinal Russo收藏中被归于Parmigianino等艺术家的作品，随后特别指出Velasquez对Juan de Pareja的肖像。",
                "line_start": 131,
                "line_end": 133,
                "span": "Markdown lines 131–133; print p. 222",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "location": "第8章，印刷页232，Markdown L255–256",
                "summary": "Haskell报告Ferdinand于1698年购入一件Parmigianino的Madonna del Collo Lungo；对应作品身份另按S3候选组记录。",
                "line_start": 255,
                "line_end": 256,
                "span": "Markdown lines 255–256; print p. 232",
            },
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "location": "第13章，印刷页341，Markdown L91–94",
                "summary": "Haskell称Zanetti在伦敦购得Lord Arundel的Parmigianino drawings，并称这些图稿影响其趣味。",
                "line_start": 91,
                "line_end": 94,
                "span": "Markdown lines 91–94; print p. 341",
            },
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "location": "第13章，印刷页343，Markdown L109–112",
                "summary": "Haskell叙述Zanetti委托Faldoni复制Parmigianino相关作品，并说Zanetti的彩色明暗木刻多取材于其图稿。",
                "line_start": 109,
                "line_end": 112,
                "span": "Markdown lines 109–112; print p. 343",
            },
        ],
        "description_zh": (
            "本卡对应索引词头Parmigianino, Francesco，在第2、4、5、8、13章均有提及。第2章将Parmigianino列入"
            "Maffeo Barberini宫中旧大师画作的非穷尽名单；第4、5章分别见于嵌套引语和转引；第8章讨论其作品及一件"
            "题为Madonna del Collo Lungo的作品；第13章涉及Zanetti购得的图稿、作品复制和木刻取材。各具体作品候选、"
            "归属及收藏关系仍按对应S2断言逐条待审。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card represents the index heading Parmigianino, Francesco, which appears in chapters 2, 4, 5, 8, and 13. "
            "Chapter 2 includes Parmigianino in a non-exhaustive list of old-master paintings in Maffeo Barberini's "
            "palace; chapters 4 and 5 mention the name in a nested quotation and a reported passage; chapter 8 discusses "
            "works attributed to him and a Madonna del Collo Lungo; and chapter 13 discusses drawings acquired by Zanetti, "
            "reproductions, and woodcuts based on those drawings. Individual work identities, attributions, and collecting "
            "relations remain subject to review against their S2 statements. The Chinese name is a project working transliteration."
        ),
        "relation_ids": ["st-chp2-seci-l108-119-palace-paintings-by-parmigianino"],
    },
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def keep_bom_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def source_quote(item: dict) -> str:
    if item.get("quote_text"):
        return item["quote_text"]
    lines = (ROOT / item["file"]).read_text(encoding="utf-8-sig").splitlines()
    return "\n".join(lines[item["line_start"] - 1 : item["line_end"]])


def make_card(t: dict) -> str:
    sources = []
    for item in t["sources"]:
        sources.append(
            {
                "citation": BOOK_CITATION,
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [
                    {
                        "source_span": item.get("span")
                        or f"Markdown lines {item.get('line_start', '?')}–{item.get('line_end', '?')}",
                        "text": source_quote(item),
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": item["file"],
                    "source_span": item["span"],
                },
            }
        )
    sources.append(
        {
            "citation": INDEX_CITATION,
            "location": f"全书索引 {t['index_entry']}",
            "sentence_summary": f"索引词头为“{t['index_quote']}”；页图校勘或页码范围见索引定位。",
            "original_quotes": [{"source_span": t["index_span"], "text": t["index_quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": t["index_file"],
                "source_span": t["index_span"],
            },
        }
    )
    fm_data = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": CARD_REF,
    }
    fm = yaml.safe_dump(fm_data, allow_unicode=True, sort_keys=False, width=1000)
    candidate_rows = "、".join(f"`{x}`" for x in t["group_candidates"])
    relation_rows = "\n".join(
        f"- [`{sid}`](../../tables/book-statements.jsonl)：S2直接关系候选，待 S6 逐条审查。"
        for sid in t["relation_ids"]
    )
    return (
        f"---\n{fm}---\n\n"
        "## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}\n\n"
        f"**English:** {t['description_en']}\n\n"
        "## 关系与证据\n\n### 身份与外部链接\n\n"
        f"- S3跨章身份组：候选 {candidate_rows}；查看 [alignment.csv](../../tables/alignment.csv) 与"
        f"[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017i)。"
        "本批未采用外部权威标识。\n\n"
        "### 关系记录\n\n"
        "当前没有登记在 `relations.csv` 的正式关系。以下 S2 直接关系候选保留待 S6 审查，不因 S4 登记而视为已确认：\n\n"
        f"{relation_rows}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Register three reviewed cross-chapter person groups in S4.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by = {r["candidate_id"]: r for r in candidates}
    align_by = {
        r["candidate_id"]: r
        for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    manifest_by = {r["ku_id"]: r for r in manifest}
    statement_data = [
        json.loads(line)
        for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statements = {d["statement_id"]: d for d in statement_data}

    planned_alignments = [dict(r) for r in alignments]
    planned_align_by = {
        r["candidate_id"]: r
        for r in planned_alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    planned_manifest = [dict(r) for r in manifest]
    accepted_lines = read_text(ACCEPTED_PATH).splitlines()
    cards: dict[Path, str] = {}
    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before_totals = sync.build_type_table(before_stats)
    relation_total = 0
    process_evidence = read_text(PROCESS_EVIDENCE_PATH)

    for t in TARGETS:
        cid, group, ku = t["candidate"], t["group"], t["ku"]
        assert cid in candidate_by and cid in align_by
        c, a = candidate_by[cid], planned_align_by[cid]
        assert c["suggested_type"] == "person"
        assert a["decision"] == "new" and not a.get("ku_id")
        assert sync.get_group(a.get("resolution_note", "")) == group
        group_members = [
            r["candidate_id"]
            for r in alignments
            if r.get("candidate_id")
            and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == group
        ]
        assert group_members == [cid], f"unexpected person group members for {group}: {group_members}"
        t["group_candidates"] = group_members
        assert ku not in manifest_by
        card_path = ROOT / f"04-knowledge/{ku}.md"
        assert not card_path.exists()
        assert f"- 04-knowledge/{ku}.md" not in accepted_lines
        assert not any(
            r.get("name_en", "").casefold() == t["name_en"].casefold()
            for r in manifest
            if r["type"] == "person"
        ), f"same-name person KU already exists: {t['name_en']}"
        if t["candidate"] == "cand-1033":
            assert c["canonical_name"] == "Fetti, Domenico"
            assert "p.454印本词头为“Fetti, Domenico”" in process_evidence
        else:
            index_text = (ROOT / t["index_file"]).read_text(encoding="utf-8-sig")
            assert t["index_quote"] in index_text, f"index name missing: {t['index_entry']}"
        for item in t["sources"]:
            quote = source_quote(item)
            assert quote
            if item["file"].lower().endswith(".pdf"):
                assert (ROOT / item["file"]).is_file() and item.get("span")
            else:
                assert quote in (ROOT / item["file"]).read_text(encoding="utf-8-sig")
        for sid in t["relation_ids"]:
            assert sid in statements
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
        relation_total += len(t["relation_ids"])
        cards[card_path] = make_card(t)
        a["ku_id"] = ku
        a["process_ref"] = PROCESS_REF
        a["resolution_note"] += (
            f" S4 registration ({DATE}): mapped {group} to {ku}; cross-chapter source anchors are retained. "
            f"{len(t['relation_ids'])} direct relation candidates remain pending S6."
        )
        planned_manifest.append(
            {
                "ku_id": ku,
                "type": "person",
                "canonical_name": f"{t['name_zh']}（{t['name_en']}）",
                "name_en": t["name_en"],
                "source_task": TASK,
                "card_path": f"04-knowledge/{ku}.md",
            }
        )

    planned_manifest.sort(key=lambda r: r["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = prior.insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")
    stats = sync.summarize_by_type(candidate_by.values(), planned_alignments)
    _, totals = sync.build_type_table(stats)
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    process_text = read_text(PROCESS_PATH)
    anchor = '<a id="s4-person-endpoints-20261017i"></a>'
    assert anchor not in process_text
    process_text += (
        "\n\n"
        + anchor
        + "\n\n### S4 person：Giacomo Guarana、Domenico Fetti 与 Parmigianino 登记（2026-10-17）\n\n"
        "S3 的三个跨章 person `new` 身份组均经同类型既有 KU 与别名检索复核，未发现可复用的现有人物卡；每组各登记一个 KU。"
        "Guarana 的索引主项与正文全名相合，第10、15章转录中的 Guaraña 保留为异写；人物候选 `cand-1237` 与作品索引子项 `cand-1238`"
        "分属 person/work，后者已在本轮 S3 合入正文作品组。第9章 Markdown 页码层写作200，但PDF物理第22页页图清楚显示印刷页260；"
        "人物卡引用页图并保留该转录差异。Fetti 的规范词头沿用印本校勘结果：索引p.454印本为Fetti，CSV与Markdown转录为Feti。"
        "Parmigianino 的索引姓名及第2、4、5、8、13章的来源语境支持同一人物候选。未加入外部身份记录或补写来源未载的人物传记；"
        "6条S2关系候选均保留待S6，未写入正式边。\n\n"
        "| 候选 / S3 身份组 | KU | 跨章来源与索引锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
    )
    for t in TARGETS:
        process_text += (
            f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['chapters']} | {len(t['relation_ids'])} |\n"
        )
    process_text += "\n"
    result_text += "\n\n### S4 person：三组跨章人物身份登记（2026-10-17）\n\n"
    for t in TARGETS:
        result_text += (
            f"- `{t['candidate']}` / `{t['group']}` → [{t['name_zh']}（{t['name_en']}）]"
            f"(../units/{t['ku']}.md)；{t['chapters']}；{len(t['relation_ids'])}条直接关系候选留待S6。\n"
        )
    result_text += "\n本批未登记正式关系或外部身份标识；候选卡提供指向 alignment.csv 与过程记录的内部身份入口。\n"

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert relation_total == 6

    if args.dry_run:
        print(
            f"DRY-RUN OK: person groups={len(TARGETS)}; cards={len(cards)}; "
            f"direct relation candidates={relation_total}"
        )
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
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(
        f"APPLIED: person groups={len(TARGETS)}; cards={len(cards)}; "
        f"manifest={len(planned_manifest):,}; registered groups={totals['registered_groups']:,}; "
        f"pending groups={totals['pending_groups']:,}"
    )


if __name__ == "__main__":
    main()
