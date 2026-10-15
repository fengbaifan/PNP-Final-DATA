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
PAGE_IMAGE = ROOT / "scripts/.tmp_active_s2_chp15_p369_body_20261004.png"
SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l49-59"

EXPECTED_HASHES = {
    "statements": "5d76724eaea941deddb471633c47b6f7ead0ae4db92a45a4e2bd055299480e8c",
    "candidates": "7c5b90f61197a79c0ce4aa0395ae76dacc15c493583b65126f0b86803110d3d0",
    "mentions": "32183fcec73f8c0bcbaa643a4a3bf1c8b74aaab65be9b904f92f545d934f625c",
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "pdf": "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
    "page_image": "672bfa6441e06c8f3624418ee2575a1ba79929f169f9f277bfe57bc74500f6af",
}

# True means an evidence-supported S2 relation candidate, not an S6 formal edge.
DECISIONS: dict[str, tuple[bool, str, str | None]] = {
    "st-chp15-p369-querini-reform-within-ruling-class": (
        True,
        "Haskell explicitly interprets Querini's proposed reform as a shift of power from one ruling-class faction to another; preserve this as his political interpretation without identifying either faction.",
        "Both factions and the precise institutional body are unnamed. Keep the source-attributed factional shift open; do not infer faction membership or a specific constitutional outcome.",
    ),
    "st-chp15-p369-querini-withdrawal-from-active-politics": (
        False,
        "This records a time-bounded biographical state after Querini's release, not a relation to a named political institution or office; the qualification already prevents overclaiming about all public roles.",
        None,
    ),
    "st-chp15-p369-querini-enlightenment-involvement": (
        True,
        "Haskell explicitly links Querini with the Enlightenment as an intellectual movement; retain the broad source-defined concept and the gradual wording.",
        None,
    ),
    "st-chp15-p369-wynne-links-three-patrons": (
        False,
        "This is Haskell's interpretive grouping of Wynne's place in three patrons' lives. The surrounding text specifies different relationships and does not support one common relation to all three.",
        None,
    ),
    "st-chp15-p369-wynne-interest-in-learned-company": (
        False,
        "This is Haskell's characterization of Wynne's main personal interest, not evidence of a specific affiliation or individual relationship with an identified learned society.",
        None,
    ),
    "st-chp15-p369-haskell-rosenberg-hardly-aspired-to-learned-company": (
        False,
        "This is Haskell's comparative characterization of Rosenberg's disposition; the passage identifies no specific social or institutional relation.",
        None,
    ),
    "st-chp15-p369-wynne-account-source-for-alticchiero": (
        True,
        "Haskell explicitly identifies Wynne's 1787 Alticchiero account (candidate cand-10534, named in note 4) as his main source for the villa. Keep the source relation attributed; the publication was not independently consulted.",
        None,
    ),
    "st-chp15-p369-wynne-philosophers-modest-retreats": (
        False,
        "This reports a general philosophical contrast in Wynne's opening remarks. The quotation does not itself identify a relationship between Alticchiero and a separately identified philosopher group.",
        None,
    ),
    "st-chp15-p369-alticchiero-simple-convenient-furnishings": (
        False,
        "This is a description of the villa's arrangement in Wynne's quoted account, not an entity relation; retain the quotation and source attribution.",
        None,
    ),
    "st-chp15-p369-alticchiero-no-theft-precautions": (
        False,
        "This is a historical security condition reported through Wynne's account, not a relation between separately identified entities.",
        None,
    ),
    "st-chp15-p369-wynne-trust-human-nature-tahiti-alticchiero": (
        True,
        "Haskell reports Wynne's exclamation that trust in human nature could be found at Tahiti. Preserve the rhetorical attribution and link the source-defined concept to the named place; this is not an empirical measurement.",
        None,
    ),
    "st-chp15-p369-haskell-alticchiero-unique-and-edifying": (
        False,
        "This is Haskell's evaluative claim that Alticchiero is unique in Italy and edifying even in Switzerland, not a factual relation to either place.",
        None,
    ),
    "st-chp15-p369-haskell-doubts-progressive-interpretation": (
        False,
        "This is Haskell's historiographical assessment of Querini's reform, not a relation between entities.",
        None,
    ),
    "st-chp15-p369-reforms-not-fundamental-change": (
        False,
        "This is a scalar characterization of the scope of Querini's proposed reforms; the factional relation is recorded separately.",
        None,
    ),
    "st-chp15-p369-querini-intellectual-cultural-pursuits-after-release": (
        False,
        "This summarizes Querini's activities after release as a biographical state; no distinct institution, work, or social endpoint is identified.",
        None,
    ),
    "st-chp15-p369-querini-festari-trip-observations": (
        True,
        "Haskell explicitly reports Querini and Festari acting together during their trip, admiring art and architecture and discussing local trade and industry. The places and individual works are not enumerated.",
        None,
    ),
    "st-chp15-p369-furniture-not-lavish": (
        False,
        "This is a material-quality description in Wynne's quoted account, not an entity relation.",
        None,
    ),
    "st-chp15-p369-arrangement-simple-convenient": (
        False,
        "This is a design-quality description in Wynne's quoted account, not an entity relation.",
        None,
    ),
    "st-chp15-p369-alticchiero-no-dogs": (
        False,
        "This records a condition of the villa grounds in Wynne's account, not a relation between identified entities.",
        None,
    ),
    "st-chp15-p369-wynne-trust-human-nature-alticchiero": (
        True,
        "Haskell reports Wynne's exclamation that trust in human nature could be found at Alticchiero. Preserve the rhetorical attribution and link the source-defined concept to the named place; this is not an empirical measurement.",
        None,
    ),
    "st-chp15-p369-alticchiero-edifying-in-switzerland": (
        False,
        "This is Haskell's evaluative comparison of the villa's effect with Switzerland, not a factual relation to that country.",
        None,
    ),
}

NEW_CANDIDATE = {
    "candidate_id": "cand-12240",
    "canonical_name": "Trust in human nature in Mme Rosenberg's comparison of Tahiti and Alticchiero",
    "suggested_type": "term",
    "status": "open",
    "detail": "Source-defined idea in Giustiniana Wynne-Rosenberg's reported exclamation that trust in human nature could be found at Tahiti and Alticchiero. Keep the claim rhetorical and attributed; do not treat it as a measured condition of either population.",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT_ID}#L57",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_hashes() -> None:
    paths = {"statements": STATEMENTS, "candidates": CANDIDATES, "mentions": MENTIONS, "source": SOURCE, "pdf": PDF, "page_image": PAGE_IMAGE}
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
    parser = argparse.ArgumentParser(description="Classify remaining p.369 S2 relation candidates.")
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
    if len(segment_rows) != 39:
        raise SystemExit(f"Expected 39 statements in p.369 segment, found {len(segment_rows)}")
    unset_ids = {row["statement_id"] for row in segment_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset_ids != set(DECISIONS):
        raise SystemExit(f"Unset statement set changed: {sorted(unset_ids ^ set(DECISIONS))}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_rows) != 18:
        raise SystemExit("Expected exactly 18 already-classified true relation candidates")
    if any(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_rows):
        raise SystemExit("Unexpected pre-existing false classification in this segment")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row.get("candidate_id", "").startswith("cand-"))
    if max_candidate != 12239 or NEW_CANDIDATE["candidate_id"] in candidate_by_id:
        raise SystemExit(f"Candidate ID ceiling changed: cand-{max_candidate}")
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    new_mention_ids = ["m-chp15-p369-querini-0056", "m-chp15-p369-querini-0057"]
    if any(mention_id in mention_by_id for mention_id in new_mention_ids):
        raise SystemExit("A proposed p.369 mention ID already exists")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(lines[48:59])
    if not segment_text.startswith("[Page 369]\n"):
        raise SystemExit("Source segment boundary changed")
    trust_span = phrase_span(segment_text, "such trust in human nature")
    account_span = phrase_span(segment_text, "her rapturous account")

    endpoint_updates = {
        "st-chp15-p369-wynne-account-source-for-alticchiero": {"subject_candidate_id": "cand-10534"},
        "st-chp15-p369-wynne-trust-human-nature-tahiti-alticchiero": {
            "subject_candidate_id": "cand-12240", "predicate": "trust_in_human_nature_reportedly_found_at_tahiti"
        },
        "st-chp15-p369-wynne-trust-human-nature-alticchiero": {
            "subject_candidate_id": "cand-12240", "predicate": "trust_in_human_nature_reportedly_found_at_alticchiero"
        },
    }
    for statement_id, changes in endpoint_updates.items():
        if statement_id not in by_id:
            raise SystemExit(f"Missing statement for endpoint update: {statement_id}")
        by_id[statement_id].update(changes)

    mention_rows.extend([
        {
            "mention_id": new_mention_ids[0], "segment_id": SEGMENT_ID, "candidate_id": "cand-12240",
            "surface_form": "such trust in human nature", "start_char": str(trust_span[0]), "end_char": str(trust_span[1]),
            "note": "Source-defined idea in Mme Rosenberg's rhetorical comparison of Tahiti and Alticchiero; not a measured population trait.",
        },
        {
            "mention_id": new_mention_ids[1], "segment_id": SEGMENT_ID, "candidate_id": "cand-10534",
            "surface_form": "her rapturous account", "start_char": str(account_span[0]), "end_char": str(account_span[1]),
            "note": "Coreferential mention of Wynne's Alticchiero account identified by note 4; the 1787 publication was not independently consulted.",
        },
    ])

    for statement_id, candidate_id in [
        ("st-chp15-p369-wynne-account-source-for-alticchiero", "cand-10534"),
        ("st-chp15-p369-wynne-trust-human-nature-tahiti-alticchiero", "cand-12240"),
        ("st-chp15-p369-wynne-trust-human-nature-alticchiero", "cand-12240"),
    ]:
        ids = by_id[statement_id]["qualifiers"].setdefault("mentioned_candidate_ids", [])
        if candidate_id not in ids:
            ids.append(candidate_id)

    for statement_id, (is_relation, note, open_reason) in DECISIONS.items():
        qualifiers = by_id[statement_id]["qualifiers"]
        qualifiers["relation_candidate"] = is_relation
        qualifiers["relation_candidate_note"] = note
        if is_relation and open_reason:
            qualifiers["open_endpoint_reason"] = open_reason
        else:
            qualifiers.pop("open_endpoint_reason", None)

    candidate_rows.append({field: NEW_CANDIDATE.get(field, "") for field in candidate_fields})

    true_count = sum(is_relation for is_relation, _, _ in DECISIONS.values())
    false_count = len(DECISIONS) - true_count
    print(f"Segment: {SEGMENT_ID}; remaining classifications: {len(DECISIONS)} ({true_count} true, {false_count} false)")
    print("New candidate: cand-12240, source-bounded term for the reported idea of trust in human nature.")
    print(f"Mention {new_mention_ids[0]}: 'such trust in human nature' [{trust_span[0]},{trust_span[1]}) -> cand-12240")
    print(f"Mention {new_mention_ids[1]}: 'her rapturous account' [{account_span[0]},{account_span[1]}) -> cand-10534")
    print("Endpoint updates:")
    for statement_id, changes in endpoint_updates.items():
        print(f"  {statement_id}: {changes}")

    if not args.apply:
        print("PREVIEW ONLY; no files written.")
        return

    backup_suffix = ".bak-s2-ch15-p369-classification-20261015"
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
