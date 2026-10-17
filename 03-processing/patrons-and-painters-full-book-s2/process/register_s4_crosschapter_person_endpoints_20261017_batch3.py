from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

ITEMS = (
    {
        "candidate": "cand-1688",
        "group": "new-person:lady-mary-montagu-wortley-e31f25b442",
        "ku_id": "units/persons/lady-mary-wortley-montagu",
        "card_rel": "04-knowledge/units/persons/lady-mary-wortley-montagu.md",
        "canonical_name": "玛丽·沃特利·蒙塔古夫人（Lady Mary Wortley Montagu）",
        "name_en": "Lady Mary Wortley Montagu",
        "anchor": "s4-person-lady-mary-wortley-montagu-20261017",
        "description_cn": "第10章以Mary Wortley Montagu具名，记述她认为Smith自述为她服务时的自我夸耀令人难以忍受；第14章又以Lady Mary Wortley Montagu具名，叙述Algarotti周旋于她与Lord Hervey的示好。两处姓名与称谓共同支持同一人物身份。",
        "description_en": "Chapter 10 names Mary Wortley Montagu and says she found Smith’s self-congratulation over a service to her overwhelming. Chapter 14 names Lady Mary Wortley Montagu while recounting Algarotti’s handling of her and Lord Hervey’s advances. The two forms refer to the same person in the book.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "lines": [392],
                "location": "第10章，印刷页302；OCR L392",
                "span": "line 392; print p. 302",
                "quote": "Mary Wortley Montagu found the self-congratulation with which he rendered her a service overwhelming",
                "summary": "哈斯克尔称Mary Wortley Montagu认为Smith自我夸耀其为她效劳的做法令人难以忍受。",
            },
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "lines": [25],
                "location": "第14章，印刷页349；OCR L25",
                "span": "line 25; print p. 349",
                "quote": "With some cynicism he played off the advances of Lord Hervey and Lady Mary Wortley Montagu, both of whom were enraptured by him.",
                "summary": "哈斯克尔称Algarotti带有几分玩世不恭地应对Lord Hervey与Lady Mary Wortley Montagu的示好。",
            },
        ),
        "statement_ids": (
            "st-chp10-p302-montagu-service",
            "st-chp14-p349-social-advances-montagu",
        ),
    },
    {
        "candidate": "cand-0919",
        "group": "new-person:denis-diderot-940e9e0035",
        "ku_id": "units/persons/denis-diderot",
        "card_rel": "04-knowledge/units/persons/denis-diderot.md",
        "canonical_name": "德尼·狄德罗（Denis Diderot）",
        "name_en": "Denis Diderot",
        "anchor": "s4-person-denis-diderot-20261017",
        "description_cn": "第14章记载Diderot对Algarotti把画作遗赠给普鲁士国王与老Pitt一事作出讽刺评论，并在注释中经Treat转引一段法文；第20章后记再次提到该讽刺。本条保留原书的转述链，不据此确认引文的原始文本或完整语境。",
        "description_en": "Chapter 14 says Diderot made sarcastic comments about Algarotti’s bequests of pictures to the king of Prussia and the elder Pitt, and reproduces a French passage through Treat. The postscript in chapter 20 refers to the sarcasm again. This entry preserves the book’s attribution chain without claiming independent confirmation of the original text or its full context.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "lines": [102],
                "location": "第14章，印刷页356；OCR L102",
                "span": "line 102; print p. 356",
                "quote": "a gesture that aroused sarcastic comments from Diderot.",
                "summary": "哈斯克尔称Algarotti向普鲁士国王和老Pitt遗赠画作的举动招致Diderot的讽刺评论。",
            },
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "lines": [198],
                "location": "第14章，印刷页356，注5；OCR L198",
                "span": "line 198; print p. 356, note 5",
                "quote": "je trouve plus de vanité à cela qu’à son épitaphe",
                "summary": "哈斯克尔注明该法文评语经Treat第209页转引；Diderot称这比墓志铭更显虚荣。",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "lines": [191],
                "location": "第20章后记，印刷页409；OCR L191",
                "span": "line 191; print p. 409",
                "quote": "much to the sarcastic^amusement of Diderot",
                "summary": "哈斯克尔在后记中再次提及Diderot对Algarotti遗赠行为的讽刺反应；本地OCR在sarcastic与amusement之间保留插入符号。",
            },
        ),
        "statement_ids": (
            "st-chp14-p356-diderot-sarcastic-reaction-to-bequest",
            "st-chp14-p356-note5-treat-diderot-quotation",
        ),
    },
)


def insert_accepted(text: str, card_rel: str) -> str:
    lines = text.splitlines()
    assert f"- {card_rel}" not in lines
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def card_text(item: dict[str, object]) -> str:
    sources = []
    for source in item["sources"]:
        sources.append({
            "citation": BOOK_CITATION,
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["span"], "text": source["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source["file"],
                "source_span": source["span"],
            },
        })
    fm = {
        "title": item["canonical_name"],
        "name_en": item["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}",
    }
    frontmatter = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    links = "；".join(
        f"[来源{index}](../../../{source['file']}#L{source['lines'][0]})"
        for index, source in enumerate(item["sources"], start=1)
    )
    relations = "、".join(f"`{sid}`" for sid in item["statement_ids"])
    body = f"""## 内容

### 描述

**中文：** {item['description_cn']} {links}

**English:** {item['description_en']} {links}

### 本章相关内容

本卡仅记录哈斯克尔在所引章节中的人物身份及必要语境，不补写来源未提供的生卒、亲缘或履历信息。

## 关系与证据

### 关系记录

本任务未新增正式关系。直接S2关系候选{relations}留待S6逐条裁决。
"""
    return f"---\n{frontmatter}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two cross-chapter person identity groups as S4 KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id)
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    cards: list[tuple[dict[str, object], str, Path]] = []
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    for item in ITEMS:
        cid = str(item["candidate"])
        row = decisions[cid]
        assert candidate_by_id[cid].get("suggested_type") == "person"
        assert row.get("decision") == "new" and not row.get("ku_id"), (cid, row)
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        group_members = {
            other["candidate_id"] for other in alignments
            if other.get("candidate_id") and not other.get("external_source")
            and other.get("decision") == "new"
            and sync.get_group(other.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        card_path = ROOT / str(item["card_rel"])
        assert not card_path.exists() and str(item["card_rel"]) not in accepted
        assert not any(entry.get("ku_id") == item["ku_id"] or entry.get("card_path") == item["card_rel"] for entry in manifest)
        assert not any(
            entry.get("type") == "person"
            and entry.get("name_en", "").casefold() == str(item["name_en"]).casefold()
            for entry in manifest
        ), item["name_en"]

        for source in item["sources"]:
            source_text = " ".join((ROOT / str(source["file"])).read_text(encoding="utf-8-sig").split())
            assert " ".join(str(source["quote"]).split()) in source_text, (cid, source)

        direct = [
            statement for statement in statements
            if statement.get("subject_candidate_id") == cid or statement.get("object_candidate_id") == cid
        ]
        relation_ids = {
            statement["statement_id"] for statement in direct
            if (statement.get("qualifiers") or {}).get("relation_candidate") is True
        }
        assert relation_ids == set(item["statement_ids"]), (cid, relation_ids, item["statement_ids"])

        planned_by_id[cid]["ku_id"] = item["ku_id"]
        planned_by_id[cid]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}"
        planned_by_id[cid]["resolution_note"] += (
            f" S4 registration ({DATE}): {item['group']} maps to {item['ku_id']}; "
            "cross-chapter source identity registered; no independent external identity verification or formal S6 relation is implied."
        )
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "person",
            "canonical_name": item["canonical_name"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })
        card = card_text(item)
        fm = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert fm and isinstance(yaml.safe_load(fm.group(1)), dict)
        cards.append((item, card, card_path))

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_append = f"""

### S4 person：跨章人物关系端点——Lady Mary Wortley Montagu 与 Denis Diderot（{DATE}）

`cand-1688`（{ITEMS[0]['group']}）依据第10章与第14章的全名、头衔及语境登记为[Lady Mary Wortley Montagu](../units/persons/lady-mary-wortley-montagu.md)。`cand-0919`（{ITEMS[1]['group']}）依据第14章与第20章后记的姓名和回指登记为[Denis Diderot](../units/persons/denis-diderot.md)；第14章注释明确将法文引语经Treat转引。两组各新增一个person KU；4条直接S2关系候选均待S6，未新增正式边或外部核验状态。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-montagu-diderot-20261017"></a>

### S4 person：两组跨章人物关系端点（{DATE}）

- `cand-1688`（`{ITEMS[0]['group']}`）登记至[Lady Mary Wortley Montagu](../../../04-knowledge/units/persons/lady-mary-wortley-montagu.md)。第10章p.302与第14章p.349分别给出Mary Wortley Montagu和Lady Mary Wortley Montagu，并记录不同语境；两项姓名与书内指代支持同一人物身份。两个直接关系候选均保留待S6。
- `cand-0919`（`{ITEMS[1]['group']}`）登记至[Denis Diderot](../../../04-knowledge/units/persons/denis-diderot.md)。第14章p.356正文及注5、第二版后记p.409再次提及其对Algarotti遗赠行为的讽刺反应；法文原话在书中注明经Treat转引，本次未独立核对Treat原书。两条直接关系候选均保留待S6。
- 两组新增2个person KU和2条候选映射；4条直接S2关系候选保持待S6，不登记正式关系、不添加外部身份核验状态。

`cand-1688` and `cand-0919` are registered as separate person KUs based on cross-chapter names and references. Haskell's Diderot quotation is explicitly mediated through Treat and was not independently checked. All four direct relation candidates remain pending S6; no formal relations or external identity status were added.

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = PROCESS.read_text(encoding="utf-8-sig").rstrip() + process_append
    accepted_next = accepted
    for item, _, _ in cards:
        accepted_next = insert_accepted(accepted_next, str(item["card_rel"]))

    if args.dry_run:
        print("dry-run passed: " + "; ".join(f"{item['candidate']} -> {item['ku_id']}" for item in ITEMS))
        print(
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        print("verified_direct_relation_candidates=4; no external verification status or S6 formal relation rows will be written; no files changed")
        return 0

    for _, card, card_path in cards:
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_next, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
