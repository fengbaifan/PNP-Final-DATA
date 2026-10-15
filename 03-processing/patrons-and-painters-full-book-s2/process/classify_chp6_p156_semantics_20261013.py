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
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
SEGMENT = "chp-6:06_CHP-6_sec_i:l112-118"
FOOTNOTE_SEGMENT = "chp-6:06_CHP-6_sec_i:l120-157"
BACKUP_SUFFIX = ".bak-s2-chp6-p156-semantics-20261013"

EXPECTED_HASHES = {
    SOURCE: "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    STATEMENTS: "a951fac556b6ab9c9c4028e19df07cbfd65cbb18091768484c8868aaaa606642",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    MENTIONS: "276c7a57f8deb1f109fcbc87036cebed1ca7a1019d35bd64c4230551219e0803",
    COVERAGE: "485693a483a20d614ae223d5908342007566fdfa26c15771ad3a3421d227c8de",
}

TARGETS = {
    "st-chp6-p156-ascanius-location",
    "st-chp6-p156-claude-employment-taste",
    "st-chp6-p156-colonna-status-and-antiquity",
    "st-chp6-p156-death-1689",
    "st-chp6-p156-eight-mythological-scenes-commissioned",
    "st-chp6-p156-fantastic-pursuit-evaluation",
    "st-chp6-p156-flight-into-egypt-purchased",
    "st-chp6-p156-fresco-category-distinction",
    "st-chp6-p156-fresco-cycle-depicts-marcantonio-at-lepanto",
    "st-chp6-p156-fresco-cycle-in-gallery",
    "st-chp6-p156-infidelities-lead-to-departure",
    "st-chp6-p156-lorenzo-employs-coli-on-scheme",
    "st-chp6-p156-lorenzo-employs-gherardi-on-scheme",
    "st-chp6-p156-lorenzo-ignores-criticism-complete",
    "st-chp6-p156-lorenzo-love-of-art-persists",
    "st-chp6-p156-maria-separation-demand",
    "st-chp6-p156-past-glory-and-venetian-analogy",
    "st-chp6-p156-retires-from-public-life",
    "st-chp6-p156-subject-allusions-suggest-lorenzo-connection",
    "st-chp6-p156-venetian-colouring",
    "st-chp6-p156-visit-to-spain-and-connections",
}

TRUE_NOTE = (
    "This is a source-grounded relation candidate at S2; source attribution and "
    "qualifications remain attached, and no formal S6 edge is created."
)
FALSE_NOTE = (
    "This is a biographical, scalar, stylistic, evaluative, or causal "
    "interpretation rather than a specific entity relation."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields, rows, bom):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def extract(lines, start, end, first, last):
    text = "\n".join(lines[start - 1:end])
    begin = text.find(first)
    if begin < 0:
        raise SystemExit(f"quote start missing L{start}-L{end}: {first!r}")
    if first == last:
        if text.find(first, begin + len(first)) >= 0:
            raise SystemExit(f"quote anchor is not unique L{start}-L{end}: {first!r}")
        return first
    finish = text.find(last, begin + len(first))
    if finish < 0:
        raise SystemExit(f"quote end missing L{start}-L{end}: {last!r}")
    return text[begin:finish + len(last)]


SOURCE_LINES = SOURCE.read_text(encoding="utf-8-sig").splitlines()
SEGMENT_TEXT = "\n".join(SOURCE_LINES[111:118])


def revise(by_id, sid, *, subject, object_, predicate, claim, relation, qualification,
           mentioned, start, end, first=None, last=None, quote=None, extra=None):
    row = by_id[sid]
    q = row.setdefault("qualifiers", {})
    row.update({
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "original_quote": quote if quote is not None else extract(SOURCE_LINES, start, end, first, last),
    })
    q.update({
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": "156",
        "pdf_physical_page": 11,
        "claim": claim,
        "speaker": "Haskell",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": TRUE_NOTE if relation else FALSE_NOTE,
    })
    if relation:
        q.pop("open_endpoint_reason", None)
    if extra:
        q.update(extra)
    return row


def new_statement(sid, subject, object_, predicate, claim, qualification,
                  mentioned, start, end, first, last, text_layer="authorial historical narrative",
                  extra=None):
    q = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": "156",
        "pdf_physical_page": 11,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": True,
        "relation_candidate_note": TRUE_NOTE,
    }
    if extra:
        q.update(extra)
    return {
        "statement_id": sid,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": extract(SOURCE_LINES, start, end, first, last),
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def build_outputs():
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")
    if SOURCE_LINES[111].strip() != "[Page 156]":
        raise SystemExit("p.156 page boundary changed")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {sid for sid, row in by_id.items()
             if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset != TARGETS:
        raise SystemExit(f"p.156 unset target set changed: {sorted(unset)}")

    candidate_fields, candidates, _ = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    for cid in {"cand-6337", "cand-0768", "cand-0773", "cand-0777", "cand-0780", "cand-0811", "cand-0814", "cand-0815", "cand-1509", "cand-3380", "cand-6342", "cand-6344", "cand-6345", "cand-6346", "cand-6347", "cand-8123"}:
        if cid not in candidate_by_id:
            raise SystemExit(f"required p.156 candidate missing: {cid}")
    if candidate_by_id["cand-8123"]["suggested_type"] != "institution":
        raise SystemExit("Spain polity candidate type changed")

    mention_fields, mentions, mention_bom = read_csv(MENTIONS)
    mentions_by_id = {row["mention_id"]: row for row in mentions}
    mention_updates = {
        "m-chp6-p156-001": ("cand-6337", "The p.155 sentence continues with the complaints from scholars or pedants; mapped to that criticism group."),
        "m-chp6-p156-028": ("cand-8123", "Spain is named as a country here; mapped to a political entity, distinct from a geographic-place candidate."),
    }
    for mid, (candidate_id, _) in mention_updates.items():
        if mid not in mentions_by_id:
            raise SystemExit(f"required p.156 mention missing: {mid}")
        if mentions_by_id[mid]["segment_id"] != SEGMENT:
            raise SystemExit(f"unexpected p.156 mention segment: {mid}")
        mentions_by_id[mid]["candidate_id"] = candidate_id
        mentions_by_id[mid]["note"] = mention_updates[mid][1]
    mentions_by_id["m-chp6-p156-030"]["note"] = (
        "Printed as 'public life'; S0 OCR reads 'public Use'. Preserve the source span and record the correction on the statement."
    )
    mentions_by_id["m-chp6-p156-045"]["note"] = (
        "Printed as Gesù; S0 OCR reads Gesu and omits the accent."
    )

    coverage_fields, coverage, coverage_bom = read_csv(COVERAGE)
    cov = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.156 coverage state: {cov}")

    revise(by_id, "st-chp6-p156-ascanius-location",
           subject="cand-0773", object_="cand-3380", predicate="located-at-ashmolean-museum",
           claim="Haskell reports Ascanius shooting the Stag of Sylvia at the Ashmolean Museum.",
           relation=True,
           qualification="This records the location stated in Haskell's text; no present-day location is independently verified.",
           mentioned=["cand-0773", "cand-3380", "cand-0768"], start=114, end=114,
           first="Stag of Sylvia, now", last="now in the Ashmolean Museum.",
           quote="now in the Ashmolean Museum.")
    revise(by_id, "st-chp6-p156-claude-employment-taste",
           subject="cand-0811", object_="cand-0768", predicate="employs-claude-over-nearly-twenty-years",
           claim="Haskell says Lorenzo employed Claude over nearly twenty years and interprets this as evidence of discrimination in Lorenzo's taste.",
           relation=True,
           qualification="The duration and taste judgment remain Haskell's account; the sentence does not enumerate the employment's terms.",
           mentioned=["cand-0811", "cand-0768"], start=113, end=113,
           first="and his employment of Claude", last="showed the discrimination of his taste.",
           extra={
               "footnote_marker": 1,
               "footnote_number": 1,
               "footnote_markers": [1],
               "footnote_segment": FOOTNOTE_SEGMENT,
               "footnote_refs": [{"marker": 1, "segment_id": FOOTNOTE_SEGMENT, "source_line": 156}],
               "footnote_statement_ids": ["st-chp6-notes-l156-p156-n1-1"],
               "footnote_link_status": "linked",
               "footnote_text_pending": False,
           })
    revise(by_id, "st-chp6-p156-colonna-status-and-antiquity",
           subject="cand-4638", object_=None, predicate="impoverished-yet-among-leading-families-claiming-ancient-lineage",
           claim="Haskell says the impoverished Colonna remained among a few leading Roman families able to claim an ancestry of heroic antiquity.",
           relation=False,
           qualification="This is a qualified historical and social characterization by Haskell, not a relation to a named office or institution.",
           mentioned=["cand-4638"], start=118, end=118,
           first="The Colonna, though greatly impoverished", last="an ancestry of heroic antiquity.")
    revise(by_id, "st-chp6-p156-death-1689",
           subject="cand-0811", object_=None, predicate="died-in-1689",
           claim="Haskell gives Lorenzo Onofrio's death year as 1689.", relation=False,
           qualification="A biographical date claim; the source is not independently verified here.",
           mentioned=["cand-0811"], start=117, end=117,
           first="and died in 1689.", last="and died in 1689.")
    revise(by_id, "st-chp6-p156-eight-mythological-scenes-commissioned",
           subject="cand-0811", object_="cand-6339", predicate="commissions-eight-mythological-scenes",
           claim="Haskell says Lorenzo subsequently commissioned an eight-scene mythological series from Claude.",
           relation=True,
           qualification="The source identifies the series as eight scenes and names examples; the group remains distinct from the separately indexed Landscape with the Flight into Egypt.",
           mentioned=["cand-0811", "cand-0768", "cand-6339", "cand-0777", "cand-0773"], start=113, end=113,
           first="he subsequently commissioned from him a series of eight mythological scenes",
           last="he subsequently commissioned from him a series of eight mythological scenes")
    revise(by_id, "st-chp6-p156-fantastic-pursuit-evaluation",
           subject="cand-0811", object_=None, predicate="pursuit-delights-scandalmongers-but-serves-little-other-purpose",
           claim="Haskell says a 'fantastic pursuit' delighted scandalmongers but served little other purpose.",
           relation=False,
           qualification="The source's allusion is not further identified; retain Haskell's evaluative wording without resolving the pursuit's referent.",
           mentioned=["cand-0811"], start=117, end=117,
           first="A fantastic pursuit", last="served little other purpose,")
    revise(by_id, "st-chp6-p156-flight-into-egypt-purchased",
           subject="cand-0811", object_="cand-0780", predicate="buys-landscape-with-flight-into-egypt-in-1662",
           claim="Haskell says Lorenzo bought Landscape with the Flight into Egypt in 1662, the year after his marriage, from Claude.",
           relation=True,
           qualification="The source calls Claude 'the artist'; the marriage reference is used only for the stated relative chronology.",
           mentioned=["cand-0811", "cand-0780", "cand-0768", "cand-1509"], start=113, end=113,
           first="After a Landscape with the Flight into Egypt", last="the year after his marriage,")
    revise(by_id, "st-chp6-p156-fresco-category-distinction",
           subject="cand-6345", object_=None, predicate="fresco-cycle-given-distinctive-decorative-category",
           claim="Haskell places the battle scene in a decorative category of its own and says it has little connection with contemporary frescoes by Gaulli and Carlo Maratta.",
           relation=False,
           qualification="This is an art-historical comparison and evaluation; the unnamed comparator fresco groups are not independently modeled as work entities in this statement.",
           mentioned=["cand-6345", "cand-1117", "cand-3112", "cand-1526", "cand-0090"], start=118, end=118,
           first="is in a category of its own as decoration", last="in the Altieri palace.",
           extra={"ocr_corrections": [
               {"source_file": SOURCE_FILE, "source_line": 118, "ocr": "Gesu", "print": "Gesù", "basis": "CHP-6.pdf physical page 11."},
           ]})
    revise(by_id, "st-chp6-p156-fresco-cycle-depicts-marcantonio-at-lepanto",
           subject="cand-6345", object_="cand-0814", predicate="depicts-marcantonio-colonna-at-lepanto",
           claim="Haskell describes the frescoes as recording Marc'Antonio Colonna's exploits at the Battle of Lepanto.",
           relation=True,
           qualification="The fresco cycle is unnamed; this records the represented person and battle as stated by Haskell.",
           mentioned=["cand-6345", "cand-0814", "cand-6343", "cand-4638"], start=117, end=118,
           first="the frescoes, recording the exploits of his ancestor",
           last="Marc’Antonio Colonna at the Battle of\nLepanto,")
    revise(by_id, "st-chp6-p156-fresco-cycle-in-gallery",
           subject="cand-6345", object_="cand-6344", predicate="located-on-ceiling-of-great-gallery",
           claim="Haskell locates the Lepanto frescoes on the ceiling of the great gallery in Lorenzo's palace.",
           relation=True,
           qualification="The great gallery remains distinct from the palace as a whole.",
           mentioned=["cand-6345", "cand-6344", "cand-0815"], start=118, end=118,
           first="the ceiling of the great gallery", last="in his palace.")
    revise(by_id, "st-chp6-p156-infidelities-lead-to-departure",
           subject="cand-0811", object_="cand-1509", predicate="infidelities-lead-to-wife-leaving-in-1672",
           claim="Haskell attributes Maria's leaving Lorenzo in 1672 to his reckless infidelities.",
           relation=True,
           qualification="This retains Haskell's stated causal account and does not add details about the separation.",
           mentioned=["cand-0811", "cand-1509"], start=116, end=117,
           first="and his reckless infidelities", last="her leaving him in\n1672.")
    revise(by_id, "st-chp6-p156-lorenzo-employs-coli-on-scheme",
           subject="cand-0811", object_="cand-0803", predicate="employs-giovanni-coli-on-lepanto-decoration",
           claim="Haskell says Lorenzo employed Giovanni Coli on the Colonna palace Lepanto decorative scheme fourteen years before the reported 1689 death.",
           relation=True,
           qualification="The relative date follows Haskell's adjacent chronology; the source calls Coli one of two Lucchese artists.",
           mentioned=["cand-0811", "cand-0803", "cand-6345"], start=117, end=117,
           first="Fourteen years earlier he had employed", last="decorative schemes of the second half of the seventeenth century:")
    revise(by_id, "st-chp6-p156-lorenzo-employs-gherardi-on-scheme",
           subject="cand-0811", object_="cand-1154", predicate="employs-filippo-gherardi-on-lepanto-decoration",
           claim="Haskell says Lorenzo employed Filippo Gherardi on the Colonna palace Lepanto decorative scheme fourteen years before the reported 1689 death.",
           relation=True,
           qualification="The relative date follows Haskell's adjacent chronology; the source calls Gherardi one of two Lucchese artists.",
           mentioned=["cand-0811", "cand-1154", "cand-6345"], start=117, end=117,
           first="Fourteen years earlier he had employed", last="decorative schemes of the second half of the seventeenth century:")
    revise(by_id, "st-chp6-p156-lorenzo-ignores-criticism-complete",
           subject="cand-0811", object_="cand-6337", predicate="takes-no-note-of-complaints-from-scholars-or-pedants",
           claim="Haskell completes the previous page's sentence: Lorenzo took no note of complaints from scholars or pedants.",
           relation=True,
           qualification="This closes p.155 L109 after 'take any note'; it describes Lorenzo's response, not the validity of the criticism.",
           mentioned=["cand-0811", "cand-6337"], start=113, end=113,
           first="of the complaints of scholars or pedants", last="of the complaints of scholars or pedants",
           extra={"continuation_status": "complete",
                  "continued_from_segment_id": "chp-6:06_CHP-6_sec_i:l102-110",
                  "continued_from_source_line": 109,
                  "continuation_resolved_from_statement_id": "st-chp6-p155-lorenzo-response-to-criticism-partial"})
    revise(by_id, "st-chp6-p156-lorenzo-love-of-art-persists",
           subject="cand-0811", object_=None, predicate="love-of-art-not-diminished-by-private-life",
           claim="Haskell says Lorenzo's love of art was not diminished by complications in his private life.",
           relation=False,
           qualification="An authorial characterization of taste and private life, not a specific relation to a separate entity.",
           mentioned=["cand-0811"], start=116, end=116,
           first="Certainly, his love of art", last="the growing complications of his private life.")
    revise(by_id, "st-chp6-p156-maria-separation-demand",
           subject="cand-0811", object_="cand-1509", predicate="agrees-to-maria-demand-for-separatione-di-letto",
           claim="Haskell says Lorenzo agreed, within a few years of marriage, to Maria's demand for a 'separatione di letto'.",
           relation=True,
           qualification="The Italian phrase is retained as quoted; its legal status and terms are not defined in this passage.",
           mentioned=["cand-0811", "cand-1509", "cand-6341"], start=116, end=116,
           first="Within a few years of his marriage", last="a ‘separatione di letto’,",
           extra={"ocr_corrections": [
               {"source_file": SOURCE_FILE, "source_line": 116, "ocr": "“separatione di letto”", "print": "‘separatione di letto’", "basis": "CHP-6.pdf physical page 11."},
           ]})
    revise(by_id, "st-chp6-p156-past-glory-and-venetian-analogy",
           subject="cand-4638", object_="cand-6347", predicate="past-prowess-consolation-compared-with-venetian-patricians",
           claim="Haskell interprets contemplation of the Colonna's past prowess as consolation as new families usurped earlier glories, comparing their circumstances with those of Venetian patricians.",
           relation=False,
           qualification="This is an interpretive social analogy; 'new families' and the particular Venetian patricians are not individually identified.",
           mentioned=["cand-4638", "cand-6347"], start=118, end=118,
           first="As the ‘new’ families usurped", last="somewhat similar circumstances... . . .")
    revise(by_id, "st-chp6-p156-retires-from-public-life",
           subject="cand-0811", object_=None, predicate="virtually-retires-from-public-life",
           claim="Haskell says Lorenzo virtually retired from public life after a brief visit to Spain.",
           relation=False,
           qualification="The source says 'virtually'; the OCR correction to 'life' is recorded below, with the original source surface retained.",
           mentioned=["cand-0811", "cand-6342"], start=117, end=117,
           first="he virtually retired from public Use", last="he virtually retired from public Use",
           extra={"ocr_corrections": [
               {"source_file": SOURCE_FILE, "source_line": 117, "ocr": "public Use", "print": "public life", "basis": "CHP-6.pdf physical page 11."},
           ]})
    revise(by_id, "st-chp6-p156-subject-allusions-suggest-lorenzo-connection",
           subject="cand-0811", object_="cand-6339", predicate="source-infers-lorenzo-connected-with-creation-of-scenes",
           claim="Haskell infers that Lorenzo was closely connected with creating the mythological pictures because some subjects almost certainly allude to the Colonna family and estates.",
           relation=True,
           qualification="This remains Haskell's inference, not a claim that Lorenzo painted the scenes; only some subjects are said to allude to the family and estates.",
           mentioned=["cand-0811", "cand-6339", "cand-4638", "cand-6340"], start=114, end=115,
           first="The unusual nature of many of the subjects", last="closely connected with the creation of these beautiful pictures.")
    revise(by_id, "st-chp6-p156-venetian-colouring",
           subject="cand-6345", object_="cand-6346", predicate="described-as-rendered-in-bold-venetian-colouring",
           claim="Haskell describes the fresco scene's ships and masts as rendered in bold Venetian colouring.",
           relation=False,
           qualification="This is an attributed stylistic description, retained as a statement rather than a formal relation.",
           mentioned=["cand-6345", "cand-6346"], start=118, end=118,
           first="This battle scene with its plunging ships", last="all rendered in bold Venetian colouring")
    revise(by_id, "st-chp6-p156-visit-to-spain-and-connections",
           subject="cand-0811", object_="cand-6342", predicate="makes-brief-visit-to-spain",
           claim="Haskell reports that Lorenzo made a brief visit to Spain.", relation=True,
           qualification="No date, route, or political purpose is supplied.",
           mentioned=["cand-0811", "cand-6342", "cand-8123"], start=117, end=117,
           first="after a brief visit to Spain", last="after a brief visit to Spain")

    additions = [
        new_statement("st-chp6-p156-claude-last-picture-identification", "cand-0773", "cand-0768",
            "identified-as-claudes-last-picture",
            "Haskell identifies Ascanius shooting the Stag of Sylvia as Claude's last picture.",
            "This records the identification in Haskell's text; it does not independently verify authorship or chronology.",
            ["cand-0773", "cand-0768"], 113, 114,
            "Claude’s last picture, Ascanius shooting the", "Stag of Sylvia,"),
        new_statement("st-chp6-p156-scene-series-includes-enchanted-castle", "cand-6339", "cand-0777",
            "includes-work-titled-enchanted-castle",
            "Haskell includes the so-called Enchanted Castle among the eight mythological scenes commissioned by Lorenzo.",
            "The source's 'so-called' wording is retained; the title remains linked to its existing work candidate.",
            ["cand-6339", "cand-0777"], 113, 113,
            "including the so-called Enchanted Castle", "including the so-called Enchanted Castle"),
        new_statement("st-chp6-p156-scene-series-includes-ascanius", "cand-6339", "cand-0773",
            "includes-work-titled-ascanius-shooting-stag-of-sylvia",
            "Haskell includes Ascanius shooting the Stag of Sylvia among the eight mythological scenes commissioned by Lorenzo.",
            "This preserves the source's series membership claim without merging the work with the separately indexed Landscape with the Flight into Egypt.",
            ["cand-6339", "cand-0773", "cand-0768"], 113, 114,
            "and Claude’s last picture, Ascanius shooting the", "Stag of Sylvia,"),
        new_statement("st-chp6-p156-lorenzo-commission-from-claude", "cand-0811", "cand-0768",
            "commissions-eight-mythological-scenes-from-claude",
            "Haskell says Lorenzo commissioned the eight-scene mythological series from Claude.",
            "The commission relationship and the work group are represented in linked statements; no completion date is added.",
            ["cand-0811", "cand-0768", "cand-6339"], 113, 113,
            "he subsequently commissioned from him", "a series of eight mythological scenes"),
        new_statement("st-chp6-p156-flight-into-egypt-bought-from-claude", "cand-0811", "cand-0768",
            "buys-landscape-with-flight-into-egypt-from-claude-in-1662",
            "Haskell says Lorenzo bought Landscape with the Flight into Egypt from Claude in 1662.",
            "The work-specific purchase and seller are separated from the work-group commission; 1662 remains the source date.",
            ["cand-0811", "cand-0768", "cand-0780"], 113, 113,
            "which he bought", "from the artist in 1662"),
        new_statement("st-chp6-p156-lorenzo-connections-with-spain-grow-closer", "cand-0811", "cand-8123",
            "connections-with-spain-become-closer",
            "Haskell says Lorenzo's connections with Spain became ever closer.",
            "The source says 'ever closer'; Spain is represented here as a political entity, distinct from geographic-place candidates.",
            ["cand-0811", "cand-8123"], 117, 117,
            "with which country his connections became ever closer", "with which country his connections became ever closer"),
    ]
    new_ids = {row["statement_id"] for row in additions}
    if len(new_ids) != len(additions) or new_ids & set(by_id):
        raise SystemExit("duplicate or preexisting planned p.156 statement ID")
    for row in additions:
        by_id[row["statement_id"]] = row
    statements = [by_id[row["statement_id"]] for row in statements]
    statements.extend(additions)

    # Print evidence corrects OCR, while the source text and mention spans stay unchanged.
    corrected_mentions = mentions_by_id
    if corrected_mentions["m-chp6-p156-001"]["candidate_id"] != "cand-6337":
        raise SystemExit("continuation complaint mention mapping did not update")
    if corrected_mentions["m-chp6-p156-028"]["candidate_id"] != "cand-8123":
        raise SystemExit("Spain country mention mapping did not update")

    valid_candidates = set(candidate_by_id)
    for mention in mentions:
        if mention["candidate_id"] not in valid_candidates:
            raise SystemExit(f"mention points to absent candidate: {mention['mention_id']}")
        if mention["segment_id"] == SEGMENT:
            start, end = int(mention["start_char"]), int(mention["end_char"])
            if SEGMENT_TEXT[start:end] != mention["surface_form"]:
                raise SystemExit(f"p.156 mention offsets are not exact: {mention['mention_id']}")

    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    for row in segment_rows:
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") not in (True, False):
            raise SystemExit(f"p.156 statement remains unclassified: {row['statement_id']}")
        referenced = set(q.get("mentioned_candidate_ids", []))
        endpoints = {row.get("subject_candidate_id"), row.get("object_candidate_id")} - {None}
        if not (referenced | endpoints) <= valid_candidates:
            raise SystemExit(f"p.156 candidate reference missing: {row['statement_id']}")
    linked = by_id["st-chp6-p156-claude-employment-taste"]["qualifiers"]
    if linked.get("footnote_statement_ids") != ["st-chp6-notes-l156-p156-n1-1"]:
        raise SystemExit("p.156 note 1 link is missing from the marked statement")

    cov["note"] += (
        " p.156 body L112-118 was reviewed against CHP-6.pdf physical page 11. All 21 previously unset statements were classified; "
        "six atomic statements were added to separate Claude's last-picture identification, named works within the eight-scene series, "
        "commissioning from Claude, the work-specific purchase from Claude, and Lorenzo's closer connections with Spain. The p.155 "
        "criticism continuation now links to its completed statement. The note-1 marker is linked to the existing p.156 citation row. "
        "The complaints-group and Spain mentions were remapped to their stated referents; OCR corrections for 'public life', Gesu/Gesù, "
        "and the quoted separation phrase are recorded without changing S0."
    )

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        MENTIONS: csv_bytes(mention_fields, mentions, mention_bom),
        COVERAGE: csv_bytes(coverage_fields, coverage, coverage_bom),
    }
    summary = {
        "segment": SEGMENT,
        "previously_unset_classified": len(TARGETS),
        "new_atomic_statements": len(additions),
        "segment_statement_count_after": len(segment_rows),
        "relation_candidates_in_segment_after": sum(row["qualifiers"].get("relation_candidate") is True for row in segment_rows),
        "non_relational_in_segment_after": sum(row["qualifiers"].get("relation_candidate") is False for row in segment_rows),
        "unset_in_segment_after": sum(row["qualifiers"].get("relation_candidate") is None for row in segment_rows),
        "mentions_remapped": sorted(mention_updates),
        "mode": "dry-run",
    }
    if summary["segment_statement_count_after"] != 27 or summary["relation_candidates_in_segment_after"] != 19 or summary["non_relational_in_segment_after"] != 8 or summary["unset_in_segment_after"]:
        raise SystemExit(f"unexpected p.156 totals: {summary}")
    return outputs, summary


def main():
    parser = argparse.ArgumentParser(description="Classify p.156 S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up and apply the reviewed p.156 batch.")
    args = parser.parse_args()
    outputs, summary = build_outputs()
    summary["mode"] = "apply" if args.apply else "dry-run"
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("backup already exists; refusing to overwrite")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    for path, data in outputs.items():
        atomic_write(path, data)
    print("APPLIED; backups:")
    for backup in backups.values():
        print(backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
