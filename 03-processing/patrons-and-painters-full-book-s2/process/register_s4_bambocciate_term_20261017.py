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

GROUP = "sg3-term-cand-6099"
MEMBERS = ("cand-6099",)
KU_ID = "units/terms/bambocciate-small-pictures-everyday-life"
CARD_PATH = "04-knowledge/units/terms/bambocciate-small-pictures-everyday-life.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s3-s4-term-bambocciate-small-pictures-20261017"

DIRECT_RELATIONS = (
    "st-chp5-p132-bambocciate-support-and-origin",
    "st-chp5-p134-good-poor-and-small-scale",
    "st-chp5-p134-rosa-poem-protest",
    "st-chp5-p143-carpegna-and-teodoli-associated_with_bambocciate",
    "st-chp6-p158-marucelli-bambocciate",
    "st-chp5-p132-highest-ranks-support-bambocciate",
    "st-chp5-p138-battle-genre-described-as-more-respectable-than-bambocciate",
    "st-chp5-p143-teodoli-specialized-in-bambocciate",
)

RECORD = {
    "title_zh": "日常生活题材的小幅画作",
    "name_en": "Bambocciate",
    "description_zh": (
        "哈斯克尔以意大利语复数“bambocciate”指描绘日常生活场景的小幅画作。第5章将其置于17世纪罗马绘画、观众与赞助接受史中；"
        "第6章又以该词指藏家 Lorenzo Marucelli 欣赏的 Theodor Helmbrecker 画作。此卡记录书内的图像／绘画类别用法，"
        "不把它等同于 Bamboccianti 画家群体，也不推定其为边界固定、涵盖所有日常生活题材作品的正式艺术流派。"
    ),
    "description_en": (
        "Haskell uses the Italian plural “bambocciate” for small pictures representing scenes from everyday life. Chapter 5 places the term "
        "within the reception of seventeenth-century Roman painting, audiences, and patronage; Chapter 6 uses it for pictures by Theodor "
        "Helmbrecker admired by Lorenzo Marucelli. This unit records the book's picture-category usage. It is distinct from the Bamboccianti "
        "group of painters and is not treated as a formally bounded genre covering every depiction of everyday life."
    ),
    "sources": [
        card_writer.source(
            "5", "132", "05_CHP-5_sec_iii.md", "7",
            "the support that was won by the bambocciate, those little pictures which represented scenes from everyday life",
            "哈斯克尔直接以描绘日常生活场景的小幅画作解释 bambocciate，并讨论其在17世纪罗马的接受史。",
        ),
        card_writer.source(
            "5", "134", "05_CHP-5_sec_iii.md", "21–24",
            "There is much point in Salvator Rosa’s bitter protest about the welcome given to the bambocciate",
            "第134页将 Salvator Rosa 对 bambocciate 接受情况的诗性抗议置于讨论中，并称画中人物为“good poor”。",
        ),
        card_writer.source(
            "5", "141", "05_CHP-5_sec_iii.md", "115–116",
            "the bambocciate were described in terms that often bore little resemblance to the actual pictures",
            "哈斯克尔指出针对这一类别的攻击性描述有时与实际画作并不相符；本卡保留此为作者的评论。",
        ),
        card_writer.source(
            "5", "143", "05_CHP-5_sec_iv.md", "18–20",
            "those who specialised in bambocciate, like the Conte Carpegna and the Marchese Teodoli",
            "哈斯克尔提到 Carpegna 和 Teodoli 专门收藏或关注 bambocciate；该用法指画作类别，不指画家群体。",
        ),
        card_writer.source(
            "6", "158", "06_CHP-6_sec_iv.md", "15",
            "he delighted in the bambocciate of the Flemish painter Theodor Helmbrecker",
            "哈斯克尔以 bambocciate 指 Lorenzo Marucelli 欣赏的 Helmbrecker 画作，并说明其中有乡村生活及带寓意的场景。",
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

**原书用词：** Haskell 在第5章 p.132 以“bambocciate”称描绘日常生活场景的小幅画作；后文在 p.134、p.141、p.143 继续将其作为绘画类别讨论，第6章 p.158 也用它指 Helmbrecker 的画作。此词记录作者在不同段落中的书内用法，不代表本书给出了形式化定义或固定成员范围。

**对象辨析：** “Bamboccianti”指与 Pieter van Laer 及其追随者相关的画家群体／艺术现象；“bambocciate”指画作类别。既有[Bamboccianti术语卡](bamboccianti.md)明确保留这一区别。二者词形相关但对象类型不同，不合并；本卡也不把个别画作或画家自动归入该类别。

**范围限制：** 第5章把该类别置于17世纪罗马绘画语境，并讨论其支持者、批评及受众；Haskell还提醒，对该类作品的攻击性描述有时与实际画作相去甚远。故卡片不以“日常生活题材”反向扩张为所有农民、乡村生活或风俗画，也不把作者的社会评价改写为外部分类结论。

### 本书用例

- 第5章 p.132：直接释为描绘日常生活场景的小幅画作，并讨论其早期支持及后来获得社会高层支持的过程；来源措辞“there is reason to believe”保留为作者推断。
- 第5章 pp.134、141：讨论画中“good poor”的表现，以及相关批评对画作的描述可能与实际作品不相称。
- 第5章 p.143：以 Carpegna、Teodoli 为关注或专门收藏这一类别的例子。
- 第6章 p.158：称 Marucelli 欣赏 Helmbrecker 的 bambocciate，并提到其中有乡村生活和带寓意的画面。

## 关系与证据

没有建立正式关系。8条直接 S2 关系候选仍待 S6：`st-chp5-p132-bambocciate-support-and-origin`、`st-chp5-p132-highest-ranks-support-bambocciate`、`st-chp5-p134-good-poor-and-small-scale`、`st-chp5-p134-rosa-poem-protest`、`st-chp5-p138-battle-genre-described-as-more-respectable-than-bambocciate`、`st-chp5-p143-carpegna-and-teodoli-associated_with_bambocciate`、`st-chp5-p143-teodoli-specialized-in-bambocciate`、`st-chp6-p158-marucelli-bambocciate`。本次没有新增正式关系或外部艺术史核验。
"""
    return f"---\n{fm}---\n\n{body}"


def s3_resolution(old_note: str) -> str:
    return (
        f"group={GROUP}; source_ref=chp-5:05_CHP-5_sec_iii:l5-10#L7; S3 cross-chapter adjudication 2026-10-17: "
        "retain new as a distinct term. Haskell directly describes bambocciate as little pictures representing scenes from everyday life "
        "(Chapter 5 p.132), and uses the picture-category term again in Chapters 5 and 6, including discussion of criticism, collectors, "
        "and Helmbrecker's works. The existing units/terms/bamboccianti KU represents the artist group/phenomenon; its card expressly "
        "distinguishes the related picture term. Same wording family does not establish same term identity, and no existing same-scope "
        f"bambocciate KU was found. prior_rationale={old_note}"
    )


def update_process(text: str) -> str:
    entry = f"""\n\n<a id=\"{PROCESS_ANCHOR}\"></a>

### S3→S4 term：bambocciate 小幅日常生活画作身份裁决与登记（2026-10-17）

`cand-6099`保持 `new`，作为独立术语组 `{GROUP}` 登记。第5章 p.132 直接将 bambocciate 释作描绘日常生活场景的小幅画作；第5章 pp.134、141、143 及第6章 p.158 将其用于画面表现、评价、收藏和 Helmbrecker 作品。既有 `units/terms/bamboccianti` 记录画家群体／艺术现象，其卡片明确把 bambocciate 保留为不同的画作类别；相关词形不构成同一性。未发现相同范围的既有 term KU。

S4登记为[日常生活题材小幅画作术语卡](../../../04-knowledge/units/terms/bambocciate-small-pictures-everyday-life.md)。卡片记录 Haskell 的描述及不同章节用法，不将其推广为涵盖所有日常生活题材的固定流派。8条直接 S2 关系候选继续待 S6；没有外部术语核验或新增正式关系。

S4累计登记520组/650条候选映射；待登记4,284组/4,328条；KU总数1,539。
"""
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        return text
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = replace_once(
        text,
        "S4 已登记519组、映射649条成员候选；尚待登记4,285组、4,329条映射。",
        "S4 已登记520组、映射650条成员候选；尚待登记4,284组、4,328条映射。",
        "current S4 count",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,538 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,539 KU", "manifest count")
    heading = "### S3→S4 term：bambocciate 小幅日常生活画作身份裁决与登记（2026-10-17）"
    if heading not in text:
        entry = f"""\n\n{heading}

`cand-6099`与`Bamboccianti`画家群体保持对象区分，登记至[术语卡](../units/terms/bambocciate-small-pictures-everyday-life.md)。第5章释义及第5、6章用例支持其作为小幅日常生活画作类别的书内用法；8条直接关系候选待S6。

S4当前登记520组/650条候选映射；待登记4,284组/4,328条；KU总数1,539。
"""
        text = text.rstrip() + entry
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the Bambocciate picture-category term group")
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
        print("ALREADY REGISTERED: sg3-term-cand-6099 -> " + KU_ID)
        return 0

    assert len(manifest) == 1538, f"unexpected manifest count: {len(manifest)}"
    assert not card_path.exists(), card_path
    assert CARD_PATH not in accepted_text
    candidate = candidate_by_id[MEMBERS[0]]
    alignment = alignment_by_id[MEMBERS[0]]
    assert candidate["suggested_type"] == "term"
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
        and "bambocciate" in (row["canonical_name"] + " " + row["name_en"]).casefold()
        for row in manifest
    ), "possible same-scope Bambocciate term KU already exists"
    assert any(row["ku_id"] == "units/terms/bamboccianti" for row in manifest)

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(new_rows), len(groups)) == (4978, 4804)
    assert (len(registered), sum(map(len, registered.values()))) == (519, 649)

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
    assert len(planned_manifest) == 1539
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
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (520, 650)

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
            "dry-run passed: group=sg3-term-cand-6099 candidates=1 direct_relation_candidates=8 "
            "registered_groups_after=520 mapped_candidates_after=650 manifest_after=1539"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=sg3-term-cand-6099 candidates=1 direct_relation_candidates=8 "
        "registered_groups=520 mapped_candidates=650 manifest=1539"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
