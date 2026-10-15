from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
BODY_SEGMENT = "chp-9:09_CHP-9_intro:l157-165"
NOTES_SEGMENT = "chp-9:09_CHP-9_intro:l323-445"
BACKUP_SUFFIX = "bak-s2-chp9-p256-semantic-endpoints-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "cfca70b2350fa230553237d6a5b91ad38900bc10b40521384a0158da3f37f3be",
    "mentions.csv": "001d429d87c91092df2e07517ed40f18aaa663705b8abf590a84b517745fc81a",
    "book-statements.jsonl": "181de89ea95e6d2c3e722d6be9f905cc097122b0bebf1447ed70cfbd5d3427f2",
}
EXPECTED_SEGMENT_HASHES = {
    BODY_SEGMENT: "2962dfdf9f25c1a0a8e2fa89b192fe3d26b5118a976e05a05f8812fa1bdf6c50",
    NOTES_SEGMENT: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
NEW_CANDIDATES = (
    {
        "candidate_id": "cand-12380",
        "canonical_name": "Many Venetian patrician families reported to claim Roman descent",
        "line": 163,
        "surface": "patrician famines",
        "type": "term",
        "detail": "Source-defined collective group in Haskell's statement that many patrician families claimed Roman descent. The scan confirms 'families'; individual lineages and the ancestry claims are not verified here.",
    },
    {
        "candidate_id": "cand-12381",
        "canonical_name": "Roman descent claimed by patrician families in Haskell's Venetian account",
        "line": 163,
        "surface": "Roman descent",
        "type": "term",
        "detail": "The ancestry claim Haskell reports for many patrician families. This records the claim's content and does not verify Roman descent or identify a lineage.",
    },
    {
        "candidate_id": "cand-12382",
        "canonical_name": "The century's love of melodrama in Haskell's Venetian account",
        "line": 164,
        "surface": "the century’s love of melodrama",
        "type": "term",
        "detail": "A source-bounded cultural tendency that Haskell says the Sacrifice theme satisfied; no broader population or independent historical claim is added.",
    },
    {
        "candidate_id": "cand-12383",
        "canonical_name": "Responsibilities of power in Haskell's Venetian account",
        "line": 164,
        "surface": "the responsibilities of power",
        "type": "term",
        "detail": "The political responsibilities that Haskell says the Sacrifice theme alluded to; no particular officeholder or painting is implied.",
    },
    {
        "candidate_id": "cand-12384",
        "canonical_name": "Roman heroes as comparison figures in Haskell's Venetian account",
        "line": 163,
        "surface": "Roman heroes",
        "type": "term",
        "detail": "The class of Roman heroic figures used in the source's generalization about comparisons made to Venetian state officials; the separately named Mucius Scaevola and Pompey remain individually recorded.",
    },
    {
        "candidate_id": "cand-12385",
        "canonical_name": "Cordellina's magnanimity as interpreted in the Montecchio wall paintings",
        "line": 161,
        "surface": "magnanimity of his patron",
        "type": "term",
        "detail": "Haskell's interpretation of two Tiepolo wall paintings at Cordellina's country house as allusions to their patron's magnanimity. This is an attributed interpretation, not an independently verified commission intention.",
    },
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def rewrite_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writeheader()
    writer.writerows(rows)
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + stream.getvalue().encode("utf-8")


def is_open(row: dict[str, object]) -> bool:
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [row for row in rows if is_open(row)]
    object_only = sum(bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id") for row in opens)
    subject_only = sum(not row.get("subject_candidate_id") and bool(row.get("object_candidate_id")) for row in opens)
    both = sum(not row.get("subject_candidate_id") and not row.get("object_candidate_id") for row in opens)
    return len(opens), object_only, subject_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    raw_by_name = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(raw_by_name[name]) != expected:
            raise ValueError(f"Input table changed since review: {name}")

    candidate_ids = {row["candidate_id"] for row in candidates}
    for item in NEW_CANDIDATES:
        if item["candidate_id"] in candidate_ids or any(row["canonical_name"] == item["canonical_name"] for row in candidates):
            raise ValueError(f"Candidate ID or name already exists: {item['candidate_id']}")

    segments = {
        segment["segment_id"]: segment
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for segment in [json.loads(line)]
    }
    for segment_id, expected in EXPECTED_SEGMENT_HASHES.items():
        if segments[segment_id].get("sha256") != expected:
            raise ValueError(f"Source segment changed: {segment_id}")

    body = segments[BODY_SEGMENT]
    source_lines = (ROOT / body["source_file"]).read_text(encoding="utf-8").splitlines()
    mention_by_id = {row["mention_id"]: row for row in mentions}
    new_candidate_rows: list[dict[str, str]] = []
    new_mentions: list[dict[str, str]] = []
    for item in NEW_CANDIDATES:
        line_no = item["line"]
        line = source_lines[line_no - 1]
        surface = item["surface"]
        if line.count(surface) != 1:
            raise ValueError(f"Expected unique source phrase not found: {item['candidate_id']}: {surface!r}")
        segment_start = int(body["line_start"])
        line_base = sum(len(text) + 1 for text in source_lines[segment_start - 1 : line_no - 1])
        new_candidate_rows.append({
            "candidate_id": item["candidate_id"], "index_entry_id": "", "canonical_name": item["canonical_name"],
            "index_page_range": "", "suggested_type": item["type"], "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": item["detail"],
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{BODY_SEGMENT}#L{line_no}",
        })
        if item["candidate_id"] != "cand-12380":
            mention_id = f"m-chp9-p256-{item['candidate_id'].removeprefix('cand-')}"
            if mention_id in mention_by_id:
                raise ValueError(f"Mention ID already exists: {mention_id}")
            start = line.find(surface)
            new_mentions.append({
                "mention_id": mention_id, "segment_id": BODY_SEGMENT, "candidate_id": item["candidate_id"],
                "surface_form": surface, "start_char": str(line_base + start),
                "end_char": str(line_base + start + len(surface)), "note": item["detail"],
            })
    patron_surface = "his patron"
    patron_line_no = 161
    patron_line = source_lines[patron_line_no - 1]
    if patron_line.count(patron_surface) != 1 or "m-chp9-p256-cordellina-patron-anaphor" in mention_by_id:
        raise ValueError("Expected unique Cordellina anaphor mention was absent or already recorded")
    patron_line_base = sum(len(text) + 1 for text in source_lines[int(body["line_start"]) - 1 : patron_line_no - 1])
    patron_start = patron_line.find(patron_surface)
    new_mentions.append({
        "mention_id": "m-chp9-p256-cordellina-patron-anaphor", "segment_id": BODY_SEGMENT,
        "candidate_id": "cand-0842", "surface_form": patron_surface,
        "start_char": str(patron_line_base + patron_start),
        "end_char": str(patron_line_base + patron_start + len(patron_surface)),
        "note": "Anaphoric reference to Carlo Cordellina in Haskell's interpretation of the two wall paintings.",
    })

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    before_counts = endpoint_counts(rows)
    if before_counts != (425, 268, 53, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {before_counts}")
    index = {row["statement_id"]: row for row in rows}
    target_ids = (
        "st-chp9-p256-cordellina-described-as-leading-advocate",
        "st-chp9-p256-patrician-families-claimed-roman-descent",
        "st-chp9-p256-sacrifice-theme-links-melodrama-and-power",
        "st-chp9-p256-state-officials-heard-roman-hero-comparisons",
        "st-chp9-p256-wall-paintings-allude-to-cordellina-magnanimity",
    )
    if any(statement_id not in index or not is_open(index[statement_id]) for statement_id in target_ids):
        raise ValueError("One or more expected open p.256 body statements are absent or already resolved")
    for statement_id in (
        "st-chp9-p256-note6-pietro-loredan-orazione",
        "st-chp9-p256-note7-antonio-loredan-orazione",
    ):
        if statement_id not in index or not is_open(index[statement_id]):
            raise ValueError(f"Expected open p.256 footnote statement missing: {statement_id}")
        index[statement_id]["qualifiers"]["open_endpoint_reason"] = (
            "This citation assertion is made in the current book's note, but the exact current edition of the source book is not represented as a candidate in the table. "
            "Keep the cited oration as the object; do not use Francis Haskell as a proxy for the book or invent a source-book endpoint here."
        )

    role_mention = mention_by_id["m-chp9-p256-cordellina-leading-advocate"]
    if role_mention.get("candidate_id") != "cand-0842":
        raise ValueError("Leading-advocate mention no longer has the reviewed pre-update mapping")
    role_mention["candidate_id"] = "cand-8372"
    role_mention["note"] = "Professional-role phrase for Carlo Cordellina; the sentence identifies him as an advocate within the legal profession."

    family_mention = mention_by_id["m-chp9-p256-patrician-families"]
    if family_mention.get("candidate_id") != "cand-8108":
        raise ValueError("Patrician-family mention no longer has the reviewed pre-update mapping")
    family_mention["candidate_id"] = "cand-12380"
    family_mention["note"] = "Haskell's source-defined collective group claiming Roman descent; the scan confirms OCR 'famines' as 'families'."

    role = index[target_ids[0]]
    role["object_candidate_id"] = "cand-8372"
    rq = role["qualifiers"]
    rq["claim"] = "Haskell describes Carlo Cordellina as the leading advocate of his day, within the legal profession."
    rq["relation_candidate_note"] = "The phrase identifies Cordellina as an advocate; cand-8372 represents the legal profession that supplies the role's professional class."
    rq.pop("open_endpoint_reason", None)

    families = index[target_ids[1]]
    families["subject_candidate_id"] = "cand-12380"
    families["object_candidate_id"] = "cand-12381"
    fq = families["qualifiers"]
    fq["mentioned_candidate_ids"] = ["cand-12380", "cand-12381"]
    fq["relation_candidate_note"] = "The source names an unnamed group of many patrician families and reports their Roman-descent claims; it does not verify the genealogies or identify individual families."
    fq.pop("open_endpoint_reason", None)

    sacrifice = index[target_ids[2]]
    line_164 = source_lines[163]
    sentence_start = line_164.index("The theme of Sacrifice")
    sentence_end = line_164.index(" But antiquity", sentence_start)
    sacrifice_quote = line_164[sentence_start:sentence_end]
    if not sacrifice_quote.endswith("."):
        raise ValueError("Could not isolate the exact p.256 Sacrifice sentence")
    sacrifice["object_candidate_id"] = "cand-12382"
    sacrifice["predicate"] = "satisfied_contemporary_love_of_melodrama"
    sq = sacrifice["qualifiers"]
    sq["claim"] = "Haskell says the theme of Sacrifice satisfied the century's love of melodrama."
    sq["mentioned_candidate_ids"] = ["cand-8403", "cand-12382"]
    sq["relation_candidate_note"] = "This is the first of two propositions in the source sentence; the distinct allusion to responsibilities of power is recorded separately."
    sq.pop("open_endpoint_reason", None)
    sacrifice["original_quote"] = sacrifice_quote

    power = deepcopy(sacrifice)
    power["statement_id"] = "st-chp9-p256-sacrifice-theme-alludes-to-power-responsibilities"
    power["object_candidate_id"] = "cand-12383"
    power["predicate"] = "alluded_to_responsibilities_of_power"
    power["qualifiers"]["claim"] = "Haskell says the Sacrifice theme alluded to the responsibilities of power."
    power["qualifiers"]["mentioned_candidate_ids"] = ["cand-8403", "cand-12383"]
    power["qualifiers"]["relation_candidate_note"] = "This is the second proposition in the source sentence, separated from its statement about satisfying the century's love of melodrama."
    if power["statement_id"] in index:
        raise ValueError(f"Statement ID already exists: {power['statement_id']}")
    rows.append(power)
    index[power["statement_id"]] = power

    officials = index[target_ids[3]]
    officials["object_candidate_id"] = "cand-12384"
    oq = officials["qualifiers"]
    oq["mentioned_candidate_ids"] = ["cand-8405", "cand-12384"]
    oq["relation_candidate_note"] = "The source generalizes about state officials hearing comparisons with the class of Roman heroes; Mucius Scaevola and Pompey remain separately represented as examples."
    oq.pop("open_endpoint_reason", None)

    wall = index[target_ids[4]]
    line_160 = source_lines[159]
    line_161 = source_lines[160]
    quote_start = line_160.index("Tiepolo, who was much irritated")
    quote_end = line_161.index("Triumph of the Arts on the ceiling.") + len("Triumph of the Arts on the ceiling.")
    wall_quote = line_160[quote_start:] + "\n" + line_161[:quote_end]
    wall["subject_candidate_id"] = "cand-2583"
    wall["object_candidate_id"] = "cand-12385"
    wall["predicate"] = "work_alludes_to_patron_magnanimity"
    wall["original_quote"] = wall_quote
    wq = wall["qualifiers"]
    wq["source_line_start"] = 160
    wq["source_line_end"] = 161
    wq["claim"] = "Haskell interprets Tiepolo's The Continence of Scipio as an allusion to the magnanimity of Cordellina, its patron."
    wq["mentioned_candidate_ids"] = ["cand-2583", "cand-0842", "cand-12385"]
    wq["qualification"] = "This is Haskell's interpretation of the wall painting, not an independently verified commission statement or intention."
    wq["relation_candidate_note"] = "The sentence identifies The Continence of Scipio among two wall paintings and explicitly interprets the wall scenes as allusions to their patron's magnanimity; each work is represented as its own subject."
    wq.pop("open_endpoint_reason", None)

    darius = deepcopy(wall)
    darius["statement_id"] = "st-chp9-p256-family-of-darius-alludes-to-cordellina-magnanimity"
    darius["subject_candidate_id"] = "cand-2589"
    darius["qualifiers"]["claim"] = "Haskell interprets Tiepolo's The Family of Darius before Alexander the Great as an allusion to the magnanimity of Cordellina, its patron."
    darius["qualifiers"]["mentioned_candidate_ids"] = ["cand-2589", "cand-0842", "cand-12385"]
    if darius["statement_id"] in index:
        raise ValueError(f"Statement ID already exists: {darius['statement_id']}")
    rows.append(darius)
    index[darius["statement_id"]] = darius

    if endpoint_counts(rows) != (420, 263, 53, 104):
        raise ValueError(f"Unexpected post-update endpoint counts: {endpoint_counts(rows)}")
    candidate_after = append_rows(candidate_raw, candidate_fields, new_candidate_rows)
    mention_after = rewrite_rows(mention_raw, mention_fields, mentions + new_mentions)
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")
    print(f"candidates={len(candidates)}->{len(candidates) + len(new_candidate_rows)}")
    print(f"mentions={len(mentions)}->{len(mentions) + len(new_mentions)} (1 remapped existing mention)")
    print(f"statements={len(rows) - 2}->{len(rows)} (2 atomic statements added)")
    print("resolved=advocate_role, patrician_family_group, sacrifice_melodrama, sacrifice_power, roman_hero_comparisons, each_wall_painting_magnanimity")
    print("retained_open=p256_note6_current_source_book_subject, p256_note7_current_source_book_subject")
    print(f"open_endpoints={before_counts}->{endpoint_counts(rows)}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} sha256 {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = ((CANDIDATES, candidate_after), (MENTIONS, mention_after), (STATEMENTS, statement_after))
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temp, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temp, data in pairs:
            temp.write_bytes(data)
        for path, backup, temp, _ in pairs:
            temp.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temp, _ in pairs:
            if temp.exists():
                temp.unlink()
        for path, backup in replaced:
            shutil.copy2(backup, path)
        raise
    for path, backup, _, _ in pairs:
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
