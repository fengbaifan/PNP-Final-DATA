#!/usr/bin/env python3
"""Classify and refine the p.105 S2 relation-review segment."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l80-89"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "18e5ceac63c431e5df905b26270ac6ef123624177a519b77b8b5c6fd25d234fa"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "16c7862e885a48f9acc3fc9c3bb9c5e8df38798c8fcbd5942e12e55191276490",
    "entity-candidates.csv": "77ae3fe81fd1e64d5ce0292f36d6fca8638bb0d954448d4e956b063e1f3ebbb7",
    "mentions.csv": "b0fc973a5711ddd704fdda1d1b4a064df8fb8970cfc0de584207b0e289670838",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l80-89-relations-20261011"
NEW_CANDIDATES = ("cand-11646", "cand-11647")
NEW_MENTION_ID = "m-chp4-sec-ii-l80-89-venetian-vogue"
NEW_STATEMENTS = (
    "st-chp4-sec-ii-l80-89-poussin-friend-of-jean-lemaire",
    "st-chp4-sec-ii-l80-89-lemaire-created-capricci",
    "st-chp4-sec-ii-l80-89-connoisseurs-helped-launch-venetian-vogue",
    "st-chp4-sec-ii-l80-89-print-dedicated-by-podesta",
)

UNCLASSIFIED_DUAL_IDS = {
    "st-chp4-sec-ii-l80-89-annibale-interpreted-antique-forms",
    "st-chp4-sec-ii-l80-89-cassiano-acquired-varotari-pictures",
    "st-chp4-sec-ii-l80-89-cassiano-in-roman-connoisseur-group",
    "st-chp4-sec-ii-l80-89-cassiano-owned-straightforward-landscapes",
    "st-chp4-sec-ii-l80-89-cassiano-quote-on-lemaire-capricci",
    "st-chp4-sec-ii-l80-89-cassiano-reported-advice-to-poussin",
    "st-chp4-sec-ii-l80-89-cassiano-watched-venetian-market",
    "st-chp4-sec-ii-l80-89-caution-against-esoteric-overreading",
    "st-chp4-sec-ii-l80-89-classical-erudition-venetian-colour-stimulated-poussin",
    "st-chp4-sec-ii-l80-89-landscape-mythological-figures-probable",
    "st-chp4-sec-ii-l80-89-mystic-marriage-possible-niece-commemoration",
    "st-chp4-sec-ii-l80-89-podesta-print-after-titian-work",
    "st-chp4-sec-ii-l80-89-podesta-print-dedicated-to-cassiano",
    "st-chp4-sec-ii-l80-89-poussin-classical-spirit-continuation",
    "st-chp4-sec-ii-l80-89-poussin-exceeded-antiquarian-copying",
    "st-chp4-sec-ii-l80-89-rare-evidence-of-poussin-demands-fragment",
    "st-chp4-sec-ii-l80-89-sacrifice-theme-recorded-in-drawings",
    "st-chp4-sec-ii-l80-89-travellers-noted-poussin-collection",
    "st-chp4-sec-ii-l80-89-varotari-travelled-to-copy-worship",
    "st-chp4-sec-ii-l80-89-worship-of-venus-sent-to-spain",
}

RELATION_NOTES = {
    "st-chp4-sec-ii-l80-89-annibale-interpreted-antique-forms": "Haskell's evaluative characterization of Annibale's interpretation of antique forms; 'hitherto' remains bounded to the source's account.",
    "st-chp4-sec-ii-l80-89-cassiano-acquired-varotari-pictures": "Haskell reports Cassiano acquired a number of pictures from Varotari; no individual picture or count is identified.",
    "st-chp4-sec-ii-l80-89-cassiano-in-roman-connoisseur-group": "Haskell places Cassiano among an unnamed group of Roman connoisseurs; group membership and boundaries remain unspecified.",
    "st-chp4-sec-ii-l80-89-cassiano-owned-straightforward-landscapes": "Haskell says Cassiano owned some straightforward landscapes; the works are not individually identified.",
    "st-chp4-sec-ii-l80-89-cassiano-quote-on-lemaire-capricci": "This is Cassiano's reported appreciation of architectural remains in Lemaire's capricci, mediated by Haskell and footnote 1; the cited letter was not independently checked.",
    "st-chp4-sec-ii-l80-89-cassiano-reported-advice-to-poussin": "The advice is attributed to Cassiano only as reported by Haskell; preserve the reported-speech status.",
    "st-chp4-sec-ii-l80-89-cassiano-watched-venetian-market": "Haskell reports Cassiano's interest in the Venetian picture market; no market record or transaction is specified.",
    "st-chp4-sec-ii-l80-89-caution-against-esoteric-overreading": "This is Haskell's explicit caution about interpreting Cassiano's patronage of Poussin; retain 'almost certainly' and do not turn it into an independently verified motive.",
    "st-chp4-sec-ii-l80-89-classical-erudition-venetian-colour-stimulated-poussin": "Haskell attributes stimulation to the combination of classical erudition and Venetian colour; the source does not isolate either component's effect.",
    "st-chp4-sec-ii-l80-89-landscape-mythological-figures-probable": "The claim concerns landscape paintings and hypothesized mythological subject matter, not Cassiano as an agent; keep 'most likely' and the individual works unidentified.",
    "st-chp4-sec-ii-l80-89-mystic-marriage-possible-niece-commemoration": "Haskell says the unidentified painting was possibly made to celebrate a niece; the antecedent of 'his' and her identity remain unresolved.",
    "st-chp4-sec-ii-l80-89-podesta-print-after-titian-work": "Haskell describes the unidentified print as taken from Titian's painting; the print's maker and exact identity are not established.",
    "st-chp4-sec-ii-l80-89-podesta-print-dedicated-to-cassiano": "The work is the dedicatee-side relation; Andrea Podestà is preserved as the reported dedicator, without inferring that he made the print.",
    "st-chp4-sec-ii-l80-89-poussin-classical-spirit-continuation": "This continuation completes the p.104 claim about Poussin absorbing classical art; it points to that same classical-art tradition, not the separate early-1620s periodizing phrase.",
    "st-chp4-sec-ii-l80-89-poussin-exceeded-antiquarian-copying": "Haskell infers Cassiano recognized Poussin's broader capabilities; retain it as authorial interpretation.",
    "st-chp4-sec-ii-l80-89-rare-evidence-of-poussin-demands-fragment": "The fragment concerns rare evidence of Poussin's demands on Cassiano and is resolved by the continuation at L92; no specific demand is stated here.",
    "st-chp4-sec-ii-l80-89-sacrifice-theme-recorded-in-drawings": "Haskell links Cassiano's interest in the Sacrifice theme to drawings made for him; the traveller's work, drawings, and draughtsman are not identified as the same objects or people.",
    "st-chp4-sec-ii-l80-89-travellers-noted-poussin-collection": "This is an attributed general estimate of about fifty Poussin paintings in Cassiano's collection; it is not an inventory count.",
    "st-chp4-sec-ii-l80-89-varotari-travelled-to-copy-worship": "Haskell reports Varotari travelled to Rome to copy the painting; preserve the narrative attribution and date context.",
    "st-chp4-sec-ii-l80-89-worship-of-venus-sent-to-spain": "The source places the painting's reported transfer to Spain in 1637 but does not identify the sender or circumstances.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
        newline="",
    )


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_statement(statement_id: str, subject: str, predicate: str, obj: str, quote: str,
                   line_start: int, line_end: int, claim: str, note: str,
                   mentioned: list[str]) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "pdf_physical_page": 16,
            "printed_page_locator": "p.105",
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": True,
            "relation_candidate_note": note,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    if sha(source_bytes) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source hash changed")
    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    if source_lines[79] != "[Page 105]":
        raise SystemExit("preflight failed: printed-page marker changed")
    body = "\n".join(source_lines[79:89])
    segment_rows = read_jsonl(SEGMENTS)
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if segment is None or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("preflight failed: segment manifest changed")

    paths = [TABLES / name for name in EXPECTED_SHA256]
    for path in paths:
        expected = EXPECTED_SHA256[path.name]
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"preflight failed: {path.name} hash {actual} != expected {expected}")

    statements_path = TABLES / "book-statements.jsonl"
    candidates_path = TABLES / "entity-candidates.csv"
    mentions_path = TABLES / "mentions.csv"
    statements = read_jsonl(statements_path)
    candidates, candidate_fields = read_csv(candidates_path)
    mentions, mention_fields = read_csv(mentions_path)
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}

    segment_statements = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    actual_unclassified = {
        row["statement_id"] for row in segment_statements
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
        and "relation_candidate" not in row.get("qualifiers", {})
    }
    if actual_unclassified != UNCLASSIFIED_DUAL_IDS:
        raise SystemExit("preflight failed: unclassified dual-statement set changed")
    if set(RELATION_NOTES) != UNCLASSIFIED_DUAL_IDS:
        raise SystemExit("preflight failed: decision notes do not cover exactly the pending dual statements")
    if any(cid in candidate_by_id for cid in NEW_CANDIDATES):
        raise SystemExit("preflight failed: a planned candidate ID already exists")
    if NEW_MENTION_ID in mention_by_id:
        raise SystemExit("preflight failed: planned mention ID already exists")
    if any(sid in statement_by_id for sid in NEW_STATEMENTS):
        raise SystemExit("preflight failed: a planned statement ID already exists")

    required_candidates = {
        "cand-1385": "person", "cand-1984": "person", "cand-2036": "person",
        "cand-3575": "term", "cand-4248": "work", "cand-4301": "term",
        "cand-5558": "person", "cand-5755": "work", "cand-5756": "term",
        "cand-5757": "work", "cand-5771": "", "cand-5776": "term",
        "cand-11645": "term",
    }
    for cid, expected_type in required_candidates.items():
        if cid not in candidate_by_id or candidate_by_id[cid].get("suggested_type", "") != expected_type:
            raise SystemExit(f"preflight failed: candidate boundary/type changed for {cid}")
    if candidate_by_id["cand-5757"].get("canonical_name") != "Andrea Podestà's unidentified print after The Worship of Venus":
        raise SystemExit("preflight failed: print candidate changed")
    antique_mention = mention_by_id.get("m-chp4-sec-ii-l80-89-antique-forms")
    if antique_mention is None or antique_mention.get("candidate_id") != "cand-4301":
        raise SystemExit("preflight failed: antique-forms mention mapping changed")
    spirit_id = "st-chp4-sec-ii-l80-89-poussin-classical-spirit-continuation"
    if statement_by_id[spirit_id].get("object_candidate_id") != "cand-4301":
        raise SystemExit("preflight failed: p.105 classical-spirit continuation mapping changed")
    if statement_by_id["st-chp4-sec-ii-l80-89-landscape-mythological-figures-probable"].get("subject_candidate_id") != "cand-2036":
        raise SystemExit("preflight failed: landscape interpretation endpoints changed")
    if statement_by_id["st-chp4-sec-ii-l80-89-podesta-print-dedicated-to-cassiano"].get("subject_candidate_id") != "cand-5558":
        raise SystemExit("preflight failed: print dedication endpoints changed")

    def source_quote(text: str) -> str:
        start = body.find(text)
        if start < 0:
            raise SystemExit("preflight failed: source phrase absent: " + text.encode("ascii", "backslashreplace").decode("ascii"))
        return body[start:start + len(text)]

    vogue_surface = "vogue for Venetian painting"
    vogue_start = body.find(vogue_surface)
    if vogue_start < 0:
        raise SystemExit("preflight failed: vogue mention surface absent")

    # Source-bounded concepts and work-group wording.
    antique_term = {
        "candidate_id": "cand-11646", "index_entry_id": "", "canonical_name": "Antique forms translated into acceptable seventeenth-century language",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell's characterization of Annibale Carracci as interpreting antique forms in an acceptable language of his own century; distinct from the early-1620s classical-reaction phrase and the general classical-art tradition.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L84",
    }
    vogue_term = {
        "candidate_id": "cand-11647", "index_entry_id": "", "canonical_name": "Vogue for Venetian painting in Haskell's account",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "A source-bounded artistic vogue that Haskell says an unnamed group of Roman connoisseurs helped launch; its period, reach, and participant list are unspecified.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L82",
    }
    candidates.extend([antique_term, vogue_term])
    antique_mention["candidate_id"] = "cand-11646"
    antique_mention["note"] = "The phrase names the antique forms Annibale Carracci is described as interpreting in an acceptable seventeenth-century language; not the early-1620s reaction candidate."
    mentions.append({
        "mention_id": NEW_MENTION_ID, "segment_id": SEGMENT_ID, "candidate_id": "cand-11647",
        "surface_form": vogue_surface, "start_char": str(vogue_start), "end_char": str(vogue_start + len(vogue_surface)),
        "note": "The sentence describes a vogue for Venetian painting, distinct from the artistic tradition candidate used for the shorter phrase 'Venetian painting'.",
    })

    # Correct subject/object mapping where the source claim is about a genre and its motifs.
    annibale = statement_by_id["st-chp4-sec-ii-l80-89-annibale-interpreted-antique-forms"]
    annibale["object_candidate_id"] = "cand-11646"
    annibale["qualifiers"]["mentioned_candidate_ids"] = ["cand-0576", "cand-11646"]
    annibale["qualifiers"]["claim"] = "Haskell calls Annibale Carracci the leading interpreter of antique forms in an acceptable seventeenth-century language up to that point."

    spirit = statement_by_id[spirit_id]
    spirit["object_candidate_id"] = "cand-11645"
    spirit["qualifiers"]["mentioned_candidate_ids"] = ["cand-1984", "cand-11645"]

    landscape = statement_by_id["st-chp4-sec-ii-l80-89-landscape-mythological-figures-probable"]
    landscape["subject_candidate_id"] = "cand-3575"
    landscape["object_candidate_id"] = "cand-5776"
    landscape["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-3575", "cand-5776"]
    landscape["qualifiers"]["claim"] = "Haskell says some paintings referred to as Landscapes, in the collection under discussion, most likely contained mythological figures and therefore had implications beyond nature records."

    # The dedication is a work-to-person relation. Keep the dedicator as a separate, source-supported role.
    print_row = statement_by_id["st-chp4-sec-ii-l80-89-podesta-print-dedicated-to-cassiano"]
    print_row["subject_candidate_id"] = "cand-5757"
    print_row["predicate"] = "dedicated_to"
    print_row["qualifiers"]["claim"] = "Haskell reports that Andrea Podestà dedicated the unidentified print after Titian's Worship of Venus to Cassiano."
    print_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-5558", "cand-2036", "cand-5757", "cand-2637", "cand-4248"]
    print_row["qualifiers"]["qualification"] = "The print is the dedicatee-side work relation; Andrea Podestà is the reported dedicator, but the source does not identify the print's maker."
    candidate_by_id["cand-5757"]["canonical_name"] = "Unidentified print after Titian's The Worship of Venus, dedicated by Andrea Podestà to Cassiano"
    candidate_by_id["cand-5757"]["detail"] = "Haskell reports that Andrea Podestà dedicated a print taken from Titian's painting to Cassiano; the print's individual identity and maker are not established."

    # Record the source's additional explicit relation claims as separate atomic candidates.
    additions = [
        make_statement(
            NEW_STATEMENTS[0], "cand-1984", "friend_of", "cand-1385",
            source_quote("Poussin’s friend, Jean Lemaire"), 81, 81,
            "Haskell identifies Jean Lemaire as Poussin's friend.",
            "The friendship is stated by Haskell in the page-105 narrative; no date or further particulars are supplied.",
            ["cand-1984", "cand-1385"],
        ),
        make_statement(
            NEW_STATEMENTS[1], "cand-1385", "creator_of", "cand-5755",
            source_quote("capricci by Poussin’s friend, Jean Lemaire"), 81, 81,
            "Haskell attributes the unidentified plural capricci containing ancient architectural remains to Jean Lemaire.",
            "The source's 'by' explicitly attributes the plural work group to Lemaire; no individual capriccio is identified.",
            ["cand-1385", "cand-5755"],
        ),
        make_statement(
            NEW_STATEMENTS[2], "cand-5771", "helped_launch_vogue_for", "cand-11647",
            source_quote("group of Roman connoisseurs who helped to launch the vogue for Venetian painting"), 82, 82,
            "Haskell credits the unnamed group of Roman connoisseurs with helping to launch the vogue for Venetian painting.",
            "The group is unnamed and the vogue's time span and reach are not specified.",
            ["cand-5771", "cand-11647", "cand-5756"],
        ),
        make_statement(
            NEW_STATEMENTS[3], "cand-5757", "dedicated_by", "cand-5558",
            source_quote("The Genoese engraver Andrea\nPodesta dedicated to him a print taken from Titian’s Worship of Venus-"), 82, 83,
            "Haskell identifies Andrea Podestà as the person who dedicated the unidentified print to Cassiano.",
            "The source supports the dedicator role but does not explicitly establish who made the print.",
            ["cand-5757", "cand-5558", "cand-2036", "cand-2637", "cand-4248"],
        ),
    ]
    statements.extend(additions)

    for statement_id, note in RELATION_NOTES.items():
        row = statement_by_id[statement_id]
        qualifiers = row.setdefault("qualifiers", {})
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note

    for row in additions:
        quote = row["original_quote"]
        start_line = row["qualifiers"]["source_line_start"]
        end_line = row["qualifiers"]["source_line_end"]
        source_span = "\n".join(source_lines[start_line - 1:end_line])
        if quote not in source_span:
            raise SystemExit(f"preflight failed: added quote not contained in source lines for {row['statement_id']}")

    statement_ids = [row["statement_id"] for row in statements]
    candidate_ids = [row["candidate_id"] for row in candidates]
    mention_ids = [row["mention_id"] for row in mentions]
    if len(set(statement_ids)) != len(statement_ids) or len(set(candidate_ids)) != len(candidate_ids) or len(set(mention_ids)) != len(mention_ids):
        raise SystemExit("preflight failed: duplicate statement, candidate, or mention ID")
    candidate_id_set = set(candidate_ids)
    for row in statements:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_id_set:
                raise SystemExit(f"preflight failed: missing endpoint candidate {endpoint}")
    if (antique_mention["candidate_id"], antique_mention["surface_form"]) != ("cand-11646", "antique forms"):
        raise SystemExit("preflight failed: corrected antique-forms mention does not match the planned concept")
    new_mention = mention_by_id[NEW_MENTION_ID] if NEW_MENTION_ID in mention_by_id else mentions[-1]
    if body[int(new_mention["start_char"]):int(new_mention["end_char"])] != vogue_surface:
        raise SystemExit("preflight failed: new vogue mention offsets do not match the source segment")

    segment_after = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    segment_dual_after = [row for row in segment_after if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    segment_status = {
        "statements": len(segment_after),
        "dual": len(segment_dual_after),
        "true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_dual_after),
        "false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_dual_after),
        "unclassified": sum("relation_candidate" not in row.get("qualifiers", {}) for row in segment_dual_after),
    }
    totals_after = {"candidates": len(candidates), "mentions": len(mentions), "statements": len(statements)}
    expected_totals = {"candidates": 11625, "mentions": 27563, "statements": 12971}
    if totals_after != expected_totals or segment_status != {"statements": 29, "dual": 24, "true": 24, "false": 0, "unclassified": 0}:
        raise SystemExit(f"preflight failed: unexpected totals or segment state: {totals_after}, {segment_status}")

    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "classifications": [{"statement_id": sid, "relation_candidate": True, "note": RELATION_NOTES[sid]} for sid in sorted(UNCLASSIFIED_DUAL_IDS)],
        "new_candidates": candidates[-2:],
        "new_mentions": [mentions[-1]],
        "new_statements": [
            {"statement_id": row["statement_id"], "subject_candidate_id": row["subject_candidate_id"],
             "predicate": row["predicate"], "object_candidate_id": row["object_candidate_id"],
             "source_lines": [row["qualifiers"]["source_line_start"], row["qualifiers"]["source_line_end"]],
             "original_quote": row["original_quote"]}
            for row in additions
        ],
        "corrected_endpoints_and_candidate": {
            "annibale_interpreted_antique_forms": {"old_object": "cand-4301", "new_object": "cand-11646"},
            "poussin_classical_spirit_continuation": {"old_object": "cand-4301", "new_object": "cand-11645"},
            "landscape_subject_inference": {"old_subject": "cand-2036", "new_subject": "cand-3575", "object": "cand-5776"},
            "podesta_dedication": {"old": ["cand-5558", "dedicated_print_to", "cand-2036"], "new": ["cand-5757", "dedicated_to", "cand-2036"]},
            "print_dedicator": ["cand-5757", "dedicated_by", "cand-5558"],
            "print_candidate_name": "maker not inferred",
        },
        "segment_after": segment_status,
        "totals_after": totals_after,
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = [path.with_name(path.name + "." + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("preflight failed: a batch backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_jsonl(statements_path, statements)
    write_csv(candidates_path, candidates, candidate_fields)
    write_csv(mentions_path, mentions, mention_fields)
    for path in paths:
        print(f"written_sha256 {path.name} {sha(path.read_bytes())}")
    print("backups " + ", ".join(path.name for path in backups))


if __name__ == "__main__":
    main()
