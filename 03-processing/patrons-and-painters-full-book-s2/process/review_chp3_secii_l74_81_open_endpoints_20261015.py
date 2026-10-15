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
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
SEGMENT_ID = "chp-3:03_CHP-3_sec_ii:l74-81"
SUFFIX = "bak-s2-chp3-secii-l74-81-open-endpoints-20261015"


def sha(data: bytes) -> str:
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


def open_count(raw: bytes) -> int:
    total = 0
    for line in raw.decode("utf-8").splitlines():
        item = json.loads(line)
        q = item.get("qualifiers") or {}
        if q.get("relation_candidate") is True and (
            not item.get("subject_candidate_id") or not item.get("object_candidate_id")
        ):
            total += 1
    return total


def load_segment_text() -> str:
    for line in SEGMENTS.open(encoding="utf-8"):
        row = json.loads(line)
        if row.get("segment_id") == SEGMENT_ID:
            lines = SOURCE.read_text(encoding="utf-8").splitlines()
            return "\n".join(lines[int(row["line_start"]) - 1 : int(row["line_end"])])
    raise ValueError(f"Missing segment {SEGMENT_ID}")


def span(text: str, phrase: str) -> tuple[int, int]:
    start = text.find(phrase)
    if start < 0 or text.find(phrase, start + 1) >= 0:
        raise ValueError(f"Source phrase missing or repeated: {phrase}")
    return start, start + len(phrase)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidate_rows = read_csv(CANDIDATES)
    mention_raw, mention_fields, mention_rows = read_csv(MENTIONS)
    max_cid = max(int(re.fullmatch(r"cand-(\d+)", r["candidate_id"]).group(1)) for r in candidate_rows)
    if max_cid != 12316:
        raise ValueError(f"Candidate sequence changed: expected 12316, got {max_cid}")
    segment_mentions = [r for r in mention_rows if r.get("segment_id") == SEGMENT_ID]
    nums = [int(m.group(1)) for r in segment_mentions if (m := re.fullmatch(r"m-chp3-secii-l74-81-(\d+)", r["mention_id"]))]
    if max(nums, default=0) != 52:
        raise ValueError(f"Mention sequence changed: expected 52, got {max(nums, default=0)}")
    new_cids = ["cand-12317", "cand-12318"]
    new_mids = ["m-chp3-secii-l74-81-0053", "m-chp3-secii-l74-81-0054"]
    if any(r["candidate_id"] in new_cids for r in candidate_rows) or any(r["mention_id"] in new_mids for r in mention_rows):
        raise ValueError("A planned ID already exists")

    text = load_segment_text()
    sample = next(r for r in segment_mentions if r["mention_id"] == "m-chp3-secii-l74-81-0002")
    if int(sample["start_char"]) != text.index("his family chapel"):
        raise ValueError("Reconstructed segment text does not match existing mention offsets")
    surfaces = ["his chapel", "to artists for the next hundred years"]
    spans = [span(text, x) for x in surfaces]

    new_candidates = [
        {
            "candidate_id": new_cids[0], "index_entry_id": "",
            "canonical_name": "Individual chapels of the unnamed other Florentine families at S. Andrea della Valle",
            "index_page_range": "", "suggested_type": "place", "status": "open", "index_source_file": "",
            "sub_entry": "",
            "detail": "Distributive group: Haskell says each of several other Florentine families had a chapel they tried to make more beautiful than the others. Names, exact number, and individual chapel identities are not supplied; keep distinct from Maffeo Barberini's family chapel.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L75",
        },
        {
            "candidate_id": new_cids[1], "index_entry_id": "",
            "canonical_name": "Artists who used Lanfranco's S. Andrea della Valle dome as a model (unnamed collective)",
            "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says Lanfranco's dome served as a model to artists for the next hundred years. The artists are unnamed and unbounded; preserve the duration as Haskell's wording, not independently verified use by every artist.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L79",
        },
    ]
    new_mentions = [
        {
            "mention_id": new_mids[0], "segment_id": SEGMENT_ID, "candidate_id": new_cids[0],
            "surface_form": surfaces[0], "start_char": str(spans[0][0]), "end_char": str(spans[0][1]),
            "note": "Distributive singular for each of the other Florentine families; distinct from Maffeo's earlier chapel.",
        },
        {
            "mention_id": new_mids[1], "segment_id": SEGMENT_ID, "candidate_id": new_cids[1],
            "surface_form": surfaces[1], "start_char": str(spans[1][0]), "end_char": str(spans[1][1]),
            "note": "Unbounded artist collective within Haskell's stated hundred-year horizon.",
        },
    ]

    statement_raw = STATEMENTS.read_bytes()
    lines = statement_raw.decode("utf-8").splitlines(keepends=True)
    targets = {
        "st-chp3-secii-l74-81-florentine-families-competed-over-chapels",
        "st-chp3-secii-l74-81-lanfranco-dome-model-for-later-artists",
    }
    found: set[str] = set()
    for i, line in enumerate(lines):
        item = json.loads(line)
        sid = item.get("statement_id")
        if sid not in targets:
            continue
        found.add(sid)
        q = item.setdefault("qualifiers", {})
        if item.get("segment_id") != SEGMENT_ID or item.get("object_candidate_id"):
            raise ValueError(f"Unexpected statement state for {sid}")
        item["object_candidate_id"] = new_cids[0] if sid.endswith("chapels") else new_cids[1]
        if sid.endswith("chapels"):
            q["relation_candidate_note"] = "The quoted distributive 'his chapel' applies to each of the other Florentine families, defining a group of individual chapel spaces. Map that group separately from Maffeo Barberini's named family chapel; identities and count remain open."
        else:
            q["relation_candidate_note"] = "Haskell explicitly says the dome served as a model 'to artists for the next hundred years.' Link the unnamed artist collective, leave person-group type unset, and preserve the source's duration wording."
        q.pop("open_endpoint_reason", None)
        lines[i] = json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
    if found != targets:
        raise ValueError(f"Missing targets: {sorted(targets - found)}")

    candidate_after = append_csv(candidate_raw, candidate_fields, new_candidates)
    mention_after = append_csv(mention_raw, mention_fields, new_mentions)
    statement_after = "".join(lines).encode("utf-8")
    paths = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    backups = {p: p.with_name(f"{p.name}.{SUFFIX}") for p in paths}

    print(f"candidate_rows={len(candidate_rows)}->{len(candidate_rows)+2}")
    print(f"mention_rows={len(mention_rows)}->{len(mention_rows)+2}")
    print(f"statement_rows={sum(1 for _ in STATEMENTS.open(encoding='utf-8'))}->{len(lines)}")
    print(f"open_endpoints={open_count(statement_raw)}->{open_count(statement_after)}")
    for path, after in paths.items():
        print(f"{path.relative_to(ROOT)} {sha(path.read_bytes())}->{sha(after)}")
    print("resolved: Florentine chapel group cand-12317; unnamed later artists cand-12318")
    if args.preview:
        return 0

    if any(p.exists() for p in backups.values()):
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
        print(f"applied_sha256={path.relative_to(ROOT)}:{sha(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
