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
SEGMENT = "chp-7:07_CHP-7_sec_i:l205-213"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p185-l205-213-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "a20f84700c7214b79651aae41b89a9e258508e80ffa45ee87619543eb8796d8b",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p185-i01": "This records Mazarin commissioning Guercino's Scene from the Life of Cato; the named work is the endpoint and Guercino remains its creator mention.",
    "st-chp7-p185-i02": "This records Mazarin ordering the Camillus painting from Poussin in 1637; the index sub-entry identifies the work and the artist remains distinct.",
    "st-chp7-p185-i03": "This records Haskell's account of the episode depicted and its derivation from Livy; the episode is not independently verified here.",
    "st-chp7-p185-i05": "This records La Vrillière adding a group of paintings in the 1640s and preserves the listed artists and titles without expanding the set.",
    "st-chp7-p185-i06": "This records Haskell's attribution of The War between the Romans and the Sabines to Guercino; it is a source attribution, not independent authorship verification.",
    "st-chp7-p185-i07": "This records Haskell's attribution of Coriolanus and his Mother to Guercino; the mother's identity is not supplied.",
    "st-chp7-p185-i08": "This records Haskell's attribution of Caesar restoring Cleopatra to her usurped Throne to Pietro da Cortona; the index sub-entry is retained as the work candidate despite its unresolved type suggestion.",
    "st-chp7-p185-i09": "This records Haskell's attribution of The Sibyl announcing the Birth of Christ to Augustus to Pietro da Cortona; the Sibyl is not identified more specifically.",
    "st-chp7-p185-i10": "This records Haskell's attribution of The Finding of Romulus and Remus to Pietro da Cortona; the title figures remain distinct from the artist.",
    "st-chp7-p185-i11": "This records Haskell's attribution of The Death of Cleopatra to Alessandro Turchi; the index sub-entry is the work endpoint.",
    "st-chp7-p185-i12": "This records the later completion of La Vrillière's painting series with Maratta's Augustus closing the Temple of Janus; some years later remains approximate.",
    "st-chp7-p185-i13": "This records Haskell's interpretation that the listed ten paintings show a difference in taste between La Vrillière and Mazarin; ten is preserved as the author's count.",
    "st-chp7-p185-i14": "This preserves Haskell's contrast between French dramatic culture and Italian opera and ballet as an attributed cultural comparison.",
    "st-chp7-p185-i15": "This records Haskell's qualified claim that the two patrons shared ideals in one respect and continued to seek artists in Italy.",
    "st-chp7-p185-i16": "This records Haskell's claim that a distinct group of patrons, mostly bankers, lawyers, and merchants, began rejecting contemporary Italian painting.",
    "st-chp7-p185-i17": "This records the same emerging patron group beginning to develop what was later considered a more specifically French taste for reticence and classicism.",
    "st-chp7-p185-i18": "This records Haskell's claim that reticence and classicism appealed little to La Vrillière and Mazarin; neither quality refers to a general rejection of French art.",
    "st-chp7-p185-i19": "This records Mazarin's return to Paris in 1653 while the sale of Charles I's pictures in London continued; no purchase date is inferred from simultaneity.",
    "st-chp7-p185-i20": "This records Mazarin's purchase of Correggio's Jupiter and Antiope through his ambassador M. de Bordeaux; the cited page is not independently read.",
    "st-chp7-p185-i21": "This records Mazarin's purchase of Titian's Venus of the Pardo through the same ambassador; title alignment with the index remains for S3.",
    "st-chp7-p185-i22": "This records Mazarin acquiring a group of Van Dyck paintings that includes The Children of Charles I; the other group members are not inferred.",
    "st-chp7-p185-i23": "This preserves Haskell's tentative explanation that satisfaction with the acquisitions may have contributed to reduced collecting and patronage; much decreased does not mean stopped.",
    "st-chp7-p185-i24": "This records Romanelli's 1655 return to Paris and work for the Queen Mother at the Louvre; the title is not identified with a named person by inference.",
    "st-chp7-p185-i25": "This records Romanelli being encouraged to paint Roman histories Mazarin had rejected nine years earlier; the encourager is not named.",
    "st-chp7-p185-i26": "This records Vigarani's 1659 theatre project moving from Mazarin's palace to the Tuileries after insufficient space was found; completion is not asserted.",
    "st-chp7-p185-i27": "This records Mazarin promoting the enterprises while they were executed more in the monarch's name; the Louis XIV comparison remains Haskell's foreshadowing analogy.",
    "st-chp7-p185-i28": "This preserves Haskell's tentative suggestion that Fronde hostility may have affected Mazarin's later activity; neither timing nor a specific causal mechanism is supplied.",
    "st-chp7-p185-i29": "This records Mazarin's continuing acquisition of Italian brocades and fabrics and preserves Haskell's evaluative phrasing.",
    "st-chp7-p185-i30": "This records Mazarin's final visit to his pictures one month before death and opens Brienne's quoted memoir, which continues on p.186.",
}

FALSE_NOTES = {
    "st-chp7-p185-i04": "This is Haskell's size and stylistic evaluation of one painting, without a separate relation between represented entities.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p185-i08": "The index sub-entry names a specific painting, but its candidate row is still suggested_type=person; the work/person boundary needs S3 resolution.",
    "st-chp7-p185-i09": "The index sub-entry names the painting while its candidate row is still suggested_type=person; the work/person boundary needs S3 resolution, and the Sibyl is unnamed.",
    "st-chp7-p185-i10": "The index sub-entry names the painting while its candidate row is still suggested_type=person; the work/person boundary needs S3 resolution.",
    "st-chp7-p185-i19": "The sentence describes an ongoing sale but the endpoint candidate represents the picture collection rather than a separately identified sale event; London remains the stated location.",
    "st-chp7-p185-i22": "The source identifies one painting within a group of Van Dyck works but leaves the group's other members unspecified.",
    "st-chp7-p185-i23": "The cause is Haskell's tentative inference about satisfaction with the haul; no separate satisfaction event is identified.",
    "st-chp7-p185-i24": "The source uses the title Queen Mother; identity is left unresolved rather than aligned to Anne of Austria.",
    "st-chp7-p185-i25": "The source does not identify who encouraged Romanelli; the histories are an unidentified series and the prior rejection is attributed to Mazarin.",
    "st-chp7-p185-i26": "The theatre project moved sites after a space constraint, but the source does not say whether a theatre was completed at the Tuileries.",
    "st-chp7-p185-i28": "The suggested effect is unquantified and remains explicitly tentative; the statement does not identify a particular activity or mechanism.",
    "st-chp7-p185-i30": "The quoted account continues on p.186; this statement records only the opening and attribution of the memoir passage.",
}

ENDPOINT_FIXES = {
    "st-chp7-p185-i19": {"object": ("cand-0654", "cand-6812")},
    "st-chp7-p185-i28": {
        "subject": ("cand-1588", "cand-6860"),
        "object": ("cand-6860", "cand-1588"),
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
    parser = argparse.ArgumentParser(description="Classify p.185 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (204, "[Page 185]"),
        (205, "earlier. He followed this with a commission to Guercino"),
        (206, "The subject was chosen from Livy"),
        (206, "In the 1640s La Vrilliere added to these a series of paintings"),
        (209, "When Mazarin returned to Paris in 1653"),
        (210, "Gaspare Vigarani was summoned from Mantua in 1659"),
        (211, "Perhaps the hostility of the Fronde"),
        (212, "Italian precious brocades and stuffs"),
        (212, "A month before his death he paid a last visit to his pictures"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.185 source-line guards failed")

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
    if unset != expected_targets or len(unset) != 30:
        raise SystemExit(f"p.185 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 206 or end > 213 or start > end:
            raise SystemExit(f"invalid p.185 source anchor: {sid} {start}-{end}")
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

    sale_mentions = by_id["st-chp7-p185-i19"].get("qualifiers", {}).get("mentioned_candidate_ids", [])
    if "cand-0654" not in sale_mentions or "cand-6812" in sale_mentions:
        raise SystemExit("p.185 sale endpoint mentions changed; review before applying")
    prior = by_id["st-chp7-p184-i17"].get("qualifiers") or {}
    if prior.get("continuation_source_line") != 206 or prior.get("continuation_status") != "closed":
        raise SystemExit("p.184 cross-page closure changed; review before applying")
    quote_end = by_id["st-chp7-p186-q01"].get("qualifiers") or {}
    if by_id["st-chp7-p186-q01"].get("segment_id") != "chp-7:07_CHP-7_sec_i:l215-222" or quote_end.get("source_line_start") != 216 or quote_end.get("source_line_end") != 218:
        raise SystemExit("p.186 quoted memoir closure changed; review before applying")

    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (_, new) in changes.items():
            row[f"{field}_candidate_id"] = new
    sale_q = by_id["st-chp7-p185-i19"].setdefault("qualifiers", {})
    sale_q["mentioned_candidate_ids"] = [cid for cid in sale_q.get("mentioned_candidate_ids", []) if cid != "cand-0654"]
    sale_q["mentioned_candidate_ids"].append("cand-6812")
    for sid, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = sid in TRUE_NOTES
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]

    quote_start = by_id["st-chp7-p185-i30"].setdefault("qualifiers", {})
    quote_start["continuation_to_segment_id"] = "chp-7:07_CHP-7_sec_i:l215-222"
    quote_start["continuation_to_statement_id"] = "st-chp7-p186-q01"
    quote_start["continuation_status"] = "closed"
    quote_start["continuation_source_line_start"] = 216
    quote_start["continuation_source_line_end"] = 218
    quote_end["continuation_of_statement_id"] = "st-chp7-p185-i30"
    quote_end["continuation_from_segment_id"] = SEGMENT
    quote_end["continuation_status"] = "closed"

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
        "continuation_link": "st-chp7-p185-i30 -> st-chp7-p186-q01",
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
