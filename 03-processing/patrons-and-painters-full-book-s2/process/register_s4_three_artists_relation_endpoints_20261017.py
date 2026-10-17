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
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017c"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-1632",
        "group": "new-person:livio-mehus-0c1b46a467",
        "ku": "units/persons/livio-mehus",
        "name_zh": "利维奥·梅胡斯",
        "name_en": "Livio Mehus",
        "index_entry": "M.csv#172",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "index_quote": "Mehus, Livio",
        "body_source": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "source_fragments": ["Yet Livio Mehus they largely ignored", "In 1677 they owned three pictures by him"],
        "sources": [
            {
                "location": "第8章；印刷页213；Markdown L116",
                "summary": "Haskell称德尔罗索兄弟在1677年拥有 Livio Mehus 的三幅画，到十二年后这些作品已不在其藏品中。",
                "span": "Markdown line 116; print p. 213",
                "quotes": [("line 116", "Yet Livio Mehus they largely ignored. In 1677 they owned three pictures by him; twelve years later these had disappeared.")],
            },
            {
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "location": "第8章；印刷页240；Markdown L351",
                "summary": "Haskell称 Mehus 为佛兰德人，称费迪南多收藏其三十件作品，并把他描述为费迪南多随行艺术家中最具威尼斯特征者；关于其去世使其未能直接服务费迪南多的说法属于作者推断。",
                "span": "Markdown line 351; print p. 240",
                "quotes": [("line 351", "the Flemish Livio Mehus, thirty of whose works Ferdinand owned. Such prominence is not surprising, for Mehus was by far the most Venetian of all the artists in his entourage and his tremendous vivacity combined with a slightly troubled eroticism made an obvious appeal to Ferdinand. Only the death of this painter in 1691, before Ferdinand’s patronage had reached its fullest extent, can have prevented him working directly for the Grand Prince who sought to make amends for this neglect by assiduously collecting his canvases and giving support to his son.1")],
            },
        ],
        "description_zh": "Haskell称 Livio Mehus 为佛兰德画家，并记德尔罗索兄弟在1677年拥有其三幅画、十二年后这些作品已不在其藏品中。第8章另称费迪南多收藏其三十件作品，赞赏其艺术特点；“去世使他未能直接为费迪南多工作”是 Haskell 的推断，保留为来源判断。中文名为项目工作音译。",
        "description_en": "Haskell identifies Livio Mehus as a Flemish painter and reports that the del Rosso brothers owned three of his pictures in 1677, which had disappeared from their collection twelve years later. Elsewhere the book says Ferdinand owned thirty of his works and describes qualities that appealed to the prince. The claim that Mehus's death prevented him from working directly for Ferdinand is Haskell's inference and remains attributed to the source. The Chinese name is a project working transliteration.",
        "location": "第8章，印刷页213、240；Markdown L116、351",
        "relation_ids": [
            "st-chp8-p213-mehus-freshness-would-suit-giordano-patrons",
            "st-chp8-p240-mehus-appeal",
            "st-chp8-p213-mehus-ignored-by-brothers",
        ],
    },
    {
        "candidate": "cand-1743",
        "group": "new-person:giuseppe-nogari-a391e671c6",
        "ku": "units/persons/giuseppe-nogari",
        "name_zh": "朱塞佩·诺加里",
        "name_en": "Giuseppe Nogari",
        "index_entry": "N.csv#23",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/N.csv",
        "index_quote": "Nogari, Giuseppe",
        "body_source": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "source_fragments": ["the only other artist well represented in his collection was Giuseppe Nogari", "This painter was famous above all for his ‘teste di fantasia’"],
        "sources": [
            {
                "location": "第10章；印刷页316；Markdown L116–117",
                "summary": "Haskell称 Nogari 以‘teste di fantasia’闻名，即受北方画家、尤其伦勃朗影响的半身想象肖像，通常描绘老人；Schulenburg 收藏其作品并委托其他题材。",
                "span": "Markdown lines 116–117; print p. 316",
                "quotes": [("line 116", "the only other artist well represented in his collection was Giuseppe Nogari. This painter was famous above all for his ‘teste di fantasia’—imaginary half-length portraits, strongly influenced by Northern artists especially Rembrandt, usually of old men and women.")],
            },
            {
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "location": "第9章；印刷页200；Markdown L206",
                "summary": "Haskell记述 Giuseppe Nogari 为 Marco Foscarini 绘制肖像。",
                "span": "Markdown line 206; print p. 200",
                "quotes": [("line 206", "Giuseppe Nogari his portrait.4")],
            },
        ],
        "description_zh": "Haskell称 Giuseppe Nogari 是画家，以受北方画家、尤其伦勃朗影响的‘teste di fantasia’半身想象肖像闻名，并记其为 Marco Foscarini 绘制肖像。书中还记述 Schulenburg 收藏 Nogari 的作品并委托其绘制多件寓意画。以上均为书内记载；中文名为项目工作音译。",
        "description_en": "Haskell identifies Giuseppe Nogari as a painter known for ‘teste di fantasia’, imaginary half-length portraits influenced by Northern artists, especially Rembrandt. The book also reports that he painted a portrait of Marco Foscarini and that Schulenburg collected and commissioned works by him. These statements are recorded as the book's account. The Chinese name is a project working transliteration.",
        "location": "第9章印刷页200；第10章印刷页316；Markdown L204–206、116–117",
        "relation_ids": [
            "st-chp10-p316-nogari-only-other-artist-well-represented",
            "st-chp9-p260-nogari-portrait",
            "st-chp10-p312-nogari-painted-portraits-of",
        ],
    },
    {
        "candidate": "cand-1047",
        "group": "new-person:fontebasso-francesco-76776557de",
        "ku": "units/persons/francesco-fontebasso",
        "name_zh": "弗朗切斯科·丰特巴索",
        "name_en": "Francesco Fontebasso",
        "index_entry": "F.csv#62",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/F.csv",
        "index_quote": "Fontebasso, Francesco",
        "body_source": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "source_fragments": ["He was followed in 1762 by Francesco Fontebasso, a pupil of", "Sebastiano Ricci, who decorated the Winter Palace"],
        "sources": [
            {
                "location": "第10章；印刷页297；Markdown L340–341",
                "summary": "Haskell称 Francesco Fontebasso 于1762年跟随 Rotari 前往圣彼得堡，是 Sebastiano Ricci 的学生，并装饰冬宫。",
                "span": "Markdown lines 340–341; print p. 297",
                "quotes": [("lines 340–341", "He was followed in 1762 by Francesco Fontebasso, a pupil of\nSebastiano Ricci, who decorated the Winter Palace,5")],
            },
            {
                "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
                "location": "第9章；印刷页272；Markdown L54–55",
                "summary": "Haskell称 Fontebasso 为威尼斯 Santa Maria Assunta 天花板绘制壁画，题材包括亚伯拉罕迎接三天使及以利亚升天。",
                "span": "Markdown lines 54–55; print p. 272",
                "quotes": [("lines 54–55", "None of the leading painters left work there,3 and Fontebasso, who frescoed the ceiling, depicted on it The Three Angels visiting Abraham, which had no specific relationship to\nJesuit iconography, and Elijah carried to Heaven in a Chariot of Fire, a subject hitherto associated almost exclusively with the Carmelites.4")],
            },
            {
                "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "location": "第13章；印刷页339；Markdown L75–76",
                "summary": "Haskell称 Fontebasso 与 Gaetano Zompini 是为 Zatta 的插图本工作、处理但未能充分诠释中世纪图像的两位艺术家。",
                "span": "Markdown lines 75–76; print p. 339",
                "quotes": [("lines 75–76", "The strain of coping with mediaeval iconography proved a difficult one for the two artists who especially worked for him, Francesco\nFontebasso and Gaetano Zompini, and the results, though often engaging, hardly contribute much to an interpretation of the poem.")],
            },
        ],
        "description_zh": "Haskell称 Francesco Fontebasso 是 Sebastiano Ricci 的学生，记其于1762年赴圣彼得堡并装饰冬宫；他也为威尼斯 Santa Maria Assunta 教堂绘制天花板壁画，并与 Gaetano Zompini 为 Zatta 的《但丁》插图本工作。上述活动及评价限于本书所述范围。中文名为项目工作音译。",
        "description_en": "Haskell identifies Francesco Fontebasso as a pupil of Sebastiano Ricci and says that he went to St Petersburg in 1762 and decorated the Winter Palace. The book also attributes ceiling frescoes at Santa Maria Assunta in Venice to him and says he worked with Gaetano Zompini on Zatta's illustrated Dante edition. The activities and assessment remain limited to the book's account. The Chinese name is a project working transliteration.",
        "location": "第9章印刷页272；第10章印刷页297；第13章印刷页339；Markdown L54–55、340–341、75–76",
        "relation_ids": [
            "st-chp10-p297-fontebasso-winter-palace",
            "st-chp13-p339-dante-medieval-iconography-difficult-for-artists",
            "st-chp9-p272-fontebasso-elijah",
            "st-chp9-p272-fontebasso-three-angels",
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
    parser = argparse.ArgumentParser(description="Register three reviewed source-local artist person groups in S4.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
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
    anchor = '<a id="s4-person-endpoints-20261017c"></a>'
    assert anchor not in process_text
    process_text += "\n\n" + anchor + "\n\n### S4 person：三位画家直接关系端点登记（2026-10-17）\n\n"
    process_text += "三个候选均为单成员 person new 身份组，正文与索引可互相定位，现各登记一张 KU。卡片仅记录来源支持的身份和语境；直接 S2 关系候选保留待 S6，没有新增正式关系。\n\n"
    process_text += "| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |\n|---|---|---|---:|\n"
    for t in TARGETS:
        process_text += f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['location']} 与索引 {t['index_entry']} | {len(t['relation_ids'])} |\n"
    process_text += "\nMehus 关于其去世可能使其未能直接为费迪南多工作的说法保留为 Haskell 的推断；Nogari 与 Foscarini、Schulenburg 的肖像／委托表述，以及 Fontebasso 的作品与工作关系仍按 S2 候选待 S6 审查。中文名均注明为项目工作音译。\n"
    result_text += "\n\n### S4 person：Livio Mehus、Giuseppe Nogari 与 Francesco Fontebasso 登记（2026-10-17）\n\n"
    for t in TARGETS:
        result_text += f"- `{t['candidate']}` → [{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)：{t['location']}；{len(t['relation_ids'])}条直接关系候选待 S6。\n"
    result_text += "\n未新增正式关系或外部身份核验。\n"

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == 433
    assert totals["pending_groups"] == 4380
    assert totals["pending_members"] == 4439

    if args.dry_run:
        print(f"DRY-RUN OK: groups={len(TARGETS)}; cards={len(cards)}; direct relation candidates={sum(len(t['relation_ids']) for t in TARGETS)}")
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
