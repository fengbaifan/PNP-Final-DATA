from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l106-116"
SOURCE_SHA = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA = "a8b23e48d2d3b070393ce4916c2070c2af41aab6567c9689f15a87c5ab512e6c"
PRE_HASHES = {
    STATEMENTS.name: "beb8635ec3d607c4770aa8d8b6ed3a89356966c6881ca4332285414030604d83",
    CANDIDATES.name: "a2ff14404ac175aebc840ec14757224268e36b5c769900a0cc6efdc598bac9ce",
    MENTIONS.name: "f185325cc1c16819bcfc4acf1f0b703a8190573471b40eaa6ee1f6af9b539dee",
}
BACKUP_SUFFIX = ".bak-s2-chp3-seciv-l106-116-relations-20261011"

RELATION_NOTES = {
    "st-chp3-seciv-l106-116-camillo-visited-work-in-progress":
        "Haskell explicitly says Camillo visited the active rebuilding work in 1663; this does not identify the unfinished project with the later completed church.",
    "st-chp3-seciv-l106-116-camillo-left-1000-scudi":
        "Camillo's money is directed to the rebuilding project; the 1663 visit is event context. No modern currency conversion is inferred.",
    "st-chp3-seciv-l106-116-camillo-ordered-berni-obeyed":
        "Records Camillo's reported instruction to follow Bernini's orders; the conditional statement is not treated as proof that all his substance was spent.",
    "st-chp3-seciv-l106-116-berni-refused-battle-pictures":
        "Haskell reports Bernini refused this specified group of battle pictures as payment; titles and number remain unknown.",
    "st-chp3-seciv-l106-116-berni-scrutinised-and-endorsed-bills":
        "Records Bernini's reported scrutiny and endorsement of project bills and contracts; no individual document is identified.",
    "st-chp3-seciv-l106-116-berni-supervised-workmen":
        "Records direct supervision of the source's unnamed workmen group; no membership or count is inferred.",
    "st-chp3-seciv-l106-116-berni-virtual-patron-and-refused-payment":
        "Haskell calls Bernini the virtual patron of the rebuilding enterprise; this is not converted into formal ownership or a documented appointment.",
    "st-chp3-seciv-l106-116-berni-refused-all-payment":
        "Records Bernini's project-scoped refusal of payment. The source does not name a payer or quantify the refused remuneration.",
    "st-chp3-seciv-l106-116-mattia-assistant-to-berni":
        "The source explicitly identifies Mattia de' Rossi as Bernini's assistant.",
    "st-chp3-seciv-l106-116-mattia-paid-in-kind":
        "Records the reported in-kind remuneration for Mattia's work in this project context; the payer is not identified.",
    "st-chp3-seciv-l106-116-plates-uncertain-raphael-attribution":
        "Preserves Haskell's expressly tentative attribution of the two plates to Raphael or his school; it is not an accepted authorship claim.",
    "st-chp3-seciv-l106-116-church-as-expression-of-berni":
        "Records Haskell's interpretive expression link between the specific S. Andrea index subentry and Bernini's genius; it does not establish authorship by itself.",
    "st-chp3-seciv-l106-116-iconography-centred-on-andrew":
        "Haskell links the church's decorative iconography to the separately represented figure of St Andrew, retaining the qualification 'in some degree'.",
    "st-chp3-seciv-l106-116-jesuit-destination-provided-impulse":
        "Preserves Haskell's interpretation that the Jesuit destination supplied a special artistic impulse; it does not assert a specific commission by the Jesuits.",
    "st-chp3-seciv-l106-116-putti-descend-into-chapel":
        "Records the described spatial movement of the unnamed golden-putti group into the main chapel; no individual count or medium is inferred.",
    "st-chp3-seciv-l106-116-spatial-pressure-compared-to-gesu":
        "Haskell explicitly compares the described emotional and spatial effect with the later Gesu; the comparison does not assert a historical dependency.",
    "st-chp3-seciv-l106-116-spatial-pressure-compared-to-s-ignazio":
        "Haskell explicitly compares the described emotional and spatial effect with the later S. Ignazio; the comparison does not assert a historical dependency.",
    "st-chp3-seciv-l106-116-berni-advice-presumed":
        "Preserves Haskell's inference that Bernini's advice must have been taken; the source does not document the advice or its implementation.",
    "st-chp3-seciv-l106-116-heirs-funded-artists":
        "Records Haskell's reported funding connection between the unidentified heirs and the altar-painting arrangements; the pronoun is not expanded to claim that every artist or work was paid by them.",
    "st-chp3-seciv-l106-116-jesuits-arranged-artists-directly":
        "Haskell explicitly attributes the direct arrangements with artists to the Jesuits.",
    "st-chp3-seciv-l106-116-jesuits-considered-altar-paintings":
        "Haskell explicitly says the Jesuits considered the altar-painting problem after the main structure was complete.",
    "st-chp3-seciv-l106-116-guglielmo-commissioned-martyrdom-1668":
        "Records the reported 1668 commission to Guglielmo for the named work; the commissioner is not identified in this sentence.",
    "st-chp3-seciv-l106-116-martyrdom-for-high-altar":
        "Records the source's placement destination for this specific altarpiece; no survival or current location is inferred.",
    "st-chp3-seciv-l106-116-guglielmo-and-giacomo-novitiate-work":
        "Haskell says Guglielmo had been employed at the novitiate with his Jesuit brother; the name continues on p.88, so the cross-page evidence remains qualified.",
    "st-chp3-seciv-l106-116-gaulli-payment-note-865-13":
        "Haskell's footnote reports a cited archival entry that Gaulli was paid from the novitiate's own funds through Scaramuccia; the archival item has not been independently consulted.",
    "st-chp3-seciv-l106-116-novitiate-intended-recovery-from-prince":
        "The cited entry says Novitiate funds were advanced with the intention to recover the sum from the unnamed Prince; Scaramuccia is the named intermediary. It does not report a completed recovery.",
}
NONRELATION_NOTES = {
    "st-chp3-seciv-l106-116-enterprise-gauged-by-visit":
        "This is Haskell's narrative framing of an episode as evidence for the project's spirit, not a historical relation between the project and the visit.",
    "st-chp3-seciv-l106-116-plates-unsold":
        "This is a reported status of the plate group; the attempted sale has no identified counterparty.",
    "st-chp3-seciv-l106-116-plates-valuation":
        "This is a scalar valuation claim with no identified valuer, date, or counterparty.",
    "st-chp3-seciv-l106-116-church-marble-and-oval-plan":
        "This is a descriptive architectural claim about the church's material, decoration, and plan, not a directed relation between two entities.",
    "st-chp3-seciv-l106-116-lantern-light-symbolism":
        "This describes a visual-symbolic effect within one dome; the current endpoints identify the church and dome, not distinct light and ray entities, so it remains a claim rather than a relation candidate.",
    "st-chp3-seciv-l106-116-sunlight-effect-more-poignant-than-fresco":
        "This is Haskell's scalar comparison of visual effect, with no specific fresco identified as the other endpoint.",
    "st-chp3-seciv-l106-116-prince-pamfili-reported-dead-1667":
        "This is a one-entity date/status claim. The unnamed Prince remains distinct from Camillo and from other Pamfili candidates.",
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11617",
        "index_entry_id": "",
        "canonical_name": "Jesuit novitiate of S. Andrea al Quirinale (institutional funds source)",
        "index_page_range": "",
        "suggested_type": "institution",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The cited footnote says Gaulli's payment was made from the funds of the Novitiate. This is the institutional financial referent, distinct from the unresolved novitiate place candidate cand-5080 and from the Jesuits candidate cand-3403. The cited archival item has not been independently consulted.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L114",
    },
    {
        "candidate_id": "cand-11618",
        "index_entry_id": "",
        "canonical_name": "Unidentified workmen engaged in the S. Andrea rebuilding",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Unspecified group of workers, including those assigned the most menial tasks, whom Haskell says Bernini directly supervised. Members and count are not given.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L109",
    },
]

EXPECTED_IDS = {
    "st-chp3-seciv-l106-116-berni-advice-presumed",
    "st-chp3-seciv-l106-116-berni-refused-battle-pictures",
    "st-chp3-seciv-l106-116-berni-scrutinised-and-endorsed-bills",
    "st-chp3-seciv-l106-116-berni-supervised-workmen",
    "st-chp3-seciv-l106-116-berni-virtual-patron-and-refused-payment",
    "st-chp3-seciv-l106-116-camillo-left-1000-scudi",
    "st-chp3-seciv-l106-116-camillo-ordered-berni-obeyed",
    "st-chp3-seciv-l106-116-camillo-visited-work-in-progress",
    "st-chp3-seciv-l106-116-church-as-expression-of-berni",
    "st-chp3-seciv-l106-116-church-marble-and-oval-plan",
    "st-chp3-seciv-l106-116-enterprise-gauged-by-visit",
    "st-chp3-seciv-l106-116-gaulli-payment-note-865-13",
    "st-chp3-seciv-l106-116-guglielmo-and-giacomo-novitiate-work",
    "st-chp3-seciv-l106-116-guglielmo-commissioned-martyrdom-1668",
    "st-chp3-seciv-l106-116-heirs-funded-artists",
    "st-chp3-seciv-l106-116-iconography-centred-on-andrew",
    "st-chp3-seciv-l106-116-jesuit-destination-provided-impulse",
    "st-chp3-seciv-l106-116-jesuits-arranged-artists-directly",
    "st-chp3-seciv-l106-116-jesuits-considered-altar-paintings",
    "st-chp3-seciv-l106-116-lantern-light-symbolism",
    "st-chp3-seciv-l106-116-martyrdom-for-high-altar",
    "st-chp3-seciv-l106-116-mattia-assistant-to-berni",
    "st-chp3-seciv-l106-116-mattia-paid-in-kind",
    "st-chp3-seciv-l106-116-plates-uncertain-raphael-attribution",
    "st-chp3-seciv-l106-116-plates-unsold",
    "st-chp3-seciv-l106-116-plates-valuation",
    "st-chp3-seciv-l106-116-prince-pamfili-reported-dead-1667",
    "st-chp3-seciv-l106-116-putti-descend-into-chapel",
    "st-chp3-seciv-l106-116-spatial-pressure-compared-to-gesu",
    "st-chp3-seciv-l106-116-spatial-pressure-compared-to-s-ignazio",
    "st-chp3-seciv-l106-116-sunlight-effect-more-poignant-than-fresco",
}
NEW_STATEMENTS = [
    {
        "statement_id": "st-chp3-seciv-l106-116-berni-refused-all-payment",
        "subject_candidate_id": "cand-0298",
        "object_candidate_id": "cand-5309",
        "predicate": "refused_all_payment_for_project",
        "qualifiers": {
            "source_line_start": 109,
            "source_line_end": 109,
            "claim": "Haskell says Bernini refused all payment for his role in the enterprise.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": 87,
            "pdf_physical_page": 29,
            "qualification": "The source gives no named payer or total remuneration; the separately recorded battle-picture example is not treated as an additional payment.",
            "relation_candidate": True,
            "relation_candidate_note": RELATION_NOTES["st-chp3-seciv-l106-116-berni-refused-all-payment"],
        },
        "original_quote": "",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "segment_id": SEGMENT_ID,
    },
    {
        "statement_id": "st-chp3-seciv-l106-116-novitiate-intended-recovery-from-prince",
        "subject_candidate_id": "cand-11617",
        "object_candidate_id": "cand-5327",
        "predicate": "reported_intention_to_recover_novitiate_funds_from_prince",
        "qualifiers": {
            "source_line_start": 114,
            "source_line_end": 116,
            "claim": "Haskell's quoted archival report attributes to Father Francesco Scaramuccia an intention to recover the Novitiate-funded sum from Prince Pamfili.",
            "speaker": "Haskell quoting a cited archival entry; the stated intention is attributed to Father Francesco Scaramuccia",
            "text_layer": "footnote quote and archival-source report",
            "print_page": 87,
            "pdf_physical_page": 29,
            "qualification": "The cited archival item has not been independently consulted. The passage reports an intention, not a completed recovery; the Prince is not identified as Camillo.",
            "archive_candidate_id": "cand-5338",
            "intermediary_candidate_id": "cand-5339",
            "source_claim_not_independently_verified": True,
            "linked_body_statement_ids": [
                "st-chp3-seciv-l106-116-heirs-funded-artists",
                "st-chp3-seciv-l106-116-prince-pamfili-reported-dead-1667",
            ],
            "relation_candidate": True,
            "relation_candidate_note": RELATION_NOTES["st-chp3-seciv-l106-116-novitiate-intended-recovery-from-prince"],
        },
        "original_quote": "",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "segment_id": SEGMENT_ID,
    },
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> tuple[list[str], list[dict], str, bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), eol, has_bom


def encode_csv(fields: list[str], rows: list[dict], eol: str, has_bom: bool) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="raise", lineterminator=eol)
    writer.writeheader()
    writer.writerows(rows)
    text = output.getvalue()
    return (("\ufeff" if has_bom else "") + text).encode("utf-8")


def encode_jsonl(rows: list[dict], eol: str, has_bom: bool) -> bytes:
    text = eol.join(json.dumps(row, ensure_ascii=False) for row in rows) + eol
    return (("\ufeff" if has_bom else "") + text).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write only after all preconditions pass")
    args = parser.parse_args()

    require(sha(SOURCE) == SOURCE_SHA, "source file hash changed")
    source_text = SOURCE.read_text(encoding="utf-8-sig")
    source_lines = source_text.splitlines()
    segment_text = "\n".join(source_lines[105:116])
    require(hashlib.sha256(segment_text.encode("utf-8")).hexdigest() == SEGMENT_SHA,
            "source segment hash changed")
    require("Workmen engaged on the most menial tasks" in segment_text, "workmen anchor missing")
    require("He was himself the virtual patron of the whole enterprise" in segment_text,
            "virtual patron anchor missing")
    require("con animo di rivalersene dal Signor" in segment_text,
            "footnote recovery anchor missing")

    for path in [STATEMENTS, CANDIDATES, MENTIONS]:
        require(sha(path) == PRE_HASHES[path.name], f"pre-write hash changed: {path.name}")

    statement_rows = read_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_eol, candidate_bom = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_eol, mention_bom = read_csv(MENTIONS)
    segment_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    segment_ids = {row["statement_id"] for row in segment_rows}
    require(len(segment_rows) == 31 and segment_ids == EXPECTED_IDS,
            "unexpected statement set for this segment")
    require(all("relation_candidate" not in row.get("qualifiers", {}) for row in segment_rows),
            "segment already has a relation classification")
    require(not any(row.get("candidate_id") in {item["candidate_id"] for item in NEW_CANDIDATES}
                    for row in candidate_rows), "new candidate ID already exists")
    require(not any(row.get("mention_id") == "m-chp3-seciv-l106-116-0044" for row in mention_rows),
            "new mention ID already exists")
    require(not any(row.get("statement_id") == item["statement_id"]
                    for row in statement_rows for item in NEW_STATEMENTS),
            "new statement ID already exists")

    candidates_by_id = {row["candidate_id"]: row for row in candidate_rows}
    statements_by_id = {row["statement_id"]: row for row in segment_rows}
    noviziato = next((row for row in mention_rows
                      if row.get("mention_id") == "m-chp3-seciv-l106-116-0042"), None)
    require(noviziato is not None and noviziato.get("candidate_id") == "cand-5080"
            and noviziato.get("surface_form") == "Noviziato"
            and noviziato.get("start_char") == "3049"
            and noviziato.get("end_char") == "3058", "Noviziato mention changed")
    require("cand-11617" not in candidates_by_id and "cand-11618" not in candidates_by_id,
            "new candidate IDs already exist")

    for statement_id, note in RELATION_NOTES.items():
        require(statement_id in statements_by_id or
                statement_id in {row["statement_id"] for row in NEW_STATEMENTS},
                f"relation note has no statement: {statement_id}")
    for statement_id, note in NONRELATION_NOTES.items():
        require(statement_id in statements_by_id, f"nonrelation has no statement: {statement_id}")

    for row in segment_rows:
        sid = row["statement_id"]
        q = row.setdefault("qualifiers", {})
        is_relation = sid in RELATION_NOTES
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = RELATION_NOTES[sid] if is_relation else NONRELATION_NOTES[sid]

    camillo_payment = statements_by_id["st-chp3-seciv-l106-116-camillo-left-1000-scudi"]
    camillo_payment["object_candidate_id"] = "cand-5309"

    camillo_payment["qualifiers"]["qualification"] = (
        "The 1663 visit is event context; the 1,000 scudi were left toward the ongoing rebuilding expense. "
        "The passage gives no modern currency conversion."
    )

    bernini_supervision = statements_by_id["st-chp3-seciv-l106-116-berni-supervised-workmen"]
    bernini_supervision["object_candidate_id"] = "cand-11618"

    bernini_supervision["qualifiers"]["qualification"] = (
        "The supervised group is the unnamed workmen engaged in the S. Andrea rebuilding; "
        "the source gives no membership or count."
    )

    virtual_patron = statements_by_id["st-chp3-seciv-l106-116-berni-virtual-patron-and-refused-payment"]
    virtual_patron["predicate"] = "served_as_virtual_patron_of_the_enterprise"
    virtual_patron["qualifiers"]["claim"] = (
        "Haskell describes Bernini as the virtual patron of the whole enterprise."
    )
    virtual_patron["qualifiers"]["qualification"] = (
        "This is Haskell's characterization of Bernini's role, not a formal appointment or ownership."
    )
    virtual_patron["original_quote"] = (
        "He was himself the virtual patron of the whole enterprise"
    )

    gaulli_payment = statements_by_id["st-chp3-seciv-l106-116-gaulli-payment-note-865-13"]
    gaulli_payment["subject_candidate_id"] = "cand-11617"
    gaulli_payment["object_candidate_id"] = "cand-1117"
    gaulli_payment["predicate"] = "reported_paid_100_scudi_from_novitiate_funds_to_gaulli"
    gaulli_payment["qualifiers"]["claim"] = (
        "Haskell's footnote quotes an archival entry reporting that Gaulli was paid 100 scudi "
        "from the Novitiate's own funds through Father Francesco Scaramuccia."
    )

    payment_start = segment_text.find("Thus Gaulli was paid")
    recovery_start = segment_text.find("con animo di rivalersene dal Signor", payment_start)
    require(payment_start >= 0 and recovery_start > payment_start, "payment quote anchors changed")
    gaulli_payment["original_quote"] = segment_text[payment_start:recovery_start].rstrip()

    noviziato["candidate_id"] = "cand-11617"
    noviziato["note"] = (
        "In the Italian payment quotation, this identifies the Novitiate as the reported source of funds, "
        "not the physical place candidate cand-5080. The cited archive has not been independently consulted."
    )

    workmen_start = segment_text.find("Workmen engaged on the most menial tasks")
    require(workmen_start == 566 and workmen_start + len("Workmen engaged on the most menial tasks") == 606,
            "workmen mention span changed")
    mention_rows.append({
        "mention_id": "m-chp3-seciv-l106-116-0044",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-11618",
        "surface_form": "Workmen engaged on the most menial tasks",
        "start_char": "566",
        "end_char": "606",
        "note": "Unidentified worker group directly supervised by Bernini on the S. Andrea rebuilding; membership and count are not stated.",
    })
    candidate_rows.extend(NEW_CANDIDATES)

    for row in NEW_STATEMENTS:
        if row["statement_id"] == "st-chp3-seciv-l106-116-berni-refused-all-payment":
            row["original_quote"] = "and refused all payment"
        else:
            recovery_start = segment_text.find("con animo di rivalersene dal Signor")
            prince_end = segment_text.find(" . . .", recovery_start)
            require(recovery_start >= 0 and prince_end > recovery_start, "recovery quote anchor changed")
            row["original_quote"] = segment_text[recovery_start:prince_end + 6]
        statement_rows.append(row)

    relation_ids = EXPECTED_IDS.intersection(RELATION_NOTES)
    require(len(relation_ids) == 24, "expected 24 existing relation candidates")
    require(sum(row["qualifiers"].get("relation_candidate") is True
                for row in statement_rows if row.get("segment_id") == SEGMENT_ID) == 26,
            "expected 26 segment relation candidates")
    require(sum(row["qualifiers"].get("relation_candidate") is False
                for row in statement_rows if row.get("segment_id") == SEGMENT_ID) == 7,
            "expected seven segment nonrelations")
    require(sum("relation_candidate" not in row.get("qualifiers", {})
                for row in statement_rows if row.get("segment_id") == SEGMENT_ID) == 0,
            "segment still has unclassified statements")

    candidates_by_id = {row["candidate_id"]: row for row in candidate_rows}
    reviewed_segment = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    for row in reviewed_segment:
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is True:
            subject_id, object_id = row.get("subject_candidate_id"), row.get("object_candidate_id")
            require(subject_id in candidates_by_id and object_id in candidates_by_id,
                    f"relation candidate has missing endpoint: {row['statement_id']}")
            require(candidates_by_id[subject_id].get("status") != "excluded"
                    and candidates_by_id[object_id].get("status") != "excluded",
                    f"relation candidate uses excluded endpoint: {row['statement_id']}")

    bilateral = sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
                    for row in statement_rows)
    bilateral_relations = sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
                              and row.get("qualifiers", {}).get("relation_candidate") is True
                              for row in statement_rows)
    bilateral_nonrelations = sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
                                 and row.get("qualifiers", {}).get("relation_candidate") is False
                                 for row in statement_rows)
    bilateral_unclassified = sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
                                 and "relation_candidate" not in row.get("qualifiers", {})
                                 for row in statement_rows)
    total_relations = sum(row.get("qualifiers", {}).get("relation_candidate") is True
                          for row in statement_rows)
    require(len(statement_rows) == 12809, "unexpected statement total")
    require(len(candidate_rows) == 11596, "unexpected candidate total")
    require(len(mention_rows) == 27531, "unexpected mention total")
    require((bilateral, bilateral_relations, bilateral_nonrelations, bilateral_unclassified)
            == (8608, 5080, 484, 3044), "unexpected bilateral classification totals")
    require(total_relations == 5132, "unexpected relation-candidate total")

    prepared = {
        STATEMENTS: encode_jsonl(statement_rows, "\n", STATEMENTS.read_bytes().startswith(b"\xef\xbb\xbf")),
        CANDIDATES: encode_csv(candidate_fields, candidate_rows, candidate_eol, candidate_bom),
        MENTIONS: encode_csv(mention_fields, mention_rows, mention_eol, mention_bom),
    }
    print("segment: 31 existing statements classified; 2 atomic statements added")
    print("classification: 26 relation candidates; 7 nonrelations; 0 unclassified")
    print("endpoint corrections: Camillo payment -> rebuilding project; Bernini supervision -> unnamed workmen")
    print("footnote 5: separate Novitiate-to-Gaulli payment and Scaramuccia-to-Prince recovery intention")
    print("candidates: 2 added; mentions: 1 added; no S6 relations written")
    print("post totals: statements=12809 candidates=11596 mentions=27531")
    print("bilateral: total=8608 relation=5080 nonrelation=484 unclassified=3044")
    if not args.apply:
        print("DRY-RUN PASS; no files written")
        return

    backup_paths = {
        STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX),
        CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + BACKUP_SUFFIX),
        MENTIONS: MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX),
    }
    require(all(not path.exists() for path in backup_paths.values()), "backup path already exists")
    for path, backup in backup_paths.items():
        shutil.copy2(path, backup)
    temps = []
    try:
        for path, data in prepared.items():
            temp = path.with_name(path.name + ".tmp-write")
            require(not temp.exists(), f"temporary path already exists: {temp.name}")
            temp.write_bytes(data)
            temps.append((temp, path))
        for temp, path in temps:
            os.replace(temp, path)
    finally:
        for temp, _ in temps:
            if temp.exists():
                temp.unlink()

    print("APPLY PASS")
    for path in [STATEMENTS, CANDIDATES, MENTIONS]:
        print(f"post_sha256 {path.name} {sha(path)}")
    print("recovery copies:")
    for backup in backup_paths.values():
        print(backup.name)


if __name__ == "__main__":
    main()
