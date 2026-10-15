from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l40-52"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"

BACKUPS = {
    STATEMENTS: TABLES / "book-statements.jsonl.bak-s2-chp3-sec-ii-l40-52-relations-20261010",
    CANDIDATES: TABLES / "entity-candidates.csv.bak-s2-chp3-sec-ii-l40-52-relations-20261010",
    MENTIONS: TABLES / "mentions.csv.bak-s2-chp3-sec-ii-l40-52-relations-20261010",
}

HASHES = {
    STATEMENTS: "a1759d5ff8db01139667e4a718c92180f3331adbc6824116d04462ab63abc44f",
    CANDIDATES: "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    MENTIONS: "fb2d4512ace8ebd177abf3279b0a10ad0610aab8038fe03c8b3de33eb6097dba",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

ID = {
    "altarpiece_domitilla": "st-chp3-secii-l40-52-altarpiece-depicts-st-domitilla",
    "altarpiece_saints": "st-chp3-secii-l40-52-altarpiece-flanked-by-saints",
    "angelo": "st-chp3-secii-l40-52-angelo-continues-family-patronage",
    "barocci_commission": "st-chp3-secii-l40-52-barocci-painted-commission",
    "barocci_effect": "st-chp3-secii-l40-52-barocci-picture-aesthetic-effect",
    "cesi_fund": "st-chp3-secii-l40-52-cesi-fund-chiesa-nuova",
    "cesi_influence": "st-chp3-secii-l40-52-cesi-influence-farnese",
    "cesi_interference": "st-chp3-secii-l40-52-cesi-little-building-interference",
    "cesi_rights": "st-chp3-secii-l40-52-cesi-seek-farnese-rights",
    "cesi_terms": "st-chp3-secii-l40-52-cesi-terms-arms-privileges",
    "chapel_merit": "st-chp3-secii-l40-52-chapel-paintings-sometimes-high-merit",
    "chapels_marian": "st-chp3-secii-l40-52-chapels-marian-mysteries",
    "coronation_not_obtained": "st-chp3-secii-l40-52-coronation-altarpiece-not-obtained",
    "families_decorated": "st-chp3-secii-l40-52-families-decorated-chapels",
    "family_changed_church": "st-chp3-secii-l40-52-family-patronage-changed-church-character",
    "facade": "st-chp3-secii-l40-52-fa\u00e7ade-erection-delay",
    "financial": "st-chp3-secii-l40-52-financial-difficulties-seek-patron",
    "high_altar": "st-chp3-secii-l40-52-high-altar-nativity",
    "longhi": "st-chp3-secii-l40-52-longhi-replaces-matteo",
    "main_structure": "st-chp3-secii-l40-52-main-structure-complete",
    "many_patrons": "st-chp3-secii-l40-52-many-new-patrons-florentine-cultured",
    "accept_terms": "st-chp3-secii-l40-52-oratorians-accept-terms",
    "commission": "st-chp3-secii-l40-52-oratorians-commission-visitation-altarpiece",
    "kept_affairs": "st-chp3-secii-l40-52-oratorians-kept-affairs",
    "sought_more": "st-chp3-secii-l40-52-oratorians-sought-more-barocci",
    "patrons_variety": "st-chp3-secii-l40-52-patrons-added-variety-richness-colour",
    "philip_concealed": "st-chp3-secii-l40-52-philip-concealed-picture-effects",
    "philip_sent_away": "st-chp3-secii-l40-52-philip-sent-away-viewing-women",
    "philip_whitewash": "st-chp3-secii-l40-52-philip-whitewash-not-stucco",
    "pomerancio_altarpiece": "st-chp3-secii-l40-52-pomerancio-altarpiece-and-location",
    "pomerancio_portrait": "st-chp3-secii-l40-52-pomerancio-painted-philip-portrait",
    "pomerancio_popular": "st-chp3-secii-l40-52-pomerancio-popular",
    "presentation": "st-chp3-secii-l40-52-presentation-of-jesus-commissioned",
    "ecstasy": "st-chp3-secii-l40-52-reported-philip-ecstasy",
    "same_process": "st-chp3-secii-l40-52-same-process-earlier-in-music",
    "transept": "st-chp3-secii-l40-52-transept-altars-presentation-coronation",
    "arrived_rome": "st-chp3-secii-l40-52-visitation-painting-arrived-rome",
}

NEW_IDS = {
    "cesi_shared": "st-chp3-secii-l40-52-cesi-shared-love-art-splendour",
    "cesi_plans": "st-chp3-secii-l40-52-cesi-plans-based-on-farnese",
    "cesi_personal_privileges": "st-chp3-secii-l40-52-cesi-personal-congregation-privileges",
    "cesi_family_privileges": "st-chp3-secii-l40-52-cesi-family-congregation-privileges",
    "altarpiece_achilleus": "st-chp3-secii-l40-52-altarpiece-flanked-by-achilleus",
    "transept_coronation": "st-chp3-secii-l40-52-transept-altars-coronation",
    "paintings_location": "st-chp3-secii-l40-52-chapel-paintings-located-in-chapels",
    "altarpiece_location": "st-chp3-secii-l40-52-altarpiece-located-in-titular-church",
    "baronio_titular": "st-chp3-secii-l40-52-baronio-titular-church",
}

CANDIDATE_ROWS = [
    {
        "candidate_id": "cand-11588",
        "index_entry_id": "",
        "canonical_name": "Women who came to gaze at Philip Neri (unnamed group)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Passage-bounded, unnamed group of women said to come to gaze at Philip Neri before the Barocci picture; membership and count are not supplied.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L49",
    },
    {
        "candidate_id": "cand-11589",
        "index_entry_id": "",
        "canonical_name": "Paintings in the chapels taken over by the new patrons (unnamed group)",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Unnamed group referred to collectively as paintings in the new patrons' chapels; the passage supplies no titles, artists, membership, or count.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L52",
    },
]

FALSE_NOTES = {
    ID["chapel_merit"]: "This is Haskell's evaluative attribute of an unnamed group of paintings, not an entity-to-entity relation; the paintings' chapel setting is recorded separately.",
    ID["main_structure"]: "Completion by 1590 is a temporal state of Chiesa Nuova, not a relation between entities.",
    ID["many_patrons"]: "This describes the unnamed patron group; 'many' and 'often' remain qualified and no individual patrons are inferred.",
    ID["same_process"]: "This is Haskell's historical analogy between changes in chapel decoration and earlier musical performances, not a direct entity relation.",
}

TRUE_NOTES = {
    ID["altarpiece_domitilla"]: "Haskell describes the altarpiece as depicting St Domitilla; keep the visual description attributed to him and the print footnote link.",
    ID["altarpiece_saints"]: "Haskell places St Nereus as one of two saints flanking St Domitilla; the companion figure is recorded separately.",
    ID["angelo"]: "Haskell says Angelo Cesi continued the Cesi family's patronage of Chiesa Nuova some years after Pier Donato's death.",
    ID["barocci_commission"]: "Haskell says the Oratorians turned to Barocci for the Chapel of the Visitation altarpiece; preserve Urbino as the stated context.",
    ID["barocci_effect"]: "Haskell describes the painting's appeal to Philip Neri; retain the author's aesthetic and psychological characterization.",
    ID["cesi_fund"]: "Haskell says Pier Donato Cesi agreed to fund completion of Chiesa Nuova.",
    ID["cesi_influence"]: "Haskell characterizes Pier Donato Cesi as under Cardinal Farnese's influence; the two following claims are split out.",
    ID["cesi_interference"]: "Haskell says Cesi interfered little in the church building; preserve the qualified wording.",
    ID["cesi_rights"]: "Cesi sought rights like Farnese's; Farnese is the comparator, while Chiesa Nuova and Ges\u00f9 remain distinct location qualifiers.",
    ID["cesi_terms"]: "Haskell says accepted terms provided for Cesi's arms to be set up in Chiesa Nuova; this is not a report that they were installed.",
    ID["chapels_marian"]: "Haskell says the Chiesa Nuova chapels were dedicated to Marian mysteries; the named dedications remain separate statements.",
    ID["coronation_not_obtained"]: "Haskell says the Oratorians failed to obtain Barocci's Coronation altarpiece; this does not establish whether another version existed.",
    ID["families_decorated"]: "Haskell says wealthy families who took over the chapels generally assumed responsibility for their decoration.",
    ID["family_changed_church"]: "Haskell attributes a change in Chiesa Nuova's character to family-led chapel decoration; preserve this interpretive claim.",
    ID["facade"]: "The façade is related to Chiesa Nuova's main structure by a sixteen-year interval; do not calculate an absolute erection year.",
    ID["financial"]: "Haskell's immediate narrative identifies Pier Donato Cesi as the patron who agreed to fund completion; no other patron or date is inferred.",
    ID["high_altar"]: "Haskell says the High Altar was assigned to the Nativity of the Virgin.",
    ID["longhi"]: "Haskell says Martino Longhi the Elder replaced Matteo da Castello as architect of Chiesa Nuova.",
    ID["accept_terms"]: "Haskell says the Oratorians accepted Cesi's terms.",
    ID["commission"]: "Haskell says the Oratorians commissioned the untitled Chapel of the Visitation painting in 1582; its subject is not supplied here.",
    ID["kept_affairs"]: "Haskell says the Oratorians largely kept Chiesa Nuova's affairs in their own hands; retain 'largely'.",
    ID["sought_more"]: "Haskell says the Oratorians wanted additional works by Barocci; no further completed commission is inferred.",
    ID["patrons_variety"]: "Haskell says intervention by the new patrons introduced variety, richness, and colour into Chiesa Nuova.",
    ID["philip_concealed"]: "Haskell reports that Philip would try to conceal the painting's effects on him; retain the habitual 'would'.",
    ID["philip_sent_away"]: "Haskell reports Philip angrily sending away the unnamed women who came to gaze at him; keep the women as a bounded but unidentified group.",
    ID["philip_whitewash"]: "Haskell says Philip insisted on whitewashed walls and vault without stucco; whether this reflected taste or economy remains unclear.",
    ID["pomerancio_altarpiece"]: "Haskell attributes the altarpiece to Pomerancio; the exact title remains unspecified and S3 identity normalization remains open.",
    ID["pomerancio_portrait"]: "Haskell says Pomerancio painted a portrait of Philip Neri; no title, date, or location is supplied.",
    ID["pomerancio_popular"]: "Haskell says Pomerancio was especially popular with the Oratorian Congregation; identity normalization remains for S3.",
    ID["presentation"]: "Haskell says the Oratorians managed to commission Barocci's Presentation of Jesus in the Temple.",
    ID["ecstasy"]: "Haskell reproduces an unspecified account of Philip's response to the painting; do not treat it as independently verified.",
    ID["transept"]: "Haskell assigns the Presentation of the Virgin to the transept altars; the Coronation dedication is recorded separately.",
    ID["arrived_rome"]: "Haskell says the painting reached Rome four years after its commission; no arrival year is calculated.",
}

ANCHORS = {
    ID["altarpiece_domitilla"]: "St Domitilla with a rapt expression",
    ID["altarpiece_saints"]: "between Saints Nereus and Achilleus",
    ID["angelo"]: "continued the family patronage",
    ID["barocci_commission"]: "they turned to Federico Barocci in Urbino",
    ID["barocci_effect"]: "made a special appeal to the mystical strand",
    ID["cesi_fund"]: "he agreed to pay for the completion",
    ID["cesi_influence"]: "under the influence of Cardinal",
    ID["cesi_interference"]: "he interfered little enough",
    ID["cesi_rights"]: "same rights as those of Farnese",
    ID["cesi_terms"]: "His arms too were to be set up",
    ID["chapel_merit"]: "paintings in their chapels were sometimes of high merit",
    ID["chapels_marian"]: "chapels were then dedicated to the mysteries",
    ID["coronation_not_obtained"]: "unsuccessful in getting from him an altarpiece of the Coronation",
    ID["families_decorated"]: "rich families who took over the chapels to be responsible for their decoration",
    ID["family_changed_church"]: "change the character of the church",
    ID["facade"]: "fa\u00e7ade by Fausto Rughesi",
    ID["financial"]: "Oratorians were now compelled to turn to a patron",
    ID["high_altar"]: "High Altar being assigned to Her Nativity",
    ID["longhi"]: "Martino Longhi the Elder replaced Matteo da Castello",
    ID["main_structure"]: "main structure was complete",
    ID["many_patrons"]: "Many of the new patrons were Florentines",
    ID["accept_terms"]: "His terms were accepted",
    ID["commission"]: "commissioned an altar painting to be placed",
    ID["kept_affairs"]: "The Oratorians thus kept the affairs",
    ID["sought_more"]: "anxious to obtain other works by the same artist",
    ID["patrons_variety"]: "with their intervention there was introduced a new note",
    ID["philip_concealed"]: "conceal the effects of the picture",
    ID["philip_sent_away"]: "irritated by the women who came to gaze at him",
    ID["philip_whitewash"]: "walls and the vault should be merely whitewashed",
    ID["pomerancio_altarpiece"]: "an altarpiece showing St Domitilla",
    ID["pomerancio_portrait"]: "he had painted St Philip\u2019s portrait",
    ID["pomerancio_popular"]: "Congregation was Pomerancio",
    ID["presentation"]: "managed to commission one of The Presentation of Jesus in the Temple",
    ID["ecstasy"]: "unconsciously be rapt into a sweet ecstasy",
    ID["same_process"]: "same process had occurred many years earlier in the musical performances",
    ID["transept"]: "those in the transepts to Her Presentation and Her Coronation",
    ID["arrived_rome"]: "which reached Rome four years later",
}

EXPECTED_BEFORE = {
    "statements": 12704,
    "candidates": 11565,
    "mentions": 27504,
    "bilateral": 8499,
    "bilateral_true": 4590,
    "bilateral_false": 460,
    "bilateral_pending": 3449,
    "relation_candidates_total": 4637,
    "relation_candidates_open": 47,
}

EXPECTED_AFTER = {
    "statements": 12713,
    "candidates": 11567,
    "mentions": 27506,
    "bilateral": 8509,
    "bilateral_true": 4632,
    "bilateral_false": 460,
    "bilateral_pending": 3417,
    "relation_candidates_total": 4679,
    "relation_candidates_open": 47,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value: str) -> str:
    return " ".join(value.split())


def parse_jsonl(raw: bytes):
    parsed = []
    offset = 0
    for line in raw.splitlines(keepends=True):
        if line.strip():
            parsed.append((json.loads(line), offset, offset + len(line), line))
        offset += len(line)
    return parsed


def has_endpoint(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def stats(statements, candidates, mentions):
    both = [
        row for row in statements
        if has_endpoint(row.get("subject_candidate_id")) and has_endpoint(row.get("object_candidate_id"))
    ]

    def flag(row):
        qualifiers = row.get("qualifiers", {})
        return qualifiers.get("relation_candidate") if isinstance(qualifiers, dict) else None

    return {
        "statements": len(statements),
        "candidates": len(candidates),
        "mentions": len(mentions),
        "bilateral": len(both),
        "bilateral_true": sum(flag(row) is True for row in both),
        "bilateral_false": sum(flag(row) is False for row in both),
        "bilateral_pending": sum(flag(row) is None for row in both),
        "relation_candidates_total": sum(flag(row) is True for row in statements),
        "relation_candidates_open": sum(
            flag(row) is True
            and not (has_endpoint(row.get("subject_candidate_id")) and has_endpoint(row.get("object_candidate_id")))
            for row in statements
        ),
    }


def csv_read(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    with io.StringIO(text, newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    newline = "\r\n" if raw.count(b"\r\n") > raw.count(b"\n") / 2 else "\n"
    return fields, rows, bom, newline


def csv_write(fields, rows, bom, newline):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    data = handle.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def atomic_replace(path: Path, data: bytes):
    fd, temp_name = tempfile.mkstemp(prefix=f"{path.stem}.s2-l40-52.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def clone_statement(parent, new_id, subject, obj, predicate, claim, quote, start, end, note, extra=None, qualification=None):
    row = dict(parent)
    q = dict(parent.get("qualifiers", {}))
    for key in ("additional_subject_candidate_id", "additional_event_candidate_id", "venue_candidate_id", "family_candidate_id"):
        q.pop(key, None)
    q.update({
        "source_line_start": start,
        "source_line_end": end,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "print_page": 69,
        "pdf_physical_page": 7,
        "relation_candidate": True,
        "relation_candidate_note": note,
    })
    if qualification:
        q["qualification"] = qualification
    if extra:
        q.update(extra)
    row.update({
        "statement_id": new_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    })
    return row


def make_new_statements(targets):
    rows = []
    # Split Cesi's influence, shared taste, and plans into three distinct claims.
    rows.append(clone_statement(
        targets[ID["cesi_influence"]], NEW_IDS["cesi_shared"], "cand-0640", "cand-0995",
        "shared_love_of_art_and_splendour_with",
        "Haskell says Pier Donato Cesi shared Cardinal Farnese's love of art and splendour.",
        "He shared his love of art and of splendour", 43, 43,
        "Haskell describes shared aesthetic interests; this is separate from Cesi's influence and plans.",
        qualification="The pronoun refers to Pier Donato Cesi in the immediately preceding sentence.",
    ))
    rows.append(clone_statement(
        targets[ID["cesi_influence"]], NEW_IDS["cesi_plans"], "cand-0640", "cand-0995",
        "based_many_plans_on",
        "Haskell says many of Pier Donato Cesi's plans were directly based on Cardinal Farnese's.",
        "many of his plans were directly based on those of the older and more powerful figure", 43, 43,
        "Haskell attributes the planning relationship to Cesi; the passage does not identify individual plans.",
        qualification="The pronouns refer to Cesi and Farnese respectively.",
        extra={"quantity_qualifier": "many"},
    ))

    # Split Cesi's accepted terms into the arms display, his privileges, and family privileges.
    terms = targets[ID["cesi_terms"]]
    privileges_quote = "he and his family were to enjoy overriding privileges in the affairs of the Congregation"
    rows.append(clone_statement(
        terms, NEW_IDS["cesi_personal_privileges"], "cand-0640", "cand-3402",
        "was_to_enjoy_overriding_privileges_in",
        "Haskell says the accepted terms provided that Cesi was to enjoy overriding privileges in Congregation affairs.",
        privileges_quote, 43, 43,
        "This scalar statement covers Pier Donato Cesi's own privileges; family privileges are recorded separately.",
        qualification="The terms were accepted; this passage does not describe later exercise of these privileges.",
    ))
    rows.append(clone_statement(
        terms, NEW_IDS["cesi_family_privileges"], "cand-5030", "cand-3402",
        "was_to_enjoy_overriding_privileges_in",
        "Haskell says the accepted terms provided that Cesi's family was to enjoy overriding privileges in Congregation affairs.",
        privileges_quote, 43, 43,
        "This scalar statement covers the Cesi family as a group, distinct from Pier Donato Cesi himself.",
        qualification="The terms were accepted; no later exercise or individual family member is asserted.",
    ))

    rows.append(clone_statement(
        targets[ID["altarpiece_saints"]], NEW_IDS["altarpiece_achilleus"], "cand-5046", "cand-5049",
        "depicts_flanking_saint",
        "Haskell describes St Achilleus as one of the saints flanking St Domitilla in the altarpiece.",
        "between Saints Nereus and Achilleus", 50, 50,
        "The second flanking figure is recorded as a separate scalar depiction claim.",
        extra={"central_figure_candidate_id": "cand-5047", "depiction_position": "flanking"},
    ))
    rows.append(clone_statement(
        targets[ID["transept"]], NEW_IDS["transept_coronation"], "cand-5034", "cand-5037",
        "assigned_to_dedication",
        "Haskell says the transept altars were assigned to the Coronation of the Virgin.",
        "Her Coronation", 48, 48,
        "The Coronation dedication is split from the Presentation dedication; the altars remain an unspecified group.",
    ))
    rows.append(clone_statement(
        targets[ID["chapel_merit"]], NEW_IDS["paintings_location"], "cand-11589", "cand-5042",
        "located_in",
        "Haskell locates the unnamed group of paintings in the chapels taken over by the new patrons.",
        "the paintings in their chapels", 52, 52,
        "The source explicitly gives the paintings' chapel setting; no individual work or chapel is identified.",
        extra={"patron_group_candidate_id": "cand-5044"},
    ))
    rows.append(clone_statement(
        targets[ID["pomerancio_altarpiece"]], NEW_IDS["altarpiece_location"], "cand-5046", "cand-5050",
        "located_in",
        "Haskell places Pomerancio's altarpiece in Cardinal Baronio's titular church of that name.",
        "in Cardinal Baronio’s titular church of that name", 50, 50,
        "The work's venue is explicit, but the church identity behind 'of that name' remains unresolved.",
        extra={"venue_name_referent": "St Domitilla"},
    ))
    rows.append(clone_statement(
        targets[ID["pomerancio_altarpiece"]], NEW_IDS["baronio_titular"], "cand-0250", "cand-5050",
        "had_titular_church",
        "Haskell identifies the described church as Cardinal Baronio's titular church.",
        "Cardinal Baronio’s titular church of that name", 50, 50,
        "The titular relation is stated, but the church's formal identity remains unresolved in this passage.",
        extra={"venue_name_referent": "St Domitilla"},
    ))
    return rows


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    for path, expected in HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"SHA mismatch for {path.relative_to(ROOT)}: {actual}")
    for backup in BACKUPS.values():
        if backup.exists():
            raise SystemExit(f"recovery backup already exists: {backup}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = [row for row in csv.DictReader(handle) if row["segment_id"] == SEGMENT]
    if len(coverage) != 1 or (
        coverage[0]["disposition"], coverage[0]["migration_status"], coverage[0]["source_line_ranges"]
    ) != ("reviewed", "complete", "L41-52"):
        raise SystemExit(f"unexpected coverage row: {coverage}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[39:52])
    if len(segment_text) != 3459 or segment_text.find("the women who came to gaze at him") != 2056 or segment_text.find("the paintings in their chapels") != 3160:
        raise SystemExit("segment text or planned mention spans changed")

    statement_raw = STATEMENTS.read_bytes()
    parsed = parse_jsonl(statement_raw)
    rows = [row for row, _, _, _ in parsed]
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT]
    targets = {row["statement_id"]: row for row in segment_rows}
    if len(segment_rows) != 37 or set(targets) != set(ID.values()):
        raise SystemExit(f"unexpected segment statements: rows={len(segment_rows)}, ids={len(targets)}")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in segment_rows):
        raise SystemExit("a target statement already has a relation decision")

    source_text = normalize(" ".join(source_lines))
    for statement_id, anchor in ANCHORS.items():
        row = targets[statement_id]
        q = row.get("qualifiers", {})
        if anchor not in normalize(row.get("original_quote", "")):
            raise SystemExit(f"quote anchor missing from statement {statement_id}: {anchor}")
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start > end:
            raise SystemExit(f"invalid source locator for {statement_id}: {q}")
        if anchor not in normalize(" ".join(source_lines[start - 1:end])):
            raise SystemExit(f"source anchor not found for {statement_id}: {anchor}")
    if "Cardinal Pier Donato Cesi" not in source_text or "Saints Nereus" not in source_text or "Achilleus" not in source_text:
        raise SystemExit("required source context changed")

    candidate_fields, candidate_rows, candidate_bom, candidate_newline = csv_read(CANDIDATES)
    mention_fields, mention_rows, mention_bom, mention_newline = csv_read(MENTIONS)
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    numeric_ids = [int(row["candidate_id"].removeprefix("cand-")) for row in candidate_rows if row["candidate_id"].removeprefix("cand-").isdigit()]
    if len(candidate_rows) != 11565 or max(numeric_ids) != 11587:
        raise SystemExit(f"candidate table changed: rows={len(candidate_rows)}, max_id={max(numeric_ids)}")
    if len(mention_rows) != 27504:
        raise SystemExit(f"mention table changed: rows={len(mention_rows)}")
    if candidate_ids.intersection(row["candidate_id"] for row in CANDIDATE_ROWS):
        raise SystemExit("new candidate ID already exists")
    new_mention_ids = ["m-chp3-secii-l40-52-0065", "m-chp3-secii-l40-52-0066"]
    if mention_ids.intersection(new_mention_ids):
        raise SystemExit("new mention ID already exists")
    if len({row["statement_id"] for row in rows}) != len(rows):
        raise SystemExit("statement table already contains duplicate IDs")
    if set(NEW_IDS.values()).intersection(row["statement_id"] for row in rows):
        raise SystemExit("one or more split statement IDs already exist")

    before = stats(rows, candidate_rows, mention_rows)
    if before != EXPECTED_BEFORE:
        raise SystemExit(f"unexpected pre-write counts: {before}")

    replacements = {}
    for statement_id, row in targets.items():
        updated = dict(row)
        q = dict(row.get("qualifiers", {}))
        q["relation_candidate"] = statement_id not in FALSE_NOTES
        q["relation_candidate_note"] = FALSE_NOTES[statement_id] if statement_id in FALSE_NOTES else TRUE_NOTES[statement_id]
        updated["qualifiers"] = q
        replacements[statement_id] = updated

    def edit(statement_id, *, subject=None, obj=None, predicate=None, claim=None, quote=None, source_end=None, remove_q=(), q_updates=None):
        row = dict(replacements[statement_id])
        q = dict(row.get("qualifiers", {}))
        for key in remove_q:
            q.pop(key, None)
        if q_updates:
            q.update(q_updates)
        row["qualifiers"] = q
        if subject is not None:
            row["subject_candidate_id"] = subject
        if obj is not None:
            row["object_candidate_id"] = obj
        if predicate is not None:
            row["predicate"] = predicate
        if claim is not None:
            q["claim"] = claim
        if quote is not None:
            row["original_quote"] = quote
        if source_end is not None:
            q["source_line_end"] = source_end
        row["qualifiers"] = q
        replacements[statement_id] = row

    edit(ID["cesi_influence"], predicate="was_under_influence_of", claim="Haskell says Pier Donato Cesi was very much under Cardinal Farnese's influence.", quote="Cardinal Pier Donato Cesi was obviously very much under the influence of Cardinal Farnese.")
    edit(ID["cesi_rights"], obj="cand-0995", predicate="sought_rights_matching_those_of", claim="Haskell says Cesi insisted on rights at Chiesa Nuova like those Farnese enjoyed at the Ges\u00f9.", q_updates={"target_church_candidate_id": "cand-0710", "comparison_venue_candidate_id": "cand-3112"})
    edit(ID["cesi_terms"], obj="cand-0710", predicate="arms_to_be_displayed_in", claim="Haskell says Cesi's accepted terms provided that his arms were to be set up in Chiesa Nuova.", remove_q=("family_candidate_id",), q_updates={"terms_accepted_by_candidate_id": "cand-3402", "qualification": "The terms were accepted; this passage does not state that the arms were later installed."})
    edit(ID["financial"], obj="cand-0640", predicate="sought_patronage_from", claim="Haskell says financial difficulties compelled the Oratorians to turn to a patron, whom the immediate narrative identifies as Pier Donato Cesi, who agreed to fund completion of the church.", quote="difficulties soon intervened, and the Oratorians were now compelled to turn to a patron. Cardinal Pier Donato Cesi was obviously very much under the influence of Cardinal Farnese. He shared his love of art and of splendour and many of his plans were directly based on those of the older and more powerful figure. When, therefore, he agreed to pay for the completion of the Chiesa Nuova", source_end=43, q_updates={"source_line_start": 41, "identified_patron_candidate_id": "cand-0640", "qualification": "The next sentences identify Cesi as the patron in this narrative sequence and say he agreed to pay for completion; no other patron or exact transaction date is inferred."})
    edit(ID["facade"], obj="cand-0710", predicate="fa\u00e7ade_erected_after_main_structure_completion_of", claim="Haskell says the Chiesa Nuova fa\u00e7ade was erected sixteen years after the church's main structure was complete.", q_updates={"temporal_anchor_candidate_id": "cand-0710", "interval_years": 16, "qualification": "The source supplies a relative interval only; no absolute erection year is calculated."})
    edit(ID["philip_sent_away"], obj="cand-11588", predicate="reported_sent_away_women_viewing_him_before_picture", claim="Haskell reports that, irritated by the women who came to gaze at him before the picture, Philip would angrily send them away.", q_updates={"context_work_candidate_id": "cand-5039", "group_candidate_id": "cand-11588", "qualification": "The group is unnamed and its membership and count are unknown; 'would' remains a reported habitual account."})
    edit(ID["chapel_merit"], subject="cand-11589", obj="", predicate="sometimes_of_high_merit", claim="Haskell says the paintings in the new patrons' chapels were sometimes of high merit.", quote="Many of the new patrons were Florentines, like St Philip himself, often of great culture, and thus it was that the paintings in their chapels were sometimes of high merit.", q_updates={"chapels_candidate_id": "cand-5042", "patron_group_candidate_id": "cand-5044", "qualification": "This is Haskell's evaluative description of an unnamed work group; 'sometimes' is retained."})
    edit(ID["transept"], predicate="assigned_to_dedication", claim="Haskell says the transept altars were assigned to the Presentation of the Virgin.", remove_q=("additional_event_candidate_id",), q_updates={"dedication_candidate_id": "cand-5036"})
    edit(ID["altarpiece_saints"], predicate="depicts_flanking_saint", claim="Haskell describes St Nereus as one of the saints flanking St Domitilla in the altarpiece.", remove_q=("additional_subject_candidate_id",), q_updates={"central_figure_candidate_id": "cand-5047", "depiction_position": "flanking"})
    edit(ID["pomerancio_altarpiece"], predicate="painted", claim="Haskell says Pomerancio had painted the altarpiece showing St Domitilla between Saints Nereus and Achilleus.", remove_q=("venue_candidate_id",), q_updates={"qualification": "The work's exact title is not supplied. The p.69 footnote marker is linked to p.70 note 1; the cited publications were not independently consulted."})
    edit(ID["pomerancio_portrait"], q_updates={"qualification": "Haskell identifies a portrait of Philip Neri but supplies no title, date, or location; the p.69 print has no footnote marker after this portrait clause."})
    edit(ID["pomerancio_popular"], predicate="was_popular_with", claim="Haskell says Pomerancio was especially popular with the Oratorian Congregation.", quote="Another artist especially popular with the Congregation was Pomerancio", q_updates={"source_line_start": 49, "source_line_end": 50, "qualification": "The sentence crosses the L49-L50 line break; the body name is mapped to the Pomerancio index candidate and identity normalization remains for S3."})
    edit(ID["altarpiece_domitilla"], q_updates={"qualification": "Haskell's visual description is followed by p.69 footnote 1, linked to p.70 note 1; the cited publications were not independently consulted."})
    edit(ID["same_process"], q_updates={"qualification": "Haskell compares changes in chapel decoration with earlier changes in Oratorian musical performances; no individual performance is identified.", "continuation_segment_id": "chp-3:03_CHP-3_sec_ii:l54-60"})

    new_statements = make_new_statements(targets)
    insert_after = {
        ID["cesi_influence"]: [new_statements[0], new_statements[1]],
        ID["cesi_terms"]: [new_statements[2], new_statements[3]],
        ID["altarpiece_saints"]: [new_statements[4]],
        ID["transept"]: [new_statements[5]],
        ID["chapel_merit"]: [new_statements[6]],
        ID["pomerancio_altarpiece"]: [new_statements[7], new_statements[8]],
    }

    note_ids = {"st-chp3-secii-p69-p70-note1-cozzi", "st-chp3-secii-p69-p70-note1-friedlaender"}
    note_replacements = 0
    added_links = [ID["altarpiece_saints"], NEW_IDS["altarpiece_achilleus"], NEW_IDS["altarpiece_location"]]
    for row, _, _, _ in parsed:
        if row.get("statement_id") not in note_ids:
            continue
        updated = dict(row)
        q = dict(row.get("qualifiers", {}))
        linked = list(q.get("linked_body_statement_ids", []))
        for linked_id in added_links:
            if linked_id not in linked:
                linked.append(linked_id)
        q["linked_body_statement_ids"] = linked
        updated["qualifiers"] = q
        replacements[row["statement_id"]] = updated
        note_replacements += 1
    if note_replacements != 2:
        raise SystemExit(f"expected two p.70 footnote 1 citation rows, found {note_replacements}")

    all_new_ids = set(NEW_IDS.values())
    if set(row["statement_id"] for row in new_statements) != all_new_ids:
        raise SystemExit("unexpected split statement ID set")

    pieces = []
    inserted_ids = set()
    for row, start, end, raw_line in parsed:
        statement_id = row.get("statement_id")
        newline = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n"
        if statement_id in replacements:
            pieces.append(json.dumps(replacements[statement_id], ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline)
        else:
            pieces.append(raw_line)
        for addition in insert_after.get(statement_id, []):
            pieces.append(json.dumps(addition, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline)
            inserted_ids.add(addition["statement_id"])
    if inserted_ids != all_new_ids:
        raise SystemExit(f"not all new statements were inserted: {inserted_ids ^ all_new_ids}")
    projected_statement_bytes = b"".join(pieces)
    projected_statements = [row for row, _, _, _ in parse_jsonl(projected_statement_bytes)]
    projected_segment = [row for row in projected_statements if row.get("segment_id") == SEGMENT]
    if len(projected_segment) != 46:
        raise SystemExit(f"unexpected projected segment statement count: {len(projected_segment)}")
    if len({row["statement_id"] for row in projected_statements}) != len(projected_statements):
        raise SystemExit("projected statement IDs are not unique")

    # Validate every new statement's exact quotation against the cited source line range.
    for row in new_statements:
        q = row["qualifiers"]
        excerpt = normalize(" ".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]]))
        quote = normalize(row["original_quote"])
        if quote not in excerpt:
            raise SystemExit(f"new quote is not present in its source lines: {row['statement_id']}")

    candidate_projection = candidate_rows + CANDIDATE_ROWS
    mention_specs = [
        {
            "mention_id": "m-chp3-secii-l40-52-0065",
            "segment_id": SEGMENT,
            "candidate_id": "cand-11588",
            "surface_form": "the women who came to gaze at him",
            "start_char": "2056",
            "end_char": "2089",
            "note": "Passage-bounded unnamed group; object of Philip Neri's reported act of sending them away.",
        },
        {
            "mention_id": "m-chp3-secii-l40-52-0066",
            "segment_id": SEGMENT,
            "candidate_id": "cand-11589",
            "surface_form": "the paintings in their chapels",
            "start_char": "3160",
            "end_char": "3190",
            "note": "Unnamed group of works described as being in the new patrons' chapels; no individual painting is named.",
        },
    ]
    mention_projection = list(mention_rows)
    # Keep the local segment's mentions in source order, before the next segment's rows.
    last_target_index = max(i for i, row in enumerate(mention_projection) if row["segment_id"] == SEGMENT)
    mention_projection[last_target_index + 1:last_target_index + 1] = mention_specs

    for candidate in CANDIDATE_ROWS:
        if candidate["candidate_id"] in candidate_ids:
            raise SystemExit(f"duplicate candidate ID: {candidate['candidate_id']}")
    for mention in mention_specs:
        if mention["mention_id"] in mention_ids:
            raise SystemExit(f"duplicate mention ID: {mention['mention_id']}")
        if segment_text[int(mention["start_char"]):int(mention["end_char"])] != mention["surface_form"]:
            raise SystemExit(f"mention span mismatch: {mention['mention_id']}")

    candidate_bytes = csv_write(candidate_fields, candidate_projection, candidate_bom, candidate_newline)
    mention_bytes = csv_write(mention_fields, mention_projection, mention_bom, mention_newline)
    final_stats = stats(projected_statements, candidate_projection, mention_projection)
    if final_stats != EXPECTED_AFTER:
        raise SystemExit(f"unexpected projected counts: {final_stats}")
    target_true = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in projected_segment)
    target_false = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in projected_segment)
    if (target_true, target_false) != (42, 4):
        raise SystemExit(f"unexpected target relation classification counts: true={target_true}, false={target_false}")

    print(json.dumps({
        "mode": "dry-run" if args.dry_run else "apply",
        "segment_id": SEGMENT,
        "print_page": 69,
        "physical_pdf_page": 7,
        "source_statement_count_before": len(segment_rows),
        "source_statement_count_after": len(projected_segment),
        "new_statements": list(NEW_IDS.values()),
        "new_candidates": [row["candidate_id"] for row in CANDIDATE_ROWS],
        "new_mentions": [row["mention_id"] for row in mention_specs],
        "classifications": {"relation_candidates": target_true, "nonrelations": target_false},
        "before": before,
        "after": final_stats,
        "updated_note_rows": sorted(note_ids),
        "backups": [str(path.relative_to(ROOT)) for path in BACKUPS.values()] if args.apply else [],
    }, ensure_ascii=False, indent=2))

    if args.dry_run:
        return

    # Save all recovery copies before replacing any table.
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)

    atomic_replace(STATEMENTS, projected_statement_bytes)
    atomic_replace(CANDIDATES, candidate_bytes)
    atomic_replace(MENTIONS, mention_bytes)

    written_statements = [row for row, _, _, _ in parse_jsonl(STATEMENTS.read_bytes())]
    written_candidates = csv_read(CANDIDATES)[1]
    written_mentions = csv_read(MENTIONS)[1]
    written_stats = stats(written_statements, written_candidates, written_mentions)
    if written_stats != EXPECTED_AFTER:
        raise SystemExit(f"post-write mismatch: {written_stats}; backups retained")
    actual_segment = [row for row in written_statements if row.get("segment_id") == SEGMENT]
    if len(actual_segment) != 46 or sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in actual_segment) != 42:
        raise SystemExit("post-write target segment verification failed; backups retained")
    print(json.dumps({
        "post_write_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (STATEMENTS, CANDIDATES, MENTIONS)},
        "post_write_counts": written_stats,
        "recovery_backups_retained": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
