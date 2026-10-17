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
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-dati-animuccia-simonini-20261017"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-0905",
        "group": "new-person:carlo-dati-621c03d9fe",
        "ku": "units/persons/carlo-dati",
        "name_zh": "卡洛·达蒂",
        "name_en": "Carlo Dati",
        "index_entry": "D.csv#7",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/D.csv",
        "index_quote": "Dati, Carlo",
        "body_source": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "source_fragments": [
            "Carlo Dati, his Florentine disciple and friend",
            "This portrait forms the frontispiece to Carlo Dati’s panegyric.",
        ],
        "sources": [
            {
                "location": "第4章，印刷页108；OCR L116",
                "summary": "Haskell称 Carlo Dati 为 Cassiano 的佛罗伦萨门生与友人，并评论其关于 Cassiano 宗教观点与反炼金术的篇幅。",
                "span": "line 116; print p. 108",
                "quotes": [("line 116", "Carlo Dati, his Florentine disciple and friend")],
            },
            {
                "location": "第4章注释；OCR L240；索引定位 p. 100n",
                "summary": "注释称 Cassiano 的一幅肖像是 Carlo Dati 颂文的卷首图。",
                "span": "line 240; chapter-four note; index locator p. 100n",
                "quotes": [("line 240", "This portrait forms the frontispiece to Carlo Dati’s panegyric.")],
            },
        ],
        "description_zh": (
            "Haskell在讨论Cassiano dal Pozzo对科学的兴趣时，将Carlo Dati称为其佛罗伦萨门生与友人，"
            "并提及Dati关于Cassiano宗教观点及其对炼金术之厌恶的论述。第4章注释另称Cassiano的一幅肖像"
            "是Dati颂文的卷首图。本卡仅登记书内具名人物及其有限语境，不补充外部生平或文献身份。"
        ),
        "description_en": (
            "In discussing Cassiano dal Pozzo’s interest in science, Haskell calls Carlo Dati his Florentine disciple and friend, "
            "and refers to Dati’s discussion of Cassiano’s religious views and detestation of alchemy. A chapter-four note also "
            "says that a portrait of Cassiano formed the frontispiece to Dati’s panegyric. This card records the person and limited "
            "context named in the book; it adds no external biography or bibliographic identity."
        ),
        "location": "第4章，印刷页108及注释 OCR L240",
        "index_file_quote": "Dati, Carlo",
        "relation_ids": [
            "st-chp4-sec-ii-l109-119-dati-disciple-friend",
            "st-chp4-sec-ii-l109-119-dati-friend-cassiano",
            "st-chp4-sec-ii-l109-119-dati-pages-about-cassiano-orthodoxy-alchemy",
        ],
    },
    {
        "candidate": "cand-0108",
        "group": "new-person:animuccia-giovanni-221f8cfa79",
        "ku": "units/persons/giovanni-animuccia",
        "name_zh": "乔万尼·阿尼穆恰",
        "name_en": "Giovanni Animuccia",
        "index_entry": "A.csv#109",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
        "index_quote": "Animuccia, Giovanni",
        "body_source": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
        "source_fragments": ["composer Giovanni Animuccia as early as 1563"],
        "sources": [
            {
                "location": "第3章，印刷页70；OCR L55",
                "summary": "Haskell称 Giovanni Animuccia 为作曲家，并引用一段标为1563年的第一人称陈述，涉及祈祷所音乐。",
                "span": "line 55; print p. 70",
                "quotes": [("line 55", "composer Giovanni Animuccia as early as 1563")],
            },
        ],
        "description_zh": (
            "第3章在叙述圣哲罗姆祈祷所的音乐时称Giovanni Animuccia为作曲家，并引述一段标为1563年的陈述，"
            "涉及祈祷所初期与后续音乐出版的变化。本卡只记录原书明示的姓名和作曲家身份，不补充个人生平，"
            "也不独立核验该引文的版本。"
        ),
        "description_en": (
            "In its account of music at the Oratory of S. Girolamo, Chapter 3 identifies Giovanni Animuccia as a composer "
            "and quotes a statement dated as early as 1563 about changes in the Oratory’s musical publications. This card "
            "records only the name and composer identity stated in the book; it adds no biography and does not independently "
            "verify the quoted text’s edition."
        ),
        "location": "第3章，印刷页70",
        "index_file_quote": "Animuccia, Giovanni",
        "relation_ids": [
            "st-chp3-secii-l54-60-animuccia-first-book-intent",
            "st-chp3-secii-l54-60-animuccia-oratory-growth-and-second-book",
            "st-chp3-secii-l54-60-haskell-musical-shift",
        ],
    },
    {
        "candidate": "cand-2435",
        "group": "new-person:francesco-simonini-44f28a129e",
        "ku": "units/persons/francesco-simonini",
        "name_zh": "弗朗切斯科·西蒙尼尼",
        "name_en": "Francesco Simonini",
        "index_entry": "S.csv#123",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/S.csv",
        "index_quote": "Simonini, Francesco",
        "body_source": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "source_fragments": [
            "Francesco Simonini",
            "His principal battles were painted by Simonini",
            "whom he apparently took on his campaigns",
        ],
        "sources": [
            {
                "location": "第10章，印刷页312；OCR L20",
                "summary": "Haskell列 Francesco Simonini 为 Schulenburg 的肖像画家之一，并称 Simonini 绘制其主要战役场景。",
                "span": "line 20; print p. 312",
                "quotes": [
                    ("line 20", "Francesco Simonini"),
                    ("line 20", "His principal battles were painted by Simonini"),
                ],
            },
        ],
        "description_zh": (
            "第10章列Francesco Simonini为Schulenburg的肖像画家之一，并称其绘制Schulenburg的主要战役场景。"
            "Haskell谨慎地说Schulenburg似乎曾带Simonini随军出征；本卡保留这一不确定表述，仅记录书内人物身份与语境。"
        ),
        "description_en": (
            "Chapter 10 lists Francesco Simonini among the painters of Schulenburg’s portraits and says Simonini painted "
            "Schulenburg’s principal battles. Haskell cautiously says that Schulenburg apparently took Simonini on campaigns; "
            "this qualification is retained. The card records only the person and context in the book."
        ),
        "location": "第10章，印刷页312",
        "index_file_quote": "Simonini, Francesco",
        "relation_ids": [
            "st-chp10-p312-simonini-battles-and-campaigns",
            "st-chp10-p312-simonini-painted-portraits-of",
            "st-chp10-p312-schulenburg-battle-paintings-created-by-simonini",
        ],
    },
]


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
    relation_ids = ", ".join(t["relation_ids"])
    body_link = f"[{t['location']}](../../../{t['body_source']})"
    index_link = f"[索引 {t['index_entry']}](../../../{t['index_file']})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']}〔{body_link}；{index_link}〕

**English:** {t['description_en']} ({body_link}; {index_link})

### 名称与身份

- 原书姓名：{t['name_en']}；中文显示名为本项目工作音译。
- 身份范围：限于本书正文、注释与索引所支持的同名人物，不添加外部生平或身份标识。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。{len(t['relation_ids'])} 条直接 S2 关系候选（{relation_ids}）保留待 S6 审查；本卡登记不等于关系裁决。逐组裁决记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-dati-animuccia-simonini-20261017)。
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
    parser = argparse.ArgumentParser(description="Register three reviewed person relation-endpoint groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    statement_rows = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statements = {row["statement_id"]: row for row in statement_rows}
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
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
        assert members == [cid], f"unexpected identity-group members for {group}: {members}"
        card_rel = f"04-knowledge/{ku}.md"
        assert not any(row.get("ku_id") == ku for row in manifest)
        assert not (ROOT / card_rel).exists()
        assert card_rel not in accepted_lines
        assert not any(
            row.get("type") == "person" and row.get("name_en", "").casefold() == t["name_en"].casefold()
            for row in manifest
        ), f"same-name person KU already exists: {t['name_en']}"
        body = (ROOT / t["body_source"]).read_text(encoding="utf-8-sig")
        assert all(fragment in body for fragment in t["source_fragments"]), f"body evidence missing for {cid}"
        index_bytes = (ROOT / t["index_file"]).read_bytes()
        try:
            index = index_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            index = index_bytes.decode("cp1252")
        assert t["index_quote"] in index, f"index evidence missing for {cid}"
        relations = [
            statements[sid] for sid in t["relation_ids"]
            if sid in statements
        ]
        assert len(relations) == len(t["relation_ids"])
        assert all(
            (row.get("qualifiers") or {}).get("relation_candidate") is True
            and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
            for row in relations
        ), f"direct relation-candidate set mismatch for {cid}"
        card = make_card(t)
        frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)
        cards[ROOT / card_rel] = card
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

    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    next_process = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    anchor = '<a id="s4-person-endpoints-dati-animuccia-simonini-20261017"></a>'
    assert anchor not in next_process
    next_process = next_process.rstrip() + (
        f"\n\n{anchor}\n\n### S4 person：三个直接关系端点身份组登记（{DATE}）\n\n"
        "本批按 person 类型登记三个单成员 S3 new 身份组，每组对应一个双语 KU。仅依据 Haskell 正文、注释与索引记录书内身份；"
        "未添加外部生平、身份标识或正式关系。\n\n"
    )
    for t in TARGETS:
        next_process += (
            f"- {t['candidate']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）]"
            f"(../../../04-knowledge/{t['ku']}.md)（{t['ku']}）。书内锚点：{t['location']}；索引 {t['index_entry']}；"
            f"{len(t['relation_ids'])} 条直接 S2 关系候选留待 S6：{', '.join(t['relation_ids'])}。\n"
        )
    next_process += (
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
    assert count == 1, "could not refresh the current strict-stage pending-mapping count"
    next_result += (
        f"\n\n### S4 person：三个直接关系端点身份组登记（{DATE}）\n\n"
        + "\n".join(
            f"- {t['candidate']} → [{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)；"
            f"{len(t['relation_ids'])} 条直接关系候选留待 S6。"
            for t in TARGETS
        )
        + "\n\n本批未新增正式关系或外部身份核验。"
    )

    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert totals["registered_groups"] == 660
    assert totals["pending_groups"] == 4127
    assert totals["pending_members"] == 4153
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
        f"applied: groups={len(TARGETS)}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
