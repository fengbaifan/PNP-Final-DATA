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
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l78-84"
BACKUP_SUFFIX = "bak-s2-chp8-p218-source-groups-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "b668251d8977caf93a397655282e8c66312b20941aa4b06a61b60e6d9da2bcff",
    "mentions.csv": "af07394bd47b09b493419ec810055274fb173730ce7eb780a48c024043a60bce",
    "book-statements.jsonl": "b3f44d6dc571bbcdbcd3f81b6b1f862c7c2ffff7eac4afa75aa8df3fdd9cfbc7",
}
EXPECTED_SEGMENT_HASH = "a9adfb724cd4f057a4de3aa9bd62f9818990c72c1612a9072e223c978569ae22"


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
    opens = [row for row in rows if is_open(row)]
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
        raise ValueError("Source segment changed")
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source = "\n".join(lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])

    specs = [
        (
            "cand-12370",
            "Patrons in Haskell's account of Ciro Ferri's 1665 Santa Maria Maggiore commission",
            "",
            "Haskell refers to Ferri's patrons as a plural group whose relations with the artist cooled during a delay. The passage does not identify its membership or equate it with the appointed committee.",
            "patrons",
        ),
        (
            "cand-12371",
            "Various artists who proposed themselves for the three remaining Santa Maria Maggiore pictures",
            "",
            "Haskell describes an unnamed plural group of artists who proposed themselves for the remaining pictures. No individual artist or exact membership is supplied.",
            "Various artists",
        ),
    ]
    candidate_index = {r["candidate_id"]: r for r in candidates}
    names = {r["canonical_name"] for r in candidates}
    new_candidates: list[dict[str, str]] = []
    new_mentions: list[dict[str, str]] = []
    for cid, name, kind, detail, surface in specs:
        if cid in candidate_index or name in names:
            raise ValueError(f"Candidate ID or name already exists: {cid} / {name}")
        start = source.find(surface)
        if start < 0 or source.find(surface, start + 1) >= 0:
            raise ValueError(f"Expected unique source phrase missing or repeated: {surface}")
        line_no = int(segment["line_start"]) + source.count("\n", 0, start)
        new_candidates.append(
            {
                "candidate_id": cid,
                "index_entry_id": "",
                "canonical_name": name,
                "index_page_range": "",
                "suggested_type": kind,
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": detail,
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
            }
        )
        new_mentions.append(
            {
                "mention_id": f"m-chp8-{cid}-source-mention",
                "segment_id": SEGMENT_ID,
                "candidate_id": cid,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(start + len(surface)),
                "note": detail,
            }
        )
        candidate_index[cid] = new_candidates[-1]
        names.add(name)

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    statement_index = {r["statement_id"]: r for r in rows}
    targets = (
        ("st-chp8-p218-delay-cools-relations", "cand-1027", None, "cand-12370"),
        ("st-chp8-p218-artists-propose-for-remaining-works", None, "cand-12060", "cand-12371"),
    )
    for sid, expected_subject, expected_object, candidate in targets:
        row = statement_index.get(sid)
        if row is None or not is_open(row):
            raise ValueError(f"Expected open statement missing or already resolved: {sid}")
        if expected_subject is not None and row.get("subject_candidate_id") != expected_subject:
            raise ValueError(f"Unexpected subject for {sid}")
        if expected_object is not None and row.get("object_candidate_id") != expected_object:
            raise ValueError(f"Unexpected object for {sid}")
        if sid == "st-chp8-p218-delay-cools-relations":
            row["object_candidate_id"] = candidate
            note = "The plural source term 'patrons' is represented as an unnamed group for this commission; do not equate its membership with the appointed committee or infer the delay's cause."
        else:
            row["subject_candidate_id"] = candidate
            note = "The source identifies various self-proposing artists as a group; no individual candidate or artist-to-picture assignment is inferred."
        q = row.get("qualifiers") or {}
        q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + [candidate]))
        q["relation_candidate_note"] = note
        q.pop("open_endpoint_reason", None)
        row["qualifiers"] = q

    after_counts = endpoint_counts(rows)
    if after_counts != (434, 273, 57, 104):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")
    remaining = [r["statement_id"] for r in rows if r.get("segment_id") == SEGMENT_ID and is_open(r)]
    if remaining:
        raise ValueError(f"Unexpected remaining open p.218 statements: {remaining}")

    candidate_after = append_rows(candidate_raw, candidate_fields, new_candidates)
    mention_after = append_rows(mention_raw, mention_fields, new_mentions)
    statement_after = (
        "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)
    ).encode("utf-8")
    print(f"candidate_rows={len(candidates)}->{len(candidates) + len(new_candidates)}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + len(new_mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    print(f"resolved_statements={','.join(sid for sid, *_ in targets)}")
    print(f"open_endpoints={endpoint_counts([json.loads(x) for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{after_counts}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} {digest(before)}->{digest(after)}")
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
