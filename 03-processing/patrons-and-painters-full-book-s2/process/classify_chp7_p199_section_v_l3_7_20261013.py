from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_v.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-7.pdf"
SEGMENT = "chp-7:07_CHP-7_sec_v:l3-7"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp7-p199-sec-v-20261013")

EXPECTED_HASHES = {
    STATEMENTS.name: "8eb7c47052417215571aefbe39a102a0092045419bf88fc2a5564d8f3c002245",
    CANDIDATES.name: "9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d",
    SOURCE.name: "956054d03a849749a1f7a0dbf0eade81c5cb1252a284cc26d024a7f9f134b432",
    PDF.name: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
}

TRUE_NOTES = {
    "st-chp7-p199-v-artists-european-favourites":
        "Haskell explicitly characterizes the named artists as European favourites. Retain this comparative cultural-reception claim as author-attributed; it is not a measured popularity ranking.",
    "st-chp7-p199-v-artists-sent-works-abroad":
        "This retains Haskell’s collective claim that artists in Bologna, Venice and Naples sent works to the named distant cities; no individual artist, work or origin-to-destination pairing is inferred.",
    "st-chp7-p199-v-collectors-alternative-centres":
        "This retains Haskell’s qualified claim that aspiring collectors in England and Germany could and often did turn to Bologna, Venice or Naples instead of Rome; no individual collector-to-city assignment is inferred.",
    "st-chp7-p199-v-league-with-holy-roman-empire":
        "Haskell names the Holy Roman Empire as a partner in the Holy League joined by Venice; no accession date beyond the sentence or fuller treaty structure is inferred.",
    "st-chp7-p199-v-league-with-polish-king":
        "Haskell names the King of Poland as a partner in the Holy League joined by Venice; the monarch remains a title-only candidate pending S3 identity review.",
    "st-chp7-p199-v-painters-looked-north":
        "This retains Haskell’s broad claim about the northward orientation of painters in the Italian patronage account; the group candidate is source-defined and no individual migration route is inferred.",
    "st-chp7-p199-v-papal-decline-and-italianising":
        "This records Haskell’s paradoxical causal interpretation linking declining papal prestige with the Italianising of Europe; the policy, agents and scope of Italianising remain unspecified.",
    "st-chp7-p199-v-papal-power-and-provincial-centres":
        "This records Haskell’s qualified causal argument that loss of papal power indirectly encouraged active provincial centres; preserve indirectly and the source’s quoted label.",
    "st-chp7-p199-v-roman-art-reputation":
        "This retains Haskell’s qualitative account of Roman art’s reputation and representation by Maratta; great reputation and no longer unique are the author’s comparative judgments.",
    "st-chp7-p199-v-venice-joined-league-1684":
        "This records Haskell’s statement that Venice joined the Holy League in 1684; Venice’s status as a political actor remains distinct from the city candidate pending S3.",
    "st-chp7-p199-v-vienna-saved-1683":
        "This records Haskell’s statement that Vienna was saved from the Turks in 1683; the particular battle, force and agent are not identified in this sentence.",
    "st-chp7-p199-v-wars-renew-italys-politics":
        "This preserves Haskell’s account of several complex wars renewing Italy’s international political prominence and disrupting a long-standing status quo; the wars are not enumerated and nearly 150 years remains approximate.",
}
FALSE_NOTES = {
    "st-chp7-p199-v-open-then-came-the":
        "This is a cross-segment continuation marker, not a historical relation candidate; its clause is completed by p.200 L10.",
    "st-chp7-p199-v-patronage-conditions-changed":
        "This is a broad authorial contextual synthesis about changing conditions of patronage, without a separately identified entity-to-entity relation. Preserve it as a source statement but exclude it from the relation-candidate set.",
}
OPEN_ENDPOINT_NOTES = {
    "st-chp7-p199-v-artists-european-favourites":
        "The eight named painters remain individually listed, but the source does not define a single artist-group entity or identify a European audience as a bounded target; preserve the group claim without inventing either endpoint.",
    "st-chp7-p199-v-collectors-alternative-centres":
        "The collector group is source-defined and named destination cities remain in mentions, but no bounded destination-group candidate or collector-to-city mapping is established.",
}

EXPECTED_ROWS = {
    "st-chp7-p199-v-artists-european-favourites": (5, 6, "artists_described_as_european_favourites"),
    "st-chp7-p199-v-artists-sent-works-abroad": (4, 4, "artists_sent_works_to_distant_cities"),
    "st-chp7-p199-v-collectors-alternative-centres": (4, 4, "collectors_could_turn_to_other_italian_centres"),
    "st-chp7-p199-v-league-with-holy-roman-empire": (7, 7, "alliance_named_with"),
    "st-chp7-p199-v-league-with-polish-king": (7, 7, "alliance_named_with"),
    "st-chp7-p199-v-open-then-came-the": (7, 7, "chronological_continuation"),
    "st-chp7-p199-v-painters-looked-north": (3, 3, "painters_compelled_to_look_north"),
    "st-chp7-p199-v-papal-decline-and-italianising": (3, 4, "declining_papal_prestige_linked_to_italianising"),
    "st-chp7-p199-v-papal-power-and-provincial-centres": (4, 4, "loss_of_papal_power_indirectly_encouraged_provincial_centres"),
    "st-chp7-p199-v-patronage-conditions-changed": (3, 3, "patronage_conditions_changed"),
    "st-chp7-p199-v-roman-art-reputation": (4, 4, "roman_art_retained_reputation_but_was_no_longer_unique"),
    "st-chp7-p199-v-venice-joined-league-1684": (7, 7, "joined_alliance"),
    "st-chp7-p199-v-vienna-saved-1683": (7, 7, "reported_saved_from"),
    "st-chp7-p199-v-wars-renew-italys-politics": (6, 6, "wars_brought_italy_into_international_politics"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    temp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {path.name: sha256(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: {hashes}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    for index, fragment in {
        2: "Painters were compelled to look north",
        3: "Artists in these cities broke through",
        5: "wars brought Italy back into the forefront",
        6: "Venice joined a Holy League",
    }.items():
        if fragment not in source_lines[index]:
            raise SystemExit(f"source guard failed at line {index + 1}: {fragment}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("statement IDs are not unique")
    expected_ids = set(TRUE_NOTES) | set(FALSE_NOTES)
    actual_ids = {
        row["statement_id"] for row in rows
        if row.get("segment_id") == SEGMENT
    }
    if actual_ids != set(EXPECTED_ROWS):
        raise SystemExit(f"segment statement set changed: {sorted(actual_ids ^ set(EXPECTED_ROWS))}")
    actual_unset = {
        sid for sid in actual_ids
        if (by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None
    }
    if actual_unset != expected_ids:
        raise SystemExit(f"segment unset set changed: {sorted(actual_unset ^ expected_ids)}")

    output = []
    for original in rows:
        sid = original["statement_id"]
        if sid not in expected_ids:
            output.append(original)
            continue
        row = dict(original)
        q = dict(row.get("qualifiers") or {})
        line_start, line_end, predicate = EXPECTED_ROWS[sid]
        if row.get("predicate") != predicate or q.get("source_line_start") != line_start or q.get("source_line_end") != line_end:
            raise SystemExit(f"statement source/predicate changed: {sid}")
        q["relation_candidate"] = sid in TRUE_NOTES
        q["relation_candidate_note"] = TRUE_NOTES.get(sid, FALSE_NOTES.get(sid))
        if sid in OPEN_ENDPOINT_NOTES:
            q["open_endpoint_reason"] = OPEN_ENDPOINT_NOTES[sid]
        if sid == "st-chp7-p199-v-painters-looked-north":
            if row.get("subject_candidate_id") is not None or row.get("object_candidate_id") != "cand-4490":
                raise SystemExit("northward painter endpoint changed since review")
            row["subject_candidate_id"] = "cand-7273"
            mention_ids = list(q.get("mentioned_candidate_ids") or [])
            if "cand-7273" not in mention_ids:
                mention_ids.append("cand-7273")
            q["mentioned_candidate_ids"] = mention_ids
        row["qualifiers"] = q
        output.append(row)

    counts = {
        "statements": len(output),
        "True": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in output),
        "False": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in output),
        "unset": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in output),
    }
    if counts != {"statements": 14193, "True": 8740, "False": 3433, "unset": 2020}:
        raise SystemExit(f"unexpected post-counts: {counts}")

    after = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in output) + "\n").encode("utf-8")
    after_hash = sha256(after)
    report = {
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified_true": len(TRUE_NOTES),
        "classified_false": len(FALSE_NOTES),
        "endpoint_corrections": {"st-chp7-p199-v-painters-looked-north": ["cand-7273", "cand-4490"]},
        "post_counts": counts,
        "before_sha256": hashes,
        "after_statement_sha256": after_hash,
        "backup": str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"recovery copy already exists: {BACKUP}")
    BACKUP.write_bytes(raw[STATEMENTS])
    atomic_write(STATEMENTS, after)
    if sha256(STATEMENTS.read_bytes()) != after_hash:
        raise SystemExit("post-write statement hash mismatch")
    print("applied; recovery copy written; statement hash verified")


if __name__ == "__main__":
    main()
