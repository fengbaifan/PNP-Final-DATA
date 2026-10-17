from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-belloni-clostermann-20261017"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-0271",
        "group": "new-person:antonio-belloni-giovanni-da1194d2db",
        "ku": "units/persons/giovanni-antonio-belloni",
        "name_zh": "乔万尼·安东尼奥·贝洛尼",
        "name_en": "Giovanni Antonio Belloni",
        "index_entry": "B.csv#118",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
        "index_quote": "Belloni, Giovanni Antonio",
        "body_source": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "source_fragments": [
            "Giovanni Antonio Belloni",
            "who gave splendid hospitality to the exiled ‘James III’",
            "he sent the last artist on a journey to Rome",
        ],
        "sources": [
            {
                "location": "第8章，印刷页203；OCR L8",
                "summary": "Haskell以全名列出 Giovanni Antonio Belloni，称其接待流亡中的 James III、收藏多位画家的作品，并送 Gambarini 赴罗马。",
                "span": "line 8; print p. 203",
                "quotes": [
                    ("line 8", "Giovanni Antonio Belloni"),
                    ("line 8", "who gave splendid hospitality to the exiled ‘James III’"),
                    ("line 8", "he sent the last artist on a journey to Rome"),
                ],
            },
        ],
        "description_zh": (
            "第8章在叙述博洛尼亚商人对艺术的支持时，以全名称Giovanni Antonio Belloni，记其接待流亡中的James III、"
            "收藏dal Sole、Torelli、Crespi与Gambarini等人的画作，并送Gambarini赴罗马。紧接着原文另称商人"
            "Giovanni Battista Bellucci；本卡保持两人为不同人物。上述收藏与行动仍按S2关系候选留待审查。"
        ),
        "description_en": (
            "In its account of artistic patronage by Bolognese merchants, Chapter 8 names Giovanni Antonio Belloni and says "
            "he gave hospitality to the exiled James III, owned pictures by dal Sole, Torelli, Crespi, and Gambarini, and sent "
            "Gambarini to Rome. The text immediately distinguishes another merchant, Giovanni Battista Bellucci; this card "
            "keeps them as separate people. The collection and activity claims remain S2 relation candidates for review."
        ),
        "location": "第8章，印刷页203",
        "relation_ids": [
            "st-chp8-p203-belloni-collection",
            "st-chp8-p203-belloni-hospitality-james-iii",
            "st-chp8-p203-belloni-sent-gambarini-to-rome",
        ],
    },
    {
        "candidate": "cand-0791",
        "group": "new-person:clostermann-john-ba5d3dbe8f",
        "ku": "units/persons/john-clostermann",
        "name_zh": "约翰·克洛斯特曼",
        "name_en": "John Clostermann",
        "index_entry": "C.csv#321",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/C.csv",
        "index_quote": "Clostermann, John",
        "body_source": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "source_fragments": [
            "portrait painter John Closterman",
            "Closterman sent him some drawings of Prudence and Justice by Domenico Guidi",
            "At the same time Closterman, who had already painted a full-length portrait",
        ],
        "sources": [
            {
                "location": "第7章，印刷页198；OCR L82–83",
                "summary": "Haskell在正文拼作 John／Closterman，称其为肖像画家，并叙述其受 Shaftesbury 派往罗马寻找雕塑家、寄送 Guidi 图稿及已绘制 Shaftesbury 肖像。",
                "span": "lines 82–83; print p. 198",
                "quotes": [
                    ("line 82", "portrait painter John Closterman"),
                    ("line 83", "Closterman sent him some drawings of Prudence and Justice by Domenico Guidi"),
                ],
            },
        ],
        "description_zh": (
            "第7章称John Closterman为肖像画家，并叙述Shaftesbury于1699年派他赴罗马寻找可制作一组美德雕像的雕塑家；"
            "Closterman寄来Domenico Guidi的审慎与正义图稿，并曾为Shaftesbury绘制全身肖像。原书索引拼作"
            "Clostermann, John，正文拼作Closterman；本卡保留这项拼写差异，不据此拆分人物。"
        ),
        "description_en": (
            "Chapter 7 calls John Closterman a portrait painter and says Shaftesbury sent him to Rome in 1699 to find a sculptor "
            "for a series of Virtues. Closterman sent drawings of Prudence and Justice by Domenico Guidi and had already painted "
            "a full-length portrait of Shaftesbury. The index spells the surname Clostermann, while the chapter text spells it "
            "Closterman; the difference is retained and does not split the person."
        ),
        "location": "第7章，印刷页198",
        "relation_ids": [
            "st-chp7-p198-closterman-instructions-advice",
            "st-chp7-p198-closterman-shaftesbury-portrait",
            "st-chp7-p198-guidi-drawings-project-failed",
        ],
    },
]


def decode_index(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def make_card(t: dict) -> str:
    sources = []
    for item in t["sources"]:
        sources.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": t["body_source"],
                "source_span": item["span"],
            },
        })
    sources.append({
        "citation": INDEX_CITATION,
        "location": f"全书索引 {t['index_entry']}",
        "sentence_summary": f"索引以 {t['index_quote']} 列出人物主项。",
        "original_quotes": [{"source_span": t["index_entry"], "text": t["index_quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": t["index_file"],
            "source_span": t["index_entry"],
        },
    })
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body_link = f"[{t['location']}](../../../{t['body_source']})"
    index_link = f"[索引 {t['index_entry']}](../../../{t['index_file']})"
    relations = ", ".join(t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']}〔{body_link}；{index_link}〕

**English:** {t['description_en']} ({body_link}; {index_link})

### 名称与身份

- 规范展示名依据书内具名锚点与索引主项；中文名为本项目工作音译。
- 身份范围限于 Haskell 对该人物的记载，本轮未补充外部生平或身份标识。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。{len(t['relation_ids'])} 条直接 S2 关系候选（{relations}）留待 S6 审查；KU 登记不代替关系裁决。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-belloni-clostermann-20261017)。
"""


def insert_accepted(lines: list[str], card_rel: str) -> list[str]:
    entry = f"- {card_rel}"
    assert entry not in lines
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_rel),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Belloni and Clostermann as reviewed person groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    statements = {
        row["statement_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    planned_manifest = [dict(row) for row in manifest]
    cards: dict[Path, str] = {}

    for t in TARGETS:
        cid, group, ku = t["candidate"], t["group"], t["ku"]
        candidate = candidate_by_id[cid]
        alignment = planned_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == group
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == group
        ]
        assert members == [cid], f"unexpected group members for {group}: {members}"
        card_rel = f"04-knowledge/{ku}.md"
        assert not any(row.get("ku_id") == ku for row in manifest)
        assert not (ROOT / card_rel).exists()
        assert card_rel not in accepted_lines
        assert not any(
            row.get("type") == "person" and row.get("name_en", "").casefold() == t["name_en"].casefold()
            for row in manifest
        ), f"same-name person KU already exists: {t['name_en']}"
        source = (ROOT / t["body_source"]).read_text(encoding="utf-8-sig")
        assert all(fragment in source for fragment in t["source_fragments"]), f"body evidence missing for {cid}"
        index = decode_index(ROOT / t["index_file"])
        assert t["index_quote"] in index, f"index evidence missing for {cid}"
        relation_rows = [statements[sid] for sid in t["relation_ids"] if sid in statements]
        assert len(relation_rows) == len(t["relation_ids"])
        assert all(
            (row.get("qualifiers") or {}).get("relation_candidate") is True
            and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
            for row in relation_rows
        ), f"direct relation-candidate set mismatch for {cid}"
        cards[ROOT / card_rel] = make_card(t)
        alignment["ku_id"] = ku
        alignment["process_ref"] = PROCESS_REF
        alignment["resolution_note"] += (
            f" S4 registration ({DATE}): mapped {group} to {ku}; bilingual source-backed person card created. "
            f"{len(t['relation_ids'])} direct S2 relation candidates remain pending S6."
        )
        planned_manifest.append({
            "ku_id": ku,
            "type": "person",
            "canonical_name": t["name_zh"],
            "name_en": t["name_en"],
            "source_task": TASK,
            "card_path": card_rel,
        })

    # The adjacent Bellucci is a separate named person and remains in its own S3 group.
    bellucci = planned_by_id["cand-0285"]
    assert bellucci["decision"] == "new" and sync.get_group(bellucci.get("resolution_note", "")) != TARGETS[0]["group"]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    next_process = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    anchor = '<a id="s4-person-endpoints-belloni-clostermann-20261017"></a>'
    assert anchor not in next_process
    next_process = next_process.rstrip() + (
        f"\n\n{anchor}\n\n### S4 person：Belloni 与 Clostermann 直接关系端点登记（{DATE}）\n\n"
        "本批登记两个单成员 person new 身份组，每组对应一个双语 KU；仅记录书内人物身份与语境，不新增外部生平或正式关系。\n"
    )
    for t in TARGETS:
        next_process += (
            f"- {t['candidate']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）]"
            f"(../../../04-knowledge/{t['ku']}.md)（{t['ku']}）；书内锚点：{t['location']}，索引 {t['index_entry']}；"
            f"{len(t['relation_ids'])} 条直接 S2 关系候选留待 S6：{', '.join(t['relation_ids'])}。\n"
        )
    next_process += (
        "- Belloni 所在段落另列 Giovanni Battista Bellucci；cand-0285 保持独立 new 组，不并入 Belloni。"
        "Closterman／Clostermann 的正文与索引拼写差异在卡片中并列保留。\n"
        f"\nS4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_result = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    next_result, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        next_result,
        count=1,
    )
    assert count == 1
    next_result += (
        f"\n\n### S4 person：Belloni 与 Clostermann 直接关系端点登记（{DATE}）\n\n"
        + "\n".join(
            f"- {t['candidate']} → [{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)；"
            f"{len(t['relation_ids'])} 条直接关系候选留待 S6。"
            for t in TARGETS
        )
        + "\n\nBelloni 与 Giovanni Battista Bellucci 分立；Closterman／Clostermann 拼写差异保留。未新增正式关系或外部身份核验。"
    )

    assert len(planned_manifest) == len(manifest) + 2
    assert totals["registered_groups"] == 662
    assert totals["registered_members"] == 818
    assert totals["pending_groups"] == 4124
    assert totals["pending_members"] == 4150
    if args.dry_run:
        print(
            f"dry-run passed: groups={len(TARGETS)}; cards={len(cards)}; "
            f"direct relation candidates={sum(len(t['relation_ids']) for t in TARGETS)}"
        )
        print(
            f"manifest={len(manifest)}->{len(planned_manifest)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    for path, card in cards.items():
        path.write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=2; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
