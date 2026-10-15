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
SEGMENT = "chp-7:07_CHP-7_sec_i:l102-111"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p178-l102-111-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "47650e17ec1ca31da5cd205d28f7626be2507ff9de1edc09fad6f4e82a65297a",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p178-i01": "This records the condition that Guercino settle at Charles I's court and closes the p.177 continuation; acceptance is not claimed.",
    "st-chp7-p178-i02": "This preserves the reported refusal and the reasons attributed to Guercino in a source Haskell introduces as hearsay; the Mahon note qualifies the surrounding narrative.",
    "st-chp7-p178-i03": "This records Charles I's handwritten invitation to Albani with Haskell's uncertainty about timing and the source's spelling variation.",
    "st-chp7-p178-i04": "This records Albani declining Charles I's offer while preserving Haskell's explicit uncertainty about his motive.",
    "st-chp7-p178-i05": "This records Charles I's wish to bring Pietro Tacca to London and the Grand Duke of Tuscany's refusal to authorize the visit; it does not claim a formal commission or completed work.",
    "st-chp7-p178-i06": "This records Charles I obtaining Orazio Gentileschi after continued effort, with Haskell's comparison to the stature of the artists originally hoped for retained as evaluation.",
    "st-chp7-p178-i07": "This records Charles I obtaining Francesco Fanelli as the sculptor in the same recruitment outcome; the quality comparison remains Haskell's evaluation.",
    "st-chp7-p178-i08": "This records Gentileschi's earlier work in Paris and his probable recruitment to England near the end of 1625; the inducing agent is not identified.",
    "st-chp7-p178-i09": "This records Haskell's account of Gentileschi shedding Caravaggist influence and developing a lighter, more decorative style while in Paris; no single cause is asserted.",
    "st-chp7-p178-i10": "This records Gentileschi's welcome by Charles I and the Duke of Buckingham in England and Haskell's account that the stylistic development continued there.",
    "st-chp7-p178-i11": "This records a relation between Gentileschi's Biblical easel-picture approach and likely Protestant reception, retaining Haskell's assessment rather than treating it as documented viewer response.",
    "st-chp7-p178-i12": "This records the contrast between Gentileschi's politically harmless commissions and Stuart propaganda entrusted to Rubens; judgments about relative ability and currency remain Haskell's.",
    "st-chp7-p178-i13": "This records Gentileschi painting canvases of the Muses and Virtues for the ceiling of the Queen's house, which Haskell attributes to Inigo Jones; the house location is unspecified.",
    "st-chp7-p178-i14": "This records Haskell's stylistic comparison between the Muses and Virtues canvases and Veronese with the Libreria in Venice; it does not claim direct copying of a specific work.",
    "st-chp7-p178-i16": "This preserves Haskell's comparison that Rubens surpassed Gentileschi in Paris as in England alongside the author's characterization of Gentileschi's condition.",
    "st-chp7-p178-i17": "This records Charles I's continued interest in an Italian sculptor and his recruitment of Fanelli around 1635; the date remains approximate.",
    "st-chp7-p178-i18": "This records Fanelli's Florentine background and source-described formation in the traditions of Giambologna, Tacca and Francavilla; no formal apprenticeship is inferred.",
    "st-chp7-p178-i19": "This records the scope and subjects of Fanelli's English bronze work; individual bronzes remain unidentified.",
    "st-chp7-p178-i20": "This records Haskell's interpretation that the horse and portrait subjects of Fanelli's bronzes reflected the Duke of Newcastle's interests; the works are the subject endpoint and the patron is the object endpoint.",
    "st-chp7-p178-i21": "This records the Duke of Newcastle's governorship of Charles, Prince of Wales, and his stated enthusiasm for riding; the Prince is identified as the future Charles II without adding dates.",
    "st-chp7-p178-i22": "This records Fanelli drawing on sacred and profane literature for portrayals made for the Duke of Newcastle and his circle; no individual source text or horse portrayal is named.",
    "st-chp7-p178-i23": "This records Fanelli making a bust of the young Prince of Wales, using the indexed work candidate rather than treating the bust as the artist.",
    "st-chp7-p178-i24": "This records Fanelli making a separate bust of Charles I; the work's distinction and the strained expression and lifeless eyes remain Haskell's evaluations.",
}

FALSE_NOTES = {
    "st-chp7-p178-i15": "This records wear and Haskell's aesthetic judgment about the canvases without asserting a discrete relation between represented entities.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p178-i05": "The statement combines Charles I's wish to recruit Tacca with the Grand Duke of Tuscany's separate refusal to authorize the visit; the scalar subject-object pair captures the recruitment aim, while the refusal actor remains in mentions.",
    "st-chp7-p178-i10": "The source names both Charles I and the Duke of Buckingham as welcoming Gentileschi but does not say which patron initiated the welcome.",
    "st-chp7-p178-i11": "The specific easel pictures, their audiences and any actual Protestant responses are not identified.",
    "st-chp7-p178-i13": "The Queen's house and individual canvases are not identified beyond the source-bounded group and its named builder.",
    "st-chp7-p178-i14": "The Libreria is not represented by a resolved work or architectural candidate in this statement; the stylistic reference remains at the source's named artist and place level.",
    "st-chp7-p178-i18": "The source names three artistic traditions but does not identify Fanelli's formal teachers or training institutions.",
    "st-chp7-p178-i22": "The Duke's circle is unnamed and no specific literary sources or individual horse portrayals are identified.",
}

ENDPOINT_FIXES = {
    "st-chp7-p178-i20": {
        "subject": ("cand-1737", "cand-6745"),
        "object": ("cand-0989", "cand-1737"),
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.178 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (101, "[Page 178]"),
        (102, "settle at his court"),
        (103, "Nor was"),
        (105, "Orazio Gentileschi had already been working for some time in Paris"),
        (109, "Charles I was just as keen to employ an Italian sculptor"),
        (110, "The Duke was governor of Charles, Prince of Wales"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.178 source-line guards failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES) | set(FALSE_NOTES)
    if unset != expected_targets or len(unset) != 24:
        raise SystemExit(f"p.178 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 102 or end > 111 or start > end:
            raise SystemExit(f"invalid p.178 source anchor: {sid} {start}-{end}")
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

    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (_, new) in changes.items():
            row[f"{field}_candidate_id"] = new
    for mapping in (TRUE_NOTES, FALSE_NOTES):
        for sid, note in mapping.items():
            q = by_id[sid].setdefault("qualifiers", {})
            q["relation_candidate"] = sid in TRUE_NOTES
            q["relation_candidate_note"] = note
            if sid in OPEN_ENDPOINTS:
                q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified": len(unset),
        "relation_candidate_true": len(TRUE_NOTES),
        "relation_candidate_false": len(FALSE_NOTES),
        "unset_in_segment": 0,
        "endpoint_corrections": [
            f"{sid} {field}_candidate_id {old!r} -> {new!r}"
            for sid, changes in ENDPOINT_FIXES.items()
            for field, (old, new) in changes.items()
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
