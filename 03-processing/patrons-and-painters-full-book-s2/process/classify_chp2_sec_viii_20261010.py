from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_viii.md"
PDF = ROOT / "02-sources/01-book/CHP-2.pdf"
BACKUP_SUFFIX = ".bak-s2-handoff-chp2-p61-p62-conclusion-20261010"

EXPECTED_SHA = {
    STATEMENTS: "637010822eb67c99c1a6c6c206f77ad6f7549744aef2a1c780d3622fd0b19205",
    MENTIONS: "ad57d10340723ec589285d0ad37a1ea0e5963a96360896febbe6e07abf5e31a9",
    CANDIDATES: "b4ac5c42748249c553bf133ab9267acb9fbb85422d1198208b19b7e8b8c250de",
    SOURCE: "95f938db89eb64a86bbc54065bf1e93e2d4849cd6ed5e6b02aedbe0f1e23350a",
    PDF: "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
}

SEGMENT_A = "chp-2:02_CHP-2_sec_viii:l3-7"
SEGMENT_B = "chp-2:02_CHP-2_sec_viii:l9-14"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_viii.md"
GROUP_ID = "cand-11577"
BOOK = "cand-2962"
BERNINI = "cand-0295"
CORTONA = "cand-0342"
BARBERINI = "cand-0198"
BORROMINI = "cand-0404"
URBAN = "cand-0209"
ROME = "cand-4490"
PAPACY = "cand-4223"
FRANCE_POLITICAL = "cand-4221"
WAR = "cand-4965"
SCHOLARS = "cand-4971"
COURTS = "cand-4970"
PAINTERS = "cand-4972"

TRUE_NOTES = {
    "artist-patron-relationship-fruitful": "Haskell explicitly evaluates the Bernini–Barberini relationship as unusually fruitful; this is a source-attributed relationship assessment, not an independently verified outcome.",
    "barberini-admired-borromini-talents": "The source reports occasional Barberini admiration for Borromini; the p.61 footnote is linked, and the statement remains source-qualified.",
    "barberini-heritage-and-artistic-choice": "Haskell attributes the later influence of the city's Baroque style to the Barberini choice of artists; no specific later building or commission is inferred.",
    "barberini-patronage-realization-and-support": "The source explicitly reports the family's recognition and support of the two artists named immediately before; the collective endpoint is bounded to Bernini and Pietro da Cortona.",
    "bernini-and-cortona-not-originally-discovered": "The source makes an explicit negative claim about the family's prior discovery of this two-artist group; it is retained as a negative S2 candidate, not converted into a positive edge.",
    "bernini-authority-relative-neglect-borromini": "Haskell attributes Borromini's relative neglect through the end of Urban's reign to Bernini's artistic authority; this is a source-specific causal candidate.",
    "bernini-barberini-common-culture-fragment": "This page-ending clause asserts one shared characteristic of Bernini and the Barberini; the following statement continues the same comparison with further traits.",
    "bernini-retained-despite-construction-errors": "The source reports that the Barberini retained Bernini while his constructional errors threatened to overwhelm him; this is a patronage candidate.",
    "camassei-dropped-as-limitations-emerged": "The source reports the Barberini ending their support of Camassei as his limitations became apparent; this is a patronage candidate.",
    "first-supreme-opportunities-to-bernini-and-cortona": "The source says the Barberini gave first supreme opportunities to the two artists named in the passage; the collective endpoint is bounded to those two.",
    "no-new-squares-recall-urban": "The source makes a negative public-commemoration claim about Urban VIII; no square is named, so the object endpoint remains open.",
    "rome-not-transformed-under-urban": "The source explicitly denies a transformation of Rome under Urban VIII; retain the negation and do not infer a positive urban project.",
    "antonio-supports-sacchi": "Haskell explicitly names Cardinal Antonio's support of Andrea Sacchi as a contrasting patronage example.",
    "bernin-barberini-and-julius-michelangelo-comparison": "Haskell explicitly compares the Bernini–Barberini relationship with the Julius II–Michelangelo relationship; no additional property of the comparator pair is inferred.",
    "bernin-later-introspection-not-pursued-under-urban": "The source ties Bernini's artistic direction while working for Urban to the absence of later introspection and mysticism; no unnamed sculpture is identified.",
    "confidence-enabled-bernin-experiment": "The source says confidence between Bernini and the Barberini allowed him to experiment; this is a source-qualified relationship claim.",
    "francesco-supports-pietro": "Haskell explicitly names Cardinal Francesco's support of Pietro da Cortona as a contrasting patronage example.",
    "french-king-self-glorification-through-lebrun": "The text calls Le Brun the unnamed King of France's artist and says he used a modified Cortona style to express royal self-glorification; no specific appointment or commission is inferred.",
    "scholar-painter-contact-and-intellectual-art": "Haskell says the unnamed scholar group was brought into contact with the unnamed painter group and attributes later intellectual effects to that contact; the two groups are explicit S2 endpoints only.",
    "shared-traits-completed": "The continuation explicitly attributes shared respect for the past, religious feeling with dramatic ostentation, and ambition to Bernini and the Barberini; it is an authorial comparison, not kinship or formal affiliation.",
    "war-end-and-france-change-papal-situation": "The source explicitly names the end of the Thirty Years' War as one factor expected to change the papacy's remaining international position; the separate France factor is split into its own statement.",
}

FALSE_NOTES = {
    "bernini-genius-and-authority": "This is Haskell's assessment of Bernini's stature and authority over unnamed arts; no discrete entity-to-entity relation is asserted in this statement.",
    "borromini-exception-in-rome": "This is a comparative assessment of artistic stature in Rome, not a claim that Borromini held a specific position or had a formal relation with the city.",
    "family-sense-of-values": "This is Haskell's assessment of the family's judgement; the statement does not assert a separate relation between identifiable entities.",
    "barberini-opinions-and-contrasting-tendencies": "This characterizes the family's opinions and contrasting tendencies; the specific patronage examples are recorded in separate statements.",
    "contrast-with-earlier-experiments-and-borghese-taste": "This compares broad artistic climates and Cardinal Borghese's taste; it does not assert a specific relation with the Barberini period.",
    "cortona-ceiling-hysteria-interpretation": "This is Haskell's interpretive description of a single fresco's mood, not a relation candidate.",
    "court-art-grandeur-flattery": "This is a general characterization of court art with no identified endpoint pair.",
    "illusionism-overwhelms-onlooker": "This is a generalized account of techniques and audience effect; no specific work or identifiable audience is named.",
    "learning-as-barberini-circle-characteristic": "This characterizes the Barberini circle's attention to learning; the concrete court, scholar, and painter relations are handled separately.",
    "no-later-pope-matches-urban-self-glorification": "This is a broad comparative judgement about unnamed later popes, not a specific historical relation candidate.",
    "papacy-loss-power-prestige-under-urban": "This reports an institutional condition during Urban's reign; it does not assert a direct relation between the papacy and Urban.",
    "period-freedom-from-dogmatism-and-variety": "This is a general characterization of the period's intellectual climate, not an entity relation.",
    "religious-imagery-supports-secular-claims": "This is a general interpretive proposition about types of imagery and claims; it names no specific work or claim endpoint.",
    "urban-death-changes-situation": "This is a retrospective transition summary with an undefined 'situation' and an unbounded 'everyone'; it is retained as a statement, not a relation candidate.",
}

SEGMENT_A_SUFFIXES = {
    "artist-patron-relationship-fruitful", "barberini-admired-borromini-talents",
    "barberini-heritage-and-artistic-choice", "barberini-patronage-realization-and-support",
    "bernini-and-cortona-not-originally-discovered", "bernini-authority-relative-neglect-borromini",
    "bernini-barberini-common-culture-fragment", "bernini-genius-and-authority",
    "bernini-retained-despite-construction-errors", "borromini-exception-in-rome",
    "camassei-dropped-as-limitations-emerged", "family-sense-of-values",
    "first-supreme-opportunities-to-bernini-and-cortona", "no-new-squares-recall-urban",
    "rome-not-transformed-under-urban",
}


def statement_id(suffix: str) -> str:
    segment = "l3-7" if suffix in SEGMENT_A_SUFFIXES else "l9-14"
    return f"st-chp2-sec-viii-{segment}-{suffix}"


TRUE_IDS = {statement_id(suffix) for suffix in TRUE_NOTES}
FALSE_IDS = {statement_id(suffix) for suffix in FALSE_NOTES}
CLASSIFICATION = {
    **{statement_id(suffix): (True, note) for suffix, note in TRUE_NOTES.items()},
    **{statement_id(suffix): (False, note) for suffix, note in FALSE_NOTES.items()},
}

NEW_FRANCE_ID = "st-chp2-sec-viii-l9-14-france-arrogance-changes-papal-situation"
NEW_SCHOLAR_ID = "st-chp2-sec-viii-l9-14-scholars-welcomed-at-barberini-courts"
NEW_MENTION_BOTH = "m-chp2-sec-viii-l3-7-0032"
NEW_MENTION_THEM = "m-chp2-sec-viii-l3-7-0033"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.splitlines(keepends=True)
    rows = [json.loads(line.decode("utf-8-sig")) for line in lines if line.strip()]
    newline = b"\r\n" if any(line.endswith(b"\r\n") for line in lines) else b"\n"
    return rows, bom, newline


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames
    return rows, fields, bom, newline


def write_jsonl(rows: list[dict], bom: bool, newline: bytes) -> bytes:
    out = []
    for i, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if i == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        out.append(line + newline)
    return b"".join(out)


def write_csv(rows: list[dict], fields: list[str], bom: bool, newline: str) -> bytes:
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    data = buf.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def counts(rows: list[dict]) -> dict:
    marked = [s for s in rows if (s.get("qualifiers") or {}).get("relation_candidate") is True]
    complete = sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) for s in marked)
    dual_unclassified = sum(
        bool(s.get("subject_candidate_id") and s.get("object_candidate_id"))
        and (s.get("qualifiers") or {}).get("relation_candidate") not in (True, False)
        for s in rows
    )
    return {
        "statements": len(rows), "relations": len(marked), "complete_relations": complete,
        "open_relations": len(marked) - complete, "dual_unclassified": dual_unclassified,
        "footnote_claims": sum(s.get("predicate") == "footnote-claim" for s in rows),
        "cites": sum(s.get("predicate") == "cites" and
                     (s.get("qualifiers") or {}).get("relation_candidate") is True for s in rows),
    }


def preflight():
    for path, expected in EXPECTED_SHA.items():
        require(sha(path) == expected, f"unexpected SHA-256 for {path.relative_to(ROOT)}")
    statements, statement_bom, statement_newline = read_jsonl(STATEMENTS)
    mentions, mention_fields, mention_bom, mention_newline = read_csv(MENTIONS)
    candidates, candidate_fields, candidate_bom, candidate_newline = read_csv(CANDIDATES)
    by_id = {s["statement_id"]: s for s in statements}
    require(len(by_id) == len(statements), "duplicate statement_id")
    target = {sid for sid in by_id if sid.startswith("st-chp2-sec-viii-")}
    require(target == TRUE_IDS | FALSE_IDS, f"classification does not cover exact section statements: {len(target)}")
    require(all((by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in target),
            "some target statements have already been classified")
    require(NEW_FRANCE_ID not in by_id and NEW_SCHOLAR_ID not in by_id,
            "new statement ID already exists")
    require(counts(statements) == {
        "statements": 12680, "relations": 3659, "complete_relations": 3644,
        "open_relations": 15, "dual_unclassified": 4427, "footnote_claims": 1, "cites": 118,
    }, f"ledger counts changed: {counts(statements)}")
    require(len(candidates) == 11554 and len(mentions) == 27487, "candidate/mention counts changed")
    numeric_ids = [int(c["candidate_id"].split("-")[1]) for c in candidates]
    require(max(numeric_ids) == 11576 and GROUP_ID not in {c["candidate_id"] for c in candidates},
            "candidate ID sequence changed")
    candidate_by_id = {c["candidate_id"]: c for c in candidates}
    require(FRANCE_POLITICAL in candidate_by_id and candidate_by_id[FRANCE_POLITICAL]["suggested_type"] == "institution",
            "political France candidate changed or is missing")
    require(all(c in candidate_by_id for c in (BERNINI, CORTONA, BARBERINI, PAPACY, WAR, SCHOLARS, COURTS, PAINTERS)),
            "expected candidate endpoint missing")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_a = "\n".join(source_lines[2:7])
    segment_b = "\n".join(source_lines[8:14])
    mention_by_id = {m["mention_id"]: m for m in mentions}
    pair_mention = mention_by_id.get("m-chp2-sec-viii-l3-7-0017")
    require(pair_mention is not None and pair_mention["surface_form"] == "these men"
            and pair_mention["candidate_id"] == BERNINI and pair_mention["start_char"] == "828"
            and pair_mention["end_char"] == "837" and segment_a[828:837] == "these men",
            "plural referent mention changed")
    france_mention = mention_by_id.get("m-chp2-sec-viii-l9-14-0009")
    require(france_mention is not None and france_mention["surface_form"] == "France"
            and france_mention["candidate_id"] == "cand-4266" and france_mention["start_char"] == "816"
            and france_mention["end_char"] == "822" and segment_b[816:822] == "France",
            "France mention changed")
    require(NEW_MENTION_BOTH not in mention_by_id and NEW_MENTION_THEM not in mention_by_id,
            "new mention ID already exists")
    require(not any(m["segment_id"] == SEGMENT_A and m["start_char"] == "547" for m in mentions),
            "the 'both' mention already exists")
    require(not any(m["segment_id"] == SEGMENT_A and m["start_char"] == "859" for m in mentions),
            "the second 'them' mention already exists")

    pdf_text = " ".join(__import__("fitz").open(PDF)[49].get_text().split())
    pdf_text_62 = " ".join(__import__("fitz").open(PDF)[50].get_text().split())
    require('though "the Barberini showed on occasion that they admired his talents' in pdf_text,
            "p.61 PDF text layer does not verify the clause location; the print-only reading was separately checked in the page image")
    require("arrogance of France" in pdf_text_62 and "Scholars of all kinds" in pdf_text_62,
            "print p.62 does not verify the source claims")
    return (statements, statement_bom, statement_newline, mentions, mention_fields, mention_bom,
            mention_newline, candidates, candidate_fields, candidate_bom, candidate_newline,
            by_id, candidate_by_id, segment_a, segment_b)


def make_candidate() -> dict:
    return {
        "candidate_id": GROUP_ID, "index_entry_id": "",
        "canonical_name": "Bernini and Pietro da Cortona (collective referent in Haskell's passage)",
        "index_page_range": "", "suggested_type": "", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "The plural referents 'both', 'these men', and the later 'them' in this passage denote Gian Lorenzo Bernini (cand-0295) and Pietro da Cortona (cand-0342). The bounded pair is used only to resolve this source passage; it is not an institutional group, and no further members are implied.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_viii:l3-7#L3",
    }


def make_changes(state):
    (statements, statement_bom, statement_newline, mentions, mention_fields, mention_bom,
     mention_newline, candidates, candidate_fields, candidate_bom, candidate_newline,
     by_id, candidate_by_id, segment_a, segment_b) = state
    rows = copy.deepcopy(statements)
    by_id = {s["statement_id"]: s for s in rows}
    require(len(CLASSIFICATION) == 35, f"expected 35 classifications, got {len(CLASSIFICATION)}")
    for sid, (is_relation, note) in CLASSIFICATION.items():
        s = by_id[sid]
        q = s.setdefault("qualifiers", {})
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note

    pair_ids = (
        "st-chp2-sec-viii-l3-7-barberini-patronage-realization-and-support",
        "st-chp2-sec-viii-l3-7-bernini-and-cortona-not-originally-discovered",
        "st-chp2-sec-viii-l3-7-first-supreme-opportunities-to-bernini-and-cortona",
    )
    for sid in pair_ids:
        require(by_id[sid]["subject_candidate_id"] == BARBERINI and by_id[sid].get("object_candidate_id") is None,
                f"collective endpoint changed: {sid}")
        by_id[sid]["object_candidate_id"] = GROUP_ID
    mention_rows = copy.deepcopy(mentions)
    mention_by_id = {m["mention_id"]: m for m in mention_rows}
    mention_by_id["m-chp2-sec-viii-l3-7-0017"]["candidate_id"] = GROUP_ID
    france = mention_by_id["m-chp2-sec-viii-l9-14-0009"]
    france["candidate_id"] = FRANCE_POLITICAL
    new_mentions = [
        {"mention_id": NEW_MENTION_BOTH, "segment_id": SEGMENT_A, "candidate_id": GROUP_ID,
         "surface_form": "both", "start_char": "547", "end_char": "551",
         "note": "Plural anaphor refers to Bernini and Pietro da Cortona, the two artists named immediately before."},
        {"mention_id": NEW_MENTION_THEM, "segment_id": SEGMENT_A, "candidate_id": GROUP_ID,
         "surface_form": "them", "start_char": "859", "end_char": "863",
         "note": "Object of 'support'; refers to Bernini and Pietro da Cortona as the bounded collective pair."},
    ]
    require(segment_a[547:551] == "both" and segment_a[859:863] == "them", "new plural mention spans changed")
    last_segment_index = max(i for i, m in enumerate(mention_rows) if m["segment_id"] == SEGMENT_A)
    mention_rows[last_segment_index + 1:last_segment_index + 1] = new_mentions

    candidate_rows = copy.deepcopy(candidates)
    candidate_rows.append(make_candidate())

    # Record the print-only correction without altering S0 or original_quote.
    borromini = by_id["st-chp2-sec-viii-l3-7-barberini-admired-borromini-talents"]
    borromini_q = borromini["qualifiers"]
    corrections = borromini_q.setdefault("ocr_corrections", [])
    require(not any(x.get("source_line") == 6 for x in corrections if isinstance(x, dict)),
            "line 6 OCR correction already exists")
    corrections.append({
        "source_file": SOURCE_FILE, "source_line": 6,
        "ocr": 'though "the Barberini showed on occasion that they admired his talents.',
        "print": "though the Barberini showed on occasion that they admired his talents.",
        "basis": "CHP-2.pdf physical page 50.",
    })

    # Split the two causes in the p.62 sentence so France is not treated as a place.
    war = by_id["st-chp2-sec-viii-l9-14-war-end-and-france-change-papal-situation"]
    war_q = war["qualifiers"]
    war_q["claim"] = "Haskell says the end of the Thirty Years' War would soon change the papacy's remaining international political position."
    war_q["qualification"] = "The source supplies no more exact interval for 'soon'; this statement isolates the war-ending factor from France's separate political role."
    war_q.pop("additional_place_candidate_id", None)
    war_q.pop("political_entity_candidate_id", None)
    war_q["relation_candidate"] = True
    war_q["relation_candidate_note"] = TRUE_NOTES["war-end-and-france-change-papal-situation"]
    france_statement = copy.deepcopy(war)
    france_statement["statement_id"] = NEW_FRANCE_ID
    france_statement["subject_candidate_id"] = FRANCE_POLITICAL
    france_statement["object_candidate_id"] = PAPACY
    france_statement["predicate"] = "political-change-anticipated"
    france_statement["qualifiers"] = copy.deepcopy(war_q)
    france_statement["qualifiers"]["claim"] = "Haskell says France's arrogance would soon change the papacy's remaining international political position."
    france_statement["qualifiers"]["qualification"] = "The source supplies no more exact interval for 'soon'; France is treated as the political actor named in the sentence, not as a geographic location."
    france_statement["qualifiers"]["political_entity_candidate_id"] = FRANCE_POLITICAL
    france_statement["qualifiers"]["relation_candidate_note"] = "S2 candidate for Haskell's attributed claim about France's political effect on the papacy; the source names no individual French ruler or government action, and no formal S6 edge is created."

    # Separate scholars' reception at court from their contact with painters.
    scholar_contact = by_id["st-chp2-sec-viii-l9-14-scholar-painter-contact-and-intellectual-art"]
    contact_q = scholar_contact["qualifiers"]
    contact_q.pop("painter_group_candidate_id", None)
    contact_q["claim"] = "Haskell says scholars of all kinds were brought into contact with painters, giving rise to art of great intellectual subtlety and theories that later became highly influential."
    contact_q["qualification"] = "Neither scholars nor painters are individually identified; the claimed cultural effects remain attributed to Haskell."
    scholar_contact["subject_candidate_id"] = SCHOLARS
    scholar_contact["object_candidate_id"] = PAINTERS
    scholar_contact["predicate"] = "brought-into-contact-with"
    contact_q["relation_candidate"] = True
    contact_q["relation_candidate_note"] = TRUE_NOTES["scholar-painter-contact-and-intellectual-art"]
    court_welcome = copy.deepcopy(scholar_contact)
    court_welcome["statement_id"] = NEW_SCHOLAR_ID
    court_welcome["subject_candidate_id"] = SCHOLARS
    court_welcome["object_candidate_id"] = COURTS
    court_welcome["predicate"] = "hosted_by"
    court_welcome["qualifiers"] = copy.deepcopy(contact_q)
    court_welcome["qualifiers"]["claim"] = "Haskell says scholars of all kinds were welcomed at Barberini courts."
    court_welcome["qualifiers"]["qualification"] = "The source names plural courts but does not identify their institutional boundaries or any individual scholars."
    court_welcome["qualifiers"].pop("artistic_result", None)
    court_welcome["qualifiers"].pop("theories_later_influential", None)
    court_welcome["qualifiers"]["relation_candidate_note"] = "S2 candidate for the source's explicit report that scholars were welcomed at Barberini courts; the courts and scholars remain source-level collectives, and no formal S6 edge is created."

    output = []
    for s in rows:
        output.append(s)
        if s["statement_id"] == scholar_contact["statement_id"]:
            output.append(court_welcome)
        if s["statement_id"] == war["statement_id"]:
            output.append(france_statement)
    return output, mention_rows, candidate_rows, statement_bom, statement_newline, mention_fields, mention_bom, mention_newline, candidate_fields, candidate_bom, candidate_newline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes; default is dry-run")
    args = parser.parse_args()
    state = preflight()
    (statements, mentions, candidates, statement_bom, statement_newline, mention_fields, mention_bom,
     mention_newline, candidate_fields, candidate_bom, candidate_newline) = make_changes(state)
    after = counts(statements)
    require(after["statements"] == 12682 and after["relations"] == 3682 and
            after["complete_relations"] == 3666 and after["open_relations"] == 16 and
            after["footnote_claims"] == 1 and after["cites"] == 118,
            f"projected counts differ: {after}")
    preview = {
        "action": "apply" if args.apply else "dry-run",
        "before": counts(state[0]), "after": after,
        "candidate_rows": {"before": len(state[7]), "after": len(candidates)},
        "mention_rows": {"before": len(state[3]), "after": len(mentions)},
        "classified_existing_statements": {"relation": len(TRUE_IDS), "not_relation": len(FALSE_IDS)},
        "open_relation_statement": "st-chp2-sec-viii-l3-7-no-new-squares-recall-urban",
        "new_candidates": [GROUP_ID],
        "new_mentions": [NEW_MENTION_BOTH, NEW_MENTION_THEM],
        "new_statements": [NEW_SCHOLAR_ID, NEW_FRANCE_ID],
        "corrected_mentions": {
            "these men": GROUP_ID,
            "both": GROUP_ID,
            "support them": GROUP_ID,
            "France": FRANCE_POLITICAL,
        },
    }
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    if not args.apply:
        return

    targets = [STATEMENTS, MENTIONS, CANDIDATES]
    backups = {p: p.with_name(p.name + BACKUP_SUFFIX) for p in targets}
    for backup in backups.values():
        require(not backup.exists(), f"recovery backup already exists: {backup.name}")
    for p, backup in backups.items():
        shutil.copy2(p, backup)
    payloads = {
        STATEMENTS: write_jsonl(statements, statement_bom, statement_newline),
        MENTIONS: write_csv(mentions, mention_fields, mention_bom, mention_newline),
        CANDIDATES: write_csv(candidates, candidate_fields, candidate_bom, candidate_newline),
    }
    temps = []
    try:
        for p, content in payloads.items():
            with tempfile.NamedTemporaryFile(dir=p.parent, prefix=p.name + ".tmp-", delete=False) as f:
                f.write(content)
                temps.append((p, Path(f.name)))
        for p, temp in temps:
            os.replace(temp, p)
        post_statements, *_ = read_jsonl(STATEMENTS)
        post_mentions, *_ = read_csv(MENTIONS)
        post_candidates, *_ = read_csv(CANDIDATES)
        require(counts(post_statements) == after, "post-write statement counts mismatch")
        require(len(post_mentions) == 27489 and len(post_candidates) == 11555, "post-write table row counts mismatch")
        by_id = {s["statement_id"]: s for s in post_statements}
        require(NEW_FRANCE_ID in by_id and NEW_SCHOLAR_ID in by_id and GROUP_ID in {c["candidate_id"] for c in post_candidates},
                "post-write new rows missing")
        require(by_id[NEW_FRANCE_ID]["subject_candidate_id"] == FRANCE_POLITICAL and
                by_id[NEW_FRANCE_ID]["object_candidate_id"] == PAPACY, "France relation endpoints changed")
        require(by_id["st-chp2-sec-viii-l3-7-barberini-admired-borromini-talents"]["qualifiers"]["ocr_corrections"],
                "print correction missing")
        print(json.dumps({
            "result": "applied", "counts": counts(post_statements),
            "statements_sha256": sha(STATEMENTS), "mentions_sha256": sha(MENTIONS),
            "candidates_sha256": sha(CANDIDATES),
            "backups": {str(p.relative_to(ROOT)): str(b.relative_to(ROOT)) for p, b in backups.items()},
        }, ensure_ascii=True, indent=2))
    except Exception:
        for p, backup in backups.items():
            shutil.copy2(backup, p)
        raise
    finally:
        for _, temp in temps:
            if temp.exists():
                temp.unlink()


if __name__ == "__main__":
    main()
