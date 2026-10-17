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
DATE = "2026-10-17"
ANCHOR = "s4-person-direct-endpoints-gloucester-farsetti-monconys-mei-newcastle-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-1204", "index_entry": "G.csv#111",
        "canonical_name": "Gloucester, William Henry, 1st Duke of",
        "group": "new-person:1st-gloucester-henry-of-william-f80c2b53e6",
        "ku": "units/persons/william-henry-duke-of-gloucester",
        "card": "04-knowledge/units/persons/william-henry-duke-of-gloucester.md",
        "name_zh": "威廉·亨利（第一代格洛斯特公爵）",
        "name_en": "William Henry, 1st Duke of Gloucester",
        "body_name": "Duke of Gloucester",
        "body_source": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "body_span": "lines 17-18 and 25-27; print p.366",
        "body_location": "第15章；印刷页366及注1",
        "body_summary": "Haskell称途经帕多瓦的格洛斯特公爵竖立了Azzo d’Este雕像；注1记其1775年9月和1777年5月在帕多瓦期间患病，并称Memmo首次访问时与他有联系、劝其订制雕像的日期不确定。",
        "context_en": "Haskell says the Duke of Gloucester erected a statue of Azzo d’Este while passing through Padua. Note 1 reports illness during visits in September 1775 and May 1777, and says Memmo was in touch with him on the first visit while the date of persuading him to order the statue remains uncertain.",
        "relation_ids": ["st-chp15-p366-duke-gloucester-azzo-statue", "st-chp15-p366-note1-duke-visits", "st-chp15-p366-note1-memmo-contact-and-order-date"],
        "endpoints": {
            "st-chp15-p366-duke-gloucester-azzo-statue": ("cand-1204", "cand-10486", "duke_of_gloucester_erected_statue_of_azzo"),
            "st-chp15-p366-note1-duke-visits": ("cand-1204", "cand-3944", "note_reports_duke_gloucester_padua_visits_and_illness"),
            "st-chp15-p366-note1-memmo-contact-and-order-date": ("cand-1642", "cand-1204", "memmo_contacted_duke_during_first_visit_order_date_uncertain"),
        },
    },
    {
        "candidate": "cand-1000", "index_entry": "F.csv#15",
        "canonical_name": "Farsetti, Anton Francesco",
        "group": "new-person:anton-farsetti-francesco-89c16bbb22",
        "ku": "units/persons/anton-francesco-farsetti",
        "card": "04-knowledge/units/persons/anton-francesco-farsetti.md",
        "name_zh": "安东·弗朗切斯科·法尔塞蒂", "name_en": "Anton Francesco Farsetti",
        "body_name": "nephew Anton Francesco",
        "body_source": "02-sources/02-Markdown/15_CHP-15_sec_i.md",
        "body_span": "line 39; print p.364", "body_location": "第15章；印刷页364",
        "body_summary": "Haskell称Tommaso Giuseppe的晚年因侄子Anton Francesco挥霍而痛苦，并说Tommaso曾向宗教裁判所告发他。",
        "context_en": "Haskell says Tommaso Giuseppe’s later years were embittered by the dissipated extravagance of his nephew Anton Francesco and that Tommaso denounced him to the Inquisitors.",
        "relation_ids": ["st-chp15-p364-tommaso-embittered-by-nephew", "st-chp15-p364-tommaso-denounced-anton-francesco", "st-chp15-p364-anton-nephew-of-tommaso"],
        "endpoints": {
            "st-chp15-p364-tommaso-embittered-by-nephew": ("cand-1013", "cand-1000", "last_years_embittered_by_nephew_anton_francesco_extravagance"),
            "st-chp15-p364-tommaso-denounced-anton-francesco": ("cand-1013", "cand-1000", "denounced_nephew_anton_francesco_to_inquisitors"),
            "st-chp15-p364-anton-nephew-of-tommaso": ("cand-1000", "cand-1013", "nephew_of_tommaso_giuseppe"),
        },
    },
    {
        "candidate": "cand-1685", "index_entry": "M.csv#225",
        "canonical_name": "Monconys, Balthasar de",
        "group": "new-person:balthasar-de-monconys-0b85e40d5c",
        "ku": "units/persons/balthasar-de-monconys",
        "card": "04-knowledge/units/persons/balthasar-de-monconys.md",
        "name_zh": "巴尔塔萨·德·蒙科尼", "name_en": "Balthasar de Monconys",
        "body_name": "Monsieur de Monconys",
        "body_source": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "body_span": "line 40; print p.124", "body_location": "第5章；印刷页124",
        "body_summary": "Haskell称法国旅行者Monsieur de Monconys于1664年访问罗马，Simonelli带他参观艺术家工作室、介绍Poussin与Claude，并卖给他一幅未具名的画。",
        "context_en": "Haskell identifies Monsieur de Monconys as a French traveller who visited Rome in 1664. Simonelli took him around artists’ studios, introduced him to Poussin and Claude, and sold him an unidentified picture.",
        "relation_ids": ["st-chp5-p124-monconys-rome-visit", "st-chp5-p124-monconys-visited-rome", "st-chp5-p124-monconys-picture-sale"],
        "mention_only_candidates": ["st-chp5-p124-monconys-introduced-poussin", "st-chp5-p124-monconys-introduced-claude"],
        "endpoints": {
            "st-chp5-p124-monconys-rome-visit": ("cand-2434", "cand-1685", "guided_visitor_around_studios"),
            "st-chp5-p124-monconys-visited-rome": ("cand-1685", "cand-4490", "visited_place"),
            "st-chp5-p124-monconys-picture-sale": ("cand-2434", "cand-1685", "sold_unidentified_picture_to"),
        },
    },
    {
        "candidate": "cand-1633", "index_entry": "M.csv#173",
        "canonical_name": "Mei, Bernardino",
        "group": "new-person:bernardino-mei-15dd160f7a",
        "ku": "units/persons/bernardino-mei",
        "card": "04-knowledge/units/persons/bernardino-mei.md",
        "name_zh": "贝尔纳迪诺·梅伊", "name_en": "Bernardino Mei",
        "body_name": "Bernardino Mei",
        "body_source": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
        "body_span": "lines 95-97; print p.154", "body_location": "第6章；印刷页154",
        "body_summary": "Haskell称Flavio Chigi委托Bernardino Mei绘制天花板壁画，并在列举的Chigi宫殿寓意画中提到《正义与和平》及《从维纳斯的欢愉中救出的青年》。",
        "context_en": "Haskell says Flavio Chigi commissioned Bernardino Mei to paint a ceiling fresco and lists Justice and Peace and Youth rescued from the Pleasures of Venus among Mei’s allegories in the Chigi palace.",
        "relation_ids": ["st-chp6-p154-mei-allegories", "st-chp6-p154-mei-paints-fortune-fresco", "st-chp6-p154-mei-youth-rescued-allegory"],
        "endpoints": {
            "st-chp6-p154-mei-allegories": ("cand-1633", "cand-1634", "mei-allegory-of-justice-and-peace"),
            "st-chp6-p154-mei-paints-fortune-fresco": ("cand-1633", "cand-6326", "painted-by-bernardino-mei"),
            "st-chp6-p154-mei-youth-rescued-allegory": ("cand-1633", "cand-1635", "mei-allegory-youth-rescued-from-pleasures-of-venus"),
        },
    },
    {
        "candidate": "cand-1737", "index_entry": "N.csv#17",
        "canonical_name": "Newcastle, William Cavendish, Duke of",
        "group": "new-person:cavendish-newcastle-of-william-adc14e205b",
        "ku": "units/persons/william-cavendish-duke-of-newcastle",
        "card": "04-knowledge/units/persons/william-cavendish-duke-of-newcastle.md",
        "name_zh": "威廉·卡文迪什（纽卡斯尔公爵）",
        "name_en": "William Cavendish, Duke of Newcastle",
        "body_name": "Duke of Newcastle",
        "body_source": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "body_span": "lines 110-111; print p.178", "body_location": "第7章；印刷页178",
        "body_summary": "Haskell称Fanelli制作的青铜小像和马匹题材呼应其主要赞助人纽卡斯尔公爵的兴趣，并称公爵曾任Charles王子导师且热衷骑马。",
        "context_en": "Haskell says Fanelli’s small bronzes and horse subjects reflected the interests of one of his principal patrons, the Duke of Newcastle, who was governor to Charles, Prince of Wales, and an enthusiastic rider. Fanelli drew on sacred and profane literature for horse portrayals made for the Duke and his circle.",
        "relation_ids": ["st-chp7-p178-i20", "st-chp7-p178-i21", "st-chp7-p178-i22"],
        "endpoints": {
            "st-chp7-p178-i20": ("cand-6745", "cand-1737", "fanelli_bronzes_reflected_duke_of_newcastles_interests"),
            "st-chp7-p178-i21": ("cand-1737", "cand-0656", "governed_charles_prince_of_wales_and_was_an_enthusiastic_rider"),
            "st-chp7-p178-i22": ("cand-0989", "cand-1737", "used_sacred_and_profane_literature_to_dignify_horse_portrayals"),
        },
    },
]


def make_card(t: dict) -> str:
    index_file = t["index_entry"].split("#", 1)[0]
    index_path = f"02-sources/03-Index/03-2-Index-CSV/{index_file}"
    sources = [
        {
            "citation": INDEX_CITATION,
            "location": f"全书索引 {t['index_entry']}",
            "sentence_summary": f"索引以“{t['canonical_name']}”列出此人，页码指向本卡所据正文。",
            "original_quotes": [{"source_span": t["index_entry"], "text": t["canonical_name"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": index_path, "source_span": t["index_entry"]},
        },
        {
            "citation": HASKELL_CITATION,
            "location": t["body_location"],
            "sentence_summary": t["body_summary"],
            "original_quotes": [{"source_span": t["body_span"], "text": t["body_name"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["body_source"], "source_span": t["body_span"]},
        },
    ]
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"], "type": "person", "evidence_status": "source_backed",
        "sources": sources, "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    name_rows = "\n".join([
        f"| 索引名 | {t['canonical_name']} | S1（索引 {t['index_entry']}） |",
        f"| 正文称谓 | {t['body_name']} | S2（{t['body_location']}） |",
    ])
    relation_ids = ", ".join(t["relation_ids"])
    chapter = t["body_location"].split("第", 1)[1].split("章", 1)[0]
    context_zh = (
        f"{t['body_summary']} 本批只登记人物身份；直接关系候选{relation_ids}均保留待S6，"
        "不因建立KU而判定关系成立。"
    )
    mention_only_zh = ""
    mention_only_en = ""
    if t.get("mention_only_candidates"):
        mention_only_zh = f"此外，{'、'.join(t['mention_only_candidates'])}仅在mentioned_candidate_ids中提及该人物，并非结构化主客体端点，不纳入本批直接端点映射。"
        mention_only_en = f" The person is also mentioned, but is not a subject or object endpoint, in {', '.join(t['mention_only_candidates'])}; those candidates are excluded from this direct-endpoint mapping."
    return (
        f"---\n{fm}\n---\n\n## 内容\n\n### 描述\n\n"
        f"**中文：** 本卡按全书索引中的完整姓名及第{chapter}章对应正文称谓登记该人物。"
        "本轮未查验外部人物规范记录；卡片只保留书内身份锚点，不扩展未经本书支持的履历。\n\n"
        f"**English:** This card registers the person named in the book index and matched to the corresponding chapter form in the text. "
        "No external authority record was consulted in this batch; the card preserves the book-based identity anchor without adding unsupported biography.\n\n"
        f"### 名称\n\n| 字段 | 值 | 证据 |\n|---|---|---|\n{name_rows}\n\n"
        f"### 本书语境\n\n**中文：** {context_zh}{mention_only_zh}\n\n"
        f"**English:** {t['context_en']} The direct S2 relation candidates {relation_ids} remain for S6; registration itself creates no edge.{mention_only_en}\n\n"
        "## 关系与证据\n\n### 关系记录\n\n"
        "当前没有正式关系。正文中的导航与线索不自动形成关系边。\n\n"
        f"**中文：** S2直接关系候选{relation_ids}保留待S6逐条裁决；本批不新增正式关系。\n\n"
        f"**English:** The direct S2 relation candidates {relation_ids} remain for individual S6 review; this registration adds no formal relations.\n"
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
        temp_path = Path(handle.name)
        handle.write(content)
    try:
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def with_bom(text: str, original: bytes | None = None) -> bytes:
    encoded = text.encode("utf-8")
    if original is None or original.startswith(b"\xef\xbb\xbf"):
        return b"\xef\xbb\xbf" + encoded
    return encoded


def main() -> int:
    parser = argparse.ArgumentParser(description="Register five direct-endpoint person groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    base = helper.base
    sync = base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_lines = accepted.splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    cards = {t["card"]: make_card(t) for t in TARGETS}
    card_paths = {t["card"]: ROOT / t["card"] for t in TARGETS}

    for t in TARGETS:
        candidate = candidate_by_id[t["candidate"]]
        alignment = alignment_by_id[t["candidate"]]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("index_entry_id") == t["index_entry"]
        assert candidate.get("canonical_name") == t["canonical_name"]
        assert alignment.get("decision") == "new"
        assert base.sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and base.sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert members == [t["candidate"]], (t["group"], members)
        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and (row.get("subject_candidate_id") == t["candidate"] or row.get("object_candidate_id") == t["candidate"])
        }
        assert direct == set(t["endpoints"]), (t["candidate"], sorted(direct), sorted(t["endpoints"]))
        for sid, (subject, obj, predicate) in t["endpoints"].items():
            statement = statement_by_id[sid]
            assert (statement.get("subject_candidate_id"), statement.get("object_candidate_id"), statement.get("predicate")) == (subject, obj, predicate)
        index_path = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / t["index_entry"].split("#", 1)[0]
        assert t["canonical_name"] in index_path.read_text(encoding="utf-8-sig")
        assert t["body_name"] in (ROOT / t["body_source"]).read_text(encoding="utf-8-sig")
        if alignment.get("ku_id"):
            assert alignment.get("ku_id") == t["ku"]
        else:
            assert t["ku"] not in manifest_by_ku
            assert t["card"] not in accepted_paths and not card_paths[t["card"]].exists()

    pending = [t for t in TARGETS if not alignment_by_id[t["candidate"]].get("ku_id")]
    if not pending:
        for t in TARGETS:
            assert card_paths[t["card"]].read_text(encoding="utf-8-sig") == cards[t["card"]]
            assert t["card"] in accepted_paths and manifest_by_ku[t["ku"]].get("card_path") == t["card"]
        print("ALREADY REGISTERED: five person groups and five candidate mappings are present.")
        return 0
    assert len(pending) == len(TARGETS), [t["candidate"] for t in pending]

    before_stats = sync.summarize_by_type(candidates, alignments)
    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        alignment = next(row for row in planned_alignments if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        alignment["ku_id"] = t["ku"]
        alignment["process_ref"] = PROCESS_REF
        alignment["resolution_note"] += (
            f" S4 registration: preserved S3 singleton group {t['group']} -> {t['ku']}; source-local registration only; "
            "no external identity was added and direct relation candidates remain for S6."
        )
        planned_manifest.append({
            "ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"],
            "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"],
        })
        planned_accepted = helper.base.insert_accepted(planned_accepted, t["card"])
    planned_manifest.sort(key=lambda row: row["ku_id"])

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == before_totals["registered_members"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    additions, cards_with_tables = extract_card_fields(cards)
    assert cards_with_tables == len(TARGETS) and len(additions) == 2 * len(TARGETS), (cards_with_tables, len(additions))
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    existing_enrichment_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing_enrichment = [json.loads(line) for line in existing_enrichment_text.splitlines() if line.strip()]
    natural_keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) for row in existing_enrichment}
    existing_ids = {row.get("enrichment_id", "") for row in existing_enrichment}
    max_id = max((int(m.group(1)) for value in existing_ids if (m := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + offset:05d}"
        assert (row["ku_id"], row["field"], row["value"], row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in existing_ids
    planned_enrichment = existing_enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in additions) + "\n"

    process_text = base.process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Gloucester、Farsetti、Monconys、Mei、Newcastle（{DATE}）\n\n"
    for t in TARGETS:
        relations = "、".join(t["relation_ids"])
        mention_only = t.get("mention_only_candidates", [])
        mention_note = (
            f"另在{ '、'.join(mention_only) }中仅列为提及对象，不是结构化主客体端点，故不作直接端点映射。"
            if mention_only else ""
        )
        process_text += (
            f"- {t['candidate']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/units/persons/{t['ku'].split('/', 2)[2]}.md)。"
            f"以索引{t['index_entry']}与{t['body_location']}的称谓建立书内身份锚点；S2直接关系候选{relations}留待S6逐条裁决。{mention_note}本批未查验外部身份记录，不新增正式关系。\n"
        )
    relation_count = sum(len(t["relation_ids"]) for t in TARGETS)
    process_text += (
        f"\n本批登记5个既有S3 new单成员人物组及5条候选映射，新增{len(additions)}条source_backed名称字段；"
        "不改写S3分组，不添加外部身份标识、候选、来源或正式关系。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接端点登记：Gloucester、Farsetti、Monconys、Mei、Newcastle（{DATE}）\n\n"
        "登记5个已有S3 new单成员人物组，各组对应一个KU；候选映射保留原S3分组号。名称字段仅依据全书索引及对应正文形式，"
        f"本批未查验外部人物规范记录，也未新增关系。{relation_count}条直接S2关系候选保留待S6逐条裁决。"
        f"KU={len(planned_manifest)}，名称字段总数={len(existing_enrichment) + len(additions)}。"
        f"详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    temp_dir = Path(tempfile.mkdtemp(prefix="pnp-s4-person-endpoints-"))
    try:
        alignment_stage = temp_dir / "alignment.csv"
        manifest_stage = temp_dir / "ku-manifest.csv"
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
        for path in temp_dir.glob("*"):
            path.unlink()
        temp_dir.rmdir()

    if args.dry_run:
        print("S4 dry-run passed: five pre-existing singleton S3 person groups and all direct S2 relation endpoints match.")
        print(f"candidate_mappings=5; source_backed_name_fields={len(additions)}; direct_relation_candidates={relation_count}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
        print("external_identity_rows=0; formal_relations_added=0; candidate_backlog_changed=0; sources_registry_changed=0; no files changed")
        return 0

    originals = {path: path.read_bytes() if path.exists() else None for path in writes}
    try:
        for path, content in writes.items():
            atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            if content is None:
                if path.exists():
                    path.unlink()
            else:
                atomic_write(path, content)
        raise
    print(
        f"applied: groups=5; candidate_mappings=5; external_identity_rows=0; name_fields={len(additions)}; "
        f"direct_relation_candidates={relation_count}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
