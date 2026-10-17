from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

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
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-person-admiral-byng-identity-group-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
GROUP = "new-person:admiral-byng-817cd89b59"
MEMBERS = ["cand-0475", "cand-7301"]
KU = "units/persons/admiral-byng"
CARD = "04-knowledge/units/persons/admiral-byng.md"
IDENTITY_STATEMENT = "st-chp7-p200-n5-binchs-identified-byng"
RELATION_IDS = [
    "st-chp7-p200-n5-binchs-return-naples",
    "st-chp7-p200-n5-byng-fleet-command",
    "st-chp7-p200-v-paolo-works-for-binchs-and-daun",
]
BT = chr(96)

helper.DATE = DATE
helper.PROCESS_REF = PROCESS_REF


def extract_card_fields(card: str) -> tuple[list[dict], dict, list[str], int]:
    from scripts import build_field_facts
    from scripts.build_field_facts import extract_records

    with tempfile.TemporaryDirectory(prefix="pnp-s4-byng-") as temp_root:
        temp_base = Path(temp_root)
        temp_card = temp_base / CARD
        temp_card.parent.mkdir(parents=True, exist_ok=True)
        temp_card.write_text(card, encoding="utf-8")
        previous_base = build_field_facts.BASE
        build_field_facts.BASE = temp_base
        try:
            return extract_records([{"ku_id": KU, "card_path": CARD}])
        finally:
            build_field_facts.BASE = previous_base

TARGET = {
    "candidate": "cand-0475",
    "members": MEMBERS,
    "group": GROUP,
    "ku": KU,
    "card": CARD,
    "name_zh": "拜恩海军上将",
    "name_en": "Admiral Byng",
    "name_field": "索引名",
    "index_entries": [
        {"entry": "B.csv#323", "file": "B.csv", "name": "Byng, Admiral", "page": "200n"}
    ],
    "source_fragments": [
        "working for the English Admiral ‘Binchs’",
        "must be Admiral Byng, as from 1718 Commander of the British fleet in the Mediterranean",
        "back in Naples in 1719",
    ],
    "book_sources": [
        {
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
            "source_span": "line 13; print p. 200",
            "location": "第7章 p.200；OCR L13",
            "summary": "正文称那不勒斯被攻占后，Paolo de Matteis为‘English Admiral “Binchs”’工作；这段文字没有把具体委托、作品或合同逐项说明。",
            "quote": "and he found himself working for the English Admiral ‘Binchs’ and the Austrian commander Count Daun",
        },
        {
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
            "source_span": "line 67; print p. 200, footnote 5; PDF physical p. 38",
            "location": "第7章 p.200 注5；OCR L67；PDF物理第38页",
            "summary": "Haskell称‘Binchs’必定是Admiral Byng，并称其自1718年起任地中海英国舰队司令；同注报告‘Binchs’于1719年已回那不勒斯。身份识别是作者推断，被引来源未在本任务中另行核验。",
            "quote": "must be Admiral Byng, as from 1718 Commander of the British fleet in the Mediterranean",
        },
    ],
    "description_zh": (
        "本卡按全书索引主项“Byng, Admiral”记录书中称为Admiral Byng的人物。正文另以来源拼写‘Admiral “Binchs”’称呼他；"
        "Haskell在第7章p.200注5明确将‘Binchs’认作Admiral Byng。这是书内作者推断，未作外部身份核验；索引未提供名字。中文名为工作音译。"
    ),
    "description_en": (
        "This card records the person indexed as “Byng, Admiral” and called Admiral Byng in the book. The text also uses the source form “Admiral ‘Binchs’”; "
        "in Chapter 7, p.200, note 5, Haskell identifies “Binchs” as Admiral Byng. This is the author’s inference within the book, not an externally verified identity; "
        "the index does not give a personal name. The Chinese rendering is a working transliteration."
    ),
    "relation_ids": RELATION_IDS,
    "relation_context_zh": (
        "第7章p.200将三项陈述分别留存：注5报告‘Binchs’于1719年已回那不勒斯，并称Admiral Byng自1718年起指挥地中海英国舰队；"
        "正文称Paolo de Matteis在那不勒斯被攻占后为这位英国海军上将工作。均为Haskell的书内陈述，具体履历或关系解释留待S6审查。"
    ),
    "relation_context_en": (
        "Chapter 7, p.200, preserves three separate statements: note 5 reports that “Binchs” had returned to Naples by 1719 and describes Admiral Byng as "
        "commander of the British fleet in the Mediterranean from 1718; the main text says Paolo de Matteis worked for this English admiral after Naples was captured. "
        "These remain statements in Haskell’s book; their specific biographical or relational interpretation awaits S6 review."
    ),
    "statement_endpoints": [
        (
            "st-chp7-p200-n5-binchs-return-naples",
            "cand-7301",
            "cand-3534",
            "reported_back_in_naples_by_1719",
            "back in Naples in 1719",
        ),
        (
            "st-chp7-p200-n5-byng-fleet-command",
            "cand-0475",
            "cand-7354",
            "described_as_commander_of",
            "as from 1718 Commander of the British fleet in the Mediterranean",
        ),
        (
            "st-chp7-p200-v-paolo-works-for-binchs-and-daun",
            "cand-1581",
            "cand-7301",
            "worked_for_after_conquest",
            "working for the English Admiral ‘Binchs’",
        ),
    ],
}


def make_card() -> str:
    card = helper.make_card(TARGET)
    index_row = "| 索引名 | Byng, Admiral | S1（索引 B.csv#323） |"
    alias_row = "| 别名 | Admiral ‘Binchs’ | S2（第7章 p.200，正文） |"
    assert index_row in card
    card = card.replace(index_row, index_row + "\n" + alias_row, 1)
    assert card.count("| 别名 | Admiral ‘Binchs’ | S2（第7章 p.200，正文） |") == 1
    return card


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the reconciled Admiral Byng S3 person group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    base = helper.base
    alignment_fields, alignments = base.sync.read_csv(ALIGNMENT_PATH)
    _, candidates = base.sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = base.sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    assert len(candidate_by_id) == len(alignment_by_id)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [
        json.loads(line)
        for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statement_by_id = {row["statement_id"]: row for row in statements}
    before_stats = base.sync.summarize_by_type(candidates, alignments)

    for candidate_id in MEMBERS:
        candidate = candidate_by_id[candidate_id]
        alignment = alignment_by_id[candidate_id]
        assert candidate.get("suggested_type") == "person"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert base.sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_members = [
        row["candidate_id"]
        for row in alignments
        if row.get("candidate_id")
        and not row.get("external_source")
        and row.get("decision") == "new"
        and base.sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert set(group_members) == set(MEMBERS), group_members
    index_row = base.read_index_rows("B.csv")[323]
    assert index_row.get("Main Entry") == "Byng, Admiral" and index_row.get("Page Numbers", "") == "200n"
    source_text = (ROOT / TARGET["book_sources"][0]["source_file"]).read_text(encoding="utf-8-sig")
    normalized_source = re.sub(r"\s+", " ", source_text)
    assert all(re.sub(r"\s+", " ", fragment) in normalized_source for fragment in TARGET["source_fragments"])
    assert re.sub(r"\s+", " ", TARGET["book_sources"][1]["quote"]) in normalized_source
    assert not (ROOT / CARD).exists()
    assert KU not in manifest_by_ku and CARD not in accepted_paths
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en") or "").casefold() == TARGET["name_en"].casefold()
        for row in manifest
    )
    assert statement_by_id[IDENTITY_STATEMENT]["qualifiers"].get("relation_candidate") is False

    direct = {
        row["statement_id"]
        for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and (row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS)
    }
    expected_direct = {row[0] for row in TARGET["statement_endpoints"]}
    assert direct == expected_direct, (direct, expected_direct)
    for statement_id, subject, obj, predicate, quote_fragment in TARGET["statement_endpoints"]:
        statement = statement_by_id[statement_id]
        assert statement.get("subject_candidate_id") == subject and statement.get("object_candidate_id") == obj
        assert statement.get("predicate") == predicate
        assert quote_fragment in statement.get("original_quote", "")

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for candidate_id in MEMBERS:
        alignment = next(
            row for row in planned_alignments
            if row.get("candidate_id") == candidate_id and not row.get("external_source")
        )
        alignment["ku_id"] = KU
        alignment["process_ref"] = PROCESS_REF
        alignment["resolution_note"] += (
            f" S4登记（{DATE}）：身份组{GROUP}映射至{KU}；原书身份识别归因于Haskell，未作外部身份核验。"
            "直接关系/履历候选保留待S6，本次不创建formal relations。"
        )
    planned_manifest.append(
        {
            "ku_id": KU,
            "type": "person",
            "canonical_name": TARGET["name_zh"],
            "name_en": TARGET["name_en"],
            "source_task": TASK,
            "card_path": CARD,
        }
    )
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = helper.base.insert_accepted(accepted_lines, CARD)
    assert len(planned_manifest) == len(manifest) + 1
    assert len({line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")}) == len(accepted_paths) + 1

    stats = base.sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(item[key] for item in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert stats["person"]["registered_groups"] == before_stats["person"]["registered_groups"] + 1
    assert stats["person"]["registered_members"] == before_stats["person"]["registered_members"] + 2
    assert stats["person"]["pending_groups"] == before_stats["person"]["pending_groups"] - 1
    assert stats["person"]["pending_members"] == before_stats["person"]["pending_members"] - 2
    assert totals["registered_groups"] == before_totals["registered_groups"] + 1
    assert totals["registered_members"] == before_totals["registered_members"] + 2
    assert totals["pending_groups"] == before_totals["pending_groups"] - 1
    assert totals["pending_members"] == before_totals["pending_members"] - 2

    card = make_card()
    card_frontmatter = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert card_frontmatter and isinstance(base.yaml.safe_load(card_frontmatter.group(1)), dict)
    process_text = base.process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物：Admiral Byng身份组登记（{DATE}）\n\n"
        f"`cand-0475`与`cand-7301`共用S3身份组`{GROUP}`，登记为一个人物KU："
        f"[拜恩海军上将（Admiral Byng）](../../../{CARD})。卡片分别记录索引名‘Byng, Admiral’与正文来源拼写‘Admiral ‘Binchs’’；"
        "注5对两者的识别作为Haskell的推断保留，未写作外部核验结论。两条名称字段各有对应索引或正文证据。"
        f"S2关系/履历候选{', '.join(f'`{sid}`' for sid in RELATION_IDS)}留待S6；"
        f"`{IDENTITY_STATEMENT}`已在S3作为身份证据关闭，不进入formal relations。\n\n"
        f"本批登记1个S3 new人物组、2条候选映射；不添加外部身份事实或formal relations。"
        f"登记后人物类型S4为{base.sync.fmt(stats['person']['registered_groups'])}组/"
        f"{base.sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{base.sync.fmt(stats['person']['pending_groups'])}组/{base.sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{base.sync.fmt(totals['registered_groups'])}组/{base.sync.fmt(totals['registered_members'])}条已登记、"
        f"{base.sync.fmt(totals['pending_groups'])}组/{base.sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )

    result_text = base.sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    with ENRICHMENT_PATH.open(encoding="utf-8-sig") as handle:
        existing_enrichment_text = handle.read()
    existing_enrichment = [json.loads(line) for line in existing_enrichment_text.splitlines() if line.strip()]
    # Extract structured name rows from the exact proposed card without writing to the workspace.
    additions, source_registry, warnings, cards_with_tables = extract_card_fields(card)
    assert cards_with_tables == 1 and len(additions) == 2
    assert {row.get("field") for row in additions} == {"索引名", "别名"}
    assert all(row.get("source_ref") in {"S1", "S2"} for row in additions)
    assert all(row.get("source_ids") == ["haskell-1980-rev-ed"] for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert set(source_registry) == {"haskell-1980-rev-ed"}
    assert not warnings, warnings
    natural_keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id")) for row in existing_enrichment}
    existing_ids = {row.get("enrichment_id", "") for row in existing_enrichment}
    max_id = max(
        (int(match.group(1)) for value in existing_ids if (match := re.fullmatch(r"enr-(\d+)", value))),
        default=0,
    )
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + offset:05d}"
        key = (row["ku_id"], row["field"], row["value"], row.get("source_id", ""))
        assert key not in natural_keys and row["enrichment_id"] not in existing_ids

    result_text, count = re.subn(
        r"^\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$",
        f"| [既有字段表](../tables/enrichment.jsonl) | {base.sync.fmt(len(existing_enrichment) + len(additions))}条，其中1,615条 unverified |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert count == 1
    result_text += (
        f"\n\n### S4人物身份组登记：Admiral Byng（{DATE}）\n\n"
        f"`cand-0475`、`cand-7301` → [`{KU}`](../units/persons/admiral-byng.md)。"
        "一张卡、两条S3成员映射；登记索引名与书内来源别名各一条enrichment。"
        "书内身份推断未转写为外部身份验证，三项实质候选留待S6，身份断言已作为S3证据关闭。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: group={GROUP}; members={len(MEMBERS)}; card={CARD}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"enrichment={len(existing_enrichment)}->{len(existing_enrichment)+len(additions)}; "
            f"relation_candidates={len(RELATION_IDS)}; formal_relations_added=0; no files changed"
        )
        return 0

    (ROOT / CARD).write_text(card, encoding="utf-8", newline="\n")
    base.sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    base.sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    with ENRICHMENT_PATH.open("w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(existing_enrichment_text.rstrip("\r\n") + "\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {KU}; members={len(MEMBERS)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; enrichment_rows={len(additions)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
