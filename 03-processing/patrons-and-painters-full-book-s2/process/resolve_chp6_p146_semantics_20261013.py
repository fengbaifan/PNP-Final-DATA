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
SEC_I = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"
INTRO = ROOT / "02-sources/02-Markdown/06_CHP-6_intro.md"

EXPECTED_HASHES = {
    STATEMENTS: "cf570d972dacf08659fb4842c97e602861cf44d726522503949013fb3bd8f3a7",
    CANDIDATES: "ecdfcf43f119585fc7c3714561627b0f346e625a47b76bcb270b5b420120fe4c",
    MENTIONS: "4fae73c6a1d593a31615f5adc7840730c52ee4e4df054f36bc165a91f7b19b29",
    COVERAGE: "148b9215ac373f4d8a5a28614c6aebb56deb6e3f0a8580e4bcc941edb30414be",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp6-p146-semantic-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp6-p146-election-event-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp6-p146-election-event-20261013"),
    COVERAGE: COVERAGE.with_name("s2-coverage.csv.bak-s2-chp6-p146-semantic-20261013"),
}

TITLE_Q = "The printed chapter title frames chapter 6 as a decline of Roman patronage."
POUSSIN_QUOTE = (
    "N August 1645, a little more than a year after the death of Pope Urban VIII, Poussin "
    "Iwrote to his Parisian patron Chantelou, who was trying to buy some antique marbles, "
    "that ‘things in Rome have greatly changed under the present papacy and we no longer "
    "enjoy any special favour at court’.1"
)
FRENCH_QUOTE = (
    "But it was not only French interests that suffered with the election of the Hispanophil "
    "Giambattista Pamfili as Innocent X."
)
ARTS_QUOTE = (
    "But it was not only French interests that suffered with the election of the Hispanophil "
    "Giambattista Pamfili as Innocent X. The arts as a whole received a blow which had the "
    "most lasting consequences."
)
ARTS_ONLY_QUOTE = "The arts as a whole received a blow which had the most lasting consequences."
FACTORS_HEADING_QUOTE = "Many factors were involved, great and small:"
FACTORS = [
    ("st-chp6-p146-factor-european-balance", "cand-6245", "European balance of power"),
    ("st-chp6-p146-factor-family-ambition", "cand-6246", "political ambitions of a single family"),
    ("st-chp6-p146-factor-economic-collapse", "cand-6247", "economic collapse"),
    ("st-chp6-p146-factor-temperament", "cand-6248", "individual quirks of temperament"),
    ("st-chp6-p146-factor-plague", "cand-6249", "plague"),
    ("st-chp6-p146-factor-starvation", "cand-6250", "starvation"),
    ("st-chp6-p146-factor-sudden-death", "cand-6251", "sudden death"),
    ("st-chp6-p146-factor-fashion", "cand-6252", "changes of fashion"),
]
WAR_ONSET_QUOTE = (
    "The decline had already begun some three years earher with the outbreak of the War of Castro"
)
CASTRO_TOWN_QUOTE = "War of Castro, a little town belonging to the Duke of Parma"
CASTRO_TERRITORY_QUOTE = (
    "War of Castro, a little town belonging to the Duke of Parma but situated well within papal territory."
)
DISPUTE_QUOTE = (
    "A series of financial disputes with the Duke led to his excommunication and the rapid occupation of the town."
)
COALITION_QUOTE = (
    "But the campaign which had begun so well suddenly changed its nature when France, Tuscany, "
    "Venice and Modena banded together, either openly or in private, to put an end to what had "
    "now become an ambitious Barberini scheme to extend their private dominions."
)
TADDEO_QUOTE = "Don Taddeo showed his disastrous limitations as commander-in-chief;"
FOREIGN_TROOPS_QUOTE = "foreign troops once more marched on Rome"
PANIC_QUOTE = "and the,panic of a second 1527 swept through the city."
TAXES_QUOTE = (
    "New taxes were raised, private silver was confiscated. This was hardly the moment for artistic patronage."
)
PEACE_QUOTE = (
    "March 1644 a humiliating peace was signed, and, soon after, Urban VIII died amid the ' execration of his subjects.4"
)
STORMY_QUOTE = "The Conclave that followed was particularly stormy."
GUARDS_QUOTE = (
    "In Rome armed guards were called in to defend the principal palaces from roaming mobs, and clashes were frequent."
)
CIVIC_QUOTE = (
    "The civic authorities made a feeble attempt to take over responsibility, only to be overruled by the College of Cardinals."
)
INNOCENT_QUOTE = (
    "Innocent X, was inclined neither by race—he was a Roman, a nationality notorious to this day for its lack "
    "of interest in the arts—nor by his financial situation—wholly chaotic after twenty years of Barberini "
    "extravagance—nor yet by personal temperament to continue the sumptuous patronage that had distinguished "
    "the previous reign."
)
NEPHEW_QUOTE = "Only ambition remained; and here he faced a difficult problem. For he had only one nephew,"

NOTES = {
    "st-chp6-p146-note1-correspondance": ("intro", 8, "1 CorresponJance, p. 316."),
    "st-chp6-p146-note2-passeri-haskell": (
        "intro", 9, "2 Passeri, p. 301, gives a very vivid account of the situation. See also Haskell, 1959."
    ),
    "st-chp6-p146-note3-pastor": ("intro", 10, "3 Pastor, XIII, pp. 881-95."),
    "st-chp6-p146-note4-gigli": (
        "intro", 11, "4 For the effects of the war in Rome see Gigli, pp. 203-40."
    ),
}
BODY_QUOTES = {
    "st-chp6-title-frame": ("intro", 5, 5, "THE DECLINE OF ROMAN PATRONAGE"),
    "st-chp6-p146-poussin-letter": ("sec_i", 3, 4, POUSSIN_QUOTE),
    "st-chp6-p146-arts-election": ("sec_i", 4, 4, ARTS_QUOTE),
    "st-chp6-p146-multifactor-list": ("sec_i", 4, 4, FACTORS_HEADING_QUOTE),
    "st-chp6-p146-decline-war-onset": ("sec_i", 5, 6, WAR_ONSET_QUOTE),
    "st-chp6-p146-castro-dispute": ("sec_i", 6, 6, DISPUTE_QUOTE),
    "st-chp6-p146-castro-location": ("sec_i", 6, 6, CASTRO_TOWN_QUOTE),
    "st-chp6-p146-coalition": ("sec_i", 6, 6, COALITION_QUOTE),
    "st-chp6-p146-taddeo-command": ("sec_i", 6, 6, TADDEO_QUOTE),
    "st-chp6-p146-foreign-troops": ("sec_i", 6, 7, FOREIGN_TROOPS_QUOTE),
    "st-chp6-p146-1527-panic": ("sec_i", 7, 7, PANIC_QUOTE),
    "st-chp6-p146-taxes-and-patronage": ("sec_i", 7, 7, TAXES_QUOTE),
    "st-chp6-p146-1644-peace": ("sec_i", 8, 8, PEACE_QUOTE),
    "st-chp6-p146-urban-death": ("sec_i", 8, 8, PEACE_QUOTE),
    "st-chp6-p146-conclave-crisis": ("sec_i", 9, 9, STORMY_QUOTE),
    "st-chp6-p146-civic-authority": ("sec_i", 10, 10, CIVIC_QUOTE),
    "st-chp6-p146-innocent-patronage": ("sec_i", 11, 11, INNOCENT_QUOTE),
    "st-chp6-p146-only-nephew-partial": ("sec_i", 11, 11, NEPHEW_QUOTE),
}
EXPECTED_SEGMENTS = {
    "st-chp6-title-frame": "chp-6:06_CHP-6_intro:l3-5",
    **{
        sid: "chp-6:06_CHP-6_intro:l7-11"
        for sid in NOTES
    },
    **{
        sid: "chp-6:06_CHP-6_sec_i:l3-11"
        for sid in BODY_QUOTES
        if sid != "st-chp6-title-frame"
    },
}

FLAGS_AND_NOTES = {
    "st-chp6-title-frame": (
        False,
        "Editorial chapter-title framing, not an entity-to-entity or domain relation.",
    ),
    "st-chp6-p146-poussin-letter": (
        True,
        "The reported communication explicitly links Nicolas Poussin to Paul-Fréart de Chantelou. "
        "The quoted letter content remains attributed to Poussin; the first-person plural is not expanded to a named group.",
    ),
    "st-chp6-p146-arts-election": (
        True,
        "Haskell links the arts' lasting setback with the election of Innocent X. "
        "The statement preserves the author's broad assessment and does not independently verify causation.",
    ),
    "st-chp6-p146-multifactor-list": (
        False,
        "This records Haskell's framing that the change involved many factors; the listed factors are recorded as separate relation candidates below.",
    ),
    "st-chp6-p146-decline-war-onset": (
        True,
        "Haskell explicitly associates the beginning of the patronage decline with the outbreak of the War of Castro; the chronology remains approximate as worded.",
    ),
    "st-chp6-p146-castro-dispute": (
        True,
        "The author links financial disputes with the Duke to excommunication and occupation. "
        "The agent of excommunication and occupation is not named and is not inferred.",
    ),
    "st-chp6-p146-castro-location": (
        True,
        "The source states that Castro belonged to the Duke of Parma. This preserves a source-attributed territorial relation, not an independently aligned identity.",
    ),
    "st-chp6-p146-coalition": (
        True,
        "Haskell says the four political actors banded together against the Barberini scheme; formal treaty or permanent coalition status is not asserted.",
    ),
    "st-chp6-p146-taddeo-command": (
        False,
        "This is Haskell's evaluative assessment of Don Taddeo's limitations; the role phrase is retained as context and is not converted into a separate appointment relation.",
    ),
    "st-chp6-p146-foreign-troops": (
        True,
        "The source explicitly relates an unnamed troop group to its march toward Rome; no state or commander is identified.",
    ),
    "st-chp6-p146-1527-panic": (
        True,
        "Haskell compares the panic in Rome to a second 1527. The event candidate remains an interpretation for later identity review.",
    ),
    "st-chp6-p146-taxes-and-patronage": (
        True,
        "Haskell connects the crisis described in the passage with an unsuitable moment for artistic patronage. "
        "The tax and confiscation agents remain unspecified.",
    ),
    "st-chp6-p146-1644-peace": (
        True,
        "The source explicitly places the unnamed peace after the War of Castro; treaty name and signatories are not supplied here.",
    ),
    "st-chp6-p146-urban-death": (
        True,
        "The source explicitly places Urban VIII's death soon after the March 1644 peace. "
        "The phrase about subjects' execration remains Haskell's characterization.",
    ),
    "st-chp6-p146-conclave-crisis": (
        False,
        "This statement records Haskell's characterization of the conclave as stormy. "
        "The separate guards, mobs and clashes claim is recorded below.",
    ),
    "st-chp6-p146-civic-authority": (
        True,
        "The source explicitly states that the College of Cardinals overruled the civic authorities' attempted takeover of responsibility.",
    ),
    "st-chp6-p146-innocent-patronage": (
        True,
        "Haskell links Innocent X's inclination not to continue the previous reign's sumptuous patronage with the reasons he lists; these remain authorial assessments.",
    ),
    "st-chp6-p146-only-nephew-partial": (
        True,
        "The source frames Innocent X's dynastic problem around having only one nephew; the next source segment identifies him as Camillo.",
    ),
    "st-chp6-p146-note1-correspondance": (
        True,
        "Haskell's footnote explicitly cites the identified Poussin Correspondance edition. This records a bibliographic candidate and does not independently verify the quoted letter.",
    ),
    "st-chp6-p146-note2-passeri-haskell": (
        True,
        "Haskell's note explicitly cites Passeri at page 301. This records a bibliographic candidate and does not import claims from the cited work.",
    ),
    "st-chp6-p146-note3-pastor": (
        True,
        "Haskell's note explicitly cites Pastor, volume XIII. This records a bibliographic candidate and does not verify the cited account.",
    ),
    "st-chp6-p146-note4-gigli": (
        True,
        "Haskell's note explicitly cites Gigli, pages 203–240. The cited publication's exact title and edition remain unresolved.",
    ),
}

FACTOR_CLAIMS = {
    "cand-6245": "Haskell lists the European balance of power as one factor in the lasting change to the arts and patronage.",
    "cand-6246": "Haskell lists the political ambitions of a single family as one factor in the lasting change to the arts and patronage.",
    "cand-6247": "Haskell lists economic collapse as one factor in the lasting change to the arts and patronage.",
    "cand-6248": "Haskell lists individual quirks of temperament as one factor in the lasting change to the arts and patronage.",
    "cand-6249": "Haskell lists plague as one factor in the lasting change to the arts and patronage.",
    "cand-6250": "Haskell lists starvation as one factor in the lasting change to the arts and patronage.",
    "cand-6251": "Haskell lists sudden death as one factor in the lasting change to the arts and patronage.",
    "cand-6252": "Haskell lists changes of fashion as one factor in the lasting change to the arts and patronage.",
}
FACTOR_NOTE = (
    "This is an attributed factor link from Haskell's explanation; the passage does not quantify "
    "relative contribution or independently establish causal strength."
)
FOOTNOTE_KEYS_FOR_REMOVAL = {
    "footnote_markers", "footnote_link_status", "footnote_marker", "footnote_segment",
    "footnote_segment_id", "footnote_source_line", "footnote_source_lines", "footnote_refs",
    "footnote_statement_ids", "footnote_text_pending", "footnote_body_link_status", "footnote_pending",
}


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
    if not lines or not lines[0].startswith(b"\xef\xbb\xbf"):
        raise SystemExit("coverage CSV BOM preflight failed")
    header = next(csv.reader([lines[0].decode("utf-8-sig")]))
    segment_idx = header.index("segment_id")
    note_idx = header.index("note")
    expected_old = {
        "chp-6:06_CHP-6_intro:l7-11": (
            "四条章首页脚注均已登记为引用定位并链接至规范正文L3-L11的相关断言；"
            "保留书目身份待索引/书目S2核对。L8 CorresponJance按印本校为Correspondance，不改S0。"
        ),
        "chp-6:06_CHP-6_sec_i:l3-11": (
            "按印刷页146逐行处理；四个脚注挂点已回链。L11唯一侄辈句由页147 L14点名Camillo，跨页续接已关闭。"
        ),
    }
    updated = {
        "chp-6:06_CHP-6_intro:l7-11": (
            "四个脚注标记对应五条《赞助人与画家》到archive的引用候选（注2拆分Passeri与Haskell 1959）；"
            "引文关系不验证被引内容。书目匹配状态见各候选；L8 CorresponJance按印本校为Correspondance，S0不改。"
        ),
        "chp-6:06_CHP-6_sec_i:l3-11": (
            "印刷页146正文已按关系与非关系语义分类；选举影响、八项解释因素、Castro领属/辖域、"
            "枢机会议评价与治安陈述分别记录。L11唯一侄辈句由页147 L14点名Camillo，跨页续接已关闭。"
        ),
    }
    seen: set[str] = set()
    out: list[bytes] = [lines[0]]
    for raw in lines[1:]:
        text = raw.decode("utf-8")
        row = next(csv.reader([text]))
        segment_id = row[segment_idx]
        if segment_id in expected_old:
            if segment_id in seen or row[note_idx] != expected_old[segment_id]:
                raise SystemExit(f"coverage row preflight failed: {segment_id}")
            seen.add(segment_id)
            row[note_idx] = updated[segment_id]
            buf = io.StringIO(newline="")
            csv.writer(buf, lineterminator="\r\n").writerow(row)
            out.append(buf.getvalue().encode("utf-8"))
        else:
            out.append(raw)
    if seen != set(expected_old):
        raise SystemExit(f"coverage rows missing: {sorted(set(expected_old) - seen)}")
    return b"".join(out)


def make_body_statement(
    statement_id: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    quote: str,
    qualifiers: dict,
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": "chp-6:06_CHP-6_sec_i:l3-11",
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
    }


def make_citation_statement(
    statement_id: str,
    object_id: str,
    claim: str,
    quote: str,
    locator: str,
    mentioned: list[str],
    relation_note: str,
    note2_q: dict,
) -> dict:
    q = deepcopy(note2_q)
    q.update(
        {
            "source_line_start": 9,
            "source_line_end": 9,
            "printed_page": "146",
            "pdf_physical_page": 1,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "authorial footnote citation",
            "qualification": "The note identifies a citation target; the cited publication has not been independently consulted here.",
            "mentioned_candidate_ids": mentioned,
            "citation_locator": locator,
            "footnote_marker": 2,
            "footnote_segment": "chp-6:06_CHP-6_intro:l7-11",
            "footnote_body_link_status": "linked",
            "linked_body_statement_ids": ["st-chp6-p146-multifactor-list"] + [x[0] for x in FACTORS],
            "related_segment": "chp-6:06_CHP-6_sec_i:l3-11",
            "related_source_lines": [4],
            "relation_candidate": True,
            "relation_candidate_note": relation_note,
        }
    )
    return {
        "statement_id": statement_id,
        "segment_id": "chp-6:06_CHP-6_intro:l7-11",
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": object_id,
        "predicate": "cites",
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/06_CHP-6_intro.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve the printed-page 146 S2 statements.")
    parser.add_argument("--apply", action="store_true", help="write after guarded dry-run checks pass")
    args = parser.parse_args()

    raw_files = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(raw_files[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: expected {expected}, got {actual}")
    for backup in BACKUPS.values():
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing to overwrite: {backup}")

    sec_lines = SEC_I.read_text(encoding="utf-8").splitlines()
    intro_lines = INTRO.read_text(encoding="utf-8").splitlines()
    source_texts = {"sec_i": sec_lines, "intro": intro_lines}
    for sid, (source_name, first, last, quote) in BODY_QUOTES.items():
        source_span = " ".join(source_texts[source_name][first - 1:last])
        if normalize(quote) not in normalize(source_span):
            raise SystemExit(f"source quote preflight failed: {sid}")
    for sid, (source_name, line_no, quote) in NOTES.items():
        source_span = source_texts[source_name][line_no - 1]
        if normalize(quote) not in normalize(source_span):
            raise SystemExit(f"footnote quote preflight failed: {sid}")
    new_quote_anchors = {
        "st-chp6-p146-french-interests-election": (4, FRENCH_QUOTE),
        "st-chp6-p146-castro-papal-territory": (6, CASTRO_TERRITORY_QUOTE),
        "st-chp6-p146-conclave-guards-mobs": (9, GUARDS_QUOTE),
        **{sid: (4, phrase) for sid, _, phrase in FACTORS},
    }
    for sid, (line_no, quote) in new_quote_anchors.items():
        source_span = sec_lines[line_no - 1]
        if normalize(quote) not in normalize(source_span):
            raise SystemExit(f"new body source quote preflight failed: {sid}")
    if normalize("See also Haskell, 1959.") not in normalize(intro_lines[8]):
        raise SystemExit("Haskell 1959 citation anchor mismatch")

    statements_text = raw_files[STATEMENTS].decode("utf-8")
    rows = [json.loads(line) for line in statements_text.splitlines() if line.strip()]
    by_id: dict[str, dict] = {}
    for row in rows:
        sid = row.get("statement_id")
        if sid in by_id:
            raise SystemExit(f"duplicate statement ID already present: {sid}")
        by_id[sid] = row
    if set(FLAGS_AND_NOTES) != set(BODY_QUOTES) | set(NOTES):
        raise SystemExit("classification/quote target sets do not match")
    if len(set(BODY_QUOTES) | set(NOTES)) != 22:
        raise SystemExit("unexpected printed-page 146 base statement count")
    target_ids = set(BODY_QUOTES) | set(NOTES)
    for sid in target_ids:
        row = by_id.get(sid)
        if row is None:
            raise SystemExit(f"target statement missing: {sid}")
        if row.get("segment_id") != EXPECTED_SEGMENTS[sid] or row.get("origin") != "book":
            raise SystemExit(f"statement provenance mismatch: {sid}")
        if (row.get("qualifiers") or {}).get("relation_candidate") is not None:
            raise SystemExit(f"statement already classified: {sid}")
    new_ids = {
        "st-chp6-p146-french-interests-election",
        "st-chp6-p146-castro-papal-territory",
        "st-chp6-p146-conclave-guards-mobs",
        "st-chp6-p146-note2-haskell-1959-citation",
        *[sid for sid, _, _ in FACTORS],
    }
    if new_ids & set(by_id):
        raise SystemExit(f"new statement ID already present: {sorted(new_ids & set(by_id))}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidate_reader = csv.DictReader(f)
        candidate_fields = candidate_reader.fieldnames or []
        candidates = {r["candidate_id"]: r for r in candidate_reader}
    required_types = {
        "cand-2962": "archive",
        "cand-4634": "archive",
        "cand-6240": "archive",
        "cand-6241": "archive",
        "cand-4237": "archive",
        "cand-6269": "archive",
        "cand-6243": "",
        "cand-6244": "term",
        "cand-6267": "term",
        "cand-1831": "institution",
        "cand-6257": "place",
        "cand-6260": "event",
        "cand-6261": "",
        "cand-6262": "",
        "cand-1819": "person",
    }
    for cid, expected_type in required_types.items():
        candidate = candidates.get(cid)
        if candidate is None or candidate.get("suggested_type") != expected_type:
            raise SystemExit(f"candidate preflight failed: {cid} must exist with type {expected_type!r}")
    if "cand-11955" in candidates:
        raise SystemExit("new election event candidate ID already exists")

    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mention_reader = csv.DictReader(f)
        mention_fields = mention_reader.fieldnames or []
        mention_rows = list(mention_reader)
    if any(m["mention_id"] == "m-chp6-p146-062" for m in mention_rows):
        raise SystemExit("new election event mention ID already exists")
    if not any(
        m["segment_id"] == "chp-6:06_CHP-6_sec_i:l3-11"
        and m["candidate_id"] == "cand-6243"
        and m["surface_form"] == "French interests"
        and m["start_char"] == "311"
        and m["end_char"] == "327"
        for m in mention_rows
    ):
        raise SystemExit("existing French-interests mention anchor mismatch")
    segment_text = "\n".join(sec_lines[2:11])
    election_at = segment_text.find("election of the Hispanophil")
    if election_at < 0 or segment_text[election_at:election_at + 8] != "election":
        raise SystemExit("election event mention surface mismatch")
    election_start, election_end = election_at, election_at + 8
    for m in mention_rows:
        if m["segment_id"] != "chp-6:06_CHP-6_sec_i:l3-11":
            continue
        start, end = int(m["start_char"]), int(m["end_char"])
        if election_start < end and start < election_end:
            raise SystemExit(f"new election mention overlaps existing mention {m['mention_id']}")
    if election_start != 351 or election_end != 359:
        raise SystemExit(f"unexpected election mention offsets: {election_start}:{election_end}")

    changed: dict[str, dict] = {}
    for sid, (source_name, first, last, quote) in BODY_QUOTES.items():
        row = by_id[sid]
        q = row["qualifiers"]
        if q.get("source_line_start") != first or q.get("source_line_end") != last:
            raise SystemExit(f"source line anchor mismatch: {sid}")
        if q.get("printed_page") != "146":
            raise SystemExit(f"printed page mismatch: {sid}")
        before = deepcopy(row)
        row["original_quote"] = quote
        if sid == "st-chp6-p146-poussin-letter":
            q["source_line_end"] = 4
        elif sid == "st-chp6-p146-decline-war-onset":
            q["source_line_end"] = 6
        elif sid == "st-chp6-p146-foreign-troops":
            q["source_line_end"] = 7
        flag, flag_note = FLAGS_AND_NOTES[sid]
        q["relation_candidate"] = flag
        q["relation_candidate_note"] = flag_note
        changed[sid] = before

    for sid, (source_name, line_no, quote) in NOTES.items():
        row = by_id[sid]
        q = row["qualifiers"]
        expected_line = line_no
        if q.get("source_line_start") != expected_line or q.get("source_line_end") != expected_line:
            raise SystemExit(f"footnote line anchor mismatch: {sid}")
        if q.get("printed_page") != "146":
            raise SystemExit(f"footnote page mismatch: {sid}")
        before = deepcopy(row)
        row["original_quote"] = quote
        q["relation_candidate"] = FLAGS_AND_NOTES[sid][0]
        q["relation_candidate_note"] = FLAGS_AND_NOTES[sid][1]
        row["subject_candidate_id"] = "cand-2962"
        row["predicate"] = "cites"
        if sid == "st-chp6-p146-note1-correspondance":
            row["object_candidate_id"] = "cand-4634"
            q["claim"] = "Haskell's footnote cites the Poussin Correspondance edition, page 316, for the letter quoted in the body."
            q["qualification"] = "The bibliography identifies the cited edition; its text has not been independently consulted here."
            q["citation_locator"] = "p. 316"
            q["mentioned_candidate_ids"] = ["cand-2962", "cand-4634"]
        elif sid == "st-chp6-p146-note2-passeri-haskell":
            row["object_candidate_id"] = "cand-6241"
            q["claim"] = "Haskell's note cites Passeri's work at page 301 for an account of the situation."
            q["qualification"] = "The note identifies Passeri and page 301; the work title and contents are not independently verified from this citation."
            q["citation_locator"] = "p. 301"
            q["mentioned_candidate_ids"] = ["cand-2962", "cand-1856", "cand-6241"]
            factor_links = ["st-chp6-p146-multifactor-list"] + [x[0] for x in FACTORS]
            q["linked_body_statement_ids"] = factor_links
        elif sid == "st-chp6-p146-note3-pastor":
            row["object_candidate_id"] = "cand-4237"
            q["claim"] = "Haskell's note cites Pastor, volume XIII, pages 881–895, in connection with the War of Castro."
            q["qualification"] = "Citation locator only; the exact edition remains unspecified and the cited pages have not been independently consulted."
            q["citation_locator"] = "vol. XIII, pp. 881–895"
            q["mentioned_candidate_ids"] = ["cand-2962", "cand-4237"]
        elif sid == "st-chp6-p146-note4-gigli":
            row["object_candidate_id"] = "cand-6269"
            q["claim"] = "Haskell's note directs readers to Gigli, pages 203–240, for the effects of the war in Rome."
            q["qualification"] = "The exact title and edition remain unresolved; the cited pages have not been independently consulted."
            q["citation_locator"] = "pp. 203–240"
            q["mentioned_candidate_ids"] = ["cand-2962", "cand-1168", "cand-6269"]
        changed[sid] = before

    arts = by_id["st-chp6-p146-arts-election"]
    arts_q = arts["qualifiers"]
    arts["subject_candidate_id"] = "cand-6244"
    arts["object_candidate_id"] = "cand-11955"
    arts["predicate"] = "arts-affected-by-papal-election"
    arts_q["claim"] = "Haskell says the arts as a whole received a lasting blow in connection with the election of Giambattista Pamfili as Innocent X."
    arts_q["qualification"] = "This preserves Haskell's broad historical assessment; the passage does not independently establish the strength or mechanism of causation."
    arts_q["mentioned_candidate_ids"] = ["cand-6244", "cand-11955", "cand-1819"]
    for key in FOOTNOTE_KEYS_FOR_REMOVAL:
        arts_q.pop(key, None)

    meta = by_id["st-chp6-p146-multifactor-list"]
    meta_q = meta["qualifiers"]
    meta["predicate"] = "many-factors-described"
    meta_q["claim"] = "Haskell describes the lasting change to the arts as involving many factors, large and small."
    meta_q["qualification"] = "This records the author's framing of the list; each named factor is separately linked to the change below."
    meta_q["mentioned_candidate_ids"] = ["cand-6267"]

    castro = by_id["st-chp6-p146-castro-location"]
    castro["predicate"] = "town-belonged-to-duke-of-parma"
    castro["qualifiers"]["claim"] = "Haskell describes Castro as a small town belonging to the Duke of Parma."
    castro["qualifiers"]["qualification"] = "The source states ducal belonging; the Duke's identity remains an S3 alignment matter."
    castro["qualifiers"]["mentioned_candidate_ids"] = ["cand-6257", "cand-0996"]

    stormy = by_id["st-chp6-p146-conclave-crisis"]
    stormy["predicate"] = "conclave-characterized-as-stormy"
    stormy["subject_candidate_id"] = "cand-6260"
    stormy["object_candidate_id"] = None
    stormy["qualifiers"]["claim"] = "Haskell characterizes the conclave following Urban VIII's death as particularly stormy."
    stormy["qualifiers"]["mentioned_candidate_ids"] = ["cand-6260"]

    urban = by_id["st-chp6-p146-urban-death"]
    urban["object_candidate_id"] = "cand-6259"
    urban["qualifiers"]["mentioned_candidate_ids"] = ["cand-0209", "cand-6259"]

    note2 = by_id["st-chp6-p146-note2-passeri-haskell"]
    note2_q = note2["qualifiers"]
    note2_q["linked_body_statement_ids"] = ["st-chp6-p146-multifactor-list"] + [x[0] for x in FACTORS]

    event_candidate = {
        "candidate_id": "cand-11955",
        "index_entry_id": "",
        "canonical_name": "Election of Giambattista Pamfili as Innocent X",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The passage names the election of Giambattista Pamfili as Innocent X as the change accompanying effects on French interests and the arts. It gives no exact election date or independent account; identity alignment remains for S3.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-6:06_CHP-6_sec_i:l3-11#L4",
    }
    election_mention = {
        "mention_id": "m-chp6-p146-062",
        "segment_id": "chp-6:06_CHP-6_sec_i:l3-11",
        "candidate_id": "cand-11955",
        "surface_form": "election",
        "start_char": str(election_start),
        "end_char": str(election_end),
        "note": "Event mention in the phrase election of Giambattista Pamfili as Innocent X; date and event identity details remain source-limited.",
    }

    election_q = {
        "source_line_start": 4,
        "source_line_end": 4,
        "printed_page": "146",
        "pdf_physical_page": 1,
        "claim": "Haskell says French interests suffered in connection with the election of Giambattista Pamfili as Innocent X.",
        "speaker": "Haskell",
        "text_layer": "authorial historical interpretation",
        "qualification": "The actors composing French interests are unspecified; the wording links the setback with the election but does not state a mechanism.",
        "mentioned_candidate_ids": ["cand-6243", "cand-11955", "cand-1819"],
        "relation_candidate": True,
        "relation_candidate_note": "Haskell explicitly links the suffering of French interests with the election of Innocent X; the collective actors and causal mechanism remain unspecified.",
    }
    french_statement = make_body_statement(
        "st-chp6-p146-french-interests-election",
        "cand-6243",
        "cand-11955",
        "french-interests-suffered-with-papal-election",
        FRENCH_QUOTE,
        election_q,
    )

    territory_q = deepcopy(castro["qualifiers"])
    territory_q.update(
        {
            "claim": "Haskell says Castro lay well within papal territory.",
            "text_layer": "authorial geographical description",
            "qualification": "The source distinguishes the town's ducal belonging from its location within papal territory; the place and territorial identity candidates remain for S3.",
            "mentioned_candidate_ids": ["cand-6257", "cand-1831"],
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly relates Castro's location to papal territory, separately from the Duke's territorial claim.",
        }
    )
    territory_statement = make_body_statement(
        "st-chp6-p146-castro-papal-territory",
        "cand-6257",
        "cand-1831",
        "located-within-papal-territory",
        CASTRO_TERRITORY_QUOTE,
        territory_q,
    )

    guards_q = {
        "source_line_start": 9,
        "source_line_end": 9,
        "printed_page": "146",
        "pdf_physical_page": 1,
        "claim": "Haskell says armed guards in Rome were called to defend the principal palaces against roaming mobs, and clashes were frequent.",
        "speaker": "Haskell",
        "text_layer": "authorial historical narrative",
        "qualification": "The palaces, guards, mobs and clash participants are not identified beyond these generic descriptions.",
        "mentioned_candidate_ids": ["cand-6260", "cand-4490", "cand-6261", "cand-6262"],
        "relation_candidate": True,
        "relation_candidate_note": "The source reports armed guards defending palaces against roaming mobs and frequent clashes; no specific guards, buildings or participants are inferred.",
    }
    guards_statement = make_body_statement(
        "st-chp6-p146-conclave-guards-mobs",
        "cand-6261",
        "cand-6262",
        "guards-defended-palaces-against-mobs",
        GUARDS_QUOTE,
        guards_q,
    )

    citation_note = (
        "Haskell's note explicitly cites this archive. This records a bibliographic candidate and does not verify the cited content."
    )
    haskell_1959_statement = make_citation_statement(
        "st-chp6-p146-note2-haskell-1959-citation",
        "cand-6240",
        "Haskell's note also cites his 1959 article, identified in the bibliography as The market for Italian art in the 17th century.",
        "See also Haskell, 1959.",
        "1959; no page specified in this note",
        ["cand-2962", "cand-6240"],
        "The note cites Haskell's 1959 publication, identified by its bibliography entry; that article has not been independently consulted.",
        note2_q,
    )
    note2["qualifiers"]["linked_body_statement_ids"] = ["st-chp6-p146-multifactor-list"] + [x[0] for x in FACTORS]

    factor_base = deepcopy(meta_q)
    factor_statements = []
    for sid, candidate_id, phrase in FACTORS:
        q = deepcopy(factor_base)
        q["claim"] = FACTOR_CLAIMS[candidate_id]
        q["mentioned_candidate_ids"] = [candidate_id, "cand-6267"]
        q["relation_candidate"] = True
        q["relation_candidate_note"] = FACTOR_NOTE
        factor_statements.append(
            make_body_statement(
                sid,
                candidate_id,
                "cand-6267",
                "listed-as-factor-in-artistic-patronage-change",
                phrase,
                q,
            )
        )

    new_rows = {
        "st-chp6-p146-arts-election": [french_statement],
        "st-chp6-p146-multifactor-list": factor_statements,
        "st-chp6-p146-castro-location": [territory_statement],
        "st-chp6-p146-conclave-crisis": [guards_statement],
        "st-chp6-p146-note2-passeri-haskell": [haskell_1959_statement],
    }
    final_rows: list[dict] = []
    for row in rows:
        final_rows.append(row)
        final_rows.extend(new_rows.get(row.get("statement_id"), []))
    if len(final_rows) != len(rows) + len(new_ids):
        raise SystemExit("statement output count mismatch")
    if {r["statement_id"] for r in final_rows} != set(by_id) | new_ids:
        raise SystemExit("statement output ID set mismatch")
    output_lines: list[str] = []
    for raw_line in statements_text.splitlines():
        raw_row = json.loads(raw_line)
        sid = raw_row.get("statement_id")
        if sid in target_ids:
            output_lines.append(json.dumps(by_id[sid], ensure_ascii=False, separators=(",", ":")))
        else:
            output_lines.append(raw_line)
        output_lines.extend(
            json.dumps(extra, ensure_ascii=False, separators=(",", ":"))
            for extra in new_rows.get(sid, [])
        )
    statements_output = ("\n".join(output_lines) + "\n").encode("utf-8")

    candidates_output = append_csv_row(raw_files[CANDIDATES], candidate_fields, event_candidate)
    mentions_output = append_csv_row(raw_files[MENTIONS], mention_fields, election_mention)
    coverage_output = update_coverage(raw_files[COVERAGE])

    outputs = {
        STATEMENTS: statements_output,
        CANDIDATES: candidates_output,
        MENTIONS: mentions_output,
        COVERAGE: coverage_output,
    }
    print(
        "preflight passed: base_statements=22 added_statements=12 "
        "added_candidates=1 added_mentions=1"
    )
    print("classifications: relation_candidate=true=30 false=4 unset=0 for the processed p.146 statements")
    print("statement changes:")
    for sid in sorted(target_ids):
        row = by_id[sid]
        q = row["qualifiers"]
        print(
            f"  {sid}: relation_candidate={q['relation_candidate']} "
            f"predicate={row['predicate']} quote={normalize(row['original_quote'])[:115]}"
        )
    print("new statements:")
    for sid in sorted(new_ids):
        row = next(r for r in final_rows if r["statement_id"] == sid)
        print(f"  {sid}: {row['predicate']} {row['subject_candidate_id']} -> {row['object_candidate_id']}")
    for path, output in outputs.items():
        print(f"  {path.relative_to(ROOT)}: {len(raw_files[path])} -> {len(output)} bytes; sha256={sha256(output)}")

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
