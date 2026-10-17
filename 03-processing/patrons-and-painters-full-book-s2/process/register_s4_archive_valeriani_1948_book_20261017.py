from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_archive_memmo_query_sheet_20261017 as previous  # noqa: E402

sync = previous.sync
ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
GROUP = "archive-group-09a3b2fdbd56"
MEMBERS = ("cand-11088", "cand-11204")
KU_ID = "units/archives/teatralni-zhivopicets-giuseppe-valeriani-1948"
CARD_REL = f"04-knowledge/{KU_ID}.md"
NAME_ZH = "舞台画家朱塞佩·瓦莱里亚尼"
NAME_EN = "Theatrical Painter Giuseppe Valeriani"
PROCESS_ANCHOR = "s4-valeriani-1948-book-20261017"
BODY_SOURCE = "02-sources/02-Markdown/20_CHP-20Postscript.md"
BIB_SOURCE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
BODY_QUOTE = (
    "The interest of the eighteenth-century Russian court in attracting artists from Venice was investigated "
    "in a fully documented book about Giuseppe Valeriani in 1948,7"
)
NOTE_QUOTE = "7 Konopleva."
BIB_QUOTE = "Konopleva, M. S.: Teatralni Zhivopicets Giuseppe Valeriani, Leningrad 1948."
BODY_STATEMENT = "st-chp20-p406-russian-court-valeriani-book"
NOTE_STATEMENT = "st-chp20-p406-n07-citation"
BIB_STATEMENT = "st-chp21-bib-l616-656-entry-28"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def source_rows() -> list[dict]:
    records = [
        {
            "location": "第20章后记；印刷页406；Markdown L157。",
            "summary": "Haskell称18世纪俄国宫廷吸引威尼斯艺术家的兴趣由一部1948年、资料详尽的 Giuseppe Valeriani 著作研究；该书未独立查阅。",
            "span": "line 157; print p. 406",
            "quote": BODY_QUOTE,
            "file": BODY_SOURCE,
        },
        {
            "location": "第20章后记；印刷页406注7；Markdown L262。",
            "summary": "注7只列出姓氏 Konopleva，完整作者身份不据短引推断。",
            "span": "line 262; print p. 406, note 7",
            "quote": NOTE_QUOTE,
            "file": BODY_SOURCE,
        },
        {
            "location": "书后书目；印刷页426；Markdown L652。",
            "summary": "书目列出作者著录、罗马化题名、出版地与年份；被引书籍本身未独立查阅。",
            "span": "line 652; print p. 426",
            "quote": BIB_QUOTE,
            "file": BIB_SOURCE,
        },
    ]
    return [
        {
            "citation": BOOK_CITATION,
            "location": record["location"],
            "sentence_summary": record["summary"],
            "original_quotes": [{"source_span": record["span"], "text": record["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": record["file"],
                "source_span": record["span"],
            },
        }
        for record in records
    ]


def card_text() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body_link = "../../../" + BODY_SOURCE
    bib_link = "../../../" + BIB_SOURCE
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 哈斯克尔第20章称，18世纪俄国宫廷吸引威尼斯艺术家的兴趣由一部1948年、资料详尽的 Giuseppe Valeriani 著作研究；该句注7为 Konopleva。书后书目将其列为 M. S. Konopleva 所著 *Teatralni Zhivopicets Giuseppe Valeriani*，Leningrad，1948。本卡所用中文与英文名称是依据题名作的描述性工作译名，不是经核实的正式译名。书籍本身未独立查阅。[第20章 p.406 正文与注7]({body_link})（L157、262）；[书后书目 p.426]({bib_link})（L652）。

**English:** Haskell says in Chapter 20 that an extensively documented 1948 book about Giuseppe Valeriani investigated the eighteenth-century Russian court’s interest in attracting artists from Venice; note 7 gives “Konopleva.” The bibliography lists the work as by M. S. Konopleva, *Teatralni Zhivopicets Giuseppe Valeriani*, Leningrad, 1948. The Chinese and English display names are descriptive working translations of the printed title, not verified official translations. The book itself was not independently consulted.

### 文献身份与范围

- 原题：*Teatralni Zhivopicets Giuseppe Valeriani*；保留 Haskell 书目中的罗马化拼写。
- 作者著录：Konopleva, M. S.；不扩写首字母，也不据短引识别为某一具名人物。
- 出版信息：Leningrad，1948；此处仅记录 Haskell 书目著录，未独立核对版本、出版社、馆藏或原书。
- 主题范围按 Haskell 的概述限定为18世纪俄国宫廷吸引威尼斯艺术家的兴趣及 Giuseppe Valeriani；不据此扩写书中论证或研究结论。
- 同一 S3 身份组 {GROUP} 的 cand-11088（正文描述）与 cand-11204（注7及书目记录）共同映射至本卡。

## 关系与证据

第20章正文 statement {BODY_STATEMENT} 将该书与 Giuseppe Valeriani 相联系，作为直接关系候选留待 S6 核对端点、关系类型、方向、语境与证据；本卡未新增正式关系。{NOTE_STATEMENT} 记录注7的书目短引，{BIB_STATEMENT} 记录书后书目条目，二者均为引文身份依据，不单独构成关系。候选作者 cand-11203、注8所列两篇论文 cand-11089、俄罗斯宫廷 cand-11087 与出版地 cand-5796 均保持各自 S3 决定，不并入本卡。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the 1948 Valeriani book identity group in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_lines = accepted.splitlines()
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decision_by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id and cid in decision_by_id for cid in MEMBERS)
    group_members = {
        cid for cid, row in decision_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decision_by_id[cid].get("decision") == "new" and not decision_by_id[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted_lines
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and any(term in " ".join(row.values()).casefold()
                for term in ("teatralni zhivopicets", "giuseppe valeriani"))
        for row in manifest
    ), "possible same-type archive already exists"
    assert f'<a id="{PROCESS_ANCHOR}"></a>' not in process_text
    assert "S4 archive：1948 年 Giuseppe Valeriani 著作登记" not in result_text

    for relative, quote in ((BODY_SOURCE, BODY_QUOTE), (BODY_SOURCE, NOTE_QUOTE), (BIB_SOURCE, BIB_QUOTE)):
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        assert normalized(quote) in normalized(source_text), f"source evidence changed: {relative}"

    statements = [
        json.loads(line)
        for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statement_by_id = {row["statement_id"]: row for row in statements}
    assert {BODY_STATEMENT, NOTE_STATEMENT, BIB_STATEMENT} <= set(statement_by_id)
    body = statement_by_id[BODY_STATEMENT]
    note = statement_by_id[NOTE_STATEMENT]
    bib = statement_by_id[BIB_STATEMENT]
    assert body.get("subject_candidate_id") == "cand-11088"
    assert body.get("object_candidate_id") == "cand-9382"
    assert body.get("original_quote") and "fully documented book about Giuseppe Valeriani" in body["original_quote"]
    assert body.get("qualifiers", {}).get("relation_candidate") is True
    assert body.get("qualifiers", {}).get("footnote_statement_ids") == [NOTE_STATEMENT]
    assert note.get("object_candidate_id") == "cand-11204"
    assert note.get("original_quote") == NOTE_QUOTE
    assert note.get("qualifiers", {}).get("relation_candidate") is False
    assert "Footnote 7 identifies the 1948 book" in note.get("qualifiers", {}).get("claim", "")
    assert bib.get("object_candidate_id") == "cand-11204"
    record = bib.get("qualifiers", {}).get("bibliographic_record", {})
    assert record.get("author_as_printed") == "Konopleva, M. S."
    assert record.get("title_as_printed") == "Teatralni Zhivopicets Giuseppe Valeriani"
    assert record.get("publication_details_as_printed") == "Leningrad 1948"

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; one KU for both cross-chapter candidates."
    planned_manifest = [dict(row) for row in manifest]
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated archive card frontmatter is invalid"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = previous.refresh_process_type_table(process_text, stats)
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        "### S4 archive：1948 年 Giuseppe Valeriani 著作登记（2026-10-17）\n\n"
        f"- 同一 S3 new 身份组 {GROUP} 的 cand-11088（第20章 p.406 正文）和 cand-11204（注7及第21章 p.426 书目）"
        f"共同映射至 [{NAME_ZH}](../../../{CARD_REL})（{KU_ID}）；2条候选映射对应1个 archive KU。原题、作者著录、出版地与年份均按 Haskell 书内书目记录，书未独立查阅。\n"
        "- 中文与英文名称为描述性工作译名。作者保留为书目所载 M. S. Konopleva，不扩写身份。正文关于此书研究俄国宫廷吸引威尼斯艺术家的兴趣，是直接关系候选，留待 S6；注7和书目条目只作身份依据，不另建关系。\n"
        "- 作者候选 cand-11203 与注8两篇文章 cand-11089 仍 undecided；俄罗斯宫廷 cand-11087 与出版地 cand-5796 保持各自 S3 new、待 S4；Valeriani 人物 cand-9382 已有 KU；索引标题 cand-2679 仍 excluded。以上均未并入本书卡。\n"
        f"\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    next_process = next_process.rstrip() + process_append + "\n"
    next_result += (
        "\n\n### S4 archive：1948 年 Giuseppe Valeriani 著作登记（2026-10-17）\n\n"
        f"cand-11088 与 cand-11204 按 S3 同组裁决共同映射至 [{NAME_ZH}](../units/archives/{Path(KU_ID).name}.md)。"
        "正文、注7与书目页形成可追溯身份链；作者身份和被引书原文未扩展，正文关系候选仍待 S6。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    next_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 archive dry-run passed: group={GROUP}; candidates={len(MEMBERS)}; one KU={KU_ID}")
        print(f"relation_candidate={BODY_STATEMENT} pending S6; note and bibliography statements remain non-relations")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(next_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: group={GROUP}; candidates={len(MEMBERS)} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
