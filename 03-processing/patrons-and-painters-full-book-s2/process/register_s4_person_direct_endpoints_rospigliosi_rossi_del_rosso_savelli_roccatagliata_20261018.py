from __future__ import annotations

import argparse
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
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s4-person-direct-endpoints-rospigliosi-rossi-del-rosso-savelli-roccatagliata-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-2262", "members": ["cand-2262"], "index_entry": "Q-R.csv#190",
        "canonical_name": "Rospigliosi, Camillo", "group": "new-person:camillo-rospigliosi-fb5ca73bce",
        "ku": "units/persons/camillo-rospigliosi", "card": "04-knowledge/units/persons/camillo-rospigliosi.md",
        "name_zh": "卡米洛·罗什皮廖西", "name_en": "Camillo Rospigliosi",
        "name_rows": [
            ("索引名", "Rospigliosi, Camillo", "S1（索引 Q-R.csv#190）"),
            ("正文姓名形式", "Camillo Rospigliosi", "S2（第5章 p.127）"),
        ],
        "sources": [{
            "location": "第5章；印刷页127",
            "summary": "Haskell称Camillo Rospigliosi是教皇的兄弟；他与四个儿子刚被接纳为Compagnia della Misericordia的新成员。",
            "quote": "Camillo Rospigliosi", "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
            "source_span": "line 81; print p.127",
        }],
        "description_zh": "本卡按全书索引和第5章p.127登记Camillo Rospigliosi；本批只保留书内姓名和身份锚点，不将四名未具名儿子扩写为具名实体。",
        "description_en": "This card registers Camillo Rospigliosi under the index and chapter 5, p.127 forms. It preserves the book-based name and identity anchor and does not expand the four unnamed sons into named entities.",
        "context_zh": "Haskell称Camillo为教皇的兄弟，并称他与四个儿子刚被接纳为Compagnia della Misericordia的新成员。相关S2关系仍待S6。",
        "context_en": "Haskell identifies Camillo as the Pope’s brother and says he and his four sons had just been admitted to the Compagnia della Misericordia. The related S2 candidates remain for S6.",
        "relation_ids": ["st-chp5-p127-camillo-brother-of-pope", "st-chp5-p127-rospigliosi-sons-novices", "st-chp5-p127-four-sons-of-camillo"],
        "endpoints": {
            "st-chp5-p127-camillo-brother-of-pope": ("cand-2262", "cand-11755", "brother_of"),
            "st-chp5-p127-rospigliosi-sons-novices": ("cand-2262", "cand-6048", "admitted_as_novices_with_four_sons"),
            "st-chp5-p127-four-sons-of-camillo": ("cand-11763", "cand-2262", "children_of"),
        },
    },
    {
        "primary": "cand-2272", "members": ["cand-2272"], "index_entry": "Q-R.csv#200",
        "canonical_name": "Rossi, Mattia de'", "group": "new-person:de-mattia-rossi-f41c4c976a",
        "ku": "units/persons/mattia-de-rossi", "card": "04-knowledge/units/persons/mattia-de-rossi.md",
        "name_zh": "马蒂亚·德·罗西", "name_en": "Mattia de’ Rossi",
        "name_rows": [
            ("索引名", "Rossi, Mattia de'", "S1（索引 Q-R.csv#200）"),
            ("正文姓名形式", "Mattia de’ Rossi", "S2（第3章 pp.87、89）"),
        ],
        "sources": [
            {
                "location": "第3章；印刷页87",
                "summary": "Haskell称Mattia de’ Rossi是Bernini的助手，并报告其报酬仅为酒、战役题材画作和两件旧陶盘。",
                "quote": "Mattia de’ Rossi", "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "line 109; print p.87",
            },
            {
                "location": "第3章；印刷页89",
                "summary": "Haskell称S. Ignazio圆顶方案是根据Mattia de’ Rossi的建议获采纳。",
                "quote": "On the advice of Mattia de’ Rossi", "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "line 136; print p.89",
            },
        ],
        "description_zh": "本卡按全书索引和第3章pp.87、89的正文姓名形式登记Mattia de’ Rossi；现有Carlo de’ Rossi卡为另一人物。",
        "description_en": "This card registers Mattia de’ Rossi under the index and chapter 3, pp.87 and 89 forms. The existing Carlo de’ Rossi card is a different person.",
        "context_zh": "Haskell称Mattia是Bernini的助手，报酬包括酒、战役题材画作和两件旧陶盘；另称Pozzo的方案依据Mattia的建议获采纳。以上关系候选均待S6。",
        "context_en": "Haskell identifies Mattia as Bernini’s assistant and reports payment in wine, battle pictures, and two old majolica plates. Haskell also says Pozzo’s plan was accepted on Mattia’s advice. These relation candidates remain for S6.",
        "relation_ids": ["st-chp3-seciv-l106-116-mattia-assistant-to-berni", "st-chp3-seciv-l106-116-mattia-paid-in-kind", "st-chp3-seciv-l130-139-mattia-advice-plan-accepted"],
        "endpoints": {
            "st-chp3-seciv-l106-116-mattia-assistant-to-berni": ("cand-2272", "cand-0298", "served_as_assistant_to"),
            "st-chp3-seciv-l106-116-mattia-paid-in-kind": ("cand-2272", "cand-5309", "was_paid_in_kind_for_work"),
            "st-chp3-seciv-l130-139-mattia-advice-plan-accepted": ("cand-2272", "cand-5368", "advice_led_to_acceptance_of_pozzos_plan"),
        },
    },
    {
        "primary": "cand-2282", "members": ["cand-2282", "cand-2283", "cand-2284"],
        "index_entry": "Q-R.csv#210", "canonical_name": "Rosso, Lorenzo del",
        "member_index_entries": [
            ("cand-2283", "Q-R.csv#211", "and Luca Giordano"),
            ("cand-2284", "Q-R.csv#212", "taste"),
        ],
        "group": "new-person:del-lorenzo-rosso-0ec611aff2",
        "ku": "units/persons/lorenzo-del-rosso", "card": "04-knowledge/units/persons/lorenzo-del-rosso.md",
        "name_zh": "洛伦佐·德尔·罗索", "name_en": "Lorenzo del Rosso",
        "name_rows": [
            ("索引名", "Rosso, Lorenzo del", "S1（索引 Q-R.csv#210）"),
            ("正文名", "Lorenzo", "S2（第8章 pp.210-212）"),
        ],
        "sources": [
            {
                "location": "全书索引 Q-R.csv#211；子项and Luca Giordano；列页212-213",
                "summary": "同一索引姓名条目下的Luca Giordano子项定位于关于del Rosso兄弟与Giordano的连续讨论。",
                "quote": "and Luca Giordano", "source_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
                "source_span": "Q-R.csv#211",
            },
            {
                "location": "全书索引 Q-R.csv#212；子项taste；列页213",
                "summary": "同一索引姓名条目下的taste子项定位于p.213。",
                "quote": "taste", "source_file": "02-sources/03-Index/03-2-Index-CSV/Q-R.csv",
                "source_span": "Q-R.csv#212",
            },
            {
                "location": "第8章；印刷页210",
                "summary": "Haskell称Via Chiara附近的住宅由Andrea、Lorenzo与Ottavio del Rosso三兄弟居住。",
                "quote": "It was inhabited by three brothers, Andrea, Lorenzo and Ottavio", "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "source_span": "lines 81-82; print p.210",
            },
            {
                "location": "第8章；印刷页211",
                "summary": "Haskell讨论Lorenzo和Ottavio的遗嘱，并说明除Lorenzo向Montemagni遗赠Caravaggio画作外，遗嘱未提及绘画。",
                "quote": "The wills of Lorenzo and Ottavio", "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "source_span": "lines 92-94; print p.211",
            },
            {
                "location": "第8章；印刷页212",
                "summary": "Haskell称Lorenzo和Andrea可能在那不勒斯开始职业生涯，并称Luca Giordano是兄弟们在那不勒斯的主要艺术代理人。",
                "quote": "Luca Giordano was their principal artistic agent in Naples", "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "source_span": "lines 102-105; print p.212",
            },
        ],
        "description_zh": "本卡将cand-2282主索引条目及cand-2283、cand-2284两个同名索引子项合为Lorenzo del Rosso一人。正文称其与Andrea、Ottavio为兄弟；本卡不并入兄弟或Del Rosso家族KU。",
        "description_en": "This card groups the main index entry cand-2282 with the two same-name index subentries cand-2283 and cand-2284 as one person, Lorenzo del Rosso. The text identifies him as brother to Andrea and Ottavio; this card does not merge him with his brothers or the Del Rosso family KU.",
        "context_zh": "Haskell提及Lorenzo与Ottavio的遗嘱、Lorenzo向Montemagni遗赠一幅Caravaggio画作，并以可能语气提出他和Andrea或在那不勒斯开始职业生涯。Luca Giordano及taste为同一索引条目子项；相关关系候选待S6。",
        "context_en": "Haskell discusses Lorenzo’s and Ottavio’s wills, Lorenzo’s bequest of a Caravaggio painting to Montemagni, and the possibility that he and Andrea began their careers in Naples. Luca Giordano and taste are subentries under the same index name; related relation candidates remain for S6.",
        "relation_ids": ["st-chp8-p210-house-inhabited-by-lorenzo-del-rosso", "st-chp8-p211-wills-and-caravaggio-bequest", "st-chp8-p212-lorenzo-may-have-started-career-naples"],
        "endpoints": {
            "st-chp8-p210-house-inhabited-by-lorenzo-del-rosso": ("cand-7486", "cand-2282", "via_chiara_house_inhabited_by_lorenzo_del_rosso"),
            "st-chp8-p211-wills-and-caravaggio-bequest": ("cand-2282", "cand-7514", "wills_cited_and_lorenzo_bequest_of_caravaggio_picture_to_montemagni"),
            "st-chp8-p212-lorenzo-may-have-started-career-naples": ("cand-2282", "cand-3534", "lorenzo_may_have_started_career_in_naples"),
        },
    },
    {
        "primary": "cand-2376", "members": ["cand-2376"], "index_entry": "S.csv#64",
        "canonical_name": "Savelli, Prince Giulio", "group": "new-person:giulio-savelli-0722b9a04e",
        "ku": "units/persons/giulio-savelli", "card": "04-knowledge/units/persons/giulio-savelli.md",
        "name_zh": "朱利奥·萨韦利", "name_en": "Prince Giulio Savelli",
        "name_rows": [
            ("索引名", "Savelli, Prince Giulio", "S1（索引 S.csv#64）"),
            ("正文称谓", "Prince Giulio", "S2（第3章 p.92）"),
        ],
        "sources": [{
            "location": "第3章；印刷页92",
            "summary": "Haskell称Prince Giulio是Savelli家族首领，并记述他在皇帝调停后放弃教堂赞助权，以换取对其枢机祖先善行的特别表彰。",
            "quote": "Prince Giulio, the head of the family", "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
            "source_span": "lines 166-167; print p.92",
        }],
        "description_zh": "本卡按索引和第3章p.92登记Savelli家族首领Prince Giulio；与其祖先Cardinal Savelli分开。",
        "description_en": "This card registers Prince Giulio, head of the Savelli family, under the index and chapter 3, p.92 forms. He remains distinct from his ancestor Cardinal Savelli.",
        "context_zh": "Haskell称皇帝调停Prince Giulio放弃S. Ignazio祭坛赞助权的安排，并以特别表彰其枢机祖先善行作为交换。该关系候选仍待S6。",
        "context_en": "Haskell says the Emperor mediated Prince Giulio’s relinquishment of patronage for the S. Ignazio altar in exchange for special references to his Cardinal ancestor’s beneficence. This relation candidate remains for S6.",
        "relation_ids": ["st-chp3-seciv-l165-177-emperor-mediated-patronage-transfer", "st-chp3-seciv-l165-177-savelli-family-head-of-giulio", "st-chp3-seciv-l165-177-cardinal-savelli-ancestor-of-giulio"],
        "endpoints": {
            "st-chp3-seciv-l165-177-emperor-mediated-patronage-transfer": ("cand-5418", "cand-2376", "mediated_giulio_savelli_giving_up_chapel_patronage_for_memorial_references"),
            "st-chp3-seciv-l165-177-savelli-family-head-of-giulio": ("cand-2376", "cand-5417", "head_of_family"),
            "st-chp3-seciv-l165-177-cardinal-savelli-ancestor-of-giulio": ("cand-2375", "cand-2376", "ancestor_of"),
        },
    },
    {
        "primary": "cand-2205", "members": ["cand-2205"], "index_entry": "Q-R.csv#132",
        "canonical_name": "Roccatagliata, Giovanni Stefano", "group": "new-person:giovanni-roccatagliata-stefano-9f5bb05e0c",
        "ku": "units/persons/giovanni-stefano-roccatagliata", "card": "04-knowledge/units/persons/giovanni-stefano-roccatagliata.md",
        "name_zh": "乔瓦尼·斯特法诺·罗卡塔利亚塔", "name_en": "Giovanni Stefano Roccatagliata",
        "name_rows": [
            ("索引名", "Roccatagliata, Giovanni Stefano", "S1（索引 Q-R.csv#132）"),
            ("正文姓名形式", "Giovanni Stefano Roccatagliata", "S2（第5章 p.121注7）"),
        ],
        "sources": [{
            "location": "第5章；印刷页121注7",
            "summary": "Haskell的注释称Roccatagliata与Poussin关系密切、曾向Valguarnera出售画作，并引述Bertolotti称其为热那亚人；所引Bertolotti未在本批独立查阅。",
            "quote": "Giovanni Stefano Roccatagliata", "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
            "source_span": "line 131; p.121 n.7",
        }],
        "description_zh": "本卡按索引Q-R.csv#132及第5章p.121注7的全名形式登记Giovanni Stefano Roccatagliata；本批不将Haskell转引的Bertolotti当作独立查阅。",
        "description_en": "This card registers Giovanni Stefano Roccatagliata under index Q-R.csv#132 and chapter 5, p.121 n.7. This batch does not treat Haskell’s citation of Bertolotti as an independently consulted source.",
        "context_zh": "Haskell的注释称Roccatagliata与Poussin关系密切、向Valguarnera出售画作，并转引Bertolotti称其为热那亚人；售画候选的OCR与来源表述限制一并保留，关系待S6。",
        "context_en": "Haskell’s note says Roccatagliata was close to Poussin and sold pictures to Valguarnera, and cites Bertolotti for his Genoese origin. The OCR and source-attribution limitations on the sales candidate are retained; relations remain for S6.",
        "relation_ids": ["st-chp5-note-p121-n7-roccatagliata-contact", "st-chp5-note-p121-n7-roccatagliata-sales"],
        "endpoints": {
            "st-chp5-note-p121-n7-roccatagliata-contact": ("cand-2205", "cand-1984", "close_contact_with"),
            "st-chp5-note-p121-n7-roccatagliata-sales": ("cand-2205", "cand-2684", "sold_pictures_to"),
        },
    },
]


def make_card(t: dict) -> str:
    sources = []
    for candidate_id, index_entry, subentry in t.get("member_index_entries", []):
        entry_file = index_entry.split("#", 1)[0]
        sources.append({
            "citation": INDEX_CITATION,
            "location": f"全书索引 {index_entry}；子项{subentry}",
            "sentence_summary": f"与主条目同名的索引子项，页码定位到{t['canonical_name']}相关段落。",
            "original_quotes": [{"source_span": index_entry, "text": subentry}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/03-Index/03-2-Index-CSV/{entry_file}",
                "source_span": index_entry,
            },
        })
    index_file = t["index_entry"].split("#", 1)[0]
    sources.insert(0, {
        "citation": INDEX_CITATION,
        "location": f"全书索引 {t['index_entry']}",
        "sentence_summary": f"索引以“{t['canonical_name']}”列出此人。",
        "original_quotes": [{"source_span": t["index_entry"], "text": t["canonical_name"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/03-Index/03-2-Index-CSV/{index_file}",
            "source_span": t["index_entry"],
        },
    })
    for source in t["sources"]:
        sources.append({
            "citation": HASKELL_CITATION, "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["source_span"], "text": source["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source["source_file"],
                "source_span": source["source_span"],
            },
        })
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"],
        "type": "person", "evidence_status": "source_backed", "sources": sources,
        "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    name_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in t["name_rows"])
    relations = ", ".join(t["relation_ids"])
    return (
        f"---\n{fm}\n---\n\n## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}\n\n**English:** {t['description_en']}\n\n"
        f"### 名称\n\n| 字段 | 值 | 证据 |\n|---|---|---|\n{name_rows}\n\n"
        f"### 本书语境\n\n**中文：** {t['context_zh']} 直接S2关系候选{relations}保留待S6；本批不据身份登记裁定关系。\n\n"
        f"**English:** {t['context_en']} The direct S2 relation candidates {relations} remain for S6; this registration makes no relation decision.\n\n"
        "## 关系与证据\n\n### 关系记录\n\n"
        "当前没有正式关系。正文中的导航与线索不自动形成关系边。\n\n"
        f"**中文：** 直接S2关系候选{relations}保留待S6逐条裁决；本批不新增正式关系。\n\n"
        f"**English:** The direct S2 relation candidates {relations} remain for individual S6 review; this registration adds no formal relations.\n"
    )


def extract_card_fields(cards: dict[str, str]) -> tuple[list[dict], int]:
    from scripts import build_field_facts
    from scripts.build_field_facts import extract_records
    with tempfile.TemporaryDirectory(prefix="pnp-s4-person-endpoints-") as temp_root:
        temp_base = Path(temp_root)
        rows = []
        for t in TARGETS:
            temp_card = temp_base / t["card"]
            temp_card.parent.mkdir(parents=True, exist_ok=True)
            temp_card.write_text(cards[t["card"]], encoding="utf-8")
            rows.append({"ku_id": t["ku"], "card_path": t["card"]})
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
        if tmp.exists():
            tmp.unlink()


def with_bom(text: str, original: bytes | None = None) -> bytes:
    raw = text.encode("utf-8")
    if original is None or original.startswith(b"\xef\xbb\xbf"):
        return b"\xef\xbb\xbf" + raw
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Register five source-local person groups, including one three-candidate group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    base = helper.base
    sync = base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {r["statement_id"]: r for r in statements}
    cards = {t["card"]: make_card(t) for t in TARGETS}
    card_paths = {t["card"]: ROOT / t["card"] for t in TARGETS}
    all_members = [cid for t in TARGETS for cid in t["members"]]
    assert len(all_members) == len(set(all_members))

    for t in TARGETS:
        for cid in t["members"]:
            candidate, alignment = candidate_by_id[cid], alignment_by_id[cid]
            assert candidate.get("suggested_type") == "person"
            assert alignment.get("decision") == "new"
            assert base.sync.get_group(alignment.get("resolution_note", "")) == t["group"]
            if alignment.get("ku_id"):
                assert alignment.get("ku_id") == t["ku"]
            else:
                assert t["ku"] not in manifest_by_ku
                assert t["card"] not in accepted_paths and not card_paths[t["card"]].exists()
        group_members = [
            r["candidate_id"] for r in alignments
            if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new"
            and base.sync.get_group(r.get("resolution_note", "")) == t["group"]
        ]
        assert sorted(group_members) == sorted(t["members"]), (t["group"], group_members, t["members"])
        main_candidate = candidate_by_id[t["primary"]]
        assert main_candidate.get("index_entry_id") == t["index_entry"]
        assert main_candidate.get("canonical_name") == t["canonical_name"]
        direct = {
            r["statement_id"] for r in statements
            if (r.get("qualifiers") or {}).get("relation_candidate") is True
            and (r.get("subject_candidate_id") == t["primary"] or r.get("object_candidate_id") == t["primary"])
        }
        assert direct == set(t["endpoints"]), (t["primary"], sorted(direct), sorted(t["endpoints"]))
        for sid, expected in t["endpoints"].items():
            row = statement_by_id[sid]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == expected
        index_path = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / t["index_entry"].split("#", 1)[0]
        assert t["canonical_name"] in index_path.read_text(encoding="utf-8-sig")
        for cid, entry, subentry in t.get("member_index_entries", []):
            subrow = candidate_by_id[cid]
            assert subrow.get("index_entry_id") == entry and subrow.get("sub_entry") == subentry
            assert subentry in index_path.read_text(encoding="utf-8-sig")
        for source in t["sources"]:
            source_text = (ROOT / source["source_file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", source["quote"]) in re.sub(r"\s+", " ", source_text), (t["primary"], source["source_span"])

    pending_groups = [t for t in TARGETS if not all(alignment_by_id[cid].get("ku_id") for cid in t["members"])]
    if not pending_groups:
        for t in TARGETS:
            assert all(alignment_by_id[cid].get("ku_id") == t["ku"] for cid in t["members"])
            assert card_paths[t["card"]].read_text(encoding="utf-8-sig") == cards[t["card"]]
            assert t["card"] in accepted_paths and manifest_by_ku[t["ku"]].get("card_path") == t["card"]
        print("ALREADY REGISTERED: five person groups and seven candidate mappings are present.")
        return 0
    assert len(pending_groups) == len(TARGETS)

    before_stats = sync.summarize_by_type(candidates, alignments)
    planned_alignments = [dict(r) for r in alignments]
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        for cid in t["members"]:
            row = next(r for r in planned_alignments if r.get("candidate_id") == cid and not r.get("external_source"))
            row["ku_id"] = t["ku"]
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] += (
                f" S4 registration: group {t['group']} -> {t['ku']}; "
                "source-local registration only; no external identity was added and direct relation candidates remain for S6."
            )
        planned_manifest.append({
            "ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"],
            "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"],
        })
        planned_accepted = helper.base.insert_accepted(planned_accepted, t["card"])
    planned_manifest.sort(key=lambda r: r["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(r[key] for r in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(r[key] for r in before_stats.values()) for key in next(iter(before_stats.values()))}
    group_count, member_count = len(TARGETS), len(all_members)
    assert totals["registered_groups"] == before_totals["registered_groups"] + group_count
    assert totals["registered_members"] == before_totals["registered_members"] + member_count
    assert totals["pending_groups"] == before_totals["pending_groups"] - group_count
    assert totals["pending_members"] == before_totals["pending_members"] - member_count
    assert len(planned_manifest) == len(manifest) + group_count

    additions, cards_with_tables = extract_card_fields(cards)
    assert cards_with_tables == group_count and len(additions) == 2 * group_count
    assert all(r.get("evidence_status") == "source_backed" for r in additions)
    enrichment_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing_enrichment = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id", "")) for r in existing_enrichment}
    existing_ids = {r.get("enrichment_id", "") for r in existing_enrichment}
    max_id = max((int(m.group(1)) for value in existing_ids if (m := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for n, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + n:05d}"
        assert (row["ku_id"], row["field"], row["value"], row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in existing_ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(r, ensure_ascii=False) for r in additions) + "\n"

    process_text = base.process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接端点登记：Rospigliosi、Rossi、Del Rosso、Savelli、Roccatagliata（{DATE}）\n\n"
    for t in TARGETS:
        relations = "、".join(t["relation_ids"])
        members = "、".join(t["members"])
        process_text += (
            f"- 候选{members}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/units/persons/{t['ku'].split('/', 2)[2]}.md)。"
            f"索引主项{t['index_entry']}与所列正文建立书内身份锚点；直接S2关系候选{relations}留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。\n"
        )
    relation_count = sum(len(t["relation_ids"]) for t in TARGETS)
    process_text += (
        f"\n本批登记5个既有S3 new身份组、{member_count}条候选映射，新增{len(additions)}条source_backed名称字段；"
        "不添加外部身份标识、候选、来源或正式关系。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接端点登记：Rospigliosi、Rossi、Del Rosso、Savelli、Roccatagliata（{DATE}）\n\n"
        "登记5个已有S3 new身份组，其中Lorenzo del Rosso组包含cand-2282、cand-2283、cand-2284三条候选映射。"
        f"各组只建立一个KU；本批未查验外部人物规范记录，未新增关系；{relation_count}条直接S2关系候选保留待S6逐条裁决。"
        f"KU={len(planned_manifest)}，名称字段总数={len(existing_enrichment) + len(additions)}。"
        f"详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    temp_dir = Path(tempfile.mkdtemp(prefix="pnp-s4-person-endpoints-"))
    try:
        alignment_stage, manifest_stage = temp_dir / "alignment.csv", temp_dir / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT_PATH: alignment_stage.read_bytes(),
            MANIFEST_PATH: manifest_stage.read_bytes(),
            ENRICHMENT_PATH: with_bom(planned_enrichment, ENRICHMENT_PATH.read_bytes()),
            ACCEPTED_PATH: with_bom("\n".join(planned_accepted) + "\n", ACCEPTED_PATH.read_bytes()),
            PROCESS_PATH: with_bom(process_text + "\n", PROCESS_PATH.read_bytes()),
            RESULT_PATH: with_bom(result_text + "\n", RESULT_PATH.read_bytes()),
        }
        for t in TARGETS:
            writes[card_paths[t["card"]]] = with_bom(cards[t["card"]])
    finally:
        for p in temp_dir.glob("*"):
            p.unlink()
        temp_dir.rmdir()

    if args.dry_run:
        print("S4 dry-run passed: five pre-existing S3 person groups and all candidate members/direct endpoints match.")
        print(f"candidate_mappings={member_count}; new_groups={group_count}; source_backed_name_fields={len(additions)}; direct_relation_candidates={relation_count}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
        print("external_identity_rows=0; formal_relations_added=0; candidate_backlog_changed=0; sources_registry_changed=0; no files changed")
        return 0

    originals = {p: p.read_bytes() if p.exists() else None for p in writes}
    try:
        for p, content in writes.items():
            atomic_write(p, content)
    except Exception:
        for p, content in originals.items():
            if content is None:
                if p.exists():
                    p.unlink()
            else:
                atomic_write(p, content)
        raise
    print(
        f"applied: groups={group_count}; candidate_mappings={member_count}; external_identity_rows=0; "
        f"name_fields={len(additions)}; direct_relation_candidates={relation_count}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
