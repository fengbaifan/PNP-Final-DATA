"""Classify and normalize the remaining p.203 S2 statements.

Default invocation is a guarded dry run. The original OCR source remains unchanged.
"""
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
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE = ROOT / SOURCE_REL
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l3-12"
INTRO_NOTES_SEGMENT = "chp-8:08_CHP-8_intro:l7-10"
BACKUP_SUFFIX = ".bak-s2-chp8-p203-relations-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "49dcf18acbc985b85b3e1ad6707d418febbeff3fd87111faa92d8b509542a1e2",
    CANDIDATES: "ed1a698cad783887d9f511972c329cd1a649b1d1ab924255ad996893675020c3",
    MENTIONS: "8976f979a97de735298020f8438d40eeba2e37b02e54901d308322393a21ccea",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
EXPECTED_SEGMENT_SHA = "db07ec7058c789d990203d8c8481c7a56c303b3c10655c8019656d99b03d78f3"
UNSET_IDS = {
    "st-chp8-p203-belloni-collection",
    "st-chp8-p203-belloni-hospitality-james-iii",
    "st-chp8-p203-belloni-sent-gambarini-to-rome",
    "st-chp8-p203-bellucci-crespi-pictures",
    "st-chp8-p203-bellucci-dal-sole-pictures",
    "st-chp8-p203-bologna-senatorial-collections",
    "st-chp8-p203-bolognese-doctors-picture-owners",
    "st-chp8-p203-genoa-republic",
    "st-chp8-p203-genoese-family-collections",
    "st-chp8-p203-local-schools-support",
    "st-chp8-p203-malpighi-friends-and-collector",
    "st-chp8-p203-malpighi-reni-painting-and-taste",
    "st-chp8-p203-merchant-group-open-continuation",
    "st-chp8-p203-merchants-role",
    "st-chp8-p203-n5-zanotti-and-b109",
    "st-chp8-p203-naples-families-and-school",
    "st-chp8-p203-professional-class-patrons",
}
RENAMED_IDS = {
    "st-chp8-p203-malpighi-friends-and-collector": "st-chp8-p203-malpighi-friend-guercino",
}
NEW_STATEMENT_IDS = {
    "st-chp8-p203-italian-patronage-context",
    "st-chp8-p203-bologna-second-capital",
    "st-chp8-p203-bologna-senatorial-families-rule",
    "st-chp8-p203-malpighi-friend-cignani",
    "st-chp8-p203-malpighi-connoisseur-description",
    "st-chp8-p203-malpighi-keen-collector",
    "st-chp8-p203-n5-cite-zanotti",
    "st-chp8-p203-naples-school-support",
}
CANDIDATE_SPECS = [
    ("cand-12006", "Unidentified pictures by dal Sole, Torelli, Crespi and Gambarini in Belloni's holdings", "work", "Haskell reports a large group of pictures by four named artists in Belloni's ownership. No individual title, date, or location is supplied.", 8),
    ("cand-12007", "Unidentified pictures by Crespi in Bellucci's holdings", "work", "Haskell reports works by Crespi owned by Bellucci; no individual title, date, or location is supplied.", 8),
    ("cand-12008", "Unidentified pictures by dal Sole in Bellucci's holdings", "work", "Haskell reports many more works by dal Sole owned by Bellucci; no individual title, date, or location is supplied.", 9),
    ("cand-12009", "Bologna senatorial families named in Haskell's account (group)", "", "Source-defined group of the Albergati, Aldrovandi, Ercolani, Ghisilieri, Pepoli and Sampieri families. It is not one family, and branches or individual members are not identified.", 8),
    ("cand-12010", "Unidentified collections built by Bologna's senatorial families (group)", "", "Collective scope of the several collections attributed to the named senatorial families. Do not merge them into one collection or infer titles, complete membership, or individual ownership.", 8),
    ("cand-12011", "Picture holdings in the palaces of principal Genoese mercantile families (group)", "", "Haskell describes holdings across several family palaces, including works by native painters, occasional pictures brought from Bologna, and old masters. This is not one private collection.", 6),
    ("cand-12012", "Noble families and religious orders supporting local painting schools (group)", "", "Source-defined actor group consisting of the two classes named by Haskell; no particular family, order, or school is identified.", 4),
    ("cand-12013", "Bolognese doctors named as picture owners (group)", "", "Source-defined group of Paolo Battista Balbi, Beccari and Marcello Malpighi, to whom Haskell distributively attributes picture ownership. Their individual pictures are not identified or assigned.", 8),
]
MENTION_SPECS = [
    ("m-s2-chp8-p203-belloni-picture-group", "cand-12006", "large numbers of pictures by Giovan Gioseffo dal Sole, Felice Torelli, Crespi and Gambarini", "Unidentified works grouped by Haskell under Belloni's ownership."),
    ("m-s2-chp8-p203-bellucci-crespi-picture-group", "cand-12007", "works by\nCrespi", "Unidentified works by Crespi in Bellucci's holdings."),
    ("m-s2-chp8-p203-bellucci-dal-sole-picture-group", "cand-12008", "many more by dal Sole", "Unidentified works by dal Sole in Bellucci's holdings."),
    ("m-s2-chp8-p203-bologna-senatorial-families-group", "cand-12009", "the Albergati and the Aldrovandi, the Ercolani and Ghisilieri, Pepoli and Sampieri", "The six families grouped by Haskell as Bologna's senatorial families."),
    ("m-s2-chp8-p203-bologna-family-collections-group", "cand-12010", "vast collections of the works of artists still basking in the reflected glory of the Carracci and their followers", "The collective but non-individualized family collections described by Haskell."),
    ("m-s2-chp8-p203-genoese-palace-holdings-group", "cand-12011", "filled their palaces with the works of native painters, the occasional contemporary picture brought back from Bologna, where the Legate or Vicelcgate was nearly always a Genoese, and a selection of old masters", "Aggregate palace holdings across the named Genoese families; individual holdings are not assigned."),
    ("m-s2-chp8-p203-school-supporter-group", "cand-12012", "the great noble families and the religious orders", "The two source-defined classes that supported local painting schools."),
    ("m-s2-chp8-p203-bolognese-doctors-owner-group", "cand-12013", "Paolo Battista Balbi, Beccari and the great - Marcello Malpighi", "The three doctors to whom Haskell distributively attributes picture ownership."),
    ("m-s2-chp8-p203-leading-cities-group", "cand-2066", "all the leading cities", "Collective city scope in Haskell's account of provincial patronage."),
    ("m-s2-chp8-p203-each-city-group", "cand-2066", "each one of these cities", "Anaphoric reference to the previously described Italian provincial cities."),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def jsonl_bytes(rows) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows) -> bytes:
    import io
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def normalize(text: str) -> str:
    return " ".join(text.split())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all guards pass")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    hashes = {path: sha(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit("one or more source tables changed since this script's reviewed baseline")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES, MENTIONS)}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("a recovery copy already exists; inspect it before applying this script")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_rows = read_jsonl(SEGMENTS)
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (segment["line_start"], segment["line_end"]) != (3, 12):
        raise SystemExit("p.203 source segment metadata changed")
    if segment.get("asset_sha256") != EXPECTED_HASHES[SOURCE]:
        raise SystemExit("p.203 source asset fingerprint does not match the segment registry")
    segment_text = "\n".join(source_lines[2:12])
    if segment.get("sha256") != EXPECTED_SEGMENT_SHA or sha(segment_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.203 segment text changed since review")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("statement IDs are not unique")
    current_segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    actual_unset = {
        row["statement_id"] for row in current_segment_rows
        if "relation_candidate" not in (row.get("qualifiers") or {})
    }
    if actual_unset != UNSET_IDS:
        raise SystemExit(f"unexpected p.203 unset statement inventory: {sorted(actual_unset ^ UNSET_IDS)}")
    if len(current_segment_rows) != 17:
        raise SystemExit(f"unexpected p.203 statement count before review: {len(current_segment_rows)}")
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("one or more planned statement IDs already exist")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise SystemExit("candidate or mention IDs are not unique")
    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidates)
    if max_candidate != 12005:
        raise SystemExit(f"candidate sequence changed: expected cand-12005, found cand-{max_candidate}")
    new_candidate_ids = {spec[0] for spec in CANDIDATE_SPECS}
    new_mention_ids = {spec[0] for spec in MENTION_SPECS}
    if new_candidate_ids & set(candidate_by_id) or new_mention_ids & set(mention_by_id):
        raise SystemExit("a planned candidate or mention ID already exists")

    def excerpt(start_line: int, end_line: int, first: str, last: str) -> str:
        source = "\n".join(source_lines[start_line - 1:end_line])
        start = source.find(first)
        end = source.rfind(last)
        if start < 0 or end < start:
            raise SystemExit(f"expected source phrase missing at L{start_line}-L{end_line}: {first!r} ... {last!r}")
        end += len(last)
        return source[start:end]

    new_candidates = []
    for candidate_id, name, kind, detail, line in CANDIDATE_SPECS:
        new_candidates.append({
            "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
            "index_page_range": "", "suggested_type": kind, "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": detail,
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        })
    candidates.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    new_mentions = []
    for mention_id, candidate_id, surface, note in MENTION_SPECS:
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"planned mention has no candidate: {mention_id}")
        starts = [i for i in range(len(segment_text)) if segment_text.startswith(surface, i)]
        if len(starts) != 1:
            raise SystemExit(f"mention surface is not unique in p.203 source text: {mention_id}: {surface!r}")
        start = starts[0]
        new_mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
        })
    mentions.extend(new_mentions)
    mention_by_id.update({row["mention_id"]: row for row in new_mentions})

    def revise(statement_id: str, *, predicate: str, subject: str | None, object_id: str | None,
               claim: str, qualification: str, quote_text: str, start_line: int, end_line: int,
               mentioned: list[str], relation: bool, relation_note: str,
               open_reason: str | None = None, extra: dict | None = None,
               remove_qualifiers: tuple[str, ...] = ()) -> dict:
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        for key in remove_qualifiers:
            q.pop(key, None)
        source = "\n".join(source_lines[start_line - 1:end_line])
        if normalize(quote_text) not in normalize(source):
            raise SystemExit(f"statement quote does not match source: {statement_id}")
        q.update({
            "source_line_start": start_line, "source_line_end": end_line,
            "printed_page": 203, "pdf_physical_page": 1,
            "claim": claim, "speaker": q.get("speaker", "Haskell"),
            "text_layer": q.get("text_layer", "body"), "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation, "relation_candidate_note": relation_note,
        })
        if open_reason:
            q["open_endpoint_reason"] = open_reason
        else:
            q.pop("open_endpoint_reason", None)
        if extra:
            q.update(extra)
        row.update({
            "subject_candidate_id": subject, "object_candidate_id": object_id,
            "predicate": predicate, "qualifiers": q, "original_quote": quote_text,
        })
        return row

    def new_statement(statement_id: str, *, subject: str | None, object_id: str | None,
                      predicate: str, claim: str, qualification: str, quote_text: str,
                      start_line: int, end_line: int, mentioned: list[str],
                      relation: bool, relation_note: str, speaker: str = "Haskell",
                      text_layer: str = "body", open_reason: str | None = None,
                      extra: dict | None = None) -> dict:
        source = "\n".join(source_lines[start_line - 1:end_line])
        if normalize(quote_text) not in normalize(source):
            raise SystemExit(f"new statement quote does not match source: {statement_id}")
        q = {
            "source_line_start": start_line, "source_line_end": end_line,
            "printed_page": 203, "pdf_physical_page": 1,
            "claim": claim, "speaker": speaker, "text_layer": text_layer,
            "qualification": qualification, "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation, "relation_candidate_note": relation_note,
        }
        if open_reason:
            q["open_endpoint_reason"] = open_reason
        if extra:
            q.update(extra)
        return {
            "statement_id": statement_id, "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject, "object_candidate_id": object_id,
            "predicate": predicate, "qualifiers": q, "original_quote": quote_text,
            "origin": "book", "source_file": SOURCE_REL,
        }

    # Separate the broad Italian-patronage context from its explicit school-support relation.
    revise(
        "st-chp8-p203-local-schools-support", predicate="supporting_groups_supported_local_painting_schools",
        subject="cand-12012", object_id="cand-7380",
        claim="Haskell says local painting schools flourished with support from great noble families and religious orders.",
        qualification="The named groups are collective and no individual school, family, or order is identified.",
        quote_text=excerpt(4, 4, "local schools of painting", "religious orders."), start_line=4, end_line=4,
        mentioned=["cand-12012", "cand-7380"], relation=True,
        relation_note="The source explicitly names two supporting actor classes and local painting schools; the group candidates preserve the collective scope.",
        remove_qualifiers=("ocr_corrections",),
    )
    revise(
        "st-chp8-p203-belloni-collection", predicate="merchant_owned_picture_group",
        subject="cand-0271", object_id="cand-12006",
        claim="Haskell says Belloni owned large numbers of pictures by dal Sole, Torelli, Crespi, and Gambarini.",
        qualification="The source-level work group is not an inventory; no individual title, date, or location is supplied.",
        quote_text=excerpt(8, 8, "owned large numbers of pictures", "Gambarini,"), start_line=8, end_line=8,
        mentioned=["cand-0271", "cand-12006", "cand-2480", "cand-2645", "cand-0871", "cand-1113"],
        relation=True, relation_note="Belloni is the stated owner and the unnamed picture group is bounded by the four named artists.",
    )
    revise(
        "st-chp8-p203-belloni-hospitality-james-iii", predicate="hosted_person",
        subject="cand-0271", object_id="cand-1318",
        claim="Haskell says Belloni gave hospitality to the exiled James III.",
        qualification="The title is retained as the source gives it; identity and regnal convention remain for S3.",
        quote_text=excerpt(8, 8, "Giovanni Antonio Belloni", "the exiled ‘James III’,"), start_line=8, end_line=8,
        mentioned=["cand-0271", "cand-1318"], relation=True,
        relation_note="The sentence directly identifies Belloni as the host and James III as the recipient of hospitality.",
    )
    revise(
        "st-chp8-p203-belloni-sent-gambarini-to-rome", predicate="merchant_sent_artist_on_journey_to_city",
        subject="cand-0271", object_id="cand-1113",
        claim="Haskell says Belloni sent Gambarini on a journey to Rome.",
        qualification="No date, purpose, or evidence that Belloni financed the journey is supplied.",
        quote_text=excerpt(8, 8, "and he sent the last artist", "Rome5"), start_line=8, end_line=8,
        mentioned=["cand-0271", "cand-1113", "cand-4490"], relation=True,
        relation_note="The person-to-person action is explicit; Rome remains the destination qualifier rather than the object of the sending relation.",
        extra={"destination_candidate_id": "cand-4490"},
    )
    revise(
        "st-chp8-p203-bellucci-crespi-pictures", predicate="merchant_owned_picture_group",
        subject="cand-0285", object_id="cand-12007",
        claim="Haskell says Bellucci owned unidentified works by Crespi.",
        qualification="No individual work, date, or location is supplied; Crespi is retained as the creator qualifier.",
        quote_text=excerpt(8, 9, "also owned works by", "Crespi"), start_line=8, end_line=9,
        mentioned=["cand-0285", "cand-12007", "cand-0871"], relation=True,
        relation_note="The owner and a source-bounded group of works are represented separately from the artist who made them.",
        extra={"creator_candidate_id": "cand-0871"},
    )
    revise(
        "st-chp8-p203-bellucci-dal-sole-pictures", predicate="merchant_owned_picture_group",
        subject="cand-0285", object_id="cand-12008",
        claim="Haskell says Bellucci owned many more unidentified works by dal Sole.",
        qualification="The comparative wording ‘many more’ is retained; no individual work, date, or location is supplied.",
        quote_text=excerpt(9, 9, "and many more by", "dal Sole."), start_line=9, end_line=9,
        mentioned=["cand-0285", "cand-12008", "cand-2480"], relation=True,
        relation_note="The owner and the unnamed group of works are separate from dal Sole as creator; the quantity comparison remains source-attributed.",
        extra={"creator_candidate_id": "cand-2480"},
    )
    revise(
        "st-chp8-p203-bologna-senatorial-collections", predicate="senatorial_families_built_collections_of_carracci_influenced_works",
        subject="cand-12009", object_id="cand-12010",
        claim="Haskell says Bologna's named senatorial families built vast collections of works by artists still associated with the reflected glory of the Carracci and their followers.",
        qualification="The statement concerns the family group and its several collections; it does not assign a collection to each family or identify individual works.",
        quote_text=excerpt(8, 8, "who built up vast collections", "Carracci and their followers."), start_line=8, end_line=8,
        mentioned=["cand-12009", "cand-12010", "cand-7373", "cand-7374", "cand-7375", "cand-7376", "cand-7377", "cand-7378", "cand-7383"],
        relation=True, relation_note="The family group and the aggregate collection scope are explicit in the source; Carracci influence qualifies the works rather than serving as the collection object.",
        remove_qualifiers=("ocr_corrections",),
    )
    revise(
        "st-chp8-p203-bolognese-doctors-picture-owners", predicate="doctors_owned_unidentified_pictures",
        subject="cand-12013", object_id=None,
        claim="Haskell says Paolo Battista Balbi, Beccari, and Marcello Malpighi all owned pictures.",
        qualification="The source distributes ownership across the three named doctors; it does not assign a particular picture to any one of them.",
        quote_text=excerpt(8, 8, "In Bologna there were the doctors:", "all owned pictures."), start_line=8, end_line=8,
        mentioned=["cand-12013", "cand-0381", "cand-0164", "cand-0264", "cand-1500"], relation=True,
        relation_note="The named doctor group is the source's collective subject; the picture endpoint remains open because no works are identified.",
        open_reason="Haskell names no individual picture or single shared collection, and the sentence does not assign specific pictures to the three doctors.",
        extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 8, "ocr": "great - Marcello", "print": "great Marcello", "basis": "CHP-8.pdf physical page 1; stray OCR punctuation removed."}]},
        remove_qualifiers=("ocr_corrections",),
    )
    revise(
        "st-chp8-p203-genoa-republic", predicate="mercantile_aristocracy_dominated_polity",
        subject="cand-1132", object_id="cand-7379",
        claim="Haskell says Genoa's rich mercantile aristocracy dominated the Republic.",
        qualification="The passage names no officeholders or political mechanism; this remains Haskell's broad characterization.",
        quote_text=excerpt(4, 4, "In Genoa", "the Republic."), start_line=4, end_line=4,
        mentioned=["cand-1131", "cand-1132", "cand-7379"], relation=True,
        relation_note="Both the social group and the polity are explicit endpoints; the source supplies the direction of domination.",
    )
    revise(
        "st-chp8-p203-genoese-family-collections", predicate="mercantile_families_filled_palaces_with_picture_holdings",
        subject="cand-1132", object_id="cand-12011",
        claim="Haskell says the principal Genoese mercantile families filled their palaces with works by native painters, occasional contemporary pictures from Bologna, and selected old masters.",
        qualification="The group claim spans multiple family palaces and holdings; it assigns no particular picture or palace to an individual family.",
        quote_text=excerpt(5, 6, "Its principal members", "old masters."), start_line=5, end_line=6,
        mentioned=["cand-1132", "cand-12011", "cand-7357", "cand-7358", "cand-7359", "cand-7360", "cand-7361", "cand-7362", "cand-7363", "cand-7364", "cand-7365", "cand-7366", "cand-7367", "cand-0381", "cand-7381", "cand-4288"],
        relation=True, relation_note="The group of mercantile families and their aggregate palace holdings are source-bounded; the distinct families and works remain unassigned individually.",
    )
    revise(
        "st-chp8-p203-malpighi-reni-painting-and-taste", predicate="malpighi_commented_on_painting",
        subject="cand-1500", object_id="cand-7384",
        claim="Haskell reports Malpighi's comment on a painting of S. Luigi Gonzaga by Guido Reni.",
        qualification="Haskell's separate characterization of Malpighi's taste is not part of this relation; the painting's identity and location are not independently verified.",
        quote_text=excerpt(8, 8, "quel abito gesuitico", "Guido Reni"), start_line=8, end_line=8,
        mentioned=["cand-1500", "cand-7384", "cand-5453", "cand-2132"], relation=True,
        relation_note="The source directly reports Malpighi's comment about the candidate painting; the quoted remark remains attributed through Haskell.",
    )
    revise(
        "st-chp8-p203-merchant-group-open-continuation", predicate="descriptive_sentence_open_continuation",
        subject=None, object_id=None,
        claim="The p.203 fragment introduces the most cultivated and interesting member of a small merchant group, with the sentence completed on p.204 as Giovanni Ricci.",
        qualification="This row is retained as a page-continuation marker; the complete Ricci claim is recorded in the p.204 segment.",
        quote_text=excerpt(9, 9, "Crespi and many more by dal Sole.", "this little"), start_line=9, end_line=9,
        mentioned=[], relation=False,
        relation_note="The fragment is not an independent proposition; its continuation is represented in the following p.204 statement.",
        extra={"continuation_status": "completed", "continuation_completed_in_segment_id": "chp-8:08_CHP-8_sec_i:l14-21", "continuation_source_lines": [15]},
    )
    revise(
        "st-chp8-p203-merchants-role", predicate="merchants_influential_in_bologna_artistic_life",
        subject="cand-2065", object_id="cand-0381",
        claim="Haskell says merchants, especially at the end of the century, played a very influential role in Bologna's artistic life.",
        qualification="This is the author's general assessment; Belloni and Bellucci are examples, not an exhaustive merchant group.",
        quote_text=excerpt(8, 8, "there were the merchants", "artistic life of the city."), start_line=8, end_line=8,
        mentioned=["cand-2065", "cand-0381", "cand-0271", "cand-0285"], relation=True,
        relation_note="The source identifies merchants as the actor group and Bologna as the city whose artistic life they influenced.",
    )
    revise(
        "st-chp8-p203-n5-zanotti-and-b109", predicate="manuscript_source_for_family_collection_records",
        subject="cand-7387", object_id="cand-7390",
        claim="Haskell calls manuscript B.109 by Marcello Oretti an essential source for Belloni's, Bellucci's, and Bolognese family collections.",
        qualification="This records Haskell's source description; the manuscript was not independently consulted and ‘essential’ is not an independent completeness assessment.",
        quote_text=excerpt(10, 12, "The essential source", "Bolognese."), start_line=10, end_line=12,
        mentioned=["cand-7387", "cand-7390", "cand-7385", "cand-7386", "cand-0271", "cand-0285", "cand-0381"],
        relation=True, relation_note="The manuscript and the source-defined family-collection scope are separate endpoints; the claim is explicitly attributed to Haskell's note.",
        extra={"manuscript_shelfmark": "B.109", "repository_candidate_id": "cand-7386", "author_candidate_id": "cand-7385"},
        remove_qualifiers=("citations", "citation_publication_candidate_id", "citation_locator", "cited_material_not_independently_consulted"),
    )
    revise(
        "st-chp8-p203-naples-families-and-school", predicate="neapolitan_landowners_prospered_under_spanish_rule",
        subject="cand-1723", object_id="cand-4591",
        claim="Haskell says the named Neapolitan feudal landowners prospered under Spanish rule.",
        qualification="This collective statement does not identify individual family members or quantify prosperity.",
        quote_text=excerpt(6, 8, "the feudal landowners of the", "prospered under Spanish rule"), start_line=6, end_line=8,
        mentioned=["cand-1722", "cand-1723", "cand-7368", "cand-7369", "cand-7370", "cand-7371", "cand-7372", "cand-4591"],
        relation=True, relation_note="The passage directly links the source-defined landowner group to the Spanish-rule context; the claim remains attributed to Haskell.",
    )
    revise(
        "st-chp8-p203-professional-class-patrons", predicate="professional_classes_important_as_patrons_in_cities",
        subject="cand-2065", object_id="cand-2066",
        claim="Haskell says patrons from professional classes were important in the previously described provincial cities.",
        qualification="The claim is a generalization about the group and cities; it does not imply equal importance or identify all patrons.",
        quote_text=excerpt(8, 8, "Moreover, in each one of these cities", "were also of importance."), start_line=8, end_line=8,
        mentioned=["cand-2065", "cand-2066", "cand-3397", "cand-3401", "cand-0381"], relation=True,
        relation_note="The professional-class patron group and the previously named city group are explicit, source-linked endpoints.",
    )

    # The original sentence's three contextual claims and the relationship claims are recorded separately.
    general_context = new_statement(
        "st-chp8-p203-italian-patronage-context", subject="cand-3461", object_id=None,
        predicate="authorial_comparison_of_world_and_italian_patronage",
        claim="Haskell contrasts the New World with the Old and says patronage remained extensive in Italy, where leading cities treated it as a natural accompaniment of wealth and power.",
        qualification="This is a broad authorial comparison and characterization, not a measurable relation between the named places and wealth.",
        quote_text=excerpt(3, 4, "HE new world", "wealth and power"), start_line=3, end_line=4,
        mentioned=["cand-3461", "cand-2066"], relation=False,
        relation_note="The passage offers a broad historical comparison and general condition rather than a discrete entity-to-entity relation.",
        text_layer="authorial interpretation",
        extra={"ocr_corrections": [
            {"source_file": SOURCE_REL, "source_line": 3, "ocr": "HE", "print": "THE", "basis": "CHP-8.pdf physical page 1."},
            {"source_file": SOURCE_REL, "source_line": 4, "ocr": "Titself", "print": "itself", "basis": "CHP-8.pdf physical page 1."},
        ]},
    )
    bologna_capital = new_statement(
        "st-chp8-p203-bologna-second-capital", subject="cand-0382", object_id="cand-1831",
        predicate="bologna_described_as_second_capital_of_papal_states",
        claim="Haskell describes Bologna as the second capital within the Papal States.",
        qualification="This is the author's historical characterization; it does not specify a constitutional or modern administrative status.",
        quote_text=excerpt(8, 8, "within the papal states themselves Bologna", "the second.capital"), start_line=8, end_line=8,
        mentioned=["cand-1831", "cand-0382"], relation=True,
        relation_note="The city and the Papal States are both named in the same source clause; the OCR punctuation correction is recorded below.",
        extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 8, "ocr": "second.capital", "print": "second capital", "basis": "CHP-8.pdf physical page 1."}]},
    )
    bologna_rule = new_statement(
        "st-chp8-p203-bologna-senatorial-families-rule", subject="cand-12009", object_id="cand-0382",
        predicate="senatorial_families_ruled_bologna_with_limited_autonomy",
        claim="Haskell says Bologna was ruled by the named senatorial families, which retained some semblance of autonomy.",
        qualification="The source describes the families collectively and qualifies their autonomy as only a semblance; no individual family is assigned a ruling act.",
        quote_text=excerpt(8, 8, "was ruled by senatorial families", "Pepoli and Sampieri"), start_line=8, end_line=8,
        mentioned=["cand-12009", "cand-0382", "cand-7373", "cand-7374", "cand-7375", "cand-7376", "cand-7377", "cand-7378"],
        relation=True, relation_note="The source directly states that the bounded family group ruled Bologna; the qualification preserves the limited-autonomy wording.",
    )
    malpighi_friend_cignani = new_statement(
        "st-chp8-p203-malpighi-friend-cignani", subject="cand-1500", object_id="cand-0748",
        predicate="friendship_with_person",
        claim="Haskell identifies Cignani as one of the artists who was a friend of Malpighi.",
        qualification="The phrase ‘such as’ gives examples rather than a complete list of Malpighi's artist friends.",
        quote_text=excerpt(8, 8, "the friend of artists such as Guercino", "Cignani"), start_line=8, end_line=8,
        mentioned=["cand-1500", "cand-0748"], relation=True,
        relation_note="The source explicitly includes Cignani in the set of Malpighi's artist friends.",
    )
    malpighi_connoisseur = new_statement(
        "st-chp8-p203-malpighi-connoisseur-description", subject="cand-1500", object_id=None,
        predicate="described_as_connoisseur_with_fine_decided_taste",
        claim="Haskell describes Malpighi as a connoisseur with fine and decided tastes.",
        qualification="This is Haskell's evaluative description of a person's attribute; the reported painting comment is preserved separately.",
        quote_text=excerpt(8, 8, "Indeed the latter was a connoisseur", "decided tastes"), start_line=8, end_line=8,
        mentioned=["cand-1500"], relation=False,
        relation_note="This is a descriptive attribute of Malpighi, not a relation between two independently identified entities.",
        text_layer="authorial characterization",
    )
    malpighi_collector = new_statement(
        "st-chp8-p203-malpighi-keen-collector", subject="cand-1500", object_id=None,
        predicate="described_as_keen_picture_collector",
        claim="Haskell describes Malpighi as a keen collector.",
        qualification="This is a description of Malpighi's activity; his friendships and comment on the Reni painting are recorded separately.",
        quote_text=excerpt(8, 8, "and a keen collector", "collector."), start_line=8, end_line=8,
        mentioned=["cand-1500"], relation=False,
        relation_note="The sentence describes a person's collecting activity without identifying a collection object or a second entity endpoint.",
        text_layer="authorial characterization",
    )
    naples_school = new_statement(
        "st-chp8-p203-naples-school-support", subject="cand-1723", object_id="cand-7382",
        predicate="neapolitan_landowners_supported_local_school_of_art",
        claim="Haskell says the Neapolitan feudal landowners gave lavish support to a local school of art.",
        qualification="The school is not named as a formal institution; Haskell compares its brilliance and diversity with Rome.",
        quote_text=excerpt(8, 8, "gave lavish support", "brilliance and diversity."), start_line=8, end_line=8,
        mentioned=["cand-1723", "cand-7368", "cand-7369", "cand-7370", "cand-7371", "cand-7372", "cand-7382", "cand-4490"],
        relation=True, relation_note="The source expressly connects the named landowner group to the local school; the Roman comparison remains an authorial qualification.",
    )
    zanotti_citation = {
        "statement_id": "st-chp8-p203-n5-cite-zanotti", "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2962", "object_candidate_id": "cand-7115", "predicate": "cites",
        "qualifiers": {
            "source_line_start": 10, "source_line_end": 10, "printed_page": 203, "pdf_physical_page": 1,
            "claim": "Haskell's p.203 note 5 cites Zanotti, volume I, page 389.",
            "speaker": "Haskell footnote", "text_layer": "bibliographic citation to publication",
            "qualification": "The cited page was not independently consulted; the locator is preserved as printed.",
            "mentioned_candidate_ids": ["cand-2962", "cand-7115"], "footnote_marker": 5,
            "citations": [{"source_candidate_id": "cand-2962", "publication_candidate_id": "cand-7115", "volume": "I", "page": "389"}],
            "citation_publication_candidate_id": "cand-7115", "citation_locator": "vol. I, p. 389",
            "cited_material_not_independently_consulted": True, "relation_candidate": True,
            "relation_candidate_note": "The note explicitly cites the separate Zanotti publication; its page is a locator, not independently consulted evidence.",
        },
        "original_quote": excerpt(10, 10, "Zanotti, I", "p. 389."), "origin": "book", "source_file": SOURCE_REL,
    }
    new_rows = [general_context, bologna_capital, bologna_rule, malpighi_friend_cignani,
                malpighi_connoisseur, malpighi_collector, naples_school, zanotti_citation]
    for row in new_rows:
        if row["statement_id"] in by_id:
            raise SystemExit(f"new statement ID collision: {row['statement_id']}")
        by_id[row["statement_id"]] = row

    # The old compound ID becomes the single Guercino friendship; replace any historical references.
    old_friend_id, new_friend_id = next(iter(RENAMED_IDS.items()))
    friend_row = by_id.pop(old_friend_id)
    friend_row["statement_id"] = new_friend_id
    friend_quote = excerpt(8, 8, "the friend of artists such as", "Guercino")
    q = dict(friend_row.get("qualifiers") or {})
    q.update({
        "source_line_start": 8, "source_line_end": 8, "printed_page": 203, "pdf_physical_page": 1,
        "claim": "Haskell identifies Guercino as one of the artists who was a friend of Malpighi.",
        "speaker": "Haskell", "text_layer": "body",
        "qualification": "The phrase ‘such as’ gives examples rather than a complete list of Malpighi's artist friends.",
        "mentioned_candidate_ids": ["cand-1500", "cand-1258"], "relation_candidate": True,
        "relation_candidate_note": "The source explicitly includes Guercino in the set of Malpighi's artist friends.",
    })
    q.pop("open_endpoint_reason", None)
    friend_row.update({
        "subject_candidate_id": "cand-1500", "object_candidate_id": "cand-1258",
        "predicate": "friendship_with_person", "qualifiers": q, "original_quote": friend_quote,
    })
    by_id[new_friend_id] = friend_row
    for row in statements + new_rows:
        if row is friend_row:
            continue
        qf = row.get("qualifiers") or {}
        for key, value in list(qf.items()):
            if isinstance(value, list):
                qf[key] = [new_friend_id if item == old_friend_id else item for item in value]
            elif isinstance(value, dict):
                for nested_key, nested_value in list(value.items()):
                    if isinstance(nested_value, list):
                        value[nested_key] = [new_friend_id if item == old_friend_id else item for item in nested_value]

    # Insert new rows after the existing p.203 source block while preserving the rest of source order.
    last_segment_index = max(i for i, row in enumerate(statements) if row.get("segment_id") == SEGMENT_ID)
    statements[last_segment_index + 1:last_segment_index + 1] = new_rows
    by_id = {row["statement_id"]: row for row in statements}

    note_links = {
        1: (["st-chp8-p203-genoese-family-collections"], ["st-chp8-p203-n1-soprani"], INTRO_NOTES_SEGMENT, "L8-L8", "Soprani is cited for Haskell's account of the Genoese families."),
        2: (["st-chp8-p203-naples-families-and-school", "st-chp8-p203-naples-school-support"], ["st-chp8-p203-n2-naples-citations", "st-chp8-p203-n2-cite-maresca"], INTRO_NOTES_SEGMENT, "L8-L8", "The note's general Naples references are linked to the landowner and school claims."),
        3: (["st-chp8-p203-bologna-senatorial-collections"], ["st-chp8-p203-n3-bologna-citations", "st-chp8-p203-n3-cite-zanotti"], INTRO_NOTES_SEGMENT, "L9-L9", "Malvasia and Zanotti are cited for the Bologna family collections."),
        4: (["st-chp8-p203-malpighi-connoisseur-description", "st-chp8-p203-malpighi-reni-painting-and-taste", new_friend_id, "st-chp8-p203-malpighi-friend-cignani", "st-chp8-p203-malpighi-keen-collector"], ["st-chp8-p203-n4-ruffo-citation"], INTRO_NOTES_SEGMENT, "L10-L10", "Ruffo is cited in connection with Haskell's Malpighi passage."),
        5: (["st-chp8-p203-belloni-collection", "st-chp8-p203-belloni-sent-gambarini-to-rome", "st-chp8-p203-bellucci-crespi-pictures", "st-chp8-p203-bellucci-dal-sole-pictures"], ["st-chp8-p203-n5-zanotti-and-b109", "st-chp8-p203-n5-cite-zanotti"], SEGMENT_ID, "L10-L12", "Note 5 cites Zanotti and identifies B.109 as a source for the named collections."),
    }

    def update_note_links(marker: int) -> None:
        body_ids, note_ids, note_segment, note_range, link_note = note_links[marker]
        body_rows = [by_id[sid] for sid in body_ids]
        note_rows = [by_id[sid] for sid in note_ids]
        if any(row.get("segment_id") != SEGMENT_ID for row in body_rows):
            raise SystemExit(f"unexpected p.203 body segment in note {marker} link")
        body_lines: dict[int, list[str]] = {}
        for row in body_rows:
            line = int(row["qualifiers"]["source_line_start"])
            body_lines.setdefault(line, []).append(row["statement_id"])
            qf = dict(row.get("qualifiers") or {})
            qf.update({
                "footnote_marker": marker, "footnote_segment": note_segment,
                "footnote_line_range": note_range, "footnote_text_pending": False,
                "footnote_body_link_status": "linked",
                "footnote_body_line_range": f"L{row['qualifiers']['source_line_start']}-L{row['qualifiers']['source_line_end']}",
                "footnote_note_statement_ids": [note["statement_id"] for note in note_rows],
                "footnote_link_note": link_note,
            })
            row["qualifiers"] = qf
        refs = [{
            "marker": marker, "segment_id": SEGMENT_ID, "source_line": line,
            "statement_ids": ids,
        } for line, ids in sorted(body_lines.items())]
        related_lines = sorted(body_lines)
        for row in note_rows:
            qf = dict(row.get("qualifiers") or {})
            qf.update({
                "linked_body_statement_ids": body_ids,
                "footnote_number": marker, "footnote_segment": note_segment,
                "related_segment": SEGMENT_ID, "related_source_lines": related_lines,
                "related_body_statement_ids": body_ids, "footnote_refs": refs,
                "footnote_link_status": "linked", "footnote_body_link_status": "linked",
                "footnote_text_pending": False,
            })
            row["qualifiers"] = qf

    for marker in note_links:
        update_note_links(marker)

    # Keep every source-level mention and statement quote anchored to this exact S0 segment.
    all_candidate_ids = set(candidate_by_id)
    for mention in new_mentions:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"mention offset mismatch: {mention['mention_id']}")
    for row in statements:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        qf = row.get("qualifiers") or {}
        start, end = int(qf["source_line_start"]), int(qf["source_line_end"])
        source = "\n".join(source_lines[start - 1:end])
        if normalize(row["original_quote"]) not in normalize(source):
            raise SystemExit(f"p.203 source quote mismatch: {row['statement_id']}")
        if not set(qf.get("mentioned_candidate_ids", [])) <= all_candidate_ids:
            raise SystemExit(f"missing candidate mention endpoint: {row['statement_id']}")
        if qf.get("relation_candidate") is True:
            missing = not row.get("subject_candidate_id") or not row.get("object_candidate_id")
            if missing and not qf.get("open_endpoint_reason"):
                raise SystemExit(f"true relation candidate has an unexplained open endpoint: {row['statement_id']}")
        if qf.get("relation_candidate") is None:
            raise SystemExit(f"p.203 statement remains unclassified: {row['statement_id']}")

    # Update the renamed Guercino statement in all cross-references, including the new note-4 links.
    for row in statements:
        if row.get("statement_id") == "st-chp8-p203-malpighi-keen-collector":
            continue
        qf = row.get("qualifiers") or {}
        for key, value in list(qf.items()):
            if isinstance(value, list):
                qf[key] = [new_friend_id if item == old_friend_id else item for item in value]
            elif isinstance(value, dict):
                for nested_key, nested_value in list(value.items()):
                    if isinstance(nested_value, list):
                        value[nested_key] = [new_friend_id if item == old_friend_id else item for item in nested_value]

    planned_keys = [(row["canonical_name"].casefold(), row["suggested_type"].casefold()) for row in new_candidates]
    if len(planned_keys) != len(set(planned_keys)):
        raise SystemExit("planned candidates duplicate each other by canonical name/type")
    existing_keys = {(row["canonical_name"].casefold(), row["suggested_type"].casefold()) for row in candidates if row["candidate_id"] not in new_candidate_ids}
    if existing_keys.intersection(planned_keys):
        raise SystemExit("a planned candidate duplicates an existing canonical-name/type pair")
    expected_counts = {"statements": 14212, "candidates": 11991, "mentions": 28055, "true": 8871, "false": 3443, "unset": 1898}
    actual_counts = {
        "statements": len(statements), "candidates": len(candidates), "mentions": len(mentions),
        "true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements),
        "false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements),
        "unset": sum("relation_candidate" not in (row.get("qualifiers") or {}) for row in statements),
    }
    if actual_counts != expected_counts:
        raise SystemExit(f"unexpected post-write counts: {actual_counts}")

    output = {
        STATEMENTS: jsonl_bytes(statements),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions),
    }
    report = {
        "mode": "apply" if args.apply else "dry_run", "segment_id": SEGMENT_ID,
        "unclassified_statement_rows_reviewed": len(UNSET_IDS),
        "new_statements": sorted(NEW_STATEMENT_IDS),
        "renamed_statement": {old_friend_id: new_friend_id},
        "new_candidates": [row["candidate_id"] for row in new_candidates],
        "new_mentions": [row["mention_id"] for row in new_mentions],
        "post_counts": actual_counts,
        "input_sha256": {path.name: digest for path, digest in hashes.items()},
        "output_sha256": {path.name: sha(data) for path, data in output.items()},
        "recovery_copies": [path.name + BACKUP_SUFFIX for path in (STATEMENTS, CANDIDATES, MENTIONS)],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return

    for path, backup in backups.items():
        shutil.copy2(path, backup)
    for path, data in output.items():
        atomic_write(path, data)
    if any(sha(path.read_bytes()) != sha(output[path]) for path in output):
        raise SystemExit("post-write table hash verification failed; recovery copies are preserved")
    print("applied; recovery copies written and post-write hashes verified")


if __name__ == "__main__":
    main()
