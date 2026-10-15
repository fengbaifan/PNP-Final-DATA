"""Classify p.214 S2 statements, resolve the p.213 link, and repair mappings."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l120-124"
SEGMENT_SHA = "021c88a32fcf270e3b3425913361730c08754daaaf5edaeddef950e5ef1d71c7"
BACKUP_SUFFIX = ".bak-s2-chp8-p214-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "21dd045d7092ba19345a689228b648ebbe723f400f19bebe61d4edd9261d7a90",
    CANDIDATES: "2c6b34b884d3a6dcacc70d99fc8d669ffdd4d65f01822140bf0dfac4374f0071",
    MENTIONS: "dbf7ad838bf902d4f00cc58506c009309b462d2b4aa5c45953dbbb23590465cb",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
}
NEW_CANDIDATE = (
    "cand-12054",
    "Unidentified Mattia Preti pictures in the Baglioni collection",
    "work",
    "Haskell says the Baglioni owned pictures by Mattia Preti; no title or count is supplied for this group in the passage.",
    123,
)
NEW_MENTION_ID = "m-chp8-p214-040"
NEW_STATEMENT_IDS = {
    "st-chp8-p214-baglioni-interest-in-neapolitan-art",
    "st-chp8-p214-baglioni-preti-pictures",
    "st-chp8-p214-influence-on-young-tiepolo",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preconditions and dry-run checks pass")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED_HASHES:
        raise SystemExit("a table, source, or page image changed since the p.214 review baseline")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[119:124])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("p.214 S0 segment changed since review")
    segment_rows = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    segment = segment_rows.get(SEGMENT_ID)
    if not segment or (
        segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
        segment.get("sha256"), segment.get("asset_sha256"),
    ) != (SOURCE_REL, 120, 124, SEGMENT_SHA, EXPECTED_HASHES[SOURCE]):
        raise SystemExit("p.214 segment manifest does not match the reviewed source")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_statement = {row["statement_id"]: row for row in statements}
    by_candidate = {row["candidate_id"]: row for row in candidates}
    by_mention = {row["mention_id"]: row for row in mentions}
    if len(by_statement) != len(statements) or len(by_candidate) != len(candidates) or len(by_mention) != len(mentions):
        raise SystemExit("statement, candidate, or mention identifiers are not unique")

    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {row["statement_id"] for row in page_rows if "relation_candidate" not in (row.get("qualifiers") or {})}
    if len(page_rows) != 7 or unset != {row["statement_id"] for row in page_rows}:
        raise SystemExit(f"unexpected p.214 inventory: rows={len(page_rows)}, unset={len(unset)}")
    if NEW_STATEMENT_IDS & set(by_statement) or NEW_MENTION_ID in by_mention:
        raise SystemExit("a planned p.214 identifier already exists")
    if NEW_CANDIDATE[0] in by_candidate or max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12053:
        raise SystemExit("candidate sequence changed since the reviewed p.214 baseline")

    durazzo_open = by_statement.get("st-chp8-p213-durazzo-local-collection-and-bologna-open")
    if not durazzo_open or durazzo_open.get("qualifiers", {}).get("continuation_statement_id") != "st-chp8-p214-durazzo-naples-continuation":
        raise SystemExit("the p.213 Durazzo sentence no longer links to p.214")
    four_canvas_group = by_candidate.get("cand-7573")
    if not four_canvas_group or not four_canvas_group["canonical_name"].startswith("Four Luca Giordano canvases"):
        raise SystemExit("the p.214 Giordano canvas group changed since review")
    if by_mention.get("m-chp8-p214-029", {}).get("surface_form") != "Preti" or by_mention.get("m-chp8-p214-029", {}).get("candidate_id") != "cand-2056":
        raise SystemExit("the Mattia Preti person mention changed since review")

    candidates.append({
        "candidate_id": NEW_CANDIDATE[0], "index_entry_id": "", "canonical_name": NEW_CANDIDATE[1],
        "index_page_range": "", "suggested_type": NEW_CANDIDATE[2], "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": NEW_CANDIDATE[3], "exclude_reason": "",
        "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L{NEW_CANDIDATE[4]}",
    })
    four_canvas_group["detail"] = (
        "Haskell identifies four canvases Giordano painted for Girolamo Durazzo's family and names their subjects. "
        "This is distinct from the unidentified pictures Durazzo obtained from Bologna and Naples; no item-level acquisition route is supplied."
    )
    four_canvas_group["candidate_source_ref"] = f"{SEGMENT_ID}#L121"

    phrase = "pictures by Mattia\nPreti"
    start = segment_text.find(phrase)
    if start < 0 or segment_text.find(phrase, start + 1) >= 0:
        raise SystemExit("the p.214 Preti-pictures phrase is missing or repeated")
    end = start + len(phrase)
    if segment_text[start:end] != phrase:
        raise SystemExit("new p.214 Preti work-group mention does not match source offsets")
    for row in mentions:
        if row["segment_id"] != SEGMENT_ID:
            continue
        other_start, other_end = int(row["start_char"]), int(row["end_char"])
        overlaps = start < other_end and end > other_start
        if overlaps and row["mention_id"] not in {"m-chp8-p214-028", "m-chp8-p214-029"}:
            contained = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if not contained:
                raise SystemExit(f"new Preti work-group mention overlaps {row['mention_id']} without nesting")
    mentions.append({
        "mention_id": NEW_MENTION_ID, "segment_id": SEGMENT_ID, "candidate_id": NEW_CANDIDATE[0],
        "surface_form": phrase, "start_char": str(start), "end_char": str(end),
        "note": "Unidentified works by Mattia Preti owned by the Baglioni; nested around the separate artist mentions.",
    })

    def excerpt(first: str, last: str) -> str:
        start_at, end_at = segment_text.find(first), segment_text.rfind(last)
        if start_at < 0 or end_at < start_at:
            raise SystemExit(f"expected p.214 source excerpt missing: {first!r} ... {last!r}")
        return segment_text[start_at:end_at + len(last)]

    def update(statement_id: str, relation: bool, note: str, **changes) -> None:
        row = by_statement[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        qualifier_changes = changes.pop("qualifier_changes", {})
        for key, value in qualifier_changes.items():
            if value is None:
                q.pop(key, None)
            else:
                q[key] = value
        q.update(changes.pop("qualifiers", {}))
        row["qualifiers"] = q
        row.update(changes)

    def make_statement(statement_id: str, predicate: str, subject: str | None, obj: str | None,
                       claim: str, quote: str, start_line: int, end_line: int, mentioned: list[str],
                       relation: bool, note: str, qualification: str, **extra) -> dict:
        q = {
            "source_line_start": start_line, "source_line_end": end_line,
            "printed_page": 214, "pdf_physical_page": 12, "claim": claim,
            "speaker": "Haskell", "text_layer": "body", "qualification": qualification,
            "mentioned_candidate_ids": mentioned, "relation_candidate": relation,
            "relation_candidate_note": note,
        }
        q.update(extra)
        return {
            "statement_id": statement_id, "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": q, "original_quote": quote,
            "origin": "book", "source_file": SOURCE_REL,
        }

    update(
        "st-chp8-p214-baglioni-family-publishers-and-nobility", True,
        "Haskell describes the Venice Baglioni as a family of rich publishers who entered the nobility early in the eighteenth century; the idiom 'bought their way' is retained as his wording, not parsed as a specific transaction.",
        predicate="baglioni_family_of_rich_publishers_entered_venetian_nobility_early_eighteenth_century",
        qualification="No individual family member, exact ennoblement date, or independent record is supplied. Keep this Venice family distinct from the Perugia Baglioni candidate pending S3 alignment.",
        mentioned_candidate_ids=["cand-7575", "cand-2719"],
    )
    update(
        "st-chp8-p214-baglioni-neapolitan-holdings", True,
        "The statement is narrowed to the Baglioni's reported holdings by Giordano and Solimena; their interest in Neapolitan art and the Preti pictures are separate statements.",
        predicate="baglioni_family_owned_giordano_and_solimena_pictures",
        object_candidate_id="cand-7576",
        claim="Haskell says the Baglioni owned several pictures by Luca Giordano and two by Francesco Solimena, including Jacob and Rebecca and Rebecca and Eliezer.",
        original_quote=excerpt("they owned several by Luca Giordano", "Rebecca and Eliezer"),
        qualification="The number of Giordano pictures and their titles are not supplied. The two Solimena title candidates remain distinct; the printed reading 'Barach' in the separate Durazzo passage is unresolved against the index.",
        mentioned_candidate_ids=["cand-7575", "cand-7576", "cand-1172", "cand-2484", "cand-2487", "cand-2491"],
    )
    update(
        "st-chp8-p214-baglioni-pictures-in-collection", True,
        "The statement is assigned to the group of Giordano and Solimena pictures and the Baglioni collection that held them; the collection is explicitly located in Venice outside Naples.",
        predicate="giordano_and_solimena_pictures_hung_together_in_baglioni_collection",
        subject_candidate_id="cand-7576", object_candidate_id="cand-0159",
    )
    update(
        "st-chp8-p214-durazzo-naples-continuation", True,
        "This p.214 clause completes the p.213 statement: Durazzo turned to Bologna and also to Naples for many pictures. Keep this source group distinct from the four Giordano canvases named next.",
        predicate="girolamo_durazzo_obtained_many_pictures_from_bologna_and_naples",
        object_candidate_id="cand-12053",
        qualification="The p.213 sentence begins the Bologna route and p.214 adds Naples. Counts, titles and item-level routes are not given; the acquisition route of the four canvases is not specified.",
        mentioned_candidate_ids=["cand-0953", "cand-12053", "cand-0381", "cand-3534", "cand-7360"],
        qualifier_changes={
            "continues_statement_id": "st-chp8-p213-durazzo-local-collection-and-bologna-open",
        },
    )
    update(
        "st-chp8-p214-giordano-four-canvases-for-durazzo", True,
        "Haskell explicitly says Giordano painted four canvases for Girolamo Durazzo's family; the four source-described works remain grouped and their acquisition route is not inferred.",
        predicate="luca_giordano_painted_four_canvases_for_durazzo_family",
    )
    update(
        "st-chp8-p214-influence-on-pittoni-and-tiepolo", True,
        "The sentence names Pittoni and the young Tiepolo as recipients of considerable influence; the ambiguous 'whose' antecedent remains the source-described Baglioni picture group and is not narrowed to individual titles.",
        predicate="baglioni_collection_pictures_influenced_pittoni",
        subject_candidate_id="cand-7576", object_candidate_id="cand-1950",
        claim="Haskell says the preceding Baglioni picture group had considerable influence on Pittoni.",
        original_quote=excerpt("whose influence on Pittoni", "Pittoni"),
        qualification="The antecedent of 'whose' may be the two Solimena pictures or the broader group of Giordano and Solimena holdings; Haskell names Pittoni as one recipient.",
        mentioned_candidate_ids=["cand-7576", "cand-1950"],
    )
    update(
        "st-chp8-p214-solimena-two-histories", True,
        "Haskell reports two further large Old Testament history paintings by Solimena around 1704 in the continuing Durazzo collection account; retain the approximate date and printed title spelling.",
    )

    # Link the p.213 and p.214 halves of the Durazzo acquisition sentence in both directions.
    p213_q = dict(durazzo_open["qualifiers"])
    p213_q["continuation_status"] = "closed"
    p213_q["continuation_statement_id"] = "st-chp8-p214-durazzo-naples-continuation"
    p213_q["continuation_resolution"] = "p.214 L121 adds Naples after p.213's Bologna phrase; both clauses refer to the unidentified picture group cand-12053."
    durazzo_open["qualifiers"] = p213_q
    for statement_id, relation, note, quote, mentioned, subject, obj, qualification in [
        (
            "st-chp8-p214-baglioni-interest-in-neapolitan-art", True,
            "This records Haskell's explicit attribution of interest in Neapolitan art to the Venice Baglioni family, distinct from the inventory of specific pictures.",
            excerpt("They showed a great interest in Neapolitan art", "Neapolitan art"),
            ["cand-7575", "cand-7577"], "cand-7575", "cand-7577",
            "The passage gives a source-specific description of interest; it does not establish that every work held by the family was Neapolitan.",
        ),
        (
            "st-chp8-p214-baglioni-preti-pictures", True,
            "Haskell says the Baglioni owned an unspecified group of pictures by Mattia Preti; the artist and the works are kept as distinct candidates.",
            excerpt("besides pictures by Mattia", "Preti"),
            ["cand-7575", NEW_CANDIDATE[0], "cand-2056"], "cand-7575", NEW_CANDIDATE[0],
            "No titles or count are given for the Preti pictures in this passage.",
        ),
        (
            "st-chp8-p214-influence-on-young-tiepolo", True,
            "Haskell also names the young Tiepolo as a recipient of the considerable influence; the antecedent remains the unresolved source-described picture group.",
            excerpt("whose influence on Pittoni and the young Tiepolo", "young Tiepolo"),
            ["cand-7576", "cand-2569"], "cand-7576", "cand-2569",
            "The text does not resolve whether the two Solimena pictures or the broader Baglioni group is the antecedent of 'whose'.",
        ),
    ]:
        if statement_id == "st-chp8-p214-influence-on-young-tiepolo":
            predicate = "baglioni_collection_pictures_influenced_young_tiepolo"
            start_line, end_line = 124, 124
        elif statement_id == "st-chp8-p214-baglioni-interest-in-neapolitan-art":
            predicate = "baglioni_family_showed_interest_in_neapolitan_art"
            start_line, end_line = 123, 123
        else:
            predicate = "baglioni_family_owned_unidentified_mattia_preti_pictures"
            start_line, end_line = 123, 124
        statements.append(make_statement(
            statement_id, predicate, subject, obj,
            (
                "Haskell says the Baglioni showed great interest in Neapolitan art."
                if statement_id == "st-chp8-p214-baglioni-interest-in-neapolitan-art"
                else "Haskell says the Baglioni owned pictures by Mattia Preti."
                if statement_id == "st-chp8-p214-baglioni-preti-pictures"
                else "Haskell says the preceding Baglioni picture group had considerable influence on the young Tiepolo."
            ),
            quote, start_line, end_line, mentioned, relation, note, qualification,
        ))

    p213_q = durazzo_open["qualifiers"]
    if p213_q.get("continuation_statement_id") != "st-chp8-p214-durazzo-naples-continuation":
        raise SystemExit("the completed p.213 continuation link is inconsistent")
    p214_durazzo = by_statement["st-chp8-p214-durazzo-naples-continuation"]
    if p214_durazzo["qualifiers"].get("continues_statement_id") != "st-chp8-p213-durazzo-local-collection-and-bologna-open":
        raise SystemExit("the p.214 continuation pointer was not written")
    changed_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(changed_rows) != 10 or any("relation_candidate" not in row.get("qualifiers", {}) for row in changed_rows):
        raise SystemExit("the updated p.214 statement inventory is incomplete")
    all_candidate_ids = {row["candidate_id"] for row in candidates}
    bad_refs = []
    for row in changed_rows:
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id"),
                             *(row.get("qualifiers", {}).get("mentioned_candidate_ids") or [])):
            if candidate_id and candidate_id not in all_candidate_ids:
                bad_refs.append((row["statement_id"], candidate_id))
    if bad_refs:
        raise SystemExit(f"p.214 statements refer to absent candidates: {bad_refs}")

    outputs = {
        STATEMENTS: jsonl_bytes(statements),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions),
    }
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    print("p.214 statements:", len(page_rows), "->", len(changed_rows),
          "relation candidates:", sum(bool(row["qualifiers"]["relation_candidate"]) for row in changed_rows))
    print("added candidate:", NEW_CANDIDATE[0], NEW_CANDIDATE[1])
    print("added mention:", NEW_MENTION_ID, repr(phrase), "offsets", start, end)
    print("added statements:", ", ".join(sorted(NEW_STATEMENT_IDS)))
    for path, data in outputs.items():
        print(path.name, "sha256:", sha(data))
    if args.apply:
        backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
        if any(path.exists() for path in backups.values()):
            raise SystemExit("a p.214 recovery copy already exists; inspect it before applying")
        for path, backup in backups.items():
            shutil.copy2(path, backup)
        for path, data in outputs.items():
            atomic_write(path, data)
        print("recovery copies:", ", ".join(path.name for path in backups.values()))


if __name__ == "__main__":
    main()
