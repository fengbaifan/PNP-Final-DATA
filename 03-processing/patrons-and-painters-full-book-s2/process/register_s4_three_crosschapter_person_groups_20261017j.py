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
ANCHOR = "s4-person-endpoints-20261017j"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-1524",
        "group": "new-person:carlo-ferdinando-mantua-of-66e2b330e3",
        "ku": "units/persons/ferdinando-carlo-gonzaga",
        "name_zh": "费迪南多·卡洛·贡扎加",
        "name_en": "Ferdinando Carlo Gonzaga",
        "index_entry": "M.csv#61",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "index_quote": "Mantua, Ferdinando Carlo, Duke of",
        "index_span": "M.csv#61; index row 63; pp. 267, 312",
        "chapters": "第9、10章；索引 M.csv#61",
        "sources": [
            {
                "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "location": "第9章，印刷页267，Markdown L317–321",
                "summary": "Haskell称Ferdinando Carlo Gonzaga为曼托瓦末代公爵，记述其1706年避居威尼斯、两年后去世，并以不确定语气讨论Sagredo图稿的可能来源。",
                "line_start": 317,
                "line_end": 321,
                "span": "Markdown lines 317–321; print p. 267",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "location": "第10章，印刷页312，Markdown L21–23",
                "summary": "Haskell称Schulenburg于1724年购入的多数古代作品来自Ferdinando Carlo Gonzaga的曼托瓦末代公爵画廊。",
                "line_start": 21,
                "line_end": 23,
                "span": "Markdown lines 21–23; print p. 312",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Mantua, Ferdinando Carlo, Duke of”及第9、10章的Ferdinando Carlo Gonzaga。Haskell称其为曼托瓦末代公爵，"
            "记述他在1706年奥地利入侵后避居威尼斯，两年后于帕多瓦去世；第10章将Schulenburg购藏的多数古代作品联系到他的画廊。"
            "关于他本人或其近侍可能持有Sagredo图稿的说法是Haskell提出的假设，仍保留其不确定性。既有人物卡中的Ferdinando, Duke of Mantua"
            "对应第7章p.175所述、1624年在位且为Vincenzo之子的较早人物；本卡与之分列。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card represents the index heading “Mantua, Ferdinando Carlo, Duke of” and the Ferdinando Carlo Gonzaga "
            "named in chapters 9 and 10. Haskell identifies him as the last Duke of Mantua, says he sought refuge in Venice "
            "after the Austrian invasion in 1706 and died in Padua two years later, and connects most of Schulenburg's "
            "purchase of old-master works to his gallery. Haskell's suggestion that Ferdinando Carlo or someone in his "
            "entourage may have owned the drawings later assembled by Sagredo remains a hypothesis. The existing KU "
            "Ferdinando, Duke of Mantua refers to the earlier duke described on p. 175 as Marie de Medici's nephew and "
            "Vincenzo's son in 1624; this card records a separate person. The Chinese name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp10-p312-works-from-gonzaga-gallery",
            "st-chp9-p267-ducal-pictures-sent-and-distributed",
            "st-chp9-p267-ferdinando-death-in-padua",
            "st-chp9-p267-ferdinando-refuge-in-venice",
            "st-chp9-p267-tentative-mantuan-origin-of-sagredo-drawings",
        ],
        "identity_extra": (
            "书内身份分界：[较早的Ferdinando, Duke of Mantua](ferdinando-duke-of-mantua.md)对应1624年语境；本卡对应Ferdinando Carlo Gonzaga及1706–1708年语境。"
        ),
    },
    {
        "candidate": "cand-0087",
        "group": "new-person:altieri-emilio-clement-x-0c9723ef22",
        "ku": "units/persons/emilio-altieri-pope-clement-x",
        "name_zh": "埃米利奥·阿尔蒂耶里",
        "name_en": "Emilio Altieri (Pope Clement X)",
        "index_entry": "A.csv#88",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
        "index_quote": "Altieri, Emilio (Pope Clement X)",
        "index_span": "A.csv#88; index row 90; pp. 118, 161, 162",
        "chapters": "第4、6章；索引 A.csv#88",
        "sources": [
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "location": "第4章，印刷页118，Markdown L220–222",
                "summary": "Haskell称Pope Clement X于1670年任命Massimi为Cardinal与Maestro di Camera，并说明Massimi委托的Clemency壁画以教皇自取名号作双关。",
                "line_start": 220,
                "line_end": 222,
                "span": "Markdown lines 220–222; print p. 118",
            },
            {
                "file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
                "location": "第6章，第五节，印刷页161，Markdown L3–12",
                "summary": "Haskell描述Clement X的高龄、Altieri家族对宫殿完工的担忧、Don Gasparo作为教皇侄辈及Clement X限制过度裙带关系的措施。",
                "line_start": 3,
                "line_end": 12,
                "span": "Markdown lines 3–12; print p. 161",
            },
            {
                "file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
                "location": "第6章，第五节，印刷页162，Markdown L14–18",
                "summary": "Haskell继续讨论Clement X的节俭理由，并称Innocent XI继任Clement X、在位十三年。",
                "line_start": 14,
                "line_end": 18,
                "span": "Markdown lines 14–18; print p. 162",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Altieri, Emilio (Pope Clement X)”。第4章称Clement X于1670年任命Massimi担任Cardinal与Maestro di Camera，"
            "并将以Clemency为题的壁画解释为对教皇自取名号的双关；第6章讨论Altieri家族的宫殿计划、Don Gasparo Altieri的教皇侄辈身份、"
            "Clement X抑制过度裙带关系的尝试及其继任者Innocent XI。Altieri家族及其成员各自保持独立对象身份；相关正式关系留待S6逐条审查。"
            "中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card represents the index heading “Altieri, Emilio (Pope Clement X).” Chapter 4 says Clement X appointed "
            "Massimi both Cardinal and Maestro di Camera in 1670 and reads the Clemency fresco as a pun on the name the "
            "pope assumed. Chapter 6 discusses the Altieri family's palace project, Don Gasparo Altieri's status as the "
            "pope's nephew, Clement X's effort to reduce excessive nepotism, and his succession by Innocent XI. The Altieri "
            "family and its members remain separate identities; the related formal relations await individual S6 review. "
            "The Chinese name is a project working transliteration."
        ),
        "relation_ids": [
            "st-chp4-sec-ii-p118-clement-x-appointments",
            "st-chp4-sec-ii-p118-fresco-papal-allusion",
            "st-chp6-p161-v1-15",
            "st-chp6-p161-v1-21",
            "st-chp6-p162-v1-18",
        ],
        "identity_extra": (
            "Altieri家族为独立对象，见[Altieri family KU](../../families/altieri-family-clement-x.md)；本卡指人物Emilio Altieri。"
        ),
    },
    {
        "candidate": "cand-0155",
        "group": "new-person:bacon-francis-e77bd98874",
        "ku": "units/persons/francis-bacon",
        "name_zh": "弗朗西斯·培根",
        "name_en": "Francis Bacon",
        "index_entry": "B.csv#2",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
        "index_quote": "Bacon, Sir Francis",
        "index_span": "B.csv#2; index row 4; pp. 107n, 320, 370",
        "chapters": "第4、10、15章；索引 B.csv#2",
        "sources": [
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "location": "第4章注释，印刷页107注，Markdown L263",
                "summary": "Haskell转引Peiresc于1635年的法文信件，其中写作Baccon并提到del Pozzo所取回的相关著作；保留转引层级与原拼写。",
                "line_start": 263,
                "line_end": 263,
                "span": "Markdown line 263; note on print p. 107",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "location": "第10章，印刷页320，Markdown L158–160",
                "summary": "Haskell称Lodoli喜爱的作者包括Galileo和Bacon。",
                "line_start": 158,
                "line_end": 160,
                "span": "Markdown lines 158–160; print p. 320",
            },
            {
                "file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "location": "第15章，印刷页370，Markdown L62",
                "summary": "Haskell称Querini宅邸的图书室陈列Bacon半身像，并评价他为启蒙运动奠基者及Lodoli特别敬仰的人物。",
                "line_start": 62,
                "line_end": 62,
                "span": "Markdown line 62; print p. 370",
            },
        ],
        "description_zh": (
            "本卡对应索引词头“Bacon, Sir Francis”，连接第4、10、15章的人名提及。第4章注释转引Peiresc 1635年法文信件时写作Baccon；"
            "第10章称Bacon是Lodoli喜爱的作者之一；第15章写到Querini图书室中的Bacon半身像，并将“启蒙运动奠基者”及Lodoli特别敬仰者的评价"
            "归于Haskell。转引中的Baccon作为原拼异文保留；此卡不独立核验信件或评价。中文名为通行工作译名。"
        ),
        "description_en": (
            "This card represents the index heading “Bacon, Sir Francis” and the name occurrences in chapters 4, 10, and 15. "
            "Chapter 4's note transcribes Baccon in a French letter by Peiresc dated 1635; chapter 10 names Bacon among "
            "Lodoli's favourite authors; and chapter 15 describes a bust of Bacon in Querini's library, attributing to "
            "Haskell the characterization of him as a founder of the Enlightenment and Lodoli's particular hero. The "
            "transcribed form Baccon is retained as a source variant; the letter and Haskell's evaluation are not independently "
            "verified here. The Chinese name is the project's working rendering."
        ),
        "relation_ids": [
            "st-chp10-p320-bacon-favourite-author-of-lodoli",
            "st-chp15-p370-bacon-as-enlightenment-founder",
            "st-chp15-p370-bacon-bust-depicts-francis-bacon",
            "st-chp15-p370-bacon-as-lodoli-particular-hero",
        ],
        "identity_extra": "",
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
            "sentence_summary": f"索引词头为“{t['index_quote']}”；页码范围见索引定位。",
            "original_quotes": [{"source_span": t["index_span"], "text": t["index_quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": t["index_file"],
                "source_span": t["index_span"],
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
    candidates = f"`{t['candidate']}`"
    relation_rows = "\n".join(
        f"- [`{sid}`](../../tables/book-statements.jsonl)：S2直接关系候选，待 S6 逐条审查。"
        for sid in t["relation_ids"]
    )
    identity_extra = f"\n\n- {t['identity_extra']}" if t["identity_extra"] else ""
    return (
        f"---\n{fm}---\n\n"
        "## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}\n\n"
        f"**English:** {t['description_en']}\n\n"
        "## 关系与证据\n\n### 身份与外部链接\n\n"
        f"- S3跨章身份组：候选 {candidates}；查看 [alignment.csv](../../tables/alignment.csv) 与"
        f"[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
        f"本批未采用外部权威标识。{identity_extra}\n\n"
        "### 关系记录\n\n"
        "当前没有登记在 `relations.csv` 的正式关系。以下 S2 直接关系候选保留待 S6 审查，不因 S4 登记而视为已确认：\n\n"
        f"{relation_rows}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Register three reviewed cross-chapter person groups in S4.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by = {r["candidate_id"]: r for r in candidates}
    align_by = {
        r["candidate_id"]: r
        for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    manifest_by = {r["ku_id"]: r for r in manifest}
    statements = {
        data["statement_id"]: data
        for data in (
            json.loads(line)
            for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    planned_alignments = [dict(r) for r in alignments]
    planned_by = {
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
        c, a = candidate_by[cid], planned_by[cid]
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
        assert group_members == [cid], f"unexpected person group members for {group}: {group_members}"
        t["group_candidates"] = group_members
        assert ku not in manifest_by
        card_path = ROOT / f"04-knowledge/{ku}.md"
        assert not card_path.exists()
        assert f"- 04-knowledge/{ku}.md" not in accepted_lines
        assert not any(
            r.get("name_en", "").casefold() == t["name_en"].casefold()
            for r in manifest
            if r["type"] == "person"
        ), f"same-name person KU already exists: {t['name_en']}"
        index_bytes = (ROOT / t["index_file"]).read_bytes()
        assert t["index_quote"].encode("ascii") in index_bytes, f"index name missing: {t['index_entry']}"
        for item in t["sources"]:
            quote = source_quote(item)
            assert quote and quote in (ROOT / item["file"]).read_text(encoding="utf-8-sig")
        for sid in t["relation_ids"]:
            assert sid in statements
            statement = statements[sid]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
        relation_total += len(t["relation_ids"])
        cards[card_path] = make_card(t)
        a["ku_id"] = ku
        a["process_ref"] = PROCESS_REF
        a["resolution_note"] += (
            f" S4 registration ({DATE}): mapped {group} to {ku}; chapter and index identity anchors are retained. "
            f"{len(t['relation_ids'])} direct relation candidates remain pending S6."
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
        planned_accepted = prior.insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")
    stats = sync.summarize_by_type(candidate_by.values(), planned_alignments)
    _, totals = sync.build_type_table(stats)
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    process_text = read_text(PROCESS_PATH)
    anchor = f'<a id="{ANCHOR}"></a>'
    assert anchor not in process_text
    process_text += (
        "\n\n"
        + anchor
        + "\n\n### S4 person：Ferdinando Carlo Gonzaga、Emilio Altieri 与 Francis Bacon 登记（2026-10-17）\n\n"
        "三个单成员跨章person `new` 组各登记一个KU，补齐双语描述、原书与索引证据、alignment候选映射及可点击的身份入口。"
        "Ferdinando Carlo Gonzaga与既有的Ferdinando, Duke of Mantua经姓名、世代及年代语境区分；Emilio Altieri作为人物与Altieri家族对象分开；"
        "Francis Bacon的ch.4转引拼写Baccon保留为来源异文。共14条直接S2关系候选继续待S6审查；本批未新增正式关系或外部身份记录。\n\n"
        "| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
    )
    for t in TARGETS:
        process_text += (
            f"| `{t['candidate']}` / `{t['group']}` | `{t['ku']}` | {t['chapters']} | {len(t['relation_ids'])} |\n"
        )
    process_text += "\n"
    result_text += "\n\n### S4 person：三组跨章人物身份登记（2026-10-17）\n\n"
    for t in TARGETS:
        result_text += (
            f"- `{t['candidate']}` / `{t['group']}` → [{t['name_zh']}（{t['name_en']}）]"
            f"(../units/{t['ku']}.md)；{t['chapters']}；{len(t['relation_ids'])}条直接关系候选留待S6。\n"
        )
    result_text += "\n本批未登记正式关系或外部身份标识；候选卡提供指向 alignment.csv 与过程记录的内部身份入口。\n"

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert relation_total == 14

    if args.dry_run:
        print(
            f"DRY-RUN OK: person groups={len(TARGETS)}; cards={len(cards)}; "
            f"direct relation candidates={relation_total}"
        )
        print(
            f"manifest: {len(manifest):,}->{len(planned_manifest):,}; "
            f"registered groups: {before_totals['registered_groups']:,}->{totals['registered_groups']:,}; "
            f"pending groups: {before_totals['pending_groups']:,}->{totals['pending_groups']:,}; "
            f"pending candidate mappings: {before_totals['pending_members']:,}->{totals['pending_members']:,}"
        )
        for t in TARGETS:
            print(f"{t['candidate']} -> {t['ku']}; group={t['group']}; {len(t['relation_ids'])} S6 candidates")
        return

    for path, card in cards.items():
        path.write_bytes(card.encode("utf-8"))
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(
        f"APPLIED: person groups={len(TARGETS)}; cards={len(cards)}; "
        f"manifest={len(planned_manifest):,}; registered groups={totals['registered_groups']:,}; "
        f"pending groups={totals['pending_groups']:,}"
    )


if __name__ == "__main__":
    main()
