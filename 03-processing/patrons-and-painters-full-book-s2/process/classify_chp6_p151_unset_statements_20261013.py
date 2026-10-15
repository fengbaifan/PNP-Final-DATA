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
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md"
SEGMENT = "chp-6:06_CHP-6_sec_i:l59-67"
TARGETS = {
    "st-chp6-p151-alexander-circle-friendship",
    "st-chp6-p151-alexander-cultivation-and-intentions",
    "st-chp6-p151-alexander-summons-bernini",
    "st-chp6-p151-bernini-regains-supremacy",
    "st-chp6-p151-alexander-resumes-urban-projects",
    "st-chp6-p151-bernini-erects-apostles-chair",
    "st-chp6-p151-bernini-papal-tomb",
    "st-chp6-p151-chair-doctors-and-milanese-comparison",
    "st-chp6-p151-chair-light-and-architecture",
    "st-chp6-p151-expressionist-element-at-chair",
    "st-chp6-p151-alexander-building-epithet",
    "st-chp6-p151-bernini-and-pupils-city-building",
    "st-chp6-p151-bernini-colonnade-embraces-square",
    "st-chp6-p151-bernini-constantine-statue",
    "st-chp6-p151-cortona-and-other-altarpieces",
    "st-chp6-p151-cortona-quirinal-gallery-scheme",
    "st-chp6-p151-cortona-santa-maria-della-pace",
    "st-chp6-p151-baroque-flowering-obscures-economic-crisis",
    "st-chp6-p151-economic-drains-partial",
}
CANDIDATE_IDS = [f"cand-{n}" for n in range(11977, 11982)]
MENTION_IDS = [
    "m-chp6-p151-urban-projects",
    "m-chp6-p151-urban-works-agents",
    "m-chp6-p151-urban-works-group",
]
NEW_STATEMENT_IDS = [
    "st-chp6-p151-st-peters-returned-to-centre",
    "st-chp6-p151-golden-age-seemed-to-return",
    "st-chp6-p151-other-artists-altarpieces",
    "st-chp6-p151-quirinal-scheme-employs-leading-artists",
]
EXPECTED_HASHES = {
    STATEMENTS: "99c25bde7a08be4a3b2008ed17e7d824039a5dfeaf5e18ed553ab33d6e8a78c7",
    CANDIDATES: "55ef906c26048ac57e026eca4721b3b5d1e74ff1f4d3c11be1285fe21d6ab240",
    MENTIONS: "e1e62602312fc1b2dc593b390e280bdaf476deaadc2fc6f19c6e18b4d98df4d4",
    COVERAGE: "263673fae6f6ff637c05fd5a56fc539987636ebfe2c321ed46593e461a3edbb3",
}
SOURCE_SHA256 = "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d"
SEGMENT_SHA256 = "a58bb87d1e2279ebd02cb6c313eca2091e8d1bb0e114d1d3ae148dbdb57e3a8d"
BACKUP_SUFFIX = ".bak-s2-chp6-p151-unset-classification-20261013"
FALSE_NOTE = "This is a source-attributed descriptive, evaluative, or incomplete-segment claim, not an independent relation between represented entities."
TRUE_NOTE = "This is an explicit source-attributed relation candidate retained at S2; it does not create a formal S6 edge."


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return " ".join(text.split())


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    os.replace(temp, path)


def quote_between(text: str, first: str, last: str) -> str:
    start = text.find(first)
    if start < 0:
        raise SystemExit(f"quote start not found: {first!r}")
    if first == last:
        return text[start:start + len(first)]
    end = text.find(last, start + len(first))
    if end < 0:
        raise SystemExit(f"quote end not found: {last!r}")
    return text[start:end + len(last)]


def make_candidate(cid: str, name: str, kind: str, detail: str, line: int) -> dict[str, str]:
    return {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line}",
    }


def add_mention(mid: str, cid: str, surface: str, note: str, text: str) -> dict[str, str]:
    positions = [i for i in range(len(text)) if text.startswith(surface, i)]
    if len(positions) != 1:
        raise SystemExit(f"expected one mention surface, got {len(positions)}: {mid} / {surface!r}")
    start = positions[0]
    return {"mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
            "surface_form": surface, "start_char": str(start),
            "end_char": str(start + len(surface)), "note": note}


def new_statement(sid: str, subject: str | None, object_: str | None, predicate: str,
                  claim: str, quote: str, start: int, end: int, mentioned: list[str],
                  relation: bool, qualification: str, note: str, *, extra: dict | None = None) -> dict:
    qualifiers = {
        "source_line_start": start, "source_line_end": end,
        "printed_page": "151", "pdf_physical_page": 6,
        "claim": claim, "speaker": "Haskell", "text_layer": "authorial historical narrative",
        "qualification": qualification, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": note,
    }
    if extra:
        qualifiers.update(extra)
    return {"statement_id": sid, "segment_id": SEGMENT,
            "subject_candidate_id": subject, "object_candidate_id": object_,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote, "origin": "book",
            "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md"}


def build_outputs() -> tuple[dict[Path, bytes], dict[str, object]]:
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")
    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")
    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[58:67])
    if sha256(segment_text.encode("utf-8")) != SEGMENT_SHA256 or source_lines[58].strip() != "[Page 151]":
        raise SystemExit("p.151 source segment hash/page mismatch")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs in source table")
    unset = {sid for sid, row in by_id.items()
             if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset != TARGETS:
        raise SystemExit(f"p.151 unset target set changed: {sorted(unset)}")
    if any(sid in by_id for sid in NEW_STATEMENT_IDS):
        raise SystemExit("planned new p.151 statement ID already exists")

    cfields, candidates, cbom = read_csv(CANDIDATES)
    mfields, mentions, mbom = read_csv(MENTIONS)
    vfields, coverage, vbom = read_csv(COVERAGE)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    if any(cid in candidate_ids for cid in CANDIDATE_IDS) or any(mid in mention_ids for mid in MENTION_IDS):
        raise SystemExit("planned p.151 candidate or mention ID already exists")
    numeric_candidate_ids = [int(row["candidate_id"].split("-")[1]) for row in candidates
                             if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()]
    if max(numeric_candidate_ids) != 11976:
        raise SystemExit(f"candidate sequence changed: max={max(numeric_candidate_ids)}")
    cov_by_id = {row["segment_id"]: row for row in coverage}
    cov = cov_by_id.get(SEGMENT)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.151 coverage state: {cov}")

    quotes_spec = {
        "st-chp6-p151-alexander-circle-friendship": (60, 61, "the circle of poets", "Urban\nVIII."),
        "st-chp6-p151-alexander-cultivation-and-intentions": (61, 61, "He was therefore deeply cultivated", "distinguished ancestry and associations."),
        "st-chp6-p151-alexander-summons-bernini": (62, 62, "On the very day of his election", "S. Maria del Popolo.1"),
        "st-chp6-p151-bernini-regains-supremacy": (63, 64, "Bernini enjoyed once again", "even more spectacular use."),
        "st-chp6-p151-alexander-resumes-urban-projects": (64, 64, "For the new Pope", "projects of Urban.2"),
        "st-chp6-p151-bernini-erects-apostles-chair": (65, 65, "Bernini crowned his life’s work", "Doctors of the Church."),
        "st-chp6-p151-bernini-papal-tomb": (65, 66, "Bernini was also commissioned", "after the Pope’s death."),
        "st-chp6-p151-chair-doctors-and-milanese-comparison": (65, 65, "At the base of the Chair itself", "early years of the century."),
        "st-chp6-p151-chair-light-and-architecture": (65, 65, "Light streams through the window", "classical framework of the architecture."),
        "st-chp6-p151-expressionist-element-at-chair": (65, 65, "A mystical and expressionist element", "turned to dramatic use."),
        "st-chp6-p151-alexander-building-epithet": (66, 66, "Alexander certainly earned his punning nickname", "Papa di grande edificazione’.3"),
        "st-chp6-p151-bernini-and-pupils-city-building": (66, 66, "Elsewhere he and his pupils", "new palaces, churches, fountains, streets and squares."),
        "st-chp6-p151-bernini-colonnade-embraces-square": (66, 66, "Outside the church", "embrace the square."),
        "st-chp6-p151-bernini-constantine-statue": (66, 66, "almost completed", "the statue of Constantine the Great."),
        "st-chp6-p151-cortona-and-other-altarpieces": (66, 66, "Pietro also worked on the reconstruction", "Alexander VII"),
        "st-chp6-p151-cortona-quirinal-gallery-scheme": (66, 66, "In the Quirinal, meanwhile", "a large decorative scheme"),
        "st-chp6-p151-cortona-santa-maria-della-pace": (66, 66, "Pietro also worked on the reconstruction of S. Maria della Pace", "Pietro also worked on the reconstruction of S. Maria della Pace"),
        "st-chp6-p151-baroque-flowering-obscures-economic-crisis": (67, 67, "This astonishing flowering of the Roman Baroque", "second half of the seventeenth century."),
        "st-chp6-p151-economic-drains-partial": (67, 67, "It is evident that despite the tremendous drains on the", "It is evident that despite the tremendous drains on the"),
    }
    quotes: dict[str, str] = {}
    for sid, (first_line, last_line, first, last) in quotes_spec.items():
        span = "\n".join(source_lines[first_line - 1:last_line])
        quote = quote_between(span, first, last)
        if norm(quote) not in norm(by_id[sid].get("original_quote", "")):
            raise SystemExit(f"p.151 source quote mismatch: {sid}")
        quotes[sid] = quote

    added_candidates = [
        make_candidate("cand-11977", "Urban VIII papal projects resumed under Alexander VII (unnamed work group)", "work",
            "Haskell says Alexander VII seemed intent on resuming Urban VIII's projects after Innocent X's interruption. The projects are not listed here; this group is distinct from Urban VIII as a person.", 64),
        make_candidate("cand-11978", "Bernini and his unnamed pupils in the p.151 urban-works account (source-defined group)", "term",
            "The text explicitly groups Bernini with his pupils as responsible for new urban works; no pupil is named and no other membership is implied.", 66),
        make_candidate("cand-11979", "New Roman urban works attributed to Bernini and his pupils (unidentified group)", "term",
            "Aggregate category covering new palaces, churches, fountains, streets, and squares in Haskell's account. No individual building, fountain, street, square, or project is named.", 66),
        make_candidate("cand-11980", "Other artists who painted altarpieces for Alexander VII-patronised churches (unnamed group)", "term",
            "Haskell says many artists besides Pietro da Cortona painted altarpieces for churches patronised by Alexander VII. Their names and works are not supplied; do not merge them with cand-3540.", 66),
        make_candidate("cand-11981", "Leading Roman artists employed on the Quirinal Old Testament scheme (unnamed group)", "term",
            "Haskell says the decorative scheme employed all the leading Roman artists to paint Old Testament scenes. No artists or paintings are identified; do not merge this source-defined group with cand-3540.", 66),
    ]
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    altarpieces = candidate_by_id.get("cand-6315")
    if not altarpieces or altarpieces["canonical_name"] != "Unidentified altarpieces by Pietro da Cortona for churches patronised by Alexander VII":
        raise SystemExit("cand-6315 p.151 altarpiece candidate changed")
    altarpieces["canonical_name"] = "Unidentified altarpieces for churches patronised by Alexander VII (Cortona and other artists)"
    altarpieces["detail"] = (
        "Haskell says Pietro da Cortona painted a number of altarpieces for other churches patronised by Alexander VII. "
        "He adds that many other artists did so as well. No titles, count, individual churches, or artist names are supplied. "
        "This is a source-defined aggregate of unidentified altarpieces, not a claim that every artist made the same works."
    )
    if any(row["candidate_id"] in candidate_ids for row in added_candidates):
        raise SystemExit("planned p.151 candidate already exists")

    new_mentions = [
        add_mention(MENTION_IDS[0], "cand-11977", "the projects of Urban",
                    "Urban VIII's unnamed project group, described as resumed by Alexander VII.", segment_text),
        add_mention(MENTION_IDS[1], "cand-11978", "he and his pupils",
                    "Bernini and his unnamed pupils as joint actors in Haskell's urban-works account.", segment_text),
        add_mention(MENTION_IDS[2], "cand-11979", "new palaces, churches, fountains, streets and squares",
                    "Collective work category; none of the individual structures or public works is identified.", segment_text),
    ]

    remap_ids = {"m-chp6-p151-165": "cand-11981", "m-chp6-p151-171": "cand-11980"}
    for row in mentions:
        if row["mention_id"] in remap_ids:
            if row["candidate_id"] != "cand-3540":
                raise SystemExit(f"p.151 artist mention mapping changed: {row}")
            row["candidate_id"] = remap_ids[row["mention_id"]]
            row["note"] = "Mapped to its source-bounded p.151 artist group; not merged with the separate cand-3540 collective."
    if {row["mention_id"] for row in mentions if row["mention_id"] in remap_ids} != set(remap_ids):
        raise SystemExit("expected p.151 Roman-artist mentions missing")

    planned_cids = candidate_ids | set(CANDIDATE_IDS)
    all_candidate_ids = planned_cids
    decisions = {
        "st-chp6-p151-alexander-circle-friendship": (
            "cand-0665", "cand-6301", "alexander_was_intimate_friend_of_urban_viii_court_circle",
            "Haskell completes the p.150 sentence: before his thirteen-year legation in Cologne, Alexander had been an intimate friend of the circle around Urban VIII’s court.", True,
            "The circle is unnamed and distinct from the court as an institution; this relation also has its opening fragment in p.150.",
            "The source explicitly identifies Alexander's friendship with the source-defined circle."),
        "st-chp6-p151-alexander-cultivation-and-intentions": (
            "cand-0665", None, "haskell_describes_alexander_as_cultivated_and_intending_to_meet_high_hopes",
            "Haskell describes Alexander as deeply cultivated and says he intended to meet the high hopes raised by his ancestry and associations.", False,
            "This is Haskell's assessment of character and intention, not a relation to a distinct entity.", FALSE_NOTE),
        "st-chp6-p151-alexander-summons-bernini": (
            "cand-0665", "cand-0312", "alexander_summoned_bernini_and_ordered_chapel_work_on_election_day",
            "Haskell says that on election day Alexander summoned Bernini to discuss plans for St Peter’s and ordered him to continue work already begun on the family chapel in S. Maria del Popolo.", True,
            "The exact election date and formal chapel name are not supplied; footnote 1 cites Baldinucci, 1948, p. 107, not independently read.",
            "The source explicitly links Alexander's summons and order to Bernini; the chapel and St Peter's remain contextual endpoints."),
        "st-chp6-p151-bernini-regains-supremacy": (
            "cand-0312", "cand-0665", "bernini_regained_supremacy_during_alexander_vii_pontificate",
            "Haskell says Bernini regained the complete supremacy he had held under Urban VIII and used it more spectacularly during Alexander VII’s pontificate.", True,
            "'Complete supremacy' and its comparative use are Haskell's characterization.",
            "The source explicitly locates Bernini's renewed standing in Alexander VII's pontificate."),
        "st-chp6-p151-alexander-resumes-urban-projects": (
            "cand-0665", "cand-11977", "alexander_seemed_intent_on_resuming_urban_viii_projects",
            "Haskell says Alexander VII seemed intent on undoing the interruption under Innocent X and resuming Urban VIII’s projects.", True,
            "The intended action is hedged by 'seemed'; no projects are enumerated here. The St Peter's centrality sentence is recorded separately.",
            "This is an explicit, qualified relation between Alexander and a source-defined group of Urban VIII projects.",
            ["cand-0665", "cand-11977", "cand-1819", "cand-0209"]),
        "st-chp6-p151-bernini-erects-apostles-chair": (
            "cand-0312", "cand-6304", "bernini_erected_apostles_chair_in_st_peters_apse",
            "Haskell says Bernini erected the Apostle’s chair in St Peter’s apse, with a rich decor of golden putti and Doctors of the Church.", True,
            "Keep the source's descriptive name; the passage supplies no formal title or individually identified figures.",
            "The source explicitly attributes the erection of the work to Bernini."),
        "st-chp6-p151-bernini-papal-tomb": (
            "cand-0312", "cand-6305", "bernini_was_commissioned_to_build_alexander_vii_papal_tomb",
            "Haskell says Bernini was commissioned to build Alexander VII’s papal tomb, though work began only after the Pope’s death; he contrasts it with the triumphal monument to Urban VIII.", True,
            "The commissioner is not named; Alexander VII is identified from the immediate context. No completion date is supplied.",
            "The source explicitly states Bernini's commission for the tomb; timing and comparison remain qualified."),
        "st-chp6-p151-chair-doctors-and-milanese-comparison": (
            "cand-6304", "cand-6316", "apostles_chair_religious_energy_compared_with_milanese_painters",
            "Haskell compares the chair’s nervous religious energy with the work of unnamed Milanese painters inspired by Cardinal Federico Borromeo.", True,
            "The comparison is Haskell's formal interpretation; it does not claim that the Milanese painters directly influenced Bernini.",
            "The source explicitly makes a comparative relation between the work's religious expression and an unnamed painter group.",
            ["cand-6304", "cand-6316", "cand-0403"]),
        "st-chp6-p151-chair-light-and-architecture": (
            "cand-6304", "cand-5696", "apostles_chair_composition_breaks_classical_framework_at_st_peters",
            "Haskell describes light taking bodily form in gilded stucco rays, clouds and putti around the chair, which appear to break through the classical framework of the architecture.", True,
            "This is Haskell's visual reading of the chair's relation to the Basilica's architecture, not a measured physical claim.",
            "The passage explicitly describes the composition as breaking through the architectural framework at St Peter's."),
        "st-chp6-p151-expressionist-element-at-chair": (
            "cand-0312", "cand-6304", "bernini_mystical_expressionist_element_used_dramatically_in_apostles_chair",
            "Haskell says a mystical and expressionist element, which he dates to Bernini’s work after Urban VIII’s death, was turned to dramatic use in the Apostle’s chair.", True,
            "The style label and chronology are Haskell's account, not independently tested here.",
            "The source explicitly connects an element in Bernini's work with its use in this identified chair."),
        "st-chp6-p151-alexander-building-epithet": (
            "cand-0665", None, "haskell_credits_alexander_with_punning_building_nickname",
            "Haskell says Alexander certainly earned the punning nickname 'Papa di grande edificazione'.", False,
            "The Italian phrase is a punning nickname, not an official office or formal title; the golden-age comparison is recorded separately.", FALSE_NOTE),
        "st-chp6-p151-bernini-and-pupils-city-building": (
            "cand-11978", "cand-11979", "bernini_and_pupils_were_responsible_for_new_urban_works_in_rome",
            "Haskell attributes new palaces, churches, fountains, streets, and squares in Rome to Bernini and his pupils.", True,
            "No individual pupils, structures, fountains, streets, squares, or projects are named; the collective agent and works remain source-bounded groups.",
            "The source explicitly attributes a group of urban works to Bernini and his pupils.",
            ["cand-11978", "cand-11979", "cand-0312", "cand-4490"]),
        "st-chp6-p151-bernini-colonnade-embraces-square": (
            "cand-0312", "cand-6307", "bernini_built_colonnade_that_embraces_st_peters_square",
            "Haskell says Bernini built the huge colonnade extending to embrace the square.", True,
            "The adjacent St Peter's context identifies the square; the passage gives no construction dates or completion status.",
            "The source explicitly links Bernini's construction of the colonnade to the work candidate."),
        "st-chp6-p151-bernini-constantine-statue": (
            "cand-0312", "cand-6310", "bernini_almost_completed_constantine_statue_in_vatican_palace",
            "Haskell says Bernini almost completed a statue of Constantine the Great in the Vatican Palace.", True,
            "Do not infer completion or current location from this account.",
            "The source explicitly attributes the statue's near-completion to Bernini; the Scala Regia design is recorded in a separate statement."),
        "st-chp6-p151-cortona-and-other-altarpieces": (
            "cand-0342", "cand-6315", "cortona_painted_altarpieces_for_alexander_patronised_churches",
            "Haskell says Pietro da Cortona painted a number of altarpieces for churches patronised by Alexander VII.", True,
            "The works, count, and individual churches are not identified; other artists' work is split into a separate statement.",
            "The source explicitly attributes the altarpiece work to Cortona."),
        "st-chp6-p151-cortona-quirinal-gallery-scheme": (
            "cand-0342", "cand-6312", "cortona_was_in_charge_of_quirinal_old_testament_scheme",
            "Haskell says Pietro da Cortona was in charge of a large decorative scheme in the Quirinal gallery.", True,
            "The individual paintings are not named; the scheme's employment of leading Roman artists is recorded separately. Haskell's 'Barberini favourite' does not identify which family member is meant.",
            "The source explicitly places Cortona in charge of this identified decorative scheme.",
            ["cand-0342", "cand-3464", "cand-4275", "cand-6311", "cand-6312"]),
        "st-chp6-p151-cortona-santa-maria-della-pace": (
            "cand-0342", "cand-6314", "cortona_worked_on_santa_maria_della_pace_reconstruction",
            "Haskell says Pietro da Cortona worked on the reconstruction of S. Maria della Pace.", True,
            "The wording does not make Cortona the sole architect or builder and supplies no date.",
            "The source explicitly links Cortona to work on this reconstruction."),
        "st-chp6-p151-baroque-flowering-obscures-economic-crisis": (
            "cand-4500", "cand-6247", "roman_baroque_flowering_makes_economic_crisis_harder_to_estimate",
            "Haskell argues that the flourishing of the Roman Baroque makes the real extent of the economic crisis affecting Rome in the second half of the seventeenth century difficult to estimate.", True,
            "This is Haskell's methodological argument; it supplies no quantitative estimate of the crisis.",
            "The source explicitly connects the artistic flourishing to the difficulty of estimating the economic crisis."),
        "st-chp6-p151-economic-drains-partial": (
            None, None, "p151_partial_phrase_about_financial_drains_completed_on_p152",
            "P.151 ends with an incomplete phrase about 'tremendous drains'; the complete financial comparison begins on p.152 and is carried by the linked statement there.", False,
            "The phrase is incomplete in this segment and does not state the affected finances until p.152 L70; preserve the continuation link rather than infer an endpoint here.",
            "This segment fragment alone does not express a complete relation; the completed claim is recorded on p.152.", []),
    }
    added_candidate_ids = set(CANDIDATE_IDS)
    all_cids = candidate_ids | added_candidate_ids
    for sid, values in decisions.items():
        if sid not in TARGETS:
            raise SystemExit(f"unexpected p.151 decision target: {sid}")
        if len(values) == 8:
            subject, object_, predicate, claim, relation, qualification, note, mentioned = values
        else:
            subject, object_, predicate, claim, relation, qualification, note = values
            mentioned = None
        row = by_id[sid]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = object_
        row["predicate"] = predicate
        row["original_quote"] = quotes[sid]
        q = row["qualifiers"]
        q.update({"claim": claim, "relation_candidate": relation,
                  "relation_candidate_note": note, "qualification": qualification,
                  "mentioned_candidate_ids": list(mentioned) if mentioned is not None else [x for x in (subject, object_) if x]})
    if set(decisions) != TARGETS:
        raise SystemExit("not all p.151 unset statements received a classification")
    by_id["st-chp6-p151-alexander-resumes-urban-projects"]["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-0665", "cand-11977", "cand-1819", "cand-0209", "cand-5696"]
    by_id["st-chp6-p151-chair-light-and-architecture"]["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-6304", "cand-5696"]
    by_id["st-chp6-p151-alexander-building-epithet"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-0665"]
    by_id["st-chp6-p151-economic-drains-partial"]["qualifiers"]["mentioned_candidate_ids"] = []
    by_id["st-chp6-p151-economic-drains-partial"]["qualifiers"].update({
        "continuation_status": "closed",
        "continuation_to_segment_id": "chp-6:06_CHP-6_sec_i:l69-76",
        "continued_by_source_line": 70,
        "continuation_resolved_by_statement_id": "st-chp6-p152-alexander-financial-resources",
    })

    friendship = by_id["st-chp6-p151-alexander-circle-friendship"]["qualifiers"]
    friendship.update({
        "continuation_status": "complete",
        "continued_from_segment_id": "chp-6:06_CHP-6_sec_i:l48-57",
        "continued_from_source_line": 57,
        "continuation_resolved_from_statement_id": "st-chp6-p150-alexander-friendship-partial",
    })
    life_correction = {
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
        "source_line": 66, "ocr": "niahy", "print": "many",
        "basis": "CHP-6.pdf physical page 6.",
    }

    remapped_by_id = {row["mention_id"]: row for row in mentions if row["mention_id"] in {"m-chp6-p151-165", "m-chp6-p151-171"}}
    if set(remapped_by_id) != {"m-chp6-p151-165", "m-chp6-p151-171"}:
        raise SystemExit("expected p.151 artist mentions missing")

    def make_new_statement(sid: str, subject: str | None, object_: str | None, predicate: str,
                           claim: str, quote: str, relation: bool, qualification: str,
                           note: str, mentioned: list[str], *, extra: dict | None = None) -> dict:
        result = new_statement(sid, subject, object_, predicate, claim, quote,
            64 if sid == NEW_STATEMENT_IDS[0] else 66, 64 if sid == NEW_STATEMENT_IDS[0] else 66,
            mentioned, relation, qualification, note, extra=extra)
        for cid in [subject, object_]:
            if cid and cid not in all_cids:
                raise SystemExit(f"new statement endpoint missing: {sid} -> {cid}")
        if not set(mentioned) <= all_cids:
            raise SystemExit(f"new statement mention missing: {sid}")
        return result

    central_quote = quote_between(segment_text, "Once more St Peter’s", "centre of the scene.")
    golden_age_quote = quote_between(segment_text, "It seemed as if", "golden age had returned")
    other_artists_quote = quote_between(segment_text, "as did niahy other artists", "as did niahy other artists")
    artists_employed_quote = quote_between(segment_text, "which employed all the leading Roman artists", "great gallery.")
    new_statements = [
        make_new_statement(NEW_STATEMENT_IDS[0], "cand-5696", None,
            "haskell_says_st_peters_returned_to_centre_of_roman_patronage_scene",
            "Haskell says St Peter’s returned to the centre of the scene.", central_quote, False,
            "This is Haskell's metaphorical assessment of prominence, not a relation between St Peter's and a separate entity.",
            FALSE_NOTE, ["cand-5696"]),
        make_new_statement(NEW_STATEMENT_IDS[1], None, None,
            "haskell_says_a_golden_age_seemed_to_return",
            "Haskell says it seemed as if a golden age had returned.", golden_age_quote, False,
            "This is a source-attributed historical metaphor, not a relation between represented entities.",
            FALSE_NOTE, []),
        make_new_statement(NEW_STATEMENT_IDS[2], "cand-11980", "cand-6315",
            "other_unnamed_artists_also_painted_altarpieces_for_alexander_patronised_churches",
            "Haskell says many other artists besides Cortona also painted altarpieces for churches patronised by Alexander VII.",
            other_artists_quote, True,
            "The artists and individual works are unnamed; the group endpoint represents the source-defined aggregate, without implying that every artist made the same works. S0 OCR reads 'niahy'; print reads 'many'.",
            "The source explicitly says this unnamed artist group also painted altarpieces in the aggregate described here.",
            ["cand-11980", "cand-6315", "cand-0665"],
            extra={"ocr_corrections": [life_correction]}),
        make_new_statement(NEW_STATEMENT_IDS[3], "cand-6312", "cand-11981",
            "quirinal_old_testament_scheme_employed_leading_roman_artists",
            "Haskell says the Quirinal Old Testament decorative scheme employed all the leading Roman artists to paint scenes in the great gallery.",
            artists_employed_quote, True,
            "No artist or painting is named; the artists are kept distinct from cand-3540, a group in a different passage.",
            "The source explicitly says the decorative scheme employed the source-defined artist group.",
            ["cand-6312", "cand-11981", "cand-6311"]),
    ]
    if any(row["statement_id"] in by_id for row in new_statements):
        raise SystemExit("planned p.151 statement ID already exists")

    for row in new_statements:
        by_id[row["statement_id"]] = row
    statements = [by_id[row["statement_id"]] for row in statements]
    statements.extend(new_statements)

    cov["note"] += (
        " p.151 physical page 6 was reviewed against CHP-6.pdf. The 19 previously unset statements are classified, "
        "including Alexander’s friendship with the Urban VIII court circle, his summons and order to Bernini, "
        "Bernini’s works and commissions, Cortona’s schemes and reconstruction work, and Haskell’s Roman Baroque/economic argument. "
        "Four statements were added to separate St Peter’s centrality, the golden-age metaphor, other artists’ altarpieces, and the Quirinal scheme’s artist group. "
        "Five source-bounded candidates and three mentions were added; the existing leading/other artist mentions were remapped from cand-3540. "
        "The p.151 fragment on financial drains is linked to its completed p.152 statement. The OCR 'niahy' is retained in S0 and corrected only in S2."
    )

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        CANDIDATES: csv_bytes(cfields, candidates + added_candidates, cbom),
        MENTIONS: csv_bytes(mfields, mentions + new_mentions, mbom),
        COVERAGE: csv_bytes(vfields, coverage, vbom),
    }
    totals = {
        "true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in statements),
        "false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in statements),
        "unset": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in statements),
    }
    summary = {
        "segment": SEGMENT, "statements_classified": len(TARGETS),
        "new_atomic_statements": len(new_statements),
        "relation_candidates_in_segment": sum(by_id[sid]["qualifiers"].get("relation_candidate") is True for sid in TARGETS)
            + sum(row["qualifiers"]["relation_candidate"] is True for row in new_statements),
        "non_relational_in_segment": sum(by_id[sid]["qualifiers"].get("relation_candidate") is False for sid in TARGETS)
            + sum(row["qualifiers"]["relation_candidate"] is False for row in new_statements),
        "candidates_added": CANDIDATE_IDS, "mentions_added": MENTION_IDS,
        "candidate_revised": "cand-6315", "artist_mentions_remapped": sorted(remapped_by_id),
        "totals_after": totals, "mode": "dry-run",
    }
    return outputs, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and atomize p.151 S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up affected tables, then atomically write reviewed results.")
    args = parser.parse_args()
    outputs, summary = build_outputs()
    summary["mode"] = "apply" if args.apply else "dry-run"
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    for path, backup in backups.items():
        if backup.exists() and backup.read_bytes() != path.read_bytes():
            raise SystemExit(f"existing backup differs from current pre-write state: {backup.name}")
    for path, backup in backups.items():
        if not backup.exists():
            shutil.copy2(path, backup)
    for path, data in outputs.items():
        atomic_write(path, data)
    print("APPLIED; backups:")
    for backup in backups.values():
        print(backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
