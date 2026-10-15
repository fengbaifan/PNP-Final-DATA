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
    STATEMENTS: "cdc3dd4930d131872655e382b81100989e9a91086f619206835e4291594d308e",
    CANDIDATES: "7b316b6b610246b3f58635e6a122c902fc8a71b2ee5ce361feb87475b9f61dde",
    MENTIONS: "0db26a9146f1d34951f004a5b3c7215a1f93391cfdefa48436960da2c1dbc47e",
    COVERAGE: "80f7fe65de4dbe54e962b2136a4ea07ff7e278388536a28e3135c1b4b44a6b27",
}
SOURCE_SHA256 = "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d"
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp6-p148-semantic-20261013"),
    COVERAGE: COVERAGE.with_name("s2-coverage.csv.bak-s2-chp6-p148-semantic-20261013"),
}
SEGMENT = "chp-6:06_CHP-6_sec_i:l26-36"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"

QUOTES = {
    "st-chp6-p148-algardi-builds-camillo-villa": (
        34, 35, "During the course of it he had been responsible for the construction by Algardi of one of the most magnificent of all Roman villas."
    ),
    "st-chp6-p148-algardi-bust-of-donna-olimpia": (30, 31, "busts of Innocent and Donna Olimpia"),
    "st-chp6-p148-algardi-bust-of-innocent": (30, 30, "busts of Innocent"),
    "st-chp6-p148-algardi-classical-manner": (
        31, 31, "In all these he moved away from the warmth and vigour typical of Bernini and adopted a colder, more classical manner"
    ),
    "st-chp6-p148-algardi-constructs-papal-family-villa": (
        31, 31, "in the construction of a villa for the Pope’s family"
    ),
    "st-chp6-p148-algardi-st-peters-commissions": (
        31, 31, "was given vital commissions in St Peter’s"
    ),
    "st-chp6-p148-artistic-life-revival-partial": (
        36, 36, "and some of the most beautiful and familiar achievements of the Roman Baroque"
    ),
    "st-chp6-p148-astalli-assigned-papal-palace": (
        33, 33, "The palace itself had been assigned to yet another substitute for a true papal nephew, Camillo Astalli"
    ),
    "st-chp6-p148-astalli-relation-to-olimpia": (
        33, 34, "Camillo Astalli, inevitably a relation of Donna Olimpia"
    ),
    "st-chp6-p148-astalli-substitute-nephew": (
        33, 33, "substitute for a true papal nephew, Camillo Astalli"
    ),
    "st-chp6-p148-astalli-uses-pamfili-name": (
        34, 34, "who added to the general confusion by calling himself Pamfili"
    ),
    "st-chp6-p148-bernini-replaced-by-algardi": (
        30, 30, "Bernini also lost his position as the most favoured sculptor of the day and was replaced by Alessandro Algardi"
    ),
    "st-chp6-p148-bernini-returns-to-favour": (
        31, 31, "In fact, however, Bernini’s achievements and reputation were too great for him to be neglected for long"
    ),
    "st-chp6-p148-borromini-preservation-constraint": (
        28, 29, "Borromini, the most daring of Baroque architects, was told to preserve the essential structure of the old\n' basilica"
    ),
    "st-chp6-p148-camillo-builds-palace": (
        36, 36, "now set about building a palace for himself opposite the Collegio Romano"
    ),
    "st-chp6-p148-camillo-employs-antonio-del-grande": (
        36, 36, "for which he employed Antonio del Grande"
    ),
    "st-chp6-p148-camillo-exile-characterization": (
        34, 34, "His ‘exile’ had not been very arduous or painful."
    ),
    "st-chp6-p148-camillo-fills-and-decorates-villa": (
        35, 35, "This he filled with antiquities and had lavishly decorated."
    ),
    "st-chp6-p148-camillo-other-projects": (
        36, 36, "and he also took in hand a number of other projects, both public and private."
    ),
    "st-chp6-p148-camillo-return-to-rome": (
        34, 34, "Prince Pamfili finally returned to Rome"
    ),
    "st-chp6-p148-cortona-choice-and-camillo-pamfili": (
        34, 34, "But the actual choice ofPietro da Cortona may, perhaps, reflect the reviving fortunes of the authentic Prince CamiUo Pamfili"
    ),
    "st-chp6-p148-cortona-first-commission": (
        33, 33, "It was not until the end of 1651, seven years after the change of papacy, that Pietro da Cortona was given his first official commission"
    ),
    "st-chp6-p148-cortona-palace-gallery-commission": (
        33, 33, "to fresco the ceiling of the gallery in the papal palace in the Piazza Navona"
    ),
    "st-chp6-p148-financial-ceiling-constraint": (
        29, 29, "the financial troubles which afflicted Innocent’s reign made it impossible for him to replace the sixteenth-century wooden ceiling with the vault that he had planned.1"
    ),
    "st-chp6-p148-lateran-frescoes-destroyed": (
        27, 28, "replaces frescoes by Gentile da Fabriano and\nPisanello destroyed during the rebuilding."
    ),
    "st-chp6-p148-lateran-interior-and-ornament": (
        27, 28, "These will not at once be apparent to the visitor struck by the dazzling white interior of the Lateran basilica and the fantasy of its ornamentation which, as he will subsequently learn, replaces frescoes by Gentile da Fabriano and\nPisanello destroyed during the rebuilding."
    ),
    "st-chp6-p148-reactionary-continuation": (
        27, 27, "character, as were most of those created under Innocent’s auspices—the family palace because of Girolamo Rainaldi’s age and limitations, the church because of the inhibiting instructions given to Borromini."
    ),
}

FALSE_NOTE = (
    "This is Haskell’s source-attributed assessment or identity statement; it does not assert a relation between the represented entities."
)
NEW_IDS = {
    "st-chp6-p148-algardi-constructs-camillo-villa",
    "st-chp6-p148-algardi-manner-fits-forties",
    "st-chp6-p148-bernini-fountain-restores-favour",
    "st-chp6-p148-innocent-piazza-navona-patronage-centre",
    "st-chp6-p148-borromini-applies-gifts-to-decoration",
    "st-chp6-p148-camillo-artistic-interest",
    "st-chp6-p148-pope-receives-camillo-1651",
    "st-chp6-p148-camillo-decorates-villa",
    "st-chp6-p148-pamfili-palace-rainaldi-limitations",
    "st-chp6-p148-lateran-instructions-limit-borromini",
    "st-chp6-p148-artistic-life-revived-after-camillo-return",
}
OLD_ANCHORS = {
    "st-chp6-p148-bernini-returns-to-favour": (31, 32),
    "st-chp6-p148-camillo-builds-palace": (35, 36),
    "st-chp6-p148-lateran-interior-and-ornament": (27, 27),
}
NOTE2_ID = "st-chp6-notes-l123-p148-n2"
OLD_FOUNTAIN_BODY_ID = "st-chp6-p148-bernini-returns-to-favour"
NEW_FOUNTAIN_BODY_ID = "st-chp6-p148-bernini-fountain-restores-favour"
NOTE2_LINKS = [NEW_FOUNTAIN_BODY_ID]
OLD_COVERAGE_NOTE = (
    "按印刷页148迁移；关闭页147 L24→本段L27的reactionary续接，并记录本段L36至下一段L39的Baroque成就句partial。"
    "脚注1、2待L120-157注释段迁移后回链。OCR差异记过程，不改S0。"
)
NEW_COVERAGE_NOTE = (
    "印刷页148正文27条原statement全部分类，拆分委托者/建造者、创作行动、风格判断及独立接收事实，新增11条statement。"
    "p.147 reactionary句由本段L27闭合；本段L36艺术成就分句由p.149 L39闭合。页图校读只记S2；脚注1、2已回链。"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def update_coverage(data: bytes) -> bytes:
    lines = data.splitlines(keepends=True)
    header = next(csv.reader([lines[0].decode("utf-8-sig")]))
    segment_idx, note_idx = header.index("segment_id"), header.index("note")
    seen = False
    out = [lines[0]]
    for raw in lines[1:]:
        row = next(csv.reader([raw.decode("utf-8")]))
        if row[segment_idx] == SEGMENT:
            if seen or row[note_idx] != OLD_COVERAGE_NOTE:
                raise SystemExit("p.148 coverage row preflight failed")
            seen = True
            row[note_idx] = NEW_COVERAGE_NOTE
            buf = io.StringIO(newline="")
            csv.writer(buf, lineterminator="\r\n").writerow(row)
            out.append(buf.getvalue().encode("utf-8"))
        else:
            out.append(raw)
    if not seen:
        raise SystemExit("p.148 coverage row not found")
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
            "printed_page": "148",
            "pdf_physical_page": 3,
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
    parser = argparse.ArgumentParser(description="Resolve the p. 148 body segment at S2.")
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

    statements_text = raw_files[STATEMENTS].decode("utf-8")
    rows = [json.loads(line) for line in statements_text.splitlines() if line.strip()]
    by_id: dict[str, dict] = {}
    for row in rows:
        sid = row["statement_id"]
        if sid in by_id:
            raise SystemExit(f"duplicate statement ID: {sid}")
        by_id[sid] = row
    if len(QUOTES) != 27 or set(QUOTES) & NEW_IDS:
        raise SystemExit("p.148 statement target or addition-ID declaration mismatch")
    for sid, (first, last, _) in QUOTES.items():
        row = by_id.get(sid)
        if row is None or row.get("segment_id") != SEGMENT or row.get("source_file") != SOURCE_FILE:
            raise SystemExit(f"target provenance mismatch: {sid}")
        q = row.get("qualifiers") or {}
        if q.get("relation_candidate") is not None:
            raise SystemExit(f"statement already classified: {sid}")
        if q.get("printed_page") != "148":
            raise SystemExit(f"printed page mismatch: {sid}")
        old_anchor = (q.get("source_line_start"), q.get("source_line_end"))
        if old_anchor != OLD_ANCHORS.get(sid, (first, last)):
            raise SystemExit(f"source line anchor mismatch: {sid}")
    if set(by_id) & NEW_IDS:
        raise SystemExit(f"new statement IDs already exist: {sorted(set(by_id) & NEW_IDS)}")

    note2 = by_id.get(NOTE2_ID)
    if note2 is None:
        raise SystemExit("p.148 footnote 2 statement missing")
    nq = note2.get("qualifiers") or {}
    if nq.get("linked_body_statement_ids") != [OLD_FOUNTAIN_BODY_ID] or nq.get("citation_body_statement_ids") != [OLD_FOUNTAIN_BODY_ID]:
        raise SystemExit("p.148 footnote 2 backlink preflight failed")
    previous_page_continuation = by_id.get("st-chp6-p147-major-works-reactionary-partial")
    if not previous_page_continuation or previous_page_continuation["qualifiers"].get("continuation_resolved_by_statement_id") != "st-chp6-p148-reactionary-continuation":
        raise SystemExit("p.147 reactionary continuation backlink preflight failed")
    later_page_statement = by_id.get("st-chp6-p149-artistic-achievements-identified")
    if not later_page_statement or later_page_statement["qualifiers"].get("continuation_source_segment_id") != SEGMENT:
        raise SystemExit("p.149 artistic-achievements continuation preflight failed")

    for sid, (first, last, quote) in QUOTES.items():
        row = by_id[sid]
        q = row["qualifiers"]
        row["original_quote"] = quote
        q["source_line_start"] = first
        q["source_line_end"] = last
        q["relation_candidate"] = None  # assigned explicitly below

    def decide(sid: str, is_relation: bool, note: str) -> None:
        q = by_id[sid]["qualifiers"]
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note

    decide("st-chp6-p148-algardi-builds-camillo-villa", True, "Haskell says Camillo was responsible for construction of the villa by Algardi; the builder and responsible patron are separated into two candidates.")
    decide("st-chp6-p148-algardi-bust-of-donna-olimpia", True, "The source explicitly reports an Algardi bust of Donna Olimpia; the index subentry supplies the provisional work candidate.")
    decide("st-chp6-p148-algardi-bust-of-innocent", True, "The source explicitly reports an Algardi bust of Innocent X; the index subentry supplies the provisional work candidate.")
    decide("st-chp6-p148-algardi-classical-manner", True, "This preserves Haskell's explicit stylistic comparison between Algardi and Bernini, with its authorial framing.")
    decide("st-chp6-p148-algardi-constructs-papal-family-villa", True, "Haskell reports that Algardi was commissioned in construction of a Pope-family villa; cand-1817 is a provisional index candidate, and identity with Camillo's villa remains for S3 alignment.")
    decide("st-chp6-p148-algardi-st-peters-commissions", True, "The source explicitly reports important commissions for Algardi at St Peter's, without naming the individual works.")
    decide("st-chp6-p148-artistic-life-revival-partial", True, "This is the source-attributed relation between Camillo's return and the creation of notable Roman Baroque achievements; the sentence closes on p. 149.")
    decide("st-chp6-p148-astalli-assigned-papal-palace", True, "The source explicitly says the Piazza Navona palace was assigned to Camillo Astalli; the assigning actor is not named.")
    decide("st-chp6-p148-astalli-relation-to-olimpia", True, "Haskell explicitly calls Camillo Astalli a relation of Donna Olimpia but does not specify the kinship.")
    decide("st-chp6-p148-astalli-substitute-nephew", True, "This preserves Haskell's dynastic characterization of Astalli as a substitute for a true papal nephew; it does not identify him with Prince Camillo Pamfili.")
    decide("st-chp6-p148-astalli-uses-pamfili-name", False, FALSE_NOTE + " The source's male reflexive refers to Astalli; this statement does not merge him with the authentic Prince Camillo Pamfili.")
    decide("st-chp6-p148-bernini-replaced-by-algardi", True, "Haskell explicitly connects Bernini's loss of the favoured sculptor position with Algardi's replacement in that position.")
    decide("st-chp6-p148-bernini-returns-to-favour", False, FALSE_NOTE)
    decide("st-chp6-p148-borromini-preservation-constraint", True, "Haskell says Borromini was instructed to preserve the old basilica's essential structure; the person who issued the instruction is not identified.")
    decide("st-chp6-p148-camillo-builds-palace", True, "The source reports Camillo's own palace project opposite the Collegio Romano; it remains distinct from the Piazza Navona papal palace.")
    decide("st-chp6-p148-camillo-employs-antonio-del-grande", True, "The source explicitly names Antonio del Grande as employed for Camillo's palace; his formal title and exact scope remain unspecified.")
    decide("st-chp6-p148-camillo-exile-characterization", False, FALSE_NOTE)
    decide("st-chp6-p148-camillo-fills-and-decorates-villa", True, "The source says Camillo filled the villa with antiquities; its separate decoration action is recorded in a new statement.")
    decide("st-chp6-p148-camillo-other-projects", True, "Haskell reports Camillo undertook additional public and private projects, but identifies none of them here.")
    decide("st-chp6-p148-camillo-return-to-rome", True, "This records Camillo's return to Rome; receipt by Innocent X is separated into its own statement.")
    decide("st-chp6-p148-cortona-choice-and-camillo-pamfili", True, "Haskell cautiously suggests that the choice of Cortona may reflect the renewed fortunes of Prince Camillo; 'may, perhaps' remains explicit.")
    decide("st-chp6-p148-cortona-first-commission", True, "The source dates Cortona's first official commission to the end of 1651; it does not name the person who assigned it.")
    decide("st-chp6-p148-cortona-palace-gallery-commission", True, "The source explicitly identifies the purpose and site of Cortona's commission: frescoing the gallery ceiling in the Piazza Navona papal palace.")
    decide("st-chp6-p148-financial-ceiling-constraint", True, "Haskell links financial troubles during Innocent's reign to the unrealized ceiling replacement; the antecedent of 'him' is not resolved here.")
    decide("st-chp6-p148-lateran-frescoes-destroyed", True, "The source reports the destruction of the Gentile da Fabriano and Pisanello fresco group during rebuilding; it does not name each fresco.")
    decide("st-chp6-p148-lateran-interior-and-ornament", True, "This preserves Haskell's account of the Lateran interior and ornament replacing frescoes; the visitor's response remains a framed perspective, not a universal reception claim.")
    decide("st-chp6-p148-reactionary-continuation", False, FALSE_NOTE + " This closes the p. 147 aesthetic characterization and preserves Haskell's attributed causal explanation.")

    # Separate builder from responsible patron in Camillo's villa account.
    responsible = by_id["st-chp6-p148-algardi-builds-camillo-villa"]
    responsible["subject_candidate_id"] = "cand-1814"
    responsible["object_candidate_id"] = "cand-1817"
    responsible["predicate"] = "responsible-for-construction-of-villa-by-algardi"
    responsible["qualifiers"]["claim"] = "Haskell says Prince Camillo was responsible for the construction of a magnificent Roman villa by Algardi during his exile."
    responsible["qualifiers"]["mentioned_candidate_ids"] = ["cand-1814", "cand-0034", "cand-1817"]

    # Separate Algardi's style comparison from Haskell's period characterization.
    manner = by_id["st-chp6-p148-algardi-classical-manner"]
    manner["qualifiers"]["claim"] = "Haskell says Algardi moved away from the warmth and vigour typical of Bernini and adopted a colder, more classical manner."
    manner["qualifiers"]["qualification"] = "This stylistic contrast is Haskell's interpretation; the sentence's assessment of the 1640s atmosphere is recorded separately."
    manner["qualifiers"]["mentioned_candidate_ids"] = ["cand-0034", "cand-0312"]

    choice = by_id["st-chp6-p148-cortona-choice-and-camillo-pamfili"]
    choice["predicate"] = "cortona-choice-may-reflect-camillo-fortunes"
    choice["qualifiers"]["claim"] = "Haskell cautiously suggests that the choice of Pietro da Cortona may reflect the renewed fortunes of the authentic Prince Camillo Pamfili."
    choice["qualifiers"]["qualification"] = "The causal interpretation remains explicitly tentative ('may, perhaps'); Camillo's interests and taste are recorded separately."
    choice["qualifiers"]["mentioned_candidate_ids"] = ["cand-0342", "cand-1814"]
    choice["qualifiers"]["ocr_corrections"] = [
        {"source_line": 34, "source_form": "ofPietro", "print_reading": "of Pietro", "locator": "CHP-6.pdf physical page 3 / print p. 148"},
        {"source_line": 34, "source_form": "CamiUo", "print_reading": "Camillo", "locator": "CHP-6.pdf physical page 3 / print p. 148"},
    ]

    artistic = by_id["st-chp6-p148-artistic-life-revival-partial"]
    artistic["subject_candidate_id"] = "cand-4500"
    artistic["object_candidate_id"] = None
    artistic["predicate"] = "notable-roman-baroque-achievements-created-after-camillo-return"
    artistic["qualifiers"]["claim"] = "Haskell says some of the most beautiful and familiar Roman Baroque achievements were created after Camillo's return."
    artistic["qualifiers"]["qualification"] = "This is the second clause of the p. 148 sentence and remains incomplete until p. 149 L39 names examples. 'Most beautiful and familiar' remains Haskell's assessment."
    artistic["qualifiers"]["mentioned_candidate_ids"] = ["cand-4500", "cand-1814"]

    astalli_name = by_id["st-chp6-p148-astalli-uses-pamfili-name"]
    astalli_name["subject_candidate_id"] = "cand-0144"
    astalli_name["object_candidate_id"] = None
    astalli_name["predicate"] = "uses-pamfili-name"
    astalli_name["qualifiers"]["claim"] = "Haskell says Camillo Astalli called himself Pamfili, adding to the confusion around the papal-nephew succession."
    astalli_name["qualifiers"]["qualification"] = "The source distinguishes Astalli from the authentic Prince Camillo Pamfili; the shared surname does not establish identity."
    astalli_name["qualifiers"]["mentioned_candidate_ids"] = ["cand-0144"]

    bernini = by_id[OLD_FOUNTAIN_BODY_ID]
    old_bernini_q = deepcopy(bernini["qualifiers"])
    bernini["subject_candidate_id"] = "cand-0312"
    bernini["object_candidate_id"] = None
    bernini["predicate"] = "achievements-and-reputation-prevent-prolonged-neglect"
    bernini["qualifiers"]["claim"] = "Haskell says Bernini's achievements and reputation were too great for him to be neglected for long."
    bernini["qualifiers"]["qualification"] = "This is Haskell's evaluation of Bernini's reputation; the Fountain's role in his return to favour is recorded separately."
    bernini["qualifiers"]["mentioned_candidate_ids"] = ["cand-0312"]
    for key in list(bernini["qualifiers"]):
        if key.startswith("footnote_") or key == "footnote_markers":
            bernini["qualifiers"].pop(key)

    preservation = by_id["st-chp6-p148-borromini-preservation-constraint"]
    preservation["predicate"] = "instructed-to-preserve-basilica-structure"
    preservation["qualifiers"]["claim"] = "Haskell says Borromini was told to preserve the essential structure of the old Lateran basilica."
    preservation["qualifiers"]["qualification"] = "The source does not identify who issued the instruction. The claimed consequence for Borromini's design work is separate."
    preservation["qualifiers"]["mentioned_candidate_ids"] = ["cand-0406", "cand-0704"]
    preservation["qualifiers"]["ocr_corrections"] = [
        {"source_line": 29, "source_form": "' basilica", "print_reading": "basilica", "locator": "CHP-6.pdf physical page 3 / print p. 148"}
    ]

    first_commission = by_id["st-chp6-p148-cortona-first-commission"]
    first_commission["object_candidate_id"] = None
    first_commission["predicate"] = "receives-first-official-commission-by-end-1651"
    first_commission["qualifiers"]["claim"] = "Haskell says Cortona received his first official commission at the end of 1651, seven years after the change of papacy."
    first_commission["qualifiers"]["mentioned_candidate_ids"] = ["cand-0342", "cand-1819"]
    first_commission["qualifiers"]["qualification"] = "The source gives a date and papal-transition context but does not identify the person who assigned the commission; exact chronology is not independently verified here."

    return_to_rome = by_id["st-chp6-p148-camillo-return-to-rome"]
    return_to_rome["object_candidate_id"] = "cand-4490"
    return_to_rome["predicate"] = "returns-to-rome-after-exile"
    return_to_rome["qualifiers"]["claim"] = "After a series of inconclusive skirmishes with his mother, Prince Camillo returned to Rome."
    return_to_rome["qualifiers"]["qualification"] = "Haskell separately says the Pope received Camillo early in 1651; that reception claim is recorded in a new statement."
    return_to_rome["qualifiers"]["mentioned_candidate_ids"] = ["cand-1814", "cand-1496", "cand-4490"]

    fill_villa = by_id["st-chp6-p148-camillo-fills-and-decorates-villa"]
    fill_villa["predicate"] = "fills-villa-with-antiquities"
    fill_villa["qualifiers"]["claim"] = "Haskell says Camillo filled the villa with antiquities."
    fill_villa["qualifiers"]["qualification"] = "The villa's identity remains provisional pending S3 alignment; its lavish decoration is a separate statement."
    fill_villa["qualifiers"]["mentioned_candidate_ids"] = ["cand-1814", "cand-1817"]

    palace = by_id["st-chp6-p148-camillo-builds-palace"]
    palace["qualifiers"]["mentioned_candidate_ids"] = ["cand-1814", "cand-1816", "cand-5082"]

    financial = by_id["st-chp6-p148-financial-ceiling-constraint"]
    financial["subject_candidate_id"] = None
    financial["object_candidate_id"] = "cand-6277"
    financial["predicate"] = "financial-troubles-prevent-planned-ceiling-replacement"
    financial["qualifiers"]["claim"] = "Haskell says financial troubles during Innocent X's reign made replacement of the Lateran's sixteenth-century wooden ceiling with a planned vault impossible."
    financial["qualifiers"]["mentioned_candidate_ids"] = ["cand-1819", "cand-0406", "cand-0704", "cand-6277"]
    financial["qualifiers"]["qualification"] = "The antecedent of 'him' in the source clause is not resolved; the planned vault and exact agent are not identified as separate candidates. Footnote 1 cites Wittkower and Portoghesi, whose works were not independently consulted."

    destruction = by_id["st-chp6-p148-lateran-frescoes-destroyed"]
    destruction["object_candidate_id"] = "cand-6277"
    destruction["predicate"] = "frescoes-destroyed-during-lateran-remodelling"
    destruction["qualifiers"]["claim"] = "Haskell says the frescoes by Gentile da Fabriano and Pisanello were destroyed during the Lateran rebuilding."
    destruction["qualifiers"]["mentioned_candidate_ids"] = ["cand-6278", "cand-0985", "cand-1940", "cand-6277"]

    reactionary = by_id["st-chp6-p148-reactionary-continuation"]
    reactionary["qualifiers"]["claim"] = "Haskell completes the p. 147 sentence by describing most works made under Innocent X's auspices as somewhat reactionary and attributing the family palace's limitations to Rainaldi and the church's to instructions given to Borromini."
    reactionary["qualifiers"]["mentioned_candidate_ids"] = ["cand-1824", "cand-6277", "cand-2093", "cand-0406", "cand-0704"]

    artistlife = new_statement(
        "st-chp6-p148-artistic-life-revived-after-camillo-return",
        "cand-1814", None, "artistic-life-revives-after-camillo-return",
        "Indeed, after his return to the city artistic Use notably revived from the torpor which had been so evident during the earliest years of Innocent X’s reign,",
        "Haskell says Rome's artistic life notably revived after Camillo's return, relative to the torpor he associates with the earliest years of Innocent X's reign.",
        36, 36, ["cand-1814", "cand-4490", "cand-1819"], True,
        "This records Haskell's temporal association between Camillo's return and artistic revival; it does not infer that his return alone caused the change.",
        "The clause is complete on p. 148; the following achievements clause is recorded separately and closes on p. 149.",
        text_layer="authorial historical narrative and interpretation",
    )
    artistlife["qualifiers"]["ocr_corrections"] = [
        {"source_line": 36, "source_form": "Use", "print_reading": "life", "locator": "CHP-6.pdf physical page 3 / print p. 148"}
    ]

    additions: dict[str, list[dict]] = {}

    def add(after: str, statement: dict) -> None:
        additions.setdefault(after, []).append(statement)

    add("st-chp6-p148-algardi-builds-camillo-villa", new_statement(
        "st-chp6-p148-algardi-constructs-camillo-villa",
        "cand-0034", "cand-1817", "builds-villa-during-camillo-exile",
        "construction by Algardi of one of the most magnificent of all Roman villas.",
        "Haskell says Algardi constructed a magnificent Roman villa during Camillo's exile.",
        34, 35, ["cand-0034", "cand-1814", "cand-1817"], True,
        "This separates the named builder from Camillo's responsibility for the project; the villa identity remains provisional pending S3 alignment.",
        "The source gives no villa name or exact date.",
    ))
    add("st-chp6-p148-algardi-classical-manner", new_statement(
        "st-chp6-p148-algardi-manner-fits-forties",
        "cand-0034", None, "manner-fits-disillusioned-atmosphere-of-1640s",
        "a colder, more classical manner that fitted in well enough with the disillusioned atmosphere of the ’forties.",
        "Haskell says Algardi's colder, more classical manner fitted the disillusioned atmosphere of the 1640s.",
        31, 31, ["cand-0034"], False, FALSE_NOTE,
        "This is Haskell's aesthetic and period interpretation, not an independently measured cultural condition.",
        text_layer="authorial historical assessment",
    ))
    fountain = new_statement(
        NEW_FOUNTAIN_BODY_ID,
        "cand-0312", "cand-0317", "regains-favour-through-fountain",
        "with his Fountain of the Four Rivers in the Piazza Navona, the square that Innocent made the centre of his patronage, he climbed back quickly to savour though not yet to his previous position of complete authority.2",
        "Haskell says Bernini quickly regained favour through the Fountain of the Four Rivers, though not his former complete authority.",
        31, 32, ["cand-0312", "cand-0317"], True,
        "This preserves Haskell's account of the Fountain's role in Bernini's return to favour; 'savour' is the S0 OCR reading for printed 'favour'.",
        "The source's contrast with Bernini's former authority remains Haskell's characterization.",
        text_layer="authorial historical narrative and interpretation",
        base_q=old_bernini_q,
    )
    fountain["qualifiers"]["ocr_corrections"] = [
        {"source_line": 32, "source_form": "savour", "print_reading": "favour", "locator": "CHP-6.pdf physical page 3 / print p. 148"}
    ]
    add(OLD_FOUNTAIN_BODY_ID, fountain)
    add(OLD_FOUNTAIN_BODY_ID, new_statement(
        "st-chp6-p148-innocent-piazza-navona-patronage-centre",
        "cand-1819", "cand-3455", "makes-piazza-navona-centre-of-patronage",
        "the square that Innocent made the centre of his patronage",
        "Haskell says Innocent X made Piazza Navona the centre of his patronage.",
        32, 32, ["cand-1819", "cand-3455"], True,
        "This separates Haskell's claim about Innocent X's patronage geography from Bernini's use of the Fountain to regain favour.",
        "The statement records Haskell's account and does not infer that all papal patronage was located there.",
    ))
    add("st-chp6-p148-borromini-preservation-constraint", new_statement(
        "st-chp6-p148-borromini-applies-gifts-to-decoration",
        "cand-0406", "cand-6277", "directs-design-work-to-decoration",
        "and thus had to use his brilliantly imaginative gifts on decoration rather than on the designing of a wholly new cathedral.",
        "Haskell says the preservation constraint led Borromini to apply his design work to decoration rather than a wholly new cathedral.",
        29, 29, ["cand-0406", "cand-6277"], True,
        "This records Haskell's stated consequence of the preservation instruction; the instruction's issuer remains unnamed.",
        "The source's praise of Borromini's gifts is Haskell's characterization.",
        text_layer="authorial historical narrative and interpretation",
    ))
    add("st-chp6-p148-cortona-choice-and-camillo-pamfili", new_statement(
        "st-chp6-p148-camillo-artistic-interest",
        "cand-1814", None, "only-family-member-with-keen-artistic-interest-and-taste",
        "the only member of the family to show a keen interest in the arts and to have any real taste.",
        "Haskell characterizes Prince Camillo as the only Pamfili family member with keen artistic interest and real taste.",
        34, 34, ["cand-1814", "cand-3456"], False, FALSE_NOTE,
        "This is Haskell's evaluative characterization of Camillo and his family, not an independently established comparison.",
        text_layer="authorial historical assessment",
    ))
    add("st-chp6-p148-camillo-return-to-rome", new_statement(
        "st-chp6-p148-pope-receives-camillo-1651",
        "cand-1819", "cand-1814", "receives-camillo-in-rome",
        "was received by the Pope early in 1651.",
        "Haskell says Innocent X received Prince Camillo in Rome early in 1651.",
        34, 34, ["cand-1819", "cand-1814", "cand-4490"], True,
        "The source reports receipt by the Pope and dates it to early 1651; the ceremony or formal status is not specified.",
        "The claim is kept separate from Camillo's return to Rome.",
    ))
    add("st-chp6-p148-camillo-fills-and-decorates-villa", new_statement(
        "st-chp6-p148-camillo-decorates-villa",
        "cand-1814", "cand-1817", "lavishly-decorates-villa",
        "and had lavishly decorated.",
        "Haskell says Camillo had the villa lavishly decorated.",
        35, 35, ["cand-1814", "cand-1817"], True,
        "The villa remains provisionally linked to the index subentry for Camillo's villa built by Algardi; S3 must confirm identity.",
        "The source does not identify the decorators or specific decoration.",
    ))
    add("st-chp6-p148-reactionary-continuation", new_statement(
        "st-chp6-p148-pamfili-palace-rainaldi-limitations",
        "cand-1824", "cand-2093", "palace-limitations-attributed-to-rainaldi-age",
        "the family palace because of Girolamo Rainaldi’s age and limitations",
        "Haskell attributes limitations of the family palace to Rainaldi's age and limitations.",
        27, 27, ["cand-1824", "cand-2093"], True,
        "This preserves Haskell's attributed causal explanation; it does not independently assess Rainaldi's abilities.",
        "The building is the Piazza Navona palace in the p. 147 context.",
        text_layer="authorial historical narrative and interpretation",
    ))
    add("st-chp6-p148-reactionary-continuation", new_statement(
        "st-chp6-p148-lateran-instructions-limit-borromini",
        "cand-0704", "cand-0406", "church-limitations-attributed-to-instructions-to-borromini",
        "the church because of the inhibiting instructions given to Borromini.",
        "Haskell attributes the church's limitations to inhibiting instructions given to Borromini.",
        27, 27, ["cand-0704", "cand-0406"], True,
        "This records Haskell's causal attribution; the person or institution that issued the instructions is not named.",
        "The instructions are distinct from the later explicit direction to preserve the basilica's structure.",
        text_layer="authorial historical narrative and interpretation",
    ))
    add("st-chp6-p148-artistic-life-revival-partial", artistlife)

    # Preserve the existing p. 148 footnote 2 backlink on the Fountain statement.
    nq["linked_body_statement_ids"] = NOTE2_LINKS
    nq["citation_body_statement_ids"] = NOTE2_LINKS
    later_page_statement["qualifiers"]["continuation_source_statement_id"] = "st-chp6-p148-artistic-life-revival-partial"

    candidates = set()
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = {r["candidate_id"] for r in csv.DictReader(f)}
    mentions = {}
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mentions = {r["mention_id"]: r for r in csv.DictReader(f)}
    all_additions = [item for group in additions.values() for item in group]
    for row in all_additions + [by_id[sid] for sid in QUOTES]:
        if row.get("subject_candidate_id") and row["subject_candidate_id"] not in candidates:
            raise SystemExit(f"unknown subject candidate: {row['statement_id']}")
        if row.get("object_candidate_id") and row["object_candidate_id"] not in candidates:
            raise SystemExit(f"unknown object candidate: {row['statement_id']}")
        for cid in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if cid not in candidates:
                raise SystemExit(f"unknown mentioned candidate {cid}: {row['statement_id']}")

    final_ids = set(by_id)
    output_lines: list[str] = []
    for raw_line in statements_text.splitlines():
        row = json.loads(raw_line)
        sid = row["statement_id"]
        if sid in QUOTES or sid in {NOTE2_ID, "st-chp6-p149-artistic-achievements-identified"}:
            output_lines.append(json.dumps(by_id[sid], ensure_ascii=False, separators=(",", ":")))
        else:
            output_lines.append(raw_line)
        for extra in additions.get(sid, []):
            if extra["statement_id"] in final_ids:
                raise SystemExit(f"duplicate added statement: {extra['statement_id']}")
            final_ids.add(extra["statement_id"])
            output_lines.append(json.dumps(extra, ensure_ascii=False, separators=(",", ":")))
    if final_ids != set(by_id) | NEW_IDS:
        raise SystemExit("statement output ID set mismatch")
    statement_output = ("\n".join(output_lines) + "\n").encode("utf-8")
    coverage_output = update_coverage(raw_files[COVERAGE])
    outputs = {STATEMENTS: statement_output, COVERAGE: coverage_output}

    segment_rows = [by_id[sid] for sid in QUOTES] + all_additions
    flag_counts = {
        "true": sum(row["qualifiers"].get("relation_candidate") is True for row in segment_rows),
        "false": sum(row["qualifiers"].get("relation_candidate") is False for row in segment_rows),
        "unset": sum(row["qualifiers"].get("relation_candidate") is None for row in segment_rows),
    }
    if len(segment_rows) != 38 or flag_counts != {"true": 32, "false": 6, "unset": 0}:
        raise SystemExit(f"unexpected p.148 classification counts: {flag_counts}; statements={len(segment_rows)}")
    for row in segment_rows:
        q = row["qualifiers"]
        first, last = q["source_line_start"], q["source_line_end"]
        span = " ".join(source_lines[first - 1:last])
        if normalize(row.get("original_quote", "")) not in normalize(span):
            raise SystemExit(f"output quote is not a source substring: {row['statement_id']}")
    print(f"preflight passed: base_statements=27 added_statements={len(NEW_IDS)} total={len(segment_rows)}")
    print(f"processed p.148 relation flags: true={flag_counts['true']} false={flag_counts['false']} unset={flag_counts['unset']}")
    print("new statement IDs:")
    for sid in sorted(NEW_IDS):
        row = next(statement for added in additions.values() for statement in added if statement["statement_id"] == sid)
        print(f"  {sid}: {row['predicate']} {row['subject_candidate_id']} -> {row['object_candidate_id']}")
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
