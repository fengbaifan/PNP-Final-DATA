from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_vii.md"
SEGMENTS = TABLES / "segments.jsonl"

EXPECTED_HASHES = {
    STATEMENTS: "73db073ef12b1f208337e5aecb7b2a47b996906f9777ea9760100ab0d072ed92",
    CANDIDATES: "98dcbf281c29380597ed333d99d8904b3d2490b8cd478cff844c59ef0cdd24f0",
    MENTIONS: "8686c40d25536147ca354307a47c58a67765dec31eb2c7ddf9f199d95a077d51",
}
SOURCE_SHA256 = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
SEGMENT_HASHES = {
    "chp-2:02_CHP-2_sec_vii:l5-19": "1b18b06e5140dfa2987c07e3901cfe46c546a3be3a32f4a6d661de2b98d251c6",
    "chp-2:02_CHP-2_sec_vii:l21-30": "e48382ee2fca2bf2cc0b3b462cb713065f12dccd36d92690e2a4017b10e49bb3",
}
NEW_CANDIDATE_ID = "cand-11895"
NEW_MENTION_ID = "m-chp2-secvii-l3-19-0082"
ARTISTS_SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l5-19"
ARTISTS_SOURCE_REF = "chp-2:02_CHP-2_sec_vii:l5-19#L11"
ARTISTS_SURFACE = "artists"

CLASSIFICATIONS = {
    "st-chp2-secvii-l5-19-barberini-presence-in-exile": (
        False,
        "Haskell's phrase characterizes the Barberini's influence at a reduced scale; it is a scalar authorial assessment, not a relation to another entity.",
    ),
    "st-chp2-secvii-l5-19-exile-impact-on-artists": (
        True,
        "The sentence explicitly states that the Barberini exile affected the collective denoted by 'artists'. Its membership is unspecified; Romanelli and Bernini are discussed separately and are not treated as the whole group.",
    ),
    "st-chp2-secvii-l5-19-patronage-after-return-fragment": (
        False,
        "This is the opening fragment of Haskell's evaluative statement about the scale of the Barberini's patronage after their return; it continues in the next segment and does not assert a relation between distinct entities.",
    ),
    "st-chp2-secvii-l21-30-patronage-after-return-continuation": (
        False,
        "This continuation completes Haskell's evaluative comparison of the Barberini's post-return patronage with its former scale; it is not a relation between distinct entities.",
    ),
    "st-chp2-secvii-l21-30-romanelli-death-1662-retirement": (
        False,
        "The statement reports Romanelli's death date and describes his circumstances as virtual retirement; it does not assert a relation between distinct entities.",
    ),
    "st-chp2-secvii-l21-30-tapestry-duration-fragment": (
        False,
        "This is a duration assertion about the tapestry work followed by an incomplete causal clause; the continuation is linked to the next segment and does not establish a relation between distinct entities.",
    ),
}

BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp2-secvii-l5-30-classifications-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp2-secvii-l5-30-open-artists-group-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp2-secvii-l5-30-open-artists-group-20261013"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_csv(path: Path, raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader)


def render_csv(path: Path, raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    rendered = output.getvalue().encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    return rendered


def load_statements(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def render_statements(raw: bytes, rows: list[dict]) -> bytes:
    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    return rendered


def verify_source_and_segments() -> None:
    source_raw = SOURCE.read_bytes()
    if sha256(source_raw) != SOURCE_SHA256:
        raise SystemExit("protected S0 source changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment_map = {row["segment_id"]: row for row in segment_rows}
    for segment_id, expected in SEGMENT_HASHES.items():
        segment = segment_map.get(segment_id)
        if not segment or segment.get("sha256") != expected:
            raise SystemExit(f"protected segment metadata changed: {segment_id}")
        segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
        if sha256(segment_text.encode("utf-8")) != expected:
            raise SystemExit(f"protected source lines changed: {segment_id}")
    segment = segment_map[ARTISTS_SEGMENT_ID]
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    start = segment_text.find(ARTISTS_SURFACE)
    if start < 0 or segment_text.find(ARTISTS_SURFACE, start + 1) >= 0:
        raise SystemExit("expected one exact 'artists' span in the target segment")
    if start != 1247:
        raise SystemExit(f"protected artists mention offset changed: {start}")
    line11 = source_lines[10]
    if "The exile of the Barberini was a terrible blow to artists." not in line11:
        raise SystemExit("expected exile-impact sentence changed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify six remaining section VII statements and register the explicit unnamed artist group.")
    parser.add_argument("--apply", action="store_true", help="write changes after protected preview checks")
    args = parser.parse_args()

    raw_by_path = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(raw_by_path[path])
        if actual != expected:
            raise SystemExit(f"protected table changed: {path.name}; expected {expected}, found {actual}")
    verify_source_and_segments()
    if any(path.exists() for path in BACKUPS.values()):
        existing = [path.name for path in BACKUPS.values() if path.exists()]
        raise SystemExit(f"backup already exists: {existing}")

    statement_rows = load_statements(raw_by_path[STATEMENTS])
    statement_map = {row.get("statement_id"): row for row in statement_rows}
    if len(statement_map) != len(statement_rows):
        raise SystemExit("duplicate statement_id in protected table")
    if not set(CLASSIFICATIONS).issubset(statement_map):
        raise SystemExit("one or more target statements are missing")
    candidate_fields, candidate_rows = load_csv(CANDIDATES, raw_by_path[CANDIDATES])
    mention_fields, mention_rows = load_csv(MENTIONS, raw_by_path[MENTIONS])
    if NEW_CANDIDATE_ID in {row.get("candidate_id") for row in candidate_rows}:
        raise SystemExit(f"candidate already exists: {NEW_CANDIDATE_ID}")
    if NEW_MENTION_ID in {row.get("mention_id") for row in mention_rows}:
        raise SystemExit(f"mention already exists: {NEW_MENTION_ID}")

    for statement_id in CLASSIFICATIONS:
        row = statement_map[statement_id]
        if row.get("qualifiers", {}).get("relation_candidate") is not None:
            raise SystemExit(f"statement already classified: {statement_id}")
        if row.get("segment_id") not in SEGMENT_HASHES:
            raise SystemExit(f"unexpected segment for {statement_id}: {row.get('segment_id')}")
        if row.get("object_candidate_id") is not None:
            raise SystemExit(f"unexpected pre-existing object endpoint: {statement_id}")
        q = row.get("qualifiers", {})
        if q.get("source_line_start") is None or q.get("source_line_end") is None:
            raise SystemExit(f"missing source line range: {statement_id}")
        source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
        cited = " ".join(" ".join(source_lines[int(q["source_line_start"]) - 1:int(q["source_line_end"])]).split())
        quote = " ".join(row.get("original_quote", "").split())
        if quote not in cited:
            raise SystemExit(f"quote does not match cited source lines: {statement_id}")

    candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Artists affected by the Barberini exile (unnamed collective)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell describes the Barberini exile as a terrible blow to artists. The members of this collective are not named or enumerated in this passage; Romanelli and Bernini are discussed separately and are not inferred to constitute the whole group.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": ARTISTS_SOURCE_REF,
    }
    if set(candidate) != set(candidate_fields):
        raise SystemExit("candidate schema changed; refusing to append candidate")
    candidate_rows.append(candidate)

    mention = {
        "mention_id": NEW_MENTION_ID,
        "segment_id": ARTISTS_SEGMENT_ID,
        "candidate_id": NEW_CANDIDATE_ID,
        "surface_form": ARTISTS_SURFACE,
        "start_char": "1247",
        "end_char": "1254",
        "note": "Unnamed collective explicitly named as affected by the Barberini exile; membership is unspecified.",
    }
    if set(mention) != set(mention_fields):
        raise SystemExit("mention schema changed; refusing to append mention")
    mention_rows.append(mention)

    for statement_id, (is_relation, note) in CLASSIFICATIONS.items():
        row = statement_map[statement_id]
        q = row["qualifiers"]
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note
        if statement_id == "st-chp2-secvii-l5-19-exile-impact-on-artists":
            row["object_candidate_id"] = NEW_CANDIDATE_ID
            mentioned = q.setdefault("mentioned_candidate_ids", [])
            if NEW_CANDIDATE_ID not in mentioned:
                mentioned.append(NEW_CANDIDATE_ID)

    rendered_by_path = {
        STATEMENTS: render_statements(raw_by_path[STATEMENTS], statement_rows),
        CANDIDATES: render_csv(CANDIDATES, raw_by_path[CANDIDATES], candidate_fields, candidate_rows),
        MENTIONS: render_csv(MENTIONS, raw_by_path[MENTIONS], mention_fields, mention_rows),
    }
    print("Section VII p.59–60 residual statement preview")
    for statement_id, (is_relation, note) in CLASSIFICATIONS.items():
        endpoint = f" object={NEW_CANDIDATE_ID}" if is_relation else ""
        print(f"{statement_id}: {'true' if is_relation else 'false'}{endpoint} — {note}")
    print(f"candidate: {NEW_CANDIDATE_ID} — {candidate['canonical_name']} (status=open)")
    print(f"mention: {NEW_MENTION_ID} — {ARTISTS_SURFACE} [{mention['start_char']},{mention['end_char']}) in {ARTISTS_SEGMENT_ID}")
    for path, rendered in rendered_by_path.items():
        print(f"{path.relative_to(ROOT)}: {sha256(raw_by_path[path])} -> {sha256(rendered)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return

    for path in rendered_by_path:
        shutil.copy2(path, BACKUPS[path])
        tmp = path.with_name(path.name + ".tmp-s2-secvii-l5-30")
        tmp.write_bytes(rendered_by_path[path])
        tmp.replace(path)
    print("mode=apply; backups=" + ", ".join(path.name for path in BACKUPS.values()))


if __name__ == "__main__":
    main()
