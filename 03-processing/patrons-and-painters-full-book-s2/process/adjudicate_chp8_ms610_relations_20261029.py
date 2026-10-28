from __future__ import annotations

import argparse
import csv
import json
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
RELATION_TYPES = ROOT / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml"
DOMAIN_RANGE = ROOT / "01-domain" / "relation-domain-range.yml"
SOURCE_FILE = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE_ID = "haskell-1980-rev-ed"
STATEMENT_ID = "st-chp8-p222-n1-manuscript-source"
REPOSITORY_STATEMENT_ID = "st-chp8-p222-n1-manuscript-repository"
BOOK_KU = "units/archives/patrons-and-painters"
MANUSCRIPT_KU = "units/archives/antonelli-ms-610-ferrara-episcopal-palace-gallery-manuscript"
LIBRARY_KU = "units/institutions/biblioteca-ariostea-ferrara"
SOURCE_SPAN = "第8章印刷页222注1；PDF物理页24；OCR L382"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


relations_path = TABLES / "relations.csv"
relation_fields, relations = read_csv(relations_path)
manifest_fields, manifest = read_csv(TABLES / "ku-manifest.csv")
source_fields, sources = read_csv(TABLES / "sources.csv")
manifest_ids = {row["ku_id"] for row in manifest}
source_ids = {row["source_id"] for row in sources}
if not {BOOK_KU, MANUSCRIPT_KU, LIBRARY_KU} <= manifest_ids:
    raise SystemExit("S4 endpoint registration is incomplete")
if SOURCE_ID not in source_ids:
    raise SystemExit(f"missing evidence source: {SOURCE_ID}")

statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
statement = next((row for row in statements if row["statement_id"] == STATEMENT_ID), None)
if statement is None or statement["subject_candidate_id"] != "cand-2962" or statement["object_candidate_id"] != "cand-7711":
    raise SystemExit("manuscript source statement changed since semantic review")
if not statement["qualifiers"].get("relation_candidate"):
    raise SystemExit("source-use statement is no longer an S2 relation candidate")
if "cand-7712" not in statement["qualifiers"].get("mentioned_candidate_ids", []):
    raise SystemExit("S2 source statement no longer records Biblioteca Ariostea as a mentioned endpoint")
repository_statement = next((row for row in statements if row["statement_id"] == REPOSITORY_STATEMENT_ID), None)
if (
    repository_statement is None
    or repository_statement["subject_candidate_id"] != "cand-7711"
    or repository_statement["object_candidate_id"] != "cand-7712"
    or not repository_statement["qualifiers"].get("relation_candidate")
):
    raise SystemExit("separate manuscript repository relation candidate is missing")
mentions = [
    row for row in csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline=""))
]
if not any(row["mention_id"] == "m-chp8-p222-n1-ariostea" and row["candidate_id"] == "cand-7712" for row in mentions):
    raise SystemExit("restored Biblioteca Ariostea mention is missing")

types = yaml.safe_load(RELATION_TYPES.read_text(encoding="utf-8"))
domain_range = yaml.safe_load(DOMAIN_RANGE.read_text(encoding="utf-8"))["domain_range"]
drafts = [
    {
        "subject_ku_id": BOOK_KU,
        "object_ku_id": MANUSCRIPT_KU,
        "predicate": "derived_from",
        "time": "",
        "role": "据述来源手稿",
        "scope": "仅限第8章关于费拉拉大主教宫及画廊的叙述；不表示全书由该手稿编写。",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": SOURCE_SPAN + f'；S2={STATEMENT_ID}；“This account ... is taken from”',
        "source_file": SOURCE_FILE,
        "note": "对应S2候选 st-chp8-p222-n1-manuscript-source。Haskell将该段宫殿叙述明确归于MS. 610；手稿及其内容未独立查阅。",
    },
    {
        "subject_ku_id": MANUSCRIPT_KU,
        "object_ku_id": LIBRARY_KU,
        "predicate": "located_at",
        "time": "",
        "role": "Haskell所报手稿地点",
        "scope": "Haskell称MS. 610为“a manuscript in the Biblioteca Ariostea, Ferrara”；不主张当前保管状态。",
        "origin": "book",
        "status": "pending",
        "source_id": SOURCE_ID,
        "source_span": SOURCE_SPAN + f'；S2={REPOSITORY_STATEMENT_ID}；“It is a manuscript in the Biblioteca Ariostea, Ferrara”',
        "source_file": SOURCE_FILE,
        "note": "对应S2候选 st-chp8-p222-n1-manuscript-repository。原文支持来源所报的机构地点，但S6词表将located_at标记为needs_split，且held_by的domain不含archive；在保管/位置语义有可用的忠实谓词前保持pending，不升为formal。",
    },
]

for row in drafts:
    if row["predicate"] not in types["types"]:
        raise SystemExit(f"uncontrolled relation type: {row['predicate']}")
    constraint = domain_range.get(row["predicate"])
    if constraint and (
        row["subject_ku_id"].split("/", 2)[1].rstrip("s") not in constraint["domain"]
        or row["object_ku_id"].split("/", 2)[1].rstrip("s") not in constraint["range"]
    ):
        raise SystemExit(f"domain/range mismatch: {row['predicate']} {row['subject_ku_id']} -> {row['object_ku_id']}")

def natural_key(row):
    return tuple(row.get(k, "") for k in ("subject_ku_id", "predicate", "object_ku_id", "time", "role", "scope"))


existing_keys = {natural_key(row) for row in relations}
for row in drafts:
    if natural_key(row) in existing_keys:
        raise SystemExit(f"duplicate relation natural key: {natural_key(row)}")
    existing_keys.add(natural_key(row))

def next_relation_number(rows):
    return max((int(row["relation_id"].removeprefix("rel-")) for row in rows), default=0) + 1


next_id = next_relation_number(relations)
for offset, row in enumerate(drafts):
    row["relation_id"] = f"rel-{next_id + offset:04d}"

preview = {"mode": "dry-run", "source_statement": STATEMENT_ID, "decisions": drafts}
parser = argparse.ArgumentParser(description="Adjudicate the source-use and repository-location relationships for MS. 610.")
parser.add_argument("--apply", action="store_true", help="apply the reviewed S6 decisions")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

relations.extend(drafts)
write_csv_atomic(relations_path, relation_fields, relations)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
