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
ENTITY_PATH = TABLES / "entity-candidates.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
SAME_CANDIDATE = "cand-6179"
SAME_GROUP = "sg3-term-cand-6179"
SAME_KU = "units/terms/history-painting"
NEW_CANDIDATE = "cand-5254"
NEW_GROUP = "sg3-term-cand-5254"
NEW_KU = "units/terms/blood-of-christ-iconographic-theme"
NEW_CARD = f"04-knowledge/{NEW_KU}.md"
NEW_NAME_ZH = "基督之血图像主题"
NEW_NAME_EN = "Blood of Christ Iconographic Theme"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATIONS = [
    "st-chp3-seciv-l58-67-bernini-affected-uncertain-origin",
    "st-chp3-seciv-l58-67-bernini-blood-belief-quotation",
    "st-chp3-seciv-l58-67-blood-theme-dear-to-molinos",
    "st-chp3-seciv-l58-67-dome-suitability-more-likely-explanation",
    "st-chp3-seciv-l58-67-final-scheme-different-but-linked",
    "st-chp3-seciv-l58-67-molinos-association-possible-obstacle",
    "st-chp3-seciv-notes-l189-204-p82-n4-adam-eve-link-the-programmes",
]


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第3章；印刷页82；OCR L61–64",
            "sentence_summary": "Haskell identifies the Blood of Christ as a devotional theme especially dear to Molinos, then reports Bernini's belief through a nested quotation.",
            "original_quotes": [
                {"source_span": "line 61", "text": "A thème especially dear to Molinos—and one, of course, by no means new—was that of the Blood of Christ"},
                {"source_span": "lines 63–64", "text": "the belief that he always had in the powers of the Blood of Christ in which, he used to say, he hoped to drown his sins."},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "lines 61–64",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第3章；印刷页82；OCR L65",
            "sentence_summary": "Haskell presents alternative, qualified explanations for why the Blood of Christ theme was not used for the Gesù dome and distinguishes Gaulli's eventual subject from it.",
            "original_quotes": [
                {"source_span": "line 65", "text": "Perhaps the theme, innocuous when Bernini had first drawn it a few years earlier, had by now become too closely associated with Molinos to be palatable to the Jesuits."},
                {"source_span": "line 65", "text": "More likely they realised that, whatever its significance for private devotion, it was wholly unsuitable for the decoration of a dome."},
                {"source_span": "line 65", "text": "Gaulli’s scheme, when finally brought to fruition, was based on a different subject, although it retained links with the Blood of Christ"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "line 65",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第3章注4；印刷页82；OCR L204",
            "sentence_summary": "Haskell says Adam and Eve commonly appeared in versions of the Blood of Christ but limits what early drawings can establish.",
            "original_quotes": [
                {"source_span": "line 204", "text": "The figures were, however, generally included in versions of The Blood of Christ and thus constitute a link between the two programmes."},
                {"source_span": "line 204", "text": "these are in far too early a stage to constitute serious evidence."},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "line 204",
            },
        },
    ]
    fm = {
        "title": f"{NEW_NAME_ZH}（{NEW_NAME_EN}）",
        "name_en": NEW_NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": PROCESS_REF,
    }
    body = """## 内容

### 描述

**中文：** 本卡记录 Haskell 第3章所讨论的“基督之血”宗教与图像主题。作者称该主题尤其为 Molinos 所珍视，并通过第二层引文转述 Bernini 对基督之血力量的信仰；Bernini 是否从 Molinos 得到这一观念，Haskell 明言无法确定。谈及耶稣会士未采用该主题装饰 Gesù 穹顶时，Haskell 同时给出与 Molinos 关联的可能性和“更可能”的穹顶适用性解释。最终 Gaulli 穹顶方案属于不同题材，虽保留与此主题的联系。本卡不指某件绘画、图稿或穹顶方案。

**English:** This card records the religious and iconographic theme of the Blood of Christ discussed in Chapter 3. Haskell says the theme was especially dear to Molinos and, through a nested quotation, reports Bernini's belief in the power of Christ's Blood. Haskell explicitly leaves uncertain whether Bernini derived the notion from Molinos. In discussing the Jesuits' non-adoption of the theme for the Gesù dome, Haskell offers both a possible association with Molinos and a more likely explanation based on the theme's suitability for a dome. Gaulli's eventual dome scheme had a different subject while retaining links to this theme. This unit does not denote a particular painting, drawing, or dome scheme.

### 身份边界

候选 `cand-5254` 表示一般 devotional/iconographic theme。Bernini 的绘图、据称的言论、Gaulli 的早期构想及最终 `Duplex Intercessio` 方案均是分立对象；不将主题与任何单件作品或方案合并。注4对早期图稿证据力的限制原样保留。

Candidate `cand-5254` denotes a general devotional and iconographic theme. Bernini's drawing, reported words, Gaulli's early proposal, and the final `Duplex Intercessio` scheme remain distinct objects; the theme is not merged with any single work or programme. Haskell's limitation on the evidentiary value of early drawings is retained.

## 关系与证据

7条直接 S2 `relation_candidate` 留待 S6：`st-chp3-seciv-l58-67-bernini-affected-uncertain-origin`, `st-chp3-seciv-l58-67-bernini-blood-belief-quotation`, `st-chp3-seciv-l58-67-blood-theme-dear-to-molinos`, `st-chp3-seciv-l58-67-dome-suitability-more-likely-explanation`, `st-chp3-seciv-l58-67-final-scheme-different-but-linked`, `st-chp3-seciv-l58-67-molinos-association-possible-obstacle`, `st-chp3-seciv-notes-l189-204-p82-n4-adam-eve-link-the-programmes`。保留作者与嵌套引文的语气和限定；本卡未新增正式关系。
"""
    return f"---\n{yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignment if not row.get("external_source")}
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert candidate_by_id[SAME_CANDIDATE]["suggested_type"] == "term"
    assert alignment_by_id[SAME_CANDIDATE]["decision"] == "new"
    assert sync.get_group(alignment_by_id[SAME_CANDIDATE].get("resolution_note", "")) == SAME_GROUP
    assert SAME_KU in manifest_by_id and manifest_by_id[SAME_KU]["type"] == "term"
    assert candidate_by_id[NEW_CANDIDATE]["suggested_type"] == "term"
    assert alignment_by_id[NEW_CANDIDATE]["decision"] == "new" and not alignment_by_id[NEW_CANDIDATE].get("ku_id")
    assert sync.get_group(alignment_by_id[NEW_CANDIDATE].get("resolution_note", "")) == NEW_GROUP
    assert NEW_KU not in manifest_by_id and not (ROOT / NEW_CARD).exists()
    assert f"- {NEW_CARD}" not in accepted_lines
    assert not any(
        row["type"] == "term" and any(token in (row["canonical_name"] + row["name_en"]).casefold()
                                         for token in ("blood of christ", "christ's blood"))
        for row in manifest
    ), "possible existing Blood of Christ term KU"

    statements = sync.load_statements()
    statement_by_id = {row["statement_id"]: row for row in statements}
    for sid in RELATIONS:
        assert sid in statement_by_id
        row = statement_by_id[sid]
        assert row.get("qualifiers", {}).get("relation_candidate") is True
        assert NEW_CANDIDATE in (
            row.get("subject_candidate_id"), row.get("object_candidate_id"),
            *row.get("qualifiers", {}).get("mentioned_candidate_ids", []),
        ), f"candidate not present in relation statement {sid}"

    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") == SAME_CANDIDATE and not row.get("external_source"):
            row["decision"] = "same"
            row["ku_id"] = SAME_KU
            row["process_ref"] = "S3-cross-chapter-term-reuse-2026-10-17"
            row["resolution_note"] = (
                f"prior_group={SAME_GROUP}; S3 correction 2026-10-17: same as existing term KU {SAME_KU}. "
                "The candidate names the same general painting genre already defined by the History painting card; "
                "Chapter 5's use for Miel and Cerquozzi and Chapter 9's discussion of the genre do not identify a "
                "distinct narrower term or entity. Reuse the existing KU; no duplicate term card is created."
            )
        elif row.get("candidate_id") == NEW_CANDIDATE and not row.get("external_source"):
            row["ku_id"] = NEW_KU
            row["resolution_note"] = (row.get("resolution_note", "") +
                f" S4 registration: mapped {NEW_GROUP} to {NEW_KU}.")

    planned_manifest = [dict(row) for row in manifest]
    planned_manifest.append({
        "ku_id": NEW_KU,
        "type": "term",
        "canonical_name": NEW_NAME_ZH,
        "name_en": NEW_NAME_EN,
        "source_task": TASK,
        "card_path": NEW_CARD,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s3-history-painting-reuse-and-s4-blood-of-christ-term\"></a>\n\n"
        "### S3 term 复用修正与 S4 图像主题登记（2026-10-17）\n\n"
        f"`{SAME_CANDIDATE}` 原 S3 `new` 组 `{SAME_GROUP}` 与既有 [历史画术语卡](../../../04-knowledge/units/terms/history-painting.md) 表达同一绘画门类。"
        "复核卡片及第5章 p.140、第9章 p.257 的用法后，将该候选改为 `same` → `units/terms/history-painting`；"
        "本书语境没有定义独立子类，不重复建卡。\n\n"
        f"`{NEW_CANDIDATE}` 保持 S3 `new` 组 `{NEW_GROUP}`，登记为 `units/terms/blood-of-christ-iconographic-theme`。"
        "第3章 p.82 将 Blood of Christ 明称为 devotional theme；Molinos、Bernini、Jesuit dome debate 与 Duplex Intercessio 的区别及不确定性均按原文保留。"
        "7条直接 relation_candidate 留待 S6，未新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S3/S4 term：history painting 复用与 Blood of Christ 主题登记（2026-10-17）\n\n"
        f"`{SAME_CANDIDATE}` 从原 `new` 身份组修正为 `same`，复用[历史画（History painting）](../units/terms/history-painting.md)；"
        "历史画作为画种的书内用法没有形成独立窄义实体。"
        f"`{NEW_CANDIDATE}` 映射至[基督之血图像主题](../units/terms/blood-of-christ-iconographic-theme.md)，7条直接关系候选留待 S6。"
        "历史画未新建 KU，主题卡未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > NEW_CARD),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {NEW_CARD}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("S3/S4 term dry-run passed: cand-6179 -> same history-painting; cand-5254 -> new Blood of Christ term")
        print(f"registered term groups={totals['registered_groups']}; new term cards=1; formal_relations_added=0")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / NEW_CARD).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / NEW_CARD).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: same corrections=1; new groups registered=1; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
