from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "new-person:finelli-giuliano-bbae0005b0"
MEMBERS = ("cand-1038",)
KU_ID = "units/persons/giuliano-finelli"
CARD_PATH = "04-knowledge/units/persons/giuliano-finelli.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s3-s4-person-giuliano-finelli-20261017"

DIRECT_RELATIONS = (
    "st-chp7-p171-i24",
    "st-chp7-p172-cont-i02",
    "st-chp7-p172-cont-i07",
    "st-chp7-p172-cont-i08",
)

RECORD = {
    "title_zh": "朱利亚诺·芬内利",
    "name_en": "Giuliano Finelli",
    "description_zh": (
        "哈斯克尔称 Giuliano Finelli 为雕塑家，并以“Neapolitan parentage”描述其家世；第7章记载他从罗马前往那不勒斯工作，"
        "以及 Count of Monterey 的副王利用职权促成其在大教堂装饰工程中获得较原计划更大的份额。第10章又将 Finelli 列入为西班牙王室收藏制作古代作品摹本及原创作品的雕塑家。"
        "这些为书内记载，未据此补充出生地、完整生平或外部身份核验。中文名为工作音译。"
    ),
    "description_en": (
        "Haskell identifies Giuliano Finelli as a sculptor and describes his parentage as Neapolitan. Chapter 7 says that he came from Rome "
        "to work in Naples and that the Viceroy, Count of Monterey, used his influence to secure Finelli a larger-than-planned share of the "
        "cathedral decoration. Chapter 10 also names Finelli among the sculptors who made copies after the antique and original works for the "
        "Spanish royal collection. These are source-local statements; no birthplace, full biography, or external identity verification is added. "
        "The Chinese display name is a working transliteration."
    ),
    "sources": [
        card_writer.source(
            "7", "171", "07_CHP-7_sec_i.md", "29",
            "the sculptor Giuliano Finelli, of Neapohtan parentage",
            "哈斯克尔在第171页称 Finelli 为雕塑家，并以 OCR 词形 Neapohtan 描述其家世；S2 扫描页校读为 Neapolitan。",
        ),
        card_writer.source(
            "7", "172", "07_CHP-7_sec_i.md", "301",
            "Cathedral he too was at once taken up by the Viceroy",
            "第172页续接前页 Finelli 句子，称副王在大教堂接纳并雇用他，随后为其争取更大的装饰份额。",
        ),
        card_writer.source(
            "10", "190", "07_CHP-7_sec_i.md", "261",
            "Giuliano Finelli, Alessandro Algardi and other less distinguished men in Rome and Naples made copies after the antique and original works for the royal collection.",
            "第190页列出 Finelli 与 Algardi 等人为王室收藏制作古代作品摹本及原创作品。",
        ),
    ],
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note: str):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label} anchor; found {count}")
    return text.replace(old, new, 1)


def make_card():
    sources = []
    for item in RECORD["sources"]:
        sources.append({
            "citation": card_writer.BOOK_CITATION,
            "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}",
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    frontmatter = {
        "title": f"{RECORD['title_zh']}（{RECORD['name_en']}）",
        "name_en": RECORD["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {RECORD['description_zh']}

**English:** {RECORD['description_en']}

### 姓名与书内身份

- **姓名：** Giuliano Finelli；全名见第7章 p.171 正文及第7章 p.190 索引。中文“朱利亚诺·芬内利”为工作音译，未另行确认通行译名。
- **职业：** 雕塑家。第7章称其从罗马来到那不勒斯工作；OCR 读作“Neapohtan parentage”，S2 页图校读为“Neapolitan parentage”。此措辞不等于出生地判断。
- **委托语境：** 第7章称副王 Count of Monterey 在大教堂接纳 Finelli，并运用影响力使他获得较原计划更大的装饰份额；该份额曾遭当地雕塑家 Cosimo Fanzago 强烈反对。原文没有在此详述最初计划或冲突结果。
- **王室收藏工作：** 第10章 p.190 将 Finelli 与 Alessandro Algardi 等并列，称他们为王室收藏制作古代作品摹本及原创作品。此处不推定具体作品、媒材清单或现藏地点。

## 关系与证据

没有建立正式关系。4条直接 S2 关系候选仍待 S6：`st-chp7-p171-i24`（由罗马来工作，目的地由跨页续句补足）、`st-chp7-p172-cont-i02`（副王在大教堂接纳 Finelli）、`st-chp7-p172-cont-i07`（副王运用影响力争取装饰份额）、`st-chp7-p172-cont-i08`（Fanzago 反对增加 Finelli 的份额）。关系端点、实际关系类型、方向及限定仍按原断言逐条审理。

本卡仅依据 Haskell 的书内记载；没有补充外部人物辞典或艺术家数据库身份记录。
"""
    return f"---\n{fm}---\n\n{body}"


def s3_resolution(old_note: str) -> str:
    return (
        f"source_ref=candidate=cand-1038;index_entry=F.csv#53;index_pages=171,172,190; group={GROUP}; "
        "S3 cross-chapter identity review 2026-10-17: retain new as a source-local person. Chapter 7 p.171 gives the full name Giuliano Finelli "
        "and sculptor role; the p.172 continuation uses anaphoric references and names Finelli again in the cathedral-decoration account; "
        "the Chapter 7 p.190 narrative and F.csv index also give Giuliano Finelli. The normalized full-name anchors and linked context support "
        "one person, with no conflicting same-name identity in the person manifest. The Neapolitan-parentage reading follows the existing S2 "
        "scan correction of OCR 'Neapohtan'; it is not birthplace evidence. No external identity source was used. prior_rationale=" + old_note
    )


def update_process(text: str) -> str:
    entry = f"""\n\n<a id=\"{PROCESS_ANCHOR}\"></a>

### S3→S4 person：Giuliano Finelli 跨章身份组裁决与登记（2026-10-17）

`cand-1038`（F.csv#53，索引页171、172、190）维持 `new` 人物组 `{GROUP}`。第7章 p.171 给出全名 Giuliano Finelli 与 sculptor 身份；同一段跨至 p.172，代词和后续 Finelli 全名均处于副王在大教堂雇用雕塑家的叙述；第7章 p.190 再次列出 Giuliano Finelli，并称其参与为王室收藏制作摹本及原创作品。索引全名、正文姓名与跨页指代相合，person manifest 未发现同名既有 KU。OCR 的“Neapohtan”依 S2 页图校读为“Neapolitan”；这里只记家世用语，不推断出生地。未使用外部身份来源。

S4登记至[Giuliano Finelli 人物卡](../../../04-knowledge/units/persons/giuliano-finelli.md)，卡片仅记录书内职业、赞助语境及王室收藏工作。4条直接 S2 关系候选仍待 S6；没有新增正式关系或外部生平断言。

S4累计登记522组/652条候选映射；待登记4,282组/4,326条；KU总数1,541。
"""
    if f'<a id="{PROCESS_ANCHOR}\"></a>' in text:
        return text
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = replace_once(
        text,
        "S4 已登记521组、映射651条成员候选；尚待登记4,283组、4,327条映射。",
        "S4 已登记522组、映射652条成员候选；尚待登记4,282组、4,326条映射。",
        "current S4 count",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,540 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,541 KU", "manifest count")
    heading = "### S3→S4 person：Giuliano Finelli 跨章身份组裁决与登记（2026-10-17）"
    if heading not in text:
        entry = f"""\n\n{heading}

`cand-1038`依据索引全名、p.171正文及p.172跨页续句、第190页正文中的全名与相合语境，登记为[人物卡](../units/persons/giuliano-finelli.md)。4条直接关系候选待S6；不补充外部生平或出生地。

S4当前登记522组/652条候选映射；待登记4,282组/4,326条；KU总数1,541。
"""
        text = text.rstrip() + entry
    return text


def main():
    parser = argparse.ArgumentParser(description="Register Giuliano Finelli's source-local person group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    card_path = ROOT / CARD_PATH
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    if card_path.exists() and alignment_by_id[MEMBERS[0]].get("ku_id") == KU_ID:
        assert any(row["ku_id"] == KU_ID for row in manifest)
        assert CARD_PATH in accepted_text
        print("ALREADY REGISTERED: new-person:finelli-giuliano-bbae0005b0 -> " + KU_ID)
        return 0

    assert len(manifest) == 1540, f"unexpected manifest count: {len(manifest)}"
    assert not card_path.exists(), card_path
    assert CARD_PATH not in accepted_text
    assert candidate_by_id[MEMBERS[0]]["suggested_type"] == "person"
    alignment = alignment_by_id[MEMBERS[0]]
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    group_rows = [
        row for row in alignments
        if not row.get("external_source") and row.get("decision") == "new"
        and get_group(row["resolution_note"]) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == list(MEMBERS)
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    assert not any(
        row["type"] == "person"
        and "giuliano finelli" in (row["canonical_name"] + " " + row["name_en"]).casefold()
        for row in manifest
    ), "possible same-person KU already exists"

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(new_rows), len(groups)) == (4978, 4804)
    assert (len(registered), sum(map(len, registered.values()))) == (521, 651)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    old_note = planned_by_id[MEMBERS[0]]["resolution_note"]
    planned_by_id[MEMBERS[0]]["resolution_note"] = s3_resolution(old_note)
    planned_by_id[MEMBERS[0]]["ku_id"] = KU_ID
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": RECORD["title_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1541
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row["decision"] == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {
        group: rows for group, rows in planned_groups.items()
        if any(row.get("ku_id") for row in rows)
    }
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (522, 652)

    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])
    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in DIRECT_RELATIONS:
                statements[statement["statement_id"]] = statement
    assert set(statements) == set(DIRECT_RELATIONS)
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements.values())

    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    card_text = make_card()

    if args.dry_run:
        print(
            "dry-run passed: group=new-person:finelli-giuliano-bbae0005b0 candidates=1 direct_relation_candidates=4 "
            "registered_groups_after=522 mapped_candidates_after=652 manifest_after=1541"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=new-person:finelli-giuliano-bbae0005b0 candidates=1 direct_relation_candidates=4 "
        "registered_groups=522 mapped_candidates=652 manifest=1541"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
