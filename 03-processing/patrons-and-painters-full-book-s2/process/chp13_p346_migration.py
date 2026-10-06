"""Controlled S2 migration for printed p.346; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
SEGMENT = "chp-13:13_CHP-13_intro:l173-177"
P345_SEGMENT = "chp-13:13_CHP-13_intro:l161-171"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
SEGMENT_SHA = "1707ce58364293f8f81819502d125502c9cc25d285580b0ecb3377ab547939d1"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p346-20261003"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.346 migration")
args = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if sha(SOURCE) != SOURCE_SHA or sha(PDF) != PDF_SHA:
    raise SystemExit("source Markdown or registered PDF SHA changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[172:177])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("p.346 source segment changed")
for token in (
    "agent for many far more important collectors than himself",
    "Zaccaria Sagredo,",
    "Zanetti, Consul Smith",
    "the flourishing and parasitic art world of Venice",
    "stall in the Merceria",
    "hunchback Leonardo Pasquetti",
):
    if token not in segment_text:
        raise SystemExit(f"required printed-page text missing: {token}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
state = (len(candidates), len(mentions), len(statements), len(coverage))
if state != (10112, 21865, 9772, 830):
    raise SystemExit(f"unexpected pre-state {state}")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
required_candidates = {"cand-1853", "cand-2329", "cand-2440", "cand-2640", "cand-2719", "cand-2838"}
if not required_candidates.issubset(candidate_by_id):
    raise SystemExit(f"required existing candidates missing: {sorted(required_candidates - candidate_by_id.keys())}")
new_candidate_id = "cand-10126"
if new_candidate_id in candidate_by_id:
    raise SystemExit(f"candidate ID already exists: {new_candidate_id}")

coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or coverage_by_id[SEGMENT]["disposition"] != "queued":
    raise SystemExit("p.346 coverage is not queued")
if P345_SEGMENT not in coverage_by_id or coverage_by_id[P345_SEGMENT]["disposition"] != "reviewed":
    raise SystemExit("p.345 coverage is no longer reviewed")

segment_rows = read_jsonl(TABLES / "segments.jsonl")
segment = next((row for row in segment_rows if row["segment_id"] == SEGMENT), None)
if not segment or segment["sha256"] != SEGMENT_SHA:
    raise SystemExit("p.346 segment row/hash changed")

new_candidate = {field: "" for field in candidate_fields}
new_candidate.update({
    "candidate_id": new_candidate_id,
    "canonical_name": "Merceria (Venice; specific site unresolved)",
    "suggested_type": "place",
    "status": "open",
    "detail": "The passage identifies the Merceria as the location of a print stall where Toni would buy prints. The specific stall and exact place referent are not identified; no modern address is inferred.",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT}#L176",
})

mention_specs = [
    ("cand-2640", "Toni", "Coreferential subject of the p.345 dealer/agent sentence and guide in this passage."),
    ("cand-2329", "Zaccaria Sagredo", "Named as one of the collectors for whom Toni acted as an agent."),
    ("cand-2838", "Zanetti", "Surname only. Provisionally linked to the elder Zanetti from the preceding contrast; identity remains for S3 alignment."),
    ("cand-2440", "Consul Smith", "Consular title plus surname; reused Joseph Smith index candidate pending S3 identity alignment."),
    ("cand-2719", "Venice", "The Venetian art world and Merceria passage setting."),
    (new_candidate_id, "the Merceria", "Named location of the print stall; exact site remains unresolved."),
    ("cand-1853", "hunchback Leonardo Pasquetti", "Person named as the print seller; 'hunchback' is retained only as the author's descriptor."),
]

mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
for i, (candidate_id, surface, note) in enumerate(mention_specs, 1):
    mention_id = f"m-s2-ch13-p346-{i:03d}"
    if mention_id in mention_ids:
        raise SystemExit(f"mention ID exists: {mention_id}")
    start = segment_text.find(surface)
    if start < 0:
        raise SystemExit(f"mention not found: {surface!r}")
    if candidate_id not in candidate_by_id and candidate_id != new_candidate_id:
        raise SystemExit(f"missing candidate {candidate_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })

statement_by_id = {row["statement_id"]: row for row in statements}
new_statements = []


def add_statement(statement_id, start, end, subject, obj, predicate, claim, quote, qualification, mentioned, relation=False, speaker="Haskell", layer="authorial narrative", cross_refs=()):
    if statement_id in statement_by_id or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"statement exists: {statement_id}")
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 346,
        "pdf_physical_page": 19,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(mentioned),
    }
    if relation:
        qualifiers["relation_candidate"] = True
    if cross_refs:
        qualifiers["cross_reference_segments"] = list(cross_refs)
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })


add_statement(
    "st-chp13-p346-toni-dealer-agent-role", 174, 175, "cand-2640", None,
    "dealer_and_agent_for_collectors",
    "The passage completes its statement that Toni was a dealer and acted as agent for collectors described by Haskell as far more important than himself.",
    "agent for many far more important collectors than himself, such as Zaccaria Sagredo,\nZanetti, Consul Smith and various foreign visitors.",
    "The sentence begins on p.345 L171 ('He was also a dealer, and he acted as') and closes here. 'Far more important' is Haskell's characterization; the statement does not infer a specific transaction or date.",
    ["cand-2640", "cand-2329", "cand-2838", "cand-2440"],
    cross_refs=[P345_SEGMENT],
)
for candidate_id, label, identity_note in [
    ("cand-2329", "Zaccaria Sagredo", "The index candidate is reused pending S3 alignment."),
    ("cand-2838", "Zanetti", "Surname only; provisional elder-Zanetti mapping follows the preceding contrast, but the agent claim does not explicitly disambiguate the identity."),
    ("cand-2440", "Consul Smith", "The index candidate for Joseph Smith is reused; the passage supplies a title and surname only."),
]:
    add_statement(
        f"st-chp13-p346-toni-agent-for-{label.lower().replace(' ', '-')}", 174, 175,
        "cand-2640", candidate_id, "acted_as_agent_for",
        f"Haskell names {label} as one of the collectors for whom Toni acted as an agent.",
        "agent for many far more important collectors than himself, such as Zaccaria Sagredo, Zanetti, Consul Smith and various foreign visitors.",
        f"{identity_note} The passage supplies no individual commission, date, or object for this agency.",
        ["cand-2640", candidate_id], relation=True,
    )
add_statement(
    "st-chp13-p346-haskell-characterizes-venetian-art-world", 176, 176,
    "cand-2719", None, "authorial_characterization",
    "Haskell characterizes the Venetian art world as flourishing and parasitic.",
    "With Toni as guide we can descend yet another stage into the flourishing and parasitic art world of Venice",
    "This preserves Haskell's evaluative language as authorial interpretation rather than a neutral measured description.",
    ["cand-2640", "cand-2719"], speaker="Haskell", layer="authorial interpretation",
)
add_statement(
    "st-chp13-p346-toni-would-buy-prints-from-pasquetti", 176, 176,
    "cand-2640", "cand-1853", "would_buy_prints_from",
    "Haskell says that Toni would go to a stall in the Merceria and buy prints from Leonardo Pasquetti.",
    "follow him to a stall in the Merceria where he would go and buy prints from the hunchback Leonardo Pasquetti.",
    "The source uses habitual/illustrative 'would'; it does not identify a dated purchase, individual print, count, or exact stall. The named Merceria place candidate is unresolved at site level.",
    ["cand-2640", "cand-1853", new_candidate_id], relation=True,
)

coverage_by_id[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L173-177",
    "note": "Printed p.346 was checked against CHP-13.pdf physical page 19. Closed p.345's Toni dealer/agent sentence across the page break; recorded the named collectors with identity limits, Haskell's evaluative description of Venice, and the habitual print-buying narrative involving Leonardo Pasquetti and the unresolved Merceria site. The final anonymity/silence phrase is treated as rhetorical transition, not a separate entity claim. No page-specific footnotes occur here.",
})
coverage_by_id[P345_SEGMENT]["note"] = "Printed p.345 was checked against CHP-13.pdf physical page 18. The p.344 quotation closes at L162 and is cross-linked; the Toni dealer/agent sentence now closes at p.346 L174-175. Printed notes 1-3 map to consolidated L249-L251 and remain pending, so this segment remains partial. S2-only OCR corrections: L164 Varíe→Varie and Use→life; L166 112?→112 with printed note marker 1. No changes to canonical OCR."

candidate_rows = candidates + [new_candidate]
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
print(f"candidates +1; mentions +{len(new_mentions)}; statements +{len(new_statements)}; p.346 coverage reviewed/complete")
print("p.345 coverage remains partial for consolidated printed notes 1-3")
if not args.apply:
    print("dry-run only; pass --apply to write")
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = Path(str(path) + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage)
print("applied; recovery backups saved for candidate, mention, statement, and coverage tables")
