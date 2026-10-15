from __future__ import annotations

import argparse
import copy
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
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "94291d0c05d4b8148ee3dbc3c871c572270b0fbad4c893e70c5b61af5e6efc6e",
    MENTIONS: "625e82141e7a2f273026af777826c3e2d28d8aee0e83c69a26a11775f2fdfe3a",
    STATEMENTS: "341247e2bbf9c34204c84a4bf31cfe40647cc4ce822809b63a653b7aa596d4c8",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l139-152"
WEALTH_STATEMENT_ID = "st-chp2-seciv-l139-152-barberini-wealth-and-revival-interpretation"
REVIVAL_STATEMENT_ID = "st-chp2-seciv-l139-152-barberini-revives-ancient-forms"
PALACE_CONTENTS_STATEMENT_ID = "st-chp2-seciv-l139-152-palace-filled-with-art-and-treasures"
FOLIO_CONTENTS_STATEMENT_ID = "st-chp2-seciv-l139-152-1642-volume-describes-palace-contents"
OLD_FAMILIES_CANDIDATE_ID = "cand-12306"
PALACE_CONTENTS_CANDIDATE_ID = "cand-12307"
MENTION_IDS = {
    "oldest_families": "m-chp2-seciv-l139-152-oldest-families",
    "palace_contents": "m-chp2-seciv-l139-152-works-and-treasures",
    "contents_anaphor": "m-chp2-seciv-l139-152-palace-contents-anaphor",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-palace-contents-oldest-families-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def write_csv(data: bytes, headers: list[str], rows: list[dict[str, str]]) -> bytes:
    line_ending = "\r\n" if b"\r\n" in data else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    return bom + buffer.getvalue().encode("utf-8")


def open_endpoint_counts(rows: list[dict]) -> tuple[int, int, int, int]:
    relation_rows = [row for row in rows if row.get("qualifiers", {}).get("relation_candidate") is True]
    subject_missing = sum(not row.get("subject_candidate_id") for row in relation_rows)
    object_missing = sum(not row.get("object_candidate_id") for row in relation_rows)
    both_missing = sum(
        not row.get("subject_candidate_id") and not row.get("object_candidate_id")
        for row in relation_rows
    )
    return (
        subject_missing + object_missing - both_missing,
        object_missing - both_missing,
        subject_missing - both_missing,
        both_missing,
    )


def add_candidate_mention_ids(qualifiers: dict, *candidate_ids: str) -> None:
    qualifiers["mentioned_candidate_ids"] = list(
        dict.fromkeys([*(qualifiers.get("mentioned_candidate_ids") or []), *candidate_ids])
    )


def build() -> tuple[dict[Path, bytes], dict[str, tuple[int, int]]]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    candidate_bytes = CANDIDATES.read_bytes()
    candidate_headers, candidate_rows = read_csv(candidate_bytes)
    mention_bytes = MENTIONS.read_bytes()
    mention_headers, mention_rows = read_csv(mention_bytes)
    statement_bytes = STATEMENTS.read_bytes()
    statement_rows = [json.loads(line) for line in statement_bytes.splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    if len(statement_by_id) != len(statement_rows):
        raise SystemExit("duplicate statement IDs")
    before_open = open_endpoint_counts(statement_rows)

    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if candidate_ids.intersection({OLD_FAMILIES_CANDIDATE_ID, PALACE_CONTENTS_CANDIDATE_ID}):
        raise SystemExit("planned candidate ID already exists")
    if mention_ids.intersection(MENTION_IDS.values()):
        raise SystemExit("planned mention ID already exists")
    if REVIVAL_STATEMENT_ID in statement_by_id:
        raise SystemExit("planned statement ID already exists")
    max_candidate = max(
        int(row["candidate_id"].split("-")[1])
        for row in candidate_rows
        if row["candidate_id"].startswith("cand-")
    )
    if max_candidate != 12305:
        raise SystemExit(f"candidate sequence changed: {max_candidate}")
    for row in candidate_rows:
        name = row.get("canonical_name", "").casefold()
        if any(term in name for term in ("oldest families", "works and treasures in the barberini palace", "barberini palace contents group")):
            raise SystemExit(f"possible duplicate source group candidate: {row['candidate_id']}")

    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 segment or source asset mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment text hash mismatch")

    surfaces = {
        "the oldest families": "the oldest families",
        "works of art and treasures of all kinds": "works of art and treasures of all kinds",
        "its contents": "its contents",
    }
    spans: dict[str, tuple[int, int]] = {}
    for surface, anchor in surfaces.items():
        if text.count(anchor) != 1:
            raise SystemExit(f"source anchor changed or is not unique: {anchor}")
        start = text.index(anchor)
        end = start + len(surface)
        if text[start:end] != surface:
            raise SystemExit(f"source span mismatch for {surface}")
        spans[surface] = (start, end)
        for row in mention_rows:
            if (
                row["segment_id"] == SEGMENT_ID
                and start < int(row["end_char"])
                and end > int(row["start_char"])
            ):
                raise SystemExit(f"source span overlaps existing mention: {row['mention_id']}")

    barberini_mention = next(
        (row for row in mention_rows if row.get("mention_id") == "m-chp2-seciv-l139-152-0014"),
        None,
    )
    if (
        not barberini_mention
        or barberini_mention.get("candidate_id") != "cand-3464"
        or barberini_mention.get("surface_form") != "the Barberini"
        or (int(barberini_mention["start_char"]), int(barberini_mention["end_char"])) != (823, 836)
    ):
        raise SystemExit("existing subject mention for the revival claim changed")

    wealth = statement_by_id.get(WEALTH_STATEMENT_ID)
    palace = statement_by_id.get(PALACE_CONTENTS_STATEMENT_ID)
    folio = statement_by_id.get(FOLIO_CONTENTS_STATEMENT_ID)
    if (
        not wealth
        or wealth.get("segment_id") != SEGMENT_ID
        or wealth.get("subject_candidate_id") != "cand-3464"
        or wealth.get("object_candidate_id") not in (None, "")
        or wealth.get("qualifiers", {}).get("relation_candidate") is not True
        or wealth.get("qualifiers", {}).get("statement_sequence") != 7
        or "lavish consumption of wealth" not in wealth.get("original_quote", "")
    ):
        raise SystemExit("Barberini wealth statement state changed")
    if (
        not palace
        or palace.get("segment_id") != SEGMENT_ID
        or palace.get("subject_candidate_id") != "cand-0241"
        or palace.get("object_candidate_id") not in (None, "")
        or palace.get("qualifiers", {}).get("relation_candidate") is not True
    ):
        raise SystemExit("palace contents statement state changed")
    if (
        not folio
        or folio.get("segment_id") != SEGMENT_ID
        or folio.get("subject_candidate_id") != "cand-4774"
        or folio.get("object_candidate_id") != "cand-0241"
        or folio.get("qualifiers", {}).get("relation_candidate") is not True
    ):
        raise SystemExit("1642 volume contents statement state changed")

    candidate_rows.extend(
        [
            {
                "candidate_id": OLD_FAMILIES_CANDIDATE_ID,
                "index_entry_id": "",
                "canonical_name": "Unnamed oldest families said to be harmed by Barberini wealth consumption",
                "index_page_range": "",
                "suggested_type": "",
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": "Haskell says the Barberini's lavish wealth consumption was effectively ruining 'the oldest families'; none is individually named or enumerated. Keep this source-defined group distinct from the adjacent phrase 'most venerable of Roman families' unless further evidence identifies its membership.",
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": f"{SEGMENT_ID}#L143",
            },
            {
                "candidate_id": PALACE_CONTENTS_CANDIDATE_ID,
                "index_entry_id": "",
                "canonical_name": "Unspecified works and treasures in the Barberini palace",
                "index_page_range": "",
                "suggested_type": "",
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": "Haskell says the palace was being filled with works of art and treasures of all kinds; the following 1642 account describes paintings, allegorical ceilings, antiques, and library holdings. This is a broad contents group, not a complete inventory; keep it separate from the narrower paintings group cand-4791, the palace cand-0241, and the 1642 volume cand-4774.",
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": f"{SEGMENT_ID}#L144",
            },
        ]
    )
    mention_specs = [
        ("the oldest families", OLD_FAMILIES_CANDIDATE_ID, "Unidentified collective described as harmed by Barberini wealth consumption."),
        ("works of art and treasures of all kinds", PALACE_CONTENTS_CANDIDATE_ID, "Broad source-defined contents group of the Barberini palace; the complete inventory is not supplied."),
        ("its contents", PALACE_CONTENTS_CANDIDATE_ID, "Anaphoric reference to the palace contents group introduced in the preceding sentence."),
    ]
    for (surface, candidate_id, note), mention_id in zip(mention_specs, MENTION_IDS.values(), strict=True):
        start, end = spans[surface]
        mention_rows.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(end),
                "note": note,
            }
        )

    wealth["predicate"] = "barberini-wealth-consumption-ruins-oldest-families-reported"
    wealth["original_quote"] = "At the same time as their lavish consumption of wealth was effectively ruining the oldest families"
    wealth_q = wealth.setdefault("qualifiers", {})
    wealth["object_candidate_id"] = OLD_FAMILIES_CANDIDATE_ID
    wealth_q["claim"] = "Haskell says the Barberini's lavish consumption of wealth was effectively ruining the oldest families."
    wealth_q["qualification"] = "This is Haskell's evaluative account of economic harm; no affected family is individually named or enumerated."
    wealth_q["relation_candidate_note"] = "The explicit phrase 'the oldest families' is mapped to an open source-defined group; do not equate it with every Roman family or the adjacent 'most venerable' families."
    wealth_q.pop("open_endpoint_reason", None)
    add_candidate_mention_ids(wealth_q, "cand-3464", OLD_FAMILIES_CANDIDATE_ID)

    revival = copy.deepcopy(wealth)
    revival["statement_id"] = REVIVAL_STATEMENT_ID
    revival["subject_candidate_id"] = "cand-3464"
    revival["object_candidate_id"] = None
    revival["predicate"] = "barberini-attempts-to-revive-ancient-forms-reported"
    revival["original_quote"] = "the Barberini were desperately trying to revive the ancient forms for their own benefit."
    revival_q = revival["qualifiers"]
    revival_q["claim"] = "Haskell says the Barberini were desperately trying to revive the ancient forms for their own benefit."
    revival_q["qualification"] = "This is Haskell's broad interpretive account; the phrase 'ancient forms' is not delimited to specific practices or objects."
    revival_q["relation_candidate_note"] = "The source does not identify or bound the 'ancient forms'; do not treat the nearby joust, prefecture ceremony, marriage, or feudal rights as a complete set."
    revival_q["open_endpoint_reason"] = "The phrase 'ancient forms' is broad and does not identify a specific custom or bounded set of practices."
    revival_q["statement_sequence"] = 8
    revival_q["mentioned_candidate_ids"] = ["cand-3464"]
    revival_q["related_statement_ids"] = [WEALTH_STATEMENT_ID]
    wealth_q["related_statement_ids"] = list(
        dict.fromkeys([*(wealth_q.get("related_statement_ids") or []), REVIVAL_STATEMENT_ID])
    )

    for row in statement_rows:
        if row.get("segment_id") == SEGMENT_ID:
            sequence = row.get("qualifiers", {}).get("statement_sequence")
            if isinstance(sequence, int) and sequence >= 8:
                row["qualifiers"]["statement_sequence"] = sequence + 1

    palace["object_candidate_id"] = PALACE_CONTENTS_CANDIDATE_ID
    palace_q = palace.setdefault("qualifiers", {})
    palace_q["relation_candidate_note"] = "Map the explicit phrase 'works of art and treasures of all kinds' to a broad, open palace-contents group; the complete inventory and individual items remain unspecified."
    palace_q.pop("open_endpoint_reason", None)
    add_candidate_mention_ids(palace_q, PALACE_CONTENTS_CANDIDATE_ID)

    folio_q = folio.setdefault("qualifiers", {})
    add_candidate_mention_ids(folio_q, PALACE_CONTENTS_CANDIDATE_ID)

    updated_rows: list[dict] = []
    for row in statement_rows:
        updated_rows.append(row)
        if row.get("statement_id") == WEALTH_STATEMENT_ID:
            updated_rows.append(revival)
    if len({row["statement_id"] for row in updated_rows}) != len(updated_rows):
        raise SystemExit("statement IDs not unique after prepared update")

    after_open = open_endpoint_counts(updated_rows)
    true_before = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in statement_rows)
    true_after = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in updated_rows)
    if before_open != (509, 332, 64, 113):
        raise SystemExit(f"unexpected open-endpoint baseline: {before_open}")
    if after_open != (508, 331, 64, 113):
        raise SystemExit(f"unexpected projected open-endpoint counts: {after_open}")
    if true_before != 10380 or true_after != 10381:
        raise SystemExit(f"unexpected relation-candidate counts: {true_before} -> {true_after}")
    if (len(candidate_rows), len(mention_rows), len(updated_rows)) != (12285, 26477, 15117):
        raise SystemExit("unexpected projected table counts")

    updated_candidates = write_csv(candidate_bytes, candidate_headers, candidate_rows)
    updated_mentions = write_csv(mention_bytes, mention_headers, mention_rows)
    line_ending = "\r\n" if b"\r\n" in statement_bytes else "\n"
    updated_statements = line_ending.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated_rows
    ).encode("utf-8") + line_ending.encode("ascii")
    return {
        CANDIDATES: updated_candidates,
        MENTIONS: updated_mentions,
        STATEMENTS: updated_statements,
    }, spans


def apply(updates: dict[Path, bytes]) -> None:
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("recovery backup already exists")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"file changed after preview: {path.relative_to(ROOT)}")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    temporary: dict[Path, Path] = {}
    written: list[Path] = []
    try:
        for path, data in updates.items():
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
                temp_path = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            temporary[path] = temp_path
        for path, temp_path in temporary.items():
            os.replace(temp_path, path)
            written.append(path)
    except Exception:
        for path in reversed(written):
            shutil.copy2(BACKUPS[path], path)
        raise
    finally:
        for temp_path in temporary.values():
            if temp_path.exists():
                temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updates, spans = build()
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {sha(path.read_bytes())} -> {sha(data)}")
    print("New source-bounded open groups: cand-12306 (oldest families) and cand-12307 (palace works and treasures).")
    print("Split the line-143 compound claim; the ancient-forms endpoint remains open. Reused cand-12307 for the folio contents mention.")
    print("Spans: " + ", ".join(f"{surface} [{start},{end})" for surface, (start, end) in spans.items()))
    print("Open endpoints: 509 -> 508; projected counts: 12,285 candidates, 26,477 mentions, 15,117 statements.")
    if args.apply:
        apply(updates)
        print("Applied with recovery backups.")


if __name__ == "__main__":
    main()
