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
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017e"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-1740",
        "group": "new-person:goswin-nickel-8976064042",
        "ku": "units/persons/goswin-nickel",
        "name_zh": "戈斯温·尼克尔",
        "name_en": "Goswin Nickel",
        "index_entry": "N.csv#20",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/N.csv",
        "index_quote": "Nickel, Goswin",
        "body_source": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "source_fragments": ["the Belgian Goswin Nickel", "The General of the Society, Padre Nickel"],
        "sources": [
            {
                "location": "第3章；印刷页78；Markdown L23–24",
                "summary": "Haskell称当时耶稣会总会长为比利时人 Goswin Nickel，并指出当时副会长 Oliva 的影响更突出。",
                "span": "Markdown lines 23–24; print p. 78",
                "quotes": [("lines 23–24", "The General of the\nJesuits at this time was the Belgian Goswin Nickel, but the outstanding personality was already the Vicar, Oliva, and there can be little doubt that it was he who took advantage of the new situation.")],
            },
            {
                "location": "第3章；印刷页91；Markdown L160",
                "summary": "Haskell称 Padre Nickel 曾建议将秘鲁遗产用于罗马 Gesù 教堂小堂装饰，并记述西班牙方面随后散布相关传闻。",
                "span": "Markdown line 160; print p. 91",
                "quotes": [("line 160", "The General of the Society, Padre Nickel, suggested that the money would be better employed in decorating a chapel in the Gesù in Rome. But the Spaniards evidently did not welcome this idea, and soon began to spread rumours that the General wanted the money ‘for his own private use’. Again, the matter was dropped.")],
            },
        ],
        "description_zh": "Haskell称 Goswin Nickel 为比利时耶稣会总会长，并记其曾建议将秘鲁遗产用于装饰罗马 Gesù 教堂的一座小堂。相关建议及西班牙方面的传闻均按书内叙述保留；中文名为项目工作音译。",
        "description_en": "Haskell identifies Goswin Nickel as the Belgian Superior General of the Jesuits and reports his proposal to use a Peruvian legacy to decorate a chapel in the Gesù in Rome. The proposal and the subsequent Spanish rumours are retained as the book's account. The Chinese name is a project working transliteration.",
        "location": "第3章印刷页78、91；Markdown L24、160",
        "relation_ids": [
            "st-chp3-seciv-l152-163-nickel-proposed-redirecting-legacy",
            "st-chp3-seciv-l16-24-courtois-letters-and-test",
            "st-chp3-seciv-l16-24-nickel-oliva-roles",
            "st-chp3-seciv-l16-24-courtois-good-faith-test",
            "st-chp3-seciv-l152-163-spaniards-spread-rumour-about-nickel",
        ],
    },
    {
        "candidate": "cand-1705",
        "group": "new-person:francesco-morosini-b34af6f696",
        "ku": "units/persons/francesco-morosini",
        "name_zh": "弗朗切斯科·莫罗西尼",
        "name_en": "Francesco Morosini",
        "index_entry": "M.csv#246",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "index_quote": "Morosini, Francesco",
        "body_source": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "source_fragments": ["Francesco Morosini in the Peloponnese", "dismissed by Francesco Morosini for incompetence"],
        "sources": [
            {
                "location": "第9章；印刷页246；Markdown L21–22",
                "summary": "Haskell称 Francesco Morosini 于1686年在伯罗奔尼撒的胜利受到热烈庆祝，但成果未能持久。",
                "span": "Markdown lines 21–22; print p. 246",
                "quotes": [("lines 21–22", "The triumphs of\nFrancesco Morosini in the Peloponnese, celebrated with almost hysterical enthusiasm in 1686, were short-lived.")],
            },
            {
                "location": "第9章；印刷页248；Markdown L41",
                "summary": "Haskell称威尼斯总督宫的凯旋拱门由 Gregorio Lazzarini 绘制，以纪念 Morosini 在伯罗奔尼撒的短暂胜利。",
                "span": "Markdown line 41; print p. 248",
                "quotes": [("line 41", "So too are the paintings in the Palazzo Ducale designed to commemorate the actions of great commanders after victorious wars—reaching a climax in the triumphal arch painted by Gregorio Lazzarini, the best known painter of the day, in honour of Francesco Morosini’s short-lived successes in the Peloponnese.")],
            },
            {
                "location": "第9章；印刷页249；Markdown L79",
                "summary": "Haskell称 Antonio Barbaro 因失职被 Francesco Morosini 解职，并转而在威尼斯煽动针对 Morosini 的敌意。",
                "span": "Markdown lines 79–80; print p. 249",
                "quotes": [("line 79", "Antonio Barbaro’s conduct in the war of Candia had been somewhat discreditable, and he had been dismissed by Francesco Morosini for incompetence.")],
            },
        ],
        "description_zh": "Haskell在威尼斯的军事与政治语境中记述 Francesco Morosini 于1686年在伯罗奔尼撒取得的胜利及其纪念活动，并称 Antonio Barbaro 曾被其解职。相关人物关系和战事表述按本书范围保留；中文名为项目工作音译。",
        "description_en": "Haskell discusses Francesco Morosini in the military and political context of Venice, recording his 1686 successes in the Peloponnese and their commemoration, and says Antonio Barbaro was dismissed by him. The events and person relations remain within the book's account. The Chinese name is a project working transliteration.",
        "location": "第9章印刷页246、248–249；Markdown L21–22、41、79–80",
        "relation_ids": [
            "st-chp9-p246-morosini-triumphs",
            "st-chp9-p248-palace-commemorations",
            "st-chp9-p249-barbaro-conduct",
            "st-chp9-p252-daniele-iv-command",
            "st-chp9-p249-barbaro-returned-and-opposed-morosini",
        ],
    },
    {
        "candidate": "cand-0922",
        "group": "new-person:diziani-gaspare-4eb64b5752",
        "ku": "units/persons/gaspare-diziani",
        "name_zh": "加斯帕雷·迪齐亚尼",
        "name_en": "Gaspare Diziani",
        "index_entry": "D.csv#24",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/D.csv",
        "index_quote": "Diziani, Gaspare",
        "body_source": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "source_fragments": ["Gaspare\nDiziani went to Dresden in 1717", "He employed Gaspare Diziani for three years"],
        "sources": [
            {
                "location": "第10章；印刷页278；Markdown L30–31",
                "summary": "Haskell称 Gaspare Diziani 于1717年前往德累斯顿，为 Augustus the Strong 担任三年舞台布景画家。",
                "span": "Markdown lines 30–31; print p. 278",
                "quotes": [("lines 30–31", "Gaspare\nDiziani went to Dresden in 1717 and worked for three years as scene painter for Augustus the Strong.3")],
            },
            {
                "location": "第10章；印刷页294；Markdown L293",
                "summary": "Haskell称 Augustus the Strong 曾雇用 Diziani，主要为剧院与庆典绘制布景。",
                "span": "Markdown line 293; print p. 294",
                "quotes": [("line 293", "He employed Gaspare Diziani for three years almost exclusively on painting scenery for the theatre and the festivals which were his special delight.")],
            },
            {
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
                "location": "第6章；印刷页165；Markdown L40",
                "summary": "Haskell称 Diziani 后来赴罗马，获 Cardinal Ottoboni 接纳，并为其名义教堂的四十小时敬礼仪式制作舞台布景。",
                "span": "Markdown line 40; print p. 165",
                "quotes": [("line 40", "More than thirty years later Ricci’s pupil, Gaspare Diziani, also came to Rome and was at once taken up by the patriotic Cardinal. But he produced nothing more for him than a magnificent stage set for the ceremony of the Forty Hours in Ottoboni’s titular church of S. Lorenzo in Damaso.5")],
            },
        ],
        "description_zh": "Haskell称 Gaspare Diziani 是 Sebastiano Ricci 的学生，1717年赴德累斯顿为 Augustus the Strong 绘制舞台布景；他后来也赴罗马，为 Cardinal Ottoboni 制作四十小时敬礼仪式的舞台布景。相关委托和工作关系按书内语境保留；中文名为项目工作音译。",
        "description_en": "Haskell identifies Gaspare Diziani as a pupil of Sebastiano Ricci, says he went to Dresden in 1717 to paint stage scenery for Augustus the Strong, and later went to Rome to produce a set for the Forty Hours ceremony for Cardinal Ottoboni. The commissions and working relations are retained within the book's context. The Chinese name is a project working transliteration.",
        "location": "第6章印刷页165；第10章印刷页278、294；Markdown L40、30–31、293",
        "relation_ids": [
            "st-chp10-p278-diziani-augustus-scene-painter",
            "st-chp10-p294-diziani-employment",
            "st-chp6-p165-v1-22",
            "st-chp6-p165-v1-23",
            "st-chp6-p165-v1-24",
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
    parser = argparse.ArgumentParser(description="Register three reviewed cross-chapter person endpoint groups in S4.")
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
    anchor = '<a id="s4-person-endpoints-20261017e"></a>'
    assert anchor not in process_text
    process_text += "\n\n" + anchor + "\n\n### S4 person：三组跨章人物端点登记（2026-10-17）\n\n"
    relation_total = sum(len(t["relation_ids"]) for t in TARGETS)
    process_text += f"三个候选均为单成员 person new 身份组，具索引主项及跨章正文锚点；类型与身份边界按现有 S3 决定登记。各组分别登记一张人物 KU。{relation_total} 条直接 S2 关系候选保留待 S6，未新增正式关系。\n\n"
    process_text += "| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |\n|---|---|---|---:|\n"
    for t in TARGETS:
        process_text += f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['location']} 与索引 {t['index_entry']} | {len(t['relation_ids'])} |\n"
    process_text += "\nNickel 与 Morosini 的卡片保留 Haskell 对人物及事件的来源表述，不扩展为外部履历。Diziani 的舞台布景委托候选跨第6、10章对应其人物端点；正式关系仍待 S6。\n"
    result_text += "\n\n### S4 person：Goswin Nickel、Francesco Morosini 与 Gaspare Diziani 登记（2026-10-17）\n\n"
    for t in TARGETS:
        result_text += f"- `{t['candidate']}` → [{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)：{t['location']}；{len(t['relation_ids'])}条直接关系候选待 S6。\n"
    result_text += "\n未新增正式关系或外部身份核验。\n"

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == 439
    assert totals["pending_groups"] == 4374
    assert totals["pending_members"] == 4433

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
