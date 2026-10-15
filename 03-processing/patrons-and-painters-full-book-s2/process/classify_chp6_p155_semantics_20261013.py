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
SEGMENT = "chp-6:06_CHP-6_sec_i:l102-110"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp6-p155-semantics-20261013"

EXPECTED_HASHES = {
    SOURCE: "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    STATEMENTS: "7881134ba1d63916578c0d0f9103320c7a87344a5e2faeffd2ac7c64e03165db",
    CANDIDATES: "7f720e2238740cb0a1054ed745373c47719a29b8edad8e65219ebe070c7f464d",
    MENTIONS: "38368632695c1a3a3479192b249782d227e87b67045e3df15f64db061362b554",
    COVERAGE: "71d835e695032cdca8d29263288a7f5688f6056fe5241f5988cdabf0d8b9f07b",
}

TARGETS = {
    "st-chp6-p155-colonna-family-patronage-exception",
    "st-chp6-p155-dughet-landscapes-with-maratta-figures",
    "st-chp6-p155-flavio-limited-employment-complete",
    "st-chp6-p155-landscape-demand-peak",
    "st-chp6-p155-lorenzo-response-to-criticism-partial",
    "st-chp6-p155-maria-impression-of-palace",
    "st-chp6-p155-maria-social-position",
    "st-chp6-p155-patronage-decline-causes",
    "st-chp6-p155-resta-profile",
    "st-chp6-p155-talent-availability-declines",
}

TRUE_NOTE = (
    "S2 identifies a specific source-grounded relation candidate; qualifications "
    "are retained, and no formal S6 edge is created."
)
FALSE_NOTE = (
    "This is a contextual, scalar, evaluative, or causal interpretation rather "
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
        "printed_page": "155", "pdf_physical_page": 10,
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
           qualification, mentioned, start, end, first=None, last=None,
           quote=None, speaker="Haskell", text_layer="authorial historical narrative",
           extra=None):
    row = by_id[sid]
    q = row.setdefault("qualifiers", {})
    original_quote = quote if quote is not None else extract(SOURCE_LINES, start, end, first, last)
    row.update({"subject_candidate_id": subject, "object_candidate_id": object_,
                "predicate": predicate, "original_quote": original_quote})
    q.update({"source_line_start": start, "source_line_end": end,
              "printed_page": "155", "pdf_physical_page": 10,
              "claim": claim, "speaker": speaker, "text_layer": text_layer,
              "qualification": qualification,
              "mentioned_candidate_ids": mentioned,
              "relation_candidate": relation,
              "relation_candidate_note": TRUE_NOTE if relation else FALSE_NOTE})
    if extra:
        q.update(extra)
    return row


SOURCE_LINES = SOURCE.read_text(encoding="utf-8-sig").splitlines()
SEGMENT_TEXT = "\n".join(SOURCE_LINES[101:110])


def build_outputs():
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")
    if SOURCE_LINES[101].strip() != "[Page 155]":
        raise SystemExit("p.155 page boundary changed")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs in table")
    unset = {sid for sid, row in by_id.items()
             if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset != TARGETS:
        raise SystemExit(f"p.155 unset target set changed: {sorted(unset)}")

    cfields, candidates, cbom = read_csv(CANDIDATES)
    mfields, mentions, mbom = read_csv(MENTIONS)
    vfields, coverage, vbom = read_csv(COVERAGE)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    new_candidate_id = "cand-12001"
    new_mention_ids = {"m-chp6-p155-prelates", "m-chp6-p155-economic-collapse"}
    if new_candidate_id in candidate_ids or new_mention_ids & mention_ids:
        raise SystemExit("a planned p.155 candidate or mention ID already exists")
    numbers = [int(r["candidate_id"].split("-")[1]) for r in candidates
               if r["candidate_id"].startswith("cand-") and r["candidate_id"].split("-")[1].isdigit()]
    if max(numbers) != 12000:
        raise SystemExit(f"candidate sequence changed: max={max(numbers)}")
    if "cand-6247" not in candidate_ids:
        raise SystemExit("the existing economic-collapse candidate is missing")
    cov = next((r for r in coverage if r["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.155 coverage state: {cov}")

    candidate_to_add = make_candidate(
        new_candidate_id,
        "Prelates subject to Alexander VII's measures against residence in Rome (unnamed group)",
        "term",
        "Haskell reports papal measures to prevent prelates from leaving their provincial sees to live in Rome; no individual prelate or measure is named.",
        104,
    )
    new_mentions = [
        make_mention("m-chp6-p155-prelates", new_candidate_id, "prelates",
                     "Unnamed group targeted by the Pope's measures restricting residence in Rome.", SEGMENT_TEXT),
        make_mention("m-chp6-p155-economic-collapse", "cand-6247", "economic collapse",
                     "Economic decline as one of Haskell's stated causes for fewer and less influential great patrons.", SEGMENT_TEXT),
    ]
    old_segment_mentions = [m for m in mentions if m["segment_id"] == SEGMENT]
    for new in new_mentions:
        start, end = int(new["start_char"]), int(new["end_char"])
        for old in old_segment_mentions:
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if start < old_end and old_start < end:
                raise SystemExit(f"new p.155 mention overlaps existing mention: {new['mention_id']} / {old['mention_id']}")
    for i, left in enumerate(new_mentions):
        left_start, left_end = int(left["start_char"]), int(left["end_char"])
        for right in new_mentions[i + 1:]:
            right_start, right_end = int(right["start_char"]), int(right["end_char"])
            if left_start < right_end and right_start < left_end:
                raise SystemExit(f"new p.155 mentions overlap: {left['mention_id']} / {right['mention_id']}")

    revise(by_id, "st-chp6-p155-colonna-family-patronage-exception",
           subject="cand-4638", object_="cand-6334", predicate="only-old-established-clan-continues-to-acquire-important-pictures",
           claim="Haskell says that among the old-established clans only the Colonna continued almost without interruption to acquire important new pictures.", relation=True,
           qualification="This is Haskell's account of an exception to broader patronage decline; 'only' and 'almost without interruption' remain qualified source wording.",
           mentioned=["cand-4638", "cand-6334"], start=105, end=105,
           first="Indeed, of the old-established clans", last="important new pictures.")
    revise(by_id, "st-chp6-p155-dughet-landscapes-with-maratta-figures",
           subject="cand-0949", object_="cand-1526", predicate="dughet-landscapes-sometimes-include-figures-by-maratta",
           claim="Haskell says some landscapes by Gaspard Dughet included figures by Carlo Maratta.", relation=True,
           qualification="The source says 'sometimes'; it does not identify which landscapes or figures.",
           mentioned=["cand-0949", "cand-1526"], start=107, end=107,
           first="Gaspard Dughet (sometimes", last="Carlo Maratta)")
    revise(by_id, "st-chp6-p155-flavio-limited-employment-complete",
           subject="cand-0665", object_="cand-0671", predicate="patronage-reduces-flavio-opportunities-to-employ-first-rate-artists",
           claim="Haskell completes the previous page's statement: the extent of Alexander VII's patronage reduced Flavio's opportunity to employ first-rate artists.", relation=True,
           qualification="The p.154 fragment and p.155 continuation are read together; this does not identify which artists Flavio would otherwise have employed.",
           mentioned=["cand-0671", "cand-0665", "cand-3540"], start=103, end=103,
           quote="artists",
           extra={"continuation_status": "complete", "continuation_resolved_from_statement_id": "st-chp6-p154-flavio-limited-interest-partial",
                  "continued_from_segment_id": "chp-6:06_CHP-6_sec_i:l91-100", "continued_from_source_line": 100})
    revise(by_id, "st-chp6-p155-landscape-demand-peak",
           subject=None, object_="cand-6336", predicate="constant-demand-for-landscapes-peaks-at-start-of-new-century",
           claim="Haskell says constant demand for landscapes reached its peak at the beginning of the new century.", relation=False,
           qualification="This is a trend statement; 'the new century' is not converted to a specific calendar year.",
           mentioned=["cand-6336"], start=108, end=108,
           first="Commenting on the constant demand", last="the beginning of the new century,")
    revise(by_id, "st-chp6-p155-lorenzo-response-to-criticism-partial",
           subject="cand-0811", object_="cand-6337", predicate="colonna-takes-no-note-of-landscape-and-scholarly-criticism",
           claim="Haskell says Lorenzo was too lively and expansive a patron to take note of the criticism, completed on p.156 as complaints from scholars or pedants.", relation=True,
           qualification="The sentence crosses to p.156 L113; the source characterizes Lorenzo's response, not the validity of the critics' arguments.",
           mentioned=["cand-0811", "cand-6337"], start=109, end=109,
           first="Colonna, however", last="to take any note",
           extra={"continuation_status": "closed", "continuation_to_segment_id": "chp-6:06_CHP-6_sec_i:l112-118",
                  "continuation_to_fragment": "of the complaints of scholars or pedants",
                  "continuation_resolved_by_segment": "chp-6:06_CHP-6_sec_i:l112-118",
                  "continuation_resolved_by_source_line": 113,
                  "continuation_resolved_by_statement_id": "st-chp6-p156-lorenzo-ignores-criticism-complete"})
    revise(by_id, "st-chp6-p155-maria-impression-of-palace",
           subject="cand-1509", object_="cand-0815", predicate="struck-by-splendour-of-husbands-family-palace-on-arrival",
           claim="Haskell says Maria Mancini was struck on arriving in Rome by the splendour of her husband's family palace, after the comparative meanness of its exterior.", relation=True,
           qualification="This records Haskell's account of Maria's impression and comparison, not a neutral architectural ranking.",
           mentioned=["cand-1509", "cand-0811", "cand-0815", "cand-4490"], start=106, end=106,
           first="When she arrived in Rome", last="after the comparative meanness of its exterior.")
    revise(by_id, "st-chp6-p155-maria-social-position",
           subject="cand-1509", object_="cand-0675", predicate="one-of-two-leading-ladies-in-roman-society-with-christina",
           claim="Haskell says Maria was for some years one of the two leading ladies in Roman society, rivalled only by Queen Christina of Sweden, while bearing Lorenzo sons.", relation=True,
           qualification="This is Haskell's description of social standing; it does not identify a formal office or rank.",
           mentioned=["cand-1509", "cand-0811", "cand-4490", "cand-0675"], start=106, end=107,
           first="For some years, while she bore him son after son", last="Christina of Sweden.")
    revise(by_id, "st-chp6-p155-patronage-decline-causes",
           subject=None, object_=None, predicate="economic-collapse-and-papal-residence-measures-contribute-to-decline-in-great-patrons",
           claim="Haskell attributes the decline in the number and standards of great patrons partly to economic collapse and papal measures discouraging prelates from leaving their provincial sees to live in Rome.", relation=False,
           qualification="This is Haskell's causal explanation of a broad historical decline. The specific papal policy and its target group are represented separately.",
           mentioned=["cand-6247", "cand-0665", "cand-4490", new_candidate_id], start=104, end=105,
           first="The reasons for this decline", last="played a considerable part in the process.1")
    revise(by_id, "st-chp6-p155-resta-profile",
           subject="cand-2134", object_=None, predicate="described-as-scholarly-collector-and-pioneer-in-drawing-study",
           claim="Haskell describes Padre Sebastiano Resta as a scholarly collector and pioneer in the study of Renaissance drawings.", relation=False,
           qualification="This is a biographical characterization, not a specific relation to a named work or institution.",
           mentioned=["cand-2134", "cand-3578"], start=108, end=108,
           first="Padre Sebastiano Resta", last="study of Renaissance drawings,")
    revise(by_id, "st-chp6-p155-talent-availability-declines",
           subject=None, object_=None, predicate="wide-choice-of-talent-under-earlier-popes-no-longer-exists-under-alexander-vii",
           claim="Haskell says the wide choice of talent available under Paul V and Urban VIII no longer existed under Alexander VII.", relation=False,
           qualification="This is a historical comparison of artistic availability, not an assertion that named artists disappeared.",
           mentioned=["cand-0393", "cand-0228", "cand-0665"], start=104, end=104,
           first="It is also true that the wide choice of talent", last="no longer in existence.")
    revise(by_id, "st-chp6-p155-lorenzo-maria-marriage",
           subject="cand-0811", object_="cand-1509", predicate="marries-maria-mancini-in-1661",
           claim="Haskell says Lorenzo Onofrio married Maria Mancini in 1661, when he was 24.", relation=True,
           qualification="The age and year are as stated by Haskell; no independent chronology is added.",
           mentioned=["cand-0811", "cand-1509"], start=106, end=106,
           first="In 1661, at the age of 24", last="he married Maria Mancini")

    additions = [
        new_statement("st-chp6-p155-old-and-new-families-economic-position", None, None,
            "old-families-impoverished-and-new-families-reluctant-to-settle-in-rome",
            "Haskell says old families were increasingly impoverished and new families increasingly reluctant to settle in Rome.", False,
            "This is a broad economic and settlement trend; the passage does not enumerate families beyond the later Colonna exception.",
            ["cand-4490"], 105, 105,
            "The old families were increasingly impoverished", "reluctant to settle in Rome."),
        new_statement("st-chp6-p155-pope-measures-restrict-prelates-residence", "cand-0665", new_candidate_id,
            "introduces-measures-to-prevent-prelates-leaving-provincial-sees-for-rome",
            "Haskell says the Pope introduced measures intended to prevent prelates from abandoning their provincial sees and living in Rome.", True,
            "The prelates and measures are unnamed; this records the stated aim of the policy, not whether it succeeded.",
            ["cand-0665", new_candidate_id, "cand-4490"], 104, 105,
            "a number of measures introduced by the Pope", "living in\nRome"),
        new_statement("st-chp6-p155-maria-niece-of-mazarin", "cand-1509", "cand-1588",
            "niece-of-cardinal-mazarin", "Haskell identifies Maria Mancini as Cardinal Mazarin's niece.", True,
            "The kinship is stated by Haskell; no further family line is inferred.",
            ["cand-1509", "cand-1588"], 106, 106,
            "the niece of", "Cardinal Mazarin"),
        new_statement("st-chp6-p155-maria-first-love-of-louis-xiv", "cand-1509", "cand-1447",
            "described-as-louis-xiv-first-love", "Haskell describes Maria Mancini as Louis XIV's first love.", True,
            "This preserves Haskell's characterization without adding a date or further personal history.",
            ["cand-1509", "cand-1447"], 106, 106,
            "the first love of", "Louis XIV."),
    ]
    new_ids = {row["statement_id"] for row in additions}
    if len(new_ids) != len(additions) or new_ids & set(by_id):
        raise SystemExit("duplicate or preexisting planned p.155 statement ID")
    for row in additions:
        by_id[row["statement_id"]] = row
    statements = [by_id[row["statement_id"]] for row in statements]
    statements.extend(additions)

    # Preserve the source-level spelling, while recording the two OCR readings
    # that the p.155 physical scan corrects in Resta's quoted criticism.
    resta = by_id.get("st-chp6-p155-resta-landscape-criticism")
    if not resta or resta.get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("the already classified Resta criticism statement changed")
    rq = resta["qualifiers"]
    corrections = list(rq.get("ocr_corrections", []))
    corrections.extend([
        {"source_file": SOURCE_FILE, "source_line": 109, "ocr": "hot much enjoyed",
         "print": "not much enjoyed", "basis": "CHP-6.pdf physical page 10."},
        {"source_file": SOURCE_FILE, "source_line": 109, "ocr": "earher'days",
         "print": "earlier days", "basis": "CHP-6.pdf physical page 10."},
    ])
    rq["ocr_corrections"] = corrections

    valid_candidates = candidate_ids | {new_candidate_id}
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
            raise SystemExit(f"p.155 statement remains unclassified: {row['statement_id']}")

    cov["note"] += (
        " p.155 physical page 10 was reviewed against CHP-6.pdf. The ten previously unset statements were classified; "
        "Colonna acquisition, the Dughet-Maratta figure relation, Maria's marriage and separate kinship/first-love claims, "
        "and the Pope's residence measures were distinguished from broad economic comparisons and aesthetic judgments. "
        "One source-bounded prelate group and two exact mentions were added. The p.154 Flavio-patronage sentence and the "
        "p.155 criticism sentence retain their p.154 and p.156 continuation links. The printed page corrects two OCR words "
        "in Resta's quotation; corrections are recorded on its existing statement. Footnote links remain intact."
    )

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        CANDIDATES: csv_bytes(cfields, candidates + [candidate_to_add], cbom),
        MENTIONS: csv_bytes(mfields, mentions + new_mentions, mbom),
        COVERAGE: csv_bytes(vfields, coverage, vbom),
    }
    summary = {
        "segment": SEGMENT, "previously_unset_classified": len(TARGETS),
        "new_atomic_statements": len(additions), "segment_statement_count_after": len(segment_rows),
        "relation_candidates_in_segment_after": sum(r["qualifiers"].get("relation_candidate") is True for r in segment_rows),
        "non_relational_in_segment_after": sum(r["qualifiers"].get("relation_candidate") is False for r in segment_rows),
        "unset_in_segment_after": sum(r["qualifiers"].get("relation_candidate") is None for r in segment_rows),
        "candidate_added": new_candidate_id, "mentions_added": sorted(new_mention_ids),
        "mode": "dry-run",
    }
    if summary["unset_in_segment_after"] or summary["segment_statement_count_after"] != 31:
        raise SystemExit(f"unexpected p.155 segment totals: {summary}")
    return outputs, summary


def main():
    parser = argparse.ArgumentParser(description="Classify p.155 S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up affected tables and apply the reviewed p.155 batch.")
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
