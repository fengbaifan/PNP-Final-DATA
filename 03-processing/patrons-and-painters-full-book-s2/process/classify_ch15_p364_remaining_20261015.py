import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md"
BODY = "chp-15:15_CHP-15_sec_i:l38-41"
BACKUP_TAG = ".bak-s2-ch15-p364-classification-20261015"
EXPECTED = {
    "statements": "07fadfbf5e08fdcdffea3f22c558c6267807ffd355eb85c437dad471137c8d91",
    "candidates": "aa1aecc014ad439a02e1ca3c8d9eb7b7f7603e6a4083b07fa9e278b3c2571973",
    "mentions": "1f19c4915b39f367825a821abf1d12c3057f7401efa4715028256a28fb5c0eec",
    "coverage": "b7570dd49b18dbbf673aace92124157cf10aeb4339c5087df21e4bdb70ffb23b",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

paths = {
    "statements": STATEMENTS,
    "candidates": CANDIDATES,
    "mentions": MENTIONS,
    "coverage": COVERAGE,
}
for key, path in paths.items():
    if sha(path.read_bytes()) != EXPECTED[key]:
        raise SystemExit(f"unexpected pre-write hash: {key}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[37:41])
if not segment_text.startswith("[Page 364]\npatronage os contemporary artists."):
    raise SystemExit("p.364 S0 source span changed")

statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in statements}
candidate_rows = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
mention_rows = list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
mention_by_id = {row["mention_id"]: row for row in mention_rows}
coverage_rows = list(csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline="")))

true_notes = {
    "st-chp15-p364-tommaso-preferred-books-manuscripts":
        "Tommaso's explicit preference links him to the identified personal collection; keep the comparison with works of art as a qualifier and do not invent a separate art endpoint.",
    "st-chp15-p364-tommaso-loyal-to-family-tradition":
        "The claim concerns an abstract Farsetti family tradition, not membership in or loyalty to the family entity. A separate term candidate preserves that distinction.",
    "st-chp15-p364-tommaso-embittered-by-nephew":
        "Haskell directly links Anton Francesco's extravagance to the embitterment of Tommaso's last years. This is a source-attributed biographical effect; the nephew relation is independently explicit.",
    "st-chp15-p364-farsetti-example-as-nobility-withdrew":
        "Haskell asserts that the unnamed Venetian nobility no longer occupied its traditional arts-support role. The group and role remain broad source-defined concepts; no individual, policy, or institution is inferred.",
    "st-chp15-p364-denunciation-to-no-avail":
        "'This' refers to the denunciation event. 'To no avail' records the reported outcome without inferring a response or action by the Inquisitors.",
    "st-chp15-p364-farsetti-collections-sold":
        "The plural collections are unitemized and are not equated with the indexed cast or painting collections. The statement links the source-defined collection set to the separately indexed sale event cand-1012; no owner or buyer is inferred.",
    "st-chp15-p364-venetian-scholars-dismayed-by-sale":
        "The preceding sale event is reported to have caused dismay among an unnamed collective of Venetian scholars. No individuals or institution are identified.",
    "st-chp15-p364-new-patron-public-service-model":
        "Haskell attributes the public-service conception to plural newer patrons and names Andrea Memmo as an example. The group endpoint preserves that scope and does not assign the view to Memmo alone.",
}
false_notes = {
    "st-chp15-p364-tommaso-rueful-about-filippo-costs":
        "The 'note of ruefulness' is Haskell's interpretation of Tommaso's account and its discussion of expense, not a distinct relation between Tommaso and Filippo. The collection and expense claims remain separately recorded.",
    "st-chp15-p364-property-finally-broken-up-and-sold":
        "The source does not identify the owner or scope of 'the property' or the agent in its breakup. Preserve the attributed claim without mapping it to a particular palace, estate, or person.",
    "st-chp15-p364-retrospective-farsetti-influence-negligible-or-deleterious":
        "This is Haskell's retrospective evaluation of Farsetti's influence, not a relation between independently identified entities.",
    "st-chp15-p364-farsetti-shadowy-aims-more-interesting-than-achievements":
        "This is Haskell's characterization of Farsetti and comparison of aims with achievements, not a relation between distinct entities.",
    "st-chp15-p364-farsetti-midway-between-patron-models":
        "This is Haskell's typological placement between broad models of patronage. It establishes no direct relation between Farsetti and Andrea Memmo or between two identified groups.",
}
if len(true_notes) != 8 or len(false_notes) != 5:
    raise SystemExit("internal p.364 classification count changed")
target_ids = set(true_notes) | set(false_notes)
if len(target_ids) != 13 or not target_ids.issubset(by_id):
    raise SystemExit("p.364 unresolved statement set changed")
body_rows = [row for row in statements if row.get("segment_id") == BODY]
if len(body_rows) != 21:
    raise SystemExit(f"unexpected p.364 statement count: {len(body_rows)}")
for sid in target_ids:
    row = by_id[sid]
    if row.get("segment_id") != BODY or row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit(f"unexpected p.364 statement pre-state: {sid}")

new_candidates = [
    {
        "candidate_id": "cand-12222", "index_entry_id": "", "canonical_name": "Farsetti family tradition described on p.364",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "An abstract tradition to which Haskell says Tommaso Giuseppe remained loyal. Distinct from the Farsetti family entity cand-10431 and from the family-history account whose identity remains unresolved.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": BODY + "#L39",
    },
    {
        "candidate_id": "cand-12223", "index_entry_id": "", "canonical_name": "Traditional role of supporting the arts attributed to the nobility (p.364)",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "The social role Haskell says the nobility was no longer playing. No particular policy, institution, or individual is identified.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": BODY + "#L40",
    },
    {
        "candidate_id": "cand-12224", "index_entry_id": "", "canonical_name": "Unitemized group of Farsetti collections sold in the early 19th century (p.364)",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "The source refers to a plural set whose exact items, owner, and scope are unspecified. Do not equate it with the indexed cast or painting collections cand-1005 and cand-1006, or assume those exhaust the set.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": BODY + "#L39",
    },
    {
        "candidate_id": "cand-12225", "index_entry_id": "", "canonical_name": "Unnamed Venetian scholars described as dismayed by the collections sale (p.364)",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "An unnamed collective in Haskell's report of the sale's reception. No individual scholars, institution, or precise group boundary is supplied.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": BODY + "#L39",
    },
    {
        "candidate_id": "cand-12226", "index_entry_id": "", "canonical_name": "New men in arts patronage exemplified by Andrea Memmo (p.364)",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "A plural, source-defined group contrasted with self-sufficient patrons of the past. Andrea Memmo is an example, not the group's sole member; no formal association is implied.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": BODY + "#L41",
    },
]
if any(row["candidate_id"] in candidate_by_id for row in new_candidates):
    raise SystemExit("one or more new p.364 candidate IDs already exist")
if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) != 12221:
    raise SystemExit("candidate sequence changed")

new_mentions_spec = [
    ("m-chp15-p364-nobility-0001", "cand-10473", "the nobility", "Unspecified noble group in the Venetian context; no named individuals or formal organization are inferred."),
    ("m-chp15-p364-arts-role-0001", "cand-12223", "traditional rôle of supporting the arts", "Social role stated by Haskell; no specific programme or institution is named."),
    ("m-chp15-p364-collections-0001", "cand-12224", "the collections", "Unitemized plural group; not equated with indexed collection candidates cand-1005 or cand-1006."),
    ("m-chp15-p364-sale-0001", "cand-1012", "sold", "The verb anchors the sale event indexed at F.csv#27; it does not identify the sold items, owner, or buyer."),
    ("m-chp15-p364-scholars-0001", "cand-12225", "Venetian scholars", "Unnamed collective; no individual or institution is identified."),
    ("m-chp15-p364-new-men-0001", "cand-12226", "those new men", "Plural group exemplified by Andrea Memmo; the source does not make Memmo its sole member."),
]
for mention_id, candidate_id, surface, _ in new_mentions_spec:
    if mention_id in mention_by_id:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if candidate_id not in candidate_by_id and candidate_id not in {row["candidate_id"] for row in new_candidates}:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    start = segment_text.find(surface)
    if start < 0 or segment_text.find(surface, start + 1) >= 0:
        raise SystemExit(f"source surface missing or ambiguous: {surface}")

tradition_mention = mention_by_id.get("m-chp15-p364-0007")
if not tradition_mention or tradition_mention["candidate_id"] != "cand-10431":
    raise SystemExit("family-tradition mention pre-state changed")
tradition_mention["candidate_id"] = "cand-12222"
tradition_mention["note"] = "Source-defined family tradition/concept, distinct from the Farsetti family entity cand-10431."

endpoint_updates = {
    "st-chp15-p364-tommaso-loyal-to-family-tradition": ("cand-1013", "cand-12222", ["cand-1013", "cand-12222"]),
    "st-chp15-p364-farsetti-example-as-nobility-withdrew": ("cand-10473", "cand-12223", ["cand-10473", "cand-12223"]),
    "st-chp15-p364-farsetti-collections-sold": ("cand-12224", "cand-1012", ["cand-12224", "cand-1012"]),
    "st-chp15-p364-venetian-scholars-dismayed-by-sale": ("cand-1012", "cand-12225", ["cand-1012", "cand-12225"]),
    "st-chp15-p364-new-patron-public-service-model": ("cand-12226", "cand-10467", ["cand-12226", "cand-10467"]),
}
for sid, (subject, obj, mentioned) in endpoint_updates.items():
    row = by_id[sid]
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = obj
    row.setdefault("qualifiers", {})["mentioned_candidate_ids"] = mentioned

for sid, note in true_notes.items():
    q = by_id[sid].setdefault("qualifiers", {})
    q["relation_candidate"] = True
    q["relation_candidate_note"] = note
for sid, note in false_notes.items():
    q = by_id[sid].setdefault("qualifiers", {})
    q["relation_candidate"] = False
    q["relation_candidate_note"] = note

candidate_rows.extend(new_candidates)
new_mentions = []
for mention_id, candidate_id, surface, note in new_mentions_spec:
    start = segment_text.find(surface)
    new_mentions.append({
        "mention_id": mention_id, "segment_id": BODY, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
    })
mention_rows.extend(new_mentions)

coverage_matches = [row for row in coverage_rows if row["segment_id"] == BODY]
if len(coverage_matches) != 1:
    raise SystemExit("p.364 coverage row missing or duplicated")
coverage_note = coverage_matches[0]["note"]
append_note = (
    " 2026-10-15 semantic classification: all 21 body statements are now classified (16 relation candidates, 5 non-relational claims). "
    "Added source-bound candidates for family tradition, the traditional arts-support role, the unitemized collection group, Venetian scholars, and the newer-patron group; "
    "reused the existing sale-event candidate cand-1012. The collection set remains unitemized, and Memmo remains an exemplar rather than the sole holder of the public-service view."
)
if "2026-10-15 semantic classification:" in coverage_note:
    raise SystemExit("p.364 coverage already contains this classification note")
coverage_matches[0]["note"] = coverage_note + append_note

candidate_ids = {row["candidate_id"] for row in candidate_rows}
if len(candidate_ids) != len(candidate_rows):
    raise SystemExit("duplicate candidate IDs after p.364 update")
mention_ids = {row["mention_id"] for row in mention_rows}
if len(mention_ids) != len(mention_rows):
    raise SystemExit("duplicate mention IDs after p.364 update")
for row in statements:
    if row.get("segment_id") == BODY:
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"unknown p.364 statement endpoint {endpoint} in {row['statement_id']}")
        for endpoint in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if endpoint not in candidate_ids:
                raise SystemExit(f"unknown p.364 mention endpoint {endpoint} in {row['statement_id']}")
for row in new_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"p.364 mention span mismatch: {row['mention_id']}")

body_rows = [row for row in statements if row.get("segment_id") == BODY]
counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in body_rows)
if len(body_rows) != 21 or counts[True] != 16 or counts[False] != 5 or counts[None] != 0:
    raise SystemExit(f"unexpected p.364 closure: {len(body_rows)} {counts}")

def csv_bytes(rows, fields):
    from io import StringIO
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + stream.getvalue()).encode("utf-8")

outputs = {
    STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
    CANDIDATES: csv_bytes(candidate_rows, list(candidate_rows[0])),
    MENTIONS: csv_bytes(mention_rows, list(mention_rows[0])),
    COVERAGE: csv_bytes(coverage_rows, list(coverage_rows[0])),
}
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "segment": BODY,
    "statements": {"total": len(body_rows), "true": counts[True], "false": counts[False], "unset": counts[None]},
    "new_candidates": [row["candidate_id"] for row in new_candidates],
    "new_mentions": [row["mention_id"] for row in new_mentions],
    "endpoint_updates": endpoint_updates,
    "after_sha256": {path.name: sha(data) for path, data in outputs.items()},
}, ensure_ascii=False, indent=2))

if args.apply:
    for key, path in paths.items():
        backup = path.with_name(path.name + BACKUP_TAG)
        if backup.exists() and sha(backup.read_bytes()) != EXPECTED[key]:
            raise SystemExit(f"backup differs: {backup.name}")
        if not backup.exists():
            shutil.copy2(path, backup)
    for path, data in outputs.items():
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent) as handle:
            handle.write(data)
            temp = Path(handle.name)
        temp.replace(path)
    print(json.dumps({"written_sha256": {path.name: sha(path.read_bytes()) for path in outputs}}, ensure_ascii=False, indent=2))
