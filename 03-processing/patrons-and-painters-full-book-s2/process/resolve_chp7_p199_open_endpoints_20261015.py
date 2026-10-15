from __future__ import annotations

import argparse
import copy
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
SOURCE = ROOT / "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
SEGMENT_ID = "chp-7:07_CHP-7_sec_iv:l89-95"
BACKUP_SUFFIX = "bak-s2-chp7-p199-open-endpoints-20261015"
EXPECTED_INPUT_HASHES = {
    "entity-candidates.csv": "9f74f394cb9c7bc7265716645aff439842d5e1b5ebef15fe3246fa23ba4766dc",
    "mentions.csv": "e43483fdde105b3fc9e1885dc14e08016714b8572c26644f860f5170d55aafec",
    "book-statements.jsonl": "303f21c9a61139078b62584936f167373c68bfd19ce699e94e8e7dd0ad4d6676",
}

CANDIDATES_TO_ADD = [
    {
        "candidate_id": "cand-12341",
        "canonical_name": "Art's role in civilising society as attributed to Shaftesbury (p. 199)",
        "detail": "Haskell says Shaftesbury was among the first to stress art's role in civilising society. This records the attributed theoretical concept, not an independently established causal law.",
    },
    {
        "candidate_id": "cand-12342",
        "canonical_name": "The proposition that a good society gives birth to good art (p. 199)",
        "detail": "Haskell describes this as Shaftesbury's less acceptable extension of the civilising role of art. Preserve the attribution and critique; do not state it as an established causal law.",
    },
    {
        "candidate_id": "cand-12343",
        "canonical_name": "Painting's emotional appeal in Haskell's account of Shaftesbury (p. 199)",
        "detail": "Haskell infers from Shaftesbury's informal writings that he recognized painting's emotional appeal. No particular text or painting is named.",
    },
]

MENTIONS_TO_ADD = [
    {
        "mention_id": "m-chp7-p199-civilising-role",
        "candidate_id": "cand-12341",
        "surface_form": "‘civilising’ society",
        "note": "The phrase names the social role of art attributed to Shaftesbury by Haskell.",
    },
    {
        "mention_id": "m-chp7-p199-good-society-good-art",
        "candidate_id": "cand-12342",
        "surface_form": "a good society would necessarily give birth to good art",
        "note": "Haskell identifies this as Shaftesbury's less acceptable extension of the preceding concept.",
    },
    {
        "mention_id": "m-chp7-p199-emotional-appeal",
        "candidate_id": "cand-12343",
        "surface_form": "the more emotional appeal of painting",
        "note": "The quality discussed in Haskell's reading of Shaftesbury's informal writings; no specific painting is identified.",
    },
]

NEW_STATEMENT_ID = "st-chp7-p199-shaftesbury-good-society-produces-good-art"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"), extrasaction="raise")
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidate_rows = read_csv(CANDIDATES)
    mention_raw, mention_fields, mention_rows = read_csv(MENTIONS)
    raw_by_name = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": STATEMENTS.read_bytes(),
    }
    for name, expected in EXPECTED_INPUT_HASHES.items():
        if digest(raw_by_name[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if max(int(cid.removeprefix("cand-")) for cid in candidate_ids) != 12340:
        raise ValueError("Candidate sequence changed")
    if {c["candidate_id"] for c in CANDIDATES_TO_ADD} & candidate_ids:
        raise ValueError("A planned candidate ID already exists")
    if {m["mention_id"] for m in MENTIONS_TO_ADD} & mention_ids:
        raise ValueError("A planned mention ID already exists")

    segment = next(
        json.loads(line) for line in SEGMENTS.open(encoding="utf-8")
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])

    added_mentions: list[dict[str, str]] = []
    spans: list[tuple[int, int, str]] = []
    for mention in MENTIONS_TO_ADD:
        start = text.find(mention["surface_form"])
        if start < 0 or text.find(mention["surface_form"], start + 1) >= 0:
            raise ValueError(f"Source phrase missing or repeated: {mention['mention_id']}")
        end = start + len(mention["surface_form"])
        if any(start < old_end and old_start < end for old_start, old_end, _ in spans):
            raise ValueError(f"Planned mentions overlap: {mention['mention_id']}")
        spans.append((start, end, mention["mention_id"]))
        for old in mention_rows:
            if old["segment_id"] != SEGMENT_ID:
                continue
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if start < old_end and old_start < end:
                raise ValueError(f"New mention overlaps existing mention {old['mention_id']}")
        added_mentions.append({
            "mention_id": mention["mention_id"], "segment_id": SEGMENT_ID,
            "candidate_id": mention["candidate_id"], "surface_form": mention["surface_form"],
            "start_char": str(start), "end_char": str(end), "note": mention["note"],
        })

    rows = [json.loads(line) for line in raw_by_name["book-statements.jsonl"].decode("utf-8").splitlines()]
    index = {row["statement_id"]: i for i, row in enumerate(rows)}
    target_ids = {
        "st-chp7-p199-choice-hercules-failed-to-convey-thought",
        "st-chp7-p199-shaftesbury-civilising-role-of-art",
        "st-chp7-p199-shaftesbury-emotional-appeal",
    }
    if not target_ids <= index.keys() or NEW_STATEMENT_ID in index:
        raise ValueError("Target or planned statement ID changed")
    for sid in target_ids:
        row = rows[index[sid]]
        if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") not in {"cand-7245", "cand-2426"}:
            raise ValueError(f"Target statement identity changed: {sid}")
        q = row.get("qualifiers") or {}
        if q.get("relation_candidate") is not True or row.get("object_candidate_id") is not None:
            raise ValueError(f"Target statement no longer has the expected open object: {sid}")

    before_open = sum(
        1 for row in rows
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    )
    if before_open != 470:
        raise ValueError(f"Open endpoint count changed: expected 470, got {before_open}")

    thought = rows[index["st-chp7-p199-choice-hercules-failed-to-convey-thought"]]
    q = thought["qualifiers"]
    thought["object_candidate_id"] = "cand-7249"
    q["mentioned_candidate_ids"] = ["cand-7245", "cand-7249"]
    q["relation_candidate_note"] = "The preceding page names Vice and Virtue as the work's moral theme; Haskell's judgment that the picture could not convey its complex thought remains attributed, not independent reception evidence."
    q["related_statement_ids"] = ["st-chp7-p198-shaftesbury-quoted-aesthetic-instruction"]
    q.pop("open_endpoint_reason", None)

    civilising = rows[index["st-chp7-p199-shaftesbury-civilising-role-of-art"]]
    civilising_quote = "He was one of the first to stress the role of art in\n‘civilising’ society"
    civilising["object_candidate_id"] = "cand-12341"
    civilising["predicate"] = "stressed_role_of_art_in_civilising_society"
    civilising["original_quote"] = civilising_quote
    q = civilising["qualifiers"]
    q["source_line_start"] = 93
    q["source_line_end"] = 94
    q["claim"] = "Haskell says Shaftesbury was one of the first to stress art's role in civilising society."
    q["qualification"] = "Haskell attributes the idea to Shaftesbury; the further proposition and Haskell's criticism are recorded separately."
    q["mentioned_candidate_ids"] = ["cand-2426", "cand-12341"]
    q["relation_candidate_note"] = "This records Shaftesbury's attributed theoretical concept of art's civilising role; it is not asserted as an independently established causal law."
    q.pop("open_endpoint_reason", None)

    good_society = copy.deepcopy(civilising)
    good_society["statement_id"] = NEW_STATEMENT_ID
    good_society["object_candidate_id"] = "cand-12342"
    good_society["predicate"] = "extended_theory_to_good_society_giving_birth_to_good_art"
    good_society_quote = "though he extended this to the less acceptable concept that a good society would necessarily give birth to good art"
    good_society["original_quote"] = good_society_quote
    q = good_society["qualifiers"]
    q["source_line_start"] = 94
    q["source_line_end"] = 94
    q["claim"] = "Haskell says Shaftesbury extended his account of art's civilising role to the less acceptable concept that a good society would necessarily give birth to good art."
    q["qualification"] = "Haskell calls this a less acceptable extension; the proposition is attributed to Shaftesbury, not endorsed as a causal law."
    q["mentioned_candidate_ids"] = ["cand-2426", "cand-12342"]
    q["relation_candidate_note"] = "This records Haskell's attributed account of Shaftesbury's proposition and preserves Haskell's explicit criticism."
    q.pop("open_endpoint_reason", None)

    emotional = rows[index["st-chp7-p199-shaftesbury-emotional-appeal"]]
    emotional["object_candidate_id"] = "cand-12343"
    emotional["predicate"] = "recognised_emotional_appeal_of_painting"
    emotional_quote = "And his informal writings prove that he was certainly not blind to the more emotional appeal of painting."
    emotional["original_quote"] = emotional_quote
    q = emotional["qualifiers"]
    q["claim"] = "Haskell says Shaftesbury's informal writings show that he was not blind to painting's more emotional appeal."
    q["qualification"] = "This is Haskell's inference from Shaftesbury's informal writings; no particular text or painting is identified."
    q["mentioned_candidate_ids"] = ["cand-2426", "cand-12343"]
    q["relation_candidate_note"] = "The object is the aesthetic quality named in the sentence; the claim remains Haskell's reading of unspecified informal writings."
    q.pop("open_endpoint_reason", None)

    added_candidates = [
        {
            "candidate_id": c["candidate_id"], "index_entry_id": "",
            "canonical_name": c["canonical_name"], "index_page_range": "",
            "suggested_type": "term", "status": "open", "index_source_file": "",
            "sub_entry": "", "detail": c["detail"], "exclude_reason": "",
            "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L94",
        }
        for c in CANDIDATES_TO_ADD
    ]
    candidate_after = append_csv(candidate_raw, candidate_fields, added_candidates)
    mention_after = append_csv(mention_raw, mention_fields, added_mentions)
    statement_after = ("".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        for row in rows + [good_society]
    )).encode("utf-8")
    paths = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    after_open_rows = [
        json.loads(line) for line in statement_after.decode("utf-8").splitlines()
        if (lambda r: r.get("segment_id") == SEGMENT_ID
            and (r.get("qualifiers") or {}).get("relation_candidate") is True
            and (not r.get("subject_candidate_id") or not r.get("object_candidate_id")))(json.loads(line))
    ]
    after_open = sum(
        1 for line in statement_after.decode("utf-8").splitlines()
        if (lambda r: (r.get("qualifiers") or {}).get("relation_candidate") is True
            and (not r.get("subject_candidate_id") or not r.get("object_candidate_id")))(json.loads(line))
    )
    print(f"candidate_rows={len(candidate_rows)}->{len(candidate_rows) + len(added_candidates)}")
    print(f"mention_rows={len(mention_rows)}->{len(mention_rows) + len(added_mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows) + 1}")
    print(f"open_endpoints={before_open}->{after_open}")
    print(f"segment_open={[r['statement_id'] for r in after_open_rows]}")
    for path, data in paths.items():
        print(f"{path.relative_to(ROOT)} {digest(path.read_bytes())}->{digest(data)}")
    if args.preview:
        return 0

    backups = {path: path.with_name(f"{path.name}.{BACKUP_SUFFIX}") for path in paths}
    if any(backup.exists() for backup in backups.values()):
        raise FileExistsError("A recovery copy already exists; refusing to overwrite it")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    temps: dict[Path, Path] = {}
    try:
        for path, data in paths.items():
            temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
            if temp.exists():
                raise FileExistsError(f"Temporary file already exists: {temp}")
            temp.write_bytes(data)
            temps[path] = temp
        for path, temp in temps.items():
            temp.replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        raise
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
