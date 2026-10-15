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
SEGMENT = "chp-7:07_CHP-7_sec_i:l140-148"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p181-l140-148-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "6bbfdfff2c9191de7e1f8e077d59e82ec01d85267d1c090c6c39a40befb12aaf",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p181-i03": "This records Haskell's claim that ancient lyric poetry and mythological subject matter strongly appealed to Mazarin; the appeal is attributed to other sources and is not independently verified.",
    "st-chp7-p181-i04": "This records Haskell's claim that Mazarin thereafter took no further interest in Poussin's career.",
    "st-chp7-p181-i05": "This records Brienne's reproach of Mazarin for neglecting Poussin's mature pictures; Brienne's account remains distinct from Haskell's later assessment of it.",
    "st-chp7-p181-i06": "This preserves Haskell's assessment that Brienne's description of Mazarin is generally consistent after allowing for Brienne's prejudice.",
    "st-chp7-p181-i07": "This records Brienne's description of Mazarin as a passionate enthusiast, transmitted through Haskell.",
    "st-chp7-p181-i08": "This records Brienne's description of Mazarin's ambition to acquire pictures as unscrupulous; the evaluation remains attributed.",
    "st-chp7-p181-i09": "This records Brienne's description of Mazarin as fastidious in his love of art objects and finery; the evaluation remains attributed.",
    "st-chp7-p181-i10": "This preserves Haskell's explicitly imagined scene of Mazarin discussing acquisitions and selecting their placement; it is not treated as a witnessed episode.",
    "st-chp7-p181-i11": "This records Brienne's quoted account of Mazarin's pleasure in arranging valuable objects; the listed objects remain source-attributed and no ownership beyond the quotation is inferred.",
    "st-chp7-p181-i12": "This records Haskell's connection between Mazarin's increasing duties, absence from Rome, and growing association with France.",
    "st-chp7-p181-i13": "This records Mazarin settling in Paris early in 1640.",
    "st-chp7-p181-i14": "This records Mazarin being made Cardinal at the end of the following year, 1641; the appointing authority is not named in this passage.",
    "st-chp7-p181-i17": "This preserves Haskell's causal interpretation that the deaths of Richelieu and Louis XIII enabled Mazarin to pursue artistic tastes and ambitions at an unusual scale.",
    "st-chp7-p181-i18": "This records Mazarin's early failed attempts to attract Italian artists to France while Urban VIII remained alive; failure does not imply that no Italian artists later worked for him.",
    "st-chp7-p181-i19": "This records Mazarin's failed attempt to have Bernini enlarge the palace he had acquired from Jacques Tubeuf; the acquisition and enlargement proposal remain distinct actions.",
    "st-chp7-p181-i20": "This records Mazarin's initial inability to bring leading Italian musicians to Paris, including Leonora Baroni; it does not say that all Italian musicians were excluded.",
    "st-chp7-p181-i21": "This records Mazarin's stated determination to use Italian artists of different kinds.",
    "st-chp7-p181-i22": "This records Haskell's causal claim that a change of regime in Rome made later recruitment possible; the political transition itself is not represented by the current scalar endpoints.",
    "st-chp7-p181-i23": "This records Francesco Barberini fleeing Innocent X's persecution and arriving in Paris in 1646; the persecution and journey are separate actions within one source statement.",
    "st-chp7-p181-i24": "This records Francesco Barberini placing himself under the protection of his former protégé Mazarin.",
    "st-chp7-p181-i25": "This records Romanelli experiencing neglect and hostility after returning to Rome; the agents responsible are not identified.",
    "st-chp7-p181-i26": "This records Romanelli painting the newly built upper gallery of Mazarin's palace by June; the passage does not give a precise year in this sentence.",
    "st-chp7-p181-i27": "This records Romanelli's proposal for a series of Roman histories for Mazarin's gallery; the proposal is distinct from the subject eventually selected.",
    "st-chp7-p181-i28": "This records Mazarin's preference for Ovid's Metamorphoses as a livelier subject that better suited the taste of the country, according to Haskell.",
    "st-chp7-p181-i29": "This records Haskell's interpretation that Mazarin's gallery choice was characteristic in light of his probable relations with Poussin; 'probable' remains explicit.",
}

FALSE_NOTES = {
    "st-chp7-p181-i01": "This p.181 fragment closes the stylistic-comparison statement already represented by st-chp7-p180-i35; it is linked as a continuation rather than counted as a second independent relation candidate.",
    "st-chp7-p181-i02": "This is a work-specific statement that the subject remains unresolved, not a relation between entities.",
    "st-chp7-p181-i15": "This is a dated biographical event about Richelieu, without a second entity endpoint.",
    "st-chp7-p181-i16": "This is a dated biographical event about Louis XIII, without a second entity endpoint.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p181-i03": "The two pictures and the ancient poetic or mythological source works are not all represented as resolved work candidates; the appeal claim is explicitly mediated by other sources.",
    "st-chp7-p181-i06": "This is Haskell's assessment of Brienne's account; it does not independently verify the historical characterization of Mazarin.",
    "st-chp7-p181-i10": "The imagined acquisition, its placement and the other amateurs or artists are not identified.",
    "st-chp7-p181-i12": "The statement combines absence from Rome with growing association with the French polity; it does not identify the duties or a discrete political office causing the change.",
    "st-chp7-p181-i14": "The Cardinal's office is stated, but the appointing authority or appointment instrument is not identified in this passage.",
    "st-chp7-p181-i17": "The deaths and the resulting opening for Mazarin's artistic activity are not represented as event nodes; Haskell's causal link remains interpretive.",
    "st-chp7-p181-i18": "The targeted artists are a broad group, and the source does not identify each recruitment attempt or the exact institutional action under Urban VIII.",
    "st-chp7-p181-i20": "The musicians are an unenumerated group; Baroni is the only named example, and the passage does not identify the travel arrangements.",
    "st-chp7-p181-i22": "The regime change and subsequent recruitment are not represented by event candidates; Rome is a location, not the causal endpoint.",
    "st-chp7-p181-i23": "The source combines flight from persecution and arrival in Paris; it does not detail the individual acts or legal mechanism of persecution.",
    "st-chp7-p181-i25": "The source does not identify who or what caused Romanelli's neglect and hostility; Rome is retained as location context.",
    "st-chp7-p181-i29": "The connection to Poussin is explicitly described as probable and interpretive, not as a verified commission or formal relation.",
}

ENDPOINT_FIXES = {
    "st-chp7-p181-i01": {
        "subject": ("cand-1984", None),
        "object": ("cand-2630", None),
    },
    "st-chp7-p181-i22": {
        "subject": ("cand-1588", None),
        "object": ("cand-4490", None),
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
    parser = argparse.ArgumentParser(description="Classify p.181 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (139, "[Page 181]"),
        (140, "young Titian, to which they owe so much"),
        (141, "Poussin’s career and when, many years later"),
        (142, "As yet this rich life of the senses was only just opening up to him"),
        (143, "It has already been pointed out that Mazarin’s earliest attempts"),
        (144, "Italian musicians, including his former mistress Leonora Baroni"),
        (145, "Back in Rome his favourite painter Giovan Francesco Romanelli"),
        (146, "The artist proposed a series of Roman histories"),
        (147, "Cardinal ‘showed that he preferred the Metamorphoses"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.181 source-line guards failed")

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
    if unset != expected_targets or len(unset) != 29:
        raise SystemExit(f"p.181 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 141 or end > 148 or start > end:
            raise SystemExit(f"invalid p.181 source anchor: {sid} {start}-{end}")
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

    prior = by_id["st-chp7-p180-i35"].get("qualifiers") or {}
    if prior.get("relation_candidate") is not True:
        raise SystemExit("p.180 continuation statement is not classified as expected")
    if prior.get("continuation_resolved_by_statement_id") != "st-chp7-p181-i03":
        raise SystemExit("unexpected p.180 continuation target; review before applying")

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
    by_id["st-chp7-p181-i01"].setdefault("qualifiers", {})["continuation_from_statement_id"] = "st-chp7-p180-i35"
    by_id["st-chp7-p180-i35"].setdefault("qualifiers", {})["continuation_resolved_by_statement_id"] = "st-chp7-p181-i01"

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
        "continuation_link": "st-chp7-p180-i35 <-> st-chp7-p181-i01",
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
