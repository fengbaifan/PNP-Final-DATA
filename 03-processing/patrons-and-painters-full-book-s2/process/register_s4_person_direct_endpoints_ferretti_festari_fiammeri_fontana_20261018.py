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
ANCHOR = "s4-person-direct-endpoints-ferretti-festari-fiammeri-fontana-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-1026", "entry": "F.csv#41", "index_name": "Ferretti, Gian Domenico",
        "canonical_name": "Ferretti, Gian Domenico", "pages": "299",
        "group": "new-person:domenico-ferretti-gian-23c449bb47", "ku": "units/persons/gian-domenico-ferretti",
        "card": "04-knowledge/units/persons/gian-domenico-ferretti.md",
        "name_zh": "吉安·多梅尼科·费雷蒂", "name_en": "Gian Domenico Ferretti",
        "name_rows": [("索引名", "Ferretti, Gian Domenico", "S1（索引 F.csv#41）"), ("正文姓名形式", "Gian Domenico Ferretti", "S2（第10章 p.299）")],
        "sources": [{
            "location": "第10章；印刷页299", "summary": "Haskell称佛罗伦萨画家Gian Domenico Ferretti绘制了一部再版书籍的卷首插图，该插图尚待雕刻。",
            "quote": "drawn by the ‘famous painter’ Gian Domenico Ferretti of Florence",
            "file": "02-sources/02-Markdown/10_CHP-10_intro.md", "span": "lines 364-365; print p.299",
        }],
        "zh": "本卡依据索引F.csv#41与第10章p.299登记Gian Domenico Ferretti；本书称其为佛罗伦萨画家，并称其绘制卷首插图。",
        "en": "This card registers Gian Domenico Ferretti under index F.csv#41 and chapter 10, p.299; the book calls him a Florentine painter and says he drew a frontispiece.",
        "context_zh": "Haskell称Ferretti绘制Guicciardini《Histories》再版的卷首插图，插图待雕刻；直接S2关系候选留待S6。",
        "context_en": "Haskell says Ferretti drew the frontispiece for a reprint of Guicciardini’s Histories, which was to be engraved; the direct S2 relation candidate remains for S6.",
        "relations": ["st-chp10-p299-publication-obstacles"],
        "endpoints": {"st-chp10-p299-publication-obstacles": ("cand-2440", "cand-1026", "publication_obstacles_and_frontispiece_engraving")},
    },
    {
        "primary": "cand-1032", "entry": "F.csv#47", "index_name": "Festari, Girolamo",
        "canonical_name": "Festari, Girolamo", "pages": "369",
        "group": "new-person:festari-girolamo-bb06b8d193", "ku": "units/persons/girolamo-festari",
        "card": "04-knowledge/units/persons/girolamo-festari.md",
        "name_zh": "吉罗拉莫·费斯塔里", "name_en": "Girolamo Festari",
        "name_rows": [("索引名", "Festari, Girolamo", "S1（索引 F.csv#47）"), ("正文姓名形式", "Girolamo Festari", "S2（第15章 p.369）")],
        "sources": [{
            "location": "第15章；印刷页369", "summary": "Haskell称Girolamo Festari为医生与科学家，并记其1777年陪同Querini出行。",
            "quote": "During the trip he and his companion, the doctor and scientist Girolamo Festari",
            "file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md", "span": "line 53; print p.369",
        }],
        "zh": "本卡依据索引F.csv#47与第15章p.369登记Girolamo Festari；本书称其为医生、科学家，并记其陪同Querini出行。",
        "en": "This card registers Girolamo Festari under index F.csv#47 and chapter 15, p.369; the book identifies him as a doctor and scientist who accompanied Querini on a trip.",
        "context_zh": "Haskell称Festari陪同Querini于1777年赴瑞士旅行；同行期间二人观看绘画与建筑，并谈论当地贸易和工业。两条直接S2关系候选留待S6。",
        "context_en": "Haskell says Festari accompanied Querini to Switzerland in 1777; during the trip they viewed paintings and architecture and discussed local trade and industry. Both direct S2 relation candidates remain for S6.",
        "relations": ["st-chp15-p369-querini-festari-companion-trip", "st-chp15-p369-querini-festari-trip-observations"],
        "endpoints": {
            "st-chp15-p369-querini-festari-companion-trip": ("cand-2075", "cand-1032", "travelled_with_festari_as_companion_in_1777"),
            "st-chp15-p369-querini-festari-trip-observations": ("cand-2075", "cand-1032", "during_trip_admired_art_and_architecture_and_commented_on_trade_and_industry"),
        },
    },
    {
        "primary": "cand-1034", "entry": "F.csv#49", "index_name": "Fiammeri, Giovanni Battista",
        "canonical_name": "Fiammeri, Giovanni Battista", "pages": "67",
        "group": "new-person:battista-fiammeri-giovanni-1df26fcd92", "ku": "units/persons/giovanni-battista-fiammeri",
        "card": "04-knowledge/units/persons/giovanni-battista-fiammeri.md",
        "name_zh": "乔瓦尼·巴蒂斯塔·菲亚梅里", "name_en": "Giovanni Battista Fiammeri",
        "name_rows": [("索引名", "Fiammeri, Giovanni Battista", "S1（索引 F.csv#49）"), ("正文姓名形式", "Giovanni Battista Fiammeri", "S2（第3章 p.67）"), ("注释简称", "Fiammeri", "S2（第3章 p.67注4）")],
        "sources": [{
            "location": "第3章；印刷页67", "summary": "Haskell称耶稣会画家Giovanni Battista Fiammeri主持S. Vitale教堂装饰，工作受总会长Claudio Aquaviva直接控制。",
            "quote": "The decoration was directed by a Jesuit painter Giovanni Battista Fiammeri under the immediate control of the General, Claudio Aquaviva",
            "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md", "span": "lines 25-26; print p.67",
        }],
        "zh": "本卡依据索引F.csv#49与第3章p.67登记耶稣会画家Giovanni Battista Fiammeri；本书称其主持S. Vitale教堂装饰。",
        "en": "This card registers the Jesuit painter Giovanni Battista Fiammeri under index F.csv#49 and chapter 3, p.67; the book says he directed the decoration of S. Vitale.",
        "context_zh": "Haskell称Fiammeri主持S. Vitale教堂装饰，Claudio Aquaviva直接控制该项目并提出建议；个别壁画未命名。直接S2关系候选留待S6。",
        "context_en": "Haskell says Fiammeri directed the decoration of S. Vitale under Claudio Aquaviva’s direct control and with his suggestions; individual frescoes are not named. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp3-secii-l19-31-fiammeri-directed-vitale-decoration"],
        "endpoints": {"st-chp3-secii-l19-31-fiammeri-directed-vitale-decoration": ("cand-1034", "cand-5022", "painter_directed_church_decoration")},
    },
    {
        "primary": "cand-1044", "entry": "F.csv#59", "index_name": "Fontana, Carlo",
        "canonical_name": "Fontana, Carlo", "pages": "165",
        "group": "new-person:carlo-fontana-ca9cdad95d", "ku": "units/persons/carlo-fontana",
        "card": "04-knowledge/units/persons/carlo-fontana.md",
        "name_zh": "卡洛·丰塔纳", "name_en": "Carlo Fontana",
        "name_rows": [("索引名", "Fontana, Carlo", "S1（索引 F.csv#59）"), ("正文姓名形式", "Carlo Fontana", "S2（第6章 p.165）")],
        "sources": [{
            "location": "第6章；印刷页165", "summary": "Haskell称Juvarra的建筑风格受到Carlo Fontana学院派巴洛克风格的影响，并将相关学习期限定为1704至1714年。",
            "quote": "the academic Baroque of Carlo Fontana between 1704 and 1714",
            "file": "02-sources/02-Markdown/06_CHP-6_sec_v.md", "span": "lines 36-37; print p.165",
        }],
        "zh": "本卡依据索引F.csv#59与第6章p.165登记Carlo Fontana；本书在Juvarra的建筑风格语境中提到其学院派巴洛克。",
        "en": "This card registers Carlo Fontana under index F.csv#59 and chapter 6, p.165; the book mentions his academic Baroque in the context of Juvarra’s architectural style.",
        "context_zh": "Haskell称Juvarra在1704至1714年间吸收Carlo Fontana的学院派巴洛克，其建筑风格受到影响。直接S2关系候选留待S6。",
        "context_en": "Haskell says Juvarra absorbed Carlo Fontana’s academic Baroque from 1704 to 1714 and that it affected his architectural style. The direct S2 relation candidate remains for S6.",
        "relations": ["st-chp6-p165-v1-07"],
        "endpoints": {"st-chp6-p165-v1-07": ("cand-1339", "cand-1044", "architectural_style_influenced_by_fontana")},
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
    with tempfile.TemporaryDirectory(prefix="pnp-s4-ferretti-festari-fiammeri-fontana-") as temp_root:
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
    parser = argparse.ArgumentParser(description="Register four source-local person groups with direct S2 endpoints.")
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
        print("ALREADY REGISTERED: four Ferretti/Festari/Fiammeri/Fontana person groups are present.")
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Ferretti、Festari、Fiammeri与Carlo Fontana（{DATE}）\n\n"
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
        f"\n\n### S4人物直接关系端点登记：Ferretti、Festari、Fiammeri与Carlo Fontana（{DATE}）\n\n"
        "登记Gian Domenico Ferretti、Girolamo Festari、Giovanni Battista Fiammeri与Carlo Fontana四个S3 new人物组。名称、描述和语境均限于索引及所引章节；五条直接S2关系候选仍待S6逐条裁决。"
        f"本批无外部身份记录或正式关系；KU={len(planned_manifest)}，名称字段={len(additions)}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-ferretti-festari-fiammeri-fontana-") as temp_name:
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
