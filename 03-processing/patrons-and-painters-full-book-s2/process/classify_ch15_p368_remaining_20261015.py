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
SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l38-47"

EXPECTED_HASHES = {
    "statements": "e3119d0298a4e066dd6c9de171e5915964adca0caa34f2955df7e176d0f5e17c",
    "candidates": "ce5db5ee8c6a670b5edee2d6bd822f0fba2812ebc5e50ee1ca82c5978e83b173",
    "mentions": "ccf1eff692dbca406efea0676ed1e8a2457ea347ec757a51a01e0b54bb94cea1",
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "pdf": "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
}

# True means an evidence-supported S2 relation candidate, not an S6 formal edge.
DECISIONS: dict[str, tuple[bool, str, str | None]] = {
    "st-chp15-p368-prato-effect-of-decay": (
        True,
        "Haskell explicitly links general decay at the Prà to worn inscriptions, less legible figures and a changed state of weaker sculptures; retain the retrospective site-level observation without claiming a separate work identity.",
        "The source describes changes in the site's inscriptions, figures and sculptures as qualities of the place, not as separately identified entities; it names no specific sculpture or inscription.",
    ),
    "st-chp15-p368-prato-beauty-utility-and-enlightenment": (
        False,
        "This is Haskell's broad evaluative characterization of the Prà scheme as an attempt to combine beauty and utility and address an Enlightenment concern; the current candidate endpoints do not identify that abstract problem as a distinct entity relation.",
        None,
    ),
    "st-chp15-p368-memmo-political-ambition-declines": (
        True,
        "Haskell explicitly links the parallel decline of Memmo's political ambitions and Venice's fortunes. Preserve the comparison and do not turn 'with' into a specific causal mechanism.",
        None,
    ),
    "st-chp15-p368-memmo-forty-eight-paintings": (
        False,
        "This is a qualified scalar characterization of Memmo's interest in painting, not a relation to a specific artwork, artist, or institution; preserve Haskell's 'seems' wording.",
        None,
    ),
    "st-chp15-p368-memmo-open-house-until-death": (
        True,
        "Haskell reports a recurring social practice at Memmo's family palace, with his brothers and unnamed guests present. The event and palace are distinct endpoints; the brothers and guests remain separate open groups.",
        None,
    ),
    "st-chp15-p368-farsetti-memmo-public-service-patronage": (
        True,
        "Haskell explicitly connects Farsetti's arts patronage with civic service in Venice and Padua. Keep the civic-service concept distinct from the p.364 public-service conception pending later identity comparison.",
        None,
    ),
    "st-chp15-p368-querini-emerges-as-major-venetian-patron": (
        False,
        "Calling Querini the 'last important patron' to emerge in Venice is Haskell's historical ranking, not a discrete relation to the city.",
        None,
    ),
    "st-chp15-p368-querini-private-art-public-interest": (
        False,
        "This characterizes the private scope of Querini's interest in art; it does not identify a separate relation or public actor.",
        None,
    ),
    "st-chp15-p368-querini-scholar-gentleman-ideal": (
        True,
        "Haskell explicitly presents Querini's later life as an example of the source-defined scholar-gentleman ideal; preserve the evaluative attribution and do not convert it into an occupational classification.",
        None,
    ),
    "st-chp15-p368-querini-born-and-admired-lodoli": (
        False,
        "This records Querini's birth year as a scalar biographical property; his admiration for Lodoli is represented in a separate statement.",
        None,
    ),
    "st-chp15-p368-memmo-public-service-patronage": (
        True,
        "Haskell explicitly connects Memmo's arts patronage with civic service in Venice and Padua. Keep the civic-service concept distinct from the p.364 public-service conception pending later identity comparison.",
        None,
    ),
    "st-chp15-p368-querini-enlightened-views-comparison": (
        False,
        "This compares the extent of Querini's views with Farsetti and Memmo; it is Haskell's intellectual ranking, not a social or institutional relation among the patrons.",
        None,
    ),
    "st-chp15-p368-querini-public-interest-accusation": (
        True,
        "Haskell reports an accusation that Querini advanced his own interests at the public's expense. Keep the allegation attributed and connect it only to the source-bounded public collective; the accusers and affected individuals remain unknown.",
        None,
    ),
    "st-chp15-p368-querini-earlier-life-stormy": (
        False,
        "This is Haskell's comparative characterization of Querini's earlier life, not a relation between independently identified entities.",
        None,
    ),
    "st-chp15-p368-querini-successful-political-career": (
        False,
        "This describes Querini's political career as successful without naming an office, institution, or other relation endpoint; retain it as an attributed biographical assessment.",
        None,
    ),
    "st-chp15-p368-querini-authorities-difficulties": (
        True,
        "Haskell explicitly reports Querini's difficulties with unnamed authorities. Keep the authorities as a source-bounded open institution candidate and do not equate them with the State Inquisition before the subsequent dispute passage is assessed.",
        None,
    ),
    "st-chp15-p368-querini-first-notoriety-1761": (
        True,
        "Haskell links Querini's first notoriety to the 1761 constitutional crisis represented by the existing event candidate; preserve the source's attribution and temporal scope.",
        None,
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12237",
        "canonical_name": "Civic service linked to arts patronage in Venice and Padua (Haskell p.368)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-defined concept linking Farsetti's and Memmo's arts patronage with their services to the public life of Venice and Padua. It does not identify offices or institutions. Keep distinct from cand-10467, the p.364 conception of arts support itself as a public service, pending S3 identity comparison.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L44",
    },
    {
        "candidate_id": "cand-12238",
        "canonical_name": "Public whose interests Querini was accused of advancing his own interests against",
        "suggested_type": "",
        "status": "open",
        "detail": "Source-bounded collective referred to as 'the public' in the accusation Haskell reports. The passage gives no members, institution, or accuser; do not treat the allegation as independently established.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L45",
    },
    {
        "candidate_id": "cand-12239",
        "canonical_name": "Unidentified authorities involved in Querini's early political difficulties",
        "suggested_type": "institution",
        "status": "open",
        "detail": "Haskell refers to 'the authorities' but does not identify the body or office. A later sentence introduces the State Inquisition as the focus of the 1761 dispute; do not assume it is the same authority without explicit evidence.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L46",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_hashes() -> None:
    paths = {"statements": STATEMENTS, "candidates": CANDIDATES, "mentions": MENTIONS, "source": SOURCE, "pdf": PDF}
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
    parser = argparse.ArgumentParser(description="Classify remaining p.368 S2 relation candidates.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="Validate and print changes without writing (default).")
    mode.add_argument("--apply", action="store_true", help="Apply the changes after all preconditions pass.")
    args = parser.parse_args()

    require_hashes()
    statement_rows = load_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_bom = load_csv(CANDIDATES)
    mention_fields, mention_rows, mention_bom = load_csv(MENTIONS)

    segment_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    by_id = {row["statement_id"]: row for row in segment_rows}
    if len(segment_rows) != 31:
        raise SystemExit(f"Expected 31 statements in p.368 segment, found {len(segment_rows)}")
    unset_ids = {row["statement_id"] for row in segment_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset_ids != set(DECISIONS):
        raise SystemExit(f"Unset statement set changed: {sorted(unset_ids ^ set(DECISIONS))}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_rows) != 14:
        raise SystemExit("Expected exactly 14 already-classified true relation candidates")
    if any(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_rows):
        raise SystemExit("Unexpected pre-existing false classification in this segment")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row.get("candidate_id", "").startswith("cand-"))
    if max_candidate != 12236:
        raise SystemExit(f"Candidate ID ceiling changed: cand-{max_candidate}")
    if any(row["candidate_id"] in candidate_by_id for row in NEW_CANDIDATES):
        raise SystemExit("A proposed candidate ID already exists")

    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    new_mention_ids = [
        "m-chp15-p368-querini-0052",
        "m-chp15-p368-querini-0053",
        "m-chp15-p368-querini-0054",
    ]
    if any(mention_id in mention_by_id for mention_id in new_mention_ids):
        raise SystemExit("A proposed p.368 mention ID already exists")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[37:47])
    if not segment_text.startswith("[Page 368]\n"):
        raise SystemExit("Source segment boundary changed")
    known = mention_by_id.get("m-chp15-p368-querini-0001")
    if not known or known.get("start_char") != "11" or segment_text[11:16] != known.get("surface_form"):
        raise SystemExit("Known source-span anchor no longer matches p.368 segment text")

    service_phrase = "their services to the public life of Venice and Padua"
    service_span = phrase_span(segment_text, service_phrase)
    accusation_context = "those of the public"
    accusation_start, accusation_end = phrase_span(segment_text, accusation_context)
    public_start = accusation_start + len("those of ")
    public_end = accusation_end
    authority_span = phrase_span(segment_text, "the authorities")
    new_mentions = [
        {
            "mention_id": new_mention_ids[0], "segment_id": SEGMENT_ID, "candidate_id": "cand-12237",
            "surface_form": service_phrase, "start_char": str(service_span[0]), "end_char": str(service_span[1]),
            "note": "Source concept linking both patrons' arts patronage with civic service; it does not name a formal office or institution.",
        },
        {
            "mention_id": new_mention_ids[1], "segment_id": SEGMENT_ID, "candidate_id": "cand-12238",
            "surface_form": "the public", "start_char": str(public_start), "end_char": str(public_end),
            "note": "Source-bounded collective whose interests are said to have been subordinated in the reported accusation; no members or accuser are named.",
        },
        {
            "mention_id": new_mention_ids[2], "segment_id": SEGMENT_ID, "candidate_id": "cand-12239",
            "surface_form": "the authorities", "start_char": str(authority_span[0]), "end_char": str(authority_span[1]),
            "note": "Unidentified authorities in Querini's early political difficulties; do not equate them with the State Inquisition without explicit evidence.",
        },
    ]

    endpoint_updates = {
        "st-chp15-p368-memmo-open-house-until-death": {"object_candidate_id": "cand-10517"},
        "st-chp15-p368-farsetti-memmo-public-service-patronage": {"object_candidate_id": "cand-12237"},
        "st-chp15-p368-memmo-public-service-patronage": {"object_candidate_id": "cand-12237"},
        "st-chp15-p368-querini-public-interest-accusation": {"object_candidate_id": "cand-12238"},
        "st-chp15-p368-querini-authorities-difficulties": {"object_candidate_id": "cand-12239"},
    }
    for statement_id, changes in endpoint_updates.items():
        if statement_id not in by_id:
            raise SystemExit(f"Missing statement for endpoint update: {statement_id}")
        by_id[statement_id].update(changes)

    candidate_mentions = {
        "st-chp15-p368-farsetti-memmo-public-service-patronage": "cand-12237",
        "st-chp15-p368-memmo-public-service-patronage": "cand-12237",
        "st-chp15-p368-querini-public-interest-accusation": "cand-12238",
        "st-chp15-p368-querini-authorities-difficulties": "cand-12239",
    }
    for statement_id, candidate_id in candidate_mentions.items():
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

    candidate_rows.extend({field: row.get(field, "") for field in candidate_fields} for row in NEW_CANDIDATES)
    mention_rows.extend(new_mentions)

    true_count = sum(is_relation for is_relation, _, _ in DECISIONS.values())
    false_count = len(DECISIONS) - true_count
    print(f"Segment: {SEGMENT_ID}; remaining classifications: {len(DECISIONS)} ({true_count} true, {false_count} false)")
    print("New source-bounded candidates: cand-12237 civic-service concept, cand-12238 public collective, cand-12239 unidentified authorities")
    for row in new_mentions:
        print(f"Mention {row['mention_id']}: {row['surface_form']!r} [{row['start_char']},{row['end_char']}) -> {row['candidate_id']}")
    print("Endpoint updates:")
    for statement_id, changes in endpoint_updates.items():
        print(f"  {statement_id}: {changes}")

    if not args.apply:
        print("PREVIEW ONLY; no files written.")
        return

    backup_suffix = ".bak-s2-ch15-p368-classification-20261015"
    targets = [STATEMENTS, CANDIDATES, MENTIONS]
    backups = [path.with_name(path.name + backup_suffix) for path in targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A recovery backup already exists; inspect it before applying")
    payloads = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statement_rows) + "\n").encode("utf-8"),
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
