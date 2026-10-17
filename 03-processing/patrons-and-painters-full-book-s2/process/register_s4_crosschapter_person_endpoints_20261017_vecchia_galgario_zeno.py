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
ANCHOR = "s4-crosschapter-person-endpoints-vecchia-galgario-zeno-20261017"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-2707",
        "group": "new-person:della-pietro-vecchia-bd2908fb58",
        "ku": "units/persons/pietro-della-vecchia",
        "name_zh": "皮耶特罗·德拉·韦基亚",
        "name_en": "Pietro della Vecchia",
        "index_entry": "UVWXYZ.csv#43",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "index_line": 45,
        "index_quote": "Vecchia, Pietro della",
        "index_span": "UVWXYZ.csv#43; CSV line 45; pp. 193, 340, 376",
        "chapters": "第7、13、16章；索引 UVWXYZ.csv#43",
        "relation_ids": [
            "st-chp7-p193-leopold-patronizes-vecchia",
            "st-chp7-p193-vecchia-forgeries",
            "st-chp16-p376-vianello-vecchia-favourite",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "line_start": 8,
                "line_end": 8,
                "location": "第7章，印刷页193，Markdown L8",
                "span": "Markdown line 8; print p. 193",
                "summary": "Haskell称Archduke Leopold Wilhelm曾赞助Pietro della Vecchia，并把其声誉部分归于对Giorgione作品的伪作；此为作者判断，未独立核验。",
                "quote_text": "one of the contemporaries whom he most patronised was Pietro della Vecchia",
            },
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "line_start": 80,
                "line_end": 80,
                "location": "第13章，印刷页340，Markdown L80",
                "span": "Markdown line 80; print p. 340",
                "summary": "Haskell称Pinelli的收藏中包含Pietro della Vecchia的绘画。",
                "quote_text": "and Pietro della Vecchia, figure very strongly in his collection",
            },
            {
                "file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "line_start": 41,
                "line_end": 41,
                "location": "第16章，印刷页376，Markdown L41",
                "span": "Markdown line 41; print p. 376",
                "summary": "Haskell称Vianello最喜爱Pietro della Vecchia的作品；该行OCR将名拼作“Pietrp”。",
                "quote_text": "His special favourite was Pietrp della Vecchia",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Vecchia, Pietro della”及第7、13、16章中Pietro della Vecchia的提及。第7章称Archduke Leopold Wilhelm曾赞助他，并称其声誉部分依赖对Giorgione作品的伪作；"
            "第13章提到Pinelli收藏中有其绘画；第16章记载Vianello最喜爱他的作品，原Markdown将名转录为“Pietrp”。作者对伪作和作品归属的判断保留为来源表述。"
        ),
        "description_en": (
            "This card represents the index entry “Vecchia, Pietro della” and references to Pietro della Vecchia in chapters 7, 13, and 16. Chapter 7 says Archduke Leopold Wilhelm patronised him and that part of his reputation depended on forgeries of Giorgione. Chapter 13 mentions his pictures in Pinelli’s collection. Chapter 16 records Vianello’s special preference for his work; the source Markdown transcribes the name there as “Pietrp.” The author’s statements about forgery and attribution remain attributed to the book."
        ),
        "identity_extra": "p.193与索引提供全名锚点；p.376的OCR异文“Pietrp”按来源原样保留。未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-2707 remains the person group new-person:della-pietro-vecchia-bd2908fb58. The full name in chapter 7 p.193 and index UVWXYZ.csv#43 anchors chapter 13 p.340 and chapter 16 p.376 references; the latter OCR reads “Pietrp” and is retained as transcribed. Haskell’s forgery statement remains an authorial claim, not independent authentication. No exact existing person KU matched; no external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-1101",
        "group": "new-person:fra-galgario-ghislandi-vittore-8b50b26f92",
        "ku": "units/persons/fra-galgario-vittore-ghislandi",
        "name_zh": "维托雷·吉斯兰迪（Fra Galgario）",
        "name_en": "Fra Galgario (Vittore Ghislandi)",
        "index_entry": "G.csv#8",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/G.csv",
        "index_line": 10,
        "index_quote": "Galgario, Fra (Vittore Ghislandi)",
        "index_span": "G.csv#8; CSV line 10; pp. 165, 200, 201",
        "chapters": "第6、7章；索引 G.csv#8",
        "relation_ids": [
            "st-chp6-p165-v1-25",
            "st-chp6-p165-v1-26",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
                "line_start": 40,
                "line_end": 40,
                "location": "第6章，印刷页165，Markdown L40",
                "span": "Markdown line 40; print p. 165",
                "summary": "Haskell称Fra Galgario与威尼斯密切相关、居住在Bergamo，并拒绝Ottoboni召他赴罗马。",
                "quote_text": "Fra Galgario, refused to come to Rome when called there by Ottoboni",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
                "line_start": 18,
                "line_end": 18,
                "location": "第7章，印刷页200注，Markdown L18",
                "span": "Markdown line 18; index locator p. 200",
                "summary": "注释记述其为Prince Eugene绘制肖像，Markdown转录名为“Vittore Gliislandi”。",
                "quote_text": "portrait from Vittore Gliislandi",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
                "line_start": 50,
                "line_end": 51,
                "location": "第7章，印刷页201，Markdown L55",
                "span": "Markdown lines 50–51; print p. 201",
                "summary": "Haskell将Vittore Ghislandi列入Prince Eugene收藏中的意大利画家。",
                "quote_text": "by Vittore\nGhislandi from Bergamo",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Galgario, Fra (Vittore Ghislandi)”及第6、7章中的Fra Galgario／Vittore Ghislandi。第6章称Fra Galgario与威尼斯密切相关、居于Bergamo，并拒绝Ottoboni召其赴罗马；"
            "第7章将Vittore Ghislandi列入Prince Eugene收藏中的画家，并在注释提及其肖像。索引将两种称谓置于同一词头。"
        ),
        "description_en": (
            "This card represents the index entry “Galgario, Fra (Vittore Ghislandi)” and Fra Galgario / Vittore Ghislandi in chapters 6 and 7. Chapter 6 says Fra Galgario was closely associated with Venice, lived in Bergamo, and refused Ottoboni’s call to Rome. Chapter 7 lists Vittore Ghislandi among painters represented in Prince Eugene’s collection and mentions his portrait in a note. The index places both names under one entry."
        ),
        "identity_extra": "S3按索引明确的别名关系将Fra Galgario与Vittore Ghislandi归入同一人物；保留第7章注释转录异文“Gliislandi”。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-1101 remains the person group new-person:fra-galgario-ghislandi-vittore-8b50b26f92. Index G.csv#8 explicitly joins “Fra Galgario” and “Vittore Ghislandi”; chapter 6 p.165 uses the former, while chapter 7 pp.200–201 uses the latter. The note transcription “Vittore Gliislandi” is retained as a source variant. No exact existing person KU matched; no external identity source was accessed."
        ),
    },
    {
        "candidate": "cand-2869",
        "group": "new-person:apostolo-zeno-9866a1a3e7",
        "ku": "units/persons/apostolo-zeno",
        "name_zh": "阿波斯托洛·泽诺",
        "name_en": "Apostolo Zeno",
        "index_entry": "UVWXYZ.csv#206",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "index_line": 208,
        "index_quote": "Zeno, Apostolo",
        "index_span": "UVWXYZ.csv#206; CSV line 208; pp. 230, 300",
        "chapters": "第8、10章；索引 UVWXYZ.csv#206",
        "relation_ids": [
            "st-chp8-p230-writers-and-redi-editions",
            "st-chp10-p300-smith-connoisseur-contacts",
        ],
        "sources": [
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "line_start": 229,
                "line_end": 230,
                "location": "第8章，印刷页230，Markdown L229–230",
                "span": "Markdown lines 229–230; print p. 230",
                "summary": "Haskell称Ferdinand支持Apostolo Zeno等作家并资助诗集出版。",
                "quote_text": "He supported writers such as Apostolo Zeno",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "line_start": 377,
                "line_end": 378,
                "location": "第10章，印刷页300，Markdown L377–378",
                "span": "Markdown lines 377–378; print p. 300",
                "summary": "Haskell称Joseph Smith早年曾与Apostolo Zeno、Algarotti、Antonio Maria Zanetti等鉴赏家保持友好往来。",
                "quote_text": "friendly relations at various times with the connoisseurs Apostolo Zeno",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Apostolo Zeno”及第8、10章中的Apostolo Zeno。第8章称Ferdinand支持Zeno等作家并资助诗集出版；"
            "第10章称Joseph Smith早年曾与Zeno等鉴赏家保持友好往来。关系断言仍分别作为S2候选留待S6审查。"
        ),
        "description_en": (
            "This card represents the index entry “Apostolo Zeno” and Apostolo Zeno in chapters 8 and 10. Chapter 8 says Ferdinand supported Zeno and other writers and financed editions of poets. Chapter 10 says Joseph Smith had friendly relations at various times with Zeno and other connoisseurs. These relationship assertions remain individual S2 candidates for S6 review."
        ),
        "identity_extra": "第8、10章均给出Apostolo Zeno全名；未采用外部身份标识。",
        "s3_note": (
            "S3 cross-chapter review (2026-10-17): cand-2869 remains the person group new-person:apostolo-zeno-9866a1a3e7. Index UVWXYZ.csv#206 and the matching full name at chapter 8 p.230 and chapter 10 p.300 support one source-local person identity. No exact existing person KU matched; no external identity source was accessed."
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
        "### S3→S4 person：Pietro della Vecchia、Fra Galgario 与 Apostolo Zeno 登记（2026-10-17）\n\n"
        "按索引主项及跨章正文锚点复核三个person new组。Pietro della Vecchia由第7章p.193全名连接至第13章p.340和第16章p.376；后者OCR读作“Pietrp”，保留原样，第7章关于Giorgione伪作的表述仍是Haskell的判断。Fra Galgario与Vittore Ghislandi按G.csv#8的同一索引词头合组；第7章注释另有“Gliislandi”转录异文。Apostolo Zeno由第8章p.230和第10章p.300的同名全称跨章锚定。无外部身份资料写入，6条S2关系候选继续留待S6。\n\n"
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
    result_heading = "### S3→S4 person：Pietro della Vecchia、Fra Galgario 与 Apostolo Zeno 登记（2026-10-17）"
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
