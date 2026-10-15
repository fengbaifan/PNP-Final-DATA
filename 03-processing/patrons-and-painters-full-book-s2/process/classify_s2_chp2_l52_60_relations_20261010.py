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
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SEGMENT = "chp-2:02_CHP-2_sec_ii:l52-60"
EXPECTED_HASHES = {
    STATEMENTS.name: "1f2c9f91eca1e597bb46de006c113243b5293f9135ec6598ff9a0847878f23a0",
    CANDIDATES.name: "da02249471cace0cb8171c618e02d568145b53b297b04d17c389d67da2c8aec9",
    MENTIONS.name: "92fb7e69cf47bdeb2fc1c5c173a58db637868e7c7ccab2b5ba513189e3b661e0",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp2-sec-ii-l52-60-20261010"),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp2-sec-ii-l52-60-20261010"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp2-sec-ii-l52-60-20261010"),
}
NEW_CANDIDATE = {
    "candidate_id": "cand-11587",
    "index_entry_id": "",
    "canonical_name": "Relics associated with the four most-venerated saints at St Peter’s (members unspecified)",
    "index_page_range": "",
    "suggested_type": "",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": (
        "Haskell says relics associated with the four most-venerated saints at St Peter’s could be displayed "
        "on feast days and recalled by stone reproductions carried by angels. No individual relics, count, "
        "identifiers, or present-day holdings are supplied. Keep this open, untyped source-defined group "
        "distinct from the saints themselves and from their statues."
    ),
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": SEGMENT + "#L54",
}
NEW_MENTION = {
    "mention_id": "m-chp2-secii-l52-60-0089",
    "segment_id": SEGMENT,
    "candidate_id": "cand-11587",
    "surface_form": "the relics associated with the saints concerned",
    "start_char": "683",
    "end_char": "730",
    "note": "原文所指与四位最受崇敬圣人相关、可在节日展示的圣髑；具体物件及现藏处未给出。",
}
TRUE_NOTES = {
    "st-chp2-secii-l52-60-andrew-controversy-barque-touchstone":
        "Haskell reports that Duquesnoy's St Andrew aroused controversy and served as a touchstone for critics hostile to Bernini's more Baroque tendencies. Preserve the reception claim and the unnamed critics.",
    "st-chp2-secii-l52-60-balconies-display-relics":
        "Haskell says balconies above the niches enabled display of relics associated with the four saints on certain feast days. The relic group is not the saints themselves; no feast days or individual relics are named.",
    "st-chp2-secii-l52-60-barberini-patronage-complaint":
        "This preserves Haskell's generalized report that working for the Barberini without Bernini's patronage was said to be impossible. The complainants and individual cases remain unidentified.",
    "st-chp2-secii-l52-60-berninipayment":
        "Haskell reports Bernini received 10,000 scudi for building the baldacchino; the payer is not named here, and this amount is distinct from the total project cost reported at L47.",
    "st-chp2-secii-l52-60-berniniprestige-and-authority":
        "Haskell attributes Bernini's prestige in Rome and Europe and his now 'absolute' authority with Urban VIII to the work. Preserve this as authorial assessment, not a formal office or measured status.",
    "st-chp2-secii-l52-60-berninischeme-accepted-plan-revised":
        "This records acceptance of Bernini's scheme and the reported revision moving altars to the crypt and reserving the dome niches for statues. Keep this arrangement distinct from the baldacchino's broader iconographic scheme.",
    "st-chp2-secii-l52-60-berniniselects-sculptors":
        "Haskell says Bernini selected four leading sculptors and produced one figure himself. Whether Bernini is included in the count of four remains unresolved; the other sculptors are not all identified here.",
    "st-chp2-secii-l52-60-completed-scheme-new-meaning":
        "Haskell interprets the completed ensemble as giving new meaning to St Peter's through Urban VIII and Bernini's patronage. Preserve this as the author's reading, not an independently measured change.",
    "st-chp2-secii-l52-60-duquesnoy-carves-andrew":
        "The source reports that François Duquesnoy carved the St Andrew sculpture after working under Bernini on the baldacchino; no date is supplied in this passage.",
    "st-chp2-secii-l52-60-four-most-venerated-saints":
        "Haskell describes the four saints by the veneration of their relics. Only St Longinus and St Andrew are named in this passage; do not infer the other members.",
    "st-chp2-secii-l52-60-honours-and-influence":
        "This preserves Haskell's account of honours for Bernini and his family and the figurative description 'virtually artistic dictator of Rome'; it is not a formal title.",
    "st-chp2-secii-l52-60-marble-relief-started-1633":
        "Haskell says Bernini and unnamed assistants began the marble relief at the end of 1633. No assistants are identified and the relief's version remains unspecified.",
    "st-chp2-secii-l52-60-matilda-bequest-and-territorial-government":
        "Haskell reports that Countess Matilda bequeathed her property to the Holy See and interprets this as establishing the Church's territorial government on a firm basis. No exact year is supplied.",
    "st-chp2-secii-l52-60-matilda-body-transferred":
        "Haskell reports that Urban VIII had Matilda's body specially transferred from the province of Mantua. Retain the province-level origin; the destination and exact date are not given.",
    "st-chp2-secii-l52-60-matilda-relief-depicts-canossa":
        "Haskell says the principal relief on Matilda's tomb depicts Henry IV kneeling before Gregory VII at Canossa to convey the bequest's implications. The depiction is not independent evidence for the historical event.",
    "st-chp2-secii-l52-60-matilda-tomb-designed":
        "Haskell says Bernini designed a tomb for Countess Matilda in St Peter's right aisle at the same time he began the marble relief. Keep tomb and relief as distinct works.",
    "st-chp2-secii-l52-60-papacy-and-house-reminder":
        "Haskell interprets the integrated ensemble as reminding viewers of the papacy's glories and Urban VIII's own house. Preserve 'passionate reminder' as authorial language and resolve 'house' to the Barberini family only as the source's referent.",
    "st-chp2-secii-l52-60-passeri-quote-poison-fragment":
        "This records Passeri's quoted satirical fragment about Bernini as transmitted by Haskell; the sentence continues in the next segment and the metaphor is not literal.",
    "st-chp2-secii-l52-60-passeri-satirical-parody":
        "Haskell attributes to Passeri a parody of a poem praising Bernini, using the dragon and golden-apples metaphor. Preserve literary satire and do not treat it as a literal accusation.",
    "st-chp2-secii-l52-60-programme-duration":
        "Haskell says the work lasted many years and continued almost until the end of Urban VIII's pontificate. Preserve 'almost'; no exact start or end year is inferred.",
    "st-chp2-secii-l52-60-relief-location-subject":
        "Haskell says the relief was intended for the church interior and was in the portico at the time of writing. The subject description and 'foundation stone' metaphor remain source context, not independent claims about present location or papal doctrine.",
    "st-chp2-secii-l52-60-religious-elements-hymn":
        "This preserves Haskell's metaphorical reading of the programme as a hymn of praise to Christ, his saints, and apostles; do not turn the devotional interpretation into a formal dedication record.",
    "st-chp2-secii-l52-60-stone-angel-reproductions":
        "Haskell says stone reproductions carried by angels recalled the associated saints' relics to the faithful. The text does not specify the reproductions' exact iconography.",
    "st-chp2-secii-l52-60-two-further-direct-commissions":
        "This is Haskell's stated scope for the two direct commissions discussed next; it does not assert that Urban made no other commissions for St Peter's.",
    "st-chp2-secii-l52-60-urban-drawn-to-baldacchino":
        "Haskell conjectures that Urban VIII must have been drawn toward the baldacchino when entering St Peter's. Preserve this inferred viewing experience, not as direct testimony about Urban's thoughts.",
}
OLD_ENDPOINTS = {
    "st-chp2-secii-l52-60-andrew-controversy-barque-touchstone": ("cand-4413", "cand-3993"),
    "st-chp2-secii-l52-60-balconies-display-relics": ("cand-4414", "cand-4406"),
    "st-chp2-secii-l52-60-barberini-patronage-complaint": ("cand-3464", "cand-0295"),
    "st-chp2-secii-l52-60-berninipayment": ("cand-0295", "cand-4234"),
    "st-chp2-secii-l52-60-berniniprestige-and-authority": ("cand-0295", "cand-0209"),
    "st-chp2-secii-l52-60-berninischeme-accepted-plan-revised": ("cand-4432", "cand-4403"),
    "st-chp2-secii-l52-60-berniniselects-sculptors": ("cand-0295", "cand-4405"),
    "st-chp2-secii-l52-60-completed-scheme-new-meaning": ("cand-4433", "cand-3135"),
    "st-chp2-secii-l52-60-duquesnoy-carves-andrew": ("cand-0952", "cand-4413"),
    "st-chp2-secii-l52-60-four-most-venerated-saints": ("cand-4406", "cand-3135"),
    "st-chp2-secii-l52-60-honours-and-influence": ("cand-0295", "cand-3464"),
    "st-chp2-secii-l52-60-marble-relief-started-1633": ("cand-0295", "cand-4417"),
    "st-chp2-secii-l52-60-matilda-bequest-and-territorial-government": ("cand-4419", "cand-4424"),
    "st-chp2-secii-l52-60-matilda-body-transferred": ("cand-0209", "cand-4419"),
    "st-chp2-secii-l52-60-matilda-relief-depicts-canossa": ("cand-4421", "cand-4428"),
    "st-chp2-secii-l52-60-matilda-tomb-designed": ("cand-0295", "cand-4420"),
    "st-chp2-secii-l52-60-papacy-and-house-reminder": ("cand-4433", "cand-4223"),
    "st-chp2-secii-l52-60-passeri-quote-poison-fragment": ("cand-1856", "cand-0295"),
    "st-chp2-secii-l52-60-passeri-satirical-parody": ("cand-1856", "cand-0295"),
    "st-chp2-secii-l52-60-programme-duration": ("cand-4433", "cand-0209"),
    "st-chp2-secii-l52-60-relief-location-subject": ("cand-4417", "cand-3135"),
    "st-chp2-secii-l52-60-religious-elements-hymn": ("cand-4433", "cand-4141"),
    "st-chp2-secii-l52-60-stone-angel-reproductions": ("cand-4415", "cand-4406"),
    "st-chp2-secii-l52-60-two-further-direct-commissions": ("cand-0209", "cand-3135"),
    "st-chp2-secii-l52-60-urban-drawn-to-baldacchino": ("cand-0209", "cand-4234"),
}
FINAL_ENDPOINTS = dict(OLD_ENDPOINTS)
FINAL_ENDPOINTS.update({
    "st-chp2-secii-l52-60-balconies-display-relics": ("cand-4414", "cand-11587"),
    "st-chp2-secii-l52-60-stone-angel-reproductions": ("cand-4415", "cand-11587"),
})


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv_row(raw: bytes, headers: list[str], row: dict[str, str]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    buffer = io.StringIO(newline="")
    csv.writer(buffer, lineterminator=newline).writerow([row.get(key, "") for key in headers])
    prefix = b"" if raw.endswith((b"\n", b"\r")) else newline.encode("ascii")
    return raw + prefix + buffer.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed classifications and the relic endpoint correction")
    args = parser.parse_args()

    raw_statements = STATEMENTS.read_bytes()
    raw_candidates, candidate_headers, candidate_rows = read_csv(CANDIDATES)
    raw_mentions, mention_headers, mention_rows = read_csv(MENTIONS)
    actual_hashes = {
        STATEMENTS.name: hashlib.sha256(raw_statements).hexdigest(),
        CANDIDATES.name: hashlib.sha256(raw_candidates).hexdigest(),
        MENTIONS.name: hashlib.sha256(raw_mentions).hexdigest(),
    }
    require(actual_hashes == EXPECTED_HASHES, f"table hashes changed since review: {actual_hashes}")
    for backup in BACKUPS.values():
        require(not backup.exists(), f"recovery backup already exists: {backup.name}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for line_no, phrase in {
        53: "scheme was accepted and the plan was changed",
        54: "the relics associated with the saints concerned",
        55: "At the end of 1633 Bernini",
        56: "bequest at the end of the eleventh century",
        57: "the scheme was eventually complete",
        58: "a passionate reminder of the overwhelming glories of the papacy",
        59: "his authority with the Pope was now absolute",
        60: "10,000 scudi for his building of the baldacchino",
    }.items():
        require(line_no <= len(source_lines) and phrase in source_lines[line_no - 1],
                f"source line {line_no} changed: {phrase!r}")
    source_text = "\n".join(source_lines[51:60])
    phrase = NEW_MENTION["surface_form"]
    start = source_text.index(phrase)
    require((start, start + len(phrase)) == (683, 730), "reviewed relic mention span changed")

    bom = raw_statements.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw_statements else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw_statements.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    require(set(OLD_ENDPOINTS) <= set(by_id), "one or more expected statements are absent")
    pending = {
        row["statement_id"] for row in rows
        if row.get("segment_id") == SEGMENT
        and row.get("subject_candidate_id") and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(pending == set(TRUE_NOTES), f"pending bilateral statement set changed: {sorted(pending ^ set(TRUE_NOTES))}")
    require(set(TRUE_NOTES) == set(OLD_ENDPOINTS), "classification and endpoint review sets differ")

    candidates_by_id = {row["candidate_id"]: row for row in candidate_rows}
    require(NEW_CANDIDATE["candidate_id"] not in candidates_by_id, "new candidate ID already exists")
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) == 11586,
            "candidate ID sequence changed")
    require("candidate_id" in candidate_headers, "candidate table schema changed")
    mentions_by_id = {row["mention_id"]: row for row in mention_rows}
    require(NEW_MENTION["mention_id"] not in mentions_by_id, "new mention ID already exists")
    require("mention_id" in mention_headers, "mention table schema changed")
    require(NEW_MENTION["start_char"] == str(start) and source_text[start:start + len(phrase)] == phrase,
            "relic mention anchor does not match source")

    for statement_id, old_endpoints in OLD_ENDPOINTS.items():
        row = by_id[statement_id]
        require(row.get("segment_id") == SEGMENT, f"{statement_id} is outside the reviewed segment")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == old_endpoints,
                f"{statement_id} endpoints changed")
        q = row.get("qualifiers") or {}
        require(q.get("relation_candidate") is None, f"{statement_id} is already classified")
        first, last = q.get("source_line_start"), q.get("source_line_end")
        require(isinstance(first, int) and isinstance(last, int) and 52 <= first <= last <= 60,
                f"{statement_id} has an invalid source anchor")
        anchor = "\n".join(source_lines[first - 1:last])
        require(row.get("original_quote") in anchor, f"{statement_id} quote no longer matches source")
        row["subject_candidate_id"], row["object_candidate_id"] = FINAL_ENDPOINTS[statement_id]
        q = dict(q)
        q["relation_candidate"] = True
        q["relation_candidate_note"] = TRUE_NOTES[statement_id]
        row["qualifiers"] = q

    output_lines = []
    for index, row in enumerate(rows):
        encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            encoded = b"\xef\xbb\xbf" + encoded
        output_lines.append(encoded + newline)
    statement_payload = b"".join(output_lines)
    candidate_payload = append_csv_row(raw_candidates, candidate_headers, NEW_CANDIDATE)
    mention_payload = append_csv_row(raw_mentions, mention_headers, NEW_MENTION)

    true_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                         and (row.get("qualifiers") or {}).get("relation_candidate") is True)
    false_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                          and (row.get("qualifiers") or {}).get("relation_candidate") is False)
    pending_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                            and (row.get("qualifiers") or {}).get("relation_candidate") is None)
    require((true_bilateral, false_bilateral, pending_bilateral) == (4057, 451, 3989),
            f"unexpected projected bilateral counts: {(true_bilateral, false_bilateral, pending_bilateral)}")

    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified_true": list(TRUE_NOTES),
        "classified_false": [],
        "endpoint_corrections": {
            statement_id: [OLD_ENDPOINTS[statement_id], FINAL_ENDPOINTS[statement_id]]
            for statement_id in OLD_ENDPOINTS if OLD_ENDPOINTS[statement_id] != FINAL_ENDPOINTS[statement_id]
        },
        "new_candidate": NEW_CANDIDATE["candidate_id"],
        "new_mention": NEW_MENTION["mention_id"],
        "after_bilateral": {"relation_true": true_bilateral, "relation_false": false_bilateral,
                            "unclassified": pending_bilateral},
        "payload_sha256": {
            STATEMENTS.name: hashlib.sha256(statement_payload).hexdigest(),
            CANDIDATES.name: hashlib.sha256(candidate_payload).hexdigest(),
            MENTIONS.name: hashlib.sha256(mention_payload).hexdigest(),
        },
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    payloads = {STATEMENTS: statement_payload, CANDIDATES: candidate_payload, MENTIONS: mention_payload}
    created_backups: list[Path] = []
    temps: list[Path] = []
    try:
        for path, backup in BACKUPS.items():
            shutil.copy2(path, backup)
            created_backups.append(backup)
        for path, payload in payloads.items():
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                handle.write(payload)
                temps.append(Path(handle.name))
        for temp, path in zip(temps, payloads):
            os.replace(temp, path)
        written = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        written_by_id = {row["statement_id"]: row for row in written}
        require(all((written_by_id[key].get("qualifiers") or {}).get("relation_candidate") is True for key in TRUE_NOTES),
                "one or more classifications were not persisted")
        require(all((written_by_id[key].get("subject_candidate_id"), written_by_id[key].get("object_candidate_id")) == FINAL_ENDPOINTS[key]
                    for key in FINAL_ENDPOINTS), "one or more endpoint corrections were not persisted")
        with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
            persisted_candidates = {row["candidate_id"] for row in csv.DictReader(handle)}
        with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
            persisted_mentions = {row["mention_id"] for row in csv.DictReader(handle)}
        require(NEW_CANDIDATE["candidate_id"] in persisted_candidates and NEW_MENTION["mention_id"] in persisted_mentions,
                "new candidate/mention was not persisted")
    except Exception:
        for temp in temps:
            if temp.exists():
                temp.unlink()
        for path, backup in BACKUPS.items():
            if backup in created_backups:
                shutil.copy2(backup, path)
        raise

    print(json.dumps({
        "result": "applied",
        "statement_count": len(written),
        "candidate_count": len(persisted_candidates),
        "mention_count": len(persisted_mentions),
        "sha256_after": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in payloads},
        "backups": [backup.name for backup in created_backups],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
