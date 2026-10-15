from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p332_page_review_20261014.png"
SEGMENT = "chp-13:13_CHP-13_intro:l3-12"
BACKUP_SUFFIX = ".bak-s2-chp13-p332-semantic-review-20261014"

EXPECTED_HASHES = {
    CANDIDATES.name: "b16fae8cb66538313c1d51e3e36c5db6ac3245166a1353f87c811438da9f9ecf",
    MENTIONS.name: "8aae995f4cd39ed9ce086cb3583657c574539ef9daa1f82ab59cb0f28d6187e9",
    STATEMENTS.name: "e3304c0c27c05d8048d0ff65e3e59d8f3e2c1476935f72a02e5ccb4dd0eddf0c",
    SOURCE.name: "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    PDF.name: "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc",
    IMAGE.name: "9a28de10454d9ef07041bd00c9c49ebf55355803787c193b0295f3f81b812dbf",
}

TARGET_IDS = {
    "st-chp13-p332-artists-labour-on-book-illustration",
    "st-chp13-p332-book-illustration-market-format-limits",
    "st-chp13-p332-bookshops-cultural-contact",
    "st-chp13-p332-carlevarijs-le-fabriche-1703-example",
    "st-chp13-p332-conditional-lax-censorship",
    "st-chp13-p332-copyright-effects-on-local-and-export-books",
    "st-chp13-p332-government-copyright-encouragement",
    "st-chp13-p332-gran-teatro-designed-for-travellers",
    "st-chp13-p332-gran-teatro-includes-tiepolo-pictures",
    "st-chp13-p332-grosley-venice-paris-publication-permission-report",
    "st-chp13-p332-lax-censorship-and-international-book-market",
    "st-chp13-p332-le-fabriche-designed-for-travellers",
    "st-chp13-p332-lovisa-gran-teatro-publication-and-illustrations",
    "st-chp13-p332-marieschi-views-appealed-to-fragonard",
    "st-chp13-p332-marieschi-views-designed-for-travellers",
    "st-chp13-p332-publishers-european-ties-and-patronage",
    "st-chp13-p332-publishers-export-illustrated-books",
    "st-chp13-p332-publishing-role-in-venetian-economy",
    "st-chp13-p332-republic-efforts-to-maintain-publishing-supremacy",
    "st-chp13-p332-travellers-created-demand-for-engraving",
}

UNSET_IDS = {
    "st-chp13-p332-artists-labour-on-book-illustration",
    "st-chp13-p332-book-illustration-market-format-limits",
    "st-chp13-p332-bookshops-cultural-contact",
    "st-chp13-p332-conditional-lax-censorship",
    "st-chp13-p332-copyright-effects-on-local-and-export-books",
    "st-chp13-p332-gran-teatro-designed-for-travellers",
    "st-chp13-p332-grosley-venice-paris-publication-permission-report",
    "st-chp13-p332-lax-censorship-and-international-book-market",
    "st-chp13-p332-le-fabriche-designed-for-travellers",
    "st-chp13-p332-marieschi-views-designed-for-travellers",
    "st-chp13-p332-publishers-european-ties-and-patronage",
    "st-chp13-p332-publishers-export-illustrated-books",
    "st-chp13-p332-publishing-role-in-venetian-economy",
    "st-chp13-p332-republic-efforts-to-maintain-publishing-supremacy",
    "st-chp13-p332-travellers-created-demand-for-engraving",
}

TRUE_IDS = {
    "st-chp13-p332-carlevarijs-le-fabriche-1703-example",
    "st-chp13-p332-government-copyright-encouragement",
    "st-chp13-p332-gran-teatro-designed-for-travellers",
    "st-chp13-p332-gran-teatro-includes-tiepolo-pictures",
    "st-chp13-p332-le-fabriche-designed-for-travellers",
    "st-chp13-p332-lovisa-gran-teatro-publication-and-illustrations",
    "st-chp13-p332-marieschi-views-appealed-to-fragonard",
    "st-chp13-p332-marieschi-views-designed-for-travellers",
}

FALSE_NOTES = {
    "st-chp13-p332-artists-labour-on-book-illustration": "This is a broad historical generalization; no individual artist or identified work is an endpoint.",
    "st-chp13-p332-book-illustration-market-format-limits": "This is Haskell's comparative assessment of market, scale, and technique, not a relation between identified entities.",
    "st-chp13-p332-bookshops-cultural-contact": "The statement concerns bookshops and Venetians as general classes; no specific shop or person is identified for a formal relation.",
    "st-chp13-p332-conditional-lax-censorship": "The sentence states a condition under which censorship was lax; it does not identify the actor enforcing censorship or assert a government-to-policy relation.",
    "st-chp13-p332-copyright-effects-on-local-and-export-books": "This is a broad causal claim about book markets and quality. The publisher-group candidate is not the direct outcome endpoint named in the sentence.",
    "st-chp13-p332-grosley-venice-paris-publication-permission-report": "This records Grosley's attributed comparison of publication permissions in Venice and Paris; it does not establish a historical relation between the traveler and either place.",
    "st-chp13-p332-lax-censorship-and-international-book-market": "This is Haskell's causal interpretation of censorship and a market, without a specific market entity or relation endpoint.",
    "st-chp13-p332-publishers-european-ties-and-patronage": "This combines a broad social characterization and general patronage; no specific European contact, patron, or recipient is identified.",
    "st-chp13-p332-publishers-export-illustrated-books": "The sentence describes a general wish among publishers; no specific book, export market, or actor is identified as an endpoint.",
    "st-chp13-p332-publishing-role-in-venetian-economy": "This is a broad historical characterization of a publishing sector's economic importance, not a specific relation to an identified entity.",
    "st-chp13-p332-republic-efforts-to-maintain-publishing-supremacy": "The sentence is passive and does not identify who made the efforts; no actor or specific policy endpoint is stated.",
    "st-chp13-p332-travellers-created-demand-for-engraving": "This is a general causal claim about travel and demand; the travelers and the engraving market are not identified entities.",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(stream.name)
    temp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(stream.name)
    temp.replace(path)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Semantically review p.332 statements and endpoints")
    parser.add_argument("--apply", action="store_true", help="write after exact preflight; default is preview")
    args = parser.parse_args()

    paths = [CANDIDATES, MENTIONS, STATEMENTS, SOURCE, PDF, IMAGE]
    actual = {path.name: sha(path) for path in paths}
    if actual != EXPECTED_HASHES:
        raise SystemExit(f"preflight hash mismatch; no writes made: {actual}")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    rows = read_jsonl(STATEMENTS)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    by_id = {row["statement_id"]: row for row in rows}
    if len(candidate_by_id) != len(candidates) or len(by_id) != len(rows):
        raise SystemExit("duplicate candidate or statement ID in current tables")
    if len(candidates) != 12096 or len(mentions) != 20100:
        raise SystemExit(f"unexpected current table sizes: candidates={len(candidates)} mentions={len(mentions)}")
    if {r["statement_id"] for r in rows if r.get("segment_id") == SEGMENT} != TARGET_IDS:
        raise SystemExit("p.332 statement set changed; no writes made")
    current_unset = {
        r["statement_id"] for r in rows
        if r.get("segment_id") == SEGMENT and "relation_candidate" not in r.get("qualifiers", {})
    }
    if current_unset != UNSET_IDS:
        raise SystemExit(f"p.332 unset statement set changed: {sorted(current_unset ^ UNSET_IDS)}")
    if not TRUE_IDS <= by_id.keys() or not set(FALSE_NOTES) <= UNSET_IDS:
        raise SystemExit("classification map inconsistent")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if source_lines[2] != "[Page 2]" or not source_lines[11].startswith("’forties,are books like Carlevarijs"):
        raise SystemExit("canonical p.332 source text changed")
    if source_lines[11][315:325] != "travellers":
        raise SystemExit("traveller mention span changed")
    target_rows = [r for r in rows if r.get("segment_id") == SEGMENT]
    for row in target_rows:
        q = row["qualifiers"]
        start, end = q["source_line_start"], q["source_line_end"]
        block = "\n".join(source_lines[start - 1:end])
        if not row.get("original_quote") or row["original_quote"] not in block:
            raise SystemExit(f"source quote mismatch: {row['statement_id']}")

    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidates)
    if max_candidate != 12118 or "cand-12119" in candidate_by_id:
        raise SystemExit(f"unexpected candidate sequence: max={max_candidate}")
    if "m-s2-ch13-p332-036" in mention_ids:
        raise SystemExit("planned audience mention ID already exists")
    for cid, old_name, old_subentry in [
        ("cand-0555", "Carlevarijs, Luca", "Le Fabriche e Vedute di Venetia"),
        ("cand-1453", "Lovisa, Domenico", "Il Gran Teatro delle Pitture e Prospettive di Venezia"),
    ]:
        row = candidate_by_id[cid]
        if (row["canonical_name"], row["sub_entry"]) != (old_name, old_subentry):
            raise SystemExit(f"unexpected indexed work candidate pre-state: {cid}")

    group = {field: "" for field in candidate_fields}
    group.update({
        "candidate_id": "cand-12119",
        "canonical_name": "Travellers as intended readers of illustrated Venetian publications",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-local readership group explicitly named for Le Fabriche e Vedute di Venetia, Il Gran Teatro, and Marieschi's 1741 views on p.332. No individual travellers, national origin, membership, or visit dates are identified; keep distinct from the narrower foreign-traveller groups.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L12",
    })

    candidate_by_id["cand-0555"].update({
        "canonical_name": "Le Fabriche e Vedute di Venetia (1703)",
        "suggested_type": "archive",
        "detail": "Indexed subentry under Luca Carlevarijs, represented here as the cited 1703 illustrated publication. Haskell attributes the title to Carlevarijs by possessive construction; this page does not distinguish design, engraving, printing, or publishing roles.",
    })
    candidate_by_id["cand-1453"].update({
        "canonical_name": "Il Gran Teatro delle Pitture e Prospettive di Venezia (1720)",
        "suggested_type": "archive",
        "detail": "Indexed subentry under Domenico Lovisa, represented here as the 1720 publication. Haskell says Lovisa published it and that it contained drawings and pictures by several artists.",
    })

    new_mention = {
        "mention_id": "m-s2-ch13-p332-036",
        "segment_id": SEGMENT,
        "candidate_id": "cand-12119",
        "surface_form": "travellers",
        "start_char": "2055",
        "end_char": "2065",
        "note": "Unspecified readership group introduced for the two named publications; Marieschi's views inherit the same audience through ‘as were’.",
    }

    for sid, is_relation in {**{sid: True for sid in TRUE_IDS}, **{sid: False for sid in FALSE_NOTES}}.items():
        row = by_id[sid]
        q = row["qualifiers"]
        q["relation_candidate"] = is_relation
        if sid in FALSE_NOTES:
            q["qualification"] = FALSE_NOTES[sid]

    carlevarijs = by_id["st-chp13-p332-carlevarijs-le-fabriche-1703-example"]
    carlevarijs["subject_candidate_id"] = "cand-0555"
    carlevarijs["predicate"] = "created_by"
    carlevarijs["object_candidate_id"] = "cand-0554"
    carlevarijs["qualifiers"]["qualification"] = "The possessive title associates the publication with Carlevarijs. This candidate records a general creator attribution and does not specify whether he designed, engraved, printed, or published it."

    lovisa = by_id["st-chp13-p332-lovisa-gran-teatro-publication-and-illustrations"]
    lovisa["subject_candidate_id"] = "cand-1453"
    lovisa["predicate"] = "published_by"
    lovisa["object_candidate_id"] = "cand-1452"
    lovisa["qualifiers"]["time"] = "1720"
    lovisa["qualifiers"]["qualification"] = "Haskell explicitly identifies Domenico Lovisa as publisher in 1720; the adjacent illustration details remain in the claim, without a complete list of artists."

    tiepolo = by_id["st-chp13-p332-gran-teatro-includes-tiepolo-pictures"]
    tiepolo["predicate"] = "illustrated_by"
    tiepolo["qualifiers"]["qualification"] = "Haskell includes the young Tiepolo among several artists whose pictures appeared in the publication; no individual picture or plate is identified."

    for sid in [
        "st-chp13-p332-le-fabriche-designed-for-travellers",
        "st-chp13-p332-gran-teatro-designed-for-travellers",
        "st-chp13-p332-marieschi-views-designed-for-travellers",
    ]:
        row = by_id[sid]
        row["predicate"] = "intended_for"
        row["object_candidate_id"] = "cand-12119"
        q = row["qualifiers"]
        q["relation_candidate"] = True
        if "cand-12119" not in q.get("mentioned_candidate_ids", []):
            q.setdefault("mentioned_candidate_ids", []).append("cand-12119")
        q["qualification"] = "The source says the two publications were designed for travellers and applies the same intended audience to Marieschi's views by anaphoric continuation; no individual traveller is identified."

    for row in rows:
        q = row.get("qualifiers", {})
        if row.get("segment_id") == SEGMENT and row["statement_id"] in TRUE_IDS:
            for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
                if endpoint and endpoint not in candidate_by_id and endpoint != "cand-12119":
                    raise SystemExit(f"unknown endpoint after review: {row['statement_id']} -> {endpoint}")

    candidates = list(candidate_by_id.values()) + [group]
    mentions.append(new_mention)
    after_target = [r for r in rows if r.get("segment_id") == SEGMENT]
    counts = {
        "true": sum(r["qualifiers"].get("relation_candidate") is True for r in after_target),
        "false": sum(r["qualifiers"].get("relation_candidate") is False for r in after_target),
        "unset": sum("relation_candidate" not in r["qualifiers"] for r in after_target),
    }
    if counts != {"true": 8, "false": 12, "unset": 0}:
        raise SystemExit(f"unexpected p.332 classification totals: {counts}")

    candidate_output = sorted(candidates, key=lambda row: row["candidate_id"])
    mention_output = sorted(mentions, key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
    statement_output = rows
    # Use csv serialization for canonical quoting and stable LF line endings.
    def csv_bytes(fields, items):
        import io
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(items)
        return stream.getvalue().encode("utf-8")

    output_bytes = {
        CANDIDATES: csv_bytes(candidate_fields, candidate_output),
        MENTIONS: csv_bytes(mention_fields, mention_output),
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statement_output) + "\n").encode("utf-8"),
    }
    print("p.332 source: CHP-13.pdf physical page 1; page image and source hash preflight passed.")
    print("Candidate repair: c0555 and c1453 now name their indexed publications; no index provenance is removed.")
    print("Added one open readership term and one exact mention; three intended_for relations now have the shared source-defined audience endpoint.")
    print(f"p.332 statements: {len(after_target)}; relation_candidate true/false/unset: {counts['true']}/{counts['false']}/{counts['unset']}.")
    for path, data in output_bytes.items():
        print(f"planned {path.name} sha256: {hashlib.sha256(data).hexdigest()}")
    if not args.apply:
        print("preview only; no files written")
        return 0

    destinations = [CANDIDATES, MENTIONS, STATEMENTS]
    for path in destinations:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
    for path in destinations:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    for path, data in output_bytes.items():
        path.write_bytes(data)
    print("applied; recovery copies created with suffix", BACKUP_SUFFIX)
    for path in destinations:
        print(f"written {path.name} sha256: {sha(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
