from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_archive_memmo_query_sheet_20261017 as process_sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "sg3-term-enlightenmentinitaly"
MEMBERS = ("cand-0974", "cand-0975", "cand-0976")
KU_ID = "units/terms/enlightenment-in-italy"
CARD_REL = "04-knowledge/units/terms/enlightenment-in-italy.md"
NAME_ZH = "意大利启蒙运动"
NAME_EN = "Enlightenment in Italy"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
CH8_QUOTE = "Raimondo may have been among those many patrons of the dawning Age of the Enlightenment"
CH10_INTRO_QUOTE = "among the figures commemorated were many of the ‘Saints’ of the Enlightenment such as Locke and Newton."
CH10_SECTION_QUOTES = (
    "more and more those Italians—writers, artists and intellectuals—who wished to experience the new developments were compelled to travel to London or Paris.",
    "the peace of Aix-la-Chapelle in 1748 is usually taken as the starting-point for a new spirit in Italy.",
    "In these changes Venice had played little direct part.",
    "nearly all of which presupposed the abolition of rule by aristocracy.",
)
CH15_QUOTE = (
    "the ‘Enlightenment’, as it had reached Venice through publishers and travellers or men of letters such as Lodoli and\n"
    "Algarotti, suggested new possibilities for a different kind of patronage"
)
PROCESS_ANCHOR = "s4-term-enlightenment-in-italy-20261017"
S3_RATIONALE = (
    " S3 identity-group rationale (2026-10-17): E.csv#9–11 share the main index heading 'Enlightenment in Italy'; "
    "#10 (contacts of Italian intellectuals with England and France) and #11 (opposition in Venice) are topical "
    "subentries under that heading, not independently named terms. The book uses the same source-local concept "
    "across its Ch.8 discussion of the dawning Age of the Enlightenment, Ch.10's Italy-wide account and Venetian "
    "qualification, and Ch.15's explicit account of the Enlightenment as it reached Venice. Keep the local Venice "
    "discussion as context within the indexed term; do not convert Haskell's framing into a comprehensive external "
    "period definition. The Ch.10 p.288 phrase 'Saints of the Enlightenment' is metaphorical, not a religious class."
)


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def source_rows():
    return [
        {
            "citation": BOOK_CITATION,
            "location": "第8章，印刷页225，Markdown 行175。",
            "sentence_summary": "哈斯克尔试探性地将 Raimondo 置于启蒙时代赞助人的背景中，并对比其公共画廊与私人空间。",
            "original_quotes": [
                {"source_span": "line 175; print p. 225", "text": CH8_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "line 175; print p. 225",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章引言，印刷页288，Markdown 行223。",
            "sentence_summary": "哈斯克尔将 Locke、Newton 等称作启蒙运动的“圣徒”；该处为比喻用法。",
            "original_quotes": [
                {"source_span": "line 223; print p. 288", "text": CH10_INTRO_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 223; print p. 288",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页317–318，Markdown 行130、134、138–139。",
            "sentence_summary": (
                "本章讨论意大利对英法思想发展的接触、启蒙思想在意大利的缓慢传播及其通常以1748年为起点的叙述；"
                "随后指出威尼斯对这些变化直接参与较少，同时讨论威尼斯维护贵族统治现状的立场。"
            ),
            "original_quotes": [
                {"source_span": "line 130; print p. 317", "text": CH10_SECTION_QUOTES[0]},
                {"source_span": "line 134; print p. 318", "text": CH10_SECTION_QUOTES[1]},
                {"source_span": "line 138; print p. 318", "text": CH10_SECTION_QUOTES[2]},
                {"source_span": "line 139; print p. 318", "text": CH10_SECTION_QUOTES[3]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "lines 130, 134, 138–139; print pp. 317–318",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第15章，印刷页361，Markdown 行13–14；句子续至 p.362。",
            "sentence_summary": "哈斯克尔称启蒙思想经出版者、旅行者及 Lodoli、Algarotti 等文人进入威尼斯，并带来不同赞助方式的可能。",
            "original_quotes": [
                {"source_span": "lines 13–14; print p. 361", "text": CH15_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/15_CHP-15_sec_i.md",
                "source_span": "lines 13–14; print p. 361, continued on p. 362",
            },
        },
    ]


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch8 = "../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md"
    ch10intro = "../../../02-sources/02-Markdown/10_CHP-10_intro.md"
    ch10 = "../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md"
    ch15 = "../../../02-sources/02-Markdown/15_CHP-15_sec_i.md"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本术语卡记录哈斯克尔在《赞助人与画家》中关于意大利启蒙运动及其威尼斯语境的书内用法。第10章将其置于18世纪意大利思想变化、对英法文化的接触和威尼斯的有限直接参与之中；第15章又讨论启蒙思想如何经出版者、旅行者和文人进入威尼斯，并提示一种不同的艺术赞助可能。第8章将 Raimondo 试探性地置于“启蒙时代赞助人”的背景下，第10章“启蒙运动的圣徒”则是比喻。以上是哈斯克尔的叙述框架，不作为对启蒙运动的完整学术定义或外部验证。

**English:** This term records Haskell’s use of the Enlightenment in Italy and its Venetian context in *Patrons and Painters*. Chapter 10 places it within eighteenth-century intellectual changes in Italy, contact with English and French culture, and Venice’s limited direct part in those changes. Chapter 15 also discusses how Enlightenment ideas reached Venice through publishers, travellers, and men of letters, suggesting new possibilities for artistic patronage. Chapter 8 tentatively places Raimondo among patrons of the “dawning Age of the Enlightenment”; Chapter 10’s “Saints of the Enlightenment” is metaphorical. This is Haskell’s narrative framing, not a comprehensive scholarly definition or an externally verified periodization.

### 术语范围与边界

- **索引主项：** `Enlightenment in Italy`（E.csv#9，pp.317–331）。`cand-0975`（E.csv#10，contacts of Italian intellectuals with England and France）与 `cand-0976`（E.csv#11，opposition in Venice）是该主项下的主题子目，记录论述入口，不拆为两个独立术语。
- **书内时间与限定：** 第10章称启蒙思想在意大利起初传播缓慢，并说1748年《亚琛和约》通常被视为意大利“新精神”的起点；“usually taken”保留为哈斯克尔描述的常见分期，不等同于断言思想此前不存在。[第10章 pp.317–318]({ch10})（L130、134、138–139）
- **威尼斯语境：** 第10章称威尼斯对前述变化直接参与有限，并讨论维护现状、反对废除贵族统治的本地立场；第15章则写启蒙思想“进入威尼斯”后的新赞助可能。[第15章 p.361]({ch15})（L13–14，续至 p.362）
- **其他书内用法：** 第8章的“启蒙时代赞助人”是对 Raimondo 的试探性归类。[第8章 p.225]({ch8})（L175）；第10章引言的“启蒙运动的圣徒”指 Locke、Newton 等人物，是比喻而非宗教身份。[第10章引言 p.288]({ch10intro})（L223）
- **对象边界：** 本卡保存 Haskell 的书内概念与论述变化，不固定为全学界统一的启蒙定义，不推导意大利各地同质经历，也不把威尼斯政治反对者并成成员清单。未使用外部术语或思想史数据库。

## 关系与证据

本卡未登记正式关系。直接关联该术语的 S2 statements 将其用于作者的历史叙述、分期与语境说明，当前均未分类为正式关系候选；本次只登记术语身份，不新增 `relations.csv` 关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Haskell's term 'Enlightenment in Italy' in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decision_by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id for cid in MEMBERS)
    group_members = {
        cid for cid, row in decision_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    expected_index = {
        "cand-0974": ("E.csv#9", "", "317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331"),
        "cand-0975": ("E.csv#10", "contacts of Italian intellectuals with England and France", "317, 318, 319"),
        "cand-0976": ("E.csv#11", "opposition in Venice", "318, 326, 327"),
    }
    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        assert candidate.get("suggested_type") == "term"
        assert decision_by_id[cid].get("decision") == "new" and not decision_by_id[cid].get("ku_id")
        assert (candidate.get("index_entry_id"), candidate.get("sub_entry"), candidate.get("index_page_range")) == expected_index[cid]

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "term" and NAME_EN.casefold() == (row.get("name_en") or "").casefold() for row in manifest)

    source_checks = (
        ("02-sources/02-Markdown/08_CHP-8_sec_ii.md", (CH8_QUOTE,)),
        ("02-sources/02-Markdown/10_CHP-10_intro.md", (CH10_INTRO_QUOTE,)),
        ("02-sources/02-Markdown/10_CHP-10_sec_ii.md", CH10_SECTION_QUOTES),
        ("02-sources/02-Markdown/15_CHP-15_sec_i.md", (CH15_QUOTE,)),
    )
    for relative, quotes in source_checks:
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        for quote in quotes:
            assert normalized(quote) in normalized(source_text), f"source quote changed: {relative}: {quote[:80]!r}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relation_candidates = [
        row for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert relation_candidates == [], [row["statement_id"] for row in relation_candidates]
    expected_direct = {
        "st-chp10-p317-diffusion-of-enlightened-ideas-was-slow",
        "st-chp10-p318-enlightenment-doctrines-presupposed-end-of-aristocratic-rule",
        "st-chp10-p318-peace-aix-as-starting-point-for-new-spirit-in-italy",
        "st-chp10-p318-voltaire-commented-on-intellectual-revival",
        "st-chp15-p361-enlightenment-different-patronage-partial",
    }
    assert {row["statement_id"] for row in direct} == expected_direct

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        row = planned_by_id[cid]
        if S3_RATIONALE.strip() not in row["resolution_note"]:
            row["resolution_note"] += S3_RATIONALE
        row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
        row["ku_id"] = KU_ID

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "term",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated term card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    assert f"<a id=\"{PROCESS_ANCHOR}\"></a>" not in next_process
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S3/S4 term：Enlightenment in Italy 跨章身份组登记（{DATE}）\n\n"
        f"- `{GROUP}` 包含 `cand-0974`（E.csv#9）、`cand-0975`（#10 contacts of Italian intellectuals with England and France）、"
        "`cand-0976`（#11 opposition in Venice）；三个候选共享索引主项，两个子项是同一术语下的主题入口，不是另两个术语。"
        f"本组登记为[{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（`{KU_ID}`）。\n"
        "- 跨章对照覆盖第8章 p.225、第10章引言 p.288、第10章 pp.317–318和第15章 p.361。第8章“dawning Age”表述是对 Raimondo 的试探归类；"
        "第10章将启蒙思想在意大利的扩散说为初期缓慢，并称1748年通常被视为意大利“新精神”的起点，同时指出威尼斯直接参与有限；"
        "第15章又明确描述启蒙思想如何进入威尼斯。合并保留同一书内概念及其地域语境，不外推统一分期。\n"
        f"- 5 条直接 S2 statements 均非正式关系候选；本批未写入 `relations.csv`，也未使用外部术语库。"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
            f"direct_statements={len(direct)}; relation_candidates={len(relation_candidates)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; card_frontmatter=valid"
        )
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
        f"direct_statements={len(direct)}; relation_candidates={len(relation_candidates)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
