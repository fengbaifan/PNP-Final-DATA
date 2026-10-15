from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_iv.md"
SEGMENT = "chp-6:06_CHP-6_sec_iv:l52-53"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-seciv-p161-l52-53-relation-classification-20261013"

EXPECTED = {
    STATEMENTS: "5b810a729008ba9bab1a0070d1e09fe6956e9a2d54e7053044591d9ceb4716d8",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
}

NOTES = {
    "st-chp6-p161-canini-faithful-pupil-of-domenichino": "This records Haskell's explicit pupil relationship; 'most faithful' remains his superlative characterization.",
    "st-chp6-p161-canini-protege-of-bellori": "This records Haskell's explicit patronage/protege relationship; 'his own' resolves to Bellori in the preceding clause.",
    "st-chp6-p161-christina-influence-arcadia-formation": "This records Haskell's qualified causal claim linking Christina's literary influence to the Society of Arcadia's formation; preserve the relative one-year interval.",
    "st-chp6-p161-christina-patronage-living-painters-limited": "This records Haskell's assessment of Christina's patronage relation to living painters; the source does not name the painters or a specific commission.",
    "st-chp6-p161-christina-patronizes-canini-with-bellori-guidance": "This records Haskell's account of Bellori encouraging Christina to patronise Canini; it does not imply a specific commission or employment.",
    "st-chp6-p161-gherardi-devotee-of-venetian-colour": "This records Haskell's characterization of Gherardi's devotion to Venetian colour as an artistic ideal.",
    "st-chp6-p161-mola-heir-venetian-tradition": "This records Haskell's comparative characterization of Mola in relation to the Venetian tradition; the superlative remains evaluative.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.161 section IV S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "[Page 161]" not in source_lines[51] or "Venetian tradition" not in source_lines[52]:
        raise SystemExit("p.161 source-line guard failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unset != set(NOTES):
        raise SystemExit(f"p.161 unset target set changed: {sorted(unset ^ set(NOTES))}")

    for sid, note in NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
    by_id["st-chp6-p161-christina-patronage-living-painters-limited"]["qualifiers"]["open_endpoint_reason"] = (
        "The passage refers generally to living painters without naming individuals or defining a bounded group; retain the source-defined open endpoint."
    )

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "segment": SEGMENT, "classified": len(unset), "relation_candidate_true": len(NOTES), "relation_candidate_false": 0, "unset_in_segment": 0, "before_sha256": digest(raw[STATEMENTS]), "after_sha256": digest(result)}, ensure_ascii=False))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
