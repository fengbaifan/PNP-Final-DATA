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
ANCHOR = "s4-person-direct-endpoints-dolfin-douglas-erlach-ferdinand-ferrari-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-0926", "entry": "D.csv#28", "index_name": "Dolfin, Daniele (Archbishop of Udine)",
        "canonical_name": "Dolfin, Daniele (Archbishop of Udine)", "pages": "253n",
        "group": "new-person:a-daniele-dolfin-new-patriarch-daniele-dol-463e05f412",
        "ku": "units/persons/daniele-dolfin-archbishop-of-udine", "card": "04-knowledge/units/persons/daniele-dolfin-archbishop-of-udine.md",
        "name_zh": "丹尼埃莱·多尔芬（乌迪内总主教）", "name_en": "Daniele Dolfin (Archbishop of Udine)",
        "name_rows": [("索引名", "Dolfin, Daniele (Archbishop of Udine)", "S1（索引 D.csv#28）"), ("正文姓名形式", "Daniele Dolfin", "S2（第9章 p.253注1）")],
        "sources": [{
            "location": "第9章；印刷页253注1", "summary": "Haskell注释称1759年一位新任宗主教Daniele Dolfin（Dionisio的侄子）召回Tiepolo及其子Gian Domenico到Udine装饰主教座堂附近的Cappella della Purità。",
            "quote": "a new patriarch, Daniele Dolfin, nephew of Dionisio",
            "file": "02-sources/02-Markdown/09_CHP-9_intro.md", "span": "line 360; print p.253 n.1",
        }],
        "zh": "本卡按索引D.csv#28登记第9章p.253注1所称的Daniele Dolfin（Archbishop of Udine）。该人物与第9章p.252记载1729年去世的Daniele III及Daniele IV区分。",
        "en": "This card registers the Daniele Dolfin (Archbishop of Udine) in chapter 9, p.253 n.1 under index D.csv#28. He is distinct from Daniele III and Daniele IV, whom chapter 9, p.252 says died in 1729.",
        "context_zh": "Haskell称1759年新任宗主教Daniele Dolfin召回Tiepolo与Gian Domenico到Udine装饰Cappella della Purità，并称其为Dionisio的侄子。直接S2关系候选留待S6。",
        "context_en": "Haskell says the new patriarch Daniele Dolfin recalled Tiepolo and Gian Domenico to Udine in 1759 to decorate the Cappella della Purità and identifies him as Dionisio’s nephew. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp9-p253-note1-later-recall-and-chapel"],
        "endpoints": {"st-chp9-p253-note1-later-recall-and-chapel": ("cand-0926", "cand-8285", "recalled_tiepolo_and_gian_domenico_to_decorate_chapel_in_1759")},
    },
    {
        "primary": "cand-0946", "entry": "D.csv#48", "index_name": "Douglas, Hamilton, Marquis of",
        "canonical_name": "Douglas, Hamilton, Marquis of", "pages": "375n",
        "group": "new-person:douglas-hamilton-of-7bc05a28df", "ku": "units/persons/hamilton-marquis-of-douglas",
        "card": "04-knowledge/units/persons/hamilton-marquis-of-douglas.md",
        "name_zh": "汉密尔顿（道格拉斯侯爵）", "name_en": "Hamilton, Marquis of Douglas",
        "name_rows": [("索引名", "Douglas, Hamilton, Marquis of", "S1（索引 D.csv#48）"), ("正文称谓", "Hamilton, Marquis of Douglas", "S2（第16章 p.375注3）")],
        "sources": [{
            "location": "第16章；印刷页375注3", "summary": "Haskell注释将Hamilton, Marquis of Douglas列为与Sasso保持联系的人之一，并指向Epistolario Moschini中的书信；该书信未在本批独立查阅。",
            "quote": "Hamilton, Marquis of Douglas (1800-2)",
            "file": "02-sources/02-Markdown/16_CHP-16_intro.md", "span": "line 89; print p.375 n.3",
        }],
        "zh": "本卡按索引D.csv#48与第16章p.375注3登记Hamilton, Marquis of Douglas；原书未在该处提供个人全名。",
        "en": "This card registers Hamilton, Marquis of Douglas under index D.csv#48 and chapter 16, p.375 n.3; the book supplies no personal full name here.",
        "context_zh": "Haskell注释称其与Sasso保持联系，并将相关书信指向Epistolario Moschini；本批未独立查阅该书信。直接S2关系候选留待S6。",
        "context_en": "Haskell’s note says he was in touch with Sasso and points to letters in the Epistolario Moschini; those letters were not independently consulted in this batch. The direct S2 candidate remains for S6.",
        "relations": ["st-chp16-p375-douglas-in-touch-with-sasso"],
        "endpoints": {"st-chp16-p375-douglas-in-touch-with-sasso": ("cand-0946", "cand-2364", "was_in_touch_with")},
    },
    {
        "primary": "cand-0978", "entry": "E.csv#13", "index_name": "Erlach, Fischer von", "canonical_name": "Erlach, Fischer von", "pages": "201",
        "group": "new-person:erlach-fischer-von-a7b320e21b", "ku": "units/persons/fischer-von-erlach",
        "card": "04-knowledge/units/persons/fischer-von-erlach.md", "name_zh": "费舍尔·冯·埃尔拉赫", "name_en": "Fischer von Erlach",
        "name_rows": [("索引名", "Erlach, Fischer von", "S1（索引 E.csv#13）"), ("正文姓名形式", "Fischer von Erlach", "S2（第7章 p.201）")],
        "sources": [{
            "location": "第7章；印刷页201", "summary": "Haskell称Prince Eugene的冬宫由Fischer von Erlach开工。",
            "quote": "His Winter Palace begun by Fischer von Erlach",
            "file": "02-sources/02-Markdown/07_CHP-7_sec_v.md", "span": "line 46; print p.201",
        }],
        "zh": "本卡按索引E.csv#13与第7章p.201登记Fischer von Erlach；来源在此未提供其名字。",
        "en": "This card registers Fischer von Erlach under index E.csv#13 and chapter 7, p.201; the source gives no given name here.",
        "context_zh": "Haskell称Prince Eugene的冬宫由Fischer von Erlach开工。直接S2关系候选留待S6。",
        "context_en": "Haskell says Fischer von Erlach began work on Prince Eugene’s Winter Palace. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp7-p201-v-winter-palace-begun-by-fischer"],
        "endpoints": {"st-chp7-p201-v-winter-palace-begun-by-fischer": ("cand-7306", "cand-0978", "building_begun_by_architect")},
    },
    {
        "primary": "cand-1016", "entry": "F.csv#31", "index_name": "Ferdinand Maria, Elector of Bavaria", "canonical_name": "Ferdinand Maria, Elector of Bavaria", "pages": "193",
        "group": "new-person:bavaria-elector-ferdinand-maria-of-70b67fff1d", "ku": "units/persons/ferdinand-maria-elector-of-bavaria",
        "card": "04-knowledge/units/persons/ferdinand-maria-elector-of-bavaria.md", "name_zh": "费迪南德·玛丽亚（巴伐利亚选帝侯）", "name_en": "Ferdinand Maria, Elector of Bavaria",
        "name_rows": [("索引名", "Ferdinand Maria, Elector of Bavaria", "S1（索引 F.csv#31）"), ("正文姓名形式", "Elector Ferdinand Maria", "S2（第7章 p.193）")],
        "sources": [{
            "location": "第7章；印刷页193", "summary": "Haskell称选帝侯Ferdinand Maria于1652年与Adelaide Enrichetta of Savoy结婚。",
            "quote": "the Elector Ferdinand Maria married Adelaide Enrichetta of Savoy",
            "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md", "span": "lines 14-15; print p.193",
        }],
        "zh": "本卡按索引F.csv#31与第7章p.193登记巴伐利亚选帝侯Ferdinand Maria；此处不扩写原书未载的生平。",
        "en": "This card registers Ferdinand Maria, Elector of Bavaria, under index F.csv#31 and chapter 7, p.193; no biography beyond the source is added here.",
        "context_zh": "Haskell称Ferdinand Maria于1652年与Adelaide Enrichetta of Savoy结婚。直接S2关系候选留待S6。",
        "context_en": "Haskell says Ferdinand Maria married Adelaide Enrichetta of Savoy in 1652. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp7-p193-ferdinand-maria-marriage"],
        "endpoints": {"st-chp7-p193-ferdinand-maria-marriage": ("cand-1016", "cand-2380", "married")},
    },
    {
        "primary": "cand-1020", "entry": "F.csv#35", "index_name": "Ferrari, Giovanni", "canonical_name": "Ferrari, Giovanni", "pages": "367",
        "group": "new-person:ferrari-giovanni-b75250fc2c", "ku": "units/persons/giovanni-ferrari", "card": "04-knowledge/units/persons/giovanni-ferrari.md",
        "name_zh": "乔瓦尼·费拉里", "name_en": "Giovanni Ferrari",
        "name_rows": [("索引名", "Ferrari, Giovanni", "S1（索引 F.csv#35）"), ("正文姓名形式", "Giovanni Ferrari", "S2（第15章 p.367）")],
        "sources": [{
            "location": "第15章；印刷页367", "summary": "Haskell称Antonio Cappello委托Giovanni Ferrari制作自己的雕像，之后该雕像置于Prato della Valle。",
            "quote": "commissioned by Antonio Cappello from Giovanni Ferrari",
            "file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md", "span": "line 36; print p.367",
        }],
        "zh": "本卡按索引F.csv#35与第15章p.367登记Giovanni Ferrari；创作及委托语境限于Haskell此处记载。",
        "en": "This card registers Giovanni Ferrari under index F.csv#35 and chapter 15, p.367; the work and commission context is limited to Haskell’s passage.",
        "context_zh": "Haskell称Antonio Cappello委托Giovanni Ferrari制作自己的雕像，该雕像随后置于Prato della Valle。直接S2关系候选留待S6。",
        "context_en": "Haskell says Antonio Cappello commissioned Giovanni Ferrari to make a statue of himself, which later found a place in the Prato della Valle. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp15-p367-canova-statue-made-by-ferrari"],
        "endpoints": {"st-chp15-p367-canova-statue-made-by-ferrari": ("cand-11531", "cand-1020", "created_by")},
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
    with tempfile.TemporaryDirectory(prefix="pnp-s4-dolfin-douglas-erlach-ferdinand-ferrari-") as temp_root:
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
        print("ALREADY REGISTERED: five Dolfin/Douglas/Erlach/Bavaria/Ferrari person groups are present.")
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Dolfin、Douglas、Erlach、Ferdinand Maria、Ferrari（{DATE}）\n\n"
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
        f"\n\n### S4人物直接关系端点登记：Dolfin、Douglas、Erlach、Ferdinand Maria、Ferrari（{DATE}）\n\n"
        "登记Daniele Dolfin（Archbishop of Udine）、Hamilton, Marquis of Douglas、Fischer von Erlach、Ferdinand Maria（Elector of Bavaria）与Giovanni Ferrari五个S3 new身份组。"
        "对未载全名的对象保留来源称谓；cand-0926与1729年去世的Daniele III、IV区分。五条直接S2关系候选仍待S6逐条裁决。"
        f"本批无外部身份记录或正式关系；KU={len(planned_manifest)}，名称字段={len(additions)}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-dolfin-douglas-erlach-ferdinand-ferrari-") as temp_name:
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
