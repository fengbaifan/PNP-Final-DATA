from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import register_s4_person_endpoints_assereto_barelli_baretti_bartoli_basadonna_bassi_20261017 as helper  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
ENTITY = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ENRICHMENT = TABLES / "enrichment.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s4-person-direct-endpoints-colonna-concina-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-0806", "index_entry": "C.csv#336", "index_name": "Colonna, Filippo", "canonical_name": "Colonna, Filippo", "pages": "155",
        "group": "new-person:colonna-filippo-75b1b9b619", "ku": "units/persons/filippo-colonna",
        "card": "04-knowledge/units/persons/filippo-colonna.md", "name_zh": "菲利波·科隆纳", "name_en": "Filippo Colonna",
        "name_rows": [("索引名", "Colonna, Filippo", "S1（索引 C.csv#336）"), ("正文姓名形式", "Filippo", "S2（第6章 p.155）")],
        "sources": [{
            "location": "第6章；印刷页155", "summary": "Haskell称Colonna家族宫殿在本世纪上半叶由Filippo及其子Cardinal Girolamo大幅重建并装饰。",
            "quote": "largely rebuilt and decorated by Filippo and his son, Cardinal Girolamo",
            "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md", "source_span": "line 105; print p.155",
        }],
        "description_zh": "本卡按索引C.csv#336与第6章p.155登记Filippo Colonna；书内提及其子为Cardinal Girolamo，不与该子的人物KU合并。",
        "description_en": "This card registers Filippo Colonna under index C.csv#336 and chapter 6, p.155. The book names Cardinal Girolamo as his son; the two person KUs remain distinct.",
        "context_zh": "Haskell称Colonna家族宫殿在本世纪上半叶由Filippo和其子Cardinal Girolamo大幅重建并装饰；该宫殿未在此处具名。直接S2关系候选留待S6。",
        "context_en": "Haskell says the Colonna family palace was largely rebuilt and decorated by Filippo and his son Cardinal Girolamo in the first half of the century; the palace is not named here. The direct S2 relation candidate remains for S6.",
        "relation_ids": ["st-chp6-p155-colonna-palace-rebuilt"],
        "endpoints": {"st-chp6-p155-colonna-palace-rebuilt": ("cand-0815", "cand-0806", "rebuilt-and-decorated-by")},
    },
    {
        "primary": "cand-0808", "index_entry": "C.csv#338", "index_name": "Colonna, Prince Francesco", "canonical_name": "Colonna, Prince Francesco", "pages": "31",
        "group": "new-person:colonna-francesco-51fabc2402", "ku": "units/persons/prince-francesco-colonna",
        "card": "04-knowledge/units/persons/prince-francesco-colonna.md", "name_zh": "弗朗切斯科·科隆纳亲王", "name_en": "Prince Francesco Colonna",
        "name_rows": [("索引名", "Colonna, Prince Francesco", "S1（索引 C.csv#338）"), ("正文称谓", "Prince Francesco Colonna", "S2（第2章 p.31注5）")],
        "sources": [{
            "location": "第2章；印刷页31注5", "summary": "Haskell的注释称Prince Francesco Colonna宣布出售Roviano城堡的信由Abbate Michele Giustiniani刊出；所引书目未在本批独立查阅。",
            "quote": "Prince Francesco Colonna’s letter announcing the sale",
            "source_file": "02-sources/02-Markdown/02_CHP-2_sec_i.md", "source_span": "line 157; print p.31 n.5",
        }],
        "description_zh": "本卡按索引C.csv#338及第2章p.31注5登记Prince Francesco Colonna；仅保留原书使用的称号与姓名形式。",
        "description_en": "This card registers Prince Francesco Colonna under index C.csv#338 and chapter 2, p.31 n.5, retaining the title and name form used by the book.",
        "context_zh": "Haskell注释称其宣布出售Roviano城堡的信由Abbate Michele Giustiniani刊出；该注释仍是书内转引，相关直接S2候选留待S6。",
        "context_en": "Haskell’s note says his letter announcing the sale of Roviano Castle was published by Abbate Michele Giustiniani; this remains a report within Haskell’s note, and the direct S2 candidate remains for S6.",
        "relation_ids": ["st-chp2-seci-l124-157-colonna-sale-letter"],
        "endpoints": {"st-chp2-seci-l124-157-colonna-sale-letter": ("cand-0808", "cand-4387", "sale_letter_reported")},
    },
    {
        "primary": "cand-0810", "index_entry": "C.csv#340", "index_name": "Colonna, Don Giuliano", "canonical_name": "Colonna, Don Giuliano", "pages": "207n",
        "group": "new-person:colonna-giuliano-09b7a0c524", "ku": "units/persons/don-giuliano-colonna",
        "card": "04-knowledge/units/persons/don-giuliano-colonna.md", "name_zh": "唐·朱利亚诺·科隆纳", "name_en": "Don Giuliano Colonna",
        "name_rows": [("索引名", "Colonna, Don Giuliano", "S1（索引 C.csv#340）"), ("正文称谓", "Don Giuliano Colonna", "S2（第8章 p.207注1）")],
        "sources": [{
            "location": "第8章；印刷页207注1", "summary": "Haskell称Ferdinand van den Einden的女儿之一嫁给Don Giuliano Colonna；该女儿未具名。",
            "quote": "One of these married Don Giuliano Colonna",
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "source_span": "line 136; print p.207 n.1",
        }],
        "description_zh": "本卡按索引C.csv#340与第8章p.207注1登记Don Giuliano Colonna；本书未在该处给出其个人名或完整世系。",
        "description_en": "This card registers Don Giuliano Colonna under index C.csv#340 and chapter 8, p.207 n.1. The passage gives no personal given name or full genealogy.",
        "context_zh": "Haskell称Ferdinand van den Einden的女儿之一嫁给Don Giuliano Colonna；该女儿未具名。直接S2关系候选留待S6。",
        "context_en": "Haskell says one of Ferdinand van den Einden’s daughters married Don Giuliano Colonna; the daughter is unnamed. The direct S2 relation candidate remains for S6.",
        "relation_ids": ["st-chp8-p207-n1-daughter-married-giuliano-colonna"],
        "endpoints": {"st-chp8-p207-n1-daughter-married-giuliano-colonna": ("cand-7598", "cand-0810", "married")},
    },
    {
        "primary": "cand-0814", "index_entry": "C.csv#344", "index_name": "Colonna, Marc'Antonio", "canonical_name": "Colonna, Marc'Antonio", "pages": "156",
        "group": "new-person:antonio-colonna-marc-512265ff8f", "ku": "units/persons/marc-antonio-colonna",
        "card": "04-knowledge/units/persons/marc-antonio-colonna.md", "name_zh": "马尔坎托尼奥·科隆纳", "name_en": "Marc’Antonio Colonna",
        "name_rows": [("索引名", "Colonna, Marc'Antonio", "S1（索引 C.csv#344）"), ("正文姓名形式", "Marc’Antonio Colonna", "S2（第6章 p.156）")],
        "sources": [{
            "location": "第6章；印刷页156", "summary": "Haskell称壁画记录了Marc’Antonio Colonna在勒班陀战役中的功绩，并称其为相关人物的祖先。",
            "quote": "the exploits of his ancestor Marc’Antonio Colonna at the Battle of Lepanto",
            "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md", "source_span": "lines 117-118; print p.156",
        }],
        "description_zh": "本卡按索引C.csv#344及第6章p.156登记Marc’Antonio Colonna；本批不据姓名相似扩展其世系身份。",
        "description_en": "This card registers Marc’Antonio Colonna under index C.csv#344 and chapter 6, p.156; this batch does not extend his genealogy beyond the text.",
        "context_zh": "Haskell称相关壁画记录其祖先Marc’Antonio Colonna在勒班陀战役中的功绩；此处未将壁画进一步识别为独立作品。直接S2候选留待S6。",
        "context_en": "Haskell says the frescoes recorded the exploits of their ancestor Marc’Antonio Colonna at the Battle of Lepanto; the frescoes are not further identified as a distinct work here. The direct S2 candidate remains for S6.",
        "relation_ids": ["st-chp6-p156-fresco-cycle-depicts-marcantonio-at-lepanto"],
        "endpoints": {"st-chp6-p156-fresco-cycle-depicts-marcantonio-at-lepanto": ("cand-6345", "cand-0814", "depicts-marcantonio-colonna-at-lepanto")},
    },
    {
        "primary": "cand-0819", "index_entry": "C.csv#349", "index_name": "Concina, Padre Daniele", "canonical_name": "Concina, Padre Daniele", "pages": "271",
        "group": "new-person:concina-daniele-66b178ccc2", "ku": "units/persons/padre-daniele-concina",
        "card": "04-knowledge/units/persons/padre-daniele-concina.md", "name_zh": "达尼埃莱·孔奇纳神父", "name_en": "Padre Daniele Concina",
        "name_rows": [("索引名", "Concina, Padre Daniele", "S1（索引 C.csv#349）"), ("正文姓名形式", "Padre Daniele Concina", "S2（第9章 p.271）")],
        "sources": [{
            "location": "第9章；印刷页271", "summary": "Haskell称Padre Daniele Concina来自Gesuati及其毗邻修道院，曾猛烈抨击耶稣会，并较早提出取缔耶稣会。",
            "quote": "Padre Daniele Concina poured out a stream of invective against the Jesuits",
            "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md", "source_span": "line 46; print p.271",
        }],
        "description_zh": "本卡按索引C.csv#349与第9章p.271登记Padre Daniele Concina；所述身份与主张限于Haskell的本段记载。",
        "description_en": "This card registers Padre Daniele Concina under index C.csv#349 and chapter 9, p.271; the identity and claims recorded here are limited to Haskell’s passage.",
        "context_zh": "Haskell称Concina来自Gesuati及其毗邻修道院，曾猛烈抨击耶稣会并较早提出取缔该会。直接S2关系候选留待S6。",
        "context_en": "Haskell says Concina came from the Gesuati and its adjoining monastery, attacked the Jesuits, and was among the first to suggest suppressing the Society. The direct S2 relation candidate remains for S6.",
        "relation_ids": ["st-chp9-p271-concina-anti-jesuit-invective"],
        "endpoints": {"st-chp9-p271-concina-anti-jesuit-invective": ("cand-0819", "cand-1322", "concina_from_gesuati_and_adjoining_monastery_poured_invective_against_jesuits_and_was_among_first_to_suggest_suppression")},
    },
]


def make_card(target: dict) -> str:
    index_file = target["index_entry"].split("#", 1)[0]
    sources = [{
        "citation": INDEX_CITATION, "location": f"全书索引 {target['index_entry']}",
        "sentence_summary": f"索引以“{target['index_name']}”列出此人并定位至第{target['pages']}页。",
        "original_quotes": [{"source_span": target["index_entry"], "text": target["index_name"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": f"02-sources/03-Index/03-2-Index-CSV/{index_file}", "source_span": target["index_entry"]},
    }]
    for source in target["sources"]:
        sources.append({
            "citation": HASKELL_CITATION, "location": source["location"], "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["source_span"], "text": source["quote"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source["source_file"], "source_span": source["source_span"]},
        })
    fm = yaml.safe_dump({
        "title": f"{target['name_zh']}（{target['name_en']}）", "name_en": target["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": sources, "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    name_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in target["name_rows"])
    relations = ", ".join(target["relation_ids"])
    return (
        f"---\n{fm}\n---\n\n## 内容\n\n### 描述\n\n**中文：** {target['description_zh']}\n\n**English:** {target['description_en']}\n\n"
        f"### 名称\n\n| 字段 | 值 | 证据 |\n|---|---|---|\n{name_rows}\n\n"
        f"### 本书语境\n\n**中文：** {target['context_zh']} 直接S2关系候选{relations}保留待S6；本批不据身份登记裁定关系。\n\n"
        f"**English:** {target['context_en']} The direct S2 relation candidate {relations} remains for S6; this registration makes no relation decision.\n\n"
        "## 关系与证据\n\n### 关系记录\n\n当前没有正式关系。正文中的导航与线索不自动形成关系边。\n\n"
        f"**中文：** 直接S2关系候选{relations}保留待S6逐条裁决；本批不新增正式关系。\n\n"
        f"**English:** The direct S2 relation candidate {relations} remains for individual S6 review; this registration adds no formal relation.\n"
    )


def extract_card_fields(cards: dict[str, str]) -> tuple[list[dict], int]:
    from scripts import build_field_facts
    from scripts.build_field_facts import extract_records
    with tempfile.TemporaryDirectory(prefix="pnp-s4-colonna-concina-") as temp_root:
        temp_base = Path(temp_root)
        rows = []
        for target in TARGETS:
            temp_card = temp_base / target["card"]
            temp_card.parent.mkdir(parents=True, exist_ok=True)
            temp_card.write_text(cards[target["card"]], encoding="utf-8")
            rows.append({"ku_id": target["ku"], "card_path": target["card"]})
        previous_base = build_field_facts.BASE
        build_field_facts.BASE = temp_base
        try:
            additions, _registry, warnings, cards_with_tables = extract_records(rows)
            assert not warnings, warnings
            return additions, cards_with_tables
        finally:
            build_field_facts.BASE = previous_base


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        handle.write(content)
    try:
        tmp.replace(path)
    finally:
        if tmp.exists(): tmp.unlink()


def with_bom(text: str, original: bytes | None = None) -> bytes:
    raw = text.encode("utf-8")
    return b"\xef\xbb\xbf" + raw if original is None or original.startswith(b"\xef\xbb\xbf") else raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Register five source-local person groups with direct S2 relation endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    base = helper.base
    sync = base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    cards = {target["card"]: make_card(target) for target in TARGETS}
    card_paths = {target["card"]: ROOT / target["card"] for target in TARGETS}
    all_members = [target["primary"] for target in TARGETS]

    for target in TARGETS:
        candidate, alignment = candidate_by_id[target["primary"]], alignment_by_id[target["primary"]]
        assert candidate.get("suggested_type") == "person" and alignment.get("decision") == "new"
        assert candidate.get("canonical_name") == target["canonical_name"]
        assert candidate.get("index_entry_id") == target["index_entry"] and candidate.get("index_page_range") == target["pages"]
        assert base.sync.get_group(alignment.get("resolution_note", "")) == target["group"]
        if alignment.get("ku_id"):
            assert alignment.get("ku_id") == target["ku"]
        else:
            assert target["ku"] not in manifest_by_ku
            assert target["card"] not in accepted_paths and not card_paths[target["card"]].exists()
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and base.sync.get_group(row.get("resolution_note", "")) == target["group"]
        ]
        assert group_members == [target["primary"]], (target["group"], group_members)
        index_file, index_id = target["index_entry"].split("#", 1)
        index_lines = (ROOT / "02-sources/03-Index/03-2-Index-CSV" / index_file).read_text(encoding="utf-8-sig").splitlines()
        csv_row = next(csv.reader([index_lines[int(index_id) + 1]]))
        assert csv_row[0] == target["index_name"] and target["pages"] in csv_row[-1]
        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and (row.get("subject_candidate_id") == target["primary"] or row.get("object_candidate_id") == target["primary"])
        }
        assert direct == set(target["endpoints"]), (target["primary"], sorted(direct), sorted(target["endpoints"]))
        for statement_id, expected in target["endpoints"].items():
            row = statement_by_id[statement_id]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == expected
        for source in target["sources"]:
            source_text = (ROOT / source["source_file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", source["quote"]) in re.sub(r"\s+", " ", source_text), (target["primary"], source["source_span"])

    pending = [target for target in TARGETS if not alignment_by_id[target["primary"]].get("ku_id")]
    if not pending:
        for target in TARGETS:
            assert alignment_by_id[target["primary"]].get("ku_id") == target["ku"]
            assert card_paths[target["card"]].read_text(encoding="utf-8-sig") == cards[target["card"]]
            assert target["card"] in accepted_paths and manifest_by_ku[target["ku"]].get("card_path") == target["card"]
        print("ALREADY REGISTERED: five Colonna/Concina person groups and candidate mappings are present.")
        return 0
    assert len(pending) == len(TARGETS)

    before_stats = sync.summarize_by_type(candidates, alignments)
    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for target in TARGETS:
        row = next(item for item in planned_alignments if item.get("candidate_id") == target["primary"] and not item.get("external_source"))
        row["ku_id"] = target["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += (
            f" S4 registration: group {target['group']} -> {target['ku']}; "
            "source-local registration only; no external identity was added and direct relation candidates remain for S6."
        )
        planned_manifest.append({
            "ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"],
            "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"],
        })
        planned_accepted = helper.base.insert_accepted(planned_accepted, target["card"])
    planned_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    group_count, member_count = len(TARGETS), len(all_members)
    assert totals["registered_groups"] == before_totals["registered_groups"] + group_count
    assert totals["registered_members"] == before_totals["registered_members"] + member_count
    assert totals["pending_groups"] == before_totals["pending_groups"] - group_count
    assert totals["pending_members"] == before_totals["pending_members"] - member_count
    assert len(planned_manifest) == len(manifest) + group_count

    additions, cards_with_tables = extract_card_fields(cards)
    assert cards_with_tables == group_count and len(additions) == 2 * group_count
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    existing_enrichment = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) for row in existing_enrichment}
    existing_ids = {row.get("enrichment_id", "") for row in existing_enrichment}
    max_id = max((int(match.group(1)) for value in existing_ids if (match := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for number, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + number:05d}"
        assert (row["ku_id"], row["field"], row["value"], row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in existing_ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in additions) + "\n"

    process_text = base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Colonna与Concina（{DATE}）\n\n"
    for target in TARGETS:
        process_text += (
            f"- {target['primary']}（{target['group']}）→ [{target['name_zh']}（{target['name_en']}）]"
            f"(../../../04-knowledge/units/persons/{target['ku'].split('/', 2)[2]}.md)。"
            f"索引{target['index_entry']}与所列章节页段构成书内身份依据；直接S2关系候选{','.join(target['relation_ids'])}留待S6。"
            "本批不扩写来源未载的姓名或世系，不查验外部身份记录，也不新增正式关系。\n"
        )
    relation_count = sum(len(target["relation_ids"]) for target in TARGETS)
    process_text += (
        f"\n本批登记{group_count}个S3 new人物组、{member_count}条候选映射和{len(additions)}条source_backed名称字段；"
        f"{relation_count}条直接S2关系候选留待S6。未添加外部身份标识、来源、候选或正式关系。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接关系端点登记：Colonna与Concina（{DATE}）\n\n"
        "登记Filippo Colonna、Prince Francesco Colonna、Don Giuliano Colonna、Marc’Antonio Colonna与Padre Daniele Concina五个S3 new组；"
        "候选姓名和头衔按索引及章节原文保留，未据同姓合并或推定额外世系。五条直接S2关系候选仍待S6逐条裁决。"
        f"未查验外部身份记录、未新增正式关系；KU={len(planned_manifest)}，名称字段={len(additions)}。"
        f"详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-colonna-concina-") as temp_name:
        temp_dir = Path(temp_name)
        alignment_stage, manifest_stage = temp_dir / "alignment.csv", temp_dir / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: alignment_stage.read_bytes(), MANIFEST: manifest_stage.read_bytes(),
            ENRICHMENT: with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: with_bom(result_text + "\n", RESULT.read_bytes()),
        }
        for target in TARGETS:
            writes[ROOT / target["card"]] = with_bom(cards[target["card"]])

    if args.dry_run:
        print(f"S4 dry-run passed: groups={group_count}; candidate_mappings={member_count}; source_backed_name_fields={len(additions)}; direct_relation_candidates={relation_count}.")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
        print("external_identity_rows=0; formal_relations_added=0; candidate_backlog_changed=0; sources_registry_changed=0; no files changed")
        return 0

    originals = {path: path.read_bytes() if path.exists() else None for path in writes}
    try:
        for path, content in writes.items(): atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            if content is None:
                if path.exists(): path.unlink()
            else: atomic_write(path, content)
        raise
    print(f"applied: groups={group_count}; candidate_mappings={member_count}; name_fields={len(additions)}; relation_candidates={relation_count}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
