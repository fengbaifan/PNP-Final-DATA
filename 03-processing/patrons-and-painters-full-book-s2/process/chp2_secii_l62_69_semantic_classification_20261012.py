from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
SOURCE_SHA = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l62-69"
SEGMENT_SHA = "5564afc7580a476caafc29bef915eb98b1b88341c4e49252023a785d0616d2fe"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l62-69-20261012"
EXPECTED = {
    "book-statements.jsonl": "2e89742f448674d1e8e318a3a053ce02be22136dce00b134da6123b4a1a8e29d",
    "entity-candidates.csv": "46c40b4944db9fb937549e14b53eec02b9de0ac8471140d9edb0303411a5a6b4",
    "mentions.csv": "b782041655a999dbb744a2d859a508fbf2f33f5a0f1a182fb66040fd4859af00",
    "s2-coverage.csv": "71976be81e6af4c8f949ff90396e6953dc6a8f93994401737d5a6d174c071888",
}
UNSET = {
    "st-chp2-secii-l62-69-assistant-execution-generalization",
    "st-chp2-secii-l62-69-few-cardinals-or-princes-access",
}
NEW_CANDIDATES = {
    "cand-11883": {
        "candidate_id": "cand-11883",
        "index_entry_id": "",
        "canonical_name": "Cardinals or princes able to obtain works from Bernini (unnamed group)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell describes a small, unidentified class of cardinals or princes who could obtain works from Bernini. No members are enumerated; do not infer a complete membership list from nearby examples.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L64",
    },
    "cand-11884": {
        "candidate_id": "cand-11884",
        "index_entry_id": "",
        "canonical_name": "Assistants who executed Bernini works in other cases (unnamed group)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell generalizes that execution was often left to assistants in other cases. Neither the assistants nor the works are identified; keep distinct from assistants tied to a specific work, including cand-4418.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L65",
    },
}
NEW_MENTIONS = [
    {
        "mention_id": "m-chp2-secii-l62-69-0079",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-11883",
        "surface_form": "Only very few cardinals or princes",
        "start_char": "994",
        "end_char": "1028",
        "note": "Source-defined class of a small, unidentified set of potential patrons who could obtain works from Bernini; no members are inferred.",
    },
    {
        "mention_id": "m-chp2-secii-l62-69-0080",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-11884",
        "surface_form": "assistants",
        "start_char": "1314",
        "end_char": "1324",
        "note": "Unidentified assistants said to execute work in other cases; this generalized group is distinct from the assistants tied to a specific work such as cand-4418.",
    },
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def set_relation(row: dict, note: str, mentioned: list[str], open_reason: str) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = True
    qualifiers["relation_candidate_note"] = note
    qualifiers["mentioned_candidate_ids"] = mentioned
    qualifiers["open_endpoint_reason"] = open_reason


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")

    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.37 source segment fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[61:69])
    for phrase in ("Only very few cardinals or princes", "the execution at least was often left to assistants"):
        if phrase not in source_text:
            raise SystemExit(f"protected p.37 passage changed; re-review before applying: {phrase}")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET:
        raise SystemExit(f"unexpected p.37 unset statement set: {sorted(unset)}")
    if set(NEW_CANDIDATES) & set(candidate_by_id):
        raise SystemExit("planned candidate ID already exists")
    if any(row["mention_id"] in mention_by_id for row in NEW_MENTIONS):
        raise SystemExit("planned mention ID already exists")
    if "cand-0295" not in candidate_by_id or "cand-4418" not in candidate_by_id:
        raise SystemExit("required Bernini or specific-assistant candidate is missing")

    for mention in mentions:
        if mention["segment_id"] != SEGMENT_ID:
            continue
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"existing p.37 mention span changed or is invalid: {mention['mention_id']}")
    for mention in NEW_MENTIONS:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"planned p.37 mention span is invalid: {mention['mention_id']}")

    assistant = statement_by_id["st-chp2-secii-l62-69-assistant-execution-generalization"]
    assistant["object_candidate_id"] = "cand-11884"
    assistant["qualifiers"]["claim"] = "Haskell says that in other cases, at least the execution was often left to assistants."
    set_relation(
        assistant,
        "Haskell reports a generalized pattern of assistant execution in other cases; do not infer that every Bernini work was executed by assistants.",
        ["cand-0295", "cand-11884"],
        "The source names neither the assistants nor the specific works; the source-defined group preserves the general role without assigning individuals.",
    )

    access = statement_by_id["st-chp2-secii-l62-69-few-cardinals-or-princes-access"]
    access["object_candidate_id"] = "cand-11883"
    set_relation(
        access,
        "The source says only a very few cardinals or princes could obtain works from Bernini; their identities and the full group membership are not enumerated.",
        ["cand-0295", "cand-11883"],
        "The source-defined class is small but unidentified; nearby named patrons are not a complete membership list.",
    )

    candidate_rows = [NEW_CANDIDATES[cid] for cid in NEW_CANDIDATES]
    candidates.extend(candidate_rows)
    segment_indices = [i for i, row in enumerate(mentions) if row["segment_id"] == SEGMENT_ID]
    if not segment_indices or segment_indices != list(range(segment_indices[0], segment_indices[-1] + 1)):
        raise SystemExit("p.37 mention rows are not contiguous; reinsert manually in source order")
    first, last = segment_indices[0], segment_indices[-1]
    segment_mentions = mentions[first:last + 1] + NEW_MENTIONS
    segment_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
    mentions[first:last + 1] = segment_mentions

    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.37 coverage row")
    coverage_note = (
        " S2 follow-up classified the generalized assistant-execution claim and the limited-access claim as relation candidates. "
        "Two source-defined, unnamed groups were added for the assistants and the small class of cardinals or princes; no individual members were inferred. "
        "The printed p.37 scan confirms both statements. Footnote 1 follows the special authorization for Scipione Borghese's busts and is not assigned to these two claims."
    )
    if coverage_note.strip() not in coverage_rows[0]["note"]:
        coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + coverage_note

    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(candidate_ids) != len(candidates):
        raise SystemExit("candidate IDs are not unique after write preparation")
    for row in statements:
        if row["segment_id"] != SEGMENT_ID:
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key) and row[key] not in candidate_ids:
                raise SystemExit(f"p.37 statement has missing {key}: {row['statement_id']} -> {row[key]}")
        referenced = row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
        if set(referenced) - candidate_ids:
            raise SystemExit(f"p.37 statement has missing mentioned candidates: {row['statement_id']}")
    if any(source_text[int(m["start_char"]):int(m["end_char"])] != m["surface_form"] for m in mentions if m["segment_id"] == SEGMENT_ID):
        raise SystemExit("p.37 mention span audit failed")
    if any(row.get("qualifiers", {}).get("relation_candidate") is None for row in statements if row["segment_id"] == SEGMENT_ID):
        raise SystemExit("p.37 segment still has unset relation_candidate values")

    updated = {
        "book-statements.jsonl": statements,
        "entity-candidates.csv": candidates,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2 printed p.37 / normalized S0 L62-69",
        "classified_unset_ids": sorted(UNSET),
        "new_candidates": sorted(NEW_CANDIDATES),
        "new_mentions": [row["mention_id"] for row in NEW_MENTIONS],
        "remaining_unset": [],
        "counts_delta": {"statements": 0, "candidates": 2, "mentions": 2},
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(serialize(name, rows)).hexdigest() for name, rows in updated.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, rows in updated.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(serialize(name, rows))
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if any(written_by_id[sid].get("qualifiers", {}).get("relation_candidate") is not True for sid in UNSET):
            raise SystemExit("a p.37 relation_candidate value was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
        "statement_count": len(written),
        "candidate_count": len(candidates),
        "mention_count": len(mentions),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
