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
ANCHOR = "s4-person-direct-endpoints-guidiccioni-malpighi-gambarini-pourbus-sacchetti-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "candidate": "cand-1281", "index_entry": "G.csv#191", "canonical_name": "Guidiccioni, Lelio",
        "group": "new-person:guidiccioni-lelio-3a426183a6",
        "ku": "units/persons/lelio-guidiccioni", "card": "04-knowledge/units/persons/lelio-guidiccioni.md",
        "name_zh": "莱利奥·圭迪乔尼", "name_en": "Lelio Guidiccioni",
        "body_sources": [
            {
                "location": "第5章；印刷页121",
                "summary": "Haskell称Lelio Guidiccioni是巴贝里尼圈内诗人和收藏者，并以may well be等措辞表示他可能被不诚实的商人以存疑归属作品欺骗。",
                "quote": "Lelio Guidiccioni", "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "source_span": "line 10; print p.121",
            },
            {
                "location": "第5章；印刷页121注2",
                "summary": "注2称一幅Mercati版画献给Guidiccioni，铭文记录其对绘画的喜爱。",
                "quote": "dedicated to Lelio Guidiccioni", "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "source_span": "line 127; p.121 n.2",
            },
        ],
        "name_rows": [
            ("索引名", "Guidiccioni, Lelio", "S1（索引 G.csv#191）"),
            ("正文姓名形式", "Lelio Guidiccioni", "S2（第5章 p.121）"),
        ],
        "description_zh": "本卡按全书索引与第5章p.121的完整姓名登记诗人Lelio Guidiccioni；本批只登记书内身份，不补写其生平或将Haskell的推测升级为事实。",
        "description_en": "This card registers the poet Lelio Guidiccioni under the full name in the index and chapter 5, p.121. This batch records the book-based identity only and does not expand his biography or turn Haskell’s conjecture into fact.",
        "context_zh": "Haskell称他为巴贝里尼圈内诗人和绘画收藏者，并说他可能受不诚实画商误导而买入存疑归属的作品；注2另称献给他的Mercati版画铭文记录其爱好绘画。",
        "context_en": "Haskell describes him as a poet in the Barberini circle and a collector who may have been misled by dealers into acquiring works with doubtful attributions. Note 2 also records a Mercati print dedicated to him with an inscription about his love of painting.",
        "relation_ids": ["st-chp5-note-p121-n2-mercati-print", "st-chp5-p121-guidiccioni-attributions", "st-chp5-note-p121-n2-print-inscription-interest"],
        "endpoints": {
            "st-chp5-note-p121-n2-mercati-print": ("cand-6092", "cand-1281", "dedicated_to"),
            "st-chp5-p121-guidiccioni-attributions": ("cand-1281", "cand-11908", "collection_acquisition_reported"),
            "st-chp5-note-p121-n2-print-inscription-interest": ("cand-6092", "cand-1281", "inscription_records_interest_of"),
        },
    },
    {
        "candidate": "cand-1500", "index_entry": "M.csv#37", "canonical_name": "Malpighi, Marcello",
        "group": "new-person:malpighi-marcello-dfbdbe5c0e",
        "ku": "units/persons/marcello-malpighi", "card": "04-knowledge/units/persons/marcello-malpighi.md",
        "name_zh": "马尔切洛·马尔皮基", "name_en": "Marcello Malpighi",
        "body_sources": [{
            "location": "第8章；印刷页203",
            "summary": "Haskell称医生Marcello Malpighi是具有鲜明鉴赏趣味的收藏者、Guercino与Cignani等画家的朋友，并报告他评论过一幅Guido Reni作品。",
            "quote": "Marcello Malpighi", "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "source_span": "line 8; print p.203",
        }],
        "name_rows": [
            ("索引名", "Malpighi, Marcello", "S1（索引 M.csv#37）"),
            ("正文姓名形式", "Marcello Malpighi", "S2（第8章 p.203）"),
        ],
        "description_zh": "本卡按全书索引及第8章p.203的完整姓名登记医生与收藏者Marcello Malpighi；本轮未查验外部人物规范记录。",
        "description_en": "This card registers the physician and collector Marcello Malpighi under the full name in the index and chapter 8, p.203. No external person authority record was consulted in this batch.",
        "context_zh": "Haskell称Malpighi收藏绘画、具有鲜明鉴赏趣味，并是Guercino和Cignani等艺术家的朋友；其对Guido Reni一幅作品的评论也按作者报告保留。",
        "context_en": "Haskell describes Malpighi as a picture collector with decided tastes and a friend of artists including Guercino and Cignani; his comment on a Guido Reni painting is retained as reported by the author.",
        "relation_ids": ["st-chp8-p203-malpighi-friend-guercino", "st-chp8-p203-malpighi-reni-painting-and-taste", "st-chp8-p203-malpighi-friend-cignani"],
        "endpoints": {
            "st-chp8-p203-malpighi-friend-guercino": ("cand-1500", "cand-1258", "friendship_with_person"),
            "st-chp8-p203-malpighi-reni-painting-and-taste": ("cand-1500", "cand-7384", "malpighi_commented_on_painting"),
            "st-chp8-p203-malpighi-friend-cignani": ("cand-1500", "cand-0748", "friendship_with_person"),
        },
    },
    {
        "candidate": "cand-1113", "index_entry": "G.csv#20", "canonical_name": "Gambarini, Giuseppe",
        "group": "new-person:gambarini-giuseppe-41d66b2cf1",
        "ku": "units/persons/giuseppe-gambarini", "card": "04-knowledge/units/persons/giuseppe-gambarini.md",
        "name_zh": "朱塞佩·甘巴里尼", "name_en": "Giuseppe Gambarini",
        "body_sources": [
            {
                "location": "第8章；印刷页203",
                "summary": "Haskell称商人Giovanni Antonio Belloni将Gambarini派往罗马旅行。",
                "quote": "sent the last artist on a journey to Rome", "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "source_span": "line 8; print p.203",
            },
            {
                "location": "第8章；印刷页223",
                "summary": "Haskell提到Russo委托包括Giuseppe Gambarini在内的博洛尼亚画家创作作品。",
                "quote": "two bambocciate by Giuseppe Gambarini", "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "line 142; print p.223",
            },
            {
                "location": "第8章；印刷页225",
                "summary": "Haskell称Giuseppe Gambarini为Buonaccorsi宫殿的埃涅阿斯题材画作绘制了后续场景。",
                "quote": "Giuseppe Gambarini", "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "lines 168-170; print p.225",
            },
        ],
        "name_rows": [
            ("索引名", "Gambarini, Giuseppe", "S1（索引 G.csv#20）"),
            ("正文姓名形式", "Giuseppe Gambarini", "S2（第8章 pp.223、225）"),
        ],
        "description_zh": "本卡将第8章p.203的Gambarini称谓与同章pp.223、225出现的Giuseppe Gambarini按索引G.csv#20归于同一书内人物组；本批不补写外部生平。",
        "description_en": "This card groups the p.203 form Gambarini with Giuseppe Gambarini in chapter 8, pp.223 and 225, under index entry G.csv#20. This batch adds no external biography.",
        "context_zh": "Haskell称Belloni派Gambarini赴罗马；随后提及Russo委托的两幅小风俗画，并称Gambarini为Buonaccorsi宫殿的埃涅阿斯题材绘制了后续场景。",
        "context_en": "Haskell says Belloni sent Gambarini to Rome, later notes two bambocciate commissioned by Russo, and names Gambarini among the painters who produced further Aeneid scenes for the Buonaccorsi palace.",
        "relation_ids": ["st-chp8-p203-belloni-sent-gambarini-to-rome", "st-chp8-p225-gambarini-pagan-scenes", "st-chp8-p225-artist-produces-aeneid-scenes-gambarini"],
        "endpoints": {
            "st-chp8-p203-belloni-sent-gambarini-to-rome": ("cand-0271", "cand-1113", "merchant_sent_artist_on_journey_to_city"),
            "st-chp8-p225-gambarini-pagan-scenes": ("cand-1113", "cand-7778", "commissioned_to_paint_pagan_scenes"),
            "st-chp8-p225-artist-produces-aeneid-scenes-gambarini": ("cand-1113", "cand-7776", "produced_further_aeneid_scenes_for_gallery"),
        },
    },
    {
        "candidate": "cand-1983", "index_entry": "P.csv#185", "canonical_name": "Pourbus, Franz, the Younger",
        "group": "new-person:franz-pourbus-younger-cd004e16c5",
        "ku": "units/persons/franz-pourbus-the-younger", "card": "04-knowledge/units/persons/franz-pourbus-the-younger.md",
        "name_zh": "弗朗茨·普尔布斯（小）", "name_en": "Franz Pourbus the Younger",
        "body_sources": [{
            "location": "第7章；印刷页174",
            "summary": "Haskell称Marie de Medici召Franz Pourbus the Younger赴巴黎；他于1609年到达，并为Marie及其宫廷绘制许多肖像。",
            "quote": "Franz Pourbus the Younger", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "source_span": "lines 55-57; print p.174",
        }],
        "name_rows": [
            ("索引名", "Pourbus, Franz, the Younger", "S1（索引 P.csv#185）"),
            ("正文姓名形式", "Franz Pourbus the Younger", "S2（第7章 p.174）"),
        ],
        "description_zh": "本卡按全书索引和第7章p.174登记画家Franz Pourbus the Younger；姓名限定语the Younger依照书内形式保留。",
        "description_en": "This card registers the painter Franz Pourbus the Younger under the index and chapter 7, p.174 forms; the qualifier the Younger is retained as given in the book.",
        "context_zh": "Haskell称Marie de Medici召Pourbus赴巴黎；他于1609年到达，并为Marie及其宫廷绘制多幅肖像。相关S2候选均保留待S6。",
        "context_en": "Haskell says Marie de Medici summoned Pourbus to Paris; he arrived in 1609 and painted many portraits of Marie and the court. The related S2 candidates remain for S6.",
        "relation_ids": ["st-chp7-p174-i19", "st-chp7-p174-i20", "st-chp7-p174-i21"],
        "endpoints": {
            "st-chp7-p174-i19": ("cand-1631", "cand-1983", "summoned_pourbus_to_paris"),
            "st-chp7-p174-i20": ("cand-1983", "cand-4653", "arrived_in_paris_in_1609"),
            "st-chp7-p174-i21": ("cand-1983", "cand-6686", "painted_portraits_of_marie_and_court"),
        },
    },
    {
        "candidate": "cand-2312", "index_entry": "S.csv#0", "canonical_name": "Sacchetti, Giovanni Francesco",
        "group": "new-person:francesco-giovanni-sacchetti-e5e90628e9",
        "ku": "units/persons/giovanni-francesco-sacchetti", "card": "04-knowledge/units/persons/giovanni-francesco-sacchetti.md",
        "name_zh": "乔瓦尼·弗朗切斯科·萨凯蒂", "name_en": "Giovanni Francesco Sacchetti",
        "body_sources": [{
            "location": "第7章；印刷页180",
            "summary": "Haskell称Giovanni Francesco Sacchetti注意到Mazarin在瓦尔泰利纳的外交才能，并称Giovanni Francesco是Giulio与Marcello Sacchetti的兄弟。",
            "quote": "Giovanni Francesco Sacchetti, brother of Giulio and Marcello", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "source_span": "lines 133-134; print p.180",
        }],
        "name_rows": [
            ("索引名", "Sacchetti, Giovanni Francesco", "S1（索引 S.csv#0）"),
            ("正文姓名形式", "Giovanni Francesco Sacchetti", "S2（第7章 p.180）"),
        ],
        "description_zh": "本卡按全书索引和第7章p.180的完整姓名登记Giovanni Francesco Sacchetti；只记录书内身份，不补写其生平。",
        "description_en": "This card registers Giovanni Francesco Sacchetti under the full name in the index and chapter 7, p.180. It records the book-based identity only and adds no biography.",
        "context_zh": "Haskell称Mazarin在瓦尔泰利纳的外交才能引起Sacchetti注意，并明确称Giovanni Francesco为Giulio和Marcello Sacchetti的兄弟。",
        "context_en": "Haskell says Mazarin’s diplomatic ability in Valtellina attracted Sacchetti’s attention and explicitly identifies Giovanni Francesco as brother to Giulio and Marcello Sacchetti.",
        "relation_ids": ["st-chp7-p180-i09", "st-chp7-p180-i10", "st-chp7-p180-i11"],
        "endpoints": {
            "st-chp7-p180-i09": ("cand-1588", "cand-2312", "mazarin_diplomatic_ability_attracted_giovanni_francesco_sacchetti"),
            "st-chp7-p180-i10": ("cand-2312", "cand-2313", "giovanni_francesco_sacchetti_was_brother_of_giulio_sacchetti"),
            "st-chp7-p180-i11": ("cand-2312", "cand-2314", "giovanni_francesco_sacchetti_was_brother_of_marcello_sacchetti"),
        },
    },
]


def make_card(t: dict) -> str:
    index_file = t["index_entry"].split("#", 1)[0]
    index_path = f"02-sources/03-Index/03-2-Index-CSV/{index_file}"
    sources = [{
        "citation": INDEX_CITATION, "location": f"全书索引 {t['index_entry']}",
        "sentence_summary": f"索引以“{t['canonical_name']}”列出此人。",
        "original_quotes": [{"source_span": t["index_entry"], "text": t["canonical_name"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": index_path, "source_span": t["index_entry"]},
    }]
    for source in t["body_sources"]:
        sources.append({
            "citation": HASKELL_CITATION, "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["source_span"], "text": source["quote"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source["source_file"], "source_span": source["source_span"]},
        })
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"],
        "type": "person", "evidence_status": "source_backed", "sources": sources,
        "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    name_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in t["name_rows"])
    relation_ids = ", ".join(t["relation_ids"])
    return (
        f"---\n{fm}\n---\n\n## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}\n\n**English:** {t['description_en']}\n\n"
        f"### 名称\n\n| 字段 | 值 | 证据 |\n|---|---|---|\n{name_rows}\n\n"
        f"### 本书语境\n\n**中文：** {t['context_zh']} 直接S2关系候选{relation_ids}保留待S6；本批不据身份登记裁定关系。\n\n"
        f"**English:** {t['context_en']} The direct S2 relation candidates {relation_ids} remain for S6; this registration makes no relation decision.\n\n"
        "## 关系与证据\n\n### 关系记录\n\n"
        "当前没有正式关系。正文中的导航与线索不自动形成关系边。\n\n"
        f"**中文：** 直接S2关系候选{relation_ids}保留待S6逐条裁决；本批不新增正式关系。\n\n"
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
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {r["statement_id"]: r for r in statements}
    cards = {t["card"]: make_card(t) for t in TARGETS}
    card_paths = {t["card"]: ROOT / t["card"] for t in TARGETS}

    for t in TARGETS:
        candidate = candidate_by_id[t["candidate"]]
        alignment = alignment_by_id[t["candidate"]]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("index_entry_id") == t["index_entry"]
        assert candidate.get("canonical_name") == t["canonical_name"]
        assert base.sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        if alignment.get("ku_id"):
            assert alignment.get("decision") == "new" and alignment.get("ku_id") == t["ku"]
        else:
            assert alignment.get("decision") == "new"
            assert t["ku"] not in manifest_by_ku
            assert t["card"] not in accepted_paths and not card_paths[t["card"]].exists()
        members = [
            r["candidate_id"] for r in alignments
            if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new"
            and base.sync.get_group(r.get("resolution_note", "")) == t["group"]
        ]
        assert members == [t["candidate"]], (t["group"], members)
        direct = {
            r["statement_id"] for r in statements
            if (r.get("qualifiers") or {}).get("relation_candidate") is True
            and (r.get("subject_candidate_id") == t["candidate"] or r.get("object_candidate_id") == t["candidate"])
        }
        assert direct == set(t["endpoints"]), (t["candidate"], sorted(direct), sorted(t["endpoints"]))
        for sid, endpoints in t["endpoints"].items():
            row = statement_by_id[sid]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == endpoints
        idx = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / t["index_entry"].split("#", 1)[0]
        assert t["canonical_name"] in idx.read_text(encoding="utf-8-sig")
        for source in t["body_sources"]:
            source_text = (ROOT / source["source_file"]).read_text(encoding="utf-8-sig")
            normalized = re.sub(r"\s+", " ", source_text)
            quote = re.sub(r"\s+", " ", source["quote"])
            assert quote in normalized, (t["candidate"], source["source_span"], source["quote"])

    pending = [t for t in TARGETS if not alignment_by_id[t["candidate"]].get("ku_id")]
    if not pending:
        for t in TARGETS:
            assert alignment_by_id[t["candidate"]].get("ku_id") == t["ku"]
            assert card_paths[t["card"]].read_text(encoding="utf-8-sig") == cards[t["card"]]
            assert t["card"] in accepted_paths
            assert manifest_by_ku[t["ku"]].get("card_path") == t["card"]
        print("ALREADY REGISTERED: five person groups and five candidate mappings are present.")
        return 0
    assert len(pending) == len(TARGETS), [t["candidate"] for t in pending]

    before_stats = sync.summarize_by_type(candidates, alignments)
    planned_alignments = [dict(r) for r in alignments]
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        row = next(r for r in planned_alignments if r.get("candidate_id") == t["candidate"] and not r.get("external_source"))
        row["ku_id"] = t["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += f" S4 registration: preserved S3 singleton group {t['group']} -> {t['ku']}; source-local registration only; no external identity was added and direct relations remain for S6."
        planned_manifest.append({
            "ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"],
            "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"],
        })
        planned_accepted = helper.base.insert_accepted(planned_accepted, t["card"])
    planned_manifest.sort(key=lambda r: r["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(r[key] for r in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(r[key] for r in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == before_totals["registered_members"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    additions, cards_with_tables = extract_card_fields(cards)
    assert cards_with_tables == len(TARGETS) and len(additions) == 2 * len(TARGETS)
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Guidiccioni、Malpighi、Gambarini、Pourbus、Sacchetti（{DATE}）\n\n"
    for t in TARGETS:
        relations = "、".join(t["relation_ids"])
        process_text += (
            f"- {t['candidate']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）](../../../04-knowledge/units/persons/{t['ku'].split('/', 2)[2]}.md)。"
            f"以索引{t['index_entry']}和所列正文姓名／语境建立书内身份锚点；直接S2关系候选{relations}留待S6逐条裁决。本批不查验外部身份记录，不新增正式关系。\n"
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
        f"\n\n### S4人物直接端点登记：Guidiccioni、Malpighi、Gambarini、Pourbus、Sacchetti（{DATE}）\n\n"
        "登记5个已有S3 new单成员人物组，各组对应一个KU；候选映射保留原S3分组号。名称及描述依据全书索引和对应正文。"
        f"本批未查验外部人物规范记录，未新增关系；{relation_count}条直接S2关系候选保留待S6逐条裁决。"
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
