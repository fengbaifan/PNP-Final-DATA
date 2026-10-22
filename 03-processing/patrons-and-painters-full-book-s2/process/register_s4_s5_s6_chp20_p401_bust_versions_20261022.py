from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.build_field_facts import extract_records  # noqa: E402

TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_FILE = "02-sources/02-Markdown/20_CHP-20Postscript.md"
SOURCE_ID = "haskell-1980-rev-ed"
ANCHOR = "s4-s5-s6-chp20-p401-bust-versions-20261022"

ITEMS = [
    {
        "candidate_id": "cand-10965",
        "group": "workgrp-10ae8b71daeeb5",
        "ku_id": "units/works/paolo-giordano-ii-bust-humphris-version",
        "type": "work",
        "canonical_name": "保罗·乔尔达诺二世·奥尔西尼相关青铜半身像（Humphris 版本）",
        "name_en": "Small bronze bust associated with Paolo Giordano II Orsini (Humphris version)",
        "card_path": "04-knowledge/units/works/paolo-giordano-ii-bust-humphris-version.md",
    },
    {
        "candidate_id": "cand-10966",
        "group": "workgrp-09f72370b284a3",
        "ku_id": "units/works/paolo-giordano-ii-bust-plymouth-version",
        "type": "work",
        "canonical_name": "保罗·乔尔达诺二世·奥尔西尼半身像的普利茅斯版本",
        "name_en": "Another version of the Paolo Giordano II Orsini bust (Plymouth)",
        "card_path": "04-knowledge/units/works/paolo-giordano-ii-bust-plymouth-version.md",
    },
    {
        "candidate_id": "cand-10969",
        "group": "sg3-institution-cand-10969",
        "ku_id": "units/institutions/city-museum-and-art-gallery-plymouth",
        "type": "institution",
        "canonical_name": "普利茅斯 City Museum and Art Gallery",
        "name_en": "City Museum and Art Gallery, Plymouth",
        "card_path": "04-knowledge/units/institutions/city-museum-and-art-gallery-plymouth.md",
    },
]

EXPECTED_RELATION_CANDIDATES = {
    "st-chp20-p401-humphris-bust-possession",
    "st-chp20-p401-wittkower-bust-attribution-proposal",
    "st-chp20-p401-plymouth-bust-version-discussed",
    "st-chp20-p401-haskell-rejects-bernini-bust-attribution",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = path.read_bytes()
    bom = raw.startswith(bytes.fromhex("efbbbf"))
    eol = "\r\n" if b"\r\n" in raw else "\n"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames or [], list(reader), bom, eol


def csv_bytes(path: Path, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    raw = path.read_bytes()
    bom = raw.startswith(bytes.fromhex("efbbbf"))
    eol = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=eol)
    writer.writeheader()
    writer.writerows(rows)
    payload = stream.getvalue().encode("utf-8")
    return (bytes.fromhex("efbbbf") if bom else b"") + payload


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".codex-tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def candidate_group(note: str) -> str | None:
    match = re.search(r"(?:^|[;\s])group=([^;\s]+)", note or "")
    return match.group(1) if match else None


def insert_accepted(text: str, card_path: str) -> str:
    assert card_path not in text, f"accepted.yml already contains {card_path}"
    lines = text.splitlines()
    insert_at = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > card_path
        ),
        next((index for index, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_path}")
    eol = "\r\n" if "\r\n" in text else "\n"
    return eol.join(lines) + eol


def build() -> tuple[dict[Path, bytes], list[dict[str, str]]]:
    candidates_path = TABLES / "entity-candidates.csv"
    alignment_path = TABLES / "alignment.csv"
    manifest_path = TABLES / "ku-manifest.csv"
    relations_path = TABLES / "relations.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"

    _, candidates, _, _ = read_csv(candidates_path)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    align_fields, alignments, _, _ = read_csv(alignment_path)
    manifest_fields, manifest, _, _ = read_csv(manifest_path)
    relation_fields, relations, _, _ = read_csv(relations_path)

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = [dict(row) for row in manifest]
    alignment_by_candidate = {
        row["candidate_id"]: row
        for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_by_id = {row["ku_id"]: row for row in planned_manifest}

    for item in ITEMS:
        candidate = candidate_by_id[item["candidate_id"]]
        assert candidate["suggested_type"] == item["type"], item["candidate_id"]
        alignment = alignment_by_candidate[item["candidate_id"]]
        assert alignment["decision"] == "new" and not alignment.get("ku_id"), item["candidate_id"]
        assert candidate_group(alignment.get("resolution_note", "")) == item["group"], item["candidate_id"]
        group_members = [
            row["candidate_id"]
            for row in planned_alignments
            if row.get("decision") == "new"
            and not row.get("external_source")
            and candidate_group(row.get("resolution_note", "")) == item["group"]
        ]
        assert group_members == [item["candidate_id"]], (item["group"], group_members)
        assert (ROOT / item["card_path"]).is_file(), item["card_path"]
        assert item["ku_id"] not in manifest_by_id
        assert not any(
            row.get("name_en", "").casefold() == item["name_en"].casefold()
            for row in planned_manifest
        )
        alignment["ku_id"] = item["ku_id"]
        alignment["resolution_note"] = (
            (alignment.get("resolution_note", "") or "").rstrip()
            + f" S4 registration: mapped {item['group']} to {item['ku_id']}; distinct work-version/institution groups retained."
        )
        row = {
            "ku_id": item["ku_id"],
            "type": item["type"],
            "canonical_name": item["canonical_name"],
            "name_en": item["name_en"],
            "source_task": "chp-20",
            "card_path": item["card_path"],
        }
        planned_manifest.append(row)
        manifest_by_id[item["ku_id"]] = row

    source_path = ROOT / SOURCE_FILE
    source_text = " ".join(source_path.read_text(encoding="utf-8-sig").split())
    assert "came into the possession of Cyril Humphris" in source_text
    assert "another version, in the City Museum and Art Gallery, Plymouth" in source_text
    source_rows = read_csv(TABLES / "sources.csv")[1]
    assert sum(row.get("source_id") == SOURCE_ID for row in source_rows) == 1

    with (TABLES / "book-statements.jsonl").open(encoding="utf-8") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    direct_relation_ids = {
        row["statement_id"]
        for row in statements
        if row.get("statement_id")
        and {row.get("subject_candidate_id"), row.get("object_candidate_id")}
        & {item["candidate_id"] for item in ITEMS}
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relation_ids == EXPECTED_RELATION_CANDIDATES, direct_relation_ids

    existing_enrichment = [
        json.loads(line)
        for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    additions, source_registry, warnings, cards_with_tables = extract_records(
        [{"ku_id": item["ku_id"], "card_path": item["card_path"]} for item in ITEMS]
    )
    assert cards_with_tables == len(ITEMS)
    assert len(additions) == 10, len(additions)
    assert not warnings, warnings
    assert set(source_registry) == {SOURCE_ID}
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert all(row.get("source_ids") == [SOURCE_ID] for row in additions)
    existing_enrichment_ids = {row.get("enrichment_id", "") for row in existing_enrichment}
    existing_occurrences = {row.get("occurrence_id", "") for row in existing_enrichment}
    assert not any(row.get("ku_id") in {item["ku_id"] for item in ITEMS} for row in existing_enrichment)

    planned_relations = [dict(row) for row in relations]
    numeric_ids = [
        int(match.group(1))
        for row in planned_relations
        if (match := re.fullmatch(r"rel-(\d+)", row.get("relation_id", "")))
    ]
    next_id = max(numeric_ids, default=0) + 1
    new_relations = [
        {
            "relation_id": f"rel-{next_id:04d}",
            "subject_ku_id": ITEMS[0]["ku_id"],
            "object_ku_id": "units/persons/cyril-humphris",
            "predicate": "held_by",
            "time": "After appearance of the first edition; exact date not stated",
            "role": "持有人（来源称进入其 possession）",
            "scope": "仅指Humphris版本；Haskell称其在第一版出版后进入Cyril Humphris之手。此边记录来源所述持有，不等同于所有权或当前保管状态，并与普利茅斯版本区分。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": "lines 85–86; print p.401; PDF physical p.10; st-chp20-p401-humphris-bust-possession",
            "source_file": SOURCE_FILE,
            "note": "原书明确报告进入Humphris之手；未给出转移日期。",
        },
        {
            "relation_id": f"rel-{next_id + 1:04d}",
            "subject_ku_id": ITEMS[1]["ku_id"],
            "object_ku_id": ITEMS[2]["ku_id"],
            "predicate": "held_by",
            "time": "Haskell’s account; date not stated",
            "role": "来源所述保管机构",
            "scope": "仅指普利茅斯版本。Haskell称该版本在City Museum and Art Gallery, Plymouth；不表示当前馆藏状态，也不延伸到Humphris版本。statement中关于Radcliffe于1978、1979年讨论该版本的部分不纳入此边。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": "line 87; print p.401; PDF physical p.10; st-chp20-p401-plymouth-bust-version-discussed",
            "source_file": SOURCE_FILE,
            "note": "仅裁决明确的机构所在语句；被引研究未独立查阅。",
        },
    ]

    relation_spec = yaml.safe_load(
        (ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8")
    )["domain_range"]
    natural_keys = {
        (
            row.get("subject_ku_id"), row.get("predicate"), row.get("object_ku_id"),
            row.get("time"), row.get("scope"),
        )
        for row in planned_relations
    }
    for relation in new_relations:
        assert relation["predicate"] in relation_spec
        predicate = relation_spec[relation["predicate"]]
        assert manifest_by_id[relation["subject_ku_id"]]["type"] in predicate["domain"]
        assert manifest_by_id[relation["object_ku_id"]]["type"] in predicate["range"]
        key = (
            relation["subject_ku_id"], relation["predicate"], relation["object_ku_id"],
            relation["time"], relation["scope"],
        )
        assert key not in natural_keys
        natural_keys.add(key)
        assert relation["source_id"] and relation["source_span"] and relation["source_file"]
    planned_relations.extend(new_relations)

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_raw = accepted_path.read_bytes()
    accepted_bom = accepted_raw.startswith(bytes.fromhex("efbbbf"))
    accepted_text = accepted_raw.decode("utf-8-sig")
    for item in ITEMS:
        accepted_text = insert_accepted(accepted_text, item["card_path"])
    accepted_bytes = accepted_text.encode("utf-8")
    if accepted_bom:
        accepted_bytes = bytes.fromhex("efbbbf") + accepted_bytes

    outputs = {
        alignment_path: csv_bytes(alignment_path, align_fields, planned_alignments),
        manifest_path: csv_bytes(manifest_path, manifest_fields, planned_manifest),
        relations_path: csv_bytes(relations_path, relation_fields, planned_relations),
        accepted_path: accepted_bytes,
    }
    return outputs, new_relations


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed S4/S6 batch")
    args = parser.parse_args()
    outputs, new_relations = build()
    print("S4 mappings:")
    for item in ITEMS:
        print(f"  {item['candidate_id']} -> {item['ku_id']} ({item['type']}; {item['group']})")
    print("S5 fields: 10 source-backed rows from three new cards; field extraction warnings=0")
    print("S6 formal relations:")
    for relation in new_relations:
        print(
            f"  {relation['relation_id']} {relation['subject_ku_id']} "
            f"--{relation['predicate']}--> {relation['object_ku_id']} "
            f"[{relation['source_span']}]"
        )
    print("S6 rejected current graph edges:")
    print("  st-chp20-p401-wittkower-bust-attribution-proposal: scholarly proposal is not a controlled creator edge")
    print("  st-chp20-p401-haskell-rejects-bernini-bust-attribution: attribution judgment is not a work-person edge")
    print("Files planned: alignment.csv, ku-manifest.csv, accepted.yml, relations.csv")
    if not args.apply:
        print("preview only; pass --apply to write")
        return 0
    for path, payload in outputs.items():
        atomic_write(path, payload)
    print("applied alignment.csv, ku-manifest.csv, accepted.yml, and relations.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
