#!/usr/bin/env python3
"""One-time migration of retained card relation qualifiers into relations.csv.

Matches by endpoints, predicate and exact evidence locator. Existing table values
win on conflict; the source note is preserved only for a uniquely matched row.
"""
from __future__ import annotations

import argparse
import csv
import json
import posixpath
import re
from collections import defaultdict
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
TABLES = BASE / "04-knowledge" / "tables"
RELATIONS = TABLES / "relations.csv"
KU_TYPES = ("persons", "families", "institutions", "places", "works", "archives", "terms", "procedures", "events")
QUALIFIERS = ("time", "role", "scope")
RELATION_COLUMNS = ["relation_id", "subject_ku_id", "object_ku_id", "predicate", "time", "role", "scope", "origin",
                    "status", "source_id", "source_span", "source_file", "note"]


def norm(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def normalize_target(source_card: Path, target: str) -> str:
    value = target.replace("\\", "/").strip()
    for prefix in ("04-knowledge/units/", "units/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    while value.startswith("../"):
        value = value[3:]
    while value.startswith("./"):
        value = value[2:]
    if not value.startswith(tuple(f"{kind}/" for kind in KU_TYPES)):
        value = posixpath.normpath(posixpath.join(source_card.parent.relative_to(UNITS).as_posix(), value))
    return value


def read_relations() -> list[dict]:
    with RELATIONS.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def plan_migration() -> tuple[list[dict], dict]:
    rows = read_relations()
    buckets: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        subject = row["subject_ku_id"].removeprefix("units/") + ".md"
        obj = row["object_ku_id"].removeprefix("units/") + ".md"
        buckets[(subject, row["predicate"], obj)].append(index)
    units_with_edges = 0
    matched = 0
    unmatched = []
    ambiguous = []
    reused = set()
    notes_added = 0
    qualifiers_added = 0
    source_ids_added = 0
    locators_repaired = 0
    source_id_ambiguities = []
    formal_rows_recovered = []
    local_by_url: dict[str, list[str]] = defaultdict(list)
    for source in csv.DictReader((TABLES / "sources.csv").open(encoding="utf-8-sig", newline="")):
        if source.get("url") and source.get("source_id"):
            local_by_url[norm(source["url"])].append(source["source_id"])
    for card in UNITS.rglob("*.md"):
        text = card.read_text(encoding="utf-8-sig")
        parts = re.match(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
        if not parts:
            continue
        fm = yaml.safe_load(parts.group(1)) or {}
        card_edges = fm.get("relations") or []
        if not isinstance(card_edges, list):
            continue
        for edge in card_edges:
            if not isinstance(edge, dict):
                continue
            units_with_edges += 1
            key = (card.relative_to(UNITS).as_posix(), str(edge.get("relation_type", "")), normalize_target(card, str(edge.get("target", ""))))
            candidates = [i for i in buckets.get(key, []) if i not in reused]
            evidence = edge.get("evidence_ref") if isinstance(edge.get("evidence_ref"), dict) else {}
            source_file, source_span = norm(evidence.get("source_file")), norm(evidence.get("source_span"))
            exact = [i for i in candidates if norm(rows[i].get("source_file")) == source_file and norm(rows[i].get("source_span")) == source_span]
            # A small number of recent rows were imported with a truncated URL
            # and blank span. Recover those only when endpoints + predicate
            # leave exactly one unused row and the card retains both locators.
            if not exact and source_file and source_span:
                incomplete = [i for i in candidates if not rows[i].get("source_span") or not norm(rows[i].get("source_file"))]
                if len(incomplete) == 1:
                    exact = incomplete
            if len(exact) > 1:
                def score(index: int) -> int:
                    return sum(bool(edge.get(field)) and bool(rows[index].get(field)) and norm(edge[field]) == norm(rows[index][field]) for field in QUALIFIERS)
                scores = {i: score(i) for i in exact}
                best = max(scores.values(), default=0)
                exact = [i for i in exact if scores[i] == best and best > 0]
            if len(exact) != 1:
                # Restore an admitted edge that was absent from the table only
                # when the card itself records an evidence-backed decision,
                # its endpoint exists, and the natural key is not present.
                if not candidates and edge.get("review_status") == "evidence_backed_relation" and source_file and source_span:
                    source_path = UNITS / key[0]
                    target_path = UNITS / (key[2] if key[2].endswith(".md") else key[2] + ".md")
                    if source_path.is_file() and target_path.is_file():
                        next_id = max((int(re.sub(r"\D", "", r["relation_id"]) or 0) for r in rows), default=0) + 1
                        recovered = {column: "" for column in RELATION_COLUMNS}
                        recovered.update({
                            "relation_id": f"rel-{next_id:04d}", "subject_ku_id": "units/" + key[0][:-3],
                            "object_ku_id": "units/" + key[2][:-3], "predicate": key[1],
                            "time": str(edge.get("time", "") or ""), "role": str(edge.get("role", "") or ""),
                            "scope": str(edge.get("scope", "") or ""), "origin": "explicit", "status": "formal",
                            "source_file": str(evidence.get("source_file", "")),
                            "source_span": str(evidence.get("source_span", "")), "note": str(edge.get("note", "") or ""),
                        })
                        rows.append(recovered)
                        buckets[(key[0][:-3], key[1], key[2][:-3])].append(len(rows) - 1)
                        reused.add(len(rows) - 1)
                        matched += 1
                        notes_added += bool(recovered["note"])
                        qualifiers_added += sum(bool(recovered[field]) for field in QUALIFIERS)
                        locators_repaired += 1
                        formal_rows_recovered.append(recovered["relation_id"])
                        continue
                item = {"card": card.relative_to(BASE).as_posix(), "predicate": edge.get("relation_type"), "target": edge.get("target"), "source_file": evidence.get("source_file"), "source_span": evidence.get("source_span"), "candidate_relation_ids": [rows[i]["relation_id"] for i in (exact or candidates)]}
                (ambiguous if exact or candidates else unmatched).append(item)
                continue
            index = exact[0]
            row = rows[index]
            reused.add(index)
            matched += 1
            note = str(edge.get("note", "") or "").strip()
            if note and not row.get("note"):
                row["note"] = note
                notes_added += 1
            for field in QUALIFIERS:
                value = str(edge.get(field, "") or "").strip()
                if value and not row.get(field):
                    row[field] = value
                    qualifiers_added += 1
            if not row.get("source_id") and source_file.startswith(("http://", "https://")):
                matches = local_by_url.get(norm(source_file), [])
                if len(matches) == 1:
                    row["source_id"] = matches[0]
                    source_ids_added += 1
                elif len(matches) > 1:
                    source_id_ambiguities.append({"card": card.relative_to(BASE).as_posix(), "relation_id": row["relation_id"], "source_url_match_count": len(matches)})
            elif not row.get("source_id") and source_file.startswith("02-sources/"):
                row["source_id"] = "haskell-1980-rev-ed"
                source_ids_added += 1
            if source_span and (not row.get("source_span") or not row.get("source_file") or norm(row.get("source_file")) != source_file):
                row["source_file"] = str(evidence.get("source_file", ""))
                row["source_span"] = str(evidence.get("source_span", ""))
                locators_repaired += 1
    result = {"card_relation_rows": units_with_edges, "uniquely_matched": matched, "relation_rows_without_card_context": len(rows) - len(reused),
              "notes_added": notes_added, "qualifier_cells_added": qualifiers_added, "source_ids_added": source_ids_added,
              "locators_repaired": locators_repaired, "source_id_ambiguities": source_id_ambiguities,
              "formal_rows_recovered": formal_rows_recovered, "ambiguous": ambiguous, "unmatched": unmatched}
    return rows, result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write uniquely matched retained context to relations.csv")
    args = parser.parse_args()
    rows, result = plan_migration()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["ambiguous"] or result["unmatched"]:
        print("Refusing to apply while any retained card edge lacks a unique evidence-backed match.")
        return 2
    if args.apply:
        temp = RELATIONS.with_suffix(".csv.tmp")
        with temp.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=RELATION_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        temp.replace(RELATIONS)
        print(f"applied={RELATIONS.relative_to(BASE)}")
    else:
        print("preview only; pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
