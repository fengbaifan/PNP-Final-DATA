from __future__ import annotations

import argparse
import csv
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

GROUP = "sg3-term-germanpatronage"
MEMBERS = ("cand-1145", "cand-1146")
KU_ID = "units/terms/german-patronage-of-italian-art"
CARD_PATH = "04-knowledge/units/terms/german-patronage-of-italian-art.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s3-s4-german-patronage-of-italian-art-20261017"

RECORD = {
    "title_zh": "德国对意大利艺术的赞助",
    "name_en": "German patronage of Italian art",
    "description_zh": (
        "本术语记录哈斯克尔书中以“German patronage”指称的历史主题：德国诸侯国与宫廷，以及书中明确提及的德国教会领主，"
        "对意大利画家及意大利艺术品的雇用、委托或购藏。第7章着重17世纪后期对意大利多个艺术中心的影响；"
        "第10章则讨论18世纪德国宫廷、尤其对威尼斯艺术家的赞助。两处反映不同时段与地域焦点，不据此推定一个连续统一的制度或网络。"
    ),
    "description_en": (
        "This term records the historical topic Haskell indexes as “German patronage”: the employment of Italian painters and the commissioning "
        "or acquisition of Italian art by German principalities and courts, including German princely clergy explicitly discussed in the book. "
        "Chapter 7 emphasizes effects on several Italian centres in the later seventeenth century; Chapter 10 discusses German courts and, in "
        "particular, patronage of Venetian artists in the eighteenth century. These are distinct periods and regional emphases; the unit does not "
        "infer one continuous institution or network."
    ),
    "sources": [
        card_writer.source(
            "7", "194", "07_CHP-7_sec_iv.md", "25–31",
            "So extensive and influential did this German patronage then become",
            "哈斯克尔称，17世纪后期德国诸侯国对意大利画家的赞助规模和影响显著，并指出罗马、博洛尼亚、威尼斯等地受到影响。",
        ),
        card_writer.source(
            "7", "195", "07_CHP-7_sec_iv.md", "41–43",
            "uninterrupted German order books",
            "第7章以持续不断的德国委托概括其对意大利画家工作的影响；这是作者的书内表述。",
        ),
        card_writer.source(
            "10", "278", "10_CHP-10_intro.md", "28–32",
            "many German courts had been obtaining works of art from",
            "第10章称德国宫廷至少一代以来从意大利取得艺术品，并记载较强宫廷还吸引意大利艺术家前往任职。",
        ),
        card_writer.source(
            "10", "294", "10_CHP-10_intro.md", "298–303",
            "The patronage of his son Augustus III, who succeeded to the throne in 1733, was of a wholly different order",
            "哈斯克尔将 Augustus III 的赞助和收藏置于其父 Augustus the Strong 之后，并提到德累斯顿绘画馆的地位。",
        ),
        card_writer.source(
            "10", "295", "10_CHP-10_intro.md", "316–317",
            "No sovereign in Germany could rival Augustus in his patronage or collecting",
            "哈斯克尔比较 Augustus 与其他德国君主对当代威尼斯绘画的赞助或收藏；比较为作者表述，未量化。",
        ),
        card_writer.source(
            "10", "296", "10_CHP-10_intro.md", "319–325",
            "German patronage of Venetian art, and Venetian art itself, reached a climax in 1750",
            "第10章把 Tiepolo 受委托装饰 Würzburg Residenz 与作者所称德国赞助威尼斯艺术的1750年高峰相联系。",
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
        "type": "term",
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

### 术语范围与边界

**原书词形：** 索引主词形为“German patronage”；一项子目指17世纪，另一项指18世纪德国对威尼斯艺术家的赞助。卡片以“德国对意大利艺术的赞助”作为描述性双语题名，不把它当作原书中另一个固定专名。

**17世纪语境：** 第7章称，从17世纪80年代起，数十个德国诸侯国足以吸引重要意大利画家；罗马、博洛尼亚和威尼斯主要受到这一赞助来源影响，意大利画家也为德国诸侯工作，部分作品北运。第195页以持续的德国委托概括此种影响（第7章，印刷页194–195）。这些是作者的范围概括，不据此计算委托规模或推定所有个案均属同一体系。

**18世纪语境：** 第10章记载德国宫廷从意大利购画并延请画家赴维也纳、德累斯顿和慕尼黑等地；后文分别讨论 Augustus III 的收藏与对威尼斯当代艺术家的赞助、Clemens August 的委托，以及 Tiepolo 在 Würzburg 的装饰工程。Haskell 将1750年的 Würzburg 委托称作德国赞助威尼斯艺术的高峰；此处保留为作者的时期判断（第10章，印刷页278、294–296）。

**对象边界：** 本术语是对书内艺术赞助主题的记录，不是一所机构、单一赞助人、家族或某件委托作品，也不表示跨越两世纪的连续统一网络。一般性的“艺术赞助”、罗马赞助衰退、具体宫廷、个人和委托事件保持各自的对象粒度；本卡只记录德国方面赞助意大利艺术这一特定范围。书内的比较、高峰与影响判断均保留为 Haskell 的论述，不当作独立量化或外部验证结论。

### 索引用法

- `cand-1145`（G.csv#52）列“in 17th century”，对应第7章 pp.193–195 的意大利多地语境。
- `cand-1146`（G.csv#53）列“of Venetian artists in 18th century”，对应第10章对德国宫廷及威尼斯艺术家的论述；p.278 同时提供德国宫廷从意大利购画、雇用画家的较广背景。

## 关系与证据

### 关系记录

未建立正式关系。`cand-1145` 的四条直接 S2 关系候选仍待 S6：`st-chp7-p194-bologna-affected-by-patronage`、`st-chp7-p194-rome-affected-by-patronage`、`st-chp7-p194-venice-affected-by-patronage`、`st-chp7-p195-price-of-german-orders`。本次只完成术语身份登记，没有将书内判断转为正式关系。

### 身份与外部链接

本卡记录本书及其索引的术语用法；本次没有使用外部术语或身份数据库。
"""
    return f"---\n{fm}---\n\n{body}"


def s3_resolution(candidate_id: str, old_note: str) -> str:
    specific = {
        "cand-1145": (
            "source_ref=chp-7:07_CHP-7_sec_iv:l23-46#m-chp7-p194-b016; S3 cross-chapter adjudication 2026-10-17: "
            "retain new in sg3-term-germanpatronage. Chapter 7 pp.194-195 describes German principalities and princes "
            "supporting Italian painters across Rome, Bologna, Venice and other centres; Chapter 10 pp.278, 294-296 "
            "discusses German courts acquiring Italian art and patronizing Venetian artists. The index subentries mark "
            "seventeenth- and eighteenth-century uses of the same broad source topic; the card records them as distinct "
            "historical contexts and infers no continuous institution or network. Existing Art patronage and Roman "
            "patronage terms have different scope, not the same term identity."
        ),
        "cand-1146": (
            "source_ref=chp-10:10_CHP-10_intro:l22-32#m-chp10-p294-german-patronage-index; S3 cross-chapter adjudication 2026-10-17: "
            "retain new in sg3-term-germanpatronage. Chapter 10 p.278 places German courts' Italian purchases and "
            "employment of Italian painters in a broader context; pp.294-296 focus on Augustus III, other German "
            "sovereigns and princely clergy, and Venetian art. Compared with cand-1145 and Chapter 7 pp.194-195, this is "
            "the same broad source topic with a distinct eighteenth-century and Venetian-art emphasis, not a separate "
            "institution or a claim of uninterrupted continuity. Existing Art patronage and Roman patronage terms have "
            "different scope, not the same term identity."
        ),
    }[candidate_id]
    return f"group={GROUP}; {specific}; prior_rationale={old_note}"


def update_process(text: str) -> str:
    entry = f"""\n\n<a id=\"{PROCESS_ANCHOR}\"></a>

### S3→S4 term：German patronage 跨章身份组裁决与登记（2026-10-17）

`cand-1145`（G.csv#52，子目“in 17th century”）与`cand-1146`（G.csv#53，子目“of Venetian artists in 18th century”）保留为同一 `new` term 组 `{GROUP}`。第7章 pp.194–195 将17世纪后期的德国诸侯赞助与意大利多个绘画中心、受雇画家和北运作品相连；第10章 p.278 描述德国宫廷从意大利购画及延请画家，pp.294–296 则聚焦 Augustus III、其他德国君主及教会诸侯赞助威尼斯艺术。两项索引指向同一宽泛书内主题，但各自的时代与地域重心分开记录，不推断连续统一的制度或网络。现有一般术语 Art patronage 与罗马赞助主题的 term KU 范围不同，均不复用；未发现与本组同粒度的既有 KU。

S4将两条候选共同映射至[德国对意大利艺术的赞助术语卡](../../../04-knowledge/units/terms/german-patronage-of-italian-art.md)。卡片逐项限定第7章和第10章的历史语境、索引用法及作者的时期判断，没有外部术语核验。`cand-1145` 的4条直接 S2 关系候选仍待 S6：`st-chp7-p194-bologna-affected-by-patronage`、`st-chp7-p194-rome-affected-by-patronage`、`st-chp7-p194-venice-affected-by-patronage`、`st-chp7-p195-price-of-german-orders`；本次没有新增正式关系。

S4累计登记518组/647条候选映射；待登记4,286组/4,331条；KU总数1,537。
"""
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        return text
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = replace_once(
        text,
        "S4 已登记517组、映射645条成员候选；尚待登记4,287组、4,333条映射。",
        "S4 已登记518组、映射647条成员候选；尚待登记4,286组、4,331条映射。",
        "current S4 count",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,536 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,537 KU", "manifest count")
    entry = f"""\n\n### S3→S4 term：German patronage 跨章身份组裁决与登记（2026-10-17）

`cand-1145` 与 `cand-1146` 保留为同一 `new` 术语组并映射至[术语卡](../units/terms/german-patronage-of-italian-art.md)。第7章的17世纪后期意大利多地语境与第10章的18世纪德国宫廷、威尼斯艺术语境分别记录，不推断连续统一制度。四条直接关系候选留待S6；未新增正式关系。

S4当前登记518组/647条候选映射；待登记4,286组/4,331条；KU总数1,537。
"""
    if "### S3→S4 term：German patronage 跨章身份组裁决与登记（2026-10-17）" not in text:
        text = text.rstrip() + entry
    return text


def main():
    parser = argparse.ArgumentParser(description="Adjudicate and register the German patronage term group")
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

    if card_path.exists() and all(alignment_by_id[cid].get("ku_id") == KU_ID for cid in MEMBERS):
        assert any(row["ku_id"] == KU_ID for row in manifest)
        assert CARD_PATH in accepted_text
        print("ALREADY REGISTERED: sg3-term-germanpatronage -> units/terms/german-patronage-of-italian-art")
        return 0

    assert len(manifest) == 1536, f"unexpected manifest count: {len(manifest)}"
    assert not card_path.exists(), card_path
    assert CARD_PATH not in accepted_text
    assert all(cid in candidate_by_id and cid in alignment_by_id for cid in MEMBERS)
    assert all(candidate_by_id[cid]["suggested_type"] == "term" for cid in MEMBERS)
    assert all(alignment_by_id[cid]["decision"] == "new" and not alignment_by_id[cid].get("ku_id") for cid in MEMBERS)
    assert all(get_group(alignment_by_id[cid]["resolution_note"]) == GROUP for cid in MEMBERS)
    group_rows = [
        row for row in alignments
        if not row.get("external_source") and row.get("decision") == "new"
        and get_group(row["resolution_note"]) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(MEMBERS)
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    existing_terms = [
        row for row in manifest if row["type"] == "term"
        and any(token in (row["canonical_name"] + " " + row["name_en"]).casefold()
                for token in ("german patronage of italian art", "german art patronage", "deutsche kunstpatronage"))
    ]
    assert not existing_terms, f"possible same-scope term KU already exists: {existing_terms}"

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(new_rows), len(groups)) == (4978, 4804)
    assert (len(registered), sum(map(len, registered.values()))) == (517, 645)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        old_note = planned_by_id[cid]["resolution_note"]
        planned_by_id[cid]["resolution_note"] = s3_resolution(cid, old_note)
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "term",
        "canonical_name": RECORD["title_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1537
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row.get("decision") == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {
        group: rows for group, rows in planned_groups.items()
        if any(row.get("ku_id") for row in rows)
    }
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (518, 647)

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

    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    direct_relation_ids = (
        "st-chp7-p194-bologna-affected-by-patronage",
        "st-chp7-p194-rome-affected-by-patronage",
        "st-chp7-p194-venice-affected-by-patronage",
        "st-chp7-p195-price-of-german-orders",
    )
    statements = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        import json
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in direct_relation_ids:
                statements.append(statement)
    assert {row["statement_id"] for row in statements} == set(direct_relation_ids)
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)

    if args.dry_run:
        print(
            "dry-run passed: group=sg3-term-germanpatronage candidates=2 direct_relation_candidates=4 "
            "registered_groups_after=518 mapped_candidates_after=647 manifest_after=1537"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=sg3-term-germanpatronage candidates=2 direct_relation_candidates=4 "
        "registered_groups=518 mapped_candidates=647 manifest=1537"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
