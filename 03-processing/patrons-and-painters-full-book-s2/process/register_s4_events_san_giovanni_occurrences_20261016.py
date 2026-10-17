from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
SERIES_CANDIDATE = "cand-6039"
SERIES_KU = "units/events/annual-exhibition-s-giovanni-decollato"
SERIES_CARD = "annual-exhibition-s-giovanni-decollato.md"
BOOK_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

EVENTS = (
    {
        "candidate": "cand-11766",
        "group": "sg3-event-cand-11766",
        "ku_id": "units/events/s-giovanni-decollato-exhibition-1662",
        "card": "04-knowledge/units/events/s-giovanni-decollato-exhibition-1662.md",
        "zh": "罗马圣若望斩首堂1662年展览",
        "en": "1662 Exhibition at S. Giovanni Decollato, Rome",
        "year": "1662",
        "direct": 4,
        "relations": 4,
        "summary": "第5章称1662年由 Sacchetti 负责组织展览；Pietro da Cortona 获显著位置，Sacchetti 还从罗马著名画廊借来古代大师作品。",
        "quotes": (
            ("line 81", "In 1662 it fell to the Sacchetti to organise the exhibition."),
            ("line 81", "Naturally, writes Rosa, pride of place was given to Pietro da Cortona, the family painter."),
            ("line 81", "they were also able to obtain the loan of old masters from many of the most famous galleries of the city."),
        ),
        "body": """### 书内活动记录

- **组织：** 哈斯克尔称1662年由 Sacchetti 负责组织本届展览。
- **陈列：** 哈斯克尔转述 Rosa 称，Pietro da Cortona 获显著位置；Sacchetti 还利用其在罗马贵族中的影响力，从城中著名画廊借来古代大师作品。
""",
    },
    {
        "candidate": "cand-11767",
        "group": "sg3-event-cand-11767",
        "ku_id": "units/events/s-giovanni-decollato-exhibition-1668",
        "card": "04-knowledge/units/events/s-giovanni-decollato-exhibition-1668.md",
        "zh": "罗马圣若望斩首堂1668年展览",
        "en": "1668 Exhibition at S. Giovanni Decollato, Rome",
        "year": "1668",
        "direct": 8,
        "relations": 8,
        "summary": "第5章以1662年之后六年叙述 Rospigliosi 负责展览，陈列规模与奢华程度超过此前；展场延展至教堂外部空间。",
        "quotes": (
            ("line 81", "Six years later the Rospigliosi were responsible and they challenged all previous patrons by the lavishness of the display they organised."),
            ("line 81", "The whole façade, the cemetery, the piazza and even the adjoining street were draped with rare and precious tapestries, silver and magnificent pictures."),
            ("line 82", "The Rospigliosi decided that only old masters should be shown and that all contemporary work should be excluded."),
            ("lines 82–83", "he managed—alone among living artists—to get two of his pictures exhibited."),
        ),
        "body": """### 书内活动记录

- **组织：** 哈斯克尔由1662年“六年后”推至1668年，称 Rospigliosi 负责组织，并以展陈奢华程度超过此前各届。
- **展场与展品：** 临近的立面、墓园、广场及街道悬挂挂毯、银器和画作；组织者决定只展古代大师作品、排除当代作品。Salvator Rosa 最终仍有两幅作品入选。
- **语境：** Haskell 称 Camillo Rospigliosi（教宗之弟）及其四名儿子刚成为管理教堂的 Compagnia della Misericordia 初学成员；此背景不改变该届展览本身的身份。
""",
    },
    {
        "candidate": "cand-11768",
        "group": "sg3-event-s-giovanni-decollato-1675",
        "ku_id": "units/events/s-giovanni-decollato-exhibition-1675",
        "card": "04-knowledge/units/events/s-giovanni-decollato-exhibition-1675.md",
        "zh": "罗马圣若望斩首堂1675年圣年展览",
        "en": "Holy Year 1675 Exhibition at S. Giovanni Decollato, Rome",
        "year": "1675",
        "direct": 3,
        "relations": 3,
        "summary": "第5章称1675年圣年另办一次华丽展览，Medici 展出二百余幅画作，并以织物装饰教堂外部空间。",
        "quotes": (
            ("line 88", "Another lavish exhibition was arranged for the Holy Year of 1675 when over two hundred pictures were shown by the Medici."),
            ("line 88", "Outside the church were hung tapestries and damasks giving the illusion of stage scenery as the public walked among them; while inside the cloisters and in one of the rooms opening on to them were works by living and dead artists including Raphael, Titian and the Carracci."),
        ),
        "body": """### 书内活动记录

- **展览：** 哈斯克尔称1675年圣年另办一次华丽展览，Medici 展出了二百余幅作品。
- **布置与作品：** 教堂外悬挂挂毯与锦缎，形成舞台布景般的效果；回廊内及相连房间展出在世与已故艺术家的作品，包括 Raphael、Titian 和 Carracci。
""",
    },
    {
        "candidate": "cand-11769",
        "group": "sg3-event-s-giovanni-decollato-1736",
        "ku_id": "units/events/s-giovanni-decollato-exhibition-1736",
        "card": "04-knowledge/units/events/s-giovanni-decollato-exhibition-1736.md",
        "zh": "罗马圣若望斩首堂1736年展览",
        "en": "1736 Exhibition at S. Giovanni Decollato, Rome",
        "year": "1736",
        "direct": 4,
        "relations": 2,
        "summary": "第5章称1736年展出新旧画作212幅并发行目录；原文只说有人期待教宗竞价，不确认其实际出价。",
        "quotes": (
            ("line 90", "Thus 212 pictures, old and modern, were exhibited in 1736, a catalogue was issued, and there were hopes that the Pope would make a bid."),
        ),
        "body": """### 书内活动记录

- **展品与目录：** 哈斯克尔记载，1736年展出了212幅古代与当代画作，并发行目录。
- **可能的购藏：** 原文只称当时“希望”教宗出价；未确认是否提出报价或购入作品。
""",
    },
)


def make_card(event: dict) -> str:
    source_rows = []
    page = "127" if event["year"] in {"1662", "1668"} else "128"
    line_range = "81–83" if event["year"] == "1662" else ("81–83" if event["year"] == "1668" else ("88" if event["year"] == "1675" else "90"))
    for span, quote in event["quotes"]:
        source_rows.append(
            {
                "citation": BOOK_CITATION,
                "location": f"第5章第I节；印刷页{page}；OCR L{line_range}",
                "sentence_summary": event["summary"],
                "original_quotes": [{"source_span": span, "text": quote}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": f"lines {line_range}; print p. {page}",
                },
            }
        )
    frontmatter = {
        "title": f"{event['zh']}（{event['en']}）",
        "name_en": event["en"],
        "type": "event",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    page_link = f"[第5章 p.{page}](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L{line_range}）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录罗马 S. Giovanni Decollato 每年8月29日年度展览系列中的 {event['year']} 年具体场次。哈斯克尔将该场次与已单独建卡的[年度展览系列]({SERIES_CARD})联系；此为原书候选关系，正式 `instance_of` 边留待 S6。{page_link}

**English:** This unit records the specific {event['year']} occurrence in the annual exhibition series held at S. Giovanni Decollato in Rome on 29 August. Haskell connects this occurrence to the separately registered [annual series]({SERIES_CARD}); this remains a source-backed relationship candidate pending formal `instance_of` review in S6. {page_link}

### 活动性质与时间

- **活动性质：** 年度重复展览系列中的一次具体场次；与系列本体分开登记。
- **时间：** {event['year']}年；系列按年于8月29日举行，但本届具体日仍以系列语境为依据，不增补原文未载的届次日历记录。
- **地点：** 罗马 S. Giovanni Decollato 教堂回廊及原文明确提及的相邻展场空间。{page_link}

{event['body']}
## 关系与证据

### 关系记录

当前没有已登记的正式关系。与年度系列的 `instance_of` 关系及本届组织、参展和陈列关系仍在[原书陈述表](../../tables/book-statements.jsonl)中逐条留待 S6。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four dated S. Giovanni Decollato exhibition occurrences in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert decisions[SERIES_CANDIDATE]["ku_id"] == SERIES_KU
    assert len(EVENTS) == 4
    for event in EVENTS:
        cid = event["candidate"]
        assert candidate_by_id[cid].get("suggested_type") == "event"
        row = decisions[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert result_sync.get_group(row.get("resolution_note", "")) == event["group"]
        group_rows = [
            r for r in alignments
            if r.get("candidate_id") and not r.get("external_source")
            and r.get("decision") == "new"
            and result_sync.get_group(r.get("resolution_note", "")) == event["group"]
        ]
        assert [r["candidate_id"] for r in group_rows] == [cid]
        assert not (ROOT / event["card"]).exists()
        assert event["card"] not in accepted
        assert not any(r.get("ku_id") == event["ku_id"] or r.get("card_path") == event["card"] for r in manifest)

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for event in EVENTS:
        for _, quote in event["quotes"]:
            assert " ".join(quote.split()) in source_text, (event["candidate"], quote)

    statements = result_sync.load_statements()
    direct_by_id = {}
    for event in EVENTS:
        cid = event["candidate"]
        direct = [
            row for row in statements
            if row.get("subject_candidate_id") == cid or row.get("object_candidate_id") == cid
        ]
        relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
        assert len(direct) == event["direct"], (cid, len(direct))
        assert len(relations) == event["relations"], (cid, len(relations))
        assert any(
            row.get("subject_candidate_id") == cid and row.get("object_candidate_id") == SERIES_CANDIDATE
            for row in direct
        ), f"{cid} lacks its source-backed series-instance statement"
        direct_by_id[cid] = (len(direct), len(relations))

    planned_alignment = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    cards = []
    for event in EVENTS:
        row = next(r for r in planned_alignment if r.get("candidate_id") == event["candidate"] and not r.get("external_source"))
        row["ku_id"] = event["ku_id"]
        row["resolution_note"] += f" S4 registration: mapped {event['group']} to {event['ku_id']}."
        planned_manifest.append(
            {
                "ku_id": event["ku_id"],
                "type": "event",
                "canonical_name": event["zh"],
                "name_en": event["en"],
                "source_task": TASK,
                "card_path": event["card"],
            }
        )
        cards.append((ROOT / event["card"], make_card(event)))

    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S4 event：S. Giovanni Decollato 年度展览四个具体场次登记（2026-10-16）\n\n"
        "将 `cand-11766`（1662）、`cand-11767`（1668）、`cand-11768`（1675圣年）与 `cand-11769`（1736）分别映射至各自事件卡；四者均为已登记年度系列 `cand-6039` 的具体场次，不并入系列本体。1662、1668年份来自原文明确年份及“六年后”的时间顺序；系列日期为每年8月29日，但不为各场次另补精确日。1736年212幅画作与目录为实际记载，教宗出价仅为原文所说的期待。"
        "四卡均保留组织、陈列和届次关系为 S2 候选，不写入正式 `relations.csv`；四组共19条直接 S2 陈述，其中17条为关系候选，留待 S6；未开展 S5。"
        f"S4 累计登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    result_note = (
        "\n\n### event：S. Giovanni Decollato 1662、1668、1675、1736年场次 S4 登记（2026-10-16）\n\n"
        "四个具体年份的展览现各有独立事件卡，分别连接同一年度系列；不把场次、系列本体或管理教堂合并。17条关系候选留待 S6。"
        f"全书 S4 当前登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print("S4 event occurrences dry-run passed:")
        for event in EVENTS:
            print(f"  {event['candidate']} ({event['year']}) -> {event['ku_id']}; direct={event['direct']}; relation candidates={event['relations']}")
        print("all four source quotes checked; each occurrence remains distinct from the annual series")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted paths unique")
        print(f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}")
        return 0

    for path, content in cards:
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    result_sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    result_sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    for event in EVENTS:
        card_rel = event["card"]
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card_rel}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied {len(EVENTS)} event occurrences; manifest={len(planned_manifest):,}; "
        f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; "
        f"pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
