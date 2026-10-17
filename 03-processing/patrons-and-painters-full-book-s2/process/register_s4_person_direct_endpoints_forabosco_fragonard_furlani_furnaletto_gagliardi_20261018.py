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
ANCHOR = "s4-person-direct-endpoints-forabosco-fragonard-furlani-furnaletto-gagliardi-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-1052", "entry": "F.csv#67", "index_name": "Forabosco, Girolamo",
        "canonical_name": "Forabosco, Girolamo", "pages": "169",
        "group": "new-person:forabosco-girolamo-forabosco-girolamo-vene-196ebc5df6", "ku": "units/persons/girolamo-forabosco",
        "card": "04-knowledge/units/persons/girolamo-forabosco.md",
        "name_zh": "吉罗拉莫·福拉博斯科", "name_en": "Girolamo Forabosco",
        "name_rows": [("索引名", "Forabosco, Girolamo", "S1（索引 F.csv#67）"), ("正文姓名形式", "Girolamo Forabosco", "S2（第7章 p.169）")],
        "sources": [{
            "location": "第7章；印刷页169", "summary": "Haskell记载1671年Ruffo在Messina向威尼斯画家Girolamo Forabosco求画时遭到拒绝；随后转述Forabosco声望及欧洲王侯求画的说法。",
            "quote": "the Venetian Girolamo Forabosco",
            "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "span": "line 6; print p.169",
        }],
        "zh": "本卡依据索引F.csv#67与第7章p.169登记威尼斯画家Girolamo Forabosco；有关委托与声望的叙述限于Haskell此处转述。",
        "en": "This card registers the Venetian painter Girolamo Forabosco under index F.csv#67 and chapter 7, p.169; the account of commissions and reputation is limited to Haskell’s report here.",
        "context_zh": "Haskell称Ruffo于1671年在Messina向Forabosco求画而遭拒，并间接转述欧洲王侯常向他求画的说法。两条直接S2关系候选留待S6。",
        "context_en": "Haskell says Ruffo was refused when he sought a picture from Forabosco in Messina in 1671, and relays an indirect report that European princes frequently sought works from him. Both direct S2 relation candidates remain for S6.",
        "relations": ["st-chp7-p169-i08", "st-chp7-p169-i10"],
        "endpoints": {
            "st-chp7-p169-i08": ("cand-2297", "cand-1052", "sought_picture_from_and_was_snubbed_by"),
            "st-chp7-p169-i10": ("cand-1052", "cand-6598", "said_european_princes_implored_him_for_pictures"),
        },
    },
    {
        "primary": "cand-1063", "entry": "F.csv#78", "index_name": "Fragonard, Jean Honoré",
        "canonical_name": "Fragonard, Jean Honoré", "pages": "332",
        "group": "new-person:fragonard-honore-jean-f88a2369f3", "ku": "units/persons/jean-honore-fragonard",
        "card": "04-knowledge/units/persons/jean-honore-fragonard.md",
        "name_zh": "让-奥诺雷·弗拉戈纳尔", "name_en": "Jean Honoré Fragonard",
        "name_rows": [("索引名", "Fragonard, Jean Honoré", "S1（索引 F.csv#78）"), ("正文简称", "Fragonard", "S2（第13章 p.332；第9章 p.257）")],
        "sources": [
            {
                "location": "第13章；印刷页332", "summary": "Haskell称Marieschi于1741年的城市景观在多年后Fragonard访问Venice时吸引了他；未识别具体作品或访问日期。",
                "quote": "Marieschi’s views of 1741 which so appealed to Fragonard on his visit to Venice many years later",
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md", "span": "line 12; print p.332",
            },
            {
                "location": "第9章；印刷页257", "summary": "Haskell提出有理由相信Fragonard一类画家与部分鉴赏家可能区分bozzetti与完整装饰作品；保留其推测语气。",
                "quote": "painters like Fragonard and some connoisseurs of the time may have made the same distinction",
                "file": "02-sources/02-Markdown/09_CHP-9_intro.md", "span": "line 175; print p.257",
            },
        ],
        "zh": "本卡依据索引F.csv#78及第13章、第9章中的Fragonard称名登记Jean Honoré Fragonard；来源未将具体城市景观或推测性审美判断落实为新增作品或确定关系。",
        "en": "This card registers Jean Honoré Fragonard under index F.csv#78 and the Fragonard references in chapters 13 and 9; the sources do not identify a particular view or turn the qualified aesthetic suggestion into a new work or certain relation.",
        "context_zh": "第13章称Marieschi的1741年城市景观多年后吸引了到访Venice的Fragonard；第9章仅推测他与部分鉴赏家可能作出相同的bozzetti区分。两条直接S2关系候选留待S6。",
        "context_en": "Chapter 13 says Marieschi’s 1741 views appealed to Fragonard on a later visit to Venice; chapter 9 only suggests that he and some connoisseurs may have made the same distinction concerning bozzetti. Both direct S2 relation candidates remain for S6.",
        "relations": ["st-chp13-p332-marieschi-views-appealed-to-fragonard", "st-chp9-p257-fragonard-connoisseurs-may-share-distinction"],
        "endpoints": {
            "st-chp13-p332-marieschi-views-appealed-to-fragonard": ("cand-9977", "cand-1063", "views_appealed_to_fragonard_during_later_venice_visit"),
            "st-chp9-p257-fragonard-connoisseurs-may-share-distinction": ("cand-1063", "cand-8422", "fragonard_and_connoisseurs_may_have_shared_bozzetti_preference"),
        },
    },
    {
        "primary": "cand-1091", "entry": "F.csv#108", "index_name": "Furlani, Ventura",
        "canonical_name": "Furlani, Ventura", "pages": "362",
        "group": "new-person:furlani-ventura-5493c4c482", "ku": "units/persons/ventura-furlani",
        "card": "04-knowledge/units/persons/ventura-furlani.md",
        "name_zh": "文图拉·富尔拉尼", "name_en": "Ventura Furlani",
        "name_rows": [("索引名", "Furlani, Ventura", "S1（索引 F.csv#108）"), ("正文姓名形式", "Ventura Furlani", "S2（第15章 p.362）")],
        "sources": [{
            "location": "第15章；印刷页362", "summary": "Haskell称雕塑家Ventura Furlani受Farsetti雇用，为古代主要雕像制作石膏模；未列出具体雕像。",
            "quote": "the sculptor Ventura Furlani to make casts from the main statues of antiquity",
            "file": "02-sources/02-Markdown/15_CHP-15_sec_i.md", "span": "line 19; print p.362",
        }],
        "zh": "本卡依据索引F.csv#108与第15章p.362登记雕塑家Ventura Furlani；本书此处称其受雇制作古代雕像的模本。",
        "en": "This card registers the sculptor Ventura Furlani under index F.csv#108 and chapter 15, p.362; the passage says he was employed to make casts from ancient statues.",
        "context_zh": "Haskell称Farsetti雇用Furlani为古代主要雕像制作石膏模；本段未列具体对象。直接S2关系候选留待S6。",
        "context_en": "Haskell says Farsetti employed Furlani to make casts from the principal antique statues; the passage names no individual object. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp15-p362-furlani-employed-to-make-casts"],
        "endpoints": {"st-chp15-p362-furlani-employed-to-make-casts": ("cand-1002", "cand-1091", "employed_ventura_furlani_to_make_casts_from_main_statues_of_antiquity")},
    },
    {
        "primary": "cand-1092", "entry": "F.csv#109", "index_name": "Furnaletto, Lodovico",
        "canonical_name": "Furnaletto, Lodovico", "pages": "340",
        "group": "new-person:furnaletto-lodovico-fb8983e6c5", "ku": "units/persons/lodovico-furnaletto",
        "card": "04-knowledge/units/persons/lodovico-furnaletto.md",
        "name_zh": "洛多维科·富尔纳莱托", "name_en": "Lodovico Furnaletto",
        "name_rows": [("索引名", "Furnaletto, Lodovico", "S1（索引 F.csv#109）"), ("正文姓名形式", "Lodovico Furnaletto", "S2（第13章 p.340）")],
        "sources": [{
            "location": "第13章；印刷页340", "summary": "Haskell称Lodovico Furnaletto是版画商，称其在Ponte de’Baretteri经营三十余年，并于1766年委托Canaletto绘制12幅待由Brustolon雕刻的图画。",
            "quote": "Lodovico Furnaletto, who was a dealer in prints with no claims to practice the art himself",
            "file": "02-sources/02-Markdown/13_CHP-13_intro.md", "span": "lines 86-87; print p.340",
        }],
        "zh": "本卡依据索引F.csv#109与第13章p.340登记版画商Lodovico Furnaletto；本书称其未以艺术家身份从事创作。",
        "en": "This card registers the print dealer Lodovico Furnaletto under index F.csv#109 and chapter 13, p.340; the book says he did not claim to practise the art himself.",
        "context_zh": "Haskell称Furnaletto在Ponte de’Baretteri经营三十余年，1766年委托Canaletto绘制12幅图画交Brustolon雕刻；不由约数推算开业年份。两条直接S2关系候选留待S6。",
        "context_en": "Haskell says Furnaletto was established at Ponte de’Baretteri for more than thirty years and commissioned twelve Canaletto drawings in 1766 for Brustolon to engrave; no opening year is inferred from the approximate duration. Both direct S2 relation candidates remain for S6.",
        "relations": ["st-chp13-p340-furnaletto-commissioned-twelve-canaletto-drawings-in-1766", "st-chp13-p340-furnaletto-established-over-thirty-years-at-ponte-de-baretteri"],
        "endpoints": {
            "st-chp13-p340-furnaletto-commissioned-twelve-canaletto-drawings-in-1766": ("cand-1092", "cand-0503", "commissioned_twelve_canaletto_drawings_in_1766"),
            "st-chp13-p340-furnaletto-established-over-thirty-years-at-ponte-de-baretteri": ("cand-1092", "cand-10053", "established_at_ponte_de_baretteri_for_more_than_thirty_years"),
        },
    },
    {
        "primary": "cand-1098", "entry": "G.csv#5", "index_name": "Gagliardi, Bernardino",
        "canonical_name": "Gagliardi, Bernardino", "pages": "157",
        "group": "new-person:bernardino-gagliardi-bdbef465f5", "ku": "units/persons/bernardino-gagliardi",
        "card": "04-knowledge/units/persons/bernardino-gagliardi.md",
        "name_zh": "贝尔纳迪诺·加利亚尔迪", "name_en": "Bernardino Gagliardi",
        "name_rows": [("索引名", "Gagliardi, Bernardino", "S1（索引 G.csv#5）"), ("正文姓名形式", "Bernardino Gagliardi", "S2（第6章 p.157）")],
        "sources": [{
            "location": "第6章；印刷页157", "summary": "Haskell以Bernardino Gagliardi为例，指出其作品属于Antonio degli Effetti的收藏；未指明具体画作。",
            "quote": "Bernardino Gagliardi",
            "file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md", "span": "line 8; print p.157",
        }],
        "zh": "本卡依据索引G.csv#5与第6章p.157登记Bernardino Gagliardi；本书在Antonio degli Effetti收藏语境中以其为例。",
        "en": "This card registers Bernardino Gagliardi under index G.csv#5 and chapter 6, p.157; the book names him as an example in the context of Antonio degli Effetti’s collection.",
        "context_zh": "Haskell称Antonio degli Effetti收藏中包括Bernardino Gagliardi等画家的作品；此处未识别具体作品，原文仅举例并非完整名录。直接S2关系候选留待S6。",
        "context_en": "Haskell says Antonio degli Effetti’s collection included works by painters such as Bernardino Gagliardi; no individual work is identified and the example is not a complete roster. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp6-p157-collection-includes-work-by-gagliardi"],
        "endpoints": {"st-chp6-p157-collection-includes-work-by-gagliardi": ("cand-6389", "cand-1098", "collection_includes_work_by")},
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
    with tempfile.TemporaryDirectory(prefix="pnp-s4-forabosco-fragonard-furlani-furnaletto-gagliardi-") as temp_root:
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
    parser = argparse.ArgumentParser(description="Register five source-local person groups with direct S2 endpoints.")
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
        print("ALREADY REGISTERED: five Forabosco/Fragonard/Furlani/Furnaletto/Gagliardi person groups are present.")
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
    expected_name_fields = sum(len(target["name_rows"]) for target in TARGETS)
    assert cards_with_tables == count and len(additions) == expected_name_fields
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Forabosco、Fragonard、Furlani、Furnaletto与Gagliardi（{DATE}）\n\n"
    for target in TARGETS:
        process_text += (
            f"- {target['primary']}（{target['group']}）→ [{target['name_zh']}（{target['name_en']}）]"
            f"(../../../04-knowledge/units/persons/{target['ku'].split('/', 2)[2]}.md)。"
            f"索引{target['entry']}与所列章节页段构成书内身份依据；直接S2关系候选{','.join(target['relations'])}留待S6。"
            "来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。\n"
        )
    relation_count = sum(len(target["relations"]) for target in TARGETS)
    process_text += (
        f"\n本批登记{count}个S3 new人物组、{count}条候选映射和{len(additions)}条source_backed名称字段；"
        f"{relation_count}条直接S2关系候选留待S6。未添加外部身份标识、来源、候选或正式关系。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接关系端点登记：Forabosco、Fragonard、Furlani、Furnaletto与Gagliardi（{DATE}）\n\n"
        "登记Girolamo Forabosco、Jean Honoré Fragonard、Ventura Furlani、Lodovico Furnaletto与Bernardino Gagliardi五个S3 new人物组。Fragonard第9章p.257的推测语气及Furnaletto经营年限约数按来源保留；八条直接S2关系候选仍待S6逐条裁决。"
        f"本批无外部身份记录或正式关系；KU={len(planned_manifest)}，名称字段={len(additions)}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-forabosco-fragonard-furlani-furnaletto-gagliardi-") as temp_name:
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
