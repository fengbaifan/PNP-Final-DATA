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
CANDIDATES_PATH = TABLES / "entity-candidates.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
GROUP = "new-person:abbate-giustiniani-michele-496853d11b"
KU_ID = "units/persons/abbate-michele-giustiniani"
CARD_REL = "04-knowledge/units/persons/abbate-michele-giustiniani.md"
CANDIDATES = ("cand-1199", "cand-4388")


def make_card() -> str:
    sources = [
        {
            "source_file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
            "location": "第2章；印刷页31；注5；OCR L157",
            "span": "line 157; print p. 31 note 5",
            "summary": "Haskell称 Prince Francesco Colonna 的来信由 Michele Giustiniani 第I卷第116页刊布；来源 OCR 将 Abbate 误作 Abbatc。",
            "quotes": [("line 157", "Michele Giustiniani, I, p. 116")],
        },
        {
            "source_file": "02-sources/02-Markdown/04_CHP-4_intro.md",
            "location": "第4章注释；索引定位 p.94n；OCR L13",
            "span": "line 13; index G.csv#106, p. 94n",
            "summary": "Haskell称一封信于1675年由 Abate Michele Giustiniani 首次刊布，并指向第III卷第417页。",
            "quotes": [("line 13", "published for the first time by the Abate Michele Giustiniani in 1675 (III, p. 417)")],
        },
        {
            "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            "location": "第4章；印刷页115；OCR L189",
            "span": "line 189; print p. 115",
            "summary": "Haskell在讨论 elder Camillo 时引用 Abbate Michele Giustiniani 第II卷第62–63页。",
            "quotes": [("line 189", "For the first Camillo see Abbate Michele Giustiniani, II, pp. 62-3")],
        },
        {
            "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            "location": "第4章注释；OCR L297、306",
            "span": "lines 297, 306; citations to volumes II and III",
            "summary": "两条注文分别引用 Abbate Michele Giustiniani 第II卷第471页和第III卷第567页。",
            "quotes": [
                ("line 297", "Abbate Michele Giustiniani, II, p. 471"),
                ("line 306", "Abbate Michele Giustiniani, III, p. 567"),
            ],
        },
        {
            "source_file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md",
            "location": "第6章；印刷页158注3；OCR L61",
            "span": "line 61; print p. 158 note 3",
            "summary": "Haskell在 Adami 引文的注文中引用 Abbate Michele Giustiniani 第I卷第336页。",
            "quotes": [("line 61", "Abbate Michele Giustiniani, I, p. 336")],
        },
        {
            "source_file": "02-sources/03-Index/03-1-Index-MD/G.md",
            "location": "规范化书后索引；G.csv#106",
            "span": "index entry G.csv#106",
            "summary": "书后索引列 Giustiniani, Abbate Michele，定位第94页注文。",
            "quotes": [("index entry G.csv#106", "Giustiniani, Abbate Michele |  |  |  | 94n")],
        },
    ]
    frontmatter = {
        "title": "米凯莱·朱斯蒂尼亚尼（Abbate Michele Giustiniani）",
        "name_en": "Abbate Michele Giustiniani",
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

**中文：** Haskell 将其称为 Abate 或 Abbate Michele Giustiniani。第2章注释称一封 Francesco Colonna 来信由 Michele Giustiniani 第I卷第116页刊布；第4章注释称另一封信于1675年首次刊布于其第III卷，并在第4、6章以同一姓名引用第I至III卷。此卡仅代表书内所指人物，不推定完整生平，也不将各卷合并为同一文献版本。[第2章注5](../../../02-sources/02-Markdown/02_CHP-2_sec_i.md)（L157）；[第4章注释](../../../02-sources/02-Markdown/04_CHP-4_intro.md)（L13；索引 G.csv#106）；[第4章](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L189、297、306）；[第6章](../../../02-sources/02-Markdown/06_CHP-6_sec_iv.md)（L61）

**English:** Haskell refers to him as Abate or Abbate Michele Giustiniani. A Chapter 2 note says a letter by Francesco Colonna was published by Michele Giustiniani in volume I, p.116; a Chapter 4 note says another letter was first published in 1675 in his volume III, and Chapters 4 and 6 cite volumes I–III under the same name. This card represents the person named in the book. It does not infer a full biography or merge the cited volumes into one publication or edition. [Chapter 2, note 5](../../../02-sources/02-Markdown/02_CHP-2_sec_i.md) (L157); [Chapter 4 note](../../../02-sources/02-Markdown/04_CHP-4_intro.md) (L13; index G.csv#106); [Chapter 4](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md) (L189, 297, 306); [Chapter 6](../../../02-sources/02-Markdown/06_CHP-6_sec_iv.md) (L61)

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 原文称谓 | Abate Michele Giustiniani；Abbate Michele Giustiniani | 第4章注释 L13；第4章 L189、297、306；第6章 L61 |
| 索引形式 | Giustiniani, Abbate Michele | 书后索引 G.csv#106 |

### 本章相关内容

- 第2章注5将 Prince Francesco Colonna 宣告出售的一封信，指向 Giustiniani 第I卷第116页。
- 第4章注释称一封信于1675年首次刊布在其第III卷第417页；第4章后续注文引用第II卷第62–63页、第471页及第III卷第319、567页；第6章注3引用第I卷第336页。
- 卷册及被引文献的题名、版次与相互关系不在本卡范围内。

## 关系与证据

### 身份与外部链接

当前身份为书内对齐，未新增外部身份标识或外部生平资料。

### 关系记录

本轮没有为该人物新增正式关系。书中对卷册的引用保留为来源陈述；对应 archive 候选的身份与书目细节仍按过程记录待决。
"""
    return f"---\n{yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the existing S3 Abbate Michele Giustiniani person group as one S4 KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(CANDIDATES_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not (ROOT / CARD_REL).exists()
    assert CARD_REL not in ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert all(candidate_by_id[cid]["suggested_type"] == "person" for cid in CANDIDATES)
    assert candidate_by_id["cand-1199"]["index_entry_id"] == "G.csv#106"
    assert candidate_by_id["cand-1199"]["index_page_range"] == "94n"
    prior_detail = candidate_by_id["cand-4388"]["detail"]
    assert "identity" in prior_detail and "unresolved" in prior_detail
    assert all(alignment_by_id[cid]["decision"] == "new" and not alignment_by_id[cid].get("ku_id") for cid in CANDIDATES)
    assert all(sync.get_group(alignment_by_id[cid].get("resolution_note", "")) == GROUP for cid in CANDIDATES)
    assert "identical normalized full-name/explicit-alias anchor" in alignment_by_id["cand-1199"]["resolution_note"]

    source_refs = {
        "02-sources/02-Markdown/02_CHP-2_sec_i.md": "Abbatc Michele Giustiniani, I, p. 116",
        "02-sources/02-Markdown/04_CHP-4_intro.md": "published for the first time by the Abate Michele Giustiniani in 1675 (III, p. 417)",
        "02-sources/02-Markdown/04_CHP-4_sec_ii.md": "For the first Camillo see Abbate Michele Giustiniani, II, pp. 62-3",
        "02-sources/02-Markdown/06_CHP-6_sec_iv.md": "Abbate Michele Giustiniani, I, p. 336",
        "02-sources/03-Index/03-1-Index-MD/G.md": "| Giustiniani, Abbate Michele |  |  |  | 94n |",
    }
    for rel, quote in source_refs.items():
        assert quote in (ROOT / rel).read_text(encoding="utf-8-sig"), (rel, quote)

    candidate_ids = set(candidate_by_id)
    assert "cand-4389" in candidate_ids and "cand-5963" in candidate_ids and "cand-5504" in candidate_ids
    statements = sync.load_statements()
    relevant = [
        row for row in statements
        if row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES
    ]
    assert relevant
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is False for row in relevant)

    planned_candidates = [dict(row) for row in candidates]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}
    planned_candidate_by_id["cand-4388"]["detail"] = (
        "Source-derived person candidate from a footnote: Haskell names Abate Michele Giustiniani as a publisher. "
        "Identity is aligned with index candidate cand-1199. Titles and editions of the cited volumes I–III remain unresolved "
        "on separate archive candidates cand-4389, cand-5963 and cand-5504."
    )

    planned_alignments = [dict(row) for row in alignments]
    planned_alignment_by_id = {
        row["candidate_id"]: row for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        row = planned_alignment_by_id[cid]
        old_note = row["resolution_note"]
        row["ku_id"] = KU_ID
        row["resolution_note"] = (
            old_note
            + f" S4 registration: mapped {GROUP} to {KU_ID}."
            + (f" prior_candidate_detail={prior_detail}" if cid == "cand-4388" else "")
        )

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "米凯莱·朱斯蒂尼亚尼",
        "name_en": "Abbate Michele Giustiniani",
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

    stats = sync.summarize_by_type(planned_candidates, planned_alignments)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4 person：Abbate Michele Giustiniani 跨章人物组登记（2026-10-17）\n\n"
        f"人物组 `{GROUP}` 包含 `cand-1199`（G.csv#106，索引定位 p.94n）与 `cand-4388`（第2章 p.31 注5正文来源候选），登记为一张[人物卡](../../../{CARD_REL})。"
        "索引形式为 ‘Giustiniani, Abbate Michele’；原书第2章以 ‘Abbatc Michele Giustiniani’（OCR字形）称其为一封信的刊布者，第4章注释称 ‘Abate Michele Giustiniani’ 于1675年首次刊布另一封信，第4、6章注文以 ‘Abbate Michele Giustiniani’ 引用卷册I–III。姓名、头衔词形与跨章引用语境支持同一书内人物；不推定完整生平。"
        "仅将人物候选登记至 `units/persons/abbate-michele-giustiniani`。第2、4、6章被引的 volume I/II/III 书目对象不并入人物卡；archive 候选 `cand-4389`、`cand-5963`、`cand-5504` 继续 `undecided`，因为完整题名、版本及卷册间关系尚未确定。相关 S2 statements 均为非关系引用陈述，本轮未新增 `relations.csv` 边，也未添加 backlog 行。候选 `cand-4388` 的旧 detail 将身份和书目缺口混写；现修正为身份已对齐、卷册书目仍待证，旧文字保存在 alignment 历史说明中。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Abbate Michele Giustiniani 跨章人物组（2026-10-17）\n\n"
        f"`cand-1199` 与 `cand-4388` 共同映射至 `{KU_ID}`。第2章将其列为来信刊布者，第4、6章以 Abate/Abbate Michele Giustiniani 引用相关卷册；书目卷册身份继续待证，不与人物或彼此合并。"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    card_text = make_card()
    if args.dry_run:
        print("S4 Abbate Michele Giustiniani person-group dry-run passed")
        print(f"{CANDIDATES} -> {KU_ID}; one card for one identity group")
        print("cited archive-volume candidates remain undecided; no formal relation or backlog row added")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        print("no files changed")
        return 0

    card_path = ROOT / CARD_REL
    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    sync.write_csv(CANDIDATES_PATH, candidate_fields, planned_candidates)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATES} -> {KU_ID}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
