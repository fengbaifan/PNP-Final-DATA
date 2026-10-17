from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MENTIONS_PATH = TABLES / "mentions.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s3-s4-person-giovanni-ricci-20261017"
CANDIDATES = ("cand-2147", "cand-2148")
GROUP = "new-person:giovanni-ricci-3e157bdeda"
KU_ID = "units/persons/giovanni-ricci"
CARD_REL = "04-knowledge/units/persons/giovanni-ricci.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "乔瓦尼·里奇"
NAME_EN = "Giovanni Ricci"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/Q-R.csv"
SOURCE_204 = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE_238 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
MENTION_ID = "m-chp8-p238-giovanni-ricci"
MENTION_SEGMENT = "chp-8:08_CHP-8_sec_ii:l327-336"
MENTION_START = "754"
MENTION_END = "768"

RELATION_IDS = (
    "st-chp8-p204-crespi-biographer-evaluates-ricci-treatment",
    "st-chp8-p204-ricci-admired-contemporary-artists",
    "st-chp8-p204-ricci-dealer-terms",
    "st-chp8-p204-ricci-sent-crespi-to-absorb-influences",
    "st-chp8-p238-note2-ricci-pepoli-correspondence",
    "st-chp8-p238-ricci-acquired-work",
    "st-chp8-p238-ricci-financed-travels",
)
NON_RELATION_IDS = ("st-chp8-p204-ricci-leading-patron",)

SOURCES = (
    {
        "citation": BOOK_CITATION,
        "location": "书后索引，Q-R.csv#74",
        "summary": "索引主项 Ricci, Giovanni 定位至 pp.204、238；索引提供本书内定位，不单独证明传记事实。",
        "quote": '"Ricci, Giovanni",,,,"204, 238"',
        "doc_id": "patrons-and-painters-index",
        "file": INDEX_FILE,
        "span": "Q-R.csv#74",
    },
    {
        "citation": BOOK_CITATION,
        "location": "书后索引，Q-R.csv#75",
        "summary": "缩进子目 patronage of Crespi 定位至 p.204；其主项为 Ricci, Giovanni。索引提供本书内定位，不单独证明传记事实。",
        "quote": '"Ricci, Giovanni",,patronage of Crespi,,204',
        "doc_id": "patrons-and-painters-index",
        "file": INDEX_FILE,
        "span": "Q-R.csv#75",
    },
    {
        "citation": BOOK_CITATION,
        "location": "第8章，印刷页204；OCR L14–16",
        "summary": "正文以全名 Giovanni Ricci 标识一位开明商人群体成员，并记述其赞助 Crespi、欣赏当代艺术家及作为画作经纪人的安排；对经纪安排的称许部分转引未具名传记作者。",
        "quote": "group of enlightened merchants was certainly Giovanni Ricci. He was a rich and discriminating patron who showed a keen appreciation of many contemporary artists, above all Burrini and the young Crespi.",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_204,
        "span": "lines 14–16; print p. 204",
    },
    {
        "citation": BOOK_CITATION,
        "location": "第8章，印刷页238；OCR L327–336",
        "summary": "第8章 p.238 再次给出 Giovanni Ricci 全名，并称其为 Crespi 在 Bologna 的赞助人之一，曾资助 Crespi 早年意大利旅行并购入其大量作品。",
        "quote": "particularly Giovanni Ricci, the rich marchandamateur who had financed his early travels throughout Italy and subsequently acquired a very large proportion of his work",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_238,
        "span": "lines 327–336; print p. 238",
    },
)


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": item["citation"],
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": item["doc_id"],
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relation_list = "、\n".join(f"- `{sid}`" for sid in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第8章 p.204 与 p.238 所述、索引主项及子目共同定位的 Giovanni Ricci。p.204 将他列入“开明商人”群体，称其为富有且有辨别力的赞助人，并记述他欣赏多位当代艺术家、特别是 Burrini 与年轻的 Crespi；该页还称他为 Crespi 经营画作并将转售利润交给画家的中间人，相关称许部分转引未具名传记作者。p.238 再称 Ricci 资助 Crespi 早年在意大利旅行并购入其大量作品。以上均为 Haskell 书内叙述；本卡不扩写外部生平。中文显示名为项目工作音译。

**English:** This card records the Giovanni Ricci discussed on pp. 204 and 238 of Haskell’s chapter 8 and located by the matching index heading and subentry. On p. 204 Haskell places him among the “enlightened merchants,” calls him a rich and discriminating patron, and says he appreciated several contemporary artists, especially Burrini and the young Crespi. The page also describes Ricci acting as Crespi’s dealer and passing resale profits to the artist; part of the praise is quoted from Crespi’s unnamed biographer. On p. 238 Haskell again names Ricci among Crespi’s Bolognese patrons and says he financed Crespi’s early travels in Italy and acquired a large proportion of his work. These are reports in Haskell’s book; the card adds no external biography. The Chinese display name is a project working transliteration.

### 名称与身份边界

索引主项 `Ricci, Giovanni`（Q-R.csv#74）列 p.204、p.238；缩进子目 `patronage of Crespi`（Q-R.csv#75）列 p.204。第8章两页均出现全名，且共同置于 Crespi 的赞助语境；候选 `cand-2147` 与 `cand-2148` 据此归入同一书内人物组。既有人物卡 Marco Ricci、Sebastiano Ricci 与 Giambattista Ricciardi 均为不同的全名对象，不与本卡合并。此判断不延伸到任何其他姓 Ricci 的候选。

The index main entry `Ricci, Giovanni` (Q-R.csv#74) lists pp. 204 and 238; its indented subentry `patronage of Crespi` (Q-R.csv#75) lists p. 204. Both chapter pages give the full name in the context of Crespi’s patronage, so candidates `cand-2147` and `cand-2148` are grouped as one book-local person. Existing cards for Marco Ricci, Sebastiano Ricci, and Giambattista Ricciardi represent different full-name identities and are not merged. This decision does not extend to any other Ricci candidate.

## 关系与证据

本次没有新增正式关系。以下7条直接 S2 关系候选留待 S6 逐项审查：

{relation_list}

第8章 p.204 的 `st-chp8-p204-ricci-leading-patron` 是 Haskell 的评价性身份描述，保持非关系陈述；`st-chp8-p204-crespi-biographer-evaluates-ricci-treatment` 的评价来源限定为 Crespi 未具名传记作者经 Haskell 转引。未写入 `relations.csv`。
"""


def update_process(text: str, totals: dict, manifest_count: int) -> str:
    if f'<a id="{ANCHOR}"></a>' in text:
        return text
    entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Giovanni Ricci 索引主项、子目与跨页正文并组登记（{DATE}）

S3 复核将 `cand-2147`（Q-R.csv#74，索引定位 pp.204、238）由 `undecided` 改为 `new`，与 `cand-2148`（Q-R.csv#75，“patronage of Crespi”，p.204）共同保留在 `{GROUP}`。此前 `cand-2147` 的未决理由称其无正文提及；复核发现第8章 p.238 L327–336 已以全名 Giovanni Ricci 记述其为 Crespi 的 Bologna 赞助人，且 S2 的 `st-chp8-p238-note2-ricci-pepoli-correspondence`、`st-chp8-p238-ricci-acquired-work`、`st-chp8-p238-ricci-financed-travels` 已将其作为直接端点。现向 mentions.csv 补入 `m-chp8-p238-giovanni-ricci`（L329，chars 224–238），不改写这三条既有 statement 的命题。p.204 与 p.238 两处全名、对 Crespi 的重叠赞助语境，以及同一索引主项/子目结构支持两候选同一身份；旧 undecided 理由保留于候选对齐行及本过程记录。

该组登记为[乔瓦尼·里奇人物卡](../../../04-knowledge/units/persons/giovanni-ricci.md)。卡片限于哈斯克尔书内身份和角色，不补外部生平。7条直接 S2 关系候选留待 S6，评价性 `st-chp8-p204-ricci-leading-patron` 继续保持非关系陈述；本次未修改 `relations.csv`。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(manifest_count)}。
"""
    return text.rstrip() + entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the Giovanni Ricci index/body identity group and register one person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    mention_fields, mentions = sync.read_csv(MENTIONS_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    repaired_mention = next((row for row in mentions if row.get("mention_id") == MENTION_ID), None)
    if (
        CARD_PATH.exists()
        and any(row.get("ku_id") == KU_ID for row in manifest)
        and all(decisions[cid].get("decision") == "new" and decisions[cid].get("ku_id") == KU_ID for cid in CANDIDATES)
        and all(sync.get_group(decisions[cid].get("resolution_note", "")) == GROUP for cid in CANDIDATES)
        and repaired_mention is not None
        and repaired_mention.get("start_char") == MENTION_START
        and repaired_mention.get("end_char") == MENTION_END
    ):
        print("ALREADY REGISTERED: Giovanni Ricci group, person KU, and p.238 mention alignment")
        return 0
    assert len(manifest) == 1550 and len(alignments) == 12642
    assert len(mentions) == 26618
    assert all(candidate_map[cid]["suggested_type"] == "person" for cid in CANDIDATES)
    assert decisions["cand-2147"]["decision"] == "undecided" and not decisions["cand-2147"].get("ku_id")
    assert decisions["cand-2148"]["decision"] == "new" and not decisions["cand-2148"].get("ku_id")
    assert sync.get_group(decisions["cand-2148"].get("resolution_note", "")) == GROUP
    assert not (ROOT / CARD_REL).exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row["candidate_id"] == MENTION_ID for row in mentions)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)

    expected_sources = {
        INDEX_FILE: ("Ricci, Giovanni", "patronage of Crespi"),
        SOURCE_204: ("group of enlightened merchants was certainly Giovanni Ricci.", "Ricci also acted as a dealer for Crespi"),
        SOURCE_238: ("particularly Giovanni Ricci, the rich marchandamateur", "financed his early travels throughout Italy"),
    }
    for rel, snippets in expected_sources.items():
        source_text = (ROOT / rel).read_text(encoding="utf-8-sig")
        for snippet in snippets:
            assert snippet in source_text, f"missing source excerpt {snippet!r} in {rel}"

    source_238_lines = (ROOT / SOURCE_238).read_text(encoding="utf-8-sig").splitlines()
    segment_238 = "\n".join(source_238_lines[326:336])
    assert segment_238.index("Giovanni Ricci") == int(MENTION_START)
    statements = {s["statement_id"]: s for s in sync.load_statements()}
    assert set(RELATION_IDS + NON_RELATION_IDS) <= set(statements)
    assert all(statements[sid]["qualifiers"].get("relation_candidate") is True for sid in RELATION_IDS)
    assert all(statements[sid]["qualifiers"].get("relation_candidate") is False for sid in NON_RELATION_IDS)
    assert decisions["cand-2147"]["candidate_id"] == "cand-2147"

    planned_alignment = [dict(row) for row in alignments]
    prior = decisions["cand-2147"]["resolution_note"]
    current_note_2147 = (
        f"source_ref=candidate=cand-2147;index_entry=Q-R.csv#74;index_pages=204, 238;"
        f"s2_mentions={MENTION_ID}@{SOURCE_238}#L327-336[Giovanni Ricci;chars={MENTION_START}-{MENTION_END}]; "
        f"prior_decision=undecided; prior_reason=index main entry previously had no mapped body mention; "
        f"S3 correction: p.238 body gives Giovanni Ricci by full name and existing S2 statements map the person as a direct endpoint; "
        f"grouped with cand-2148 by exact full-name and shared Crespi-patronage context across pp.204 and 238; group={GROUP}; "
        "Source-local person identity only; no external biography added."
    )
    current_note_2148 = (
        f"source_ref=candidate=cand-2148;index_entry=Q-R.csv#75;index_pages=204;"
        "s2_mentions=m-chp8-p204-001@02-sources/02-Markdown/08_CHP-8_sec_i.md#L14-21[Giovanni Ricci;chars=56-70],"
        "m-chp8-p204-009@02-sources/02-Markdown/08_CHP-8_sec_i.md#L14-21[Ricci;chars=517-522]; "
        f"group={GROUP}; S3 grouping: p.204 full name and Crespi-patronage subentry align with the same full name and patronage context on p.238 (cand-2147). "
        "Source-local identity only; no external biography added."
    )
    for row in planned_alignment:
        if row.get("candidate_id") == "cand-2147" and not row.get("external_source"):
            row["decision"] = "new"
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] = current_note_2147 + f" prior_resolution_note={prior}"
        elif row.get("candidate_id") == "cand-2148" and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] = current_note_2148

    planned_mentions = list(mentions) + [{
        "mention_id": MENTION_ID,
        "segment_id": MENTION_SEGMENT,
        "candidate_id": "cand-2147",
        "surface_form": "Giovanni Ricci",
        "start_char": MENTION_START,
        "end_char": MENTION_END,
        "note": "Full name in the p.238 discussion of Crespi's Bolognese patrons; linked to index main entry Q-R.csv#74 and its p.204 subentry.",
    }]
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    assert len(planned_manifest) == 1551
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert (totals["registered_groups"], totals["registered_members"], totals["pending_groups"], totals["pending_members"]) == (532, 666, 4272, 4313)
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text = result_text.replace("26,618 mentions", "26,619 mentions", 1)
    assert "26,619 mentions" in result_text
    old_warning = "审计警告中的4,329条待登记 `decision=new` alignment 行，含4,314条候选决定映射（4,273组）和15条外部身份记录。"
    new_warning = "审计警告中的4,328条待登记 `decision=new` alignment 行，含4,313条候选决定映射（4,272组）和15条外部身份记录。"
    assert old_warning in result_text
    result_text = result_text.replace(old_warning, new_warning, 1)
    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"), totals, len(planned_manifest))
    result_note = (
        f"\n\n### S3→S4 person：Giovanni Ricci（{DATE}）\n\n"
        f"`cand-2147`、`cand-2148` → [{NAME_ZH}（{NAME_EN}）](../units/persons/giovanni-ricci.md)。"
        "父级索引定位项与“patronage of Crespi”子目由第8章 pp.204、238 的同名正文归为一组；索引候选 cand-2147 的旧未决理由已在过程记录中说明并保留。"
        "7条关系候选留待 S6；评价性陈述不转成关系，本次未新增正式边。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, row in enumerate(accepted_lines) if row.startswith("- 04-knowledge/units/") and row[2:] > CARD_REL),
        next((i for i, row in enumerate(accepted_lines) if row == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("dry-run passed: cand-2147 and cand-2148 form one source-local Giovanni Ricci group")
        print("p.238 mention ledger repair and seven relation-candidate links verified; prior undecided reason preserved")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; mentions={len(mentions):,}->{len(planned_mentions):,}")
        print("S4 registered=532 groups/666 candidates; pending=4,272 groups/4,313 candidates; relation table unchanged")
        print("planned writes: person card, alignment.csv, mentions.csv, ku-manifest.csv, accepted.yml, process record, result")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    sync.write_csv(MENTIONS_PATH, mention_fields, planned_mentions)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Giovanni Ricci registered; manifest={len(planned_manifest)}; mentions={len(planned_mentions)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
