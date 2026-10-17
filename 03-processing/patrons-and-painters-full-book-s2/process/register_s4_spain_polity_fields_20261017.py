from __future__ import annotations
import argparse, csv, difflib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.build_field_facts import (
    BASE, TABLES, ENRICHMENT, SOURCES, extract_records, assign_ids, write_jsonl
)

KU_ID = 'units/institutions/spain-polity'

def main():
    parser = argparse.ArgumentParser(description='Extract and register only the Spain polity card table rows.')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    with (TABLES / 'ku-manifest.csv').open(encoding='utf-8-sig', newline='') as f:
        manifest = list(csv.DictReader(f))
    ku_rows = [row for row in manifest if row.get('ku_id') == KU_ID]
    if len(ku_rows) != 1:
        raise ValueError(f'expected one manifest row for {KU_ID}, got {len(ku_rows)}')
    records, registry, warnings, cards_with_tables = extract_records(ku_rows)
    assign_ids(records, ENRICHMENT)
    if warnings:
        raise ValueError('extractor warnings: ' + '; '.join(warnings))
    if not records or cards_with_tables != 1:
        raise ValueError(f'expected table records; got records={len(records)} cards={cards_with_tables}')
    if set(registry) != {'haskell-1980-rev-ed'}:
        raise ValueError(f'unexpected source IDs: {sorted(registry)}')
    with SOURCES.open(encoding='utf-8-sig', newline='') as f:
        source_rows = list(csv.DictReader(f))
    registered = {row.get('source_id') for row in source_rows}
    if 'haskell-1980-rev-ed' not in registered:
        raise ValueError('Haskell book source is not registered')
    old_records = [json.loads(line) for line in ENRICHMENT.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    old_ids = {row.get('enrichment_id') for row in old_records}
    old_occurrences = {row.get('occurrence_id') for row in old_records}
    if any(row['enrichment_id'] in old_ids for row in records):
        raise ValueError('generated enrichment ID already exists')
    if any(row['occurrence_id'] in old_occurrences for row in records):
        raise ValueError('generated occurrence ID already exists')
    if any(row.get('ku_id') != KU_ID for row in records):
        raise ValueError('extractor returned an unrelated KU row')
    print(json.dumps({'mode':'apply' if args.apply else 'dry-run','ku_id':KU_ID,'records':len(records),'source_ids':sorted(registry),'warnings':warnings,'enrichment_ids':[r['enrichment_id'] for r in records],'existing_records':len(old_records),'new_records':len(records),'sources_csv_changes':0},ensure_ascii=False))
    for row in records:
        print(json.dumps(row,ensure_ascii=False))
    if args.apply:
        write_jsonl(ENRICHMENT, old_records + records)
        print(f'applied {len(records)} records to {ENRICHMENT.relative_to(BASE)}; sources.csv unchanged')

if __name__ == '__main__':
    raise SystemExit(main())