from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_three_crosschapter_person_groups_20261017j as card_template  # noqa: E402
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
ANCHOR = "s4-richmond-title-identity-20261017"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGET = {
    "candidate": "cand-2193",
    "group_candidates": ["cand-2193", "cand-2194"],
    "group": "new-person:of-richmond-9053928efd",
    "ku": "units/persons/duke-of-richmond-mcswiny-british-worthies",
    "name_zh": "里士满公爵",
    "name_en": "Duke of Richmond",
    "index_entry": "Q-R.csv#120",
    "index_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
    "index_quote": "Richmond, Duke of",
    "index_span": "Q-R.csv#120–121; index rows 122–123; pp. 287, 289–291",
    "chapters": "第10章，印刷页287–291；索引 Q-R.csv#120–121",
    "sources": [
        {
            "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
            "location": "第10章，印刷页287，Markdown L212–213",
            "summary": "Haskell称McSwiny代表Lord March筹划英国名人墓葬寓意画系列，并说明Lord March于1723年成为里士满公爵。",
            "line_start": 212,
            "line_end": 213,
            "span": "Markdown lines 212–213; print p. 287",
            "quote_text": "Acting on behalf of Lord March, who became\nDuke of Richmond in 1723, he proposed to have painted by the leading Italian artists a series of allegorical tombs to commemorate the great men of England’s recent history.",
        },
        {
            "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
            "location": "第10章注2，印刷页288，Markdown L541",
            "summary": "Haskell称一封1727年11月28日McSwiny致里士满公爵的信曾由Francis Watson提供给他查看；本项目未独立查阅该信。",
            "line_start": 541,
            "line_end": 541,
            "span": "Markdown line 541; note 2 on print p. 288",
            "quote_text": "a letter from McSwiny to the Duke of Richmond dated 28 November 1727 kindly shown to me by Mr Francis Watson.",
        },
        {
            "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
            "location": "第10章，印刷页289，Markdown L230",
            "summary": "Haskell称该系列到1722年已有十五幅开始制作，多数后来由里士满公爵购得。",
            "line_start": 230,
            "line_end": 230,
            "span": "Markdown line 230; print p. 289",
            "quote_text": "The scheme began well, and by 1722 fifteen pictures had already been started, most of which were later acquired by the Duke of Richmond.",
        },
        {
            "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
            "location": "第10章，印刷页290，Markdown L246",
            "summary": "Haskell称里士满公爵购买了至少十幅画；对其具体购藏范围仍保留注释中的不确定性。",
            "line_start": 246,
            "line_end": 246,
            "span": "Markdown line 246; print p. 290",
            "quote_text": "Despite these problems, the Duke of Richmond bought at least ten of the paintings, and other versions of some of them also found purchasers.",
        },
        {
            "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
            "location": "第10章，印刷页291，Markdown L259",
            "summary": "Haskell称1741年出版物中的九幅寓意墓葬版画均来自里士满公爵的收藏。",
            "line_start": 259,
            "line_end": 259,
            "span": "Markdown line 259; print p. 291",
            "quote_text": "There were eighteen instead of fifty plates, and only nine of the allegorical tombs were engraved—all from the Duke of Richmond’s collection.",
        },
        {
            "citation": INDEX_CITATION,
            "file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
            "location": "全书索引 Q-R.csv#121 子目",
            "summary": "索引在里士满公爵下列出McSwiny's British Worthies子目，定位p.289–291。",
            "line_start": 123,
            "line_end": 123,
            "span": "Q-R.csv row 123; printed pp. 289–291",
            "quote_text": '"Richmond, Duke of",,and McSwiny\'s British Worthies,,"289, 290, 291"',
        },
    ],
    "description_zh": (
        "本卡按Haskell书中“Duke of Richmond”称谓记录与McSwiny英国名人墓葬画系列相关的人物。第10章p.287称McSwiny代表Lord March筹划该系列，并说Lord March于1723年成为里士满公爵；p.288注2记一封1727年McSwiny致公爵的信；p.289–291继续叙述同一系列及公爵购藏。索引主项与“and McSwiny’s British Worthies”子目相连，支持把两条索引候选及对应正文提及归入同一书内人物组。所引段落没有提供该人的完整个人姓名，本卡保留头衔作工作名称；具体购藏清单按Haskell所述保留不确定性。中文名为描述性工作译名。"
    ),
    "description_en": (
        "This card records the person whom Haskell refers to as the Duke of Richmond in the McSwiny British Worthies sequence. Chapter 10 p. 287 says McSwiny acted for Lord March, who became Duke of Richmond in 1723; note 2 on p. 288 cites a 1727 letter from McSwiny to the Duke; and pp. 289–291 continue with the same series and the Duke’s acquisitions. The index main entry and its “and McSwiny’s British Worthies” subentry support grouping the two index candidates and their corresponding body references as one source-local person. The cited passages do not give his full personal name, so the title is retained as a working label; Haskell’s uncertainty about the exact acquired pictures is preserved. The Chinese name is a descriptive working rendering."
    ),
    "relation_ids": [
        "st-chp10-p288-n02-letter-shown-to-haskell",
        "st-chp10-p289-note2-1741-reported-ownership",
        "st-chp10-p289-note2-richmond-probable-total",
        "st-chp10-p289-pictures-started-richmond-acquisition",
        "st-chp10-p290-richmond-purchases",
        "st-chp10-p291-volume-plate-and-tomb-count",
    ],
    "identity_extra": (
        "本组为书内头衔身份；原文未给完整个人姓名，未从外部材料补名。"
    ),
    "s3_review_note": (
        "S3 correction (2026-10-17): the prior note incorrectly called 'Duke of Richmond' a full personal name and described the grouping as a normalized full-name match. "
        "The cited passages provide a title only. The group is retained as one source-local person because p.287 names Lord March as becoming Duke in 1723, p.288 cites McSwiny's letter to the Duke in 1727, and pp.289–291 continue with the Duke in the same British Worthies sequence. "
        "No full personal name is inferred; it remains unverified."
    ),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def keep_bom_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def source_quote(item: dict) -> str:
    lines = (ROOT / item["file"]).read_text(encoding="utf-8-sig").splitlines()
    block = "\n".join(lines[item["line_start"] - 1 : item["line_end"]])
    quote = item.get("quote_text", block)
    assert quote in block, f"quote not found in source span: {item['file']}:{item['line_start']}"
    return quote


def make_card(t: dict) -> str:
    card_template.TASK = TASK
    card_template.CARD_REF = CARD_REF
    card_template.ANCHOR = ANCHOR
    card_template.DATE = DATE
    sources = []
    for item in t["sources"]:
        sources.append(
            {
                "citation": item.get("citation", BOOK_CITATION),
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [{"source_span": f"Markdown lines {item['line_start']}–{item['line_end']}", "text": source_quote(item)}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": item["file"], "source_span": item["span"]},
            }
        )
    sources.append(
        {
            "citation": INDEX_CITATION,
            "location": f"全书索引 {t['index_entry']}",
            "sentence_summary": f"索引词头为“{t['index_quote']}”；页码范围见索引定位。",
            "original_quotes": [{"source_span": t["index_span"], "text": t["index_quote"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["index_file"], "source_span": t["index_span"]},
        }
    )
    fm = yaml.safe_dump(
        {
            "title": f"{t['name_zh']}（{t['name_en']}）",
            "name_en": t["name_en"],
            "type": "person",
            "evidence_status": "source_backed",
            "sources": sources,
            "created": DATE,
            "updated": DATE,
            "process_ref": CARD_REF,
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    candidate_links = "、".join(f"`{cid}`" for cid in t["group_candidates"])
    relation_rows = "\n".join(
        f"- [`{sid}`](../../tables/book-statements.jsonl)：S2直接关系候选，待 S6 逐条审查。"
        for sid in t["relation_ids"]
    )
    return (
        f"---\n{fm}---\n\n## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}\n\n**English:** {t['description_en']}\n\n"
        "## 关系与证据\n\n### 身份与外部链接\n\n"
        f"- S3跨章身份组：候选 {candidate_links}；查看 [alignment.csv](../../tables/alignment.csv) 与"
        f"[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。本批未采用外部权威标识。"
        f"{t['identity_extra']}\n\n"
        "### 关系记录\n\n当前没有登记在 `relations.csv` 的正式关系。以下 S2 直接关系候选保留待 S6 审查，不因 S4 登记而视为已确认：\n\n"
        f"{relation_rows}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Review and register the Duke of Richmond identity group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by = {r["candidate_id"]: r for r in candidates}
    planned = [dict(r) for r in alignments]
    planned_by = {r["candidate_id"]: r for r in planned if r.get("candidate_id") and not r.get("external_source")}
    manifest_by = {r["ku_id"]: r for r in manifest}
    statements = {
        r["statement_id"]: r
        for r in (json.loads(line) for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    accepted_lines = read_text(ACCEPTED_PATH).splitlines()

    assert set(TARGET["group_candidates"]) == {"cand-2193", "cand-2194"}
    assert TARGET["ku"] not in manifest_by
    assert not (ROOT / f"04-knowledge/{TARGET['ku']}.md").exists()
    assert f"- 04-knowledge/{TARGET['ku']}.md" not in accepted_lines
    assert not any(r.get("name_en", "").casefold() == TARGET["name_en"].casefold() for r in manifest if r["type"] == "person")
    index_bytes = (ROOT / TARGET["index_file"]).read_bytes()
    assert TARGET["index_quote"].encode("ascii") in index_bytes

    group_members = [
        r["candidate_id"]
        for r in alignments
        if r.get("candidate_id") and r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == TARGET["group"]
    ]
    assert set(group_members) == set(TARGET["group_candidates"]), group_members
    assert all(candidate_by[cid]["suggested_type"] == "person" for cid in TARGET["group_candidates"])
    assert all(planned_by[cid]["decision"] == "new" and not planned_by[cid].get("ku_id") for cid in TARGET["group_candidates"])
    assert all(source_quote(item) for item in TARGET["sources"])
    for sid in TARGET["relation_ids"]:
        assert sid in statements
        statement = statements[sid]
        assert statement.get("qualifiers", {}).get("relation_candidate") is True
        assert set(TARGET["group_candidates"]).intersection((statement.get("subject_candidate_id"), statement.get("object_candidate_id")))

    cards = {ROOT / f"04-knowledge/{TARGET['ku']}.md": make_card(TARGET)}
    for cid in TARGET["group_candidates"]:
        row = planned_by[cid]
        row["ku_id"] = TARGET["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += f" {TARGET['s3_review_note']} S4 registration: group {TARGET['group']} maps to {TARGET['ku']}; {len(TARGET['relation_ids'])} direct relation candidates remain pending S6."

    planned_manifest = [dict(r) for r in manifest]
    planned_manifest.append(
        {
            "ku_id": TARGET["ku"],
            "type": "person",
            "canonical_name": f"{TARGET['name_zh']}（{TARGET['name_en']}）",
            "name_en": TARGET["name_en"],
            "source_task": TASK,
            "card_path": f"04-knowledge/{TARGET['ku']}.md",
        }
    )
    planned_manifest.sort(key=lambda r: r["ku_id"])
    planned_accepted = prior.insert_accepted(accepted_lines, f"04-knowledge/{TARGET['ku']}.md")
    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before_totals = sync.build_type_table(before_stats)
    stats = sync.summarize_by_type(candidate_by.values(), planned)
    _, totals = sync.build_type_table(stats)
    assert len(planned_manifest) == len(manifest) + 1
    assert totals["registered_groups"] == before_totals["registered_groups"] + 1
    assert totals["pending_groups"] == before_totals["pending_groups"] - 1
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGET["group_candidates"])
    assert len(TARGET["relation_ids"]) == 6

    process_text = read_text(PROCESS_PATH)
    anchor = f'<a id="{ANCHOR}"></a>'
    assert anchor not in process_text
    process_text += (
        "\n\n" + anchor + "\n\n"
        "### S3→S4 person：里士满公爵身份组复核与登记（2026-10-17）\n\n"
        f"{TARGET['s3_review_note']} 两条索引候选共同映射至一个标题式人物 KU；完整个人姓名仍待证。6条直接关系候选留待 S6，未登记正式关系。\n\n"
        "| 候选 / S3身份组 | KU | 身份证据锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
        f"| `cand-2193`、`cand-2194` / `{TARGET['group']}` | `{TARGET['ku']}` | 第10章 p.287–291；Q-R.csv#120–121 | 6 |\n"
    )
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    result_text += (
        "\n\n### S3→S4 person：里士满公爵身份组复核与登记（2026-10-17）\n\n"
        f"`cand-2193`、`cand-2194` 维持同一 `{TARGET['group']}`，映射至"
        f"[里士满公爵人物卡](../units/{TARGET['ku']}.md)。原文仅提供头衔，完整个人姓名留待核实；6条直接关系候选留待 S6。\n"
    )

    if args.dry_run:
        print(
            f"DRY-RUN OK: one person group; candidates={len(TARGET['group_candidates'])}; "
            f"cards={len(cards)}; direct relation candidates={len(TARGET['relation_ids'])}"
        )
        print(
            f"manifest: {len(manifest):,}->{len(planned_manifest):,}; "
            f"registered groups: {before_totals['registered_groups']:,}->{totals['registered_groups']:,}; "
            f"pending groups: {before_totals['pending_groups']:,}->{totals['pending_groups']:,}; "
            f"pending candidate mappings: {before_totals['pending_members']:,}->{totals['pending_members']:,}"
        )
        return

    for path, text in cards.items():
        path.write_bytes(text.encode("utf-8"))
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(
        f"APPLIED: person group={TARGET['group']}; candidates={len(TARGET['group_candidates'])}; "
        f"manifest={len(planned_manifest):,}; registered groups={totals['registered_groups']:,}; pending groups={totals['pending_groups']:,}"
    )


if __name__ == "__main__":
    main()
