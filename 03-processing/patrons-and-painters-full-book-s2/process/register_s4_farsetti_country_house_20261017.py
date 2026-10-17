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

GROUP = "sg3-place-farsetti-country-house-s-maria-di-sala"
MEMBERS = ("cand-1007", "cand-10432")
KU_ID = "units/places/filippo-farsetti-country-house-s-maria-di-sala"
CARD_PATH = "04-knowledge/units/places/filippo-farsetti-country-house-s-maria-di-sala.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s3-s4-place-farsetti-country-house-s-maria-di-sala-20261017"

DIRECT_RELATIONS = (
    "st-chp15-p362-country-villa-design-description",
    "st-chp15-p362-country-villa-arcades-and-columns-partial",
    "st-chp15-p362-villa-located-at-s-maria-di-sala",
    "st-chp15-p362-villa-intended-for-cast-collection",
    "st-chp15-p362-villa-intended-for-painting-collection",
    "st-chp15-p363-farsetti-said-spent-million-ducats",
    "st-chp15-p363-contemporary-praised-villa",
    "st-chp15-p363-attention-to-gardens",
    "st-chp15-p362-country-villa-closer-to-austrian-pattern",
)

RECORD = {
    "title_zh": "圣玛丽亚迪萨拉的法尔塞蒂乡间别墅",
    "name_en": "Farsetti's country house at S. Maria di Sala",
    "description_zh": (
        "本卡指哈斯克尔第15章所述菲利波·法尔塞蒂在 S. Maria di Sala 家族庄园的乡间别墅。原书将它与法尔塞蒂在威尼斯的家族宫邸分开，"
        "并说明原拟在帕多瓦建造的罗马式别墅计划因与当地土地所有者发生争议而未能实施，随后转至 S. Maria di Sala 建造。"
        "中文和英文题名均为描述性工作名称，不声称是建筑正式名称。"
    ),
    "description_en": (
        "This card represents Filippo Farsetti's country house on the family estates at S. Maria di Sala, as described in Chapter 15. "
        "The book distinguishes it from Farsetti's family palace in Venice and says that an earlier plan for a Roman-type villa at Padua "
        "was not realized after a dispute with local landowners; he then turned to the S. Maria di Sala estate. Both display names are "
        "descriptive working names, not claims to an official building title."
    ),
    "sources": [
        card_writer.source(
            "15", "362", "15_CHP-15_sec_i.md", "24",
            "he turned to the family estates at S. Maria di Sala, a few miles away",
            "哈斯克尔称，原拟在帕多瓦建造别墅的计划受阻后，法尔塞蒂转往 S. Maria di Sala 的家族庄园。",
        ),
        card_writer.source(
            "15", "362", "15_CHP-15_sec_i.md", "24",
            "The villa, designed to hold his expanding collections, was wholly unlike the standard Venetian prototypes",
            "第362页将该处称为 villa，并描述其为收藏而设计，且不同于标准威尼斯别墅原型。",
        ),
        card_writer.source(
            "15", "362", "15_CHP-15_sec_i.md", "24–25",
            "The lower storey of these wings is made up of rectangular arcades",
            "同段描述别墅中央凸湾、两翼和端部亭体，并称两翼下层由矩形拱廊构成。",
        ),
        card_writer.source(
            "15", "363", "15_CHP-15_sec_i.md", "28",
            "It is now a battered shell used as a store by local peasants.",
            "哈斯克尔在该段写作时称别墅已成为破损外壳并被当地农民用作储物处；这不是对当前状态的判断。",
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
        "type": "place",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {RECORD['description_zh']} 第362页还将建筑描述为中央部分凸出、主楼两侧接低层翼部并连至小型方形亭体；两翼下层为矩形拱廊。第363页关于建筑状况的文字仅记录哈斯克尔写作时的叙述，不表示目前保存状态。[第15章 p.362](../../../02-sources/02-Markdown/15_CHP-15_sec_i.md)（L24–25）[第15章 p.363](../../../02-sources/02-Markdown/15_CHP-15_sec_i.md)（L28）

**English:** {RECORD['description_en']} Page 362 describes a projecting central bay, lower wings joined to small square pavilions, and rectangular arcades on the wings' lower storeys. The statement about the building's condition records Haskell's account at the time of writing and does not establish its present state. [Chapter 15, p. 362](../../../02-sources/02-Markdown/15_CHP-15_sec_i.md) (L24–25) [Chapter 15, p. 363](../../../02-sources/02-Markdown/15_CHP-15_sec_i.md) (L28)

### 名称与身份边界

- **索引对应：** `cand-1007`（F.csv#22）列出“country house at S. Maria di Sala”；正文候选`cand-10432`在同一段称其为“country house”及“villa”，位置和法尔塞蒂语境相合，故两项共同指向本卡。
- **与其他地点区分：** 第362页先称法尔塞蒂家族在威尼斯 Rialto 附近的宫邸，再另述其 S. Maria di Sala 家族庄园上的乡间别墅；帕多瓦的罗马式别墅是未实现的原计划，不并入本卡。
- **对象类型：** 建筑地点（place 的 building 子类）。收藏、花园、柱件、Dea Concordia 神庙及单独的建筑比较对象不并为该建筑本身；原书关于其设计、结构、用途、装饰费用及赞誉的叙述均保留来源限定。
- **名称性质：** 原书未在该段提供正式专名；卡片题名是依据地点和描述对象所作的描述性工作名称。

## 关系与证据

未建立正式关系。以下9条直接 S2 关系候选仍待 S6 按端点、关系类型、方向、语境和证据逐项审查：`st-chp15-p362-country-villa-design-description`、`st-chp15-p362-country-villa-arcades-and-columns-partial`、`st-chp15-p362-villa-located-at-s-maria-di-sala`、`st-chp15-p362-villa-intended-for-cast-collection`、`st-chp15-p362-villa-intended-for-painting-collection`、`st-chp15-p363-farsetti-said-spent-million-ducats`、`st-chp15-p363-contemporary-praised-villa`、`st-chp15-p363-attention-to-gardens`、`st-chp15-p362-country-villa-closer-to-austrian-pattern`。若其他端点仍为未决或未登记，相关边继续保持待审。
"""
    return f"---\n{fm}---\n\n{body}"


def s3_resolution(candidate_id: str, old_note: str) -> str:
    specific = {
        "cand-1007": (
            "source_ref=F.csv#22 p.362-363; S3 cross-source adjudication 2026-10-17: retain new in "
            "sg3-place-farsetti-country-house-s-maria-di-sala. The index subentry explicitly names Farsetti's country "
            "house at S. Maria di Sala; body candidate cand-10432 calls the same residence a country house/villa on the "
            "family estate. The Rialto family palace and unrealized Padua villa plan are distinct places/plans; neither is merged."
        ),
        "cand-10432": (
            "source_ref=chp-15:15_CHP-15_sec_i:l16-25#L24; S3 cross-source adjudication 2026-10-17: retain new in "
            "sg3-place-farsetti-country-house-s-maria-di-sala. The body calls the residence a villa/country house and "
            "locates it on the family estates at S. Maria di Sala; this matches the exact index subentry of cand-1007. "
            "It is distinct from Farsetti's Rialto family palace and the unbuilt Padua plan."
        ),
    }[candidate_id]
    return f"group={GROUP}; {specific}; prior_rationale={old_note}"


def update_process(text: str) -> str:
    entry = f"""\n\n<a id=\"{PROCESS_ANCHOR}\"></a>

### S3→S4 place：Farsetti 在 S. Maria di Sala 的乡间别墅身份组裁决与登记（2026-10-17）

`cand-1007`（F.csv#22，索引子目“country house at S. Maria di Sala”）与`cand-10432`（第15章 p.362 正文）维持同一 `new` 身份组 `{GROUP}`。正文将其称为 country house/villa，定位于法尔塞蒂家族在 S. Maria di Sala 的庄园；索引子目与正文对象的地点、所有者语境及建筑称谓相合。第362页另述法尔塞蒂在 Rialto 附近的家族宫邸，以及因争议未建成的帕多瓦罗马式别墅计划；两者不并入本组。登记名称为描述性工作题名，原书未给该建筑正式专名。

S4将两条候选映射至[法尔塞蒂 S. Maria di Sala 乡间别墅地点卡](../../../04-knowledge/units/places/filippo-farsetti-country-house-s-maria-di-sala.md)。卡片将第363页“battered shell”严格限定为哈斯克尔写作时的记述；未据此推定目前建筑状态，也未补外部地理或建筑身份。9条直接 S2 关系候选继续待 S6，其中收藏端点`cand-1005`、`cand-1006`仍为 untyped/undecided；本批没有新增正式关系。

S4累计登记519组/649条候选映射；待登记4,285组/4,329条；KU总数1,538。
"""
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        return text
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = replace_once(
        text,
        "S4 已登记518组、映射647条成员候选；尚待登记4,286组、4,331条映射。",
        "S4 已登记519组、映射649条成员候选；尚待登记4,285组、4,329条映射。",
        "current S4 count",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,537 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,538 KU", "manifest count")
    heading = "### S3→S4 place：Farsetti 在 S. Maria di Sala 的乡间别墅身份组裁决与登记（2026-10-17）"
    if heading not in text:
        entry = f"""\n\n{heading}

`cand-1007`（索引子目）与`cand-10432`（正文候选）依据第15章 p.362 对同一 S. Maria di Sala 乡间别墅的明确对应，共同映射至[地点卡](../units/places/filippo-farsetti-country-house-s-maria-di-sala.md)。Rialto 家族宫邸与未实现的帕多瓦计划保持区分；9条直接关系候选留待S6。

S4当前登记519组/649条候选映射；待登记4,285组/4,329条；KU总数1,538。
"""
        text = text.rstrip() + entry
    return text


def main():
    parser = argparse.ArgumentParser(description="Register Farsetti's S. Maria di Sala country-house place group")
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
        print("ALREADY REGISTERED: sg3-place-farsetti-country-house-s-maria-di-sala -> " + KU_ID)
        return 0

    assert len(manifest) == 1537, f"unexpected manifest count: {len(manifest)}"
    assert not card_path.exists(), card_path
    assert CARD_PATH not in accepted_text
    assert all(cid in candidate_by_id and cid in alignment_by_id for cid in MEMBERS)
    assert all(candidate_by_id[cid]["suggested_type"] == "place" for cid in MEMBERS)
    assert all(alignment_by_id[cid]["decision"] == "new" and not alignment_by_id[cid].get("ku_id") for cid in MEMBERS)
    assert all(get_group(alignment_by_id[cid]["resolution_note"]) == GROUP for cid in MEMBERS)
    group_rows = [
        row for row in alignments
        if not row.get("external_source") and row.get("decision") == "new"
        and get_group(row["resolution_note"]) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(MEMBERS)
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    assert not any(
        row["type"] == "place"
        and any(token in (row["canonical_name"] + " " + row["name_en"]).casefold()
                for token in ("farsetti country house", "villa at s. maria di sala", "villa of s. maria di sala"))
        for row in manifest
    ), "possible same-scope place KU already exists"

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(new_rows), len(groups)) == (4978, 4804)
    assert (len(registered), sum(map(len, registered.values()))) == (518, 647)

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
        "type": "place",
        "canonical_name": RECORD["title_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1538
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
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (519, 649)

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
            "dry-run passed: group=sg3-place-farsetti-country-house-s-maria-di-sala candidates=2 "
            "direct_relation_candidates=9 registered_groups_after=519 mapped_candidates_after=649 manifest_after=1538"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=sg3-place-farsetti-country-house-s-maria-di-sala candidates=2 "
        "direct_relation_candidates=9 registered_groups=519 mapped_candidates=649 manifest=1538"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
