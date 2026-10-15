from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_iv.md"
SEGMENT_ID = "chp-5:05_CHP-5_sec_iv:l3-12"
FOLLOWING_SEGMENT = "chp-5:05_CHP-5_sec_iv:l14-21"
SUFFIX = "bak-s2-chp5-rosa-open-groups-20261015"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, fieldnames=fields, lineterminator=newline, extrasaction="raise").writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline.encode("ascii")
    return raw + stream.getvalue().encode("utf-8")


def load_segment_text(segment_id: str) -> str:
    segment = next(json.loads(line) for line in SEGMENTS.open(encoding="utf-8") if json.loads(line).get("segment_id") == segment_id)
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])


def unique_span(text: str, phrase: str) -> tuple[int, int]:
    start = text.find(phrase)
    if start < 0 or text.find(phrase, start + 1) >= 0:
        raise ValueError(f"Source phrase missing or repeated: {phrase}")
    return start, start + len(phrase)


def open_count(raw: bytes) -> int:
    count = 0
    for line in raw.decode("utf-8").splitlines():
        row = json.loads(line)
        q = row.get("qualifiers") or {}
        if q.get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")):
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidate_rows = read_csv(CANDIDATES)
    mention_raw, mention_fields, mention_rows = read_csv(MENTIONS)
    max_cid = max(int(re.fullmatch(r"cand-(\d+)", row["candidate_id"]).group(1)) for row in candidate_rows)
    if max_cid != 12320:
        raise ValueError(f"Candidate sequence changed: expected 12320, got {max_cid}")
    new_candidate_ids = {"cand-12321", "cand-12322"}
    new_mention_ids = {
        "m-chp5-p142-rosa-social-circle",
        "m-chp5-p142-rosa-unnamed-clients",
        "m-chp5-p142-bamboccianti-patrons",
    }
    if any(row["candidate_id"] in new_candidate_ids for row in candidate_rows):
        raise ValueError("A planned candidate ID already exists")
    if any(row["mention_id"] in new_mention_ids for row in mention_rows):
        raise ValueError("A planned mention ID already exists")

    first_text = load_segment_text(SEGMENT_ID)
    spans = {
        "a brilliant society": unique_span(first_text, "a brilliant society"),
        "lais clients": unique_span(first_text, "lais clients"),
        "their patrons": unique_span(first_text, "their patrons"),
    }
    new_candidates = [
        {
            "candidate_id": "cand-12321", "index_entry_id": "",
            "canonical_name": "Unidentified Florentine society at whose centre Rosa found himself (p. 142)",
            "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says Rosa found himself at the centre of a brilliant society in Florence and continues that his social talents were admired there. The members and boundaries of this social circle are not identified.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L12",
        },
        {
            "candidate_id": "cand-12322", "index_entry_id": "",
            "canonical_name": "Unidentified patrons of the Bamboccianti artist and followers in Rosa's satire",
            "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says Rosa's bitterness was directed at the patrons of the artist and followers discussed in the Bamboccianti passage. No patron, membership, or number is named; the embedded satire is mediated through Haskell.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L8",
        },
    ]
    new_mentions = [
        {
            "mention_id": "m-chp5-p142-rosa-social-circle", "segment_id": SEGMENT_ID,
            "candidate_id": "cand-12321", "surface_form": "a brilliant society",
            "start_char": str(spans["a brilliant society"][0]), "end_char": str(spans["a brilliant society"][1]),
            "note": "Unnamed Florentine social circle; membership and boundaries are not supplied.",
        },
        {
            "mention_id": "m-chp5-p142-rosa-unnamed-clients", "segment_id": SEGMENT_ID,
            "candidate_id": "cand-6218", "surface_form": "lais clients",
            "start_char": str(spans["lais clients"][0]), "end_char": str(spans["lais clients"][1]),
            "note": "OCR surface preserved; print reads 'his clients'. Context contrasts Rosa's view with Haskell's immediately following account of the Roman connoisseurs' influence.",
        },
        {
            "mention_id": "m-chp5-p142-bamboccianti-patrons", "segment_id": SEGMENT_ID,
            "candidate_id": "cand-12322", "surface_form": "their patrons",
            "start_char": str(spans["their patrons"][0]), "end_char": str(spans["their patrons"][1]),
            "note": "Patrons of the artist and followers under discussion; this is a different group from Rosa's clients.",
        },
    ]

    statement_raw = STATEMENTS.read_bytes()
    statement_lines = statement_raw.decode("utf-8").splitlines(keepends=True)
    targets = {
        "st-chp5-p142-rosa-at-center-of-florentine-society": (None, "cand-12321"),
        "st-chp5-p142-rosa-landscapes-and-battles-as-client-driven-compromise": (None, "cand-6218"),
        "st-chp5-p142-rosa-satire-targeted-patrons": (None, "cand-12322"),
        "st-chp5-p143-rosa-talents-admired-in-florence": (FOLLOWING_SEGMENT, "cand-12321"),
    }
    found: set[str] = set()
    for i, line in enumerate(statement_lines):
        row = json.loads(line)
        sid = row.get("statement_id")
        if sid not in targets:
            continue
        expected_segment, new_object = targets[sid]
        expected_segment = expected_segment or SEGMENT_ID
        if row.get("segment_id") != expected_segment or row.get("subject_candidate_id") != "cand-2236" or row.get("object_candidate_id") is not None:
            raise ValueError(f"Unexpected statement state for {sid}")
        q = row.setdefault("qualifiers", {})
        if q.get("relation_candidate") is not True:
            raise ValueError(f"Statement is no longer a relation candidate: {sid}")
        row["object_candidate_id"] = new_object
        q["mentioned_candidate_ids"] = list(dict.fromkeys([*(q.get("mentioned_candidate_ids") or []), new_object]))
        if sid == "st-chp5-p142-rosa-at-center-of-florentine-society":
            q["claim"] = "Haskell says Rosa found himself at the centre of an unidentified brilliant society in Florence; the following segment continues that his social talents were admired there."
            q["relation_candidate_note"] = "Use one source-bounded open group for the 'brilliant society' and the continuation's Florentine audience; preserve Florence as setting, not as the group endpoint."
        elif sid == "st-chp5-p142-rosa-landscapes-and-battles-as-client-driven-compromise":
            q["claim"] = "Haskell reports Rosa's view that client obtuseness compelled him to paint landscapes and battles, contrasting it with his own account that Roman connoisseurs shaped Rosa's landscape output."
            q["qualification"] = "Keep Rosa's reported perspective distinct from Haskell's evaluative account; the shared source-bounded group is the unnamed Roman connoisseurs in the following sentence."
            q["relation_candidate_note"] = "Context links Rosa's unnamed 'clients' to Haskell's immediately following Roman connoisseurs, who are said to have compelled his landscape production. Link the existing open group candidate and preserve the differing attribution; do not infer individual membership."
            q["related_statement_ids"] = list(dict.fromkeys([*(q.get("related_statement_ids") or []), "st-chp5-p142-roman-connoisseurs-shaped-rosa-landscape-output"]))
        elif sid == "st-chp5-p142-rosa-satire-targeted-patrons":
            q["relation_candidate_note"] = "The phrase 'their patrons' explicitly identifies an unnamed group distinct from Rosa's own clients; use a separate open group candidate. The embedded satire remains mediated through Haskell."
        else:
            q["claim"] = "Haskell says Rosa's conversation, music, poetry, and mime were admired as much as his painting by the Florentine society introduced at the end of the preceding segment."
            q["qualification"] = "This continues the preceding segment's 'brilliant society'; no members are named."
            q["relation_candidate_note"] = "Resolve the unnamed Florentine audience to the same open social-circle candidate introduced in the preceding segment; preserve the continuation link."
            q["related_statement_ids"] = list(dict.fromkeys([*(q.get("related_statement_ids") or []), "st-chp5-p142-rosa-at-center-of-florentine-society"]))
        q.pop("open_endpoint_reason", None)
        statement_lines[i] = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        found.add(sid)
    if found != set(targets):
        raise ValueError(f"Missing targets: {sorted(set(targets) - found)}")

    candidate_after = append_csv(candidate_raw, candidate_fields, new_candidates)
    mention_after = append_csv(mention_raw, mention_fields, new_mentions)
    statement_after = "".join(statement_lines).encode("utf-8")
    paths = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    backups = {path: path.with_name(f"{path.name}.{SUFFIX}") for path in paths}
    print(f"candidate_rows={len(candidate_rows)}->{len(candidate_rows)+2}")
    print(f"mention_rows={len(mention_rows)}->{len(mention_rows)+3}")
    print(f"statement_rows={len(statement_lines)} unchanged")
    print(f"open_endpoints={open_count(statement_raw)}->{open_count(statement_after)}")
    for path, after in paths.items():
        print(f"{path.relative_to(ROOT)} {digest(path.read_bytes())}->{digest(after)}")
    print("resolved: Florentine society cand-12321 across p.142-p.143; Rosa clients cand-6218; separate Bamboccianti patron group cand-12322")
    if args.preview:
        return 0
    if any(path.exists() for path in backups.values()):
        raise FileExistsError("A recovery copy already exists; refusing to overwrite it")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    temps: dict[Path, Path] = {}
    try:
        for path, data in paths.items():
            temp = path.with_name(f"{path.name}.tmp-{SUFFIX}")
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
