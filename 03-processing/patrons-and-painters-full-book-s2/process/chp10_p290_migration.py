"""Controlled S2 migration for printed p.290; dry-run unless --apply is passed."""
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
PREV = "chp-10:10_CHP-10_intro:l229-238"
SEG = "chp-10:10_CHP-10_intro:l240-251"
NEXT = "chp-10:10_CHP-10_intro:l253-266"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "ef64cbecefee43e1f858aefaa615e3603fdd63d1a733cb1718b0b7de09f78f20"
BACKUP = ".bak-s2-chp10-p290-reapply-20261002"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(src[239:251])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != SEG_SHA or src[239].strip() != "[Page 290]":
    raise SystemExit("p.290 source segment hash/page mismatch")
if "theme of Memento Mori." not in src[240] or "The Gierusaleme Liberata" not in body:
    raise SystemExit("p.290 scan-checked text no longer matches source")

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9017:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")), (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "mcswiny": "cand-1466", "bingley": "cand-0376", "devonshire": "cand-0918",
    "richmond": "cand-2194", "marlborough": "cand-8869", "marlborough_monument": "cand-9015",
    "british_worthies": "cand-9013", "glorious_revolution": "cand-9008", "england": "cand-8983",
    "tasso": "cand-2545", "morice": "cand-1702", "fratta": "cand-1076",
    "bologna": "cand-0381", "venice": "cand-2719", "scheme": "cand-9007",
    "capricci": "cand-9017",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
richmond = next(row for row in candidates if row["candidate_id"] == E["richmond"])
if richmond["index_page_range"] != "289, 290, 291" or richmond["sub_entry"] != "and McSwiny's British Worthies":
    raise SystemExit("p.290 Richmond candidate is not the page-specific index entry")

NEW_SPECS = [
    ("memento_mori", "Memento Mori (theme of mortality referenced by Haskell)", "term",
     "The old theme named at the end of Haskell's cross-page comparison; distinguish this theme from the capricci genre candidate.", 241),
    ("client_letter", "Unidentified client letter to McSwiny quoted by Haskell (1729)", "archive",
     "A client letter quoted in Haskell's account; the sender and exact manuscript locator are supplied in note 1, which remains pending in the consolidated notes segment.", 241),
    ("devonshire_altered_version", "Bingley-held version of McSwiny's Duke of Devonshire picture (described as Brutus)", "work",
     "A version that an unnamed client said Lord Bingley had changed into a Brutus and possessed in 1729. Its relationship to the Ricci-collaborated Devonshire monument and other versions remains unresolved pending note 2.", 241),
    ("shovel_person", "Sir Cloudesly Shovel (source spelling; identity pending S3)", "person",
     "Named as the subject of a McSwiny picture in a client's 1729 letter; retain the printed form until identity alignment.", 241),
    ("shovel_altered_version", "Bingley-held version of McSwiny's Sir Cloudesly Shovel picture (described as a Roman Admiral)", "work",
     "A version that an unnamed client said Lord Bingley had changed into a Roman Admiral and possessed in 1729. Note 2's version history remains pending.", 241),
    ("brutus_iconographic_role", "Brutus (iconographic role assigned to the altered Devonshire picture; identity unresolved)", "",
     "The client says the picture was turned into a Brutus. The current taxonomy does not license treating an iconographic role as a specific person or work; preserve the source wording and leave type unresolved.", 241),
    ("roman_admiral_iconographic_role", "Roman Admiral (iconographic role assigned to the altered Shovel picture)", "",
     "The client says the picture was turned into a Roman Admiral. This is an iconographic role, not an independently identified person; preserve the wording and leave type unresolved.", 241),
    ("goodwood", "Goodwood (site of the Duke of Richmond's dining room)", "place",
     "Haskell locates the Duke's dining room and the paintings at Goodwood; the precise building/site identity is not supplied in this passage.", 241),
    ("goodwood_dining_room", "Duke of Richmond's dining room at Goodwood", "place",
     "An interior space in which Haskell says the series hung; keep the room distinct from the works displayed there and from the wider Goodwood site.", 241),
    ("meaning_description", "Unidentified written explanation of the paintings' meanings at Goodwood", "archive",
     "A written description said to have been left for visitors in the Duke of Richmond's dining room; no author, date, or title is supplied here.", 241),
    ("mcswiny_reply_letter", "McSwiny's letter replying to a critic about the monument scheme (quoted by Haskell)", "archive",
     "A letter quoted as McSwiny's reply to a critic. Note 4 identifies its correspondence details, which remain pending in the consolidated notes segment.", 241),
    ("fratta_drawings", "D. M. Fratta's drawings after pictures in McSwiny's monument series (group)", "work",
     "Drawings Fratta was employed to make for the proposed engravings; the passage gives no individual titles and does not establish the later publication of the planned volume.", 246),
    ("subscription_pamphlet", "To the Ladies and Gentlemen of Taste (McSwiny subscription pamphlet)", "archive",
     "A pamphlet Haskell says McSwiny issued sometime in the 1730s, inviting subscriptions for a proposed volume; do not treat the planned volume as completed.", 247),
    ("planned_volume", "McSwiny's proposed volume of fifty copper plates for the British Worthies series", "archive",
     "A publication project described in the subscription pamphlet: 24 sepulchral pieces, 24 inscription plates, a frontispiece, and a title plate. The passage gives proposed dimensions, not evidence that the volume was completed.", 248),
]
newc, C = [], {}
for i, (key, name, kind, detail, line) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{i:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    newc.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                 "index_page_range": "", "suggested_type": kind, "status": "open",
                 "index_source_file": "", "sub_entry": "", "detail": detail,
                 "exclude_reason": "", "candidate_origin": "body-mention",
                 "candidate_source_ref": f"{SEG}#L{line}"})

scheme = next(row for row in candidates if row["candidate_id"] == E["scheme"])
old_scheme_detail = "Proposed commission on behalf of Lord March; p.288 describes intended subjects, political scope, format and division of roles. P.289 reports fifteen pictures begun by 1722 and Haskell's judgement that the series failed its declared purpose; the extent of acquisition is qualified by note 2, pending migration. Not all proposals or intended designs prove completion."
if scheme["detail"] != old_scheme_detail:
    raise SystemExit("McSwiny scheme detail changed")
scheme["detail"] = "Proposed commission on behalf of Lord March; p.288 records intended subjects, political scope, format and division of roles. P.289 reports fifteen pictures begun by 1722 and Haskell's judgement that the series failed its declared purpose; p.290 reports Richmond bought at least ten and Morice the remaining completed works in 1730, and describes a proposed engraving volume. Note 2 qualifies the acquisition list; no claim that every proposal or publication was completed."
capricci = next(row for row in candidates if row["candidate_id"] == E["capricci"])
old_capricci_detail = "Haskell uses capricci for a later-century taste in pictures of crumbling ruins and elegant spectators, marked by romantic melancholy and a picturesque adaptation of the memento mori theme. This is a genre-level reference, distinct from the specifically attributed Capriccio pittoresco candidate."
if capricci["detail"] != old_capricci_detail:
    raise SystemExit("capricci candidate detail changed")
capricci["detail"] = "Haskell uses capricci for a later-century taste in pictures of crumbling ruins and elegant spectators, marked by romantic melancholy and a picturesque adaptation of the separately registered Memento Mori theme. This is a genre-level reference, distinct from the specifically attributed Capriccio pittoresco candidate."

offsets, offset = {}, 0
for line in range(240, 252):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p290-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    positions, at = [], offsets[line]
    line_end = at + len(src[line - 1])
    while True:
        at = body.find(surface, at)
        if at < 0 or at >= line_end:
            break
        positions.append(at - offsets[line])
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = offsets[line] + positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTIONS = [
    ("memento-mori",241,"Memento Mori",C["memento_mori"],"The named theme closing p.289's cross-page sentence; it is separate from the capricci genre."),
    ("client-letter",241,"one client",C["client_letter"],"Unidentified correspondent in a 1729 letter; note 1 remains pending."),
    ("mcswiny-contemporaries",241,"McSwiny",E["mcswiny"],"Subject of the contemporaries discussed in the letter passage."),
    ("other-pictures",241,"your other pictures",E["scheme"],"The client's reference to other pictures in the series; the exact objects are not individually named."),
    ("devonshire",241,"D. of Devonshire",E["devonshire"],"Abbreviated title; do not infer the duke's personal identity."),
    ("shovel",241,"Sir Cloudesly Shovel",C["shovel_person"],"Printed form retained; identity alignment remains S3."),
    ("devonshire-version",241,"the first",C["devonshire_altered_version"],"Refers to the Devonshire picture version in the client's account, reportedly turned into a Brutus."),
    ("shovel-version",241,"the other",C["shovel_altered_version"],"Refers to the Shovel picture version in the client's account, reportedly turned into a Roman Admiral."),
    ("brutus-role",241,"Brutus",C["brutus_iconographic_role"],"Iconographic role only; exact figure identity is not supplied."),
    ("roman-admiral-role",241,"Roman Admiral",C["roman_admiral_iconographic_role"],"Iconographic role only; no individual is named."),
    ("bingley",241,"my Lord Bingley",E["bingley"],"Title reference in the client's reported account."),
    ("richmond-dining",241,"Duke of Richmond",E["richmond"],"Mapped to the index-specific candidate for McSwiny's British Worthies series."),
    ("dining-room",241,"dining-room",C["goodwood_dining_room"],"Interior display space, kept distinct from the paintings and the wider site."),
    ("goodwood",241,"Goodwood",C["goodwood"],"Named site where Haskell locates the dining room."),
    ("written-description",241,"a written description left to explain the meaning",C["meaning_description"],"Unidentified explanatory document; note 3 remains pending."),
    ("great-men",241,"great men",E["british_worthies"],"Haskell's description of the intended commemorative subject group."),
    ("england",241,"England",E["england"],"Country whose great men are the subject of the homage."),
    ("heritage-1688",241,"heritage of 1688",E["glorious_revolution"],"Haskell's phrasing; preserve as the heritage of the Glorious Revolution, not a separate event."),
    ("mcswiny-drawbacks",241,"McSwiny",E["mcswiny"],"Haskell says McSwiny realized the scheme's drawbacks.",1),
    ("mcswiny-reply",241,"he replied to his critic",C["mcswiny_reply_letter"],"Refers to McSwiny's quoted letter; recipient/date details remain pending note 4."),
    ("tasso-work",242,"The Gierusaleme Liberata",E["tasso"],"Printed title form confirmed on the scan; maps to the existing Tasso work sub-entry."),
    ("marlborough",243,"Duke of Malbro",E["marlborough"],"Abbreviated title in McSwiny's quoted letter; personal identity remains for S3."),
    ("marlborough-monument",243,"Monum.t",E["marlborough_monument"],"Abbreviated reference to the McSwiny-series Marlborough monument."),
    ("richmond-purchase",246,"Duke of Richmond",E["richmond"],"Mapped to the page-specific British Worthies index candidate."),
    ("series-paintings",246,"at least ten of the paintings",E["scheme"],"Haskell reports a minimum acquisition count; note 2's list uncertainty remains pending."),
    ("other-versions",246,"other versions of some of them",E["scheme"],"Haskell says other versions also found purchasers; identities are unspecified."),
    ("morice",246,"Sir William Morice",E["morice"],"Named purchaser; note 5 source remains pending."),
    ("mcswiny-1730",246,"McSwiny",E["mcswiny"],"Subject of Haskell's account of the 1730 sale."),
    ("engravings",246,"engravings of the series",E["scheme"],"Planned reproductions of the series, linked to the proposed volume."),
    ("fratta",246,"D. M. Fratta",E["fratta"],"Named Bolognese artist; note 6 remains pending."),
    ("fratta-drawings",246,"drawings of the pictures",C["fratta_drawings"],"Group of drawings commissioned for the planned engravings; no individual titles supplied."),
    ("bologna",247,"Bologna",E["bologna"],"City where the pictures appeared in the source account."),
    ("venice",247,"Venice",E["venice"],"City where the pictures appeared in the source account."),
    ("pamphlet",247,"a pamphlet",C["subscription_pamphlet"],"Printed solicitation Haskell says McSwiny issued in the 1730s."),
    ("pamphlet-title",247,"To the\nLadies and Gentlemen of Taste",C["subscription_pamphlet"],"Quoted address/title of the subscription pamphlet spans a source line break."),
    ("volume",248,"a magnificent volume",C["planned_volume"],"Proposed publication solicited by the pamphlet, not confirmed as completed."),
    ("volume-work-claim",248,"a more compleat Work of the Kind",C["planned_volume"],"Pamphlet's promotional wording; preserve as a quoted claim."),
    ("fifty-plates",248,"fifty copper Plates",C["planned_volume"],"Proposed number of plates."),
    ("sepulchral-pieces",248,"twenty four Sepulchral\nPieces",C["planned_volume"],"One proposed plate category; the source phrase spans a line break and these works are not individually identified here."),
    ("inscription-plates",249,"twenty four Inscription Plates",C["planned_volume"],"One proposed plate category, described as ornamented with emblematic figures."),
    ("emblematic-figures",249,"Emblematical Figures",C["planned_volume"],"Ornamental content of the proposed inscription plates."),
    ("frontispiece",249,"the\nFrontispiece",C["planned_volume"],"Proposed component of the volume; the source phrase spans a line break."),
    ("title-plate",250,"the Title-Plate",C["planned_volume"],"Proposed component of the volume."),
    ("sepulchral-size-reference",250,"the Sepulchral Pieces",C["planned_volume"],"Reference standard for the proposed plate dimensions."),
    ("europe",248,"Europe", "cand-3462", "Part of the pamphlet's promotional comparison."),
]
for item in MENTIONS:
    add_m(*item)

new_s = []


def quote(start, end):
    first = body.find(start)
    if first < 0:
        raise SystemExit(f"quote start absent: {start!r}")
    last = body.find(end, first)
    if last < 0:
        raise SystemExit(f"quote end absent: {end!r}")
    return body[first:last + len(end)]


def add_s(sid, lo, hi, subject, obj, predicate, start, end, claim, qualification,
          mentioned, speaker="Haskell", layer="authorial narrative", relation=False,
          footnote=None, cross=None):
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 290,
                  "pdf_physical_page": 19, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
    if cross:
        qualifiers["cross_reference_segments"] = cross
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


memento_statement = next((row for row in statements if row["statement_id"] == "st-chp10-p289-picturesque-capricci"), None)
if not memento_statement or memento_statement["segment_id"] != PREV:
    raise SystemExit("expected p.289 capricci statement missing")
if memento_statement["object_candidate_id"] != E["capricci"]:
    raise SystemExit("unexpected p.289 capricci endpoint")
memento_statement["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
    memento_statement["qualifiers"].get("mentioned_candidate_ids", []) + [C["memento_mori"]]))

add_s("st-chp10-p290-client-letter-addressed",241,241,C["client_letter"],E["mcswiny"],
      "addressed_to",
      "wrote one client in 1729", "your other pictures",
      "Haskell quotes an unnamed client writing to McSwiny in 1729 about pictures in the series.",
      "The sender and exact letter identification are deferred to note 1 in the consolidated notes segment.",
      [C["client_letter"],E["mcswiny"],E["scheme"]],speaker="Haskell reporting an unidentified client's letter",
      layer="reported correspondence",relation=True,footnote=1)
add_s("st-chp10-p290-client-critique",241,241,C["client_letter"],E["scheme"],
      "client_says_pictures_were_finely_painted_but_defective_in_identifying_the_hero",
      "if I tell you that it has been thought", "defective in that respect [establishing the identity of the hero]",
      "The quoted client says McSwiny's other pictures were finely painted but considered defective in making the hero's identity clear.",
      "This is the client's reported assessment, with Haskell's bracketed clarification; it is not an independent evaluation of every picture.",
      [C["client_letter"],E["scheme"]],speaker="Unidentified client quoted by Haskell",
      layer="reported quotation",footnote=1)
version_quote_start = "I mean those for the late D. of Devonshire"
version_quote_end = "in whose possession they now are."
add_s("st-chp10-p290-devonshire-version-subject",241,241,C["devonshire_altered_version"],E["devonshire"],
      "picture_version_has_duke_of_devonshire_as_subject",
      version_quote_start, version_quote_end,
      "The client identifies one picture as being for the late Duke of Devonshire and says Lord Bingley changed its design into a Brutus.",
      "The report is a client's 1729 account; note 2 will distinguish versions and remains pending.",
      [C["client_letter"],C["devonshire_altered_version"],E["devonshire"],C["brutus_iconographic_role"]],
      speaker="Unidentified client quoted by Haskell",layer="reported quotation",relation=True,footnote=2)
add_s("st-chp10-p290-devonshire-version-brutus",241,241,C["devonshire_altered_version"],C["brutus_iconographic_role"],
      "client_reports_devonshire_picture_turned_into_a_brutus_by_lord_bingley",
      version_quote_start, version_quote_end,
      "The client reports that the Devonshire picture had been turned into a Brutus by Lord Bingley, who then possessed it.",
      "Brutus is retained as an unresolved iconographic role, not identified with a specific historical person.",
      [C["client_letter"],C["devonshire_altered_version"],C["brutus_iconographic_role"],E["bingley"]],
      speaker="Unidentified client quoted by Haskell",layer="reported quotation",relation=True,footnote=2)
add_s("st-chp10-p290-shovel-version-subject",241,241,C["shovel_altered_version"],C["shovel_person"],
      "picture_version_has_sir_cloudesly_shovel_as_subject",
      version_quote_start, version_quote_end,
      "The client identifies the other picture as being for Sir Cloudesly Shovel and says Lord Bingley changed its design into a Roman Admiral.",
      "Retain the printed name and the client's version account; note 2 remains pending.",
      [C["client_letter"],C["shovel_altered_version"],C["shovel_person"],C["roman_admiral_iconographic_role"]],
      speaker="Unidentified client quoted by Haskell",layer="reported quotation",relation=True,footnote=2)
add_s("st-chp10-p290-shovel-version-admiral",241,241,C["shovel_altered_version"],C["roman_admiral_iconographic_role"],
      "client_reports_shovel_picture_turned_into_a_roman_admiral_by_lord_bingley",
      version_quote_start, version_quote_end,
      "The client reports that the Shovel picture was turned into a Roman Admiral by Lord Bingley, who then possessed it.",
      "Roman Admiral is an unresolved iconographic role, not an identified individual.",
      [C["client_letter"],C["shovel_altered_version"],C["roman_admiral_iconographic_role"],E["bingley"]],
      speaker="Unidentified client quoted by Haskell",layer="reported quotation",relation=True,footnote=2)
add_s("st-chp10-p290-devonshire-version-held-bingley",241,241,C["devonshire_altered_version"],E["bingley"],
      "held_by_lord_bingley_according_to_1729_client_letter",
      version_quote_start, version_quote_end,
      "The client says the altered Devonshire picture was in Lord Bingley's possession in 1729.",
      "Possession is recorded as reported; do not convert it into ownership without further evidence.",
      [C["client_letter"],C["devonshire_altered_version"],E["bingley"]],
      speaker="Unidentified client quoted by Haskell",layer="reported quotation",relation=True,footnote=2)
add_s("st-chp10-p290-shovel-version-held-bingley",241,241,C["shovel_altered_version"],E["bingley"],
      "held_by_lord_bingley_according_to_1729_client_letter",
      version_quote_start, version_quote_end,
      "The client says the altered Shovel picture was in Lord Bingley's possession in 1729.",
      "Possession is reported by the client and is distinct from proven ownership.",
      [C["client_letter"],C["shovel_altered_version"],E["bingley"]],
      speaker="Unidentified client quoted by Haskell",layer="reported quotation",relation=True,footnote=2)
add_s("st-chp10-p290-richmond-dining-room",241,241,E["scheme"],C["goodwood_dining_room"],
      "paintings_hung_as_large_decorative_pictures_in_duke_of_richmonds_dining_room_at_goodwood",
      "As large decorative paintings hanging", "they were admirable.",
      "Haskell describes the large decorative paintings as hanging in the Duke of Richmond's dining room at Goodwood, where he says visitors could find a written explanation; he judges them admirable in that setting.",
      "This is Haskell's description and appraisal; the source does not date the installation. The written explanation is registered separately as an unidentified archive item.",
      [E["scheme"],E["richmond"],C["goodwood_dining_room"],C["goodwood"],C["meaning_description"]],
      layer="authorial description and evaluation",relation=True,footnote=3)
add_s("st-chp10-p290-written-description",241,241,C["meaning_description"],E["scheme"],
      "written_description_explained_the_paintings_meaning_for_visitors",
      "where conscientious visitors could find", "left to explain the meaning",
      "Haskell says visitors to the Goodwood dining room could find a written description left to explain the paintings' meaning.",
      "The document's author, title, date and survival are not established here; note 3 is pending.",
      [C["meaning_description"],E["scheme"],C["goodwood_dining_room"]],
      layer="authorial report",footnote=3)
add_s("st-chp10-p290-homage-unsuitable",241,241,E["scheme"],E["glorious_revolution"],
      "haskell_says_pictures_were_unsuitable_as_homage_to_englands_great_men_and_1688_heritage",
      "As a homage to the great men of England", "they were wholly unsuitable.",
      "Haskell judges the pictures wholly unsuitable as a homage to England's great men that might establish a fashion among those who valued the heritage of 1688.",
      "This is Haskell's historical and evaluative interpretation, not a statement that the paintings were commissioned by a formal political group.",
      [E["scheme"],E["british_worthies"],E["england"],E["glorious_revolution"]],
      layer="authorial interpretation")
add_s("st-chp10-p290-mcswiny-realized-drawbacks",241,241,E["mcswiny"],E["scheme"],
      "haskell_says_mcswiny_realized_drawbacks_but_rejected_overly_logical_iconographic_programme",
      "McSwiny himself realised their drawbacks", "destroy the charm that they had.",
      "Haskell says McSwiny recognized the scheme's drawbacks but understood that slavishly following an overly logical iconographic programme would destroy its charm.",
      "This is Haskell's account of McSwiny's understanding; the explanation that follows is a quoted letter, not independent verification.",
      [E["mcswiny"],E["scheme"]],layer="authorial interpretation")
add_s("st-chp10-p290-mcswiny-reply-letter",241,245,C["mcswiny_reply_letter"],E["mcswiny"],
      "authored_by_mcswiny_as_reply_to_a_critic",
      "he replied to his critic", "Statues etc.",
      "The letter quoted by Haskell is presented as McSwiny's reply to a critic about how the monument pictures communicated their subjects.",
      "Recipient and date are deferred to note 4 in the consolidated notes segment; do not infer them from context.",
      [C["mcswiny_reply_letter"],E["mcswiny"],E["scheme"]],speaker="Haskell quoting McSwiny",
      layer="reported correspondence",relation=True,footnote=4)
add_s("st-chp10-p290-single-story-constraint",241,242,E["mcswiny"],E["scheme"],
      "mcswiny_says_narrow_format_allowed_only_one_mans_story_without_triviality",
      "impossible to tell", "The Gierusaleme Liberata.",
      "McSwiny says that in a narrow compass it is impossible to tell more than one man's story without becoming trivial and making the pictures resemble cuts in The Gierusaleme Liberata.",
      "This is McSwiny's quoted explanation; the printed title spelling is retained and the cited letter source remains pending note 4.",
      [E["mcswiny"],E["scheme"],E["tasso"]],speaker="McSwiny quoted by Haskell",
      layer="reported quotation",footnote=4)
add_s("st-chp10-p290-marlborough-monument-example",243,244,E["marlborough_monument"],E["marlborough"],
      "mcswiny_describes_marlborough_monument_as_soldier_visiting_a_great_generals_monument",
      "Monum.t to y.e Memory", "but the visit",
      "McSwiny explains that in the Marlborough monument he makes a soldier with guards visit the monument of a great general, and means nothing beyond the visit.",
      "This is an explanation of intended iconography in McSwiny's letter; the passage does not establish that every pictured event was executed exactly as described.",
      [E["marlborough_monument"],E["marlborough"],E["mcswiny"]],speaker="McSwiny quoted by Haskell",
      layer="reported iconographic explanation",relation=True,footnote=4)
add_s("st-chp10-p290-marlborough-iconographic-limits",244,245,E["marlborough_monument"],E["marlborough"],
      "mcswiny_says_battles_and_abilities_would_require_additional_emblems_and_sculptural_forms",
      "now if I was to represent his battles", "Statues etc.",
      "McSwiny says that representing Marlborough's battles, sieges and abilities as a counsellor would require medallions, medals, reliefs and statues.",
      "This is McSwiny's rationale for limiting the image; it does not state that those additional forms were present in the monument.",
      [E["marlborough_monument"],E["marlborough"],E["mcswiny"]],speaker="McSwiny quoted by Haskell",
      layer="reported iconographic explanation",footnote=4)
add_s("st-chp10-p290-richmond-purchases",246,246,E["scheme"],E["richmond"],
      "duke_of_richmond_bought_at_least_ten_paintings_and_other_versions_found_purchasers",
      "Despite these problems", "other versions of some of them also found purchasers.",
      "Haskell says the Duke of Richmond bought at least ten paintings and that other versions of some pictures also found purchasers.",
      "The minimum count and later acquisition lists are not reconciled here; note 2 remains pending, and purchase is not conflated with later ownership.",
      [E["scheme"],E["richmond"]],relation=True)
add_s("st-chp10-p290-morice-purchase",246,246,E["scheme"],E["morice"],
      "sir_william_morice_bought_remaining_completed_pictures_in_1730",
      "Then in 1730 McSwiny scored", "ones that had been completed.",
      "Haskell says that in 1730 Sir William Morice bought the remaining pictures that had been completed.",
      "The source does not say that incomplete works were purchased; note 5's letter reference remains pending.",
      [E["scheme"],E["morice"],E["mcswiny"]],relation=True,footnote=5)
add_s("st-chp10-p290-engraving-profit",246,246,E["mcswiny"],E["scheme"],
      "mcswiny_planned_engraving_series_for_additional_profit",
      "he had in any case decided from the first", "issuing engravings of the series",
      "Haskell says McSwiny had decided from the outset that issuing engravings of the series could bring further profits.",
      "This records the reported plan and motive, not proof of the number of engravings actually issued.",
      [E["mcswiny"],E["scheme"]],layer="authorial report")
add_s("st-chp10-p290-fratta-drawings",246,247,C["fratta_drawings"],E["fratta"],
      "mcswiny_employed_d_m_fratta_to_make_drawings_of_series_pictures_in_bologna_and_venice",
      "for this purpose he employed", "Bologna and Venice.",
      "Haskell says McSwiny employed the Bolognese artist D. M. Fratta to make drawings of the pictures as they appeared in Bologna and Venice.",
      "The passage describes the commission and intended use for engravings; it supplies no individual drawing titles. Note 6 remains pending.",
      [C["fratta_drawings"],E["fratta"],E["mcswiny"],E["scheme"],E["bologna"],E["venice"]],
      relation=True,footnote=6)
add_s("st-chp10-p290-subscription-pamphlet",247,248,C["subscription_pamphlet"],C["planned_volume"],
      "mcswiny_issued_titled_pamphlet_in_1730s_inviting_subscriptions_for_proposed_volume",
      "Some time in the 1730s", "a magnificent volume",
      "Haskell says that sometime in the 1730s McSwiny issued a pamphlet addressed To the Ladies and Gentlemen of Taste, inviting subscriptions for a proposed volume.",
      "The decade is approximate; the pamphlet and proposed volume are distinct records, and the passage does not establish that the volume was published.",
      [C["subscription_pamphlet"],C["planned_volume"],E["mcswiny"]],speaker="Haskell reporting and quoting McSwiny",
      layer="authorial report with quoted pamphlet title")
add_s("st-chp10-p290-proposed-volume-description",248,248,C["planned_volume"],None,
      "pamphlet_promotes_proposed_volume_as_more_complete_than_prior_european_publications",
      "a more compleat Work of the Kind", "any part of Europe",
      "The pamphlet describes the proposed volume as a more complete work of its kind than any previously published in Europe.",
      "This is promotional wording quoted by Haskell, not an independently verified comparison or proof of publication.",
      [C["planned_volume"],C["subscription_pamphlet"],"cand-3462"],speaker="McSwiny's pamphlet quoted by Haskell",
      layer="reported promotional claim")
add_s("st-chp10-p290-proposed-volume-contents",248,250,C["planned_volume"],None,
      "planned_fifty_plate_volume_comprised_24_sepulchral_24_inscription_frontispiece_and_title_plate",
      "fifty copper Plates", "the Title-Plate;",
      "The proposed volume was to contain fifty copper plates: twenty-four sepulchral pieces, twenty-four inscription plates ornamented with emblematic figures, a frontispiece and a title plate.",
      "These are announced components of a planned publication, not evidence that all plates were completed or issued.",
      [C["planned_volume"]],speaker="McSwiny's pamphlet quoted by Haskell",
      layer="reported publication specification")
add_s("st-chp10-p290-proposed-volume-dimensions",250,251,C["planned_volume"],None,
      "planned_plates_same_size_two_feet_two_inches_high_by_one_foot_five_inches_wide",
      "all of the same size", "Breadth.",
      "The pamphlet says the plates were to share the sepulchral pieces' size: two feet two inches high and one foot five inches wide.",
      "These are proposed dimensions, not measurements of surviving plates.",
      [C["planned_volume"]],speaker="McSwiny's pamphlet quoted by Haskell",
      layer="reported publication specification")

cov[PREV]["note"] = "P.289 L232's capricci/picturesque sentence closes at p.290 L241 with 'theme of Memento Mori'; that term is now separately registered as cand-9018 and linked to the p.289 statement. P.289 note excerpts L233-238 remain pending in consolidated notes L543-544."
cov[SEG].update({"disposition":"reviewed","migration_status":"complete","source_line_ranges":"L241-251",
                 "note":"Printed p.290 was checked against CHP-10.pdf physical page 19. Closed p.289's Memento Mori sentence at L241. Recorded the 1729 client letter and critique with the two altered picture versions and Lord Bingley's reported possession; Haskell's Goodwood display appraisal and the written meaning-description; his judgement about the heritage of 1688; McSwiny's quoted iconographic rationale for the Marlborough monument; reported acquisitions by Richmond and Morice; and the engraving/drawing and proposed subscription volume project. Iconographic roles Brutus and Roman Admiral remain type-undecided; names, version identities, purchase claims and footnote evidence retain attribution and pending-note limits. The printed title reads 'The Gierusaleme Liberata'; OCR form matches the scan. Notes 1-6 remain in the separate consolidated notes segment and are not duplicated in this body segment."})
cov[NEXT]["note"] = "Next source-order segment is printed p.291 at L253-266; p.290 body segment L241-251 is complete. P.289 note excerpts still await consolidated notes L543-544."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"new_candidates":len(newc),"new_candidate_ids":[row["candidate_id"] for row in newc],
                  "updated_candidates":[E["scheme"],E["capricci"]],"new_mentions":len(newm),
                  "new_statements":len(new_s),"coverage":{"p289":cov[PREV]["migration_status"],
                  "p290":cov[SEG]["migration_status"],"p291":cov[NEXT]["migration_status"]}},ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup=Path(str(path)+BACKUP)
        if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.290 S2 migration; p.290 body is complete, with its notes tracked in the consolidated notes segment.")
