from __future__ import annotations

import argparse
import csv
import hashlib
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
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
PAGE_IMAGE = ROOT / ".tmp_s2_ch3_phys18-18.png"
SEGMENT = "chp-3:03_CHP-3_sec_iv:l3-6"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-iv-l3-6-relations-20261010")
EXPECTED = {
    TABLE: "b3132d176293a6da8b4a7e3bf60879ddac788769dd895d623003ebb60a7471c7",
    CANDIDATES: "1c36e0fa29ea9f353eb8ac121ede84eca7414b08b122fa3afb5ea09b4d54789e",
    MENTIONS: "95c7e31ddd47c0122c86019eda1a7b337e5a2e3ace30fcbcf0b49c84e3a28438",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    PAGE_IMAGE: "b8c9b0696003334ddc7ba7779fb6f8aeee8af50324df9ce2111faeb1fe84b09f",
}
TRUE_NOTES = {
    "st-chp3-seciv-l3-6-capuchins-unwilling-patronage": "Haskell explicitly describes the Capuchins as recipients of Barberini patronage; unwillingness qualifies the reported relationship.",
    "st-chp3-seciv-l3-6-cupola-cartoons-started": "Haskell says Pietro began painting cartoons for the Chiesa Nuova cupola in November 1646; the continuation and date remain linked to the next segment.",
    "st-chp3-seciv-l3-6-oratorian-appeal-grand-duke-leave": "The Oratorians asked the Grand Duke to grant Pietro temporary leave; the request is not evidence that leave was granted.",
    "st-chp3-seciv-l3-6-oratorian-renewed-commission": "Haskell says the Oratorians had sought further commissions from Pietro since the sacristy fresco.",
    "st-chp3-seciv-l3-6-oratorians-outclassed-by-jesuits": "This is Haskell's explicit comparative judgment about the Oratorians and Jesuits, not a formal institutional edge.",
    "st-chp3-seciv-l3-6-pietro-palazzo-pitti": "Haskell says Pietro had worked for some years on the Palazzo Pitti decoration; duration and 1646 narrative context are preserved.",
    "st-chp3-seciv-l3-6-pietro-seeking-leave-florence": "Haskell says Pietro sought opportunities to leave Florence while working on the Palazzo Pitti decoration.",
    "st-chp3-seciv-l3-6-promise-medici": "Haskell says Pietro promised to continue working for the Medici before beginning the cupola cartoons; exact terms are unstated.",
}
FALSE_NOTES = {
    "st-chp3-seciv-l3-6-barberini-exile": "This records the Barberini family's political condition, not a relation between two identified entities.",
    "st-chp3-seciv-l3-6-chiesa-nuova-largely-undecorated": "This is a church-decoration state; no bounded or independently identified work is asserted as an endpoint.",
    "st-chp3-seciv-l3-6-gesu-largely-undecorated": "This is a church-decoration state; no bounded or independently identified work is asserted as an endpoint.",
    "st-chp3-seciv-l3-6-pietro-obligations": "This is Haskell's causal assessment of Pietro's limited availability. The three named patrons are represented separately in source-reported patronage candidates.",
    "st-chp3-seciv-l3-6-s-ignazio-largely-undecorated": "This is a church-decoration state; no bounded or independently identified work is asserted as an endpoint.",
    "st-chp3-seciv-l3-6-stronger-position": "This is Haskell's qualitative assessment of the Oratorians' situation, not a relation to a second entity.",
    "st-chp3-seciv-l3-6-theatine-comparable-decoration": "This describes the church's overall decoration; the painting is not a bounded or identified work group for an entity relation.",
    "st-chp3-seciv-l3-6-urban-viii-died": "This is a biographical date claim about Urban VIII, not an entity relation.",
}
NEW_RELATIONS = [
    ("st-chp3-seciv-l3-6-pietro-patronage-sacchetti", "cand-4452", "m-chp3-seciv-l3-6-0060", "Sacchetti family"),
    ("st-chp3-seciv-l3-6-pietro-patronage-barberini", "cand-3464", "m-chp3-seciv-l3-6-0048", "Barberini family"),
    ("st-chp3-seciv-l3-6-pietro-patronage-grand-duke", "cand-5180", "m-chp3-seciv-l3-6-0061", "Grand Duke of Tuscany"),
]
PIETRO_MENTION = ("m-chp3-seciv-l3-6-0053", "cand-3096", "Pietro da Cortona")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + b"".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline for r in rows)


def atomic_write(path: Path, payload: bytes) -> None:
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as f:
            f.write(payload)
            temp = Path(f.name)
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    for path, expected in EXPECTED.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed: {path.relative_to(ROOT)}")
    require(not BACKUP.exists(), "recovery backup already exists")

    raw = TABLE.read_bytes()
    rows = read_jsonl(TABLE)
    require(len(rows) == 12750 and len({r["statement_id"] for r in rows}) == len(rows), "statement table changed")
    by_id = {r["statement_id"]: r for r in rows}
    segment_rows = [r for r in rows if r.get("segment_id") == SEGMENT]
    require(len(segment_rows) == 17, "source-segment statement count changed")
    bilateral_pending = {
        r["statement_id"] for r in segment_rows
        if r.get("subject_candidate_id") and r.get("object_candidate_id")
        and (r.get("qualifiers") or {}).get("relation_candidate") is None
    }
    single_pending = {
        r["statement_id"] for r in segment_rows
        if bool(r.get("subject_candidate_id")) != bool(r.get("object_candidate_id"))
        and (r.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(bilateral_pending == set(TRUE_NOTES), "pending bilateral statement set changed")
    require(single_pending == set(FALSE_NOTES), "pending single-ended statement set changed")
    require((by_id["st-chp3-seciv-l3-6-pietro-small-sacristy-fresco"].get("qualifiers") or {}).get("relation_candidate") is True, "existing classified statement changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[2:6])
    require("Capuchins alone had been the unwilling recipients of Barberini patronage." in segment_text, "p.76 source text changed")
    require("such powerful patrons as" in source_lines[5], "patronage sentence changed")
    for sid in bilateral_pending | single_pending:
        quote = " ".join(by_id[sid].get("original_quote", "").split())
        require(quote and quote in " ".join(segment_text.split()), f"source quote mismatch: {sid}")

    manifest = {r["segment_id"]: r for r in read_jsonl(SEGMENTS)}.get(SEGMENT)
    require(manifest and (manifest.get("source_file"), manifest.get("line_start"), manifest.get("line_end")) == ("02-sources/02-Markdown/03_CHP-3_sec_iv.md", 3, 6), "S0 segment boundary changed")
    with COVERAGE.open(encoding="utf-8-sig", newline="") as f:
        coverage = next((r for r in csv.DictReader(f) if r["segment_id"] == SEGMENT), None)
    require(coverage and (coverage["disposition"], coverage["migration_status"]) == ("reviewed", "complete"), "S2 coverage incomplete")

    candidates = {r["candidate_id"] for r in csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
    mentions = {r["mention_id"]: r for r in csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline=""))}
    require(PIETRO_MENTION[0] in mentions and (mentions[PIETRO_MENTION[0]]["candidate_id"], mentions[PIETRO_MENTION[0]]["surface_form"]) == PIETRO_MENTION[1:], "Pietro antecedent mention changed")
    for _, candidate_id, mention_id, _ in NEW_RELATIONS:
        require(candidate_id in candidates and mention_id in mentions, f"patron endpoint or mention missing: {candidate_id}")
        require(mentions[mention_id]["candidate_id"] == candidate_id, f"patron mention mapping changed: {mention_id}")

    source_line = source_lines[5]
    phrase_at = source_line.find("engagements with such powerful patrons as")
    quote_start = source_line.rfind("But ", 0, phrase_at)
    quote_end = source_line.find(".", phrase_at)
    require(phrase_at >= 0 and quote_start >= 0 and quote_end >= 0, "cannot locate patronage sentence")
    patron_quote = source_line[quote_start:quote_end + 1]
    require(not any(sid in by_id for sid, *_ in NEW_RELATIONS), "new statement ID already exists")

    for sid, note in TRUE_NOTES.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q.update(relation_candidate=True, relation_candidate_note=note)
        by_id[sid]["qualifiers"] = q
    for sid, note in FALSE_NOTES.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q.update(relation_candidate=False, relation_candidate_note=note)
        by_id[sid]["qualifiers"] = q

    new_rows = []
    for sid, patron_id, mention_id, patron_name in NEW_RELATIONS:
        q = {
            "source_line_start": 6,
            "source_line_end": 6,
            "claim": f"Haskell identifies the {patron_name} as one example of the powerful patrons with whom Pietro da Cortona had engagements that limited his availability for additional work.",
            "speaker": "Haskell",
            "text_layer": "body",
            "print_page": 76,
            "pdf_physical_page": 18,
            "time_context": "Narrative before the summer 1646 appeal; the dates of individual patronage engagements are not stated.",
            "qualification": "The phrase 'such powerful patrons as' gives non-exhaustive examples; no particular commission, work, contract, or exclusive patronage is asserted.",
            "referent_resolution": "The phrase 'the artist' refers to Pietro da Cortona named earlier in the same paragraph.",
            "mentioned_candidate_ids": [patron_id, "cand-3096"],
            "relation_candidate": True,
            "relation_candidate_note": "Haskell explicitly identifies this patron in a non-exhaustive list. This is an S2 source-reported patronage candidate; keep the artist as object and do not infer a specific commission.",
        }
        new_rows.append({
            "statement_id": sid,
            "segment_id": SEGMENT,
            "subject_candidate_id": patron_id,
            "object_candidate_id": "cand-3096",
            "predicate": "patronized",
            "qualifiers": q,
            "original_quote": patron_quote,
            "origin": "book",
            "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        })
    parent_index = next(i for i, r in enumerate(rows) if r["statement_id"] == "st-chp3-seciv-l3-6-pietro-obligations")
    rows[parent_index + 1:parent_index + 1] = new_rows

    flag = lambda r: (r.get("qualifiers") or {}).get("relation_candidate")
    bilateral = [r for r in rows if r.get("subject_candidate_id") and r.get("object_candidate_id")]
    b_true = sum(flag(r) is True for r in bilateral)
    b_false = sum(flag(r) is False for r in bilateral)
    b_pending = sum(flag(r) is None for r in bilateral)
    relation_total = sum(flag(r) is True for r in rows)
    relation_open = sum(flag(r) is True and not (r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in rows)
    require((len(rows), len(bilateral), b_true, b_false, b_pending, relation_total, relation_open) == (12753, 8546, 4801, 475, 3270, 4850, 49), "projected whole-book counts differ")
    after_segment = [r for r in rows if r.get("segment_id") == SEGMENT]
    require((len(after_segment), sum(flag(r) is True for r in after_segment), sum(flag(r) is False for r in after_segment), sum(flag(r) is None for r in after_segment)) == (20, 12, 8, 0), "projected segment totals differ")

    payload = encode_jsonl(rows, raw)
    report = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT,
        "classified_bilateral": len(TRUE_NOTES),
        "classified_single_ended_as_nonrelations": len(FALSE_NOTES),
        "new_patronage_relation_candidates": len(new_rows),
        "bilateral_after": {"total": len(bilateral), "relation_candidates": b_true, "nonrelations": b_false, "unclassified": b_pending},
        "relation_candidates_total": relation_total,
        "relation_candidates_open": relation_open,
        "post_write_sha256": hashlib.sha256(payload).hexdigest(),
    }
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    shutil.copy2(TABLE, BACKUP)
    try:
        atomic_write(TABLE, payload)
        saved = read_jsonl(TABLE)
        saved_by_id = {r["statement_id"]: r for r in saved}
        require(len(saved) == 12753 and all(saved_by_id[sid]["qualifiers"].get("relation_candidate") is True for sid, *_ in NEW_RELATIONS), "post-write checks failed")
        require(digest(TABLE) == hashlib.sha256(payload).hexdigest(), "post-write digest differs")
    except Exception:
        if BACKUP.exists():
            shutil.copy2(BACKUP, TABLE)
        raise
    report.update(result="applied", backup=str(BACKUP.relative_to(ROOT)), sha256_after=digest(TABLE))
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
