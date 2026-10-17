from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATES = ("cand-1827",)
GROUP = "new-person:giovanni-pannini-paolo-73bd439aee"
KU_ID = "units/persons/giovanni-paolo-pannini"
CARD_REL = "04-knowledge/units/persons/giovanni-paolo-pannini.md"
CH10 = "02-sources/02-Markdown/10_CHP-10_intro.md"
CH14 = "02-sources/02-Markdown/14_CHP-14_intro.md"
CH19 = "02-sources/02-Markdown/19_CHP-19Appendix.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/P.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp10-p308-possible-pannini-source",
    "st-chp14-p351-pannini-subject",
    "st-chp14-p358-recommended-study-pannini",
    "st-chp14-p357-pantheon-commissioned-painter",
    "st-chp14-p357-pannini-specialized-in-capricci",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页297注、307–308；OCR L332–343、445–466",
            "sentence_summary": (
                "第297页注记称 Juvarra 在四件罗马订画中向 Pannini 和 Locatelli 各订两件。"
                "第307页将 Pannini 作为同时代罗马绘画的参照；第308页称 Canaletto 可能在一次较早的罗马之行中"
                "从 Pannini 得到 caprice 构思，但 Haskell 同时保留 Algarotti 影响的可能。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 343",
                    "text": (
                        "In 1723 Juvarra commissioned a painting from Marco Ricci to indicate his proposals for the "
                        "Castello di Rivoli. As was to occur later in his commissions for Spain he showed his preference "
                        "for Roman painting by ordering four pictures from there (two each from Pannini and Locatelli) "
                        "compared with only one each from a Venetian and a Turinese artist—see Viale, 1950-1, p. 161."
                    ),
                },
                {
                    "source_span": "line 452",
                    "text": (
                        "It is significant that Smith should have wished for views of antiquity only and ignored the "
                        "contemporary Rome of Pannini; yet it is hard to see these playing more than a symbolical role "
                        "in the rise of the neo-classic."
                    ),
                },
                {
                    "source_span": "line 461",
                    "text": (
                        "It is equally possible that Canaletto derived the idea from Pannini on his visit to Rome a year "
                        "or two before"
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH10,
                "source_span": "lines 343, 452, 461; print pp. 297n, 307–308",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章；印刷页351、357–358；OCR L46–53、107–124",
            "sentence_summary": (
                "第351页称 Pannini 被要求在其 vedute 中画入古代罗马人。第357页叙述 Algarotti 委托 Pannini 绘制万神殿内部，"
                "并称 Pannini 擅长建筑 capricci；第358页记 Algarotti 建议将 Pannini 作为学习对象。"
                "委托、专长和推荐相关表述均仍以原书关系候选进入 S6 裁决。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 50",
                    "text": "and to Pannini being required to paint ancient Romans among his vedute",
                },
                {
                    "source_span": "lines 109–110",
                    "text": (
                        "For himself he commissioned Pannini to paint an Interior of the\n"
                        "Pantheon which he asked Bonomo to keep for him in his rooms and possibly to exhibit."
                    ),
                },
                {
                    "source_span": "line 114",
                    "text": (
                        "Architectural capricci of the kind had long been familiar in Rome where Pannini had made a "
                        "speciality of them"
                    ),
                },
                {
                    "source_span": "lines 122–123",
                    "text": (
                        "For these reasons he recommends studying Flemish painters such as Teniers and\n"
                        "Wouwermans, as well as Vernet and Pannini."
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH14,
                "source_span": "lines 50, 109–110, 114, 122–123; print pp. 351, 357–358",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第19章附录；印刷页393；OCR L152–153",
            "sentence_summary": (
                "第393页称 1776 年售卖的素描和蚀刻版画中，Pannini 等艺术家的作品数量可观；"
                "原文没有在此逐件列出作品。"
            ),
            "original_quotes": [
                {
                    "source_span": "lines 152–153",
                    "text": (
                        "The drawings and etchings in the 1776 sale are far more numerous, and Canaletto, Maneschi,\n"
                        "Pannini, Zais, Zuccarelli, Marco Ricci and Tiepolo are all well represented."
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CH19,
                "source_span": "lines 152–153; print p. 393",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；P.csv#26–27；印刷页297n、307、308、351、357、358、393",
            "sentence_summary": (
                "书后索引以 Giovanni Paolo Pannini 为人物主项，列出跨章页码；另以同一姓名列出作品子项"
                "“Interior of the Pantheon”（P.csv#27）。"
            ),
            "original_quotes": [
                {
                    "source_span": "index entry P.csv#26",
                    "text": "| Pannini, Giovanni Paolo |  |  |  | 297n, 307, 308, 351, 357, 358, 393 |",
                },
                {
                    "source_span": "index entry P.csv#27",
                    "text": "| Pannini, Giovanni Paolo |  | Interior of the Pantheon |  | 357 |",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entries P.csv#26–27",
            },
        },
    ]
    frontmatter = {
        "title": "乔瓦尼·保罗·帕尼尼（Giovanni Paolo Pannini）",
        "name_en": "Giovanni Paolo Pannini",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch10 = f"[第10章 pp.297n、307–308](../../../{CH10})（L343、452、461）"
    ch14 = f"[第14章 pp.351、357–358](../../../{CH14})（L50、109–110、114、122–123）"
    ch19 = f"[第19章附录 p.393](../../../{CH19})（L152–153）"
    index = f"[书后索引](../../../{INDEX_FILE})（P.csv#26–27）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应书后索引人物主项“Pannini, Giovanni Paolo”（P.csv#26）及其所指的第10、14、19章段落。Haskell在不同章节提及 Pannini 与罗马绘画、建筑 capricci、绘画委托及 Canaletto 的 caprice 构思；其中有关影响、委托和绘画要求的关系候选保留原文限定，待 S6 裁决。本次只登记人物身份。索引另有同名作品子项“Interior of the Pantheon”（P.csv#27；`cand-1828`）；该作品候选当前仍为 S3 `undecided`，不并入本人物，也不据索引建立作品卡。{ch10} {ch14} {ch19} {index}

**English:** This card records the person entry “Pannini, Giovanni Paolo” (P.csv#26) and the passages it indexes in Chapters 10, 14, and 19. Haskell discusses Pannini in connection with Roman painting, architectural capricci, painting commissions, and Canaletto’s caprice ideas. The book’s qualifications about influence, commission, and proposed subject matter are retained; related candidates remain for S6 adjudication. This step registers the person identity only. The index has a separate work subentry, “Interior of the Pantheon” (P.csv#27; `cand-1828`). That work candidate remains `undecided` at S3 and is not merged into this person or registered as a work from the index alone. {ch10} {ch14} {ch19} {index}

### 身份边界

人物主项 P.csv#26 与同名作品子项 P.csv#27 分开。`cand-1828`（work：Interior of the Pantheon）因当前 S3 记录缺少可核的正文提及锚点而保持待证；本卡不将人物与作品合并，也不将委托陈述视为作品完成或现存实物作者身份的证明。

Person entry P.csv#26 remains distinct from work subentry P.csv#27. Candidate `cand-1828` (work: Interior of the Pantheon) remains unresolved because its current S3 record lacks a verifiable body-mention anchor. This card does not merge the person and work, or treat the commission statement as proof of completion or authorship of a surviving object.

## 关系与证据

5条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。其中万神殿内部作品的委托关系因作品端点 `cand-1828` 仍为 S3 `undecided`，不进入正式关系。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Giovanni Paolo Pannini's S3 person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert not (ROOT / CARD_REL).exists()
    assert CARD_REL not in accepted
    assert not any(
        row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL
        or (row.get("type") == "person" and (row.get("name_en") or "").casefold() == "giovanni paolo pannini")
        for row in manifest
    ), "Giovanni Paolo Pannini person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "P.csv#26"
    assert candidate["canonical_name"] == "Pannini, Giovanni Paolo"
    assert candidate["index_page_range"] == "297n, 307, 308, 351, 357, 358, 393"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    work_candidate = candidate_by_id["cand-1828"]
    work_alignment = alignment_by_id["cand-1828"]
    assert work_candidate["index_entry_id"] == "P.csv#27"
    assert work_candidate["suggested_type"] == "work"
    assert work_candidate["sub_entry"] == "Interior of the Pantheon"
    assert work_alignment["decision"] == "undecided" and not work_alignment.get("ku_id")

    ch10_text = (ROOT / CH10).read_text(encoding="utf-8-sig")
    ch14_text = (ROOT / CH14).read_text(encoding="utf-8-sig")
    ch19_text = (ROOT / CH19).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "two each from Pannini and Locatelli" in ch10_text
    assert "It is equally possible that Canaletto derived the idea from Pannini" in ch10_text
    assert "Pannini being required to paint ancient Romans among his vedute" in ch14_text
    assert "commissioned Pannini to paint an Interior of the" in ch14_text
    assert "Pannini had made a speciality of them" in ch14_text
    assert "as well as Vernet and Pannini" in ch14_text
    assert "Pannini, Zais, Zuccarelli, Marco Ricci and Tiepolo are all well represented" in ch19_text
    assert "| Pannini, Giovanni Paolo |  |  |  | 297n, 307, 308, 351, 357, 358, 393 |" in index_text
    assert "| Pannini, Giovanni Paolo |  | Interior of the Pantheon |  | 357 |" in index_text

    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == RELATION_CANDIDATES, direct_relations

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATES[0] and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "乔瓦尼·保罗·帕尼尼",
        "name_en": "Giovanni Paolo Pannini",
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-giovanni-paolo-pannini-person\"></a>\n\n"
        "### S4 person：Giovanni Paolo Pannini 身份组登记（2026-10-17）\n\n"
        f"`cand-1827`（P.csv#26，索引页码297n、307、308、351、357、358、393）沿用 S3 身份组 `{GROUP}`，"
        f"登记为[乔瓦尼·保罗·帕尼尼人物卡](../../../{CARD_REL})。索引主项和第10、14、19章的姓名提及支持书内身份映射；"
        "卡片只保留有书内来源的语境及其原有不确定性，未访问外部身份来源。\n\n"
        "索引中的 `cand-1828`（P.csv#27，work：Interior of the Pantheon）与人物分开；其 S3 仍为 undecided，"
        "不由同名子项或委托语句推定作品身份。5条直接 relation_candidate 保留待 S6："
        + ", ".join(sorted(RELATION_CANDIDATES))
        + "。万神殿委托关系的作品端点未决；本轮未新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Giovanni Paolo Pannini 身份组登记（2026-10-17）\n\n"
        f"`cand-1827`（P.csv#26）映射至[Giovanni Paolo Pannini 人物卡](../units/persons/giovanni-paolo-pannini.md)。"
        "索引的 P.csv#27 “Interior of the Pantheon”是分立 work 候选 `cand-1828`，S3 仍为 undecided；"
        "不据此或委托陈述将人物与作品合并。5条直接关系候选仍待 S6，且未登记正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 Giovanni Paolo Pannini dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"identity_group={GROUP}; candidates={len(group_rows)}; direct_relation_candidates={len(direct_relations)}")
        print(f"separate_work_candidate=cand-1828; s3_decision={work_alignment['decision']}; no work KU inferred")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / CARD_REL).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATES[0]} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
