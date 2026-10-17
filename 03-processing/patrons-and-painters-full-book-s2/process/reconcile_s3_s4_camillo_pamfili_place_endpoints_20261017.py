from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as previous  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ENTITY_PATH = TABLES / "entity-candidates.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
PALACE_CANDIDATE = "cand-1816"
VILLA_CANDIDATE = "cand-1817"
OLD_GROUP = "sg3-place-pamfiliprincecamillonephewtopopeinnocentx"
VILLA_GROUP = "sg3-place-villa-doria-pamphilj"
PALACE_KU = "units/places/palazzo-doria-pamfili"
VILLA_KU = "units/places/villa-doria-pamphilj"
CARD_REL = f"04-knowledge/{VILLA_KU}.md"
PROCESS_REF = "S3-S4-cross-chapter-camillo-pamfili-places-2026-10-17"
PROCESS_ANCHOR = "s3-s4-camillo-pamfili-place-endpoints-20261017"
ROMA_URL = "https://www.turismoroma.it/en/node/1422"
SOVRAINTENDENZA_URL = "https://sovraintendenzaroma.it/node/2148"
DIRECT_STATEMENTS = {
    "st-chp6-p148-algardi-builds-camillo-villa",
    "st-chp6-p148-algardi-constructs-camillo-villa",
    "st-chp6-p148-algardi-constructs-papal-family-villa",
    "st-chp6-p148-camillo-fills-and-decorates-villa",
    "st-chp6-p148-camillo-decorates-villa",
    "st-chp6-p148-camillo-builds-palace",
}
VILLA_STATEMENTS = DIRECT_STATEMENTS - {"st-chp6-p148-camillo-builds-palace"}
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def normalized(text: str) -> str:
    return " ".join(text.split())


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows):
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8-sig",
        newline="\n",
    )


def card_text() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第6章，印刷页148；Markdown L34–35。",
            "sentence_summary": "Haskell称 Camillo Pamfili 在流放期间负责由 Algardi 建造一座罗马名园；原文未给该别墅正式名称。",
            "original_quotes": [
                {
                    "source_span": "lines 34–35; print p. 148",
                    "text": "During the course of it he had been responsible for the construction by Algardi of one of the most magnificent of all Roman villas.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "source_span": "lines 34–35; print p. 148",
            },
        },
        {
            "citation": (
                "Sovraintendenza Capitolina ai Beni Culturali, Villa Doria Pamphilj. "
                f"{SOVRAINTENDENZA_URL}. Accessed 2026-10-17."
            ),
            "location": "Dalle preesistenze alla nascita della villa Pamphilj, paragraphs 1–3.",
            "sentence_summary": (
                "Identifies Villa Doria Pamphilj as the Pamphilj family country residence; "
                "records Camillo Pamphilj's building work and the participation of Alessandro Algardi among artists active in the complex."
            ),
        },
    ]
    frontmatter = {
        "title": "罗马多利亚·潘菲利别墅（Villa Doria Pamphilj, Rome）",
        "name_en": "Villa Doria Pamphilj, Rome",
        "type": "place",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    book = "[第6章 p.148](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L34–35）"
    municipal = f"[罗马首都督察局：Villa Doria Pamphilj]({SOVRAINTENDENZA_URL})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡将 Haskell 第6章 p.148 未具名的罗马别墅与 Villa Doria Pamphilj 作身份对齐。原文称 Camillo Pamfili 在流放期间负责由 Algardi 建造一座罗马名园，但没有给出正式名称。罗马首都督察局将 Villa Doria Pamphilj 记为 Pamphilj 家族的乡间庄园，并记载 Camillo 的营建活动及 Algardi 等艺术家在园区内参与工程。名称、人物、艺术家和地点语境相合，足以支持 S3 身份判断；不将 Haskell 对 Algardi 的表述扩写为其独自设计整个庄园。{book} {municipal}

**English:** This card aligns the unnamed Roman villa in Haskell’s Chapter 6, p. 148, with Villa Doria Pamphilj. Haskell says that Camillo Pamfili was responsible during his exile for the construction by Algardi of a major Roman villa, without supplying its formal name. The Capitoline Superintendence identifies Villa Doria Pamphilj as the Pamphilj family’s country estate and records Camillo’s building activity and the participation of Algardi and other artists in the complex. The name, patron, artist, and place context support the S3 identity match; Haskell’s wording is not expanded into a claim that Algardi alone designed the whole estate.{book} {municipal}

### 名称与范围

- **名称：** Villa Doria Pamphilj；书中未给出该名称，采用罗马文化遗产记录中的地点名称。{municipal}
- **地点性质：** 罗马的历史乡间庄园。外部记录将 Casino del Bel Respiro 列为园区中的单体建筑；本卡不等同于该 Casino。{municipal}
- **对象边界：** 与第6章 p.148 随后所称、位于 Collegio Romano 对面的宫殿分别建模；该宫殿另映射至既有 Palazzo Doria-Pamfili KU。{book}

## 关系与证据

### 身份与外部链接

- {municipal}（用于比对地点名称、庄园范围及书内人物／艺术家语境；不是书内关系或原件事实核验。）

"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Correct the Camillo Pamfili palace/villa place identities and register Villa Doria Pamphilj."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }

    assert candidate_by_id[PALACE_CANDIDATE]["suggested_type"] == "place"
    assert candidate_by_id[PALACE_CANDIDATE]["index_entry_id"] == "P.csv#15"
    assert candidate_by_id[PALACE_CANDIDATE]["sub_entry"] == "palace"
    assert candidate_by_id[VILLA_CANDIDATE]["suggested_type"] == "place"
    assert candidate_by_id[VILLA_CANDIDATE]["index_entry_id"] == "P.csv#16"
    assert candidate_by_id[VILLA_CANDIDATE]["sub_entry"] == "villa built by Algardi"
    assert all(alignment_by_id[cid]["decision"] == "new" and not alignment_by_id[cid].get("ku_id")
               for cid in (PALACE_CANDIDATE, VILLA_CANDIDATE))
    assert all(sync.get_group(alignment_by_id[cid]["resolution_note"]) == OLD_GROUP
               for cid in (PALACE_CANDIDATE, VILLA_CANDIDATE))
    old_members = {
        row["candidate_id"]
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == OLD_GROUP
    }
    assert old_members == {PALACE_CANDIDATE, VILLA_CANDIDATE}, old_members
    assert any(row.get("ku_id") == PALACE_KU and row.get("type") == "place" for row in manifest)
    assert not any(row.get("ku_id") == VILLA_KU or row.get("card_path") == CARD_REL for row in manifest)
    assert not (ROOT / CARD_REL).exists() and CARD_REL not in accepted_lines
    assert PROCESS_ANCHOR not in process_text and "Camillo Pamfili 宫殿与别墅身份纠偏" not in result_text

    chapter = (ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md").read_text(encoding="utf-8-sig")
    norm_chapter = normalized(chapter)
    assert normalized("During the course of it he had been responsible for the construction by Algardi of one of the most magnificent of all Roman villas.") in norm_chapter
    assert normalized("set about building a palace for himself opposite the Collegio Romano") in norm_chapter
    index = (ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "P.csv").read_text(encoding="utf-8-sig")
    assert "villa built by Algardi" in index and "palace" in index

    statements = read_jsonl(STATEMENTS_PATH)
    statement_by_id = {row["statement_id"]: row for row in statements}
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in {PALACE_CANDIDATE, VILLA_CANDIDATE}
        or row.get("object_candidate_id") in {PALACE_CANDIDATE, VILLA_CANDIDATE}
    ]
    assert {row["statement_id"] for row in direct} == DIRECT_STATEMENTS
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is True for row in direct)
    assert len([row for row in direct if row.get("object_candidate_id") == VILLA_CANDIDATE]) == 5
    assert len([row for row in direct if row.get("object_candidate_id") == PALACE_CANDIDATE]) == 1

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    old_palace_note = planned_by_id[PALACE_CANDIDATE]["resolution_note"]
    old_villa_note = planned_by_id[VILLA_CANDIDATE]["resolution_note"]

    palace_row = planned_by_id[PALACE_CANDIDATE]
    palace_row["decision"] = "same"
    palace_row["ku_id"] = PALACE_KU
    palace_row["process_ref"] = PROCESS_REF
    palace_row["resolution_note"] = (
        f"source_ref=P.csv#15 (sub-entry: palace); existing_ku=04-knowledge/{PALACE_KU}.md; "
        f"S3 place correction {DATE}: same -> {PALACE_KU}. Haskell ch.6 p.148 distinguishes the palace "
        "built for Prince Camillo Pamfili opposite the Collegio Romano from the earlier villa built by Algardi. "
        "The existing Palazzo Doria-Pamfili place KU represents the same Rome palace: Roma Capitale, Turismo Roma, "
        "identifies the Via del Corso palace and records its transfer to Camillo Pamphilj in 1647 and work entrusted "
        f"to Antonio Del Grande ({ROMA_URL}; accessed {DATE}). The indexed palace is not the separate Piazza Navona "
        "Papal palace. prior_decision=new; prior_group={OLD_GROUP}; prior_resolution_note={old_palace_note}"
    )

    villa_row = planned_by_id[VILLA_CANDIDATE]
    villa_row["ku_id"] = VILLA_KU
    villa_row["process_ref"] = PROCESS_REF
    villa_row["resolution_note"] = (
        f"source_ref=P.csv#16 (sub-entry: villa built by Algardi); prior_s3_group_token={OLD_GROUP}; "
        f"group={VILLA_GROUP}; S3 place correction {DATE}: separate from cand-1816 palace. Haskell ch.6 p.148 "
        "says Camillo Pamfili was responsible for construction by Algardi of an unnamed Roman villa. "
        "The Capitoline Superintendence's Villa Doria Pamphilj record identifies the Pamphilj country estate, "
        "Camillo's building activity, and Algardi among artists active in the complex "
        f"({SOVRAINTENDENZA_URL}; accessed {DATE}). These place, patron, and artist anchors support the identity "
        "match to Villa Doria Pamphilj; this does not state Algardi alone designed the whole estate. "
        f"S4 registration: one new place KU {VILLA_KU}. prior_resolution_note={old_villa_note}"
    )
    assert sync.get_group(villa_row["resolution_note"]) == VILLA_GROUP

    planned_manifest = [dict(row) for row in manifest]
    planned_manifest.append({
        "ku_id": VILLA_KU,
        "type": "place",
        "canonical_name": "罗马多利亚·潘菲利别墅",
        "name_en": "Villa Doria Pamphilj, Rome",
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    next_id = max(
        (int(match.group(1)) for row in planned_alignment
         if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))),
        default=0,
    ) + 1
    external_rows_to_add = [
        {
            "alignment_id": f"aln-{next_id:04d}",
            "candidate_id": PALACE_CANDIDATE,
            "ku_id": PALACE_KU,
            "external_source": "Roma Capitale, Turismo Roma",
            "external_id": ROMA_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity comparison only: the official Roma Capitale tourism record identifies Palazzo Doria Pamphilj "
                "at Via del Corso and records its 1647 transfer to Camillo Pamphilj and later work by Antonio Del Grande. "
                "Compared with Haskell ch.6 p.148 and the existing place KU; this does not validate a formal relation."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 1:04d}",
            "candidate_id": VILLA_CANDIDATE,
            "ku_id": VILLA_KU,
            "external_source": "Sovraintendenza Capitolina ai Beni Culturali",
            "external_id": SOVRAINTENDENZA_URL,
            "decision": "new",
            "accessed_date": DATE,
            "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity comparison only: the official Villa Doria Pamphilj record describes the Pamphilj family country "
                "residence, Camillo Pamphilj's building activity, and artists including Alessandro Algardi. These identity "
                "anchors match Haskell ch.6 p.148; they do not establish that Algardi alone designed the estate or validate "
                "a formal relation."
            ),
        },
    ]
    planned_alignment.extend(external_rows_to_add)

    accepted_insert = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(accepted_insert, f"- {CARD_REL}")
    next_accepted = "\n".join(accepted_lines) + "\n"

    card = card_text()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)

    planned_statements = [dict(row) for row in statements]
    statement_plan = {row["statement_id"]: row for row in planned_statements}
    q1 = statement_plan["st-chp6-p148-algardi-builds-camillo-villa"]["qualifiers"]
    q1["qualification"] = (
        "The passage leaves the villa unnamed; S3 aligns its indexed referent with Villa Doria Pamphilj. "
        "This identity decision does not adjudicate the relation candidate."
    )
    q2 = statement_plan["st-chp6-p148-algardi-constructs-camillo-villa"]["qualifiers"]
    q2["relation_candidate_note"] = (
        "This separates the named builder from Camillo's responsibility for the project. S3 aligns cand-1817 "
        "with Villa Doria Pamphilj; the relation remains a candidate for S6."
    )
    q3 = statement_plan["st-chp6-p148-algardi-constructs-papal-family-villa"]["qualifiers"]
    q3["qualification"] = (
        "The villa is unnamed in the passage; S3 aligns the indexed Camillo-villa referent with Villa Doria Pamphilj. "
        "The separate report of a Pope-family commission remains source-qualified."
    )
    q3["relation_candidate_note"] = (
        "Haskell reports that Algardi was commissioned in construction of a Pope-family villa; S3 maps cand-1817 "
        "to Villa Doria Pamphilj, while the reported commission remains a relation candidate for S6."
    )
    q4 = statement_plan["st-chp6-p148-camillo-fills-and-decorates-villa"]["qualifiers"]
    q4["qualification"] = (
        "S3 aligns the villa reference with Villa Doria Pamphilj; its lavish decoration remains a separate statement."
    )
    q5 = statement_plan["st-chp6-p148-camillo-decorates-villa"]["qualifiers"]
    q5["relation_candidate_note"] = (
        "The villa now maps to Villa Doria Pamphilj via S3; S6 still must assess the relation candidate. "
        "The source does not identify the decorators or specific decoration."
    )
    assert all((statement_plan[sid].get("qualifiers") or {}).get("relation_candidate") is True for sid in DIRECT_STATEMENTS)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    alignment_row_pattern = re.compile(r"^\| \[全书对齐\]\(\.\./tables/alignment\.csv\) \|.*$", re.M)
    alignment_replacement = (
        f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(len(planned_alignment))} 条："
        f"{sync.fmt(len(candidates))} 条候选决定记录及 {sync.fmt(sum(bool(r.get('external_source')) for r in planned_alignment))} 条外部身份记录；"
        "候选决定数见下表 |"
    )
    next_result, count = alignment_row_pattern.subn(alignment_replacement, next_result, count=1)
    assert count == 1

    next_process = previous.refresh_process_type_table(process_text, stats)
    next_process += (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        "### S3/S4 place：Camillo Pamfili 的 palace 与 Algardi villa 分组纠偏（2026-10-17）\n\n"
        f"原组 {OLD_GROUP} 将 P.csv#15 的 palace（cand-1816）与 P.csv#16 的 villa built by Algardi（cand-1817）"
        "合为一个 place 身份，索引的共同父项 Camillo Pamfili 不能证明两座建筑为同一地点。第6章 p.148 先称流放期间"
        "Camillo 负责由 Algardi 建造一座罗马别墅，随后另称返罗马后为自己建造一座位于 Collegio Romano 对面的宫殿，"
        "明确区分 villa 与另建 palace。\n\n"
        f"cand-1816 改为 same → {PALACE_KU}，复用既有 Palazzo Doria-Pamfili 地点卡。Roma Capitale 的 Turismo Roma "
        "记录将该罗马宫殿定位于 Via del Corso，并记载其1647年归 Camillo Pamphilj，及其委托 Antonio Del Grande 的沿革"
        f"（{ROMA_URL}；访问于 {DATE}）；结合既有卡所载第1章宫殿身份与第6章位置描述，支持复用。旧 new 组及理由保存在 alignment 历史字段。\n\n"
        f"cand-1817 保持 new，但从共享旧组拆出到 {VILLA_GROUP}，并登记至 {VILLA_KU}。罗马首都督察局将 Villa Doria Pamphilj "
        "记为 Pamphilj 家族乡间庄园，记录 Camillo 的营建活动，并称 Algardi 等艺术家参与园区建设"
        f"（{SOVRAINTENDENZA_URL}；访问于 {DATE}）。该比对支持别墅身份，不把 Algardi 写成整个庄园的唯一设计者。"
        "外部身份记录分别附于两条 alignment 行；共组旧 token 和原理由均保留。\n\n"
        "更新 book-statements.jsonl 中五条 villa 端点的 S3 映射限定，保留原书陈述和候选谓词。"
        "五条 villa 关系候选及一条 palace 关系候选共六条均仍待 S6；relations.csv 未改写。\n\n"
        f"S4 新增一张地点卡 {CARD_REL}，cand-1817 映射该 KU；cand-1816 映射既有宫殿 KU。"
        "本次不添加正式关系，也未填入未经单条核验的 enrichment 字段。\n\n"
        f"更新后 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个既有 KU），"
        f"new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}组），"
        f"conflict={sync.fmt(totals['conflict'])}，excluded={sync.fmt(totals['excluded'])}，"
        f"undecided={sync.fmt(totals['undecided'])}；S4 已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条映射；KU={len(planned_manifest)}。"
    )
    next_result += (
        "\n\n### S3/S4 place：Camillo Pamfili palace 与 Villa Doria Pamphilj 分组纠偏（2026-10-17）\n\n"
        "cand-1816（P.csv#15, palace）复用既有 Palazzo Doria-Pamfili KU；cand-1817（P.csv#16, villa built by Algardi）"
        f"拆出为独立 new place 组 {VILLA_GROUP}，映射至 [Villa Doria Pamphilj](../units/places/villa-doria-pamphilj.md)。"
        "第6章 p.148 明确叙述先有 Algardi 建造的别墅、后另建 Collegio Romano 对面的宫殿；官方记录中的 Camillo、Algardi 与罗马乡间庄园语境支持身份区分。"
        "六条直接关系候选继续待 S6，无正式边新增。"
        f"当前 S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个既有 KU）、"
        f"new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}组）；"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU={len(planned_manifest)}。"
    )

    if args.dry_run:
        print(f"S3/S4 place reconciliation dry-run passed: {PALACE_CANDIDATE} -> same {PALACE_KU}")
        print(f"{VILLA_CANDIDATE} -> new group {VILLA_GROUP} -> {VILLA_KU}")
        print("Chapter 6 p.148 distinguishes the Algardi villa from the later palace opposite Collegio Romano.")
        print("two official external identity records attached; 6 relation candidates remain for S6")
        print(
            f"new groups={sync.fmt(totals['new_groups'])}; S4 registered="
            f"{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(planned_manifest)}; alignments={len(planned_alignment)}"
        )
        print("dry-run makes no changes")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text(next_accepted, encoding="utf-8-sig", newline="\n")
    write_jsonl(STATEMENTS_PATH, planned_statements)
    card_path = ROOT / CARD_REL
    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: same={sync.fmt(totals['same_candidates'])}, new="
        f"{sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"KU={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
