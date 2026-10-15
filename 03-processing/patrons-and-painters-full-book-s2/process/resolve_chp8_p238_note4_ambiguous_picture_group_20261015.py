from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l372-461"
STATEMENT_ID = "st-chp8-p238-note4-pictures-at-pisa-cabinet"
BACKUP_SUFFIX = "bak-s2-chp8-p238-note4-ambiguous-picture-group-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "50b94dc190c7880b2991fabe61b9bd887e974e84a14fed2d2c24c9c4de7c7e43",
    "mentions.csv": "6aeaaaa3f35fe1f3fe4b6618fcd57ea2633b260746cf4dfcf7e1e47a4c5d7cab",
    "book-statements.jsonl": "70e56001e83376db3d4af01b2a6d9ac64e07c8fb45e2d145c9df9d481d4e2757",
}
EXPECTED_SEGMENT_HASH = "62a4611253d2bf05494ef55b0511b53861b0947a05aee1c7a9fdbab976ecbc3f"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open(row: dict[str, object]) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [r for r in rows if is_open(r)]
    object_only = sum(bool(r.get("subject_candidate_id")) and not r.get("object_candidate_id") for r in opens)
    subject_only = sum(not r.get("subject_candidate_id") and bool(r.get("object_candidate_id")) for r in opens)
    both = sum(not r.get("subject_candidate_id") and not r.get("object_candidate_id") for r in opens)
    return len(opens), object_only, subject_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    raw_by_name = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(raw_by_name[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    segment = next(
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Footnote segment changed")
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source = "\n".join(lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    surface = "These pictures"
    start = source.find(surface)
    if start < 0 or source.find(surface, start + 1) >= 0:
        raise ValueError("Expected unique anaphoric phrase missing or repeated")

    cid = "cand-12373"
    name = "Paintings referred to as 'These pictures' in Haskell's p.238 note 4 (scope uncertain)"
    if any(r["candidate_id"] == cid or r["canonical_name"] == name for r in candidates):
        raise ValueError("Candidate ID or name already exists")
    line_no = int(segment["line_start"]) + source.count("\n", 0, start)
    detail = "A source-level work group referenced collectively by footnote 4. Its antecedent may be the two genre scenes just described and may also include the preceding satirical picture; membership remains unresolved, and no individual work-to-location edge is asserted."
    candidate = {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
    }
    mention = {
        "mention_id": f"m-chp8-{cid}-source-mention",
        "segment_id": SEGMENT_ID,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": detail,
    }
    if any(r["mention_id"] == mention["mention_id"] for r in mentions):
        raise ValueError("Mention ID already exists")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    statement = next((r for r in rows if r.get("statement_id") == STATEMENT_ID), None)
    if statement is None or not is_open(statement) or statement.get("object_candidate_id") != "cand-8048":
        raise ValueError("Expected open Pisa cabinet statement not found")
    statement["subject_candidate_id"] = cid
    q = statement.get("qualifiers") or {}
    q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + [cid]))
    q["relation_candidate_note"] = "Footnote 4 collectively refers to a picture group whose scope is unresolved; preserve both the possible inclusion of the satirical picture and the 'are—or were in 1941' time qualification, without mapping any individual work to the cabinet."
    q.pop("open_endpoint_reason", None)
    statement["qualifiers"] = q

    after_counts = endpoint_counts(rows)
    if after_counts != (431, 272, 55, 104):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")
    candidate_after = append_rows(candidate_raw, candidate_fields, [candidate])
    mention_after = append_rows(mention_raw, mention_fields, [mention])
    statement_after = (
        "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)
    ).encode("utf-8")
    print(f"candidate_rows={len(candidates)}->{len(candidates) + 1}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + 1}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    print(f"resolved_statement={STATEMENT_ID}|subject->{cid}")
    print(f"retained_scope_qualification={detail}")
    print(f"open_endpoints={endpoint_counts([json.loads(x) for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{after_counts}")
    for fname, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{fname} {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = ((CANDIDATES, candidate_after), (MENTIONS, mention_after), (STATEMENTS, statement_after))
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temp, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temp, data in pairs:
            temp.write_bytes(data)
        for path, backup, temp, _ in pairs:
            temp.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temp, _ in pairs:
            if temp.exists():
                temp.unlink()
        for path, backup in replaced:
            shutil.copy2(backup, path)
        raise
    for path, backup, _, _ in pairs:
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
