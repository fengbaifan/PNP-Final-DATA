#!/usr/bin/env python3
"""Link legacy alignments that refer to admitted KUs but have no index candidate.

This is a provenance mapping only. It preserves every alignment decision and does
not decide that any external identity is correct.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TABLES = BASE / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
ALIGNMENTS = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ALIGNMENT_EVIDENCE = BASE / "03-processing" / "patrons-and-painters-chp-1" / "process" / "alignment-evidence.jsonl"
CANDIDATE_COLUMNS = ["candidate_id", "index_entry_id", "canonical_name", "index_page_range", "suggested_type",
                     "status", "index_source_file", "sub_entry", "detail", "exclude_reason",
                     "candidate_origin", "candidate_source_ref"]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def read_alignment_evidence() -> list[dict]:
    if not ALIGNMENT_EVIDENCE.is_file():
        return []
    return [json.loads(line) for line in ALIGNMENT_EVIDENCE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="add explicit non-index candidates and link alignments")
    args = parser.parse_args()
    candidates = read_csv(CANDIDATES)
    alignments = read_csv(ALIGNMENTS)
    evidence_rows = read_alignment_evidence()
    manifest = {row["ku_id"]: row for row in read_csv(MANIFEST)}
    by_slug: dict[str, list[dict]] = {}
    for row in manifest.values():
        by_slug.setdefault(Path(row["card_path"]).stem, []).append(row)
    by_existing_origin = {row.get("candidate_source_ref", ""): row for row in candidates if row.get("candidate_origin") == "accepted-ku"}
    max_id = max((int(match.group(1)) for row in candidates if (match := re.fullmatch(r"cand-(\d+)", row.get("candidate_id", "")))), default=0)
    added = []
    linked = 0
    restored = 0
    candidates_added_for_restored = 0
    decisions_restored = 0
    restored_mappings = []
    unresolved = []
    for alignment in alignments:
        if alignment.get("candidate_id"):
            continue
        # Earlier conversion read only `key`; later alignment revisions use
        # `unit`. Recover the exact source row by stable alignment ID order,
        # requiring the retained process_ref to agree before using its locator.
        if alignment.get("legacy_ku_id") == "units/" and evidence_rows:
            match = re.fullmatch(r"aln-(\d+)", alignment.get("alignment_id", ""))
            evidence = evidence_rows[int(match.group(1)) - 1] if match and int(match.group(1)) <= len(evidence_rows) else {}
            if evidence and alignment.get("process_ref") == str(evidence.get("review", "") or ""):
                unit = str(evidence.get("key") or evidence.get("unit") or "").replace("\\", "/").strip()
                if unit and not unit.startswith("units/"):
                    unit = "units/" + unit
                unit = unit.removesuffix(".md")
                ku = manifest.get(unit)
                if ku:
                    alignment["ku_id"] = ku["ku_id"]
                    alignment["resolution_note"] = f"Recovered from alignment-evidence.jsonl by alignment_id order and matching process_ref={alignment['process_ref']}."
                    restored += 1
                    candidate = by_existing_origin.get(ku["card_path"])
                    if candidate is None:
                        max_id += 1
                        candidate = {
                            "candidate_id": f"cand-{max_id:04d}", "index_entry_id": "",
                            "canonical_name": ku["canonical_name"], "index_page_range": "",
                            "suggested_type": ku["type"], "status": "open", "index_source_file": "",
                            "sub_entry": "", "detail": "", "exclude_reason": "",
                            "candidate_origin": "accepted-ku", "candidate_source_ref": ku["card_path"],
                        }
                        by_existing_origin[ku["card_path"]] = candidate
                        candidates.append(candidate)
                        added.append(candidate)
                        candidates_added_for_restored += 1
                    alignment["candidate_id"] = candidate["candidate_id"]
                    qid = next((str(evidence.get(field) or "") for field in
                                ("confirmed_qid", "qid", "wikipedia_item", "pageprops_item")
                                if evidence.get(field)), "")
                    source_status = str(evidence.get("status") or evidence.get("outcome") or "")
                    if qid:
                        alignment["external_source"] = alignment.get("external_source") or "Wikidata"
                        alignment["external_id"] = qid
                    if source_status in {"paired", "identity_paired"} and qid and alignment.get("decision") != "same":
                        alignment["decision"] = "same"
                        decisions_restored += 1
                    alignment["accessed_date"] = alignment.get("accessed_date") or str(evidence.get("access_date") or evidence.get("date") or "")
                    restored_mappings.append((alignment["alignment_id"], ku["ku_id"], candidate["candidate_id"], alignment["decision"], qid))
                    linked += 1
                    continue
                unresolved.append(alignment.get("alignment_id", ""))
                continue
        ku = manifest.get(alignment.get("ku_id", ""))
        if ku is None:
            slug = alignment.get("ku_id", "").rstrip("/").split("/")[-1]
            matches = by_slug.get(slug, []) if slug else []
            if len(matches) == 1:
                ku = matches[0]
                alignment["ku_id"] = ku["ku_id"]
        if not ku:
            if alignment.get("ku_id", "") == "units/":
                alignment["legacy_ku_id"] = "units/"
                alignment["ku_id"] = ""
                if alignment.get("decision") == "same" and not alignment.get("external_id"):
                    alignment["decision"] = "undecided"
                alignment["resolution_note"] = "迁移输入缺失原对象路径与候选名称；身份映射保留为待决。"
            unresolved.append(alignment.get("alignment_id", ""))
            continue
        card_path = ku["card_path"]
        candidate = by_existing_origin.get(card_path)
        if candidate is None:
            max_id += 1
            candidate = {
                "candidate_id": f"cand-{max_id:04d}",
                "index_entry_id": "",
                "canonical_name": ku["canonical_name"],
                "index_page_range": "",
                "suggested_type": ku["type"],
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": "",
                "exclude_reason": "",
                "candidate_origin": "accepted-ku",
                "candidate_source_ref": card_path,
            }
            by_existing_origin[card_path] = candidate
            candidates.append(candidate)
            added.append(candidate)
        alignment["candidate_id"] = candidate["candidate_id"]
        linked += 1
    print(f"alignment_rows={len(alignments)} linked_now={linked} restored_from_source={restored} decisions_restored={decisions_restored} new_nonindex_candidates={len(added)} restored_candidates_added={candidates_added_for_restored} unresolved={len(unresolved)}")
    for row in added[:8]:
        print(f"ADD {row['candidate_id']} {row['suggested_type']} {row['canonical_name']} [{row['candidate_source_ref']}]")
    for alignment_id, ku_id, candidate_id, decision, qid in restored_mappings:
        print(f"RESTORE {alignment_id} -> {ku_id} {candidate_id} decision={decision} external_id={qid or '<none>'}")
    if unresolved:
        print(f"UNRESOLVED (retained for explicit follow-up): {','.join(unresolved[:40])}")
    if args.apply:
        write_csv(CANDIDATES, candidates, CANDIDATE_COLUMNS)
        write_csv(ALIGNMENTS, alignments, ["alignment_id", "candidate_id", "ku_id", "external_source", "external_id", "decision", "accessed_date", "process_ref", "legacy_ku_id", "resolution_note"])
        print("applied candidate provenance links and recovered directly recorded alignment outcomes")
    else:
        print("preview only; pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
