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
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_FILE = "02-sources/02-Markdown/20_CHP-20Postscript.md"
SOURCE_ID = "haskell-1980-rev-ed"
ORIGINAL_ID = "st-chp20-p401-plymouth-bust-version-discussed"
VARIANT_ID = "st-chp20-p401-plymouth-bust-another-version"
DISCUSSION_ID = "st-chp20-p401-plymouth-bust-radcliffe-discussion"
RELATION_ID = "rel-1453"


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


def patched_jsonl(path: Path, replacements: dict[str, dict], additions: list[dict]) -> bytes:
    raw = path.read_bytes()
    bom = bytes.fromhex("efbbbf") if raw.startswith(bytes.fromhex("efbbbf")) else b""
    text = raw[len(bom):].decode("utf-8")
    pending = dict(replacements)
    output: list[str] = []
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if content:
            record = json.loads(content)
            if record.get("statement_id") in pending:
                newline = line[len(content):]
                record = pending.pop(record["statement_id"])
                line = json.dumps(record, ensure_ascii=False) + newline
        output.append(line)
    assert not pending, sorted(pending)
    if additions:
        if output and not output[-1].endswith(("\n", "\r")):
            output[-1] += "\n"
        output.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in additions)
    return bom + "".join(output).encode("utf-8")


def build() -> tuple[dict[Path, bytes], dict]:
    statements_path = TABLES / "book-statements.jsonl"
    relations_path = TABLES / "relations.csv"
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    assert "another version, in the City Museum and Art Gallery, Plymouth, was discussed by Anthony Radcliffe in 1978 and 1979" in source_text

    statements = [
        json.loads(line)
        for line in statements_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_id = {row["statement_id"]: row for row in statements}
    original = by_id[ORIGINAL_ID]
    old_claim = "Haskell says another version of the bust was in the City Museum and Art Gallery, Plymouth, and was discussed by Anthony Radcliffe in 1978 and 1979."
    assert original["qualifiers"]["claim"] == old_claim
    assert original["qualifiers"].get("relation_candidate") is True
    assert VARIANT_ID not in by_id and DISCUSSION_ID not in by_id

    revised = json.loads(json.dumps(original, ensure_ascii=False))
    revised["predicate"] = "another_bust_version_was_in_city_museum_and_art_gallery_plymouth"
    revised_q = revised["qualifiers"]
    revised_q.update({
        "source_line_start": 87,
        "source_line_end": 88,
        "claim": "Haskell says another version of the bust was in the City Museum and Art Gallery, Plymouth.",
        "text_layer": "authorial report of an object location",
        "qualification": "The source does not date this location. The relation to the preceding bust and Radcliffe's 1978/1979 discussion are recorded separately.",
        "mentioned_candidate_ids": ["cand-10966", "cand-10969"],
        "related_statement_ids": [VARIANT_ID, DISCUSSION_ID],
        "relation_candidate": True,
        "relation_candidate_note": "The location clause alone maps to held_by; scholarly discussion is preserved in a separate non-graph statement.",
    })
    revised["original_quote"] = "another version, in the City Museum and Art Gallery, Plymouth"

    variant_statement = {
        "statement_id": VARIANT_ID,
        "segment_id": original["segment_id"],
        "subject_candidate_id": "cand-10966",
        "object_candidate_id": "cand-10965",
        "predicate": "haskell_calls_plymouth_bust_another_version_of_preceding_bust",
        "qualifiers": {
            "source_line_start": 87,
            "source_line_end": 87,
            "printed_page": 401,
            "pdf_physical_page": 10,
            "claim": "Haskell calls the Plymouth bust another version of the bust just described as having come into Humphris's possession.",
            "speaker": "Haskell",
            "text_layer": "authorial report of a version relation",
            "qualification": "This follows the source's 'another version' wording; it does not equate the physical objects or identify a common maker.",
            "mentioned_candidate_ids": ["cand-10966", "cand-10965"],
            "related_statement_ids": ["st-chp20-p401-humphris-bust-possession", ORIGINAL_ID],
            "relation_candidate": True,
            "relation_candidate_note": "The explicit version wording supports the controlled variant_of relation; no authorship or object identity is inferred.",
        },
        "original_quote": "another version",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    discussion_statement = {
        "statement_id": DISCUSSION_ID,
        "segment_id": original["segment_id"],
        "subject_candidate_id": "cand-10966",
        "object_candidate_id": "cand-10968",
        "predicate": "haskell_reports_radcliffe_discussed_plymouth_bust_in_1978_and_1979",
        "qualifiers": {
            "source_line_start": 88,
            "source_line_end": 88,
            "printed_page": 401,
            "pdf_physical_page": 10,
            "claim": "Haskell reports that Anthony Radcliffe discussed the Plymouth version in 1978 and 1979.",
            "speaker": "Haskell",
            "text_layer": "authorial report of scholarship",
            "qualification": "The cited studies are separately represented in the linked footnote-citation statements and were not consulted in this batch. No controlled predicate for a scholar's discussion of a work is added.",
            "mentioned_candidate_ids": ["cand-10966", "cand-10968"],
            "related_statement_ids": [ORIGINAL_ID],
            "relation_candidate": False,
        },
        "original_quote": "was discussed by Anthony Radcliffe in 1978 and 1979",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }

    relation_fields, relations, _, _ = read_csv(relations_path)
    assert not any(row.get("relation_id") == RELATION_ID for row in relations)
    assert any(
        row.get("relation_id") == "rel-1452"
        and row.get("subject_ku_id") == "units/works/paolo-giordano-ii-bust-plymouth-version"
        and row.get("predicate") == "held_by"
        and row.get("object_ku_id") == "units/institutions/city-museum-and-art-gallery-plymouth"
        for row in relations
    )
    relation = {
        "relation_id": RELATION_ID,
        "subject_ku_id": "units/works/paolo-giordano-ii-bust-plymouth-version",
        "object_ku_id": "units/works/paolo-giordano-ii-bust-humphris-version",
        "predicate": "variant_of",
        "time": "",
        "role": "来源所称的另一版本",
        "scope": "Haskell称普利茅斯版本为前句所述胸像的“another version”；仅记录来源表达的版本关系，不将两件实物认作同一对象，不推断共同制作或作者归属。",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": "line 87; print p.401; PDF physical p.10; " + VARIANT_ID,
        "source_file": SOURCE_FILE,
        "note": "原书明确使用“another version”；与Humphris持有、普利茅斯馆藏及Bernini归属争论分别记录。",
    }

    _, manifest, _, _ = read_csv(TABLES / "ku-manifest.csv")
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    domain_range = yaml.safe_load(
        (ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8")
    )["domain_range"]
    vocab = yaml.safe_load(
        (ROOT / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml").read_text(encoding="utf-8")
    )["types"]
    assert relation["predicate"] in vocab and relation["predicate"] in domain_range
    spec = domain_range[relation["predicate"]]
    assert manifest_by_id[relation["subject_ku_id"]]["type"] in spec["domain"]
    assert manifest_by_id[relation["object_ku_id"]]["type"] in spec["range"]
    relations.append(relation)

    statements_payload = patched_jsonl(
        statements_path,
        {ORIGINAL_ID: revised},
        [variant_statement, discussion_statement],
    )
    return {
        statements_path: statements_payload,
        relations_path: csv_bytes(relations_path, relation_fields, relations),
    }, {"relation": relation, "statements": [revised, variant_statement, discussion_statement]}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed S2/S6 correction")
    args = parser.parse_args()
    outputs, details = build()
    print(f"S2: split the p.401 compound claim; add {VARIANT_ID} (relation candidate) and {DISCUSSION_ID} (non-graph report)")
    print(f"S6: add {RELATION_ID} variant_of from Plymouth version to the Humphris version")
    print("The existing held_by edge stays scoped to the museum-location clause; no S3 decision changes.")
    print("preview only; pass --apply to write" if not args.apply else "")
    if args.apply:
        for path, payload in outputs.items():
            atomic_write(path, payload)
        print("applied book-statements.jsonl and relations.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
