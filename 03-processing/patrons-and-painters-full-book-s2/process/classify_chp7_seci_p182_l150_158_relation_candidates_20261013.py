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
SEGMENT = "chp-7:07_CHP-7_sec_i:l150-158"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p182-l150-158-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "066c33b936697f6c7e632016f6c528d9adecabe79b0a99d02778e27ab992a9cf",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p182-i01": "This records Haskell's assessment that Mazarin's preference for the Metamorphoses suited Romanelli's artistic strengths; the judgment remains attributed.",
    "st-chp7-p182-i02": "This records Haskell's comparison of Romanelli's relative ease with Arcadian subjects and martial scenes; the listed works remain examples rather than an exhaustive corpus.",
    "st-chp7-p182-i03": "This preserves Haskell's claim that Mazarin's nominal dependence on Louis XIV and Anne of Austria made glorification inappropriate; it does not infer a constitutional status beyond the wording.",
    "st-chp7-p182-i04": "This records Haskell's architectural assessment that the narrow gallery vault was poorly suited to a unified fresco of the Palazzo Barberini kind; no specific comparison fresco is identified.",
    "st-chp7-p182-i05": "This records Romanelli dividing the gallery into framed compartments of several shapes; it does not infer a count of individual paintings.",
    "st-chp7-p182-i07": "This records Haskell's interpretation that Romanelli's gallery frescoes helped shape French taste against more exuberant Italian Baroque work.",
    "st-chp7-p182-i08": "This preserves Haskell's claim that Mazarin's early rule was important for the diffusion of Italian art.",
    "st-chp7-p182-i09": "This records Haskell's broad account of Italian cultural forms and artworks arriving in Paris; the list is illustrative, not an inventory.",
    "st-chp7-p182-i10": "This records Giacomo Torelli being sent to Paris by the Duke of Parma in 1645 after working for that duke; the duke's personal identity is not supplied.",
    "st-chp7-p182-i11": "This records Haskell's claim that Torelli's decors and techniques attracted more attention than the operas for which they were designed; the individual decors and audience are not identified.",
    "st-chp7-p182-i12": "This records Grimaldi's 1648 arrival to complete the decoration of Mazarin's gallery by painting landscapes in window niches and embrasures.",
    "st-chp7-p182-i13": "This records unnamed Italian potentates sending pictures to Mazarin in order to secure his favour; the collective remains unenumerated.",
    "st-chp7-p182-i14": "This records Bentivoglio commissioning a Carità Romana by Guercino for Mazarin in 1639; the commission and intended recipient remain distinct from direct acquisition by Mazarin.",
    "st-chp7-p182-i15": "This records Mazarin acquiring a St Peter painting directly from Guercino; the exact work identity remains at the source's indexed description.",
    "st-chp7-p182-i16": "This records Mazarin acquiring an unidentified genre picture of a girl with a basket of fruit directly from Guercino.",
    "st-chp7-p182-i17": "This records Mazarin acquiring Guercino's Venus mourning over the Death of Adonis; the indexed work remains distinct from same-subject works by others.",
    "st-chp7-p182-i18": "This records Mazarin commissioning a landscape with the Flight into Egypt from Claude in 1647; the commission remains distinct from other Claude works.",
    "st-chp7-p182-i19": "This records Haskell's claim that Romanelli's and Grimaldi's arrivals did not satisfy Mazarin's broader ambition to bring Italian artists to Paris.",
    "st-chp7-p182-i20": "This records Mazarin personally writing to Algardi in 1648 and making generous offers to reverse an earlier refusal dated approximately six years before.",
    "st-chp7-p182-i21": "This records Haskell's account that Algardi nearly departed for France before papal policy intervened; the policy and its agent remain unspecified.",
    "st-chp7-p182-i22": "This records Haskell's comparison of Algardi's position in the Pamfili court with Bernini's earlier position in the Barberini court.",
    "st-chp7-p182-i23": "This records Haskell's account that Innocent X and his nephew would not allow their principal artist Algardi to leave Rome; the nephew remains unidentified.",
    "st-chp7-p182-i24": "This records the opening of a quoted account of offers and promises made to Algardi; the quote continues on p.183 and is not treated as a complete transaction here.",
}

FALSE_NOTES = {
    "st-chp7-p182-i06": "This is Haskell's aesthetic evaluation of the gallery figures, without a separate relation between represented entities.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p182-i02": "The comparison covers several erotic/Arcadian examples and a martial example; no single work endpoint captures the general assessment.",
    "st-chp7-p182-i03": "The statement refers to both Louis XIV and Regent Anne of Austria; the scalar endpoint captures only the king, and the political dependence remains source-qualified.",
    "st-chp7-p182-i04": "The gallery is identified, but the type of unified fresco is not an entity candidate and no specific Palazzo Barberini fresco is named.",
    "st-chp7-p182-i08": "The source gives no bounded dates for the 'early years' or discrete measure of Italian art diffusion.",
    "st-chp7-p182-i09": "The arrivals comprise an unquantified mix of performances, fashions, artworks and crafts; the source provides no item-level inventory.",
    "st-chp7-p182-i11": "The designs and techniques are not identified as separate work candidates, and the audience whose attention changed is unnamed.",
    "st-chp7-p182-i13": "The potentates are unnamed and their picture gifts are not individually identified.",
    "st-chp7-p182-i19": "The source does not define how much larger ambition remained unsatisfied or enumerate the Italian artists included in it.",
    "st-chp7-p182-i21": "Papal policy is unnamed and the exact mechanism that stopped Algardi's departure is not described.",
    "st-chp7-p182-i23": "The nephew is unidentified; the statement's scalar subject is Innocent X while the source uses a collective 'they'.",
    "st-chp7-p182-i24": "The offerors are Innocent X and an unnamed nephew, and the quoted terms and consequences continue in the next segment.",
}

ENDPOINT_FIXES = {
    "st-chp7-p182-i02": {"object": ("cand-2210", None)},
    "st-chp7-p182-i04": {"object": ("cand-4957", None)},
    "st-chp7-p182-i11": {"subject": ("cand-2647", None)},
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.182 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (149, "[Page 182]"),
        (150, "a wise one in view of the nature of Romanelli’s talents"),
        (151, "Romulus and Remus (Plate 26b)"),
        (151, "Glorification of Mazarin was out of the question"),
        (152, "Romanelli divided the area into a number of oval"),
        (153, "These early years of Mazarin’s rule were important"),
        (157, "However mean Innocent X and his nephew might be"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.182 source-line guards failed")

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
        raise SystemExit(f"p.182 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 151 or end > 158 or start > end:
            raise SystemExit(f"invalid p.182 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")
    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (old, new) in changes.items():
            if row.get(f"{field}_candidate_id") != old:
                raise SystemExit(f"unexpected {field} endpoint for {sid}; review before applying")
            if new and new not in candidate_ids:
                raise SystemExit(f"replacement candidate missing for {sid}: {new}")

    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (_, new) in changes.items():
            row[f"{field}_candidate_id"] = new
    for sid, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
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
            if old != new
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
