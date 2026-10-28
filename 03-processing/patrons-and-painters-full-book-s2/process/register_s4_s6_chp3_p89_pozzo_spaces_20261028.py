#!/usr/bin/env python3
"""Preview/apply S4 registration and S6 decisions for Pozzo's S. Ignazio endpoints."""
from __future__ import annotations

import argparse
import csv
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp3-p89-pozzo-spaces-20261028"
TASK = "patrons-and-painters-full-book-s2"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
WORK_KU = "units/works/pozzo-fresco-cycle-tribune-apse-s-ignazio"
POZZO_KU = "units/persons/andrea-pozzo"
EVENT_KU = "units/events/la-storta-promise-to-st-ignatius"
APSE_KU = "units/places/apse-of-s-ignazio"
TRIBUNE_KU = "units/places/tribune-of-s-ignazio"
NEW_ENDPOINTS = {
    "cand-5096": (APSE_KU, "place", "圣依纳爵堂后殿空间", "Apse of S. Ignazio", "04-knowledge/units/places/apse-of-s-ignazio.md"),
    "cand-5372": (TRIBUNE_KU, "place", "圣依纳爵堂祭坛席空间", "Tribune of S. Ignazio", "04-knowledge/units/places/tribune-of-s-ignazio.md"),
    "cand-5374": ("units/places/la-storta", "place", "拉斯托尔塔", "La Storta", "04-knowledge/units/places/la-storta.md"),
}
EXPECTED_MAPPINGS = {
    "cand-5373": WORK_KU,
    "cand-2034": POZZO_KU,
    "cand-5375": EVENT_KU,
    "cand-3403": "units/institutions/jesuits",
    "cand-4500": "units/terms/baroque-cultural-category-haskell",
}
FORMAL_SPECS = [
    ("st-chp3-seciv-l130-139-pozzo-painted-later-cycle", WORK_KU, "created_by", POZZO_KU,
     "1685年后若干年（确切年份未载）", "壁画作者", "仅记录 Haskell 对该壁画组的创作者归属和宽泛时间；不推断精确创作或完工年份。", "Haskell 于第3章 p.89 L138 明确称 Pozzo 绘制了该壁画组。"),
    ("st-chp3-seciv-l130-139-pozzo-painted-frescoes-in-tribune", WORK_KU, "located_at", TRIBUNE_KU,
     "1685年后若干年（确切年份未载）", "壁画所在空间", "Haskell 所述 Pozzo 壁画组位于 S. Ignazio 的祭坛席；不推断现状或精确建筑边界。", "Haskell 于第3章 p.89 L138 将该壁画组定位在 S. Ignazio 祭坛席。"),
    ("st-chp3-seciv-l130-139-pozzo-painted-frescoes-in-apse", WORK_KU, "located_at", APSE_KU,
     "1685年后若干年（确切年份未载）", "壁画所在空间", "Haskell 所述 Pozzo 壁画组位于 S. Ignazio 的后殿；不推断现状或精确建筑边界。", "Haskell 于第3章 p.89 L138 将该壁画组定位在 S. Ignazio 后殿。"),
    ("st-chp3-seciv-l130-139-promise-event-at-la-storta", EVENT_KU, "occurred_at", "units/places/la-storta",
     "", "Haskell 所述宗教叙事的场景", "仅记录 Haskell 叙事中该应许场景位于 La Storta；不构成独立历史事实或现代地点定位。", "Haskell 于第3章 p.89 L138–139 将 La Storta 称作该宗教叙事的地点；本边只记录书内叙事定位。"),
]
DECIDED_NONFORMAL = {
    "st-chp3-seciv-l130-139-cycle-culminates-in-la-storta-promise": "pending: Haskell clearly identifies the La Storta promise narrative as the fresco cycle's culmination, but the current relation-domain/range contract does not allow a work-to-event has_subject edge. Preserve the source claim in the work and event descriptions; reopen only if the controlled relation model gains an accurate work-depicts-event expression.",
    "st-chp3-seciv-l130-139-cycle-depicts-early-society-events": "rejected: statement describes unnamed events in the Society's early history, but its current object endpoint is the Jesuit institution itself; no specific event endpoint is supplied. Retain the source-based description and the separately identified La Storta narrative-location edge; do not encode the institution as the depicted event.",
    "st-chp3-seciv-l141-150-cycle-compared-with-gaulli": "pending: the comparison's Gesù fresco endpoint cand-5244 remains S3 undecided and has no KU. Reassess only after the work identity/version is resolved; do not infer the specific work from the following sentence naming The Adoration of the Lamb.",
    "st-chp3-seciv-l141-150-cycle-reaction-against-baroque": "rejected as a formal edge: this is Haskell's qualified art-historical interpretation, and the controlled vocabulary has no exact predicate for a reaction against a broad cultural category. Preserve the interpretation in the work description; do not substitute influenced_by or a neutral classification.",
    "st-chp3-seciv-l141-150-jesuits-welcomed-different-work": "rejected as a formal edge: Haskell reports acceptance and welcome, but no controlled relation type expresses institutional reception without implying patronage, commission, or support. Preserve the reception claim and its either/or explanation in the work description.",
}


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def csv_bytes(path: Path, fields, rows) -> bytes:
    import io
    buffer = io.StringIO(newline="")
    line_ending = "\r\n" if b"\r\n" in path.read_bytes() else "\n"
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def insert_sorted_unit_paths(accepted: str, card_paths: list[str]) -> str:
    marker = "claims:\n"
    if marker not in accepted:
        raise ValueError("accepted.yml claims section not found")
    units_text, rest = accepted.split(marker, 1)
    lines = units_text.splitlines(keepends=True)
    for card_path in card_paths:
        entry = f"- {card_path}\n"
        if entry.rstrip("\n") in {line.rstrip("\r\n") for line in lines}:
            continue
        insert_at = next((i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:].strip() > card_path), len(lines))
        lines.insert(insert_at, entry)
    return "".join(lines) + marker + rest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed S4/S6 batch")
    args = parser.parse_args()

    paths = {
        "alignment": TABLES / "alignment.csv",
        "manifest": TABLES / "ku-manifest.csv",
        "relations": TABLES / "relations.csv",
        "statements": TABLES / "book-statements.jsonl",
        "accepted": ROOT / "04-knowledge" / "accepted.yml",
    }
    align_fields, alignments = read_csv(paths["alignment"])
    manifest_fields, manifest = read_csv(paths["manifest"])
    relation_fields, relations = read_csv(paths["relations"])
    statements = [json.loads(line) for line in paths["statements"].read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    accepted = paths["accepted"].read_text(encoding="utf-8-sig")
    by_candidate = {}
    for row in alignments:
        by_candidate.setdefault(row["candidate_id"], []).append(row)

    to_register = []
    for candidate, (ku_id, expected_type, zh, en, card_path) in NEW_ENDPOINTS.items():
        rows = [r for r in by_candidate.get(candidate, []) if r["external_source"] == ""]
        if len(rows) != 1 or rows[0]["decision"] != "new" or rows[0]["ku_id"] not in {"", ku_id}:
            raise ValueError(f"S3/S4 precondition failed for {candidate}: {rows}")
        existing_manifest = [r for r in manifest if r["ku_id"] == ku_id]
        if rows[0]["ku_id"]:
            if len(existing_manifest) != 1 or existing_manifest[0]["card_path"] != card_path:
                raise ValueError(f"existing KU mapping/manifest mismatch for {candidate}: {existing_manifest}")
        else:
            if existing_manifest:
                raise ValueError(f"KU already registered without alignment mapping: {ku_id}")
            to_register.append(candidate)
        if not (ROOT / card_path).is_file():
            raise ValueError(f"create and inspect the target card before applying: {card_path}")
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    for candidate, ku_id in EXPECTED_MAPPINGS.items():
        rows = by_candidate.get(candidate, [])
        if len([r for r in rows if r["external_source"] == ""]) != 1 or not any(r["ku_id"] == ku_id for r in rows):
            raise ValueError(f"expected existing candidate mapping not found: {candidate} -> {ku_id}")
        if ku_id not in manifest_by_ku:
            raise ValueError(f"existing endpoint missing from manifest: {ku_id}")

    statement_by_id = {row["statement_id"]: row for row in statements}
    all_decided = [spec[0] for spec in FORMAL_SPECS] + list(DECIDED_NONFORMAL)
    for statement_id in all_decided:
        statement = statement_by_id.get(statement_id)
        if not statement or not statement.get("qualifiers", {}).get("relation_candidate"):
            raise ValueError(f"relation candidate precondition failed: {statement_id}")
    expected_endpoints = {
        "st-chp3-seciv-l130-139-pozzo-painted-later-cycle": ("cand-2034", "cand-5373"),
        "st-chp3-seciv-l130-139-pozzo-painted-frescoes-in-tribune": ("cand-5373", "cand-5372"),
        "st-chp3-seciv-l130-139-pozzo-painted-frescoes-in-apse": ("cand-5373", "cand-5096"),
        "st-chp3-seciv-l130-139-cycle-culminates-in-la-storta-promise": ("cand-5373", "cand-5375"),
        "st-chp3-seciv-l130-139-promise-event-at-la-storta": ("cand-5375", "cand-5374"),
        "st-chp3-seciv-l130-139-cycle-depicts-early-society-events": ("cand-5373", "cand-3403"),
        "st-chp3-seciv-l141-150-cycle-compared-with-gaulli": ("cand-5373", "cand-5244"),
        "st-chp3-seciv-l141-150-cycle-reaction-against-baroque": ("cand-5373", "cand-4500"),
        "st-chp3-seciv-l141-150-jesuits-welcomed-different-work": ("cand-3403", "cand-5373"),
    }
    for statement_id, endpoints in expected_endpoints.items():
        actual = (statement_by_id[statement_id].get("subject_candidate_id"), statement_by_id[statement_id].get("object_candidate_id"))
        if actual != endpoints:
            raise ValueError(f"candidate endpoints changed for {statement_id}: {actual}")
    undecided = by_candidate.get("cand-5244", [])
    if not any(r["decision"] == "undecided" and not r["ku_id"] for r in undecided):
        raise ValueError("Gesù frescoes comparison endpoint is no longer S3 undecided")

    # The two new places are registered from source-bounded identity decisions.
    for candidate in to_register:
        ku_id, _kind, _zh, _en, card_path = NEW_ENDPOINTS[candidate]
        row = next(r for r in by_candidate[candidate] if r["external_source"] == "")
        row["ku_id"] = ku_id
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = row["resolution_note"].rstrip() + f" S4 registration (2026-10-28): registered source-bounded place KU {ku_id}; no external identity, parent-space relation, or current condition is asserted. process_ref={PROCESS_REF}."
    manifest.extend(
        {"ku_id": NEW_ENDPOINTS[candidate][0], "type": NEW_ENDPOINTS[candidate][1], "canonical_name": NEW_ENDPOINTS[candidate][2],
         "name_en": NEW_ENDPOINTS[candidate][3], "source_task": TASK, "card_path": NEW_ENDPOINTS[candidate][4]}
        for candidate in to_register
    )

    superseded_candidate = "st-chp3-seciv-l130-139-cycle-culminates-in-la-storta-promise"
    superseded = [r for r in relations if f"statement={superseded_candidate}" in r["source_span"]]
    if superseded:
        if len(superseded) != 1 or (superseded[0]["relation_id"], superseded[0]["subject_ku_id"], superseded[0]["predicate"], superseded[0]["object_ku_id"]) != ("rel-2520", WORK_KU, "has_subject", EVENT_KU):
            raise ValueError(f"unexpected existing relation for pending candidate {superseded_candidate}: {superseded}")
        relations.remove(superseded[0])
    next_relation = max(int(r["relation_id"].split("-")[1]) for r in relations) + 1
    for statement_id, subject, predicate, object_, time, role, scope, note in FORMAL_SPECS:
        natural = (subject, predicate, object_, time, role, scope)
        evidence_matches = [r for r in relations if f"statement={statement_id}" in r["source_span"]]
        if evidence_matches:
            if len(evidence_matches) != 1:
                raise ValueError(f"duplicate relation rows cite {statement_id}: {evidence_matches}")
            existing = evidence_matches[0]
            if (existing["subject_ku_id"], existing["predicate"], existing["object_ku_id"], existing["status"], existing["source_id"]) != (subject, predicate, object_, "formal", SOURCE_ID):
                raise ValueError(f"existing adjudication conflicts with reviewed decision for {statement_id}: {existing}")
            existing.update({"time": time, "role": role, "scope": scope, "note": note, "source_span": f"Chapter 3, printed p. 89, lines 138–139; statement={statement_id}"})
            continue
        existing = [r for r in relations if (r["subject_ku_id"], r["predicate"], r["object_ku_id"], r["time"], r["role"], r["scope"]) == natural]
        if existing:
            if len(existing) != 1 or existing[0]["status"] != "formal" or f"statement={statement_id}" not in existing[0]["source_span"]:
                raise ValueError(f"conflicting or duplicate existing relation: {natural}; {existing}")
            continue
        relations.append({
            "relation_id": f"rel-{next_relation:04d}", "subject_ku_id": subject, "object_ku_id": object_,
            "predicate": predicate, "time": time, "role": role, "scope": scope, "origin": "book", "status": "formal",
            "source_id": SOURCE_ID, "source_span": f"Chapter 3, printed p. 89, lines 138–139; statement={statement_id}",
            "source_file": SOURCE_FILE, "note": note,
        })
        next_relation += 1

    card_paths = [value[4] for value in NEW_ENDPOINTS.values()]
    accepted = insert_sorted_unit_paths(accepted, card_paths)
    outputs = {
        paths["alignment"]: csv_bytes(paths["alignment"], align_fields, alignments),
        paths["manifest"]: csv_bytes(paths["manifest"], manifest_fields, manifest),
        paths["relations"]: csv_bytes(paths["relations"], relation_fields, relations),
        paths["accepted"]: accepted.encode("utf-8"),
    }
    print("PREVIEW" if not args.apply else "APPLY")
    print("S4: 3 source-bounded places registered; existing S3 decisions retained.")
    print("S6: 4 formal rows (created_by, 2 located_at, occurred_at); 2 pending and 3 rejected decisions are recorded in process/knowledge.md.")
    for path, data in outputs.items():
        before = path.read_bytes()
        if before == data:
            continue
        diff = difflib.unified_diff(before.decode("utf-8-sig").splitlines(keepends=True), data.decode("utf-8-sig").splitlines(keepends=True), fromfile="before", tofile="after")
        print(f"--- {path.relative_to(ROOT)}")
        print("".join(diff), end="")
    if not args.apply:
        return
    originals = {path: path.read_bytes() for path in outputs}
    try:
        for path, data in outputs.items():
            path.write_bytes(data)
    except Exception:
        for path, data in originals.items():
            path.write_bytes(data)
        raise
    print(f"Applied {len(outputs)} reviewed table/registry files; rollback snapshot retained in memory until all writes succeeded.")


if __name__ == "__main__":
    main()
