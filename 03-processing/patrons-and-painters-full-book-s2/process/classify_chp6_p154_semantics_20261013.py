from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md"
SEGMENT = "chp-6:06_CHP-6_sec_i:l91-100"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp6-p154-semantics-20261013"

EXPECTED_HASHES = {
    SOURCE: "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    STATEMENTS: "66ef98e01e2b45f52c1cb426c2f2539b71db5ddf2d71b1400f2e922228d12438",
    CANDIDATES: "4ac129d760b34f153f71cf88b701874d1ce1e7b664638d0fd336d83b9ef8b852",
    MENTIONS: "b260bcdd3463e3dc3d878dfffe4698ed5143cf038cbf838de4a498dcc92511ec",
    COVERAGE: "50e46e6e5397a9269113e0c4c53b1b0fe29c4531dce1b4c03d0e0f2694200cd8",
}

TARGETS = {
    "st-chp6-p154-ariccia-portrait-collection",
    "st-chp6-p154-baldinucci-controversy-and-don-mario",
    "st-chp6-p154-bernin-rebuilds-chigi-palace",
    "st-chp6-p154-canini-and-gaulli-palace-works",
    "st-chp6-p154-chigi-nephews-and-flavio-interest",
    "st-chp6-p154-collection-less-distinguished",
    "st-chp6-p154-don-mario-mei-fresco",
    "st-chp6-p154-flavio-limited-interest-partial",
    "st-chp6-p154-fortune-and-virtue-in-papal-wealth",
    "st-chp6-p154-hostility-to-chigi-family",
    "st-chp6-p154-mei-allegories",
    "st-chp6-p154-palace-facade-interior-contrast",
    "st-chp6-p154-rosa-fortune-painting-completed",
    "st-chp6-p154-rosa-motives-and-rival-interpretation",
}

TRUE_NOTE = (
    "S2 identifies a specific source-grounded relation candidate; qualifications "
    "are retained, and no formal S6 edge is created."
)
FALSE_NOTE = (
    "This is a contextual, scalar, evaluative, or interpretive assertion rather "
    "than a specific entity relation."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields, rows, bom):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    os.replace(temp, path)


def extract(lines, start_line, end_line, first, last):
    text = "\n".join(lines[start_line - 1:end_line])
    start = text.find(first)
    if start < 0:
        raise SystemExit(f"quote start missing L{start_line}-L{end_line}: {first!r}")
    end = text.find(last, start + len(first))
    if end < 0:
        raise SystemExit(f"quote end missing L{start_line}-L{end_line}: {last!r}")
    return text[start:end + len(last)]


def make_candidate(cid, name, kind, detail, line):
    return {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line}",
    }


def make_mention(mid, cid, surface, note, segment_text):
    at = segment_text.find(surface)
    if at < 0 or segment_text.find(surface, at + 1) >= 0:
        raise SystemExit(f"mention anchor must occur once: {mid}: {surface!r}")
    return {"mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
            "surface_form": surface, "start_char": str(at),
            "end_char": str(at + len(surface)), "note": note}


def new_statement(sid, subject, object_, predicate, claim, relation, qualification,
                  mentioned, start, end, first, last, speaker="Haskell",
                  text_layer="authorial historical narrative", extra=None):
    q = {
        "source_line_start": start, "source_line_end": end,
        "printed_page": "154", "pdf_physical_page": 9,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": TRUE_NOTE if relation else FALSE_NOTE,
    }
    if extra:
        q.update(extra)
    return {
        "statement_id": sid, "segment_id": SEGMENT,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": q,
        "original_quote": extract(SOURCE_LINES, start, end, first, last),
        "origin": "book", "source_file": SOURCE_FILE,
    }


def revise(by_id, sid, *, subject, object_, predicate, claim, relation,
           qualification, mentioned, start, end, first, last,
           speaker="Haskell", text_layer="authorial historical narrative",
           extra=None):
    row = by_id[sid]
    q = row.setdefault("qualifiers", {})
    row.update({"subject_candidate_id": subject, "object_candidate_id": object_,
                "predicate": predicate,
                "original_quote": extract(SOURCE_LINES, start, end, first, last)})
    q.update({"source_line_start": start, "source_line_end": end,
              "printed_page": "154", "pdf_physical_page": 9,
              "claim": claim, "speaker": speaker, "text_layer": text_layer,
              "qualification": qualification,
              "mentioned_candidate_ids": mentioned,
              "relation_candidate": relation,
              "relation_candidate_note": TRUE_NOTE if relation else FALSE_NOTE})
    if extra:
        q.update(extra)
    return row


SOURCE_LINES = SOURCE.read_text(encoding="utf-8-sig").splitlines()
SEGMENT_TEXT = "\n".join(SOURCE_LINES[90:100])


def build_outputs():
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")
    if SOURCE_LINES[90].strip() != "[Page 154]":
        raise SystemExit("p.154 page boundary changed")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs in table")
    unset = {sid for sid, row in by_id.items()
             if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset != TARGETS:
        raise SystemExit(f"p.154 unset target set changed: {sorted(unset)}")

    cfields, candidates, cbom = read_csv(CANDIDATES)
    mfields, mentions, mbom = read_csv(MENTIONS)
    vfields, coverage, vbom = read_csv(COVERAGE)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    new_candidate_ids = [f"cand-{n}" for n in range(11995, 12001)]
    new_mention_ids = [
        "m-chp6-p154-jealous-rivals", "m-chp6-p154-painted-animals",
        "m-chp6-p154-canini-ceilings", "m-chp6-p154-gaulli-paintings",
        "m-chp6-p154-antique-statues",
    ]
    if any(cid in candidate_ids for cid in new_candidate_ids) or any(mid in mention_ids for mid in new_mention_ids):
        raise SystemExit("a planned p.154 candidate or mention ID already exists")
    numbers = [int(r["candidate_id"].split("-")[1]) for r in candidates
               if r["candidate_id"].startswith("cand-") and r["candidate_id"].split("-")[1].isdigit()]
    if max(numbers) != 11994:
        raise SystemExit(f"candidate sequence changed: max={max(numbers)}")
    cov = next((r for r in coverage if r["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.154 coverage state: {cov}")

    candidates_to_add = [
        make_candidate("cand-11995", "Unnamed jealous rivals of Salvator Rosa commenting on the painting", "term",
                       "Haskell attributes the potentially subversive reading to jealous rivals but does not identify them or establish that they were artists.", 92),
        make_candidate("cand-11996", "Animal gathering depicted in Rosa's painting (unnamed group)", "term",
                       "Source-defined painted group: pigs, wolves, foxes, wild birds and beasts of prey; it is not a claim about actual animals.", 92),
        make_candidate("cand-11997", "Other ceiling paintings by Giovanni Angelo Canini in the Chigi palace (unnamed group)", "work",
                       "Haskell says there were other ceilings by Canini in the palace; individual subjects and titles are not supplied here.", 97),
        make_candidate("cand-11998", "Mythological paintings and portraits by Gaulli in the Chigi palace (unnamed group)", "work",
                       "Haskell groups unnamed mythological paintings and portraits by Gaulli among the palace contents; no individual titles or attributions are added.", 97),
        make_candidate("cand-11999", "Antique statues in the Chigi palace (unnamed group)", "work",
                       "Haskell reports antique statues in the palace in quantity but does not identify individual sculptures.", 97),
        make_candidate("cand-12000", "Collections of earlier papal nephews (unnamed comparative group)", "work",
                       "The unnamed collections used by Haskell as a comparison for Flavio Chigi's collection; no earlier papal nephews or collections are identified here.", 97),
    ]
    if any(row["candidate_id"] in candidate_ids for row in candidates_to_add):
        raise SystemExit("planned p.154 candidate already exists")

    new_mentions = [
        make_mention(new_mention_ids[0], "cand-11995", "jealous rivals",
                     "Unidentified critics whom Haskell says emphasized the picture's potentially subversive significance.", SEGMENT_TEXT),
        make_mention(new_mention_ids[1], "cand-11996", "pigs, wolves, foxes, wild birds and beasts of prey",
                     "The p.154 continuation completing the animal group depicted in Rosa's picture; the source ends the list here.", SEGMENT_TEXT),
        make_mention(new_mention_ids[2], "cand-11997", "other ceilings",
                     "Unnamed ceiling paintings attributed to Canini in Haskell's palace list.", SEGMENT_TEXT),
        make_mention(new_mention_ids[3], "cand-11998", "mythological paintings and portraits",
                     "Unnamed group of palace works attributed to Gaulli; individual works are not named.", SEGMENT_TEXT),
        make_mention(new_mention_ids[4], "cand-11999", "antique statues",
                     "Unidentified antique statues reported among the palace contents.", SEGMENT_TEXT),
    ]
    old_segment_mentions = [m for m in mentions if m["segment_id"] == SEGMENT]
    for new in new_mentions:
        start, end = int(new["start_char"]), int(new["end_char"])
        for old in old_segment_mentions:
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if start < old_end and old_start < end:
                raise SystemExit(f"new p.154 mention overlaps existing mention: {new['mention_id']} / {old['mention_id']}")
    for i, left in enumerate(new_mentions):
        left_start, left_end = int(left["start_char"]), int(left["end_char"])
        for right in new_mentions[i + 1:]:
            right_start, right_end = int(right["start_char"]), int(right["end_char"])
            if left_start < right_end and right_start < left_end:
                raise SystemExit(f"new p.154 mentions overlap: {left['mention_id']} / {right['mention_id']}")

    # Replace the obsolete family mention on the comparison with the correctly
    # source-bounded, unnamed group of earlier papal nephews' collections.
    old_mentions_by_id = {m["mention_id"]: m for m in mentions}
    earlier = old_mentions_by_id.get("m-chp6-p154-318")
    if not earlier or earlier["candidate_id"] != "cand-6329" or earlier["surface_form"] != "earlier papal nephews":
        raise SystemExit("the p.154 earlier-nephews comparison mention changed")
    earlier.update({"candidate_id": "cand-12000",
                    "note": "Unnamed comparison group of earlier papal nephews' collections; distinct from the Chigi family under Alexander VII."})

    revise(by_id, "st-chp6-p154-ariccia-portrait-collection",
           subject="cand-0671", object_="cand-6328", predicate="hangs-portrait-collection-at-country-house-in-ariccia",
           claim="Haskell says Cardinal Flavio later hung a collection of portraits of thirty-six of Rome's most beautiful women in his country house at Ariccia.", relation=True,
           qualification="The portraits and sitters are unidentified; 'most beautiful' is Haskell's description, not a verified ranking.",
           mentioned=["cand-0671", "cand-6328", "cand-6325", "cand-6324", "cand-4490"], start=97, end=97,
           first="Cardinal Flavio, who, in his country house", last="most beautiful women in Rome3;",
           extra={"footnote_markers": [3], "footnote_link_status": "linked", "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157",
                  "footnote_target_line": 149, "footnote_printed_page": "154",
                  "footnote_citation_statement_ids": ["st-chp6-notes-l149-p154-n3"], "footnote_pending": False})
    revise(by_id, "st-chp6-p154-baldinucci-controversy-and-don-mario",
           subject="cand-2236", object_="cand-6224", predicate="nearly-forced-to-explain-picture-meaning-in-prison",
           claim="Haskell quotes Baldinucci saying the affair became so serious that Rosa was on the point of having to explain the meaning of his picture in prison.", relation=True,
           qualification="This is Baldinucci's account as quoted by Haskell; it does not establish that Rosa was imprisoned or formally charged.",
           mentioned=["cand-0166", "cand-2236", "cand-6224"], start=93, end=94,
           first="The affair assumed such proportions", last="in prison",
           speaker="Haskell quoting Baldinucci", text_layer="nested historical quotation",
           extra={"footnote_markers": [1], "footnote_link_status": "linked", "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157",
                  "footnote_target_line": 147, "footnote_printed_page": "154",
                  "footnote_citation_statement_ids": ["st-chp6-notes-l147-p154-n1-citation"], "footnote_pending": False})
    revise(by_id, "st-chp6-p154-bernin-rebuilds-chigi-palace",
           subject="cand-0671", object_="cand-0312", predicate="employs-bernini-to-build-or-rebuild-palace",
           claim="Haskell says Cardinal Flavio employed Bernini to build, or rather rebuild, the palace in Piazza SS. Apostoli.", relation=True,
           qualification="The author's attribution is preserved; the source does not identify which surviving portions Bernini executed.",
           mentioned=["cand-0671", "cand-0312", "cand-0816", "cand-6212"], start=96, end=96,
           first="Cardinal Flavio was fond of painting", last="the palace in piazza SS. Apostoli")
    revise(by_id, "st-chp6-p154-canini-and-gaulli-palace-works",
           subject="cand-0671", object_="cand-0530", predicate="takes-canini-to-paris-to-draw-scenes",
           claim="Haskell says Cardinal Flavio took Giovanni Angelo Canini with him on a visit to Paris to draw scenes of interest.", relation=True,
           qualification="The source says the visit was humiliating and gives the purpose as drawing scenes; it does not identify completed drawings.",
           mentioned=["cand-0671", "cand-0530", "cand-4653"], start=97, end=97,
           first="whom the Cardinal had taken", last="visit to Paris;")
    revise(by_id, "st-chp6-p154-chigi-nephews-and-flavio-interest",
           subject="cand-6329", object_=None, predicate="chigi-nephews-described-as-lacking-intelligence-or-culture",
           claim="Haskell says neither of the Chigi nephews showed great intelligence or culture.", relation=False,
           qualification="This is Haskell's evaluative characterization of the two named nephews, not an independently assessed trait.",
           mentioned=["cand-6329", "cand-0671", "cand-0664"], start=96, end=96,
           first="Neither of the Chigi nephews", last="intelligence or culture,")
    revise(by_id, "st-chp6-p154-collection-less-distinguished",
           subject="cand-0816", object_="cand-12000", predicate="collection-judged-less-distinguished-than-earlier-papal-nephews-collections",
           claim="Haskell allows that the collection contained some fine pictures but judges it less distinguished than the collections of earlier papal nephews.", relation=False,
           qualification="The comparative collections are not identified; Haskell's aesthetic assessment is retained as his judgment.",
           mentioned=["cand-0816", "cand-12000"], start=97, end=98,
           first="No doubt there were some fine pictures", last="not a distinguished one.4",
           extra={"footnote_markers": [4], "footnote_link_status": "linked", "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157",
                  "footnote_target_line": 150, "footnote_printed_page": "154",
                  "footnote_citation_statement_ids": ["st-chp6-notes-l150-p154-n4"], "footnote_pending": False,
                  "ocr_corrections": [{"source_file": SOURCE_FILE, "source_line": 98,
                      "ocr": "- is not a distinguished one", "print": "is not a distinguished one",
                      "basis": "CHP-6.pdf physical page 9."}]})
    revise(by_id, "st-chp6-p154-don-mario-mei-fresco",
           subject="cand-0671", object_="cand-6326", predicate="commissions-mei-ceiling-fresco-of-fortune-under-virtue",
           claim="At about that time, Cardinal Flavio was commissioning from Bernardino Mei a ceiling fresco of Fortune under the control of Virtue.", relation=True,
           qualification="Haskell calls Mei a second-rate Sienese painter; that is the author's evaluation. The fresco's building, date, and later location are not supplied here.",
           mentioned=["cand-0671", "cand-1633", "cand-6326", "cand-6323", "cand-6327", "cand-0674"], start=95, end=96,
           first="his son, Cardinal Flavio Chigi", last="under the control of Virtue.2",
           extra={"footnote_markers": [2], "footnote_link_status": "linked", "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157",
                  "footnote_target_line": 148, "footnote_printed_page": "154",
                  "footnote_citation_statement_ids": ["st-chp6-notes-l148-p154-n2"], "footnote_pending": False})
    revise(by_id, "st-chp6-p154-flavio-limited-interest-partial",
           subject="cand-0671", object_="cand-0665", predicate="uncle-patronage-reduces-flavio-opportunities-to-employ-first-rate-artists-partial",
           claim="Haskell begins to argue that the extent of Alexander VII's patronage reduced Flavio's opportunities to employ first-rate artists; the sentence continues on p.155.", relation=True,
           qualification="The p.154 source is incomplete at 'first-rate'; p.155 L103 supplies 'artists'. Preserve the cross-page continuation and do not infer which artists Flavio could otherwise have employed.",
           mentioned=["cand-0671", "cand-0665"], start=100, end=100,
           first="The very extent of his uncle\u2019s patronage", last="first-rate",
           extra={"continuation_status": "closed", "continuation_to_segment_id": "chp-6:06_CHP-6_sec_i:l102-110",
                  "continuation_to_fragment": "artists\u2014it is significant that Bernini did not begin to reconstruct the palace",
                  "continuation_resolved_by_segment": "chp-6:06_CHP-6_sec_i:l102-110",
                  "continuation_resolved_by_source_line": 103,
                  "continuation_resolved_by_statement_id": "st-chp6-p155-flavio-limited-employment-complete"})
    revise(by_id, "st-chp6-p154-fortune-and-virtue-in-papal-wealth",
           subject=None, object_="cand-6329", predicate="general-opinion-attributes-papal-family-wealth-to-fortune-not-virtue",
           claim="Haskell says general opinion shared Rosa's view that the riches accruing to the papal family resulted from Fortune alone, with little or no sign of Virtue.", relation=False,
           qualification="This records Haskell's report of contemporary opinion and Rosa's view, not an objective explanation of the family's wealth.",
           mentioned=["cand-2236", "cand-6224", "cand-6323", "cand-6329", "cand-6330", "cand-6331"], start=96, end=96,
           first="The issue was thus a live one", last="no sign of Virtue.",
           speaker="Haskell reporting general opinion and Rosa's view", text_layer="authorial summary of attributed opinion")
    revise(by_id, "st-chp6-p154-hostility-to-chigi-family",
           subject="cand-0665", object_="cand-6329", predicate="perceived-delay-in-summoning-chigi-relatives-linked-to-hostility",
           claim="Haskell says hostility toward Alexander VII's brother Mario and nephews Flavio and Agostino was greater because it had seemed for a time that the Pope had decided not to summon them from Siena.", relation=True,
           qualification="Haskell reports how the situation seemed to observers; this does not establish that Alexander VII had actually decided not to summon them.",
           mentioned=["cand-0665", "cand-0674", "cand-0671", "cand-0664", "cand-5203", "cand-6329"], start=96, end=96,
           first="In fact, the hostility aroused", last="his native Siena.")
    revise(by_id, "st-chp6-p154-mei-allegories",
           subject="cand-1633", object_="cand-1634", predicate="mei-allegory-of-justice-and-peace",
           claim="Haskell lists Justice and Peace among the allegories by Bernardino Mei in the palace.", relation=True,
           qualification="The work is identified by the index sub-entry; the source does not supply a date or specify its exact location within the palace.",
           mentioned=["cand-1633", "cand-1634", "cand-0671"], start=96, end=97,
           first="There were the allegories by Mei", last="Justice and Peace")
    revise(by_id, "st-chp6-p154-palace-facade-interior-contrast",
           subject="cand-0816", object_=None, predicate="contrasts-spectacular-facade-with-disappointing-interior",
           claim="Haskell links Flavio's mediocrity of taste and Bernini's genius to a rare contrast between the palace's spectacular facade and its interior decoration and pictures, which he calls an anti-climax.", relation=False,
           qualification="This is Haskell's aesthetic interpretation. The source does not separately attribute every interior work or feature of the facade to Bernini.",
           mentioned=["cand-0816", "cand-0312", "cand-0671", "cand-4490"], start=96, end=96,
           first="The result of Flavio\u2019s mediocrity of taste", last="extraordinary anti-climax.",
           text_layer="authorial art-historical interpretation")
    revise(by_id, "st-chp6-p154-rosa-fortune-painting-completed",
           subject="cand-6224", object_="cand-11996", predicate="depicts-animal-gathering-completing-p153-description",
           claim="The p.154 continuation identifies the gathering in Rosa's picture as pigs, wolves, foxes, wild birds and beasts of prey.", relation=True,
           qualification="This closes the partial p.153 description; it records represented animals, not actual animals or independently identified species.",
           mentioned=["cand-6224", "cand-11996", "cand-6323"], start=92, end=92,
           first="pigs, wolves, foxes", last="beasts of prey.",
           text_layer="authorial art-historical description",
           extra={"continuation_status": "complete", "continuation_resolved_from_statement_id": "st-chp6-p153-rosa-fortune-painting-partial",
                  "continued_from_segment_id": "chp-6:06_CHP-6_sec_i:l78-89", "continued_from_source_line": 89})
    revise(by_id, "st-chp6-p154-rosa-motives-and-rival-interpretation",
           subject="cand-2236", object_=None, predicate="rosa-had-personal-motives-for-bitterness-not-necessarily-political",
           claim="Haskell says Rosa had his own motives for bitterness, which were not necessarily inspired by the political situation.", relation=False,
           qualification="This is Haskell's qualified account; he does not identify those motives in this passage.",
           mentioned=["cand-2236"], start=92, end=92,
           first="It has already been shown that Rosa", last="inspired by the political situation.")

    additions = [
        new_statement("st-chp6-p154-don-mario-intervenes-for-rosa", "cand-0674", "cand-2236",
            "intervenes-to-prevent-rosa-explaining-picture-in-prison",
            "Baldinucci's quoted account says Don Mario Chigi's intervention prevented Rosa from having to explain the picture's meaning in prison.", True,
            "This is a reported intervention, not a claim that Rosa was imprisoned or formally charged.",
            ["cand-0674", "cand-2236", "cand-6224"], 94, 94,
            "that the painter was on the point", "intervention of Don Mario Chigi",
            speaker="Baldinucci as quoted by Haskell", text_layer="nested historical quotation"),
        new_statement("st-chp6-p154-don-mario-brother-of-pope", "cand-0674", "cand-0665",
            "brother-of-alexander-vii", "Haskell identifies Don Mario Chigi as the Pope's brother.", True,
            "The kinship is explicitly stated in the source.",
            ["cand-0674", "cand-0665"], 94, 94,
            "Don Mario Chigi", "brother"),
        new_statement("st-chp6-p154-don-mario-implicated-in-rosa-interpretation", "cand-0674", "cand-6224",
            "implicated-in-rosas-satirical-interpretation-of-fortune",
            "Haskell says Don Mario was among those most obviously implicated in Rosa's satirical interpretation of Fortune.", True,
            "This is Haskell's reading of the picture's allusions, not evidence of a documented response by Don Mario.",
            ["cand-0674", "cand-2236", "cand-6224", "cand-6323"], 94, 94,
            "one of those most obviously implicated", "satirical interpretation of Fortune.",
            extra={"ocr_corrections": [{"source_file": SOURCE_FILE, "source_line": 94,
                      "ocr": "Fortune. -", "print": "Fortune.", "basis": "CHP-6.pdf physical page 9."}]}),
        new_statement("st-chp6-p154-rosa-picture-allusions-obvious", "cand-6224", None,
            "allusions-described-as-too-obvious-to-pass-unnoticed",
            "Haskell says the picture's allusions were too obvious to pass unnoticed.", False,
            "This is Haskell's interpretive assessment, not a measured claim about every viewer.",
            ["cand-6224"], 92, 92,
            "None the less the allusions of this picture", "too obvious to pass unnoticed,"),
        new_statement("st-chp6-p154-jealous-rivals-call-picture-subversive", "cand-11995", "cand-6224",
            "rivals-point-to-pictures-potentially-subversive-significance",
            "Haskell says jealous rivals quickly pointed to the picture's potentially subversive significance when Rosa exhibited it.", True,
            "The rivals are unnamed and their interpretation is reported by Haskell; potential subversiveness is not treated as established intent.",
            ["cand-11995", "cand-6224", "cand-2236", "cand-6040"], 92, 93,
            "jealous rivals were quick to point", "Rosa exhibited it at S. Giovanni Decollato."),
        new_statement("st-chp6-p154-rosa-exhibits-picture-at-s-giovanni", "cand-2236", "cand-6040",
            "exhibits-picture-at-s-giovanni-decollato",
            "Haskell says Rosa exhibited the picture at S. Giovanni Decollato.", True,
            "This records the exhibition venue stated in the text; it does not add an exhibition date.",
            ["cand-2236", "cand-6040", "cand-6224"], 93, 93,
            "Rosa exhibited it", "S. Giovanni Decollato."),
        new_statement("st-chp6-p154-don-mario-father-of-flavio", "cand-0674", "cand-0671",
            "father-of-cardinal-flavio-chigi", "Haskell identifies Cardinal Flavio Chigi as Don Mario's son.", True,
            "The kinship is explicit; no further family relationships are inferred.",
            ["cand-0674", "cand-0671"], 95, 95,
            "his son, ", "Cardinal Flavio Chigi"),
        new_statement("st-chp6-p154-double-irony-of-don-mario-intervention", "cand-0674", None,
            "haskell-describes-intervention-and-fresco-commission-as-double-irony",
            "Haskell frames Don Mario's intervention and Flavio's nearly contemporaneous fresco commission as a double irony.", False,
            "This is Haskell's rhetorical interpretation of the juxtaposition.",
            ["cand-0674", "cand-0671", "cand-6326"], 95, 95,
            "There is a double irony", "about this time"),
        new_statement("st-chp6-p154-flavio-buys-palace-from-colonna-family", "cand-0671", "cand-4638",
            "buys-palace-from-branch-of-colonna-family-in-1662",
            "Haskell says Cardinal Flavio bought the palace in Piazza SS. Apostoli from a branch of the Colonna family in 1662.", True,
            "The source names only a branch of the family, not the sellers individually; the purchase is not independently verified here.",
            ["cand-0671", "cand-0816", "cand-6212", "cand-4638"], 96, 96,
            "which he bought from a branch of the Colonna family", "in 1662."),
        new_statement("st-chp6-p154-chigi-palace-at-ss-apostoli", "cand-0816", "cand-6212",
            "located-in-piazza-ss-apostoli", "Haskell locates the palace in Piazza SS. Apostoli.", True,
            "The source abbreviates the site as SS. Apostoli; its exact building identity is not resolved beyond the existing candidate.",
            ["cand-0816", "cand-6212"], 96, 96,
            "the palace in", "piazza SS. Apostoli"),
        new_statement("st-chp6-p154-flavio-fond-of-painting", "cand-0671", None,
            "flavio-fond-of-painting", "Haskell says Cardinal Flavio was fond of painting.", False,
            "This is Haskell's brief characterization of Flavio's interest.",
            ["cand-0671"], 96, 96,
            "Cardinal Flavio was", "fond of painting"),
        new_statement("st-chp6-p154-chigi-family-grows-richer-and-overbearing", "cand-6329", None,
            "family-growth-in-wealth-and-overbearing-reputation-accompanied-disappointment",
            "Haskell says that as the traditional pattern developed the family grew richer and more overbearing, while disappointment became intense.", False,
            "This is Haskell's broad social interpretation; the passage gives no measure of wealth or public opinion.",
            ["cand-6329"], 96, 96,
            "As the traditional pattern developed", "disappointment became intense."),
        new_statement("st-chp6-p154-mei-paints-fortune-fresco", "cand-1633", "cand-6326",
            "painted-by-bernardino-mei", "Haskell identifies Bernardino Mei as the painter of the ceiling fresco commissioned by Flavio.", True,
            "The index identifies the work as a Mei fresco; Haskell's 'second-rate' is retained as an attributed judgment, not an accepted quality rating.",
            ["cand-1633", "cand-6326", "cand-0671"], 95, 96,
            "Bernardino Mei, a ceiling fresco", "under the control of Virtue.2"),
        new_statement("st-chp6-p154-mei-youth-rescued-allegory", "cand-1633", "cand-1635",
            "mei-allegory-youth-rescued-from-pleasures-of-venus",
            "Haskell lists Youth rescued from the Pleasures of Venus among Mei's allegories in the palace.", True,
            "The index sub-entry identifies the work; the source gives no date or exact room.",
            ["cand-1633", "cand-1635", "cand-0671"], 96, 97,
            "the allegories by Mei", "Youth rescued from the Pleasures of Venus"),
        new_statement("st-chp6-p154-chigi-palace-has-canini-ceilings", "cand-0816", "cand-11997",
            "contains-other-ceilings-by-canini", "Haskell says the palace contained other ceilings by Giovanni Angelo Canini.", True,
            "The individual ceiling paintings and their subjects are not identified here.",
            ["cand-0816", "cand-11997", "cand-0530"], 97, 97,
            "there were other ceilings", "by Giovanni Angelo Canini"),
        new_statement("st-chp6-p154-chigi-palace-has-gaulli-paintings", "cand-0816", "cand-11998",
            "contains-mythological-paintings-and-portraits-by-gaulli",
            "Haskell says the palace contained unnamed mythological paintings and portraits by Gaulli.", True,
            "The source does not identify individual works or establish the full extent of Gaulli's contribution.",
            ["cand-0816", "cand-11998", "cand-1117"], 97, 97,
            "mythological paintings and portraits", "by Gaulli"),
        new_statement("st-chp6-p154-chigi-palace-has-antique-statues", "cand-0816", "cand-11999",
            "contains-antique-statues", "Haskell says the palace contained antique statues in quantity.", True,
            "No individual statue or provenance is supplied.",
            ["cand-0816", "cand-11999"], 97, 97,
            "antique statues", "in plenty."),
        new_statement("st-chp6-p154-some-fine-pictures-in-collection", "cand-0816", None,
            "haskell-allows-collection-included-some-fine-pictures",
            "Haskell allows that the collection contained some fine pictures.", False,
            "This is Haskell's evaluative allowance and does not identify which pictures he means.",
            ["cand-0816"], 97, 97,
            "No doubt", "some fine pictures,"),
        new_statement("st-chp6-p154-flavio-limited-interest-not-only-cause", "cand-0671", None,
            "limited-interest-not-only-reason-for-collection-lack-of-distinction",
            "Haskell says Flavio's limited interest was not the only reason for the collection's lack of distinction.", False,
            "This sentence introduces a further explanation that continues on p.155.",
            ["cand-0671", "cand-0816"], 100, 100,
            "Flavio\u2019s limited interest", "lack of distinction."),
    ]
    new_ids = {row["statement_id"] for row in additions}
    if len(new_ids) != len(additions) or new_ids & set(by_id):
        raise SystemExit("duplicate or preexisting planned p.154 statement ID")
    for row in additions:
        by_id[row["statement_id"]] = row
    statements = [by_id[row["statement_id"]] for row in statements]
    statements.extend(additions)

    valid_candidates = candidate_ids | set(new_candidate_ids)
    valid_mentions = mentions + new_mentions
    for mention in valid_mentions:
        if mention["candidate_id"] not in valid_candidates:
            raise SystemExit(f"mention points to absent candidate: {mention['mention_id']}")
        if mention["segment_id"] == SEGMENT:
            start, end = int(mention["start_char"]), int(mention["end_char"])
            if SEGMENT_TEXT[start:end] != mention["surface_form"]:
                raise SystemExit(f"mention offsets do not match source text: {mention['mention_id']}")
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    for row in segment_rows:
        q = row.get("qualifiers", {})
        referenced = set(q.get("mentioned_candidate_ids", []))
        if not referenced <= valid_candidates:
            raise SystemExit(f"statement mentions absent candidates: {row['statement_id']}: {sorted(referenced - valid_candidates)}")
        endpoints = {row.get("subject_candidate_id"), row.get("object_candidate_id")} - {None}
        if not endpoints <= valid_candidates:
            raise SystemExit(f"statement has absent endpoint candidate: {row['statement_id']}")
        if q.get("relation_candidate") not in (True, False):
            raise SystemExit(f"p.154 statement remains unclassified: {row['statement_id']}")

    cov["note"] += (
        " p.154 physical page 9 was reviewed against CHP-6.pdf. The fourteen previously unset statements were classified, "
        "and broad entries were split into Rosa's personal motives, rival interpretation, Baldinucci's report, Don Mario's "
        "intervention and kinship, Flavio's palace purchase and commissions, the Mei allegories, palace contents, and "
        "collection assessments. Six source-bounded candidates and five exact mentions were added; the 'earlier papal "
        "nephews' comparison mention was corrected from the Chigi-family candidate to its own unnamed collection group. "
        "The four existing footnote links remain attached to their relevant statements. The partial Flavio patronage sentence "
        "remains linked to p.155; the animal list closes the p.153 painting description. S0 is unchanged; OCR line artifacts "
        "are recorded in S2."
    )

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        CANDIDATES: csv_bytes(cfields, candidates + candidates_to_add, cbom),
        MENTIONS: csv_bytes(mfields, mentions + new_mentions, mbom),
        COVERAGE: csv_bytes(vfields, coverage, vbom),
    }
    summary = {
        "segment": SEGMENT, "previously_unset_classified": len(TARGETS),
        "new_atomic_statements": len(additions), "segment_statement_count_after": len(segment_rows),
        "relation_candidates_in_segment_after": sum(r["qualifiers"].get("relation_candidate") is True for r in segment_rows),
        "non_relational_in_segment_after": sum(r["qualifiers"].get("relation_candidate") is False for r in segment_rows),
        "unset_in_segment_after": sum(r["qualifiers"].get("relation_candidate") is None for r in segment_rows),
        "candidates_added": new_candidate_ids, "mentions_added": new_mention_ids,
        "existing_mention_remapped": "m-chp6-p154-318", "mode": "dry-run",
    }
    if summary["unset_in_segment_after"] or summary["segment_statement_count_after"] != 33:
        raise SystemExit(f"unexpected p.154 segment totals: {summary}")
    return outputs, summary


def main():
    parser = argparse.ArgumentParser(description="Classify and atomize p.154 S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up affected tables and apply the reviewed p.154 batch.")
    args = parser.parse_args()
    outputs, summary = build_outputs()
    summary["mode"] = "apply" if args.apply else "dry-run"
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("backup already exists; refusing to overwrite")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    for path, data in outputs.items():
        atomic_write(path, data)
    print("APPLIED; backups:")
    for backup in backups.values():
        print(backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
