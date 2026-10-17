from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = "S4-full-book-2026-10-17"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017f"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-2035",
        "group": "new-person:antonio-carlo-dal-pozzo-7658578989",
        "ku": "units/persons/carlo-antonio-dal-pozzo",
        "name_zh": "卡洛·安东尼奥·达尔·波佐",
        "name_en": "Carlo Antonio dal Pozzo",
        "index_entry": "P.csv#238",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
        "index_quote": "Pozzo, Carlo Antonio dal",
        "body_source": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "source_fragments": ["younger brother Carlo Antonio", "special interest to Cassiano’s brother, Carlo Antonio"],
        "sources": [
            {
                "location": "第4章；印刷页100；Markdown L21",
                "summary": "Haskell称 Carlo Antonio 是 Cassiano 的弟弟，具有科学与艺术兴趣，其赞助活动可能与兄长同样重要。",
                "span": "Markdown line 21; print p. 100",
                "quotes": [("line 21", "He shared it with his younger brother Carlo Antonio and his sister-in-law Teodora. Carlo Antonio too had considerable scientific and artistic interests and there is some evidence to suggest that his patronage was almost as significant as that of Cassiano—but as often happens in such cases it is the elder brother and head of the family who has been given all the credit.")],
            },
            {
                "location": "第4章；印刷页104；Markdown L63",
                "summary": "Haskell称 Cassiano 的弟弟 Carlo Antonio 对 Poussin 绘制的鸟类大画特别感兴趣。",
                "span": "Markdown line 63; print p. 104",
                "quotes": [("line 63", "He also painted large pictures—often life-size—of birds (eagles, ostriches and others) which were of special interest to Cassiano’s brother, Carlo Antonio.3")],
            },
            {
                "location": "第4章；印刷页113；Markdown L162",
                "summary": "Haskell记 Cassiano 于1657年去世，弟弟 Carlo Antonio 比他多活三十余年。",
                "span": "Markdown line 162; print p. 113",
                "quotes": [("line 162", "In 1657 he died, survived for more than thirty years by his brother Carlo Antonio.")],
            },
            {
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "location": "后记第4章；印刷页400；Markdown L55",
                "summary": "Haskell称 Carlo Antonio 为 Cassiano 的弟弟和继承人，并称其本人也是重要收藏家与赞助人。",
                "span": "Markdown line 55; print p. 400",
                "quotes": [("line 55", "Cassiano’s brother and heir Carlo Antonio (himself a notable collector and patron)")],
            },
        ],
        "description_zh": "Haskell称 Carlo Antonio dal Pozzo 是 Cassiano dal Pozzo 的弟弟，具有科学和艺术兴趣，其赞助活动可能与 Cassiano 同样重要；后记称他为 Cassiano 的继承人及收藏家、赞助人。来源还记其对 Poussin 鸟类画的兴趣。亲缘及相关作品关系留待 S6 审查；中文名为项目工作音译。",
        "description_en": "Haskell identifies Carlo Antonio dal Pozzo as Cassiano dal Pozzo's younger brother, with scientific and artistic interests and patronage that may have been nearly as significant as Cassiano's. The postscript calls him Cassiano's heir as well as a notable collector and patron. The book also notes his interest in Poussin's bird paintings. Family and work relations await S6 review. The Chinese name is a project working transliteration.",
        "location": "第4章印刷页100、104、113；后记印刷页400；Markdown L21、63、162；后记L55",
        "relation_ids": [
            "st-chp4-sec-ii-l15-22-shared-home",
            "st-chp4-sec-ii-l53-63-carlo-antonio-interested-in-poussin-bird-pictures",
            "st-chp4-sec-ii-p104-footnote3-olina-notes-carlo-antonio-interest",
            "st-chp4-sec-ii-p113-carlo-antonio-survival",
            "st-chp4-sec-ii-p113-carlo-antonio-brother-of-cassiano",
        ],
    },
    {
        "candidate": "cand-1896",
        "group": "new-person:iv-of-philip-spain-12d022dbb2",
        "ku": "units/persons/philip-iv-spain",
        "name_zh": "西班牙国王腓力四世",
        "name_en": "Philip IV of Spain",
        "index_entry": "P.csv#97",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
        "index_quote": "Philip IV of Spain",
        "body_source": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "source_fragments": ["King Philip IV"],
        "sources": [
            {
                "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "location": "第4章；印刷页116；Markdown L199–200",
                "summary": "Haskell称西班牙大使的阴谋导致 Philip IV 拒绝在宫廷接见 Massimi，理由是 Massimi 对法国人过于友好。",
                "span": "Markdown lines 199–200; print p. 116",
                "quotes": [("lines 199–200", "Intrigues by the Spanish ambassador in Rome led to\nPhilip IV refusing to receive him at court on the grounds that he was too friendly with the French.")],
            },
            {
                "location": "第7章；印刷页172；Markdown L32–35",
                "summary": "Haskell称 King Philip IV 持续关注罗马艺术，并记其代理人约在1636年为 Buen Retiro 宫谈判订制一组大型风景画。",
                "span": "Markdown lines 32–35; print p. 172",
                "quotes": [("lines 32–35", "During all this time King Philip IV, whose appetite for painting was by no means satiated by the employment of Rubens and Velasquez, remained deeply interested in the\nRoman scene. In 1628 his ambassador commissioned one of Guido Reni’s largest, most splendid and romantic compositions, The Abduction of Helen, to be followed three years later by an even finer pendant of The Death of Dido from Guercino in Bologna; but owing to some diplomatic confusion neither picture was sent to Madrid.3 Then, in about 1636, an agent of the King negotiated an ambitious commission for a set of more than a dozen large landscape paintings each of which was to include the figure of some hermit or anchorite.4 These were designed to decorate the palace of Buen Retiro which was being built at this very time on the site of a monastery of Jeronymites.")],
            },
        ],
        "description_zh": "Haskell称 Philip IV of Spain 持续关注罗马艺术，并记其代理人曾为 Buen Retiro 宫谈判一组大型风景画委托；第4章另记他拒绝在宫廷接见 Camillo Massimi。相关宫廷与艺术赞助表述按本书限定保留；中文名为项目工作译名。",
        "description_en": "Haskell says Philip IV of Spain remained interested in the Roman art scene and records an agent negotiating a series of large landscape commissions for the Buen Retiro palace. Chapter 4 also reports that he refused to receive Camillo Massimi at court. The court and patronage statements retain the book's scope and qualifications. The Chinese name is a project working rendering.",
        "location": "第4章印刷页116；第7章印刷页172；Markdown L199–200、32–35",
        "relation_ids": [
            "st-chp4-sec-ii-p116-court-refusal",
            "st-chp4-sec-ii-p116-ambassador-intrigue-caused-refusal",
            "st-chp7-p172-i01",
            "st-chp7-p172-i07",
            "st-chp7-p172-i12",
        ],
    },
    {
        "candidate": "cand-0928",
        "group": "new-person:daniele-dolfin-iv-16ea57c49e",
        "ku": "units/persons/daniele-dolfin-iv",
        "name_zh": "丹尼埃莱·多尔芬四世",
        "name_en": "Daniele IV Dolfin",
        "index_entry": "D.csv#30",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/D.csv",
        "index_quote": "Dolfin, Daniele IV",
        "body_source": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "source_fragments": ["His brother, Daniele IV, who died in the same year", "Dionisio, younger brother of the two Danieles"],
        "sources": [
            {
                "location": "第9章；印刷页252；Markdown L119–122",
                "summary": "Haskell称 Daniele IV 与 Daniele III 是兄弟，二人均于1729年去世；Daniele IV 是土耳其战争中的指挥官，曾在伯罗奔尼撒及1715年作战。",
                "span": "Markdown lines 119–122; print p. 252",
                "quotes": [("line 119", "His brother, Daniele IV, who died in the same year, was one of the most heroic commanders in the Turkish wars, both under Morosini in the Peloponnese and again in 1715.6"), ("lines 120–122", "The Dolfin also enjoyed 2 virtual monopoly of the patriarchate of Aquileia.6 In 1698\nDionisio, younger brother of the two Danieles, was given the post and went to live in\nUdine, the seat of the bishopric.")],
            },
        ],
        "description_zh": "Haskell称 Daniele IV Dolfin 是 Daniele III 的兄弟，二人于1729年同年去世；Daniele IV 曾在土耳其战争中担任指挥官，并参加伯罗奔尼撒及1715年的战事。来源对兄弟关系及军职的记载留待 S6 审查；中文名为项目工作音译。",
        "description_en": "Haskell identifies Daniele IV Dolfin as the brother of Daniele III; both died in 1729. He describes Daniele IV as a commander in the Turkish wars, serving in the Peloponnese and again in 1715. The source's family and military role statements await S6 review. The Chinese name is a project working transliteration.",
        "location": "第9章印刷页252；Markdown L119–122",
        "relation_ids": [
            "st-chp9-p252-daniele-iv-brother-of-iii",
            "st-chp9-p252-daniele-iv-command",
            "st-chp9-p252-dionisio-younger-brother-of-iv",
            "st-chp9-p252-daniele-iv-1715-service",
        ],
    },
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def keep_bom_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def make_card(t: dict) -> str:
    sources = []
    for item in t["sources"]:
        sources.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": span, "text": quote} for span, quote in item["quotes"]],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": item.get("source_file", t["body_source"]), "source_span": item["span"]},
        })
    sources.append({
        "citation": INDEX_CITATION,
        "location": f"全书索引 {t['index_entry']}",
        "sentence_summary": f"索引以 {t['index_quote']} 列出人物主项。",
        "original_quotes": [{"source_span": t["index_entry"], "text": t["index_quote"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["index_file"], "source_span": t["index_entry"]},
    })
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
    rels = ", ".join(t["relation_ids"])
    count = len(t["relation_ids"])
    body = f"""## 内容

### 描述

**中文：** {t['description_zh']}〔[{t['location']}](../../../{t['body_source']})〕

**English:** {t['description_en']} ([{t['location']}](../../../{t['body_source']}))

## 关系与证据

### 关系记录

目前没有登记在 `relations.csv` 中的正式关系。直接 S2 关系候选共 {count} 条（{rels}），保留待 S6 审查；本卡登记不等于关系裁决。"""
    return f"---\n{fm}---\n\n{body}\n"


def insert_accepted(lines: list[str], card_rel: str) -> list[str]:
    entry = f"- {card_rel}"
    assert entry not in lines
    units_idx = lines.index("units:")
    claims_idx = next((i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])), len(lines))
    insert_at = claims_idx
    for i in range(units_idx + 1, claims_idx):
        if lines[i].startswith("- ") and lines[i][2:] > card_rel:
            insert_at = i
            break
    lines.insert(insert_at, entry)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Register three reviewed person groups in S4.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    align_by = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    candidate_by = {r["candidate_id"]: r for r in candidates}
    manifest_by = {r["ku_id"]: r for r in manifest}
    statement_data = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statements = {d["statement_id"]: d for d in statement_data}

    planned_alignments = [dict(r) for r in alignments]
    planned_align_by = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    planned_manifest = [dict(r) for r in manifest]
    accepted_lines = read_text(ACCEPTED_PATH).splitlines()
    cards: dict[Path, str] = {}

    for t in TARGETS:
        cid, group, ku = t["candidate"], t["group"], t["ku"]
        assert cid in candidate_by and cid in align_by
        c, a = candidate_by[cid], planned_align_by[cid]
        assert c["suggested_type"] == "person"
        assert a["decision"] == "new" and not a.get("ku_id")
        assert sync.get_group(a.get("resolution_note", "")) == group
        group_members = [r["candidate_id"] for r in alignments if r.get("candidate_id") and r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == group]
        assert group_members == [cid], f"unexpected group members for {group}: {group_members}"
        assert ku not in manifest_by
        assert not (ROOT / f"04-knowledge/{ku}.md").exists()
        assert f"- 04-knowledge/{ku}.md" not in accepted_lines
        assert not any(r.get("name_en", "").casefold() == t["name_en"].casefold() for r in manifest if r["type"] == "person"), f"same-name person KU already exists: {t['name_en']}"
        source_text = (ROOT / t["body_source"]).read_text(encoding="utf-8-sig")
        for fragment in t["source_fragments"]:
            assert fragment in source_text, f"source fragment missing for {cid}: {fragment}"
        for item in t["sources"]:
            item_text = (ROOT / item.get("source_file", t["body_source"])).read_text(encoding="utf-8-sig")
            for _, quote in item["quotes"]:
                assert quote in item_text, f"source quote missing for {cid}: {item['location']}"
        index_text = (ROOT / t["index_file"]).read_text(encoding="utf-8-sig")
        assert t["index_quote"] in index_text, f"index name missing: {t['index_entry']}"
        for sid in t["relation_ids"]:
            assert sid in statements and statements[sid].get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statements[sid].get("subject_candidate_id"), statements[sid].get("object_candidate_id"))
        card_path = ROOT / f"04-knowledge/{ku}.md"
        cards[card_path] = make_card(t)
        a["ku_id"] = ku
        a["process_ref"] = PROCESS_REF
        count = len(t["relation_ids"])
        a["resolution_note"] += f" S4 registration ({DATE}): mapped {group} to {ku}; bilingual card preserves source-supported identity and context. {count} direct relation candidates remain pending S6."
        planned_manifest.append({
            "ku_id": ku,
            "type": "person",
            "canonical_name": f"{t['name_zh']}（{t['name_en']}）",
            "name_en": t["name_en"],
            "source_task": TASK,
            "card_path": f"04-knowledge/{ku}.md",
        })

    planned_manifest.sort(key=lambda r: r["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")
    stats = sync.summarize_by_type(candidate_by.values(), planned_alignments)
    _, totals = sync.build_type_table(stats)
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    process_text = read_text(PROCESS_PATH)
    anchor = '<a id="s4-person-endpoints-20261017f"></a>'
    assert anchor not in process_text
    process_text += "\n\n" + anchor + "\n\n### S4 person：三组人物直接关系端点登记（2026-10-17）\n\n"
    relation_total = sum(len(t["relation_ids"]) for t in TARGETS)
    process_text += f"三个候选均为单成员 person new 身份组，索引主项与正文提供交叉身份锚点，现分别登记一张人物 KU。{relation_total} 条直接 S2 关系候选保留待 S6；没有新增正式关系。\n\n"
    process_text += "| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |\n|---|---|---|---:|\n"
    for t in TARGETS:
        process_text += f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['location']} 与索引 {t['index_entry']} | {len(t['relation_ids'])} |\n"
    process_text += "\nCarlo Antonio dal Pozzo 与 Cassiano dal Pozzo 是兄弟，分别映射各自人物卡；Philip IV 按跨章索引人物主项登记；Daniele IV Dolfin 与已登记的 Daniele III Dolfin 区分。以上边仍待 S6 审查。\n"
    result_text += "\n\n### S4 person：Carlo Antonio dal Pozzo、Philip IV 与 Daniele IV Dolfin 登记（2026-10-17）\n\n"
    for t in TARGETS:
        result_text += f"- `{t['candidate']}` → [{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)：{t['location']}；{len(t['relation_ids'])}条直接关系候选待 S6。\n"
    result_text += "\n未新增正式关系或外部身份核验。\n"

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == 442
    assert totals["pending_groups"] == 4371
    assert totals["pending_members"] == 4430

    if args.dry_run:
        print(f"DRY-RUN OK: groups={len(TARGETS)}; cards={len(cards)}; direct relation candidates={relation_total}")
        print(f"manifest: {len(manifest):,}->{len(planned_manifest):,}; registered groups={totals['registered_groups']:,}; pending groups={totals['pending_groups']:,}; pending candidate mappings={totals['pending_members']:,}")
        return

    for path, card in cards.items():
        path.write_bytes(card.encode("utf-8"))
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(f"APPLIED: groups={len(TARGETS)}; new person KUs={len(cards)}; manifest={len(planned_manifest):,}; pending groups={totals['pending_groups']:,}")


if __name__ == "__main__":
    main()
