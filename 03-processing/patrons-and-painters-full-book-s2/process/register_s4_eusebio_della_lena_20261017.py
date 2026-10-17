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
    "candidate": "cand-1386",
    "group": "new-person:della-eusebio-lena-d7eabb742e",
    "ku_id": "units/persons/eusebio-della-lena",
    "card_rel": "04-knowledge/units/persons/eusebio-della-lena.md",
    "card_path": ROOT / "04-knowledge" / "units" / "persons" / "eusebio-della-lena.md",
    "type": "person",
    "name_zh": "尤西比奥·德拉莱纳",
    "name_en": "Eusebio della Lena",
}
STATEMENT = "st-chp16-p375-eusebio-friend-of-casanova"


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
            "location": "第16章；印刷页375；OCR L30–32",
            "sentence_summary": "Haskell 介绍 Giacomo della Lena 及其兄弟时称 Eusebio 是 Casanova 的朋友；本句仅给出名字 Eusebio。",
            "original_quotes": [{
                "source_span": "lines 30–32",
                "text": "The Abate Giacomo della Lena, for instance, was also on the fringes of scholarship. He was a close friend of the Abate G. A. Moschini, an antiquarian who saved many Venetian records from destruction, and he himself wrote an account of the ‘Spoliation of Pictures from Venice’.5 This deals with the activities of various collectors who had removed pictures from the city, ranging from Cardinal Leopold de’\nMedici to his own contemporaries. As a nineteenth-century historian drily commented, he was well qualified to write such an account, for he himself was deeply involved in picture dealing—mainly with the Germans. Della Lena had been born in Lucca in 1732, but he spent most of his life in Venice, where he acted as Spanish vice-consul and where he died in 1807. He probably owed the job to his brother Innocenzo, who was the\nSpanish Ambassador’s doctor, while another brother, Eusebio, was a friend of Casanova.",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "source_span": "lines 30–32; print p. 375",
            },
        },
        {
            "citation": BOOK,
            "location": "书后索引；印刷页458；OCR L1747",
            "sentence_summary": "索引列出 Eusebio della Lena 并给出 p.375；索引用于定位，未据此补写传记。",
            "original_quotes": [{
                "source_span": "line 1747",
                "text": "Lena, Eusebio della, 375",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/22_CHP-22Index.md",
                "source_span": "line 1747; print p. 458 (page marker at line 1705)",
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
    p16 = "[第16章 p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L30–32）"
    index = "[书末索引 p.458](../../../02-sources/02-Markdown/22_CHP-22Index.md)（L1747）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应书末索引形式 “Eusebio della Lena”（L.csv#43，索引页458，定位第375页）。第16章正文在介绍 Giacomo della Lena 的兄弟时只称 “Eusebio”，并称他是 Casanova 的朋友；姓氏形式取自同页索引。除这一亲属与友谊语境外，本卡不补充生卒、职业或其他生平信息。{index}；{p16}

**English:** This card represents the index form “Eusebio della Lena” (L.csv#43; index p. 458, locator p. 375). In Chapter 16, Haskell names him only as “Eusebio” while introducing the brothers of Giacomo della Lena, and says he was a friend of Casanova; the surname form is taken from the index entry. The card adds no dates, occupation, or biography beyond this kinship and friendship context. {index}; {p16}

### 名称与身份边界

- 索引形式：Lena, Eusebio della；索引页458，指向第16章 p.375。正文称 “Eusebio”；索引用于定位姓名形式，不单独代替正文证据。
- 书内关系语境将其称为 Giacomo della Lena 的“another brother”；本卡据此保留 della Lena 姓氏形式，但不扩写兄弟谱系或其他成员关系。
- 中文显示名为工作音译；没有外部身份核验或生平补足。

### 关系与证据

S2 候选 `st-chp16-p375-eusebio-friend-of-casanova` 将 Eusebio 与[Jacques Casanova de Seingalt](jacques-casanova-de-seingalt.md)相连。该友谊关系留待 S6 核查；本卡未新增正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Eusebio della Lena direct person endpoint in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == ITEM["candidate"])
    alignment = next(row for row in alignments if row.get("candidate_id") == ITEM["candidate"] and not row.get("external_source"))
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert candidate["canonical_name"] == "Lena, Eusebio della"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == ITEM["group"]
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
    direct = [row for row in statements if ITEM["candidate"] in (row.get("subject_candidate_id"), row.get("object_candidate_id"))]
    assert len(direct) == 1 and direct[0]["statement_id"] == STATEMENT
    assert direct[0].get("qualifiers", {}).get("relation_candidate") is True

    chapter = (ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md").read_text(encoding="utf-8-sig")
    index = (ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md").read_text(encoding="utf-8-sig")
    assert "while another brother, Eusebio, was a friend of Casanova." in chapter
    assert "Lena, Eusebio della, 375" in index

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
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4：Eusebio della Lena 人物端点登记（2026-10-17）\n\n"
        f"人物组 `{ITEM['group']}`（`{ITEM['candidate']}`）映射至[尤西比奥·德拉莱纳人物卡]"
        "(../../../04-knowledge/units/persons/eusebio-della-lena.md)。第16章正文只称其为 Eusebio，并称其为 Giacomo della Lena 的另一位兄弟；"
        "书末索引以 Eusebio della Lena 汇集该页。卡片保留这一书内姓名与亲属语境，不作外部身份扩展。"
        f"其与 Casanova 的1条关系候选留待 S6；本轮未修改 `relations.csv`。S4 累计登记"
        f"{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4：Eusebio della Lena 人物端点登记（2026-10-17）\n\n"
        f"`{ITEM['candidate']}` 登记为[Eusebio della Lena 人物卡](../units/persons/eusebio-della-lena.md)。"
        "姓名形式依据书末索引，正文仅称 Eusebio，并以兄弟关系提供语境。其与 Casanova 的关系候选待 S6；未新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    if args.dry_run:
        print(f"S4 Eusebio della Lena registration dry-run passed: {ITEM['candidate']} -> {ITEM['ku_id']}")
        print("identity source: index form plus Chapter 16 sibling context; direct relation endpoint: Casanova KU mapped")
        print(f"direct statements={len(direct)}; formal relations added=0; manifest={len(manifest):,}->{len(planned_manifest):,}")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("unique group and destination, index/source evidence, and endpoint mapping checked; no files changed")
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
