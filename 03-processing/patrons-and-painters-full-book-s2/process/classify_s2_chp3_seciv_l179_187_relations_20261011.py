from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l179-187"
PREFIX = "st-chp3-seciv-l179-187-"
SOURCE_SHA = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA = "735eea420b569b17af9a18dee8d308b1cdf516ba4cb1f58643f11f68c99a0fa9"
PRE_HASHES = {
    STATEMENTS.name: "4d015d8c43a549a80945cbf9ed45faa52df49e8b41fc042d3c0313ee0384076e",
    CANDIDATES.name: "297b5155de43ed5ecedbc4d531d926f22ad9fbc8858088da5cc70559453a475b",
    MENTIONS.name: "bce0e64c18bf9f3a4e404f9e6acf2c72dc21d1883e2f67e3fcd5593bd4507ce6",
}
BACKUP_SUFFIX = ".bak-s2-chp3-seciv-l179-187-relations-20261011"

CLASSIFICATIONS = {
    "altar-reliefs-embedded-in-ornament": (True, "Haskell says the St Ignatius reliefs are embedded in the altar's colour and ornament; the statement links the reliefs to their containing work."),
    "annunciation-relief-in-right-chapel": (True, "The passage identifies the Annunciation relief as part of the right-transept chapel completed in 1749."),
    "assumption-relief-represents-luigi-gonzaga": (True, "The passage directly identifies Luigi Gonzaga as the subject of Legros's relief."),
    "baroque-art-generally-emotional": (False, "This is a broad authorial characterization of Baroque art, with no second entity or bounded relation."),
    "bracci-made-annunciation-relief": (True, "Haskell names Pietro Bracci as one of the makers of the Annunciation relief."),
    "ceiling-schemes-give-logical-force": (False, "This is an interpretive assessment of the ceilings' effect, not a relation between two entities."),
    "chiesa-nuova-private-miracle-devotion": (True, "Haskell links the Chiesa Nuova ceiling to the private-miracle theme; the unnamed Order's devotion is separated into two statements."),
    "deliberate-policy-evidenced-by-commissions": (True, "Haskell presents Legros's St Stanislas figure as a notable commission evidencing the Jesuits' deliberate affective policy."),
    "della-valle-made-annunciation-relief": (True, "Haskell names Filippo della Valle as one of the makers of the Annunciation relief."),
    "documents-preserved-in-jesuit-archives": (True, "The passage says documents relating to the monument project are preserved in the cited Jesuit Archives dossier."),
    "fabrini-cited-for-annunciation-relief": (True, "The text explicitly directs readers to Fabrini in connection with the Annunciation relief."),
    "grace-through-society-and-blessed-salvation-contrast": (True, "Haskell links Jesuit art's stated purpose to the representation of divine grace through the Society of Jesus."),
    "illusionistic-art-motivated-by-doctrine": (True, "Haskell attributes the illusionistic art to Jesuit patronage and doctrinal considerations; the three named church locations are recorded separately."),
    "jesuit-ceilings-universal-participation": (True, "Haskell links the universal participatory theme to the Gesù and S. Ignazio ceilings; each church is recorded separately."),
    "jesuits-as-missionaries-and-art-as-worldly": (True, "Haskell connects Jesuit missionary identity with the worldly character he assigns to Jesuit art."),
    "jesuits-followed-current-styles-under-constraints": (True, "The passage says the Jesuits tried to follow contemporary artistic styles; the unparticularized style reference is retained as an open term candidate."),
    "later-jesuit-art-stressed-doctrine": (True, "Haskell says Jesuit commissions increasingly stressed doctrinal elements when the order could employ artists directly."),
    "legros-completed-altar-with-relief": (True, "Haskell says Legros completed Pozzo's altar with an appealing bas-relief."),
    "legros-completed-ludovisi-monument-in-1710": (True, "Haskell directly attributes completion of the 1710 monument to Pierre Legros."),
    "legros-made-stanislas-figure": (True, "Haskell identifies Pierre Legros as the maker of the polychrome deathbed figure."),
    "less-interest-in-already-blessed-salvation": (True, "Haskell contrasts Jesuit artistic interest with the individual salvation of those already blessed."),
    "monument-to-cardinal-ludovisi": (True, "The passage identifies Cardinal Ludovico Ludovisi as a subject commemorated by the monument."),
    "monument-to-pope-gregory-xv": (True, "The passage identifies Pope Gregory XV as a subject commemorated by the monument."),
    "nineteenth-century-summary-called-inaccurate": (False, "This is Haskell's evaluation of a nineteenth-century summary, not a historical relation between entities."),
    "pozzo-designed-1697-altar": (True, "Haskell directly attributes the 1697 altar design to Andrea Pozzo; its location is also recorded separately."),
    "quoted-report-says-figure-moved-visitors": (True, "The quoted report says the figure moved the people who came to see it; their identities and number remain unknown."),
    "right-chapel-completed-in-1749": (False, "This records a chapel's completion date and state, not a relation between entities."),
    "stanislas-figure-kept-in-novitiate": (True, "Haskell says the figure was kept in a poorly lit room in the novitiate; the novitiate's identity remains unresolved."),
    "traveller-recalled-earlier-emotional-experience": (True, "Haskell says the unidentified English Protestant traveller believed he had experienced the Jesuit emotional effect nearly a century earlier."),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def csv_payload(fields: list[str], rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\r\n")
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def candidate(candidate_id: str, name: str, suggested_type: str, detail: str, source_line: int) -> dict[str, str]:
    return {
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
        "candidate_source_ref": f"{SEGMENT_ID}#L{source_line}",
    }


def mention(mention_id: str, candidate_id: str, surface: str, text: str, note: str) -> dict[str, str]:
    start = text.find(surface)
    if start < 0 or text.find(surface, start + len(surface)) >= 0:
        raise ValueError(f"surface must occur exactly once in segment text: {surface!r}")
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


def new_statement(template: dict, statement_id: str, subject: str, predicate: str, obj: str,
                  claim: str, quote: str, source_line: int, note: str) -> dict:
    row = copy.deepcopy(template)
    row["statement_id"] = statement_id
    row["subject_candidate_id"] = subject
    row["predicate"] = predicate
    row["object_candidate_id"] = obj
    row["original_quote"] = quote
    q = row["qualifiers"]
    q["source_line_start"] = source_line
    q["source_line_end"] = source_line
    q["claim"] = claim
    q["speaker"] = "Haskell"
    q["text_layer"] = "authorial narrative"
    q["print_page"] = 93
    q["pdf_physical_page"] = 35
    q["qualification"] = "The statement is limited to the passage's wording; it does not identify unnamed actors or infer completion beyond what is stated."
    q["relation_candidate"] = True
    q["relation_candidate_note"] = note
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed S2 updates")
    args = parser.parse_args()

    if sha(SOURCE) != SOURCE_SHA:
        raise SystemExit("source hash changed")
    segment_rows = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8").splitlines()]
    segment = next(row for row in segment_rows if row["segment_id"] == SEGMENT_ID)
    if segment["sha256"] != SEGMENT_SHA:
        raise SystemExit("segment hash changed")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        if sha(path) != PRE_HASHES[path.name]:
            raise SystemExit(f"pre-hash mismatch: {path.name}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[178:187])
    statements_bytes = STATEMENTS.read_bytes()
    statement_lines = statements_bytes.splitlines(keepends=True)
    statement_rows = [json.loads(line) for line in statement_lines]
    target_rows = {row["statement_id"][len(PREFIX):]: row for row in statement_rows if row.get("segment_id") == SEGMENT_ID}
    if set(target_rows) != set(CLASSIFICATIONS):
        raise SystemExit(f"unexpected p.93 statement set: {sorted(set(target_rows) ^ set(CLASSIFICATIONS))}")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in target_rows.values()):
        raise SystemExit("p.93 statements are no longer all unclassified")

    candidate_fields, candidate_rows = read_csv(CANDIDATES)
    mention_fields, mention_rows = read_csv(MENTIONS)
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if max(int(cid.split("-")[1]) for cid in candidate_ids if cid.startswith("cand-")) != 11625:
        raise SystemExit("candidate sequence changed")

    new_candidates = [
        candidate("cand-11626", "Unnamed religious Order described in the Chiesa Nuova ceiling passage", "institution",
                  "Haskell describes an unnamed Order as worshipping the Virgin and St Philip; this passage does not identify it with the Oratorians or another institution.", 184),
        candidate("cand-11627", "Contemporary artistic styles referred to in the Jesuit art passage", "term",
                  "The unspecified styles Haskell says Jesuits followed; no particular style or movement is inferred, and it is not equated with Baroque art.", 181),
        candidate("cand-11628", "Unidentified visitors moved by the St Stanislas Kostka figure", "",
                  "A collective audience in the nested quotation; the visitors' identities and number are not given, and no generic audience type exists in the current taxonomy.", 181),
    ]
    new_mentions = [
        mention("m-chp3-seciv-l179-187-rel-0052", "cand-11626", "an Order", segment_text,
                "Unnamed religious Order; identity unresolved and not inferred from the church context."),
        mention("m-chp3-seciv-l179-187-rel-0053", "cand-11627", "current styles", segment_text,
                "Unparticularized contemporaneous artistic styles; not equated with Baroque."),
        mention("m-chp3-seciv-l179-187-rel-0054", "cand-11628", "those who come to see it", segment_text,
                "Unidentified visitors quoted as being moved by the figure; members and number unknown."),
    ]
    if candidate_ids.intersection(row["candidate_id"] for row in new_candidates):
        raise SystemExit("new candidate ID collision")
    if mention_ids.intersection(row["mention_id"] for row in new_mentions):
        raise SystemExit("new mention ID collision")

    revised = copy.deepcopy(target_rows)
    for suffix, (is_relation, note) in CLASSIFICATIONS.items():
        row = revised[suffix]
        q = row["qualifiers"]
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note

    revised["chiesa-nuova-private-miracle-devotion"]["qualifiers"]["claim"] = "Haskell describes the Chiesa Nuova ceiling as showing a private miracle."
    revised["chiesa-nuova-private-miracle-devotion"]["original_quote"] = "In the Chiesa Nuova we look up and see a private miracle"
    relief = revised["altar-reliefs-embedded-in-ornament"]
    relief["subject_candidate_id"], relief["object_candidate_id"] = relief["object_candidate_id"], relief["subject_candidate_id"]
    relief["predicate"] = "embedded_in"
    relief["qualifiers"]["claim"] = "Haskell says the bas-reliefs depicting St Ignatius's life and miracles are embedded in the altar's mass of colour and ornament."
    policy = revised["deliberate-policy-evidenced-by-commissions"]
    policy["subject_candidate_id"] = "cand-5440"
    policy["predicate"] = "commission_evidences_deliberate_jesuit_affective_policy"
    policy["qualifiers"]["claim"] = "Haskell presents Legros's St Stanislas figure as a notable commission evidencing the Jesuits' deliberate affective policy."
    policy["original_quote"] = "That this policy was now deliberate is shown by other commissions of the time— most notably the gruesome polychrome figure by Legros of St Stanislas Kostka on his deathbed"
    styles = revised["jesuits-followed-current-styles-under-constraints"]
    styles["object_candidate_id"] = "cand-11627"
    styles["predicate"] = "followed_contemporary_artistic_styles"
    styles["qualifiers"]["claim"] = "Haskell says the Jesuits tried to follow the artistic styles current at the time, often with difficulty because of limited money or patrons."
    policy["qualifiers"]["relation_candidate_note"] = CLASSIFICATIONS["deliberate-policy-evidenced-by-commissions"][1]
    traveler = revised["traveller-recalled-earlier-emotional-experience"]
    traveler["subject_candidate_id"], traveler["object_candidate_id"] = traveler["object_candidate_id"], traveler["subject_candidate_id"]
    traveler["qualifiers"]["claim"] = "Haskell says an English Protestant traveller believed he had experienced the Jesuit emotional effect nearly a century earlier."
    audience = revised["quoted-report-says-figure-moved-visitors"]
    audience["object_candidate_id"] = "cand-11628"
    audience["qualifiers"]["claim"] = "The quoted description says the figure powerfully moved those who came to see it."

    template = next(iter(target_rows.values()))
    additions = [
        new_statement(template, PREFIX + "unnamed-order-worshipped-virgin", "cand-11626", "worshipped", "cand-3427",
                      "Haskell says the unnamed Order worshipped the Virgin above all else.",
                      "an Order that worshipped the Virgin and St Philip above all else", 184,
                      "The passage attributes devotion to the Virgin to an unnamed Order; its identity remains unresolved."),
        new_statement(template, PREFIX + "unnamed-order-worshipped-st-philip", "cand-11626", "worshipped", "cand-1898",
                      "Haskell says the unnamed Order worshipped St Philip above all else.",
                      "an Order that worshipped the Virgin and St Philip above all else", 184,
                      "The passage attributes devotion to St Philip to an unnamed Order; its identity remains unresolved."),
        new_statement(template, PREFIX + "illusionistic-art-in-s-andrea", "cand-5149", "was_site_of_jesuit_illusionistic_art", "cand-5444",
                      "Haskell locates Jesuit-fostered illusionistic art at S. Andrea al Quirinale.",
                      "art that they fostered in S. Andrea al Quirinale, the Gesù and above all S. Ignazio", 182,
                      "This records one named church in Haskell's list; it does not imply that the examples were identical works."),
        new_statement(template, PREFIX + "illusionistic-art-in-gesu", "cand-5200", "was_site_of_jesuit_illusionistic_art", "cand-5444",
                      "Haskell locates Jesuit-fostered illusionistic art at the Gesù.",
                      "art that they fostered in S. Andrea al Quirinale, the Gesù and above all S. Ignazio", 182,
                      "This records one named church in Haskell's list; it does not imply that the examples were identical works."),
        new_statement(template, PREFIX + "illusionistic-art-in-s-ignazio", "cand-5439", "was_site_of_jesuit_illusionistic_art", "cand-5444",
                      "Haskell especially associates Jesuit-fostered illusionistic art with S. Ignazio.",
                      "art that they fostered in S. Andrea al Quirinale, the Gesù and above all S. Ignazio", 182,
                      "This records the church Haskell emphasizes; it does not identify a particular work."),
        new_statement(template, PREFIX + "gesu-ceiling-universal-theme", "cand-5200", "ceiling_presented_universal_participatory_theme", "cand-5449",
                      "Haskell says the Gesù ceiling presented a universal theme in which worshippers played an essential part.",
                      "in the Gesù and S. Ignazio we are witnesses of a universal theme in whose development we ourselves play an essential part", 184,
                      "This assigns the stated theme to the Gesù ceiling, without enumerating participants."),
        new_statement(template, PREFIX + "s-ignazio-ceiling-universal-theme", "cand-5439", "ceiling_presented_universal_participatory_theme", "cand-5449",
                      "Haskell says the S. Ignazio ceiling presented a universal theme in which worshippers played an essential part.",
                      "in the Gesù and S. Ignazio we are witnesses of a universal theme in whose development we ourselves play an essential part", 184,
                      "This assigns the stated theme to S. Ignazio, without enumerating participants."),
        new_statement(template, PREFIX + "pozzo-altar-located-left-transept", "cand-5451", "located_in", "cand-5459",
                      "Haskell places Pozzo's 1697 altar in the left transept of S. Ignazio.",
                      "an altar in the left transept of S. Ignazio", 185,
                      "The location is stated directly; the transept is kept as the immediate place endpoint."),
        new_statement(template, PREFIX + "ludovisi-monument-located-in-s-ignazio", "cand-5457", "located_in", "cand-5439",
                      "Haskell says Legros's 1710 monument was completed in the same church, S. Ignazio.",
                      "completed the monument to Pope Gregory XV and Cardinal Ludovisi in the same church", 186,
                      "The anaphoric 'same church' refers to S. Ignazio in the immediately preceding sentence."),
    ]
    new_statement_ids = {row["statement_id"] for row in additions}
    if any(row["statement_id"] in {s["statement_id"] for s in statement_rows} for row in additions):
        raise SystemExit("new statement ID collision")

    # Verify the indexed surfaces are anchored in the page-marker-inclusive segment text.
    for row in new_mentions:
        a, b = int(row["start_char"]), int(row["end_char"])
        if segment_text[a:b] != row["surface_form"]:
            raise SystemExit(f"invalid mention span: {row['mention_id']}")

    counts = {True: 0, False: 0}
    for value, _note in CLASSIFICATIONS.values():
        counts[value] += 1
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "segment": SEGMENT_ID,
        "existing_statements_classified": len(revised),
        "classification_counts": {str(k).lower(): v for k, v in counts.items()},
        "new_statements": len(additions),
        "new_candidates": [row["candidate_id"] for row in new_candidates],
        "new_mentions": [{"id": row["mention_id"], "surface": row["surface_form"], "span": [row["start_char"], row["end_char"]]} for row in new_mentions],
        "direction_corrections": ["altar-reliefs-embedded-in-ornament", "deliberate-policy-evidenced-by-commissions", "traveller-recalled-earlier-emotional-experience"],
        "resulting_segment_total": len(revised) + len(additions),
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES, MENTIONS)]
    for path, backup in zip((STATEMENTS, CANDIDATES, MENTIONS), backups):
        shutil.copy2(path, backup)

    rewritten_lines: list[bytes] = []
    for raw in statement_lines:
        row = json.loads(raw)
        suffix = row["statement_id"][len(PREFIX):] if row.get("segment_id") == SEGMENT_ID else None
        if suffix in revised:
            row = revised[suffix]
            rewritten_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n")
        else:
            rewritten_lines.append(raw)
    rewritten_lines.extend(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n" for row in additions)
    STATEMENTS.write_bytes(b"".join(rewritten_lines))

    with CANDIDATES.open("ab") as handle:
        existing = CANDIDATES.read_bytes()
        if existing and not existing.endswith((b"\n", b"\r")):
            handle.write(b"\r\n")
        handle.write(csv_payload(candidate_fields, new_candidates))
    with MENTIONS.open("ab") as handle:
        existing = MENTIONS.read_bytes()
        if existing and not existing.endswith((b"\n", b"\r")):
            handle.write(b"\r\n")
        handle.write(csv_payload(mention_fields, new_mentions))

    after = {path.name: sha(path) for path in (STATEMENTS, CANDIDATES, MENTIONS)}
    print(json.dumps({"applied": True, "after_sha256": after, "backups": [str(path.relative_to(ROOT)) for path in backups]}, indent=2))


if __name__ == "__main__":
    main()
