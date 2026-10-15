from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md"
PDF = ROOT / "02-sources/01-book/CHP-5.pdf"
PAGE_IMAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p125_page_review_20261011.png"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
TABLES = {
    "statements": ROOT / "04-knowledge/tables/book-statements.jsonl",
    "candidates": ROOT / "04-knowledge/tables/entity-candidates.csv",
    "mentions": ROOT / "04-knowledge/tables/mentions.csv",
}
SOURCE_SHA256 = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA256 = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
PAGE_IMAGE_SHA256 = "c43955cb7d59339049136e16e79535af09271afa5a207ce7615c42825c23eec8"
BODY_SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l51-58"
NOTES_SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l125-147"
BODY_SEGMENT_SHA256 = "4608edfb8cd37a6e30c08ff2a88ac9896834e424339dad4474c4f5c4bf57075c"
NOTES_SEGMENT_SHA256 = "5fdb179fd5637ce1d0a0b6b3da66e4e871452e25debcd265e4749060845324e8"
EXPECTED_TABLE_SHA256 = {
    "statements": "3cf6ad7095fc5dd53928e5e80063d0ada07dc2c4077301fda0047b6840ea4899",
    "candidates": "bb2bbb083346defcdc080fecd0853376489e3ae47bf69d58ec3a64cc2f8b1eef",
    "mentions": "544f4b1f7f996c750325052e94d47178a8a79889454ff6aa4aa0b704d5517cab",
}
BACKUP_SUFFIX = ".bak-s2-chp5-p125-20261011"
RELATION_NOTE = "S2 source-attributed relation candidate only; this classification does not create a formal S6 edge."
NONRELATION_NOTE = "This is a source-attributed contextual, comparative, negative, or interpretive claim; it does not assert a specific binary entity relation."


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return raw, bom, text, reader.fieldnames, list(reader)


def emit_csv(headers, rows, bom: bool, source_text: str) -> bytes:
    newline = "\r\n" if "\r\n" in source_text else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=newline, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in headers})
    return (b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8")


def require_segment(records, segment_id, expected_sha, source_lines):
    row = next((item for item in records if item.get("segment_id") == segment_id), None)
    if row is None or row.get("sha256") != expected_sha:
        raise SystemExit(f"STOP: expected S0 segment record changed: {segment_id}")
    start, end = int(row["line_start"]), int(row["line_end"])
    if "\n".join(source_lines[start - 1:end]).encode("utf-8") and sha("\n".join(source_lines[start - 1:end]).encode("utf-8")) != expected_sha:
        raise SystemExit(f"STOP: source line slice does not match S0 segment hash: {segment_id}")
    return row


def make_candidate(candidate_id, name, kind, source_line, detail):
    return {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L{source_line}",
    }


def make_statement(statement_id, subject, object_, predicate, claim, quote, line_start, line_end,
                   relation, qualification, mentioned, speaker="Haskell", layer="authorial narrative",
                   extra=None):
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "pdf_physical_page": 6,
        "printed_page_locator": "p.125",
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation,
        "relation_candidate_note": RELATION_NOTE if relation else NONRELATION_NOTE,
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": BODY_SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Review and classify p.125 S2 statements; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the validated S2 table updates")
    args = parser.parse_args()

    for path, expected, label in (
        (SOURCE, SOURCE_SHA256, "canonical source"),
        (PDF, PDF_SHA256, "chapter PDF"),
        (PAGE_IMAGE, PAGE_IMAGE_SHA256, "p.125 page image"),
    ):
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"STOP: {label} changed: {path} ({actual})")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    with SEGMENTS.open(encoding="utf-8-sig") as handle:
        segment_rows = [json.loads(line) for line in handle if line.strip()]
    body_segment = require_segment(segment_rows, BODY_SEGMENT_ID, BODY_SEGMENT_SHA256, source_lines)
    require_segment(segment_rows, NOTES_SEGMENT_ID, NOTES_SEGMENT_SHA256, source_lines)
    if body_segment["source_file"] != "02-sources/02-Markdown/05_CHP-5_sec_i.md":
        raise SystemExit("STOP: p.125 segment points to an unexpected source asset")
    if not all(
        phrase in source_lines[line - 1]
        for line, phrase in (
            (52, "advantages, shrewdly yet discreetly"),
            (53, "The principal occasions"),
            (54, "In 1607"),
            (55, "an occasion which was apparently attended"),
            (56, "Bergamasque community in Rome"),
            (57, "S. Bartolomeo all’Isola"),
            (58, "papers of Giuseppe Ghezzi now in the Museo di Roma"),
            (143, "See Haskell, in Studi Secenteschi, i960"),
        )
    ):
        raise SystemExit("STOP: p.125 body/footnote text changed")

    source_text = "\n".join(source_lines)
    body_text = "\n".join(source_lines[int(body_segment["line_start"]) - 1:int(body_segment["line_end"])])
    notes_row = next(item for item in segment_rows if item["segment_id"] == NOTES_SEGMENT_ID)
    notes_text = "\n".join(source_lines[int(notes_row["line_start"]) - 1:int(notes_row["line_end"])])
    if sha(body_text.encode("utf-8")) != BODY_SEGMENT_SHA256 or sha(notes_text.encode("utf-8")) != NOTES_SEGMENT_SHA256:
        raise SystemExit("STOP: decoded segment slice does not match its S0 hash")

    raw_statement = TABLES["statements"].read_bytes()
    statement_bom = raw_statement.startswith(b"\xef\xbb\xbf")
    statement_text = raw_statement.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in statement_text else "\n"
    statement_rows = [json.loads(line) for line in statement_text.splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statement_rows}
    if len(by_id) != len(statement_rows):
        raise SystemExit("STOP: duplicate statement IDs")
    p125_ids = {
        "st-chp5-note-p125-n1-citation",
        "st-chp5-p125-artists-display-opportunity",
        "st-chp5-p125-bartolomeo-all-isola-exhibitions",
        "st-chp5-p125-bergamasque-chronology",
        "st-chp5-p125-bergamasque-decoration-observer",
        "st-chp5-p125-bergamasque-devotional-purpose",
        "st-chp5-p125-bergamasque-exhibition-practice",
        "st-chp5-p125-bergamasque-venue-funding",
        "st-chp5-p125-claude-wals-naples",
        "st-chp5-p125-exhibition-location-and-profile",
        "st-chp5-p125-exhibition-religious-calendar",
        "st-chp5-p125-exhibitions-public-contact",
        "st-chp5-p125-exhibitions-usefulness",
        "st-chp5-p125-ghezzi-papers-research-note",
        "st-chp5-p125-mantua-1607-display",
        "st-chp5-p125-mantua-event-attendance",
        "st-chp5-p125-painters-pressure-exhibition",
        "st-chp5-p125-sinigaglia-peasant-anecdote",
        "st-chp5-p125-three-figures-professional-label",
    }
    if not p125_ids.issubset(by_id):
        raise SystemExit(f"STOP: p.125 statement set changed; missing={sorted(p125_ids - set(by_id))}")
    if any(by_id[sid].get("qualifiers", {}).get("relation_candidate") is not None for sid in p125_ids):
        raise SystemExit("STOP: at least one p.125 target statement was already classified")
    for name, path in TABLES.items():
        actual = sha(path.read_bytes())
        if actual != EXPECTED_TABLE_SHA256[name]:
            raise SystemExit(f"STOP: {name} table changed: {actual}")

    candidate_raw, candidate_bom, candidate_text, candidate_fields, candidate_rows = read_csv(TABLES["candidates"])
    mention_raw, mention_bom, mention_text, mention_fields, mention_rows = read_csv(TABLES["mentions"])
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(candidate_by_id) != len(candidate_rows) or len(mention_by_id) != len(mention_rows):
        raise SystemExit("STOP: duplicate candidate or mention IDs")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) != 11714:
        raise SystemExit("STOP: candidate ID sequence changed; do not allocate IDs automatically")

    candidate_specs = [
        ("cand-11715", "Artists Haskell generally encounters at Roman exhibitions (p.125)", "term", 53,
         "A source-bounded group described as minor landscape/genre specialists and, above all, painters newly arrived in Rome or returning after a long absence. No members are named."),
        ("cand-11716", "Other craftsmen and merchants exhibiting wares alongside artists (p.125)", "term", 53,
         "Unnamed exhibitors whom Haskell says artists probably showed alongside at exhibitions; the source supplies no members or venue."),
        ("cand-11717", "Connoisseurs of standing attracted to exhibitions (p.125)", "term", 53,
         "An unnamed audience group in Haskell's qualified assessment; no individuals are identified."),
        ("cand-11718", "Artists in Haskell's p.125 claim about contact with a wider public", "term", 53,
         "A source-defined, unnamed group of artists whom the extension of exhibitions brought into contact with a wider public."),
        ("cand-11719", "Wider public reached through exhibitions in Haskell's p.125 account", "term", 53,
         "The unspecified audience in Haskell's comparison of exhibitions with dealers; membership is not given."),
        ("cand-11720", "Saints' days and processions as common exhibition occasions (p.125)", "event", 53,
         "A source-defined class of recurring religious occasions associated with public picture display; no individual event is dated here."),
        ("cand-11721", "Unnamed young peasant boy inspired by pictures at the Sinigaglia fair (p.125)", "person", 53,
         "Haskell reports hearing that a young peasant boy took up painting after seeing a picture stall; identity, date, and later career are unknown."),
        ("cand-11722", "Fair of Sinigaglia in the peasant-boy anecdote (p.125)", "event", 53,
         "The fair is named as the setting of the anecdote; no year or specific fair edition is supplied."),
        ("cand-11723", "Pictures displayed at a stall at the Sinigaglia fair (p.125)", "work", 53,
         "An unidentified group of pictures that Haskell says covered a stall at the fair; no titles or makers are named."),
        ("cand-11724", "Unidentified landscapes by Goffredo Wals seen by Claude (p.125)", "work", 53,
         "A source-defined group of Wals landscapes Claude was supposedly shown at a Roman exhibition; no titles or surviving objects are identified."),
        ("cand-11725", "Rome exhibition/display occasion involving Caravaggio's Death of the Virgin (1607)", "event", 53,
         "The narrative links an exhibition arranged under pressure from Roman painters with the 1607 display of Caravaggio's painting. The source gives no exact venue or event title."),
        ("cand-11726", "Unnamed agent of the Duke of Mantua in the 1607 account (p.125)", "person", 54,
         "The agent is the buyer and display actor in Haskell's account; the source does not name or further identify this person."),
        ("cand-11727", "Leading artists who apparently attended the 1607 occasion (unnamed group)", "term", 55,
         "Haskell says all the leading artists apparently attended; no members or complete roster are supplied."),
        ("cand-11728", "Bergamasque community's recurring St Bartholomew exhibitions in Rome (p.125)", "event", 56,
         "A recurring, more organized exhibition series held on 24 August for the community's patron saint. The source says it was flourishing by 1650 but gives no start date."),
        ("cand-11729", "Church of S. Bartolomeo with the Bergamasque exhibition courtyard (p.125)", "place", 57,
         "The source names this church as the courtyard venue. Keep it distinct from S. Bartolomeo all'Isola and from the generic index lead cand-0698."),
        ("cand-11730", "Unnamed Guardiano who paid for the Bergamasque exhibitions (p.125)", "person", 57,
         "The singular officeholder is named only by the title Guardiano; identity and institutional affiliation are not resolved."),
        ("cand-11731", "Tapestries hung on the S. Bartolomeo facade and nearby houses (p.125)", "work", 57,
         "An unidentified group of tapestries described in the event decoration; no individual textile is identified."),
        ("cand-11732", "Pictures spread around the inner courtyard of S. Bartolomeo (p.125)", "work", 57,
         "An unidentified group of pictures compared by an unnamed observer with the exterior hangings; no works are named."),
        ("cand-11733", "Houses around the S. Bartolomeo courtyard (p.125)", "place", 57,
         "The surrounding houses are mentioned as a group and are said to have been hung with tapestries; no individual buildings are identified."),
        ("cand-11734", "Unnamed devotees of St Bartholomew at the Bergamasque exhibition (p.125)", "term", 57,
         "A source-defined audience group honoured alongside the saint; no members are named."),
        ("cand-11735", "S. Bartolomeo all'Isola named in the exhibition account (p.125)", "place", 57,
         "Haskell attributes name-day exhibitions to this site name. The responsible institution and its identity relative to the building remain unresolved; keep separate from cand-11729."),
        ("cand-11736", "Name-day exhibitions attributed to S. Bartolomeo all'Isola (p.125)", "event", 57,
         "A source-defined exhibition series for the site's saint's name day; Haskell ranks it as less important than the Bergamasque series."),
        ("cand-11737", "Artists given display opportunities at the Bergamasque exhibitions (p.125)", "term", 57,
         "An unnamed group of artists whom Haskell says could display works at these devotional exhibitions."),
        ("cand-11738", "Artists of established reputation in Haskell's p.125 generalization", "term", 53,
         "A generic group about whom Haskell makes a claim concerning the perceived dignity of public exhibitions; no members are named."),
        ("cand-11739", "Painters in Rome who pressed for another exhibition (p.125)", "term", 53,
         "The unnamed group whom Haskell says pressured for an exhibition; membership and number are not given."),
    ]
    new_candidates = []
    for spec in candidate_specs:
        cid, name, kind, source_line, detail = spec
        if cid in candidate_by_id:
            raise SystemExit(f"STOP: candidate ID already exists: {cid}")
        new_candidates.append(make_candidate(cid, name, kind, source_line, detail))

    segment_starts = {
        BODY_SEGMENT_ID: int(body_segment["line_start"]),
        NOTES_SEGMENT_ID: int(notes_row["line_start"]),
    }
    segment_texts = {BODY_SEGMENT_ID: body_text, NOTES_SEGMENT_ID: notes_text}
    new_mentions = []
    next_mention = 25

    def add_mention(candidate_id, surface, source_line, note, segment_id=BODY_SEGMENT_ID, occurrence=0):
        nonlocal next_mention
        text = segment_texts[segment_id]
        start_line = segment_starts[segment_id]
        local_line = source_line - start_line
        lines = text.split("\n")
        if local_line < 0 or local_line >= len(lines):
            raise ValueError(f"line {source_line} is outside {segment_id}")
        line = lines[local_line]
        starts = []
        offset_in_line = 0
        while True:
            found = line.find(surface, offset_in_line)
            if found < 0:
                break
            starts.append(found)
            offset_in_line = found + 1
        if occurrence >= len(starts):
            raise ValueError(f"{surface!r} missing on source line {source_line}; found={len(starts)}")
        start = sum(len(part) + 1 for part in lines[:local_line]) + starts[occurrence]
        end = start + len(surface)
        if text[start:end] != surface:
            raise ValueError(f"mention span mismatch: {surface!r} at [{start},{end})")
        mention_id = f"m-chp5-p125-{next_mention:04d}" if segment_id == BODY_SEGMENT_ID else f"m-chp5-note-p125-{next_mention - 24:04d}"
        next_mention += 1
        if mention_id in mention_by_id:
            raise SystemExit(f"STOP: mention ID already exists: {mention_id}")
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })
        return mention_id

    for cid, surface, line, note in (
        ("cand-11715", "those that wegenerally come across", 53, "Source-defined profile group; the printed page reads 'those that we generally come across'."),
        ("cand-11716", "other craftsmen or merchants", 53, "Unnamed exhibitors whom artists probably showed alongside."),
        ("cand-11717", "connoisseurs of standing", 53, "Audience described as attracted by exhibitions."),
        ("cand-11718", "the artist", 53, "Generic artist in Haskell's public-contact claim."),
        ("cand-11719", "wider public", 53, "Unspecified audience in Haskell's public-contact claim."),
        ("cand-11720", "many saints’ days and processions", 53, "Recurring religious occasions identified as principal contexts for exhibitions."),
        ("cand-11721", "a young peasant boy", 53, "Anonymous person in the reported Sinigaglia anecdote."),
        ("cand-11722", "the fair of Sinigaglia", 53, "The fair is an event setting; the existing place mention Sinigaglia remains separate."),
        ("cand-11723", "a stall covered with pictures", 53, "The displayed pictures are unidentified."),
        ("cand-11724", "landscapes by the Flemish artist Goffredo Wals", 53, "Unidentified works reportedly seen by Claude."),
        ("cand-11725", "another exhibition", 53, "Narrative antecedent to the 1607 display occasion; connection is preserved as the passage presents it."),
        ("cand-11725", "an occasion", 55, "Anaphoric mention of the 1607 painting-display occasion."),
        ("cand-11726", "the Duke of Mantua’s agent", 54, "Unnamed buyer and display actor in the 1607 account."),
        ("cand-11727", "all the leading artists", 55, "The group said to have apparently attended the occasion."),
        ("cand-11728", "More organised exhibitions", 56, "Recurring Bergamasque community exhibition series."),
        ("cand-11728", "These", 57, "Anaphoric reference to the Bergamasque exhibitions."),
        ("cand-11730", "the Guardiano", 57, "Anonymous officeholder named as payer."),
        ("cand-11731", "tapestries", 57, "Unidentified textiles hung on the church facade and nearby houses."),
        ("cand-11733", "the houses round about", 57, "Unnamed surrounding buildings hung with tapestries."),
        ("cand-11732", "pictures spread round the inner courtyard", 57, "Unidentified works in the courtyard display."),
        ("cand-11734", "his devotees", 57, "The source's possessive refers to St Bartholomew."),
        ("cand-11736", "exhibitions", 57, "Name-day exhibition series attributed by the source to S. Bartolomeo all'Isola."),
        ("cand-11737", "artists", 57, "Unspecified artists offered display opportunities at the Bergamasque exhibitions."),
        ("cand-11738", "artist of established reputation", 53, "Generic group in Haskell's judgment about lowering one's dignity."),
        ("cand-11739", "the painters in Rome", 53, "Unnamed group said to have pressured for another exhibition."),
        ("cand-11739", "them", 54, "Anaphoric reference to the painters in Rome."),
    ):
        add_mention(cid, surface, line, note)
    add_mention("cand-11355", "Studi Secenteschi", 143,
                "Journal title in Haskell's note 1; citation is recorded as printed, not independently consulted.",
                segment_id=NOTES_SEGMENT_ID)

    mention_updates = {
        "m-chp5-p125-0019": (
            "cand-11729",
            "Named church and courtyard venue; distinct from S. Bartolomeo all’Isola.",
        ),
        "m-chp5-p125-0020": (
            "cand-11735",
            "Site named for less important name-day exhibitions; organizer identity remains unresolved.",
        ),
    }
    for mention_id, (candidate_id, note) in mention_updates.items():
        if mention_id not in mention_by_id:
            raise SystemExit(f"STOP: expected p.125 place mention is missing: {mention_id}")
        mention_by_id[mention_id]["candidate_id"] = candidate_id
        mention_by_id[mention_id]["note"] = note
    if any(m["segment_id"] == BODY_SEGMENT_ID and m["candidate_id"] == "cand-0698" for m in mention_rows):
        raise SystemExit("STOP: a p.125 venue mention still points to the generic Churches index lead")

    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})
    new_ids = {row["candidate_id"] for row in new_candidates}
    existing_candidate_ids = set(candidate_by_id)

    def revise(statement_id, subject, object_, predicate, claim, quote, start, end, relation, qualification,
               mentioned, speaker="Haskell", layer="authorial narrative", extra=None):
        source_span = "\n".join(source_lines[start - 1:end])
        if quote not in source_span:
            raise ValueError(f"quote is not present in its source lines for {statement_id}")
        row = by_id[statement_id]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = object_
        row["predicate"] = predicate
        row["original_quote"] = quote
        q = dict(row.get("qualifiers", {}))
        for key in ("footnote_links", "footnote_link_status"):
            q.pop(key, None)
        q.update({
            "source_line_start": start,
            "source_line_end": end,
            "pdf_physical_page": 6,
            "printed_page_locator": "p.125",
            "claim": claim,
            "speaker": speaker,
            "text_layer": layer,
            "qualification": qualification,
            "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
            "relation_candidate": relation,
            "relation_candidate_note": RELATION_NOTE if relation else NONRELATION_NOTE,
        })
        if extra:
            q.update(extra)
        row["qualifiers"] = q

    revise(
        "st-chp5-p125-three-figures-professional-label", "cand-11712", None,
        "professional_dealer_label_rejected",
        "Haskell says that calling Carlo, Mancini, and Simonelli professional dealers would have offended them.",
        "to call them professional dealers would not only have bitterly offended them", 52, 52, False,
        "The source describes Haskell's assessment of how the three figures would have received the label; it does not record their own response.",
        ["cand-11712"])
    revise(
        "st-chp5-p125-exhibitions-public-contact", "cand-11718", "cand-11719",
        "brought_into_contact_with_by_exhibition_extension",
        "Haskell argues that the gradual extension of exhibitions brought artists into contact with a wider public more effectively than dealers did.",
        "Far more effective than any kind of dealer in bringing the artist into contact with a wider public was the gradual extension of art exhibitions.1",
        53, 53, True,
        "This is Haskell's comparative interpretation. Exhibitions are the stated means; the groups of artists and public remain unnamed.",
        ["cand-0132", "cand-0125", "cand-11718", "cand-11719"],
        extra={"footnote_statement_ids": ["st-chp5-note-p125-n1-citation"]})
    revise(
        "st-chp5-p125-exhibition-religious-calendar", "cand-0132", "cand-11720",
        "held_on_religious_occasions",
        "Haskell says the principal occasions for exhibitions were the many saints' days and processions that characterized seventeenth-century life.",
        "The principal occasions for these were provided by the many saints’ days and processions which were such a feature of seventeenth-century life.",
        53, 53, True,
        "This describes a general pattern, not a dated exhibition on any particular feast day.",
        ["cand-0132", "cand-11720"])
    revise(
        "st-chp5-p125-exhibition-location-and-profile", "cand-0132", None,
        "exhibition_location_unspecified",
        "Haskell says no exact location seems to have been specified for the exhibitions under discussion.",
        "No exact spot seems to have been indicated", 53, 53, False,
        "The source explicitly leaves the site unspecified; no venue is inferred from the later examples.",
        ["cand-0132"])
    revise(
        "st-chp5-p125-exhibitions-usefulness", "cand-0132", "cand-11715",
        "useful_to",
        "Haskell says exhibitions seem to have been useful for the artists he generally encounters, whom he describes as minor landscape or genre specialists and recent arrivals or returnees.",
        "For such men exhibitions seem to have been useful", 53, 53, True,
        "Such men refers to the source-defined profile group. The claim remains qualified by 'seem'. The OCR joins 'we generally'; the printed page reads 'we generally'.",
        ["cand-0132", "cand-11715"])
    revise(
        "st-chp5-p125-sinigaglia-peasant-anecdote", "cand-11721", "cand-11723",
        "inspired_by",
        "Haskell reports hearing of a young peasant boy who decided to take up painting after seeing a stall covered with pictures at the Sinigaglia fair.",
        "we hear of a young peasant boy who decided to take up painting as the result of seeing a stall covered with pictures at the fair of Sinigaglia",
        53, 53, True,
        "The anecdote is explicitly hearsay ('we hear of'); the boy's identity, the fair edition, and later career are not supplied.",
        ["cand-11721", "cand-11723", "cand-11722", "cand-4702"])
    revise(
        "st-chp5-p125-claude-wals-naples", "cand-0767", "cand-11724",
        "saw_at_exhibition",
        "Claude is supposed to have seen unidentified landscapes by Goffredo Wals at a Roman exhibition.",
        "Claude is supposed to have seen landscapes by the Flemish artist Goffredo Wals at an exhibition in Rome",
        53, 53, True,
        "Preserve 'is supposed to have'; the paintings are not individually identified, and the exhibition's venue is unspecified.",
        ["cand-0767", "cand-11724", "cand-2800", "cand-4490"])
    revise(
        "st-chp5-p125-painters-pressure-exhibition", "cand-11739", "cand-11725",
        "pressured_arrangement_of",
        "Haskell says another exhibition, different in aim and organization, was arranged under pressure from painters in Rome.",
        "And another exhibition—though very different in aim and organisation—was actually arranged under pressure from the painters in Rome.",
        53, 53, True,
        "The following 1607 painting-display account is treated as the occasion introduced here, as the narrative sequence indicates; no exact venue or exhibition title is supplied.",
        ["cand-11739", "cand-11725"])
    revise(
        "st-chp5-p125-mantua-1607-display", "cand-11726", "cand-6026",
        "displayed_work_to_satisfy_painters",
        "Haskell says the Duke of Mantua's unnamed agent was forced to satisfy the painters by putting Caravaggio's Death of the Virgin on view.",
        "In 1607 the Duke of Mantua’s agent was forced to satisfy them by putting on view\nCaravaggio’s Death of the Virgin",
        54, 55, True,
        "The acting person is the unnamed agent, not the Duke. 'Them' refers to the painters in Rome; the display occasion is linked to the preceding exhibition passage.",
        ["cand-11726", "cand-6025", "cand-6026", "cand-0547", "cand-11739", "cand-11725"])
    revise(
        "st-chp5-p125-mantua-event-attendance", "cand-11725", "cand-11727",
        "attended_by",
        "Haskell says the 1607 occasion was apparently attended by all the leading artists.",
        "an occasion which was apparently attended by all the leading artists",
        55, 55, True,
        "Preserve 'apparently'; the source does not name the artists or provide a complete roster.",
        ["cand-11725", "cand-11727"])
    revise(
        "st-chp5-p125-bergamasque-exhibition-practice", "cand-6027", "cand-11728",
        "organized",
        "Haskell says the Bergamasque community in Rome sometimes held more organized exhibitions on 24 August.",
        "More organised exhibitions were sometimes held on 24 August by the Bergamasque community in Rome",
        56, 56, True,
        "The passage describes a recurring practice for the community's patron-saint feast; membership and individual event dates are not itemized.",
        ["cand-6027", "cand-11728", "cand-4490"])
    revise(
        "st-chp5-p125-bergamasque-venue-funding", "cand-11728", "cand-11729",
        "held_at",
        "Haskell says the Bergamasque exhibitions took place in the courtyard of the church of S. Bartolomeo.",
        "These took place in the courtyard of the church of S. Bartolomeo",
        57, 57, True,
        "This is a courtyard venue, not the church of S. Bartolomeo all'Isola. The generic index lead cand-0698 is not used as the building endpoint.",
        ["cand-11728", "cand-11729"])
    revise(
        "st-chp5-p125-bergamasque-devotional-purpose", "cand-11728", "cand-6028",
        "dedicated_to",
        "Haskell says the occasion served primarily as a spectacular decorative display in honor of St Bartholomew and his devotees.",
        "As in all Roman exhibitions of this kind, the occasion served primarily to put on a spectacular decorative show in honour of the saint and his devotees.",
        57, 57, True,
        "The source's 'the saint' refers to St Bartholomew named in the preceding sentence. Haskell generalizes about Roman exhibitions of this kind.",
        ["cand-11728", "cand-6028", "cand-11734"])
    revise(
        "st-chp5-p125-bergamasque-decoration-observer", "cand-11731", "cand-11732",
        "impressiveness_compared_by_observer",
        "An unnamed observer could not decide whether the exterior hangings or the pictures spread around the inner courtyard made the greater impression.",
        "an observer confessed that it was hard to decide which was the more impressive: the general-effect created by the hangings outside or the pictures spread round the inner courtyard.",
        57, 57, True,
        "This records the observer's uncertainty, not an assertion that the displays were equally impressive. The printed page reads 'general effect'; S0 OCR has 'general-effect'.",
        ["cand-11731", "cand-11732", "cand-11729"],
        speaker="unnamed observer as reported by Haskell", layer="reported observer judgment")
    revise(
        "st-chp5-p125-bergamasque-chronology", "cand-11728", None,
        "flourishing_by_date_with_start_uncertain",
        "Haskell says the start date of the Bergamasque exhibitions is uncertain, while they were flourishing by 1650.",
        "It is not certain when the exhibitions began, but they were certainly flourishing by 1650.",
        57, 57, False,
        "The source supplies a terminus by which the series flourished, not a founding date.",
        ["cand-11728"])
    revise(
        "st-chp5-p125-bartolomeo-all-isola-exhibitions", "cand-11735", "cand-11736",
        "arranged_name_day_exhibitions",
        "Haskell attributes exhibitions for the saint's name day to S. Bartolomeo all'Isola.",
        "S. Bartolomeo all’Isola arranged exhibitions for the saint’s name day",
        57, 57, True,
        "The source uses the site name as the arranger; the responsible institution is unresolved. Keep this site distinct from the Bergamasque church and series.",
        ["cand-11735", "cand-11736"])
    revise(
        "st-chp5-p125-artists-display-opportunity", "cand-11728", "cand-11737",
        "provided_display_opportunity_for",
        "Haskell says the Bergamasque exhibitions gave artists an opportunity to display their works.",
        "Despite their devotional purpose the exhibitions certainly provided artists with the opportunity to display their works",
        57, 57, True,
        "The comparison beginning 'and were far more dignified' continues in p.126 statement st-chp5-p126-fair-comparison-closed and is not duplicated here.",
        ["cand-11728", "cand-11737"],
        extra={"continued_by_statement_ids": ["st-chp5-p126-fair-comparison-closed"]})
    revise(
        "st-chp5-p125-ghezzi-papers-research-note", None, "cand-6029",
        "archival_material_used_by_author",
        "In a first-person footnote, Haskell says she made extensive use of Giuseppe Ghezzi's papers for the exhibitions at S. Salvatore in Lauro.",
        "For the exhibitions at S. Salvatore in Lauro I have made extensive use of the papers of Giuseppe Ghezzi",
        58, 58, False,
        "This is the author's account of research provenance. Haskell is the speaker, not a candidate endpoint; the archive's current location is stated separately.",
        ["cand-0720", "cand-6029", "cand-1157"],
        layer="authorial footnote continuation",
        extra={"footnote_marker": 1, "footnote_segment": NOTES_SEGMENT_ID, "related_source_lines": [143]})

    new_statements = []

    def add_body(sid, subject, object_, predicate, claim, quote, start, end, relation, qualification,
                 mentioned, **kwargs):
        if sid in by_id:
            raise SystemExit(f"STOP: statement ID already exists: {sid}")
        source_span = "\n".join(source_lines[start - 1:end])
        if quote not in source_span:
            raise ValueError(f"quote is not present in its source lines for {sid}")
        row = make_statement(sid, subject, object_, predicate, claim, quote, start, end,
                             relation, qualification, mentioned, **kwargs)
        new_statements.append(row)
        return row

    add_body(
        "st-chp5-p125-three-figures-discreet-dealing", "cand-11712", None, "discreet_picture_dealing",
        "Haskell says the three figures used the advantages of dealing in pictures shrewdly and discreetly.",
        "advantages, shrewdly yet discreetly, to deal in pictures", 52, 52, False,
        "This is a source-attributed group-level description; it does not identify a particular transaction or counterparty.",
        ["cand-11712", "cand-0125"])
    add_body(
        "st-chp5-p125-three-figures-label-misleading", "cand-11712", None, "professional_dealer_label_misleading",
        "Haskell says calling the three figures professional dealers would give a wholly wrong impression.",
        "but would also give a wholly wrong impression.", 52, 52, False,
        "This is Haskell's assessment of the label, separate from his claim that it would have offended the three figures.",
        ["cand-11712"])
    add_body(
        "st-chp5-p125-corpus-domini-display-association", "cand-6024", "cand-0132", "associated_with_picture_display",
        "Haskell says Corpus Domini was especially associated with picture display, but was not the only such occasion.",
        "The feast of Corpus Domini above all was associated with the display of pictures, but it certainly had no monopoly.",
        53, 53, True,
        "This is a general association; the source does not date a particular exhibition to Corpus Domini.",
        ["cand-6024", "cand-0132"])
    add_body(
        "st-chp5-p125-artists-exhibited-alongside-craftsmen", "cand-11715", "cand-11716", "exhibited_alongside",
        "Haskell says artists probably exhibited indiscriminately alongside other craftsmen or merchants showing wares.",
        "artists probably exhibited indiscriminately with other craftsmen or merchants showing their wares.",
        53, 53, True,
        "Preserve 'probably'; no specific artists, craftsmen, merchants, or exhibition are identified.",
        ["cand-11715", "cand-11716", "cand-0132"])
    add_body(
        "st-chp5-p125-established-artists-dignity", "cand-11738", None, "public_exhibition_dignity_assessed",
        "Haskell asserts that an artist of established reputation would not think of lowering his dignity by exhibiting this way.",
        "Obviously no artist of established reputation would ever think of lowering his dignity in this way",
        53, 53, False,
        "This is Haskell's general judgment, not testimony from a named artist.",
        ["cand-11738", "cand-0132"])
    add_body(
        "st-chp5-p125-exhibition-participant-profile", "cand-11715", None, "participant_profile_described",
        "Haskell says the artists he generally encounters are minor landscape or genre specialists and, above all, painters newly arrived in Rome or returning after a long absence.",
        "those that wegenerally come across are minor specialists in landscape and genre and above all painters newly arrived in Rome or returning after a long absence.",
        53, 53, False,
        "The profile is Haskell's qualified account of artists he encounters, not a complete population list. The printed page reads 'we generally'; S0 OCR joins the words.",
        ["cand-11715"])
    add_body(
        "st-chp5-p125-exhibitions-attracted-connoisseurs", "cand-0132", "cand-11717", "attracted",
        "Haskell says exhibitions seem to have attracted connoisseurs of standing.",
        "and to have attracted connoisseurs of standing.", 53, 53, True,
        "The source qualifies the assessment with 'seem'; no connoisseurs are named.",
        ["cand-0132", "cand-11717"])
    add_body(
        "st-chp5-p125-sinigaglia-stall-at-fair", "cand-11723", "cand-11722", "displayed_at",
        "Haskell places the stall covered with pictures at the fair of Sinigaglia.",
        "seeing a stall covered with pictures at the fair of Sinigaglia", 53, 53, True,
        "The fair edition and the pictures' makers, titles, ownership, and later locations are not given.",
        ["cand-11723", "cand-11722", "cand-4702"])
    add_body(
        "st-chp5-p125-claude-struck-by-wals-landscapes", "cand-0767", "cand-11724", "was_struck_by",
        "Claude is supposed to have been struck by the landscapes of Goffredo Wals shown at a Roman exhibition.",
        "to have been so struck with them", 53, 53, True,
        "This continues the source's 'is supposed to have' qualification; 'them' refers to Wals's unidentified landscapes.",
        ["cand-0767", "cand-11724", "cand-2800", "cand-4490"])
    add_body(
        "st-chp5-p125-claude-studied-under-wals", "cand-0767", "cand-2800", "studied_under",
        "Claude is supposed to have gone to Naples to study under Goffredo Wals after seeing the landscapes.",
        "that he went to study under him in Naples", 53, 53, True,
        "Preserve the source's 'is supposed to have' qualification; Naples is the stated place, with no date supplied.",
        ["cand-0767", "cand-2800", "cand-1722"])
    add_body(
        "st-chp5-p125-claude-wals-career-effect", "cand-0767", None, "career_effect_assessed",
        "Haskell says the move to study under Wals played a decisive part in Claude's career.",
        "a move which played a decisive part in his career.", 53, 53, False,
        "This is Haskell's assessment of the career effect; the underlying episode remains introduced as something Claude is supposed to have done.",
        ["cand-0767", "cand-2800", "cand-1722"])
    add_body(
        "st-chp5-p125-mantua-painting-acquired-by-agent", "cand-6026", "cand-11726", "acquired_by",
        "Haskell says the Duke of Mantua's agent had just bought Caravaggio's Death of the Virgin.",
        "which he had just bought", 55, 55, True,
        "The buyer is the unnamed agent, not the Duke. The purchase is said to have just occurred before the display.",
        ["cand-6026", "cand-11726", "cand-0547"])
    add_body(
        "st-chp5-p125-mantua-painting-bought-for-duke", "cand-11726", "cand-6025", "bought_for",
        "The unnamed agent bought Caravaggio's Death of the Virgin for the Duke of Mantua.",
        "bought for the Duke", 55, 55, True,
        "The source specifies the purchase beneficiary; it does not by itself establish a later transfer or present ownership.",
        ["cand-11726", "cand-6025", "cand-6026"])
    add_body(
        "st-chp5-p125-rubens-advised-mantua-purchase", "cand-2293", "cand-11726", "advised",
        "Haskell says Rubens advised the Duke of Mantua's agent on the purchase of the painting.",
        "on Rubens’s advice", 55, 55, True,
        "The advice is attached to the agent's purchase of Death of the Virgin; the source does not quote the advice or date it separately.",
        ["cand-2293", "cand-11726", "cand-6026", "cand-6025"])
    add_body(
        "st-chp5-p125-mantua-artists-influence-interpretation", "cand-11727", None, "influence_and_emancipation_interpreted",
        "Haskell interprets the artists' apparent attendance as striking evidence of their growing influence and emancipation.",
        "who thus provided striking evidence of their growing influence and emancipation.", 55, 55, False,
        "This is Haskell's interpretation of the reported attendance, not an independently established measure.",
        ["cand-11725", "cand-11727"])
    add_body(
        "st-chp5-p125-bergamasque-exhibition-celebrated-saint", "cand-11728", "cand-6028", "celebrated_feast_of",
        "The Bergamasque exhibitions were held to celebrate the feast day of the community's patron saint, St Bartholomew.",
        "to celebrate the feast day of their patron saint, St Bartholomew.", 56, 56, True,
        "The source supplies 24 August as the recurring date and names the saint; it does not further resolve the saint's identity.",
        ["cand-11728", "cand-6027", "cand-6028"])
    add_body(
        "st-chp5-p125-guardiano-paid-bergamasque-exhibitions", "cand-11730", "cand-11728", "paid_for",
        "Haskell says the Guardiano paid for the Bergamasque exhibitions.",
        "were paid for by the Guardiano.", 57, 57, True,
        "The Guardiano is unnamed; the source does not state the amount or identify the officeholder.",
        ["cand-11730", "cand-11728"])
    add_body(
        "st-chp5-p125-bergamasque-exhibitions-honoured-devotees", "cand-11728", "cand-11734", "honoured",
        "The decorative exhibition was held in honor of St Bartholomew's devotees as well as the saint.",
        "his devotees.", 57, 57, True,
        "The possessive refers to St Bartholomew; the devotees remain an unnamed group.",
        ["cand-11728", "cand-6028", "cand-11734"])
    add_body(
        "st-chp5-p125-tapestries-hung-on-church-facade", "cand-11731", "cand-11729", "hung_on_facade_of",
        "Haskell says tapestries were hung on the facade of the church of S. Bartolomeo.",
        "The façade of the church was hung with tapestries", 57, 57, True,
        "The source names no individual tapestries and the building remains distinct from S. Bartolomeo all'Isola.",
        ["cand-11731", "cand-11729"])
    add_body(
        "st-chp5-p125-tapestries-hung-on-nearby-houses", "cand-11731", "cand-11733", "hung_on",
        "Haskell says the houses around the church were also hung with tapestries.",
        "as were the houses round about", 57, 57, True,
        "The source gives no individual house or textile.",
        ["cand-11731", "cand-11733", "cand-11729"])
    add_body(
        "st-chp5-p125-pictures-displayed-in-courtyard", "cand-11732", "cand-11729", "displayed_in_courtyard_of",
        "Haskell describes pictures spread around the inner courtyard of the church of S. Bartolomeo.",
        "the pictures spread round the inner courtyard.", 57, 57, True,
        "No individual painting or maker is identified.",
        ["cand-11732", "cand-11729"])
    add_body(
        "st-chp5-p125-all-isola-exhibitions-less-important", "cand-11736", "cand-11728", "less_important_than",
        "Haskell assesses the S. Bartolomeo all'Isola exhibitions as less important than the Bergamasque exhibitions.",
        "but they were less important.", 57, 57, True,
        "This is Haskell's relative assessment; no measure of importance is specified.",
        ["cand-11736", "cand-11735", "cand-11728"])
    add_body(
        "st-chp5-note-p125-ghezzi-papers-held-by-museo", "cand-6029", "cand-6030", "held_by",
        "Haskell says Giuseppe Ghezzi's papers were then in the Museo di Roma.",
        "now in the Museo di Roma.", 58, 58, True,
        "This is the location stated in Haskell's footnote; the holding is not independently checked against a museum catalogue.",
        ["cand-6029", "cand-1157", "cand-6030"],
        layer="authorial footnote continuation",
        extra={"footnote_marker": 1, "footnote_segment": NOTES_SEGMENT_ID, "related_source_lines": [143]})

    revise(
        "st-chp5-note-p125-n1-citation", "cand-2962", "cand-11355", "cites",
        "Haskell cites his 1960 article in Studi Secenteschi for the section on exhibitions and its full references.",
        "1 See Haskell, in Studi Secenteschi, i960, for the whole section on exhibitions with full references.",
        143, 143, True,
        "The print reads 1960; S0 OCR reads i960. This records Haskell's citation locator only; the cited article was not independently consulted.",
        ["cand-2962", "cand-11355"],
        layer="authorial footnote citation",
        extra={
            "footnote_marker": 1,
            "footnote_segment": NOTES_SEGMENT_ID,
            "linked_body_statement_ids": [
                "st-chp5-p125-exhibitions-public-contact",
                "st-chp5-p125-exhibition-religious-calendar",
                "st-chp5-p125-exhibition-location-and-profile",
                "st-chp5-p125-exhibitions-usefulness",
                "st-chp5-p125-painters-pressure-exhibition",
                "st-chp5-p125-mantua-1607-display",
                "st-chp5-p125-bergamasque-exhibition-practice",
            ],
        })

    by_id.update({row["statement_id"]: row for row in new_statements})
    new_statement_ids = {row["statement_id"] for row in new_statements}
    if len(by_id) != len(statement_rows) + len(new_statements):
        raise SystemExit("STOP: statement ID collision")
    for row in list(by_id.values()):
        if row.get("segment_id") == BODY_SEGMENT_ID and row["statement_id"] in p125_ids | new_statement_ids:
            qualifiers = row.get("qualifiers", {})
            relation = qualifiers.get("relation_candidate")
            if not isinstance(relation, bool):
                raise SystemExit(f"STOP: p.125 statement remains unclassified: {row['statement_id']}")
            if relation and not (row.get("subject_candidate_id") and row.get("object_candidate_id")):
                raise SystemExit(f"STOP: p.125 relation candidate lacks an endpoint: {row['statement_id']}")
            for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
                if endpoint and endpoint not in existing_candidate_ids:
                    raise SystemExit(f"STOP: unresolved p.125 endpoint {endpoint} in {row['statement_id']}")
            for candidate_id in qualifiers.get("mentioned_candidate_ids", []):
                if candidate_id not in existing_candidate_ids:
                    raise SystemExit(f"STOP: unresolved p.125 mention candidate {candidate_id} in {row['statement_id']}")
    if any(row["candidate_id"] not in existing_candidate_ids for row in new_mentions):
        raise SystemExit("STOP: a new p.125 mention points to an unknown candidate")
    note_row = by_id["st-chp5-note-p125-n1-citation"]
    if note_row["subject_candidate_id"] != "cand-2962" or note_row["object_candidate_id"] != "cand-11355":
        raise SystemExit("STOP: p.125 footnote citation endpoints are incomplete")

    candidate_rows.extend(new_candidates)
    mention_rows.extend(new_mentions)
    outputs = {
        "statements": None,
        "candidates": emit_csv(candidate_fields, candidate_rows, candidate_bom, candidate_text),
        "mentions": emit_csv(mention_fields, mention_rows, mention_bom, mention_text),
    }
    output_lines = []
    for raw_line in statement_text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if line.strip():
            original = json.loads(line)
            updated = by_id.get(original["statement_id"])
            if updated is not None and original["statement_id"] in p125_ids:
                line = json.dumps(updated, ensure_ascii=False)
                ending = ending or newline
        output_lines.append(line + ending)
    if output_lines and not output_lines[-1].endswith(("\n", "\r")):
        output_lines[-1] += newline
    for row in new_statements:
        output_lines.append(json.dumps(row, ensure_ascii=False) + newline)
    outputs["statements"] = (b"\xef\xbb\xbf" if statement_bom else b"") + "".join(output_lines).encode("utf-8")

    all_statement_ids = set(by_id)
    for row in new_statements:
        linked = row.get("qualifiers", {}).get("linked_body_statement_ids", [])
        missing = set(linked) - all_statement_ids
        if missing:
            raise SystemExit(f"STOP: p.125 footnote links missing statements: {sorted(missing)}")
    print("p.125 source, PDF, page image, S0 segment hashes and current table hashes verified")
    print(f"revised existing statements: {len(p125_ids)}; new atomic statements: {len(new_statements)}")
    print(f"new source-bounded candidates: {len(new_candidates)}; new exact mentions: {len(new_mentions)}; corrected venue mentions: 2")
    print(f"statement classifications: {sum(r['qualifiers']['relation_candidate'] is True for r in by_id.values() if r['statement_id'] in p125_ids | new_statement_ids)} relation candidates, "
          f"{sum(r['qualifiers']['relation_candidate'] is False for r in by_id.values() if r['statement_id'] in p125_ids | new_statement_ids)} scalar claims")
    for name, data in outputs.items():
        print(f"{name}: {len(TABLES[name].read_bytes())} bytes -> {len(data)} bytes; sha256={sha(data)}")
    if not args.apply:
        print("dry-run only; no table written")
        return 0

    backups = {name: path.with_name(path.name + BACKUP_SUFFIX) for name, path in TABLES.items()}
    existing_backups = [path.name for path in backups.values() if path.exists()]
    if existing_backups:
        raise SystemExit(f"STOP: recovery copy already exists: {existing_backups}")
    for path in backups.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    written = []
    try:
        for name, path in TABLES.items():
            shutil.copy2(path, backups[name])
        for name, path in TABLES.items():
            temp = path.with_name(path.name + ".tmp-s2-chp5-p125")
            temp.write_bytes(outputs[name])
            temp.replace(path)
            written.append(name)
    except Exception:
        for name in written:
            shutil.copy2(backups[name], TABLES[name])
        raise
    print("written; recovery copies:")
    for name, path in backups.items():
        print(f"  {name}: {path.name}")
    for name, path in TABLES.items():
        print(f"  {path.relative_to(ROOT).as_posix()}: {sha(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
