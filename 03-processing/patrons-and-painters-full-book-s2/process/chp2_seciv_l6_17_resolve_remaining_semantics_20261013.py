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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l6-17"
SEGMENT_SHA = "438d479ced460d329f80c12d875c4bee2672944f6017cdc0e7c78b19820af78c"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l6-17-semantics-20261013"
EXPECTED = {
    "book-statements.jsonl": "d694e2347b3aa0bdb019f5a3021a5a1147faa76d1fbfcb9f1a30865465ab389a",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "4d994ac4a126aa5b1b40ab134750827ee6252c3f9adf1ba52876128f9c67d7c2",
}
UNSET_IDS = {
    "st-chp2-seciv-l6-17-cassiano-patron-assessment",
    "st-chp2-seciv-l6-17-competition-and-committee-fragment",
    "st-chp2-seciv-l6-17-decision-and-collecting-assessment",
    "st-chp2-seciv-l6-17-francesco-armistice-instruction",
    "st-chp2-seciv-l6-17-francesco-status-assessment",
    "st-chp2-seciv-l6-17-madrid-mission-failure",
    "st-chp2-seciv-l6-17-party-courtesy-reception",
    "st-chp2-seciv-l6-17-tapestries-depict-constantine",
    "st-chp2-seciv-l6-17-wealth-used-for-learning",
}
NEW_COMMITTEE_ID = "st-chp2-seciv-l6-17-committee-correspondence-and-list-preparation"
NEW_COLLECTION_ASSESSMENT_ID = "st-chp2-seciv-l6-17-collection-begins-well-assessment"
COMPETITION_QUOTE = (
    "All over Italy, but especially in Florence and Rome, artists and their protectors were competing with each other "
    "for the great opportunities that now arose."
)
DECISION_QUOTE = "It must have been a difficult decision for him—too difficult, indeed, to last for long"
COLLECTION_QUOTE = "His art collecting had certainly begun well."
COMMITTEE_QUOTE = "The committee was being bombarded with letters; lists were being drawn"
PRIOR_PARIS_OUTCOME = "st-chp2-seciv-l6-17-paris-mission-outcome"
COMMITTEE_CONTINUATION = "st-chp2-seciv-l19-29-committee-lists-amended"
FOOTNOTE_THREE = "st-chp2-seciv-l190-245-citation-03"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve remaining S2 claims and split two compound statements in CHP-2 section IV, L6-17."
    )
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected print-p.44 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected unset statement set: {sorted(unset)}")
    if NEW_COMMITTEE_ID in statement_by_id or NEW_COLLECTION_ASSESSMENT_ID in statement_by_id:
        raise SystemExit("a planned atomic statement ID already exists")
    required_ids = {
        *UNSET_IDS,
        "st-chp2-seciv-l6-17-altarpiece-opportunity",
        "st-chp2-seciv-l6-17-francesco-initially-refused-tapestries",
        "st-chp2-seciv-l6-17-francesco-accepted-tapestries",
        "st-chp2-seciv-l6-17-louvre-visit",
        "st-chp2-seciv-l6-17-fontainebleau-visit",
        "st-chp2-seciv-l6-17-paris-retinue-included-cassiano",
        PRIOR_PARIS_OUTCOME,
        "st-chp2-seciv-l6-17-no-concessions-to-huguenots",
        "st-chp2-seciv-l6-17-francesco-court-cultural-center",
        "st-chp2-seciv-l6-17-welcomed-french-intellectuals",
        COMMITTEE_CONTINUATION,
        FOOTNOTE_THREE,
    }
    if required_ids - statement_by_id.keys():
        raise SystemExit(f"required cross-linked statements missing: {sorted(required_ids - statement_by_id.keys())}")
    candidate_ids = {row["candidate_id"] for row in candidates}
    needed_candidates = {"cand-2036", "cand-3035", "cand-4594", "cand-4596", "cand-4598", "cand-4603", "cand-4605", "cand-4306", "cand-3114", "cand-3397", "cand-3126"}
    if not needed_candidates.issubset(candidate_ids):
        raise SystemExit(f"required candidates missing: {sorted(needed_candidates - candidate_ids)}")
    mention_pairs = {(row["segment_id"], row["candidate_id"], row["surface_form"]) for row in mentions}
    if (SEGMENT_ID, "cand-4596", "they") not in mention_pairs:
        raise SystemExit("the party's courtesy-reception pronoun is not mapped to the Paris retinue candidate")

    source_text = SOURCE.read_text(encoding="utf-8-sig")
    for quote in (COMPETITION_QUOTE, DECISION_QUOTE, COLLECTION_QUOTE, COMMITTEE_QUOTE):
        if quote not in source_text:
            raise SystemExit(f"protected source quote not found: {quote}")
    if len([row for row in coverage if row.get("segment_id") == SEGMENT_ID]) != 1:
        raise SystemExit("expected one print-p.44 L6-17 coverage row")

    cassiano = statement_by_id["st-chp2-seciv-l6-17-cassiano-patron-assessment"]
    cassiano_q = cassiano.setdefault("qualifiers", {})
    cassiano_q["relation_candidate"] = False
    cassiano_q["relation_candidate_note"] = (
        "This is Haskell's evaluative ranking of Cassiano among Italian art patrons, not an entity relation; "
        "the generalized comparison class is not a bounded endpoint."
    )
    cassiano_q["mentioned_candidate_ids"] = ["cand-2036"]

    competition = statement_by_id["st-chp2-seciv-l6-17-competition-and-committee-fragment"]
    competition["subject_candidate_id"] = None
    competition["object_candidate_id"] = "cand-4605"
    competition["predicate"] = "competed_for_patronage_opportunities_reported"
    competition["original_quote"] = COMPETITION_QUOTE
    competition_q = competition.setdefault("qualifiers", {})
    competition_q["claim"] = (
        "Haskell says artists and their protectors competed for the great opportunities arising across Italy, "
        "especially in Florence and Rome."
    )
    competition_q["qualification"] = (
        "No individual competitors are named; the passage identifies only a general class of artists and their protectors. "
        "Its connection to the new St Peter's altarpiece commissions follows the immediately preceding sentence."
    )
    competition_q["relation_candidate"] = True
    competition_q["relation_candidate_note"] = (
        "The source explicitly reports competition for artistic opportunities. The competing persons remain unnamed; "
        "the adjacent altarpiece statement supplies the commission context."
    )
    competition_q["open_endpoint_reason"] = (
        "No individual artists or protectors are identified, so the collective subject cannot be resolved to a candidate."
    )
    competition_q["mentioned_candidate_ids"] = ["cand-3114", "cand-3397", "cand-3126", "cand-4605"]
    competition_q["related_statement_ids"] = ["st-chp2-seciv-l6-17-altarpiece-opportunity"]
    competition_q.pop("committee_candidate_id", None)
    competition_q.pop("continuation_statement_id", None)

    decision = statement_by_id["st-chp2-seciv-l6-17-decision-and-collecting-assessment"]
    decision["original_quote"] = DECISION_QUOTE
    decision_q = decision.setdefault("qualifiers", {})
    decision_q["claim"] = "Haskell judges Francesco's initial refusal of the tapestries as a decision too difficult to sustain."
    decision_q["qualification"] = "This is Haskell's retrospective interpretation of the later reversal, recorded separately from the acceptance event."
    decision_q["relation_candidate"] = False
    decision_q["relation_candidate_note"] = (
        "This is an authorial judgment about Francesco's decision, not a relation claim. The initial refusal and later acceptance "
        "are recorded in separate statements."
    )
    decision_q["mentioned_candidate_ids"] = ["cand-3035"]
    decision_q["related_statement_ids"] = [
        "st-chp2-seciv-l6-17-francesco-initially-refused-tapestries",
        "st-chp2-seciv-l6-17-francesco-accepted-tapestries",
    ]

    new_collection = {
        "statement_id": NEW_COLLECTION_ASSESSMENT_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-3035",
        "object_candidate_id": None,
        "predicate": "art_collecting_assessment",
        "qualifiers": {
            "source_line_start": 10,
            "source_line_end": 10,
            "claim": "Haskell says Francesco's art collecting had begun well.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": 44,
            "pdf_physical_page": 29,
            "qualification": "This is an evaluative summary, not a measurable property or an entity relation.",
            "relation_candidate": False,
            "relation_candidate_note": "This is Haskell's evaluative summary of the opening of Francesco's collection, not a relation claim.",
            "mentioned_candidate_ids": ["cand-3035"],
            "related_statement_ids": ["st-chp2-seciv-l6-17-francesco-accepted-tapestries"],
        },
        "original_quote": COLLECTION_QUOTE,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }

    armistice = statement_by_id["st-chp2-seciv-l6-17-francesco-armistice-instruction"]
    armistice_q = armistice.setdefault("qualifiers", {})
    armistice_q["relation_candidate"] = True
    armistice_q["relation_candidate_note"] = (
        "The passage reports an instruction directed to Francesco, but its passive construction does not identify who issued it."
    )
    armistice_q["open_endpoint_reason"] = "The instruction's issuing authority is not named in the source passage."
    armistice_q["mentioned_candidate_ids"] = ["cand-3035"]
    armistice_q["related_statement_ids"] = ["st-chp2-seciv-l6-17-no-concessions-to-huguenots"]

    status = statement_by_id["st-chp2-seciv-l6-17-francesco-status-assessment"]
    status_q = status.setdefault("qualifiers", {})
    status_q["relation_candidate"] = False
    status_q["relation_candidate_note"] = (
        "This is a contrastive authorial characterization of Francesco's wealth, social standing, and limited independent "
        "political power; no distinct civic office or bounded institution is identified."
    )
    status_q["mentioned_candidate_ids"] = ["cand-3035"]

    madrid = statement_by_id["st-chp2-seciv-l6-17-madrid-mission-failure"]
    madrid["subject_candidate_id"] = "cand-4603"
    madrid["object_candidate_id"] = "cand-4594"
    madrid["predicate"] = "mission_failure_compared_with_reported"
    madrid_q = madrid.setdefault("qualifiers", {})
    madrid_q["claim"] = "Haskell describes the Madrid mission as a failure equal to the earlier Paris mission."
    madrid_q["qualification"] = (
        "The comparison refers back to Haskell's description of the Paris mission as a disastrous failure; "
        "the particular outcome of the Madrid mission is not specified here."
    )
    madrid_q["relation_candidate"] = True
    madrid_q["relation_candidate_note"] = (
        "The phrase 'an equal failure' explicitly compares the Madrid mission with the Paris mission."
    )
    madrid_q["mentioned_candidate_ids"] = ["cand-4603", "cand-4594"]
    madrid_q["related_statement_ids"] = [PRIOR_PARIS_OUTCOME]
    madrid_q.pop("open_endpoint_reason", None)

    courtesy = statement_by_id["st-chp2-seciv-l6-17-party-courtesy-reception"]
    courtesy["subject_candidate_id"] = "cand-4596"
    courtesy["object_candidate_id"] = None
    courtesy["predicate"] = "received_courteous_reception_from_unspecified_hosts_reported"
    courtesy_q = courtesy.setdefault("qualifiers", {})
    courtesy_q["claim"] = (
        "Haskell says the Paris party was received everywhere with extreme courtesy; the receiving persons or institutions are unnamed."
    )
    courtesy_q["relation_candidate"] = True
    courtesy_q["relation_candidate_note"] = (
        "This is an explicit reception relation involving the Paris party, mapped to the existing retinue candidate; "
        "the recipients remain unnamed."
    )
    courtesy_q["open_endpoint_reason"] = "No receiving persons, institutions, or bounded host group are named."
    courtesy_q["mentioned_candidate_ids"] = ["cand-4596"]
    courtesy_q["related_statement_ids"] = [
        "st-chp2-seciv-l6-17-louvre-visit",
        "st-chp2-seciv-l6-17-fontainebleau-visit",
        "st-chp2-seciv-l6-17-paris-retinue-included-cassiano",
    ]

    tapestries = statement_by_id["st-chp2-seciv-l6-17-tapestries-depict-constantine"]
    tapestries_q = tapestries.setdefault("qualifiers", {})
    tapestries_q["relation_candidate"] = True
    tapestries_q["relation_candidate_note"] = (
        "The source explicitly says the tapestries depict scenes from 'The Life of Constantine'. The distinct narrative or cycle "
        "referent remains unresolved; footnote 3 identifies only U. Barberini (1950), whose title/identity is not established here."
    )
    tapestries_q["open_endpoint_reason"] = (
        "The represented narrative/cycle is named, but the source does not identify its precise referent or boundaries; "
        "do not create a separate work candidate from the title alone."
    )
    tapestries_q["mentioned_candidate_ids"] = ["cand-4598"]
    tapestries_q["related_statement_ids"] = [FOOTNOTE_THREE]

    wealth = statement_by_id["st-chp2-seciv-l6-17-wealth-used-for-learning"]
    wealth_q = wealth.setdefault("qualifiers", {})
    wealth_q["relation_candidate"] = False
    wealth_q["relation_candidate_note"] = (
        "This is Haskell's broad contextual account of wealth and influence being used for cultural pursuits and Francesco's devotion. "
        "The passive wording names no acting agent, recipient, institution, or work, so it is retained as a source-limited biographical "
        "claim rather than a normalized entity relation."
    )
    wealth_q["mentioned_candidate_ids"] = ["cand-3035"]
    wealth_q["related_statement_ids"] = [
        "st-chp2-seciv-l6-17-francesco-court-cultural-center",
        "st-chp2-seciv-l6-17-welcomed-french-intellectuals",
    ]

    new_committee = {
        "statement_id": NEW_COMMITTEE_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-4306",
        "object_candidate_id": None,
        "predicate": "committee_correspondence_and_list_preparation_reported",
        "qualifiers": {
            "source_line_start": 17,
            "source_line_end": 17,
            "claim": (
                "Haskell says the unnamed St Peter's decoration committee was being bombarded with letters while lists were being drawn."
            ),
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": 44,
            "pdf_physical_page": 29,
            "qualification": (
                "The letter senders and list contents are not identified. The phrase is cut off at the page break and continues "
                "in section IV L19-29, where committee list amendments and discussions are reported."
            ),
            "relation_candidate": True,
            "relation_candidate_note": (
                "The source reports committee activity involving correspondence and preparation of lists; the external correspondents "
                "and specific list entries remain open."
            ),
            "open_endpoint_reason": "No letter authors, individual letters, or specific list entries are named.",
            "mentioned_candidate_ids": ["cand-4306"],
            "related_statement_ids": [COMMITTEE_CONTINUATION],
        },
        "original_quote": COMMITTEE_QUOTE,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }

    statements.extend([new_collection, new_committee])
    if any(
        row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
        for row in statements
    ):
        raise SystemExit("section IV L6-17 still has unset relation_candidate values")

    coverage_row = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    coverage_note = (
        " 本轮逐项闭合9条旧unset，并拆分两条复合statement：艺术家/保护人竞争与委员会来信/名单分别记录；拒收判断与“收藏开端良好”分别保留。"
        "Cassiano评价、Francesco社会政治状态及宽泛财富用途保留为非关系陈述；停战指令保留未名发令者，"
        "马德里使团失败与巴黎使团结局建立比较候选，礼遇接收方与《The Life of Constantine》题材身份维持开放。"
        "印刷p.44（PDF物理第29页）已核对；脚注3仅指U. Barberini（1950），未据此确定题材身份；S0来源未改。"
    )
    if coverage_note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_note

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    result = {
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "closed_unset_ids": sorted(UNSET_IDS),
        "classifications": {
            "false": [
                "st-chp2-seciv-l6-17-cassiano-patron-assessment",
                "st-chp2-seciv-l6-17-decision-and-collecting-assessment",
                NEW_COLLECTION_ASSESSMENT_ID,
                "st-chp2-seciv-l6-17-francesco-status-assessment",
                "st-chp2-seciv-l6-17-wealth-used-for-learning",
            ],
            "true": [
                "st-chp2-seciv-l6-17-competition-and-committee-fragment",
                NEW_COMMITTEE_ID,
                "st-chp2-seciv-l6-17-francesco-armistice-instruction",
                "st-chp2-seciv-l6-17-madrid-mission-failure",
                "st-chp2-seciv-l6-17-party-courtesy-reception",
                "st-chp2-seciv-l6-17-tapestries-depict-constantine",
            ],
        },
        "new_candidates": 0,
        "new_mentions": 0,
        "new_atomic_statements": [NEW_COMMITTEE_ID, NEW_COLLECTION_ASSESSMENT_ID],
        "remaining_unset_in_segment": [],
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if written_by_id["st-chp2-seciv-l6-17-party-courtesy-reception"].get("subject_candidate_id") != "cand-4596":
            raise SystemExit("party reception was not mapped to its existing retinue candidate")
        if written_by_id[NEW_COMMITTEE_ID].get("qualifiers", {}).get("relation_candidate") is not True:
            raise SystemExit("the split committee correspondence statement was not persisted")
        if written_by_id[NEW_COLLECTION_ASSESSMENT_ID].get("qualifiers", {}).get("relation_candidate") is not False:
            raise SystemExit("the split collection assessment was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
