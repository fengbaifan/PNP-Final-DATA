from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l165-177"
PREFIX = "st-chp3-seciv-l165-177-"
SOURCE_SHA = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA = "31d51a622ebe4435aba123bb7584365b46a72264ce8b84261771e0033a17f19e"
PRE_HASHES = {
    STATEMENTS.name: "6b20e7d0d50c5975c4c4754236ec25f61fecc515e2deb818fa7ec3e6e18cb8fb",
    CANDIDATES.name: "99e215d0845caf24804cd6354262cf6517d8d048d90c784c52929c52a6dc5224",
    MENTIONS.name: "0d449642eee336201b7632c5dbc7d590dcc0d432f54cd6127d512e5bd384acfb",
}
BACKUP_SUFFIX = ".bak-s2-chp3-seciv-l165-177-relations-20261011"
SOURCE_LINES: list[str] = []

EXPECTED_SUFFIXES = {
    "academy-authorities-less-enthusiastic",
    "altar-craftsmanship-and-complexity",
    "chapel-building-under-jesuit-control",
    "competition-caused-uproar-and-rivalry",
    "doctors-figures-scheme-abandoned",
    "drawings-models-exhibited-and-private-vote",
    "duke-refused-tribune-permission",
    "emperor-mediated-patronage-transfer",
    "jesuits-had-money-and-patronage-rights",
    "jesuits-resigned-to-left-transept",
    "legros-celebrated-by-french-students",
    "legros-dismissed-for-private_commissions",
    "legros-remained-in-rome-and-became-jesuit-sculptor",
    "legros-won-statue-competition",
    "letters-arrived-for-arrangements-father",
    "letters-carried-complaints-to-duke",
    "members-and-architects-preferred-tribune",
    "pozzo-given-charge-of-altar",
    "pozzo-plans-choice-did-not-calm-situation",
    "pozzo-selected-craftsmen-and-ran-sculptor-competitions",
    "pozzo-threatened-withdrawal-and-debates-continued",
    "site-officially-belonged-to-savelli",
    "subtle-basreliefs-described-across-page",
    "theodon-group-chosen-to-show-no-style-preference",
    "tirso-final-decision-may-1695",
}

CLASSIFICATIONS = {
    "academy-authorities-less-enthusiastic": (
        True,
        "Haskell directly reports the French Academy authorities' comparative response to Legros's selection; the authorities and their reasons remain unspecified.",
    ),
    "altar-craftsmanship-and-complexity": (
        False,
        "This is Haskell's aesthetic assessment of one altar, not an assertion between two entities.",
    ),
    "chapel-building-under-jesuit-control": (
        True,
        "Haskell reports the Jesuits' stated preference that construction of the St Ignatius chapel remain in their hands; this does not establish legal ownership.",
    ),
    "competition-caused-uproar-and-rivalry": (
        True,
        "The row is narrowed to the architects' and patrons' conduct in the altar competition; the statement that the competition caused an uproar is kept separately as a non-relational narrative claim.",
    ),
    "doctors-figures-scheme-abandoned": (
        True,
        "The two proposed figures belonged to the altar programme and the scheme was abandoned; the source does not identify who planned or cancelled them.",
    ),
    "drawings-models-exhibited-and-private-vote": (
        True,
        "The row is narrowed to the submitted drawings and models being exhibited at the Galleria Farnese; the artists' vote is recorded separately.",
    ),
    "duke-refused-tribune-permission": (
        True,
        "Haskell directly attributes refusal of permission for the tribune location to the Duke of Parma; his personal identity and the legal scope remain unresolved.",
    ),
    "emperor-mediated-patronage-transfer": (
        True,
        "Haskell says the unidentified Holy Roman Emperor mediated Prince Giulio's relinquishment of Savelli chapel patronage; the exchange is not an ownership transfer.",
    ),
    "jesuits-had-money-and-patronage-rights": (
        True,
        "Haskell attributes both the means and patronage rights for the planned altar to the Jesuits; neither fact proves the altar was completed.",
    ),
    "jesuits-resigned-to-left-transept": (
        True,
        "Haskell reports the Jesuits' reluctant acceptance of the left-transept location after the Duke refused the tribune.",
    ),
    "legros-celebrated-by-french-students": (
        True,
        "The source directly reports the French students' celebration of Legros; the group remains unidentified beyond this description.",
    ),
    "legros-dismissed-for-private_commissions": (
        True,
        "The French Academy dismissed Legros in connection with his acceptance of private commissions; the group he agreed to make and his pensioner status are recorded separately.",
    ),
    "legros-remained-in-rome-and-became-jesuit-sculptor": (
        True,
        "The row is narrowed to Legros becoming the Jesuits' principal sculptor; his remaining in Rome is recorded separately as a location relation.",
    ),
    "legros-won-statue-competition": (
        True,
        "Haskell says Pierre Legros won the competition for the planned statue of St Ignatius; the statue's ranking as the most important sculpture is recorded separately as an authorial assessment.",
    ),
    "letters-arrived-for-arrangements-father": (
        True,
        "Haskell says signed and anonymous letters reached the unnamed Jesuit father in charge; the letters, senders, dates, and archival identities are not individually identified.",
    ),
    "letters-carried-complaints-to-duke": (
        True,
        "Haskell says the Duke was told the allegations, but does not identify the informant or say that the earlier letters were the source; the subject endpoint is therefore left open.",
    ),
    "members-and-architects-preferred-tribune": (
        True,
        "Haskell reports a preference for the tribune among many Society members and consulted architects; the unnamed group is not asserted to be unanimous.",
    ),
    "pozzo-given-charge-of-altar": (
        True,
        "Haskell reports that Pozzo was placed in complete charge of the altar, but uses passive voice and does not identify the appointing agent; the subject endpoint is left open.",
    ),
    "pozzo-plans-choice-did-not-calm-situation": (
        True,
        "This preserves Haskell's attributed assessment that choosing Pozzo's altar plans did not improve the project situation.",
    ),
    "pozzo-selected-craftsmen-and-ran-sculptor-competitions": (
        True,
        "The row is narrowed to Pozzo selecting the craftsmen; his separate organization of sculptor competitions is recorded as another relation candidate.",
    ),
    "pozzo-threatened-withdrawal-and-debates-continued": (
        True,
        "The row is narrowed to Pozzo's threat to withdraw from the altar project; the debate topic and further architects consulted are recorded separately without inventing their agents.",
    ),
    "site-officially-belonged-to-savelli": (
        True,
        "Haskell says the chapel site officially belonged to the Savelli; the source does not specify the legal instrument or exact property scope.",
    ),
    "subtle-basreliefs-described-across-page": (
        True,
        "Haskell says the altar included bas-reliefs of Ignatius's life and miracles; the sentence continues at p.93 L180, where its contrast and visibility are completed.",
    ),
    "theodon-group-chosen-to-show-no-style-preference": (
        True,
        "The row is narrowed to the Jesuits choosing Théodon's group for the other side of the altar; Haskell's interpretation of style policy and comparison with Legros are recorded separately.",
    ),
    "tirso-final-decision-may-1695": (
        True,
        "The row is narrowed to Tirso Gonzalez's May 1695 decision concerning the altar; his prohibition of further criticism is recorded separately.",
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], bytes]:
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return rows, raw


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


def encode_jsonl_preserving_unchanged(rows: list[dict], raw: bytes) -> bytes:
    lines = raw.splitlines(keepends=True)
    current = {row["statement_id"]: row for row in rows}
    if len(current) != len(rows):
        raise SystemExit("duplicate statement IDs in prepared JSONL")
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    bom = raw.startswith(b"\xef\xbb\xbf")
    output: list[bytes] = []
    old_ids: set[str] = set()
    for index, line in enumerate(lines):
        if not line.strip():
            output.append(line)
            continue
        old = json.loads(line.decode("utf-8-sig"))
        sid = old["statement_id"]
        if sid in old_ids or sid not in current:
            raise SystemExit(f"duplicate or removed statement in prepared JSONL: {sid}")
        old_ids.add(sid)
        if old == current[sid]:
            output.append(line)
        else:
            encoded = (json.dumps(current[sid], ensure_ascii=False, separators=(",", ":")) + eol.decode("ascii")).encode("utf-8")
            if index == 0 and bom:
                encoded = b"\xef\xbb\xbf" + encoded
            output.append(encoded)
    new_ids = set(current) - old_ids
    if new_ids and output and not output[-1].endswith((b"\n", b"\r")):
        output.append(eol)
    for row in rows:
        if row["statement_id"] in new_ids:
            output.append((json.dumps(row, ensure_ascii=False, separators=(",", ":")) + eol.decode("ascii")).encode("utf-8"))
    return b"".join(output)


def quote_fragment(source_lines: list[str], line_start: int, line_end: int, phrase: str) -> str:
    excerpt = "\n".join(source_lines[line_start - 1 : line_end])
    pattern = r"\s+".join(re.escape(word) for word in phrase.split())
    match = re.search(pattern, excerpt, flags=re.IGNORECASE)
    if not match:
        raise SystemExit(f"quote phrase not found in S0 L{line_start}-{line_end}: {phrase!r}")
    return match.group(0)


def statement(
    suffix: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    line_start: int,
    line_end: int,
    phrase: str,
    claim: str,
    relation_candidate: bool,
    relation_note: str,
    qualification: str,
    *,
    speaker: str = "Haskell",
    text_layer: str = "authorial narrative",
    mentioned_candidate_ids: list[str] | None = None,
    extra: dict | None = None,
) -> dict:
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "print_page": 92,
        "pdf_physical_page": 34,
        "qualification": qualification,
        "relation_candidate": relation_candidate,
        "relation_candidate_note": relation_note,
    }
    if mentioned_candidate_ids:
        qualifiers["mentioned_candidate_ids"] = mentioned_candidate_ids
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": PREFIX + suffix,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote_fragment(SOURCE_LINES, line_start, line_end, phrase),
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and refine CHP-3 printed p.92 S2 statements.")
    parser.add_argument("--apply", action="store_true", help="write only after all reviewed preconditions pass")
    args = parser.parse_args()

    source_raw = SOURCE.read_bytes()
    if sha(source_raw) != SOURCE_SHA:
        raise SystemExit("source hash changed; re-review before applying")
    global SOURCE_LINES
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    SOURCE_LINES = source_lines
    if len(source_lines) != 243 or source_lines[164] != "[Page 92]":
        raise SystemExit("unexpected source structure or page marker")
    segment_rows, _ = read_jsonl(SEGMENTS)
    segment_meta = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment_meta) != 1 or segment_meta[0].get("sha256") != SEGMENT_SHA:
        raise SystemExit("normalized segment hash changed; re-review before applying")

    statement_rows, statement_raw = read_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_eol, candidate_bom, candidate_raw = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_eol, mention_bom, mention_raw = read_csv(MENTIONS)
    raw_by_name = {
        STATEMENTS.name: statement_raw,
        CANDIDATES.name: candidate_raw,
        MENTIONS.name: mention_raw,
    }
    for name, expected in PRE_HASHES.items():
        if sha(raw_by_name[name]) != expected:
            raise SystemExit(f"{name} changed since review; re-review before applying")

    segment_statements = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    found_suffixes = {
        row["statement_id"][len(PREFIX) :]
        for row in segment_statements
        if row["statement_id"].startswith(PREFIX)
    }
    if len(segment_statements) != 25 or found_suffixes != EXPECTED_SUFFIXES:
        raise SystemExit(f"unexpected p.92 statement scope: count={len(segment_statements)}, missing={sorted(EXPECTED_SUFFIXES-found_suffixes)}, extra={sorted(found_suffixes-EXPECTED_SUFFIXES)}")
    if any((row.get("qualifiers") or {}).get("relation_candidate") not in (None, True) for row in segment_statements):
        raise SystemExit("p.92 statement classifications changed; re-review before applying")
    coverage_rows = read_csv(TABLES / "s2-coverage.csv")[1]
    coverage = [row for row in coverage_rows if row.get("segment_id") == SEGMENT_ID]
    if len(coverage) != 1 or (coverage[0].get("disposition"), coverage[0].get("migration_status")) != ("reviewed", "complete"):
        raise SystemExit("p.92 coverage changed; do not modify the coverage ledger")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if len(candidate_by_id) != len(candidate_rows):
        raise SystemExit("duplicate candidate IDs")
    candidate_updates = {
        "cand-5427": {
            "canonical_name": "Unidentified Society members, architects, and patrons involved in the altar project",
            "suggested_type": "",
            "detail": "An unenumerated set of Society members, consulted architects, and patrons discussed across printed p.92. The passage does not provide membership or establish that all participants shared one view; no generic people-group type is assigned.",
        },
        "cand-5428": {
            "suggested_type": "",
            "detail": "Unidentified sculptors and artists participating in the altar competitions. Individuals named elsewhere in the passage remain separately represented; no generic people-group type is assigned.",
        },
        "cand-5430": {
            "suggested_type": "",
            "detail": "Unidentified crowds waiting at Casa Professa for the competition result; size and membership are not supplied, so no generic people-group type is assigned.",
        },
        "cand-5431": {
            "suggested_type": "",
            "detail": "Unidentified French students reported to have celebrated Legros; membership and institutional representation are not specified, so no generic people-group type is assigned.",
        },
        "cand-5438": {
            "suggested_type": "",
            "detail": "Unidentified craftsmen selected by Andrea Pozzo for the altar; names and individual roles are not supplied, so no generic people-group type is assigned.",
        },
    }
    if any(cid not in candidate_by_id for cid in candidate_updates):
        raise SystemExit("a p.92 candidate to revise is missing")
    natural_keys = {
        (row.get("canonical_name", "").casefold(), row.get("suggested_type", ""))
        for row in candidate_rows
        if row["candidate_id"] not in candidate_updates
    }
    for cid, update in candidate_updates.items():
        candidate_by_id[cid].update(update)
        key = (candidate_by_id[cid].get("canonical_name", "").casefold(), candidate_by_id[cid].get("suggested_type", ""))
        if key in natural_keys:
            raise SystemExit(f"candidate name/type collision after update: {cid} {key}")
        natural_keys.add(key)

    mention_additions: list[dict] = []
    group_phrase = "many members of the Society"
    full_segment = "\n".join(source_lines[164:177])
    group_start = full_segment.index(group_phrase)
    group_mention = {
        "mention_id": "m-chp3-seciv-l165-177-0064",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-5427",
        "surface_form": group_phrase,
        "start_char": str(group_start),
        "end_char": str(group_start + len(group_phrase)),
        "note": "Source names many members of the Society as a group with various consulted architects who considered the tribune most suitable; membership is not specified.",
    }
    existing_mention_ids = {row["mention_id"] for row in mention_rows}
    if group_mention["mention_id"] in existing_mention_ids:
        raise SystemExit("the planned p.92 group mention ID already exists")
    for row in mention_rows:
        if row.get("segment_id") == SEGMENT_ID and row.get("candidate_id") == "cand-5427" and (row.get("start_char"), row.get("end_char")) == (group_mention["start_char"], group_mention["end_char"]):
            raise SystemExit("the planned p.92 group mention span already exists")
    mention_additions.append(group_mention)

    updates_by_suffix = {suffix: (value, note) for suffix, (value, note) in CLASSIFICATIONS.items()}
    updates_by_suffix["chapel-building-under-jesuit-control"] = (
        True,
        CLASSIFICATIONS["chapel-building-under-jesuit-control"][1],
    )
    row_by_suffix = {row["statement_id"][len(PREFIX) :]: row for row in segment_statements}
    for suffix, (is_relation, note) in updates_by_suffix.items():
        row = row_by_suffix[suffix]
        qualifiers = row.setdefault("qualifiers", {})
        qualifiers["relation_candidate"] = is_relation
        qualifiers["relation_candidate_note"] = note

    edits = {
        "competition-caused-uproar-and-rivalry": {
            "qualifiers.claim": "Haskell says architects and their patrons jockeyed for position, slandered rivals, and intrigued in the context of the altar competition.",
            "predicate": "participants_jockeyed_and_intrigued_in_competition",
            "object_candidate_id": "cand-5427",
        },
        "drawings-models-exhibited-and-private-vote": {
            "qualifiers.claim": "Haskell says the drawings and models submitted for the altar competition were exhibited in the Galleria Farnese.",
            "predicate": "exhibited_at",
            "subject_candidate_id": "cand-5429",
            "object_candidate_id": "cand-5423",
        },
        "doctors-figures-scheme-abandoned": {
            "qualifiers.claim": "Haskell says two further figures of Doctors of the Church were planned for the altar programme and the scheme was abandoned as unsuitable.",
            "subject_candidate_id": "cand-5420",
            "predicate": "planned_figures_abandoned_as_unsuitable_to_pay_court_to_saint",
        },
        "emperor-mediated-patronage-transfer": {
            "qualifiers.claim": "Haskell says the Holy Roman Emperor mediated Prince Giulio's relinquishment of Savelli chapel patronage in exchange for special references to Cardinal Savelli's beneficence.",
        },
        "letters-carried-complaints-to-duke": {
            "qualifiers.claim": "Haskell says the Duke of Parma was told allegations that the church was being wrecked, white marble was being rubbed with egg yolk to appear yellow, and the organisation was a 'confusion of babel'.",
            "subject_candidate_id": None,
            "predicate": "duke_informed_of_reported_allegations",
            "qualifiers.speaker": "Haskell relaying an unidentified informant's report",
            "qualifiers.text_layer": "reported allegations",
            "qualifiers.qualification": "The source does not identify who informed the Duke and does not say the earlier signed and anonymous letters were the source of these allegations; the source endpoint remains open.",
            "qualifiers.mentioned_candidate_ids": ["cand-4905", "cand-5200"],
        },
        "members-and-architects-preferred-tribune": {
            "qualifiers.claim": "Haskell says many Society members and consulted architects considered the tribune the most suitable position, as Oliva had.",
            "subject_candidate_id": "cand-5427",
            "object_candidate_id": "cand-5000",
        },
        "pozzo-given-charge-of-altar": {
            "subject_candidate_id": None,
            "object_candidate_id": "cand-2034",
            "predicate": "placed_in_complete_charge_of_altar",
            "qualifiers.qualification": "The sentence uses passive voice and does not identify who placed Pozzo in charge; retain an open source endpoint.",
            "qualifiers.mentioned_candidate_ids": ["cand-2034", "cand-5420"],
        },
        "pozzo-plans-choice-did-not-calm-situation": {
            "qualifiers.claim": "Haskell says the inevitable choice of Pozzo's altar plans did nothing to improve the project situation.",
            "object_candidate_id": "cand-5421",
        },
        "pozzo-selected-craftsmen-and-ran-sculptor-competitions": {
            "qualifiers.claim": "Haskell says Pozzo chose the craftsmen for the altar project.",
            "predicate": "selected_craftsmen_for_altar",
            "object_candidate_id": "cand-5438",
        },
        "pozzo-threatened-withdrawal-and-debates-continued": {
            "qualifiers.claim": "Haskell says Pozzo threatened to withdraw from the altar project.",
            "predicate": "threatened_to_withdraw_from_project",
            "object_candidate_id": "cand-5420",
        },
        "tirso-final-decision-may-1695": {
            "qualifiers.claim": "Haskell says Tirso Gonzalez made his irrevocable decision concerning the altar in May 1695 after much hesitation.",
            "object_candidate_id": "cand-5420",
        },
        "legros-won-statue-competition": {
            "qualifiers.claim": "Haskell says Pierre Legros won the competition for the planned statue of St Ignatius.",
            "predicate": "won_competition_for",
            "subject_candidate_id": "cand-1379",
            "object_candidate_id": "cand-5426",
        },
        "legros-remained-in-rome-and-became-jesuit-sculptor": {
            "qualifiers.claim": "Haskell says Legros became the Jesuits' principal sculptor.",
            "predicate": "became_principal_sculptor_for",
            "subject_candidate_id": "cand-1379",
            "object_candidate_id": "cand-3403",
        },
        "theodon-group-chosen-to-show-no-style-preference": {
            "qualifiers.claim": "Haskell says the Jesuits chose Théodon's group Faith crushing Idolatry for the other side of the altar.",
            "predicate": "chosen_for_other_side_of_altar",
            "object_candidate_id": "cand-5434",
        },
    }
    for suffix, changes in edits.items():
        row = row_by_suffix[suffix]
        for key, value in changes.items():
            if key.startswith("qualifiers."):
                row.setdefault("qualifiers", {})[key.split(".", 1)[1]] = value
            else:
                row[key] = value

    # The p.92 sentence opened on p.91 and the last one closes on p.93 L180.
    row_by_suffix["subtle-basreliefs-described-across-page"].setdefault("qualifiers", {}).update(
        {"continuation_to_segment_id": "chp-3:03_CHP-3_sec_iv:l179-187", "continuation_to_source_line": 180}
    )

    new_statements = [
        statement("savelli-family-head-of-giulio", "cand-2376", "cand-5417", "head_of_family", 166, 167,
                  "Prince Giulio, the head of the family", "Haskell identifies Prince Giulio as head of the Savelli family.", True,
                  "The passage directly calls Prince Giulio head of the family; preserve the source attribution and do not infer a wider genealogy.",
                  "The sentence names the family only through the surrounding Savelli reference.", mentioned_candidate_ids=["cand-2376", "cand-5417"]),
        statement("cardinal-savelli-ancestor-of-giulio", "cand-2375", "cand-2376", "ancestor_of", 166, 167,
                  "his ancestor, the Cardinal", "Haskell identifies Cardinal Savelli as an ancestor of Prince Giulio.", True,
                  "The source gives a general ancestor relation and does not specify the exact degree of kinship.",
                  "Cardinal Savelli is identified by title and the Savelli context; no further kinship degree is supplied.", mentioned_candidate_ids=["cand-2375", "cand-2376"]),
        statement("savelli-family-relinquished-chapel-patronage", "cand-5417", "cand-5236", "relinquished_patronage_of", 166, 167,
                  "Prince Giulio, the head of the family, to give up its patronage", "Haskell says Prince Giulio, as head of the Savelli family, gave up the family's patronage of the St Ignatius chapel.", True,
                  "The source concerns patronage of the chapel, not ownership of the site or fabric.",
                  "The text attributes the action to Prince Giulio as head of the Savelli family.", mentioned_candidate_ids=["cand-2376", "cand-5417", "cand-5236"]),
        statement("special-references-to-cardinal-savelli", None, "cand-2375", "commemorative_reference_to", 166, 167,
                  "special references to the beneficence of his ancestor, the Cardinal", "Haskell says the patronage concession was exchanged for special references to Cardinal Savelli's beneficence.", True,
                  "The source does not identify who would make the references or exactly where they would appear; keep the subject endpoint open.",
                  "The source explicitly identifies Cardinal Savelli as the object of the references but leaves their agent and placement unstated.", speaker="Haskell", mentioned_candidate_ids=["cand-2375", "cand-5417"]),
        statement("competition-caused-uproar", "cand-5421", None, "caused_uproar", 170, 170,
                  "A competition was organised and caused an uproar", "Haskell says the altar competition caused an uproar.", False,
                  "This is a reported effect of the competition without a second entity endpoint; participant conduct is recorded in the related group statement.",
                  "The wording is Haskell's characterization of the competition.", mentioned_candidate_ids=["cand-5421"]),
        statement("devotional-medium-debate", None, "cand-5437", "debated_devotional_effect_of_media", 171, 171,
                  "endless debates as to whether a statue or a picture inspired greater devotion", "Haskell says the devotional effect of a statue versus a picture remained under debate.", False,
                  "The debate participants are not identified; this is retained as a narrative claim rather than an entity relation.",
                  "The source gives neither the debaters nor a particular statue or picture.", text_layer="authorial narrative", mentioned_candidate_ids=["cand-5437"]),
        statement("more-architects-consulted", None, "cand-5427", "consulted_about_altar_project", 171, 171,
                  "more architects were consulted", "Haskell says further architects were consulted about the altar project.", True,
                  "The source uses passive voice and does not identify the person or group doing the consultation; keep that endpoint open.",
                  "The passage identifies the consulted architects only as a plural group.", mentioned_candidate_ids=["cand-5427"]),
        statement("tirso-forbade-further-criticism", "cand-1213", "cand-5420", "forbade_further_criticism_of", 171, 171,
                  "forbade any further criticisms", "Haskell says Tirso Gonzalez forbade further criticism of the altar project after his May 1695 decision.", True,
                  "The source does not enumerate the critics or criticisms; retain the project as the bounded object.",
                  "The preceding sentence identifies Tirso Gonzalez as the General who made the decision.", mentioned_candidate_ids=["cand-1213", "cand-5420"]),
        statement("pozzo-organized-sculptor-competitions", "cand-2034", "cand-5421", "organized_competition_for", 172, 172,
                  "organised competitions for the sculptors", "Haskell says Andrea Pozzo organised competitions for sculptors working on the altar programme.", True,
                  "The number and complete list of sculptors and competitions are not supplied.",
                  "The pronoun 'He' refers to Andrea Pozzo in the preceding sentence.", mentioned_candidate_ids=["cand-2034", "cand-5421", "cand-5428"]),
        statement("artists-voted-on-submitted-designs", "cand-5428", "cand-5429", "voted_on_submitted_designs", 172, 172,
                  "They were then asked to vote, in private, for the one they thought the best, excluding their own", "Haskell says the invited artists voted privately for the best submitted design while excluding their own.", True,
                  "The source describes a voting procedure but does not identify the selected design or enumerate voters and submissions.",
                  "'They' refers to the artists invited to attend the exhibition.", text_layer="authorial narrative", mentioned_candidate_ids=["cand-5428", "cand-5429"]),
        statement("statue-most-important-sculpture", None, "cand-5426", "authorial_importance_assessment", 172, 173,
                  "The most important piece of sculpture was, naturally, the statue of St Ignatius", "Haskell describes the statue of St Ignatius as the most important piece of sculpture in the altar programme.", False,
                  "This is Haskell's evaluative description of one work, not a relation between two entities.",
                  "The source's 'naturally' marks the author's evaluation.", text_layer="authorial evaluation", mentioned_candidate_ids=["cand-5426"]),
        statement("legros-agreed-to-make-marble-group", "cand-1379", "cand-5433", "agreed_to_make", 173, 174,
                  "agreed to make a large marble group of Religion triumphing over Heresy", "Haskell says Pierre Legros agreed to make the marble group Religion triumphing over Heresy for one side of the altar.", True,
                  "The source reports agreement to make the group, not its completion or present location.",
                  "The group is the private commission that precedes the Academy's dismissal of Legros.", mentioned_candidate_ids=["cand-1379", "cand-5433"]),
        statement("legros-pensioner-of-king-france", "cand-1379", "cand-5432", "pensioner_of", 173, 174,
                  "status as a pensioner of the King of France", "Haskell describes Legros as a pensioner of the King of France.", True,
                  "The King is identified by office only; do not infer a personal identity from the date.",
                  "This statement records the status invoked in the Academy's action, not the source of Legros's pension.", mentioned_candidate_ids=["cand-1379", "cand-5432"]),
        statement("legros-remained-in-rome", "cand-1379", "cand-4490", "remained_in", 174, 174,
                  "remained in Rome", "Haskell says Legros remained in Rome after the Academy dismissed him.", True,
                  "The source reports his location and does not specify a residence or uninterrupted duration.",
                  "The source links his remaining in Rome with the subsequent account of his Jesuit role.", mentioned_candidate_ids=["cand-1379", "cand-4490"]),
        statement("jesuits-style-policy-interpretation", "cand-3403", None, "authorial_interpretation_of_style_policy", 175, 175,
                  "they were in no way concerned to promote one particular style", "Haskell interprets the Jesuits' selection as suggesting that they did not promote one particular style.", False,
                  "This is explicitly framed as Haskell's interpretation ('as if to show') and has no separately bounded second entity.",
                  "Preserve the inferential wording rather than treating the Jesuits' intent as independently established.", text_layer="authorial interpretation", mentioned_candidate_ids=["cand-3403"]),
        statement("theodon-group-contrasted-with-legros-group", "cand-5434", "cand-5433", "contrasted_with", 175, 175,
                  "heavily classical lumpiness was a total contrast to Legros", "Haskell says Théodon's group's heavily classical style contrasted with Legros's dramatic Baroque vigour.", True,
                  "The comparison is Haskell's stylistic assessment of the two sculptural groups; it does not imply different completion states.",
                  "The source compares the selected Théodon group directly with Legros's group.", text_layer="authorial evaluation", mentioned_candidate_ids=["cand-5434", "cand-5433"]),
    ]

    existing_ids = {row["statement_id"] for row in statement_rows}
    new_ids = [row["statement_id"] for row in new_statements]
    if len(set(new_ids)) != len(new_ids) or existing_ids.intersection(new_ids):
        raise SystemExit("a planned p.92 statement ID already exists or is duplicated")
    valid_candidate_ids = set(candidate_by_id)
    for row in [*segment_statements, *new_statements]:
        for field in ("subject_candidate_id", "object_candidate_id"):
            value = row.get(field)
            if value is not None and value not in valid_candidate_ids:
                raise SystemExit(f"unknown {field} in {row['statement_id']}: {value}")
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") not in (True, False):
            raise SystemExit(f"unclassified p.92 statement: {row['statement_id']}")
        start, end = q.get("source_line_start"), q.get("source_line_end")
        quote = row.get("original_quote", "")
        if not (166 <= start <= end <= 177) or quote not in "\n".join(source_lines[start - 1 : end]):
            raise SystemExit(f"invalid p.92 source quote/range: {row['statement_id']}")
    for row in new_statements:
        if not (166 <= row["qualifiers"]["source_line_start"] <= row["qualifiers"]["source_line_end"] <= 177):
            raise SystemExit(f"new statement outside p.92 body: {row['statement_id']}")

    segment_mentions = [row for row in mention_rows if row.get("segment_id") == SEGMENT_ID]
    for row in [*segment_mentions, *mention_additions]:
        start, end = int(row["start_char"]), int(row["end_char"])
        if full_segment[start:end] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']} {row['surface_form']!r}")
        if row["candidate_id"] not in valid_candidate_ids:
            raise SystemExit(f"unknown mention candidate: {row['mention_id']}")

    # Preserve the p.92-to-p.93 continuation at the first printed word, not the page marker.
    target_row = row_by_suffix["subtle-basreliefs-described-across-page"]
    if target_row["qualifiers"].get("continuation_to_source_line") != 180:
        raise SystemExit("p.92 continuation target must be p.93 L180")

    prepared_statements = [*statement_rows, *new_statements]
    prepared_candidates = list(candidate_by_id.values())
    prepared_mentions = [*mention_rows, *mention_additions]
    statement_bytes = encode_jsonl_preserving_unchanged(prepared_statements, statement_raw)
    candidate_bytes = encode_csv(candidate_fields, prepared_candidates, candidate_eol, candidate_bom)
    mention_bytes = encode_csv(mention_fields, prepared_mentions, mention_eol, mention_bom)
    post_counts = {
        "statements": len(prepared_statements),
        "candidates": len(prepared_candidates),
        "mentions": len(prepared_mentions),
        "p92_statements": len(segment_statements) + len(new_statements),
        "p92_relation_true": sum(row["qualifiers"]["relation_candidate"] is True for row in [*segment_statements, *new_statements]),
        "p92_relation_false": sum(row["qualifiers"]["relation_candidate"] is False for row in [*segment_statements, *new_statements]),
        "p92_open_relations": sum(
            row["qualifiers"]["relation_candidate"] is True and (row.get("subject_candidate_id") is None or row.get("object_candidate_id") is None)
            for row in [*segment_statements, *new_statements]
        ),
    }
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "segment": SEGMENT_ID,
        "print_page": 92,
        "pdf_physical_page": 34,
        "classification_updates": len(CLASSIFICATIONS),
        "new_statements": [row["statement_id"] for row in new_statements],
        "candidate_updates": {cid: {"canonical_name": update.get("canonical_name"), "suggested_type": update["suggested_type"]} for cid, update in candidate_updates.items()},
        "new_mentions": mention_additions,
        "counts_after": post_counts,
        "coverage_unchanged": {"disposition": coverage[0]["disposition"], "migration_status": coverage[0]["migration_status"]},
        "continuation_to": f"chp-3:03_CHP-3_sec_iv:l179-187#L180",
        "source_image_review": ["physical p.34 confirms Monsù", "physical p.34 confirms Théodon", "leading OCR dashes at L175 are not printed text"],
        "post_hashes": {
            STATEMENTS.name: sha(statement_bytes),
            CANDIDATES.name: sha(candidate_bytes),
            MENTIONS.name: sha(mention_bytes),
        },
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    changes = {
        STATEMENTS: statement_bytes,
        CANDIDATES: candidate_bytes,
        MENTIONS: mention_bytes,
    }
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in changes}
    for backup in backups.values():
        if backup.exists():
            raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup}")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    for path, data in changes.items():
        path.write_bytes(data)
    for path, expected in ((STATEMENTS, sha(statement_bytes)), (CANDIDATES, sha(candidate_bytes)), (MENTIONS, sha(mention_bytes))):
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"post-write hash mismatch: {path}")
    print(json.dumps({"write": "complete", "recovery_copies": [str(path) for path in backups.values()]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
