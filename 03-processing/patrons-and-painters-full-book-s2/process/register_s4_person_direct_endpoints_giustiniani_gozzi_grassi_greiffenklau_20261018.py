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
ANCHOR = "s4-person-direct-endpoints-giustiniani-gozzi-grassi-greiffenklau-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-1196", "entry": "G.csv#103", "index_name": "Giustiniani, Benedetto",
        "canonical_name": "Giustiniani, Benedetto", "pages": "29",
        "group": "new-person:benedetto-giustiniani-461ae63141", "ku": "units/persons/benedetto-giustiniani",
        "card": "04-knowledge/units/persons/benedetto-giustiniani.md",
        "name_zh": "贝内代托·朱斯蒂尼亚尼", "name_en": "Benedetto Giustiniani",
        "name_rows": [("索引名", "Giustiniani, Benedetto", "S1（索引 G.csv#103）"), ("正文姓名形式", "Benedetto", "S2（第2章 p.29）")],
        "sources": [{
            "location": "第2章；印刷页29", "summary": "Haskell称Benedetto与其兄弟曾是Caravaggio最热心的支持者之一；关系按原文范围保留。",
            "quote": "Benedetto had been among Caravaggio’s most enthusiastic supporters",
            "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md", "span": "line 100; print p.29",
        }],
        "zh": "本卡依据索引G.csv#103与第2章p.29登记Benedetto Giustiniani；本书提及其与兄弟对Caravaggio的支持。",
        "en": "This card registers Benedetto Giustiniani under index G.csv#103 and chapter 2, p.29; the book mentions his and his brother’s support for Caravaggio.",
        "context_zh": "Haskell称Benedetto与其兄弟曾是Caravaggio最热心的支持者之一；本卡不把兄弟的支持拆分或强化为独立 patronage 事实。直接S2关系候选留待S6。",
        "context_en": "Haskell says Benedetto and his brother had been among Caravaggio’s most enthusiastic supporters; the account is not split or strengthened into a separate patronage claim for Benedetto. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp2-seci-l95-106-benedetto-caravaggio-support"],
        "endpoints": {"st-chp2-seci-l95-106-benedetto-caravaggio-support": ("cand-1196", "cand-0544", "patronized")},
    },
    {
        "primary": "cand-1198", "entry": "G.csv#105", "index_name": "Giustiniani, Girolamo Ascanio",
        "canonical_name": "Giustiniani, Girolamo Ascanio", "pages": "370",
        "group": "new-person:ascanio-girolamo-giustiniani-d1dc8c0909", "ku": "units/persons/girolamo-ascanio-giustiniani",
        "card": "04-knowledge/units/persons/girolamo-ascanio-giustiniani.md",
        "name_zh": "吉罗拉莫·阿斯卡尼奥·朱斯蒂尼亚尼", "name_en": "Girolamo Ascanio Giustiniani",
        "name_rows": [("索引名", "Giustiniani, Girolamo Ascanio", "S1（索引 G.csv#105）"), ("正文姓名形式", "Girolamo Ascanio Giustiniani", "S2（第15章 p.370）")],
        "sources": [{
            "location": "第15章；印刷页370", "summary": "Haskell称Girolamo Ascanio Giustiniani是Querini最亲密的朋友，并称Altar of Friendship下的铭文献给他；铭文原文未转录。",
            "quote": "Girolamo Ascanio Giustiniani",
            "file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md", "span": "line 65; print p.370",
        }],
        "zh": "本卡依据索引G.csv#105与第15章p.370登记Girolamo Ascanio Giustiniani；本书称其为Querini最亲密的朋友。",
        "en": "This card registers Girolamo Ascanio Giustiniani under index G.csv#105 and chapter 15, p.370; the book identifies him as Querini’s closest friend.",
        "context_zh": "Haskell称Giustiniani为Querini最亲密的朋友，并称友谊祭坛下的铭文献给他；铭文文字未见转录。两条直接S2关系候选留待S6。",
        "context_en": "Haskell calls Giustiniani Querini’s closest friend and says an inscription below the Altar of Friendship was dedicated to him; the inscription is not transcribed. Both direct S2 relation candidates remain for S6.",
        "relations": ["st-chp15-p370-altar-inscription-dedicated-to-giustiniani", "st-chp15-p370-giustiniani-querinis-closest-friend"],
        "endpoints": {
            "st-chp15-p370-altar-inscription-dedicated-to-giustiniani": ("cand-10558", "cand-1198", "dedicated_to"),
            "st-chp15-p370-giustiniani-querinis-closest-friend": ("cand-2075", "cand-1198", "friend_of"),
        },
    },
    {
        "primary": "cand-1219", "entry": "G.csv#127", "index_name": "Gozzi, Carlo",
        "canonical_name": "Gozzi, Carlo", "pages": "256, 323",
        "group": "new-person:carlo-gozzi-b0baf536c1", "ku": "units/persons/carlo-gozzi",
        "card": "04-knowledge/units/persons/carlo-gozzi.md",
        "name_zh": "卡洛·戈齐", "name_en": "Carlo Gozzi",
        "name_rows": [("索引名", "Gozzi, Carlo", "S1（索引 G.csv#127）"), ("正文姓名形式", "Carlo Gozzi", "S2（第9章 p.256）")],
        "sources": [{
            "location": "第9章；印刷页256", "summary": "Haskell称一项反动宣言在Carlo Gozzi的某些写作中找到文学对应；未列出具体作品标题。",
            "quote": "some of the writings of Carlo Gozzi",
            "file": "02-sources/02-Markdown/09_CHP-9_intro.md", "span": "line 165; print p.256",
        }],
        "zh": "本卡依据索引G.csv#127与第9章p.256登记Carlo Gozzi；本书将其部分写作与一项反动宣言联系起来。",
        "en": "This card registers Carlo Gozzi under index G.csv#127 and chapter 9, p.256; the book relates some of his writings to a reactionary manifesto.",
        "context_zh": "Haskell把一项反动宣言解释为在Gozzi的某些写作中的文学对应；原文未指出具体作品，卡片不补题名。直接S2关系候选留待S6。",
        "context_en": "Haskell interprets a reactionary manifesto as finding a literary equivalent in some of Gozzi’s writings; no specific work is named, and none is added here. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp9-p256-gozzi-literary-equivalent"],
        "endpoints": {"st-chp9-p256-gozzi-literary-equivalent": ("cand-8408", "cand-1219", "literary_equivalent_in_writings_of_carlo_gozzi")},
    },
    {
        "primary": "cand-1226", "entry": "G.csv#134", "index_name": "Grassi, Orazio",
        "canonical_name": "Grassi, Orazio", "pages": "74",
        "group": "new-person:grassi-orazio-488025973f", "ku": "units/persons/orazio-grassi",
        "card": "04-knowledge/units/persons/orazio-grassi.md",
        "name_zh": "奥拉齐奥·格拉西", "name_en": "Orazio Grassi",
        "name_rows": [("索引名", "Grassi, Orazio", "S1（索引 G.csv#134）"), ("正文姓名形式", "Orazio Grassi", "S2（第3章 p.74）")],
        "sources": [{
            "location": "第3章；印刷页74", "summary": "Haskell称耶稣会士Orazio Grassi虽无建筑经验仍被任命负责S. Ignazio项目，并称他以与Galileo的争论著名。",
            "quote": "a Jesuit father, Orazio Grassi, of no architectural experience but celebrated for a controversy with Galileo",
            "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md", "span": "line 116; print p.74",
        }],
        "zh": "本卡依据索引G.csv#134与第3章p.74登记耶稣会士Orazio Grassi；建筑项目任命及Galileo争论均按本书记载。",
        "en": "This card registers the Jesuit Orazio Grassi under index G.csv#134 and chapter 3, p.74; the project appointment and Galileo controversy are recorded as stated in the book.",
        "context_zh": "Haskell称Grassi无建筑经验却获任S. Ignazio项目，并以其与Galileo的争论著名；本段未说明争论细节或任命者。两条直接S2关系候选留待S6。",
        "context_en": "Haskell says Grassi was appointed to the S. Ignazio project despite having no architectural experience and was known for a controversy with Galileo; the passage gives no details of the controversy or the appointing agent. Both direct S2 relation candidates remain for S6.",
        "relations": ["st-chp3-secii-l115-123-grassi-appointment", "st-chp3-secii-l115-123-grassi-galileo"],
        "endpoints": {
            "st-chp3-secii-l115-123-grassi-appointment": ("cand-1226", "cand-3967", "appointed_for_project"),
            "st-chp3-secii-l115-123-grassi-galileo": ("cand-1226", "cand-1105", "controversy_with"),
        },
    },
    {
        "primary": "cand-1230", "entry": "G.csv#140", "index_name": "Greiffenklau, Karl Philip von",
        "canonical_name": "Greiffenklau, Karl Philip von", "pages": "296",
        "group": "new-person:greiffenklau-karl-philip-von-775d76e75d", "ku": "units/persons/karl-philip-von-greiffenklau",
        "card": "04-knowledge/units/persons/karl-philip-von-greiffenklau.md",
        "name_zh": "卡尔·菲利普·冯·格赖芬克劳", "name_en": "Karl Philip von Greiffenklau",
        "name_rows": [("索引名", "Greiffenklau, Karl Philip von", "S1（索引 G.csv#140）"), ("正文姓名形式", "Karl Philip von Greiffenklau", "S2（第10章 p.296）")],
        "sources": [
            {
                "location": "第10章；印刷页296", "summary": "Haskell称Würzburg主教区在一段未具名继承时期后由Karl Philip von Greiffenklau接掌。",
                "quote": "after the death of Frederick Karl in 1746 and a short interval under his successor it was taken over by Karl Philip von Greiffenklau",
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md", "span": "line 320; print p.296",
            },
            {
                "location": "第10章；印刷页296", "summary": "Haskell称Karl Philip费力且耗费巨大地说服Tiepolo前往Würzburg装饰Kaisersaal。",
                "quote": "with great difficulty and at enormous expense finally persuaded Tiepolo to come to Wurzburg",
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md", "span": "lines 320-321; print p.296",
            },
        ],
        "zh": "本卡依据索引G.csv#140与第10章p.296登记Karl Philip von Greiffenklau；本书在Würzburg主教区及Tiepolo委托语境中提及他。",
        "en": "This card registers Karl Philip von Greiffenklau under index G.csv#140 and chapter 10, p.296; the book mentions him in connection with the Würzburg bishopric and Tiepolo’s commission.",
        "context_zh": "Haskell称Karl Philip在1746年后接掌Würzburg主教区，并费力说服Tiepolo赴Würzburg装饰Kaisersaal；前任后的短期继承者身份未明。两条直接S2关系候选留待S6。",
        "context_en": "Haskell says Karl Philip took over the Würzburg bishopric after 1746 and persuaded Tiepolo to decorate the Kaisersaal; the short-term successor before him remains unnamed. Both direct S2 relation candidates remain for S6.",
        "relations": ["st-chp10-p296-bishopric-transfer", "st-chp10-p296-karl-philip-persuades-tiepolo"],
        "endpoints": {
            "st-chp10-p296-bishopric-transfer": ("cand-9118", "cand-1230", "the_wurzburg_bishopric_passed_to_karl_philip_after_frederick_karl_and_a_short_successor_interval"),
            "st-chp10-p296-karl-philip-persuades-tiepolo": ("cand-1230", "cand-2569", "karl_philip_persuaded_tiepolo_to_come_to_wurzburg_and_decorate_the_kaisersaal"),
        },
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
    with tempfile.TemporaryDirectory(prefix="pnp-s4-giustiniani-gozzi-grassi-greiffenklau-") as temp_root:
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
        print("ALREADY REGISTERED: five Giustiniani/Gozzi/Grassi/Greiffenklau person groups are present.")
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Giustiniani、Gozzi、Grassi与Greiffenklau（{DATE}）\n\n"
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
        f"\n\n### S4人物直接关系端点登记：Giustiniani、Gozzi、Grassi与Greiffenklau（{DATE}）\n\n"
        "登记Benedetto Giustiniani、Girolamo Ascanio Giustiniani、Carlo Gozzi、Orazio Grassi与Karl Philip von Greiffenklau五个S3 new人物组。Giustiniani家族候选保持为不同人物；Gozzi作品未具名，Grassi任命者与Greiffenklau短期前任仍未识别。八条直接S2关系候选仍待S6逐条裁决。"
        f"本批无外部身份记录或正式关系；KU={len(planned_manifest)}，名称字段={len(additions)}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-giustiniani-gozzi-grassi-greiffenklau-") as temp_name:
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
