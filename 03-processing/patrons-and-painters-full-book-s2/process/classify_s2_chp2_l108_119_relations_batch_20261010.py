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
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_i.md"
EXPECTED_SHA = "4769a0997fdb33e95265d7f5470072e928c4e745267615baa8e9e243459e3308"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-l108-119-relations-20261010")
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l108-119"

SPECS = {
    "st-chp2-seci-l108-119-giustiniani-roncalli-trip": (
        "accompanied by the painter Cristoforo Roncalli",
        "Haskell reports that Giustiniani and Roncalli travelled together in 1606; retain the four-month and Northern Europe/Low Countries scope. This does not establish a formal employment relationship.",
    ),
    "st-chp2-seci-l108-119-two-men-visited": (
        "The two men had visited churches and private collections",
        "The source reports a joint visit by Giustiniani and Roncalli during the trip; it does not identify the visited churches or collections.",
    ),
    "st-chp2-seci-l108-119-two-men-discussed-art": (
        "discussed pictures and landscapes",
        "The source reports that Giustiniani and Roncalli discussed pictures and landscapes during the trip; preserve Haskell's characterization of their expertise as a source assessment.",
    ),
    "st-chp2-seci-l108-119-welcomed-northern-artists": (
        "gave a special welcome to Northern artists",
        "Haskell reports Giustiniani's welcome to Northern artists in Rome; the group is unnamed and the statement does not imply that every Northern artist received the welcome.",
    ),
    "st-chp2-seci-l108-119-northern-artists-resided-in-palace": (
        "many of whom lived in his palace",
        "Haskell says many members of the unnamed Northern artists group lived in Giustiniani's palace. Retain the source's non-exhaustive 'many' and the unresolved identity of the palace.",
    ),
    "st-chp2-seci-l108-119-florentine-sculptors-chapel-decoration": (
        "A group of Florentine sculptors was completing the decoration of his family chapel",
        "Haskell reports the unnamed Florentine sculptor group was completing decoration of Maffeo's family chapel; this does not assign the work solely to one artist or establish completion date.",
    ),
    "st-chp2-seci-l108-119-pietro-bernini-member": (
        "among them Pietro Bernini",
        "The wording places Pietro Bernini within the unnamed Florentine sculptor group. Encode the stated membership person-to-group; it does not assign him sole responsibility for the decoration.",
    ),
    "st-chp2-seci-l108-119-maffeo-correspondence-peiresc": (
        "engaged in a learned correspondence with the Provençal antiquary Peiresc",
        "Haskell reports learned correspondence between Maffeo Barberini and Peiresc; no dates, letters, or independent consultation of the correspondence are established here.",
    ),
    "st-chp2-seci-l108-119-commissioned-modern-pictures-reni": (
        "commissioned modern pictures by Guido Reni",
        "Haskell reports that Maffeo commissioned modern pictures by Guido Reni; no individual works or commission dates are specified in this statement.",
    ),
    "st-chp2-seci-l108-119-commissioned-modern-pictures-pomarancio": (
        "and by Pomarancio",
        "Haskell reports that Maffeo commissioned modern pictures by the artist printed as Pomarancio; no individual works are named here, and canonical identity remains for S3.",
    ),
    "st-chp2-seci-l108-119-acquired-jacob-and-angel": (
        "from whom he acquired a Jacob and the Angel",
        "Haskell reports Maffeo's acquisition of the work from Pomarancio. Preserve the seller/source qualifier; this statement does not establish Pomarancio as creator or identify the work's version.",
    ),
    "st-chp2-seci-l108-119-maffeo-commissioned-st-sebastian": (
        "commission a work from him—a St Sebastian",
        "Haskell reports a commission by Maffeo from Gian Lorenzo Bernini for the St Sebastian work. Preserve 'among the first', the absent commission date, and unresolved version; the related design and retention statements remain separate.",
    ),
    "st-chp2-seci-l108-119-st-sebastian-designed-for-chapel": (
        "designed originally for his chapel",
        "Haskell says the St Sebastian was originally designed for Maffeo's family chapel; intended location does not establish installation there.",
    ),
    "st-chp2-seci-l108-119-st-sebastian-retained-in-palace": (
        "retained hi the palace",
        "Haskell says the St Sebastian was retained in Maffeo's palace. Preserve the OCR wording in the evidence anchor; the building's identity is unresolved and must not be merged with Giustiniani's palace.",
    ),
    "st-chp2-seci-l108-119-reni-worked-during-bologna-legate": (
        "who had worked for him during his legateship in Bologna",
        "Haskell reports that Reni worked for Maffeo during the latter's legateship in Bologna; do not infer an exact employment term or a specific work from this sentence.",
    ),
    "st-chp2-seci-l108-119-maffeo-intellectual-circle": (
        "He moved, above all, in a circle of writers, scholars, scientists and poets",
        "Haskell places Maffeo in an unnamed intellectual and literary circle; preserve the source-defined group scope without inferring a complete membership list.",
    ),
    "st-chp2-seci-l108-119-ludovisi-monopolised-after-1621": (
        "Ludovisi monopolised Bernini’s output",
        "Haskell characterizes the Ludovisi family's control of Bernini's output as a monopoly after 1621; retain the source's temporal scope and characterization without expanding it to all patronage.",
    ),
}

EXPECTED_ENDPOINTS = {
    "st-chp2-seci-l108-119-giustiniani-roncalli-trip": ("cand-1200", "cand-2218"),
    "st-chp2-seci-l108-119-two-men-visited": ("cand-1200", "cand-2218"),
    "st-chp2-seci-l108-119-two-men-discussed-art": ("cand-1200", "cand-2218"),
    "st-chp2-seci-l108-119-welcomed-northern-artists": ("cand-1200", "cand-4341"),
    "st-chp2-seci-l108-119-northern-artists-resided-in-palace": ("cand-4341", "cand-4310"),
    "st-chp2-seci-l108-119-florentine-sculptors-chapel-decoration": ("cand-4346", "cand-4252"),
    "st-chp2-seci-l108-119-pietro-bernini-member": ("cand-4346", "cand-0339"),
    "st-chp2-seci-l108-119-maffeo-correspondence-peiresc": ("cand-0209", "cand-1861"),
    "st-chp2-seci-l108-119-commissioned-modern-pictures-reni": ("cand-0209", "cand-2124"),
    "st-chp2-seci-l108-119-commissioned-modern-pictures-pomarancio": ("cand-0209", "cand-2218"),
    "st-chp2-seci-l108-119-acquired-jacob-and-angel": ("cand-0209", "cand-4345"),
    "st-chp2-seci-l108-119-maffeo-commissioned-st-sebastian": ("cand-0209", "cand-4347"),
    "st-chp2-seci-l108-119-st-sebastian-designed-for-chapel": ("cand-4347", "cand-4252"),
    "st-chp2-seci-l108-119-st-sebastian-retained-in-palace": ("cand-4347", "cand-4343"),
    "st-chp2-seci-l108-119-reni-worked-during-bologna-legate": ("cand-2124", "cand-0209"),
    "st-chp2-seci-l108-119-maffeo-intellectual-circle": ("cand-0209", "cand-4344"),
    "st-chp2-seci-l108-119-ludovisi-monopolised-after-1621": ("cand-4348", "cand-0295"),
}

REVERSE_MEMBERSHIP = "st-chp2-seci-l108-119-pietro-bernini-member"
CONTEXT_CHECKS = {
    111: ("accompanied by the painter Cristoforo Roncalli", "The two men had visited churches and private collections", "discussed pictures and landscapes", "special welcome to Northern artists", "many of whom lived in his palace"),
    113: ("He moved, above all, in a circle of writers, scholars, scientists and poets", "engaged in a learned correspondence with the Provençal antiquary Peiresc"),
    114: ("commissioned modern pictures by Guido Reni", "who had worked for him during his legateship in Bologna", "and by"),
    115: ("from whom he acquired a Jacob and the Angel", "A group of Florentine sculptors was completing the decoration of his family chapel", "among them Pietro Bernini", "commission a work from him—a St Sebastian", "designed originally for his chapel", "retained hi the palace"),
    117: ("Ludovisi monopolised Bernini’s output",),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(rows: list[dict]) -> dict[str, int]:
    flag = lambda row: (row.get("qualifiers") or {}).get("relation_candidate")
    complete = lambda row: bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
    true_rows = [row for row in rows if flag(row) is True]
    false_rows = [row for row in rows if flag(row) is False]
    return {
        "statements": len(rows),
        "relation_true": len(true_rows),
        "relation_true_with_two_endpoints": sum(complete(row) for row in true_rows),
        "relation_true_open": sum(not complete(row) for row in true_rows),
        "relation_false": len(false_rows),
        "double_endpoint_unclassified": sum(complete(row) and flag(row) not in (True, False) for row in rows),
    }


def read_rows() -> tuple[list[dict], bool, bytes]:
    raw = TABLE.read_bytes()
    require(sha256(TABLE) == EXPECTED_SHA, "book-statements.jsonl changed since review")
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    require(set(SPECS) <= set(by_id), "one or more reviewed statement IDs are absent")

    with (ROOT / "04-knowledge/tables/entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    with (ROOT / "04-knowledge/tables/s2-coverage.csv").open(encoding="utf-8-sig", newline="") as handle:
        segment_ids = {row["segment_id"] for row in csv.DictReader(handle)}

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    require(SEGMENT_ID in segment_ids, "reviewed segment is absent from S2 coverage")
    require(max(CONTEXT_CHECKS) <= len(source_lines), "source context line exceeds file length")
    for line_no, phrases in CONTEXT_CHECKS.items():
        for phrase in phrases:
            require(phrase in source_lines[line_no - 1], f"source context line {line_no} no longer matches {phrase!r}")

    for statement_id, (expected_text, _) in SPECS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        require(qualifiers.get("relation_candidate") not in (True, False), f"{statement_id} already classified")
        require(row.get("segment_id") == SEGMENT_ID, f"{statement_id} is outside the reviewed segment")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == EXPECTED_ENDPOINTS[statement_id],
                f"{statement_id} endpoints changed since review")
        require(row.get("subject_candidate_id") in candidate_ids and row.get("object_candidate_id") in candidate_ids,
                f"{statement_id} has a missing candidate endpoint")
        start, end = qualifiers.get("source_line_start"), qualifiers.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int) and start <= end and end <= len(source_lines),
                f"{statement_id} has an invalid source line anchor")
        anchored_text = " ".join(source_lines[start - 1:end])
        require(expected_text in anchored_text,
                f"{statement_id} anchor text does not match the reviewed source")

    return rows, bom, newline


def serialize(rows: list[dict], bom: bool, newline: bytes) -> bytes:
    out = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        out.append(line + newline)
    return b"".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write reviewed S2 classifications; default is dry-run")
    args = parser.parse_args()
    rows, bom, newline = read_rows()
    before = counts(rows)
    require(before == {
        "statements": 12682,
        "relation_true": 3748,
        "relation_true_with_two_endpoints": 3732,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4341,
    }, f"unexpected before counts: {before}")

    by_id = {row["statement_id"]: row for row in rows}
    for statement_id, (_, note) in SPECS.items():
        row = by_id[statement_id]
        if statement_id == REVERSE_MEMBERSHIP:
            row["subject_candidate_id"], row["object_candidate_id"] = EXPECTED_ENDPOINTS[statement_id][::-1]
        qualifiers = dict(row.get("qualifiers") or {})
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note
        row["qualifiers"] = qualifiers

    after = counts(rows)
    require(after == {
        "statements": 12682,
        "relation_true": 3765,
        "relation_true_with_two_endpoints": 3749,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4324,
    }, f"unexpected projected counts: {after}")
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "reviewed_statement_count": len(SPECS),
        "statement_ids": list(SPECS),
        "source_context_lines_checked": len(CONTEXT_CHECKS),
        "membership_direction_corrected": REVERSE_MEMBERSHIP,
        "before": before,
        "after": after,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    require(not BACKUP.exists(), f"recovery backup already exists: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".tmp-", delete=False) as handle:
            handle.write(serialize(rows, bom, newline))
            temp_path = Path(handle.name)
        os.replace(temp_path, TABLE)
        written = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        require(counts(written) == after, "post-write counts do not match preview")
        by_written_id = {row["statement_id"]: row for row in written}
        require(all((by_written_id[statement_id].get("qualifiers") or {}).get("relation_candidate") is True
                    for statement_id in SPECS), "one or more classifications were not persisted")
        require((by_written_id[REVERSE_MEMBERSHIP]["subject_candidate_id"],
                 by_written_id[REVERSE_MEMBERSHIP]["object_candidate_id"]) == ("cand-0339", "cand-4346"),
                "membership direction correction was not persisted")
        print(json.dumps({
            "result": "applied",
            "counts": counts(written),
            "sha256": sha256(TABLE),
            "backup": str(BACKUP.relative_to(ROOT)),
        }, ensure_ascii=False, indent=2))
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    main()
