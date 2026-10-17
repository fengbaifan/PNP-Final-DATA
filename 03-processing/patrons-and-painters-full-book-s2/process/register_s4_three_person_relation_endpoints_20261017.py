from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
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
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017b"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-0788",
        "group": "new-person:august-clemens-cologne-elector-of-a0fd03e59b",
        "ku": "units/persons/clemens-august-elector-cologne",
        "name_zh": "克莱门斯·奥古斯特",
        "name_en": "Clemens August, Archbishop-Elector of Cologne",
        "index_entry": "C.csv#312",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/C.csv",
        "index_quote": "Clemens August, Archbishop-Elector of Cologne",
        "body_source": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "source_fragments": ["Thus Clemens August, Archbishop-Elector of Cologne", "owned pastels by her", "Soon after 1730 he began commissioning altar paintings"],
        "sources": [
            {
                "location": "第10章；印刷页295；OCR L316",
                "summary": "Haskell称 Clemens August 为科隆大主教选侯，记他曾雇用 Amigoni 并常访威尼斯；兄长身份按原文保留为 S2 候选。",
                "span": "line 316; print p. 295",
                "quotes": [("line 316", "Thus Clemens August, Archbishop-Elector of Cologne and younger brother of the Elector of Bavaria, who had employed Amigoni, was also a frequent visitor to Venice.")],
            },
            {
                "location": "第10章；印刷页296；OCR L319",
                "summary": "Haskell称 Clemens August 是 Rosalba Carriera 的仰慕者并拥有她的粉彩画；又记他约1730年后开始为其庇护的多所教堂委托祭坛画。",
                "span": "line 319; print p. 296",
                "quotes": [("line 319", "admirer of Rosalba and owned pastels by her."), ("line 319", "Soon after 1730 he began commissioning altar paintings for the many churches under his patronage by Pittoni, Piazzetta")],
            },
        ],
        "description_zh": "Haskell称 Clemens August 为科隆大主教选侯，记他曾雇用 Amigoni、常访威尼斯、拥有 Rosalba Carriera 的粉彩画，并于约1730年后为其庇护的多所教堂委托祭坛画。亲属、作品和委托陈述保留原书范围与限定；中文名为项目工作音译。",
        "description_en": "Haskell identifies Clemens August as Archbishop-Elector of Cologne and says that he employed Amigoni, frequently visited Venice, owned pastels by Rosalba Carriera, and began commissioning altar paintings for churches under his patronage soon after 1730. The family, work, and commission statements remain within the scope and qualifications of the book. The Chinese name is a project working transliteration.",
        "location": "第10章，印刷页295–296；OCR L316、319",
        "relation_ids": [
            "st-chp10-p295-clemens-sibling",
            "st-chp10-p295-clemens-title",
            "st-chp10-p295-clemens-venice-visits",
            "st-chp10-p296-clemens-altar-commissions",
            "st-chp10-p296-clemens-carriera-pastels",
        ],
    },
    {
        "candidate": "cand-1001",
        "group": "new-person:daniele-farsetti-fe28988990",
        "ku": "units/persons/daniele-farsetti",
        "name_zh": "达尼埃莱·法尔塞蒂",
        "name_en": "Daniele Farsetti",
        "index_entry": "F.csv#16",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/F.csv",
        "index_quote": "Farsetti, Daniele",
        "body_source": "02-sources/02-Markdown/15_CHP-15_sec_i.md",
        "source_fragments": ["His cousin Daniele (17251787), himself an amateur painter", "inherited the collection and even increased it"],
        "sources": [
            {
                "location": "第15章；印刷页363；OCR L35",
                "summary": "Haskell称 Daniele Farsetti 是 Filippo Farsetti 的表亲和业余画家，曾在 S. Rocco 展览展出部分粉彩画，并继承、扩充其收藏。",
                "span": "line 35; print p. 363",
                "quotes": [("line 35", "His cousin Daniele (17251787), himself an amateur painter who once showed some of his pastels at the exhibitionof S. Rocco, inherited the collection and even increased it")],
            }
        ],
        "description_zh": "Haskell称 Daniele Farsetti 是 Filippo Farsetti 的表亲和业余画家，曾在 S. Rocco 展览展出部分粉彩画，后来继承并扩充 Filippo 的收藏。相关亲缘、收藏与赞助陈述均按原书记载保留；中文名为项目工作音译。",
        "description_en": "Haskell describes Daniele Farsetti as Filippo Farsetti's cousin and an amateur painter. He once showed some of his pastels at the S. Rocco exhibition and later inherited and increased Filippo's collection. The family, collection, and patronage statements are retained as the book reports them. The Chinese name is a project working transliteration.",
        "location": "第15章，印刷页363；OCR L35",
        "relation_ids": [
            "st-chp15-p363-daniele-cousin-amateur-painter",
            "st-chp15-p363-daniele-showed-pastels-at-s-rocco",
            "st-chp15-p363-daniele-inherited-increased-collection",
            "st-chp15-p363-daniele-continued-patronage-partial",
            "st-chp15-p364-tommaso-brother-of-daniele",
        ],
    },
    {
        "candidate": "cand-2686",
        "group": "new-person:giuseppe-valletta-5ab1f14845",
        "ku": "units/persons/giuseppe-valletta",
        "name_zh": "朱塞佩·瓦莱塔",
        "name_en": "Giuseppe Valletta",
        "index_entry": "UVWXYZ.csv#22",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "index_quote": "Valletta, Giuseppe",
        "body_source": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "source_fragments": ["Giuseppe\nValletta, poet and arbiter of taste", "Valletta used to help Luca Giordano with his problems of iconography"],
        "sources": [
            {
                "location": "第8章；印刷页204；OCR L17–18",
                "summary": "Haskell称 Giuseppe Valletta 是那不勒斯诗人、品味裁断者及 Luca Giordano 与 Francesco Solimena 的赞助人。",
                "span": "lines 17–18; print p. 204",
                "quotes": [("lines 17–18", "Above all there was Giuseppe\nValletta, poet and arbiter of taste, friend of Shaftesbury and the patron of Luca Giordano and Solimena.")],
            },
            {
                "location": "第8章；印刷页204；OCR L129（注3）",
                "summary": "第3注转引 De Dominici 等资料，称 Valletta 曾帮助 Luca Giordano 处理图像学问题，并购入一批建筑画；引注原文未独立查阅。",
                "span": "line 129; print p. 204, note 3",
                "quotes": [("line 129", "Valletta used to help Luca Giordano with his problems of iconography (de Dominici, IV, p. 196)")],
            },
        ],
        "description_zh": "Haskell称 Giuseppe Valletta 是那不勒斯诗人和品味裁断者，也是 Luca Giordano 与 Francesco Solimena 的赞助人。注释转述其曾帮助 Giordano 处理图像学问题；相关二手引注未独立查阅。中文名为项目工作音译。",
        "description_en": "Haskell describes Giuseppe Valletta as a Neapolitan poet and arbiter of taste, and as a patron of Luca Giordano and Francesco Solimena. A footnote reports that he used to help Giordano with iconographic problems; the cited secondary references were not independently consulted. The Chinese name is a project working transliteration.",
        "location": "第8章，印刷页204；OCR L17–18、129（注3）",
        "relation_ids": [
            "st-chp8-p204-valletta-bought-codazzi-paintings",
            "st-chp8-p204-valletta-friend-of-shaftesbury",
            "st-chp8-p204-valletta-helps-giordano-iconography",
            "st-chp8-p204-valletta-patron-of-giordano",
            "st-chp8-p204-valletta-patron-of-solimena",
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
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["body_source"], "source_span": item["span"]},
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
    body = f"""## 内容

### 描述

**中文：** {t['description_zh']}〔[{t['location']}](../../../{t['body_source']})〕

**English:** {t['description_en']} ([{t['location']}](../../../{t['body_source']}))

## 关系与证据

### 关系记录

目前没有登记在 `relations.csv` 中的正式关系。直接 S2 关系候选共 5 条（{rels}），保留待 S6 审查；本卡登记不等于关系裁决。"""
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
    parser = argparse.ArgumentParser(description="Register three reviewed source-local person endpoint groups in S4.")
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
        __import__("json").loads(line)
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
        index_bytes = (ROOT / t["index_file"]).read_bytes()
        try:
            index_text = index_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            index_text = index_bytes.decode("cp1252")
        assert t["index_quote"] in index_text, f"index name missing: {t['index_entry']}"
        assert len(t["relation_ids"]) == 5
        for sid in t["relation_ids"]:
            assert sid in statements and statements[sid].get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statements[sid].get("subject_candidate_id"), statements[sid].get("object_candidate_id"))
        card_path = ROOT / f"04-knowledge/{ku}.md"
        cards[card_path] = make_card(t)
        a["ku_id"] = ku
        a["process_ref"] = PROCESS_REF
        a["resolution_note"] += f" S4 registration ({DATE}): mapped {group} to {ku}; bilingual card preserves only book-supported identity and context. Five direct relation candidates remain pending S6."
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
    anchor = '<a id="s4-person-endpoints-20261017b"></a>'
    assert anchor not in process_text
    process_text += "\n\n" + anchor + "\n\n### S4 person：三个直接关系端点身份组登记（2026-10-17）\n\n"
    process_text += "三个候选均为独立的单成员 person new 组，现各登记一张 KU。卡片的名称和描述均以索引、正文或注释为据；不补外部传记信息。每组的5条 S2 关系候选保留待 S6，未写入正式关系。\n\n"
    process_text += "| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |\n|---|---|---|---:|\n"
    for t in TARGETS:
        process_text += f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['location']} 与索引 {t['index_entry']} | 5 |\n"
    process_text += "\nDaniele Farsetti 的 p.363 OCR 日期连写及 “exhibitionof” 转录保留在原始摘录中，本卡描述不依赖日期校正。Clemens August 的“younger brother”及 Valletta 的 patronage／friendship 陈述仅保留为 S2 候选；不由卡片登记代替关系审查。\n"
    result_text += "\n\n### S4 person：Clemens August、Daniele Farsetti 与 Giuseppe Valletta 登记（2026-10-17）\n\n"
    for t in TARGETS:
        result_text += f"- `{t['candidate']}` → [{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)：{t['location']}；5条直接关系候选待 S6。\n"
    result_text += "\n未新增正式关系或外部身份核验。\n"

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == 430
    assert totals["pending_groups"] == 4383
    assert totals["pending_members"] == 4442

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
