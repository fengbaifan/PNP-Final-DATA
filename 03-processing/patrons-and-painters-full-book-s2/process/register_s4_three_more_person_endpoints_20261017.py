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
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017g"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-1726",
        "group": "new-person:gabriel-naude-260f2e8c57",
        "ku": "units/persons/gabriel-naude",
        "name_zh": "加布里埃尔·诺代",
        "name_en": "Gabriel Naudé",
        "index_entry": "N.csv#6",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/N.csv",
        "index_quote": "Naudé, Gabriel",
        "sources": [
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "location": "第2章，印刷页33，Markdown L27–28",
                "summary": "Haskell以“French disbeliever”引出一段法文引语；同页注3将说话者标为Gabriel Naudé。",
                "line_start": 27,
                "line_end": 28,
                "span": "Markdown lines 27–28; print p. 33",
            },
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "location": "第2章，注3，Markdown L155",
                "summary": "注3将前文法国说话者归引为Gabriel Naudé，并说明引文转引自Pintard。",
                "line_start": 155,
                "line_end": 155,
                "span": "Markdown line 155; note 3 to print p. 33",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "location": "第4章，印刷页107，Markdown L106–107",
                "summary": "Haskell将Gabriel Naudé列入法国libertins，并称他们属于Cassiano的亲密朋友。",
                "line_start": 106,
                "line_end": 107,
                "span": "Markdown lines 106–107; print p. 107",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "location": "第4章，印刷页108–109，Markdown L117–120",
                "summary": "Haskell称Naudé是Cassiano的好友，并说他为Cassiano收藏中的肖像撰写拉丁铭文。",
                "line_start": 117,
                "line_end": 120,
                "span": "Markdown lines 117–120; print pp. 108–109",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "location": "第7章，印刷页177，Markdown L95",
                "summary": "Haskell转述Naudé在1638年对部分绘画可能流向Lord Arundel的判断。",
                "line_start": 95,
                "line_end": 95,
                "span": "Markdown line 95; print p. 177",
            },
        ],
        "description_zh": (
            "Haskell在第2章通过注3将“法国怀疑者”的引语归于Gabriel Naudé；第4章称Naudé等人为Cassiano的亲密朋友，"
            "并称Naudé是Cassiano的好友、曾为其收藏中的肖像撰写拉丁铭文；第7章转述Naudé在1638年对部分绘画可能流向"
            "Lord Arundel的判断。以上身份和语境均按书中转述记录，涉及人物或作品的断言留待S6逐条审查。"
            "中文名为本项目工作译名。"
        ),
        "description_en": (
            "Haskell identifies the speaker of a French quotation in chapter 2 as Gabriel Naudé in note 3. "
            "Chapter 4 names Naudé among the French libertins, describes them as close friends of Cassiano, "
            "calls Naudé Cassiano's great friend, and says Naudé wrote Latin inscriptions for portraits in "
            "Cassiano's collection. Chapter 7 reports Naudé's 1638 expectation that some pictures might go "
            "to Lord Arundel. These are recorded as Haskell's account; person and work assertions await "
            "individual S6 review. The Chinese name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp2-sec-ii-l20-28-naude-french-quotation",
            "st-chp4-sec-ii-l109-119-naude-alternative-response",
            "st-chp4-sec-ii-l109-119-portraits-naude-fragment",
            "st-chp7-p177-i09",
        ],
    },
    {
        "candidate": "cand-2107",
        "group": "new-person:giorgio-maria-rapparini-2fa43bcc34",
        "ku": "units/persons/giorgio-maria-rapparini",
        "name_zh": "乔治奥·玛丽亚·拉帕里尼",
        "name_en": "Giorgio Maria Rapparini",
        "index_entry": "Q-R.csv#34",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
        "index_quote": "Rapparini, Giorgio Maria",
        "sources": [
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "location": "第10章，印刷页282，Markdown L142–143",
                "summary": "Haskell称Rapparini为选侯Johann Wilhelm的朝臣，叙述他引导选侯赞助活动，并说明他是画家、作家且曾在罗马师从Carlo Maratta。OCR在行末与下一词间连写姓名；索引主条目分开书写。",
                "line_start": 142,
                "line_end": 143,
                "span": "Markdown lines 142–143; print p. 282",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "location": "第10章，注1，Markdown L520",
                "summary": "Haskell说明Rapparini的颂词写于1709年，因此没有提及Pellegrini；并说明所引文字取自其手稿出版本。",
                "line_start": 520,
                "line_end": 520,
                "span": "Markdown line 520; note 1 to print p. 282",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "location": "第10章，印刷页283，Markdown L153",
                "summary": "Haskell评价Rapparini对Van Dyck与Rubens的说法，并将其置于选侯画廊的叙述中。",
                "line_start": 153,
                "line_end": 153,
                "span": "Markdown line 153; print p. 283",
            },
        ],
        "description_zh": (
            "第10章将Giorgio Maria Rapparini称为Johann Wilhelm选侯的一名朝臣。Haskell转述Rapparini关于选侯的颂词，"
            "并称Rapparini引导选侯的赞助活动，既是画家也是作家，曾在罗马师从Carlo Maratta。"
            "第282页OCR将姓名连写为“Giorgio MariaRapparini”；索引主条目为“Rapparini, Giorgio Maria”，"
            "本卡按索引分词呈现姓名，原文引句保留OCR形式。相关归属和引述断言留待S6逐条审查。中文名为本项目工作译名。"
        ),
        "description_en": (
            "Chapter 10 identifies Giorgio Maria Rapparini as a courtier of Elector Johann Wilhelm. Haskell "
            "quotes Rapparini's eulogy of the Elector and says Rapparini guided his patronage, was both a "
            "painter and a writer, and had studied under Carlo Maratta in Rome. The p. 282 OCR joins the "
            "name as “Giorgio MariaRapparini”; the index main entry separates it as “Rapparini, Giorgio "
            "Maria.” The card follows the index form while preserving the source transcription in its quote. "
            "Attributed statements await individual S6 review. The Chinese name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp10-notes-p282n1-eulogy-1709-no-pellegrini",
            "st-chp10-p282-rapparini-alexander-comparison",
            "st-chp10-p282-rapparini-apotheosis",
            "st-chp10-p282-rapparini-guided-study",
        ],
    },
    {
        "candidate": "cand-2694",
        "group": "new-person:ottavio-vannini-9f4cacf09c",
        "ku": "units/persons/ottavio-vannini",
        "name_zh": "奥塔维奥·万尼尼",
        "name_en": "Ottavio Vannini",
        "index_entry": "UVWXYZ.csv#30",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "index_quote": "Vannini, Ottavio",
        "sources": [
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "location": "第8章，印刷页212，Markdown L99–101",
                "summary": "Haskell称Vannini为Del Rosso家族礼拜堂壁画的作者和家族画家，记述其去世及留给学生完成的祭坛画，并列出为该家族创作的四幅旧约场景；对其画风的评价保留为Haskell的判断。",
                "line_start": 99,
                "line_end": 101,
                "span": "Markdown lines 99–101; print p. 212",
            },
        ],
        "description_zh": (
            "Haskell称Ottavio Vannini为Del Rosso家族礼拜堂壁画的作者和该家族的画家，称他一年后去世并留下祭坛画由学生完成；"
            "又将四幅旧约场景及其他绘画归于他，并记述相关作品在家族中的位置。其关于画风和作品评价的文字保留为Haskell的判断。"
            "人物、作品及委托关系候选均留待S6逐条审查。中文名为本项目工作译名。"
        ),
        "description_en": (
            "Haskell names Ottavio Vannini as the painter of frescoes in the Del Rosso family chapel and as "
            "the family's painter. He says Vannini died the following year, leaving an altar picture for a "
            "pupil to complete, and attributes four Old Testament scenes and other pictures to him. "
            "Evaluative statements about his style and works remain attributed to Haskell. Person, work, "
            "and commission assertions await individual S6 review. The Chinese name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp8-p212-altar-picture-left-for-pupil-completion",
            "st-chp8-p212-chapel-decorated-with-vannini-frescoes",
            "st-chp8-p212-four-scenes-made-for-house-and-considered-finest",
            "st-chp8-p212-vannini-style-and-florentine-disegno-assessment",
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
    parser = argparse.ArgumentParser(description="Register three reviewed person groups in S4.")
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
            f" S4 registration ({DATE}): mapped {group} to {ku}; bilingual card preserves the "
            f"book and index anchors. {count} direct relation candidates remain pending S6."
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
    anchor = '<a id="s4-person-endpoints-20261017g"></a>'
    assert anchor not in process_text
    process_text += (
        "\n\n"
        + anchor
        + "\n\n### S4 person：Gabriel Naudé、Giorgio Maria Rapparini 与 Ottavio Vannini 登记（2026-10-17）\n\n"
    )
    process_text += (
        f"按 S3 的三个 person new 单人组各登记一个 KU，共保留 {relation_total} 条已标记的直接关系候选供 S6 审查；"
        "本批没有将候选断言写入正式关系。Naudé 的跨章姓名锚点由第2、4、7章及索引互相支持；"
        "Rapparini 第282页姓名在 OCR 转录中连写，索引主条目提供分词形式，原引句保留原转录；"
        "Vannini 的记录限定于第8章所载家族礼拜堂、作品与作者评价。未引入外部身份或传记资料。\n\n"
    )
    process_text += "| 候选 / S3 身份组 | KU | 来源与索引锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
    for t in TARGETS:
        locations = "；".join(item["location"] for item in t["sources"])
        process_text += (
            f"| {t['candidate']} / {t['group']} | {t['ku']} | {locations}；索引 {t['index_entry']} | "
            f"{len(t['relation_ids'])} |\n"
        )
    process_text += "\n"
    result_text += (
        "\n\n### S4 person：Gabriel Naudé、Giorgio Maria Rapparini 与 Ottavio Vannini 登记（2026-10-17）\n\n"
    )
    for t in TARGETS:
        result_text += (
            f"- {t['candidate']}：[{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)；"
            f"{t['index_entry']}；{len(t['relation_ids'])} 条直接关系候选留待 S6。\n"
        )
    result_text += "\nRapparini 姓名的 OCR 连写已在卡片中保留并注明索引分词依据；本批未登记正式关系或外部身份标识。\n"

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert relation_total == 12

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
