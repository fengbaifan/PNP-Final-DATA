from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
RELATIONS_PATH = TABLES / "relations.csv"
CARD_REL = "04-knowledge/units/works/antonio-verrio-fresco-on-staircase-of-hampton-court-palace.md"
CARD_PATH = ROOT / CARD_REL
WORK_KU = "units/works/antonio-verrio-fresco-on-staircase-of-hampton-court-palace"
WILLIAM_KU = "units/persons/william-iii-of-england"
SHAFTESBURY_KU = "units/persons/anthony-ashley-cooper-3rd-earl"
GROUP_ID = "workgrp-f05ecf107cead1"
ANCHOR = "s3-s4-s5-s6-chp7-plate29-verrio-reconciliation-20261028"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
CITATION = "Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this printing 2006)."
SUBJECT_STATEMENT = "st-chp7-p196-hampton_fresco_subject"
PROGRAM_STATEMENT = "st-chp7-p198-shaftesbury-verrio-programme"
SUBJECT_RELATION_ID = "rel-2480"
PROGRAM_RELATION_ID = "rel-2481"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    encoding = "utf-8-sig" if path.read_bytes().startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha1(value.encode('utf-8')).hexdigest()[:16]}"


def read_jsonl(path: Path) -> tuple[str, list[dict]]:
    raw = path.read_text(encoding="utf-8-sig")
    records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return ("utf-8-sig" if path.read_bytes().startswith(b"\xef\xbb\xbf") else "utf-8", records)


def write_jsonl(path: Path, encoding: str, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in records) + "\n", encoding=encoding, newline="\n")


def patch_card() -> str:
    text = CARD_PATH.read_text(encoding="utf-8-sig")
    match = re.match(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        raise ValueError("Existing work card has an invalid YAML frontmatter boundary")
    frontmatter = yaml.safe_load(match.group(1))
    body = text[match.end():]
    sources = frontmatter.get("sources") or []
    if any("printed p. 196" in item.get("location", "") for item in sources):
        raise ValueError("Chapter 7 p.196 source is already present; refusing duplicate write")

    sources.extend([
        {
            "citation": CITATION,
            "location": "第7章，印刷页196，L59；PDF物理页34。",
            "sentence_summary": "Haskell将图版29所示汉普顿宫寓意壁画描述为表现William III战胜以法国为首的天主教势力，题材取自Julian the Apostate的著作。",
            "original_quotes": [{
                "source_span": "Chapter 7, printed p. 196, line 59; PDF physical p. 34",
                "text": "Before the end of the century, however, he had been taken up by the new regime and was being employed at Hampton Court, where in a complex allegorical fresco, whose subject was chosen from the writings of Julian the Apostate, he portrayed the triumph of William III over the Catholic powers led by France (Plate 29).",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "line 59; printed p. 196; PDF physical p. 34",
            },
        },
        {
            "citation": CITATION,
            "location": "第7章，印刷页198，L82；PDF物理页36。",
            "sentence_summary": "Haskell推测Shaftesbury很可能帮助拟定了汉普顿宫多幅Verrio壁画的方案，并称其含有对William III政策的寓意。",
            "original_quotes": [{
                "source_span": "Chapter 7, printed p. 198, line 82; PDF physical p. 36",
                "text": "Then as an eager Whig intellectual, deeply sympathetic to Holland and hostile to France, he had in all probability helped to draw up the programme for Verrio’s frescoes at Hampton Court with their learned allusions to the policies of William III.",
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "line 82; printed p. 198; PDF physical p. 36",
            },
        },
    ])
    frontmatter["sources"] = sources
    frontmatter["updated"] = "2026-10-28"
    frontmatter["process_ref"] = PROCESS_REF

    old_zh = "**中文：** 《赞助人与画家》图版29目录所记的《汉普顿宫楼梯壁画》艺术对象。"
    new_zh = (
        "**中文：** 本卡记录《赞助人与画家》图版29目录所记的《汉普顿宫楼梯壁画》。第7章将图版29与一幅复杂寓意壁画相连，称其表现William III战胜以法国为首的天主教势力，题材取自Julian the Apostate的著作。此处只记录Haskell的书内描述，不补入外部实物身份。"
        "[第7章 p.196](../../../02-sources/02-Markdown/07_CHP-7_sec_iv.md#L59)"
    )
    old_en = "**English:** The art object titled Fresco on staircase of Hampton Court Palace, listed as plate 29 in Patrons and Painters."
    new_en = (
        "**English:** This card records the Fresco on staircase of Hampton Court Palace listed as plate 29 in *Patrons and Painters*. Chapter 7 links plate 29 to a complex allegorical fresco depicting William III’s triumph over the Catholic powers led by France, with a subject drawn from the writings of Julian the Apostate. This records Haskell’s description and adds no external object identification. "
        "[Chapter 7, p. 196](../../../02-sources/02-Markdown/07_CHP-7_sec_iv.md#L59)"
    )
    if old_zh not in body or old_en not in body:
        raise ValueError("Expected existing bilingual card description was not found")
    body = body.replace(old_zh, new_zh, 1).replace(old_en, new_en, 1)
    dumped = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{dumped}---\n{body}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile the Chapter 7 Plate 29 work identity and adjudicate its S6 candidates.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    alignment_by_id = {row["alignment_id"]: row for row in alignments}
    decisions = [("aln-3098", "cand-2763"), ("aln-7389", "cand-7213")]
    for alignment_id, candidate_id in decisions:
        row = alignment_by_id[alignment_id]
        assert row["candidate_id"] == candidate_id
        assert row["decision"] == "new" and not row["ku_id"] and not row["external_source"]
        assert f"group={GROUP_ID}" in row["resolution_note"]
        row["decision"] = "same"
        row["ku_id"] = WORK_KU
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += (
            " | Targeted S3 recheck: same as the accepted plate-29 work KU. The Chapter 7 p.196 body mention explicitly ends '(Plate 29)', "
            "matching the front-matter plate-29 caption 'Antonio Verrio: Fresco on staircase of Hampton Court Palace'; "
            "cand-2763 is the index lead cross-linked to cand-7213 in the same work group. Retain group provenance and map both candidates to one KU."
        )

    manifest = {row["ku_id"]: row for row in read_csv(TABLES / "ku-manifest.csv")[1]}
    assert manifest[WORK_KU]["type"] == "work"
    assert manifest[WILLIAM_KU]["type"] == "person"
    assert manifest[SHAFTESBURY_KU]["type"] == "person"
    accepted = yaml.safe_load((ROOT / "04-knowledge" / "accepted.yml").read_text(encoding="utf-8-sig"))
    assert CARD_REL in accepted["units"]
    candidates = {row["candidate_id"]: row for row in read_csv(TABLES / "entity-candidates.csv")[1]}
    assert candidates["cand-2763"]["suggested_type"] == "work"
    assert candidates["cand-7213"]["suggested_type"] == "work"
    assert "UVWXYZ.csv#99" in candidates["cand-2763"]["index_entry_id"]

    mentions = {row["mention_id"]: row for row in read_csv(TABLES / "mentions.csv")[1]}
    assert mentions["m-chp7-p196-b055"]["candidate_id"] == "cand-7213"
    assert mentions["m-chp7-p196-b060"]["surface_form"] == "Plate 29"
    assert mentions["m-chp7-p196-b060"]["candidate_id"] == "cand-7213"
    assert mentions["m-chp7-p196-b057"]["candidate_id"] == "cand-2814"
    endpoint_rows = {row["candidate_id"]: row for row in alignments if row["candidate_id"] in {"cand-2814", "cand-2426"} and not row["external_source"]}
    assert endpoint_rows["cand-2814"]["ku_id"] == WILLIAM_KU
    assert endpoint_rows["cand-2426"]["ku_id"] == SHAFTESBURY_KU

    _, statements_raw = read_jsonl(TABLES / "book-statements.jsonl")
    statements = {row["statement_id"]: row for row in statements_raw}
    subject = statements[SUBJECT_STATEMENT]
    program = statements[PROGRAM_STATEMENT]
    assert subject["subject_candidate_id"] == "cand-7213" and subject["object_candidate_id"] == "cand-2814"
    assert subject["qualifiers"]["relation_candidate"] is True
    assert program["subject_candidate_id"] == "cand-2426" and program["object_candidate_id"] == "cand-7213"
    assert program["qualifiers"]["relation_candidate"] is True
    assert "in all probability" in program["original_quote"]

    relation_fields, relations = read_csv(RELATIONS_PATH)
    assert not any(row["relation_id"] in {SUBJECT_RELATION_ID, PROGRAM_RELATION_ID} for row in relations)
    existing_formal = [row for row in relations if row["subject_ku_id"] == WORK_KU]
    assert {row["relation_id"] for row in existing_formal} >= {"rel-0413", "rel-0414", "rel-0415"}
    for target, predicate, time in ((WILLIAM_KU, "has_subject", ""), (SHAFTESBURY_KU, "designed_by", "")):
        assert not any(row["subject_ku_id"] == WORK_KU and row["object_ku_id"] == target and row["predicate"] == predicate and row["time"] == time for row in relations)
    next_relation = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
    assert next_relation == 2480

    range_matrix = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))["domain_range"]
    controlled = set(yaml.safe_load((ROOT / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml").read_text(encoding="utf-8"))["types"])
    for predicate in ("has_subject", "designed_by"):
        assert predicate in controlled
        assert "work" in range_matrix[predicate]["domain"] and "person" in range_matrix[predicate]["range"]

    enrichment_encoding, enrichment = read_jsonl(ENRICHMENT_PATH)
    table_id = "tbl-01630f927bbc1b03"
    table_rows = [row for row in enrichment if row["ku_id"] == WORK_KU and row["table_id"] == table_id]
    assert sorted(int(row["row_index"]) for row in table_rows) == [1, 2, 3, 4]
    assert not any(row["ku_id"] == WORK_KU and row["field"] == "主题／题材" for row in enrichment)
    next_enrichment = max(int(row["enrichment_id"].split("-")[1]) for row in enrichment) + 1
    assert next_enrichment == 18529
    field_value = "复杂寓意壁画；表现William III战胜以法国为首的天主教势力。Haskell称题材取自Julian the Apostate的著作。"
    enrichment.append({
        "enrichment_id": f"enr-{next_enrichment:05d}",
        "ku_id": WORK_KU,
        "field": "主题／题材",
        "value": field_value,
        "origin": "book",
        "source_id": SOURCE_ID,
        "source_ids": [SOURCE_ID],
        "source_ref": "S1",
        "source_citations": [CITATION],
        "source_urls": [],
        "evidence": "S1；第7章，印刷页196 L59；PDF物理页34",
        "evidence_status": "source_backed",
        "dispute": None,
        "accessed_date": "",
        "occurrence_id": stable_id("occ", f"{WORK_KU}|主题／题材"),
        "table_id": table_id,
        "table_section": "内容 / 来源所载信息",
        "has_header": True,
        "table_header": ["字段", "值", "证据"],
        "row_index": 5,
        "cells": ["主题／题材", field_value, "S1；第7章，印刷页196 L59；PDF物理页34"],
        "unit_evidence_status": "source_backed",
    })

    relations.extend([
        {
            "relation_id": SUBJECT_RELATION_ID,
            "subject_ku_id": WORK_KU,
            "object_ku_id": WILLIAM_KU,
            "predicate": "has_subject",
            "time": "",
            "role": "寓意壁画的表现对象",
            "scope": "仅记录Haskell对图版29所示寓意壁画的描述：表现William III战胜以法国为首的天主教势力；不将其改写为独立历史事件或外部核实的作品题材。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 7, printed p. 196, line 59; statement={SUBJECT_STATEMENT}; mention=m-chp7-p196-b057; plate-reference=m-chp7-p196-b060",
            "source_file": SOURCE_FILE,
            "note": f"S6 formal; source-bounded subject description, PDF physical p. 34. See {PROCESS_REF}.",
        },
        {
            "relation_id": PROGRAM_RELATION_ID,
            "subject_ku_id": WORK_KU,
            "object_ku_id": SHAFTESBURY_KU,
            "predicate": "designed_by",
            "time": "",
            "role": "Haskell推测其参与方案拟定",
            "scope": "Pending: Haskell称Shaftesbury“in all probability”帮助拟定Verrio在汉普顿宫的多幅壁画方案；贡献程度及是否具体涉及图版29作品未确定，不作为确定设计归属。",
            "origin": "book",
            "status": "pending",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 7, printed p. 198, line 82; statement={PROGRAM_STATEMENT}",
            "source_file": SOURCE_FILE,
            "note": f"S6 pending; preserve probability and plural-program scope. See {PROCESS_REF}.",
        },
    ])

    card_text = patch_card()
    print("S3: reopen the two source-linked rows only; map cand-2763 and cand-7213 to the existing Plate 29 work KU as same.")
    print(f"S4: reuse {WORK_KU}; no KU created.")
    print("S5: add one source-backed subject/theme field from Chapter 7, p. 196.")
    print("S6: rel-2480 has_subject formal; rel-2481 designed_by pending because Haskell's probability and plural scope remain unresolved.")
    print("Card: append p.196/p.198 source entries and refresh its CSV-backed relation view after preflight.")
    if args.dry_run:
        return

    write_csv(ALIGNMENT_PATH, alignment_fields, alignments)
    write_jsonl(ENRICHMENT_PATH, enrichment_encoding, enrichment)
    write_csv(RELATIONS_PATH, relation_fields, relations)
    CARD_PATH.write_text(card_text, encoding="utf-8", newline="\n")
    print("Applied targeted S3/S5/S6 reconciliation; inspect the existing card with build_cards.py --preview.")


if __name__ == "__main__":
    main()
