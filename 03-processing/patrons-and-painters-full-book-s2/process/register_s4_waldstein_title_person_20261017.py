from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
ITEM = {
    "candidate": "cand-2797",
    "group": "new-person:of-waldstein-9d1421b82c",
    "ku_id": "units/persons/count-of-waldstein-casanova-dux",
    "card_rel": "04-knowledge/units/persons/count-of-waldstein-casanova-dux.md",
    "card_path": ROOT / "04-knowledge" / "units" / "persons" / "count-of-waldstein-casanova-dux.md",
    "type": "person",
    "name_zh": "瓦尔德施泰因伯爵（Casanova 在 Dux 的保护人）",
    "name_en": "Count of Waldstein",
}
STATEMENTS = {
    "st-chp15-p367-casanova-patron-waldstein",
    "st-chp15-p367-waldstein-might-fund-statue",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def card_text() -> str:
    sources = [
        {
            "citation": BOOK,
            "location": "第15章；印刷页367；OCR L33–34",
            "sentence_summary": (
                "Haskell 称 Casanova 在 Dux 的保护人是 Count of Waldstein，并记载 Memmo 询问他是否愿意为 Prà della Valle 的一座雕像出资；"
                "这只是询问，不是承诺或付款。"
            ),
            "original_quotes": [{
                "source_span": "lines 33–34",
                "text": "Memmo wrote to his old friend Casanova and asked whether his patron at Dux, the Count of\nWaldstein, might not be prepared to pay for one—",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "source_span": "lines 33–34; print p. 367",
            },
        },
        {
            "citation": BOOK,
            "location": "书后索引；印刷页473；OCR L3448",
            "sentence_summary": "索引仅列出 Waldstein, Count of 并指向 p.367；没有提供名字。",
            "original_quotes": [{
                "source_span": "line 3448",
                "text": "Waldstein, Count of, 367",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/22_CHP-22Index.md",
                "source_span": "line 3448; print p. 473 (page marker at line 3407)",
            },
        },
    ]
    fm = yaml.safe_dump({
        "title": f"{ITEM['name_zh']}（{ITEM['name_en']}）",
        "name_en": ITEM["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }, allow_unicode=True, sort_keys=False, width=1000)
    p367 = "[第15章 p.367](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L33–34）"
    index = "[书末索引 p.473](../../../02-sources/02-Markdown/22_CHP-22Index.md)（L3448）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记 Haskell 在第15章称为 “the Count of Waldstein” 的特定书内人物：他是 Casanova 在 Dux 的保护人。书末索引也仅列出 “Waldstein, Count of”，未给出名字。Memmo 曾询问他是否愿意为 Prà della Valle 的一座雕像出资；这是可能性问题，不证明他承诺出资、付款或委托作品。{index}；{p367}

**English:** This card registers the source-local person Haskell calls “the Count of Waldstein” in Chapter 15: Casanova’s patron at Dux. The book index likewise lists only “Waldstein, Count of” and supplies no given name. Memmo asked whether he might be willing to pay for a statue for the Prà della Valle; this is a question about possible support, not evidence of a pledge, payment, or commission. {index}; {p367}

### 名称与身份边界

- 索引形式：Waldstein, Count of；定位 p.367。书内未提供名字或其他可用于外部消歧的身份字段。
- 本卡将其作为 p.367 语境中的特定人物登记，依据是其“Casanova 在 Dux 的保护人”角色；不据爵称推定家族支系、名字、生卒或其他履历。
- 该来源内人物身份可与其他 KU 分开识别；历史人物的外部姓名对应尚未核验。本卡不把外部消歧未完成转写成已确认身份。

### 关系与证据

以下关系候选留待 S6；本卡未新增正式关系：

- `st-chp15-p367-casanova-patron-waldstein`：Casanova（已登记人物 KU）；只保留 p.367 的特定顾问／保护人语境。
- `st-chp15-p367-waldstein-might-fund-statue`：`cand-11561`（`undecided`，Prà della Valle 一座未识别雕像的可能资助）；原文仅为询问，不证明资助成立。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-local Count of Waldstein person endpoint in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate = candidate_by_id[ITEM["candidate"]]
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    alignment = alignment_by_id[ITEM["candidate"]]
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert candidate["canonical_name"] == "Waldstein, Count of"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == ITEM["group"]
    assert "source anchor gives a full personal name" in alignment["resolution_note"]
    assert alignment_by_id["cand-0591"].get("ku_id") == "units/persons/jacques-casanova-de-seingalt"
    assert alignment_by_id["cand-11561"]["decision"] == "undecided"
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
        and sync.get_group(row.get("resolution_note", "")) == ITEM["group"]
    ]
    assert [row["candidate_id"] for row in group_rows] == [ITEM["candidate"]]
    assert not ITEM["card_path"].exists() and ITEM["card_rel"] not in accepted
    assert not any(row.get("ku_id") == ITEM["ku_id"] or row.get("card_path") == ITEM["card_rel"] for row in manifest)
    assert not any(
        row["type"] == "person"
        and (row.get("name_en", "").casefold() == ITEM["name_en"].casefold()
             or row.get("canonical_name", "").casefold() == ITEM["name_zh"].casefold())
        for row in manifest
    )

    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = {
        row["statement_id"] for row in statements
        if ITEM["candidate"] in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct == STATEMENTS
    assert all(
        row.get("qualifiers", {}).get("relation_candidate") is True
        for row in statements if row["statement_id"] in STATEMENTS
    )
    chapter = (ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md").read_text(encoding="utf-8-sig")
    index = (ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md").read_text(encoding="utf-8-sig")
    assert "his patron at Dux, the Count of\nWaldstein, might not be prepared to pay for one" in chapter
    assert "Waldstein, Count of, 367" in index

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    target = planned_by_id[ITEM["candidate"]]
    target["ku_id"] = ITEM["ku_id"]
    target["resolution_note"] += (
        " S3 correction 2026-10-17: prior phrase ‘source anchor gives a full personal name’ is inaccurate; "
        "the book gives only the index/title form ‘Waldstein, Count of’. Retain new as a source-local person because "
        "p.367 identifies this singular person by the role ‘Casanova’s patron at Dux’; no given name or external historical identity is asserted."
    )
    target["resolution_note"] += f" S4 registration: mapped {ITEM['group']} to {ITEM['ku_id']}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": ITEM["ku_id"], "type": ITEM["type"], "canonical_name": ITEM["name_zh"],
        "name_en": ITEM["name_en"], "source_task": TASK, "card_path": ITEM["card_rel"],
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3/S4：Waldstein 伯爵称谓的身份限定与端点登记（2026-10-17）\n\n"
        f"候选 `{ITEM['candidate']}` 保持 `{ITEM['group']}`／`new`，登记至[Waldstein 伯爵人物卡]"
        "(../../../04-knowledge/units/persons/count-of-waldstein-casanova-dux.md)。复核更正了 S3 旧备注：书中没有给出名字，索引仅列 “Waldstein, Count of”；"
        "保留 `new` 的范围是 p.367 语境中 Casanova 在 Dux 的特定保护人这一 source-local person，不宣称外部历史身份已确定。"
        "同页另一陈述只询问他是否愿为一座雕像出资，候选 `cand-11561` 仍为 `undecided`；不写成委托或付款。"
        "两条关系候选均待 S6，未写入 `relations.csv`。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S3/S4：Waldstein 伯爵称谓限定（2026-10-17）\n\n"
        f"`{ITEM['candidate']}` 保持 source-local `new`，登记为[Count of Waldstein 人物卡]"
        "(../units/persons/count-of-waldstein-casanova-dux.md)。旧 S3 备注误称原书提供全名，现已在 alignment 行追加更正：原书只给爵称及“Casanova 在 Dux 的保护人”语境；卡片未推定名字或外部身份。"
        "是否为 Prà della Valle 一座雕像出资只是 Memmo 的询问，未证明承诺；雕像候选 `cand-11561` 保持 `undecided`，两条关系候选待 S6。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    if args.dry_run:
        print(f"S3/S4 Waldstein title-person dry-run passed: {ITEM['candidate']} -> {ITEM['ku_id']}")
        print("source gives a title and unique Dux patron context only; no forename or external identity asserted")
        print("S3 rationale correction preserved in alignment; statue candidate cand-11561 remains undecided")
        print(f"direct relation candidates={len(direct)}; formal relations added=0; manifest={len(manifest):,}->{len(planned_manifest):,}")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("group, title-form evidence, endpoint status, and destination uniqueness checked; no files changed")
        return 0

    ITEM["card_path"].write_text(card_text(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > ITEM["card_rel"]),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {ITEM['card_rel']}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {ITEM['candidate']} -> {ITEM['ku_id']}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
