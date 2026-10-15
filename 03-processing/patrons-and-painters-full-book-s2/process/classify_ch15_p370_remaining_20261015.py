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
PAGE_IMAGE = ROOT / "scripts/.tmp_active_s2_chp15_p370_20261004.png"
SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l61-67"

EXPECTED_HASHES = {
    "statements": "5f2ba785bd1245907df9b718dd3851404c1c21d9aa2f71e153dd84ad0406fac8",
    "candidates": "46b30db712bb9c0e66bfefd920193dd4f377895d6c05f217cd1bd52eda5ac6b7",
    "mentions": "682f33c982afe88c1cb1d1103575b752c7b810f4126f4545ab407c21d5b25ba6",
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "pdf": "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
    "page_image": "d51e4233565769dc393f84d151f04eeef5c29f8f643480aaa3ec5488e4a0b795",
}

# True means an evidence-supported S2 relation candidate, not an S6 formal edge.
DECISIONS: dict[str, tuple[bool, str, str | None]] = {
    "st-chp15-p370-alticchiero-decoration-combined-with-utility": (
        False,
        "This is Haskell's general design summary of the villa's decorative and practical qualities, not a relation between independently identified entities.",
        None,
    ),
    "st-chp15-p370-bacon-as-enlightenment-founder": (
        True,
        "Haskell explicitly characterizes Francis Bacon as a founding father of the Enlightenment; retain the source-attributed intellectual association without treating it as an independently verified historical conclusion.",
        None,
    ),
    "st-chp15-p370-querini-garden-as-expression-of-taste": (
        True,
        "Haskell explicitly compares the garden with the house as an expression of Querini's taste. Preserve this as Haskell's interpretation, not an independently established preference ranking.",
        None,
    ),
    "st-chp15-p370-alticchiero-garden-formal-and-agreeable-confusion": (
        False,
        "This is a visual description of the garden's layout and planting, not a relation between separately identified entities.",
        None,
    ),
    "st-chp15-p370-youngs-night-thoughts-romantic-influence": (
        True,
        "Haskell explicitly reports the European romantic reception of Young's Night Thoughts; the audience and specific reading evidence are not identified.",
        None,
    ),
    "st-chp15-p370-garden-allegory-philosophers-way-of-life": (
        True,
        "Haskell explicitly interprets the main garden as an allegory of the philosopher's way of life; preserve the interpretive attribution and the existing term endpoint.",
        None,
    ),
    "st-chp15-p370-querini-aristocratic-cast-and-1761-downfall": (
        False,
        "This is Haskell's inference about Querini's character from his choice of Phocion, not a relation between independently identified entities.",
        None,
    ),
    "st-chp15-p370-other-altars-material": (
        True,
        "Haskell explicitly says the other altars were formed from antique sculpture or modern imitations; preserve the material relationship at the sculpture-programme level.",
        "The individual antique sculptures and modern imitations are not identified, so no item-level source-work endpoint can be assigned.",
    ),
    "st-chp15-p370-wynne-reflects-on-eastern-veneration": (
        True,
        "Haskell reports that the bust prompted Wynne to reflect on a stated idea of veneration for the mad in the East; this records her reported reflection, not an independently verified cultural practice.",
        None,
    ),
    "st-chp15-p370-epicurus-epithet-and-reception": (
        False,
        "The French phrase is an epithet describing Epicurus, not a relation to a separately identified entity; the reception claim is split into its own statement.",
        None,
    ),
    "st-chp15-p370-phocion-epithet-and-stance": (
        False,
        "The French phrase is an epithet describing Phocion, not a relation to a separately identified entity; the claim about standing against the mob is split into its own statement.",
        None,
    ),
    "st-chp15-p370-populace-recognized-reform-harm": (
        True,
        "Haskell attributes to the source-described populace a perception that Querini's proposed reforms would harm their interests; preserve this as reported opinion, not verified population-wide belief.",
        None,
    ),
    "st-chp15-p370-populace-rejoiced-at-querini-downfall": (
        True,
        "Haskell reports that the populace rejoiced at Querini's 1761 downfall. Keep 'downfall' as the source's wording and do not equate it with the separately recorded arrest or detention.",
        None,
    ),
    "st-chp15-p370-wynne-recalled-proverbial-link": (
        True,
        "Haskell reports Wynne's recollection of a proverbial association between madness, prophets, and poets; preserve it as a reported idea rather than a general cultural fact.",
        None,
    ),
    "st-chp15-p370-cabane-as-romantic-expression": (
        False,
        "This is Haskell's aesthetic interpretation of the garden design, not a relation between independently identified entities.",
        None,
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12241",
        "canonical_name": "The populace in Haskell's account of Querini's 1761 downfall",
        "suggested_type": "",
        "status": "open",
        "detail": "Source-bounded collective referred to as 'the populace' in Haskell's account of Querini's proposed reforms and 1761 downfall. Members and institutional boundaries are not given; do not identify this group with the public mentioned in the separate p.368 accusation without evidence.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L65",
    },
    {
        "candidate_id": "cand-12242",
        "canonical_name": "Reported Eastern veneration of the mad in Mme Rosenberg's reflection",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-defined idea in Haskell's report of Wynne's thought. 'The East' is broad, and the reported belief is not independently verified; do not treat it as a general fact about Eastern societies.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L67",
    },
    {
        "candidate_id": "cand-12243",
        "canonical_name": "Proverbial association of the mad with prophets and poets as reported by Haskell",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-defined proverbial idea in Haskell's account of Wynne's recollection. The proverb and its tradition are not identified; preserve it as a reported reflection, not an independently verified cultural generalization.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L67",
    },
]

NEW_MENTIONS = [
    ("m-chp15-p370-alticchiero-0050", "cand-12241", "the populace", "Source-bounded collective named in Haskell's report of Querini's 1761 downfall."),
    ("m-chp15-p370-alticchiero-0051", "cand-12242", "the veneration felt in the East for the mad", "Idea reported through Wynne's reflection; the broad cultural claim is not independently verified."),
    ("m-chp15-p370-alticchiero-0052", "cand-12243", "their proverbial relationship with prophets and poets", "Wynne's reported recollection of an unnamed proverbial association."),
]

NEW_STATEMENTS = {
    "st-chp15-p370-epicurus-misunderstood-by-vulgar-minds": {
        "statement_id": "st-chp15-p370-epicurus-misunderstood-by-vulgar-minds",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0977",
        "object_candidate_id": None,
        "predicate": "misunderstood_by_vulgar_minds",
        "qualifiers": {
            "source_line_start": 64,
            "source_line_end": 64,
            "printed_page": 370,
            "pdf_physical_page": 10,
            "claim": "Haskell says Epicurus was much misunderstood by vulgar minds.",
            "speaker": "Haskell",
            "text_layer": "authorial report",
            "qualification": "The audience is a rhetorical, generic description and is not an independently identified group.",
            "mentioned_candidate_ids": ["cand-0977"],
            "relation_candidate": True,
            "relation_candidate_note": "Haskell explicitly reports a reception relationship between Epicurus and a generic audience.",
            "open_endpoint_reason": "'Vulgar minds' is a generic rhetorical audience, not an independently identifiable group; preserve the attributed reception claim without inventing a group entity.",
        },
        "original_quote": "so much misunderstood by vulgar minds",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
    },
    "st-chp15-p370-phocion-stood-out-against-ignorant-mob": {
        "statement_id": "st-chp15-p370-phocion-stood-out-against-ignorant-mob",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-10556",
        "object_candidate_id": None,
        "predicate": "stood_out_against_ignorant_mob",
        "qualifiers": {
            "source_line_start": 65,
            "source_line_end": 65,
            "printed_page": 370,
            "pdf_physical_page": 10,
            "claim": "Haskell describes Phocion as having dared to stand out against the ignorant mob.",
            "speaker": "Haskell",
            "text_layer": "authorial report",
            "qualification": "This is Haskell's characterization of Phocion and the crowd.",
            "mentioned_candidate_ids": ["cand-10556"],
            "relation_candidate": True,
            "relation_candidate_note": "Haskell explicitly relates Phocion's stance to a generically described crowd.",
            "open_endpoint_reason": "The 'ignorant mob' is a rhetorical, unnamed crowd with no independently identifiable membership; preserve the attributed relation without inventing a group entity.",
        },
        "original_quote": "the man who had dared to stand out against the ignorant mob",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
    },
}


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
    parser = argparse.ArgumentParser(description="Classify remaining p.370 S2 statements.")
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
    if len(segment_rows) != 52:
        raise SystemExit(f"Expected 52 existing statements in p.370 segment, found {len(segment_rows)}")
    unset_ids = {row["statement_id"] for row in segment_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset_ids != set(DECISIONS):
        raise SystemExit(f"Unset statement set changed: {sorted(unset_ids ^ set(DECISIONS))}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_rows) != 37:
        raise SystemExit("Expected exactly 37 already-classified true relation candidates")
    if any(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_rows):
        raise SystemExit("Unexpected pre-existing false classification in this segment")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row.get("candidate_id", "").startswith("cand-"))
    proposed_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if max_candidate != 12240 or proposed_candidate_ids.intersection(candidate_by_id):
        raise SystemExit(f"Candidate ID ceiling or proposed IDs changed: cand-{max_candidate}")

    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    proposed_mention_ids = [row[0] for row in NEW_MENTIONS]
    if any(mention_id in mention_by_id for mention_id in proposed_mention_ids):
        raise SystemExit("A proposed p.370 mention ID already exists")
    if set(NEW_STATEMENTS).intersection(by_id):
        raise SystemExit("A proposed split statement ID already exists")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(lines[60:67])
    if not segment_text.startswith("[Page 370]\n"):
        raise SystemExit("Source segment boundary changed")
    mention_spans = [phrase_span(segment_text, phrase) for _, _, phrase, _ in NEW_MENTIONS]
    if phrase_span(segment_text, "le Philosophe de la sage volupté") is None:
        raise SystemExit("Epicurus epithet is missing from the source segment")
    if phrase_span(segment_text, "Philosophe Citoyen") is None:
        raise SystemExit("Phocion epithet is missing from the source segment")
    if phrase_span(segment_text, "so much misunderstood by vulgar minds") is None:
        raise SystemExit("Epicurus reception phrase is missing from the source segment")
    if phrase_span(segment_text, "the man who had dared to stand out against the ignorant mob") is None:
        raise SystemExit("Phocion stance phrase is missing from the source segment")

    endpoint_updates = {
        "st-chp15-p370-wynne-reflects-on-eastern-veneration": {
            "object_candidate_id": "cand-12242",
            "predicate": "reflected_on_reported_eastern_veneration_of_the_mad",
        },
        "st-chp15-p370-populace-recognized-reform-harm": {
            "subject_candidate_id": "cand-2075",
            "object_candidate_id": "cand-12241",
            "predicate": "querini_proposed_reforms_seen_by_populace_as_adverse_to_their_interests",
        },
        "st-chp15-p370-populace-rejoiced-at-querini-downfall": {
            "subject_candidate_id": "cand-12241",
            "object_candidate_id": "cand-2075",
            "predicate": "populace_rejoiced_at_querini_downfall_in_1761",
        },
        "st-chp15-p370-wynne-recalled-proverbial-link": {
            "object_candidate_id": "cand-12243",
            "predicate": "recalled_proverbial_association_of_mad_with_prophets_and_poets",
        },
    }
    for statement_id, changes in endpoint_updates.items():
        if statement_id not in by_id:
            raise SystemExit(f"Missing statement for endpoint update: {statement_id}")
        by_id[statement_id].update(changes)

    by_id["st-chp15-p370-epicurus-epithet-and-reception"].update(
        predicate="given_epithet_philosopher_of_wise_pleasure",
        original_quote="le Philosophe de la sage volupté",
    )
    by_id["st-chp15-p370-epicurus-epithet-and-reception"]["qualifiers"].update(
        claim="Haskell gives Epicurus the French epithet 'philosopher of wise pleasure'.",
        qualification="The French epithet is reproduced as printed; this is Haskell's characterization.",
    )
    by_id["st-chp15-p370-phocion-epithet-and-stance"].update(
        predicate="given_epithet_citizen_philosopher",
        original_quote="Philosophe Citoyen",
    )
    by_id["st-chp15-p370-phocion-epithet-and-stance"]["qualifiers"].update(
        claim="Haskell calls Phocion 'the citizen philosopher'.",
        qualification="This is Haskell's epithet for Phocion; his described stance against the mob is recorded separately.",
    )

    for statement_id, candidate_id in [
        ("st-chp15-p370-wynne-reflects-on-eastern-veneration", "cand-12242"),
        ("st-chp15-p370-populace-recognized-reform-harm", "cand-12241"),
        ("st-chp15-p370-populace-rejoiced-at-querini-downfall", "cand-12241"),
        ("st-chp15-p370-wynne-recalled-proverbial-link", "cand-12243"),
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

    new_by_id = NEW_STATEMENTS
    for statement_id, new_row in new_by_id.items():
        is_relation, note, open_reason = (True, new_row["qualifiers"]["relation_candidate_note"], new_row["qualifiers"].get("open_endpoint_reason"))
        new_row["qualifiers"]["relation_candidate"] = is_relation
        new_row["qualifiers"]["relation_candidate_note"] = note
        if open_reason:
            new_row["qualifiers"]["open_endpoint_reason"] = open_reason

    # Insert each split atom immediately after its source statement.
    expanded_statements: list[dict] = []
    for row in statement_rows:
        expanded_statements.append(row)
        if row.get("statement_id") == "st-chp15-p370-epicurus-epithet-and-reception":
            expanded_statements.append(NEW_STATEMENTS["st-chp15-p370-epicurus-misunderstood-by-vulgar-minds"])
        elif row.get("statement_id") == "st-chp15-p370-phocion-epithet-and-stance":
            expanded_statements.append(NEW_STATEMENTS["st-chp15-p370-phocion-stood-out-against-ignorant-mob"])

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

    segment_after = [row for row in expanded_statements if row.get("segment_id") == SEGMENT_ID]
    true_count = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_after)
    false_count = sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_after)
    unset_count = sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in segment_after)
    if (true_count, false_count, unset_count, len(segment_after)) != (48, 6, 0, 54):
        raise SystemExit(f"Unexpected post-classification counts: {true_count}/{false_count}/{unset_count}/{len(segment_after)}")

    print(f"Segment: {SEGMENT_ID}; classified 15 original unset statements and split 2 compound claims.")
    print(f"Segment after: {len(segment_after)} statements ({true_count} true, {false_count} false, {unset_count} unset).")
    print("New candidates:")
    for candidate in NEW_CANDIDATES:
        print(f"  {candidate['candidate_id']}: {candidate['canonical_name']}")
    print("New exact-span mentions:")
    for mention_spec, span in zip(NEW_MENTIONS, mention_spans):
        print(f"  {mention_spec[0]} -> {mention_spec[1]}: {mention_spec[2]!r} [{span[0]},{span[1]})")
    print("New atomic statements:")
    for statement_id, row in NEW_STATEMENTS.items():
        print(f"  {statement_id}: {row['predicate']} [{row['original_quote']}]")
    print("Endpoint updates:")
    for statement_id, changes in endpoint_updates.items():
        print(f"  {statement_id}: {changes}")

    if not args.apply:
        print("PREVIEW ONLY; no files written.")
        return

    backup_suffix = ".bak-s2-ch15-p370-classification-20261015"
    targets = [STATEMENTS, CANDIDATES, MENTIONS]
    backups = [path.with_name(path.name + backup_suffix) for path in targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A recovery backup already exists; inspect it before applying")
    payloads = {
        STATEMENTS: encode_jsonl(expanded_statements),
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
