"""Guarded semantic refinement of composite statements on printed p.236."""
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
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
SEGMENT = "chp-8:08_CHP-8_sec_ii:l303-309"
NOTES_SEGMENT = "chp-8:08_CHP-8_sec_ii:l372-461"
BACKUP_SUFFIX = ".bak-s2-chp8-p236-semantic-refinement-20261014"
EXPECTED = {
    STATEMENTS: "0b6a39075d04df0d7a5470fd18b0243a3a2312263d34140029ad630447cf7bd9",
    COVERAGE: "c95176724cf93b487241027d6add17d3b5ca8c3c14ae5066f5c59d2815e134ec",
}
EXPECTED_EXISTING = {
    "st-chp8-p236-ceiling-venus-adonis-scene",
    "st-chp8-p236-corner-busts",
    "st-chp8-p236-ferdinand-collaboration-in-pitti-work",
    "st-chp8-p236-overdoor-composition",
    "st-chp8-p236-ricci-frescoes-and-court-atmosphere",
    "st-chp8-p236-ricci-small-figure-pictures",
    "st-chp8-p236-rococo-style-and-reception",
    "st-chp8-p236-style-contrast-with-earlier-work",
    "st-chp8-p236-wall-scene-diana-actaeon",
    "st-chp8-p236-wall-scene-diana-callisto",
    "st-chp8-p236-wall-scene-europa-bull",
    "st-chp8-p236-wall-scene-pan-syrinx",
}
NEW_IDS = {
    "st-chp8-p236-gherardi-instructions-report",
    "st-chp8-p236-frescoes-new-departure",
    "st-chp8-p236-prince-character-century-shift",
    "st-chp8-p236-frescoes-stylistic-novelty",
    "st-chp8-p236-frescoes-delighted-ferdinand",
    "st-chp8-p236-collaborator-painted-backgrounds",
    "st-chp8-p236-picture-group-appealed-to-ferdinand",
    "st-chp8-p236-ricci-letter-appraisal",
    "st-chp8-p236-macchiette-popularity",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    temporary.replace(path)


def cut(text: str, start: str, end: str | None = None, *, include_end=False) -> str:
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"source fragment not found: {start!r}")
    if end is None:
        return text[a:].rstrip()
    b = text.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f"source end fragment not found after {start!r}: {end!r}")
    if include_end:
        b += len(end)
    return text[a:b].rstrip()


def set_review(row, *, subject, object_, predicate, claim, quote, note, mentioned, relation,
               speaker="Haskell", text_layer="body", speaker_judgment=True,
               ocr_corrections=None, lines=(304, 304)):
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q.update({
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 236, "pdf_physical_page": 42,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": note, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": note,
        "speaker_judgment": speaker_judgment,
    })
    q.pop("ocr_corrections", None)
    if ocr_corrections:
        q["ocr_corrections"] = ocr_corrections
    q.pop("linked_note_statement_ids", None)


def new_statement(statement_id, subject, object_, predicate, lines, claim, quote, *, note,
                  mentioned, relation, speaker="Haskell", text_layer="body",
                  speaker_judgment=True, ocr_corrections=None):
    row = {"statement_id": statement_id, "segment_id": SEGMENT,
           "subject_candidate_id": subject, "object_candidate_id": object_, "predicate": predicate,
           "qualifiers": {}, "original_quote": quote, "origin": "book", "source_file": SOURCE_REL}
    set_review(row, subject=subject, object_=object_, predicate=predicate, claim=claim,
               quote=quote, note=note, mentioned=mentioned, relation=relation,
               speaker=speaker, text_layer=text_layer, speaker_judgment=speaker_judgment,
               ocr_corrections=ocr_corrections, lines=lines)
    return row


def plan():
    for path, expected in EXPECTED.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)}")
    segments = read_jsonl(SEGMENTS)
    metas = {row["segment_id"]: row for row in segments}
    meta = metas.get(SEGMENT)
    if not meta or (meta["line_start"], meta["line_end"]) != (303, 309):
        raise SystemExit("unexpected p.236 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[302:309])
    if sha(segment_text.encode("utf-8")) != meta["sha256"]:
        raise SystemExit("p.236 source segment hash mismatch")
    l304, l305, l306, l307, l308, l309 = (source_lines[n - 1] for n in range(304, 310))
    full307_308 = l307 + "\n" + l308
    quotes = {
        "ferdinand_inference": cut(l304, "From everything we know", " Indeed, some forty years later"),
        "gherardi_instructions": cut(l304, "Indeed, some forty years later", " There is, of course, no record"),
        "new_departure": "which represent a new departure in his career",
        "court_atmosphere": cut(l304, "reflect the more lighthearted", " The Prince’s own character", include_end=False),
        "prince_character": cut(l304, "The Prince’s own character", " The heavy drama"),
        "stylistic_novelty": cut(full307_308, "Everything is painted with a verve", "European art.", include_end=True),
        "ferdinand_delight": cut(l308, "The frescoes delighted Ferdinand", " and yet"),
        "rococo_forecast": cut(l308, "and yet their intimate, rococo style", "Italy.", include_end=True),
        "ricci_pictures": cut(l309, "Ricci also painted various pictures for him at this time", " which were usually the work of a collaborator"),
        "collaborator_backgrounds": cut(l309, "which were usually the work of a collaborator", " These especially appealed"),
        "ferdinand_taste": cut(l309, "These especially appealed to his taste", "—‘le figurette"),
        "ricci_appraisal": cut(l309, "‘le figurette mi piacciono assaissimo", "he wrote of one pair of such scenes he had been shown", include_end=True),
        "macchiette": cut(l309, "and macchiette of this kind", " Ricci wrote again"),
    }
    for name, quote in quotes.items():
        if not quote or quote not in segment_text:
            raise SystemExit(f"quote is not an exact p.236 source span ({name}): {quote!r}")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    existing = [row for row in statements if row.get("segment_id") == SEGMENT]
    if {row["statement_id"] for row in existing} != EXPECTED_EXISTING:
        raise SystemExit(f"unexpected p.236 statement set: {len(existing)} rows")
    _, coverage = read_csv(COVERAGE)
    cov = next((r for r in coverage if r["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.236 coverage state: {cov}")
    _, candidates = read_csv(CANDIDATES)
    candidate_ids = {r["candidate_id"] for r in candidates}

    def review(statement_id, **kwargs):
        set_review(by_id[statement_id], **kwargs)

    review("st-chp8-p236-ferdinand-collaboration-in-pitti-work",
        subject="cand-1609", object_="cand-7967",
        predicate="haskell_inferred_ferdinand_collaborated_extensively_in_riccis_pitti_work",
        claim="Haskell infers from Ferdinand’s patronage that the Prince must have collaborated extensively in Ricci’s Pitti work.",
        quote=quotes["ferdinand_inference"],
        note="This is Haskell’s inference, not a surviving record; the later Gherardi report about specific instructions is separately recorded.",
        mentioned=["cand-1609", "cand-7967", "cand-2179"], relation=True)
    review("st-chp8-p236-ricci-frescoes-and-court-atmosphere",
        subject="cand-7967", object_="cand-8010",
        predicate="frescoes_reflected_the_lighthearted_avant_garde_atmosphere_of_ferdinands_court",
        claim="Haskell says Ricci’s Pitti frescoes reflected the more lighthearted and avant-garde atmosphere of Ferdinand’s court.",
        quote=quotes["court_atmosphere"],
        note="This is Haskell’s interpretation of the relation between the frescoes and court atmosphere, not an independently verified historical characterization.",
        mentioned=["cand-7967", "cand-2179", "cand-1609", "cand-8010"], relation=True,
        ocr_corrections=[{"source_line": 304, "ocr": "avantgarde", "print": "avant-garde", "basis": "CHP-8.pdf physical page 42"}])
    review("st-chp8-p236-ricci-small-figure-pictures",
        subject="cand-2179", object_="cand-8001",
        predicate="painted_small_figure_pictures_for_ferdinand_with_architectural_backgrounds",
        claim="Haskell says Ricci painted various pictures for Ferdinand, particularly pictures of little figures against architectural backgrounds.",
        quote=quotes["ricci_pictures"],
        note="This records the described picture group; the next clause about who usually painted the backgrounds is separately stated.",
        mentioned=["cand-2179", "cand-8001", "cand-1609"], relation=True,
        lines=(309, 309))
    review("st-chp8-p236-rococo-style-and-reception",
        subject="cand-8004", object_=None,
        predicate="haskell_assessed_rococo_styles_parisian_popularity_and_limited_future_in_italy",
        claim="Haskell says the frescoes’ intimate Rococo style would become popular in Parisian boudoirs but had little future in Italy.",
        quote=quotes["rococo_forecast"],
        note="This is Haskell’s stylistic and reception assessment; its future-looking claim is not independently verified here.",
        mentioned=["cand-7967", "cand-8004", "cand-4653", "cand-3461"], relation=False,
        ocr_corrections=[{"source_line": 308, "ocr": "little suture in Italy", "print": "little future in Italy", "basis": "CHP-8.pdf physical page 42"}],
        lines=(308, 308))

    additions = [
        new_statement("st-chp8-p236-gherardi-instructions-report", "cand-2179", "cand-1609",
            "followed_ferdinands_specific_instructions_for_the_pitti_decoration", (304, 304),
            "Haskell reports that, about forty years later, a writer who knew Ricci said Ricci followed the Grand Prince’s specific instructions for the decoration.",
            quotes["gherardi_instructions"], note="The writer is identified in note 1 as Abate Gherardi; the quoted account is mediated through Haskell and was not independently consulted.",
            mentioned=["cand-2179", "cand-1609", "cand-7967"], relation=True),
        new_statement("st-chp8-p236-frescoes-new-departure", "cand-7967", None,
            "haskell_described_the_frescoes_as_a_new_departure_in_riccis_career", (304, 304),
            "Haskell describes Ricci’s Pitti frescoes as a new departure in the artist’s career.",
            quotes["new_departure"], note="This is Haskell’s art-historical characterization, not a separately verified career-periodization claim.",
            mentioned=["cand-7967", "cand-2179"], relation=False),
        new_statement("st-chp8-p236-prince-character-century-shift", "cand-1609", None,
            "haskell_interpreted_ferdinands_character_as_symbolizing_a_less_harsh_new_century", (304, 304),
            "Haskell interprets Ferdinand’s character as symbolizing a coming century that would be less harsh, bigoted, and passionate, and says Ricci’s frescoes assert this change.",
            quotes["prince_character"], note="This is Haskell’s interpretation of Ferdinand and the frescoes, not an independently established description of the century.",
            mentioned=["cand-1609", "cand-7967"], relation=False),
        new_statement("st-chp8-p236-frescoes-stylistic-novelty", "cand-7967", None,
            "haskell_said_the_frescoes_painterly_manner_was_new_to_florence_and_european_art", (307, 308),
            "Haskell says the frescoes’ fluent painterly manner was totally new to Florence and European art.",
            quotes["stylistic_novelty"], note="This is an attributed stylistic assessment.",
            mentioned=["cand-7967", "cand-3397", "cand-8011"], relation=False),
        new_statement("st-chp8-p236-frescoes-delighted-ferdinand", "cand-7967", "cand-1609",
            "delighted_ferdinand", (308, 308),
            "Haskell says the Pitti frescoes delighted Ferdinand.", quotes["ferdinand_delight"],
            note="The source reports Ferdinand’s response; it does not specify a date or separate occasion.",
            mentioned=["cand-7967", "cand-1609"], relation=True,
            speaker="Haskell reporting Ferdinand’s response"),
        new_statement("st-chp8-p236-collaborator-painted-backgrounds", "cand-8003", "cand-8001",
            "usually_painted_architectural_backgrounds_for_small_figure_pictures", (309, 309),
            "Haskell says architectural backgrounds for these pictures were usually the work of an unidentified collaborator.",
            quotes["collaborator_backgrounds"], note="No collaborator is named, and the wording describes a usual division of labor rather than identifying the collaborator for every picture.",
            mentioned=["cand-8003", "cand-8001"], relation=True),
        new_statement("st-chp8-p236-picture-group-appealed-to-ferdinand", "cand-8001", "cand-1609",
            "particularly_appealed_to_ferdinands_taste", (309, 309),
            "Haskell says the small-figure pictures especially appealed to Ferdinand’s taste.",
            quotes["ferdinand_taste"], note="The antecedent is the small-figure pictures; Ricci’s separate quoted appraisal of one pair follows.",
            mentioned=["cand-8001", "cand-1609"], relation=True),
        new_statement("st-chp8-p236-ricci-letter-appraisal", "cand-2179", None,
            "ricci_praised_one_pair_of_small_figure_scenes_shown_to_him", (309, 309),
            "Haskell quotes Ricci describing one pair of small-figure scenes shown to him as graceful, well distributed, and made with little.",
            quotes["ricci_appraisal"], note="The pair is not individually identified. Note 3 says it is unclear whether the pictures in question were by Ricci; this statement records his reported appraisal, not authorship.",
            mentioned=["cand-2179", "cand-8001"], relation=False,
            speaker="Ricci as quoted by Haskell", text_layer="body quotation",
            ocr_corrections=[{"source_line": 309, "ocr": "perche", "print": "perchè", "basis": "CHP-8.pdf physical page 42"}]),
        new_statement("st-chp8-p236-macchiette-popularity", "cand-8002", None,
            "haskell_said_macchiette_became_enormously_popular_as_the_century_progressed", (309, 309),
            "Haskell says macchiette of this kind became enormously popular as the century progressed.",
            quotes["macchiette"], note="This is Haskell’s broad reception statement about the genre term, not a claim about a named work or artist relationship.",
            mentioned=["cand-8002"], relation=False),
    ]
    additions_by_id = {row["statement_id"]: row for row in additions}
    if set(additions_by_id) != NEW_IDS or len(additions) != len(NEW_IDS) or NEW_IDS & set(by_id):
        raise SystemExit("unexpected or duplicate p.236 refinement statement IDs")

    all_rows = statements + additions
    by_id = {row["statement_id"]: row for row in all_rows}
    # Reattach the footnotes to the atomic assertions they actually support.
    note_links = {
        "st-chp8-p236-note1-gherardi-publication": ["st-chp8-p236-gherardi-instructions-report"],
        "st-chp8-p236-note1-gherardi-report": ["st-chp8-p236-gherardi-instructions-report"],
        "st-chp8-p236-note2-sketch-at-orleans": ["st-chp8-p236-ceiling-venus-adonis-scene"],
        "st-chp8-p236-note3-letter106-attribution-uncertain": ["st-chp8-p236-ricci-letter-appraisal"],
        "st-chp8-p236-note3-saluzzi-painting-at-lucca": ["st-chp8-p236-collaborator-painted-backgrounds"],
    }
    for note_id, body_ids in note_links.items():
        note = by_id.get(note_id)
        if note is None:
            raise SystemExit(f"missing p.236 note statement: {note_id}")
        note.setdefault("qualifiers", {})["linked_body_statement_ids"] = body_ids
        for body_id in body_ids:
            body = by_id[body_id]
            links = body.setdefault("qualifiers", {}).setdefault("linked_note_statement_ids", [])
            if note_id not in links:
                links.append(note_id)

    counts = {"true": 0, "false": 0}
    final_target = [r for r in all_rows if r.get("segment_id") == SEGMENT]
    for row in final_target:
        q = row.get("qualifiers", {})
        value = q.get("relation_candidate")
        if value not in (True, False):
            raise SystemExit(f"p.236 statement remains unclassified: {row['statement_id']}")
        counts["true" if value else "false"] += 1
        refs = set(q.get("mentioned_candidate_ids", []))
        refs.update(x for x in (row.get("subject_candidate_id"), row.get("object_candidate_id")) if x)
        if missing := refs - candidate_ids:
            raise SystemExit(f"unknown candidate refs in {row['statement_id']}: {sorted(missing)}")
    coverage_row = next(r for r in coverage if r["segment_id"] == SEGMENT)
    coverage_row["note"] += (
        " Semantic refinement 2026-10-14 rechecked the body against CHP-8.pdf physical page 42. Separated Haskell’s inference "
        "about Ferdinand’s participation from the Gherardi report about specific instructions; separated the frescoes’ new-career "
        "assessment, court-atmosphere interpretation, and Prince-character interpretation; extracted Ferdinand’s reported delight; "
        "and separated Ricci’s picture group, the collaborator’s backgrounds, Ferdinand’s taste, Ricci’s quoted appraisal, and the "
        "later popularity of macchiette. Footnotes 1 and 3 now link to the statements they support. Existing scan-based corrections, "
        "including ‘suture’ to ‘future’, remain in S2; no candidate, mention, KU, or formal S6 relation was added."
    )
    preview = {
        "mode": "dry-run", "segment": SEGMENT, "physical_page": 42,
        "existing_statements_reviewed": len(existing), "new_statements": sorted(NEW_IDS),
        "final_statement_count": len(final_target), "relation_candidate_counts": counts,
        "quote_spans_verified": len(quotes), "note_links": note_links,
        "new_candidates": 0, "new_mentions": 0, "formal_relations_created": 0,
    }
    payload = {
        STATEMENTS: jsonl_bytes(all_rows),
        COVERAGE: csv_bytes(read_csv(COVERAGE)[0], coverage),
    }
    return preview, payload


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.236 semantic refinement")
args = parser.parse_args()
preview, payload = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
for path in (STATEMENTS, COVERAGE):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
for path, data in payload.items():
    atomic_write(path, data)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
