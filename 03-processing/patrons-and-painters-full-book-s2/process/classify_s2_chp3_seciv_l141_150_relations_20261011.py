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
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l141-150"
PREFIX = "st-chp3-seciv-l141-150-"
SOURCE_SHA = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA = "5e18c21b46bf5b681a69942d515c6c08d18fea2d6ad07c2f78ae3e6bd5cc1e7c"
PRE_HASHES = {
    STATEMENTS.name: "7187003acb624903cacdd10e46a9d964c5cce1a9b506be1b6093b34773dec34b",
    CANDIDATES.name: "b32ddc4aa22601c189c6ba40944afa6030033124b559e09d68d2dd54e2fe09a0",
    MENTIONS.name: "19d291df8437d40ece8a5ed0a91a8b132db0d7ca7df0e25342a0f663459c550a",
    COVERAGE.name: "e9c4b793d40f00d6d5cb0952413aae2e7c55787a5a820bfe9dcc27e9159b66cc",
}
BACKUP_SUFFIX = ".bak-s2-chp3-seciv-l141-150-relations-20261011"

RELATION_NOTES = {
    "ceiling-as-jesuit-missionary-celebration": "Haskell explicitly describes the vault ceiling as a celebration of the Jesuit missionaries; the OCR wording remains as transcribed in S0.",
    "cycle-compared-with-gaulli": "The comparison continues the p.89 sentence. Haskell compares Pozzo's tribune and apse frescoes with Gaulli's Gesù frescoes; the earlier work is not narrowed to a single named fresco.",
    "cycle-reaction-against-baroque": "This is Haskell's qualified art-historical interpretation ('in some ways'), not a neutral classification.",
    "dome-reputation-led-to-vault-idea": "The quoted biographer explicitly says the dome painting's reputation gave rise to the vault project; footnote 2's Baldinucci citation chain is recorded, while the Francesco/Filippo identity discrepancy remains unresolved.",
    "fathers-agreed-to-employ-pozzo": "The quoted biographer says the Jesuit fathers agreed to employ Pozzo; this records agreement, not a dated contract or completed commission.",
    "fathers-consulted-rome-artists": "The quoted biographer says the Jesuit fathers consulted unnamed painters and architects in Rome before undertaking the project.",
    "fresco-based-on-luke-words": "Haskell attributes the quoted saying to Christ as reported by St Luke and says the fresco was based on it; the source passage is not independently aligned to a verse or version.",
    "jesuits-welcomed-different-work": "Haskell explicitly says the Jesuits accepted and welcomed Pozzo's work; the reasons he proposes remain alternatives in a linked statement.",
    "painted-four-pendentive-scenes": "Haskell explicitly attributes the four named pendentive scenes to Pozzo; no additional scenes or completion details are inferred.",
    "pozzo-adapted-reference-to-ignatius": "Haskell says Pozzo adapted the reference from the Church to St Ignatius; the rhetorical question about the saint's encouragement of disciples is recorded separately.",
    "pozzo-avoided-doctor-subjects": "Haskell says Pozzo wished to avoid the Doctors of the Church as customary pendentive subjects; this records intention, not a claim about every prior pendentive.",
    "pozzo-avoided-evangelist-subjects": "Haskell says Pozzo wished to avoid the Evangelists as customary pendentive subjects; this records intention, not a claim about every prior pendentive.",
    "pozzo-began-vault-undertaking-in-1688": "Haskell dates the beginning of Pozzo's undertaking to 1688; this does not say the fresco was completed then.",
    "pozzo-called-stucco-kitchen-suitable": "Haskell attributes the quoted critical comparison of the stucco to Pozzo; it is a reported comment, not an objective assessment.",
    "pozzo-described-ray-from-jesus-through-ignatius": "Pozzo's quoted explanation describes the fresco as depicting Jesus sending a ray to Ignatius; the subsequent transmission by Ignatius is recorded separately.",
    "pozzo-described-ray-to-name-shield": "Pozzo's quoted explanation says a second ray strikes a shield bearing the Name of Jesus; this is reported iconographic meaning.",
    "pozzo-destroyed-stucco-decoration": "The biographical quotation says Pozzo destroyed the previous stucco decoration; no date or surviving trace is inferred.",
    "pozzo-explained-fresco-meaning": "Haskell reports that Pozzo later explained the fresco's meaning at length and cites Tietze; the cited discussion is not independently consulted here.",
    "pozzo-explained-honour-to-ignatius": "Pozzo's quoted explanation interprets the fresco as honouring Ignatius for the glory of the Redeemer's name; this is the artist's reported interpretation.",
    "roman-populace-butchers-joke": "Haskell reports a joke circulating among the Roman populace about four butchers; no speaker is named and this is not treated as population-wide opinion.",
    "scenes-intended-against-heresy": "Haskell describes the pendentive scenes as designed to illustrate zeal against heresy; this preserves his account of intended meaning.",
    "stucco-removal-required-for-vault-fresco": "Haskell calls removal of the stucco inevitable if the vault was to be painted; this is the author's stated condition for the project.",
    "vault-previously-decorated-with-stucco": "Haskell explicitly says the vault had previously been decorated with stucco; no maker or date is supplied.",
}

NONRELATION_NOTES = {
    "cycle-full-figures-rigid-framework": "This is a one-work formal description and evaluation, not an entity-to-entity relation.",
    "opposition-and-jesuit-abandonment-fears": "After splitting off the project's abandonment consideration, this row records the Jesuits' reported fear of public affront as a collective state, with no second entity endpoint.",
}

QUOTE_SPECS = {
    "ceiling-as-jesuit-missionary-celebration": (150, 150, "avast celebration of the Jesuit missionaries"),
    "cycle-compared-with-gaulli": (142, 142, "Gaulli’s frescoes in the Gesù: they lack both the theological complexity and the emotional power of the earlier work."),
    "cycle-full-figures-rigid-framework": (143, 143, "Every figure is displayed to the full and the whole composition is given rigidity by a bold architectural framework."),
    "cycle-reaction-against-baroque": (142, 143, "In some ways they mark a reaction against the\nBaroque."),
    "dome-reputation-led-to-vault-idea": (147, 147, "because of the extraordinary reputation acquired through this painting [the dome], not only by Padre Andrea, the artist, but also by the Society, which commissioned it, that the idea was born of painting the entire vault of the same church of S. Ignazio"),
    "fathers-agreed-to-employ-pozzo": (147, 147, "the reverend fathers were agreed to employ Padre Pozzo"),
    "fathers-consulted-rome-artists": (147, 147, "they moved with considerable caution before undertaking it, so as to consult the famous painters and architects of Rome."),
    "fresco-based-on-luke-words": (149, 149, "T am come to send fire on the earth: but what will I, if it be already kindled?’"),
    "jesuits-welcomed-different-work": (143, 144, "That a work so immeasurably different in feeling and style from The Adoration os the Lamb was accepted and welcomed by the\nJesuits"),
    "opposition-and-jesuit-abandonment-fears": (147, 147, "the Jesuits were frightened of going about for fear of receiving some public affront"),
    "painted-four-pendentive-scenes": (145, 145, "he painted Judith with the head of Holofernes, David with the head of Goliath, Jael hammering a nail into Sisera, and Samson killing a thousand with a jawbone."),
    "pozzo-adapted-reference-to-ignatius": (149, 149, "Adapting this reference from the Church to St Ignatius himself"),
    "pozzo-avoided-doctor-subjects": (145, 145, "On the pendentives Pozzo wished to avoid the subjects usual for this position—the Evangelists and the Doctors of the Church—and to choose something different."),
    "pozzo-avoided-evangelist-subjects": (145, 145, "On the pendentives Pozzo wished to avoid the subjects usual for this position—the Evangelists and the Doctors of the Church—and to choose something different."),
    "pozzo-began-vault-undertaking-in-1688": (147, 147, "in 1688 Pozzo began his colossal undertaking (Plate 15)"),
    "pozzo-called-stucco-kitchen-suitable": (147, 147, "more suitable for a kitchen than for a church"),
    "pozzo-described-ray-from-jesus-through-ignatius": (150, 150, "I have painted the figure of Jesus, who sends forth a ray of fight to the heart of Ignatius"),
    "pozzo-described-ray-to-name-shield": (150, 150, "From the breast of the Redeemer there emerges another ray which strikes a shield, on which is painted the Name of Jesus, the crown of light."),
    "pozzo-destroyed-stucco-decoration": (147, 147, "the artist ruthlessly destroyed"),
    "pozzo-explained-fresco-meaning": (148, 148, "In later years the artist himself explained the meaning of his fresco at great length."),
    "pozzo-explained-honour-to-ignatius": (150, 150, "the Redeemer, having as his purpose the glory of His name, wishes to honour Ignatius"),
    "roman-populace-butchers-joke": (145, 146, "the Roman populace was less reverent, and the word went around that:\n‘anyone who wants to buy good meat should go to S. Ignazio, as four new butchers have just opened there!’"),
    "scenes-intended-against-heresy": (145, 145, "Though designed to illustrate the zeal with which heresy must always be thwarted"),
    "stucco-removal-required-for-vault-fresco": (147, 147, "For this step, inevitable, of course, if he was to paint the vault"),
    "vault-previously-decorated-with-stucco": (147, 147, "The vault had previously been decorated with stucco work"),
}

NEW_CANDIDATE = {
    "candidate_id": "cand-11623",
    "index_entry_id": "",
    "canonical_name": "Saying about sending fire on earth attributed to Christ and reported by St Luke",
    "index_page_range": "",
    "suggested_type": "archive",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": "Source-bounded candidate for the saying quoted on printed p.90 as Christ's words reported by St Luke. The exact biblical verse, version, and textual transmission are not independently verified; preserve the book's OCR wording.",
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT_ID}#L149",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], bytes]:
    raw = path.read_bytes()
    records = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return records, raw


def read_csv(path: Path) -> tuple[list[str], list[dict], str, bool, bytes]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), eol, bom, raw


def encode_csv(fields: list[str], rows: list[dict], eol: str, bom: bool) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="raise", lineterminator=eol)
    writer.writeheader()
    writer.writerows(rows)
    return (("\ufeff" if bom else "") + output.getvalue()).encode("utf-8")


def encode_jsonl_preserving_unchanged(records: list[dict], raw: bytes) -> bytes:
    raw_lines = raw.splitlines(keepends=True)
    current_by_id = {row["statement_id"]: row for row in records}
    if len(current_by_id) != len(records):
        raise SystemExit("duplicate statement IDs in prepared JSONL")
    eol = "\r\n" if b"\r\n" in raw else "\n"
    bom = raw.startswith(b"\xef\xbb\xbf")
    output: list[bytes] = []
    original_ids: set[str] = set()
    for line_index, line in enumerate(raw_lines):
        if not line.strip():
            output.append(line)
            continue
        original = json.loads(line.decode("utf-8-sig"))
        statement_id = original["statement_id"]
        if statement_id in original_ids:
            raise SystemExit(f"duplicate statement ID in source JSONL: {statement_id}")
        original_ids.add(statement_id)
        record = current_by_id.get(statement_id)
        if record is None:
            raise SystemExit(f"existing statement was removed: {statement_id}")
        if original == record:
            output.append(line)
        else:
            encoded = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + eol).encode("utf-8")
            if line_index == 0 and bom:
                encoded = b"\xef\xbb\xbf" + encoded
            output.append(encoded)
    new_ids = set(current_by_id) - original_ids
    if new_ids and output and not output[-1].endswith((b"\n", b"\r")):
        output.append(eol.encode("ascii"))
    for record in records:
        if record["statement_id"] not in new_ids:
            continue
        line = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + eol).encode("utf-8")
        if not original_ids and not output and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line)
    return b"".join(output)


def exact_quote(source_lines: list[str], start: int, end: int, needle: str) -> str:
    excerpt = "\n".join(source_lines[start - 1 : end])
    if needle not in excerpt:
        raise SystemExit(f"quote does not match S0 lines L{start}-{end}: {needle!r}")
    return needle


def make_statement(
    suffix: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    quote: str,
    line_start: int,
    line_end: int,
    claim: str,
    qualification: str,
    relation_candidate: bool,
    relation_note: str,
    speaker: str = "Haskell",
    text_layer: str = "authorial narrative",
) -> dict:
    return {
        "statement_id": PREFIX + suffix,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "print_page": 90,
            "pdf_physical_page": 32,
            "qualification": qualification,
            "relation_candidate": relation_candidate,
            "relation_candidate_note": relation_note,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify CHP-3 printed p.90 S2 statements and split compound claims.")
    parser.add_argument("--apply", action="store_true", help="write only after dry-run preconditions and checks pass")
    args = parser.parse_args()

    source_raw = SOURCE.read_bytes()
    if sha(source_raw) != SOURCE_SHA:
        raise SystemExit("source file hash changed; re-review before applying")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[140:150])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("normalized p.90 segment hash changed; re-review before applying")
    segment_rows, _ = read_jsonl(SEGMENTS)
    segment = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment) != 1 or segment[0].get("sha256") != SEGMENT_SHA:
        raise SystemExit("segment inventory does not match the reviewed source")

    statement_rows, statement_raw = read_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_eol, candidate_bom, _ = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_eol, mention_bom, _ = read_csv(MENTIONS)
    coverage_fields, coverage_rows, coverage_eol, coverage_bom, _ = read_csv(COVERAGE)
    for path in (STATEMENTS, CANDIDATES, MENTIONS, COVERAGE):
        if sha(path.read_bytes()) != PRE_HASHES[path.name]:
            raise SystemExit(f"unexpected {path.name} hash; data changed since this review")

    segment_statements = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    expected_suffixes = set(RELATION_NOTES) | set(NONRELATION_NOTES)
    found_suffixes = {row["statement_id"][len(PREFIX):] for row in segment_statements if row["statement_id"].startswith(PREFIX)}
    if len(segment_statements) != 25 or found_suffixes != expected_suffixes:
        raise SystemExit(f"unexpected segment rows: count={len(segment_statements)}, missing={sorted(expected_suffixes-found_suffixes)}, extra={sorted(found_suffixes-expected_suffixes)}")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in segment_statements):
        raise SystemExit("segment already has a classification; do not reapply")
    coverage = [row for row in coverage_rows if row.get("segment_id") == SEGMENT_ID]
    if len(coverage) != 1 or (coverage[0].get("disposition"), coverage[0].get("migration_status")) != ("reviewed", "complete"):
        raise SystemExit("coverage state changed; preserve and re-review before applying")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if len(candidate_by_id) != len(candidate_rows) or "cand-11623" in candidate_by_id:
        raise SystemExit("candidate IDs changed or proposed candidate already exists")
    mention_ids = {row["mention_id"] for row in mention_rows}
    if len(mention_ids) != len(mention_rows) or "m-chp3-seciv-l141-150-0064" in mention_ids:
        raise SystemExit("mention IDs changed or proposed mention already exists")
    natural_keys = {(row.get("canonical_name", ""), row.get("suggested_type", "")) for row in candidate_rows}
    new_candidate_key = (NEW_CANDIDATE["canonical_name"], NEW_CANDIDATE["suggested_type"])
    if new_candidate_key in natural_keys:
        raise SystemExit("proposed source candidate duplicates an existing natural key")

    all_statement_ids = {row["statement_id"] for row in statement_rows}
    if len(all_statement_ids) != len(statement_rows):
        raise SystemExit("duplicate statement IDs in source table")

    row_by_suffix = {row["statement_id"][len(PREFIX):]: row for row in segment_statements}
    for suffix, note in RELATION_NOTES.items():
        row = row_by_suffix[suffix]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
    for suffix, note in NONRELATION_NOTES.items():
        row = row_by_suffix[suffix]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note

    for suffix, (start, end, needle) in QUOTE_SPECS.items():
        row_by_suffix[suffix]["original_quote"] = exact_quote(source_lines, start, end, needle)

    comparison = row_by_suffix["cycle-compared-with-gaulli"]["qualifiers"]
    comparison["linked_body_statement_ids"] = [
        "st-chp3-seciv-l130-139-cycle-culminates-in-la-storta-promise"
    ]

    dome = row_by_suffix["dome-reputation-led-to-vault-idea"]
    dome["qualifiers"]["qualification"] = (
        "The quotation inserts ‘[the dome]’ after ‘this painting’, distinguishing the earlier dome device from the vault fresco. "
        "Footnote 2 reads ‘Baldinucci MS. cit.’ and points through p.89 n.3 to p.88 n.5, which names Francesco Baldinucci and the Vita del Padre Pozzo manuscript. "
        "The manuscript was not consulted; the index separately lists Filippo Baldinucci, so the biographer's identity remains unresolved."
    )
    scripture = row_by_suffix["fresco-based-on-luke-words"]
    scripture["object_candidate_id"] = "cand-11623"
    scripture["qualifiers"]["qualification"] = (
        "This records Haskell's attribution of the saying to Christ through St Luke. The quoted source, verse, and version are not independently verified; "
        "S0's ‘T am’ OCR is preserved and the scan correction is recorded only in the S2 note."
    )
    scripture["qualifiers"]["mentioned_candidate_ids"] = ["cand-4910", "cand-3564", "cand-11623"]
    fear = row_by_suffix["opposition-and-jesuit-abandonment-fears"]
    fear["object_candidate_id"] = None
    fear["predicate"] = "jesuits_feared_public_affront_after_pozzo_was_attacked"
    fear["qualifiers"]["claim"] = "The biographical quotation says the Jesuits feared receiving a public affront after Pozzo was attacked for removing the stucco."
    fear["qualifiers"]["qualification"] = "The fear is a collective state reported by the biographer; the attackers are unnamed. Consideration of abandoning the vault project is recorded separately."
    rays = row_by_suffix["pozzo-described-ray-from-jesus-through-ignatius"]
    rays["predicate"] = "depicted_jesus_sending_ray_to_ignatius"
    rays["qualifiers"]["claim"] = "In Pozzo's quoted explanation, the vault fresco depicts Jesus sending a ray to Ignatius's heart."
    rays["qualifiers"]["qualification"] = "This records the artist's reported iconographic interpretation, not a historical event; Ignatius's transmission of the ray is stated separately."
    adaptation = row_by_suffix["pozzo-adapted-reference-to-ignatius"]
    adaptation["qualifiers"]["claim"] = "Haskell says Pozzo adapted the Church-directed reference to St Ignatius."
    welcomed = row_by_suffix["jesuits-welcomed-different-work"]
    welcomed["qualifiers"]["claim"] = "Haskell says the Jesuits accepted and welcomed Pozzo's work despite its difference in feeling and style from The Adoration of the Lamb."
    candidate_by_id["cand-5388"]["detail"] = (
        "Haskell attributes the p.90 quotation to Pozzo's biographer. Footnote 2 cites ‘Baldinucci MS. cit.’ and points through p.89 n.3 to p.88 n.5, "
        "which names Francesco Baldinucci, Vita del Padre Pozzo (Cod. Palat. 565, fols. 120–142). The manuscript was not consulted. The book index separately lists "
        "Filippo Baldinucci; the biographer's identity remains unresolved, so these persons are not merged."
    )

    coverage[0]["note"] += (
        " Printed p.90 scan checked: OCR ‘os’/print ‘of’ in The Adoration of the Lamb, ‘T am’/‘I am’, ‘avast’/‘a vast’, ‘fight’/‘light’, and ‘thevault’/‘the vault’; "
        "S0 remains unchanged. This batch classifies the segment's relation claims and separates compound statements."
    )

    quote_text = exact_quote(
        source_lines, 149, 149,
        "T am come to send fire on the earth: but what will I, if it be already kindled?",
    )
    mention_start = segment_text.index(quote_text)
    new_mention = {
        "mention_id": "m-chp3-seciv-l141-150-0064",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-11623",
        "surface_form": quote_text,
        "start_char": str(mention_start),
        "end_char": str(mention_start + len(quote_text)),
        "note": "Exact S0 OCR quotation attributed by Haskell to Christ as reported by St Luke; the printed scan reads ‘I am’, but S0 is unchanged and the exact biblical verse/version remains unverified.",
    }
    if quote_text not in segment_text or not (0 <= mention_start < mention_start + len(quote_text) <= len(segment_text)):
        raise SystemExit("new scriptural quotation mention span is invalid")

    new_rows = [
        make_statement(
            "jesuit-taste-alternative-explanations", "cand-3403", None,
            "haskell_offered_alternative_explanations_for_jesuit_taste",
            exact_quote(source_lines, 144, 145, "either that their taste had changed out of all recognition in the last few\n, years, or that this taste was sufficiently catholic to include anything grandiose without too much concern for its style"),
            143, 145,
            "Haskell offers two alternatives for why the Jesuits welcomed the work: their taste may have changed, or it may have been broad enough to include grandiose work regardless of style.",
            "This is Haskell's either-or interpretation of Jesuit taste, not a resolved fact about the Society's motives.",
            False,
            "The passage gives competing explanations and no separate entity-to-entity relation.",
        ),
        make_statement(
            "pozzo-attacked-for-stucco-removal", "cand-2034", None,
            "pozzo_was_attacked_for_removing_vault_stucco",
            exact_quote(source_lines, 147, 147, "he was so bitterly attacked"),
            147, 147,
            "The biographical quotation says Pozzo was bitterly attacked for removing the stucco as a necessary step before painting the vault.",
            "The attackers are not identified; this is recorded as a one-sided report and not a relation to an invented group.",
            False,
            "The source identifies Pozzo as the target but gives no candidate endpoint for the unnamed attackers.",
            speaker="Unidentified biographer of Andrea Pozzo, quoted by Haskell",
            text_layer="biographical quotation reported by Haskell",
        ),
        make_statement(
            "jesuits-considered-abandoning-vault-project", "cand-3403", "cand-5074",
            "considered_abandoning_vault_fresco_project",
            exact_quote(source_lines, 147, 147, "They considered, therefore, abandoning the work and leaving the vault as it was."),
            147, 147,
            "The biographical quotation says the Jesuits considered abandoning the vault project and leaving the vault as it was.",
            "The next sentence says it was already too late; the consideration is not treated as an accomplished abandonment.",
            True,
            "The quotation explicitly relates the Jesuits' reported decision to the vault project, while preserving intention rather than completed action.",
            speaker="Unidentified biographer of Andrea Pozzo, quoted by Haskell",
            text_layer="biographical quotation reported by Haskell",
        ),
        make_statement(
            "ignatius-encouraged-disciples-rhetorical-question", "cand-1309", "cand-5393",
            "reported_ignatius_exhortation_to_disciples",
            exact_quote(source_lines, 149, 149, "had not the saint often encouraged his disciples with the words ‘Go and set everything aflame’?"),
            149, 149,
            "Haskell rhetorically asks whether St Ignatius often encouraged his disciples with the words ‘Go and set everything aflame’.",
            "The relation is recorded as Haskell's rhetorical question within Pozzo's reported interpretation, not as independently verified wording or frequency.",
            True,
            "The sentence explicitly associates St Ignatius with his unnamed disciples as recipients of the reported exhortation.",
            text_layer="authorial rhetorical question in account of the artist's explanation",
        ),
        make_statement(
            "fresco-depicts-ignatius-transmitting-ray", "cand-5074", "cand-1309",
            "depicts_ignatius_receiving_and_transmitting_ray",
            exact_quote(source_lines, 150, 150, "a ray of fight to the heart of Ignatius, which is then transmitted by him to the most distant hearts of the four parts of the world"),
            150, 150,
            "In Pozzo's quoted explanation, the vault fresco depicts the ray reaching Ignatius's heart and being transmitted by him to distant hearts across the four parts of the world.",
            "This is the artist's reported iconographic explanation, not a historical transmission of a physical ray; the scan reads ‘light’ while S0 reads ‘fight’.",
            True,
            "The quoted interpretation explicitly depicts Ignatius receiving and transmitting the ray; the claim remains attributed to Pozzo through Haskell.",
            speaker="Pozzo, quoted by Haskell",
            text_layer="artist's reported iconographic explanation",
        ),
    ]

    existing_new_ids = {row["statement_id"] for row in new_rows}
    if existing_new_ids & all_statement_ids or len(existing_new_ids) != 5:
        raise SystemExit("new statement IDs collide or are not unique")
    statement_rows.extend(new_rows)
    candidate_rows.append(NEW_CANDIDATE)
    mention_rows.append(new_mention)

    for row in statement_rows:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_by_id and endpoint != "cand-11623":
                raise SystemExit(f"missing candidate endpoint {endpoint} in {row['statement_id']}")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is None for row in statement_rows if row.get("segment_id") == SEGMENT_ID):
        raise SystemExit("segment still has an unclassified statement")
    segment_after = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment_after) != 30:
        raise SystemExit(f"unexpected segment statement count: {len(segment_after)}")
    segment_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in segment_after)
    segment_nonrelations = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in segment_after)
    bilateral = [row for row in statement_rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    bilateral_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral)
    bilateral_nonrelations = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral)
    bilateral_unclassified = len(bilateral) - bilateral_relations - bilateral_nonrelations
    total_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statement_rows)
    open_relations = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
        for row in statement_rows
    )
    if (len(statement_rows), len(candidate_rows), len(mention_rows)) != (12828, 11601, 27536):
        raise SystemExit("unexpected post-write row counts")
    if (segment_relations, segment_nonrelations) != (26, 4):
        raise SystemExit(f"unexpected segment classification totals: {segment_relations}/{segment_nonrelations}")
    if (len(bilateral), bilateral_relations, bilateral_nonrelations, bilateral_unclassified, total_relations, open_relations) != (8618, 5166, 490, 2962, 5218, 52):
        raise SystemExit("unexpected global relation classification totals")

    prepared = {
        STATEMENTS: encode_jsonl_preserving_unchanged(statement_rows, statement_raw),
        CANDIDATES: encode_csv(candidate_fields, candidate_rows, candidate_eol, candidate_bom),
        MENTIONS: encode_csv(mention_fields, mention_rows, mention_eol, mention_bom),
        COVERAGE: encode_csv(coverage_fields, coverage_rows, coverage_eol, coverage_bom),
    }
    print("source and normalized segment hashes match the reviewed CHP-3 p.90 passage")
    print("reviewed 25 existing statements, classified the segment at 26 relation candidates and 4 one-sided/nonrelation records")
    print("split the compounded Jesuit fear/abandonment statement and added five atomic statements")
    print("added one open scriptural-source candidate and one exact quote mention; preserved the Francesco/Filippo identity conflict")
    print(f"post totals: statements={len(statement_rows)} candidates={len(candidate_rows)} mentions={len(mention_rows)}")
    print(f"bilateral statements: {len(bilateral)}; relation={bilateral_relations}; nonrelation={bilateral_nonrelations}; unclassified={bilateral_unclassified}")
    print(f"relation candidates total={total_relations}; open endpoints={open_relations}")
    print("JSONL serializer preserves all unchanged rows and blank lines byte-for-byte")
    if not args.apply:
        print("DRY-RUN PASS; no files written")
        return

    backup_paths = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in prepared}
    if any(path.exists() for path in backup_paths.values()):
        raise SystemExit("a recovery copy already exists; refusing to overwrite")
    for path, backup in backup_paths.items():
        shutil.copy2(path, backup)
    temps: list[tuple[Path, Path]] = []
    try:
        for path, data in prepared.items():
            temp = path.with_name(path.name + ".tmp-write")
            if temp.exists():
                raise SystemExit(f"temporary output already exists: {temp.name}")
            temp.write_bytes(data)
            temps.append((temp, path))
        for temp, path in temps:
            os.replace(temp, path)
        for path, data in prepared.items():
            if path.read_bytes() != data:
                raise SystemExit(f"post-write byte check failed: {path.name}")
    except Exception:
        for temp, _ in temps:
            if temp.exists():
                temp.unlink()
        for path, backup in backup_paths.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    print("APPLY PASS")
    for path in prepared:
        print(f"post_sha256 {path.name} {sha(path.read_bytes())}")
    print("recovery copies:")
    for backup in backup_paths.values():
        print(backup.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
