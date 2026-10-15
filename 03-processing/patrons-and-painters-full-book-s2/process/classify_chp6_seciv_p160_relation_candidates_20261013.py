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
SEGMENT = "chp-6:06_CHP-6_sec_iv:l40-50"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-seciv-p160-relation-classification-20261013"

EXPECTED = {
    STATEMENTS: "0b86f3c5d9e9c306788d5db925e6da203c5cad35ca5a3e4645a79cb6cfd90584",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
}

TRUE_NOTES = {
    "st-chp6-p160-artists-from-other-cities-rome": "This records Haskell's claim about visiting artists being scorned in Rome and conditionally compelled to regularise their style; unnamed artists remain a source-defined group.",
    "st-chp6-p160-artists-use-of-christina-collection": "This is Haskell's explicit relation between Rome's artists and Christina's displayed pictures, framed as an evaluative claim about their failure to draw inspiration from them.",
    "st-chp6-p160-bellori-accademia-christina-appointments": "This records Bellori's dated secretary appointment and subsequent appointment to Christina's service; the undated sequence is preserved.",
    "st-chp6-p160-bellori-influence-on-gaulli-reception": "This records Haskell's qualified attribution of part of the hostile reception to Bellori's classicising influence.",
    "st-chp6-p160-bellori-opposes-rival-view": "This records Bellori's opposition to the source-defined rival artistic view; the separate explanation of its limited Roman reception remains qualified and deferred.",
    "st-chp6-p160-bellori-words-hardened-into-dogma": "This records the reception of Bellori's ideas among followers; the followers remain unnamed and the duration is Haskell's characterization.",
    "st-chp6-p160-christina-arrival-conversion": "This records Christina's arrival in Rome in relation to her earlier conversion; no conversion date is inferred from her stated age.",
    "st-chp6-p160-christina-collection-displayed": "This records Christina displaying a collection at Palazzo Riario on the Lungara; the collection's identity and individual works remain unresolved.",
    "st-chp6-p160-christina-patronage-mola-partial": "This preserves the explicit relation of Christina's admiration to Mola alongside Haskell's separate qualified assessment of her patronage.",
    "st-chp6-p160-christina-travel-and-residence": "This records Christina's reported travel to France and Sweden and residence in Rome through 1689; individual voyage dates are not supplied.",
    "st-chp6-p160-gaulli-fresco-hostile-reception": "This records the reported reception of Gaulli's Gesu frescoes and the anonymous artists' collective appraisal without naming its members.",
    "st-chp6-p160-gaulli-later-classical-style": "This records Haskell's claim that Gaulli adopted a more classical style in subsequent works; those works are not individually identified.",
    "st-chp6-p160-gustavus-looted-collection-from-prague": "This records Haskell's claim that Gustavus Adolphus looted pictures from Prague for the collection; it is not independent verification and the collection is not merged with another candidate.",
    "st-chp6-p160-maratta-classical-comparison": "This records Haskell's explicit comparison of Maratta's painting with the classical ideal and high Baroque artists, retaining the author's evaluative framing.",
}

FALSE_NOTES = {
    "st-chp6-p160-articulate-criticism-public-sentiment": "This is Haskell's broad causal interpretation of a general public sentiment, not a specific entity relation; it does not claim that criticism caused artistic decline.",
    "st-chp6-p160-bellori-influence-grew": "This is a general biographical statement about Bellori's growing influence over time, without a specific target entity.",
    "st-chp6-p160-christina-quoted-appearance": "This is a quoted physical characterization of Christina; the cited authors are not assigned as the speaker of any particular phrase.",
    "st-chp6-p160-christina-social-and-cultural-influence": "This is a broad characterization of Christina's social effect and eccentricity; the political, literary, and artistic circles are not identified as specific endpoints.",
    "st-chp6-p160-haskell-interprets-shortage-sentiment": "This is Haskell's broad interpretation of a reported sentiment, not a specific entity relation; its two qualified explanations remain distinct.",
    "st-chp6-p160-jacomo-di-castro-1670-shortage": "This records a nested quotation attributed to Jacomo di Castro, not a relation between identified entities; the letter citation is handled separately as source evidence.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.160 S2 statement relation candidacy")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "[Page 160]" not in source_lines[39] or not all(source_lines[n - 1].strip() for n in range(41, 51)):
        raise SystemExit("p.160 source-line guard failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    targets = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES) | set(FALSE_NOTES)
    if targets != expected_targets or len(targets) != 20:
        raise SystemExit(f"p.160 unset target set changed: {sorted(targets ^ expected_targets)}")

    import csv
    import io

    candidates = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidates}
    for sid in sorted(targets):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 41 or end > 50 or start > end:
            raise SystemExit(f"invalid p.160 source anchor: {sid} {start}-{end}")
        endpoint_ids = [row.get("subject_candidate_id"), row.get("object_candidate_id")]
        endpoint_ids += q.get("mentioned_candidate_ids", [])
        missing = sorted({cid for cid in endpoint_ids if cid and cid not in candidate_ids})
        if missing:
            raise SystemExit(f"candidate endpoint missing for {sid}: {missing}")

    for sid, note in TRUE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
    for sid, note in FALSE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    counts = {"relation_candidate_true": len(TRUE_NOTES), "relation_candidate_false": len(FALSE_NOTES), "unset_in_segment": 0}
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "segment": SEGMENT, "classified": len(targets), "counts": counts, "before_sha256": digest(raw[STATEMENTS]), "after_sha256": digest(result)}, ensure_ascii=False))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
