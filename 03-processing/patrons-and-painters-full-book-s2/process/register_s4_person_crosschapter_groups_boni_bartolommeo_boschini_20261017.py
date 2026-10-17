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
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/B.csv"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
GROUPS = {
    "boni": {
        "members": ["cand-0388", "cand-0389"],
        "group": "new-person:antonio-boni-giacomo-1f5e983239",
        "ku_id": "units/persons/giacomo-antonio-boni",
        "name_zh": "贾科莫·安东尼奥·博尼",
        "name_en": "Giacomo Antonio Boni",
        "card": "04-knowledge/units/persons/giacomo-antonio-boni.md",
        "anchor": "s4-person-boni-crosschapter-20261017",
        "review": (
            "B.csv#235 主项列 p.201 与 p.214 注；B.csv#236 子项“Virgil 'portrait' for Prince Eugene of Savoy”列 p.201。"
            "第7章 p.201 以全名称在 Bologna 为 Prince Eugene 绘制 Virgil 'portrait' 的 Boni；第8章 p.214 注以同一全名"
            "称受召为宫殿房间绘制神话壁画。跨章全名、职业语境及索引子项互相吻合，未发现同名冲突或既有 person KU。"
        ),
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第7章，印刷页201；OCR L52",
                "summary": "Haskell 称 Giacomo Antonio Boni 在 Bologna 为 Prince Eugene 绘制 Virgil 写作《埃涅阿斯纪》的肖像画。",
                "quote": "Virgil, whose ‘portrait’ writing the Aeneid he commissioned from Giacomo Antonio Boni in Bologna.",
                "file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
                "span": "line 52; print p. 201",
            },
            {
                "citation": BOOK_CITATION,
                "location": "第8章，印刷页214，注；视觉转录 L1",
                "summary": "注释称 Giacomo Antonio Boni 受召为宫殿房间绘制神话壁画。",
                "quote": "they summoned Giacomo Antonio Boni to decorate the rooms of their palace with mythological frescoes",
                "file": "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md",
                "span": "line 1; print p. 214 note",
            },
            {
                "citation": INDEX_CITATION,
                "location": "全书索引 B.csv#235–236",
                "summary": "主项列 p.201、p.214 注；子项定位 Prince Eugene 的 Virgil 肖像委托。",
                "quote": "Boni, Giacomo Antonio; Virgil ‘portrait’ for Prince Eugene of Savoy",
                "file": INDEX_FILE,
                "span": "B.csv#235–236",
            },
        ],
        "description_zh": (
            "Haskell 在第7章 p.201 记载 Giacomo Antonio Boni 在 Bologna 为 Prince Eugene 绘制 Virgil 写作《埃涅阿斯纪》的肖像画；"
            "第8章 p.214 注又以同一全名记载其受召为宫殿房间绘制神话壁画。书后索引将 p.201 与 p.214 注列于同一人物主项，"
            "并以 Virgil 肖像作为 p.201 子项。本卡记录书内跨章人物身份与这两处工作语境，不推定具体作品现状或未明示的委托方。"
        ),
        "description_en": (
            "In Chapter 7, p.201, Haskell says Giacomo Antonio Boni in Bologna was commissioned by Prince Eugene to paint a ‘portrait’ of Virgil writing the Aeneid. "
            "Chapter 8, p.214 note, names Boni again as summoned to decorate palace rooms with mythological frescoes. The index places p.201 and p.214 n. under one person entry, "
            "with the Virgil portrait as a p.201 subentry. This card records the book’s cross-chapter identity and these two work contexts without asserting the works’ present status or an unnamed patron’s identity."
        ),
    },
    "bartolommeo": {
        "members": ["cand-0252", "cand-0253"],
        "group": "new-person:bartolommeo-fra-e49e28ddb8",
        "ku_id": "units/persons/fra-bartolommeo",
        "name_zh": "弗拉·巴托洛梅奥",
        "name_en": "Fra Bartolommeo",
        "card": "04-knowledge/units/persons/fra-bartolommeo.md",
        "anchor": "s4-person-fra-bartolommeo-crosschapter-20261017",
        "review": (
            "B.csv#99 主项列 p.348；B.csv#100 的 S. Marco 子项列 p.231。第8章 p.231 明确将 S. Marco 画作归于 Fra Bartolommeo；"
            "第14章 p.348 记载 Algarotti 对 Fra Bartolommeo 的艺术成就印象深刻。两处均指画家，不将作品 S. Marco 并入人物卡。"
        ),
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第8章，印刷页231；OCR L247",
                "summary": "Haskell 称 Ferdinand 从圣马可堂购入 Fra Bartolommeo 的 S. Marco 画作，并于1692年以复制品替换。",
                "quote": "purchasing Fra Bartolommeo’s S. Marco from the church dedicated to that saint and having it replaced by a copy in 1692",
                "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "span": "line 247; print p. 231",
            },
            {
                "citation": BOOK_CITATION,
                "location": "第14章，印刷页348；OCR L18",
                "summary": "Haskell 记载 Algarotti 于1733年在 Florence 对 Fra Bartolommeo 的艺术成就印象深刻。",
                "quote": "he was overwhelmed by the greatness of Fra Bartolommeo, of whom he now heard for the first time",
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "span": "line 18; print p. 348",
            },
            {
                "citation": INDEX_CITATION,
                "location": "全书索引 B.csv#99–100",
                "summary": "Fra Bartolommeo 主项定位 p.348；S. Marco 子项定位 p.231。",
                "quote": "Bartolommeo, Fra; S. Marco",
                "file": INDEX_FILE,
                "span": "B.csv#99–100",
            },
        ],
        "description_zh": (
            "Haskell 在第8章 p.231 将 S. Marco 画作归于 Fra Bartolommeo，记载 Ferdinand 于1692年以复制品替换该教堂原画；"
            "第14章 p.348 又记载 Algarotti 于1733年在 Florence 对 Fra Bartolommeo 的艺术成就印象深刻。索引将两处定位于同一人物项。"
            "本卡记录书内人物身份；S. Marco 作品与其版本不作为人物知识元并入。"
        ),
        "description_en": (
            "In Chapter 8, p.231, Haskell attributes the S. Marco painting to Fra Bartolommeo and says Ferdinand replaced the church painting with a copy in 1692. "
            "Chapter 14, p.348, records Algarotti’s strong impression of Fra Bartolommeo’s art in Florence in 1733. The index locates both passages under one person entry. "
            "This card records the person in the book; the S. Marco work and its versions are not folded into the person unit."
        ),
    },
    "bosch": {
        "members": ["cand-0412", "cand-0413"],
        "group": "new-person:boschini-marco-6cf51f8040",
        "ku_id": "units/persons/marco-boschini",
        "name_zh": "马尔科·博斯基尼",
        "name_en": "Marco Boschini",
        "card": "04-knowledge/units/persons/marco-boschini.md",
        "anchor": "s4-person-boschini-crosschapter-20261017",
        "review": (
            "第7章 p.193 注2的 Boschini p.44 引文由第21章书目识别为 Marco Boschini《La carta del navegar pittoresco》（Venice, 1660）；"
            "第13章 p.345 明称 Marco Boschini 的《Ricche Miniere》于1733年由较年轻的 Zanetti 修订。B.csv#259–260 主项及作品子项对应两章。"
            "两部出版物仍各自作为 archive 对象处理；作者身份合并为一个人物 KU。"
        ),
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第7章，印刷页193，注2",
                "summary": "脚注以 Boschini, p.44 引用其著作，并称该书讨论 Leopold Wilhelm 的威尼斯古代大师收藏。",
                "quote": "Boschini, p. 44 — The book is dedicated to the Archduke and discusses his collection of Venetian old masters",
                "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "span": "line 21; print p. 193, note 2",
            },
            {
                "citation": BOOK_CITATION,
                "location": "第21章书目，印刷页416；OCR L231",
                "summary": "书目将相关出版物著录为 Marco Boschini《La carta del navegar pittoresco》，Venice, 1660。",
                "quote": "Boschini, Marco: La carta del navegar pittoresco, Venezia 1660.",
                "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
                "span": "line 231; print p. 416",
            },
            {
                "citation": BOOK_CITATION,
                "location": "第13章，印刷页345；OCR L164",
                "summary": "Haskell 称较年轻的 Zanetti 修订 Boschini 的《Ricche Miniere》，1733年编辑出版。",
                "quote": "his admirable revision of Boschini’s Ricche Miniere edited in 1733",
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "span": "line 164; print p. 345",
            },
            {
                "citation": INDEX_CITATION,
                "location": "全书索引 B.csv#259–260",
                "summary": "Boschini, Marco 主项及 Ricche Miniere 子项定位第13章 p.345。",
                "quote": "Boschini, Marco; Ricche Miniere",
                "file": INDEX_FILE,
                "span": "B.csv#259–260",
            },
        ],
        "description_zh": (
            "Haskell 第21章书目将 Marco Boschini 的《La carta del navegar pittoresco》著录为 Venice, 1660；第7章 p.193 注2以 Boschini p.44 引用该书。"
            "第13章 p.345 又记载较年轻的 Zanetti 于1733年修订 Boschini 的《Ricche Miniere》。两处姓名、书目锚点与索引主项相合，"
            "支持将作者作为同一人物登记。两部出版物保留各自的 archive 身份；本卡不将作者与著作合并为同一 KU。"
        ),
        "description_en": (
            "Haskell’s Chapter 21 bibliography lists Marco Boschini’s La carta del navegar pittoresco (Venice, 1660), cited at p.44 in the Chapter 7, p.193 note. "
            "Chapter 13, p.345, also records the younger Zanetti’s 1733 revision of Boschini’s Ricche Miniere. The names, bibliographic anchors, and index entry support one author identity. "
            "The two publications retain separate archive identities; this card does not merge an author with his books."
        ),
    },
}


def source_objects(spec: dict) -> list[dict]:
    result = []
    for source in spec["sources"]:
        if source["citation"] == INDEX_CITATION:
            path = f"../../../{INDEX_FILE}"
        elif "; " in source["file"]:
            path = "../../../02-sources/02-Markdown/07_CHP-7_sec_iv.md"
        else:
            path = f"../../../{source['file']}"
        result.append({
            "citation": source["citation"],
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["span"], "text": source["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source["file"],
                "source_span": source["span"],
            },
            "link": path,
        })
    return result


def make_card(key: str) -> str:
    spec = GROUPS[key]
    fm_sources = source_objects(spec)
    yaml_sources = []
    for s in fm_sources:
        yaml_sources.append({k: v for k, v in s.items() if k != "link"})
    process_ref = f"03-processing/{TASK}/process/knowledge.md#{spec['anchor']}"
    fm = yaml.safe_dump({
        "title": f"{spec['name_zh']}（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": yaml_sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": process_ref,
    }, allow_unicode=True, sort_keys=False, width=1000)
    links = "；".join(f"[{s['location']}]({s['link']})" for s in fm_sources)
    members = "、".join(spec["members"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {spec['description_zh']}〔{links}〕

**English:** {spec['description_en']} ({links})

### 身份与来源边界

- 本卡对应 S3 new 身份组 {spec['group']}，成员为 {members}；书内跨章证据支持这些候选指向同一人物。
- 仅记录来源中可见的人名、语境和著作／作品提及；不补充未经本轮核验的生平、馆藏现状或作品版本。

## 关系与证据

### 关系记录

本轮未在 relations.csv 新增正式关系。姓名同现、引文或作品归属依据仍按具体 statement 及关系阶段处理。逐组裁决见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{spec['anchor']})。
"""


def insert_accepted(lines: list[str], card_rel: str) -> list[str]:
    entry = f"- {card_rel}"
    assert entry not in lines
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_rel),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Review and register three cross-chapter person identity groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    planned_alignments = [dict(row) for row in alignments]
    member_rows = {}
    for key, spec in GROUPS.items():
        actual_group_members = [
            row["candidate_id"] for row in planned_alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert actual_group_members == spec["members"]
        rows = [
            row for row in planned_alignments
            if row.get("candidate_id") in spec["members"] and not row.get("external_source")
        ]
        assert len(rows) == len(spec["members"]) and all(row["decision"] == "new" and not row.get("ku_id") for row in rows)
        assert not any(row.get("ku_id") == spec["ku_id"] for row in manifest)
        assert not (ROOT / spec["card"]).exists()
        assert spec["card"] not in accepted_lines
        assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == spec["name_en"].casefold() for row in manifest)
        for row in rows:
            row["process_ref"] = f"{TASK}#{spec['anchor']}"
            row["resolution_note"] += f" S3跨章语义复核（{DATE}）：{spec['review']}"
            row["ku_id"] = spec["ku_id"]
            row["resolution_note"] += (
                f" S4登记（{DATE}）：{spec['group']} 中的候选映射至 {spec['ku_id']}；一组一张来源限定 person KU。"
            )
        member_rows[key] = rows

    for relative in (
        "02-sources/02-Markdown/07_CHP-7_sec_v.md",
        "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md",
        "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "02-sources/02-Markdown/13_CHP-13_intro.md",
        "02-sources/02-Markdown/14_CHP-14_intro.md",
        "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    ):
        assert (ROOT / relative).is_file()
    source_texts = {
        relative: (ROOT / relative).read_text(encoding="utf-8-sig")
        for relative in (
            "02-sources/02-Markdown/07_CHP-7_sec_v.md",
            "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md",
            "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
            "02-sources/02-Markdown/13_CHP-13_intro.md",
            "02-sources/02-Markdown/14_CHP-14_intro.md",
            "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
            "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        )
    }
    assert "Giacomo Antonio Boni in Bologna" in source_texts["02-sources/02-Markdown/07_CHP-7_sec_v.md"]
    assert "summoned Giacomo Antonio Boni to decorate the rooms" in source_texts["02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md"]
    assert "Fra Bartolommeo’s S. Marco" in source_texts["02-sources/02-Markdown/08_CHP-8_sec_ii.md"]
    assert "overwhelmed by the greatness of Fra Bartolommeo" in source_texts["02-sources/02-Markdown/14_CHP-14_intro.md"]
    assert "Boschini, p. 44" in source_texts["02-sources/02-Markdown/07_CHP-7_sec_iv.md"]
    assert "Boschini, Marco: La carta del navegar pittoresco" in source_texts["02-sources/02-Markdown/21_CHP-21Bibliography.md"]
    assert "revision of Boschini’s Ricche Miniere edited in 1733" in source_texts["02-sources/02-Markdown/13_CHP-13_intro.md"]

    member_ids = {cid for spec in GROUPS.values() for cid in spec["members"]}
    direct_relations = {
        statement["statement_id"] for statement in statements
        if (statement.get("qualifiers") or {}).get("relation_candidate") is True
        and (statement.get("subject_candidate_id") in member_ids or statement.get("object_candidate_id") in member_ids)
    }
    assert not direct_relations, f"unexpected direct S2 relation candidates need explicit card treatment: {sorted(direct_relations)}"

    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    cards = {}
    for key, spec in GROUPS.items():
        cards[spec["card"]] = make_card(key)
        planned_manifest.append({
            "ku_id": spec["ku_id"],
            "type": "person",
            "canonical_name": spec["name_zh"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": spec["card"],
        })
        planned_accepted = insert_accepted(planned_accepted, spec["card"])
        frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", cards[spec["card"]], re.DOTALL)
        assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)
    planned_manifest.sort(key=lambda row: row["ku_id"])

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4968
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 670
    assert totals["registered_members"] == 830
    assert totals["pending_groups"] == 4115
    assert totals["pending_members"] == 4138
    assert len(planned_manifest) == len(manifest) + len(GROUPS)

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    additions = []
    for key, spec in GROUPS.items():
        assert f'<a id="{spec["anchor"]}"></a>' not in process_text
        members = "、".join(spec["members"])
        additions.append(
            f"<a id=\"{spec['anchor']}\"></a>\n\n### S3/S4 person：{spec['name_en']} 跨章身份复核与登记（{DATE}）\n\n"
            f"- 候选 {members} 维持同一 S3 new 组 {spec['group']}；{spec['review']}\n"
            f"- 该组登记为 [{spec['name_zh']}（{spec['name_en']}）](../../../{spec['card']})（{spec['ku_id']}）。"
            "卡片限于本书中的姓名、语境与具体书目／作品提及；未补外部传记，未写入正式关系。"
        )
    process_text = process_text.rstrip() + "\n\n" + "\n\n".join(additions) + (
        f"\n\nS4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert count == 1
    result_text += "\n\n### S3/S4 person：三组跨章人物身份复核与登记（2026-10-17）\n\n"
    result_text += "；".join(
        f"{ '、'.join(spec['members']) } → [{spec['name_zh']}（{spec['name_en']}）](../units/persons/{Path(spec['card']).stem}.md)"
        for spec in GROUPS.values()
    ) + "。逐组裁决、来源边界与组成员见过程记录。"

    if args.dry_run:
        print(
            f"dry-run passed: groups={len(GROUPS)}; candidate_mappings={sum(len(s['members']) for s in GROUPS.values())}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    for card_rel, card_text in cards.items():
        (ROOT / card_rel).write_text(card_text, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(GROUPS)}; candidate_mappings={sum(len(s['members']) for s in GROUPS.values())}; "
        f"manifest={len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
