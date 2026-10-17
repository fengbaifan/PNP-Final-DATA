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
ANCHOR = "s4-crosschapter-person-endpoints-mazza-goya-mattielli-20261017"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-1602",
        "group": "new-person:giuseppe-mazza-c434d5ebb3",
        "ku": "units/persons/giuseppe-mazza",
        "name_zh": "朱塞佩·马扎",
        "name_en": "Giuseppe Mazza",
        "index_entry": "M.csv#141",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "index_line": 143,
        "index_quote": "Mazza, Giuseppe",
        "index_span": "M.csv#141; CSV line 143; pp. 222, 251",
        "chapters": "第8、9章；索引 M.csv#141",
        "relation_ids": [
            "st-chp8-p222-ferrerio-pupil",
            "st-chp8-p227-mazza-created-busts",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "line_start": 127,
                "line_end": 127,
                "location": "第8章，印刷页222，Markdown L127",
                "span": "Markdown line 127; print p. 222",
                "summary": "Haskell称一位雕塑家是博洛尼亚人Giuseppe Mazza的学生。",
                "quote_text": "the Bolognese Giuseppe Mazza",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "line_start": 200,
                "line_end": 200,
                "location": "第8章，印刷页227，Markdown L200",
                "span": "Markdown line 200; print p. 227",
                "summary": "Haskell称画廊由Mazza创作的Diana与Endymion半身像补足。",
                "quote_text": "Busts of Diana and Endymion by the Bolognese Giuseppe Mazza",
            },
            {
                "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "line_start": 110,
                "line_end": 111,
                "location": "第9章，印刷页251，Markdown L110–111",
                "span": "Markdown lines 110–111; print p. 251",
                "summary": "Haskell提到Manin家族宫殿中的一尊由Giuseppe Mazza制作的大理石维纳斯像。",
                "quote_text": "a marble\nVenus by Giuseppe Mazza",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Giuseppe Mazza”及第8、9章中的博洛尼亚雕塑家Giuseppe Mazza。第8章称有雕塑家是他的学生，并将Diana与Endymion半身像归于他；"
            "第9章提及Manin家族宫殿中的一尊大理石维纳斯像。作品归属与师生关系仍分别作为书内断言候选留待S6审查。"
        ),
        "description_en": (
            "This card represents the index entry “Giuseppe Mazza” and the Bolognese sculptor Giuseppe Mazza in chapters 8 and 9. Chapter 8 calls a sculptor his pupil and attributes busts of Diana and Endymion to him. Chapter 9 mentions a marble Venus in a Manin family palace. The pupil and work attributions remain separate book statements awaiting S6 review."
        ),
        "identity_extra": "第8章全名与索引页222、251及第9章全名提及相合；未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-1602 remains the person group new-person:giuseppe-mazza-c434d5ebb3. Full-name references at chapter 8 pp.222/227 and chapter 9 p.251 align with index M.csv#141; no exact existing person KU matched. No external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-1216",
        "group": "new-person:francisco-goya-8314253007",
        "ku": "units/persons/francisco-goya",
        "name_zh": "弗朗西斯科·戈雅",
        "name_en": "Francisco Goya",
        "index_entry": "G.csv#124",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/G.csv",
        "index_line": 126,
        "index_quote": "Goya, Francisco",
        "index_span": "G.csv#124; CSV line 126; pp. 192, 297n",
        "chapters": "第7、10章；索引 G.csv#124",
        "relation_ids": [
            "st-chp7-p192-i19",
            "st-chp10-p297-note3-giaquinto-influence-on-young-goya",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "line_start": 289,
                "line_end": 289,
                "location": "第7章，印刷页192，Markdown L289",
                "span": "Markdown line 289; print p. 192",
                "summary": "Haskell称Luca Giordano对年轻Goya的影响后来产生了积极作用。",
                "quote_text": "his influence, though at the time it may have proved enfeebling for some already feeble local painters, was much later absorbed with profit by the young Goya",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 572,
                "line_end": 572,
                "location": "第10章注释，印刷页297注3，Markdown L572",
                "span": "Markdown line 572; print p. 297n3",
                "summary": "Haskell称Corrado Giaquinto对年轻Goya的影响大于其他意大利画家。",
                "quote_text": "whose influence on the young Goya was far greater than that of any other Italian painter",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Goya, Francisco”及第7、10章所称“young Goya”。第7章称Luca Giordano的影响后来为Goya所吸收；"
            "第10章注释称Corrado Giaquinto对年轻Goya的影响超过其他意大利画家。这里只记录原书的比较与影响判断，不作外部艺术史验证。"
        ),
        "description_en": (
            "This card represents the index entry “Goya, Francisco” and “the young Goya” in chapters 7 and 10. Chapter 7 says Luca Giordano’s influence was later absorbed by Goya. A chapter 10 note says Corrado Giaquinto’s influence on the young Goya was greater than that of any other Italian painter. These comparisons and influence claims are recorded as Haskell’s statements, without external art-historical verification."
        ),
        "identity_extra": "索引给出Francisco全名，第7、10章的“young Goya”语境及页码范围相合；未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-1216 remains the person group new-person:francisco-goya-8314253007. Index G.csv#124 supplies the full form Francisco Goya and pp.192/297n; chapter 7 p.192 and chapter 10 n.3 both refer to the young Goya in painter-influence contexts. No exact existing person KU matched; no external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-1584",
        "group": "new-person:lorenzo-mattielli-e53f3c6116",
        "ku": "units/persons/lorenzo-mattielli",
        "name_zh": "洛伦佐·马泰利",
        "name_en": "Lorenzo Mattielli",
        "index_entry": "M.csv#123",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "index_line": 125,
        "index_quote": "Mattielli, Lorenzo",
        "index_span": "M.csv#123; CSV line 125; pp. 201, 353",
        "chapters": "第7、14章；索引 M.csv#123",
        "relation_ids": [
            "st-chp7-p201-v-mattielli-aristocratic-gardens",
            "st-chp7-p201-v-mattielli-parodi-statues",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
                "line_start": 50,
                "line_end": 50,
                "location": "第7章，印刷页201，Markdown L50",
                "span": "Markdown line 50; print p. 201",
                "summary": "Haskell称Lorenzo Mattielli与Domenico Antonio Parodi为Prince Eugene大厅和花园制作雕像。",
                "quote_text": "Lorenzo Mattielli and Domenico Antonio Parodi made statues for the hall and gardens",
            },
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "line_start": 70,
                "line_end": 71,
                "location": "第14章，印刷页353，Markdown L70–71",
                "span": "Markdown lines 70–71; print p. 353",
                "summary": "Haskell提到布吕尔府邸中的海神喷泉由Lorenzo Mattielli制作。",
                "quote_text": "the\nNeptune fountain by Lorenzo Mattielli",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Lorenzo Mattielli”及第7、14章中的雕塑家Lorenzo Mattielli。第7章称他与Domenico Antonio Parodi为Prince Eugene的大厅和花园制作雕像；"
            "第14章将布吕尔府邸中的海神喷泉归于Mattielli。作品归属仍按原书表述留待关系阶段审查。"
        ),
        "description_en": (
            "This card represents the index entry “Lorenzo Mattielli” and the sculptor Lorenzo Mattielli in chapters 7 and 14. Chapter 7 says he and Domenico Antonio Parodi made statues for Prince Eugene’s hall and gardens. Chapter 14 attributes the Neptune fountain at Brühl’s houses to Mattielli. These work attributions remain as stated in the book and await relation review."
        ),
        "identity_extra": "第7、14章全名及索引页201、353共同支持同一跨章人物组；未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-1584 remains the person group new-person:lorenzo-mattielli-e53f3c6116. The full name in chapter 7 p.201 and chapter 14 p.353 aligns with index M.csv#123; no exact existing person KU matched. No external identity source was accessed."
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
        "### S3→S4 person：Giuseppe Mazza、Francisco Goya 与 Lorenzo Mattielli 登记（2026-10-17）\n\n"
        "按索引全名及跨章正文提及复核三个person new组。Giuseppe Mazza由第8章p.222、p.227及第9章p.251的全名锚定；Francisco Goya由索引全名连接至第7章p.192和第10章p.297注的“young Goya”语境，原书影响判断不作外部验证；Lorenzo Mattielli由第7章p.201与第14章p.353的雕塑/喷泉语境连接。无外部身份资料写入，6条S2直接关系候选留待S6。\n\n"
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
    result_heading = "### S3→S4 person：Giuseppe Mazza、Francisco Goya 与 Lorenzo Mattielli 登记（2026-10-17）"
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
