from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
SEGMENT = "chp-7:07_CHP-7_sec_i:l170-176"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p184-l170-176-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "cb298a9bca3a66e71ab47379df6f3219eaf43a3c2198d4bc3d2b10db269078e8",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p184-i01": "This records the sequence from Charles I's political opposition and execution to Parliament's sale of his picture collection; the political opponents and Parliament remain distinct mentions.",
    "st-chp7-p184-i02": "This records Mazarin's commission to Jabach to acquire pictures from the collection of a former rival; the rival's identity and the individual pictures remain unresolved.",
    "st-chp7-p184-i03": "This records Haskell's account that Mazarin returned to power by 1653 and found most, not all, of his paintings had survived earlier threats.",
    "st-chp7-p184-i04": "This records the inventory used to assess Mazarin's collecting and patronage over the preceding twenty years; it remains distinct from the separately cited 1661 inventory.",
    "st-chp7-p184-i05": "This records Haskell's approximate count of some 500 pictures owned by Mazarin and preserves the stated exception and artist-familiarity limits.",
    "st-chp7-p184-i06": "This records the comparative representation of seventeenth-century painters in Mazarin's collection, retaining the named artists and the unnamed comparison group.",
    "st-chp7-p184-i07": "This preserves Haskell's assessment of Mazarin's continuing taste and limited attention to later or non-Roman/Bolognese painting; almost no remains a qualified claim.",
    "st-chp7-p184-i08": "This records Haskell's claim that Mazarin did not change his collecting position after resuming collecting; it does not generalize to every individual work.",
    "st-chp7-p184-i09": "This records the single stated exception among works Mazarin acquired from 1653 to 1661, while keeping acquisition date separate from creation date.",
    "st-chp7-p184-i10": "This records Haskell's claim that many gallery pictures were gifts from friends and clients, limiting what their quality and subject matter can show about Mazarin's own taste.",
    "st-chp7-p184-i11": "This records Haskell's generalization about Mazarin's direct commissions and preserves nearly always and the profane/even erotic gradation.",
    "st-chp7-p184-i12": "This records the enemies' accusation about Mazarin's use of lascivious images and Haskell's qualified assessment using Titian and Correggio as examples.",
    "st-chp7-p184-i13": "This records Haskell's proposed comparison between Mazarin's taste and that of his contemporary La Vrillière; it is a method suggestion, not a claim of equivalence.",
    "st-chp7-p184-i14": "This records Brienne's comparative preference with the stated Correggio and Titian exceptions; the four La Vrillière paintings remain unidentified as individual works.",
    "st-chp7-p184-i15": "This records La Vrillière's palace, its architect, and the paintings kept there by artists also represented in Mazarin's apartments; the palace remains unnamed.",
    "st-chp7-p184-i16": "This records Haskell's contrast between La Vrillière's heroic antique themes and the mythological taste discussed immediately before; the quoted country-taste view remains attributed.",
    "st-chp7-p184-i17": "This records La Vrillière's acquisition of Reni's The Rape of Helen and the preceding purchase by Marie de Medici; the sentence closes with 'earlier' at p.185 L206.",
    "st-chp7-p184-q01": "This closes the p.183 sentence about Mazarin's political reversals and threatened collection dispersal, adding the contrast with vital new purchases without identifying individual purchases.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p184-i01": "The statement combines Charles I's unnamed opponents with the later sale of a collection-like picture gallery; Parliament and the opponents remain in mentions, and the gallery candidate has no settled taxonomy type.",
    "st-chp7-p184-i02": "The former rival is not named in this sentence and the pictures purchased from that collection are not individually identified.",
    "st-chp7-p184-i06": "The comparison group is unnamed and its membership is not enumerated; the source names only examples of artists represented.",
    "st-chp7-p184-i08": "The position or taste Mazarin did not modify is described through the prior context rather than represented by a separate entity candidate.",
    "st-chp7-p184-i14": "The four preferred La Vrillière pictures and the three Correggio works are not identified individually; Titian's Venus is likewise unspecified.",
    "st-chp7-p184-i15": "The palace is not named; artists and paintings in the comparison are retained as mentions rather than expanded into an inventory.",
    "st-chp7-p184-i17": "The sentence contains two acquisition relations for the same work; the main endpoints are La Vrillière and the painting, while Marie de Medici's prior purchase is retained as a separate mentioned relation for downstream review.",
    "st-chp7-p184-q01": "The phrase 'vital new purchases' does not identify the works or their number.",
}

ENDPOINT_FIXES = {
    "st-chp7-p184-i01": {"object": ("cand-0654", "cand-6812")},
    "st-chp7-p184-i06": {"object": ("cand-1258", "cand-6831")},
    "st-chp7-p184-i12": {"object": ("cand-2630", "cand-1588")},
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.184 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (169, "[Page 184]"),
        (170, "Charles I in England was being faced"),
        (171, "By 1653 Mazarin"),
        (172, "Perhaps the best way of estimating Mazarin"),
        (174, "Some time before 1635 he acquired a large and famous picture"),
        (205, "earlier. He followed this with a commission to Guercino"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.184 source-line guards failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES)
    if unset != expected_targets or len(unset) != 18:
        raise SystemExit(f"p.184 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 171 or end > 176 or start > end:
            raise SystemExit(f"invalid p.184 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")
    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (old, new) in changes.items():
            if row.get(f"{field}_candidate_id") != old:
                raise SystemExit(f"unexpected {field} endpoint for {sid}; review before applying")
            if new not in candidate_ids:
                raise SystemExit(f"replacement candidate missing for {sid}: {new}")

    if "cand-0654" not in (by_id["st-chp7-p184-i01"].get("qualifiers") or {}).get("mentioned_candidate_ids", []):
        raise SystemExit("Charles I duplicate-index mention changed; review before applying")
    if "cand-1588" in (by_id["st-chp7-p184-i12"].get("qualifiers") or {}).get("mentioned_candidate_ids", []):
        raise SystemExit("Mazarin is already in the p.184-i12 mention list; review before applying")
    prior = by_id["st-chp7-p183-i19"].get("qualifiers") or {}
    if prior.get("continuation_resolved_by_statement_id") != "st-chp7-p184-q01":
        raise SystemExit("p.183 continuation link changed; review before applying")

    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (_, new) in changes.items():
            row[f"{field}_candidate_id"] = new
    q = by_id["st-chp7-p184-i01"].setdefault("qualifiers", {})
    q["mentioned_candidate_ids"] = [cid for cid in q.get("mentioned_candidate_ids", []) if cid != "cand-0654"]
    q = by_id["st-chp7-p184-i12"].setdefault("qualifiers", {})
    q["mentioned_candidate_ids"] = ["cand-1588"] + q.get("mentioned_candidate_ids", [])
    for sid, note in TRUE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]

    quote_closure = by_id["st-chp7-p184-q01"].setdefault("qualifiers", {})
    quote_closure["continuation_of_statement_id"] = "st-chp7-p183-i19"
    quote_closure["continuation_from_segment_id"] = "chp-7:07_CHP-7_sec_i:l160-168"
    quote_closure["continuation_status"] = "closed"
    work_closure = by_id["st-chp7-p184-i17"].setdefault("qualifiers", {})
    work_closure["continuation_to_segment_id"] = "chp-7:07_CHP-7_sec_i:l205-213"
    work_closure["continuation_source_line"] = 206
    work_closure["continuation_status"] = "closed"
    work_closure["continuation_fragment"] = "earlier."
    work_closure["continuation_resolved_by_segment_id"] = "chp-7:07_CHP-7_sec_i:l205-213"
    work_closure["continuation_resolved_source_line"] = 206

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified": len(unset),
        "relation_candidate_true": len(TRUE_NOTES),
        "relation_candidate_false": 0,
        "unset_in_segment": 0,
        "endpoint_corrections": [
            f"{sid} {field}_candidate_id {old!r} -> {new!r}"
            for sid, changes in ENDPOINT_FIXES.items()
            for field, (old, new) in changes.items()
            if old != new
        ],
        "mention_corrections": [
            "st-chp7-p184-i01 removed duplicate Charles I candidate cand-0654",
            "st-chp7-p184-i12 added Mazarin candidate cand-1588",
        ],
        "continuation_links": [
            "st-chp7-p183-i19 -> st-chp7-p184-q01",
            "st-chp7-p184-i17 -> p.185 L206 ('earlier.')",
        ],
        "before_sha256": digest(raw[STATEMENTS]),
        "after_sha256": digest(result),
    }, ensure_ascii=True))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
