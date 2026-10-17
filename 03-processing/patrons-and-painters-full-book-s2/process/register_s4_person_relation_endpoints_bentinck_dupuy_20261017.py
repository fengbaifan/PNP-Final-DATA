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
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-bentinck-dupuy-20261017"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-0289",
        "group": "new-person:bentinck-william-f9cae452d7",
        "ku": "units/persons/william-bentinck",
        "name_zh": "威廉·本廷克",
        "name_en": "William Bentinck",
        "index_entry": "B.csv#136",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
        "index_quote": "Bentinck, William",
        "body_source": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "source_fragments": [
            "the Dutch William Bentinck",
            "whose loyalty to the Orange cause had been rewarded with vast estates",
        ],
        "sources": [
            {
                "location": "第10章，印刷页280；OCR L53",
                "summary": "Haskell称 Henry, Duke of Portland 的父亲为 the Dutch William Bentinck，并称其对 Orange cause 的忠诚获得大量地产作为回报。",
                "span": "line 53; print p. 280",
                "quotes": [
                    ("line 53", "the Dutch William Bentinck"),
                    ("line 53", "whose loyalty to the Orange cause had been rewarded with vast estates"),
                ],
            },
        ],
        "description_zh": (
            "第10章将年轻的Henry（后来的Portland公爵）称作“the Dutch William Bentinck”之子，并记述William Bentinck"
            "对Orange cause的忠诚以大量地产作为回报。标题采用索引主项姓名；本卡限于书内人物身份与原书语境，"
            "不补充完整头衔、生平或外部身份。"
        ),
        "description_en": (
            "Chapter 10 identifies the father of the young Henry, later Duke of Portland, as “the Dutch William Bentinck” and "
            "says his loyalty to the Orange cause was rewarded with vast estates. The title follows the index entry. This card "
            "records the person and context in the book without adding a fuller title, biography, or external identity."
        ),
        "location": "第10章，印刷页280",
        "relation_ids": [
            "st-chp10-p280-bentinck-orange-loyalty-reward",
            "st-chp10-p280-portland-son-of-bentinck",
            "st-chp10-p280-williamiii-favourite-bentinck",
        ],
    },
    {
        "candidate": "cand-0951",
        "group": "new-person:christophe-dupuy-384608af60",
        "ku": "units/persons/christophe-dupuy",
        "name_zh": "克里斯托夫·迪皮",
        "name_en": "Christophe Dupuy",
        "index_entry": "D.csv#53",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/D.csv",
        "index_quote": "Dupuy, Christophe",
        "body_source": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "source_fragments": [
            "Christophe Dupuy, the prior of the Carthusian Order in Rome",
            "showing these to Christophe Dupuy",
            "whose conversation was so restrained",
        ],
        "sources": [
            {
                "location": "第4章，印刷页108；OCR L110",
                "summary": "Haskell称 Christophe Dupuy 为罗马加尔都西会的 prior，并叙述 Cassiano 于1641年向他展示 Bouchard 的文件。",
                "span": "line 110; print p. 108",
                "quotes": [
                    ("line 110", "Christophe Dupuy, the prior of the Carthusian Order in Rome"),
                    ("line 110", "In 1641 we find Cassiano showing these to Christophe Dupuy"),
                ],
            },
        ],
        "description_zh": (
            "第4章称Christophe Dupuy为罗马加尔都西会的prior，并记述Cassiano于1641年向他展示Jean-Jacques Bouchard的"
            "文件；Haskell还说Dupuy此前只认识Bouchard较为克制的“official”一面。本卡保留原书对其职务与语境的有限表述，"
            "不补充外部生平或修会任职年表。"
        ),
        "description_en": (
            "Chapter 4 identifies Christophe Dupuy as the prior of the Carthusian Order in Rome and says Cassiano showed him "
            "Jean-Jacques Bouchard’s papers in 1641. Haskell adds that Dupuy had known only Bouchard’s restrained “official” "
            "persona. The card keeps this limited account of his role and context and adds no external biography or institutional timeline."
        ),
        "location": "第4章，印刷页108",
        "relation_ids": [
            "st-chp4-sec-ii-l109-119-cassiano-shows-papers-to-dupuy",
            "st-chp4-sec-ii-l109-119-dupuy-knew-official-bouchard",
            "st-chp4-sec-ii-l109-119-dupuy-prior-in-rome",
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
    relation_ids = ", ".join(t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']}〔{body_link}；{index_link}〕

**English:** {t['description_en']} ({body_link}; {index_link})

### 名称与身份

- 原书姓名与索引主项指向同一书内人物；中文名为本项目工作音译。
- 身份范围限于 Haskell 的正文及索引记载，本轮未增加外部身份标识或生平资料。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。{len(t['relation_ids'])} 条直接 S2 关系候选（{relation_ids}）保留待 S6 审查；登记 KU 不代表关系裁决。逐组过程见[记录](../../../03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-bentinck-dupuy-20261017)。
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
    parser = argparse.ArgumentParser(description="Register two reviewed person relation-endpoint groups in S4.")
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
        assert not (ROOT / card_rel).exists() and card_rel not in accepted_lines
        assert not any(
            row.get("type") == "person" and row.get("name_en", "").casefold() == t["name_en"].casefold()
            for row in manifest
        ), f"same-name person KU already exists: {t['name_en']}"
        body = (ROOT / t["body_source"]).read_text(encoding="utf-8-sig")
        assert all(fragment in body for fragment in t["source_fragments"]), f"source evidence missing for {cid}"
        assert t["index_quote"] in decode_index(ROOT / t["index_file"]), f"index evidence missing for {cid}"
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

    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = insert_accepted(planned_accepted, f"04-knowledge/{t['ku']}.md")
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    next_process = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    anchor = '<a id="s4-person-endpoints-bentinck-dupuy-20261017"></a>'
    assert anchor not in next_process
    next_process = next_process.rstrip() + (
        f"\n\n{anchor}\n\n### S4 person：Bentinck 与 Dupuy 直接关系端点登记（{DATE}）\n\n"
        "本批按 person 类型登记两个单成员 S3 new 组，各对应一个双语 KU。证据限于 Haskell 正文与书后索引；未添加外部传记或身份标识。\n"
    )
    for t in TARGETS:
        next_process += (
            f"- {t['candidate']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）]"
            f"(../../../04-knowledge/{t['ku']}.md)（{t['ku']}）；书内锚点：{t['location']}；索引 {t['index_entry']}；"
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
    assert count == 1
    next_result += (
        f"\n\n### S4 person：Bentinck 与 Dupuy 直接关系端点登记（{DATE}）\n\n"
        + "\n".join(
            f"- {t['candidate']} → [{t['name_zh']}（{t['name_en']}）](../units/{t['ku']}.md)；"
            f"{len(t['relation_ids'])} 条直接关系候选留待 S6。"
            for t in TARGETS
        )
        + "\n\n本批未新增正式关系或外部身份核验。"
    )

    assert len(planned_manifest) == len(manifest) + 2
    assert totals["registered_groups"] == 665
    assert totals["registered_members"] == 821
    assert totals["pending_groups"] == 4121
    assert totals["pending_members"] == 4147
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
