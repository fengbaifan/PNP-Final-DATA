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
ANCHOR = "s4-person-direct-endpoints-galli-garganego-genovesi-gerbault-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-1111", "entry": "G.csv#18", "index_name": "Galli, Agnolo",
        "canonical_name": "Galli, Agnolo", "pages": "105n",
        "group": "new-person:agnolo-galli-924c863641", "ku": "units/persons/agnolo-galli",
        "card": "04-knowledge/units/persons/agnolo-galli.md",
        "name_zh": "阿尼奥洛·加利", "name_en": "Agnolo Galli",
        "name_rows": [("索引名", "Galli, Agnolo", "S1（索引 G.csv#18）"), ("正文姓名形式", "Agnolo Galli", "S2（第4章 p.105注释）")],
        "sources": [{
            "location": "第4章；印刷页105注释", "summary": "Haskell注释称Cassiano 1629年11月3日致Agnolo Galli于Florence的信，并经Rinehart转述Cassiano为Galli购买绘画；信件和Rinehart第52页未在本批独立查阅。",
            "quote": "Agnolo Galli in Florence for whom Cassiano was buying pictures",
            "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md", "span": "line 255; print p.105 n.2",
        }],
        "zh": "本卡依据索引G.csv#18与第4章p.105注释登记Agnolo Galli；通信及购画信息限于Haskell经Rinehart所作转述。",
        "en": "This card registers Agnolo Galli under index G.csv#18 and chapter 4, p.105 n.2; the correspondence and picture-buying account are limited to Haskell’s report through Rinehart.",
        "context_zh": "Haskell注释称Cassiano为Galli购买绘画；原信及Rinehart所引第52页未在本批独立查阅，不据此推定完成购藏。直接S2关系候选留待S6。",
        "context_en": "Haskell’s note says Cassiano was buying pictures for Galli; the letter and Rinehart’s cited page 52 were not independently consulted in this batch, and no completed acquisition is inferred. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp4-sec-ii-notes-l255-259-fn255-galli-letter"],
        "endpoints": {"st-chp4-sec-ii-notes-l255-259-fn255-galli-letter": ("cand-2036", "cand-1111", "buying_pictures_for")},
    },
    {
        "primary": "cand-1112", "entry": "G.csv#19", "index_name": "Galli-Bibiena, Ferdinando",
        "canonical_name": "Galli-Bibiena, Ferdinando", "pages": "201",
        "group": "new-person:bibiena-ferdinando-galli-dc0b5ad40e", "ku": "units/persons/ferdinando-galli-bibiena",
        "card": "04-knowledge/units/persons/ferdinando-galli-bibiena.md",
        "name_zh": "费迪南多·加利-比比耶纳", "name_en": "Ferdinando Galli-Bibiena",
        "name_rows": [("索引名", "Galli-Bibiena, Ferdinando", "S1（索引 G.csv#19）"), ("正文姓名形式", "Ferdinando Galli-Bibiena", "S2（第7章 p.201；据版面校正OCR拼写）")],
        "sources": [{
            "location": "第7章；印刷页201", "summary": "Haskell称Ferdinando Galli-Bibiena制作了精彩的戏剧性演出；未指出具体演出、时间、场地或作品。",
            "quote": "Ferdinando Galli-Bibbiena produced marvellous theatrical spectacles",
            "file": "02-sources/02-Markdown/07_CHP-7_sec_v.md", "span": "line 54; print p.201",
        }],
        "zh": "本卡依据索引G.csv#19与第7章p.201登记Ferdinando Galli-Bibiena；本书称其制作戏剧性演出。",
        "en": "This card registers Ferdinando Galli-Bibiena under index G.csv#19 and chapter 7, p.201; the book says he produced theatrical spectacles.",
        "context_zh": "Haskell称Galli-Bibiena制作了精彩的戏剧性演出；个别演出、日期、场地或作品均未命名。直接S2关系候选留待S6。",
        "context_en": "Haskell says Galli-Bibiena produced marvellous theatrical spectacles; no individual production, date, venue, or work is named. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp7-p201-v-galli-bibiena-theatrical-spectacles"],
        "endpoints": {"st-chp7-p201-v-galli-bibiena-theatrical-spectacles": ("cand-1112", "cand-12345", "produced_theatrical_spectacles")},
    },
    {
        "primary": "cand-1114", "entry": "G.csv#21", "index_name": "Garganego, Girolamo",
        "canonical_name": "Garganego, Girolamo", "pages": "324n",
        "group": "new-person:garganego-girolamo-1498d7ac22", "ku": "units/persons/girolamo-garganego",
        "card": "04-knowledge/units/persons/girolamo-garganego.md",
        "name_zh": "吉罗拉莫·加尔加内戈", "name_en": "Girolamo Garganego",
        "name_rows": [("索引名", "Garganego, Girolamo", "S1（索引 G.csv#21）"), ("注释姓名形式", "Girolamo Garganego", "S2（第10章 p.324注3）")],
        "sources": [{
            "location": "第10章；印刷页324注3", "summary": "Haskell在注释中引用Girolamo Garganego的题献，并称其中Goldoni与Alessandro Longhi的比较很含糊；引文中的Longhi拼写已据页面校正。",
            "quote": "Girolamo Garganego",
            "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "span": "line 327; print p.324 n.3",
        }],
        "zh": "本卡依据索引G.csv#21与第10章p.324注3登记Girolamo Garganego；注释将相关比较归于其题献引文。",
        "en": "This card registers Girolamo Garganego under index G.csv#21 and chapter 10, p.324 n.3; the note attributes the relevant comparison to a quoted dedication by him.",
        "context_zh": "Haskell称Garganego题献中对Goldoni与Alessandro Longhi的比较很含糊；本批不据该比较推断其与其他人物的交往关系。直接S2关系候选留待S6。",
        "context_en": "Haskell calls Garganego’s dedication comparison of Goldoni and Alessandro Longhi very vague; no personal relationship is inferred from that comparison. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp10-p324-n3-dedication-compares-goldoni-and-longhi"],
        "endpoints": {"st-chp10-p324-n3-dedication-compares-goldoni-and-longhi": ("cand-1114", "cand-1424", "dedication-compares-goldoni-and-alessandro-longhi")},
    },
    {
        "primary": "cand-1133", "entry": "G.csv#40", "index_name": "Genovesi, Antonio",
        "canonical_name": "Genovesi, Antonio", "pages": "318",
        "group": "new-person:antonio-genovesi-3d7e20d618", "ku": "units/persons/antonio-genovesi",
        "card": "04-knowledge/units/persons/antonio-genovesi.md",
        "name_zh": "安东尼奥·杰诺维西", "name_en": "Antonio Genovesi",
        "name_rows": [("索引名", "Genovesi, Antonio", "S1（索引 G.csv#40）"), ("正文姓名形式", "Antonio Genovesi", "S2（第10章 p.318）")],
        "sources": [{
            "location": "第10章；印刷页318", "summary": "Haskell称Antonio Genovesi于1754年在Naples就任席位，并称其为欧洲首位政治经济学教授；未给出大学或席位的正式名称。",
            "quote": "Antonio Genovesi took up his chair in Naples as the first professor of political economy in Europe",
            "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "span": "line 136; print p.318",
        }],
        "zh": "本卡依据索引G.csv#40与第10章p.318登记Antonio Genovesi；职位与优先权表述按Haskell原文限定。",
        "en": "This card registers Antonio Genovesi under index G.csv#40 and chapter 10, p.318; the office and priority claim remain attributed to Haskell’s wording.",
        "context_zh": "Haskell称Genovesi于1754年在Naples就任政治经济学教授席位，并称其为欧洲首位；原文未列大学或正式席位名称。直接S2关系候选留待S6。",
        "context_en": "Haskell says Genovesi took up a chair in Naples in 1754 as Europe’s first professor of political economy; the institution and official chair title are not given. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp10-p318-genovesi-first-professor-of-political-economy"],
        "endpoints": {"st-chp10-p318-genovesi-first-professor-of-political-economy": ("cand-1133", "cand-8404", "took-chair-in-naples-in-1754-as-first-professor-in-europe")},
    },
    {
        "primary": "cand-1142", "entry": "G.csv#49", "index_name": "Gerbault, Francesco",
        "canonical_name": "Gerbault, Francesco", "pages": "336",
        "group": "new-person:francesco-gerbault-8e64d75c81", "ku": "units/persons/francesco-gerbault",
        "card": "04-knowledge/units/persons/francesco-gerbault.md",
        "name_zh": "弗朗切斯科·热尔博", "name_en": "Francesco Gerbault",
        "name_rows": [("索引名", "Gerbault, Francesco", "S1（索引 G.csv#49）"), ("正文姓名形式", "Francesco Gerbault", "S2（第13章 p.336）")],
        "sources": [{
            "location": "第13章；印刷页336", "summary": "Haskell称Francesco Gerbault是Louis XV的西班牙语和意大利语译员，并记其为《Orlando Furioso》豪华版计划发出订阅邀请；该版被作为计划讨论。",
            "quote": "Francesco Gerbault, Louis XV’s interpreter of Spanish and Italian",
            "file": "02-sources/02-Markdown/13_CHP-13_intro.md", "span": "line 42; print p.336",
        }],
        "zh": "本卡依据索引G.csv#49与第13章p.336登记Francesco Gerbault；其职务及订阅邀请均按本书记载。",
        "en": "This card registers Francesco Gerbault under index G.csv#49 and chapter 13, p.336; his role and subscription invitation are recorded as stated in the book.",
        "context_zh": "Haskell称Gerbault受托为《Orlando Furioso》豪华版计划发出订阅邀请；此处不将计划写成已出版作品。直接S2关系候选留待S6。",
        "context_en": "Haskell says Gerbault was to issue a subscription invitation for a projected sumptuous edition of Orlando Furioso; the project is not treated here as a published work. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp13-p336-gerbault-invited-orlando-subscriptions"],
        "endpoints": {"st-chp13-p336-gerbault-invited-orlando-subscriptions": ("cand-1142", "cand-9997", "issued_subscription_invitation_for_projected_edition")},
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
    with tempfile.TemporaryDirectory(prefix="pnp-s4-galli-garganego-genovesi-gerbault-") as temp_root:
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
        print("ALREADY REGISTERED: five Galli/Galli-Bibiena/Garganego/Genovesi/Gerbault person groups are present.")
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Galli、Galli-Bibiena、Garganego、Genovesi与Gerbault（{DATE}）\n\n"
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
        f"\n\n### S4人物直接关系端点登记：Galli、Galli-Bibiena、Garganego、Genovesi与Gerbault（{DATE}）\n\n"
        "登记Agnolo Galli、Ferdinando Galli-Bibiena、Girolamo Garganego、Antonio Genovesi与Francesco Gerbault五个S3 new人物组。购画及书信信息保留转引状态，Garganego的嵌套题献和Genovesi优先权说法均按来源归属表述；五条直接S2关系候选仍待S6逐条裁决。"
        f"本批无外部身份记录或正式关系；KU={len(planned_manifest)}，名称字段={len(additions)}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-galli-garganego-genovesi-gerbault-") as temp_name:
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
