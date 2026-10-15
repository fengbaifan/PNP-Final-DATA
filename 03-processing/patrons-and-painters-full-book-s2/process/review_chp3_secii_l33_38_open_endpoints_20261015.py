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
SEGMENT_ID = "chp-3:03_CHP-3_sec_ii:l33-38"
SUFFIX = "bak-s2-chp3-secii-l33-38-open-endpoints-20261015"
OLD_SUBJECT_MAPPING = "m-s2-chp3-surface-63666aa72ed2899c"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_table(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
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


def source_text() -> str:
    for line in SEGMENTS.open(encoding="utf-8"):
        row = json.loads(line)
        if row.get("segment_id") == SEGMENT_ID:
            lines = SOURCE.read_text(encoding="utf-8").splitlines()
            return "\n".join(lines[int(row["line_start"]) - 1 : int(row["line_end"])])
    raise ValueError(f"Missing segment {SEGMENT_ID}")


def find_span(text: str, phrase: str) -> tuple[int, int]:
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

    cand_raw, cand_fields, cand_rows = csv_table(CANDIDATES)
    mention_raw, mention_fields, mention_rows = csv_table(MENTIONS)
    if max(int(re.fullmatch(r"cand-(\d+)", r["candidate_id"]).group(1)) for r in cand_rows) != 12313:
        raise ValueError("Candidate sequence changed; review IDs before continuing")
    seg_mentions = [r for r in mention_rows if r.get("segment_id") == SEGMENT_ID]
    numeric = [int(m.group(1)) for r in seg_mentions if (m := re.fullmatch(r"m-chp3-secii-l33-38-(\d+)", r["mention_id"]))]
    if max(numeric, default=0) != 53:
        raise ValueError(f"Mention sequence changed; expected 53, got {max(numeric, default=0)}")
    ids = ["cand-12314", "cand-12315", "cand-12316"]
    mention_ids = [f"m-chp3-secii-l33-38-{n:04d}" for n in range(54, 58)]
    if any(r["candidate_id"] in ids for r in cand_rows) or any(r["mention_id"] in mention_ids for r in mention_rows):
        raise ValueError("A planned candidate or mention ID already exists")

    text = source_text()
    sample = next(r for r in seg_mentions if r["mention_id"] == "m-chp3-secii-l33-38-0001")
    if int(sample["start_char"]) != text.index("S. Andrea"):
        raise ValueError("Reconstructed source text does not match existing mention offsets")
    surfaces = [
        "paintings in S. Andrea and S. Vitale",
        "fake pilasters and columns",
        "marble altars",
        "ornements d’architecture",
    ]
    spans = [find_span(text, phrase) for phrase in surfaces]

    new_candidates = [
        {
            "candidate_id": ids[0], "index_entry_id": "",
            "canonical_name": "Subject matter of the frescoes discussed by Louis Richeôme",
            "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "",
            "sub_entry": "",
            "detail": "The depicted subject matter that Richeôme says should direct devotion; specific fresco subjects are not enumerated. Distinct from the unrelated Contracts index subentry 'subject'.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L35",
        },
        {
            "candidate_id": ids[1], "index_entry_id": "",
            "canonical_name": "Paintings in S. Andrea al Quirinale and S. Vitale discussed by Richeôme",
            "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "",
            "sub_entry": "",
            "detail": "A source-defined group of paintings named as the subject of Richeôme's 1611 book; titles, individual works, and completeness of the group are not supplied.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L34",
        },
        {
            "candidate_id": ids[2], "index_entry_id": "",
            "canonical_name": "Ornamental forms Richeôme says do not touch devotion",
            "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "",
            "sub_entry": "",
            "detail": "A source-defined category including pilasters, columns, marble altars, cornices, pedestals, paintings, reliefs, and architectural ornaments. No individual object or exact church assignment is identified.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L34",
        },
    ]
    new_mentions = [
        {
            "mention_id": mention_ids[0], "segment_id": SEGMENT_ID, "candidate_id": ids[1],
            "surface_form": surfaces[0], "start_char": str(spans[0][0]), "end_char": str(spans[0][1]),
            "note": "Source-defined group named as the topic of Richeôme's book; individual paintings are not listed.",
        },
        {
            "mention_id": mention_ids[1], "segment_id": SEGMENT_ID, "candidate_id": ids[2],
            "surface_form": surfaces[1], "start_char": str(spans[1][0]), "end_char": str(spans[1][1]),
            "note": "One example of the heterogeneous ornamental category Richeôme rejects.",
        },
        {
            "mention_id": mention_ids[2], "segment_id": SEGMENT_ID, "candidate_id": ids[2],
            "surface_form": surfaces[2], "start_char": str(spans[2][0]), "end_char": str(spans[2][1]),
            "note": "Another example in Haskell's summary of Richeôme's position.",
        },
        {
            "mention_id": mention_ids[3], "segment_id": SEGMENT_ID, "candidate_id": ids[2],
            "surface_form": surfaces[3], "start_char": str(spans[3][0]), "end_char": str(spans[3][1]),
            "note": "French phrase for architectural ornaments in Richeôme's quotation.",
        },
    ]

    statement_raw = STATEMENTS.read_bytes()
    lines = statement_raw.decode("utf-8").splitlines(keepends=True)
    targets = {
        "st-chp3-secii-l33-38-new-church-not-dependent-on-one-patron",
        "st-chp3-secii-l33-38-philip-attracted-cultivated-people-and-decorated-church",
        "st-chp3-secii-l33-38-richeome-book-topic-paintings",
        "st-chp3-secii-l33-38-richeome-focused-devotion-on-fresco-subject",
        "st-chp3-secii-l33-38-richeome-rejected-extravagant-ornament",
    }
    found: set[str] = set()
    for i, line in enumerate(lines):
        item = json.loads(line)
        sid = item.get("statement_id")
        if sid not in targets:
            continue
        found.add(sid)
        if item.get("segment_id") != SEGMENT_ID:
            raise ValueError(f"Wrong segment for {sid}")
        q = item.setdefault("qualifiers", {})
        if sid.endswith("new-church-not-dependent-on-one-patron"):
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open endpoint for {sid}")
            q["open_endpoint_reason"] = (
                "'One all-powerful patron' is a generic counterfactual role, not an identified person or bounded group. "
                "Although Farnese is named as an obstruction, Haskell does not identify him as the sole patron whose goodwill "
                "would have been required; retain the negative scope and leave the endpoint open."
            )
        elif sid.endswith("philip-attracted-cultivated-people-and-decorated-church"):
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open endpoint for {sid}")
            item["object_candidate_id"] = "cand-5029"
            q["relation_candidate_note"] = "The source-defined group 'many of the most cultivated spirits of the time' is already recorded as candidate cand-5029; connect Philip Neri to that group and preserve the quantifier 'many'."
            q.pop("open_endpoint_reason", None)
        elif sid.endswith("richeome-book-topic-paintings"):
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open endpoint for {sid}")
            item["object_candidate_id"] = ids[1]
            q["relation_candidate_note"] = "The phrase 'paintings in S. Andrea and S. Vitale' is a source-defined group and the stated topic of Richeôme's book; no individual titles or exhaustive membership are supplied."
            q.pop("open_endpoint_reason", None)
        elif sid.endswith("richeome-focused-devotion-on-fresco-subject"):
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open endpoint for {sid}")
            item["object_candidate_id"] = ids[0]
            q["relation_candidate_note"] = "The intended object is the fresco subject matter, not the unrelated Contracts index subentry 'subject'. Map it to source-bound term cand-12314; specific images remain unidentified."
            q.pop("open_endpoint_reason", None)
        elif sid.endswith("richeome-rejected-extravagant-ornament"):
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open endpoint for {sid}")
            item["object_candidate_id"] = ids[2]
            q["relation_candidate_note"] = "Richeôme's quoted position concerns a source-defined category of ornamental forms, including the named architectural and pictorial examples; do not assign the rejection to one church or specific work."
            q.pop("open_endpoint_reason", None)
        lines[i] = json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
    if found != targets:
        raise ValueError(f"Missing targets: {sorted(targets - found)}")

    old_mention = next((r for r in mention_rows if r.get("mention_id") == OLD_SUBJECT_MAPPING), None)
    if not old_mention or old_mention.get("candidate_id") != "cand-0840" or old_mention.get("surface_form") != "subject":
        raise ValueError("Expected mistaken lexical mapping to Contracts/subject was not found")
    old_mention["candidate_id"] = ids[0]
    old_mention["note"] = "Iconographic subject matter of frescoes; corrected from the unrelated Contracts index subentry 'subject'."

    candidate_after = append_csv(cand_raw, cand_fields, new_candidates)
    mention_after = append_csv(mention_raw, mention_fields, new_mentions)
    mention_bytes = io.StringIO(newline="")
    writer = csv.DictWriter(mention_bytes, fieldnames=mention_fields, lineterminator="\r\n" if b"\r\n" in mention_raw else "\n")
    writer.writeheader()
    writer.writerows(mention_rows)
    mention_correction = mention_bytes.getvalue().encode("utf-8")
    # Preserve existing mention bytes except for the one corrected row, then append new mentions.
    old_csv = mention_raw.decode("utf-8-sig")
    old_rows_bytes = old_csv.splitlines(keepends=True)
    header = old_rows_bytes[0]
    newline = "\r\n" if b"\r\n" in mention_raw else "\n"
    patched_rows = [header]
    for row in mention_rows:
        stream = io.StringIO(newline="")
        csv.DictWriter(stream, fieldnames=mention_fields, lineterminator=newline).writerow(row)
        patched_rows.append(stream.getvalue())
    mention_after = "".join(patched_rows).encode("utf-8")
    if mention_raw.startswith(b"\xef\xbb\xbf"):
        mention_after = b"\xef\xbb\xbf" + mention_after
    # Add the four source-grounded mentions after the corrected existing rows.
    mention_after = append_csv(mention_after, mention_fields, new_mentions)
    statement_after = "".join(lines).encode("utf-8")

    paths = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    backups = {p: p.with_name(f"{p.name}.{SUFFIX}") for p in paths}
    print(f"candidate_rows={len(cand_rows)}->{len(cand_rows)+3}")
    print(f"mention_rows={len(mention_rows)}->{len(mention_rows)+4}")
    print(f"statement_rows={sum(1 for _ in STATEMENTS.open(encoding='utf-8'))}->{len(lines)}")
    print(f"open_endpoints={open_count(statement_raw)}->{open_count(statement_after)}")
    for path, after in paths.items():
        print(f"{path.relative_to(ROOT)} {sha(path.read_bytes())}->{sha(after)}")
    print("endpoint resolutions: cand-5029, cand-12314, cand-12315, cand-12316; retain one generic patron open")

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
                raise FileExistsError(f"Temporary file exists: {temp}")
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
