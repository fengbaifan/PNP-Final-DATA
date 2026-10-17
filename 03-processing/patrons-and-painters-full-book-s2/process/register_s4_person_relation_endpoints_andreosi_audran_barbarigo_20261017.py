from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s4-person-relation-endpoints-andreosi-audran-barbarigo-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
INDEX_DIR = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"

TARGETS = [
    {
        "candidate": "cand-0104",
        "group": "new-person:andreosi-francesco-01c295bada",
        "ku": "units/persons/francesco-andreosi",
        "card": "04-knowledge/units/persons/francesco-andreosi.md",
        "name_zh": "弗朗切斯科·安德雷奥西",
        "name_en": "Francesco Andreosi",
        "index_entry": "A.csv#105",
        "index_file": "A.csv",
        "index_name": "Andreosi, Francesco",
        "index_page": "366",
        "index_subentry": "statue of Antenor for Prà della Valle",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "source_span": "lines 17-18; print p. 366",
        "source_quote": "to be made by\nFrancesco Andreosi",
        "source_fragments": ["Memmo himself inaugurated the scheme", "Francesco Andreosi"],
        "location": "第15章；印刷页366；OCR L17-L18",
        "summary": "Haskell称，Memmo启动Prà della Valle雕像计划时，所提Antenor雕像预定由Francesco Andreosi制作；原文未确认雕像完工。",
        "description_zh": (
            "哈斯克尔在第15章记述，Memmo启动Prà della Valle的雕像计划时，提出由Francesco Andreosi制作Antenor雕像。"
            "此卡只记录书中点名的预定制作者身份；该段没有确认雕像完工，也没有提供可据以补写的个人传记信息。"
        ),
        "description_en": (
            "In Chapter 15, Haskell says that when Memmo inaugurated the Prà della Valle statue scheme, "
            "the offered statue of Antenor was to be made by Francesco Andreosi. This card records only the intended-maker "
            "identity named in the book; the passage does not confirm completion or provide biographical details."
        ),
        "related_context_zh": "雕像候选cand-10484仍为S3 undecided；Haskell表述的是预定制作角色，没有确认完成。",
        "related_context_en": "The statue candidate cand-10484 remains S3 undecided; Haskell reports an intended making role and does not confirm completion.",
        "relation_id": "st-chp15-p366-antenor-statue-made-by-andreosi",
        "other_candidate": "cand-10484",
        "other_decision": "undecided",
        "statement_subject": "cand-10484",
        "statement_object": "cand-0104",
        "statement_predicate": "statue_planned_to_be_made_by_andreosi",
        "statement_fragment": "to be made by",
    },
    {
        "candidate": "cand-0145",
        "group": "new-person:audran-benoit-418a187a46",
        "ku": "units/persons/benoit-audran",
        "card": "04-knowledge/units/persons/benoit-audran.md",
        "name_zh": "贝努瓦·奥德朗",
        "name_en": "Benoit Audran",
        "index_entry": "A.csv#146",
        "index_file": "A.csv",
        "index_name": "Audran, Benoit",
        "index_page": "370",
        "index_subentry": "",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "source_span": "line 62; print p. 370",
        "source_quote": "engraved-by Audran",
        "source_fragments": ["illustrations to Daphnis and Chloe", "engraved-by Audran"],
        "location": "第15章；印刷页370；OCR L62",
        "summary": "Haskell称，Querini书房中的Daphnis and Chloe插图由Régent Philippe d’Orléans绘制，并由Audran雕刻；索引将此处Audran列为Benoit Audran。",
        "description_zh": (
            "哈斯克尔在第15章称，Querini书房中的Daphnis and Chloe插图由Régent Philippe d’Orléans绘制，并由Audran雕刻；"
            "本书索引将该页的Audran列为Benoit Audran。此卡据此记录人物姓名及书中所述雕刻角色，不推定具体版本或单件印张。"
        ),
        "description_en": (
            "In Chapter 15, Haskell says that the Daphnis and Chloe illustrations in Querini’s study were drawn by the "
            "Régent Philippe d’Orléans and engraved by Audran; the book index identifies the Audran entry at that page as Benoit Audran. "
            "This card records the indexed person name and the engraving role reported in the book, without inferring a specific edition or impression."
        ),
        "related_context_zh": "插图组候选cand-10549仍为S3 undecided；书中没有确定版次或单件印张。",
        "related_context_en": "The illustration group candidate cand-10549 remains S3 undecided; the book identifies no edition or individual impression.",
        "relation_id": "st-chp15-p370-daphnis-chloe-prints-engraved-by-audran",
        "other_candidate": "cand-10549",
        "other_decision": "undecided",
        "statement_subject": "cand-10549",
        "statement_object": "cand-0145",
        "statement_predicate": "created_by",
        "statement_fragment": "engraved-by Audran",
    },
    {
        "candidate": "cand-0182",
        "group": "new-person:barbarigo-caterina-dd31afee3f",
        "ku": "units/persons/caterina-barbarigo",
        "card": "04-knowledge/units/persons/caterina-barbarigo.md",
        "name_zh": "卡特琳娜·巴尔巴里戈",
        "name_en": "Caterina Barbarigo",
        "index_entry": "B.csv#29",
        "index_file": "B.csv",
        "index_name": "Barbarigo, Caterina",
        "index_page": "333",
        "index_subentry": "",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "source_span": "lines 18-19; print p. 333",
        "source_quote": "Caterina Barbarigo in 1765 through her agent Gaspara Gozzi",
        "source_fragments": ["Caterina Barbarigo in 1765", "through her agent Gaspara Gozzi"],
        "location": "第13章；印刷页333；OCR L18-L19",
        "summary": "Haskell引述Caterina Barbarigo于1765年提出的小册子制作要求，并称要求经其所写的代理人Gaspara Gozzi传达；引文及代理人姓名未独立核验。",
        "description_zh": (
            "哈斯克尔在第13章引述Caterina Barbarigo于1765年对一本小册子制作提出的要求，并称这些要求经其所写的代理人Gaspara Gozzi传达。"
            "此处原话由哈斯克尔转引，未在本任务中独立核验；书中索引另列Gozzi, Gasparo并指向同页，该拼写与身份冲突仍未解决。"
            "本卡只记录可确定的Barbarigo人物身份和书内陈述，不据此消解Gozzi冲突或扩写传记。"
        ),
        "description_en": (
            "In Chapter 13, Haskell quotes specifications Caterina Barbarigo gave in 1765 for a pamphlet and says they were conveyed "
            "through an agent he names Gaspara Gozzi. The quoted wording was not independently checked for this task. The book index also "
            "lists Gozzi, Gasparo at the same page; that spelling and identity conflict remains unresolved. This card records the supported "
            "Barbarigo identity and the book’s account without resolving the Gozzi conflict or adding biography."
        ),
        "related_context_zh": "S2关系候选记载Haskell所述的传达角色；对象候选cand-9979（Gaspara Gozzi）仍与索引cand-1220（Gozzi, Gasparo）冲突，未建立正式关系。",
        "related_context_en": "The S2 relation candidate records the transmission role reported by Haskell; object candidate cand-9979 (Gaspara Gozzi) remains in conflict with index candidate cand-1220 (Gozzi, Gasparo), so no formal relation is established.",
        "relation_id": "st-chp13-p333-barbarigo-1765-pamphlet-instructions-through-gozzi",
        "other_candidate": "cand-9979",
        "other_decision": "conflict",
        "statement_subject": "cand-0182",
        "statement_object": "cand-9979",
        "statement_predicate": "conveyed_pamphlet_specifications_through_agent",
        "statement_fragment": "through her agent Gaspara Gozzi",
    },
]


def load_index_rows(file_name: str) -> list[dict[str, str]]:
    raw = (INDEX_DIR / file_name).read_bytes()
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw.decode("cp1252")
    return list(csv.DictReader(io.StringIO(content)))


def make_card(t: dict) -> str:
    book_source = {
        "citation": BOOK_CITATION,
        "location": t["location"],
        "sentence_summary": t["summary"],
        "original_quotes": [{"source_span": t["source_span"], "text": t["source_quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": t["source_file"],
            "source_span": t["source_span"],
        },
    }
    sources = [book_source]
    if t.get("index_entry"):
        sources.append({
            "citation": INDEX_CITATION,
            "location": f"全书索引 {t['index_entry']}",
            "sentence_summary": f"索引以“{t['index_name']}”列出人物，并指向印刷页{t['index_page']}。",
            "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}",
                "source_span": t["index_entry"],
            },
        })
    for item in t.get("extra_sources", []):
        sources.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": t["source_file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": t.get("process_ref", PROCESS_REF),
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body_link = f"[{t['location']}](../../../{t['source_file']})"
    index_link = (
        f"[索引 {t['index_entry']}](../../../02-sources/03-Index/03-2-Index-CSV/{t['index_file']})"
        if t.get("index_entry") else ""
    )
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']} {body_link} {index_link}

**English:** {t['description_en']} {body_link} {index_link}

### 本书相关内容

{t['related_context_zh']} {body_link}

{t['related_context_en']} {body_link}

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

S2关系候选 `{t['relation_id']}` 保留待S6审查；{t['related_context_zh']}

No formal relation is recorded. S2 relation candidate `{t['relation_id']}` remains for S6 review; {t['related_context_en']}
"""


def process_type_table(stats: dict[str, dict]) -> str:
    lines = [
        "| 类型 | 候选 | same | new（组/成员） | conflict | excluded | undecided | S4已登记（组/成员） | S4待登记（组/成员） |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    keys = (
        "total", "same_candidates", "new_groups", "new_candidates", "conflict", "excluded", "undecided",
        "registered_groups", "registered_members", "pending_groups", "pending_members",
    )
    totals = {key: sum(row[key] for row in stats.values()) for key in keys}
    for kind in sync.TYPE_ORDER:
        row = stats[kind]
        lines.append(
            f"| {kind} | {sync.fmt(row['total'])} | {sync.fmt(row['same_candidates'])} "
            f"| {sync.fmt(row['new_groups'])} / {sync.fmt(row['new_candidates'])} "
            f"| {sync.fmt(row['conflict'])} | {sync.fmt(row['excluded'])} | {sync.fmt(row['undecided'])} "
            f"| {sync.fmt(row['registered_groups'])} / {sync.fmt(row['registered_members'])} "
            f"| {sync.fmt(row['pending_groups'])} / {sync.fmt(row['pending_members'])} |"
        )
    lines.append(
        f"| **合计** | **{sync.fmt(totals['total'])}** | **{sync.fmt(totals['same_candidates'])}** "
        f"| **{sync.fmt(totals['new_groups'])} / {sync.fmt(totals['new_candidates'])}** "
        f"| **{sync.fmt(totals['conflict'])}** | **{sync.fmt(totals['excluded'])}** | **{sync.fmt(totals['undecided'])}** "
        f"| **{sync.fmt(totals['registered_groups'])} / {sync.fmt(totals['registered_members'])}** "
        f"| **{sync.fmt(totals['pending_groups'])} / {sync.fmt(totals['pending_members'])}** |"
    )
    return "\n".join(lines)


def replace_process_table(text: str, stats: dict[str, dict]) -> str:
    lines = text.splitlines()
    section = next(i for i, line in enumerate(lines) if line.startswith("## 按类型决定数"))
    start = next(i for i in range(section, len(lines)) if lines[i].startswith("| 类型 | 候选 | same |"))
    end = next(i for i in range(start, len(lines)) if not lines[i].strip())
    lines[start:end] = process_type_table(stats).splitlines()
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three source-backed S3 person groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_rows = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in alignment_rows}
    assert len(alignment_by_id) == len(alignment_rows) == len(candidate_by_id)
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    assert len(manifest_by_ku) == len(manifest)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }

    statements = [json.loads(line) for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}

    registration_states = []
    for t in TARGETS:
        cid = t["candidate"]
        assert cid in candidate_by_id and candidate_by_id[cid].get("suggested_type") == "person"
        alignment = alignment_by_id[cid]
        assert sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        assert candidate_by_id[cid].get("canonical_name") == t["index_name"]
        assert candidate_by_id[cid].get("index_entry_id") == t["index_entry"]
        group_members = [
            row["candidate_id"] for row in alignment_rows
            if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert group_members == [cid], (t["group"], group_members)

        index_hits = [
            row for row in load_index_rows(t["index_file"])
            if row.get("Main Entry") == t["index_name"] and row.get("Page Numbers") == t["index_page"]
        ]
        assert len(index_hits) == 1, (t["index_entry"], index_hits)
        source = (ROOT / t["source_file"]).read_text(encoding="utf-8-sig")
        assert all(fragment in source for fragment in t["source_fragments"]), t["candidate"]

        statement = statement_by_id[t["relation_id"]]
        assert statement.get("qualifiers", {}).get("relation_candidate") is True
        assert statement.get("subject_candidate_id") == t["statement_subject"]
        assert statement.get("object_candidate_id") == t["statement_object"]
        assert statement.get("predicate") == t["statement_predicate"]
        assert t["statement_fragment"] in statement.get("original_quote", "")
        assert alignment_by_id[t["other_candidate"]].get("decision") == t["other_decision"]

        existing_name = [
            row for row in manifest
            if row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold()
        ]
        assert len(existing_name) <= 1
        assert (t["ku"] in manifest_by_ku) == (len(existing_name) == 1)
        assert not existing_name or existing_name[0].get("ku_id") == t["ku"]
        card_path = ROOT / t["card"]
        aligned = alignment.get("ku_id", "") == t["ku"]
        listed = t["card"] in accepted_paths
        present = card_path.exists()
        assert aligned == listed == present or not any((aligned, listed, present)), (t["candidate"], aligned, listed, present)
        if aligned:
            assert alignment.get("decision") == "new"
        else:
            assert alignment.get("decision") == "new" and not alignment.get("ku_id")
            assert t["card"] not in accepted_paths and not present
        registration_states.append(aligned)

    if any(registration_states):
        assert all(registration_states), "partial batch registration detected; inspect before proceeding"
        changed_cards = [t for t in TARGETS if (ROOT / t["card"]).read_text(encoding="utf-8-sig") != make_card(t)]
        if changed_cards:
            if args.dry_run:
                print("registered mappings verified; generated card content differs and is ready for a controlled refresh:")
                for t in changed_cards:
                    print(t["card"])
                print("no files changed")
                return 0
            for t in changed_cards:
                (ROOT / t["card"]).write_text(make_card(t), encoding="utf-8-sig", newline="\n")
            print(f"refreshed generated card content for {len(changed_cards)} registered person KUs; S4 mappings unchanged.")
            return 0
        print("ALREADY REGISTERED: all three S3 person groups map to their expected person KUs; cards match the controlled template.")
        return 0

    planned_alignment = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        row = next(row for row in planned_alignment if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        row["ku_id"] = t["ku"]
        row["resolution_note"] += f" S4 registration: mapped {t['group']} to {t['ku']}."
        planned_manifest.append({
            "ku_id": t["ku"],
            "type": "person",
            "canonical_name": f"{t['name_zh']}（{t['name_en']}）",
            "name_en": t["name_en"],
            "source_task": TASK,
            "card_path": t["card"],
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] == 733 and totals["registered_members"] == 904
    assert totals["pending_groups"] == 4045 and totals["pending_members"] == 4059
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    process_text = replace_process_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        "### S4 person relation endpoints：Andreosi、Audran、Barbarigo（2026-10-17）\n\n"
        f"`cand-0104`、`cand-0145`、`cand-0182` 分属三个单候选 S3 身份组，分别登记为 "
        "[Francesco Andreosi](../../../04-knowledge/units/persons/francesco-andreosi.md)、"
        "[Benoit Audran](../../../04-knowledge/units/persons/benoit-audran.md)、"
        "[Caterina Barbarigo](../../../04-knowledge/units/persons/caterina-barbarigo.md)。"
        "Andreosi 只按Haskell所述预定制作角色记录，雕像候选 `cand-10484` 仍为 undecided；"
        "Audran 按第15章姓氏与同页索引全名对齐，插图组候选 `cand-10549` 仍为 undecided；"
        "Barbarigo 的1765年小册子要求为Haskell转引，代理人候选 `cand-9979` 与索引候选 `cand-1220` 仍有姓名/身份冲突。"
        "三个S2关系候选均保留待S6审查，未写入正式关系；Barbarigo引文及Gozzi身份未作外部核验。\n\n"
        f"本批登记3组/3条候选映射；累计S4已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条，KU={sync.fmt(len(planned_manifest))}。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text += (
        "\n\n### S4 人物身份组登记：Andreosi、Audran、Barbarigo（2026-10-17）\n\n"
        "`cand-0104` → `units/persons/francesco-andreosi`；只记录Haskell称为Antenor雕像预定制作者，"
        "作品候选仍待决。`cand-0145` → `units/persons/benoit-audran`；同页索引展开Audran为Benoit Audran，"
        "插图组候选仍待决。`cand-0182` → `units/persons/caterina-barbarigo`；其1765年要求为Haskell转引，"
        "Gaspara Gozzi 与索引 Gozzi, Gasparo 的身份冲突保留。三个S2关系候选未转为正式关系。\n\n"
        f"本批3组/3条映射；累计已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU={sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    for t in TARGETS:
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > t["card"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {t['card']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    assert len([line for line in planned_accepted.splitlines() if line.startswith("- 04-knowledge/units/")]) == len(planned_manifest)

    if args.dry_run:
        print("S4 person dry-run passed: three verified singleton identity groups; all candidate/index/source/statement checks passed.")
        for t in TARGETS:
            print(f"{t['candidate']} -> {t['ku']}; relation_candidate={t['relation_id']}; other_endpoint={t['other_candidate']}:{t['other_decision']}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}")
        print("formal_relations_added=0; enrichment_rows_changed=0; no files changed")
        return 0

    for t in TARGETS:
        (ROOT / t["card"]).write_text(make_card(t), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=3; candidate_mappings=3; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
