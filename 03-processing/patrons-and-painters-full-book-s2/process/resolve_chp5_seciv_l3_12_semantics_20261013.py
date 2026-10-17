from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEGMENT_ID = "chp-5:05_CHP-5_sec_iv:l3-12"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_iv.md"
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"

EXPECTED = {
    SOURCE_FILE: "805df7b2bdc296cf987069cb0cea829bc07ec8932e28b075e9575f0c2ac67c4f",
    "04-knowledge/tables/book-statements.jsonl": "35abcafaca15914e43189a697217950216108ec7ebbf1760e3568767e843441e",
    "04-knowledge/tables/mentions.csv": "e9efe57dad19046726d81c1a956a0d43fef5f2115f9080abb23bfdce54f04335",
}
EXPECTED_SEGMENT_SHA = "de2379de13fdefc90d3a2678b3e07fc8883697634f51bca4a89c61ddfd82c9c7"
BACKUP_SUFFIX = ".bak-s2-chp5-seciv-l3-12-20261013"


CLASSIFICATIONS = {
    "st-chp5-p142-academy-quarrels-would-not-deter-cardinal": (
        True,
        "The sentence presents a counterfactual patronage relation: Rosa's Academy quarrels would not have deterred an unnamed authoritative cardinal. It is not evidence of an actual commission.",
        "The cardinal and commission are hypothetical and unnamed; retain the counterfactual as an open relation candidate, not an actual patronage edge.",
    ),
    "st-chp5-p142-bamboccianti-pursued-rosa": (
        True,
        "Haskell explicitly characterizes the Bamboccianti as pursuing Rosa; preserve this broad attributed relation without inventing particular acts or members.",
        None,
    ),
    "st-chp5-p142-cerquozzi-and-rosa-considered-rivals": (
        True,
        "The passage explicitly reports that Cerquozzi and Rosa were considered rival landscape painters; Haskell's evaluation of this as an insult remains attributed to him.",
        None,
    ),
    "st-chp5-p142-cerquozzi-died-march-1660": (
        False,
        "This records Cerquozzi's death and its month, an event/date statement rather than a relation between entity endpoints.",
        None,
    ),
    "st-chp5-p142-cerquozzi-fashionable-after-rosa-return-1649": (
        True,
        "Haskell reports Rosa's perception of Cerquozzi's relative fashionability on Rosa's return to Rome; this is not an independently measured popularity comparison.",
        None,
    ),
    "st-chp5-p142-corsini-family-admired-cerquozzi": (
        True,
        "The passage names the Corsini family among Cerquozzi's keenest admirers in Florence; the family remains a collective endpoint.",
        None,
    ),
    "st-chp5-p142-other-painters-got-commission-opportunities": (
        False,
        "This is Haskell's evaluative comparison with unnamed painters and does not identify a pairwise relation suitable for an entity edge.",
        None,
    ),
    "st-chp5-p142-roman-connoisseurs-shaped-rosa-landscape-output": (
        True,
        "Haskell directly attributes Rosa's adherence to small romantic landscapes to the influence of Roman connoisseurs; retain his evaluative language and the group's unspecified membership.",
        None,
    ),
    "st-chp5-p142-rosa-at-center-of-florentine-society": (
        True,
        "The statement describes Rosa's position within an unidentified Florentine social circle. Florence is the setting, not the social-group endpoint.",
        "The society is not separately identified or typed in this passage; Florence is recorded as setting only, so the relation endpoint remains open.",
    ),
    "st-chp5-p142-rosa-bitter-quarrels-with-academy": (
        True,
        "Haskell explicitly reports bitter quarrels between Rosa and the Accademia di S. Luca; no date or particular dispute is supplied.",
        None,
    ),
    "st-chp5-p142-rosa-bought-vanlaer-copy-for-ricciardi": (
        True,
        "Haskell reports Rosa's purchase of an unidentified copy after Van Laer to gratify his closest friend; this supports acquisition by Rosa and does not establish transfer of ownership to Ricciardi.",
        None,
    ),
    "st-chp5-p142-rosa-career-bedevilled-by-bamboccianti": (
        True,
        "This is an explicit, attributed account connecting Rosa's career with the Bamboccianti's triumph. 'Confused with' and 'bedevilled by' remain Haskell's characterization, not a separately verified causal mechanism.",
        None,
    ),
    "st-chp5-p142-rosa-did-not-succeed-in-ambition": (
        False,
        "This reports the outcome of Rosa's ambition without identifying a second entity or a realized relationship.",
        None,
    ),
    "st-chp5-p142-rosa-imagined-himself-as-poussin": (
        False,
        "Haskell describes Rosa's imagined self-comparison with Poussin, not a historical relation or interaction between the two artists.",
        None,
    ),
    "st-chp5-p142-rosa-landscapes-and-battles-as-client-driven-compromise": (
        True,
        "Rosa's reported self-conception explicitly links his landscape and battle production to pressure from clients; the clients are unnamed and the account remains attributed.",
        "The clients are an unnamed collective; no particular patron, commission, or work is identified.",
    ),
    "st-chp5-p142-rosa-launched-attack-after-cerquozzi-fashion": (
        False,
        "This records Haskell's account of Rosa launching an attack after a change in fashionability; the target is not specified in this sentence and the later satire statement preserves its stated target.",
        None,
    ),
    "st-chp5-p142-rosa-leaves-rome-and-settles-in-florence": (
        True,
        "The passage reports Rosa's departure from Rome and settlement in Florence. The separately recorded Bernini-hostility statement preserves the qualified cause; 'partly' is not expanded to a sole cause.",
        None,
    ),
    "st-chp5-p142-rosa-satire-targeted-patrons": (
        True,
        "Haskell explicitly says Rosa's bitterness was directed toward the patrons of the artist and followers under discussion; the embedded quotation is mediated through Haskell.",
        "The patrons are an unidentified collective. The nearby wording links 'their' to the artist and followers; no individual patron is named.",
    ),
    "st-chp5-p142-rosa-self-conception-as-moral-history-painter": (
        False,
        "This records Rosa's reported self-description as a painter of moral histories, an attribute rather than a relation between entities.",
        None,
    ),
    "st-chp5-p142-rosa-sought-but-failed-public-commission": (
        True,
        "The passage explicitly reports Rosa's desire and failure to obtain a great public commission. Preserve this as an unrealized, open relation candidate; do not infer a commissioning patron or completed work.",
        "No commissioning person, institution, or particular work is identified; the commission is desired but not realized.",
    ),
    "st-chp5-p142-rosa-wished-for-hypothetical-patrons-for-histories": (
        True,
        "Haskell reports Rosa's wish for a patron like Cassiano dal Pozzo or Camillo Massimi to support his perceived talent; the two named men are alternatives, not actual patrons in this account.",
        "The passage presents Cassiano and Camillo as alternatives and states a wish, not actual patronage; preserve the modality and do not create an S6 patronage edge.",
    ),
    "st-chp5-p142-salviati-family-admired-cerquozzi": (
        True,
        "The passage names the Salviati family among Cerquozzi's keenest admirers in Florence; the family remains a collective endpoint.",
        None,
    ),
    "st-chp5-p142-shaftesbury-compared-rosa-and-poussin": (
        True,
        "Haskell reports Shaftesbury's comparison of Rosa and Poussin as 'honest moral men'; this is a reception/comparison relation, not evidence that the two artists were friends.",
        None,
    ),
    "st-chp5-p142-shaftesbury-hearsay-rosa-poussin-friends": (
        True,
        "Haskell reports Shaftesbury's second-hand account from unnamed old virtuosos and painters that Rosa and Poussin were friends; preserve both levels of attribution.",
        None,
    ),
    "st-chp5-p142-simonelli-early-patron-and-vanlaer-interest": (
        True,
        "The sentence reports Simonelli as one of Rosa's early patrons and separately says he showed interest in Van Laer; the new atomic statement captures the latter relation.",
        None,
    ),
}


ADDED_STATEMENTS = [
    {
        "statement_id": "st-chp5-p142-simonelli-interested-in-van-laer",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2434",
        "object_candidate_id": "cand-1351",
        "predicate": "interested_in",
        "qualifiers": {
            "source_line_start": 4,
            "source_line_end": 5,
            "printed_page": "142",
            "pdf_physical_page": 27,
            "claim": "Haskell says Simonelli also showed an interest in Pieter van Laer.",
            "speaker": "Haskell",
            "text_layer": "authorial narration",
            "qualification": "No particular Van Laer work, transaction, or patronage relation is specified.",
            "mentioned_candidate_ids": ["cand-2236", "cand-2434", "cand-1351"],
            "relation_candidate": True,
            "relation_candidate_note": "The sentence directly reports Simonelli's interest in Van Laer; it does not establish a transaction, ownership, or patronage relationship.",
        },
        "original_quote": "who also showed an interest in\nPieter van Laer.",
        "origin": "book",
        "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp5-p142-rosa-ricciardi-friendship",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2236",
        "object_candidate_id": "cand-2187",
        "predicate": "friend_of",
        "qualifiers": {
            "source_line_start": 8,
            "source_line_end": 9,
            "printed_page": "142",
            "pdf_physical_page": 27,
            "claim": "Haskell describes Giambattista Ricciardi as Rosa's closest friend in the account of Rosa buying a Van Laer copy to gratify him.",
            "speaker": "Haskell",
            "text_layer": "authorial narration",
            "qualification": "This is Haskell's characterization of their friendship; it does not state that Rosa transferred ownership of the copy to Ricciardi.",
            "mentioned_candidate_ids": ["cand-2236", "cand-2187"],
            "relation_candidate": True,
            "relation_candidate_note": "The phrase explicitly identifies Ricciardi as Rosa's closest friend.",
        },
        "original_quote": "his closest friend\nGiambattista Ricciardi.",
        "origin": "book",
        "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp5-p142-bernini-hostility-partly-drove-rosa-from-rome",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0307",
        "object_candidate_id": "cand-2236",
        "predicate": "reported_hostility_toward",
        "qualifiers": {
            "source_line_start": 5,
            "source_line_end": 6,
            "printed_page": "142",
            "pdf_physical_page": 27,
            "claim": "Haskell attributes part of Rosa's being driven from Rome to Bernini's hostility toward him.",
            "speaker": "Haskell",
            "text_layer": "authorial narration",
            "qualification": "The source says 'partly'; it does not make Bernini's hostility the sole cause.",
            "place_candidate_id": "cand-4490",
            "mentioned_candidate_ids": ["cand-0307", "cand-2236", "cand-4490"],
            "relation_candidate": True,
            "relation_candidate_note": "The passage explicitly attributes part of Rosa's departure from Rome to Bernini's hostility; preserve the reported, partial causal scope.",
        },
        "original_quote": "partly through the hostility of the\n' all powerful Bernini",
        "origin": "book",
        "source_file": SOURCE_FILE,
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    text = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(text)


def read_csv(path: Path) -> tuple[list[str], list[dict], bool]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader), bom


def write_csv(path: Path, fieldnames: list[str], rows: list[dict], bom: bool) -> None:
    with path.open("w", encoding="utf-8-sig" if bom else "utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prepare() -> tuple[list[dict], list[dict], list[str], bool]:
    for relative, expected in EXPECTED.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise SystemExit(f"guard failed: {relative} SHA-256 {actual} != expected {expected}")

    segment = next((row for row in read_jsonl(SEGMENTS) if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_SHA or segment.get("source_file") != SOURCE_FILE:
        raise SystemExit("guard failed: target segment fingerprint or source path changed")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("guard failed: duplicate statement IDs exist")
    target_ids = {row["statement_id"] for row in statements if row.get("segment_id") == SEGMENT_ID}
    if target_ids != set(CLASSIFICATIONS):
        raise SystemExit(f"guard failed: target statement IDs differ; expected={len(CLASSIFICATIONS)} actual={len(target_ids)}")
    if any(row.get("qualifiers", {}).get("relation_candidate") is not None for row in statements if row.get("statement_id") in target_ids):
        raise SystemExit("guard failed: one or more target statements have already been classified")
    if any(row["statement_id"] in by_id for row in ADDED_STATEMENTS):
        raise SystemExit("guard failed: one or more added statement IDs already exist")

    fieldnames, mentions, bom = read_csv(MENTIONS)
    bad_mention = [row for row in mentions if row.get("mention_id") == "m-s2-surface-ac909e179ccd8dfc"]
    if len(bad_mention) != 1 or bad_mention[0].get("candidate_id") != "cand-2244" or bad_mention[0].get("surface_form") != "In Florence":
        raise SystemExit("guard failed: expected Florence mention mapping has changed")
    return statements, mentions, fieldnames, bom


def apply_changes(statements: list[dict], mentions: list[dict]) -> tuple[int, int]:
    changed = 0
    for row in statements:
        statement_id = row["statement_id"]
        if statement_id not in CLASSIFICATIONS:
            continue
        relation, note, open_reason = CLASSIFICATIONS[statement_id]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        if open_reason:
            q["open_endpoint_reason"] = open_reason
        else:
            q.pop("open_endpoint_reason", None)
        changed += 1

    # The object is the unnamed social circle; Florence is only the setting.
    at_center = next(row for row in statements if row["statement_id"] == "st-chp5-p142-rosa-at-center-of-florentine-society")
    at_center["object_candidate_id"] = None
    at_center["qualifiers"]["place_candidate_id"] = "cand-3397"

    # Keep the already-cited early patronage statement atomic; the next clause gets its own row below.
    simonelli = next(row for row in statements if row["statement_id"] == "st-chp5-p142-simonelli-early-patron-and-vanlaer-interest")
    citation_keys = (
        "footnote_marker",
        "footnote_target_line",
        "footnote_link_status",
        "citation_segment_id",
        "citation_source_line_start",
        "citation_source_line_end",
        "footnote_refs",
    )
    simonelli_citation = {key: copy.deepcopy(simonelli["qualifiers"][key]) for key in citation_keys if key in simonelli["qualifiers"]}
    purchase = next(row for row in statements if row["statement_id"] == "st-chp5-p142-rosa-bought-vanlaer-copy-for-ricciardi")
    friendship_citation = {key: copy.deepcopy(purchase["qualifiers"][key]) for key in citation_keys if key in purchase["qualifiers"]}
    simonelli["predicate"] = "patronized_by"
    simonelli["qualifiers"]["claim"] = "On Rosa's arrival in Rome in 1637, one of his first patrons was the amateur dealer Simonelli."
    simonelli["qualifiers"]["mentioned_candidate_ids"] = ["cand-2236", "cand-2434"]
    simonelli["qualifiers"].pop("artist_candidate_id", None)
    simonelli["qualifiers"].pop("footnote_relation_note", None)
    simonelli["original_quote"] = "On his arrival in Rome in 1637 one of his first patrons had been the amateur dealer Niccol�� Simonelli"

    ADDED_STATEMENTS[0]["qualifiers"].update(simonelli_citation)
    ADDED_STATEMENTS[0]["qualifiers"]["footnote_relation_note"] = "Marker 1 follows the Van Laer clause; note 1 contextualizes Simonelli's relation to Rosa but does not directly prove this separate interest claim."
    ADDED_STATEMENTS[1]["qualifiers"].update(friendship_citation)
    ADDED_STATEMENTS[1]["qualifiers"]["footnote_relation_note"] = "Note 4 cites a letter from Rosa to Ricciardi, but the letter was not independently consulted and is not independent confirmation of their friendship."

    statements.extend(ADDED_STATEMENTS)

    changed_mentions = 0
    for row in mentions:
        if row.get("mention_id") == "m-s2-surface-ac909e179ccd8dfc":
            row["candidate_id"] = "cand-3397"
            row["note"] = "city; setting of the sentence"
            changed_mentions += 1
    return changed, changed_mentions


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve S2 semantics for Chapter 5 section iv, lines 3-12.")
    parser.add_argument("--apply", action="store_true", help="write guarded changes; default prints preview only")
    args = parser.parse_args()

    statements, mentions, mention_fields, mentions_bom = prepare()
    changed_statements, changed_mentions = apply_changes(statements, mentions)
    if changed_statements != len(CLASSIFICATIONS) or changed_mentions != 1:
        raise SystemExit("guard failed: unexpected change count")

    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    result_counts = {"true": 0, "false": 0, "unset": 0}
    for row in target_rows:
        value = row.get("qualifiers", {}).get("relation_candidate")
        result_counts["true" if value is True else "false" if value is False else "unset"] += 1
    if result_counts != {"true": 22, "false": 6, "unset": 0}:
        raise SystemExit(f"guard failed: unexpected target classification counts {result_counts}")

    if not args.apply:
        print("PREVIEW only; no table writes")
        print(f"classified existing statements: {changed_statements}")
        print(f"new atomic statements: {len(ADDED_STATEMENTS)}")
        print(f"final segment statements: {len(target_rows)}; relation candidates={result_counts['true']}; nonrelations={result_counts['false']}; unset={result_counts['unset']}")
        print("corrected mention: m-s2-surface-ac909e179ccd8dfc -> cand-3397 (Florence)")
        for row in ADDED_STATEMENTS:
            print(f"added | {row['statement_id']} | {row['subject_candidate_id']} -> {row['predicate']} -> {row['object_candidate_id']} | {row['qualifiers']['claim']}")
        return

    for relative in ("04-knowledge/tables/book-statements.jsonl", "04-knowledge/tables/mentions.csv"):
        path = ROOT / relative
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"guard failed: backup already exists: {backup.name}")
        shutil.copy2(path, backup)

    write_jsonl(STATEMENTS, statements)
    write_csv(MENTIONS, mention_fields, mentions, mentions_bom)
    print("applied guarded S2 classification and mention correction")
    print(f"backups: {STATEMENTS.name + BACKUP_SUFFIX}, {MENTIONS.name + BACKUP_SUFFIX}")
    print(f"classified existing statements: {changed_statements}")
    print(f"new atomic statements: {len(ADDED_STATEMENTS)}")
    print(f"final segment statements: {len(target_rows)}; relation candidates={result_counts['true']}; nonrelations={result_counts['false']}; unset={result_counts['unset']}")
    print(f"corrected mention: m-s2-surface-ac909e179ccd8dfc -> cand-3397 (Florence)")


if __name__ == "__main__":
    main()
