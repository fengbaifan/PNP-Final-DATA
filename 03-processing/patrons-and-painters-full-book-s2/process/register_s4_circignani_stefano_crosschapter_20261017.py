from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-circignani-stefano-crosschapter-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SPECS = [
    {
        "candidate": "cand-1970",
        "group": "new-person:circignani-dalle-niccolo-pomarance-f260aa2103",
        "type": "person",
        "ku": "units/persons/niccolo-circignani-dalle-pomarance",
        "card": "04-knowledge/units/persons/niccolo-circignani-dalle-pomarance.md",
        "name_zh": "尼科洛·奇尔奇尼亚尼",
        "name_en": "Niccolò Circignani dalle Pomarance",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 67.",
                "location": "第3章，印刷页67；OCR L19–22。",
                "summary": "哈斯克尔称未具名校长委托 Nicolo Circignani dalle Pomarance 制作 S. Stefano Rotondo 的壁画组。",
                "quotes": [("lines 21–22; print p. 67", "Nicolo Circignani dalle Pomarance")],
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "span": "lines 19–22; print p. 67",
            },
            {
                "citation": f"{BOOK_CITATION}, index, s.v. Pomarance.",
                "location": "书后索引，P.csv#171；所列页码67、399。",
                "summary": "索引将 Pomarance, Niccolò Circignani dalle 与第3章及后记页码相连。",
                "quotes": [("P.csv#171", "Pomarance, Niccolò Circignani dalle")],
                "doc_id": "patrons-and-painters-index",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
                "span": "P.csv#171",
            },
            {
                "citation": f"{BOOK_CITATION}, postscript, p. 399.",
                "location": "后记，印刷页399；OCR L40–42。",
                "summary": "哈斯克尔后记再次将 S. Stefano Rotondo 的殉道场景称为 Circignani 所画，并以同组壁画讨论Thomas Buser的比较。",
                "quotes": [("lines 40–41; print p. 399", "painted by Circignani in the Jesuit church of S. Stefano Rotondo")],
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "span": "lines 40–42; print p. 399",
            },
        ],
        "body_zh": (
            "本卡记录书后索引所列 Niccolò Circignani dalle Pomarance，以及第3章正文称作 Nicolo Circignani dalle Pomarance、"
            "后记简称 Circignani 的画家身份。第3章称一位未具名校长委托他制作 S. Stefano Rotondo 的殉道题材壁画；"
            "后记 p.399 再次以 Circignani 指称该组壁画。章间身份对应以索引页码和正文互文为依据；不补写生卒、籍贯或其他外部生平。"
        ),
        "body_en": (
            "This card records the painter indexed as Niccolò Circignani dalle Pomarance, named in Chapter 3 as Nicolo Circignani dalle Pomarance, "
            "and referred to as Circignani in the postscript. Chapter 3 says an unnamed rector commissioned him to make the martyrdom frescoes at S. Stefano Rotondo; "
            "the postscript again identifies that cycle as painted by Circignani. The cross-chapter identity rests on the index locator and the book’s repeated reference; "
            "no dates, birthplace, or other external biography are added."
        ),
        "section": "### 人物身份",
        "boundary": "原书中的画家姓名与称名，不扩写为外部传记。",
        "boundary_en": "The painter’s source-local name and forms of reference, without an external biography.",
    },
    {
        "candidate": "cand-10924",
        "group": "sg3-place-cand-10924",
        "type": "place",
        "ku": "units/places/s-stefano-rotondo-rome",
        "card": "04-knowledge/units/places/s-stefano-rotondo-rome.md",
        "name_zh": "罗马圣斯特凡诺圆形堂",
        "name_en": "Church of S. Stefano Rotondo, Rome",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 67.",
                "location": "第3章，印刷页67；OCR L19–22。",
                "summary": "哈斯克尔将 S. Stefano Rotondo 称为耶稣会分得的一座早期基督教建筑，并叙述其中的 Circignani 壁画。",
                "quotes": [("lines 19–20; print p. 67", "the venerable early Christian temple of S. Stefano Rotondo")],
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "span": "lines 19–22; print p. 67",
            },
            {
                "citation": f"{BOOK_CITATION}, postscript, p. 399.",
                "location": "后记，印刷页399；OCR L40–42。",
                "summary": "后记将 Circignani 的殉道壁画定位于耶稣会教堂 S. Stefano Rotondo。",
                "quotes": [("lines 40–41; print p. 399", "in the Jesuit church of S. Stefano Rotondo")],
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "span": "lines 40–42; print p. 399",
            },
        ],
        "body_zh": (
            "本卡记录第3章及后记共同指称的罗马 S. Stefano Rotondo 教堂建筑。第3章称其为耶稣会分得的一座早期基督教建筑；"
            "后记称 Circignani 的殉道壁画位于该耶稣会教堂。教堂建筑为 place，壁画组为独立 work；本卡不补写现代地址、建筑沿革或现存状况。"
        ),
        "body_en": (
            "This card records the church building in Rome referred to in both Chapter 3 and the postscript as S. Stefano Rotondo. "
            "Chapter 3 calls it an early Christian building allotted to the Jesuits; the postscript places Circignani’s martyrdom frescoes in that Jesuit church. "
            "The church is a place and the fresco cycle is a separate work. No modern address, building history, or present condition is added."
        ),
        "section": "### 建筑地点身份",
        "boundary": "教堂建筑地点；殉道壁画组另作为 work，不与建筑合并。",
        "boundary_en": "The church building as a place; its martyrdom fresco cycle is a separate work.",
    },
    {
        "candidate": "cand-5020",
        "group": "sg3-institution-cand-5020",
        "type": "institution",
        "ku": "units/institutions/late-roman-empire",
        "card": "04-knowledge/units/institutions/late-roman-empire.md",
        "name_zh": "晚期罗马帝国",
        "name_en": "Late Roman Empire",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 67.",
                "location": "第3章，印刷页67；OCR L22。",
                "summary": "哈斯克尔称壁画组呈现的早期基督教殉道事件大多发生于晚期罗马帝国时期。",
                "quotes": [("line 22; print p. 67", "mostly enacted under the late Roman empire")],
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "span": "line 22; print p. 67",
            },
        ],
        "body_zh": (
            "本卡按 S3 的 institution 分类，记录原书明确命名的晚期罗马帝国政治实体。哈斯克尔将壁画组描绘的早期基督教殉道事件限定为“大多”发生于该语境；"
            "本卡保留这一范围限定，不补写政体边界、年代分期或个别殉道事件。"
        ),
        "body_en": (
            "This card records the source-named Late Roman Empire under the S3 institution classification. Haskell places the early Christian martyrdoms depicted in the cycle mostly in this setting. "
            "The qualification “mostly” is retained; no political boundaries, period dates, or individual martyrdoms are added."
        ),
        "section": "### 政治实体身份",
        "boundary": "原书用作殉道事件语境的政治实体；“大多”保留为范围限定。",
        "boundary_en": "The political entity used as the setting for the martyrdoms; the source’s “mostly” qualification is retained.",
    },
    {
        "candidate": "cand-5019",
        "group": "workgrp-859c21d6ba4ca9",
        "type": "work",
        "ku": "units/works/circignani-martyrdom-fresco-cycle-s-stefano-rotondo",
        "card": "04-knowledge/units/works/circignani-martyrdom-fresco-cycle-s-stefano-rotondo.md",
        "name_zh": "圣斯特凡诺圆形堂殉道题材壁画组",
        "name_en": "Circignani’s Martyrdom Fresco Cycle at S. Stefano Rotondo",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 67.",
                "location": "第3章，印刷页67；OCR L21–22。",
                "summary": "哈斯克尔称未具名校长委托 Circignani 创作一组详细壁画，表现早期基督教圣徒殉道；原书称事件大多发生于晚期罗马帝国，并称每幅壁画附有酷刑说明。",
                "quotes": [
                    ("lines 21–22; print p. 67", "a series of exceedingly brutal frescoes designed to illustrate the martyrdoms of early Christian saints"),
                    ("line 22; print p. 67", "mostly enacted under the late Roman empire"),
                    ("line 22; print p. 67", "the explanation of the torture was attached to each fresco"),
                ],
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "span": "lines 21–22; print p. 67",
            },
            {
                "citation": f"{BOOK_CITATION}, postscript, p. 399.",
                "location": "后记，印刷页399；OCR L40–42。",
                "summary": "哈斯克尔后记以 Circignani 的 S. Stefano Rotondo 殉道场景回指第3章壁画组，并转述 Thomas Buser 关于图像的教诲意图和形式、而非具体构图的比较。",
                "quotes": [("lines 40–41; print p. 399", "the horrific scenes of martyrdom painted by Circignani in the Jesuit church of S. Stefano Rotondo")],
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "span": "lines 40–42; print p. 399",
            },
        ],
        "body_zh": (
            "本卡记录 Circignani 为 S. Stefano Rotondo 创作的殉道题材壁画组。第3章称一位未具名校长委托其创作，画面以早期基督教圣徒殉道为题材，"
            "事件大多发生在晚期罗马帝国时期，且每幅壁画附有酷刑说明。哈斯克尔在后记 p.399 再次以 Circignani 和 S. Stefano Rotondo 指称该组壁画；"
            "他转述 Thomas Buser 将图像的教诲意图与形式同耶稣会 Jerome Nadal 的福音默想图书相比较，同时明确不是具体构图的影响。此处是哈斯克尔对 Buser 的转述，未独立核阅 Buser 原文。"
            "壁画组为 work，与[圣斯特凡诺圆形堂建筑](../places/s-stefano-rotondo-rome.md)分开。"
        ),
        "body_en": (
            "This unit records Circignani’s martyrdom fresco cycle at S. Stefano Rotondo. Chapter 3 says an unnamed rector commissioned the cycle; its subjects are early Christian martyrs, "
            "mostly in the Late Roman Empire, and each fresco had an explanation of its torture. In the postscript, p. 399, Haskell again identifies the cycle through Circignani and S. Stefano Rotondo. "
            "He reports Thomas Buser’s comparison of its didactic intent and format with Jerome Nadal’s Jesuit book of gospel meditations, while explicitly excluding influence on the actual compositions. "
            "This is Haskell’s report of Buser; Buser’s original text was not independently consulted. The frescoes are a work, separate from the [church building](../places/s-stefano-rotondo-rome.md)."
        ),
        "section": "### 作品身份",
        "boundary": "壁画组为 work；教堂建筑、晚期罗马帝国政治实体及各条正式关系均分别记录。",
        "boundary_en": "The fresco cycle is a work; the church building, Late Roman Empire, and formal relations are recorded separately.",
    },
]

RELATION_STATEMENTS = {
    "st-chp3-secii-l19-31-jesuits-pride-in-innovation",
    "st-chp3-secii-l19-31-rector-commissioned-stefano-cycle",
    "st-chp3-secii-l19-31-stefano-cycle-martyrdoms-setting",
    "st-chp3-secii-l19-31-venetian-tradition-in-subjects",
    "st-chp3-secii-p67-note2-necrology-claim",
    "st-chp3-secii-l19-31-stefano-torture-explanations-attached",
}


def make_card(spec: dict) -> str:
    sources = []
    for item in spec["sources"]:
        sources.append({
            "citation": item["citation"],
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": item["doc_id"],
                "source_file": item["source_file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{spec['name_zh']}（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": spec["type"],
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

{spec['section']}

**中文：** {spec['body_zh']}

**English:** {spec['body_en']}

### 对象边界

**中文：** {spec['boundary']}

**English:** {spec['boundary_en']}

## 关系与证据

当前没有已登记的正式关系。相关 S2 关系候选留待 S6 核对端点、方向、语境和证据；本次不将断言转换为关系边，不新增 S5 enrichment。
"""


def insert_accepted_paths(text: str, card_paths: list[str]) -> str:
    lines = text.splitlines()
    for card_path in sorted(card_paths):
        assert f"- {card_path}" not in lines
        insert_at = next(
            (
                i for i, line in enumerate(lines)
                if line.startswith("- 04-knowledge/units/") and line[2:] > card_path
            ),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_path}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Circignani person, place, polity, and work groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    manifest_by_ku = {row.get("ku_id"): row for row in manifest}

    for spec in SPECS:
        cid = spec["candidate"]
        assert candidate_map[cid].get("suggested_type") == spec["type"]
        decision = decisions[cid]
        assert decision.get("decision") == "new" and not decision.get("ku_id")
        assert sync.get_group(decision.get("resolution_note", "")) == spec["group"]
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new" and not row.get("ku_id")
            and sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert members == [cid], (spec["group"], members)
        assert spec["card"] not in accepted_text
        assert not (ROOT / spec["card"]).exists()
        assert not any(row.get("ku_id") == spec["ku"] or row.get("card_path") == spec["card"] for row in manifest)
        assert not any(
            row.get("type") == spec["type"]
            and row.get("name_en", "").casefold() == spec["name_en"].casefold()
            for row in manifest
        ), f"duplicate type/name for {cid}"

    all_quotes = [
        (item["source_file"], quote)
        for spec in SPECS for item in spec["sources"] for _, quote in item["quotes"]
    ]
    for source_file, quote in all_quotes:
        source = " ".join((ROOT / source_file).read_text(encoding="utf-8-sig").split())
        assert " ".join(quote.split()) in source, (source_file, quote)

    _, mentions = sync.read_csv(TABLES / "mentions.csv")
    mention_by_id = {row["mention_id"]: row for row in mentions}
    assert mention_by_id["m-chp3-secii-l19-31-0007"].get("candidate_id") == "cand-5019"
    assert mention_by_id["m-chp20-p399-019"].get("candidate_id") == "cand-5019"
    assert mention_by_id["m-chp20-p399-024"].get("candidate_id") == "cand-5019"
    assert mention_by_id["m-chp20-p399-020"].get("candidate_id") == "cand-1970"
    assert decisions["cand-5017"].get("decision") == "undecided"
    assert decisions["cand-5018"].get("decision") == "undecided"
    assert decisions["cand-4319"].get("decision") == "undecided"
    assert decisions["cand-5147"].get("decision") == "undecided"
    assert decisions["cand-12311"].get("decision") == "undecided"

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    assert RELATION_STATEMENTS.issubset(statements)
    assert all(statements[sid].get("qualifiers", {}).get("relation_candidate") is True for sid in RELATION_STATEMENTS)
    artist_edge = statements["st-chp3-secii-l19-31-rector-commissioned-stefano-cycle"]
    assert artist_edge.get("qualifiers", {}).get("commissioned_artist_candidate_id") == "cand-1970"

    planned_alignment = [dict(row) for row in alignments]
    for spec in SPECS:
        matched = [
            row for row in planned_alignment
            if row.get("candidate_id") == spec["candidate"] and not row.get("external_source")
        ]
        assert len(matched) == 1
        matched[0]["ku_id"] = spec["ku"]
        matched[0]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        matched[0]["resolution_note"] += (
            f" S4 registration: cross-chapter source-backed {spec['type']} group "
            f"{spec['group']} maps to {spec['ku']}; remaining unresolved identities and formal relations stay pending."
        )

    planned_manifest = list(manifest)
    for spec in SPECS:
        planned_manifest.append({
            "ku_id": spec["ku"],
            "type": spec["type"],
            "canonical_name": spec["name_zh"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": spec["card"],
        })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    mapped = "；".join(
        f"`{s['candidate']}`（{s['group']}）→ [{s['name_zh']}](../../../{s['card']})"
        for s in SPECS
    )
    unresolved = "、".join(["cand-5017 German College", "cand-5018 未具名校长", "cand-4319 Venetian High Renaissance tradition", "cand-5147 Lauretano", "cand-12311 未分类的说明文字组"])
    process_text += f"""

<a id="{ANCHOR}"></a>

### S4 跨章：Circignani 与 S. Stefano Rotondo 殉道壁画组身份登记（{DATE}）

本次按各自 S3 身份组登记四个对象：{mapped}。第3章 p.67 将一组早期基督教殉道壁画归于 Niccolò Circignani dalle Pomarance，并称一位未具名校长委托其创作；后记 p.399 再以 Circignani 指称 S. Stefano Rotondo 的同组殉道场景。索引 P.csv#171 将人物条目连至 p.67 与 p.399，支持人名和跨章身份对应。作品、画家、教堂地点和 Late Roman Empire 政治实体分别登记，不合并为同一 KU。

第20章通过哈斯克尔转述 Thomas Buser 对教诲意图和形式的比较，不把它写成图像构图的直接来源；未独立查阅 Buser 原文。六条 S2 关系候选 `{', '.join(sorted(RELATION_STATEMENTS))}` 留待 S6。其余未决对象保留原 S3 去向：{unresolved}；不因四项登记而提升为已知端点。未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_note = (
        f"\n\n### S4 跨章：Circignani 与 S. Stefano Rotondo 殉道壁画组（{DATE}）\n\n"
        f"按四个独立 S3 身份组登记画家、教堂地点、晚期罗马帝国政治实体与殉道壁画 work。"
        "第3章 p.67 与后记 p.399 的人名、作品称谓及索引 P.csv#171 支持跨章对应；Haskell 对 Buser 的转述与其限定保留为转述。"
        "未具名校长、German College、Lauretano、Venetian High Renaissance tradition 与未分类说明文字仍按原状态待证；六条关系候选留待 S6。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    result_text = result_text.rstrip() + result_note
    planned_accepted = insert_accepted_paths(accepted_text, [spec["card"] for spec in SPECS])
    cards = [(ROOT / spec["card"], make_card(spec)) for spec in SPECS]

    if args.dry_run:
        print("dry-run passed: four singleton S3 groups are new and have distinct person/place/institution/work destinations")
        print("verified chapter 3 p.67, postscript p.399, index P.csv#171, and all quoted source spans")
        print("cross-chapter work mentions map to cand-5019; artist alias maps to cand-1970")
        print(f"S6 relation candidates preserved: {len(RELATION_STATEMENTS)}; undecided endpoint groups preserved: 5")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; all accepted paths unique")
        print("planned writes: four bilingual cards, accepted.yml, ku-manifest.csv, four alignment mappings, process record, result")
        return 0

    for path, content in cards:
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: 4 S4 groups; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
