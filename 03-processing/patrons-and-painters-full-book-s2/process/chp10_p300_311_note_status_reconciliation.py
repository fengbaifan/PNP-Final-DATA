"""Reconcile completed Chapter 10 footnote processing status on pp. 300-311.

The cited publications, letters, and archival records remain unconsulted where
the qualifications say so. This migration only removes stale workflow wording,
updates one now-completed internal cross-reference, and adds p.301 to the p.300
Goldoni note's related-body links. Default mode is dry-run; use --apply after
reviewing the displayed changes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
COVERAGE = ROOT / "04-knowledge" / "tables" / "s2-coverage.csv"
INTRO = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SECTION_II = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"

EXPECTED_TABLE_SHA256 = "6ed25bcafce8c554aa5c16ac6d1074ff3e7acb5a0de358e8962ec02d027c6a73"
EXPECTED_FILE_HASHES = {
    INTRO: "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    SECTION_II: "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    PDF: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
}
EXPECTED_SEGMENTS = {
    "chp-10:10_CHP-10_intro:l368-380": "a58eea87703095acaf4a07377eb5d7100bd76a790c0f082e230997e995d686a6",
    "chp-10:10_CHP-10_intro:l382-389": "81d50c04e66752729a137c595c19a54e93fa8ac153a2b324f8e1ac515a108784",
    "chp-10:10_CHP-10_intro:l456-466": "64cd99d39303a5fd6feebb08c5dd19b6bdbe48df72d80357b3c5995c30494964",
    "chp-10:10_CHP-10_intro:l468-479": "f94d7f83181d838df32049848707d735907115f01dde74e89dac6de11d635dac",
    "chp-10:10_CHP-10_intro:l481-489": "1b5b051796bbac3725681b091cb6e82a00f22381d0f651f934a9ccbd590f66b7",
    "chp-10:10_CHP-10_intro:l491-634": "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76",
    "chp-10:10_CHP-10_sec_ii:l7-15": "d1ecabafafb97a33a1b33afebe2048844aac6d981489d52bc56291d668e4b225",
    "chp-10:10_CHP-10_sec_ii:l273-349": "1308aba246107e6a7b237b1eb55c37538d11de95f6bb5aa150dd92ef734d6028",
}

# Each replacement is limited to a stale footnote-processing clause. Existing
# uncertainty about cited material, identities, dates, and claim scope remains.
REPLACEMENTS = {
    "st-chp10-p300-consul-resumption-and-death": (
        "footnote 1’s state-paper references remain pending.",
        "footnote 1 transcribes State Papers 99/70 and an Esposizione Principi register locator; neither cited record was consulted.",
    ),
    "st-chp10-p300-lodoli-memmo-and-smith-meetings": (
        "the reported acknowledgment and its source remain pending in footnote 4.",
        "footnote 4 cites the reported Memmo acknowledgment at 1786, p. 1, and a nested Lami reference; neither cited text was consulted.",
    ),
    "st-chp10-p300-lodoli-memmo-wynne-rivalry": (
        "footnote 5 remains pending.",
        "footnote 5 cites B. Brunelli, 1923; the cited work and content were not consulted.",
    ),
    "st-chp10-p300-smith-claimed-government-friendships": (
        "the 1740 letter is pending in footnote 7.",
        "footnote 7 transcribes a locator for Smith’s 26 August 1740 letter; the letter and archive record were not consulted.",
    ),
    "st-chp10-p300-smith-connoisseur-contacts": (
        "its text and dedication remain pending.",
        "footnote 2 cites Goldoni’s dedication in Opere, V, p. 259; the cited volume and dedication were not consulted.",
    ),
    "st-chp10-p300-smith-influence-after-1744": (
        "Footnote 6 is pending.",
        "Footnote 6 cites State Papers 99/69, p. 224r; the archive and cited page were not consulted.",
    ),
    "st-chp10-p300-smith-patron-and-painters": (
        "footnote 2’s source and collection details remain pending.",
        "footnote 2 cites Goldoni’s dedication and Blunt and Croft-Murray, pp. 137 ff.; the cited volume and pages were not consulted.",
    ),
    "st-chp10-p301-goldoni-and-smith-will": (
        "p.300 footnote 2 cites the dedication and remains pending in the consolidated notes segment.",
        "the Goldoni dedication clause continues from p.300 and is linked to note 2; the cited volume was not consulted.",
    ),
    "st-chp10-p301-lodoli-collection": (
        "footnote 3 remains pending.",
        "footnote 3 cites Previtali without identifying which of the two local bibliography matches applies; neither work was consulted.",
    ),
    "st-chp10-p301-mead-newton-friendship": (
        "which remains pending in the consolidated notes segment.",
        "which transcribes Haskell’s report about Smith and Pasquali’s Newton-related publications and a 1757 Tempio della Filosofia passage; the local 1755 bibliography match remains unresolved and the cited page was not read.",
    ),
    "st-chp10-p301-poleni-profile": (
        "footnote 4’s letters remain pending.",
        "footnote 4 transcribes Haskell’s account of the 1747 Poleni letters; the manuscripts were not consulted and no folios are supplied.",
    ),
    "st-chp10-p301-smith-official-visitors": (
        "footnote 7 remains pending.",
        "footnote 7 cites Levey, Burlington Magazine (1959), pp. 139 and 143; the article and pages were not independently consulted.",
    ),
    "st-chp10-p301-smith-pasquali-publication-activity": (
        "footnote 1 and its cited letters remain pending.",
        "footnote 1 transcribes Haskell’s Grosley quotation; the original source behind the locator ‘U’, p. 99, remains unresolved and was not consulted.",
    ),
    "st-chp10-p308-english-overdoor-architecture": (
        " The page’s footnotes remain pending in the consolidated notes segment.",
        "",
    ),
    "st-chp10-p308-two-roman-capricci-for-smith": (
        "footnote 2 remains pending in the consolidated notes segment.",
        "footnote 2 reports that the settings are imaginary and appear to have been inspired by Padua, citing Cust, p. 153; that page was not consulted.",
    ),
    "st-chp10-p309-smith-bought-more-canaletto-views": (
        "; p.309 footnotes 1–6 remain pending in the consolidated notes segment.",
        ".",
    ),
    "st-chp10-p310-1756-royal-negotiations-war": (
        "Footnote 2 remains pending.",
        "Footnote 2 cites Parker, p. 11; the cited page was not read.",
    ),
    "st-chp10-p310-1762-sale-to-george-iii": (
        "Footnote 6 points to Appendix 5 and remains pending.",
        "Footnote 6 points to Appendix 5; this internal reference does not independently confirm the sale details.",
    ),
    "st-chp10-p310-country-house-holdings": (
        "Footnote 1 remains pending in the consolidated notes segment.",
        "Footnote 1 cites Orlandi and Fleming for a reported 1757 visit and collection description; the cited pages were not independently read.",
    ),
    "st-chp10-p310-james-adam-meeting-and-assessment": (
        "Footnote 5's letter references remain pending.",
        "Footnote 5 transcribes references to James Adam’s letters of 20 and 27 August 1760 and Fleming, 1962, p. 270; the letters and page were not consulted.",
    ),
    "st-chp10-p310-smith-gave-up-theatre-box": (
        "Footnote 3 remains pending.",
        "Footnote 3 transcribes the Gabrieli register locator; the cited register and catalogue entry were not consulted.",
    ),
    "st-chp10-p310-smith-resigned-consulship": (
        "the cited letter in footnote 4 is dated 29 October 1760, but its note text remains pending.",
        "footnote 4 identifies a letter dated 29 October 1760; the letter was not consulted, and the note does not independently document the resignation.",
    ),
    "st-chp10-p310-smith-return-and-italy-travel-plan": (
        "Footnote 4 remains pending.",
        "Footnote 4 identifies the unconsulted 29 October 1760 letter cited for this quotation.",
    ),
    "st-chp10-p311-frederick-requested-young-castrato": (
        "Footnote 4 is pending review.",
        "Footnote 4 cites Leben, II, p. 312; the cited page was not independently consulted.",
    ),
    "st-chp10-p311-schulenburg-birth-and-origin": (
        "Footnote 1 is pending review.",
        "Footnote 1 identifies the 1834 Leben biography; the work was not independently consulted.",
    ),
    "st-chp10-p311-schulenburg-last-years-and-funeral-at-verona": (
        "footnote 3 is pending review.",
        "footnote 3 cites a funeral-procession drawing and itinerary; neither the drawing nor archive record was consulted, so the itinerary is not independently verified.",
    ),
    "st-chp10-p311-schulenburg-talked-about-women": (
        "p.311 footnote 5 remains pending review.",
        "footnote 5 quotes De Brosses through Haskell; the cited volume and page were not independently consulted.",
    ),
    "st-chp10-p311-venice-honored-schulenburg-with-statue-and-pension": (
        "Footnote 2 is pending review.",
        "Footnote 2 cites Romanin, VIII, p. 53; the cited passage was not independently consulted.",
    ),
    "st-chp10-p311-will-asserted-authority-no-children": (
        ", and p.311 footnotes remain pending.",
        ".",
    ),
    "st-chp10-p300-note3-gherardi-muratori-letters": (
        "Chapter 13 is not yet read; neither letters nor referenced chapter content were consulted for this note.",
        "Chapter 13 has since received S2 reading; the specific cross-reference and cited letters were not independently checked for this note.",
    ),
}

NOTE2_ID = "st-chp10-p300-note2-goldoni-dedication"
GOLDONI_P301_ID = "st-chp10-p301-goldoni-and-smith-will"
EXPECTED_NOTE2_LINKS = [
    "st-chp10-p300-smith-patron-and-painters",
    "st-chp10-p300-smith-connoisseur-contacts",
]

EXPECTED_ANCHORS = {
    "st-chp10-p300-consul-resumption-and-death": ("chp-10:10_CHP-10_intro:l368-380", 300, 1),
    "st-chp10-p300-lodoli-memmo-and-smith-meetings": ("chp-10:10_CHP-10_intro:l368-380", 300, 4),
    "st-chp10-p300-lodoli-memmo-wynne-rivalry": ("chp-10:10_CHP-10_intro:l368-380", 300, 5),
    "st-chp10-p300-smith-claimed-government-friendships": ("chp-10:10_CHP-10_intro:l368-380", 300, 7),
    "st-chp10-p300-smith-connoisseur-contacts": ("chp-10:10_CHP-10_intro:l368-380", 300, None),
    "st-chp10-p300-smith-influence-after-1744": ("chp-10:10_CHP-10_intro:l368-380", 300, 6),
    "st-chp10-p300-smith-patron-and-painters": ("chp-10:10_CHP-10_intro:l368-380", 300, 2),
    "st-chp10-p301-goldoni-and-smith-will": ("chp-10:10_CHP-10_intro:l382-389", 301, None),
    "st-chp10-p301-lodoli-collection": ("chp-10:10_CHP-10_intro:l382-389", 301, 3),
    "st-chp10-p301-mead-newton-friendship": ("chp-10:10_CHP-10_intro:l382-389", 301, 6),
    "st-chp10-p301-poleni-profile": ("chp-10:10_CHP-10_intro:l382-389", 301, 4),
    "st-chp10-p301-smith-official-visitors": ("chp-10:10_CHP-10_intro:l382-389", 301, 7),
    "st-chp10-p301-smith-pasquali-publication-activity": ("chp-10:10_CHP-10_intro:l382-389", 301, 1),
    "st-chp10-p308-english-overdoor-architecture": ("chp-10:10_CHP-10_intro:l456-466", 308, None),
    "st-chp10-p308-two-roman-capricci-for-smith": ("chp-10:10_CHP-10_intro:l456-466", 308, 2),
    "st-chp10-p309-smith-bought-more-canaletto-views": ("chp-10:10_CHP-10_intro:l468-479", 309, None),
    "st-chp10-p310-1756-royal-negotiations-war": ("chp-10:10_CHP-10_intro:l481-489", 310, 2),
    "st-chp10-p310-1762-sale-to-george-iii": ("chp-10:10_CHP-10_intro:l481-489", 310, 6),
    "st-chp10-p310-country-house-holdings": ("chp-10:10_CHP-10_intro:l481-489", 310, 1),
    "st-chp10-p310-james-adam-meeting-and-assessment": ("chp-10:10_CHP-10_intro:l481-489", 310, 5),
    "st-chp10-p310-smith-gave-up-theatre-box": ("chp-10:10_CHP-10_intro:l481-489", 310, 3),
    "st-chp10-p310-smith-resigned-consulship": ("chp-10:10_CHP-10_intro:l481-489", 310, None),
    "st-chp10-p310-smith-return-and-italy-travel-plan": ("chp-10:10_CHP-10_intro:l481-489", 310, 4),
    "st-chp10-p311-frederick-requested-young-castrato": ("chp-10:10_CHP-10_sec_ii:l7-15", 311, 4),
    "st-chp10-p311-schulenburg-birth-and-origin": ("chp-10:10_CHP-10_sec_ii:l7-15", 311, 1),
    "st-chp10-p311-schulenburg-last-years-and-funeral-at-verona": ("chp-10:10_CHP-10_sec_ii:l7-15", 311, 3),
    "st-chp10-p311-schulenburg-talked-about-women": ("chp-10:10_CHP-10_sec_ii:l7-15", 311, 5),
    "st-chp10-p311-venice-honored-schulenburg-with-statue-and-pension": ("chp-10:10_CHP-10_sec_ii:l7-15", 311, 2),
    "st-chp10-p311-will-asserted-authority-no-children": ("chp-10:10_CHP-10_sec_ii:l7-15", 311, None),
    "st-chp10-p300-note3-gherardi-muratori-letters": ("chp-10:10_CHP-10_intro:l491-634", 300, 3),
    NOTE2_ID: ("chp-10:10_CHP-10_intro:l491-634", 300, 2),
}

ALLOWED_PENDING_IDS = {
    "st-chp10-p310-palace-holdings",  # explicit S3 grouping uncertainty
    "st-chp10-p311-schulenburg-defended-corfu-1715-1716",  # cross-page S3 identity distinction
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all hash and row preconditions pass")
    args = parser.parse_args()

    if sha256(TABLE) != EXPECTED_TABLE_SHA256:
        raise SystemExit(f"precondition failed: statements table hash={sha256(TABLE)}")
    for path, expected in EXPECTED_FILE_HASHES.items():
        if sha256(path) != expected:
            raise SystemExit(f"precondition failed: {path.name} sha256={sha256(path)}")

    segment_rows = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines())
    }
    for segment_id, expected in EXPECTED_SEGMENTS.items():
        if segment_rows.get(segment_id, {}).get("sha256") != expected:
            raise SystemExit(f"precondition failed: segment hash changed: {segment_id}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = {row["segment_id"]: row for row in csv.DictReader(handle)}
    for segment_id in EXPECTED_SEGMENTS:
        row = coverage.get(segment_id, {})
        if row.get("disposition") != "reviewed" or row.get("migration_status") != "complete":
            raise SystemExit(f"precondition failed: S2 segment is not reviewed/complete: {segment_id}")

    raw_lines = TABLE.read_bytes().splitlines(keepends=True)
    rows = [json.loads(line) for line in raw_lines]
    if len(rows) != 12251:
        raise SystemExit(f"precondition failed: statement count={len(rows)}")
    by_id = {row["statement_id"]: (index, row) for index, row in enumerate(rows)}
    if len(by_id) != len(rows) or not set(REPLACEMENTS) <= set(by_id):
        raise SystemExit("precondition failed: duplicate or missing statement IDs")

    plans = {}
    for statement_id, (old_text, new_text) in REPLACEMENTS.items():
        index, row = by_id[statement_id]
        q = row.get("qualifiers", {})
        expected_segment, expected_page, expected_marker = EXPECTED_ANCHORS[statement_id]
        if row.get("segment_id") != expected_segment or q.get("printed_page") != expected_page:
            raise SystemExit(f"precondition failed: body/note anchor changed: {statement_id}")
        if q.get("footnote_marker") != expected_marker:
            raise SystemExit(f"precondition failed: printed marker changed: {statement_id}")
        if expected_marker is not None and q.get("footnote_text_pending") is not False:
            raise SystemExit(f"precondition failed: footnote text state changed: {statement_id}")
        qualification = q.get("qualification", "")
        if qualification.count(old_text) != 1:
            raise SystemExit(f"precondition failed: expected stale wording missing/nonunique: {statement_id}")
        updated = json.loads(json.dumps(row))
        updated["qualifiers"]["qualification"] = qualification.replace(old_text, new_text, 1).rstrip()
        if re.search(r"\b(?:pending|queued|unreviewed)\b", updated["qualifiers"]["qualification"], re.I):
            raise SystemExit(f"precondition failed: unrelated status wording remains in target row: {statement_id}")
        plans[statement_id] = updated

    _, note2 = by_id[NOTE2_ID]
    note2_q = note2.get("qualifiers", {})
    if note2_q.get("source_line_start") != 583 or note2_q.get("footnote_marker") != 2:
        raise SystemExit("precondition failed: p.300 note 2 anchor changed")
    if note2_q.get("related_body_statement_ids") != EXPECTED_NOTE2_LINKS:
        raise SystemExit("precondition failed: p.300 note 2 body links changed")
    linked_note2 = json.loads(json.dumps(note2))
    linked_note2["qualifiers"]["related_body_statement_ids"] = EXPECTED_NOTE2_LINKS + [GOLDONI_P301_ID]
    plans[NOTE2_ID] = linked_note2

    pending_after = set()
    for row in rows:
        q = row.get("qualifiers", {})
        if q.get("printed_page") in {300, 301, 308, 309, 310, 311}:
            text = str(plans.get(row["statement_id"], row).get("qualifiers", {}).get("qualification", ""))
            if re.search(r"\b(?:pending|queued|unreviewed)\b", text, re.I):
                pending_after.add(row["statement_id"])
    if pending_after != ALLOWED_PENDING_IDS:
        raise SystemExit(f"precondition failed: unresolved wording set changed: {sorted(pending_after)}")

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "qualification_rows": len(REPLACEMENTS),
        "link_rows": [NOTE2_ID],
        "changes": [{
            "statement_id": sid,
            "qualification_before": by_id[sid][1].get("qualifiers", {}).get("qualification"),
            "qualification_after": plan.get("qualifiers", {}).get("qualification"),
        } for sid, plan in plans.items() if sid != NOTE2_ID],
        "remaining_pending_ids": sorted(pending_after),
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return 0

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp10-p300-311-note-status-"))
    backup = backup_dir / "book-statements.jsonl"
    shutil.copy2(TABLE, backup)
    for statement_id, updated in plans.items():
        index, _ = by_id[statement_id]
        line = raw_lines[index]
        newline = b"\r\n" if line.endswith(b"\r\n") else b"\n"
        raw_lines[index] = json.dumps(updated, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline
    TABLE.write_bytes(b"".join(raw_lines))

    written = [json.loads(line) for line in TABLE.read_bytes().splitlines()]
    differences = []
    for before, after in zip(rows, written):
        if before == after:
            continue
        expected_after = plans.get(before["statement_id"])
        if expected_after != after or {k: v for k, v in before.items() if k != "qualifiers"} != {k: v for k, v in after.items() if k != "qualifiers"}:
            shutil.copy2(backup, TABLE)
            raise SystemExit("postcondition failed; restored backup")
        if before["statement_id"] == NOTE2_ID:
            old_q = {k: v for k, v in before["qualifiers"].items() if k != "related_body_statement_ids"}
            new_q = {k: v for k, v in after["qualifiers"].items() if k != "related_body_statement_ids"}
        else:
            old_q = {k: v for k, v in before["qualifiers"].items() if k != "qualification"}
            new_q = {k: v for k, v in after["qualifiers"].items() if k != "qualification"}
        if old_q != new_q:
            shutil.copy2(backup, TABLE)
            raise SystemExit("postcondition failed: change escaped approved field; restored backup")
        differences.append(before["statement_id"])
    if set(differences) != set(plans):
        shutil.copy2(backup, TABLE)
        raise SystemExit("postcondition failed: changed row set differs; restored backup")

    print(f"backup={backup}")
    print(f"table_sha256={sha256(TABLE)}")
    print(f"rows_changed={len(differences)}; qualification_only={len(REPLACEMENTS)}; note_link_only=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
