"""Atomize and correct p.241 body statements against the printed page."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
SEGMENT = "chp-8:08_CHP-8_sec_ii:l361-370"
FOOTNOTE_SEGMENT = "chp-8:08_CHP-8_sec_ii:l372-461"
BACKUP_SUFFIX = ".bak-s2-chp8-p241-l361-370-semantic-review-20261014"
EXPECTED_TABLE_SHA256 = "9b1e90617498eb29591e54c5e47f7407a757e3209a036644bd74f1d3a5f30453"
EXPECTED_MENTIONS_SHA256 = "69b9f7216fae5f6cbcec6ef59bff5d9b53793b2a1e1fe7e05300b4feb29e75e4"
EXPECTED_CANDIDATES_SHA256 = "fbd1003c7ef3c541bfa80da617d022d1427ae5b25a8610a90536cfeacee056a1"
EXPECTED_EXISTING = {
    "st-chp8-p241-additional-loans",
    "st-chp8-p241-artists-preferred-ferdinand",
    "st-chp8-p241-attendance-success-and-academy",
    "st-chp8-p241-florentine-absence-and-cardinal-loan",
    "st-chp8-p241-later-exhibitions-before-ferdinands-death",
    "st-chp8-p241-portrait-as-patronage-signal",
    "st-chp8-p241-quoted-praise-and-art-patronage",
    "st-chp8-p241-twenty-odd-loans",
    "st-chp8-p241-venetian-and-neapolitan-contingents",
    "st-chp8-p241-venetian-school-and-florence",
    "st-chp8-p241-venice-concluding-assessment",
}
NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12099", "canonical_name": "Classical-academic theories dictating artistic practice in Rome (Haskell's description)",
        "suggested_type": "term", "detail": "Source-defined theory group said by Haskell to dictate artistic practice in Rome; keep distinct from other classicism candidates until identity alignment.", "source_line": 369,
    },
    {
        "candidate_id": "cand-12100", "canonical_name": "The painterly mode in Haskell's account of Ferdinand's Florence",
        "suggested_type": "term", "detail": "Haskell's substantivized use of 'the painterly' for an artistic mode centered in Florence for a few years; not treated as a formally named school.", "source_line": 369,
    },
    {
        "candidate_id": "cand-12101", "canonical_name": "Artists who felt their talents would be stifled in papal Rome and would have welcomed work for Ferdinand (unnamed group)",
        "suggested_type": "term", "detail": "Unnamed group in Haskell's explanatory inference; no members, count, or actual employment records are identified in this sentence.", "source_line": 369,
    },
    {
        "candidate_id": "cand-12102", "canonical_name": "Italian painting in Haskell's closing assessment of Venice (p.241)",
        "suggested_type": "term", "detail": "Source-local category in Haskell's closing assessment that the most interesting Italian painting was to be found in Venice; distinct from the broader candidate 'Italian art'.", "source_line": 370,
    },
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def jsonl_bytes(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    temporary.replace(path)


def phrase(line: str, text: str) -> str:
    start = line.find(text)
    if start < 0:
        raise SystemExit(f"source phrase not found: {text!r}")
    return line[start:start + len(text)]


def quoted(rows, sid, *, subject, object_, predicate, claim, quote, lines,
           qualification, mentioned, relation, relation_note, extras=None,
           speaker="Haskell"):
    rows_by_id = {row["statement_id"]: row for row in rows}
    row = rows_by_id.get(sid)
    if row is None:
        row = {
            "statement_id": sid, "segment_id": SEGMENT,
            "origin": "book", "source_file": SOURCE_REL,
        }
        rows.append(row)
    row["segment_id"] = SEGMENT
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    row["origin"] = "book"
    row["source_file"] = SOURCE_REL
    q = {
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 241, "pdf_physical_page": 47,
        "claim": claim, "speaker": speaker, "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": relation_note,
    }
    if extras:
        q.update(extras)
    row["qualifiers"] = q
    return row


def csv_row_bytes(row, fieldnames, lineterminator="\n"):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore", lineterminator=lineterminator)
    writer.writerow(row)
    return stream.getvalue().encode("utf-8")


def update_csv(data: bytes, *, patch_ids=None, additions=None):
    patch_ids = patch_ids or {}
    additions = additions or []
    bom = data.startswith(b"\xef\xbb\xbf")
    text = data.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    if not lines:
        raise SystemExit("empty CSV table")
    fieldnames = next(csv.reader([lines[0].rstrip("\r\n")]))
    ending = "\r\n" if "\r\n" in text else "\n"
    found = set()
    for index in range(1, len(lines)):
        raw = lines[index].rstrip("\r\n")
        if not raw:
            continue
        parsed = next(csv.reader([raw]))
        if parsed and parsed[0] in patch_ids:
            if parsed[0] in found:
                raise SystemExit(f"duplicate CSV id: {parsed[0]}")
            updated = dict(zip(fieldnames, parsed))
            expected = patch_ids[parsed[0]]["expected_candidate_id"]
            if updated.get("candidate_id") != expected:
                raise SystemExit(f"unexpected mapping for {parsed[0]}: {updated.get('candidate_id')}")
            updated.update(patch_ids[parsed[0]]["changes"])
            lines[index] = csv_row_bytes(updated, fieldnames, ending).decode("utf-8").rstrip("\r\n") + lines[index][len(raw):]
            found.add(parsed[0])
    if found != set(patch_ids):
        raise SystemExit(f"CSV patch ids missing: {sorted(set(patch_ids)-found)}")
    existing_ids = {next(csv.reader([line.rstrip("\r\n")]))[0] for line in lines[1:] if line.strip()}
    duplicate = existing_ids.intersection(row["mention_id"] if "mention_id" in row else row["candidate_id"] for row in additions)
    if duplicate:
        raise SystemExit(f"CSV addition ids already exist: {sorted(duplicate)}")
    appended = b"".join(csv_row_bytes(row, fieldnames, ending) for row in additions)
    output = "".join(lines).encode("utf-8") + appended
    return (b"\xef\xbb\xbf" + output if bom else output), len(found), len(additions)


def plan():
    table_bytes, mentions_bytes, candidates_bytes = TABLE.read_bytes(), MENTIONS.read_bytes(), CANDIDATES.read_bytes()
    expected = [
        (table_bytes, EXPECTED_TABLE_SHA256, "book-statements"),
        (mentions_bytes, EXPECTED_MENTIONS_SHA256, "mentions"),
        (candidates_bytes, EXPECTED_CANDIDATES_SHA256, "entity-candidates"),
    ]
    for data, digest, label in expected:
        if sha(data).lower() != digest.lower():
            raise SystemExit(f"{label} changed since p.240 review; refusing write")

    meta = next((r for r in read_jsonl(SEGMENTS) if r.get("segment_id") == SEGMENT), None)
    if not meta or (meta.get("line_start"), meta.get("line_end")) != (361, 370):
        raise SystemExit("unexpected p.241 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[360:370])
    if sha(segment_text.encode("utf-8")) != meta.get("sha256"):
        raise SystemExit("p.241 source segment hash mismatch")
    lines = {n: source_lines[n - 1] for n in range(362, 371)}

    quotes = {
        "portrait": phrase(lines[362], "who thus unmistakably showed his patronage of the whole venture."),
        "taste": phrase(lines[362], "No less clear was the orientation of his taste, and hence the general impulse he wished to give to contemporary art."),
        "twenty_odd": phrase(lines[362], "Of the twenty-odd pictures he lent in all"),
        "seven_old_masters": phrase(lines[362], "seven were Venetian old masters"),
        "cagnacci": phrase(lines[363], "his Guido Cagnacci Magdalene"),
        "cagnacci_colour": phrase(lines[363], "di colore freschissimo"),
        "cassana": phrase(lines[363], "his Cassana Portrait of a Hunter"),
        "marco_landscapes": phrase(lines[363], "almost certainly, four landscapes by Marco Ricci"),
        "florentine_absence": phrase(lines[364], "Not a single work by any of the Florentine artists, old or new, represented in his collection was shown by the Grand Prince."),
        "hint": phrase(lines[364], "The hint could hardly have been clearer"),
        "cardinal_loan": phrase(lines[364], "further Venetian paintings lent by Cardinal Medici"),
        "venetians": phrase(lines[365] + "\n" + lines[366], "Venetians made an impressive showing in the exhibition"),
        "neapolitan": "a strong\n" + phrase(lines[366], "Neapolitan contingent mainly lent by the del Rosso brothers"),
        "del_rosso": phrase(lines[366], "mainly lent by the del Rosso brothers"),
        "luca": phrase(lines[366], "Luca Giordano was much in evidence"),
        "attended": phrase(lines[367], "The Grand Prince himself attended the exhibition"),
        "duration": phrase(lines[367], "the exhibition which remained open for several days"),
        "success": phrase(lines[367], "was evidently a success"),
        "illness": phrase(lines[367], "Ferdinand soon fell seriously ill"),
        "academy_organized": phrase(lines[367], "the Accademia del Disegno, under whose auspices it had been organised"),
        "academy_dormancy": phrase(lines[367], "returned to the slumbers which had characterised most of its recent existence"),
        "later_events": phrase(lines[367], "Exhibitions, planned on similar lines, took place at haphazard intervals in 1715, 1724, 1729, 173 7 and 1767?"),
        "ferdinand_died": phrase(lines[368], "But Ferdinand died before any of these."),
        "venetian_school": phrase(lines[369], "By the time of his death the Venetian school of painting was widely recognised as the most lively in Italy."),
        "masters_not_seen": phrase(lines[369], "Though he did not see the triumphs of its greatest masters"),
        "promotion": phrase(lines[369], "he had derived immense satisfaction from his promotion of all that was most vital in contemporary art"),
        "painterly": lines[369][lines[369].find("For a few years"):lines[369].find(", in direct opposition")],
        "classical_academic": phrase(lines[369], "the classical-academic theories which dictated practice in Rome"),
        "stifled_artists": phrase(lines[369], "artists who rightly felt that their talents would have been stifled in the papal city"),
        "art_patronage_role": phrase(lines[369], "It is for this reason that he plays such a notable part in any account of Italian art patronage"),
        "quoted_praise": lines[369][lines[369].find("we can at least understand"):lines[369].find(".4", lines[369].find("we can at least understand")) + 2],
        "venice_closing": lines[370],
    }

    rows = read_jsonl(TABLE)
    existing = {row["statement_id"]: row for row in rows if row.get("segment_id") == SEGMENT}
    if set(existing) != EXPECTED_EXISTING:
        raise SystemExit(f"unexpected p.241 statement ids: {sorted(set(existing)^EXPECTED_EXISTING)}")
    if any(row.get("segment_id") == FOOTNOTE_SEGMENT and row.get("statement_id", "").startswith("st-chp8-p241-") for row in rows):
        note_rows = {row["statement_id"] for row in rows if row.get("segment_id") == FOOTNOTE_SEGMENT}
    else:
        note_rows = set()
    required_note_ids = {
        "st-chp8-p241-note1-fogolari-letter116",
        "st-chp8-p241-note2-uncertain-landscape-lender",
        "st-chp8-p241-note3-1767-catalogue",
        "st-chp8-p241-note4-sgrilli-locator",
        "st-chp8-p241-note5-gabburri-correspondence",
        "st-chp8-p241-note5-gerini-follower",
    }
    if not required_note_ids.issubset(note_rows):
        raise SystemExit("p.241 footnote statements are not present for linking")

    new_ids = set()

    def add(sid, subject, object_, predicate, claim, quote, line_range, qualification,
            mentioned, relation, relation_note, extras=None, speaker="Haskell"):
        if sid not in EXPECTED_EXISTING:
            if any(r.get("statement_id") == sid for r in rows):
                raise SystemExit(f"statement id already exists: {sid}")
            new_ids.add(sid)
        return quoted(rows, sid, subject=subject, object_=object_, predicate=predicate,
            claim=claim, quote=quote, lines=line_range, qualification=qualification,
            mentioned=mentioned, relation=relation, relation_note=relation_note,
            extras=extras, speaker=speaker)

    # Portrait, taste and the approximate exhibition loan group.
    add("st-chp8-p241-portrait-as-patronage-signal", "cand-1609", "cand-7977",
        "portrait_display_signalled_ferdinands_patronage_of_exhibition",
        "Haskell says the portrait of Ferdinand above the chapel door unmistakably signalled his patronage of the exhibition.", quotes["portrait"], (362, 362),
        "This is Haskell's interpretation of the display; the portrait is unidentified beyond its sitter and location.",
        ["cand-1609", "cand-8071", "cand-7977"], True,
        "The source interprets the portrait display as a signal of Ferdinand's patronage; it does not identify the portrait maker.",
        {"continuation_from_segment_id": FOOTNOTE_SEGMENT})
    add("st-chp8-p241-ferdinand-taste-direction", "cand-1609", "cand-8100",
        "intended_to_direct_contemporary_art_through_taste",
        "Haskell says Ferdinand's taste made clear the general impulse he wished to give contemporary art.", quotes["taste"], (362, 362),
        "This is Haskell's interpretation of Ferdinand's artistic direction, not an independently established program.",
        ["cand-1609", "cand-8100"], True,
        "The passage explicitly connects Ferdinand's taste and intention with the direction of contemporary art.")
    add("st-chp8-p241-twenty-odd-loans", "cand-1609", "cand-8076",
        "lent_approximately_twenty_odd_pictures_to_1706_exhibition",
        "Haskell says Ferdinand lent twenty-odd pictures in all to the exhibition.", quotes["twenty_odd"], (362, 362),
        "The total is approximate; Haskell names some constituent paintings in the following list.",
        ["cand-1609", "cand-8076", "cand-7977"], True,
        "The passage explicitly attributes the approximate loan group to Ferdinand and the exhibition.")
    add("st-chp8-p241-seven-venetian-old-masters", "cand-8076", "cand-4288",
        "included_seven_venetian_old_master_paintings",
        "Haskell says seven of Ferdinand's twenty-odd loans were Venetian old-master paintings.", quotes["seven_old_masters"], (362, 362),
        "The seven are not a separate named collection; individual works are identified below only by painter.",
        ["cand-8076", "cand-4288", "cand-8104", "cand-7977"], True,
        "The source explicitly describes the seven paintings as part of Ferdinand's exhibition loan group.")

    works = [
        ("giorgione", "cand-8082", "cand-1188", "a Giorgione", 362),
        ("titian", "cand-8083", "cand-2630", "a Titian", 362),
        ("veronese", "cand-8084", "cand-2755", "a Veronese", 362),
        ("tintoretto", "cand-8085", "cand-2627", "a Tintoretto", 362),
        ("pordenone", "cand-8086", "cand-1975", "a Pordenone", 362),
        ("schiavone", "cand-8087", "cand-2395", "a Schiavone", 362),
        ("bordone", "cand-8088", "cand-0391", "a Paris Bordone", 362),
        ("guercino", "cand-8089", "cand-1258", "an early Guercino", 362),
        ("carracci", "cand-8090", "cand-0580", "a Lodovico Carracci", 362),
        ("schedoni", "cand-8091", "cand-2394", "Schedoni", 363),
    ]
    for slug, work_id, artist_id, surface, source_line in works:
        quote = phrase(lines[source_line], surface)
        artist = surface.removeprefix("a ").removeprefix("an early ")
        add(f"st-chp8-p241-{slug}-loan", "cand-1609", work_id,
            "lent_unidentified_painting_to_1706_exhibition",
            f"Haskell includes an unidentified painting by {artist} among Ferdinand's loans to the 1706 exhibition.",
            quote, (source_line, source_line),
            "The painting is not titled or located. In context it belongs to the approximate group Ferdinand lent; the passage does not provide an individual loan record.",
            ["cand-1609", "cand-7977", "cand-8076", work_id, artist_id], True,
            "Haskell's list places this work within Ferdinand's exhibition loans; the maker attribution remains as stated in the source.")

    add("st-chp8-p241-additional-loans", "cand-1609", "cand-0479",
        "lent_cagnacci_magdalene_to_1706_exhibition",
        "Haskell says Ferdinand lent Guido Cagnacci's Magdalene to the 1706 exhibition.", quotes["cagnacci"], (363, 363),
        "The work is identified by painter and title only; note 1 cites the published letter through Fogolari, not an independently consulted original.",
        ["cand-1609", "cand-0478", "cand-0479", "cand-7977"], True,
        "The sentence directly attributes the loan to Ferdinand.",
        {"footnote_marker": 1, "footnote_statement_ids": ["st-chp8-p241-note1-fogolari-letter116"], "cited_material_not_independently_consulted": True})
    add("st-chp8-p241-cagnacci-colour-description", "cand-0479", None,
        "described_as_di_colore_freschissimo",
        "Haskell quotes the description 'di colore freschissimo' for the Magdalene.", quotes["cagnacci_colour"], (363, 363),
        "This is an aesthetic description carried through Haskell's quotation; the cited letter was not independently consulted.",
        ["cand-0479", "cand-0478"], False,
        "A quoted aesthetic characterization, not a separate relation between entities.",
        {"footnote_marker": 1, "footnote_statement_ids": ["st-chp8-p241-note1-fogolari-letter116"], "quoted_speaker": "Letter 116 as quoted by Haskell; original not independently consulted", "cited_material_not_independently_consulted": True})
    add("st-chp8-p241-cassana-hunter-loan", "cand-1609", "cand-0599",
        "lent_cassana_portrait_of_a_hunter_to_1706_exhibition",
        "Haskell says Ferdinand also lent Cassana's Portrait of a Hunter.", quotes["cassana"], (363, 363),
        "The painting is indexed by title and painter; no further identity or location is supplied here.",
        ["cand-1609", "cand-0593", "cand-0599", "cand-7977"], True,
        "The source directly attributes the painting loan to Ferdinand.")
    add("st-chp8-p241-marco-ricci-landscape-loan", "cand-1609", "cand-8077",
        "probably_lent_four_marco_ricci_landscapes_to_1706_exhibition",
        "Haskell says Ferdinand almost certainly lent four landscapes by Marco Ricci.", quotes["marco_landscapes"], (363, 363),
        "The attribution is explicitly probable. Note 2 says the documentary lender is unnamed and only links two landscapes received by Ferdinand in May 1706 as a likely explanation.",
        ["cand-1609", "cand-2149", "cand-8077", "cand-7977"], True,
        "This is retained as a qualified loan candidate, not a certain documentary attribution.",
        {"footnote_marker": 2, "footnote_statement_ids": ["st-chp8-p241-note2-uncertain-landscape-lender"], "cited_material_not_independently_consulted": True})

    add("st-chp8-p241-florentine-absence-and-cardinal-loan", "cand-1609", "cand-7977",
        "showed_no_works_by_florentine_artists_from_his_collection",
        "Haskell says Ferdinand showed no works by Florentine artists represented in his collection.", quotes["florentine_absence"], (364, 364),
        "This is a negative statement about this exhibition; the unnamed artists are retained as a collective and no broader absence is inferred.",
        ["cand-1609", "cand-8103", "cand-7977"], False,
        "The negative absence is preserved as a source claim, not converted into a positive formal edge.")
    add("st-chp8-p241-florentine-hint-interpretation", "cand-1609", "cand-7977",
        "absence_of_florentine_works_interpreted_as_a_hint",
        "Haskell interprets the absence of Florentine works as an unmistakable hint.", quotes["hint"], (364, 364),
        "The hint's precise intended message is not specified; this records Haskell's interpretation only.",
        ["cand-1609", "cand-8103", "cand-7977"], False,
        "This is Haskell's interpretation of an absence, not a separate positive relation.")
    add("st-chp8-p241-cardinal-medici-loan", "cand-8074", "cand-8075",
        "lent_further_venetian_paintings_to_1706_exhibition",
        "Haskell says an unidentified Cardinal Medici lent further Venetian paintings to the exhibition.", quotes["cardinal_loan"], (364, 364),
        "Neither the Cardinal's identity nor the paintings are specified; do not identify him with another Medici by title alone.",
        ["cand-8074", "cand-8075", "cand-7977"], True,
        "The source explicitly attributes the additional paintings to Cardinal Medici and places them in this exhibition.")

    add("st-chp8-p241-venetian-and-neapolitan-contingents", "cand-8104", "cand-7977",
        "made_an_impressive_showing_at_1706_exhibition",
        "Haskell says Venetians made an impressive showing in the exhibition.", quotes["venetians"], (365, 365),
        "The group is collective and the individual works are not enumerated here; 'impressive' is Haskell's assessment.",
        ["cand-8104", "cand-7977"], True,
        "The passage describes the Venetian group as represented at the exhibition.")
    add("st-chp8-p241-neapolitan-contingent", "cand-8092", "cand-7977",
        "represented_neapolitan_works_at_1706_exhibition",
        "Haskell says the exhibition had a strong Neapolitan contingent.", quotes["neapolitan"], (365, 366),
        "The works and individual lenders are not identified beyond the collective qualification that follows.",
        ["cand-8092", "cand-7977"], True,
        "The source explicitly places the Neapolitan work group in the exhibition.")
    add("st-chp8-p241-del-rosso-neapolitan-lending", "cand-8078", "cand-8092",
        "mainly_lent_neapolitan_works_to_1706_exhibition",
        "Haskell says the Neapolitan contingent was mainly lent by the del Rosso brothers.", quotes["del_rosso"], (366, 366),
        "The brothers are treated as a collective lender; no individual member or contribution is inferred.",
        ["cand-8078", "cand-8092", "cand-7977"], True,
        "The passage explicitly attributes most of this work group to the del Rosso brothers.")
    add("st-chp8-p241-luca-giordano-presence", "cand-1172", "cand-7977",
        "represented_prominently_at_1706_exhibition",
        "Haskell says Luca Giordano was much in evidence at the exhibition.", quotes["luca"], (366, 366),
        "No particular Giordano painting is identified by this sentence.",
        ["cand-1172", "cand-7977", "cand-8092"], True,
        "The source directly reports Giordano's prominent representation in the exhibition.")

    add("st-chp8-p241-attendance-success-and-academy", "cand-1609", "cand-7977",
        "attended_1706_exhibition",
        "Haskell says Ferdinand himself attended the exhibition.", quotes["attended"], (367, 367),
        "The sentence reports attendance; it does not by itself establish Ferdinand's role in organizing the event.",
        ["cand-1609", "cand-7977"], True,
        "The source explicitly says Ferdinand attended the exhibition.")
    add("st-chp8-p241-exhibition-duration", "cand-7977", None,
        "remained_open_for_several_days",
        "Haskell says the exhibition remained open for several days.", quotes["duration"], (367, 367),
        "The exact opening and closing dates are not supplied in this sentence.",
        ["cand-7977"], False,
        "Duration is an event attribute rather than a relation between distinct entities.")
    add("st-chp8-p241-exhibition-success", "cand-7977", None,
        "evidently_a_success_in_haskells_assessment",
        "Haskell judges the exhibition to have been evidently successful.", quotes["success"], (367, 367),
        "This is explicitly Haskell's assessment; no independent measure of success is supplied.",
        ["cand-7977"], False,
        "A qualitative assessment of the event, not a distinct relation.")
    add("st-chp8-p241-ferdinand-illness", "cand-1609", None,
        "fell_seriously_ill_soon_after_exhibition",
        "Haskell says Ferdinand soon fell seriously ill.", quotes["illness"], (367, 367),
        "The illness is undiagnosed; 'soon after' follows the exhibition narrative.",
        ["cand-1609", "cand-7977"], False,
        "This records a health and chronology claim, not a formal relation.")
    add("st-chp8-p241-academy-organized-exhibition", "cand-0004", "cand-7977",
        "organized_exhibition_under_its_auspices",
        "Haskell says the Accademia del Disegno organized the exhibition under its auspices.", quotes["academy_organized"], (367, 367),
        "The source identifies the Academy's auspices but does not attribute all practical organization to it.",
        ["cand-0004", "cand-7977"], True,
        "The passage explicitly connects the Academy with the exhibition's auspices.")
    add("st-chp8-p241-academy-returned-to-inactivity", "cand-0004", None,
        "returned_to_inactivity_after_exhibition_and_ferdinands_illness",
        "Haskell says that after Ferdinand fell ill, the Accademia del Disegno returned to its former inactivity.", quotes["academy_dormancy"], (367, 367),
        "The description of the Academy's prior and subsequent inactivity is Haskell's characterization.",
        ["cand-0004", "cand-1609", "cand-7977"], False,
        "This is an institutional-state description rather than a relation to another knowledge object.")
    add("st-chp8-p241-later-exhibitions-before-ferdinands-death", "cand-8079", None,
        "similar_exhibitions_occurred_at_irregular_intervals_in_listed_years",
        "Haskell lists similar exhibitions in 1715, 1724, 1729, 1737, and 1767 at haphazard intervals.", quotes["later_events"], (367, 367),
        "The individual later events are not identified here. The printed year is 1737; the source OCR separates its digits, and the superscript after 1767 is footnote 3.",
        ["cand-8079"], False,
        "This records a sequence and timing of events, not a relation between distinct entities.",
        {"footnote_marker": 3, "footnote_statement_ids": ["st-chp8-p241-note3-1767-catalogue"], "ocr_corrections": [{"source_line": 367, "ocr": "173 7", "print": "1737", "basis": "CHP-8.pdf physical page 47"}, {"source_line": 367, "ocr": "1767?", "print": "1767³", "basis": "CHP-8.pdf physical page 47"}]})
    add("st-chp8-p241-ferdinand-died-before-later-exhibitions", "cand-1609", "cand-8079",
        "died_before_later_similar_exhibitions",
        "Haskell says Ferdinand died before any of the later similar exhibitions he lists.", quotes["ferdinand_died"], (368, 368),
        "The source establishes only that his death preceded all listed events; no death year is added here.",
        ["cand-1609", "cand-8079"], True,
        "The text explicitly states a temporal relation between Ferdinand's death and the later exhibition series.")

    add("st-chp8-p241-venetian-school-and-florence", "cand-8094", "cand-3461",
        "widely_recognized_as_italys_most_lively_painting_school_by_ferdinands_death",
        "Haskell says that by Ferdinand's death the Venetian school was widely recognized as the liveliest in Italy.", quotes["venetian_school"], (369, 369),
        "This is Haskell's broad retrospective assessment; the recognizing parties and measure of 'liveliness' are not specified.",
        ["cand-8094", "cand-3461", "cand-1609"], True,
        "The passage makes a source-attributed comparison between the Venetian school and painting in Italy.")
    add("st-chp8-p241-ferdinand-did-not-see-venetian-triumphs", "cand-1609", "cand-8094",
        "did_not_witness_triumphs_of_venetian_schools_greatest_masters",
        "Haskell says Ferdinand did not see the triumphs of the Venetian school's greatest masters.", quotes["masters_not_seen"], (369, 369),
        "No individual master or triumph is named; this remains a negative temporal claim.",
        ["cand-1609", "cand-8094"], False,
        "The negative temporal statement is retained as a claim, not a positive formal relation.")
    add("st-chp8-p241-ferdinand-satisfaction-in-promotion", "cand-1609", "cand-8100",
        "promoted_vital_contemporary_art",
        "Haskell says Ferdinand derived immense satisfaction from promoting what he regarded as most vital in contemporary art.", quotes["promotion"], (369, 369),
        "The selection of what was most vital is Haskell's characterization; no specific works or artists are enumerated here.",
        ["cand-1609", "cand-8100"], True,
        "The statement identifies Ferdinand's promotion of contemporary art as an activity, while retaining Haskell's evaluative wording.")
    add("st-chp8-p241-florence-painterly-centre", "cand-1041", "cand-12100",
        "served_as_centre_of_painterly_mode_for_a_few_years",
        "Haskell says Florence became a centre of the painterly mode for a few years under Ferdinand's patronage.", quotes["painterly"], (369, 369),
        "The phrase 'the painterly' is Haskell's broad art-historical characterization, not a named formal school; Ferdinand is the stated agent of the change.",
        ["cand-1609", "cand-1041", "cand-12100"], True,
        "The source explicitly characterizes Florence as a temporary centre of this artistic mode.",
        {"ocr_corrections": [{"source_line": 369, "ocr": "��painterly��", "print": "‘painterly’", "basis": "CHP-8.pdf physical page 47"}]})
    add("st-chp8-p241-classical-academic-practice-rome", "cand-12099", "cand-4490",
        "dictated_artistic_practice_in_rome",
        "Haskell says classical-academic theories dictated artistic practice in Rome.", quotes["classical_academic"], (369, 369),
        "This is Haskell's generalization; the theories are kept distinct from other classicism candidates pending identity alignment.",
        ["cand-12099", "cand-4490"], True,
        "The source explicitly connects the named theory group with artistic practice in Rome.")
    add("st-chp8-p241-artists-preferred-ferdinand", "cand-12101", "cand-1609",
        "would_have_been_delighted_to_work_for_ferdinand",
        "Haskell reasons that artists who felt their talents would be stifled in papal Rome would have been delighted to work for Ferdinand.", quotes["stifled_artists"], (369, 369),
        "This is Haskell's explanatory inference, not evidence that identified artists actually worked for Ferdinand; membership and number remain unspecified.",
        ["cand-12101", "cand-4490", "cand-1609"], False,
        "The statement is explicitly inferential and modal rather than a documented employment relation.")
    add("st-chp8-p241-ferdinand-role-art-patronage", "cand-1609", "cand-4131",
        "played_a_notable_part_in_accounts_of_italian_art_patronage",
        "Haskell says Ferdinand plays a notable part in accounts of Italian art patronage.", quotes["art_patronage_role"], (369, 369),
        "This is Haskell's evaluative summary of Ferdinand's historical significance, not a separate patronage event.",
        ["cand-1609", "cand-4131"], False,
        "The phrase is a historiographical assessment rather than a distinct formal relation.")
    add("st-chp8-p241-quoted-praise-and-art-patronage", "cand-1609", "cand-7847",
        "haskell_partly_accepts_mid_eighteenth_century_praise_of_ferdinand",
        "Haskell says one can understand, though not wholly endorse, a mid-eighteenth-century writer's description of Ferdinand as unrivalled in the world for magnanimity and generosity.", quotes["quoted_praise"], (369, 369),
        "Note 4 cites Sgrilli, p.3, but the cited page was not independently consulted; do not treat the quoted praise as an independently verified evaluation.",
        ["cand-1609", "cand-7847"], False,
        "This is Haskell's report and partial evaluation of a historical writer's praise, not a formal relation.",
        {"footnote_marker": 4, "footnote_statement_ids": ["st-chp8-p241-note4-sgrilli-locator"], "cited_material_not_independently_consulted": True, "quoted_speaker": "Unidentified mid-eighteenth-century writer as presented by Haskell; note 4 cites Sgrilli p.3"})
    add("st-chp8-p241-venice-concluding-assessment", "cand-12102", "cand-2719",
        "most_interesting_italian_painting_found_in_venice_by_that_time",
        "Haskell concludes that by that time the most interesting Italian painting was to be found in Venice, as Ferdinand had anticipated.", quotes["venice_closing"], (370, 370),
        "This is Haskell's evaluative art-historical and geographic assessment. 'By that time' follows the preceding account of Ferdinand's death; the prior anticipation is not independently established here.",
        ["cand-12102", "cand-2719", "cand-1609"], True,
        "The conclusion asserts a geographic concentration of Italian painting in Venice, while preserving Haskell's evaluative qualification.",
        {"footnote_marker": 5, "footnote_statement_ids": ["st-chp8-p241-note5-gabburri-correspondence", "st-chp8-p241-note5-gerini-follower"], "ocr_corrections": [{"source_line": 370, "ocr": "itself.5 .", "print": "itself.⁵", "basis": "CHP-8.pdf physical page 47"}]})

    # Add source-bound entities for the concepts and group, and repair the Italian-painting mention.
    candidate_text = candidates_bytes.decode("utf-8-sig")
    candidate_reader = csv.DictReader(io.StringIO(candidate_text))
    candidate_rows = list(candidate_reader)
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    if candidate_ids.intersection(c["candidate_id"] for c in NEW_CANDIDATES):
        raise SystemExit("one of the planned p.241 candidate ids already exists")
    max_candidate = max(int(cid.removeprefix("cand-")) for cid in candidate_ids if cid.startswith("cand-"))
    if [c["candidate_id"] for c in NEW_CANDIDATES] != [f"cand-{n}" for n in range(max_candidate + 1, max_candidate + 5)]:
        raise SystemExit(f"candidate ids are not the next four sequence values after cand-{max_candidate}")
    candidate_fields = list(candidate_reader.fieldnames or [])
    candidate_additions = []
    for c in NEW_CANDIDATES:
        candidate_additions.append({
            field: {
                "candidate_id": c["candidate_id"], "index_entry_id": "", "canonical_name": c["canonical_name"],
                "index_page_range": "", "suggested_type": c["suggested_type"], "status": "open",
                "index_source_file": "", "sub_entry": "", "detail": c["detail"], "exclude_reason": "",
                "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L{c['source_line']}",
            }.get(field, "") for field in candidate_fields
        })

    source_mentions = [
        ("m-chp8-p241-classical-academic-theories", "cand-12099", "the classical-academic theories which dictated practice in Rome", "Distinct source-defined theory group; not yet aligned with other classicism candidates."),
        ("m-chp8-p241-painterly-mode", "cand-12100", "painterly", "Haskell's substantivized art-historical mode; quotation glyphs are OCR-corrupted in S0."),
        ("m-chp8-p241-artists-stifled-rome", "cand-12101", "artists who rightly felt that their talents would have been stifled in the papal city", "Unnamed group in Haskell's explanatory inference."),
        ("m-chp8-p241-schedoni-work", "cand-8091", "Schedoni.", "Unidentified painting designated by its painter; punctuation extends the work mention beyond the nested painter mention."),
    ]
    mention_reader = csv.DictReader(io.StringIO(mentions_bytes.decode("utf-8-sig")))
    mention_fieldnames = list(mention_reader.fieldnames or [])
    mention_additions = []
    for mid, cid, surface, note in source_mentions:
        start = segment_text.find(surface)
        if start < 0:
            raise SystemExit(f"mention source span not found: {surface!r}")
        end = start + len(surface)
        if segment_text[start:end] != surface:
            raise SystemExit(f"mention span mismatch: {mid}")
        mention_additions.append({
            field: {"mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
                    "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note}.get(field, "")
            for field in mention_fieldnames
        })

    mention_patch = {
        "m-chp8-p240-241-italian-painting-venice": {
            "expected_candidate_id": "cand-3461",
            "changes": {"candidate_id": "cand-12102", "note": "Italian painting as a source-local art-historical category; distinct from the place Italy and the broader Italian art candidate."},
        }
    }
    mentions_output, mention_patch_count, mention_add_count = update_csv(
        mentions_bytes, patch_ids=mention_patch, additions=mention_additions)
    candidates_output, candidate_patch_count, candidate_add_count = update_csv(
        candidates_bytes, additions=candidate_additions)
    if candidate_patch_count != 0 or candidate_add_count != len(NEW_CANDIDATES):
        raise SystemExit("candidate CSV write plan mismatch")

    segment_rows = [r for r in rows if r.get("segment_id") == SEGMENT]
    if {r["statement_id"] for r in segment_rows} != EXPECTED_EXISTING | new_ids:
        raise SystemExit("p.241 post-edit statement id set does not match plan")
    if any(r.get("qualifiers", {}).get("relation_candidate") not in (True, False) for r in segment_rows):
        raise SystemExit("p.241 has an unset or invalid relation_candidate")
    if any(r["original_quote"] not in segment_text for r in segment_rows):
        bad = [r["statement_id"] for r in segment_rows if r["original_quote"] not in segment_text]
        raise SystemExit(f"p.241 quote is not an exact source substring: {bad}")

    preview = {
        "mode": "dry-run", "p241_original_statements": len(EXPECTED_EXISTING),
        "p241_new_statements": len(new_ids), "p241_statement_total": len(segment_rows),
        "p241_relation_candidate_flags": {
            "true": sum(r["qualifiers"]["relation_candidate"] is True for r in segment_rows),
            "false": sum(r["qualifiers"]["relation_candidate"] is False for r in segment_rows),
        },
        "new_candidates": [c["candidate_id"] for c in NEW_CANDIDATES],
        "new_mentions": mention_add_count, "corrected_mention_mappings": mention_patch_count,
        "source_quote_and_mention_span_checks": "passed",
        "footnotes_linked": sorted(required_note_ids),
        "total_book_statements_after_write": len(rows),
        "corrected_endpoints": {
            "artists_stifled_in_Rome": ["cand-4490 (Rome)", "cand-12101 (unnamed artist group)"],
            "Italian_painting": ["cand-3461 (Italy)", "cand-12102 (Italian painting concept)"],
        },
        "ocr_corrections": [
            "p.241 L367 printed 1737; source Markdown has '173 7'",
            "p.241 L367 printed footnote 3 after 1767; source Markdown has '?'",
            "p.241 L369 printed ‘painterly’; S0 quote glyphs are corrupted",
            "p.241 L370 printed footnote 5 after 'itself'; S0 has trailing ' .', source left unchanged",
        ],
    }
    return preview, jsonl_bytes(rows), mentions_output, candidates_output


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write after all preconditions and semantic checks pass")
args = parser.parse_args()
preview, table_output, mentions_output, candidates_output = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
else:
    expected_digests = {TABLE: EXPECTED_TABLE_SHA256, MENTIONS: EXPECTED_MENTIONS_SHA256, CANDIDATES: EXPECTED_CANDIDATES_SHA256}
    for path in (TABLE, MENTIONS, CANDIDATES):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if sha(backup.read_bytes()).lower() != expected_digests[path].lower():
                raise SystemExit(f"existing backup does not match the guarded pre-write source: {backup}")
        else:
            shutil.copy2(path, backup)
    atomic_write(TABLE, table_output)
    atomic_write(MENTIONS, mentions_output)
    atomic_write(CANDIDATES, candidates_output)
    preview["mode"] = "applied"
    preview["backups"] = [str(p.with_name(p.name + BACKUP_SUFFIX).relative_to(ROOT)) for p in (TABLE, MENTIONS, CANDIDATES)]
    print(json.dumps(preview, ensure_ascii=False, indent=2))
