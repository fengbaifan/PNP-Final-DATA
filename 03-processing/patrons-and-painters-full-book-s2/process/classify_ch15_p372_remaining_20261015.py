from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-15.pdf"
PAGE_IMAGE = ROOT / "scripts/.tmp_active_s2_chp15_p372_20261004.png"
SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l85-88"

EXPECTED_HASHES = {
    "statements": "2785c0477e4afe4967d63a432f29e9742787eb58c42dde79389673e841bc8169",
    "candidates": "bc46e5a2c1a9d7c9f064329cd1d27578c6e3b6016420b1d1d0d778820eba88fe",
    "mentions": "21b92d5f259ccc09b23983232e8baf64b3c3bd0caf6c40f8229d27c57707253a",
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "pdf": "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
    "page_image": "811e9891b03805ec6c50e1571c3a65c17419dbf2272fbca71d7d2b18c69e0b98",
}

DECISIONS: dict[str, tuple[bool, str, str | None]] = {
    "st-chp15-p372-renier-compromised-with-opposing-forces": (
        True,
        "Haskell explicitly says Renier later compromised with forces he had once attacked; keep the unnamed political group source-bounded and do not infer its members or faction.",
        None,
    ),
    "st-chp15-p372-querini-pagan-shrines-personal-significance": (
        True,
        "Haskell interprets pagan shrines and temples as having personal significance for Querini, whether sentimental or romantic; this is not evidence of formal religious belief.",
        None,
    ),
    "st-chp15-p372-maffei-collected-antique-sculpture": (
        True,
        "Haskell explicitly says Maffei collected antique sculpture; retain the generic category as a collecting interest without inventing individual objects.",
        None,
    ),
    "st-chp15-p372-querini-distinguished-from-maffei": (
        True,
        "Haskell explicitly distinguishes Querini's activities from Maffei's by the significance pagan antiquity held for Querini; preserve this as the author's comparison.",
        None,
    ),
    "st-chp15-p372-querini-return-compared-with-winckelmann": (
        True,
        "Haskell explicitly compares Querini's return to an ideal world of the past with Winckelmann's and qualifies Querini's lesser intellectual or critical insight; retain the comparative attribution.",
        None,
    ),
    "st-chp15-p372-pagan-shrines-lacked-significance-for-most-contemporaries": (
        True,
        "Haskell contrasts Querini's relation to pagan shrines with their lack of comparable significance for most scholars and antiquarians of his age; preserve 'most' and the source attribution.",
        None,
    ),
    "st-chp15-p372-maffei-recorded-evidence-of-the-past": (
        True,
        "Haskell says Maffei lovingly recorded evidence of the past; retain the attributed scholarly activity while leaving its unspecified objects open.",
        "The recorded evidence is not itemized or identified as particular works or documents, so the source does not support a specific object endpoint.",
    ),
    "st-chp15-p372-querini-retired-from-contemporary-politics": (
        False,
        "This is Haskell's broad characterization of Querini's later biographical state; no specific office, institution, or political event is named as a relation endpoint.",
        None,
    ),
    "st-chp15-p372-querini-returned-to-ideal-world-of-past": (
        False,
        "'The ideal world of the past' is Haskell's interpretive description, not a named entity or independently identified relation endpoint.",
        None,
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12247",
        "canonical_name": "Unidentified political forces Renier had attacked and later compromised with",
        "suggested_type": "",
        "status": "open",
        "detail": "Source-bounded group in Haskell's account of Renier. The forces, their members, and their political identity are not named; do not equate them with Querini's reform opponents or any previously described faction.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L86",
    },
    {
        "candidate_id": "cand-12248",
        "canonical_name": "Pagan shrines and temples as objects of Querini's reported sentimental or romantic significance",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-defined concept in Haskell's interpretation of Querini's relation to pagan antiquity. No individual shrine or temple is identified, and this does not establish formal religious belief.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L87",
    },
    {
        "candidate_id": "cand-12249",
        "canonical_name": "Antique sculpture as a collecting category in Haskell's account of Maffei",
        "suggested_type": "term",
        "status": "open",
        "detail": "Generic category of objects that Haskell says Maffei collected; it is not a particular collection or a set of identified sculptures.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L87",
    },
    {
        "candidate_id": "cand-12250",
        "canonical_name": "Most scholars and antiquarians of Querini's age in Haskell's comparison",
        "suggested_type": "",
        "status": "open",
        "detail": "Source-bounded unnamed collective qualified by Haskell as 'most'; no individuals, academy, or formal organization are identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L87",
    },
]

NEW_MENTIONS = [
    ("m-chp15-p372-querini-0018", "cand-12247", "the forces that he had once attacked", "Unnamed political group in Haskell's account of Renier; membership and faction are not supplied."),
    ("m-chp15-p372-querini-0019", "cand-12248", "the shrines and temples of paganism", "Generic concept in Haskell's interpretation of Querini; no individual site is identified."),
    ("m-chp15-p372-querini-0020", "cand-12249", "antique sculpture", "Generic collecting category attributed to Maffei; no individual sculpture is named."),
    ("m-chp15-p372-querini-0021", "cand-12250", "the scholars and antiquarians of his age", "Unnamed collective qualified by the source as 'most'."),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_hashes() -> None:
    paths = {
        "statements": STATEMENTS,
        "candidates": CANDIDATES,
        "mentions": MENTIONS,
        "source": SOURCE,
        "pdf": PDF,
        "page_image": PAGE_IMAGE,
    }
    for label, path in paths.items():
        if not path.exists():
            raise SystemExit(f"Required input is missing: {path}")
        actual = sha256(path)
        if actual != EXPECTED_HASHES[label]:
            raise SystemExit(f"Precondition hash changed for {label}: {actual}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def encode_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def load_csv(path: Path) -> tuple[list[str], list[dict], bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), has_bom


def encode_csv(fields: list[str], rows: list[dict], has_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + data if has_bom else data


def phrase_span(text: str, phrase: str) -> tuple[int, int]:
    positions = [i for i in range(len(text)) if text.startswith(phrase, i)]
    if len(positions) != 1:
        raise SystemExit(f"Expected one source occurrence of {phrase!r}, found {len(positions)}")
    return positions[0], positions[0] + len(phrase)


def write_atomic(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(prefix=path.name + ".", suffix=".tmp", dir=path.parent, delete=False) as temp:
        temp.write(data)
        temp_path = Path(temp.name)
    temp_path.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify remaining p.372 S2 statements.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="Validate and print planned changes without writing (default).")
    mode.add_argument("--apply", action="store_true", help="Apply changes after all preconditions pass.")
    args = parser.parse_args()

    require_hashes()
    statement_rows = load_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_bom = load_csv(CANDIDATES)
    mention_fields, mention_rows, mention_bom = load_csv(MENTIONS)

    segment_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    by_id = {row["statement_id"]: row for row in segment_rows}
    if len(segment_rows) != 13:
        raise SystemExit(f"Expected 13 statements in p.372 segment, found {len(segment_rows)}")
    unset_ids = {row["statement_id"] for row in segment_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset_ids != set(DECISIONS):
        raise SystemExit(f"Unset statement set changed: {sorted(unset_ids ^ set(DECISIONS))}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_rows) != 4:
        raise SystemExit("Expected exactly 4 already-classified true relation candidates")
    if any(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_rows):
        raise SystemExit("Unexpected pre-existing false classification in this segment")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row.get("candidate_id", "").startswith("cand-"))
    proposed_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if max_candidate != 12246 or proposed_candidate_ids.intersection(candidate_by_id):
        raise SystemExit(f"Candidate ID ceiling or proposed IDs changed: cand-{max_candidate}")

    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    proposed_mention_ids = [row[0] for row in NEW_MENTIONS]
    if any(mention_id in mention_by_id for mention_id in proposed_mention_ids):
        raise SystemExit("A proposed p.372 mention ID already exists")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(lines[84:88])
    if not segment_text.startswith("[Page 372]\n"):
        raise SystemExit("Source segment boundary changed")
    mention_spans = [phrase_span(segment_text, phrase) for _, _, phrase, _ in NEW_MENTIONS]

    endpoint_updates = {
        "st-chp15-p372-renier-compromised-with-opposing-forces": {
            "object_candidate_id": "cand-12247",
        },
        "st-chp15-p372-querini-pagan-shrines-personal-significance": {
            "object_candidate_id": "cand-12248",
        },
        "st-chp15-p372-maffei-collected-antique-sculpture": {
            "object_candidate_id": "cand-12249",
        },
        "st-chp15-p372-pagan-shrines-lacked-significance-for-most-contemporaries": {
            "subject_candidate_id": "cand-12248",
            "object_candidate_id": "cand-12250",
            "predicate": "pagan_shrines_lacked_comparable_significance_for_most_contemporary_scholars_and_antiquarians",
        },
    }
    for statement_id, changes in endpoint_updates.items():
        if statement_id not in by_id:
            raise SystemExit(f"Missing statement for endpoint update: {statement_id}")
        by_id[statement_id].update(changes)

    # The statement id in the existing data includes the query-verb phrase in its stem.
    if "st-chp15-p372-querini-distinguished-from-maffei" not in by_id:
        raise SystemExit("Missing Querini/Maffei comparison statement")
    by_id["st-chp15-p372-querini-distinguished-from-maffei"]["qualifiers"].setdefault("mentioned_candidate_ids", []).append("cand-12248")
    by_id["st-chp15-p372-pagan-shrines-lacked-significance-for-most-contemporaries"]["qualifiers"].setdefault("mentioned_candidate_ids", []).extend(["cand-12248", "cand-12250"])

    for statement_id, (is_relation, note, open_reason) in DECISIONS.items():
        qualifiers = by_id[statement_id]["qualifiers"]
        qualifiers["relation_candidate"] = is_relation
        qualifiers["relation_candidate_note"] = note
        if is_relation and open_reason:
            qualifiers["open_endpoint_reason"] = open_reason
        else:
            qualifiers.pop("open_endpoint_reason", None)

    for statement_id, candidate_id in [
        ("st-chp15-p372-renier-compromised-with-opposing-forces", "cand-12247"),
        ("st-chp15-p372-querini-pagan-shrines-personal-significance", "cand-12248"),
        ("st-chp15-p372-maffei-collected-antique-sculpture", "cand-12249"),
        ("st-chp15-p372-pagan-shrines-lacked-significance-for-most-contemporaries", "cand-12250"),
    ]:
        ids = by_id[statement_id]["qualifiers"].setdefault("mentioned_candidate_ids", [])
        if candidate_id not in ids:
            ids.append(candidate_id)

    for mention_spec, span in zip(NEW_MENTIONS, mention_spans):
        mention_id, candidate_id, surface_form, note = mention_spec
        mention_rows.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": surface_form,
                "start_char": str(span[0]),
                "end_char": str(span[1]),
                "note": note,
            }
        )
    for candidate in NEW_CANDIDATES:
        candidate_rows.append({field: candidate.get(field, "") for field in candidate_fields})

    segment_after = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    true_count = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_after)
    false_count = sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_after)
    unset_count = sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in segment_after)
    if (true_count, false_count, unset_count, len(segment_after)) != (11, 2, 0, 13):
        raise SystemExit(f"Unexpected post-classification counts: {true_count}/{false_count}/{unset_count}/{len(segment_after)}")

    print(f"Segment: {SEGMENT_ID}; classified {len(DECISIONS)} remaining statements.")
    print(f"Segment after: {len(segment_after)} statements ({true_count} true, {false_count} false, {unset_count} unset).")
    print("New candidates:")
    for candidate in NEW_CANDIDATES:
        print(f"  {candidate['candidate_id']}: {candidate['canonical_name']}")
    print("New exact-span mentions:")
    for mention_spec, span in zip(NEW_MENTIONS, mention_spans):
        print(f"  {mention_spec[0]} -> {mention_spec[1]}: {mention_spec[2]!r} [{span[0]},{span[1]})")
    print("Endpoint updates:")
    for statement_id, changes in endpoint_updates.items():
        print(f"  {statement_id}: {changes}")

    if not args.apply:
        print("PREVIEW ONLY; no files written.")
        return

    backup_suffix = ".bak-s2-ch15-p372-classification-20261015"
    targets = [STATEMENTS, CANDIDATES, MENTIONS]
    backups = [path.with_name(path.name + backup_suffix) for path in targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A recovery backup already exists; inspect it before applying")
    payloads = {
        STATEMENTS: encode_jsonl(statement_rows),
        CANDIDATES: encode_csv(candidate_fields, candidate_rows, candidate_bom),
        MENTIONS: encode_csv(mention_fields, mention_rows, mention_bom),
    }
    try:
        for source, backup in zip(targets, backups):
            shutil.copy2(source, backup)
        for path, data in payloads.items():
            write_atomic(path, data)
    except Exception:
        for source, backup in zip(targets, backups):
            if backup.exists():
                shutil.copy2(backup, source)
        raise
    print("APPLIED. Recovery copies:")
    for path in backups:
        print(f"  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
