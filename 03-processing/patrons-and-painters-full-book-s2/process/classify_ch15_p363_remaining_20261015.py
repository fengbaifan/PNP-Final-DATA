import argparse
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
EXPECTED = {
    "statements": "aa9d9bf8061ad8bc26e0bfc66903c2319b2d4c4c350ef03807a29603f8811ad3",
    "mentions": "5d8ddbf2e0928518e4c8e913a48ea9d65b02b1df9457edd594ccfe6cec98b853",
    "candidates": "aa1aecc014ad439a02e1ca3c8d9eb7b7f7603e6a4083b07fa9e278b3c2571973",
}
BACKUP_TAG = ".bak-s2-ch15-p363-semantic-review-20261015"
BODY = "chp-15:15_CHP-15_sec_i:l27-36"

FALSE_NOTES = {
    "st-chp15-p363-villa-rigidity-breaks-natural-rhythm":
        "This is Haskell's architectural interpretation of the villa's form. It remains a source-attributed claim, not an edge between independently identified entities.",
    "st-chp15-p363-villa-impressive-rather-than-beautiful":
        "This is an aesthetic comparison, not a relation between distinct entities. The modal 'must have been' remains in the claim.",
    "st-chp15-p363-villa-battered-shell-at-haskell-time":
        "This is a time-relative condition and use description of the villa. No separately identified store or user group is named; the claim remains limited to Haskell's time.",
    "st-chp15-p363-garden-columns-temples-towers":
        "This is a description of garden features. The source names no individual structures, and the mention is mapped to the garden rather than inventing a separate feature group.",
    "st-chp15-p363-wealth-and-sculpture-made-farsetti-important":
        "This is Haskell's counterfactual assessment of Farsetti's social importance, not a relation between independently identified entities.",
    "st-chp15-p363-real-influence-from-contemporary-arts":
        "This is Haskell's causal interpretation of Farsetti's influence. It is retained as an attributed claim, not a graph edge.",
    "st-chp15-p363-allowance-called-particularly-fitting":
        "This is Haskell's rhetorical evaluation of the separately recorded allowance; it adds no distinct relation beyond that event and the palace's role as a centre.",
    "st-chp15-p363-farsetti-ill-incapacitated-before-death":
        "This is a biographical condition and approximate time interval, with no distinct endpoint. Preserve 'five or six years' and the 1774 death reference as stated.",
}
TRUE_NOTES = {
    "st-chp15-p363-canova-steeped-in-antiquity-before-rome":
        "The following clause says Canova had already seen Farsetti's copies of antique originals. The existing source-relative casts collection candidate is the bounded endpoint; no individual antique works are identified.",
    "st-chp15-p363-farsetti-did-not-see-canova-success":
        "This is an explicit temporal relation between Farsetti and Canova's later success. The phrase 'appeared to justify' remains Haskell's qualified evaluation, not an independently assessed outcome.",
    "st-chp15-p363-farsetti-not-only-family-arts-patron":
        "Haskell explicitly says Farsetti was not the only member of his family to encourage the arts; the next sentence names cousin Daniele as another such family member.",
}
NOTE2_ID = "st-chp15-p363-note2-boscovich-letter"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

paths = {"statements": STATEMENTS, "mentions": MENTIONS, "candidates": CANDIDATES}
for key, path in paths.items():
    if sha(path.read_bytes()) != EXPECTED[key]:
        raise SystemExit(f"unexpected pre-write hash: {key}")

statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in statements}
all_ids = set(FALSE_NOTES) | set(TRUE_NOTES) | {NOTE2_ID}
if len(all_ids) != 12 or not all_ids.issubset(by_id):
    raise SystemExit("p363 unresolved statement set changed")
for sid in all_ids:
    row = by_id[sid]
    if row["segment_id"] != BODY or row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit(f"unexpected p363 segment or pre-classification: {sid}")

candidate_ids = {row["candidate_id"] for row in __import__("csv").DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
for sid, note in FALSE_NOTES.items():
    q = by_id[sid].setdefault("qualifiers", {})
    q["relation_candidate"] = False
    q["relation_candidate_note"] = note
for sid, note in TRUE_NOTES.items():
    row = by_id[sid]
    q = row.setdefault("qualifiers", {})
    if sid == "st-chp15-p363-canova-steeped-in-antiquity-before-rome":
        row["object_candidate_id"] = "cand-1005"
    q["relation_candidate"] = True
    q["relation_candidate_note"] = note

row = by_id[NOTE2_ID]
q = row.setdefault("qualifiers", {})
if q.get("mentioned_candidate_ids") is None or "cand-10450" not in q["mentioned_candidate_ids"]:
    raise SystemExit("Boscovich letter citation candidate missing")
row["subject_candidate_id"] = "cand-2962"
row["object_candidate_id"] = "cand-10450"
row["predicate"] = "cites"
q.update({
    "relation_candidate": True,
    "relation_candidate_note": "The note explicitly cites the identified 1772 letter as published in 1811. This records the book-to-source citation path only; the letter and quoted passage were not independently consulted and do not identify the anonymous villa praiser.",
    "citation_locator": "letter from P. Boscovich to Vallisnieri, 1772; published 1811, p. 33",
    "footnote_segment_id": BODY,
    "footnote_source_lines": [36],
    "footnote_text_pending": False,
    "cited_source_independently_consulted": False,
    "citation_body_statement_ids": ["st-chp15-p363-contemporary-praised-villa"],
})
if "cand-2962" not in q["mentioned_candidate_ids"]:
    q["mentioned_candidate_ids"].append("cand-2962")
if "cand-1005" not in candidate_ids:
    raise SystemExit("antique casts endpoint missing")

for row in statements:
    if row["statement_id"].startswith("st-chp15-p363-"):
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"unknown p363 endpoint {endpoint} in {row['statement_id']}")
        for endpoint in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if endpoint not in candidate_ids:
                raise SystemExit(f"unknown p363 mention endpoint {endpoint} in {row['statement_id']}")

body = [row for row in statements if row.get("segment_id") == BODY]
counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in body)
if len(body) != 35 or counts[True] != 27 or counts[False] != 8 or counts[None] != 0:
    raise SystemExit(f"unexpected p363 closure: {len(body)} {counts}")

output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "p363_body": {"statements": len(body), "true": counts[True], "false": counts[False], "unset": counts[None]},
    "classified_ids": {"true": sorted(set(TRUE_NOTES) | {NOTE2_ID}), "false": sorted(FALSE_NOTES)},
    "corrected_endpoint": {"statement_id": "st-chp15-p363-canova-steeped-in-antiquity-before-rome", "object_candidate_id": "cand-1005"},
    "normalized_citation": {"statement_id": NOTE2_ID, "subject": "cand-2962", "object": "cand-10450", "predicate": "cites"},
    "after_sha256": sha(output),
}, ensure_ascii=False, indent=2))

if args.apply:
    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_TAG)
    if backup.exists() and sha(backup.read_bytes()) != EXPECTED["statements"]:
        raise SystemExit(f"backup differs: {backup.name}")
    if not backup.exists():
        shutil.copy2(STATEMENTS, backup)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=STATEMENTS.parent) as handle:
        handle.write(output)
        temp = Path(handle.name)
    temp.replace(STATEMENTS)
    print(json.dumps({"written_sha256": sha(STATEMENTS.read_bytes())}, indent=2))
