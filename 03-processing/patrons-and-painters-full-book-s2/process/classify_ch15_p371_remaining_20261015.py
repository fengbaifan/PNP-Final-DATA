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
PAGE_IMAGE = ROOT / "scripts/.tmp_active_s2_chp15_p371_20261004.png"
SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l69-83"

EXPECTED_HASHES = {
    "statements": "e2bb11a9c4b17d24e69394e5da7142dd23e14423b98d44f6933b71f5f4cf97dc",
    "candidates": "57de0c56ba43206e6974d5445646f9c2d6f2d3b94677be4800e6b064985439d0",
    "mentions": "71c73c4a91821aba6009beb0b00e9a6754eabc39b4bde4462daec69b25c7f7a9",
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "pdf": "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
    "page_image": "e3b2bcc6a215270217cd208dff50101ffe66981d0689f37e73377231084945ac",
}

DECISIONS: dict[str, tuple[bool, str]] = {
    "st-chp15-p371-querini-alter-spirits-and-mme-characterization": (
        True,
        "Haskell reports Mme Rosenberg's characterization of Querini's soul; retain the attribution and the existing source-bounded outlook term.",
    ),
    "st-chp15-p371-vices-depicted-after-apelles-pliny": (
        False,
        "This aggregate sentence is already represented by separate statements for each vice depicted, the relief's relation to Apelles' composition, and Pliny's record of that composition; it adds no distinct relation endpoint.",
    ),
    "st-chp15-p371-mme-rosenberg-distrust-of-allegory": (
        True,
        "Haskell reports Mme Rosenberg's response to allegory as a representational mode; retain her stated contrast between painted ceilings and sculpture without generalizing it to all viewers.",
    ),
    "st-chp15-p371-querini-garden-allegories-straightforward": (
        True,
        "Haskell reports that Mme Rosenberg found the allegories in Querini's garden straightforward; preserve this attributed response and the garden endpoint.",
    ),
    "st-chp15-p371-sculpture-collection-assessment-limit": (
        False,
        "This records Haskell's stated limit on what he can infer from Rosenberg's illustrations, not a relation between independently identified entities.",
    ),
    "st-chp15-p371-de-non-engraver-and-collector": (
        False,
        "This is a biographical role and evaluative description of De Non; the statement remains available as a source claim but is not a relation between identified entities.",
    ),
    "st-chp15-p371-de-non-appealed-to-querini": (
        False,
        "Haskell's phrase 'well qualified to appeal' is an explanatory judgment about suitability, not a claim that an actual appeal or influence occurred; the separate statement that De Non moved in Querini's circle records the supported social relation.",
    ),
    "st-chp15-p371-literary-inspiration-and-renaissance-art-life": (
        False,
        "This is Haskell's broad interpretive synthesis about Querini's literary inspiration and way of living with art; the specific association with Renier and Canova commission are recorded separately.",
    ),
    "st-chp15-p371-querini-sacrifice-evil-and-good-spirits": (
        True,
        "Haskell reports, through Mme Rosenberg, Querini's belief that sacrifice to both good and evil spirits could bring happiness; preserve this as an attributed belief, not an independently established practice.",
    ),
    "st-chp15-p371-villa-attracted-enormous-attention": (
        False,
        "This is a qualitative narrative summary without an identified audience or other relation endpoint.",
    ),
    "st-chp15-p371-querini-antique-restraint": (
        True,
        "Haskell reports Querini's view that restraint and lack of excess characterized the antique; preserve it as Querini's attributed aesthetic interpretation.",
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12244",
        "canonical_name": "Querini's reported belief in sacrifice to good and evil spirits for happiness",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-defined belief reported by Haskell through Mme Rosenberg. Do not infer a specific ritual, institution, or independently verified practice.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L71",
    },
    {
        "candidate_id": "cand-12245",
        "canonical_name": "Restraint and lack of excess as Querini's view of the antique",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-defined aesthetic interpretation attributed by Haskell to Querini; it describes how he understood the antique, not an independently established property of all ancient art.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L76",
    },
    {
        "candidate_id": "cand-12246",
        "canonical_name": "Famous composition by Apelles recorded by Pliny (work identity unspecified)",
        "suggested_type": "work",
        "status": "open",
        "detail": "The source says the Alticchiero bas-relief was based on a famous composition by Apelles as recorded by Pliny. The composition's title, subject identity, and surviving work are not independently identified here.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L72",
    },
]

NEW_MENTIONS = [
    ("m-chp15-p371-querini-0059", "cand-12244", "sacrifice to evil as well as to good spirits", "Querini's reported belief, mediated through Mme Rosenberg and Haskell."),
    ("m-chp15-p371-querini-0060", "cand-12245", "a restraint and lack of excess", "Aesthetic interpretation attributed to Querini by Haskell."),
    ("m-chp15-p371-querini-0061", "cand-12246", "the famous composition", "Unidentified work by Apelles as described through Pliny's record."),
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
    parser = argparse.ArgumentParser(description="Classify remaining p.371 S2 statements and repair source-work endpoints.")
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
    if len(segment_rows) != 49:
        raise SystemExit(f"Expected 49 statements in p.371 segment, found {len(segment_rows)}")
    unset_ids = {row["statement_id"] for row in segment_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset_ids != set(DECISIONS):
        raise SystemExit(f"Unset statement set changed: {sorted(unset_ids ^ set(DECISIONS))}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_rows) != 38:
        raise SystemExit("Expected exactly 38 already-classified true relation candidates")
    if any(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_rows):
        raise SystemExit("Unexpected pre-existing false classification in this segment")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row.get("candidate_id", "").startswith("cand-"))
    proposed_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if max_candidate != 12243 or proposed_candidate_ids.intersection(candidate_by_id):
        raise SystemExit(f"Candidate ID ceiling or proposed IDs changed: cand-{max_candidate}")

    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    proposed_mention_ids = [row[0] for row in NEW_MENTIONS]
    if any(mention_id in mention_by_id for mention_id in proposed_mention_ids):
        raise SystemExit("A proposed p.371 mention ID already exists")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(lines[68:83])
    if not segment_text.startswith("[Page 371]\n"):
        raise SystemExit("Source segment boundary changed")
    mention_spans = [phrase_span(segment_text, phrase) for _, _, phrase, _ in NEW_MENTIONS]
    if phrase_span(segment_text, "bas-relief based on the famous composition of") is None:
        raise SystemExit("Apelles composition phrase is missing from the source segment")

    endpoint_updates = {
        "st-chp15-p371-mme-rosenberg-distrust-of-allegory": {
            "object_candidate_id": "cand-11542",
            "predicate": "mme_rosenberg_distrusted_allegory_and_found_sculptural_allegory_easier_to_understand",
        },
        "st-chp15-p371-querini-sacrifice-evil-and-good-spirits": {
            "object_candidate_id": "cand-12244",
            "predicate": "believed_sacrifice_to_good_and_evil_spirits_for_happiness",
        },
        "st-chp15-p371-querini-antique-restraint": {
            "object_candidate_id": "cand-12245",
            "predicate": "attributed_restraint_and_lack_of_excess_to_antiquity",
        },
        "st-chp15-p371-relief-based-on-apelles-composition": {
            "object_candidate_id": "cand-12246",
        },
        "st-chp15-p371-pliny-recorded-apelles-composition": {
            "object_candidate_id": "cand-12246",
        },
    }
    for statement_id, changes in endpoint_updates.items():
        if statement_id not in by_id:
            raise SystemExit(f"Missing statement for endpoint update: {statement_id}")
        by_id[statement_id].update(changes)

    for statement_id, candidate_id in [
        ("st-chp15-p371-querini-sacrifice-evil-and-good-spirits", "cand-12244"),
        ("st-chp15-p371-querini-antique-restraint", "cand-12245"),
        ("st-chp15-p371-relief-based-on-apelles-composition", "cand-12246"),
        ("st-chp15-p371-pliny-recorded-apelles-composition", "cand-12246"),
    ]:
        ids = by_id[statement_id]["qualifiers"].setdefault("mentioned_candidate_ids", [])
        if candidate_id not in ids:
            ids.append(candidate_id)

    for statement_id, (is_relation, note) in DECISIONS.items():
        qualifiers = by_id[statement_id]["qualifiers"]
        qualifiers["relation_candidate"] = is_relation
        qualifiers["relation_candidate_note"] = note
        if not is_relation:
            qualifiers.pop("open_endpoint_reason", None)

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
    if (true_count, false_count, unset_count, len(segment_after)) != (43, 6, 0, 49):
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

    backup_suffix = ".bak-s2-ch15-p371-classification-20261015"
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
