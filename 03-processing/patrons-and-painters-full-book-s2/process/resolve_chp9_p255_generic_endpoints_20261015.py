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
SEGMENT_ID = "chp-9:09_CHP-9_intro:l148-155"
BACKUP_SUFFIX = "bak-s2-chp9-p255-generic-endpoints-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "09fd28b562c9bae876b4041ad201c9ce2abe20231abf37735fcc134456ac11bb",
    "mentions.csv": "9c8d0649c7f8c1e19a46ef0ee206fb0327b460c656eca896b1bf7b8db7d646bc",
    "book-statements.jsonl": "dfb0f0e60023900fbc0860c26e7b4721088859dde5d55f5bc4cd46ba7eb0559b",
}
EXPECTED_SEGMENT_HASH = "f88796ddd6e409c8850bf64361d76760ed61b8c36cc02b18a32bfe7b35010e3d"
EXPECTED_AFTER = (425, 268, 53, 104)
NEW_CANDIDATES = (
    {
        "candidate_id": "cand-12378",
        "canonical_name": "Family age, wisdom, and virtue suggested by personified Time in Haskell's p.255 account",
        "line": 152,
        "type": "term",
        "detail": "A source-bounded symbolic concept: Haskell says a standard figure of Time could suggest a family's age, wisdom and virtue, while the reference need not be precise. No specific family is identified.",
    },
    {
        "candidate_id": "cand-12379",
        "canonical_name": "Most eighteenth-century Venetian artists in Haskell's p.255 account of modelli",
        "line": 155,
        "type": "term",
        "detail": "The collective class described by Haskell as 'most' eighteenth-century Venetian artists who first produced modelli for patron inspection. It does not mean all artists or identify individual members.",
    },
)


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
            raise ValueError(f"Input table changed since review: {name}")
    for info in NEW_CANDIDATES:
        if any(r["candidate_id"] == info["candidate_id"] or r["canonical_name"] == info["canonical_name"] for r in candidates):
            raise ValueError(f"Candidate ID or name already exists: {info['candidate_id']}")

    segment = next(
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Page 255 segment changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    phrases = {
        "cand-12378": "old in wisdom and virtue",
        "cand-12379": "Most Venetian artists of the eighteenth century",
    }
    candidate_rows = []
    new_mentions = []
    for info in NEW_CANDIDATES:
        line_no = info["line"]
        line = source_lines[line_no - 1]
        surface = phrases[info["candidate_id"]]
        if line.count(surface) != 1:
            raise ValueError(f"Expected unique source phrase not found: {surface}")
        line_base = sum(len(text) + 1 for text in source_lines[int(segment["line_start"]) - 1 : line_no - 1])
        start = line.find(surface)
        candidate_rows.append({
            "candidate_id": info["candidate_id"], "index_entry_id": "", "canonical_name": info["canonical_name"],
            "index_page_range": "", "suggested_type": info["type"], "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": info["detail"],
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
        })
        mid = "m-chp9-p255-family-time-symbol" if info["candidate_id"] == "cand-12378" else "m-chp9-p255-most-venetian-artists-modelli"
        if any(m["mention_id"] == mid for m in mentions):
            raise ValueError(f"Mention ID already exists: {mid}")
        new_mentions.append({
            "mention_id": mid, "segment_id": SEGMENT_ID, "candidate_id": info["candidate_id"],
            "surface_form": surface, "start_char": str(line_base + start),
            "end_char": str(line_base + start + len(surface)),
            "note": info["detail"],
        })

    rows = [json.loads(text) for text in statement_raw.decode("utf-8").splitlines() if text.strip()]
    if endpoint_counts(rows) != (427, 269, 54, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {endpoint_counts(rows)}")
    index = {r["statement_id"]: r for r in rows}
    ids = {
        "artist": "st-chp9-p255-artist-initiative-in-subject-choice",
        "modelli": "st-chp9-p255-modelli-presented-for-inspection",
        "families": "st-chp9-p255-old-families-followed-historical-subjects",
        "time": "st-chp9-p255-time-as-suggestive-family-symbol",
    }
    for key, sid in ids.items():
        if sid not in index or not is_open(index[sid]):
            raise ValueError(f"Expected open p.255 statement missing: {sid}")

    modelli = index[ids["modelli"]]
    modelli["subject_candidate_id"] = "cand-12379"
    mq = modelli["qualifiers"]
    mq["mentioned_candidate_ids"] = list(dict.fromkeys((mq.get("mentioned_candidate_ids") or []) + ["cand-12379"]))
    mq["relation_candidate_note"] = "The source names the subject only as 'most' eighteenth-century Venetian artists; this source-defined group preserves that scope without identifying individuals or extending the claim to all artists."
    mq.pop("open_endpoint_reason", None)

    time_row = index[ids["time"]]
    time_row["object_candidate_id"] = "cand-12378"
    tq = time_row["qualifiers"]
    tq["mentioned_candidate_ids"] = list(dict.fromkeys((tq.get("mentioned_candidate_ids") or []) + ["cand-12378"]))
    tq["relation_candidate_note"] = "The symbolic target is the source-bounded idea that a family could be represented as old in wisdom and virtue; the passage names no specific family and retains 'could suggest'."
    tq.pop("open_endpoint_reason", None)

    artist = index[ids["artist"]]
    aq = artist["qualifiers"]
    aq["open_endpoint_reason"] = "Haskell makes a general claim about 'at least some cases' and does not identify the artist who initiated the choice. Tiepolo is discussed nearby, but the statement's scope is generic; do not assign the claim to him."
    aq["relation_candidate_note"] = "The source supports artist initiative in some cases but leaves the artist(s) unnamed; preserve the open subject rather than map the adjacent Tiepolo example."

    families = index[ids["families"]]
    fq = families["qualifiers"]
    fq["open_endpoint_reason"] = "This statement combines two propositions: other old families followed the Corner example, and subjects of this kind were beyond the reach of a Widmann or a Grassi. The current Venetian-nobility endpoint does not represent both claims or identify the unnamed group; atomize the claim before assigning a scalar subject."
    fq["relation_candidate_note"] = "The source refers to a generic group of old families and then contrasts subject access with Widmann and Grassi. Keep the compound statement endpoint open until the two propositions are separated; do not force the Venetian-nobility term into both roles."

    if endpoint_counts(rows) != EXPECTED_AFTER:
        raise ValueError(f"Unexpected post-update endpoint counts: {endpoint_counts(rows)}")
    candidate_after = append_rows(candidate_raw, candidate_fields, candidate_rows)
    mention_after = append_rows(mention_raw, mention_fields, new_mentions)
    statement_after = ("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)).encode("utf-8")
    print(f"candidates={len(candidates)}->{len(candidates) + len(candidate_rows)}")
    print(f"mentions={len(mentions)}->{len(mentions) + len(new_mentions)}")
    print(f"statements={len([1 for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{len(rows)}")
    print("resolved=modelli_generic_group->cand-12379; time_symbol_target->cand-12378")
    print("reviewed_open=artist_generic_subject; old_families_compound_claim")
    print(f"open_endpoints={endpoint_counts([json.loads(x) for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{endpoint_counts(rows)}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} sha256 {digest(before)}->{digest(after)}")
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
