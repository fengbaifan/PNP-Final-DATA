from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l144-179"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-ii-l144-179-relations-20261010")
EXPECTED = {
    TABLE: "f08928f63c73ce666ab11988370a3001363176273e5263c9044b130d75315061",
    CANDIDATES: "1c36e0fa29ea9f353eb8ac121ede84eca7414b08b122fa3afb5ea09b4d54789e",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
}
NOTES = {
    "st-chp3-secii-l144-179-oratorian-conditions-for-rubens": "The passage reports the Oratorians' conditions for Rubens's commission: examples, a contribution to cost, and an instructed composition.",
    "st-chp3-secii-l144-179-oratorians-accepted-revised-proposal": "The Oratorians accepted Rubens's revised proposal after he identified the first canvas's lighting problem.",
    "st-chp3-secii-l144-179-revised-proposal-layout": "The proposed central and lateral pictures were to enclose the existing miraculous Madonna and Child image; the intended slate medium and lighting rationale remain in the claim.",
    "st-chp3-secii-l144-179-rubens-found-lighting-unsatisfactory": "The statement records Rubens's own assessment of the first canvas's lighting, not an independent modern judgment.",
    "st-chp3-secii-l144-179-rubens-painted-first-picture": "Haskell says Rubens painted the first picture under the agreed terms to the Oratorians' satisfaction.",
    "st-chp3-secii-l144-179-rubens-persuaded-revised-proposal": "Haskell says Rubens persuaded the Oratorians to accept a new proposal; the statement preserves the sequence and lighting rationale.",
    "st-chp3-secii-l144-179-serra-threat-reluctant-agreement": "Haskell reports Serra's conditional threat to redirect his funds and the Oratorians' reluctant agreement; retain both actors and the reported condition.",
    "st-chp3-secii-p67-note2-anonymous-life-claim": "The anonymous Latin life is reported to say that Lauretano's example was followed in other Jesuit churches; keep the statement attributed to that source.",
    "st-chp3-secii-p67-note2-necrology-claim": "The quoted necrology presents Lauretano as the first person its writer knew to initiate annotated martyrdom paintings; preserve the writer's qualification and the cited church example.",
    "st-chp3-secii-p67-note2-rector-identification": "The phrase 'the same rector' links the previously unnamed German College rector to Lauretano through the cited necrology; this is a source-based identification claim.",
    "st-chp3-secii-p67-note5-church-replacement": "The note says the referenced earlier S. Andrea al Quirinale church was pulled down to make way for Bernini's replacement church.",
    "st-chp3-secii-p73-note5-drawing-project-link": "Haskell says the drawing was probably connected with Domenichino's S. Ignazio project; retain the probability rather than assert certainty.",
    "st-chp3-secii-p75-note6-sapienza-appointment": "The note says Borromini became architect of the Sapienza in 1632; the Sapienza referent and type remain unresolved.",
    "st-chp3-secii-p76-note3-catinari-barnabite": "The note identifies S. Carlo ai Catinari as a Barnabite church.",
    "st-chp3-secii-p76-note3-dome-pupil": "The note attributes the dome painting to an unnamed pupil of Guido Reni; keep the painter unidentified.",
}

def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

def normalized(value: str) -> str:
    return " ".join(value.split())

def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + b"".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline for r in rows)

def atomic_write(path: Path, payload: bytes) -> None:
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as f:
            f.write(payload)
            temp = Path(f.name)
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    for path, expected in EXPECTED.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed: {path.relative_to(ROOT)}")
    require(not BACKUP.exists(), "recovery backup already exists")
    raw = TABLE.read_bytes()
    rows = read_jsonl(TABLE)
    require(len(rows) == 12750 and len({r["statement_id"] for r in rows}) == len(rows), "statement table changed")
    by_id = {r["statement_id"]: r for r in rows}
    segment_rows = [r for r in rows if r.get("segment_id") == SEGMENT]
    pending = {r["statement_id"] for r in segment_rows if r.get("subject_candidate_id") and r.get("object_candidate_id") and (r.get("qualifiers") or {}).get("relation_candidate") is None}
    require(pending == set(NOTES) and len(pending) == 15, "pending bilateral statement set changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[143:179])
    require("They laid down stringent conditions" in source_text and "same rector" in source_text and "Sapienza in 1632" in source_text, "source segment text changed")
    require(all(normalized(by_id[sid].get("original_quote", "")) in normalized(source_text) for sid in pending), "a pending quote does not match the source segment")
    manifest = {r["segment_id"]: r for r in read_jsonl(SEGMENTS)}.get(SEGMENT)
    require(manifest and (manifest.get("source_file"), manifest.get("line_start"), manifest.get("line_end")) == ("02-sources/02-Markdown/03_CHP-3_sec_ii.md", 144, 179), "S0 segment boundary changed")
    with COVERAGE.open(encoding="utf-8-sig", newline="") as f:
        coverage = next((r for r in csv.DictReader(f) if r["segment_id"] == SEGMENT), None)
    require(coverage and (coverage["disposition"], coverage["migration_status"]) == ("reviewed", "complete"), "S2 coverage incomplete")
    candidates = {r["candidate_id"] for r in csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
    require(all(by_id[sid].get("subject_candidate_id") in candidates and by_id[sid].get("object_candidate_id") in candidates for sid in pending), "candidate endpoint missing")
    for sid, note in NOTES.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q.update(relation_candidate=True, relation_candidate_note=note)
        by_id[sid]["qualifiers"] = q
    flag = lambda r: (r.get("qualifiers") or {}).get("relation_candidate")
    bilateral = [r for r in rows if r.get("subject_candidate_id") and r.get("object_candidate_id")]
    b_true = sum(flag(r) is True for r in bilateral)
    b_false = sum(flag(r) is False for r in bilateral)
    b_pending = sum(flag(r) is None for r in bilateral)
    relation_total = sum(flag(r) is True for r in rows)
    relation_open = sum(flag(r) is True and not (r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in rows)
    require((len(bilateral), b_true, b_false, b_pending, relation_total, relation_open) == (8543, 4790, 475, 3278, 4839, 49), "projected whole-book counts differ")
    seg = [r for r in segment_rows]
    seg_true = sum(flag(r) is True for r in seg)
    seg_pending = sum(flag(r) is None for r in seg if r.get("subject_candidate_id") and r.get("object_candidate_id"))
    require((sum(flag(r) is True for r in seg if r.get("subject_candidate_id") and r.get("object_candidate_id")), seg_pending) == (17, 0), "projected segment bilateral counts differ")
    payload = encode_jsonl(rows, raw)
    report = {"action": "apply" if args.apply else "dry-run", "segment_id": SEGMENT, "new_relation_candidates": len(NOTES), "bilateral_after": {"total": len(bilateral), "relation_candidates": b_true, "nonrelations": b_false, "unclassified": b_pending}, "relation_candidates_total": relation_total, "relation_candidates_open": relation_open, "post_write_sha256": hashlib.sha256(payload).hexdigest()}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return
    shutil.copy2(TABLE, BACKUP)
    try:
        atomic_write(TABLE, payload)
        saved = read_jsonl(TABLE)
        saved_by_id = {r["statement_id"]: r for r in saved}
        require(len(saved) == 12750 and all((saved_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is True for sid in NOTES), "post-write classifications differ")
        require(digest(TABLE) == hashlib.sha256(payload).hexdigest(), "post-write digest differs")
    except Exception:
        if BACKUP.exists():
            shutil.copy2(BACKUP, TABLE)
        raise
    report["result"] = "applied"
    report["backup"] = str(BACKUP.relative_to(ROOT))
    report["sha256_after"] = digest(TABLE)
    print(json.dumps(report, ensure_ascii=True, indent=2))

if __name__ == "__main__":
    main()
