#!/usr/bin/env python3
"""Classify p.117 statements and linked footnotes with guarded table writes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l207-216"
NOTE_SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "a1dd4753e13a03aace4b7f15bb9900680156d2aa5df93eb0ff6f28364a235497"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "d59bf516d948b5b466e545a4c54463551e29ebfb294d2d8de70007931f18ea83",
    "entity-candidates.csv": "1dca21e4b7d97ced8d4cfe03935590a41deb6f2200dc50e326a5be9c406bb3d7",
    "mentions.csv": "d6799b3adb4609a49de00e7d224b8b0abf8041a47dd77de15e1a051ae8aaba8c",
}
BACKUP_SUFFIX = "bak-s2-chp4-p117-relations-20261011"

P117_IDS = {
    "st-chp4-sec-ii-p117-alexander-avoids-offending-french",
    "st-chp4-sec-ii-p117-alexander-conciliates-venetians",
    "st-chp4-sec-ii-p117-amateur-and-lessons",
    "st-chp4-sec-ii-p117-bellori-anecdote",
    "st-chp4-sec-ii-p117-cassiano-role",
    "st-chp4-sec-ii-p117-cassiano-visits",
    "st-chp4-sec-ii-p117-copies-of-buildings-paintings",
    "st-chp4-sec-ii-p117-four-portraits-continuation",
    "st-chp4-sec-ii-p117-french-protested-violently",
    "st-chp4-sec-ii-p117-library-antiquities-focus",
    "st-chp4-sec-ii-p117-massimi-recalled-1658",
    "st-chp4-sec-ii-p117-mood-and-moral-reading",
    "st-chp4-sec-ii-p117-named-poussin-pair",
    "st-chp4-sec-ii-p117-nuncio-service",
    "st-chp4-sec-ii-p117-papal-policy-shift",
    "st-chp4-sec-ii-p117-patronage-difficulty",
    "st-chp4-sec-ii-p117-portrait-purchases",
    "st-chp4-sec-ii-p117-possible-poussin-acquisition",
    "st-chp4-sec-ii-p117-poussin-library-visits",
    "st-chp4-sec-ii-p117-poussin-massimi-friendship",
    "st-chp4-sec-ii-p117-poussin-relationship",
    "st-chp4-sec-ii-p117-pyrenees-balance",
    "st-chp4-sec-ii-p117-spanish-backing",
    "st-chp4-sec-ii-p117-unfinished-gift-1664",
    "st-chp4-sec-ii-p117-venetian-jesuit-readmission",
    "st-chp4-sec-ii-p117-venetians-protested-violently",
}
NOTE_IDS = {
    "st-chp4-sec-ii-p117note-fn1-lumbroso",
    "st-chp4-sec-ii-p117note-fn2-bartoli-drawings",
    "st-chp4-sec-ii-p117note-fn2-michaelis",
    "st-chp4-sec-ii-p117note-fn3-unknown-patron",
    "st-chp4-sec-ii-p117note-fn3-blunt-1938",
    "st-chp4-sec-ii-p117note-fn3-panofsky-1957",
    "st-chp4-sec-ii-p117note-fn4-bellori-441",
    "st-chp4-sec-ii-p117note-fn5-resident-testimony",
    "st-chp4-sec-ii-p117note-fn5-claretta",
    "st-chp4-sec-ii-p117note-fn5-drawing-inscription",
}

CANDIDATES = [
    {
        "candidate_id": "cand-11664", "index_entry_id": "",
        "canonical_name": "Venetian political authority involved in Jesuit readmission and protest (body unspecified)",
        "index_page_range": "", "suggested_type": "institution", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell attributes Jesuit readmission and protest to the Venetians collectively; the political body and individual officials are not identified. Keep distinct from the Venetian artists collective cand-3457.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L210",
    },
    {
        "candidate_id": "cand-11665", "index_entry_id": "",
        "canonical_name": "Unidentified King, Queen, and two Infantas portrayed in the four portraits for Massimi",
        "index_page_range": "", "suggested_type": "", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Source-bounded sitter group. The passage supplies royal titles and the number of Infantas but no personal names; do not identify them from context.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L208",
    },
    {
        "candidate_id": "cand-11666", "index_entry_id": "",
        "canonical_name": "Older Roman buildings and paintings for which Massimi arranged copies (unidentified group)",
        "index_page_range": "", "suggested_type": "", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Mixed, source-bounded group of unnamed buildings and paintings. The passage identifies neither individual originals nor copies.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L211",
    },
    {
        "candidate_id": "cand-11667", "index_entry_id": "",
        "canonical_name": "Pair of early Poussin works discussed as a possible Massimi acquisition",
        "index_page_range": "", "suggested_type": "work", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "The source names King Midas washing his Face in the River Pactolus and the first version of the Arcadian Shepherds as a pair in this acquisition account. This does not establish pendant status, a common original patron, or secure provenance.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L212",
    },
    {
        "candidate_id": "cand-11668", "index_entry_id": "",
        "canonical_name": "Unidentified heirs of Cassiano dal Pozzo",
        "index_page_range": "", "suggested_type": "", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Unnamed group mentioned only as a possible source of the two Poussin works. Haskell explicitly says there is no direct evidence; membership and transaction remain unverified.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L211",
    },
]
NEW_STATEMENT_IDS = {
    "st-chp4-sec-ii-p117-lessons-from-poussin",
    "st-chp4-sec-ii-p117-studio-conversation",
    "st-chp4-sec-ii-p117-cassiano-accompanied-on-visits",
    "st-chp4-sec-ii-p117-no-further-job-twelve-years",
    "st-chp4-sec-ii-p117-portraits-of-royal-sitters",
    "st-chp4-sec-ii-p117-pair-arcadian-member",
    "st-chp4-sec-ii-p117-poussin-independence",
    "st-chp4-sec-ii-p117-pair-possible-source-heirs",
    "st-chp4-sec-ii-p117-spanish-french-quarrels",
    "st-chp4-sec-ii-p117note-fn2-bartoli-authorship",
    "st-chp4-sec-ii-p117note-fn5-maratta-preference",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return " ".join(text.split())


def unique_span(text: str, needle: str) -> tuple[int, int]:
    start = text.find(needle)
    if start < 0 or text.find(needle, start + 1) >= 0:
        raise SystemExit(f"source phrase absent or ambiguous: {needle!r}")
    return start, start + len(needle)


def excerpt(text: str, start: str, end: str) -> str:
    left = text.find(start)
    if left < 0 or text.find(start, left + 1) >= 0:
        raise SystemExit(f"source excerpt start absent or ambiguous: {start!r}")
    right = text.find(end, left + len(start))
    if right < 0:
        raise SystemExit(f"source excerpt end absent: {end!r}")
    return text[left:right + len(end)]


def make_statement(
    sid: str, segment_id: str, subject: str | None, obj: str | None, predicate: str,
    quote: str, start: int, end: int, claim: str, relation: bool, note: str,
    mentioned: list[str], *, qualification: str = "", marker: int | None = None,
    note_line: int | None = None, note_ids: list[str] | None = None,
    extra: dict | None = None,
) -> dict:
    is_body = segment_id == SEGMENT_ID
    qualifiers = {
        "source_line_start": start, "source_line_end": end,
        "pdf_physical_page": 28, "printed_page_locator": "p.117",
        "claim": claim, "speaker": "Haskell" if is_body else "Haskell's footnote",
        "text_layer": "authorial narrative" if is_body else "authorial footnote claim",
        "mentioned_candidate_ids": mentioned, "relation_candidate": relation,
        "relation_candidate_note": note,
    }
    if qualification:
        qualifiers["qualification"] = qualification
    if marker is not None:
        qualifiers.update({
            "footnote_marker": marker, "footnote_segment": NOTE_SEGMENT_ID,
            "footnote_source_line": note_line, "footnote_link_status": "linked",
        })
    if note_ids:
        qualifiers["footnote_statement_ids"] = note_ids
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book", "source_file": SOURCE_REL,
    }


def append_csv(original: bytes, rows: list[dict]) -> bytes:
    if not rows:
        return original
    headers = next(csv.reader(io.StringIO(original.decode("utf-8-sig"), newline="")))
    eol = "\r\n" if b"\r\n" in original else "\n"
    buf = io.StringIO(newline="")
    csv.DictWriter(buf, fieldnames=headers, extrasaction="raise", lineterminator=eol).writerows(rows)
    if not original.endswith((b"\n", b"\r")):
        original += eol.encode("ascii")
    return original + buf.getvalue().encode("utf-8")


def remap_mentions(original: bytes, replacements: dict[str, tuple[str, str]]) -> bytes:
    lines = original.decode("utf-8-sig").splitlines(keepends=True)
    found: set[str] = set()
    for i, line in enumerate(lines):
        for mid, (old, new) in replacements.items():
            if line.startswith(mid + ","):
                if mid in found or f",{old}," not in line:
                    raise SystemExit(f"unexpected mention mapping: {mid}")
                lines[i] = line.replace(f",{old},", f",{new},", 1)
                found.add(mid)
    if found != set(replacements):
        raise SystemExit(f"mention rows missing: {sorted(set(replacements)-found)}")
    return "".join(lines).encode("utf-8")


def transform_jsonl(original: bytes, updates: dict[str, dict], additions: list[dict]) -> bytes:
    eol = b"\r\n" if b"\r\n" in original else b"\n"
    output: list[bytes] = []
    found: set[str] = set()
    for raw in original.splitlines(keepends=True):
        content = raw.rstrip(b"\r\n")
        if not content:
            output.append(raw)
            continue
        row = json.loads(content.decode("utf-8"))
        sid = row.get("statement_id")
        if sid in updates:
            if sid in found:
                raise SystemExit(f"duplicate existing statement ID: {sid}")
            row.update(updates[sid])
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + (raw[len(content):] or eol))
            found.add(sid)
        else:
            output.append(raw)
    if found != set(updates):
        raise SystemExit(f"statements missing: {sorted(set(updates)-found)}")
    if output and not output[-1].endswith((b"\n", b"\r")):
        output[-1] += eol
    output.extend(json.dumps(r, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + eol for r in additions)
    return b"".join(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write validated p.117 changes")
    args = parser.parse_args()
    source_bytes = SOURCE.read_bytes()
    if digest(source_bytes) != SOURCE_SHA256:
        raise SystemExit("source fingerprint changed; stop and review")
    lines = source_bytes.decode("utf-8").splitlines()
    body = "\n".join(lines[206:216])
    notes = "\n".join(lines[231:308])
    if not body.startswith("[Page 117]\n") or digest(body.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("p.117 source segment differs from the audited boundary/fingerprint")
    segments = [
        json.loads(x) for x in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if x.strip()
    ]
    registry = next((r for r in segments if r.get("segment_id") == SEGMENT_ID), None)
    if not registry or registry.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("p.117 segment registry fingerprint changed")

    paths = {n: TABLES / n for n in EXPECTED_SHA256}
    originals = {n: p.read_bytes() for n, p in paths.items()}
    for name, expected in EXPECTED_SHA256.items():
        if digest(originals[name]) != expected:
            raise SystemExit(f"{name} changed since the p.116 checkpoint")
    statement_rows = [
        json.loads(x.decode("utf-8")) for x in originals["book-statements.jsonl"].splitlines() if x.strip()
    ]
    body_rows = [r for r in statement_rows if r.get("segment_id") == SEGMENT_ID]
    note_rows = [r for r in statement_rows if r.get("segment_id") == NOTE_SEGMENT_ID and r.get("statement_id") in NOTE_IDS]
    if len(body_rows) != 26 or {r["statement_id"] for r in body_rows} != P117_IDS:
        raise SystemExit(f"expected exact 26 p.117 statements; found {len(body_rows)}")
    if {r["statement_id"] for r in note_rows} != NOTE_IDS:
        raise SystemExit("p.117 footnote statement set changed")
    for row in body_rows + note_rows:
        q = row.get("qualifiers", {}) or {}
        if q.get("relation_candidate") is not None:
            raise SystemExit(f"statement already classified: {row['statement_id']}")
        source_text = body if row.get("segment_id") == SEGMENT_ID else notes
        if norm(row.get("original_quote", "")) not in norm(source_text):
            raise SystemExit(f"quote is not present in source: {row['statement_id']}")

    mention_rows = list(csv.DictReader(io.StringIO(originals["mentions.csv"].decode("utf-8-sig"), newline="")))
    body_mentions = [r for r in mention_rows if r.get("segment_id") == SEGMENT_ID]
    if len(body_mentions) != 34:
        raise SystemExit(f"expected 34 pre-existing p.117 mentions; found {len(body_mentions)}")
    for m in body_mentions:
        if body[int(m["start_char"]):int(m["end_char"])] != m["surface_form"]:
            raise SystemExit(f"mention span mismatch: {m['mention_id']}")

    pair_match = re.search(r"a pair of that painter[’']s most beautiful early works", body)
    heirs_match = re.search(r"heirs of\s+Cassiano", body)
    if not pair_match or not heirs_match:
        raise SystemExit("p.117 pair/heirs source phrases are absent")
    q = lambda a, b: excerpt(body, a, b)

    updates: dict[str, dict] = {}

    def set_row(
        sid: str, relation: bool, note: str, *, subject=Ellipsis, obj=Ellipsis,
        predicate=None, quote=None, claim=None, mentioned=None, qualification=None,
        open_reason=None, qpatch=None,
    ) -> None:
        row = next(r for r in body_rows + note_rows if r["statement_id"] == sid)
        changes: dict = {}
        if subject is not Ellipsis:
            changes["subject_candidate_id"] = subject
        if obj is not Ellipsis:
            changes["object_candidate_id"] = obj
        if predicate is not None:
            changes["predicate"] = predicate
        if quote is not None:
            changes["original_quote"] = quote
        qualifiers = dict(row.get("qualifiers", {}) or {})
        qualifiers["relation_candidate"] = relation
        qualifiers["relation_candidate_note"] = note
        if open_reason:
            qualifiers["open_endpoint_reason"] = open_reason
        else:
            qualifiers.pop("open_endpoint_reason", None)
        if claim is not None:
            qualifiers["claim"] = claim
        if mentioned is not None:
            qualifiers["mentioned_candidate_ids"] = mentioned
        if qualification is not None:
            qualifiers["qualification"] = qualification
        if qpatch:
            qualifiers.update(qpatch)
        changes["qualifiers"] = qualifiers
        updates[sid] = changes

    set_row("st-chp4-sec-ii-p117-alexander-avoids-offending-french", True,
        "Records Alexander VII's policy toward the French collective used at p.116; individual French actors are not named.",
        subject="cand-0665", obj="cand-5968", mentioned=["cand-0665", "cand-5968"])
    set_row("st-chp4-sec-ii-p117-alexander-conciliates-venetians", True,
        "Political conciliatory effort attributed to the source-bounded Venetian authority; the formal body is not named.",
        subject="cand-0665", obj="cand-11664", mentioned=["cand-0665", "cand-11664"])
    set_row("st-chp4-sec-ii-p117-amateur-and-lessons", False,
        "The retained clause describes Massimi as an amateur artist. The probable lessons relationship is split into a new statement.",
        subject="cand-1564", obj=None, predicate="amateur_artist",
        quote="Massimi was an amateur artist", claim="Haskell describes Massimi as an amateur artist.",
        mentioned=["cand-1564"], qualification="Scalar description; probable lessons are recorded separately.")
    set_row("st-chp4-sec-ii-p117-bellori-anecdote", True,
        "Records Poussin showing Massimi downstairs. Haskell attributes the anecdote to Bellori; their studio conversation is split separately.",
        subject="cand-1984", obj="cand-1564", predicate="showed_downstairs",
        quote=q("Poussin showing Massimi downstairs", "late one night"),
        claim="Haskell summarizes Bellori's anecdote of Poussin showing Massimi downstairs late one night.",
        mentioned=["cand-3535", "cand-1984", "cand-1564"],
        qualification="Haskell's summary of Bellori, not independent consultation.")
    set_row("st-chp4-sec-ii-p117-cassiano-role", True,
        "Haskell compares Massimi to a role left vacant by Cassiano but marks the claim with 'seems'; this is not a formal office succession.",
        subject="cand-1564", obj="cand-2036", predicate="seemed_to_assume_role_left_by",
        mentioned=["cand-1564", "cand-2036"], qualification="'Seems' and 'in many ways' preserve the author's inference.")
    set_row("st-chp4-sec-ii-p117-cassiano-visits", True,
        "The retained clause records Massimi knowing Cassiano. Accompanying Cassiano on connoisseur visits is split separately.",
        subject="cand-1564", obj="cand-2036", predicate="knew", quote="whom he had known",
        claim="Haskell says Massimi knew Cassiano dal Pozzo.", mentioned=["cand-1564", "cand-2036"])
    set_row("st-chp4-sec-ii-p117-copies-of-buildings-paintings", True,
        "Massimi arranged copying of this mixed source-bounded group; originals and copies are not individually identified.",
        subject="cand-1564", obj="cand-11666", predicate="arranged_copying_of",
        mentioned=["cand-1564", "cand-11666"])
    set_row("st-chp4-sec-ii-p117-four-portraits-continuation", True,
        "The continuation says the portraits were for Massimi; it does not assert a formal commission. Creator is recorded at p.116 and sitters are linked separately.",
        subject="cand-5976", obj="cand-1564", predicate="intended_for",
        claim="Haskell completes the p.116 sentence: Velasquez's four portraits were for Massimi.",
        mentioned=["cand-2709", "cand-1564", "cand-5976", "cand-11665"])
    set_row("st-chp4-sec-ii-p117-french-protested-violently", True,
        "The passage records French collective protest but supplies no grammatical object; nearby Spanish policy is context, not a confirmed target.",
        subject="cand-5968", obj=None, predicate="protested_violently",
        mentioned=["cand-5968", "cand-4591", "cand-4632", "cand-5977"],
        open_reason="The protest target is unstated. Do not infer that the French protested against Massimi, Spain, or the Peace of the Pyrenees.")
    set_row("st-chp4-sec-ii-p117-library-antiquities-focus", False,
        "Scalar account of what occupied Massimi's attention, not a relation to his library or antiquities collection.",
        subject="cand-1564", obj=None, mentioned=["cand-1564", "cand-1574", "cand-1571"])
    set_row("st-chp4-sec-ii-p117-massimi-recalled-1658", True,
        "The retained clause records the 1658 recall to Rome. The next twelve years without a job are split as a separate scalar claim.",
        subject="cand-1564", obj="cand-4490", predicate="recalled_to",
        quote="In 1658 Massimi was recalled to Rome",
        claim="Haskell says Massimi was recalled to Rome in 1658.",
        mentioned=["cand-1564", "cand-4490"], qpatch={"time": "1658"})
    set_row("st-chp4-sec-ii-p117-mood-and-moral-reading", False,
        "Haskell's aesthetic and moral interpretation of two works and their relevance to Massimi's career, not an entity relation.",
        subject="cand-1564", obj=None, mentioned=["cand-1564", "cand-2009", "cand-4800", "cand-11667"],
        qualification="Haskell retains 'if not actually moral'; nested interpretation is not independently verified.")
    set_row("st-chp4-sec-ii-p117-named-poussin-pair", True,
        "Records the first named member of the source-bounded pair; membership does not establish pendant status.",
        subject="cand-11667", obj="cand-2009", predicate="contains",
        quote=q("the King\nMidas washing his Face", "River Pactolus"),
        claim="Haskell identifies King Midas washing his Face in the River Pactolus as one work in the pair.",
        mentioned=["cand-11667", "cand-2009", "cand-1984"])
    set_row("st-chp4-sec-ii-p117-nuncio-service", False,
        "Haskell's comparative evaluation of Massimi's diplomatic service, not a relation to a named entity.",
        subject="cand-1564", obj=None, mentioned=["cand-1564"])
    set_row("st-chp4-sec-ii-p117-papal-policy-shift", False,
        "General authorial observation about papal succession and policy; the policy is not identified as an entity.",
        subject="cand-0665", obj=None, mentioned=["cand-0665", "cand-4490"])
    set_row("st-chp4-sec-ii-p117-patronage-difficulty", False,
        "General statement about difficulty procuring work from unnamed fashionable artists; no specific relation is asserted.",
        subject="cand-1564", obj=None, mentioned=["cand-1564"])
    set_row("st-chp4-sec-ii-p117-portrait-purchases", False,
        "The sentence evaluates purchases as benefits but does not identify the buyer. Do not assert Massimi bought the portraits or unnamed objects.",
        subject="cand-1564", obj="cand-5976", mentioned=["cand-1564", "cand-5976"],
        qualification="'Must have seemed' is Haskell's interpretation; buyer is not explicit.")
    set_row("st-chp4-sec-ii-p117-possible-poussin-acquisition", True,
        "Tentative claim that Massimi may have acquired the source-bounded pair. The possible source among Cassiano's heirs is separated and retains the no-direct-evidence caveat.",
        subject="cand-11667", obj="cand-1564", predicate="acquired_by",
        claim="Haskell says Massimi may have acquired the pair of early Poussin works discussed here.",
        mentioned=["cand-11667", "cand-1564", "cand-1984", "cand-2009", "cand-4800", "cand-2036", "cand-11668"],
        qualification="'May well have been now' is tentative; a possible source is not established.",
        qpatch={"possible_source_candidate_id": "cand-11668", "possible_source_subject_candidate_id": "cand-2036"})
    set_row("st-chp4-sec-ii-p117-poussin-library-visits", True,
        "The source says Poussin must have visited Massimi's library; the endpoint is the library candidate, not Massimi as a person.",
        subject="cand-1984", obj="cand-1574", predicate="visited",
        mentioned=["cand-1984", "cand-1564", "cand-1574"],
        qualification="'Must have' is Haskell's inference.")
    set_row("st-chp4-sec-ii-p117-poussin-massimi-friendship", True,
        "Haskell explicitly says the two men established a very close friendship.",
        subject="cand-1564", obj="cand-1984", predicate="friend_of",
        mentioned=["cand-1564", "cand-1984"])
    set_row("st-chp4-sec-ii-p117-poussin-relationship", True,
        "Records Haskell's 'closest relationship possible' claim. Poussin's independence from changes in client status is split as a scalar statement.",
        subject="cand-1564", obj="cand-1984", predicate="friend_of",
        quote="and above all he too enjoyed the closest relationship possible with Poussin",
        claim="Haskell says Massimi enjoyed the closest possible relationship with Poussin.",
        mentioned=["cand-1564", "cand-1984"], qualification="The superlative remains Haskell's description.")
    set_row("st-chp4-sec-ii-p117-pyrenees-balance", True,
        "Preserves Haskell's forward-looking account linking the French collective to the Peace of the Pyrenees; not independently verified as causal analysis.",
        subject="cand-5968", obj="cand-5977", predicate="would_seal_balance_of_power_through",
        mentioned=["cand-5968", "cand-5977"], qualification="Prospective authorial account; no treaty date supplied.")
    set_row("st-chp4-sec-ii-p117-spanish-backing", True,
        "Records Massimi backing Spain as a political side; France is retained as context and a separate statement records the named quarrel.",
        subject="cand-1564", obj="cand-4591", predicate="backed_in_quarrels",
        mentioned=["cand-1564", "cand-4591", "cand-4632"],
        qualification="'As if to belie' marks Haskell's inference about motive.")
    set_row("st-chp4-sec-ii-p117-unfinished-gift-1664", True,
        "Records the unfinished work's recipient. Poussin remains giver in a qualifier because the transfer has three roles.",
        subject="cand-5988", obj="cand-1564", predicate="given_to",
        mentioned=["cand-1984", "cand-1564", "cand-5988"],
        qualification="Title continues at p.118 L219; the work was unfinished and given in 1664.",
        qpatch={"giver_candidate_id": "cand-1984", "time": "1664"})
    set_row("st-chp4-sec-ii-p117-venetian-jesuit-readmission", True,
        "Haskell attributes the agreement to the source-bounded Venetian political authority; 'their territory' is not separately identified.",
        subject="cand-11664", obj="cand-1319", predicate="agreed_to_readmit",
        mentioned=["cand-11664", "cand-1319"], qualification="'Some fifty years' is approximate.")
    set_row("st-chp4-sec-ii-p117-venetians-protested-violently", True,
        "The source records collective Venetian protest but supplies no grammatical object; prior Spanish policy is not a confirmed target.",
        subject="cand-11664", obj=None, predicate="protested_violently",
        mentioned=["cand-11664", "cand-4591", "cand-4632"],
        open_reason="The elliptical clause 'So too did the Venetians' does not state the protest target.")

    note_configs = {
        "st-chp4-sec-ii-p117note-fn1-lumbroso": (False, "Bibliographic locator only; no relation claim.", None, "cand-5980", None),
        "st-chp4-sec-ii-p117note-fn2-bartoli-drawings": (True, "The note reports Massimi owning this 160-drawing group; individual drawings and collection identity are unspecified.", "cand-5983", "cand-1564", "owned_by"),
        "st-chp4-sec-ii-p117note-fn2-michaelis": (False, "Bibliographic locator only; the cited page was not independently consulted.", None, "cand-5979", None),
        "st-chp4-sec-ii-p117note-fn3-unknown-patron": (False, "The note explicitly says the pair's original patron is unknown; do not infer Massimi as the original patron.", "cand-11667", None, None),
        "st-chp4-sec-ii-p117note-fn3-blunt-1938": (False, "Bibliographic citation only; no claim from Blunt is imported.", None, "cand-5981", None),
        "st-chp4-sec-ii-p117note-fn3-panofsky-1957": (False, "Bibliographic citation only; scan shows footnote 4 begins Bellori after Panofsky.", None, "cand-4865", None),
        "st-chp4-sec-ii-p117note-fn4-bellori-441": (False, "Bibliographic locator for Bellori's report, not a separate relation claim.", None, "cand-5982", None),
        "st-chp4-sec-ii-p117note-fn5-resident-testimony": (False, "Nested contemporary testimony; the specific reported preference for Maratta is split into a new relation candidate.", "cand-5984", "cand-1564", None),
        "st-chp4-sec-ii-p117note-fn5-claretta": (False, "Bibliographic citation only; the cited page was not independently consulted.", None, "cand-5985", None),
        "st-chp4-sec-ii-p117note-fn5-drawing-inscription": (False, "Evidence locator to an inscription; the drawing was not independently inspected.", None, "cand-5987", None),
    }
    for sid, (relation, note, subject, obj, predicate) in note_configs.items():
        row = next(r for r in note_rows if r["statement_id"] == sid)
        qualifiers = dict(row.get("qualifiers", {}) or {})
        qualifiers["relation_candidate"] = relation
        qualifiers["relation_candidate_note"] = note
        if sid == "st-chp4-sec-ii-p117note-fn3-unknown-patron":
            qualifiers["mentioned_candidate_ids"] = ["cand-11667", "cand-2009", "cand-4800"]
        updates[sid] = {
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "qualifiers": qualifiers,
        }
        if predicate:
            updates[sid]["predicate"] = predicate

    additions = [
        make_statement("st-chp4-sec-ii-p117-lessons-from-poussin", SEGMENT_ID, "cand-1564", "cand-1984",
            "trained_by", "and probably took lessons\n-from him", 215, 216,
            "Haskell says Massimi probably took lessons from Poussin.", True,
            "The student-teacher relation is explicit but qualified by 'probably'; cited inscription not independently inspected.",
            ["cand-1564", "cand-1984", "cand-5987"], qualification="'Probably' is retained.",
            marker=5, note_line=302, note_ids=["st-chp4-sec-ii-p117note-fn5-drawing-inscription"],
            extra={"ocr_corrections": [{"source_line": 216, "source_form": "-from", "print_form": "—from"}]}),
        make_statement("st-chp4-sec-ii-p117-studio-conversation", SEGMENT_ID, "cand-1984", "cand-1564",
            "talked_together_in_studio", "after they had been talking together in his studio", 215, 215,
            "Haskell summarizes Bellori's account of Poussin and Massimi talking in Poussin's studio.", True,
            "Distinct interaction before Poussin showed Massimi downstairs; Haskell's summary of Bellori.",
            ["cand-3535", "cand-1984", "cand-1564"], qualification="Studio not separately identified.",
            marker=4, note_line=301, note_ids=["st-chp4-sec-ii-p117note-fn4-bellori-441"]),
        make_statement("st-chp4-sec-ii-p117-cassiano-accompanied-on-visits", SEGMENT_ID, "cand-1564", "cand-2036",
            "accompanied_on_connoisseur_visits", "and accompanied on his visits to connoisseurs", 211, 211,
            "Haskell says Massimi accompanied Cassiano on Cassiano's visits to connoisseurs.", True,
            "The possessive 'his' refers to Cassiano; unnamed connoisseurs are not expanded.",
            ["cand-1564", "cand-2036"], qualification="Connoisseurs are unnamed.",
            marker=1, note_line=299, note_ids=["st-chp4-sec-ii-p117note-fn1-lumbroso"]),
        make_statement("st-chp4-sec-ii-p117-no-further-job-twelve-years", SEGMENT_ID, "cand-1564", None,
            "had_no_further_job_for_twelve_years", "and was given no further job for the next twelve years.", 210, 210,
            "Haskell says Massimi had no further job for the next twelve years after recall.", False,
            "Duration/status claim; no employer, job, or office is named.",
            ["cand-1564"], qualification="No exact end date is calculated."),
        make_statement("st-chp4-sec-ii-p117-portraits-of-royal-sitters", SEGMENT_ID, "cand-5976", "cand-11665",
            "has_subject", "portraits of the King and Queen and of two Infantas", 208, 208,
            "Haskell says the four portraits depict a King, Queen, and two Infantas.", True,
            "Source supplies sitter roles only; no names or monarchies are inferred.",
            ["cand-5976", "cand-11665"], qualification="Personal identities are unspecified."),
        make_statement("st-chp4-sec-ii-p117-pair-arcadian-member", SEGMENT_ID, "cand-11667", "cand-4800",
            "contains", "and the first version of the Arcadian Shepherds", 213, 213,
            "Haskell identifies the first version of the Arcadian Shepherds as one work in the pair.", True,
            "Group membership only; not evidence that the works are pendants.",
            ["cand-11667", "cand-4800", "cand-1984"], qualification="Source says first version."),
        make_statement("st-chp4-sec-ii-p117-poussin-independence", SEGMENT_ID, "cand-1984", None,
            "remained_comparatively_unaffected_by_client_status",
            "one of the only artists in the city whose independence allowed him to remain comparatively unaffected by changes in status among his clients.",
            211, 211, "Haskell describes Poussin as comparatively unaffected by changes in client status.", False,
            "Scalar authorial evaluation split from the Massimi-Poussin friendship claim.",
            ["cand-1984"], qualification="'One of the only' and 'comparatively' remain Haskell's qualifiers."),
        make_statement("st-chp4-sec-ii-p117-pair-possible-source-heirs", SEGMENT_ID, "cand-11667", "cand-11668",
            "possibly_acquired_from", "possibly even from the heirs of\nCassiano, though there is no direct evidence for this", 211, 213,
            "Haskell raises Cassiano's unidentified heirs as a possible source while expressly stating there is no direct evidence.", True,
            "Source-bounded possibility only; neither provenance nor heirs' identity is established.",
            ["cand-11667", "cand-11668", "cand-2036"], qualification="'Possibly even' and 'no direct evidence' stay attached."),
        make_statement("st-chp4-sec-ii-p117-spanish-french-quarrels", SEGMENT_ID, "cand-4591", "cand-4632",
            "quarreled_with", "their quarrels with France", 208, 208,
            "Haskell situates the Spaniards in quarrels with France.", True,
            "Political sides are named; cause and external details are not supplied.",
            ["cand-4591", "cand-4632"]),
        make_statement("st-chp4-sec-ii-p117note-fn2-bartoli-authorship", NOTE_SEGMENT_ID, "cand-5983", "cand-0251",
            "created_by", "drawings by Pietro Santo Bartoli", 300, 300,
            "The footnote identifies Pietro Santo Bartoli as maker of the 160 drawings.", True,
            "Separates stated maker from Massimi's ownership; cited Michaelis page not consulted.",
            ["cand-5983", "cand-0251"], qualification="Haskell's footnote attribution.",
            marker=2, note_line=300, note_ids=["st-chp4-sec-ii-p117note-fn2-michaelis"]),
        make_statement("st-chp4-sec-ii-p117note-fn5-maratta-preference", NOTE_SEGMENT_ID, "cand-1564", "cand-1526",
            "was_reportedly_partial_to", "et e partiale del signor Carlo Maratta", 302, 302,
            "The quoted 1675 Resident says Massimi was partial to Carlo Maratta.", True,
            "Reported preference only; no commission or patronage relation is inferred.",
            ["cand-5984", "cand-1564", "cand-1526"],
            qualification="The contemporary document is quoted by Haskell and was not independently consulted.",
            marker=5, note_line=302, note_ids=["st-chp4-sec-ii-p117note-fn5-resident-testimony"]),
    ]

    current_candidates = list(csv.DictReader(io.StringIO(originals["entity-candidates.csv"].decode("utf-8-sig"), newline="")))
    current_ids = {r["candidate_id"] for r in current_candidates}
    numbers = [int(x[5:]) for x in current_ids if x.startswith("cand-") and x[5:].isdigit()]
    new_ids = {r["candidate_id"] for r in CANDIDATES}
    if max(numbers) != 11663 or current_ids & new_ids:
        raise SystemExit("candidate ID allocation changed since p.116")
    all_candidate_ids = current_ids | new_ids
    new_mentions: list[dict] = []

    def add_mention(mid: str, cid: str, surface: str, note: str) -> None:
        start, end = unique_span(body, surface)
        new_mentions.append({
            "mention_id": mid, "segment_id": SEGMENT_ID, "candidate_id": cid,
            "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
        })

    add_mention("m-chp4-sec-ii-p117-0034", "cand-11665",
        "the King and Queen and of two Infantas", "Sitter roles only; personal identities are not supplied.")
    add_mention("m-chp4-sec-ii-p117-0035", "cand-11666",
        "many of the older Roman buildings and paintings", "Mixed group arranged for copying; originals and copies are unnamed.")
    add_mention("m-chp4-sec-ii-p117-0036", "cand-11667", pair_match.group(0),
        "Source-defined pair; not evidence of pendant status.")
    add_mention("m-chp4-sec-ii-p117-0037", "cand-11668", heirs_match.group(0),
        "Unidentified heirs, mentioned only as a possible source without direct evidence.")

    existing_ids = {r["statement_id"] for r in statement_rows}
    if existing_ids & NEW_STATEMENT_IDS or {r["statement_id"] for r in additions} != NEW_STATEMENT_IDS:
        raise SystemExit("new statement IDs collide or do not match the reviewed plan")
    if {r["mention_id"] for r in mention_rows} & {r["mention_id"] for r in new_mentions}:
        raise SystemExit("new mention ID collision")

    replacements = {
        "m-chp4-sec-ii-p117-0016": ("cand-3457", "cand-11664"),
        "m-chp4-sec-ii-p117-0017": ("cand-3457", "cand-11664"),
    }
    statement_bytes = transform_jsonl(originals["book-statements.jsonl"], updates, additions)
    candidate_bytes = append_csv(originals["entity-candidates.csv"], CANDIDATES)
    mention_bytes = append_csv(remap_mentions(originals["mentions.csv"], replacements), new_mentions)
    outputs = {
        "book-statements.jsonl": statement_bytes,
        "entity-candidates.csv": candidate_bytes,
        "mentions.csv": mention_bytes,
    }

    parsed = [json.loads(x) for x in statement_bytes.decode("utf-8").splitlines() if x.strip()]
    scoped = [
        r for r in parsed if r.get("segment_id") == SEGMENT_ID
        or (r.get("segment_id") == NOTE_SEGMENT_ID and r.get("statement_id") in NOTE_IDS | NEW_STATEMENT_IDS)
    ]
    if len(scoped) != 47 or any(r.get("qualifiers", {}).get("relation_candidate") is None for r in scoped):
        raise SystemExit(f"p.117 scope not fully classified; found {len(scoped)} rows")
    for row in scoped:
        qrow = row.get("qualifiers", {})
        for cid in [
            row.get("subject_candidate_id"), row.get("object_candidate_id"),
            *qrow.get("mentioned_candidate_ids", []),
            qrow.get("giver_candidate_id"), qrow.get("possible_source_candidate_id"),
        ]:
            if cid and cid not in all_candidate_ids:
                raise SystemExit(f"unknown candidate reference in {row['statement_id']}: {cid}")
        source_text = body if row.get("segment_id") == SEGMENT_ID else notes
        if norm(row.get("original_quote", "")) not in norm(source_text):
            raise SystemExit(f"planned quote does not match source: {row['statement_id']}")

    mentions_after = list(csv.DictReader(io.StringIO(mention_bytes.decode("utf-8-sig"), newline="")))
    for m in mentions_after:
        if m.get("segment_id") == SEGMENT_ID and body[int(m["start_char"]):int(m["end_char"])] != m["surface_form"]:
            raise SystemExit(f"planned mention span mismatch: {m['mention_id']}")

    stats = {
        "mode": "apply" if args.apply else "dry-run",
        "source_sha256": digest(source_bytes), "segment_sha256": SEGMENT_SHA256,
        "prewrite_sha256": {n: digest(b) for n, b in originals.items()},
        "body_statements_before": len(body_rows), "linked_note_statements_before": len(note_rows),
        "scoped_statements_after": len(scoped),
        "relation_candidates": sum(r["qualifiers"]["relation_candidate"] is True for r in scoped),
        "non_relations": sum(r["qualifiers"]["relation_candidate"] is False for r in scoped),
        "open_relations": [
            r["statement_id"] for r in scoped if r["qualifiers"]["relation_candidate"] is True
            and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
        ],
        "new_candidates": [r["candidate_id"] for r in CANDIDATES],
        "new_mentions": [
            {k: m[k] for k in ("mention_id", "candidate_id", "surface_form", "start_char", "end_char")}
            for m in new_mentions
        ],
        "new_statements": sorted(NEW_STATEMENT_IDS), "mention_remaps": replacements,
        "postwrite_sha256": {n: digest(b) for n, b in outputs.items()},
    }
    print(json.dumps(stats, ensure_ascii=True, indent=2))

    if args.apply:
        backups = {n: p.with_name(p.name + "." + BACKUP_SUFFIX) for n, p in paths.items()}
        if any(p.exists() for p in backups.values()):
            raise SystemExit("p.117 recovery backup already exists; inspect it before retrying")
        for name, backup in backups.items():
            shutil.copy2(paths[name], backup)
        written: list[str] = []
        try:
            for name, data in outputs.items():
                paths[name].with_name(paths[name].name + ".tmp-p117-s2").write_bytes(data)
            for name in outputs:
                paths[name].with_name(paths[name].name + ".tmp-p117-s2").replace(paths[name])
                written.append(name)
        except Exception:
            for name in written:
                shutil.copy2(backups[name], paths[name])
            raise
        print("applied; recovery backups: " + ", ".join(p.name for p in backups.values()))


if __name__ == "__main__":
    main()
