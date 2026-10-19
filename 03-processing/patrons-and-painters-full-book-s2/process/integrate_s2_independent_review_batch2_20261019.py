from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE_CH15_I = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md"
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + ".bak-s2-independent-review-batch2-20261019"
)

OPEN_ACTOR_REASON = (
    "The preceding sentence distinguishes the Consorzio council from the whole city; "
    "the following pronoun 'they' does not isolate one of those actors. Keep the actor "
    "endpoint open rather than assigning it solely to the committee or governors."
)
ARTIST_GROUP_NOTE = (
    "The source names artists from Milan and its surroundings as a plural group commissioned "
    "for the listed works. It does not identify individual painters or assign a named painter "
    "to a particular work."
)

UPDATES: dict[str, dict[str, object]] = {
    "st-chp8-p216-governors-pleased-with-massacre": {
        "expected": {
            "subject_candidate_id": "cand-7641",
            "object_candidate_id": "cand-7653",
            "predicate": "source_says_governors_pleased_with_work",
        },
        "row": {
            "subject_candidate_id": None,
            "predicate": "positive_reaction_to_work",
        },
        "qualifiers": {
            "claim": "Haskell says the actor referred to as 'they' was pleased with Padre Massimo's Massacre of the Innocents.",
            "qualification": OPEN_ACTOR_REASON,
            "mentioned_candidate_ids": ["cand-7640", "cand-7641", "cand-7653"],
            "relation_candidate_note": "The positive reaction is explicit, but the passage does not isolate the committee, council, governors, or whole city as the actor. Preserve the open subject endpoint.",
            "open_endpoint_reason": OPEN_ACTOR_REASON,
        },
    },
    "st-chp8-p216-governors-request-massimo-leave": {
        "expected": {
            "subject_candidate_id": "cand-7640",
            "object_candidate_id": "cand-3405",
            "predicate": "requested_temporary_leave_for_massimo",
        },
        "row": {"subject_candidate_id": None},
        "qualifiers": {
            "claim": "Haskell says the actor referred to as 'they' implored the Capuchins to grant Padre Massimo temporary leave to settle in Bergamo for further painting; the request came to nothing.",
            "qualification": "The same unresolved 'they' follows the committee, council, and whole-city context. The request was unsuccessful and did not produce leave, relocation, or further work.",
            "mentioned_candidate_ids": ["cand-7640", "cand-7641", "cand-3405", "cand-1576", "cand-6208"],
            "relation_candidate_note": "The unsuccessful request is explicit, but its actor is not safely identifiable as only the committee or governors; preserve the open subject endpoint.",
            "open_endpoint_reason": OPEN_ACTOR_REASON,
        },
    },
    "st-chp8-p216-milan-artists-commissioned-killing-of-sisera": {
        "expected": {"subject_candidate_id": "cand-12367"},
        "row": {},
        "qualifiers": {
            "claim": "Haskell lists The Killing of Sisera among four works for which artists from Milan and its surroundings were commissioned; no individual painter is assigned to this work.",
            "qualification": "The artist is represented by the source-defined plural group cand-12367; individual membership and work-to-painter assignments are not supplied.",
            "relation_candidate_note": ARTIST_GROUP_NOTE,
        },
    },
    "st-chp8-p216-milan-artists-commissioned-sacrifice-of-isaac": {
        "expected": {"subject_candidate_id": "cand-12367"},
        "row": {},
        "qualifiers": {
            "claim": "Haskell lists The Sacrifice of Isaac among four works for which artists from Milan and its surroundings were commissioned; no individual painter is assigned to this work.",
            "qualification": "The artist is represented by the source-defined plural group cand-12367; individual membership and work-to-painter assignments are not supplied.",
            "relation_candidate_note": ARTIST_GROUP_NOTE,
        },
    },
    "st-chp8-p216-milan-artists-commissioned-jacobs-ladder": {
        "expected": {"subject_candidate_id": "cand-12367"},
        "row": {},
        "qualifiers": {
            "claim": "Haskell lists Jacob's Ladder among four works for which artists from Milan and its surroundings were commissioned; no individual painter is assigned to this work.",
            "qualification": "The artist is represented by the source-defined plural group cand-12367; individual membership and work-to-painter assignments are not supplied.",
            "relation_candidate_note": ARTIST_GROUP_NOTE,
        },
    },
    "st-chp8-p216-milan-artists-commissioned-murder-of-cain": {
        "expected": {"subject_candidate_id": "cand-12367"},
        "row": {},
        "qualifiers": {
            "claim": "Haskell lists The Murder of Cain among four works for which artists from Milan and its surroundings were commissioned; no individual painter is assigned to this work.",
            "qualification": "The artist is represented by the source-defined plural group cand-12367; individual membership and work-to-painter assignments are not supplied.",
            "relation_candidate_note": ARTIST_GROUP_NOTE,
        },
    },
    "st-chp15-p361-tiepolo-no-desire-to-return-to-italy": {
        "expected": {"source_line_start": 5, "source_line_end": 5},
        "row": {},
        "qualifiers": {
            "source_line_start": 4,
            "claim": "By 1764, Haskell says Tiepolo was in Spain and showed no desire to return to Italy.",
        },
        "quote_from_source_lines_4_5": True,
        "ocr_corrections": [
            {"source_line": 4, "ocr": "Y 1764", "print": "By 1764", "basis": "CHP-15.pdf physical page 1."},
            {"source_line": 5, "ocr": "Bnearly", "print": "nearly", "basis": "CHP-15.pdf physical page 1."},
        ],
    },
    "st-chp15-p361-pittoni-neglect-with-declining-powers": {
        "expected": {"source_line_start": 5, "source_line_end": 5},
        "row": {},
        "qualifiers": {
            "source_line_start": 4,
            "claim": "By 1764, Haskell says Pittoni was increasingly neglected as his powers declined.",
        },
        "quote_from_source_lines_4_5": True,
        "ocr_corrections": [
            {"source_line": 4, "ocr": "Y 1764", "print": "By 1764", "basis": "CHP-15.pdf physical page 1."},
            {"source_line": 5, "ocr": "Bnearly", "print": "nearly", "basis": "CHP-15.pdf physical page 1."},
        ],
    },
    "st-chp15-p371-rosenberg-portrait-depicts-rosenberg": {
        "expected": {"source_line_start": 81, "source_line_end": 81},
        "row": {},
        "qualifiers": {"source_line_start": 80},
        "quote_from_source_lines_80_81": True,
    },
    "st-chp15-p371-rembrandt-prints-influenced-novelli": {
        "expected": {"mentioned_candidate_ids": ["cand-10580", "cand-1756"]},
        "row": {},
        "qualifiers": {"mentioned_candidate_ids": ["cand-10580", "cand-1752", "cand-1756"]},
    },
}

NEW_STATEMENT = {
    "statement_id": "st-chp15-p371-de-non-principal-pupil-novelli",
    "segment_id": "chp-15:15_CHP-15_sec_ii:l69-83",
    "subject_candidate_id": "cand-1752",
    "object_candidate_id": "cand-1756",
    "predicate": "had_as_principal_pupil",
    "qualifiers": {
        "source_line_start": 77,
        "source_line_end": 78,
        "printed_page": 371,
        "pdf_physical_page": 11,
        "claim": "Haskell identifies Francesco Novelli as Dominique De Non's principal pupil.",
        "speaker": "Haskell",
        "text_layer": "authorial report",
        "qualification": "This records Haskell's description; no independent biographical source was consulted in this review.",
        "mentioned_candidate_ids": ["cand-1752", "cand-1756"],
        "relation_candidate": True,
        "relation_candidate_note": "The p.371 sentence names De Non as the person whose Rembrandt prints affected the style of his principal pupil, Francesco Novelli.",
    },
    "original_quote": "De Non settled in Venice for about five years in the early ’nineties, and led a busy life as a controversial but highly admired engraver and also as a collector.\nHe bought a large proportion of Zanetti’s prints, including the Rembrandts, which had a profound effect on his own style and that of his principal pupil Francesco Novelli.",
    "origin": "book",
    "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare(before: bytes) -> tuple[bytes, list[str]]:
    source_lines = SOURCE_CH15_I.read_text(encoding="utf-8-sig").splitlines()
    expected_quote_4_5 = "\n".join(source_lines[3:5])
    source_lines_ii = (ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md").read_text(encoding="utf-8-sig").splitlines()
    expected_quote_80_81 = "\n".join(source_lines_ii[79:81])
    rows = before.splitlines(keepends=True)
    bom = b"\xef\xbb\xbf" if before.startswith(b"\xef\xbb\xbf") else b""
    if bom:
        rows = before[len(bom):].splitlines(keepends=True)
    by_id: dict[str, tuple[int, dict[str, object]]] = {}
    for i, raw in enumerate(rows):
        if not raw.strip():
            continue
        row = json.loads(raw.rstrip(b"\r\n").decode("utf-8"))
        if row["statement_id"] in by_id:
            raise SystemExit(f"duplicate statement id: {row['statement_id']}")
        by_id[row["statement_id"]] = (i, row)

    changed: list[str] = []
    for statement_id, fix in UPDATES.items():
        if statement_id not in by_id:
            raise SystemExit(f"missing statement: {statement_id}")
        i, row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        for key, value in fix["expected"].items():
            if key in {"source_line_start", "source_line_end", "mentioned_candidate_ids"}:
                actual = q.get(key)
            else:
                actual = row.get(key)
            if actual != value:
                raise SystemExit(f"evidence guard failed: {statement_id}.{key}: {actual!r}")
        row.update(fix["row"])
        for key, value in fix["qualifiers"].items():
            q[key] = value
        if "quote_from_source_lines_4_5" in fix:
            row["original_quote"] = expected_quote_4_5
        if "quote_from_source_lines_80_81" in fix:
            row["original_quote"] = expected_quote_80_81
        if "ocr_corrections" in fix:
            prior = list(q.get("ocr_corrections") or [])
            prior.extend(fix["ocr_corrections"])
            q["ocr_corrections"] = prior
        row["qualifiers"] = q
        ending = b"\r\n" if rows[i].endswith(b"\r\n") else b"\n"
        rows[i] = json.dumps(row, ensure_ascii=False).encode("utf-8") + ending
        by_id[statement_id] = (i, row)
        changed.append(statement_id)

    if NEW_STATEMENT["statement_id"] in by_id:
        raise SystemExit(f"new statement already exists: {NEW_STATEMENT['statement_id']}")
    # The quoted text must be present verbatim in the source lines cited by the new statement.
    if not all(any(piece in line for line in source_lines_ii[76:78]) for piece in ["De Non settled in Venice", "He bought a large proportion"]):
        raise SystemExit("source guard failed for the new De Non–Novelli pupil statement")
    ending = b"\r\n" if rows and rows[-1].endswith(b"\r\n") else b"\n"
    rows.append(json.dumps(NEW_STATEMENT, ensure_ascii=False).encode("utf-8") + ending)
    changed.append(NEW_STATEMENT["statement_id"])
    return bom + b"".join(rows), changed


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    temp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Integrate guarded S2 independent-review corrections.")
    parser.add_argument("--apply", action="store_true", help="apply changes and retain a recovery copy")
    args = parser.parse_args()
    before = STATEMENTS.read_bytes()
    after, changed = prepare(before)
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "statements_changed_or_added": changed,
        "before_sha256": sha(before),
        "after_sha256": sha(after),
        "backup": str(BACKUP.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return
    if STATEMENTS.read_bytes() != before:
        raise SystemExit("statement table changed after preflight; rerun dry-run")
    if BACKUP.exists() and BACKUP.read_bytes() != before:
        raise SystemExit(f"refusing to overwrite a different recovery backup: {BACKUP.name}")
    if not BACKUP.exists():
        shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, after)
    if sha(STATEMENTS.read_bytes()) != sha(after):
        atomic_write(STATEMENTS, before)
        raise SystemExit("post-write hash mismatch; original table restored")
    print("applied; recovery backup retained; output hash verified")


if __name__ == "__main__":
    main()
