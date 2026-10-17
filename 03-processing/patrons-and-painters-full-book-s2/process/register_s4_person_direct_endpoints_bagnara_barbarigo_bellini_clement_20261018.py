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
ANCHOR = "s4-person-direct-endpoints-bagnara-barbarigo-bellini-clement-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

TARGETS = [
    {
        "primary": "cand-0160", "members": ["cand-0160"], "index_entry": "B.csv#7",
        "index_name": "Bagnara, Duchess of", "index_pages": "209",
        "canonical_name": "Bagnara, Duchess of", "group": "new-person:bagnara-duchess-of-4e303ad55f",
        "ku": "units/persons/duchess-of-bagnara", "card": "04-knowledge/units/persons/duchess-of-bagnara.md",
        "name_zh": "巴尼亚拉公爵夫人", "name_en": "Duchess of Bagnara",
        "name_rows": [
            ("索引名", "Bagnara, Duchess of", "S1（索引 B.csv#7）"),
            ("正文称谓", "the Duchess of Bagnara", "S2（第8章 p.209）"),
        ],
        "sources": [{
            "location": "第8章；印刷页209",
            "summary": "Haskell称Ruffo的母亲巴尼亚拉公爵夫人为他建造了宫殿；本段没有提供该人物的个人姓名，也未给宫殿专名。",
            "quote": "which his mother, the Duchess of Bagnara, had built for him.",
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "source_span": "line 67; print p.209",
        }],
        "description_zh": "本卡登记全书索引和第8章p.209所称的巴尼亚拉公爵夫人。原书此处未提供其个人姓名，故以有据称谓标识，不补造姓名。",
        "description_en": "This card registers the person called the Duchess of Bagnara in the index and chapter 8, p.209. The passage supplies no personal name, so the source appellation is retained without inventing one.",
        "context_zh": "Haskell称她是Ruffo的母亲，并称她为Ruffo建造了宫殿；该段没有给出宫殿名称。此项直接S2关系候选仍待S6。",
        "context_en": "Haskell identifies her as Ruffo’s mother and says she built the palace for him; the passage does not name the palace. This direct S2 relation candidate remains for S6.",
        "relation_ids": ["st-chp8-p209-ruffo-mother-built-palace"],
        "endpoints": {"st-chp8-p209-ruffo-mother-built-palace": ("cand-0160", "cand-7467", "duchess_of_bagnara_built_ruffos_palace_for_him")},
    },
    {
        "primary": "cand-0183", "members": ["cand-0183"], "index_entry": "B.csv#30",
        "index_name": "Barbarigo, Pietro", "index_pages": "254",
        "canonical_name": "Barbarigo, Pietro", "group": "new-person:affiliations-barbarigo-pietro-political-s--c55fc905b5",
        "ku": "units/persons/pietro-barbarigo", "card": "04-knowledge/units/persons/pietro-barbarigo.md",
        "name_zh": "皮耶特罗·巴尔巴里戈", "name_en": "Pietro Barbarigo",
        "name_rows": [
            ("索引名", "Barbarigo, Pietro", "S1（索引 B.csv#30）"),
            ("正文姓名形式", "Pietro Barbarigo", "S2（第9章 p.254）"),
        ],
        "sources": [{
            "location": "第9章；印刷页254",
            "summary": "Haskell称Pietro Barbarigo是极端天主教派的重要成员，并称他的侄辈被纳入Tiepolo于1745年为他绘制的《Strength protecting Wisdom》壁画。注释所引研究未在本批独立查阅。",
            "quote": "Pietro Barbarigo, the leading member of the extreme Catholic faction",
            "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md", "source_span": "line 143; print p.254",
        }],
        "description_zh": "本卡按索引B.csv#30与第9章p.254登记Pietro Barbarigo；身份与活动范围仅据本书记载。",
        "description_en": "This card registers Pietro Barbarigo under index B.csv#30 and chapter 9, p.254. His identity and activity are recorded from this book only.",
        "context_zh": "Haskell称Barbarigo为极端天主教派的重要成员，并称Tiepolo于1745年为他绘制的《Strength protecting Wisdom》中包括其侄辈。侄辈未具名；相关直接关系候选仍待S6。",
        "context_en": "Haskell describes Barbarigo as a leading member of the extreme Catholic faction and says his nephews appeared in Tiepolo’s 1745 Strength protecting Wisdom fresco painted for him. The nephews are unnamed; the direct relation candidate remains for S6.",
        "relation_ids": ["st-chp9-p254-barbarigo-nephews-in-strength-fresco"],
        "endpoints": {"st-chp9-p254-barbarigo-nephews-in-strength-fresco": ("cand-0183", "cand-8314", "pietro_barbarigo_had_nephews_included_in_tiepolo_fresco_in_1745")},
    },
    {
        "primary": "cand-0270", "members": ["cand-0270"], "index_entry": "B.csv#117",
        "index_name": "Bellini, Giovanni", "index_pages": "380, 410",
        "canonical_name": "Bellini, Giovanni", "group": "new-person:bellini-giovanni-b88f43a625",
        "ku": "units/persons/giovanni-bellini", "card": "04-knowledge/units/persons/giovanni-bellini.md",
        "name_zh": "乔瓦尼·贝利尼", "name_en": "Giovanni Bellini",
        "name_rows": [
            ("索引名", "Bellini, Giovanni", "S1（索引 B.csv#117）"),
            ("正文姓氏形式", "Bellini", "S2（第17章 p.380；第20章 p.410）"),
        ],
        "sources": [
            {
                "location": "第17章；印刷页380",
                "summary": "Haskell称Manfrin收藏中的威尼斯绘画以Mantegna与Bellini开头，并延及后世画家。",
                "quote": "The Venetian pictures began with Mantegna and Bellini",
                "source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_span": "line 12; print p.380",
            },
            {
                "location": "第20章后记；印刷页410",
                "summary": "Haskell称Della Lena欣赏Vivarini、Carpaccio与Bellini的“beautiful simplicity”。",
                "quote": "beautiful simplicity’ of Vivarini, Carpaccio and Bellini",
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "source_span": "line 207; print p.410",
            },
        ],
        "description_zh": "本卡按索引B.csv#117将第17章p.380和第20章p.410两处Bellini映射为Giovanni Bellini；索引另将Gentile Bellini列为不同人物。",
        "description_en": "Under index B.csv#117, this card maps the Bellini references on chapter 17, p.380 and chapter 20, p.410 to Giovanni Bellini. The index lists Gentile Bellini separately.",
        "context_zh": "Haskell在Manfrin收藏的威尼斯绘画范围中提到Bellini，并在后记中提到Della Lena对Bellini的赞赏。这里没有识别具体作品；直接S2候选仍待S6。",
        "context_en": "Haskell mentions Bellini among the Venetian painting represented in Manfrin’s collection and later notes Della Lena’s admiration for Bellini. No individual work is identified here; the direct S2 candidate remains for S6.",
        "relation_ids": ["st-chp17-p380-manfrin-collection-represented-bellini"],
        "endpoints": {"st-chp17-p380-manfrin-collection-represented-bellini": ("cand-1513", "cand-0270", "collection_represented_works_by")},
    },
    {
        "primary": "cand-0789", "members": ["cand-0789"], "index_entry": "C.csv#313",
        "index_name": "Clement, Abbé", "index_pages": "344",
        "canonical_name": "Clément, Abbé", "group": "new-person:abbe-clement-abbe-clement-s-d72d932bb3",
        "ku": "units/persons/abbe-clement-zanetti-description", "card": "04-knowledge/units/persons/abbe-clement-zanetti-description.md",
        "name_zh": "克莱芒（Abbé Clement）", "name_en": "Abbé Clement",
        "name_rows": [
            ("索引名", "Clement, Abbé", "S1（索引 C.csv#313）"),
            ("正文称谓", "Abbé Clement", "S2（第13章 p.344）"),
        ],
        "sources": [
            {
                "location": "第13章；印刷页344",
                "summary": "Haskell把对Zanetti的“fameux amateur, et un peu marchand d’antiquités”描述归于Abbé Clement。",
                "quote": "the Abbé Clement’s description of Zanetti",
                "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md", "source_span": "line 118; print p.344",
            },
            {
                "location": "第13章；印刷页344注2",
                "summary": "该注释列出简写引文“P. Clement, p.124”；本批未独立查阅该书，也不据此扩写个人全名。",
                "quote": "2 P. Clement, p. 124.",
                "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md", "source_span": "line 240; print p.344 n.2",
            },
        ],
        "description_zh": "本卡登记原书索引及第13章p.344所称的Abbé Clement。原书没有在此提供其个人全名；路径用于区分这一书内引用身份，不代表外部人物身份已确认。",
        "description_en": "This card registers the Abbé Clement named in the index and chapter 13, p.344. The book does not supply a personal full name here; the path distinguishes this source-local cited identity and does not claim external identification.",
        "context_zh": "Haskell将有关Zanetti的评价归于Abbé Clement，原文保留“un peu”的限定；第13章p.344注2简引P. Clement, p.124，所引原书未在本批查阅。直接S2候选留待S6。",
        "context_en": "Haskell attributes the description of Zanetti to Abbé Clement and retains the qualification “un peu.” Chapter 13, p.344 n.2 cites P. Clement, p.124 in short form; that work was not consulted in this batch. The direct S2 candidate remains for S6.",
        "relation_ids": ["st-chp13-p344-clement-description_of_zanetti"],
        "endpoints": {"st-chp13-p344-clement-description_of_zanetti": ("cand-0789", "cand-2838", "described_as_famous_amateur_and_somewhat_an_antique_dealer")},
    },
]


def make_card(target: dict) -> str:
    sources = []
    index_file, index_id = target["index_entry"].split("#", 1)
    sources.append({
        "citation": INDEX_CITATION,
        "location": f"全书索引 {target['index_entry']}",
        "sentence_summary": f"索引以“{target['index_name']}”列出此人并定位至第{target['index_pages']}页。",
        "original_quotes": [{"source_span": target["index_entry"], "text": target["index_name"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/03-Index/03-2-Index-CSV/{index_file}",
            "source_span": target["index_entry"],
        },
    })
    for source in target["sources"]:
        sources.append({
            "citation": HASKELL_CITATION, "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["source_span"], "text": source["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters", "source_file": source["source_file"],
                "source_span": source["source_span"],
            },
        })
    frontmatter = {
        "title": f"{target['name_zh']}（{target['name_en']}）", "name_en": target["name_en"],
        "type": "person", "evidence_status": "source_backed", "sources": sources,
        "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    name_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in target["name_rows"])
    relations = ", ".join(target["relation_ids"])
    return (
        f"---\n{fm}\n---\n\n## 内容\n\n### 描述\n\n"
        f"**中文：** {target['description_zh']}\n\n**English:** {target['description_en']}\n\n"
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
    with tempfile.TemporaryDirectory(prefix="pnp-s4-bagnara-barbarigo-bellini-clement-") as temp_root:
        temp_base = Path(temp_root)
        rows = []
        for target in TARGETS:
            temp_card = temp_base / target["card"]
            temp_card.parent.mkdir(parents=True, exist_ok=True)
            temp_card.write_text(cards[target["card"]], encoding="utf-8")
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
        if tmp.exists():
            tmp.unlink()


def with_bom(text: str, original: bytes | None = None) -> bytes:
    raw = text.encode("utf-8")
    return b"\xef\xbb\xbf" + raw if original is None or original.startswith(b"\xef\xbb\xbf") else raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four source-local person groups with direct relation candidates.")
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
    all_members = [candidate_id for target in TARGETS for candidate_id in target["members"]]
    assert len(all_members) == len(set(all_members))

    for target in TARGETS:
        for candidate_id in target["members"]:
            candidate, alignment = candidate_by_id[candidate_id], alignment_by_id[candidate_id]
            assert candidate.get("suggested_type") == "person"
            assert alignment.get("decision") == "new"
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
        assert sorted(group_members) == sorted(target["members"]), (target["group"], group_members, target["members"])
        main_candidate = candidate_by_id[target["primary"]]
        assert main_candidate.get("index_entry_id") == target["index_entry"]
        assert main_candidate.get("canonical_name") == target["canonical_name"]
        assert main_candidate.get("index_page_range") == target["index_pages"]
        index_file, index_id = target["index_entry"].split("#", 1)
        index_lines = (ROOT / "02-sources/03-Index/03-2-Index-CSV" / index_file).read_text(encoding="utf-8-sig").splitlines()
        csv_row = next(csv.reader([index_lines[int(index_id) + 1]]))
        assert csv_row[0].strip('"') == target["index_name"], (target["index_entry"], csv_row)
        assert target["index_pages"] in csv_row[-1]
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
            source_text = (ROOT / source["source_file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", source["quote"]) in re.sub(r"\s+", " ", source_text), (target["primary"], source["source_span"])

    pending = [target for target in TARGETS if not all(alignment_by_id[cid].get("ku_id") for cid in target["members"])]
    if not pending:
        for target in TARGETS:
            assert all(alignment_by_id[cid].get("ku_id") == target["ku"] for cid in target["members"])
            assert card_paths[target["card"]].read_text(encoding="utf-8-sig") == cards[target["card"]]
            assert target["card"] in accepted_paths and manifest_by_ku[target["ku"]].get("card_path") == target["card"]
        print("ALREADY REGISTERED: four person groups and four candidate mappings are present.")
        return 0
    assert len(pending) == len(TARGETS)

    before_stats = sync.summarize_by_type(candidates, alignments)
    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for target in TARGETS:
        for candidate_id in target["members"]:
            row = next(item for item in planned_alignments if item.get("candidate_id") == candidate_id and not item.get("external_source"))
            row["ku_id"] = target["ku"]
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] += (
                f" S4 registration: group {target['group']} -> {target['ku']}; "
                "source-local registration only; no external identity was added and direct relation candidates remain for S6."
            )
        planned_manifest.append({
            "ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"],
            "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"],
        })
        planned_accepted = helper.base.insert_accepted(planned_accepted, target["card"])
    planned_manifest.sort(key=lambda row: row["ku_id"])
    before_stats = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    group_count, member_count = len(TARGETS), len(all_members)
    assert totals["registered_groups"] == before_totals["registered_groups"] + group_count
    assert totals["registered_members"] == before_totals["registered_members"] + member_count
    assert totals["pending_groups"] == before_totals["pending_groups"] - group_count
    assert totals["pending_members"] == before_totals["pending_members"] - member_count
    assert len(planned_manifest) == len(manifest) + group_count

    additions, cards_with_tables = extract_card_fields(cards)
    assert cards_with_tables == group_count and len(additions) == 2 * group_count
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物直接关系端点登记：Bagnara、Barbarigo、Bellini、Clément（{DATE}）\n\n"
    for target in TARGETS:
        ids = "、".join(target["relation_ids"])
        process_text += (
            f"- {target['primary']}（{target['group']}）→ [{target['name_zh']}（{target['name_en']}）]"
            f"(../../../04-knowledge/units/persons/{target['ku'].split('/', 2)[2]}.md)。"
            f"索引{target['index_entry']}与指定正文页段构成书内身份依据；S2直接关系候选{ids}留待S6。"
            "个人姓名未由原书提供的对象保留原称谓；本批未查验外部身份记录，不新增正式关系。\n"
        )
    relation_count = sum(len(target["relation_ids"]) for target in TARGETS)
    process_text += (
        f"\n本批登记{group_count}个S3 new人物组和{member_count}条候选映射，新增{len(additions)}条source_backed名称字段；"
        "不添加外部身份标识、候选、来源或正式关系。4条直接S2关系候选留待S6。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物直接关系端点登记：Bagnara、Barbarigo、Bellini、Clément（{DATE}）\n\n"
        "登记4个已有S3 new人物组，各组各映射一个候选到一个KU。巴尼亚拉公爵夫人与Abbé Clement保留原书称谓，不补造个人全名；"
        "Giovanni Bellini与Gentile Bellini分开。4条直接S2关系候选仍待S6逐条裁决；本批未查验外部身份记录或新增正式关系。"
        f"KU={len(planned_manifest)}，新增名称字段={len(additions)}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-bagnara-barbarigo-bellini-clement-") as temp_name:
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
        for target in TARGETS:
            writes[card_paths[target["card"]]] = with_bom(cards[target["card"]])

    if args.dry_run:
        print(f"S4 dry-run passed: groups={group_count}; candidate_mappings={member_count}; source_backed_name_fields={len(additions)}; direct_relation_candidates={relation_count}.")
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
                if path.exists(): path.unlink()
            else:
                atomic_write(path, content)
        raise
    print(f"applied: groups={group_count}; candidate_mappings={member_count}; name_fields={len(additions)}; relation_candidates={relation_count}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
