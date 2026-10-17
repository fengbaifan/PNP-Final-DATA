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

GROUP = "sg3-term-cand-6148"
MEMBERS = ("cand-6148",)
KU_ID = "units/terms/cerquozzi-patrons-spanish-sphere-context"
CARD_PATH = "04-knowledge/units/terms/cerquozzi-patrons-spanish-sphere-context.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s3-s4-term-cerquozzi-patrons-spanish-sphere-20261017"

DIRECT_RELATIONS = (
    "st-chp5-p137-association-and-gradual-acceptance",
    "st-chp5-p137-families-contrast-barberini-circle",
    "st-chp5-p137-families-favored-subjects",
    "st-chp5-p137-families-stylistic-preferences",
    "st-chp5-p137-patrons-spanish-sphere",
    "st-chp5-p137-families-concentrated-on-salvator-rosa",
    "st-chp5-p137-families-concentrated-on-jan-miel",
    "st-chp5-p137-families-concentrated-on-giacomo-borgognone",
    "st-chp5-p137-families-concentrated-on-later-bamboccianti",
    "st-chp5-p137-families-ignored-classicism-venetian-colour-balance",
    "st-chp5-p137-families-ignored-baroque-exuberance",
)

RECORD = {
    "title_zh": "哈斯克尔所述塞尔奎齐赞助人的西班牙势力圈语境",
    "name_en": "Haskell's account of Cerquozzi's patrons in the Spanish sphere",
    "description_zh": (
        "本术语记录哈斯克尔第5章对塞尔奎齐重要赞助人及罗马若干赞助家族的讨论：作者称其重要赞助人中“几乎所有”都在西班牙势力范围内，"
        "并以拉帕乔利枢机、拉吉蒙席、卡米洛·卡兰迪尼伯爵等为书内例子。原文同时讨论这些家庭与 Barberini 圈在品味上的差异，"
        "但没有给出完整名单，也没有将他们描述为一个有正式组织身份的团体。本卡仅表达作者的书内分类语境，不推定统一机构、固定成员或直接政治控制。"
    ),
    "description_en": (
        "This term records Haskell's Chapter 5 discussion of Cerquozzi's important patrons and several Roman patron families. He says “nearly all” "
        "of the important patrons were within the Spanish sphere of influence and gives Cardinal Rapaccioli, Monsignor Raggi, and Count Camillo "
        "Carandini among the examples in the passage. He also contrasts the taste of most of these families with the Barberini circle. The book "
        "does not provide a complete roster or describe them as a formally organized body. This unit records the author's source-bound category; "
        "it does not infer a unified institution, fixed membership, or direct political control."
    ),
    "sources": [
        card_writer.source(
            "5", "137", "05_CHP-5_sec_iii.md", "70–71",
            "nearly all his more important patrons were within the Spanish sphere of influence.",
            "哈斯克尔以“nearly all”限定塞尔奎齐较重要赞助人与西班牙势力范围的关系；这是作者对该段 patron 群体的概括。",
        ),
        card_writer.source(
            "5", "137", "05_CHP-5_sec_iii.md", "72–73",
            "Cardinal Rapaccioli, who died in 1657, and who owned many of his pictures, was boycotted by the French in the conclave of 1655 because of his Spanish affiliations",
            "第137页以 Rapaccioli、Raggi 与 Carandini 等说明书内语境；政治立场和收藏信息均按作者叙述及限定保留。",
        ),
        card_writer.source(
            "5", "137", "05_CHP-5_sec_iii.md", "74–76",
            "most of these families showed a striking contrast in taste with the more cultivated Barberini circle.",
            "哈斯克尔比较多数相关家庭与 Barberini 圈的品味，并称其绘画偏好；这是作者的艺术史解释。",
        ),
        card_writer.source(
            "5", "137", "05_CHP-5_sec_iii.md", "78–80",
            "There is not much reason for believing that this change was the direct result, of specific pressures from his patrons",
            "哈斯克尔明确不认为塞尔奎齐题材变化可直接归因于赞助人的特定压力；卡片保留这一因果限定。",
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

**来源称谓与范围：** 第137页承接塞尔奎齐的赞助语境，称其“几乎所有”较重要赞助人均处于西班牙势力范围内；随后列出政治关联和赞助关系的例子，并以“most of these families”限定审美比较。索引式展示名为描述性工作标题，不是原书正式术语或该群体的自称。

**群体边界：** 本卡记录哈斯克尔讨论中的赞助人／家庭语境，不是人物或家族名册，也不是正式机构、党派或已证实的协同行动网络。卡片列举的姓名只是段中例子，不穷举成员；“nearly all”“most”等原文限定继续适用。

**解释边界：** 哈斯克尔把相关群体与 Barberini 圈在品味上对照，并讨论他们关注的画家及题材；这些是作者的归纳。该段明确提醒，塞尔奎齐晚年题材变化不宜归因于赞助人的直接特定压力。此处不把“Spanish sphere”改写为统一政治控制或 formal patronage system。

### 本书语境

- 第5章 p.137：称“几乎所有”塞尔奎齐较重要的赞助人处于西班牙势力范围内，并以 Rapaccioli、Raggi、Carandini 等说明书内语境。来源用“within the Spanish sphere of influence”“devoted to the Spanish cause”“Spanish affiliations”等不同表达，各按原句保留。
- 同页称多数相关家庭与 Barberini 圈在品味上有显著差异，并讨论其对风景画家、Cerquozzi 类似题材画家及后代 Bamboccianti 的关注；该比较不构成成员资格清单。
- 第5章 p.137 还指出塞尔奎齐晚年题材变化并无充分理由归因于赞助人施加的具体压力；赞助关系与艺术变化的因果判断不在本卡中扩大。

## 关系与证据

没有建立正式关系。11条直接 S2 关系候选留待 S6 逐项审查端点、关系类型、方向和语境：`st-chp5-p137-association-and-gradual-acceptance`、`st-chp5-p137-families-contrast-barberini-circle`、`st-chp5-p137-families-favored-subjects`、`st-chp5-p137-families-stylistic-preferences`、`st-chp5-p137-patrons-spanish-sphere`、`st-chp5-p137-families-concentrated-on-salvator-rosa`、`st-chp5-p137-families-concentrated-on-jan-miel`、`st-chp5-p137-families-concentrated-on-giacomo-borgognone`、`st-chp5-p137-families-concentrated-on-later-bamboccianti`、`st-chp5-p137-families-ignored-classicism-venetian-colour-balance`、`st-chp5-p137-families-ignored-baroque-exuberance`。本卡只记录书内讨论类别，不作外部政治身份核验。
"""
    return f"---\n{fm}---\n\n{body}"


def s3_resolution(old_note: str) -> str:
    return (
        f"group={GROUP}; source_ref=chp-5:05_CHP-5_sec_iii:l70-80#L71; S3 term adjudication 2026-10-17: retain new as a "
        "source-defined conceptual category, not as a formal group entity. Haskell says nearly all Cerquozzi's more important patrons "
        "were within the Spanish sphere, gives several political/family examples, and refers to 'most of these families' in the taste "
        "comparison; he supplies no complete roster or organizational identity. Existing person/family/institution KUs are different "
        "object granularities, and no exact same-scope term KU was found. Preserve 'nearly all' and 'most'; do not infer Spanish control, "
        f"a fixed membership, or direct patron pressure on style. prior_rationale={old_note}"
    )


def update_process(text: str) -> str:
    entry = f"""\n\n<a id=\"{PROCESS_ANCHOR}\"></a>

### S3→S4 term：塞尔奎齐赞助人的西班牙势力圈语境裁决与登记（2026-10-17）

`cand-6148` 保持 `new` 并登记为 `{GROUP}`。第5章 p.137 称塞尔奎齐几乎所有较重要赞助人位于西班牙势力范围，随后以 Rapaccioli、Raggi、Carandini 等为例，并称“多数”相关家庭与 Barberini 圈在品味上有显著差异。此候选是作者段落中的概念性集体类别，不是 institution、单一家族或完整人物清单；原文没有组织身份，也未列出穷尽成员。S3 保留 `nearly all`、`most` 限定，不推断西班牙政治控制、统一网络或固定成员。个体 person 和具体 family KU 为不同对象粒度；未发现同范围既有 term KU。

S4登记至[术语卡](../../../04-knowledge/units/terms/cerquozzi-patrons-spanish-sphere-context.md)。卡片记述作者的审美比较及其对“直接赞助压力”因果解释的保留；11条直接 S2 关系候选继续待 S6，不新增正式关系或外部政治身份断言。

S4累计登记521组/651条候选映射；待登记4,283组/4,327条；KU总数1,540。
"""
    if f'<a id="{PROCESS_ANCHOR}\"></a>' in text:
        return text
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = replace_once(
        text,
        "S4 已登记520组、映射650条成员候选；尚待登记4,284组、4,328条映射。",
        "S4 已登记521组、映射651条成员候选；尚待登记4,283组、4,327条映射。",
        "current S4 count",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,539 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,540 KU", "manifest count")
    heading = "### S3→S4 term：塞尔奎齐赞助人的西班牙势力圈语境裁决与登记（2026-10-17）"
    if heading not in text:
        entry = f"""\n\n{heading}

`cand-6148`以作者定义的概念类别保留为 `new` 并登记至[术语卡](../units/terms/cerquozzi-patrons-spanish-sphere-context.md)。保留“几乎所有”和“多数”的范围限定；不把相关家庭写成正式组织或穷尽成员清单。11条直接关系候选待S6。

S4当前登记521组/651条候选映射；待登记4,283组/4,327条；KU总数1,540。
"""
        text = text.rstrip() + entry
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the source-defined Cerquozzi patronage term group")
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
        print("ALREADY REGISTERED: sg3-term-cand-6148 -> " + KU_ID)
        return 0

    assert len(manifest) == 1539, f"unexpected manifest count: {len(manifest)}"
    assert not card_path.exists(), card_path
    assert CARD_PATH not in accepted_text
    assert candidate_by_id[MEMBERS[0]]["suggested_type"] == "term"
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
        row["type"] == "term"
        and any(token in (row["canonical_name"] + " " + row["name_en"]).casefold()
                for token in ("cerquozzi patrons in the spanish sphere", "roman patron families within the spanish sphere"))
        for row in manifest
    ), "possible same-scope term KU already exists"

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(new_rows), len(groups)) == (4978, 4804)
    assert (len(registered), sum(map(len, registered.values()))) == (520, 650)

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
        "type": "term",
        "canonical_name": RECORD["title_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1540
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
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (521, 651)

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
            "dry-run passed: group=sg3-term-cand-6148 candidates=1 direct_relation_candidates=11 "
            "registered_groups_after=521 mapped_candidates_after=651 manifest_after=1540"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=sg3-term-cand-6148 candidates=1 direct_relation_candidates=11 "
        "registered_groups=521 mapped_candidates=651 manifest=1540"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
