"""Controlled S2 migration for printed p.303; dry-run unless --apply."""
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
P302 = "chp-10:10_CHP-10_intro:l391-400"
P303 = "chp-10:10_CHP-10_intro:l402-409"
P304 = "chp-10:10_CHP-10_intro:l411-421"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = "495f93b64c40367385d1b1489962a7d4395395a56aca6187c5e132f664343488"
BACKUP = ".bak-s2-chp10-p303-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
first, last, PAGE, PHYSICAL = 402, 409, 303, 32
body = "\n".join(src[first - 1:last])
digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
if digest != EXPECTED_SEGMENT_SHA or src[401].strip() != "[Page 303]" or "Ricci’s Use" not in body:
    raise SystemExit(f"p.303 source segment mismatch: {digest}")
line_offsets, offset = {}, 0
for line_no in range(first, last + 1):
    line_offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1

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
if maximum != 9195:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((P302, ("reviewed", "partial")), (P303, ("queued", "pending")),
                      (P304, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] == P303 for row in mentions) or any(row["segment_id"] == P303 for row in statements):
    raise SystemExit("p.303 already has mention or statement rows")

E = {
    "smith": "cand-2440", "sebastiano_ricci": "cand-2183", "marco_ricci": "cand-2153",
    "veronese": "cand-2755", "zanetti": "cand-2838", "algarotti": "cand-0041",
    "carriera": "cand-0588", "george_iii": "cand-1141", "dingley": "cand-0921",
    "palazzo_balbi": "cand-2464", "venice": "cand-3401", "london": "cand-1422",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("ricci_thirteen_compositions", "Thirteen religious and classical compositions by Sebastiano Ricci in Joseph Smith’s collection", "work",
     "A group of thirteen paintings described on p.303; titles and individual identities are not supplied.", 403),
    ("veronese_head_studies", "Studies of heads copied from Paolo Veronese in Joseph Smith’s collection", "work",
     "A series of head studies used by Haskell as evidence for a possible en-bloc acquisition from Sebastiano Ricci’s studio.", 403),
    ("ricci_211_drawings", "211 miscellaneous drawings by Sebastiano Ricci in Joseph Smith’s collection", "work",
     "Haskell says Smith likely acquired this group of drawings, spanning various periods, in the same way as the studio works; the acquisition remains qualified.", 403),
    ("marco_42_paintings", "42 paintings by Marco Ricci in Joseph Smith’s collection", "work",
     "The passage gives a count of 42 paintings but does not identify individual works or how many Smith commissioned.", 404),
    ("marco_150_drawings", "Nearly 150 drawings by Marco Ricci in Joseph Smith’s collection", "work",
     "The passage gives an approximate count; individual drawings and commissioning status are not identified.", 404),
    ("zanetti_1743_book", "Unidentified 1743 book with engravings by Antonio Maria Zanetti related to Marco Ricci", "archive",
     "Haskell says some works were engraved in a book dedicated to Francesco Algarotti; its title, exact contents, and the possessive reference in ‘his own paintings’ remain to be checked against the consolidated note.", 404),
    ("carriera_pastel_portraits", "Rosalba Carriera’s pastel portrait collection in Joseph Smith’s Venetian collection", "work",
     "A body of pastel portraits described as the best-known group of Carriera’s paintings in Venice; individual sitters and works are not enumerated here.", 406),
    ("winter_pastel", "Winter, pastel by Rosalba Carriera in Joseph Smith’s collection", "work",
     "A work called Winter, represented in Smith’s words as a beautiful female covering herself with a pelisse; the passage says Smith commissioned two versions.", 406),
    ("winter_two_versions", "Two versions of Rosalba Carriera’s Winter commissioned by Joseph Smith", "work",
     "The passage distinguishes two versions and says Smith kept the one he preferred and sent the other to an unnamed friend or client; the individual versions are not identified.", 406),
    ("dingley_picture_request", "Unidentified country-girl picture requested from Rosalba Carriera by Robert Dingley", "work",
     "Dingley’s 1735 letter asks for a picture in the style of Winter; the text does not establish that Carriera executed it.", 406),
    ("rialto", "Rialto area in Venice", "place",
     "Used only as the locative reference for Smith’s residence; no more precise building identification is supplied in this passage.", 408),
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
                 "candidate_source_ref": f"{P303}#L{line}"})

newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p303-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    line_start = line_offsets[line]
    line_end = line_start + len(src[line - 1])
    positions, at = [], line_start
    while True:
        at = body.find(surface, at)
        if at < 0 or at + len(surface) > line_end:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": P303, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    ("smith-opening", 403, "Smith", E["smith"], "Closes p.302’s acquisition hypothesis; p.303 states that Smith had not yet formed a distinctive taste."),
    ("ricci-opening", 403, "Ricci", E["sebastiano_ricci"], "Sebastiano Ricci; surname-only reference in the continuation from p.302."),
    ("thirteen-compositions", 403, "thirteen religious and classical compositions", C["ricci_thirteen_compositions"]),
    ("head-studies", 403, "a series of studies of heads copied from", C["veronese_head_studies"]),
    ("veronese", 403, "Veronese", E["veronese"], "Paolo Veronese, named as the source for the copied head studies."),
    ("ricci-artist-coref", 403, "the artist’s studio", E["sebastiano_ricci"], "The artist is Sebastiano Ricci; the passage hypothesizes acquisition from his studio."),
    ("211-drawings", 403, "the 211 miscellaneous drawings", C["ricci_211_drawings"]),
    ("sebastiano-nephew", 404, "Sebastiano’s nephew", E["sebastiano_ricci"], "Names the uncle in the kinship statement about Marco Ricci."),
    ("marco-nephew", 404, "Marco", E["marco_ricci"], "Marco Ricci, identified as Sebastiano’s nephew."),
    ("smith-collection", 404, "Smith’s collection", E["smith"]),
    ("marco-42-paintings", 404, "the 42 paintings", C["marco_42_paintings"]),
    ("marco-nearly-150-drawings", 404, "nearly 150 drawings", C["marco_150_drawings"]),
    ("marco-commissioned-by-him", 404, "him", E["smith"], "Corefers to Smith; the passage says the proportion directly commissioned by him is unclear."),
    ("zanetti", 404, "Antonio Maria Zanetti", E["zanetti"], "The page-index candidate is reused; identity and biographical particulars remain for S3."),
    ("engraving-book", 404, "a book", C["zanetti_1743_book"], "Unidentified publication referenced by footnote 1; detailed note handling remains pending."),
    ("marco-ricci", 404, "Marco Ricci", E["marco_ricci"]),
    ("algarotti", 404, "Francesco Algarotti", E["algarotti"]),
    ("venice", 406, "Venice", E["venice"]),
    ("carriera", 406, "Rosalba Carriera", E["carriera"], "The p.303 index subentry ‘work for Consul Smith’ is reused; S3 will reconcile it with the main Carriera candidate."),
    ("smith-carriera-known", 406, "him", E["smith"], "Corefers to Smith in the statement that Carriera knew him by 1721.", 0),
    ("carriera-early-work", 406, "she", E["carriera"], "Corefers to Rosalba Carriera."),
    ("smith-carriera-work", 406, "him", E["smith"], "Corefers to Smith as the person Carriera worked for by 1723.", 1),
    ("carriera-list", 406, "her name", E["carriera"], "Carriera’s name appears first in Smith’s list of pictures sold to George III."),
    ("smith-picture-list", 406, "his pictures", E["smith"], "The pictures were Smith’s and were listed when he sold them to George III."),
    ("george-sale", 406, "George III", E["george_iii"]),
    ("carriera-payments", 406, "she", E["carriera"], "Corefers to Carriera in the account of payments in 1725, 1726 and 1728.", 1),
    ("smith-payments", 406, "him", E["smith"], "Corefers to Smith as payer.", 2),
    ("smith-carriera-commissions", 406, "Smith", E["smith"], "Smith obtained commissions for Carriera from other Englishmen."),
    ("carriera-pastels", 406, "large collection of pastel portraits", C["carriera_pastel_portraits"]),
    ("carriera-pastels-in-venice", 406, "her paintings", E["carriera"], "Carriera’s paintings; Venice is the location of the comparison."),
    ("winter", 406, "Winter", C["winter_pastel"]),
    ("smith-quoted-description", 406, "Smith’s words", E["smith"]),
    ("winter-description", 406, "Beautiful Female covering herself with a Pelisse", C["winter_pastel"], "Quoted description attributed to Smith by Haskell; the cited letter/source remains pending."),
    ("two-versions", 406, "two versions of this", C["winter_two_versions"], "‘This’ refers to the Winter pastel just named."),
    ("smith-commissioned-versions", 406, "Smith commissioned", E["smith"]),
    ("friend-or-client", 406, "a friend (or client)", C["winter_two_versions"], "Recipient of the second version is anonymous; ‘or client’ is Haskell’s uncertainty."),
    ("rosalba-letter", 406, "Rosalba", E["carriera"], "Carriera is the addressee of the 1735 letter.", 1),
    ("london", 406, "London", E["london"]),
    ("dingley", 406, "Robert Dingley", E["dingley"]),
    ("requested-picture", 406, "a picture ‘of a pretty young country girl", C["dingley_picture_request"], "Quoted request in Dingley’s letter; execution is not established."),
    ("winter-style", 406, "Winter", C["winter_pastel"], "Second reference to Winter in the Dingley letter.", 1),
    ("smith-collection-in-letter", 406, "Mr Smith’s collection", E["smith"]),
    ("smith-asked-not-to-tell", 406, "Mr Smith", E["smith"], "Dingley asks that Smith not be told about his request.", 1),
    ("smith-career-outline", 407, "Smith’s career", E["smith"]),
    ("smith-residence", 408, "the Palazzo Balbi", E["palazzo_balbi"], "Index cue candidate; building identity still requires S3 alignment."),
    ("rialto", 408, "the Rialto", C["rialto"]),
    ("smith-age-residence", 408, "He", E["smith"], "Corefers to Smith; the sentence continues on p.304."),
]
for row in M:
    add_m(*row)

new_s = []


def add_s(local, lo, hi, subject, obj, predicate, claim, qualification, relation=False,
          footnote=None, cross=None, layer="authorial narrative", speaker="Haskell"):
    sid = f"st-chp10-p303-{local}"
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    mentioned = []
    for mention in newm:
        start = int(mention["start_char"])
        line_no = max((n for n, off in line_offsets.items() if off <= start), default=first)
        if lo <= line_no <= hi and mention["candidate_id"] not in mentioned:
            mentioned.append(mention["candidate_id"])
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": PAGE,
                  "pdf_physical_page": PHYSICAL, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        page_map = {P302: 302, P304: 304, NOTES: None}
        pages = [page_map[item] for item in cross if page_map[item] is not None]
        if pages:
            qualifiers["cross_reference_printed_pages"] = pages
    new_s.append({"statement_id": sid, "segment_id": P303, "subject_candidate_id": subject,
                  "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": "\n".join(src[lo - 1:hi]), "source_file": SOURCE_FILE, "origin": "book"})


add_s("ricci-studio-acquisition", 403, 403, E["smith"], C["ricci_thirteen_compositions"],
      "likely_acquired_part_of_ricci_studio_en_bloc",
      "Haskell says the commonplace religious and classical subjects, together with Smith’s ownership of head studies copied from Veronese, strongly suggest that Smith acquired a section of Sebastiano Ricci’s studio en bloc.",
      "This is Haskell’s inference, not a documented transaction; he adds that such a commission would be most unusual.",
      relation=True, cross=[P302], layer="authorial hypothesis")
add_s("ricci-drawings-acquisition", 403, 403, E["smith"], C["ricci_211_drawings"],
      "likely_acquired_211_drawings_in_same_way",
      "Haskell says Smith likely acquired 211 miscellaneous drawings dating from various periods in Ricci’s life in the same way.",
      "The acquisition is explicitly probable rather than documented.", relation=True, cross=[P302], layer="authorial hypothesis")
add_s("marco-kinship", 404, 404, E["marco_ricci"], E["sebastiano_ricci"], "nephew_of",
      "Marco Ricci is identified as Sebastiano Ricci’s nephew.", "The text gives the kinship directly.", relation=True)
add_s("marco-collection", 404, 404, E["smith"], C["marco_42_paintings"],
      "collection_included_works_by_marco_ricci",
      "Marco Ricci was very fully represented in Smith’s collection, which included 42 paintings and nearly 150 drawings.",
      "The counts are as reported by Haskell; the individual objects are not identified.", relation=True)
add_s("marco-commissioning-uncertain", 404, 404, E["smith"], E["marco_ricci"],
      "directly_commissioned_uncertain_share_of_marco_works",
      "Haskell says it is unclear what proportion of Marco Ricci’s paintings and drawings Smith directly commissioned; one drawing is dated 1710, when Haskell considers it most unlikely that the two men knew one another.",
      "Both the commissioning share and the inference about acquaintance are qualified; do not turn the uncertainty into a negative fact.", relation=True, layer="authorial interpretation")
add_s("zanetti-engraving-book", 404, 404, E["zanetti"], C["zanetti_1743_book"],
      "engraved_some_marco_ricci_works_in_1743_book",
      "Some of the works were engraved by Antonio Maria Zanetti in a book dated 1743 and dedicated to Francesco Algarotti.",
      "The book’s exact identity and the antecedent of ‘his own paintings’ remain unresolved pending the note and bibliography.", relation=True,
      footnote=1, layer="authorial narrative")
add_s("zanetti-book-subjects", 404, 404, C["zanetti_1743_book"], C["marco_42_paintings"],
      "included_engraved_subjects_of_roman_ruins_country_life_and_landscapes",
      "The subjects included fantastic Roman ruins, country-life scenes and landscapes, with a cross-reference to Plate 55b.",
      "The passage describes subject matter, not a complete title list; Plate 55b’s caption is a separate source segment.", cross=[P304])
add_s("smith-carriera-early-work", 406, 406, E["smith"], E["carriera"],
      "knew_by_1721_and_worked_for_by_1723",
      "Records cited by Haskell say Carriera knew Smith in 1721 and was working for him by 1723; Haskell infers she was among the first painters he employed.",
      "The source records are cited in footnote 2 and remain pending in the consolidated notes segment.", relation=True,
      footnote=2)
add_s("carriera-sale-to-george", 406, 406, E["smith"], E["george_iii"],
      "sold_pictures_to_george_iii_with_carriera_first_on_list",
      "When Smith sold his pictures to George III, Carriera’s name appeared first on the list.",
      "This is a statement about the list order, not proof that all Carriera works were sold to George III; footnote 2 remains pending.", relation=True,
      footnote=2)
add_s("smith-paid-carriera", 406, 406, E["smith"], E["carriera"], "paid_carriera_in_1725_1726_and_1728",
      "Haskell says Carriera received payments from Smith in 1725, 1726 and 1728.",
      "The cited payment records are not independently checked here; see pending footnote 3.", relation=True, footnote=3)
add_s("smith-arranged-english-commissions", 406, 406, E["smith"], E["carriera"],
      "obtained_commissions_for_carriera_from_other_englishmen",
      "Smith obtained commissions for Carriera from other Englishmen.",
      "The English clients are not named in this passage; the cited source is pending in footnote 3.", relation=True, footnote=3)
add_s("carriera-pastel-group", 406, 406, E["smith"], C["carriera_pastel_portraits"],
      "owned_large_collection_of_carriera_pastel_portraits",
      "Smith’s large collection of pastel portraits formed the best-known group of Carriera’s paintings in Venice.",
      "The comparative wording is Haskell’s; no complete inventory or count is given.", relation=True)
add_s("winter-description", 406, 406, E["carriera"], C["winter_pastel"],
      "winter_recognized_as_carriera_masterpiece_and_described_by_smith",
      "Haskell calls Winter Carriera’s universally recognized masterpiece and quotes Smith’s description of a beautiful female covering herself with a pelisse.",
      "The description is attributed to Smith by Haskell; footnote 4 and the original source remain pending.",
      relation=True, footnote=4, layer="nested quotation", speaker="Haskell quoting Joseph Smith")
add_s("smith-commissioned-winter-versions", 406, 406, E["smith"], C["winter_two_versions"],
      "commissioned_two_versions_kept_preferred_version_and_sent_other_to_friend_or_client",
      "Smith commissioned two versions of Winter, kept the one he preferred and sent the other to an unnamed friend or client.",
      "The recipient and the two physical versions are unidentified; preserve Haskell’s ‘friend (or client)’ uncertainty.",
      relation=True, footnote=5)
add_s("dingley-requested-similar-picture", 406, 406, E["dingley"], C["dingley_picture_request"],
      "requested_picture_in_style_of_winter_from_carriera_in_1735",
      "Writing from London in 1735, Robert Dingley asked Carriera for a picture of a pretty young country girl in the style of Winter and asked that Smith not be told.",
      "The cited letter is mediated through Haskell and its note; the passage does not establish that Carriera completed the requested picture.",
      relation=True, footnote=6, layer="nested correspondence quotation", speaker="Robert Dingley as quoted by Haskell")
add_s("smith-age-palazzo-balbi", 408, 408, E["smith"], E["palazzo_balbi"],
      "aged_55_and_lived_at_palazzo_balbi_near_rialto",
      "Haskell says Smith was then aged 55 and living at the Palazzo Balbi near the Rialto.",
      "The sentence continues on p.304 with the timing of his arrival and is cross-referenced there; building identity remains for S3.",
      relation=True, cross=[P304])

all_ids = cids | {row["candidate_id"] for row in newc}
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < first or q["source_line_end"] > last:
        raise SystemExit(f"statement range outside p.303: {row['statement_id']}")
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"missing statement FK {row['statement_id']} -> {cid}")
    if not q["mentioned_candidate_ids"]:
        raise SystemExit(f"statement has no anchored mention: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

cov[P302]["note"] = cov[P302]["note"].replace(
    "L399’s acquisition hypothesis continues at p.303, so this segment remains partial.",
    "L399’s acquisition hypothesis closes on p.303; the p.302 note excerpts and footnotes 1–6 remain pending in the consolidated notes segment, so this segment remains partial.")
cov[P303].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L403-408",
    "note": "Printed p.303 body checked against CHP-10.pdf physical page 32. Closed p.302’s tentative acquisition account: Haskell infers that Smith acquired part of Sebastiano Ricci’s studio en bloc and likely acquired 211 drawings in the same way. Recorded Marco Ricci’s kinship to Sebastiano, his 42 paintings and nearly 150 drawings in Smith’s collection, the uncertain commissioning share, Zanetti’s 1743 book dedicated to Algarotti, and the described subjects. Recorded Smith’s early patronage of Carriera, payments and commissions, her pastel portrait group and Winter, two versions kept/sent, and Robert Dingley’s 1735 request for a similar picture; the request does not prove execution. Reused page-index candidates for Smith, Sebastiano/Marco Ricci, Veronese, Zanetti, Algarotti, Carriera, George III, Dingley, Palazzo Balbi, Venice and London; added distinct candidates for the named work groups, publication, Winter versions, requested picture and Rialto locator. Scan-only OCR corrections: ‘Ricci’s Use’ reads ‘Ricci’s life’; ‘such’ a commission’ reads ‘such a commission’. L409 and footnotes 1–6 remain for the consolidated notes segment; the last body sentence continues on p.304, so p.303 remains partial."})

summary = {"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
           "segment": P303, "segment_sha256": digest, "new_candidates": len(newc),
           "candidate_ids": [row["candidate_id"] for row in newc],
           "new_mentions": len(newm), "new_statements": len(new_s),
           "coverage": {"p302": cov[P302]["migration_status"], "p303": cov[P303]["migration_status"],
                        "p304": cov[P304]["migration_status"]}}
print(json.dumps(summary, ensure_ascii=False, indent=2))
if sys.argv[-1:] == ["--apply"]:
    for path in (cp, mp, sp, vp):
        backup = Path(str(path) + BACKUP)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(cp, cf, candidates + newc)
    write_csv(mp, mf, mentions + newm)
    write_jsonl(sp, statements + new_s)
    write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
    print("Applied p.303 S2 body migration; p.303 footnotes remain in the consolidated notes segment.")
