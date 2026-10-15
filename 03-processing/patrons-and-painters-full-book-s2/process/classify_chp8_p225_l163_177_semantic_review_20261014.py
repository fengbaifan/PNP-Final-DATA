"""Guarded S2 semantic review for printed p.225, body and notes lines 163-177."""
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
SEGMENT = "chp-8:08_CHP-8_sec_ii:l163-177"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p225_review.png"
BACKUP_SUFFIX = ".bak-s2-chp8-p225-l163-177-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "9b2b6d3f4527cc72c4598d54634d60559f41974c34bb92478581c801b01be8a4",
    CANDIDATES: "cb3ce497861298c246f085302cc93ea361c836fc346b69d3f924415aca8a2ce3",
    MENTIONS: "4bdba439ad754bd6b47086f78fd19c34db53d659f1ba9e182d8b73d421d13456",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PAGE_IMAGE: "a76d04b48d47a9e563135fd738baf251467fa275ff049e1dbc904d62ca3a9830",
}

CLASSIFICATIONS = {
    "st-chp8-p225-antique-and-christian-themes-as-genre": (False,
        "This is Haskell's conceptual account of an eighteenth-century shift in genre painting, not a relation between entities."),
    "st-chp8-p225-crespi-leto-surviving-work": (True,
        "The source identifies the surviving fable among Crespi's four works; its subject and Haskell's aesthetic assessment are separated below."),
    "st-chp8-p225-dido-interest-closes": (False,
        "This reports Haskell's reception/evaluative claim about the painting, not a relation between entities."),
    "st-chp8-p225-enlightenment-patron-inference-open": (True,
        "Haskell tentatively places Raimondo among an unnamed patron group; preserve the modality and the explicit open collective endpoint."),
    "st-chp8-p225-few-records-of-collection": (False,
        "This is a negative statement about surviving documentation, not a relation candidate."),
    "st-chp8-p225-modern-works-in-palace-rooms": (True,
        "The source explicitly places the unidentified modern works in other rooms of Raimondo's palace; Haskell's inference about Raimondo is separated below."),
    "st-chp8-p225-rome-cultural-exchange": (False,
        "This is Haskell's historical interpretation of dal Sole's visit, not a formal relation candidate."),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_jsonl(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def csv_bytes(path: Path, rows):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        headers = next(csv.reader(f))
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=headers, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        temp = Path(f.name)
        f.write(data)
    temp.replace(path)


def verify_inputs():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    checks = [
        (164, "own. canvas of"),
        (170, "all of whom turned out further scenes from the poem"),
        (171, "in-some of the other rooms"),
        (172, "shows with what engaging irony he could interpret"),
        (173, "who was also commissioned to paint pagan scenes"),
        (175, "those many patrons of the dawning Age of the Enlightenment"),
        (177, "Libra dei Conti"),
    ]
    for line, quote in checks:
        if quote not in lines[line - 1]:
            raise SystemExit(f"source excerpt mismatch at L{line}: {quote}")


def new_statement(statement_id, subject, object_, predicate, lines, claim, quote, *,
                  relation, note, mentioned, extra=None, speaker="Haskell"):
    q = {
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 225, "pdf_physical_page": 27, "claim": claim,
        "speaker": speaker, "text_layer": "body", "qualification": note,
        "mentioned_candidate_ids": mentioned, "relation_candidate": relation,
        "relation_candidate_note": note,
    }
    if extra:
        q.update(extra)
    return {
        "statement_id": statement_id, "segment_id": SEGMENT,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": q, "original_quote": quote,
        "origin": "book", "source_file": SOURCE_REL,
    }


def plan():
    statements = read_jsonl(STATEMENTS)
    candidates = read_csv(CANDIDATES)
    mentions = read_csv(MENTIONS)
    by_id = {r["statement_id"]: r for r in statements}
    seg_rows = [r for r in statements if r.get("segment_id") == SEGMENT]
    unset = {r["statement_id"] for r in seg_rows
             if "relation_candidate" not in r.get("qualifiers", {})}
    if len(seg_rows) != 15 or unset != set(CLASSIFICATIONS):
        raise SystemExit(f"unexpected p225 state: rows={len(seg_rows)} unset={sorted(unset)}")
    candidate_ids = {r["candidate_id"] for r in candidates}
    mention_ids = {r["mention_id"] for r in mentions}
    planned_ids = [
        "cand-12084", "m-chp8-p225-enlightenment-patrons",
        "st-chp8-p225-artist-produces-aeneid-scenes-gambarini",
        "st-chp8-p225-artist-produces-aeneid-scenes-franceschini",
        "st-chp8-p225-artist-produces-aeneid-scenes-lazzarini",
        "st-chp8-p225-artist-produces-aeneid-scenes-balestra",
        "st-chp8-p225-collection-no-inventory-survived",
        "st-chp8-p225-leto-work-depicts-leto",
        "st-chp8-p225-crespi-interpretive-irony",
        "st-chp8-p225-gambarini-manner-contrast",
        "st-chp8-p225-giaquinto-little-or-no-trace",
        "st-chp8-p225-modern-works-raimondo-awareness",
        "st-chp8-p225-n3-libro-records-franceschini-payment",
        "st-chp8-p225-dal-sole-working-on-andromache-canvas",
    ]
    if candidate_ids.intersection({"cand-12084"}) or mention_ids.intersection({"m-chp8-p225-enlightenment-patrons"}) or set(planned_ids[2:]).intersection(by_id):
        raise SystemExit("one or more planned p225 IDs already exist")

    for sid, (is_relation, note) in CLASSIFICATIONS.items():
        q = by_id[sid]["qualifiers"]
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note

    # Keep the four painter-to-work claims separate from Haskell's criticism.
    critical = by_id["st-chp8-p225-aeneid-artists-and-evaluation"]
    critical["predicate"] = "haskell_criticized_style_of_aeneid_scenes"
    critical["subject_candidate_id"] = "cand-7776"
    critical["object_candidate_id"] = None
    critical["qualifiers"].update({
        "source_line_start": 170, "source_line_end": 170,
        "claim": "Haskell judges the further Aeneid scenes clumsy and unconvincing and describes the large-scale romantic history-painting tradition as an empty academic exercise.",
        "speaker_judgment": True, "relation_candidate": False,
        "relation_candidate_note": "This preserves Haskell's art-historical and aesthetic judgment, not an entity relation.",
    })
    critical["original_quote"] = "all of whom turned out further scenes from the poem were not men from whom anything very new could be expected. Their works have a clumsiness and a lack of conviction which suggests that the tradition of large-scale romantic history painting to which they harked back had been drained of vitality and was now little more than an empty academic exercise."
    for slug, artist, name in [
        ("gambarini", "cand-1113", "Giuseppe Gambarini"),
        ("franceschini", "cand-1069", "Marcantonio Franceschini"),
        ("lazzarini", "cand-1368", "Gregorio Lazzarini"),
        ("balestra", "cand-0168", "Antonio Balestra"),
    ]:
        statements.append(new_statement(
            f"st-chp8-p225-artist-produces-aeneid-scenes-{slug}", artist, "cand-7776",
            "produced_further_aeneid_scenes_for_gallery", (168, 170),
            f"Haskell says {name} produced further Aeneid scenes for Raimondo's gallery.",
            "Giuseppe Gambarini2 and\nMarcantonio Franceschini in Bologna,3 Gregorio Lazzarini4 and Antonio Balestra in\nVenice,5 all of whom turned out further scenes from the poem",
            relation=True,
            note="The source explicitly includes this named painter in the group who produced further scenes; no individual scene is identified here.",
            mentioned=[artist, "cand-7776", "cand-7763"],
            extra={"artist_place_context": {"Franceschini": "Bologna", "Lazzarini": "Venice", "Balestra": "Venice"}.get(name.split()[-1])},
        ))

    collection = by_id["st-chp8-p225-collection-divided-and-no-inventory"]
    collection["predicate"] = "collection_pictures_repeatedly_divided_among_family"
    collection["qualifiers"]["claim"] = "Haskell says the Buonaccorsi collection's pictures were repeatedly split among members of the family."
    collection["qualifiers"]["relation_candidate"] = True
    collection["qualifiers"]["relation_candidate_note"] = "This records the reported division of the collection's pictures among family members; the separate no-inventory claim is below."
    collection["original_quote"] = "the pictures were repeatedly split up among members of the family"

    crespi = by_id["st-chp8-p225-crespi-leto-surviving-work"]
    crespi["predicate"] = "created_surviving_fable"
    crespi["qualifiers"].update({
        "claim": "Of Crespi's four fables for Raimondo, Haskell identifies Leto turning the Shepherds into Frogs as the one that survived.",
        "mentioned_candidate_ids": ["cand-0871", "cand-7775", "cand-0880", "cand-7773"],
        "relation_candidate": True,
        "relation_candidate_note": "The source explicitly identifies this work as the surviving fable among Crespi's four reported paintings.",
    })
    crespi["original_quote"] = "the one that has survived—Leto turning the Shepherds into Frogs"

    gamb = by_id["st-chp8-p225-gambarini-pagan-scenes"]
    gamb["qualifiers"]["claim"] = "Haskell says Giuseppe Gambarini was also commissioned to paint pagan scenes."
    gamb["qualifiers"]["mentioned_candidate_ids"] = ["cand-1113", "cand-7778"]
    gamb["qualifiers"]["relation_candidate"] = True
    gamb["original_quote"] = "who was also commissioned to paint pagan scenes"

    gia = by_id["st-chp8-p225-giaquinto-reported-work-and-little-trace"]
    gia["predicate"] = "reported_to_have_worked_for_buonaccorsi_family"
    gia["qualifiers"]["claim"] = "Haskell reports that Corrado Giaquinto worked for the Buonaccorsi family."
    gia["qualifiers"]["mentioned_candidate_ids"] = ["cand-1165", "cand-7729"]
    gia["qualifiers"]["relation_candidate"] = True
    gia["qualifiers"]["relation_candidate_note"] = "The source explicitly reports work for the Buonaccorsi; the separate lack-of-trace claim is recorded below."
    gia["original_quote"] = "who is reported to have worked for the Buonaccorsi"

    modern = by_id["st-chp8-p225-modern-works-in-palace-rooms"]
    modern["predicate"] = "located_in_other_palace_rooms"
    modern["qualifiers"].update({
        "source_line_start": 171, "source_line_end": 171,
        "claim": "Haskell says unidentified works by more interesting and modern painters were found in other rooms of Raimondo's palace.",
        "mentioned_candidate_ids": ["cand-7779", "cand-7731"],
        "relation_candidate": True,
        "relation_candidate_note": "The source explicitly locates the unidentified works in other rooms of the palace; the following inference about Raimondo is separated below.",
        "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 171,
                             "ocr": "in-some", "print": "in some",
                             "basis": "CHP-8.pdf physical page 27."}],
    })
    modern["original_quote"] = "Indeed it was in-some of the other rooms in Raimondo’s palace that works by the more interesting and ‘modern’ painters of the day were to be found"

    dal_sole = by_id["st-chp8-p225-dal-sole-visits-dido"]
    dal_sole["predicate"] = "visited_palace_to_see_arrived_painting"
    dal_sole["qualifiers"].update({
        "source_line_start": 165, "source_line_end": 166,
        "claim": "After hearing that Solimena's Dido painting had arrived, Giovan Gioseffo dal Sole insisted on coming to the Buonaccorsi palace to see it.",
        "mentioned_candidate_ids": ["cand-2480", "cand-2486", "cand-7731"],
        "relation_candidate": True,
        "relation_candidate_note": "The source directly reports the artist's visit to see the arriving painting.",
    })
    dal_sole["original_quote"] = "heard of its arrival and insisted on coming to the\nBuonaccorsi palace to see it"

    enlightenment = by_id["st-chp8-p225-enlightenment-patron-inference-open"]
    enlightenment["object_candidate_id"] = "cand-12084"
    enlightenment["predicate"] = "possibly_member_of_patron_group_with_public_private_taste_contrast"
    enlightenment["qualifiers"].update({
        "claim": "Haskell tentatively suggests Raimondo may have belonged to a group of Enlightenment-era patrons whose public galleries looked to the past while their private apartments held smaller, more intimate pictures.",
        "mentioned_candidate_ids": ["cand-0467", "cand-12084", "cand-0974", "cand-7765"],
        "relation_candidate": True,
        "relation_candidate_note": "The explicit 'may have been among' relation is preserved as Haskell's tentative comparison; the group remains unnamed and open.",
        "modality": "may have been among",
    })

    n3 = by_id["st-chp8-p225-n3-franceschini-mercury-painting"]
    n3["predicate"] = "painted_work_for"
    n3["qualifiers"]["claim"] = "Haskell's footnote reports that Franceschini painted Mercury awaking Aeneas."
    n3["qualifiers"]["mentioned_candidate_ids"] = ["cand-1069", "cand-1071", "cand-7772", "cand-4164"]
    n3["qualifiers"]["relation_candidate"] = True
    n3["original_quote"] = "Franceschini painted Mercury awaking Aeneas"

    family = next(r for r in candidates if r["candidate_id"] == "cand-7729")
    family["canonical_name"] = "Buonaccorsi family"
    family["suggested_type"] = "family"
    family["detail"] = "Haskell describes Raimondo as born into this old, extended family on p.223 and refers to its members as the Buonaccorsi on p.225; exact genealogy and membership remain unresolved."
    leto_work = next(r for r in candidates if r["candidate_id"] == "cand-0880")
    leto_work["canonical_name"] = "Leto turning the Shepherds into Frogs (painting by Giuseppe Maria Crespi)"
    leto_work["detail"] = "Work-specific index candidate for the one fable Haskell says survived among Crespi's four works; do not infer a present location from this passage."

    patron_group = {
        "candidate_id": "cand-12084", "index_entry_id": "",
        "canonical_name": "Enlightenment-era patrons with contrasting public-gallery and private-apartment tastes (unnamed group)",
        "index_page_range": "", "suggested_type": "", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell tentatively describes patrons whose public galleries looked to the past while private apartments held smaller, more intimate pictures; membership and extent are not supplied.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L175",
    }
    candidates.append(patron_group)
    source_text = "\n".join(SOURCE.read_text(encoding="utf-8-sig").splitlines()[162:177])
    if source_text[2219:2277] != "those many patrons of the dawning Age of the Enlightenment":
        raise SystemExit("Enlightenment patron-group mention span mismatch")
    mentions.append({
        "mention_id": "m-chp8-p225-enlightenment-patrons", "segment_id": SEGMENT,
        "candidate_id": "cand-12084",
        "surface_form": "those many patrons of the dawning Age of the Enlightenment",
        "start_char": "2219", "end_char": "2277",
        "note": "Unnamed group in Haskell's tentative comparison; its membership and extent are not given.",
    })

    # New atomic claims separated from existing composites.
    additions = [
        new_statement("st-chp8-p225-collection-no-inventory-survived", "cand-7765", None,
            "no_inventory_survived_for_collection", (175, 175),
            "Haskell says no inventory of the Buonaccorsi collection survived.",
            "no inventory has survived", relation=False,
            note="This is a negative documentation claim, not a historical relation candidate.",
            mentioned=["cand-7765"]),
        new_statement("st-chp8-p225-leto-work-depicts-leto", "cand-0880", "cand-7773",
            "depicts_mythological_figure", (172, 172),
            "The surviving fable depicts Leto turning the Shepherds into Frogs.",
            "Leto turning the Shepherds into Frogs", relation=True,
            note="The source identifies the named mythological figure in the surviving painting's subject.",
            mentioned=["cand-0880", "cand-7773"]),
        new_statement("st-chp8-p225-crespi-interpretive-irony", "cand-0880", None,
            "haskell_praises_crespis_interpretive_irony", (172, 172),
            "Haskell praises the engaging irony with which Crespi interpreted classical mythology.",
            "shows with what engaging irony he could interpret the stories of classical mythology",
            relation=False, note="This is Haskell's aesthetic judgment of Crespi's interpretation.",
            mentioned=["cand-0871", "cand-0880"], extra={"speaker_judgment": True}),
        new_statement("st-chp8-p225-gambarini-manner-contrast", "cand-1113", None,
            "haskell_contrasts_gambarini_manner_with_crespi", (173, 173),
            "Haskell contrasts Gambarini's placid, sensual manner with Crespi's humour.",
            "was rather different: more placid and more sensual and with none of Crespi’s humour",
            relation=False, note="This is the author's stylistic comparison, separate from Gambarini's commission.",
            mentioned=["cand-1113", "cand-0871"], extra={"speaker_judgment": True}),
        new_statement("st-chp8-p225-giaquinto-little-or-no-trace", "cand-1165", None,
            "author_reports_little_or_no_trace_of_artist", (175, 175),
            "Haskell says little or no trace can be found of Corrado Giaquinto.",
            "Little or no trace can be found of Corrado Giaquinto", relation=False,
            note="This is an authorial statement about surviving evidence, not an entity relation.",
            mentioned=["cand-1165"]),
        new_statement("st-chp8-p225-modern-works-raimondo-awareness", "cand-0467", None,
            "haskell_infers_raimondo_awareness_of_painters_qualities", (171, 172),
            "Haskell infers from the contrast between the gallery scenes and other works that Raimondo understood the painters' essential qualities.",
            "the striking contrast between these and the men who painted the scenes from the Aeneid shows that\nRaimondo must have had a genuine awareness of their essential qualities",
            relation=False, note="This preserves Haskell's inference as an attributed interpretation, not a formal relation.",
            mentioned=["cand-0467", "cand-7779", "cand-7776"], extra={"speaker_judgment": True}),
        new_statement("st-chp8-p225-n3-libro-records-franceschini-payment", "cand-7766", "cand-1069",
            "account_book_records_payment_to_artist", (177, 177),
            "Haskell's footnote says an entry in Franceschini's Libro dei Conti records that he was paid 1000 lire.",
            "an entry in the artist’s Libra dei Conti (Biblioteca Comunale, Bologna—MS. B.4067) which shows that he was paid 1000 lire",
            relation=True, note="This is Haskell's report of a manuscript entry; the account book itself has not been consulted.",
            mentioned=["cand-7766", "cand-1069"], extra={
                "amount": "1000 lire", "reported_source": "Libro dei Conti",
                "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 177,
                    "ocr": "Libra dei Conti", "print": "Libro dei Conti",
                    "basis": "CHP-8.pdf physical page 27."}],
            }),
        new_statement("st-chp8-p225-dal-sole-working-on-andromache-canvas", "cand-2480", "cand-2481",
            "working_on_canvas_in", (164, 165),
            "Haskell says Giovan Gioseffo dal Sole was working in Bologna on his canvas Andromache weeping before Aeneas.",
            "Giovan Gioseffo dal Sole, who was working on his own. canvas of\nAndromache weeping before Aeneas",
            relation=True, note="The page image reads 'own canvas'; the work is an existing work-specific index candidate.",
            mentioned=["cand-2480", "cand-2481", "cand-3398"], extra={
                "location_candidate_id": "cand-3398",
                "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 164,
                    "ocr": "own.", "print": "own", "basis": "CHP-8.pdf physical page 27."}],
            }),
    ]
    statements.extend(additions)

    # Preserve the OCR note even when the cleaned quote no longer includes the error.
    dal_sole["qualifiers"]["ocr_corrections"] = [{
        "source_file": SOURCE_REL, "source_line": 164, "ocr": "own.", "print": "own",
        "basis": "CHP-8.pdf physical page 27."
    }]
    n3["qualifiers"]["ocr_corrections"] = [{
        "source_file": SOURCE_REL, "source_line": 177, "ocr": "Libra dei Conti", "print": "Libro dei Conti",
        "basis": "CHP-8.pdf physical page 27."
    }]

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for sid in ["st-chp8-p225-aeneid-artists-and-evaluation",
                "st-chp8-p225-collection-divided-and-no-inventory",
                "st-chp8-p225-crespi-leto-surviving-work",
                "st-chp8-p225-dido-interest-closes",
                "st-chp8-p225-enlightenment-patron-inference-open",
                "st-chp8-p225-gambarini-pagan-scenes",
                "st-chp8-p225-giaquinto-reported-work-and-little-trace",
                "st-chp8-p225-modern-works-in-palace-rooms",
                "st-chp8-p225-n3-franceschini-mercury-painting",
                "st-chp8-p225-dal-sole-visits-dido"]:
        q = by_id[sid]["qualifiers"]
        excerpt = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
        if by_id[sid]["original_quote"] not in excerpt:
            raise SystemExit(f"source quote mismatch: {sid}")
    for row in additions:
        q = row["qualifiers"]
        excerpt = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
        if row["original_quote"] not in excerpt:
            raise SystemExit(f"source quote mismatch: {row['statement_id']}")
    artist_quote = "Giuseppe Gambarini2 and\nMarcantonio Franceschini in Bologna,3 Gregorio Lazzarini4 and Antonio Balestra in\nVenice,5 all of whom turned out further scenes from the poem"
    if artist_quote not in "\n".join(source_lines[167:170]):
        raise SystemExit("artist group quote mismatch")

    final = [r for r in statements if r.get("segment_id") == SEGMENT]
    summary = {
        "p225_original_rows": len(seg_rows), "new_statements": len(additions) + 4,
        "new_candidates": 1, "new_mentions": 1,
        "classified_previously_unset": len(CLASSIFICATIONS),
        "candidate_names_corrected": 2,
        "p225_final_statements": len(final),
        "p225_final_true": sum(r["qualifiers"].get("relation_candidate") is True for r in final),
        "p225_final_false": sum(r["qualifiers"].get("relation_candidate") is False for r in final),
        "p225_final_unset": sum("relation_candidate" not in r.get("qualifiers", {}) for r in final),
    }
    if (summary["p225_final_statements"], summary["p225_final_true"],
            summary["p225_final_false"], summary["p225_final_unset"]) != (27, 16, 11, 0):
        raise SystemExit(f"unexpected p225 plan totals: {summary}")
    return write_jsonl(statements), csv_bytes(CANDIDATES, candidates), csv_bytes(MENTIONS, mentions), summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write guarded plan; default dry-run")
    args = parser.parse_args()
    verify_inputs()
    statement_bytes, candidate_bytes, mention_bytes, summary = plan()
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", **summary}, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    verify_inputs()
    outputs = {STATEMENTS: statement_bytes, CANDIDATES: candidate_bytes, MENTIONS: mention_bytes}
    for path in outputs:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if backup.read_bytes() != path.read_bytes():
                raise SystemExit(f"existing backup differs: {backup.name}")
        else:
            shutil.copy2(path, backup)
        if sha(backup.read_bytes()) != EXPECTED[path]:
            raise SystemExit(f"backup hash mismatch: {backup.name}")
    for path, data in outputs.items():
        atomic_write(path, data)
    print("written_sha256=" + json.dumps({p.name: sha(p.read_bytes()) for p in outputs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
