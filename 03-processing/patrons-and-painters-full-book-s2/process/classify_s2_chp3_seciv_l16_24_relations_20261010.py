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
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PAGE = ROOT / ".tmp_s2_chp3_phys20_l14_20261010.png"
SEGMENT = "chp-3:03_CHP-3_sec_iv:l16-24"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"

BACKUPS = {
    TABLE: TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-iv-l16-24-relations-20261010"),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp3-sec-iv-l16-24-endpoints-20261010"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp3-sec-iv-l16-24-endpoints-20261010"),
    COVERAGE: COVERAGE.with_name(COVERAGE.name + ".bak-s2-chp3-sec-iv-l16-24-print-corrections-20261010"),
}

EXPECTED = {
    TABLE: "de7b8ff24a8cc5d28c4f59bd0b365fdd44378337576c555f1e036601856e671a",
    CANDIDATES: "1c36e0fa29ea9f353eb8ac121ede84eca7414b08b122fa3afb5ea09b4d54789e",
    MENTIONS: "95c7e31ddd47c0122c86019eda1a7b337e5a2e3ace30fcbcf0b49c84e3a28438",
    COVERAGE: "2d017a5268b0e8ce381d0b73df26a2d8f666b48a94dae0e3ee76476bb549aa64",
    SOURCE: "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE: "b2e30f8f48bee9052d6fa34b3036a4f7ebe1ce3e2f7ae966fe02e24122f890ca",
}

NOTE_IDS = {
    1: [
        "st-chp3-seciv-notes-l189-204-p78-n1-de-dominici",
        "st-chp3-seciv-notes-l189-204-p78-n1-lumbroso",
    ],
    2: ["st-chp3-seciv-notes-l189-204-p78-n2-oliva-literature"],
    3: ["st-chp3-seciv-notes-l189-204-p78-n3-salvagnini"],
}

CORRECTION_NOTE = (
    " Print p.78/PDF physical p.20 image checked: L20 OCR 'lais son' reads 'his son'; "
    "L22 OCR 'Pis tro da Cortona' reads 'Pietro da Cortona'. S0 OCR and original_quote remain unchanged."
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader), list(reader.fieldnames or []), raw


def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline
        for row in rows
    )


def encode_csv(rows: list[dict[str, str]], fields: list[str], raw: bytes) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    prefix = "\ufeff" if raw.startswith(b"\xef\xbb\xbf") else ""
    return (prefix + stream.getvalue()).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as stream:
            stream.write(payload)
            temp = Path(stream.name)
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and normalize S2 statements for print p.78 L17-24.")
    parser.add_argument("--apply", action="store_true", help="Write after every fixed preflight check passes; default is dry-run.")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed: {path.relative_to(ROOT)}")
    require(all(not path.exists() for path in BACKUPS.values()), "one or more recovery backups already exist")

    raw_table = TABLE.read_bytes()
    rows = read_jsonl(TABLE)
    require(len(rows) == 12753 and len({row["statement_id"] for row in rows}) == len(rows), "statement count or IDs changed")
    by_id = {row["statement_id"]: row for row in rows}
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT]
    require(len(segment_rows) == 22, "source-segment statement count changed")
    require(all((row.get("qualifiers") or {}).get("relation_candidate") is None for row in segment_rows), "segment already has relation decisions")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[15:24])
    norm = lambda value: " ".join(value.split())

    def quote_span(start_line: int, end_line: int, first: str, last: str) -> str:
        span = "\n".join(source_lines[start_line - 1:end_line])
        start = span.index(first)
        stop = span.index(last, start) + len(last)
        quote = span[start:stop]
        require(norm(quote) in norm(span), f"constructed quote does not match source lines {start_line}-{end_line}")
        return quote

    expected_original_ids = {
        "st-chp3-seciv-l16-24-cardinal-reserved-decoration",
        "st-chp3-seciv-l16-24-courtois-approach-rector",
        "st-chp3-seciv-l16-24-courtois-battle-painter",
        "st-chp3-seciv-l16-24-courtois-connections",
        "st-chp3-seciv-l16-24-courtois-entry",
        "st-chp3-seciv-l16-24-courtois-gave-up-art",
        "st-chp3-seciv-l16-24-courtois-letters-and-test",
        "st-chp3-seciv-l16-24-courtois-origin",
        "st-chp3-seciv-l16-24-courtois-portrait-account",
        "st-chp3-seciv-l16-24-courtois-series-opening",
        "st-chp3-seciv-l16-24-courtois-vows-and-residence",
        "st-chp3-seciv-l16-24-courtois-wife-rumour",
        "st-chp3-seciv-l16-24-farnese-heirs",
        "st-chp3-seciv-l16-24-gesu-state",
        "st-chp3-seciv-l16-24-nickel-oliva-roles",
        "st-chp3-seciv-l16-24-oliva-character",
        "st-chp3-seciv-l16-24-oliva-election",
        "st-chp3-seciv-l16-24-preti-commission",
        "st-chp3-seciv-l16-24-preti-layout",
        "st-chp3-seciv-l16-24-preti-reception",
        "st-chp3-seciv-l16-24-s-andrea-decoration",
        "st-chp3-seciv-l16-24-tapestry-concealment",
    }
    require({row["statement_id"] for row in segment_rows} == expected_original_ids, "original statement set changed")

    candidate_rows, candidate_fields, raw_candidates = read_csv(CANDIDATES)
    mention_rows, mention_fields, raw_mentions = read_csv(MENTIONS)
    coverage_rows, coverage_fields, raw_coverage = read_csv(COVERAGE)
    require(len(candidate_rows) == 11571 and len(mention_rows) == 27511, "candidate or mention count changed")
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) == 11593, "candidate ID cursor changed")
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    segment_mentions = [row for row in mention_rows if row["segment_id"] == SEGMENT]
    require(max(int(row["mention_id"].rsplit("-", 1)[1]) for row in segment_mentions) == 57, "mention ID cursor changed")

    coverage = next((row for row in coverage_rows if row["segment_id"] == SEGMENT), None)
    require(coverage is not None, "coverage row missing")
    require(
        (coverage["disposition"], coverage["migration_status"], coverage["source_line_ranges"], coverage["note"])
        == ("reviewed", "complete", "L17-24", "Printed p.78 body L17-24; L17 closes the preceding continuation and L24 continues to p.79 L27, now closed. Footnotes 1-3 are migrated and linked to notes L192-194. Segment complete."),
        "coverage row changed",
    )
    coverage["note"] += CORRECTION_NOTE

    candidates_to_add = [
        (11594, "Unidentified wife of Jacques Courtois", "person", "The passage mentions Courtois's wife, who died about 1654, but gives no name or independent identity. Keep her anonymous and preserve the murder allegation as a rumour.", 22),
        (11595, "Unidentified son and grandson of Alessandro, the great captain", "", "Two unnamed people described as his son and grandson. Haskell says they had little sympathy for the Jesuits; their identities and exact relationship to Cardinal Alessandro Farnese are unresolved.", 20),
        (11596, "The north (region unspecified in Haskell's account)", "place", "Vague source phrase for where Alessandro, the great captain, spent his life. The passage supplies no boundaries or political/geographic identity; do not infer northern Italy or a particular court.", 20),
        (11597, "Unidentified rector of the Jesuit college in Siena", "person", "The unnamed rector approached by Courtois when he decided to become a Jesuit. The college is cand-5204 and its location is Siena; the rector's personal identity is not supplied.", 22),
        (11598, "Ceremonial tapestries used at the Gesu (unnamed group)", "work", "Unnamed tapestries that Haskell says could be hung in the Gesu on ceremonial occasions to conceal its bleakness temporarily. Individual works and their owners are not identified.", 19),
        (11599, "Unidentified confessor in Courtois's quoted account", "person", "The first-person passage represented by Haskell identifies a confessor who gave Courtois a copper portrait and told him to alter it; the confessor's name and identity are not supplied.", 22),
        (11600, "Further decorations at S. Andrea della Valle (unnamed group)", "work", "Passage-local group of further decorations undertaken at S. Andrea della Valle. The ensuing text describes the c.1650 Preti apse commission, but the sentence does not define the full membership of this group or name its agent.", 17),
    ]
    candidate_add_rows = []
    for number, name, suggested_type, detail, line in candidates_to_add:
        candidate_id = f"cand-{number}"
        require(candidate_id not in candidate_by_id, f"candidate already exists: {candidate_id}")
        candidate_add_rows.append({
            "candidate_id": candidate_id,
            "index_entry_id": "",
            "canonical_name": name,
            "index_page_range": "",
            "suggested_type": suggested_type,
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": detail,
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT}#L{line}",
        })
    # An unnamed heir group has no faithful type in the current taxonomy; do not label it as a term.
    require(candidate_by_id["cand-5007"]["suggested_type"] == "term", "heirs candidate type changed")
    candidate_by_id["cand-5007"]["suggested_type"] = ""
    candidate_by_id["cand-5007"]["detail"] = (
        "Unnamed collective heirs of Cardinal Alessandro Farnese. Haskell discusses their role in the Gesu decoration, "
        "but does not identify the individuals or establish exact kinship; do not merge them with Alessandro, the great captain, "
        "or his unnamed son and grandson."
    )

    mention_specs = [
        ("m-chp3-seciv-l16-24-0058", "cand-11594", "his wife", "The unnamed woman identified as Courtois's wife; no name or further identity is supplied."),
        ("m-chp3-seciv-l16-24-0059", "cand-11595", "lais son and grandson", "S0 OCR reads 'lais'; the print reads 'his'. Two unnamed people; do not infer their identities or merge them with Cardinal Farnese's heirs."),
        ("m-chp3-seciv-l16-24-0060", "cand-11596", "the north", "The source's vague regional phrase; do not normalize to northern Italy or another bounded region."),
        ("m-chp3-seciv-l16-24-0061", "cand-11597", "the rector of the Society’s college in Siena", "The unnamed individual Courtois approached; college and Siena retain their own nested mentions."),
        ("m-chp3-seciv-l16-24-0062", "cand-11599", "my confessor", "Role-based person in Courtois's quotation as represented by Haskell; personal identity and memoir source are not given."),
        ("m-chp3-seciv-l16-24-0063", "cand-11598", "Tapestries specially hung out", "Unnamed work group mentioned in the Gesu description; ceremonial use is stated as a possibility."),
        ("m-chp3-seciv-l16-24-0064", "cand-11600", "further decorations", "Unnamed decorations at S. Andrea della Valle; no agent is named in this clause."),
    ]
    mention_add_rows = []
    for mention_id, candidate_id, surface, note in mention_specs:
        require(mention_id not in mention_by_id, f"mention already exists: {mention_id}")
        start = segment_text.index(surface)
        end = start + len(surface)
        require(segment_text[start:end] == surface, f"mention does not match source: {mention_id}")
        mention_add_rows.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    MISSING = object()

    def revise(
        statement_id: str,
        *,
        subject=MISSING,
        object_=MISSING,
        predicate: str | None = None,
        claim: str | None = None,
        relation: bool | None = None,
        relation_note: str | None = None,
        qualifier_updates: dict | None = None,
        remove_qualifiers: tuple[str, ...] = (),
    ) -> dict:
        row = by_id[statement_id]
        if subject is not MISSING:
            row["subject_candidate_id"] = subject
        if object_ is not MISSING:
            row["object_candidate_id"] = object_
        if predicate is not None:
            row["predicate"] = predicate
        qualifiers = dict(row.get("qualifiers") or {})
        if claim is not None:
            qualifiers["claim"] = claim
        for key in remove_qualifiers:
            qualifiers.pop(key, None)
        if qualifier_updates:
            qualifiers.update(qualifier_updates)
        if relation is not None:
            qualifiers["relation_candidate"] = relation
            qualifiers["relation_candidate_note"] = relation_note or ""
        row["qualifiers"] = qualifiers
        return row

    def add_statement(
        statement_id: str,
        subject: str | None,
        object_: str | None,
        predicate: str,
        start_line: int,
        end_line: int,
        claim: str,
        quote: str,
        relation: bool,
        relation_note: str,
        extra: dict | None = None,
        footnote: int | None = None,
    ) -> dict:
        require(statement_id not in by_id, f"statement already exists: {statement_id}")
        span = "\n".join(source_lines[start_line - 1:end_line])
        require(quote and norm(quote) in norm(span), f"quote does not anchor to L{start_line}-{end_line}: {statement_id}")
        qualifiers = {
            "source_line_start": start_line,
            "source_line_end": end_line,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "body",
            "print_page": 78,
            "pdf_physical_page": 20,
            "relation_candidate": relation,
            "relation_candidate_note": relation_note,
        }
        if extra:
            qualifiers.update(extra)
        if footnote is not None:
            qualifiers.update({
                "footnote_marker": footnote,
                "footnote_segment_id": "chp-3:03_CHP-3_sec_iv:l189-243",
                "footnote_source_lines": [{1: 192, 2: 193, 3: 194}[footnote]],
                "footnote_pending": False,
                "footnote_citation_statement_ids": NOTE_IDS[footnote],
            })
        row = {
            "statement_id": statement_id,
            "segment_id": SEGMENT,
            "subject_candidate_id": subject,
            "object_candidate_id": object_,
            "predicate": predicate,
            "qualifiers": qualifiers,
            "original_quote": quote,
            "origin": "book",
            "source_file": SOURCE_FILE,
        }
        by_id[statement_id] = row
        rows.append(row)
        return row

    # Existing statements are narrowed to their own proposition and given explicit S2 decisions.
    revise(
        "st-chp3-seciv-l16-24-cardinal-reserved-decoration",
        object_="cand-5000",
        claim="Haskell says Cardinal Alessandro Farnese reserved decoration of the Gesu tribune for himself and his family; the larger plan was scarcely underway at his death.",
        relation=True,
        relation_note="The Cardinal is the named agent and the tribune is the explicit architectural target; retain the family reservation and unfinished-plan context.",
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-approach-rector",
        object_="cand-11597",
        predicate="approached_rector_to_join_society",
        claim="After deciding to become a Jesuit, Courtois approached the unnamed rector of the Society's college in Siena.",
        relation=True,
        relation_note="The direct target is the rector, not the college; retain the college and Siena as contextual institution and place endpoints.",
        qualifier_updates={"college_candidate_id": "cand-5204", "place_candidate_id": "cand-5203"},
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-battle-painter",
        claim="Haskell says Courtois made a name as a painter of battle scenes after experiencing army life.",
        relation=False,
        relation_note="This is a biographical profession/reputation claim about Courtois; no second identified entity is asserted.",
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-connections",
        object_="cand-2124",
        predicate="was_taken_up_by",
        claim="Haskell says Guido Reni took up Courtois; the passage does not define the precise nature of this support.",
        relation=True,
        relation_note="The source names Guido Reni as the person who took up Courtois; keep the unspecified nature of that support explicit.",
        qualifier_updates={"relationship_scope": "The source phrase 'taken up by' is retained without converting it into a specific formal patronage or training relation."},
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-entry",
        claim="Haskell says Jacques Courtois, also called Giacomo Borgognone, entered the Jesuit Society in 1657.",
        relation=True,
        relation_note="The source directly states that Courtois entered the Jesuit Society in 1657.",
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-gave-up-art",
        claim="Haskell says Borgognone entered the Jesuit Society without brushes, intending to give up art permanently.",
        relation=True,
        relation_note="The Society is the explicit destination of his entry; the intention to give up art remains a source-reported qualification, not an assertion that he stopped painting.",
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-letters-and-test",
        predicate="sent_with_letters_of_introduction_to",
        claim="Haskell says Courtois was sent with letters of introduction to Goswin Nickel, the General in Rome.",
        relation=True,
        relation_note="This statement records the named destination of the introduction; the passive requirement to prove good faith is split into a separate open-endpoint claim.",
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-origin",
        predicate="came_to_italy_from_at_age",
        claim="Haskell says Courtois came to Italy from Dijon when he was 15.",
        relation=True,
        relation_note="The source gives both origin and destination and states Courtois's age; separate destination relation is recorded as well.",
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-portrait-account",
        claim="In the first-person account quoted by Haskell, Courtois says he transformed the copper portrait into an image of Our Saviour.",
        relation=True,
        relation_note="The work is the portrait explicitly named in the quotation; Our Saviour is the depicted subject, not a second work endpoint.",
        qualifier_updates={"ocr_note": "The scan was checked; S0's broken quote text is retained in original_quote."},
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-series-opening",
        claim="Within a year of entering the Society, Courtois was painting a series at Casa Professa; its subjects and forms continue in L26-L33.",
        relation=True,
        relation_note="Courtois is directly linked to the unfinished series reference; its location is separately linked to the Casa Professa candidate.",
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-vows-and-residence",
        object_="cand-5080",
        predicate="spent_rest_of_life_at",
        claim="Haskell names the novitiate of S. Andrea as one of the two places where Courtois spent the rest of his life; the passage does not divide the time between them.",
        relation=True,
        relation_note="The source explicitly names the novitiate as one of two residences; do not equate it with S. Andrea della Valle or infer the time split.",
        qualifier_updates={"other_place_candidate_id": "cand-5206", "duration_distribution": "not specified"},
        remove_qualifiers=("other_place_candidate_id",),
    )
    revise(
        "st-chp3-seciv-l16-24-courtois-wife-rumour",
        object_="cand-11594",
        predicate="was_rumoured_to_have_murdered",
        claim="Haskell reports rumours that Courtois had murdered his wife; the passage presents this only as a rumour, not an established fact.",
        relation=True,
        relation_note="The source explicitly links Courtois to the unnamed woman as the subject of a murder rumour; preserve its epistemic status.",
        qualifier_updates={"epistemic_status": "reported rumour, not established fact", "wife_candidate_id": "cand-11594"},
    )
    revise(
        "st-chp3-seciv-l16-24-farnese-heirs",
        object_="cand-5000",
        predicate="proved_recalcitrant_about_decoration_of",
        claim="In context, Haskell says Cardinal Farnese's unnamed heirs resisted the decoration reserved for his family, including the tribune; their identities remain unresolved.",
        relation=True,
        relation_note="The preceding sentence identifies the reserved decoration; this statement links the unnamed heirs to that project without identifying individuals or inferring kinship beyond 'heirs'.",
        qualifier_updates={"named_alessandro_candidate_id": "cand-5201", "decoration_scope_candidates": ["cand-5000", "cand-4999"], "descendant_identities": "the later son and grandson are unnamed; do not infer identities", "relationship_scope": "Keep Cardinal Farnese's unnamed heirs distinct from Alessandro, the great captain, and his unnamed son and grandson."},
    )
    revise(
        "st-chp3-seciv-l16-24-gesu-state",
        claim="Haskell compares the Gesu's appearance in 1665 with its appearance in 1589, the year Cardinal Farnese died.",
        relation=False,
        relation_note="This is a state and temporal-comparison claim about one church; the dates and Cardinal's death are qualifiers, not a second relation endpoint.",
    )
    revise(
        "st-chp3-seciv-l16-24-nickel-oliva-roles",
        predicate="served_as_general_of",
        claim="Haskell identifies the Belgian Goswin Nickel as General of the Jesuits at that time.",
        relation=True,
        relation_note="This statement records Nickel's office in the Society; Oliva's separate Vicar role and Haskell's inference are recorded separately.",
        remove_qualifiers=("vicar_candidate_id", "epistemic_status"),
    )
    revise(
        "st-chp3-seciv-l16-24-oliva-character",
        claim="Haskell characterizes Oliva as cultivated, devoted to the arts, patient, and diplomatically skilled with difficult patrons.",
        relation=False,
        relation_note="This is an authorial characterization of Oliva; no particular patron is identified as a second endpoint.",
    )
    revise(
        "st-chp3-seciv-l16-24-oliva-election",
        claim="Haskell says Gian Paolo Oliva was elected General of the Jesuits in 1661.",
        relation=True,
        relation_note="The statement records Oliva's election to the named Jesuit office; Haskell's claim about subsequent change is split into its own statement.",
    )
    revise(
        "st-chp3-seciv-l16-24-preti-commission",
        object_="cand-3404",
        predicate="persuaded_to_commission",
        claim="Around 1650 Donna Olimpia persuaded the Theatines to commission an apse fresco at S. Andrea della Valle.",
        relation=True,
        relation_note="Donna Olimpia persuaded the Theatines; the Theatines' commission of the work and Preti's execution are separate relations.",
        qualifier_updates={"work_candidate_id": "cand-5199", "artist_candidate_id": "cand-2056", "location_candidate_id": "cand-5197"},
    )
    revise(
        "st-chp3-seciv-l16-24-preti-layout",
        claim="Haskell says Preti divided the apse wall into three compartments and depicted scenes from the saint's martyrdom.",
        relation=True,
        relation_note="The named artist and the apse-fresco work are explicit endpoints; the saint remains unnamed in this sentence.",
    )
    revise(
        "st-chp3-seciv-l16-24-preti-reception",
        object_="cand-4490",
        predicate="was_forced_to_leave",
        claim="Haskell says Preti was forced to leave Rome in bitterness; he attributes the denigration of Preti's style to the prestige of earlier frescoes combined with Roman painters' chauvinism.",
        relation=True,
        relation_note="The departure has an explicit Rome endpoint. Preserve the causal explanation and its status as Haskell's interpretation; the related imitation and fresco-status claims are split separately.",
    )
    revise(
        "st-chp3-seciv-l16-24-s-andrea-decoration",
        subject="cand-11600",
        predicate="further_decorations_undertaken_at",
        claim="Haskell says further, otherwise unspecified decorations were undertaken at S. Andrea della Valle; the passive clause does not name their agent or define the group's full membership.",
        relation=True,
        relation_note="The source directly locates an unnamed group of decorations at S. Andrea; do not attribute the clause to Pietro or assume it refers only to Preti's apse frescoes.",
    )
    revise(
        "st-chp3-seciv-l16-24-tapestry-concealment",
        subject="cand-11598",
        object_="cand-5200",
        predicate="could_temporarily_conceal_bleakness_of",
        claim="Haskell says ceremonial tapestries could temporarily conceal the Gesu's bleakness on special occasions.",
        relation=True,
        relation_note="The source names the tapestries and church; retain 'might' as a possibility rather than a claim that concealment always occurred.",
        qualifier_updates={"modality": "possible; the source says 'might'"},
    )

    # New, independently anchored atomic claims and endpoints.
    added: list[dict] = []
    def add(*args, **kwargs):
        added.append(add_statement(*args, **kwargs))

    add("st-chp3-seciv-l16-24-cardinal-high-altar-decoration", "cand-0995", "cand-4999", "reserved_decoration_for_self_and_family", 19, 19,
        "Haskell says Cardinal Alessandro Farnese reserved decoration of the Gesu High Altar for himself and his family.",
        quote_span(19, 19, "Cardinal had reserved", "himself and his family"), True,
        "The High Altar is separately named alongside the tribune; keep the two decoration targets distinct.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "family_scope": "the source says 'himself and his family'; individual family members are not named"})

    add("st-chp3-seciv-l16-24-gesu-decoration-plan-status", "cand-5200", None, "reserved_decoration_work_scarcely_begun_by_cardinal_death", 19, 19,
        "Haskell says the decoration Cardinal Farnese had planned for the Gesu had scarcely begun by the time of his death in 1589.",
        quote_span(19, 19, "though he had conceived grandiose plans", "time of his death."), False,
        "This is a single-place project-status claim, not an entity-to-entity relation.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "related_person_candidate_id": "cand-0995", "date": 1589})

    add("st-chp3-seciv-l16-24-courtois-decided-to-join-jesuits", "cand-0399", "cand-3403", "decided_to_join", 22, 22,
        "After his wife's death, Courtois decided to become a Jesuit.", quote_span(22, 22, "he decided to become a Jesuit", "he decided to become a Jesuit"), True,
        "The source explicitly states Courtois's decision to join the Jesuit order, separately from his approach to its college rector.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20})

    add("st-chp3-seciv-l16-24-courtois-friend-cerquozzi", "cand-0399", "cand-0633", "made_friends_with", 21, 22,
        "Haskell says Courtois later made friends with Michelangelo Cerquozzi.", quote_span(21, 22, "later made friends with Michelangelo Cerquozzi", "Michelangelo Cerquozzi"), True,
        "Cerquozzi is separately named; retain one person-to-person relation per named friend.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20})

    add("st-chp3-seciv-l16-24-courtois-friend-pietro-da-cortona", "cand-0399", "cand-3096", "made_friends_with", 21, 22,
        "Haskell says Courtois later made friends with Pietro da Cortona.", quote_span(21, 22, "later made friends with Michelangelo Cerquozzi", "Pis tro da Cortona."), True,
        "The print reads Pietro da Cortona; S0 OCR 'Pis tro' is preserved in the quote and mapped to the existing candidate.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "OCR_visual_correction": "S0 reads 'Pis tro da Cortona'; print p.78 reads 'Pietro da Cortona'."})

    add("st-chp3-seciv-l16-24-courtois-good-faith-test", "cand-0399", None, "required_to_prove_good_faith_by_artistic_skill", 22, 22,
        "Haskell says Courtois was required in Rome to prove his good faith by an unusual use of his artistic skill; the authority is not named.",
        quote_span(22, 22, "was there required to prove his good faith", "undoubted skill."), True,
        "The source asserts a requirement but uses passive voice; leave its authority unresolved instead of assigning it to Goswin Nickel.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "unresolved_endpoint": "the person or institution requiring the proof is not identified"})

    add("st-chp3-seciv-l16-24-courtois-arrived-in-italy", "cand-0399", "cand-3461", "came_to_at_age", 21, 21,
        "Haskell says Courtois came to Italy from Dijon at age 15.", quote_span(21, 21, "had come to Italy from Dijon", "only 15,"), True,
        "The source explicitly names Italy as destination and Dijon as origin; the existing statement records the origin separately.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "age": 15, "origin_candidate_id": "cand-5202"}, footnote=3)

    add("st-chp3-seciv-l16-24-series-painted-at-casa-professa", "cand-5207", "cand-5206", "painted_at", 24, 24,
        "Haskell places Courtois's series painting at Casa Professa within a year of his entering the Society.",
        quote_span(24, 24, "Within a year he was painting in the Casa Professa a series of", "series of"), True,
        "The work and the named Jesuit house are separate candidate endpoints; the series description continues in L26-L33.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "artist_candidate_id": "cand-0399", "time_context": "within a year of entering the Society"})

    add("st-chp3-seciv-l16-24-courtois-final-vows", "cand-0399", "cand-3403", "took_final_vows_in", 23, 23,
        "After entering the Society, Courtois took final vows in the Jesuit order.", quote_span(23, 23, "He then took the final vows", "He then took the final vows"), True,
        "The immediate narrative context resolves the order as the Jesuit Society; this is recorded separately from the two named residences.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "context_resolution": "the order is supplied by the immediately preceding account of Courtois's Jesuit entry"})

    add("st-chp3-seciv-l16-24-courtois-residence-casa-professa", "cand-0399", "cand-5206", "spent_rest_of_life_at", 23, 23,
        "Haskell names Casa Professa as one of the two places where Courtois spent the rest of his life; the passage does not divide the time between them.",
        quote_span(23, 23, "spent the rest of his life in the novitiate of S. Andrea", "Casa Professa."), True,
        "Casa Professa is distinct from the S. Andrea novitiate; retain both locations without inferring how long Courtois lived at either.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "other_place_candidate_id": "cand-5080", "duration_distribution": "not specified"})

    add("st-chp3-seciv-l16-24-courtois-married-to-wife", "cand-0399", "cand-11594", "was_married_to", 22, 22,
        "Haskell identifies the unnamed woman as Courtois's wife; no personal name or fuller identity is supplied.", quote_span(22, 22, "his wife", "his wife"), True,
        "The source explicitly identifies a spouse but does not name her; preserve the open person candidate.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "identity_status": "unnamed in the passage"})

    add("st-chp3-seciv-l16-24-courtois-wife-died", "cand-11594", None, "died_around_1654_after_stormy_marriage", 22, 22,
        "Haskell says Courtois's unnamed wife died about 1654 after several years of stormy married life.",
        quote_span(22, 22, "In about 1654 his wife died", "stormy married life"), False,
        "This is a death-date and biographical-status claim about one unnamed person; the murder allegation is represented separately.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "date": "about 1654"})

    add("st-chp3-seciv-l16-24-farnese-heirs-high-altar-decoration", "cand-5007", "cand-4999", "proved_recalcitrant_about_decoration_of", 19, 20,
        "In context, Haskell says Cardinal Farnese's unnamed heirs resisted the reserved decoration of the Gesu High Altar; their identities remain unresolved.",
        quote_span(19, 20, "His heirs had proved wholly recalcitrant", "His heirs had proved wholly recalcitrant"), True,
        "The High Altar is separately named among the decoration reserved by Cardinal Farnese; do not infer individual heirs or exact kinship.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "contextual_target": "Cardinal Farnese's reserved decoration plan"})

    add("st-chp3-seciv-l16-24-alessandro-spent-life-in-north", "cand-5201", "cand-11596", "spent_life_in", 19, 19,
        "Haskell says Alessandro, the great captain, spent all his life in the north; the region is not specified.",
        quote_span(19, 19, "Alessandro, the great captain", "spent all his life in the north"), True,
        "Retain the source's vague regional endpoint; do not identify Alessandro or normalize 'the north' to a modern region.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "identity_status": "Alessandro's identity remains unresolved in this passage"})

    add("st-chp3-seciv-l16-24-alessandro-descendants-no-sympathy-for-jesuits", "cand-11595", "cand-3403", "had_little_sympathy_for", 19, 20,
        "Haskell says the unnamed son and grandson of Alessandro, the great captain, had little sympathy for the Jesuits.",
        quote_span(19, 20, "lais son and grandson", "Jesuits."), True,
        "The print reads 'his son'; both descendants remain unnamed and distinct from Cardinal Farnese's unspecified heirs.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "OCR_visual_correction": "S0 reads 'lais son'; print p.78 reads 'his son'.", "antecedent_candidate_id": "cand-5201"})

    add("st-chp3-seciv-l16-24-oliva-vicar-of-jesuits", "cand-1771", "cand-3403", "served_as_vicar_of", 24, 24,
        "Haskell identifies Oliva as the Vicar of the Jesuits at that time.", quote_span(24, 24, "the Vicar, Oliva", "the Vicar, Oliva"), True,
        "Oliva's office is separate from Nickel's Generalship; preserve the source's relative time without assigning a new exact date.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "time_context": "at the time described; no exact start date supplied"})

    add("st-chp3-seciv-l16-24-oliva-took-advantage-of-new-situation", "cand-1771", None, "took_advantage_of_new_situation", 24, 24,
        "Haskell infers that Oliva took advantage of the new situation; the phrase does not identify a separate bounded event endpoint.",
        quote_span(24, 24, "there can be little doubt that it was he who took advantage", "new situation."), True,
        "Keep Haskell's inference and leave the referent of 'new situation' open.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "epistemic_status": "authorial inference explicitly marked by 'there can be little doubt'", "unresolved_endpoint": "new situation; not separately identified"})

    add("st-chp3-seciv-l16-24-jesuit-order-changed-under-oliva", "cand-3403", "cand-1771", "changed_under_rule_of", 21, 21,
        "Haskell says everything changed under Oliva's rule as Jesuit General.",
        quote_span(21, 21, "under his rule everything was changed", "under his rule everything was changed"), True,
        "This is Haskell's broad historical characterization; the source does not enumerate what changed.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "qualification": "broad authorial summary, not an enumerated change set"}, footnote=2)

    add("st-chp3-seciv-l16-24-theatines-commission-preti-apse", "cand-3404", "cand-5199", "commissioned_apse_fresco", 18, 18,
        "Around 1650 the Theatines commissioned Mattia Preti's apse fresco at S. Andrea della Valle after Donna Olimpia persuaded them.",
        quote_span(18, 18, "Donna Olimpia, persuaded the Theatines", "apse of their church."), True,
        "The Theatines are the commissioning institution and the apse fresco is the work; Preti's execution is separately recorded.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "date": "about 1650", "artist_candidate_id": "cand-2056", "location_candidate_id": "cand-5197"})

    add("st-chp3-seciv-l16-24-preti-imitated-domenichino", "cand-2056", "cand-0932", "tried_to_imitate", 18, 18,
        "Haskell says Preti tried to imitate Domenichino.", quote_span(18, 18, "Domenichino (whom Preti tried to imitate)", "whom Preti tried to imitate)"), True,
        "The parenthetical explicitly names Domenichino as Preti's model; do not merge the two artists.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20}, footnote=1)

    add("st-chp3-seciv-l16-24-domenichino-frescoes-regarded-as-classics", "cand-5067", None, "came_to_be_regarded_as_classics", 18, 18,
        "Haskell says Domenichino's earlier frescoes at S. Andrea had come to be regarded as classics.",
        quote_span(18, 18, "the frescoes of Domenichino", "had come to be looked upon as classics"), False,
        "This is a reputation/status claim about the identified fresco group, not a relation to another entity.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20}, footnote=1)

    add("st-chp3-seciv-l16-24-lanfranco-frescoes-regarded-as-classics", "cand-5065", None, "came_to_be_regarded_as_classics", 18, 18,
        "Haskell says Lanfranco's earlier frescoes at S. Andrea had come to be regarded as classics.",
        quote_span(18, 18, "Lanfranco of a generation earlier", "had come to be looked upon as classics"), False,
        "This is a reputation/status claim about the identified fresco group, not a relation to another entity.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20}, footnote=1)

    add("st-chp3-seciv-l16-24-courtois-confessor-gave-portrait", "cand-11599", "cand-0399", "gave_portrait_and_instructed_to_transform", 22, 23,
        "In the first-person account represented by Haskell, Courtois says an unidentified confessor gave him the copper portrait and told him to alter it for a spiritual subject.",
        quote_span(22, 23, "my confessor", "spiritual."), True,
        "The confessor is a role-based, unnamed person; the portrait is recorded in the qualifier and the work transformation has its own statement.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "quotation_speaker": "Courtois as represented in Haskell's quotation; the cited memoir/source is not identified here", "work_candidate_id": "cand-5205", "ocr_note": "The original OCR's broken quote is retained; no claim is made about the unidentified memoir."})

    add("st-chp3-seciv-l16-24-pietro-completed-chiesa-nuova-scheme", "cand-3096", "cand-5183", "completed_scheme_in", 19, 19,
        "Haskell says Pietro da Cortona completed the Chiesa Nuova scheme in 1665, about thirty years after beginning it.",
        quote_span(19, 19, "In 1665 when Pietro da Cortona completed the great scheme", "thirty years earlier"), True,
        "The completion is a separate claim from the Gesu's appearance comparison; retain the existing scheme candidate and its Chiesa Nuova context.",
        {"speaker": "Haskell", "print_page": 78, "pdf_physical_page": 20, "date": 1665, "work_place_candidate_id": "cand-3110"})

    # Add the exact footnote reverse links for all claims derived from the cited print sentences.
    footnote_body_ids = {
        1: [
            "st-chp3-seciv-l16-24-preti-reception",
            "st-chp3-seciv-l16-24-preti-imitated-domenichino",
            "st-chp3-seciv-l16-24-domenichino-frescoes-regarded-as-classics",
            "st-chp3-seciv-l16-24-lanfranco-frescoes-regarded-as-classics",
        ],
        2: ["st-chp3-seciv-l16-24-oliva-election", "st-chp3-seciv-l16-24-jesuit-order-changed-under-oliva"],
        3: ["st-chp3-seciv-l16-24-courtois-origin", "st-chp3-seciv-l16-24-courtois-arrived-in-italy"],
    }
    for footnote, body_ids in footnote_body_ids.items():
        for body_id in body_ids:
            q = dict(by_id[body_id].get("qualifiers") or {})
            q["footnote_marker"] = footnote
            q["footnote_segment_id"] = "chp-3:03_CHP-3_sec_iv:l189-243"
            q["footnote_source_lines"] = [{1: 192, 2: 193, 3: 194}[footnote]]
            q["footnote_pending"] = False
            q["footnote_citation_statement_ids"] = NOTE_IDS[footnote]
            by_id[body_id]["qualifiers"] = q
        for note_id in NOTE_IDS[footnote]:
            require(note_id in by_id, f"footnote statement missing: {note_id}")
            q = dict(by_id[note_id].get("qualifiers") or {})
            old = q.get("linked_body_statement_ids", [])
            q["linked_body_statement_ids"] = list(dict.fromkeys(old + body_ids))
            by_id[note_id]["qualifiers"] = q

    # Ensure every relation candidate has valid candidate endpoints; the two intentional single-ended candidates remain open.
    candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in candidate_add_rows}
    candidate_ids.update({"cand-5000", "cand-4999"})
    for row in rows:
        if row.get("segment_id") != SEGMENT:
            continue
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            require(endpoint is None or endpoint in candidate_ids, f"missing endpoint {endpoint} in {row['statement_id']}")

    new_statement_ids = [row["statement_id"] for row in added]
    require(len(new_statement_ids) == 24, f"unexpected number of new statements: {len(new_statement_ids)}")
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement ID after preparation")
    final_segment = [row for row in rows if row.get("segment_id") == SEGMENT]
    relation_flag = lambda row: (row.get("qualifiers") or {}).get("relation_candidate")
    segment_counts = {
        "statements": len(final_segment),
        "bilateral": sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in final_segment),
        "relation_candidates": sum(relation_flag(row) is True for row in final_segment),
        "nonrelations": sum(relation_flag(row) is False for row in final_segment),
        "unclassified": sum(relation_flag(row) is None for row in final_segment),
        "open_relation_candidates": sum(relation_flag(row) is True and not (row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in final_segment),
    }
    require(segment_counts == {"statements": 46, "bilateral": 37, "relation_candidates": 39, "nonrelations": 7, "unclassified": 0, "open_relation_candidates": 2}, f"unexpected segment counts: {segment_counts}")

    candidate_rows.extend(candidate_add_rows)
    mention_rows.extend(mention_add_rows)
    require(len({row["candidate_id"] for row in candidate_rows}) == len(candidate_rows), "duplicate candidate ID after preparation")
    require(len({row["mention_id"] for row in mention_rows}) == len(mention_rows), "duplicate mention ID after preparation")
    for row in mention_add_rows:
        require(row["candidate_id"] in {c["candidate_id"] for c in candidate_rows}, f"mention target missing: {row['mention_id']}")

    payloads = {
        TABLE: encode_jsonl(rows, raw_table),
        CANDIDATES: encode_csv(candidate_rows, candidate_fields, raw_candidates),
        MENTIONS: encode_csv(mention_rows, mention_fields, raw_mentions),
        COVERAGE: encode_csv(coverage_rows, coverage_fields, raw_coverage),
    }
    global_counts = {
        "statements": len(rows),
        "candidates": len(candidate_rows),
        "mentions": len(mention_rows),
        "bilateral_statements": sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in rows),
        "bilateral_relation_candidates": sum(bool(relation_flag(row) is True and row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in rows),
        "bilateral_nonrelations": sum(bool(relation_flag(row) is False and row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in rows),
        "bilateral_unclassified": sum(bool(relation_flag(row) is None and row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in rows),
        "all_relation_candidates": sum(relation_flag(row) is True for row in rows),
        "open_relation_candidates": sum(relation_flag(row) is True and not (row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in rows),
    }
    require(global_counts == {
        "statements": 12777,
        "candidates": 11578,
        "mentions": 27518,
        "bilateral_statements": 8569,
        "bilateral_relation_candidates": 4855,
        "bilateral_nonrelations": 476,
        "bilateral_unclassified": 3238,
        "all_relation_candidates": 4906,
        "open_relation_candidates": 51,
    }, f"unexpected whole-book counts: {global_counts}")

    report = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT,
        "segment_after": segment_counts,
        "new_statements": len(added),
        "new_candidates": len(candidate_add_rows),
        "new_mentions": len(mention_add_rows),
        "whole_book_after": global_counts,
        "post_write_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(payload).hexdigest() for path, payload in payloads.items()},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, payload in payloads.items():
            atomic_write(path, payload)
        saved_rows = read_jsonl(TABLE)
        saved_by_id = {row["statement_id"]: row for row in saved_rows}
        saved_segment = [row for row in saved_rows if row.get("segment_id") == SEGMENT]
        require(len(saved_rows) == 12777 and len(saved_segment) == 46, "statement post-write counts failed")
        require(all(relation_flag(row) is not None for row in saved_segment), "segment contains unclassified statements")
        require(sum(relation_flag(row) is True for row in saved_segment) == 39, "segment relation count failed")
        require(sum(relation_flag(row) is False for row in saved_segment) == 7, "segment nonrelation count failed")
        saved_candidate_ids = {row["candidate_id"] for row in read_csv(CANDIDATES)[0]}
        for row in saved_segment:
            for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
                require(endpoint is None or endpoint in saved_candidate_ids, f"post-write endpoint missing: {row['statement_id']} -> {endpoint}")
        require(digest(TABLE) == hashlib.sha256(payloads[TABLE]).hexdigest(), "statement post-write SHA mismatch")
        require(digest(CANDIDATES) == hashlib.sha256(payloads[CANDIDATES]).hexdigest(), "candidate post-write SHA mismatch")
        require(digest(MENTIONS) == hashlib.sha256(payloads[MENTIONS]).hexdigest(), "mention post-write SHA mismatch")
        require(digest(COVERAGE) == hashlib.sha256(payloads[COVERAGE]).hexdigest(), "coverage post-write SHA mismatch")
    except Exception:
        # Backups are intentionally retained for recovery; do not silently roll back a partial write.
        raise
    print("Apply complete; all four tables passed exact post-write checks. Recovery copies were retained.")


if __name__ == "__main__":
    main()
