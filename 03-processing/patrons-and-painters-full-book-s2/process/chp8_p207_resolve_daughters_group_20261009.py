from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
MENTIONS = TABLE_DIR / "mentions.csv"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l126-157"
STATEMENT_ID = "st-chp8-p207-n1-ferdinand-left-thirds-to-daughters"
MENTION_ID = "m-chp8-p207-note-024"
CANDIDATE_ID = "cand-11553"
SURFACE = "his three daughters"
PRECEDENT_ID = "cand-7810"
EXPECTED_GROUP_NAME = "Stefano Conti's three unnamed daughters"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_row(values: list[str], newline: str = "") -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator=newline)
    writer.writerow(values)
    return buffer.getvalue()


def decode_csv(raw: bytes) -> tuple[str, bool]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def encode_csv(text: str, bom: bool) -> bytes:
    return ("\ufeff" + text if bom else text).encode("utf-8")


def validate_source() -> tuple[str, int, int]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(lines[125:157])
    start = segment_text.find(SURFACE)
    if start < 0 or segment_text.find(SURFACE, start + 1) >= 0:
        raise SystemExit("Expected exactly one 'his three daughters' source span in the reviewed segment.")
    if segment_text.find("a third of his pictures") != 1846 or start != 1881:
        raise SystemExit("Source-segment offsets differ from the previously verified p.207 note anchors.")
    if "One of these married Don Giuliano Colonna" not in segment_text:
        raise SystemExit("The individual daughter reference is not present in the same note segment.")
    return segment_text, start, start + len(SURFACE)


def main() -> None:
    parser = argparse.ArgumentParser(description="Represent Van den Einden's bounded unnamed-daughters group as an S2 candidate endpoint.")
    parser.add_argument("--apply", action="store_true", help="Write only after all three exact dry-run hashes are supplied.")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    segment_text, start, end = validate_source()
    statement_raw = STATEMENTS.read_bytes()
    mention_raw = MENTIONS.read_bytes()
    candidate_raw = CANDIDATES.read_bytes()
    statement_lines = statement_raw.decode("utf-8").splitlines(keepends=True)
    statement_records = [json.loads(line) for line in statement_lines if line.strip()]
    targets = [row for row in statement_records if row.get("statement_id") == STATEMENT_ID]
    if len(targets) != 1:
        raise SystemExit(f"Expected exactly one target statement, found {len(targets)}.")
    target = targets[0]
    if target.get("segment_id") != SEGMENT_ID or target.get("subject_candidate_id") != "cand-0914" or target.get("object_candidate_id"):
        raise SystemExit("The target statement no longer has the reviewed source/subject/open-endpoint state.")
    if target.get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("The target is no longer an open S2 relation candidate.")
    if CANDIDATE_ID in target.get("qualifiers", {}).get("mentioned_candidate_ids", []):
        raise SystemExit("The planned group candidate is already mentioned by the target statement.")

    candidate_text, candidate_bom = decode_csv(candidate_raw)
    candidate_rows = list(csv.DictReader(io.StringIO(candidate_text, newline="")))
    candidate_by_id = {row.get("candidate_id"): row for row in candidate_rows}
    if candidate_by_id.get(PRECEDENT_ID, {}).get("canonical_name") != EXPECTED_GROUP_NAME:
        raise SystemExit("The untyped three-daughters group precedent cand-7810 has changed.")
    if PRECEDENT_ID not in target.get("qualifiers", {}).get("mentioned_candidate_ids", []) and PRECEDENT_ID not in candidate_by_id:
        raise SystemExit("No existing bounded unnamed-daughters group precedent was found.")
    if CANDIDATE_ID in candidate_by_id:
        raise SystemExit(f"Planned candidate ID {CANDIDATE_ID} already exists.")
    highest = max(int(row["candidate_id"].removeprefix("cand-")) for row in candidate_rows)
    if highest != 11552 or int(CANDIDATE_ID.removeprefix("cand-")) != highest + 1:
        raise SystemExit(f"Candidate sequence changed; current highest ID is {highest}.")

    mention_text, mention_bom = decode_csv(mention_raw)
    mention_rows = list(csv.DictReader(io.StringIO(mention_text, newline="")))
    mention_by_id = {row.get("mention_id"): row for row in mention_rows}
    if MENTION_ID in mention_by_id:
        raise SystemExit(f"Planned mention ID {MENTION_ID} already exists.")
    phrase_mentions = [
        row for row in mention_rows
        if row.get("segment_id") == SEGMENT_ID and row.get("surface_form") == SURFACE
    ]
    if phrase_mentions:
        raise SystemExit("The exact group mention is already present; inspect its candidate mapping before continuing.")
    prior_member = mention_by_id.get("m-chp8-p207-note-007")
    if not prior_member or prior_member.get("candidate_id") != "cand-7598" or prior_member.get("surface_form") != "One of these":
        raise SystemExit("The existing individual-daughter mention no longer matches the reviewed evidence.")

    header = next(csv.reader(io.StringIO(candidate_text, newline="")))
    candidate_values = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Ferdinand van den Einden's three unnamed daughters",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Bounded collective of Ferdinand van den Einden's three unnamed daughters. The source identifies one member "
            "as the wife of Don Giuliano Colonna but provides no names; keep the group distinct from the individual "
            "daughter candidate cand-7598 and do not assign shares to individual identities. No group type is forced."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L136",
    }
    candidate_newline = "\r\n" if b"\r\n" in candidate_raw else "\n"
    candidate_line = csv_row([candidate_values.get(column, "") for column in header], candidate_newline)
    candidate_after = candidate_text
    if candidate_after and not candidate_after.endswith(("\n", "\r")):
        candidate_after += candidate_newline
    candidate_after += candidate_line

    mention_header = next(csv.reader(io.StringIO(mention_text, newline="")))
    mention_values = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": SURFACE,
        "start_char": str(start),
        "end_char": str(end),
        "note": "Bounded collective of three unnamed daughters; candidate type remains unassigned; no individual share assignment is implied.",
    }
    mention_newline = "\r\n" if b"\r\n" in mention_raw else "\n"
    mention_line = csv_row([mention_values.get(column, "") for column in mention_header], mention_newline)
    mention_lines = mention_text.splitlines(keepends=True)
    marker = MENTION_ID.replace("note-024", "note-023") + ","
    positions = [index for index, line in enumerate(mention_lines) if line.startswith(marker)]
    if len(positions) != 1:
        raise SystemExit("Could not uniquely find the p.207 note-023 insertion anchor.")
    mention_lines.insert(positions[0] + 1, mention_line)
    mention_after = "".join(mention_lines)

    target_new = json.loads(json.dumps(target))
    target_new["object_candidate_id"] = CANDIDATE_ID
    target_new["qualifiers"]["mentioned_candidate_ids"].append(CANDIDATE_ID)
    target_new["qualifiers"]["qualification"] = (
        "The text explicitly identifies a bounded group of three unnamed daughters, represented by an untyped group candidate. "
        "It does not identify any daughter individually beyond the one who married Giuliano Colonna or assign one-third shares to individual identities."
    )
    statement_newline = "\r\n" if b"\r\n" in statement_raw else "\n"
    statement_after_lines = []
    replaced = 0
    for line in statement_lines:
        if not line.strip():
            statement_after_lines.append(line)
            continue
        record = json.loads(line)
        if record.get("statement_id") == STATEMENT_ID:
            statement_after_lines.append(json.dumps(target_new, ensure_ascii=False, separators=(",", ":")) + statement_newline)
            replaced += 1
        else:
            statement_after_lines.append(line)
    if replaced != 1:
        raise SystemExit("Could not uniquely replace the p.207 target statement.")
    statement_after = "".join(statement_after_lines).encode("utf-8")

    print(f"statements_sha256={sha256(statement_raw)}")
    print(f"mentions_sha256={sha256(mention_raw)}")
    print(f"candidates_sha256={sha256(candidate_raw)}")
    print(f"candidate_add={CANDIDATE_ID}: {candidate_values['canonical_name']} (type remains unassigned)")
    print(f"mention_add={MENTION_ID}: {SURFACE} [{start}:{end})")
    print(f"statement_update={STATEMENT_ID}: object null -> {CANDIDATE_ID}")
    print("expected_counts_after_apply: candidates +1; mentions +1; statements unchanged; relation_candidates unchanged; complete_endpoints +1; open_endpoints -1")
    if not args.apply:
        print("DRY-RUN: no files changed.")
        return

    expected = (args.expected_statements_sha256, args.expected_mentions_sha256, args.expected_candidates_sha256)
    actual = (sha256(statement_raw), sha256(mention_raw), sha256(candidate_raw))
    if None in expected or expected != actual:
        raise SystemExit("--apply requires all three expected hashes from this exact dry run.")

    changes = [
        (STATEMENTS, statement_raw, statement_after),
        (MENTIONS, mention_raw, encode_csv(mention_after, mention_bom)),
        (CANDIDATES, candidate_raw, encode_csv(candidate_after, candidate_bom)),
    ]
    backups = []
    for path, old, _ in changes:
        backup = path.with_name(path.name + ".bak-s2-handoff-chp8-p207-daughters-group-20261009")
        if backup.exists():
            raise SystemExit(f"Refusing to overwrite recovery copy: {backup}")
        backups.append((path, old, backup))
    for path, old, backup in backups:
        shutil.copy2(path, backup)

    temps = []
    try:
        for path, _, new in changes:
            temp = path.with_name(path.name + ".tmp-s2-handoff-chp8-p207")
            temp.write_bytes(new)
            temps.append((temp, path))
        for temp, path in temps:
            os.replace(temp, path)
    except Exception:
        for temp, _ in temps:
            if temp.exists():
                temp.unlink()
        raise
    print("APPLIED: candidate, mention, and statement endpoint written.")
    for path, _, backup in backups:
        print(f"recovery_copy={backup} sha256={sha256(backup.read_bytes())}")
        print(f"new_file={path} sha256={sha256(path.read_bytes())}")


if __name__ == "__main__":
    main()
