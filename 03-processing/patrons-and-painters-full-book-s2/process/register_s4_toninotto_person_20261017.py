from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
GROUP = "new-person:giuseppe-toninotto-7d1c034d26"
KU_ID = "units/persons/padre-giuseppe-toninotto"
CARD_REL = "04-knowledge/units/persons/padre-giuseppe-toninotto.md"
CANDIDATE_ID = "cand-2643"
RELATION_STATEMENTS = {
    "st-chp16-p376-toninotto-showed-tourists-around-frari",
    "st-chp16-p376-toninotto-disgrace-with-state-inquisition",
    "st-chp16-p376-toninotto-del-pian-prints-after-carpaccio",
    "st-chp16-p376-toninotto-vecchia-works",
    "st-chp16-p376-toninotto-zais-works",
    "st-chp16-p376-toninotto-guardi-works",
    "st-chp16-p376-toninotto-guardi-capricci",
    "st-chp16-p376-toninotto-unnamed-venetian-views",
}


def make_card() -> str:
    sources = [
        {
            "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
            "location": "第16章；印刷页376；OCR L43–44",
            "span": "lines 43–44; print p. 376",
            "summary": "Haskell称其为多明我会士 Padre Giuseppe Toninotto，并将其置于威尼斯收藏者群体中。",
            "quotes": [("lines 43–44", "More modest than any of these but with similar tastes was the Dominican Padre Giuseppe Toninotto.")],
        },
        {
            "source_file": "02-sources/03-Index/03-1-Index-MD/T.md",
            "location": "规范化书后索引；T.csv#106；印刷页376",
            "span": "index entry T.csv#106",
            "summary": "书后索引以 Toninotto, Padre Giuseppe 定位第376页。",
            "quotes": [("index entry T.csv#106", "| Toninotto, Padre Giuseppe |  |  |  | 376 |")],
        },
        {
            "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
            "location": "第16章；印刷页376；OCR L44",
            "span": "line 44; print p. 376",
            "summary": "同一段落称 Toninotto 帮助记录和收藏威尼斯艺术，并记述其1785年负责出版一组版画。",
            "quotes": [("line 44", "In 1785 he was responsible for publishing a series of nine large prints by Giovanni del Pian of Carpaccio’s famous scenes of the Life of St Ursula.")],
        },
    ]
    frontmatter = {
        "title": "朱塞佩·托尼诺托神父（Padre Giuseppe Toninotto）",
        "name_en": "Padre Giuseppe Toninotto",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)",
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [
                    {"source_span": span, "text": quote}
                    for span, quote in item.get("quotes", [])
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": item["source_file"],
                    "source_span": item["span"],
                },
            }
            for item in sources
        ],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    body = """## 内容

### 描述

**中文：** Haskell 在讨论威尼斯收藏者时称其为多明我会士 Padre Giuseppe Toninotto，并说他较此前人物低调但趣味相近。第16章 p.376 以全名称其，并将其置于记录、收藏威尼斯艺术的语境中。此卡登记书内人物身份，不补充外部生平或修会履历。[第16章 p.376](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L43–45）；[书后索引](../../../02-sources/03-Index/03-1-Index-MD/T.md)（T.csv#106）

**English:** In his discussion of Venetian collectors, Haskell identifies him as the Dominican Padre Giuseppe Toninotto and says he was more modest than the preceding figures but had similar tastes. Chapter 16, p.376, gives his personal name and places him in the account of recording and collecting Venetian art. This card registers the person as identified in the book and adds no external biography or religious history. [Chapter 16, p.376](../../../02-sources/02-Markdown/16_CHP-16_intro.md) (L43–45); [Index](../../../02-sources/03-Index/03-1-Index-MD/T.md) (T.csv#106)

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 书内称谓 | Padre Giuseppe Toninotto | 第16章 p.376，L43–44 |
| 索引形式 | Toninotto, Padre Giuseppe | 书后索引 T.csv#106 |

### 身份

| 字段 | 值 | 证据 |
|---|---|---|
| 修会身份 | Dominican（多明我会士；按 Haskell 的称谓） | 第16章 p.376，L43–44 |

## 关系与证据

### 身份与外部链接

当前身份依据为本书第16章全名与书后索引定位；本轮未新增外部身份标识或外部生平资料。

### 关系记录

本轮未写入正式关系。第16章 p.376 的八条 S2 关系候选继续保留待 S6，部分作品端点仍为 `undecided`；逐条状态和候选映射见[过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。
"""
    return f"---\n{yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S3 Giuseppe Toninotto person group as one S4 KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate = candidate_by_id[CANDIDATE_ID]
    alignment = alignment_by_id[CANDIDATE_ID]
    assert candidate["canonical_name"] == "Toninotto, Padre Giuseppe"
    assert candidate["suggested_type"] == "person" and candidate["index_entry_id"] == "T.csv#106"
    assert candidate["index_page_range"] == "376"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not (ROOT / CARD_REL).exists()
    assert CARD_REL not in ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert not any(row.get("decision") == "same" and row.get("ku_id") == KU_ID for row in alignments)

    chapter = (ROOT / "02-sources/02-Markdown/16_CHP-16_intro.md").read_text(encoding="utf-8-sig")
    index = (ROOT / "02-sources/03-Index/03-1-Index-MD/T.md").read_text(encoding="utf-8-sig")
    assert "More modest than any of these but with similar tastes was the Dominican Padre\nGiuseppe Toninotto." in chapter
    assert "In 1785 he was responsible for publishing a series of nine large prints by Giovanni del Pian" in chapter
    assert "| Toninotto, Padre Giuseppe |  |  |  | 376 |" in index

    statements = sync.load_statements()
    relation_rows = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE_ID
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert {row["statement_id"] for row in relation_rows} == RELATION_STATEMENTS
    endpoint_status = {}
    for row in relation_rows:
        oid = row.get("object_candidate_id")
        if not oid:
            continue
        endpoint_status[oid] = alignment_by_id[oid]["decision"]
    assert endpoint_status == {
        "cand-10642": "new",
        "cand-10524": "new",
        "cand-10636": "new",
        "cand-10646": "undecided",
        "cand-10637": "undecided",
        "cand-10638": "undecided",
        "cand-10639": "undecided",
        "cand-10640": "undecided",
    }

    planned_alignments = [dict(row) for row in alignments]
    planned_alignment_by_id = {
        row["candidate_id"]: row for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_alignment_by_id[CANDIDATE_ID]["ku_id"] = KU_ID
    planned_alignment_by_id[CANDIDATE_ID]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "朱塞佩·托尼诺托神父",
        "name_en": "Padre Giuseppe Toninotto",
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_replacements = [
        ("| [既有字段表](../tables/enrichment.jsonl) | 10,478条，其中1,580条 unverified |",
         "| [既有字段表](../tables/enrichment.jsonl) | 10,481条，其中1,583条 unverified |"),
        ("审计警告中的4,563条待登记 `decision=new` alignment 行，含4,548条候选决定映射（4,477组）和15条外部身份记录。",
         "审计警告中的4,562条待登记 `decision=new` alignment 行，含4,547条候选决定映射（4,476组）和15条外部身份记录。"),
    ]
    for old, new in result_replacements:
        assert old in result_text, old
        result_text = result_text.replace(old, new, 1)

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4 person：Giuseppe Toninotto 直接关系端点登记（2026-10-17）\n\n"
        f"候选 `cand-2643`（T.csv#106）保持 S3 人物组 `{GROUP}`，登记至[朱塞佩·托尼诺托人物卡](../../../{CARD_REL})，一组一 KU。第16章 p.376 明称其为 Dominican Padre Giuseppe Toninotto；规范化索引以反序形式列出 Toninotto, Padre Giuseppe。当前 accepted/manifest 中无同类型同一人物卡，本轮只登记书内身份，不补充外部生平或身份标识。"
        f"该人作为主体的8条 S2 relation_candidate 原样保留：Frari 导览、宗教裁判所处分、1785年版画出版、两件 della Vecchia 作品、Zais 绘画与素描、Guardi 绘画、四件 capricci、四幅威尼斯风景。后四个作品端点 `cand-10637`–`cand-10640` 及 `cand-10646` 当前为 `undecided`；Frari `cand-10642`、State Inquisition `cand-10524` 与 del Pian 版画 `cand-10636` 仍是 S3 `new`、待各自 S4。因对象端点未全部登记或消歧，本轮未写正式关系，未新加 backlog 行。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Giuseppe Toninotto 直接端点（2026-10-17）\n\n"
        f"`cand-2643` 映射至 `{KU_ID}`。其8条直接 S2 关系候选保留待 S6；Frari、State Inquisition 与 Del Pian 版画候选待 S4，其余相关作品候选仍待身份消歧。未登记正式关系。"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    card_text = make_card()
    if args.dry_run:
        print("S4 Toninotto direct-endpoint person-group dry-run passed")
        print(f"{CANDIDATE_ID} -> {KU_ID}; eight S2 relation candidates remain unchanged")
        print("Frari, State Inquisition and Del Pian print candidates remain new; five collection-work endpoints remain undecided")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        print("no files changed")
        return 0

    card_path = ROOT / CARD_REL
    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE_ID} -> {KU_ID}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
