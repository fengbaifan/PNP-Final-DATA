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
    "candidate": "cand-0591",
    "group": "new-person:casanova-de-jacques-seingalt-f2334ab49d",
    "ku_id": "units/persons/jacques-casanova-de-seingalt",
    "card_rel": "04-knowledge/units/persons/jacques-casanova-de-seingalt.md",
    "card_path": ROOT / "04-knowledge" / "units" / "persons" / "jacques-casanova-de-seingalt.md",
    "type": "person",
    "name_zh": "雅克·卡萨诺瓦·德·塞恩加尔特",
    "name_en": "Jacques Casanova de Seingalt",
}
STATEMENTS = {
    "st-chp9-p274-casanova-corner-reputation",
    "st-chp15-p364-memmo-close-friend-casanova",
    "st-chp15-p367-letter-to-casanova-about-waldstein",
    "st-chp16-p375-eusebio-friend-of-casanova",
    "st-chp15-p367-casanova-patron-waldstein",
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


def make_card() -> str:
    source_rows = [
        {
            "location": "第9章；印刷页274；OCR L74",
            "summary": "Haskell 称 Flaminio Corner 严谨到 Casanova 本人也承认其名誉无瑕。",
            "file": "09_CHP-9_sec_ii.md",
            "span": "line 74; print p. 274",
            "quote": "So rigid was he, so unbending even with his friends, that Casanova himself had to admit that ‘sa reputation était sans tache’.4",
        },
        {
            "location": "第15章；印刷页364；OCR L4",
            "summary": "Haskell 以 Casanova 为密友说明 Andrea Memmo 与他的交往关系。",
            "file": "15_CHP-15_sec_ii.md",
            "span": "line 4; print p. 364",
            "quote": "he was not the close friend of Casanova for nothing.",
        },
        {
            "location": "第15章；印刷页367；OCR L33–34",
            "summary": "Haskell 称 Memmo 给老友 Casanova 写信，并询问其在 Dux 的保护人 Count of Waldstein 是否愿意出资。",
            "file": "15_CHP-15_sec_ii.md",
            "span": "lines 33–34; print p. 367",
            "quote": "Memmo wrote to his old friend Casanova and asked whether his patron at Dux, the Count of\nWaldstein, might not be prepared to pay for one",
        },
        {
            "location": "第16章；印刷页375；OCR L32",
            "summary": "Haskell 称 Giacomo della Lena 的兄弟 Eusebio 是 Casanova 的朋友。",
            "file": "16_CHP-16_intro.md",
            "span": "line 32; print p. 375",
            "quote": "while another brother, Eusebio, was a friend of Casanova.",
        },
    ]
    index_source = {
        "citation": BOOK,
        "location": "书后索引；印刷页449；OCR L768（页标见 L682）",
        "sentence_summary": (
            "书末索引 OCR 行列出页码274、364、367、375，但漏识 Casanova 首字母 C；"
            "实体候选索引记录 C.csv#115 保留规范定位形式 Casanova de Seingalt, Jacques。此处仅作为定位依据。"
        ),
        "original_quotes": [{
            "source_span": "line 768",
            "text": "asanova de Seingalt, Jacques, 274, 364, 367, 375",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/22_CHP-22Index.md",
            "source_span": "line 768; print p. 449 (page marker at line 682)",
        },
    }
    sources = [index_source] + [{
        "citation": BOOK,
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [{"source_span": item["span"].split(";", 1)[0], "text": item["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{item['file']}",
            "source_span": item["span"],
        },
    } for item in source_rows]
    fm = yaml.safe_dump({
        "title": f"{ITEM['name_zh']}（{ITEM['name_en']}）",
        "name_en": ITEM["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-16",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }, allow_unicode=True, sort_keys=False, width=1000)
    p9 = "[第9章 p.274](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L74）"
    p15a = "[第15章 p.364](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L4）"
    p15b = "[第15章 p.367](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L33–34）"
    p16 = "[第16章 p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L32）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应书末索引条目 “Casanova de Seingalt, Jacques”（C.csv#115），索引页码为274、364、367、375；索引 OCR 第449页 L768 漏识首字母 C，完整形式按规范化索引记录保留，索引只作定位依据。正文使用简称 Casanova。Haskell 在第9章提到 Casanova 与 Flaminio Corner 的名誉评价；第15章称 Andrea Memmo 是 Casanova 的密友，并记载 Memmo 给 Casanova 写信；第16章称 Eusebio della Lena 是 Casanova 的朋友。本卡不补充书外生平。[书末索引](../../../02-sources/02-Markdown/22_CHP-22Index.md)（p.449，L768）；{p9}；{p15a}；{p15b}；{p16}

**English:** This card represents the index entry “Casanova de Seingalt, Jacques” (C.csv#115), indexed at pp. 274, 364, 367, and 375; the index OCR at p. 449, line 768, omits the initial C, which is retained in the normalized index record. The index serves as a locator. The body text uses the short form Casanova. Chapter 9 refers to Casanova in connection with Flaminio Corner’s reputation. Chapter 15 describes Andrea Memmo as Casanova’s close friend and records that Memmo wrote to him. Chapter 16 calls Eusebio della Lena a friend of Casanova. This card adds no biography from outside the book. [Book index](../../../02-sources/02-Markdown/22_CHP-22Index.md) (p. 449, L768); {p9}; {p15a}; {p15b}; {p16}

### 名称与身份边界

- 索引形式：Casanova de Seingalt, Jacques；索引定位 274、364、367、375。书末索引 OCR 第449页 L768 漏识首字母 C，候选记录 C.csv#115 保留完整规范定位形式；正文为简称 “Casanova”。索引用于汇集定位，不单独替代正文证据。
- 本卡以同一书内索引项与四处对应正文简称登记 source-local 人物身份；未使用外部身份数据库，也未把索引姓名形式扩展为完整传记。
- Dux 的保护人 Count of Waldstein 和 Eusebio della Lena 分别保持独立人物候选；本卡不将其身份并入 Casanova。

### 书内语境

第9章 p.274 将 Casanova 放在 Corner 对朋友也严谨的叙述中；第15章 p.364、p.367 将他放在 Memmo 的友谊和通信语境中，并提到 Count of Waldstein；第16章 p.375 以 Eusebio 为 Casanova 的朋友。上述均是 Haskell 的书内叙述，不独立证明信件原件、私人关系的持续时间或 Count of Waldstein 的完整身份。

## 关系与证据

五条关系候选均留待 S6 核查；本卡不新增正式关系：

- `st-chp9-p274-casanova-corner-reputation`：Flaminio Corner（既有 KU）。
- `st-chp15-p364-memmo-close-friend-casanova`、`st-chp15-p367-letter-to-casanova-about-waldstein`：Andrea Memmo（既有 KU）。
- `st-chp16-p375-eusebio-friend-of-casanova`：Eusebio della Lena（S3 new，待 S4）。
- `st-chp15-p367-casanova-patron-waldstein`：Count of Waldstein（S3 new，待 S4；书内未给出名）。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Casanova person group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    candidate = candidate_by_id[ITEM["candidate"]]
    alignment = decision_by_id[ITEM["candidate"]]
    assert candidate["canonical_name"] == "Casanova de Seingalt, Jacques"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == ITEM["group"]
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
        and sync.get_group(row.get("resolution_note", "")) == ITEM["group"]
    ]
    assert [row["candidate_id"] for row in group_rows] == [ITEM["candidate"]]
    assert not ITEM["card_path"].exists()
    assert ITEM["card_rel"] not in accepted
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
    assert direct == STATEMENTS, direct ^ STATEMENTS
    assert all(
        row.get("qualifiers", {}).get("relation_candidate") is True
        for row in statements if row["statement_id"] in STATEMENTS
    )

    quote_sources = [
        ("09_CHP-9_sec_ii.md", "So rigid was he, so unbending even with his friends, that Casanova himself had to admit that ‘sa reputation était sans tache’.4"),
        ("15_CHP-15_sec_ii.md", "he was not the close friend of Casanova for nothing."),
        ("15_CHP-15_sec_ii.md", "Memmo wrote to his old friend Casanova and asked"),
        ("16_CHP-16_intro.md", "while another brother, Eusebio, was a friend of Casanova."),
    ]
    for filename, quote in quote_sources:
        text = (ROOT / "02-sources" / "02-Markdown" / filename).read_text(encoding="utf-8-sig")
        assert quote in text, (filename, quote)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id[ITEM["candidate"]]["ku_id"] = ITEM["ku_id"]
    planned_by_id[ITEM["candidate"]]["resolution_note"] += f" S4 registration: mapped {ITEM['group']} to {ITEM['ku_id']}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": ITEM["ku_id"], "type": ITEM["type"], "canonical_name": ITEM["name_zh"],
        "name_en": ITEM["name_en"], "source_task": TASK, "card_path": ITEM["card_rel"],
    })
    stats = sync.summarize_by_type(candidate_rows, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4：Jacques Casanova de Seingalt 跨章人物组登记（2026-10-16）\n\n"
        f"人物组 `{ITEM['group']}`（`{ITEM['candidate']}`）映射至[雅克·卡萨诺瓦·德·塞恩加尔特人物卡]"
        "(../../../04-knowledge/units/persons/jacques-casanova-de-seingalt.md)。本书索引给出全名形式和四个页码；正文跨第9、15、16章以 Casanova 指称。"
        "Corner 与 Memmo 端点已映射；Eusebio della Lena 与 Count of Waldstein 各自仍为 S3 new、待 S4。"
        "5条关系候选全部留待 S6，未改 `relations.csv`；Count of Waldstein 的书内称谓不扩展为未经证实的名字或生平。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4：Casanova de Seingalt 跨章人物组登记（2026-10-16）\n\n"
        f"候选 `{ITEM['candidate']}` 登记为[Jacques Casanova de Seingalt 人物卡](../units/persons/jacques-casanova-de-seingalt.md)。"
        "索引全名对应 p.274、364、367、375；正文使用 Casanova。五条关系候选留待 S6；Corner 与 Memmo 已有 KU，Eusebio 与 Count of Waldstein 仍待 S4。"
        "本轮不新增正式边或扩写 Count of Waldstein 的身份。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    if args.dry_run:
        print(f"S4 Casanova registration dry-run passed: {ITEM['candidate']} -> {ITEM['ku_id']}")
        print(f"direct statements={len(direct)}; all are relation candidates; formal relations added=0")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("S3 group, existing KU uniqueness, direct statements, and source quotations checked; no files changed")
        return 0

    ITEM["card_path"].write_text(make_card(), encoding="utf-8-sig", newline="\n")
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
