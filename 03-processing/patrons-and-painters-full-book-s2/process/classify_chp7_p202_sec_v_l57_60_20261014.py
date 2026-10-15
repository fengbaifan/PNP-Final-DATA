from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_v.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-7.pdf"
SEGMENT = "chp-7:07_CHP-7_sec_v:l57-60"
EXPECTED_SEGMENT_SHA = "23f500dd20ab35e415f6e3d39bf8df9580d68fddfa74e3a502d05076458ee825"
CITY_GROUP = "cand-12005"
CITY_MENTION = "m-chp7-p201-p202-106"
BACKUP_SUFFIX = ".bak-s2-chp7-p202-sec-v-l57-60-20261014"

EXPECTED_HASHES = {
    STATEMENTS.name: "d38d747d9988c4e9b4806b00bbc23bdb26cfd89c13e94217a289810016d6c1e9",
    CANDIDATES.name: "9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d",
    MENTIONS.name: "40821fb7d0e896dac7ddfb5b3c61e798fb46ee42109c7007fb714401d9b6244d",
    SEGMENTS.name: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE.name: "956054d03a849749a1f7a0dbf0eade81c5cb1252a284cc26d024a7f9f134b432",
    PDF.name: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
}

TRUE_NOTES = {
    "st-chp7-p202-v-baroque-conquest-transition": "This preserves Haskell's metaphorical account of Vienna as the last conquest of the Baroque during changing values; it is not a literal conquest or a claim of universal stylistic termination.",
    "st-chp7-p202-v-savoy-transformed-after-war": "This records Haskell's claim that Savoy emerged transformed from the War of the Spanish Succession; the accompanying artistic flowering is represented separately.",
    "st-chp7-p202-v-smaller-towns-anticipated-turin": "This records Haskell's statement that unnamed smaller provincial towns had anticipated Turin's artist-attraction policy; the source defers their identification.",
    "st-chp7-p202-v-turin-attracted-painters-or-pictures": "This records the Turin policy with its explicit actor, co-actor, destination, source-city group, and unresolved disjunction between painters and their pictures.",
    "st-chp7-p202-v-turin-recruitment-failures": "This records Haskell's account of failed attempts to recruit artists for Turin and repeated refusals to travel north; individual artists and attempts remain unidentified.",
    "st-chp7-p202-v-victor-amadeus-and-juvarra-change-turin": "This records Victor Amadeus's change to Turin's artistic situation with Juvarra's help; the quoted epithet does not establish a formal office.",
}

FALSE_NOTES = {
    "st-chp7-p202-v-savoy-dukes-preferred-hunting-and-military": "This is Haskell's generalized comparative characterization of unnamed dukes' interests, not a relation between distinct identified entities.",
    "st-chp7-p202-v-turin-architecture-and-painting-patronage": "This is a broad evaluative claim about the historical standing of Turin's architecture, not an entity relation; the separate painting-patronage judgment is recorded independently.",
}

EXPECTED_IDS = {
    "st-chp7-p202-v-baroque-conquest-transition",
    "st-chp7-p202-v-savoy-dukes-preferred-hunting-and-military",
    "st-chp7-p202-v-savoy-transformed-after-war",
    "st-chp7-p202-v-smaller-towns-anticipated-turin",
    "st-chp7-p202-v-turin-architecture-and-painting-patronage",
    "st-chp7-p202-v-turin-attracted-painters-or-pictures",
    "st-chp7-p202-v-turin-recruitment-failures",
    "st-chp7-p202-v-victor-amadeus-and-juvarra-change-turin",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def csv_row_bytes(fieldnames: list[str], row: dict[str, str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
    writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes after all guards pass")
    args = parser.parse_args()

    paths = [STATEMENTS, CANDIDATES, MENTIONS, SEGMENTS, SOURCE, PDF]
    raw = {path: path.read_bytes() for path in paths}
    hashes = {path.name: sha(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: {hashes}")

    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES, MENTIONS)]
    if any(path.exists() for path in backups):
        raise SystemExit(f"recovery copy already exists: {[str(path) for path in backups if path.exists()]}")

    source_lines = raw[SOURCE].decode("utf-8").splitlines()
    segment_text = "\n".join(source_lines[56:60])
    city_surface = "a wide variety of more richly endowed cities"
    start = segment_text.find(city_surface)
    if start != 1049 or segment_text[start:start + len(city_surface)] != city_surface:
        raise SystemExit(f"source span moved: {start}")
    for quote in (
        "Savoy was the other continental state which emerged transformed from the war of the Spanish succession",
        "here too victory was accompanied by a wonderful flowering of the arts.",
        "During much of the seventeenth century the architecture of Turin had been of European significance",
        "patronage of painting had been almost laughable in its futility.",
        "Local talent was rare",
        "attempts to attract artists from other towns had met with a long scries of failures. Painter after painter had refused to makejhejourney north",
        "They followed the example of patrons in other uncreative centres",
        "and attracted leading painters, or at least their pictures, from a wide variety of more richly endowed cities.",
    ):
        if quote not in "\n".join(source_lines[56:60]):
            raise SystemExit(f"source quote not found: {quote!r}")

    with SEGMENTS.open("r", encoding="utf-8") as stream:
        segments = [json.loads(line) for line in stream]
    seg = next(row for row in segments if row["segment_id"] == SEGMENT)
    if seg.get("sha256") != EXPECTED_SEGMENT_SHA:
        raise SystemExit("segment hash mismatch")

    with CANDIDATES.open("r", encoding="utf-8-sig", newline="") as stream:
        candidate_reader = csv.DictReader(stream)
        candidate_fields = candidate_reader.fieldnames
        candidates = list(candidate_reader)
    candidate_ids = {row["candidate_id"] for row in candidates}
    if CITY_GROUP in candidate_ids:
        raise SystemExit(f"candidate id already exists: {CITY_GROUP}")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates if row["candidate_id"].startswith("cand-")) != 12004:
        raise SystemExit("candidate id sequence changed")

    with MENTIONS.open("r", encoding="utf-8", newline="") as stream:
        mention_reader = csv.DictReader(stream)
        mention_fields = mention_reader.fieldnames
        mentions = list(mention_reader)
    mention_ids = {row["mention_id"] for row in mentions}
    if CITY_MENTION in mention_ids:
        raise SystemExit(f"mention id already exists: {CITY_MENTION}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8").splitlines()]
    by_id = {row["statement_id"]: row for row in rows}
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT]
    if {row["statement_id"] for row in segment_rows} != EXPECTED_IDS:
        raise SystemExit("p.202 statement set changed")
    if set(TRUE_NOTES) | set(FALSE_NOTES) != EXPECTED_IDS:
        raise SystemExit("classification map does not cover exactly the p.202 source segment")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in segment_rows):
        raise SystemExit("expected all p.202 rows to be unclassified")

    new_ids = {
        "st-chp7-p202-v-savoy-victory-flowering-arts",
        "st-chp7-p202-v-turin-local-artists-rare",
        "st-chp7-p202-v-dukes-resigned-to-patronage-situation",
        "st-chp7-p202-v-turin-painting-patronage-futility",
        "st-chp7-p202-v-victor-juvarra-follow-other-centres",
    }
    if new_ids & by_id.keys():
        raise SystemExit(f"new statement ids already exist: {sorted(new_ids & by_id.keys())}")

    # Refine the two compound claims before classifying the existing rows.
    savoy = by_id["st-chp7-p202-v-savoy-transformed-after-war"]
    savoy["predicate"] = "state_emerged_transformed_from_war_of_spanish_succession"
    sq = dict(savoy.get("qualifiers") or {})
    sq.update({
        "claim": "Haskell says Savoy emerged transformed from the War of the Spanish Succession.",
        "qualification": "The separate statement about victory accompanying a flowering of the arts is linked to this sentence; no specific victory is named.",
    })
    savoy["qualifiers"] = sq

    dukes = by_id["st-chp7-p202-v-savoy-dukes-preferred-hunting-and-military"]
    dukes["object_candidate_id"] = None
    dukes["predicate"] = "successive_dukes_preferred_hunting_and_military_to_art_cultivation"
    dukes["original_quote"] = "successive dukes, who were in any case more addicted to hunting and military pursuits than the cultivation of art"
    dq = dict(dukes.get("qualifiers") or {})
    dq.update({
        "claim": "Haskell characterizes successive dukes of Savoy as more attached to hunting and military pursuits than to cultivating art.",
        "qualification": "This is Haskell's broad comparison of an unnamed group; the separate claim that they seemed resigned to the situation is recorded independently.",
        "open_endpoint_reason": "The source compares interests in hunting, military pursuits, and art cultivation but does not identify these activities as candidate entities.",
    })
    dukes["qualifiers"] = dq

    architecture = by_id["st-chp7-p202-v-turin-architecture-and-painting-patronage"]
    architecture["predicate"] = "turin_architecture_had_european_significance"
    architecture["original_quote"] = "During much of the seventeenth century the architecture of Turin had been of European significance"
    aq = dict(architecture.get("qualifiers") or {})
    aq.update({
        "claim": "Haskell says Turin's architecture had European significance during much of the seventeenth century.",
        "qualification": "This is a broad evaluation of historical standing; 'European significance' is not a distinct entity endpoint.",
    })
    architecture["qualifiers"] = aq

    attracted = by_id["st-chp7-p202-v-turin-attracted-painters-or-pictures"]
    attracted["subject_candidate_id"] = "cand-2388"
    attracted["object_candidate_id"] = None
    attracted["predicate"] = "attracted_painters_or_pictures_from_richer_cities_to_turin"
    attracted["original_quote"] = "and attracted leading painters, or at least their pictures, from a wide variety of more richly endowed cities."
    tq = dict(attracted.get("qualifiers") or {})
    tq.update({
        "claim": "Haskell says Victor Amadeus and Juvarra attracted leading painters, or at least their pictures, from a wide variety of more richly endowed cities to Turin.",
        "qualification": "The grammatical subject is the plural 'they', referring to Victor Amadeus and Juvarra. Preserve the explicit painter/picture alternative; no city, painter, or picture is individually identified.",
        "co_actor_candidate_ids": ["cand-1339"],
        "target_city_candidate_id": "cand-2663",
        "disjunctive_object_candidate_ids": ["cand-7344", "cand-7345"],
        "origin_city_group_candidate_id": CITY_GROUP,
        "open_endpoint_reason": "The source explicitly says 'painters, or at least their pictures'; these different entity types remain alternative objects. Their source cities are an unnamed group recorded by a source-derived candidate.",
    })
    mids = list(tq.get("mentioned_candidate_ids") or [])
    for cid in (CITY_GROUP,):
        append_unique(mids, cid)
    tq["mentioned_candidate_ids"] = mids
    attracted["qualifiers"] = tq

    recruitment = by_id["st-chp7-p202-v-turin-recruitment-failures"]
    recruitment["object_candidate_id"] = "cand-7333"
    recruitment["predicate"] = "attempts_to_recruit_painters_for_turin_failed"
    recruitment["original_quote"] = "attempts to attract artists from other towns had met with a long scries of failures. Painter after painter had refused to makejhejourney north"
    rq = dict(recruitment.get("qualifiers") or {})
    rq.update({
        "claim": "Haskell says repeated attempts to attract artists from other towns to Turin failed, with painter after painter refusing the northward journey.",
        "qualification": "Artists, dates, and individual recruitment attempts remain unidentified; the S0 OCR forms 'scries' and 'makejhejourney' are retained with the existing S2 print corrections.",
    })
    recruitment["qualifiers"] = rq

    changed = by_id["st-chp7-p202-v-victor-amadeus-and-juvarra-change-turin"]
    changed["predicate"] = "changed_turin_artistic_situation_with_help_from_juvarra"
    cq = dict(changed.get("qualifiers") or {})
    cq["assistant_candidate_id"] = "cand-1339"
    cq["affected_place_candidate_id"] = "cand-2663"
    changed["qualifiers"] = cq

    # Link footnote 1 to both atomic claims in the cited sentence.
    citation_id = "st-chp7-p202-n1-cite-claretta"
    citation = by_id[citation_id]
    fq = dict(citation.get("qualifiers") or {})
    for field in ("linked_body_statement_ids", "related_body_statement_ids"):
        body_ids = list(fq.get(field) or [])
        append_unique(body_ids, "st-chp7-p202-v-savoy-victory-flowering-arts")
        fq[field] = body_ids
    citation["qualifiers"] = fq
    refs = [{"marker": 1, "segment_id": "chp-7:07_CHP-7_sec_v:l62-76", "source_line": 76}]
    sq = dict(savoy.get("qualifiers") or {})
    sq.update({"footnote_statement_ids": [citation_id], "footnote_refs": refs, "footnote_body_link_status": "linked"})
    savoy["qualifiers"] = sq

    false_notes = dict(FALSE_NOTES)
    for sid, note in TRUE_NOTES.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        by_id[sid]["qualifiers"] = q
    for sid, note in false_notes.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
        by_id[sid]["qualifiers"] = q

    common = {"segment_id": SEGMENT, "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md", "origin": "book"}
    new_rows = [
        {
            **common, "statement_id": "st-chp7-p202-v-savoy-victory-flowering-arts",
            "subject_candidate_id": "cand-2379", "object_candidate_id": "cand-2502", "predicate": "victory_accompanied_flowering_of_arts",
            "qualifiers": {
                "source_line_start": 59, "source_line_end": 59, "printed_page": 202, "pdf_physical_page": 44,
                "claim": "Haskell says victory in the context of Savoy's transformation was accompanied by a flowering of the arts.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "The passage does not identify a specific victory or state a single causal mechanism; the cited sentence's footnote 1 is linked.",
                "mentioned_candidate_ids": ["cand-2379", "cand-2502"], "footnote_marker": 1,
                "footnote_statement_ids": [citation_id], "footnote_refs": refs, "footnote_body_link_status": "linked",
                "relation_candidate": True,
                "relation_candidate_note": "This separates the arts-flowering clause from the preceding claim that Savoy emerged transformed from the war.",
            },
            "original_quote": "here too victory was accompanied by a wonderful flowering of the arts.1",
        },
        {
            **common, "statement_id": "st-chp7-p202-v-turin-local-artists-rare",
            "subject_candidate_id": "cand-2663", "object_candidate_id": "cand-7332", "predicate": "local_artist_talent_was_rare_in_turin",
            "qualifiers": {
                "source_line_start": 59, "source_line_end": 59, "printed_page": 202, "pdf_physical_page": 44,
                "claim": "Haskell says local artistic talent was rare in Turin.", "speaker": "Haskell", "text_layer": "body",
                "qualification": "The local artists are unnamed; the statement is separate from the failed recruitment of artists from elsewhere.",
                "mentioned_candidate_ids": ["cand-2663", "cand-7332"], "relation_candidate": True,
                "relation_candidate_note": "This records the source's city-to-local-artist-group claim without inferring individual artists.",
            },
            "original_quote": "Local talent was rare",
        },
        {
            **common, "statement_id": "st-chp7-p202-v-dukes-resigned-to-patronage-situation",
            "subject_candidate_id": "cand-7334", "object_candidate_id": None, "predicate": "successive_dukes_seemed_resigned_to_turin_painting_patronage_situation",
            "qualifiers": {
                "source_line_start": 59, "source_line_end": 59, "printed_page": 202, "pdf_physical_page": 44,
                "claim": "Haskell says the successive dukes seemed generally resigned to the situation in Turin.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "Preserve 'seemed' and the unnamed collective subject; this is a separate authorial characterization from their stated interests.",
                "mentioned_candidate_ids": ["cand-7334", "cand-2663"], "relation_candidate": False,
                "relation_candidate_note": "This is a qualified generalized characterization, not a relation between distinct identified entities.",
            },
            "original_quote": "seemed generally resigned to the situation",
        },
        {
            **common, "statement_id": "st-chp7-p202-v-turin-painting-patronage-futility",
            "subject_candidate_id": "cand-2663", "object_candidate_id": None, "predicate": "turin_painting_patronage_characterized_as_futile",
            "qualifiers": {
                "source_line_start": 59, "source_line_end": 59, "printed_page": 202, "pdf_physical_page": 44,
                "claim": "Haskell characterizes Turin's painting patronage as having been futile.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "The wording 'almost laughable in its futility' is Haskell's evaluative judgment, not a measured outcome.",
                "mentioned_candidate_ids": ["cand-2663"], "relation_candidate": False,
                "relation_candidate_note": "This is an evaluative historical description without a distinct relation endpoint.",
            },
            "original_quote": "patronage of painting had been almost laughable in its futility.",
        },
        {
            **common, "statement_id": "st-chp7-p202-v-victor-juvarra-follow-other-centres",
            "subject_candidate_id": "cand-2388", "object_candidate_id": "cand-7335", "predicate": "followed_example_of_patrons_in_other_uncreative_centres",
            "qualifiers": {
                "source_line_start": 60, "source_line_end": 60, "printed_page": 202, "pdf_physical_page": 44,
                "claim": "Haskell says Victor Amadeus and Juvarra followed the example of patrons in other uncreative centres.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "The plural subject refers to Victor Amadeus and Juvarra; the comparative phrase 'uncreative centres' is Haskell's wording.",
                "mentioned_candidate_ids": ["cand-2388", "cand-1339", "cand-7335"],
                "co_actor_candidate_ids": ["cand-1339"], "relation_candidate": True,
                "relation_candidate_note": "This separates the stated precedent from the Turin policy's resulting attraction of painters or pictures.",
            },
            "original_quote": "They followed the example of patrons in other uncreative centres",
        },
    ]
    rows.extend(new_rows)
    by_id.update({row["statement_id"]: row for row in new_rows})
    output = [by_id[row["statement_id"]] for row in rows]

    counts = {
        "statements": len(output),
        "true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in output),
        "false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in output),
        "unset": sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in output),
    }
    if counts != {"statements": 14201, "true": 8811, "false": 3439, "unset": 1951}:
        raise SystemExit(f"unexpected post-counts: {counts}")

    candidate_row = {
        "candidate_id": CITY_GROUP, "index_entry_id": "", "canonical_name": "More richly endowed cities from which painters or pictures were drawn (unnamed group)",
        "index_page_range": "", "suggested_type": "place", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell refers to a wide variety of more richly endowed cities as sources for painters or their pictures attracted to Turin; no city or individual source assignment is named.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT + "#L60",
    }
    mention_row = {
        "mention_id": CITY_MENTION, "segment_id": SEGMENT, "candidate_id": CITY_GROUP,
        "surface_form": city_surface, "start_char": str(start), "end_char": str(start + len(city_surface)),
        "note": "Unnamed group of richer source cities; no city identities or assignments to individual painters or pictures are supplied.",
    }
    if set(candidate_row) != set(candidate_fields or []):
        raise SystemExit(f"candidate CSV field mismatch: {candidate_fields}")
    if set(mention_row) != set(mention_fields or []):
        raise SystemExit(f"mention CSV field mismatch: {mention_fields}")

    candidate_after = raw[CANDIDATES] + csv_row_bytes(candidate_fields, candidate_row)
    mention_after = raw[MENTIONS] + csv_row_bytes(mention_fields, mention_row)
    statement_after = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in output) + "\n").encode("utf-8")

    report = {
        "mode": "apply" if args.apply else "dry_run", "segment": SEGMENT,
        "existing_classified_true": len(TRUE_NOTES), "existing_classified_false": len(FALSE_NOTES),
        "new_statements": len(new_rows), "new_candidates": 1, "new_mentions": 1,
        "footnote_1_body_links": fq["linked_body_statement_ids"], "post_counts": counts,
        "input_sha256": hashes,
        "after_sha256": {STATEMENTS.name: sha(statement_after), CANDIDATES.name: sha(candidate_after), MENTIONS.name: sha(mention_after)},
        "backups": [str(path.relative_to(ROOT)) for path in backups],
        "new_candidate": candidate_row, "new_mention": mention_row,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return

    for path, content in zip((STATEMENTS, CANDIDATES, MENTIONS), (raw[STATEMENTS], raw[CANDIDATES], raw[MENTIONS])):
        path.with_name(path.name + BACKUP_SUFFIX).write_bytes(content)
    for path, content in ((STATEMENTS, statement_after), (CANDIDATES, candidate_after), (MENTIONS, mention_after)):
        atomic_write(path, content)
        if sha(path.read_bytes()) != report["after_sha256"][path.name]:
            raise SystemExit(f"post-write hash mismatch: {path.name}")
    print("applied; three recovery copies written and post-write hashes verified")


if __name__ == "__main__":
    main()
