from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
PAGE_IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p330_page_review_20261014.png"
NOTES_IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p330_notes_zoom_20261014.png"

SEGMENT = "chp-10:10_CHP-10_sec_ii:l258-267"
NOTE_SEGMENT = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
BACKUP_SUFFIX = ".bak-s2-chp10-p330-semantic-reconciliation-20261014"

EXPECTED = {
    STATEMENTS.name: "02f786c62cb0e42de5db7ea01a5415429208238f9b1e7a813aef04f573d9d7f2",
    MENTIONS.name: "bfbea89915234deb7c7ff862f835fdb03e3230376358e75d8cd7dce40d49008d",
    CANDIDATES.name: "8559728c6c477ae823abc74d04eb71011ebc2ad1dd0c69ba29c3876df28e259e",
    COVERAGE.name: "ff87d1a0232ad5a342018d20cf7709346e013e1ec9f81f2c6a86a92c54a09d37",
    SOURCE.name: "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    PAGE_IMAGE.name: "ccce47208c600c7e52a8664a0e9227ae0a7df2d5f1eca1422284a3a7dce25569",
    NOTES_IMAGE.name: "1286e68c3d58d04378a267194823cbc834899d768f9a143e2e87ad558921191f",
}

EXPECTED_BODY_IDS = {
    "st-chp10-p330-memmo-artistic-freedom",
    "st-chp10-p330-memmo-dues-query",
    "st-chp10-p330-memmo-inquisitori-and-sheet",
    "st-chp10-p330-memmo-vasari-academy-queries",
    "st-chp10-p330-n04-ii-martyn",
    "st-chp10-p330-n04-iii-gazzetta",
    "st-chp10-p330-patronage-debate",
    "st-chp10-p330-reform-comparisons-and-professions",
    "st-chp10-p330-status-debate-continuation",
    "st-chp10-p330-venetian-exhibition-sites-open",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def load_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def dump_csv(fields: list[str], rows: list[dict]) -> bytes:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def quote_between(lines: list[str], first: int, last: int, start: str, end: str) -> str:
    block = "\n".join(lines[first - 1:last])
    a = block.find(start)
    if a < 0:
        raise ValueError(f"quote start missing at {first}-{last}: {start!r}")
    b = block.find(end, a if start == end else a + len(start))
    if b < 0:
        raise ValueError(f"quote end missing at {first}-{last}: {end!r}")
    return block[a:b + len(end)]


def new_statement(
    sid: str,
    subject: str | None,
    obj: str | None,
    predicate: str,
    quote: str,
    start: int,
    end: int,
    claim: str,
    speaker: str,
    text_layer: str,
    qualification: str,
    mentions: list[str],
    relation: bool,
    **extra: object,
) -> dict:
    qualifiers: dict[str, object] = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 330,
        "pdf_physical_page": 63,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentions,
        "relation_candidate": relation,
    }
    qualifiers.update(extra)
    return {
        "statement_id": sid,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after exact-hash and semantic preflight")
    args = parser.parse_args()

    paths = [STATEMENTS, MENTIONS, CANDIDATES, COVERAGE, SOURCE, PAGE_IMAGE, NOTES_IMAGE]
    hashes = {path.name: sha(path) for path in paths}
    if hashes != EXPECTED:
        raise SystemExit(f"preflight hash mismatch; no writes made: {hashes}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    body_text = "\n".join(source_lines[257:267])
    statements = load_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement_id in current table")
    body_ids = {row["statement_id"] for row in statements if row.get("segment_id") == SEGMENT}
    if body_ids != EXPECTED_BODY_IDS:
        raise SystemExit(f"p.330 body statement set mismatch: {sorted(body_ids ^ EXPECTED_BODY_IDS)}")

    p329 = by_id.get("st-chp10-p329-artist-status-debate-open")
    p331 = by_id.get("st-chp10-p331-piazza-display-completion")
    if not p329 or not p331:
        raise SystemExit("p.329/p.331 continuation endpoints are missing")
    if p329["qualifiers"].get("continuation_closed_by_statement_id") != "st-chp10-p330-status-debate-continuation":
        raise SystemExit("p.329 artist-status continuation link changed")
    if by_id["st-chp10-p330-venetian-exhibition-sites-open"]["qualifiers"].get("continuation_closed_by_statement_id") != p331["statement_id"]:
        raise SystemExit("p.330/p.331 exhibition-site continuation link changed")

    candidate_fields, candidates = load_csv(CANDIDATES)
    candidate_ids = {row["candidate_id"] for row in candidates}
    numeric_ids = [int(row["candidate_id"].split("-", 1)[1]) for row in candidates
                   if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-", 1)[1].isdigit()]
    if max(numeric_ids) != 12117 or "cand-12118" in candidate_ids:
        raise SystemExit(f"candidate sequence changed; max={max(numeric_ids)}")

    mention_fields, mentions = load_csv(MENTIONS)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("duplicate mention_id in current table")
    existing_checks = {
        "m-s2-ch10-p330-0001": ("cand-1642", "Andrea Memmo"),
        "m-s2-ch10-p330-0006": ("cand-0498", "C."),
        "m-s2-ch10-p330-0038": ("cand-0138", "Scuola"),
    }
    for mid, (candidate_id, surface) in existing_checks.items():
        row = mention_by_id.get(mid)
        if not row or row["candidate_id"] != candidate_id or row["surface_form"] != surface:
            raise SystemExit(f"mention preflight mismatch for {mid}")
        start = int(row["start_char"])
        if body_text[start:start + len(surface)] != surface:
            raise SystemExit(f"mention offset changed for {mid}")
    if "m-s2-ch10-p330-0043" in mention_by_id:
        raise SystemExit("new p.330 Vasari-work mention ID already exists")

    coverage_fields, coverage = load_csv(COVERAGE)
    coverage_row = next((r for r in coverage if r.get("segment_id") == SEGMENT), None)
    if not coverage_row:
        raise SystemExit("p.330 coverage row is missing")

    def update(
        sid: str,
        *,
        predicate: str | None = None,
        subject: str | None = None,
        obj: str | None = None,
        set_subject: bool = False,
        set_obj: bool = False,
        quote: str | None = None,
        claim: str | None = None,
        speaker: str | None = None,
        text_layer: str | None = None,
        qualification: str | None = None,
        mentioned: list[str] | None = None,
        relation: bool | None = None,
        start: int | None = None,
        end: int | None = None,
        remove: tuple[str, ...] = (),
        **extra: object,
    ) -> None:
        row = by_id[sid]
        q = row.setdefault("qualifiers", {})
        if predicate is not None:
            row["predicate"] = predicate
        if set_subject:
            row["subject_candidate_id"] = subject
        if set_obj:
            row["object_candidate_id"] = obj
        if quote is not None:
            row["original_quote"] = quote
        if claim is not None:
            q["claim"] = claim
        if speaker is not None:
            q["speaker"] = speaker
        if text_layer is not None:
            q["text_layer"] = text_layer
        if qualification is not None:
            q["qualification"] = qualification
        if mentioned is not None:
            q["mentioned_candidate_ids"] = mentioned
        if relation is not None:
            q["relation_candidate"] = relation
        if start is not None:
            q["source_line_start"] = start
        if end is not None:
            q["source_line_end"] = end
        for key in remove:
            q.pop(key, None)
        q.update(extra)

    added_statements: list[dict] = []

    def add(*args: object, **kwargs: object) -> dict:
        row = new_statement(*args, **kwargs)  # type: ignore[arg-type]
        sid = row["statement_id"]
        if sid in by_id or any(existing["statement_id"] == sid for existing in added_statements):
            raise SystemExit(f"new statement ID already exists: {sid}")
        added_statements.append(row)
        by_id[sid] = row
        return row

    # Keep the queried painter local and unidentified; the note's Canaletto suggestion remains separate.
    candidates.append({
        "candidate_id": "cand-12118",
        "index_entry_id": "",
        "canonical_name": "Unidentified Venetian painter C. in Andrea Memmo's reform query",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell's note says the letter C. almost certainly refers to Canaletto, but immediately records a chronology tension. Preserve the unnamed person as source-local and do not identify C. with Canaletto in S2.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L260",
    })
    candidate_ids.add("cand-12118")

    # Existing mention C. is not the established Canaletto identity. The question also names a source-local work.
    mention_by_id["m-s2-ch10-p330-0006"]["candidate_id"] = "cand-12118"
    mention_by_id["m-s2-ch10-p330-0006"]["note"] = "Haskell's note offers Canaletto as an almost-certain hypothesis but notes a chronology tension; this source-local candidate remains unidentified."
    mention_by_id["m-s2-ch10-p330-0038"]["candidate_id"] = "cand-8588"
    mention_by_id["m-s2-ch10-p330-0038"]["note"] = "Scuola names the exhibition venue in Martyn's cited passage; exact church/institution identity remains unresolved."
    vasari_start = body_text.find("Vasari")
    vasari_end = body_text.find("Montorsoli.", vasari_start)
    if vasari_start < 0 or vasari_end < 0:
        raise SystemExit("Vasari's Life of Montorsoli span is missing from the p.330 segment")
    vasari_surface = body_text[vasari_start:vasari_end + len("Montorsoli")]
    mentions.append({
        "mention_id": "m-s2-ch10-p330-0043",
        "segment_id": SEGMENT,
        "candidate_id": "cand-9864",
        "surface_form": vasari_surface,
        "start_char": str(vasari_start),
        "end_char": str(vasari_end + len("Montorsoli")),
        "note": "The work Memmo reminds himself to read; mapped to the source-local literary-work candidate, not to Vasari as a person.",
    })
    mention_by_id["m-s2-ch10-p330-0043"] = mentions[-1]

    # Split the office membership claim from the independently cited archival sheet.
    office_quote = quote_between(source_lines, 259, 260, "was one of the", "reorganisation of the guilds.")
    update(
        "st-chp10-p330-memmo-inquisitori-and-sheet",
        predicate="served_as_member_of_body_concerned_with_guild_reorganisation",
        quote=office_quote,
        claim="Haskell identifies Andrea Memmo as one of the Inquisitori alle Arti, a body concerned with guild reorganisation.",
        speaker="Haskell",
        text_layer="authorial narrative",
        qualification="The page image reads Inquisitori alle Arti, distinct from Inquisitori di Stato. This records Haskell's attribution of membership and remit; institutional identity awaits later alignment.",
        mentioned=["cand-1642", "cand-9851"],
        relation=True,
        start=259,
        end=260,
        remove=("footnote_marker", "footnote_segment", "footnote_refs", "footnote_statement_ids", "footnote_body_link_status"),
    )
    sheet_quote = quote_between(source_lines, 260, 260, "Among his papers there survives a sheet", "preparing his-report.")
    sheet_statement = add(
        "st-chp10-p330-memmo-preparatory-sheet",
        "cand-1642",
        "cand-9857",
        "prepared_report_with_queries_recorded_on_sheet",
        sheet_quote,
        260,
        260,
        "Haskell says a sheet among Memmo's papers records queries he briefly wrote while preparing his report.",
        "Haskell",
        "authorial narrative",
        "The sheet is known here through Haskell and the book's Appendix 6 reference, not through independent archival consultation.",
        ["cand-1642", "cand-9857"],
        True,
        footnote_marker=1,
        footnote_segment=NOTE_SEGMENT,
        footnote_refs=[{"marker": 1, "segment_id": NOTE_SEGMENT, "source_line": 346}],
        footnote_statement_ids=["st-chp10-p330-n01-memmo-sheet-appendix"],
        footnote_body_link_status="linked",
        ocr_corrections=[{"source_line": 260, "ocr": "his-report", "print": "his report"}],
    )

    # Separate the three content units in Memmo's quoted preparatory queries.
    dues_policy_quote = quote_between(source_lines, 260, 260, "It will be necessary", "those men who practise them,")
    add(
        "st-chp10-p330-memmo-dues-policy-query",
        "cand-1642",
        "cand-9852",
        "proposed_freeing_liberal_arts_practitioners_from_dues",
        dues_policy_quote,
        260,
        260,
        "In the quoted preparatory note, Memmo says liberal-arts practitioners should be freed from subjection to dues.",
        "Andrea Memmo as quoted by Haskell",
        "quoted preparatory note",
        "This is a draft proposal, not evidence that an exemption was enacted.",
        ["cand-1642", "cand-9867", "cand-9852"],
        True,
    )
    temperament_quote = quote_between(source_lines, 260, 260, "to explain how strange is the temperament", "of Painters.")
    add(
        "st-chp10-p330-memmo-painter-temperament-query",
        "cand-1642",
        "cand-3151",
        "queried_painters_temperament",
        temperament_quote,
        260,
        260,
        "Memmo's preparatory query proposes explaining what he calls the strange temperament of painters.",
        "Andrea Memmo as quoted by Haskell",
        "quoted preparatory note",
        "This is Memmo's question in a draft note, not a general finding about painters.",
        ["cand-1642", "cand-3151"],
        True,
    )
    c_query_quote = quote_between(source_lines, 260, 260, "An example is the famous living Venetian painter C.", "Why does C. claim to be freed from taxes?")
    update(
        "st-chp10-p330-memmo-dues-query",
        predicate="questioned_unidentified_painters_claimed_tax_exemption",
        quote=c_query_quote,
        claim="Memmo asks why the unnamed living Venetian painter C. claims to be freed from taxes.",
        speaker="Andrea Memmo as quoted by Haskell",
        text_layer="quoted preparatory query",
        qualification="This is a draft question, not evidence of an enacted exemption. The source-local painter C. remains unidentified; Haskell's qualified Canaletto hypothesis and chronology tension remain in note 2.",
        mentioned=["cand-1642", "cand-12118", "cand-9852"],
        relation=True,
        start=260,
        end=260,
    )
    update(
        "st-chp10-p330-reform-comparisons-and-professions",
        relation=False,
        qualification="These are questions and possible models in a preparatory note, not evidence that reforms were adopted or formal relationships were established.",
    )

    # The reading reminder and the Academy questions are separate claims; note 3 supports the work reference.
    vasari_read_quote = quote_between(source_lines, 261, 261, "He looks to the past", "Montorsoli.3")
    update(
        "st-chp10-p330-memmo-vasari-academy-queries",
        predicate="queried_venetian_academy_device_name_and_patron_saint",
        quote=quote_between(source_lines, 261, 261, "He even wonders", "Academy placed?"),
        claim="Haskell says Memmo wondered whether the Venetian Academy's device and name could be improved and asked which saint protected it.",
        speaker="Haskell",
        text_layer="authorial narrative",
        qualification="The passage reports questions, not an adopted emblem or name and not an identified patron saint.",
        mentioned=["cand-1642", "cand-0005"],
        relation=True,
        start=261,
        end=261,
        remove=("footnote_marker", "footnote_segment", "footnote_refs", "footnote_statement_ids", "footnote_body_link_status"),
    )
    add(
        "st-chp10-p330-memmo-read-vasari-life",
        "cand-1642",
        "cand-9864",
        "reminded_himself_to_read_life_of_montorsoli",
        vasari_read_quote,
        261,
        261,
        "Haskell says Memmo reminds himself to read Vasari's Life of Montorsoli.",
        "Haskell reporting Memmo's note",
        "authorial narrative reporting a preparatory note",
        "The title is linked to the source-local work candidate; the cited text is not independently consulted.",
        ["cand-1642", "cand-2702", "cand-1699", "cand-9864"],
        True,
        footnote_marker=3,
        footnote_segment=NOTE_SEGMENT,
        footnote_refs=[{"marker": 3, "segment_id": NOTE_SEGMENT, "source_line": 348}],
        footnote_statement_ids=["st-chp10-p330-n03-vasari-life"],
        footnote_body_link_status="linked",
    )

    # Keep Memmo's quoted position distinct from Haskell's evaluation of his unusual outlook.
    freedom_quote = quote_between(source_lines, 261, 261, "It is right that the imaginative side", "That is why they were called liberal.")
    update(
        "st-chp10-p330-memmo-artistic-freedom",
        quote=freedom_quote,
        claim="In the quoted note, Memmo says painting's imaginative side should be practised freely and nobly and genius should not be fettered.",
        speaker="Andrea Memmo as quoted by Haskell",
        text_layer="quotation",
        qualification="This is an attributed position in a preparatory note, not evidence of an enacted policy.",
        mentioned=["cand-1642", "cand-9735", "cand-9867"],
        relation=True,
    )
    exceptional_quote = quote_between(source_lines, 261, 261, "But Memmo, with his interest", "not wholly new.")
    add(
        "st-chp10-p330-memmo-exceptional-administrator",
        "cand-1642",
        None,
        "described_as_exceptional_among_administrators",
        exceptional_quote,
        261,
        261,
        "Haskell characterizes Memmo as exceptional among administrators while saying his ideas were not wholly new.",
        "Haskell",
        "authorial evaluation",
        "This is Haskell's comparative assessment; it does not identify a specific administrator group or establish a relation to an individual.",
        ["cand-1642", "cand-9735", "cand-3151", "cand-3585"],
        False,
    )

    # The unfinished artist-status sentence closes here; the adjacent patronage debate is split by claim.
    update(
        "st-chp10-p330-status-debate-continuation",
        relation=False,
        continuation_from_statement_id="st-chp10-p329-artist-status-debate-open",
        continuation_status="closed",
    )
    p329["qualifiers"]["continuation_to_statement_id"] = "st-chp10-p330-status-debate-continuation"
    p329["qualifiers"]["continuation_status"] = "closed"
    unchanged_quote = quote_between(source_lines, 262, 262, "The status of the artist", "remained unchanged,")
    add(
        "st-chp10-p330-artist-status-unchanged",
        "cand-0140",
        None,
        "status_remained_unchanged",
        unchanged_quote,
        262,
        262,
        "Haskell says the artist's social status remained unchanged.",
        "Haskell",
        "authorial narrative",
        "This is a general historical statement, not a relation to the Academy or to a named person.",
        ["cand-0140"],
        False,
    )
    survival_quote = quote_between(source_lines, 262, 263, "and the only theoretical question", "bring patrons into being.")
    add(
        "st-chp10-p330-traditional-patronage-survival-question",
        "cand-9855",
        None,
        "debated_whether_traditional_patronage_was_necessary_for_art_survival",
        survival_quote,
        262,
        263,
        "Haskell reports debate over whether traditional patronage was necessary for art to survive or whether great art would attract patrons.",
        "Haskell",
        "authorial narrative reporting a theoretical debate",
        "This records the question under discussion; it does not assert either position as a settled fact.",
        ["cand-0140", "cand-0005", "cand-9855", "cand-0041"],
        False,
    )
    algarotti_quote = quote_between(source_lines, 262, 263, "as\nFrancesco\" Algarotti maintained", "bring patrons into being.")
    update(
        "st-chp10-p330-patronage-debate",
        predicate="argued_great_art_would_itself_attract_patrons",
        set_subject=True,
        subject="cand-0041",
        set_obj=True,
        obj="cand-9855",
        quote=algarotti_quote,
        claim="Haskell attributes to Francesco Algarotti the view that the existence of great art would itself bring patrons into being.",
        speaker="Francesco Algarotti as reported by Haskell",
        text_layer="authorial narrative reporting an attributed argument",
        qualification="This is Haskell's attribution of one position in a theoretical debate, not an independently consulted Algarotti text.",
        mentioned=["cand-0041", "cand-9855"],
        relation=True,
        start=262,
        end=263,
    )

    # The exhibition site continues onto p.331; split Martyn's two reported events and the Gazzetta notice.
    update(
        "st-chp10-p330-venetian-exhibition-sites-open",
        relation=True,
    )
    martyn_common = {
        "speaker": "Thomas Martyn as quoted by Haskell",
        "text_layer": "indirect printed-source quotation",
        "qualification": "Haskell cites Martyn, p.448; neither the book nor cited page was independently consulted. Preserve the source wording and avoid identifying the exact church or institution beyond S. Rocco / Scuola.",
        "mentioned": ["cand-9858", "cand-9865", "cand-9866", "cand-8588"],
        "relation": True,
        "footnote_marker": 4,
        "footnote_segment": NOTE_SEGMENT,
        "footnote_refs": [{"marker": 4, "segment_id": SEGMENT, "source_line": 265}],
        "footnote_statement_ids": ["st-chp10-p330-n04-haskell-levey", "st-chp10-p330-n04-i-nunzio-report", "st-chp10-p330-n04-ii-martyn", "st-chp10-p330-n04-iii-gazzetta"],
        "footnote_body_link_status": "linked",
    }
    procession_quote = quote_between(source_lines, 265, 265, "On S. Rocco", "that Saint’s church:")
    update(
        "st-chp10-p330-n04-ii-martyn",
        predicate="reported_signory_procession_to_s_rocco",
        set_subject=True,
        subject="cand-9865",
        set_obj=True,
        obj="cand-8588",
        quote=procession_quote,
        claim="Martyn's cited passage says the Signory goes in procession to S. Rocco's church on the saint's day.",
        speaker="Thomas Martyn as quoted by Haskell",
        text_layer="indirect printed-source quotation",
        qualification="Haskell cites Martyn, p.448; neither the book nor cited page was independently consulted. Retain Signory as named and do not normalize it to the Venetian Senate.",
        mentioned=["cand-9858", "cand-9865", "cand-8588"],
        relation=True,
        start=265,
        end=265,
        **{k: v for k, v in martyn_common.items() if k not in {"speaker", "text_layer", "qualification", "mentioned", "relation"}},
    )
    painters_quote = quote_between(source_lines, 265, 266, "and the painters of the present Venetian school", "Scuola.")
    add(
        "st-chp10-p330-n04-ii-painters-exhibited",
        "cand-9866",
        "cand-8588",
        "exhibited_performances_at_scuola_on_s_rocco_day",
        painters_quote,
        265,
        266,
        "Martyn's cited passage says painters of the present Venetian school exhibit their performances in the Scuola on S. Rocco's day.",
        martyn_common["speaker"],
        martyn_common["text_layer"],
        martyn_common["qualification"],
        martyn_common["mentioned"],
        True,
        footnote_marker=4,
        footnote_segment=NOTE_SEGMENT,
        footnote_refs=[{"marker": 4, "segment_id": SEGMENT, "source_line": 265}],
        footnote_statement_ids=martyn_common["footnote_statement_ids"],
        footnote_body_link_status="linked",
    )

    portrait_quote = quote_between(source_lines, 266, 267, "De", "nulla piu si potrebbe desiderare.")
    portrait_corrections = [
        {"source_line": 266, "ocr": "ku", "print": "fu"},
        {"source_line": 267, "ocr": "Nassi [sir", "print": "Nassi [sic"},
        {"source_line": 267, "ocr": "piu", "print": "più"},
    ]
    update(
        "st-chp10-p330-n04-iii-gazzetta",
        predicate="reported_praise_of_doge_foscarini_portrait_attributed_to_nassi",
        quote=portrait_quote,
        claim="The cited 1762 Nuova Gazzetta Veneta notice praises a portrait of Doge Marco Foscarini attributed there to Signor Nassi [sic—Nazari?].",
        speaker="Nuova Gazzetta Veneta notice as quoted by Haskell",
        text_layer="indirect printed-source quotation",
        qualification="Haskell's transcription of the notice is not independently checked. Preserve the printed uncertainty sic—Nazari?; do not identify Nassi with an indexed Nazari.",
        mentioned=["cand-9860", "cand-1053", "cand-9861", "cand-9862"],
        relation=True,
        start=266,
        end=267,
        ocr_corrections=portrait_corrections,
    )
    other_works_quote = quote_between(source_lines, 267, 267, "Vi si videro anche altre Opere", "tutti ebbero la dovuta lode.")
    add(
        "st-chp10-p330-n04-iii-other-works-praised",
        "cand-9860",
        None,
        "notice_reported_praise_of_other_old_and_living_painters_works",
        other_works_quote,
        267,
        267,
        "The notice also says other works by old and living painters were seen and received due praise.",
        "Nuova Gazzetta Veneta notice as quoted by Haskell",
        "indirect printed-source quotation",
        "The other works and painters are not individually identified; this report is not independently checked.",
        ["cand-9860", "cand-9866"],
        False,
        footnote_marker=4,
        footnote_segment=NOTE_SEGMENT,
        footnote_refs=[{"marker": 4, "segment_id": SEGMENT, "source_line": 266}],
        footnote_statement_ids=["st-chp10-p330-n04-haskell-levey", "st-chp10-p330-n04-i-nunzio-report", "st-chp10-p330-n04-ii-martyn", "st-chp10-p330-n04-iii-gazzetta"],
        footnote_body_link_status="linked",
    )

    # The scan records these readings without changing the immutable S0 transcription.
    n01 = by_id["st-chp10-p330-n01-memmo-sheet-appendix"]["qualifiers"]
    n01["ocr_corrections"] = [{"source_line": 346, "ocr": "in. full", "print": "in full"}]
    n02 = by_id["st-chp10-p330-n02-canaletto-hypothesis"]["qualifiers"]
    n02["ocr_corrections"] = [{"source_line": 347, "ocr": "refers��to", "print": "refers to"}]
    n03 = by_id["st-chp10-p330-n03-vasari-life"]["qualifiers"]
    n03["ocr_corrections"] = [{"source_line": 348, "ocr": "Lise", "print": "Life"}]
    n03["linked_body_statement_ids"] = ["st-chp10-p330-memmo-read-vasari-life"]
    n01["linked_body_statement_ids"] = ["st-chp10-p330-memmo-preparatory-sheet"]
    n02["linked_body_statement_ids"] = ["st-chp10-p330-memmo-dues-query"]
    # Keep the footnote's note-to-body map complete after splitting its two cited extracts.
    p330_sites = by_id["st-chp10-p330-venetian-exhibition-sites-open"]["qualifiers"]
    footnote_ids = list(p330_sites.get("footnote_statement_ids", []))
    for sid in ["st-chp10-p330-n04-ii-painters-exhibited", "st-chp10-p330-n04-iii-other-works-praised"]:
        if sid not in footnote_ids:
            footnote_ids.append(sid)
    p330_sites["footnote_statement_ids"] = footnote_ids
    for sid in ["st-chp10-p330-n04-haskell-levey", "st-chp10-p330-n04-i-nunzio-report", "st-chp10-p330-n04-ii-martyn", "st-chp10-p330-n04-iii-gazzetta"]:
        note_q = by_id[sid]["qualifiers"]
        note_q["linked_body_statement_ids"] = ["st-chp10-p330-venetian-exhibition-sites-open"]
    mention_by_id["m-s2-ch10-p330-0041"]["note"] = "The scanned note reads '[sic—Nazari?]'; retain the qualification and do not map this candidate to an indexed Nazari as a settled identity."

    # One segment-level record documents what was semantically reconciled and what follows in source order.
    coverage_row["note"] = "p.330 L258-267 semantically classified, including the note 4 extracts printed on this page. Page 330 and note scans confirm the recorded OCR corrections; the source transcription remains unchanged. Painter C. remains unidentified. The artist-status sentence closes p.329; the Piazza S. Marco description closes at p.331 L270. Consolidated note records remain in their source segment for the later note pass."

    statements.extend(added_statements)
    new_body_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(new_body_rows) != 19:
        raise SystemExit(f"expected 19 p.330 body rows after split, found {len(new_body_rows)}")
    statuses = {True: 0, False: 0, "unset": 0}
    for row in new_body_rows:
        status = row.get("qualifiers", {}).get("relation_candidate", "unset")
        statuses[status] += 1
    if statuses != {True: 13, False: 6, "unset": 0}:
        raise SystemExit(f"unexpected p.330 status distribution: {statuses}")
    if any(not row.get("qualifiers", {}).get("claim") or not row.get("original_quote") for row in added_statements):
        raise SystemExit("new statement missing claim or source quote")
    if body_text[int(mention_by_id["m-s2-ch10-p330-0043"]["start_char"]):int(mention_by_id["m-s2-ch10-p330-0043"]["end_char"])] != vasari_surface:
        raise SystemExit("new Vasari-work mention span failed exact-source check")

    output = {
        STATEMENTS: dump_jsonl(statements),
        MENTIONS: dump_csv(mention_fields, mentions),
        CANDIDATES: dump_csv(candidate_fields, candidates),
        COVERAGE: dump_csv(coverage_fields, coverage),
    }
    print("p.330 semantic reconciliation preview")
    print(f"body rows: {len(new_body_rows)}; relation_candidate true/false/unset: {statuses[True]}/{statuses[False]}/{statuses['unset']}")
    print("new candidate: cand-12118 (unidentified painter C.; open, no Canaletto identity merge)")
    print("mentions: remap m-s2-ch10-p330-0006 to cand-12118; remap 0038 Scuola to cand-8588; add 0043 Vasari's Life of Montorsoli to cand-9864")
    print("new statements:")
    for row in added_statements:
        print(f"  {row['statement_id']}: relation_candidate={row['qualifiers']['relation_candidate']} | {row['original_quote'][:110].replace(chr(10), ' / ')}")
    print("cross-page links: p.329 artist-status -> p.330 closure; p.330 Piazza S. Marco -> p.331 completion retained")
    print("footnote links 1-4 refreshed; S0 transcription not modified")
    print("planned output hashes:")
    for path, data in output.items():
        print(f"  {path.name}: {hashlib.sha256(data).hexdigest()}")
    if not args.apply:
        print("preview only; no files written (use --apply after reviewing this exact plan)")
        return 0

    backups: list[tuple[Path, Path]] = []
    for path in output:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    for path, data in output.items():
        path.write_bytes(data)
    print("applied; recoverable backups:")
    for _, backup in backups:
        print(f"  {backup.name}")
    print("written hashes:")
    for path in output:
        print(f"  {path.name}: {sha(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
