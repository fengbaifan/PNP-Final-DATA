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
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

ITEMS = {
    "cand-1232": {
        "group": "new-person:francesco-giovanni-grimaldi-fae8a41265",
        "ku_id": "units/persons/giovanni-francesco-grimaldi",
        "card_rel": "04-knowledge/units/persons/giovanni-francesco-grimaldi.md",
        "type": "person",
        "name_zh": "乔瓦尼·弗朗切斯科·格里马尔迪（Giovanni Francesco Grimaldi）",
        "name_en": "Giovanni Francesco Grimaldi",
        "sources": [
            {
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "location": "第2章；印刷页57；OCR L178–179",
                "span": "lines 178–179; print p. 57",
                "summary": "Haskell 将 Giovanni Francesco Grimaldi 列为 Giulio Rospigliosi 曾给予资助或赞助的画家之一。",
                "quotes": [
                    ("lines 178–179", "Many other artists received patronage if not always advice at different stages in his life—Camassei and Lodovico Gimignani, Giovanni Francesco Grimaldi and Mattia Preti; Carlo Maratta"),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "location": "第6章；印刷页155；OCR L107",
                "span": "line 107; print p. 155",
                "summary": "Haskell 称 Gianfrancesco Grimaldi 与其他画家受雇为 Lorenzo Onofrio Colonna 的宫殿绘制风景画；索引将第155页纳入 Giovanni Francesco Grimaldi 条目。",
                "quotes": [
                    ("line 107", "Gianfrancesco Grimaldi and many other artists were engaged to paint landscapes in his palace"),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "location": "第7章；印刷页181–183；OCR L147、L155–166",
                "span": "lines 147, 155–166; print pp. 181–183",
                "summary": "Haskell 称 Giovanni Francesco Grimaldi 于1648年到巴黎完成 Cardinal Mazarin 宫殿画廊的装饰，并记其在 Fronde 冲突期间藏身于耶稣会神学院后返乡。",
                "quotes": [
                    ("lines 155–156", "Then in 1648, soon after the departure of Romanelli, the Bolognese painter Giovanni Francesco Grimaldi came to complete the decoration of the Cardinal’s gallery, by painting landscapes in theniches and embrasures of the windows."),
                    ("lines 164–166", "Giovanni Francesco Grimaldi had to hide in a Jesuit seminary before he too managed to get back home."),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "location": "第7章；印刷页191；OCR L273",
                "span": "line 273; print p. 191",
                "summary": "Haskell 再次以全名提及 Grimaldi，并称其为 landscape artist；同段另称 Del Carpio 会访问若干画家的画室。",
                "quotes": [
                    ("line 273", "and Giovanni Francesco Grimaldi, the landscape artist"),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/22_CHP-22Index.md",
                "location": "书后索引；索引条目 G.csv#142",
                "span": "index entry Grimaldi, Giovanni Francesco",
                "summary": "索引以完整姓名汇集第57、155、182–183及191页；转录尾部页码有OCR噪声，正文第191页仍有全名锚点。",
                "quotes": [("index entry", "Grimaldi, Giovanni Francesco, 57,155,182-3, lyi")],
            },
        ],
        "body": """### 描述

**中文：** 本卡对应书后索引“Grimaldi, Giovanni Francesco”（G.csv#142）以及第2、6、7章的跨章提及。正文以 “Giovanni Francesco Grimaldi” 指称 Rospigliosi 资助的画家、1648年到巴黎工作的博洛尼亚画家和风景画家；第6章使用变体 “Gianfrancesco Grimaldi”。索引把第155页纳入同一全名条目，页182–183、191的正文也再次给出全名，因此在书内归为同一 source-local 人物组。未作外部身份或生平补充。[第2章 p.57](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L178–179）；[第6章 p.155](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L107）；[第7章 pp.181–183](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L147、155–166）；[第7章 p.191](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L273）；[书后索引](../../../02-sources/02-Markdown/22_CHP-22Index.md)（L1553）

**English:** This card represents the index entry “Grimaldi, Giovanni Francesco” (G.csv#142) and references across Chapters 2, 6, and 7. The prose names Giovanni Francesco Grimaldi as a painter patronized by Rospigliosi, a Bolognese painter who came to Paris in 1648, and a landscape artist; Chapter 6 uses the form “Gianfrancesco Grimaldi.” The index places p.155 under the full-name entry, while pp.182–183 and 191 again give the full name. These book-local references support one source-local person group. No external identity or biography is added. [Chapter 2, p.57](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md) (L178–179); [Chapter 6, p.155](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md) (L107); [Chapter 7, pp.181–183](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md) (L147, 155–166); [Chapter 7, p.191](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md) (L273); [Index](../../../02-sources/02-Markdown/22_CHP-22Index.md) (L1553)

### 名称与身份边界

- 对应 S3 候选 `cand-1232`（G.csv#142），保持身份组 `new-person:francesco-giovanni-grimaldi-fae8a41265`；本书索引将其页码提及归在完整姓名下。
- 第6章的 “Gianfrancesco” 由同一索引条目与第155页上下文支持，不据姓氏单独合并。索引最后的页码在Markdown中转录为 “lyi”；候选记录据正文全名记为191，来源差异保留。
- 不与同章的 Giovanni Francesco Romanelli 合并；二者姓氏、索引条目和作品语境均不同。
- p.191 关于 Del Carpio 访问画家工作室的关系候选，其 S2 端点为未定位的工作室集合 `cand-6959`，不是 Grimaldi 人物；保持原端点和待证状态。

### 关系与证据

4条直接 `relation_candidate` 留待 S6：

- `st-chp2-seciv-l171-179-rospigliosi-patronized-grimaldi`
- `st-chp6-p155-grimaldi-landscape-decoration`
- `st-chp7-p182-i12`
- `st-chp7-p183-i18`

`st-chp7-p191-i15`（“landscape artist”）是人物属性陈述，维持非关系分类；未新增正式关系。
""",
    },
    "cand-6781": {
        "group": "sg3-place-cand-6781",
        "ku_id": "units/places/mazarin-upper-gallery",
        "card_rel": "04-knowledge/units/places/mazarin-upper-gallery.md",
        "type": "place",
        "name_zh": "马扎然宫新建上层画廊（Mazarin’s Newly Built Upper Gallery）",
        "name_en": "Mazarin’s Newly Built Upper Gallery",
        "sources": [
            {
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "location": "第7章；印刷页181–182；OCR L147、L151–156",
                "span": "lines 147, 151–156; print pp. 181–182",
                "summary": "Haskell 称 Romanelli 于1646年相关叙述中已在 Mazarin 宫新建上层画廊工作；后文说明长筒形狭窄画廊不适于统一构图，并称 Romanelli 将绘画区域分隔为多个装饰框格。",
                "quotes": [
                    ("lines 146–147", "and by June Romanelli was already at work painting the newly built upper gallery of Mazarin’s palace (Plate 26a)."),
                    ("lines 151–153", "and in any case the long tunnel vault of the narrow gallery was scarcely adapted to a great unified fresco as in the Palazzo Barberini. In the event, Romanelli divided the area into a number of oval, circular, rectangular and square compartments separated from each other by frames of gilt stucco."),
                    ("lines 155–156", "Then in 1648, soon after the departure of Romanelli, the Bolognese painter Giovanni Francesco Grimaldi came to complete the decoration of the Cardinal’s gallery, by painting landscapes in theniches and embrasures of the windows."),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/00_05_List_of_Plates.md",
                "location": "图版目录；Plate 26b；Markdown L79",
                "span": "line 79; Plate 26b caption",
                "summary": "图版目录称《Romulus and Remus》为 Bibliothèque Nationale（formerly Palais Mazarin）画廊天花板的局部，为画廊与既有 Palais Mazarin 建筑定位提供书内证据。",
                "quotes": [
                    ("line 79", "26 a Nanteuil: Cardinal Mazarin in his Gallery b Romanelli: Romulus and Remus. Detail from ceiling of gallery in Bibliothèque Nationale (formerly Palais Mazarin)"),
                ],
            },
        ],
        "body": """### 描述

**中文：** 本卡登记 Cardinal Mazarin 宫殿内被 Haskell 称作 “newly built upper gallery” 的具体室内空间。第7章称 Romanelli 曾在其中工作、以多个装饰框格组织绘画区域，1648年 Giovanni Francesco Grimaldi 又完成该画廊的后续装饰。图版目录将《Romulus and Remus》标作 Bibliothèque Nationale（formerly Palais Mazarin）画廊天花板的局部。这里记录画廊空间，不与整座 [Palais Mazarin](palais-mazarin.md) 宫殿或既有顶画作品合并；原书未给出画廊专名。[第7章 pp.181–182](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L147、151–156）；[图版目录 Plate 26b](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)（L79）

**English:** This card represents the specific interior space that Haskell calls the “newly built upper gallery” of Cardinal Mazarin’s palace. Chapter 7 describes Romanelli working there and dividing its painted area into framed compartments; in 1648 Giovanni Francesco Grimaldi completed further decoration of the gallery. The list of plates identifies *Romulus and Remus* as a detail from the ceiling of a gallery in the Bibliothèque Nationale (formerly Palais Mazarin). This unit represents the gallery space, separate from the [Palais Mazarin](palais-mazarin.md) building and the existing ceiling-painting KU. The book gives no proper name for the gallery. [Chapter 7, pp.181–182](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md) (L147, 151–156); [List of Plates, Plate 26b](../../../02-sources/02-Markdown/00_05_List_of_Plates.md) (L79)

### 地点身份与边界

- 对应 S3 place 候选 `cand-6781`，保持 `sg3-place-cand-6781`；本卡仅指 Mazarin 宫内的上层画廊空间，不指整座 Palais Mazarin。
- 图版目录将天花板图像定位于 Bibliothèque Nationale（formerly Palais Mazarin）；整座建筑候选 `cand-3946` 已复用 `units/places/palais-mazarin`。
- 顶画《Romulus and Remus》候选 `cand-4090` 已复用 `units/works/romanelli-romulus-and-remus`。本卡不把画廊与其中作品合并，也不自行补写建筑现址或精确房间方位。

### 关系与证据

6条直接 S2 `relation_candidate` 留待 S6：

- `st-chp7-p181-i26`（Romanelli 在画廊作画）
- `st-chp7-p182-i04`（画廊结构及统一壁画构图的限制）
- `st-chp7-p182-i05`（Romanelli 分隔画面区域）
- `st-chp7-p182-i12`（Grimaldi 完成画廊装饰）
- `st-chp7-plate26b-detail-context`（顶画图版定位）
- `st-chp7-plate26b-gallery-location`（与 Palais Mazarin 的空间定位）

相关人物、整座宫殿和作品已各自映射或明确保留于其候选行；本卡未新增正式关系。
""",
    },
}

EXPECTED_STATEMENTS = {
    "cand-1232": {
        "st-chp2-seciv-l171-179-rospigliosi-patronized-grimaldi": True,
        "st-chp6-p155-grimaldi-landscape-decoration": True,
        "st-chp7-p182-i12": True,
        "st-chp7-p183-i18": True,
        "st-chp7-p191-i15": False,
    },
    "cand-6781": {
        "st-chp7-p181-i26": True,
        "st-chp7-p182-i04": True,
        "st-chp7-p182-i05": True,
        "st-chp7-p182-i12": True,
        "st-chp7-plate26b-detail-context": True,
        "st-chp7-plate26b-gallery-location": True,
    },
}


def make_card(item: dict) -> str:
    sources = []
    for source in item["sources"]:
        sources.append({
            "citation": BOOK,
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in source["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source["source_file"],
                "source_span": source["span"],
            },
        })
    frontmatter = {
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": item["type"],
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    return f"---\n{yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)}---\n\n## 内容\n\n{item['body']}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Giovanni Francesco Grimaldi and Mazarin's upper gallery in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert candidate_by_id["cand-1232"]["suggested_type"] == "person"
    assert candidate_by_id["cand-6781"]["suggested_type"] == "place"
    assert decisions["cand-1232"]["decision"] == "new" and not decisions["cand-1232"].get("ku_id")
    assert sync.get_group(decisions["cand-1232"].get("resolution_note", "")) == ITEMS["cand-1232"]["group"]
    assert decisions["cand-6781"]["decision"] == "new" and not decisions["cand-6781"].get("ku_id")
    assert sync.get_group(decisions["cand-6781"].get("resolution_note", "")) == ITEMS["cand-6781"]["group"]

    files = {source["source_file"] for item in ITEMS.values() for source in item["sources"]}
    source_text = {
        path: " ".join((ROOT / path).read_text(encoding="utf-8-sig").split())
        for path in files
    }
    for item in ITEMS.values():
        for source in item["sources"]:
            for _, quote in source["quotes"]:
                assert " ".join(quote.split()) in source_text[source["source_file"]], (source["location"], quote)
    assert "Grimaldi, Giovanni Francesco, 57,155,182-3" in source_text["02-sources/02-Markdown/22_CHP-22Index.md"]
    assert "Gianfrancesco Grimaldi" in source_text["02-sources/02-Markdown/06_CHP-6_sec_i.md"]
    assert "Giovanni Francesco Grimaldi" in source_text["02-sources/02-Markdown/07_CHP-7_sec_i.md"]
    assert "formerly Palais Mazarin" in source_text["02-sources/02-Markdown/00_05_List_of_Plates.md"]

    statements = sync.load_statements()
    for candidate_id, expected in EXPECTED_STATEMENTS.items():
        direct = {
            row["statement_id"]: row for row in statements
            if candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        }
        assert set(direct) == set(expected), (candidate_id, sorted(set(direct) ^ set(expected)))
        for statement_id, expected_flag in expected.items():
            actual = (direct[statement_id].get("qualifiers") or {}).get("relation_candidate")
            assert actual is expected_flag, statement_id

    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id["cand-1232"]["resolution_note"] += (
        " S3 cross-chapter source check 2026-10-17: the index entry G.csv#142 groups pp.57, 155, 182–183, and 191 under "
        "‘Giovanni Francesco Grimaldi’; Chapters 2 and 7 give that full form, while Chapter 6 uses ‘Gianfrancesco’. "
        "The indexed p.155 locator supports the variant as this same source-local person. The index transcription ‘lyi’ for the final locator is retained as OCR noise; p.191 itself gives the full name. "
        "No matching same-type person KU exists. The p.191 studio-visit statement remains attached to unidentified studios cand-6959, not to this person as a relationship endpoint."
    )
    planned_by_id["cand-6781"]["resolution_note"] += (
        " S3 source-boundary check 2026-10-17: the p.181–182 account identifies a distinct upper-gallery interior within Palais Mazarin; "
        "the Plate 26b caption locates the gallery ceiling in Bibliothèque Nationale (formerly Palais Mazarin). "
        "The palace and ceiling painting remain separate existing identities; this source-local place group represents only the gallery space."
    )

    planned_manifest = list(manifest)
    existing_ids = {row.get("ku_id") for row in manifest}
    existing_cards = {row.get("card_path") for row in manifest}
    accepted_lines = accepted.splitlines()
    for candidate_id, item in ITEMS.items():
        row = planned_by_id[candidate_id]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert item["ku_id"] not in existing_ids and item["card_rel"] not in existing_cards
        assert not (ROOT / item["card_rel"]).exists()
        assert item["card_rel"] not in accepted
        row["ku_id"] = item["ku_id"]
        row["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": item["type"],
            "canonical_name": item["name_zh"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > item["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {item['card_rel']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3–S4：Grimaldi 跨章人物组与 Mazarin 画廊地点（2026-10-17）\n\n"
        "S3 复核 `cand-1232`：索引 G.csv#142 以 Giovanni Francesco Grimaldi 汇集第2章 p.57、第6章 p.155、第7章 pp.182–183、191；正文p.155的 ‘Gianfrancesco’ 由索引同条目和相邻语境支持为同一书内人物。索引转录末尾 ‘lyi’ 保留，正文 p.191 有全名定位。该人物无同类型既有KU，按现行 new 组登记。"
        "`cand-1231`（Angelica Griè）仍因索引页212n无正文提及而 undecided，不并入 Grimaldi。`cand-6784` 未列成员的意大利艺术家集合、`cand-6803` 未定位的耶稣会神学院、`cand-6959` 三处未定位画家工作室均保留 undecided。"
        "`cand-6781` 为 Mazarin 宫殿上层画廊这一内部 place；图版目录将相关天花板作品定位于 Bibliothèque Nationale（formerly Palais Mazarin），故不与整座 Palais Mazarin（cand-3946）或顶画（cand-4090）合并。"
        "人物 `cand-1232` 与画廊 `cand-6781` 分别登记；Romanelli、Rospigliosi、Colonna family palace、Palais Mazarin、顶画复用已有 KU。4条 Grimaldi 和6条画廊直接 relation_candidate 全部留待 S6；一条 landscape artist 属性维持非关系。`relations.csv` 未改。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S3–S4 复核：Grimaldi 与 Mazarin 画廊（2026-10-17）\n\n"
        "Grimaldi 全名及第6章变体按同一索引条目与跨章页码归组；`cand-1232` 已登记一张 source-local person 卡。Mazarin 宫殿上层画廊按独立 place 身份登记，与 Palais Mazarin 和《Romulus and Remus》顶画分开。"
        "索引未支持的 Angelica Griè、成员不明艺术家集合、未定位神学院与工作室仍为 undecided；现有关系端点复用决定保持原样。"
        "本批关系候选留待 S6，未新增正式关系。"
        f"S3 new 共{sync.fmt(totals['new_candidates'])}条候选/{sync.fmt(totals['new_groups'])}组；"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    if args.dry_run:
        print("Grimaldi cross-chapter identity and Mazarin gallery S4 dry-run passed")
        print("cand-1232: four chapters and index entry support one Giovanni Francesco Grimaldi person group")
        print("cand-6781: distinct upper-gallery place; Palais Mazarin and ceiling work reuse targets verified")
        print("4 person relations + 6 place relations remain pending S6; non-relation statement preserved")
        print("Angelica Griè, artist collective, seminary, and studios remain undecided")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}")
        print(f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; new alignment rows pending={sync.fmt(totals['pending_members'] + 15)}")
        print("no files changed")
        return 0

    for item in ITEMS.values():
        path = ROOT / item["card_rel"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(make_card(item), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: two KUs registered; manifest={len(planned_manifest)}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
