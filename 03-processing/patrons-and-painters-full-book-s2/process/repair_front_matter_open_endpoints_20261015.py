from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
SEGMENTS = TABLE_DIR / "segments.jsonl"
COVERAGE = TABLE_DIR / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "00_05_List_of_Plates.md"

EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "3a2657206a473e52ba00f8b2798ead93096a0a5a4bed6a133937ccd94ad99c2a",
    MENTIONS: "0f94db41865447debd1d5861257a7e89219f361ceb2810ef4909c14a04111d16",
    STATEMENTS: "15d9ecb790d2b8295e918f7f7fe7b9f29a29e847ba80c0e6d9d7fc54cf4a8d32",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    COVERAGE: "1352b756f0f0310c00d21bfc3bfe194b5a347d291b699db78b5c85fa6e636a4d",
    SOURCE: "96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83",
}

BACKUPS = {
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-fm-open-endpoints-20261015"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-fm-open-endpoints-20261015"),
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-fm-open-endpoints-20261015"),
}

GROUPS = [
    {
        "candidate_id": "cand-12263",
        "mention_id": "m-fm-2ed-l174-185-group-migration",
        "statement_id": "st-fm-2ed-l174-185-10-group-migration",
        "segment_id": "front-matter:00_05_List_of_Plates:l174-185",
        "surface": "a number of the ablest painters",
        "expected_start": None,
        "source_line": 180,
        "canonical_name": "Painters said to have moved to Rome from Naples or Tuscany (Waterhouse source-defined group)",
        "detail": "Waterhouse describes an unbounded group of painters who moved to Rome, naming Conca, Giaquinto and Batoni as examples. The two possible origins, Naples and Tuscany, are not paired to individuals. Type remains unset because the taxonomy has no person-group type.",
        "note": "Exact source phrase for the group of painters; the three named examples and both unpaired origin alternatives remain in the qualifiers.",
    },
    {
        "candidate_id": "cand-12264",
        "mention_id": "m-fm-2ed-l174-185-group-refusers",
        "statement_id": "st-fm-2ed-l174-185-11-refusal-explanation",
        "segment_id": "front-matter:00_05_List_of_Plates:l174-185",
        "surface": "such minor personalities",
        "expected_start": None,
        "source_line": 182,
        "canonical_name": "Painters said to have refused to settle in Rome under pressure (Waterhouse source-defined group)",
        "detail": "Waterhouse's group claim includes P. G. Piola, Viani and Lazzarini as examples; their identities remain unresolved. Fear of competition is Waterhouse's proposed group-level explanation, not verified testimony by the painters. Type remains unset because the taxonomy has no person-group type.",
        "note": "Group descriptor mapped without overlapping the separately mapped name mentions; the source's proposed motive and unresolved identities remain qualified.",
    },
    {
        "candidate_id": "cand-12265",
        "mention_id": "m-fm-2ed-l174-185-group-guido-guercino",
        "statement_id": "st-fm-2ed-l174-185-12-guido-guercino-comparison",
        "segment_id": "front-matter:00_05_List_of_Plates:l174-185",
        "surface": "Guido and Guercino",
        "expected_start": 1628,
        "source_line": 183,
        "canonical_name": "Guido and Guercino as seventeenth-century refusal examples (source-defined group)",
        "detail": "The quoted comparison treats Guido and Guercino together as examples of painters who refused to stay in Rome in the seventeenth century. Guercino maps to cand-3062; Guido remains identity-unresolved as cand-4205. No specific occasion is supplied. Type remains unset because the taxonomy has no person-group type.",
        "note": "The group mention contains the two separately mapped person mentions; Guido's identity remains open and the source gives no particular refusal occasion.",
    },
    {
        "candidate_id": "cand-12266",
        "mention_id": "m-fm-2ed-l174-185-group-disjunctive-list",
        "statement_id": "st-fm-2ed-l174-185-14-disjunctive-painter-claim",
        "segment_id": "front-matter:00_05_List_of_Plates:l174-185",
        "surface": "list of distinguished",
        "expected_start": None,
        "source_line": 184,
        "canonical_name": "Distinguished Italian artists in Haskell's Rome comparison (source-defined group)",
        "detail": "Haskell describes a formidable, non-exhaustive list and names Crespi and Solimena as examples. The alternatives (no consequential work for Rome's principal churches or palaces, or visiting only as tourists) are not assigned to either person. Crespi's identity remains unresolved. Type remains unset because the taxonomy has no person-group type.",
        "note": "Source-defined list mapped as a group; participant candidates retain the two named examples and the disjunctive criteria remain group-level.",
    },
    {
        "candidate_id": "cand-12267",
        "mention_id": "m-fm-2ed-l174-185-group-later-generation",
        "statement_id": "st-fm-2ed-l174-185-17-later-generation",
        "segment_id": "front-matter:00_05_List_of_Plates:l174-185",
        "surface": "Giaquinto and Batoni",
        "expected_start": 2302,
        "source_line": 184,
        "canonical_name": "Giaquinto and Batoni as the later generation arriving in Rome (source-defined group)",
        "detail": "Haskell says Giaquinto and Batoni came to Rome a generation later than the previously discussed painters. Rome is inherited from the preceding sentence; the relative chronology has no exact date. Type remains unset because the taxonomy has no person-group type.",
        "note": "The paired grammatical subject is mapped as a source-defined group; participant candidates and the relative, non-absolute chronology remain explicit.",
    },
    {
        "candidate_id": "cand-12268",
        "mention_id": "m-fm-pl-p64-private-collection",
        "statement_id": "st-fm-pl-p64-private-collection",
        "segment_id": "front-matter:00_05_List_of_Plates:l140-172",
        "surface": "Private Collection",
        "expected_start": 395,
        "source_line": 148,
        "canonical_name": "Unidentified private collection in London (plate 64 caption)",
        "detail": "The caption places the work in an unnamed private collection in London. The owner and collection identity are not supplied; type remains unset because the taxonomy has no collection type.",
        "note": "Anonymous collection as stated in the caption; no owner, institution or current custody is inferred.",
    },
    {
        "candidate_id": "cand-12269",
        "mention_id": "m-fm-pl-p68a-private-collections",
        "statement_id": "st-fm-pl-p68a-private",
        "segment_id": "front-matter:00_05_List_of_Plates:l140-172",
        "surface": "Private Collections",
        "expected_start": None,
        "source_line": 158,
        "canonical_name": "Unidentified private collections for plate 68a (caption group)",
        "detail": "The caption uses a plural private-collections label for the three portraits but identifies neither the collections nor their number or owners. Type remains unset because the taxonomy has no collection-group type.",
        "note": "Plural anonymous collection label mapped as a source-defined group; no specific holder or current custody is inferred.",
    },
]

EXPECTED_STATEMENTS = {
    "st-fm-2ed-l174-185-10-group-migration": (None, "cand-3126", ["cand-3881", "cand-3786", "cand-3871"]),
    "st-fm-2ed-l174-185-11-refusal-explanation": (None, "cand-3126", ["cand-4202", "cand-4203", "cand-4204"]),
    "st-fm-2ed-l174-185-12-guido-guercino-comparison": (None, "cand-3126", ["cand-4205", "cand-3062"]),
    "st-fm-2ed-l174-185-14-disjunctive-painter-claim": (None, "cand-3126", ["cand-4206", "cand-3884"]),
    "st-fm-2ed-l174-185-17-later-generation": (None, "cand-3126", ["cand-3786", "cand-3871"]),
    "st-fm-pl-p64-private-collection": ("cand-4036", None, None),
    "st-fm-pl-p68a-private": ("cand-4190", None, None),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def serialize_csv_row(headers: list[str], row: dict[str, str]) -> bytes:
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n", extrasaction="ignore").writerow(row)
    return buffer.getvalue().encode("utf-8")


def append_bytes(current: bytes, addition: bytes) -> bytes:
    separator = b"" if current.endswith((b"\n", b"\r")) else b"\n"
    return current + separator + addition


def validate_and_build() -> tuple[dict[Path, bytes], dict[str, str]]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit(f"HEAD changed: expected {EXPECTED_HEAD}, got {head}")
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"{path.relative_to(ROOT)} hash changed: expected {expected}, got {actual}")

    candidate_bytes, mention_bytes, statement_bytes = CANDIDATES.read_bytes(), MENTIONS.read_bytes(), STATEMENTS.read_bytes()
    candidate_headers, candidates = parse_csv(candidate_bytes)
    mention_headers, mentions = parse_csv(mention_bytes)
    if len(candidates) != 12_240 or len(mentions) != 26_428:
        raise SystemExit("unexpected candidate or mention row counts")
    candidate_ids = [row["candidate_id"] for row in candidates]
    mention_ids = [row["mention_id"] for row in mentions]
    if len(candidate_ids) != len(set(candidate_ids)) or len(mention_ids) != len(set(mention_ids)):
        raise SystemExit("duplicate candidate or mention IDs already exist")
    existing_candidates, existing_mentions = set(candidate_ids), set(mention_ids)
    for group in GROUPS:
        if group["candidate_id"] in existing_candidates or group["mention_id"] in existing_mentions:
            raise SystemExit(f"candidate or mention ID already exists: {group['candidate_id']}")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    segment_map = {row["segment_id"]: row for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())}
    coverage_map = {row["segment_id"]: row for row in csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline=""))}
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_digest = sha256(SOURCE.read_bytes())
    mention_rows_by_segment: dict[str, list[dict[str, str]]] = {}
    for row in mentions:
        mention_rows_by_segment.setdefault(row["segment_id"], []).append(row)

    statement_lines = statement_bytes.splitlines(keepends=True)
    statement_indexes: dict[str, tuple[int, dict]] = {}
    decoded_statements = []
    for index, raw in enumerate(statement_lines):
        if raw.strip():
            row = json.loads(raw)
            decoded_statements.append(row)
            statement_indexes[row["statement_id"]] = (index, row)
    if len(decoded_statements) != 15_109:
        raise SystemExit("unexpected statement count")

    new_candidate_rows, new_mention_rows = [], []
    changed_statements: dict[str, dict] = {}
    for group in GROUPS:
        segment = segment_map.get(group["segment_id"])
        if not segment:
            raise SystemExit(f"missing source segment: {group['segment_id']}")
        if source_digest != segment.get("asset_sha256"):
            raise SystemExit(f"S0 asset hash mismatch: {group['segment_id']}")
        segment_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])] )
        if sha256(segment_text.encode("utf-8")) != segment.get("sha256"):
            raise SystemExit(f"S0 segment hash mismatch: {group['segment_id']}")
        coverage = coverage_map.get(group["segment_id"])
        if not coverage or coverage.get("disposition") != "reviewed" or coverage.get("migration_status") != "complete":
            raise SystemExit(f"S2 coverage is not reviewed/complete: {group['segment_id']}")
        start = group["expected_start"]
        if start is None:
            start = segment_text.find(group["surface"])
        if start < 0 or segment_text[start:start + len(group["surface"])] != group["surface"]:
            raise SystemExit(f"surface does not match exact S0 span: {group['mention_id']}")
        if group["expected_start"] is None and segment_text.find(group["surface"], start + 1) != -1:
            raise SystemExit(f"surface is not unique; provide a reviewed offset: {group['mention_id']}")
        for old in mention_rows_by_segment.get(group["segment_id"], []):
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if start < old_end and start + len(group["surface"]) > old_start:
                if old["candidate_id"] not in EXPECTED_STATEMENTS[group["statement_id"]][2] if EXPECTED_STATEMENTS[group["statement_id"]][2] else True:
                    raise SystemExit(f"new group span overlaps an unrelated mention: {group['mention_id']} with {old['mention_id']}")

        original = statement_indexes.get(group["statement_id"])
        if not original:
            raise SystemExit(f"missing statement: {group['statement_id']}")
        statement_index, row = original
        expected_subject, expected_object, expected_members = EXPECTED_STATEMENTS[group["statement_id"]]
        if row.get("subject_candidate_id") != expected_subject or row.get("object_candidate_id") != expected_object:
            raise SystemExit(f"statement endpoints changed: {group['statement_id']}")
        qualifiers = row.get("qualifiers", {})
        if qualifiers.get("relation_candidate") is not True:
            raise SystemExit(f"statement is not a relation candidate: {group['statement_id']}")
        if expected_members is not None and qualifiers.get("participant_candidate_ids") != expected_members:
            raise SystemExit(f"statement participants changed: {group['statement_id']}")
        if qualifiers.get("source_line_start") != group["source_line"]:
            raise SystemExit(f"statement source anchor changed: {group['statement_id']}")
        if group["candidate_id"] not in candidate_by_id:
            if expected_members:
                for member_id in expected_members:
                    if member_id not in candidate_by_id:
                        raise SystemExit(f"participant candidate missing: {member_id}")

        new_candidate_rows.append({
            "candidate_id": group["candidate_id"], "index_entry_id": "", "canonical_name": group["canonical_name"],
            "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "",
            "sub_entry": "", "detail": group["detail"], "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{group['segment_id']}#L{group['source_line']}",
        })
        new_mention_rows.append({
            "mention_id": group["mention_id"], "segment_id": group["segment_id"], "candidate_id": group["candidate_id"],
            "surface_form": group["surface"], "start_char": str(start), "end_char": str(start + len(group["surface"])),
            "note": group["note"],
        })
        updated = dict(row)
        endpoint = "subject_candidate_id" if expected_subject is None else "object_candidate_id"
        updated[endpoint] = group["candidate_id"]
        new_qualifiers = dict(qualifiers)
        new_qualifiers.pop("open_endpoint_reason", None)
        new_qualifiers["relation_candidate_note"] = group["note"]
        updated["qualifiers"] = new_qualifiers
        changed_statements[group["statement_id"]] = updated
        original_line = statement_lines[statement_index]
        line_ending = b"\r\n" if original_line.endswith(b"\r\n") else b"\n" if original_line.endswith(b"\n") else b""
        statement_lines[statement_index] = json.dumps(updated, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + line_ending

    candidate_after, mention_after = candidate_bytes, mention_bytes
    for row in new_candidate_rows:
        candidate_after = append_bytes(candidate_after, serialize_csv_row(candidate_headers, row))
    for row in new_mention_rows:
        mention_after = append_bytes(mention_after, serialize_csv_row(mention_headers, row))
    statement_after = b"".join(statement_lines)

    _, candidate_check = parse_csv(candidate_after)
    _, mention_check = parse_csv(mention_after)
    statement_check = [json.loads(line) for line in statement_after.splitlines() if line.strip()]
    if len(candidate_check) != 12_247 or len(mention_check) != 26_435 or len(statement_check) != 15_109:
        raise SystemExit("projected row counts do not match")
    if len({r["candidate_id"] for r in candidate_check}) != len(candidate_check):
        raise SystemExit("projected candidate IDs are not unique")
    if len({r["mention_id"] for r in mention_check}) != len(mention_check):
        raise SystemExit("projected mention IDs are not unique")
    if sum(1 for row in statement_check if row.get("qualifiers", {}).get("relation_candidate") is True) != 10_373:
        raise SystemExit("relation candidate count changed unexpectedly")

    updates = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    summary = {"candidate_count": len(candidate_check), "mention_count": len(mention_check), "statement_count": len(statement_check)}
    return updates, summary


def apply_transaction(updates: dict[Path, bytes]) -> None:
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("one or more recovery backups already exist")
    for path, expected in EXPECTED_HASHES.items():
        if sha256(path.read_bytes()) != expected:
            raise SystemExit(f"{path.relative_to(ROOT)} changed after preview")
    for source, backup in BACKUPS.items():
        shutil.copy2(source, backup)
    temps: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for target, data in updates.items():
            with tempfile.NamedTemporaryFile("wb", dir=target.parent, delete=False) as stream:
                temp_path = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            temps[target] = temp_path
        for target, temp_path in temps.items():
            os.replace(temp_path, target)
            replaced.append(target)
    except Exception:
        for target in reversed(replaced):
            shutil.copy2(BACKUPS[target], target)
        raise
    finally:
        for temp_path in temps.values():
            if temp_path.exists():
                temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve seven reviewed S2 front-matter collective or anonymous endpoints.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updates, summary = validate_and_build()
    for group in GROUPS:
        expected_subject, expected_object, _ = EXPECTED_STATEMENTS[group["statement_id"]]
        target_endpoint = "subject" if expected_subject is None else "object"
        print(f"{group['statement_id']}: {target_endpoint} -> {group['candidate_id']} ({group['surface']!r})")
    print(f"projected candidates={summary['candidate_count']} mentions={summary['mention_count']} statements={summary['statement_count']}")
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(data)}")
    if args.preview:
        print("preview only; no files or backups written")
        return
    apply_transaction(updates)
    print("recovery backups:")
    for backup in BACKUPS.values():
        print(backup)
    print("applied")


if __name__ == "__main__":
    main()
