"""Refine p.237 composite statements and repair Ricci entity links."""
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
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
SEG236 = "chp-8:08_CHP-8_sec_ii:l303-309"
SEG237 = "chp-8:08_CHP-8_sec_ii:l311-325"
BACKUP_SUFFIX = ".bak-s2-chp8-p237-l311-325-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "410ef39fbbf7b10e6db470315e15e05fd0ec0fa1c70106dc5b601147772f534f",
    MENTIONS: "a43e7ba5020f19f60b8973a63dbcf541e71f8dc353c891bf33c0db3eedfff702",
}
EXPECTED_P237 = {
    "st-chp8-p237-crespi-struck-by-ricci",
    "st-chp8-p237-crespi-style-compared-with-ricci",
    "st-chp8-p237-ferdinand-commissioned-still-lives",
    "st-chp8-p237-ferdinand-encouraged-crespi",
    "st-chp8-p237-ferdinand-role-in-crespi-career",
    "st-chp8-p237-note2-ferdinand-litigation",
    "st-chp8-p237-note2-silva-correspondence-citations",
    "st-chp8-p237-note3-other-bolognese-artists",
    "st-chp8-p237-note5-return-to-bologna",
    "st-chp8-p237-ricci-crespi-missed-meeting",
    "st-chp8-p237-ricci-england-1716",
}
NEW_IDS = {
    "st-chp8-p236-ricci-wrote-to-ferdinand-again-1708",
    "st-chp8-p237-ricci-return-venice-before-letter",
    "st-chp8-p237-artists-pioneered-late-baroque-break",
    "st-chp8-p237-court-mood-affected-crespi",
    "st-chp8-p237-court-mood-affected-ricci",
    "st-chp8-p237-crespi-wishes-to-work-for-ferdinand",
    "st-chp8-p237-court-important-outside-florence",
    "st-chp8-p237-ferdinand-impressed-by-massacre",
    "st-chp8-p237-still-life-choice-assessment",
    "st-chp8-p237-ferdinand-appreciated-intimate-talents",
    "st-chp8-p237-pleasant-subject-commissions",
    "st-chp8-p237-patronage-enabled-break-from-histories",
    "st-chp8-p237-crespi-first-florence-visit-duration",
    "st-chp8-p237-note2-cites-silva-letter-155",
    "st-chp8-p237-note2-cites-silva-letter-299",
    "st-chp8-p237-note2-cites-silva-letter-607",
    "st-chp8-p237-note2-cites-zambeccari-letter",
    "st-chp8-p237-note3-santi-in-touch-with-ferdinand",
    "st-chp8-p237-note3-dal-sole-in-touch-with-ferdinand",
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


def normalized(text: str) -> str:
    return " ".join(text.split())


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


def set_statement(row, *, subject, object_, predicate, claim, quote, lines, page,
                  physical, qualification, mentioned, relation, text_layer="body",
                  speaker="Haskell", relation_note=None, extras=None):
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q.update({
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": page, "pdf_physical_page": physical,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
    })
    if relation_note is not None:
        q["relation_candidate_note"] = relation_note
    else:
        q.pop("relation_candidate_note", None)
    if extras:
        q.update(extras)


def new_statement(statement_id, segment, subject, object_, predicate, *, lines, page,
                  physical, claim, quote, qualification, mentioned, relation,
                  text_layer="body", speaker="Haskell", relation_note=None, extras=None):
    row = {
        "statement_id": statement_id, "segment_id": segment,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": {}, "original_quote": quote,
        "origin": "book", "source_file": SOURCE_REL,
    }
    set_statement(row, subject=subject, object_=object_, predicate=predicate,
                  claim=claim, quote=quote, lines=lines, page=page, physical=physical,
                  qualification=qualification, mentioned=mentioned, relation=relation,
                  text_layer=text_layer, speaker=speaker,
                  relation_note=relation_note, extras=extras)
    return row


def plan():
    for path, expected in EXPECTED.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)}")

    metas = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
    if (metas.get(SEG236, {}).get("line_start"), metas.get(SEG236, {}).get("line_end")) != (303, 309):
        raise SystemExit("unexpected p.236 segment metadata")
    if (metas.get(SEG237, {}).get("line_start"), metas.get(SEG237, {}).get("line_end")) != (311, 325):
        raise SystemExit("unexpected p.237 segment metadata")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    l309 = source_lines[308]
    l314, l315, l316, l317, l318, l319, l320, l321, l322, l323, l324, l325 = (
        source_lines[n - 1] for n in range(314, 326)
    )
    quotes = {
        "crespi_impression": "\n".join([
            l314,
            l315,
            l316,
            cut(l317, "Venetian painter’s ‘spirit’.1", " And although", include_end=True),
        ]),
        "pioneering": cut(l317, "the two most interesting artists of the period", " missed meeting each other"),
        "missed_meeting": cut(l317, "missed meeting each other", ", the new mood"),
        "court_mood": cut(l317, "the new mood that prevailed there", " Crespi’s own innovations"),
        "style_comparison": cut(l317, "Crespi’s own innovations", " it is therefore hardly surprising"),
        "encouragement": "\n".join([
            cut(l317, "it is therefore hardly surprising"),
            l318,
            cut(l319, "Massacre of the Innocents.2", " Crespi’s anxiety", include_end=True),
        ]),
        "crespi_wish": cut(l319, "Crespi’s anxiety to work for Ferdinand", " provides clear evidence"),
        "court_importance": "\n".join([
            cut(l319, "Crespi’s anxiety to work for Ferdinand"),
            cut(l320, "Florence,3", " and when he brought the picture"),
        ]),
        "ferdinand_impressed": cut(l320, "when he brought the picture to Ferdinand", " The Grand Prince at once commissioned"),
        "still_life_commission": cut(l320, "The Grand Prince at once commissioned", "—a curious"),
        "still_life_assessment": cut(l320, "a curious and significant choice", " In fact"),
        "career_importance": cut(l321, "Ferdinand is of great importance", " He seems"),
        "intimate_talents": cut(l321, "He seems to have been among the first", " The commissions"),
        "pleasant_commissions": cut(l321, "The commissions with which he flooded the artist", " and with the support"),
        "career_shift": cut(l321, "and with the support of such a powerful protector", " On this first visit"),
        "first_visit": cut(l321, "On this first visit to Florence", "; but he"),
        "litigation": cut(l322, "Ferdinand himself took a hand", " See letters-between"),
        "silva_citations": cut(l322, "See letters-between", None),
        "zambeccari_citation": cut(l322, "and also letter from Ferdinand", None),
        "graziani": cut(l323, "Other Bolognese artists", " Giovan Gioseffo Santi"),
        "santi": cut(l323, "Giovan Gioseffo Santi", " and Giovan Gioseffo dal Sole"),
        "dal_sole": "\n".join([cut(l323, "Giovan Gioseffo dal Sole"), l324]),
        "return_to_bologna": cut(l325, "He was back in Bologna", "—see above"),
    }
    for name, quote in quotes.items():
        line_start, line_end = {
            "crespi_impression": (314, 317), "pioneering": (317, 317),
            "missed_meeting": (317, 317), "court_mood": (317, 317),
            "style_comparison": (317, 317), "encouragement": (317, 319),
            "crespi_wish": (319, 319), "court_importance": (319, 320),
            "ferdinand_impressed": (320, 320), "still_life_commission": (320, 320),
            "still_life_assessment": (320, 320), "career_importance": (321, 321),
            "intimate_talents": (321, 321), "pleasant_commissions": (321, 321),
            "career_shift": (321, 321), "first_visit": (321, 321),
            "litigation": (322, 322), "silva_citations": (322, 322),
            "zambeccari_citation": (322, 322), "graziani": (323, 323),
            "santi": (323, 323), "dal_sole": (323, 324),
            "return_to_bologna": (325, 325),
        }[name]
        cited = "\n".join(source_lines[line_start - 1:line_end])
        if normalized(quote) not in normalized(cited):
            raise SystemExit(f"quote is not an exact source span ({name})")
    if "Ricci wrote again to Ferdinand in 1708 after" not in l309:
        raise SystemExit("p.236 sentence fragment is absent from source L309")
    if "his return to Venice" not in source_lines[311]:
        raise SystemExit("p.237 continuation is absent from source L312")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    existing_p237 = {row["statement_id"] for row in statements if row.get("segment_id") == SEG237}
    if existing_p237 != EXPECTED_P237:
        raise SystemExit(f"unexpected p.237 statement set: {len(existing_p237)} rows")
    if set(by_id) & NEW_IDS:
        raise SystemExit("one or more planned statement IDs already exist")
    candidates = {row["candidate_id"] for row in read_csv(TABLES / "entity-candidates.csv")[1]}
    required_candidates = {
        "cand-0871", "cand-1229", "cand-1609", "cand-2154", "cand-2356", "cand-2433",
        "cand-2480", "cand-2962", "cand-3397", "cand-3398", "cand-3401", "cand-6809",
        "cand-8010", "cand-8012", "cand-8013", "cand-8014", "cand-8015", "cand-8017",
        "cand-8018", "cand-8019", "cand-8020", "cand-8021", "cand-8027",
    }
    if not required_candidates <= candidates:
        raise SystemExit(f"required candidates are missing: {sorted(required_candidates - candidates)}")

    fields, mention_rows = read_csv(MENTIONS)
    target_mentions = [r for r in mention_rows if r.get("segment_id") in {SEG236, SEG237}]
    if not any(r.get("mention_id") == "m-chp8-p237-ricci-return-venice" and r.get("candidate_id") == "cand-2179" for r in target_mentions):
        raise SystemExit("unexpected p.237 Venice mention mapping")

    # Ricci is a person; cand-2179 is the index subentry for his work for Ferdinand.
    # Correct only the reviewed p.236-p.237 segment rows and their source mentions.
    for row in statements:
        if row.get("segment_id") in {SEG236, SEG237}:
            if row.get("subject_candidate_id") == "cand-2179":
                row["subject_candidate_id"] = "cand-2154"
            if row.get("object_candidate_id") == "cand-2179":
                row["object_candidate_id"] = "cand-2154"
            q = row.get("qualifiers", {})
            ids = q.get("mentioned_candidate_ids")
            if isinstance(ids, list):
                q["mentioned_candidate_ids"] = list(dict.fromkeys("cand-2154" if x == "cand-2179" else x for x in ids))
            if row.get("segment_id") == SEG237:
                ids = q.get("mentioned_candidate_ids")
                if isinstance(ids, list):
                    q["mentioned_candidate_ids"] = list(dict.fromkeys("cand-0871" if x == "cand-0873" else x for x in ids))
    for row in mention_rows:
        if row.get("segment_id") in {SEG236, SEG237}:
            if row.get("candidate_id") == "cand-2179":
                row["candidate_id"] = "cand-2154"
            if row.get("segment_id") == SEG237 and row.get("candidate_id") == "cand-0873":
                row["candidate_id"] = "cand-0871"
    next(r for r in mention_rows if r["mention_id"] == "m-chp8-p237-ricci-return-venice").update({
        "candidate_id": "cand-3401",
        "note": "Venice, the city to which Ricci had returned before writing again to Ferdinand.",
    })

    by_id = {row["statement_id"]: row for row in statements}
    common_p237 = {"page": 237, "physical": 43}
    def revise(statement_id, *, subject, object_, predicate, claim, quote, lines,
               qualification, mentioned, relation, text_layer="body", relation_note=None,
               extras=None):
        set_statement(by_id[statement_id], subject=subject, object_=object_, predicate=predicate,
                      claim=claim, quote=quote, lines=lines, page=237, physical=43,
                      qualification=qualification, mentioned=mentioned, relation=relation,
                      text_layer=text_layer, relation_note=relation_note, extras=extras)

    revise("st-chp8-p237-crespi-struck-by-ricci",
        subject="cand-0871", object_="cand-2154", predicate="reported_as_struck_by_ricci_spirit",
        claim="Haskell says the Grand Prince was not the only person impressed by Ricci’s work in Florence: after a brief visit to the Medici capital, Crespi was back in Bologna in February 1708 and wrote Ferdinand that Ricci’s spirit had struck him too.",
        quote=quotes["crespi_impression"], lines=(314, 317),
        qualification="Haskell reports the content of Crespi’s letter; the cited letter itself was not independently consulted.",
        mentioned=["cand-0871", "cand-3398", "cand-3397", "cand-1609", "cand-2154", "cand-8015"],
        relation=True, extras={"footnote_marker": 1, "quoted_speaker": "Giuseppe Maria Crespi"})
    revise("st-chp8-p237-crespi-style-compared-with-ricci",
        subject="cand-0871", object_="cand-2154", predicate="stylistic_innovations_compared_with_ricci",
        claim="Haskell compares Crespi’s innovations with Ricci’s: looser brushwork, a more painterly and spirited manner, greater individual temperament, and devotion to Venetian tradition.",
        quote=quotes["style_comparison"], lines=(317, 317),
        qualification="This is Haskell’s stylistic comparison, not an independently measured attribution or influence claim.",
        mentioned=["cand-0871", "cand-2154", "cand-8012", "cand-8013"], relation=False,
        relation_note="A stylistic comparison; Haskell does not claim that either artist influenced or collaborated with the other.",
        extras={"ocr_corrections": [{"source_line": 317, "ocr": "had'much", "print": "had much", "basis": "CHP-8.pdf physical page 43"}]})
    revise("st-chp8-p237-ricci-crespi-missed-meeting",
        subject="cand-0871", object_="cand-2154", predicate="missed_meeting_at_ferdinands_court_by_two_or_three_months",
        claim="Haskell says Crespi and Ricci missed meeting each other by two or three months at Ferdinand’s court.",
        quote=quotes["missed_meeting"], lines=(317, 317),
        qualification="The two artists are identified from the immediate paragraph context; Haskell gives an approximate interval.",
        mentioned=["cand-0871", "cand-2154", "cand-8010"], relation=True,
        relation_note="A source-reported non-meeting at a named court and approximate time; this is not a claim that they met.")
    revise("st-chp8-p237-ferdinand-encouraged-crespi",
        subject="cand-1609", object_="cand-0871", predicate="encouraged_crespi_to_present_massacre",
        claim="Haskell says Crespi received all possible encouragement from Ferdinand when he arrived in Florence at the beginning of 1708 to present his Massacre of the Innocents.",
        quote=quotes["encouragement"], lines=(317, 319),
        qualification="The pronouns refer to Crespi presenting his painting to Ferdinand; note 2 separately recounts the commission and Silva’s default.",
        mentioned=["cand-1609", "cand-0871", "cand-3397", "cand-0882"], relation=True,
        extras={"footnote_marker": 2})
    revise("st-chp8-p237-ferdinand-commissioned-still-lives",
        subject="cand-1609", object_="cand-8014", predicate="commissioned_still_lives_from_crespi",
        claim="After Crespi brought the Massacre of the Innocents to Ferdinand, the Grand Prince immediately commissioned a couple of still lives from him.",
        quote=quotes["still_life_commission"], lines=(320, 320),
        qualification="The still lives are an unspecified pair; titles and object identities are not supplied.",
        mentioned=["cand-1609", "cand-0871", "cand-8014"], relation=True,
        extras={"footnote_marker": 4})
    revise("st-chp8-p237-ferdinand-role-in-crespi-career",
        subject="cand-1609", object_="cand-0871", predicate="patronage_important_to_crespi_career",
        claim="Haskell considers Ferdinand of great importance in Crespi’s career, partly because of the patronage just described.",
        quote=quotes["career_importance"], lines=(321, 321),
        qualification="This is Haskell’s assessment of Ferdinand’s importance to Crespi’s career; the specific commissions and career shift are recorded separately.",
        mentioned=["cand-1609", "cand-0871"], relation=True,
        relation_note="The source explicitly connects Ferdinand’s patronage with Crespi’s career; the underlying causal interpretation remains Haskell’s.")
    revise("st-chp8-p237-note2-ferdinand-litigation",
        subject="cand-1609", object_="cand-8027", predicate="intervened_in_crespi_silva_disputes_and_litigation",
        claim="Haskell says Ferdinand took part in the disputes and litigation from which Crespi emerged victorious.",
        quote=quotes["litigation"], lines=(322, 322),
        qualification="This is Haskell’s report; the underlying letters are listed in the following citation sentence and were not independently consulted.",
        mentioned=["cand-1609", "cand-0871", "cand-2433", "cand-8027"], relation=True,
        text_layer="footnote report", extras={"footnote_marker": 2})
    revise("st-chp8-p237-note3-other-bolognese-artists",
        subject="cand-1609", object_="cand-1229", predicate="other_bolognese_artists_in_touch_with_ferdinand",
        claim="Haskell identifies Ercole Graziani as another Bolognese artist in touch with Ferdinand.",
        quote=quotes["graziani"], lines=(323, 323),
        qualification="This is the continuation of note 3 on the printed page; identity follows the indexed name and remains for S3 review.",
        mentioned=["cand-1609", "cand-1229"], relation=True,
        relation_note="The note explicitly says Graziani was in touch with Ferdinand; cited sources were not independently consulted.",
        text_layer="footnote 3 continuation", extras={"footnote_marker": 3})
    revise("st-chp8-p237-note5-return-to-bologna",
        subject="cand-0871", object_="cand-3398", predicate="back_in_bologna_by_26_february_1708",
        claim="Haskell says Crespi was back in Bologna by 26 February 1708.",
        quote=quotes["return_to_bologna"], lines=(325, 325),
        qualification="The date is the latest stated by Haskell and points to the dated letter in note 1; it does not independently establish the exact return day.",
        mentioned=["cand-0871", "cand-3398", "cand-8015"], relation=True,
        relation_note="The note explicitly locates Crespi back in Bologna by the cited date.",
        text_layer="footnote 5 report", extras={"footnote_marker": 5,
            "cross_reference_statement_ids": ["st-chp8-p237-note1-letter-citation"],
            "ocr_corrections": [{"source_line": 325, "ocr": "26,1708", "print": "26, 1708", "basis": "CHP-8.pdf physical page 43"}]})

    # The current unresolved row is converted into the first of five book-to-archive citations.
    citation_items = [
        ("st-chp8-p237-note2-silva-correspondence-citations", "cand-8017", "Ferdinand–Silva letter, Filza 5904 No. 96", quotes["silva_citations"], (322, 322)),
        ("st-chp8-p237-note2-cites-silva-letter-155", "cand-8018", "Ferdinand–Silva letter, Filza 5904 No. 155", quotes["silva_citations"], (322, 322)),
        ("st-chp8-p237-note2-cites-silva-letter-299", "cand-8019", "Ferdinand–Silva letter, Filza 5904 No. 299", quotes["silva_citations"], (322, 322)),
        ("st-chp8-p237-note2-cites-silva-letter-607", "cand-8020", "Ferdinand–Silva letter, Filza 5904 No. 607", quotes["silva_citations"], (322, 322)),
        ("st-chp8-p237-note2-cites-zambeccari-letter", "cand-8021", "Ferdinand’s letter to Eleonora Zambeccari, Filza 5897 No. 287", quotes["zambeccari_citation"], (322, 322)),
    ]
    for statement_id, archive_id, archive_label, quote, lines in citation_items:
        row = by_id.get(statement_id)
        if row is None:
            row = new_statement(statement_id, SEG237, "cand-2962", archive_id, "cites",
                lines=lines, **common_p237,
                claim=f"Haskell’s book cites {archive_label} in note 2.", quote=quote,
                qualification="This is a bibliographic locator only; the letter was not independently consulted and the citation does not itself verify Haskell’s litigation account.",
                mentioned=["cand-2962", "cand-1609", "cand-2433", archive_id], relation=True,
                text_layer="bibliographic pointer",
                relation_note="The book explicitly cites this archival item; no independent claim about the letter’s contents is made.",
                extras={"footnote_marker": 2})
            statements.append(row)
            by_id[statement_id] = row
        else:
            set_statement(row, subject="cand-2962", object_=archive_id, predicate="cites",
                claim=f"Haskell’s book cites {archive_label} in note 2.", quote=quote, lines=lines,
                page=237, physical=43,
                qualification="This is a bibliographic locator only; the letter was not independently consulted and the citation does not itself verify Haskell’s litigation account.",
                mentioned=["cand-2962", "cand-1609", "cand-2433", archive_id], relation=True,
                text_layer="bibliographic pointer",
                relation_note="The book explicitly cites this archival item; no independent claim about the letter’s contents is made.",
                extras={"footnote_marker": 2})
        if archive_id in {"cand-8017", "cand-8018", "cand-8019", "cand-8020"}:
            row["qualifiers"]["ocr_corrections"] = [{"source_line": 322, "ocr": "letters-between", "print": "letters between", "basis": "CHP-8.pdf physical page 43"}]

    for statement_id, archive_id, label, quote in [
        ("st-chp8-p237-note3-santi-in-touch-with-ferdinand", "cand-2356", "Giovan Gioseffo Santi", quotes["santi"]),
        ("st-chp8-p237-note3-dal-sole-in-touch-with-ferdinand", "cand-2480", "Giovan Gioseffo dal Sole", quotes["dal_sole"]),
    ]:
        row = new_statement(statement_id, SEG237, "cand-1609", archive_id,
            "other_bolognese_artists_in_touch_with_ferdinand", lines=(323, 324), **common_p237,
            claim=f"Haskell identifies {label} as another Bolognese artist in touch with Ferdinand.",
            quote=quote,
            qualification="This continues note 3 without a repeated marker; the identity follows the indexed name and remains for S3 review.",
            mentioned=["cand-1609", archive_id], relation=True,
            text_layer="footnote 3 continuation",
            relation_note="The note explicitly says this artist was in touch with Ferdinand; cited sources were not independently consulted.",
            extras={"footnote_marker": 3})
        if label.endswith("dal Sole"):
            row["qualifiers"]["ocr_corrections"] = [{"source_line": 323, "ocr": "sec letters", "print": "see letters", "basis": "CHP-8.pdf physical page 43"}]
        statements.append(row)
        by_id[statement_id] = row

    additions = [
        new_statement("st-chp8-p237-ricci-return-venice-before-letter", SEG237, "cand-2154", "cand-1609",
            "wrote_to_ferdinand_again_in_1708_after_returning_to_venice", lines=(312, 312), **common_p237,
            claim="Haskell says Ricci wrote to Ferdinand again in 1708 after returning to Venice.",
            quote="his return to Venice",
            qualification="This phrase completes the sentence begun at p.236 L309; the prior-page statement and this continuation together establish the sequence. The letter was not independently consulted.",
            mentioned=["cand-2154", "cand-1609", "cand-3401"], relation=True,
            text_layer="body continuation",
            relation_note="The source explicitly links Ricci’s 1708 letter to Ferdinand with his return to Venice.",
            extras={"continuation_from_segment_id": SEG236,
                    "continued_from_statement_id": "st-chp8-p236-ricci-wrote-to-ferdinand-again-1708"}),
        new_statement("st-chp8-p237-artists-pioneered-late-baroque-break", SEG237, "cand-0871", "cand-2154",
            "pioneered_break_with_late_baroque_conventions", lines=(317, 317), **common_p237,
            claim="Haskell describes Crespi and Ricci as two of the period’s most interesting artists, both pioneering a decisive break with late Baroque conventions.",
            quote=quotes["pioneering"],
            qualification="This is Haskell’s evaluative art-historical characterization, not a claim of influence or collaboration between the painters.",
            mentioned=["cand-0871", "cand-2154", "cand-8012"], relation=False,
            relation_note="A comparative period characterization; the source does not assert a formal relationship between the artists."),
        new_statement("st-chp8-p237-court-mood-affected-crespi", SEG237, "cand-8010", "cand-0871",
            "court_mood_profoundly_affected_artist", lines=(317, 317), **common_p237,
            claim="Haskell says the new mood at Ferdinand’s court profoundly affected Crespi.",
            quote=quotes["court_mood"],
            qualification="The plural ‘them both’ refers to Crespi and Ricci; this row records the effect on Crespi separately.",
            mentioned=["cand-8010", "cand-0871", "cand-2154"], relation=True,
            relation_note="Haskell explicitly attributes an effect on Crespi to the mood prevailing at Ferdinand’s court."),
        new_statement("st-chp8-p237-court-mood-affected-ricci", SEG237, "cand-8010", "cand-2154",
            "court_mood_profoundly_affected_artist", lines=(317, 317), **common_p237,
            claim="Haskell says the new mood at Ferdinand’s court profoundly affected Ricci.",
            quote=quotes["court_mood"],
            qualification="The plural ‘them both’ refers to Crespi and Ricci; this row records the effect on Ricci separately.",
            mentioned=["cand-8010", "cand-0871", "cand-2154"], relation=True,
            relation_note="Haskell explicitly attributes an effect on Ricci to the mood prevailing at Ferdinand’s court."),
        new_statement("st-chp8-p237-crespi-wishes-to-work-for-ferdinand", SEG237, "cand-0871", "cand-1609",
            "was_anxious_to_work_for_ferdinand", lines=(319, 319), **common_p237,
            claim="Haskell says Crespi was anxious to work for Ferdinand.", quote=quotes["crespi_wish"],
            qualification="This records Crespi’s stated wish for work, separately from Haskell’s argument about the court’s importance to artists outside Florence.",
            mentioned=["cand-0871", "cand-1609"], relation=True,
            relation_note="The source explicitly reports Crespi’s desire to work for Ferdinand."),
        new_statement("st-chp8-p237-court-important-outside-florence", SEG237, "cand-8010", None,
            "haskell_assessed_court_as_important_to_artists_outside_florence", lines=(319, 320), **common_p237,
            claim="Haskell treats Crespi’s wish to work for Ferdinand as evidence that the Grand Prince’s court had become important to artists outside Florence.",
            quote=quotes["court_importance"],
            qualification="This is Haskell’s generalization from Crespi’s case; the unnamed artists are not converted into a collective entity.",
            mentioned=["cand-8010", "cand-0871", "cand-1609", "cand-3397"], relation=False,
            relation_note="An authorial assessment about the court’s wider importance; no specific external artist group is named."),
        new_statement("st-chp8-p237-ferdinand-impressed-by-massacre", SEG237, "cand-1609", "cand-0871",
            "impressed_by_crespis_discrimination_and_enthusiasm", lines=(320, 320), **common_p237,
            claim="When Crespi brought the picture to Ferdinand, Haskell says the Grand Prince was deeply impressed by Crespi’s discrimination and enthusiasm.",
            quote=quotes["ferdinand_impressed"],
            qualification="The pronouns are read from the clause context: Crespi brought the picture and Ferdinand was impressed by Crespi’s discernment and enthusiasm.",
            mentioned=["cand-1609", "cand-0871", "cand-0882"], relation=True,
            relation_note="The source directly reports Ferdinand’s response to Crespi when he presented the painting."),
        new_statement("st-chp8-p237-still-life-choice-assessment", SEG237, "cand-1609", "cand-8014",
            "haskell_assessed_still_life_commission_as_curious_significant_choice", lines=(320, 320), **common_p237,
            claim="Haskell calls the still-life commission a curious and significant choice after the agitation of the history painting that introduced Crespi to Ferdinand.",
            quote=quotes["still_life_assessment"],
            qualification="This is Haskell’s interpretation of the subject choice; the pair of still lives remains unidentified.",
            mentioned=["cand-1609", "cand-0871", "cand-0882", "cand-8014"], relation=False,
            relation_note="An authorial assessment of the commission’s subject choice, not a distinct formal relation."),
        new_statement("st-chp8-p237-ferdinand-appreciated-intimate-talents", SEG237, "cand-1609", "cand-0871",
            "seems_among_first_to_appreciate_crespis_intimate_talents", lines=(321, 321), **common_p237,
            claim="Haskell says Ferdinand seems to have been among the first to appreciate the essentially intimate nature of Crespi’s talents.",
            quote=quotes["intimate_talents"],
            qualification="Haskell’s ‘seems’ and ‘among the first’ remain qualified; this is a claim about Ferdinand’s perception of Crespi’s work.",
            mentioned=["cand-1609", "cand-0871"], relation=False,
            relation_note="A qualified appraisal claim; it does not independently establish a formal relation."),
        new_statement("st-chp8-p237-pleasant-subject-commissions", SEG237, "cand-1609", "cand-0871",
            "commissioned_crespi_for_pleasant_subjects", lines=(321, 321), **common_p237,
            claim="Haskell says Ferdinand’s commissions to Crespi were all for ‘pleasant subjects’ (‘d’argomenti piacevoli’).",
            quote=quotes["pleasant_commissions"],
            qualification="This generalizes across the commissions described; it does not identify each work or title.",
            mentioned=["cand-1609", "cand-0871"], relation=True,
            relation_note="Haskell explicitly describes Ferdinand’s commissions to Crespi by subject and patron."),
        new_statement("st-chp8-p237-patronage-enabled-break-from-histories", SEG237, "cand-1609", "cand-0871",
            "patronage_enabled_crespi_to_break_from_history_painting", lines=(321, 321), **common_p237,
            claim="Haskell says Ferdinand’s support enabled Crespi to move away from the religious and secular histories that had formed most of his output.",
            quote=quotes["career_shift"],
            qualification="This is Haskell’s causal interpretation of Ferdinand’s support and Crespi’s change of subject matter.",
            mentioned=["cand-1609", "cand-0871"], relation=True,
            relation_note="The source expressly connects the protector’s support with Crespi’s departure from history painting."),
        new_statement("st-chp8-p237-crespi-first-florence-visit-duration", SEG237, "cand-0871", "cand-3397",
            "first_florence_visit_lasted_scarcely_more_than_a_month", lines=(321, 321), **common_p237,
            claim="Haskell says Crespi remained in Florence scarcely more than a month on this first visit.",
            quote=quotes["first_visit"],
            qualification="The source’s qualified duration is retained; note 5 says Crespi was back in Bologna by 26 February 1708.",
            mentioned=["cand-0871", "cand-3397", "cand-3398", "cand-8015"], relation=True,
            relation_note="A source-reported first visit to Florence with a qualified duration.",
            extras={"footnote_marker": 5,
                    "cross_reference_statement_ids": ["st-chp8-p237-note5-return-to-bologna"]}),
    ]
    statements.extend(additions)
    by_id.update({row["statement_id"]: row for row in additions})

    # Add the completed clause's first fragment to p.236; the p.237 row above links it.
    p236_row = new_statement("st-chp8-p236-ricci-wrote-to-ferdinand-again-1708", SEG236,
        "cand-2154", "cand-1609", "wrote_to_ferdinand_again_in_1708", lines=(309, 309),
        page=236, physical=42,
        claim="Haskell says Ricci wrote to Ferdinand again in 1708.",
        quote="Ricci wrote again to Ferdinand in 1708 after",
        qualification="The sentence continues across the page break; p.237 L312 specifies that the letter followed Ricci’s return to Venice. The letter was not independently consulted.",
        mentioned=["cand-2154", "cand-1609", "cand-3401"], relation=True,
        text_layer="body continuation",
        relation_note="The source directly reports renewed correspondence from Ricci to Ferdinand in 1708.")
    statements.append(p236_row)

    # Link the p.237 continuation to the newly separated p.236 letter claim.
    ret = by_id["st-chp8-p237-ricci-return-venice-before-letter"]
    ret["qualifiers"]["continuation_from_segment_id"] = SEG236
    ret["qualifiers"]["continued_from_statement_id"] = p236_row["statement_id"]
    eng = by_id["st-chp8-p237-ricci-england-1716"]
    set_statement(eng, subject="cand-2154", object_="cand-6809",
        predicate="travelled_to_england_and_remained_abroad_until_1716",
        claim="A year after returning to Venice, Ricci went to England and stayed abroad until 1716.",
        quote="but a year later he went to England and stayed abroad until\n1716.",
        lines=(312, 313), page=237, physical=43,
        qualification="A year later is measured from the return to Venice in the immediately preceding clause; England is the geographic destination, and S3 identity review remains pending.",
        mentioned=["cand-2154", "cand-3401", "cand-6809"], relation=True,
        relation_note="The source explicitly reports Ricci’s move to England and his stay abroad until 1716.",
        extras={"cross_reference_statement_ids": ["st-chp8-p237-ricci-return-venice-before-letter"]})

    # Make source mentions resolve to their actual named entities after row edits.
    if not any(r.get("mention_id") == "m-chp8-p237-crespi-innovation" and r.get("candidate_id") == "cand-0871" for r in mention_rows):
        raise SystemExit("p.237 Crespi mention correction did not apply")
    if not any(r.get("mention_id") == "m-chp8-p237-venetian-painter" and r.get("candidate_id") == "cand-2154" for r in mention_rows):
        raise SystemExit("p.237 Ricci mention correction did not apply")

    if {row["statement_id"] for row in statements} & NEW_IDS != NEW_IDS:
        raise SystemExit("not all planned statement rows were built")
    if any(row.get("segment_id") in {SEG236, SEG237} and
           (row.get("subject_candidate_id") == "cand-2179" or row.get("object_candidate_id") == "cand-2179")
           for row in statements):
        raise SystemExit("a p.236-p.237 person endpoint still uses Ricci's work candidate")

    preview = {
        "mode": "dry-run", "p237_existing": len(existing_p237),
        "p237_added": len(NEW_IDS) - 1, "p237_statement_total": sum(r.get("segment_id") == SEG237 for r in statements),
        "p236_added": 1, "statement_total": len(statements),
        "p236_p237_ricci_person_endpoint_fixes": sum(
            1 for r in statements if r.get("segment_id") in {SEG236, SEG237}
            and (r.get("subject_candidate_id") == "cand-2154" or r.get("object_candidate_id") == "cand-2154")),
        "mention_reassignments": [
            "p.236-p.237 Ricci mentions: cand-2179 -> cand-2154",
            "p.237 Venice location: cand-2179 -> cand-3401",
            "p.237 Crespi mentions: cand-0873 -> cand-0871",
        ],
        "new_statement_ids": sorted(NEW_IDS),
    }
    return preview, statements, fields, mention_rows


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
preview, statements, mention_fields, mention_rows = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (STATEMENTS, MENTIONS):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
atomic_write(STATEMENTS, jsonl_bytes(statements))
atomic_write(MENTIONS, csv_bytes(mention_fields, mention_rows))
preview["mode"] = "applied"
preview["backups"] = [
    str(STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX).relative_to(ROOT)),
    str(MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX).relative_to(ROOT)),
]
print(json.dumps(preview, ensure_ascii=False, indent=2))
