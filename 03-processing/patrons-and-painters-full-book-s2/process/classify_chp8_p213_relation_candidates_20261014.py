"""Classify p.213 S2 statements, separate mixed claims, and repair mappings."""
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
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l108-118"
SEGMENT_SHA = "ebbb5be59dbc67e1337d077618074f382126d0f7c97e61e385c00514897599f3"
BACKUP_SUFFIX = ".bak-s2-chp8-p213-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "d4333e08973a1e57315f29a4cde4d73b5654c5c7ad4481be847e9e8cf364f64d",
    CANDIDATES: "db12a86f6ea32a804c66359f08a1a9e8db15999915cfdfa294d69ebd914d1139",
    MENTIONS: "ea25d16eb80355b27f6f7fabdd97cd076c092cf8bd4a583a9a1027c2df8e5f29",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
}
NEW_CANDIDATES = [
    (
        "cand-12052",
        "Florentine painting as a regional artistic field",
        "term",
        "A source-specific regional painting field used as the endpoint in Haskell's assessment of the Giordano decorations' effect; it does not name an institution or imply that all Florentine painting shared one condition.",
        115,
    ),
    (
        "cand-12053",
        "Unidentified Girolamo Durazzo pictures obtained from Bologna and Naples",
        "work",
        "Haskell says Durazzo turned to Bologna and Naples for many pictures, without titles, a count by city, or item-level acquisition routes. Distinct from the four Giordano canvases separately named for his family.",
        118,
    ),
]
NEW_MENTION_ID = None
NEW_STATEMENT_IDS = {
    "st-chp8-p213-collection-neglected-rome",
    "st-chp8-p213-collection-outstanding-interest",
    "st-chp8-p213-collection-shift-advanced-international-taste",
    "st-chp8-p213-giordano-devotional-pictures",
    "st-chp8-p213-giordano-works-crucial-to-central-italy",
    "st-chp8-p213-giordano-works-ranked-century-masterpieces",
    "st-chp8-p213-mehus-aesthetic-match-assessment",
    "st-chp8-p213-mehus-ignored-by-brothers",
    "st-chp8-p213-nome-inventory-described-as-lorenese",
    "st-chp8-p213-nome-contemporary-popularity",
    "st-chp8-p213-durazzo-family-membership",
    "st-chp8-p213-durazzo-family-built-local-art-collection",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preconditions and dry-run checks pass")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED_HASHES:
        raise SystemExit("a table, source, or page image changed since the p.213 review baseline")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[107:118])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("p.213 S0 segment changed since review")
    segment_rows = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    segment = segment_rows.get(SEGMENT_ID)
    if not segment or (
        segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
        segment.get("sha256"), segment.get("asset_sha256"),
    ) != (SOURCE_REL, 108, 118, SEGMENT_SHA, EXPECTED_HASHES[SOURCE]):
        raise SystemExit("p.213 segment manifest does not match the reviewed source")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_statement = {row["statement_id"]: row for row in statements}
    by_candidate = {row["candidate_id"]: row for row in candidates}
    by_mention = {row["mention_id"]: row for row in mentions}
    if len(by_statement) != len(statements) or len(by_candidate) != len(candidates) or len(by_mention) != len(mentions):
        raise SystemExit("statement, candidate, or mention identifiers are not unique")

    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {row["statement_id"] for row in page_rows if "relation_candidate" not in (row.get("qualifiers") or {})}
    if len(page_rows) != 19 or unset != {row["statement_id"] for row in page_rows}:
        raise SystemExit(f"unexpected p.213 inventory: rows={len(page_rows)}, unset={len(unset)}")
    if NEW_STATEMENT_IDS & set(by_statement):
        raise SystemExit("a planned p.213 statement identifier already exists")
    if {row[0] for row in NEW_CANDIDATES} & set(by_candidate):
        raise SystemExit("a planned p.213 candidate identifier already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12051:
        raise SystemExit("candidate sequence changed since the reviewed p.213 baseline")

    expected_mentions = {
        "m-chp8-p213-018": ("cand-7560", "eighteenth-century art"),
        "m-chp8-p213-044": ("cand-4490", "total neglect of Rome"),
        "m-chp8-p213-051": ("cand-7563", "seventeenth century"),
        "m-chp8-p213-054": ("cand-1041", "cultural life of Florence"),
        "m-chp8-p213-064": ("cand-1041", "Florentine painting"),
        "m-chp8-p213-067": ("cand-1041", "Florence"),
        "m-chp8-p213-085": ("cand-7573", "many of his pictures"),
    }
    for mention_id, expected in expected_mentions.items():
        row = by_mention.get(mention_id)
        if not row or (row["candidate_id"], row["surface_form"]) != expected:
            raise SystemExit(f"mention {mention_id} no longer matches the reviewed prestate")
    required_corrections = {
        "st-chp8-p213-callot-print-and-original-plate": {
            "source_line": 112,
            "ocr": "La Fiera dellTmpruneta",
            "print": "La Fiera dell'Impruneta",
            "basis": "CHP-8.pdf physical page 11.",
        },
        "st-chp8-p213-durazzo-local-collection-and-bologna-open": {
            "source_line": 118,
            "ocr": ". of one",
            "print": "of one",
            "basis": "CHP-8.pdf physical page 11; the initial mark is not printed sentence punctuation.",
        },
    }
    for statement_id, correction in required_corrections.items():
        if correction not in (by_statement[statement_id].get("qualifiers", {}).get("ocr_corrections") or []):
            raise SystemExit(f"expected p.213 correction missing or changed on {statement_id}")
    p214_continuation = by_statement.get("st-chp8-p214-durazzo-naples-continuation")
    if not p214_continuation:
        raise SystemExit("the p.214 Durazzo continuation statement is missing")

    for candidate_id, name, kind, detail, line in NEW_CANDIDATES:
        candidates.append({
            "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
            "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
            "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        })

    # Remove context-only spans that had been mapped to unrelated entities.
    mentions = [row for row in mentions if row["mention_id"] not in {
        "m-chp8-p213-018", "m-chp8-p213-051", "m-chp8-p213-054"
    }]
    by_mention = {row["mention_id"]: row for row in mentions}
    rome_row = by_mention["m-chp8-p213-044"]
    rome = "Rome"
    rome_start = segment_text.find("total neglect of Rome") + len("total neglect of ")
    if rome_start < 0 or segment_text[rome_start:rome_start + len(rome)] != rome:
        raise SystemExit("nested Rome place span does not match p.213 source")
    rome_row.update({
        "surface_form": rome, "start_char": str(rome_start), "end_char": str(rome_start + len(rome)),
        "note": "Nested place mention in Haskell's collection profile; the surrounding phrase is an evaluative description, not the city entity.",
    })
    by_mention["m-chp8-p213-064"].update({
        "candidate_id": "cand-12052",
        "note": "Regional field of painting named as the object of Haskell's assessment; distinct from Florence as a place.",
    })
    by_mention["m-chp8-p213-085"].update({
        "candidate_id": "cand-12053",
        "note": "Unidentified pictures sourced by Durazzo in Bologna and Naples; distinct from the four Giordano canvases named on p.214.",
    })
    candidates_by_id = {row["candidate_id"]: row for row in candidates}
    if "cand-12052" not in candidates_by_id or "cand-12053" not in candidates_by_id:
        raise SystemExit("the new p.213 candidate rows were not registered")

    def excerpt(first: str, last: str) -> str:
        start_at, end_at = segment_text.find(first), segment_text.rfind(last)
        if start_at < 0 or end_at < start_at:
            raise SystemExit(f"expected p.213 source excerpt missing: {first!r} ... {last!r}")
        return segment_text[start_at:end_at + len(last)]

    def update(statement_id: str, relation: bool, note: str, **changes) -> None:
        row = by_statement[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        qualifier_changes = changes.pop("qualifier_changes", {})
        for key, value in qualifier_changes.items():
            if value is None:
                q.pop(key, None)
            else:
                q[key] = value
        q.update(changes.pop("qualifiers", {}))
        row["qualifiers"] = q
        row.update(changes)

    def make_statement(statement_id: str, predicate: str, subject: str | None, obj: str | None,
                       claim: str, quote: str, start_line: int, end_line: int, mentioned: list[str],
                       relation: bool, note: str, qualification: str, **extra) -> dict:
        q = {
            "source_line_start": start_line, "source_line_end": end_line,
            "printed_page": 213, "pdf_physical_page": 11, "claim": claim,
            "speaker": "Haskell", "text_layer": "body", "qualification": qualification,
            "mentioned_candidate_ids": mentioned, "relation_candidate": relation,
            "relation_candidate_note": note,
        }
        q.update(extra)
        return {
            "statement_id": statement_id, "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": q, "original_quote": quote,
            "origin": "book", "source_file": SOURCE_REL,
        }

    # Split collection profile from Haskell's evaluative conclusion.
    update(
        "st-chp8-p213-collection-emphasis-on-naples-and-neglect-of-rome", True,
        "The statement is narrowed to Haskell's explicit claim that the collection placed great emphasis on Naples; the Rome omission and the author's evaluation are separate claims.",
        predicate="del_rosso_collection_emphasized_naples",
        object_candidate_id="cand-3534",
        claim="Haskell says the Del Rosso collection placed great emphasis on Naples.",
        original_quote=excerpt("the del Rosso collection with its great emphasis on", "Naples"),
        qualification="This describes Haskell's account of the collection's geographic profile.",
        mentioned_candidate_ids=["cand-7520", "cand-3534"],
    )
    update(
        "st-chp8-p213-collection-shift-from-disegno-to-colore", True,
        "The claim is narrowed to the reported shift in the collection from the Florentine disegno tradition toward colore; Haskell's interpretation of that shift follows in a separate statement.",
        predicate="del_rosso_collection_shifted_from_florentine_disegno_toward_colore",
        claim="Haskell describes a sudden shift in the Del Rosso collection from the Florentine tradition of disegno toward the values of colore.",
        original_quote=excerpt("their sudden conversion from the Florentine tradition of", "colore"),
        qualification="The source characterizes a collecting shift; it does not imply that individual works or patrons changed artistic identity.",
        mentioned_candidate_ids=["cand-7520", "cand-7533", "cand-7562"],
    )
    update(
        "st-chp8-p213-conditional-rosso-role-in-giordano-commissions", True,
        "Both intermediary role and influence remain conditional in Haskell's wording; the statement concerns the paired decorative works rather than only the Corsini commission.",
        object_candidate_id="cand-7565",
        qualification="Haskell says that if Giordano's commissions were obtained through Del Rosso, this would support a claim of influence for the brothers; neither route nor influence is treated as settled.",
        mentioned_candidate_ids=["cand-7489", "cand-1172", "cand-7547", "cand-7546", "cand-7545", "cand-2145", "cand-7234", "cand-7565"],
    )
    update(
        "st-chp8-p213-ferdinand-another-florentine-devotee", True,
        "Haskell presents Ferdinand as a future Florentine devotee of the sketchy, unfinished and lively brushwork discussed here; this is not a claim that he belonged to the Del Rosso family.",
        predicate="grand_prince_ferdinand_would_be_another_florentine_devotee_of_lively_brushwork",
        subject_candidate_id="cand-1609", object_candidate_id="cand-7560",
        claim="Haskell says the new appreciation of sketchy, unfinished and lively brushwork was to have another great Florentine devotee in Grand Prince Ferdinand de' Medici.",
    )
    update(
        "st-chp8-p213-financial-interest-belief-about-giordano-patronage", False,
        "This is Haskell's explicitly tentative suspicion about the motive for Giordano's special patronage, not an established financial transaction or motive.",
        qualifier_changes={"ocr_corrections": [{
            "source_line": 116, "ocr": "may have Been dictated", "print": "may have been dictated",
            "basis": "CHP-8.pdf physical page 11.",
        }]},
    )
    update(
        "st-chp8-p213-giordano-erotic-subjects-and-ignudo", True,
        "This completes the p.212 open sentence with the distant ignudo and named fable subjects; the Italian phrase remains a source description without an independent iconographic identification.",
    )
    update(
        "st-chp8-p213-giordano-modelli-favored", True,
        "Haskell explicitly reports the brothers' particular fondness for Giordano's modelli for altarpieces and other works.",
    )
    update(
        "st-chp8-p213-giordano-religious-and-devotional-pictures", True,
        "This statement is narrowed to Giordano's religious paintings with Old and New Testament scenes; the separate devotional pictures are recorded independently.",
        predicate="del_rosso_brothers_owned_giordano_religious_paintings_with_testament_scenes",
        object_candidate_id="cand-7557",
        claim="Haskell says the brothers owned religious paintings by Giordano with scenes from the Old and New Testaments.",
        original_quote=excerpt("they also owned religious paintings", "scenes from the Old and New Testaments"),
        qualification="The paintings and their scenes are not individually identified.",
        mentioned_candidate_ids=["cand-7489", "cand-7557", "cand-1172"],
    )
    update(
        "st-chp8-p213-giordano-works-regional-importance", True,
        "This row is narrowed to Haskell's claim that the paired decorative works had little effect on Florentine painting; the Central Italy claim and the masterpieces ranking are separated.",
        predicate="giordano_decorative_works_had_little_effect_on_florentine_painting",
        object_candidate_id="cand-12052",
        claim="Haskell says the Giordano decorations had disappointingly little effect on Florentine painting.",
        original_quote=excerpt("These works, though they had disappointingly little effect on Florentine painting", "Florentine painting"),
        qualification="This is Haskell's attributed assessment of the paired works' reception in a regional painting field.",
        mentioned_candidate_ids=["cand-7565", "cand-12052", "cand-1041"],
    )
    update(
        "st-chp8-p213-mehus-freshness-would-suit-giordano-patrons", True,
        "This row is narrowed to the reported collecting behavior: Haskell says the Del Rosso brothers largely ignored Livio Mehus. The counterfactual assessment of Mehus's suitability is separated.",
        predicate="del_rosso_brothers_largely_ignored_livio_mehus",
        subject_candidate_id="cand-7489", object_candidate_id="cand-1632",
        claim="Haskell says the Del Rosso brothers largely ignored Livio Mehus.",
        original_quote=excerpt("Yet Livio Mehus", "they largely ignored"),
        qualification="This reports a pattern of the brothers' collecting as Haskell describes it; it does not mean they owned no Mehus works, since the next sentence names three.",
        mentioned_candidate_ids=["cand-7489", "cand-1632"],
    )
    update(
        "st-chp8-p213-mehus-three-pictures-disappeared", True,
        "Haskell reports a collecting trajectory for the same three-picture group: owned in 1677 and absent twelve years later; no destination or cause is supplied.",
        qualification="The later date is relative in the source. The disappearance is preserved as Haskell's report and is not tied to a specific inventory unless separately evidenced.",
    )
    update(
        "st-chp8-p213-neapolitan-painting-diffused-through-patrons", True,
        "Haskell uses collections of patrons who looked beyond their native cities to illustrate Neapolitan painting's wider Italian importance; the passage then gives the Durazzo and Baglioni examples.",
    )
    update(
        "st-chp8-p213-new-appreciation-of-brushwork", False,
        "This is Haskell's broad forecast about the later importance of a manner of brushwork, not a discrete historical relation to an identified eighteenth-century art object or institution.",
        object_candidate_id=None,
        claim="Haskell says the brothers' new appreciation of sketchy, unfinished and lively brushwork would be important in eighteenth-century art.",
        original_quote=excerpt("This new appreciation", "eighteenth-century art"),
        qualification="The future importance is Haskell's art-historical assessment; the deleted mention 'eighteenth-century art' was an unrelated mapping to the brushwork candidate and is retained only in this source-level claim.",
        mentioned_candidate_ids=["cand-7560"],
    )
    update(
        "st-chp8-p213-nome-alias-and-inventory-description", True,
        "The statement is narrowed to Nomé's reported alias; his inventory description as 'Lorenese' is a distinct claim about the inventory's wording.",
        predicate="francois_nome_was_generally_known_as_monsu_desiderio",
        object_candidate_id=None,
        claim="Haskell identifies the Frenchman François Nomé as generally known as Monsù Desiderio.",
        original_quote=excerpt("Frenchman François Nome", "generally known as ‘Monsù Desiderio’"),
        qualification="The accented spelling is confirmed by the page image. The alias is reported by Haskell.",
        mentioned_candidate_ids=["cand-1749"],
    )
    update(
        "st-chp8-p213-nome-collecting-may-have-followed-giordano-intervention", True,
        "Haskell's causal and intermediary claims are explicitly modal; the object is the collected work group described immediately after, not Nomé the person.",
        predicate="del_rosso_brushwork_appreciation_may_have_led_to_collecting_nome_pictures_through_giordano",
        object_candidate_id="cand-7566",
        qualification="The source says appreciation may have led to collecting Nomé's work through Giordano; this route is not independently established.",
        mentioned_candidate_ids=["cand-7489", "cand-1172", "cand-7561", "cand-1749", "cand-7566"],
    )
    update(
        "st-chp8-p213-nome-eleven-visionary-ruin-pictures", True,
        "Haskell reports an inventory group of eleven Nomé pictures and several descriptions; these are not normalized into identified titles except where a candidate already records a source description.",
    )
    update(
        "st-chp8-p213-callot-print-and-original-plate", True,
        "Haskell says the brothers apparently possessed the original plate, preserving the qualification and distinguishing the printing matrix from Callot's print.",
        qualifier_changes={"ocr_corrections": [{
            "source_line": 112, "ocr": "La Fiera dellTmpruneta", "print": "La Fiera dell\\u2019Impruneta",
            "basis": "CHP-8.pdf physical page 11.",
        }]},
    )
    update(
        "st-chp8-p213-collection-contribution-to-florence-difficult-to-assess", False,
        "This is Haskell's stated difficulty in assessing the collection's possible cultural contribution; the conditional influence claim is recorded separately.",
    )
    update(
        "st-chp8-p213-collection-emphasis-on-naples-and-neglect-of-rome", True,
        "This statement is narrowed to Haskell's claim that the collection emphasized Naples; the Rome omission has its own endpoint and statement.",
        qualifier_changes={"footnote_statement_ids": ["st-chp8-p213-n1-more-del-rosso-pictures", "st-chp8-p213-n1-longhi-publication"]},
    )
    update(
        "st-chp8-p213-collection-shift-from-disegno-to-colore", True,
        "This statement records the collection's reported shift; the claim that the shift signified advanced international taste is separated as Haskell's interpretation.",
    )
    update(
        "st-chp8-p213-conditional-rosso-role-in-giordano-commissions", True,
        "This remains Haskell's conditional influence argument and is cross-referenced to the p.212 Corsini commission candidate; the p.213 statement concerns both decorative works.",
    )
    update(
        "st-chp8-p213-durazzo-local-collection-and-bologna-open", True,
        "This is narrowed to the Bologna picture route that continues on p.214; the family membership and its local Genoese art collection are split into separate statements.",
        predicate="girolamo_durazzo_turned_to_bologna_for_many_pictures_continues_to_naples",
        object_candidate_id="cand-12053",
        claim="Haskell says Girolamo Durazzo turned to Bologna for many pictures; the sentence continues on p.214 to add Naples.",
        original_quote=excerpt("turned not only to Bologna", "as was"),
        qualification="The named cities are source routes for an unidentified group; the p.214 continuation completes the sentence.",
        qualifier_changes={
            "mentioned_candidate_ids": ["cand-0953", "cand-1131", "cand-0381", "cand-12053"],
            "ocr_corrections": [],
        },
    )

    # The title uses an apostrophe glyph in print; preserve it in the OCR correction.
    callot = by_statement["st-chp8-p213-callot-print-and-original-plate"]
    callot_q = dict(callot["qualifiers"])
    callot_q["ocr_corrections"] = [{
        "source_line": 112, "ocr": "La Fiera dellTmpruneta", "print": "La Fiera dell\u2019Impruneta",
        "basis": "CHP-8.pdf physical page 11.",
    }]
    callot["qualifiers"] = callot_q
    # Move the p.213 line-break OCR repair to the split family-membership claim.
    durazzo = by_statement["st-chp8-p213-durazzo-local-collection-and-bologna-open"]
    durazzo_q = dict(durazzo["qualifiers"])
    durazzo_q.pop("ocr_corrections", None)
    durazzo["qualifiers"] = durazzo_q

    add_specs = [
        (
            "st-chp8-p213-collection-neglected-rome", "del_rosso_collection_totally_neglected_rome",
            "cand-7520", "cand-4490", "Haskell says the Del Rosso collection showed a total neglect of Rome.",
            excerpt("its total neglect of Rome", "its total neglect of Rome"), 114, 114,
            ["cand-7520", "cand-4490"], True,
            "This is the separately named Rome side of Haskell's collection profile, distinct from Naples emphasis and his evaluation of the collection.",
            "The statement reports Haskell's characterization of the collection's holdings; it does not establish that every Rome-related work was absent.",
            {"footnote_numbers": [1], "footnote_marker": 1, "footnote_segment": "chp-8:08_CHP-8_sec_i:l126-157", "footnote_statement_ids": ["st-chp8-p213-n1-more-del-rosso-pictures", "st-chp8-p213-n1-longhi-publication"]},
        ),
        (
            "st-chp8-p213-collection-outstanding-interest", "haskell_judges_del_rosso_collection_of_outstanding_interest",
            "cand-7520", None, "Haskell calls the Del Rosso collection an isolated phenomenon of outstanding interest.",
            excerpt("As an isolated phenomenon", "is of outstanding interest"), 113, 114,
            ["cand-7520"], False,
            "This is Haskell's evaluative conclusion, not a separate relation between the collection and a named endpoint.",
            "The sentence's footnote refers to additional holdings and a publication; it does not independently establish the evaluation.",
            {"footnote_numbers": [1], "footnote_marker": 1, "footnote_segment": "chp-8:08_CHP-8_sec_i:l126-157", "footnote_statement_ids": ["st-chp8-p213-n1-more-del-rosso-pictures", "st-chp8-p213-n1-longhi-publication"]},
        ),
        (
            "st-chp8-p213-collection-shift-advanced-international-taste", "collection_shift_symptomatic_of_advanced_international_taste_near_venetian_revival",
            "cand-7520", "cand-7563", "Haskell interprets the collection's shift as symptomatic of advanced international taste near the Venetian revival.",
            excerpt("was symptomatic of the most advanced international taste", "great Venetian revival"), 114, 115,
            ["cand-7520", "cand-7533", "cand-7562", "cand-7563", "cand-7564"], False,
            "This is Haskell's art-historical interpretation of a collection shift, not an independently established influence relation.",
            "The source places the interpretation near the end of the seventeenth century and on the verge of a Venetian revival.",
            {},
        ),
        (
            "st-chp8-p213-giordano-devotional-pictures", "del_rosso_brothers_owned_giordano_devotional_pictures",
            "cand-7489", "cand-7558", "Haskell says the brothers also owned more purely devotional pictures by Giordano.",
            excerpt("as well as more purely devotional pictures", "more purely devotional pictures"), 109, 109,
            ["cand-7489", "cand-7558", "cand-1172"], True,
            "This is the separate devotional group in Haskell's sentence, distinct from Giordano's paintings with Old and New Testament scenes.",
            "No individual devotional picture is titled in this passage.",
            {},
        ),
        (
            "st-chp8-p213-giordano-works-crucial-to-central-italy", "giordano_decorative_works_crucial_to_central_italy",
            "cand-7565", "cand-7392", "Haskell says the Corsini and Palazzo Riccardi decorations were of crucial importance to central Italy.",
            excerpt("were of crucial importance to central Italy", "central Italy"), 115, 115,
            ["cand-7565", "cand-7392"], True,
            "This records Haskell's attributed regional importance claim for the two named decorations.",
            "The claim is limited to central Italy and is not independently measured here.",
            {},
        ),
        (
            "st-chp8-p213-giordano-works-ranked-century-masterpieces", "haskell_ranks_giordano_decorations_among_century_masterpieces",
            "cand-7565", None, "Haskell ranks the two decorations among the masterpieces of the century.",
            excerpt("in their own right they rank among the masterpieces of the century", "masterpieces of the century"), 115, 115,
            ["cand-7565"], False,
            "This is an attributed comparative ranking without a separate identified endpoint or independent standard.",
            "The ranking is Haskell's assessment of the paired decorative works.",
            {},
        ),
        (
            "st-chp8-p213-mehus-aesthetic-match-assessment", "haskell_says_mehus_might_have_suited_giordano_friends_and_patron_group",
            "cand-1632", None, "Haskell says Mehus's freshness and vitality could surely have suited Giordano's friends and patrons.",
            excerpt("There was, for instance", "Giordano."), 115, 116,
            ["cand-1632", "cand-1041", "cand-1172", "cand-7489"], False,
            "This is Haskell's counterfactual aesthetic assessment; it does not establish an actual commission or relationship.",
            "The text immediately contrasts the assessment with the brothers' reported neglect of Mehus.",
            {},
        ),
        (
            "st-chp8-p213-mehus-ignored-by-brothers", "del_rosso_brothers_largely_ignored_livio_mehus",
            "cand-7489", "cand-1632", "Haskell says the Del Rosso brothers largely ignored Livio Mehus.",
            excerpt("Yet Livio Mehus", "they largely ignored"), 116, 116,
            ["cand-7489", "cand-1632"], True,
            "This is a specific reported pattern of collecting; the next sentence qualifies any absolute reading by naming three Mehus pictures owned in 1677.",
            "'Largely ignored' is Haskell's qualified wording, not a claim that no Mehus pictures were owned.",
            {},
        ),
        (
            "st-chp8-p213-nome-inventory-described-as-lorenese", "del_rosso_inventory_described_nome_as_lorenese",
            "cand-7500", "cand-1749", "Haskell reports that the Del Rosso inventory described François Nomé as 'Lorenese'.",
            excerpt("described in their inventory as", "‘Lorenese’"), 111, 111,
            ["cand-7500", "cand-1749"], True,
            "This records the inventory's reported wording; it does not independently establish Nomé's birthplace or nationality.",
            "The designation is attributed to the inventory through Haskell.",
            {},
        ),
        (
            "st-chp8-p213-nome-contemporary-popularity", "haskell_says_nome_had_acquired_enormous_popularity_in_his_own_day",
            "cand-1749", None, "Haskell says François Nomé had acquired enormous popularity in his own day.",
            excerpt("who has acquired enormous popularity", "in our own day"), 110, 111,
            ["cand-1749"], False,
            "This is Haskell's present-day reception comment, not an evidenced relation in the Del Rosso collection record.",
            "'Our own day' refers to the author's period of writing, not the present day.",
            {},
        ),
        (
            "st-chp8-p213-durazzo-family-membership", "girolamo_durazzo_was_member_of_leading_genoese_patrician_family",
            "cand-0953", "cand-7360", "Haskell identifies Girolamo Durazzo as a member of one of Genoa's leading patrician families.",
            excerpt("a member", "leading patrician families"), 117, 118,
            ["cand-0953", "cand-7360", "cand-1131"], True,
            "This is a distinct family-membership claim; the family candidate remains open because the branch is not named.",
            "The OCR adds a leading period before 'of one'; the page image confirms the sentence continues without punctuation.",
            {"ocr_corrections": [{
                "source_line": 118, "ocr": ". of one", "print": "of one",
                "basis": "CHP-8.pdf physical page 11; the initial mark is not printed sentence punctuation.",
            }]},
        ),
        (
            "st-chp8-p213-durazzo-family-built-local-art-collection", "durazzo_family_built_extensive_collection_of_local_genoese_art",
            "cand-7360", "cand-7572", "Haskell says the Durazzo family built an extensive collection of local Genoese art over the centuries.",
            excerpt("families which over the centuries", "collection of local art"), 118, 118,
            ["cand-7360", "cand-7572", "cand-1131"], True,
            "This concerns the family's collection of local art, separate from Girolamo's later purchases of pictures in Bologna and Naples.",
            "The collection is kept as an open type-unresolved candidate because the current taxonomy has no collection type.",
            {},
        ),
    ]
    for (statement_id, predicate, subject, obj, claim, quote, start_line, end_line,
         mentioned, relation, note, qualification, extra) in add_specs:
        statements.append(make_statement(
            statement_id, predicate, subject, obj, claim, quote, start_line, end_line,
            mentioned, relation, note, qualification, **extra,
        ))

    p212_collection_refs = ["st-chp8-p213-n1-more-del-rosso-pictures", "st-chp8-p213-n1-longhi-publication"]
    updated_by_statement = {row["statement_id"]: row for row in statements}
    for statement_id in ("st-chp8-p213-collection-emphasis-on-naples-and-neglect-of-rome", "st-chp8-p213-collection-neglected-rome"):
        q = dict(updated_by_statement[statement_id]["qualifiers"])
        q["footnote_statement_ids"] = p212_collection_refs
        updated_by_statement[statement_id]["qualifiers"] = q

    changed_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(changed_rows) != 31 or any("relation_candidate" not in row.get("qualifiers", {}) for row in changed_rows):
        raise SystemExit("the updated p.213 statement inventory is incomplete")
    all_candidate_ids = {row["candidate_id"] for row in candidates}
    bad_refs = []
    for row in changed_rows:
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id"),
                             *(row.get("qualifiers", {}).get("mentioned_candidate_ids") or [])):
            if candidate_id and candidate_id not in all_candidate_ids:
                bad_refs.append((row["statement_id"], candidate_id))
    if bad_refs:
        raise SystemExit(f"p.213 statements refer to absent candidates: {bad_refs}")
    p212_link = by_statement["st-chp8-p212-giordano-pictures-included-many-erotic-works-open"]
    if p212_link.get("qualifiers", {}).get("continuation_statement_id") != "st-chp8-p213-giordano-erotic-subjects-and-ignudo":
        raise SystemExit("the p.212-p.213 erotic-work cross-page link changed")

    outputs = {
        STATEMENTS: jsonl_bytes(statements),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions),
    }
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    print("p.213 statements:", len(page_rows), "->", len(changed_rows),
          "relation candidates:", sum(bool(row["qualifiers"]["relation_candidate"]) for row in changed_rows))
    print("added candidates:", ", ".join(row[0] for row in NEW_CANDIDATES))
    print("removed context-only/wrongly mapped mentions: m-chp8-p213-018, m-chp8-p213-051, m-chp8-p213-054")
    print("repaired mentions: Rome span; Florentine painting term; Durazzo picture group")
    print("added statements:", ", ".join(sorted(NEW_STATEMENT_IDS)))
    for path, data in outputs.items():
        print(path.name, "sha256:", sha(data))
    if args.apply:
        backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
        if any(path.exists() for path in backups.values()):
            raise SystemExit("a p.213 recovery copy already exists; inspect it before applying")
        for path, backup in backups.items():
            shutil.copy2(path, backup)
        for path, data in outputs.items():
            atomic_write(path, data)
        print("recovery copies:", ", ".join(path.name for path in backups.values()))


if __name__ == "__main__":
    main()
