from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    STATEMENTS: "7d654dfb29798e67f2826d2e6c84a1d4178d3dd848e75f8c9bd6d635d1a8594c",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l71-78"
STATEMENT_ID = "st-chp2-secii-l71-78-marcello-searches-for-new-talent"
COPYIST_STATEMENT_ID = "st-chp2-secii-l71-78-marcello-sought-galatea-copyist"
MARCELLO_ID = "cand-2314"
PIETRO_ID = "cand-0342"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp2-marcello-talent-search-20261015")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_segment() -> str:
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 segment or source asset mismatch")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    return text


def build() -> bytes:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")
    text = source_segment()
    line = SOURCE.read_text(encoding="utf-8-sig").splitlines()[76]
    start = line.find("he was always searching for new talent")
    end_phrase = "Pietro da Cortona was at once brought within the Sacchetti orbit"
    end = line.find(end_phrase)
    if start < 0 or end < start:
        raise SystemExit("source context changed")
    quote = line[start:end + len(end_phrase)]
    if quote not in text:
        raise SystemExit("context quote is outside the registered segment")
    if "seeking out the artist" not in text or end_phrase not in text:
        raise SystemExit("cross-sentence identity link changed")

    rows = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    target = next((row for row in rows if row.get("statement_id") == STATEMENT_ID), None)
    if not target:
        raise SystemExit("target statement not found")
    q = dict(target.get("qualifiers", {}))
    if target.get("segment_id") != SEGMENT_ID or target.get("subject_candidate_id") != MARCELLO_ID or target.get("object_candidate_id") not in (None, "") or q.get("relation_candidate") is not True:
        raise SystemExit("target statement state changed")
    supporting = next((row for row in rows if row.get("statement_id") == COPYIST_STATEMENT_ID), None)
    if not supporting or supporting.get("object_candidate_id") != PIETRO_ID or "Pietro da Cortona" not in supporting.get("qualifiers", {}).get("claim", ""):
        raise SystemExit("supporting copyist statement changed")

    target["object_candidate_id"] = PIETRO_ID
    q.pop("open_endpoint_reason", None)
    q["claim"] = "Haskell says Marcello was always searching for new talent and illustrates this with his search for the artist of Raphael’s Galatea copy, identified in the next sentence as Pietro da Cortona."
    q["qualification"] = "The passage states a general practice, then narrates Marcello seeking out the Galatea copyist and identifies him as Pietro in the immediately following sentence. Preserve this as one example, not the only target of Marcello’s search."
    q["relation_candidate_note"] = "Haskell’s general statement about Marcello’s search is immediately followed by the specific Galatea-copy episode; the adjacent statement identifies the copyist as Pietro da Cortona. The endpoint represents this narrated example while retaining the broader wording."
    q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), PIETRO_ID]))
    target["qualifiers"] = q
    target["original_quote"] = quote

    output: list[bytes] = []
    found = False
    for raw in STATEMENTS.read_bytes().splitlines(keepends=True):
        if not raw.strip():
            output.append(raw)
            continue
        row = json.loads(raw)
        if row.get("statement_id") == STATEMENT_ID:
            ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
            output.append(json.dumps(target, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
            found = True
        else:
            output.append(raw)
    if not found:
        raise SystemExit("target row disappeared")
    updated = b"".join(output)
    if len(rows) != 15114:
        raise SystemExit(f"statement count changed: {len(rows)}")
    return updated


def apply(updated: bytes) -> None:
    if BACKUP.exists():
        raise SystemExit("recovery backup already exists")
    if sha(STATEMENTS.read_bytes()) != EXPECTED_HASHES[STATEMENTS]:
        raise SystemExit("statement table changed after preview")
    shutil.copy2(STATEMENTS, BACKUP)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=STATEMENTS.parent, delete=False) as handle:
            temp_path = Path(handle.name)
            handle.write(updated)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, STATEMENTS)
    except Exception:
        shutil.copy2(BACKUP, STATEMENTS)
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updated = build()
    print(f"{STATEMENTS.relative_to(ROOT)}: {sha(STATEMENTS.read_bytes())} -> {sha(updated)}")
    print(f"Object {PIETRO_ID} is one source-supported example of {MARCELLO_ID}'s general search for new talent; source quote extended through the next-sentence identification.")
    print("Projected open endpoints: 520 -> 519; candidate/mention/statement counts unchanged.")
    if args.apply:
        apply(updated)
        print("Applied with recovery backup.")


if __name__ == "__main__":
    main()
