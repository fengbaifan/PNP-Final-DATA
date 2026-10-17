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
ANCHOR = "s4-poleni-crosschapter-person-20261017"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGET = {
    "candidate": "cand-1968",
    "group_candidates": ["cand-1968", "cand-9182"],
    "group": "new-person:giovanni-poleni-8cd50ead76",
    "ku": "units/persons/giovanni-poleni",
    "name_zh": "乔瓦尼·波莱尼",
    "name_en": "Giovanni Poleni",
    "index_entry": "P.csv#169",
    "index_file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
    "index_quote": "Poleni, Marchese Giovanni",
    "index_span": "P.csv#169; index row 171; pp. 201, 367",
    "chapters": "第10、15章；索引 P.csv#169",
    "sources": [
        {
            "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
            "location": "第10章，印刷页301，Markdown L387",
            "summary": "Haskell以全名称Poleni为Smith在Padua的熟人，并称其为大学教授、工程师和建筑师。",
            "line_start": 387,
            "line_end": 387,
            "span": "Markdown line 387; print p. 301",
            "quote_text": "Smith’s other acquaintance in Padua was the Marchese Giovanni Poleni, also a professor at the University, and an engineer and architect of some distinction—in many ways a typical product of the provincial Enlightenment.",
        },
        {
            "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
            "location": "第10章注4，印刷页301，Markdown L591",
            "summary": "注4转述Poleni于1747年写给Smith的两封信，并说明信中请求Smith向Visentini取得绘图；Haskell未提供原件页码，本项目未查阅原信。",
            "line_start": 591,
            "line_end": 591,
            "span": "Markdown line 591; note 4 on print p. 301",
            "quote_text": "There are two very friendly letters from Poleni to Smith, dated 9 and 17 April 1747, in the Biblioteca Marciana—MSS. Ital:Cl.X. Cod CCLXXXVIII—6580.",
        },
        {
            "file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
            "location": "第15章，印刷页367，Markdown L36",
            "summary": "Haskell称Canova于1781年受委为Leonardo Venier制作一尊Marchese Poleni雕像。",
            "line_start": 36,
            "line_end": 36,
            "span": "Markdown line 36; print p. 367",
            "quote_text": "Canova, who was commissioned in 1781 to make a statue of the Marchese Poleni for Leonardo Venier",
        },
    ],
    "description_zh": (
        "本卡对应索引词头“Poleni, Marchese Giovanni”及第10章明载的Marchese Giovanni Poleni。第10章称他为Smith在Padua的熟人、大学教授、工程师和建筑师；"
        "注4转述1747年两封致Smith的信，称Poleni曾请Smith向Visentini取得绘图，但原信未在本项目中查阅，请求是否完成亦未据此确认。第15章记Canova于1781年受委为Marchese Poleni制作雕像。"
        "索引另列p.201与p.367；当前S2人物提及映射对应p.301及p.367，p.201仅作为索引定位保留，不单独作为本次身份判断依据。中文名为本项目工作音译。"
    ),
    "description_en": (
        "This card represents the index heading “Poleni, Marchese Giovanni” and the Marchese Giovanni Poleni named in chapter 10. Haskell describes him as Smith’s acquaintance in Padua, a university professor, engineer, and architect. "
        "Note 4 reports two 1747 letters to Smith and says Poleni asked Smith to obtain drawings from Visentini; the letters were not consulted for this project, and fulfillment of the request is not inferred. Chapter 15 reports that Canova was commissioned in 1781 to make a statue of Marchese Poleni. "
        "The index also lists p. 201 and p. 367; the current S2 person mentions map to pp. 301 and 367. The p. 201 locator is retained as an index reference and is not used alone as identity evidence. The Chinese name is a project working transliteration."
    ),
    "relation_ids": [
        "st-chp10-p301-poleni-profile",
        "st-chp10-p301-note4-poleni-requested-drawings",
        "st-chp15-p367-poleni-statue-depicts-poleni",
    ],
    "identity_extra": (
        "本组含索引候选cand-1968与第10章正文候选cand-9182；全名锚点位于p.301，p.367的Marchese Poleni对应同一索引主项。"
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
                "citation": BOOK_CITATION,
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
    parser = argparse.ArgumentParser(description="Review and register the cross-chapter Giovanni Poleni identity group.")
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

    assert set(TARGET["group_candidates"]) == {"cand-1968", "cand-9182"}
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
        row["resolution_note"] += (
            " S3 cross-chapter review (2026-10-17): cand-9182 names Marchese Giovanni Poleni at ch.10 p.301; "
            "the index candidate cand-1968 is anchored by the same full name and ch.15 p.367's Marchese Poleni reference. "
            "The index p.201 locator is retained but is not used alone as identity evidence."
            f" S4 registration: group {TARGET['group']} maps to {TARGET['ku']}; {len(TARGET['relation_ids'])} direct relation candidates remain pending S6."
        )

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
    assert len(TARGET["relation_ids"]) == 3

    process_text = read_text(PROCESS_PATH)
    anchor = f'<a id="{ANCHOR}"></a>'
    assert anchor not in process_text
    process_text += (
        "\n\n" + anchor + "\n\n"
        "### S3→S4 person：Giovanni Poleni 跨章身份组复核与登记（2026-10-17）\n\n"
        "索引候选 `cand-1968`（P.csv#169）与正文候选 `cand-9182` 合并登记为一个人物 KU。第10章 p.301 给出全名 Marchese Giovanni Poleni；"
        "同章注4转述1747年致 Smith 的两封信；第15章 p.367 以 Marchese Poleni 指称 Canova 受委制作雕像的对象。正文全名与索引主项的倒置姓名相合，"
        "且 p.367 的称号与其吻合，支持跨章同一身份。索引所列 p.201 保留为定位，但当前 S2 提及未映射该页，本裁决不以该页码单独作证。"
        "未查阅注4所述原信，也未引入外部身份记录。两条候选共同映射至一个 KU；3 条直接关系候选留待 S6，未登记正式关系。\n\n"
        "| 候选 / S3身份组 | KU | 身份证据锚点 | 直接关系候选 |\n|---|---|---|---:|\n"
        f"| `cand-1968`、`cand-9182` / `{TARGET['group']}` | `{TARGET['ku']}` | 第10章 p.301；第15章 p.367；P.csv#169 | 3 |\n"
    )
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    result_text += (
        "\n\n### S3→S4 person：Giovanni Poleni 跨章身份组复核与登记（2026-10-17）\n\n"
        f"`cand-1968`（P.csv#169）与 `cand-9182`（第10章 p.301）维持同一 `{TARGET['group']}`，映射至"
        f"[Giovanni Poleni 人物卡](../units/{TARGET['ku']}.md)。第15章 p.367 的 Marchese Poleni 语境与 p.301 的全名相合；"
        "索引 p.201 定位保留，但不单独作为本次身份依据。3 条直接关系候选留待 S6。\n"
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
