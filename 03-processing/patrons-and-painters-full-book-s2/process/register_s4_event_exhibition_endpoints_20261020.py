from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-20"
ANCHOR = "s4-event-direct-endpoints-exhibitions-ch5-ch10-20261020"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

BATCH = [
    {
        "candidate": "cand-11770",
        "group": "sg3-event-cand-11770",
        "alignment_id": "aln-11933",
        "ku_id": "units/events/s-salvatore-in-lauro-exhibition-1675",
        "card_rel": "04-knowledge/units/events/s-salvatore-in-lauro-exhibition-1675.md",
        "name_zh": "圣年1675年圣萨尔瓦托雷因劳罗展览",
        "name_en": "Holy Year 1675 Exhibition at S. Salvatore in Lauro",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "location": "第5章第I节，印刷页128，原文行94。",
        "source_span": "line 94; print p.128",
        "quotes": [
            "We know that in the Holy Year of 1675, so rich in exhibitions, the one at S. Salvatore in Lauro was said to equal any held in Rome.",
        ],
        "summary": "Haskell identifies the S. Salvatore in Lauro exhibition held in the Holy Year 1675 and reports that it was said to equal any exhibition in Rome. The reported comparison is not treated as an independently established evaluation.",
        "cn": "本卡登记哈斯克尔在常规展览系列叙述中明确指称的圣年1675年 S. Salvatore in Lauro 展览这一具体届次。原书称其“据说”可与罗马任何展览相比；这是来源转述的评价，不是本卡的独立判断。该届次与已登记的常规系列分别成卡；所属系列关系及确切场地端点留待 S6。",
        "en": "This unit records the specific Holy Year 1675 exhibition at S. Salvatore in Lauro that Haskell identifies in his account of the regular exhibition series. The source says it was reported to equal any exhibition in Rome; this is a reported evaluation, not an independent judgment in this unit. The dated occurrence has its own unit, separate from the registered recurring series; the series relation and a precise venue endpoint remain for S6.",
        "details": [
            "活动性质 / Event: 圣年1675年的具体画展场次；不代表整个常规系列。",
            "来源评价 / Reported evaluation: Haskell称该届展览据说可与罗马任何展览相比；仅保留为转述。",
        ],
        "relations": [
            "st-chp5-p128-salvatore-1675-instance-of-series",
            "st-chp5-p128-salvatore-exhibition-purpose",
            "st-chp5-p128-salvatore-lenders-glorified",
        ],
    },
    {
        "candidate": "cand-11771",
        "group": "sg3-event-cand-11771",
        "alignment_id": "aln-11934",
        "ku_id": "units/events/s-salvatore-in-lauro-exhibition-1697",
        "card_rel": "04-knowledge/units/events/s-salvatore-in-lauro-exhibition-1697.md",
        "name_zh": "1697年圣萨尔瓦托雷因劳罗展览",
        "name_en": "1697 Exhibition at S. Salvatore in Lauro",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "location": "第5章第I节，印刷页128，原文行97。",
        "source_span": "line 97; print p.128",
        "quotes": [
            "Thus in 1697 Prince Pio agreed to lend his pictures entirely at his own expense—on condition that his alone were shown.",
            "They included a number of Venetian old masters and were all hung together under the arcades of the loggia.",
            "But in order to satisfy other collectors who also wanted to display their treasures further pictures were hung separately in the upper gallery of the cloisters.",
            "The occasion turned into a brilliant social ceremony with a sermon from the preacher of St Peter’s and a great assembly of cardinals.",
        ],
        "summary": "Haskell describes the 1697 exhibition in which Prince Pio lent pictures at his own expense on the condition that only his pictures be shown; other collectors were accommodated with a separate display, and the occasion became a social ceremony. The other collectors, preacher, and cardinals are not named in this passage.",
        "cn": "本卡登记哈斯克尔记载的1697年展览场次。Prince Pio 同意自费出借画作，条件是只展出他的画；为满足其他收藏者，另有画作陈列于回廊上层画廊。作者称该场次成为一场社会仪式，包含圣彼得教堂一位传道者的布道及枢机主教集会。此处没有给其他收藏者、传道者或枢机主教具名；本卡不为这些群体补造身份。",
        "en": "This unit records the 1697 exhibition described by Haskell. Prince Pio agreed to lend pictures at his own expense on the condition that only his pictures be shown; further pictures were displayed in the upper gallery of the cloisters to accommodate other collectors. Haskell says the occasion became a social ceremony with a sermon by a preacher of St Peter’s and an assembly of cardinals. The passage does not name the other collectors, preacher, or cardinals; this unit does not supply identities for them.",
        "details": [
            "时间 / Date: 1697年。",
            "出借条件 / Lending condition: Prince Pio 同意自费出借，条件是只展出他的画作。",
            "陈列 / Display: Pio 的威尼斯古代大师画作集中陈列于 loggia 拱廊下；为满足其他收藏者，另有画作陈列于回廊上层画廊。",
            "仪式 / Ceremony: Haskell称该场次有圣彼得教堂传道者布道和枢机主教集会；此处未具名。",
        ],
        "relations": [
            "st-chp5-p128-salvatore-1697-instance-of-series",
            "st-chp5-p128-other-collectors-display-intent",
            "st-chp5-p128-preacher-sermon",
            "st-chp5-p128-cardinals-assembly",
        ],
    },
    {
        "candidate": "cand-9872",
        "group": "sg3-event-cand-9872",
        "alignment_id": "aln-10044",
        "ku_id": "units/events/venetian-academy-piazzetta-exhibition-series",
        "card_rel": "04-knowledge/units/events/venetian-academy-piazzetta-exhibition-series.md",
        "name_zh": "威尼斯学院皮亚泽塔年度展览系列",
        "name_en": "Venetian Academy Annual Exhibition Series at the Piazzetta",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章第II节，印刷页331，原文行271。",
        "source_span": "line 271; print p.331",
        "quotes": [
            "In 1777 a much more official type of exhibition was organised when a number of nobles asked the members of the Academy to display their work each year at a stand in the Piazzetta.",
            "The artists viewed the arrangements without enthusiasm as they themselves were required to meet all the expenses, which were heavy.",
            "Many of them did not have pictures available for exhibition, and the Academy had to resort to loans to make up the required numbers.",
            "Complaints were frequently made and by 1787 the cost had become crippling and the shows were discontinued.",
        ],
        "summary": "Haskell says that in 1777 nobles asked Academy members to exhibit annually at a stand in the Piazzetta. The artists bore heavy costs, the Academy used loans to make up the required number of pictures, and the shows had been discontinued by 1787. The exact final exhibition year is not given.",
        "cn": "本卡登记哈斯克尔所述威尼斯学院在皮亚泽塔设立年度展览安排的系列：1777年一群未具名贵族请求学院成员每年在一处展台展示作品；艺术家须承担高额开销，学院还需借画补足数量。作者说抱怨频繁，到1787年费用已难以承受，展览遂停止；原文没有给出末届的确切年份。“国家干预艺术”的句子是作者对这一变化的总结，不作为独立机构或关系事实。第10章 p.331 尚未完成本轮独立 S2 审读。",
        "en": "This unit records the annual exhibition arrangement described by Haskell for the Venetian Academy at a stand in the Piazzetta. In 1777 a group of unnamed nobles asked Academy members to exhibit there each year; artists had to meet heavy expenses, and the Academy resorted to loans to make up the required number of pictures. Haskell says complaints were frequent and that the shows had been discontinued by 1787 because costs had become crippling; the exact final year is not stated. His concluding phrase about State interference in the arts is retained as the author’s interpretation, not made into a separate institutional or relational fact. Chapter 10, p. 331, has not yet been covered by this round of independent S2 review.",
        "details": [
            "活动性质 / Event: 在威尼斯皮亚泽塔一处展台举行的年度展览安排；本卡登记系列，不指某一届。",
            "开始 / Start: 1777年；未具名贵族请求学院成员每年展示作品。",
            "费用与借展 / Costs and loans: 艺术家承担高额费用；学院借入画作补足展出数量。",
            "终止 / End: Haskell称展览至1787年时已停办；不推定末届确切年份。",
        ],
        "relations": [
            "st-chp10-p331-academy-borrowed-pictures",
            "st-chp10-p331-academy-exhibition-series-started-1777",
            "st-chp10-p331-academy-exhibitors-bore-cost",
            "st-chp10-p331-state-interference-evaluation",
        ],
    },
]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, fieldnames, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_block(item):
    return {
        "citation": BOOK_CITATION,
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [
            {"source_span": item["source_span"], "text": quote}
            for quote in item["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": item["source_file"],
            "source_span": item["source_span"],
        },
    }


def make_card(item):
    frontmatter = {
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": "event",
        "sub_type": "recurring annual exhibition series" if item["candidate"] == "cand-9872" else "dated exhibition occurrence",
        "evidence_status": "source_backed",
        "sources": [source_block(item)],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_path = "../../../" + item["source_file"]
    page = "128" if item["candidate"] in {"cand-11770", "cand-11771"} else "331"
    line = "94" if item["candidate"] == "cand-11770" else "97" if item["candidate"] == "cand-11771" else "271"
    ref = f"[第{5 if page == '128' else 10}章 p.{page}]({source_path})（L{line}）"
    details = "\n".join(f"- {row}〔{ref}〕" for row in item["details"])
    relations = "、".join(f"`{rid}`" for rid in item["relations"])
    body = f"""## 内容

### 描述

**中文：** {item['cn']}〔{ref}〕

**English:** {item['en']} {ref}

### 活动性质与时间

{details}

## 关系与证据

当前没有登记在 `relations.csv` 中的正式关系。与本候选直接相关的 S2 关系候选 {relations} 均留待 S6，逐项核对端点、谓词、方向、时间／语境及来源证据；本次 S4 登记不预判关系成立。
"""
    return f"---\n{fm}---\n\n{body}"


def insert_accepted(text, paths):
    lines = text.splitlines()
    for path in paths:
        if f"- {path}" in lines:
            raise AssertionError(f"accepted.yml already includes {path}")
    for path in sorted(paths):
        insert_at = next(
            (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > path),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {path}")
    return "\n".join(lines) + "\n"


def direct_queue(candidates, alignment, statements, sync):
    by_id = {row["candidate_id"]: row for row in candidates}
    decision = {row["candidate_id"]: row for row in alignment if row.get("candidate_id") and not row.get("external_source")}
    pending_group_members = defaultdict(list)
    for cid, row in decision.items():
        if cid in by_id and row.get("decision") == "new" and not row.get("ku_id"):
            group = sync.get_group(row.get("resolution_note", ""))
            pending_group_members[group].append(cid)
    direct_ids = set()
    for statement in statements:
        if statement.get("qualifiers", {}).get("relation_candidate") is True:
            direct_ids.update(cid for cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) if cid)
    direct_groups = {
        sync.get_group(decision[cid].get("resolution_note", ""))
        for cid in direct_ids
        if cid in decision and decision[cid].get("decision") == "new" and not decision[cid].get("ku_id")
    }
    direct_candidate_count = sum(len([cid for cid in pending_group_members[g] if cid in direct_ids]) for g in direct_groups)
    direct_member_count = sum(len(pending_group_members[g]) for g in direct_groups)
    by_type = defaultdict(lambda: {"groups": 0, "candidates": 0, "members": 0})
    for group in direct_groups:
        members = pending_group_members[group]
        kind = by_id[members[0]].get("suggested_type", "未分类")
        by_type[kind]["groups"] += 1
        by_type[kind]["members"] += len(members)
        by_type[kind]["candidates"] += len([cid for cid in members if cid in direct_ids])
    return {
        "groups": len(direct_groups),
        "candidates": direct_candidate_count,
        "members": direct_member_count,
        "by_type": dict(by_type),
    }


def main():
    parser = argparse.ArgumentParser(description="Register three source-backed event endpoints in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(PROCESS_DIR))
    import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
    import register_s4_archive_memmo_query_sheet_20261017 as archive_sync

    candidate_fields, candidates = read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_rows = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

    planned_alignment = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    card_texts = {}
    used_groups = set()
    for item in BATCH:
        candidate = candidate_by_id[item["candidate"]]
        alignment = decision_rows[item["candidate"]]
        assert candidate["suggested_type"] == "event"
        assert alignment["alignment_id"] == item["alignment_id"]
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == item["group"]
        assert item["group"] not in used_groups
        used_groups.add(item["group"])
        assert not (ROOT / item["card_rel"]).exists()
        assert item["card_rel"] not in accepted
        assert not any(row.get("ku_id") == item["ku_id"] or row.get("card_path") == item["card_rel"] for row in manifest)
        assert not any(row.get("type") == "event" and (row.get("name_en", "").casefold() == item["name_en"].casefold() or row.get("canonical_name", "") == item["name_zh"]) for row in manifest)

        source = ROOT / item["source_file"]
        flat_source = " ".join(source.read_text(encoding="utf-8-sig").split())
        for quote in item["quotes"]:
            assert " ".join(quote.split()) in flat_source, f"quotation mismatch: {item['candidate']}"

        direct = [row for row in statements if item["candidate"] in (row.get("subject_candidate_id"), row.get("object_candidate_id"))]
        relation_ids = {
            row["statement_id"] for row in direct
            if row.get("qualifiers", {}).get("relation_candidate") is True
        }
        assert relation_ids == set(item["relations"]), (item["candidate"], relation_ids)

        target = next(row for row in planned_alignment if row.get("candidate_id") == item["candidate"] and not row.get("external_source"))
        target["ku_id"] = item["ku_id"]
        target["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."
        planned_manifest.append({
            "ku_id": item["ku_id"], "type": "event", "canonical_name": item["name_zh"],
            "name_en": item["name_en"], "source_task": TASK, "card_path": item["card_rel"],
        })
        card = make_card(item)
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)
        card_texts[item["card_rel"]] = card

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    direct = direct_queue(candidates, planned_alignment, statements, sync)
    assert direct["groups"] == 1756 and direct["members"] == 1770, direct
    event_direct_groups = direct["by_type"].get("event", {}).get("groups", 0)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_text = archive_sync.refresh_process_type_table(process_text, stats)
    relation_candidates = [row for row in statements if row.get("qualifiers", {}).get("relation_candidate") is True]
    missing_endpoints = [row for row in relation_candidates if not row.get("subject_candidate_id") or not row.get("object_candidate_id")]
    missing_subject = sum(not row.get("subject_candidate_id") for row in missing_endpoints)
    missing_object = sum(not row.get("object_candidate_id") for row in missing_endpoints)
    enrichment_rows = [line for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    untyped = sum(not row.get("suggested_type") or row.get("suggested_type") == "unclassified" for row in candidates)
    direct_by_type = "、".join(
        f"{kind} {direct['by_type'].get(kind, {}).get('groups', 0)}组／{direct['by_type'].get(kind, {}).get('members', 0)}成员"
        for kind in ("person", "institution", "event", "place", "work", "archive", "term")
        if direct["by_type"].get(kind, {}).get("groups", 0)
    )
    current_snapshot = (
        f"当前快照（{DATE}）：人物冲突{stats['person']['conflict']}项、作品冲突{stats['work']['conflict']}项；冲突两侧和来源位置均留在候选行，不强选一方。"
        f"{totals['undecided']}项 `undecided` 各自保留对象、版本、身份、类型或来源锚点不足的理由与后续去向；其中{untyped}项仍为未分类类型，等待类型证据，不强塞入现有类。"
        f"按候选级裁决汇总，{totals['total']}个候选均有现行决定；same={totals['same_candidates']}（指向{totals['same_kus']}个既有KU）、new={totals['new_candidates']}（{totals['new_groups']}个身份组）。"
        f"S4已登记{totals['registered_groups']}组／{totals['registered_members']}条映射，待登记{totals['pending_groups']}组／{totals['pending_members']}条成员映射；"
        f"其中直接关系端点待登记{direct['groups']}组／{direct['candidates']}个直接端点候选、共含{direct['members']}条组成员映射（{direct_by_type}），"
        f"非直接映射待登记{totals['pending_groups'] - direct['groups']}组／{totals['pending_members'] - direct['members']}条。"
        f"S2有{len(relation_candidates)}条 `relation_candidate=true` statement，其中{len(missing_endpoints)}条至少一端没有候选ID（仅缺subject {missing_subject - sum(not row.get('subject_candidate_id') and not row.get('object_candidate_id') for row in missing_endpoints)}、"
        f"仅缺object {missing_object - sum(not row.get('subject_candidate_id') and not row.get('object_candidate_id') for row in missing_endpoints)}、两端均缺{sum(not row.get('subject_candidate_id') and not row.get('object_candidate_id') for row in missing_endpoints)}）。"
        f"字段表共{len(enrichment_rows)}条，其中{sum(json.loads(line).get('evidence_status') == 'unverified' for line in enrichment_rows)}条unverified。"
        "上述是决定记录与映射状态，不表示冲突、待证身份或关系已解决。"
    )
    snapshot_pattern = re.compile(r"当前快照（2026-10-19）：.*?(?=\n\n)", re.S)
    process_text, snapshot_count = snapshot_pattern.subn(current_snapshot, process_text, count=1)
    assert snapshot_count == 1, "could not refresh current process snapshot"
    process_note = f"""

<a id="{ANCHOR}"></a>

### S4 event：第5、10章展览直接端点登记（{DATE}）

沿用既有 S3 `new` 决定，将三个事件身份组各登记为一张 KU，并按已核原文保存双语描述和逐条引文。

| candidate | S3 身份组 | 来源锚点 | S4 KU | 直接 S2 关系候选 |
|---|---|---|---|---|
| `cand-11770` | `sg3-event-cand-11770` | 第5章 p.128 L94 | `units/events/s-salvatore-in-lauro-exhibition-1675` | `st-chp5-p128-salvatore-1675-instance-of-series`、`st-chp5-p128-salvatore-exhibition-purpose`、`st-chp5-p128-salvatore-lenders-glorified` |
| `cand-11771` | `sg3-event-cand-11771` | 第5章 p.128 L97 | `units/events/s-salvatore-in-lauro-exhibition-1697` | `st-chp5-p128-salvatore-1697-instance-of-series`、`st-chp5-p128-other-collectors-display-intent`、`st-chp5-p128-preacher-sermon`、`st-chp5-p128-cardinals-assembly` |
| `cand-9872` | `sg3-event-cand-9872` | 第10章 p.331 L271 | `units/events/venetian-academy-piazzetta-exhibition-series` | `st-chp10-p331-academy-borrowed-pictures`、`st-chp10-p331-academy-exhibition-series-started-1777`、`st-chp10-p331-academy-exhibitors-bore-cost`、`st-chp10-p331-state-interference-evaluation` |

1675与1697是两个具体展览场次，不与已登记的 S. Salvatore 常规系列合并；1675 的来源评价保持为转述。1697卡仅记录 Prince Pio 的出借条件、分区陈列和未具名仪式参与者，不补推个人身份。`cand-9872` 登记为年度系列：1777年开始，Haskell称至1787年时展览已停止，未推定末届年份；“国家干预艺术”的总结保留为作者判断。第10章 p.331 尚未完成本轮独立 S2 审读。

本批新增3张事件卡、3条 manifest 记录、3条 accepted 路径及3条 alignment KU 映射；S3 决定和组边界未变。上述11条直接 `relation_candidate=true` 陈述均留待 S6 逐项裁决，本轮未写入正式关系、未新增 S5 字段或外部身份行。

登记后 S4 已登记{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['new_groups'])}组、{sync.fmt(totals['registered_members'])}/{sync.fmt(totals['new_candidates'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条映射。直接端点队列为{sync.fmt(direct['groups'])}组/{sync.fmt(direct['candidates'])}个候选/{sync.fmt(direct['members'])}条成员映射，其中事件{sync.fmt(event_direct_groups)}组；非直接待登记队列为{sync.fmt(totals['pending_groups'] - direct['groups'])}组/{sync.fmt(totals['pending_members'] - direct['members'])}条映射。KU={len(planned_manifest)}。
"""
    process_text += process_note

    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    plan_pattern = re.compile(r"^3\. \*\*批量完成S4直接关系端点。\*\*.*?(?=^4\.)", re.M | re.S)
    plan_item = (
        f"3. **批量完成S4直接关系端点。** 当前已登记{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['new_groups'])}组、"
        f"{sync.fmt(totals['registered_members'])}/{sync.fmt(totals['new_candidates'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组／{sync.fmt(totals['pending_members'])}条；"
        f"直接端点队列为{sync.fmt(direct['groups'])}组／{sync.fmt(direct['candidates'])}个候选／{sync.fmt(direct['members'])}条成员映射（事件{sync.fmt(event_direct_groups)}组），"
        f"非直接队列为{sync.fmt(totals['pending_groups'] - direct['groups'])}组／{sync.fmt(totals['pending_members'] - direct['members'])}条映射。"
        "本批完成第5章两项具体展览场次和威尼斯学院年度展览系列登记；后续按端点影响、来源锚点和身份边界稳定性分类型批次处理。KU登记只解除端点缺口，不预判S6关系成立。\n"
    )
    result_text, replaced = plan_pattern.subn(plan_item, result_text, count=1)
    assert replaced == 1, "could not refresh S4 plan item"
    result_note = f"""

### S4 event：第5、10章展览直接端点登记（{DATE}）

`cand-11770`与`cand-11771`分别登记为1675、1697年 S. Salvatore in Lauro 的具体展览场次，保持与既有常规系列卡分立；`cand-9872`登记为1777年开始、至1787年时已停办的威尼斯学院皮亚泽塔年度展览系列，不补推末届年份。共新增3张双语事件卡和3条候选映射。11条直接 S2 关系候选仍留待 S6；没有新增正式关系、S5字段或外部身份行。详情见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""
    insert_marker = "\n\n## 范围与覆盖\n"
    assert insert_marker in result_text
    result_text = result_text.replace(insert_marker, result_note + insert_marker, 1)

    planned_accepted = insert_accepted(accepted, [row["card_rel"] for row in BATCH])
    if args.dry_run:
        print(f"dry-run passed: cards={len(card_texts)}, mapped_candidates={len(BATCH)}, direct_relation_candidates={sum(len(row['relations']) for row in BATCH)}")
        print(f"S4 registered={totals['registered_groups']}/{totals['new_groups']} groups, {totals['registered_members']}/{totals['new_candidates']} candidate maps; pending={totals['pending_groups']} groups/{totals['pending_members']} maps")
        print(f"direct pending={direct['groups']} groups/{direct['candidates']} candidate endpoints/{direct['members']} member maps; event={event_direct_groups} groups")
        print(f"manifest={len(manifest)}->{len(planned_manifest)}; relation table unchanged; enrichment unchanged; accepted paths unique")
        return 0

    for rel, card in card_texts.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(card, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    ACCEPTED.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {len(BATCH)} event groups registered; direct relation candidates remain pending S6")


if __name__ == "__main__":
    main()
