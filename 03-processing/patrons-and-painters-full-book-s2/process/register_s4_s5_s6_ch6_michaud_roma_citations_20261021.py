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
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PROCESS_DIR))

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_s5_s6_archive_citations_20261020 as archive_batch
import scripts.build_field_facts as field_facts

TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
RELATIONS_PATH = TABLES / "relations.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
AGENTS_PATH = ROOT / "AGENTS.md"

DATE = "2026-10-21"
ANCHOR = "s4-s5-s6-ch6-michaud-roma-citations-20261021"
CH6 = "02-sources/02-Markdown/06_CHP-6_sec_v.md"
BIB = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
SUBJECT_CANDIDATE = "cand-2962"
SUBJECT_KU = "units/archives/patrons-and-painters"
STATEMENTS = [
    "st-chp6-p162-n7-cite",
    "st-chp6-p163-n1-cite",
    "st-chp6-p163-n3-cite",
    "st-chp6-p163-n4-cite",
]

SPECS = [
    {
        "candidate": "cand-6571",
        "group": "archive-group-06ab78ee5350",
        "ku_id": "units/archives/michaud-louis-xiv-et-innocent-xi-1882-1883",
        "type": "archive",
        "sub_type": "multi-volume book",
        "name_zh": "路易十四与英诺森十一世",
        "name_en": "Louis XIV and Innocent XI",
        "sources": [
            {
                "location": "第21章书目，印刷页430，Markdown L811。",
                "summary": "Haskell 书目列 E. Michaud、原题名、四卷本、Paris 与 1882-3；本卡只登记该书目形式。",
                "source_file": BIB,
                "span": "line 811; printed p. 430",
                "quotes": ["Michaud, E.: Louis XIV et Innocent XI, 4 vols., Paris 1882-3."],
                "link": "[第21章 p.430 书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L811)",
            },
            {
                "location": "第6章，印刷页162注7，Markdown L54。",
                "summary": "注7将一份1683年法国使节报告标为转引自 Michaud 第一卷 p.176；本卡仅记录 Haskell 的引注定位。",
                "source_file": CH6,
                "span": "line 54; printed p. 162 n. 7",
                "quotes": ["quoted Michaud, I, p. 176."],
                "link": "[第6章 p.162 注7](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md#L54)",
            },
            {
                "location": "第6章，印刷页163注1，Markdown L55。",
                "summary": "注1以 ibid. 指回 Michaud，并标第一卷 p.68；被引页未核读。",
                "source_file": CH6,
                "span": "line 55; printed p. 163 n. 1",
                "quotes": ["1 ibid., I, p. 68."],
                "link": "[第6章 p.163 注1](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md#L55)",
            },
        ],
        "fields": [
            ("文献类型", "四卷本图书（据 Haskell 书目）", "S1；第21章书目，印刷页430，L811"),
            ("原题名", "*Louis XIV et Innocent XI*", "S1；第21章书目，印刷页430，L811"),
            ("书目责任者形式", "E. Michaud（照录 Haskell 形式；未关联人物 KU）", "S1；第21章书目，印刷页430，L811"),
            ("卷册范围", "4 vols.", "S1；第21章书目，印刷页430，L811"),
            ("出版项", "Paris，1882-3（照录原排形式）", "S1；第21章书目，印刷页430，L811"),
            ("Haskell 书内引注定位", "第6章 p.162 注7：Michaud 第一卷 p.176；被引页未独立查阅", "S2；第6章印刷页162注7，L54"),
            ("Haskell 书内引注定位", "第6章 p.163 注1：ibid. 指 Michaud 第一卷 p.68；被引页未独立查阅", "S3；第6章印刷页163注1，L55"),
        ],
        "paragraph_zh": (
            "本卡登记 Haskell 第21章书目所列 E. Michaud 四卷本 *Louis XIV et Innocent XI*（Paris，1882-3）。"
            "第6章 p.162 注7转引 Michaud 第一卷 p.176，第6章 p.163 注1以 ibid. 标引第一卷 p.68。"
            "本批未查阅该书或被引页，也未据书目责任者形式推定人物身份。"
        ),
        "paragraph_en": (
            "This unit records E. Michaud’s four-volume *Louis XIV et Innocent XI* (Paris, 1882-3) as listed in Haskell’s chapter 21 bibliography. "
            "Chapter 6 note 7 refers to vol. I, p. 176, and note 1 on p. 163 uses ibid. for vol. I, p. 68. "
            "Neither the publication nor its cited pages was consulted, and the bibliographic author form is not linked to a person KU."
        ),
        "citations": [
            {
                "statement": STATEMENTS[0],
                "role": "第6章 p.162 注7转引 Michaud 第一卷",
                "scope": "Haskell 注7称法国使节报告转引自 Michaud 第一卷 p.176；formal cites 仅表示书内转引定位，不表示已核读 Michaud 或报告。",
                "span": "line 54; printed p. 162 n. 7",
            },
            {
                "statement": STATEMENTS[1],
                "role": "第6章 p.163 注1引用 Michaud 第一卷",
                "scope": "Haskell 注1以 ibid. 指回 Michaud 第一卷 p.68；formal cites 仅表示书内引注定位，不表示已核读被引页或其内容。",
                "span": "line 55; printed p. 163 n. 1",
            },
        ],
    },
    {
        "candidate": "cand-6575",
        "group": "archive-group-e4f0548d6dd1",
        "ku_id": "units/archives/roma-volume-xix-1941",
        "type": "archive",
        "sub_type": "periodical volume",
        "name_zh": "Roma 第十九卷（1941）",
        "name_en": "Roma, vol. XIX (1941)",
        "sources": [
            {
                "location": "第6章，印刷页163注3–4，Markdown L57–58。",
                "summary": "注3称1679年1月28日 avviso 刊于 Roma, XIX (1941), p.161；注4称2月18日 avviso 刊于 ibid.。此处仅记录 Haskell 所引期刊卷册及定位，不表示期刊或 avvisi 已独立查阅。",
                "source_file": CH6,
                "span": "lines 57-58; printed p. 163 nn. 3-4",
                "quotes": [
                    "3 See avviso of 28 January 1679 published in Roma, XIX, 1941, p. 161.",
                    "4 See avviso of 18 February 1679 published ibid.",
                ],
                "link": "[第6章 p.163 注3–4](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md#L57)",
            },
        ],
        "fields": [
            ("文献类型", "期刊卷册（据 Haskell 引注）", "S1；第6章印刷页163注3–4，L57–58"),
            ("刊名", "*Roma*（照录 Haskell 引注形式）", "S1；第6章印刷页163注3，L57"),
            ("卷次", "XIX", "S1；第6章印刷页163注3，L57"),
            ("出版年", "1941", "S1；第6章印刷页163注3，L57"),
            ("Haskell 书内引注定位", "第6章 p.163 注3：1月28日 avviso，Roma XIX (1941), p.161", "S1；第6章印刷页163注3，L57"),
            ("Haskell 书内引注定位", "第6章 p.163 注4：2月18日 avviso，刊载于 ibid.；原注未重复页码", "S1；第6章印刷页163注4，L58"),
        ],
        "paragraph_zh": (
            "本卡对应 Haskell 第6章脚注所引 *Roma* 第十九卷（1941）：注3称 1679年1月28日 avviso 刊于 p.161，"
            "注4称 2月18日 avviso 刊于 ibid.，未另列页码。此卡登记被引期刊卷册，不把两则 avvisi 合并为卷册本身，"
            "也不表示期刊或通知原文已查阅。"
        ),
        "paragraph_en": (
            "This unit represents the *Roma* periodical volume XIX (1941) cited in Haskell’s chapter 6 notes. "
            "Note 3 locates the avviso of 28 January 1679 at p. 161; note 4 says the avviso of 18 February was published ibid. and gives no separate page. "
            "The unit is the cited volume, not either notice, and neither the volume nor the avvisi was consulted."
        ),
        "citations": [
            {
                "statement": STATEMENTS[2],
                "role": "第6章 p.163 注3引注 1679年1月28日 avviso",
                "scope": "Haskell 注3称 1月28日 avviso 刊于 Roma XIX (1941), p.161；formal cites 仅记录书内引注，不表示已核读期刊或 avviso。",
                "span": "line 57; printed p. 163 n. 3",
            },
            {
                "statement": STATEMENTS[3],
                "role": "第6章 p.163 注4引注 1679年2月18日 avviso",
                "scope": "Haskell 注4称 2月18日 avviso 刊于 ibid.，未另列页码；formal cites 仅记录同卷引注，不推定未载 locator 或核实内容。",
                "span": "line 58; printed p. 163 n. 4",
            },
        ],
    },
]


def write_text_preserving(path: Path, text: str) -> None:
    raw = path.read_bytes() if path.exists() else b""
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    encoding = "utf-8-sig" if bom else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        handle.write(text.replace("\n", newline))


def write_csv_preserving(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in raw else "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def replace_one(text: str, pattern: str, replacement: str, label: str) -> str:
    result, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.M)
    assert count == 1, f"could not update {label}"
    return result


def extract_fields(card_texts: dict[Path, str], manifest_rows: list[dict]) -> list[dict]:
    old_base = field_facts.BASE
    with tempfile.TemporaryDirectory(prefix="pnp-s4-ch6-citations-") as temp_name:
        temp_root = Path(temp_name)
        field_facts.BASE = temp_root
        for target, text in card_texts.items():
            temp_card = temp_root / target.relative_to(ROOT)
            temp_card.parent.mkdir(parents=True, exist_ok=True)
            temp_card.write_text(text, encoding="utf-8-sig", newline="\n")
        try:
            selected = [row for row in manifest_rows if row["ku_id"] in {spec["ku_id"] for spec in SPECS}]
            rows, _, warnings, cards_with_tables = field_facts.extract_records(selected)
        finally:
            field_facts.BASE = old_base
    expected = sum(len(spec["fields"]) for spec in SPECS)
    assert not warnings, warnings
    assert cards_with_tables == len(SPECS) and len(rows) == expected, (cards_with_tables, len(rows), expected)
    assert all(row["source_ids"] == ["haskell-1980-rev-ed"] for row in rows), rows
    assert all(row["evidence_status"] == "source_backed" and row["origin"] == "book" for row in rows)
    field_facts.assign_ids(rows, ENRICHMENT_PATH)
    return rows


def update_result_table(result: str, prefix: str, replacement: str) -> str:
    return replace_one(result, rf"^\| \[{re.escape(prefix)}\].*$", replacement, f"result artifact {prefix}")


def format_type_counts(type_counts: dict[str, tuple[int, int]]) -> str:
    labels = {
        "person": "person", "institution": "institution", "event": "event",
        "place": "place", "work": "work", "archive": "archive", "term": "term",
        "family": "family", "procedure": "procedure",
    }
    order = ["person", "institution", "event", "place", "work", "archive", "term", "family", "procedure"]
    return "、".join(
        f"{labels[k]} {type_counts.get(k, (0, 0))[0]}组／{type_counts.get(k, (0, 0))[1]}成员"
        for k in order if type_counts.get(k, (0, 0))[0]
    ) or "无"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two chapter 6 citation endpoints and adjudicate their four S6 candidates.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    archive_batch.DATE = DATE
    archive_batch.ANCHOR = ANCHOR
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    relation_fields, relations = sync.read_csv(RELATIONS_PATH)
    _, source_rows = sync.read_csv(TABLES / "sources.csv")
    statements = sync.load_statements()
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_candidate = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    statement_by_id = {row["statement_id"]: row for row in statements}
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    agents_text = AGENTS_PATH.read_text(encoding="utf-8-sig")

    assert ANCHOR not in process_text and ANCHOR not in result_text
    source_ids = {row["source_id"] for row in source_rows}
    assert "haskell-1980-rev-ed" in source_ids
    assert all(statement_id in statement_by_id for statement_id in STATEMENTS)
    target_candidates = {spec["candidate"] for spec in SPECS}
    target_statements = {
        row["statement_id"]
        for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and (row.get("subject_candidate_id") in target_candidates or row.get("object_candidate_id") in target_candidates)
    }
    assert target_statements == set(STATEMENTS), target_statements
    for spec in SPECS:
        candidate = candidate_by_id[spec["candidate"]]
        decision = alignment_by_candidate[spec["candidate"]]
        assert candidate["suggested_type"] == "archive"
        assert decision["decision"] == "new" and not decision.get("ku_id")
        assert sync.get_group(decision.get("resolution_note", "")) == spec["group"]
        group_members = [
            row["candidate_id"]
            for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert group_members == [spec["candidate"]], group_members
        card_path = f"04-knowledge/{spec['ku_id']}.md"
        assert not (ROOT / card_path).exists() and card_path not in accepted_text
        assert not any(row["ku_id"] == spec["ku_id"] or row["card_path"] == card_path for row in manifest)
        assert not any(row["type"] == "archive" and row["name_en"].casefold() == spec["name_en"].casefold() for row in manifest)
        for item in spec["sources"]:
            source_text = (ROOT / item["source_file"]).read_text(encoding="utf-8-sig")
            normalized_source = " ".join(source_text.split())
            for quote in item["quotes"]:
                assert " ".join(quote.split()) in normalized_source, (item["source_file"], quote)

    subject_decision = alignment_by_candidate[SUBJECT_CANDIDATE]
    assert subject_decision["decision"] == "same" and subject_decision["ku_id"] == SUBJECT_KU
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    assert manifest_by_id[SUBJECT_KU]["type"] == "archive"
    relation_rules = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8-sig"))
    cites_rule = relation_rules["domain_range"]["cites"]
    assert "archive" in cites_rule["domain"] and "archive" in cites_rule["range"]

    for statement_id in STATEMENTS:
        statement = statement_by_id[statement_id]
        assert (statement.get("qualifiers") or {}).get("relation_candidate") is True
        assert statement.get("predicate") == "footnote_citation"
        assert statement.get("subject_candidate_id") == SUBJECT_CANDIDATE
        assert statement.get("object_candidate_id") in target_candidates
        assert not any(statement_id in row.get("note", "") for row in relations), f"already in relations: {statement_id}"
        assert not any(statement_id in line for line in process_text.splitlines()), f"already adjudicated in process: {statement_id}"

    planned_alignment = [dict(row) for row in alignments]
    new_cards: dict[Path, str] = {}
    for spec in SPECS:
        decision = next(row for row in planned_alignment if row.get("candidate_id") == spec["candidate"] and not row.get("external_source"))
        decision["ku_id"] = spec["ku_id"]
        decision["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        decision["resolution_note"] += (
            f" S4 registration: {spec['group']} maps to {spec['ku_id']}; "
            "Haskell book-local bibliography/footnotes only; no external identity or cited-content verification is claimed."
        )
        card_rel = f"04-knowledge/{spec['ku_id']}.md"
        new_cards[ROOT / card_rel] = archive_batch.make_archive_card(spec)

    planned_manifest = list(manifest) + [
        {
            "ku_id": spec["ku_id"],
            "type": "archive",
            "canonical_name": spec["name_zh"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": f"04-knowledge/{spec['ku_id']}.md",
        }
        for spec in SPECS
    ]
    planned_accepted = archive_batch.insert_accepted_paths(
        accepted_text,
        [f"04-knowledge/{spec['ku_id']}.md" for spec in SPECS],
    )

    next_relation_id = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
    planned_relation_rows = []
    spec_by_statement = {
        item["statement"]: spec
        for spec in SPECS
        for item in spec["citations"]
    }
    for offset, statement_id in enumerate(STATEMENTS):
        spec = spec_by_statement[statement_id]
        citation = next(item for item in spec["citations"] if item["statement"] == statement_id)
        planned_relation_rows.append(
            {
                "relation_id": f"rel-{next_relation_id + offset:04d}",
                "subject_ku_id": SUBJECT_KU,
                "object_ku_id": spec["ku_id"],
                "predicate": "cites",
                "time": "",
                "role": citation["role"],
                "scope": citation["scope"],
                "origin": "book",
                "status": "formal",
                "source_id": "haskell-1980-rev-ed",
                "source_span": citation["span"],
                "source_file": CH6,
                "note": f"S2 statement: {statement_id}. The edge records Haskell's in-book citation only; the cited publication and contents were not consulted.",
            }
        )
    relation_keys = {
        (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"])
        for row in relations
    }
    for row in planned_relation_rows:
        key = (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"])
        assert key not in relation_keys, key
        relation_keys.add(key)
    planned_relations = relations + planned_relation_rows

    new_fields = extract_fields(new_cards, planned_manifest)
    old_enrichment = [
        json.loads(line)
        for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    planned_field_count = len(old_enrichment) + len(new_fields)
    current_unverified = sum(row.get("evidence_status") == "unverified" for row in old_enrichment)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    direct_groups, direct_candidates, direct_members, direct_types = archive_batch.summarize_relation_endpoint_queue(
        candidates, planned_alignment, planned_manifest, statements
    )
    pending_groups = totals["pending_groups"]
    pending_members = totals["pending_members"]
    non_direct_groups = pending_groups - direct_groups
    non_direct_members = pending_members - direct_members

    s6_match = re.search(
        r"([\d,]+)/([\d,]+)条S2关系候选（([\d,]+) formal、([\d,]+) pending、([\d,]+) rejected）",
        result_text,
    )
    assert s6_match, "current cumulative S6 counts not found in result"
    s6_total, s6_denominator, s6_formal, s6_pending, s6_rejected = [int(value.replace(",", "")) for value in s6_match.groups()]
    assert s6_total == s6_formal + s6_pending + s6_rejected
    assert s6_denominator == sum(1 for row in statements if (row.get("qualifiers") or {}).get("relation_candidate") is True)
    next_s6 = (s6_total + len(STATEMENTS), s6_denominator, s6_formal + len(STATEMENTS), s6_pending, s6_rejected)
    relation_status = {name: sum(row["status"] == name for row in planned_relations) for name in ("formal", "pending", "rejected")}
    missing_source = sum(not row.get("source_id") for row in planned_relations)

    updated_result = result_text
    batch_result = (
        f"### S4/S5/S6 archive：第6章 Michaud 与 Roma 引注端点（{DATE}）\n\n"
        f"沿用既有 S3 `new` 单成员组登记两项 archive：`cand-6571`（`archive-group-06ab78ee5350`）对应 Michaud 四卷本 *Louis XIV et Innocent XI*；"
        f"`cand-6575`（`archive-group-e4f0548d6dd1`）对应 *Roma* XIX (1941)。两组身份沿用第21章书目与第6章脚注定位，不增加外部身份断言。"
        f"按 Haskell 原书支持新增{len(new_fields)}条 `source_backed` 字段。\n\n"
        f"S6 对四条脚注候选逐条裁为 formal `cites`，登记 `{planned_relation_rows[0]['relation_id']}`–`{planned_relation_rows[-1]['relation_id']}`。"
        "关系仅记录 Haskell 的书内引注；Michaud 各卷、Roma 卷册、报告、avvisi 及被引内容均未独立查阅。"
        f"批后 S4 {totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条映射；"
        f"S5字段{planned_field_count:,}条（{current_unverified:,}条 `unverified`）；S6累计{next_s6[0]:,}/{next_s6[1]:,}项裁决；关系表{len(planned_relations):,}条。"
        f"逐项依据见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。\n"
    )
    date_marker = f"更新日期：{DATE}。\n"
    assert date_marker in updated_result
    updated_result = updated_result.replace(date_marker, date_marker + "\n" + batch_result + "\n", 1)

    updated_result = replace_one(
        updated_result,
        r"^- \*\*S4：\*\*.*$",
        f"- **S4：** 已登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条候选映射；待登记{pending_groups:,}组／{pending_members:,}条映射，直接端点{direct_groups:,}组／{direct_members:,}条组成员映射。",
        "result S4 overview",
    )
    updated_result = replace_one(
        updated_result,
        r"^- \*\*S5：\*\*.*$",
        f"- **S5：** 字段表{planned_field_count:,}条，其中{current_unverified:,}条为 `unverified`；未核字段按证据逐项处理。",
        "result S5 overview",
    )
    updated_result = replace_one(
        updated_result,
        r"^- \*\*S6：\*\*.*$",
        f"- **S6：** 关系表{len(planned_relations):,}条（{relation_status['formal']:,} formal、{relation_status['pending']:,} pending）；过程记录累计逐条裁决{next_s6[0]:,}/{next_s6[1]:,}条S2关系候选（{next_s6[2]:,} formal、{next_s6[3]:,} pending、{next_s6[4]:,} rejected），其余{next_s6[1]-next_s6[0]:,}条待逐项裁决。",
        "result S6 overview",
    )
    updated_result = update_result_table(
        updated_result,
        "KU 登记",
        f"| [KU 登记](../tables/ku-manifest.csv) | {len(planned_manifest):,} KU；新组登记与待登记分类型统计见下表 |",
    )
    updated_result = update_result_table(
        updated_result,
        "字段表",
        f"| [字段表](../tables/enrichment.jsonl) | {planned_field_count:,}条，其中{current_unverified:,}条 unverified |",
    )
    updated_result = update_result_table(
        updated_result,
        "关系表",
        f"| [关系表](../tables/relations.csv) | {len(planned_relations):,}条：{relation_status['formal']:,} formal、{relation_status['pending']:,} pending；{missing_source}条缺结构化 `source_id`；S2另有10,402条`relation_candidate=true`的statement，二者不是同一计数口径 |",
    )
    matrix_marker = "| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |"
    matrix_start = updated_result.index(matrix_marker)
    matrix_end = updated_result.index("\n\n", matrix_start)
    type_table, _ = sync.build_type_table(stats)
    updated_result = updated_result[:matrix_start] + type_table + updated_result[matrix_end:]

    current_stage_block = (
        f"S4已登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条候选映射；"
        f"待登记{pending_groups:,}组／{pending_members:,}条映射，其中直接关系端点{direct_groups:,}组／{direct_members:,}条组成员映射，"
        f"非直接映射{non_direct_groups:,}组／{non_direct_members:,}条。"
        f"S5字段表{planned_field_count:,}条、其中{current_unverified:,}条unverified。"
        f"S6关系表{len(planned_relations):,}条（{relation_status['formal']:,} formal、{relation_status['pending']:,} pending），"
        f"过程记录累计逐条裁决{next_s6[0]:,}/{next_s6[1]:,}条S2关系候选（{next_s6[2]:,} formal、{next_s6[3]:,} pending、{next_s6[4]:,} rejected）；"
        f"其余{next_s6[1]-next_s6[0]:,}条待逐项裁决，全部关系均有结构化source_id。"
    )
    agents_text = replace_one(
        agents_text,
        r"S4已登记[^。]*。S5字段表[^。]*。S6关系表[^。]*。",
        current_stage_block,
        "AGENTS stage snapshot",
    )

    process_note = f"""

<a id="{ANCHOR}"></a>

### S4/S5/S6 archive：第6章 Michaud 与 Roma 引注端点（{DATE}）

沿用既有 S3 `new` 决定登记两个单成员 archive 组，不改 S3 身份裁决：`cand-6571` / `archive-group-06ab78ee5350` 映射到 `units/archives/michaud-louis-xiv-et-innocent-xi-1882-1883`；`cand-6575` / `archive-group-e4f0548d6dd1` 映射到 `units/archives/roma-volume-xix-1941`。Michaud 身份依据第21章印刷页430 L811 的书目条目“E. Michaud: Louis XIV et Innocent XI, 4 vols., Paris 1882-3.”；其书目责任者形式不用于推定或登记人物身份。Roma 卷册身份依据第6章印刷页163注3–4：注3把 1679年1月28日 avviso 定位为 *Roma*, XIX (1941), p.161，注4以 ibid. 指回该刊载来源且没有另写页码。所引文献、报告与 avvisi 均未在本批独立查阅。

两张卡按中英双语格式登记，分别新增7条与6条 `source_backed` 字段，共{len(new_fields)}条；字段只记录 Haskell 原书的题名、书目形式、卷册／出版项与书内引注 locator。字段状态不表示独立外部核验。

**S6逐条裁决：** 四条 S2 候选均以 Haskell 的书内脚注为证据，`footnote_citation` 映射为受控的 `cites`。主体 `cand-2962` 已复用 `units/archives/patrons-and-painters`；两个 archive 客体由本批登记。正式边各自保留脚注、所引文献／avviso 和 locator 范围；边仅表示 Haskell 的引注，不表示被引内容已读或核实。

| statement_id | 原书定位与对象 | 决定 | 正式关系 |
|---|---|---|---|
| `st-chp6-p162-n7-cite` | 第6章 p.162 注7；Michaud I, p.176 | formal `cites`，书内转引定位 | `{planned_relation_rows[0]['relation_id']}` |
| `st-chp6-p163-n1-cite` | 第6章 p.163 注1；ibid., Michaud I, p.68 | formal `cites`，书内引注定位 | `{planned_relation_rows[1]['relation_id']}` |
| `st-chp6-p163-n3-cite` | 第6章 p.163 注3；1月28日 avviso，Roma XIX (1941), p.161 | formal `cites`，书内引注定位 | `{planned_relation_rows[2]['relation_id']}` |
| `st-chp6-p163-n4-cite` | 第6章 p.163 注4；2月18日 avviso，刊于 ibid.，原注未另列页码 | formal `cites`，不推定 locator | `{planned_relation_rows[3]['relation_id']}` |

批后 S4 登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条映射；待登记{pending_groups:,}组／{pending_members:,}条，其中直接端点{direct_groups:,}组／{direct_candidates:,}个候选／{direct_members:,}条成员映射、非直接{non_direct_groups:,}组／{non_direct_members:,}条。S5字段表{planned_field_count:,}条、{current_unverified:,}条 `unverified`。S6累计逐条裁决{next_s6[0]:,}/{next_s6[1]:,}条（{next_s6[2]:,} formal、{next_s6[3]:,} pending、{next_s6[4]:,} rejected）；关系表{len(planned_relations):,}条（{relation_status['formal']:,} formal、{relation_status['pending']:,} pending）。
"""
    updated_process = process_text.rstrip() + process_note

    if args.preview:
        print("REVIEWABLE BATCH PREVIEW")
        print(f"S4 groups/mappings: +{len(SPECS)} / +{len(SPECS)}; after={totals['registered_groups']:,}/{totals['new_groups']:,} groups, {totals['registered_members']:,}/{totals['new_candidates']:,} mappings")
        print(f"S5 fields: +{len(new_fields)} source_backed; after={planned_field_count:,}, unverified={current_unverified:,}")
        print(f"S6 decisions: +{len(STATEMENTS)} formal cites; after={next_s6[0]:,}/{next_s6[1]:,}; relation table={len(planned_relations):,} ({relation_status['formal']:,} formal, {relation_status['pending']:,} pending)")
        print("\nALIGNMENT MAPPINGS")
        for spec in SPECS:
            print(f"{spec['candidate']} | {spec['group']} | new -> {spec['ku_id']}")
        print("\nS5 FIELD RECORDS")
        for row in new_fields:
            print(json.dumps({k: row[k] for k in ("ku_id", "field", "value", "source_id", "source_ref", "evidence_status")}, ensure_ascii=False))
        print("\nS6 RELATION RECORDS")
        for row in planned_relation_rows:
            print(json.dumps(row, ensure_ascii=False))
        for path, content in new_cards.items():
            print(f"\nNEW CARD: {path.relative_to(ROOT)}\n{content}")
        print("\nPROCESS RECORD APPEND")
        print(process_note)
        print("\nCURRENT RESULT VALUES")
        for line in updated_result.splitlines()[:22]:
            if line.startswith(("- **S4", "- **S5", "- **S6", "### S4/S5/S6")) or line.startswith("沿用既有 S3") or line.startswith("S6 对四条"):
                print(line)
        print("\nAGENTS CURRENT SNAPSHOT SEGMENT")
        print(current_stage_block)
        print("\nACCEPTED PATHS")
        for spec in SPECS:
            print(f"- 04-knowledge/{spec['ku_id']}.md")
        return 0

    if args.dry_run:
        print(f"dry-run passed: 2 existing S3 archive groups -> 2 new KU cards ({', '.join(spec['ku_id'] for spec in SPECS)})")
        print(f"verified exact book quotations: {sum(len(item['quotes']) for spec in SPECS for item in spec['sources'])}")
        print(f"S5 fields: {len(new_fields)} source_backed; enrichment {len(old_enrichment):,}->{planned_field_count:,}; unverified unchanged={current_unverified:,}")
        print(f"S6: {len(STATEMENTS)} formal cites -> {planned_relation_rows[0]['relation_id']}–{planned_relation_rows[-1]['relation_id']}; endpoints, domain/range, evidence IDs, and natural keys pass")
        print(f"S4: {totals['registered_groups']:,}/{totals['new_groups']:,} groups, {totals['registered_members']:,}/{totals['new_candidates']:,} mappings; pending {pending_groups:,}/{pending_members:,}")
        print(f"direct endpoint queue: {direct_groups:,} groups/{direct_candidates:,} candidates/{direct_members:,} mappings; types: {format_type_counts(direct_types)}")
        print(f"relation table: {len(planned_relations):,} rows ({relation_status['formal']:,} formal, {relation_status['pending']:,} pending); missing source_id={missing_source}")
        print("planned writes: 2 cards; accepted.yml; ku-manifest.csv; alignment.csv; relations.csv; enrichment.jsonl; process/result/AGENTS snapshots")
        return 0

    for path, content in new_cards.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text_preserving(path, content)
    write_csv_preserving(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv_preserving(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    write_csv_preserving(RELATIONS_PATH, relation_fields, planned_relations)
    write_text_preserving(ACCEPTED_PATH, planned_accepted)
    with ENRICHMENT_PATH.open("a", encoding="utf-8", newline="\n") as handle:
        for row in new_fields:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    write_text_preserving(PROCESS_PATH, updated_process)
    write_text_preserving(RESULT_PATH, updated_result.rstrip() + "\n")
    write_text_preserving(AGENTS_PATH, agents_text)
    print(f"applied: 2 archive KU cards; S4 registered {totals['registered_groups']:,}/{totals['new_groups']:,} groups")
    print(f"S6: 4 formal cites ({planned_relation_rows[0]['relation_id']}–{planned_relation_rows[-1]['relation_id']}); S5: {len(new_fields)} source_backed fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
