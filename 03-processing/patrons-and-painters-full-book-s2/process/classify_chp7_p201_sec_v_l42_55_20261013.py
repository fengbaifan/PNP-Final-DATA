from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_v.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-7.pdf"
SEGMENT = "chp-7:07_CHP-7_sec_v:l42-55"
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + ".bak-s2-chp7-p201-sec-v-l42-55-20261013"
)

EXPECTED_HASHES = {
    STATEMENTS.name: "2ae9cd775215da0d1a3e559e8e8b85c4766eb0869a00eb604716f4ef70b18eb8",
    CANDIDATES.name: "9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d",
    MENTIONS.name: "40821fb7d0e896dac7ddfb5b3c61e798fb46ee42109c7007fb714401d9b6244d",
    SOURCE.name: "956054d03a849749a1f7a0dbf0eade81c5cb1252a284cc26d024a7f9f134b432",
    PDF.name: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
}

TRUE_NOTES = {
    "st-chp7-p201-v-apotheosis-designed-by-eugene": "This records Haskell's statement that Eugene designed the marble Apotheosis; the source does not establish a broader architectural role.",
    "st-chp7-p201-v-apotheosis-evaluative-interpretation": "This retains Haskell's interpretation of the surviving Apotheosis as evidence of Eugene's megalomania, with the qualification 'if not of his taste'.",
    "st-chp7-p201-v-apotheosis-executed-by-permoser": "This records Haskell's attribution of the marble Apotheosis to Permoser; no independent attribution check is implied.",
    "st-chp7-p201-v-artists-painted-belvedere-frescoes": "This preserves Haskell's collective account of Italian artists painting frescoes in the Upper and Lower Belvederes; it does not assign individual frescoes to individual artists.",
    "st-chp7-p201-v-belvederes-by-hildebrandt": "This records Haskell's attribution of the two Belvederes to Hildebrandt while preserving them as a pair.",
    "st-chp7-p201-v-caprara-commissions-bologna-paintings": "This records Haskell's report that Caprara commissioned many paintings in Bologna; the paintings are not individually identified.",
    "st-chp7-p201-v-collection-contained-flemish-primitives": "This records that Eugene's collection formerly contained an unidentified group of Flemish primitives; the works and collection history remain unresolved.",
    "st-chp7-p201-v-eugene-boni-virgil-portrait": "This records the source's reported commission of a Virgil 'portrait' from Boni in Bologna; it does not resolve the work's identity or medium.",
    "st-chp7-p201-v-eugene-employed-crespi-five-years": "This records Haskell's stated five-year employment of Crespi by Eugene without inferring dates or a formal office.",
    "st-chp7-p201-v-eugene-gallery-pictures": "This records the source's collective account of pictures hung in Eugene's gallery; no picture titles, artist-to-work assignments, or gallery building are inferred.",
    "st-chp7-p201-v-eugene-loyalty-characterization": "This retains Haskell's comparison of Eugene's loyalty to Italy in the arts of peace; the paired characterization of loyalty to Austria in war is split into a separate statement.",
    "st-chp7-p201-v-eugene-no-interest-in-venetian-manner": "This preserves Haskell's qualified claim that Eugene seems to have shown no interest in the lighter Venetian manner; the style is not equated with the painters as an entity.",
    "st-chp7-p201-v-eugene-patronage-of-italian-artists": "This records Haskell's account of Eugene's patronage of Italian painters and sculptors without inferring individual commissions beyond those stated separately.",
    "st-chp7-p201-v-eugene-preferred-ancient-poetic-subjects": "This preserves Haskell's inference from surviving records and inventories that Eugene preferred subjects from ancient poets; Virgil is an example, not the complete object group.",
    "st-chp7-p201-v-eugene-private-patron": "This records Haskell's characterization of Eugene as a private patron while preserving the source's unverified comparative superlatives.",
    "st-chp7-p201-v-eugene-reputation-among-italians": "This records Haskell's report of how Italians of Eugene's own time regarded him; it is an attributed contemporary reputation, not independent testimony.",
    "st-chp7-p201-v-galli-bibiena-theatrical-spectacles": "This records Haskell's report that Galli-Bibiena produced theatrical spectacles; individual productions are not named.",
    "st-chp7-p201-v-italian-commanders-furnish-palaces": "This records the commanders' stated interest in furnishing their Viennese palaces with pictures from their native land; no completed purchase is asserted.",
    "st-chp7-p201-v-italian-pictures-enriched-vienna-collections": "This preserves Haskell's collective account of pictures from Italy entering the new Vienna collections; no receiving institution or individual work is inferred.",
    "st-chp7-p201-v-martinelli-town-palace-1691": "This records that Martinelli came to build the Liechtenstein family's town palace in 1691; the statement does not claim completion in that year.",
    "st-chp7-p201-v-mattielli-aristocratic-gardens": "This records Haskell's collective claim that Mattielli made sculpture for many aristocratic gardens; individual works and gardens are unnamed.",
    "st-chp7-p201-v-mattielli-parodi-statues": "This records the source's joint naming of Mattielli and Parodi as makers of statues for the hall and gardens, without assigning individual statues to either maker.",
    "st-chp7-p201-v-painters-stopped-in-vienna": "This preserves Haskell's general claim that painters travelling north to Germany stopped to work in Vienna; no individual painter or date is supplied.",
    "st-chp7-p201-v-picture-collection-dispersed": "This records Haskell's statement that the picture collection had been dispersed; the date, agents, and destinations are not given.",
    "st-chp7-p201-v-pictures-by-neapolitan-painters": "This records the source's identification of del Po and Solimena as the Neapolitan painters represented in Eugene's gallery; their identities and the individual pictures remain subject to later alignment.",
    "st-chp7-p201-v-pozzo-garden-palace-ceiling-1704": "This records that Pozzo, summoned by the unnamed Emperor, began painting the hall ceiling in the Liechtenstein family's garden palace in 1704; completion is not stated.",
    "st-chp7-p201-v-solimena-sends-altarpieces": "This records Haskell's report that Solimena sent altarpieces for an unidentified chapel; no number, title, or date is supplied.",
    "st-chp7-p201-v-vienna-cultural-setting": "This retains Haskell's broad interpretation of Vienna's aristocratic and religious setting as culturally intelligible to Italians; it is not an independently verified causal account.",
    "st-chp7-p201-v-vienna-many-nobles-patronize-italian-art": "This preserves Haskell's contextual claim that Eugene was one among many nobles commissioning Italian art; the other patrons and commissions remain unnamed.",
    "st-chp7-p201-v-vienna-rise-after-military-victories": "This records Haskell's account of military outcomes establishing Vienna as a great European capital; the events remain unnamed and are not treated as a relation to Europe itself.",
    "st-chp7-p201-v-winter-palace-begun-by-fischer": "This records Haskell's statement that Fischer von Erlach began Eugene's Winter Palace; no completion date or precise role is supplied.",
}

FALSE_NOTES = {
    "st-chp7-p201-v-eugene-taste-sumptuous-heavy": "This is a source-attributed aesthetic characterization of Eugene's taste, not a relation between identifiable entities.",
    "st-chp7-p201-v-list-not-exhaustive": "This is a qualification about list completeness, not an entity relation; the unnamed additional artists must not be inferred.",
}

EXPECTED_IDS = {
    "st-chp7-p201-v-apotheosis-designed-by-eugene",
    "st-chp7-p201-v-apotheosis-evaluative-interpretation",
    "st-chp7-p201-v-apotheosis-executed-by-permoser",
    "st-chp7-p201-v-artists-painted-belvedere-frescoes",
    "st-chp7-p201-v-belvederes-by-hildebrandt",
    "st-chp7-p201-v-caprara-commissions-bologna-paintings",
    "st-chp7-p201-v-collection-contained-flemish-primitives",
    "st-chp7-p201-v-eugene-boni-virgil-portrait",
    "st-chp7-p201-v-eugene-employed-crespi-five-years",
    "st-chp7-p201-v-eugene-gallery-pictures",
    "st-chp7-p201-v-eugene-loyalty-characterization",
    "st-chp7-p201-v-eugene-no-interest-in-venetian-manner",
    "st-chp7-p201-v-eugene-patronage-of-italian-artists",
    "st-chp7-p201-v-eugene-preferred-ancient-poetic-subjects",
    "st-chp7-p201-v-eugene-private-patron",
    "st-chp7-p201-v-eugene-reputation-among-italians",
    "st-chp7-p201-v-eugene-taste-sumptuous-heavy",
    "st-chp7-p201-v-galli-bibiena-theatrical-spectacles",
    "st-chp7-p201-v-italian-commanders-furnish-palaces",
    "st-chp7-p201-v-italian-pictures-enriched-vienna-collections",
    "st-chp7-p201-v-list-not-exhaustive",
    "st-chp7-p201-v-martinelli-town-palace-1691",
    "st-chp7-p201-v-mattielli-aristocratic-gardens",
    "st-chp7-p201-v-mattielli-parodi-statues",
    "st-chp7-p201-v-painters-stopped-in-vienna",
    "st-chp7-p201-v-picture-collection-dispersed",
    "st-chp7-p201-v-pictures-by-neapolitan-painters",
    "st-chp7-p201-v-pozzo-garden-palace-ceiling-1704",
    "st-chp7-p201-v-solimena-sends-altarpieces",
    "st-chp7-p201-v-vienna-cultural-setting",
    "st-chp7-p201-v-vienna-many-nobles-patronize-italian-art",
    "st-chp7-p201-v-vienna-rise-after-military-victories",
    "st-chp7-p201-v-winter-palace-begun-by-fischer",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes after all guards pass")
    args = parser.parse_args()

    paths = [STATEMENTS, CANDIDATES, MENTIONS, SOURCE, PDF]
    raw = {path: path.read_bytes() for path in paths}
    hashes = {path.name: sha(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: {hashes}")
    if BACKUP.exists():
        raise SystemExit(f"recovery copy already exists: {BACKUP}")

    source_text = raw[SOURCE].decode("utf-8")
    quote_checks = [
        "Besides these men there were a number of high commanders of Italian origin serving in the Imperial army",
        "the great Prince Eugene of\nSavoy proved as loyal to Italy in the arts of peace as he was to Austria in those of war.",
        "many of whom came to work in Vienna for other patrons.",
        "a new Rome, which rivalled the old in its appeal to artists.",
    ]
    for quote in quote_checks:
        if quote not in source_text:
            raise SystemExit(f"source quote not found: {quote!r}")

    with CANDIDATES.open("r", encoding="utf-8-sig", newline="") as stream:
        candidate_rows = list(csv.DictReader(stream))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    required_candidates = {
        "cand-0389", "cand-2772", "cand-3398", "cand-3461", "cand-4221",
        "cand-4490", "cand-7284", "cand-7303", "cand-7304", "cand-7312",
        "cand-7322", "cand-7323", "cand-7341", "cand-7342",
    }
    if not required_candidates <= candidate_ids:
        raise SystemExit(f"missing candidate ids: {sorted(required_candidates - candidate_ids)}")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mention_rows = list(csv.DictReader(stream))
    existing_mentions = {
        (row["segment_id"], row["candidate_id"])
        for row in mention_rows
        if row["segment_id"] == SEGMENT
    }
    required_mentions = {
        (SEGMENT, candidate_id)
        for candidate_id in ("cand-0389", "cand-2772", "cand-3398", "cand-3461", "cand-4490", "cand-7284", "cand-7323", "cand-7341", "cand-7342")
    }
    if not required_mentions <= existing_mentions:
        raise SystemExit(f"missing segment mentions: {sorted(required_mentions - existing_mentions)}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8").splitlines()]
    by_id = {row["statement_id"]: row for row in rows}
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT]
    segment_ids = {row["statement_id"] for row in segment_rows}
    if segment_ids != EXPECTED_IDS:
        raise SystemExit(f"segment statement set changed: {sorted(segment_ids ^ EXPECTED_IDS)}")
    if set(TRUE_NOTES) | set(FALSE_NOTES) != EXPECTED_IDS:
        raise SystemExit("classification map does not cover exactly the source segment")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in segment_rows):
        raise SystemExit("expected all p.201 rows to be unclassified")

    new_ids = {
        "st-chp7-p201-v-eugene-loyalty-austria-in-war",
        "st-chp7-p201-v-venetian-painters-work-in-vienna-for-other-patrons",
        "st-chp7-p201-v-vienna-rivalled-rome-appeal-to-artists",
    }
    if new_ids & by_id.keys():
        raise SystemExit(f"new statement ids already exist: {sorted(new_ids & by_id.keys())}")

    p200_id = "st-chp7-p200-v-italian-commanders-open-continuation"
    p200 = by_id[p200_id]
    expected_p200 = (
        "cand-7303", "cand-7304", "intended_to_furnish_palaces_with_native_pictures"
    )
    if (p200.get("subject_candidate_id"), p200.get("object_candidate_id"), p200.get("predicate")) != expected_p200:
        raise SystemExit("p.200 continuation row changed")
    p200["predicate"] = "served_in_imperial_army"
    p200["original_quote"] = "Besides these men there were a number of high commanders of Italian origin serving in the Imperial army"
    pq = dict(p200.get("qualifiers") or {})
    pq.update({
        "claim": "Haskell identifies the unnamed high commanders of Italian origin as serving in the Imperial army.",
        "qualification": "This is the first clause of a sentence that continues onto p.201; the separate furnishing intention is retained in st-chp7-p201-v-italian-commanders-furnish-palaces.",
        "mentioned_candidate_ids": ["cand-7303", "cand-7304"],
        "relation_candidate": True,
        "relation_candidate_note": "This records the source's statement of the unnamed group's service in the Imperial army; it does not identify individual commanders.",
    })
    p200["qualifiers"] = pq

    endpoint_updates = {
        "st-chp7-p201-v-eugene-preferred-ancient-poetic-subjects": {"object_candidate_id": "cand-7342"},
        "st-chp7-p201-v-mattielli-parodi-statues": {"object_candidate_id": "cand-7312"},
        "st-chp7-p201-v-pictures-by-neapolitan-painters": {"object_candidate_id": "cand-7341"},
        "st-chp7-p201-v-eugene-no-interest-in-venetian-manner": {"object_candidate_id": None},
        "st-chp7-p201-v-vienna-rise-after-military-victories": {"object_candidate_id": None},
    }
    for sid, update in endpoint_updates.items():
        by_id[sid].update(update)

    by_id["st-chp7-p201-v-eugene-loyalty-characterization"]["predicate"] = "characterized_as_loyal_to_italy_in_arts_of_peace"
    by_id["st-chp7-p201-v-eugene-loyalty-characterization"]["qualifiers"]["claim"] = "Haskell characterizes Prince Eugene as loyal to Italy in the arts of peace."
    by_id["st-chp7-p201-v-eugene-boni-virgil-portrait"]["qualifiers"]["commissioned_artist_candidate_id"] = "cand-0389"
    by_id["st-chp7-p201-v-caprara-commissions-bologna-paintings"]["qualifiers"]["commission_location_candidate_id"] = "cand-3398"
    by_id["st-chp7-p201-v-vienna-rise-after-military-victories"]["original_quote"] = "Delivery from the Turks and then victory against the\nFrench established the city as a great European capital"

    open_reasons = {
        "st-chp7-p201-v-eugene-private-patron": "The source's superlative compares Eugene with unnamed European patrons; no comparison set is enumerated.",
        "st-chp7-p201-v-eugene-no-interest-in-venetian-manner": "The object is the stylistic category 'lighter manner of the Venetians'; no candidate in this segment represents that style, and the painter group is not an equivalent object.",
        "st-chp7-p201-v-galli-bibiena-theatrical-spectacles": "The source names theatrical spectacles as a class but identifies no individual production or work group.",
        "st-chp7-p201-v-mattielli-parodi-statues": "The source jointly names two makers but does not assign individual statues to either; retain the statue group and leave its maker endpoint open.",
        "st-chp7-p201-v-picture-collection-dispersed": "The source says the picture collection was dispersed but names no agents, date, destinations, or successor collection.",
        "st-chp7-p201-v-vienna-rise-after-military-victories": "The source gives relief from the Turks and victory against the French as causal context but names no specific events; Europe is not the object of the capital-status claim.",
    }
    for sid, reason in open_reasons.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q["open_endpoint_reason"] = reason
        by_id[sid]["qualifiers"] = q

    for sid, note in TRUE_NOTES.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        by_id[sid]["qualifiers"] = q
    for sid, note in FALSE_NOTES.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
        by_id[sid]["qualifiers"] = q

    new_rows = [
        {
            "statement_id": "st-chp7-p201-v-eugene-loyalty-austria-in-war",
            "segment_id": SEGMENT,
            "subject_candidate_id": "cand-2385",
            "object_candidate_id": "cand-7284",
            "predicate": "characterized_as_loyal_to_austria_in_war",
            "qualifiers": {
                "source_line_start": 43, "source_line_end": 44, "printed_page": 201, "pdf_physical_page": 43,
                "claim": "Haskell characterizes Prince Eugene as loyal to Austria in war.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "This is the paired half of Haskell's comparison with Eugene's loyalty to Italy in the arts of peace.",
                "mentioned_candidate_ids": ["cand-2385", "cand-7284"],
                "relation_candidate": True,
                "relation_candidate_note": "This preserves the Austria-in-war side of Haskell's comparison as a separate source-attributed claim.",
            },
            "original_quote": "the great Prince Eugene of\nSavoy proved as loyal to Italy in the arts of peace as he was to Austria in those of war.",
            "origin": "book", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
        },
        {
            "statement_id": "st-chp7-p201-v-venetian-painters-work-in-vienna-for-other-patrons",
            "segment_id": SEGMENT,
            "subject_candidate_id": "cand-7323",
            "object_candidate_id": "cand-2772",
            "predicate": "came_to_work_in_vienna_for_other_patrons",
            "qualifiers": {
                "source_line_start": 52, "source_line_end": 52, "printed_page": 201, "pdf_physical_page": 43,
                "claim": "Haskell says that many Venetian painters came to work in Vienna for other patrons.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "The other patrons and individual painters are unnamed; this statement does not identify Eugene as one of those patrons.",
                "mentioned_candidate_ids": ["cand-7323", "cand-2772"],
                "relation_candidate": True,
                "relation_candidate_note": "This separates the Venetian painters' work in Vienna for other patrons from Eugene's qualified lack of interest in their manner.",
            },
            "original_quote": "many of whom came to work in Vienna for other patrons.",
            "origin": "book", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
        },
        {
            "statement_id": "st-chp7-p201-v-vienna-rivalled-rome-appeal-to-artists",
            "segment_id": SEGMENT,
            "subject_candidate_id": "cand-2772",
            "object_candidate_id": "cand-4490",
            "predicate": "rivalled_in_appeal_to_artists",
            "qualifiers": {
                "source_line_start": 53, "source_line_end": 54, "printed_page": 201, "pdf_physical_page": 43,
                "claim": "Haskell says Vienna, called a 'new Rome', rivalled the old Rome in its appeal to artists.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "'New Rome' is a metaphorical comparison; the passage does not identify Vienna with Rome.",
                "mentioned_candidate_ids": ["cand-2772", "cand-4490"],
                "relation_candidate": True,
                "relation_candidate_note": "This isolates the explicit Vienna-to-Rome comparison from the preceding statement about military outcomes and capital status.",
            },
            "original_quote": "a new Rome, which rivalled the old in its appeal to artists.",
            "origin": "book", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
        },
    ]
    rows.extend(new_rows)
    by_id.update({row["statement_id"]: row for row in new_rows})
    output = [p200 if row["statement_id"] == p200_id else by_id[row["statement_id"]] for row in rows]

    counts = {
        "statements": len(output),
        "true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in output),
        "false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in output),
        "unset": sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in output),
    }
    if counts != {"statements": 14196, "true": 8802, "false": 3435, "unset": 1959}:
        raise SystemExit(f"unexpected post-counts: {counts}")

    post_by_id = {row["statement_id"]: row for row in output}
    if post_by_id["st-chp7-p201-v-vienna-rise-after-military-victories"]["object_candidate_id"] is not None:
        raise SystemExit("Vienna-capital claim retained an improper Europe endpoint")
    if post_by_id["st-chp7-p201-v-eugene-preferred-ancient-poetic-subjects"]["object_candidate_id"] != "cand-7342":
        raise SystemExit("ancient-poets group endpoint was not applied")
    if post_by_id["st-chp7-p201-v-mattielli-parodi-statues"]["object_candidate_id"] != "cand-7312":
        raise SystemExit("statue-group endpoint was not applied")
    if post_by_id["st-chp7-p201-v-pictures-by-neapolitan-painters"]["object_candidate_id"] != "cand-7341":
        raise SystemExit("Neapolitan-painter group endpoint was not applied")
    if post_by_id["st-chp7-p200-v-italian-commanders-open-continuation"]["predicate"] != "served_in_imperial_army":
        raise SystemExit("p.200 continuation clause was not atomized")

    after = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in output) + "\n").encode("utf-8")
    report = {
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "existing_classified_true": len(TRUE_NOTES),
        "existing_classified_false": len(FALSE_NOTES),
        "new_atomic_statements": len(new_rows),
        "p200_continuation_clause_corrected": True,
        "post_counts": counts,
        "input_sha256": hashes,
        "after_statement_sha256": sha(after),
        "backup": str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return

    BACKUP.write_bytes(raw[STATEMENTS])
    atomic_write(STATEMENTS, after)
    if sha(STATEMENTS.read_bytes()) != report["after_statement_sha256"]:
        raise SystemExit("post-write statement hash mismatch")
    print("applied; recovery copy written; statement hash verified")


if __name__ == "__main__":
    main()
