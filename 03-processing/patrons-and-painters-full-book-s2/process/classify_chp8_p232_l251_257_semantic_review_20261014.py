"""Guarded S2 semantic review for printed p.232, body lines 251-257."""
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
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l251-257"
BACKUP_SUFFIX = ".bak-s2-chp8-p232-l251-257-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "9262b5b7ce68a7be591d12f993eb83335ff70c6a24bd429e00f94d7703a417b4",
    CANDIDATES: "bac8d8c5bf76ce80d8298549f1ed5e82da34905d4d3eb11d7f54ab33a3e25602",
    COVERAGE: "b5800f382f7e6f61795b74774bb766cfea519576d57a9c0717e504decaf6f45b",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
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


def cut(line: str, start: str, end: str | None = None, *, include_end: bool = False) -> str:
    a = line.find(start)
    if a < 0:
        raise SystemExit(f"source fragment not found: {start!r}")
    if end is None:
        return line[a:].rstrip()
    b = line.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f"source end fragment not found after {start!r}: {end!r}")
    if include_end:
        b += len(end)
    return line[a:b].rstrip()


def plan():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

    segments = read_jsonl(SEGMENTS)
    meta = {row["segment_id"]: row for row in segments}.get(SEGMENT)
    if not meta or (meta["line_start"], meta["line_end"]) != (251, 257):
        raise SystemExit("unexpected p.232 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if sha("\n".join(source_lines[250:257]).encode("utf-8")) != meta["sha256"]:
        raise SystemExit("p.232 source segment hash mismatch")

    candidate_fields, candidates = read_csv(CANDIDATES)
    statements = read_jsonl(STATEMENTS)
    coverage_fields, coverage = read_csv(COVERAGE)
    by_id = {row["statement_id"]: row for row in statements}
    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(target_rows) != 22:
        raise SystemExit(f"expected 22 migrated p.232 statements; got {len(target_rows)}")
    if any(row.get("qualifiers", {}).get("relation_candidate") not in (True, False) for row in target_rows):
        raise SystemExit("p.232 has an unexpected unclassified or invalid relation_candidate value")
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"], coverage_row["source_line_ranges"]) != ("reviewed", "complete", "L251-257"):
        raise SystemExit(f"unexpected p.232 coverage state: {coverage_row}")

    l252, l253, l254, l255, l256, l257 = (source_lines[n - 1] for n in range(252, 258))
    quotes = {
        "st-chp8-p232-cassana-agent": l252 + "\n" + l253[:l253.index(" From these letters")],
        "st-chp8-p232-ferdinand-approval-vocabulary": (
            cut(l253, "The expressions which he uses most frequently") + "\n" +
            cut(l254, "—vague terms", " painting.", include_end=True)
        ),
        "st-chp8-p232-veronese-colour-invention": cut(l254, "a Veronese is admired because", "; an engraving is"),
        "st-chp8-p232-engraving-appraisal": cut(l254, "an engraving is", "; an artist working for him"),
        "st-chp8-p232-instructions-to-unnamed-artists": cut(l254, "an artist working for him", "; another is told"),
        "st-chp8-p232-ferdinand-told-second-artist-meno-flemmatico": cut(l254, "another is told to be", ". He sees a Maffei"),
        "st-chp8-p232-maffei-painting-impasto": cut(l254, "He sees a Maffei", "; in Livorno"),
        "st-chp8-p232-bassanino-rape-sabines": cut(l254, "in Livorno there is a Rape of the Sabines", " which looks like"),
        "st-chp8-p232-bassanino-appraisal": cut(l254, "which looks like a Strozzi", "; a Van Dyck"),
        "st-chp8-p232-vandyck-bozzetto": cut(l254, "a Van Dyck bozzetto is", ". From these expressions", include_end=True),
        "st-chp8-p232-brushstroke-colour-vs-drawing": cut(l254, "From these expressions and from many more", " at the time.", include_end=True),
        "st-chp8-p232-belle-matiere": cut(l254, "He showed an acute sensitivity", "eighteenth-century connoisseurs.", include_end=True),
        "st-chp8-p232-artistic-discrimination": cut(l254, "Like many of these connoisseurs", "appreciation of pictures.", include_end=True),
        "st-chp8-p232-rubens-examination": cut(l254, "In a Rubens", "foliage of the trees;", include_end=True),
        "st-chp8-p232-packing-instructions": cut(l254, "he gives detailed practical instructions", "to pack a picture;", include_end=True),
        "st-chp8-p232-read-lives-painters": cut(l254, "he reads through Lives of the Painters;"),
        "st-chp8-p232-jokes-on-attribution": cut(l254, "he jokes about those"),
        "st-chp8-p232-madonna-collo-lungo-purchase": cut(l255, "in 1698 he bought Parmigianino’s", "—but were vital"),
        "st-chp8-p232-contemporary-patronage-conflict": cut(l255, "Yet with two conspicuous exceptions") + "\n" + l256,
        "st-chp8-p232-collaborative-patronage": cut(l257, "For Ferdinand art patronage involved", "between prince and painter.", include_end=True),
        "st-chp8-p232-eagle-ganymede-example": cut(l257, "This might range from sending", "3 His attitude"),
        "st-chp8-p232-fumiani-david-instruction": cut(l257, "His attitude is clearly shown", " He insisted on always seeing"),
        "st-chp8-p232-modelli-order-and-review-open": cut(l257, "He insisted on always seeing tnodelli"),
    }
    if set(quotes) != {row["statement_id"] for row in target_rows} | {"st-chp8-p232-bassanino-appraisal"}:
        raise SystemExit("quote map does not cover the p.232 statement set")

    for statement_id, quote in quotes.items():
        if statement_id == "st-chp8-p232-bassanino-appraisal":
            continue
        row = by_id[statement_id]
        if quote not in "\n".join(source_lines[250:257]):
            raise SystemExit(f"quote is not an exact p.232 source span: {statement_id}")
        row["original_quote"] = quote

    # Review Haskell's claims against the scan and correct the mistaken relation endpoint.
    notes = {
        "st-chp8-p232-artistic-discrimination": "Haskell's evaluative comparison of Ferdinand's qualities and collecting class; this broad judgment is content, not a discrete graph relation.",
        "st-chp8-p232-belle-matiere": "Attributed description of artistic sensitivity and a general account of later connoisseurial taste; no discrete work or formal relation is asserted.",
        "st-chp8-p232-brushstroke-colour-vs-drawing": "Haskell's interpretive account of aesthetic preference and Roman art theory, not a discrete formal relation.",
        "st-chp8-p232-cassana-agent": "The p.231 sentence closes here: Cassana is explicitly Ferdinand's agent in Venice from 1698; retain the person-to-person role with its reported date.",
        "st-chp8-p232-collaborative-patronage": "This is Haskell's broad comparison of patronage practice. The text names no individual painter in this general claim, so no object endpoint is assigned.",
        "st-chp8-p232-contemporary-patronage-conflict": "This is Haskell's interpretive assessment of Ferdinand's taste against contemporary art theory; the passage does not establish a formal relation to the Baroque as an entity.",
        "st-chp8-p232-eagle-ganymede-example": "The source says Ferdinand sent an eagle to his unnamed court painter; the painter is the relation endpoint, while the eagle and Ganymede composition remain contextual mentions.",
        "st-chp8-p232-engraving-appraisal": "This is an aesthetic appraisal of an unidentified engraving; the current relation vocabulary has no discrete appraisal relation, so preserve it as source content.",
        "st-chp8-p232-ferdinand-approval-vocabulary": "This describes the language of Ferdinand's letters and Haskell's interpretation of it, rather than a formal relation.",
        "st-chp8-p232-ferdinand-told-second-artist-meno-flemmatico": "A specific reported instruction from Ferdinand to a separately unidentified second artist; keep the endpoint distinct from the first unnamed painter.",
        "st-chp8-p232-fumiani-david-instruction": "The quoted instruction names Fumiani as the intended painter and Cassana as the letter recipient; the exact composition remains unidentified.",
        "st-chp8-p232-instructions-to-unnamed-artists": "A specific reported instruction from Ferdinand to an unnamed artist; do not merge this artist with the separately described second painter.",
        "st-chp8-p232-jokes-on-attribution": "This is a biographical anecdote about Ferdinand's jokes; it supplies no named interlocutor or work endpoint.",
        "st-chp8-p232-madonna-collo-lungo-purchase": "The source explicitly reports Ferdinand's 1698 acquisition of the named painting; version and present location remain unspecified.",
        "st-chp8-p232-maffei-painting-impasto": "This records Ferdinand's reaction to an unidentified Maffei painting; it is an attributed appraisal, not a formal relation candidate.",
        "st-chp8-p232-modelli-order-and-review-open": "This continues into p.233 and records a general practice involving modelli, not a relation to an identified model or work.",
        "st-chp8-p232-packing-instructions": "The passage reports a general practical activity and names no recipient or specific picture, so no formal relation endpoint is assigned.",
        "st-chp8-p232-read-lives-painters": "The text identifies only a general Lives of the Painters text; retain the reading claim without inventing a bibliographic identity or formal relation.",
        "st-chp8-p232-rubens-examination": "This reports Ferdinand's examination and attribution suspicion concerning an unidentified Rubens painting; it is not a formal relation candidate.",
        "st-chp8-p232-vandyck-bozzetto": "This is an attributed appraisal of an unidentified Van Dyck sketch, not a formal relation candidate.",
        "st-chp8-p232-veronese-colour-invention": "This is Ferdinand's attributed appraisal of an unidentified Veronese painting; its title and present identity remain open.",
        "st-chp8-p232-bassanino-rape-sabines": "The source explicitly places this identified-by-description painting at Livorno in the letter context; no exact observation date or current location is supplied.",
    }
    for statement_id, note in notes.items():
        if statement_id not in by_id:
            raise SystemExit(f"missing reviewed statement {statement_id}")
        by_id[statement_id]["qualifiers"]["relation_candidate_note"] = note

    cassana = by_id["st-chp8-p232-cassana-agent"]
    cassana["qualifiers"].update({
        "source_line_start": 252, "source_line_end": 253,
        "claim": "Haskell identifies Niccolò Cassana as a Genoese artist who acted as Ferdinand's agent in Venice from 1698.",
        "qualification": "The passage reports the role and date; the cited correspondence is not independently consulted.",
        "mentioned_candidate_ids": ["cand-1609", "cand-0593", "cand-3401"],
    })

    approval = by_id["st-chp8-p232-ferdinand-approval-vocabulary"]
    approval["qualifiers"].update({
        "claim": "Haskell says Ferdinand most often expressed approval in his letters with gran gusto or buon gusto, terms he considers vague but revealing of his relish for painting.",
        "qualification": "This is Haskell's reading of the wording in letters; the cited correspondence was not independently consulted.",
        "mentioned_candidate_ids": ["cand-1609", "cand-1625"],
        "relation_candidate": False,
    })

    collab = by_id["st-chp8-p232-collaborative-patronage"]
    collab["object_candidate_id"] = None
    collab["qualifiers"].update({
        "claim": "Haskell characterizes Ferdinand's patronage as involving more collaboration between prince and painter than was usual.",
        "qualification": "The source makes a general comparison and does not identify a particular painter as the counterpart in this claim.",
        "mentioned_candidate_ids": ["cand-1609"],
        "relation_candidate": False,
    })

    conflict = by_id["st-chp8-p232-contemporary-patronage-conflict"]
    conflict["qualifiers"].update({
        "claim": "Haskell says the general direction of art theory conflicted with Ferdinand's personal tastes and made it difficult to find painters unaffected by the period's classicising doctrines, apart from two exceptions.",
        "qualification": "This is Haskell's interpretive assessment; the two exceptions and individual painters are not identified in this sentence.",
        "mentioned_candidate_ids": ["cand-1609", "cand-3569"],
        "relation_candidate": False,
    })

    bassanino = by_id["st-chp8-p232-bassanino-rape-sabines"]
    bassanino["subject_candidate_id"] = "cand-7882"
    bassanino["object_candidate_id"] = "cand-6716"
    bassanino["predicate"] = "painting_reported_at_livorno_in_ferdinands_letter_context"
    bassanino["qualifiers"].update({
        "claim": "Haskell's passage reports a Rape of the Sabines by Virgilio Bassanino at Livorno.",
        "speaker": "Haskell",
        "qualification": "The text places the painting at Livorno in the context of Ferdinand's letters; it supplies no exact observation date and does not establish its present location.",
        "mentioned_candidate_ids": ["cand-7882", "cand-6716", "cand-0255"],
        "relation_candidate": True,
    })
    bassanino_appraisal = {
        "statement_id": "st-chp8-p232-bassanino-appraisal",
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-1609",
        "object_candidate_id": "cand-7882",
        "predicate": "compared_bassanino_painting_to_strozzi_and_praised_brushstroke",
        "qualifiers": {
            "source_line_start": 254, "source_line_end": 254,
            "printed_page": 232, "pdf_physical_page": 34,
            "claim": "In Haskell's account of Ferdinand's expressions, the Rape of the Sabines looks like a Strozzi and has a brio di pennello grande.",
            "speaker": "Ferdinand (as reported through Haskell)",
            "text_layer": "reported appraisal",
            "qualification": "The compared Strozzi is not identified. This is an aesthetic appraisal, not a formal relation type.",
            "mentioned_candidate_ids": ["cand-1609", "cand-7882", "cand-0255", "cand-7914", "cand-1625"],
            "relation_candidate": False,
            "relation_candidate_note": "This preserves Ferdinand's reported comparison and brushstroke appraisal separately from the painting's reported location.",
            "speaker_judgment": True,
        },
        "original_quote": quotes["st-chp8-p232-bassanino-appraisal"],
        "origin": "book",
        "source_file": SOURCE_REL,
    }
    if bassanino_appraisal["original_quote"] not in "\n".join(source_lines[250:257]):
        raise SystemExit("Bassanino appraisal quote is not an exact source span")
    if bassanino_appraisal["statement_id"] in by_id:
        raise SystemExit("Bassanino appraisal statement already exists")

    eagle = by_id["st-chp8-p232-eagle-ganymede-example"]
    eagle["object_candidate_id"] = "cand-7890"
    eagle["predicate"] = "sent_eagle_to_unnamed_court_painter_for_ganymede_composition"
    eagle["qualifiers"].update({
        "claim": "Haskell gives an example in which Ferdinand supplied an eagle to his unnamed court painter to help with a Ganymede composition.",
        "qualification": "The source does not establish whether the eagle was a live animal, model, or another aid; the composition's maker and completion are unidentified.",
        "mentioned_candidate_ids": ["cand-1609", "cand-7890", "cand-7891", "cand-7892"],
        "relation_candidate": True,
        "relation_candidate_note": notes["st-chp8-p232-eagle-ganymede-example"],
    })

    modelli = by_id["st-chp8-p232-modelli-order-and-review-open"]
    modelli["predicate"] = "insisted_on_seeing_modelli_of_ordered_pictures"
    modelli["qualifiers"].update({
        "claim": "Haskell says Ferdinand insisted on always seeing the modelli of pictures he ordered.",
        "qualification": "The purposes of this practice continue on p.233 and are linked in the next-page statement.",
    })

    term_topic = next((row for row in candidates if row["candidate_id"] == "cand-1625"), None)
    if not term_topic or term_topic["suggested_type"] != "term" or term_topic["sub_entry"] != "taste in painting":
        raise SystemExit("unexpected index candidate for Ferdinand's painting taste")
    term_topic["canonical_name"] = "Ferdinand's taste in painting (indexed topic)"
    term_topic["detail"] = "Index subentry under Grand Prince Ferdinand's entry, covering his taste in painting. Treat this as an aesthetic topic, not as a second person entity; S2 references are source-attributed interpretations."

    additions = [bassanino_appraisal]
    target_final = [row for row in target_rows] + additions
    counts = {"true": 0, "false": 0, "unset": 0}
    for row in target_final:
        value = row["qualifiers"].get("relation_candidate")
        counts["true" if value is True else "false" if value is False else "unset"] += 1
    if counts["unset"]:
        raise SystemExit(f"p.232 remains unclassified: {counts}")

    coverage_row["note"] += (
        " Semantic review 2026-10-14 rechecked all 22 body statements against CHP-8.pdf physical page 34; "
        "narrowed overbroad quote spans, split the Bassanino painting's reported Livorno location from Ferdinand's appraisal, "
        "corrected the eagle-supply relation endpoint to the unnamed court painter, and closed the modelli continuation at p.233."
    )
    preview = {
        "mode": "dry-run", "segment": SEGMENT, "pdf_physical_page": 34,
        "existing_statements_reviewed": len(target_rows),
        "new_statements": [bassanino_appraisal["statement_id"]],
        "quotes_narrowed": len(quotes) - 1,
        "endpoint_corrections": [
            {"statement_id": "st-chp8-p232-eagle-ganymede-example", "object_candidate_id": "cand-7890", "role": "unnamed court painter"},
            {"statement_id": "st-chp8-p232-bassanino-rape-sabines", "subject_candidate_id": "cand-7882", "object_candidate_id": "cand-6716", "role": "painting reported at Livorno"},
        ],
        "candidate_title_correction": "cand-1625: Ferdinand's taste in painting (indexed topic)",
        "final_statement_counts": counts,
    }
    payload = {
        STATEMENTS: jsonl_bytes(statements + additions),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        COVERAGE: csv_bytes(coverage_fields, coverage),
    }
    return preview, payload


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.232 S2 review")
args = parser.parse_args()
preview, payload = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
for path in (STATEMENTS, CANDIDATES, COVERAGE):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
for path, data in payload.items():
    atomic_write(path, data)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
