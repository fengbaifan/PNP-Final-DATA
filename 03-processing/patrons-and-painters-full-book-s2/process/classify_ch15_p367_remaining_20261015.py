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
PAGE_IMAGE = ROOT / "scripts/.tmp_active_s2_chp15_p367_body_hi_20261004.png"
SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l30-36"

EXPECTED_HASHES = {
    "statements": "30c4fe3b1bbf126f887d39e5e9265e093e81f95021ffb5f5965dbbbb09996fbf",
    "candidates": "6b06805a83adef22e45be657b6cf2e0835edae2b777cc8a3bc4afd26ed9bd867",
    "mentions": "189a1728d9ee30248be1b55fe996c6b7d61438d58fb94fe8a192cef523998eac",
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "pdf": "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
    "page_image": "9a564347b5af1363b3ee1a66a3b1a7516226c300a51ffde7e9dad7e8df9845e1",
}

# True means a source-supported S2 relation candidate, not an S6 formal edge.
DECISIONS: dict[str, tuple[bool, str, str | None]] = {
    "st-chp15-p367-elementi-publication-in-rome": (
        True,
        "Haskell explicitly connects Memmo's publication of the Elementi with the work itself; Rome and the relative time remain qualifiers, and the book has not been independently consulted.",
        None,
    ),
    "st-chp15-p367-elementi-account-of-lodoli-theories": (
        True,
        "The source describes the Elementi as an account of Lodoli's architectural theories; retain the work-to-thinker relation as Haskell's characterization, not an independently verified bibliographic conclusion.",
        None,
    ),
    "st-chp15-p367-apologhi-satirised-leading-figures": (
        True,
        "Haskell says the Apologhi satirised a source-defined group of Venetian society figures. Their names and number are not supplied; use the open collective candidate.",
        None,
    ),
    "st-chp15-p367-memmo-dissatisfied-with-progress": (
        True,
        "Haskell explicitly reports Memmo's dissatisfaction with progress on the Prà della Valle scheme; preserve this as an attributed person-to-project stance.",
        None,
    ),
    "st-chp15-p367-debts-amphitheatre-and-statue-progress": (
        False,
        "This reports the project's debt-clearing state. The passage does not identify a debtor, creditor, or payment relation, and it does not assign the debt personally to Memmo.",
        None,
    ),
    "st-chp15-p367-results-difficult-to-assess": (
        False,
        "This is Haskell's evaluative judgment about how difficult the project's final results are to assess, not a relation between independently identified entities.",
        None,
    ),
    "st-chp15-p367-patronage-and-speed-caused-variation": (
        True,
        "Haskell explicitly attributes variation in sculptural quality and style to divided patronage and pressure for cheap, rapid completion. Preserve the causal account as attributed, without assigning individual patrons or sculptors.",
        "The causal outcome is a quality-and-style variation in the Prà scheme, not a separately identified work or actor; no individual patron, sculptor, or contribution is named.",
    ),
    "st-chp15-p367-canova-only-sculptor-survived-his-age": (
        False,
        "This is a comparative career and survival assessment of the sculptors involved, not a source-supported relation between identified entities.",
        None,
    ),
    "st-chp15-p367-canova-statue-only-contemporary-honoured": (
        True,
        "Haskell explicitly places the Canova statue within the source-defined group of honoured heroes and calls it the only contemporary represented; the group remains unnamed and open.",
        None,
    ),
    "st-chp15-p367-sculptural-quality-and-rococo-remains": (
        False,
        "This is Haskell's aesthetic assessment of unnamed sculptors' competence and elegance; it does not identify a relation suitable for the entity graph.",
        None,
    ),
    "st-chp15-p367-hero-subjects-and-medieval-costumes": (
        False,
        "This describes the range of distinction among the source-defined heroes, from an unnamed donor's ancestor to named examples. It is a group-level descriptive property, not a relation; retain the group as the statement's subject.",
        None,
    ),
    "st-chp15-p367-climate-and-prato-impression-partial": (
        True,
        "Haskell explicitly says time and Italian climate altered the Prà's original impression and describes seasonal effects. Keep the site-linked causal observation source-bound and preserve the p.368 continuation.",
        "The passage identifies the Prà as the affected site but treats the original impression and seasonal effects as descriptive qualities, not separate entities; no finer environmental agent or measurable effect is specified.",
    ),
    "st-chp15-p367-skala-student-description": (
        True,
        "The source explicitly links Skala's study to Padua; retain the claim that he was the first German student after the League of Cambrai as Haskell's qualified description.",
        None,
    ),
    "st-chp15-p367-veith-student-fame-1709": (
        False,
        "This is a qualified biographical description of Veith's reputation in 1709; it names no institution or other relation endpoint, and the question mark must remain.",
        None,
    ),
    "st-chp15-p367-canova-statue-tribute-to-reputation": (
        False,
        "This is Haskell's evaluative interpretation of the statue as a tribute to Canova's reputation, not a separate factual relation.",
        None,
    ),
    "st-chp15-p367-rococo-sculpture-remains-at-prato": (
        True,
        "The passage locates surviving Rococo sculpture at the Prà della Valle; retain the site-to-sculptural-remains relation while attributing the 'one of the best places' evaluation to Haskell.",
        None,
    ),
    "st-chp15-p367-heroes-period-middle-ages": (
        True,
        "Haskell explicitly assigns many members of the source-defined Prà heroes group to the Middle Ages; connect the group to the period without inferring individual statue dates.",
        None,
    ),
    "st-chp15-p367-hero-costumes-reproduced": (
        False,
        "This describes the varying accuracy and seriousness of costume reproduction as a group-level quality; it is not a relation between independently identified entities.",
        None,
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12235",
        "canonical_name": "Unnamed Venetian society figures satirised in Lodoli's Apologhi",
        "suggested_type": "",
        "status": "open",
        "detail": "Source-defined collective of leading figures in Venetian society that Haskell says the Apologhi satirised. The passage gives no names, number, or roster; do not infer individuals from the surrounding account. The candidate remains untyped and open.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L32",
    },
    {
        "candidate_id": "cand-12236",
        "canonical_name": "Heroes represented at the Prà della Valle",
        "suggested_type": "",
        "status": "open",
        "detail": "Source-defined collective of heroes represented at the Prà della Valle. Haskell gives Livy and Galileo as examples and refers to an unnamed donor's ancestor, but supplies no complete roster, count, or one-to-one identification of statues; the candidate remains untyped and open.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L36",
    },
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
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), has_bom


def encode_csv(fields: list[str], rows: list[dict], has_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if has_bom else data


def add_candidate(fields: list[str], row: dict) -> dict:
    return {field: row.get(field, "") for field in fields}


def find_phrase(text: str, phrase: str) -> tuple[int, int]:
    start = text.find(phrase)
    if start < 0 or text.find(phrase, start + 1) >= 0:
        raise SystemExit(f"Expected exactly one source occurrence: {phrase!r}")
    return start, start + len(phrase)


def write_atomic(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(prefix=path.name + ".", suffix=".tmp", dir=path.parent, delete=False) as temp:
        temp.write(data)
        temp_path = Path(temp.name)
    temp_path.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify the remaining p.367 S2 relation candidates.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="Validate and print the planned changes without writing (default).")
    mode.add_argument("--apply", action="store_true", help="Apply changes after all preconditions pass.")
    args = parser.parse_args()

    require_hashes()
    statement_rows = load_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_bom = load_csv(CANDIDATES)
    mention_fields, mention_rows, mention_bom = load_csv(MENTIONS)

    segment_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    by_id = {row["statement_id"]: row for row in segment_rows}
    if len(segment_rows) != 38:
        raise SystemExit(f"Expected 38 statements in p.367 segment, found {len(segment_rows)}")
    unset_ids = {row["statement_id"] for row in segment_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset_ids != set(DECISIONS):
        raise SystemExit(f"Unset statement set changed: {sorted(unset_ids ^ set(DECISIONS))}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_rows) != 20:
        raise SystemExit("Expected exactly 20 already-classified true relation candidates")
    if any(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_rows):
        raise SystemExit("Unexpected pre-existing false classification in this segment")

    candidates_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row.get("candidate_id", "").startswith("cand-")) != 12234:
        raise SystemExit("Candidate ID ceiling changed; review new IDs before applying")
    if any(row["candidate_id"] in candidates_by_id for row in NEW_CANDIDATES):
        raise SystemExit("A proposed candidate ID already exists")

    mentions_by_id = {row["mention_id"]: row for row in mention_rows}
    new_mention_ids = ["m-chp15-p367-memmo-0068", "m-chp15-p367-memmo-0069", "m-chp15-p367-memmo-0070"]
    if any(mention_id in mentions_by_id for mention_id in new_mention_ids):
        raise SystemExit("A proposed p.367 mention ID already exists")
    if any(row.get("segment_id") == SEGMENT_ID and row.get("mention_id", "").endswith(("-0068", "-0069", "-0070")) for row in mention_rows):
        raise SystemExit("A p.367 mention suffix is already in use")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[29:36])
    if not segment_text.startswith("[Page 367]\n"):
        raise SystemExit("Source segment boundary changed")
    existing_elementi = mentions_by_id.get("m-chp15-p367-memmo-0001")
    if not existing_elementi or existing_elementi.get("start_char") != "50" or segment_text[50:86] != existing_elementi.get("surface_form"):
        raise SystemExit("Known source-span anchor no longer matches the p.367 segment text")

    phrase_mentions = [
        (new_mention_ids[0], "cand-12235", "many of the leading figures of Venetian society", "Unnamed collective satirised by the Apologhi; the source supplies no names or roster."),
        (new_mention_ids[1], "cand-12236", "a host of great and legendary heroes", "Source-defined group of heroes represented at the Prà della Valle; membership is not fully enumerated."),
        (new_mention_ids[2], "cand-12236", "the heroes celebrated", "Coreferential source phrase for the heroes represented at the Prà della Valle; no complete roster is supplied."),
    ]
    new_mentions = []
    for mention_id, candidate_id, surface, note in phrase_mentions:
        start, end = find_phrase(segment_text, surface)
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    endpoint_updates = {
        "st-chp15-p367-apologhi-satirised-leading-figures": {"object_candidate_id": "cand-12235"},
        "st-chp15-p367-canova-statue-only-contemporary-honoured": {"object_candidate_id": "cand-12236"},
        "st-chp15-p367-hero-subjects-and-medieval-costumes": {"subject_candidate_id": "cand-12236"},
        "st-chp15-p367-heroes-period-middle-ages": {"subject_candidate_id": "cand-12236"},
        "st-chp15-p367-hero-costumes-reproduced": {"subject_candidate_id": "cand-12236"},
        "st-chp15-p367-skala-student-description": {"object_candidate_id": "cand-1803"},
    }

    for statement_id, changes in endpoint_updates.items():
        if statement_id not in by_id:
            raise SystemExit(f"Missing statement for endpoint update: {statement_id}")
        by_id[statement_id].update(changes)

    for statement_id, candidate_id in [
        ("st-chp15-p367-apologhi-satirised-leading-figures", "cand-12235"),
        ("st-chp15-p367-canova-statue-only-contemporary-honoured", "cand-12236"),
        ("st-chp15-p367-hero-subjects-and-medieval-costumes", "cand-12236"),
        ("st-chp15-p367-heroes-period-middle-ages", "cand-12236"),
        ("st-chp15-p367-hero-costumes-reproduced", "cand-12236"),
    ]:
        ids = by_id[statement_id]["qualifiers"].setdefault("mentioned_candidate_ids", [])
        if candidate_id not in ids:
            ids.append(candidate_id)

    for statement_id, (is_relation, note, open_reason) in DECISIONS.items():
        row = by_id[statement_id]
        qualifiers = row["qualifiers"]
        qualifiers["relation_candidate"] = is_relation
        qualifiers["relation_candidate_note"] = note
        if is_relation and open_reason:
            qualifiers["open_endpoint_reason"] = open_reason
        else:
            qualifiers.pop("open_endpoint_reason", None)

    for row in NEW_CANDIDATES:
        candidate_rows.append(add_candidate(candidate_fields, row))
    mention_rows.extend(new_mentions)

    true_count = sum(is_relation for is_relation, _, _ in DECISIONS.values())
    false_count = len(DECISIONS) - true_count
    print(f"Segment: {SEGMENT_ID}; remaining classifications: {len(DECISIONS)} ({true_count} true, {false_count} false)")
    print("New candidates: cand-12235 (satirised Venetian society figures), cand-12236 (Prà heroes)")
    for row in new_mentions:
        print(f"Mention {row['mention_id']}: {row['surface_form']!r} [{row['start_char']},{row['end_char']}) -> {row['candidate_id']}")
    print("Endpoint updates:")
    for statement_id, changes in endpoint_updates.items():
        print(f"  {statement_id}: {changes}")

    if not args.apply:
        print("PREVIEW ONLY; no files written.")
        return

    backup_suffix = ".bak-s2-ch15-p367-classification-20261015"
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
