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
ANCHOR = "s4-crosschapter-person-endpoints-resta-palladio-walpole-20261017"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-2134",
        "group": "new-person:resta-sebastiano-912fe4613b",
        "ku": "units/persons/sebastiano-resta",
        "name_zh": "塞巴斯蒂亚诺·雷斯塔",
        "name_en": "Sebastiano Resta",
        "index_entry": "Q-R.csv#61",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
        "index_line": 63,
        "index_quote": "Resta, Padre Sebastiano",
        "index_span": "Q-R.csv#61; CSV line 63; pp. 77, 135n, 155, 211n",
        "chapters": "第3、5、6、8章；索引 Q-R.csv#61",
        "relation_ids": [
            "st-chp3-seciv-l8-14-resta-oval-scenes",
            "st-chp6-p155-resta-landscape-criticism",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "line_start": 12,
                "line_end": 13,
                "location": "第3章，印刷页77，Markdown L12–13",
                "span": "Markdown lines 12–13; print p. 77",
                "summary": "Haskell称约1700年由奥拉托会学者与收藏家Padre Sebastiano Resta选出的艺术家绘制一组椭圆圣经场景。",
                "quote_text": "chosen by the Oratorian scholar and collector Padre Sebastiano Resta",
            },
            {
                "file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
                "line_start": 138,
                "line_end": 138,
                "location": "第5章注释，印刷页135注，Markdown L138",
                "span": "Markdown line 138; index locator p. 135n",
                "summary": "脚注引用Sebastiano Resta于1704年2月27日致Bernardino Lorca的信。",
                "quote_text": "letter of Sebastiano Resta dated 27 February 1704",
            },
            {
                "file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "line_start": 108,
                "line_end": 108,
                "location": "第6章，印刷页155，Markdown L108",
                "span": "Markdown line 108; print p. 155",
                "summary": "Haskell称Resta为学者、收藏家及文艺复兴素描研究先驱，并引述他对风景画家的意见。",
                "quote_text": "Padre Sebastiano Resta, a scholarly collector and pioneer in the study of Renaissance drawings",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "line_start": 95,
                "line_end": 95,
                "location": "第8章，印刷页211注，Markdown L95",
                "span": "Markdown line 95; index locator p. 211n",
                "summary": "脚注称Ottavio、Andrea与Lorenzo的罗马艺术活动见于Resta致Francesco Gabburri的两封信。",
                "quote_text": "two letters from Sebastiano Resta to Francesco Gabburri",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Resta, Padre Sebastiano”及第3、5、6、8章中的Sebastiano Resta。第3章称他为奥拉托会学者和收藏家，约1700年选定绘制一组椭圆圣经场景的艺术家；"
            "第6章称他为文艺复兴素描研究先驱，并引述其对风景画的意见。第5、8章注释分别引用他的书信。"
        ),
        "description_en": (
            "This card represents the index entry “Resta, Padre Sebastiano” and Sebastiano Resta in chapters 3, 5, 6, and 8. Chapter 3 calls him an Oratorian scholar and collector and says that he selected artists for a group of oval biblical scenes around 1700. Chapter 6 calls him a pioneer in the study of Renaissance drawings and quotes his view of landscape painting. Notes in chapters 5 and 8 cite his letters."
        ),
        "identity_extra": "跨章姓名与索引主项相合；未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-2134 remains the source-local person group new-person:resta-sebastiano-912fe4613b. The index full heading and chapter 3 p.77 / chapter 6 p.155 full-name anchors align the chapter 5 and 8 letter citations. No exact existing person KU matched; no external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-1807",
        "group": "new-person:andrea-palladio-5e91b207a4",
        "ku": "units/persons/andrea-palladio",
        "name_zh": "安德烈亚·帕拉迪奥",
        "name_en": "Andrea Palladio",
        "index_entry": "P.csv#6",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
        "index_line": 8,
        "index_quote": "Palladio, Andrea",
        "index_span": "P.csv#6; CSV line 8; pp. 103, 278, 348, 356, 357, 407",
        "chapters": "第4、10、14章及 Postscript；索引 P.csv#6",
        "relation_ids": [
            "st-chp10-p278-whig-sons-admired-venice-and-palladio",
            "st-chp14-p348-palladio-quote-and-prussia",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "line_start": 51,
                "line_end": 51,
                "location": "第4章，印刷页103，Markdown L51",
                "span": "Markdown line 51; print p. 103",
                "summary": "Haskell在建筑史叙述中将Palladio列入恢复古典建筑秩序的建筑师。",
                "quote_text": "Bramante, Serlio, Palladio, Vignola",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 36,
                "line_end": 36,
                "location": "第10章，印刷页278，Markdown L36",
                "span": "Markdown line 36; print p. 278",
                "summary": "Haskell称Palladio为威尼斯的主要建筑师，并称英国贵族之子仰慕他。",
                "quote_text": "Venice and its leading architect Palladio",
            },
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "line_start": 17,
                "line_end": 17,
                "location": "第14章，印刷页348，Markdown L17",
                "span": "Markdown line 17; print p. 348",
                "summary": "Haskell称Algarotti对Palladio作品的热情及其向普鲁士传播建筑师声誉的活动。",
                "quote_text": "helped to spread the cult for the architect to Prussia",
            },
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "line_start": 113,
                "line_end": 115,
                "location": "第14章，印刷页357，Markdown L113–115",
                "span": "Markdown lines 113–115; print p. 357",
                "summary": "Haskell描述Canaletto依照Palladio方案构想大运河景观，并提及Palladio对Rialto的方案。",
                "quote_text": "Palladio’s plans for the Rialto",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "line_start": 168,
                "line_end": 168,
                "location": "Postscript，印刷页407，Markdown L168",
                "span": "Markdown line 168; print p. 407",
                "summary": "Postscript称Smith委托系列体现对Palladio及其建筑原则的推崇。",
                "quote_text": "glorification of Palladio and his architectural principles",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Andrea Palladio”及第4、10、14章和Postscript中的建筑师Palladio。第10章称他为威尼斯主要建筑师；第14章记载Algarotti对其作品的推崇及Canaletto依其方案构想运河景观；"
            "Postscript将Joseph Smith的建筑图像委托与对Palladio建筑原则的推崇联系起来。"
        ),
        "description_en": (
            "This card represents the index entry “Andrea Palladio” and the architect Palladio in chapters 4, 10, 14, and the Postscript. Chapter 10 calls him Venice’s leading architect. Chapter 14 records Algarotti’s admiration for his works and Canaletto’s view conceived according to his scheme. The Postscript connects Joseph Smith’s architectural commissions with the glorification of Palladio’s principles."
        ),
        "identity_extra": "索引全名与跨章对建筑师Palladio的称谓相合；作品及委托关系仍按各自语境保留。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-1807 remains the person group new-person:andrea-palladio-5e91b207a4. Index P.csv#6 and chapter 4 p.103, chapter 10 p.278, chapter 14 pp.348/357, and Postscript p.407 consistently refer to the architect Andrea Palladio; no exact existing person KU matched. No external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-2798",
        "group": "new-person:horace-walpole-71c5b539dc",
        "ku": "units/persons/horace-walpole",
        "name_zh": "霍勒斯·沃波尔",
        "name_en": "Horace Walpole",
        "index_entry": "UVWXYZ.csv#135",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "index_line": 137,
        "index_quote": "Walpole, Horace",
        "index_span": "UVWXYZ.csv#135; CSV line 137; pp. 264, 301, 356",
        "chapters": "第9、10、14章；索引 UVWXYZ.csv#135",
        "relation_ids": [
            "st-chp10-p301-smith-unpopularity-and-walpole",
            "st-chp14-p356-veronese-for-walpole-conditional-1738",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "line_start": 241,
                "line_end": 241,
                "location": "第9章，印刷页264，Markdown L241",
                "span": "Markdown line 241; print p. 264",
                "summary": "Haskell称Horace Walpole于1739至1741年在意大利旅行时听闻Sagredo收藏拟出售。",
                "quote_text": "Horace Walpole, travelling in Italy between 1739 and 1741",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 389,
                "line_end": 389,
                "location": "第10章，印刷页301，Markdown L389",
                "span": "Markdown line 389; print p. 301",
                "summary": "Haskell称Walpole曾讥称Joseph Smith为“威尼斯商人”。",
                "quote_text": "Walpole characteristically jeered at him as ‘the Merchant of Venice’",
            },
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "line_start": 102,
                "line_end": 102,
                "location": "第14章，印刷页356，Markdown L102",
                "span": "Markdown line 102; print p. 356",
                "summary": "Haskell称Algarotti早在1738年便计划为Walpole购入一幅Veronese作品；原文记计划，不记实际购得。",
                "quote_text": "as early as 1738 he was planning to get hold of a Veronese for Walpole",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Walpole, Horace”及第9、10、14章中的Horace Walpole。第9章称他于1739至1741年在意大利旅行并听闻Sagredo收藏拟出售；"
            "第10章称他讥称Joseph Smith为“威尼斯商人”；第14章称Algarotti曾计划为他购入一幅Veronese作品，原书并未说该计划已实现。"
        ),
        "description_en": (
            "This card represents the index entry “Walpole, Horace” and Horace Walpole in chapters 9, 10, and 14. Chapter 9 says that he heard of the proposed sale of the Sagredo collection while travelling in Italy between 1739 and 1741. Chapter 10 says he jeered at Joseph Smith as the “Merchant of Venice.” Chapter 14 says Algarotti planned to acquire a Veronese for him; the text does not say that the plan was carried out."
        ),
        "identity_extra": "第9章给出全名，索引及第10、14章姓氏提及保持同一跨章人物组；未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-2798 remains the source-local person group new-person:horace-walpole-71c5b539dc. The full name at chapter 9 p.264 and index UVWXYZ.csv#135 anchor chapter 10 p.301 and chapter 14 p.356 references; the latter remains a planned acquisition, not a completed purchase. No exact existing person KU matched; no external identity source was accessed."
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
        label = (
            f"Markdown lines {item['line_start']}–{item['line_end']}"
            if item["line_start"] != item["line_end"]
            else f"Markdown line {item['line_start']}"
        )
        card_sources.append(
            {
                "citation": item.get("citation", BOOK_CITATION),
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [{"source_span": label, "text": source_quote(item)}],
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
    relation_rows = "\n".join(
        f"- [`{sid}`](../../tables/book-statements.jsonl)：S2直接关系候选，待S6审查。"
        for sid in t["relation_ids"]
    )
    return (
        f"---\n{frontmatter}---\n\n## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}\n\n**English:** {t['description_en']}\n\n"
        "## 关系与证据\n\n### 身份与外部链接\n\n"
        f"- S3人物组：候选 `{t['candidate']}`；查看 [alignment.csv](../../tables/alignment.csv) 与[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
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
        assert t["index_quote"].encode("ascii") in (ROOT / t["index_file"]).read_bytes()
        for item in t["sources"]:
            source_quote(item)
        source_quote({"file": t["index_file"], "line_start": t["index_line"], "line_end": t["index_line"], "quote_text": t["index_quote"]})
        for sid in t["relation_ids"]:
            assert sid in statements
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
        if registered:
            assert card_path.read_text(encoding="utf-8-sig") == make_card(t)
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
            cards[card_path] = make_card(t)

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

    process_text = read_text(PROCESS_PATH)
    process_record = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S3→S4 person：Sebastiano Resta、Andrea Palladio 与 Horace Walpole 登记（2026-10-17）\n\n"
        "按索引主项和多章正文/注释全名、称谓及语境复核三个person new组。Resta的第3章p.77全名、第6章p.155身份描述与第5、8章书信引用相合；Palladio的索引全名与第4、10、14章及Postscript中的建筑师语境相合；Walpole由第9章p.264全名连接至第10、14章的姓氏提及，其中1738年购画仍为计划。三组均无现成同类型人物KU；未引入外部身份断言。6条S2直接关系候选留待S6。\n\n"
        "| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
    )
    for t in TARGETS:
        process_record += f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['chapters']} | {len(t['relation_ids'])} |\n"
    process_record += "\n"
    if f'<a id="{ANCHOR}"></a>' in process_text:
        assert all(t["group"] in process_text for t in TARGETS)
    else:
        process_text += process_record
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    result_heading = "### S3→S4 person：Sebastiano Resta、Andrea Palladio 与 Horace Walpole 登记（2026-10-17）"
    if result_heading in result_text:
        assert all(t["ku"] in result_text for t in TARGETS)
    else:
        result_text += "\n\n" + result_heading + "\n\n"
        for t in TARGETS:
            result_text += (
                f"- `{t['candidate']}` / `{t['group']}` → "
                f"[{t['name_zh']}（{t['name_en']}）](../{t['ku']}.md)；{t['chapters']}；"
                f"{len(t['relation_ids'])}条直接关系候选留待S6。\n"
            )
        result_text += "\n本批未新增正式关系或外部身份断言。\n"

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
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(f"APPLIED: groups={newly_registered}; cards={len(cards)}; registered={totals['registered_groups']:,}; pending={totals['pending_groups']:,}")


if __name__ == "__main__":
    main()
