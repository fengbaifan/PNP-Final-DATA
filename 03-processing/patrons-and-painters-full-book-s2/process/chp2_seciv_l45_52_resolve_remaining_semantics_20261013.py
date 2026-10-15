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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l45-52"
NOTES_SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l190-245"
SEGMENT_SHA = "8cde8f28190a93455f5efa9d6dd2c56c37633da7f376e805fcdb2bd660dd0fe5"
NOTES_SEGMENT_SHA = "5dd2839d3e713ca4795b2bfd4de98120305a38026d0d41ffcc7c84e19fbcfd2a"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l45-52-semantics-20261013"
EXPECTED = {
    "book-statements.jsonl": "b694d4d636e43531432e1aaceacba4b908cecaffefb97490892d9b263b049963",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "6a21a1fbe8b92345b3cf98d6a98c524ad48fc79e9bd55d3afba9ab3c5c18ee19",
}
UNSET_IDS = {
    "st-chp2-seciv-l45-52-others-excuse-taddeo",
    "st-chp2-seciv-l45-52-prefecture-revived",
    "st-chp2-seciv-l45-52-taddeo-brawl-and-murder",
    "st-chp2-seciv-l45-52-taddeo-intellectual-resources",
    "st-chp2-seciv-l45-52-taddeo-made-public-figure",
    "st-chp2-seciv-l45-52-taddeo-sugar-and-honey-description",
    "st-chp2-seciv-l45-52-taddeo-withdrawal-or-violence",
}
NEW_MURDER_ID = "st-chp2-seciv-l45-52-taddeo-murder-involvement"
NEW_DETERIORATION_ID = "st-chp2-seciv-l45-52-taddeo-character-deterioration"
NEW_PISANO_CITATION_ID = "st-chp2-seciv-l190-245-citation-85"
NEW_RENIER_MENTION_ID = "m-chp2-seciv-l190-245-0149"
OLD_BRAWL_QUOTE = "Within three years he was involved in a street brawl and a savage murder."
BRAWL_QUOTE = "Within three years he was involved in a street brawl."
PARDON_QUOTE = (
    "A papal pardon, phrased so widely that it covered any interpretation put on the events that had occurred, settled that,"
)
DETERIORATION_QUOTE = "but the deterioration in lais character continued."
INTELLECT_QUOTE = (
    "intellectual resources of his elder and younger brothers and he was quite unable to cope with the overpowering "
    "position that his uncle planned for him."
)
PUBLIC_FIGURE_QUOTE = "Against his inclination he was turned into a public figure."
PREFECTURE_QUOTE = "The Prefecture of Rome was virtually obsolescent. It was now revived in all its authority."
WITHDRAWAL_QUOTE = (
    "Torn between his natural laziness and the arrogance that was expected of him, Taddeo alternatively backed out or resorted to violence."
)
OTHERS_QUOTE = (
    "yet on every such occasion there was someone to comment that it was not really his fault and that his only ambition was to live quietly—if splendidly."
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def add_unique(values: list[str], additions: list[str]) -> list[str]:
    return list(dict.fromkeys([*values, *additions]))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve the remaining Taddeo claims in CHP-2 section IV L45-52, split event and character claims, "
            "and repair the p.47 footnote evidence links."
        )
    )
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")
    segment_by_id = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    segment = segment_by_id.get(SEGMENT_ID)
    notes_segment = segment_by_id.get(NOTES_SEGMENT_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected print-p.47 source segment fingerprint changed")
    if (
        not notes_segment
        or notes_segment.get("sha256") != NOTES_SEGMENT_SHA
        or notes_segment.get("asset_sha256") != SOURCE_SHA
    ):
        raise SystemExit("protected section IV notes segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(statement_by_id) != len(statements) or len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise SystemExit("duplicate statement, candidate, or mention IDs")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected L45-52 unset statement set: {sorted(unset)}")
    if NEW_MURDER_ID in statement_by_id or NEW_DETERIORATION_ID in statement_by_id or NEW_PISANO_CITATION_ID in statement_by_id:
        raise SystemExit("one or more planned statement IDs already exist")
    if NEW_RENIER_MENTION_ID in mention_by_id:
        raise SystemExit("planned Renier Zeno mention ID already exists")
    required_statements = {
        "st-chp2-seciv-l45-52-papal-pardon-and-character-deterioration",
        "st-chp2-seciv-l45-52-taddeo-age-and-election-context",
        "st-chp2-seciv-l31-43-taddeo-characterization",
        "st-chp2-seciv-l190-245-citation-19",
        "st-chp2-seciv-l190-245-citation-20",
        "st-chp2-seciv-l190-245-citation-21",
        "st-chp2-seciv-l190-245-venetian-reports-taddeo",
        "st-chp2-seciv-l190-245-taddeo-moral-claim-disputed",
        "st-chp21-bib-l928-983-entry-27",
    }
    if required_statements - statement_by_id.keys():
        raise SystemExit(f"required body or note statements missing: {sorted(required_statements - statement_by_id.keys())}")
    needed_candidates = {"cand-0239", "cand-0209", "cand-4217", "cand-4265", "cand-4641", "cand-4642", "cand-4643", "cand-4645", "cand-4871", "cand-11419"}
    if not needed_candidates.issubset(candidate_by_id):
        raise SystemExit(f"required candidate IDs missing: {sorted(needed_candidates - candidate_by_id.keys())}")
    if candidate_by_id["cand-4871"].get("canonical_name") != "Giuho Pisano (1921), bibliographic reference; title and identity unresolved":
        raise SystemExit("the protected p.47 Pisano candidate has changed")
    if not any(m.get("segment_id") == NOTES_SEGMENT_ID and m.get("candidate_id") == "cand-4265" for m in mentions):
        if NEW_RENIER_MENTION_ID in mention_by_id:
            raise SystemExit("unexpected Renier Zeno note mention state")
    source_text = SOURCE.read_text(encoding="utf-8-sig")
    for quote in (OLD_BRAWL_QUOTE, PARDON_QUOTE, INTELLECT_QUOTE, PUBLIC_FIGURE_QUOTE, PREFECTURE_QUOTE, WITHDRAWAL_QUOTE, OTHERS_QUOTE):
        if quote not in source_text:
            raise SystemExit(f"protected S0 quote no longer matches the source: {quote}")
    body_coverage_rows = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    note_coverage_rows = [row for row in coverage if row.get("segment_id") == NOTES_SEGMENT_ID]
    if len(body_coverage_rows) != 1 or len(note_coverage_rows) != 1:
        raise SystemExit("expected exactly one body and one notes coverage row")

    brawl = statement_by_id["st-chp2-seciv-l45-52-taddeo-brawl-and-murder"]
    brawl["object_candidate_id"] = "cand-4641"
    brawl["predicate"] = "involved_in_reported_event"
    brawl["original_quote"] = BRAWL_QUOTE
    brawl_q = brawl.setdefault("qualifiers", {})
    brawl_q["claim"] = "Haskell says Taddeo was involved in a street brawl within three years of Urban VIII becoming Pope."
    brawl_q["qualification"] = (
        "No exact date or other participant is supplied. The adjacent savage murder is recorded separately; the source does not establish whether it was the same incident."
    )
    brawl_q["relation_candidate"] = True
    brawl_q["relation_candidate_note"] = "The source explicitly links Taddeo to the existing open street-brawl event candidate."
    brawl_q["mentioned_candidate_ids"] = ["cand-0239", "cand-4641"]
    brawl_q["related_statement_ids"] = [NEW_MURDER_ID]
    brawl_q.pop("event_candidate_ids", None)

    murder = {
        "statement_id": NEW_MURDER_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0239",
        "object_candidate_id": "cand-4642",
        "predicate": "involved_in_reported_event",
        "qualifiers": {
            "source_line_start": 48,
            "source_line_end": 48,
            "claim": "Haskell says Taddeo was involved in a savage murder within three years of Urban VIII becoming Pope.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": 47,
            "pdf_physical_page": 32,
            "qualification": "The source does not specify Taddeo's precise role or date, and does not establish whether this and the street brawl were one incident.",
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly links Taddeo to the existing open savage-murder event candidate.",
            "mentioned_candidate_ids": ["cand-0239", "cand-4642"],
            "related_statement_ids": ["st-chp2-seciv-l45-52-taddeo-brawl-and-murder"],
        },
        "original_quote": OLD_BRAWL_QUOTE,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }

    pardon = statement_by_id["st-chp2-seciv-l45-52-papal-pardon-and-character-deterioration"]
    if pardon.get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("the protected papal-pardon relation classification changed")
    pardon["predicate"] = "pardon_concerning_reported_events_of_person"
    pardon["original_quote"] = PARDON_QUOTE
    pardon_q = pardon.setdefault("qualifiers", {})
    pardon_q["claim"] = "Haskell says a broadly worded papal pardon settled the matter concerning the reported brawl and murder involving Taddeo."
    pardon_q["qualification"] = (
        "The pronoun 'that' refers to the preceding incidents. The pardon’s date, issuing authority, and precise legal scope are not supplied; "
        "the two incidents remain distinct candidates without an asserted identity link."
    )
    pardon_q["relation_candidate_note"] = (
        "The source links Taddeo's reported incidents to an unnamed papal pardon, represented by the existing open archive candidate; it does not name the issuing authority."
    )
    pardon_q["mentioned_candidate_ids"] = ["cand-0239", "cand-4643", "cand-4641", "cand-4642"]
    pardon_q["related_statement_ids"] = ["st-chp2-seciv-l45-52-taddeo-brawl-and-murder", NEW_MURDER_ID]
    pardon_q.pop("footnote_marker", None)
    pardon_q.pop("footnote_refs", None)
    pardon_q.pop("footnote_segment", None)

    deterioration = {
        "statement_id": NEW_DETERIORATION_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0239",
        "object_candidate_id": None,
        "predicate": "character_deterioration_assessment_reported",
        "qualifiers": {
            "source_line_start": 48,
            "source_line_end": 48,
            "claim": "Haskell says Taddeo's character continued to deteriorate.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": 47,
            "pdf_physical_page": 32,
            "footnote_marker": 2,
            "footnote_segment": NOTES_SEGMENT_ID,
            "footnote_refs": [{"marker": 2, "segment_id": NOTES_SEGMENT_ID, "source_line": 206}],
            "qualification": "This is Haskell's evaluative moral characterization. The printed page reads 'his'; S0 OCR reads 'lais'.",
            "relation_candidate": False,
            "relation_candidate_note": "This is an authorial characterization of Taddeo, not an entity relation.",
            "mentioned_candidate_ids": ["cand-0239"],
            "related_statement_ids": ["st-chp2-seciv-l190-245-taddeo-moral-claim-disputed", "st-chp2-seciv-l190-245-citation-20", "st-chp2-seciv-l190-245-citation-21"],
        },
        "original_quote": DETERIORATION_QUOTE,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }

    others = statement_by_id["st-chp2-seciv-l45-52-others-excuse-taddeo"]
    others["subject_candidate_id"] = "cand-0239"
    others["object_candidate_id"] = None
    others["predicate"] = "exculpatory_comments_and_quiet_ambition_reported"
    others["original_quote"] = OTHERS_QUOTE
    others_q = others.setdefault("qualifiers", {})
    others_q["claim"] = (
        "Haskell says an unnamed person repeatedly excused Taddeo and described his ambition as living quietly, if splendidly."
    )
    others_q["attribution"] = (
        "The body leaves the commenter unnamed. Footnote 3 cites reports from Venetian ambassadors and says they were often embroiled with Taddeo, but does not identify them as the commenters."
    )
    others_q["relation_candidate"] = False
    others_q["relation_candidate_note"] = (
        "The claimed comments have no named agent; the Venetian ambassadorial report is recorded separately in the related footnote statement."
    )
    others_q["mentioned_candidate_ids"] = ["cand-0239"]
    others_q["related_statement_ids"] = ["st-chp2-seciv-l190-245-venetian-reports-taddeo"]
    others_q.pop("open_endpoint_reason", None)

    prefecture = statement_by_id["st-chp2-seciv-l45-52-prefecture-revived"]
    prefecture["original_quote"] = PREFECTURE_QUOTE
    prefecture_q = prefecture.setdefault("qualifiers", {})
    prefecture_q["claim"] = "Haskell says the Prefecture of Rome was virtually obsolescent and its authority was revived."
    prefecture_q["qualification"] = (
        "This is an institutional status-change claim. The passive sentence does not name the reviving authority; the adjacent Urban VIII context is not used to infer an agent."
    )
    prefecture_q["relation_candidate"] = False
    prefecture_q["relation_candidate_note"] = (
        "The office's historical status is preserved as a source claim, but no second entity endpoint or named reviver is established."
    )
    prefecture_q["mentioned_candidate_ids"] = ["cand-4645"]

    intellect = statement_by_id["st-chp2-seciv-l45-52-taddeo-intellectual-resources"]
    intellect["original_quote"] = INTELLECT_QUOTE
    intellect_q = intellect.setdefault("qualifiers", {})
    intellect_q["claim"] = "Haskell says Taddeo lacked the intellectual resources of his elder and younger brothers and could not cope with the position his uncle planned for him."
    intellect_q["qualification"] = (
        "This completes the cross-page sentence begun in L38. The comparison is Haskell's characterization; the brothers remain unnamed and are not collapsed into an inferred group candidate."
    )
    intellect_q["relation_candidate"] = False
    intellect_q["relation_candidate_note"] = "This is an evaluative comparison of Taddeo's personal capacity, not an entity relation."
    intellect_q["mentioned_candidate_ids"] = ["cand-0239"]
    intellect_q["related_statement_ids"] = ["st-chp2-seciv-l31-43-taddeo-characterization"]
    intellect_q.pop("continuation_segment_id", None)
    intellect_q.pop("continuation_source_line", None)
    intellect_q.pop("continuation_to_statement_id", None)

    public_figure = statement_by_id["st-chp2-seciv-l45-52-taddeo-made-public-figure"]
    public_figure["original_quote"] = PUBLIC_FIGURE_QUOTE
    public_q = public_figure.setdefault("qualifiers", {})
    public_q["claim"] = "Haskell says Taddeo was turned into a public figure against his inclination."
    public_q["qualification"] = "The source does not identify the agent who turned him into a public figure; the claim describes a change of status."
    public_q["relation_candidate"] = False
    public_q["relation_candidate_note"] = "This is a status characterization of Taddeo, not a relation to an identified agent or institution."
    public_q["mentioned_candidate_ids"] = ["cand-0239"]
    public_q["related_statement_ids"] = [NEW_PISANO_CITATION_ID]

    sugar = statement_by_id["st-chp2-seciv-l45-52-taddeo-sugar-and-honey-description"]
    sugar["subject_candidate_id"] = "cand-4265"
    sugar["object_candidate_id"] = "cand-0239"
    sugar["predicate"] = "described_as_characterization_reported"
    sugar_q = sugar.setdefault("qualifiers", {})
    sugar_q["claim"] = "Haskell reports that Renier Zeno described Taddeo as 'all sugar, all honey' when Urban VIII became Pope."
    sugar_q["attribution"] = (
        "The body is passive; footnote 1 cites Barozzi e Berchet, I, p. 153, and identifies Renier Zeno (1621-1623). The cited page was not independently read."
    )
    sugar_q["relation_candidate"] = True
    sugar_q["relation_candidate_note"] = (
        "Footnote 1 attributes the quoted characterization to a source associated with Renier Zeno; keep the citation-based attribution and do not claim independent verification."
    )
    sugar_q["mentioned_candidate_ids"] = ["cand-4265", "cand-0239"]
    sugar_q["related_statement_ids"] = ["st-chp2-seciv-l190-245-citation-19"]
    sugar_q.pop("open_endpoint_reason", None)

    withdrawal = statement_by_id["st-chp2-seciv-l45-52-taddeo-withdrawal-or-violence"]
    withdrawal["original_quote"] = WITHDRAWAL_QUOTE
    withdrawal_q = withdrawal.setdefault("qualifiers", {})
    withdrawal_q["claim"] = (
        "Haskell characterizes Taddeo as alternating between backing out and resorting to violence amid natural laziness and expected arrogance."
    )
    withdrawal_q["qualification"] = "The motives and character traits are Haskell's interpretation, not independently verified facts."
    withdrawal_q["relation_candidate"] = False
    withdrawal_q["relation_candidate_note"] = "This is an authorial characterization of Taddeo's behavior, not an entity relation."
    withdrawal_q["mentioned_candidate_ids"] = ["cand-0239"]

    statements.extend([murder, deterioration])

    candidate = candidate_by_id["cand-4871"]
    candidate["canonical_name"] = "Giulio Pisano (1931), footnote reference; title and identity unresolved"
    candidate["detail"] = (
        "The printed p.47 footnote reads 'Giulio Pisano. 1931.'; S0 OCR reads 'Giuho Pisano. 1011'. "
        "The chapter 21 bibliography separately contains cand-11419, G. Pisano's 1931 article on Don Taddeo; "
        "do not merge the note reference and bibliography entry before S3 identity comparison."
    )
    pisano_mention = mention_by_id["m-chp2-seciv-l190-245-0035"]
    pisano_mention["note"] = (
        "S0 OCR reads 'Giuho Pisano. 1011'; the print page reads 'Giulio Pisano. 1931.' A separate chapter-21 bibliography candidate (cand-11419) is a possible S3 identity comparison, not merged here."
    )
    renier_mention = {
        "mention_id": NEW_RENIER_MENTION_ID,
        "segment_id": NOTES_SEGMENT_ID,
        "candidate_id": "cand-4265",
        "surface_form": "Renier Zeno",
        "start_char": "1251",
        "end_char": "1262",
        "note": "Named in p.47 footnote 1 as the source cited for Taddeo's 'all sugar, all honey' characterization; the cited page was not independently read.",
    }
    mentions.append(renier_mention)

    citation_19 = statement_by_id["st-chp2-seciv-l190-245-citation-19"]
    citation_19_q = citation_19.setdefault("qualifiers", {})
    citation_19_q["linked_body_statement_ids"] = add_unique(
        citation_19_q.get("linked_body_statement_ids", []), ["st-chp2-seciv-l45-52-taddeo-sugar-and-honey-description"]
    )
    citation_19_q["related_statement_ids"] = add_unique(
        citation_19_q.get("related_statement_ids", []), ["st-chp2-seciv-l45-52-taddeo-sugar-and-honey-description"]
    )

    venetian_reports = statement_by_id["st-chp2-seciv-l190-245-venetian-reports-taddeo"]
    venetian_reports_q = venetian_reports.setdefault("qualifiers", {})
    venetian_reports_q["related_statement_ids"] = add_unique(
        venetian_reports_q.get("related_statement_ids", []), ["st-chp2-seciv-l45-52-others-excuse-taddeo"]
    )
    venetian_reports_q["linked_body_statement_ids"] = add_unique(
        venetian_reports_q.get("linked_body_statement_ids", []), ["st-chp2-seciv-l45-52-others-excuse-taddeo"]
    )

    moral_note = statement_by_id["st-chp2-seciv-l190-245-taddeo-moral-claim-disputed"]
    moral_q = moral_note.setdefault("qualifiers", {})
    moral_q["related_statement_ids"] = add_unique(moral_q.get("related_statement_ids", []), [NEW_DETERIORATION_ID])
    for note_id in ("st-chp2-seciv-l190-245-citation-20", "st-chp2-seciv-l190-245-citation-21"):
        note_q = statement_by_id[note_id].setdefault("qualifiers", {})
        note_q["linked_body_statement_ids"] = add_unique(note_q.get("linked_body_statement_ids", []), [NEW_DETERIORATION_ID])
        note_q["related_statement_ids"] = add_unique(note_q.get("related_statement_ids", []), [NEW_DETERIORATION_ID])

    citation_52 = {
        "statement_id": NEW_PISANO_CITATION_ID,
        "segment_id": NOTES_SEGMENT_ID,
        "subject_candidate_id": None,
        "object_candidate_id": "cand-4871",
        "predicate": "footnote_citation",
        "qualifiers": {
            "source_line_start": 208,
            "source_line_end": 208,
            "claim": "Footnote 4 cites Giulio Pisano (1931); the cited work title is not supplied in the note.",
            "speaker": "Haskell's footnote",
            "text_layer": "bibliographic citation",
            "print_page": 47,
            "pdf_physical_page": 32,
            "footnote_marker": 4,
            "qualification": (
                "Citation locator only. The page image corrects S0 OCR 'Giuho Pisano. 1011' to 'Giulio Pisano. 1931'. "
                "Chapter 21 separately lists a G. Pisano 1931 article on Taddeo (cand-11419); identity remains for S3 comparison."
            ),
            "page_image_ocr_corrections": [
                {"source_line": 208, "ocr": "Giuho Pisano. 1011.", "print": "Giulio Pisano. 1931."}
            ],
            "relation_candidate": False,
            "relation_candidate_note": "This is a bibliographic locator, not a substantive entity relation.",
            "mentioned_candidate_ids": ["cand-4871"],
            "related_segment": SEGMENT_ID,
            "related_source_lines": [50],
            "related_print_pages": [47],
            "linked_body_statement_ids": ["st-chp2-seciv-l45-52-taddeo-made-public-figure"],
            "related_statement_ids": ["st-chp2-seciv-l45-52-taddeo-made-public-figure", "st-chp21-bib-l928-983-entry-27"],
            "candidate_identity_question": ["cand-4871", "cand-11419"],
        },
        "original_quote": "4 Giuho Pisano. 1011.",
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    statements.append(citation_52)

    body_coverage = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    body_note = (
        " 本轮闭合7条旧unset：将Taddeo与街头斗殴、凶杀分别连到既有事件候选；赦免与品格恶化拆开，后者作为作者评价保留。"
        "依脚注1将“all sugar, all honey”归于Renier Zeno；匿名评论者保留为未指认主体，脚注3仅与现有威尼斯使节报告记录互链。"
        "Prefecture复兴、公共人物身份、智力与行为描述按状态/评价保存，不补造施事者。页图校正p.47的章节分隔、his/lais及Pisano脚注；S0未改。"
    )
    if body_note.strip() not in body_coverage["note"]:
        body_coverage["note"] = body_coverage["note"].rstrip() + body_note

    note_coverage = next(row for row in coverage if row.get("segment_id") == NOTES_SEGMENT_ID)
    note_note = (
        " S2回链补充：为p.47注1新增Renier Zeno精确mention并连到Taddeo描述；为注4补入citation-85。页图读作“Giulio Pisano. 1931.”，"
        "将cand-4871的OCR错年修正；与第21章候选cand-11419保持分立，身份留给S3比较。"
    )
    if note_note.strip() not in note_coverage["note"]:
        note_coverage["note"] = note_coverage["note"].rstrip() + note_note

    remaining = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if remaining:
        raise SystemExit(f"section IV L45-52 still has unset relation_candidate values: {sorted(remaining)}")

    updated = {
        "book-statements.jsonl": statements,
        "entity-candidates.csv": candidates,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    result = {
        "mode": "apply" if args.apply else "preview",
        "segments": [SEGMENT_ID, NOTES_SEGMENT_ID],
        "closed_unset_ids": sorted(UNSET_IDS),
        "classification_counts": {"true": 2, "false": 5},
        "new_statements": [NEW_MURDER_ID, NEW_DETERIORATION_ID, NEW_PISANO_CITATION_ID],
        "new_candidates": 0,
        "new_mentions": [NEW_RENIER_MENTION_ID],
        "updated_candidate": "cand-4871",
        "s3_identity_comparison_preserved": ["cand-4871", "cand-11419"],
        "source_asset_unchanged": True,
        "remaining_unset_in_body_segment": [],
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if written_by_id[NEW_MURDER_ID].get("object_candidate_id") != "cand-4642":
            raise SystemExit("the split savage-murder statement was not persisted")
        if written_by_id[NEW_DETERIORATION_ID].get("qualifiers", {}).get("relation_candidate") is not False:
            raise SystemExit("the split character-deterioration statement was not persisted")
        if written_by_id[NEW_PISANO_CITATION_ID].get("object_candidate_id") != "cand-4871":
            raise SystemExit("the corrected Pisano footnote citation was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
