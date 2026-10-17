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
ANCHOR = "s4-person-direct-endpoints-constable-contarini-correr-corsini-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-0822", "entry": "C.csv#352", "index_name": "Constable, John", "canonical_name": "Constable, John", "pages": "360",
        "group": "new-person:constable-john-425769ec08", "ku": "units/persons/john-constable", "card": "04-knowledge/units/persons/john-constable.md",
        "name_zh": "约翰·康斯特勃尔", "name_en": "John Constable",
        "name_rows": [("索引名", "Constable, John", "S1（索引 C.csv#352）"), ("正文姓名形式", "John Constable", "S2（第14章 p.360）")],
        "sources": [{
            "location": "第14章；印刷页360", "summary": "Haskell称Algarotti去世三十多年后，John Constable仍在漫长冬夜研读他的作品。",
            "quote": "John Constable whiled away the long winter evenings by studying his works",
            "file": "02-sources/02-Markdown/14_CHP-14_intro.md", "span": "line 145; print p.360",
        }],
        "zh": "本卡按索引C.csv#352与第14章p.360登记John Constable；此处只记录Haskell所述其阅读Algarotti作品的语境。",
        "en": "This card registers John Constable under index C.csv#352 and chapter 14, p.360, recording only Haskell’s account of his reading of Algarotti’s works.",
        "context_zh": "Haskell称Algarotti去世三十多年后，John Constable仍在漫长冬夜研读Algarotti的作品。直接S2关系候选留待S6。",
        "context_en": "Haskell says John Constable studied Algarotti’s works during long winter evenings more than thirty years after Algarotti’s death. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp14-p360-constable-studied-works"],
        "endpoints": {"st-chp14-p360-constable-studied-works": ("cand-0822", "cand-0050", "studied_algarottis_works_more_than_thirty_years_after_his_death")},
    },
    {
        "primary": "cand-0823", "entry": "C.csv#353", "index_name": "Contarini, Pietro", "canonical_name": "Contarini, Pietro", "pages": "32",
        "group": "new-person:contarini-pietro-8efdf34875", "ku": "units/persons/pietro-contarini", "card": "04-knowledge/units/persons/pietro-contarini.md",
        "name_zh": "彼得罗·孔塔里尼", "name_en": "Pietro Contarini",
        "name_rows": [("索引名", "Contarini, Pietro", "S1（索引 C.csv#353）"), ("正文姓名形式", "Pietro Contarini", "S2（第2章 p.32）")],
        "sources": [{
            "location": "第2章；印刷页32", "summary": "Haskell转引Pietro Contarini于1623年对教皇辖境及罗马古今盛况的描述，并称罗马如同世界商埠。",
            "quote": "wrote Pietro Contarini in 1623", "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md", "span": "line 15; print p.32",
        }],
        "zh": "本卡按索引C.csv#353与第2章p.32登记Pietro Contarini；1623年的描述作为Haskell转引保存。",
        "en": "This card registers Pietro Contarini under index C.csv#353 and chapter 2, p.32; the 1623 description is retained as quoted by Haskell.",
        "context_zh": "Haskell转引Pietro Contarini于1623年称罗马兼具古代遗存与当代营建，如同“世界的商埠”。直接S2候选留待S6。",
        "context_en": "Haskell quotes Pietro Contarini in 1623 describing Rome’s ancient remains and modern building as making it an “emporium of the Universe.” The direct S2 candidate remains for S6.",
        "relations": ["st-chp2-sec-ii-l10-18-contarini-state-and-rome-description"],
        "endpoints": {"st-chp2-sec-ii-l10-18-contarini-state-and-rome-description": ("cand-0823", "cand-3126", "reported_ambassadorial_characterization")},
    },
    {
        "primary": "cand-0856", "entry": "C.csv#386", "index_name": "Correr, Fra Francesco Antonio", "canonical_name": "Correr, Fra Francesco Antonio", "pages": "271",
        "group": "new-person:antonio-correr-fra-francesco-bae96cd018", "ku": "units/persons/fra-francesco-antonio-correr", "card": "04-knowledge/units/persons/fra-francesco-antonio-correr.md",
        "name_zh": "弗朗切斯科·安东尼奥·科雷尔修士", "name_en": "Fra Francesco Antonio Correr",
        "name_rows": [("索引名", "Correr, Fra Francesco Antonio", "S1（索引 C.csv#386）"), ("正文姓名形式", "Fra Francesco Antonio Correr", "S2（第9章 p.271）")],
        "sources": [{
            "location": "第9章；印刷页271", "summary": "Haskell称Capuchin修会的一名成员Fra Francesco Antonio Correr于1734年成为威尼斯宗主教。",
            "quote": "Fra Francesco Antonio Correr, was made Patriarch of Venice",
            "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md", "span": "line 48; print p.271",
        }],
        "zh": "本卡按索引C.csv#386与第9章p.271登记Fra Francesco Antonio Correr；本书称其为Capuchin修会成员。",
        "en": "This card registers Fra Francesco Antonio Correr under index C.csv#386 and chapter 9, p.271; the book identifies him as a Capuchin.",
        "context_zh": "Haskell称Correr于1734年成为威尼斯宗主教；该记录按本书表述保存。直接S2关系候选留待S6。",
        "context_en": "Haskell says Correr became Patriarch of Venice in 1734; this account is retained as stated in the book. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp9-p271-correr-patriarch-1734"],
        "endpoints": {"st-chp9-p271-correr-patriarch-1734": ("cand-0539", "cand-0856", "fra_francesco_antonio_correr_made_patriarch_of_venice_in_1734")},
    },
    {
        "primary": "cand-0861", "entry": "C.csv#391", "index_name": "Corsini, Marchese Filippo", "canonical_name": "Corsini, Marchese Filippo", "pages": "137n",
        "group": "new-person:corsini-filippo-097b8200c1", "ku": "units/persons/marchese-filippo-corsini", "card": "04-knowledge/units/persons/marchese-filippo-corsini.md",
        "name_zh": "菲利波·科西尼侯爵", "name_en": "Marchese Filippo Corsini",
        "name_rows": [("索引名", "Corsini, Marchese Filippo", "S1（索引 C.csv#391）"), ("正文称谓", "the Marchese Filippo Corsini", "S2（第5章 p.137注3）")],
        "sources": [{
            "location": "第5章；印刷页137注3", "summary": "Haskell称Florence的Marchese Filippo Corsini以拥有Jan Miel描绘席地坐者及幼童的画作为自豪；Haskell转引Baldinucci，该原书未在本批独立查阅。",
            "quote": "the Marchese Filippo Corsini was proud to own a painting by Jan Miel",
            "file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "span": "line 144; print p.137 n.3",
        }],
        "zh": "本卡按索引C.csv#391与第5章p.137注3登记Marchese Filippo Corsini；对Jan Miel画作的所有权信息保留为Haskell转引。",
        "en": "This card registers Marchese Filippo Corsini under index C.csv#391 and chapter 5, p.137 n.3; the ownership report about Jan Miel’s painting is retained as Haskell’s account.",
        "context_zh": "Haskell称Florence的Corsini侯爵拥有Jan Miel描绘一名男子与幼童的画，并转引Baldinucci；该引文来源未在本批独立查阅。直接S2关系候选留待S6。",
        "context_en": "Haskell says the Corsini marchese in Florence owned a Jan Miel painting of a man and child and cites Baldinucci; that cited source was not independently consulted in this batch. The direct S2 candidate remains for S6.",
        "relations": ["st-chp5-notes-l144-corsini-miel"],
        "endpoints": {"st-chp5-notes-l144-corsini-miel": ("cand-11943", "cand-0861", "owned_by")},
    },
    {
        "primary": "cand-0862", "entry": "C.csv#392", "index_name": "Corsini, Lorenzo (Pope Clement XII)", "canonical_name": "Corsini, Lorenzo (Pope Clement XII)", "pages": "317",
        "group": "new-person:clement-xii-corsini-lorenzo-b071aa0e12", "ku": "units/persons/lorenzo-corsini-pope-clement-xii", "card": "04-knowledge/units/persons/lorenzo-corsini-pope-clement-xii.md",
        "name_zh": "洛伦佐·科西尼（教宗克勉十二世）", "name_en": "Lorenzo Corsini (Pope Clement XII)",
        "name_rows": [("索引名", "Corsini, Lorenzo (Pope Clement XII)", "S1（索引 C.csv#392）"), ("正文称谓", "the Pope", "S2（第10章 p.317；索引指明为Clement XII）")],
        "sources": [{
            "location": "第10章；印刷页317", "summary": "Haskell称1737年教皇曾试图阻止在佛罗伦萨S. Croce教堂为Galileo建造陵墓；同页索引将该处归于Lorenzo Corsini，即Pope Clement XII。",
            "quote": "As late as 1737 the Pope tried to prevent the erection of a mausoleum to Galileo",
            "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "span": "line 130; print p.317",
        }],
        "zh": "本卡按索引C.csv#392将第10章p.317的the Pope映射为Lorenzo Corsini（Pope Clement XII）；不与另有其人的Clement XIII混同。",
        "en": "Under index C.csv#392, this card maps the Pope in chapter 10, p.317 to Lorenzo Corsini (Pope Clement XII), distinct from the separate person Clement XIII.",
        "context_zh": "Haskell称1737年教皇试图阻止在佛罗伦萨S. Croce教堂为Galileo建造陵墓。身份名称依同页索引C.csv#392；直接S2候选留待S6。",
        "context_en": "Haskell says that in 1737 the Pope tried to prevent a mausoleum for Galileo at S. Croce in Florence. The index C.csv#392 supplies the identity; the direct S2 candidate remains for S6.",
        "relations": ["st-chp10-p317-pope-attempted-to-prevent-galileo-mausoleum"],
        "endpoints": {"st-chp10-p317-pope-attempted-to-prevent-galileo-mausoleum": ("cand-0862", "cand-9703", "tried-to-prevent-erection-in-1737")},
    },
]


def make_card(target: dict) -> str:
    index_file = target["entry"].split("#", 1)[0]
    sources = [{
        "citation": INDEX_CITATION, "location": f"全书索引 {target['entry']}",
        "sentence_summary": f"索引以“{target['index_name']}”列出此人并定位至第{target['pages']}页。",
        "original_quotes": [{"source_span": target["entry"], "text": target["index_name"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": f"02-sources/03-Index/03-2-Index-CSV/{index_file}", "source_span": target["entry"]},
    }]
    for source in target["sources"]:
        sources.append({
            "citation": HASKELL_CITATION, "location": source["location"], "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["span"], "text": source["quote"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source["file"], "source_span": source["span"]},
        })
    fm = yaml.safe_dump({
        "title": f"{target['name_zh']}（{target['name_en']}）", "name_en": target["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": sources, "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    name_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in target["name_rows"])
    relations = ", ".join(target["relations"])
    return (
        f"---\n{fm}\n---\n\n## 内容\n\n### 描述\n\n**中文：** {target['zh']}\n\n**English:** {target['en']}\n\n"
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
    with tempfile.TemporaryDirectory(prefix="pnp-s4-constable-contarini-correr-corsini-") as temp_root:
        temp_base = Path(temp_root)
        rows = []
        for target in TARGETS:
            card = temp_base / target["card"]
            card.parent.mkdir(parents=True, exist_ok=True)
            card.write_text(cards[target["card"]], encoding="utf-8")
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
    parser = argparse.ArgumentParser(description="Register five source-local person groups with direct S2 relation candidates.")
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

    for target in TARGETS:
        candidate, alignment = candidate_by_id[target["primary"]], alignment_by_id[target["primary"]]
        assert candidate.get("suggested_type") == "person" and alignment.get("decision") == "new"
        assert candidate.get("canonical_name") == target["canonical_name"]
        assert candidate.get("index_entry_id") == target["entry"] and candidate.get("index_page_range") == target["pages"]
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
        index_file, index_id = target["entry"].split("#", 1)
        index_lines = (ROOT / "02-sources/03-Index/03-2-Index-CSV" / index_file).read_text(encoding="utf-8-sig").splitlines()
        index_row = next(csv.reader([index_lines[int(index_id) + 1]]))
        assert index_row[0] == target["index_name"] and target["pages"] in index_row[-1]
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
            text = (ROOT / source["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", source["quote"]) in re.sub(r"\s+", " ", text), (target["primary"], source["span"])

    pending = [target for target in TARGETS if not alignment_by_id[target["primary"]].get("ku_id")]
    if not pending:
        for target in TARGETS:
            assert alignment_by_id[target["primary"]].get("ku_id") == target["ku"]
            assert card_paths[target["card"]].read_text(encoding="utf-8-sig") == cards[target["card"]]
            assert target["card"] in accepted_paths and manifest_by_ku[target["ku"]].get("card_path") == target["card"]
        print("ALREADY REGISTERED: five Constable/Contarini/Correr/Corsini person groups and mappings are present.")
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
        planned_manifest.append({"ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"], "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"]})
        planned_accepted = helper.base.insert_accepted(planned_accepted, target["card"])
    planned_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    count = len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + count
    assert totals["registered_members"] == before_totals["registered_members"] + count
    assert totals["pending_groups"] == before_totals["pending_groups"] - count
    assert totals["pending_members"] == before_totals["pending_members"] - count
    assert len(planned_manifest) == len(manifest) + count

    additions, cards_with_tables = extract_card_fields(cards)
    assert cards_with_tables == count and len(additions) == 2 * count
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Constable、Contarini、Correr、Corsini（{DATE}）\n\n"
    for target in TARGETS:
        process_text += (
            f"- {target['primary']}（{target['group']}）→ [{target['name_zh']}（{target['name_en']}）]"
            f"(../../../04-knowledge/units/persons/{target['ku'].split('/', 2)[2]}.md)。"
            f"索引{target['entry']}与正文页段构成书内身份依据；直接S2关系候选{','.join(target['relations'])}留待S6。"
            "本批不查验外部身份记录，不新增正式关系；Haskell转引的Baldinucci来源未独立查阅。\n"
        )
    relation_count = sum(len(target["relations"]) for target in TARGETS)
    process_text += (
        f"\n本批登记{count}个S3 new人物组、{count}条候选映射及{len(additions)}条source_backed名称字段；"
        f"{relation_count}条直接S2关系候选留待S6。未添加外部身份标识、候选、来源或正式关系。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接关系端点登记：Constable、Contarini、Correr、Corsini（{DATE}）\n\n"
        "登记John Constable、Pietro Contarini、Fra Francesco Antonio Correr、Marchese Filippo Corsini与Lorenzo Corsini（Pope Clement XII）五个S3 new身份组。"
        "名称、称号和书内语境以索引及正文为准；不扩写外部生平。五条直接S2关系候选继续待S6逐条裁决；Haskell转引的Baldinucci来源未在本批独立查阅。"
        f"未新增外部身份记录或正式关系；KU={len(planned_manifest)}，名称字段={len(additions)}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-constable-contarini-correr-corsini-") as temp_name:
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
        for target in TARGETS: writes[ROOT / target["card"]] = with_bom(cards[target["card"]])

    if args.dry_run:
        print(f"S4 dry-run passed: groups={count}; candidate_mappings={count}; source_backed_name_fields={len(additions)}; direct_relation_candidates={relation_count}.")
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
    print(f"applied: groups={count}; candidate_mappings={count}; name_fields={len(additions)}; relation_candidates={relation_count}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
