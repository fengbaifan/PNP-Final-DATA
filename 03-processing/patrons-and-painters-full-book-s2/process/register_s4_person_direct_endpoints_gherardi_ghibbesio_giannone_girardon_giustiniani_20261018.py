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
ANCHOR = "s4-person-direct-endpoints-gherardi-ghibbesio-giannone-girardon-giustiniani-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-1152", "entry": "G.csv#59", "index_name": "Gherardi, Antonio",
        "canonical_name": "Gherardi, Antonio", "pages": "161",
        "group": "new-person:antonio-gherardi-131ec7865c", "ku": "units/persons/antonio-gherardi",
        "card": "04-knowledge/units/persons/antonio-gherardi.md",
        "name_zh": "安东尼奥·盖拉尔迪", "name_en": "Antonio Gherardi",
        "name_rows": [("索引名", "Gherardi, Antonio", "S1（索引 G.csv#59）"), ("正文姓名形式", "Antonio Gherardi", "S2（第6章 p.161）")],
        "sources": [{
            "location": "第6章；印刷页161", "summary": "Haskell称Antonio Gherardi为Pierfrancesco Mola的学生，并称其是Venetian colour的爱好者。",
            "quote": "Antonio Gherardi, another special devotee of Venetian colour",
            "file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md", "span": "line 53; print p.161",
        }],
        "zh": "本卡依据索引G.csv#59与第6章p.161登记Antonio Gherardi；本书称其为Mola的学生和Venetian colour的爱好者。",
        "en": "This card registers Antonio Gherardi under index G.csv#59 and chapter 6, p.161; the book identifies him as Mola’s pupil and a devotee of Venetian colour.",
        "context_zh": "Haskell称Antonio Gherardi为Pierfrancesco Mola的学生，并称其是Venetian colour的爱好者；不与现有Pietro Ercole Gherardi卡仅凭姓氏合并。两条直接S2关系候选留待S6。",
        "context_en": "Haskell identifies Antonio Gherardi as a pupil of Pierfrancesco Mola and a devotee of Venetian colour; he is not merged with the existing Pietro Ercole Gherardi card on surname alone. Both direct S2 relation candidates remain for S6.",
        "relations": ["st-chp6-p161-gherardi-devotee-of-venetian-colour", "st-chp6-p161-gherardi-pupil-of-mola"],
        "endpoints": {
            "st-chp6-p161-gherardi-devotee-of-venetian-colour": ("cand-1152", "cand-6145", "devotee_of_venetian_colour"),
            "st-chp6-p161-gherardi-pupil-of-mola": ("cand-1152", "cand-1676", "pupil_of"),
        },
    },
    {
        "primary": "cand-1158", "entry": "G.csv#65", "index_name": "Ghibbesio, Jacopo",
        "canonical_name": "Ghibbesio, Jacopo", "pages": "94",
        "group": "new-person:ghibbesio-jacopo-d39f4a5655", "ku": "units/persons/jacopo-ghibbesio",
        "card": "04-knowledge/units/persons/jacopo-ghibbesio.md",
        "name_zh": "雅各布·吉贝西奥", "name_en": "Jacopo Ghibbesio",
        "name_rows": [("索引名", "Ghibbesio, Jacopo", "S1（索引 G.csv#65）"), ("正文姓名形式", "Jacopo Ghibbesio", "S2（第4章 p.94）")],
        "sources": [{
            "location": "第4章；印刷页94", "summary": "Haskell称Jacopo Ghibbesio是大学教授、父母为英国人，并拥有许多Pietro da Cortona的绘画与素描。",
            "quote": "Jacopo Ghibbesio, a university professor born of English parents",
            "file": "02-sources/02-Markdown/04_CHP-4_intro.md", "span": "line 7; print p.94",
        }],
        "zh": "本卡依据索引G.csv#65与第4章p.94登记Jacopo Ghibbesio；本书称其为大学教授并记其收藏Pietro da Cortona作品。",
        "en": "This card registers Jacopo Ghibbesio under index G.csv#65 and chapter 4, p.94; the book identifies him as a university professor and a collector of works by Pietro da Cortona.",
        "context_zh": "Haskell称Ghibbesio拥有许多Pietro da Cortona的绘画与素描；未列具体作品、题名、日期或数量。直接S2关系候选留待S6。",
        "context_en": "Haskell says Ghibbesio owned many paintings and drawings by Pietro da Cortona; no individual work, title, date, or exact count is given. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp4-intro-l3-8-ghibbesio-collection-contents"],
        "endpoints": {"st-chp4-intro-l3-8-ghibbesio-collection-contents": ("cand-11566", "cand-1158", "owned_by")},
    },
    {
        "primary": "cand-1164", "entry": "G.csv#71", "index_name": "Giannone, Pietro",
        "canonical_name": "Giannone, Pietro", "pages": "318",
        "group": "new-person:giannone-pietro-68879d63dd", "ku": "units/persons/pietro-giannone",
        "card": "04-knowledge/units/persons/pietro-giannone.md",
        "name_zh": "彼得罗·贾诺内", "name_en": "Pietro Giannone",
        "name_rows": [("索引名", "Giannone, Pietro", "S1（索引 G.csv#71）"), ("正文姓名形式", "Pietro Giannone", "S2（第10章 p.318）")],
        "sources": [{
            "location": "第10章；印刷页318", "summary": "Haskell称Pietro Giannone与其他非正统思想者迅速被逐出Venice共和国领土；本段未分别交代日期或驱逐细节。",
            "quote": "Pietro Giannone, Carlo Antonio Pilati, Giuseppe Baretti and other unorthodox thinkers were rapidly expelled from her territory",
            "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "span": "lines 139-140; print p.318",
        }],
        "zh": "本卡依据索引G.csv#71与第10章p.318登记Pietro Giannone；本书在思想者被逐出Venice共和国领土的叙述中提及他。",
        "en": "This card registers Pietro Giannone under index G.csv#71 and chapter 10, p.318; the book names him in its account of thinkers expelled from Venetian territory.",
        "context_zh": "Haskell称Giannone与其他非正统思想者被迅速逐出Venice共和国领土；来源没有提供其个人驱逐日期或独立细节。直接S2关系候选留待S6。",
        "context_en": "Haskell says Giannone and other unorthodox thinkers were rapidly expelled from Venetian territory; the passage gives no individual date or separate detail for his expulsion. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled"],
        "endpoints": {"st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled": ("cand-1164", "cand-8838", "expelled_from_territory")},
    },
    {
        "primary": "cand-1193", "entry": "G.csv#100", "index_name": "Girardon, François",
        "canonical_name": "Girardon, François", "pages": "188",
        "group": "new-person:francois-girardon-3ccbbdffed", "ku": "units/persons/francois-girardon",
        "card": "04-knowledge/units/persons/francois-girardon.md",
        "name_zh": "弗朗索瓦·吉拉尔东", "name_en": "François Girardon",
        "name_rows": [("索引名", "Girardon, François", "S1（索引 G.csv#100）"), ("正文姓名形式", "Girardon", "S2（第7章 p.188）")],
        "sources": [{
            "location": "第7章；印刷页188", "summary": "Haskell称Girardon后来改动了一尊雕像，其形象被称为Marcus Curtius；该名称指雕像，不是另一人物候选。",
            "quote": "Soon Girardon made the necessary alterations and the figure was called Marcus Curtius",
            "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "span": "line 240; print p.188",
        }],
        "zh": "本卡依据索引G.csv#100与第7章p.188登记François Girardon；本书在雕像改动的叙述中以姓氏指称他。",
        "en": "This card registers François Girardon under index G.csv#100 and chapter 7, p.188; the book refers to him by surname in its account of alterations to a statue.",
        "context_zh": "Haskell称Girardon改动了一尊雕像，之后该形象被称为Marcus Curtius；此名称属于雕像形象，不另建人物候选。直接S2关系候选留待S6。",
        "context_en": "Haskell says Girardon altered a statue and that the figure was subsequently called Marcus Curtius; this name refers to the statue, not a separate person candidate. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp7-p188-i31"],
        "endpoints": {"st-chp7-p188-i31": ("cand-1193", "cand-6917", "altered_statue_and_figure_called_marcus_curtius")},
    },
    {
        "primary": "cand-1195", "entry": "G.csv#102", "index_name": "Giustiniani, Andrea",
        "canonical_name": "Giustiniani, Andrea", "pages": "95",
        "group": "new-person:andrea-giustiniani-2bbf388a1b", "ku": "units/persons/andrea-giustiniani",
        "card": "04-knowledge/units/persons/andrea-giustiniani.md",
        "name_zh": "安德烈亚·朱斯蒂尼亚尼", "name_en": "Andrea Giustiniani",
        "name_rows": [("索引名", "Giustiniani, Andrea", "S1（索引 G.csv#102）"), ("正文姓名形式", "Andrea", "S2（第4章 p.95）")],
        "sources": [{
            "location": "第4章；印刷页95", "summary": "Haskell称Giustiniani的继承人Andrea在下一代将与Innocent X的侄女Maria Pamfili结婚；原文为计划性表述。",
            "quote": "the marriage of his heir Andrea to Maria Pamsili, niece of Innocent X",
            "file": "02-sources/02-Markdown/04_CHP-4_sec_i.md", "span": "line 12; print p.95",
        }],
        "zh": "本卡依据索引G.csv#102与第4章p.95登记Andrea Giustiniani；本书称其为Giustiniani的继承人，婚姻为当时的预期安排。",
        "en": "This card registers Andrea Giustiniani under index G.csv#102 and chapter 4, p.95; the book identifies him as Giustiniani’s heir and describes the marriage as prospective.",
        "context_zh": "Haskell称继承人Andrea原计划与Maria Pamfili结婚；该说法在本段是前瞻安排，不改写为已完成婚姻。直接S2关系候选留待S6。",
        "context_en": "Haskell says the heir Andrea was to marry Maria Pamfili; the passage presents this prospectively, not as a completed marriage. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp4-sec-i-l6-18-heir-marriage"],
        "endpoints": {"st-chp4-sec-i-l6-18-heir-marriage": ("cand-1195", "cand-5518", "marriage_reported")},
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
    with tempfile.TemporaryDirectory(prefix="pnp-s4-gherardi-ghibbesio-giannone-girardon-giustiniani-") as temp_root:
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
        print("ALREADY REGISTERED: five Gherardi/Ghibbesio/Giannone/Girardon/Giustiniani person groups are present.")
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Gherardi、Ghibbesio、Giannone、Girardon与Giustiniani（{DATE}）\n\n"
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
        f"\n\n### S4人物直接关系端点登记：Gherardi、Ghibbesio、Giannone、Girardon与Giustiniani（{DATE}）\n\n"
        "登记Antonio Gherardi、Jacopo Ghibbesio、Pietro Giannone、François Girardon与Andrea Giustiniani五个S3 new人物组。Gherardi与既有Pietro Ercole Gherardi不作姓氏推断合并；Giustiniani婚姻保留为来源中的预期安排。六条直接S2关系候选仍待S6逐条裁决。"
        f"本批无外部身份记录或正式关系；KU={len(planned_manifest)}，名称字段={len(additions)}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-gherardi-ghibbesio-giannone-girardon-giustiniani-") as temp_name:
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
