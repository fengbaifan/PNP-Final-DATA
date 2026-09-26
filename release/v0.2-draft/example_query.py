#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description="Query one entity from this dataset package.")
parser.add_argument("ku_id", nargs="?", default="units/persons/guercino")
parser.add_argument("--full", action="store_true", help="include complete evidence and relation rows")
args = parser.parse_args()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def read_csv(name):
    with (root / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

entity = next((r for r in read_csv("entities.csv") if r["ku_id"] == args.ku_id), None)
if entity is None:
    raise SystemExit(f"Unknown ku_id: {args.ku_id}")
enrichment = [json.loads(line) for line in (root / "enrichment.jsonl").read_text(encoding="utf-8").splitlines() if line]
relations = read_csv("relations.csv")
fields = [r for r in enrichment if r["ku_id"] == args.ku_id]
field_ids = {r["enrichment_id"] for r in fields}
references = [r for r in read_csv("portable-references.csv") if r["enrichment_id"] in field_ids]
outgoing = [r for r in relations if r["subject_ku_id"] == args.ku_id]
incoming = [r for r in relations if r["object_ku_id"] == args.ku_id]
if args.full:
    result = {"entity": entity, "fields": fields, "portable_references": references,
              "outgoing_relations": outgoing, "incoming_relations": incoming}
else:
    field_sample = fields[:5]
    result = {
        "entity": entity,
        "field_count": len(fields),
        "fields_sample": [{key: row.get(key, "") for key in ("field", "value", "evidence_status", "source_ref")} for row in field_sample],
        "fields_omitted": max(0, len(fields) - len(field_sample)),
        "portable_reference_count": len(references),
        "portable_references_sample": references[:5],
        "portable_references_omitted": max(0, len(references) - 5),
        "outgoing_relations": [{key: row.get(key, "") for key in ("relation_id", "object_ku_id", "predicate", "status", "source_id")} for row in outgoing],
        "incoming_relations": [{key: row.get(key, "") for key in ("relation_id", "subject_ku_id", "predicate", "status", "source_id")} for row in incoming],
    }
print(json.dumps(result, ensure_ascii=False, indent=2))
