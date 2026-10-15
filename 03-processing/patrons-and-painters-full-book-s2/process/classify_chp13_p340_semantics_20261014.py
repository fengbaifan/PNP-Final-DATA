#!/usr/bin/env python3
"""Review p.340 S2 statements, endpoints, and mentions; dry-run by default."""

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
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l79-88"
SEGMENT_SHA256 = "661b04d02c9cbf2feda5e28e972bcb16c5375d173d775de71709151c87e2d073"
PRE_HASHES = {
    STATEMENTS.name: "b5f5093a83e089d128c363f39f2fac48a8175f45c03af4be7b5e773d884b802e",
    CANDIDATES.name: "80bdfc0b187f1890268f11384bf45325a9b49f31dc9e2c1450c624d001e7adc4",
    MENTIONS.name: "f1ade53623bab8632c3afa3f41af66366bf7786559d1b548fb433a73ca93aba1",
}
BACKUP_SUFFIX = ".bak-s2-ch13-p340-semantic-review-20261014"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_atomic(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def csv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    with tempfile.SpooledTemporaryFile(
        mode="w+", encoding="utf-8-sig", newline="", max_size=8 * 1024 * 1024
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        stream.seek(0)
        return stream.read().encode("utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks")
    args = parser.parse_args()

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = digest(path)
        expected = PRE_HASHES[path.name]
        if actual != expected:
            raise SystemExit(f"preflight failed: {path.name} SHA-256 {actual} != {expected}")
    segment = next(
        (row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID),
        None,
    )
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.340 segment identity/hash changed")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("preflight failed: duplicate statement_id")
    local = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(local) != 41:
        raise SystemExit(f"preflight failed: expected 41 p.340 statements, found {len(local)}")
    decisions = {
        "st-chp13-p340-canaletto-drawings-depicted-principal-ducale-ceremonies": True,
        "st-chp13-p340-furnaletto-established-over-thirty-years-at-ponte-de-baretteri": True,
        "st-chp13-p340-furnaletto-print-dealer-not-claiming-to-practise-art": False,
        "st-chp13-p340-pinelli-born-and-known-for-learning": False,
        "st-chp13-p340-pinelli-collection-attributed-old-master-pictures": True,
        "st-chp13-p340-pinelli-collection-contemporary-artists-tiepolo-count": True,
        "st-chp13-p340-pinelli-collection-dispersal-distressed-contemporaries": True,
        "st-chp13-p340-pinelli-collection-suggested-historical-approach": True,
        "st-chp13-p340-pinelli-seems-most-interested-in-sixteenth-century-art": True,
        "st-chp13-p340-print-sellers-often-important-art-patrons": False,
        "st-chp13-p340-printed-note-three-rava-citation-tail": False,
        "st-chp13-p340-remondini-served-different-public": True,
        "st-chp13-p340-remondini-expanded-and-acquired-international-clientele": True,
        "st-chp13-p340-remondini-low-priced-facsimiles": True,
        "st-chp13-p340-remondini-sold-devotional-prints-for-peasant-homes": True,
        "st-chp13-p340-remondini-specialised-in-cheap-romantic-novels": True,
        "st-chp13-p340-remondini-most-conspicuous-print-seller": False,
        "st-chp13-p340-viero-printer-opened-shop-1754": True,
        "st-chp13-p340-wagner-german-and-opened-shop-1742": True,
        "st-chp13-p340-wagner-shop-significant-to-printers": True,
    }
    unset = {
        row["statement_id"]
        for row in local
        if row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != set(decisions):
        raise SystemExit(f"preflight failed: unexpected unset IDs: {sorted(unset ^ set(decisions))}")
    for statement_id, value in decisions.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = value

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[78:88])

    def exact_span(surface: str, before: str | None = None, after: str | None = None) -> tuple[int, int]:
        search_start = 0
        if before is not None:
            anchor = segment_text.find(before)
            if anchor < 0:
                raise SystemExit(f"preflight failed: mention anchor missing: {before!r}")
            search_start = anchor + len(before)
        start = segment_text.find(surface, search_start)
        if start < 0:
            raise SystemExit(f"preflight failed: source mention missing: {surface!r}")
        end = start + len(surface)
        if after is not None:
            following = segment_text.find(after, end)
            if following < 0:
                raise SystemExit(f"preflight failed: mention boundary missing after {surface!r}")
        elif segment_text.find(surface, end) >= 0:
            raise SystemExit(f"preflight failed: ambiguous source mention: {surface!r}")
        return start, end

    new_candidates = [
        ("cand-12162", "Dispersal of Maffeo Pinelli’s library and picture collection (1785)", "event",
         "The joint posthumous dispersal of Pinelli’s library and picture collection reported on p.340; distinct from the two holdings themselves.", 82),
        ("cand-12163", "Contemporaries distressed by the dispersal of Pinelli’s collections", "term",
         "Haskell reports distress among unnamed contemporaries; no individuals or boundaries are identified.", 82),
        ("cand-12164", "Joseph Wagner’s unnamed shop opened in 1742", "",
         "A shop Joseph Wagner opened in 1742 and whose significance to printers Haskell describes; type remains open because the source does not separate the commercial establishment from its premises.", 86),
        ("cand-12165", "Printers for whom Wagner’s shop was significant", "term",
         "The source-defined occupational group is unnamed; no individual printers are identified.", 86),
        ("cand-12166", "Teodoro Viero’s unnamed shop opened in 1754", "",
         "A shop Teodoro Viero opened in 1754; type remains open because the source does not separate the commercial establishment from its premises.", 86),
        ("cand-12167", "Remondini print market", "term",
         "The commercial market Haskell distinguishes from the larger enterprises discussed earlier; keep distinct from its international clientele and public.", 84),
        ("cand-12168", "Printers employed by Remondini for reproduction", "term",
         "An unnamed occupational group described as some of the best printers; no individual printer or print is identified.", 85),
        ("cand-12169", "Leading artists employed by Remondini for reproduction", "term",
         "An unnamed group of leading artists employed to produce paintings and drawings for extensive reproduction; no individual commission is supplied here.", 85),
        ("cand-12170", "Artists of Pinelli’s own century represented in his collection", "term",
         "A source-defined group said to be well represented; Tiepolo’s four pictures are separately identified as a narrower group.", 80),
    ]
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        candidate_fields = reader.fieldnames
        candidates = list(reader)
    candidate_ids = {row["candidate_id"] for row in candidates}
    if any(candidate_id in candidate_ids for candidate_id, *_ in new_candidates):
        raise SystemExit("preflight failed: one or more new candidate IDs already exist")
    for candidate_id, name, suggested_type, detail, source_line in new_candidates:
        candidates.append({
            "candidate_id": candidate_id,
            "index_entry_id": "",
            "canonical_name": name,
            "index_page_range": "",
            "suggested_type": suggested_type,
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": detail,
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + f"#L{source_line}",
        })

    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        mention_fields = reader.fieldnames
        mentions = list(reader)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("preflight failed: duplicate mention_id")
    if mention_by_id.get("m-s2-ch13-p340-041", {}).get("candidate_id") != "cand-10056":
        raise SystemExit("preflight failed: market mention m-s2-ch13-p340-041 changed")
    mention_by_id["m-s2-ch13-p340-041"]["candidate_id"] = "cand-12167"
    mention_by_id["m-s2-ch13-p340-041"]["note"] = "The Remondini’s commercial market, distinct from its clientele and the public it served."

    new_mentions = [
        ("m-s2-ch13-p340-073", "cand-12162", "were dispersed", "The joint dispersal event involving Pinelli’s two distinct collections."),
        ("m-s2-ch13-p340-074", "cand-12163", "many contemporaries", "Unnamed contemporaries whom Haskell says the dispersal distressed."),
        ("m-s2-ch13-p340-075", "cand-12164", "a shop", "Wagner’s shop opened in 1742; source does not give its address or name.", "Joseph Wagner, who opened ", " in 1742"),
        ("m-s2-ch13-p340-076", "cand-12164", "which", "Relative reference to Wagner’s shop, described as significant to printers.", " in 1742, ", " was of the utmost significance"),
        ("m-s2-ch13-p340-077", "cand-12165", "printers", "Source-defined occupational group for whom Wagner’s shop was significant.", "significance.to ", ", though"),
        ("m-s2-ch13-p340-078", "cand-12166", "a shop", "Viero’s shop opened in 1754; no name or address is supplied.", "Teodoro Viero, himself a printer, who opened ", " in 1754"),
        ("m-s2-ch13-p340-079", "cand-12166", "to which", "Relative reference to Viero’s shop; Haskell says the same qualified assessment applies.", " in 1754 ", " the same applies"),
        ("m-s2-ch13-p340-080", "cand-12170", "Most of the artists of his own century", "The collective artists whose representation Haskell describes.", "Pictures attributed", " were also well represented"),
        ("m-s2-ch13-p340-081", "cand-12168", "some of the best printers", "Unnamed printers employed by Remondini as its firm grew richer."),
        ("m-s2-ch13-p340-082", "cand-12169", "many leading artists", "Unnamed leading artists employed by Remondini to make works for reproduction."),
        ("m-s2-ch13-p340-083", "cand-2123", "their appearance on the scene", "The pronoun refers to the Remondini firm, whose arrival the institutions greeted with hostility.", "institutions which greeted ", " with bitter hostility"),
    ]
    for entry in new_mentions:
        mention_id, candidate_id, surface, note, *anchors = entry
        if mention_id in mention_by_id:
            raise SystemExit(f"preflight failed: {mention_id} already exists")
        start, end = exact_span(surface, *(anchors or [None, None]))
        row = {
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": segment_text[start:end],
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        }
        mentions.append(row)
        mention_by_id[mention_id] = row

    def revise(statement_id: str, *, subject: str, obj: str | None, predicate: str,
               claim: str, quote: str, qualification: str, mentioned: list[str], relation: bool) -> None:
        row = by_id[statement_id]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = obj
        row["predicate"] = predicate
        row["original_quote"] = quote
        q = row["qualifiers"]
        q["claim"] = claim
        q["qualification"] = qualification
        q["mentioned_candidate_ids"] = mentioned
        q["relation_candidate"] = relation

    def add_statement(statement_id: str, subject: str, obj: str | None, predicate: str,
                      claim: str, quote: str, line: int, qualification: str,
                      mentioned: list[str], relation: bool) -> None:
        if statement_id in by_id:
            raise SystemExit(f"preflight failed: {statement_id} already exists")
        if quote not in segment_text:
            raise SystemExit(f"preflight failed: new statement quote not in S0: {quote!r}")
        row = {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": {
                "source_line_start": line,
                "source_line_end": line,
                "printed_page": 340,
                "pdf_physical_page": 9,
                "claim": claim,
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "qualification": qualification,
                "mentioned_candidate_ids": mentioned,
                "ocr_corrections": [],
                "relation_candidate": relation,
            },
            "original_quote": quote,
            "origin": "book",
            "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        }
        statements.append(row)
        by_id[statement_id] = row

    revise(
        "st-chp13-p340-pinelli-born-and-known-for-learning",
        subject="cand-1932", obj=None, predicate="born_in_1735",
        claim="Haskell says Maffeo Pinelli was born in 1735.",
        quote="He was born in 1735",
        qualification="This is a biographical attribute; the following reputation claim is split into a separate statement.",
        mentioned=["cand-1932"], relation=False,
    )
    add_statement(
        "st-chp13-p340-pinelli-reputation-for-learning", "cand-1932", None,
        "gained_reputation_for_learning", "Haskell says Pinelli soon acquired a great reputation for learning.",
        "soon acquired a great reputation for learning", 80,
        "This is an attributed biographical characterization, not an independently verified educational record.",
        ["cand-1932"], False,
    )

    revise(
        "st-chp13-p340-pinelli-collection-contemporary-artists-tiepolo-count",
        subject="cand-10031", obj="cand-10041", predicate="included_four_tiepolo_pictures",
        claim="Haskell says Pinelli’s picture collection included four pictures by a Tiepolo.",
        quote="Tiepolo with four pictures",
        qualification="The surname Tiepolo remains unresolved; the four pictures are kept separate from the broader group of contemporary artists.",
        mentioned=["cand-10031", "cand-10041", "cand-10037"], relation=True,
    )
    add_statement(
        "st-chp13-p340-pinelli-contemporary-artists-well-represented", "cand-10031", "cand-12170",
        "artists_of_pinellis_own_century_well_represented",
        "Haskell says most artists of Pinelli’s own century were well represented in his picture collection.",
        "Most of the artists of his own century were also well represented", 80,
        "The artists form an unnamed source-defined group; Tiepolo’s four pictures are treated separately.",
        ["cand-10031", "cand-12170"], True,
    )

    revise(
        "st-chp13-p340-pinelli-collection-dispersal-distressed-contemporaries",
        subject="cand-12162", obj="cand-12163", predicate="dispersal_distressed_contemporaries",
        claim="Haskell says the posthumous dispersal of Pinelli’s library and picture collection caused great distress among many contemporaries.",
        quote="After Pinelli’s death in 1785 both his library and picture collection were dispersed, to the great distress of many contemporaries.",
        qualification="The dispersal is represented as a joint event; the two collections remain separate objects. The affected contemporaries are unnamed.",
        mentioned=["cand-1932", "cand-12162", "cand-10030", "cand-10031", "cand-12163"], relation=True,
    )

    revise(
        "st-chp13-p340-remondini-served-different-public",
        subject="cand-12167", obj="cand-10058", predicate="served_a_different_public_from_great_enterprises",
        claim="Haskell says the Remondini print market served a very different public from the large enterprises discussed earlier.",
        quote="On the whole their market was restricted to a very different public from that of the great enterprises that have been discussed so far.",
        qualification="The passage does not identify or quantify that public beyond later mentioning peasants’ houses and an international clientele.",
        mentioned=["cand-2123", "cand-12167", "cand-10058"], relation=True,
    )

    revise(
        "st-chp13-p340-remondini-expanded-and-acquired-international-clientele",
        subject="cand-2123", obj="cand-10056", predicate="acquired_international_clientele",
        claim="Haskell says the Remondini firm began to acquire an international clientele around the middle of the eighteenth century.",
        quote="began to acquire an international clientèle",
        qualification="The source gives an approximate period and no named clients; the firm’s expansion is recorded separately.",
        mentioned=["cand-2123", "cand-10056"], relation=True,
    )
    add_statement(
        "st-chp13-p340-remondini-expanded-around-mid-century", "cand-2123", None,
        "expanded_around_mid_eighteenth_century",
        "Haskell says the Remondini firm greatly expanded towards the middle of the eighteenth century.",
        "they greatly expanded", 85,
        "This is a broad change in the firm’s scale; the international clientele is recorded in a separate statement.",
        ["cand-2123"], False,
    )

    revise(
        "st-chp13-p340-remondini-rivalry-with-established-institutions",
        subject="cand-2123", obj="cand-10057", predicate="entered_rivalry_with_established_publishing_institutions",
        claim="Haskell says the Remondini firm entered into rivalry with more established publishing institutions.",
        quote="This brought them into rivalry with the more established institutions",
        qualification="The institutions remain unnamed; the following clause about their hostile reaction is recorded separately.",
        mentioned=["cand-2123", "cand-10057"], relation=True,
    )
    add_statement(
        "st-chp13-p340-established-institutions-greeted-remondini-with-hostility", "cand-10057", "cand-2123",
        "greeted_remondini_arrival_with_bitter_hostility",
        "Haskell says the established institutions greeted the Remondini firm’s arrival with bitter hostility.",
        "which greeted their appearance on the scene with bitter hostility", 85,
        "The institutions are not named; hostility is Haskell’s characterization.",
        ["cand-10057", "cand-2123"], True,
    )

    revise(
        "st-chp13-p340-remondini-low-priced-facsimiles",
        subject="cand-2123", obj="cand-10049", predicate="produced_low_priced_facsimiles_of_other_publications",
        claim="Haskell says the Remondini produced facsimiles of other publications at much reduced prices.",
        quote="producing facsimiles of other publications at much reduced prices",
        qualification="The production practice is a relation candidate; Haskell’s judgment that the firm had ‘few scruples’ is recorded separately.",
        mentioned=["cand-2123", "cand-10049"], relation=True,
    )
    add_statement(
        "st-chp13-p340-haskell-judged-remondini-facsimile-practice-unscrupulous", "cand-2123", None,
        "criticized_as_having_few_scruples_over_facsimile_production",
        "Haskell characterizes the Remondini as having few scruples about producing facsimiles.",
        "the Remondini had few scruples", 85,
        "This is Haskell’s evaluative judgment, not a neutral property or legal finding.",
        ["cand-2123", "cand-10049"], False,
    )

    revise(
        "st-chp13-p340-remondini-employed-printers-and-artists-for-reproduction",
        subject="cand-2123", obj="cand-12168", predicate="employed_printers_for_reproduction",
        claim="As the firm grew richer, the Remondini could employ some of the best printers.",
        quote="the firm grew richer it was able to employ not only some of the best printers",
        qualification="This clause identifies the printer group; employment of leading artists and their work output is recorded separately.",
        mentioned=["cand-2123", "cand-12168"], relation=True,
    )
    add_statement(
        "st-chp13-p340-remondini-employed-leading-artists-for-reproduction", "cand-2123", "cand-12169",
        "employed_leading_artists_to_produce_reproductive_images",
        "As the firm grew richer, the Remondini could employ many leading artists to produce paintings and drawings for extensive reproduction.",
        "many leading artists to produce paintings and drawings for extensive reproduction", 85,
        "The artists are unnamed; the work group is the output described in the same clause.",
        ["cand-2123", "cand-12169", "cand-10051"], True,
    )

    revise(
        "st-chp13-p340-wagner-german-and-opened-shop-1742",
        subject="cand-2796", obj="cand-12164", predicate="opened_shop_in_1742",
        claim="Haskell says Joseph Wagner opened a shop in 1742.",
        quote="opened a shop in 1742",
        qualification="The shop is a source-defined commercial establishment; its name, address, and taxonomy type remain unresolved.",
        mentioned=["cand-2796", "cand-12164"], relation=True,
    )
    add_statement(
        "st-chp13-p340-wagner-identified-as-german", "cand-2796", None,
        "identified_as_german",
        "Haskell identifies Joseph Wagner as German.",
        "the German Joseph Wagner", 86,
        "This is an attributed biographical description, not a relation to a named German institution or place.",
        ["cand-2796"], False,
    )
    revise(
        "st-chp13-p340-wagner-shop-significant-to-printers",
        subject="cand-12164", obj="cand-12165", predicate="shop_was_of_utmost_significance_to_printers",
        claim="Haskell says Wagner’s shop was of the utmost significance to printers.",
        quote="which was of the utmost significance.to printers",
        qualification="The relative pronoun refers to Wagner’s shop; printers are an unnamed source-defined occupational group. The OCR period before ‘to’ is corrected in S2 only.",
        mentioned=["cand-2796", "cand-12164", "cand-12165"], relation=True,
    )

    revise(
        "st-chp13-p340-viero-printer-opened-shop-1754",
        subject="cand-2773", obj="cand-12166", predicate="opened_shop_in_1754",
        claim="Haskell says Teodoro Viero opened a shop in 1754.",
        quote="who opened a shop in 1754",
        qualification="The shop is a source-defined commercial establishment; its name, address, and taxonomy type remain unresolved.",
        mentioned=["cand-2773", "cand-12166"], relation=True,
    )
    add_statement(
        "st-chp13-p340-viero-identified-as-printer", "cand-2773", None,
        "identified_as_printer", "Haskell identifies Teodoro Viero as a printer.",
        "himself a printer", 86,
        "This is an occupational attribute; the shop opening is recorded separately.",
        ["cand-2773"], False,
    )

    additions = [row for row in statements if row.get("segment_id") == SEGMENT_ID and row["statement_id"] not in {r["statement_id"] for r in local}]
    if len(additions) != 8:
        raise SystemExit(f"preflight failed: expected 8 new statements, found {len(additions)}")
    if any(row["original_quote"] not in segment_text for row in statements if row.get("segment_id") == SEGMENT_ID):
        raise SystemExit("preflight failed: one or more final p.340 quotes do not match S0")

    print(f"segment={SEGMENT_ID}; SHA-256={SEGMENT_SHA256}; original statements={len(local)}; classified={len(decisions)}")
    print("atomization: Pinelli birth/reputation; contemporary artists/Tiepolo; Remondini expansion/clientele, rivalry/hostility, facsimile practice/evaluation, printer/artist groups; Wagner/Viero shop occupation and opening")
    print("endpoint repairs: Pinelli dispersal event and affected contemporaries; Remondini market/public; Wagner and Viero shops; printers and artist groups")
    print(f"new candidates={len(new_candidates)} (cand-12162–cand-12170); new mentions={len(new_mentions)}; new statements={len(additions)}")
    for statement_id, value in decisions.items():
        print(f"  {statement_id}: {value}")
    if not args.apply:
        print("DRY RUN only; no files written. Pass --apply to write after review.")
        return

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False) for row in statements) + "\n").encode("utf-8")
    write_atomic(STATEMENTS, statement_bytes)
    write_atomic(CANDIDATES, csv_bytes(candidate_fields, candidates))
    write_atomic(MENTIONS, csv_bytes(mention_fields, mentions))
    print("APPLIED. Backups saved for statements, candidates, and mentions.")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"  {path.name}: {digest(path)}")


if __name__ == "__main__":
    main()
