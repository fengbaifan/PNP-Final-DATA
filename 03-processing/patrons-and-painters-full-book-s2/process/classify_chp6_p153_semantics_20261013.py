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
SEGMENT = "chp-6:06_CHP-6_sec_i:l78-89"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp6-p153-semantics-20261013"

EXPECTED_HASHES = {
    SOURCE: "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    STATEMENTS: "50f9d8ceda48eb8de6260f8fe2903a48c06e2d0a7824429d04e344ec86774e3a",
    CANDIDATES: "05e7cfe9d29d811ea33d99eee8d8041ba101a0bb3c1d64cc742618262191d174",
    MENTIONS: "a1d6153c85e9ecff7fd731cbf1dd1a5583ea64901353c8eb85b9c6071777b107",
    COVERAGE: "ba2b0f7ff93c53d051f80a3753b46d7be8a2ffbf0e4bcc754faf3b444c20f5c2",
}

TARGETS = {
    "st-chp6-p153-alexander-protests-1648-settlement",
    "st-chp6-p153-bernini-leave-and-oliva-pressure",
    "st-chp6-p153-crequi-crisis-1662",
    "st-chp6-p153-defeat-effects-widen",
    "st-chp6-p153-departure-diminishes-papal-prestige",
    "st-chp6-p153-political-crisis-affects-patronage",
    "st-chp6-p153-rosa-fortune-painting-partial",
    "st-chp6-p153-rumours-bernini-stays-paris",
    "st-chp6-p153-targets-for-anti-papal-satire",
    "st-chp6-p153-treaty-pisa-louvre-proposals",
    "st-chp6-p153-war-with-france-averted",
}

TRUE_NOTE = (
    "S2 identifies a specific source-grounded relation candidate; qualifications "
    "are retained, and no formal S6 edge is created."
)
FALSE_NOTE = (
    "This is a contextual, scalar, transitional, or interpretive assertion rather "
    "than a specific entity relation."
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
        temp = Path(handle.name)
    os.replace(temp, path)


def extract(lines, start_line, end_line, first, last):
    text = "\n".join(lines[start_line - 1:end_line])
    start = text.find(first)
    if start < 0:
        raise SystemExit(f"quote start missing L{start_line}-L{end_line}: {first!r}")
    end = text.find(last, start + len(first))
    if end < 0:
        raise SystemExit(f"quote end missing L{start_line}-L{end_line}: {last!r}")
    return text[start:end + len(last)]


def make_candidate(cid, name, kind, detail, line):
    return {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line}",
    }


def make_mention(mid, cid, surface, note, segment_text):
    at = segment_text.find(surface)
    if at < 0 or segment_text.find(surface, at + 1) >= 0:
        raise SystemExit(f"mention anchor must occur once: {mid}: {surface!r}")
    return {"mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
            "surface_form": surface, "start_char": str(at),
            "end_char": str(at + len(surface)), "note": note}


def new_statement(sid, subject, object_, predicate, claim, relation, qualification,
                  mentioned, start, end, first, last, speaker="Haskell",
                  text_layer="authorial historical narrative", extra=None):
    q = {
        "source_line_start": start, "source_line_end": end,
        "printed_page": "153", "pdf_physical_page": 8,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": TRUE_NOTE if relation else FALSE_NOTE,
    }
    if extra:
        q.update(extra)
    return {
        "statement_id": sid, "segment_id": SEGMENT,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": q,
        "original_quote": extract(SOURCE_LINES, start, end, first, last),
        "origin": "book", "source_file": SOURCE_FILE,
    }


def revise(by_id, sid, *, subject, object_, predicate, claim, relation,
           qualification, mentioned, start, end, first, last,
           speaker="Haskell", text_layer="authorial historical narrative",
           extra=None):
    row = by_id[sid]
    q = row.setdefault("qualifiers", {})
    row.update({"subject_candidate_id": subject, "object_candidate_id": object_,
                "predicate": predicate,
                "original_quote": extract(SOURCE_LINES, start, end, first, last)})
    q.update({"source_line_start": start, "source_line_end": end,
              "printed_page": "153", "pdf_physical_page": 8,
              "claim": claim, "speaker": speaker, "text_layer": text_layer,
              "qualification": qualification,
              "mentioned_candidate_ids": mentioned,
              "relation_candidate": relation,
              "relation_candidate_note": TRUE_NOTE if relation else FALSE_NOTE})
    if extra:
        q.update(extra)
    return row


SOURCE_LINES = SOURCE.read_text(encoding="utf-8-sig").splitlines()
SEGMENT_TEXT = "\n".join(SOURCE_LINES[77:89])


def build_outputs():
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")
    if SOURCE_LINES[77].strip() != "[Page 153]":
        raise SystemExit("p.153 page boundary changed")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs in table")
    unset = {sid for sid, row in by_id.items()
             if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset != TARGETS:
        raise SystemExit(f"p.153 unset target set changed: {sorted(unset)}")

    cfields, candidates, cbom = read_csv(CANDIDATES)
    mfields, mentions, mbom = read_csv(MENTIONS)
    vfields, coverage, vbom = read_csv(COVERAGE)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    new_candidate_ids = [f"cand-{n}" for n in range(11990, 11995)]
    new_mention_ids = [
        "m-chp6-p153-nephews-representatives", "m-chp6-p153-characteristic-brawl",
        "m-chp6-p153-papal-guard", "m-chp6-p153-other-architects",
        "m-chp6-p153-roman-observers", "m-chp6-p153-principal-courtiers",
    ]
    if any(cid in candidate_ids for cid in new_candidate_ids) or any(mid in mention_ids for mid in new_mention_ids):
        raise SystemExit("a planned p.153 candidate or mention ID already exists")
    numbers = [int(r["candidate_id"].split("-")[1]) for r in candidates
               if r["candidate_id"].startswith("cand-") and r["candidate_id"].split("-")[1].isdigit()]
    if max(numbers) != 11989:
        raise SystemExit(f"candidate sequence changed: max={max(numbers)}")
    cov = next((r for r in coverage if r["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.153 coverage state: {cov}")

    candidates_to_add = [
        make_candidate("cand-11990", "Alexander VII's unnamed nephews and representatives in the 1662 incident", "term",
                       "A source-defined group publicly insulted and compelled to apologize after Créqui's diplomatic incident; no members are individually named.", 81),
        make_candidate("cand-11991", "Unnamed Roman street brawl used as a pretext in the Créqui incident", "event",
                       "The characteristic street brawl is not identified; Haskell reports that Créqui seized on it as a pretext.", 81),
        make_candidate("cand-11992", "Alexander VII's papal guard dismissed after the 1662 incident", "institution",
                       "The guard is unnamed and treated only as a source-bounded collective in Haskell's account.", 82),
        make_candidate("cand-11993", "Other unnamed architects approached for Louvre rebuilding designs", "term",
                       "Haskell says Bernini and a number of other architects were asked for Louvre rebuilding designs; the other architects are not identified.", 84),
        make_candidate("cand-11994", "Unnamed Roman observers expecting Bernini might remain in Paris", "term",
                       "Haskell quotes unnamed observers, including the Pope and principal courtiers, as expecting Bernini might stay in Paris after about six months.", 87),
    ]
    if any(row["candidate_id"] in candidate_ids for row in candidates_to_add):
        raise SystemExit("planned p.153 candidate already exists")

    new_mentions = [
        make_mention(new_mention_ids[0], "cand-11990", "nephews and representatives",
                     "Unnamed group in Haskell's account of the 1662 Créqui incident.", SEGMENT_TEXT),
        make_mention(new_mention_ids[1], "cand-11991", "one of the characteristic street brawls of the time",
                     "The unnamed brawl used as a pretext; not identified as an act by Alexander VII's relatives.", SEGMENT_TEXT),
        make_mention(new_mention_ids[2], "cand-11992", "his guard",
                     "Unnamed papal guard that Alexander VII was forced to dismiss, according to Haskell.", SEGMENT_TEXT),
        make_mention(new_mention_ids[3], "cand-11993", "a number of other architects",
                     "Unnamed architects grouped with Bernini in the request for Louvre designs.", SEGMENT_TEXT),
        make_mention(new_mention_ids[4], "cand-11994", "Many people",
                     "The unnamed observers in Haskell's quoted report about Bernini's possible stay in Paris.", SEGMENT_TEXT),
        make_mention(new_mention_ids[5], "cand-11994", "principal-courtiers",
                     "Senior courtiers named as part of the unnamed observer group.", SEGMENT_TEXT),
    ]
    old_segment_mentions = [m for m in mentions if m["segment_id"] == SEGMENT]
    for new in new_mentions:
        start, end = int(new["start_char"]), int(new["end_char"])
        for old in old_segment_mentions:
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if start < old_end and old_start < end:
                raise SystemExit(f"new p.153 mention overlaps existing mention: {new['mention_id']} / {old['mention_id']}")
    for i, left in enumerate(new_mentions):
        left_start, left_end = int(left["start_char"]), int(left["end_char"])
        for right in new_mentions[i + 1:]:
            right_start, right_end = int(right["start_char"]), int(right["end_char"])
            if left_start < right_end and right_start < left_end:
                raise SystemExit(f"new p.153 mentions overlap: {left['mention_id']} / {right['mention_id']}")

    # Each existing composite ID is retained for its main proposition; distinct
    # source claims are added below with their own exact source spans.
    revise(by_id, "st-chp6-p153-war-with-france-averted",
           subject="cand-0665", object_="cand-1447", predicate="war-averted-by-papal-surrender-to-louis-xiv",
           claim="Haskell says Louis XIV's threatened war was averted by the Pope's total surrender to him.", relation=True,
           qualification="This records Haskell's account of the settlement and does not independently characterize the Pope's action beyond the source wording.",
           mentioned=["cand-0665", "cand-1447"], start=79, end=80,
           first="The war to which Rosa alluded", last="Louis XIV who was threatening it.")
    revise(by_id, "st-chp6-p153-political-crisis-affects-patronage",
           subject="cand-4490", object_=None, predicate="relative-importance-of-political-and-financial-factors-in-patronage",
           claim="Haskell judges Rome's political situation as important as financial decline in affecting patronage.", relation=False,
           qualification="This is Haskell's comparative explanation; it does not specify a discrete patronage relation or quantify either factor.",
           mentioned=["cand-4490", "cand-6247"], start=80, end=80,
           first="And, in fact, the political situation of Rome", last="affecting patronage.")
    revise(by_id, "st-chp6-p153-alexander-protests-1648-settlement",
           subject="cand-0665", object_="cand-6322", predicate="protests-against-1648-peace-settlement",
           claim="As papal legate in Germany, Alexander VII vainly protested against the 1648 peace settlement ending the Thirty Years' War because it did not take papal interests into account.", relation=True,
           qualification="The settlement is not formally named in this passage; retain Haskell's 'vainly' and the stated papal-interest objection.",
           mentioned=["cand-0665", "cand-5529", "cand-6322", "cand-4965", "cand-4223"], start=80, end=80,
           first="As legate in Germany", last="papal interests into account.")
    revise(by_id, "st-chp6-p153-crequi-crisis-1662",
           subject="cand-6321", object_="cand-0665", predicate="uses-street-brawl-as-pretext-to-humiliate-alexander-vii",
           claim="Haskell says that in 1662 the Duc de Créqui used a characteristic street brawl as a pretext to humiliate Alexander VII.", relation=True,
           qualification="The brawl is unnamed. Haskell's comparison with the Sack of Rome describes the degree of humiliation and is not an independently measured ranking.",
           mentioned=["cand-6321", "cand-11991", "cand-0665", "cand-6258"], start=80, end=81,
           first="This reached a climax in 1662", last="the Sack of Rome in 1527.")
    revise(by_id, "st-chp6-p153-defeat-effects-widen",
           subject="cand-0665", object_=None, predicate="diplomatic-defeat-has-further-effects",
           claim="Haskell transitions from the diplomatic defeat to effects in other spheres.", relation=False,
           qualification="This is a transition, not an independent relation or outcome claim.",
           mentioned=["cand-0665"], start=83, end=83,
           first="The effects of this crushing defeat", last="other spheres.")
    revise(by_id, "st-chp6-p153-treaty-pisa-louvre-proposals",
           subject="cand-0312", object_="cand-1451", predicate="asked-to-provide-louvre-rebuilding-designs",
           claim="Within a month of the Treaty of Pisa, Bernini was approached and asked to provide designs for rebuilding the Louvre.", relation=True,
           qualification="Haskell dates the request relative to the treaty; this does not establish that Bernini's designs were adopted or that rebuilding occurred.",
           mentioned=["cand-0312", "cand-1939", "cand-1451", "cand-1450"], start=84, end=84,
           first="Within a month of the Treaty of Pisa", last="the rebuilding of the Louvre.")
    revise(by_id, "st-chp6-p153-bernini-leave-and-oliva-pressure",
           subject="cand-0665", object_="cand-0312", predicate="grants-bernini-three-months-leave-amid-french-arrangements",
           claim="While Bernini worked on St Peter's colonnade, Alexander VII gave him three months' leave in view of arrangements then being made with the French Crown.", relation=True,
           qualification="Haskell says the Pope considered Bernini's presence in Rome desirable; the quoted phrase gives the stated context but does not reduce the decision to a single cause.",
           mentioned=["cand-0665", "cand-0312", "cand-5317"], start=85, end=86,
           first="Yet \u2018in view of the arrangements", last="three months leave of absence,")
    revise(by_id, "st-chp6-p153-rumours-bernini-stays-paris",
           subject="cand-0312", object_="cand-4653", predicate="bernini-expected-by-roman-observers-to-remain-in-paris",
           claim="After Bernini had been away about six months, Haskell quotes unnamed Roman observers, including the Pope and principal courtiers, as expecting that Bernini might stay in Paris.", relation=True,
           qualification="The observers are unnamed and the period is approximate. This records an expectation, not Bernini's decision or actual residence.",
           mentioned=["cand-11994", "cand-0665", "cand-4223", "cand-0312", "cand-4653"], start=87, end=87,
           first="Many people, and not least the Pope", last="decided to stay in Paris.\u2019")
    revise(by_id, "st-chp6-p153-departure-diminishes-papal-prestige",
           subject="cand-0665", object_="cand-0312", predicate="bernini-departure-immediate-artistic-result-of-alexander-vii-defeat",
           claim="Haskell calls Bernini's temporary departure the most immediate artistic result of Alexander VII's diplomatic defeat.", relation=True,
           qualification="This is Haskell's causal and artistic interpretation; the source OCR reads 'Vil' for 'VII'.",
           mentioned=["cand-0665", "cand-0312"], start=88, end=88,
           first="The unwelcome departure of Bernini", last="Alexander Vil\u2019s defeat.",
           extra={"ocr_corrections": [{"source_file": SOURCE_FILE, "source_line": 88,
                     "ocr": "Alexander Vil's", "print": "Alexander VII's",
                     "basis": "CHP-6.pdf physical page 8."}]})
    revise(by_id, "st-chp6-p153-targets-for-anti-papal-satire",
           subject="cand-0111", object_="cand-3464", predicate="earlier-roman-satire-targets-barberini-extravagance-and-war-of-castro",
           claim="Haskell says the extravagance of the Barberini and the War of Castro had provided popular targets for Roman satire.", relation=True,
           qualification="This records the source's characterization of earlier satirical targets; it does not assert that the entire Barberini family shared a single policy.",
           mentioned=["cand-0111", "cand-3464", "cand-4904"], start=88, end=89,
           first="The extravagance of the Barberini", last="provided obvious and much appreciated targets.")
    revise(by_id, "st-chp6-p153-rosa-fortune-painting-partial",
           subject="cand-6224", object_="cand-6323", predicate="depicts-fortune-with-cornucopia-partial",
           claim="Haskell says the picture represents Fortune seated at the top of the canvas with a great cornucopia, pouring riches toward a gathering whose description continues on p.154.", relation=True,
           qualification="This is the partial visual description on p.153; p.154 L92 completes the gathering as pigs, wolves, foxes, wild birds and beasts of prey.",
           mentioned=["cand-6224", "cand-6323", "cand-2236", "cand-2269", "cand-3571"], start=89, end=89,
           first="a picture painted by Salvator Rosa", last="to a gathering of",
           text_layer="authorial art-historical description",
           extra={"continuation_status": "closed", "continuation_to_segment_id": "chp-6:06_CHP-6_sec_i:l91-100",
                  "continuation_to_fragment": "pigs, wolves, foxes, wild birds and beasts of prey",
                  "continued_by_source_line": 92, "continuation_resolved_by_segment": "chp-6:06_CHP-6_sec_i:l91-100",
                  "continuation_resolved_by_source_line": 92,
                  "continuation_resolved_by_statement_id": "st-chp6-p154-rosa-fortune-painting-completed"})

    additions = [
        new_statement("st-chp6-p153-alexander-career-demonstrates-collapse", "cand-0665", None,
            "career-demonstrates-collapse-of-papal-position",
            "Haskell presents Alexander VII's career as demonstrating a collapse in papal political position.", False,
            "This is Haskell's summary interpretation, not a discrete event or quantified measure.",
            ["cand-0665", "cand-4223"], 80, 80, "The career of Alexander VII", "demonstrated the collapse.",
            text_layer="authorial historical interpretation"),
        new_statement("st-chp6-p153-louis-xiv-nationalism-against-alexander", "cand-1447", "cand-0665",
            "aggressive-nationalism-pressures-alexander-vii", "Haskell says Alexander VII soon began to suffer from Louis XIV's aggressive nationalism.", True,
            "Haskell's political characterization is retained as his account; this does not independently assess Louis XIV's policy.",
            ["cand-1447", "cand-0665"], 80, 80, "As Pope he soon began to suffer", "aggressive nationalism.",
            text_layer="authorial historical narrative and interpretation"),
        new_statement("st-chp6-p153-nephews-representatives-insulted", "cand-6321", "cand-11990",
            "publicly-insults-and-compels-apology-of-alexander-vii-relatives-and-representatives",
            "Haskell says Alexander VII's unnamed nephews and representatives were publicly insulted and compelled to apologize over an incident they had not provoked.", True,
            "The relatives and representatives are unnamed; the source does not identify them individually.",
            ["cand-6321", "cand-0665", "cand-11990", "cand-11991"], 81, 81,
            "nephews and representatives", "they had not provoked;"),
        new_statement("st-chp6-p153-avignon-threatened-with-occupation", "cand-5317", "cand-6270",
            "threatens-french-occupation-of-avignon", "Haskell says Avignon was threatened with French occupation during the 1662 crisis.", True,
            "This is a threat, not a claim that French occupation occurred.",
            ["cand-1447", "cand-6270", "cand-5317"], 81, 82,
            "Avignon was threatened with", "French occupation;"),
        new_statement("st-chp6-p153-pope-forced-to-dismiss-guard", "cand-0665", "cand-11992",
            "forced-to-dismiss-papal-guard", "Haskell says Alexander VII was forced to dismiss his guard after the incident.", True,
            "The guard is unnamed and retained as a source-bounded collective.",
            ["cand-0665", "cand-11992"], 82, 82,
            "the Pope was forced to dismiss", "his guard."),
        new_statement("st-chp6-p153-other-architects-asked-for-louvre-designs", "cand-11993", "cand-1451",
            "asked-to-provide-louvre-rebuilding-designs", "Haskell says other unnamed architects were also approached and asked for Louvre rebuilding designs.", True,
            "The source does not identify these architects; no proposal is said to have been adopted.",
            ["cand-11993", "cand-1451", "cand-1450"], 84, 84,
            "a number of other architects", "the rebuilding of the Louvre."),
        new_statement("st-chp6-p153-bernini-invited-to-supervise-louvre-proposals", "cand-0312", "cand-4653",
            "invited-to-paris-to-supervise-louvre-proposals", "A year after the design request, Bernini was invited to Paris to supervise his proposals.", True,
            "The source reports an invitation and proposal supervision, not a completed Louvre commission.",
            ["cand-0312", "cand-4653", "cand-1451"], 84, 84,
            "A year later Bernini was invited", "to supervise his proposals."),
        new_statement("st-chp6-p153-diplomatic-courtesies-and-hidden-forces", "cand-1447", "cand-0665",
            "courtesy-exchange-masks-underlying-political-forces", "Haskell says formal courtesies were maintained through flattering letters and delicately sought papal permission, while more powerful forces operated beneath the exchange.", False,
            "This is Haskell's interpretation of diplomatic form and underlying motives; the source does not name the person who sought permission.",
            ["cand-1447", "cand-0800", "cand-0665", "cand-5317"], 84, 84,
            "The correct forms were upheld", "more powerful forces were at work.",
            text_layer="authorial historical interpretation"),
        new_statement("st-chp6-p153-bernini-working-on-st-peters-colonnade", "cand-0312", "cand-6307",
            "working-on-st-peters-colonnade", "Bernini was actively engaged on the colonnade of St Peter's at the time.", True,
            "This records the project association stated by Haskell; it does not add a commission date.",
            ["cand-0312", "cand-6307", "cand-5696"], 85, 85,
            "Bernini was actively engaged", "at the time."),
        new_statement("st-chp6-p153-pope-desired-bernini-presence-in-rome", "cand-0665", "cand-0312",
            "regards-berninis-presence-in-rome-as-desirable", "Alexander VII acknowledged that Bernini's presence in Rome was very desirable.", True,
            "This is Haskell's report of the Pope's stated view; Rome is the context for Bernini's presence.",
            ["cand-0665", "cand-0312", "cand-4490"], 85, 86,
            "His presence in", "very desirable as the Pope acknowledged."),
        new_statement("st-chp6-p153-oliva-anxious-to-appease-french", "cand-1771", "cand-5317",
            "seeks-to-appease-french", "Oliva was most anxious to appease the French.", True,
            "This states Haskell's characterization of Oliva's motive, not an independently verified intention.",
            ["cand-1771", "cand-5317"], 86, 87,
            "Oliva, the General of the Jesuits", "most anxious to appease the\nFrench,"),
        new_statement("st-chp6-p153-oliva-pressures-bernini-to-go-paris", "cand-1771", "cand-0312",
            "pressures-bernini-to-go-to-paris", "Oliva put strong moral pressure on Bernini to go to France.", True,
            "Haskell describes moral pressure; this does not establish Bernini's motive for travelling.",
            ["cand-1771", "cand-0312", "cand-4653", "cand-5317"], 86, 87,
            "put the greatest moral pressure", "to go."),
        new_statement("st-chp6-p153-rome-tense-after-bernini-absence", "cand-4490", None,
            "rome-tense-after-bernini-absence", "After Bernini had been away about six months, Haskell says the feeling in Rome was tense and nervous.", False,
            "This records Haskell's broad description of public feeling, not a measurable citywide condition.",
            ["cand-4490", "cand-0312"], 87, 87,
            "After he had been away some six months", "the feeling in Rome was tense and nervous."),
        new_statement("st-chp6-p153-papal-authority-fallen", "cand-4223", None,
            "papal-authority-described-as-fallen", "Haskell says the observers' expectation that Bernini might remain in Paris showed how far papal authority had fallen.", False,
            "This is Haskell's political interpretation of the reported expectation.",
            ["cand-4223", "cand-0665", "cand-0312", "cand-4653"], 87, 87,
            "To such a state had the Pope\u2019s authority", "fallen.1"),
        new_statement("st-chp6-p153-psychological-effects-more-profound", "cand-0665", None,
            "psychological-effects-described-as-more-profound-and-long-term", "Haskell says the psychological effects were more profound and ultimately more disturbing than Bernini's immediate departure.", False,
            "This is Haskell's comparative interpretation, not a measurable psychological outcome.",
            ["cand-0665", "cand-0312"], 88, 88,
            "Psychologically the effects", "much more disturbing."),
        new_statement("st-chp6-p153-papal-prestige-suffers-in-rome", "cand-4223", "cand-4490",
            "papal-prestige-suffers-in-rome-after-humiliation-abroad", "Haskell says the Pope's prestige suffered in Rome after his humiliation abroad.", True,
            "This is Haskell's assessment of papal prestige, not an independently measured public-opinion result.",
            ["cand-4223", "cand-0665", "cand-4490"], 88, 88,
            "Humiliated abroad", "suffered in Rome itself."),
        new_statement("st-chp6-p153-anti-clerical-satire-long-history", "cand-0111", "cand-4490",
            "anti-clerical-literature-and-pasquinades-have-long-history-in-rome", "Haskell says anti-clerical literature and pasquinades had a long and vigorous history in Rome.", False,
            "This is a broad historical characterization; the passage supplies no dated works or individual authors.",
            ["cand-0111", "cand-4490"], 88, 88,
            "Anti-clerical literature and pasquinades", "a long and vigorous history in the city."),
        new_statement("st-chp6-p153-donna-olimpia-satire-target", "cand-0111", "cand-1496",
            "satirical-target-donna-olimpias-court-dominance", "Haskell says Donna Olimpia's dominance at court provided an obvious and popular target for Roman satire.", True,
            "This records the source's account of a satirical target, not a separate claim about Donna Olimpia's political authority.",
            ["cand-0111", "cand-1496"], 89, 89,
            "followed by the dominance at court of Donna Olimpia", "provided obvious and much appreciated targets."),
        new_statement("st-chp6-p153-satirical-contempt-reaches-new-heights", "cand-0111", None,
            "satirical-contempt-for-pope-and-papacy-reaches-new-heights", "Haskell says satirical contempt for Alexander VII, and sometimes for the papacy as an institution, reached new heights under his pontificate.", False,
            "This is Haskell's trend assessment. OCR corruption in the papacy phrase is preserved in S0 and does not identify a distinct institution beyond the source context.",
            ["cand-0111", "cand-0665", "cand-4223"], 89, 89,
            "Now, under Alexander VII", "reached new heights.2",
            text_layer="authorial historical interpretation",
            extra={"ocr_corrections": [{"source_file": SOURCE_FILE, "source_line": 89,
                      "ocr": "institution os 'th\u00e9 pdpacy", "print": "institution of the papacy",
                      "basis": "CHP-6.pdf physical page 8."}]}),
        new_statement("st-chp6-p153-general-dissatisfaction-focused-in-rosa-picture", "cand-0111", "cand-6224",
            "general-dissatisfaction-focused-in-rosa-picture", "Haskell says general dissatisfaction was focused in Rosa's picture.", True,
            "This is Haskell's interpretive association between political discontent and the painting, not proof that the picture depicts a specific political person.",
            ["cand-0111", "cand-6224", "cand-2236", "cand-2269"], 89, 89,
            "The general dissatisfaction was focused", "for Carlo de\u2019 Rossi (Plate 24)."),
        new_statement("st-chp6-p153-la-fortuna-painted-by-rosa", "cand-6224", "cand-2236",
            "painted-by-salvator-rosa", "Haskell identifies Salvator Rosa as the painter of the picture.", True,
            "The artwork candidate is source-bounded to the painting described here; no date or present location is added.",
            ["cand-6224", "cand-2236"], 89, 89,
            "a picture painted by Salvator Rosa", "for Carlo de\u2019 Rossi (Plate 24)."),
        new_statement("st-chp6-p153-la-fortuna-made-for-carlo-de-rossi", "cand-6224", "cand-2269",
            "made-for-carlo-de-rossi", "Haskell says Salvator Rosa painted the picture for Carlo de' Rossi.", True,
            "This records the relationship stated in the book, not independent confirmation of a commission or ownership history.",
            ["cand-6224", "cand-2236", "cand-2269"], 89, 89,
            "a picture painted by Salvator Rosa for Carlo de\u2019 Rossi", "(Plate 24)."),
    ]
    new_ids = {row["statement_id"] for row in additions}
    if len(new_ids) != len(additions) or new_ids & set(by_id):
        raise SystemExit("duplicate or preexisting planned p.153 statement ID")
    for row in additions:
        by_id[row["statement_id"]] = row
    statements = [by_id[row["statement_id"]] for row in statements]
    statements.extend(additions)

    valid_candidates = candidate_ids | set(new_candidate_ids)
    valid_mentions = mentions + new_mentions
    for mention in valid_mentions:
        if mention["candidate_id"] not in valid_candidates:
            raise SystemExit(f"mention points to absent candidate: {mention['mention_id']}")
        if mention["segment_id"] == SEGMENT:
            start, end = int(mention["start_char"]), int(mention["end_char"])
            if SEGMENT_TEXT[start:end] != mention["surface_form"]:
                raise SystemExit(f"mention offsets do not match source text: {mention['mention_id']}")
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    for row in segment_rows:
        q = row.get("qualifiers", {})
        referenced = set(q.get("mentioned_candidate_ids", []))
        if not referenced <= valid_candidates:
            raise SystemExit(f"statement mentions absent candidates: {row['statement_id']}: {sorted(referenced - valid_candidates)}")
        endpoints = {row.get("subject_candidate_id"), row.get("object_candidate_id")} - {None}
        if not endpoints <= valid_candidates:
            raise SystemExit(f"statement has absent endpoint candidate: {row['statement_id']}")
        if q.get("relation_candidate") not in (True, False):
            raise SystemExit(f"p.153 statement remains unclassified: {row['statement_id']}")

    # The p.153 footnote marker remains attached to the retained leave statement;
    # the split footnote record already links its treaty employment claim there.
    cov["note"] += (
        " p.153 physical page 8 was checked against CHP-6.pdf. The eleven previously unset statements were classified; "
        "composites were atomized across the 1648 protest, 1662 Créqui crisis, Louvre proposals, Bernini's leave and "
        "Oliva's pressure, papal prestige, satirical targets, and Rosa's La Fortuna. Five source-bounded candidates and "
        "six exact mentions were added for unnamed actors/events. The note 1 link remains on the leave statement and "
        "the existing footnote split; Haskell's interpretations, observer expectations, threats, and OCR corrections "
        "remain explicitly qualified. The p.153 painting description is linked to its p.154 continuation."
    )

    out = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        CANDIDATES: csv_bytes(cfields, candidates + candidates_to_add, cbom),
        MENTIONS: csv_bytes(mfields, mentions + new_mentions, mbom),
        COVERAGE: csv_bytes(vfields, coverage, vbom),
    }
    summary = {
        "segment": SEGMENT, "previously_unset_classified": len(TARGETS),
        "new_atomic_statements": len(additions), "segment_statement_count_after": len(segment_rows),
        "relation_candidates_in_segment_after": sum(r["qualifiers"].get("relation_candidate") is True for r in segment_rows),
        "non_relational_in_segment_after": sum(r["qualifiers"].get("relation_candidate") is False for r in segment_rows),
        "unset_in_segment_after": sum(r["qualifiers"].get("relation_candidate") is None for r in segment_rows),
        "candidates_added": new_candidate_ids, "mentions_added": new_mention_ids,
        "mode": "dry-run",
    }
    if summary["unset_in_segment_after"] or summary["segment_statement_count_after"] != 33:
        raise SystemExit(f"unexpected p.153 segment totals: {summary}")
    return out, summary


def main():
    parser = argparse.ArgumentParser(description="Classify and atomize p.153 S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up affected tables and apply the reviewed p.153 batch.")
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
