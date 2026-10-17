from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"
GROUP = "archive-group-3c5e5c17bee5"
MEMBERS = ("cand-10514",)
KU_ID = "units/archives/andrea-memmo-inventory-petizion-488-1792"
CARD_REL = "04-knowledge/units/archives/andrea-memmo-inventory-petizion-488-1792.md"
NAME_ZH = "安德烈亚·梅莫1792年财物清单（Petizion 488）"
NAME_EN = "Andrea Memmo Effects Inventory (Petizion 488, 1792)"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
QUOTE = (
    "3 See the inventory drawn up by Sasso and Viero in the Archivio di Stato, Venice—Petizion 488,\n"
    "30 Gennaio 1792 and 24 Febbraio 1792/3 M.V., part of which Is published by Levi, II, p. 254. "
    "Among the more valuable items in Memmo’s collection was a drawing of the holy family by Mengs. "
    "He also owned several hundred prints but there is rarely any indication of the artist."
)


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    return [{
        "citation": BOOK_CITATION,
        "location": "第15章，印刷页368，注3；Markdown 行99–100；该档案记录及 Levi 所刊部分均未独立查阅。",
        "sentence_summary": (
            "Haskell 指向威尼斯国家档案馆 Petizion 488 中由 Sasso 与 Viero 编制的 Memmo 财物清单，"
            "列出 1792年1月30日及 1792/3年2月24日 M.V. 两个日期，并称其中一部分由 Levi 第二卷第254页刊出；"
            "同注报告清单涉及 Mengs 的圣家图及 Memmo 收藏的数百幅版画。"
        ),
        "original_quotes": [{"source_span": "lines 99–100", "text": QUOTE}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
            "source_span": "lines 99–100; print p. 368, note 3",
        },
    }]


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "archival record",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记 Haskell 第15章所引威尼斯国家档案馆 Petizion 488 中的 Andrea Memmo 财物清单档案记录。注3称清单由 Sasso 与 Viero 编制，涉及1792年1月30日及1792/3年2月24日 M.V. 两个日期，并称部分内容刊于 Levi 第二卷第254页。Haskell 同注提到 Mengs 的圣家图及数百幅版画；这些内容是本书转述，档案原件与 Levi 刊本均未在本轮查阅。

**English:** This card records the Andrea Memmo effects-inventory archival record cited from Petizion 488 in Chapter 15. Note 3 says it was drawn up by Sasso and Viero, gives entries dated 30 January 1792 and 24 February 1792/3 M.V., and states that part was published in volume II of Levi, page 254. Haskell’s note also mentions a Holy Family drawing by Mengs and several hundred prints; these remain Haskell’s report, as neither the archival record nor Levi’s publication was consulted in this pass.

### 档案身份与范围

- **档案定位：** Archivio di Stato, Venice；Petizion 488；据 Haskell 第15章 p.368 注3。未核对馆藏目录、档号层级或原件。
- **日期：** 30 Gennaio 1792；24 Febbraio 1792/3 M.V.。保留来源写法，不折算历法或合并成单一日期。
- **编制者：** Sasso 与 Viero；仅记 Haskell 所给姓氏，不扩展身份。
- **刊布信息：** Haskell 称部分内容见 Levi, vol. II, p.254；刊布版本及其与档案原件的对应范围未独立查阅。
- 本卡指向被引的档案记录／卷宗，不表示具体单件或实物副本已定位。Mengs 图画与数百幅版画是 Haskell 对清单内容的转述，不因此另建具体藏品记录。

### 身份边界

S3 新组 {GROUP} 仅含 archive 候选 cand-10514。它与 Andrea Memmo 人物卡及既有 Torcellan 1963 年人物研究著作分开；S2 所列 Sasso、Viero、Levi、Mengs 等对象不并入本 KU。档案身份登记不验证清单所述内容。

## 关系与证据

当前没有登记正式关系。6条直接 S2 关系候选留待 S6，分别涉及档案形成、保管定位、部分刊布及清单内容；端点与证据须在关系阶段逐项裁决。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Memmo inventory at Petizion 488 in S4")
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
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id for cid in MEMBERS)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and any(term in " ".join(row.values()).casefold() for term in ("petizion 488", "memmo effects inventory"))
        for row in manifest
    )
    source_text = " ".join((ROOT / "02-sources/02-Markdown/15_CHP-15_sec_ii.md").read_text(encoding="utf-8-sig").split())
    assert " ".join(QUOTE.split()) in source_text

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert len(direct) == 6 and len(relations) == 6, (len(direct), len(relations))

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
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
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n### S4 archive：Andrea Memmo Petizion 488 财物清单档案身份组登记（{DATE}）\n\n"
        f"- cand-10514 → {GROUP} → {KU_ID}；Haskell 第15章 p.368 注3将记录定位于 Archivio di Stato, Venice, Petizion 488，列出1792年1月30日及1792/3年2月24日 M.V. 两个日期，并称部分内容刊于 Levi II, p.254。档案原件及刊本未查阅。\n"
        "- 直接 S2 记录6条，全部为关系候选，留待 S6。清单身份不表示清单内容或 Haskell 的 Mengs 图画、版画转述已独立验证；未将任何端点并入本 KU。\n"
        "- 未新增正式关系、外部馆藏身份或 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_process = process_text + process_append

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; sources=1; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
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
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; direct_statements={len(direct)}; "
        f"relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
