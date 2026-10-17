"""Classify p.210 S2 statements and repair their entity mappings."""
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
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l72-82"
BACKUP_SUFFIX = ".bak-s2-chp8-p210-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "5190aef282907eb2879a558f55c50290c24ecd1a73436245419c21e053326d37",
    CANDIDATES: "229d49ff9aea63134bcfe162f56104db5287473906a2fbd148ef85d598b44c84",
    MENTIONS: "7890100a9cb7cd78f3fe163d19133fc353dfbecf7d239d71b396fd93ecabd095",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
EXPECTED_SEGMENT_SHA = "d5bbe689b640f0ac4401ba569f34e632888be52322e9c51dd483a006f88c9de6"

CANDIDATE_SPECS = [
    ("cand-12040", "Pictures of Rembrandt reported in Abram Breughel's 1665 letter", "work",
     "Unidentified Rembrandt pictures whose local reception is reported in Breughel's 1665 letter; 'here' is geographically unresolved.", 73),
    ("cand-12041", "Rembrandt etchings mentioned in Haskell's account of Italian reception", "work",
     "Unspecified etchings by Rembrandt, mentioned as an exception in Haskell's generalization about Italian reception.", 73),
    ("cand-12042", "Seven unidentified pictures by Guercino in Don Antonio Ruffo's collection", "work",
     "A group of seven unnamed Guercino pictures reported in Ruffo's collection; no titles are supplied here.", 74),
    ("cand-12043", "Unidentified pictures by Andrea Sacchi and Carlo Maratta in Ruffo's collection", "work",
     "The one unnamed picture by each of Sacchi and Maratta reported in Ruffo's collection; the two works remain unidentified.", 74),
    ("cand-12044", "Listed Neapolitan and South Italian pictures inherited by Don Antonio Ruffo", "work",
     "The preceding group of counted pictures by Novelli, Ribera, Andrea Vaccaro and Stanzione; Haskell says most were inherited from Ruffo's brother.", 75),
    ("cand-12045", "Florentine appreciation of Neapolitan art", "term",
     "The appreciation of Neapolitan art among the unnamed Florentine patrons discussed by Haskell; it is distinct from the patrons themselves.", 81),
    ("cand-12046", "Unspecified provincial centres challenging Rome's artistic supremacy", "term",
     "The unnamed provincial centres in Haskell's period-level account; no individual city is identified in this sentence.", 81),
    ("cand-12047", "Neapolitan artists acquiring international prestige", "term",
     "The unnamed group of Neapolitan artists in Haskell's generalization about international prestige; no individual artists are listed here.", 81),
    ("cand-12048", "Rome's artistic supremacy in Italian patronage", "term",
     "The artistic supremacy attributed to Rome in Haskell's account of provincial centres; this is a concept, not the city itself.", 81),
]

NEW_STATEMENT_IDS = {
    "st-chp8-p210-neapolitan-artists-acquired-international-prestige",
    "st-chp8-p210-ruffo-owned-seven-guercino-pictures",
    "st-chp8-p210-ruffo-owned-sacchi-and-maratta-pictures",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
    hashes = {path: sha(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit("a table or source file changed since the p.210 review baseline")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES, MENTIONS)}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("a recovery copy already exists; inspect it before applying")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[71:82])
    if sha(segment_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.210 source segment changed since review")
    segments = read_jsonl(TABLES / "segments.jsonl")
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (segment.get("line_start"), segment.get("line_end")) != (72, 82):
        raise SystemExit("p.210 segment metadata changed")
    if segment.get("sha256") != EXPECTED_SEGMENT_SHA or segment.get("asset_sha256") != EXPECTED_HASHES[SOURCE]:
        raise SystemExit("p.210 segment/source fingerprints do not match")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(by_id) != len(statements) or len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise SystemExit("statement, candidate, or mention IDs are not unique")

    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {row["statement_id"] for row in page_rows if "relation_candidate" not in (row.get("qualifiers") or {})}
    expected_unset = {
        "st-chp8-p210-breughel-reported-rembrandt-reception-1665",
        "st-chp8-p210-house-via-chiara-location-description",
        "st-chp8-p210-neapolitan-painting-crossed-spanish-imperial-frontiers",
        "st-chp8-p210-provincial-centres-and-neapolitan-prestige",
        "st-chp8-p210-rembrandt-reception-in-italy",
        "st-chp8-p210-ruffo-comparatively-unaffected-by-classicism",
        "st-chp8-p210-ruffo-gallery-isolated-cultural-stronghold",
        "st-chp8-p210-ruffo-gallery-limited-wider-significance",
        "st-chp8-p210-unnamed-agent-italian-remark",
    }
    if len(page_rows) != 34 or unset != expected_unset:
        raise SystemExit(f"unexpected p.210 inventory: rows={len(page_rows)}, unset_delta={sorted(unset ^ expected_unset)}")
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("a planned statement ID already exists")
    if {row[0] for row in CANDIDATE_SPECS} & set(candidate_by_id):
        raise SystemExit("a planned candidate ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12039:
        raise SystemExit("candidate sequence changed since the reviewed baseline")

    expected_mentions = {
        "m-chp8-p210-001": ("cand-12039", "contemporaries"),
        "m-chp8-p210-011": ("cand-2117", "his etchings"),
        "m-chp8-p210-033": ("cand-1258", "his pictures"),
        "m-chp8-p210-049": ("cand-7480", "most of these"),
        "m-chp8-p210-051": ("cand-7468", "Religious subjects"),
        "m-chp8-p210-072": ("cand-2300", "public commissions"),
        "m-chp8-p210-080": ("cand-4490", "absolute supremacy of Rome"),
        "m-chp8-p210-081": ("cand-7484", "provincial centres"),
        "m-chp8-p210-082": ("cand-7480", "Neapolitan artists"),
        "m-chp8-p210-092": ("cand-7486", "three brothers"),
        "m-chp8-p210-012": ("cand-2297", "Russo’s"),
        "m-chp8-p210-017": ("cand-2297", "Russo himself"),
        "m-chp8-p210-056": ("cand-2297", "Russo"),
        "m-chp8-p210-065": ("cand-2297", "Russo’s"),
    }
    for mention_id, expected in expected_mentions.items():
        row = mention_by_id.get(mention_id)
        if not row or (row["candidate_id"], row["surface_form"]) != expected:
            raise SystemExit(f"mention {mention_id} no longer matches its expected prestate")
    planned_mentions = {"m-chp8-p210-096", "m-chp8-p210-097", "m-chp8-p210-098", "m-chp8-p210-099"}
    if planned_mentions & set(mention_by_id):
        raise SystemExit("a planned mention ID already exists")

    def exact_mention(mention_id: str, candidate_id: str, surface: str, note: str = "") -> dict:
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"expected unique mention text is missing or repeated: {surface!r}")
        return {"mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
                "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note}

    new_candidates = []
    for candidate_id, name, kind, detail, line in CANDIDATE_SPECS:
        new_candidates.append({
            "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
            "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
            "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        })
    candidates.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    mapping_changes = {
        "m-chp8-p210-011": ("cand-12041", "Refers to Rembrandt's etchings as a group of works, not to Rembrandt the person."),
        "m-chp8-p210-033": ("cand-12042", "Refers to the seven pictures by Guercino, not to the painter."),
        "m-chp8-p210-049": ("cand-12044", "'Most of these' refers to the listed group of pictures, not to the painters."),
        "m-chp8-p210-080": ("cand-12048", "This phrase denotes Rome's artistic supremacy, not the city itself; a nested Rome mention preserves the place reference."),
        "m-chp8-p210-081": ("cand-12046", "Unspecified provincial centres are distinct from the broader patronage shift."),
        "m-chp8-p210-082": ("cand-12047", "This general group of Neapolitan artists is broader than the painters represented in Ruffo's gallery."),
        "m-chp8-p210-092": ("cand-7489", "The three Del Rosso brothers are identified as members of the Del Rosso family; the p.211 continuation confirms the surname."),
    }
    for mention_id, (candidate_id, note) in mapping_changes.items():
        mention_by_id[mention_id]["candidate_id"] = candidate_id
        mention_by_id[mention_id]["note"] = note
    for mention_id in ("m-chp8-p210-012", "m-chp8-p210-017", "m-chp8-p210-056", "m-chp8-p210-065"):
        mention_by_id[mention_id]["note"] = "S0 OCR reads Russo; CHP-8.pdf physical page 8 confirms Ruffo. The source transcription remains unchanged."
    new_mentions = [
        exact_mention("m-chp8-p210-096", "cand-12040", "pictures of Rembrandt", "Unidentified works referred to in Breughel's 1665 reported letter."),
        exact_mention("m-chp8-p210-097", "cand-12043", "one each by Sacchi and Maratta", "The unnamed pictures counted for Sacchi and Maratta, grouped as two unidentified works."),
        exact_mention("m-chp8-p210-098", "cand-12045", "this appreciation", "Refers to Florentine appreciation of Neapolitan art, not to the patrons as a group."),
    ]
    nested_phrase = "absolute supremacy of Rome"
    nested_start = segment_text.find(nested_phrase)
    if nested_start < 0 or segment_text.find(nested_phrase, nested_start + 1) >= 0:
        raise SystemExit("expected unique nested Rome reference is missing or repeated")
    city_start = nested_start + nested_phrase.rfind("Rome")
    new_mentions.append({"mention_id": "m-chp8-p210-099", "segment_id": SEGMENT_ID, "candidate_id": "cand-4490",
                         "surface_form": "Rome", "start_char": str(city_start), "end_char": str(city_start + 4),
                         "note": "Nested place reference within the phrase for Rome's artistic supremacy."})
    mentions = [row for row in mentions if row["mention_id"] not in {"m-chp8-p210-051", "m-chp8-p210-072"}]
    mentions.extend(new_mentions)
    mention_by_id = {row["mention_id"]: row for row in mentions}

    def add_corrections(q: dict, corrections: list[dict]) -> None:
        old = list(q.get("ocr_corrections") or [])
        for correction in corrections:
            if correction not in old:
                old.append(correction)
        q["ocr_corrections"] = old

    def update(statement_id: str, relation: bool, note: str, **changes) -> None:
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        for key in ("predicate", "subject_candidate_id", "object_candidate_id", "original_quote"):
            if key in changes:
                value = changes.pop(key)
                if key == "predicate":
                    row[key] = value
                elif key == "subject_candidate_id":
                    row[key] = value
                elif key == "object_candidate_id":
                    row[key] = value
                else:
                    row[key] = value
        corrections = changes.pop("ocr_corrections", None)
        if corrections:
            add_corrections(q, corrections)
        for key, value in changes.items():
            if key == "mentioned_candidate_ids":
                q[key] = list(dict.fromkeys(value))
            else:
                q[key] = value
        row["qualifiers"] = q

    def source_excerpt(line_no: int, first: str, last: str) -> str:
        source_line = source_lines[line_no - 1]
        start, end = source_line.find(first), source_line.rfind(last)
        if start < 0 or end < start:
            raise SystemExit(f"expected source phrase missing at L{line_no}: {first!r} ... {last!r}")
        return source_line[start:end + len(last)]

    page8 = "CHP-8.pdf physical page 8."
    update(
        "st-chp8-p210-breughel-reported-rembrandt-reception-1665", True,
        "This is a reported statement by Breughel about the reception of Rembrandt's pictures; the letter itself and the geographic scope of 'here' remain unresolved.",
        predicate="breughel_reported_low_regard_for_rembrandt_pictures_in_1665",
        object_candidate_id="cand-12040",
        claim="Haskell reports that Abram Breughel wrote in 1665 that Rembrandt's pictures were not highly regarded 'here'.",
        qualification="Haskell says Breughel was probably not being insincere. Although Breughel is introduced as Ruffo's agent in Rome, the passage does not define the geographic scope of 'here'; the letter itself is not independently read here.",
        mentioned_candidate_ids=["cand-0448", "cand-12040", "cand-4490"],
    )
    update(
        "st-chp8-p210-house-via-chiara-location-description", True,
        "The source locates the principal outpost of Florentine appreciation of Neapolitan art at the house; the appreciation and the house are distinct referents.",
        predicate="florentine_appreciation_of_neapolitan_art_had_principal_outpost_at_house",
        subject_candidate_id="cand-12045", object_candidate_id="cand-7486",
        claim="Haskell locates the principal outpost of Florentine appreciation of Neapolitan art in a fine house on Via Chiara near S. Maria Novella, set in a beautiful garden with fountains and statues.",
        mentioned_candidate_ids=["cand-12045", "cand-7486", "cand-7487", "cand-7488", "cand-1041"],
    )
    update(
        "st-chp8-p210-neapolitan-painting-crossed-spanish-imperial-frontiers", True,
        "This is an explicit historical claim that Neapolitan painting spread beyond the political frontiers of the Spanish Empire.",
        mentioned_candidate_ids=["cand-1729", "cand-7478"],
    )
    update(
        "st-chp8-p210-provincial-centres-and-neapolitan-prestige", True,
        "The first clause states that unnamed provincial centres challenged Rome's artistic supremacy; the separate prestige claim is recorded independently.",
        predicate="provincial_centres_challenged_romes_artistic_supremacy",
        subject_candidate_id="cand-12046", object_candidate_id="cand-12048",
        claim="Haskell says that, in this phase of Italian patronage, various provincial centres challenged Rome's absolute supremacy.",
        qualification="This is Haskell's period-level interpretation; it does not define every provincial centre or claim that Rome ceased to matter.",
        original_quote=source_excerpt(81, "one of the characteristics", "provincial centres"),
        mentioned_candidate_ids=["cand-12046", "cand-12048", "cand-4490", "cand-7484"],
    )
    update(
        "st-chp8-p210-rembrandt-reception-in-italy", False,
        "This is Haskell's broad assessment of Rembrandt's reception in Italy, not a specific historical relation; the etchings remain a separate group of works.",
        object_candidate_id="cand-3461",
        mentioned_candidate_ids=["cand-2117", "cand-3461", "cand-12041"],
    )
    update(
        "st-chp8-p210-ruffo-comparatively-unaffected-by-classicism", True,
        "Haskell makes a qualified claim about Ruffo's stance in relation to identifiable Roman classicist doctrines; 'comparatively' does not mean wholly unaffected.",
        mentioned_candidate_ids=["cand-2297", "cand-4628", "cand-4490"],
    )
    update(
        "st-chp8-p210-ruffo-gallery-isolated-cultural-stronghold", False,
        "This is Haskell's metaphorical and qualified characterization of the gallery, not a historical relation between the collection and the Spanish Empire.",
        object_candidate_id=None,
        mentioned_candidate_ids=["cand-7468", "cand-7478", "cand-2297"],
    )
    update(
        "st-chp8-p210-ruffo-gallery-limited-wider-significance", False,
        "This is Haskell's evaluative claim about the gallery's wider significance, not a discrete relation to an identified endpoint.",
        object_candidate_id=None,
        mentioned_candidate_ids=["cand-7468"],
    )
    update(
        "st-chp8-p210-unnamed-agent-italian-remark", True,
        "This is a reported communication from Ruffo's unidentified agent to Ruffo; the Italian words are preserved as reported by Haskell, with visible OCR errors corrected in the S2 note.",
        claim="Haskell reports that Ruffo's unnamed agent wrote that desiring pictures by famous painters could not be called an illness.",
        qualification="The source reports an Italian quotation; the agent is not identified and must not be merged with Abram Breughel.",
        mentioned_candidate_ids=["cand-7476", "cand-2297"],
        ocr_corrections=[
            {"source_line": 73, "ocr": "desiderate", "print": "desiderare", "basis": page8},
        ],
    )

    update(
        "st-chp8-p210-ruffo-gallery-isolated-cultural-stronghold", False,
        "This is Haskell's metaphorical and qualified characterization of the gallery, not a historical relation between the collection and the Spanish Empire.",
        ocr_corrections=[{"source_line": 77, "ocr": "Russo��s", "print": "Ruffo's", "basis": page8}],
    )
    update(
        "st-chp8-p210-ruffo-returned-blind-homer-for-completion", True,
        "Haskell reports Ruffo's response to the painting and its return for completion; the source does not establish a later conservation or provenance history.",
        ocr_corrections=[
            {"source_line": 74, "ocr": "Russo himself", "print": "Ruffo himself", "basis": page8},
        ],
    )
    update(
        "st-chp8-p210-ruffo-interest-in-polidoro-da-caravaggio", True,
        "Haskell attributes a special interest in Polidoro da Caravaggio to Ruffo.",
        ocr_corrections=[{"source_line": 75, "ocr": "Russo", "print": "Ruffo", "basis": page8}],
    )
    update(
        "st-chp8-p210-ruffo-owned-189-rembrandt-prints", True,
        "Haskell reports Ruffo's collection of prints and its count of Rembrandt prints.",
        ocr_corrections=[{"source_line": 76, "ocr": "he. also owned", "print": "he also owned", "basis": page8}],
    )
    update(
        "st-chp8-p210-ruffo-bought-three-rembrandt-pictures", True,
        "The sentence explicitly identifies three Rembrandt pictures and reports that Ruffo bought them over about twelve years.",
        ocr_corrections=[
            {"source_line": 73, "ocr": "Rembrandt��Aristotle", "print": "Rembrandt—Aristotle", "basis": page8},
            {"source_line": 73, "ocr": "Homer��bought", "print": "Homer—bought", "basis": page8},
        ],
    )
    update(
        "st-chp8-p210-guercino-picture-to-match-rembrandt-aristotle", True,
        "Haskell reports that Ruffo asked Guercino for an unidentified picture to match Rembrandt's Aristotle; the title of Guercino's picture is not supplied.",
    )
    update(
        "st-chp8-p210-ruffo-sought-early-robust-guercino-works", True,
        "Haskell says Ruffo made additional efforts to obtain examples of Guercino's early and robust style; no individual work is named.",
    )
    update(
        "st-chp8-p210-guercino-apparent-favourite-and-counts", True,
        "The source gives a qualified patron preference claim about Guercino; the work counts that support Haskell's assessment are split into separate statements.",
        predicate="haskell_judged_guercino_among_ruffos_favourites",
        claim="Haskell says Guercino seems to have been among Ruffo's favourites.",
        qualification="The word 'seems' marks this as Haskell's qualified assessment, not Ruffo's own statement.",
        mentioned_candidate_ids=["cand-2297", "cand-1258"],
    )
    update(
        "st-chp8-p210-ruffo-gallery-neapolitan-and-south-italian-holdings", True,
        "The statement identifies the regional painter group best represented in Ruffo's gallery; the listed works and their inheritance status are represented separately.",
        mentioned_candidate_ids=["cand-2297", "cand-7480", "cand-7468", "cand-1757", "cand-2140", "cand-2673", "cand-2506", "cand-12044"],
    )
    update(
        "st-chp8-p210-most-listed-south-italian-pictures-inherited-from-brother", True,
        "'Most of these' refers to the listed picture group; Haskell says most of that group were inherited from Ruffo's brother, without allocating works among artists.",
        predicate="most_listed_south_italian_pictures_inherited_from_ruffos_brother",
        subject_candidate_id="cand-12044", object_candidate_id="cand-7479",
        claim="Haskell says most of the listed Neapolitan and South Italian pictures in Ruffo's gallery were inherited from his brother.",
        qualification="The source does not allocate the inherited works among the four named painters or explicitly name the recipient of the inheritance.",
        mentioned_candidate_ids=["cand-12044", "cand-7479", "cand-2297", "cand-7480", "cand-7468"],
    )

    def make_statement(statement_id: str, predicate: str, subject: str | None, obj: str | None,
                       claim: str, quote: str, line: int, mentioned: list[str], relation: bool,
                       note: str, qualification: str, **extra) -> dict:
        q = {
            "source_line_start": line, "source_line_end": line, "printed_page": 210, "pdf_physical_page": 8,
            "claim": claim, "speaker": "Haskell", "text_layer": "body", "qualification": qualification,
            "mentioned_candidate_ids": mentioned, "relation_candidate": relation,
            "relation_candidate_note": note,
        }
        q.update(extra)
        return {"statement_id": statement_id, "segment_id": SEGMENT_ID,
                "subject_candidate_id": subject, "object_candidate_id": obj,
                "predicate": predicate, "qualifiers": q, "original_quote": quote,
                "origin": "book", "source_file": SOURCE_REL}

    statements.extend([
        make_statement(
            "st-chp8-p210-ruffo-owned-seven-guercino-pictures",
            "ruffo_owned_seven_unidentified_pictures_by_guercino", "cand-2297", "cand-12042",
            "Haskell says Ruffo owned seven unidentified pictures by Guercino.",
            source_excerpt(74, "he owned seven of his pictures", "Sacchi and Maratta"), 74,
            ["cand-2297", "cand-1258", "cand-12042"], True,
            "This is a specific collection-count claim about seven Guercino pictures; the individual works are unnamed.",
            "The count is reported by Haskell and does not identify the works or establish a complete oeuvre count.",
            quantity=7, quantity_qualifier="reported collection count"),
        make_statement(
            "st-chp8-p210-ruffo-owned-sacchi-and-maratta-pictures",
            "ruffo_owned_one_unidentified_picture_each_by_sacchi_and_maratta", "cand-2297", "cand-12043",
            "Haskell says Ruffo owned one unidentified picture each by Andrea Sacchi and Carlo Maratta.",
            source_excerpt(74, "he owned seven of his pictures", "Sacchi and Maratta"), 74,
            ["cand-2297", "cand-2318", "cand-1526", "cand-12043"], True,
            "This records the two reported one-picture holdings as an unidentified work group; the individual pictures are not named.",
            "The counts are reported by Haskell and do not establish complete oeuvres for either artist.",
            quantity=2, quantity_detail={"Andrea Sacchi": 1, "Carlo Maratta": 1}),
        make_statement(
            "st-chp8-p210-neapolitan-artists-acquired-international-prestige",
            "haskell_said_neapolitan_artists_acquired_international_prestige", "cand-12047", None,
            "Haskell says Neapolitan artists acquired international prestige.",
            source_excerpt(81, "the international prestige acquired by Neapolitan artists", "Neapolitan artists"), 81,
            ["cand-12047"], False,
            "This is a period-level attribute claim about an unnamed artist group, without a distinct relation endpoint or named event.",
            "This remains Haskell's generalization; no individual artists or measures of prestige are specified."),
    ])

    # The three statements about the house share a plural subject in the sentence; preserve the family group as context.
    for statement_id in (
        "st-chp8-p210-house-inhabited-by-three-rosso-brothers-open",
        "st-chp8-p210-house-inhabited-by-lorenzo-del-rosso",
        "st-chp8-p210-house-inhabited-by-ottavio-del-rosso",
    ):
        q = dict(by_id[statement_id].get("qualifiers") or {})
        q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + ["cand-7489"]))
        by_id[statement_id]["qualifiers"] = q

    final_page = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(final_page) != 37 or any("relation_candidate" not in (row.get("qualifiers") or {}) for row in final_page):
        raise SystemExit("p.210 statements remain unclassified or the planned statement count changed")
    if len(statements) != 14241 or len(candidates) != 12026 or len(mentions) != 28074:
        raise SystemExit(f"unexpected output counts: statements={len(statements)}, candidates={len(candidates)}, mentions={len(mentions)}")

    outputs = {STATEMENTS: jsonl_bytes(statements), CANDIDATES: csv_bytes(candidate_fields, candidates),
               MENTIONS: csv_bytes(mention_fields, mentions)}
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    print("p.210 statements:", len(final_page),
          "true:", sum(row["qualifiers"]["relation_candidate"] is True for row in final_page),
          "false:", sum(row["qualifiers"]["relation_candidate"] is False for row in final_page))
    print("new statements:", ", ".join(sorted(NEW_STATEMENT_IDS)))
    print("new candidates:", ", ".join(row["candidate_id"] for row in new_candidates))
    print("new mentions:", ", ".join(row["mention_id"] for row in new_mentions))
    print("removed non-entity mentions: m-chp8-p210-051, m-chp8-p210-072")
    for path, data in outputs.items():
        print(f"{path.relative_to(ROOT)} sha256={sha(data)} bytes={len(data)}")

    if args.apply:
        for path, backup in backups.items():
            shutil.copy2(path, backup)
        try:
            for path, data in outputs.items():
                atomic_write(path, data)
        except Exception:
            for path, backup in backups.items():
                path.write_bytes(backup.read_bytes())
            raise
        print("recovery copies:", ", ".join(str(path.relative_to(ROOT)) for path in backups.values()))


if __name__ == "__main__":
    main()
