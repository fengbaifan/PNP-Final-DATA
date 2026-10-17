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
ANCHOR = "s4-crosschapter-person-endpoints-mead-maderno-zanetti-20261017"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidates": ["cand-1604"],
        "group": "new-person:mead-richard-ffc4adb9cf",
        "ku": "units/persons/richard-mead",
        "name_zh": "理查德·米德",
        "name_en": "Richard Mead",
        "index_entry": "M.csv#144",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "index_line": 146,
        "index_quote": "Mead, Dr Richard",
        "index_span": "M.csv#144; CSV line 146; pp. 118, 301, 343n, 357",
        "chapters": "第4、10、14章；索引 M.csv#144",
        "relation_ids": [
            "st-chp4-sec-ii-p118-mead-purchase",
            "st-chp10-p301-mead-newton-friendship",
            "st-chp10-p301-smith-mead-letter",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "line_start": 226,
                "line_end": 226,
                "location": "第4章，印刷页118，Markdown L226",
                "span": "Markdown line 226; print p. 118",
                "summary": "Haskell将Dr Richard Mead列为购买Massimi遗产中部分绘画、素描和古物的买家。",
                "quote_text": "Dr Richard Mead.",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 389,
                "line_end": 389,
                "location": "第10章，印刷页301，Markdown L389",
                "span": "Markdown line 389; print p. 301",
                "summary": "Haskell引用Smith称Mead为朋友，并称他是英国重要艺术收藏家及Newton的好友。",
                "quote_text": "the ‘celeberrimo S.r Dottor Mead’",
            },
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "line_start": 111,
                "line_end": 111,
                "location": "第14章，印刷页357，Markdown L111",
                "span": "Markdown line 111; print p. 357",
                "summary": "Haskell称Algarotti曾在伦敦见到Mead收藏中的Pannini作品。",
                "quote_text": "Dr Mead’s collection in London",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Mead, Dr Richard”及正文中的Dr Richard Mead／Dr Mead。第4章称他从Massimi遗产出售中购入部分绘画、素描和古物；"
            "第10章称他为Joseph Smith的朋友、英国重要艺术收藏家和Isaac Newton的好友；第14章提到Mead在伦敦的收藏中有Pannini的作品。"
            "以上仅记录本书明确给出的身份与语境。"
        ),
        "description_en": (
            "This card represents the index entry “Mead, Dr Richard” and Dr Richard Mead / Dr Mead in the text. Chapter 4 names him among buyers of some paintings, drawings, and antiquities sold from the Massimi estate. Chapter 10 calls him a friend of Joseph Smith, a leading English art collector, and a great friend of Isaac Newton. Chapter 14 refers to Pannini paintings in Mead’s London collection. These statements retain the scope given in the book."
        ),
        "identity_extra": "跨章对齐依据为索引全名与第4章全名、后续章节的Dr Mead及收藏语境；未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-1604 remains the source-local person group new-person:mead-richard-ffc4adb9cf. The index full name M.csv#144 and chapter 4 p.118 “Dr Richard Mead” anchor chapter 10 p.301 “Dottor Mead” and chapter 14 p.357 “Dr Mead’s collection”; no exact existing person KU matched. No external identity source was accessed."
        ),
    },
    {
        "candidates": ["cand-1477", "cand-4873"],
        "group": "new-person:carlo-maderno-530c4fdfa7",
        "ku": "units/persons/carlo-maderno",
        "name_zh": "卡洛·马代尔诺",
        "name_en": "Carlo Maderno",
        "index_entry": "M.csv#14",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "index_line": 16,
        "index_quote": "Maderno, Carlo",
        "index_span": "M.csv#14; CSV line 16; pp. 27, 34, 47, 48, 71, 74, 75, 396",
        "chapters": "第2、3章及 Postscript；索引 M.csv#14",
        "relation_ids": [
            "st-chp2-seci-l71-80-maderno-nave-continuation",
            "st-chp3-secii-l62-72-maderno-brought-in-work-proceeded",
            "st-chp3-secii-l125-135-borromini-early-employment",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "line_start": 72,
                "line_end": 72,
                "location": "第2章，印刷页27，Markdown L72",
                "span": "Markdown line 72; print p. 27",
                "summary": "Maderno在圣彼得大教堂增建中殿方案的讨论中被具名提及；紧接的迁居和任职叙述不归于Maderno。",
                "quote_text": "Carlo Maderno",
            },
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "line_start": 72,
                "line_end": 72,
                "location": "第3章，印刷页71，Markdown L72",
                "span": "Markdown line 72; print p. 71",
                "summary": "Haskell称Peretti-Montalto将罗马知名建筑师Maderno带入正在推进的教堂工程。",
                "quote_text": "He brought in the best known architect in Rome, Carlo Maderno",
            },
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "line_start": 119,
                "line_end": 120,
                "location": "第3章，印刷页74，Markdown L119–120",
                "span": "Markdown lines 119–120; print p. 74",
                "summary": "Haskell称Ludovisi安排建筑师委员会审查Grassi的方案，其中包括Carlo Maderno。",
                "quote_text": "including the painter Domenichino and Carlo\nMaderno",
            },
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "line_start": 133,
                "line_end": 133,
                "location": "第3章，印刷页75，Markdown L133",
                "span": "Markdown line 133; print p. 75",
                "summary": "Haskell称Borromini早年曾在Maderno和Bernini手下承担较小任务。",
                "quote_text": "under Maderno and Bernini",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "line_start": 12,
                "line_end": 12,
                "location": "Postscript，印刷页396，Markdown L12",
                "span": "Markdown line 12; print p. 396",
                "summary": "Postscript提到Hibbard关于Carlo Maderno及家族宫殿起源的研究。",
                "quote_text": "Howard Hibbard’s monograph on Carlo Maderno",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Carlo Maderno”及候选cand-1477、cand-4873。第2章将Maderno置于圣彼得大教堂增建中殿方案的讨论中；"
            "第3章称Peretti-Montalto将他带入教堂工程，并称Borromini曾在Maderno与Bernini手下承担较小任务。Postscript提及Hibbard关于Maderno家族宫殿起源的专著。"
        ),
        "description_en": (
            "This card represents the index entry “Carlo Maderno” and candidates cand-1477 and cand-4873. Chapter 2 names Maderno in its discussion of the proposed nave addition to St Peter’s. Chapter 3 says Peretti-Montalto brought him into a church project and that Borromini had earlier worked on comparatively minor tasks under Maderno and Bernini. The Postscript refers to Hibbard’s monograph on Maderno and the origins of the family palace."
        ),
        "identity_extra": "cand-1477与cand-4873按同一全名合并为一个跨章人物KU；未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-1477 and cand-4873 remain one person group, new-person:carlo-maderno-530c4fdfa7, on the identical full name in chapter 2, chapter 3, and the Postscript, with index M.csv#14 as the chapter-spanning locator. In chapter 2 p.27 the name occurs in the nave-plan passage; the adjacent pronoun about moving to Spoleto and becoming bishop refers to another person and is not attributed to Maderno. No exact existing person KU matched; no external identity source was accessed."
        ),
    },
    {
        "candidates": ["cand-2861", "cand-9280"],
        "group": "new-person:girolamo-zanetti-2aceef0ec5",
        "ku": "units/persons/girolamo-zanetti",
        "name_zh": "吉罗拉莫·扎内蒂",
        "name_en": "Girolamo Zanetti",
        "index_entry": "UVWXYZ.csv#198",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "index_line": 200,
        "index_quote": "Zanetti, Girolamo",
        "index_span": "UVWXYZ.csv#198; CSV line 200; pp. 268n, 306, 360n",
        "chapters": "第9、10、14章；索引 UVWXYZ.csv#198",
        "relation_ids": [
            "st-chp10-p306-note5-letter-quote",
            "st-chp10-p306-zanetti-criticism-of-gems",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
                "line_start": 90,
                "line_end": 90,
                "location": "第9章注释，印刷页268注，Markdown L90",
                "span": "Markdown line 90; index locator p. 268n",
                "summary": "脚注引用Girolamo Zanetti于1743年5月22日的文字及其1885年刊本。",
                "quote_text": "[Girolamo Zanetti]: 22 Maggio 1743",
            },
            {
                "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
                "line_start": 120,
                "line_end": 120,
                "location": "第9章注释，印刷页274注，Markdown L120",
                "span": "Markdown line 120; index locator p. 274n",
                "summary": "脚注再次引用Girolamo Zanetti于1743年3月25日的文字。",
                "quote_text": "[Girolamo Zanetti]: 25 Marzo 1743",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 492,
                "line_end": 492,
                "location": "第10章注释，印刷页276注1，Markdown L492",
                "span": "Markdown line 492; print p. 276n1",
                "summary": "脚注引用Girolamo Zanetti的《Elogio》并讨论其1708年日期说法；该书未在本任务中独立查阅。",
                "quote_text": "Girolamo Zanetti: Elogio, 1781 (published 1818)",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 439,
                "line_end": 440,
                "location": "第10章，印刷页306，Markdown L439–440",
                "span": "Markdown lines 439–440; print p. 306",
                "summary": "Haskell称Girolamo Zanetti曾评论其兄弟Antonio Maria为Smith复制宝石所得报酬及Smith古物的质量。",
                "quote_text": "Girolamo\nZanetti later said that his brother Antonio Maria",
            },
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "line_start": 218,
                "line_end": 218,
                "location": "第14章注释，印刷页360注，Markdown L218",
                "span": "Markdown line 218; index locator p. 360n",
                "summary": "脚注将Girolamo Zanetti列为1743年评论Algarotti者之一。",
                "quote_text": "comments of Girolamo Zanetti in 1743",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Zanetti, Girolamo”及候选cand-2861、cand-9280。第9、10、14章多处以全名引用其1743年文字或《Elogio》；"
            "第10章p.306称他曾评论其兄弟Antonio Maria为Joseph Smith复制宝石所得报酬及Smith古物。既有Anton Maria Zanetti the Elder人物卡与Girolamo为不同人物。"
        ),
        "description_en": (
            "This card represents the index entry “Zanetti, Girolamo” and candidates cand-2861 and cand-9280. Chapters 9, 10, and 14 cite his writings from 1743 or his Elogio. On p. 306, chapter 10 says that he commented on his brother Antonio Maria’s payment for copying gems for Joseph Smith and on Smith’s antiquities. The existing person card for Anton Maria Zanetti the Elder represents a different person."
        ),
        "identity_extra": "跨章全名为Girolamo Zanetti；第10章明确将Anton Maria Zanetti称为其兄弟，二人不合并。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-2861 and cand-9280 remain one person group, new-person:girolamo-zanetti-2aceef0ec5. The full name occurs in the chapter 9 notes, chapter 10 notes/text, and chapter 14 note; index UVWXYZ.csv#198 supplies pp. 268n, 306, and 360n. Chapter 10 p.306 explicitly identifies Anton Maria as Girolamo’s brother, so this group remains distinct from the existing Anton Maria Zanetti the Elder KU. No external identity source was accessed."
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
    quote = item["quote_text"]
    assert quote in block, f"quote missing: {item['file']}:{item['line_start']}–{item['line_end']}"
    return quote


def make_card(t: dict) -> str:
    all_sources = list(t["sources"]) + [
        {
            "citation": INDEX_CITATION,
            "file": t["index_file"],
            "line_start": t["index_line"],
            "line_end": t["index_line"],
            "location": f"全书索引 {t['index_entry']}",
            "span": t["index_span"],
            "summary": f"索引词头为“{t['index_quote']}”；页码范围按CSV登记。",
            "quote_text": t["index_quote"],
        }
    ]
    card_sources = []
    for item in all_sources:
        line_label = (
            f"Markdown lines {item['line_start']}–{item['line_end']}"
            if item["line_start"] != item["line_end"]
            else f"Markdown line {item['line_start']}"
        )
        card_sources.append(
            {
                "citation": item.get("citation", BOOK_CITATION),
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [{"source_span": line_label, "text": source_quote(item)}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": item["file"],
                    "source_span": item["span"],
                },
            }
        )
    frontmatter = yaml.safe_dump(
        {
            "title": f"{t['name_zh']}（{t['name_en']}）",
            "name_en": t["name_en"],
            "type": "person",
            "evidence_status": "source_backed",
            "sources": card_sources,
            "created": DATE,
            "updated": DATE,
            "process_ref": CARD_REF,
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    candidate_labels = ", ".join(f"`{cid}`" for cid in t["candidates"])
    relation_rows = "\n".join(
        f"- [`{sid}`](../../tables/book-statements.jsonl)：S2直接关系候选，待S6审查。"
        for sid in t["relation_ids"]
    )
    return (
        f"---\n{frontmatter}---\n\n## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}\n\n**English:** {t['description_en']}\n\n"
        "## 关系与证据\n\n### 身份与外部链接\n\n"
        f"- S3人物组：{candidate_labels}；查看 [alignment.csv](../../tables/alignment.csv) 与[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
        f"本批未采用外部权威标识。{t['identity_extra']}\n\n"
        "### 关系记录\n\n当前没有登记在 `relations.csv` 的正式关系。以下直接关系候选仍待S6逐条审查：\n\n"
        f"{relation_rows}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Register three reviewed cross-chapter person groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

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
    accepted_lines = read_text(ACCEPTED_PATH).splitlines()
    cards = {}
    registered_flags = []
    relation_total = 0

    for t in TARGETS:
        ku = t["ku"]
        member_ids = t["candidates"]
        member_rows = [candidate_by[cid] for cid in member_ids]
        alignment_rows = [planned_by[cid] for cid in member_ids]
        assert all(c["suggested_type"] == "person" for c in member_rows)
        assert all(a["decision"] == "new" and a.get("ku_id", "") in ("", ku) for a in alignment_rows)
        assert all(sync.get_group(a.get("resolution_note", "")) == t["group"] for a in alignment_rows)
        group_members = [
            r["candidate_id"]
            for r in alignments
            if r.get("candidate_id")
            and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == t["group"]
        ]
        assert sorted(group_members) == sorted(member_ids), f"unexpected members in {t['group']}: {group_members}"
        card_path = ROOT / f"04-knowledge/{ku}.md"
        accepted_ref = f"- 04-knowledge/{ku}.md" in accepted_lines
        flags = [all(a.get("ku_id") == ku for a in alignment_rows), ku in manifest_by, card_path.exists(), accepted_ref]
        assert len(set(flags)) == 1, f"partial registration state for {t['group']}: {flags}"
        is_registered = flags[0]
        registered_flags.append(is_registered)
        exact_name_matches = [
            r for r in manifest
            if r["type"] == "person" and r.get("name_en", "").casefold() == t["name_en"].casefold()
        ]
        assert not exact_name_matches or (is_registered and all(r["ku_id"] == ku for r in exact_name_matches))
        assert t["index_quote"].encode("ascii") in (ROOT / t["index_file"]).read_bytes()
        for item in t["sources"]:
            source_quote(item)
        source_quote(
            {
                "file": t["index_file"],
                "line_start": t["index_line"],
                "line_end": t["index_line"],
                "quote_text": t["index_quote"],
            }
        )
        for sid in t["relation_ids"]:
            assert sid in statements, f"missing S2 statement {sid}"
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert any(cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) for cid in member_ids)
        if is_registered:
            assert card_path.read_text(encoding="utf-8-sig") == make_card(t)
            for a, c in zip(alignment_rows, member_rows):
                assert a.get("process_ref") == PROCESS_REF
                assert f"S4 registration: group {t['group']} mapped to {ku};" in a.get("resolution_note", "")
                assert c.get("detail") == t["s3_note"]
        else:
            for a, c in zip(alignment_rows, member_rows):
                a["ku_id"] = ku
                a["process_ref"] = PROCESS_REF
                a["resolution_note"] += (
                    f" {t['s3_note']} S4 registration: group {t['group']} mapped to {ku}; "
                    f"{len(t['relation_ids'])} direct relation candidates remain pending S6."
                )
                c["detail"] = t["s3_note"]
            cards[card_path] = make_card(t)
        relation_total += len(t["relation_ids"])

    newly_registered = sum(not flag for flag in registered_flags)
    planned_manifest = [dict(r) for r in manifest]
    for t, registered in zip(TARGETS, registered_flags):
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
    assert totals["pending_members"] == before_totals["pending_members"] - len(
        [cid for t, registered in zip(TARGETS, registered_flags) if not registered for cid in t["candidates"]]
    )
    assert relation_total == 8

    process_text = read_text(PROCESS_PATH)
    process_record = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S3→S4 person：Mead、Maderno 与 Zanetti 跨章身份组登记（2026-10-17）\n\n"
        "按候选全名、索引页码及跨章正文/注释锚点复核三个person new组。cand-1477与cand-4873共用Carlo Maderno组；第2章p.27的Maderno仅是中殿方案语境中的具名建筑师，紧接的迁居Spoleto及任主教叙述不归给他。cand-2861与cand-9280共用Girolamo Zanetti组；第10章p.306明确称Anton Maria为Girolamo之兄，故与既有Anton Maria Zanetti the Elder卡区分。Richard Mead由第4章p.118全名、索引和第10、14章的称谓/收藏语境连接。未引入外部身份断言；8条S2直接关系候选继续留待S6。\n\n"
        "| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
    )
    for t in TARGETS:
        process_record += (
            f"| `{', '.join(t['candidates'])}` / `{t['group']}` | `{t['ku']}` | {t['chapters']} | {len(t['relation_ids'])} |\n"
        )
    process_record += "\n"
    if f'<a id="{ANCHOR}"></a>' in process_text:
        assert all(t["group"] in process_text for t in TARGETS)
    else:
        process_text += process_record

    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    result_heading = "### S3→S4 person：Mead、Maderno 与 Zanetti 跨章身份组登记（2026-10-17）"
    if result_heading in result_text:
        assert all(t["ku"] in result_text for t in TARGETS)
    else:
        result_text += "\n\n" + result_heading + "\n\n"
        for t in TARGETS:
            result_text += (
                f"- `{', '.join(t['candidates'])}` / `{t['group']}` → "
                f"[{t['name_zh']}（{t['name_en']}）](../{t['ku']}.md)；{t['chapters']}；"
                f"{len(t['relation_ids'])}条直接关系候选留待S6。\n"
            )
        result_text += "\n本批未新增正式关系或外部身份断言。\n"

    if args.dry_run:
        state = "ALREADY REGISTERED" if newly_registered == 0 else "DRY-RUN OK"
        print(f"{state}: person groups={len(TARGETS)}; mappings={sum(len(t['candidates']) for t in TARGETS)}; cards to create={len(cards)}; direct relation candidates={relation_total}")
        print(
            f"manifest: {len(manifest):,}->{len(planned_manifest):,}; registered groups: "
            f"{before_totals['registered_groups']:,}->{totals['registered_groups']:,}; "
            f"pending groups: {before_totals['pending_groups']:,}->{totals['pending_groups']:,}; "
            f"pending candidate mappings: {before_totals['pending_members']:,}->{totals['pending_members']:,}"
        )
        for t in TARGETS:
            print(f"{','.join(t['candidates'])} -> {t['ku']}; group={t['group']}; {len(t['relation_ids'])} S6 candidates")
        return

    if newly_registered == 0:
        print(f"ALREADY REGISTERED: groups={len(TARGETS)}; cards={len(cards)}; direct relation candidates={relation_total}")
        return
    for path, card in cards.items():
        path.write_bytes(card.encode("utf-8"))
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned)
    sync.write_csv(ENTITY_PATH, candidate_fields, candidates)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(
        f"APPLIED: groups={newly_registered}; candidate mappings="
        f"{sum(len(t['candidates']) for t in TARGETS if not registered_flags[TARGETS.index(t)])}; "
        f"cards={len(cards)}; registered={totals['registered_groups']:,}; pending={totals['pending_groups']:,}"
    )


if __name__ == "__main__":
    main()
