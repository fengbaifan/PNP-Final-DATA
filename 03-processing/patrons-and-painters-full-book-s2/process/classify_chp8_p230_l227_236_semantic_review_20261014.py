"""Guarded S2 semantic review for printed p.230, body lines 227-234."""
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
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p230_review.png"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l227-236"
BACKUP_SUFFIX = ".bak-s2-chp8-p230-l227-236-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "b2cacfb2ed3c495b502059fbbf63c1c6f4cf73d90360c6619334a175378d55e9",
    CANDIDATES: "cef58d5f14f19f8ecf91813e872d269b54d813e102ad9656f341b824c7660693",
    MENTIONS: "5ef706c9bdae87b32183b51da4903b65846fb08016e8b57c8fff2f2ed05d2bf6",
    COVERAGE: "607342f702dafa6672481b4d0e71703a0427fc2e898242d816f13ad4465117f1",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PAGE_IMAGE: "fe43647bc8925308636e5977d43ac0e6dd1ecc75330fb69aef5fef458442e866",
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


def fragment(line: str, start: str, end: str | None = None) -> str:
    a = line.find(start)
    if a < 0:
        raise SystemExit(f"source fragment not found: {start!r}")
    if end is None:
        return line[a:].rstrip()
    b = line.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f"source end fragment not found after {start!r}: {end!r}")
    return line[a:b].rstrip()


def new_statement(statement_id, subject, object_, predicate, lines, claim, quote, *,
                  relation, note, mentioned, speaker="Haskell", text_layer="body", extra=None):
    qualifiers = {
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 230, "pdf_physical_page": 32,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": note, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": note,
    }
    if extra:
        qualifiers.update(extra)
    return {"statement_id": statement_id, "segment_id": SEGMENT,
            "subject_candidate_id": subject, "object_candidate_id": object_,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote, "origin": "book", "source_file": SOURCE_REL}


def plan():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")
    segments = read_jsonl(SEGMENTS)
    meta = {row["segment_id"]: row for row in segments}.get(SEGMENT)
    if not meta or (meta["line_start"], meta["line_end"]) != (227, 236):
        raise SystemExit("unexpected p.230 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if sha("\n".join(source_lines[226:236]).encode("utf-8")) != meta["sha256"]:
        raise SystemExit("p.230 source segment hash mismatch")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    coverage_fields, coverage = read_csv(COVERAGE)
    by_id = {row["statement_id"]: row for row in statements}
    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(target_rows) != 20:
        raise SystemExit(f"expected 20 migrated p.230 statements; got {len(target_rows)}")
    expected_unset = {
        "st-chp8-p230-contemporary-obituary-praise",
        "st-chp8-p230-cosimo-reign",
        "st-chp8-p230-discerning-patron-and-scholars",
        "st-chp8-p230-heir-attempts-closed",
        "st-chp8-p230-illness-death",
        "st-chp8-p230-regent-louis-comparison",
        "st-chp8-p230-retirement-and-houses",
        "st-chp8-p230-two-venice-visits",
        "st-chp8-p230-venice-memory-observation-open",
    }
    for statement_id in expected_unset:
        if statement_id not in by_id or by_id[statement_id]["qualifiers"].get("relation_candidate") is not None:
            raise SystemExit(f"unexpected status or missing statement: {statement_id}")
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"], coverage_row["source_line_ranges"]) != ("reviewed", "complete", "L227-236"):
        raise SystemExit(f"unexpected p.230 coverage state: {coverage_row}")

    lines = {i + 1: line for i, line in enumerate(source_lines)}
    l228, l229, l230, l231, l232, l233, l234 = (lines[n] for n in range(228, 235))
    q_obituary = l231[l231.index("With his death"):].rstrip() + "\n" + l232
    q_cosimo = fragment(l230, "His tyrannical old father")
    q_correspondence = fragment(l229, "He corresponded with artists and musicians", "and his great sensibilities")
    q_painter_patron = fragment(l229, "and his great sensibilities", "He welcomed foreign scholars")
    q_scholars = fragment(l229, "He welcomed foreign scholars", "He supported writers")
    q_attempts = fragment(l228, "had failed. Their efforts too came to nothing.", "Meanwhile")
    q_illness = fragment(l230, "But now ill-health began to strike", "His last years")
    q_death = fragment(l230, "and he died in 1713", "His tyrannical old father")
    q_regent = fragment(l230, "It was as if the") + "\n" + fragment(l231, "Regent had died before Louis XIV.")
    q_retire_poggio = fragment(l228, "Meanwhile Ferdinand gave up the struggle", "and Pratolino")
    q_retire_pratolino = fragment(l228, "especially Poggio a Caiano and Pratolino", ", there to enjoy himself")
    q_retirement_activities = fragment(l228, "there to enjoy himself")
    q_two_visits = fragment(l233, "The most important events in Ferdinand", "The city already")
    q_venice_reputation = fragment(l233, "The city already had the reputation", "and the Grand Prince")
    q_theatre_fame = fragment(l229, "His theatre at Pratolino was famous throughout Italy", "and for it")
    q_designer_employment = fragment(l229, "and for it he employed leading stage designers", "He corresponded")
    q_republic_gifts = fragment(l234, "The Republic gave him lavish presents")
    q_reciprocated = fragment(l234, "and he reciprocated")
    q_return_intention = fragment(l234, "he announced his intention of returning to Venice for the next carnival", "He never did")

    classifications = {
        "st-chp8-p230-contemporary-obituary-praise": (True, "The words are attributed to a contemporary admirer; note 4 suggests Luca Ombrosi as the probable author, but does not confirm the identity."),
        "st-chp8-p230-cosimo-reign": (False, "This is a biographical chronology claim about Cosimo III, not a relation statement."),
        "st-chp8-p230-discerning-patron-and-scholars": (False, "The existing row is narrowed to Ferdinand's correspondence with unnamed artists and musicians; related patronage and hospitality claims are separated below."),
        "st-chp8-p230-heir-attempts-closed": (True, "This closes p.229's family-succession continuation and records that the unnamed family's attempt came to nothing."),
        "st-chp8-p230-illness-death": (False, "The illness and its qualified connection to earlier dissipation are biographical claims; death is recorded separately."),
        "st-chp8-p230-regent-louis-comparison": (False, "This is Haskell's historical analogy, not a formal relationship."),
        "st-chp8-p230-retirement-and-houses": (True, "The source explicitly says Ferdinand retired to Poggio a Caiano; Pratolino is recorded as a separate place endpoint."),
        "st-chp8-p230-two-venice-visits": (False, "Haskell's ranking of the two visits as Ferdinand's most important life events is an evaluative judgment; Venice's general reputation is separated below."),
        "st-chp8-p230-venice-memory-observation-open": (False, "This is Haskell's interpretive account of memory and later observation, completed through the p.231 continuation."),
    }
    for statement_id, (value, note) in classifications.items():
        q = by_id[statement_id]["qualifiers"]
        q["relation_candidate"] = value
        q["relation_candidate_note"] = note

    obituary = by_id["st-chp8-p230-contemporary-obituary-praise"]
    obituary["subject_candidate_id"] = "cand-7851"
    obituary["object_candidate_id"] = "cand-1609"
    obituary["predicate"] = "probable_ombrosi_testimony_praising_ferdinand_as_protector_of_arts"
    obituary["original_quote"] = q_obituary
    obituary["qualifiers"].update({
        "claim": "Haskell reports an admirer saying Ferdinand's death removed joyfulness from Florence and Tuscany and took away a protector of the arts; footnote 4 suggests Luca Ombrosi as the probable author.",
        "speaker": "Unidentified contemporary admirer; footnote 4 suggests Luca Ombrosi as probable author",
        "text_layer": "reported direct speech",
        "qualification": "The identity remains probable, not confirmed; keep the body attribution and footnote's named candidate linked without treating the suggestion as established fact.",
        "mentioned_candidate_ids": ["cand-7851", "cand-1609", "cand-3397", "cand-6232"],
        "footnote_marker": 4,
        "footnote_segment_id": "chp-8:08_CHP-8_sec_ii:l372-461",
        "footnote_source_line": 408,
        "footnote_statement_ids": ["st-chp8-p230-note4-ombrosi-attribution"],
        "footnote_link_status": "resolved_source_migration",
        "identity_status": "probable_from_footnote_not_confirmed",
    })

    cosimo = by_id["st-chp8-p230-cosimo-reign"]
    cosimo["original_quote"] = q_cosimo
    cosimo["qualifiers"].update({"claim": "Haskell says Cosimo III remained on the throne after forty-three years.",
                                 "mentioned_candidate_ids": ["cand-1607"],
                                 "qualification": "This is a source-attributed chronological claim; the page image confirms the line wording."})

    correspondence = by_id["st-chp8-p230-discerning-patron-and-scholars"]
    correspondence["original_quote"] = q_correspondence
    correspondence["qualifiers"].update({"claim": "Ferdinand corresponded with artists and musicians.",
                                         "mentioned_candidate_ids": ["cand-1609"],
                                         "qualification": "The source names no individual correspondents; it is kept as a biographical claim without invented group endpoints."})

    attempts = by_id["st-chp8-p230-heir-attempts-closed"]
    attempts["subject_candidate_id"] = "cand-5179"
    attempts["object_candidate_id"] = "cand-1609"
    attempts["predicate"] = "medici_family_attempted_succession_without_success_after_ferdinand"
    attempts["original_quote"] = q_attempts
    attempts["qualifiers"].update({"claim": "The unnamed Medici family members' effort to secure succession where Ferdinand had failed also came to nothing.",
                                   "mentioned_candidate_ids": ["cand-5179", "cand-1609"],
                                   "qualification": "This completes the p.229 continuation; the individual family members and any prospective heir remain unidentified."})

    illness = by_id["st-chp8-p230-illness-death"]
    illness["predicate"] = "suffered_ill_health_and_epileptic_fits_after_earlier_dissipation"
    illness["original_quote"] = q_illness
    illness["qualifiers"].update({"claim": "Haskell says Ferdinand developed ill health and epileptic fits, apparently as consequences of his earlier dissipation.",
                                  "mentioned_candidate_ids": ["cand-1609"],
                                  "qualification": "The causal explanation is expressly qualified as 'apparently'; death is recorded separately."})

    regent = by_id["st-chp8-p230-regent-louis-comparison"]
    regent["original_quote"] = q_regent
    regent["qualifiers"].update({"claim": "Haskell compares Ferdinand's death to the hypothetical death of the Regent before Louis XIV.",
                                 "mentioned_candidate_ids": ["cand-1609", "cand-7841", "cand-1447"],
                                 "qualification": "The Regent remains unidentified; the sentence is an analogy, not an identity claim."})

    retirement = by_id["st-chp8-p230-retirement-and-houses"]
    retirement["object_candidate_id"] = "cand-1966"
    retirement["predicate"] = "retired_to_poggio_a_caiano_after_giving_up_heir_effort"
    retirement["original_quote"] = q_retire_poggio
    retirement["qualifiers"].update({"claim": "After giving up the struggle to secure an heir, Ferdinand retired to Poggio a Caiano.",
                                     "mentioned_candidate_ids": ["cand-1609", "cand-1966"],
                                     "qualification": "Pratolino is recorded in a separate statement; his later leisure and collecting activity is also separated."})

    two_visits = by_id["st-chp8-p230-two-venice-visits"]
    two_visits["predicate"] = "haskell_ranks_two_venice_visits_as_ferdinands_most_important_life_events"
    two_visits["original_quote"] = q_two_visits
    two_visits["qualifiers"].update({"claim": "Haskell calls Ferdinand's two visits to Venice the most important events in his life.",
                                     "mentioned_candidate_ids": ["cand-1609", "cand-3401"],
                                     "qualification": "This is Haskell's evaluative ranking, distinct from the specific 1696 visit and its documented relations."})

    memory = by_id["st-chp8-p230-venice-memory-observation-open"]
    memory["qualifiers"].update({"claim": "Haskell says the memory of Venice haunted Ferdinand and that he put it to good use in his later study of Venetian pictures.",
                                 "qualification": "The clause about his careful study continues at p.231 L239 and is linked to st-chp8-p231-venetian-pictures-recalled; this remains Haskell's interpretation.",
                                 "continued_to_segment_id": "chp-8:08_CHP-8_sec_ii:l238-249",
                                 "continued_to_source_line": 239,
                                 "continuation_closed_by_statement_id": "st-chp8-p231-venetian-pictures-recalled"})

    theatre = by_id["st-chp8-p230-pratolino-theatre"]
    theatre["predicate"] = "haskell_says_pratolino_theatre_was_famous_throughout_italy"
    theatre["original_quote"] = q_theatre_fame
    theatre["qualifiers"].update({"claim": "Haskell says Ferdinand's theatre at Pratolino was famous throughout Italy.",
                                  "mentioned_candidate_ids": ["cand-1609", "cand-7839", "cand-3461"],
                                  "relation_candidate": False,
                                  "relation_candidate_note": "This is Haskell's assessment of the theatre's fame; the employment of stage designers is recorded separately."})

    gifts = by_id["st-chp8-p230-republic-gifts-and-return"]
    gifts["predicate"] = "republic_of_venice_gave_ferdinand_lavish_presents"
    gifts["original_quote"] = q_republic_gifts
    gifts["qualifiers"].update({"claim": "The Republic of Venice gave Ferdinand lavish presents.",
                                "mentioned_candidate_ids": ["cand-6255", "cand-1609"],
                                "qualification": "The reciprocal response and Ferdinand's unfulfilled plan to return are split into separate statements."})

    candidate_ids = {row["candidate_id"] for row in candidates}
    required_candidates = {"cand-1966", "cand-7838", "cand-7839", "cand-7840", "cand-7851", "cand-6255", "cand-1609", "cand-3401"}
    if not required_candidates <= candidate_ids:
        raise SystemExit(f"missing endpoint candidates: {sorted(required_candidates - candidate_ids)}")

    statement_ids = {row["statement_id"] for row in statements}
    additions = [
        new_statement("st-chp8-p230-discriminating-painter-patron", "cand-1609", None,
                      "described_as_discriminating_patron_of_many_painters", (229, 229),
                      "Haskell says Ferdinand's sensibilities made him a discriminating patron of many of the day's most interesting painters.",
                      q_painter_patron, relation=False,
                      note="This is Haskell's evaluative characterization; no unnamed painter group is invented as an endpoint.",
                      mentioned=["cand-1609"]),
        new_statement("st-chp8-p230-welcomed-foreign-scholars", "cand-1609", None,
                      "welcomed_foreign_scholars_and_showed_his_collections", (229, 229),
                      "Haskell says Ferdinand welcomed foreign scholars and delighted in showing them his collections.",
                      q_scholars, relation=False,
                      note="The scholars and the displayed collections are not individually identified in this passage.",
                      mentioned=["cand-1609"]),
        new_statement("st-chp8-p230-ferdinand-died-1713", "cand-1609", None,
                      "died_in_1713_at_age_fifty", (230, 230),
                      "Haskell says Ferdinand died in 1713 at the age of fifty.",
                      q_death, relation=False,
                      note="This preserves the date and age separately from the preceding account of illness.",
                      mentioned=["cand-1609"]),
        new_statement("st-chp8-p230-retired-to-pratolino", "cand-1609", "cand-7838",
                      "retired_to_pratolino_after_giving_up_heir_effort", (228, 228),
                      "After giving up the struggle to secure an heir, Ferdinand retired to Pratolino.",
                      q_retire_pratolino, relation=True,
                      note="Pratolino is separately represented as a place; later theatrical use is recorded in its own statement.",
                      mentioned=["cand-1609", "cand-7838"]),
        new_statement("st-chp8-p230-retirement-leisure-and-collections", "cand-1609", None,
                      "organized_theatrical_displays_and_picture_collections_at_country_houses", (228, 228),
                      "At the country houses Ferdinand enjoyed himself and organized theatrical displays and picture collections.",
                      q_retirement_activities, relation=False,
                      note="The activities are preserved as biographical content; the passage does not specify which house hosted each display or collection.",
                      mentioned=["cand-1609", "cand-1966", "cand-7838"]),
        new_statement("st-chp8-p230-venice-reputation-for-pleasures", "cand-3401", None,
                      "haskell_characterizes_venice_as_encouraging_pleasure_except_political_unorthodoxy", (233, 233),
                      "Haskell says Venice had a long-standing reputation for allowing and encouraging every pleasure except political unorthodoxy.",
                      q_venice_reputation, relation=False,
                      note="This is Haskell's general characterization of Venice, distinct from the events in Ferdinand's visits.",
                      mentioned=["cand-3401"]),
        new_statement("st-chp8-p230-bibbiena-stage-designers", "cand-1609", "cand-7840",
                      "employed_bibbiena_family_members_as_stage_designers", (229, 229),
                      "Ferdinand employed leading stage designers for his Pratolino theatre, including members of the Bibbiena family.",
                      q_designer_employment, relation=True,
                      note="The theatre is the work context and members of the Bibbiena family are the source-named designer group.",
                      mentioned=["cand-1609", "cand-7839", "cand-7840"]),
        new_statement("st-chp8-p230-ferdinand-reciprocated-republic-gifts", "cand-1609", "cand-6255",
                      "ferdinand_reciprocated_republic_of_venice_gifts", (234, 234),
                      "Ferdinand reciprocated the Republic of Venice's lavish presents.",
                      q_reciprocated, relation=True,
                      note="The sentence reverses direction after stating the Republic's gifts; the direction is recorded explicitly.",
                      mentioned=["cand-1609", "cand-6255"]),
        new_statement("st-chp8-p230-ferdinand-announced-return-to-venice", "cand-1609", "cand-3401",
                      "announced_intention_to_return_to_venice_next_carnival_but_did_not", (234, 234),
                      "Ferdinand announced an intention to return to Venice for the next carnival, but he never did.",
                      q_return_intention, relation=True,
                      note="This records an unfulfilled intention, not a completed return visit.",
                      mentioned=["cand-1609", "cand-3401"], extra={"outcome": "intended return did not occur"}),
    ]
    for row in additions:
        if row["statement_id"] in statement_ids:
            raise SystemExit(f"statement ID already exists: {row['statement_id']}")
        statement_ids.add(row["statement_id"])

    mention_ids = {row["mention_id"] for row in mentions}
    spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mentions}
    offsets = {}
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), source_lines[meta["line_start"] - 1:meta["line_end"]]):
        offsets[line_no] = offset
        offset += len(line) + 1
    line_positions = {i + 1: line for i, line in enumerate(source_lines)}
    new_mentions = []
    mention_id = "m-chp8-p230-contemporary-admirer"
    if mention_id in mention_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    surface = "a contemporary admirer"
    start_local = line_positions[231].find(surface)
    if start_local < 0:
        raise SystemExit("p.230 contemporary-admirer mention not found")
    start, end = offsets[231] + start_local, offsets[231] + start_local + len(surface)
    if (SEGMENT, str(start), str(end)) in spans:
        raise SystemExit("duplicate p.230 contemporary-admirer mention span")
    new_mentions.append({"mention_id": mention_id, "segment_id": SEGMENT, "candidate_id": "cand-7851",
                         "surface_form": surface, "start_char": str(start), "end_char": str(end),
                         "note": "Footnote 4 suggests Luca Ombrosi as the probable author; this body attribution remains uncertain."})

    totals = {"true": 0, "false": 0, "unset": 0}
    for row in statements + additions:
        if row.get("segment_id") != SEGMENT:
            continue
        value = row.get("qualifiers", {}).get("relation_candidate")
        totals["true" if value is True else "false" if value is False else "unset"] += 1
    if totals["unset"]:
        raise SystemExit(f"p.230 remains unclassified: {totals}")

    preview = {
        "mode": "dry-run", "segment": SEGMENT, "page_image": PAGE_IMAGE.relative_to(ROOT).as_posix(),
        "existing_statements_reviewed": len(target_rows), "new_statements": [row["statement_id"] for row in additions],
        "new_mentions": [mention_id], "p230_final_statement_counts": totals,
        "semantic_fixes": [
            "link the contemporary admirer to the footnote's probable Luca Ombrosi candidate with identity uncertainty preserved",
            "separate the Republic's gift, Ferdinand's reciprocation and his unfulfilled return intention",
            "split retirement to named houses from leisure and collecting activity",
            "separate the Pratolino theatre's reputation from employment of Bibbiena stage designers",
            "atomize illness, death, city reputation and scholarly hospitality claims",
        ],
    }
    payload = {
        STATEMENTS: jsonl_bytes(statements + additions),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions + new_mentions),
        COVERAGE: csv_bytes(coverage_fields, coverage),
    }
    return preview, payload


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.230 S2 review")
args = parser.parse_args()
preview, payload = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
for path in (STATEMENTS, CANDIDATES, MENTIONS, COVERAGE):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
for path, data in payload.items():
    atomic_write(path, data)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
