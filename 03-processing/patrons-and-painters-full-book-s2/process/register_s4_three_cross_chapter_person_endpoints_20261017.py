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
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017d"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-2133",
        "group": "new-person:paolo-renier-809f039f6e",
        "ku": "units/persons/paolo-renier",
        "name_zh": "保罗·雷尼耶",
        "name_en": "Paolo Renier",
        "index_entry": "Q-R.csv#60",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
        "index_quote": "Renier, Paolo",
        "body_source": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "source_fragments": ["1767 Paolo Renier wrote", "wrote Paolo Renier in 1772"],
        "sources": [
            {
                "location": "第9章；印刷页257；Markdown L170",
                "summary": "Haskell引述 Paolo Renier 于1772年论述自由共和国中的公民身份与臣属服务之别。",
                "span": "Markdown line 170; print p. 257",
                "quotes": [("line 170", "‘There must be a great difference’, wrote Paolo Renier in 1772, ‘between a minister who serves his Prince as a subject and one to whom God’s special grace has granted the supreme boon of living in a free Republic and of being a small but essential part of the whole.’")],
            },
            {
                "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "location": "第15章；印刷页371–372；Markdown L83、86",
                "summary": "Haskell将 Paolo Renier 描述为 Querini 的政治友人，并记其于1779年成为威尼斯总督；两人关系及后续政治分歧留作关系候选审查。",
                "span": "Markdown lines 83, 86–87; print pp. 371–372",
                "quotes": [("line 83", "In his younger days he had been closely associated with another potential reformer, Paolo Renier"), ("lines 86–87", "to become Doge in 1779. When, later, Renier compromised with the forces that he had once attacked, Querini flung the bust in a rage of disappointment against the Altar of\nFuries in his garden.1")],
            },
        ],
        "description_zh": "Haskell引述 Paolo Renier 于1772年关于自由共和国、公民身份与臣属服务的论说，并记其于1779年成为威尼斯总督。有关其政治立场及与 Querini 的交往按书内叙述保留；关系候选尚待 S6 审查。中文名为项目工作音译。",
        "description_en": "Haskell quotes Paolo Renier in 1772 on the distinction between serving a prince as a subject and living as a citizen of a free republic, and records that he became Doge in 1779. Accounts of his political positions and association with Querini remain attributed to the book; their relation candidates await S6 review. The Chinese name is a project working transliteration.",
        "location": "第9章印刷页257；第15章印刷页371–372；Markdown L170、83、86–87",
        "relation_ids": [
            "st-chp15-p372-renier-became-doge-1779",
            "st-chp15-p372-renier-compromised-with-opposing-forces",
            "st-chp15-p371-querini-associated-with-paolo-renier",
            "st-chp15-p371-renier-bust-portrayed-paolo-renier",
            "st-chp9-p247-renier-avoid-novelty",
        ],
    },
    {
        "candidate": "cand-1979",
        "group": "new-person:first-henry-of-portland-5343884e1e",
        "ku": "units/persons/henry-first-duke-portland",
        "name_zh": "亨利，波特兰第一代公爵",
        "name_en": "Henry, first Duke of Portland",
        "index_entry": "P.csv#181",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
        "index_quote": "Portland, Henry, first Duke of",
        "body_source": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "source_fragments": ["One of his earliest employers in England was Lord Portland", "Henry, who succeeded to the Portland title in 1709 and was created first Duke in 1716"],
        "sources": [
            {
                "location": "第10章；印刷页279；Markdown L49",
                "summary": "Haskell称 Lord Portland 是 Ricci 早期的英国雇主之一。",
                "span": "Markdown line 49; print p. 279",
                "quotes": [("line 49", "One of his earliest employers in England was Lord Portland")],
            },
            {
                "location": "第10章；印刷页280；Markdown L52–55",
                "summary": "Haskell称 Henry 是 William Bentinck 之子，1709年继承 Portland 爵位、1716年成为第一代公爵；他曾委托 Sebastiano Ricci 为其宅邸及乡间住宅礼拜堂绘画。",
                "span": "Markdown lines 52–55; print p. 280",
                "quotes": [("lines 52–53", "This young man was the son of\nWilliam Ill’s great favourite, the Dutch William Bentinck, whose loyalty to the Orange cause had been rewarded with vast estates.2 Henry, who succeeded to the Portland title in 1709 and was created first Duke in 1716, had lived a great deal abroad and had had his portrait painted by Rigaud in 1699—a work that seems to endorse the opinion of a contemporary that he was ‘a fine fellow, but very affected’."), ("lines 53–55", "He commissioned paintings from Ricci for his town house, and above all for the chapel of his country house at\nBulstrode Park in Buckinghamshire—The Ascension, The Last Supper, The Baptism of\nChrist and The Visitation.3")],
            },
        ],
        "description_zh": "Haskell将此人物称作 Henry，并记他是 William Bentinck 之子，1709年继承 Portland 爵位、1716年成为第一代公爵。他委托 Sebastiano Ricci 为城镇宅邸及 Bulstrode Park 乡间住宅礼拜堂作画。中文展示名按书后索引的头衔译出；来源未给出更完整的名字。",
        "description_en": "Haskell identifies the person as Henry, son of William Bentinck, who succeeded to the Portland title in 1709 and was created first Duke in 1716. He commissioned Sebastiano Ricci to paint for his town house and the chapel at his country house at Bulstrode Park. The displayed name follows the index title; the source does not provide a fuller given name.",
        "location": "第10章印刷页279–280；Markdown L49、52–55",
        "relation_ids": [
            "st-chp10-p279-portland-early-employer-open",
            "st-chp10-p280-portland-bulstrode-chapel-programme",
            "st-chp10-p280-portland-commissioned-pellegrini",
            "st-chp10-p280-portland-ricci-townhouse",
            "st-chp10-p280-portland-son-of-bentinck",
        ],
    },
    {
        "candidate": "cand-2286",
        "group": "new-person:del-ottavio-rosso-c602335dc8",
        "ku": "units/persons/ottavio-del-rosso",
        "name_zh": "奥塔维奥·德尔·罗索",
        "name_en": "Ottavio del Rosso",
        "index_entry": "Q-R.csv#214",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
        "index_quote": "Rosso, Ottavio del",
        "body_source": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "source_fragments": ["three brothers, Andrea, Lorenzo and Ottavio", "Ottavio entered the"],
        "sources": [
            {
                "location": "第8章；印刷页210–211；Markdown L82、85",
                "summary": "Haskell称 Andrea、Lorenzo 与 Ottavio del Rosso 是兄弟，并将他们称为当时重要收藏家之一。",
                "span": "Markdown lines 82, 85; print pp. 210–211",
                "quotes": [("line 82", "It was inhabited by three brothers, Andrea, Lorenzo and Ottavio"), ("line 85", "del Rosso, who were among the most notable collectors")],
            },
            {
                "location": "第8章；印刷页211；Markdown L86–87",
                "summary": "Haskell称 Ottavio 入教会并任 Volterra 主教，居于 Volterra；原文 OCR 将 Bishop 识别为“Bjshop”。",
                "span": "Markdown lines 86–87; print p. 211",
                "quotes": [("lines 86–87", "Ottavio entered the\nChurch and became Bjshop of Volterra, where he lived in ‘concetto di straordinaria bontà’;")],
            },
            {
                "location": "第8章；印刷页211；Markdown L96",
                "summary": "Haskell记 Ottavio 于1714年去世。",
                "span": "Markdown line 96; print p. 211",
                "quotes": [("line 96", "Ottavio died in 1714")],
            },
        ],
        "description_zh": "Haskell称 Ottavio del Rosso 是 Andrea 与 Lorenzo del Rosso 的兄弟，曾入教会并居于 Volterra；原书 OCR 将其职衔识别为“Bjshop”，按语境释读为主教，未作外部核验。书中记 Ottavio 于1714年去世。相关亲缘、任职与居住关系留待 S6 审查。中文名为项目工作音译。",
        "description_en": "Haskell identifies Ottavio del Rosso as a brother of Andrea and Lorenzo del Rosso, says he entered the Church and lived in Volterra, and records his death in 1714. The OCR reads his office as “Bjshop”; the description interprets this in context as bishop, without independent external verification. The family, office, and residence relation candidates remain for S6 review. The Chinese name is a project working transliteration.",
        "location": "第8章印刷页210–211；Markdown L82、85–87、96",
        "relation_ids": [
            "st-chp8-p210-house-inhabited-by-ottavio-del-rosso",
            "st-chp8-p211-ottavio-bishop-volterra",
            "st-chp8-p211-ottavio-entered-church",
            "st-chp8-p211-ottavio-lived-in-volterra",
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
    anchor = '<a id="s4-person-endpoints-20261017d"></a>'
    assert anchor not in process_text
    process_text += "\n\n" + anchor + "\n\n### S4 person：三组跨章人物端点登记（2026-10-17）\n\n"
    process_text += "三个候选各自属于单成员 person new 身份组，均有索引主项及正文身份锚点；Henry 与 Ottavio 的姓名按来源可确证范围呈现。各组分别登记一张人物 KU。14 条直接 S2 关系候选保留待 S6，未新增正式关系。\n\n"
    process_text += "| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |\n|---|---|---|---:|\n"
    for t in TARGETS:
        process_text += f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['location']} 与索引 {t['index_entry']} | {len(t['relation_ids'])} |\n"
    process_text += "\nOttavio p.211 的 OCR 将 Bishop 识别为“Bjshop”，卡片保留原始转录并在描述中按语境释读，未作外部核验。Henry 以书中给出的 Henry 和 Portland 公爵头衔作双语展示，不补未见于本书的名字。\n"
    result_text += "\n\n### S4 person：Paolo Renier、Henry（波特兰第一代公爵）与 Ottavio del Rosso 登记（2026-10-17）\n\n"
    for t in TARGETS:
        result_text += f"- `{t['candidate']}` → [{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)：{t['location']}；{len(t['relation_ids'])}条直接关系候选待 S6。\n"
    result_text += "\n未新增正式关系或外部身份核验。\n"

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == 436
    assert totals["pending_groups"] == 4377
    assert totals["pending_members"] == 4436

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
