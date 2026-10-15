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
    CANDIDATES: "5c95fa30b671cca1d96b732b32739370f78cf699d8f9a840b356bcfa9f53042a",
    MENTIONS: "1b0521bfe3faa36587dae194bca5a7772c59f1fca114f725241caa9d0a3c8ac6",
    STATEMENTS: "cd7192b8b01c6fc0ecc9a267830911748e0df3b7f40b215d19fa56827a4206aa",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l54-63"
GUIDO_STATEMENT_ID = "st-chp2-seciv-l54-63-guido-missions-shape-taste-and-writings"
ENZO_STATEMENT_ID = "st-chp2-seciv-l54-63-enzo-post-created-by-pope"
NEW_STATEMENT_ID = "st-chp2-seciv-l54-63-guido-missions-provided-writing-material"
MISSION_CANDIDATE_ID = "cand-12301"
WRITINGS_CANDIDATE_ID = "cand-12302"
POST_CANDIDATE_ID = "cand-12303"
MENTION_IDS = {
    MISSION_CANDIDATE_ID: "m-chp2-seciv-l54-63-guido-nunciature-missions",
    POST_CANDIDATE_ID: "m-chp2-seciv-l54-63-enzo-diplomatic-post",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-bentivoglio-missions-post-20261015")
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
    original_rows: list[dict] = []
    statement_by_id: dict[str, dict] = {}
    for raw in statement_bytes.splitlines(keepends=False):
        if raw.strip():
            row = json.loads(raw)
            original_rows.append(row)
            statement_by_id[row["statement_id"]] = row
    if len(statement_by_id) != len(original_rows):
        raise SystemExit("duplicate statement IDs")
    before_rows = copy.deepcopy(original_rows)

    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if any(cid in candidate_ids for cid in (MISSION_CANDIDATE_ID, WRITINGS_CANDIDATE_ID, POST_CANDIDATE_ID)):
        raise SystemExit("planned candidate ID already exists")
    if any(mid in mention_ids for mid in MENTION_IDS.values()):
        raise SystemExit("planned mention ID already exists")
    if NEW_STATEMENT_ID in statement_by_id:
        raise SystemExit("planned statement ID already exists")
    max_candidate = max(
        int(row["candidate_id"].split("-")[1])
        for row in candidate_rows
        if row["candidate_id"].startswith("cand-")
    )
    if max_candidate != 12300:
        raise SystemExit(f"candidate sequence changed: {max_candidate}")

    segments = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 segment or source asset mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment text hash mismatch")

    surfaces = {
        "missions": MISSION_CANDIDATE_ID,
        "a post": POST_CANDIDATE_ID,
    }
    spans: dict[str, tuple[int, int]] = {}
    for surface in surfaces:
        if text.count(surface) != 1:
            raise SystemExit(f"source phrase changed or is not unique: {surface}")
        start = text.index(surface)
        end = start + len(surface)
        spans[surface] = (start, end)
        for row in mention_rows:
            if (
                row["segment_id"] == SEGMENT_ID
                and start < int(row["end_char"])
                and end > int(row["start_char"])
            ):
                raise SystemExit(f"source span overlaps existing mention: {row['mention_id']}")

    writings_mention = next(
        (row for row in mention_rows if row.get("mention_id") == "m-chp2-seciv-l54-63-0049"),
        None,
    )
    if (
        not writings_mention
        or writings_mention.get("segment_id") != SEGMENT_ID
        or writings_mention.get("candidate_id") != "cand-0291"
        or writings_mention.get("surface_form") != "his very popular historical writings"
        or (int(writings_mention["start_char"]), int(writings_mention["end_char"]))
        != (2432, 2468)
    ):
        raise SystemExit("existing Guido historical-writings mention state changed")

    guido = statement_by_id.get(GUIDO_STATEMENT_ID)
    enzo = statement_by_id.get(ENZO_STATEMENT_ID)
    if (
        not guido
        or guido.get("segment_id") != SEGMENT_ID
        or guido.get("subject_candidate_id") != "cand-0291"
        or guido.get("object_candidate_id") not in (None, "")
        or guido.get("qualifiers", {}).get("relation_candidate") is not True
        or guido.get("original_quote")
        != "missions which strongly influenced his tastes and political sympathies and provided him with the material for his very popular historical writings."
    ):
        raise SystemExit("Guido missions statement state changed")
    if (
        not enzo
        or enzo.get("segment_id") != SEGMENT_ID
        or enzo.get("subject_candidate_id") != "cand-4656"
        or enzo.get("object_candidate_id") not in (None, "")
        or enzo.get("qualifiers", {}).get("relation_candidate") is not True
    ):
        raise SystemExit("Enzo post statement state changed")

    candidate_rows.extend(
        [
            {
                "candidate_id": MISSION_CANDIDATE_ID,
                "index_entry_id": "",
                "canonical_name": "Guido Bentivoglio's nunciature missions in Flanders and Paris (source-defined group)",
                "index_page_range": "",
                "suggested_type": "event",
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": "Haskell says Guido served as Nunzio in Flanders and Paris over the previous fourteen years and calls these his missions. The passage does not give individual mission dates or refer to independent mission records; this candidate represents the source-defined group.",
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": f"{SEGMENT_ID}#L60",
            },
            {
                "candidate_id": WRITINGS_CANDIDATE_ID,
                "index_entry_id": "",
                "canonical_name": "Guido Bentivoglio's unnamed historical writings",
                "index_page_range": "",
                "suggested_type": "work",
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": "Haskell calls Guido's historical writings very popular and says his missions supplied material for them. No title, count, or publication details are supplied in this passage.",
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": f"{SEGMENT_ID}#L60",
            },
            {
                "candidate_id": POST_CANDIDATE_ID,
                "index_entry_id": "",
                "canonical_name": "Ferrara-to-Rome ambassadorial post created for Enzo Bentivoglio",
                "index_page_range": "",
                "suggested_type": "term",
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": "Haskell reports that Enzo served for a time in this post, specially created by an unnamed Pope to satisfy local sensibilities. The passage gives no formal office title or creation date.",
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": f"{SEGMENT_ID}#L61",
            },
        ]
    )
    for surface, candidate_id in surfaces.items():
        start, end = spans[surface]
        mention_rows.append(
            {
                "mention_id": MENTION_IDS[candidate_id],
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(end),
                "note": "Source-bounded mission, writing, or office term; dates, titles, membership, or publication details remain open as stated in candidate detail.",
            }
        )

    writings_mention["candidate_id"] = WRITINGS_CANDIDATE_ID
    writings_mention["note"] = "Guido's unnamed historical writings; no individual title or publication details are identified in this passage."

    guido["object_candidate_id"] = MISSION_CANDIDATE_ID
    guido["predicate"] = "diplomatic_missions_influence_tastes_and_sympathies_reported"
    guido["original_quote"] = "missions which strongly influenced his tastes and political sympathies"
    guido_q = guido.setdefault("qualifiers", {})
    guido_q["claim"] = "Haskell says Guido's Flanders and Paris missions strongly influenced his tastes and political sympathies."
    guido_q["qualification"] = "This is Haskell's causal assessment; no particular taste, political position, or change is identified here. Individual mission dates remain unspecified."
    guido_q["relation_candidate_note"] = "Map the explicit plural 'missions' to a source-defined event group for Guido's service in Flanders and Paris; do not invent dates or an exhaustive itinerary."
    guido_q.pop("open_endpoint_reason", None)
    guido_q["mentioned_candidate_ids"] = list(
        dict.fromkeys([*(guido_q.get("mentioned_candidate_ids") or []), MISSION_CANDIDATE_ID])
    )

    writing_statement = copy.deepcopy(guido)
    writing_statement["statement_id"] = NEW_STATEMENT_ID
    writing_statement["subject_candidate_id"] = MISSION_CANDIDATE_ID
    writing_statement["object_candidate_id"] = WRITINGS_CANDIDATE_ID
    writing_statement["predicate"] = "diplomatic_missions_provided_material_for_historical_writings_reported"
    writing_statement["original_quote"] = "and provided him with the material for his very popular historical writings."
    writing_q = writing_statement["qualifiers"]
    writing_q["claim"] = "Haskell says Guido's diplomatic missions provided material for his very popular historical writings."
    writing_q["qualification"] = "Haskell's popularity assessment is retained as authorial characterization; the passage names no individual writing or publication."
    writing_q["relation_candidate_note"] = "Represent the explicitly named historical writings as an open work-group candidate; no title or complete corpus is supplied."
    writing_q["mentioned_candidate_ids"] = ["cand-0291", MISSION_CANDIDATE_ID, WRITINGS_CANDIDATE_ID]
    writing_q.pop("open_endpoint_reason", None)
    writing_q.pop("related_statement_ids", None)

    enzo["object_candidate_id"] = POST_CANDIDATE_ID
    enzo_q = enzo.setdefault("qualifiers", {})
    enzo_q["qualification"] = "The source defines the post only by Enzo's Ferrara-to-Rome ambassador role and its creation to satisfy local sensibilities. The creating Pope remains unidentified as cand-4656, distinct from cand-4655; no formal title or date is given."
    enzo_q["relation_candidate_note"] = "Map the source-described diplomatic post to a term candidate; preserve the Pope's unresolved identity and distinction from cand-4655."
    enzo_q.pop("open_endpoint_reason", None)
    enzo_q["mentioned_candidate_ids"] = list(
        dict.fromkeys([*(enzo_q.get("mentioned_candidate_ids") or []), POST_CANDIDATE_ID])
    )

    updated_rows: list[dict] = []
    for row in original_rows:
        updated_rows.append(row)
        if row.get("statement_id") == GUIDO_STATEMENT_ID:
            updated_rows.append(writing_statement)
    if len({row["statement_id"] for row in updated_rows}) != len(updated_rows):
        raise SystemExit("statement IDs not unique after prepared update")

    before_open = open_endpoint_counts(before_rows)
    after_open = open_endpoint_counts(updated_rows)
    true_before = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in before_rows)
    true_after = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in updated_rows)
    if before_open != (513, 336, 64, 113) or after_open != (511, 334, 64, 113):
        raise SystemExit(f"unexpected open-endpoint counts: {before_open} -> {after_open}")
    if true_before != 10379 or true_after != 10380:
        raise SystemExit(f"unexpected relation-candidate counts: {true_before} -> {true_after}")
    if (len(candidate_rows), len(mention_rows), len(updated_rows)) != (12281, 26472, 15116):
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
    print("New candidates: cand-12301 (event mission group), cand-12302 (work group), cand-12303 (diplomatic office term).")
    print("Reused existing mention m-chp2-seciv-l54-63-0049 for cand-12302; added only two mentions.")
    print("One compound missions claim split into two; Enzo's post endpoint linked; Guido's cardinal appointing authority remains open.")
    print("Spans: " + ", ".join(f"{surface} [{a},{b})" for surface, (a, b) in spans.items()))
    print("Open endpoints: 513 -> 511; projected counts: 12,281 candidates, 26,472 mentions, 15,116 statements.")
    if args.apply:
        apply(updates)
        print("Applied with recovery backups.")


if __name__ == "__main__":
    main()
