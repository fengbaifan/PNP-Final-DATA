#!/usr/bin/env python3
"""Reconcile index rows and preserve stable accepted-KU or source-derived candidates."""
from __future__ import annotations

import argparse
import csv
import io
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
INDEX_DIR = BASE / "02-sources" / "03-Index" / "03-2-Index-CSV"
OUTPUT = BASE / "04-knowledge" / "tables" / "entity-candidates.csv"
ALIGNMENTS = BASE / "04-knowledge" / "tables" / "alignment.csv"
MANIFEST = BASE / "04-knowledge" / "tables" / "ku-manifest.csv"
COLUMNS = ["candidate_id", "index_entry_id", "canonical_name", "index_page_range", "suggested_type",
           "status", "index_source_file", "sub_entry", "detail", "exclude_reason",
           "candidate_origin", "candidate_source_ref"]


def read_rows() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(INDEX_DIR.glob("*.csv")):
        raw = path.read_bytes()
        try:
            content = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            content = raw.decode("gb18030")
        for index, row in enumerate(csv.DictReader(io.StringIO(content))):
            main = (row.get("Main Entry") or "").strip()
            if not main:
                continue
            sub = (row.get("Sub-entry") or "").strip()
            detail = (row.get("Detail") or "").strip()
            is_crossref = bool(re.search(r"\bsee\s+under\b", f"{sub} {detail}", re.I))
            reason = f"索引交叉引用：{sub or detail}" if is_crossref else ""
            rows.append({
                "index_entry_id": f"{path.name}#{index}",
                "canonical_name": main,
                "index_page_range": (row.get("Page Numbers") or "").strip(),
                "suggested_type": "",
                "status": "excluded" if is_crossref else "open",
                "index_source_file": path.name,
                "sub_entry": sub,
                "detail": detail,
                "exclude_reason": reason,
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write entity-candidates.csv")
    args = parser.parse_args()
    source_rows = read_rows()
    existing = {}
    existing_accepted = {}
    existing_other = {}
    next_id = 0
    if OUTPUT.exists():
        for row in csv.DictReader(OUTPUT.open(encoding="utf-8-sig", newline="")):
            if row.get("candidate_origin") == "accepted-ku":
                existing_accepted[row.get("candidate_source_ref", "")] = row
            elif row.get("index_entry_id"):
                existing[row.get("index_entry_id", "")] = row
            elif row.get("candidate_origin") and row.get("candidate_source_ref"):
                key = (row["candidate_origin"], row["candidate_source_ref"], row.get("canonical_name", ""))
                existing_other[key] = row
            match = re.fullmatch(r"cand-(\d+)", row.get("candidate_id", ""))
            if match:
                next_id = max(next_id, int(match.group(1)))
    output_rows = []
    for row in source_rows:
        old = existing.get(row["index_entry_id"], {})
        candidate_id = old.get("candidate_id", "")
        if not candidate_id:
            next_id += 1
            candidate_id = f"cand-{next_id:04d}"
        # Preserve prior human decisions for current candidate rows; record every source-index field.
        if row["status"] != "excluded":
            row["status"] = old.get("status") or "open"
            row["suggested_type"] = old.get("suggested_type", "")
            row["exclude_reason"] = old.get("exclude_reason", "")
        output_rows.append({"candidate_id": candidate_id, **row, "candidate_origin": "", "candidate_source_ref": ""})

    # Existing alignments provide an explicit candidate-to-KU mapping. For a
    # chapter-1 KU without one, create an accepted-ku candidate whose source is
    # the already admitted KU card. This makes S2's candidate FK usable without
    # guessing which index spelling denotes the same object.
    aligned_kus = set()
    if ALIGNMENTS.exists():
        with ALIGNMENTS.open(encoding="utf-8-sig", newline="") as handle:
            aligned_kus = {row.get("ku_id", "") for row in csv.DictReader(handle) if row.get("candidate_id") and row.get("ku_id")}
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))
    accepted_output = list(existing_accepted.values())
    newly_added_accepted = []
    for ku in manifest_rows:
        source_ref = ku.get("card_path", "")
        if ku.get("source_task") != "chp-1" or ku.get("ku_id") in aligned_kus:
            continue
        if source_ref in existing_accepted:
            continue
        next_id += 1
        candidate = {
            "candidate_id": f"cand-{next_id:04d}", "index_entry_id": "",
            "canonical_name": ku.get("canonical_name", ""), "index_page_range": "",
            "suggested_type": ku.get("type", ""), "status": "open", "index_source_file": "",
            "sub_entry": "", "detail": "", "exclude_reason": "",
            "candidate_origin": "accepted-ku", "candidate_source_ref": source_ref,
        }
        existing_accepted[source_ref] = candidate
        accepted_output.append(candidate)
        newly_added_accepted.append(candidate)
    output_rows.extend(accepted_output)
    output_rows.extend(existing_other.values())
    ids = [row["candidate_id"] for row in output_rows]
    keys = [row["index_entry_id"] for row in output_rows if row["index_entry_id"]]
    accepted_refs = [row["candidate_source_ref"] for row in output_rows if row.get("candidate_origin") == "accepted-ku"]
    body_refs = [(row.get("candidate_origin", ""), row.get("candidate_source_ref", ""), row.get("canonical_name", ""))
                 for row in output_rows if row.get("candidate_origin") not in {"", "accepted-ku"}]
    if len(ids) != len(set(ids)) or len(keys) != len(set(keys)) or len(accepted_refs) != len(set(accepted_refs)) or len(body_refs) != len(set(body_refs)):
        print("duplicate candidate_id, index_entry_id, accepted KU source ref, or body candidate source+name; refusing to continue")
        return 2
    print(f"index_rows={len(source_rows)} total_candidates={len(output_rows)} open_index_candidates={sum(row['status']=='open' and not row.get('candidate_origin') for row in output_rows)} excluded_crossrefs={sum(row['status']=='excluded' for row in output_rows)} accepted_ku_candidates={sum(row.get('candidate_origin')=='accepted-ku' for row in output_rows)} source_derived_candidates={sum(row.get('candidate_origin') not in {'', 'accepted-ku'} for row in output_rows)} new_chp1_accepted_candidates={len(newly_added_accepted)}")
    for row in newly_added_accepted[:8]:
        print(f"ADD {row['candidate_id']} {row['canonical_name']} [{row['candidate_source_ref']}]")
    if args.apply:
        temp = OUTPUT.with_suffix(OUTPUT.suffix + ".tmp")
        with temp.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(output_rows)
        temp.replace(OUTPUT)
        print(f"applied={OUTPUT.relative_to(BASE)}")
    else:
        print("preview only; pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
