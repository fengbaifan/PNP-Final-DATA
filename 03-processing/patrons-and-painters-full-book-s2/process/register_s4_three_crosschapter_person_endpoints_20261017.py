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
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017h"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-0417",
        "group": "new-person:bottari-giovanni-634e17e1ce",
        "ku": "units/persons/giovanni-bottari",
        "name_zh": "乔瓦尼·博塔里",
        "name_en": "Giovanni Bottari",
        "index_entry": "B.csv#264",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
        "index_quote": "Bottari, Giovanni",
        "sources": [
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "location": "第14章，印刷页348，Markdown L21",
                "summary": "Haskell称Algarotti抵达罗马后不久结识Giovanni Bottari并与他开始终身通信；同段将Bottari列为罗马学者和古物研究者群体成员，但没有为该群体命名机构。",
                "line_start": 21,
                "line_end": 21,
                "span": "Markdown line 21; print p. 348",
            }
        ],
        "description_zh": (
            "第14章印刷页348明确写出Giovanni Bottari全名，并称Algarotti到罗马后不久结识他、与他开始终身通信；"
            "同段将Bottari列为罗马一群学者与古物研究者中的成员，但没有将该群体命名为学院或机构。"
            "第4、5、7、10、13章的姓氏提及主要处于书目引注语境，作为跨章对齐线索，不在此扩写为传记事实。"
            "相关人际及群体断言留待S6审查。中文名为本项目工作译名。"
        ),
        "description_en": (
            "On p. 348, chapter 14 gives Giovanni Bottari's full name and says that Algarotti met him soon "
            "after arriving in Rome and began a lifelong correspondence with him. The same passage places "
            "Bottari among a group of scholars and antiquarians in Rome but does not name that group as an "
            "academy or institution. Surname mentions in chapters 4, 5, 7, 10, and 13 are chiefly in "
            "bibliographic citations; they serve as cross-chapter alignment traces and are not expanded "
            "here into biographical claims. The person and group assertions await S6 review. The Chinese "
            "name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp14-p348-bottari-correspondence",
            "st-chp14-p348-roman-scholars",
        ],
    },
    {
        "candidate": "cand-0247",
        "group": "new-person:barocci-federico-c04914b5a3",
        "ku": "units/persons/federico-barocci",
        "name_zh": "费德里科·巴罗奇",
        "name_en": "Federico Barocci",
        "index_entry": "B.csv#94",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
        "index_quote": "Barocci, Federico",
        "sources": [
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "location": "第2章，印刷页26，Markdown L56–58",
                "summary": "Haskell称Maffeo Barberini曾请求Barocci为其私人房间送画；原文将姓名跨行排印，并明确记述为请求。",
                "line_start": 56,
                "line_end": 58,
                "span": "Markdown lines 56–58; print p. 26",
            },
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "location": "第3章，印刷页69，Markdown L49",
                "summary": "Haskell称1582年Oratorians委托Federico Barocci为Visitation小堂创作祭坛画，并记述其后续作品请求。",
                "line_start": 49,
                "line_end": 49,
                "span": "Markdown line 49; print p. 69",
            },
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "location": "第3章，印刷页76，Markdown L142",
                "summary": "Haskell以Barocci为较早的参照，比较Borromini对特定反宗教改革感受性的表达；此处记录的是作者的艺术比较，不是二人的传记关系。",
                "line_start": 142,
                "line_end": 142,
                "span": "Markdown line 142; print p. 76",
            },
        ],
        "description_zh": (
            "第2章称Maffeo Barberini曾请求Federico Barocci为其私人房间送画；原文记录的是请求，不据此推断画作已经送达或完成。"
            "第3章称Oratorians于1582年委托Barocci为Visitation小堂创作祭坛画，并希望取得更多作品；同章还将Borromini与Barocci"
            "相隔多年并置，比较二人对特定反宗教改革感受性的表达。委托、作品及比较断言留待S6逐条审查。"
            "中文名为本项目工作译名。"
        ),
        "description_en": (
            "Chapter 2 says Maffeo Barberini asked Federico Barocci to send a picture for his private "
            "apartments; the passage records a request and does not establish that a picture was sent or "
            "completed. Chapter 3 says the Oratorians commissioned Barocci in 1582 for an altarpiece in "
            "the Chapel of the Visitation and wanted further works. The same chapter compares Borromini "
            "with Barocci, many years earlier, as interpreters of a specified Counter-Reformation "
            "sensibility. Commission, work, and comparison assertions await individual S6 review. The "
            "Chinese name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp2-seci-l55-69-barocci-picture-request",
            "st-chp3-secii-l137-142-borromini-barocci-sensibility",
            "st-chp3-secii-l40-52-barocci-painted-commission",
            "st-chp3-secii-l40-52-oratorians-sought-more-barocci",
        ],
    },
    {
        "candidate": "cand-1194",
        "group": "new-person:giulio-romano-864f91350e",
        "ku": "units/persons/giulio-romano",
        "name_zh": "朱利奥·罗马诺",
        "name_en": "Giulio Romano",
        "index_entry": "G.csv#101",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/G.csv",
        "index_quote": "Giulio Romano",
        "sources": [
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "location": "第2章，印刷页30，Markdown L113–115",
                "summary": "Haskell将Giulio Romano列入Cardinal Barberini宫中旧大师绘画的群体性叙述；原文未识别具体作品。",
                "line_start": 113,
                "line_end": 115,
                "span": "Markdown lines 113–115; print p. 30",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "location": "第10章，印刷页312，Markdown L21–23",
                "summary": "Haskell称Giulio Romano与Castiglione曾受Gonzaga家族大量雇用，并将此事置于Schulenburg购入Mantua公爵旧藏的叙述中。",
                "line_start": 21,
                "line_end": 23,
                "span": "Markdown lines 21–23; print p. 312",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "location": "第7章，印刷页186，Markdown L216",
                "summary": "Haskell引述Brienne的法文回忆，其中一幅挂毯设计被写作Jules Romain；S3将该法文形式连到索引人名Giulio Romano，此处仍是被引来源的归属。",
                "line_start": 216,
                "line_end": 216,
                "span": "Markdown line 216; print p. 186",
            },
        ],
        "description_zh": (
            "第2章把Giulio Romano列入Cardinal Barberini宫中旧大师绘画的群体性叙述，没有在该段识别具体作品或逐件归属。"
            "第10章称他与Castiglione曾受Gonzaga家族大量雇用。第7章转引Brienne以法文Jules Romain将挂毯设计归于该名；"
            "本卡依据S3对齐至索引人名，但保留这是被引来源的归属，未作独立作品核验。以上作品及雇佣关系断言留待S6逐条审查。"
            "中文名为本项目工作译名。"
        ),
        "description_en": (
            "Chapter 2 includes Giulio Romano in a group-level account of old-master paintings in Cardinal "
            "Barberini's palace; that passage does not identify individual works or assign each one to "
            "him. Chapter 10 says that he and Castiglione had been much employed by the Gonzaga. Chapter 7 "
            "quotes Brienne attributing a tapestry design to “Jules Romain”; S3 aligns this French form "
            "with the index entry Giulio Romano, while retaining it as an attribution in a quoted source "
            "rather than independent work verification. These work and employment assertions await "
            "individual S6 review. The Chinese name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp10-p312-gonzaga-employed-romano-and-castiglione",
            "st-chp2-seci-l108-119-palace-paintings-by-giulio-romano",
            "st-chp7-p186-i02",
        ],
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
    return "\n".join(lines[item["line_start"] - 1 : item["line_end"]])


def make_card(t: dict) -> str:
    sources = []
    for item in t["sources"]:
        sources.append(
            {
                "citation": BOOK_CITATION,
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [
                    {
                        "source_span": f"Markdown lines {item['line_start']}–{item['line_end']}",
                        "text": source_quote(item),
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": item["file"],
                    "source_span": item["span"],
                },
            }
        )
    sources.append(
        {
            "citation": INDEX_CITATION,
            "location": f"全书索引 {t['index_entry']}",
            "sentence_summary": f"索引主条目列出“{t['index_quote']}”。",
            "original_quotes": [{"source_span": t["index_entry"], "text": t["index_quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": t["index_file"],
                "source_span": t["index_entry"],
            },
        }
    )
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
    locations = "；".join(item["location"] for item in t["sources"])
    relation_ids = "、".join(t["relation_ids"])
    count = len(t["relation_ids"])
    return (
        f"---\n{fm}---\n\n"
        "## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}（{locations}）\n\n"
        f"**English:** {t['description_en']} ({locations})\n\n"
        "## 关系与证据\n\n### 关系登记\n\n"
        f"目前尚无 relations.csv 中的正式关系。S2 标记为直接关系候选的 {count} 条断言 "
        f"({relation_ids}) 留待 S6 逐条审查；S4 登记不预先将其确认为关系。\n"
    )


def insert_accepted(lines: list[str], card_rel: str) -> list[str]:
    entry = f"- {card_rel}"
    assert entry not in lines
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    insert_at = claims_idx
    for i in range(units_idx + 1, claims_idx):
        if lines[i].startswith("- ") and lines[i][2:] > card_rel:
            insert_at = i
            break
    lines.insert(insert_at, entry)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Register three reviewed cross-chapter person groups in S4.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    align_by = {
        r["candidate_id"]: r
        for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    candidate_by = {r["candidate_id"]: r for r in candidates}
    manifest_by = {r["ku_id"]: r for r in manifest}
    statement_data = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statements = {d["statement_id"]: d for d in statement_data}

    planned_alignments = [dict(r) for r in alignments]
    planned_align_by = {
        r["candidate_id"]: r
        for r in planned_alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    planned_manifest = [dict(r) for r in manifest]
    accepted_lines = read_text(ACCEPTED_PATH).splitlines()
    cards: dict[Path, str] = {}

    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before_totals = sync.build_type_table(before_stats)
    relation_total = 0

    for t in TARGETS:
        cid, group, ku = t["candidate"], t["group"], t["ku"]
        assert cid in candidate_by and cid in align_by
        c, a = candidate_by[cid], planned_align_by[cid]
        assert c["suggested_type"] == "person"
        assert a["decision"] == "new" and not a.get("ku_id")
        assert sync.get_group(a.get("resolution_note", "")) == group
        group_members = [
            r["candidate_id"]
            for r in alignments
            if r.get("candidate_id")
            and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == group
        ]
        assert group_members == [cid], f"unexpected group members for {group}: {group_members}"
        assert ku not in manifest_by
        card_path = ROOT / f"04-knowledge/{ku}.md"
        assert not card_path.exists()
        assert f"- 04-knowledge/{ku}.md" not in accepted_lines
        assert not any(
            r.get("name_en", "").casefold() == t["name_en"].casefold()
            for r in manifest
            if r["type"] == "person"
        ), f"same-name person KU already exists: {t['name_en']}"
        for item in t["sources"]:
            quote = source_quote(item)
            assert quote and quote in (ROOT / item["file"]).read_text(encoding="utf-8-sig")
        index_text = (ROOT / t["index_file"]).read_text(encoding="utf-8-sig")
        assert t["index_quote"] in index_text, f"index name missing: {t['index_entry']}"
        for sid in t["relation_ids"]:
            assert sid in statements
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
        relation_total += len(t["relation_ids"])
        cards[card_path] = make_card(t)
        a["ku_id"] = ku
        a["process_ref"] = PROCESS_REF
        count = len(t["relation_ids"])
        a["resolution_note"] += (
            f" S4 registration ({DATE}): mapped {group} to {ku}; source-specific identity and "
            f"cross-chapter anchors are retained. {count} direct relation candidates remain pending S6."
        )
        planned_manifest.append(
            {
                "ku_id": ku,
                "type": "person",
                "canonical_name": f"{t['name_zh']}（{t['name_en']}）",
                "name_en": t["name_en"],
                "source_task": TASK,
                "card_path": f"04-knowledge/{ku}.md",
            }
        )

    planned_manifest.sort(key=lambda r: r["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")
    stats = sync.summarize_by_type(candidate_by.values(), planned_alignments)
    _, totals = sync.build_type_table(stats)
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    process_text = read_text(PROCESS_PATH)
    anchor = '<a id="s4-person-endpoints-20261017h"></a>'
    assert anchor not in process_text
    process_text += (
        "\n\n"
        + anchor
        + "\n\n### S4 person：Giovanni Bottari、Federico Barocci 与 Giulio Romano 登记（2026-10-17）\n\n"
    )
    process_text += (
        f"按 S3 的三个跨章 person new 身份组各登记一个 KU，共保留 {relation_total} 条直接关系候选供 S6 审查；"
        "没有把来源中的请求、群体性作品归属、艺术比较或转引归属提升为正式关系。Bottari 的跨章姓氏命中主要是书目引注，"
        "以第14章 p.348 的全名和关系上下文作为卡片依据；Barocci 的英文全名跨行出现，由正文其他页及索引相互支持；"
        "Giulio Romano 的法文异名 Jules Romain 按 S3 与索引主条目对齐，Brienne 的作品归属仍为被引来源的说法。"
        "未引入外部身份或传记资料。\n\n"
    )
    process_text += "| 候选 / S3 身份组 | KU | 跨章来源与索引锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
    for t in TARGETS:
        locations = "；".join(item["location"] for item in t["sources"])
        process_text += (
            f"| {t['candidate']} / {t['group']} | {t['ku']} | {locations}；索引 {t['index_entry']} | "
            f"{len(t['relation_ids'])} |\n"
        )
    process_text += "\n"
    result_text += (
        "\n\n### S4 person：Giovanni Bottari、Federico Barocci 与 Giulio Romano 登记（2026-10-17）\n\n"
    )
    for t in TARGETS:
        result_text += (
            f"- {t['candidate']}：[{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)；"
            f"{t['index_entry']}；{len(t['relation_ids'])} 条直接关系候选留待 S6。\n"
        )
    result_text += "\n本批保留各来源的范围与归属限定，未登记正式关系或外部身份标识。\n"

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert relation_total == 9

    if args.dry_run:
        print(
            f"DRY-RUN OK: groups={len(TARGETS)}; cards={len(cards)}; "
            f"direct relation candidates={relation_total}"
        )
        print(
            f"manifest: {len(manifest):,}->{len(planned_manifest):,}; "
            f"registered groups: {before_totals['registered_groups']:,}->{totals['registered_groups']:,}; "
            f"pending groups: {before_totals['pending_groups']:,}->{totals['pending_groups']:,}; "
            f"pending candidate mappings: {before_totals['pending_members']:,}->{totals['pending_members']:,}"
        )
        return

    for path, card in cards.items():
        path.write_bytes(card.encode("utf-8"))
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(
        f"APPLIED: groups={len(TARGETS)}; person KUs={len(cards)}; "
        f"manifest={len(planned_manifest):,}; registered groups={totals['registered_groups']:,}; "
        f"pending groups={totals['pending_groups']:,}"
    )


if __name__ == "__main__":
    main()
