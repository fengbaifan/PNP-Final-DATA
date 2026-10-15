from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
COVERAGE = TABLE_DIR / "s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"

EXPECTED_HASHES = {
    STATEMENTS: "344c2f598069c0c885f95ccb583e2d3e0956e8c152734cab6871dfda4dd635cf",
    CANDIDATES: "cd4315025fcf3660251c3495c4c85e2d581642c2864379e1c3ae7dd737243798",
    MENTIONS: "cbfd05625e64c2c0c0bd90c1704c48c9f0f2f2d71a02ca712163e83d4e00a410",
    COVERAGE: "18ee051fe1bbf7712fd368681d0dcea8291838dd21f988fe176b1759336b092b",
}
SOURCE_SHA256 = "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d"
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp6-p147-semantic-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp6-p147-artist-group-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp6-p147-artist-group-20261013"),
    COVERAGE: COVERAGE.with_name("s2-coverage.csv.bak-s2-chp6-p147-semantic-20261013"),
}
SEGMENT = "chp-6:06_CHP-6_sec_i:l13-24"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"

QUOTES = {
    "st-chp6-p147-barberini-family-flees": (17, 17, "The Barberini themselves fled when an investigation of their incomes was threatened"),
    "st-chp6-p147-bernini-campanile-demolition": (20, 20, "His official career reached its lowest point"),
    "st-chp6-p147-bernini-cornaro-chapel-commission": (
        19, 20, "Bernini undertook his first large private commission for a generation—the Cornaro chapel in S. Maria della Vittoria with the famous St Theresa"
    ),
    "st-chp6-p147-bernini-expresses-bitterness-in-group": (
        20, 20, "and expressed the bitterness of his feelings in a group of Time unveiling Truth."
    ),
    "st-chp6-p147-bernini-replaced-as-leading-architect": (
        20, 22, "His place as leading, architect was taken by two men—Girolamo Rainaldi, a totally unfashionable figure nearly thirty years older than himself, and Francesco Borromini, his hated rival."
    ),
    "st-chp6-p147-borromini-rival-of-bernini": (22, 22, "Francesco Borromini, his hated rival."),
    "st-chp6-p147-borromini-takes-over-lateran-remodelling": (
        23, 23, "Borromini took over the complete remodelling of St John Lateran, the Cathedral of Rome"
    ),
    "st-chp6-p147-camillo-authority-retained": (
        14, 14, "the Pope and the already appointed Secretary of State firmly retained all serious political authority in their own hands."
    ),
    "st-chp6-p147-camillo-cardinal-nephew": (
        14, 14, "In November, only two months after these arrangements, Camillo was made Cardinal nephew and given a pile of benefices."
    ),
    "st-chp6-p147-camillo-dynastic-choice": (
        14, 14, "Should this young man of 22 be given political power in the only manner possible by being made a cardinal or should he be encouraged to marry and found a princely dynasty? The Pope hesitated, and then decided that the second course was the right one."
    ),
    "st-chp6-p147-camillo-legate-avignon": (
        14, 14, "He began his duties as legate at Avignon with some enthusiasm"
    ),
    "st-chp6-p147-camillo-military-appointments": (
        14, 14, "Camillo was made commander-in-chief of all the land and sea forces and governor of the more important strong points."
    ),
    "st-chp6-p147-camillo-not-leading-patron": (
        17, 17, "All this will have made it clear that for some years Camillo Pamfili was in no position to replace Francesco Barberini as the leading art patron in Rome."
    ),
    "st-chp6-p147-camillo-resigns-and-marries": (
        14, 14, "in 1647 he went through the almost unheard-of procedure of resigning his cardinalate and marrying."
    ),
    "st-chp6-p147-cortona-continues-oratorian-work": (
        19, 19, "Pietro da Cortona carried on working for the Oratorians;"
    ),
    "st-chp6-p147-francesco-maidalchini-selected": (
        17, 18, "the 17-y earold Francesco Maidalchini who was chosen by his aunt Donna Olimpia to supersede Camillo as papal nephew"
    ),
    "st-chp6-p147-innocent-directs-patronage": (
        19, 19, "Thus it was the Pope himself who directed what patronage there was."
    ),
    "st-chp6-p147-lateran-and-st-peters-contrast": (
        22, 24, "whose decrepit and still largely mediaeval condition was the more glaring by contrast with the splendour of Urban VIII’s decoration of St Peter’s."
    ),
    "st-chp6-p147-major-works-reactionary-partial": (
        23, 24, "Both these major works were somewhat ‘reactionary’ in"
    ),
    "st-chp6-p147-olimpia-court-position-and-character": (
        14, 15, "whose dominating position in Innocent X’s court, led to endless scandals and ferocious quarrels"
    ),
    "st-chp6-p147-olimpia-excludes-camillo-and-wife": (
        16, 16, "and she showed her displeasure at Camillo’s marriage by making sure that neither he nor his wife should be allowed into the city.1"
    ),
    "st-chp6-p147-olimpia-guides-camillo": (
        14, 15, "he had been alternatively encouraged and thwarted by his formidable mother, the Pope’s sister-in-law, Donna Olimpia Maidalchini."
    ),
    "st-chp6-p147-only-nephew-named-camillo": (14, 14, "Camillo."),
    "st-chp6-p147-outsider-secretary-of-state": (14, 14, "An outsider was brought in as Secretary of State"),
    "st-chp6-p147-rainaldi-characterized": (
        20, 21, "Rainaldi, a totally unfashionable figure nearly thirty years older than himself"
    ),
    "st-chp6-p147-rainaldi-plans-pamfili-palace": (
        22, 23, "Rainaldi planned the vast palace on the Piazza Navona"
    ),
}

FALSE_NOTE = (
    "This is the source-attributed evaluation or page-turn identity closure described in the claim; "
    "it is not an additional entity-to-entity or domain relation."
)
RELATION_NOTE = (
    "This preserves Haskell's source-attributed relationship candidate. It is not an independently verified fact or an S6 formal edge."
)
FLAGS = {
    "st-chp6-p147-barberini-family-flees": (True, "The collective family's flight is explicit; the text does not identify the investigating authority, the members who left or their destination."),
    "st-chp6-p147-bernini-campanile-demolition": (False, "This is Haskell's evaluative characterization of Bernini's official career; the committee's decision is recorded separately."),
    "st-chp6-p147-bernini-cornaro-chapel-commission": (True, "The source explicitly relates Bernini to a large private commission at the Cornaro Chapel; the chapel remains a site and the commissioner is not named."),
    "st-chp6-p147-bernini-expresses-bitterness-in-group": (True, "This preserves Haskell's interpretation of an expressive relation between Bernini and the named group; it is not a documented statement by Bernini here."),
    "st-chp6-p147-bernini-replaced-as-leading-architect": (True, "This records Rainaldi taking Bernini's place as leading architect; the parallel Borromini statement is separate."),
    "st-chp6-p147-borromini-rival-of-bernini": (True, "Haskell explicitly characterizes Borromini as Bernini's rival."),
    "st-chp6-p147-borromini-takes-over-lateran-remodelling": (True, "The source explicitly relates Borromini to the remodelling project; the project is distinct from the church building."),
    "st-chp6-p147-camillo-authority-retained": (True, "This records Innocent X's stated retention of political authority over Camillo; the Secretary of State's parallel role is separately recorded."),
    "st-chp6-p147-camillo-cardinal-nephew": (True, "The source attributes Camillo's appointment as Cardinal nephew and grant of benefices to the changed plan; the benefices are not individually identified."),
    "st-chp6-p147-camillo-dynastic-choice": (True, "Haskell explicitly reports Innocent X's choice between a cardinalate and marriage/dynasty for Camillo."),
    "st-chp6-p147-camillo-legate-avignon": (True, "The source states that Camillo served as legate at Avignon; it gives no exact start date."),
    "st-chp6-p147-camillo-military-appointments": (True, "The source reports Camillo's appointments but leaves the appointing actor unstated; exact dates and strong points are also unspecified."),
    "st-chp6-p147-camillo-not-leading-patron": (True, "Haskell explicitly compares Camillo's position with Francesco Barberini's leading role in Roman patronage; the assessment is time-bounded."),
    "st-chp6-p147-camillo-resigns-and-marries": (True, "The revised statement records Camillo's marriage to the unnamed wife; the cardinalate resignation is separately recorded."),
    "st-chp6-p147-cortona-continues-oratorian-work": (True, "The source explicitly states that Pietro da Cortona continued working for the Oratorians; no specific project or dates are named."),
    "st-chp6-p147-francesco-maidalchini-selected": (True, "This records Donna Olimpia's selection of Francesco Maidalchini to supersede Camillo as papal nephew; Haskell's forecast about cultural impact is separate."),
    "st-chp6-p147-innocent-directs-patronage": (True, "This records Innocent X directing the patronage that remained. His stated building and artist-use policies are separate candidate statements."),
    "st-chp6-p147-lateran-and-st-peters-contrast": (True, "This preserves Haskell's explicit comparison of the Lateran's condition with the splendour of Urban VIII's St Peter's decoration."),
    "st-chp6-p147-major-works-reactionary-partial": (False, "This is Haskell's incomplete aesthetic characterization of two works, continued on p. 148; it is not an entity-to-entity relation."),
    "st-chp6-p147-olimpia-court-position-and-character": (True, "This records Donna Olimpia's position in Innocent X's court and Haskell's attribution of scandals and quarrels to it; personality traits are separately recorded."),
    "st-chp6-p147-olimpia-excludes-camillo-and-wife": (True, "The revised statement records Donna Olimpia's exclusion of Camillo from Rome; his wife's exclusion is recorded separately."),
    "st-chp6-p147-olimpia-guides-camillo": (True, "Haskell explicitly says Donna Olimpia alternately encouraged and thwarted Camillo during the manoeuvres."),
    "st-chp6-p147-only-nephew-named-camillo": (False, "This closes a page-break anaphora; the nephew relation is already recorded in the p. 146 statement."),
    "st-chp6-p147-outsider-secretary-of-state": (True, "The source explicitly reports appointment of an unnamed outsider to the Secretary of State role; no person identity is inferred."),
    "st-chp6-p147-rainaldi-characterized": (True, "The revised statement records Haskell's approximate age comparison between Rainaldi and Bernini; the 'unfashionable' assessment is separate."),
    "st-chp6-p147-rainaldi-plans-pamfili-palace": (True, "The revised statement records Rainaldi as planner of the Piazza Navona palace; Innocent X's earlier residence there is separate."),
}

NEW_IDS = {
    "st-chp6-p147-bernini-campanile-committee-decision",
    "st-chp6-p147-bernini-replaced-by-borromini",
    "st-chp6-p147-camillo-secretary-state-authority",
    "st-chp6-p147-camillo-resigns-cardinalate",
    "st-chp6-p147-francesco-maidalchini-culture-assessment",
    "st-chp6-p147-olimpia-characteristics",
    "st-chp6-p147-olimpia-jealousy",
    "st-chp6-p147-olimpia-excludes-wife",
    "st-chp6-p147-rainaldi-unfashionable",
    "st-chp6-p147-innocent-lived-pamfili-palace",
    "st-chp6-p147-innocent-building-intention",
    "st-chp6-p147-innocent-limits-urban-artists",
}
ARTIST_GROUP_ID = "cand-11956"
ARTIST_GROUP_MENTION_ID = "m-chp6-p147-075"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def csv_row_bytes(fields: list[str], row: dict[str, str]) -> bytes:
    buf = io.StringIO(newline="")
    csv.writer(buf, lineterminator="\r\n").writerow([row.get(k, "") for k in fields])
    return buf.getvalue().encode("utf-8")


def append_csv_row(data: bytes, fields: list[str], row: dict[str, str]) -> bytes:
    if not data.endswith((b"\n", b"\r")):
        raise SystemExit("CSV append preflight failed: table has no final line break")
    return data + csv_row_bytes(fields, row)


def update_coverage(data: bytes) -> bytes:
    lines = data.splitlines(keepends=True)
    header = next(csv.reader([lines[0].decode("utf-8-sig")]))
    segment_idx, note_idx = header.index("segment_id"), header.index("note")
    old_note = (
        "按规范段逐行处理印刷页147正文；关闭L11唯一侄辈→L14 Camillo续接，并在L24开启延续至下一段L27的reactionary句。"
        "脚注1回链待L120-157迁移。OCR校勘见过程记录；S0不改。"
    )
    new_note = (
        "印刷页147正文26条原statement均已裁决，新增12条用于分开双端关系、角色、行动和评价；"
        "脚注1继续链接L16排斥断言，页内reactionary句由页148 L27闭合。保留S0 OCR，校勘见过程记录。"
    )
    seen = False
    out = [lines[0]]
    for raw in lines[1:]:
        row = next(csv.reader([raw.decode("utf-8")]))
        if row[segment_idx] == SEGMENT:
            if seen or row[note_idx] != old_note:
                raise SystemExit("p.147 coverage row preflight failed")
            seen = True
            row[note_idx] = new_note
            buf = io.StringIO(newline="")
            csv.writer(buf, lineterminator="\r\n").writerow(row)
            out.append(buf.getvalue().encode("utf-8"))
        else:
            out.append(raw)
    if not seen:
        raise SystemExit("p.147 coverage row not found")
    return b"".join(out)


def new_statement(
    sid: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    quote: str,
    claim: str,
    first: int,
    last: int,
    mentioned: list[str],
    relation: bool,
    relation_note: str,
    qualification: str,
    text_layer: str = "authorial historical narrative",
    base_q: dict | None = None,
) -> dict:
    q = deepcopy(base_q) if base_q is not None else {}
    q.update(
        {
            "source_line_start": first,
            "source_line_end": last,
            "printed_page": "147",
            "pdf_physical_page": 2,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": text_layer,
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation,
            "relation_candidate_note": relation_note,
        }
    )
    return {
        "statement_id": sid,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve the p. 147 body segment at S2.")
    parser.add_argument("--apply", action="store_true", help="write after guarded dry-run checks pass")
    args = parser.parse_args()

    raw_files = {p: p.read_bytes() for p in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(raw_files[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: expected {expected}, got {actual}")
    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")
    for backup in BACKUPS.values():
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing to overwrite: {backup}")

    source_lines = source_bytes.decode("utf-8").splitlines()
    for sid, (first, last, quote) in QUOTES.items():
        span = " ".join(source_lines[first - 1:last])
        if normalize(quote) not in normalize(span):
            raise SystemExit(f"source quote preflight failed: {sid}")

    source_text = "\n".join(source_lines[12:24])
    artist_start = source_text.find("artists most closely associated")
    if artist_start < 0 or source_text[artist_start:artist_start + 7] != "artists":
        raise SystemExit("predecessor-artists source anchor mismatch")
    artist_start, artist_end = artist_start, artist_start + 7

    statements_text = raw_files[STATEMENTS].decode("utf-8")
    rows = [json.loads(line) for line in statements_text.splitlines() if line.strip()]
    by_id: dict[str, dict] = {}
    for row in rows:
        sid = row["statement_id"]
        if sid in by_id:
            raise SystemExit(f"duplicate statement ID: {sid}")
        by_id[sid] = row
    if len(QUOTES) != 26 or set(QUOTES) != set(FLAGS):
        raise SystemExit("p.147 expected statement count or classification target mismatch")
    for sid, (first, last, _) in QUOTES.items():
        row = by_id.get(sid)
        if row is None or row.get("segment_id") != SEGMENT or row.get("source_file") != SOURCE_FILE:
            raise SystemExit(f"target provenance mismatch: {sid}")
        q = row.get("qualifiers") or {}
        if q.get("relation_candidate") is not None:
            raise SystemExit(f"statement already classified: {sid}")
        old_anchor = (q.get("source_line_start"), q.get("source_line_end"))
        expected_old_anchor = (14, 14) if sid == "st-chp6-p147-olimpia-guides-camillo" else (first, last)
        if old_anchor != expected_old_anchor:
            raise SystemExit(f"source line anchor mismatch: {sid}")
        if q.get("printed_page") != "147":
            raise SystemExit(f"printed page mismatch: {sid}")
    if set(by_id) & NEW_IDS:
        raise SystemExit(f"new statement IDs already exist: {sorted(set(by_id) & NEW_IDS)}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidate_reader = csv.DictReader(f)
        candidate_fields = candidate_reader.fieldnames or []
        candidates = {r["candidate_id"]: r for r in candidate_reader}
    if ARTIST_GROUP_ID in candidates:
        raise SystemExit(f"candidate ID already exists: {ARTIST_GROUP_ID}")
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mention_reader = csv.DictReader(f)
        mention_fields = mention_reader.fieldnames or []
        mention_rows = list(mention_reader)
    if any(m["mention_id"] == ARTIST_GROUP_MENTION_ID for m in mention_rows):
        raise SystemExit(f"mention ID already exists: {ARTIST_GROUP_MENTION_ID}")
    for m in mention_rows:
        if m["segment_id"] != SEGMENT:
            continue
        start, end = int(m["start_char"]), int(m["end_char"])
        if artist_start < end and start < artist_end:
            raise SystemExit(f"artist group mention overlaps existing mention {m['mention_id']}")
    if artist_start != 2216 or artist_end != 2223:
        raise SystemExit(f"unexpected artist mention offsets: {artist_start}:{artist_end}")

    # Set exact source quotes and relation-candidate decisions for the original rows.
    for sid, (first, last, quote) in QUOTES.items():
        row = by_id[sid]
        q = row["qualifiers"]
        row["original_quote"] = quote
        flag, note = FLAGS[sid]
        q["relation_candidate"] = flag
        q["relation_candidate_note"] = note
        q["source_line_start"] = first
        q["source_line_end"] = last

    # Keep mixed clauses as separate claims where their endpoints or semantic status differ.
    camp = by_id["st-chp6-p147-bernini-campanile-demolition"]
    camp["subject_candidate_id"] = "cand-0312"
    camp["object_candidate_id"] = None
    camp["predicate"] = "official-career-characterized-as-low-point"
    camp["qualifiers"]["claim"] = "Haskell says the committee's decision to remove the campanile marked the low point of Bernini's official career."
    camp["qualifiers"]["mentioned_candidate_ids"] = ["cand-0312", "cand-6276", "cand-6275"]

    replacement = by_id["st-chp6-p147-bernini-replaced-as-leading-architect"]
    replacement["object_candidate_id"] = "cand-2093"
    replacement["predicate"] = "replaced-as-leading-architect-by"
    replacement["original_quote"] = "His place as leading, architect was taken by two men—Girolamo Rainaldi, a totally unfashionable figure nearly thirty years older than himself, and Francesco Borromini, his hated rival."
    replacement["qualifiers"]["claim"] = "Haskell says Girolamo Rainaldi took Bernini's place as leading architect."
    replacement["qualifiers"]["mentioned_candidate_ids"] = ["cand-0312", "cand-2093"]

    authority = by_id["st-chp6-p147-camillo-authority-retained"]
    authority["original_quote"] = "the Pope and the already appointed Secretary of State firmly retained all serious political authority in their own hands."
    authority["predicate"] = "retains-political-authority-over-camillo"
    authority["qualifiers"]["claim"] = "Haskell says Innocent X firmly retained serious political authority over Camillo during the legation."
    authority["qualifiers"]["mentioned_candidate_ids"] = ["cand-1819", "cand-1814"]

    military = by_id["st-chp6-p147-camillo-military-appointments"]
    military["subject_candidate_id"] = None
    military["object_candidate_id"] = "cand-1814"
    military["predicate"] = "is-made-commander-in-chief-and-governor"
    military["original_quote"] = "Camillo was made commander-in-chief of all the land and sea forces and governor of the more important strong points."
    military["qualifiers"]["claim"] = "Haskell says Camillo was made commander-in-chief of the land and sea forces and governor of the more important strong points."
    military["qualifiers"]["qualification"] = (
        "The source uses passive constructions and does not identify who made these appointments; "
        "the Pope is not inferred as appointing subject from the surrounding passage."
    )
    military["qualifiers"]["mentioned_candidate_ids"] = ["cand-1814"]

    marriage = by_id["st-chp6-p147-camillo-resigns-and-marries"]
    marriage["predicate"] = "marries-unidentified-wife"
    marriage["original_quote"] = "in 1647 he went through the almost unheard-of procedure of resigning his cardinalate and marrying."
    marriage["qualifiers"]["claim"] = "Haskell says Camillo married his unnamed wife in 1647 after resigning his cardinalate."
    marriage["qualifiers"]["mentioned_candidate_ids"] = ["cand-1814", "cand-6271"]

    chosen = by_id["st-chp6-p147-francesco-maidalchini-selected"]
    chosen["qualifiers"]["claim"] = "Haskell says Donna Olimpia chose Francesco Maidalchini to supersede Camillo as papal nephew."
    chosen["qualifiers"]["mentioned_candidate_ids"] = ["cand-1496", "cand-1495", "cand-1814"]

    policy = by_id["st-chp6-p147-innocent-directs-patronage"]
    policy["predicate"] = "directs-remaining-patronage"
    policy["qualifiers"]["claim"] = "Haskell says Innocent X directed the patronage that remained."
    policy["qualifiers"]["qualification"] = "The Pope's building aim and proposed restriction on artists associated with Urban VIII are preserved in separate statements; the passage does not say every aim was completed."
    policy["qualifiers"]["mentioned_candidate_ids"] = ["cand-1819", "cand-6267"]

    court = by_id["st-chp6-p147-olimpia-court-position-and-character"]
    court["qualifiers"]["claim"] = "Haskell says Donna Olimpia's dominant position at Innocent X's court led to scandals and quarrels."
    court["qualifiers"]["mentioned_candidate_ids"] = ["cand-1496", "cand-1819"]

    exclusion = by_id["st-chp6-p147-olimpia-excludes-camillo-and-wife"]
    exclusion["original_quote"] = "and she showed her displeasure at Camillo’s marriage by making sure that neither he nor his wife should be allowed into the city.1"
    exclusion["qualifiers"]["claim"] = "Haskell says Donna Olimpia ensured that Camillo was not allowed into Rome after his marriage."
    exclusion["qualifiers"]["mentioned_candidate_ids"] = ["cand-1496", "cand-1814", "cand-4490"]

    # Resolve the Rainaldi sentence into age, aesthetic assessment and planning/residence claims.
    rainaldi = by_id["st-chp6-p147-rainaldi-characterized"]
    rainaldi["predicate"] = "nearly-thirty-years-older-than"
    rainaldi["original_quote"] = "Rainaldi, a totally unfashionable figure nearly thirty years older than himself"
    rainaldi["qualifiers"]["claim"] = "Haskell estimates that Girolamo Rainaldi was nearly thirty years older than Bernini."
    rainaldi["qualifiers"]["mentioned_candidate_ids"] = ["cand-2093", "cand-0312"]

    plan = by_id["st-chp6-p147-rainaldi-plans-pamfili-palace"]
    plan["predicate"] = "plans-palace"
    plan["original_quote"] = "Rainaldi planned the vast palace on the Piazza Navona"
    plan["qualifiers"]["claim"] = "Haskell says Girolamo Rainaldi planned the vast palace on Piazza Navona."
    plan["qualifiers"]["mentioned_candidate_ids"] = ["cand-2093", "cand-1824", "cand-3455"]

    nephew = by_id["st-chp6-p147-only-nephew-named-camillo"]
    nephew["qualifiers"]["claim"] = "The opening name Camillo closes the page-break reference to Innocent X's only nephew."
    nephew["qualifiers"]["relation_candidate_note"] = (
        "This is a cross-page identity closure; the nephew relation itself is retained in the p. 146 statement."
    )

    source_quote_line20 = "under the chairmanship of the Pope, a special committee decided to pull down the first oflhe two proposed campaniles which he had added to the façade of St Peter’s for Urban VIII."
    if normalize(source_quote_line20) not in normalize(source_lines[19]):
        raise SystemExit("campanile committee clause anchor mismatch")
    source_quote_line14 = source_lines[13]

    additions: dict[str, list[dict]] = {}
    def add(after: str, statement: dict) -> None:
        additions.setdefault(after, []).append(statement)

    add("st-chp6-p147-bernini-campanile-demolition", new_statement(
        "st-chp6-p147-bernini-campanile-committee-decision",
        "cand-6276", "cand-6275", "committee-decided-to-remove-campanile",
        source_quote_line20,
        "Haskell says a special committee, chaired by Innocent X, decided to pull down the first of the two proposed campaniles Bernini had added to St Peter's façade for Urban VIII.",
        20, 20, ["cand-6276", "cand-6275", "cand-1819", "cand-0312", "cand-4232", "cand-5696", "cand-0209"],
        True,
        "This records the source-attributed committee decision and named target structure; it does not infer the second campanile's completion or fate.",
        "The committee's membership is unspecified; Haskell identifies Innocent X as its chair.",
    ))
    add("st-chp6-p147-bernini-replaced-as-leading-architect", new_statement(
        "st-chp6-p147-bernini-replaced-by-borromini",
        "cand-0312", "cand-0406", "replaced-as-leading-architect-by",
        "His place as leading, architect was taken by two men—Girolamo Rainaldi, a totally unfashionable figure nearly thirty years older than himself, and Francesco Borromini, his hated rival.",
        "Haskell says Francesco Borromini also took Bernini's place as leading architect.",
        20, 22, ["cand-0312", "cand-0406"], True,
        "This records the second named successor separately; the source does not imply the two men held an identical formal office.",
        "Haskell calls Borromini Bernini's hated rival.",
    ))
    add("st-chp6-p147-camillo-authority-retained", new_statement(
        "st-chp6-p147-camillo-secretary-state-authority",
        "cand-4294", "cand-1814", "office-retains-authority-over-camillo",
        "the already appointed Secretary of State firmly retained all serious political authority in their own hands.",
        "Haskell says the already appointed Secretary of State also retained serious political authority over Camillo.",
        14, 14, ["cand-4294", "cand-1814", "cand-1819"], True,
        "The Secretary of State's holder is unnamed; the claim preserves the role-level actor without inferring a person.",
        "The Secretary of State is recorded as the source-defined office candidate.",
    ))
    resignation = new_statement(
        "st-chp6-p147-camillo-resigns-cardinalate",
        "cand-1814", None, "resigns-cardinalate",
        "resigning his cardinalate",
        "Haskell says Camillo resigned his cardinalate in 1647.",
        14, 14, ["cand-1814"], True,
        "The source dates the resignation to 1647; the cardinalate is a role rather than a separately identified entity in this passage.",
        "This records a source-attributed office transition.",
    )
    resignation["qualifiers"]["year"] = 1647
    add("st-chp6-p147-camillo-resigns-and-marries", resignation)
    add("st-chp6-p147-francesco-maidalchini-selected", new_statement(
        "st-chp6-p147-francesco-maidalchini-culture-assessment",
        "cand-1495", None, "assessed-as-unlikely-to-affect-roman-culture",
        "was clearly not destined to make an impact on Roman culture.",
        "Haskell judges Francesco Maidalchini unlikely to make an impact on Roman culture.",
        18, 18, ["cand-1495", "cand-4490"], False, FALSE_NOTE,
        "This is Haskell's evaluative forecast, not a measured conclusion.",
        "authorial historical assessment",
    ))
    add("st-chp6-p147-olimpia-court-position-and-character", new_statement(
        "st-chp6-p147-olimpia-characteristics",
        "cand-1496", None, "characterized-as-shrewd-greedy-and-ambitious",
        "was shrewd, greedy and ambitious.",
        "Haskell characterizes Donna Olimpia as shrewd, greedy and ambitious.",
        15, 15, ["cand-1496"], False, FALSE_NOTE,
        "These are Haskell's attributed personality descriptions, not independently established facts.",
        "authorial characterization",
    ))
    add("st-chp6-p147-olimpia-court-position-and-character", new_statement(
        "st-chp6-p147-olimpia-jealousy",
        "cand-1496", None, "characterized-as-jealous-of-court-position",
        "Above all she was excessively jealous of anyone replacing her as the first lady in Rome",
        "Haskell describes Donna Olimpia as excessively jealous of anyone replacing her as first lady in Rome.",
        16, 16, ["cand-1496", "cand-4490"], False, FALSE_NOTE,
        "This is Haskell's attributed psychological characterization, not an independently established fact.",
        "authorial characterization",
        base_q=exclusion["qualifiers"],
    ))
    add("st-chp6-p147-olimpia-excludes-camillo-and-wife", new_statement(
        "st-chp6-p147-olimpia-excludes-wife",
        "cand-1496", "cand-6271", "excludes-unidentified-wife-from-rome",
        "neither he nor his wife should be allowed into the city.1",
        "Haskell says Donna Olimpia ensured that Camillo's unnamed wife was not allowed into Rome.",
        16, 16, ["cand-1496", "cand-1814", "cand-6271", "cand-4490"], True,
        "The wife is unnamed and the administrative mechanism is unspecified; this preserves only Haskell's reported exclusion.",
        "authorial historical narrative",
        base_q=exclusion["qualifiers"],
    ))
    add("st-chp6-p147-rainaldi-characterized", new_statement(
        "st-chp6-p147-rainaldi-unfashionable",
        "cand-2093", None, "characterized-as-unfashionable",
        "a totally unfashionable figure",
        "Haskell characterizes Girolamo Rainaldi as totally unfashionable.",
        20, 21, ["cand-2093"], False, FALSE_NOTE,
        "This is Haskell's evaluative characterization, not an independently measured fact.",
        "authorial characterization",
    ))
    add("st-chp6-p147-rainaldi-plans-pamfili-palace", new_statement(
        "st-chp6-p147-innocent-lived-pamfili-palace",
        "cand-1819", "cand-1824", "lived-in-as-cardinal",
        "where Innocent had lived as a cardinal",
        "Haskell says Innocent X had lived in the Piazza Navona palace as a cardinal.",
        22, 23, ["cand-1819", "cand-1824", "cand-3455"], True,
        "This is a past residence report; the statement does not say the building was constructed under Innocent X.",
        "authorial historical narrative",
    ))
    add("st-chp6-p147-innocent-directs-patronage", new_statement(
        "st-chp6-p147-innocent-building-intention",
        "cand-1819", None, "intended-to-erect-palace-and-ecclesiastical-buildings",
        "to erect the usual great family palace and ecclesiastical buildings",
        "Haskell says Innocent X intended to erect a family palace and ecclesiastical buildings.",
        19, 19, ["cand-1819"], True,
        "The passage names building types but does not identify every planned structure; none is inferred from the later Piazza Navona reference.",
        "authorial historical narrative",
    ))
    add("st-chp6-p147-innocent-directs-patronage", new_statement(
        "st-chp6-p147-innocent-limits-urban-artists",
        "cand-1819", ARTIST_GROUP_ID, "intended-to-limit-use-of-predecessor-associated-artists",
        "to make as little use as possible of the artists most closely associated with his predecessor.",
        "Haskell says Innocent X intended to use as few as possible of the artists most closely associated with Urban VIII.",
        19, 19, ["cand-1819", ARTIST_GROUP_ID, "cand-0209"], True,
        "This records the Pope's stated intention; the group is unnamed and its members are not inferred.",
        "authorial historical narrative",
    ))

    artist_candidate = {
        "candidate_id": ARTIST_GROUP_ID,
        "index_entry_id": "",
        "canonical_name": "Artists most closely associated with Urban VIII in Haskell's p. 147 account",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell describes an unnamed group of artists most closely associated with Urban VIII, whose use Innocent X intended to minimize. No members are identified in this passage.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-6:06_CHP-6_sec_i:l13-24#L19",
    }
    artist_mention = {
        "mention_id": ARTIST_GROUP_MENTION_ID,
        "segment_id": SEGMENT,
        "candidate_id": ARTIST_GROUP_ID,
        "surface_form": "artists",
        "start_char": str(artist_start),
        "end_char": str(artist_end),
        "note": "Noun head of Haskell's unnamed group most closely associated with Urban VIII; group members remain unidentified.",
    }

    # Mark the full p.147 sentence-final footnote as linked to the split exclusion claims.
    note1 = by_id.get("st-chp6-notes-l121-p147-n1")
    if note1 is None:
        raise SystemExit("p.147 footnote statement missing")
    nq = note1.get("qualifiers") or {}
    expected_links = ["st-chp6-p147-olimpia-excludes-camillo-and-wife"]
    if nq.get("linked_body_statement_ids") != expected_links or nq.get("citation_body_statement_ids") != expected_links:
        raise SystemExit("p.147 footnote backlink preflight failed")
    q_exclusion = exclusion["qualifiers"]
    q_exclusion["footnote_body_link_status"] = "linked"
    q_exclusion["footnote_pending"] = False
    for extra_id in ["st-chp6-p147-olimpia-jealousy", "st-chp6-p147-olimpia-excludes-wife"]:
        if extra_id not in NEW_IDS:
            raise SystemExit("unexpected footnote-linked p.147 statement")
    note_links = [
        "st-chp6-p147-olimpia-excludes-camillo-and-wife",
        "st-chp6-p147-olimpia-excludes-wife",
    ]
    nq["linked_body_statement_ids"] = note_links
    nq["citation_body_statement_ids"] = note_links

    new_ids_in_source = NEW_IDS
    if set(by_id) & new_ids_in_source:
        raise SystemExit(f"new statement IDs already exist: {sorted(set(by_id) & new_ids_in_source)}")

    output_lines: list[str] = []
    final_ids = set(by_id)
    for raw_line in statements_text.splitlines():
        row = json.loads(raw_line)
        sid = row["statement_id"]
        if sid in QUOTES:
            output_lines.append(json.dumps(by_id[sid], ensure_ascii=False, separators=(",", ":")))
        elif sid == "st-chp6-notes-l121-p147-n1":
            output_lines.append(json.dumps(note1, ensure_ascii=False, separators=(",", ":")))
        else:
            output_lines.append(raw_line)
        for extra in additions.get(sid, []):
            if extra["statement_id"] in final_ids:
                raise SystemExit(f"duplicate added statement: {extra['statement_id']}")
            final_ids.add(extra["statement_id"])
            output_lines.append(json.dumps(extra, ensure_ascii=False, separators=(",", ":")))
    if final_ids != set(by_id) | new_ids_in_source:
        raise SystemExit("statement output ID set mismatch")
    statement_output = ("\n".join(output_lines) + "\n").encode("utf-8")

    candidate_output = append_csv_row(raw_files[CANDIDATES], candidate_fields, artist_candidate)
    mention_output = append_csv_row(raw_files[MENTIONS], mention_fields, artist_mention)
    coverage_output = update_coverage(raw_files[COVERAGE])
    outputs = {
        STATEMENTS: statement_output,
        CANDIDATES: candidate_output,
        MENTIONS: mention_output,
        COVERAGE: coverage_output,
    }

    flag_counts = {
        "true": sum(FLAGS[sid][0] for sid in FLAGS) + 8,
        "false": sum(not FLAGS[sid][0] for sid in FLAGS) + 4,
        "unset": 0,
    }
    print("preflight passed: base_statements=26 added_statements=12 added_candidates=1 added_mentions=1")
    print(f"processed p.147 relation flags: true={flag_counts['true']} false={flag_counts['false']} unset=0")
    print("new statement IDs:")
    for sid in sorted(NEW_IDS):
        row = next(statement for added in additions.values() for statement in added if statement["statement_id"] == sid)
        print(f"  {sid}: {row['predicate']} {row['subject_candidate_id']} -> {row['object_candidate_id']}")
    print(f"new candidate mention: {ARTIST_GROUP_ID} surface='artists' span={artist_start}:{artist_end}")
    for path, output in outputs.items():
        print(f"{path.relative_to(ROOT)}: {len(raw_files[path])} -> {len(output)} bytes; sha256={sha256(output)}")
    if not args.apply:
        print("dry-run only; all tables remain unchanged")
        return

    temp_paths: dict[Path, str] = {}
    try:
        for path, output in outputs.items():
            fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
            with os.fdopen(fd, "wb") as f:
                f.write(output)
                f.flush()
                os.fsync(f.fileno())
            temp_paths[path] = temp_name
        for path, backup in BACKUPS.items():
            shutil.copy2(path, backup)
        for path, temp_name in temp_paths.items():
            os.replace(temp_name, path)
        temp_paths.clear()
    finally:
        for temp_name in temp_paths.values():
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    print("applied; recovery backups:")
    for backup in BACKUPS.values():
        print(f"  {backup.relative_to(ROOT)}")
    for path, output in outputs.items():
        print(f"  {path.relative_to(ROOT)} sha256={sha256(output)}")


if __name__ == "__main__":
    main()
